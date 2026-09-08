# Async Pipeline Documentation

CodeGate's analysis pipeline takes significant time (often 1-3 minutes depending on the AI provider and test suite size). Therefore, it cannot block the FastAPI web server. CodeGate uses **Redis** and **Celery** to handle this asynchronously.

## Infrastructure

- **Broker:** Redis 7 (acts as the message queue).
- **Worker:** Celery (configured with a concurrency of 2 by default).

## Full PR Analysis Flow

1. **Developer** opens a Pull Request on GitHub.
2. **GitHub** fires a Webhook to the CodeGate `FastAPI` endpoint.
3. **FastAPI** verifies the webhook signature, identifies the `Repository`, and creates a `PullRequest` record in PostgreSQL.
4. **FastAPI** creates an `AnalysisRun` and an `AnalysisJob` record, setting the state to `QUEUED`.
5. **FastAPI** enqueues the job ID into **Redis** via Celery's `delay()` method, and immediately returns a `200 OK` to GitHub.
6. **Celery Worker** picks up the job from Redis and updates the state to `RUNNING`.
7. **Worker** executes the engines in sequence:
   - **AI Review**
   - **Static Analysis**
   - **Tests / Coverage**
8. **Worker** normalizes the results and computes the **Quality Score** and **Risk Score**.
9. **Worker** evaluates the results against the **Merge Policy** (PASS, WARNING, BLOCK).
10. **Worker** generates a **Reviewer Recommendation**.
11. **Worker** saves all findings to **PostgreSQL**.
12. **Worker** publishes a **GitHub Check** back to the PR with the final status and a comment containing the summary.
13. **Dashboard** displays the results (users can view them immediately by navigating to the UI).

## Job States

An `AnalysisJob` transitions through the following states:

- `QUEUED`: Job is in Redis waiting for a worker.
- `RUNNING`: Worker is actively processing the job.
- `SUCCEEDED`: Analysis completed successfully.
- `FAILED`: Analysis encountered an unrecoverable error.
- `RETRYING`: Analysis failed transiently (e.g., API timeout) and will be retried.
- `SKIPPED`: The PR was updated with a newer commit (stale SHA protection), so this older job is skipped.

## Stale SHA Protection

If a developer pushes a new commit to a PR while an analysis is already `QUEUED` or `RUNNING`, CodeGate detects the SHA mismatch. It will safely `SKIP` the older analysis to save API credits and compute resources, prioritizing the latest commit.
