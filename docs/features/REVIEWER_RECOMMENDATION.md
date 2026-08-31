# Reviewer Recommendation

CodeGate suggests optimal reviewers deterministically.

## Signals
- CODEOWNERS: 40%
- Exact file expertise: 30%
- Directory expertise: 20%
- Recency: 10%

## Constraints
- PR author is excluded.
- Bots are excluded.
- History is bounded by `base_sha`.
- Operates in an advisory-only capacity (does not auto-approve).
