---
id: f0-calculus-multivariable
title: 미적분 II — 다변수
summary: >-
  편미분·기울기·연쇄법칙·다중적분과 발산·회전을 계산하고 기울기의 기하적 의미를 설명하는 수준까지
  올린다. MIT 18.02 로 안내하는 가이드형 레슨이고, 진단을 통과하면 건너뛴다.
objectives:
  - 편미분과 기울기를 계산하고 기울기가 최대 증가 방향임을 설명할 수 있다.
  - 다변수 연쇄법칙과 야코비안 행렬을 쓸 수 있다.
  - 1·2차 Taylor 전개로 다변수 함수를 근사하고 Hessian 으로 임계점을 분류할 수 있다.
  - 라그랑주 승수로 제약 최적화 문제를 풀 수 있다.
  - 다중적분과 변수변환(야코비안 행렬식)을 계산할 수 있다.
prerequisites: [f0-linear-algebra]
difficulty: 1
estimated_minutes: 4200
tags: [foundations, calculus, guide]
activities:
  - id: f0-calculus-multivariable-diagnostic
    kind: quiz
    title: 시작 전 자가 진단 (통과하면 이 레슨을 건너뛴다)
    estimated_minutes: 40
  - id: f0-calculus-multivariable-lectures
    kind: reading
    title: MIT 18.02 강의 영상·노트 수강
    estimated_minutes: 2400
  - id: f0-calculus-multivariable-problems
    kind: exercise
    title: 문제집과 기출 시험 풀이 (해답으로 자기 채점)
    estimated_minutes: 1760
resources:
  - title: "MIT 18.02 Multivariable Calculus (Fall 2007)"
    url: https://ocw.mit.edu/courses/18-02-multivariable-calculus-fall-2007/
    kind: course
    note: 1순위. 강의 영상, 강의 노트, 기출 시험과 해답 공개.
  - title: "NumPy 수치 미분 연습"
    url: https://numpy.org/doc/stable/user/
    kind: notes
    note: 기울기·야코비안을 유한차분으로 검산하는 연습에 쓴다. 연구 트랙 전체가 이 검산을 요구한다.
---

# 미적분 II — 다변수

## 도달 목표

이 레슨은 **가이드형**이다. 통과하면 건너뛴다.

연구 트랙에서 쓰는 형태로 말하면: **기울기와 야코비안이 없으면 최적화도 추정도 없다.** C4(최적
제어)의 모든 유도, C5(상태 추정)의 모든 야코비안, R0 의 수치 미분 검증이 이 레슨을 전제한다.
특히 **야코비안을 "편미분을 모은 행렬"로 자유롭게 다루는 것**과 **Hessian 으로 임계점을
분류하는 것**이 핵심이다.

통과 기준은 §시작 전 자가 진단의 6문항 중 5문항 이상이다.

## 시작 전 자가 진단

`rc quiz f0-calculus-multivariable` 로 푼다. 5/6 이상이면 건너뛰고 `f0-differential-equations` 로 간다.

```quiz
activity: f0-calculus-multivariable-diagnostic
questions:
  - id: q1
    type: short
    prompt: "$M$ 이 대칭일 때 $f(x) = x^\\top M x$ 의 기울기 $\\nabla f$ 를 $M$ 과 $x$ 로 쓰면?"
    answer: ["2Mx", "2 M x", "2*M*x", "2Mx^T", "2 Mx"]
    explanation: "성분으로 전개해 미분하면 $\\nabla f = (M + M^\\top)x$ 이고 $M$ 이 대칭이므로 $2Mx$. 이 한 줄이 최소제곱·LQR·정보행렬 유도에서 계속 나온다."
    concept: { front: "이차형식의 기울기", back: "$\\nabla(x^\\top Mx) = (M+M^\\top)x$, 대칭이면 $2Mx$" }
  - id: q2
    type: single
    prompt: "기울기 $\\nabla f(x_0)$ 의 기하적 의미는?"
    choices:
      - "등위면(level set)의 접선 방향"
      - "함수가 가장 빠르게 증가하는 방향이고 등위면에 수직이다"
      - "함수의 최솟값 위치"
      - "Hessian 의 최대 고유벡터"
    answer: 1
    explanation: "방향 미분 $D_u f = \\nabla f^\\top u$ 가 $u = \\nabla f/\\lVert\\nabla f\\rVert$ 에서 최대이고, 등위면 위의 방향에서는 0 이므로 기울기는 등위면에 수직이다."
    concept: { front: "기울기의 기하적 의미", back: "최대 증가 방향이며 등위면에 수직. 크기는 그 방향의 증가율" }
  - id: q3
    type: short
    prompt: "$g: \\mathbb{R}^3 \\to \\mathbb{R}^2$ 의 야코비안 행렬의 크기는 몇 행 몇 열인가? (예: 2x3)"
    answer: ["2x3", "2×3", "2 x 3", "2-by-3", "2 by 3"]
    explanation: "출력 차원 × 입력 차원 = $2\\times3$. 행이 출력, 열이 입력이다. 이 규약을 틀리면 전치를 잘못 써서 추정이 조용히 틀린다."
    concept: { front: "야코비안의 크기 규약", back: "출력 차원 × 입력 차원 (행 = 출력, 열 = 입력)" }
  - id: q4
    type: single
    prompt: "$f(x,y) = x^2 - y^2$ 의 원점 $(0,0)$ 은 어떤 점인가?"
    choices: ["국소 최소", "국소 최대", "안장점(saddle)", "판정할 수 없다"]
    answer: 2
    explanation: "Hessian 이 $\\mathrm{diag}(2, -2)$ 로 고윳값의 부호가 섞여 있으므로 안장점이다. 비볼록 최적화에서 안장점을 다루는 것이 연구 트랙의 반복 주제다."
    concept: { front: "Hessian 으로 임계점 분류", back: "고윳값 전부 양수 = 국소 최소, 전부 음수 = 국소 최대, 부호 혼재 = 안장점" }
  - id: q5
    type: short
    prompt: "제약 $g(x)=0$ 아래에서 $f(x)$ 를 최적화할 때, 라그랑주 조건은 $\\nabla f = \\lambda \\cdot ?$"
    answer: ["grad g", "∇g", "nabla g", "gradient of g", "\\nabla g"]
    explanation: "$\\nabla f = \\lambda\\nabla g$ — 최적점에서 두 기울기가 평행하다. C4 의 PMP 와 C2 의 제약 동역학이 이 조건의 확장이다."
    concept: { front: "라그랑주 승수 조건", back: "$\\nabla f = \\lambda\\nabla g$ (제약 하 최적점에서 기울기가 평행)" }
  - id: q6
    type: truefalse
    prompt: "변수변환으로 다중적분을 계산할 때 야코비안 행렬식의 절댓값을 곱해야 한다."
    answer: true
    explanation: "$\\int f(x)dx = \\int f(\\phi(u))\\lvert\\det D\\phi(u)\\rvert du$. 행렬식이 부피 변화율이기 때문이다. 확률에서 변수변환할 때도 같은 인자가 나온다."
    concept: { front: "다중적분의 변수변환", back: "야코비안 행렬식의 절댓값을 곱한다 — 행렬식이 부피 변화율" }
```

## 학습 경로

**1순위 자료**: [MIT 18.02 Multivariable Calculus (Fall 2007)](https://ocw.mit.edu/courses/18-02-multivariable-calculus-fall-2007/).

| 단계 | 18.02 범위 | 무엇을 할 수 있게 되는가 | 예상 |
|---|---|---|---|
| 1 | 벡터와 행렬, 매개곡선 (L1–L6) | 내적·외적, 평면·직선, 속도·가속도 | 12시간 |
| 2 | 편미분과 기울기 (L8–L13) | 기울기, 방향 미분, 연쇄법칙, 야코비안, 라그랑주 승수 | 22시간 |
| 3 | 다중적분 (L16–L21) | 이중·삼중적분, 극·구면좌표, 변수변환 | 18시간 |
| 4 | 벡터장 (L22–L31) | 선적분, 발산·회전, 그린·스토크스 정리 | 18시간 |

합계 약 70시간. **2단계가 이 레슨의 핵심**이고 연구 트랙에서 가장 많이 쓰인다. 4단계는 로보틱스에서
덜 쓰이지만 유체·전자기 문헌을 읽을 때 필요하다 — 시간이 부족하면 4단계를 나중으로 미뤄도 된다.

## 이 단계 공부법

1. **진단을 먼저 (40분)** — 5/6 이상이면 끝이다.
2. **2단계에 시간을 몰아넣는다** — 기울기·야코비안·연쇄법칙은 뒤에서 매일 쓴다. 나머지보다
   두 배 더 연습한다.
3. **모든 기울기를 유한차분으로 검산한다 (매 단계)** — 손으로 구한 $\nabla f$ 와 numpy 중심
   차분이 일치하는지 본다. **이 습관이 연구 트랙 재현 과제의 기본 동작**이고, R0 에서 스텝 크기
   선택까지 다룬다.
4. **야코비안의 모양을 먼저 쓴다** — 계산 전에 "출력 × 입력" 크기를 적는다. 전치 실수를 막는
   가장 싼 방법이다.
5. **라그랑주 승수를 기하로 이해한다 (2시간)** — "등위면이 접한다"는 그림을 그린다. C4 의
   Pontryagin 최대 원리와 C2 의 제약 동역학이 같은 그림의 확장이다.
6. **기출로 판정한다** — 18.02 기출 2회를 시간 재고 80% 이상.

**통과 기준**: 진단 5/6 이상, 18.02 기출 80% 이상, 그리고 임의의 $g:\mathbb{R}^n\to\mathbb{R}^m$
에 대해 야코비안을 손으로 구하고 유한차분으로 검산하는 코드를 쓸 수 있다.
