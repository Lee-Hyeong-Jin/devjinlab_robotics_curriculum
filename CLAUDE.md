# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

로보틱스 커리큘럼 및 학습 보조 플랫폼 (Robotics curriculum and learning-assist platform).
Two modes share one Python core library (`src/robotics_curriculum`):
- **Local mode** — Markdown/YAML content under `curriculum/`, the `rc` CLI, SQLite progress in
  `.rc/progress.db`, and an offline MkDocs static site.
- **Server mode** — FastAPI (`/api/v1`), accounts (local passwords or OIDC), PostgreSQL, and the
  Next.js frontend in `web/`, all started from `docker-compose.yml`.

All roadmap milestones (P0-1 … P2-6) are done; new work is follow-up on a finished platform.

Key documents:
- `docs/PRD.md` — product requirements (FR-1 … FR-10, release plan, data model).
- `docs/platform-design.md` — platform design (layers, storage, auth, operations).
- `docs/architecture/{auth,frontend,operations}.md` — implementation rules per area.
- `docs/curriculum/CONTENT_MODEL.md` — content schema (the pydantic models in `content/models.py` win).
- `docs/api/openapi.yaml` + `docs/api/role-matrix.md` — API contract and who may call what.
- `docs/operations/RUNBOOK.md`, `docs/operations/RELEASE.md` — running and releasing server mode.
- `docs/HARNESS.md` — how this repo is developed (graph-engineering harness, hooks, workflows).
- `harness/graph.md` — the development graph (nodes, gates, loop nodes).
- `docs/adr/` — architecture decisions. Write one with `/adr` for any hard-to-reverse choice.

## Commands

Requires Python 3.12 and `uv`. Always run Python through `uv run`.

```bash
uv sync                                                # install deps (incl. dev group)
uv run rc --help                                       # CLI entry point
uv run rc validate                                     # validate ./curriculum
uv run ruff check . && uv run ruff format --check .    # lint + format check
uv run mypy                                            # strict type check of src/ (targets in [tool.mypy])
uv run pytest                                          # full test suite
uv run pytest --cov                                    # tests + coverage gate (fail_under in [tool.coverage.report])
uv run pytest tests/test_cli.py::test_version_prints_package_version   # single test
uv run pytest -rs                                      # show why PostgreSQL cases skipped (needs Docker or RC_TEST_DATABASE_URL)
uv run rc site build --strict --out /tmp/site          # static site build as CI runs it
uv run rc api serve                                    # API in local mode (no login); RC_AUTH_MODE=server for accounts
uv run alembic upgrade head                            # PostgreSQL schema (needs RC_DATABASE_URL)
bash scripts/harness/check.sh [--quick]                # the verification gate: Python + web/ + rc validate + site build; --quick = Python lint/types only
uv run pre-commit install                              # enable git hooks; `uv run pre-commit run --all-files` runs them all
docker build -t robotics-curriculum:local .            # container image (non-root; default `rc --help`)
export RC_DB_PASSWORD=dev RC_AUTH_SECRET=dev            # compose has no secret defaults (SRV-06)
docker compose run --rm cli validate                   # run any rc subcommand in the container
docker compose up -d --build --wait web                # db -> migrate -> api -> web (bash scripts/smoke.sh)
uv build                                               # sdist + wheel into dist/ (release.yml does this on v* tags)
python3 -I scripts/harness/roadmap.py summary|next|get <id>|set <id> <status> [note]   # roadmap state
```

Web frontend (run inside `web/`, Node >= 22):

```bash
npm ci && npm run dev                                  # http://localhost:3000; needs `uv run rc api serve` running
npm run lint && npm run typecheck && npm test && npm run build   # the web gate (plus `npm run format:check` in CI)
npx vitest run src/path/to/file.test.tsx               # single unit/component test
npm run api:types                                      # regenerate src/lib/api/schema.d.ts from docs/api/openapi.yaml
E2E_BASE_URL=... npx playwright test smoke             # needs a local-mode API
E2E_AUTH=1 E2E_BASE_URL=... npx playwright test journey   # needs a server-mode API (see web/README.md)
```

Slash commands (project skills): `/graph-status`, `/verify`, `/verify-fix`, `/review-loop`,
`/milestone <id>`, `/platform-loop [n]`, `/adr <title>`, `/new-lesson <path> "<title>"`.
The workflow-backed ones (`/milestone`, `/platform-loop`, `/verify-fix`, `/review-loop`) spawn
many agents; only the user launches them.

## Architecture

- `src/robotics_curriculum/` — the core library; the CLI and the API are two thin callers of it.
  - `content/` loads and validates `curriculum/`; `progress/` stores progress behind one
    `ProgressStore` contract (SQLite `store.py`, PostgreSQL `postgres.py`, opened via
    `progress.factory.open_store()` from `RC_DATABASE_URL`). Neither knows the other.
  - `learn/` is the only module joining content and progress (quiz, SM-2 review, stats);
    `report/` and `site/` build on it. `roadmap.py` is the prerequisite graph and next-lesson logic.
  - `auth/` (Argon2id accounts, sessions, OIDC, mailer) and `api/` (FastAPI app, routers,
    settings from `RC_*` env) exist only for server mode and need the `api` extra.
    `RC_AUTH_MODE=local` means no login and a fixed user 1; `server` turns on accounts.
  - `i18n/` — message catalog (`locales/ko.yaml`, `en.yaml`); Korean is the default, `--lang en`
    or `RC_LANG=en` switches. User-facing CLI strings go through the catalog, not literals.
  - `cli.py` mounts the sub-apps (`progress`, `report`, `site`, `api`), each defined in its
    package's own `cli.py`.
- `web/` — Next.js App Router + next-intl (`messages/ko.json`, `en.json`). It never imports the
  Python core; all data comes from the API through `src/lib/api/` (types generated from
  `docs/api/openapi.yaml`). An API schema change must update `openapi.yaml`,
  `tests/snapshots/openapi.json`, and `web/src/lib/api/schema.d.ts` together — CI fails on drift.
- `curriculum/` — content source of truth: `Course > Module > Lesson > Activity`. Two courses:
  `robotics-expert` (m1–m10) and `robotics-research` (with a `papers.yaml` registry, ADR 0014).
  Lessons are Markdown with YAML frontmatter; English lives in sibling files (`x.en.md`,
  `x.en.yaml`, `module.en.yaml`, `course.en.yaml`; ADR 0012). The code schema wins over
  `docs/curriculum/LESSON_TEMPLATE.md`.
- `tests/` — pytest for the core, API, and content. PostgreSQL cases start a throwaway container
  (testcontainers) and skip with a reason when Docker is unavailable.
- `scripts/ops/` (backup, restore, restore drill), `scripts/smoke.sh` (compose end-to-end),
  `alembic.ini` + `progress/migrations/` (PostgreSQL schema).
- `harness/` — development graph spec (`graph.md`) and state (`roadmap.yaml`: milestones with
  `todo | in_progress | done | blocked`, dependencies, acceptance criteria).
- `scripts/harness/` — hook scripts and the verification gate. `check.sh` auto-detects the stack
  from `pyproject.toml` / `package.json`.
- `.claude/workflows/` — graph executors (`platform-loop` → `milestone` → inline loops
  implement/verify, review/fix, acceptance; `verify-fix` and `review-loop` standalone).
- `.claude/agents/` — node executors: planner, implementer, verifier, reviewer, acceptance-tester,
  integrator, plus curriculum-designer, research-scout.
- `.claude/rules/` — engineering rules (global) and content rules (`curriculum/**`).
- Hooks (`.claude/settings.json`): SessionStart injects branch/roadmap status; PreToolUse guards
  destructive Bash; PostToolUse formats `.py` with ruff; Stop runs `check.sh --quick` when there
  are uncommitted code changes and blocks the turn on failure.

## Engineering standards

- Licenses: code Apache-2.0 (`LICENSE`, `NOTICE`); `curriculum/` content CC BY 4.0 (`curriculum/LICENSE`).
- Type hints are required in `src/`; `mypy` runs in strict mode and must pass (CI, `check.sh`, pre-commit).
- Coverage gate: line+branch coverage must stay at or above `fail_under` in `pyproject.toml` (80).
- Commits follow Conventional Commits and carry a DCO `Signed-off-by:` line for external
  contributions (`git commit -s`); see `CONTRIBUTING.md`.
- CI (`.github/workflows/ci.yml`) mirrors `check.sh` and adds the compose smoke test, the web
  build, the API-types drift check, two Playwright + axe legs, and a backup/restore drill.
- Security issues are reported privately per `SECURITY.md` (GitHub advisories, 90-day disclosure);
  never discuss them in public issues or commit messages.
- User-visible changes get a line under `## [Unreleased]` in `CHANGELOG.md`.

## Working rules

- Work in a branch or worktree, never commit to `main`; the user pushes and merges.
- Every behavior change ships with a test; never weaken, skip, or delete tests to pass the gate.
- Loops have an exit condition and a cap; after 3 identical failures stop and report.
- Milestone work: `/milestone <id>` writes `docs/specs/<id>.md`, commits on the branch, updates
  `harness/roadmap.yaml`, and writes `reports/milestones/<id>.md`.
- Do not read or commit `.env`; config examples go in `.env.example`.
- Commit messages: `type(scope): summary`; milestone commits use the milestone id as scope.

## Notes

- `../my_first_webots_project` is a separate, unrelated project. Do not read its layout or
  commands into this repo. Simulator integration is out of scope for this platform.
- `research_notes/` holds the user's research (written by other sessions); treat it as source
  material and cite paths rather than copying.
- `harness/roadmap.yaml` is the record of what shipped; add a new milestone there before starting
  milestone-sized work.
- Web env vars go in `web/.env.local` (the harness blocks writes to `.env*`); see `web/README.md`.
