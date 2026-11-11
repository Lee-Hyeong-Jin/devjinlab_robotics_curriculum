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
- Lesson translations as sibling files (`<lesson>.<lang>.md`, ADR 0012): text only, so the
  prerequisite graph stays single-sourced. The loader, `rc validate`, the API
  (`Accept-Language`, with `lang` and `available_languages` in the response) and
  `rc site build --lang` use a translation when there is one and fall back to the language the
  lesson was written in.
- Accessibility checks for the generated site (document language, heading levels, table
  headers, skip link, image alt text, contrast of the project's own colours); the
  in-progress status colour was darkened to meet WCAG AA on white.
- Message catalogues for Korean and English (`src/robotics_curriculum/i18n/locales/*.yaml`,
  ADR 0011): the CLI picks a language with `--lang` or `RC_LANG`, `rc site build --lang`
  translates the site chrome, and the API localizes problem titles from `Accept-Language`.
  Lesson content stays in the language it was written in. A few CLI lines that were English
  regardless of locale (the unlock list, the prerequisite warning) are now Korean by default.
- Quizzes and spaced repetition (P1-2): ` ```quiz ` blocks in lesson bodies (single, multiple,
  true/false, short answer) validated by `rc validate`; `rc quiz <lesson>` grades in the
  terminal and turns wrong answers and `concept` questions into flashcards; `rc review`
  schedules them with SM-2 (ADR 0005); progress schema v2 (cards, card_state, reviews,
  quiz_attempts, quiz_runs, activity_progress) included in JSON export/import; quiz accuracy
  and review counts in the weekly report and `rc status`; quiz questions on lesson pages with
  answers folded into `<details>`.
- Prerequisite roadmap with done / in-progress / locked states and next-lesson recommendation.
- Offline static study site (MkDocs Material): dashboard, roadmap, module and lesson pages,
  resource library.
- HTTP API (`rc api serve`, optional extra `api`): FastAPI app under `/api/v1` for courses,
  modules, lessons, resources, progress (status, next, start, stop, log, done), weekly and
  module reports, and progress export; `/healthz`, `/readyz`, `/version`; RFC 9457
  problem+json errors, `X-Request-ID`, JSON logs, and an OpenAPI snapshot test.
- PostgreSQL progress store for server mode (optional extra `postgres`: SQLAlchemy 2 Core +
  psycopg 3) with Alembic migrations, backend selection via `RC_DATABASE_URL` (unset keeps the
  local SQLite file), `rc progress transfer` to move local SQLite or JSON-export data into
  PostgreSQL (merge without duplicates, `--user-id` to assign a server account), and a `db`
  service (PostgreSQL 16) in the Compose file.
- Server-mode accounts (`RC_AUTH_MODE=server`): email + Argon2id passwords, login throttling,
  server-side session cookies with CSRF protection, personal access tokens with scopes, roles
  learner/author/admin, per-user progress, password reset and email verification by mail,
  account export and deletion, admin user management and an audit log; security headers.
- OIDC login (Authorization Code + PKCE) for providers listed in `RC_OIDC_PROVIDERS`, with
  account linking and `/api/v1/me/identities`.
- Prometheus metrics at `/metrics` (request counts, latency histogram, in-flight requests,
  database pool usage); `RC_API_METRICS=0` turns it off.
- `docs/api/openapi.yaml` is generated from the served API (plus `x-planned` routes) and a test
  keeps them identical.
- Engineering scaffolding: Apache-2.0 license for code, CC BY 4.0 for curriculum content,
  contribution guide, Code of Conduct, security policy, issue and PR templates, Dependabot,
  GitHub Actions CI and release workflows, strict mypy, coverage gate, pre-commit hooks,
  Dockerfile and Compose file.
- Development harness: graph spec (`harness/graph.md`), roadmap state (`harness/roadmap.yaml`),
  verification gate (`scripts/harness/check.sh`), Claude Code hooks, agents, and workflows
  (see `docs/HARNESS.md`).
- Architecture decision records 0001–0004 (Phase 1 stack, harness, SQLite progress store,
  MkDocs static site).
- `rc --verbose/-v` turns on debug logging to stderr; library modules log through the
  standard `logging` module (never personal data such as study notes).
- `rc progress import --allow-unknown` and `rc site build --force`: escape hatches for the
  new input and output-path checks listed under Security.

### Changed

- Engineering rules (`.claude/rules/engineering.md`): coverage gate is core-library line+branch
  80%; every commit carries a DCO `Signed-off-by`; large design changes go through `docs/rfcs/`
  then an ADR; only Apache-2.0-compatible dependencies; CHANGELOG is mandatory; server-mode
  observability and OWASP ASVS L2 checks; multi-session agent operating rules.
- Roadmap acceptance criteria for P1-2 and P2-1 … P2-5 now cite PRD appendix C IDs; P1-2 uses
  SM-2 and depends on P1-5, P2-1 depends on P1-2.
- `docs/HARNESS.md` documents how hooks behave in worktree sessions.

### Security

- Server review fixes (`docs/reviews/2026-11-11-server-review.md`): the compose stack and the api
  image run in server mode with required secrets and no default database password; local mode
  refuses non-loopback binds; the bootstrap admin is promoted only after email verification
  (or with `rc api promote-admin`); password-reset requests are rate limited and only the newest
  reset link works; error bodies no longer show server paths; denied requests and admin reads
  are audited; account deletion anonymizes the user's audit entries; api containers run with a
  read-only root, no capabilities and `no-new-privileges`.
- `.github/workflows/security.yml`: CodeQL (Python, security-and-quality) and pip-audit of the
  locked runtime dependencies on every PR, on pushes to `main`, and weekly. Any known
  vulnerability in a runtime dependency fails the job.
- The static site no longer passes curriculum text through to HTML unchanged: titles,
  summaries, objectives, tags, activity and resource names are HTML-escaped (including the
  nav titles and `site_name` in `mkdocs.yml`, which the theme writes out verbatim), rendered
  pages are cleaned with an `nh3` allowlist, and each page carries a Content-Security-Policy
  meta tag. A resource `url` that is not `http(s)` is shown as plain text instead of a link.
- `rc site build` refuses an `--out` or `--src` directory that holds files it did not write
  (no `.rc-site` marker), and refuses the working directory, the repository root and `$HOME`
  outright; `--force` allows the first case. mkdocs empties both directories, so a mistyped
  path used to delete unrelated files.
- Content loading rejects files that leave the content root once symlinks are resolved,
  reports unreadable or non-UTF-8 files instead of raising, checks prerequisite cycles
  iteratively (a long chain used to exhaust the stack) and requires ids to be unique across
  courses. Every command validates the curriculum, not only `rc validate`.
- `rc progress import` validates the export against the database invariants and refuses
  lesson ids that are not in the curriculum unless `--allow-unknown` is passed; study
  durations are capped at one day. The progress database is opened in WAL mode with a busy
  timeout, its files are created owner-only, and storage failures (such as a locked
  database) are reported as `error: ...` instead of a traceback.
