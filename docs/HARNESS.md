# 개발 하네스 (Harness)

이 저장소는 플랫폼을 **그래프 엔지니어링** 방식으로 개발한다. 개발 과정을 노드(작업/게이트)와 엣지(흐름), **루프 노드**(조건 만족까지 반복)로 정의하고, Claude Code 가 그 그래프를 실행한다. 사람은 그래프를 설계하고, 게이트의 판정 근거를 보고, blocked 된 지점에서 결정을 내린다.

그래프 자체는 [harness/graph.md](../harness/graph.md) 에 있다. 이 문서는 그래프를 돌리는 **하네스 구성요소**를 설명한다.

## 구성요소

| 계층 | 위치 | 역할 |
|---|---|---|
| 상태 | `harness/roadmap.yaml` | 마일스톤 상태 저장소(todo / in_progress / done / blocked). 바깥 루프가 읽고 쓴다. |
| 상태 도구 | `scripts/harness/roadmap.py` | `summary`, `next`, `get`, `set` 로 로드맵을 결정적으로 읽고 쓴다. |
| 실행기 | `.claude/workflows/*.js` | 그래프를 실행하는 Workflow 스크립트. 루프·분기·팬아웃은 스크립트가(결정적으로), 각 노드의 내용은 에이전트가 담당. |
| 노드 실행자 | `.claude/agents/*.md` | planner, implementer, verifier, reviewer, acceptance-tester, integrator + 도메인(curriculum-designer, research-scout). |
| 게이트 | `scripts/harness/check.sh` | 린트·타입·테스트. 스택(pyproject.toml / package.json)을 자동 감지. Phase 1 은 Python(uv + ruff + pytest). |
| 훅 | `.claude/settings.json` → `scripts/harness/*.sh, *.py` | 세션 시작 컨텍스트, Bash 가드, 저장 후 포맷, 턴 종료 시 검증 게이트. |
| 진입점 | `.claude/skills/*/SKILL.md` | `/platform-loop`, `/milestone`, `/verify-fix`, `/review-loop`, `/graph-status`, `/verify`, `/adr`, `/new-lesson`. |
| 규칙 | `.claude/rules/*.md` | 엔지니어링 규칙(전역), 콘텐츠 규칙(curriculum/ 경로 한정). |

## 워크플로(그래프 실행기)

| 워크플로 | 그래프 위치 | 루프 | 종료 조건 |
|---|---|---|---|
| `platform-loop` | L0 바깥 루프 | 마일스톤 단위 | 실행 가능 마일스톤 없음, blocked 발생, `maxMilestones`, 토큰 예산 |
| `milestone` | N1~N9 서브그래프 | L1(implement→verify, max 3), L2(review→skeptic→fix, max 2), L3(acceptance 재분해, max 2) | acceptance 통과 또는 최대 반복 → done / blocked |
| `verify-fix` | L1 단독 | verify→fix (max 3) | check.sh 통과 |
| `review-loop` | L2 단독 | review→skeptic×2→fix (max 2) | blocking finding 0 |

워크플로는 Claude Code 의 Workflow 도구로 실행되며, 에이전트를 여러 개 띄우므로 **사용자가 스킬로 명시 실행**할 때만 돈다. `milestone` 은 `platform-loop` 가 `workflow('milestone')` 로 중첩 호출한다(중첩은 한 단계만 가능하므로 `milestone` 안에는 L1/L2 가 인라인되어 있다).

## 훅

| 이벤트 | 스크립트 | 동작 |
|---|---|---|
| SessionStart | `session_start.sh` | 브랜치, 변경 수, 스택, 로드맵 요약을 컨텍스트로 주입 |
| PreToolUse(Bash) | `guard_bash.py` | 파괴적 명령(rm -rf /, reset --hard, 강제 push, sudo, .env 쓰기 등) deny, 위험 명령(push, rebase, docker rm, 재귀 삭제) ask |
| PostToolUse(Write/Edit) | `format_file.sh` | .py → ruff format + fix, JS/TS/JSON → prettier(있을 때만). 실패해도 도구는 막지 않음 |
| Stop | `stop_gate.sh` | 커밋되지 않은 코드 변경이 있고 스택이 감지되면 `check.sh --quick` 실행, 실패 시 턴 종료를 막고 수정 요구 |

훅 변경 후에는 `/hooks` 를 한 번 열거나 세션을 재시작해야 반영된다.

## 권한

`.claude/settings.json` 의 permissions: 읽기·검색, 읽기 전용 git, uv/ruff/pytest/npm 스크립트, 하네스 스크립트는 allow. `.env`, `~/.ssh`, `~/.aws` 읽기와 sudo·강제 push·reset --hard 는 deny. push·rebase·docker 는 ask. 개인 취향은 `.claude/settings.local.json`(gitignore 됨)에 둔다.

## 일상 흐름

1. `/graph-status` 로 상태 확인.
2. 작은 변경은 그냥 작업하고 `/verify` 로 게이트 통과 확인(Stop 훅이 어차피 검사한다).
3. 마일스톤 단위 작업은 작업 브랜치에서 `/milestone <id>`. 여러 개를 연달아 돌리려면 `/platform-loop N`.
4. 결과는 `reports/milestones/<id>.md`, 명세는 `docs/specs/<id>.md`, 결정은 `docs/adr/`.
5. blocked 가 나오면 보고서의 미해결 항목을 보고 사람이 결정한 뒤(로드맵 수정, ADR 작성) 다시 돌린다.

## 그래프 확장하기

- 새 노드: `harness/graph.md` 표에 추가 → 필요하면 `.claude/agents/` 에 실행자 추가 → 워크플로 스크립트에 연결.
- 새 루프: 종료 조건과 최대 반복 수를 반드시 정의. 각 반복은 이전 반복의 구조화된 피드백을 입력으로 받아야 한다.
- 새 게이트: 실행 가능한 검증(명령·테스트)으로 판정하도록 하고, 판정 근거를 출력 스키마에 포함.
- 새 마일스톤: `harness/roadmap.yaml` 에 id/title/status/depends_on/goal/acceptance/note 로 추가. acceptance 는 검증 가능하게.

## 현재 전제

- 스택: Phase 1 은 Python 단일(uv + ruff + pytest), 콘텐츠는 Markdown + YAML, CLI + 정적 사이트. Node 경로는 감지 로직에 남아 있지만 기본 가정은 Python.
- `pyproject.toml` 은 아직 없다(P0-1 마일스톤에서 생성). 그때까지 check.sh 는 "no build stack detected" 를 출력하고 Stop 게이트는 비활성이다.
- 로드맵 마일스톤 내용은 docs/PRD.md(0.1 Draft) 기반 초안이며 설계 세션 결과에 따라 바뀐다. 구조만 확정.
