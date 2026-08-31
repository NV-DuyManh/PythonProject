# CodeGate API

## System
- `GET /api/v1/system/status` - Health check.

## Repositories
- `GET /api/v1/repositories` - List repos.
- `POST /api/v1/repositories` - Create repo.

## Pull Requests
- `GET /api/v1/pull_requests` - List PRs.

## Analyses
- `GET /api/v1/analyses/{id}` - Get analysis state.

## Findings
- `GET /api/v1/findings` - List static analysis issues.

## Testing/Coverage
- `GET /api/v1/testing` - Get test results.

## Reviewer Recommendation
- `GET /api/v1/reviewers` - Get suggestions.

## Dashboard / Analytics
- `GET /api/v1/dashboard/overview` - KPIs.

## GitHub Integrations
- `POST /api/v1/github_connections` - Register App.

## Webhook
- `POST /api/v1/github_webhooks` - Process events.
