# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

로보틱스 커리큘럼 및 학습 보조 플랫폼 (Robotics curriculum and learning-assist platform).
Phase 1 is a single Python stack: Markdown/YAML content under `curriculum/` plus the `rc` CLI,
later a static site. Node/Next.js is deferred to Phase 2 or later.

Key documents:
- `docs/PRD.md` — product requirements (FR-1 … FR-10, release plan, data model).
- `docs/platform-design.md` — platform design (written by the design session; may not exist yet on this branch).
- `docs/curriculum/CONTENT_MODEL.md` — content schema (M1 work in progress; may not exist yet).
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
uv run pytest                                          # full test suite
uv run pytest tests/test_cli.py::test_version_prints_package_version   # single test
bash scripts/harness/check.sh [--quick]                # the verification gate (lint+format+tests; --quick skips tests)
python3 -I scripts/harness/roadmap.py summary|next|get <id>|set <id> <status> [note]   # roadmap state
```

Slash commands (project skills): `/graph-status`, `/verify`, `/verify-fix`, `/review-loop`,
`/milestone <id>`, `/platform-loop [n]`, `/adr <title>`, `/new-lesson <path> "<title>"`.
The workflow-backed ones (`/milestone`, `/platform-loop`, `/verify-fix`, `/review-loop`) spawn
many agents; only the user launches them.

## Architecture

- `src/robotics_curriculum/` — package (Typer CLI in `cli.py`; content loader, validators, and
  progress storage land here per the roadmap). Tests in `tests/`.
- `curriculum/` — content source of truth: `Track > Module > Lesson > Activity`, lessons are
  Markdown with YAML frontmatter (see `docs/curriculum/LESSON_TEMPLATE.md`; the code schema wins
  once it exists).
- `harness/` — development graph spec (`graph.md`) and state (`roadmap.yaml`: milestones with
  `todo | in_progress | done | blocked`, dependencies, acceptance criteria).
- `scripts/harness/` — hook scripts and the verification gate. `check.sh` auto-detects the stack
  from `pyproject.toml` / `package.json`.
- `.claude/workflows/` — graph executors (`platform-loop` → `milestone` → inline loops
  implement/verify, review/fix, acceptance; `verify-fix` and `review-loop` standalone).
- `.claude/agents/` — node executors: planner, implementer, verifier, reviewer, acceptance-tester,
  integrator, plus curriculum-designer, robotics-sim-engineer, research-scout.
- `.claude/rules/` — engineering rules (global) and content rules (`curriculum/**`).
- Hooks (`.claude/settings.json`): SessionStart injects branch/roadmap status; PreToolUse guards
  destructive Bash; PostToolUse formats `.py` with ruff; Stop runs `check.sh --quick` when there
  are uncommitted code changes and blocks the turn on failure.

## Working rules

- Work in a branch or worktree, never commit to `main`; the user pushes and merges.
- Every behavior change ships with a test; never weaken, skip, or delete tests to pass the gate.
- Loops have an exit condition and a cap; after 3 identical failures stop and report.
- Milestone work: `/milestone <id>` writes `docs/specs/<id>.md`, commits on the branch, updates
  `harness/roadmap.yaml`, and writes `reports/milestones/<id>.md`.
- Do not read or commit `.env`; config examples go in `.env.example`.
- Commit messages: `type(scope): summary`; milestone commits use the milestone id as scope.

## Notes

- `../my_first_webots_project` is a separate project used as a reference for Webots labs
  (worlds/, controllers/, protos/). Read it, never modify it, and do not apply its layout here.
- `research_notes/` holds the user's research (written by other sessions); treat it as source
  material and cite paths rather than copying.
- `harness/roadmap.yaml` milestone contents are placeholders derived from the PRD and will change
  as design sessions conclude; only the schema is fixed.
