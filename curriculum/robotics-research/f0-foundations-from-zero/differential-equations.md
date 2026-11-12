---
id: f0-differential-equations
title: 미분방정식
summary: >-
  1·2계 ODE 를 풀고, 선형 계의 해를 고윳값으로 해석하고, 수치 적분기가 왜 필요한지 설명하는
  수준까지 올린다. MIT 18.03 으로 안내하는 가이드형 레슨이고, 진단을 통과하면 건너뛴다.
objectives:
  - 1계 선형·분리형 ODE 를 풀고 적분인자를 쓸 수 있다.
  - 2계 상수계수 ODE 의 일반해를 특성방정식으로 구하고 감쇠 거동을 분류할 수 있다.
  - 선형 연립 ODE 의 해를 행렬 지수와 고윳값으로 쓸 수 있다.
  - 상평면에서 평형점을 분류하고 안정성을 판정할 수 있다.
  - 해석적 해가 없을 때 수치 적분기가 필요한 이유와 강성(stiffness)의 뜻을 말할 수 있다.
prerequisites: [f0-calculus-multivariable]
difficulty: 1
estimated_minutes: 3600
tags: [foundations, differential-equations, guide]
activities:
  - id: f0-differential-equations-diagnostic
    kind: quiz
    title: 시작 전 자가 진단 (통과하면 이 레슨을 건너뛴다)
    estimated_minutes: 40
  - id: f0-differential-equations-lectures
    kind: reading
    title: MIT 18.03 강의 영상·노트 수강
    estimated_minutes: 2000
  - id: f0-differential-equations-problems
    kind: exercise
    title: 문제집 풀이 (해답으로 자기 채점) + scipy 로 수치해 비교
    estimated_minutes: 1560
resources:
  - title: "MIT 18.03 Differential Equations (Spring 2010)"
    url: https://ocw.mit.edu/courses/18-03-differential-equations-spring-2010/
    kind: course
    note: 1순위. 강의 영상, 강의 노트, 문제집과 해답 공개.
  - title: "SciPy integrate 문서 (solve_ivp)"
    url: https://docs.scipy.org/doc/scipy/reference/integrate.html
    kind: notes
    note: 해석적 해와 수치해를 비교하는 실습에 쓴다. 적분기 선택(RK45 vs Radau)과 강성 문제를 본다.
---

# 미분방정식

## 도달 목표

이 레슨은 **가이드형**이다. 통과하면 건너뛴다.

**로봇의 운동은 미분방정식이다.** $\dot{x} = f(x,u)$ 가 연구 트랙 전체의 출발점이고, C2(동역학)는
그 $f$ 를 세우는 법, C3·C4(제어)는 $u$ 를 고르는 법, C5(추정)는 노이즈가 있는 관측에서 $x$ 를
알아내는 법이다. 특히 **선형 계의 해를 고윳값으로 읽는 것**(안정성)과 **행렬 지수**는 C1 의
지수 사상, C3 의 Lyapunov 안정성, C4 의 LQR 로 곧바로 이어진다.

통과 기준은 §시작 전 자가 진단의 6문항 중 5문항 이상이다.

## 시작 전 자가 진단

`rc quiz f0-differential-equations` 로 푼다. 5/6 이상이면 건너뛰고 `f0-probability-statistics` 로 간다.

```quiz
activity: f0-differential-equations-diagnostic
questions:
  - id: q1
    type: short
    prompt: "$\\dot{x} = ax$, $x(0)=x_0$ 의 해는 $x(t) = x_0 e^{kt}$ 다. $k$ 는?"
    answer: ["a", "a t", "at"]
    explanation: "$k=a$. 이 가장 단순한 ODE 의 해가 행렬로 확장되면 $\\dot{x}=Ax \\Rightarrow x(t)=e^{At}x_0$ 이고, 그것이 C1 의 지수 사상과 C4 의 LQR 의 출발점이다."
    concept: { front: "$\\dot{x}=ax$ 의 해", back: "$x(t) = x_0e^{at}$. 행렬판은 $x(t)=e^{At}x_0$" }
  - id: q2
    type: single
    prompt: "$\\ddot{y} + 2\\dot{y} + 5y = 0$ 의 거동은?"
    choices: ["과감쇠(진동 없음)", "임계감쇠", "감쇠 진동(underdamped)", "발산"]
    answer: 2
    explanation: "특성방정식 $s^2+2s+5=0$ 의 근은 $s = -1 \\pm 2i$ 로 복소이고 실수부가 음수다 — 진동하며 감쇠한다. PID 이득을 고르는 감각이 여기서 나온다."
    concept: { front: "2계 상수계수 ODE 의 거동 분류", back: "특성근이 복소면 진동, 실수부 부호가 안정성. 중근이면 임계감쇠" }
  - id: q3
    type: single
    prompt: "$\\dot{x} = Ax$ 가 (점근적으로) 안정할 조건은?"
    choices:
      - "$A$ 의 모든 고윳값의 실수부가 음수"
      - "$A$ 의 모든 고윳값이 실수"
      - "$\\det A > 0$"
      - "$A$ 가 대칭"
    answer: 0
    explanation: "$x(t)=e^{At}x_0$ 이고 $e^{\\lambda t}$ 가 $\\lambda$ 의 실수부로 증감을 결정하므로, 모든 고윳값의 실수부가 음수여야 한다. C3 의 Lyapunov 안정성이 이것을 비선형으로 확장한다."
    concept: { front: "선형 계의 안정성 조건", back: "모든 고윳값의 실수부 < 0 (이산 시간은 모든 고윳값의 크기 < 1)" }
  - id: q4
    type: short
    prompt: "1계 선형 ODE $\\dot{x} + p(t)x = q(t)$ 를 풀 때 곱하는 적분인자는 $\\mu(t) = e^{?}$ (지수 안의 식)"
    answer: ["int p dt", "∫p dt", "integral of p", "\\int p(t)dt", "int p(t) dt"]
    explanation: "$\\mu = e^{\\int p\\,dt}$ 를 곱하면 좌변이 $(\\mu x)'$ 가 되어 적분으로 풀린다. C1 의 Duhamel 공식도 같은 적분인자 기법이다."
    concept: { front: "1계 선형 ODE 의 적분인자", back: "$\\mu = e^{\\int p\\,dt}$ — 곱하면 좌변이 완전미분 $(\\mu x)'$ 가 된다" }
  - id: q5
    type: truefalse
    prompt: "스텝 크기를 충분히 작게 하면 전진 Euler 법은 어떤 문제에서도 안정적으로 적분할 수 있다."
    answer: true
    explanation: "이론적으로는 참이다 — 전진 Euler 의 안정 영역이 유한하므로 강성(stiff) 문제에서는 스텝을 **극단적으로** 작게 해야 하고, 그러면 반올림 오차와 계산 비용이 폭발한다. 즉 실무에서는 거짓처럼 작동한다. 그래서 암시적 적분기를 쓴다 — R0 의 적분기 레슨이 이것을 다룬다."
    concept: { front: "전진 Euler 와 강성 문제", back: "안정 영역이 유한해 강성 문제에서 스텝이 극단적으로 작아진다 — 실무에서는 암시적 적분기를 쓴다" }
  - id: q6
    type: single
    prompt: "상평면에서 평형점의 야코비안 고윳값이 $+1$ 과 $-2$ 일 때 그 평형점은?"
    choices: ["안정 노드", "불안정 노드", "안장점", "중심(center)"]
    answer: 2
    explanation: "고윳값의 부호가 섞여 있으면 안장점이다 — 한 방향으로 끌리고 다른 방향으로 밀린다. 보행 로봇의 리미트 사이클 분석(S3)에서 이 분류를 쓴다."
    concept: { front: "평형점 분류", back: "고윳값 부호로: 전부 음수 = 안정 노드, 전부 양수 = 불안정, 혼재 = 안장점, 순허수 = 중심" }
```

## 학습 경로

**1순위 자료**: [MIT 18.03 Differential Equations (Spring 2010)](https://ocw.mit.edu/courses/18-03-differential-equations-spring-2010/).
강의 영상·노트와 문제집·해답이 공개된다.

| 단계 | 18.03 범위 | 무엇을 할 수 있게 되는가 | 예상 |
|---|---|---|---|
| 1 | 1계 ODE | 분리형, 적분인자, 방향장, 존재·유일성 | 12시간 |
| 2 | 2계 상수계수 | 특성방정식, 감쇠 분류, 공명과 주파수 응답 | 15시간 |
| 3 | 연립 ODE 와 행렬 | 행렬 지수, 고윳값·고유벡터로 해 쓰기, 상평면 | 20시간 |
| 4 | 비선형과 수치해 | 평형점 분류, 선형화, 수치 적분기와 강성 | 13시간 |

합계 약 60시간. **3단계가 연구 트랙과 가장 직접 연결된다**(행렬 지수 → C1, 안정성 → C3).

## 이 단계 공부법

1. **진단을 먼저 (40분)** — 5/6 이상이면 끝이다.
2. **해석적 해와 수치해를 항상 같이 본다 (매 단계)** — 손으로 푼 해를 `scipy.integrate.solve_ivp`
   결과와 겹쳐 그린다. 둘이 어긋나는 지점(스텝 크기, 강성)이 R0 의 적분기 레슨으로 이어진다.
3. **3단계는 선형대수와 함께 본다 (20시간)** — $e^{At}$ 를 고윳값 분해로 계산해 본다.
   `f0-linear-algebra` 를 먼저 둔 이유가 여기서 드러난다.
4. **상평면을 그린다 (3시간)** — 2차원 비선형 계의 벡터장을 matplotlib 로 그리고 평형점 주변을
   확대한다. S3(보행)의 리미트 사이클이 이 그림의 확장이다.
5. **강성을 직접 만든다 (2시간)** — 고윳값이 $-1$ 과 $-1000$ 인 선형 계를 전진 Euler 로 적분해
   스텝을 줄여 가며 언제 안정해지는지 본다. "왜 암시적 적분기가 있는가"의 답이 숫자로 나온다.
6. **문제집으로 판정한다** — 18.03 문제집 전체를 해답으로 채점해 80% 이상.

**통과 기준**: 진단 5/6 이상, 18.03 문제집 80% 이상, 그리고 $\dot{x}=Ax$ 의 해를 고윳값으로 쓰고
수치 적분과 비교하는 코드를 스스로 쓸 수 있다.
