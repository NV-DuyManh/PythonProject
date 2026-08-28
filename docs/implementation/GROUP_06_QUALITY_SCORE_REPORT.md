# GROUP 06 — EXPLAINABLE QUALITY SCORE ENGINE — ACCEPTANCE REPORT

**Date:** 2026-08-28
**Status:** VERIFIED

---

## 1. Executive Summary
Group 06 introduces a deterministic, explainable, and persisted Quality Score Engine for CodeGate. The engine calculates an overall PR quality score (0–100) based on six canonical dimensions: Code Quality, Security, Complexity, Testing, Maintainability, and AI Review. 

It handles missing data correctly (e.g. Test/Coverage not yet implemented) by re-normalizing the weights of available dimensions and explicitly marking the score as "partial". All scoring logic is completely objective, versioned, and independent of LLM whims.

---

## 2. Quality Architecture
```
codegate/engines/quality/
├── __init__.py
├── config.py         — Centralized weights, penalties, and grade thresholds
├── schemas.py        — ComponentResult and QualityScoreResult Pydantic models
├── components.py     — Individual scoring functions for the 6 canonical dimensions
├── engine.py         — QualityScoreEngine orchestration and partial weight normalization
└── explanation.py    — Breakdown dictionary builder
```
The architecture is decoupled from HTTP routers and the database, operating as a pure function `(Findings, Metrics) -> QualityScoreResult`.

---

## 3. QualityScore Model
Added to `codegate/database/models/analysis.py`:
- Contains `overall_score`, `grade`, `is_complete`, `available_weight`, `calculation_version`.
- Persists all 6 component scores (nullable) and `missing_dimensions`.
- `breakdown_json` holds the detailed explainability tree.
- A `UniqueConstraint` on `(analysis_run_id, calculation_version)` prevents duplicate rows.

---

## 4. Canonical Dimensions & Weights
- **Code Quality:** 25%
- **Security:** 20%
- **Testing:** 20%
- **Complexity:** 15%
- **Maintainability:** 10%
- **AI Review:** 10%

---

## 5. Missing-Dimension Strategy
Dimensions lacking real data (e.g., Testing, Maintainability) are skipped. The engine calculates the `available_weight` and normalizes the score. `is_complete` is set to `False`. We do not pretend missing data means "100% perfect".

---

## 6. Penalty Policy
Configured centrally in `config.py`:
- INFO: 0
- LOW: 2
- MEDIUM: 6
- HIGH: 15
- CRITICAL: 30

---

## 7. Code Quality Component
Sources `RUFF` findings on changed code. Starts at 100, subtracts penalties, clamped at 0.

## 8. Security Component
Sources `BANDIT` and AI security findings on changed code. Implements basic exact-match fingerprinting `(source, rule_id, file_path, start_line)` to deduplicate repeated scoring facts before applying penalties.

## 9. Complexity Component
Sources `RADON` cyclomatic complexity metrics on changed files. Maps grades to penalties: `C=3, D=8, E=15, F=25`.

## 10. Maintainability Component
Currently returns `None` (missing data). 

## 11. AI Review Component
Sources `AI` findings. Not strictly bound to `is_changed_file=True` to allow PR-level comments, but ignores if `is_changed_file=False`. Clamped at 10% canonical weight to prevent AI from dominating objective metrics.

## 12. Testing Component
Currently returns `None` (missing data).

---

## 13. Changed-Code Rules
Code quality and Security components explicitly check `(is_new_code or is_changed_file)`. Historical debt (`is_changed_file=False`) is successfully excluded from the penalty calculation.

## 14. Grade Policy
- A: 90–100
- B: 80–89.99
- C: 70–79.99
- D: 60–69.99
- F: <60
Boundaries verified in unit tests.

## 15. Explainability
`breakdown_json` exposes:
- Base score and final clamped score
- Finding count and penalty total
- Array of `reasons` mapping exact finding IDs to applied severity and penalty amounts.

## 16. Persistence
`QualityScoreService.calculate_and_persist()` handles SQLite upsert based on `(analysis_run_id, calculation_version)`, mapping component scores correctly to DB columns.

## 17. Automatic Calculation
Integrated into `codegate/services/analysis_orchestrator.py`. Triggered automatically after findings are persisted and before `COMPLETED` state is saved. Quality score calculation errors are caught and logged, preserving the original AnalysisRun data.

## 18. API
- `GET /api/v1/analyses/{analysis_id}/quality`
- `POST /api/v1/analyses/{analysis_id}/quality/recalculate`
Endpoints fully implemented in `analyses.py` with 404 handling.

## 19. Migration
Alembic migration `f7ff7f175678` successfully created `quality_scores` table as a child of `263ae425f3cf`.
**Fresh DB test:** `upgrade head`, `downgrade 263ae425f3cf`, and `re-upgrade` all completed cleanly.

## 20. Tests
Engine and API tests covering all requirements: no-findings, severity penalties, historical debt exclusion, partial weight normalization, clamp, grade boundaries, and reproducibility. 
All CodeGate tests pass.

## 21. Reproducibility
Verified. Multiple calls with identical inputs yield identical score, grade, and breakdown.

## 22. Regression
**CodeGate tests:** `46 passed, 0 failed` (baseline was 37).
**PR-Agent tests:** `2568 passed, 9 failed` (all in known baseline families). No new upstream failures.

## 23. Files Created
- `codegate/engines/quality/__init__.py`
- `codegate/engines/quality/config.py`
- `codegate/engines/quality/schemas.py`
- `codegate/engines/quality/components.py`
- `codegate/engines/quality/engine.py`
- `codegate/engines/quality/explanation.py`
- `codegate/schemas/quality.py`
- `codegate/repositories/quality_store.py`
- `codegate/services/quality_service.py`
- `codegate/alembic/versions/f7ff7f175678_add_quality_score_model.py`
- `tests/codegate/engines/test_quality_engine.py`
- `tests/codegate/api/test_quality_api.py`
- `docs/implementation/GROUP_06_QUALITY_SCORE_REPORT.md`

## 24. Files Modified
- `codegate/database/models/analysis.py` (Added `QualityScore`)
- `codegate/database/models/__init__.py` (Exposed `QualityScore`)
- `codegate/api/routers/analyses.py` (Added endpoints)
- `codegate/services/analysis_orchestrator.py` (Added auto-calculation hook)

## 25. Known Limitations
- Partial score is returned when components lack data, which is explicitly noted in `is_complete=False`.
- SQLite doesn't natively support `Decimal`, so `Float` is used with 2-decimal rounding.
- PR Detail Summary logic is deferred to avoid polluting PR query objects until frontend consumes it.

## 26. Group Verdict

```text
QUALITY ENGINE:               PASS
DETERMINISTIC:                PASS
EXPLAINABILITY:               PASS
CHANGED-CODE SCORING:         PASS
PARTIAL SCORE HANDLING:       PASS
MISSING DATA SAFETY:          PASS
GRADE BOUNDARIES:             PASS
QUALITY PERSISTENCE:          PASS
QUALITY API:                  PASS
AUTOMATIC CALCULATION:        PASS
MIGRATION:                    PASS
FRESH DB MIGRATION:           PASS

CODEGATE TESTS:
  TOTAL:   46
  PASSED:  46
  FAILED:  0
  SKIPPED: 0

PR-AGENT REGRESSION:          UNCHANGED
NEW UPSTREAM FAILURES:        0

READY FOR GROUP 07:           YES
```
