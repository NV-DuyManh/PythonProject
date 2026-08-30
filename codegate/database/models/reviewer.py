import json
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, Any
from codegate.database.base import Base

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

class ReviewerRecommendationConfig(Base, TimestampMixin):
    __tablename__ = "reviewer_recommendation_configs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    top_n: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    minimum_recommendation_score: Mapped[float] = mapped_column(Float, default=20.0, nullable=False)
    
    history_days: Mapped[int] = mapped_column(Integer, default=365, nullable=False)
    max_history_commits: Mapped[int] = mapped_column(Integer, default=2000, nullable=False)
    
    allow_external_codeowners: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    eligible_roles_json: Mapped[str] = mapped_column(String(512), default='["ADMIN", "MAINTAINER", "REVIEWER"]', nullable=False)
    
    revision: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    repository = relationship("Repository")


class ReviewerRecommendation(Base):
    __tablename__ = "reviewer_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    config_id: Mapped[int] = mapped_column(ForeignKey("reviewer_recommendation_configs.id", ondelete="CASCADE"), nullable=False)
    
    engine_version: Mapped[str] = mapped_column(String(50), nullable=False)
    config_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    
    eligible_candidate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    recommended_candidate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    is_complete: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    available_weight: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    
    missing_sources_json: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    unresolved_codeowners_json: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    
    config_snapshot_json: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    breakdown_json: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    
    error_message: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    analysis_run = relationship("AnalysisRun")
    candidates = relationship(
        "ReviewerRecommendationCandidate", 
        back_populates="recommendation",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("analysis_run_id", "config_id", "config_revision", "engine_version", name="uix_reviewer_logical_identity"),
    )


class ReviewerRecommendationCandidate(Base):
    __tablename__ = "reviewer_recommendation_candidates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recommendation_id: Mapped[int] = mapped_column(ForeignKey("reviewer_recommendations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    provider_username: Mapped[str] = mapped_column(String(255), nullable=False)
    
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    
    codeowners_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    exact_file_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    directory_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recency_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    exact_file_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    directory_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    file_coverage_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    matched_files_json: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    reasons_json: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    evidence_json: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    recommendation = relationship("ReviewerRecommendation", back_populates="candidates")
