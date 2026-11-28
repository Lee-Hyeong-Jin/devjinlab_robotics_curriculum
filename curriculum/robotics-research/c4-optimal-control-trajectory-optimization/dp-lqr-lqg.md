---
id: c4-dp-lqr-lqg
title: 동적 계획법·LQR·LQG
summary: >-
  최적성의 원리에서 Bellman 방정식과 HJB 를 세우고, 검증 정리(verification theorem)로 DP 가
  PMP 가 주지 못한 **충분조건**을 준다는 것을 증명한다. 수반 변수가 값 함수의 기울기
  $\lambda = \partial V/\partial x$ 임을 보여 앞 레슨과 잇고, LQR 을 DP·PMP·완전제곱 세 가지
  경로로 유도해 같은 Riccati 식에 도달함을 확인한다. Riccati 반복의 단조 수렴과 폐루프 안정성을
  증명하고, 검출 가능성이 깨질 때 "최적이지만 불안정한" LQR 이 나오는 것을 수치로 본다.
  마지막으로 LQG 분리 정리를 유도하고 Doyle 1978 로 그 보장이 **강건성이 아니라는** 것을 본다.
objectives:
  - 최적성의 원리에서 이산 Bellman 방정식과 연속 HJB 를 유도하고 검증 정리를 증명 스케치로 재구성할 수 있다.
  - HJB 를 상태로 미분해 $\lambda = \partial V/\partial x$ 와 수반 방정식을 얻고, 값 함수가 미분 불가능한 지점에서 무엇이 깨지는지 설명할 수 있다.
  - LQR 을 DP·PMP·완전제곱 세 경로로 유도하고 세 결과가 같은 Riccati 식임을 보일 수 있다.
  - Riccati 반복이 단조 수렴하는 조건과 폐루프가 안정한 조건을 분리해 말하고, 검출 가능성이 깨진 반례를 구성할 수 있다.
  - LQG 분리 정리를 추정 오차의 직교성으로 유도하고, 그것이 안정성 여유를 보장하지 않는 이유를 Doyle 의 예로 설명할 수 있다.
prerequisites: [c4-pontryagin-indirect]
difficulty: 4
estimated_minutes: 600
tags: [optimal-control, dynamic-programming, hjb, lqr, lqg, riccati, research]
activities:
  - id: c4-dp-lqr-lqg-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 110
  - id: c4-dp-lqr-lqg-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c4-dp-lqr-lqg-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 2 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 210
  - id: c4-dp-lqr-lqg-reproduction
    kind: reproduction
    title: 재현 과제 — LQR 이득의 네 가지 계산과 세 유도의 일치 (R1)
    estimated_minutes: 110
  - id: c4-dp-lqr-lqg-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 20
resources:
  - title: "Tedrake, Underactuated Robotics — Dynamic Programming"
    url: https://underactuated.csail.mit.edu/dp.html
    kind: book
    note: ch.7. 값 함수와 이산화된 DP. 전문 무료.
  - title: "Tedrake, Underactuated Robotics — Linear Quadratic Regulators"
    url: https://underactuated.csail.mit.edu/lqr.html
    kind: book
    note: ch.8. LQR 과 Riccati, 그리고 LQR 의 국소 사용법(TVLQR). 전문 무료.
  - title: "Stanford AA203 Optimal and Learning-based Control"
    url: https://stanfordasl.github.io/aa203/
    kind: course
    note: W4–W5 가 DP·LQR·LQG. 강의 노트와 과제가 공개되어 있다.
papers:
  - id: bellman1954-dp-theory
    required: true
    role: seminal
  - id: kalman1960-optimal-control
    required: true
    role: seminal
  - id: doyle1978-lqg-margins
    required: true
    role: critique
  - id: athans1971-lqg
    role: survey
  - id: kleinman1968-riccati-iteration
    role: standard
  - id: crandall1983-viscosity
    role: standard
---

# 동적 계획법·LQR·LQG

## 전제와 기호

앞 레슨 `c4-pontryagin-indirect` 는 최적 제어의 **필요조건**을 세웠다. 이 레슨은 같은 문제를
**값 함수**로 다시 보고 **충분조건**을 얻는다. 그 대가는 차원의 저주이고, 선형·2차 문제에서만
값 함수가 닫힌 형태로 남는다 — 그것이 LQR 이다. 권장 선수는 앞 레슨과 R0 모듈이다.

이 레슨이 추가로 전제하는 것:

- 선형대수: 대칭 양정부호 순서($P \succeq 0$), Schur 보완, 고윳값과 스펙트럼 반경.
- 확률: 조건부 기댓값, 직교 분해(orthogonal projection), 가우시안의 선형 변환.
  칼만 필터의 유도 자체는 `c5-manifold-estimation` 에 있고, 여기서는 **결과만** 쓴다.
- 제어: 가제어성(controllability)·안정화 가능성(stabilizability)·검출 가능성(detectability).

표기 규약(C4 모듈 공통, 앞 레슨에 이어서):

| 기호 | 뜻 |
|---|---|
| $V(x, t)$ | 값 함수(value function) — $(x,t)$ 에서 출발한 **최적** 잔여 비용 |
| $x_{k+1} = Ax_k + Bu_k$ | 이산 시간 선형계. $A \in \mathbb{R}^{n\times n}$, $B \in \mathbb{R}^{n \times m}$ |
| $Q \succeq 0$, $R \succ 0$ | 단계 비용 가중. $Q_f \succeq 0$ 는 종단 비용 가중 |
| $P_k \succeq 0$ | 값 함수의 2차 계수. $V_k(x) = \tfrac12 x^\top P_k x$ |
| $K_k$ | 피드백 이득. $u_k^* = -K_k x_k$ |
| $S_k$ | $R + B^\top P_{k+1} B \succ 0$ (제어에 대한 Hessian) |
| $\rho(M)$ | 스펙트럼 반경 $\max_i \lvert \mu_i(M)\rvert$ |
| $w_k \sim \mathcal{N}(0, W)$, $v_k \sim \mathcal{N}(0, V)$ | 과정·측정 잡음(LQG). 서로·시간에 대해 독립 |
| $\hat{x}_k$, $e_k$ | 추정값 $\mathbb{E}[x_k \mid y_{0:k}]$ 와 오차 $x_k - \hat{x}_k$ |

**비용 규약**: 이 코스는 **$\tfrac12$ 를 붙인다** — $J = \tfrac12\sum (x^\top Qx + u^\top Ru)
+ \tfrac12 x_N^\top Q_f x_N$. 많은 교재가 $\tfrac12$ 없이 쓰므로 $P$ 가 2배로 차이 난다.
논문을 읽을 때 두 번째로 확인할 것이 이것이다(첫 번째는 앞 레슨의 부호 규약).

기준 문제. **이산**:

$$
\min_{u_{0:N-1}} \; \tfrac12\sum_{k=0}^{N-1}\big(x_k^\top Q x_k + u_k^\top R u_k\big)
  + \tfrac12 x_N^\top Q_f x_N \quad \text{s.t.} \quad x_{k+1} = Ax_k + Bu_k,\; x_0 \text{ 주어짐}. \tag{1}
$$

**연속**(앞 레슨의 $(\mathrm{P})$ 와 같은 문제):
$\min \int_t^{t_f}\ell(x,u,s)\,ds + \varphi(x(t_f))$ s.t. $\dot x = f(x,u,s)$, $x(t) = x$.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`f0-how-to-read-this-track` 레슨의 "유도 깊이 등급" 절).

- **R1 (Bellman 방정식과 검증 정리) [D3]** — 최적성의 원리에서 값 함수는
  $$V_k(x) = \min_{u}\big\{\tfrac12(x^\top Qx + u^\top Ru) + V_{k+1}(Ax + Bu)\big\}, \quad V_N(x) = \tfrac12 x^\top Q_f x \tag{2}$$
  를 만족하고, 연속 시간에서는 **HJB 방정식**
  $$-\frac{\partial V}{\partial t} = \min_{u \in U}\left\{\ell(x,u,t) + \frac{\partial V}{\partial x}f(x,u,t)\right\}, \qquad V(x, t_f) = \varphi(x) \tag{3}$$
  이 성립한다. 역방향도 참이다(**검증 정리**): 어떤 $C^1$ 함수 $W$ 가 (3)과 종단 조건을 만족하면
  $W$ 는 **곧 값 함수**이고, (3)의 최솟값을 주는 $u$ 가 최적 제어다. 즉 DP 는 PMP 가 주지 못한
  **충분조건**을 준다.
- **R2 (수반 변수 = 값 함수의 기울기) [D2]** — $V$ 가 $C^2$ 이면 최적 궤적 위에서
  $$\lambda(t) := \left(\frac{\partial V}{\partial x}(x^*(t), t)\right)^\top \tag{4}$$
  이 앞 레슨의 수반 방정식 $\dot\lambda = -\ell_x^\top - f_x^\top\lambda$ 와 종단 조건
  $\lambda(t_f) = \varphi_x^\top$ 를 **정확히** 만족한다. LQR 에서는 $V = \tfrac12 x^\top Px$ 이므로
  $\lambda = Px$ — 간접법의 "sweep" 가설이 여기서 설명된다.
- **R3 (LQR 의 세 가지 유도) [D3]** — (1)의 해는 $u_k^* = -K_k x_k$ 이고
  $$
  K_k = S_k^{-1}B^\top P_{k+1}A, \quad S_k = R + B^\top P_{k+1}B, \quad
    P_k = Q + A^\top P_{k+1}A - A^\top P_{k+1}B\,S_k^{-1}B^\top P_{k+1}A, \quad P_N = Q_f, \tag{5}
  $$
  이며 같은 (5)가 **DP**(2차 가설 + 완전제곱), **PMP**(선형 2점 경계값 문제 + $\lambda_k = P_kx_k$),
  **완전제곱 항등식** 세 경로 모두에서 나온다. 세 번째 경로는 등식
  $$J(u_{0:N-1}) = \tfrac12 x_0^\top P_0 x_0 + \tfrac12\sum_{k=0}^{N-1}(u_k + K_kx_k)^\top S_k (u_k + K_kx_k) \tag{6}$$
  를 주며, 이것이 **모든** 제어열에 대해 성립하므로 최적성이 곧바로 따라온다(DP 의 충분조건을
  LQR 에서 손으로 확인하는 가장 짧은 길이다).
- **R4 (Riccati 수렴과 폐루프 안정성) [D3]** — $Q \succeq 0$, $R \succ 0$, $(A,B)$ 안정화
  가능이면 (5)를 $Q_f = 0$ 에서 역방향으로 돌린 $P^{(n)}$ 은 $n$ 에 대해 **단조 증가하고
  유계**이므로 수렴하고, 극한 $P_\infty$ 는 이산 Riccati 대수방정식(DARE)을 만족한다.
  여기에 $(A, Q^{1/2})$ **검출 가능**을 더하면 $P_\infty \succ 0$ 이고
  $$\rho\big(A - BK_\infty\big) < 1. \tag{7}$$
  검출 가능이 깨지면 DARE 에 PSD 해가 여러 개 생기고, 반복이 **안정화하지 않는 해**로
  수렴할 수 있다 — "최적이지만 불안정한" LQR.
- **R5 (LQG 분리 정리와 그 한계) [D2]** — 잡음 $w, v$ 가 가법·가우시안·독립이고 비용이 (1)의
  2차형식이면, 최적 제어는
  $$u_k^* = -K_k \hat{x}_k, \qquad \hat{x}_k = \mathbb{E}[x_k \mid y_{0:k}] \;(\text{칼만 필터}), \tag{8}$$
  즉 **결정론적 LQR 이득을 추정값에 그대로 적용**한 것이다($K_k$ 는 잡음 공분산에 의존하지
  않는다 — 확실성 등가, certainty equivalence). 그러나 이 최적성은 **모델이 정확할 때의
  기대 비용**에 대한 것뿐이다: Doyle 1978 은 LQG 폐루프의 이득 여유(gain margin)를 **임의로
  작게** 만들 수 있음을 보였다. **[D2]**

## 유도

### R1 — Bellman 방정식과 HJB

**최적성의 원리**(Bellman 1954): 최적 궤적의 어느 중간 상태에서 출발한 **잔여** 궤적은 그
중간 상태에서 출발한 문제의 최적해다. 이것은 정의에서 바로 따라온다 — 잔여 궤적이 최적이
아니라면 그 부분만 바꿔 전체 비용을 낮출 수 있고, 그러면 원래 궤적이 최적이 아니었다.
(핵심은 **비용이 단계별로 더해진다**는 것뿐이다. 이 가법성이 깨지면 DP 가 성립하지 않는다 —
아래 실패 모드.)

이산에서 $V_k(x) :=$ ($k$ 단계에서 상태 $x$ 로 시작한 최적 잔여 비용)로 두면, 한 단계만
떼어내고 나머지에 원리를 적용해 (2)를 얻는다. 연속으로 가려면 시간 간격 $\Delta$ 를 잡고

$$
V(x, t) = \min_{u}\Big\{\ell(x,u,t)\Delta + V\big(x + f(x,u,t)\Delta,\; t+\Delta\big)\Big\} + o(\Delta)
$$

에서 $V$ 를 $(x,t)$ 주변으로 1차 전개한다:

$$
V(x,t) = \min_u\Big\{\ell\Delta + V(x,t) + \frac{\partial V}{\partial x}f\Delta
  + \frac{\partial V}{\partial t}\Delta\Big\} + o(\Delta).
$$

$V(x,t)$ 와 $\partial V/\partial t\,\Delta$ 는 $u$ 에 무관하므로 최솟값 밖으로 빼내고, 양변에서
$V(x,t)$ 를 지우고 $\Delta$ 로 나눈 뒤 $\Delta \to 0$ 하면 (3)이다. **1차 전개를 쓴 것이
$V \in C^1$ 가정의 자리다.**

### R1(계속) — 검증 정리 [D3 는 증명 스케치 절에]

(3)은 "최적해가 있다면 $V$ 가 만족한다"는 필요조건으로 읽힐 수 있다. 중요한 것은 **역**이다:
(3)을 만족하는 $C^1$ 함수를 **아무 방법으로든** 하나 찾으면 그것이 값 함수이고 그 최소화자가
최적 제어다. 앞 레슨의 PMP 는 이런 역방향을 주지 못했다(극단곡선이 최적이 아닐 수 있었다).
증명은 아래 "증명 스케치"에 있고, 한 줄 요약은 "(3)을 임의의 허용 궤적 위에서 적분하면
부등식, 최소화자 궤적 위에서는 등식"이다.

### R2 — $\lambda = \partial V/\partial x$

(3)의 최솟값을 주는 제어를 $u^*(x,t)$ 라 하고 $V$ 가 $C^2$ 라고 두자. (3)을 $x$ 로 미분한다.
$u^*$ 가 최솟값을 주므로 $u$ 를 지나는 미분항은 사라진다(포락선 정리 — 앞 레슨 (14)와 같은
단계):

$$
-\frac{\partial^2 V}{\partial t \partial x} = \ell_x + \frac{\partial V}{\partial x}f_x
  + f^\top \frac{\partial^2 V}{\partial x^2}. \tag{9}
$$

이제 최적 궤적 $x^*(t)$ 위에서 $\lambda(t)^\top := \partial V/\partial x$ 의 시간 미분을 쓴다.
$\dot{x}^* = f$ 이므로 연쇄율로

$$
\dot\lambda^\top = \frac{d}{dt}\frac{\partial V}{\partial x}
  = \underbrace{f^\top\frac{\partial^2 V}{\partial x^2}}_{\text{상태 변화}}
  + \underbrace{\frac{\partial^2 V}{\partial t \partial x}}_{\text{시간 변화}}. \tag{10}
$$

(9)를 (10)에 대입하면 $f^\top V_{xx}$ 항이 **상쇄되고**

$$
\dot\lambda^\top = f^\top V_{xx} - \ell_x - \lambda^\top f_x - f^\top V_{xx}
  = -\ell_x - \lambda^\top f_x
  \;\;\Longleftrightarrow\;\; \dot\lambda = -\ell_x^\top - f_x^\top\lambda, \tag{11}
$$

정확히 앞 레슨의 수반 방정식 (2)다($\lambda_0 = 1$ 인 정상 경우). 종단 조건도
$V(x,t_f) = \varphi(x)$ 에서 $\lambda(t_f) = \varphi_x^\top$ 로 맞는다.

**읽는 법**: 수반 변수는 "값 함수의 기울기"이고, 간접법이 추측해야 했던 $\lambda(0)$ 는
$\partial V/\partial x(x_0, 0)$ 다 — 앞 레슨의 마지막 열린 문제(학습으로 $\lambda(0)$ 를
주기)가 왜 자연스러운 발상인지가 여기서 보인다. PMP 는 값 함수의 **기울기만** 들고 다니는
방법이고, DP 는 **함수 전체**를 들고 다니는 방법이다. 전자는 궤적 하나에 $O(n)$, 후자는
격자에 $O(\text{격자}^n)$ — 차원의 저주의 정확한 소재지다.

**가정이 깨지는 곳**: (4)는 $V$ 가 미분 가능해야 한다. 그런데 값 함수는 일반적으로 **미분
불가능**하다. 앞 레슨의 최소 시간 이중 적분기가 바로 그 예다 — 스위칭 곡선
$x_1 = -\tfrac12 x_2\lvert x_2\rvert$ 위에서 두 개의 최적 궤적이 만나고, 그 곡선을 가로지르며
$\partial V/\partial x$ 가 점프한다. 그 점들에서 (4)는 정의되지 않지만 PMP 는 여전히
(여러 개의) 수반 변수를 준다. 이 간극을 메우는 것이 **점성 해(viscosity solution)** 이론
([Crandall & Lions 1983](https://doi.org/10.1090/S0002-9947-1983-0690039-8))이고,
HJB 를 그 약한 의미로 풀면 검증 정리가 비매끄러운 경우로 확장된다. 두 번째 실패 모드는
**비가법 비용**이다 — 비용이 $\max_t g(x(t))$ 처럼 단계별 합이 아니면 (2)의 분해 자체가
성립하지 않아 상태를 늘려(예: 지금까지의 최대값을 상태로) 가법으로 되돌려야 한다.

### R3 — LQR 의 세 가지 유도

#### (a) DP 경로

(2)에 2차 가설 $V_{k+1}(x) = \tfrac12 x^\top P_{k+1}x$ 를 넣는다($P_N = Q_f$ 에서 시작하므로
귀납법의 기저가 맞다):

$$
V_k(x) = \min_u \tfrac12\Big[x^\top Qx + u^\top Ru + (Ax+Bu)^\top P_{k+1}(Ax+Bu)\Big].
$$

대괄호는 $u$ 에 대한 2차형식이고 $u$ 의 Hessian 은
$R + B^\top P_{k+1}B = S_k \succ 0$ ($R \succ 0$, $P_{k+1}\succeq 0$)이므로 유일한 최솟값이
있다. $u$ 로 미분해 0:

$$
Ru + B^\top P_{k+1}(Ax + Bu) = 0 \;\Longrightarrow\; S_k u = -B^\top P_{k+1}Ax
  \;\Longrightarrow\; u^* = -\underbrace{S_k^{-1}B^\top P_{k+1}A}_{K_k}x. \tag{12}
$$

$u^*$ 를 다시 넣는다. 교차항을 모으면($P_{k+1}$ 대칭을 씀)

$$
2V_k(x) = x^\top\Big[Q + A^\top P_{k+1}A - A^\top P_{k+1}BK_k - K_k^\top B^\top P_{k+1}A
  + K_k^\top S_k K_k\Big]x.
$$

여기서 $K_k^\top S_kK_k = (S_k^{-1}B^\top P_{k+1}A)^\top S_k (S_k^{-1}B^\top P_{k+1}A)
= A^\top P_{k+1}B\,S_k^{-1}B^\top P_{k+1}A = A^\top P_{k+1}BK_k$ 이고, 같은 식이
$K_k^\top B^\top P_{k+1}A$ 와도 같다. 따라서 세 교차항 중 둘이 상쇄되어 하나만 남고

$$
P_k = Q + A^\top P_{k+1}A - A^\top P_{k+1}BK_k
  = Q + A^\top P_{k+1}A - A^\top P_{k+1}B\,S_k^{-1}B^\top P_{k+1}A, \tag{13}
$$

즉 (5)다. $V_k$ 도 2차형식이므로 귀납이 닫힌다.

**같은 식의 Joseph 형태**. 위 계산을 반대로 묶으면

$$
P_k = Q + K_k^\top R K_k + (A - BK_k)^\top P_{k+1}(A - BK_k) \tag{14}
$$

가 나온다(문제 P1 에서 (13) $\Leftrightarrow$ (14)를 보인다). (14)는 **세 항이 모두
$\succeq 0$** 이라 반올림 오차가 생겨도 $P_k$ 가 대칭 PSD 를 벗어나지 않는다. (13)은 두 큰 양의
차여서 $P$ 가 거의 특이할 때 대칭성과 PSD 를 잃는다. 재현 과제에서 두 형태를 모두 구현해
같은 답을 주는 것을 확인하되, 실무 코드는 (14)를 쓴다.

#### (b) PMP 경로

앞 레슨의 PMP 를 이산으로 쓴다. $H_k = \tfrac12(x_k^\top Qx_k + u_k^\top Ru_k)
+ \lambda_{k+1}^\top(Ax_k + Bu_k)$ 에서

$$
\frac{\partial H_k}{\partial u_k} = Ru_k + B^\top\lambda_{k+1} = 0,
  \qquad \lambda_k = \frac{\partial H_k}{\partial x_k} = Qx_k + A^\top\lambda_{k+1},
  \qquad \lambda_N = Q_fx_N. \tag{15}
$$

(15)는 $u_k = -R^{-1}B^\top\lambda_{k+1}$ 를 넣으면 $(x, \lambda)$ 에 대한 **선형 2점 경계값
문제**다. 앞 레슨 R4 의 조건수 폭발이 바로 이 문제에 적용되므로 직접 풀면 안 된다. 대신
R2 가 알려준 **가설** $\lambda_k = P_kx_k$ 를 넣는다(이것이 "Riccati sweep"이다):

$$
P_kx_k = Qx_k + A^\top P_{k+1}x_{k+1} = Qx_k + A^\top P_{k+1}(Ax_k + Bu_k),
$$
$$
Ru_k + B^\top P_{k+1}(Ax_k + Bu_k) = 0 \;\Longrightarrow\; u_k = -S_k^{-1}B^\top P_{k+1}Ax_k.
$$

두 번째 식이 (12)와 **같고**, 그것을 첫 식에 넣으면 (13)이 나온다. $x_k$ 가 임의이므로 행렬
등식으로 읽을 수 있다. 종단에서 $\lambda_N = Q_fx_N$ 이 $P_N = Q_f$ 를 준다.

**얻은 것**: 2점 경계값 문제를 **역방향 Riccati 재귀 + 순방향 상태 전파**로 쪼갰다. 조건수
$e^{2\sigma T}$ 가 사라진 이유는 미지수를 $t=0$ 에 모으지 않고 **단계마다 분해**했기 때문이다 —
앞 레슨 R4 의 "다중 슈팅" 논리를 선형 문제에서 극한까지 밀어붙인 것이 Riccati 재귀다.

#### (c) 완전제곱 경로

이 경로는 가설도 귀납도 쓰지 않는다. $P_k$ 를 (5)로 **정의**하고, 임의의 제어열에 대해
각 단계에서

$$
\tfrac12 x_k^\top P_kx_k - \tfrac12x_{k+1}^\top P_{k+1}x_{k+1}
  + \tfrac12(x_k^\top Qx_k + u_k^\top Ru_k)
  = \tfrac12(u_k + K_kx_k)^\top S_k(u_k + K_kx_k) \tag{16}
$$

임을 직접 전개해 확인한다(문제 P2). (16)을 $k = 0, \dots, N-1$ 로 더하면 좌변의
$x_k^\top P_kx_k$ 가 **망원경처럼 소거**되고 $\tfrac12 x_N^\top P_Nx_N = \tfrac12x_N^\top Q_fx_N$
이 종단 비용과 만나 (6)이 된다. (6)의 우변은 $S_k \succ 0$ 이므로 각 항이 $\ge 0$ 이고,
$u_k = -K_kx_k$ 일 때 **정확히 0** 이다. 따라서

- $J \ge \tfrac12x_0^\top P_0x_0$ 이 **모든** 제어열에 대해 성립하고(하한),
- 등호는 $u_k = -K_kx_k$ 에서 달성된다(하한이 도달됨).

이것이 최적성의 증명이다. (6)은 LQR 에서 **검증 정리를 손으로 쓴 것**이고, 동시에 "최적
궤적에서 얼마나 멀어졌나"를 재는 양 $\sum \lVert u_k + K_kx_k\rVert_{S_k}^2$ 를 공짜로 준다 —
`c4-ilqr-ddp` 의 기대 비용 감소량과 선탐색이 이 양으로 쓰인다.

**가정이 깨지는 곳**: 세 경로 모두 $R \succ 0$ 을 썼다. $R$ 이 특이하면 $S_k$ 가 특이해질 수
있고 ($B$ 의 어떤 방향이 $P_{k+1}$ 의 영공간에 있을 때) (12)의 최솟값이 유일하지 않다 —
"싼 제어(cheap control)" 극한이고, 극단적으로 $R = 0$ 이면 최적 제어가 충격(impulse)으로
간다. 또 $Q \succeq 0$ 이 깨져 $Q$ 가 부정부호면 대괄호의 $u$ Hessian 은 여전히 $S_k \succ 0$
일 수 있어 각 단계의 최솟값은 존재하지만 $P_k$ 가 발산할 수 있다(유한 시간에 값 함수가
$-\infty$ 로 가는 "공액점(conjugate point)"). 유한 지평선에서 $P_k$ 가 발산하는지는
$S_k \succ 0$ 이 모든 $k$ 에서 유지되는지로 판정한다.

### R4 — Riccati 반복의 수렴과 폐루프 안정성

증명은 아래 "증명 스케치"에 있다. 여기서는 **두 가설이 서로 다른 일을 한다**는 점만
분리해 둔다.

- **안정화 가능성 $(A,B)$** → $P^{(n)}$ 이 **유계**다. 어떤 안정화 이득 $\bar{K}$ 를 쓰면
  무한 지평선 비용이 유한하고, 최적해는 그보다 나쁠 수 없으므로
  $P^{(n)} \preceq \bar{P}$ 가 모든 $n$ 에서 성립한다.
- **검출 가능성 $(A, Q^{1/2})$** → 극한이 **안정화**한다. 이것이 없으면 "비용이 보이지 않는"
  불안정 모드가 생긴다.

두 번째를 수치로 못 박는다. $n = m = 1$, $A = 2$, $B = 1$, $Q = 0$, $R = 1$ 을 보자.
$(A,B)$ 는 안정화 가능하지만 $Q = 0$ 이므로 $(A, Q^{1/2}) = (2, 0)$ 은 검출 가능하지 않다.
DARE 는

$$
P = 0 + 4P - \frac{(2P)^2}{1 + P} \;\Longrightarrow\; P(1+P) = 4P(1+P) - 4P^2
  \;\Longrightarrow\; P^2 = 3P \tag{17}
$$

이므로 PSD 해가 **두 개**다: $P = 0$ 과 $P = 3$.

- $P = 0$: $K = 0$, 폐루프 $A - BK = 2$, $\rho = 2 > 1$ — **불안정**. 그런데 $Q = 0$ 이라
  상태를 아무리 발산시켜도 비용이 0 이므로 이것은 **진짜로 최적**이다.
- $P = 3$: $K = (1+3)^{-1}\cdot 1\cdot 3\cdot 2 = 1.5$, 폐루프 $2 - 1.5 = 0.5$, $\rho = 0.5$ —
  안정화 해.

그리고 $Q_f = 0$ 에서 역방향 재귀를 돌리면 $P_k \equiv 0$ 이므로 **비안정화 해로 수렴한다**.
$Q_f = 1$ 에서 돌리면 $P \to 3$ 으로 수렴한다($1 \to 2 \to 2.6\overline{6} \to 2.9091 \to \cdots$).
재현 과제의 조건 4 가 이것이다. 교훈: **"LQR 은 항상 안정화한다"는 틀렸다.** $Q$ 가 모든
불안정 모드를 보도록(검출 가능하도록) 고르는 것은 설계자의 책임이고, 수치 해법을 고를 때도
"어느 DARE 해로 가는가"를 의식해야 한다(안정화 해를 고르는 것이 Schur 분해 기반 해법과
[Kleinman 1968](https://doi.org/10.1109/TAC.1968.1098829) 반복의 목적이다).

### R5 — LQG 분리 정리

문제: $x_{k+1} = Ax_k + Bu_k + w_k$, $y_k = Cx_k + v_k$, 비용은 (1)의 기댓값. 제어
$u_k$ 는 측정 이력 $y_{0:k}$ 의 함수여야 한다(**정보 제약**).

핵심 단계는 상태를 **추정값과 오차로 쪼개는** 것이다. $x_k = \hat{x}_k + e_k$,
$\hat{x}_k = \mathbb{E}[x_k\mid y_{0:k}]$. 조건부 기댓값의 정의에서 $\mathbb{E}[e_k \mid y_{0:k}] = 0$
이고, 따라서 $y_{0:k}$ 의 **임의의** 함수 $h$ 에 대해 $\mathbb{E}[e_k^\top h(y_{0:k})] = 0$ 이다
(직교성). $\hat{x}_k$ 와 $u_k$ 는 둘 다 그런 함수이므로

$$
\mathbb{E}[x_k^\top Qx_k]
  = \mathbb{E}[\hat{x}_k^\top Q\hat{x}_k] + 2\,\mathbb{E}[e_k^\top Q\hat{x}_k] + \mathbb{E}[e_k^\top Qe_k]
  = \mathbb{E}[\hat{x}_k^\top Q\hat{x}_k] + \mathbb{E}[e_k^\top Qe_k]. \tag{18}
$$

둘째 항은 **제어에 의존하지 않는다** — 선형 가우시안계에서 추정 오차 공분산
$\Sigma_k = \mathbb{E}[e_ke_k^\top]$ 는 칼만 필터의 리카티 재귀로 결정되고 $u$ 가 들어가지
않는다(제어는 $\hat{x}$ 를 움직일 뿐 오차를 바꾸지 않는다 — 선형성과 가법 잡음 때문이다).
그러므로 전체 비용은

$$
J = \underbrace{\tfrac12\mathbb{E}\Big[\sum(\hat{x}_k^\top Q\hat{x}_k + u_k^\top Ru_k) + \hat{x}_N^\top Q_f\hat{x}_N\Big]}_{\text{제어에 의존}}
  + \underbrace{\tfrac12\sum\operatorname{tr}(Q\Sigma_k) + \tfrac12\operatorname{tr}(Q_f\Sigma_N)}_{\text{제어와 무관한 상수}} \tag{19}
$$

로 쪼개진다. 첫 항은 $\hat{x}$ 의 동역학

$$
\hat{x}_{k+1} = A\hat{x}_k + Bu_k + L_{k+1}\underbrace{(y_{k+1} - C(A\hat{x}_k + Bu_k))}_{\text{혁신(innovation)},\ \text{백색}} \tag{20}
$$

에 대한 **가법 백색 잡음이 있는 LQR 문제**다. 여기에 (2)의 DP 를 적용하면, 2차 가설에
잡음이 더하는 항은 $\tfrac12\operatorname{tr}(P_{k+1}\Lambda_{k+1})$ 꼴의 **$u$ 에 무관한 상수**뿐이므로
최소화자는 결정론적 경우와 **똑같이** (12)가 된다. 즉 (8)이고, 이득 $K_k$ 는 $W, V$ 에
의존하지 않는다.

**가정이 깨지는 곳 — 네 가지**

1. **강건성이 아니다(Doyle 1978).** (8)은 모델이 **정확할 때의 기대 비용**에 최적이다.
   Doyle 은 $A = \begin{bmatrix}1&1\\0&1\end{bmatrix}$, $B = \begin{bmatrix}0\\1\end{bmatrix}$,
   $C = \begin{bmatrix}1&0\end{bmatrix}$, $Q = q\begin{bmatrix}1&1\\1&1\end{bmatrix}$,
   $W = \sigma\begin{bmatrix}1&1\\1&1\end{bmatrix}$, $R = V = 1$ 로 두면 입력 이득을 $m$ 배
   했을 때 폐루프가 안정한 $m$ 의 구간이 $q = \sigma \to \infty$ 에서 **한 점으로 줄어드는**
   것을 보였다. 수치로: $q = \sigma = 1$ 에서 $m \in (0.9208, 1.056)$, $q = \sigma = 10^4$ 에서
   $m \in (0.9905, 1.0000)$ (문제 P5). LQR 단독은 이득 여유가 $(\tfrac12, \infty)$ 로
   보장되지만, **관측기를 끼우면 그 보장이 사라진다.**
2. **확실성 등가가 깨지는 경우.** 잡음이 상태·제어에 **곱으로** 들어가면(승법 잡음, 모델
   파라미터 불확실성) 기대 비용에 $u$ 와 공분산의 곱이 생겨 최적 이득이 공분산에 의존한다.
   그러면 제어는 "정보를 얻기 위해 일부러 흔드는"(dual control) 성분을 갖는다.
3. **정보 제약이 선형이 아닐 때.** $U$ 에 제약이 있거나($\lvert u\rvert \le 1$) 비용이 2차가
   아니면 (19)의 분해가 성립하지 않는다. 제약 LQG 의 최적 정책은 일반적으로 $\hat{x}$ 의
   선형 함수가 아니며, 실무는 MPC 로 간다(`c4-mpc`).
4. **잡음이 가우시안이 아닐 때.** (18)의 직교성은 조건부 기댓값의 성질이라 가우시안이 아니어도
   성립하지만, $\hat{x}_k = \mathbb{E}[x\mid y]$ 를 **칼만 필터가 계산해 준다**는 것이 가우시안
   가정이다. 비가우시안에서 칼만 필터는 최적 **선형** 추정기일 뿐이고, 분리 정리는 "선형
   정책 중에서 최적"으로 약해진다.

## 증명 스케치

### R1 — 검증 정리 (verification theorem) [D3]

**가설**
H1: $W \in C^1(\mathbb{R}^n \times [0, t_f])$ 가 모든 $(x,t)$ 에서 (3)과
$W(x, t_f) = \varphi(x)$ 를 만족한다.
H2: 각 $(x,t)$ 에서 (3)의 최솟값이 어떤 $u^\sharp(x,t) \in U$ 에서 달성되고, 그
피드백으로 생성되는 궤적 $\dot{x} = f(x, u^\sharp(x,t), t)$ 가 $[t_0, t_f]$ 에서 존재한다.
H3: $\ell$, $f$ 는 적분 가능할 만큼 매끄럽다(앞 레슨 H1 과 같다).

**결론** C: $W(x_0, t_0) = V(x_0, t_0)$ 이고 $u^\sharp$ 가 최적 피드백이다.

**전략**: (3)을 "임의의 허용 제어 위에서는 부등식, $u^\sharp$ 위에서는 등식"으로 읽고,
$t_0$ 에서 $t_f$ 까지 적분해 비용을 **아래로 가두고 그 하한을 달성**한다. 완전제곱 (6)의
일반화다.

1. **아무 허용 제어 $u(\cdot)$ 를 고른다.** 그 궤적 $x(\cdot)$ 위에서
   $\frac{d}{dt}W(x(t),t) = W_t + W_x f(x,u,t)$ 다.
2. **(3)을 부등식으로 쓴다.** (3)은 최솟값이므로 임의의 $u$ 에 대해
   $-W_t \le \ell(x,u,t) + W_x f(x,u,t)$, 즉
   $$\frac{d}{dt}W(x(t),t) \ge -\ell(x(t), u(t), t).$$
3. **적분한다.** $t_0$ 에서 $t_f$ 까지 적분하면
   $W(x(t_f), t_f) - W(x_0,t_0) \ge -\int_{t_0}^{t_f}\ell\,dt$ 이고, H1 의 종단 조건으로
   $$W(x_0, t_0) \le \int_{t_0}^{t_f}\ell\,dt + \varphi(x(t_f)) = J[u].$$
   $u$ 가 임의였으므로 $W(x_0,t_0) \le \inf_u J[u] = V(x_0,t_0)$ — **하한**이다.
4. **하한을 달성한다.** $u = u^\sharp$ 를 쓰면 2단계가 **등식**이므로 3단계도 등식이고
   $W(x_0,t_0) = J[u^\sharp] \ge V(x_0,t_0)$.
5. 3·4 를 합치면 $W = V$ 이고 $J[u^\sharp] = V$ 이므로 $u^\sharp$ 가 최적이다. **C**.

**가설을 지우면 어디서 무너지는가**

- **H1 의 $C^1$ 을 지우면**: 1단계의 $\frac{d}{dt}W$ 가 존재하지 않는다. R2 의 실패 모드에서
  본 최소 시간 이중 적분기가 그 경우이고, 값 함수는 스위칭 곡선에서 미분 불가능하다.
  이때 (3)을 **점성 해**의 의미로 읽으면 검증 정리의 유사물이 복원되지만, 1단계의 고전적
  미적분은 부분미분(sub/superdifferential) 부등식으로 바뀐다
  ([Crandall & Lions 1983](https://doi.org/10.1090/S0002-9947-1983-0690039-8)).
- **H2 의 최솟값 달성을 지우면**: 3단계의 하한은 그대로 성립하지만 4단계가 불가능해
  $W \le V$ 만 남는다. $W$ 는 **하한을 주는 함수**가 되고, 이것이 바로 "값 함수의 하한을
  다항식 최적화로 만든다"는 접근(앞 레슨 열린 문제 2)의 뼈대다 — 등식을 포기하고 부등식만
  요구하면 **인증 가능한 하한**을 얻는다.
- **비용의 가법성을 지우면**: 1–3단계의 적분 논증 자체가 성립하지 않는다. $\max_t g(x(t))$ 류
  비용은 상태를 늘려 가법으로 되돌려야 한다.

(생략: $\inf$ 가 달성되는지, 궤적의 존재·유일성, $V$ 의 측정 가능성에 관한 기술적 조건.
표준 진술은 Bellman 1954 이후의 교재 — UA ch.7 과 Rawlings et al. 2017 ch.2 를 보라.)

### R4 — Riccati 반복의 수렴과 폐루프 안정성 [D3]

**가설**
H1: $Q = Q^\top \succeq 0$, $R = R^\top \succ 0$.
H2: $(A, B)$ 가 안정화 가능하다 — $\rho(A - B\bar{K}) < 1$ 인 $\bar{K}$ 가 있다.
H3: $(A, Q^{1/2})$ 가 검출 가능하다 — $Q^{1/2}z = 0$ 이고 $Az = \mu z$, $\lvert\mu\rvert \ge 1$
인 $z \ne 0$ 이 없다.

**결론** C1 ($Q_f = 0$ 에서 $n$ 단계 역방향으로 돌린 $P^{(n)}$): $P^{(n)} \preceq P^{(n+1)}$,
$P^{(n)} \preceq \bar{P}$, 따라서 $P^{(n)} \to P_\infty$ 이고 $P_\infty$ 는 DARE 를 만족한다.
C2: H3 아래 $\rho(A - BK_\infty) < 1$.

**전략**: C1 은 **단조 + 유계 수렴**(값 함수의 해석적 의미로 단조성을 얻는다). C2 는
$V(x) = \tfrac12x^\top P_\infty x$ 를 **리아푸노프 함수**로 쓰고, 안정하지 않은 모드가 있으면
비용이 0 이어야 함을 보여 H3 에 모순을 만든다.

1. **단조성.** $P^{(n)}$ 의 해석적 의미는 "종단 비용 없이 $n$ 단계 남은 최적 비용"
   $\tfrac12x^\top P^{(n)}x = \min_{u_{0:n-1}}\tfrac12\sum_{k=0}^{n-1}(x_k^\top Qx_k + u_k^\top Ru_k)$
   다. $n+1$ 단계 문제의 최적값은 $n$ 단계 문제의 최적값에 $\succeq 0$ 인 단계 비용 하나를
   더 치르는 것이므로 작아질 수 없다: 임의의 $(n+1)$-단계 제어열의 처음 $n$ 단계 비용은
   $n$-단계 최적값 이상이고, 남은 한 단계 비용은 $\ge 0$ 이다. 따라서
   $x^\top P^{(n+1)}x \ge x^\top P^{(n)}x$ 가 모든 $x$ 에서 성립한다.
2. **유계성.** H2 의 $\bar{K}$ 를 **고정 정책**으로 쓰면 그 무한 지평선 비용은
   $\tfrac12x^\top\bar{P}x$ 이고 $\bar{P}$ 는 이산 리아푸노프(Stein) 방정식
   $\bar{P} = Q + \bar{K}^\top R\bar{K} + (A - B\bar{K})^\top\bar{P}(A-B\bar{K})$ 의 해로
   **유한**하다($\rho(A - B\bar{K}) < 1$ 이므로 급수가 수렴한다). 최적값은 이 고정 정책보다
   나쁘지 않으므로 $P^{(n)} \preceq \bar{P}$.
3. **수렴.** 각 고정된 $x$ 에 대해 수열 $x^\top P^{(n)}x$ 는 단조 증가하고 위로 유계이므로
   수렴한다(스칼라 단조수렴). 모든 $x$ 에서의 극한값이 2차형식을 정의하고, 편극 항등식
   $4y^\top Pz = (y+z)^\top P(y+z) - (y-z)^\top P(y-z)$ 로 성분별 수렴을 얻는다. 극한을
   $P_\infty$ 라 하면, $S = R + B^\top PB \succ 0$ 이 극한에서도 유지되므로 (5)의 우변은
   $P$ 에 대해 연속이고 $P_\infty$ 는 DARE 를 만족한다.
4. **리아푸노프 항등식.** DARE 의 Joseph 형태 (14)를 $A_c := A - BK_\infty$ 로 쓰면
   $$P_\infty - A_c^\top P_\infty A_c = Q + K_\infty^\top RK_\infty \succeq 0,$$
   즉 폐루프 궤적 $x_{k+1} = A_cx_k$ 위에서
   $$2\big(V(x_{k+1}) - V(x_k)\big) = -x_k^\top(Q + K_\infty^\top RK_\infty)x_k \le 0. \tag{21}$$
5. **모순.** $A_c z = \mu z$, $\lvert\mu\rvert \ge 1$, $z \ne 0$ 라 하자. 궤적 $x_k = \mu^kz$ 에서
   (21)을 $k = 0$ 부터 더하면 좌변은 $2(\lvert\mu\rvert^{2N} - 1)V(z) \ge 0$ 이고 우변은
   $-\sum_{k<N}\lvert\mu\rvert^{2k}z^\top(Q + K_\infty^\top RK_\infty)z \le 0$ 이다. 두 부호가
   모두 가능하려면 $z^\top(Q + K_\infty^\top RK_\infty)z = 0$ 이어야 하고, $Q \succeq 0$,
   $R \succ 0$ 이므로 $Q^{1/2}z = 0$ **이면서** $K_\infty z = 0$ 이다. 그러면
   $Az = A_cz + BK_\infty z = \mu z$ 이므로 $z$ 는 $Q^{1/2}z = 0$ 인 $A$ 의
   $\lvert\mu\rvert \ge 1$ 고유벡터 — H3 에 모순이다. 따라서 $\rho(A_c) < 1$. **C2**.

**가설을 지우면 어디서 무너지는가**

- **H3(검출 가능)을 지우면**: 5단계의 모순이 사라진다. 실제로 $A = 2$, $B = 1$, $Q = 0$,
  $R = 1$ 에서 DARE 는 $P \in \{0, 3\}$ 두 PSD 해를 갖고, $P_\infty = 0$ 이 되어
  $\rho(A_c) = 2$ 다 — 유도 R4 의 수치 예다. "최적"과 "안정"은 **다른 것**이다.
- **H2(안정화 가능)를 지우면**: 2단계의 유계성이 깨져 $P^{(n)} \to \infty$ 다. 해석적으로는
  제어로 잡을 수 없는 불안정 모드가 $Q$ 에 보여 비용이 발산하는 것이다. 유한 지평선에서는
  여전히 잘 정의되므로, 이 경우에도 **유한 지평선 LQR 은 계산된다** — 다만 지평선을 늘리면
  이득이 수렴하지 않는다.
- **H1 의 $R \succ 0$ 을 지우면**: 3단계에서 $S$ 의 가역성을 잃는다. $R \succeq 0$ 로 약화하면
  $S_k$ 가 특이해질 수 있고, (5)를 유사역행렬로 쓰면 최소노름 해를 고르는 것이 되어 최적
  제어의 유일성이 사라진다.
- **단조성의 전제인 "$Q_f = 0$ 에서 시작"을 지우면**: $Q_f \succ 0$ 인 경우 $P^{(n)}$ 은
  단조가 아닐 수 있다(위에서 내려올 수도 있다). 그래도 수렴은 성립한다 —
  R4 의 수치 예에서 $Q_f = 1$ 로 시작하면 $1 \to 2 \to 2.667 \to 2.909 \to \cdots \to 3$ 으로
  **아래에서** 올라가 안정화 해로 간다. 단조성은 증명의 편의이고 결론보다 약한 성질이다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★, R3)** (13)과 Joseph 형태 (14)가 같은 식임을 보여라. 그 다음 두 형태를 부동소수점
연산으로 비교했을 때 (14)가 더 나은 이유를 한 문단으로 쓰라.
*해답 스케치*: $K^\top S K = A^\top PBK$ 와 $K^\top B^\top PA = A^\top PBK$ 를 각각
$K = S^{-1}B^\top PA$ 를 대입해 확인하고, (14)를 전개해 세 교차항 중 둘이 상쇄되는 것을 본다.
수치 쪽은 "세 항이 모두 $\succeq 0$ 이라 대칭성·PSD 가 반올림에 보존된다" vs "(13)은 큰 두 양의
차여서 상쇄 오차가 난다"를 짚으면 된다.

**P2 (유도, ★★, R3)** 완전제곱 항등식 (16)을 좌변에서 출발해 끝까지 전개하라. 그 다음 (16)을
$k$ 에 대해 더해 (6)을 얻고, (6)에서 "$u_k = -K_kx_k$ 가 유일한 최적해"가 어떻게 따라오는지
쓰라. $S_k \succ 0$ 이 어디서 필요한가?
*해답 스케치*: 좌변에 $x_{k+1} = Ax_k + Bu_k$ 와 (13)을 넣고 $x_k$·$u_k$ 의 2차형식으로
모은다. $u_ku_k$ 계수가 $S_k$, $x_ku_k$ 교차 계수가 $S_kK_k$, $x_kx_k$ 계수가
$K_k^\top S_kK_k$ 가 되어 완전제곱으로 묶인다. 유일성은 $S_k \succ 0$ 이라 (6)의 각 항이
0 이 되는 $u_k$ 가 하나뿐이라는 데서 온다. $S_k \succeq 0$ 만 있으면 최적해가 아핀 부분공간이 된다.

**P3 (증명, ★★★, R4)** DARE 의 **안정화 해가 PSD 해 중 유일**함을 보여라. 즉 $P_1, P_2$ 가
모두 DARE 를 만족하고 둘 다 $\rho(A - BK_i) < 1$ 이면 $P_1 = P_2$ 다.
*해답 스케치*: 전략은 "차 $\Delta := P_1 - P_2$ 가 **안정** 계수를 가진 Stein 방정식
$\Delta = A_{c,1}^\top\Delta A_{c,2}$ 를 만족함을 보이고, 그 유일해가 0 임을 쓰는 것"이다.
두 DARE 를 빼고 $K_i = S_i^{-1}B^\top P_iA$ 를 대입해 교차항을 정리하면 위 형태가 나온다.
핵심 사실: $\rho(M_1)\rho(M_2) < 1$ 이면 $\Delta = M_1^\top\Delta M_2$ 의 해는 $\Delta = 0$
뿐이다(반복 대입 $\Delta = (M_1^\top)^k\Delta M_2^k \to 0$). 이 논증이 왜 **비**안정화 해에는
적용되지 않는지도 한 줄로 쓰라.

**P4 (계산, ★, R4)** 연속 시간 스칼라 문제 $\dot x = ax + bu$,
$J = \tfrac12\int_0^\infty(qx^2 + ru^2)dt$ 의 CARE 를 쓰고 양의 해를 구하라.
$a = b = q = r = 1$ 에서 $P$, $K$, 폐루프 극점을 소수 10자리까지 구하고, 앞 레슨 (23)의
$\sigma = \sqrt{a^2+q}$ 와 어떻게 맞는지 쓰라.
*정답*: CARE 는 $2aP - b^2P^2/r + q = 0$ 이므로
$P = (r/b^2)\big(a + \sqrt{a^2 + qb^2/r}\big)$. $a=b=q=r=1$ 에서
$$P = 1 + \sqrt{2} = 2.4142135624, \quad K = bP/r = 2.4142135624, \quad a - bK = -\sqrt2 = -1.4142135624$$
(허용오차 $10^{-9}$). 폐루프 극점이 정확히 $-\sigma$ 다 — 간접법의 불안정 고윳값이 LQR 폐루프의
**안정** 극점으로 뒤집힌 것이고, 이것이 해밀토니안 스펙트럼의 $\pm$ 쌍 중 안정 쪽을 고르는
것과 같은 일이다. *검산*: $P$ 를 CARE 에 넣어 잔차 $< 10^{-12}$.

**P5 (계산, ★★, R5)** Doyle 1978 의 예를 수치로 재현하라. $A = \begin{bmatrix}1&1\\0&1\end{bmatrix}$,
$B = \begin{bmatrix}0\\1\end{bmatrix}$, $C = \begin{bmatrix}1&0\end{bmatrix}$,
$Q = qM$, $W = \sigma M$ ($M = \begin{bmatrix}1&1\\1&1\end{bmatrix}$), $R = V = 1$ 로 LQR 이득
$K$ 와 칼만 이득 $L$ 을 구하고, 입력을 $m$ 배 했을 때
($\dot x = Ax - mBK\hat{x}$, $\dot{\hat{x}} = A\hat x - BK\hat x + LC(x - \hat x)$)
폐루프가 안정한 $m$ 의 구간을 이분법으로 찾아라. $q = \sigma \in \{1, 10, 10^2, 10^3, 10^4\}$.
*정답*: $K = L = \big(2 + \sqrt{4+q}\big)\begin{bmatrix}1 & 1\end{bmatrix}$ (허용오차 $10^{-8}$;
$q = 1$ 에서 $4.2360679775$, $q = 10^4$ 에서 $102.0199980$). 안정 구간은
$q=\sigma=1$ 에서 $m \in (0.920844,\ 1.056)$, $q=\sigma=10^4$ 에서
$m \in (0.990486,\ 1.0000)$ — 위쪽 여유가 1 로 수렴한다(허용오차 $10^{-4}$).
*검산*: $m = 1$ 에서 폐루프 고윳값의 실수부가 모두 음수인지 먼저 확인하고(안 그러면 이분법의
전제가 깨진다), $K$ 를 CARE 잔차로 검산한다. LQR 단독($L$ 없이 $u = -Kx$)의 안정 구간은
$m \in (\tfrac12, \infty)$ 임을 같은 코드로 확인해 대비하라.

**P6 (구현, ★★, R1·R2)** 최소 시간 이중 적분기($\dot x_1 = x_2$, $\dot x_2 = u$,
$\lvert u\rvert\le1$)의 값 함수 $V(x)$ = 원점까지의 최소 시간을 격자에서 계산하고,
$\partial V/\partial x$ 를 중심 차분으로 그려 스위칭 곡선
$x_1 = -\tfrac12x_2\lvert x_2\rvert$ 위에서 기울기가 점프하는 것을 보여라.
*루브릭*: ⓐ 격자 밖 해석해(두 구간 bang-bang 을 해석적으로 적분)와 격자해가 격자 간격의
1차로 수렴한다 ⓑ 스위칭 곡선을 가로지르는 선을 따라 $\partial V/\partial x_1$ 을 그렸을 때
불연속이 **격자를 촘촘히 해도 사라지지 않는다**(수치 잡음이 아니다)는 것을 보인다
ⓒ 그 점들에서 (4)가 정의되지 않는다는 것과, PMP 는 여전히 두 개의 수반 변수를 준다는 것을
한 문단으로 쓴다 ⓓ 점성 해가 왜 필요한지 한 문장.

**P7 (반례, ★★, R4)** "LQR 은 폐루프를 항상 안정화한다"가 틀렸음을 **두 가지 서로 다른
방식**으로 보여라: (i) 검출 가능성이 깨져 비안정화 DARE 해로 수렴하는 예, (ii) $Q \succ 0$
이지만 **유한** 지평선에서 폐루프가 불안정한 예(지평선이 짧아 "지금 안정화할 이유가 없는"
경우).
*성질 체크리스트*: (i) 은 유도 R4 의 $A=2,B=1,Q=0,R=1$ 을 쓰되 $Q_f$ 를 0 과 양수로 바꿔
수렴 지점이 달라지는 것까지 보인다. (ii) 는 $N = 1$ 과 $Q_f = 0$ 을 쓰면 즉시 나온다 —
$K_0 = 0$ 이므로 한 단계 동안 상태가 발산한다. 확인할 성질: 유한 지평선 LQR 은
**시변 이득**이고 "폐루프 안정성"이라는 말이 정의되는 대상이 아니라는 점,
$\rho(A - BK_k)$ 를 각 $k$ 에서 보면 1 을 넘는 $k$ 가 있을 수 있다는 점.

**P8 (논문, ★★, R5)** Doyle 1978 두 쪽을 읽고 ⓐ 저자가 반증하는 **정확한 명제**를 한 문장으로
쓰고 ⓑ 그 반례에서 $q, \sigma \to \infty$ 가 왜 필요한지 ⓒ 이 논문 이후 로보틱스가 실제로
택한 대응이 무엇인지(LQG 대신 무엇을 쓰는가) 각각 3문장 이내로 쓰라.
*루브릭*: ⓐ 는 "LQG 설계에 보장된 이득·위상 여유가 있다"는 명제를 짚어야 통과. "LQG 가
나쁘다"로 쓰면 미달. ⓑ 는 가중을 키우면 이득이 커지고 관측기 극점이 플랜트의 불안정 모드와
상쇄되는 구조가 생겨 여유가 사라진다는 점. ⓒ 는 $\mathcal{H}_\infty$·LQG/LTR, 혹은 명시적
제약과 재계획으로 가는 MPC 중 하나를 들고 그것이 보장하는 바를 적으면 통과.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`f0-how-to-read-this-track` 레슨의 "논문 읽기" 절). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Bellman, "The theory of dynamic programming" (1954, Bull. Amer. Math. Soc.)** —
   역할: `원전(seminal)`. <https://doi.org/10.1090/S0002-9904-1954-09848-8>
   읽을 곳: 전체(14쪽). 최적성의 원리와 함수 방정식이 **어떤 문제 종류**를 위해 제안되었는지에
   주목한다(순차적 결정, 재고, 탐색).
   추가 질문: ⓐ Bellman 이 "차원의 저주"를 말할 때 정확히 무엇을 세고 있는가 —
   상태 격자인가, 정책 공간인가? ⓑ 이 글에 **수렴 증명**이 있는가, 아니면 함수 방정식의
   제안인가? 없다면 그 간극은 누가 메웠는가? ⓒ 이 글의 틀에서 (3)의 $C^1$ 가정은 어디에
   숨어 있는가?
2. **Kalman, "Contributions to the theory of optimal control" (1960, Bol. Soc. Mat. Mexicana;
   위 URL 은 2009 IEEE Press 재수록판)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1109/9780470544334.ch8>
   읽을 곳: LQR 과 Riccati 방정식을 세우는 절, 그리고 안정성·가제어성 논의.
   추가 질문: ⓐ Kalman 의 유도는 이 레슨의 세 경로 중 어느 것에 가장 가까운가?
   ⓑ 그가 "최적성이 안정성을 준다"고 말할 때 암묵적으로 쓰는 가정은 무엇이고, 유도 R4 의
   반례는 그 가정의 어느 쪽을 깨는가? ⓒ 이산이 아니라 연속으로 쓰인 이 결과를
   $\Delta \to 0$ 으로 이산에서 복원할 수 있는가?
3. **Doyle, "Guaranteed margins for LQG regulators" (1978, IEEE T-AC)** —
   역할: `반론(critique)`. <https://doi.org/10.1109/TAC.1978.1101812>
   읽을 곳: 전체(2쪽). 이 레슨에서 가장 짧고 가장 중요한 읽기다.
   추가 질문: ⓐ 반례가 **한 개**로 충분한 이유는 무엇인가(명제의 형태를 보라)?
   ⓑ 저자가 $q, \sigma$ 를 동시에 키우는 이유는? 하나만 키우면 어떻게 되는가(P5 로 확인하라)?
   ⓒ 이 논문은 무엇을 **보장하지 않는가** — "LQG 는 항상 취약하다"로 읽으면 어디가 틀렸는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히
무엇인가 (3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지
않는가** (5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과
맞는가, 분산·시드를 보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저
의심할 가정 (9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R1 (수치 검증).** 계산 예산: 노트북 CPU 1코어, 전체 1분 이내, 메모리 200 MB 이하.
numpy + scipy 만(`scipy.linalg.solve_discrete_are`, `eig`). 시뮬레이터는 쓰지 않는다.

**입력 데이터**: 없다. 전부 상수로 지정한다. 기준계는 이산화된 이중 적분기
($\Delta t = 0.1$):

$$
A = \begin{bmatrix} 1 & 0.1 \\ 0 & 1\end{bmatrix}, \quad
B = \begin{bmatrix} 0.005 \\ 0.1 \end{bmatrix}, \quad
Q = I_2, \quad R = [1], \quad Q_f = I_2, \quad x_0 = (1, 0).
$$

**과제**: ① $K_\infty$ 를 **네 가지 독립적인 방법**으로 계산한다 — (13) 재귀, Joseph 형태
(14) 재귀, `solve_discrete_are`, 그리고 심플렉틱 행렬
$Z = \begin{bmatrix} A + GA^{-\top}Q & -GA^{-\top} \\ -A^{-\top}Q & A^{-\top}\end{bmatrix}$
($G = BR^{-1}B^\top$)의 **단위원 내부 불변 부분공간**에서 $P$ 를 읽는 고윳값 해법.
② 폐루프 극점을 확인한다. ③ R3 의 세 유도가 일치함을 수치로 확인한다. ④ R4 의 검출 가능성
반례를 재현한다.

**수용 기준** — 네 조건을 **모두** 만족해야 통과다.

1. **네 방법이 일치한다.** 20000 단계 재귀 기준으로
   $$
   K_\infty = \begin{bmatrix} 0.917074563114 & 1.635596185047 \end{bmatrix}, \qquad
     P_\infty = \begin{bmatrix} 17.834931322189 & 10.012492197250 \\
       10.012492197250 & 17.856586460329 \end{bmatrix}
   $$
   이고, 네 방법의 쌍별 차가 $\max\lVert \Delta K\rVert_\infty < 10^{-10}$,
   $\max\lVert\Delta P\rVert_\infty < 10^{-10}$ 다(참고: 저자 구현에서 각각
   $3.8\times10^{-14}$, $4.9\times10^{-13}$ 이었다). 고윳값 해법은 $Z$ 의 안정 고윳값이
   **복소 공액쌍**이므로 실수 불변 부분공간을 $[\operatorname{Re}v, \operatorname{Im}v]$ 로
   잡아야 한다 — 두 열의 실수부만 쓰면 특이행렬이 된다(실패 진단표).
2. **폐루프가 안정하다.** $A - BK_\infty$ 의 고윳값이
   $0.915927504340 \pm 0.045853692377\,i$ 이고 $\rho = 0.917074563114$ 로
   $10^{-9}$ 이내로 일치하며 $\rho < 1$ 이다. $Z$ 의 고윳값 4개의 절댓값이
   $\{0.917074563114,\ 0.917074563114,\ 1.090423876336,\ 1.090423876336\}$ 로
   단위원 기준 2:2 로 갈라지는 것도 확인한다(안쪽 둘의 역수가 바깥쪽 둘이다 — 앞 레슨 R4 의
   $\pm$ 쌍의 이산 버전).
3. **세 유도가 일치한다.** $N = 60$, $Q_f = I$ 에서
   ⓐ (15)의 선형 2점 경계값 문제를 하나의 밀집 선형계로 직접 풀고
   $\max_k\lVert\lambda_k - P_kx_k\rVert_\infty < 10^{-10}$ (R2 의 (4)),
   ⓑ 그렇게 얻은 $u_k$ 가 $-K_kx_k$ 와 $\max_k\lVert\cdot\rVert_\infty < 10^{-10}$ 이내로 일치,
   ⓒ 완전제곱 (6)이 **무작위** 제어열 200개에 대해
   $\lvert J(u) - \tfrac12x_0^\top P_0x_0 - \tfrac12\sum(u_k+K_kx_k)^\top S_k(u_k+K_kx_k)\rvert
   < 10^{-9}$,
   ⓓ 최적 비용이 $\tfrac12x_0^\top P_0x_0 = 8.91648483301953$ 과 실제 롤아웃 비용이
   $10^{-12}$ 이내로 일치.
4. **검출 가능성 반례.** $A = [2]$, $B = [1]$, $Q = [0]$, $R = [1]$ 에서
   ⓐ $Q_f = 0$ 으로 500단계 역방향 재귀 → $P = 0$, $K = 0$, $\rho(A-BK) = 2$ (정확히),
   ⓑ $Q_f = 1$ 로 500단계 → $P = 3$, $K = 1.5$, $\rho = 0.5$ 가 $10^{-10}$ 이내,
   ⓒ `solve_discrete_are` 는 $P = 3$ (안정화 해)을 돌려준다,
   ⓓ 따라서 DARE 의 PSD 해가 $\{0, 3\}$ 두 개임을 (17)로 손으로 확인하고 ⓐ 와 ⓒ 가
   **서로 다른 해**를 고른다는 것을 보고서에 적는다.

**비교 대상**: ① `scipy.linalg.solve_discrete_are` 가 1차 베이스라인이다(독립 구현).
② 조건 3 의 2점 경계값 문제가 DP 와 독립적인 두 번째 베이스라인이다. ③ 조건 4 의
$P \in \{0,3\}$ 은 손으로 푼 2차방정식 (17)이 베이스라인이다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 고윳값 해법이 `Singular matrix` 로 죽는다 | 안정 고윳값이 복소 공액쌍인데 두 고유벡터의 실수부만 썼다 | 고윳값의 허수부를 출력하고, 쌍이면 $[\operatorname{Re}v, \operatorname{Im}v]$ 로 부분공간을 만든다 |
| $P$ 가 비대칭으로 자란다 | (13) 형태를 썼고 반올림이 누적됐다 | Joseph 형태 (14)로 바꾸거나 매 단계 $(P+P^\top)/2$ 로 대칭화한다. 두 결과의 차가 조건 1 의 허용오차 안인지 본다 |
| 재귀가 $K$ 로 수렴하지 않고 진동한다 | 2차형식의 $\tfrac12$ 규약을 $Q$ 나 $R$ 한쪽에만 적용했다 | $P_\infty$ 가 `solve_discrete_are` 와 정확히 2배 차이 나는지 본다 — 그렇다면 규약 불일치다 |
| 2점 경계값 문제의 해가 $P_kx_k$ 와 어긋난다 | 이산 PMP 의 첨자 규약 — $H_k$ 에 $\lambda_{k+1}$ 이 들어가고 $\lambda_k$ 가 나온다 | $N=1$ 로 줄여 손으로 푼 답과 맞춰 본다 |
| 완전제곱 항등식이 무작위 제어에서 깨진다 | $S_k$ 를 $R + B^\top P_k B$ (첨자 $k$)로 썼다 | $S_k$ 가 $P_{k+1}$ 을 쓰는지 확인한다. $N=1$ 에서 두 선택의 차가 바로 보인다 |
| 반례에서 $Q_f = 0$ 재귀가 3 으로 간다 | $Q$ 를 0 이 아니라 작은 양수로 넣었다(예: `1e-12`) | $Q$ 를 정확히 0 으로 두고, $P_1 = Q + \cdots$ 가 **정확히** 0 인지 첫 단계에서 확인한다 |

## 열린 문제

- **(열린 문제) 값 함수를 쓸 수 있는 차원의 한계** — DP 는 충분조건을 주지만 격자 기반
  계산은 $O(\text{격자}^n)$ 이다. 신경망으로 값 함수를 근사하면 차원은 올라가지만, 그렇게 얻은
  $\hat{V}$ 가 검증 정리의 **부등식**(증명 스케치 3단계)을 만족한다는 보장이 없어 "최적에
  얼마나 가까운가"를 말할 수 없다. 현재 접근: 다항식 값 함수에 대한 SOS 하한
  ([Henrion & Korda 2014](https://doi.org/10.1109/TAC.2013.2283095)), HJ 도달가능성의
  레벨셋 계산([Bansal et al. 2017](https://doi.org/10.1109/CDC.2017.8263977)).
  비어 있는 자리: 학습된 $\hat V$ 에 대해 **계산 가능한 사후 간극 한계**(a posteriori bound).
  이 질문은 `c4-robust-stochastic-oc` 와 `c8-rl-theory` 에서 다시 나온다.
- **(열린 문제) 비매끄러운 값 함수에서 기울기 기반 방법의 타당성** — 접촉이 있는 로봇의 값
  함수는 거의 확실히 미분 불가능한데, iLQR·DDP·정책 경사 모두 $\partial V/\partial x$ 류의
  양을 쓴다. 점성 해 이론은 **존재와 유일성**을 주지만, 수치 알고리즘이 쓰는 기울기가 어떤
  의미에서 올바른지에 대한 일반 이론이 없다. 현재 접근: 부분미분·clarke 미분을 쓰는
  비매끄러운 최적화, 그리고 접촉을 매끄럽게 완화하는 방법(`c4-contact-implicit-hybrid`).
  비어 있는 자리: 완화 파라미터 $\to 0$ 에서 해가 원 문제의 해로 간다는 **정량적** 보장.
- **(열린 문제) 분리 정리의 강건 버전** — Doyle 1978 이후 $\mathcal{H}_\infty$ 와 LQG/LTR 이
  여유를 되찾는 설계를 주었지만, **학습된 모델** 아래에서 추정과 제어를 분리해도 되는지는
  열려 있다. 모델 오차가 상태 추정 오차와 상관될 때 (18)의 직교성이 깨진다.
  현재 접근: 튜브 MPC 와 집합 멤버십 추정의 결합(`c4-mpc`, `c4-robust-stochastic-oc` 의
  [Mayne et al. 2005](https://doi.org/10.1016/j.automatica.2004.08.019)).
  비어 있는 자리: 학습 오차 한계가 주어졌을 때 폐루프 성능 저하의 **타이트한** 한계.
- **(열린 문제) Riccati 재귀를 대체할 구조적 해법** — $n$ 이 커지면 DARE 를 푸는 비용이
  $O(n^3)$ 이고 MPC 처럼 매 주기 다시 풀어야 하면 이것이 병목이다. 희소·저계수 구조를 쓰는
  해법은 문제별로 있지만 일반론이 없다. 현재 접근:
  [Kleinman 1968](https://doi.org/10.1109/TAC.1968.1098829) 류의 Newton 반복과 그 저계수 변형,
  그리고 DARE 를 명시적으로 풀지 않는 1차 방법. 비어 있는 자리: 상태 차원에 **준선형**인
  해법과 그 수렴 보장.

## 개념 점검

`rc quiz c4-dp-lqr-lqg` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`f0-how-to-read-this-track` 레슨의 "문제 세트" 절).

```quiz
activity: c4-dp-lqr-lqg-quiz
questions:
  - id: q1
    type: single
    prompt: "검증 정리(verification theorem)가 PMP 에 비해 더 주는 것은?"
    choices:
      - "수반 변수의 종단 조건"
      - "최적성의 **충분**조건 — HJB 를 만족하는 $C^1$ 함수를 찾으면 그것이 값 함수다"
      - "제어 제약 $U$ 를 다루는 방법"
      - "계산 복잡도의 개선"
    answer: 1
    explanation: "PMP 는 필요조건이라 극단곡선이 최적이 아닐 수 있었다. 검증 정리는 역방향이다 — HJB 와 종단 조건을 만족하는 $C^1$ 함수를 아무 방법으로든 하나 찾으면 그것이 값 함수이고 그 최소화자가 최적 제어다. 증명은 HJB 를 임의 궤적 위에서 적분해 하한을 얻고(부등식), 최소화자 궤적에서 그 하한을 달성하는(등식) 두 단계다."
    concept: { front: "DP 가 PMP 에 더하는 것", back: "충분조건. HJB 의 $C^1$ 해를 하나 찾으면 최적성이 증명된다 — 대가는 차원의 저주" }
  - id: q2
    type: short
    prompt: "최적 궤적 위에서 수반 변수 $\\lambda(t)$ 는 값 함수의 무엇과 같은가? (한 단어 또는 기호로)"
    answer: ["기울기", "gradient", "V_x", "dV/dx", "∂V/∂x", "편미분", "구배"]
    explanation: "$\\lambda = (\\partial V/\\partial x)^\\top$ 다. HJB 를 $x$ 로 미분하고 최적 궤적 위에서 $d/dt$ 를 취하면 $V_{xx}f$ 항이 상쇄되어 수반 방정식이 정확히 복원된다. LQR 에서는 $V = \\frac12 x^\\top Px$ 이므로 $\\lambda = Px$ — 간접법의 sweep 가설이 이것이다."
    concept: { front: "수반 변수의 정체", back: "값 함수의 기울기 $\\lambda = (\\partial V/\\partial x)^\\top$. PMP 는 기울기만, DP 는 함수 전체를 들고 다닌다" }
  - id: q3
    type: single
    prompt: "Riccati 재귀의 Joseph 형태 $P_k = Q + K^\\top RK + (A-BK)^\\top P_{k+1}(A-BK)$ 를 쓰는 이유는?"
    choices:
      - "연산량이 더 적기 때문"
      - "세 항이 모두 $\\succeq 0$ 이라 반올림 오차에도 대칭 PSD 가 보존되기 때문"
      - "$K$ 를 따로 계산할 필요가 없기 때문"
      - "안정화 DARE 해로 수렴하는 것이 보장되기 때문"
    answer: 1
    explanation: "두 형태는 대수적으로 동일하다. 표준형 $Q + A^\\top PA - A^\\top PBS^{-1}B^\\top PA$ 는 큰 두 양의 **차**여서 $P$ 가 거의 특이할 때 상쇄 오차로 대칭성과 양정부호성을 잃는다. Joseph 형태는 PSD 항의 합이라 그런 일이 없다. 연산량은 오히려 조금 더 많다."
    concept: { front: "Joseph(제곱근) 형태의 이점", back: "PSD 항의 합이라 반올림에도 $P \\succeq 0$ 과 대칭이 유지된다 — 연산량이 아니라 수치 안정성 때문에 쓴다" }
  - id: q4
    type: truefalse
    prompt: "$Q \\succeq 0$, $R \\succ 0$ 이고 $(A,B)$ 가 안정화 가능하면 무한 지평선 LQR 의 폐루프는 반드시 안정하다."
    answer: false
    explanation: "검출 가능성 $(A, Q^{1/2})$ 이 더 필요하다. $A=2$, $B=1$, $Q=0$, $R=1$ 에서 DARE 는 PSD 해 $P \\in \\{0,3\\}$ 를 갖고, $Q_f=0$ 에서 돌린 재귀는 $P=0$ 으로 가서 $K=0$, 폐루프 $\\rho=2$ 로 불안정하다. 비용이 0 이므로 그것은 **진짜로 최적**이다 — '최적'과 '안정'은 다른 것이다."
    concept: { front: "LQR 폐루프 안정성에 필요한 두 가설", back: "안정화 가능성 $(A,B)$ 는 $P$ 의 **유계성**을, 검출 가능성 $(A,Q^{1/2})$ 는 극한의 **안정화**를 준다" }
  - id: q5
    type: single
    prompt: "LQG 분리 정리에서 LQR 이득 $K_k$ 가 잡음 공분산 $W, V$ 에 의존하지 않는 근거는?"
    choices:
      - "잡음이 평균 0 이기 때문"
      - "추정 오차가 측정 이력의 모든 함수와 직교해 비용이 제어 의존 항과 제어 무관 항으로 쪼개지고, 가법 잡음은 $u$ 에 무관한 trace 항만 더하기 때문"
      - "칼만 필터가 최적 추정기이기 때문"
      - "$Q$ 와 $R$ 이 잡음과 무관하게 선택되기 때문"
    answer: 1
    explanation: "핵심은 두 단계다. ① $x = \\hat x + e$ 로 쪼개면 $\\mathbb{E}[e^\\top Q\\hat x] = 0$ 이라 비용이 $\\hat x$ 항과 $\\mathrm{tr}(Q\\Sigma_k)$ 항으로 분리되고, 후자는 $u$ 에 무관하다. ② $\\hat x$ 동역학은 가법 백색 잡음이 있는 선형계이고, 2차 비용에 가법 잡음이 더하는 것은 $\\frac12\\mathrm{tr}(P\\Lambda)$ 꼴의 상수뿐이므로 최소화자가 결정론적 경우와 같다. 이것이 확실성 등가이고, 승법 잡음에서는 깨진다."
    concept: { front: "확실성 등가가 성립하는 조건", back: "선형 동역학 + 2차 비용 + 가법·독립 잡음. 잡음이 곱으로 들어오거나 비용이 2차가 아니면 최적 이득이 공분산에 의존한다" }
  - id: q6
    type: truefalse
    prompt: "Doyle 1978 은 LQG 설계가 실무에서 쓸 수 없을 만큼 취약하다는 것을 보였다."
    answer: false
    explanation: "Doyle 이 반증한 명제는 '**보장된** 이득·위상 여유가 있다'는 것이고, 반례 하나로 충분하다. 그 반례는 가중 $q,\\sigma$ 를 함께 크게 키운 극단이며, 모든 LQG 설계가 취약하다는 뜻이 아니다. 교훈은 '최적성은 강건성이 아니므로 여유를 따로 설계·검증해야 한다'이고, 그 결과가 $\\mathcal{H}_\\infty$·LQG/LTR 와 명시적 제약을 다루는 MPC 다."
    concept: { front: "Doyle 1978 이 반증한 것", back: "'LQG 에는 보장된 안정성 여유가 있다'는 명제. 반례 1개로 충분하며, LQG 가 늘 취약하다는 주장은 아니다" }
```

## 이 단계 공부법

1. **규약을 먼저 고정한다 (20분)** — "전제와 기호"의 $\tfrac12$ 규약을 종이에 적어 둔다.
   교재마다 $P$ 가 2배씩 다르고, 그 때문에 틀린 이득을 쓰고 몇 시간을 잃는 일이 흔하다.
   앞 레슨의 부호 규약과 이 레슨의 $\tfrac12$ 규약, 두 줄이면 된다.
2. **(2)와 (3)을 직접 만든다 (60분)** — 최적성의 원리를 한 문장으로 쓰고, $\Delta$ 전개로
   HJB 를 유도한다. "어디서 $C^1$ 을 썼는가"를 그 자리에 표시해 둔다. 이 표시가 나중에
   점성 해가 왜 필요한지로 이어진다. UA ch.7 을 **같은 결과의 다른 설명**으로 대조해 읽는다.
3. **검증 정리를 외우지 말고 네 줄로 복원한다 (50분)** — "① 아무 제어 ② HJB 는 부등식
   ③ 적분하면 하한 ④ 최소화자에서 등식". 이 네 줄이 (6)의 완전제곱과 **같은 구조**라는 것을
   확인하면 LQR 의 최적성 증명과 일반 검증 정리가 한 덩어리로 기억된다.
4. **LQR 을 세 번 유도한다 (120분)** — 하루에 하나씩 해도 좋다. DP(2차 가설), PMP(sweep),
   완전제곱. 세 번째가 가장 짧고 가장 강하다(가설도 귀납도 없이 모든 제어열에 대한 등식).
   P1·P2 를 풀면 세 경로가 실제로 같은 대수 조작이라는 것이 보인다.
5. **"최적이지만 불안정"을 손으로 만든다 (40분)** — 유도 R4 의 $A=2,B=1,Q=0,R=1$ 을
   종이에서 끝까지 풀어 $P \in \{0,3\}$ 를 확인하고, $Q_f$ 를 0 과 1 로 바꿔 재귀가
   **다른 해로** 가는 것을 직접 본다. 이 20줄이 "LQR 은 안정화한다"는 잘못된 기억을
   영구히 지운다.
6. **재현 과제는 조건 4 를 먼저 한다 (110분)** — 스칼라라서 5분이면 끝나고, 조건 1–3 의
   행렬 코드를 쓰기 전에 규약이 맞는지 검증해 준다. 그 다음 조건 1(네 방법)을 하고,
   고윳값 해법에서 복소 공액쌍에 걸려 보는 것이 Riccati 와 심플렉틱 구조의 연결을
   기억에 남긴다.
7. **Doyle 을 마지막에 읽는다 (90분)** — Bellman → Kalman → Doyle 순서가 이 레슨의 서사다.
   Doyle 은 두 쪽이지만 P5 로 **직접 재현**해야 의미가 남는다. 안정 구간이 $q$ 를 키울 때마다
   좁아지는 표를 자기 손으로 만들어라.
8. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제" 넷 중 하나를 골라 왜 아직 안 풀렸는지
   한 문단으로 쓴다. 첫 번째(차원의 한계)가 `c4-ilqr-ddp` 전체의 동기다.

**통과 기준**: 백지에서 (12)–(13)(DP 경로)과 (6)(완전제곱)을 쓸 수 있고, 검증 정리를 네 줄로
복원할 수 있고, 검출 가능성 반례의 두 DARE 해를 손으로 구할 수 있고, 재현 과제의 네 조건을
모두 만족하는 코드를 갖고 있고, 논문 3편의 노트가 있다.
