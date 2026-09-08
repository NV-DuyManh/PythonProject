# CodeGate Local Launcher Guide

CodeGate is designed to be a high-quality local product. You can run CodeGate locally using the included one-click launcher executable, `CodeGateLauncher.exe`.

## Launcher Functions

The CodeGate Launcher provides a simple, graphical interface to manage the lifecycle of your local CodeGate instance:

- **Preflight**: Validates your system dependencies (like Docker Desktop) before attempting to start services.
- **Start**: Initiates `docker compose up -d` to launch the PostgreSQL database, Redis, backend, worker, and frontend.
- **Stop**: Safely stops all containers using `docker compose stop`, preserving your database volume.
- **Restart**: Stops and then immediately starts all CodeGate services.
- **Force Rebuild**: Rebuilds the Docker images from scratch (`docker compose build --no-cache`). Use this if you have modified source code or environment variables.
- **Logs**: Opens a view to see real-time output from any specific service container.
- **Diagnostics**: Generates a safe, secret-redacted report of your system state. This report can be exported and shared for support or debugging.
- **Open Dashboard**: Automatically opens your default web browser to the CodeGate frontend (http://127.0.0.1:5173).

## Launcher States

The launcher UI will reflect the overall health of the CodeGate platform in three primary states:

- **READY**: All required services are healthy and responding.
- **DEGRADED**: One or more non-critical services are struggling, but the platform is partially available.
- **ERROR**: A critical service (like PostgreSQL or the Backend API) has failed to start or crashed.

## Service Health Monitoring

The launcher actively monitors the health of the following six distinct services:

1. **Postgres**: The PostgreSQL 16 database.
2. **Redis**: The Redis broker used for Celery task queuing.
3. **Migration**: The Alembic database migration service (runs once on startup).
4. **Backend**: The FastAPI API server (Port 8000).
5. **Worker**: The Celery asynchronous task processor.
6. **Frontend**: The React/Vite dashboard (Port 5173).

## Data Preservation

You can safely Stop and Restart CodeGate at any time. 
**Data (PostgreSQL database and repositories) is preserved in a local Docker named volume.**

> [!WARNING]
> Do not run `docker compose down -v` unless you explicitly want to permanently delete all your CodeGate data, users, and analysis history.
