# 인증·권한 설계 (Authentication & Authorization)

| 항목 | 내용 |
|---|---|
| 버전 | 0.1 (2026-11-11, 설계 문서 v0.4의 §8을 분리) |
| 적용 범위 | 서버 모드(API 서버 + 웹 프론트엔드). 로컬 모드(`rc` CLI + 정적 사이트)는 인증 없이 `user_id=1`로 동작한다 |
| 상위 문서 | `docs/platform-design.md` §1(3계층), §4.4(계정 테이블) |

## 1. 목표와 원칙

1. **계정 하나, 로그인 방법 여럿**: 한 사용자(`users`)가 로컬 비밀번호와 여러 OIDC 제공자(`identities`)를 함께 연결할 수 있다.
2. **진도는 사용자 단위로 완전히 분리**: 모든 학습 테이블에 이미 있는 `user_id`를 인증 컨텍스트에서만 채운다. 요청 본문이나 쿼리 문자열의 `user_id`는 절대 신뢰하지 않는다.
3. **최소 권한**: 기본 역할은 `learner`. 콘텐츠 편집·사용자 관리는 명시적으로 부여된 역할만 가능하다.
4. **감사 가능**: 로그인·권한 변경·콘텐츠 게시·데이터 내보내기/삭제는 `audit_log`에 남긴다.
5. **표준 우선**: 직접 만든 암호 프로토콜 없음. 비밀번호는 Argon2id, 외부 로그인은 OIDC(Authorization Code + PKCE)만 쓴다.

## 2. 계정과 로그인 방식

### 2.1 로컬 계정 (이메일 + 비밀번호)

- 해시: **Argon2id** (`argon2-cffi`), 파라미터 `time_cost=3, memory_cost=64 MiB, parallelism=4`, 솔트 16바이트 자동. 서버 설정의 `PASSWORD_PEPPER`(선택)를 비밀번호 뒤에 붙여 해시한다. 파라미터는 해시 문자열에 포함되므로 나중에 올려도 로그인 시 자동 재해시한다.
- 비밀번호 정책: 12자 이상, 상한 128자, 이메일·이름 포함 금지. 유출 목록 검사는 HIBP k-anonymity API(선택, 설정으로 켬).
- 이메일 인증: 가입 직후 24시간 유효한 일회성 토큰(랜덤 32바이트, DB에는 SHA-256 해시만 저장)을 메일로 보낸다. 인증 전에는 학습 데이터 기록은 가능하되 공개 기능(프로필 공개, 코멘트 등 미래 기능)은 막는다.
- 비밀번호 재설정: 같은 토큰 방식, 1시간 유효, 사용 즉시 폐기, 재설정 시 모든 세션 무효화.
- 로그인 보호: IP·계정별 속도 제한(5회/분), 10회 연속 실패 시 15분 잠금, 실패·잠금은 감사 로그에 기록.
- MFA(TOTP): Phase 3. 테이블 설계만 선반영(`users.mfa_secret_enc`, `users.mfa_enabled`).

### 2.2 OIDC (Google · GitHub · 기관 IdP)

- 라이브러리 `authlib`. 제공자는 설정으로 등록한다: `OIDC_PROVIDERS='[{"id":"google","issuer":"https://accounts.google.com",...},{"id":"github",...},{"id":"univ","issuer":"https://idp.example.ac.kr",...}]'`. GitHub은 OIDC discovery가 없으므로 OAuth2 + `/user`·`/user/emails` 어댑터로 처리한다.
- 흐름: Authorization Code + PKCE, `state`·`nonce` 검증, `id_token` 서명 검증(JWKS 캐시), 이메일은 `email_verified=true`일 때만 신뢰.
- 계정 연결 규칙: `identities(provider, subject)`가 있으면 그 사용자로 로그인. 없고 인증된 이메일이 기존 로컬 계정과 같으면 **자동 연결하지 않고** "기존 계정에 로그인해 연결" 화면으로 보낸다(계정 탈취 방지). 둘 다 없으면 새 사용자 생성.
- 기관 IdP의 `groups`/`roles` 클레임을 역할 매핑에 쓸 수 있다(설정 `OIDC_ROLE_CLAIM_MAP`), 기본은 매핑 없음.

### 2.3 세션 vs JWT — 결정

| 클라이언트 | 방식 | 근거 |
|---|---|---|
| 웹 브라우저 | **서버 측 세션** + 불투명 세션 ID 쿠키 (`HttpOnly; Secure; SameSite=Lax`, 만료 14일 슬라이딩) | 즉시 폐기(로그아웃·비밀번호 변경·관리자 강제 종료)가 필요하고, 브라우저에 토큰을 노출하지 않는다. CSRF는 SameSite + 상태 변경 요청의 `X-CSRF-Token`(더블 서밋) 으로 막는다 |
| 프로그램 클라이언트 (`rc login`, 외부 도구, CI) | **개인 액세스 토큰(PAT)** `Authorization: Bearer` — 랜덤 32바이트, DB에는 해시만, 범위(`read:progress`, `write:progress`, `admin`)와 만료일 지정 | 장기 자동화에 적합하고 폐기가 단순하다. JWT를 쓰면 폐기를 위해 결국 블록리스트가 필요해 이점이 사라진다 |
| 서비스 간 (미래) | OIDC 클라이언트 자격 증명으로 받은 단기 JWT(15분) | 다른 서비스가 생길 때만 도입 |

세션 저장소: PostgreSQL `sessions_auth` 테이블(기본). 트래픽이 커지면 Redis로 교체할 수 있도록 `SessionStore` 인터페이스 뒤에 둔다. API 서버 프로세스는 상태를 갖지 않으므로 수평 확장이 가능하다.

### 2.4 `rc` CLI 의 서버 모드

- `rc login --server https://…` → 브라우저를 열어 로그인한 뒤 PAT를 발급받아 `~/.config/rc/credentials.toml`(0600)에 저장. 브라우저가 없는 환경은 Device Authorization 흐름(RFC 8628)을 Phase 3에 추가.
- 이후 `rc status`·`rc done` 등은 로컬 SQLite 대신 API를 호출한다(`ProgressStore` 구현체 `RemoteProgressStore`). 오프라인이면 로컬 큐에 쌓았다가 동기화(Phase 3).

## 3. 역할과 권한 매트릭스

역할은 `learner` < `author` < `admin` 세 개이며 `users.role` 단일 열에 둔다(PRD 8절 User 엔티티와 동일). 상위 역할은 하위 역할의 권한을 모두 포함한다(admin도 자기 진도를 가진 학습자다).

| 리소스 · 동작 | learner | author | admin |
|---|---|---|---|
| 코스·모듈·레슨·자료 읽기 | ✔ | ✔ | ✔ |
| 자기 진도·세션·카드·복습·퀴즈·노트 CRUD | ✔ (본인만) | ✔ (본인만) | ✔ (본인만) |
| 자기 데이터 내보내기 / 계정 삭제 | ✔ | ✔ | ✔ |
| 타인 진도 읽기 | ✖ | ✖ | 집계만(개인 식별 없음) |
| 콘텐츠 초안 작성·검증(`rc validate`) | ✖ | ✔ | ✔ |
| 콘텐츠 게시(정적 사이트 빌드·배포 트리거) | ✖ | ✔ | ✔ |
| 자료 카탈로그 편집 | ✖ | ✔ | ✔ |
| 사용자 목록·검색 | ✖ | ✖ | ✔ |
| 역할 부여·회수 | ✖ | ✖ | ✔ (자기 admin 회수 금지, 마지막 admin 보호) |
| 사용자 비활성화·세션 강제 종료 | ✖ | ✖ | ✔ |
| 감사 로그 열람 | ✖ | ✖ | ✔ |
| 시스템 설정 열람 | ✖ | ✖ | ✔ (시크릿 값은 마스킹) |

- 권한 검사는 FastAPI 의존성 `require(role)`과 리포지토리 계층의 `user_id` 바인딩 두 겹으로 한다. 엔드포인트가 역할을 통과해도 리포지토리는 항상 인증 컨텍스트의 `user_id`로만 조회한다.
- 콘텐츠는 git이 원본이므로 `author`의 편집은 Phase 2에서는 PR 기반(웹 편집 없음)이고, 서버는 "게시" 권한만 다룬다.

## 4. 데이터 모델 (서버 모드 추가 테이블)

```sql
users(id PK INTEGER, email UNIQUE, email_verified_at, display_name, locale, timezone,
      password_hash NULL, role TEXT NOT NULL DEFAULT 'learner',   -- learner | author | admin
      mfa_enabled bool, mfa_secret_enc NULL,
      status, created_at, updated_at, deleted_at NULL)
  -- status: active | disabled | pending_deletion ; password_hash NULL 이면 OIDC 전용 계정
identities(id PK, user_id FK, provider, subject, email, raw_claims_json, linked_at,
           UNIQUE(provider, subject))   -- PRD User.oidc_issuer+subject 를 1:N 으로 일반화
sessions_auth(id PK, user_id FK, created_at, last_seen_at, expires_at, ip, user_agent, revoked_at NULL)
api_tokens(id PK, user_id FK, name, token_hash UNIQUE, scopes_json, expires_at, last_used_at, revoked_at NULL)
one_time_tokens(id PK, user_id FK, kind, token_hash UNIQUE, expires_at, used_at NULL)
  -- kind: verify_email | reset_password
audit_log(id PK bigint, at, actor_user_id NULL, actor_ip, action, target_type, target_id,
          detail_json, request_id)
  -- action 예: auth.login.success | auth.login.failed | auth.logout | user.role.granted |
  --           user.disabled | content.published | data.exported | account.deleted
```

- 학습 테이블의 `user_id`는 양쪽 모드 모두 정수다(현재 구현 `INTEGER DEFAULT 1`). 서버 모드는 `users.id`(identity)를 FK로 건다. 로컬 모드에는 `users` 테이블이 없다.
- 역할 변경은 `users.role` 갱신 + `audit_log(user.role.changed, detail={from,to,granted_by})`. 마지막 admin의 역할은 내릴 수 없다.
- 계정 삭제(FR-10.7): 기본은 요청 즉시 학습 데이터 삭제 + `users` 행 익명화(email → `deleted-<id>@invalid`, display_name 제거, status `deleted`). 운영자가 `ACCOUNT_DELETE_GRACE_DAYS`(기본 0)를 두면 그 기간 동안 `pending_deletion`으로 두고 로그인 시 취소할 수 있다. 감사 로그는 보존 기간(`AUDIT_RETENTION_DAYS`, 기본 365) 뒤 삭제.
- 감사 로그는 append-only. 삭제 대신 보존 기간(기본 1년) 후 아카이브.
- 개인정보 최소화: 로그에는 이메일 대신 `user_id`, IP는 /24 마스킹 옵션.

## 5. 흐름

```mermaid
sequenceDiagram
  participant B as 브라우저
  participant W as 웹 (Phase 2)
  participant A as API
  participant IdP as OIDC 제공자
  B->>W: "Google로 로그인"
  W->>A: GET /api/v1/auth/oidc/google/start
  A-->>B: 302 IdP authorize (state, nonce, PKCE)
  B->>IdP: 로그인·동의
  IdP-->>B: 302 /api/v1/auth/oidc/google/callback?code&state
  B->>A: callback
  A->>IdP: code → token (PKCE verifier)
  A->>A: id_token 서명·nonce·email_verified 검증, identities 조회/생성
  A->>A: sessions_auth 생성, audit_log(auth.login.success)
  A-->>B: Set-Cookie: sid=…; 302 /dashboard
```

로컬 로그인은 `POST /api/v1/auth/login {email, password}` → Argon2id 검증 → 세션 생성으로 같은 뒷부분을 공유한다. 실패 시 응답은 성공·실패 모두 같은 시간대로 맞춘다(타이밍 차이 최소화).

## 6. API 엔드포인트 (인증 관련)

| 메서드·경로 | 설명 | 인증 |
|---|---|---|
| `POST /api/v1/auth/signup` | 로컬 계정 생성, 인증 메일 발송 | 없음 (속도 제한) |
| `POST /api/v1/auth/login` / `POST /api/v1/auth/logout` | 세션 생성/폐기 | 없음 / 세션 |
| `GET /api/v1/auth/oidc/{provider}/start` · `/callback` | OIDC 로그인 | 없음 |
| `POST /api/v1/auth/verify-email` · `/password/forgot` · `/password/reset` | 토큰 기반 | 없음 |
| `GET /api/v1/me` · `PATCH /api/v1/me` | 프로필 조회·수정(이름, locale, timezone) | 세션/PAT |
| `GET/POST/DELETE /api/v1/me/identities` | 연결 계정 관리 | 세션 |
| `GET/POST/DELETE /api/v1/me/tokens` | PAT 발급·폐기 | 세션 |
| `GET /api/v1/me/export` · `DELETE /api/v1/me` | 데이터 내보내기(JSON, `rc progress export`의 `ProgressExport`와 같은 스키마)·계정 삭제(즉시 또는 설정된 유예 기간) | 세션 |
| `GET /api/v1/admin/users` · `PATCH /api/v1/admin/users/{id}` | 목록·역할·상태 | admin |
| `GET /api/v1/admin/audit` | 감사 로그 조회 | admin |

## 7. 보안 요구 (체크리스트)

- 기준: **OWASP ASVS Level 2**(PRD 7절). 릴리스마다 `docs/ops/asvs-l2-checklist.md`를 점검하고 결과를 릴리스 노트에 첨부.
- 전송: HTTPS 강제, HSTS, 쿠키 `Secure`.
- 헤더: CSP(스크립트 self + 해시), `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`.
- CORS: 웹 프론트엔드 출처만 허용, 자격 증명 포함 요청은 명시 목록.
- 입력: pydantic 모델로 전부 검증, 파일 업로드 없음(Phase 2).
- 속도 제한: 로그인·가입·토큰 발급 엔드포인트에 IP+계정 키.
- 의존성: `pip-audit`·`trivy`를 CI에서 실행, Dependabot.
- 테스트: 인증 우회·권한 상승 시나리오는 `docs/platform-design.md` §7 참조.
- 취약점 신고: `SECURITY.md`에 비공개 신고 경로와 90일 공개 정책.
