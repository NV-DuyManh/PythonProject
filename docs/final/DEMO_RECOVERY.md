# CodeGate: Demo Recovery Guide

*Presentations fail. APIs go down. Ports collide. This guide provides immediate recovery paths so the defense presentation never stops.*

## 1. Scenario: Frontend Dashboard Does Not Open
**Symptom**: Navigating to `http://127.0.0.1:5173` shows "This site can't be reached".
**Recovery**:
1. Check terminal running the frontend / docker compose.
2. If using Docker: `docker compose -f compose.codegate.yml logs frontend`.
3. If running locally: The port may be occupied. Ensure no other Vite server is running. Do NOT blindly switch to port `5174` (it will break backend CORS). Kill the offending process:
   - Windows: `Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess | Stop-Process -Force`
4. **Fallback Path**: Show the backend JSON responses via `http://127.0.0.1:8000/api/v1/dashboard/prs` to prove the data layer works.

## 2. Scenario: Backend API Offline
**Symptom**: Dashboard shows API offline error; `http://127.0.0.1:8000/api/v1/system/status` does not resolve.
**Recovery**:
1. Check backend logs for fatal boot errors (e.g., PostgreSQL connection refused).
2. If using Docker: `docker compose -f compose.codegate.yml restart backend`.
3. **Fallback Path**: Open the API Source code (`main.py`, `routers/`) and explain the architecture instead of showing the live UI. Use screenshots from `docs/images/final/`.

## 3. Scenario: Groq / LiteLLM API Unavailable
**Symptom**: AI Review features timeout; Error 503 from LLM provider.
**Recovery**:
1. Do NOT attempt to debug the API key live.
2. Explain that the AI provider is down, which perfectly demonstrates CodeGate's resilience: the deterministic Policy Engine still calculates the risk and quality scores based on static analysis.
3. **Fallback Path**: Navigate to the persisted DEMO PRs in the dashboard. These records were created *before* the outage and contain cached AI responses, proving the integration works when the third-party is online.

## 4. Scenario: GitHub Webhook Fails (Live Demo Path)
**Symptom**: Opening a PR on GitHub does not trigger a CodeGate analysis or Check Run.
**Recovery**:
1. The Smee.io relay might be disconnected, or the GitHub App permissions might have expired.
2. **Fallback Path**: Abandon the live GitHub PR creation. Pivot immediately to the CodeGate Dashboard and say: *"While the webhook relay is experiencing latency, let's look at a Pull Request that was successfully ingested previously..."* and use the persisted DEMO cases.

## 5. Scenario: Docker / PostgreSQL Fails to Boot
**Symptom**: `docker compose up` hangs, or Postgres volume is corrupted.
**Recovery**:
1. **Fallback Path**: Immediately switch to the `CodeGateLauncher.exe` (or `launcher.py`). This uses the local SQLite fallback and runs the API/Dashboard on the host machine without Docker. This ensures the presentation continues seamlessly.

---

**Golden Rule**: Never stop talking. If a live integration fails, explain *why* it failed (e.g., "This highlights our dependence on third-party AI uptime...") and immediately pivot to the persisted Dashboard or Screenshots.
