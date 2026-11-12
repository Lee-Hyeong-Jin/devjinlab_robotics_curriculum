# 연구원 트랙 레슨 집필 지침 (Authoring the research track)

> **모듈 저자가 시작할 때 읽을 것 (5줄 요약)**
> 1. `research_notes/연구 트랙 설계/blueprint.md` 에서 **담당 모듈의 표**를 찾는다 — 그 행들이 과제 명세다.
> 2. 기준 레슨 `curriculum/robotics-research/c1-rigid-body-geometry-lie-groups/so3-se3-exponential.md`
>    (+ `.en.md`)를 **복사해서 시작한다**. 섹션 제목 10개는 §2 표 그대로 두고 바꾸지 않는다.
> 2-A. **모듈의 첫 레슨**에는 `## 시작 전 자가 진단`(3–5문항, 정답 공개)을 넣는다. 선수는
>    **잠금이 아니라 권장**이다 — "먼저 이수해야 한다" 같은 표현을 쓰지 않는다(lesson-standard §1-A).
> 3. 레슨마다 **D2 이상 유도 1개 이상**, 문제 세트 4–8문항(유형 3종 이상), 필독 논문 2–4편(URL 확인 필수),
>    재현 과제 1개(**코드로 판정 가능한** 수용 기준), 열린 문제 2–4개 — 하나라도 없으면 반송이다(§11).
> 4. 한국어 원문과 영어판(`.en.md`)을 **같은 커밋에** 넣는다. 영어판은 요약본이 아니라 전문이다.
> 5. 커밋 전에 `bash scripts/harness/check.sh` **전체**를 돌린다 — `rc validate` 만으로는 부족하다
>    (새 코스·모듈은 테스트 픽스처를 깨뜨릴 수 있다).

연구원 트랙(`curriculum/robotics-research`) 레슨 **1개를 쓰는 절차**다. 엔지니어 코스
(`curriculum/robotics-expert`)는 이 지침의 대상이 아니다 — 그쪽은
[LESSON_TEMPLATE.md](LESSON_TEMPLATE.md) 와 [CONTENT_MODEL.md](CONTENT_MODEL.md) 를 따른다.

| 문서 | 역할 |
|---|---|
| `research_notes/연구 트랙 설계/blueprint.md` | **무엇을** 쓰는가 — 레슨별 유도할 결과·필독 논문·교재 장절·재현 과제 |
| `research_notes/연구 트랙 설계/lesson-standard.md` | **어떤 기준으로** 쓰는가 — 고정 섹션, 깊이 등급, 문제 세트, 재현 티어 |
| `research_notes/연구 트랙 설계/papers.yaml` | 필독 논문 레지스트리 (id·URL·확인 여부) |
| `research_notes/연구 트랙 설계/benchmark.md` | 근거 — 대학원 과목의 실제 강의계획과 교재 |
| **이 문서** | **어떻게** 쓰는가 — 절차, 스켈레톤, 검증, 반송 사유 |
| [CONTENT_MODEL.md](CONTENT_MODEL.md) | 스키마(코드가 기준). 충돌하면 **코드가 이긴다** |

**기준 레슨(reference lesson)**: 이 지침을 그대로 적용한 실물이
`curriculum/robotics-research/c1-rigid-body-geometry-lie-groups/so3-se3-exponential.md`
(영어판 `.en.md`)다. **새 레슨은 이 파일을 복사해 시작한다.**

## 0. 시작 전 확인

```bash
git branch --show-current          # main 이면 작업 브랜치로 옮긴다
uv sync
uv run rc validate                 # 시작 시점이 깨끗한지 확인
```

- 담당 레슨 id 를 blueprint.md 에서 찾아 **그 행의 모든 열**(유도할 결과, 필독, 교재, 재현 과제)을
  먼저 읽는다. 이 지침은 그 행을 레슨으로 펼치는 방법일 뿐이다.
- 같은 모듈의 앞 레슨을 먼저 읽는다. 표기와 기호는 **모듈 안에서 일관**해야 한다.
- 모르는 주제면 쓰지 않는다. 유도를 직접 할 수 없으면 담당을 바꿔 달라고 요청한다 —
  유도를 베껴 온 레슨은 반송된다.

## 1. 한 레슨 집필 절차

1. **스켈레톤 복사** — 기준 레슨을 복사하고 front matter 와 섹션 제목만 남긴다.
2. **핵심 결과를 먼저 정한다** — 본문보다 `## 핵심 결과` 를 먼저 쓴다. R1, R2, … 로 번호를
   붙이고 각각에 깊이 등급(§3)을 단다. **D2 이상이 최소 1개** 없으면 그 레슨은 연구 수준이 아니다.
3. **유도를 종이에서 먼저 한다** — 그 다음 본문에 옮긴다. 빠진 줄이 있으면 반송된다.
4. **가정이 깨지는 지점을 찾는다** — D2/D3 결과마다 실패 모드 1개를 쓴다(§3).
5. **문제 세트** — 4–8문항, 유형 3종 이상(§5).
6. **논문** — papers.yaml 에서 id 를 가져오거나 새로 추가한다(§4). URL 확인 없이 쓰지 않는다.
7. **재현 과제** — 수용 기준을 **코드로 판정 가능한 수치 조건**으로 쓴다(§6).
8. **열린 문제** — 2–4개. "연구가 더 필요하다" 류의 문장은 금지.
9. **개념 점검 퀴즈** — 3–5문항. 문제 세트를 퀴즈로 바꾸지 않는다.
10. **공부법** — 시간 배분이 붙은 순서. 합이 `estimated_minutes` 와 어긋나지 않게.
11. **영어판 작성** — 본문 전체를 동등하게(§8). 요약본은 반송.
12. **검증과 커밋** — §9, §10.

처음 쓰는 사람의 실제 소요: 레슨 1개 8–16시간. 유도와 재현 과제 검산이 대부분을 차지한다.

## 2. 레슨 스켈레톤

front matter 는 **현재 스키마에 있는 필드만** 쓴다. 스키마 확장(papers[], problemset 블록,
`kind: paper`/`reproduction`, `level: 연구`)이 들어오기 전까지는 아래 임시 형태를 쓴다.

```yaml
---
id: c4-ilqr-ddp                      # blueprint 의 레슨 id 를 그대로. 코스 전체에서 유일
title: iLQR/DDP 와 정규화
summary: >-
  두세 문장. 이 레슨이 무엇을 유도하고 무엇을 재현하는지.
objectives:                          # 관찰 가능한 동사로. 3–5개
  - DDP 의 2차 전개를 빠진 줄 없이 유도할 수 있다.
  - 정규화 없이 iLQR 이 발산하는 조건을 설명할 수 있다.
prerequisites: [c4-dp-lqr-lqg]       # 같은 코스의 레슨 id 만. 없으면 []
                                     # 플랫폼은 이것을 잠그지 않는다 — 권장 순서 정보다
difficulty: 5                        # 연구 트랙은 트랙 내 상대값 3–5
estimated_minutes: 480               # 연구 레슨은 300–900
tags: [optimal-control, ddp, research]
activities:
  - { id: c4-ilqr-ddp-reading,      kind: reading,  title: 본문 읽기와 유도 따라가기, estimated_minutes: 90 }
  - { id: c4-ilqr-ddp-papers,       kind: reading,  title: 필독 논문 2편 + 논문별 1페이지 노트, estimated_minutes: 120 }
  - { id: c4-ilqr-ddp-problems,     kind: exercise, title: 문제 세트, estimated_minutes: 150 }
  - { id: c4-ilqr-ddp-reproduction, kind: exercise, title: 재현 과제, estimated_minutes: 90 }
  - { id: c4-ilqr-ddp-quiz,         kind: quiz,     title: 개념 점검 퀴즈, estimated_minutes: 15 }
resources:                           # 필독 논문도 당분간 여기에 (kind: article)
  - title: "Tedrake, Underactuated Robotics"
    url: https://underactuated.csail.mit.edu/
    kind: book
    note: ch.10 (Trajectory Optimization).
---
```

> **활동 kind 임시 규약**: 논문 읽기는 `reading`(제목에 "논문"을 넣는다), 문제 세트와 재현
> 과제는 `exercise`. `paper`/`reproduction`/`project` kind 가 추가되면 일괄 전환한다.

본문 섹션은 **이 순서, 이 제목**으로 고정한다(lesson-standard.md §1):

```
## 전제와 기호        ## Setup and notation
## 시작 전 자가 진단  ## Self-diagnosis before starting   (모듈의 첫 레슨만)
## 핵심 결과          ## Key results
## 유도               ## Derivation
## 증명 스케치        ## Proof sketch        (D3 결과가 있으면 필수)
## 문제 세트          ## Problem set
## 논문 읽기          ## Paper reading
## 재현 과제          ## Reproduction task
## 열린 문제          ## Open problems
## 개념 점검          ## Concept check
## 이 단계 공부법     ## How to study this stage
```

제목을 바꾸면 `extract_section` 이 절을 찾지 못해 CLI·사이트 기능이 깨진다. **영어 제목도
위 표의 문자열 그대로** 쓴다.

## 3. 유도 깊이 D0–D3

`## 핵심 결과` 의 각 결과 뒤에 `[D2]` 처럼 등급을 적는다.

| 등급 | 본문이 해야 하는 일 | 판정 질문 |
|---|---|---|
| **D0** 인용 | 결과 + 출처(교재 장·절 또는 논문 식 번호) | 선수 과정에서 이미 유도했는가? |
| **D1** 골격 | 출발 가정 → 핵심 변환 3–5단계 → 결론. 대수 중간 단계 생략 가능 | 긴 계산이 이 레슨의 본질이 아닌가? |
| **D2** 완전 유도 | 독자가 **종이 위에서 빠진 줄 없이** 따라갈 수 있다. 가정을 쓰는 지점마다 호출 | 이 레슨의 중심 결과인가? |
| **D3** 증명 | 가설(H1, H2…)과 결론(C)을 분리, 전략 한 줄, 단계 3–6개, 각 단계의 근거 | 존재·유일성·수렴·최적성·안정성 주장인가? |

규칙:
- 레슨마다 **D2 이상 1개 이상**.
- **D2/D3 결과마다 "가정이 깨지는 곳"을 1개 쓴다.** 예: "(1)은 ‖ω‖=1 에서만 성립한다 —
  단위가 아닌 φ 에 그대로 쓰면 틀린다", "θ→0 에서 이 분해 자체가 0/0 이다".
- D3 의 증명 스케치에는 **가설 하나를 지우면 어디서 무너지는지**를 쓴다. 이 한 문단이
  연구 수준과 교과서 요약을 가른다.
- 생략한 기술적 단계는 `(생략: ...)` 로 명시하고 원 논문·교재의 보조정리 번호를 건다.
- 외부 자료 본문을 통째로 옮기지 않는다(콘텐츠 규칙). 링크 + 자기 말로 쓴 유도.

## 4. 논문 인용 규칙

1. **레지스트리가 원본이다.** 필독 논문은 `research_notes/연구 트랙 설계/papers.yaml` 에 있다.
   그 id 를 쓰고, 없으면 **항목을 먼저 추가**한다.
2. **확인되지 않은 URL 은 쓰지 않는다.** 새 항목은 `verified: true` 로 올리기 전에 실제로 열어
   제목·제1저자·연도가 맞는지 확인한다. 확인 방법(권장 순서):
   - arXiv: `http://export.arxiv.org/api/query?id_list=XXXX.XXXXX`
   - DOI: `https://api.crossref.org/works/<doi>` 또는 OpenAlex
   - 그 외: 저자·연구실 페이지, 학회 프로시딩 페이지(papers.nips.cc, ijcai.org, cdn.aaai.org)
   확인 못 하면 `verified: false` + 본문에 `(미확인)` 표기. **추측한 링크를 확인된 것처럼
   쓰면 반송된다.**
3. **URL 은 영구 링크**로. arXiv abs 페이지 또는 `https://doi.org/<doi>`. PDF 직링크는 피한다
   (저자 페이지의 무료 PDF 는 예외로 허용, note 에 적는다).
4. **필독은 레슨당 2–4편.** 초과분은 `권장`으로 돌린다. 각 논문에 역할 태그를 단다:
   `원전(seminal)` / `표준(standard)` / `최신(frontier)` / `반론(critique)` / `서베이(survey)`.
5. **장식용 인용 금지.** 필독 논문은 그 레슨의 핵심 결과와 직접 연결되어야 하고, 본문에서
   "이 논문의 어느 절을 왜 읽는지"를 지정한다.
6. 논문마다 **고정 질문 10개**(lesson-standard.md §5)를 그대로 두고, 논문별 추가 질문 1–3개를 붙인다.
   산출물은 논문당 1페이지 노트.

## 5. 문제 세트 작성법

4–8문항, 아래 유형 **3종 이상**. 각 문항에 난이도(★ 15분 / ★★ 1시간 / ★★★ 하루 이상)와
대응하는 핵심 결과 번호를 붙인다.

| 유형 | 해답 공개 범위 |
|---|---|
| 유도 (P-D) | 해답 **스케치**만 (출발점 + 핵심 단계 2–3개) |
| 증명 (P-P) | 전략 + 핵심 부등식만. 전개는 숨긴다 |
| 계산 (P-N) | **정답 수치 + 허용오차**를 공개한다(자기 채점이 가능해야 하므로) |
| 구현 (P-I) | 루브릭(무엇이 맞으면 통과인가) |
| 반례 (P-C) | 성질 체크리스트 |
| 논문 (P-R) | 모범답안 대신 채점 루브릭 |

- 전체 해답을 쓰지 않는다. 목표는 "해답을 읽는 것"이 아니라 "스스로 전개하는 것"이다.
- 계산 문제는 **검산 방법**까지 쓴다(예: "(2)에 넣어 R 을 복원하고 Frobenius 오차 < 1e-12").
- 좋은 문제의 신호: 가정을 하나 바꾸면 결과가 어떻게 달라지는지 묻는 문제, 다른 차원·다른 군으로
  옮겼을 때 논증이 깨지는 지점을 찾는 문제.

## 6. 재현 과제 작성법

레슨당 1개. 티어(R1 수치 검증 / R2 알고리즘 재구현 / R3 논문 그림 재현 / R4 축소 재현)를 명시한다.
**R4 는 항상 선택 과제**로 표시한다(GPU 가 필요할 수 있으므로).

필수 기재 항목:
- **수용 기준** — 기계적으로 판정 가능한 수치 조건. 조건 2–4개로 나눠 쓴다.
  좋은 예: `max ‖log(exp(φ̂)) − φ‖∞ < 1e-12 (10^5 샘플, ‖φ‖ ∈ (1e-8, π−1e-3))`.
  **반송되는 표현**: "잘 동작하면", "비슷하면", "수렴하면"(무엇이 얼마나?).
- **입력 데이터** — 공개 데이터셋(URL)이나 레슨이 제공하는 생성 스크립트. 사용자 데이터 불필요.
- **비교 대상** — 베이스라인 1개 이상(직접 구현한 단순 방법, 표준 라이브러리, 또는 논문 보고값).
- **계산 예산** — 상한(코어·시간·메모리). numpy/scipy/jax 수준으로 끝나야 한다.
- **실패 진단표** — 흔한 실패 3개 이상과 각각의 원인·확인 방법(표로).

시뮬레이터 연동은 범위 밖이다. Drake·Pinocchio·GTSAM 등은 **라이브러리로만** 쓴다.

## 7. 수식 표기 규칙

- 인라인은 `$...$`, 디스플레이는 `$$`.
- **`$$` 는 반드시 자기 줄에 둔다.** 한 줄 수식은 `$$...$$` 를 그 줄 전체로 쓰고, 여러 줄 수식은
  여는 `$$`·내용·닫는 `$$` 를 각각 별도 줄로 둔다.

  ```markdown
  $$
  \exp(\hat{\omega}\theta) = I + \sin\theta\,\hat{\omega} + (1 - \cos\theta)\,\hat{\omega}^2. \tag{2}
  $$
  ```

- 식 번호는 `\tag{2}` 로 달고 본문에서 "(2)" 로 참조한다. 번호는 레슨 안에서만 유일하면 된다.
- `## 전제와 기호` 에 **기호 표**를 둔다(기호 / 뜻). 모듈 안에서 기호를 바꾸지 않는다.
- 차원과 좌표계를 식에 유지한다(예: $^A R_B \in SO(3)$, $\xi \in \mathbb{R}^6$).
- 코드 블록은 Python 우선. `uv run ruff format` 을 통과하는 코드만 넣는다(문서의 코드 블록도 대상).
- 퀴즈 블록(YAML) 안의 수식은 백슬래시를 **두 번** 쓴다: `"$\\hat{\\omega}^3$"`.

## 8. 번역 규칙

- 원문은 한국어(용어 영문 병기), 영어판은 `<lesson>.en.md` 에 **본문 전체**를 동등하게.
- 번역 파일 front matter 는 `id`, `lang`, `title`, `summary`, `objectives`, `tags` 만.
  구조(prerequisites·difficulty·activities·resources)는 원문에만 둔다 — 다른 키는 에러다.
- 섹션 제목은 §2 표의 영어 제목을 **그대로** 쓴다.
- 수식·기호·식 번호·정리 번호·코드·논문 제목·데이터셋 이름은 번역하지 않는다.
- 번역 파일은 **두 개**다. 둘 다 같은 커밋에 넣는다.
  - `<lesson>.en.md` — 산문(본문 전체). front matter 는 위 6개 키만.
  - `<lesson>.en.yaml` — 구조화된 텍스트: `activities`, `resources`, `quiz`. 견본은
    `curriculum/robotics-expert/m1-math-physics/vectors-matrices.en.yaml` 와
    `curriculum/robotics-research/c1-rigid-body-geometry-lie-groups/so3-se3-exponential.en.yaml`.
- 퀴즈 문항의 영어는 `<lesson>.en.yaml` 의 `quiz` 에 **문항 id 로 짝지어** 넣는다.
  `type` 과 `answer` 는 번역하지 않는다(채점 기준은 언어와 무관해야 한다). `choices` 는 개수와
  순서가 원문과 같아야 하고, `short` 문항은 그 언어의 허용 답을 `answers` 로 **추가**할 수 있다.
- 모듈을 새로 만들면 `module.en.yaml`(title, summary)도 쓴다.

## 9. 검증 체크리스트

```bash
uv run rc validate                                   # 스키마·선수지식 DAG·퀴즈 블록
uv run rc site build --out /tmp/site                 # 렌더 확인 (레슨 페이지가 생기는지)
uv run ruff format --check .                         # 문서의 Python 코드 블록 포함
bash scripts/harness/check.sh                        # 커밋 전 필수(전체). 새 코스·모듈은
                                                     # 테스트 픽스처를 깨뜨릴 수 있어 --quick 으로는 부족하다
```

섹션과 퀴즈가 실제로 추출되는지 직접 확인한다:

```bash
uv run python -c "
from pathlib import Path
from robotics_curriculum.content import load_course, parse_quiz
from robotics_curriculum.content.sections import extract_section
c = load_course(Path('curriculum/robotics-research'))
l = [x for x in c.iter_lessons() if x.id == 'c1-so3-se3-exponential'][0]
print(l.languages(), len(parse_quiz(l).questions), l.localized('en').translated)
for h in ['전제와 기호','핵심 결과','유도','증명 스케치','문제 세트','논문 읽기','재현 과제','열린 문제','개념 점검','이 단계 공부법']:
    print(('OK  ' if extract_section(l.body, h) else 'MISS'), h)
"
```

제출 전 자체 점검(lesson-standard.md §12 와 동일):

- [ ] 고정 섹션이 지정된 제목·순서로 있다(모듈 첫 레슨은 `## 시작 전 자가 진단` 포함)
- [ ] 선수를 "권장"으로 썼다 — 잠금·필수 표현이 없다
- [ ] `## 핵심 결과` 에 D2 이상이 1개 이상, 각 결과에 등급 표기
- [ ] D2/D3 결과마다 가정이 깨지는 실패 모드 1개
- [ ] 문제 세트 4–8문항, 유형 3종 이상, 난이도·해답 방침 표기
- [ ] 필독 논문 2–4편, **URL 을 실제로 열어 확인**, papers.yaml 에 등록
- [ ] 재현 과제에 기계 판정 가능한 수용 기준, 공개 데이터, 베이스라인, 계산 예산, 실패 진단표
- [ ] 열린 문제 2–4개, 각각 현재 접근 논문 포함
- [ ] `$$` 가 전부 자기 줄에, 코드 블록이 ruff format 통과
- [ ] 영어판이 본문 전체를 담고 섹션 제목이 규정 문자열과 일치
- [ ] `rc validate` 와 `rc site build` 통과
- [ ] 외부 자료 본문을 복제하지 않았다

## 9-1. 공유 파일의 경계 (저자 간 규칙)

여러 저자가 동시에 작업하므로 **공유 파일은 자기 모듈 몫만 건드린다**(오케스트레이터 승인 2026-11-12).
이 경계를 어기면 다른 저자의 작업이 조용히 사라진다 — 실제로 한 번 발생했다.

| 파일 | 내가 고쳐도 되는 것 | 건드리지 않는 것 |
|---|---|---|
| `research_notes/연구 트랙 설계/papers.yaml` | 내 모듈 레슨이 쓰는 항목(추가·수정). **추가는 파일 끝이 아니라 자기 모듈 블록(`# ── C4 …` 주석 구간) 안에** | 다른 모듈 항목 — 읽기 전용. 같은 논문을 쓰면 id 를 **재사용**하고 `lessons[]` 에 내 레슨 id 만 더한다 |
| `research_notes/연구 트랙 설계/blueprint.md` | 내 모듈 절·표의 행 | 다른 모듈 절, §1–§3(전제·구조·규약), §7–§10 |
| `research_notes/연구 트랙 설계/lesson-standard.md` | — (표준 변경은 설계 담당에게 요청) | 전체 |
| `docs/curriculum/*`, `CHANGELOG.md` | CHANGELOG 에 내 레슨 한 줄 | 나머지 |

- 같은 파일을 건드려야 하면 **먼저 담당 세션에 알리고** 수락·일정을 받는다. 커밋 후 해시를 통보한다.
- 다른 저자의 변경이 먼저 들어왔으면 **그 커밋을 머지한 뒤 그 위에** 자기 작업을 올린다.
  자기 브랜치의 오래된 상태로 덮어쓰면 안 된다.
- papers.yaml 에 항목을 추가할 때 **id 중복과 DOI 중복을 먼저 확인**한다
  (`grep -c '^  - id:' papers.yaml` 로 총수를 보고, 같은 논문이 다른 id 로 들어가지 않게 한다).

## 10. 커밋

- Conventional Commits + DCO: `git commit -s -m "content(c4): add the iLQR/DDP lesson"`
  scope 는 모듈 접두어(`c1`…`c8`, `s1`…`s5`, `r0`, `r1`, `r2`).
- 레슨 1개 = 커밋 1개(원문 + 영어판 + `module.yaml` 갱신을 함께).
- 커밋 메시지 본문에 **무엇을 어느 깊이로 유도했는지**와 검증 결과(validate/site build)를 적는다.
- `main` 에 직접 커밋하지 않는다. 푸시·머지는 사용자/오케스트레이터가 한다.
- 사용자에게 보이는 변경이므로 `CHANGELOG.md` 의 `## [Unreleased]` 에 한 줄 추가한다.

## 11. 흔한 반송 사유

1. 유도에 줄이 빠져 있다 — 독자가 종이에서 따라갈 수 없다.
2. 결과만 인용하고(D0) 끝났다 — D2 이상이 하나도 없다.
3. 실패 모드가 없다 — 가정이 언제 깨지는지 쓰지 않았다.
4. 수용 기준이 모호하다 — "잘 동작하면 통과".
5. 논문 URL 을 확인하지 않았다, 또는 추측한 arXiv 번호를 썼다.
6. 필독 논문이 레슨의 핵심 결과와 연결되지 않는다(장식용 인용).
7. 문제 세트에 전체 해답을 써 놓았다, 또는 객관식으로 바꿨다.
8. 열린 문제가 공허하다 — "더 많은 연구가 필요하다".
9. 섹션 제목을 바꿨다 — `extract_section` 이 깨진다.
10. 영어판이 요약본이다.
