# OWASP ASVS 4.0.3 Level 2 — V2, V3, V4 checklist (AC-AUTH.8)

Scope: server mode of the API (`RC_AUTH_MODE=server`), P2-2 first increment. Status: **pass** (implemented
and tested), **n/a** (feature not offered), **later** (planned, with milestone). Evidence points at code or
tests. Re-check every release (`docs/architecture/auth.md` §7).

## V2 Authentication

| ID | Requirement (short) | Status | Evidence |
|---|---|---|---|
| 2.1.1 | Passwords ≥ 12 characters | pass | `auth/crypto.py` `check_policy`; `test_password_policy` |
| 2.1.2 | Passwords up to ≥ 64 (we allow 128) | pass | `MAX_PASSWORD = 128` |
| 2.1.3 | No truncation | pass | whole password (+pepper) hashed |
| 2.1.4 | Any Unicode allowed | pass | no character-class rules |
| 2.1.5 | Users can change their password | pass | `PUT /api/v1/me/password`; `test_profile_and_password_change` |
| 2.1.6 | Change requires current password | pass | `AuthService.change_password` |
| 2.1.7 | Breached-password check | later | HIBP k-anonymity, optional (auth.md §2.1) |
| 2.1.8 | Strength meter | later | frontend (P2-4) |
| 2.1.9 | No composition rules | pass | only length / no email or name |
| 2.1.10 | No periodic rotation | pass | none |
| 2.1.11 | Paste allowed | later | frontend (P2-4) |
| 2.1.12 | Show/hide password | later | frontend (P2-4) |
| 2.2.1 | Anti-automation (brute force) | pass | 5 failures/account, 20/IP per 15 min → 429; `test_login_failures_are_uniform_and_throttled`, `test_ip_throttle` |
| 2.2.2 | Weak authenticators limited | n/a | no SMS/email OTP login |
| 2.2.3 | Notify on credential changes | later | needs mail templates for change notices |
| 2.3.1 | Initial secrets random, expire | pass | reset/verify tokens 256-bit, 30 min / 24 h |
| 2.4.1 | Passwords stored with approved KDF | pass | Argon2id m=64 MiB t=3 p=4; `test_password_hash_is_argon2id_and_never_logged` |
| 2.4.2 | Salt ≥ 32 bits, unique | pass | argon2-cffi 16-byte salt |
| 2.4.4 | Argon2 parameters documented | pass | ADR 0010, auth.md §2.1; rehash on login when raised |
| 2.4.5 | Pepper (optional) | pass | `RC_AUTH_PEPPER` |
| 2.5.1 | Recovery secret not sent in clear by default | pass | link with one-time token only |
| 2.5.2 | No password hints / secret questions | pass | none |
| 2.5.4 | No shared/default accounts | pass | bootstrap admin only via `RC_AUTH_ADMIN_EMAIL` sign-up |
| 2.5.6 | Forgotten-password uses secure flow | pass | single-use 30-min token, all sessions revoked; `test_password_reset_flow` |
| 2.5.7 | Lost OTP/MFA recovery | n/a | MFA in Phase 3 |
| 2.7.x / 2.8.x | Out-of-band / OTP authenticators | n/a | not offered |
| 2.9.x | Cryptographic authenticators | n/a | not offered |
| 2.10.1–2.10.4 | Service credentials not hard-coded, stored securely | pass | SMTP/DB secrets from environment; PATs hashed |

## V3 Session management

| ID | Requirement (short) | Status | Evidence |
|---|---|---|---|
| 3.1.1 | Session token never in URL | pass | cookie / Authorization header only |
| 3.2.1 | New token on authentication | pass | fresh `sid` per login; `test_session_fixation_is_prevented` |
| 3.2.2 | ≥ 64 bits entropy | pass | 256-bit `secrets.token_urlsafe(32)` |
| 3.2.3 | Stored securely in browser | pass | `HttpOnly; Secure; SameSite=Lax` cookie; `test_login_sets_hardened_cookies` |
| 3.2.4 | Approved generation | pass | `secrets` (CSPRNG) |
| 3.3.1 | Logout invalidates session | pass | `test_logout_revokes_session` |
| 3.3.2 | Idle / absolute timeout | pass | 14 d sliding idle, 30 d absolute; `test_session_idle_sliding_and_absolute_expiry` |
| 3.3.3 | Option to end other sessions after password change | pass | other sessions revoked automatically |
| 3.3.4 | Users can view and log out active sessions | pass | `GET/DELETE /api/v1/me/sessions`; `test_list_and_revoke_own_sessions` |
| 3.4.1 | Cookie `Secure` | pass | `RC_AUTH_COOKIE_SECURE=1` default |
| 3.4.2 | Cookie `HttpOnly` | pass | `sid` |
| 3.4.3 | Cookie `SameSite` | pass | `Lax` |
| 3.4.4 | `__Host-` prefix | later | cookie name `sid` kept for the frontend contract (ADR 0009); revisit with P2-4 |
| 3.4.5 | Cookie path scoped | pass | `Path=/`, same-origin deployment |
| 3.5.1 | Users can revoke OAuth/PAT grants | pass | `DELETE /api/v1/me/tokens/{id}` |
| 3.5.2 | Static API secrets not used for sessions | pass | PATs are per user, scoped, expiring (default 90 d) |
| 3.5.3 | Stateless tokens signed | n/a | no JWTs (ADR 0009) |
| 3.7.1 | Re-auth before sensitive actions | pass | password required for password change and account deletion |

## V4 Access control

| ID | Requirement (short) | Status | Evidence |
|---|---|---|---|
| 4.1.1 | Enforced server-side | pass | FastAPI dependencies `get_principal`, `require_admin`, `require_session` |
| 4.1.2 | Attributes not user-manipulable | pass | role/user id from the session row, never from the request |
| 4.1.3 | Least privilege | pass | default role learner; PAT scopes; tokens cannot manage the account |
| 4.1.5 | Fail securely | pass | missing/invalid credentials → 401, insufficient → 403 (problem+json) |
| 4.2.1 | IDOR protection | pass | queries bound to the caller's `user_id`; foreign session/token ids → 404; `test_progress_is_isolated_between_users` |
| 4.2.2 | CSRF protection | pass | session-bound `X-CSRF-Token`; `test_csrf_required_for_cookie_writes` |
| 4.3.1 | Admin interfaces protected | pass | `/api/v1/admin/*` needs admin role (+`admin` scope for PATs); `test_role_matrix` |
| 4.3.2 | No directory browsing / metadata leaks | pass | JSON API only; errors hide internals |
| 4.3.3 | Additional checks for high-value actions | pass | last-admin and self-demotion guards; audit log for every change |

## Related controls outside V2–V4

- Security headers (V14.4): CSP `default-src 'none'`, `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Permissions-Policy`, HSTS in server mode, `Cache-Control: no-store` on account
  endpoints — `test_security_headers`.
- Logging (V7): JSON logs with request id; passwords never logged — `test_password_hash_is_argon2id_and_never_logged`;
  audit log of logins, logouts, token and role changes, exports, deletions.
