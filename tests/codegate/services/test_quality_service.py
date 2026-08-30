import pytest
from codegate.engines.quality.engine import QualityScoreEngine
from codegate.database.models.analysis import Finding, CodeMetric

def test_quality_score_testing_cases():
    findings = []
    metrics = []

    # Case A: tests FAILED -> testing_score = 0
    res_a = QualityScoreEngine.calculate(findings, metrics, testing_score=0.0)
    # Check that the overall score is not 0 just because tests failed
    # testing_score is 0, others are 100
    # testing weight is 20%. Overall should be ~80% if everything else is perfect.
    assert res_a.overall_score > 0.0
    testing_comp_a = next(c for c in res_a.components if c.name == "testing")
    assert testing_comp_a.score == 0.0

    # Case B: tests PASSED, changed coverage = 82.5 -> testing_score = 82.5
    res_b = QualityScoreEngine.calculate(findings, metrics, testing_score=82.5)
    testing_comp_b = next(c for c in res_b.components if c.name == "testing")
    assert testing_comp_b.score == 82.5

    # Case C/D: tests PASSED no coverage, OR runner failed -> testing_score = None
    res_c = QualityScoreEngine.calculate(findings, metrics, testing_score=None)
    testing_comp_c = next(c for c in res_c.components if c.name == "testing")
    assert not testing_comp_c.included
    assert testing_comp_c.score is None
    # Verify overall score distributes the missing 20%
    assert res_c.overall_score == 100.0
