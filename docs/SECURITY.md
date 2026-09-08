# Security Policy

CodeGate is designed to analyze potentially untrusted source code. Security is handled at multiple layers of the application.

## 1. Secrets Management
- **No Hardcoded Secrets**: CodeGate requires external configuration for all secrets (`.env` or Docker secrets).
- **GitHub Private Key**: The `.pem` file is never stored in the database. It is mounted directly into the container filesystem at runtime (`/run/secrets/github-app-key.pem`) as read-only.
- **Database Passwords**: Managed strictly via environment variables.

## 2. API & Authentication Security
- **OAuth State**: A unique, short-lived `state` parameter is generated and cached in Redis during the GitHub OAuth flow to prevent Cross-Site Request Forgery (CSRF).
- **Session Hashing**: Sessions use cryptographically secure, opaque hashes. The frontend receives an `HttpOnly`, `SameSite=Lax` cookie, shielding the session from XSS attacks.
- **Webhook Signatures**: Every incoming webhook from GitHub is verified using `HMAC-SHA256` against the `GITHUB_WEBHOOK_SECRET`. Invalid or forged webhooks are immediately rejected.
- **Tenant Isolation**: Every backend API endpoint strictly verifies that the requested resource belongs to the user's `active_workspace_id`.

## 3. GitHub Integrations
- **Installation Tokens**: CodeGate does not use static Personal Access Tokens. It dynamically generates short-lived Installation Tokens using the GitHub App Private Key. These tokens are scoped precisely to the repository being analyzed and expire after 1 hour.

## 4. Test Execution Sandbox Boundary
CodeGate executes user-provided test suites to gather coverage data. This is an inherently risky operation if the repository contains malicious code.

- **DockerTestExecutor**: The Celery worker spawns a sibling container to run tests.
- **Trust Boundary**:
  - The worker has the Docker socket mounted (`/var/run/docker.sock`). **This means the worker is highly privileged.**
  - The *test container* spawned by the worker **DOES NOT** have the Docker socket mounted.
  - The test container runs unprivileged.
  - The network for the test container is disconnected by default (`network=none`), preventing data exfiltration during the test run, unless explicitly configured otherwise by the user.

> [!CAUTION]
> Because the Celery worker has access to the Docker socket, a compromise of the worker container could lead to host compromise. Ensure that CodeGate is deployed in a secure environment and that you trust the repositories you configure it to analyze. CodeGate's test sandbox provides basic isolation, but is not a hardened, multi-tenant secure enclave (like Firecracker microVMs). It is designed for Local Product Mode where the user owns the machine and the repositories.
