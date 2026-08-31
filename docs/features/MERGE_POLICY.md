# Merge Policy

Policies dictate the outcome of a Pull Request evaluation based on configurable thresholds.

## Outcomes
- **BLOCK**: Hard failure.
- **WARNING**: Advisory notice.
- **PASS**: Success.

**Precedence:** BLOCK > WARNING > PASS

## Factors
- Quality thresholds
- Risk thresholds
- Security findings
- Test failures
- Coverage
- Missing evidence

## GitHub Check Mapping
- PASS → `success`
- WARNING → `neutral`
- BLOCK → `failure`

No automatic merge or branch-protection modification is performed by CodeGate.
