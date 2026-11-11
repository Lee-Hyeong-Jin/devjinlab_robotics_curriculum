# devjin_robotics_curriculum

로보틱스 커리큘럼 및 학습 보조 플랫폼 — Markdown/YAML 콘텐츠 + `rc` CLI (Phase 1, Python only).

An open-source curriculum and learning-assist platform for becoming a robotics engineer. A
staged robotics expert course (foundation, intermediate, advanced) is written as Markdown
lessons with YAML front matter, each carrying prerequisites, objectives, curated resources, and
a "how to study this stage" section. The `rc` command-line tool validates the content, tracks
your progress and study time locally, recommends the next lesson from the prerequisite graph,
writes weekly and per-module reports, and builds an offline static study site with a dashboard,
roadmap, and resource library.

Server mode adds a FastAPI server, accounts (local passwords or OIDC), PostgreSQL, and a Next.js
web frontend on top of the same core library, for a study group or a team that wants to
self-host. `harness/roadmap.yaml` tracks what is done and what is next.

## Architecture at a glance

```
curriculum/**.md ──► content loader ──┐
  (Markdown + YAML front matter)      │
                                      ├──► core library (robotics_curriculum)
.rc/progress.db  ──► progress store ──┘      content · progress · learn · report · site
  (SQLite, or PostgreSQL in server mode)              │
                                                      ├──► rc CLI ──► terminal, static site
                                                      └──► api/v1 (FastAPI) ──► web/ (Next.js)
```

The core library knows nothing about HTTP or the terminal: `progress` references lessons by id
only, `learn` is the one module that joins content and progress, and the CLI and the API are
two thin callers of the same functions. See `.claude/rules/engineering.md` for the boundaries
and `docs/platform-design.md` for the full design.

## Documentation

| Document | What it covers |
|---|---|
| [docs/PRD.md](docs/PRD.md) | Product requirements, release plan, data model |
| [docs/platform-design.md](docs/platform-design.md) | Platform design: layers, storage, auth, operations |
| [docs/curriculum/CONTENT_MODEL.md](docs/curriculum/CONTENT_MODEL.md) | Lesson schema: front matter, activities, quiz blocks |
| [docs/api/openapi.yaml](docs/api/openapi.yaml) | Generated API schema (role matrix: `docs/api/role-matrix.md`) |
| [docs/operations/RUNBOOK.md](docs/operations/RUNBOOK.md) | Running server mode: configuration, backup, restore |
| [docs/operations/RELEASE.md](docs/operations/RELEASE.md) | How a release is cut and verified |
| [docs/adr/](docs/adr/) | Architecture decisions, numbered and dated |
| [docs/HARNESS.md](docs/HARNESS.md) | How this repository is developed (graph, hooks, workflows) |

## Setup

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Run

```bash
uv run rc --help
uv run rc --lang en status                    # messages in English (or RC_LANG=en); default is Korean
uv run rc version
uv run rc validate            # defaults to ./curriculum
uv run rc show m1-vectors-matrices        # lesson summary (objectives, prerequisites) + body
uv run rc resources m1-vectors-matrices   # materials by kind + "이 단계 공부법"; or --module ID / --all
```

Progress tracking (stored in `.rc/progress.db`; override with `RC_DATA_DIR` or `rc --data-dir DIR`):

```bash
uv run rc next                                # lessons whose prerequisites are done
uv run rc start m1-vectors-matrices           # start a timer (one at a time)
uv run rc stop --note "chapter 1"             # stop it; --discard to drop it
uv run rc log m1-vectors-matrices 1h30m       # manual time: 45, 45m, 1h30m
uv run rc done m1-vectors-matrices -u 4 -m "memo"   # mark done, understanding 1-5
uv run rc status                              # per-lesson table + 오늘 복습 수 · 최근 7일 퀴즈 정답률
uv run rc quiz m1-rotation-representations    # take the lesson quiz; --only q1,q2 / --retry-wrong
uv run rc review                              # review due flashcards with SM-2; -n 10, --lesson ID, --dry-run
uv run rc roadmap --level 기초                # [x] done [>] in progress [ ] not started [-] locked; --course ID
uv run rc progress export backup.json         # JSON backup; `rc progress import FILE [--replace]`
uv run rc report weekly                       # -> reports/weekly/YYYY-Www.md; --week 2026-W46, --out PATH, --stdout
uv run rc report module m1-math-physics       # per-module progress table (stdout; --out PATH)
```

Static site (MkDocs Material: 대시보드 · 로드맵 · 모듈/레슨 · 자료실; works offline):

```bash
uv run rc site build                  # -> site/index.html (re-run to refresh progress)
uv run rc site build --out /tmp/site  # other output dir; --src DIR keeps the generated mkdocs project
uv run rc site build --serve          # live preview via `mkdocs serve` (http://127.0.0.1:8000)
```

## Server mode (accounts, API, web)

The whole stack runs from one compose file: PostgreSQL, a one-shot schema migration, the API,
and the web frontend. Secrets have no defaults, so set them first.

```bash
cp .env.example .env                         # then edit: RC_DB_PASSWORD, RC_AUTH_SECRET, ...
export RC_DB_PASSWORD=... RC_AUTH_SECRET=... # or: set -a; . ./.env; set +a
docker compose up -d --build --wait web      # db -> migrate -> api -> web
```

- Web: <http://127.0.0.1:3000> · API: <http://127.0.0.1:8000/api/v1> (docs at `/docs`)
- Liveness `/healthz`, readiness `/readyz`, Prometheus metrics `/metrics`, JSON logs with a
  request id echoed in `X-Request-ID`.
- `bash scripts/smoke.sh` brings the same stack up, checks it end to end, and tears it down.
- First admin: set `RC_AUTH_ADMIN_EMAIL` before the first start, or run
  `uv run rc api promote-admin <email>`.
- Backup and restore, including a recovery drill: [docs/operations/RUNBOOK.md](docs/operations/RUNBOOK.md).

### PostgreSQL without the full stack (optional)

Local mode needs nothing beyond SQLite. To keep progress in PostgreSQL instead (Phase 2 server
mode, `docs/adr/0007-postgres-store.md`), install the `postgres` extra (included in `uv sync`'s
dev group; otherwise `pip install 'robotics-curriculum[postgres]'`) and set `RC_DATABASE_URL`:

```bash
docker compose up -d db                 # PostgreSQL 16 on 127.0.0.1:5432; password from RC_DB_PASSWORD (dev default rc-dev-only)
export RC_DATABASE_URL=postgresql://rc:rc-dev-only@localhost:5432/rc
uv run alembic upgrade head             # create / upgrade the schema (alembic downgrade base to undo)
```

`RC_DATABASE_URL` values: `postgresql://...` → PostgreSQL, `sqlite:///path/progress.db` → that
SQLite file, unset → `.rc/progress.db`. Stores are opened through
`robotics_curriculum.progress.factory.open_store()`.

Move existing local progress to the server database (safe to re-run: lessons are upserted by
lesson id, sessions already there are skipped):

```bash
uv run rc progress transfer --to postgresql://rc:...@host:5432/rc   # local .rc/progress.db -> server
uv run rc progress transfer --from backup.json --user-id 42          # a JSON export into account 42 (--to defaults to $RC_DATABASE_URL)
uv run rc progress transfer --mode replace                           # wipe the destination first (or --mode empty)
```
Tests start a throwaway `postgres:16.13` container via Docker (or use `RC_TEST_DATABASE_URL`)
and skip the PostgreSQL cases with a reason when neither is available (`uv run pytest -rs`).

HTTP API (FastAPI, `/api/v1`; extra `api` — `uv sync` installs it in dev, `pip install 'robotics-curriculum[api]'` otherwise):

```bash
uv run rc api serve --host 127.0.0.1 --port 8000   # docs at /docs, schema at /openapi.json; env RC_API_HOST/PORT/LOG_LEVEL
RC_AUTH_MODE=server RC_AUTH_ADMIN_EMAIL=you@example.org uv run rc api serve   # accounts + login (docs/api/role-matrix.md)
```

## Lint / format

```bash
uv run ruff check . && uv run ruff format --check .
```

## Test

```bash
uv run pytest                                                        # full suite
uv run pytest tests/test_cli.py::test_version_prints_package_version  # single test
```

See `docs/adr/` for architecture decisions.

## Contributing

Contributions to code and curriculum content are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md)
for the development setup, checks, commit conventions (Conventional Commits, DCO sign-off), and
the lesson contribution flow. Everyone taking part follows the
[Code of Conduct](CODE_OF_CONDUCT.md). Changes are tracked in [CHANGELOG.md](CHANGELOG.md).

## Security

Please report vulnerabilities privately as described in [SECURITY.md](SECURITY.md), not in
public issues.

## License

Code is licensed under the [Apache License 2.0](LICENSE) (see also [NOTICE](NOTICE)).
Curriculum content in `curriculum/` is licensed under
[CC BY 4.0](curriculum/LICENSE).
