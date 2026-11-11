---
name: adr
description: 아키텍처 결정 기록(ADR)을 docs/adr/ 에 작성한다. 스택, 라이브러리, 저장 방식, 알고리즘 선택 등 되돌리기 비싼 결정을 내릴 때 사용. 인자: 결정 제목.
argument-hint: "<decision title>"
---

1. `ls docs/adr/` 로 다음 번호(NNNN)를 정한다. 같은 주제의 기존 ADR 이 있으면 새 ADR 에서 "Supersedes" 로 연결한다.
2. docs/adr/TEMPLATE.md 를 복사해 `docs/adr/NNNN-<kebab-title>.md` 를 만든다. `$ARGUMENTS` 가 제목이다.
3. 섹션을 채운다: 맥락(왜 지금 결정해야 하나), 선택지(최소 2개, 장단점 표), 결정, 결과(얻는 것/잃는 것/후속 작업), 상태(proposed | accepted | superseded).
4. 근거가 research_notes/ 나 docs/PRD.md 에 있으면 경로를 인용한다. 근거가 없으면 research-scout 에이전트로 짧게 조사한 뒤 쓴다.
5. 결정이 CLAUDE.md 의 Commands/Architecture 에 영향을 주면 그 섹션도 갱신한다.
