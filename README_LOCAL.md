# CodeGate Local Product Mode

CodeGate is designed to be a high-quality local product. You can run CodeGate locally using the included one-click launcher.

## Prerequisites
1. **Docker Desktop**: You must have Docker Desktop installed and running.
2. **Ports**: Ensure ports `5173` (Frontend) and `8000` (Backend) are available on your machine.

## How to Start
1. Configure your environment (optional but recommended for full features). Copy `.env.example` to `.env` and fill in your keys.
2. Double-click `CodeGateLauncher.exe`.
3. In the launcher, click **Start CodeGate**.
4. The launcher will automatically validate your system, start the database, run migrations, and launch the backend, worker, and frontend.
5. Once all services show a green **READY** status, click **Open Dashboard** to view your CodeGate instance at `http://127.0.0.1:5173`.

## Troubleshooting & Diagnostics
- **View Logs**: You can view the live logs of any component (Backend, Worker, Frontend, Database, etc.) directly in the launcher by clicking **View Logs**.
- **Diagnostics**: If you encounter issues, click **Diagnostics** to generate a safe, secret-redacted report of your system state. This report can be exported and shared for support.
- **Stop/Restart**: You can safely stop and restart CodeGate at any time. Your data (Postgres database and repositories) is preserved in a local Docker volume.
