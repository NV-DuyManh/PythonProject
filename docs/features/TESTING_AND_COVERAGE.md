# Testing & Coverage

CodeGate orchestrates test execution and coverage extraction safely.

## Executors
- **DisabledExecutor**: Default fail-safe.
- **LocalTrustedExecutor**: Runs tests on the local machine (requires trust).
- **DockerExecutor**: (Future/Optional)

## Changed-Code Coverage Semantics
Calculates coverage strictly on lines modified in the PR.
- No executable changed lines: returns `null` (not 100%).
- Failing tests affect the Testing dimension, but do not automatically drop the entire Quality score to 0.
