import os
import sys
import random
from datetime import datetime, timedelta, timezone
import json

# Add the parent directory to sys.path so we can import codegate
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from sqlalchemy import select
from codegate.database.session import engine
from codegate.database.models import (
    Repository, PullRequest, AnalysisRun, 
    QualityScore, RiskScore, PolicyEvaluation,
    TestRun, CoverageReport,
    Finding, Status, Trigger, PolicyDecision,
    QualityPolicy, TestConfiguration, ReviewerRecommendationConfig,
    ReviewerRecommendation, ReviewerRecommendationCandidate,
    Team, TeamMember, User
)
from codegate.config import settings

def is_safe_to_seed(session: Session) -> bool:
    db_url = str(engine.url)
    if "sqlite" not in db_url:
        print(f"ABORT: Seed script is only safe for local SQLite development. Detected: {db_url}")
        return False
        
    repo_count = session.execute(select(Repository)).scalars().all()
    if len(repo_count) > 0:
        names = {r.name for r in repo_count}
        if not names.issubset({"codegate-core", "identity-service", "payment-platform"}):
            print("ABORT: Database contains non-demo business data. Use an empty database to seed.")
            return False
            
    return True

def clear_existing_demo(session: Session):
    from sqlalchemy import text
    session.execute(text("PRAGMA foreign_keys = ON;"))
    session.commit()
    session.query(Repository).filter(Repository.name.in_(["codegate-core", "identity-service", "payment-platform"])).delete()
    session.query(User).filter(User.username.in_(["alice", "bob", "carol", "david"])).delete()
    session.commit()

def seed_database():
    print("Seeding CodeGate database with demo data...")
    
    with Session(engine) as session:
        if not is_safe_to_seed(session):
            return
            
        clear_existing_demo(session)

        now = datetime.now(timezone.utc)
        
        # Create Users
        users = [
            User(provider="github", provider_user_id="1", username="alice", email="alice@demo.local"),
            User(provider="github", provider_user_id="2", username="bob", email="bob@demo.local"),
            User(provider="github", provider_user_id="3", username="carol", email="carol@demo.local"),
            User(provider="github", provider_user_id="4", username="david", email="david@demo.local")
        ]
        session.add_all(users)
        session.commit()

        # Repositories
        repo1 = Repository(provider="GITHUB", owner="codegate", name="codegate-core", full_name="codegate/codegate-core", url="https://github.com/codegate/codegate-core", default_branch="main", created_at=now - timedelta(days=60), updated_at=now)
        repo2 = Repository(provider="GITHUB", owner="codegate", name="identity-service", full_name="codegate/identity-service", url="https://github.com/codegate/identity-service", default_branch="main", created_at=now - timedelta(days=90), updated_at=now)
        repo3 = Repository(provider="GITHUB", owner="codegate", name="payment-platform", full_name="codegate/payment-platform", url="https://github.com/codegate/payment-platform", default_branch="main", created_at=now - timedelta(days=120), updated_at=now)
        
        session.add_all([repo1, repo2, repo3])
        session.commit()
        
        # Configs
        q_policy = QualityPolicy(repository_id=repo1.id, name="Default Policy", policy_engine_version="1.0", revision=1, quality_pass_threshold=80.0, quality_block_threshold=60.0, active=True, created_at=now)
        t_config = TestConfiguration(repository_id=repo1.id, enabled=True, framework="PYTEST", executor_type="LOCAL", timeout_seconds=900, coverage_enabled=True, created_at=now)
        r_config = ReviewerRecommendationConfig(repository_id=repo1.id, enabled=True, top_n=3, minimum_recommendation_score=20.0, history_days=365, max_history_commits=2000, allow_external_codeowners=False, revision=1, created_at=now)
        session.add_all([q_policy, t_config, r_config])
        session.commit()
        
        pr_counter = 1
        
        def create_analysis(pr, days_ago, quality, risk, policy, tests=None, coverage=None, findings=None, reviewers=None):
            run_time = now - timedelta(days=days_ago)
            run = AnalysisRun(
                pull_request_id=pr.id,
                head_sha=pr.head_sha,
                trigger=Trigger.WEBHOOK,
                status=Status.COMPLETED,
                started_at=run_time,
                completed_at=run_time + timedelta(minutes=5)
            )
            session.add(run)
            session.commit()
            
            # Quality
            grade = "A" if quality >= 90 else "B" if quality >= 80 else "C" if quality >= 70 else "D" if quality >= 60 else "F"
            q_score = QualityScore(
                analysis_run_id=run.id, overall_score=quality, grade=grade, is_complete=True, available_weight=1.0,
                code_quality_score=min(100, quality+5), security_score=min(100, quality-5), testing_score=min(100, quality+2),
                complexity_score=min(100, quality-2), maintainability_score=min(100, quality), ai_review_score=min(100, quality+1),
                calculation_version="1.0", breakdown_json={"details": "quality breakdown demo"}
            )
            session.add(q_score)
            
            # Risk
            level = "CRITICAL" if risk >= 90 else "HIGH" if risk >= 75 else "MEDIUM" if risk >= 50 else "LOW"
            r_score = RiskScore(
                analysis_run_id=run.id, overall_risk=risk, risk_level=level, is_complete=True, available_weight=1.0,
                change_surface_risk=min(100, risk+10), sensitive_path_risk=min(100, risk+5), security_risk=min(100, risk-5),
                complexity_risk=min(100, risk), calculation_version="1.0", breakdown_json={"details": "risk breakdown demo"}
            )
            session.add(r_score)
            
            # Policy
            decision = PolicyDecision.PASS if policy == "PASS" else PolicyDecision.WARNING if policy == "WARNING" else PolicyDecision.BLOCK
            reasons = []
            if decision == PolicyDecision.PASS: reasons = ["Quality score satisfies threshold.", "Risk score below warning threshold.", "Tests passed."]
            elif decision == PolicyDecision.WARNING: reasons = ["Changed-code coverage is below warning threshold."]
            else: reasons = ["PR risk exceeds blocking threshold." if risk >= 75 else "HIGH security finding exists.", "Test suite contains failures." if tests and tests.get('failed',0) > 0 else ""]
            reasons = [r for r in reasons if r]
            
            policy_eval = PolicyEvaluation(analysis_run_id=run.id, decision=decision, breakdown_json={"reasons": reasons}, policy_id=q_policy.id, policy_engine_version="1.0", policy_revision=1, evaluation_status="COMPLETED")
            session.add(policy_eval)
            
            # Tests
            if tests:
                test_run = TestRun(
                    analysis_run_id=run.id, test_configuration_id=t_config.id,
                    runner_version="1.0", framework="pytest", executor_type="local",
                    execution_status="COMPLETED", test_outcome=tests['outcome'],
                    tests_total=tests.get('total', 0), tests_passed=tests.get('passed', 0),
                    tests_failed=tests.get('failed', 0), tests_skipped=tests.get('skipped', 0)
                )
                session.add(test_run)
                
            # Coverage
            if coverage and tests:
                session.flush() # ensure test_run.id is available
                cov = CoverageReport(
                    test_run_id=test_run.id,
                    coverage_version="1.0",
                    line_coverage=coverage.get('overall'),
                    changed_line_coverage=coverage.get('changed'),
                    missing_lines=10,
                    is_complete=True
                )
                session.add(cov)
                
            # Findings
            if findings:
                for f in findings:
                    finding = Finding(
                        analysis_run_id=run.id, source=f.get('tool', 'pr-agent'),
                        rule_id=f.get('rule', 'RULE1'), severity=f['severity'], category=f['category'],
                        title=f['title'], description=f.get('desc', 'Description'),
                        file_path=f.get('file', 'src/main.py'), start_line=f.get('line', 1),
                        is_changed_file=f.get('is_changed', True), is_new_code=f.get('is_new', True)
                    )
                    session.add(finding)
                    
            # Reviewer
            if reviewers:
                rec = ReviewerRecommendation(analysis_run_id=run.id, config_id=r_config.id, engine_version="1.0", config_revision=1, status="COMPLETED")
                session.add(rec)
                session.commit()
                for i, r in enumerate(reviewers):
                    cand = ReviewerRecommendationCandidate(
                        recommendation_id=rec.id, user_id=r['user'].id, provider_username=r['user'].username,
                        rank=i+1, overall_score=r['score'],
                        reasons_json='["Authored changes", "CODEOWNER"]'
                    )
                    session.add(cand)
                    
            session.commit()
            
        def create_pr(repo, title, author, state, created_days_ago, runs_data):
            nonlocal pr_counter
            pr = PullRequest(
                repository_id=repo.id, number=pr_counter, title=title, author_username=author,
                state=state.upper(), target_branch="main", source_branch=f"feat-{pr_counter}",
                head_sha=f"abcdef{pr_counter}", created_at=now - timedelta(days=created_days_ago),
                updated_at=now - timedelta(days=created_days_ago-1),
                additions=100, deletions=20, changed_files=5
            )
            pr_counter += 1
            session.add(pr)
            session.commit()
            
            for run_data in runs_data:
                create_analysis(pr, **run_data)

        # PR 1 (repo1): MULTIPLE ANALYSES (Trend)
        create_pr(repo1, "Core logic optimization", "alice", "open", 25, [
            {'days_ago': 25, 'quality': 63, 'risk': 78, 'policy': "BLOCK", 'tests': {'outcome': 'FAILED', 'total': 100, 'passed': 95, 'failed': 5}, 'coverage': {'overall': 81.0, 'changed': 45.0}, 'findings': [{'severity': 'HIGH', 'category': 'BUG', 'title': 'Null pointer risk', 'is_changed': True, 'tool': 'Ruff'}], 'reviewers': [{'user': users[1], 'score': 95.0}]},
            {'days_ago': 24, 'quality': 82, 'risk': 47, 'policy': "WARNING", 'tests': {'outcome': 'PASSED', 'total': 100, 'passed': 100, 'failed': 0}, 'coverage': {'overall': 82.0, 'changed': 68.0}, 'reviewers': [{'user': users[1], 'score': 95.0}]},
            {'days_ago': 23, 'quality': 94, 'risk': 12, 'policy': "PASS", 'tests': {'outcome': 'PASSED', 'total': 100, 'passed': 100, 'failed': 0}, 'coverage': {'overall': 83.5, 'changed': 92.0}, 'reviewers': [{'user': users[1], 'score': 95.0}]}
        ])
        
        # PR 2 (repo2): BLOCK due to SECURITY
        create_pr(repo2, "Implement OAuth2 login", "bob", "open", 20, [
            {'days_ago': 20, 'quality': 94, 'risk': 78, 'policy': "BLOCK", 'tests': {'outcome': 'PASSED', 'total': 86, 'passed': 86, 'failed': 0}, 'coverage': {'overall': 95.0, 'changed': 98.0}, 
             'findings': [{'severity': 'CRITICAL', 'category': 'SECURITY', 'title': 'Hardcoded JWT secret', 'file': 'auth/oauth.py', 'is_changed': True, 'is_new': True, 'tool': 'Bandit'}], 
             'reviewers': [{'user': users[2], 'score': 98.5}, {'user': users[0], 'score': 82.0}]}
        ])
        
        # PR 3 (repo3): WARNING due to Coverage
        create_pr(repo3, "Add Stripe payment webhook", "david", "open", 18, [
            {'days_ago': 18, 'quality': 88, 'risk': 28, 'policy': "WARNING", 'tests': {'outcome': 'PASSED', 'total': 132, 'passed': 130, 'skipped': 2, 'failed': 0}, 'coverage': {'overall': 76.0, 'changed': 55.0}, 
             'reviewers': [{'user': users[1], 'score': 88.0}]}
        ])
        
        # PR 4 (repo1): Tests unavailable
        create_pr(repo1, "Update README docs", "carol", "merged", 15, [
            {'days_ago': 15, 'quality': 98, 'risk': 5, 'policy': "PASS", 'tests': {'outcome': 'UNKNOWN', 'total': 0}, 'coverage': {'overall': 83.5, 'changed': None}, 
             'reviewers': [{'user': users[0], 'score': 70.0}]}
        ])
        
        # PASS
        create_pr(repo1, "Refactor database models", "alice", "merged", 12, [{'days_ago': 12, 'quality': 91, 'risk': 20, 'policy': "PASS", 'tests': {'outcome': 'PASSED', 'total': 150, 'passed': 150}, 'coverage': {'overall': 85.0, 'changed': 88.0}}])
        create_pr(repo2, "Update React to 19", "bob", "open", 10, [{'days_ago': 10, 'quality': 85, 'risk': 35, 'policy': "PASS", 'tests': {'outcome': 'PASSED', 'total': 200, 'passed': 200}, 'coverage': {'overall': 90.0, 'changed': 75.0}}])
        create_pr(repo3, "Add retry logic for payments", "david", "merged", 8, [{'days_ago': 8, 'quality': 96, 'risk': 15, 'policy': "PASS", 'tests': {'outcome': 'PASSED', 'total': 80, 'passed': 80}, 'coverage': {'overall': 78.0, 'changed': 100.0}}])
        create_pr(repo1, "Clean up unused dependencies", "carol", "merged", 8, [{'days_ago': 8, 'quality': 98, 'risk': 10, 'policy': "PASS", 'tests': {'outcome': 'PASSED', 'total': 120, 'passed': 120}, 'coverage': {'overall': 85.0, 'changed': 100.0}}])
        create_pr(repo2, "Fix typo in onboarding email", "alice", "merged", 7, [{'days_ago': 7, 'quality': 99, 'risk': 2, 'policy': "PASS", 'tests': {'outcome': 'PASSED', 'total': 100, 'passed': 100}, 'coverage': {'overall': 85.0, 'changed': None}}])
        
        # WARNING
        create_pr(repo1, "Add redis caching layer", "bob", "open", 7, [{'days_ago': 7, 'quality': 81, 'risk': 47, 'policy': "WARNING", 'tests': {'outcome': 'PASSED', 'total': 155, 'passed': 155}, 'coverage': {'overall': 84.0, 'changed': 62.0}}])
        create_pr(repo2, "Migrate to Tailwind CSS", "alice", "merged", 6, [{'days_ago': 6, 'quality': 78, 'risk': 30, 'policy': "WARNING", 'tests': {'outcome': 'PASSED', 'total': 200, 'passed': 200}, 'coverage': {'overall': 88.0, 'changed': 58.0}}])
        create_pr(repo3, "Support new currency SGD", "david", "open", 5, [{'days_ago': 5, 'quality': 82, 'risk': 42, 'policy': "WARNING", 'tests': {'outcome': 'PASSED', 'total': 95, 'passed': 95}, 'coverage': {'overall': 75.0, 'changed': 65.0}, 'findings': [{'severity': 'LOW', 'category': 'CODE_QUALITY', 'title': 'Long function', 'is_changed': True, 'tool': 'Ruff'}]}])
        create_pr(repo1, "Implement pagination for dashboard", "carol", "open", 4, [{'days_ago': 4, 'quality': 79, 'risk': 48, 'policy': "WARNING", 'tests': {'outcome': 'PASSED', 'total': 110, 'passed': 110}, 'coverage': {'overall': 82.0, 'changed': 55.0}}])
        
        # BLOCK
        create_pr(repo1, "Implement async processing", "carol", "open", 4, [{'days_ago': 4, 'quality': 52, 'risk': 85, 'policy': "BLOCK", 'tests': {'outcome': 'FAILED', 'total': 160, 'passed': 150, 'failed': 10}, 'coverage': {'overall': 82.0, 'changed': 40.0}}])
        create_pr(repo2, "Add user impersonation", "bob", "closed", 3, [{'days_ago': 3, 'quality': 74, 'risk': 91, 'policy': "BLOCK", 'tests': {'outcome': 'PASSED', 'total': 210, 'passed': 210}, 'coverage': {'overall': 90.0, 'changed': 80.0}, 'findings': [{'severity': 'HIGH', 'category': 'SECURITY', 'title': 'Insecure direct object reference', 'file': 'security/impersonate.ts', 'is_changed': True, 'tool': 'AI Review'}]}])
        create_pr(repo3, "Bypass fraud check for VIPs", "david", "closed", 1, [{'days_ago': 1, 'quality': 63, 'risk': 95, 'policy': "BLOCK", 'tests': {'outcome': 'PASSED', 'total': 100, 'passed': 100}, 'coverage': {'overall': 74.0, 'changed': 0.0}, 'findings': [{'severity': 'CRITICAL', 'category': 'SECURITY', 'title': 'Business logic bypass', 'file': 'payment/fraud.py', 'is_changed': True, 'tool': 'AI Review'}]}])
        create_pr(repo1, "Update root CA certificates", "alice", "open", 1, [{'days_ago': 1, 'quality': 85, 'risk': 92, 'policy': "BLOCK", 'tests': {'outcome': 'PASSED', 'total': 100, 'passed': 100}, 'coverage': {'overall': 80.0, 'changed': 100.0}, 'findings': [{'severity': 'HIGH', 'category': 'SECURITY', 'title': 'Weak cipher suite', 'is_changed': True, 'tool': 'Bandit'}]}])
        
        # Multi-analysis block -> pass
        create_pr(repo1, "Fix memory leak in background worker", "alice", "merged", 1, [
            {'days_ago': 1, 'quality': 68, 'risk': 64, 'policy': "BLOCK", 'tests': {'outcome': 'FAILED', 'total': 165, 'passed': 164, 'failed': 1}, 'coverage': {'overall': 82.0, 'changed': 50.0}},
            {'days_ago': 0, 'quality': 92, 'risk': 25, 'policy': "PASS", 'tests': {'outcome': 'PASSED', 'total': 165, 'passed': 165}, 'coverage': {'overall': 82.2, 'changed': 95.0}}
        ])

        print("Successfully seeded realistic demo data.")

if __name__ == "__main__":
    seed_database()
