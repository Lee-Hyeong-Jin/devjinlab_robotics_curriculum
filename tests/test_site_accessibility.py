"""Accessibility of the generated site (P2-6, WCAG 2.1 AA targets of PRD §7).

Checks that run without a browser: the document language, one h1 per page with no skipped
heading levels, data tables with header cells, a skip link to the content, images with alt
text, and the contrast of the colours this project adds on top of the theme.
"""

from __future__ import annotations

import re
import shutil
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path

import pytest

from robotics_curriculum.content import load_courses
from robotics_curriculum.progress import ProgressService, SqliteProgressStore
from robotics_curriculum.site import build_site

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "curriculum"
CSS = ROOT / "src" / "robotics_curriculum" / "site" / "assets" / "rc.css"
NOW = datetime(2026, 11, 11, 12, 0, tzinfo=UTC)
VECTORS = "m1-vectors-matrices"
M1 = "modules/m1-math-physics"

# WCAG 2.1: 4.5:1 for body text, 3:1 for large text and non-text parts.
MIN_CONTRAST_TEXT = 4.5


class _Collector(HTMLParser):
    """Collects the pieces the checks need: headings, tables, images, links, html lang."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang: str | None = None
        self.headings: list[tuple[int, str]] = []
        self.images: list[dict[str, str | None]] = []
        self.links: list[tuple[str, str]] = []
        self.skip_links: list[tuple[str, str]] = []
        self._link_class: str | None = None
        self._link_label: str | None = None
        self.tables: list[dict[str, int]] = []
        self._heading: int | None = None
        self._text: list[str] = []
        self._href: str | None = None
        self._link_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "html":
            self.lang = attributes.get("lang")
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading = int(tag[1])
            self._text = []
        elif tag == "img":
            self.images.append(attributes)
        elif tag == "a":
            self._href = attributes.get("href")
            self._link_class = attributes.get("class")
            self._link_label = attributes.get("aria-label") or attributes.get("title")
            self._link_text = []
        elif tag == "table":
            self.tables.append({"th": 0, "rows": 0})
        elif tag == "th" and self.tables:
            self.tables[-1]["th"] += 1
        elif tag == "tr" and self.tables:
            self.tables[-1]["rows"] += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and self._heading is not None:
            self.headings.append((self._heading, "".join(self._text).strip()))
            self._heading = None
        elif tag == "a" and self._href is not None:
            text = "".join(self._link_text).strip()
            classes = (self._link_class or "").split()
            if "md-skip" in classes:
                self.skip_links.append((self._href, text))
            elif "headerlink" not in classes and not self._link_label:
                self.links.append((self._href, text))
            self._href = self._link_class = self._link_label = None

    def handle_data(self, data: str) -> None:
        if self._heading is not None:
            self._text.append(data)
        if self._href is not None:
            self._link_text.append(data)


def parse(html: str) -> _Collector:
    collector = _Collector()
    collector.feed(html)
    return collector


# -- contrast ------------------------------------------------------------------


def _channel(value: float) -> float:
    return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """WCAG relative luminance of ``#rrggbb``."""
    text = hex_color.lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    r, g, b = (int(text[i : i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(foreground: str, background: str) -> float:
    """WCAG contrast ratio between two ``#rrggbb`` colours (1.0 … 21.0)."""
    first, second = relative_luminance(foreground), relative_luminance(background)
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


def test_contrast_helpers_match_the_wcag_reference() -> None:
    assert contrast_ratio("#000000", "#ffffff") == pytest.approx(21.0, abs=0.01)
    assert contrast_ratio("#ffffff", "#ffffff") == pytest.approx(1.0, abs=0.01)
    assert contrast_ratio("#767676", "#ffffff") == pytest.approx(4.54, abs=0.02)


@pytest.mark.parametrize(
    ("name", "foreground", "background"),
    [
        # light scheme (Material "default": white page)
        ("rc-done", "#2e7d32", "#ffffff"),
        ("rc-in_progress", "#b35600", "#ffffff"),
        # dark scheme (Material "slate": #1f2129 page)
        ("rc-done dark", "#81c784", "#1f2129"),
        ("rc-in_progress dark", "#ffb74d", "#1f2129"),
    ],
)
def test_status_colours_meet_aa_contrast(name: str, foreground: str, background: str) -> None:
    ratio = contrast_ratio(foreground, background)
    assert ratio >= MIN_CONTRAST_TEXT, f"{name}: {ratio:.2f}:1 is below {MIN_CONTRAST_TEXT}:1"


def test_every_literal_colour_in_the_stylesheet_is_covered_by_a_contrast_test() -> None:
    """A new hard-coded colour must come with a contrast check in this file."""
    stylesheet = CSS.read_text(encoding="utf-8")
    literals = {c.lower() for c in re.findall(r"#[0-9a-fA-F]{3,6}", stylesheet)}
    checked = {"#2e7d32", "#b35600", "#81c784", "#ffb74d", "#526cfe"}
    assert literals <= checked, f"untested colours in rc.css: {sorted(literals - checked)}"


def test_accent_fallback_colour_carries_white_text() -> None:
    # #526cfe is the progress-bar fill, drawn behind white text in both schemes.
    assert contrast_ratio("#ffffff", "#526cfe") >= 3.0


# -- generated HTML ------------------------------------------------------------


@pytest.fixture(scope="module")
def site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """One built site (mkdocs runs offline) shared by the page checks."""
    tmp = tmp_path_factory.mktemp("a11y")
    root = tmp / "curriculum"
    shutil.copytree(FIXTURE, root)
    store = SqliteProgressStore.in_dir(tmp / "rcdata")
    service = ProgressService(store, load_courses(root), clock=lambda: NOW)
    service.log(VECTORS, 40)
    service.done(VECTORS, understanding=4)
    try:
        return build_site(service, tmp / "site", now=NOW)
    finally:
        store.close()


PAGES = [
    "index.html",
    "roadmap.html",
    "resources.html",
    f"{M1}/index.html",
    f"{M1}/m1-vectors-matrices.html",
]


@pytest.mark.parametrize("rel", PAGES)
def test_page_declares_the_document_language(site: Path, rel: str) -> None:
    page = parse((site / rel).read_text(encoding="utf-8"))
    assert page.lang == "ko"


def test_english_build_declares_english(tmp_path: Path) -> None:
    root = tmp_path / "curriculum"
    shutil.copytree(FIXTURE, root)
    store = SqliteProgressStore.in_dir(tmp_path / "rcdata")
    service = ProgressService(store, load_courses(root), clock=lambda: NOW)
    try:
        out = build_site(service, tmp_path / "site", now=NOW, lang="en")
    finally:
        store.close()
    assert parse((out / "index.html").read_text(encoding="utf-8")).lang == "en"


@pytest.mark.parametrize("rel", PAGES)
def test_one_h1_per_page_and_no_skipped_levels(site: Path, rel: str) -> None:
    page = parse((site / rel).read_text(encoding="utf-8"))
    levels = [level for level, _ in page.headings]
    assert levels.count(1) == 1, f"{rel}: {levels.count(1)} h1 elements"
    assert levels[0] == 1, f"{rel}: starts with h{levels[0]}"
    assert all(text for _, text in page.headings), f"{rel}: an empty heading"
    previous = levels[0]
    for level in levels[1:]:
        assert level <= previous + 1, f"{rel}: h{previous} is followed by h{level}"
        previous = level


@pytest.mark.parametrize("rel", PAGES)
def test_tables_have_header_cells(site: Path, rel: str) -> None:
    page = parse((site / rel).read_text(encoding="utf-8"))
    for index, table in enumerate(page.tables):
        assert table["th"] > 0, f"{rel}: table {index} has no th cells"


@pytest.mark.parametrize("rel", PAGES)
def test_images_have_alt_text(site: Path, rel: str) -> None:
    page = parse((site / rel).read_text(encoding="utf-8"))
    for image in page.images:
        assert "alt" in image, f"{rel}: <img src={image.get('src')!r}> has no alt"


@pytest.mark.parametrize("rel", PAGES)
def test_skip_link_points_at_the_content(site: Path, rel: str) -> None:
    html = (site / rel).read_text(encoding="utf-8")
    page = parse(html)
    assert page.skip_links, f"{rel}: no skip link (class md-skip)"
    href, text = page.skip_links[0]
    assert text, f"{rel}: the skip link has no text"
    assert href.startswith("#"), f"{rel}: the skip link points at {href}"
    target = href[1:]
    assert f'id="{target}"' in html, f"{rel}: the skip link target {href} does not exist"


@pytest.mark.parametrize("rel", PAGES)
def test_links_have_discernible_text(site: Path, rel: str) -> None:
    """Every link carries text, an aria-label or a title (the parser drops the latter two)."""
    page = parse((site / rel).read_text(encoding="utf-8"))
    without_text = [href for href, text in page.links if not text]
    assert without_text == [], f"{rel}: links without discernible text: {without_text[:3]}"


def test_status_badges_do_not_rely_on_colour_alone(site: Path) -> None:
    """Each state shows a symbol and a word, so colour is never the only signal."""
    roadmap = (site / "roadmap.html").read_text(encoding="utf-8")
    for symbol, word in (("■", "완료"), ("□", "시작 전"), ("▨", "잠김")):
        assert f"{symbol} {word}" in roadmap
