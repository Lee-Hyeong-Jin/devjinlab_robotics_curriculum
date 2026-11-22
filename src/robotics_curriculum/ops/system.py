"""Readings of the machine the API runs on: load, memory, disk, temperature, uptime.

The parsers are pure (text in, numbers out) so they can be tested with captured files; the
``read_*`` functions do the I/O and return ``None`` for anything this host does not expose.
Inside a container ``/proc`` and ``/sys`` show the host, and the disk is the data volume.
"""

from __future__ import annotations

import os
import shutil
import threading
from dataclasses import dataclass
from pathlib import Path

PROC = Path("/proc")
SYS = Path("/sys")


@dataclass(frozen=True, slots=True)
class Memory:
    total_bytes: int
    available_bytes: int
    swap_total_bytes: int = 0
    swap_free_bytes: int = 0

    @property
    def used_ratio(self) -> float:
        return 0.0 if self.total_bytes <= 0 else 1.0 - self.available_bytes / self.total_bytes

    @property
    def swap_used_ratio(self) -> float | None:
        """Share of swap in use; ``None`` on a machine without swap."""
        if self.swap_total_bytes <= 0:
            return None
        return 1.0 - self.swap_free_bytes / self.swap_total_bytes


@dataclass(frozen=True, slots=True)
class FileDescriptors:
    """Open file descriptors of the API process against its limit."""

    open: int
    limit: int | None

    @property
    def used_ratio(self) -> float | None:
        return None if not self.limit else self.open / self.limit


@dataclass(frozen=True, slots=True)
class Disk:
    path: str
    total_bytes: int
    used_bytes: int
    free_bytes: int

    @property
    def used_ratio(self) -> float:
        return 0.0 if self.total_bytes <= 0 else self.used_bytes / self.total_bytes


@dataclass(frozen=True, slots=True)
class Temperature:
    sensor: str
    celsius: float


@dataclass(frozen=True, slots=True)
class CpuTimes:
    """Cumulative jiffies from the first line of ``/proc/stat``."""

    total: int
    idle: int


def parse_loadavg(text: str) -> tuple[float, float, float] | None:
    """The 1, 5 and 15 minute load averages from ``/proc/loadavg``."""
    parts = text.split()
    try:
        return float(parts[0]), float(parts[1]), float(parts[2])
    except (IndexError, ValueError):
        return None


def parse_meminfo(text: str) -> Memory | None:
    """Total and available memory from ``/proc/meminfo`` (values there are in kB)."""
    values: dict[str, int] = {}
    for line in text.splitlines():
        name, _, rest = line.partition(":")
        fields = rest.split()
        if fields and fields[0].isdigit():
            values[name.strip()] = int(fields[0]) * 1024
    total = values.get("MemTotal")
    # MemAvailable is the kernel's own estimate of what a new program could get; MemFree
    # alone ignores reclaimable cache and makes a healthy machine look full.
    available = values.get("MemAvailable", values.get("MemFree"))
    if total is None or available is None:
        return None
    return Memory(
        total_bytes=total,
        available_bytes=min(available, total),
        swap_total_bytes=values.get("SwapTotal", 0),
        swap_free_bytes=values.get("SwapFree", 0),
    )


def parse_fd_limit(limits_text: str) -> int | None:
    """The soft "Max open files" limit from ``/proc/<pid>/limits``."""
    for line in limits_text.splitlines():
        if line.startswith("Max open files"):
            fields = line.split()
            # "Max open files  <soft>  <hard>  files"
            if len(fields) >= 5 and fields[3].isdigit():
                return int(fields[3])
    return None


def parse_uptime(text: str) -> float | None:
    """Seconds since boot from ``/proc/uptime``."""
    try:
        return float(text.split()[0])
    except (IndexError, ValueError):
        return None


def parse_cpu_times(text: str) -> CpuTimes | None:
    """Total and idle jiffies from the aggregate ``cpu`` line of ``/proc/stat``."""
    for line in text.splitlines():
        if line.startswith("cpu "):
            try:
                fields = [int(value) for value in line.split()[1:]]
            except ValueError:
                return None
            if len(fields) < 4:
                return None
            idle = fields[3] + (fields[4] if len(fields) > 4 else 0)  # idle + iowait
            return CpuTimes(total=sum(fields[:8]), idle=idle)
    return None


def cpu_usage(before: CpuTimes | None, after: CpuTimes | None) -> float | None:
    """Share of CPU time spent working between two samples (0–1), or ``None`` without two."""
    if before is None or after is None:
        return None
    total = after.total - before.total
    if total <= 0:
        return None
    return max(0.0, min(1.0, 1.0 - (after.idle - before.idle) / total))


def parse_rss_bytes(status_text: str) -> int | None:
    """Resident memory of a process from ``/proc/<pid>/status``."""
    for line in status_text.splitlines():
        if line.startswith("VmRSS:"):
            fields = line.split()
            if len(fields) >= 2 and fields[1].isdigit():
                return int(fields[1]) * 1024
    return None


def parse_millidegrees(text: str) -> float | None:
    """A sysfs temperature (millidegrees Celsius) as degrees; implausible values are dropped."""
    try:
        celsius = int(text.strip()) / 1000.0
    except ValueError:
        return None
    # Disconnected sensors report 0, negative values or absurd ones.
    return celsius if 1.0 <= celsius <= 150.0 else None


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def read_loadavg(proc: Path = PROC) -> tuple[float, float, float] | None:
    text = _read(proc / "loadavg")
    return parse_loadavg(text) if text else None


def read_memory(proc: Path = PROC) -> Memory | None:
    text = _read(proc / "meminfo")
    return parse_meminfo(text) if text else None


def read_uptime(proc: Path = PROC) -> float | None:
    text = _read(proc / "uptime")
    return parse_uptime(text) if text else None


def read_cpu_times(proc: Path = PROC) -> CpuTimes | None:
    text = _read(proc / "stat")
    return parse_cpu_times(text) if text else None


def read_process_rss(proc: Path = PROC) -> int | None:
    text = _read(proc / "self" / "status")
    return parse_rss_bytes(text) if text else None


def read_file_descriptors(proc: Path = PROC) -> FileDescriptors | None:
    try:
        count = sum(1 for _ in (proc / "self" / "fd").iterdir())
    except OSError:
        return None
    limits = _read(proc / "self" / "limits")
    return FileDescriptors(open=count, limit=parse_fd_limit(limits) if limits else None)


def read_disk(path: Path) -> Disk | None:
    """Usage of the filesystem holding ``path``."""
    try:
        usage = shutil.disk_usage(path)
    except OSError:
        return None
    return Disk(
        path=str(path), total_bytes=usage.total, used_bytes=usage.used, free_bytes=usage.free
    )


def read_temperatures(sys_root: Path = SYS) -> list[Temperature]:
    """Every temperature sensor the kernel exposes, hottest first.

    Two sources are read: ``hwmon`` (CPU package, NVMe, …, with a chip name and often a
    label) and ``thermal`` zones. A reading that appears in both is listed once.
    """
    found: dict[str, float] = {}
    hwmon = sys_root / "class" / "hwmon"
    try:
        chips = sorted(hwmon.iterdir())
    except OSError:
        chips = []
    for chip in chips:
        name = (_read(chip / "name") or chip.name).strip()
        try:
            inputs = sorted(chip.glob("temp*_input"))
        except OSError:
            continue
        for sensor in inputs:
            celsius = parse_millidegrees(_read(sensor) or "")
            if celsius is None:
                continue
            label = (_read(sensor.with_name(sensor.name.replace("_input", "_label"))) or "").strip()
            key = f"{name} {label}".strip() if label else name
            # Several inputs of one chip without labels: keep the hottest under the chip name.
            found[key] = max(found.get(key, 0.0), celsius)
    thermal = sys_root / "class" / "thermal"
    try:
        zones = sorted(thermal.glob("thermal_zone*"))
    except OSError:
        zones = []
    for zone in zones:
        celsius = parse_millidegrees(_read(zone / "temp") or "")
        if celsius is None:
            continue
        kind = (_read(zone / "type") or zone.name).strip()
        if kind not in found:
            found[kind] = celsius
    return sorted(
        (Temperature(sensor=name, celsius=value) for name, value in found.items()),
        key=lambda reading: (-reading.celsius, reading.sensor),
    )


def cpu_count() -> int:
    return os.cpu_count() or 1


class CpuSampler:
    """Remembers the previous ``/proc/stat`` sample so a reading can report usage since then.

    The first reading has nothing to compare with and reports ``None``; after that the figure
    covers the time between two looks at the page, which is what the person looking wants.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._previous: CpuTimes | None = None

    def usage(self, proc: Path = PROC) -> float | None:
        current = read_cpu_times(proc)
        with self._lock:
            previous, self._previous = self._previous, current
        return cpu_usage(previous, current)
