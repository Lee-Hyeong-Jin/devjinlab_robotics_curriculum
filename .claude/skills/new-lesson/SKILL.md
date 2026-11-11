---
name: new-lesson
description: 커리큘럼 레슨 파일을 docs/curriculum/LESSON_TEMPLATE.md 형식으로 스캐폴딩한다. 인자: 트랙/모듈/레슨 id 와 제목. 콘텐츠 스키마(P0-2)가 코드로 확정되면 그 스키마를 우선한다.
argument-hint: "<track>/<module>/<lesson-id> \"<title>\""
---

1. `$ARGUMENTS` 에서 경로(`<track>/<module>/<lesson-id>`)와 제목을 읽는다. 없으면 사용자에게 묻는다.
2. 콘텐츠 루트는 `curriculum/` 이다. 코드에 콘텐츠 스키마가 있으면(예: `rc validate` 가 존재) 그 필수 필드를 따르고, 없으면 docs/curriculum/LESSON_TEMPLATE.md 의 frontmatter 를 따른다.
3. `curriculum/<track>/<module>/<lesson-id>.md` 를 템플릿으로 만든다. 같은 모듈의 기존 레슨을 읽어 선수지식(prerequisites) 후보를 제안한다. id 는 경로와 일치시킨다.
4. 학습 목표는 관찰 가능한 동사로 3개 내외, Activity 는 reading → quiz → project(또는 external) 순서의 자리만 만든다(본문은 TODO 로 표시). 단계별 공부법과 추천 자료 절의 자리도 만든다.
5. `rc validate` 가 있으면 실행해 통과를 확인한다. 없으면 frontmatter 필수 필드가 다 있는지 눈으로 확인한다.
6. 만든 파일 경로와 다음 할 일(본문 작성, 퀴즈 작성)을 한 줄로 보고한다. 깊은 콘텐츠 작성이 필요하면 curriculum-designer 에이전트를 쓴다.
