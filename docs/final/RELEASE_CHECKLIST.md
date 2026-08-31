# CodeGate: Final Release Checklist

*Complete this checklist before freezing the project branch for academic defense or tagging a v1.0.0 release.*

## Code Verification
- [ ] **Git Status**: `git status` is clean; no untracked or uncommitted changes.
- [ ] **Secret Scan**: Run `gitleaks detect -v` on the repository; ensure zero blocking secrets.
- [ ] **Backend Tests**: Run `python -m pytest tests/codegate -q`; verify 89/89 passing.
- [ ] **Frontend Tests**: Run `npm run test:run` in `dashboard/`; verify 17/17 passing.
- [ ] **Frontend Build**: Run `npm run build` in `dashboard/`; verify successful Vite bundle generation.

## Infrastructure Verification
- [ ] **Alembic Graph**: Run `alembic heads`; verify exactly 1 linear head exists.
- [ ] **Docker Config**: Run `docker compose -f compose.codegate.yml config`; verify no syntax errors.
- [ ] **Docker Build**: Run `docker compose -f compose.codegate.yml build`; verify both backend and frontend images compile successfully.
- [ ] **Launcher**: Verify `CodeGateLauncher.exe` boots cleanly on Windows without errors.

## Content & Assets
- [ ] **Demo Data**: Verify the local SQLite database (`codegate.db`) contains persisted data for PASS, WARNING, and BLOCK PR scenarios for offline demo usage.
- [ ] **Screenshots**: Verify `docs/images/final/` contains the necessary presentation screenshots.
- [ ] **README Links**: Click all local links in the primary `README.md` to ensure no 404s to missing markdown documents.
- [ ] **Upstream Attribution**: Ensure the README clearly credits PR-Agent and delineates CodeGate's contributions.
- [ ] **License**: Verify the standard license file (`LICENSE`) is present and intact.

## Versioning (Optional)
- [ ] If required for submission, tag the repository with `git tag v1.0.0` to mark the final defense snapshot.
