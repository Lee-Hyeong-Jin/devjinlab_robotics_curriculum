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
