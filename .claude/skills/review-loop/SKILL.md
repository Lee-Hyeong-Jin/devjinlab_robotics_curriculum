---
name: review-loop
description: 루프 노드 L2 단독 실행 - 작업 트리 변경을 리뷰하고, blocking finding 마다 회의론자 2명이 반박을 시도하고, 살아남은 것만 고치기를 깨끗해질 때까지(최대 2라운드) 반복하는 워크플로를 실행한다. 인자: 리뷰 대상 설명(선택).
argument-hint: "[target]"
disable-model-invocation: true
---

사용자가 `/review-loop` 로 명시적으로 호출했다. 이것은 다중 에이전트 워크플로 실행에 대한 사용자의 옵트인이다.

1. `git status --short` 로 변경이 있는지 확인한다. 변경이 없고 `$ARGUMENTS` 도 없으면 리뷰할 것이 없다고 말하고 끝낸다.
2. Workflow 도구를 `name: "review-loop"` 로 호출한다. `$ARGUMENTS` 가 있으면 `args: {"target": "<내용>"}` (예: "HEAD~3..HEAD 의 커밋").
3. 결과를 요약한다: 라운드별 blocking/confirmed 수, 수정 내역, 남은 minor findings 목록(사용자가 판단).

워크플로 본문: .claude/workflows/review-loop.js
