"""The vendored KaTeX copy must match its manifest (server review SRV-17 / QA-19).

`rc site build` ships these files, so a silent edit or a half-finished re-vendor would
change what every reader's browser executes. The manifest pins each file by sha256;
regenerate it with ``bash scripts/ops/vendor_katex.sh <version>``.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

ASSETS = Path(__file__).resolve().parents[1] / "src/robotics_curriculum/site/assets/katex"
MANIFEST = ASSETS / "MANIFEST.sha256"
# The advisory GHSA-238p-pmpm-9mq7 covers >=0.11.0 <0.18.2.
MINIMUM_VERSION = (0, 18, 2)


def _manifest() -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(maxsplit=1)
        entries[name.strip()] = digest
    return entries


def test_manifest_lists_every_shipped_file() -> None:
    on_disk = {
        str(path.relative_to(ASSETS))
        for path in ASSETS.rglob("*")
        if path.is_file() and path.name != MANIFEST.name
    }
    assert on_disk == set(_manifest()), "re-run scripts/ops/vendor_katex.sh to refresh the manifest"


@pytest.mark.parametrize("name", sorted(_manifest()))
def test_file_matches_its_recorded_hash(name: str) -> None:
    digest = hashlib.sha256((ASSETS / name).read_bytes()).hexdigest()
    assert digest == _manifest()[name], f"{name} differs from MANIFEST.sha256"


def test_version_is_past_the_advisory_range() -> None:
    first_line = (ASSETS / "VERSION").read_text(encoding="utf-8").splitlines()[0]
    match = re.search(r"KaTeX (\d+)\.(\d+)\.(\d+)", first_line)
    assert match, f"VERSION does not start with a KaTeX version: {first_line!r}"
    version = tuple(int(part) for part in match.groups())
    assert version >= MINIMUM_VERSION, f"KaTeX {version} is inside GHSA-238p-pmpm-9mq7"
