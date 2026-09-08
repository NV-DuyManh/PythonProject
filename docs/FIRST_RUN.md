# First Time Setup (Clone & Run Guide)

This guide walks you through the exact steps required to get CodeGate running on your local machine, from downloading the source code to running your first Pull Request analysis.

CodeGate supports two execution modes: **Normal Local Product Mode** (for end-users using Docker Desktop) and **Developer Mode** (for contributors working on the source code directly).

---

## Part A: Normal Local Product Mode

This is the recommended path for users who want to run the CodeGate platform locally without modifying the source code.

### Step 1: Install Prerequisites
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for Windows/Mac or Docker Engine for Linux.
- Ensure Docker is running.
- Ensure ports `5173` (Frontend) and `8000` (Backend) are free. (Port `5174` is NOT used).

### Step 2: Clone the Repository
```bash
git clone https://github.com/NV-DuyManh/PythonProject.git
cd PythonProject
```

### Step 3: Configure Environment Variables
1. Copy the example configuration file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in the required `GROQ_API_KEY` (or `OPENAI_API_KEY`).
   > *See [AI Configuration](AI_CONFIGURATION.md) and [Configuration Guide](CONFIGURATION.md) for more details.*

### Step 4: Configure GitHub App & OAuth (Required for PR Analysis)
To analyze PRs, CodeGate requires a GitHub App installation.
1. Follow the [GitHub App Setup Guide](GITHUB_APP_SETUP.md) to create your app.
2. Follow the [Authentication Guide](AUTHENTICATION.md) to configure GitHub OAuth for user login.
3. Place your downloaded GitHub App private key (`.pem` file) into the `secrets/` directory as `secrets/github-app-key.pem`.

### Step 5: Start CodeGate

**Option 1: Using the Windows Launcher**
1. Double-click `CodeGateLauncher.exe` in the project root.
2. Click **Start CodeGate**.
3. Wait for all services to show the **READY** state.
4. Click **Open Dashboard** (or navigate to `http://127.0.0.1:5173`).

**Option 2: Using Docker CLI**
1. Run the following command:
   ```bash
   docker compose -f compose.codegate.yml up -d --build
   ```
2. Wait a few moments for the database migrations to run and the backend to become healthy.
3. Open `http://127.0.0.1:5173` in your browser.

### Step 6: Post-Installation Workflow
1. **Login:** Authenticate via GitHub OAuth on the frontend.
2. **Create Workspace:** Create your first team workspace.
3. **Connect GitHub:** Install your GitHub App into the workspace.
4. **Sync Repositories:** CodeGate will automatically fetch your available repositories.
5. **Configure Repository Tests:** Select a repository and configure its testing executor (e.g., DockerTestExecutor).
6. **Open First PR:** Open a Pull Request on GitHub in your connected repository.
7. **Verify Automatic Analysis:** Watch the CodeGate dashboard or the GitHub PR comments to see the AI review, static analysis, and test results appear automatically.

---

## Part B: Developer Mode

This path is for developers who want to modify CodeGate's Python backend or React frontend.

### Step 1: Install Developer Prerequisites
- Python 3.12 or higher
- Node.js 20 or higher
- Docker Engine / Docker Desktop (for Postgres and Redis)

### Step 2: Infrastructure Setup
Start the required databases (PostgreSQL and Redis) using Docker:
```bash
# Only start postgres and redis
docker compose -f compose.codegate.yml up -d postgres redis
```

### Step 3: Backend Setup (Python)
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
3. Run Alembic migrations:
   ```bash
   alembic upgrade head
   ```
4. Start the FastAPI backend:
   ```bash
   uvicorn codegate.api.main:app --reload --port 8000
   ```
5. In a separate terminal (with the virtual environment activated), start the Celery worker:
   ```bash
   celery -A codegate.worker.celery_app worker -l info --concurrency=2
   ```

### Step 4: Frontend Setup (React/Vite)
1. Navigate to the frontend directory:
   ```bash
   cd dashboard
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Access the development dashboard at `http://localhost:5173`.
