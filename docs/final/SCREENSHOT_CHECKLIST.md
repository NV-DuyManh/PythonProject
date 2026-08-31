# CodeGate: Final Screenshot Checklist

*Use your host browser (e.g., Chrome/Edge) to capture these required screenshots. Save them strictly under `docs/images/final/` to guarantee they render correctly in the presentation materials.*

**Pre-requisite**: Ensure the backend (port 8000) and frontend (port 5173) are running locally and populated with DEMO data.

## Required Screenshots

- [ ] `01_dashboard.png`
  - **View**: Main `/` Dashboard overview page.
  - **Focus**: Show the top-level repository cards and global analytics metrics.
  
- [ ] `02_repository_detail.png`
  - **View**: `/repository/{id}` page.
  - **Focus**: Show a list of Pull Requests categorized by PASS, WARNING, and BLOCK states.

- [ ] `03_pr_pass.png`
  - **View**: `/pr/{id}` for a successfully passing Pull Request.
  - **Focus**: Show the green PASS badge and a high Quality Score.

- [ ] `04_pr_warning.png`
  - **View**: `/pr/{id}` for a WARNING Pull Request.
  - **Focus**: Show the yellow WARNING badge and the exact rule (e.g., test coverage slightly low) that triggered it.

- [ ] `05_pr_block.png`
  - **View**: `/pr/{id}` for a BLOCKED Pull Request.
  - **Focus**: Show the red BLOCK badge prominently, confirming the policy engine stopped the merge.

- [ ] `06_quality_breakdown.png`
  - **View**: The Quality breakdown card on any PR page.
  - **Focus**: Capture the spider web/radar chart (if implemented) or the percentage bars showing Testing vs Security vs Code Quality.

- [ ] `07_risk_breakdown.png`
  - **View**: The Risk breakdown card on a high-risk PR.
  - **Focus**: Highlight the "Change Surface" or "Security" dimension causing the risk spike.

- [ ] `08_reviewer_recommendation.png`
  - **View**: The Recommended Reviewers section on a PR page.
  - **Focus**: Show the ranked list of developers and the reasons (e.g., `CODEOWNERS`, `File History`).

- [ ] `09_integrations.png`
  - **View**: The static analysis evidence card.
  - **Focus**: Show the output parsed from Ruff and Bandit (e.g., `B101` finding).

- [ ] `10_github_check.png`
  - **View**: A real Pull Request page on github.com.
  - **Focus**: Capture the bottom "Checks" area showing `CodeGate / PR Quality` successfully passing or failing the merge gate natively in GitHub.

> **CRITICAL SECURITY REMINDER**: Before saving and committing these images, inspect them manually to ensure no terminal windows, API keys, or private internal IP addresses leaked into the frame!
