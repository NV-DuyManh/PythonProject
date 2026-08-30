from typing import Optional, Protocol
from codegate.engines.policy.schemas import PolicyEvaluationResult, PolicyDecision
from pr_agent.git_providers.github_provider import GithubProvider
from pr_agent.log import get_logger

class PolicyCheckPublisher(Protocol):
    def publish(self, result: PolicyEvaluationResult, summary: str, text: str) -> Optional[int]:
        ...

class GitHubPolicyCheckPublisher:
    def __init__(self, provider):
        self.provider = provider
        
    def publish(self, result: PolicyEvaluationResult, summary: str, text: str) -> Optional[int]:
        if not isinstance(self.provider, GithubProvider):
            get_logger().info("Not a GitHub provider, skipping GitHub check publish.")
            return None
            
        if not getattr(self.provider, 'last_commit_id', None):
            get_logger().error("Cannot publish check run without a commit SHA")
            return None
            
        conclusion = "success"
        if result.decision == PolicyDecision.WARNING:
            conclusion = "neutral"
        elif result.decision == PolicyDecision.BLOCK:
            conclusion = "failure"
            
        check_run_name = "CodeGate / PR Quality"
        
        create_body = {
            "name": check_run_name,
            "head_sha": self.provider.last_commit_id.sha,
            "status": "completed",
            "conclusion": conclusion,
            "output": {
                "title": check_run_name,
                "summary": summary[:65535],
                "text": text[:65535],
            },
        }
        
        existing_id = self.provider._find_existing_check_run(check_run_name, self.provider.last_commit_id.sha)
        
        try:
            if existing_id:
                update_body = {
                    "status": "completed",
                    "conclusion": conclusion,
                    "output": {
                        "title": check_run_name,
                        "summary": summary[:65535],
                        "text": text[:65535],
                    },
                }
                res, data = self.provider.github_client._Github__requester.requestJsonAndCheck(
                    "PATCH",
                    f"{self.provider.repo_obj.url}/check-runs/{existing_id}",
                    input=update_body,
                    headers={"Accept": "application/vnd.github.v3+json"},
                )
                return existing_id
            else:
                res, data = self.provider.github_client._Github__requester.requestJsonAndCheck(
                    "POST",
                    f"{self.provider.repo_obj.url}/check-runs",
                    input=create_body,
                    headers={"Accept": "application/vnd.github.v3+json"},
                )
                return data.get("id")
        except Exception as e:
            get_logger().error(f"Failed to publish GitHub check run: {e}")
            raise e
