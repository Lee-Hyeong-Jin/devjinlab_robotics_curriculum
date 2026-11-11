# Role matrix (AC-AUTH.4)

Server mode (`RC_AUTH_MODE=server`). Roles nest: `learner < author < admin`. "PAT scope" is what a
personal access token additionally needs; browser sessions carry every scope their role allows
but must send `X-CSRF-Token` on non-GET requests. Tested by `tests/test_auth.py::test_role_matrix`
and the scope/CSRF tests next to it.

| Endpoint | anonymous | learner | author | admin | PAT scope |
|---|---|---|---|---|---|
| `GET /healthz`, `/readyz`, `/version` | 200 | 200 | 200 | 200 | — |
| `POST /api/v1/auth/signup`, `/login`, `/verify-email`, `/password/forgot`, `/password/reset` | ✔ | ✔ | ✔ | ✔ | — |
| `GET /api/v1/auth/oidc/{provider}/start`, `/callback` (302) | ✔ | ✔ (links) | ✔ (links) | ✔ (links) | — |
| `POST /api/v1/auth/logout` | 401 | ✔ | ✔ | ✔ | session |
| `GET /metrics` (internal network only) | 200 | 200 | 200 | 200 | — |
| `GET /api/v1/courses`, `/modules/*`, `/lessons/*`, `/resources` | 401 | ✔ | ✔ | ✔ | `read:progress` |
| `GET /api/v1/progress/*`, `/reports/*` (own data only) | 401 | ✔ | ✔ | ✔ | `read:progress` |
| `POST /api/v1/progress/start|stop|log|done` (own data only) | 401 | ✔ | ✔ | ✔ | `write:progress` |
| `GET /api/v1/me`, `/me/export` | 401 | ✔ | ✔ | ✔ | `read:progress` |
| `PATCH /api/v1/me`, `PUT /me/password`, `GET|DELETE /me/sessions*`, `GET|POST|DELETE /me/tokens*`, `GET|DELETE /me/identities*`, `DELETE /me` | 401 | ✔ | ✔ | ✔ | not allowed (session only) |
| `GET /api/v1/admin/users`, `/admin/users/{id}`, `/admin/audit` | 401 | 403 | 403 | ✔ | `admin` |
| `PATCH /api/v1/admin/users/{id}`, `DELETE /admin/users/{id}/sessions` | 401 | 403 | 403 | ✔ | `admin` (+`write:progress` for the method check) |

Rules enforced on top of the table:

- Learning data is always read and written for the authenticated user; no endpoint takes a `user_id`.
  Another user's session or token id answers 404.
- An admin cannot remove their own admin access; the last active admin cannot be demoted, disabled or
  deleted (409). A demotion takes effect on the next request.
- Only admins can mint tokens with the `admin` scope. Disabling a user ends their sessions and tokens.
- Author-only content actions (reindex, publish) arrive with the content-reindex work (AC-API.6).

Local mode (default) has no accounts: every request acts as user 1 and the `/auth` and account
endpoints answer 404.
