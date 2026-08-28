from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime
from codegate.database.models import Severity, Source

class FindingBase(BaseModel):
    analysis_run_id: int
    source: Source = Source.AI
    category: str
    severity: Severity = Severity.INFO
    rule_id: Optional[str] = None
    file_path: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    title: str
    description: str
    recommendation: Optional[str] = None
    confidence: Optional[float] = None
    raw_data: Optional[Any] = None

class FindingResponse(FindingBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
