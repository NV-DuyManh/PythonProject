# GROUP 05 — STATIC CODE ANALYSIS ENGINE — ACCEPTANCE REPORT

**Date:** 2026-08-28
**Verification Timestamp:** 22:57–23:08 UTC+7
**Status:** VERIFIED

---

## Architecture Overview

```
codegate/engines/analyzers/
├── __init__.py
├── base.py            — BaseAnalyzer ABC (name, command, supports, parse_output)
├── schemas.py         — NormalizedFinding, NormalizedMetric, AnalyzerResult (Pydantic)
├── runner.py          — StaticAnalysisRunner (orchestrates subprocess, timeout, DB persistence)
├── workspace.py       — AnalyzerWorkspace (git clone, checkout, cleanup)
├── ruff_analyzer.py   — RuffAnalyzer (JSON parsing, severity mapping)
├── bandit_analyzer.py — BanditAnalyzer (JSON parsing, severity mapping)
└── radon_analyzer.py  — RadonAnalyzer (JSON parsing, CodeMetric + Finding generation)
```

Database models in `codegate/database/models/analysis.py`:
- `AnalysisRun` — parent run record, FK to PullRequest
- `Finding` — normalized finding from any source (AI, Ruff, Bandit, Radon)
- `AnalyzerRun` — per-analyzer execution record (status, duration, error)
- `CodeMetric` — per-analyzer metric record (Radon cyclomatic complexity)

---

## 1. ALEMBIC REVISION CHAIN

**Commands executed:**
```
alembic history  → <base> -> 31ea6c57c62c -> 263ae425f3cf (head)
alembic heads    → 263ae425f3cf (head)
```

**Revision chain:**
| Order | Revision       | Description                  |
|-------|----------------|------------------------------|
| 1     | 31ea6c57c62c   | Initial CodeGate schema      |
| 2     | 263ae425f3cf   | Add Group 04 and 05 models   |

**Migration `263ae425f3cf` upgrade creates:**
- `webhook_events` table (with `uq_webhook_delivery` unique constraint)
- `analyzer_runs` table (FK → `analysis_runs.id`, CASCADE)
- `code_metrics` table (FK → `analysis_runs.id`, CASCADE)
- `findings.is_changed_file` column (Boolean, nullable)
- `findings.is_new_code` column (Boolean, nullable)

**Migration `263ae425f3cf` downgrade removes all of the above.**

```
ALEMBIC REVISION CHAIN: PASS
```

---

## 2. FRESH DATABASE MIGRATION

Tested on a fresh empty temporary SQLite database. No `Base.metadata.create_all()` used.

**Upgrade head (rc=0):**
```
Running upgrade  -> 31ea6c57c62c, Initial CodeGate schema
Running upgrade 31ea6c57c62c -> 263ae425f3cf, Add Group 04 and 05 models
```

**Tables after upgrade:**
```
alembic_version, analysis_runs, analyzer_runs, code_metrics, findings,
pull_request_files, pull_requests, repositories, team_members, teams,
users, webhook_events
```

**Schema verification:**
| Item                      | Result  |
|---------------------------|---------|
| analyzer_runs             | EXISTS  |
| code_metrics              | EXISTS  |
| webhook_events            | EXISTS  |
| findings.is_changed_file  | EXISTS  |
| findings.is_new_code      | EXISTS  |

**Downgrade to 31ea6c57c62c (rc=0):**
```
Tables after downgrade: alembic_version, analysis_runs, findings,
pull_request_files, pull_requests, repositories, team_members, teams, users
```
- analyzer_runs: REMOVED ✓
- code_metrics: REMOVED ✓
- webhook_events: REMOVED ✓
- findings.is_changed_file: REMOVED ✓
- findings.is_new_code: REMOVED ✓

**Re-upgrade to head (rc=0):**
All Group 05 tables restored.

```
FRESH DB UPGRADE: PASS
GROUP 05 TABLES/COLUMNS PRESENT: PASS
DOWNGRADE TO PREVIOUS REVISION: PASS
RE-UPGRADE: PASS
```

---

## 3. CODEGATE TEST SUITE

**Command:** `pytest tests/codegate -q`

```
37 passed, 10 warnings in 8.45s
```

```
TOTAL: 37
PASSED: 37
FAILED: 0
SKIPPED: 0
```

---

## 4. GROUP 04 RESTORED TESTS

| Test File                          | Result                    |
|------------------------------------|---------------------------|
| test_hardening_group04_1.py        | 4 passed, 1 warning → PASS |
| test_hardening_group04_2.py        | 1 passed, 1 warning → PASS |
| test_hardening_group04_3.py        | 2 passed, 3 warnings → PASS |
| test_integration_group04.py        | 3 passed, 2 warnings → PASS |

Coverage areas verified:
- monkey patch instance isolation ✓
- original GitHub publish preserved ✓
- normalizer mapping ✓
- analysis lifecycle ✓
- webhook lifecycle ✓
- webhook background processing ✓
- webhook unauthorized ✓
- webhook deduplication ✓

```
GROUP 04 RESTORED TESTS: PASS
```

---

## 5. METRICS API

**Command:** `pytest tests/codegate/api/test_integration_group05.py::test_get_metrics_api -v`

Test stores a `CodeMetric` in DB, then calls `GET /api/v1/analyses/{analysis_id}/metrics`.
- Endpoint returns the persisted value.
- Radon is NOT rerun during GET.
- Response status: 200.

```
METRICS API: PASS
```

---

## 6. STATIC ANALYZERS

### Real Tool Execution

Verified via `verify_group05.py` — creates temp workspace with Python fixture files, invokes `StaticAnalysisRunner` which runs actual Ruff/Bandit/Radon subprocesses:

| Analyzer | Status  | Findings/Metrics |
|----------|---------|------------------|
| Ruff     | SUCCESS | 2 findings (I001 unused import sort, F401 unused import) |
| Bandit   | SUCCESS | 1 finding (B307 eval usage) |
| Radon    | SUCCESS | 3 metrics (cyclomatic_complexity) |

### Analyzer Framework Tests

**Command:** `pytest tests/codegate/engines/test_analyzers.py -v`

| Test                                        | Result |
|---------------------------------------------|--------|
| test_ruff_analyzer                          | PASSED |
| test_bandit_analyzer                        | PASSED |
| test_radon_analyzer                         | PASSED |
| test_analyzer_runner_timeout_and_failure    | PASSED |
| test_workspace_cleanup                      | PASSED |

### Subprocess Safety

**Evidence from `runner.py`:**
- Uses `asyncio.create_subprocess_exec` — NOT `shell=True`
- Commands passed as `List[str]` via `BaseAnalyzer.command` property
- `asyncio.wait_for` with `settings.ANALYZER_TIMEOUT_SECONDS` timeout
- `stdout` and `stderr` captured via `asyncio.subprocess.PIPE`
- `grep -r "shell=True" codegate/engines/` → 0 results

### Workspace Cleanup

**Evidence from `runner.py` lines 148–166:**
- `finally: self.workspace.cleanup()` — always runs
- `workspace.cleanup()` uses `shutil.rmtree` with Windows read-only handler
- Idempotent: guards with `if self.workspace_dir and os.path.exists(...)`

### Failure Isolation

**Evidence from `runner.py` `_run_analyzer()`:**
- `except Exception as e:` catches all exceptions per-analyzer
- Returns `AnalyzerResult(status=Status.FAILED)` — never propagates
- `run_all()` loops over analyzers; one failure does not prevent others

### Timeout Isolation

**Evidence from `runner.py` lines 81–91:**
- `except asyncio.TimeoutError:` caught per-analyzer
- `process.kill()` called immediately
- Returns `AnalyzerResult(status=Status.TIMEOUT)`
- Loop continues to next analyzer

### Changed-Code Metadata

**Evidence from `analysis.py`:**
- `Finding.is_changed_file: Mapped[Optional[bool]]`
- `Finding.is_new_code: Mapped[Optional[bool]]`
- Migration `263ae425f3cf` adds both columns

### Analyzer Run Persistence

**Evidence from `runner.py`:**
- Creates `AnalyzerRun` with `status=Status.RUNNING`, commits
- After execution: updates `status`, `completed_at`, `duration_ms`, `error_message`

### Code Metric Persistence

**Evidence from `runner.py` `_persist_results()`:**
- Creates `CodeMetric` for each metric in result
- Fields: `analysis_run_id`, `analyzer`, `metric_name`, `file_path`, `symbol`, `value`, `grade`

```
REAL RUFF: PASS
REAL BANDIT: PASS
REAL RADON: PASS
SUBPROCESS SAFETY: PASS
WORKSPACE CLEANUP: PASS
FAILURE ISOLATION: PASS
TIMEOUT ISOLATION: PASS
CHANGED-CODE METADATA: PASS
ANALYZER RUN PERSISTENCE: PASS
CODE METRIC PERSISTENCE: PASS
```

---

## 7. PR-AGENT REGRESSION

**Command:** `pytest tests/unittest -q`

```
8 failed, 2569 passed, 1 skipped, 1 xfailed, 89 warnings in 168.48s
```

**All 8 failures are in known baseline families:**

| File                              | Failures |
|-----------------------------------|----------|
| test_artifacts.py                 | 1        |
| test_litellm_callback_drain.py    | 4        |
| test_local_git_provider.py        | 2        |
| test_skills_loader.py             | 1        |

**New failures outside baseline set: 0**

```
PR-AGENT REGRESSION: UNCHANGED
NEW UPSTREAM FAILURES: 0
```

---

## 8. FINAL ACCEPTANCE SUMMARY

```
GROUP 04 FUNCTIONALITY RESTORED:   PASS
ANALYZER FRAMEWORK:                PASS
REAL RUFF:                         PASS
REAL BANDIT:                       PASS
REAL RADON:                        PASS
SUBPROCESS SAFETY:                 PASS
WORKSPACE CLEANUP:                 PASS
FAILURE ISOLATION:                 PASS
TIMEOUT ISOLATION:                 PASS
CHANGED-CODE METADATA:             PASS
ANALYZER RUN PERSISTENCE:          PASS
CODE METRIC PERSISTENCE:           PASS
METRICS API:                       PASS
ALEMBIC REVISION CHAIN:            PASS
FRESH DATABASE MIGRATION:          PASS
DOWNGRADE/RE-UPGRADE:              PASS

CODEGATE TESTS:
  TOTAL:   37
  PASSED:  37
  FAILED:  0
  SKIPPED: 0

PR-AGENT REGRESSION:               UNCHANGED
NEW UPSTREAM FAILURES:             0

READY FOR GROUP 06:                YES
```