from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional
from datetime import datetime
from codegate.database.models import Provider

class RepositoryBase(BaseModel):
    provider: Provider
    owner: str
    name: str
    full_name: str
    url: str
    default_branch: str = "main"

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryUpdate(BaseModel):
    owner: Optional[str] = None
    name: Optional[str] = None
    full_name: Optional[str] = None
    url: Optional[str] = None
    default_branch: Optional[str] = None
    active: Optional[bool] = None

class RepositoryResponse(RepositoryBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
