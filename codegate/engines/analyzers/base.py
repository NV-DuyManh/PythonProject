import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from codegate.database.models.analysis import Source, Status
from codegate.engines.analyzers.schemas import AnalyzerResult


class BaseAnalyzer(ABC):
    """
    Abstract base class for static analyzers.
    """
    
    @property
    @abstractmethod
    def name(self) -> Source:
        """Return the unique Source enum for this analyzer."""
        pass
        
    @property
    @abstractmethod
    def command(self) -> List[str]:
        """Return the base command to execute the analyzer."""
        pass

    @abstractmethod
    def supports(self) -> bool:
        """Check if this analyzer can run (e.g. tool is installed)."""
        pass
        
    @abstractmethod
    def parse_output(self, stdout: str, stderr: str, returncode: int) -> AnalyzerResult:
        """
        Parse the tool's raw output into normalized findings and metrics.
        Should handle cases where the tool returns a non-zero exit code due to findings.
        """
        pass

    def run(self, workspace_path: str, changed_files: Optional[List[str]] = None) -> AnalyzerResult:
        """
        Execute the analyzer on the given workspace path.
        This base method handles the subprocess invocation and timeout,
        while delegating the parsing to the concrete analyzer.
        """
        import subprocess
        
        # We don't implement the subprocess run here directly because the orchestrator / runner
        # will handle the actual execution to inject timeouts properly.
        # This method could be used if analyzers ran independently, but in CodeGate we prefer
        # the StaticAnalysisRunner to execute the subprocess so it can handle timeout/cancellation gracefully.
        raise NotImplementedError("Execution is handled by StaticAnalysisRunner")
