# CodeGate frontend audit

Audit date: 2026-09-26. Sources: every runtime file under `src`, backend response schemas (read only), Chrome DevTools against the existing local app. No production fixtures or seeded data were added.

## Route inventory

API paths below are relative to `/api/v1`. All authenticated pages also use GET `/auth/me`, `/workspaces`, and `/system/status` through the existing shell/context.

| Route | Page / purpose | API | Main data | Primary action | Secondary actions | Observed UX problems |
| --- | --- | --- | --- | --- | --- | --- |
| `/` | Entry redirect | None | Auth state | Redirect to dashboard | None | Preserved |
| `/dashboard` | Workspace overview | GET `/dashboard/overview` | KPIs, daily history, distributions | Refresh | Chart tooltips | Oversized hero; inert date/repository filters; seven pastel cards; duplicated metrics; missing trend values converted to zero |
| `/repositories` | Repository health list | GET `/dashboard/repositories` | Access, scores, test rate, sync time | Open repository | Refresh | Wide table clips; provider badges add noise; no next action for empty state |
| `/repositories/:repositoryId` | Repository evidence/settings | GET `/dashboard/repositories/:id`, GET/PUT `/repositories/:id/testing` | Health, policy counts, recent PRs, testing configuration | Open PR | Edit/save testing according to existing role permissions | Dark form on light page; nested metric cards; little evidence context |
| `/pull-requests` | Review queue | GET `/dashboard/pull-requests` | Latest analysis, scores, policy, tests, findings | Open PR | Search title/author/repository; refresh | Large search card; clipping; no analysis shown as zero findings |
| `/pull-requests/:pullRequestId` | Analysis evidence | GET `/dashboard/pull-requests/:id`, POST `/analyses/:id/retry` | Analysis, quality/risk breakdown, policy, tests, coverage, findings, reviewers | Retry terminal analysis | Inspect evidence | Confirmed wrong field names; `undefined failed`; missing dimensions hidden; empty findings implies clean |
| `/analytics` | Historical analytics | GET `/dashboard/overview` | Same real aggregate/history data | Refresh | Chart inspection | No charts despite available history; duplicated score cards; inert filters |
| `/integrations` | Available connected services | GET `/system/status` | GitHub system status | Open GitHub integration | None | Request aborted by concurrent shell request; rendered Unknown; card is sparse |
| `/integrations/github` | GitHub installations | GET `/integrations/github/connections`, GET `/integrations/github/install`, POST `/integrations/github/connections/:id/sync`, POST `…/:id/disconnect` | Installed accounts, access scope, sync status/time | Connect GitHub | Refresh, sync, manage on GitHub, disconnect confirmation | Separate table/button styling; undefined status tokens; horizontal overflow |
| `/settings/members` | Workspace permissions | GET `/workspaces/active/members`, POST/DELETE `/workspaces/active/invitations[/:id]`, PATCH/DELETE `/workspaces/active/members/:id` | Members, roles, pending invites | Invite teammate | Change role, remove, revoke, copy invite | Modal has no dialog semantics/focus trap; unlabeled controls; excessive weights |
| `/login` | OAuth entry | GET `/auth/github/login` via existing redirect | Authentication state | Continue with GitHub | Authenticated redirect | Glass/gradient styling; authenticated visit correctly redirects |
| `/onboarding` | First workspace | POST `/workspaces` | Workspace name, submission state | Create workspace | Existing auth/workspace redirects | Same oversized auth styling; authenticated existing member redirects |
| `/invite/:token` | Invitation acceptance | GET `/invitations/:token`, POST `…/accept` | Inviter, workspace, role | Accept / log in | Dashboard on invalid invite | Nested cards, nested link/button; error state verified with invalid token |

## Existing mismatches and constraints

- PR detail backend fields: `analysis.analysis_id`, `risk.overall_risk`, `risk.risk_level`, `tests.total/passed/failed/errors/skipped`, `coverage.line_coverage/changed_line_coverage`. The previous frontend used different names. Fix presentation bindings only; retain endpoint/method/payload and retry eligibility.
- Overview test pass rate is currently returned as 0 with zero passed/failed runs. Display the supplied value with its zero-run context, never infer successful testing.
- System status is typed differently in the API client from its actual nested response. Leave client contract unchanged; presentation consumes the current runtime shape.
- Shared API request cancellation means simultaneous shell/integration status requests cancel each other. Reuse shell status in the integration presentation; preserve authentication and request implementation.
- List endpoints default to 20 records and do not expose a total in their array response. Do not imply loaded rows represent every repository/PR or invent pagination totals.
- Login/onboarding form states require an unauthenticated or new-workspace session; the current live account redirects to dashboard. Verify these states with isolated frontend tests, without logging out the user's session or creating workspaces.
- An invalid invitation returns 404 as expected. No valid invitation was created during audit.

## Design decision

Light engineering workspace, navy navigation, blue actions, green pass/success, amber warning, red block/failure, neutral unknown. System font stack, 30px page headings, 18px section headings, 14px body, 13px tables, tabular numeric metrics. 4/8/12/16/24/32 spacing; 6px controls and 8px surfaces. Density 8, variance 3, motion 2. Reuse existing primitives, installed Recharts, and native controls; no new dependencies. Shadcn MCP table/button registry inspected; no `components.json` or Radix dependency exists, so no wholesale framework migration.
