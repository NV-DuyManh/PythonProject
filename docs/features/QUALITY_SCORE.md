# Quality Score

The Quality Score is a deterministic 0-100 grade indicating the health of a Pull Request.

## Verified Weights
- Code Quality: 25%
- Security: 20%
- Testing: 20%
- Complexity: 15%
- Maintainability: 10%
- AI Review: 10%

## Partial-Evidence Normalization
If an analyzer (e.g., Testing) fails to run, its weight is re-distributed proportionately among the successful dimensions.
- `is_complete`: Boolean indicating if all analyzers finished successfully.
- `available_weight`: Total weight of successful dimensions.
- `missing_dimensions`: List of dimensions that failed/skipped.

## Grade Bands
- A: 90-100
- B: 80-89
- C: 70-79
- D: 60-69
- F: < 60
