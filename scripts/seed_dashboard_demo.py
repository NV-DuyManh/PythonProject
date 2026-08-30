import os
import sys
from datetime import datetime, timedelta, timezone

# Add the parent directory to sys.path so we can import codegate
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlmodel import Session, SQLModel, create_engine
from codegate.database.models import (
    Repository, PullRequest, AnalysisRun, 
    QualityScore, RiskScore, PolicyEvaluation,
    QualityComponent, RiskComponent, TestSummary, CoverageSummary,
    CodeFinding, ReviewerRecommendation
)
from codegate.database.session import engine

def seed_database():
    print("Seeding CodeGate database with demo data...")
    
    with Session(engine) as session:
        # Check if we already have data
        existing_prs = session.query(PullRequest).count()
        if existing_prs > 0:
            print(f"Database already contains {existing_prs} PullRequests. Skipping seed to prevent duplication.")
            return

        now = datetime.now(timezone.utc)
        
        # 1. Repositories
        repo1 = Repository(
            provider="github",
            owner="codegate",
            name="backend",
            url="https://github.com/codegate/backend",
            default_branch="main",
            created_at=now - timedelta(days=30),
            updated_at=now
        )
        repo2 = Repository(
            provider="github",
            owner="codegate",
            name="frontend-ui",
            url="https://github.com/codegate/frontend-ui",
            default_branch="main",
            created_at=now - timedelta(days=40),
            updated_at=now
        )
        repo3 = Repository(
            provider="github",
            owner="acme-corp",
            name="payment-gateway",
            url="https://github.com/acme-corp/payment-gateway",
            default_branch="main",
            created_at=now - timedelta(days=60),
            updated_at=now
        )
        
        session.add_all([repo1, repo2, repo3])
        session.commit()
        
        # Helper to create PR + Analysis
        def create_demo_pr(repo, number, title, author, state, days_ago, quality, risk, policy, tests=None, coverage=None):
            pr = PullRequest(
                repository_id=repo.id,
                number=number,
                title=title,
                author=author,
                state=state,
                base_branch="main",
                head_branch=f"feature/{title.replace(' ', '-').lower()}",
                head_sha=f"abcdef{number}123456",
                created_at=now - timedelta(days=days_ago),
                updated_at=now - timedelta(days=days_ago) + timedelta(hours=2)
            )
            session.add(pr)
            session.commit()
            
            run = AnalysisRun(
                pull_request_id=pr.id,
                trigger_event="pull_request_opened",
                status="completed",
                started_at=pr.created_at,
                completed_at=pr.updated_at
            )
            session.add(run)
            session.commit()
            
            # Quality
            q_score = QualityScore(
                analysis_run_id=run.id,
                overall_score=quality,
                grade="A" if quality >= 90 else "B" if quality >= 80 else "C" if quality >= 70 else "D" if quality >= 60 else "F"
            )
            session.add(q_score)
            session.commit()
            
            session.add_all([
                QualityComponent(score_id=q_score.id, category="Code Quality", score=min(100, quality + 2), weight=0.4),
                QualityComponent(score_id=q_score.id, category="Security", score=min(100, quality - 5), weight=0.3),
                QualityComponent(score_id=q_score.id, category="Testing", score=min(100, quality + 8), weight=0.2),
                QualityComponent(score_id=q_score.id, category="Complexity", score=min(100, quality - 12), weight=0.1),
            ])
            
            # Risk
            r_score = RiskScore(
                analysis_run_id=run.id,
                overall_score=risk,
                level="CRITICAL" if risk >= 90 else "HIGH" if risk >= 75 else "MEDIUM" if risk >= 50 else "LOW"
            )
            session.add(r_score)
            session.commit()
            
            session.add_all([
                RiskComponent(score_id=r_score.id, category="Security Surface", score=min(100, risk + 5), explanation="Analyzed data flow patterns."),
                RiskComponent(score_id=r_score.id, category="Change Size", score=min(100, max(0, risk - 20)), explanation="Lines changed across files."),
            ])
            
            # Policy
            policy_eval = PolicyEvaluation(
                analysis_run_id=run.id,
                decision=policy,
                reasons=[f"PR risk score {risk} evaluated.", f"Quality score {quality} evaluated."]
            )
            session.add(policy_eval)
            
            # Tests & Coverage
            if tests:
                test_sum = TestSummary(
                    analysis_run_id=run.id,
                    total_tests=tests['total'],
                    passed_tests=tests['passed'],
                    failed_tests=tests['failed'],
                    skipped_tests=tests.get('skipped', 0),
                    duration_seconds=12.5
                )
                session.add(test_sum)
                
            if coverage:
                cov_sum = CoverageSummary(
                    analysis_run_id=run.id,
                    overall_coverage=coverage['overall'],
                    changed_coverage=coverage['changed']
                )
                session.add(cov_sum)
                
            # Findings
            if policy == "BLOCK":
                session.add(CodeFinding(
                    analysis_run_id=run.id,
                    severity="HIGH",
                    category="Security",
                    title="Potential SQL Injection",
                    description="User input is concatenated directly into SQL query.",
                    file_path="src/db/queries.py",
                    line_number=42
                ))
            
            # Reviewers
            session.add(ReviewerRecommendation(
                analysis_run_id=run.id,
                reviewer_username="alice-dev",
                match_score=92.5,
                reasons=["CODEOWNER for 4 changed files", "Authored 12 commits in these files recently"]
            ))
            
            session.commit()
            
        # Add Demo PRs
        create_demo_pr(repo1, 128, "Improve authentication token validation", "alice-dev", "open", 1, 91, 28, "PASS", 
                       tests={'total': 124, 'passed': 124, 'failed': 0}, coverage={'overall': 85.2, 'changed': 92.0})
        create_demo_pr(repo1, 129, "Refactor core API routing", "bob-coder", "open", 2, 84, 43, "WARNING", 
                       tests={'total': 124, 'passed': 122, 'failed': 2}, coverage={'overall': 84.8, 'changed': 76.5})
        create_demo_pr(repo3, 45, "Payment permission refactor bypass", "charlie-hack", "open", 0, 74, 82, "BLOCK", 
                       tests={'total': 56, 'passed': 56, 'failed': 0}, coverage={'overall': 42.1, 'changed': 12.0})
        create_demo_pr(repo2, 88, "Update React components to Tailwind v4", "dana-design", "merged", 5, 95, 12, "PASS", 
                       tests={'total': 412, 'passed': 412, 'failed': 0}, coverage={'overall': 90.5, 'changed': 100.0})
        create_demo_pr(repo1, 130, "Add legacy SOAP endpoints", "evan-old", "open", 0, 62, 78, "BLOCK", 
                       tests={'total': 124, 'passed': 110, 'failed': 14}, coverage={'overall': 80.1, 'changed': 45.5})

        print("Successfully seeded demo data.")

if __name__ == "__main__":
    seed_database()
