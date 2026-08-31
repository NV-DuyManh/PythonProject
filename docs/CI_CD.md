# CodeGate CI/CD Pipeline

CodeGate relies on GitHub Actions to ensure code correctness, structural integrity, and security on every push and pull request.

## Architecture

The workflow is defined in `.github/workflows/codegate-ci.yml`.

### Triggers
The CI pipeline runs on:
- **`pull_request`** (Targeting `main`)
- **`push`** (To `main`)
- **`workflow_dispatch`** (Manual execution)

### Concurrency
Outdated PR runs are automatically canceled (`cancel-in-progress: true`) to save CI minutes and avoid race conditions. Unrelated branch runs will not be canceled.

### Workflow Permissions
The `codegate-ci.yml` strictly uses `contents: read` permissions. It avoids executing untrusted checkout code with secrets to protect against malicious forks.

## Jobs
The CI matrix consists of logically grouped validations:

1. **Backend Checks (`backend-tests`)**
   - Python 3.12 environment setup
   - Dependency installation (from `requirements.txt` and `requirements-dev.txt`)
   - `ruff check` on `codegate/` and `tools/`
   - `pytest tests/codegate -q` to validate all core application logic (89/89 tests must pass).

2. **Frontend Checks (`frontend-tests`)**
   - Node 20 (LTS) environment setup
   - Package installation using `npm ci`
   - `npm run lint` (`oxlint`)
   - `npm run test:run` (Vitest)
   - `npm run build` (Ensuring TS types and Vite bundling succeed)

3. **PostgreSQL Validation (`postgres-ci`)**
   - Runs against a temporary disposable `postgres:16-alpine` service container.
   - Applies Alembic migrations (`alembic upgrade head`).
   - Verifies there are no multiple hanging heads (`alembic heads | wc -l`).
   - Executes `test_postgres_crud.py` to confirm actual ORM-level insert/read/update safety.

4. **Docker Build Checks (`docker-ci`)**
   - Validates `docker compose config`.
   - Validates the build contexts for `backend` and `frontend` images.
   - Strictly does not require or utilize real secrets (`GROQ_API_KEY`, GitHub Keys).

5. **Security Scanning (`security-audit`)**
   - **Gitleaks**: Static analysis to ensure no keys or tokens were accidentally pushed into Git history.
   - **Pip-Audit**: Checks Python packages against vulnerability databases.
   - **Bandit**: Static application security testing (SAST) for Python code.
   - **NPM Audit**: Checks Javascript dependencies against vulnerability databases.

6. **Upstream PR-Agent Regression (`upstream-regression`)**
   - Runs the legacy suite, acknowledging the existing documented upstream baseline failures without necessarily blocking CodeGate integrations.

## Local Equivalents
Developers can replicate the CI locally to validate code before pushing:

**Backend Tests:**
```bash
python -m pytest tests/codegate -q
ruff check codegate tools
bandit -r codegate tools
```

**Frontend Tests:**
```bash
cd dashboard
npm run lint
npm run test:run
npm run build
```

**Database Validation:**
*(With Compose Up)*
```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python tools/test_postgres_crud.py
```
