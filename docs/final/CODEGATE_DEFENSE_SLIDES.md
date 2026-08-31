# CodeGate: Defense Presentation Slides

*This document contains the structural outline, key bullets, visual suggestions, and speaker notes for a 15-slide academic/professional defense of CodeGate.*

---

## Slide 1: Title
**Title**: CodeGate: AI-Assisted Pull Request Quality Intelligence
**Message**: Bringing deterministic engineering policy to AI code reviews.
**Visual**: CodeGate Logo + Student/Developer Name + Date.
**Speaker Notes**:
"Welcome. Today I will present CodeGate, an orchestrator designed to solve the critical gap between raw AI code assistance and strict enterprise merge policies."

---

## Slide 2: The Problem
**Title**: Why AI Code Review Isn't Enough
**Message**: Probabilistic AI hallucination cannot dictate blocking merge gates.
**Bullets**:
- PRs contain diverse signals (security, tests, logic, risk).
- AI models provide excellent semantic feedback but lack deterministic reliability.
- Teams need explainable evidence, not just a "Looks good to me" from an LLM.
- Engineering managers lack historical visibility into PR quality.
**Visual**: A diagram showing a developer overwhelmed by conflicting PR signals.
**Speaker Notes**:
"We've all seen AI review tools. But relying solely on LLMs is dangerous. They hallucinate. For an enterprise to block a merge, they need hard, deterministic evidence alongside AI."

---

## Slide 3: Objectives
**Title**: Project Objectives
**Message**: Build a centralized, hybrid analysis orchestrator.
**Bullets**:
- Centralize PR quality evidence.
- Combine probabilistic AI with deterministic static analysis.
- Produce explainable Quality and Risk scores.
- Evaluate configurable merge policies.
- Recommend suitable human reviewers.
**Visual**: Bulleted list with a checkmark graphic.
**Speaker Notes**:
"My objective was to build CodeGate: a system that centralizes these signals, calculates explainable Quality and Risk scores, enforces merge policies, and integrates directly back into GitHub."

---

## Slide 4: Upstream vs. CodeGate
**Title**: Extending PR-Agent
**Message**: Clearly separating the foundation from the CodeGate implementation.
**Bullets**:
- **PR-Agent (Foundation)**: GitHub App API, LLM Wrapper (LiteLLM/Groq), foundational prompts.
- **CodeGate (My Addition)**: Persistent PostgreSQL Domain Model, Static Analysis Orchestrators, Quality/Risk Score Engines, Policy Engine, Reviewer Recommendation, React Dashboard, and Docker/CI Architecture.
**Visual**: A two-column comparison table.
**Speaker Notes**:
"To avoid reinventing the wheel, I built CodeGate on top of the open-source PR-Agent framework. I utilized their GitHub and LLM hooks, while I architected and implemented the entire persistent data model, the scoring engines, the dashboard, and the CI infrastructure."

---

## Slide 5: CodeGate Architecture
**Title**: System Architecture
**Message**: How the components interact end-to-end.
**Bullets**:
- GitHub Webhooks trigger the API.
- Orchestrator fans out to AI, Static Analysis (Ruff/Bandit), and Test Executors.
- Data is persisted to PostgreSQL.
- Dashboard and GitHub Checks consume the results.
**Visual**: Mermaid Architecture Diagram from the Technical Report.
**Speaker Notes**:
"When a PR is opened, CodeGate catches the webhook and orchestrates a fan-out process. It simultaneously queries the AI and runs local static analyzers. Everything is persisted into a Postgres database."

---

## Slide 6: Analysis Pipeline
**Title**: Deterministic vs. Probabilistic
**Message**: Layering evidence for safety.
**Bullets**:
- **Probabilistic**: Groq LLM (Semantic Review, Explanations).
- **Deterministic**: Ruff (Style/Correctness), Bandit (Security), Radon (Complexity).
- **Testing**: Changed-code coverage via Pytest.
**Visual**: Funnel graphic combining multiple tool logos into a single database record.
**Speaker Notes**:
"This slide details the analysis layer. We use Bandit for security AST scanning and Ruff for static analysis. This deterministic data anchors the probabilistic AI review."

---

## Slide 7: The Quality Score
**Title**: Explainable Quality Scoring
**Message**: Fair, dynamically weighted grading.
**Bullets**:
- Weights: Code Quality (25%), Security (20%), Testing (20%), Complexity (15%), Maintainability (10%), AI Review (10%).
- Missing evidence redistributes available weight (doesn't default to 0).
- Transparently mapped to A-F letter grades.
**Visual**: A pie chart showing the weight distribution.
**Speaker Notes**:
"The Quality Score tells us how 'good' the code is. Importantly, if a repository isn't configured for tests, the 20% test weight is dynamically redistributed so the developer isn't unfairly punished."

---

## Slide 8: The Risk Score
**Title**: Independent Risk Assessment
**Message**: Quality is not the inverse of Risk.
**Bullets**:
- Weights: Security (40%), Change Surface (25%), Sensitive Path (20%), Complexity (15%).
- High Quality ≠ Low Risk.
- Evaluates the potential 'blast radius' of merging the PR.
**Visual**: A graph showing Quality on the X-axis and Risk on the Y-axis.
**Speaker Notes**:
"Risk is calculated completely independently. A PR could be perfectly written with 100% test coverage, but if it modifies the core authentication module, the Risk Score correctly spikes to reflect the sensitive path."

---

## Slide 9: Policy & Reviewer Recommendation
**Title**: Merge Gates & Human Expertise
**Message**: Automating process, not approvals.
**Bullets**:
- **Policy Engine**: PASS, WARNING, BLOCK (Strict Precedence).
- **Reviewer Recommendation**: Ranks users via CODEOWNERS (40%), File History (30%), Directory (20%), Recency (10%).
- CodeGate is advisory; it does not automatically merge.
**Visual**: A flowchart mapping Evidence -> Policy -> Reviewer.
**Speaker Notes**:
"With scores calculated, the Policy Engine determines if the PR should PASS, WARNING, or BLOCK. Simultaneously, it scans Git history to recommend the exact developers who have context on the modified files."

---

## Slide 10: GitHub Integration
**Title**: Frictionless Developer Experience
**Message**: Meeting developers where they work.
**Bullets**:
- Seamless GitHub App Webhook Integration.
- SHA-256 HMAC Payload Verification.
- Automated GitHub Check Runs showing PASS/BLOCK status.
**Visual**: Screenshot of a GitHub Check Run passing/failing on a PR.
**Speaker Notes**:
"The developer never has to leave GitHub. CodeGate publishes its policy decision directly to the PR as a Check Run, providing immediate feedback."

---

## Slide 11: The Dashboard
**Title**: Engineering Visibility
**Message**: Real-time analytics for managers and teams.
**Bullets**:
- React / Vite SPA.
- View real-time PR status, score breakdowns, and analyzer findings.
- Aggregate repository health analytics.
**Visual**: Screenshot of the CodeGate Dashboard Overview page.
**Speaker Notes**:
"For engineering managers, the CodeGate Dashboard provides deep visibility. They can see why a PR was blocked, drill into specific static analysis findings, and track repository health over time."

---

## Slide 12: CI/CD & Security Hardening
**Title**: Production-Ready Infrastructure
**Message**: Built for security and reproducibility.
**Bullets**:
- Docker Compose cluster isolating backend, frontend, and PostgreSQL.
- GitHub Actions CI running `gitleaks`, `pip-audit`, and `npm audit`.
- Nginx Security Headers and strict CORS policies.
**Visual**: Diagram of the CI pipeline passing/failing.
**Speaker Notes**:
"To ensure the project is deployable and secure, Phase 5 introduced a robust Docker architecture and a strict GitHub Actions pipeline that blocks hardcoded secrets and vulnerable dependencies."

---

## Slide 13: Demo Results
**Title**: End-to-End Scenarios
**Message**: Proving the system works in practice.
**Bullets**:
- **CASE A (PASS)**: High Quality, Low Risk, No Security Findings.
- **CASE B (WARNING)**: Minor Complexity Warnings, Low Test Coverage.
- **CASE C (BLOCK)**: Bandit Security Vulnerability Detected (Overrides Quality).
**Visual**: Three stacked screenshots of the Dashboard showing Pass/Warn/Block states.
**Speaker Notes**:
"I will now demonstrate three persisted scenarios. A clean PASS, a WARNING due to complexity, and a strict BLOCK caused by a deterministic security finding that the AI alone might have missed."

---

## Slide 14: Limitations
**Title**: Current Limitations
**Message**: Honest assessment of technical boundaries.
**Bullets**:
- No native cloud TLS termination (requires external reverse proxy).
- AI insights depend entirely on external API availability (Groq).
- Test execution trust boundaries require strict local configuration.
- Reviewer expertise is blind to uncommitted domain knowledge.
**Visual**: A simple list.
**Speaker Notes**:
"As with any system, there are limitations. CodeGate does not terminate its own SSL, relying on infrastructure proxies. Furthermore, test execution relies on the executor configuration to prevent arbitrary code execution from malicious PRs."

---

## Slide 15: Conclusion & Future Work
**Title**: Summary & Next Steps
**Message**: CodeGate elevates PR reviews.
**Bullets**:
- Centralized, deterministic evidence prevents AI hallucination risks.
- Explainable scores improve team velocity.
- **Future**: Enterprise SSO, ML-calibrated risk weights, GitLab/Bitbucket support.
**Visual**: CodeGate Logo + "Thank You".
**Speaker Notes**:
"In conclusion, CodeGate successfully bridges the gap between raw AI assistance and enterprise-grade policy. Thank you for your time. I am happy to take any questions."
