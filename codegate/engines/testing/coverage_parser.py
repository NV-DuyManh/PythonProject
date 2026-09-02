import json
import logging
from typing import Any, Dict, Optional

from codegate.engines.testing.schemas import CoverageMetrics

logger = logging.getLogger(__name__)

class CoverageParser:
    """Parses coverage.py JSON output to extract line and branch coverage."""
    
    @staticmethod
    def parse(json_content: str) -> Optional[CoverageMetrics]:
        if not json_content or not json_content.strip():
            return None
            
        try:
            data = json.loads(json_content)
            
            if "totals" not in data:
                logger.warning("Invalid coverage JSON: missing 'totals'")
                return None
                
            totals = data["totals"]
            
            metrics = CoverageMetrics()
            
            # Depending on coverage.py version, the keys vary slightly.
            # Usually: 'covered_lines', 'missing_lines', 'num_statements' (which acts as total_lines)
            metrics.covered_lines = totals.get("covered_lines", 0)
            metrics.missing_lines = totals.get("missing_lines", 0)
            metrics.total_lines = totals.get("num_statements", metrics.covered_lines + metrics.missing_lines)
            
            if metrics.total_lines > 0:
                metrics.line_coverage = totals.get("percent_covered", 
                                                    (metrics.covered_lines / metrics.total_lines) * 100)
            
            if "covered_branches" in totals and "num_branches" in totals:
                covered_b = totals["covered_branches"]
                num_b = totals["num_branches"]
                if num_b > 0:
                    metrics.branch_coverage = (covered_b / num_b) * 100
                    
            if "files" in data:
                metrics.files = data["files"]
                    
            return metrics
            
        except json.JSONDecodeError as e:
            logger.error(f"Malformed coverage JSON: {str(e)}")
            return None
