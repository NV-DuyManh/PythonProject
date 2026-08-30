import os
import re
from typing import List, Dict, Optional, Tuple

class CodeownersParser:
    @staticmethod
    def get_codeowners_path(repo_root: str) -> Optional[str]:
        """
        Check for CODEOWNERS file in order of GitHub precedence:
        1. .github/CODEOWNERS
        2. CODEOWNERS (root)
        3. docs/CODEOWNERS
        """
        paths = [
            os.path.join(repo_root, ".github", "CODEOWNERS"),
            os.path.join(repo_root, "CODEOWNERS"),
            os.path.join(repo_root, "docs", "CODEOWNERS"),
        ]
        for path in paths:
            if os.path.isfile(path):
                return path
        return None

    @staticmethod
    def parse_file(file_path: str) -> List[Tuple[str, List[str]]]:
        """
        Parse CODEOWNERS file and return a list of (pattern, owners).
        Skips comments and blank lines.
        """
        rules = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and blank lines
                    if not line or line.startswith("#"):
                        continue
                        
                    # Split by whitespace, first token is pattern, rest are owners
                    parts = line.split()
                    if len(parts) >= 2:
                        pattern = parts[0]
                        owners = parts[1:]
                        rules.append((pattern, owners))
        except Exception:
            pass
        return rules

    @staticmethod
    def match_pattern(file_path: str, pattern: str) -> bool:
        """
        Check if file_path matches CODEOWNERS pattern.
        Simplistic glob matching simulating GitHub CODEOWNERS rules.
        """
        # Normalize paths
        file_path = file_path.lstrip("/")
        
        # If pattern doesn't contain '/', it applies anywhere
        # e.g. *.py matches root.py and foo/bar.py
        if "/" not in pattern and not pattern.startswith("*"):
            # If it's just a directory name, e.g., 'docs', GitHub actually requires trailing slash or it means exact file.
            pass
            
        # Convert glob to regex
        # Escape special chars
        regex = pattern.replace(".", "\\.")
        
        # Handle /**/
        regex = regex.replace("/**/", "/.*/")
        # Handle **
        regex = regex.replace("**", ".*")
        # Handle *
        regex = regex.replace("*", "[^/]*")
        
        # If pattern starts with /, match from root
        if regex.startswith("/"):
            regex = "^" + regex[1:]
        else:
            # If pattern doesn't start with / and doesn't contain /, it matches anywhere
            if "/" not in pattern:
                regex = "(^|/)" + regex
            else:
                regex = "^" + regex
                
        # If pattern ends with /, it matches any file inside
        if regex.endswith("/"):
            regex = regex + ".*"
            
        # Ensure it matches exactly or is prefix for dir
        regex = regex + "$"
        
        try:
            return re.match(regex, file_path) is not None
        except Exception:
            return False

    @staticmethod
    def find_owners(file_path: str, rules: List[Tuple[str, List[str]]]) -> List[str]:
        """
        Find owners for a file based on GitHub CODEOWNERS rules.
        Last matching rule wins.
        """
        final_owners = []
        for pattern, owners in rules:
            if CodeownersParser.match_pattern(file_path, pattern):
                final_owners = owners
        return final_owners
