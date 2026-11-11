# ADR 0001: Phase 1 stack — Python only

- Status: Accepted
- Date: 2026-11-11

## Context

The platform (see `docs/PRD.md`) needs a curriculum content model, a content validator,
progress tracking, and reports. The first and only user for now is the repository owner,
so operational simplicity matters more than a rich UI.

## Decision

Phase 1 is Python only:

- Python 3.12, dependencies and virtualenv managed with `uv`
- `ruff` for lint and format, `pytest` for tests
- `typer` for the `rc` CLI, `pydantic` v2 for content/progress schemas, `pyyaml` for frontmatter
- Content lives in `curriculum/` as Markdown + YAML; the user-facing surface is the CLI
  plus a static site generated from the content later in Phase 1

Next.js / FastAPI (interactive web app, API server) are deferred to Phase 2.

## Rationale

- Solo user: no auth, no server, no deployment to operate
- Lowest ops burden: one toolchain (`uv`), one language, local files (SQLite later)
- Content first: the curriculum and its validator are the core value; a web UI can be
  layered on once the content model is stable

## Consequences

- No interactive dashboard in Phase 1; reports and progress are CLI/file based
- Data model should still reserve `user_id` so Phase 2 can add multi-user support
