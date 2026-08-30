import pytest
from codegate.engines.policy import QualityPolicyEngine, PolicyConfig, PolicyDecision
from codegate.database.models.analysis import QualityScore, RiskScore, Finding, Severity, Source

@pytest.fixture
def base_config():
    return PolicyConfig(
        quality_pass_threshold=80.0,
        quality_block_threshold=60.0,
        risk_warning_threshold=40.0,
        risk_block_threshold=70.0,
        max_critical_findings=0,
        max_high_security_findings=0,
        require_quality_score=False,
        require_risk_score=False,
        require_complete_quality=False,
        require_complete_risk=False
    )

def test_policy_pass(base_config):
    qs = QualityScore(overall_score=92, grade="A", is_complete=True)
    rs = RiskScore(overall_risk=18, risk_level="LOW", is_complete=True)
    findings = []
    
    result = QualityPolicyEngine.evaluate(base_config, qs, rs, findings)
    assert result.decision == PolicyDecision.PASS
    assert result.passed_rules_count > 0
    assert result.blocked_rules_count == 0

def test_policy_quality_warning(base_config):
    qs = QualityScore(overall_score=75, grade="B", is_complete=True)
    rs = RiskScore(overall_risk=10, risk_level="LOW", is_complete=True)
    
    result = QualityPolicyEngine.evaluate(base_config, qs, rs, [])
    assert result.decision == PolicyDecision.WARNING

def test_policy_quality_block(base_config):
    qs = QualityScore(overall_score=55, grade="C", is_complete=True)
    rs = RiskScore(overall_risk=10, risk_level="LOW", is_complete=True)
    
    result = QualityPolicyEngine.evaluate(base_config, qs, rs, [])
    assert result.decision == PolicyDecision.BLOCK

def test_policy_risk_warning(base_config):
    qs = QualityScore(overall_score=90, grade="A", is_complete=True)
    rs = RiskScore(overall_risk=55, risk_level="MEDIUM", is_complete=True)
    
    result = QualityPolicyEngine.evaluate(base_config, qs, rs, [])
    assert result.decision == PolicyDecision.WARNING

def test_policy_risk_block(base_config):
    qs = QualityScore(overall_score=95, grade="A", is_complete=True)
    rs = RiskScore(overall_risk=80, risk_level="CRITICAL", is_complete=True)
    
    result = QualityPolicyEngine.evaluate(base_config, qs, rs, [])
    assert result.decision == PolicyDecision.BLOCK

def test_policy_critical_finding_block(base_config):
    qs = QualityScore(overall_score=95, grade="A", is_complete=True)
    rs = RiskScore(overall_risk=10, risk_level="LOW", is_complete=True)
    
    f = Finding(severity=Severity.CRITICAL, is_new_code=True, source=Source.RUFF)
    
    result = QualityPolicyEngine.evaluate(base_config, qs, rs, [f])
    assert result.decision == PolicyDecision.BLOCK

def test_policy_historical_debt_ignored(base_config):
    qs = QualityScore(overall_score=95, grade="A", is_complete=True)
    rs = RiskScore(overall_risk=10, risk_level="LOW", is_complete=True)
    
    f = Finding(severity=Severity.CRITICAL, is_changed_file=False, is_new_code=False, source=Source.RUFF)
    
    result = QualityPolicyEngine.evaluate(base_config, qs, rs, [f])
    assert result.decision == PolicyDecision.PASS

def test_policy_high_security_block(base_config):
    qs = QualityScore(overall_score=95, grade="A", is_complete=True)
    rs = RiskScore(overall_risk=10, risk_level="LOW", is_complete=True)
    
    f = Finding(severity=Severity.HIGH, is_changed_file=True, source=Source.BANDIT)
    
    result = QualityPolicyEngine.evaluate(base_config, qs, rs, [f])
    assert result.decision == PolicyDecision.BLOCK

def test_policy_missing_quality(base_config):
    rs = RiskScore(overall_risk=10, risk_level="LOW", is_complete=True)
    
    # Not required -> warning
    result = QualityPolicyEngine.evaluate(base_config, None, rs, [])
    assert result.decision == PolicyDecision.WARNING
    assert "MISSING_QUALITY" in result.flags
    
    # Required -> block
    base_config.require_quality_score = True
    result = QualityPolicyEngine.evaluate(base_config, None, rs, [])
    assert result.decision == PolicyDecision.BLOCK

def test_policy_partial_quality(base_config):
    qs = QualityScore(overall_score=90, grade="A", is_complete=False)
    rs = RiskScore(overall_risk=10, risk_level="LOW", is_complete=True)
    
    # Not required -> warning
    result = QualityPolicyEngine.evaluate(base_config, qs, rs, [])
    assert result.decision == PolicyDecision.WARNING
    assert "PARTIAL_QUALITY" in result.flags
    
    # Required -> block
    base_config.require_complete_quality = True
    result = QualityPolicyEngine.evaluate(base_config, qs, rs, [])
    assert result.decision == PolicyDecision.BLOCK
