from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class TestConfigurationUpdate(BaseModel):
    enabled: Optional[bool] = None
    framework: Optional[str] = None
    executor_type: Optional[str] = None
    working_directory: Optional[str] = None
    test_paths: Optional[List[str]] = None
    pytest_args: Optional[List[str]] = None
    timeout_seconds: Optional[int] = None
    coverage_enabled: Optional[bool] = None
    coverage_source: Optional[List[str]] = None
    docker_image: Optional[str] = None

class TestConfigurationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    repository_id: int
    enabled: bool
    framework: str
    executor_type: str
    working_directory: Optional[str] = None
    test_paths_json: Optional[Any] = None
    pytest_args_json: Optional[Any] = None
    timeout_seconds: int
    coverage_enabled: bool
    coverage_source_json: Optional[Any] = None
    docker_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class TestRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    analysis_run_id: int
    execution_status: str
    test_outcome: str
    tests_total: Optional[int]
    tests_passed: Optional[int]
    tests_failed: Optional[int]
    tests_skipped: Optional[int]
    tests_errors: Optional[int]
    duration_ms: Optional[int]
    stdout_excerpt: Optional[str]
    stderr_excerpt: Optional[str]
    error_message: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

class CoverageReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    test_run_id: int
    coverage_version: Optional[str]
    line_coverage: Optional[float]
    branch_coverage: Optional[float]
    total_lines: Optional[int]
    covered_lines: Optional[int]
    missing_lines: Optional[int]
    changed_line_coverage: Optional[float]
    is_complete: bool
