import traceback
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from codegate.database.models import AnalysisRun
from codegate.database.models.policy import EvaluationStatus, PolicyEvaluation, PublishStatus, QualityPolicy
from codegate.engines.policy import POLICY_ENGINE_VERSION, QualityPolicyEngine
from codegate.engines.policy.explanation import build_evaluation_breakdown
from codegate.engines.policy.schemas import PolicyConfig
from codegate.repositories.finding_store import finding_store
from codegate.repositories.policy_store import policy_evaluation_store, quality_policy_store
from codegate.repositories.quality_store import quality_store
from codegate.repositories.risk_store import risk_store
from codegate.services.policy_publisher import PolicyCheckPublisher


class QualityPolicyService:
    def evaluate_and_publish(
        self, 
        db: Session, 
        analysis_run: AnalysisRun, 
        publisher: Optional[PolicyCheckPublisher] = None
    ) -> PolicyEvaluation:
        # Load active policy
        policy = quality_policy_store.get_by_repository(db, analysis_run.pull_request.repository_id)
        if not policy:
            policy = quality_policy_store.create_default(db, analysis_run.pull_request.repository_id)
            
        policy_config = PolicyConfig(
            quality_pass_threshold=policy.quality_pass_threshold,
            quality_block_threshold=policy.quality_block_threshold,
            risk_warning_threshold=policy.risk_warning_threshold,
            risk_block_threshold=policy.risk_block_threshold,
            max_critical_findings=policy.max_critical_findings,
            max_high_security_findings=policy.max_high_security_findings,
            require_quality_score=policy.require_quality_score,
            require_risk_score=policy.require_risk_score,
            require_complete_quality=policy.require_complete_quality,
            require_complete_risk=policy.require_complete_risk,
            test_gate_enabled=policy.test_gate_enabled,
            require_tests=policy.require_tests,
            coverage_gate_enabled=policy.coverage_gate_enabled,
            require_coverage=policy.require_coverage,
            changed_coverage_warning_threshold=policy.changed_coverage_warning_threshold,
            changed_coverage_block_threshold=policy.changed_coverage_block_threshold,
        )

        try:
            quality = quality_store.get_latest_for_analysis(db, analysis_run.id)
            risk = risk_store.get_latest_for_analysis(db, analysis_run.id)
            findings = finding_store.list_by_analysis(db, analysis_run_id=analysis_run.id)
            
            # Testing
            from codegate.repositories.testing_store import TestingStore
            testing_store = TestingStore()
            test_run = testing_store.get_test_run(db, analysis_run.id)
            cov_report = test_run.coverage_report if test_run else None

            result = QualityPolicyEngine.evaluate(
                config=policy_config,
                quality_score=quality,
                risk_score=risk,
                findings=findings,
                test_run=test_run,
                coverage_report=cov_report
            )
            
            evaluation = policy_evaluation_store.upsert(db, {
                "analysis_run_id": analysis_run.id,
                "policy_id": policy.id,
                "policy_engine_version": POLICY_ENGINE_VERSION,
                "policy_revision": policy.revision,
                "decision": result.decision.value,
                "passed_rules_count": result.passed_rules_count,
                "warning_rules_count": result.warning_rules_count,
                "blocked_rules_count": result.blocked_rules_count,
                "breakdown_json": build_evaluation_breakdown(result),
                "flags_json": result.flags,
                "config_snapshot_json": policy_config.model_dump(),
                "evaluation_status": EvaluationStatus.COMPLETED.value
            })
            
            if publisher:
                summary = self._build_check_summary(db, evaluation, quality, risk, test_run, cov_report)
                try:
                    check_id = publisher.publish(
                        result=result,
                        summary=summary,
                        text=self._build_check_text(evaluation)
                    )
                    if check_id:
                        evaluation.github_check_run_id = check_id
                        evaluation.github_publish_status = PublishStatus.SUCCESS.value
                        evaluation.published_at = datetime.now(timezone.utc)
                except Exception as e:
                    evaluation.github_publish_status = PublishStatus.FAILED.value
                    evaluation.github_publish_error = str(e)
                
                db.commit()
                db.refresh(evaluation)
                
            return evaluation
            
        except Exception as e:
            evaluation = policy_evaluation_store.upsert(db, {
                "analysis_run_id": analysis_run.id,
                "policy_id": policy.id,
                "policy_engine_version": POLICY_ENGINE_VERSION,
                "policy_revision": policy.revision,
                "config_snapshot_json": policy_config.model_dump(),
                "evaluation_status": EvaluationStatus.FAILED.value,
                "error_message": traceback.format_exc()
            })
            if publisher:
                try:
                    publisher.publish(
                        result=None, 
                        summary="CodeGate policy evaluation failed.", 
                        text=traceback.format_exc()
                    )
                except:
                    pass
            return evaluation
            
    def _build_check_summary(self, db, evaluation, quality, risk, test_run=None, cov_report=None) -> str:
        q_val = f"{quality.overall_score:.2f} ({quality.grade})" if quality else "Not available"
        r_val = f"{risk.overall_risk:.2f} ({risk.risk_level})" if risk else "Not available"
        
        tests_total = "Not available"
        tests_passed = "Not available"
        tests_failed = "Not available"
        tests_skipped = "Not available"
        overall_cov = "Not available"
        changed_cov = "Not available"
        
        if test_run:
            if test_run.tests_total is not None:
                tests_total = str(test_run.tests_total)
            if test_run.tests_passed is not None:
                tests_passed = str(test_run.tests_passed)
            if test_run.tests_failed is not None:
                tests_failed = str(test_run.tests_failed)
            if test_run.tests_skipped is not None:
                tests_skipped = str((test_run.tests_skipped or 0) + (test_run.tests_errors or 0))
                
        if cov_report:
            if cov_report.line_coverage is not None:
                overall_cov = f"{cov_report.line_coverage:.2f}%"
            if cov_report.changed_line_coverage is not None:
                changed_cov = f"{cov_report.changed_line_coverage:.2f}%"
        
        summary_text = f"""### CodeGate Policy Evaluation
- **Decision:** {evaluation.decision}
- **Quality Score:** {q_val}
- **Risk Score:** {r_val}
- **Tests Total:** {tests_total}
- **Tests Passed:** {tests_passed}
- **Tests Failed:** {tests_failed}
- **Tests Skipped/Errors:** {tests_skipped}
- **Overall Coverage:** {overall_cov}
- **Changed-Code Coverage:** {changed_cov}
- **Blocking Rules:** {evaluation.blocked_rules_count}
- **Warning Rules:** {evaluation.warning_rules_count}

### Suggested Reviewers
"""
        try:
            from codegate.services.reviewer_service import reviewer_service
            rec = reviewer_service.get_latest(db, evaluation.analysis_run_id)
            if not rec:
                summary_text += "No suitable reviewer found.\n"
            elif rec["status"] == "SKIPPED":
                summary_text += "Disabled.\n"
            elif rec["status"] == "FAILED":
                summary_text += "Unavailable.\n"
            elif not rec["recommendations"]:
                summary_text += "No suitable reviewer found.\n"
            else:
                for i, r in enumerate(rec["recommendations"]):
                    score_str = f"{r['overall_score']:.1f}"
                    reasons = "; ".join(r["reasons"])
                    summary_text += f"{i+1}. @{r['provider_username']} — {score_str}\n   {reasons}\n\n"
        except Exception:
            summary_text += "Unavailable.\n"
            
        return summary_text

    def _build_check_text(self, evaluation) -> str:
        text = "### Detailed Policy Evaluation\n\n"
        if evaluation.flags_json:
            text += f"**Flags:** {', '.join(evaluation.flags_json)}\n\n"
            
        if evaluation.breakdown_json and "rules" in evaluation.breakdown_json:
            for rule in evaluation.breakdown_json["rules"]:
                status_emoji = "✅" if rule["status"] == "PASS" else ("⚠️" if rule["status"] == "WARNING" else "❌")
                text += f"#### {status_emoji} {rule['rule_name']}\n"
                text += f"- **Status:** {rule['status']}\n"
                text += f"- **Actual:** {rule['actual_value']}\n"
                text += f"- **Expected:** {rule['expected_value']}\n"
                text += f"- **Reason:** {rule['reason']}\n\n"
        return text

quality_policy_service = QualityPolicyService()
