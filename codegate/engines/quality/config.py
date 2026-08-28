CALCULATION_VERSION = "quality-v1"

CANONICAL_WEIGHTS = {
    "code_quality": 0.25,
    "security": 0.20,
    "testing": 0.20,
    "complexity": 0.15,
    "maintainability": 0.10,
    "ai_review": 0.10,
}

SEVERITY_PENALTIES = {
    "INFO": 0,
    "LOW": 2,
    "MEDIUM": 6,
    "HIGH": 15,
    "CRITICAL": 30,
}

COMPLEXITY_GRADE_PENALTIES = {
    "A": 0,
    "B": 0,
    "C": 3,
    "D": 8,
    "E": 15,
    "F": 25,
}

def get_grade(score: float) -> str:
    """Deterministic grade mapping"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    return "F"
