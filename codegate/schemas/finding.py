from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from codegate.database.models import Severity, Source


class FindingBase(BaseModel):
    source: Source = Source.AI
    category: str
    severity: Severity = Severity.INFO
    rule_id: Optional[str] = None
    file_path: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    is_changed_file: Optional[bool] = None
    is_new_code: Optional[bool] = None
    title: str
    description: str
    recommendation: Optional[str] = None
    confidence: Optional[float] = None
    raw_data: Optional[Any] = None

class FindingResponse(FindingBase):
    id: int
    analysis_run_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FindingCreate(FindingBase):
    pass
