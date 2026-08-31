import os
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set


class GitHistoryAnalyzer:
    @staticmethod
    def _run_git(repo_root: str, args: List[str]) -> str:
        cmd = ["git", "-C", repo_root] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

    @staticmethod
    def analyze_history(
        repo_root: str,
        base_sha: str,
        changed_files: List[str],
        history_days: int = 365,
        max_commits: int = 2000,
        now: Optional[datetime] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze git history using base_sha.
        Extracts expertise per author email.
        Returns dict: { email: { exact_commits: int, dir_commits: int, last_activity: datetime } }
        """
        if now is None:
            now = datetime.now(timezone.utc)
            
        # Get directories from changed files
        changed_dirs = set()
        for f in changed_files:
            dir_name = os.path.dirname(f)
            if dir_name:
                changed_dirs.add(dir_name)
                
        # Determine cutoff date
        since_date = f"{history_days} days ago"
        
        # We need: %aE (author email), %cI (commit date ISO), files changed
        # We'll use git log with --name-only to see changed files
        args = [
            "log",
            base_sha,
            f"--max-count={max_commits}",
            f"--since={since_date}",
            "--format=COMMIT|%aE|%cI",
            "--name-only"
        ]
        
        output = GitHistoryAnalyzer._run_git(repo_root, args)
        if not output:
            return {}
            
        expertise_map = {}
        
        current_email = None
        current_date = None
        
        lines = output.split("\n")
        for line in lines:
            if not line:
                continue
                
            if line.startswith("COMMIT|"):
                parts = line.split("|")
                if len(parts) >= 3:
                    current_email = parts[1].strip().lower()
                    date_str = parts[2].strip()
                    try:
                        current_date = datetime.fromisoformat(date_str)
                    except ValueError:
                        current_date = None
                        
                    if current_email not in expertise_map:
                        expertise_map[current_email] = {
                            "exact_commits": 0,
                            "dir_commits": 0,
                            "last_activity": current_date
                        }
                    else:
                        if current_date and (expertise_map[current_email]["last_activity"] is None or current_date > expertise_map[current_email]["last_activity"]):
                            expertise_map[current_email]["last_activity"] = current_date
            else:
                # It's a file name
                if current_email:
                    file_path = line.strip()
                    file_dir = os.path.dirname(file_path)
                    
                    if file_path in changed_files:
                        expertise_map[current_email]["exact_commits"] += 1
                        
                    if file_dir in changed_dirs:
                        expertise_map[current_email]["dir_commits"] += 1
                        
        return expertise_map
