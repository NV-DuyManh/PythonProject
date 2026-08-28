import pytest
from codegate.engines.quality.engine import QualityScoreEngine
from codegate.database.models.analysis import Finding, CodeMetric, Severity, Source
from codegate.engines.quality.config import CALCULATION_VERSION

def test_quality_engine_no_findings():
    # If there are no findings, the score should be 100 for included dimensions
    findings = []
    metrics = []
    
    result = QualityScoreEngine.calculate(findings, metrics)
    
    assert result.overall_score == 100.0
    assert result.grade == "A"
    assert not result.is_complete
    assert "testing" in result.missing_dimensions
    assert "maintainability" in result.missing_dimensions
    
    # Check components
    comp_dict = {c.name: c for c in result.components}
    assert comp_dict["code_quality"].score == 100.0
    assert comp_dict["security"].score == 100.0
    assert comp_dict["ai_review"].score == 100.0
    assert comp_dict["complexity"].score == 100.0
    assert comp_dict["testing"].score is None

def test_quality_engine_severity_penalties():
    findings = [
        Finding(id=1, source=Source.RUFF, is_changed_file=True, severity=Severity.LOW, title="L"),
        Finding(id=2, source=Source.RUFF, is_changed_file=True, severity=Severity.MEDIUM, title="M"),
        Finding(id=3, source=Source.RUFF, is_changed_file=True, severity=Severity.HIGH, title="H"),
    ]
    metrics = []
    
    result = QualityScoreEngine.calculate(findings, metrics)
    comp_dict = {c.name: c for c in result.components}
    
    # Penalties: LOW (2) + MEDIUM (6) + HIGH (15) = 23
    assert comp_dict["code_quality"].score == 77.0
    assert comp_dict["code_quality"].penalty_total == 23.0

def test_quality_engine_historical_debt_excluded():
    findings = [
        # This one is not a changed file, should be ignored
        Finding(id=1, source=Source.RUFF, is_changed_file=False, severity=Severity.CRITICAL, title="C"),
        # This one is a changed file, should be counted
        Finding(id=2, source=Source.RUFF, is_changed_file=True, severity=Severity.HIGH, title="H"),
    ]
    metrics = []
    
    result = QualityScoreEngine.calculate(findings, metrics)
    comp_dict = {c.name: c for c in result.components}
    
    # Only HIGH (15) should be counted
    assert comp_dict["code_quality"].score == 85.0
    assert comp_dict["code_quality"].finding_count == 1

def test_quality_engine_partial_weight_normalization():
    # We will engineer scores:
    # Code Quality (weight 0.25) = 80
    # Security (weight 0.20) = 90
    # Complexity (weight 0.15) = 70
    # AI Review (weight 0.10) = 100
    
    findings = [
        # Code Quality: 20 penalty -> 1 HIGH (15) + 1 LOW (5? No, LOW is 2). Wait, let's just do 1 HIGH (15) + 1 LOW (2) + 3 INFO (0) ? That's 17.
        # Let's just do HIGH (15) + ? Let's do 1 LOW (2) + 3 MEDIUM (18) = 20
        Finding(id=1, source=Source.RUFF, is_changed_file=True, severity=Severity.LOW, title="L"),
        Finding(id=2, source=Source.RUFF, is_changed_file=True, severity=Severity.MEDIUM, title="M"),
        Finding(id=3, source=Source.RUFF, is_changed_file=True, severity=Severity.MEDIUM, title="M"),
        Finding(id=4, source=Source.RUFF, is_changed_file=True, severity=Severity.MEDIUM, title="M"),
        
        # Security: 10 penalty -> 1 MEDIUM (6) + 2 LOW (4) = 10
        Finding(id=5, source=Source.BANDIT, is_changed_file=True, severity=Severity.MEDIUM, title="M", rule_id="1"),
        Finding(id=6, source=Source.BANDIT, is_changed_file=True, severity=Severity.LOW, title="L", rule_id="2"),
        Finding(id=7, source=Source.BANDIT, is_changed_file=True, severity=Severity.LOW, title="L", rule_id="3"),
    ]
    
    metrics = [
        # Complexity: 30 penalty -> 2 E (30)
        CodeMetric(id=1, analyzer=Source.RADON, metric_name="cyclomatic_complexity", grade="E"),
        CodeMetric(id=2, analyzer=Source.RADON, metric_name="cyclomatic_complexity", grade="E"),
    ]
    
    result = QualityScoreEngine.calculate(findings, metrics)
    comp_dict = {c.name: c for c in result.components}
    
    assert comp_dict["code_quality"].score == 80.0
    assert comp_dict["security"].score == 90.0
    assert comp_dict["complexity"].score == 70.0
    assert comp_dict["ai_review"].score == 100.0
    
    # available weight = 0.25 + 0.20 + 0.15 + 0.10 = 0.70
    expected_score = (80 * 0.25 + 90 * 0.20 + 70 * 0.15 + 100 * 0.10) / 0.70
    
    assert result.available_weight == 0.70
    assert result.overall_score == round(expected_score, 2)
    assert not result.is_complete

def test_quality_engine_clamp():
    findings = [
        Finding(id=1, source=Source.RUFF, is_changed_file=True, severity=Severity.CRITICAL, title="C1"),
        Finding(id=2, source=Source.RUFF, is_changed_file=True, severity=Severity.CRITICAL, title="C2"),
        Finding(id=3, source=Source.RUFF, is_changed_file=True, severity=Severity.CRITICAL, title="C3"),
        Finding(id=4, source=Source.RUFF, is_changed_file=True, severity=Severity.CRITICAL, title="C4"),
    ]
    
    result = QualityScoreEngine.calculate(findings, [])
    comp_dict = {c.name: c for c in result.components}
    
    # Penalty is 120, score should clamp to 0
    assert comp_dict["code_quality"].score == 0.0

def test_quality_engine_grade_boundaries():
    # Helper to test overall score boundary
    from codegate.engines.quality.config import get_grade
    assert get_grade(90.0) == "A"
    assert get_grade(89.99) == "B"
    assert get_grade(80.0) == "B"
    assert get_grade(79.99) == "C"
    assert get_grade(70.0) == "C"
    assert get_grade(69.99) == "D"
    assert get_grade(60.0) == "D"
    assert get_grade(59.99) == "F"
    assert get_grade(0.0) == "F"

def test_quality_engine_reproducibility():
    findings = [
        Finding(id=1, source=Source.RUFF, is_changed_file=True, severity=Severity.LOW, title="L"),
    ]
    metrics = []
    
    r1 = QualityScoreEngine.calculate(findings, metrics)
    r2 = QualityScoreEngine.calculate(findings, metrics)
    
    assert r1.overall_score == r2.overall_score
    assert r1.grade == r2.grade
    assert r1.model_dump() == r2.model_dump()
