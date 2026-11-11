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

### 워크트리 세션 주의

병렬 세션은 각자 `.claude/worktrees/<name>/` 워크트리에서 일한다. 훅이 워크트리에서 어떻게 해석되는지 알아야 "훅이 조용히 꺼진" 상태나 "막혀서 아무것도 못 하는" 상태를 피할 수 있다.

**스크립트 해석 순서.** 각 훅 명령은 `git rev-parse --show-toplevel`(실패하면 `$CLAUDE_PROJECT_DIR`, 그것도 없으면 `$PWD`)을 루트로 잡고 거기서 `scripts/harness/<스크립트>` 를 찾는다. cwd 가 워크트리의 어느 하위 디렉터리든 같은 스크립트를 찾는다. 스크립트가 없을 때는:
- 저장소에 `harness/` 가 있으면(= 이 저장소인데 스크립트만 없는 상태) **PreToolUse 가드는 deny 로 차단**하고(fail-closed), Stop 은 "게이트를 건너뛴다"는 경고만 stderr 로 남긴다. Stop 을 차단하면 턴을 끝낼 방법이 없어 세션이 갇히므로 의도적으로 열어 둔다 — 같은 검사는 CI 가 강제한다.
- `harness/` 도 없으면(다른 저장소) 모든 훅이 조용히 `exit 0`.

**실측 결과 (2026-11-11, 새 `git worktree add --detach` 워크트리에서 settings.json 의 훅 명령을 페이로드와 함께 직접 실행).**

| 시나리오 | SessionStart | PreToolUse 가드 | PostToolUse 포맷 | Stop 게이트 |
|---|---|---|---|---|
| A. cwd = 워크트리 루트 | 상태 주입 | 위험 명령 deny | ruff 포맷 적용 | 실패 시 block |
| B. cwd = 워크트리 하위(`src/`), `CLAUDE_PROJECT_DIR` = 같은 워크트리 | 정상 | 정상 | 정상 | 정상 |
| C. cwd = 워크트리 하위, `CLAUDE_PROJECT_DIR` 없음 | 정상 | 정상 | 정상 | 실패 시 block |
| D. 하네스 저장소인데 `scripts/harness/` 없음 | 무동작 | **deny(스크립트 없음 사유)** | 무동작 | 경고 후 통과 |
| E. 하네스가 아닌 저장소·저장소 밖 | 무동작 | 무동작 | 무동작 | 무동작 |

예전에는 cwd 기준으로만 스크립트를 찾아서, 메인 체크아웃(`scripts/harness/` 없음)에서 시작한 세션이 워크트리 하위 디렉터리로 `cd` 하면 가드와 게이트가 경고 없이 모두 꺼졌다(fail-open). 지금은 C 가 정상 동작하고 D 에서 가드가 차단한다.

**규칙.**
- 세션은 해당 워크트리 루트에서 시작하는 것이 좋다(하위 디렉터리에서도 훅은 동작하지만 명령 경로가 헷갈린다).
- 세션은 시작할 때 읽은 훅 설정을 캐시한다. `integration` 을 머지해 `.claude/settings.json` 이나 `scripts/harness/` 가 바뀌었으면 `/hooks` 를 열어 다시 읽히거나 세션을 재시작한다. 오래된 훅 명령이 사라진 스크립트 경로를 가리켜 Bash 가 계속 막힌 사례가 있었다(platform-dev-agent-harness 세션).
- 훅이 Bash 를 막는데 원인이 훅 자체라면 우회하지 말고 사용자에게 `/hooks` 재로드나 세션 재시작을 요청한다. 다른 세션에 대신 실행을 부탁하지 않는다.
- 가드 차단 문구는 명령 문자열 전체에 정규식으로 걸린다. 테스트 페이로드나 heredoc 안의 문자열도 차단되므로, 그런 텍스트는 Write 도구로 파일에 쓴다.
- 새 워크트리에서 훅을 점검하려면: 훅 명령을 `.claude/settings.json` 에서 꺼내 워크트리 루트와 하위 디렉터리 각각에서 이벤트별 JSON 페이로드를 stdin 으로 넣어 실행하고, 가드는 deny JSON, Stop 은 실패 코드에 대해 `"decision": "block"` 을 내는지 확인한다. `scripts/harness/` 를 잠시 다른 이름으로 옮겨 D 시나리오(가드 deny)도 확인한다.

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
- `pyproject.toml` 이 있으므로 check.sh 는 Python 스택(ruff, ruff format, mypy, pytest+커버리지)을 검사하고 Stop 게이트가 활성이다.
- 로드맵 마일스톤 내용은 docs/PRD.md(0.1 Draft) 기반 초안이며 설계 세션 결과에 따라 바뀐다. 구조만 확정.
