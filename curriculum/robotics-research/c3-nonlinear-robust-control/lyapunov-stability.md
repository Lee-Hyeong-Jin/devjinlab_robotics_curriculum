---
id: c3-lyapunov-stability
title: Lyapunov 안정성과 ISS
summary: >-
  비선형 계의 안정성을 Lyapunov 함수로 판정하는 정리와 그 역정리, LaSalle 불변 집합 정리,
  그리고 입력이 있는 계의 ISS(input-to-state stability)를 비교 함수(comparison function)로
  정식화해 유도한다. 마지막에는 Lyapunov 함수 자체를 SOS(sum-of-squares) 프로그래밍으로
  탐색해 흡인 영역(region of attraction)을 인증하고, 그 인증이 왜 항상 보수적인지까지 간다.
objectives:
  - Lyapunov 정리와 LaSalle 불변 집합 정리의 가설을 분리해 증명 전략을 재구성할 수 있다.
  - 지수 안정성의 역정리를 궤적 적분으로 직접 구성하고 각 경계가 어디서 오는지 설명할 수 있다.
  - ISS-Lyapunov 함수에서 ISS 추정식의 $\beta$ 와 $\gamma$ 를 빠진 줄 없이 유도할 수 있다.
  - 0-GAS 이지만 ISS 가 아닌 계를 직접 구성하고 어느 가정이 깨지는지 설명할 수 있다.
  - 흡인 영역을 SOS 로 인증하고 그 인증이 수치 적분으로 얻은 영역에 포함되는지 검증할 수 있다.
prerequisites: []
difficulty: 5
estimated_minutes: 540
tags: [nonlinear-control, lyapunov, iss, sum-of-squares, region-of-attraction, research]
activities:
  - id: c3-lyapunov-stability-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c3-lyapunov-stability-papers
    kind: reading
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c3-lyapunov-stability-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: c3-lyapunov-stability-reproduction
    kind: exercise
    title: 재현 과제 — SOS 로 흡인 영역 인증 (R1)
    estimated_minutes: 105
  - id: c3-lyapunov-stability-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Khalil, Nonlinear Systems (3rd ed., 2002)"
    kind: book
    note: ch.4 전체(안정성·불변 집합·비교 함수·ISS), ch.4.9 가 ISS 다. 이 모듈의 1순위 교재. (공식 URL 미확인)
  - title: "Tedrake, Underactuated Robotics"
    url: https://underactuated.csail.mit.edu/
    kind: book
    note: ch.9 (Lyapunov analysis) — SOS 로 Lyapunov 함수를 찾는 절차의 로보틱스 쪽 입구. 전문 무료.
  - title: "Sontag — Smooth stabilization implies coprime factorization (1989)"
    url: https://doi.org/10.1109/9.28018
    kind: article
    note: 필독 1. ISS 가 처음 정의된 논문. §I·§III 의 정의와 주 정리만 본다.
  - title: "Papachristodoulou & Prajna — On the construction of Lyapunov functions using the sum of squares decomposition (2002)"
    url: https://doi.org/10.1109/CDC.2002.1184414
    kind: article
    note: 필독 2. SOS 로 Lyapunov 함수를 탐색하는 표준 정식화.
  - title: "Topcu, Packard & Seiler — Local stability analysis using simulations and sum-of-squares programming (2008)"
    url: https://doi.org/10.1016/j.automatica.2008.03.010
    kind: article
    note: 필독 3. 재현 과제가 이 논문의 절차(시뮬레이션으로 상한, SOS 로 하한)를 축소한 것이다.
  - title: "Sontag & Wang — On characterizations of the input-to-state stability property (1995)"
    url: https://doi.org/10.1016/0167-6911(94)00050-6
    kind: article
    note: 권장. ISS 와 ISS-Lyapunov 함수의 동등성(역방향)을 준다.
  - title: "CVXPY"
    url: https://www.cvxpy.org/
    kind: other
    note: 재현 과제의 SDP 를 푸는 도구. SCS·Clarabel 중 아무 솔버나 쓴다.
---

# Lyapunov 안정성과 ISS

## 전제와 기호

이 레슨은 C3 모듈의 첫 레슨이고, 이후 다섯 레슨(피드백 선형화·수축·수동성·적응·CBF)이 모두
여기서 세운 판정 도구를 쓴다. 다음을 전제한다(권장 선수: `robotics-expert` 코스의 M3 제어
모듈, 연구 트랙 R0 의 `r0-convex-optimization`·`r0-estimation-theory`).

- 해석: 벡터장의 국소 Lipschitz 조건과 ODE 해의 존재·유일성, Gronwall 부등식, 콤팩트성.
- 선형대수: 대칭행렬의 정부호성, Lyapunov 방정식 $A^\top P + PA = -Q$.
- 볼록 최적화: SDP 와 그 쌍대, 그리고 "$M \succeq 0$" 이 제약으로 들어간다는 사실
  (`r0-convex-optimization`). SOS 절은 이것만 있으면 읽힌다.
- 미분기하는 요구하지 않는다. 리만 계량은 `c3-contraction-incremental` 에서 처음 쓴다.

표기 규약(이 모듈 전체에 고정):

| 기호 | 뜻 |
|---|---|
| $\dot{x} = f(x)$ | $f : D \to \mathbb{R}^n$, $D \subseteq \mathbb{R}^n$ 열린집합, $f(0) = 0$, $f$ 는 국소 Lipschitz |
| $\dot{x} = f(x, u)$ | 입력이 있는 계. $u(\cdot)$ 는 본질적 유계 가측 함수, $\lVert u \rVert_\infty = \operatorname{ess\,sup}_{t \ge 0} \lvert u(t) \rvert$ |
| $\phi(t; x_0)$ | $x_0$ 에서 출발한 해(flow). 입력이 있으면 $\phi(t; x_0, u)$ |
| $V(x)$ | Lyapunov 함수 후보. $\dot{V}(x) = \nabla V(x)^\top f(x)$ ("$f$ 를 따른 미분") |
| $\alpha \in \mathcal{K}$ | 비교 함수. $\alpha(0)=0$, 연속, 강증가 |
| $\alpha \in \mathcal{K}_\infty$ | 위에 더해 $\alpha(r) \to \infty$ ($r \to \infty$) |
| $\beta \in \mathcal{KL}$ | $\beta(r,t)$ 가 $r$ 에 대해 $\mathcal{K}$, $t$ 에 대해 감소하며 $\beta(r,t)\to 0$ ($t\to\infty$) |
| $\mathcal{R}_A$ | 흡인 영역(region of attraction) $= \{x_0 : \phi(t;x_0) \to 0\}$ |
| $\Omega_c$ | 준위집합(sublevel set) $\{x : V(x) \le c\}$ |

안정성의 정의는 $\varepsilon$–$\delta$ 로 쓴다: 원점이 **안정**이면 모든 $\varepsilon>0$ 에 대해
$\delta>0$ 가 있어 $\lvert x_0 \rvert < \delta \Rightarrow \lvert \phi(t;x_0)\rvert < \varepsilon\ (\forall t \ge 0)$.
여기에 $\phi(t;x_0) \to 0$ 이 더해지면 **점근 안정**, 수렴이 $\lvert \phi \rvert \le k\lvert x_0\rvert e^{-\lambda t}$
형태면 **지수 안정**이다. 비교 함수를 쓰면 "점근 안정 $\iff$ $\lvert \phi(t;x_0)\rvert \le \beta(\lvert x_0\rvert, t)$
인 $\beta \in \mathcal{KL}$ 이 존재"로 한 줄에 쓸 수 있고, 이 표현이 ISS 로 가는 다리다.

## 시작 전 자가 진단

아래 4문항을 전부 풀 수 있으면 권장 선수 레슨을 건너뛰어도 좋다. **두 문항 이상 막히면** 괄호에
적힌 선수 레슨으로 돌아가는 편이 빠르다. 정답과 허용오차를 바로 공개한다.

1. $A = \begin{bmatrix} 0 & -1 \\ 1 & -1\end{bmatrix}$ 의 고윳값을 구하라. 원점은 안정인가?
   (권장 선수: 선형대수 — `robotics-expert` M1)
   **정답**: $\lambda = -\tfrac12 \pm \tfrac{\sqrt3}{2} i$, 실수부가 음수이므로 지수 안정.
   허용오차 $10^{-6}$.
2. 같은 $A$ 에 대해 $A^\top P + PA = -I$ 를 만족하는 대칭 $P$ 를 구하라.
   (권장 선수: `r0-linear-algebra-decompositions`)
   **정답**: $P = \begin{bmatrix} 1.5 & -0.5 \\ -0.5 & 1\end{bmatrix}$, 허용오차 $10^{-9}$.
   검산: $\operatorname{eig}(P) \approx \{0.690983,\ 1.809017\}$, $\det P = 1.25$.
3. $\dot{x} = -x^3$ 의 원점은 점근 안정인가? 지수 안정인가? 한 문장으로 근거를 적어라.
   (권장 선수: `robotics-expert` M3)
   **정답**: 점근 안정이지만 지수 안정은 아니다. 해가 $x(t) = x_0/\sqrt{1 + 2x_0^2 t}$ 로
   $O(t^{-1/2})$ 로만 줄어들고, 선형화 $\dot{x} \approx 0$ 는 아무 정보를 주지 않는다.
4. $\min_P \{ \operatorname{tr} P : P \succeq I,\ A^\top P + PA \preceq -I \}$ 는 어떤 종류의
   최적화 문제인가? (권장 선수: `r0-convex-optimization`)
   **정답**: SDP(semidefinite program) — 목적이 선형이고 제약이 선형행렬부등식(LMI)이다.
   이 레슨의 SOS 절은 이 틀에 다항식 제약을 얹는 것뿐이다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (Lyapunov 안정성 정리) [D3]** — $V \in C^1(D)$, $V(0)=0$, $V(x)>0$ ($x \in D\setminus\{0\}$)
  이고 $\dot{V}(x) \le 0$ 이면 원점은 안정하다. $\dot{V}$ 가 $D\setminus\{0\}$ 에서 음이면
  점근 안정이다. $D = \mathbb{R}^n$ 이고 $V$ 가 **방사 비유계**($\lvert x\rvert \to \infty
  \Rightarrow V(x) \to \infty$)이면 전역 점근 안정(GAS)이다.
- **R2 (지수 안정성의 역정리, converse theorem) [D3]** — 원점이 $D_0$ 에서 지수 안정이고
  $f$ 가 $C^1$ 이면
  $$
  V(x) = \int_0^T \phi(\tau; x)^\top \phi(\tau; x)\, d\tau \tag{1}
  $$
  는 적당한 $T$ 에 대해 $c_1\lvert x\rvert^2 \le V(x) \le c_2 \lvert x \rvert^2$,
  $\dot{V}(x) \le -c_3\lvert x\rvert^2$, $\lVert \partial V/\partial x\rVert \le c_4 \lvert x \rvert$
  를 만족한다. 즉 **Lyapunov 함수는 항상 존재한다** — 문제는 존재가 아니라 구성이다.
- **R3 (LaSalle 불변 집합 정리와 Barbashin–Krasovskii) [D3]** — $\Omega$ 가 콤팩트하고 전진
  불변이며 $V \in C^1$ 이 $\Omega$ 에서 $\dot{V} \le 0$ 이면, $\Omega$ 에서 출발한 모든 해는
  $E = \{x \in \Omega : \dot{V}(x) = 0\}$ 안의 **최대 불변 집합** $M$ 에 수렴한다. 따름정리
  (Barbashin–Krasovskii): $V$ 가 양정이고 $\dot V \le 0$ 이며 $E$ 안에 원점 말고는 계속
  머무는 해가 없으면 원점은 점근 안정이다.
- **R4 (ISS 와 비교 함수) [D2]** — $\alpha_1,\alpha_2,\alpha_3 \in \mathcal{K}_\infty$,
  $\sigma \in \mathcal{K}$ 에 대해
  $$
  \alpha_1(\lvert x\rvert) \le V(x) \le \alpha_2(\lvert x \rvert), \qquad
    \nabla V(x)^\top f(x,u) \le -\alpha_3(\lvert x \rvert) + \sigma(\lvert u \rvert) \tag{2}
  $$
  를 만족하는 $V$ (ISS-Lyapunov 함수)가 있으면 계는 ISS 다:
  $$
  \lvert \phi(t;x_0,u)\rvert \le \beta(\lvert x_0\rvert, t) + \gamma(\lVert u\rVert_\infty),
    \qquad \gamma = \alpha_1^{-1}\!\circ\, 2\,\alpha_2 \circ \alpha_3^{-1} \circ 2\sigma. \tag{3}
  $$
  역도 성립한다(Sontag–Wang 1995). **[D1]**
- **R5 (SOS 인증과 흡인 영역) [D2]** — $f$ 가 다항식이고 $V$, $\lambda$ 가 다항식일 때
  $$
  V - \epsilon \lvert x\rvert^2 \in \Sigma, \qquad
    -\dot{V} - \lambda(x)\,(c - V(x)) - \epsilon \lvert x \rvert^2 \in \Sigma,
    \qquad \lambda \in \Sigma \tag{4}
  $$
  ($\Sigma$ 는 SOS 다항식의 집합)이 가해이면 $\Omega_c = \{V \le c\}$ 는 유계일 때
  $\mathcal{R}_A$ 에 포함된다. (4)는 $V$ 와 $\lambda$ 에 대해 **겹선형(bilinear)** 이므로
  하나를 고정해 번갈아 푸는 교대 최적화가 된다. 이 인증은 **충분조건일 뿐**이다.

## 유도

### R4 — ISS-Lyapunov 함수에서 ISS 추정식으로

(2)를 가정하고 (3)을 만든다. 입력을 고정하고 $\mu := \lVert u \rVert_\infty$ 로 둔다.
핵심 착상은 "$\sigma(\mu)$ 를 $\alpha_3$ 의 **절반**으로 흡수할 수 있는 영역"과 그 바깥을
나누는 것이다(이득 여유, gain margin).

**1단계 (여유가 있는 영역).** $\theta = \tfrac12$ 로 두고
$\alpha_3(\lvert x \rvert) \ge 2\sigma(\mu)$ 인 $x$ 를 생각하면 (2)에서

$$
\dot{V} \le -\alpha_3(\lvert x\rvert) + \sigma(\mu)
  \le -\alpha_3(\lvert x\rvert) + \tfrac12 \alpha_3(\lvert x\rvert)
  = -\tfrac12 \alpha_3(\lvert x \rvert). \tag{5}
$$

**2단계 ($V$ 만의 미분부등식으로).** (2)의 오른쪽 부등식 $V \le \alpha_2(\lvert x\rvert)$ 에서
$\lvert x \rvert \ge \alpha_2^{-1}(V)$ 이고 $\alpha_3$ 가 증가하므로 (5)는

$$
\dot{V} \le -\tfrac12\,\alpha_3\!\left(\alpha_2^{-1}(V)\right) =: -\rho(V),
  \qquad \rho \in \mathcal{K}. \tag{6}
$$

$x$ 가 사라지고 $V$ 만 남은 것이 요점이다. 비교 보조정리(Khalil Lemma 3.4)를 $\dot{y} = -\rho(y)$,
$y(0) = V(x_0)$ 에 적용하면 해당 구간에서 $V(t) \le y(t) = \sigma_{\mathcal{KL}}(V(x_0), t)$ 이고
$\sigma_{\mathcal{KL}} \in \mathcal{KL}$ 이다.

**3단계 (들어가면 못 나오는 준위집합).**

$$
c_\mu := \alpha_2\!\left(\alpha_3^{-1}(2\sigma(\mu))\right) \tag{7}
$$

로 두고 $V(x) \ge c_\mu$ 라고 하자. 그러면 $\alpha_2(\lvert x\rvert) \ge V(x) \ge c_\mu$ 이므로
$\lvert x \rvert \ge \alpha_3^{-1}(2\sigma(\mu))$, 즉 $\alpha_3(\lvert x\rvert) \ge 2\sigma(\mu)$ 이고
(5)가 적용되어 $\dot{V} \le -\sigma(\mu) < 0$ ($\mu > 0$). 따라서 $\Omega_{c_\mu}$ 는 **전진
불변**이고, 그 바깥에서는 $V$ 가 엄격히 감소한다. 결론적으로 모든 $t\ge0$ 에서

$$
V(t) \le \max\{\, \sigma_{\mathcal{KL}}(V(x_0), t),\ c_\mu \,\} \le \sigma_{\mathcal{KL}}(V(x_0),t) + c_\mu. \tag{8}
$$

**4단계 (상태로 되돌리기).** $\lvert x \rvert \le \alpha_1^{-1}(V)$ 와 임의의
$\kappa \in \mathcal{K}$ 에 대한 약한 삼각부등식
$\kappa(a+b) \le \kappa(2a) + \kappa(2b)$ (증명: $a+b \le 2\max(a,b)$ 와 단조성)를 (8)에 쓰면

$$
\lvert x(t)\rvert \le \alpha_1^{-1}\!\big(2\sigma_{\mathcal{KL}}(\alpha_2(\lvert x_0\rvert), t)\big)
  + \alpha_1^{-1}\!\big(2 c_\mu\big)
  =: \beta(\lvert x_0 \rvert, t) + \gamma(\mu), \tag{9}
$$

즉 (3)이다. $\beta \in \mathcal{KL}$, $\gamma = \alpha_1^{-1}\circ 2\alpha_2 \circ
\alpha_3^{-1}\circ 2\sigma \in \mathcal{K}$ 이고, $\mu \to 0$ 에서 $\gamma(\mu)\to0$ 이므로
입력이 없으면 (9)는 0-GAS 추정으로 되돌아간다.

**가정이 깨지는 곳**: (2)의 $\alpha_3$ 가 $\mathcal{K}_\infty$ 가 아니라 유계인
$\mathcal{K}$ 이면 3단계의 $\alpha_3^{-1}(2\sigma(\mu))$ 가 큰 $\mu$ 에서 **정의되지 않는다** —
이때 얻는 것은 "작은 입력에 대한" 국소 ISS 뿐이다. 실제 예:

$$
\dot{x} = -x + x^2 u \tag{10}
$$

는 $u \equiv 0$ 에서 GAS(0-GAS)이지만 ISS 가 아니다. 상수 입력 $u \equiv \mu > 0$ 이면
$\dot{x} = -x + \mu x^2$ 의 불안정 평형점이 $x = 1/\mu$ 이고, $x_0 > 1/\mu$ 는 유한 시간에
발산한다(수치 확인: $\mu = 0.1$, $x_0 = 10.01$ 에서 $t \lesssim 20$ 안에 $10^8$ 을 넘고,
$x_0 = 5$ 는 0 으로 수렴한다). 유계 입력에 대해 상태가 유계라는 (3)이 깨지므로 ISS 가 아니다 —
그러나 $\mu$ 를 작게 잡을수록 탈출 문턱 $1/\mu$ 가 커지므로 **국소 ISS 는 성립한다**.

### R5 — SOS 로 Lyapunov 함수를 찾고 흡인 영역을 인증하기

유도의 뼈대는 **S-절차(S-procedure)**다. "$\Omega_c$ 안에서 $\dot V < 0$" 은 집합 포함
관계이고, 이것을 다항식 부등식 하나로 바꾸는 데 승수 $\lambda(x) \ge 0$ 을 쓴다.

**1단계.** 목표는 다음 두 조건이다: ⓐ $V$ 가 양정, ⓑ
$x \in \Omega_c \setminus\{0\} \Rightarrow \dot{V}(x) < 0$. ⓑ 를 그대로 쓰면 조건부
부등식이라 SDP 가 되지 않는다.

**2단계 (승수로 조건을 흡수).** $\lambda(x) \ge 0$ 이고

$$
-\dot{V}(x) \ge \lambda(x)\,(c - V(x)) + \epsilon\lvert x\rvert^2 \tag{11}
$$

가 **모든** $x$ 에서 성립한다고 하자. $x \in \Omega_c$ 면 $c - V(x) \ge 0$ 이므로 (11)의 오른쪽은
$\ge \epsilon\lvert x\rvert^2$ 이고 따라서 $\dot{V}(x) \le -\epsilon \lvert x\rvert^2 < 0$
($x \ne 0$). 조건부 부등식이 **무조건** 부등식 하나로 바뀌었다.

**3단계 (SOS 로 완화).** "모든 $x$ 에서 다항식이 비음" 은 일반적으로 NP-난해이므로 더 강한
충분조건인 SOS 로 바꾼다: $p \in \Sigma \iff p = \sum_i q_i^2 \iff p = z^\top Q z,\ Q \succeq 0$
($z$ 는 단항식 벡터). 이 동치가 (4)를 **SDP** 로 만든다. $Q \succeq 0$ 가 LMI 이기 때문이다.

**4단계 (겹선형성과 교대 최적화).** (11)에는 $\lambda(x) V(x)$ 항이 있어 $(V, \lambda)$ 에 대해
동시 볼록이 아니다. 실무의 해법은 번갈아 푸는 것이다:
(i) $V$ 를 고정해 $\lambda$ 와 $c$ 를 찾는다(이때 $c$ 를 최대화하면 준볼록 — 이분법으로 처리),
(ii) $\lambda$ 를 고정해 $V$ 를 찾는다(볼록). 각 단계가 SDP 이고, 목적함수는 보통 $\Omega_c$ 의
부피 대리값(예: $\det$ 또는 미리 정한 모양 집합 $\{x^\top N x \le \beta\} \subseteq \Omega_c$ 의
$\beta$)을 최대화한다. Topcu et al. 2008 은 여기에 시뮬레이션에서 얻은 **상한**을 붙여 탐색
범위를 좁힌다.

**구체 예 (재현 과제의 기준선).** 시간을 거꾸로 돌린 van der Pol 계

$$
\dot{x}_1 = -x_2, \qquad \dot{x}_2 = x_1 + (x_1^2 - 1)x_2 \tag{12}
$$

는 원점이 지수 안정이고 흡인 영역이 불안정 한계 순환(limit cycle)으로 둘러싸인 표준 예다.
선형화는 $A = \begin{bmatrix} 0 & -1\\ 1 & -1\end{bmatrix}$ ($\lambda = -\tfrac12 \pm
\tfrac{\sqrt3}{2}i$). $A^\top P + PA = -I$ 를 풀면

$$
P = \begin{bmatrix} 1.5 & -0.5 \\ -0.5 & 1 \end{bmatrix}, \qquad
  V(x) = 1.5x_1^2 - x_1x_2 + x_2^2, \qquad \det P = 1.25. \tag{13}
$$

(12)를 $f(x) = Ax + \begin{bmatrix}0\\ x_1^2x_2\end{bmatrix}$ 로 쪼개면 $\dot V$ 가 닫힌 형태로
나온다:

$$
\dot{V} = x^\top(A^\top P + PA)x + 2x^\top P \begin{bmatrix}0\\ x_1^2x_2\end{bmatrix}
  = -\lvert x\rvert^2 + 2x_1^2x_2\left(x_2 - \tfrac12 x_1\right). \tag{14}
$$

극좌표 $x = r u(\vartheta)$ 를 넣으면 $\dot V = -r^2 + 2r^4 u_1^2u_2(u_2 - \tfrac12 u_1)$ 이므로
$\dot V = 0$ 인 반지름이 $r^2 = 1/g(\vartheta)$, $g := 2u_1^2u_2(u_2-\tfrac12u_1)$ 로 **명시적으로**
풀린다. 가장 큰 인증 준위는

$$
c^\star = \min_{g(\vartheta)>0} \frac{u^\top P u}{g(\vartheta)} = 2.304478, \tag{15}
$$

$\Omega_{c^\star}$ 의 면적은 $\pi c^\star/\sqrt{\det P} = 6.475411$ 이다(모두 허용오차
$10^{-4}$, 2·10⁶ 방향 격자). 같은 계의 실제 흡인 영역을 수치 적분으로 추정하면 면적이
약 $13.72$ 이므로 **이차 $V$ 의 인증은 참값의 47% 밖에 덮지 못한다**. 이 간극을 좁히는 것이
재현 과제다.

**가정이 깨지는 곳**: (4)는 충분조건이다. ⓐ $\Omega_c$ 가 유계가 아니면 포함 논증이 깨진다
(인증 전에 유계성을 따로 확인해야 한다). ⓑ Positivstellensatz 의 차수 간극 때문에, 비음이지만
어떤 고정 차수로도 SOS 가 아닌 다항식이 존재한다 — 차수를 올려도 실패할 수 있고 "실패"가
"불안정"을 뜻하지 않는다. ⓒ SDP 솔버의 수치 오차로 $Q$ 의 최소 고윳값이 $-10^{-9}$ 수준인
"인증"이 나올 수 있다. 인증은 받은 뒤 **반드시 다시 검사한다**(격자·무작위 표본에서
$\dot V<0$, Gram 행렬의 최소 고윳값, 가능하면 유리수 반올림 후 정확 산술).

## 증명 스케치

### R1 — Lyapunov 정리

**가설** H1: $V \in C^1(D)$, $V(0)=0$, $V>0$ on $D\setminus\{0\}$. H2: $\dot V \le 0$ on $D$.
**결론** C: 원점은 안정. (H2 를 $\dot V<0$ 으로 강화하면 점근 안정.)

**전략**: $V$ 의 준위집합을 $\varepsilon$-공 안에 **갇힌 통**으로 쓴다. 해는 준위집합을 넘지
못하므로 $\delta$ 를 그 통의 안쪽 공으로 잡는다.

1. $\varepsilon>0$ 에 대해 $\bar{B}_r \subset D$ 인 $r \in (0,\varepsilon]$ 을 고르고
   $m := \min_{\lvert x\rvert = r} V(x)$ 라 두면 H1 과 구면의 콤팩트성으로 $m>0$.
2. $c \in (0,m)$ 을 하나 잡고 $\Omega_c \cap B_r$ 을 생각한다. $V$ 의 연속성과 $V(0)=0$ 에서
   $B_\delta \subseteq \Omega_c$ 인 $\delta>0$ 가 있다.
3. H2 로 $V(\phi(t;x_0))$ 는 비증가다. $x_0 \in B_\delta$ 면 $V(\phi(t)) \le V(x_0) \le c < m$
   이므로 해는 $\lvert x \rvert = r$ 에 **도달할 수 없다**(도달하면 $V \ge m$). 따라서
   $\lvert \phi(t;x_0)\rvert < r \le \varepsilon$ — 이것이 안정성의 정의다.
4. (점근 안정) $\dot V<0$ 이면 $V(\phi(t))$ 는 강감소하고 아래로 유계이므로 $V \to a \ge 0$.
   $a>0$ 이라면 해가 콤팩트 껍질 $\{a \le V \le V(x_0)\}$ 에 갇히고 거기서
   $\dot V \le -\max < 0$ 이라 유한 시간에 $V<a$ 가 되어 모순. 따라서 $a=0$, 즉 $x \to 0$.

**가설을 지우면**: H2 를 $\dot V \le 0$ 으로만 두면 점근 안정을 얻지 못한다 — $\dot x_1 = x_2$,
$\dot x_2 = -x_1$ 에 $V = \lvert x\rvert^2$ 를 쓰면 $\dot V \equiv 0$ 이고 해는 원을 영원히 돈다.
이 간극을 메우는 것이 R3 이다. 또 $D = \mathbb{R}^n$ 이어도 **방사 비유계성이 없으면 전역
결론이 거짓**이다. 반례(Khalil ch.4):

$$
\dot{x}_1 = \frac{-6x_1}{(1+x_1^2)^2} + 2x_2, \qquad
  \dot{x}_2 = \frac{-2(x_1+x_2)}{(1+x_1^2)^2}, \qquad
  V = \frac{x_1^2}{1+x_1^2} + x_2^2. \tag{16}
$$

$\dot V$ 는 원점 밖 모든 곳에서 음이지만($\lvert x\rvert \le 40$ 격자에서 최대
$-2.9\cdot10^{-9}$), $V$ 의 준위집합이 $c \ge 1$ 에서 유계가 아니라 2단계의 "갇힌 통"이
사라진다. 실제로 $x_0 = (4,\ 1.2)$ 에서 출발한 해는 $x_1$ 이 $t=60$ 까지 144 를 넘어 계속
커지며 원점으로 가지 않는다(수치 확인). $V$ 가 유계이면서 상태가 발산할 수 있다는 것이 요점이다.

생략한 기술적 단계: 해의 최대 존재 구간이 $\Omega_c$ 안에서 $[0,\infty)$ 로 늘어난다는 사실
(전진 불변 콤팩트 집합 + 국소 Lipschitz). Khalil Thm 4.1 의 증명 참조.

### R2 — 지수 안정성의 역정리

**가설** H1: $\lvert \phi(t;x)\rvert \le k\lvert x\rvert e^{-\lambda t}$ for $x \in D_0$, $k,\lambda>0$.
H2: $f \in C^1$ 이고 $D_0$ 에서 $\lVert \partial f/\partial x\rVert \le L$.
**결론** C: (1)의 $V$ 가 네 부등식($c_1,\dots,c_4$)을 만족하는 Lyapunov 함수다.

**전략**: 궤적을 **시간에 대해 적분**해 Lyapunov 함수를 만든다(Massera 의 착상). $\dot V$ 는
반군 성질 $\phi(\tau;\phi(t;x)) = \phi(t+\tau;x)$ 덕분에 적분 없이 두 끝점으로 계산된다.

1. **위쪽 경계.** H1 로 $V(x) \le \int_0^T k^2\lvert x\rvert^2 e^{-2\lambda\tau}d\tau
   \le \frac{k^2}{2\lambda}\lvert x\rvert^2 =: c_2 \lvert x\rvert^2$.
2. **아래쪽 경계.** H2 와 Gronwall 로 $\lvert \phi(\tau;x)\rvert \ge \lvert x\rvert e^{-L\tau}$.
   따라서 $V(x) \ge \frac{1-e^{-2LT}}{2L}\lvert x\rvert^2 =: c_1\lvert x\rvert^2 > 0$.
3. **감소율.** $V(\phi(t;x))= \int_t^{t+T} \lvert\phi(s;x)\rvert^2 ds$ 이므로 $t$ 로 미분하면
   $\dot V(x) = \lvert \phi(T;x)\rvert^2 - \lvert x\rvert^2 \le (k^2e^{-2\lambda T} - 1)\lvert x\rvert^2$.
   $T > \frac{\ln k}{\lambda}$ 로 잡으면 괄호가 음수가 되어 $c_3>0$ 를 얻는다. **$T$ 를 고르는
   이 한 줄이 증명의 전부**다.
4. **기울기 경계.** $x \mapsto \phi(\tau;x)$ 의 미분이 변분방정식의 해이고 H2 로
   $\lVert \partial\phi/\partial x\rVert \le e^{L\tau}$ 이므로 $\lVert \partial V/\partial x\rVert
   \le c_4\lvert x\rvert$ ($c_4$ 는 $k,L,\lambda,T$ 로 명시). $V$ 의 매끄러움은 $\phi$ 의
   매끄러움에서 온다.

**가설을 지우면**: 수렴이 지수적이 아니라 점근적일 뿐이면 (1)의 적분이 $\lvert x\rvert^2$ 로
비교되지 않아 2·3단계의 상수가 사라진다 — 이때는 $\int_0^\infty g(\lvert \phi\rvert)d\tau$
형태의 가중 적분을 쓰는 Massera·Kurzweil 구성이 필요하고, 결과도 "매끄러운 $V$ 가 존재한다"는
약한 형태다(Khalil Thm 4.16·4.17). 또 $f$ 가 국소 Lipschitz 이기만 하면 해의 유일성은 있어도
$\phi$ 가 $x$ 에 대해 $C^1$ 이 아니어서 4단계가 깨진다.

생략한 기술적 단계: 변분방정식 해의 존재와 그 경계(Khalil Lemma 3.4·Thm 3.5).

### R3 — LaSalle 불변 집합 정리

**가설** H1: $\Omega$ 콤팩트, 전진 불변. H2: $V\in C^1$, $\dot V \le 0$ on $\Omega$.
**결론** C: $x_0 \in \Omega \Rightarrow \phi(t;x_0) \to M$, $M$ 은 $E=\{\dot V=0\}$ 안의 최대 불변 집합.

**전략**: $\omega$-극한집합. "$V$ 가 극한집합에서 상수" $\Rightarrow$ "극한집합에서 $\dot V=0$".

1. H2 로 $t \mapsto V(\phi(t))$ 는 비증가, H1 로 아래로 유계 $\Rightarrow$ 극한 $a$ 가 존재.
2. H1 로 궤적이 유계이므로 $\omega$-극한집합 $\omega(x_0)$ 는 공집합이 아니고 콤팩트이며
   **불변**이고 $\phi(t;x_0) \to \omega(x_0)$ (거리 의미). [표준 사실]
3. $p \in \omega(x_0)$ 면 $\phi(t_n) \to p$ 인 $t_n \to\infty$ 가 있고 $V$ 의 연속성으로
   $V(p) = a$. 즉 $V \equiv a$ on $\omega(x_0)$.
4. $\omega(x_0)$ 가 불변이므로 거기서 출발한 해가 그 안에 머물고 $V$ 는 상수 $a$ 다. 따라서
   그 해 위에서 $\dot V = 0$, 즉 $\omega(x_0) \subseteq E$. 불변성까지 쓰면
   $\omega(x_0)\subseteq M$. 2단계의 수렴과 합치면 C.
5. (Barbashin–Krasovskii) $V$ 양정·$\dot V\le0$ 이면 유계인 $\Omega_c$ 를 $\Omega$ 로 쓸 수 있고,
   $E$ 안에 머무는 해가 원점뿐이면 $M=\{0\}$ 이므로 점근 안정.

**가설을 지우면**: H1 의 **콤팩트성**을 빼면 결론이 거짓이다 — (16)이 바로 그 예로, $\dot V\le0$
이지만 준위집합이 유계가 아니어서 해가 무한으로 간다. $M$ 이 원점보다 큰 집합일 수도 있다:
$\dot V = 0$ 인 집합에 한계 순환이 들어 있으면 LaSalle 은 "그 순환에 수렴한다"까지만 말해 준다.

생략한 기술적 단계: $\omega$-극한집합의 성질(비공·콤팩트·불변·수렴). Khalil Lemma 4.1.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R4)** (3)의 이득 $\gamma$ 를 $\theta = \tfrac12$ 가 아닌 임의의
$\theta \in (0,1)$ 로 다시 유도하라. $\theta$ 를 1 에 가깝게 잡으면 $\gamma$ 는 어떻게 변하고
대신 무엇을 잃는가?
*해답 스케치*: (5)가 $\dot V \le -(1-\theta)\alpha_3$ 로, (7)이
$c_\mu = \alpha_2(\alpha_3^{-1}(\sigma(\mu)/\theta))$ 로 바뀐다. $\theta \to 1$ 에서 $c_\mu$ 가
작아져 $\gamma$ 는 **좋아지지만** (6)의 감소율 $(1-\theta)$ 가 0 으로 가 수렴 속도 $\beta$ 가
나빠진다. 이득과 수렴률의 교환이 한 매개변수에 들어 있다.

**P2 (유도, ★★, R2)** (1)에서 $T \to \infty$ 로 보내면 어떤 조건에서 $V$ 가 잘 정의되는가?
$T=\infty$ 판을 쓰면 3단계의 $\dot V$ 계산은 어떻게 간단해지고, 대신 어느 경계가 사라지는가?
*해답 스케치*: H1 의 지수 경계로 적분이 수렴하므로 $T=\infty$ 도 잘 정의된다. 이때
$\dot V = -\lvert x\rvert^2$ 로 **정확히** 떨어져 $c_3=1$ 이 된다. 잃는 것은 2단계의
$c_1 = (1-e^{-2LT})/2L$ 가 $1/2L$ 로 느슨해지는 것이 아니라, 유한 $T$ 가 주던
"$k,\lambda$ 를 모르고도 수치적으로 적분 가능" 이라는 실용성이다.

**P3 (계산, ★, R5)** (12)에 대해 ⓐ $P$, ⓑ $c^\star$, ⓒ $\Omega_{c^\star}$ 의 면적을 구하라.
*정답*: ⓐ (13)의 $P$ (허용오차 $10^{-9}$) ⓑ $c^\star = 2.304478$ ($10^{-4}$)
ⓒ $6.475411$ ($10^{-4}$). 검산: (14)의 닫힌 형태를 쓰고 $\dot V=0$ 을 극좌표에서 풀어
$u^\top Pu/g(\vartheta)$ 의 최소를 찾는다. 최소를 주는 방향은 $\vartheta^\star \approx 2.42174$
(rad), 그 지점의 $r^\star \approx 1.138343$. 면적은 $\pi c^\star/\sqrt{\det P}$.

**P4 (구현, ★★★, R5)** (4)의 교대 최적화를 4차 $V$ 에 대해 구현하라. 단항식 기저 구성,
Gram 행렬 제약, $c$ 에 대한 이분법을 직접 쓴다(SOS 전용 패키지 금지, SDP 솔버만 사용).
*루브릭*: ⓐ 2차 $V$ 로 돌렸을 때 (15)의 $c^\star$ 를 $10^{-3}$ 이내로 재현한다 ⓑ 4차 $V$ 의
인증 면적이 2차 기준선보다 크다 ⓒ 인증을 받은 뒤 **독립적으로** 재검사한다(무작위
$10^5$ 점에서 $\dot V<0$, Gram 최소 고윳값 보고) ⓓ 교대의 종료 조건과 반복 상한이 코드에 있다.

**P5 (반례, ★★, R4)** 0-GAS 이지만 ISS 가 아닌 계를 (10)과 **다른 형태로** 하나 만들고,
(2)의 어느 부등식이 어떤 $\alpha_3$ 로도 성립할 수 없는지 보여라. 이어서 같은 계가 국소
ISS 임을 보이는 $\mathcal{K}$ 함수를 제시하라.
*성질 체크리스트*: ⓐ $u\equiv0$ 에서 GAS ⓑ 어떤 유계 입력에서 상태가 유계가 아님(유한 시간
탈출이면 충분) ⓒ $\alpha_3$ 가 유계인 $\mathcal{K}$ 로만 잡히는 구조(입력이 상태에 곱으로
들어가면 전형적) ⓓ 국소 결론에서 입력 크기 상한이 명시됨.

**P6 (증명, ★★★, R3)** LaSalle 로부터 Barbashin–Krasovskii 를 유도하고, 이어서
"$\dot V \le 0$ 이고 $E$ 가 한계 순환을 포함하는" 계를 하나 구성해 LaSalle 이 점근 안정을
주지 **못하는** 예를 보여라.
*해답 스케치*: 전제는 $\Omega_c$ 의 유계성이다. 구성 쪽은 극좌표로 $\dot r = r(1-r)(\cdot)$
류의 계를 만들고 $V$ 를 $r$ 의 함수로 잡아 $\dot V$ 가 $r=1$ 에서 0 이 되게 한다.

**P7 (논문, ★★, R4·R5)** Topcu et al. 2008 을 읽고 ⓐ 시뮬레이션이 주는 것이 흡인 영역의
상한인지 하한인지, ⓑ 그 정보를 SOS 탐색의 어디에 끼워 넣는지, ⓒ 그 절차가 반례를 만났을 때
무엇을 보고하는지를 각각 3문장 이내로 쓰라. 저자들이 보고하지 않아 재현을 막는 정보 2개를
찾아라.
*루브릭*: "시뮬레이션은 발산하는 초기조건을 찾아 **상한**(바깥 경계)을 주고, SOS 는 인증된
**하한**을 준다"를 구분하면 통과. 솔버 설정·차수·정규화 중 빠진 것을 찍으면 가점.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Sontag, "Smooth stabilization implies coprime factorization" (1989, IEEE T-AC)**
   — 역할: `원전(seminal)`. <https://doi.org/10.1109/9.28018>
   ISS 가 처음 정의된 논문이다. 제목은 coprime factorization 이지만 우리가 읽을 곳은 ISS
   정의와 그 주 정리다.
   추가 질문: ⓐ 저자가 ISS 를 정의할 때 $\mathcal{KL}$·$\mathcal{K}$ 를 쓰는 이유는 무엇이고,
   "선형 이득($L_\infty$ 유도 노름)" 정식화로는 무엇을 놓치는가?
   ⓑ 이 논문의 결과는 **무엇을 보장하지 않는가** — 특히 (10)과 같은 계에 대해.
2. **Papachristodoulou & Prajna, "On the construction of Lyapunov functions using the sum of
   squares decomposition" (2002, IEEE CDC)** — 역할: `표준(standard)`.
   <https://doi.org/10.1109/CDC.2002.1184414>
   추가 질문: ⓐ 이 논문의 정식화를 우리 (4)와 대조해 승수 $\lambda$ 의 역할을 한 줄로 쓰라.
   ⓑ 유리함수·비다항식 비선형성(삼각함수 등)은 어떻게 다루는가, 그 변환은 무엇을 가정하는가?
3. **Topcu, Packard & Seiler, "Local stability analysis using simulations and sum-of-squares
   programming" (2008, Automatica)** — 역할: `표준(standard)`.
   <https://doi.org/10.1016/j.automatica.2008.03.010>
   재현 과제의 원형이다. 시뮬레이션과 SOS 를 **양쪽에서** 조이는 구조를 본다.
   추가 질문: ⓐ 시뮬레이션 자료를 선형 제약으로 바꾸는 단계에서 보수성이 어디서 생기는가?
   ⓑ 같은 절차를 10차원 계로 옮기면 어느 단계가 먼저 터지는가(SDP 크기를 차수·차원으로 세어라)?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R1 (수치 검증).** 계산 예산: 노트북 CPU 1분 이내(SDP 포함), numpy + scipy + SDP 솔버
하나(cvxpy 의 SCS 또는 Clarabel). 대상은 (12)의 시간 역전 van der Pol 계다.
입력 데이터는 없다 — 계가 식으로 주어지고 초기조건은 직접 생성한다.

**수용 기준 (네 조건 모두)**

1. **기준선 재현**: 2차 $V$ (13)에 대해 $c^\star = 2.304478 \pm 10^{-4}$,
   $\operatorname{area}(\Omega_{c^\star}) = 6.475411 \pm 10^{-4}$.
2. **인증의 건전성**: SOS 로 찾은 $(V_4, c_4)$ ($V_4$ 는 4차)에 대해 $\Omega_{c_4}$ 에서
   균등 추출한 $10^5$ 점 전부에서 $\dot V_4 < 0$ ($\lvert x\rvert > 10^{-3}$ 인 점만),
   그리고 두 Gram 행렬의 최소 고윳값이 $\ge -10^{-8}$.
3. **인증 $\subseteq$ 실제**: $\Omega_{c_4}$ 경계에서 추출한 $10^3$ 점 전부가 수치 적분
   ($T = 80$, RK4, $\Delta t \le 2\cdot10^{-3}$)으로 $\lvert x(T)\rvert < 10^{-3}$ 에 도달.
   **단 하나라도 발산하면 인증이 틀린 것이다** — 이 경우 2 의 재검사와 솔버 설정을 보고한다.
4. **개선 폭**: $\operatorname{area}(\Omega_{c_4}) \ge 1.3 \times 6.475411 = 8.418$.
   참고로 수치 적분으로 추정한 실제 흡인 영역의 면적은 약 $13.72$ (361개 방향에 대한 반지름
   이분법, 별 모양 근사)이므로 4차 인증은 그 61% 이상을 덮어야 한다.

**비교 대상**: ⓐ 2차 $V$ 의 인증(조건 1, 면적 6.475411) ⓑ 시뮬레이션으로 추정한 실제 흡인
영역(면적 ≈ 13.72) — 인증 면적은 이 둘 **사이**에 있어야 한다. 위로 넘으면 2 또는 3 이
거짓이다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| SDP 가 "infeasible" | $\epsilon$ 이 너무 크거나 $\lambda$ 차수가 0 (상수)로 고정됨 | $\epsilon$ 을 $10^{-6}$ 까지 낮추고 $\lambda$ 를 2차로 올려 다시 푼다 |
| 인증 면적이 실제 흡인 영역보다 크다 | 승수 부호 규약 오류 또는 $\dot V$ 계산에서 $f$ 를 잘못 대입 | 2차 $V$ 로 돌려 $c^\star = 2.304478$ 이 나오는지 먼저 확인한다 |
| 교대 최적화가 진동한다 | 각 단계의 목적함수가 서로 다른 양을 최대화 | 한 쪽은 $c$, 다른 쪽은 모양 집합 $\beta$ 로 목적을 **고정**하고 단조성을 로그로 확인한다 |
| Gram 최소 고윳값이 $-10^{-4}$ 수준 | 솔버 허용오차·스케일링 문제 | 변수 스케일을 맞추고(상태를 $O(1)$ 로 정규화) 솔버 허용오차를 $10^{-10}$ 으로 조인다 |
| 적분이 발산해 조건 3 이 실패 | $\Delta t$ 가 커서 한계 순환 근처에서 수치 불안정 | $\Delta t$ 를 절반으로 줄여 결과가 바뀌는지 본다(바뀌면 적분기 문제) |

## 열린 문제

- **(열린 문제) 학습된 동역학 위에서의 안정성 인증** — $f$ 가 신경망이면 (4)의 다항식 구조가
  사라져 SOS 가 그대로 쓰이지 않고, ReLU 망은 비매끄러워 $\dot V$ 가 점별로만 정의된다. 현재
  접근: [Chang et al., Neural Lyapunov Control (2020)](https://arxiv.org/abs/2005.00611) 의
  반례 유도 학습, [Dai et al., Lyapunov-stable neural-network control (2021)](https://arxiv.org/abs/2109.14152)
  의 MILP 검증. 비어 있는 자리: 망 크기에 대해 다항 시간으로 끝나면서 **건전한(sound)** 인증,
  그리고 인증 영역을 넓히는 학습 목표.
- **(열린 문제) 차원에 대한 인증 비용** — 4차 $V$ 의 Gram 행렬은 $\binom{n+2}{2}$ 변의
  정사각이라 $n=10$ 이면 SDP 변수가 수천 개로 늘고, 차수를 올리면 지수적으로 커진다. 현재 접근:
  [DSOS/SDSOS (Ahmadi & Majumdar 2017)](https://arxiv.org/abs/1706.02586) 처럼 LP/SOCP 로
  내려오는 완화, 좌표 분해·희소성 활용. 비어 있는 자리: 로봇 규모(20–50 상태)에서 보수성을
  정량적으로 통제하면서 쓸 수 있는 인증.
- **(열린 문제) 접촉·충격이 있는 계의 Lyapunov 이론** — 해가 비매끄럽고 유일하지 않을 수 있어
  $\dot V$ 가 고전적 의미로 존재하지 않는다. 현재 접근: 비매끄러운 Lyapunov 함수와 미분 포함
  (Clarke 미분), 측도 미분 포함. 비어 있는 자리: 상보성 제약을 가진 다물체 계의 흡인 영역
  인증 — `c2-contact-dynamics` 와 `c4-contact-implicit-hybrid` 에서 같은 벽을 다시 만난다.
- **(열린 문제) ISS 이득을 자료에서 추정하기** — (3)의 $\gamma$ 는 모델에서 유도되지만, 실제
  로봇에서 쓰는 모델은 틀린다. 유한한 실험으로 $\gamma$ 의 **신뢰 상한**을 주는 절차는
  정립되지 않았다. 현재 접근: 극단값 이론 기반 추정, 시나리오 최적화. 비어 있는 자리:
  표본 수에 대한 보장이 있는 추정량.

## 개념 점검

`rc quiz c3-lyapunov-stability` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c3-lyapunov-stability-quiz
questions:
  - id: q1
    type: single
    prompt: "$V$ 가 양정이고 $\\dot{V} \\le 0$ 이며 $D = \\mathbb{R}^n$ 인데도 전역 점근 안정을 결론할 수 없는 이유로 가장 정확한 것은?"
    choices:
      - "$\\dot{V} \\le 0$ 은 $\\dot{V} < 0$ 보다 약해서 수렴을 주지 않고, $V$ 가 방사 비유계가 아니면 준위집합이 유계가 아니기 때문"
      - "$V$ 가 미분 가능하지 않을 수 있기 때문"
      - "$f$ 가 국소 Lipschitz 가 아니면 해가 유일하지 않기 때문"
      - "선형화의 고윳값을 확인하지 않았기 때문"
    answer: 0
    explanation: "두 가지가 각각 다른 결론을 막는다. $\\dot V \\le 0$ 은 안정까지만 주므로 점근성은 LaSalle 이나 $\\dot V<0$ 이 필요하고, 전역성은 준위집합의 유계성(방사 비유계)에서 온다. 식 (16)이 후자의 반례다 — $\\dot V<0$ 인데도 해가 발산한다."
    concept: { front: "전역 점근 안정에 방사 비유계성이 필요한 이유", back: "준위집합 $\\Omega_c$ 가 유계여야 해가 갇힌다. $V = x_1^2/(1+x_1^2)+x_2^2$ 처럼 유계인 $V$ 는 발산하는 해를 허용한다" }
  - id: q2
    type: short
    prompt: "ISS-Lyapunov 조건 $\\dot V \\le -\\alpha_3(|x|) + \\sigma(|u|)$ 에서 입력 항을 $\\alpha_3$ 의 절반으로 흡수할 때, 그 영역 바깥에서 얻는 감소율은 $-\\alpha_3$ 의 몇 배인가? (숫자만)"
    answer: ["0.5", "1/2", "절반", "half"]
    explanation: "$\\alpha_3(|x|) \\ge 2\\sigma(|u|)$ 인 영역에서 $\\dot V \\le -\\alpha_3 + \\sigma \\le -\\tfrac12\\alpha_3$ 이다. 이 1/2 이 식 (5)이고, 일반적으로는 $\\theta \\in (0,1)$ 에 대해 $-(1-\\theta)\\alpha_3$ 로 바뀐다."
    concept: { front: "ISS 유도의 이득 여유(gain margin)", back: "$\\alpha_3 \\ge 2\\sigma$ 영역에서 $\\dot V \\le -\\tfrac12 \\alpha_3$ — 입력 항을 감소 항의 절반으로 흡수한다" }
  - id: q3
    type: truefalse
    prompt: "SOS 프로그램 (4)가 가해가 아니면 그 계는 해당 준위집합에서 불안정하다."
    answer: false
    explanation: "(4)는 충분조건일 뿐이다. 실패는 ⓐ 차수가 낮다 ⓑ 승수 구조가 부족하다 ⓒ 솔버가 수치적으로 실패했다 중 어느 것일 수도 있다. 비음이지만 SOS 가 아닌 다항식이 존재한다는 사실(Positivstellensatz 의 차수 간극)이 근본 이유다."
    concept: { front: "SOS 인증 실패의 뜻", back: "불안정의 증거가 아니다 — 차수·승수·수치 문제일 수 있다. SOS 는 비음성의 충분조건" }
  - id: q4
    type: single
    prompt: "$\\dot{x} = -x + x^2 u$ 가 ISS 가 아닌 이유는?"
    choices:
      - "$u \\equiv 0$ 에서도 불안정하기 때문"
      - "상수 입력 $u \\equiv \\mu$ 에 대해 $x_0 > 1/\\mu$ 이면 유한 시간에 발산하므로, 유계 입력에 유계 상태라는 결론이 깨지기 때문"
      - "$\\sigma$ 를 $\\mathcal{K}$ 로 잡을 수 없기 때문"
      - "$V = x^2/2$ 가 방사 비유계가 아니기 때문"
    answer: 1
    explanation: "$u \\equiv 0$ 에서는 GAS(0-GAS)다. 그러나 $u \\equiv \\mu$ 이면 $x = 1/\\mu$ 가 불안정 평형이고 그보다 큰 초기값은 발산한다. 즉 어떤 $\\gamma$ 로도 (3)을 만족시킬 수 없다. 입력을 작게 제한하면 국소 ISS 는 성립한다."
    concept: { front: "0-GAS 이지만 ISS 가 아닌 표준 예", back: "$\\dot x = -x + x^2u$ — 상수 $u=\\mu$ 에서 $x_0 > 1/\\mu$ 가 유한 시간 발산. 국소 ISS 는 성립" }
```

## 이 단계 공부법

1. **정의를 비교 함수로 다시 쓴다 (40분)** — "안정", "점근 안정", "지수 안정", "ISS" 를
   $\varepsilon$–$\delta$ 와 $\mathcal{KL}$ 양쪽으로 적어 보고 서로 옮긴다. 이 변환이 익숙해지면
   ISS 가 새 개념이 아니라 "$\mathcal{KL}$ 추정식에 입력 항을 더한 것" 으로 읽힌다.
   Khalil ch.4.4 의 비교 함수 절을 같이 본다.
2. **증명을 전략 한 줄로 압축한 뒤 복원한다 (90분)** — R1 은 "준위집합이 통", R2 는 "궤적을
   적분", R3 은 "$\omega$-극한집합에서 $V$ 는 상수". 세 줄을 외우고 백지에서 단계를 복원한다.
   막히면 그 단계만 Khalil Thm 4.1·4.14·4.4 에서 확인한다.
3. **반례를 손으로 만난다 (60분)** — (16)을 직접 적분해 $\dot V<0$ 인데도 $x_1$ 이 커지는 것을
   보고, (10)에서 $\mu$ 를 바꿔 가며 탈출 문턱 $1/\mu$ 를 찾는다. **반례를 본 사람만 가정을
   기억한다.**
4. **ISS 유도를 네 단계로 쪼개 쓴다 (60분)** — (5)→(6)→(8)→(9). 각 단계에서 어떤 가정을
   쓰는지 여백에 적는다. P1 을 풀면 $\theta$ 가 이득과 수렴률을 어떻게 맞바꾸는지 보인다.
5. **SOS 는 "조건부 부등식을 승수로 흡수" 하나만 기억한다 (90분)** — (11)의 한 줄이 전부다.
   그 다음 재현 과제에서 2차 $V$ 기준선을 먼저 **손으로** 재현하고(식 (14)의 닫힌 형태를 쓰면
   SDP 없이 된다), 그 뒤에 4차 SOS 로 넘어간다. 순서를 바꾸면 솔버 디버깅에 시간을 다 쓴다.
6. **논문은 "무엇을 보장하지 않는가" 로 읽는다 (150분)** — Sontag 1989 는 정의, Papachristodoulou
   2002 는 정식화, Topcu 2008 은 절차를 준다. 세 편 모두에서 고정 질문 4번(보장하지 않는 것)에
   한 문단씩 답을 쓴다. 논문당 1페이지 노트는 **반드시** 쓴다.
7. **열린 문제 하나를 고른다 (30분)** — 네 개 중 하나를 골라 "왜 아직 안 풀렸는가" 를 한 문단으로
   쓴다. 이 모듈의 마지막 레슨(CBF)에서 같은 질문이 안전 제약 쪽으로 다시 나온다.

**통과 기준**: 백지에서 R1·R3 의 증명 전략을 말할 수 있고, (3)의 $\gamma$ 를 유도할 수 있고,
0-GAS 이지만 ISS 가 아닌 예를 하나 만들 수 있고, 재현 과제의 네 조건을 만족하는 코드와
논문 3편의 노트를 갖고 있다.
