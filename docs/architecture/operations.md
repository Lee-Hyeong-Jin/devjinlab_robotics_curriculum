# 운영 설계 (Operations)

| 항목 | 내용 |
|---|---|
| 버전 | 0.1 (2026-11-11, 설계 문서 v0.4의 §9를 분리) |
| 적용 범위 | 서버 모드(API 서버 + PostgreSQL + 웹). 로컬 모드는 `rc` 한 바이너리와 `.rc/rc.db` 파일만 있으면 된다 |
| 상위 문서 | `docs/platform-design.md` §1(3계층), `docs/architecture/auth.md` |

## 1. 배포 토폴로지

```mermaid
flowchart LR
  U[브라우저 / rc CLI] --> P[reverse proxy: Caddy 또는 nginx, TLS]
  P --> W[web (Phase 2)]
  P --> A[api: uvicorn + FastAPI]
  A --> D[(db: PostgreSQL 16)]
  A -.선택.-> R[(redis: 세션·속도 제한)]
  M[migrate: alembic upgrade head] --> D
  S[site: rc build → 정적 HTML] --> P
```

- 1단계는 **단일 호스트 Docker Compose**. 2단계(수요가 생기면) Kubernetes용 Helm 차트를 같은 이미지로 제공한다.
- API 서버는 무상태이므로 `api` 레플리카를 늘리기만 하면 된다. 상태는 PostgreSQL(과 선택적 Redis)에만 있다.

### `compose.yaml` 골격

```yaml
services:
  db:
    image: postgres:16
    environment: { POSTGRES_DB: rc, POSTGRES_USER: rc, POSTGRES_PASSWORD_FILE: /run/secrets/db_password }
    volumes: [dbdata:/var/lib/postgresql/data]
    healthcheck: { test: ["CMD-SHELL", "pg_isready -U rc -d rc"], interval: 10s, timeout: 5s, retries: 5 }
    secrets: [db_password]
  migrate:
    image: ghcr.io/<org>/robotics-curriculum-api:${TAG}
    command: ["alembic", "upgrade", "head"]
    env_file: .env
    depends_on: { db: { condition: service_healthy } }
  api:
    image: ghcr.io/<org>/robotics-curriculum-api:${TAG}
    command: ["uvicorn", "robotics_curriculum_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]   # 소스는 api/ 디렉터리
    env_file: .env
    depends_on: { migrate: { condition: service_completed_successfully } }
    healthcheck: { test: ["CMD", "curl", "-fsS", "http://localhost:8000/readyz"], interval: 15s, timeout: 3s, retries: 3 }
    volumes: [./curriculum:/app/curriculum:ro]
    read_only: true
    tmpfs: [/tmp]
    user: "10001:10001"
  web:
    image: ghcr.io/<org>/robotics-curriculum-web:${TAG}   # Phase 2
    depends_on: [api]
  proxy:
    image: caddy:2
    ports: ["80:80", "443:443"]
    volumes: [./deploy/Caddyfile:/etc/caddy/Caddyfile:ro, caddydata:/data, ./site:/srv/site:ro]
volumes: { dbdata: {}, caddydata: {} }
secrets: { db_password: { file: ./secrets/db_password } }
```

- 이미지는 멀티스테이지 빌드(uv로 의존성 설치 → distroless/python slim), 루트 아닌 사용자, 읽기 전용 루트 파일시스템.
- 콘텐츠(`curriculum/`)는 읽기 전용으로 마운트한다. 게시는 CI가 이미지에 콘텐츠를 구워 넣거나(권장) 볼륨 갱신으로 한다.

## 2. 헬스체크

| 엔드포인트 | 의미 | 검사 |
|---|---|---|
| `GET /healthz` | liveness — 프로세스가 살아 있음 | 즉시 200 |
| `GET /readyz` | readiness — 트래픽을 받을 준비 | DB `SELECT 1`, Alembic 리비전이 `head`와 일치, 콘텐츠 로드 성공, (Redis 켜졌으면) PING. 하나라도 실패하면 503 + 실패 항목 |
| `GET /version` | 빌드 정보 | git SHA, 이미지 태그, 콘텐츠 커밋 SHA |

## 3. 구조화 로깅

- `structlog` → JSON 한 줄/이벤트. 필수 필드: `ts`, `level`, `event`, `request_id`, `user_id`(있으면), `method`, `path`, `status`, `duration_ms`.
- `request_id`는 요청 헤더 `X-Request-ID`를 받거나 생성해 응답 헤더로 되돌려 준다. 감사 로그(`audit_log.request_id`)와 연결된다.
- PII 금지: 이메일·비밀번호·토큰은 절대 로그에 쓰지 않는다. 로거 프로세서에서 키 이름 기반 마스킹(`password`, `token`, `authorization`).
- 레벨: 운영 기본 `INFO`, 요청 로그는 `INFO`, 헬스체크 경로는 로그 제외.

## 4. 메트릭과 추적

- `GET /metrics` (Prometheus 텍스트 형식, `prometheus-fastapi-instrumentator`). 내부망에서만 노출.
- 핵심 지표: 요청 수·지연(p50/p95/p99, 경로별), 5xx 비율, DB 풀 사용량, 로그인 성공/실패 수, 활성 세션 수, 일일 활성 학습자(DAU), 레슨 완료 수.
- 알림 기준(초기): 5xx 비율 > 1% (5분), p95 > 500 ms (10분), readiness 실패, 디스크 80%.
- 추적: OpenTelemetry SDK + OTLP exporter(선택, `OTEL_EXPORTER_OTLP_ENDPOINT` 설정 시). Grafana + Prometheus + Loki(로그) + Tempo(추적)를 `deploy/observability/compose.yaml`로 제공.

## 5. 백업과 복구

| 대상 | 방법 | 주기·보존 | 복구 목표 |
|---|---|---|---|
| PostgreSQL | `pg_dump -Fc` → 객체 저장소(S3 호환), 서버 측 암호화 | 매일 02:00, 30일 보존 + 월 1회 1년 | RPO 24h, RTO 4h (PRD 7절 자체 호스팅 기본값) |
| 콘텐츠 | git 저장소가 원본 | — | 즉시 |
| 정적 사이트 | 재빌드 가능 | — | 분 단위 |
| 로컬 모드 SQLite | `rc export` JSON 또는 `.rc/rc.db` 복사 | 사용자 책임, 문서화 | — |

- 복구 리허설: 릴리스 전 1회(PRD 7절) 백업에서 빈 환경으로 복원해 `/readyz`와 샘플 쿼리를 확인하고 결과를 `docs/ops/restore-drills.md`에 기록.
- 업그레이드 전 스냅샷: `alembic upgrade` 전에 자동 `pg_dump`.

## 6. 설정 (12-factor)

설정은 전부 환경 변수. `pydantic-settings`로 읽고 시작 시 검증한다. `.env.example`을 저장소에 두고 `.env`는 무시한다.

| 변수 | 예 | 설명 |
|---|---|---|
| `RC_MODE` | `server` | `local` 이면 인증 없이 `user_id="1"` |
| `DATABASE_URL` | `postgresql+asyncpg://rc:***@db:5432/rc` | 로컬 모드는 `sqlite+aiosqlite:///.rc/rc.db` |
| `SECRET_KEY` | 32바이트 이상 랜덤 | 세션·CSRF 서명 |
| `PASSWORD_PEPPER` | 선택 | Argon2id 페퍼 |
| `SESSION_TTL_DAYS` | `14` | |
| `OIDC_PROVIDERS` | JSON 배열 | `docs/architecture/auth.md` §2.2 |
| `OIDC_*_CLIENT_SECRET` | 시크릿 | 제공자별 |
| `SMTP_URL` | `smtps://user:***@smtp.example.com:465` | 인증 메일 |
| `PUBLIC_BASE_URL` | `https://learn.example.org` | 콜백·메일 링크 |
| `CORS_ORIGINS` | `https://learn.example.org` | |
| `CONTENT_DIR` | `/app/curriculum` | |
| `LOG_LEVEL` | `INFO` | |
| `METRICS_ENABLED` | `true` | |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | 선택 | |
| `RATE_LIMIT_LOGIN` | `5/minute` | |

## 7. 시크릿

- 저장소에 시크릿 없음(`gitleaks` pre-commit + CI).
- 로컬 개발: `.env`(무시됨). 운영: Docker secrets 파일 마운트 또는 SOPS(age)로 암호화한 `secrets.enc.yaml`을 배포 시 복호화.
- 회전: `SECRET_KEY`는 쉼표로 여러 개를 두어(현재, 이전) 무중단 회전. DB 비밀번호·OIDC 클라이언트 시크릿은 분기 1회 회전, 절차를 `docs/ops/runbooks/rotate-secrets.md`에 둔다.
- 애플리케이션은 시크릿을 로그·에러 응답·`/version`에 절대 노출하지 않는다. 관리자 설정 화면은 마스킹 값만 보여 준다.

## 8. CI/CD와 릴리스

- GitHub Actions: `lint`(ruff, mypy) → `test`(pytest, 커버리지 80% 게이트) → `contract`(OpenAPI 스냅샷 diff + schemathesis) → `security`(pip-audit, gitleaks, trivy 이미지 스캔) → `build`(이미지 `ghcr.io/<org>/…:<sha>`, SBOM 첨부, cosign 서명) → `deploy`(태그 푸시 시 compose 호스트에 `docker compose pull && up -d`).
- 버전: SemVer. `main`은 항상 배포 가능. 릴리스 노트는 Conventional Commits에서 생성.
- 마이그레이션: 하위 호환(expand → migrate → contract) 원칙. 컬럼 삭제는 두 릴리스에 나눈다.

## 9. 오픈소스 프로젝트 운영

- 라이선스: PRD 14절 기본값 — 코드 **Apache-2.0**, 콘텐츠(`curriculum/`) **CC BY 4.0**(`curriculum/LICENSE`). 사용자 최종 확정 대기. 거버넌스 상세(DCO, 행동 강령, SECURITY.md, 버저닝, RFC)는 PRD 14절이 정본이며 여기서는 반복하지 않는다.
- 저장소 파일: `LICENSE`, `README.md`(설치 3가지: pipx 로컬 모드, Docker Compose, 소스), `CONTRIBUTING.md`(DCO sign-off, 브랜치·커밋 규칙, 콘텐츠 기여 가이드), `CODE_OF_CONDUCT.md`(Contributor Covenant), `SECURITY.md`, `.github/ISSUE_TEMPLATE/`(버그·콘텐츠 오류·기능), `CODEOWNERS`.
- 콘텐츠 기여: 레슨 PR은 `rc validate` CI 통과가 필수. 리뷰어는 `author` 역할과 무관하게 GitHub 권한으로 관리.
- 공개 로드맵: GitHub Projects. 외부 기여자가 잡기 좋은 이슈는 `good first issue` 라벨.
