from enum import Enum
from typing import Optional, List, Any
from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import JSON
from codegate.database.base import Base, TimestampMixin

# Use JSONB for postgres, fallback to JSON
class JSONType(JSON):
    pass

@compiles(JSONType, 'postgresql')
def compile_json_type(type_, compiler, **kw):
    return "JSONB"

class Status(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Trigger(str, Enum):
    WEBHOOK = "WEBHOOK"
    MANUAL = "MANUAL"
    PUSH = "PUSH"
    SCHEDULED = "SCHEDULED"

class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Source(str, Enum):
    AI = "AI"
    RUFF = "RUFF"
    BANDIT = "BANDIT"
    SEMGREP = "SEMGREP"
    RADON = "RADON"
    TEST = "TEST"
    COVERAGE = "COVERAGE"
    SYSTEM = "SYSTEM"


class AnalysisRun(Base, TimestampMixin):
    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    pull_request_id: Mapped[int] = mapped_column(ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    
    head_sha: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    status: Mapped[Status] = mapped_column(String(50), nullable=False, index=True)
    trigger: Mapped[Trigger] = mapped_column(String(50), nullable=False)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    ai_model: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    pull_request: Mapped["PullRequest"] = relationship("PullRequest", back_populates="analysis_runs")
    findings: Mapped[List["Finding"]] = relationship(
        "Finding", 
        back_populates="analysis_run", 
        cascade="all, delete-orphan"
    )


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    source: Mapped[Source] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[Severity] = mapped_column(String(50), nullable=False, index=True)
    
    rule_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    file_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    start_line: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    end_line: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    recommendation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    confidence: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    raw_data: Mapped[Optional[Any]] = mapped_column(JSONType, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="findings")
