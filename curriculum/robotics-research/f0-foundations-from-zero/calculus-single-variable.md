---
id: f0-calculus-single-variable
title: 미적분 I — 단변수
summary: >-
  극한·도함수·적분·Taylor 급수를 계산하고 최적화 문제를 미분으로 푸는 수준까지 올린다. MIT 18.01
  (강의 영상·노트·시험+해답 전체 공개)로 안내하는 가이드형 레슨이고, 진단을 통과하면 건너뛴다.
objectives:
  - 극한과 연속성의 정의를 쓰고 기본 함수의 도함수를 계산할 수 있다.
  - 연쇄법칙·곱·몫 법칙과 음함수 미분을 적용할 수 있다.
  - 미적분의 기본정리를 쓰고 치환·부분적분으로 적분을 계산할 수 있다.
  - Taylor 급수로 함수를 근사하고 오차 항의 차수를 말할 수 있다.
  - 1변수 최적화 문제를 도함수로 풀고 임계점을 분류할 수 있다.
prerequisites: []
difficulty: 1
estimated_minutes: 4200
tags: [foundations, calculus, guide]
activities:
  - id: f0-calculus-single-variable-diagnostic
    kind: quiz
    title: 시작 전 자가 진단 (통과하면 이 레슨을 건너뛴다)
    estimated_minutes: 40
  - id: f0-calculus-single-variable-lectures
    kind: reading
    title: MIT 18.01 강의 영상·노트 수강
    estimated_minutes: 2400
  - id: f0-calculus-single-variable-problems
    kind: exercise
    title: 문제집과 기출 시험 풀이 (해답으로 자기 채점)
    estimated_minutes: 1760
resources:
  - title: "MIT 18.01 Single Variable Calculus (Fall 2006)"
    url: https://ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006/
    kind: course
    note: 1순위. 강의 영상, 강의 노트, 기출 시험과 해답까지 공개. 진행 순서를 이 과목에 맞춘다.
  - title: "Paul's Online Math Notes — Calculus I"
    url: https://tutorial.math.lamar.edu/Classes/CalcI/CalcI.aspx
    kind: notes
    note: 막힐 때 찾아보는 참고서. 예제 풀이가 단계별로 자세하다. (URL 미확인)
---

# 미적분 I — 단변수

## 도달 목표

이 레슨은 **가이드형**이다. 새 내용을 쓰지 않고, 검증된 공개 강의로 안내하고 진단으로 통과를
판정한다. 통과하면 건너뛴다.

로보틱스에서 단변수 미적분은 그 자체로 쓰이는 일이 드물다. 하지만 **뒤의 모든 것이 이것을
전제한다**: 다변수 미적분(기울기·야코비안), 미분방정식(로봇의 운동), 최적화(제어와 추정의 전부),
확률(기댓값과 적분). 여기서 막히면 이후 모든 단계가 막힌다.

통과 기준은 §시작 전 자가 진단의 6문항 중 5문항 이상이다.

## 시작 전 자가 진단

`rc quiz f0-calculus-single-variable` 로 푼다. 5/6 이상이면 이 레슨을 건너뛰고
`f0-linear-algebra` 로 간다. 4문항 이하면 §학습 경로를 따른다.

```quiz
activity: f0-calculus-single-variable-diagnostic
questions:
  - id: q1
    type: short
    prompt: "$f(x) = x^3 e^{2x}$ 의 도함수 $f'(x)$ 를 $e^{2x}$ 로 묶어 쓰면 $f'(x) = (ax^2 + bx^3)e^{2x}$ 다. $a$ 와 $b$ 는? (쉼표로 구분)"
    answer: ["3, 2", "3,2", "a=3, b=2", "3 2"]
    explanation: "곱의 법칙으로 $f' = 3x^2e^{2x} + x^3\\cdot 2e^{2x} = (3x^2 + 2x^3)e^{2x}$. 따라서 $a=3$, $b=2$."
    concept: { front: "곱의 법칙", back: "$(uv)' = u'v + uv'$ — 지수함수가 섞이면 공통 인자로 묶어 정리한다" }
  - id: q2
    type: single
    prompt: "$\\int_0^1 x\\,e^{x}\\,dx$ 의 값은?"
    choices: ["$e - 1$", "$1$", "$e$", "$e - 2$"]
    answer: 1
    explanation: "부분적분으로 $\\int xe^x dx = xe^x - e^x$. $[xe^x - e^x]_0^1 = (e - e) - (0 - 1) = 1$."
    concept: { front: "부분적분", back: "$\\int u\\,dv = uv - \\int v\\,du$ — 다항식 × 지수·삼각 꼴에서 쓴다" }
  - id: q3
    type: short
    prompt: "$\\sin x$ 의 $x=0$ 에서 Taylor 전개를 3차까지 쓰면 $x - x^3/k$ 다. $k$ 는?"
    answer: ["6", "3!", "six"]
    explanation: "$\\sin x = x - x^3/3! + x^5/5! - \\cdots$ 이므로 $k = 3! = 6$. 앞 레슨들에서 Rodrigues 공식 같은 전개가 이 급수를 쓴다."
    concept: { front: "$\\sin x$ 의 Taylor 급수", back: "$x - x^3/3! + x^5/5! - \\cdots$ (홀수 차수만, 부호 교대)" }
  - id: q4
    type: single
    prompt: "$f(x) = x^3 - 3x$ 의 국소 최솟값을 주는 $x$ 는?"
    choices: ["$x = -1$", "$x = 0$", "$x = 1$", "국소 최솟값이 없다"]
    answer: 2
    explanation: "$f' = 3x^2 - 3 = 0$ 에서 $x = \\pm1$. $f'' = 6x$ 이므로 $f''(1) = 6 > 0$ (국소 최소), $f''(-1) = -6 < 0$ (국소 최대)."
    concept: { front: "임계점 분류", back: "$f'=0$ 인 점에서 $f''>0$ 이면 국소 최소, $f''<0$ 이면 국소 최대" }
  - id: q5
    type: truefalse
    prompt: "모든 구간에서 연속인 함수는 그 구간에서 미분가능하다."
    answer: false
    explanation: "$f(x)=|x|$ 는 모든 곳에서 연속이지만 $x=0$ 에서 미분가능하지 않다. 미분가능 ⇒ 연속이지만 역은 성립하지 않는다. 이 구분이 나중에 비매끄러운 최적화(접촉 동역학)에서 중요해진다."
    concept: { front: "연속과 미분가능의 관계", back: "미분가능 ⇒ 연속. 역은 거짓($|x|$ 가 반례)" }
  - id: q6
    type: short
    prompt: "$\\lim_{x\\to 0} \\frac{\\sin x}{x}$ 의 값은?"
    answer: ["1", "one", "1.0"]
    explanation: "Taylor 전개 $\\sin x = x - x^3/6 + \\cdots$ 를 $x$ 로 나누면 $1 - x^2/6 + \\cdots \\to 1$. 이 극한이 뒤에서 $\\sin\\theta/\\theta$ 를 작은 각에서 급수로 바꿔 쓰는 근거다."
    concept: { front: "$\\sin x / x$ 의 $x\\to0$ 극한", back: "1. Taylor 급수로 보면 $1 - x^2/6 + \\cdots$" }
```

## 학습 경로

**1순위 자료**: [MIT 18.01 Single Variable Calculus (Fall 2006)](https://ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006/).
강의 영상, 강의 노트, 기출 시험과 **해답**까지 공개돼 있어 혼자 할 수 있다.

| 단계 | 18.01 범위 | 무엇을 할 수 있게 되는가 | 예상 |
|---|---|---|---|
| 1 | 미분 (Unit 1) | 극한·연속·도함수 정의, 곱·몫·연쇄법칙, 음함수 미분 | 20시간 |
| 2 | 미분의 응용 (Unit 2) | 임계점과 최적화, 선형 근사, 관련 변화율, 평균값 정리 | 15시간 |
| 3 | 적분 (Unit 3) | 기본정리, 치환·부분적분, 부분분수, 넓이·부피 | 20시간 |
| 4 | 급수와 근사 (Unit 4–5) | Taylor 급수와 오차 항, 이상적분, 극좌표 | 15시간 |

합계 약 70시간. **단계마다 기출 시험을 시간 재고 풀어 채점하라** — 강의만 보면 "안다"고
착각한다.

## 이 단계 공부법

1. **진단을 먼저 푼다 (40분)** — 5/6 이상이면 이 레슨은 끝이다. 통과하지 못한 문항이 어느
   단계인지 보고 그 단계부터 시작한다(전부 들을 필요가 없다).
2. **영상 1개 + 문제 5개를 한 묶음으로 (매일 2–3시간)** — 영상만 연달아 보면 남지 않는다.
   18.01 은 영상마다 문제집이 붙어 있으니 그 쌍을 지키면 된다.
3. **손으로 쓴다** — 미적분은 손 운동이다. 도함수 공식을 외우는 게 아니라 **적용 속도**를 올리는
   단계이므로, 계산기나 기호 연산 도구를 쓰지 않는다.
4. **막히면 Paul's Notes 로 같은 주제를 다른 설명으로 본다** — 한 설명으로 안 되는 것은 흔하다.
   다만 **주 자료를 바꾸지는 말라**. 한 과목을 끝까지 따라가는 것이 중요하다.
5. **기출 시험으로 통과를 판정한다 (단계마다 2시간)** — 18.01 의 중간·기말을 시간을 재고 풀고
   해답으로 채점한다. 80% 미만이면 그 단계를 다시 본다.
6. **다음 레슨과의 연결을 확인한다 (30분)** — 이 레슨이 끝나면 `f0-linear-algebra` 로 간다.
   로보틱스에서 가장 먼저, 가장 많이 쓰이는 것이 선형대수여서 미적분 II 보다 앞에 둔다.

**통과 기준**: 진단 6문항 중 5개 이상, 그리고 18.01 기출 기말을 80% 이상으로 자기 채점.
