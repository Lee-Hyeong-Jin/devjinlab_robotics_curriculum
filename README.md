# devjin_robotics_curriculum

로보틱스 커리큘럼 및 학습 보조 플랫폼 — Markdown/YAML 콘텐츠 + `rc` CLI (Phase 1, Python only).

## Setup

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Run

```bash
uv run rc --help
uv run rc version
uv run rc validate            # defaults to ./curriculum
```

Progress tracking (stored in `.rc/progress.db`; override with `RC_DATA_DIR` or `rc --data-dir DIR`):

```bash
uv run rc next                                # lessons whose prerequisites are done
uv run rc start m1-vectors-matrices           # start a timer (one at a time)
uv run rc stop --note "chapter 1"             # stop it; --discard to drop it
uv run rc log m1-vectors-matrices 1h30m       # manual time: 45, 45m, 1h30m
uv run rc done m1-vectors-matrices -u 4 -m "memo"   # mark done, understanding 1-5
uv run rc status                              # per-lesson table
uv run rc progress export backup.json         # JSON backup; `rc progress import FILE [--replace]`
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
