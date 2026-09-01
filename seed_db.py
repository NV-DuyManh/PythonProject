import os
import sys

# Ensure we're in the right directory and path
sys.path.append(os.path.abspath("."))

from codegate.database.session import engine, SessionLocal
from codegate.database.base import Base
from codegate.database.models import User, Team, TeamMember, GitHubConnection, Repository, PullRequest, AnalysisRun, QualityScore, RiskScore, Finding
from codegate.database.models.team import Role
from datetime import datetime

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Create team
        team = db.query(Team).filter_by(id=1).first()
        if not team:
            team = Team(id=1, name="CodeGate HQ")
            db.add(team)
            db.commit()

        # Create user
        user = db.query(User).filter_by(id=1).first()
        if not user:
            user = User(
                id=1, 
                provider="github", 
                provider_user_id="github-123", 
                username="demouser", 
                email="demo@example.local", 
                is_active=True,
                active_workspace_id=team.id
            )
            db.add(user)
            db.commit()
            
            member = TeamMember(team_id=team.id, user_id=user.id, role=Role.ADMIN)
            db.add(member)
            db.commit()

        # Create Github connection
        conn = db.query(GitHubConnection).filter_by(id=1).first()
        if not conn:
            conn = GitHubConnection(id=1, workspace_id=team.id, installation_id=12345, account_login="demo-org", status="active")
            db.add(conn)
            db.commit()

        # Create Repositories
        if db.query(Repository).count() == 0:
            repos = [
                Repository(provider="github", owner="demo-org", name="backend-api", full_name="demo-org/backend-api", url="https://github.com/demo-org/backend-api", github_connection_id=conn.id, workspace_id=team.id, data_source="APP"),
                Repository(provider="github", owner="demo-org", name="frontend-app", full_name="demo-org/frontend-app", url="https://github.com/demo-org/frontend-app", github_connection_id=conn.id, workspace_id=team.id, data_source="APP"),
                Repository(provider="github", owner="demo-org", name="infra", full_name="demo-org/infra", url="https://github.com/demo-org/infra", github_connection_id=conn.id, workspace_id=team.id, data_source="APP"),
            ]
            db.add_all(repos)
            db.commit()

        repo1 = db.query(Repository).filter_by(name="backend-api").first()

        # Create PR
        if db.query(PullRequest).count() == 0:
            prs = [
                PullRequest(repository_id=repo1.id, provider_pr_id="101", number=101, title="Feat: Add strict auth checks", state="OPEN", author_username="demouser", source_branch="feat/auth", target_branch="main", head_sha="abcd123"),
                PullRequest(repository_id=repo1.id, provider_pr_id="102", number=102, title="Fix: Resolve memory leak in processor", state="OPEN", author_username="demouser", source_branch="fix/memleak", target_branch="main", head_sha="efgh456"),
            ]
            db.add_all(prs)
            db.commit()

        pr1 = db.query(PullRequest).filter_by(number=101).first()

        # Create Analysis Run
        if db.query(AnalysisRun).count() == 0:
            run = AnalysisRun(pull_request_id=pr1.id, head_sha="abcd123", status="completed", trigger="webhook")
            db.add(run)
            db.commit()

            q_score = QualityScore(analysis_run_id=run.id, overall_score=85, grade="B", available_weight=100.0, breakdown_json={"style": 90, "complexity": 80})
            r_score = RiskScore(analysis_run_id=run.id, overall_risk=20, risk_level="LOW", available_weight=100.0, breakdown_json={"security": 10, "bugs": 30})
            db.add(q_score)
            db.add(r_score)
            
            f1 = Finding(analysis_run_id=run.id, file_path="src/auth.py", line_number=42, severity="high", analyzer="bandit", issue_code="B105", description="Hardcoded password detected", category="security")
            f2 = Finding(analysis_run_id=run.id, file_path="src/auth.py", line_number=55, severity="medium", analyzer="ruff", issue_code="F401", description="Unused import os", category="style")
            db.add(f1)
            db.add(f2)
            db.commit()

        print("Database seeded successfully.")

        # Create AuthSession for Playwright
        import hashlib
        import secrets
        from datetime import datetime, timedelta, timezone
        from codegate.database.models import AuthSession
        
        session_token = "playwright-test-token-123456789"
        token_hash = hashlib.sha256(session_token.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(days=1)
        
        auth_session = AuthSession(
            user_id=1,
            token_hash=token_hash,
            expires_at=expires_at
        )
        db.add(auth_session)
        db.commit()
        print(f"Playwright token: {session_token}")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
