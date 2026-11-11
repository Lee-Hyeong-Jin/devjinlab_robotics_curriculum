# 엔지니어링 규칙 (오픈소스 · 엔터프라이즈 품질)

이 저장소는 공개 오픈소스이며 외부 기여자와 운영 환경을 전제로 개발한다. 아래 규칙은 사람과 에이전트 모두에게 적용되며, 검증 게이트(`bash scripts/harness/check.sh [--quick]`)와 CI 가 기계적으로 강제한다.

## 작업 흐름
- 작업은 개발 그래프(harness/graph.md)의 노드 단위로 한다: 명세 없이 구현하지 않고, 검증 없이 끝내지 않는다.
- 루프는 항상 종료 조건과 최대 반복 수를 가진다. 같은 실패로 3회 반복하면 멈추고 사람에게 보고한다.
- main/master 에 직접 커밋하지 않는다. 작업 브랜치 또는 워크트리에서 커밋하고, 통합은 `integration` 브랜치를 거쳐 사용자가 main 에 머지한다.
- 큰 설계 변경(여러 모듈·공개 API·저장소·배포 형태에 걸친 변경)은 `docs/rfcs/` 에 RFC 로 제안·토론하고, 채택되면 결정을 `docs/adr/` 에 ADR 로 기록한다(`/adr`). 되돌리기 비싼 결정(스택, 저장소, 알고리즘, 외부 서비스, 공개 API 형태)은 RFC 를 거치지 않더라도 반드시 ADR 로 남긴다.
- `git stash`(bare), `git reset --hard`, `git checkout -- .`, 강제 push, 히스토리 재작성은 금지. 작업을 잠시 치울 땐 WIP 커밋을 쓴다.
- 보고는 사실만: 실행한 명령과 출력에 근거해 말하고, 확인하지 않은 것은 확인하지 않았다고 쓴다.

## 아키텍처 경계
- `progress` 는 `content` 를 모른다(레슨·활동은 문자열 ID 로만 참조). `content` 는 `progress` 를 모른다. 둘을 잇는 것은 `learn` 뿐이다.
- `cli.py` 만 typer·터미널 I/O 를 안다. 나머지 모듈은 값을 반환하고 예외를 던진다.
- `sm2`, `graph`, `stats`, `guide`, `report` 는 순수 함수로 작성하고 단위 테스트가 필수다.
- `api/` 는 코어 라이브러리 함수만 호출하고 규칙을 중복 구현하지 않는다. `web/` 은 코어를 import 하지 않고 API 만 쓴다(설계 docs/platform-design.md §6).

## 코드 품질 (Python)
- Python 은 `uv run` 으로 실행한다(`uv run pytest -q --cov`, `uv run ruff check .`, `uv run mypy`). 의존성은 `uv add`, 락파일(uv.lock)을 함께 커밋한다.
- **타입 힌트 필수**: 모든 공개 함수·메서드·클래스 속성에 타입을 붙이고 mypy strict 모드(`--strict`, pyproject `[tool.mypy] strict = true`, 대상 `files = src`)를 통과한다. 실행은 인자 없이 `uv run mypy`. `Any`, `# type: ignore`, `cast` 는 사유 주석과 함께만 허용한다.
- 린트·포맷: ruff(E, F, I, B, UP + 프로젝트 설정)를 통과하고 `ruff format` 결과와 일치해야 한다. 문서의 Python 코드 블록도 포맷 대상이다.
- 공개 API(모듈 최상위 함수·클래스, CLI 커맨드)에는 docstring(목적, 인자, 반환, 예외)을 쓴다. 내부 구현은 이름으로 설명하고 주석은 "왜"만 적는다.
- 오류 처리: 예외는 도메인 예외 타입으로 던지고, CLI 경계에서만 사용자 메시지로 바꾼다. 빈 `except:` 와 예외 삼키기 금지. 실패는 비정상 종료 코드로 드러낸다.
- 로깅: `logging` 모듈을 쓰고 `print` 는 CLI 출력에만 쓴다. 로그에 개인 데이터(학습 메모, 경로의 사용자명 등)를 남기지 않는다.
- 서버 모드(`api/`, `web/`, Phase 2): structlog JSON 로깅 + `request_id` 상관관계(응답 헤더와 동일), `/healthz`(생존)·`/readyz`(DB 연결·콘텐츠 색인)·`/version`, Prometheus `/metrics` 를 제공한다. 세부는 docs/architecture/operations.md.
- 입력 검증: 파일·YAML·CLI 인자 등 외부 입력은 경계에서 pydantic 모델로 검증한다. 경로는 저장소/콘텐츠 루트 밖으로 벗어나지 못하게 정규화·검사한다.
- 의존성 추가는 최소화한다. **Apache-2.0 과 호환되는 라이선스만 허용**하고 copyleft(GPL·AGPL·LGPL 등)는 금지한다. 추가 시 라이선스와 유지 상태를 PR 설명에 적는다.

## 테스트와 커버리지
- 동작 변경에는 테스트가 따른다. 테스트를 약화·skip·삭제해서 게이트를 통과시키지 않는다.
- **커버리지**: 코어 라이브러리(`src/robotics_curriculum`)의 라인+분기(branch) 커버리지 80% 이상을 유지한다(pytest-cov, pyproject `[tool.coverage.run] branch = true`, `[tool.coverage.report] fail_under = 80`). 실행은 `uv run pytest -q --cov`. Phase 2 의 `api/` 도 같은 기준을 따른다. 새 모듈은 자체적으로 80% 이상이어야 하고, 커버리지를 낮추는 PR 은 사유를 적는다.
- 테스트 종류: 단위 테스트(순수 로직), 통합 테스트(CLI 엔드투엔드, 임시 디렉터리 사용), 회귀 테스트(버그 수정마다 1개). 네트워크·시간·난수에 의존하는 테스트는 모킹한다.
- 콘텐츠 검증, 간격 반복 계산, 리포트 생성, 진행도 저장은 단위 테스트가 필수다(PRD 비기능 요구사항).
- 커밋 전 로컬 확인: `bash scripts/harness/check.sh`(빠른 확인은 `--quick`), `uv run pre-commit run --all-files`.

## 커밋과 PR
- **Conventional Commits**: `type(scope): summary` — type 은 feat, fix, docs, test, refactor, perf, chore, ci, build 중 하나. scope 는 모듈명 또는 마일스톤 id. 본문에 "왜"를 쓰고, 파괴적 변경은 `BREAKING CHANGE:` 푸터를 단다.
- **DCO**: 모든 커밋에 `Signed-off-by:` 줄을 단다(`git commit -s`). 절차는 CONTRIBUTING.md.
- 커밋은 작고 한 가지 목적만 담는다. 포맷 변경과 로직 변경을 섞지 않는다.
- PR 은 템플릿(.github/PULL_REQUEST_TEMPLATE.md)을 따른다: 목적, 변경 요약, 테스트 방법, 체크리스트(게이트 통과, 문서 갱신, ADR 필요 여부, 보안 체크리스트).
- 리뷰 없이 머지하지 않는다. 에이전트 작업은 최소한 review-loop(N5/N6)을 통과해야 한다.

## 보안 리뷰 체크리스트 (PR 마다 확인)
- [ ] 비밀·토큰·개인정보가 코드, 테스트 픽스처, 로그, 리포트에 들어가지 않았다. `.env` 는 읽지도 커밋하지도 않는다(예시는 `.env.example`).
- [ ] 외부 입력(콘텐츠 파일, CLI 인자, 가져오기 JSON)은 스키마로 검증되고, 경로 조작(`..`, 절대 경로, 심볼릭 링크)이 차단된다.
- [ ] 셸 호출이 있다면 인자 리스트로 호출하고(`shell=True` 금지) 사용자 입력을 명령 문자열에 넣지 않는다.
- [ ] 역직렬화는 안전한 로더만 쓴다(`yaml.safe_load`, `json`). `pickle`, `eval`, `exec` 금지.
- [ ] 새 의존성은 라이선스(Apache-2.0 호환)와 알려진 취약점을 확인했다(`uv lock` 갱신 포함). CI 의존성 취약점 스캔(`.github/workflows/security.yml` 의 pip-audit)에서 고위험 이상 0건이어야 한다.
- [ ] 외부 네트워크 호출(AI 튜터 등)은 명시적 설정으로만 켜지고, 키 없이도 나머지 기능이 동작한다.
- [ ] 파일 쓰기는 저장소/콘텐츠/리포트 루트 안으로 제한되고, 덮어쓰기 전에 대상이 확인된다.
- [ ] 오류 메시지가 내부 경로·스택을 사용자에게 그대로 노출하지 않는다(디버그 모드 제외).
- [ ] 서버 모드(`api/`, `web/`): CSRF 방어, 보안 헤더(CSP, HSTS)를 적용했다. 릴리스마다 OWASP ASVS Level 2 체크리스트(`docs/ops/asvs-l2-checklist.md`, V2 인증·V3 세션·V4 접근제어 우선)를 점검한다.

## 라이선스와 콘텐츠
- 코드는 Apache-2.0, `curriculum/` 콘텐츠 기여는 CC BY 4.0 이다. 외부 자료는 본문을 복제하지 않고 링크만 건다.

## 문서와 릴리스
- 사용자에게 보이는 동작이 바뀌면 README 와 관련 docs/ 를 같은 PR 에서 갱신한다.
- **CHANGELOG.md 는 필수**이며 Keep a Changelog 형식을 따른다. 사용자에게 보이는 변경은 `## [Unreleased]` 에 기록하고, 보안 수정은 `### Security` 항목에 적는다.
- 릴리스는 PRD §14 를 따른다: SemVer 2.0.0, Git 태그 + GitHub Release. Docker 이미지 태그는 Phase 2 서버 모드부터, axe 접근성 CI 는 `web/` 이 생기는 Phase 2 부터 적용한다.
- 용어: 문서에서는 "진행도"(PRD 정식 용어)를 쓴다. 코드 식별자와 CLI 출력의 "진도"/`progress` 는 허용한다.
- 기여 절차는 CONTRIBUTING.md, 취약점 신고는 SECURITY.md 를 따른다.

## 에이전트 운영 규칙 (멀티 세션, 토큰 절약)
- 메시지는 완료·차단·결정 요청 때만 보낸다. 확인·감사·중간 보고는 보내지 않고, 10줄 이내 핵심만 쓴다.
- 큰 파일은 grep/sed 로 필요한 절만 읽고, 같은 파일을 반복해서 읽지 않는다. Glob/Grep 으로 범위를 좁힌다.
- 검증 출력은 마지막 3~5줄만, diff 는 `--stat` 만 보고에 붙인다.
- 끝나면 보고하고 대기한다. 다른 세션 상태를 폴링하지 않는다.
- 세션 안에서 서브에이전트를 만들지 않는다(워크플로 스킬을 사용자가 명시 실행하는 경우 제외).
- 문서 수정은 묶어서 한 커밋으로 낸다.
- 모델: 기본은 Opus 5(`claude-opus-5`)이며 `.claude/agents/*.md` 의 `model` 도 이에 맞춘다. 상위 모델이 필요하면 이유와 범위를 오케스트레이터에 요청해 승인받는다(사용자 지시, 2026-11-11).
