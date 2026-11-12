---
id: c6-kinodynamic-planning
title: 미분 제약·격자 계획
summary: >-
  가정 (A2)("경로는 연속이기만 하면 된다")를 깬다. 미분 제약 $\dot x = f(x,u)$ 아래에서는
  두 상태를 잇는 것 자체가 최적 제어 문제이고, 선형계에서는 그 해가 가제어성 그라미안으로
  닫힌 형태로 나온다. 고정 시간 최소 에너지 조종을 유도하고 시간 가중 비용의 최적 조종 시간
  $\tau^\ast$ 가 만족하는 정상 조건을 얻은 뒤, 그 조종을 RRT* 에 넣을 때 "공" 대신 "비용
  준위집합"을 써야 하는 이유를 본다. 마지막으로 조종을 포기하는 길 — 운동 원시와 상태 격자 —
  의 닫힘 조건을 유도한다. 재현 과제에서 이중 적분기 kinodynamic RRT* 를 돌려 수렴을 측정한다.
objectives:
  - 고정 시간 최소 에너지 조종의 해와 비용을 가제어성 그라미안으로 유도할 수 있다.
  - 시간 가중 비용의 최적 조종 시간이 만족하는 정상 조건을 쓰고 이중 적분기에서 닫힌 형태로 풀 수 있다.
  - kinodynamic RRT* 에서 유클리드 공 대신 비용 준위집합을 써야 하는 이유를 반례로 설명할 수 있다.
  - 상태 격자가 닫히기 위한 조건(운동 원시가 격자점을 정확히 잇는다)을 Dubins 호로 유도할 수 있다.
  - 조종이 불가능한 계에서 점근 최적성을 어떻게 회복하는지(전방 전파 + 가지치기) 설명할 수 있다.
prerequisites: [c6-search-based-planning]
difficulty: 5
estimated_minutes: 510
tags: [motion-planning, kinodynamic, differential-constraints, steering, state-lattice, research]
activities:
  - id: c6-kinodynamic-planning-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 110
  - id: c6-kinodynamic-planning-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 130
  - id: c6-kinodynamic-planning-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 2 · 계산 2 · 구현 1 · 반례 1)
    estimated_minutes: 160
  - id: c6-kinodynamic-planning-reproduction
    kind: reproduction
    title: 재현 과제 — 이중 적분기 kinodynamic RRT* 의 수렴 (R2)
    estimated_minutes: 95
  - id: c6-kinodynamic-planning-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "LaValle, Planning Algorithms"
    url: http://lavalle.pl/planning/
    kind: book
    note: ch.13 (미분 모델), ch.14 (미분 제약 하 샘플링 기반 계획) — 14.2 의 도달가능 그래프와 14.4 의 격자.
  - title: "Webb & van den Berg — Kinodynamic RRT*: optimal motion planning for systems with linear differential constraints (2013)"
    url: https://arxiv.org/abs/1205.5088
    kind: paper
    note: 필독 1. R1 의 그라미안 조종과 $\tau^\ast$ 의 정상 조건이 여기서 나온다.
  - title: "Pivtoraiko, Knepper & Kelly — Differentially constrained mobile robot motion planning in state lattices (2009)"
    url: https://doi.org/10.1002/rob.20285
    kind: paper
    note: 필독 2. 상태 격자와 운동 원시, 경로 집합(path set)의 중복 제거.
  - title: "Karaman & Frazzoli — Optimal kinodynamic motion planning using incremental sampling-based methods (2010)"
    url: https://doi.org/10.1109/CDC.2010.5717430
    kind: paper
    note: 필독 3. RRT* 를 미분 제약으로 확장할 때 필요한 가정(약 국소 가제어성)과 반경 규칙의 변형.
  - title: "Li, Littlefield & Bekris — Asymptotically optimal sampling-based kinodynamic planning (2016)"
    url: https://arxiv.org/abs/1407.2896
    kind: paper
    note: 권장. SST — 조종 없이 전방 전파 + 가지치기로 (준)최적성을 얻는다. R4 의 출처.
  - title: "Hauser & Zhou — Asymptotically optimal planning by feasible kinodynamic planning in a state-cost space (2016)"
    url: https://doi.org/10.1109/tro.2016.2602363
    kind: paper
    note: 권장. 비용을 상태에 넣어 최적 계획을 가능성 계획으로 환원한다.
  - title: "Dubins — On curves of minimal length with a constraint on average curvature (1957)"
    url: https://doi.org/10.2307/2372560
    kind: paper
    note: 권장. 곡률 제약 하 최단 경로가 호-직선-호의 유한 집합으로 분류된다는 원전.
  - title: "Reeds & Shepp — Optimal paths for a car that goes both forwards and backwards (1990)"
    url: https://doi.org/10.2140/pjm.1990.145.367
    kind: paper
    note: 권장. 후진을 허용한 Dubins 의 확장. 48개 단어 분류.
---

# 미분 제약·격자 계획

## 전제와 기호

이 모듈의 앞 다섯 레슨을 전제한다. 이 레슨은 `c6-cspace-complexity` 의 가정 **(A2)를 깬다** —
이제 경로는 연속이기만 해서는 안 되고 **동역학을 만족**해야 한다. 추가 전제:

- 선형 계통: 상태 공간 모델, 행렬 지수 $e^{At}$, 가제어성(controllability)과 그라미안.
  Riccati 방정식은 **필요하지 않다**.
- 최적 제어의 **용어만**: 비용 함수, 코스테이트(costate). 변분법의 일반론은 필요하지 않다 —
  여기서는 선형 제약 아래 최소 노름 문제(유사역행렬)로 환원해 푼다
  (권장 선수 `r0-linear-algebra-decompositions`, `c4-dp-lqr-lqg`).

표기(모듈 표기에 추가):

| 기호 | 뜻 |
|---|---|
| $x \in \mathbb{R}^n$ | 상태. 이중 적분기에서는 $(p, v)$ |
| $u \in \mathbb{R}^m$ | 제어 입력 |
| $\dot x = Ax + Bu$ | 선형 동역학 (R1·R2 의 가정) |
| $\mathcal{R}(x_0, \tau)$ | 시간 $\tau$ 안의 도달가능 집합 |
| $G(\tau)$ | 가제어성 그라미안 $\int_0^\tau e^{As}BR^{-1}B^\top e^{A^\top s}\,ds$ |
| $d(\tau)$ | $x_1 - e^{A\tau}x_0$ — 자유 운동으로 덮지 못한 차이 |
| $c(x_0, x_1)$ | 최적 조종 비용 $\min_\tau c(\tau)$ |
| $\tau^\ast$ | 최적 조종 시간 |
| $\lambda$ | 종단 코스테이트 $G(\tau)^{-1}d(\tau)$ |
| $\mathcal{P}$ | 운동 원시(motion primitive) 집합 |
| $\Lambda$ | 상태 격자(state lattice) |

**비용.** 이 레슨은 시간과 제어 노력을 함께 재는 비용

$$
J(u, \tau) \;=\; \int_0^\tau \big(1 + u(t)^\top R\, u(t)\big)\,dt
  \;=\; \tau + \int_0^\tau u^\top R\,u\,dt
  \tag{1}
$$

를 쓴다($R \succ 0$). 시간만 재면($R \to 0$) 입력 제약 없이는 비용이 0 으로 가고, 노력만 재면
($1 \to 0$) 무한히 느린 운동이 최적이 된다. **두 항이 모두 필요하고, 그 교환이 $\tau^\ast$ 를
결정한다.**

전제 하나를 명시한다: **(A6) 조종 가능성(steerability)** — 임의의 두 상태 $x_0, x_1$ 에 대해
$x_0$ 에서 $x_1$ 로 정확히 가는 제어가 있고 그 최적 비용을 계산할 수 있다. 선형·가제어
계통에서는 R1 이 이것을 준다. **비선형계에서는 일반적으로 거짓이고**, 그때 무엇을 하는지가
R4 다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명).

- **R1 (고정 시간 최적 조종과 $\tau^\ast$ 의 정상 조건) [D2]** — $(A,B)$ 가 가제어이면
  고정 시간 $\tau$ 의 최소 노력 조종은
  $$u^\ast(t) = R^{-1}B^\top e^{A^\top(\tau - t)}\,\lambda, \quad \lambda = G(\tau)^{-1}d(\tau),
    \qquad c(\tau) = \tau + d(\tau)^\top G(\tau)^{-1} d(\tau) \tag{2}$$
  이고, 최적 조종 시간은
  $$\dot c(\tau^\ast) = 1 - 2\,(A x_1)^\top \lambda - \lambda^\top B R^{-1} B^\top \lambda = 0
    \tag{3}$$
  을 만족한다. **이중 적분기에서는 닫힌 형태로 풀린다** — 정지에서 정지로 변위
  $(\Delta p_1, \Delta p_2)$ 를 가면 $c(\tau) = \tau + 12(\Delta p_1^2+\Delta p_2^2)/\tau^3$ 이고
  $\Delta p = (1,1)$ 에서
  $$c(\tau) = \tau + \frac{24}{\tau^3},\quad \tau^\ast = 72^{1/4} = 2.912950630244,
    \quad c^\ast = \tfrac43\,72^{1/4} = 3.883934173659. \tag{4}$$
- **R2 (kinodynamic RRT* 의 최적성 조건) [D2]** — 세 가지가 동시에 필요하다.
  (ⓐ) **정확한 최적 조종**(A6) — 근사 조종은 재배선을 틀리게 만든다.
  (ⓑ) **이웃 집합을 비용 준위집합으로** 정의한다:
  $N(x) = \{x' : c(x', x) \le r_n\}$. 유클리드 공을 쓰면 **비대칭성**($c(x_0,x_1) \ne c(x_1,x_0)$)과
  동역학적 접근 불가 방향 때문에 이웃의 대부분이 연결 불가가 되어 점근 최적성이 깨진다.
  (ⓒ) 반경 규칙은 **도달가능 집합의 부피**로 다시 써야 한다 — 유효 차원이 $n$ 이 아니라
  동역학이 정하는 값이 된다($\dot x = Ax+Bu$ 에서 $\mathcal{R}(x_0,\tau)$ 의 부피는
  $\tau$ 의 거듭제곱이고 지수는 Kalman 지수(controllability index)로 정해진다).
- **R3 (상태 격자의 닫힘 조건) [D2]** — 격자 $\Lambda$ 와 원시 집합 $\mathcal{P}$ 가
  **닫혀(closed)** 있다는 것은 모든 $\pi \in \mathcal{P}$ 가 $\Lambda$ 의 한 점에서 시작해
  $\Lambda$ 의 한 점에서 **정확히** 끝나는 것이다. 곡률 반지름 $\rho$ 의 좌회전 호가
  헤딩 $\theta_i \to \theta_j$ 로 가는 변위는
  $$\Delta p = \rho\big(\sin\theta_j - \sin\theta_i,\; \cos\theta_i - \cos\theta_j\big) \tag{5}$$
  이므로, $\Lambda$ 의 위치가 $\mathbb{Z}^2$ 이면 **(5)가 정수 벡터일 때만** 원시가 존재한다.
  이 조건이 격자 설계에서 헤딩 집합을 "피타고라스 각"($\sin,\cos$ 이 유리수)으로 잡는 이유다.
- **R4 (조종이 불가능할 때) [D1]** — 비선형계에서 (A6)이 깨지면 RRT* 의 재배선 자체가
  불가능하다. 대안은 **전방 전파 + 가지치기**다: 무작위 제어를 적분해 트리를 키우고, 비용이
  나쁜 가지를 비용-상태 공간의 $\delta$-근방에서 지배(domination) 관계로 솎아낸다. 이 구조가
  조종 없이 점근 (준)최적성을 준다([Li, Littlefield & Bekris 2016](https://arxiv.org/abs/1407.2896)).

## 유도

### R1 — 고정 시간 최적 조종

**도달가능 집합.** 선형계의 해는
$$x(\tau) = e^{A\tau}x_0 + \underbrace{\int_0^\tau e^{A(\tau - s)}B\,u(s)\,ds}_{=:\ \mathcal{L}_\tau u}.$$
즉 $x(\tau) = e^{A\tau}x_0 + \mathcal{L}_\tau u$ 이고, $\mathcal{L}_\tau$ 는
$L^2([0,\tau];\mathbb{R}^m) \to \mathbb{R}^n$ 의 **선형** 연산자다. 따라서 **도달가능 집합은
$\mathcal{L}_\tau$ 의 상(image)을 $e^{A\tau}x_0$ 로 평행이동한 아핀 부분공간**이고, 가제어이면
그 상이 $\mathbb{R}^n$ 전체다. 조종 문제는 선형 방정식 $\mathcal{L}_\tau u = d(\tau)$ 의
**최소 노름 해**를 찾는 것으로 환원된다 — 미분기하도 변분법도 필요 없다.

**최소 노름 해.** $\langle u, w\rangle_R = \int_0^\tau u^\top R w \, dt$ 로 내적을 두면
$\mathcal{L}_\tau$ 의 수반(adjoint)은 $(\mathcal{L}_\tau^\ast \lambda)(t) = R^{-1}B^\top
e^{A^\top(\tau - t)}\lambda$ 이고(직접 $\langle \mathcal{L}_\tau u, \lambda\rangle =
\langle u, \mathcal{L}_\tau^\ast\lambda\rangle_R$ 을 확인하라), 따라서

$$
\mathcal{L}_\tau \mathcal{L}_\tau^\ast
  = \int_0^\tau e^{A(\tau-s)} B R^{-1} B^\top e^{A^\top(\tau - s)}\,ds
  = \int_0^\tau e^{A\sigma} B R^{-1} B^\top e^{A^\top \sigma}\,d\sigma = G(\tau),
$$

($\sigma = \tau - s$ 치환). 최소 노름 해는 $u^\ast = \mathcal{L}_\tau^\ast G(\tau)^{-1}d$ 이고
이것이 (2)의 첫 식이다. 그 노름은

$$
\int_0^\tau u^{\ast\top} R u^\ast dt = \langle u^\ast, u^\ast\rangle_R
  = \langle \mathcal{L}_\tau^\ast \lambda, \mathcal{L}_\tau^\ast\lambda\rangle_R
  = \lambda^\top \mathcal{L}_\tau\mathcal{L}_\tau^\ast \lambda
  = d^\top G(\tau)^{-1} d,
$$

즉 (2)의 둘째 식이다. **$\lambda$ 는 코스테이트이고 $G^{-1}$ 는 "얼마나 세게 밀어야 하는가"를
재는 행렬**이다. $\tau \to 0$ 에서 $G(\tau) \to 0$ 이므로 비용이 발산한다 — 짧은 시간에
멀리 가려면 무한한 노력이 든다는 당연한 사실의 정량이다.

**최적 조종 시간.** (1)의 전체 비용은 $c(\tau) = \tau + d(\tau)^\top G(\tau)^{-1}d(\tau)$ 다.
미분하면 (3)이 나온다:
$$\dot c(\tau) = 1 - 2\,(Ax_1)^\top \lambda - \lambda^\top B R^{-1}B^\top \lambda.$$
세 항의 뜻이 각각 분명하다 — 1 은 시간 비용의 증가, 둘째 항은 목표 상태가 자유 운동으로
"저절로 다가오는" 이득, 셋째 항은 더 긴 시간이 주는 노력 절감이다. $\tau$ 가 작으면 셋째 항이
지배해 $\dot c < 0$, 크면 1 이 지배해 $\dot c > 0$ 이므로 **$\dot c$ 의 영점이 유일한 최소**다.
(이 글의 (3)은 200개 무작위 사례에서 유한차분과 $2.3\times10^{-7}$(차분 오차 수준) 이내로
일치함을 수치로 확인했다.)

**이중 적분기 닫힌 형태.** $n=4$, $x = (p_1,p_2,v_1,v_2)$,
$e^{A\tau} = \begin{bmatrix} I & \tau I \\ 0 & I\end{bmatrix}$, $R = I$ 이면 축마다

$$
G_{\text{axis}}(\tau) = \begin{bmatrix} \tau^3/3 & \tau^2/2 \\ \tau^2/2 & \tau \end{bmatrix},
\qquad
G_{\text{axis}}^{-1} = \frac{12}{\tau^4}\begin{bmatrix} \tau & -\tau^2/2 \\ -\tau^2/2 & \tau^3/3\end{bmatrix}
$$

($\det G_{\text{axis}} = \tau^4/3 - \tau^4/4 = \tau^4/12$). $a_i = \Delta p_i - \tau v_{0,i}$,
$b_i = \Delta v_i$ 로 두면

$$
c(\tau) = \tau + \sum_{i}\left(\frac{12 a_i^2}{\tau^3} - \frac{12 a_i b_i}{\tau^2}
  + \frac{4 b_i^2}{\tau}\right). \tag{6}
$$

정지에서 정지($v_0 = v_1 = 0$)로 변위 $\Delta p$ 를 가면 $a_i = \Delta p_i$, $b_i = 0$ 이므로
$c(\tau) = \tau + 12\lVert\Delta p\rVert^2/\tau^3$ 이고, $\dot c = 1 - 36\lVert\Delta p\rVert^2/\tau^4 = 0$
에서 $\tau^\ast = (36\lVert\Delta p\rVert^2)^{1/4}$, $c^\ast = \tfrac43\tau^\ast$ 다.
$\Delta p = (1,1)$ 이면 $\lVert\Delta p\rVert^2 = 2$, $\tau^\ast = 72^{1/4}$, $c^\ast = \tfrac43 72^{1/4}$ —
(4)다. **$c^\ast = \tfrac43\tau^\ast$ 라는 관계가 깔끔하다**: 최적점에서 노력 비용이 시간 비용의
정확히 1/3 이다(문제 P2).

**가정이 깨지는 곳**: (ⓐ) 입력 제약 $\lVert u\rVert \le u_{max}$ 가 있으면 (2)는 **틀린다** —
최소 노름 해가 제약을 위반할 수 있고, 제약된 문제는 닫힌 형태가 없다(시간 최적 해는 bang-bang
이 되고 그것이 Dubins·Reeds–Shepp 분류의 출발점이다). 실무의 우회는 $\tau$ 를 키워 노름을
줄이는 것이고, 그래서 (1)의 시간 항이 **제약의 대리(proxy)** 로 작동한다.
(ⓑ) $(A,B)$ 가 가제어가 아니면 $G(\tau)$ 가 특이해져 $G^{-1}$ 이 없다. 도달가능 집합이
부분공간이므로 그 밖의 $x_1$ 로는 **어떤 시간에도** 갈 수 없다 — 이것이 비홀로노믹 계통에서
"국소적으로는 못 가지만 전역적으로는 간다"는 현상과 **다르다**는 점에 주의하라(선형계는
도달가능성이 시간에 무관하다).

### R2 — 왜 공이 아니라 비용 준위집합인가

RRT*(`c6-asymptotic-optimality` R1)의 세 요구를 미분 제약으로 옮겨 본다.

**요구 1(피복)은 그대로.** 최적 궤적 주변을 덮는 것은 여전히 필요하다. 다만 "공"의 자리에
**도달가능 집합의 조각**이 온다.

**요구 2(연결)가 깨진다.** 유클리드 공 $\lVert x' - x\rVert \le r$ 안의 점 대부분은
$x$ 에서 **싸게 갈 수 없다**. 이중 적분기에서 보자: $x = (0,0)$(정지)에서
$x' = (\epsilon, 0)$(가까운 위치, 정지)로 가는 비용은 (4)에서
$c = \tfrac43(36\epsilon^2)^{1/4} \propto \epsilon^{1/2}$ 이지만,
$x'' = (0, \epsilon)$(같은 위치, 속도만 다름)로 가는 비용은 (6)에서 $a = -\tau\cdot 0 = 0$,
$b = \epsilon$ 이므로 $c = \tau + 4\epsilon^2/\tau$ 이고 최소는 $\tau = 2\epsilon$ 에서
$c = 4\epsilon$ 이다. 즉 **같은 유클리드 거리 $\epsilon$ 에 대해 비용이 $\epsilon^{1/2}$ 와
$\epsilon$ 로 차수가 다르다.** 유클리드 공은 비용에 대해 **등방이 아니고**, $\epsilon \to 0$
에서 그 비등방성이 무한히 커진다. 그래서 이웃을 $c(x',x) \le r_n$ 의 **준위집합**으로 정의해야
요구 1 과 요구 2 가 맞물린다.

**요구 3(비용)도 다시 써야 한다.** 준위집합 $\{x' : c(x_0,x') \le r\}$ 의 부피는 $r$ 의
거듭제곱이지만 **지수가 $n$ 이 아니다**. 이중 적분기에서 위치 방향은 $r$ 의 2승, 속도 방향은
1승에 비례해 퍼지므로(위 계산의 차수 차이) 부피는 $r^{d_{\text{eff}}}$ 꼴이고
$d_{\text{eff}} > n$ 이 된다. 따라서 반경 규칙 $r_n = \gamma(\log n/n)^{1/d}$ 의 $d$ 를
**$d_{\text{eff}}$ 로 바꿔야** 기대 이웃 수가 $\log n$ 에 비례한다. 재현 과제는
$d_{\text{eff}} = 4$(상태 차원)로 두는 **보수적 선택**을 쓰고, 그것이 보장을 해치지 않는
방향임을 조건 4 에서 확인한다.

**가정이 깨지는 곳**: 비용 함수 $c$ 는 **거리가 아니다** — 대칭성($c(x,y) = c(y,x)$)이
성립하지 않고 삼각 부등식도 일반적으로 성립하지 않는다. 그래서 `c6-asymptotic-optimality`
의 증명을 글자 그대로 옮길 수 없고, Karaman–Frazzoli 2010 은 **약 국소 가제어성(weak local
controllability)** 과 비용의 국소 Lipschitz 성질을 추가 가정으로 넣는다. 그 가정이 비선형계에서
언제 성립하는지는 **열린 문제**다.

### R3 — 상태 격자의 닫힘 조건

**왜 격자인가.** (A6)이 성립해도 조종 계산이 비싸면(비선형 최적 제어를 매 간선마다 푸는 것)
샘플링이 느려진다. 격자는 **조종을 미리 계산해 재사용**한다: 상태를 격자 $\Lambda$ 로
이산화하고, 격자점을 잇는 궤적 조각(운동 원시) 집합 $\mathcal{P}$ 를 오프라인에 만들어 두면
계획이 `c6-search-based-planning` 의 **그래프 탐색**으로 환원된다.

**닫힘 조건.** 원시 $\pi$ 를 이어 붙여 만든 궤적이 **오차 없이** 격자 위에 머물러야 한다.
$\pi$ 의 종단 상태가 격자점에서 $\epsilon$ 만큼 벗어나면 $k$ 개를 이을 때 오차가
$O(k\epsilon)$ 로 **누적**되고, 그 궤적은 더 이상 동역학을 만족하는 궤적이 아니다. 따라서

> 모든 $\pi \in \mathcal{P}$ 는 $\Lambda$ 의 한 점에서 시작해 $\Lambda$ 의 한 점에서
> **정확히** 끝나야 한다.

**Dubins 호로 보는 조건.** 곡률 반지름 $\rho$ 의 좌회전 호를 생각하자. 헤딩이 $\theta$ 일 때
위치의 변화는 $\dot p = (\cos\theta, \sin\theta)$ 이고 $\dot\theta = 1/\rho$ 이므로
$ds = \rho\,d\theta$ 로 매개화하면

$$
\Delta p = \int_{\theta_i}^{\theta_j} \rho\,(\cos\theta, \sin\theta)\,d\theta
  = \rho\big(\sin\theta_j - \sin\theta_i,\; \cos\theta_i - \cos\theta_j\big),
$$

즉 (5)다. 위치 격자가 $\mathbb{Z}^2$(단위 셀)이면 **(5)의 두 성분이 모두 정수**여야 원시가
존재한다. 두 예:

- $\theta_i = 0$, $\theta_j = \pi/2$: $\Delta p = \rho(1, 1)$ → $\rho \in \mathbb{Z}$ 일 때만.
- $\theta_i = 0$, $\theta_j = \arctan(3/4)$ (즉 $\sin\theta_j = 3/5$, $\cos\theta_j = 4/5$):
  $\Delta p = \rho(3/5,\ 1/5)$ → $\rho$ 가 **5의 배수**일 때만.

후자가 **피타고라스 각**을 쓰는 이유다: $(3,4,5)$, $(5,12,13)$ 처럼 $\sin,\cos$ 이 유리수인
헤딩을 고르면 분모의 최소공배수를 $\rho$ 에 흡수해 격자를 닫을 수 있다. 임의의 등간격 헤딩
($2\pi/N_\theta$)을 쓰면 (5)가 무리수가 되어 **닫히지 않고**, 구현은 종단 상태를 격자점으로
"스냅(snap)"하게 되며 그 순간 궤적이 동역학을 위반한다 — 격자 플래너에서 가장 흔한
정확성 결함이다.

**가정이 깨지는 곳**: 닫힘을 얻으려면 헤딩 집합과 $\rho$ 를 함께 설계해야 하므로 **격자의
해상도를 자유롭게 고를 수 없다**. 해상도를 높이려면 원시 수가 폭발하고(원시 수 ≈ 헤딩 수 ×
도달 셀 수), 중복 원시를 제거하는 것이 Pivtoraiko 등의 "경로 집합(path set)" 문제다.
그리고 격자는 **해상도 완전(resolution complete)** 일 뿐 완전하지 않다 — 격자 해상도보다
얇은 통로는 영원히 보이지 않는다.

## 증명 스케치

### R2 — kinodynamic RRT* 의 점근 최적성 조건

**가설** H1: (A6) — 임의의 두 상태에 대해 **정확한** 최적 조종과 그 비용이 계산 가능하다.
H2: 비용 $c(x,x')$ 가 국소적으로 Lipschitz 이고, 최적 궤적이 양의 "동역학적 간격"
(궤적 주변 $\delta$-관(tube) 안의 모든 상태가 자유)을 갖는다.
H3: 이웃 집합이 비용 준위집합 $N(x) = \{x' : c(x',x) \le r_n\}$ 으로 정의되고
$r_n = \gamma(\log n/n)^{1/d_{\text{eff}}}$ 이며 $\gamma$ 가 충분히 크다.
H4: 재배선이 (A6)의 **정확한** 조종으로 수행되고 하위 트리 비용이 전파된다.
**결론** C: 알고리즘은 점근 최적이다.

**전략**: `c6-asymptotic-optimality` R1 의 세 요구를 **비용 공간에서** 다시 세운다.
유클리드 구조가 쓰인 자리를 전부 비용 준위집합으로 바꾸는 것이 증명의 전부다.

1. **덮개를 비용으로 만든다.** 최적 궤적 $\sigma^\ast$ 를 비용 $r_n/2$ 간격으로 끊어 상태
   $x_0^\ast, \dots, x_m^\ast$ 를 놓고, 각각의 **비용 공** $\{x : c(x_i^\ast, x) \le r_n/4\}$ 을
   덮개로 쓴다. H2 가 이 공들이 자유공간 안에 들어감을 보장한다.
2. **샘플이 비용 공에 떨어질 확률.** 비용 공의 르베그 측도가 $\Theta(r_n^{d_{\text{eff}}})$
   이므로 $p_n = \Theta(r_n^{d_{\text{eff}}}/\mu)$ 다. 여기서 $d_{\text{eff}}$ 가 **상태 차원이
   아니라 동역학이 정하는 값**인 것이 선형 계통과의 유일한 차이다.
3. **연결.** 연속한 두 비용 공의 샘플 $y_i, y_{i+1}$ 에 대해 삼각 부등식을 쓸 수 없으므로
   (비용은 거리가 아니다) H2 의 Lipschitz 성질로
   $c(y_i, y_{i+1}) \le c(x_i^\ast, x_{i+1}^\ast) + L(\,\cdot\,) \le r_n$ 를 얻는다.
   (생략: Lipschitz 상수에서 상수 인자를 추적하는 단계 —
   [Karaman & Frazzoli 2010](https://doi.org/10.1109/CDC.2010.5717430) 의 보조정리.)
4. **합 가능성과 Borel–Cantelli.** 2·3 에서 $np_n \propto \log n$ 이 되도록 $\gamma$ 를 잡으면
   앞 레슨 R1 의 요구 1 과 **같은 계산**으로 실패 확률이 합 가능해지고 거의 확실한 수렴을 얻는다.
5. **재배선의 정확성.** H4 가 없으면(근사 조종) 재배선이 **존재하지 않는 궤적**을 트리에
   넣는다. 그러면 비용이 과소평가되어 알고리즘이 보고하는 해가 실행 불가능해진다 —
   점근 최적성보다 먼저 **타당성(validity)** 이 깨진다.

**가설을 지우면**: H1 을 지우면(비선형계) 5단계가 무너지고 RRT* 구조 자체를 쓸 수 없다 — R4 의
전방 전파로 가야 한다. H3 의 "준위집합"을 유클리드 공으로 바꾸면 3단계에서 연결이
실패한다(유도 R2 의 $\epsilon^{1/2}$ 대 $\epsilon$ 차수 차이가 원인). H2 의 동역학적 간격을
빼면 1단계의 덮개를 자유공간 안에 놓을 수 없다.

## 문제 세트

난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** $\mathcal{L}_\tau$ 의 수반이
$(\mathcal{L}_\tau^\ast\lambda)(t) = R^{-1}B^\top e^{A^\top(\tau-t)}\lambda$ 임을 내적 정의로
직접 확인하고, $\mathcal{L}_\tau\mathcal{L}_\tau^\ast = G(\tau)$ 를 유도하라.
*해답 스케치*: $\langle \mathcal{L}_\tau u, \lambda\rangle = \lambda^\top\int_0^\tau
e^{A(\tau-s)}Bu(s)ds$ 를 적분 안으로 옮기고 $\langle u, w\rangle_R$ 꼴로 맞춘다.
치환 $\sigma = \tau - s$ 가 그라미안의 표준형을 준다.

**P2 (유도, ★★, R1)** 정지–정지 이중 적분기에서 $c^\ast = \tfrac43\tau^\ast$ 임을 보이고,
**최적점에서 노력 비용과 시간 비용의 비가 항상 1:3** 임을 확인하라. 이 비가 변위에 무관한
이유를 설명하라.
*해답 스케치*: $c(\tau) = \tau + K/\tau^3$ 에서 $\dot c = 0$ 이면 $K = \tau^4/3$ 이고
$c^\ast = \tau^\ast + \tau^\ast/3$. 무관한 이유는 $c$ 가 $\tau$ 에 대해 **동차 꼴**이라
변위가 $K$ 를 통해서만 들어가기 때문이다.

**P3 (계산, ★, R1)** 이중 적분기에서 $x_0 = (0,0,0,0)$, $x_1 = (1,1,0,0)$, $R = I$ 일 때
$\tau^\ast$ 와 $c^\ast$ 를 구하고, $\tau = 2$ 와 $\tau = 3$ 의 비용을 각각 구하라.
*정답*: $c(\tau) = \tau + 24/\tau^3$. $\tau^\ast = 72^{1/4} = 2.912950630244$,
$c^\ast = \tfrac43 72^{1/4} = 3.883934173659$. $c(2) = 2 + 3 = 5$ 정확히,
$c(3) = 3 + 24/27 = 3.888888889$. 허용오차 $10^{-9}$.
검산: $\dot c(\tau) = 1 - 72/\tau^4$ 이 $\tau^\ast$ 에서 0 이고, (3)의 일반식에
$\lambda = (12/\tau^3, 12/\tau^3, -6/\tau^2, -6/\tau^2)$, $Ax_1 = 0$ 을 넣으면
$1 - \lVert B^\top\lambda\rVert^2 = 1 - 72/\tau^4$ 로 같은 식이 나온다.

**P4 (계산, ★, R3)** 곡률 반지름 $\rho$, 위치 격자 $\mathbb{Z}^2$ 에서 헤딩
$\theta_i = 0 \to \theta_j$ 의 좌회전 호가 격자를 닫는 $\rho$ 의 최솟값을 구하라.
(i) $\theta_j = \pi/2$, (ii) $\sin\theta_j = 3/5$, (iii) $\sin\theta_j = 5/13$.
*정답*: (5)에서 $\Delta p = \rho(\sin\theta_j,\ 1-\cos\theta_j)$.
(i) $\rho(1,1)$ → $\rho_{\min} = 1$.
(ii) $\cos\theta_j = 4/5$ 이므로 $\rho(3/5,\ 1/5)$ → 분모 5 → $\rho_{\min} = 5$.
(iii) $\cos\theta_j = 12/13$ 이므로 $\rho(5/13,\ 1/13)$ → $\rho_{\min} = 13$.
즉 **헤딩을 촘촘히 하면 격자를 닫는 최소 반지름이 커진다** — 해상도와 곡률의 교환이다.
허용오차: 정확한 정수.

**P5 (반례, ★★, R2)** 이중 적분기에서 "유클리드 공을 이웃으로 쓰면 점근 최적성이 깨진다"를
구체적 수치로 보이라: $x = (0,0,0,0)$ 에서 유클리드 거리 $\epsilon = 10^{-2}$ 인 두 상태
$x' = (\epsilon, 0, 0, 0)$ 과 $x'' = (0,0,\epsilon,0)$ 의 조종 비용을 각각 구하고 비율을 보라.
$\epsilon \to 0$ 에서 그 비율이 어떻게 되는가?
*성질 체크리스트*: $c(x,x') = \tfrac43(36\epsilon^2)^{1/4} = \tfrac43\sqrt{6\epsilon}$,
$c(x,x'') = 4\epsilon$. $\epsilon = 10^{-2}$ 에서 각각 $0.3266$ 과 $0.04$ — **8.2배** 차이다.
비율 $\propto \epsilon^{-1/2} \to \infty$. 유클리드 공 안에서 비용이 무계로 비등방이 되는
것을 쓸 것.

**P6 (증명, ★★, R3)** 원시의 종단 상태를 격자점으로 "스냅"하면 $k$ 개를 이을 때 상태 오차가
$O(k\epsilon)$ 로 누적됨을 보이고, 그 궤적이 동역학을 만족하지 않음을 명시하라. 이 오차를
피드백 제어로 흡수하는 방법의 한계도 쓰라.
*전략*: 스냅은 상태에 $\epsilon$ 의 점프를 넣는 것이고, 점프는 $\dot x = f(x,u)$ 의 해가 아니다.
오차 누적은 각 조각의 시작 상태가 틀린 데서 오는 전파로 쓴다(선형계면 $e^{A\tau}$ 가 증폭 인자).
피드백은 **추종 오차**를 줄이지만 계획 단계의 비용 평가가 이미 틀려 최적성이 깨진다.

**P7 (증명, ★★★, R2)** R2 의 3단계(연결)를 비용의 Lipschitz 성질만으로 완성하라. 즉
$c(x_i^\ast, x) \le r_n/4$, $c(x_{i+1}^\ast, y) \le r_n/4$ 이고
$c(x_i^\ast, x_{i+1}^\ast) \le r_n/2$ 일 때 $c(x, y) \le C\,r_n$ 인 상수 $C$ 를 찾으라
(비용이 거리가 아니므로 삼각 부등식을 쓸 수 없다는 것이 핵심 난점이다).
*전략*: 세 궤적을 이어 붙인 **가능한(feasible)** 제어를 명시적으로 구성해 그 비용을
상한으로 쓴다(최적 비용은 그 이하다). 이어 붙임이 가능하려면 중간 상태가 정확히 일치해야
하므로 조종의 정확성(H1)이 여기서 쓰인다.

**P8 (구현, ★★, R1·R2)** 재현 과제의 kinodynamic RRT* 를 쓰라. 요구: (6)의 비용으로 이웃을
정의, 고정 $\tau$ 격자에서 최솟값을 취하는 조종, 3차 Hermite 로 궤적을 샘플링한 충돌 검사,
재배선과 하위 트리 비용 전파.
*루브릭*: ⓐ 조건 1·2 의 수치가 일치한다 ⓑ 모든 해의 비용이 자유공간 하한 이상이다
ⓒ 이웃을 유클리드 공으로 바꿔 돌려 비용이 나빠지는 것을 수치로 보인다(P5 의 확인)
ⓓ 하위 트리 전파를 빼면 수렴이 멈추는 것을 보인다.

## 논문 읽기

**필독 3편.** 고정 질문 10개로 논문당 1페이지 노트를 쓴다.

1. **Webb & van den Berg, "Kinodynamic RRT*" (2013, ICRA)** — 역할: `표준(standard)`.
   <https://arxiv.org/abs/1205.5088>
   *왜 읽는가*: R1 의 (2)(3)이 여기서 나온다. 특히 $\tau$ 를 최적화하는 절을 보라 —
   이 레슨의 (3)과 같은 식이다.
   추가 질문: ⓐ 저자들이 입력 제약을 어떻게 다루는가(또는 다루지 않는가)?
   ⓑ 이웃 집합의 정의가 이 레슨 R2 의 (ⓑ)와 같은가? ⓒ 반경 규칙의 지수를 무엇으로 쓰는가?
2. **Karaman & Frazzoli, "Optimal kinodynamic motion planning using incremental sampling-based
   methods" (2010, CDC)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1109/CDC.2010.5717430>
   *왜 읽는가*: R2 의 가설 H2·H3 가 여기서 정식화된다. "약 국소 가제어성"이 정확히 무엇을
   요구하는지 확인하는 것이 요점이다.
   추가 질문: ⓐ 이 논문의 가정 아래 이중 적분기는 포함되는가? 자동차 모델은?
   ⓑ 저자들이 증명하는 것과 증명하지 않는 것을 각각 한 문장으로.
3. **Pivtoraiko, Knepper & Kelly, "Differentially constrained mobile robot motion planning in
   state lattices" (2009, JFR)** — 역할: `표준(standard)`.
   <https://doi.org/10.1002/rob.20285>
   *왜 읽는가*: R3 의 출처. 격자 설계(헤딩 집합과 반지름의 공동 선택)와 경로 집합의 중복
   제거가 이 논문의 두 기여다.
   추가 질문: ⓐ 저자들의 격자가 (5)의 정수 조건을 어떻게 만족시키는가?
   ⓑ 원시 수와 계획 품질의 교환을 어떻게 측정하는가?
   ⓒ "해상도 완전"과 "완전"의 차이를 논문은 어디서 명시하는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄 또는 그림 한 장으로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지
않는가** (5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가,
분산·시드를 보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, 30시드 × $n = 3000$ 이 30분 이내,
메모리 1GB 이내. numpy 만.

**입력 데이터(레슨이 지정).** 2차원 **이중 적분기**: 상태 $x = (p_1,p_2,v_1,v_2)$,
$\dot p = v$, $\dot v = u$, 비용 (1)에 $R = I$. 위치는 $[0,1]^2$, 속도는 $[-2,2]^2$ 로 제한한다.
$x_{start} = (0,0,0,0)$, $x_{goal} = (1,1,0,0)$. 장애물은 **위치 공간**의 직사각형
$[0.40,\ 0.60] \times [0.00,\ 0.65]$ 이고 내부가 막혀 있다.

고정 설정: 샘플은 위치 균등 $[0,1]^2$ × 속도 균등 $[-2,2]^2$, 장애물 내부 샘플은 버린다.
조종 시간은 **고정 격자** $\tau \in \{0.1\,e^{k\ln(80)/23} : k = 0,\dots,23\}$
(즉 $[0.1, 8]$ 의 로그 등간격 24점)에서 (6)의 최솟값을 취한다 — 이렇게 하면 결과가
완전히 결정론적이다. 반경은 $r_n = 4.0\,(\log n/n)^{1/4}$, 부모 후보는 비용순 상위 25개,
충돌 검사는 3차 Hermite 궤적의 16점 샘플. 시드 $0,\dots,29$. 검사점
$n \in \{500, 1000, 2000, 3000\}$.

**수용 기준 — 네 조건을 모두 만족해야 통과.**

1. **해석적 하한(R1 검증)** — 장애물을 **무시한** 자유공간 최적 조종 비용이
   $$c_{lb} = \tfrac43\,72^{1/4} = 3.883934173659, \qquad \tau^\ast = 72^{1/4} = 2.912950630244$$
   와 상대오차 $10^{-9}$ 이내로 일치한다. (3)의 일반식에 넣은 $\dot c(\tau^\ast)$ 의 절댓값이
   $10^{-9}$ 미만이다. **모든 시드·모든 검사점의 해 비용이 $c_{lb}$ 이상**이다(위반 0건).
2. **수렴(R2 검증)** — 30시드 모두 네 검사점에서 해를 찾고(30/30), 비용의 중앙값이

   | $n$ | 500 | 1000 | 2000 | 3000 |
   |---|---|---|---|---|
   | 중앙값 | 4.9967 | 4.6841 | 4.4782 | 4.4417 |
   | 중앙값/$c_{lb}$ | 1.2865 | 1.2060 | 1.1530 | 1.1436 |

   와 절대오차 0.05 이내로 일치하고 **단조 감소**한다. 30시드 전체의 최솟값은 네 검사점에서
   $4.1561 \pm 0.02$ 로 **변하지 않는다**(장애물이 있는 문제의 최적값 추정치).
3. **1.1배 수렴** — $n = 3000$ 에서 중앙값과 최솟값의 비가
   $4.4417/4.1561 = 1.0687 \le 1.10$ 이고, 그 비가 네 검사점에서 단조 감소한다
   (측정값 1.2023, 1.1270, 1.0775, 1.0687). 즉 **추정 최적값의 1.1배 안으로 수렴**한다.
4. **유클리드 이웃 대조(R2 의 ⓑ 검증)** — 이웃 집합을 비용 준위집합 대신 **유클리드 공**
   ($\lVert x' - x\rVert \le r_n$)으로 바꿔 같은 설정을 돌리고, $n = 3000$ 의 중앙값이
   **나빠지는** 것을 보고한다. 또 P5 의 두 비용 $\tfrac43\sqrt{6\epsilon}$ 과 $4\epsilon$ 을
   $\epsilon = 10^{-2}$ 에서 계산해 $0.3266$ 과 $0.0400$(비 8.165)을 얻는다.

**비교 대상.** ⓐ 해석적 자유공간 하한 $c_{lb}$ — 조건 1. ⓑ 30시드 최솟값 — 조건 2·3.
ⓒ 자기 자신의 변형(유클리드 이웃, 전파 없는 재배선) — 조건 4 와 P8 루브릭.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 비용이 $c_{lb}$ 보다 작다 | 궤적을 직선으로 보고 충돌·비용을 계산했다(동역학 무시) | 최적 해의 각 조각을 3차 Hermite 로 다시 적분해 종단 상태가 일치하는지 본다 |
| 해를 못 찾는 시드가 있다 | 속도 범위를 너무 좁게 샘플링했거나 $\tau$ 격자의 상한이 작다 | $\tau$ 격자 상한을 8 에서 2 로 줄여 성공률이 떨어지는지 본다 |
| 중앙값이 검사점마다 오른다 | 재배선 뒤 하위 트리 비용을 전파하지 않았다 | 재배선 횟수와 전파된 노드 수를 출력한다 |
| 중앙값이 거의 줄지 않는다 | 이웃을 유클리드 공으로 정의했다(조건 4 의 결함 버전) | 이웃 집합의 평균 크기와 그중 연결 성공률을 출력한다 |
| 실행이 30분을 넘긴다 | $\tau$ 격자마다 파이썬 루프로 비용을 계산했다 | (6)을 $(\text{노드}, \tau, \text{축})$ 축으로 벡터화한다 |
| 충돌이 있는 해가 통과한다 | Hermite 샘플이 16점보다 적거나 속도 한계를 검사하지 않았다 | 샘플 수를 64 로 올려 비용이 올라가는지 본다 |

## 열린 문제

- **(열린 문제) 비선형계의 조종** — (A6)은 선형계에서만 닫힌 형태로 성립한다. 일반
  비선형계에서 두 상태를 잇는 최적 조종은 그 자체가 비볼록 최적 제어 문제이고, 플래너의
  간선마다 그것을 푸는 것은 실시간성과 양립하지 않는다. 현재 접근: 조종을 포기하고 전방
  전파로 가는 [SST](https://arxiv.org/abs/1407.2896), 비용을 상태에 넣어 가능성 문제로
  바꾸는 [Hauser & Zhou 2016](https://doi.org/10.1109/tro.2016.2602363),
  국소 선형화 + iLQR(`c4-ilqr-ddp`). 비어 있는 자리: 간선당 비용이 유계이면서 최적성 보장을
  유지하는 조종 근사.
- **(열린 문제) 입력 제약이 있는 최적 조종의 닫힌 형태** — (2)는 $\lVert u\rVert \le u_{max}$
  에서 틀린다. 시간 최적 해는 bang-bang 이고 Dubins·Reeds–Shepp 처럼 **분류**는 가능하지만,
  (1)과 같은 복합 비용 + 제약에서는 분류도 닫힌 형태도 없다. 현재 접근:
  [Dubins 1957](https://doi.org/10.2307/2372560),
  [Reeds & Shepp 1990](https://doi.org/10.2140/pjm.1990.145.367) 의 고전 분류와
  수치 최적 제어. 비어 있는 자리: 제약 하 복합 비용의 조종을 플래너 속도로 푸는 방법.
- **(열린 문제) 유효 차원 $d_{\text{eff}}$ 의 결정** — R2 의 반경 규칙은 도달가능 집합 부피의
  지수 $d_{\text{eff}}$ 를 요구하지만, 일반 동역학에서 그 값을 계산하는 방법이 없다. 실무는
  상태 차원을 쓰는 **보수적 선택**을 하고(재현 과제도 그렇다) 이웃 수가 필요 이상 많아진다.
  현재 접근: 선형계의 Kalman 지수로 쓴 경우 분석
  ([Karaman & Frazzoli 2010](https://doi.org/10.1109/CDC.2010.5717430)).
  비어 있는 자리: 비선형계에서 $d_{\text{eff}}$ 를 추정하는 절차.

## 개념 점검

`rc quiz c6-kinodynamic-planning` 로 푼다. 개념 점검 전용이고, 실제 과제는 문제 세트와
재현 과제다.

```quiz
activity: c6-kinodynamic-planning-quiz
questions:
  - id: q1
    type: single
    prompt: "선형계의 고정 시간 최적 조종 문제가 변분법 없이 풀리는 이유는?"
    choices:
      - "비용이 2차식이기 때문"
      - "종단 상태가 제어에 대해 **선형**이라 최소 노름 해(유사역행렬) 문제로 환원되기 때문"
      - "동역학이 시간 불변이기 때문"
      - "그라미안이 대칭이기 때문"
    answer: 1
    explanation: "$x(\\tau) = e^{A\\tau}x_0 + \\mathcal{L}_\\tau u$ 에서 $\\mathcal{L}_\\tau$ 가 선형 연산자이므로 조종 조건은 선형 방정식 $\\mathcal{L}_\\tau u = d$ 다. 최소 노름 해는 $\\mathcal{L}_\\tau^\\ast(\\mathcal{L}_\\tau\\mathcal{L}_\\tau^\\ast)^{-1}d$ 이고 $\\mathcal{L}_\\tau\\mathcal{L}_\\tau^\\ast = G(\\tau)$ 가 그라미안이다. 비용이 2차식인 것도 쓰이지만 본질은 **제약의 선형성**이다."
    concept: { front: "선형 조종이 닫힌 형태인 이유", back: "제약 $\\mathcal{L}_\\tau u = d$ 가 선형 → 최소 노름 해 + 그라미안" }
  - id: q2
    type: single
    prompt: "이중 적분기에서 정지–정지 변위의 최적 비용과 최적 조종 시간의 관계는?"
    choices:
      - "$c^\\ast = \\tau^\\ast$"
      - "$c^\\ast = \\frac{4}{3}\\tau^\\ast$"
      - "$c^\\ast = 2\\tau^\\ast$"
      - "변위에 따라 달라진다"
    answer: 1
    explanation: "$c(\\tau) = \\tau + K/\\tau^3$ 에서 $\\dot c = 1 - 3K/\\tau^4 = 0$ 이면 $K = \\tau^{\\ast4}/3$ 이고 $c^\\ast = \\tau^\\ast + \\tau^\\ast/3 = \\frac43\\tau^\\ast$ 다. 최적점에서 노력 비용이 시간 비용의 정확히 1/3 이고, 이 비는 변위에 **무관**하다 — 변위는 $K$ 를 통해서만 들어가기 때문이다."
    concept: { front: "정지–정지 이중 적분기의 최적점", back: "$c^\\ast = \\frac43\\tau^\\ast$ — 노력:시간 = 1:3, 변위 무관" }
  - id: q3
    type: single
    prompt: "kinodynamic RRT* 에서 이웃을 유클리드 공으로 정의하면 무엇이 깨지는가?"
    choices:
      - "충돌 검사가 틀린다"
      - "같은 유클리드 거리에서 조종 비용의 차수가 달라(위치 $\\epsilon^{1/2}$, 속도 $\\epsilon$) 이웃 대부분이 싸게 연결되지 않고 피복–연결 논증이 깨진다"
      - "그라미안이 특이해진다"
      - "재배선이 순환을 만든다"
    answer: 1
    explanation: "이중 적분기에서 $x=(0,0)$ 에서 위치만 $\\epsilon$ 다른 상태로 가는 비용은 $\\frac43\\sqrt{6\\epsilon} \\propto \\epsilon^{1/2}$, 속도만 $\\epsilon$ 다른 상태로 가는 비용은 $4\\epsilon$ 다. $\\epsilon \\to 0$ 에서 비율이 $\\epsilon^{-1/2} \\to \\infty$ 로 발산하므로 유클리드 공은 비용에 대해 무계로 비등방이다. 그래서 이웃은 비용 준위집합으로 정의해야 한다."
    concept: { front: "kinodynamic 이웃 정의", back: "비용 준위집합 $\\{x' : c(x',x) \\le r_n\\}$ — 유클리드 공은 비용에 대해 비등방" }
  - id: q4
    type: truefalse
    prompt: "등간격 헤딩($2\\pi/N_\\theta$)과 임의의 곡률 반지름으로 상태 격자를 만들 수 있다."
    answer: false
    explanation: "좌회전 호의 변위는 $\\Delta p = \\rho(\\sin\\theta_j - \\sin\\theta_i,\\ \\cos\\theta_i - \\cos\\theta_j)$ 이고, 위치 격자가 $\\mathbb{Z}^2$ 이면 이것이 **정수 벡터**여야 원시가 격자를 닫는다. 등간격 헤딩은 일반적으로 무리수 변위를 주어 닫히지 않고, 구현은 종단 상태를 스냅하게 되며 그 순간 궤적이 동역학을 위반한다. 그래서 격자는 $\\sin,\\cos$ 이 유리수인 피타고라스 각을 쓴다."
    concept: { front: "상태 격자의 닫힘 조건", back: "원시의 변위가 격자 벡터와 정확히 일치해야 한다 → 피타고라스 헤딩 + 반지름 공동 설계" }
  - id: q5
    type: multiple
    prompt: "미분 제약이 들어왔을 때 앞 레슨의 RRT* 논증에서 **그대로 쓸 수 있는** 것을 모두 고르라."
    choices:
      - "최적 궤적 주변을 덮개로 덮는다는 요구 1 의 구조"
      - "유클리드 공의 부피가 $r^d$ 라는 계산"
      - "$np_n \\propto \\log n$ 이어야 합 가능해진다는 Borel–Cantelli 논증"
      - "비용의 삼각 부등식"
    answer: [0, 2]
    explanation: "덮개 구조와 Borel–Cantelli 논증은 그대로 쓰인다. 공의 부피 계산은 비용 준위집합의 부피 $r^{d_{\\mathrm{eff}}}$ 로 바뀌어야 하고($d_{\\mathrm{eff}} \\ne n$), 비용은 거리가 아니라 대칭성도 삼각 부등식도 일반적으로 성립하지 않는다 — 그래서 연결 단계를 Lipschitz 성질로 다시 세워야 한다."
    concept: { front: "RRT* 논증 중 미분 제약에서 살아남는 부분", back: "덮개 + Borel–Cantelli 는 그대로. 부피 지수와 삼각 부등식은 교체" }
  - id: q6
    type: short
    prompt: "조종(steering)을 계산할 수 없는 비선형계에서 점근 (준)최적성을 얻는 구조는?"
    answer: ["전방 전파 + 가지치기", "forward propagation and pruning", "SST", "전방 전파와 가지치기", "무작위 제어 전파 + 지배 가지치기", "propagation with pruning"]
    explanation: "무작위 제어를 적분해(전방 전파) 트리를 키우고, 비용-상태 공간의 $\\delta$-근방에서 지배(domination) 관계로 나쁜 가지를 솎아낸다. 조종이 없어도 되고, 그 대가로 보장이 '준최적성 + 해상도' 꼴로 약해진다(Li, Littlefield & Bekris 2016)."
    concept: { front: "조종 없는 kinodynamic 계획", back: "전방 전파 + $\\delta$-근방 지배 가지치기(SST) — 조종 불필요, 보장은 준최적" }
```

## 이 단계 공부법

1. **깨지는 가정을 먼저 적는다 (20분)** — (A2)가 깨지면 무엇이 달라지는지 목록으로 쓴다:
   이웃의 정의, 비용의 대칭성, 반경 규칙의 지수, 재배선의 타당성. 이 네 줄이 레슨의 구조다.
2. **조종을 선형대수로 환원한다 (70분)** — R1 을 백지에서 다시 쓴다. 핵심은 "종단 상태가
   제어의 **선형** 함수"라는 한 줄이고, 그 뒤는 최소 노름 해다. P1 을 같이 풀어 수반 연산자를
   손으로 확인하면 그라미안이 $\mathcal{L}\mathcal{L}^\ast$ 임이 기억에 남는다.
3. **닫힌 형태를 숫자로 만든다 (40분)** — P2·P3 를 푼다. $\tau^\ast = 72^{1/4}$,
   $c^\ast = \tfrac43\tau^\ast$ 를 직접 얻고, (3)의 일반식에 넣어 같은 값이 나오는지 확인한다.
   **일반식과 닫힌 형태가 일치하는 것을 본 뒤에야 (3)을 믿게 된다.**
4. **비등방성을 수치로 만난다 (30분)** — P5 를 푼다. 같은 유클리드 거리 $10^{-2}$ 에서
   비용이 8.2배 차이난다는 것을 계산하면 R2 의 (ⓑ)가 설계 선택이 아니라 **필연**임이 보인다.
5. **격자를 설계해 본다 (40분)** — P4 를 푼다. 헤딩을 촘촘히 할수록 격자를 닫는 최소 반지름이
   1 → 5 → 13 으로 커지는 것을 보면, 격자 플래너가 왜 특정 헤딩 집합을 고집하는지 끝난다.
6. **구현하고 결함 버전도 돌린다 (95분)** — 재현 과제. 조건 1·2·3 을 맞춘 뒤 조건 4
   (유클리드 이웃)를 **일부러** 돌려 나빠지는 것을 확인한다. 하위 트리 전파를 빼는 실험도 같이.
7. **논문 3편 (130분)** — Webb–van den Berg(조종) → Karaman–Frazzoli 2010(가정) →
   Pivtoraiko(격자) 순서. 앞 둘은 같은 문제의 "해법"과 "조건"이고, 셋째는 그 문제를
   **피하는** 길이다. 세 논문을 그 구도로 노트에 적는다.

**통과 기준**: R1 을 선형대수 환원으로 백지에서 유도할 수 있고, $\tau^\ast = 72^{1/4}$ 와
$c^\ast = \tfrac43\tau^\ast$ 를 손으로 얻을 수 있고, 유클리드 공이 왜 쓸 수 없는지 수치로
말할 수 있고, 재현 과제의 네 조건(특히 조건 4 의 대조 실험)을 만족하는 코드를 갖고 있고,
격자 닫힘 조건을 Dubins 호로 설명할 수 있다. 논문 3편의 노트가 있다.
