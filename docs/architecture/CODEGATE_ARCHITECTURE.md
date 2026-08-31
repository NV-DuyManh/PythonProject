# CodeGate Architecture

## Conceptual Flow
```text
GitHub
  ↓
GitHub App
  ↓
Webhook
  ↓
CodeGate API
  ↓
Pull Request Persistence
  ↓
Analysis Orchestrator
  ├── PR-Agent AI Review
  ├── Ruff
  ├── Bandit
  ├── Radon
  ├── Tests
  └── Coverage
  ↓
Quality Score
  ↓
Risk Score
  ↓
Policy Evaluation
  ↓
Reviewer Recommendation
  ↓
GitHub Check
  ↓
Dashboard / Analytics
```

## Architectural Boundaries

- `pr_agent/`: The upstream/foundation AI review engine.
- `codegate/`: CodeGate platform services, persistence, scoring, orchestration, management, analytics and integration layer.
- `dashboard/`: CodeGate React frontend.
- `tools/codegate_launcher/`: Local Windows runtime launcher.
