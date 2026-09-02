# CodeGate v1.0.0
**AI-Powered Pull Request Quality Intelligence Platform**

*Welcome to CodeGate. If you are reviewing this project for a defense or presentation, please start here: [**Final Defense & Documentation Index**](docs/final/README.md).*

CodeGate is a comprehensive Pull Request Quality Intelligence Platform that analyzes Pull Requests using AI-assisted review, static analysis, test evidence, and changed-code coverage. It provides explainable Quality and Risk Scores, Merge Policy evaluation, reviewer recommendations, and an engineering analytics dashboard.

## 🚀 Quick Start (Two Paths)

**WARNING:** Both methods use ports `8000` (Backend) and `5173` (Frontend). Do not run both methods simultaneously.

### Path A: Windows Local (Docker/PostgreSQL)
1. Double-click `CodeGateLauncher.exe` in the project root.
2. Click **START CODEGATE** (This runs `docker compose up -d --build`).
3. Browser automatically opens: http://127.0.0.1:5173

### Path B: Docker Production (PostgreSQL)
*Requires Docker Desktop installed.*
```bash
# Boot the backend, frontend, and postgres cluster
docker compose -f compose.codegate.yml up -d --build
```
Access the dashboard at http://127.0.0.1:5173.

## 🏗️ Architecture & Features

CodeGate solves the problem of subjective, inconsistent pull request reviews by unifying probabilistic AI insights with deterministic static analysis (Ruff, Bandit) and testing metrics.

- **Quality & Risk Scoring:** Deterministic algorithms.
- **Merge Policy Engine:** Blocks, warns, or passes based on strict evidence.
- **Reviewer Recommendations:** Based on CODEOWNERS and expertise.
- **Full Dashboard:** React/Vite SPA.
- **Database:** PostgreSQL 16 (production) or SQLite (testing only).
- **LLM:** Powered by Groq (Primary: `groq/openai/gpt-oss-120b`).

## 🛡️ CI/CD & Security

CodeGate guarantees safe operations via a hardened GitHub Actions pipeline (`codegate-ci.yml`) enforcing:
- **Dependency Auditing:** `pip-audit`, `npm audit`
- **Secret Scanning:** `gitleaks-action` blocks `.env`, `*.pem`, and keys.
- **Static Security:** `bandit` AST scanning for Python vulnerabilities.
- **Regression Tests:** 151/151 Backend tests and 41/41 Frontend tests pass safely.
- **API Security:** Nginx HTTP security headers, CORS restrictions, and robust error masking.

*Read the [Full Security Policy](docs/SECURITY.md).*

## 📚 Deep Dive Documentation

- [System Architecture](docs/architecture/CODEGATE_ARCHITECTURE.md)
- [Analysis Pipeline](docs/architecture/CODEGATE_ANALYSIS_PIPELINE.md)
- [Quality Score Mechanics](docs/features/QUALITY_SCORE.md)
- [Risk Score Mechanics](docs/features/RISK_SCORE.md)
- [GitHub App Integration](docs/integrations/GITHUB.md)

## 🤝 Upstream Attribution

CodeGate extends the open-source **PR-Agent** framework.
- **PR-Agent provided**: Foundational LLM wrappers (LiteLLM) and GitHub connection scaffolding.
- **CodeGate implemented**: The persistent PostgreSQL database layer, Static Analysis orchestrators, Quality/Risk scoring, Policy Engine, Reviewer Recommendation, Test execution, React Dashboard, and CI/CD security pipelines.
- CodeGate does not claim authorship over original PR-Agent code.

## 📜 License
MIT License. Upstream copyrights belong to their respective owners. CodeGate-specific additions are licensed under the same terms.
