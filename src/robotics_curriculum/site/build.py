"""Generate a MkDocs project from the curriculum + progress store and build it.

``generate_project`` writes ``mkdocs.yml`` and a ``docs/`` tree (pure Markdown, see
:mod:`robotics_curriculum.site.pages`); ``build_site`` then runs ``mkdocs build``.
Everything the built site needs (Material theme, KaTeX, CSS) is local: no CDN and no
Google Fonts, so building and viewing work offline.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from robotics_curriculum.progress import ProgressService
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
    return SiteModel(
        courses=service.courses,
        summaries=service.status(),
        next_lessons=service.next_lessons(),
        sessions=service.store.list_sessions(service.user_id),
        now=now or datetime.now().astimezone(),
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
                    {f"{symbol} {summary.lesson.title}": model.lesson_page(summary.lesson)}
                )
            stage_items.append({module.title: items})
        nav.append({stage: stage_items})
    nav.append({"자료실": RESOURCES_PAGE})
    return nav


def mkdocs_config(model: SiteModel) -> str:
    config: dict[str, Any] = {
        "site_name": model.title,
        "site_description": model.courses[0].summary if len(model.courses) == 1 else "",
        "docs_dir": DOCS_DIR,
        # Plain .html links so the built site also works when opened from disk (file://).
        "use_directory_urls": False,
        "theme": {
            "name": "material",
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
    service: ProgressService, project_dir: Path, *, now: datetime | None = None
) -> Path:
    """Write ``mkdocs.yml`` + ``docs/`` into ``project_dir``; return the config path."""
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
) -> Path:
    """Generate the MkDocs project (in ``project_dir`` or a temp dir) and build into ``out_dir``.

    ``out_dir`` is replaced by mkdocs (its old contents are removed).
    """
    if project_dir is not None:
        run_mkdocs_build(generate_project(service, project_dir, now=now), out_dir)
        return out_dir
    with tempfile.TemporaryDirectory(prefix="rc-site-") as tmp:
        run_mkdocs_build(generate_project(service, Path(tmp), now=now), out_dir)
    return out_dir


def serve_site(service: ProgressService, *, project_dir: Path | None = None) -> int:
    """Generate the project and run ``mkdocs serve`` on it until interrupted."""
    with tempfile.TemporaryDirectory(prefix="rc-site-") as tmp:
        config = generate_project(service, project_dir or Path(tmp))
        cmd = [sys.executable, "-m", "mkdocs", "serve", "-f", str(config)]
        try:
            return subprocess.call(cmd)
        except KeyboardInterrupt:
            return 0
