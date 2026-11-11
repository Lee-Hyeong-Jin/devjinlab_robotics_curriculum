---
name: graph-status
description: 개발 그래프의 현재 상태를 보여준다 - 로드맵 마일스톤 상태, 다음 실행 가능 마일스톤, 최근 마일스톤 보고서, 검증 게이트 결과. 읽기 전용.
argument-hint: "[milestone-id]"
---

읽기 전용으로 다음을 수집해 짧게 요약한다.

1. `python3 -I scripts/harness/roadmap.py summary` 와 `python3 -I scripts/harness/roadmap.py next`.
2. `$ARGUMENTS` 에 id 가 있으면 `python3 -I scripts/harness/roadmap.py get <id>` 와 reports/milestones/<id>.md(있으면), docs/specs/<id>.md(있으면)의 요점.
3. `bash scripts/harness/check.sh --quick` 결과 한 줄(통과/실패/스택 없음).
4. `git status --short | head` 와 `git log --oneline -5`.

출력: 마일스톤 표(id, 제목, 상태, note), 다음 실행 가능 마일스톤, 게이트 상태, 권장 다음 명령(`/milestone <id>`, `/verify-fix`, `/review-loop` 중 하나). 파일은 수정하지 않는다.
