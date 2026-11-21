"""The npm audit gate used by the Security workflow (scripts/ops/npm_audit_gate.py)."""

from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ops" / "npm_audit_gate.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("npm_audit_gate", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gate = _load()


def _advisory(ghsa: str, severity: str) -> dict[str, object]:
    return {
        "source": 1,
        "title": f"title of {ghsa}",
        "url": f"https://github.com/advisories/{ghsa}",
        "severity": severity,
    }


def _report(*advisories: dict[str, object]) -> dict[str, object]:
    return {
        "vulnerabilities": {
            "leaf": {"severity": "high", "via": list(advisories)},
            "parent": {"severity": "high", "via": ["leaf"]},
        }
    }


def _run(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, stdin: str, allow: str = "") -> int:
    allowlist = tmp_path / "allow.txt"
    allowlist.write_text(allow, encoding="utf-8")
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin))
    result: int = gate.main(["--allow", str(allowlist)])
    return result


def test_high_advisory_blocks(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    report = json.dumps(_report(_advisory("GHSA-aaaa-bbbb-cccc", "high")))
    assert _run(monkeypatch, tmp_path, report) == 1


def test_allowlisted_advisory_passes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    report = json.dumps(_report(_advisory("GHSA-aaaa-bbbb-cccc", "high")))
    allow = "# reason\nGHSA-aaaa-bbbb-cccc  # trailing comment\n"
    assert _run(monkeypatch, tmp_path, report, allow) == 0


def test_allowlist_does_not_hide_another_advisory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = json.dumps(
        _report(
            _advisory("GHSA-aaaa-bbbb-cccc", "high"), _advisory("GHSA-dddd-eeee-ffff", "critical")
        )
    )
    assert _run(monkeypatch, tmp_path, report, "GHSA-aaaa-bbbb-cccc\n") == 1
    out = capsys.readouterr().out
    assert "BLOCKING GHSA-dddd-eeee-ffff" in out
    assert "BLOCKING GHSA-aaaa-bbbb-cccc" not in out


def test_moderate_advisory_does_not_block(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    report = json.dumps(_report(_advisory("GHSA-aaaa-bbbb-cccc", "moderate")))
    assert _run(monkeypatch, tmp_path, report) == 0


def test_stale_allowlist_entry_fails(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    report = json.dumps({"vulnerabilities": {}})
    assert _run(monkeypatch, tmp_path, report, "GHSA-aaaa-bbbb-cccc\n") == 1


@pytest.mark.parametrize("stdin", ["not json", json.dumps({"error": {"code": "ENOLOCK"}})])
def test_unusable_input_is_an_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, stdin: str
) -> None:
    assert _run(monkeypatch, tmp_path, stdin) == 2


def test_repository_allowlist_parses() -> None:
    allowed = gate.read_allowlist(SCRIPT.parents[2] / "web" / "audit-allowlist.txt")
    # Every entry is a GHSA id; the comments around it carry the reason and the date.
    assert all(entry.startswith("GHSA-") for entry in allowed)
