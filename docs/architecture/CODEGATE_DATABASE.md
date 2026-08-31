# CodeGate Database Documentation

## ER Diagram
```mermaid
erDiagram
    User ||--o{ TeamMember : "has"
    Team ||--o{ TeamMember : "contains"
    
    GitHubConnection ||--o{ Repository : "owns"
    Repository ||--o{ PullRequest : "contains"
    
    PullRequest ||--o{ PullRequestFile : "has"
    PullRequest ||--o{ AnalysisRun : "triggers"
    PullRequest ||--o{ WebhookEvent : "generates"
    
    AnalysisRun ||--o{ AnalyzerRun : "executes"
    AnalysisRun ||--o{ Finding : "produces"
    AnalysisRun ||--o{ CodeMetric : "measures"
    AnalysisRun ||--|| QualityScore : "computes"
    AnalysisRun ||--|| RiskScore : "evaluates"
    AnalysisRun ||--|| PolicyEvaluation : "checks"
    AnalysisRun ||--|| ReviewerRecommendation : "generates"
    
    TestConfiguration ||--o{ TestRun : "defines"
    AnalysisRun ||--o{ TestRun : "includes"
    TestRun ||--o{ CoverageReport : "generates"
    
    QualityPolicy ||--o{ PolicyEvaluation : "enforces"
```

## ORM Entities
- **User / Team / TeamMember**: Role and access management.
- **GitHubConnection / Repository**: Integration states.
- **PullRequest / PullRequestFile**: PR metadata and file changes.
- **WebhookEvent**: Payload persistence and deduplication.
- **AnalysisRun**: The core execution container for a PR update.
- **Finding / AnalyzerRun / CodeMetric**: Static analysis results.
- **QualityScore / RiskScore**: Deterministic grade outputs.
- **QualityPolicy / PolicyEvaluation**: Rules and their evaluation.
- **TestConfiguration / TestRun / CoverageReport**: Testing evidence.
- **ReviewerRecommendationConfig / ReviewerRecommendation / ReviewerRecommendationCandidate**: Reviewer matching.
