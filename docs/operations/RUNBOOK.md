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

```bash
docker compose up -d --wait api     # db -> migrate -> api, 전부 healthy 될 때까지 대기
docker compose ps                   # 상태 확인
docker compose logs -f api          # JSON 로그 추적
docker compose down                 # 정지 (볼륨 유지)
docker compose down -v              # 정지 + 데이터 삭제 (주의)
docker compose run --rm cli validate   # 콘텐츠 검증 같은 일회성 작업
```

스모크 점검: `bash scripts/smoke.sh` — 스택을 올려 `/healthz`, `/readyz`, `/version`,
`/openapi.json`, `/api/v1/courses`, 요청 ID 에코, JSON 로그를 확인하고 내려놓는다.
`KEEP_UP=1` 을 주면 띄운 상태로 남긴다. 같은 스크립트가 CI 의 `smoke` 잡에서 돈다.

## 3. 상태 점검

| 확인 | 명령 | 정상 |
|---|---|---|
| 프로세스 생존 | `curl -fsS localhost:8000/healthz` | `{"status":"ok"}` |
| 요청 처리 준비 | `curl -fsS localhost:8000/readyz` | `{"status":"ready", ...}`, DB·콘텐츠 색인 각각 `ok: true` |
| 버전 | `curl -fsS localhost:8000/version` | 배포한 버전 |
| 메트릭 | `curl -fsS localhost:8000/metrics` | Prometheus 텍스트. `RC_API_METRICS=0` 이면 404 |
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

## 8. 설정

주요 환경 변수(전체 표는 operations.md §6).

| 변수 | 기본값 | 설명 |
|---|---|---|
| `RC_DATABASE_URL` | compose 가 `postgresql://rc:***@db:5432/rc` 주입 | 미설정이면 로컬 SQLite |
| `RC_DB_PASSWORD` | `rc-dev-only` | compose 의 DB 비밀번호. **운영에서는 반드시 교체** |
| `RC_CURRICULUM_DIR` | 이미지의 `/app/curriculum` | 콘텐츠 경로 |
| `RC_DATA_DIR` | `/data` | 로컬 모드 데이터 디렉터리 |
| `RC_API_HOST` / `RC_API_PORT` | `0.0.0.0` / `8000` | 바인딩 |
| `RC_API_LOG_LEVEL` | `info` | 로그 수준 |
| `RC_API_METRICS` | `1` | `0` 이면 `/metrics` 404 |

비밀은 환경 변수 또는 Docker secret 으로 주입하고 저장소에 커밋하지 않는다. `.env` 는 읽지도
커밋하지도 않는다(`.env.example` 만 둔다).

## 9. 자주 겪는 문제

| 증상 | 원인 | 대응 |
|---|---|---|
| `api` 가 unhealthy 로 재시작 | `migrate` 실패 또는 DB 미기동 | `docker compose logs migrate db` |
| `migrate` 가 즉시 실패 | `RC_DATABASE_URL` 오류, DB 미준비 | `docker compose exec db pg_isready -U rc -d rc` |
| `/readyz` 503, `content` 실패 | 콘텐츠 로드 오류 | `docker compose run --rm cli validate` |
| `backup.sh` 가 "db 서비스가 실행 중이 아님" | 스택 미기동 | `docker compose up -d --wait db` |
| 포트 5432/8000 충돌 | 호스트에 다른 서비스 | compose 의 포트 매핑 변경 |
| 디스크 부족 | 덤프·로그 누적 | `RETENTION_DAYS` 조정, 덤프를 외부 저장소로 이전 |
