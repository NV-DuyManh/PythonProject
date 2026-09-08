# CodeGate Handover Checklist

This checklist is for new developers cloning CodeGate for the first time. Follow these steps to verify your local environment is correctly configured.

## 1. Environment Verification
- [ ] Docker Desktop (or Engine) is installed and running.
- [ ] Node.js (v20+) and Python (3.12+) are installed (only required for Developer Mode).
- [ ] Repository is cloned to your local machine.

## 2. Configuration Setup
- [ ] Copied `.env.example` to `.env`.
- [ ] Filled in `GROQ_API_KEY` (or alternative AI provider key) in `.env`.
- [ ] Configured GitHub OAuth App and filled in Client ID/Secret in `.env`.
- [ ] Created a GitHub App and filled in App ID, Slug, and Webhook Secret in `.env`.
- [ ] Downloaded the GitHub App private key and placed it at `secrets/github-app-key.pem`.

## 3. Platform Startup
- [ ] Started CodeGate (via `CodeGateLauncher.exe` OR `docker compose -f compose.codegate.yml up -d --build`).
- [ ] Verified the Launcher shows all services in the **READY** state (or verified via `docker ps`).
- [ ] Opened `http://127.0.0.1:5173` in a web browser and saw the login page.

## 4. End-to-End Validation
- [ ] Successfully logged in via GitHub OAuth.
- [ ] Created a new Workspace in the dashboard.
- [ ] Clicked "Install GitHub App" and authorized the app on your GitHub account/organization.
- [ ] Synchronized repositories and selected at least one repository.
- [ ] Navigated to the repository settings and enabled "Testing Configuration" (using `DockerTestExecutor` or `DisabledExecutor`).
- [ ] Opened a dummy Pull Request in your connected GitHub repository.
- [ ] Verified the webhook was received by the Backend (check Backend logs).
- [ ] Verified the Celery Worker picked up the Analysis Job (check Worker logs).
- [ ] Verified the final CodeGate Check was published back to the GitHub Pull Request.
- [ ] Verified the Pull Request details, Quality Score, and Risk Score appeared on the CodeGate Dashboard.

If you have checked all the boxes above, your CodeGate development environment is fully operational!
