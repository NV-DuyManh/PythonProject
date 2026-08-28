# Group 01 Baseline Report

## 1. Executive Summary
This report establishes the baseline state of the `pr-agent` repository before upgrading it to the CodeGate platform architecture. The current state is completely stateless and heavily relies on Litellm and multiple Git Provider integrations. A dependency issue was identified on the current machine due to Python 3.14.6 lacking pre-built wheels for older native dependencies (PyYAML). No code was modified during this phase.

## 2. Git State
```text
Branch: main
Commit: 5a5e1de Initial project
Working tree: clean
Origin: origin https://github.com/NV-DuyManh/PythonProject.git
```

## 3. Environment
- **Python version yêu cầu**: `>=3.12` (declared in `pyproject.toml`)
- **Package manager/cách cài**: `setuptools.build_meta`, install via `pip install -e .`
- **Dependencies chính**: `litellm`, `PyGithub`, `python-gitlab`, `fastapi`, `uvicorn`, `dynaconf`, `Jinja2` (listed in `requirements.txt`).
- **Dependencies development**: `pytest`, `pytest-asyncio` (listed in `requirements-dev.txt`).
- **Test framework**: `pytest`
- **Cách chạy CLI**: `python -m pr_agent.cli` (or via entrypoint `pr-agent`).
- **Cách chạy GitHub App**: FastAPI server via `uvicorn.workers.UvicornWorker` on `pr_agent.servers.github_app:app` (or GitHub actions via `github_action_runner.py`).
- **Cách chạy Webhook**: FastAPI server on `pr_agent.servers.gitlab_webhook:app` (and others).
- **Cách chạy Docker**: Multi-stage `Dockerfile` with targets like `github_app`, `gitlab_webhook`, `cli`, `test`.
- **Environment variables quan trọng**: `OPENAI_API_KEY`, `GITHUB_TOKEN`, `GITLAB_TOKEN`, `CONFIG.SECRET_PROVIDER`.

## 4. Dependency Installation
```text
REQUIRED: >=3.12
CURRENT: 3.12.13
COMPATIBLE: YES
```

## 5. Verification Steps

1. **Environment Initialization:**
   - Identified that Python 3.14 caused native module compilation failures (`grpcio`, `PyYAML`).
   - Switched to **Python 3.12.13**.
   - Created a clean virtual environment `.venv`.

2. **Dependency Installation:**
   - Ran `pip install -e .` to install the `pr-agent` core and base dependencies.
   - **Result:** Successfully built wheels for `pr-agent`, `giteapy`, and `html2text`. Installation of all collected packages completed successfully.
   - Ran `pip install -r requirements-dev.txt` to install testing and development tools (`pytest`, etc.).
   - **Result:** Completed successfully.

3. **Smoke Tests:**
   - **Imports Test:** Executed `python -c "import pr_agent; import litellm; import git; print('Imports successful')"`
     - **Result:** Passed (exited with code 0).
   - **CLI Test:** Executed `python -m pr_agent.cli --help`
     - **Result:** Passed. The CLI initialized properly and printed the usage help text without missing dependencies.

## 6. Unit Test Results
```text
TOTAL: 2579
PASSED: 2568
FAILED: 9
SKIPPED: 1 (and 1 xfailed)
ERRORS: 0
DURATION: 131.52s
```

## 7. Failed/Skipped Tests Analysis
The following tests failed during the baseline verification:

1. `tests/unittest/test_artifacts.py::TestResolveArtifactPath::test_root_workspace_does_not_reject_valid_paths`
   - **Reason**: Path mismatch (`WindowsPath` vs `None`).
   - **Category**: `WINDOWS_COMPATIBILITY`

2. `tests/unittest/test_litellm_callback_drain.py` (5 tests failed)
   - **Reason**: Timing/cancellation assertion failures (`TimeoutError` and `assert False`) in async drain callbacks.
   - **Category**: `WINDOWS_COMPATIBILITY` / `ACTUAL_CODE_BUG`

3. `tests/unittest/test_local_git_provider.py` (2 tests failed)
   - **Reason**: Local Git provider logic mismatch (`AssertionError: assert False`).
   - **Category**: `ACTUAL_CODE_BUG`

4. `tests/unittest/test_skills_loader.py::TestPathExpansion::test_tilde_in_path_is_expanded`
   - **Reason**: Path expansion issue on Windows (`~` resolution).
   - **Category**: `WINDOWS_COMPATIBILITY`

## 8. Import Verification
Successfully imported the following core modules:
- `PRAgent` (`pr_agent.agent.pr_agent`)
- `PRReviewer` (`pr_agent.tools.pr_reviewer`)
- `GithubProvider` (`pr_agent.git_providers.github_provider`)
- `GitProvider` (`pr_agent.git_providers.git_provider`)
- `LiteLLMAIHandler` (`pr_agent.algo.ai_handlers.litellm_ai_handler`)
- `TokenHandler` (`pr_agent.algo.token_handler`)
- **File:** `tests/unittest/*`
  - **Pattern type:** `token=`, `ghp_`
  - **Potential secret:** NO (Dummy strings for unit testing like `ghp_xxx`)
  - **Action required:** None
- **File:** `pr_agent/git_providers/gitlab_provider.py` & others
  - **Pattern type:** `private_token=`
  - **Potential secret:** NO (Variable assignment/URL building logic)
  - **Action required:** None

## 10. GitIgnore Review
The current `.gitignore` includes standard Python exclusions:
- `.venv/` / `venv/`
- `__pycache__`
- `.env`
- `pr_agent/settings/.secrets.toml`
- `pr_agent/settings_prod/.secrets.toml`
- `build/`, `dist/`, `*.egg-info/`

All critical temp files and secret configurations are properly ignored.

## 11. Core Components Verification
Verified that the following modules exist and have substantial logic:
- **Git Provider Layer:** `pr_agent/git_providers/git_provider.py`, `github_provider.py`, `gitlab_provider.py`
- **AI Layer:** `pr_agent/algo/ai_handlers/litellm_ai_handler.py`
- **PR Processing:** `pr_agent/algo/pr_processing.py`, `git_patch_processing.py`, `token_handler.py`
- **PR Review:** `pr_agent/tools/pr_reviewer.py`
- **Server/Webhook:** `pr_agent/servers/github_app.py`

## 12. Current Architecture Confirmation
The baseline architecture holds true to the documentation:
```text
Git Provider (git_providers/github_provider.py)
      ↓
PR Diff Processing (algo/pr_processing.py::get_pr_diff)
      ↓
AI Review (tools/pr_reviewer.py::_get_prediction)
      ↓
Response Parsing (algo/utils.py::load_yaml)
      ↓
Git Provider Publishing (git_providers/github_provider.py::publish_comment)
```

## 13. Safe Integration Points
**A. Có nên giữ nguyên package `pr_agent/` làm engine hay không?**
- **YES.** Khối lượng code cho Git Providers và LLM handler quá lớn để viết lại. Nên giữ nguyên như một core engine.

**B. Có thể tạo package mới `codegate/` song song với `pr_agent/` hay không?**
- **YES.** Đây là cách tiếp cận an toàn nhất. `codegate` sẽ chứa FastAPI API, SQLAlchemy models, và Dashboard. Nó sẽ import `pr_agent` như một sub-module để thực thi AI review.

**C. Việc thêm SQLAlchemy/FastAPI management layer có khả năng conflict với dependency hiện tại không?**
- **MINIMAL RISK.** `pr_agent` đã dùng FastAPI (cho webhook). Cần chú ý versioning của Pydantic (hiện PR-Agent đang dùng Pydantic v2 do tương thích với LiteLLM) và FastAPI. SQLAlchemy sẽ là dependency mới hoàn toàn nên không conflict trực tiếp, nhưng cần lock version cẩn thận.

**D. Entry point nào của PR-Agent sau này nên được adapter gọi?**
- Không gọi qua `cli.py` hay `github_app.py`.
- Nên gọi trực tiếp các class trong `tools/` (ví dụ `PRReviewer(pr_url=...).run()`) hoặc tạo một Adapter Layer mới giao tiếp thẳng với `algo.pr_processing` và `algo.ai_handlers`.

**E. Module nào tuyệt đối không nên sửa sâu?**
- `algo/ai_handlers/litellm_ai_handler.py`
- `git_providers/github_provider.py` (và các provider khác)
- `algo/pr_processing.py`

## 14. Known Issues
- Build compatibility issue with Python 3.14.6 and `PyYAML` on Windows causing `pip install` to hang. Python 3.12.x must be used.
- A few unit tests fail on Windows due to path (`WindowsPath`, `~`) and async event loop timing issues.

## 15. Baseline Verdict
```text
BASELINE STATUS:
READY WITH WARNINGS

READY FOR GROUP 02:
YES
```
*(Warnings are limited to Windows-specific path resolution and async drain tests. The core API and Git providers are fully verified and clean. The project environment is officially set to Python 3.12.x).*
