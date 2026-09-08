# Authentication & Session Management

CodeGate delegates user authentication exclusively to **GitHub OAuth**. There is no local password storage.

## GitHub OAuth Flow

1. **Login Initiation**: User clicks "Login with GitHub" on the frontend.
2. **Redirect**: Backend generates an OAuth `state` token (stored temporarily in Redis to prevent CSRF) and redirects the user to GitHub.
3. **Authorization**: User authorizes the CodeGate OAuth App on GitHub.
4. **Callback**: GitHub redirects the user back to the CodeGate Backend (`/api/v1/auth/github/callback`) with a temporary code.
5. **Token Exchange**: Backend exchanges the code for a GitHub Access Token.
6. **User Sync**: Backend fetches the user's GitHub profile, creates or updates the `User` record in PostgreSQL.

## Session Management

Instead of handing the raw GitHub token to the frontend, CodeGate creates a secure, opaque session.

1. **Session Hash**: Backend generates a cryptographically secure session string.
2. **Cookie**: The session string is set as an `HttpOnly`, `SameSite=Lax` cookie on the user's browser. 
3. **TTL**: Sessions are valid for 7 days by default.

### Local vs Production Cookies

- In local development (`http://127.0.0.1`), the `Secure` flag on the cookie is disabled to allow HTTP transmission.
- In production (if deployed behind HTTPS), the `Secure` flag is strictly enforced.

## Logout & Revocation

- When a user logs out, the backend invalidates the session hash in Redis/Database and instructs the browser to clear the cookie.
- The underlying GitHub Access Token is discarded; CodeGate does not store user-level OAuth tokens persistently unless required for specific background syncs (which use GitHub App Installation tokens instead).
