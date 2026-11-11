# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `rc` CLI (Typer): `version`, `validate`, `show`, `resources`, `status`, `start`, `stop`,
  `log`, `done`, `next`, `roadmap`, `progress export|import`, `report weekly|module`,
  `site build`.
- Content model: Course > Module > Lesson > Activity as Markdown with YAML front matter, with a
  loader and validator (required fields, unknown prerequisites, prerequisite cycles, resource
  URL format).
- Robotics expert course content under `curriculum/robotics-expert/` (modules M1–M6, M8, M10 so
  far), with "이 단계 공부법" sections and resource lists for each lesson.
- Local progress tracking in SQLite (`.rc/progress.db`) behind a store interface, with JSON
  export and import.
- Weekly and per-module Markdown reports.
- Prerequisite roadmap with done / in-progress / locked states and next-lesson recommendation.
- Offline static study site (MkDocs Material): dashboard, roadmap, module and lesson pages,
  resource library.
- HTTP API (`rc api serve`, optional extra `api`): FastAPI app under `/api/v1` for courses,
  modules, lessons, resources, progress (status, next, start, stop, log, done), weekly and
  module reports, and progress export; `/healthz`, `/readyz`, `/version`; RFC 9457
  problem+json errors, `X-Request-ID`, JSON logs, and an OpenAPI snapshot test.
- Engineering scaffolding: Apache-2.0 license for code, CC BY 4.0 for curriculum content,
  contribution guide, Code of Conduct, security policy, issue and PR templates, Dependabot,
  GitHub Actions CI and release workflows, strict mypy, coverage gate, pre-commit hooks,
  Dockerfile and Compose file.
- Development harness: graph spec (`harness/graph.md`), roadmap state (`harness/roadmap.yaml`),
  verification gate (`scripts/harness/check.sh`), Claude Code hooks, agents, and workflows
  (see `docs/HARNESS.md`).
- Architecture decision records 0001–0004 (Phase 1 stack, harness, SQLite progress store,
  MkDocs static site).

### Changed

- Engineering rules (`.claude/rules/engineering.md`): coverage gate is core-library line+branch
  80%; every commit carries a DCO `Signed-off-by`; large design changes go through `docs/rfcs/`
  then an ADR; only Apache-2.0-compatible dependencies; CHANGELOG is mandatory; server-mode
  observability and OWASP ASVS L2 checks; multi-session agent operating rules.
- Roadmap acceptance criteria for P1-2 and P2-1 … P2-5 now cite PRD appendix C IDs; P1-2 uses
  SM-2 and depends on P1-5, P2-1 depends on P1-2.
- `docs/HARNESS.md` documents how hooks behave in worktree sessions.

### Security

- `.github/workflows/security.yml`: CodeQL (Python, security-and-quality) and pip-audit of the
  locked runtime dependencies on every PR, on pushes to `main`, and weekly. Any known
  vulnerability in a runtime dependency fails the job.
- PostgreSQL progress store for server mode (optional extra `postgres`: SQLAlchemy 2 Core +
  psycopg 3) with Alembic migrations, backend selection via `RC_DATABASE_URL` (unset keeps the
  local SQLite file), `rc progress transfer` to move local SQLite or JSON-export data into
  PostgreSQL (merge without duplicates, `--user-id` to assign a server account), and a `db`
  service (PostgreSQL 16) in the Compose file.
