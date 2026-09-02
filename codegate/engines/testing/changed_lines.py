import asyncio
import logging
import os
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

class ChangedLinesResolver:
    """Resolves destination line numbers from git diffs for coverage intersection."""
    
    @staticmethod
    def _normalize_path(path: str) -> str:
        # Standardize path separators for matching coverage reports to git diffs
        return path.replace('\\', '/')
        
    @staticmethod
    def parse_hunk_header(hunk_header: str) -> tuple[int, int]:
        """
        Parses hunk header like @@ -10,2 +10,4 @@
        Extracts destination start line and count: (10, 4)
        """
        try:
            parts = hunk_header.split(" ")
            if len(parts) >= 3 and parts[2].startswith('+'):
                dest_str = parts[2][1:]
                if ',' in dest_str:
                    start, count = dest_str.split(',')
                    return int(start), int(count)
                else:
                    return int(dest_str), 1
        except Exception as e:
            logger.debug(f"Failed to parse hunk header '{hunk_header}': {str(e)}")
        return 0, 0
        
    @staticmethod
    async def get_changed_lines(repo_path: str, base_sha: str, head_sha: str) -> Dict[str, Set[int]]:
        """
        Runs git diff to extract changed lines per file.
        Returns mapping: {normalized_file_path: set(changed_line_numbers)}
        """
        changed_lines: Dict[str, Set[int]] = {}
        
        command = [
            "git",
            "diff",
            "--unified=0",
            "--no-color",
            f"{base_sha}...{head_sha}"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout_bytes, stderr_bytes = await process.communicate()
            if process.returncode != 0:
                logger.warning(f"Git diff failed with code {process.returncode}: {stderr_bytes.decode()}")
                return {}
                
            stdout = stdout_bytes.decode('utf-8')
            
            current_file = None
            for line in stdout.splitlines():
                if line.startswith("+++ b/"):
                    current_file = ChangedLinesResolver._normalize_path(line[6:])
                    if current_file not in changed_lines:
                        changed_lines[current_file] = set()
                elif line.startswith("@@ ") and current_file:
                    start, count = ChangedLinesResolver.parse_hunk_header(line)
                    if count > 0:
                        for i in range(start, start + count):
                            changed_lines[current_file].add(i)
                            
            return changed_lines
            
        except Exception as e:
            logger.error(f"Error extracting changed lines via git diff: {str(e)}")
            return {}

    @staticmethod
    def calculate_changed_coverage(coverage_metrics, changed_lines: Dict[str, Set[int]]) -> tuple[int, int, float]:
        """
        Calculates coverage only for changed lines.
        Returns: (covered_lines, total_changed_lines, coverage_percentage)
        """
        covered = 0
        total = 0
        
        if not coverage_metrics or not getattr(coverage_metrics, 'files', None):
            return 0, 0, 0.0
            
        for file_path, lines_set in changed_lines.items():
            if file_path in coverage_metrics.files:
                file_cov = coverage_metrics.files[file_path]
                executed = set(file_cov.get("executed_lines", []))
                missing = set(file_cov.get("missing_lines", []))
                
                for line in lines_set:
                    if line in executed:
                        total += 1
                        covered += 1
                    elif line in missing:
                        total += 1
                            
        percentage = (covered / total * 100) if total > 0 else 0.0
        return covered, total, percentage
