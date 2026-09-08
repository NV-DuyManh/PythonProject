# Environment Configuration Guide

This guide details all available environment variables for CodeGate. You can set these variables in your `.env` file or directly in your runtime environment.

## Overview

CodeGate relies on several services (PostgreSQL, Redis, Celery, FastAPI, React). The configuration manages the connections between these services, external AI providers, and GitHub integrations.

> [!IMPORTANT]
> Never commit real secrets or API keys to version control. Always use the `.env` file, which is ignored by `.gitignore`.

---

## Configuration Variables

| VARIABLE | REQUIRED? | SECRET? | USED BY | EXAMPLE FORMAT | DESCRIPTION | DEFAULT |
|---|:---:|:---:|---|---|---|---|
| **Database & Queue** | | | | | | |
| `POSTGRES_DB` | No | No | PostgreSQL | `codegate` | Name of the PostgreSQL database. | `codegate` |
| `POSTGRES_USER` | No | No | PostgreSQL | `codegate` | Database username. | `codegate` |
| `POSTGRES_PASSWORD` | No | Yes | PostgreSQL | `super_secret_pw` | Database password. | `postgres` |
| `DATABASE_URL` | No | Yes | Backend, Worker | `postgresql+psycopg2://u:p@host/db` | Full SQLAlchemy connection string. | `postgresql+psycopg2://codegate:postgres@postgres:5432/codegate` |
| `CELERY_BROKER_URL` | No | No | Backend, Worker | `redis://redis:6379/0` | Connection string for the Redis broker. | `redis://redis:6379/0` |
| **AI Providers** | | | | | | |
| `GROQ_API_KEY` | Yes* | Yes | Backend, Worker | `gsk_12345...` | Groq API key for fast LLM inference. | None |
| `OPENAI_API_KEY` | No | Yes | Backend, Worker | `sk-12345...` | OpenAI API key for fallback models. | None |
| `CONFIG.MODEL` | No | No | Backend, Worker | `groq/openai/gpt-oss-120b` | The primary LLM to use. | `groq/openai/gpt-oss-120b` |
| **GitHub OAuth** | | | | | | |
| `GITHUB_OAUTH_CLIENT_ID` | Yes | No | Backend | `Iv1.abc123def456` | Client ID from GitHub OAuth App. | None |
| `GITHUB_OAUTH_CLIENT_SECRET` | Yes | Yes | Backend | `abc123def456...` | Client Secret from GitHub OAuth App. | None |
| `GITHUB_OAUTH_CALLBACK_URL` | Yes | No | Backend | `http://127.0.0.1:8000/...` | Full URL for the OAuth callback route. | `http://127.0.0.1:8000/api/v1/auth/github/callback` |
| **GitHub App** | | | | | | |
| `GITHUB_APP_ID` | Yes | No | Backend, Worker | `123456` | ID of your registered GitHub App. | None |
| `GITHUB_APP_SLUG` | Yes | No | Backend, Worker | `my-codegate-app` | URL slug of your GitHub App. | None |
| `GITHUB_WEBHOOK_SECRET` | Yes | Yes | Backend | `my_webhook_secret` | Secret used to verify GitHub webhook signatures. | None |
| `GITHUB_APP_PRIVATE_KEY_PATH` | No | No | Backend, Worker | `/run/secrets/key.pem` | Path inside the container to the PEM file. | `/run/secrets/github-app-key.pem` |
| **API & Frontend** | | | | | | |
| `CORS_ALLOW_ORIGINS` | No | No | Backend | `http://127.0.0.1:5173` | Comma-separated list of allowed CORS origins. | `http://127.0.0.1:5173,http://localhost:5173` |
| `VITE_CODEGATE_API_URL` | No | No | Frontend | `http://127.0.0.1:8000/api/v1` | URL where the frontend expects the backend API. | `http://127.0.0.1:8000/api/v1` |

*\* Note: Either `GROQ_API_KEY` or `OPENAI_API_KEY` is required for the AI Review capabilities.*

## Secret Management

CodeGate uses Docker Secrets or mounted files for sensitive files that shouldn't be passed via environment variables (like the GitHub App Private Key). 

By default, `compose.codegate.yml` expects the `.pem` file to be located at `./secrets/github-app-key.pem` on your host machine, which it mounts to `/run/secrets/github-app-key.pem` inside the backend and worker containers.
