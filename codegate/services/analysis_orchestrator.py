import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from codegate.database.models.pull_request import PullRequest
from codegate.database.models.analysis import AnalysisRun, Status, Trigger, Finding
from codegate.integrations.pr_agent.adapter import CodeGateAdapter
from codegate.integrations.pr_agent.normalizer import PRAgentNormalizer
from codegate.services.quality_service import quality_service
from codegate.services.risk_service import risk_service
from codegate.services.policy_service import quality_policy_service
from codegate.services.policy_publisher import GitHubPolicyCheckPublisher
from pr_agent.git_providers import get_git_provider

logger = logging.getLogger(__name__)

class AnalysisOrchestrator:
    """
    Manages the lifecycle of an AnalysisRun, interacting with the PRAgentAdapter
    and persisting results to the database.
    """
    def __init__(self, db: Session):
        self.db = db

    def _get_latest_completed_run(self, pull_request_id: int, head_sha: str) -> Optional[AnalysisRun]:
        return self.db.query(AnalysisRun).filter(
            AnalysisRun.pull_request_id == pull_request_id,
            AnalysisRun.head_sha == head_sha,
            AnalysisRun.status == Status.COMPLETED
        ).order_by(AnalysisRun.created_at.desc()).first()

    async def trigger_analysis(self, pr: PullRequest, pr_url: str, force: bool = False, trigger_type: Trigger = Trigger.MANUAL) -> Tuple[AnalysisRun, bool]:
        """
        Triggers an analysis.
        Returns Tuple[AnalysisRun, bool] where bool is True if it was a newly created/run analysis,
        and False if it reused an existing completed one.
        """
        # 1. Idempotency check
        if not force:
            existing = self._get_latest_completed_run(pr.id, pr.head_sha)
            if existing:
                logger.info(f"Reusing existing completed analysis {existing.id} for PR {pr.id} (SHA: {pr.head_sha})")
                return existing, False
                
        # 2. Create pending run
        run = AnalysisRun(
            pull_request_id=pr.id,
            head_sha=pr.head_sha,
            status=Status.PENDING,
            trigger=trigger_type
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        # 3. Execute Run
        await self._execute_run(run, pr_url)
        return run, True

    async def _execute_run(self, run: AnalysisRun, pr_url: str):
        """
        Executes the AI review flow using CodeGateAdapter, updates status, and saves findings.
        """
        try:
            # Transition to RUNNING
            run.status = Status.RUNNING
            run.started_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(run)

            # Invoke Adapter
            adapter = CodeGateAdapter(pr_url)
            raw_data = await adapter.run()

            # Normalize Findings
            finding_schemas = PRAgentNormalizer.normalize_findings(raw_data)
            
            # Save Findings
            for schema in finding_schemas:
                finding_db = Finding(
                    analysis_run_id=run.id,
                    source=schema.source,
                    category=schema.category,
                    severity=schema.severity,
                    rule_id=schema.rule_id,
                    file_path=schema.file_path,
                    start_line=schema.start_line,
                    end_line=schema.end_line,
                    title=schema.title,
                    description=schema.description,
                    recommendation=schema.recommendation,
                    confidence=schema.confidence,
                    raw_data=schema.raw_data
                )
                self.db.add(finding_db)

            # Save Usage / Metadata if available
            usage = PRAgentNormalizer.extract_usage(raw_data)
            run.tokens_used = usage.get("total_tokens", 0)
            
            # Commit findings first so quality engine can read them
            self.db.commit()
            
            # Calculate Quality Score (errors caught inside, shouldn't fail the run)
            quality_service.calculate_and_persist(self.db, run.id)
            
            # Calculate Risk Score (independent from Quality)
            risk_service.calculate_and_persist(self.db, run.id)

            # Evaluate Quality Policy and Publish GitHub Check
            try:
                git_provider = get_git_provider()(pr_url)
                publisher = GitHubPolicyCheckPublisher(git_provider)
                quality_policy_service.evaluate_and_publish(self.db, run, publisher)
            except Exception as e:
                logger.error(f"Policy evaluation or publish failed for AnalysisRun {run.id}: {e}")

            # Complete Run
            run.status = Status.COMPLETED
            run.completed_at = datetime.now(timezone.utc)
            self.db.commit()

        except Exception as e:
            logger.exception(f"AnalysisRun {run.id} failed: {str(e)}")
            self.db.rollback()
            
            # Set failed status in a new transaction context
            run.status = Status.FAILED
            run.error_message = str(e)
            run.completed_at = datetime.now(timezone.utc)
            self.db.add(run)
            self.db.commit()
