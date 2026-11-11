---
paths:
  - "curriculum/**"
  - "docs/curriculum/**"
---

# 커리큘럼 콘텐츠 규칙

- 콘텐츠 언어는 한국어, 기술 용어는 영문 병기(예: 정기구학(forward kinematics)).
- 레슨은 YAML frontmatter 가 있는 Markdown. 필수 필드: id, title, prerequisites, estimated_minutes, objectives, tags (docs/curriculum/LESSON_TEMPLATE.md). 코드의 콘텐츠 스키마가 있으면 그것이 우선이다.
- id 는 파일 경로와 일치시키고(`<track>/<module>/<lesson>`), 선수지식은 id 로 참조하며 순환이 없어야 한다.
- 학습 목표는 관찰 가능한 동사로 쓴다("설명할 수 있다", "구현할 수 있다", "계산할 수 있다").
- 수식은 KaTeX(`$...$`, `$$...$$`), 코드는 Python 우선. 이미지·영상은 상대 경로 또는 URL 로 참조하고 출처를 적는다.
- Activity 타입은 reading, quiz, lab, project, external 만 사용. lab 은 world/controller_template/judge 참조를 가진다.
- 외부 자료(논문, 강의)는 external Activity 로 연결하고, 본문을 통째로 옮기지 않는다. research_notes/ 의 조사 결과는 출처로 인용한다.
- 콘텐츠를 바꾼 뒤 `rc validate` 가 있으면 실행한다.
