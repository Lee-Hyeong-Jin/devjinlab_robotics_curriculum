# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `rc` CLI (Typer): `version`, `validate`, `show`, `resources`, `status`, `start`, `stop`,
  `log`, `done`, `next`, `roadmap`, `progress export|import`, `report weekly|module`,
  `site build`.
- Content model: Course > Module > Lesson > Activity as Markdown with YAML front matter, with a
  loader and validator (required fields, unknown prerequisites, prerequisite cycles, resource
  URL format).
- Robotics expert course content under `curriculum/robotics-expert/`, with "이 단계 공부법"
  sections and resource lists for each lesson.
- Local progress tracking in SQLite (`.rc/progress.db`) behind a store interface, with JSON
  export and import.
- Weekly and per-module Markdown reports.
- Prerequisite roadmap with done / in-progress / locked states and next-lesson recommendation.
- Offline static study site (MkDocs Material): dashboard, roadmap, module and lesson pages,
  resource library.
- Engineering scaffolding: Apache-2.0 license for code, CC BY 4.0 for curriculum content,
  contribution guide, Code of Conduct, security policy, issue and PR templates, Dependabot,
  GitHub Actions CI and release workflows, strict mypy, coverage gate, pre-commit hooks,
  Dockerfile and Compose file.
