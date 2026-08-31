# CodeGate: 10-Minute Demo Script

*This script is designed for a detailed 10-minute presentation, allowing deep dives into architecture, multiple PR scenarios, and security configurations.*

## [00:00 - 01:30] Introduction & Problem Statement
**Action**: Display Slide 2 & 3.
**Speaker**: "Hello, I am [Name]. My project is CodeGate, an AI-assisted Pull Request quality intelligence platform. Modern teams use AI for code review, but AI hallucination is a major risk. An LLM cannot be trusted to unilaterally approve or block production code. CodeGate solves this by wrapping the AI review in a deterministic safety net—aggregating static analysis, security scans, and test coverage to enforce strict, explainable merge policies."

## [01:30 - 03:00] Architecture & Pipeline
**Action**: Display Slide 5 (Architecture) and Slide 6 (Analysis Pipeline).
**Speaker**: "When a developer opens a PR, a webhook is sent to the CodeGate API. CodeGate is built on top of the open-source PR-Agent framework, leveraging its LLM hooks. However, CodeGate introduces a massive orchestration layer. It triggers the AI for semantic feedback while simultaneously launching local instances of Ruff, Bandit, and Pytest. All of this evidence is persisted into a PostgreSQL database, a completely novel addition to the upstream project."

## [03:00 - 04:30] Scenario A: The PASS Demo
**Action**: Open Dashboard (`http://127.0.0.1:5173`), select a PASS PR.
**Speaker**: "Let's look at the Dashboard, built in React and Vite. Here is a 'PASS' Pull Request. The Quality Score is 92. The Risk Score is 15. The policy engine evaluated the deterministic evidence: zero critical vulnerabilities, solid test coverage, and a positive AI review. Because it passed all thresholds, CodeGate issued a PASS policy."

## [04:30 - 06:00] Scenario B: The BLOCK Demo
**Action**: Select a BLOCK PR in the Dashboard.
**Speaker**: "Contrast that with this 'BLOCK' PR. The AI actually gave this PR a decent review, focusing on the logic. However, CodeGate's static analysis orchestration caught a severe vulnerability via Bandit—an unsafe execution path. The Policy Engine immediately overrode the AI's probabilistic assessment, assigning a BLOCK policy. This proves why hybrid evidence layering is critical."

## [06:00 - 07:00] GitHub Integration & Reviewers
**Action**: Open GitHub to show the Check Run and return to the Dashboard Reviewer section.
**Speaker**: "CodeGate communicates this BLOCK decision natively back to GitHub via a Check Run, stopping the merge. But it goes a step further. By analyzing Git history, file touches, and CODEOWNERS, CodeGate generates an advisory Reviewer Recommendation, highlighting the exact human managers best suited to audit this vulnerability."

## [07:00 - 08:30] Security, Deployment, & CI/CD
**Action**: Open IDE to show `compose.codegate.yml` and `codegate-ci.yml`.
**Speaker**: "Because this tool handles source code, security is paramount. CodeGate runs locally or via a hardened Docker Compose cluster isolating the React frontend, Python API, and PostgreSQL database. Furthermore, the repository is protected by a strict GitHub Actions CI pipeline that audits dependencies via `pip-audit`, blocks secrets with `gitleaks`, and runs 100% of the backend Pytest suite."

## [08:30 - 10:00] Conclusion & Q&A
**Action**: Display Slide 15 (Conclusion).
**Speaker**: "CodeGate successfully proves that we can harness the power of AI code review without sacrificing enterprise safety or deterministic merge policies. It centralizes intelligence, isolates risk, and provides deep engineering visibility. Thank you, I am now ready to answer your questions."
