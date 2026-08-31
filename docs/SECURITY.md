# CodeGate Security Policy

## 1. Secret Management
- **Never Commit Secrets:** Do not commit API keys, GitHub private keys (`.pem`), database passwords, or webhook secrets to the repository.
- **Local Configuration:** Use `.secrets.toml` or `.env` files for local development. Both of these formats are explicitly gitignored.
- **Docker Secrets:** When building Docker images, do not bake real secrets into the image layers. Use environment variables at runtime or mounted secrets.
- **CI Secrets:** Do not expose repository secrets to untrusted Pull Requests (especially from forks). Use `pull_request` (safe) instead of `pull_request_target`.

## 2. CI/CD Scanners
The CodeGate CI pipeline implements automatic security enforcement:
- **Gitleaks:** Scans all commits for accidentally exposed secrets.
- **Pip-Audit & NPM Audit:** Evaluates project dependencies for known CVEs. High and Critical issues must be reviewed or patched.
- **Bandit:** Performs static security analysis on Python logic to catch common vulnerabilities (e.g. unsafe exec, hardcoded passwords).

## 3. Webhook & API Security
- **GitHub Webhooks:** Payloads received by the `/api/v1/github/webhook` endpoint MUST pass SHA-256 signature validation using the configured `GITHUB_WEBHOOK_SECRET`.
- **API CORS:** Development environments use local origins. Production environments should explicitly allowlist trusted domains.
- **Logging Safety:** The application globally suppresses raw database URLs and tokens from stack traces. Never dump `os.environ` or the raw `Authorization` header to logs.

## 4. Incident Response & Credential Exposure
In the event that a credential (such as a Groq API Key or GitHub token) is accidentally exposed:
1. **Immediate Revocation:** The developer must immediately revoke or roll the exposed key via the vendor's dashboard.
2. **Do Not Reproduce:** Do not place the exposed credential in documentation, tests, or bug reports.
3. **Audit Commit History:** Ensure the secret scanner catches similar keys going forward.

*(Note: A Groq credential was historically exposed during early development. That key has been documented as compromised and must remain revoked).*

## 5. Vulnerability Reporting
If you discover a security issue, please avoid public disclosure until the maintainers have had an opportunity to address it.
