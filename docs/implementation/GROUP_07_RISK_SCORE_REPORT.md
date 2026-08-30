# GROUP 07 — EXPLAINABLE PR RISK SCORE ENGINE

**Date:** 2026-08-30
**Status:** APPROVED

---

## 1. Executive Summary
Group 07 introduces the deterministic, explainable Risk Score Engine (0–100) for CodeGate. The engine operates completely independently from the Quality Score. It calculates PR risk by aggregating canonical rules based on the security footprint, raw change surface, sensitive path alterations, and code complexity. Risk scores are persistently stored and exposed via REST APIs.

## 2. Goals
- Provide a robust, deterministically explainable Risk Score (0-100).
- Isolate the Risk evaluation pipeline from Quality Score variations.
- Expose APIs for fetching and recalculating the Risk Score idempotently.
- Support partial data calculation gracefully when upstream analyzers fail.
- Exclude historical debt (findings not on changed lines) from the Risk Score.

## 3. Final Architecture
The Group 07 implementation relies on the following core components in `codegate/engines/risk/`:

```text
codegate/engines/risk/
├── __init__.py
├── config.py
├── schemas.py
├── components.py
├── engine.py
└── explanation.py
```

Plus the integrations across the system:
- `RiskScore` SQLAlchemy model
- `RiskScoreStore` repository
- `RiskScoreService` orchestration layer
- Risk REST API endpoints
- `AnalysisOrchestrator` integration for the automatic pipeline
- Alembic database migrations

## 4. RiskScore Model
The overall PR Risk Score is derived from the following canonical dimensions:

```text
Security Risk         40%
Change Surface Risk   25%
Sensitive Path Risk   20%
Complexity Risk       15%
```

The Risk Score domain bounds are:
- `0` = very low risk
- `100` = extremely high risk

The Risk Score is evaluated independently of the Quality Score. (No `Risk = 100 - Quality` logic).

## 5. Risk Versioning
Current calculation version: `risk-v1`

## 6. Dimensions & Weights

### 7. Security Risk (40%)
Calculated from `BANDIT` or `AI` findings (security category). Historical findings (where `is_changed_file = false`) do not increase the PR Risk Score.

Severity mapping:
- `LOW      → 15`
- `MEDIUM   → 35`
- `HIGH     → 70`
- `CRITICAL → 100`

State handling:
- `SUCCESS` + `0` findings → `security_risk = 0`
- `FAILED` / `TIMEOUT` → `security_risk = null`

### 8. Change Surface Risk (25%)
Calculated strictly using `changed_lines = additions + deletions`.

Lines mapping (`0.70` weight of component):
```text
0           → 0
1–20        → 5
21–50       → 15
51–100      → 30
101–250     → 50
251–500     → 70
501–1000    → 85
>1000       → 100
```

Files mapping (`0.30` weight of component):
```text
0       → 0
1       → 5
2–3     → 10
4–7     → 25
8–15    → 50
16–30   → 75
>30     → 100
```

Formula:
```text
change_surface_risk = (lines_risk * 0.70) + (files_risk * 0.30)
```

### 9. Sensitive Path Risk (20%)
Calculated by matching changed files against sensitive path tiers. If multiple matches occur, `risk = maximum tier` (no summing).

- **Tier 1 (risk = 100):** `auth`, `authentication`, `security`, `permissions`, `payment`, `payments`, `billing`, `authorization`
- **Tier 2 (risk = 70):** `migrations`, `database`, `infra`, `infrastructure`, `deploy`, `deployment`, `.github/workflows`, `Dockerfile`, `docker-compose`
- **Tier 3 (risk = 40):** `config`, `settings`, `requirements`, `pyproject.toml`, `poetry.lock`, `package-lock.json`

### 10. Complexity Risk (15%)
Calculated from `RADON` cyclomatic complexity. Multiple changed symbols result in `complexity_risk = maximum mapped risk`.

Mapping:
- `A → 0`
- `B → 0`
- `C → 25`
- `D → 50`
- `E → 75`
- `F → 100`

State handling:
- `FAILED` / `TIMEOUT` → `complexity_risk = null`

## 11. Partial/Missing Data Handling
Missing dimension risk is represented exactly as `null` (not `0`). 

When missing data occurs, the overall risk is adjusted against the remaining available weight:
```text
overall_risk = sum(component_risk × canonical_weight) / sum(available canonical weights)
```

The output explicitly includes:
- `overall_risk`, `risk_level`, `is_complete`
- `available_weight`, `missing_dimensions`
- `components`, `flags`, `calculation_version`

## 12. Risk Levels
The numeric risk is bucketed into threshold levels:
```text
0 <= risk < 20       LOW
20 <= risk < 40      MEDIUM
40 <= risk < 70      HIGH
70 <= risk <= 100    CRITICAL
```

## 13. Historical Debt Exclusion
Only changed lines/files contribute to Security Risk and Complexity Risk. Existing vulnerabilities in unchanged lines are intentionally excluded from the PR Risk increment calculation.

## 14. Explainability
The risk calculation generates a deeply nested JSON breakdown (`breakdown_json`), tracing the exact origins of scores, active tiers, matched files, and rules to provide complete diagnostic transparency.

## 15. Risk Flags
The engine raises contextual flags (e.g., `MISSING_SECURITY_DATA`, `HIGH_SENSITIVE_FILES_CHANGED`) within the explanation to explicitly warn reviewers of specific high-risk signals or partial data runs.

## 16. Quality Independence
The Risk Score does not penalize failures of the `QualityScoreEngine`. The calculation functions are entirely isolated. If Quality fails, Risk calculates. If Risk fails, findings and Quality remain intact.

## 17. Persistence & Idempotency
Data is persisted in the `RiskScore` entity, structured as:
- `analysis_run_id`, `overall_risk`, `risk_level`
- `security_risk`, `change_surface_risk`, `sensitive_path_risk`, `complexity_risk`
- `available_weight`, `is_complete`, `missing_dimensions`, `breakdown_json`
- `calculation_version`, `created_at`, `updated_at`

The unique constraint is `analysis_run_id + calculation_version`. Recalculating the same version will safely upsert/replace idempontently.

## 18. REST API
Exposed via:
```http
GET /api/v1/analyses/{analysis_id}/risk
POST /api/v1/analyses/{analysis_id}/risk/recalculate
```

## 19. Automatic Pipeline Integration
The Risk Score flows transparently through the PR lifecycle:
```text
GitHub PR
↓
AI Review
↓
Static Analysis
↓
Quality Score
↓
Risk Score
↓
AnalysisRun COMPLETED
```

## 20. Failure Isolation
Risk pipeline failure is isolated from general analysis functionality. Upstream findings, code metrics, and the baseline QualityScore remain fully accessible if the Risk Engine encounters a fatal exception.

## 21. Alembic Migration
Database schema updates handled by:
```text
b0fce6cc6f73
```
Migration chain: `31ea6c57c62c` → `263ae425f3cf` → `f7ff7f175678` → `b0fce6cc6f73`
Tested via `upgrade head`, `downgrade`, and `re-upgrade`.

## 22. Testing
Verified against boundary mappings, idempotent database inserts, pipeline orchestrator workflows, and API responses.

## 23. Regression
Confirmed that the upstream PR-Agent functionality is unaffected.

## 24. Files Created
(Consolidated within the 07A and 07B phases).
- `codegate/engines/risk/...`
- `codegate/database/models/analysis.py` (added RiskScore model)
- `tests/codegate/engines/test_risk_engine.py`
- `tests/codegate/api/test_risk_api.py`
- `tests/codegate/services/test_risk_persistence.py`

## 25. Files Modified
(Consolidated within the 07A and 07B phases).
- `codegate/services/analysis_orchestrator.py`
- `codegate/api/routers/analyses.py`

## 26. Known Limitations
None.

## 27. Final Verdict

```text
GROUP 07 — EXPLAINABLE PR RISK SCORE ENGINE

RISK ENGINE:                     PASS
DETERMINISTIC:                   PASS
QUALITY INDEPENDENCE:            PASS

SECURITY RISK:                   PASS
CHANGE SURFACE RISK:             PASS
SENSITIVE PATH RISK:             PASS
COMPLEXITY RISK:                 PASS

PARTIAL RISK HANDLING:           PASS
ANALYZER FAILURE AWARENESS:      PASS
HISTORICAL DEBT EXCLUSION:       PASS

EXPLAINABILITY:                  PASS

RISK PERSISTENCE:                PASS
RISK API:                        PASS
AUTOMATIC CALCULATION:           PASS
FAILURE ISOLATION:               PASS

MIGRATION:                       PASS
FRESH DB MIGRATION:              PASS

DATABASE PORTABILITY:
RiskScore SQLite: PASS
RiskScore PostgreSQL-compatible: PASS
QualityScore SQLite: PASS
QualityScore PostgreSQL-compatible: PASS
Idempotent upsert: PASS

CODEGATE TESTS:
PASSED: 63
FAILED: 0

GROUP 07 FINAL STATUS: APPROVED
READY FOR GROUP 08: YES
```
