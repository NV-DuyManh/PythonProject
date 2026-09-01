# CodeGate GitHub App Setup Guide (Product / Operator)

To run a multi-tenant, dynamic CodeGate instance, you must configure **one central GitHub App**. This App will serve all Workspaces and Users. No customer needs to create their own GitHub App.

## 1. Registering the GitHub App
Navigate to your GitHub account or Organization settings:
**Settings > Developer Settings > GitHub Apps > New GitHub App**

## 2. Basic Configuration
- **GitHub App name:** `codegate-production` (or your chosen brand name)
- **Homepage URL:** The public URL of your CodeGate instance (e.g., `https://codegate.mycompany.com`)
- **Callback URL:** `https://codegate.mycompany.com/api/v1/integrations/github/setup`
- **Setup URL:** `https://codegate.mycompany.com/api/v1/integrations/github/setup`
- **Webhook URL:** `https://codegate.mycompany.com/api/v1/github_webhooks`

## 3. Permissions
Under **Repository Permissions**, grant:
- **Pull requests:** Read & Write (for inline comments and reviews)
- **Contents:** Read-only (to analyze source code)
- **Metadata:** Read-only

## 4. Subscribe to Events
Under **Subscribe to events**, select:
- **Pull request**
- **Pull request review**
- **Push**

## 5. Private Key and Secrets
1. **Generate a Private Key**: Download the `.pem` file and store it securely on your server (e.g., `/etc/codegate/github-app.pem`).
2. **Webhook Secret**: Generate a random secure string for webhook validation.

## 6. Server Environment Configuration
Configure your backend server `.env`:
```env
GITHUB_APP_ID=123456
GITHUB_APP_SLUG=codegate-production
GITHUB_APP_PRIVATE_KEY_PATH=/etc/codegate/github-app.pem
GITHUB_WEBHOOK_SECRET=your_secure_random_string
```

*Note: No OAuth Client ID/Secret or Personal Access Tokens (PATs) are needed for this flow.*
