# GitHub App Setup Guide

CodeGate requires a GitHub App to receive Pull Request webhooks, read source code, and publish CodeGate Checks back to GitHub.

This guide walks you through creating and configuring the GitHub App.

> [!NOTE]
> CodeGate uses **one** global GitHub App installation. You install this single App into multiple GitHub organizations or repositories and link them via the CodeGate Dashboard.

## Step 1: Create the GitHub App

1. Go to your GitHub profile settings (or Organization settings).
2. Navigate to **Developer settings** -> **GitHub Apps** -> **New GitHub App**.
3. Fill out the basic information:
   - **GitHub App name**: `CodeGate Local` (or your preferred name)
   - **Homepage URL**: `http://127.0.0.1:5173`
   - **Webhook URL**: `http://your-public-ip-or-tunnel/api/v1/github/webhook` 
     *(Note: If testing locally, you must use a tunneling service like ngrok, Cloudflare Tunnels, or smee.io, because GitHub cannot reach `127.0.0.1`)*
   - **Webhook secret**: Create a secure random string (save this, you will need it for `.env`).

## Step 2: Set Repository Permissions

The GitHub App requires the following permissions to function correctly:

| Category | Permission | Reason |
|---|---|---|
| **Commit statuses** | Read and write | To post pending/success/failure statuses on PRs. |
| **Contents** | Read-only | To read the repository files and calculate risk scores. |
| **Issues** | Read and write | To post comments on PRs. |
| **Metadata** | Read-only | Mandatory for all GitHub Apps. |
| **Pull requests** | Read and write | To read diffs and post review comments. |

## Step 3: Subscribe to Events

Under the **Subscribe to events** section, check the following:
- `Pull request`
- `Pull request review`
- `Pull request review comment`
- `Issue comment`

## Step 4: Generate a Private Key

1. Save the App.
2. On the App's settings page, scroll down to **Private keys** and click **Generate a private key**.
3. A `.pem` file will download to your computer.
4. Rename this file to `github-app-key.pem`.
5. Move this file into your CodeGate directory at: `secrets/github-app-key.pem`.

## Step 5: Update Your Environment

Open your `.env` file and update the following variables using the information from your GitHub App settings page:

```env
GITHUB_APP_ID=123456
GITHUB_APP_SLUG=your-app-slug
GITHUB_WEBHOOK_SECRET=the-secret-you-created-in-step-1
```

## Step 6: Install the App

1. On the GitHub App settings page, click **Install App** in the left sidebar.
2. Install it on your personal account or organization.
3. Select the repositories you want CodeGate to analyze.

You can now link these repositories to your workspace via the CodeGate dashboard!
