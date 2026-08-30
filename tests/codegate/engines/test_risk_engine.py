import pytest
from codegate.engines.risk.engine import RiskScoreEngine
from codegate.database.models.analysis import Finding, CodeMetric, AnalyzerRun, Status, Severity, Source
from codegate.database.models.pull_request import PullRequest, PullRequestFile
from codegate.engines.risk.config import get_risk_level

def test_risk_security_boundaries():
    pr = PullRequest(additions=0, deletions=0, changed_files=0)
    
    f_low = Finding(id=1, source=Source.BANDIT, severity=Severity.LOW, title="L", is_changed_file=True)
    f_med = Finding(id=2, source=Source.BANDIT, severity=Severity.MEDIUM, title="M", is_changed_file=True)
    f_high = Finding(id=3, source=Source.BANDIT, severity=Severity.HIGH, title="H", is_changed_file=True)
    f_crit = Finding(id=4, source=Source.BANDIT, severity=Severity.CRITICAL, title="C", is_changed_file=True)
    
    # Test LOW (15)
    r = RiskScoreEngine.calculate(pr, [], [f_low], [], [])
    sec = [c for c in r.components if c.name == "security"][0]
    assert sec.risk == 15.0
    assert "HIGH_SECURITY_FINDING" not in r.flags
    
    # Test MEDIUM (35)
    r = RiskScoreEngine.calculate(pr, [], [f_med], [], [])
    sec = [c for c in r.components if c.name == "security"][0]
    assert sec.risk == 35.0
    assert "HIGH_SECURITY_FINDING" not in r.flags
    
    # Test HIGH (70)
    r = RiskScoreEngine.calculate(pr, [], [f_high], [], [])
    sec = [c for c in r.components if c.name == "security"][0]
    assert sec.risk == 70.0
    assert "HIGH_SECURITY_FINDING" in r.flags
    
    # Test CRITICAL (100)
    r = RiskScoreEngine.calculate(pr, [], [f_crit], [], [])
    sec = [c for c in r.components if c.name == "security"][0]
    assert sec.risk == 100.0
    assert "HIGH_SECURITY_FINDING" in r.flags

def test_risk_security_cap_100():
    pr = PullRequest(additions=0, deletions=0, changed_files=0)
    
    findings = [
        Finding(id=1, source=Source.BANDIT, severity=Severity.HIGH, title="H1", is_changed_file=True),
        Finding(id=2, source=Source.BANDIT, severity=Severity.HIGH, title="H2", is_changed_file=True),
    ] # 70 + 70 = 140 -> should cap at 100
    
    r = RiskScoreEngine.calculate(pr, [], findings, [], [])
    sec = [c for c in r.components if c.name == "security"][0]
    assert sec.risk == 100.0

def test_risk_security_historical_ignored():
    pr = PullRequest(additions=0, deletions=0, changed_files=0)
    
    findings = [
        Finding(id=1, source=Source.BANDIT, severity=Severity.CRITICAL, title="C1", is_changed_file=False),
        Finding(id=2, source=Source.BANDIT, severity=Severity.LOW, title="L1", is_changed_file=True),
    ]
    
    r = RiskScoreEngine.calculate(pr, [], findings, [], [])
    sec = [c for c in r.components if c.name == "security"][0]
    assert sec.risk == 15.0 # only LOW is counted
    assert sec.ignored_findings == 1
    assert sec.counted_findings == 1

def test_risk_security_bandit_status():
    pr = PullRequest(additions=0, deletions=0, changed_files=0)
    
    # FAILED -> null
    run_fail = AnalyzerRun(analyzer="BANDIT", status=Status.FAILED)
    r = RiskScoreEngine.calculate(pr, [], [], [], [run_fail])
    sec = [c for c in r.components if c.name == "security"][0]
    assert sec.risk is None
    assert sec.included is False
    assert "PARTIAL_ANALYSIS" in r.flags
    
    # TIMEOUT -> null
    run_timeout = AnalyzerRun(analyzer="BANDIT", status=Status.TIMEOUT)
    r2 = RiskScoreEngine.calculate(pr, [], [], [], [run_timeout])
    sec2 = [c for c in r2.components if c.name == "security"][0]
    assert sec2.risk is None
    
    # SUCCESS + no findings -> 0
    run_success = AnalyzerRun(analyzer="BANDIT", status=Status.COMPLETED)
    r3 = RiskScoreEngine.calculate(pr, [], [], [], [run_success])
    sec3 = [c for c in r3.components if c.name == "security"][0]
    assert sec3.risk == 0.0
    assert sec3.included is True

def test_risk_change_surface():
    # Boundary test lines:
    # 20 -> 5, 21 -> 15
    pr1 = PullRequest(additions=10, deletions=10, changed_files=0)
    pr2 = PullRequest(additions=10, deletions=11, changed_files=0)
    
    cs1 = [c for c in RiskScoreEngine.calculate(pr1, [], [], [], []).components if c.name == "change_surface"][0]
    cs2 = [c for c in RiskScoreEngine.calculate(pr2, [], [], [], []).components if c.name == "change_surface"][0]
    assert cs1.reasons[0].risk_contribution == 5 * 0.70
    assert cs2.reasons[0].risk_contribution == 15 * 0.70
    
    # Boundary test lines:
    # 50 -> 15, 51 -> 30
    # 100 -> 30, 101 -> 50
    # 250 -> 50, 251 -> 70
    # 500 -> 70, 501 -> 85
    # 1000 -> 85, 1001 -> 100
    
    # Boundary test files:
    # 1 -> 5, 2 -> 10, 3 -> 10, 4 -> 25, 7 -> 25, 8 -> 50, 15 -> 50, 16 -> 75, 30 -> 75, 31 -> 100
    pr_f1 = PullRequest(additions=0, deletions=0, changed_files=1)
    pr_f2 = PullRequest(additions=0, deletions=0, changed_files=2)
    pr_f3 = PullRequest(additions=0, deletions=0, changed_files=31)
    
    cs_f1 = [c for c in RiskScoreEngine.calculate(pr_f1, [], [], [], []).components if c.name == "change_surface"][0]
    cs_f2 = [c for c in RiskScoreEngine.calculate(pr_f2, [], [], [], []).components if c.name == "change_surface"][0]
    cs_f3 = [c for c in RiskScoreEngine.calculate(pr_f3, [], [], [], []).components if c.name == "change_surface"][0]
    
    assert cs_f1.reasons[1].risk_contribution == 5 * 0.30
    assert cs_f2.reasons[1].risk_contribution == 10 * 0.30
    assert cs_f3.reasons[1].risk_contribution == 100 * 0.30

def test_risk_sensitive_paths():
    pr = PullRequest(additions=0, deletions=0, changed_files=0)
    
    files = [
        PullRequestFile(filename="src/auth/login.py"), # Tier 1 -> 100
        PullRequestFile(filename="payment/service.py"), # Tier 1 -> 100
        PullRequestFile(filename="migrations/001.sql"), # Tier 2 -> 70
        PullRequestFile(filename=".github/workflows/deploy.yml"), # Tier 2 -> 70
        PullRequestFile(filename="config/settings.py"), # Tier 3 -> 40
        PullRequestFile(filename="README.md"), # None -> 0
    ]
    
    r = RiskScoreEngine.calculate(pr, files, [], [], [])
    sp = [c for c in r.components if c.name == "sensitive_path"][0]
    
    assert sp.risk == 100.0
    assert "SENSITIVE_AUTH_CHANGE" in r.flags

def test_risk_complexity():
    pr = PullRequest(additions=0, deletions=0, changed_files=0)
    
    metrics = [
        CodeMetric(id=1, analyzer=Source.RADON, metric_name="cyclomatic_complexity", grade="B"), # 0
        CodeMetric(id=2, analyzer=Source.RADON, metric_name="cyclomatic_complexity", grade="C"), # 25
        CodeMetric(id=3, analyzer=Source.RADON, metric_name="cyclomatic_complexity", grade="F"), # 100
    ]
    
    run_success = AnalyzerRun(analyzer="RADON", status=Status.COMPLETED)
    r = RiskScoreEngine.calculate(pr, [], [], metrics, [run_success])
    cx = [c for c in r.components if c.name == "complexity"][0]
    
    assert cx.risk == 100.0
    assert "HIGH_COMPLEXITY_SYMBOL" in r.flags

def test_risk_complexity_partial():
    pr = PullRequest(additions=0, deletions=0, changed_files=0)
    
    # Radon missing -> null
    r = RiskScoreEngine.calculate(pr, [], [], [], [])
    cx = [c for c in r.components if c.name == "complexity"][0]
    
    assert cx.risk is None
    assert cx.included is False
    assert r.is_complete is False

def test_risk_boundaries():
    assert get_risk_level(19.99) == "LOW"
    assert get_risk_level(20.0) == "MEDIUM"
    assert get_risk_level(39.99) == "MEDIUM"
    assert get_risk_level(40.0) == "HIGH"
    assert get_risk_level(69.99) == "HIGH"
    assert get_risk_level(70.0) == "CRITICAL"
    assert get_risk_level(100.0) == "CRITICAL"

def test_risk_determinism_and_quality_independence():
    pr = PullRequest(additions=10, deletions=5, changed_files=2)
    files = [PullRequestFile(filename="src/auth/login.py")]
    findings = [Finding(id=1, source=Source.BANDIT, severity=Severity.LOW, title="L", is_changed_file=True)]
    metrics = [CodeMetric(id=1, analyzer=Source.RADON, metric_name="cyclomatic_complexity", grade="C")]
    runs = [
        AnalyzerRun(analyzer="BANDIT", status=Status.COMPLETED),
        AnalyzerRun(analyzer="RADON", status=Status.COMPLETED)
    ]
    
    r1 = RiskScoreEngine.calculate(pr, files, findings, metrics, runs)
    r2 = RiskScoreEngine.calculate(pr, files, findings, metrics, runs)
    
    assert r1.overall_risk == r2.overall_risk
    assert r1.risk_level == r2.risk_level
    assert r1.model_dump() == r2.model_dump()
    
    # Risk does not depend on quality because QualityScore is not an input. 
    # Therefore it is naturally independent.
