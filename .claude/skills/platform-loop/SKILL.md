---
name: platform-loop
description: 개발 그래프의 바깥 루프(L0)를 실행한다. harness/roadmap.yaml 에서 다음 마일스톤을 골라 milestone 워크플로를 돌리고, 끝나면 다음 마일스톤으로 넘어간다. 인자: 최대 마일스톤 수(기본 2).
argument-hint: "[maxMilestones]"
disable-model-invocation: true
---

사용자가 `/platform-loop` 로 명시적으로 호출했다. 이것은 다중 에이전트 워크플로 실행에 대한 사용자의 옵트인이다.

1. 먼저 `python3 -I scripts/harness/roadmap.py summary` 를 실행해 현재 상태를 사용자에게 한 줄로 보여준다. 실행 가능한 마일스톤이 없으면 그렇게 말하고 끝낸다.
2. 현재 브랜치가 main/master 면 먼저 작업 브랜치를 만든다(`git switch -c feat/<milestone-id>` 또는 워크트리).
3. Workflow 도구를 `name: "platform-loop"` 로 호출한다. `$ARGUMENTS` 가 숫자면 `args: {"maxMilestones": <숫자>}`, 비어 있으면 args 생략.
4. 워크플로가 끝나면 결과(마일스톤별 status, 커밋, 보고서 경로)를 요약하고, `blocked` 가 있으면 reports/milestones/<id>.md 의 미해결 항목을 사용자에게 보여준다.

주의: 워크플로 스크립트 본문은 .claude/workflows/platform-loop.js 에 있다. 그래프 정의는 harness/graph.md.
