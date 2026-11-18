"""Fail on high-severity npm advisories, except the ones listed in an allowlist.

``npm audit`` has no way to ignore a single advisory, so the Security workflow pipes
``npm audit --json`` into this script. Every advisory of severity high or critical fails the gate
unless its GHSA id is in the allowlist file. An allowlist entry that no longer matches anything
also fails, so an exception cannot outlive the advisory it was written for.

Usage:
    cd web && npm audit --omit=dev --json \\
        | python3 ../scripts/ops/npm_audit_gate.py --allow audit-allowlist.txt
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

BLOCKING = frozenset({"high", "critical"})


def read_allowlist(path: Path) -> set[str]:
    """Return the GHSA ids in ``path`` (one per line; ``#`` starts a comment)."""
    ids: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = line.split("#", 1)[0].strip()
        if entry:
            ids.add(entry)
    return ids


def blocking_advisories(report: dict[str, Any]) -> dict[str, str]:
    """Map GHSA id -> "package: title" for each high/critical advisory in an npm audit report."""
    found: dict[str, str] = {}
    for name, vuln in report.get("vulnerabilities", {}).items():
        for via in vuln.get("via", []):
            # A string entry points at another package whose own entry carries the advisory.
            if not isinstance(via, dict) or via.get("severity") not in BLOCKING:
                continue
            ghsa = str(via.get("url", "")).rstrip("/").rsplit("/", 1)[-1] or str(via.get("source"))
            found[ghsa] = f"{name}: {via.get('title', '')}"
    return found


def evaluate(report: dict[str, Any], allowed: set[str]) -> tuple[dict[str, str], set[str]]:
    """Return (advisories that block, allowlist entries that match nothing)."""
    found = blocking_advisories(report)
    blocking = {ghsa: text for ghsa, text in found.items() if ghsa not in allowed}
    return blocking, allowed - set(found)


def main(argv: list[str] | None = None) -> int:
    """Read an npm audit JSON report on stdin; exit 1 if the gate fails, 2 on unusable input."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--allow", type=Path, required=True, help="allowlist file of GHSA ids")
    args = parser.parse_args(argv)
    try:
        report = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"npm audit gate: stdin is not JSON ({exc})", file=sys.stderr)
        return 2
    if not isinstance(report, dict) or "vulnerabilities" not in report:
        # An npm error report (registry down, bad lockfile) must not pass as "no findings".
        print("npm audit gate: not an npm audit report", file=sys.stderr)
        return 2
    blocking, stale = evaluate(report, read_allowlist(args.allow))
    for ghsa, text in sorted(blocking.items()):
        print(f"BLOCKING {ghsa} {text}")
    for ghsa in sorted(stale):
        print(f"STALE allowlist entry {ghsa}: the advisory no longer applies, remove it")
    if blocking or stale:
        return 1
    print("npm audit gate: no high or critical advisories outside the allowlist")
    return 0


if __name__ == "__main__":
    sys.exit(main())
