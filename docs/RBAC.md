# Role-Based Access Control (RBAC)

CodeGate implements strict multi-tenancy and RBAC around the concept of a **Workspace** (Team).

A user can belong to multiple workspaces, but actions are strictly scoped to their `active_workspace_id`.

## Roles

CodeGate defines four primary roles within a Workspace:

1. **ADMIN**: Full control over the workspace, billing (if applicable), and member management.
2. **MAINTAINER**: Can configure repositories, policies, and GitHub connections, but cannot manage admins.
3. **REVIEWER**: Can view all analyses, override policy blocks (if allowed), and configure notification settings.
4. **DEVELOPER**: Read-only access to PR analyses and dashboard metrics.

## Permissions Matrix

| Permission Area | ADMIN | MAINTAINER | REVIEWER | DEVELOPER |
|---|:---:|:---:|:---:|:---:|
| **Workspace Settings** | ✅ | ❌ | ❌ | ❌ |
| **Delete Workspace** | ✅ | ❌ | ❌ | ❌ |
| **Manage Members/Invites** | ✅ | ✅* | ❌ | ❌ |
| **Manage GitHub Connection** | ✅ | ✅ | ❌ | ❌ |
| **Sync Repositories** | ✅ | ✅ | ❌ | ❌ |
| **Configure Repo Tests** | ✅ | ✅ | ❌ | ❌ |
| **Configure Policy Gates** | ✅ | ✅ | ❌ | ❌ |
| **View Dashboards/Analytics** | ✅ | ✅ | ✅ | ✅ |
| **View PR Analyses** | ✅ | ✅ | ✅ | ✅ |
| **Override Policy Blocks** | ✅ | ✅ | ✅ | ❌ |

*\* Note: Maintainers can invite users and manage roles up to the Maintainer level. They cannot grant the ADMIN role.*

## Tenant Isolation

- **IDOR Protection**: Every API endpoint that fetches a resource (Repository, PR, Analysis) verifies that the resource belongs to the user's `active_workspace_id`.
- **Last-Admin Protection**: The system prevents the removal or role-downgrade of the last remaining Admin in a workspace.
- **Data Boundaries**: A `Repository` is owned by a `GitHubConnection`, which is owned by a `Workspace`. PRs and Analyses are children of the Repository. Cross-workspace data leakage is prevented at the SQLAlchemy query level.
