## Summary

<!-- What does this change and why? Link the issue: Closes #123 -->

## Type

- [ ] feat
- [ ] fix
- [ ] content (curriculum)
- [ ] docs
- [ ] refactor / test / ci / build / chore

## Checklist

- [ ] `bash scripts/harness/check.sh` passes (ruff, mypy, pytest + coverage gate)
- [ ] `uv run rc validate` passes
- [ ] Behavior changes include tests
- [ ] User-visible changes are listed under `## [Unreleased]` in `CHANGELOG.md`
- [ ] Commits follow Conventional Commits and are signed off (`git commit -s`, DCO)
- [ ] Hard-to-reverse decisions are recorded in `docs/adr/`
