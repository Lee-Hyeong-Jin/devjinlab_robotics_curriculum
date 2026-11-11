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
