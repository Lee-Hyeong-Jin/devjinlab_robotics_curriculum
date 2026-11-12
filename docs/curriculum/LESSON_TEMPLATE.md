# 레슨 템플릿

아래 블록을 `curriculum/<course>/<module>/<lesson>.md`로 복사한 뒤 채운다.
파일 이름(확장자 제외)을 `module.yaml`의 `lessons`에 추가하고 `uv run rc validate`로 확인한다.
필드 설명은 `CONTENT_MODEL.md` 참조.

````markdown
---
id: m1-example-topic            # 코스 내 유일. 관례: <모듈 접두어>-<주제>
title: 레슨 제목
summary: 한두 문장으로 이 레슨이 다루는 내용.
objectives:
  - 학습 목표 1 (…할 수 있다)
  - 학습 목표 2
prerequisites: []               # 선수 레슨 ID 목록, 예: [m1-vectors-matrices]
difficulty: 2                   # 1(입문) ~ 5(심화)
estimated_minutes: 60
tags: [topic, keyword]
activities:
  - id: m1-example-topic-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 30
  - id: m1-example-topic-quiz
    kind: quiz
    title: 확인 퀴즈
    estimated_minutes: 10
  - id: m1-example-topic-exercise
    kind: exercise
    title: 손으로 / 코드로 풀어 보기
    estimated_minutes: 20
  # kind: reading | paper | quiz | exercise | reproduction | project
resources:                      # 선택. 단계별 학습 자료 (title만 필수)
  - title: Modern Robotics
    url: https://example.org/modern-robotics
    kind: book                  # book | course | video | article | paper | dataset | code | notes | other
    note: Ch. 3
papers: []                      # 선택. 코스 papers.yaml 의 논문 id 참조 (ADR 0014)
  #  - id: mayne-1966
  #    required: true           # 논문을 지정하면 최소 1개는 required: true
  #    role: seminal            # seminal | standard | frontier | critique | survey
  #    note: "§3 의 2차 전개"
---

# 레슨 제목

## 왜 필요한가

이 레슨이 로드맵에서 어떤 위치인지, 다음 레슨에서 어떻게 쓰이는지 한 문단.

## 핵심 개념

- 개념 1 — 정의와 직관. 수식은 `$...$` / `$$...$$` (KaTeX).
- 개념 2

## 예제

짧은 코드 블록(```python) 또는 계산 예시.

## 연습

`activities`의 exercise에 대응하는 과제 설명.

## 확인 퀴즈

`activities`의 quiz 활동에 대응하는 문항. 형식은 CONTENT_MODEL.md "본문 안의 퀴즈 블록" 참조.
`rc quiz m1-example-topic` 으로 풀고, 오답은 복습 카드가 된다.

```quiz
activity: m1-example-topic-quiz
questions:
  - id: q1
    type: single                 # single | multiple | truefalse | short
    prompt: "두 벡터의 내적이 0이면 두 벡터는?"
    choices: ["평행하다", "직교한다", "같은 벡터다", "영벡터다"]
    answer: 1                    # 0-based 인덱스
    explanation: "내적이 0이면 사잇각이 90°이므로 직교한다."
    concept: { front: "내적이 0인 두 벡터의 관계", back: "직교(사잇각 90°)" }   # 선택: 개념 카드
  - id: q2
    type: short
    prompt: "3×3 회전행렬의 행렬식 값은?"
    answer: ["1", "+1"]          # 허용 답 목록 (공백·대소문자 무시)
    explanation: "회전행렬은 직교행렬이고 반사를 포함하지 않으므로 det = +1."
```

## 더 읽을거리

- 교재/논문/강의 링크
````
