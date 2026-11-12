# 운영 런북 (서버 모드)

자체 호스팅 서버 모드를 운영하는 사람을 위한 절차서다. 설계 근거는
`docs/architecture/operations.md`, 수용 기준은 PRD 부록 C.5(AC-OPS.1~4)에 있다.
로컬 모드(`rc` CLI)만 쓰는 경우 이 문서는 필요 없다.

전제: Docker 와 compose 플러그인, 저장소 체크아웃. 모든 명령은 저장소 루트에서 실행한다.

## 1. 구성

| 서비스 | 프로파일 | 역할 |
|---|---|---|
| `db` | (기본) | PostgreSQL 16.13. 볼륨 `dbdata`, 포트는 `127.0.0.1:5432` 에만 바인딩 |
| `migrate` | (기본) | 일회성 `alembic upgrade head`. `api` 는 이 서비스가 성공 종료한 뒤에 뜬다 |
| `api` | (기본) | `rc api serve`(uvicorn). `127.0.0.1:8000`, 헬스체크는 `/readyz` |
| `cli` | `cli` | `rc` 일회성 실행용. `up` 에는 포함되지 않는다 |
| `backup` | `ops` | cron 용 `pg_dump` 컨테이너(§4) |

`web` 과 리버스 프록시는 P2-4 이후에 추가된다.

## 2. 기동과 정지

비밀값에는 기본값이 없다. 설정하지 않으면 compose 가 모든 명령(`cli` 포함)을 거부한다(§8):

```bash
export RC_DB_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
export RC_AUTH_SECRET="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
# 운영에서는 같은 값을 .env(커밋 금지)나 Docker secret 으로 둔다.
```

API 는 서버 모드(계정·세션 필수)로 뜬다. 첫 관리자는 `RC_AUTH_ADMIN_EMAIL` 로 가입 후 메일의
인증 링크를 누르면 승격된다(관리자가 아직 없을 때만). 메일이 없으면 가입 후
`docker compose run --rm api api promote-admin you@example.org` 로 승격한다(감사 로그에 기록).
이 명령은 이메일 인증을 마친 계정만 승격한다. 메일 서버가 없어 인증 링크를 받을 수 없는
환경에서는 주소 소유를 확인한 뒤 `--force` 를 붙인다.

서버는 `rc api serve` 로 띄운다. `uvicorn ...:create_app` 처럼 직접 띄워도 앱 팩토리가 같은
가드를 적용하지만(로그인 없는 local 모드를 루프백이 아닌 주소에 바인드하면 기동 거부),
`rc api serve` 가 설정 오류를 사람이 읽을 수 있는 메시지로 보여 준다.

```bash
docker compose up -d --wait api     # db -> migrate -> api, 전부 healthy 될 때까지 대기
docker compose ps                   # 상태 확인
docker compose logs -f api          # JSON 로그 추적
docker compose down                 # 정지 (볼륨 유지)
docker compose down -v              # 정지 + 데이터 삭제 (주의)
docker compose run --rm cli validate   # 콘텐츠 검증 같은 일회성 작업
```

스모크 점검: `bash scripts/smoke.sh` — 이미지를 새로 빌드해 스택을 올리고 `/healthz`, `/readyz`,
`/version`, `/openapi.json`, 자격 증명 없는 `/api/v1/courses` 401, 가입→로그인→세션으로
`/api/v1/courses` 200, `/metrics`, 요청 ID 에코, JSON 로그를 확인하고 내려놓는다. 비밀값이 없으면
일회용 임의 값을 만든다. `KEEP_UP=1` 을 주면 띄운 상태로 남긴다. 같은 스크립트가 CI 의 `smoke`
잡에서 돈다.

컨테이너 보안(서버 리뷰 SRV-09): `api`·`migrate` 는 읽기 전용 루트 파일시스템(`/tmp` 만 tmpfs,
`/data` 볼륨), `cap_drop: [ALL]`, `no-new-privileges`, 비루트 uid 10001 로 돈다. 이미지에도
`HEALTHCHECK` 가 있다.

## 3. 상태 점검

| 확인 | 명령 | 정상 |
|---|---|---|
| 프로세스 생존 | `curl -fsS localhost:8000/healthz` | `{"status":"ok"}` |
| 요청 처리 준비 | `curl -fsS localhost:8000/readyz` | `{"status":"ready", ...}`, DB·콘텐츠 색인 각각 `ok: true` |
| 버전 | `curl -fsS localhost:8000/version` | 배포한 버전 |
| 메트릭 | `curl -fsS localhost:8000/metrics` | Prometheus 텍스트. `RC_API_METRICS=0` 이면 404 |

`/metrics` 는 기본적으로 인증이 없다(내부망 전용). 셋 중 하나로 보호한다: ① 리버스 프록시에서
`/metrics` 를 외부에 노출하지 않는다(권장, compose 는 8000 을 `127.0.0.1` 에만 공개), ②
`RC_API_METRICS_TOKEN` 을 설정해 `Authorization: Bearer <토큰>` 을 요구한다(Prometheus
`authorization` 설정과 맞춘다), ③ `RC_API_METRICS=0` 으로 끈다.
| DB | `docker compose exec db pg_isready -U rc -d rc` | `accepting connections` |

`/readyz` 가 503 이면 본문의 `checks` 를 본다: `database` 실패는 DB 가 내려갔거나
`RC_DATABASE_URL` 이 틀린 것, `content` 실패는 `curriculum/` 로드 실패다(`rc validate` 로 확인).

로그는 한 줄 JSON이며 모든 요청에 `request_id` 가 있고 응답 헤더 `X-Request-ID` 와 같다.
장애를 추적할 때는 사용자에게 받은 요청 ID 로 로그를 검색한다.
`docker compose logs api | grep <request-id>`.

알림 기준(초기, operations.md §4): 5xx 비율 > 1%(5분), p95 > 500ms(10분), readiness 실패,
디스크 사용률 80%.

## 4. 백업

목표는 RPO 24시간, RTO 4시간이다(PRD 7절).

```bash
bash scripts/ops/backup.sh                       # backups/rc-<UTC>.dump
BACKUP_DIR=/srv/backups RETENTION_DAYS=30 bash scripts/ops/backup.sh
docker compose --profile ops run --rm backup     # 저장소 없이 cron 에서 돌릴 때
```

- 형식은 `pg_dump -Fc`(압축 custom). 덤프는 실행 중인 `db` 서비스 안에서 뜨므로 클라이언트와
  서버 버전이 항상 일치한다.
- 일정: 매일 02:00, 30일 보존 + 월 1회 1년(`RETENTION_DAYS` 로 호스트에서 조정).
- **덤프를 호스트 밖으로 보내야 백업이다.** 객체 저장소(S3 호환)에 서버 측 암호화로 올린다.
  `backups/` 는 `.gitignore` 에 있어 커밋되지 않는다.
- 업그레이드 전에는 `alembic upgrade` 직전에 한 번 더 받는다(operations.md §5).
- 콘텐츠는 git 이 원본이고, 정적 사이트는 재빌드 가능하므로 백업 대상이 아니다.

cron 예시(매일 02:00, 호스트):

```cron
0 2 * * * cd /srv/robotics-curriculum && BACKUP_DIR=/srv/backups bash scripts/ops/backup.sh >> /var/log/rc-backup.log 2>&1
```

## 5. 복구

```bash
bash scripts/ops/restore.sh backups/rc-20261111T020000Z.dump
```

덤프에 있는 객체를 모두 지우고 다시 만든다(`pg_restore --clean --if-exists --exit-on-error`).
스크립트가 복구 전에 `api` 를 멈추고 끝나면 다시 띄운다. 확인 프롬프트를 건너뛰려면 `FORCE=1`.

복구 후 점검: `/readyz` 200, 샘플 조회(`curl -fsS localhost:8000/api/v1/progress/lessons`),
로그에 오류 없음.

부분 복구 실패(`pg_restore` 오류)로 끝나면 데이터베이스가 중간 상태일 수 있다. 그때는 빈 DB로
다시 시작한다: `docker compose down -v && docker compose up -d --wait db` 후 다시 복구.

## 6. 복구 리허설

릴리스마다 한 번 실행하고 결과를 남긴다(AC-OPS.4).

```bash
bash scripts/ops/restore_drill.sh
```

진행도 마커를 API로 기록 → 백업 → `DROP SCHEMA public` 으로 데이터 파괴 → 복구 →
`/readyz` 와 마커 생존을 확인하고 `docs/ops/restore-drills.md` 에 한 줄을 추가한다.
**파괴적이므로 리허설 환경에서만 실행한다.** CI 의 `restore-drill` 잡에서도 같은 스크립트가
돌기 때문에 스크립트가 썩지 않는다.

## 7. 업그레이드

```bash
git pull
BACKUP_DIR=/srv/backups bash scripts/ops/backup.sh   # 1. 스냅샷
docker compose build api                             # 2. 새 이미지
docker compose up -d --wait api                      # 3. migrate 가 먼저 돌고 api 재기동
curl -fsS localhost:8000/version                     # 4. 확인
```

마이그레이션은 하위 호환(expand → migrate → contract) 원칙이라 한 릴리스 범위에서는 되돌릴 수
있다. 되돌릴 때는 `docker compose run --rm --entrypoint alembic api downgrade -1` 후 이전
이미지로 되돌린다. 컬럼 삭제가 포함된 릴리스는 스냅샷에서 복구하는 쪽이 안전하다.

## 7.1 지속 배포 (pull 방식)

단일 호스트(홈서버, 소형 VPS)는 `scripts/ops/deploy_pull.sh` 를 cron 이나 systemd 타이머로 돌린다.
호스트가 바깥으로만 요청하므로 포트를 열거나 GitHub 에 비밀을 둘 필요가 없다.

```cron
*/5 * * * * /path/to/rc-deploy/scripts/ops/deploy_pull.sh >> /path/to/rc-deploy/deploy.log 2>&1
```

동작: `origin/main` 에 새 커밋이 있고 그 커밋의 GitHub Actions `CI` 가 `success` 일 때만 배포한다.
배포 전에 `scripts/ops/backup.sh` 로 백업하고, 빨리 감기로 받은 뒤 `docker compose up -d --build --wait web`
과 헬스 체크(`/readyz`, 웹 `/login`)를 통과해야 완료로 본다. 실패하면 이전 커밋으로 되돌려 다시 올린다.
설정은 스크립트 머리말의 `DEPLOY_*` 환경 변수를 본다(비공개 저장소는 `DEPLOY_GITHUB_TOKEN` 필요).
배포 체크아웃에는 `.env` 가 있어야 하고, 호스트별 덮어쓰기는 `docker-compose.override.yml` 에 둔다.

## 8. 설정

주요 환경 변수(전체 표는 operations.md §6).

| 변수 | 기본값 | 설명 |
|---|---|---|
| `RC_DATABASE_URL` | compose 가 `postgresql://rc:***@db:5432/rc` 주입 | 미설정이면 로컬 SQLite |
| `RC_DB_PASSWORD` | **없음(필수)** | compose 의 DB 비밀번호. 미설정 시 compose 가 기동을 거부 |
| `RC_AUTH_SECRET` | **없음(필수)** | OIDC 진행 쿠키 서명 키. 모든 워커·레플리카에서 같은 값. OIDC 제공자가 설정돼 있는데 이 값이 없으면 기동을 거부한다 |
| `RC_AUTH_MODE` | 이미지·compose 에서 `server` | `local` 은 로그인 없이 모든 요청이 관리자 user 1 — 루프백 바인드에서만 허용 |
| `RC_API_ALLOW_REMOTE_LOCAL` | 미설정 | `1` 이면 local 모드를 루프백이 아닌 주소에 바인드하는 것을 허용(포트가 외부에 안 열린 경우만) |
| `RC_AUTH_ADMIN_EMAIL` | 비어 있음 | 이메일 인증을 마친 이 주소의 계정을 첫 관리자로 승격(관리자가 없을 때만) |
| `RC_PUBLIC_URL` | `http://localhost:3000` | 웹 주소(재설정 링크, OIDC 복귀) |
| `RC_AUTH_COOKIE_SECURE` | `1` | 세션 쿠키 `Secure`. `0` 은 HTTP 개발 전용 |
| `RC_SMTP_HOST` 외 `RC_SMTP_*` | 비어 있음 | 메일. 없으면 비밀번호 재설정·인증 메일 재전송 503, 이메일 인증 상태는 `unavailable` (§8.1) |
| `RC_AUTH_REQUIRE_VERIFIED_EMAIL` | `0` | `1` 이면 미인증 계정은 로그인·조회는 되고 학습 데이터 쓰기·PAT 발급이 403. SMTP 없이 `1` 이면 기동을 거부 |
| `RC_PUBLIC_CONTENT` | `0` | `1` 이면 커리큘럼(코스·모듈·레슨·자료·검색)의 GET 을 익명에 공개(ADR 0016). 진행도·노트·퀴즈·리포트·`/me`·`/admin`·`/roadmap`·모든 쓰기는 계속 세션 필요. 웹의 색인 허용도 이 값을 따른다 |
| `RC_PUBLIC_URL` (web 에도) | `http://localhost:3000` | canonical·hreflang·`sitemap.xml`·`robots.txt`·OpenGraph 의 기준 주소. api 와 web 양쪽에 같은 값을 준다 |
| `RC_OIDC_PROVIDERS` | 비어 있음 | OIDC 제공자 JSON(ADR 0010) |
| `RC_CURRICULUM_DIR` | 이미지의 `/app/curriculum` | 콘텐츠 경로 |
| `RC_DATA_DIR` | `/data` | 로컬 모드 데이터 디렉터리 |
| `RC_API_HOST` / `RC_API_PORT` | `0.0.0.0` / `8000` | 바인딩 |
| `RC_API_LOG_LEVEL` | `info` | 로그 수준 |
| `RC_API_METRICS` | `1` | `0` 이면 `/metrics` 404 |
| `RC_API_METRICS_TOKEN` | 비어 있음 | 설정하면 `/metrics` 가 해당 베어러 토큰을 요구(미설정 시 무인증) |

비밀은 환경 변수 또는 Docker secret 으로 주입하고 저장소에 커밋하지 않는다. `.env` 는 읽지도
커밋하지도 않는다(`.env.example` 만 둔다).

## 8.1 이메일 인증 켜기

SMTP 를 설정하지 않은 서버는 인증 링크를 **보낼 수 없다**. 그래서 가입 응답과 `GET /api/v1/me` 의
`email_verification` 이 `unavailable` 이 되고, 웹은 "인증 메일을 보냈습니다" 안내·미인증 배너·재전송
버튼을 아예 보여 주지 않는다(없는 메일을 기다리게 하지 않는다). 계정은 그대로 쓸 수 있다.

메일을 켜려면:

1. SMTP 변수를 넣는다. 최소 `RC_SMTP_HOST`, 보통 함께 쓰는 것:

   | 변수 | 예 | 비고 |
   |---|---|---|
   | `RC_SMTP_HOST` | `smtp.gmail.com` | 필수. 이 값이 없으면 메일 기능 전체가 꺼진다 |
   | `RC_SMTP_PORT` | `587` | 기본 587(STARTTLS) |
   | `RC_SMTP_USER` | `robot@example.org` | 인증이 필요한 경우 |
   | `RC_SMTP_PASSWORD` | 앱 비밀번호 | Docker secret 또는 환경 변수로만. 저장소에 커밋하지 않는다 |
   | `RC_SMTP_FROM` | `no-reply@example.org` | 보내는 주소. 미설정 시 `no-reply@localhost` |
   | `RC_SMTP_STARTTLS` | `1` | `0` 은 평문 SMTP(사내망 릴레이) |
   | `RC_PUBLIC_URL` | `https://learnrobotics.example.com` | 메일 안의 링크가 가리킬 웹 주소. 틀리면 링크가 열리지 않는다 |

   - **Gmail:** 2단계 인증을 켜고 *앱 비밀번호*를 발급해 `RC_SMTP_PASSWORD` 에 넣는다. 계정
     비밀번호는 거부된다. `RC_SMTP_HOST=smtp.gmail.com`, `RC_SMTP_PORT=587`,
     `RC_SMTP_USER` 는 해당 Gmail 주소, `RC_SMTP_FROM` 도 같은 주소로 둔다(다른 주소는 스팸 처리된다).
   - **일반 SMTP / 메일 발송 서비스:** 제공자가 준 호스트·포트·사용자·비밀번호를 그대로 넣고,
     `RC_SMTP_FROM` 은 그 제공자에서 검증한 도메인의 주소로 한다(SPF·DKIM).

2. 설정을 확인한다. DB 에 아무것도 쓰지 않고 한 통만 보낸다:

   ```bash
   docker compose run --rm cli api send-test-email you@example.org
   # 또는 로컬에서: uv run rc api send-test-email you@example.org
   ```

   실패하면 호스트·포트·자격 증명·방화벽을 그 순서로 확인한다. 성공하면 가입·비밀번호 재설정
   메일도 나간다.

3. API 를 다시 시작한다. 이제 `email_verification` 이 `pending` 으로 바뀌고 웹이 미인증 배너와
   "인증 메일 다시 받기" 버튼을 보여 준다. 이전에 가입한 계정은 그 버튼으로 링크를 받는다.

4. (선택) 인증을 **강제**하려면 `RC_AUTH_REQUIRE_VERIFIED_EMAIL=1` 을 켠다. 미인증 계정은 로그인과
   조회는 되지만 학습 데이터 쓰기와 PAT 발급이 403(problem+json, 재전송 안내 포함)이 된다.
   SMTP 없이 이 값을 `1` 로 두면 아무도 통과할 수 없으므로 서버가 기동을 거부한다.

## 8.2 커리큘럼 공개하기 (SEO)

공개 배포는 `RC_AUTH_MODE=server` 라서 크롤러가 로그인 화면만 본다. 커리큘럼을 검색·링크 가능하게
하려면:

1. `.env` 에 `RC_PUBLIC_CONTENT=1` 과 `RC_PUBLIC_URL=https://<공개 주소>` 를 넣는다.
   `docker-compose.yml` 이 **두 값을 api 와 web 양쪽에** 넘긴다 — api 는 익명 읽기를 열고, web 은
   그 페이지를 색인 가능하게 만들고 canonical·hreflang·사이트맵을 그 주소로 만든다. 한쪽만 받으면
   어긋나므로(web 만 → 색인 허용인데 API 가 401), compose 를 쓰지 않고 직접 띄울 때는 **두 프로세스
   모두에** 두 변수를 주어야 한다. compose 전달은
   `tests/test_server_review.py::test_compose_passes_the_public_content_settings_to_api_and_web`
   가 고정한다.
   다음 명령으로 실제로 전달되는지 확인할 수 있다(컨테이너를 띄우지 않는다):

   ```bash
   docker compose config | grep -E 'RC_PUBLIC_(CONTENT|URL)'   # api·web 각각 한 줄씩, 총 4줄
   ```
2. 확인:

   ```bash
   curl -s https://<주소>/robots.txt          # Disallow: / 가 아니어야 한다
   curl -s https://<주소>/sitemap.xml | grep -c '<url>'   # 0 이 아니어야 한다
   curl -s https://<주소>/api/v1/progress/status -o /dev/null -w '%{http_code}\n'  # 401 이어야 한다
   ```

   마지막 줄이 200 이면 **개인 데이터가 공개된 것**이므로 즉시 `RC_PUBLIC_CONTENT` 를 내린다.
3. 끄려면 `RC_PUBLIC_CONTENT=0` 으로 되돌리고 재시작한다. `robots.txt` 가 `Disallow: /` 로 돌아가고
   모든 페이지가 `noindex` 가 된다. 이미 색인된 페이지는 검색 엔진이 다시 크롤링할 때까지 남는다.

API·`/metrics`·DB 는 이 플래그와 무관하게 계속 비공개다. 브라우저는 API 를 직접 부르지 않는다.

## 9. 자주 겪는 문제

| 증상 | 원인 | 대응 |
|---|---|---|
| `api` 가 unhealthy 로 재시작 | `migrate` 실패 또는 DB 미기동 | `docker compose logs migrate db` |
| `migrate` 가 즉시 실패 | `RC_DATABASE_URL` 오류, DB 미준비 | `docker compose exec db pg_isready -U rc -d rc` |
| `/readyz` 503, `content` 실패 | 콘텐츠 로드 오류 | `docker compose run --rm cli validate` |
| `backup.sh` 가 "db 서비스가 실행 중이 아님" | 스택 미기동 | `docker compose up -d --wait db` |
| 포트 5432/8000 충돌 | 호스트에 다른 서비스 | compose 의 포트 매핑 변경 |
| 디스크 부족 | 덤프·로그 누적 | `RETENTION_DAYS` 조정, 덤프를 외부 저장소로 이전 |
