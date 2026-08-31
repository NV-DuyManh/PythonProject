# CodeGate: Final Security Checklist

*Perform this checklist before sharing the project source code, packaging a ZIP for academic submission, or pushing to a public repository.*

- [ ] **`.env` files**: Ensure no `.env` file containing real values exists in the root directory. Only `.env.example` should be shared.
- [ ] **`.secrets.toml`**: Verify that `pr_agent/settings/.secrets.toml` and `pr_agent/settings_prod/.secrets.toml` are NOT tracked by Git.
- [ ] **GitHub App Keys (`.pem`)**: Ensure no `*.pem` file has been committed anywhere in the repository.
- [ ] **Groq Keys**: Search the codebase to ensure no developer temporarily hardcoded `GROQ_API_KEY = "gsk_..."`.
- [ ] **GitHub Tokens**: Ensure no personal access tokens (`ghp_...`) exist in tests or configurations.
- [ ] **Webhook Secrets**: Verify the HMAC webhook secret is passed via environment variables, not hardcoded.
- [ ] **Local Production Credentials**: Ensure `compose.codegate.yml` uses dummy passwords (e.g., `postgres`) or explicitly relies on `.env` overrides, and that you have not committed your real database password.
- [ ] **Screenshot Safety**: Verify that all images in `docs/images/final/` do not accidentally display active terminal tokens, browser console API keys, or internal private repository names that you do not have permission to share.
- [ ] **Git History**: Ensure `gitleaks` passes on the entire branch history. If a secret was committed and then removed, you MUST rewrite the git history (e.g., using `git filter-repo`) before publishing.
