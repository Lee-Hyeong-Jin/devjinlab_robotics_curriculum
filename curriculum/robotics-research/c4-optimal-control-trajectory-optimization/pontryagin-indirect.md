---
id: c4-pontryagin-indirect
title: Pontryagin 최대 원리와 간접법
summary: >-
  최적 제어의 1차 필요조건(Pontryagin 최소 원리, PMP)을 바늘 변분(needle variation)과 분리
  초평면으로 세우고, 수반 방정식이 변분 방정식의 전치라는 사실·해밀토니안 보존·bang-bang 구조를
  직접 유도한다. 간접법(indirect method)의 조건수가 지평선 길이에 대해 지수적으로 폭발하는
  이유를 해밀토니안 흐름의 심플렉틱 구조에서 끌어내고, 브라키스토크론을 간접법으로 풀어 닫힌
  해와 $10^{-13}$ 수준까지 대조한다.
objectives:
  - 바늘 변분과 분리 초평면 논증으로 PMP 의 1차 필요조건을 재구성할 수 있다.
  - 수반 방정식이 변분 방정식의 전치임을 보이고 자율계에서 해밀토니안이 보존됨을 유도할 수 있다.
  - 제어가 아핀으로 들어갈 때 bang-bang 구조와 특이 호(singular arc)가 생기는 조건을 스위칭 함수로 판정할 수 있다.
  - 단일 슈팅의 야코비안이 $e^{\sigma T}$ 로 커지는 이유를 심플렉틱 고윳값 쌍에서 설명하고 수치로 확인할 수 있다.
  - 브라키스토크론을 간접법으로 풀고 닫힌 해(사이클로이드)와 수치적으로 대조할 수 있다.
prerequisites: []
difficulty: 4
estimated_minutes: 540
tags: [optimal-control, pontryagin, indirect-method, shooting, bang-bang, research]
activities:
  - id: c4-pontryagin-indirect-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 100
  - id: c4-pontryagin-indirect-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c4-pontryagin-indirect-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: c4-pontryagin-indirect-reproduction
    kind: reproduction
    title: 재현 과제 — 브라키스토크론 간접법과 슈팅 민감도 (R2)
    estimated_minutes: 95
  - id: c4-pontryagin-indirect-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Tedrake, Underactuated Robotics"
    url: https://underactuated.csail.mit.edu/trajopt.html
    kind: book
    note: ch.10 (Trajectory Optimization) — 10.1 간접법과 10.2 직접법의 대비. 전문 무료.
  - title: "Stanford AA203 Optimal and Learning-based Control"
    url: https://stanfordasl.github.io/aa203/
    kind: course
    note: W2–W3 가 변분법·PMP·간접법. 강의 노트와 과제가 공개되어 있다.
papers:
  - id: sussmann1997-300-years
    required: true
    role: seminal
    note: "§V"
  - id: hartl1995-pmp-state-constraints
    required: true
    role: survey
    note: "§2-§4"
  - id: betts1998-survey
    required: true
    role: survey
    note: "§3-§4"
  - id: kelly2017-trajopt-tutorial
    role: standard
  - id: fuller1963-optimum-nonlinear
    role: seminal
---

# Pontryagin 최대 원리와 간접법

## 전제와 기호

이 레슨은 C4 모듈의 첫 레슨이고, 이후 C4 의 모든 레슨(LQR·iLQR·직접법·MPC)이 여기서 세운
해밀토니안 표기와 수반 방정식을 쓴다. 권장 선수는 R0 모듈(볼록 최적화, 수치 최적화, 적분기)과
C1 모듈이지만 **잠겨 있지 않다** — 아래 자가 진단을 통과하면 바로 시작해도 된다.

이 레슨이 전제하는 것:

- 선형대수: 고윳값, 행렬 지수, 전치와 쌍대, 조건수.
- 해석: 미분방정식의 존재·유일성, 상태 전이 행렬(state-transition matrix), 음함수 정리.
- 최적화: 라그랑주 승수와 KKT, 분리 초평면 정리(separating hyperplane theorem).
- 측도론은 **요구하지 않는다** — 바늘 변분에서 "거의 모든 $t$"가 나오는 자리만 표시하고,
  기술적 세부는 원 논문으로 넘긴다.

표기 규약(C4 모듈 전체에 고정):

| 기호 | 뜻 |
|---|---|
| $x \in \mathbb{R}^n$ | 상태. 궤적은 $x(\cdot)$, 최적해는 $x^*(\cdot)$ |
| $u \in U \subseteq \mathbb{R}^m$ | 제어. $U$ 는 **닫힌** 허용 집합(볼록일 필요 없다) |
| $f(x, u, t) \in \mathbb{R}^n$ | 동역학 $\dot{x} = f(x, u, t)$ |
| $\ell(x, u, t) \in \mathbb{R}$ | 누적 비용(running cost), $\varphi(x, t)$ 는 종단 비용 |
| $\lambda(t) \in \mathbb{R}^n$ | 수반 변수(costate·adjoint). **열벡터**, $f$ 와 같은 차원 |
| $\lambda_0 \ge 0$ | 비용에 붙는 승수. $\lambda_0 = 1$ 로 정규화한 경우를 **정상(normal)**, $\lambda_0 = 0$ 을 **비정상(abnormal)** 이라 한다 |
| $H(x, u, \lambda, t)$ | 해밀토니안 $\lambda_0\,\ell(x,u,t) + \lambda^\top f(x,u,t)$ |
| $\psi(x, t) \in \mathbb{R}^q$ | 종단 제약 $\psi(x(t_f), t_f) = 0$ |
| $\Phi(t, s) \in \mathbb{R}^{n \times n}$ | 선형화 $\dot{\delta x} = f_x\,\delta x$ 의 상태 전이 행렬 |
| $z = (x, \lambda) \in \mathbb{R}^{2n}$ | 해밀토니안 계의 상태 |

**부호 규약**: 이 코스는 **최소 원리(minimum principle)** 를 쓴다 — 최적 제어가 $H$ 를
**최소화**한다. Pontryagin 의 원전은 $H$ 를 최대화하는 부호 규약이고, 두 규약은 $\lambda$ 의
부호로만 다르다. 논문을 읽을 때 첫 번째로 확인할 것이 이 부호다.

기준 문제(이 레슨 전체에서 $(\mathrm{P})$ 로 부른다):

$$
\min_{u(\cdot) \in U,\ t_f} \; J[u] = \int_0^{t_f} \ell(x, u, t)\,dt + \varphi(x(t_f), t_f)
  \quad \text{s.t.} \quad \dot{x} = f(x, u, t), \; x(0) = x_0, \; \psi(x(t_f), t_f) = 0. \tag{1}
$$

## 시작 전 자가 진단

이 모듈의 첫 레슨이므로 준비 상태를 먼저 점검한다. **선수 레슨은 잠겨 있지 않다** — 아래를 전부
풀 수 있으면 권장 선수를 건너뛰고 바로 시작해도 된다. **두 문항 이상 막히면** 괄호 안의 선수
레슨으로 돌아가는 편이 빠르다.

1. $\dot{\delta x} = A(t)\,\delta x$ 의 해를 상태 전이 행렬로 쓰고, $\Phi(t, s)$ 가 만족하는
   미분방정식과 $\Phi(t,t)$ 의 값을 말하라. (`r0-ad-and-integrators`)
   **정답**: $\delta x(t) = \Phi(t,s)\delta x(s)$, $\partial_t \Phi(t,s) = A(t)\Phi(t,s)$,
   $\Phi(t,t) = I$. 또한 $\partial_t \Phi(t,s)^{-1} = -\Phi(t,s)^{-1}A(t)$ 이므로 **전치**는
   $-A^\top$ 로 거꾸로 흐른다 — 이것이 수반 방정식의 정체다.
2. 제약 최적화 $\min_x c(x)$ s.t. $h(x) = 0$ 의 1차 필요조건(KKT)을 쓰라.
   라그랑주 승수가 "유일하게" 존재하려면 어떤 조건이 필요한가? (`r0-convex-optimization`)
   **정답**: $\nabla c + (\partial h/\partial x)^\top \nu = 0$, $h(x) = 0$. 승수의 존재·유일성은
   LICQ($\partial h/\partial x$ 가 행 풀랭크)에서 나온다. 랭크가 떨어지면 승수가 없거나
   무한히 많다 — PMP 의 $\lambda_0 = 0$ 비정상 경우가 이것의 대응물이다.
3. $A = \begin{bmatrix} 1 & -1 \\ -1 & -1\end{bmatrix}$ 의 고윳값과 $\lVert e^{At} \rVert_2$ 의
   $t \to \infty$ 거동을 말하라. (`r0-linear-algebra-decompositions`)
   **정답**: $\mu = \pm\sqrt{2}$ (허용오차 $10^{-9}$). 고윳값이 $\pm$ 쌍이므로 한 방향은
   $e^{\sqrt2 t}$ 로 폭발하고 다른 방향은 같은 비율로 감쇠한다. $\lVert e^{At}\rVert_2 \sim
   c\,e^{\sqrt2 t}$.
4. 볼록 집합 $K \subset \mathbb{R}^d$ 와 점 $p \notin K$ 에 대해 분리 초평면 정리를 쓰라.
   $K$ 가 **볼록이 아니면** 무엇이 깨지는가? (`r0-convex-optimization`)
   **정답**: $\exists\, a \ne 0$ 로 $a^\top p \le \inf_{y \in K} a^\top y$. 볼록이 아니면
   분리 초평면이 존재하지 않을 수 있다 — PMP 증명에서 "바늘 변분의 원뿔이 볼록하다"를
   따로 보여야 하는 이유다.
5. $\min_{t_f} t_f$ 처럼 종단 시각이 결정변수인 문제에서, $t_f$ 에 대한 1차 조건을 쓰면
   무엇이 되는가? 단순한 예 $\min_{T} \int_0^T 1\,dt$ s.t. $x(T) = 0$ 로 설명하라.
   (`f0-calculus-multivariable`)
   **정답**: 적분 상한에 대한 미분이므로 피적분함수의 종단값이 조건에 들어온다 —
   일반적으로 $H(t_f) + \partial\varphi/\partial t_f = 0$. 자율·종단비용 없는 최소 시간
   문제에서는 $H \equiv 0$ 이다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (Pontryagin 최소 원리) [D3]** — $(u^*, x^*, t_f^*)$ 가 $(\mathrm{P})$ 의 최적해면,
  $\lambda_0 \ge 0$ 과 절대연속 $\lambda : [0, t_f^*] \to \mathbb{R}^n$ 이 존재해
  $(\lambda_0, \lambda(t)) \ne 0$ ($\forall t$) 이고 다음이 성립한다.
  $$
  \dot{x}^* = \frac{\partial H}{\partial \lambda} = f, \qquad
    \dot{\lambda} = -\frac{\partial H}{\partial x}
    = -\lambda_0 \ell_x^\top - f_x^\top \lambda, \tag{2}
  $$
  $$
  u^*(t) \in \arg\min_{w \in U} H\big(x^*(t), w, \lambda(t), t\big)
    \quad \text{거의 모든 } t, \tag{3}
  $$
  $$
  \lambda(t_f) = \lambda_0 \varphi_x^\top + \psi_x^\top \nu \;\;(\exists \nu \in \mathbb{R}^q),
    \qquad H(t_f) + \lambda_0\frac{\partial \varphi}{\partial t_f} = 0 \;\;(t_f \text{ 자유}). \tag{4}
  $$
  **필요조건일 뿐이다** — (2)–(4)를 만족하는 궤적(**극단곡선**, extremal)은 최적이 아닐 수 있다.
- **R2 (수반 방정식의 정체와 해밀토니안 보존) [D2]** — (2)의 수반 방정식은 변분 방정식
  $\dot{\delta x} = f_x \delta x$ 의 **전치를 역시간으로 흐르게 한 것**이고, 따라서
  $\lambda(t)^\top \delta x(t)$ 는 (비용항이 없을 때) 보존량이다. 또한 $f$, $\ell$ 이 $t$ 를
  명시적으로 포함하지 않으면
  $$\frac{d}{dt}H\big(x^*(t), u^*(t), \lambda(t), t\big) = 0 \quad \text{거의 모든 } t, \tag{5}$$
  이고 $t_f$ 가 자유이며 $\varphi$ 가 $t_f$ 에 의존하지 않으면 $H \equiv 0$ 이다.
- **R3 (제어 아핀 문제의 bang-bang 구조와 특이 호) [D2]** — $f = f_0(x,t) + F(x,t)u$,
  $\ell = \ell_0(x,t)$, $U = \prod_i [a_i, b_i]$ 이면 $H$ 는 $u$ 에 아핀이고
  $$H = \lambda_0 \ell_0 + \lambda^\top f_0 + s(t)^\top u, \qquad s(t) := F(x^*,t)^\top \lambda(t), \tag{6}$$
  이므로 (3)은 성분별로 $u_i^* = a_i\,(s_i > 0)$, $u_i^* = b_i\,(s_i < 0)$ 로 풀린다.
  $s_i \equiv 0$ 인 구간에서는 1차 조건이 $u_i$ 를 **전혀 결정하지 않는다**(특이 호).
  이중 적분기 최소 시간 문제에서는 $s$ 가 $t$ 의 1차식이어서 스위칭이 **최대 1회**다.
- **R4 (단일 슈팅의 민감도 폭발) [D2]** — 간접법은 $\lambda(0)$ 를 미지수로 두고 종단 조건을
  근 찾기로 맞춘다. 그 슈팅 사상의 야코비안은 선형화된 해밀토니안 계의 상태 전이 행렬을 품고,
  그 계수 행렬은 **해밀토니안 행렬**이므로 고윳값이 $\pm\mu$ 쌍으로 온다. 쌍곡성($\sigma :=
  \max_i \operatorname{Re}\mu_i > 0$)이 있으면
  $$
  \left\lVert \frac{\partial S}{\partial p} \right\rVert \sim c\,e^{\sigma T}, \qquad
    \kappa\!\left(\frac{\partial S}{\partial p}\right) \sim e^{2\sigma T}. \tag{7}
  $$
  이고 배정밀도에서 잔차 $\mathrm{tol}$ 에 도달 가능한 지평선은
  $T \le \sigma^{-1}\ln\!\big(\mathrm{tol}/(c\,\varepsilon_{\mathrm{mach}})\big)$ 로 제한된다.
  **양방향 경계값 문제 자체는 멀쩡하다** — 망가지는 것은 초기값 문제로의 환원이다.
- **R5 (브라키스토크론의 PMP 해: 경로각이 시간의 1차식) [D2]** — 중력장에서 최소 시간 강하
  문제의 최적 경로각 $\theta(t)$ 는
  $$\dot{\theta} = -\frac{g\cos\theta}{v} = \text{const} =: -k, \qquad v(t) = \frac{g}{k}\cos\theta(t), \tag{8}$$
  를 만족하고, 따라서 $\theta(t) = \theta_0 - kt$ 는 $t$ 의 1차식이며 궤적은 사이클로이드다.
  수반 변수는 닫힌 형태로 $\lambda_x = -k/g$, $\lambda_y = -(k/g)\tan\theta_f$,
  $\lambda_v(t) = g^{-1}(\tan\theta_f\cos\theta - \sin\theta)$ 다. **[D2]**

## 유도

### R2 — 수반 방정식은 변분 방정식의 전치다

PMP 를 증명하기 전에 (2)가 어디서 오는지 먼저 본다. 이것이 R1 증명의 4·5단계를 읽는 열쇠다.

최적 궤적 $x^*$ 주변에서 제어를 $u^* + \delta u$ 로 흔들면 상태는 1차까지
$$\dot{\delta x} = f_x\,\delta x + f_u\,\delta u, \qquad \delta x(0) = 0 \tag{9}$$
을 따른다($f_x := \partial f/\partial x$ 를 $(x^*(t), u^*(t), t)$ 에서 평가). (9)의 해는
상태 전이 행렬로
$$\delta x(t) = \int_0^t \Phi(t, s)\,f_u(s)\,\delta u(s)\,ds. \tag{10}$$

비용의 1차 변화는 $\delta J = \int_0^{t_f}(\ell_x \delta x + \ell_u \delta u)\,dt
+ \varphi_x \delta x(t_f)$ 다. 여기에 (10)을 넣으면 $\delta x$ 가 **$\delta u$ 의 이중 적분**으로
들어와 다루기 어렵다. 적분 순서를 바꾸는 것이 핵심 단계다:

$$
\int_0^{t_f}\!\!\ell_x(t)\!\int_0^t \Phi(t,s) f_u(s)\delta u(s)\,ds\,dt
  = \int_0^{t_f}\!\!\left[\int_s^{t_f}\!\! \ell_x(t)\Phi(t,s)\,dt\right] f_u(s)\,\delta u(s)\,ds.
$$

그러니 $\lambda$ 를 **대괄호 안의 양의 전치**로 정의하면 모든 것이 한 번의 적분으로 정리된다:

$$
\lambda(s)^\top := \lambda_0\!\int_s^{t_f}\! \ell_x(t)\,\Phi(t,s)\,dt
  + \lambda_0 \varphi_x \Phi(t_f, s). \tag{11}
$$

(11)을 $s$ 로 미분한다. $\partial_s \Phi(t,s) = -\Phi(t,s) f_x(s)$ 이고(자가 진단 1번),
적분 하한에서 $\Phi(s,s) = I$ 가 나오므로

$$
\dot{\lambda}(s)^\top = -\lambda_0 \ell_x(s) - \lambda(s)^\top f_x(s)
  \;\;\Longleftrightarrow\;\; \dot{\lambda} = -\lambda_0 \ell_x^\top - f_x^\top \lambda
  = -\frac{\partial H}{\partial x}, \tag{12}
$$

즉 (2)다. 종단값은 (11)에 $s = t_f$ 를 넣으면 $\lambda(t_f) = \lambda_0 \varphi_x^\top$ —
(4)의 $\psi$ 가 없는 경우다. 그리고 비용 변화는

$$
\delta J = \int_0^{t_f}\Big(\lambda_0 \ell_u + \lambda^\top f_u\Big)\delta u\,dt
  = \int_0^{t_f} \frac{\partial H}{\partial u}\,\delta u\,dt. \tag{13}
$$

**읽는 법**: $\lambda$ 는 "비용의 상태에 대한 민감도를 종단에서 역시간으로 끌어온 것"이다.
$f_x$ 가 전치되어 역시간으로 흐르는 이유가 (11)의 적분 순서 교환에 전부 들어 있다.
이것은 역전파(reverse-mode AD)와 **같은 계산**이고, 그 대응이 `c4-ilqr-ddp` 의 역방향 패스다.

**가정이 깨지는 곳**: (13)은 $U = \mathbb{R}^m$ 처럼 $u$ 를 **양방향으로** 흔들 수 있을 때만
$\partial H/\partial u = 0$ 을 준다. $u^*$ 가 $U$ 의 경계에 있으면 허용되는 $\delta u$ 가
한쪽 방향뿐이라 결론은 $\partial H/\partial u \cdot \delta u \ge 0$ 이 되고, 더 나아가
$U$ 가 볼록이 아니면 1차 변분 자체가 쓸 수 없다. PMP 의 (3)이 미분이 아니라 **최소화**로
쓰인 이유가 바로 이것이다 — R1 의 증명은 (9)의 선형화를 포기하고 바늘 변분을 쓴다.

### R2(계속) — 해밀토니안 보존

$H^*(t) := \min_{w \in U} H(x^*(t), w, \lambda(t), t)$ 로 두자. 최솟값 함수이므로
Danskin 정리에 의해 $H^*$ 는 국소 리프시츠이고, 거의 모든 $t$ 에서

$$
\frac{dH^*}{dt} = \underbrace{H_x \dot{x}^* + H_\lambda \dot{\lambda}}_{\text{상태·수반}}
  + \frac{\partial H}{\partial t}\bigg|_{u = u^*}. \tag{14}
$$

(최솟값을 주는 $w$ 에 대한 미분항은 사라진다 — 포락선 정리. $u^*$ 가 뛰는 스위칭 시각에서는
$H$ 의 양쪽 값이 같으므로 $H^*$ 는 **연속**이고 (14)는 그 유한 집합 밖에서 성립한다.)

(2)를 (14)에 넣으면 상태·수반 항이 정확히 상쇄된다:

$$
H_x \dot{x}^* + H_\lambda \dot{\lambda}
  = H_x H_\lambda^\top + H_\lambda(-H_x^\top) = 0. \tag{15}
$$

따라서 $dH^*/dt = \partial H/\partial t = \lambda_0 \ell_t + \lambda^\top f_t$ 이고, $f$ 와
$\ell$ 이 $t$ 를 명시적으로 포함하지 않으면 $H^* \equiv \text{const}$ — (5)다. 여기에 $t_f$
자유 조건 (4)를 쓰면 그 상수는 0 이다.

**가정이 깨지는 곳**: (i) 비자율계. $\ell$ 이나 $f$ 에 $t$ 가 명시적으로 들어가면 $H$ 는
보존되지 않는다 — 수치해의 $\lvert H(t) - H(0)\rvert$ 를 수렴 진단에 쓰는 관행이 이때 거짓
경보를 낸다. (ii) 상태 제약 $g(x) \le 0$. 제약이 활성화되면 $\lambda$ 는 절대연속이 아니라
유계변동(BV) 함수가 되어 **점프**하고, $H$ 도 그 지점에서 뛸 수 있다(Hartl et al. 1995 §3).
(iii) $U$ 가 닫혀 있지 않으면 (3)의 최솟값이 존재하지 않아 $H^*$ 가 정의되지 않는다.

### R3 — bang-bang 과 특이 호

(6)은 $H$ 를 $u$ 에 대해 아핀으로 쓴 것이다. 아핀 함수를 상자 $\prod_i[a_i, b_i]$ 에서
최소화하면 각 성분은 계수의 부호만 보면 된다:

$$
u_i^*(t) = \begin{cases}
  a_i, & s_i(t) > 0, \\
  b_i, & s_i(t) < 0, \\
  \text{미결정}, & s_i(t) = 0.
\end{cases} \tag{16}
$$

$s(t) = F^\top\lambda$ 를 **스위칭 함수**라 한다. $s_i$ 의 영점이 고립되어 있으면 제어는
경계 사이를 튀는 bang-bang 이고, $s_i \equiv 0$ 인 구간이 있으면 그 구간이 특이 호다.

**이중 적분기 최소 시간 문제**로 구체화한다. $\dot{x}_1 = x_2$, $\dot{x}_2 = u$,
$\lvert u \rvert \le 1$, $\ell = 1$, $\varphi = 0$, 종단 $x(t_f) = 0$, $t_f$ 자유.

$$H = \lambda_0 + \lambda_1 x_2 + \lambda_2 u. \tag{17}$$

수반 방정식 (2)는 $\dot\lambda_1 = -\partial H/\partial x_1 = 0$,
$\dot\lambda_2 = -\partial H/\partial x_2 = -\lambda_1$ 이므로

$$\lambda_1(t) = c_1, \qquad \lambda_2(t) = c_2 - c_1 t. \tag{18}$$

$\lambda_2$ 는 $t$ 의 1차식이다. 1차식은 항등적으로 0 이거나 영점이 최대 1개다.

- $\lambda_2 \equiv 0$ 이면 $c_1 = c_2 = 0$ 이고 (18)에서 $\lambda \equiv 0$, 그러면 (17)로
  $H = \lambda_0$ 다. $t_f$ 가 자유라 $H \equiv 0$ 이므로 $\lambda_0 = 0$ 이 되어
  $(\lambda_0, \lambda) \ne 0$ 을 위반한다. **특이 호는 존재할 수 없다.**
- 따라서 $\lambda_2$ 의 영점은 최대 1개이고, (16)으로 $u^* = -\operatorname{sign}\lambda_2
  \in \{-1, +1\}$ 이며 스위칭은 **최대 1회**다.

$x(0) = (1, 0)$ 에서 원점까지의 해를 끝까지 쓴다. $x_1 > 0$ 이므로 먼저 감속해야 하니
$u = -1$ 로 시작한다고 두면 $x_2 = -t$, $x_1 = 1 - t^2/2$. 스위칭 시각 $t_s$ 이후 $u = +1$ 이고
원점에 닿으려면 $x_2(t_f) = 0$ 에서 $t_f - t_s = t_s$, 즉 $t_f = 2t_s$ 다. 또
$x_1(t_f) = 1 - t_s^2/2 - t_s\cdot t_s + t_s^2/2 = 1 - t_s^2 = 0$ 이므로

$$t_s = 1, \qquad t_f = 2, \qquad x(t_s) = (0.5,\, -1). \tag{19}$$

**가정이 깨지는 곳**: (i) **특이 호.** 같은 동역학에 비용 $\ell = x_1^2$ (최소 시간이 아니라
최소 제곱 편차)를 주면 $H$ 는 여전히 $u$ 에 아핀이지만 $\lambda_2$ 가 1차식이 아니고,
Fuller 1963 은 최적 제어가 유한 시간에 **무한히 많이** 스위칭함을 보였다(Fuller 현상).
스위칭 구조를 유한 개로 가정하는 모든 간접법이 이 문제에서 실패한다. (ii) **특이 호의 탐지.**
$s_i \equiv 0$ 일 때 $u$ 를 결정하려면 $\ddot{s}_i = 0$ 같은 고차 조건(Kelley 조건)을 써야
하고, 어떤 구간이 특이한지 **미리 알아내는 일반 알고리즘은 없다**(Betts 1998 §4). (iii) $H$ 가
$u$ 에 아핀이 아니면(예: $\ell$ 에 $u^\top R u$ 가 있으면) (16)은 성립하지 않고 최솟값이
내부에 생긴다 — 그쪽이 `c4-dp-lqr-lqg` 의 세계다.

### R4 — 단일 슈팅의 조건수는 $e^{\sigma T}$ 로 커진다

간접법(단일 슈팅)의 구조는 이렇다. (3)으로 $u$ 를 $(x, \lambda)$ 의 함수
$u^*(x,\lambda,t)$ 로 제거하면 (2)는 $z = (x, \lambda) \in \mathbb{R}^{2n}$ 에 대한
**닫힌 미분방정식**이 된다:

$$
\dot{z} = \mathcal{H}(z, t) := \begin{bmatrix} \partial H/\partial \lambda \\
  -\partial H/\partial x \end{bmatrix}_{u = u^*(x,\lambda,t)}
  = J\,\nabla_z H, \qquad J = \begin{bmatrix} 0 & I \\ -I & 0\end{bmatrix}. \tag{20}
$$

미지수는 $p := \lambda(0) \in \mathbb{R}^n$ (와 자유 $t_f$)이고, 조건은 종단 (4)다.
슈팅 사상을 $S(p) := r\big(z(T; p)\big)$ ($r$ 은 종단 잔차)로 쓰면

$$
\frac{\partial S}{\partial p} = \frac{\partial r}{\partial z}\,\Phi_{\mathcal H}(T, 0)
  \begin{bmatrix} 0 \\ I \end{bmatrix}, \qquad
  \dot{\Phi}_{\mathcal H} = \underbrace{J\,\nabla_z^2 H}_{=: \mathcal{A}(t)}\,\Phi_{\mathcal H}. \tag{21}
$$

$\mathcal{A} = J\,\nabla^2_z H$ 는 **해밀토니안 행렬**이다($\nabla^2_z H$ 가 대칭이므로
$(J\mathcal{S})^\top J + J (J \mathcal{S}) = 0$). 해밀토니안 행렬의 고윳값은
$\mu$ 가 고윳값이면 $-\mu$ 도 고윳값인 **$\pm$ 쌍**으로 온다. 따라서 상수계수인 경우
$\Phi_{\mathcal H}(T,0) = e^{\mathcal{A}T}$ 의 특잇값은 $e^{\sigma T}$ 와 $e^{-\sigma T}$ 로
갈라지고 ($\sigma = \max_i \operatorname{Re}\mu_i$), 조건수는 $e^{2\sigma T}$ 다 — (7)이다.

**스칼라 예로 상수까지 구한다.** $\dot{x} = ax + u$, $J = \tfrac12\int_0^T (qx^2 + u^2)dt$,
$x(0) = x_0$, 종단 자유($\varphi = 0$). 그러면 $H = \tfrac12(qx^2 + u^2) + \lambda(ax + u)$,
$\partial H/\partial u = u + \lambda = 0$ 에서 $u^* = -\lambda$, 그리고

$$
\begin{bmatrix}\dot{x} \\ \dot{\lambda}\end{bmatrix}
  = \underbrace{\begin{bmatrix} a & -1 \\ -q & -a\end{bmatrix}}_{=:\,M}
  \begin{bmatrix}x \\ \lambda\end{bmatrix}, \qquad
  \operatorname{tr} M = 0, \; \det M = -(a^2 + q). \tag{22}
$$

$\operatorname{tr} M = 0$ 이 바로 $\pm$ 쌍의 표현이다: $\mu^2 = a^2 + q$ 이므로
$\mu = \pm\sigma$, $\sigma = \sqrt{a^2+q}$. $e^{MT} = \cosh(\sigma T)I
+ \sigma^{-1}\sinh(\sigma T)M$ 이므로 종단 조건 $\lambda(T) = 0$ 의 잔차
$r(p) = \lambda(T) = (e^{MT})_{21}x_0 + (e^{MT})_{22}\,p$ 에 대해

$$
\frac{dr}{dp} = (e^{MT})_{22} = \cosh\sigma T - \frac{a}{\sigma}\sinh\sigma T
  \;\xrightarrow[T \to \infty]{}\; \underbrace{\frac{1}{2}\left(1 - \frac{a}{\sigma}\right)}_{=:\,c}
  e^{\sigma T}. \tag{23}
$$

$a = q = 1$ 이면 $\sigma = \sqrt2 = 1.4142135624$, $c = 0.1464466094$ 다.
$T = 10$ 에서 $dr/dp = 2.03 \times 10^{5}$, $T = 20$ 에서 $2.81\times10^{11}$ —
$p$ 를 배정밀도 상대오차 $\varepsilon_{\mathrm{mach}} = 2.22\times10^{-16}$ 로밖에 쓸 수 없으니
도달 가능한 최소 잔차는 $\lvert dr/dp\rvert\,\lvert p^*\rvert\,\varepsilon_{\mathrm{mach}}$ 이고,
이것이 $\mathrm{tol} = 10^{-6}$ 를 넘는 지점은

$$T^* = \frac{1}{\sigma}\ln\frac{\mathrm{tol}}{c\,\varepsilon_{\mathrm{mach}}} = 17.08 \tag{24}$$

이다(재현 과제에서 수치로 확인한다 — 실제 전환점은 $T = 17$ 이다). $T$ 가 두 배가 되면
요구 정밀도가 $e^{\sigma T}$ 배로 늘어나므로, **더 좋은 근 찾기 알고리즘으로는 고칠 수 없다.**

**왜 경계값 문제 자체는 멀쩡한가**: $e^{MT}$ 가 안정 부분공간과 불안정 부분공간으로 갈라지는
것은 사실이지만, 양방향 문제는 $x(0)$ 를 **불안정 방향에서 앞으로**, $\lambda(T)$ 를
**안정 방향에서 뒤로** 전파하면 되므로 해 연산자의 노름이 $O(1)$ 이다. 망가지는 것은
"모든 미지수를 $t=0$ 에 모아 전구간을 앞으로 적분한다"는 **환원 방식**이다. 그래서
다중 슈팅(multiple shooting)은 $N$ 구간으로 쪼개 $e^{\sigma T}$ 를 $e^{\sigma T/N}$ 로
바꾸고, collocation 은 $N \to$ 격자 수로 극한을 취한 것에 해당한다(`c4-direct-collocation-sqp`).

**가정이 깨지는 곳**: 폭발은 **쌍곡성**($\sigma > 0$)에 매여 있다. $a^2 + q < 0$ 이면
$\mu = \pm i\lvert\sigma\rvert$ 가 순허수이고 $e^{MT}$ 는 유계 진동이라 단일 슈팅의 조건수가
커지지 않는다. "간접법은 항상 터진다"는 말은 틀렸다 — 실제로 이 레슨의 재현 과제
(브라키스토크론, $t_f \approx 0.47\,\mathrm{s}$)는 단일 슈팅으로 잔차 $4\times10^{-16}$ 까지
간다. 지평선이 짧거나 비쌍곡이면 간접법은 **가장 정확한** 방법이다.

### R5 — 브라키스토크론을 PMP 로 끝까지 푼다

$y$ 를 **아래 방향**으로 양수로 잡고 경로각 $\theta$ 를 수평선 아래 각으로 둔다. 상태
$(x, y, v)$, 제어 $\theta \in \mathbb{R}$ (제약 없음), 중력 $g$:

$$
\dot{x} = v\cos\theta, \qquad \dot{y} = v\sin\theta, \qquad \dot{v} = g\sin\theta, \tag{25}
$$

$x(0) = y(0) = 0$, $v(0) = v_0 > 0$, 종단 $(x(t_f), y(t_f)) = (x_f, y_f)$, $v(t_f)$ 자유,
$t_f$ 최소화. 정상 경우 $\lambda_0 = 1$ 로 두면

$$H = 1 + \lambda_x v\cos\theta + \lambda_y v \sin\theta + \lambda_v g \sin\theta. \tag{26}$$

수반 방정식 (2):

$$
\dot\lambda_x = 0, \qquad \dot\lambda_y = 0, \qquad
  \dot\lambda_v = -(\lambda_x\cos\theta + \lambda_y\sin\theta) =: -A. \tag{27}
$$

$\theta$ 가 자유이므로 (3)은 $\partial H/\partial\theta = 0$:

$$
-\lambda_x v \sin\theta + \lambda_y v\cos\theta + \lambda_v g \cos\theta = 0
  \;\;\Longleftrightarrow\;\; vB = \lambda_v g \cos\theta, \tag{28}
$$

여기서 $B := \lambda_x\sin\theta - \lambda_y\cos\theta$ 다. $v(t_f)$ 가 자유이고 종단 비용이
없으므로 (4)에서 $\lambda_v(t_f) = 0$. $t_f$ 가 자유이고 자율계이므로 $H \equiv 0$.

**1단계 — $\lambda_x$ 를 구한다.** $H = 0$ 에 (28)의 $\lambda_v g = vB/\cos\theta$ 를 넣는다:

$$
0 = 1 + vA + \frac{vB}{\cos\theta}\sin\theta
  = 1 + v\left[\lambda_x\cos\theta + \lambda_y\sin\theta
  + (\lambda_x\sin\theta - \lambda_y\cos\theta)\tan\theta\right].
$$

대괄호를 정리한다. $\lambda_y$ 항은 $\lambda_y\sin\theta - \lambda_y\sin\theta = 0$ 으로
**지워지고**, $\lambda_x$ 항은 $\lambda_x(\cos^2\theta + \sin^2\theta)/\cos\theta
= \lambda_x/\cos\theta$ 로 모인다. 따라서

$$0 = 1 + \frac{v\lambda_x}{\cos\theta} \quad\Longrightarrow\quad \lambda_x = -\frac{\cos\theta}{v}. \tag{29}$$

$\lambda_x$ 는 (27)로 상수이므로 **$\cos\theta/v$ 가 궤적 전체에서 상수**다 — 이것이
브라키스토크론의 고전적 보존량(스넬 법칙 꼴)이다.

**2단계 — $\dot\theta$ 가 상수임을 보인다.** (29)를 미분하면

$$
0 = \frac{d}{dt}\frac{\cos\theta}{v}
  = \frac{-\dot\theta \sin\theta\, v - \cos\theta\,\dot{v}}{v^2}
  = \frac{-\dot\theta\sin\theta\,v - g\sin\theta\cos\theta}{v^2}
$$

($\dot v = g\sin\theta$ 를 썼다). $\sin\theta \ne 0$ 인 곳에서 $\sin\theta$ 로 나누면

$$\dot\theta = -\frac{g\cos\theta}{v}. \tag{30}$$

(29)에서 $\cos\theta/v = -\lambda_x$ 는 상수이므로, (30)의 우변은 그 상수의 $g$ 배다:

$$
\dot\theta = -\frac{g\cos\theta}{v} = g\lambda_x = \text{const} =: -k, \qquad
  k := -g\lambda_x > 0, \qquad v(t) = \frac{g}{k}\cos\theta(t), \tag{31}
$$

(마지막 등식은 (29)를 $v$ 에 대해 풀고 $\lambda_x = -k/g$ 를 넣은 것이다.)

즉 $\theta(t) = \theta_0 - kt$ 이고 $\lambda_x = -k/g$ — (8)이다. 초기 조건 $v(0) = v_0$ 는
$\cos\theta_0 = k v_0/g$ 로 $\theta_0$ 를 정한다.

**3단계 — $\lambda_y$ 와 $\lambda_v$.** (28)에 $v = (g/k)\cos\theta$ 를 넣으면
$\lambda_v = B/k$ 다. $\lambda_v(t_f) = 0$ 이므로 $B(t_f) = 0$, 즉
$\lambda_x \sin\theta_f = \lambda_y\cos\theta_f$ 에서

$$
\lambda_y = \lambda_x \tan\theta_f = -\frac{k}{g}\tan\theta_f, \qquad
  \lambda_v(t) = \frac{1}{g}\big(\tan\theta_f\cos\theta(t) - \sin\theta(t)\big). \tag{32}
$$

(27)의 $\dot\lambda_v = -A$ 가 (32)와 일치하는지 직접 확인하라 — 문제 P1 이다.

**4단계 — 궤적(사이클로이드).** (31)을 (25)에 넣어 적분한다. $\theta_t := \theta_0 - kt$ 로 쓰면

$$
x(t) = \frac{g}{k}\left[\frac{t}{2} + \frac{\sin 2\theta_0 - \sin 2\theta_t}{4k}\right],
  \qquad y(t) = \frac{g\,(\cos 2\theta_t - \cos 2\theta_0)}{4k^2}. \tag{33}
$$

$v_0 = 0$ 인 고전적 경우에는 $\theta_0 = \pi/2$ 이고 $\phi := 2kt$, $R := g/(4k^2)$ 로 바꾸면
(33)은 $x = R(\phi - \sin\phi)$, $y = R(1 - \cos\phi)$ — 사이클로이드다. 에너지 보존
$v^2 = v_0^2 + 2gy$ 도 (31)·(33)에서 직접 따라온다(문제 P2).

**가정이 깨지는 곳**: (i) 2단계는 $\sin\theta \ne 0$ 을 썼다. $\theta = 0$ (수평 운동)에서는
$\dot v = 0$ 이라 입자가 가속되지 않고, $v_0 = 0$ 이면 (30)의 우변이 $0/0$ 이 된다 —
고전적 브라키스토크론의 **시작점이 특이점**이고, 그래서 재현 과제는 $v_0 > 0$ 으로 특이점을
피한다. $v_0 = 0$ 에서는 $\theta_0 = \pi/2$ 가 PMP 로 강제되고 $k$ 가 급수 전개의 자유
계수로 남는다. (ii) $\lambda_x = 0$ 이면 (29)가 $1 = 0$ 이 되어 모순이므로 정상 경우에
$\lambda_x \ne 0$ 이 보장되지만, $x_f = 0$ (순수 수직 강하)처럼 문제가 퇴화하면 비정상
($\lambda_0 = 0$) 극단곡선이 들어온다. (iii) $y_f \le 0$ (목표가 출발점보다 위)이면
$v_0$ 만으로 도달 가능한지가 먼저 문제이고, 도달 불가능하면 극단곡선이 아예 없다.

## 증명 스케치

### R1 — Pontryagin 최소 원리 [D3]

**가설**
H1: $f$, $\ell$ 은 $x$ 에 대해 $C^1$, $u$ 에 대해 연속, $t$ 에 대해 가측이고 국소 유계.
H2: $U \subseteq \mathbb{R}^m$ 은 닫힌 집합(볼록·유계일 필요 없다).
H3: $u^*$ 는 $(\mathrm{P})$ 의 최적해이고, 대응하는 $x^*$ 가 $[0, t_f^*]$ 에서 존재한다.
H4: $\psi$ 는 $C^1$.

**결론** C: $(\lambda_0, \lambda) \ne 0$, $\lambda_0 \ge 0$ 가 존재해 (2)·(3)·(4)가 성립한다.

**전략**: 비용을 상태의 0번째 성분으로 올려 **도달 집합의 경계** 문제로 바꾼 뒤,
바늘 변분이 만드는 **볼록 원뿔**과 "비용을 줄이는 방향"을 분리 초평면으로 가른다.
그 분리 벡터를 흐름으로 뒤로 끌면 $\lambda$ 가 되고, 각 바늘에 대한 분리 부등식이 (3)이 된다.
핵심은 변분을 **크기가 작은** 것($\delta u$ 작음)이 아니라 **지속 시간이 짧은** 것(바늘)으로
잡는 것이다 — 그래야 $U$ 의 경계에서도 쓸 수 있다.

1. **비용을 상태로 올린다.** $x_c(t) := \int_0^t \ell\,ds$ 를 0번째 성분으로 붙여
   $\tilde{x} = (x_c, x) \in \mathbb{R}^{1+n}$, $\tilde{f} = (\ell, f)$ 로 둔다. $u^*$ 가 최적이면
   종단점 $\tilde{x}^*(t_f)$ 는 종단 제약을 만족하는 도달 집합
   $\mathcal{R} := \{\tilde{x}(t_f; u) : u(\cdot) \in \mathcal{U},\ \psi = 0\}$ 안에서
   $x_c$ 성분을 더 줄일 수 없다. 즉 $\tilde{x}^*(t_f)$ 는 $\mathcal{R}$ 의 **경계점**이다.
2. **바늘 변분.** $\tau \in (0, t_f)$, $w \in U$, 작은 $\varepsilon > 0$ 에 대해
   $u_\varepsilon := w$ on $[\tau, \tau+\varepsilon]$, $u^*$ 밖에서. 이 변분이 종단점에 주는
   변화는 $\varepsilon$ 의 1차까지
   $$
   \Delta\tilde{x}(t_f) = \varepsilon\,\tilde\Phi(t_f, \tau)
     \big[\tilde f(x^*(\tau), w, \tau) - \tilde f(x^*(\tau), u^*(\tau), \tau)\big] + o(\varepsilon),
   $$
   여기서 $\tilde\Phi$ 는 선형화 (9)의 상태 전이 행렬이다. $\tau$ 는 $u^*$ 의 **르베그 점**이어야
   한다(거의 모든 $\tau$ — 여기서 (3)의 "거의 모든 $t$"가 나온다).
3. **원뿔이 볼록하다.** 서로 다른 시각의 바늘을 **이어 붙이면** 1차 변화가 더해지고, 한 바늘의
   길이를 $\alpha\varepsilon$ 로 줄이면 변화가 $\alpha$ 배가 된다. 따라서 모든 1차 변화의 집합
   $$
   K := \operatorname{cone}\Big\{\tilde\Phi(t_f,\tau)\big[\tilde f(x^*(\tau), w, \tau)
     - \tilde f(x^*(\tau), u^*(\tau), \tau)\big] : \tau \in (0,t_f),\ w \in U \Big\}
   $$
   은 **볼록 원뿔**이다. (이 단계가 증명의 심장이다 — $U$ 의 볼록성 없이 $K$ 의 볼록성을
   얻는 곳이다. 자가 진단 4번이 왜 필요했는지가 여기다.)
4. **분리.** 1단계의 경계성은 "$K$ 가 $x_c$ 를 줄이면서 종단 제약의 접공간에 머무는 방향을
   포함하지 않는다"는 뜻이다. 따라서 $K$ 와 그 금지 방향의 볼록 집합을 분리하는
   $0 \ne (\lambda_0, -\lambda_f) \in \mathbb{R}^{1+n}$ 가 존재한다. $x_c$ 방향의 부호에서
   $\lambda_0 \ge 0$ 이 나온다. 종단 제약의 접공간에 대한 직교성이 (4)의
   $\lambda(t_f) = \lambda_0\varphi_x^\top + \psi_x^\top\nu$ 다.
5. **분리 벡터를 뒤로 끈다.** $\lambda(t)^\top := -(\lambda_0, -\lambda_f)$ 의 상태 부분을
   $\tilde\Phi(t_f, t)$ 로 당긴 것으로 정의하면, $\partial_t\tilde\Phi(t_f,t)
   = -\tilde\Phi(t_f,t)\tilde f_x(t)$ 이므로 $\lambda$ 는 정확히 (2)의 수반 방정식을 만족한다
   (R2 의 유도 (11)–(12)와 같은 계산이다). 이제 3단계의 각 생성원에 분리 부등식을 적용하면
   거의 모든 $\tau$ 와 모든 $w \in U$ 에 대해
   $$
   \lambda_0\ell(x^*,w,\tau) + \lambda(\tau)^\top f(x^*,w,\tau)
     \;\ge\; \lambda_0\ell(x^*,u^*,\tau) + \lambda(\tau)^\top f(x^*,u^*,\tau),
   $$
   즉 $H(x^*, w, \lambda, \tau) \ge H(x^*, u^*, \lambda, \tau)$ — (3)이다.
6. **$t_f$ 자유.** $t_f$ 를 $t_f \pm \varepsilon$ 로 흔드는 변분을 추가하면 $\pm$ 양쪽이
   허용되므로 등식 조건 $H(t_f) + \lambda_0\partial_{t_f}\varphi = 0$ 이 나온다.

(생략: $\mathcal{R}$ 의 1차 근사가 실제로 $K$ 로 주어진다는 보조정리 — 축소 사상/
Brouwer 고정점이 필요하다. 원전은 Pontryagin et al. 1962 의 변분 원뿔 보조정리이고,
현대적 진술은 [Sussmann & Willems 1997](https://doi.org/10.1109/37.588098) §V 다.
가측 제어에 대한 절대연속성 논증도 생략했다.)

**가설을 지우면 어디서 무너지는가**

- **H1 ($C^1$) 을 지우면**: 2단계의 $\tilde\Phi$ 가 존재하지 않는다. 강체 접촉처럼 $f$ 가
  $x$ 에 대해 불연속이면 수반 변수가 모드 전환면에서 **점프**하고, 그 점프를 기술하는 것이
  살토(saltation) 행렬이다(`c4-contact-implicit-hybrid`). 매끄러운 PMP 를 그대로 적용하면
  틀린 기울기를 얻는다.
- **상태 제약이 없다는 가정을 지우면**: $g(x) \le 0$ 이 활성화되는 구간에서 1단계의 도달 집합이
  제약면에 눌리고, 분리 벡터가 그 면 위의 **측도**를 품는다. $\lambda$ 는 절대연속이 아니라
  BV 가 되고 (2)는 $d\lambda = -H_x dt + g_x^\top d\eta$ 로 바뀐다(Hartl et al. 1995 §3).
- **$\lambda_0 > 0$ 을 기대하면**: 4단계의 분리 벡터는 $\lambda_0 = 0$ 일 수 있다(비정상 경우).
  그러면 (3)에 $\ell$ 이 들어가지 않아 **비용과 무관한** 조건이 되고 PMP 는 공허해진다.
  종단점이 도달 집합의 경계에 겨우 걸려 있을 때(제어 가능성이 간신히 성립할 때) 일어난다.
- **필요조건을 충분조건으로 읽으면**: 1단계는 "경계점"만 썼고 전역 최소성을 쓰지 않았다.
  따라서 극단곡선은 국소 최소·국소 최대·안장 어느 것도 될 수 있다. 충분성은 별도 조건
  (Jacobi 조건, 혹은 HJB 방정식의 해 존재)이 필요하다 — `c4-dp-lqr-lqg` 의 주제다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★, R5)** (32)의 $\lambda_v(t) = g^{-1}(\tan\theta_f\cos\theta - \sin\theta)$ 가
수반 방정식 $\dot\lambda_v = -(\lambda_x\cos\theta + \lambda_y\sin\theta)$ 를 만족함을
직접 미분해 확인하라. $\dot\theta = -k$, $\lambda_x = -k/g$, $\lambda_y = -(k/g)\tan\theta_f$ 다.
*해답 스케치*: 좌변은 $g^{-1}\dot\theta(-\tan\theta_f\sin\theta - \cos\theta)
= (k/g)(\tan\theta_f\sin\theta + \cos\theta)$. 우변도 같은 식이 되는지 $\lambda_x, \lambda_y$ 를
대입해 맞춰 본다. 두 식이 **모든 $\theta$ 에 대해** 같아야 한다는 점이 중요하다.

**P2 (유도, ★★, R5)** (33)을 (31)과 (25)에서 끝까지 적분해 유도하고, 에너지 보존
$v(t)^2 = v_0^2 + 2g\,y(t)$ 가 (31)·(33)에서 따라오는지 보여라. 그 다음 $v_0 \to 0$ 극한에서
$\theta_0 \to \pi/2$ 이고 (33)이 사이클로이드 $x = R(\phi-\sin\phi)$, $y = R(1-\cos\phi)$
($\phi = 2kt$, $R = g/4k^2$)로 바뀌는 것을 확인하라.
*해답 스케치*: $\int\cos^2\theta_t\,dt$ 는 반각 공식으로, $\int\cos\theta_t\sin\theta_t\,dt$ 는
$\tfrac12\int\sin 2\theta_t\,dt$ 로. 에너지는 $v = (g/k)\cos\theta$ 를 제곱하고 (33)의 $y$ 를
$\cos 2\theta = 2\cos^2\theta - 1$ 로 풀어 $\cos^2\theta_0$ 항이 상쇄되는 것을 본다.

**P3 (증명, ★★★, R3)** 이중 적분기에서 "스위칭 최대 1회"를 일반화하라. $\dot{x} = Ax + bu$,
$\lvert u\rvert \le 1$, 최소 시간, $A \in \mathbb{R}^{n\times n}$ 의 고윳값이 **모두 실수**일 때
스위칭 횟수가 최대 $n-1$ 임을 보여라. $A$ 가 복소 고윳값을 가지면 이 상한이 왜 깨지는가?
*해답 스케치*: 전략은 "스위칭 함수의 영점 개수 = 실지수함수 결합의 영점 개수"로 바꾸는 것이다.
$s(t) = b^\top\lambda(t) = b^\top e^{-A^\top t}\lambda(t_f)$ 는 $\sum_j p_j(t)e^{-\mu_j t}$
($p_j$ 는 다항식, $\sum(\deg p_j + 1) \le n$) 꼴이다. 핵심 부등식은 **Descartes 규칙의
해석적 버전**: 그런 실지수 다항식의 실영점 수는 $n-1$ 개를 넘지 못한다(귀납법 + Rolle 정리로,
$e^{\mu_1 t}$ 를 나눠 내고 미분하면 항의 수가 하나 줄어든다). 복소 고윳값이면 $s$ 에
$\sin, \cos$ 이 들어와 영점이 무한히 많을 수 있다 — 조화 진동자의 최소 시간 제어가 그 예다.

**P4 (계산, ★, R3)** 이중 적분기 $\dot x_1 = x_2$, $\dot x_2 = u$, $\lvert u\rvert \le 1$ 에서
$x(0) = (-2, -1)$ 을 원점으로 보내는 최소 시간 제어의 스위칭 시각 $t_s$, 스위칭 지점, 종단
시각 $t_f$ 를 구하라. 그 다음 같은 절차를 $x(0) = (1, 0)$ 에 적용해 (19)와 맞는지 확인하라.
*정답*: 스위칭 곡선은 $x_1 = -\tfrac12 x_2\lvert x_2\rvert$ 다. $(-2,-1)$ 은 이 곡선의
왼쪽이다($x_2 = -1$ 에서 곡선은 $x_1 = 0.5$ 인데 우리는 $x_1 = -2$). 따라서 $u = +1$ 로
시작한다. $x_1(t) = -2 - t + t^2/2$, $x_2(t) = -1 + t$ 를 곡선의 아래쪽 분지
$x_1 = -x_2^2/2$ 에 대입하면 $t^2 - 2t - \tfrac32 = 0$ 이고
$$
t_s = 1 + \tfrac12\sqrt{10} = 2.5811388301, \quad
  x(t_s) = \big(-1.25,\ \tfrac12\sqrt{10}\big), \quad
  t_f = 1 + \sqrt{10} = 4.1622776602
$$
(허용오차 $10^{-9}$). $x(0) = (1,0)$ 에서는 $t_s = 1$, $t_f = 2$, $x(t_s) = (0.5, -1)$ 이다.
*검산*: 스위칭 지점이 곡선 위에 있는지($\lvert x_1 + \tfrac12 x_2\lvert x_2\rvert\rvert
< 10^{-12}$), 그리고 두 구간을 해석적으로 이어 붙인 종단값이 $\lVert x(t_f)\rVert_\infty
< 10^{-12}$ 인지 확인한다. $u = \pm 1$ 구간은 2차 다항식이므로 수치 적분이 필요 없다.

**P5 (구현, ★★, R4)** (22)의 스칼라 LQ 문제에 단일 슈팅을 구현하고 $T = 1, 2, \dots, 25$ 에서
① $dr/dp$ 를 중심 유한차분으로 측정 ② 뉴턴법으로 도달한 최종 $\lvert r\rvert$ 를 기록하라.
$\log\lvert dr/dp\rvert$ 를 $T$ 에 대해 그려 기울기가 $\sigma$ 이고 절편이 $\ln c$ 인지 확인하라.
*루브릭*: ⓐ 측정한 기울기가 $\sqrt2$ 와 1% 이내로 맞는다 ⓑ 절편의 $e^{\text{절편}}$ 이
$0.1464466$ 과 1% 이내로 맞는다 ⓒ $\lvert r\rvert < 10^{-6}$ 에 도달하지 못하는 첫 $T$ 를
보고하고 (24)의 예측값 17.08 과 비교한다 ⓓ 적분기 허용오차를 $10^{-12}$ 보다 느슨하게
두면 폭발이 적분 오차에 가려지는 것을 확인하고 그 사실을 적는다.

**P6 (반례, ★★, R1)** "PMP 를 만족하면 최적이다"가 틀렸음을 **두 가지 서로 다른 방식**으로
보여라: (i) 극단곡선이 여러 개이고 그중 하나만 최적인 구체적 문제, (ii) $\lambda_0 = 0$ 인
비정상 극단곡선이 있어 (3)이 비용에 대해 아무 정보도 주지 않는 문제.
*성질 체크리스트*: (i) 은 종단 제약이 있고 도달 경로가 여러 개인 문제가 가장 쉽다(예:
단위원 위를 도는 계에서 목표점에 시계·반시계 두 방향으로 갈 수 있는 경우) — 두 극단곡선의
$J$ 를 직접 비교할 수 있어야 한다. (ii) 는 종단점이 도달 집합의 경계에 **정확히** 걸린 문제를
만든다(예: $\dot x = u$, $\lvert u\rvert \le 1$, $T = 1$ 고정, 종단 $x(1) = 1$, $x(0)=0$ —
제어가 유일하게 결정되므로 비용 $\ell$ 을 무엇으로 바꿔도 해가 같다). 체크할 성질:
$(\lambda_0, \lambda) \ne 0$ 은 여전히 성립하는가, $\lambda_0$ 을 1로 정규화할 수 있는가.

**P7 (논문, ★★, R2·R4)** Betts 1998 의 §3–§4 를 읽고, 저자가 간접법의 실무적 약점으로 드는
것을 **4개** 뽑아 각각이 이 레슨의 어느 결과와 대응하는지 쓰라(R2 의 보존량 진단, R3 의 특이
호 탐지, R4 의 조건수, 그리고 하나는 이 레슨이 다루지 않은 것이어야 한다). 그 다음 Hartl et
al. 1995 §3 에서 상태 제약이 들어왔을 때 (2)가 어떻게 바뀌는지 식 하나로 쓰라.
*루브릭*: 네 약점이 "스위칭 구조를 미리 알아야 한다 / 수반 변수의 초기 추정이 물리적 의미가
없어 추측이 어렵다 / 조건수 폭발 / 제약이 바뀌면 유도를 다시 해야 한다" 범주를 덮으면 통과.
"구현이 어렵다" 같은 서술만 있으면 미달. 상태 제약 쪽은 $\lambda$ 가 BV 가 되고 측도항
$g_x^\top d\eta$ 가 붙는다는 점을 짚으면 통과.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Sussmann & Willems, "300 years of optimal control: from the brachystochrone to the
   maximum principle" (1997, IEEE Control Systems Magazine)** — 역할: `표준(standard)`.
   <https://doi.org/10.1109/37.588098>
   읽을 곳: 전체(14페이지). §V 가 PMP 의 현대적 진술이고, §II–§IV 는 이 레슨의 R5 를
   역사적 순서로 다시 걷는다.
   추가 질문: ⓐ 저자들이 "변분법으로는 안 되고 PMP 가 필요하다"고 말하는 지점은 정확히
   어디인가(어떤 가정이 깨지는가)? ⓑ 이 글의 부호 규약은 최대 원리인가 최소 원리인가, 이
   레슨의 (26)과 맞추려면 무엇을 바꿔야 하는가? ⓒ 저자들이 브라키스토크론에서 PMP 가 주는
   추가 정보(변분법이 못 주는 것)로 드는 것은 무엇인가?
2. **Hartl, Sethi & Vickson, "A survey of the maximum principles for optimal control problems
   with state constraints" (1995, SIAM Review)** — 역할: `서베이(survey)`.
   <https://doi.org/10.1137/1037043>
   읽을 곳: §2(문제 설정과 제약 분류), §3(직접 수반 방정식 vs 간접 수반 방정식), §4(예).
   추가 질문: ⓐ "직접(direct)"과 "간접(indirect)" 수반 형식이 같은 문제에 서로 다른 $\lambda$
   를 주는데, 두 형식을 잇는 변환은 무엇인가? ⓑ 제약 차수(constraint order)가 높아지면
   무엇이 더 어려워지는가? ⓒ 이 레슨의 R2(해밀토니안 보존)는 상태 제약이 있으면 어떤 형태로
   살아남는가?
3. **Betts, "Survey of numerical methods for trajectory optimization" (1998, AIAA JGCD)** —
   역할: `서베이(survey)`. <https://doi.org/10.2514/2.4231>
   읽을 곳: §2(문제 종류), §3(간접법: 슈팅·다중 슈팅), §4(직접법), §6(비교와 권고).
   추가 질문: ⓐ 저자가 다중 슈팅을 권하는 이유를 이 레슨의 (7)로 정량화하면? ⓑ 1998년의
   권고 중 2026년 기준으로 바뀐 것은 무엇인가(자동 미분, 내부점 해법, GPU)?
   ⓒ 저자가 보고하는 "간접법이 더 정확하다"는 주장은 어떤 조건에서 참인가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히
무엇인가 (3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지
않는가** (5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과
맞는가, 분산·시드를 보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저
의심할 가정 (9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, 전체 2분 이내, 메모리 200 MB
이하. numpy + scipy 만(`solve_ivp`, `fsolve`/`root`). 시뮬레이터는 쓰지 않는다.

**입력 데이터**: 없다. 두 문제 모두 레슨이 상수로 지정한다.
- 문제 A(브라키스토크론): $g = 9.81\,\mathrm{m/s^2}$, $v_0 = 1.0\,\mathrm{m/s}$,
  $(x_f, y_f) = (1.0,\ 0.5)\,\mathrm{m}$.
- 문제 B(스칼라 LQ): (22)에서 $a = 1$, $q = 1$, $x_0 = 1$, $T \in \{1,\dots,30\}$.

**과제**: ① 문제 A 를 (33)의 닫힌 해로 풀고 ② 같은 문제를 (20)의 해밀토니안 계에 대한
단일 슈팅(미지수 $p = (\lambda_x, \lambda_y, \lambda_v(0), t_f) \in \mathbb{R}^4$, 잔차
$r = (x(t_f) - x_f,\ y(t_f) - y_f,\ \lambda_v(t_f),\ H(t_f))$)으로 풀어 ①과 대조하고
③ 문제 B 로 (7)·(24)의 조건수 폭발을 측정하고 ④ 다중 슈팅으로 그것이 사라지는 것을 보인다.

**수용 기준** — 네 조건을 **모두** 만족해야 통과다.

1. **닫힌 해의 값.** (33)을 $(k, t_f)$ 에 대해 풀면
   $$
   k = 2.9625143878\ \mathrm{s^{-1}}, \quad t_f = 0.4669260667\ \mathrm{s}, \quad
     \theta_0 = 1.2640177030, \quad \theta_f = -0.1192574876\ \mathrm{rad}
   $$
   이다(상대오차 $10^{-8}$ 이내). 검산: $v(t_f) = 3.2878564446\,\mathrm{m/s}$ 가
   $\sqrt{v_0^2 + 2gy_f} = \sqrt{10.81}$ 과 $10^{-9}$ 이내로 일치해야 한다.
2. **슈팅이 닫힌 해를 복원한다.** 적분기 허용오차 `rtol=1e-12, atol=1e-14` 로
   $\lVert r(p^*)\rVert_\infty < 10^{-12}$ 에 도달하고, 그 $p^*$ 가 닫힌 해의
   $$
   \lambda_x = -0.3019892342, \quad \lambda_y = 0.0361861911, \quad
     \lambda_v(0) = -0.1008662107, \quad t_f = 0.4669260667
   $$
   과 $\lVert\cdot\rVert_\infty < 10^{-10}$ 이내로 일치한다.
3. **보존량과 제어 구조.** $[0, t_f]$ 의 균등 격자 1001점에서
   ⓐ $\max_t \lvert H(t)\rvert < 10^{-10}$ (R2 의 $H \equiv 0$),
   ⓑ $\theta(t)$ 에 최소제곱 직선을 맞춘 잔차 $\max_t\lvert\theta(t) - (\theta_0 - kt)\rvert
   < 10^{-9}$ 이고 기울기가 $-k$ 와 $10^{-8}$ 이내로 일치(R5 의 "1차식"),
   ⓒ $\max_t \lvert \cos\theta(t)/v(t) - \lvert\lambda_x\rvert \rvert < 10^{-10}$
   ((29)의 보존량).
4. **조건수 폭발과 다중 슈팅.** 문제 B 에서
   ⓐ $T = 5,\dots,20$ 의 $\log\lvert dr/dp\rvert$ 에 맞춘 직선의 기울기가 $\sqrt2$ 와,
   $e^{\text{절편}}$ 이 $0.1464466$ 과 각각 **상대오차 1% 이내**,
   ⓑ 단일 슈팅으로 $\lvert r\rvert < 10^{-6}$ 에 도달하지 못하는 첫 $T$ 가 $17 \pm 2$
   (예측 (24)는 17.08),
   ⓒ 구간 길이 $\Delta = 2$ 의 다중 슈팅($N = \lceil T/\Delta\rceil$)에서 구간별 전이 행렬의
   2-노름이 $T$ 에 **무관하게** $e^{2\sqrt2} = 16.9188$ 과 $10^{-4}$ 이내로 일치하고,
   $T = 100$ 까지 $\lVert r \rVert_\infty < 10^{-8}$ 에 도달한다.

**비교 대상**: ① 문제 A 의 닫힌 해 (33) 이 1차 베이스라인이다. ② 추가로
`scipy.integrate.solve_bvp` 로 같은 경계값 문제를 풀어 $t_f$ 가 $10^{-7}$ 이내로 일치하는지
본다(시간 재매개화가 필요하다 — $\tau = t/t_f$ 로 바꾸고 $t_f$ 를 매개변수로 올린다).
③ 문제 B 의 정답은 Riccati 해로 닫혀 있다: $T \to \infty$ 에서
$p^* \to (a + \sigma)x_0 = 2.4142135624$, 폐루프 극점은 $a - (a+\sigma) = -\sigma$ 다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 슈팅이 $t_f < 0$ 이나 $\theta$ 가 $\pi$ 를 넘는 해로 간다 | (3)의 최솟값이 아니라 **최댓값** 분기를 골랐다 — $\arctan$ 의 분지 | $\theta$ 를 $\operatorname{atan2}$ 로 뽑고 $\partial^2 H/\partial\theta^2 > 0$ 를 매 스텝 확인한다 |
| 잔차가 $10^{-6}$ 에서 멈추고 더 줄지 않는다 | 적분기 허용오차가 잔차 요구보다 느슨하다 | `rtol` 을 $10^{-10} \to 10^{-12}$ 로 조이며 잔차가 따라 내려가는지 본다 |
| $H$ 가 0 이 아니라 상수 $\ne 0$ 으로 보존된다 | $t_f$ 자유 조건 (4)를 잔차에 넣지 않았다 | $r$ 의 네 번째 성분이 $H(t_f)$ 인지 확인한다 |
| $\lambda_v(t_f) = 0$ 을 빼고 미지수를 3개로 줄였는데 해가 1-매개변수 족으로 나온다 | $v(t_f)$ 가 자유라는 종단 조건을 누락 — $\lambda_y$ 가 결정되지 않는다 | 서로 다른 초기 추정 두 개로 수렴한 $\lambda_y$ 가 다른지 본다((32) 앞 문단) |
| 문제 B 에서 $T$ 가 커져도 조건수가 안 커진다 | $q < -a^2$ 로 잡아 $\mu$ 가 순허수(비쌍곡) | $\sigma = \sqrt{a^2+q}$ 가 실수인지 먼저 출력한다 |
| 유한차분 $dr/dp$ 가 큰 $T$ 에서 들쭉날쭉하다 | $e^{\sigma T}$ 가 커져 차분의 반올림 오차가 지배 | 스텝을 $h \sim \varepsilon^{1/3}$ 로 두고, 해석해 (23)과 비교한다 |

## 열린 문제

- **(열린 문제) 접촉이 있는 계의 수반 변수는 무엇인가** — H1 이 깨지는 곳이다. 모드 전환이
  **미리 주어지면** 살토 행렬로 수반 변수의 점프를 쓸 수 있지만, 모드 순서가 결정변수일 때
  PMP 를 쓰는 일반적·수치적으로 안정한 방법이 없다. 현재 접근:
  [Sussmann 1999 의 하이브리드 최대 원리](https://doi.org/10.1109/cdc.1999.832814),
  [Posa et al. 2014 의 상보성 전사](https://doi.org/10.1177/0278364913506757).
  비어 있는 자리: 모드 수가 조합적으로 늘어날 때의 복잡도 하한, 그리고 비매끄러운 지점에서
  자동 미분이 주는 기울기가 언제 올바른 수반 변수인지에 대한 판정 조건.
- **(열린 문제) 극단곡선의 전역 최적성 인증** — PMP 는 필요조건뿐이고, 비선형 문제에서
  "이 극단곡선이 전역 최적이다"를 증명하는 일반적 방법이 없다. 현재 접근: 값 함수의
  하한을 다항식 최적화로 만드는 [Henrion & Korda 2014](https://doi.org/10.1109/TAC.2013.2283095)
  류의 모멘트/SOS 완화와 [HJ 도달가능성](https://doi.org/10.1109/CDC.2017.8263977).
  비어 있는 자리: 두 접근 모두 상태 차원에 지수적이라 $n \gtrsim 6$ 의 로봇에 쓸 수 없고,
  로봇 규모에서 실용적인 **간극(gap) 인증**이 없다.
- **(열린 문제) 특이 호의 자동 탐지** — $s_i \equiv 0$ 인 구간이 어디인지 미리 아는 알고리즘이
  없어서, 간접법은 사람이 스위칭 구조를 가정해야 한다. Fuller 현상처럼 유한 구조가 아예
  없는 경우도 있다([Fuller 1963](https://doi.org/10.1080/00207216308937555)).
  현재 접근: 고차(Kelley·Goh) 조건의 수치적 검사와 [Betts 1998](https://doi.org/10.2514/2.4231)
  §4 의 경험적 절차. 비어 있는 자리: 특이 구간의 개수·위치를 **푸는 문제의 일부로** 다루는
  전사(transcription) 형식.
- **(열린 문제) 수반 변수의 초기 추정을 학습으로 줄 수 있는가** — 간접법의 실무적 장벽은
  (7)의 조건수와 "$\lambda(0)$ 에 물리적 직관이 없다"는 점이다. 값 함수의 기울기가 곧
  $\lambda$ 이므로($\lambda = \partial V/\partial x$, `c4-dp-lqr-lqg`), 근사 값 함수를 학습해
  $\lambda(0)$ 를 예측하는 길이 열려 있다. 비어 있는 자리: 학습한 $\lambda(0)$ 가 뉴턴법의
  수렴 영역 안에 들어간다는 **보증**이 없고, 그 영역의 크기 자체가 (7)에 따라
  $e^{-\sigma T}$ 로 줄어든다.

## 개념 점검

`rc quiz c4-pontryagin-indirect` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c4-pontryagin-indirect-quiz
questions:
  - id: q1
    type: single
    prompt: "PMP 의 (3)이 $\\partial H/\\partial u = 0$ 이 아니라 '$U$ 위에서의 최소화'로 쓰이는 이유는?"
    choices:
      - "$H$ 가 $u$ 에 대해 미분 불가능할 수 있기 때문"
      - "$u^*$ 가 $U$ 의 경계에 있을 수 있고, 그러면 한쪽 방향 변분만 허용되기 때문"
      - "$\\lambda$ 의 부호 규약이 최소 원리이기 때문"
      - "해밀토니안이 보존되기 때문"
    answer: 1
    explanation: "증명이 작은 $\\delta u$ 가 아니라 짧은 바늘 변분을 쓰는 이유가 이것이다. $u^*$ 가 경계에 있으면 $\\partial H/\\partial u \\cdot \\delta u \\ge 0$ 까지만 얻고, $U$ 가 볼록이 아니면 1차 변분 자체가 쓸 수 없다. 최소화 형태는 $U$ 의 모양에 무관하게 성립한다."
    concept: { front: "PMP 의 최소화 조건이 미분 조건보다 강한 이유", back: "$u^*$ 가 $U$ 의 경계에 있을 때(그리고 $U$ 가 볼록이 아닐 때) 양방향 변분이 불가능하다 — 바늘 변분은 $U$ 의 모양을 쓰지 않는다" }
  - id: q2
    type: short
    prompt: "자율계이고 종단 비용이 $t_f$ 에 의존하지 않으며 $t_f$ 가 자유일 때, 최적 궤적 위에서 해밀토니안 $H$ 의 값은?"
    answer: ["0", "zero", "영", "H=0", "H = 0", "0이다"]
    explanation: "자율성에서 $dH/dt = \\partial H/\\partial t = 0$ 이므로 $H$ 는 상수이고, $t_f$ 자유 조건 $H(t_f) + \\lambda_0\\,\\partial\\varphi/\\partial t_f = 0$ 에서 그 상수가 0 이다. 수치해의 $\\max_t|H(t)|$ 는 그래서 간접법의 1순위 수렴 진단이 된다 — 단, 비자율계에서는 이 진단이 거짓 경보를 낸다."
    concept: { front: "자율 + 자유 종단시각에서 $H$ 의 값", back: "$H \\equiv 0$. 자율성이 $H$ 를 상수로 만들고, $t_f$ 자유 조건이 그 상수를 0 으로 고정한다" }
  - id: q3
    type: single
    prompt: "이중 적분기 최소 시간 문제에서 스위칭이 최대 1회인 근거는?"
    choices:
      - "제어가 $|u| \\le 1$ 로 유계이기 때문"
      - "$H$ 가 $u$ 에 아핀이기 때문"
      - "스위칭 함수 $\\lambda_2(t) = c_2 - c_1 t$ 가 $t$ 의 1차식이고, 항등적으로 0 이면 $(\\lambda_0,\\lambda) \\ne 0$ 을 위반하기 때문"
      - "최소 시간 문제의 해가 유일하기 때문"
    answer: 2
    explanation: "아핀성은 bang-bang 꼴(부호 판정)만 주고, 횟수는 스위칭 함수의 영점 개수가 정한다. 수반 방정식이 $\\dot\\lambda_1 = 0$, $\\dot\\lambda_2 = -\\lambda_1$ 이라 $\\lambda_2$ 가 1차식이므로 영점은 최대 1개다. $\\lambda_2 \\equiv 0$ 이면 $\\lambda \\equiv 0$ 이고 $H \\equiv 0$ 에서 $\\lambda_0 = 0$ 이 되어 비자명성 조건을 깬다 — 그래서 특이 호도 없다."
    concept: { front: "bang-bang 스위칭 횟수를 정하는 것", back: "스위칭 함수 $s = F^\\top\\lambda$ 의 영점 개수. 이중 적분기에서는 $s$ 가 1차식이라 최대 1회" }
  - id: q4
    type: truefalse
    prompt: "단일 슈팅의 조건수가 지평선에 대해 지수적으로 커지는 것은 양방향 경계값 문제 자체가 악조건이기 때문이다."
    answer: false
    explanation: "경계값 문제의 해 연산자는 $O(1)$ 이다 — 불안정 방향은 앞으로, 안정 방향은 뒤로 전파하면 된다. 악조건은 '모든 미지수를 $t=0$ 에 모아 전구간을 앞으로 적분한다'는 환원 방식에서 생긴다. 그래서 다중 슈팅과 collocation 이 같은 문제를 잘 푼다."
    concept: { front: "슈팅이 터지는데 collocation 은 되는 이유", back: "악조건은 BVP 가 아니라 IVP 환원에 있다. 구간을 $N$ 개로 쪼개면 $e^{\\sigma T}$ 가 $e^{\\sigma T/N}$ 이 된다" }
  - id: q5
    type: single
    prompt: "해밀토니안 계 $\\dot z = J\\nabla_z H$ 의 선형화 행렬 고윳값이 $\\pm$ 쌍으로 오는 이유는?"
    choices:
      - "$\\nabla_z^2 H$ 가 양정부호이기 때문"
      - "$J\\nabla_z^2 H$ 가 해밀토니안 행렬이고, 그 특성다항식이 $\\mu$ 의 짝함수이기 때문"
      - "수반 방정식이 역시간으로 흐르기 때문"
      - "$J^2 = -I$ 이기 때문"
    answer: 1
    explanation: "$\\mathcal{A} = J\\mathcal{S}$ ($\\mathcal{S} = \\nabla_z^2H$ 대칭)는 $\\mathcal{A}^\\top J + J\\mathcal{A} = 0$ 을 만족하는 해밀토니안 행렬이고, 이로부터 $\\mathcal{A}$ 와 $-\\mathcal{A}^\\top$ 가 닮음이므로 스펙트럼이 원점 대칭이다. 스칼라 예 (22)에서는 $\\operatorname{tr} M = 0$ 이 그 표현이다. 안정 방향과 불안정 방향이 같은 비율로 나뉘는 것이 (7)의 $e^{2\\sigma T}$ 를 만든다."
    concept: { front: "해밀토니안 행렬의 스펙트럼 대칭", back: "$\\mu$ 가 고윳값이면 $-\\mu$ 도 고윳값. $e^{\\mathcal{A}T}$ 의 특잇값이 $e^{\\pm\\sigma T}$ 로 갈라져 슈팅 야코비안의 조건수가 $e^{2\\sigma T}$ 가 된다" }
```

## 이 단계 공부법

1. **부호 규약을 먼저 고정한다 (20분)** — "전제와 기호" 표를 종이에 옮기고, 이 레슨이
   **최소** 원리를 쓴다는 것을 표시해 둔다. Pontryagin 원전과 많은 논문은 최대 원리 규약이라
   $\lambda$ 의 부호가 반대다. 논문을 펼칠 때마다 이것부터 확인하는 습관이 유도 실수의
   절반을 없앤다.
2. **수반 방정식을 손으로 만든다 (80분)** — R2 의 (9)→(13) 을 책을 덮고 재구성한다.
   적분 순서 교환 ((10) 다음 줄)이 유일한 트릭이고, 거기서 $\lambda$ 의 **정의** (11)이
   나온다. 이 계산을 내 손으로 한 번 해 두면 `c4-ilqr-ddp` 의 역방향 패스와
   역전파가 같은 것으로 보인다.
3. **증명은 전략과 3단계만 외운다 (70분)** — R1 의 여섯 단계 중 기억할 것은 "① 비용을 상태로
   올려 경계점 문제로 ③ 바늘의 원뿔이 볼록 ④ 분리 초평면" 이다. 2·5·6 단계는 계산이다.
   그 다음 "가설을 지우면" 네 문단을 읽고, 각 문단을 한 줄로 요약해 적어 본다 — 이 네 줄이
   C4 의 나머지 레슨(접촉, 제약, 충분조건)으로 가는 지도다.
4. **bang-bang 을 손으로 풀고 수치로 확인한다 (60분)** — R3 의 (17)→(19) 를 다시 쓰고,
   P4 를 **해석적으로** 푼다(수치 적분 금지). 스위칭 곡선 $x_1 = -\tfrac12 x_2\lvert x_2\rvert$
   를 그려 두면 다음 레슨의 LQR 피드백과 대비가 선명해진다.
5. **폭발을 직접 본다 (100분)** — 재현 과제의 문제 B 를 **먼저** 한다(문제 A 보다 짧다).
   $\log\lvert dr/dp\rvert$ 가 직선으로 올라가는 그림을 자기 손으로 뽑아야 (7)이 기억에 남는다.
   그 다음 문제 A 를 단일 슈팅으로 풀면, 지평선이 짧을 때 간접법이 얼마나 정확한지
   ($10^{-16}$ 급 잔차) 동시에 보게 된다. **두 경험이 짝이다** — 하나만 하면 "간접법은
   쓸모없다" 또는 "간접법이 최고다" 중 하나로 잘못 기억한다.
6. **논문은 대비로 읽는다 (150분)** — Sussmann & Willems 를 먼저 읽어 R5 를 역사적 맥락에
   놓고, Betts §3–§4 로 "그래서 왜 실무는 직접법인가"를 받고, 마지막에 Hartl et al. §3 으로
   "제약이 들어오면 (2)가 어떻게 깨지는가"를 본다. 논문당 1페이지 노트는 **반드시** 쓴다.
7. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제" 넷 중 하나를 골라 왜 아직 안 풀렸는지
   한 문단으로 쓴다. C4 의 마지막 두 레슨(접촉, 강건)이 그 중 둘을 다시 다룬다.

**통과 기준**: 백지에서 (11)–(12)(수반 방정식의 정의와 도출)와 (19)(이중 적분기 해)를 쓸 수
있고, R1 의 증명 전략과 "가설을 지우면" 네 경우를 말할 수 있고, 재현 과제의 네 조건을 모두
만족하는 코드를 갖고 있고, 논문 3편의 노트가 있다.
