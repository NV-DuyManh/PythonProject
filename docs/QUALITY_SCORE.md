# Quality Score Mechanics

CodeGate computes a comprehensive **Quality Score** (0-100) for every Pull Request analyzed. This score determines if a PR passes the Quality Gate.

## Version
Current algorithm version: `quality-v1`

## Score Composition

The Quality Score is an aggregated metric composed of deterministic and probabilistic inputs. It is calculated using the following weights:

| Dimension | Weight | Source | Description |
|---|:---:|---|---|
| **Code Quality** | 25% | AI Review & Static Analysis | General code smells, maintainability issues, and stylistic flaws. |
| **Security** | 20% | AI Review & Bandit | Detected security vulnerabilities, hardcoded secrets, or unsafe patterns. |
| **Testing** | 20% | DockerTestExecutor | Presence of tests, test pass rate, and test coverage delta. |
| **Complexity** | 15% | Radon | Cyclomatic and cognitive complexity changes. |
| **Maintainability** | 10% | AI Review | DRY violations, missing documentation, and architecture smells. |
| **AI Review** | 10% | AI Review | The AI's overall estimated effort and holistic PR sentiment. |

## Grading Scale

The numeric score (0-100) translates into the following grades:

- **A**: >= 90
- **B**: >= 80
- **C**: >= 70
- **D**: >= 60
- **F**: < 60

## Normalization

Because not all repositories have tests configured, CodeGate employs **partial normalization**. If the `Testing` executor is disabled for a repository, the 20% weight is redistributed proportionally among the remaining dimensions. This ensures that repositories without tests are not permanently stuck with a maximum score of 80.

## Merge Policy Gate

The final Quality Score is evaluated against the Workspace's defined Merge Policy. 

CodeGate will issue a GitHub Check status based on the policy:
- **BLOCK (Failure)**: If the score falls below the required threshold.
- **WARNING (Neutral)**: If the score is marginal.
- **PASS (Success)**: If the score exceeds the threshold.

*Note: CodeGate evaluates policies and reports checks, but does **not** automatically merge PRs on GitHub.*
