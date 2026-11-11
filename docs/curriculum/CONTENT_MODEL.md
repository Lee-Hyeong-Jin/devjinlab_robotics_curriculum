# 커리큘럼 콘텐츠 모델

콘텐츠는 `curriculum/` 아래의 파일이 원본이다 (PRD 8절). 계층은
`Course(Track) > Module > Lesson > Activity`이며 디렉터리 구조와 1:1로 대응한다.
스키마 구현: `src/robotics_curriculum/content/models.py`.

## 디렉터리 구조

```
curriculum/
└── <course-dir>/                 # 코스(트랙) 하나 = 디렉터리 하나
    ├── course.yaml               # 코스 메타데이터 + 모듈 순서
    └── <module-dir>/             # 모듈 하나 = 디렉터리 하나
        ├── module.yaml           # 모듈 메타데이터 + 레슨 순서
        └── <lesson>.md           # 레슨 하나 = YAML front matter + Markdown 본문
```

- 디렉터리/파일 이름은 소문자 슬러그(`m1-math-physics`, `vectors-matrices.md`).
  `.`/`_`로 시작하는 디렉터리는 무시한다.
- `course.yaml`의 `modules`, `module.yaml`의 `lessons`는 **교육 순서**를 정한다.
  생략하면 이름순 정렬. 명시했을 때 디스크에 있는데 목록에 없는 항목은 에러다
  (실수로 누락된 콘텐츠를 막기 위함).
- Activity는 레슨 front matter의 `activities` 목록 안에 둔다. 별도 파일 없음.

## `course.yaml`

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | slug | O | 코스 ID (`robotics-basics`) |
| `title` | str | O | 표시 이름 |
| `summary` | str | O | 한두 문장 요약 |
| `tags` | list[str] | - | 기본 `[]` |
| `modules` | list[str] | - | 모듈 디렉터리 이름, 순서대로 |

## `module.yaml`

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | slug | O | 모듈 ID (`m1-math-physics`) |
| `title` | str | O | 표시 이름 |
| `summary` | str | O | 요약 |
| `level` | `기초` \| `중급` \| `고급` | - | 모듈 수준. 기본 없음 |
| `lessons` | list[str] | - | 레슨 파일 이름(확장자 제외), 순서대로 |

## 레슨 front matter (`<lesson>.md`)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | slug | O | 레슨 ID. 코스 전체에서 유일. 관례: `<모듈 접두어>-<주제>` (`m1-vectors-matrices`) |
| `title` | str | O | 표시 이름 |
| `summary` | str | O | 한두 문장 요약 |
| `objectives` | list[str] | O | 학습 목표, 1개 이상 |
| `prerequisites` | list[slug] | - | 선수 **레슨 ID** 목록. 기본 `[]` |
| `difficulty` | int 1–5 | O | 난이도 |
| `estimated_minutes` | int ≥ 1 | O | 예상 소요 시간(분) |
| `tags` | list[str] | - | 기본 `[]` |
| `activities` | list[Activity] | - | 아래 참조. 기본 `[]` |
| `resources` | list[Resource] | - | 단계별 학습 자료(교재·강의·영상 등). 아래 참조. 기본 `[]` |

front matter에 정의되지 않은 키가 있으면 에러다(오타 방지). `body`, `path`는 예약어.

### Activity

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | slug | O | 코스 전체에서 유일. 관례: `<lesson-id>-<kind>` |
| `kind` | `reading` \| `quiz` \| `exercise` | O | 활동 종류 |
| `title` | str | O | 표시 이름 |
| `estimated_minutes` | int ≥ 1 | - | 활동 단위 예상 시간 |

> 시뮬레이터 실습(`lab`)은 지원하지 않는다. PRD FR-1.3의 `project`, `external`은 아직 미지원.
> 필요해지면 `ActivityKind`에 추가한다.
> `kind: quiz` 활동의 문항은 본문의 ` ```quiz ` 블록에 쓴다(아래 "본문 안의 퀴즈 블록").

### Resource

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `title` | str | O | 자료 이름 |
| `url` | str | - | 링크 |
| `kind` | `book` \| `course` \| `video` \| `article` \| `other` | - | 자료 종류 |
| `note` | str | - | 범위·메모 (예: `Ch. 3`) |

그 단계의 공부 방법은 front matter가 아니라 본문의 `## 이 단계 공부법` 절에 쓴다
(다음 `## ` 제목 전까지). `rc resources <lesson_id>`가 자료 목록과 함께 이 절을 출력한다
(`content.sections.extract_section`).


## 본문 안의 퀴즈 블록 (` ```quiz `)

레슨의 확인 퀴즈는 front matter가 아니라 **본문의 펜스 코드 블록** ` ```quiz `(내용은 YAML)로
정의한다(PRD FR-4.1, 부록 C.1). 레슨당 블록 여러 개를 허용하며 순서대로 이어 붙인다.
구현: `src/robotics_curriculum/content/quiz_block.py` (`parse_quiz(lesson)`).

````markdown
```quiz
activity: m1-vectors-matrices-quiz        # activities[] 중 kind: quiz 인 활동 id
questions:
  - id: q1
    type: single
    prompt: "두 벡터의 내적이 0이면 두 벡터는?"
    choices: ["평행하다", "직교한다", "같은 벡터다", "영벡터다"]
    answer: 1
    explanation: "내적이 0이면 사잇각이 90°이므로 직교한다."
    concept: { front: "내적이 0인 두 벡터의 관계", back: "직교(사잇각 90°)" }
  - id: q2
    type: short
    prompt: "3×3 회전행렬의 행렬식 값은?"
    answer: ["1", "+1"]
    explanation: "회전행렬은 직교행렬이고 반사를 포함하지 않으므로 det = +1."
```
````

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `activity` | slug | - | 이 블록이 속한 `kind: quiz` 활동 id. 레슨에 quiz 활동이 하나뿐이면 생략 가능, 둘 이상인데 생략하면 에러 |
| `questions[]` | list | O | 문항 목록, 1개 이상 |

문항(`questions[]` 항목):

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | slug | O | 레슨 안에서 유일 (`q1`) |
| `type` | `single` \| `multiple` \| `truefalse` \| `short` | O | 객관식 / 다중선택 / O·X / 단답. `multi`는 `multiple`의 별칭 |
| `prompt` | str (Markdown, 수식 허용) | O | 문항 |
| `choices[]` | list[str] | single·multiple만 | 선택지 2개 이상 |
| `answer` | 타입별 | O | single: 0-based 인덱스 · multiple: 인덱스 목록(중복 없음) · truefalse: `true`/`false` · short: 허용 답 문자열 목록(앞뒤 공백·대소문자·연속 공백 무시) |
| `explanation` | str | O | 해설. 채점 직후와 카드 뒷면에 표시 |
| `concept` | `{front, back}` | - | 지정하면 정오답과 무관하게 핵심 개념 카드를 만든다 |
| `tags[]` | list[str] | - | 보관만 한다 |

블록을 YAML 리스트(문항 목록)만으로 써도 `questions`로 읽는다(설계 §3.4 호환). 지원하지 않는
키(`card` 등)는 에러다.

**`activities`의 `kind: quiz` 항목과의 관계**: 활동 항목은 시간 추정·활동 체크용 *메타*이고,
본문 퀴즈 블록이 문항의 *실체*다. `rc quiz <lesson_id>`는 본문 블록을 풀고, 모든 문항에 답하면
블록이 가리키는 quiz 활동을 `activity_progress`에 `done`으로 기록한다. 블록이 없는 레슨에
`rc quiz`를 실행하면 에러다.

플래시카드: 오답 문항은 `<lesson_id>-quiz-<qid>`(앞면 = 문항 + 선택지, 뒷면 = 정답 + 해설),
`concept`가 있는 문항은 `<lesson_id>-concept-<qid>` 카드가 된다(이미 있으면 유지).
복습 일정은 SM-2(`docs/adr/0005-sm2-spaced-repetition.md`), `rc review`.
정적 사이트는 문항·선택지를 보여주고 정답·해설은 `<details>`로 접는다.

## 레슨 번역 (`<lesson>.<lang>.md`)

레슨 텍스트의 다른 언어 판은 **원문 옆의 형제 파일**로 둔다(ADR 0012). 파일 이름의 접미사가
언어를 정한다. 원문 언어는 한국어이며 `ko` 접미사는 쓰지 않는다.

```
m1-math-physics/
├── module.yaml
├── vectors-matrices.md        # 원문 (ko)
└── vectors-matrices.en.md     # 영어 번역
```

번역 파일은 **텍스트만** 담는다. 구조(선수지식·난이도·예상 시간·활동·자료)는 원문 파일에만 있고,
번역이 커리큘럼 그래프를 바꿀 수 없다.

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `title` | str | O | 번역된 레슨 제목 |
| `summary` | str | O | 번역된 요약 |
| `objectives` | list[str] | - | 번역된 학습 목표. 생략하면 원문 상속 |
| `tags` | list[str] | - | 생략하면 원문 상속 |
| `id` | slug | - | 쓰면 원문 레슨 `id` 와 같아야 한다 |
| `lang` | str | - | 쓰면 파일 이름 접미사와 같아야 한다 |

그 밖의 키(`prerequisites`, `difficulty`, `estimated_minutes`, `activities`, `resources`, …)는
오류다. 본문(front matter 아래)은 번역된 Markdown 이며, `## 이 단계 공부법` 절은 **그 언어의
제목**으로 쓴다(영어는 `## How to study this stage`). 추출기는 요청 언어의 제목을 먼저 찾고
없으면 한국어 제목으로 폴백한다.

```markdown
---
id: m1-vectors-matrices
lang: en
title: Vectors and matrices
summary: Vectors and matrices as robotics uses them.
objectives:
  - Explain the geometric meaning of the dot and cross products.
---

# Vectors and matrices

...

## How to study this stage

1. **Videos:** ...
```

### 언어 선택과 폴백

| 표면 | 언어를 고르는 방법 |
|---|---|
| 파이썬 API | `lesson.localized(lang)` → `LocalizedLesson`(`title`, `summary`, `objectives`, `tags`, `body`, `lang`, `translated`) |
| HTTP API | 요청의 `Accept-Language`. 응답의 `lang` 이 실제로 쓰인 언어, `available_languages` 가 가진 언어 목록 |
| 정적 사이트 | `rc site build --lang en` |
| CLI | `rc --lang en ...` (UI 문자열; 레슨 본문 출력도 같은 언어의 번역이 있으면 쓴다) |

번역이 없으면 원문(한국어)을 쓰고 `translated: false` 로 알린다. 즉 **번역은 선택**이며, 없다고
해서 오류가 아니다.

### 검증 (`rc validate`)

| 규칙 | 메시지 예 |
|---|---|
| 지원하지 않는 언어 접미사 | `unsupported translation language 'fr'` |
| `ko` 접미사 사용 | `'ko' is the language lessons are written in; drop the suffix` |
| 원문 없는 번역 | `translation has no lesson to translate (vectors-matrices.md is missing)` |
| `id` 불일치 | `translation id 'x' does not match lesson id 'y'` |
| `lang` 과 파일 이름 불일치 | `front matter says lang 'ko' but the file name says 'en'` |
| 본문이 빈 번역 | `'en' translation of 'm1-vectors-matrices' has an empty body` |

## 검증 규칙 (`rc validate [PATH]`)

`PATH`는 코스 디렉터리이거나 코스 디렉터리들을 담은 상위 디렉터리(기본 `curriculum/`).
에러는 `파일경로: 메시지` 형식으로 모두 출력하고 종료 코드 1을 반환한다.

| # | 규칙 | 검출 위치 |
|---|---|---|
| 1 | `course.yaml` / `module.yaml` / front matter가 스키마를 만족 (필수 필드, 타입, 범위, 모르는 키 없음) | loader |
| 2 | 목록(`modules`, `lessons`)에 적힌 항목이 실제로 존재하고, 디스크의 항목이 목록에 모두 있음 | loader |
| 3 | 코스 내 모든 ID(코스·모듈·레슨·활동)가 유일 | validate |
| 4 | `prerequisites`의 각 항목이 존재하는 레슨 ID이며 자기 자신이 아님 | validate |
| 5 | 선수지식 그래프에 순환이 없음 (DAG) | validate |
| 6 | 코스에 모듈이 1개 이상, 모듈에 레슨이 1개 이상 | validate |
| 7 | 자료 `url`이 있으면 `http(s)://호스트...` 형식 (네트워크 접속 없이 `urllib.parse`로 검사) | validate |
| 8 | 한 레슨 안에서 자료 `title`이 유일 | validate |
| 9 | 레슨 번역 파일(`<lesson>.<lang>.md`)이 텍스트를 담고 있고 id·언어가 일치 (위 "레슨 번역" 절) | loader/validate |
| 10 | 본문 ` ```quiz ` 블록이 파싱됨: YAML 오류, 모르는 `type`, `answer` 형태·범위, `explanation` 누락, 문항 `id` 중복, `activity` 참조 오류(없는 활동, quiz 활동이 둘 이상인데 생략)를 `lesson '<id>': quiz block N: question M: ...` 형식으로 보고 | validate |

성공 시 `OK: N lessons in M modules`.

## 레슨 ID와 진도 데이터

학습 진도(`rc start/stop/log/done`, `.rc/progress.db`)는 레슨 front matter의 `id` 문자열로
저장된다 (콘텐츠 테이블에 대한 FK 없음). 퀴즈 시도·카드·복습 기록(`rc quiz`, `rc review`)도
레슨 `id`와 문항 `id` 문자열로 저장된다. 따라서:

- 레슨 `id`는 `curriculum/` 아래 **모든 코스를 통틀어** 유일해야 한다. 진도 명령은
  여러 코스에 같은 레슨 ID가 있으면 에러로 거부한다.
- 이미 학습 기록이 있는 레슨의 `id`를 바꾸면 기존 기록이 그 레슨과 끊긴다(파일 이름·
  모듈 이동은 무관). 퀴즈 문항 `id`를 바꾸면 그 문항의 카드·시도 기록도 끊긴다. 바꿔야 한다면 `rc progress export` → JSON의 `lesson_id` 수정 →
  `rc progress import --replace`로 옮긴다.

## 파이썬 API

```python
from pathlib import Path
from robotics_curriculum.content import load_course, validate_course, check

course = load_course(Path("curriculum/robotics-basics"))  # LoadError on schema problems
errors = validate_course(course)  # list[ContentError]
courses, errors = check(Path("curriculum"))  # load + validate, never raises

from robotics_curriculum.content import parse_quiz

quiz = parse_quiz(course.iter_lessons()[0])  # LessonQuiz; QuizParseError on problems
quiz.questions  # list[QuizQuestion] in order
```
