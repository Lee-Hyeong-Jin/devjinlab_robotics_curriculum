"""Run a lesson example in its own interpreter (``rc example --run`` and the test suite).

Kept apart from :mod:`content.examples`, which stays pure: this is the one place that starts a
process.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RunResult:
    returncode: int
    stdout: str
    stderr: str


EXAMPLE_TIMEOUT_SECONDS = 60


def run_example(code: str, *, timeout: float = EXAMPLE_TIMEOUT_SECONDS) -> RunResult:
    """Run one example in a fresh interpreter, in an empty directory, and collect its output.

    The interpreter is this one (so it sees the same installed packages) started in isolated
    mode: the example cannot pick up modules from the caller's directory or environment
    variables. A run that exceeds ``timeout`` counts as a failure.
    """
    with tempfile.TemporaryDirectory() as work:
        script = Path(work) / "example.py"
        script.write_text(code, encoding="utf-8")
        try:
            done = subprocess.run(  # noqa: S603 - argument list, our own interpreter
                [sys.executable, "-I", str(script)],
                cwd=work,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return RunResult(124, "", f"timed out after {timeout:g} s\n")
    return RunResult(done.returncode, done.stdout, done.stderr)
