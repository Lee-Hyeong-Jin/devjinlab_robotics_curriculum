---
name: milestone
description: 마일스톤 하나를 개발 그래프(spec → decompose → implement/verify 루프 → review 루프 → acceptance 게이트 → integrate)로 끝까지 돌린다. 인자: 마일스톤 id (harness/roadmap.yaml).
argument-hint: "<milestone-id> [--parallel]"
disable-model-invocation: true
---

사용자가 `/milestone` 로 명시적으로 호출했다. 이것은 다중 에이전트 워크플로 실행에 대한 사용자의 옵트인이다.

1. `$ARGUMENTS` 의 첫 토큰이 마일스톤 id 다. 비어 있으면 `python3 -I scripts/harness/roadmap.py next` 의 결과를 쓰고, 그것도 null 이면 사용자에게 id 를 묻는다.
2. `python3 -I scripts/harness/roadmap.py get <id>` 로 존재를 확인하고 goal 을 한 줄로 보여준다. 상태가 `done` 이면 다시 돌릴지 확인한다.
3. 현재 브랜치가 main/master 면 먼저 작업 브랜치를 만든다(`git switch -c feat/<id>`).
4. `python3 -I scripts/harness/roadmap.py set <id> in_progress` 를 실행한다.
5. Workflow 도구를 `name: "milestone"` 로 호출한다. `args: {"milestone": "<id>"}`. `--parallel` 이 있으면 `"parallelTasks": true` 를 추가한다(파일이 겹치지 않는 태스크만 병렬화됨).
6. 끝나면 status, 커밋, 보고서 경로, blocked 태스크, 미충족 수용조건을 요약한다.

워크플로 본문: .claude/workflows/milestone.js. 그래프 정의: harness/graph.md.
