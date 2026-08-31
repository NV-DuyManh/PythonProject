"""
Demo seed script — adds PASS and BLOCK example PRs for acceptance testing.
Runs against the existing SQLite database used by CodeGate.
Does NOT delete or modify any existing LIVE records.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, timezone

from codegate.database.models import (
    AnalysisRun,
    Finding,
    PolicyDecision,
    PolicyEvaluation,
    PullRequest,
    QualityScore,
    RiskScore,
    Severity,
    Source,
    State,
    Status,
    Trigger,
)
from codegate.database.session import SessionLocal


def seed():
    db = SessionLocal()
    try:
        # Check if demo PRs already exist (idempotent)
        existing = db.query(PullRequest).filter(PullRequest.number == 100).first()
        if existing:
            print("Demo PASS/BLOCK PRs already seeded. Skipping.")
            return

        repo_id = 1  # codegate-e2e-demo
        now = datetime.now(timezone.utc)

        # ===== PASS PR =====
        pass_pr = PullRequest(
            repository_id=repo_id,
            number=100,
            title="feat: add user profile caching for improved load times",
            description="Adds Redis-based caching for user profiles to reduce database load.",
            author_username="demo-dev",
            source_branch="feature/profile-cache",
            target_branch="main",
            state=State.MERGED,
            head_sha="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
            base_sha="0000000000000000000000000000000000000000",
            additions=120,
            deletions=15,
            changed_files=4,
        )
        db.add(pass_pr)
        db.flush()

        pass_ar = AnalysisRun(
            pull_request_id=pass_pr.id,
            head_sha=pass_pr.head_sha,
            status=Status.COMPLETED,
            trigger=Trigger.WEBHOOK,
            started_at=now - timedelta(minutes=5),
            completed_at=now - timedelta(minutes=3),
            ai_model="groq/llama-3.3-70b-versatile",
        )
        db.add(pass_ar)
        db.flush()

        pass_quality = QualityScore(
            analysis_run_id=pass_ar.id,
            overall_score=95.5,
            grade="A",
            is_complete=True,
            available_weight=1.0,
            missing_dimensions=[],
            breakdown_json={
                "overall_score": 95.5, "grade": "A", "is_complete": True,
                "available_weight": 1.0, "missing_dimensions": [],
                "components": [
                    {"name": "code_quality", "score": 98.0, "canonical_weight": 0.25, "included": True, "finding_count": 0, "penalty_total": 2.0, "reasons": []},
                    {"name": "security", "score": 100.0, "canonical_weight": 0.2, "included": True, "finding_count": 0, "penalty_total": 0.0, "reasons": []},
                    {"name": "complexity", "score": 92.0, "canonical_weight": 0.15, "included": True, "finding_count": 0, "penalty_total": 8.0, "reasons": []},
                    {"name": "maintainability", "score": 88.0, "canonical_weight": 0.1, "included": True, "finding_count": 0, "penalty_total": 12.0, "reasons": []},
                    {"name": "testing", "score": 95.0, "canonical_weight": 0.2, "included": True, "finding_count": 0, "penalty_total": 5.0, "reasons": []},
                    {"name": "ai_review", "score": 96.0, "canonical_weight": 0.1, "included": True, "finding_count": 0, "penalty_total": 4.0, "reasons": []},
                ],
                "calculation_version": "quality-v1"
            },
            calculation_version="quality-v1"
        )
        db.add(pass_quality)

        pass_risk = RiskScore(
            analysis_run_id=pass_ar.id,
            overall_risk=2.1,
            risk_level="LOW",
            is_complete=True,
            available_weight=1.0,
            missing_dimensions=[],
            breakdown_json={
                "overall_risk": 2.1, "risk_level": "LOW", "is_complete": True,
                "available_weight": 1.0, "missing_dimensions": [],
                "components": [
                    {"name": "security", "risk": 0.0, "canonical_weight": 0.4, "effective_weight": 0.4, "included": True, "input_facts": {}, "counted_findings": 0, "ignored_findings": 0, "reasons": [], "flags": []},
                    {"name": "change_surface", "risk": 5.0, "canonical_weight": 0.25, "effective_weight": 0.25, "included": True, "input_facts": {"additions": 120, "deletions": 15, "changed_files": 4}, "counted_findings": 0, "ignored_findings": 0, "reasons": [{"description": "Lines risk: 3.5 (changed_lines=135)"}, {"description": "Files risk: 5 (changed_files=4)"}], "flags": []},
                    {"name": "sensitive_path", "risk": 0.0, "canonical_weight": 0.2, "effective_weight": 0.2, "included": True, "input_facts": {"files_checked": 4}, "counted_findings": 0, "ignored_findings": 0, "reasons": [], "flags": []},
                    {"name": "complexity", "risk": 3.0, "canonical_weight": 0.15, "effective_weight": 0.15, "included": True, "input_facts": {}, "counted_findings": 0, "ignored_findings": 0, "reasons": [], "flags": []},
                ],
                "flags": [],
                "calculation_version": "risk-v1"
            },
            calculation_version="risk-v1"
        )
        db.add(pass_risk)

        pass_policy = PolicyEvaluation(
            analysis_run_id=pass_ar.id,
            policy_id=1,
            policy_revision=1,
            policy_engine_version="policy-v1",
            decision=PolicyDecision.PASS,
            evaluation_status="COMPLETED",
            passed_rules_count=8,
            warning_rules_count=0,
            blocked_rules_count=0,
            flags_json=[],
            breakdown_json={
                "decision": "PASS",
                "rules": [
                    {"rule_id": "MIN_QUALITY_SCORE", "rule_name": "Minimum Quality Score", "status": "PASS", "actual_value": 95.5, "expected_value": ">= 80.0", "reason": "Quality score 95.5 meets the pass threshold."},
                    {"rule_id": "MAX_RISK_SCORE", "rule_name": "Maximum Risk Score", "status": "PASS", "actual_value": 2.1, "expected_value": "< 40.0", "reason": "Risk score 2.1 is below the warning threshold."},
                    {"rule_id": "MAX_CRITICAL_FINDINGS", "rule_name": "Max Critical Findings", "status": "PASS", "actual_value": 0, "expected_value": "<= 0", "reason": "Found 0 critical findings."},
                    {"rule_id": "MAX_HIGH_SECURITY_FINDINGS", "rule_name": "Max High/Critical Security Findings", "status": "PASS", "actual_value": 0, "expected_value": "<= 0", "reason": "Found 0 high/critical security findings."},
                ],
                "flags": []
            }
        )
        db.add(pass_policy)

        # ===== BLOCK PR =====
        block_pr = PullRequest(
            repository_id=repo_id,
            number=101,
            title="fix: disable SSL verification for internal API calls",
            description="Removes SSL certificate checks for faster internal communication.",
            author_username="junior-dev",
            source_branch="fix/disable-ssl",
            target_branch="main",
            state=State.OPEN,
            head_sha="f9e8d7c6b5a4f9e8d7c6b5a4f9e8d7c6b5a4f9e8",
            base_sha="0000000000000000000000000000000000000000",
            additions=450,
            deletions=200,
            changed_files=18,
        )
        db.add(block_pr)
        db.flush()

        block_ar = AnalysisRun(
            pull_request_id=block_pr.id,
            head_sha=block_pr.head_sha,
            status=Status.COMPLETED,
            trigger=Trigger.WEBHOOK,
            started_at=now - timedelta(minutes=10),
            completed_at=now - timedelta(minutes=7),
            ai_model="groq/llama-3.3-70b-versatile",
        )
        db.add(block_ar)
        db.flush()

        block_quality = QualityScore(
            analysis_run_id=block_ar.id,
            overall_score=42.3,
            grade="F",
            is_complete=True,
            available_weight=1.0,
            missing_dimensions=[],
            breakdown_json={
                "overall_score": 42.3, "grade": "F", "is_complete": True,
                "available_weight": 1.0, "missing_dimensions": [],
                "components": [
                    {"name": "code_quality", "score": 55.0, "canonical_weight": 0.25, "included": True, "finding_count": 3, "penalty_total": 45.0, "reasons": [{"finding_id": None, "severity": "HIGH", "penalty": 15.0, "reason": "Hardcoded credentials detected"}, {"finding_id": None, "severity": "HIGH", "penalty": 15.0, "reason": "SSL verification disabled"}, {"finding_id": None, "severity": "MEDIUM", "penalty": 15.0, "reason": "Missing error handling"}]},
                    {"name": "security", "score": 15.0, "canonical_weight": 0.2, "included": True, "finding_count": 2, "penalty_total": 85.0, "reasons": [{"finding_id": None, "severity": "CRITICAL", "penalty": 50.0, "reason": "SSL certificate verification disabled"}, {"finding_id": None, "severity": "HIGH", "penalty": 35.0, "reason": "Hardcoded API key in source"}]},
                    {"name": "complexity", "score": 60.0, "canonical_weight": 0.15, "included": True, "finding_count": 1, "penalty_total": 40.0, "reasons": []},
                    {"name": "maintainability", "score": 40.0, "canonical_weight": 0.1, "included": True, "finding_count": 2, "penalty_total": 60.0, "reasons": []},
                    {"name": "testing", "score": 30.0, "canonical_weight": 0.2, "included": True, "finding_count": 0, "penalty_total": 70.0, "reasons": [{"finding_id": None, "severity": None, "penalty": 70.0, "reason": "No tests for new security-critical code"}]},
                    {"name": "ai_review", "score": 25.0, "canonical_weight": 0.1, "included": True, "finding_count": 3, "penalty_total": 75.0, "reasons": [{"finding_id": None, "severity": "CRITICAL", "penalty": 50.0, "reason": "AI: Critical Security Vulnerability"}, {"finding_id": None, "severity": "HIGH", "penalty": 25.0, "reason": "AI: Poor Error Handling"}]},
                ],
                "calculation_version": "quality-v1"
            },
            calculation_version="quality-v1"
        )
        db.add(block_quality)

        block_risk = RiskScore(
            analysis_run_id=block_ar.id,
            overall_risk=78.5,
            risk_level="HIGH",
            is_complete=True,
            available_weight=1.0,
            missing_dimensions=[],
            breakdown_json={
                "overall_risk": 78.5, "risk_level": "HIGH", "is_complete": True,
                "available_weight": 1.0, "missing_dimensions": [],
                "components": [
                    {"name": "security", "risk": 95.0, "canonical_weight": 0.4, "effective_weight": 0.4, "included": True, "input_facts": {"total_points": 85.0}, "counted_findings": 2, "ignored_findings": 0, "reasons": [{"description": "Critical: SSL verification disabled"}, {"description": "High: Hardcoded credentials"}], "flags": ["CRITICAL_SECURITY"]},
                    {"name": "change_surface", "risk": 65.0, "canonical_weight": 0.25, "effective_weight": 0.25, "included": True, "input_facts": {"additions": 450, "deletions": 200, "changed_files": 18}, "counted_findings": 0, "ignored_findings": 0, "reasons": [{"description": "Lines risk: 45 (changed_lines=650)"}, {"description": "Files risk: 25 (changed_files=18)"}], "flags": ["LARGE_CHANGE"]},
                    {"name": "sensitive_path", "risk": 80.0, "canonical_weight": 0.2, "effective_weight": 0.2, "included": True, "input_facts": {"files_checked": 18}, "counted_findings": 3, "ignored_findings": 0, "reasons": [{"description": "Modified security configuration files"}, {"description": "Changes to authentication module"}], "flags": ["SENSITIVE_FILES"]},
                    {"name": "complexity", "risk": 45.0, "canonical_weight": 0.15, "effective_weight": 0.15, "included": True, "input_facts": {}, "counted_findings": 0, "ignored_findings": 0, "reasons": [], "flags": []},
                ],
                "flags": ["CRITICAL_SECURITY", "LARGE_CHANGE", "SENSITIVE_FILES"],
                "calculation_version": "risk-v1"
            },
            calculation_version="risk-v1"
        )
        db.add(block_risk)

        # Add critical findings
        findings_data = [
            ("CRITICAL", "SSL Certificate Verification Disabled", "security", "src/api/client.py", 42, "SSL verification has been disabled, exposing the application to man-in-the-middle attacks."),
            ("HIGH", "Hardcoded API Key", "security", "src/config/settings.py", 15, "API key is hardcoded in source code instead of using environment variables."),
            ("HIGH", "Missing Error Handling", "code_quality", "src/api/client.py", 78, "HTTP requests lack proper error handling and timeout configuration."),
            ("MEDIUM", "Large Function Complexity", "complexity", "src/api/client.py", 100, "Function exceeds cyclomatic complexity threshold of 10."),
        ]
        for sev, title, cat, fpath, line, desc in findings_data:
            f = Finding(
                analysis_run_id=block_ar.id,
                source=Source.AI if cat == "security" else Source.RUFF,
                category=cat,
                severity=Severity[sev],
                title=title,
                description=desc,
                file_path=fpath,
                start_line=line,
                is_changed_file=True,
                is_new_code=True,
                confidence=90,
            )
            db.add(f)

        block_policy = PolicyEvaluation(
            analysis_run_id=block_ar.id,
            policy_id=1,
            policy_revision=1,
            policy_engine_version="policy-v1",
            decision=PolicyDecision.BLOCK,
            evaluation_status="COMPLETED",
            passed_rules_count=2,
            warning_rules_count=1,
            blocked_rules_count=3,
            flags_json=["CRITICAL_SECURITY", "LOW_QUALITY"],
            breakdown_json={
                "decision": "BLOCK",
                "rules": [
                    {"rule_id": "QUALITY_AVAILABILITY", "rule_name": "Quality Score Availability", "status": "PASS", "actual_value": "Available", "expected_value": "Available", "reason": "Quality score is present."},
                    {"rule_id": "MIN_QUALITY_SCORE", "rule_name": "Minimum Quality Score", "status": "BLOCK", "actual_value": 42.3, "expected_value": ">= 60.0", "reason": "Quality score 42.3 is below the block threshold of 60.0."},
                    {"rule_id": "MAX_RISK_SCORE", "rule_name": "Maximum Risk Score", "status": "BLOCK", "actual_value": 78.5, "expected_value": "< 70.0", "reason": "Risk score 78.5 exceeds the block threshold of 70.0."},
                    {"rule_id": "MAX_CRITICAL_FINDINGS", "rule_name": "Max Critical Findings", "status": "BLOCK", "actual_value": 1, "expected_value": "<= 0", "reason": "Found 1 critical finding (max allowed: 0)."},
                    {"rule_id": "MAX_HIGH_SECURITY_FINDINGS", "rule_name": "Max High/Critical Security Findings", "status": "WARNING", "actual_value": 2, "expected_value": "<= 1", "reason": "Found 2 high/critical security findings."},
                    {"rule_id": "RISK_AVAILABILITY", "rule_name": "Risk Score Availability", "status": "PASS", "actual_value": "Available", "expected_value": "Available", "reason": "Risk score is present."},
                ],
                "flags": ["CRITICAL_SECURITY", "LOW_QUALITY"]
            }
        )
        db.add(block_policy)

        db.commit()
        print("✓ Demo PASS PR (#100) seeded successfully")
        print("✓ Demo BLOCK PR (#101) seeded successfully")
        print(f"  PASS PR id={pass_pr.id}, analysis_id={pass_ar.id}")
        print(f"  BLOCK PR id={block_pr.id}, analysis_id={block_ar.id}")

    except Exception as e:
        db.rollback()
        print(f"X Seed failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
