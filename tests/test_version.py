"""The package version must be the one pyproject.toml declares.

`rc version`, the API's `/version` and the release tag all come from `__version__`, which is
read back from the installed distribution. If the environment is stale or someone bumps one
place and not the other, a release would ship the wrong number; this catches that.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from robotics_curriculum import __version__

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def test_version_matches_pyproject() -> None:
    declared = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["version"]
    assert __version__ == declared, (
        f"installed {__version__} but pyproject declares {declared}; run `uv sync`"
    )
