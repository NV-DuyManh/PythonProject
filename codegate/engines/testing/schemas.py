from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class Framework(str, Enum):
    PYTEST = "PYTEST"

class ExecutorType(str, Enum):
    DISABLED = "DISABLED"
    LOCAL_TRUSTED = "LOCAL_TRUSTED"
    DOCKER = "DOCKER"

class ExecutionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    SKIPPED = "SKIPPED"

class TestOutcome(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

class JUnitMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    tests: int = 0
    passed: int = 0
    failures: int = 0
    errors: int = 0
    skipped: int = 0
    duration: float = 0.0

class CoverageMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    total_lines: int = 0
    covered_lines: int = 0
    missing_lines: int = 0
    line_coverage: Optional[float] = None
    branch_coverage: Optional[float] = None
    files: Optional[Dict[str, Any]] = None

class ChangedCoverageMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    total_lines: int = 0
    covered_lines: int = 0
    missing_lines: int = 0
    coverage_percent: Optional[float] = None
