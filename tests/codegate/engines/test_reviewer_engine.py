import pytest
from datetime import datetime, timezone, timedelta
from codegate.engines.reviewer.schemas import RecommendationCandidate
from codegate.engines.reviewer.scoring import ReviewerScoringModel
from codegate.engines.reviewer.codeowners import CodeownersParser

def test_reviewer_scoring_tie_breaker():
    c1 = RecommendationCandidate(user_id=1, provider_username="Alice", overall_score=50.0, codeowners_score=40.0, exact_file_commits=10, directory_commits=0)
    c2 = RecommendationCandidate(user_id=2, provider_username="Bob", overall_score=50.0, codeowners_score=40.0, exact_file_commits=10, directory_commits=0)
    c3 = RecommendationCandidate(user_id=3, provider_username="Charlie", overall_score=50.0, codeowners_score=40.0, exact_file_commits=5, directory_commits=20)
    
    ranked = ReviewerScoringModel.rank_candidates([c2, c3, c1])
    
    assert ranked[0].provider_username == "Alice"
    assert ranked[1].provider_username == "Bob"
    assert ranked[2].provider_username == "Charlie"


def test_codeowners_parser():
    rules = [
        ("*", ["@global"]),
        ("docs/", ["@docs-team"]),
        ("src/**/*.py", ["@python-devs"]),
        ("src/auth/secret.py", ["@security", "@auth-lead"])
    ]
    
    # Global
    assert CodeownersParser.find_owners("README.md", rules) == ["@global"]
    
    # Docs
    assert CodeownersParser.find_owners("docs/index.md", rules) == ["@docs-team"]
    
    # Python
    assert CodeownersParser.find_owners("src/app/main.py", rules) == ["@python-devs"]
    
    # Secret
    assert CodeownersParser.find_owners("src/auth/secret.py", rules) == ["@security", "@auth-lead"]

def test_recency_score():
    assert ReviewerScoringModel.calculate_recency_score(0) == 100.0
    assert ReviewerScoringModel.calculate_recency_score(30) == 100.0
    assert ReviewerScoringModel.calculate_recency_score(31) == 80.0
    assert ReviewerScoringModel.calculate_recency_score(90) == 80.0
    assert ReviewerScoringModel.calculate_recency_score(91) == 50.0
    assert ReviewerScoringModel.calculate_recency_score(180) == 50.0
    assert ReviewerScoringModel.calculate_recency_score(181) == 20.0
    assert ReviewerScoringModel.calculate_recency_score(365) == 20.0
    assert ReviewerScoringModel.calculate_recency_score(366) == 0.0
