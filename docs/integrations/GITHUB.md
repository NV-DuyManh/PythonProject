# GitHub Integration

## GitHub App
Integrates securely via a GitHub App utilizing `GitHubConnection`.

## Capabilities
- Repository scoping restricts access.
- Webhook verification ensures payloads are signed by GitHub.
- Bi-directional PR sync and GitHub Checks integration.
- Multi-account design isolated by `installation_id`.
- Demo vs Live data isolation ensures demo data never leaks to live GitHub connections.

*Note: No actual tokens or private keys are stored in this repository.*
