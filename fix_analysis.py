with open('codegate/database/models/analysis.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
content = content.replace(
    'from sqlalchemy import String, Integer, ForeignKey, DateTime',
    'from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean'
)

# 2. Add Status.SUCCESS
content = content.replace(
    '    TIMEOUT = "TIMEOUT"',
    '    TIMEOUT = "TIMEOUT"\n    SUCCESS = "SUCCESS"'
)

# 4. Add fields to Finding
content = content.replace(
    '    end_line: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)',
    '    end_line: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)\n    is_changed_file: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)\n    is_new_code: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)'
)

# 5. Add relationships to AnalysisRun
content = content.replace(
    '    findings: Mapped[List["Finding"]] = relationship(',
    '    analyzer_runs: Mapped[List["AnalyzerRun"]] = relationship(\n        "AnalyzerRun", \n        back_populates="analysis_run", \n        cascade="all, delete-orphan"\n    )\n    code_metrics: Mapped[List["CodeMetric"]] = relationship(\n        "CodeMetric", \n        back_populates="analysis_run", \n        cascade="all, delete-orphan"\n    )\n    findings: Mapped[List["Finding"]] = relationship('
)

# 6. Add AnalyzerRun and CodeMetric at the end
content += '''
class AnalyzerRun(Base, TimestampMixin):
    __tablename__ = "analyzer_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    analyzer: Mapped[Source] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[Status] = mapped_column(String(50), nullable=False)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    metadata_json: Mapped[Optional[Any]] = mapped_column("metadata", JSONType, nullable=True)

    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="analyzer_runs")

class CodeMetric(Base, TimestampMixin):
    __tablename__ = "code_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    analyzer: Mapped[Source] = mapped_column(String(50), nullable=False, index=True)
    
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True, index=True)
    symbol: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    metadata_json: Mapped[Optional[Any]] = mapped_column("metadata", JSONType, nullable=True)

    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="code_metrics")
'''

with open('codegate/database/models/analysis.py', 'w', encoding='utf-8') as f:
    f.write(content)
