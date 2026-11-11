# ADR 0009: Session model — server-side sessions for browsers, PATs for programs

- Status: Accepted
- Date: 2026-11-11
- Deciders: project lead (orchestrator), on the architect's recommendation
- Related: `docs/architecture/auth.md` §2.3, PRD FR-10.8

## Context

Server mode needs an authenticated request model for two very different clients:

1. **Browsers** using the Next.js frontend (ADR 0008), which need login, logout, "log me
   out of that other device", and immediate invalidation when a password changes.
2. **Programs** — `rc login` against a server, CI jobs, and third-party tools — which
   need long-lived, scriptable credentials.

PRD FR-10.8 allows either server-side sessions or short-lived tokens with refresh, and
leaves the choice to the design.

## Decision

- **Browsers: server-side sessions.** An opaque session id in a cookie
  (`HttpOnly; Secure; SameSite=Lax`, 14-day sliding expiry). Session records live in
  PostgreSQL (`sessions_auth`) behind a `SessionStore` interface so Redis can replace it
  later. CSRF is handled by `SameSite=Lax` plus a double-submit `X-CSRF-Token` header on
  state-changing requests.
- **Programs: personal access tokens (PATs).** 32 random bytes sent as
  `Authorization: Bearer`, stored only as a hash, with scopes (`read:progress`,
  `write:progress`, `admin`) and an optional expiry. Users create and revoke them from
  the profile screen or `rc login`.
- **JWT: deferred.** No JWTs are issued for first-party clients. If service-to-service
  calls appear, short-lived (15 min) JWTs from an OIDC client-credentials grant may be
  introduced for that traffic only.

The API server stays stateless in the process sense: all session state is in the
database, so replicas scale horizontally.

## Rationale

- **Revocation is the hard requirement.** Logout, password change, admin force-logout,
  and the per-device session list (FR-10.8) all need a credential that can be destroyed
  server-side. Opaque sessions give this by deleting a row.
- **JWT would reintroduce the same state.** Making JWTs revocable requires a
  server-side blocklist checked on every request, which costs the same lookup as a
  session table while adding key rotation, clock skew and token-size concerns.
- **No token in JavaScript.** An `HttpOnly` cookie is not reachable from page scripts, so
  an XSS bug cannot exfiltrate a long-lived credential.
- **Different lifetimes for different clients.** Browser sessions should expire and
  slide; automation credentials should be explicit, named, scoped and auditable. One
  mechanism cannot be good at both.

## Consequences

- Every authenticated request does one indexed lookup in `sessions_auth`. At the PRD's
  500-concurrent-user target this is negligible; if it ever is not, the `SessionStore`
  interface allows moving to Redis without touching call sites.
- The frontend must send the CSRF header on mutations and handle 401 by redirecting to
  `/login`.
- PAT plaintext is shown exactly once at creation; the UI and `rc login` must make that
  clear.
- Cross-origin browser clients are not supported by default: the cookie is scoped to the
  app origin. A separate public API consumer uses a PAT.
- Session creation, logout, forced logout and PAT issuance/revocation are audit-logged.
