RISK_CALCULATION_VERSION = "risk-v1"

CANONICAL_WEIGHTS = {
    "security": 0.40,
    "change_surface": 0.25,
    "sensitive_path": 0.20,
    "complexity": 0.15,
}

SECURITY_POINTS = {
    "LOW": 15,
    "MEDIUM": 35,
    "HIGH": 70,
    "CRITICAL": 100,
}

# Change Surface configurations
LINES_RISK_MAPPING = [
    (0, 0, 0),
    (1, 20, 5),
    (21, 50, 15),
    (51, 100, 30),
    (101, 250, 50),
    (251, 500, 70),
    (501, 1000, 85),
    (1001, float('inf'), 100)
]

FILES_RISK_MAPPING = [
    (0, 0, 0),
    (1, 1, 5),
    (2, 3, 10),
    (4, 7, 25),
    (8, 15, 50),
    (16, 30, 75),
    (31, float('inf'), 100)
]

# Sensitive paths logic
SENSITIVE_PATHS_TIERS = {
    "tier_1": {
        "risk": 100,
        "patterns": [
            "**/auth/**",
            "**/authentication/**",
            "**/security/**",
            "**/permissions/**",
            "**/payment/**",
            "**/payments/**",
            "**/billing/**",
            "**/authorization/**"
        ]
    },
    "tier_2": {
        "risk": 70,
        "patterns": [
            "**/migrations/**",
            "**/database/**",
            "**/infra/**",
            "**/infrastructure/**",
            "**/deploy/**",
            "**/deployment/**",
            ".github/workflows/**",
            "Dockerfile",
            "docker-compose*"
        ]
    },
    "tier_3": {
        "risk": 40,
        "patterns": [
            "**/config/**",
            "**/settings/**",
            "requirements*.txt",
            "pyproject.toml",
            "poetry.lock",
            "package-lock.json"
        ]
    }
}

COMPLEXITY_MAPPING = {
    "A": 0,
    "B": 0,
    "C": 25,
    "D": 50,
    "E": 75,
    "F": 100,
}

def get_risk_level(risk_score: float) -> str:
    """Deterministic risk level mapping"""
    if risk_score < 20:
        return "LOW"
    elif risk_score < 40:
        return "MEDIUM"
    elif risk_score < 70:
        return "HIGH"
    else:
        return "CRITICAL"
