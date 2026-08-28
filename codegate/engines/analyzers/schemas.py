from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from codegate.database.models.analysis import Source, Severity, Status

class NormalizedFinding(BaseModel):
    analyzer: Source
    category: str
    severity: Severity
    rule_id: Optional[str] = None
    file_path: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    title: str
    description: str
    recommendation: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    is_new_code: Optional[bool] = None

class NormalizedMetric(BaseModel):
    analyzer: Source
    metric_name: str
    file_path: Optional[str] = None
    symbol: Optional[str] = None
    value: str
    grade: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AnalyzerResult(BaseModel):
    analyzer: Source
    status: Status
    findings: List[NormalizedFinding] = Field(default_factory=list)
    metrics: List[NormalizedMetric] = Field(default_factory=list)
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
