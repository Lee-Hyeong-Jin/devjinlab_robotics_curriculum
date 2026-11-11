"""Generate a MkDocs project from the curriculum + progress store and build it.

``generate_project`` writes ``mkdocs.yml`` and a ``docs/`` tree (pure Markdown, see
:mod:`robotics_curriculum.site.pages`); ``build_site`` then runs ``mkdocs build``.
Everything the built site needs (Material theme, KaTeX, CSS) is local: no CDN and no
Google Fonts, so building and viewing work offline.
"""

from __future__ import annotations

import html
import logging
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from robotics_curriculum.learn.review import due_count
from robotics_curriculum.progress import ProgressService
from robotics_curriculum.progress.service import find_repo_root
from robotics_curriculum.site.pages import (
    INDEX_PAGE,
    RESOURCES_PAGE,
    ROADMAP_PAGE,
    STATES,
    SiteModel,
    render_dashboard,
    render_lesson,
    render_module,
    render_resources,
    render_roadmap,
    state_of,
)
from robotics_curriculum.site.stats import stage_of

ASSETS_DIR = Path(__file__).parent / "assets"
CONFIG_FILE = "mkdocs.yml"
DOCS_DIR = "docs"
HOOKS_FILE = "rc_hooks.py"
OVERRIDES_DIR = "overrides"
#: Written into every directory this command owns, so a later build knows it may replace it.
MARKER_FILE = ".rc-site"

logger = logging.getLogger(__name__)

# script-src needs 'unsafe-inline' because mkdocs-material emits an inline bootstrap
# script; the HTML sanitizer, not the CSP, is what stops injected scripts (AC-SEC.1).
CSP = (
    "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
    "script-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'; "
    "object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
)

MAIN_TEMPLATE = (
    '{% extends "base.html" %}\n'
    "{% block extrahead %}\n"
    f'  <meta http-equiv="Content-Security-Policy" content="{CSP}">\n'
    '  <meta name="referrer" content="no-referrer">\n'
    "{% endblock %}\n"
)

#: Hook module written into the generated project; mkdocs calls it for every page.
HOOKS_MODULE = (
    '"""MkDocs hook: sanitize each rendered page (see site.sanitize)."""\n'
    "\n"
    "from typing import Any\n"
    "\n"
    "from robotics_curriculum.site.sanitize import clean\n"
    "\n"
    "\n"
    "def on_page_content(\n"
    "    html: str, page: Any = None, config: Any = None, files: Any = None\n"
    ") -> str:\n"
    "    return clean(html)\n"
)


class SiteError(Exception):
    """A site build could not start: an unsafe or non-empty output directory."""


def _special_dirs() -> list[tuple[str, Path]]:
    return [
        ("the current directory", Path.cwd().resolve()),
        ("the repository root", find_repo_root().resolve()),
        ("your home directory", Path.home().resolve()),
    ]


def _unsafe_reason(path: Path) -> str | None:
    resolved = path.resolve()
    for name, special in _special_dirs():
        if resolved == special:
            return f"it is {name}"
        if special.is_relative_to(resolved):
            return f"it contains {name}"
    return None


def ensure_writable(path: Path, *, kind: str, force: bool = False) -> None:
    """Refuse to replace a directory this command did not create (AC-SEC.2).

    ``mkdocs`` empties both the site directory and the generated project's ``docs/``, so a
    mistyped path would delete unrelated files. A directory is accepted when it does not
    exist, is empty, or carries the :data:`MARKER_FILE` left by an earlier build.
    """
    reason = _unsafe_reason(path)
    if reason is not None:
        raise SiteError(f"refusing to use {path} as the {kind}: {reason}")
    if not path.exists():
        return
    if not path.is_dir():
        raise SiteError(f"{path} is not a directory")
    if not any(path.iterdir()) or (path / MARKER_FILE).exists():
        return
    if force:
        logger.warning("replacing the contents of a non-empty %s (--force)", kind)
        return
    raise SiteError(
        f"{path} is not empty and has no {MARKER_FILE} marker from an earlier "
        f"`rc site build`; its contents would be deleted. Choose an empty directory "
        f"or pass --force."
    )


def _mark(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
        (path / MARKER_FILE).write_text(
            "Written by `rc site build`; this directory is replaced on each build.\n",
            encoding="utf-8",
        )
    except OSError as exc:  # pragma: no cover - unwritable output
        logger.debug("cannot write the build marker: %s", exc)


# Written verbatim: mkdocs' YAML loader understands the python tag, safe_dump cannot emit it.
MARKDOWN_EXTENSIONS = """\
markdown_extensions:
  - admonition
  - attr_list
  - md_in_html
  - def_list
  - footnotes
  - tables
  - toc:
      permalink: true
      slugify: !!python/object/apply:pymdownx.slugs.slugify
        kwds:
          case: lower
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.superfences
  - pymdownx.details
  - pymdownx.tasklist:
      custom_checkbox: true
"""


def build_model(service: ProgressService, now: datetime | None = None) -> SiteModel:
    """Snapshot content + progress for one user."""
    at = now or datetime.now().astimezone()
    return SiteModel(
        courses=service.courses,
        summaries=service.status(),
        next_lessons=service.next_lessons(),
        sessions=service.store.list_sessions(service.user_id),
        now=at,
        due_today=due_count(service.store, today=at.astimezone().date(), user_id=service.user_id),
    )


def _nav(model: SiteModel) -> list[Any]:
    nav: list[Any] = [{"대시보드": INDEX_PAGE}, {"로드맵": ROADMAP_PAGE}]
    for stage in model.stages():
        modules = [m for m in model.modules() if stage_of(m) == stage]
        if not modules:
            continue
        stage_items: list[Any] = []
        for module in modules:
            items: list[Any] = [model.module_page(module)]
            for summary in model.module_summaries(module):
                symbol = STATES[state_of(summary)][0]
                items.append(
                    {
                        f"{symbol} {html.escape(summary.lesson.title)}": model.lesson_page(
                            summary.lesson
                        )
                    }
                )
            stage_items.append({html.escape(module.title): items})
        nav.append({stage: stage_items})
    nav.append({"자료실": RESOURCES_PAGE})
    return nav


def mkdocs_config(model: SiteModel) -> str:
    config: dict[str, Any] = {
        # mkdocs-material writes nav titles and site_name into HTML unescaped, so
        # they are escaped here (AC-SEC.1).
        "site_name": html.escape(model.title),
        "site_description": html.escape(
            model.courses[0].summary if len(model.courses) == 1 else ""
        ),
        "docs_dir": DOCS_DIR,
        # Plain .html links so the built site also works when opened from disk (file://).
        "use_directory_urls": False,
        "theme": {
            "name": "material",
            "custom_dir": OVERRIDES_DIR,
            "language": "ko",
            "font": False,  # no Google Fonts request: system fonts, offline-safe
            "features": [
                "navigation.tabs",
                "navigation.indexes",
                "navigation.top",
                "navigation.footer",
                "toc.follow",
                "content.code.copy",
                "search.highlight",
            ],
            "palette": [
                {
                    "media": "(prefers-color-scheme: light)",
                    "scheme": "default",
                    "primary": "indigo",
                    "accent": "indigo",
                    "toggle": {"icon": "material/weather-night", "name": "다크 모드로 전환"},
                },
                {
                    "media": "(prefers-color-scheme: dark)",
                    "scheme": "slate",
                    "primary": "indigo",
                    "accent": "indigo",
                    "toggle": {"icon": "material/weather-sunny", "name": "라이트 모드로 전환"},
                },
            ],
        },
        "plugins": ["search"],
        "hooks": [HOOKS_FILE],
        "extra_css": ["assets/katex/katex.min.css", "assets/rc.css"],
        "extra_javascript": [
            "assets/katex/katex.min.js",
            "assets/katex/contrib/auto-render.min.js",
            "assets/katex-init.js",
        ],
        "nav": _nav(model),
    }
    dumped = yaml.safe_dump(config, allow_unicode=True, sort_keys=False)
    return dumped + MARKDOWN_EXTENSIONS


def generate_project(
    service: ProgressService,
    project_dir: Path,
    *,
    now: datetime | None = None,
    force: bool = False,
) -> Path:
    """Write ``mkdocs.yml`` + ``docs/`` into ``project_dir``; return the config path.

    Raises :class:`SiteError` when ``project_dir`` holds files this command did not
    write (mkdocs would delete them).
    """
    ensure_writable(project_dir, kind="mkdocs project directory", force=force)
    _mark(project_dir)
    model = build_model(service, now)
    docs = project_dir / DOCS_DIR
    if docs.exists():
        shutil.rmtree(docs)
    docs.mkdir(parents=True)
    pages: dict[str, str] = {
        INDEX_PAGE: render_dashboard(model),
        ROADMAP_PAGE: render_roadmap(model),
        RESOURCES_PAGE: render_resources(model),
    }
    for module in model.modules():
        pages[model.module_page(module)] = render_module(model, module)
    for summary in model.summaries:
        pages[model.lesson_page(summary.lesson)] = render_lesson(model, summary)
    for rel, text in pages.items():
        path = docs / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    shutil.copytree(ASSETS_DIR, docs / "assets")
    overrides = project_dir / OVERRIDES_DIR
    overrides.mkdir(parents=True, exist_ok=True)
    (overrides / "main.html").write_text(MAIN_TEMPLATE, encoding="utf-8")
    (project_dir / HOOKS_FILE).write_text(HOOKS_MODULE, encoding="utf-8")
    config_path = project_dir / CONFIG_FILE
    config_path.write_text(mkdocs_config(model), encoding="utf-8")
    return config_path


def run_mkdocs_build(config_path: Path, out_dir: Path) -> None:
    """``mkdocs build`` via its Python API (no subprocess, no network)."""
    from mkdocs.commands.build import build
    from mkdocs.config import load_config

    config = load_config(str(config_path), site_dir=str(out_dir.resolve()))
    try:
        build(config)
    finally:
        config.plugins.on_shutdown()


def build_site(
    service: ProgressService,
    out_dir: Path,
    *,
    project_dir: Path | None = None,
    now: datetime | None = None,
    force: bool = False,
) -> Path:
    """Generate the MkDocs project (in ``project_dir`` or a temp dir) and build into ``out_dir``.

    ``out_dir`` is replaced by mkdocs, so it and ``project_dir`` must pass
    :func:`ensure_writable` first; ``force`` allows a non-empty directory.
    """
    ensure_writable(out_dir, kind="site output directory", force=force)
    _mark(out_dir)
    if project_dir is not None:
        config = generate_project(service, project_dir, now=now, force=force)
        run_mkdocs_build(config, out_dir)
        return out_dir
    with tempfile.TemporaryDirectory(prefix="rc-site-") as tmp:
        config = generate_project(service, Path(tmp), now=now, force=force)
        run_mkdocs_build(config, out_dir)
    return out_dir


def serve_site(
    service: ProgressService, *, project_dir: Path | None = None, force: bool = False
) -> int:
    """Generate the project and run ``mkdocs serve`` on it until interrupted."""
    with tempfile.TemporaryDirectory(prefix="rc-site-") as tmp:
        config = generate_project(service, project_dir or Path(tmp), force=force)
        cmd = [sys.executable, "-m", "mkdocs", "serve", "-f", str(config)]
        try:
            return subprocess.call(cmd)
        except KeyboardInterrupt:
            return 0
