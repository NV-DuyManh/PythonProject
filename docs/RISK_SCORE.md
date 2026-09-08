# Risk Score Mechanics

While the Quality Score measures the *craftsmanship* of the code, the **Risk Score** evaluates the *potential danger* or *blast radius* of merging a Pull Request.

The Risk Score evaluates whether a PR requires senior reviewer attention, even if the code quality is flawless.

## Version
Current algorithm version: `risk-v1`

## Score Composition

The Risk Score is independent of the Quality Score and is weighted as follows:

| Dimension | Weight | Description |
|---|:---:|---|
| **Security Findings** | 40% | Criticality of identified security vulnerabilities. |
| **Change Surface** | 25% | Number of files modified, lines added/removed, and core components touched. |
| **Sensitive Path** | 20% | Modifications to files matching sensitive patterns (e.g., `auth/`, `crypto/`, `settings.py`, `package.json`). |
| **Complexity Delta** | 15% | Significant spikes in cyclomatic complexity indicating convoluted logic. |

## Risk Levels

The aggregated risk factors map to the following Risk Levels:

- **LOW**: < 20 (Routine changes, minor UI tweaks, docs)
- **MEDIUM**: < 40 (Standard feature additions)
- **HIGH**: < 70 (Broad refactors, dependency updates, API changes)
- **CRITICAL**: >= 70 (Security vulnerabilities detected, auth logic changed, massive surface area)

## Reviewer Recommendation Synergy

CodeGate uses the Risk Score to drive the **Reviewer Recommendation** engine. 

- For **LOW** risk PRs, CodeGate may recommend recent contributors or junior devs to spread knowledge.
- For **HIGH/CRITICAL** risk PRs, CodeGate deterministically recommends `CODEOWNERS` and developers with the highest historical expertise in the modified directories.

*Note: CodeGate provides reviewer recommendations in the PR comment, but does **not** automatically assign reviewers in GitHub.*
