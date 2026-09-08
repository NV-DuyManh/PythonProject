# Database Documentation

CodeGate uses **PostgreSQL 16** as its primary data store. Unlike the upstream PR-Agent (which is stateless), CodeGate requires persistent storage to track Pull Requests, historical analysis runs, user authentication, and tenant isolation (Workspaces).

## Database Architecture

- **Engine:** SQLAlchemy 2.0 (Async and Sync where appropriate).
- **Driver:** `psycopg2` (sync worker/api) or `asyncpg` (where strictly required, though mostly synchronous for simplicity in Celery).
- **Migrations:** Alembic.

## Schema Overview

Key entities in the database include:
- `User`, `Workspace`, `TeamMember` (RBAC & Tenancy)
- `GitHubConnection`, `Repository` (GitHub Integration)
- `PullRequest`, `AnalysisRun`, `AnalysisJob` (Execution tracking)
- `AnalysisFinding` (Individual flaws, bugs, and scores)

## Migrations (Alembic)

CodeGate uses Alembic to manage database schema versions. 

In Product Mode, migrations are run automatically on startup via the `migrate` docker-compose service, which executes:
```bash
alembic upgrade head
```

### Developer Commands

If you are developing CodeGate and changing SQLAlchemy models, you must generate a new migration:

1. Auto-generate the migration script:
   ```bash
   alembic revision --autogenerate -m "Add new feature column"
   ```
2. Apply the migration locally:
   ```bash
   alembic upgrade head
   ```

To check the current state:
```bash
alembic current
alembic heads
alembic history
```

> [!WARNING]
> Do not manually edit the PostgreSQL schema. Always use Alembic migrations to ensure the product can be safely updated by end-users.

## Data Persistence & Safety

When running via Docker Compose, PostgreSQL stores its data in a named Docker volume: `codegate_postgres_data`.

- `docker compose stop` or `docker compose down` will **preserve** this data.
- `docker compose down -v` will **DESTROY** this data permanently. 

*Note: Currently, CodeGate does not have a built-in automated backup/restore feature for the PostgreSQL volume.*
