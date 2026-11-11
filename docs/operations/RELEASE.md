# 릴리스 절차 (Release checklist)

SemVer 2.0.0 를 따르고, 릴리스는 `v<major>.<minor>.<patch>` 태그로 찍는다. 태그를 밀면
`.github/workflows/release.yml` 이 `uv build` 로 sdist·wheel 을 만들고 CHANGELOG 의 해당 절을
본문으로 GitHub Release 를 만든다. 아래 순서를 그대로 밟고, 각 단계의 실제 출력으로 확인한다.

버전을 올리는 커밋은 **릴리스 전용**이다. 기능 변경과 섞지 않는다.

## 1. 준비

- [ ] `main`(또는 `integration`)이 최신이고 작업 트리가 깨끗하다: `git status --short` 가 비어 있다.
- [ ] 미해결 보안 리뷰 지적이 없다: `docs/reviews/` 의 최신 리뷰에 열린 high 이상 항목이 없다.
- [ ] 의존성 감사가 깨끗하다: `uvx pip-audit`(런타임), `cd web && npm run audit`.

## 2. 버전 올리기

- [ ] `pyproject.toml` 의 `version` 을 올린다(소스에서 읽히므로 다른 곳에 버전 문자열을 복제하지 않는다).
- [ ] `uv lock` 으로 락파일의 프로젝트 버전을 맞춘다.
- [ ] `uv run rc version` 이 새 버전을 출력한다.
- [ ] 웹을 함께 배포하면 `web/package.json` 의 `version` 도 같은 값으로 올린다.

## 3. CHANGELOG

- [ ] `## [Unreleased]` 의 항목을 검토한다: 사용자에게 보이는 변경만 남기고, Added/Changed/
      Deprecated/Removed/Fixed/Security 로 분류한다.
- [ ] `## [Unreleased]` 아래에 `## [x.y.z] - YYYY-MM-DD` 절을 만들고 항목을 옮긴다.
      `[Unreleased]` 는 빈 채로 남긴다.
- [ ] 원격이 생겨 CHANGELOG 하단에 비교 링크(`[x.y.z]: .../compare/...`)를 두게 되면 함께 갱신한다.
- [ ] Breaking change 가 있으면 마이그레이션 방법을 그 절 첫머리에 적는다.

## 4. 검증 (모두 통과해야 한다)

- [ ] `bash scripts/harness/check.sh` → `ALL CHECKS PASSED` (ruff, mypy strict, pytest+커버리지, web lint/typecheck/test)
- [ ] `uv run rc validate` → 콘텐츠 오류 0건
- [ ] `uv run rc site build --out /tmp/rc-release-site` → 정적 사이트 생성
- [ ] `bash scripts/smoke.sh` → `SMOKE PASSED` (db → migrate → api → web 실제 기동)
- [ ] `bash scripts/ops/restore_drill.sh` → 백업·복구 리허설 통과, 결과를 `docs/ops/restore-drills.md` 에 한 줄 기록 (AC-OPS.4)
- [ ] `cd web && npm run e2e` → Playwright + axe 통과(실행 중인 API 필요)
- [ ] `uv build` → `dist/` 에 sdist 와 wheel

## 5. 이미지

- [ ] `docker build -t robotics-curriculum:<x.y.z> .` (CLI)
- [ ] `docker build --target api -t robotics-curriculum-api:<x.y.z> .`
- [ ] `docker build --target web -t robotics-curriculum-web:<x.y.z> .`
- [ ] 각 이미지가 비루트 사용자로 뜨는지 확인한다: `docker inspect --format '{{.Config.User}}' <image>`
      (CLI·API 는 `rc`, web 은 `node`).

## 6. 태그와 공개

- [ ] 릴리스 커밋: `chore(release): v<x.y.z>` (Conventional Commits, `git commit -s`).
- [ ] 태그: `git tag -a v<x.y.z> -m "v<x.y.z>"`.
- [ ] 푸시는 사용자가 한다: `git push origin main --follow-tags`.
- [ ] GitHub Actions 의 release 워크플로가 통과하고 Release 본문이 CHANGELOG 절과 일치하는지 확인한다.
- [ ] 릴리스 후 `harness/roadmap.yaml` 의 마일스톤 상태와 `docs/PRD.md` 의 릴리스 계획을 실제와 맞춘다.

## 7. 릴리스 후

- [ ] 새 `## [Unreleased]` 절이 비어 있는지 확인한다.
- [ ] 보안 수정이 포함된 릴리스라면 `SECURITY.md` 의 지원 버전 표를 갱신한다.
- [ ] 자체 호스팅 사용자를 위한 업그레이드 주의사항(마이그레이션, 환경 변수 변경)을 RUNBOOK 에 반영한다.

## 되돌리기

태그는 지우지 않는다. 문제가 있으면 다음 패치 버전을 낸다. 배포된 스택을 되돌릴 때는
RUNBOOK 의 복구 절차(이전 이미지 태그로 되돌리고, 필요하면 `alembic downgrade` 한 단계)를 따른다.
