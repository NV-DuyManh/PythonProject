from typing import Dict, Any, List
from codegate.schemas.finding import FindingCreate
from codegate.database.models.analysis import Source, Severity
import json

class PRAgentNormalizer:
    """
    Normalizes the structured data from PR-Agent into CodeGate schemas.
    """

    @staticmethod
    def _map_severity(issue: dict) -> Severity:
        """
        Infers severity from the issue text or returns MEDIUM by default.
        PR-Agent doesn't always strictly define severity in key_issues_to_review,
        but it might add header like 'issue_header: Possible Bug'.
        """
        header = (issue.get("issue_header", "")).lower()
        if "security" in header or "vulnerability" in header:
            return Severity.CRITICAL
        if "bug" in header or "error" in header or "crash" in header:
            return Severity.HIGH
        if "performance" in header:
            return Severity.MEDIUM
        if "style" in header or "typo" in header or "doc" in header:
            return Severity.LOW
        
        return Severity.MEDIUM

    @staticmethod
    def _map_category(issue: dict) -> str:
        """
        Infers category from the issue text.
        """
        header = (issue.get("issue_header", "")).lower()
        if "security" in header or "vulnerability" in header:
            return "SECURITY"
        if "bug" in header or "error" in header or "crash" in header:
            return "BUG"
        if "performance" in header:
            return "PERFORMANCE"
        if "style" in header or "typo" in header or "doc" in header:
            return "STYLE"
        
        return "OTHER"

    @classmethod
    def normalize_findings(cls, raw_data: Dict[str, Any]) -> List[FindingCreate]:
        """
        Parses the PR-Agent structured review output and maps it to FindingCreate schemas.
        """
        findings = []
        review_data = raw_data.get("review", {})
        
        key_issues = review_data.get("key_issues_to_review", [])
        if not isinstance(key_issues, list):
            return []

        for issue in key_issues:
            if not isinstance(issue, dict):
                continue
                
            # PR-Agent keys
            relevant_file = issue.get("relevant_file", "")
            if relevant_file:
                relevant_file = relevant_file.strip()
            
            # Lines
            try:
                start_line = int(str(issue.get("start_line", 0)).strip())
            except ValueError:
                start_line = None
                
            try:
                end_line = int(str(issue.get("end_line", 0)).strip())
            except ValueError:
                end_line = None

            if start_line == 0: start_line = None
            if end_line == 0: end_line = None

            # Fallback to relevant_line parsing if start_line/end_line not present
            if start_line is None:
                relevant_line = str(issue.get("relevant_line", "")).strip()
                if relevant_line.isdigit():
                    start_line = int(relevant_line)
                    end_line = int(relevant_line)

            # Titles and Descriptions
            title = issue.get("issue_header", "AI Finding").strip()
            
            # Combine content and suggestion for description/recommendation
            description = issue.get("issue_content", "") or issue.get("suggestion", "")
            
            # If suggestion is separate, use it
            recommendation = None
            if "suggestion" in issue and "issue_content" in issue:
                recommendation = issue["suggestion"]
                
            if not description:
                description = "No description provided."

            finding = FindingCreate(
                source=Source.AI,
                category=cls._map_category(issue),
                severity=cls._map_severity(issue),
                file_path=relevant_file if relevant_file else None,
                start_line=start_line,
                end_line=end_line,
                title=title,
                description=description.strip(),
                recommendation=recommendation.strip() if recommendation else None,
                confidence=None, # We do not fake confidence
                raw_data=issue
            )
            findings.append(finding)

        # Map security concerns if present
        security_concerns = review_data.get("security_concerns", "")
        if security_concerns and isinstance(security_concerns, str) and security_concerns.strip() and security_concerns.lower() not in ["no", "none", "false"]:
            findings.append(FindingCreate(
                source=Source.AI,
                category="SECURITY",
                severity=Severity.HIGH,
                title="Security Concern",
                description=security_concerns.strip(),
                raw_data={"security_concerns": security_concerns}
            ))

        return findings

    @classmethod
    def extract_usage(cls, raw_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Extract token usage from the raw output.
        """
        usage = raw_data.get("usage", {})
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }
