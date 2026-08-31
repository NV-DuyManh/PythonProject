# CodeGate: Defense Q&A

*This document contains 30 likely academic/professional defense questions, including hard critique questions, along with concise, strong answers.*

### 1. Why reuse PR-Agent?
**Answer**: PR-Agent provides a robust foundation for interacting with GitHub's Webhook API and wrapping LLM calls (via LiteLLM). Reusing this infrastructure allowed me to focus my engineering effort on the novel aspects of CodeGate: the deterministic scoring engines, policy evaluation, data persistence, and the dashboard, rather than rewriting boilerplate GitHub integration code.

### 2. What did you build yourself? (CodeGate vs PR-Agent)
**Answer**: I architected and built the entire PostgreSQL persistent data model, the Static Analysis orchestrator (Ruff/Bandit/Radon), the Quality and Risk scoring engines, the Policy Engine, the Reviewer Recommendation system, the React/Vite Dashboard, and the Docker/CI hardening. PR-Agent handles the raw LLM prompt generation; CodeGate orchestrates the intelligence around it.

### 3. Why not just use GitHub Copilot?
**Answer**: Copilot is a developer-side assistant focused on code generation and inline autocomplete. CodeGate is a repository-side orchestration platform focused on enforcing merge gates, evaluating risk, and centralizing security/testing evidence for engineering managers. They solve completely different problems.

### 4. Why not SonarQube?
**Answer**: SonarQube is excellent for deterministic static analysis but lacks semantic understanding of the *intent* of a Pull Request. CodeGate integrates deterministic tools (like Bandit/Ruff) *alongside* semantic AI review, providing a holistic merge policy rather than just a static code scan.

### 5. Why AI?
**Answer**: AI is uniquely capable of understanding the human intent behind a code change. It can detect logical flaws, explain complex changes, and summarize PRs in ways that deterministic linters cannot.

### 6. Why deterministic scores?
**Answer**: AI is probabilistic and prone to hallucination. An enterprise cannot block a critical deployment based solely on an LLM's hallucinated opinion. Deterministic scores (from Ruff, Bandit, Pytest) provide hard, verifiable evidence that anchors the AI's feedback.

### 7. Why Quality and Risk separate?
**Answer**: Because high quality does not equal low risk. A developer could write perfectly secure, 100% tested code (High Quality), but if they are refactoring the core authentication system, the blast radius is massive (High Risk). Separating them allows for nuanced merge policies.

### 8. Why these specific weights for Quality/Risk?
**Answer**: The weights (e.g., Code Quality 25%, Security 20% for Quality) reflect standard enterprise engineering priorities—security and testing are heavily weighted, while AI review is kept at 10% to prevent hallucination dominance.

### 9. How are the weights justified scientifically?
**Answer**: They are not empirically universal constants; they are designed engineering policy weights. In a real-world scenario, these would be calibrated over time using machine learning against an organization's historical incident rates.

### 10. What happens when AI is wrong? (Is this just PR-Agent with a dashboard?)
**Answer**: If the AI hallucinates, CodeGate relies on the deterministic Policy Engine. Because AI Review is only 10% of the Quality Score, a hallucinated "bad review" on perfectly passing tests and static analysis will NOT block the PR. CodeGate is far more than a dashboard; it is a deterministic safety net around the AI.

### 11. What happens when Groq fails?
**Answer**: The system captures the API failure, logs it safely, and redistributes the 10% AI weight to the remaining deterministic dimensions (Testing, Security, Complexity). The PR evaluation continues, and the dashboard remains available.

### 12. What happens when GitHub fails?
**Answer**: Webhook events would be lost, but because CodeGate uses PostgreSQL, historical analytics, previous PR evaluations, and the Dashboard remain fully functional.

### 13. How do you prevent secrets from leaking?
**Answer**: The system employs `gitleaks-action` in CI. Environment variables are managed via `.env` files and `.secrets.toml`, both of which are strictly gitignored. Docker isolates credentials, and the API globally suppresses sensitive headers from stack traces.

### 14. Why PostgreSQL?
**Answer**: PostgreSQL provides robust relational integrity, JSONB support for unstructured analyzer payloads, and concurrency safety for handling simultaneous webhook events, which SQLite struggles with at scale.

### 15. Why does SQLite still exist in the project?
**Answer**: SQLite was preserved to maintain the legacy `CodeGateLauncher` workflow for local, rapid prototyping without requiring developers to spin up Docker containers.

### 16. Why Docker?
**Answer**: Docker guarantees environment parity between development and production. It ensures the backend, frontend, and database run on the exact same OS dependencies, eliminating "it works on my machine" issues.

### 17. Why not Kubernetes?
**Answer**: Kubernetes introduces immense operational overhead. For the scale of this project, a single-node Docker Compose architecture is completely sufficient. Kubernetes would be future work if deploying to a multi-node enterprise cluster.

### 18. What does CI test?
**Answer**: CI tests Python code formatting (`ruff`), Python security (`bandit`), dependency vulnerabilities (`pip-audit`, `npm audit`), secret leakage (`gitleaks`), backend logic (`pytest` against live Postgres), frontend logic (`vitest`), and Docker build integrity.

### 19. Why no cloud deployment?
**Answer**: The scope of this phase was to provide a hardened, production-ready containerized package. Actual cloud deployment requires external provisioning (AWS/GCP), domain registration, and TLS termination, which were out of scope.

### 20. What is a merge gate?
**Answer**: A merge gate is a policy rule that prevents a Pull Request from being merged into the main branch until specific conditions (like passing tests, zero security vulnerabilities, and peer approval) are met.

### 21. Why no automatic merge?
**Answer**: CodeGate acts as an advisory intelligence platform. Automatically merging code introduces severe security risks. CodeGate publishes a GitHub Check Run (PASS/BLOCK), leaving the final click to a human maintainer.

### 22. How does reviewer recommendation work?
**Answer**: It queries the Git history of the files modified in the PR. It ranks developers based on exact file touches, directory expertise, CODEOWNERS rules, and recency of commits.

### 23. How does CODEOWNERS affect recommendation?
**Answer**: The system parses the repository's `.github/CODEOWNERS` file. If a modified file matches a CODEOWNERS pattern, those specified users receive a massive weight boost (40%) in the recommendation ranking.

### 24. How does changed-code coverage work?
**Answer**: It calculates coverage strictly on the executable lines modified *in the PR*, not the entire repository. If you change 10 executable lines and tests cover 8 of them, your changed-code coverage is 80%.

### 25. How does webhook security work?
**Answer**: GitHub signs webhook payloads using a shared secret. The CodeGate API intercepts the payload, computes an HMAC SHA-256 hash using the local secret, and compares it to the `X-Hub-Signature-256` header to verify authenticity.

### 26. How is data isolated?
**Answer**: Data is isolated via relational foreign keys tied to the `Repository` and `GitHubConnection` tables. API endpoints filter aggressively by `repository_id` to prevent cross-tenant leakage.

### 27. How does the system scale?
**Answer**: The stateless backend can be scaled horizontally behind a load balancer. PostgreSQL can be scaled vertically or replicated. Intensive static analysis tasks can eventually be decoupled into asynchronous Celery workers.

### 28. What are the system's limitations?
**Answer**: CodeGate does not natively terminate TLS. AI relies entirely on third-party APIs (Groq). Executing untrusted PR code for tests requires extremely careful local sandbox configurations to prevent RCE.

### 29. What would you improve next?
**Answer**: I would implement an external Secret Manager (like HashiCorp Vault), introduce Machine Learning to calibrate the Risk Score weights based on historical bugs, and implement Celery for asynchronous test execution.

### 30. How do you prove project contribution?
**Answer**: My contribution is proven via the distinct git commit history in `codegate/`, `dashboard/`, `docker/`, and the test suites. The "Upstream vs CodeGate" documentation explicitly distinguishes my orchestration layers from the foundational PR-Agent hooks.

### 31. Could malicious PR code attack CodeGate?
**Answer**: Yes, if the Test Executor blindly runs `pytest` on malicious PR code. This is why CodeGate defaults to `DisabledExecutor` or requires strict `LocalTrustedExecutor` configurations. In production, tests should run in isolated, disposable ephemeral containers.

### 32. Why should developers trust an AI review?
**Answer**: They shouldn't trust it blindly. That is the exact thesis of CodeGate: layering deterministic static analysis and coverage data over the AI review. Developers trust CodeGate because the AI's opinion is mathematically bounded by hard evidence.
