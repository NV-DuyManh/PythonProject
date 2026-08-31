# CodeGate Analysis Pipeline

The pipeline orchestrates the complete PR evaluation lifecycle:

1. **GitHub PR / Webhook:**
   - Input: Webhook payload.
   - Component: `codegate.api.webhooks`
   - Output: `WebhookEvent`

2. **Sync:**
   - Input: WebhookEvent.
   - Component: `PullRequestService`
   - Output: `PullRequest`, `PullRequestFile`

3. **AnalysisRun:**
   - Input: PR state.
   - Component: `AnalysisOrchestrator`
   - Output: `AnalysisRun` (Status: RUNNING)

4. **AI / Static Analysis / Tests / Coverage:**
   - Component: `AnalyzerRunner`, `TestingService`, `pr_agent`
   - Output: `Finding`, `AnalyzerRun`, `CodeMetric`, `TestRun`, `CoverageReport`

5. **Quality & Risk:**
   - Component: `QualityEngine`, `RiskEngine`
   - Output: `QualityScore`, `RiskScore`

6. **Policy & Reviewer:**
   - Component: `PolicyEngine`, `ReviewerEngine`
   - Output: `PolicyEvaluation`, `ReviewerRecommendation`

7. **GitHub Check & Dashboard:**
   - Final status synchronized back to GitHub Checks.
   - Visible on React dashboard.
