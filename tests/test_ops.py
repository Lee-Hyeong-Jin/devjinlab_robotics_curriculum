"""Monitoring pipeline (P3-2, ADR 0017): pure aggregation, system parsers, store, recorder."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import create_engine

from robotics_curriculum.ops import system
from robotics_curriculum.ops.recorder import Recorder, Retention
from robotics_curriculum.ops.store import OpsStore, StatDelta
from robotics_curriculum.ops.traffic import (
    BUCKET_COUNT,
    LATENCY_BOUNDS_MS,
    OTHER_PATH,
    RequestTotals,
    apdex,
    error_budget,
    hour_bucket,
    is_bot,
    latency_bucket,
    level,
    normalize_path,
    quantile,
    referrer_host,
    status_class,
    visitor_hash,
)

T0 = datetime(2026, 11, 22, 10, 30, tzinfo=UTC)

# -- traffic -------------------------------------------------------------------------------


def test_hour_bucket_and_status_class() -> None:
    kst = T0.astimezone(tz=UTC).replace(tzinfo=UTC)
    assert hour_bucket(kst) == datetime(2026, 11, 22, 10, 0, tzinfo=UTC)
    assert [status_class(s) for s in (200, 204, 301, 404, 429, 500, 503, 999)] == [
        2,
        2,
        3,
        4,
        4,
        5,
        5,
        5,
    ]


def test_latency_buckets_cover_every_duration() -> None:
    assert latency_bucket(0.2) == 0
    assert latency_bucket(5) == 0  # an edge belongs to its own bucket
    assert latency_bucket(5.01) == 1
    assert latency_bucket(10_000) == len(LATENCY_BOUNDS_MS) - 1
    assert latency_bucket(60_000) == BUCKET_COUNT - 1


def test_quantiles_interpolate_inside_the_bucket() -> None:
    histogram = [0] * BUCKET_COUNT
    histogram[latency_bucket(40)] = 100  # everything between 25 and 50 ms
    assert quantile(histogram, 0.5) == pytest.approx(37.5)
    assert quantile(histogram, 1.0) == pytest.approx(50.0)
    histogram[latency_bucket(800)] = 100  # and as many between 500 and 1000 ms
    assert quantile(histogram, 0.5) == pytest.approx(50.0)
    assert 500 < (quantile(histogram, 0.95) or 0) <= 1000
    assert quantile([0] * BUCKET_COUNT, 0.95) is None
    overflow = [0] * BUCKET_COUNT
    overflow[-1] = 3
    assert quantile(overflow, 0.99) == LATENCY_BOUNDS_MS[-1]


def test_request_totals_measure_availability_by_server_errors_only() -> None:
    totals = RequestTotals()
    hist = [0] * BUCKET_COUNT
    hist[2] = 90
    totals.add(2, 90, 1800.0, 24.0, hist)
    hist4 = [0] * BUCKET_COUNT
    hist4[1] = 8
    totals.add(4, 8, 64.0, 9.0, hist4)
    hist5 = [0] * BUCKET_COUNT
    hist5[8] = 2
    totals.add(5, 2, 4000.0, 2400.0, hist5)
    assert totals.count == 100
    assert (totals.client_errors, totals.server_errors) == (8, 2)
    # A wrong password is not downtime: only the two 5xx count against the service.
    assert totals.success_rate == pytest.approx(0.98)
    assert totals.mean_ms == pytest.approx(58.64)
    assert totals.duration_ms_max == 2400.0
    assert RequestTotals().success_rate is None


def test_apdex_counts_tolerating_requests_as_half() -> None:
    histogram = [0] * BUCKET_COUNT
    histogram[latency_bucket(100)] = 80  # satisfied
    histogram[latency_bucket(900)] = 10  # tolerating
    histogram[latency_bucket(4000)] = 10  # frustrated
    assert apdex(histogram) == pytest.approx(0.85)
    assert apdex([0] * BUCKET_COUNT) is None


def test_error_budget() -> None:
    budget = error_budget(100_000, 50, 0.999)
    assert budget.allowed_failures == pytest.approx(100.0)
    assert budget.availability == pytest.approx(0.9995)
    assert budget.consumed_ratio == pytest.approx(0.5)
    assert error_budget(100_000, 250, 0.999).consumed_ratio == pytest.approx(2.5)
    assert error_budget(0, 0, 0.999).consumed_ratio is None


def test_levels() -> None:
    assert [level(v, 0.8, 0.9) for v in (None, 0.5, 0.8, 0.89, 0.9, 1.0)] == [
        "ok",
        "ok",
        "warning",
        "warning",
        "critical",
        "critical",
    ]


# -- visits --------------------------------------------------------------------------------


def test_bots_are_recognised() -> None:
    chrome = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"
    )
    assert not is_bot(chrome)
    assert not is_bot(
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) Mobile/15E148 KAKAOTALK"
    )
    for agent in (
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Mozilla/5.0 (compatible; Yeti/1.1; +https://naver.me/spd)",
        "facebookexternalhit/1.1",
        "curl/8.5.0",
        "python-requests/2.32",
        "",
        None,
    ):
        assert is_bot(agent), agent


def test_paths_are_normalized_to_a_bounded_set() -> None:
    assert normalize_path("/") == "/"
    assert normalize_path("/roadmap?course=x") == "/roadmap"
    assert normalize_path("/guide/") == "/guide"
    assert normalize_path("/modules/m1-math-physics") == "/modules/m1-math-physics"
    assert normalize_path("/modules/m1/l1/quiz#top") == "/modules/m1/l1/quiz"
    # Anything else is one row, so made-up addresses cannot fill the table.
    for path in ("/admin/users/7", "/wp-login.php", "/modules/a/b/c/d", "/modules/<script>", ""):
        assert normalize_path(path) == OTHER_PATH, path


def test_referrer_keeps_the_host_only() -> None:
    assert referrer_host("https://www.google.com/search?q=learn+robotics") == "google.com"
    assert referrer_host("https://search.naver.com/search.naver?query=x") == "search.naver.com"
    assert referrer_host("https://learn.example.org/roadmap", ["learn.example.org"]) is None
    for value in (None, "", "android-app://com.example", "not a url", "https://bad host/"):
        assert referrer_host(value) is None, value


def test_visitor_hash_is_stable_within_a_day_and_changes_the_next() -> None:
    secret = b"k" * 32
    day = date(2026, 11, 22)
    same = visitor_hash(secret, day, "198.51.100.7", "UA")
    assert same == visitor_hash(secret, day, "198.51.100.7", "UA")
    assert len(same) == 16
    assert same != visitor_hash(secret, day + timedelta(days=1), "198.51.100.7", "UA")
    assert same != visitor_hash(secret, day, "198.51.100.8", "UA")
    assert same != visitor_hash(b"x" * 32, day, "198.51.100.7", "UA")
    # The address is not in the value.
    assert "198" not in same


# -- system parsers ------------------------------------------------------------------------

MEMINFO = """MemTotal:       16043124 kB
MemFree:         1651852 kB
MemAvailable:    4032080 kB
SwapTotal:       2097148 kB
SwapFree:        1048574 kB
"""


def test_system_parsers() -> None:
    assert system.parse_loadavg("0.14 0.22 0.43 1/2136 481\n") == (0.14, 0.22, 0.43)
    assert system.parse_loadavg("garbage") is None
    memory = system.parse_meminfo(MEMINFO)
    assert memory is not None
    assert memory.total_bytes == 16043124 * 1024
    assert memory.used_ratio == pytest.approx(1 - 4032080 / 16043124)
    assert memory.swap_used_ratio == pytest.approx(0.5, abs=1e-3)
    assert system.parse_meminfo("MemTotal: 10 kB\n") is None
    no_swap = system.parse_meminfo("MemTotal: 100 kB\nMemAvailable: 40 kB\n")
    assert no_swap is not None and no_swap.swap_used_ratio is None
    assert system.parse_uptime("12345.67 99999.00\n") == pytest.approx(12345.67)
    assert system.parse_rss_bytes("Name:\tpython\nVmRSS:\t  148418 kB\n") == 148418 * 1024
    assert (
        system.parse_fd_limit(
            "Max open files            1024                 524288               files\n"
        )
        == 1024
    )
    assert system.parse_millidegrees("44000\n") == 44.0
    # A disconnected sensor reports nonsense; it is dropped, not shown as 0 °C.
    assert system.parse_millidegrees("0") is None
    assert system.parse_millidegrees("-273000") is None
    assert system.parse_millidegrees("x") is None


def test_cpu_usage_between_two_samples() -> None:
    before = system.parse_cpu_times("cpu  100 0 50 800 50 0 0 0 0 0\ncpu0 1 2 3 4\n")
    after = system.parse_cpu_times("cpu  160 0 80 900 60 0 0 0 0 0\n")
    assert before is not None and after is not None
    # 200 jiffies passed, 110 of them idle or waiting on I/O.
    assert system.cpu_usage(before, after) == pytest.approx(0.45)
    assert system.cpu_usage(None, after) is None
    assert system.cpu_usage(after, after) is None


def test_temperatures_come_from_hwmon_and_thermal_zones(tmp_path: Path) -> None:
    hwmon = tmp_path / "class" / "hwmon"
    (hwmon / "hwmon0").mkdir(parents=True)
    (hwmon / "hwmon0" / "name").write_text("coretemp\n")
    (hwmon / "hwmon0" / "temp1_input").write_text("43000\n")
    (hwmon / "hwmon0" / "temp1_label").write_text("Package id 0\n")
    (hwmon / "hwmon0" / "temp2_input").write_text("0\n")  # dead sensor
    (hwmon / "hwmon1").mkdir()
    (hwmon / "hwmon1" / "name").write_text("nvme\n")
    (hwmon / "hwmon1" / "temp1_input").write_text("35850\n")
    zone = tmp_path / "class" / "thermal" / "thermal_zone0"
    zone.mkdir(parents=True)
    (zone / "type").write_text("acpitz\n")
    (zone / "temp").write_text("91000\n")
    readings = system.read_temperatures(tmp_path)
    assert [(r.sensor, r.celsius) for r in readings] == [
        ("acpitz", 91.0),
        ("coretemp Package id 0", 43.0),
        ("nvme", 35.85),
    ]
    assert system.read_temperatures(tmp_path / "missing") == []


def test_readers_return_none_where_the_host_exposes_nothing(tmp_path: Path) -> None:
    assert system.read_loadavg(tmp_path) is None
    assert system.read_memory(tmp_path) is None
    assert system.read_uptime(tmp_path) is None
    assert system.read_process_rss(tmp_path) is None
    assert system.read_file_descriptors(tmp_path) is None
    assert system.read_disk(tmp_path / "missing") is None
    disk = system.read_disk(tmp_path)
    assert disk is not None and 0 <= disk.used_ratio <= 1


# -- store and recorder --------------------------------------------------------------------


@pytest.fixture
def store(tmp_path: Path) -> OpsStore:
    return OpsStore(create_engine(f"sqlite:///{tmp_path / 'ops.db'}"))


class Clock:
    def __init__(self) -> None:
        self.now = T0

    def __call__(self) -> datetime:
        return self.now


def _delta(count: int, ms: float) -> StatDelta:
    histogram = [0] * BUCKET_COUNT
    histogram[latency_bucket(ms)] = count
    return StatDelta(count, ms * count, ms, histogram)


def test_stats_add_up_across_flushes(store: OpsStore) -> None:
    bucket = hour_bucket(T0)
    key = (bucket, "/api/v1/courses", "GET", 2)
    store.add_request_stats({key: _delta(3, 20)})
    store.add_request_stats(
        {key: _delta(2, 400), (bucket, "/api/v1/courses", "GET", 5): _delta(1, 900)}
    )
    rows = store.request_stats(bucket, bucket + timedelta(hours=1))
    ok = next(row for row in rows if row.status_class == 2)
    assert ok.count == 5
    assert ok.duration_ms_sum == pytest.approx(3 * 20 + 2 * 400)
    assert ok.duration_ms_max == 400
    assert ok.histogram[latency_bucket(20)] == 3 and ok.histogram[latency_bucket(400)] == 2
    assert {row.status_class for row in rows} == {2, 5}
    assert store.request_stats(bucket + timedelta(hours=1), bucket + timedelta(hours=2)) == []


def test_recorder_buffers_and_flushes(store: OpsStore) -> None:
    clock = Clock()
    recorder = Recorder(store, clock, flush_interval=15)
    for _ in range(4):
        recorder.record(method="GET", route="/x", status=200, duration_ms=12)
    recorder.record(method="GET", route="/x", status=503, duration_ms=30)
    bucket = hour_bucket(T0)
    # Nothing is written while requests are being served.
    assert store.request_stats(bucket, bucket + timedelta(hours=1)) == []
    assert not recorder.due()
    clock.now += timedelta(seconds=16)
    assert recorder.due()
    assert recorder.flush() == 2
    assert not recorder.due()
    rows = store.request_stats(bucket, bucket + timedelta(hours=1))
    assert sorted((row.status_class, row.count) for row in rows) == [(2, 4), (5, 1)]
    assert recorder.flush() == 0


def test_a_failed_flush_keeps_the_counts(store: OpsStore, monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = Recorder(store, Clock())
    recorder.record(method="GET", route="/x", status=200, duration_ms=12)

    def broken(_deltas: object) -> None:
        raise RuntimeError("database is away")

    monkeypatch.setattr(store, "add_request_stats", broken)
    assert recorder.flush() == 0
    monkeypatch.undo()
    recorder.record(method="GET", route="/x", status=200, duration_ms=12)
    assert recorder.flush() == 1
    bucket = hour_bucket(T0)
    assert store.request_stats(bucket, bucket + timedelta(hours=1))[0].count == 2


def test_failed_requests_are_stored_without_the_query_string(store: OpsStore) -> None:
    recorder = Recorder(store, Clock())
    recorder.record_error(
        method="GET",
        route="/api/v1/lessons/{lesson_id}",
        path="/api/v1/lessons/x?token=secret-value",
        status=500,
        duration_ms=41.5,
        request_id="req-1",
        user_id=7,
        error=ValueError("boom " + "x" * 2000),
    )
    (row,) = store.request_errors(10)
    assert row.path == "/api/v1/lessons/x"
    assert "secret-value" not in row.path
    assert row.error_type == "ValueError"
    assert row.error_message is not None and len(row.error_message) == 500
    assert (row.request_id, row.user_id, row.status) == ("req-1", 7, 500)
    # Erasing the account detaches it from the log; the failure itself stays.
    assert store.erase_user(7) == 1
    assert store.request_errors(10)[0].user_id is None
    assert store.request_errors(10, status=503) == []
    assert store.count_request_errors(T0 - timedelta(hours=1)) == 1


def test_page_views_visitors_and_referrers(store: OpsStore) -> None:
    day = date(2026, 11, 22)

    def view(
        path: str,
        visitor: str | None,
        *,
        bot: bool = False,
        signed_in: bool = False,
        ref: str | None = None,
    ) -> None:
        store.add_page_view(
            day=day,
            path=path,
            locale="ko",
            bot=bot,
            signed_in=signed_in,
            visitor=visitor,
            referrer=ref,
        )

    view("/", "aaaa", ref="google.com")
    view("/roadmap", "aaaa")
    view("/", "bbbb", ref="google.com")
    view("/", "bbbb", signed_in=True)  # signs in later the same day
    view("/", None, bot=True)
    (today,) = store.daily_visits(day, day)
    assert (today.views, today.bot_views, today.visitors) == (4, 1, 2)
    assert (today.signed_in_views, today.signed_in_visitors) == (1, 1)
    assert store.top_pages(day, day, 10) == [("/", 3), ("/roadmap", 1)]
    assert store.top_referrers(day, day, 10) == [("google.com", 2)]
    assert store.views_by_locale(day, day) == {"ko": 4}
    assert store.daily_visits(day + timedelta(days=1), day + timedelta(days=2)) == []


def test_purge_removes_only_what_is_past_retention(store: OpsStore) -> None:
    clock = Clock()
    recorder = Recorder(
        store,
        clock,
        retention=Retention(
            request_stats=timedelta(days=90),
            request_errors=timedelta(days=30),
            request_errors_max=3,
            page_views=timedelta(days=400),
            visitors=timedelta(days=35),
        ),
    )
    old, recent = T0 - timedelta(days=120), T0 - timedelta(days=1)
    store.add_request_stats(
        {
            (hour_bucket(old), "/x", "GET", 2): _delta(1, 5),
            (hour_bucket(recent), "/x", "GET", 2): _delta(1, 5),
        }
    )
    for at in (old, *([recent] * 5)):
        store.add_request_error(
            at=at, method="GET", route="/x", path="/x", status=500, duration_ms=1,
            request_id=None, user_id=None, error_type=None, error_message=None,
        )  # fmt: skip
    for day in (old.date(), (T0 - timedelta(days=40)).date(), recent.date()):
        store.add_page_view(
            day=day, path="/", locale="ko", bot=False, signed_in=False, visitor="v", referrer="g.co"
        )
    removed = recorder.purge()
    assert removed["request_stats"] == 1
    # One by age, two more by the cap of three.
    assert removed["request_errors"] == 3 and len(store.request_errors(10)) == 3
    assert removed["visitors"] == 2  # the 120- and 40-day-old pseudonyms
    assert removed["page_views"] == 0  # view counts are kept for 400 days
    assert store.table_rows()["ops_visitors"] == 1


def test_database_readings(store: OpsStore) -> None:
    assert (store.ping_ms() or 0) >= 0
    assert (store.database_size_bytes() or 0) > 0
    assert store.connections() is None  # SQLite has no connection limit to report
    assert set(store.table_rows()) == {
        "ops_request_stats",
        "ops_request_errors",
        "ops_page_views",
        "ops_visitors",
        "ops_referrers",
    }
