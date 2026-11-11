# 서버(P2-1 API · P2-2 인증 · P2-3 Postgres) 보안·품질 리뷰 (2026-11-11)

- 대상: `integration` @ `1fb6f4f`, 범위 `src/robotics_curriculum/{api,auth}/`, Postgres 저장소,
  퀴즈·복습 API, `Dockerfile`, `docker-compose.yml`
- 기준: PRD 부록 C.3(AC-AUTH.1~9), `docs/ops/asvs-l2-checklist.md`, `.claude/rules/engineering.md`
- 방법: 코드 정독 + 실제 `uvicorn` 기동(별도 포트·임시 데이터 디렉터리)과 ASGI 왕복 요청.
  재현은 `tests/test_server_review.py`(SRV-01~05, `xfail(strict=True)`). 수정은 하지 않았다.
- 게이트: 이 브랜치에서 `scripts/harness/check.sh` 통과(아래 "검증" 참조).

## 요약

| 심각도 | 건수 | ID |
|---|---|---|
| critical | 0 | — |
| high | 2 | SRV-01, SRV-02 |
| medium | 3 | SRV-03, SRV-04, SRV-06 |
| low | 4 | SRV-05, SRV-07, SRV-08, SRV-09 |

담당: SRV-01·05·07 = api-developer, SRV-02·03·04 = api-developer(인증), SRV-06·09 =
platform-harness-rules-file(컨테이너·CI), SRV-08 = db-engineer.

## High

| ID | 파일:줄 | 재현 | 영향 | 권고 |
|---|---|---|---|---|
| SRV-01 배포 기본값이 인증 없는 모드 | `api/settings.py:43`(`auth_mode = "local"` 기본), `api/deps.py:129-136,164-167`(local 모드에서 모든 요청이 `LOCAL_PRINCIPAL` = role **admin**), `Dockerfile:69`(`RC_API_HOST=0.0.0.0`), `docker-compose.yml:54-56`(api 서비스가 `RC_DATABASE_URL` 만 설정, `RC_AUTH_MODE` 없음) | `RC_AUTH_MODE` 를 비우고 uvicorn 기동 → 자격증명·CSRF 없이 `GET /api/v1/courses` 200, `POST /api/v1/progress/log` 201, `GET /api/v1/progress/status` 200, `GET /api/v1/me` 200 (`role: admin`, `email: local@localhost`). `test_srv01_compose_api_runs_in_server_mode` | 이미지와 compose 를 그대로 띄우면 **인증이 꺼진 상태로 0.0.0.0 에 바인딩**된다. compose 는 포트를 `127.0.0.1:8000` 으로만 공개하므로 기본 상태에서 원격 노출은 아니지만, 호스트의 다른 프로세스·컨테이너가 학습 데이터를 읽고 쓸 수 있고, 포트 공개를 바꾸거나 리버스 프록시 뒤에 두면 그대로 외부에 열린다. 공유 Postgres 를 쓰면서 user 1 로 동작하므로 AC-AUTH.4·AC-AUTH.5(역할 강제·사용자 격리)가 배포 기본값에서 성립하지 않는다 | ① compose api 서비스에 `RC_AUTH_MODE: server` 를 넣고, ② 서버 모드가 아닌데 `RC_API_HOST` 가 루프백이 아니면 기동을 거부하거나 경고 후 local 모드를 끄도록 한다(ASVS V1.4). ③ `/api/v1/me` 가 local 모드에서 admin 을 반환하지 않게 하거나, local 모드를 "단일 사용자, 역할 없음"으로 분리한다 |
| SRV-02 부트스트랩 관리자 이메일 선점 | `auth/service.py:201`(`role = ADMIN if email == config.bootstrap_admin_email`), `:282`(로그인은 `is_active` 만 확인, 이메일 인증 여부 무관), `auth/models.py:68-69` | `RC_AUTH_ADMIN_EMAIL=owner@example.com` + 기본값 `RC_AUTH_ALLOW_SIGNUP=1` 로 서버 모드 기동 → 공격자가 그 주소로 `POST /api/v1/auth/signup` → 응답 `role: admin`, 이메일 인증 없이 `POST /auth/login` 200(`role: admin`), `GET /api/v1/admin/users` 200. 실제 uvicorn 으로 확인. `test_srv02_bootstrap_admin_requires_verified_owner` | 관리자 주소를 아는 사람(보통 공개된 운영자 메일)이 먼저 가입하면 관리자 권한을 얻는다. 사용자 역할 변경·세션 강제 종료·감사 로그 열람이 모두 가능해 AC-AUTH.4 위반이며, 메일박스 소유 증명이 전혀 요구되지 않는다 | ① 부트스트랩 관리자는 가입이 아니라 CLI·환경에서 직접 생성(또는 초대 토큰)으로만 만든다. ② 최소한 `email_verified_at` 이 있을 때까지 승격을 보류한다. ③ 승격 시 감사 로그에 `user.role.changed` 를 남긴다(현재 signup 은 `user.created` 의 `detail.role` 로만 기록) |

## Medium

| ID | 파일:줄 | 재현 | 영향 | 권고 |
|---|---|---|---|---|
| SRV-03 비밀번호 재설정 요청에 속도 제한 없음 | `auth/service.py:461-474`(`forgot_password` 가 `failed_logins`/스로틀을 호출하지 않음), `api/routers/auth.py:91-99` | 스텁 메일러로 서버 모드 기동 후 `POST /auth/password/forgot` 20회 → 전부 202, 메일 20통 발송, 429 없음. 로그인은 5회에서 429 가 나오므로 대비가 분명하다. `test_srv03_forgot_password_is_rate_limited` | 피해자 메일박스 폭주(메일 폭탄), 발신 도메인 평판 훼손, SMTP 비용. AC-AUTH.2 의 속도 제한이 로그인에만 적용된다 | IP·이메일별 윈도 제한(예: 15분에 3회)을 `forgot_password`·`verify-email` 재발송에 적용하고 `Retry-After` 를 붙인다. 초과는 감사 로그에 남긴다 |
| SRV-04 재설정 토큰이 동시에 여러 개 유효 | `auth/service.py:216-233`(`_send_token` 가 기존 토큰을 폐기하지 않음), `:476-485` | 위 20회 요청으로 서로 다른 토큰 20개가 모두 유효 → 가장 오래된 토큰으로 `POST /auth/password/reset` 204, 두 번째 토큰으로도 204(소비된 토큰 재사용만 422). `test_srv04_new_reset_token_invalidates_the_previous_one` | 유출·유실된 링크의 위험 창이 30분 × 요청 횟수만큼 누적된다. ASVS V2.5.1(복구 토큰은 단일 유효)에 어긋난다 | 새 토큰 발급 시 같은 사용자·같은 종류의 미사용 토큰을 폐기한다. 재설정 성공 시에도 남은 토큰을 모두 폐기한다(세션 폐기는 이미 함) |
| SRV-06 compose 의 기본 DB 비밀번호 | `docker-compose.yml:23`(`POSTGRES_PASSWORD: ${RC_DB_PASSWORD:-rc-dev-only}`), `:55`(같은 기본값이 `RC_DATABASE_URL` 에) | 파일 확인. 주석(9행)은 운영에서 `POSTGRES_PASSWORD_FILE`/시크릿을 쓰라고 안내한다 | `.env` 없이 띄우면 알려진 비밀번호로 DB 가 뜬다. 같은 호스트의 다른 컨테이너·프로세스가 DB 에 접속할 수 있다 | 기본값을 없애고(`${RC_DB_PASSWORD:?set RC_DB_PASSWORD}`) 미설정 시 기동을 실패시킨다. 개발용 값은 `.env.example` 에 둔다 |

## Low

| ID | 파일:줄 | 근거 | 권고 |
|---|---|---|---|
| SRV-05 오류 응답이 서버 경로를 노출 | `api/deps.py:118`(`503 curriculum not loaded: {load_error}`), `api/routers/health.py`(`/readyz` 의 `checks.content.detail`) | 커리큘럼 디렉터리를 없애고 요청 → `GET /api/v1/courses` 503 본문과 `/readyz` 본문에 `/home/<user>/...` 절대 경로가 그대로 담긴다. `/readyz` 는 인증이 필요 없다. `test_srv05_readyz_does_not_leak_filesystem_paths` | 사용자 응답에는 "콘텐츠를 불러오지 못했습니다" 수준만, 상세는 로그에만 남긴다(엔지니어링 규칙의 "내부 경로 노출 금지") |
| SRV-07 감사 로그 공백 | `auth/service.py:177-185`, `api/deps.py:192-197` | 로그인 성공·실패·스로틀, 가입, 역할 변경, 토큰 생성·폐기, 세션 폐기, 계정 삭제는 기록된다. 기록되지 않는 것: CSRF 실패, PAT 인증 실패, 권한 부족(403), 무효 토큰으로 온 재설정 시도, 관리자 조회(`/admin/users`, `/admin/audit`) | 공격 탐지에 필요한 실패 이벤트와 관리자 접근을 추가한다(AC-AUTH.2·V7.2) |
| SRV-08 `erase_user` 의 범위 | `auth/service.py:489-499`, `api/app.py:87-92` | 계정 삭제는 `erase_learning_data`(진행도)와 `store.erase_user`(익명화)를 호출한다. 감사 로그는 보존 기간(90일)이 지나야 `anonymize_audit` 로 익명화되고, 삭제 시점에 해당 사용자 식별자가 남는다 | 설계 의도라면 AC-AUTH.6 문구에 "감사 로그는 90일 후 익명화"를 명시하고, 삭제 요청 시 즉시 익명화할지 PM·아키텍트와 합의한다 |
| SRV-09 컨테이너 헬스체크·이미지 | `Dockerfile:55-82`, `docker-compose.yml:62-74` | 비루트(uid 10001), `/data` 볼륨, curl 없는 이미지와 python 헬스체크는 적절하다. 다만 `api` 서비스에 `read_only: true`·`cap_drop`·`no-new-privileges` 가 없고, 이미지에 `HEALTHCHECK` 지시문이 없다(compose 에만 있음) | `security_opt: [no-new-privileges:true]`, `cap_drop: [ALL]`, 가능하면 `read_only: true` + `tmpfs` 를 추가한다 |

## 확인했고 문제없음

- **비밀번호**: Argon2id(`time_cost=3`, 64 MiB, `parallelism=4`), 서버 측 pepper 옵션, 12~128자 정책에
  이메일 로컬파트·표시 이름 포함 금지, 로그인 시 `check_needs_rehash` 재해싱. 미지의 계정도 더미 해시로
  한 번 검증해 타이밍 차이를 줄인다(`auth/crypto.py`). 평문·해시가 로그·응답에 들어가지 않는다(AC-AUTH.1).
- **세션**: 로그인마다 새 토큰(세션 고정 불가), 토큰은 SHA-256 으로만 저장, idle 14일 + 절대 30일 상한,
  비활성 사용자·폐기 세션 거부, 1분 단위 슬라이딩 갱신. 쿠키는 `HttpOnly`·`SameSite=lax`·`Secure`(기본값;
  `RC_AUTH_COOKIE_SECURE=0` 은 개발용). 비밀번호 변경·재설정 시 다른 세션 폐기.
- **CSRF**: 세션 쿠키 인증의 비안전 메서드는 `X-CSRF-Token` 이 저장된 해시와 일치해야 한다. 헤더 없음·오답
  모두 403 확인. PAT 요청은 쿠키를 쓰지 않으므로 면제(올바름).
- **권한**: 학습자의 `/api/v1/admin/*` 403, PAT 스코프 분리(읽기 전용 토큰의 쓰기 403), 계정 관리
  엔드포인트는 PAT 거부 403, PAT 으로 admin 스코프 토큰 발급 403, 마지막 관리자 강등·자기 강등 차단.
- **IDOR**: 진행도는 `current_user_id`(principal)로만 접근하고 경로에 user_id 가 없다. 다른 사용자의
  세션 id 로 `DELETE /api/v1/me/sessions/{id}` → 404(소유자 조건이 쿼리에 포함됨).
- **로그인 스로틀**: 이메일 5회/IP 20회(15분)에서 429 + `Retry-After` 확인, 감사 로그 기록.
- **SQL 인젝션**: `auth/store.py` 는 SQLAlchemy Core 표현식만 쓰고 `text()` 가 0건, 문자열 보간 SQL 없음.
  진행도 저장소는 바인딩 파라미터만 쓴다(1차 리뷰에서 확인).
- **열거**: 로그인 오류 메시지는 "invalid email or password" 단일, `forgot` 은 존재 여부와 무관하게 202.
- **보안 헤더**: API 는 `default-src 'none'` CSP, nosniff, `X-Frame-Options: DENY`, no-referrer,
  Permissions-Policy, COOP, 서버 모드에서 HSTS, 계정 경로에 `Cache-Control: no-store`.
- **오류 형식**: RFC 9457 problem+json, 요청 id 상관관계, 처리되지 않은 예외는 미들웨어에서 500 problem
  으로만 나가고 스택은 로그에만 남는다. CORS 미들웨어가 없어 브라우저 교차 출처 호출은 불가(의도된 설계).
- **마이그레이션**: Alembic `0003_auth` 가 compose 의 `migrate` 서비스에서 먼저 실행되고 api 는
  `service_completed_successfully` 를 기다린다.

## 미확인 (범위·환경 제약)

- OIDC/PKCE(AC-AUTH.3)는 아직 501 스텁이라 검증 대상이 없다.
- 실제 PostgreSQL 인스턴스에 대한 동시성·권한 테스트는 하지 않았다(SQLite 경로만 기동). `test_auth_postgres.py`
  는 Postgres 가 있을 때만 돌도록 되어 있다.
- 부하·성능 기준(p95 300ms/500 동시)과 접근성은 이번 범위가 아니다.

## 검증

```bash
uv run pytest tests/test_server_review.py -rx   # 5 xfailed = 결함 5건 재현
bash scripts/harness/check.sh                   # 전체 게이트
```

---

## 재검증 (2026-11-11, integration 8164f71)

방법: 실제 `rc api serve`(서버 모드, SQLite, 포획 SMTP 서버로 메일 토큰 수신) 프로세스에 대한 HTTP 프로빙,
`bash scripts/smoke.sh`(docker compose, 빌드 포함) 1회 전체 실행, 그리고 `tests/test_oidc.py` 의 FakeIdP
하니스를 재사용한 OIDC 프로빙. 실행한 명령과 응답에 근거해 적는다.

### SRV-01 ~ SRV-09 판정

| ID | 판정 | 근거 |
|---|---|---|
| SRV-01 | **해결됨** (a285491, 7e7d14c) | 서버 모드 실서버: `/api/v1/courses`·`/me`·`/progress/status`·`POST /progress/log` 모두 401. 로컬 모드 바인드 가드 동작: `--host 0.0.0.0`, `--host ::` 기동 거부, `127.0.0.1` 기동, `RC_API_ALLOW_REMOTE_LOCAL=1` 로만 우회. compose/Dockerfile 에 `RC_AUTH_MODE=server`. docker smoke: `/api/v1/courses -> 401 without credentials` |
| SRV-02 | **해결됨** (7e7d14c) | `RC_AUTH_ADMIN_EMAIL` 주소로 가입 → `role: learner`, 미인증 상태로 `/admin/users` 403. 메일 토큰으로 이메일 인증 후에만 admin 승격, 승격 후 두 번째 계정은 learner 유지(활성 admin 이 있으면 승격 안 함) |
| SRV-03 | **해결됨** (7e7d14c) | 같은 주소 8회 요청 → `[202,202,202,429,…]`, 메일 3통. 대소문자·공백 변형(`VICTIM@Example.com `)도 같은 키로 429. 다른 주소는 IP 한도(10)까지 202 |
| SRV-04 | **해결됨** (7e7d14c) | 연속 2회 요청 후 오래된 토큰 422, 최신 토큰 204, 최신 토큰 재사용 422, verify-email 토큰을 reset 으로 제출 시 422 |
| SRV-05 | **해결됨** (7e7d14c) | `/api/v1/courses`, `/readyz`, 404 응답 본문에 파일시스템 경로 없음(정규식 스캔). 상세는 서버 로그에만 |
| SRV-06 | **해결됨** (a285491) | `docker-compose.yml` 의 비밀은 모두 `${…:?set …}` 필수값. smoke 는 임의값을 생성해 주입 |
| SRV-07 | **해결됨** (7e7d14c) | `/admin/audit` 에 `auth.denied`, `admin.users.viewed`, `auth.password.reset_invalid`, `user.role.changed` 기록 확인 |
| SRV-08 | **미재검증** | 계정 삭제·익명화 경로는 이번 프로빙에서 실행하지 않았다. 문서 합의 사항(AC-AUTH.6 문구)도 미확인 |
| SRV-09 | **해결됨** (a285491) | compose 의 api/web/db 에 `read_only: true`, `tmpfs`, `cap_drop: [ALL]`, `security_opt`, Dockerfile 에 `HEALTHCHECK`. docker smoke 전체 통과(migrate exit 0, api healthy, JSON 로그, X-Request-ID 상관관계) |

우회 시도 중 막힌 것: OIDC `return_to` 오픈 리다이렉트·헤더 주입(`//evil.com`, `/\evil.com`,
`https://evil.com`, CR/LF, 탭, `%2f%2f` 모두 `/` 로 축약되거나 퍼센트 인코딩됨), 코드 재사용(다른 브라우저에서
400), state 불일치(400), PAT 로 계정 연결(409), 기존 계정 이메일 대문자 변형 자동 연결(409), CSRF 헤더 없는/틀린
쓰기(403), PAT 스코프 상승(`write:progress` 없는 PAT 로 쓰기 403, `/me/tokens` 403, `/admin/users` 403),
learner 의 `/admin/audit`(403), 사용자 간 진행도 격리(u9 1건 / admin 0건).

이전 커리큘럼 리뷰(QA-01 ~ QA-12)도 모두 해결됨: 콘텐츠 15개 필드(코스·모듈 제목/요약, 레슨 제목·요약·목표·태그·
활동·자료 note·본문·공부법)에 XSS 페이로드를 넣고 사이트를 빌드해 DOM 파서로 스캔한 결과 살아 있는 스크립트 0건.
`tests/test_security_review.py`·`tests/test_server_review.py` 21건 모두 통과(xfail 없음).

### 새 결함 (보고만, 수정하지 않음)

| ID | 심각도 | 파일:줄 | 재현 | 영향 | 권고 |
|---|---|---|---|---|---|
| SRV-10 메일 발송 실패가 500, 계정은 생성됨 | medium | `auth/service.py:267-287`(`_send_token` 가 `smtplib` 예외를 감싸지 않음), `api/routers/auth.py:90,125` | SMTP 포트를 닫고 `POST /auth/signup` → 500 `internal server error`(서버 로그에 ConnectionRefused). 그 뒤 `POST /auth/login` 200: 계정은 존재하고 인증 메일만 없다. `POST /auth/password/forgot` 도 500 | 메일 서버 장애 시 가입이 "실패"로 보이지만 계정이 남아 재가입은 409. 사용자는 이메일 인증을 받을 수 없고, 500 은 ASVS V7.4.1(예상 가능한 실패를 사용자 메시지로) 위반 | `_send_token` 에서 `smtplib.SMTPException`·`OSError` 를 잡아 `Unavailable`(503)로 바꾸고, 가입은 트랜잭션으로 되돌리거나 "메일 재발송" 경로를 제공한다 |
| SRV-11 바인드 가드가 CLI 에만 있음 | medium | `api/cli.py:84-95`(가드), `api/app.py:126-140`(`create_app` 에는 없음) | `uvicorn.run(create_app(Settings.from_env().with_overrides(host="0.0.0.0")))` 를 로컬 모드로 실행 → 기동되고 `/api/v1/me` 가 `role: admin` 반환 | FastAPI 관례대로 `uvicorn robotics_curriculum.api.app:...` 로 띄우면 SRV-01 보호가 사라진다. compose 는 `rc api serve` 를 쓰므로 기본 배포는 안전 | 가드를 `create_app`(또는 startup 이벤트)으로 옮긴다. 문서에도 `rc api serve` 사용을 명시 |
| SRV-12 웹의 CSRF 쿠키 이름 불일치 | medium | `web/src/lib/api/client.ts:21`(`CSRF_COOKIE = 'csrf'`) 대 `api/deps.py:129`(`CSRF_COOKIE = "csrf_token"`) | 코드 확인. API 는 `csrf_token` 쿠키를 심는데 웹은 `csrf` 를 읽어 `X-CSRF-Token` 을 붙인다 → 헤더 없이 전송 → 모든 쓰기가 403 | 지금은 웹에 쓰기 화면이 없어 드러나지 않는다(로그인 화면도 플레이스홀더). P2-4 의 첫 변경 요청에서 전부 실패한다 | 이름을 `csrf_token` 으로 맞추고, 상수를 생성된 스키마나 공용 상수에서 가져온다. 계약 테스트에 쓰기 1건을 추가 |
| SRV-13 웹 의존성 취약점, CI 에 npm audit 없음 | medium | `web/package.json`, `.github/workflows/security.yml:42-67`(pip-audit 만) | `npm audit --omit=dev`: 7건(high 1 `postcss` XSS via unescaped `</style>`, moderate `next`, moderate `next-intl` 오픈 리다이렉트, low `katex` 외). 전체(dev 포함) 19건, critical 2(`vitest`, `tinypool` 프로토타입 오염→RCE) | PRD 7절은 의존성 스캔을 CI 에 포함하라고 요구한다. 파이썬만 스캔되고 있다. `next-intl` 오픈 리다이렉트는 웹 라우팅에 직접 닿는다 | `npm audit --omit=dev --audit-level=high` 를 security.yml 에 추가(차단), dev 는 비차단. `next-intl`·`next`·`postcss` 갱신 |
| SRV-14 id_token 의 다중 `aud` 수용 | low | `auth/oidc.py:245-258`(PyJWT `audience=client_id`, `azp` 미검사) | FakeIdP 로 `aud: [rc-web, some-other-client]`, `azp: other` 인 id_token 발급 → 콜백 302 로그인 성공. `aud: [some-other-client]` 만이면 400 | OIDC Core 3.1.3.7 ③~⑤ 위반. 같은 IdP 에 다른 클라이언트를 가진 공격자가 다중 `aud` 토큰을 우리 코드 교환 흐름에 넣을 수 있어야 하므로 실제 악용은 어렵다(코드 교환은 우리 클라이언트가 수행) | `aud` 가 리스트면 길이 1 이고 `client_id` 와 같은지 확인하거나, `azp` 가 있으면 `client_id` 와 일치할 것을 요구한다 |
| SRV-15 `RC_AUTH_SECRET` 미설정 시 프로세스별 플로우 키 | low | `api/app.py:148-151` | 프로바이더가 설정돼 있고 시크릿이 없으면 경고만 남기고 `secrets.token_bytes(32)` 사용 | `uvicorn --workers N` 이나 복제본이 2개 이상이면 OIDC 콜백이 다른 워커에 도달해 "login expired" 로 간헐 실패. compose 는 시크릿을 필수로 요구하므로 기본 배포는 영향 없음 | 프로바이더가 있으면 시크릿을 필수로 요구(기동 실패)하거나, 단일 워커임을 확인한다 |
| SRV-16 `/metrics` 무인증 | low | `api/routers/health.py:61-72`, `api/metrics.py:1-15` | 서버 모드 실서버에서 `GET /metrics` 200(인증 없음). 라벨은 라우트 템플릿·상태코드와 DB 풀 수치뿐이고 개인 데이터는 없다. 미매칭 경로는 `unmatched` 라벨로 고정되어 카디널리티 폭증도 없다 | 설계·문서상 "내부망 전용"이며 compose 는 8000 을 127.0.0.1 에만 공개한다. 그래도 라우트 목록과 트래픽량이 노출된다 | 리버스 프록시 차단을 RUNBOOK 에 명시(이미 주석에 있음)하거나, 선택적 베어러 토큰(`RC_API_METRICS_TOKEN`)을 둔다 |
| SRV-17 번들 KaTeX 가 취약점 범위 안 | low | `src/robotics_curriculum/site/assets/katex/VERSION`(0.16.11) | `npm audit` 가 같은 권고를 보고: GHSA-238p-pmpm-9mq7 는 `>=0.11.0 <0.18.2`. 정적 사이트의 번들 사본도 같은 범위다. `katex-init.js` 는 `trust` 를 켜지 않으므로 현재 설정에서는 악용 경로가 없다 | 이전 리뷰 QA-19 의 "미확인" 항목이 확인됐다 | 0.18.2 이상으로 갱신하고 파일별 sha256 매니페스트를 테스트로 고정한다 |

### 남은 위험 (해결된 항목의 잔여)

- SRV-01 잔여: 로컬 모드는 여전히 `/api/v1/me` 에서 `role: admin` 을 반환한다(원 권고 ③ 미적용). 단일 사용자
  모드이므로 영향은 작지만, 역할 개념을 로컬 모드에서 분리하면 혼동이 줄어든다.
- SRV-02 잔여: 공격자가 `RC_AUTH_ADMIN_EMAIL` 주소를 선점하면 실제 운영자는 409 로 가입할 수 없다(계정 선점).
  또 `promote_admin`(`auth/service.py:252-268`)은 `email_verified_at` 을 확인하지 않으므로, 운영자가 선점된
  주소에 `rc api promote-admin` 을 실행하면 공격자 계정이 admin 이 된다. 승격 시 이메일 인증을 요구하거나,
  선점 계정을 식별할 수 있게 경고를 출력할 것을 권고한다.

---

## 2차 재검증 (2026-11-12, integration 52d1608)

대상 수정: 2364ee4(api-developer: SRV-10·11·14·15·16, promote-admin, SRV-08 테스트),
75468eb(devops: SRV-13 npm audit CI, SRV-17 KaTeX 0.19.1 + MANIFEST), ff75e8d(frontend: SRV-12).
방법은 1차와 같다: 실제 `rc api serve` 프로세스 프로빙, `bash scripts/smoke.sh`(docker, web 포함) 전체 실행,
`tests/test_oidc.py` FakeIdP 하니스 재사용. 게이트: `scripts/harness/check.sh` ALL CHECKS PASSED.

| ID | 판정 | 근거 |
|---|---|---|
| SRV-08 | **해결됨** (2364ee4) | `DELETE /api/v1/me` 204 → 세션 401, 재로그인 401, 진행도 삭제. 관리자 `/admin/audit` 200건 조회에서 삭제된 주소 0건(즉시 익명화), `account.deleted` 기록. 회귀 테스트 `tests/test_auth_review.py:178` |
| SRV-10 | **해결됨** (2364ee4) | SMTP 포트를 닫고 `POST /auth/signup` 201, `POST /auth/password/forgot` 202, 서버 로그에 `mail delivery failed`, 로그의 500 응답 0건. `_send_token`(`auth/service.py:282-306`)이 예외를 삼키고 감사에 남긴다 |
| SRV-11 | **해결됨** (2364ee4) | 가드가 `api/app.py:82-101`(`check_exposure`)로 이동. `uvicorn.run(create_app(Settings…host='0.0.0.0'))` 로컬 모드 → `UnsafeConfiguration` 으로 기동 실패(exit 1). `rc api serve --host 0.0.0.0` 도 여전히 거부 |
| SRV-12 | **해결됨** (ff75e8d) | `web/src/lib/api/client.ts:24` 가 `csrf_token` 으로 API(`api/deps.py:129`)와 일치 |
| SRV-13 | **부분 해결** (75468eb) | CI 에 `npm audit --omit=dev --audit-level=high`(차단) + 전체(비차단) 추가됨. **그러나 현재 락파일에서 두 명령 모두 exit 1**: 런타임 의존성에 high 1건(`postcss` XSS via unescaped `</style>`), moderate 2건(`next`, `next-intl` 오픈 리다이렉트), low 4건. 즉 이 잡은 업그레이드 전까지 CI 를 빨갛게 만든다(프런트 작업 중, 미해결로 표시) |
| SRV-14 | **해결됨** (2364ee4) | `auth/oidc.py:361-369`. `aud: [rc-web, other]` + azp 없음 → 400, `azp: other` → 400, `aud: [other]` → 400, 정상 단일 aud 는 302 |
| SRV-15 | **해결됨** (2364ee4) | 프로바이더가 있고 `RC_AUTH_SECRET` 이 없으면 기동 거부: "must be set when OIDC providers are configured: it signs the in-flight login cookie and must be identical on every worker and replica" |
| SRV-16 | **해결됨** (2364ee4) | `RC_API_METRICS_TOKEN` 설정 시 `/metrics` 는 토큰 없음 401, 틀린 토큰 401, 올바른 토큰 200. 미설정 시 공개는 문서화된 기본값이며 compose 는 127.0.0.1 에만 공개 |
| SRV-17 | **해결됨(정적 사이트)** (75468eb) | 번들 KaTeX 0.19.1(권고 범위 `<0.18.2` 밖), `MANIFEST.sha256` 25개 항목 `sha256sum -c` 전부 OK, 테스트 `tests/test_katex_assets.py`. **웹 의존성의 katex 는 아직 0.11.0–0.18.1 범위**(SRV-13 의 low 1건으로 남음) |

1차 잔여 항목도 해소됐다: `promote_admin` 은 이메일 미인증 계정을 거부하고("has not verified its email
address"), 인증 후에만 승격한다(실행 확인). 선점 자체(동일 주소 재가입 409)는 설계상 남지만, 승격 경로가 막혀
악용 가치가 낮다.

docker smoke(web 포함) 전체 통과: migrate exit 0, api/web healthy, 무자격 `/api/v1/courses` 401,
세션 로그인 후 200, `/metrics` 200, X-Request-ID 상관관계, 단일 라인 JSON 로그, 웹 4개 화면 200.

**미해결 1건(medium): SRV-13** — 런타임 의존성 high 1·moderate 2. 새 critical/high 결함은 없다.
