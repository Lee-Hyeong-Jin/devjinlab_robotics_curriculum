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

front matter에 정의되지 않은 키가 있으면 에러다(오타 방지). `body`, `path`는 예약어.

### Activity

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | slug | O | 코스 전체에서 유일. 관례: `<lesson-id>-<kind>` |
| `kind` | `reading` \| `quiz` \| `lab` \| `exercise` | O | 활동 종류 |
| `title` | str | O | 표시 이름 |
| `estimated_minutes` | int ≥ 1 | - | 활동 단위 예상 시간 |
| `lab_id` | slug | `kind: lab`일 때만 | `labs/<lab_id>/`의 실습을 가리킴. 다른 kind에서는 금지 |

> PRD FR-1.3의 `project`, `external`은 아직 미지원. 필요해지면 `ActivityKind`에 추가한다.

## 검증 규칙 (`rc validate [PATH]`)

`PATH`는 코스 디렉터리이거나 코스 디렉터리들을 담은 상위 디렉터리(기본 `curriculum/`).
에러는 `파일경로: 메시지` 형식으로 모두 출력하고 종료 코드 1을 반환한다.

| # | 규칙 | 검출 위치 |
|---|---|---|
| 1 | `course.yaml` / `module.yaml` / front matter가 스키마를 만족 (필수 필드, 타입, 범위, 모르는 키 없음) | loader |
| 2 | 목록(`modules`, `lessons`)에 적힌 항목이 실제로 존재하고, 디스크의 항목이 목록에 모두 있음 | loader |
| 3 | `lab` 활동에는 `lab_id`가 있고, 다른 kind에는 없음 | model |
| 4 | 코스 내 모든 ID(코스·모듈·레슨·활동)가 유일 | validate |
| 5 | `prerequisites`의 각 항목이 존재하는 레슨 ID이며 자기 자신이 아님 | validate |
| 6 | 선수지식 그래프에 순환이 없음 (DAG) | validate |
| 7 | 코스에 모듈이 1개 이상, 모듈에 레슨이 1개 이상 | validate |

성공 시 `OK: N lessons in M modules`.

## 파이썬 API

```python
from pathlib import Path
from robotics_curriculum.content import load_course, validate_course, check

course = load_course(Path("curriculum/robotics-basics"))  # LoadError on schema problems
errors = validate_course(course)  # list[ContentError]
courses, errors = check(Path("curriculum"))  # load + validate, never raises
```
