---
name: verify-fix
description: 루프 노드 L1 단독 실행 - 검증 게이트(scripts/harness/check.sh)를 돌리고 실패를 고치기를 통과할 때까지(최대 3회) 반복하는 워크플로를 실행한다. 인자: 추가 확인 범위(선택).
argument-hint: "[scope]"
disable-model-invocation: true
---

사용자가 `/verify-fix` 로 명시적으로 호출했다. 이것은 다중 에이전트 워크플로 실행에 대한 사용자의 옵트인이다.

1. `bash scripts/harness/check.sh --quick` 를 한 번 직접 실행한다. 이미 통과하고 `$ARGUMENTS` 도 없으면 "이미 green" 이라고 말하고 끝낸다.
2. Workflow 도구를 `name: "verify-fix"` 로 호출한다. `$ARGUMENTS` 가 있으면 `args: {"scope": "<내용>"}`.
3. 결과(ok, 남은 failures)를 요약한다. 3회 후에도 실패면 failures 를 그대로 보여주고 사람 판단을 요청한다.

워크플로 본문: .claude/workflows/verify-fix.js
