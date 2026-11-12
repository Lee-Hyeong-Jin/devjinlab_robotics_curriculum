---
id: r0-convex-optimization
title: 볼록성·쌍대성·KKT
summary: >-
  볼록 집합과 함수의 정의에서 출발해 라그랑주 쌍대를 구성하고, 약·강 쌍대성과 KKT 조건을 증명
  수준에서 다룬다. 로보틱스 문제를 SOCP·SDP 로 환원하는 감각까지 기른다.
objectives:
  - 볼록 집합·함수의 정의를 쓰고 1차·2차 판정법을 적용할 수 있다.
  - 라그랑주 쌍대 함수를 구성하고 약 쌍대성을 증명할 수 있다.
  - Slater 조건 아래 강 쌍대성이 성립함을 설명하고 쌍대 간극의 의미를 말할 수 있다.
  - KKT 조건을 쓰고 볼록 문제에서 그것이 최적성의 필요충분조건임을 보일 수 있다.
  - 로보틱스 문제를 LP·QP·SOCP·SDP 중 어디로 환원할 수 있는지 판정할 수 있다.
prerequisites: [r0-linear-algebra-decompositions]
difficulty: 4
estimated_minutes: 480
tags: [optimization, convexity, duality, kkt, research]
activities:
  - id: r0-convex-optimization-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: r0-convex-optimization-textbook
    kind: reading
    title: 교재 읽기 (Boyd-Vandenberghe ch.2-5) + 1페이지 노트
    estimated_minutes: 120
  - id: r0-convex-optimization-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 2 · 계산 1 · 구현 1)
    estimated_minutes: 150
  - id: r0-convex-optimization-reproduction
    kind: reproduction
    title: 재현 과제 — QP 를 쌍대로 풀어 쌍대 간극 확인 (R1)
    estimated_minutes: 105
  - id: r0-convex-optimization-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Boyd & Vandenberghe, Convex Optimization"
    url: https://web.stanford.edu/~boyd/cvxbook/
    kind: book
    note: ch.2 (볼록 집합), 3 (볼록 함수), 4 (볼록 문제), 5 (쌍대성). 1순위, 무료 PDF.
  - title: "Boyd 의 EE364A 강의 슬라이드"
    url: https://web.stanford.edu/~boyd/cvxbook/
    kind: course
    note: 교재 페이지에 슬라이드와 연습문제가 함께 공개된다.
  - title: "CVXPY 문서"
    url: https://www.cvxpy.org/
    kind: code
    note: 재현 과제의 비교 대상. DCP 규칙을 익히면 "볼록으로 쓸 수 있는가"를 기계적으로 판정할 수 있다.
---

# 볼록성·쌍대성·KKT

## 전제와 기호

| 기호 | 뜻 |
|---|---|
| $f_0, f_i, h_j$ | 목적함수, 부등식 제약, 등식 제약 |
| $\mathcal{D}$ | 문제의 정의역, $p^\star$ 최적값 |
| $\lambda \ge 0$, $\nu$ | 부등식·등식 제약의 쌍대 변수 |
| $L(x,\lambda,\nu)$ | 라그랑지안 |
| $g(\lambda,\nu) = \inf_x L$ | 쌍대 함수, $d^\star$ 쌍대 최적값 |
| $p^\star - d^\star$ | 쌍대 간극(duality gap) |

표준형: $\min f_0(x)$ s.t. $f_i(x)\le 0$, $h_j(x)=0$. 전제는 `f0-calculus-multivariable`(기울기,
라그랑주 승수)과 `r0-linear-algebra-decompositions`.

## 핵심 결과

- **R1 (볼록성 판정) [D2]** — $f$ 가 두 번 미분가능하면 $f$ 볼록 $\iff \nabla^2 f(x) \succeq 0$
  (정의역 전체에서). 1차 판정은 $f(y) \ge f(x) + \nabla f(x)^\top(y-x)$ 이다.
- **R2 (약 쌍대성) [D3]** — 임의의 $\lambda \ge 0$, $\nu$ 에 대해

$$
g(\lambda,\nu) \le p^\star, \qquad \text{따라서}\quad d^\star \le p^\star. \tag{1}
$$

  **문제가 볼록하지 않아도 성립한다** — 쌍대가 항상 하한을 주는 이유이고, 분기한정법의 근거다.
- **R3 (강 쌍대성과 Slater 조건) [D1]** — 볼록 문제이고 **Slater 조건**(엄격 내부점이 존재:
  $\exists x$ with $f_i(x) < 0$, $h_j(x)=0$)이 성립하면 $d^\star = p^\star$ 다. 증명은 분리
  초평면 정리를 쓰며 여기서는 인용한다 **[D0]**(Boyd–Vandenberghe §5.3.2).
- **R4 (KKT 조건) [D3]** — 미분가능한 문제에서 $(x^\star,\lambda^\star,\nu^\star)$ 가 최적이고
  강 쌍대성이 성립하면

$$
\begin{aligned}
&f_i(x^\star)\le 0,\quad h_j(x^\star)=0 &&\text{(원 실현가능)}\\
&\lambda_i^\star \ge 0 &&\text{(쌍대 실현가능)}\\
&\lambda_i^\star f_i(x^\star) = 0 &&\text{(상보 여유)}\\
&\nabla f_0 + \textstyle\sum_i \lambda_i^\star\nabla f_i + \sum_j \nu_j^\star\nabla h_j = 0 &&\text{(정류)}
\end{aligned} \tag{2}
$$

  이고, **문제가 볼록하면 (2)는 최적성의 필요충분조건**이다.
- **R5 (환원 계층) [D1]** — LP ⊂ QP ⊂ SOCP ⊂ SDP. 로보틱스에서 자주 쓰이는 환원:
  최소제곱·MPC → QP, 마찰 원뿔 제약 → SOCP, 회전 완화·SOS → SDP. **어느 계층으로 쓸 수 있는지가
  해법과 규모를 정한다.**

## 유도

### R2 — 약 쌍대성

$x$ 가 원 문제의 실현가능점이고 $\lambda \ge 0$ 이면, $f_i(x) \le 0$ 과 $h_j(x) = 0$ 에서

$$
L(x,\lambda,\nu) = f_0(x) + \sum_i \lambda_i f_i(x) + \sum_j \nu_j h_j(x) \le f_0(x) .
$$

(둘째 항은 $\lambda_i \ge 0$ 과 $f_i \le 0$ 이므로 $\le 0$, 셋째 항은 0.) 따라서 **모든** 실현가능
$x$ 에 대해

$$
g(\lambda,\nu) = \inf_{x'} L(x',\lambda,\nu) \le L(x,\lambda,\nu) \le f_0(x),
$$

여기서 $\inf$ 는 실현가능점만이 아니라 **정의역 전체**에서 취하므로 첫 부등호가 성립한다.
$x$ 에 대해 최소를 취하면 $g(\lambda,\nu) \le p^\star$ 이고, $\lambda,\nu$ 에 대해 최대를 취하면 (1)이다.

**왜 볼록성이 필요 없는가**: 위 논증은 $f_0, f_i$ 의 볼록성을 **한 번도 쓰지 않았다**. 부호 조건과
$\inf$ 의 정의만 썼다. 그래서 비볼록 문제에서도 쌍대는 하한을 준다 — `c5-robust-global-estimation`
의 SE-Sync 가 쌍대 완화로 **하한을 얻고 그것이 타이트한 조건**을 따지는 구조가 이것이다.

**가정이 깨지는 곳**: $\inf_x L$ 이 $-\infty$ 면 $g$ 가 유용한 하한을 주지 못한다. 쌍대 함수의
정의역(유한한 $(\lambda,\nu)$ 의 집합)을 함께 다뤄야 한다.

### R4 — KKT 조건의 유도(필요성)

강 쌍대성이 성립하면 $f_0(x^\star) = g(\lambda^\star,\nu^\star)$ 다. $g$ 의 정의에서

$$
f_0(x^\star) = \inf_x \Big(f_0(x) + \sum_i\lambda_i^\star f_i(x) + \sum_j \nu_j^\star h_j(x)\Big)
\le f_0(x^\star) + \sum_i \lambda_i^\star f_i(x^\star) + 0 \le f_0(x^\star),
$$

마지막 부등호는 $\lambda^\star \ge 0$, $f_i(x^\star)\le0$ 에서 나온다. 양 끝이 같으므로 **두 부등호가
모두 등호**다. 이것이 두 결론을 준다:

1. $\sum_i \lambda_i^\star f_i(x^\star) = 0$ 이고 각 항이 $\le 0$ 이므로 **항별로 0** — 상보 여유.
2. $x^\star$ 가 $L(\cdot,\lambda^\star,\nu^\star)$ 의 최소점이므로 미분가능하면 그 기울기가 0 —
   정류 조건.

**충분성(볼록일 때)**: $(2)$ 를 만족하는 $(x,\lambda,\nu)$ 가 있으면, 볼록성에서 $L(\cdot,\lambda,\nu)$
도 볼록이고 정류 조건이 전역 최소를 뜻하므로 $g(\lambda,\nu) = L(x,\lambda,\nu) = f_0(x)$
(상보 여유로 제약 항이 사라진다). 약 쌍대성과 합치면 $x$ 가 최적이다.

**읽는 법**: 상보 여유는 "**활성 제약만 승수를 갖는다**"는 뜻이다. 비활성 제약($f_i<0$)의 승수는
0 이어야 한다. CBF 안전 필터(C3)나 접촉 상보성(C2)이 모두 이 구조다.

## 증명 스케치

### R1 — 2차 판정법

**가설** H1: $f$ 는 열린 볼록 집합에서 두 번 미분가능.
**결론** C: $f$ 볼록 $\iff \nabla^2 f \succeq 0$.

**전략**: 1차원으로 환원한다. 볼록성은 모든 직선 위에서의 볼록성과 동등하다.

1. $g(t) := f(x+tv)$ 로 두면 $f$ 볼록 $\iff$ 모든 $x, v$ 에 대해 $g$ 볼록(정의에서 직접).
2. 1차원에서 $g$ 볼록 $\iff g'' \ge 0$ (미적분의 표준 결과).
3. $g''(t) = v^\top\nabla^2 f(x+tv)v$ 이므로 모든 $v$ 에 대해 $\ge 0$, 즉 $\nabla^2 f \succeq 0$. C.
4. **열린 집합이 필요한 이유**: 경계에서는 $t$ 의 양방향 섭동이 정의역을 벗어날 수 있어 2단계가
   깨진다.

**가설을 지우면**: 두 번 미분가능하지 않으면(예: $\lVert x\rVert_1$) 2차 판정을 쓸 수 없고 1차
판정이나 정의를 직접 써야 한다. 로보틱스의 강건 비용(Huber)은 미분가능하지만 2차 미분이
불연속이므로 주의가 필요하다.

## 문제 세트

★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R2)** 등식 제약만 있는 최소제곱 $\min \lVert Ax-b\rVert^2$ s.t. $Cx=d$ 의
라그랑주 쌍대 함수를 명시적으로 구하고, 쌍대 문제가 또 하나의 최소제곱임을 보여라.
*해답 스케치*: $L$ 을 $x$ 에 대해 최소화하면 $x = (A^\top A)^{-1}(A^\top b - C^\top\nu/2)$ 이고,
대입하면 $\nu$ 의 이차함수가 된다.

**P2 (유도, ★★, R5)** 마찰 원뿔 제약 $\lVert f_t\rVert_2 \le \mu f_n$ 이 **2차 원뿔(SOC)** 임을
보이고, 이 제약이 있는 접촉 힘 최적화를 SOCP 표준형으로 쓰라.
*해답 스케치*: SOC 는 $\{(z,t): \lVert z\rVert_2 \le t\}$ 다. $z = f_t$, $t = \mu f_n$ 으로 두면
그대로 맞는다. C2 의 접촉 동역학이 이 환원을 쓴다.

**P3 (증명, ★★★, R4)** KKT 의 **충분성**을 볼록 문제에서 완전히 증명하라(본문의 스케치를 빈틈
없이). 비볼록 문제에서 충분성이 깨지는 예를 하나 들라.
*해답 스케치*: 충분성은 약 쌍대성 + 정류 조건 + 상보 여유로 닫힌다. 비볼록 반례는 안장점에서
KKT 를 만족하지만 최적이 아닌 경우를 만들면 된다.

**P4 (증명, ★★, R2)** 약 쌍대성의 논증에서 볼록성이 쓰이지 않는 지점을 명시하고, 그래서
비볼록 문제의 **하한**으로 쓸 수 있음을 설명하라. SE-Sync 같은 쌍대 완화가 "타이트한지"를
무엇으로 판정하는가?
*루브릭*: $p^\star - d^\star = 0$ 인지(쌍대 간극)를 수치로 확인하거나, 완화 해의 랭크 조건을
검사한다는 점을 짚으면 통과.

**P5 (계산, ★, R4)** $\min x^2 + y^2$ s.t. $x + y \ge 2$ 의 KKT 해를 구하라.
*정답*: 제약을 $2 - x - y \le 0$ 으로 쓰면 정류 조건 $2x = \lambda$, $2y = \lambda$ 에서 $x=y$,
활성 제약 $x+y=2$ 에서 $x=y=1$, $\lambda = 2$. 최적값 2. 허용오차 $10^{-9}$.
검산: $\lambda \ge 0$ 과 상보 여유를 모두 확인하라.

**P6 (구현, ★★, R2·R4)** 무작위 볼록 QP 를 만들어 ⓐ 원 문제를 직접 풀고 ⓑ 쌍대 문제를 풀어
ⓒ 쌍대 간극이 수치 영(0)임을 확인하고 ⓓ KKT 조건 네 개를 각각 수치로 검사하라.
*루브릭*: ⓐ 등식·부등식 제약을 모두 포함한다 ⓑ 쌍대 함수를 해석적으로 구한다(수치 inf 가 아니라)
ⓒ 간극이 $10^{-8}$ 이하 ⓓ 상보 여유를 항별로 검사하고 활성/비활성 제약을 분류해 출력한다.

## 논문 읽기

**교재 예외 적용**(레슨 표준 §5). Boyd & Vandenberghe 를 1차 자료로 읽고 1페이지 노트 2편을 쓴다
(고정 질문 1·3·4·8).

1. **Boyd & Vandenberghe, ch.2–3 (볼록 집합과 함수)** — 질문: ⓐ 저자들이 "볼록성을 **인식**하는"
   방법으로 제시하는 것(연산의 보존 성질)을 정리하라. ⓑ DCP(disciplined convex programming)가
   기계적 판정을 가능하게 하는 원리는?
2. **Boyd & Vandenberghe, ch.5 (쌍대성)** — 질문: ⓐ 약 쌍대성과 강 쌍대성에 각각 필요한 가정을
   구분해 쓰라. ⓑ 저자들이 쌍대 변수에 부여하는 해석(민감도, shadow price)을 로보틱스 문제에서
   예를 들어 설명하라. ⓒ 강 쌍대성이 깨지는 예가 책에 있는가?

**보조 문헌 1편**(방법론): [CVXPY 문서](https://www.cvxpy.org/) 의 DCP 규칙 — "볼록으로 쓸 수
있는가"를 기계적으로 판정하는 도구.

## 재현 과제

**티어 R1 (수치 검증).** 예산: 노트북 CPU 1분 이내, numpy/scipy(선택적으로 cvxpy). 네 조건을
모두 만족해야 한다.

1. **쌍대 간극 영**: 무작위 볼록 QP($n=20$, 등식 3개, 부등식 10개)를 만들고 원·쌍대 최적값을
   각각 계산해 $|p^\star - d^\star| < 10^{-8}$ 를 확인한다(Slater 조건이 성립하도록 생성).
2. **KKT 네 조건**: 1 의 해에 대해 원 실현가능성·쌍대 실현가능성·상보 여유·정류 조건을 각각
   수치로 검사하고, 활성 제약과 비활성 제약을 분류해 **비활성 제약의 승수가 $10^{-8}$ 이하**임을 보인다.
3. **약 쌍대성은 비볼록에서도**: 비볼록 목적함수(예: $x^\top Qx$ 에서 $Q$ 가 부정)로 같은 꼴의
   문제를 만들어, 임의의 $\lambda\ge0$ 에서 $g(\lambda) \le p^\star$ 임을 100개 무작위 $\lambda$ 에
   대해 확인한다(여기서 $p^\star$ 는 격자 탐색으로 얻은 전역 최소).
4. **Slater 조건 위반**: 엄격 내부점이 없는 문제를 일부러 만들어 **쌍대 간극이 0 이 아닌** 예를
   보인다(또는 간극이 생기는 것을 수치로 확인).

**비교 대상**: `cvxpy` 로 같은 QP 를 풀어 최적값이 $10^{-8}$ 이내로 일치(설치 가능하면).
`scipy.optimize.minimize` 의 SLSQP 와도 비교.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 쌍대 간극이 0 이 아니다 | Slater 조건 위반 또는 쌍대 함수 계산 오류 | 엄격 내부점을 하나 찾아 출력. 없으면 조건 4 의 경우다 |
| 비활성 제약의 승수가 크다 | 활성/비활성 분류 임계값이 잘못됐다 | $f_i(x^\star)$ 와 $\lambda_i$ 를 함께 출력해 짝을 본다 |
| 정류 조건 잔차가 크다 | 제약 부호 규약($f_i \le 0$)을 섞었다 | 모든 제약을 $\le 0$ 형태로 정규화했는지 확인 |
| 조건 3 이 실패한다 | $p^\star$ 를 국소 최소로 잡았다 | 격자 탐색 범위를 넓히거나 다중 시작으로 전역 최소를 확인 |

## 열린 문제

- **(열린 문제) 비볼록 로보틱스 문제의 타이트한 완화** — 쌍대는 항상 하한을 주지만(R2),
  **어떤 문제 구조에서 완화가 타이트한지**의 분류는 부분적이다. 포즈 그래프(SE-Sync)와 점군
  정합(TEASER)에서는 알려졌지만, 접촉이 있는 궤적 최적화(C4)나 IK(C1)로는 확장되지 않았다.
- **(열린 문제) 실시간 제약 아래의 볼록 해법** — MPC 가 요구하는 kHz 급 QP 해법은 성숙했지만,
  SOCP·SDP 규모에서 실시간성을 얻는 방법은 제한적이다. 마찰 원뿔(SOCP)을 실시간으로 다루려면
  근사가 필요하고, 그 근사가 보장을 얼마나 해치는지 정량화되지 않았다.
- **(열린 문제) 학습된 모델 위의 볼록 구조** — 신경망 동역학은 비볼록이므로 제어를 볼록 문제로
  쓸 수 없다. 볼록성을 보존하는 모델 구조(입력-볼록 신경망 등)가 표현력을 얼마나 희생하는지가
  정리되지 않았다.

## 개념 점검

`rc quiz r0-convex-optimization` 로 푼다. 개념 점검 전용이다.

```quiz
activity: r0-convex-optimization-quiz
questions:
  - id: q1
    type: truefalse
    prompt: "약 쌍대성 $d^\\star \\le p^\\star$ 는 문제가 볼록할 때만 성립한다."
    answer: false
    explanation: "약 쌍대성의 증명은 부호 조건($\\lambda\\ge0$, $f_i\\le0$)과 $\\inf$ 의 정의만 쓴다 — 볼록성을 한 번도 쓰지 않는다. 그래서 비볼록 문제의 하한으로 쓸 수 있고, SE-Sync 같은 쌍대 완화의 근거가 된다."
    concept: { front: "약 쌍대성의 가정", back: "볼록성 불필요. 부호 조건과 inf 의 정의만 쓴다 — 비볼록 문제의 하한으로 쓸 수 있다" }
  - id: q2
    type: single
    prompt: "상보 여유 조건 $\\lambda_i^\\star f_i(x^\\star)=0$ 이 뜻하는 것은?"
    choices:
      - "모든 제약이 활성이다"
      - "비활성 제약($f_i<0$)의 승수는 0 이다 — 활성 제약만 승수를 갖는다"
      - "모든 승수가 0 이다"
      - "제약이 등식으로 바뀐다"
    answer: 1
    explanation: "항별로 0 이어야 하므로 $f_i<0$ 이면 $\\lambda_i=0$ 이다. CBF 안전 필터(C3)가 '비활성 구간에서 명목 제어와 일치'하는 것과 접촉 상보성(C2)이 모두 이 구조다."
    concept: { front: "상보 여유", back: "활성 제약만 승수를 갖는다. 비활성 제약($f_i<0$)의 승수는 0" }
  - id: q3
    type: single
    prompt: "마찰 원뿔 제약 $\\lVert f_t\\rVert_2 \\le \\mu f_n$ 은 어느 계층의 문제로 환원되는가?"
    choices: ["LP", "QP", "SOCP", "SDP 만 가능"]
    answer: 2
    explanation: "2차 원뿔 $\\{(z,t):\\lVert z\\rVert_2\\le t\\}$ 의 형태이므로 SOCP 다. QP 로는 쓸 수 없고(제약이 이차가 아니라 원뿔), SDP 는 과하다. 환원 계층을 아는 것이 해법과 규모를 정한다."
    concept: { front: "마찰 원뿔의 환원 계층", back: "SOCP (2차 원뿔 제약). LP ⊂ QP ⊂ SOCP ⊂ SDP" }
  - id: q4
    type: single
    prompt: "볼록 문제에서 KKT 조건은 최적성의 무엇인가?"
    choices:
      - "필요조건일 뿐"
      - "충분조건일 뿐"
      - "필요충분조건 (미분가능하고 강 쌍대성이 성립할 때)"
      - "최적성과 무관하다"
    answer: 2
    explanation: "볼록·미분가능 문제에서 강 쌍대성이 성립하면 KKT 는 필요충분이다. 비볼록에서는 필요조건일 뿐이고(안장점도 만족), 그래서 KKT 를 만족해도 최적이 아닐 수 있다."
    concept: { front: "KKT 의 지위", back: "볼록·미분가능 + 강 쌍대성이면 필요충분. 비볼록에서는 필요조건일 뿐" }
```

## 이 단계 공부법

1. **약 쌍대성을 백지에서 증명한다 (40분)** — 세 줄이다. 그리고 **어디에도 볼록성이 쓰이지
   않는다**는 것을 확인한다. 이 관찰이 C5 의 인증 가능 추정으로 이어진다.
2. **KKT 를 "등호가 되는 두 부등호"로 기억한다 (60분)** — 본문의 유도를 다시 쓰면 상보 여유와
   정류 조건이 **같은 한 줄에서** 나온다. 네 조건을 따로 외우지 않는다.
3. **환원 연습을 한다 (60분)** — 로보틱스 제약 다섯 개(관절 한계, 마찰 원뿔, 토크 한계, 충돌
   회피, 회전 제약)를 각각 LP/QP/SOCP/SDP 중 어디로 쓸 수 있는지 분류한다. P2 가 그 연습이다.
4. **쌍대 간극을 수치로 본다 (90분)** — 재현 과제 조건 1·4 를 함께 한다. Slater 조건이 깨질 때
   간극이 생기는 것을 직접 보면 "강 쌍대성은 공짜가 아니다"가 각인된다.
5. **CVXPY 의 DCP 로 판정 감각을 기른다 (40분)** — 식을 조금 바꿔 가며 DCP 를 통과/실패시킨다.
   "볼록으로 쓸 수 있는가"를 기계적으로 판정하는 훈련이고, C4 의 MPC 설계에서 바로 쓰인다.
6. **교재는 쌍대 변수의 해석에 집중한다 (120분)** — ch.5 의 민감도 해석(shadow price)이 제어에서
   "어느 제약이 비용을 지배하는가"로 읽힌다. 이 관점이 C4 와 S2 에서 반복된다.

**통과 기준**: 약 쌍대성과 KKT 필요성을 백지에서 증명할 수 있고, 로보틱스 제약을 환원 계층으로
분류할 수 있고, 재현 과제 네 조건을 만족하는 코드와 교재 노트 2편이 있다.
