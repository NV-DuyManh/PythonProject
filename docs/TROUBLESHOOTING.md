# Troubleshooting Guide

This guide covers common issues you might encounter when running or developing CodeGate locally.

> [!NOTE]
> Do not expose or paste real secrets (like your `.pem` file content or `.env` keys) when running diagnostics or asking for support.

## Common Issues

### 1. Docker Desktop Not Running
- **Symptom:** Running the Launcher or `docker compose` fails immediately with an error about the Docker daemon.
- **Cause:** Docker Desktop is not started or installed.
- **How to Check:** Run `docker info` in your terminal.
- **Fix:** Open Docker Desktop from your start menu and wait for the engine to initialize.

### 2. Port 5173 or 8000 Occupied
- **Symptom:** Frontend or Backend container fails to start, showing an "address already in use" error in the logs.
- **Cause:** Another application (or an old, orphaned CodeGate process) is using port 5173 (React) or 8000 (FastAPI).
- **How to Check:** 
  - Windows: `netstat -ano | findstr :5173`
  - Linux/Mac: `lsof -i :5173`
- **Fix:** Identify the PID of the conflicting process and terminate it, or change the exposed port in `compose.codegate.yml`.

### 3. Postgres / Redis Unhealthy
- **Symptom:** The `backend` or `worker` containers constantly restart, and the Launcher shows ERROR for Postgres or Redis.
- **Cause:** The database container crashed, or Docker is out of disk space.
- **How to Check:** Run `docker logs codegate-postgres-1`.
- **Fix:** Ensure Docker has enough allocated resources (Memory/Disk). If the database is corrupted (and you don't mind losing data), you can clear the volume with `docker compose down -v`.

### 4. Migration Failed
- **Symptom:** The `migrate` service exits with a non-zero code. Backend won't start.
- **Cause:** Database schema is out of sync or an Alembic migration script has a syntax error.
- **How to Check:** Run `docker logs codegate-migrate-1`.
- **Fix:** If developing, run `alembic heads` to ensure there are no branching conflicts. 

### 5. GitHub OAuth Callback Error
- **Symptom:** Logging in redirects you back to a blank page or a 500 error.
- **Cause:** `GITHUB_OAUTH_CLIENT_ID` or `GITHUB_OAUTH_CLIENT_SECRET` is missing/incorrect, or the Callback URL in GitHub doesn't match `http://127.0.0.1:8000/api/v1/auth/github/callback`.
- **How to Check:** Verify your `.env` file against your GitHub OAuth App settings.
- **Fix:** Correct the credentials in `.env` and restart the backend.

### 6. GitHub App Connection Error / Webhook Not Received
- **Symptom:** You open a PR, but no CodeGate analysis starts.
- **Cause:** 
  1. The Webhook URL in GitHub App settings is wrong or inaccessible.
  2. The GitHub App is not installed on the specific repository.
  3. `GITHUB_WEBHOOK_SECRET` doesn't match.
- **How to Check:** Go to your GitHub App settings -> **Advanced**. Look at the "Recent Deliveries" section. It will show if webhooks are failing (red X).
- **Fix:** If running locally, you **must** use a tunneling service (like smee.io or ngrok) to expose port 8000 to the public internet, and set that URL in GitHub. `127.0.0.1` will not work for GitHub's outbound webhooks.

### 7. AI Provider Key Missing/Invalid
- **Symptom:** Worker picks up the job but immediately fails. Logs show "Authentication Error" from LiteLLM.
- **Cause:** `GROQ_API_KEY` or `OPENAI_API_KEY` is missing, expired, or out of credits.
- **How to Check:** View the Celery worker logs in the Launcher.
- **Fix:** Verify your API key at the provider's console and update your `.env` file. Restart the worker.

### 8. Frontend Stale After Source Change
- **Symptom:** You edited React code, but the browser doesn't reflect the changes.
- **Cause:** In Product Mode (Docker), the frontend is built into a static Nginx image. It does not hot-reload.
- **How to Check:** N/A.
- **Fix:** In Product Mode, use **Force Rebuild** in the Launcher. If developing actively, use Developer Mode (`npm run dev` outside of Docker).

### 9. Test Executor Error (Coverage N/A)
- **Symptom:** The PR analysis completes, but Testing Score is 0 and Coverage is N/A. Worker logs show "Docker socket unavailable".
- **Cause:** The worker container cannot mount `/var/run/docker.sock` from the host.
- **How to Check:** Ensure `compose.codegate.yml` has the docker socket volume mount for the `worker` service.
- **Fix:** If using Docker Desktop on Windows/Mac, ensure you have granted permission for containers to access the Docker socket.

### 10. Repository ACCESS_REMOVED
- **Symptom:** A repository in your dashboard shows as unavailable.
- **Cause:** Someone uninstalled the GitHub App from that repository on GitHub.
- **How to Check:** Check your GitHub App installation settings on GitHub.com.
- **Fix:** Reinstall the app on the repository via GitHub, then click "Sync Repositories" in the CodeGate dashboard.
