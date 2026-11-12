---
id: c8-control-as-inference
title: 제어로서의 추론
summary: >-
  최대 엔트로피 RL 의 최적 정책이 볼츠만 분포이고 최적 가치가 soft-max 백업의 고정점임을
  Lagrange 쌍대로 유도하고, 그 soft Bellman 연산자가 수축임을 보인다. 이어서 최적성 변수를
  둔 그래프 모형의 변분 하한이 최대 엔트로피 목적함수와 **정확히 같음**을 보이고, 추론을
  순진하게 하면 동역학이 낙관적으로 휘는 실패 모드를 드러낸다. 마지막으로 자유 에너지에서
  경로 적분 제어와 MPPI 의 가중 평균 갱신을 유도한다.
objectives:
  - 엔트로피 정규화 목적함수에서 볼츠만 정책과 soft-max 백업을 Lagrange 쌍대로 유도할 수 있다.
  - soft Bellman 연산자가 sup-노름 $\gamma$-수축임을 증명하고 $\alpha\to0$ 극한을 설명할 수 있다.
  - 최적성 변수 모형의 ELBO 가 최대 엔트로피 RL 목적함수와 같음을 보일 수 있다.
  - 순진한 추론이 동역학을 낙관적으로 휘게 만드는 지점을 지적하고 그 편향을 수치로 보일 수 있다.
  - KL 제어의 자유 에너지에서 경로 적분 해와 MPPI 의 지수 가중 갱신을 유도할 수 있다.
  - 같은 과제에서 MPPI 와 iLQR 의 비용·표본 교환을 실험으로 도표화할 수 있다.
prerequisites: [c8-mdp-pomdp-bellman, c8-policy-gradient, c8-imitation-learning]
difficulty: 5
estimated_minutes: 540
tags: [control-as-inference, maxent-rl, soft-bellman, mppi, path-integral, research]
activities:
  - id: c8-control-as-inference-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c8-control-as-inference-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c8-control-as-inference-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 165
  - id: c8-control-as-inference-reproduction
    kind: reproduction
    title: 재현 과제 — MPPI 와 iLQR 의 비용·표본 교환 (R2)
    estimated_minutes: 120
  - id: c8-control-as-inference-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
papers:
  - id: levine2018-control-as-inference
    required: true
    role: survey
    note: "§2-4"
  - id: haarnoja2018-sac
    required: true
    role: standard
    note: "§3-4"
  - id: williams2017-mppi
    required: true
    role: standard
    note: "§II-III"
resources:
  - title: "Tedrake, Underactuated Robotics"
    url: https://underactuated.csail.mit.edu/
    kind: book
    note: ch.11 (LQR·DP) 과 ch.8 (궤적 최적화). iLQR 쪽 보조 교재. 전문 무료.
  - title: "Sutton & Barto, Reinforcement Learning: An Introduction (2nd ed.)"
    kind: book
    note: ch.13.5-13.7 (엔트로피 정규화와 actor-critic). 보조 교재. (공식 URL 미확인)
  - title: "Todorov — Efficient computation of optimal actions (2009)"
    url: https://doi.org/10.1073/pnas.0710743106
    kind: paper
    note: 권장. 선형 해결 가능(linearly-solvable) MDP — soft-max 백업이 선형 방정식이 되는 구조.
  - title: "Kappen — Linear theory for control of nonlinear stochastic systems (2005)"
    url: https://doi.org/10.1103/PhysRevLett.95.200201
    kind: paper
    note: 권장. 경로 적분 제어의 물리 쪽 원전(Feynman-Kac 변환).
  - title: "Theodorou, Buchli & Schaal — A generalized path integral control approach to RL (2010)"
    url: https://www.jmlr.org/papers/v11/theodorou10a.html
    kind: paper
    note: 권장. PI^2 — 경로 적분을 정책 개선으로 바꾼 알고리즘.
  - title: "Haarnoja et al. — Reinforcement learning with deep energy-based policies (2017)"
    url: https://arxiv.org/abs/1702.08165
    kind: paper
    note: 권장. soft Q-learning — (2)의 볼츠만 정책을 심층망으로 표현한다.
  - title: "Tassa, Erez & Todorov — Synthesis and stabilization of complex behaviors through online trajectory optimization (2012)"
    url: https://doi.org/10.1109/IROS.2012.6386025
    kind: paper
    note: 권장. iLQR/iLQG 의 정규화와 선탐색 실무.
---

# 제어로서의 추론

## 전제와 기호

`c8-mdp-pomdp-bellman` 의 Bellman 연산자, `c8-policy-gradient` 의 정책 매개화,
`c8-imitation-learning` R5 의 최대 엔트로피 유도를 쓴다. 추가 **권장 선수**:

- 볼록 최적화: 단체 위 엔트로피 최대화의 Lagrange 쌍대, log-sum-exp 의 볼록성과 매끄러움
  (`r0-convex-optimization`).
- 변분 추론: ELBO, KL 발산, 중요도 가중과 Jensen 부등식.
- 수치 최적화: Newton 법, 정규화와 선탐색(`r0-numerical-optimization`), LQR 의 역행 재귀.

표기 추가:

| 기호 | 뜻 |
|---|---|
| $\alpha$ | 온도(temperature). 엔트로피 보너스의 가중. $\alpha\to0$ 이 표준 RL |
| $H(\pi(\cdot\mid s))$ | $-\sum_a \pi(a\mid s)\log\pi(a\mid s)$ |
| $J_\alpha(\pi)$ | $\mathbb{E}_\pi\big[\sum_t \gamma^t\big(r(s_t,a_t) + \alpha H(\pi(\cdot\mid s_t))\big)\big]$ |
| $Q_\alpha, V_\alpha$ | 엔트로피 정규화 가치. $V_\alpha$ 는 (3)의 soft-max |
| $\mathcal{T}_\alpha$ | soft Bellman 최적 연산자((4)) |
| $O_t$ | 최적성 변수(optimality variable). $p(O_t=1\mid s_t,a_t) \propto \exp(r(s_t,a_t)/\alpha)$ |
| $q$ | 변분 분포. 행동에 대해서는 $q(a_t\mid s_t)$, 상태에 대해서는 참 동역학으로 고정 |
| $S(\mathbf{u})$ | 제어열 $\mathbf{u} = (u_0,\dots,u_{H-1})$ 의 누적 비용 |
| $\lambda$ | MPPI 의 온도. $\alpha$ 와 같은 역할을 비용 쪽에서 한다 |
| $w_k$ | MPPI 의 표본 가중. $w_k \propto \exp(-S(\mathbf{u}_k)/\lambda)$ |

**이 레슨의 한 줄.** `c8-mdp-pomdp-bellman` 의 $\max$ 를 **log-sum-exp 로 바꾸면** 제어 문제가
추론 문제가 된다. 그 교체가 왜 정당한지(R1·R2), 무엇을 공짜로 주고(미분 가능성, 탐색,
다봉 해) 무엇을 대가로 받는지(온도 편향, 낙관적 동역학)를 끝까지 따라간다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (최대 엔트로피 최적 정책은 볼츠만 분포) [D3]** — 고정된 $Q$ 에 대해
  $\max_{\pi(\cdot\mid s)}\big[\sum_a \pi(a\mid s)Q(s,a) + \alpha H(\pi(\cdot\mid s))\big]$ 의 해는
  $$
  \pi_\alpha(a\mid s) = \frac{\exp\!\big(Q(s,a)/\alpha\big)}{\sum_{a'}\exp\!\big(Q(s,a')/\alpha\big)}, \tag{1}
  $$
  이고 그때의 최대값은
  $$
  \alpha\log\sum_a \exp\!\big(Q(s,a)/\alpha\big) \;=:\; \operatorname{softmax}_\alpha Q(s,\cdot). \tag{2}
  $$
  즉 **엔트로피 보너스가 $\max$ 를 log-sum-exp 로 매끄럽게 만든다.**
- **R2 (soft Bellman 연산자와 그 고정점) [D3]** —
  $$
  V_\alpha(s) = \alpha\log\sum_a \exp\!\Big(\frac{r(s,a) + \gamma\sum_{s'}P(s'\mid s,a)V_\alpha(s')}{\alpha}\Big), \tag{3}
  $$
  $$
  (\mathcal{T}_\alpha v)(s) := \alpha\log\sum_a \exp\!\Big(\frac{r(s,a) + \gamma (Pv)(s,a)}{\alpha}\Big) \tag{4}
  $$
  는 sup-노름에서 $\gamma$-수축이므로 (3)의 해가 유일하다. 그 $V_\alpha$ 는 (1)의 정책의
  **실제 엔트로피 정규화 가치와 정확히 같고**, $0 \le V_\alpha - V^\* \le \frac{\alpha\log m}{1-\gamma}$
  이므로 $\alpha\to0$ 에서 표준 최적 가치로 수렴한다.
- **R3 (변분 추론과의 동등성) [D3]** — 최적성 변수 $O_{0:T-1}$ 를 둔 그래프 모형에서, 변분 분포의
  **상태 전이를 참 동역학으로 고정**하고 행동만 $q(a_t\mid s_t)$ 로 두면
  $$
  \log p(O_{0:T-1}=1) \;\ge\; \mathbb{E}_q\!\Big[\sum_t \big(r(s_t,a_t)/\alpha + H(q(\cdot\mid s_t))\big)\Big]
    \;=\; \frac{1}{\alpha}J_\alpha(q) \tag{5}
  $$
  이고, 등호는 $q$ 가 (1)일 때 성립한다. **최대 엔트로피 RL 은 이 ELBO 를 최대화하는 것과
  같은 문제다.**
- **R4 (순진한 추론은 동역학을 낙관적으로 휘게 한다) [D2]** — 상태 전이도 사후분포로 바꾸면
  $p(s_{t+1}\mid s_t,a_t,O=1) \propto P(s_{t+1}\mid s_t,a_t)\exp(V(s_{t+1})/\alpha)$ 가 되어
  **환경이 학습자에게 유리하게 움직인다고 가정**하는 셈이다. 그 결과 백업의 $\max$ 가 아니라
  **다음 상태에 대한 log-sum-exp** 가 등장하고, 값이 체계적으로 과대평가된다 — 재현 과제에서
  그 편향이 $\alpha$ 가 작아질수록 커지는 것을 측정한다($\alpha=1$ 에서 $0.107$,
  $\alpha=0.01$ 에서 $1.448$).
- **R5 (경로 적분 제어와 MPPI) [D2]** — 제어열의 사전 분포 $p(\mathbf{u})$ 와 비용
  $S(\mathbf{u})$ 에 대해 자유 에너지 하한
  $-\lambda\log\mathbb{E}_{p}\big[e^{-S/\lambda}\big] \le \mathbb{E}_q[S] + \lambda\,
  D_{\mathrm{KL}}(q\Vert p)$ 를 최소화하는 $q^\star$ 는
  $$
  q^\star(\mathbf{u}) = \frac{1}{Z}\,p(\mathbf{u})\exp\!\big(-S(\mathbf{u})/\lambda\big), \tag{6}
  $$
  이고, $p$ 가 평균 $\bar{\mathbf{u}}$ 의 가우시안이면 $q^\star$ 의 평균은 **지수 가중 평균**
  $\bar{\mathbf{u}} + \sum_k w_k\,\boldsymbol{\epsilon}_k$, $w_k \propto \exp(-S_k/\lambda)$ 로
  추정된다. 이것이 MPPI 의 갱신식이다.

## 유도

### R1 — 볼츠만 정책과 log-sum-exp

고정된 $s$ 와 $Q(s,\cdot)$ 에 대해 단체 $\Delta(\mathcal{A})$ 위의 문제

$$
\max_{\pi \ge 0,\ \sum_a \pi(a) = 1}\; \sum_a \pi(a)Q(s,a) - \alpha\sum_a \pi(a)\log\pi(a)
$$

를 푼다. Lagrangian 은 $\mathcal{L} = \sum_a \pi(a)Q(s,a) - \alpha\sum_a\pi(a)\log\pi(a)
+ \nu(1-\sum_a\pi(a))$ 이고

$$
\frac{\partial\mathcal{L}}{\partial\pi(a)} = Q(s,a) - \alpha\log\pi(a) - \alpha - \nu = 0
  \;\Longrightarrow\; \pi(a) = \exp\!\Big(\frac{Q(s,a) - \alpha - \nu}{\alpha}\Big).
$$

$\sum_a\pi(a)=1$ 로 $\nu$ 를 정하면 (1)이다($\pi > 0$ 이므로 비음 제약은 자동으로 만족된다 —
엔트로피의 $\log$ 가 경계를 밀어낸다). 최적값을 대입하면

$$
\sum_a \pi_\alpha(a)Q(s,a) + \alpha H(\pi_\alpha)
  = \sum_a \pi_\alpha(a)\Big[Q(s,a) - \alpha\log\pi_\alpha(a)\Big]
  = \sum_a \pi_\alpha(a)\cdot \alpha\log\!\sum_{a'}e^{Q(s,a')/\alpha} ,
$$

마지막 등식은 (1)에서 $Q(s,a) - \alpha\log\pi_\alpha(a) = \alpha\log\sum_{a'}e^{Q(s,a')/\alpha}$ 가
**$a$ 와 무관**하기 때문이다. $\sum_a\pi_\alpha(a)=1$ 이므로 (2)가 된다.

**읽는 법.** $\alpha\log\sum_a e^{Q/\alpha}$ 는 $\alpha\to0$ 에서 $\max_a Q$ 로, $\alpha\to\infty$
에서 $\alpha\log m + \bar{Q}$ 로 간다. 즉 온도가 **탐욕과 균등 사이를 연속으로 잇는다**.
그리고 $\max_a Q \le \operatorname{softmax}_\alpha Q \le \max_a Q + \alpha\log m$ 이므로 편향이
위로만, 최대 $\alpha\log m$ 만큼 생긴다.

**가정이 깨지는 곳.** 행동 집합이 무한(연속)이면 $\sum_a$ 가 적분이 되고 분할함수가 닫힌
형태를 갖지 않는다. 가우시안 정책으로 제한하면 (1)이 더 이상 **정확한** 최적해가 아니고,
SAC 가 하는 것이 그 근사다(정책 투영). 또 $\alpha$ 가 매우 작으면 $e^{Q/\alpha}$ 가 수치적으로
넘치므로 구현은 반드시 $\max$ 를 뽑아내는 log-sum-exp 안정화를 써야 한다.

### R2 — soft Bellman 연산자의 수축성과 극한

**수축성.** $\operatorname{softmax}_\alpha$ 가 각 인자에 대해 1-Lipschitz 임을 쓴다. 실제로

$$
\frac{\partial}{\partial Q(a)}\,\alpha\log\sum_{a'}e^{Q(a')/\alpha}
  = \frac{e^{Q(a)/\alpha}}{\sum_{a'}e^{Q(a')/\alpha}} = \pi_\alpha(a) \ge 0,
  \qquad \sum_a \pi_\alpha(a) = 1,
$$

즉 **기울기가 확률벡터**다. 따라서 평균값 정리로 임의의 $u, v$ 에 대해

$$
\big\lvert \operatorname{softmax}_\alpha u - \operatorname{softmax}_\alpha v \big\rvert
  \le \max_a \lvert u(a) - v(a)\rvert , \tag{7}
$$

`c8-mdp-pomdp-bellman` 의 (7)과 **같은 역할**이다. 그 다음은 글자 그대로 같다:
$\lvert(\mathcal{T}_\alpha u)(s) - (\mathcal{T}_\alpha v)(s)\rvert \le \max_a \gamma\lvert (Pu)(s,a)
- (Pv)(s,a)\rvert \le \gamma\lVert u-v\rVert_\infty$. Banach 로 (3)의 해가 유일하다.

**고정점이 (1)의 정책의 실제 가치다.** $V_\alpha$ 를 (3)의 해, $\pi_\alpha$ 를 (1)이라 하면 R1 의
최적값 등식이 바로 $V_\alpha(s) = \sum_a \pi_\alpha(a\mid s)\big[Q_\alpha(s,a) -
\alpha\log\pi_\alpha(a\mid s)\big]$ 를 주고, 이는 $\pi_\alpha$ 의 엔트로피 정규화 Bellman
기대 방정식이다. 그 방정식의 해가 유일하므로 $V_\alpha = V^{\pi_\alpha}_\alpha$ 다.
(재현 과제 조건 1 에서 이 등식을 $10^{-14}$ 수준으로 확인한다.)

**$\alpha\to0$ 극한.** (2)의 양쪽 부등식에 $\mathcal{T}_\alpha$ 와 $\mathcal{T}^\*$ 를 대입하면
$\mathcal{T}^\* v \le \mathcal{T}_\alpha v \le \mathcal{T}^\* v + \alpha\log m$ 이다. 두 연산자가
모두 $\gamma$-수축이므로 고정점의 차가

$$
0 \;\le\; V_\alpha - V^\* \;\le\; \frac{\alpha\log m}{1-\gamma} \tag{8}
$$

로 묶인다(수축 사상의 고정점이 연산자 섭동에 대해 $1/(1-\gamma)$ 로 안정하다는 표준 논증).
$\gamma=0.9$, $m=3$, $\alpha=0.01$ 에서 상한은 $0.110$ 이고 **실측 차는 $0.0107$** 다 —
상한이 10배 느슨하다.

**가정이 깨지는 곳.** (8)은 온도가 **고정**일 때의 진술이다. SAC 처럼 $\alpha$ 를 제약
($H \ge \bar{H}$)으로 자동 조정하면 $\alpha$ 가 상태·시점에 따라 달라져 (3)의 고정점 논증이
그대로 적용되지 않는다. 또 $\alpha$ 가 크면 (8)의 편향이 커서 **엔트로피 보너스가 과제를
바꾼다** — 보고된 성능을 표준 RL 과 비교할 때 반드시 $\alpha$ 를 함께 보고해야 하는 이유다.

### R3 — ELBO 가 최대 엔트로피 목적함수와 같다

**모형.** 상태·행동 위에 사전 분포를 두고, 각 시점에 이진 **최적성 변수** $O_t$ 를 붙여
$p(O_t = 1\mid s_t,a_t) = \exp\big(r(s_t,a_t)/\alpha\big)$ (보상을 $\le 0$ 으로 이동해 확률로
읽을 수 있게 한다). 행동 사전은 균등으로 둔다. 우리가 원하는 것은 "모든 시점이 최적이었다"는
증거의 로그 가능도 $\log p(O_{0:T-1}=1)$ 이다.

**변분 하한.** 변분 분포를 $q(s_{0:T},a_{0:T-1}) = \rho_0(s_0)\prod_t q(a_t\mid s_t)
P(s_{t+1}\mid s_t,a_t)$ 로 둔다 — **상태 전이는 참 동역학으로 고정**하는 것이 핵심이다.
Jensen 으로

$$
\log p(O_{0:T-1}=1) \;\ge\; \mathbb{E}_q\!\left[\log\frac{p(s_{0:T},a_{0:T-1},O=1)}{q(s_{0:T},a_{0:T-1})}\right].
$$

분자는 $\rho_0\prod_t \big[\tfrac{1}{m}P(s_{t+1}\mid s_t,a_t)e^{r_t/\alpha}\big]$ 이고 분모는
$\rho_0\prod_t\big[q(a_t\mid s_t)P(s_{t+1}\mid s_t,a_t)\big]$ 다. **$\rho_0$ 와 $P$ 가 약분된다.**
남는 것은

$$
\mathbb{E}_q\!\Big[\sum_t \Big(\frac{r(s_t,a_t)}{\alpha} - \log\big(m\,q(a_t\mid s_t)\big)\Big)\Big]
  = \mathbb{E}_q\!\Big[\sum_t \Big(\frac{r_t}{\alpha} + H\big(q(\cdot\mid s_t)\big)\Big)\Big] - T\log m ,
$$

즉 상수를 빼면 (5)다. $\alpha$ 를 곱하면 정확히 $J_\alpha(q)$ 다. 등호 조건은 변분 분포가
정확한 사후분포 $p(a_t\mid s_t, O_{t:T-1}=1)$ 일 때이고, 그 사후분포가 R1 의 (1)이다 — 뒤에서
앞으로 계산하면 (3)의 soft 백업이 그대로 나온다.

**무엇을 얻는가.** ① 탐색이 목적함수에 들어온다(엔트로피 항). ② 다봉 해가 자연스럽다
(사후분포가 다봉이면 정책도 다봉). ③ 미분 가능한 $\operatorname{softmax}$ 로 바뀌어 1차
방법과 궁합이 좋다. ④ 역강화학습(`c8-imitation-learning` R5)과 **같은 지수족**이 나와 두
문제를 한 틀에서 본다.

**가정이 깨지는 곳.** 보상을 $r \le 0$ 으로 옮겨야 $e^{r/\alpha}$ 가 확률이다. 이동은 가치에
상수를 더하므로 최적 정책을 바꾸지 않지만(`c8-imitation-learning` R4 의 ⓐ·ⓑ), 할인이 있으면
상수 이동이 $1/(1-\gamma)$ 로 증폭되어 **수치 규모**가 달라진다. 또 (5)는 유한 지평으로 썼다 —
할인 무한 지평은 $O_t$ 의 수를 기하분포로 두거나 할인을 사전에 넣어야 한다.

### R4 — 순진한 추론의 낙관적 동역학

변분 분포에서 **상태 전이까지** 자유롭게 두면 ELBO 는 더 커진다(자유도가 늘었으므로).
그 최적해는

$$
q^\star(s_{t+1}\mid s_t,a_t) \;\propto\; P(s_{t+1}\mid s_t,a_t)\,\exp\big(V(s_{t+1})/\alpha\big),
$$

즉 **좋은 결과로 가는 전이의 확률을 키운다.** 그러면 백업이

$$
V_{\mathrm{opt}}(s) = \operatorname{softmax}_\alpha\Big[r(s,a)
  + \underbrace{\alpha\log\sum_{s'}P(s'\mid s,a)\exp\big(\gamma V_{\mathrm{opt}}(s')/\alpha\big)}_{\text{다음 상태에 대한 soft-max}}\Big] \tag{9}
$$

가 되어, 기댓값 $\sum_{s'}P V$ 가 **log-sum-exp 로 바뀐다**. Jensen 으로
$\alpha\log\mathbb{E}[e^{\gamma V/\alpha}] \ge \gamma\mathbb{E}[V]$ 이므로
$V_{\mathrm{opt}} \ge V_\alpha$ 이고, 그 차가 **위험 추구(risk-seeking) 편향**이다.
확률적 환경에서 "운이 좋을 경우"를 계획에 반영하는 것이므로 로봇에서는 그대로 쓸 수 없다.

편향의 크기는 분산과 $1/\alpha$ 에 비례한다($\log\mathbb{E}[e^{X}] \approx \mathbb{E}[X]
+ \tfrac12\mathrm{Var}(X)$ 를 $X = \gamma V/\alpha$ 에 쓰면 $\tfrac{\gamma^2}{2\alpha}\mathrm{Var}(V)$).
따라서 **온도를 낮출수록 편향이 커진다** — 재현 과제에서 $\alpha$ 를 $1 \to 0.01$ 로 낮추며
편향이 $0.107 \to 1.448$ 로 커지는 것을 측정한다.

**가정이 깨지는 곳.** 결정론 동역학에서는 $\mathrm{Var}(V) = 0$ 이므로 (9)와 (3)이 같다 —
**편향이 사라진다**. 그래서 결정론 시뮬레이터에서 개발한 방법이 확률적 실기에서 깨지는 일이
생긴다. 반대로 변분 분포를 참 동역학으로 고정하면(R3) 편향이 없지만 ELBO 가 더 느슨하다 —
**느슨한 하한을 고르는 것이 올바른 선택**인 드문 예다.

### R5 — 자유 에너지에서 MPPI 까지

**자유 에너지 부등식.** 임의의 분포 $q$ 와 사전 $p$ 에 대해

$$
-\lambda\log\mathbb{E}_{p}\big[e^{-S(\mathbf{u})/\lambda}\big]
  \;\le\; \mathbb{E}_q\big[S(\mathbf{u})\big] + \lambda\,D_{\mathrm{KL}}(q\Vert p) \tag{10}
$$

가 성립한다(Donsker–Varadhan). 증명은 우변에서 좌변을 빼면 $\lambda D_{\mathrm{KL}}(q\Vert q^\star)
\ge 0$ 이 되는 것을 확인하는 것이고, 등호는 $q = q^\star$ 즉 (6)일 때다. 직접 확인하자:

$$
\mathbb{E}_q[S] + \lambda D_{\mathrm{KL}}(q\Vert p)
  = \lambda\,\mathbb{E}_q\!\left[\log\frac{q}{p\,e^{-S/\lambda}}\right]
  = \lambda\,\mathbb{E}_q\!\left[\log\frac{q}{q^\star}\right] - \lambda\log Z ,
$$

여기서 $Z = \mathbb{E}_p[e^{-S/\lambda}]$ 다. 첫 항이 $\lambda D_{\mathrm{KL}}(q\Vert q^\star)\ge0$
이고 둘째 항이 (10)의 좌변이므로 끝난다.

**MPPI 갱신.** $p$ 를 평균 $\bar{\mathbf{u}}$, 공분산 $\Sigma$ 의 가우시안으로 두고 (6)의
평균을 중요도 가중으로 추정한다. $\mathbf{u}_k = \bar{\mathbf{u}} + \boldsymbol{\epsilon}_k$,
$\boldsymbol{\epsilon}_k \sim \mathcal{N}(0,\Sigma)$ 를 $K$ 개 뽑으면

$$
\mathbb{E}_{q^\star}[\mathbf{u}] \;\approx\; \bar{\mathbf{u}} + \sum_{k=1}^{K} w_k\,\boldsymbol{\epsilon}_k,
  \qquad w_k = \frac{\exp\big(-(S_k - S_{\min})/\lambda\big)}{\sum_{j}\exp\big(-(S_j - S_{\min})/\lambda\big)} , \tag{11}
$$

$S_{\min}$ 을 빼는 것은 수치 안정화이며 $w$ 를 바꾸지 않는다. 이것을 반복하는 것이 MPPI 이고,
**$\lambda\to0$ 에서 $w$ 가 최저 비용 표본 하나에 집중**해 임의 탐색(random shooting)의
"가장 좋은 표본 고르기"가 된다. $\lambda\to\infty$ 에서는 $w$ 가 균등해져 갱신이 0 으로 간다.

**iLQR 과의 대비.** iLQR 은 같은 문제를 **2차 전개 + 역행 재귀**로 푼다. 미분을 쓰므로
표본이 필요 없고 수렴이 빠르지만, 미분 가능성과 국소 볼록성을 요구하고 국소 최소점에 갇힌다.
MPPI 는 미분을 쓰지 않아 접촉·불연속 비용에도 쓸 수 있지만 표본 수가 차원에 민감하다.
재현 과제가 이 교환을 같은 과제에서 측정한다.

**가정이 깨지는 곳.** (11)은 $q^\star$ 의 평균을 쓰지만 $q^\star$ 가 **다봉**이면 평균이
어느 봉우리에도 속하지 않는 제어열이 될 수 있다 — 두 개의 회피 경로의 평균이 장애물을
정면으로 통과하는 고전적 실패다. 또 $\lambda$ 가 비용 규모에 비해 작으면 유효 표본 수가
1 로 붕괴하고(`c8-offline-rl` R5 의 ESS 와 같은 현상), 크면 갱신이 사라진다.

## 증명 스케치

### R1·R2 — 볼츠만 최적성과 soft 수축 [D3]

**가설** H1: $\mathcal{A}$ 유한($\lvert\mathcal{A}\rvert = m$), 보상 유계. H2: $0\le\gamma<1$.
H3: $\alpha > 0$.
**결론** C1: (1)과 (2). C2: $\mathcal{T}_\alpha$ 가 $\gamma$-수축, (3)의 해 유일.
C3: $V_\alpha = V^{\pi_\alpha}_\alpha$ 와 (8).

**전략**: C1 은 **단체 위 Lagrange 쌍대**. C2 는 **$\operatorname{softmax}$ 의 기울기가 확률벡터**
라는 사실로 1-Lipschitz 를 얻고 `c8-mdp-pomdp-bellman` 의 논증을 재사용. C3 은 연산자 섭동의
고정점 안정성.

1. 단체 위 엔트로피 정규화 선형 문제의 1차 조건 → (1). 쓰는 것: H3($\alpha>0$ 이어야 $\log$ 항이
   존재), H1(유한 합).
2. (1)을 대입하고 $Q - \alpha\log\pi_\alpha$ 가 $a$ 와 무관함을 쓴다 → (2).
3. $\partial\operatorname{softmax}/\partial Q(a) = \pi_\alpha(a)$ 가 확률벡터 → (7) → C2.
   쓰는 것: H2.
4. R1 의 최적값 등식이 $\pi_\alpha$ 의 엔트로피 Bellman 기대 방정식과 일치 → C3 의 첫 부분.
5. $\mathcal{T}^\* v \le \mathcal{T}_\alpha v \le \mathcal{T}^\* v + \alpha\log m$ 과 고정점 안정성
   → (8). 쓰는 것: H1(그래서 $\log m$ 이 유한).

**가설 하나를 지우면**: H3 에서 $\alpha\to0$ 을 허용하면 1단계의 $\log\pi$ 항이 사라져 해가
단체의 **꼭짓점**(결정론 정책)이 되고 (1)이 정의되지 않는다 — 극한은 (8)로 다루어야 한다.
H1 에서 $m\to\infty$ 면 (8)의 상한이 무한이 되어 온도 편향을 통제할 수 없다. 연속 행동에서
$\log m$ 을 **미분 엔트로피**로 바꾸면 부호조차 보장되지 않는다.

생략: 연속 행동에서의 분할함수 존재와 교환 조건은 Haarnoja et al. 2017 §3 과
Levine 2018 §2.3.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1·R2)** (2)의 양쪽 부등식
$\max_a Q \le \operatorname{softmax}_\alpha Q \le \max_a Q + \alpha\log m$ 을 증명하고,
그것으로 (8)을 유도하라. $\gamma = 0.9$, $m = 3$ 에서 $\alpha$ 를 얼마로 두면 편향 상한이
$0.01$ 이하가 되는가?
*해답 스케치*: 하한은 한 항만 남기면 되고, 상한은 모든 항을 $\max$ 로 올리면 된다. (8)은
두 수축 연산자의 고정점 차가 연산자 차의 $1/(1-\gamma)$ 배로 묶인다는 표준 논증이다.
$\alpha\log 3/(1-0.9) \le 0.01 \Rightarrow \alpha \le 0.01\cdot0.1/\log 3 = 9.1\times10^{-4}$.

**P2 (증명, ★★★, R3)** (5)를 유도하고, 등호가 $q$ 가 정확한 사후분포일 때 성립함을 보이라.
그 다음 변분 분포에서 상태 전이를 자유롭게 두면 ELBO 가 **더 커지지만** 그 해가 (9)의 낙관적
백업임을 보여라.
*전략과 핵심 부등식*: ELBO 의 차가 $D_{\mathrm{KL}}(q\Vert p(\cdot\mid O=1))$ 이므로 등호는
KL 이 0 일 때다. 상태 전이를 자유롭게 두면 같은 1차 조건이 $q^\star(s'\mid s,a)\propto
P\,e^{V/\alpha}$ 를 주고, 그것을 ELBO 에 다시 넣으면 (9)가 나온다. 전개는 숨긴다.

**P3 (계산, ★, R2·R4)** $\gamma=0.9$, $m=3$ 인 작은 MDP 에서 $\alpha = 1, 0.1, 0.01$ 의 (8)
상한을 계산하고, 측정된 실제 차 $V_\alpha - V^\*$ 가 상한의 몇 분의 1 인지 구하라.
또 $\alpha$ 가 작아질 때 (9)의 낙관 편향이 **커지는** 이유를 2차 전개로 설명하라.
*정답*: 상한 $\alpha\log 3/(1-\gamma) = 10.986\,\alpha$ 이므로 $10.986,\ 1.0986,\ 0.10986$
(허용오차 $10^{-3}$). 측정값은 $\alpha=0.01$ 에서 $0.0107$ 이므로 상한의 약 $1/10$ 이다.
낙관 편향은 $\log\mathbb{E}[e^{\gamma V/\alpha}] \approx \gamma\mathbb{E}[V]/\alpha
+ \tfrac{\gamma^2}{2\alpha^2}\mathrm{Var}(V)$ 에 $\alpha$ 를 곱하면
$\gamma\mathbb{E}[V] + \tfrac{\gamma^2}{2\alpha}\mathrm{Var}(V)$ — 두 번째 항이 $1/\alpha$ 로 커진다.
검산: 측정값 $0.107$ ($\alpha=1$) 과 $1.448$ ($\alpha=0.01$) 의 비가 $\mathrm{Var}$ 고정 가정의
$100$ 배보다 **작은** 이유를 한 줄로 쓴다($V$ 자체가 $\alpha$ 에 따라 변하므로).

**P4 (구현, ★★, R5)** MPPI 와 iLQR 을 같은 진자 스윙업 과제에 구현해 비용을 **롤아웃 수**의
함수로 도표화하라. MPPI 는 $\lambda$ 와 표본 수 $K$ 를, iLQR 은 정규화와 선탐색을 조정한다.
*루브릭*: ⓐ 두 방법의 비용 함수·지평·초기 제어열이 **동일**하다 ⓑ 가로축을 반복 수가 아니라
**롤아웃 수(또는 동역학 호출 수)** 로 잡았다 — iLQR 의 유한차분 야코비안 비용을 세지 않으면
비교가 불공정하다 ⓒ MPPI 의 가중에서 $S_{\min}$ 을 빼는 안정화를 넣었다 ⓓ $\lambda$ 를 비용
규모에 맞춰 조정했고 유효 표본 수를 함께 보고했다 ⓔ iLQR 의 선탐색 실패 시 정규화를 키우는
분기를 구현했다.

**P5 (반례, ★★, R5)** "MPPI 는 표본을 늘리면 항상 좋아진다"는 주장이 틀림을 보이라.
$\lambda$ 가 비용 규모에 비해 너무 작을 때 $K$ 를 늘려도 개선되지 않는(또는 나빠지는) 예를
만들고, 그 원인을 유효 표본 수로 설명하라.
*성질 체크리스트*: ⓐ $\lambda \ll$ 비용 표준편차면 $w$ 가 최저 비용 표본 하나에 붕괴한다
ⓑ 그러면 갱신이 "최저 비용 표본의 잡음"이 되어 **분산이 큰 임의 탐색**과 같다
ⓒ $K$ 를 늘리면 최저 비용 표본이 더 극단적이 되어 갱신이 더 흔들릴 수 있다
ⓓ 진단은 $\mathrm{ESS} = 1/\sum_k w_k^2$ 를 출력하는 것이고, 처방은 $\lambda$ 를 비용 분산에
맞춰 적응시키는 것이다.

**P6 (논문, ★★, R3·R4·R5)** Levine 2018(§2–4), SAC(§3–4), MPPI(§II–III)를 읽고 각각 3문장
이내로 쓰라: (i) Levine 2018 이 "낙관적 동역학" 문제를 어떻게 정리하고 무엇을 처방하는가,
(ii) SAC 가 (1)의 볼츠만 정책을 가우시안으로 투영할 때 생기는 간극과 그 대가,
(iii) MPPI 의 정보이론적 유도에서 (10)에 대응하는 식과 $\lambda$ 의 역할.
*채점 루브릭*: (i) 변분 분포의 상태 전이를 참 동역학으로 고정한다는 처방을 짚으면 통과.
(ii) 투영이 ELBO 를 느슨하게 만들고 다봉 해를 잃는다는 점(그리고 reparameterization 기울기로
그 대가를 치른다). (iii) 자유 에너지/Donsker–Varadhan 부등식과 $\lambda$ 가 KL 벌점의 가중
(= 탐색 폭)이라는 점. "표본을 가중 평균한다"만 쓰면 미달.

**P7 (유도, ★★, R5)** (10)을 직접 증명하고, $p$ 가 가우시안일 때 (6)의 평균이 (11)의 가중
평균으로 추정되는 이유를 중요도 가중으로 설명하라. $\lambda\to0$ 과 $\lambda\to\infty$ 의
극한에서 갱신이 각각 무엇이 되는가?
*해답 스케치*: $\mathbb{E}_q[S] + \lambda D_{\mathrm{KL}}(q\Vert p) = \lambda
D_{\mathrm{KL}}(q\Vert q^\star) - \lambda\log Z$ 를 쓰면 끝난다. (11)은 $q^\star/p = e^{-S/\lambda}/Z$
를 중요도 가중으로 보는 것이다. $\lambda\to0$ 은 최저 비용 표본 선택(random shooting),
$\lambda\to\infty$ 는 갱신 0.

## 논문 읽기

**필독 3편.** 각 논문에 고정 질문 10개로 1페이지 노트를 쓴다(`lesson-standard.md` §5).
3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Levine, "Reinforcement learning and control as probabilistic inference: tutorial and
   review" (2018, arXiv)** — 역할: `서베이(survey)`. <https://arxiv.org/abs/1805.00909> — §2-4.
   읽는 이유: R1-R4 가 이 글의 체계이고, 특히 낙관적 동역학 문제와 그 처방이 §4 에 정리돼 있다.
   추가 질문: ⓐ 저자가 구분하는 "정확한 추론"과 "변분 추론"의 차이가 (3)과 (9) 중 어디에
   대응하는가? ⓑ 할인 $\gamma$ 를 그래프 모형에 넣는 방법으로 저자가 제시하는 것은 무엇인가?
2. **Haarnoja, Zhou, Abbeel & Levine, "Soft actor-critic" (2018, ICML)** — 역할:
   `표준(standard)`. <https://arxiv.org/abs/1801.01290> — §3-4.
   읽는 이유: 연속 행동에서 (1)을 가우시안으로 **투영**하는 실제 방법이고, 온도 자동 조정이
   (8)의 편향을 어떻게 다루는지 보는 사례다.
   추가 질문: ⓐ 정책 개선 단계의 KL 최소화가 (1)과 정확히 어떻게 다른가(투영 오차)?
   ⓑ 온도를 제약으로 바꾸면 R2 의 고정점 논증 중 무엇이 성립하지 않게 되는가?
3. **Williams, Aldrich & Theodorou, "Model predictive path integral control: from theory to
   parallel computation" (2017, JGCD)** — 역할: `표준(standard)`.
   <https://doi.org/10.2514/1.G001921> — §II-III.
   읽는 이유: R5 의 (10)·(11)이 이 논문의 정보이론적 유도다.
   추가 질문: ⓐ 저자들의 자유 에너지 유도에서 제어 비용과 상태 비용이 분리되는 자리는?
   ⓑ 실시간 구현에서 표본 수와 지평을 고르는 기준을 논문은 어떻게 제시하는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU **5분 이내**(순수 Python 루프 약 1억
동역학 호출), 메모리 200 MB 이내, numpy 만. 데이터는 필요 없다.

두 부분으로 나뉜다. **A 는 표 형식 soft Bellman 검증**(이론이 정확히 맞는지), **B 는 MPPI 대
iLQR 비교**(실무 교환이 어떻게 나오는지)다. A 를 먼저 통과시킨 뒤 B 로 간다.

**A. 표 형식 soft Bellman.** $\lvert\mathcal{S}\rvert=12$, $\lvert\mathcal{A}\rvert=3$,
$\gamma=0.9$, 전이는 Dirichlet(0.5), 보상은 $U(0,1)$ 로 생성한다. (3)의 soft 가치 반복, (1)의
볼츠만 정책, 그 정책의 엔트로피 정규화 가치(선형 해), 표준 가치 반복, 그리고 (9)의 낙관적
반복을 모두 구현한다.

**B. 진자 스윙업.** $\dot\omega = \tfrac{3g}{2l}\sin\theta + \tfrac{3}{ml^2}u$, 오일러 적분
$\Delta t = 0.05$, $m=l=1$, $u\in[-5,5]$, 지평 $H=50$, 초기 상태 $(\theta,\omega)=(\pi,0)$.
비용은 스텝마다 $\mathrm{wrap}(\theta)^2 + 0.1\omega^2 + 0.001u^2$ 이고 종단 비용은
$10(\mathrm{wrap}(\theta)^2 + 0.1\omega^2)$ 다. 초기 제어열은 $u\equiv0$ (비용 $592.18$).
iLQR 은 유한차분 야코비안 + 정규화 + 선탐색으로, MPPI 는 (11)로 구현하고 잡음은
$\epsilon_t \leftarrow \beta\epsilon_{t-1} + (1-\beta)\epsilon_t$ 로 시간 평활한다
($\beta=0.8$, $\sigma=4$).

**수용 기준** — 다섯 조건을 모두 만족해야 통과다.

1. **soft 고정점이 볼츠만 정책의 실제 가치다**: $\alpha \in \{1, 0.3, 0.1, 0.03, 0.01\}$ 전부에서
   $\max_s\lvert V_\alpha(s) - V^{\pi_\alpha}_\alpha(s)\rvert < 10^{-12}$ (측정값
   $4\times10^{-15}$–$7\times10^{-15}$). $V^{\pi_\alpha}_\alpha$ 는 보상에 $\alpha H(\pi_\alpha)$ 를
   더한 선형 해로 구한다.
2. **수축성 (7)**: 무작위 $u,v$ 300쌍에 대해
   $\lVert\mathcal{T}_\alpha u - \mathcal{T}_\alpha v\rVert_\infty / \lVert u-v\rVert_\infty \le \gamma$
   가 모든 $\alpha$ 에서 성립한다(측정 최댓값 $0.598$–$0.630$ $\le 0.9$).
3. **온도 편향 (8)**: $0 \le V_\alpha - V^\* \le \alpha\log m/(1-\gamma)$ 가 성립하고,
   $\alpha=0.01$ 에서 실측 차 $0.0107$ 이 상한 $0.1099$ 의 $1/10$ 수준임을 보고한다. 동시에
   $\alpha=0.01$ 에서 볼츠만 정책의 그리디 행동이 표준 최적 정책과 **12/12 상태에서 일치**한다.
4. **낙관적 동역학 편향 (9)**: 모든 $\alpha$ 에서 $V_{\mathrm{opt}} \ge V_\alpha$ 이고, 그 최대 차가
   $\alpha$ 가 작아질수록 **단조 증가**한다(측정값 $\alpha=1$: $0.107$, $0.3$: $0.292$,
   $0.1$: $0.597$, $0.03$: $1.117$, $0.01$: $1.448$).
5. **MPPI 대 iLQR (B)**: ⓐ iLQR 의 비용이 **단조 감소**하고 20,000 롤아웃 상당 안에서
   $J \le 105$ 에 도달한다(측정값 16,350 에서 $99.79$). ⓑ MPPI($\lambda=5$, $K=64$, 60 반복)가
   4,000 롤아웃 안에서 $J \le 130$ 에 도달한다(측정값 3,840 에서 $119.0$). ⓒ MPPI 의 평균
   유효 표본 수가 $0.1K$ **이하**다($K=256$ 에서 $1.7$, $K=1024$ 에서 $3.3$) — 가중이
   붕괴하고 있다는 진단이다. ⓓ 같은 $\lambda$ 에서 $K$ 를 $64 \to 1024$ 로 키우면 최종 비용이
   **나빠진다**($119.0 \to 162.9$) — 문제 P5 의 반례가 실제로 일어난다.

**비교 대상(베이스라인)**: ⓐ 아무것도 하지 않는 제어열($J_0 = 592.18$) — 두 방법의 공통 출발점.
ⓑ 표준 가치 반복($\alpha\to0$) — 조건 3 의 기준. ⓒ 선택: MPPI 의 $\lambda$ 를 비용 표준편차에
비례해 적응시켜(예: $\lambda_t = \mathrm{std}(S_k)$) 조건 ⓒ·ⓓ 가 개선되는지 확인한다. 이것이
P5 의 처방이 코드에서 작동하는지 보는 실험이다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 1 의 차가 $10^{-6}$ 수준 | 엔트로피 항을 보상에 더하지 않고 정책 가치만 계산했다 | $\alpha H(\pi_\alpha)$ 를 더한 보상 벡터를 출력한다 |
| $\alpha$ 가 작을 때 `inf`/`nan` | log-sum-exp 안정화를 빼먹었다 | $\max_a Q$ 를 뽑아낸 뒤 지수를 취하는지 확인한다 |
| 조건 3 의 부호가 음수($V_\alpha < V^\*$) | soft 백업에 $\alpha$ 를 곱하는 자리를 틀렸다 | $\alpha\log\sum e^{Q/\alpha}$ 의 두 $\alpha$ 가 모두 있는지 본다 |
| 조건 4 에서 $V_{\mathrm{opt}} < V_\alpha$ | (9)의 지수 안에 $\gamma$ 를 넣지 않았다 | $\alpha\log\sum_{s'}P e^{\gamma V/\alpha}$ 형태를 확인한다 |
| iLQR 이 발산한다 | 선탐색 실패 시 정규화를 키우지 않았다 | $Q_{uu}$ 의 최소 고윳값과 정규화 값을 반복마다 출력한다 |
| iLQR 의 비용이 오르내린다 | 선탐색에서 개선을 확인하지 않고 스텝을 받아들였다 | $J_{\mathrm{new}} < J$ 검사를 넣는다 |
| MPPI 가 전혀 개선되지 않는다 | $\lambda$ 가 비용 규모에 비해 너무 작아 $\mathrm{ESS}\approx1$ | $\mathrm{ESS} = 1/\sum_k w_k^2$ 를 출력하고 $\lambda$ 를 키워 본다 |
| MPPI 가 스윙업을 못 한다 | 잡음이 백색이라 궤적이 흔들리기만 한다 | $\beta$ 를 $0.8$ 로 두어 시간 평활한 잡음을 쓴다($\lambda=10,\sigma=4,K=512$, 30반복에서 $\beta=0$ 은 $337.3$, $\beta=0.8$ 은 $152.2$) |

## 열린 문제

- **(열린 문제) 온도를 과제에 맞춰 정하는 원칙** — (8)은 $\alpha$ 가 **편향을 만든다**는 것을
  정량화하지만 얼마가 적절한지는 말하지 않는다. SAC 는 엔트로피 제약으로 자동 조정하지만
  목표 엔트로피 $\bar{H}$ 가 새 하이퍼파라미터이고, 그 선택이 결과를 바꾼다. 현재 접근:
  [SAC](https://arxiv.org/abs/1801.01290) 의 이중 최적화,
  [soft Q-learning](https://arxiv.org/abs/1702.08165). 비어 있는 자리: 과제 지표에서 $\alpha$ 를
  역산하는 규칙.
- **(열린 문제) 확률적 동역학에서 추론 기반 제어의 위험 태도** — R4 는 순진한 추론이
  위험 추구가 됨을 보이고, 변분 분포를 참 동역학에 고정하면 그것이 사라진다. 그런데 **위험
  회피**가 필요한 로봇 과제에서 올바른 변분 가족이 무엇인지는 정해지지 않았다. 현재 접근:
  [Levine 2018](https://arxiv.org/abs/1805.00909) §4 의 논의,
  선형 해결 가능 MDP([Todorov 2009](https://doi.org/10.1073/pnas.0710743106)). 비어 있는 자리:
  지정한 위험 태도를 갖는 추론 정식화.
- **(열린 문제) MPPI 의 표본 복잡도와 차원** — (11)의 추정은 중요도 가중이므로 유효 표본 수가
  제어 차원과 지평에 지수적으로 민감하다(재현 과제에서 $K=1024$ 인데 $\mathrm{ESS}=3.3$).
  그래서 표본을 늘리는 것이 답이 아니고, 어떤 구조(평활 잡음, 저차원 매개화, 학습된 사전
  분포)가 그 의존성을 깨는지에 대한 이론이 없다. 현재 접근:
  [MPPI](https://doi.org/10.2514/1.G001921),
  [PI^2](https://www.jmlr.org/papers/v11/theodorou10a.html). 비어 있는 자리: 제어 차원에
  다항인 표본 복잡도 보장.
- **(열린 문제) 다봉 해를 평균하지 않는 방법** — (11)은 $q^\star$ 의 **평균**을 쓰므로 두
  회피 경로의 평균이 장애물을 통과하는 실패가 구조적으로 가능하다. 모드를 분리해 추적하는
  접근(혼합 모델, 다중 가설)은 계산이 늘고 모드 수를 미리 정해야 한다. 현재 접근:
  [Theodorou et al. 2010](https://www.jmlr.org/papers/v11/theodorou10a.html) 의 정책 개선 관점,
  그래프 기반 궤적 집합(`c6-*` 의 계획 이론). 비어 있는 자리: 모드 수를 모르는 상태에서
  평균 붕괴를 피하는 갱신식.

## 개념 점검

`rc quiz c8-control-as-inference` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c8-control-as-inference-quiz
questions:
  - id: q1
    type: single
    prompt: "엔트로피 정규화 목적함수에서 최적 정책이 볼츠만 분포인 이유는?"
    choices:
      - "정책을 지수족으로 가정했기 때문"
      - "단체 위 엔트로피 정규화 선형 문제의 1차 조건이 $\\pi \\propto e^{Q/\\alpha}$ 를 주기 때문"
      - "$\\max$ 가 미분 가능하지 않기 때문"
      - "볼츠만 분포가 분산이 가장 작기 때문"
    answer: 1
    explanation: "가정이 아니라 **결과**다. $\\sum_a \\pi Q + \\alpha H(\\pi)$ 를 단체 위에서 최대화하는 Lagrange 1차 조건이 $Q(a) - \\alpha\\log\\pi(a) = \\text{const}$ 를 주고, 정규화하면 (1)이 된다. 최대값은 (2)의 log-sum-exp 다."
    concept: { front: "볼츠만 정책의 출처", back: "단체 위 엔트로피 정규화 문제의 1차 조건 — 가정이 아니라 유도 결과" }
  - id: q2
    type: single
    prompt: "soft Bellman 연산자 $\\mathcal{T}_\\alpha$ 가 $\\gamma$-수축인 근거는?"
    choices:
      - "$\\alpha$ 가 충분히 작기 때문"
      - "$\\operatorname{softmax}$ 의 기울기가 확률벡터이므로 sup-노름에서 1-Lipschitz 이기 때문"
      - "엔트로피가 유계이기 때문"
      - "$\\log$ 가 오목이기 때문"
    answer: 1
    explanation: "$\\partial(\\alpha\\log\\sum e^{Q/\\alpha})/\\partial Q(a) = \\pi_\\alpha(a)$ 이고 이것이 확률벡터이므로 평균값 정리로 1-Lipschitz 다. 그 다음은 `c8-mdp-pomdp-bellman` 의 $\\max$ 수축 논증과 글자 그대로 같다. $\\alpha$ 의 크기는 무관하다."
    concept: { front: "soft 수축의 근거", back: "softmax 의 기울기 = 볼츠만 정책(확률벡터) → 1-Lipschitz → $\\gamma$-수축" }
  - id: q3
    type: truefalse
    prompt: "변분 분포에서 상태 전이까지 자유롭게 두면 더 좋은(더 타이트한) 하한을 얻으므로 그렇게 해야 한다."
    answer: false
    explanation: "하한은 더 커지지만, 그 최적해가 $q^\\star(s'\\mid s,a) \\propto P e^{V/\\alpha}$ 로 **동역학을 낙관적으로 휘게** 한다. 결과는 위험 추구 편향이고 확률적 환경에서 체계적 과대평가가 된다. 참 동역학에 고정한 느슨한 하한이 올바른 선택인 드문 경우다."
    concept: { front: "변분 분포의 상태 전이", back: "참 동역학에 고정한다 — 자유롭게 두면 낙관적 동역학(위험 추구) 편향" }
  - id: q4
    type: short
    prompt: "MPPI 의 가중 $w_k$ 를 비용 $S_k$ 와 온도 $\\lambda$ 로 쓰면? (비례식으로)"
    answer: ["exp(-S_k/lambda)", "exp(-S/lambda)", "e^{-S_k/\\lambda}", "exp(-S_k/lam)", "\\exp(-S_k/\\lambda)"]
    explanation: "(6)의 $q^\\star \\propto p\\,e^{-S/\\lambda}$ 를 중요도 가중으로 읽으면 $w_k \\propto \\exp(-S_k/\\lambda)$ 다. 구현에서는 $S_{\\min}$ 을 빼서 안정화하며 그것은 $w$ 를 바꾸지 않는다. $\\lambda\\to0$ 에서 최저 비용 표본 하나만 남고, $\\lambda\\to\\infty$ 에서 갱신이 0 이 된다."
    concept: { front: "MPPI 의 가중", back: "$w_k \\propto \\exp(-S_k/\\lambda)$ — 자유 에너지 최적 분포 (6)의 중요도 가중" }
  - id: q5
    type: truefalse
    prompt: "MPPI 는 표본 수 $K$ 를 늘리면 항상 더 좋은 해를 얻는다."
    answer: false
    explanation: "$\\lambda$ 가 비용 규모에 비해 작으면 가중이 최저 비용 표본 하나로 붕괴해 유효 표본 수가 1 에 가까워진다. 재현 과제에서 $\\lambda=5$ 로 $K$ 를 $64 \\to 1024$ 로 늘렸을 때 최종 비용이 $119.0 \\to 162.9$ 로 **나빠졌고**, 평균 ESS 는 $K$ 의 1% 미만이었다. 처방은 $K$ 가 아니라 $\\lambda$ 를 비용 분산에 맞추는 것이다."
    concept: { front: "MPPI 에서 $K$ 를 늘리는 것", back: "$\\lambda$ 가 작으면 ESS 가 붕괴해 효과 없음(또는 악화) — $\\lambda$ 를 비용 분산에 맞춘다" }
```

## 이 단계 공부법

1. **단체 위 문제로 시작한다 (45분)** — R1 의 Lagrange 1차 조건을 백지에서 쓴다. 볼츠만 정책이
   **가정이 아니라 결과**라는 것이 이 레슨의 첫 전환점이다. 그 다음 (2)의 양쪽 부등식을 손으로
   확인해 온도 편향의 크기를 감으로 익힌다.
2. **수축 논증을 재사용한다 (45분)** — $\operatorname{softmax}$ 의 기울기가 확률벡터라는 한 줄만
   확인하면 `c8-mdp-pomdp-bellman` 의 논증이 그대로 돌아간다. 두 레슨의 (7)을 나란히 적어
   **무엇이 교체되었는지**를 본다.
3. **ELBO 를 유도하고 약분을 직접 본다 (75분)** — R3 에서 $\rho_0$ 와 $P$ 가 약분되는 지점이
   핵심이다. 약분이 되는 이유(변분 분포의 상태 전이를 참 동역학으로 고정했기 때문)를 한 문장으로
   쓸 수 있으면 R4 의 실패 모드가 저절로 보인다.
4. **낙관적 편향을 수치로 만난다 (60분)** — 재현 과제 A 의 조건 4 를 돌려 $\alpha$ 를 낮출 때
   편향이 커지는 것을 본다. 그 다음 동역학을 결정론으로 바꿔 편향이 **사라지는 것**을 확인한다 —
   "시뮬레이터에서는 괜찮았는데 실기에서 깨진다"의 한 가지 정확한 원인이다.
5. **MPPI 와 iLQR 을 같은 축에서 비교한다 (120분)** — 재현 과제 B 를 돌린다. 가로축을 반복 수가
   아니라 **롤아웃 수**로 잡는 것이 공정성의 핵심이다. ESS 를 출력해 가중 붕괴를 직접 보고,
   $K$ 를 늘려도 나아지지 않는 것을 확인한 뒤 문제 P5 를 푼다.
6. **논문 3편과 열린 문제 (150분)** — Levine 2018(틀) → SAC(연속 행동) → MPPI(표본 기반).
   논문당 1페이지 노트는 **반드시** 쓴다. 끝으로 "열린 문제" 중 위험 태도를 골라, 재현 과제 A 의
   낙관적 반복을 **위험 회피** 쪽으로 바꾸려면 (9)의 어느 부호를 바꿔야 하는지 한 문단으로 쓴다.

**통과 기준**: 백지에서 (1)·(2)와 (10)을 유도할 수 있고, ELBO 에서 $P$ 가 약분되는 이유와
그것을 어기면 생기는 편향을 말할 수 있고, 재현 과제의 다섯 조건을 만족하는 코드와 논문 3편의
노트를 갖고 있다.
