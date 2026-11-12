# 0014. 논문은 코스 레지스트리에 한 번, 레슨은 id 로 참조한다

- 상태: accepted
- 날짜: 2026-11-12
- 관련: `research_notes/연구 트랙 설계/lesson-standard.md` §10–11, docs/curriculum/CONTENT_MODEL.md,
  docs/PRD.md FR-1·FR-6, ADR 0012(레슨 번역 파일)

## 맥락

연구 트랙은 레슨마다 필독 논문을 지정한다. 설계 단계의 서지가 이미 131편이고 같은 논문이 여러
레슨에 걸친다. 지금 스키마에는 `Resource(title, url, kind, note)` 뿐이어서

- 저자·연도·venue·역할을 `note` 문자열에 밀어넣어야 하고,
- 같은 논문을 참조하는 레슨마다 서지를 중복 기재해야 하고(131편 × 레슨 수),
- `ResourceKind` 에 `paper` 가 없었다.

그래서 논문 메타데이터를 어디에 두고, 무엇을 원본으로 삼을지 정해야 한다.

## 선택지

| 선택지 | 장점 | 단점 |
|---|---|---|
| A. 레슨 `resources[]` 에 그대로 쓴다 | 스키마 변경 0 | 서지가 레슨마다 중복되고 저자·연도를 구조적으로 쓸 수 없다. 131편이 수백 번 복사된다 |
| B. 코스 레지스트리 `papers.yaml` + 레슨이 id 로 참조 | 서지를 한 번만 쓴다. `rc` 가 검증·출력할 수 있다. 추가 전용 | 파일이 하나 늘고, 참조 무결성 규칙이 필요하다 |
| C. 저장소 전역 레지스트리 하나 | 코스 사이 중복까지 없앤다 | 코스 디렉터리가 자기 완결이라는 성질이 깨진다(코스는 독립적으로 로드된다) |

B 를 택한다. C 는 "코스 디렉터리 하나가 코스 하나"라는 콘텐츠 모델의 기본 성질을 깨고, 코스를
따로 배포할 수 없게 만든다.

## 결정

### 어디에 무엇을 쓰는가

`curriculum/<course>/papers.yaml` 은 **서지(bibliography)** 다 — 누가 무엇을 어디에 썼고, 링크를
확인했는지.

```yaml
papers:
  - id: mayne-1966
    title: "A second-order gradient method for determining optimal trajectories"
    authors: ["D. Q. Mayne"]
    year: 1966
    venue: "International Journal of Control"
    url: "https://doi.org/..."
    verified: true      # 링크를 실제로 열어 확인했는가
    role: seminal       # 기본 역할(레슨이 덮어쓸 수 있다)
    note: "전체"        # 기본 메모(레슨이 덮어쓸 수 있다)
```

레슨 front matter 는 **어떤 논문을 어떻게 읽히는가**다 — 교육적 결정이므로 레슨에 속한다.

```yaml
papers:
  - id: mayne-1966
    role: seminal       # 생략 시 레지스트리 값
    required: true      # 필독 여부. 레슨에만 있다
    note: "§3 의 2차 전개"  # 생략 시 레지스트리 값
```

**원본은 레슨 쪽이다**(curriculum-researcher 와 합의, 2026-11-12). "어떤 논문을 필독으로
지정하는가"는 레슨의 결정이고, 레지스트리는 그 논문이 무엇인지만 말한다. 따라서:

- `role` 은 레슨 참조가 레지스트리를 **덮어쓴다**. 같은 논문이 한 레슨에서는 원전(`seminal`),
  다른 레슨에서는 비판 대상(`critique`)일 수 있고 실제로 그런 경우가 있다.
- `required` 는 레지스트리에 두지 않는다. 레지스트리에서는 의미가 없다.
- 레지스트리의 `lessons[]` 는 **선택적 역색인**이다. 레슨이 아직 쓰이지 않은 설계 단계에서
  유지되던 것이고, 레슨의 `papers[]` 가 이긴다. `rc validate` 는 교차 검증만 하고 불일치는
  **경고**다. 레슨이 다 쓰이면 지워도 된다.

역할 어휘: `seminal | standard | frontier | critique | survey`.

### 검증 (규칙 10)

| 검사 | 수준 |
|---|---|
| 레슨이 참조한 id 가 레지스트리에 있다 | 오류 |
| 레지스트리 id 가 유일하다 | 오류 |
| 레지스트리 `url` 이 http(s) 형식이다(네트워크 접근 없음, 규칙 5 와 동일) | 오류 |
| 한 레슨이 같은 논문을 두 번 나열하지 않는다 | 오류 |
| 논문을 지정한 레슨은 `required: true` 를 최소 1개 갖는다 | 오류 |
| 레지스트리에 있지만 아무 레슨도 참조하지 않는 논문 | **경고** |
| 레지스트리 `lessons[]` 가 레슨들의 실제 참조와 다르다 | **경고** |

마지막 두 개를 경고로 둔 이유: 집필 중에는 서지가 레슨보다 먼저 들어온다. 이것을 오류로 만들면
논문을 먼저 정리해 두는 작업 방식이 CI 를 빨갛게 만든다.

이를 위해 `ContentError` 에 `severity: "error" | "warning"` 을 추가했다. `rc validate` 는 경고를
출력하지만 종료 코드는 0 이고, 콘텐츠를 거부해야 하는 호출자(`ProgressService.load_curriculum`)는
`validate.blocking()` 으로 경고를 걸러낸다. 로더가 내는 문제는 전부 오류다 — 파싱되지 않는 파일이
경고인 적은 없다.

### 레지스트리 없는 코스

`papers.yaml` 이 없으면 `course.papers == []` 이고 규칙 10 은 아무 말도 하지 않는다. 연구 트랙
이전의 코스(`robotics-expert`, 레슨 50개)는 **무수정으로 통과한다**. 이 성질을 테스트로 고정했다
(`tests/test_papers.py::test_a_course_without_a_registry_still_loads`).

### 출력

- `rc papers <lesson_id>`: 필독 먼저, 역할·서지 한 줄·메모·링크. `verified: false` 는 `(미확인)`.
- API `GET /lessons/{id}` 의 `papers[]`, 정적 사이트와 web 레슨 화면의 "필독 논문" 절.
  (이 커밋 다음 단계)

## 결과

- 얻는 것: 서지를 한 번만 쓰고, 참조 무결성을 기계가 검사한다. 같은 논문의 레슨별 역할 차이를
  표현할 수 있다. 기존 콘텐츠는 영향이 없다.
- 감수하는 것: 코스 디렉터리에 파일이 하나 늘고, 레슨이 혼자서는 완결되지 않는다(서지를 보려면
  레지스트리가 필요하다). 콘텐츠 모델에 "경고" 개념이 생겼다.
- 번역: 논문 제목·저자·venue 는 번역하지 않는다(발표된 그대로가 서지 정보다). 레슨 참조의 `note`
  는 편집 문장이라 번역 가치가 있지만 `<lesson>.<lang>.yaml` 확장은 이번 범위가 아니다. 필요해지면
  ADR 0012 의 구조를 따라 추가한다.
- 후속: 사이트·API·web 표시, ` ```problemset ` 블록(lesson-standard.md §11-3),
  `verified: false` 를 링크 점검 리포트의 우선 대상으로 삼기(§11-7).
