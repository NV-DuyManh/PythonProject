from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from codegate.database.models import Status, Trigger


class AnalysisRunBase(BaseModel):
    head_sha: str
    status: Status = Status.PENDING
    trigger: Trigger = Trigger.MANUAL

class AnalysisRunCreate(AnalysisRunBase):
    pass

class AnalysisRunResponse(AnalysisRunBase):
    id: int
    pull_request_id: int
    raw_output: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CodeMetricResponse(BaseModel):
    id: int
    analysis_run_id: int
    analyzer: str
    metric_name: str
    file_path: Optional[str] = None
    symbol: Optional[str] = None
    value: str
    grade: Optional[str] = None
    metadata_json: Optional[Any] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
