# Contributing

> **요약 (한국어)** — `uv sync`로 개발 환경을 만들고, 변경 후 `bash scripts/harness/check.sh`
> (ruff · mypy · pytest + 커버리지 80%)와 `uv run rc validate`를 통과시킨 뒤 PR을 보냅니다.
> 커밋 메시지는 Conventional Commits(`type(scope): summary`) 형식이며 모든 커밋에
> `git commit -s`로 DCO 서명(`Signed-off-by:`)을 답니다. 레슨은
> `docs/curriculum/LESSON_TEMPLATE.md`를 복사해 작성합니다. 코드는 Apache-2.0,
> `curriculum/` 콘텐츠는 CC BY 4.0으로 기여됩니다.

Thank you for helping. This project has two kinds of contributions: **code** (the
`robotics_curriculum` package and `rc` CLI, Apache-2.0) and **content** (lessons under
`curriculum/`, CC BY 4.0). Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md).
Security problems go through [SECURITY.md](SECURITY.md), never a public issue.

## Development setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync                          # creates .venv with runtime + dev dependencies
uv run pre-commit install        # optional: run the hooks on every commit
uv run rc --help
```

Always run Python tools through `uv run`. Do not edit `uv.lock` by hand; change dependencies
with `uv add` / `uv add --dev` and commit the updated lock file.

## Running checks

```bash
bash scripts/harness/check.sh            # ruff check, ruff format --check, mypy, pytest + coverage
bash scripts/harness/check.sh --quick    # lint + type-check only
uv run rc validate                       # validate curriculum content
uv run pre-commit run --all-files        # every pre-commit hook
```

CI runs the same steps. A pull request is mergeable only when they all pass. Rules:

- **Type hints are required** in `src/`; mypy runs in strict mode.
- **Every behavior change ships with a test.** Line + branch coverage must stay at or above
  the `fail_under` value in `pyproject.toml`. Never weaken or skip tests to pass the gate.
- Hard-to-reverse design choices get an ADR in `docs/adr/` (copy `docs/adr/TEMPLATE.md`).

## Commits

We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
type(scope): short imperative summary

Optional body explaining why.

Signed-off-by: Your Name <you@example.com>
```

Types: `feat`, `fix`, `docs`, `content`, `refactor`, `test`, `ci`, `build`, `chore`, `perf`.
Use `content` for curriculum changes. Mark breaking changes with `!` (`feat(cli)!: ...`) and a
`BREAKING CHANGE:` footer.

### Developer Certificate of Origin (DCO)

Every commit must be signed off, certifying the
[Developer Certificate of Origin 1.1](https://developercertificate.org/): you wrote the change
or otherwise have the right to submit it under the project's licenses. Sign off with
`git commit -s`. To fix the last commit: `git commit --amend -s --no-edit`; for a whole branch:
`git rebase --signoff main`.

## Branches and pull requests

1. Fork (external contributors) or create a branch from `main`: `feat/<topic>`, `fix/<topic>`,
   `content/<lesson-id>`, `docs/<topic>`.
2. Keep pull requests focused: one feature, fix, or lesson group per PR.
3. Fill in the pull request template, link the issue (`Closes #123`), and add a line under
   `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md) for user-visible changes.
4. A maintainer reviews; address comments with new commits, then the PR is squash-merged.
   Never push directly to `main`.

## Contributing curriculum content

1. Copy the block in `docs/curriculum/LESSON_TEMPLATE.md` to
   `curriculum/<course>/<module>/<lesson>.md`. Field definitions and rules are in
   `docs/curriculum/CONTENT_MODEL.md`.
2. Add the file name (without `.md`) to the `lessons` list in the module's `module.yaml`.
3. Declare real prerequisites (lesson IDs) so the prerequisite graph stays a DAG, include at
   least one entry in `resources`, and write the "이 단계 공부법" section.
4. Run `uv run rc validate` and `uv run rc show <lesson-id>`; optionally preview with
   `uv run rc site build --serve`.
5. Open a PR with type `content`. Only link resources you are allowed to reference; do not
   paste copyrighted text from them. Your content is contributed under CC BY 4.0.

To report a mistake in an existing lesson without fixing it yourself, open a
"Content issue" from the issue templates.
