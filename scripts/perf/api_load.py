#!/usr/bin/env python3
"""Load the API's read endpoints and report per-endpoint latency percentiles.

PRD §7 ("성능 / 서버") asks for p95 ≤ 300 ms on reads. This measures it without adding a
dependency: asyncio plus the ``httpx`` client the package already ships (``auth/oidc.py``).
It is a baseline tool, not a benchmark harness — it reports what this machine did, and the
numbers are only comparable against runs recorded the same way.

Usage (local mode needs no credentials)::

    RC_AUTH_MODE=local RC_DATA_DIR=/tmp/rc uv run rc api serve --port 8098 &
    uv run python scripts/perf/api_load.py --base-url http://127.0.0.1:8098

Server mode needs a caller. Pass a personal access token with ``read:progress``::

    uv run python scripts/perf/api_load.py --base-url ... --token rcp_...

Options worth knowing: ``--concurrency`` (parallel clients), ``--duration`` (seconds per
endpoint), ``--warmup`` (requests thrown away first, so the content index and connection
pool are hot), ``--format md|json``.

Writing the result down: ``--format md`` prints the table that goes into
``docs/operations/perf-baseline.md``.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import platform
import statistics
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime

import httpx

#: Read endpoints worth a baseline: the ones every screen waits on. Written as
#: (label, path) so a path with an id keeps a readable label.
DEFAULT_ENDPOINTS: tuple[tuple[str, str], ...] = (
    ("courses", "/api/v1/courses"),
    ("course", "/api/v1/courses/robotics-expert"),
    ("module", "/api/v1/modules/m1-math-physics"),
    ("lesson", "/api/v1/lessons/m1-coordinate-transforms"),
    ("resources", "/api/v1/resources"),
    ("progress.status", "/api/v1/progress/status"),
    ("progress.next", "/api/v1/progress/next"),
    ("progress.lessons", "/api/v1/progress/lessons"),
    ("reports.weekly", "/api/v1/reports/weekly"),
    ("healthz", "/healthz"),
)

#: PRD §7: p95 of a read must stay under this.
TARGET_P95_MS = 300.0


@dataclass(slots=True)
class Samples:
    """Latencies (ms) and failures for one endpoint."""

    label: str
    path: str
    latencies: list[float] = field(default_factory=list)
    statuses: dict[int, int] = field(default_factory=dict)
    errors: dict[str, int] = field(default_factory=dict)

    @property
    def count(self) -> int:
        return len(self.latencies)

    @property
    def failures(self) -> int:
        bad = sum(n for status, n in self.statuses.items() if status >= 400)
        return bad + sum(self.errors.values())

    def percentile(self, fraction: float) -> float:
        """Nearest-rank percentile, so the value is one that actually happened."""
        if not self.latencies:
            return math.nan
        ordered = sorted(self.latencies)
        rank = max(0, math.ceil(fraction * len(ordered)) - 1)
        return ordered[rank]

    @property
    def summary(self) -> dict[str, float | int | str]:
        return {
            "label": self.label,
            "path": self.path,
            "requests": self.count,
            "failures": self.failures,
            "min_ms": round(min(self.latencies), 1) if self.latencies else math.nan,
            "p50_ms": round(self.percentile(0.50), 1),
            "p95_ms": round(self.percentile(0.95), 1),
            "p99_ms": round(self.percentile(0.99), 1),
            "max_ms": round(max(self.latencies), 1) if self.latencies else math.nan,
            "mean_ms": round(statistics.fmean(self.latencies), 1) if self.latencies else math.nan,
        }


async def _hammer(client: httpx.AsyncClient, path: str, deadline: float, samples: Samples) -> None:
    """Request ``path`` back to back until ``deadline`` (a ``perf_counter`` value)."""
    while time.perf_counter() < deadline:
        started = time.perf_counter()
        try:
            response = await client.get(path)
        except httpx.HTTPError as exc:
            samples.errors[type(exc).__name__] = samples.errors.get(type(exc).__name__, 0) + 1
            continue
        elapsed_ms = (time.perf_counter() - started) * 1000
        samples.latencies.append(elapsed_ms)
        samples.statuses[response.status_code] = samples.statuses.get(response.status_code, 0) + 1


async def measure(
    client: httpx.AsyncClient,
    label: str,
    path: str,
    *,
    concurrency: int,
    duration: float,
    warmup: int,
) -> Samples:
    """Warm up, then hammer one endpoint from ``concurrency`` clients for ``duration`` seconds."""
    for _ in range(warmup):
        try:
            await client.get(path)
        except httpx.HTTPError:
            pass  # reported by the measured run; a cold start may legitimately fail
    samples = Samples(label=label, path=path)
    deadline = time.perf_counter() + duration
    await asyncio.gather(*(_hammer(client, path, deadline, samples) for _ in range(concurrency)))
    return samples


async def run(args: argparse.Namespace) -> list[Samples]:
    headers = {"Accept": "application/json"}
    if args.token:
        headers["Authorization"] = f"Bearer {args.token}"
    limits = httpx.Limits(
        max_connections=args.concurrency, max_keepalive_connections=args.concurrency
    )
    endpoints = _endpoints(args.only)
    results: list[Samples] = []
    async with httpx.AsyncClient(
        base_url=args.base_url.rstrip("/"),
        headers=headers,
        limits=limits,
        timeout=args.timeout,
    ) as client:
        for label, path in endpoints:
            print(f"  {label} ...", file=sys.stderr, flush=True)
            results.append(
                await measure(
                    client,
                    label,
                    path,
                    concurrency=args.concurrency,
                    duration=args.duration,
                    warmup=args.warmup,
                )
            )
    return results


def _endpoints(only: Sequence[str] | None) -> tuple[tuple[str, str], ...]:
    if not only:
        return DEFAULT_ENDPOINTS
    wanted = set(only)
    chosen = tuple(pair for pair in DEFAULT_ENDPOINTS if pair[0] in wanted)
    missing = wanted - {label for label, _ in DEFAULT_ENDPOINTS}
    if missing:
        raise SystemExit(f"unknown endpoint label(s): {', '.join(sorted(missing))}")
    return chosen


def render_markdown(results: Sequence[Samples], args: argparse.Namespace) -> str:
    rows = [
        "| 엔드포인트 | 요청 | 실패 | p50 | p95 | p99 | max |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for samples in results:
        s = samples.summary
        mark = "" if float(s["p95_ms"]) <= TARGET_P95_MS else " ⚠️"
        rows.append(
            f"| `{s['label']}` | {s['requests']} | {s['failures']} | {s['p50_ms']} ms | "
            f"**{s['p95_ms']} ms**{mark} | {s['p99_ms']} ms | {s['max_ms']} ms |"
        )
    worst = max((float(r.summary["p95_ms"]) for r in results), default=math.nan)
    header = (
        f"- 측정: {datetime.now(UTC).isoformat(timespec='seconds')} · "
        f"동시 {args.concurrency} · 엔드포인트당 {args.duration}s · "
        f"{platform.python_version()} on {platform.system()} {platform.machine()}\n"
        f"- 목표(PRD §7): 읽기 p95 ≤ {TARGET_P95_MS:.0f} ms · "
        f"최악 p95 {worst:.1f} ms\n"
    )
    return header + "\n" + "\n".join(rows) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="API base URL.")
    parser.add_argument("--token", default=None, help="PAT with read:progress (server mode).")
    parser.add_argument("--concurrency", type=int, default=16, help="Parallel clients.")
    parser.add_argument("--duration", type=float, default=3.0, help="Seconds per endpoint.")
    parser.add_argument("--warmup", type=int, default=5, help="Discarded requests per endpoint.")
    parser.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout (s).")
    parser.add_argument("--only", nargs="*", default=None, help="Endpoint labels to measure.")
    parser.add_argument("--format", choices=("md", "json"), default="md", help="Output format.")
    args = parser.parse_args(argv)

    print(f"loading {args.base_url}", file=sys.stderr)
    results = asyncio.run(run(args))
    if not results:
        raise SystemExit("no endpoint measured")

    if args.format == "json":
        print(json.dumps([r.summary for r in results], indent=2, ensure_ascii=False))
    else:
        print(render_markdown(results, args), end="")

    failures = sum(r.failures for r in results)
    over = [r.label for r in results if float(r.summary["p95_ms"]) > TARGET_P95_MS]
    if failures:
        print(f"warning: {failures} failed request(s)", file=sys.stderr)
    if over:
        print(f"warning: p95 over {TARGET_P95_MS:.0f} ms: {', '.join(over)}", file=sys.stderr)
    # A non-zero exit would make this unusable in a loop while a regression is investigated,
    # so the warnings above are the signal and the exit code only reports a broken run.
    return 1 if failures and all(r.count == 0 for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
