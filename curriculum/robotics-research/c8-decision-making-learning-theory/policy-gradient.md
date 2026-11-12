---
id: c8-policy-gradient
title: 정책 경사 정리
summary: >-
  정책 경사 정리를 가치함수 재귀에서 빠진 줄 없이 유도하고, 기저선이 왜 불편(unbiased)이며
  분산을 얼마나 줄이는지 최적 기저선까지 계산한다. 이어서 성능 차 보조정리에서 TRPO 의
  단조 개선 한계를 세우고, 자연 경사가 KL 제약의 2차 전개임을 보이고, PPO 의 클리핑이 그
  보장을 왜 물려받지 못하는지 짚는다.
objectives:
  - 정책 경사 정리를 $V^\pi$ 의 재귀 전개에서 빠진 줄 없이 유도할 수 있다.
  - 상태 의존 기저선의 불편성을 증명하고 분산을 최소화하는 최적 기저선을 계산할 수 있다.
  - 성능 차 보조정리(performance difference lemma)를 증명하고 대리 목적함수와의 1차 일치를 보일 수 있다.
  - TRPO 의 단조 개선 한계 $J(\pi') \ge L_\pi(\pi') - C\,D_{\mathrm{KL}}^{\max}$ 와 상수 $C$ 의 출처를 설명할 수 있다.
  - 자연 경사가 KL 제약 하 2차 전개의 해임을 유도하고 재매개화 불변성을 설명할 수 있다.
  - PPO 의 클리핑이 무엇을 보장하지 않는지, 그리고 구현 세부가 성능 차이를 만드는 지점을 지적할 수 있다.
prerequisites: [c8-mdp-pomdp-bellman]
difficulty: 5
estimated_minutes: 540
tags: [policy-gradient, trpo, ppo, natural-gradient, variance-reduction, research]
activities:
  - id: c8-policy-gradient-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c8-policy-gradient-papers
    kind: reading
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c8-policy-gradient-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: c8-policy-gradient-reproduction
    kind: exercise
    title: 재현 과제 — 추정기 분산과 표본 효율 비교 (R2)
    estimated_minutes: 105
  - id: c8-policy-gradient-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Sutton & Barto, Reinforcement Learning: An Introduction (2nd ed.)"
    kind: book
    note: ch.13 (정책 경사 방법). 이 레슨의 1순위 교재. (공식 URL 미확인)
  - title: "Sutton, McAllester, Singh & Mansour — Policy gradient methods for RL with function approximation (2000)"
    url: https://papers.nips.cc/paper_files/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html
    kind: article
    note: 필독 1. 정책 경사 정리의 원전.
  - title: "Schulman, Levine, Abbeel, Jordan & Moritz — Trust region policy optimization (2015)"
    url: https://arxiv.org/abs/1502.05477
    kind: article
    note: 필독 2. §2-3 과 부록 A (단조 개선 한계).
  - title: "Schulman, Wolski, Dhariwal, Radford & Klimov — Proximal policy optimization algorithms (2017)"
    url: https://arxiv.org/abs/1707.06347
    kind: article
    note: 필독 3. §3 의 클리핑 목적함수.
  - title: "Williams — Simple statistical gradient-following algorithms for connectionist RL (1992)"
    url: https://doi.org/10.1007/BF00992696
    kind: article
    note: 권장. REINFORCE 의 원전.
  - title: "Baxter & Bartlett — Infinite-horizon policy-gradient estimation (2001)"
    url: https://doi.org/10.1613/jair.806
    kind: article
    note: 권장. GPOMDP 와 할인이 추정 편향을 만드는 지점.
  - title: "Amari — Natural gradient works efficiently in learning (1998)"
    url: https://doi.org/10.1162/089976698300017746
    kind: article
    note: 권장. 자연 경사와 Fisher 계량의 원전.
  - title: "Kakade — A natural policy gradient (2001)"
    url: https://papers.nips.cc/paper_files/paper/2001/hash/4b86abe48d358ecf194c56c69108433e-Abstract.html
    kind: article
    note: 권장. 자연 경사를 정책 경사에 접목한 글.
  - title: "Schulman, Moritz, Levine, Jordan & Abbeel — Generalized advantage estimation (2015)"
    url: https://arxiv.org/abs/1506.02438
    kind: article
    note: 권장. $\lambda$ 로 편향-분산을 조절하는 이점 추정.
  - title: "Engstrom et al. — Implementation matters in deep policy gradients (2020)"
    url: https://arxiv.org/abs/2005.12729
    kind: article
    note: 권장(반론). PPO 의 성능이 알고리즘이 아니라 구현 세부에서 온다는 절제 실험.
  - title: "Henderson et al. — Deep reinforcement learning that matters (2017)"
    url: https://arxiv.org/abs/1709.06560
    kind: article
    note: 권장(반론). 시드·분산 보고 없이 비교하면 결론이 뒤집힌다.
  - title: "Agarwal, Kakade, Lee & Mahajan — On the theory of policy gradient methods (2019)"
    url: https://arxiv.org/abs/1908.00261
    kind: article
    note: 권장. 정책 경사의 전역 수렴과 분포 이동 항.
---

# 정책 경사 정리

## 전제와 기호

`c8-mdp-pomdp-bellman` 의 MDP 표기와 두 Bellman 연산자를 그대로 쓴다. 추가로 **권장 선수**는
다음이다(플랫폼이 잠그지 않는다):

- 다변수 미적분: 연쇄 법칙, 미분과 적분의 교환(지배 수렴), 기울기와 Hessian.
- 확률: 점수 함수(score function) 항등식, Monte Carlo 추정의 분산, 조건부 기댓값의 탑 법칙.
- 볼록 최적화: 등식·부등식 제약의 Lagrange 쌍대, 2차 전개와 신뢰영역(`r0-convex-optimization`).

표기 추가(C8 모듈 공통):

| 기호 | 뜻 |
|---|---|
| $\pi_\theta(a \mid s)$ | $\theta \in \mathbb{R}^p$ 로 매개화된 미분가능 정책. $\pi_\theta(a\mid s) > 0$ (가정 **A3**) |
| $J(\theta)$ | $\mathbb{E}_{s_0 \sim \rho_0}\big[V^{\pi_\theta}(s_0)\big]$ |
| $\rho^\pi(s)$ | **비정규화** 할인 점유도. $\rho^\pi(s) = \sum_{t \ge 0} \gamma^t \Pr(s_t = s \mid \pi, \rho_0)$ |
| $d^\pi(s)$ | 정규화 점유 분포. $d^\pi(s) = (1-\gamma)\,\rho^\pi(s)$, $\sum_s d^\pi(s) = 1$ |
| $A^\pi(s,a)$ | 이점(advantage). $A^\pi(s,a) = Q^\pi(s,a) - V^\pi(s)$ |
| $g_\theta(s,a)$ | 점수. $g_\theta(s,a) = \nabla_\theta \log \pi_\theta(a \mid s) \in \mathbb{R}^p$ |
| $F(\theta)$ | Fisher 정보행렬. $F(\theta) = \mathbb{E}_{d^\pi,\pi}\big[g_\theta g_\theta^\top\big] \in \mathbb{R}^{p\times p}$ |
| $D_{\mathrm{KL}}^{\max}(\pi \Vert \pi')$ | $\max_s D_{\mathrm{KL}}\big(\pi(\cdot\mid s) \Vert \pi'(\cdot\mid s)\big)$ |
| $L_\pi(\pi')$ | 대리 목적함수. $L_\pi(\pi') = \frac{1}{1-\gamma}\mathbb{E}_{s \sim d^\pi, a\sim\pi'}\big[A^\pi(s,a)\big]$ |

A3(정책이 모든 행동에 양의 확률을 준다)은 $\log \pi_\theta$ 가 정의되게 하는 가정이고,
결정론 정책으로 수렴하는 경로에서 **경사가 소멸하는** 원인이기도 하다(문제 P5 의 배경).

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (정책 경사 정리) [D3]** — A1–A3 아래
  $$
  \nabla_\theta J(\theta) = \sum_s \rho^\pi(s) \sum_a \nabla_\theta \pi_\theta(a\mid s)\, Q^\pi(s,a)
    = \frac{1}{1-\gamma}\, \mathbb{E}_{s \sim d^\pi,\, a \sim \pi_\theta}\!\big[\, g_\theta(s,a)\, Q^\pi(s,a) \,\big]. \tag{1}
  $$
  **점유도 $\rho^\pi$ 의 $\theta$-의존성이 사라진다**는 것이 정리의 내용이다 — 환경의 전이
  모형을 미분하지 않아도 된다.
- **R2 (기저선의 불편성과 최적 기저선) [D3]** — 임의의 $b : \mathcal{S} \to \mathbb{R}$ 에 대해
  $\mathbb{E}_{a\sim\pi}[g_\theta(s,a)\, b(s)] = 0$ 이므로 $Q^\pi$ 를 $Q^\pi - b$ 로 바꿔도 (1)은
  **불편**이다. 스칼라 매개변수에서 분산을 최소화하는 기저선은
  $$
  b^\star(s) = \frac{\mathbb{E}_{a\sim\pi}\big[\lVert g_\theta(s,a)\rVert^2\, Q^\pi(s,a)\big]}
                    {\mathbb{E}_{a\sim\pi}\big[\lVert g_\theta(s,a)\rVert^2\big]} \tag{2}
  $$
  이고, 이는 일반적으로 $V^\pi(s)$ 와 **같지 않다**(문제 P3 에서 $V^\pi$ 기저선이 $b=0$ 보다
  9 배 나쁜 예를 계산한다). 또 전체 보상 $G_0$ 대신 잔여 보상 $G_t$ 를 쓰는 것(causality)도
  불편이며 분산을 줄인다.
- **R3 (성능 차 보조정리) [D3]** — 임의의 두 정책 $\pi, \pi'$ 에 대해
  $$
  J(\pi') - J(\pi) = \frac{1}{1-\gamma}\,
    \mathbb{E}_{s \sim d^{\pi'},\, a \sim \pi'}\big[A^\pi(s,a)\big]. \tag{3}
  $$
  우변의 점유 분포가 **$\pi'$ 의 것**이라는 점이 모든 신뢰영역 논의의 출발점이다.
- **R4 (TRPO 의 단조 개선 한계) [D3]** — (3)의 $d^{\pi'}$ 를 $d^\pi$ 로 바꾼 대리 목적함수
  $L_\pi(\pi')$ 는 $\pi' = \pi$ 에서 값과 1차 미분이 일치하고,
  $\epsilon := \max_{s,a}\lvert A^\pi(s,a)\rvert$ 에 대해
  $$
  J(\pi') \;\ge\; J(\pi) + L_\pi(\pi') - \frac{4\epsilon\gamma}{(1-\gamma)^2}\, D_{\mathrm{KL}}^{\max}(\pi\Vert\pi'). \tag{4}
  $$
  따라서 $L_\pi(\pi')$ 의 개선이 벌점보다 크면 **실제 성능이 단조 증가**한다. 상수
  $4\epsilon\gamma/(1-\gamma)^2$ 는 실무 규모에서 매우 커서, 이 한계를 그대로 쓰면 스텝이
  거의 0 이 된다 — TRPO 가 $D_{\mathrm{KL}}^{\max}$ 를 평균 KL 제약으로 바꾸는 이유다.
- **R5 (자연 경사는 KL 제약의 2차 해) [D2]** — KL 반지름 $\delta$ 의 신뢰영역에서 1차 목적함수를
  최대화하는 스텝은
  $$
  \Delta\theta^\star = \sqrt{\frac{2\delta}{\nabla J^\top F^{-1} \nabla J}}\; F(\theta)^{-1}\nabla_\theta J(\theta)
    + O(\delta) \tag{5}
  $$
  이고, $F$ 가 KL 의 Hessian 이라는 사실에서 이 스텝은 **$\theta$ 의 재매개화에 불변**이다.
- **R6 (PPO 의 클리핑이 보장하지 않는 것) [D1]** — 클리핑 목적함수는 비율
  $\rho_t = \pi'(a_t\mid s_t)/\pi(a_t\mid s_t)$ 가 구간을 벗어났을 때 **기울기를 0 으로 만드는**
  것이지, $D_{\mathrm{KL}}$ 을 제약하지 않는다. 따라서 (4)의 전제가 성립하지 않고 단조 개선
  보장은 없다. 보고된 성능 차이의 상당 부분은 알고리즘이 아니라 구현 세부(이점 정규화,
  관측 정규화, 학습률 감쇠, 기울기 클리핑)에서 온다(Engstrom et al. 2020).

## 유도

### R1 — 정책 경사 정리

$\nabla_\theta V^\pi(s)$ 를 재귀로 펼친다. $V^\pi(s) = \sum_a \pi_\theta(a\mid s) Q^\pi(s,a)$ 와
$Q^\pi(s,a) = r(s,a) + \gamma\sum_{s'} P(s'\mid s,a) V^\pi(s')$ 를 쓰면, 곱의 미분으로

$$
\nabla V^\pi(s) = \sum_a \Big[ \nabla \pi_\theta(a\mid s)\, Q^\pi(s,a)
  + \pi_\theta(a\mid s)\, \nabla Q^\pi(s,a) \Big]. \tag{6}
$$

$Q^\pi$ 에서 $r(s,a)$ 와 $P$ 는 $\theta$ 와 무관하므로
$\nabla Q^\pi(s,a) = \gamma \sum_{s'} P(s'\mid s,a)\nabla V^\pi(s')$ 다. 이것을 (6)에 넣으면

$$
\nabla V^\pi(s) = \underbrace{\sum_a \nabla \pi_\theta(a\mid s) Q^\pi(s,a)}_{=:\;\phi(s)}
  + \gamma \sum_{s'} \Big(\sum_a \pi_\theta(a\mid s) P(s'\mid s,a)\Big) \nabla V^\pi(s')
  = \phi(s) + \gamma \sum_{s'} P^\pi_{ss'}\, \nabla V^\pi(s'). \tag{7}
$$

(7)은 $\nabla V^\pi$ 에 대한 **선형 고정점 방정식**이다. $\lvert \gamma \rvert < 1$ 이고 $P^\pi$ 가
확률행렬이므로 $(I - \gamma P^\pi)$ 는 가역이고 Neumann 급수로

$$
\nabla V^\pi = \sum_{t\ge0} \gamma^t (P^\pi)^t \phi
  \quad\Longrightarrow\quad
  \nabla J(\theta) = \rho_0^\top \nabla V^\pi = \sum_s \Big(\sum_{t\ge0}\gamma^t \Pr(s_t = s)\Big)\phi(s)
  = \sum_s \rho^\pi(s)\,\phi(s),
$$

즉 (1)의 첫 등식이다. 두 번째 등식은 $\nabla \pi = \pi \nabla\log\pi$(A3 이 있어야 성립)와
$d^\pi = (1-\gamma)\rho^\pi$ 를 쓴 것이다.

**왜 이것이 놀라운가.** (7)을 펼치는 과정에서 $\Pr(s_t = s)$ 자체는 $\theta$ 에 의존한다. 그런데
그 의존성의 기울기가 **급수에 이미 흡수되어** 최종 식에는 $\rho^\pi$ 가 미분되지 않은 채로만
남는다. 그래서 전이 모형 $P$ 를 몰라도 표본으로 (1)을 추정할 수 있다.

**가정이 깨지는 곳.** A3 이 깨져 어떤 $(s,a)$ 에서 $\pi_\theta(a\mid s) = 0$ 이면
$\nabla\log\pi$ 가 정의되지 않고, 그 행동의 $Q$ 는 경사에 전혀 기여하지 못한다 — softmax
정책이 포화되면 경사가 지수적으로 작아져 **탐색이 멈춘다**. 또 (1)은 기댓값이 $d^\pi$ 에
대한 것이므로, $d^\pi$ 가 도달하지 못하는 상태의 $Q$ 는 아무리 커도 경사를 바꾸지 않는다.
이 "분포 의존성"이 오프라인 RL 과 모방학습에서 다시 핵심 문제가 된다
(`c8-offline-rl`, `c8-imitation-learning`).

### R2 — 기저선, 인과성, 최적 기저선

**불편성.** A3 아래 $\sum_a \pi_\theta(a\mid s) = 1$ 을 $\theta$ 로 미분하면

$$
\mathbb{E}_{a\sim\pi}\big[g_\theta(s,a)\big] = \sum_a \pi_\theta(a\mid s)\nabla\log\pi_\theta(a\mid s)
  = \sum_a \nabla \pi_\theta(a\mid s) = \nabla 1 = 0. \tag{8}
$$

$b(s)$ 가 $a$ 에 의존하지 않으므로 $\mathbb{E}_a[g_\theta b(s)] = b(s)\,\mathbb{E}_a[g_\theta] = 0$.
즉 (1)의 $Q^\pi$ 를 $Q^\pi - b$ 로 바꾼 추정기는 같은 기댓값을 갖는다. $b$ 가 $a$ 에 의존하면
(8)을 쓸 수 없고 **편향이 생긴다**(문제 P5 에서 편향을 정확히 계산한다).

**인과성(causality).** 궤적 추정기
$\hat{g} = \sum_t \gamma^t g_\theta(s_t,a_t)\, G$ 에서 $G$ 를 전체 보상 $G_0$ 로 쓰면, 시점 $t$
이전의 보상 $r_0,\dots,r_{t-1}$ 은 $a_t$ 와 독립이므로 그 항의 기댓값이 (8)로 0 이 된다.
따라서 잔여 보상 $G_t = \sum_{k\ge t}\gamma^{k-t} r_k$ 로 바꿔도 불편이고, 기댓값이 0 인 항을
제거한 만큼 **분산만 줄어든다**. 재현 과제에서 이 효과가 분산 약 3 배로 측정된다.

**최적 기저선.** 스칼라 $\theta$ 와 고정된 $s$ 에서
$\hat{g}(a) = g_\theta(s,a)\,(Q^\pi(s,a) - b)$ 의 분산은 $b$ 에 대한 2차식이다. 기댓값이 $b$ 와
무관하므로 $\mathbb{E}[\hat{g}^2]$ 만 최소화하면 된다:

$$
\frac{\partial}{\partial b}\, \mathbb{E}_a\Big[ g_\theta^2 (Q^\pi - b)^2 \Big]
  = -2\,\mathbb{E}_a\big[g_\theta^2 (Q^\pi - b)\big] = 0
  \;\Longrightarrow\; b^\star = \frac{\mathbb{E}_a[g_\theta^2 Q^\pi]}{\mathbb{E}_a[g_\theta^2]},
$$

즉 (2)다. 벡터 $\theta$ 에서는 $g_\theta^2$ 를 $\lVert g_\theta \rVert^2$ 로 바꾼 것이 trace
기준의 최적해다. **$b^\star$ 는 $Q$ 를 $\lVert g_\theta\rVert^2$ 로 가중한 평균**이고, 가중을
무시한 $V^\pi = \mathbb{E}_a[Q^\pi]$ 와 일치하지 않는다.

**가정이 깨지는 곳.** $V^\pi$ 를 기저선으로 쓰는 관행은 "이점이 평균 0 이면 분산이 작다"는
직관에 기대지만, 가중이 비대칭인 상태에서는 $b = V^\pi$ 가 $b = 0$ 보다 **더 나쁠 수 있다**
(문제 P3: 분산 $0.0064 \to 0.0576$, 9 배). 또 $b$ 를 데이터로 추정하면 $b$ 가 $a$ 와 상관되어
엄밀한 불편성이 깨진다 — 같은 배치로 기저선을 적합하고 그 배치에서 경사를 추정하면
작은 편향이 들어간다.

### R3 — 성능 차 보조정리

$\pi'$ 의 궤적에 대해 $A^\pi$ 의 할인 합을 전개한다. $A^\pi(s,a) = r(s,a) + \gamma
\mathbb{E}_{s'}[V^\pi(s')] - V^\pi(s)$ 를 쓰면

$$
\mathbb{E}_{\pi'}\Big[\sum_{t\ge0}\gamma^t A^\pi(s_t,a_t)\Big]
 = \mathbb{E}_{\pi'}\Big[\sum_{t\ge0}\gamma^t \big(r_t + \gamma V^\pi(s_{t+1}) - V^\pi(s_t)\big)\Big].
$$

$V^\pi$ 항은 **망원(telescoping)** 으로 접힌다:
$\sum_t \gamma^t(\gamma V^\pi(s_{t+1}) - V^\pi(s_t)) = -V^\pi(s_0)$ (유계성 A1 로 꼬리가 0 으로
간다). 따라서

$$
\mathbb{E}_{\pi'}\Big[\sum_{t\ge0}\gamma^t A^\pi(s_t,a_t)\Big] = J(\pi') - J(\pi),
$$

좌변을 점유 분포로 다시 쓰면 $\frac{1}{1-\gamma}\mathbb{E}_{s\sim d^{\pi'}, a\sim\pi'}[A^\pi]$
이므로 (3)이다.

**읽는 법**: (3)은 "$\pi$ 의 이점을 $\pi'$ 의 분포에서 재면 성능 차가 정확히 나온다"고 말한다.
문제는 $d^{\pi'}$ 를 모른다는 것이고, 정책 경사·TRPO·오프라인 RL 은 모두 이 한 항을 어떻게
근사하는가에 대한 서로 다른 답이다.

**가정이 깨지는 곳.** 망원 전개는 $\gamma < 1$ 과 $V^\pi$ 의 유계성을 쓴다. $\gamma = 1$ 이고
흡수 상태가 없으면 양변이 발산한다. 또 (3)은 **정확한** $A^\pi$ 를 전제한다 — 추정된
$\hat{A}$ 를 넣으면 오차가 $1/(1-\gamma)$ 로 증폭된다.

### R4 — 대리 목적함수와 신뢰영역

(3)에서 $d^{\pi'}$ 를 $d^\pi$ 로 바꾼 것이 $L_\pi(\pi')$ 다. 두 성질을 확인한다.

**1차 일치.** $\pi' = \pi$ 에서 $\mathbb{E}_{a\sim\pi}[A^\pi(s,a)] = 0$ 이므로 $L_\pi(\pi) = 0$ 이고,
$\theta$ 로 미분하면 $\nabla_{\theta'} L_{\pi_\theta}(\pi_{\theta'})\big|_{\theta'=\theta} =
\frac{1}{1-\gamma}\mathbb{E}_{d^\pi,\pi}[g_\theta A^\pi] = \nabla_\theta J(\theta)$ — (1)에서
기저선 $V^\pi$ 를 쓴 형태와 정확히 같다. 즉 $L$ 은 $J$ 의 **1차 모형**이다.

**오차 항.** $d^{\pi'}$ 와 $d^\pi$ 의 차이는 두 정책이 궤적 위에서 처음으로 달라지는 시점에
의해 지배된다. 전변동(total variation) $\alpha = \max_s D_{\mathrm{TV}}(\pi\Vert\pi')$ 로
짝지음(coupling)을 만들면, 시점 $t$ 까지 한 번도 달라지지 않을 확률이 $(1-\alpha)^t$ 이상이고
각 불일치가 이점에 최대 $2\epsilon$ 를 기여하므로 오차가 $O(\epsilon\gamma\alpha^2/(1-\gamma)^2)$
로 묶인다. Pinsker 부등식 $D_{\mathrm{TV}}^2 \le \tfrac12 D_{\mathrm{KL}}$ 로 $\alpha^2$ 를 KL 로
바꾸면 (4)의 상수 $4\epsilon\gamma/(1-\gamma)^2$ 가 나온다
(생략: 짝지음의 세부는 TRPO 부록 A 의 보조정리 1–3).

**가정이 깨지는 곳.** (4)의 $\epsilon$ 은 **최대** 이점이고 $D^{\max}_{\mathrm{KL}}$ 은 **최대** KL
이다. 둘 다 최악의 상태에서 결정되므로, 상태 공간이 크면 벌점이 폭발해 허용 스텝이 0 에
가까워진다. 실무의 TRPO 는 $D^{\max}_{\mathrm{KL}}$ 을 $\bar{D}_{\mathrm{KL}} =
\mathbb{E}_{s\sim d^\pi}[D_{\mathrm{KL}}]$ 로 바꾸는데, 이 치환으로 **단조 개선 보장은 사라진다.**
즉 실무의 TRPO 는 정리의 알고리즘이 아니라 정리에서 영감을 받은 알고리즘이다.

### R5 — 자연 경사

$\delta$-KL 신뢰영역에서 1차 목적함수를 최대화한다:

$$
\max_{\Delta\theta}\; \nabla J^\top \Delta\theta
  \quad\text{s.t.}\quad \bar{D}_{\mathrm{KL}}(\theta \Vert \theta + \Delta\theta) \le \delta .
$$

KL 은 $\Delta\theta = 0$ 에서 값과 1차 미분이 모두 0 이고 Hessian 이 Fisher 행렬이다:

$$
\bar{D}_{\mathrm{KL}}(\theta\Vert\theta+\Delta\theta)
  = \tfrac12 \Delta\theta^\top F(\theta)\,\Delta\theta + O(\lVert\Delta\theta\rVert^3). \tag{9}
$$

(9)를 제약에 넣고 Lagrange 조건을 쓰면 $\nabla J = \lambda F \Delta\theta$, 즉
$\Delta\theta \propto F^{-1}\nabla J$ 이고, 제약을 등호로 채우면 (5)의 계수가 나온다.

**재매개화 불변성.** $\theta = h(\psi)$ 로 좌표를 바꾸면 $\nabla_\psi J = H^\top \nabla_\theta J$,
$F_\psi = H^\top F_\theta H$ ($H = \partial h/\partial\psi$)이므로
$F_\psi^{-1}\nabla_\psi J = H^{-1} F_\theta^{-1}\nabla_\theta J$ — **같은 정책 변화**를 준다.
보통의 경사는 이 성질이 없어서 신경망의 매개화에 따라 스텝이 달라진다.

**가정이 깨지는 곳.** (9)는 2차 전개이므로 $\delta$ 가 커지면 틀린다. 또 $F$ 를 표본으로
추정하면 조건수가 나빠 $F^{-1}$ 가 불안정하다 — 실무는 공액기울기(CG)로 $F^{-1}\nabla J$ 를
행렬 없이 풀고 선탐색(line search)으로 실제 KL 과 대리 개선을 **검사**한다. 이 선탐색이
TRPO 구현에서 보장을 지탱하는 유일한 장치다.

## 증명 스케치

### R1 — 정책 경사 정리 [D3]

**가설** H1: A1(보상 유계)·A2($\gamma<1$). H2: $\pi_\theta(a\mid s)$ 가 $\theta$ 에 대해 미분가능.
H3: A3($\pi_\theta > 0$) 또는 $\nabla\pi$ 를 직접 쓰는 형태만 사용.
**결론** C: (1).

**전략**: 가치함수 재귀의 고정점 전개(Neumann 급수). 미분과 무한급수의 교환은 유계 수렴으로.

1. $V^\pi(s) = \sum_a \pi Q^\pi$ 를 곱의 미분으로 전개 → (6). 쓰는 것: H2.
2. $r, P$ 가 $\theta$ 와 무관하다는 사실로 $\nabla Q^\pi$ 를 $\nabla V^\pi$ 로 되돌린다 → (7).
3. (7)을 $(I - \gamma P^\pi)\nabla V^\pi = \phi$ 로 읽고 Neumann 급수로 푼다. 쓰는 것: H1(급수의
   절대 수렴과 항별 미분 교환).
4. $\rho_0$ 로 가중해 $\rho^\pi$ 를 얻고, H3 로 $\nabla\pi = \pi\nabla\log\pi$ 를 쓴다 → C.

**가설 하나를 지우면**: H1 의 $\gamma<1$ 을 지우면 3단계의 Neumann 급수가 수렴하지 않아 전개
자체가 불가능하다(평균 보상 정책 경사는 정상분포의 미분을 따로 다룬다). H3 를 지우면 (1)의
두 번째 형태(점수 함수 형태)를 쓸 수 없고 첫 형태만 유효하다 — 결정론 정책 경사(DPG)가
$\nabla_a Q$ 를 쓰는 다른 경로로 가는 이유다.

생략: 연속 상태·행동에서의 교환 조건은 지배 수렴 정리로. Sutton et al. 2000 의 정리 1–2.

### R4 — 단조 개선 한계 [D3]

**가설** H1–H2(위와 동일). H4: $\epsilon = \max_{s,a}\lvert A^\pi(s,a)\rvert < \infty$.
**결론** C: (4), 그리고 $L_\pi(\pi') > C D^{\max}_{\mathrm{KL}}$ 이면 $J(\pi') > J(\pi)$.

**전략**: 성능 차 보조정리(정확한 등식) → 점유 분포 치환의 오차를 짝지음으로 묶기 → Pinsker
로 TV 를 KL 로 교체.

1. (3)을 세운다(망원 전개). 쓰는 것: H1.
2. $d^{\pi'}$ 를 $d^\pi$ 로 치환한 오차를, 두 정책이 시점 $t$ 까지 일치할 확률
   $\ge (1-\alpha)^t$ 로 묶는다. 쓰는 것: H4, 짝지음.
3. 불일치 1회가 이점에 최대 $2\epsilon$ 를 주고 할인 합이 $\gamma/(1-\gamma)^2$ 규모임을 써서
   오차 $\le 4\epsilon\gamma\alpha^2/(1-\gamma)^2$.
4. Pinsker $\alpha^2 \le \tfrac12 D^{\max}_{\mathrm{KL}}$ 로 바꾼다 → C.

**가설 하나를 지우면**: H4 를 지우면(이점이 비유계) 상수가 무한이 되어 한계가 공허하다.
그리고 2단계의 $D^{\max}$ 를 평균 KL 로 바꾸면 짝지음이 최악 상태를 덮지 못해 **부등식이
성립하지 않는다** — 실무 TRPO 와 정리 사이의 간극이 정확히 여기다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** 유한 지평 $T$, 할인 없는 경우($\gamma=1$)에 대해 R1 을 다시 유도하라.
$\rho^\pi$ 의 자리에 무엇이 오는지, 그리고 $T \to \infty$ 에서 왜 발산하는지 쓰라.
*해답 스케치*: (7)의 전개가 $T$ 단계에서 끝나므로 $\sum_{t=0}^{T-1}(P^\pi)^t$ 가 남는다. 이는
$T$ 에 비례해 커지고 Neumann 급수의 수렴 인자가 없다. $\gamma<1$ 은 이 합을 유계로 만드는
정규화 장치이고, 그래서 할인은 "모델링 가정"이면서 동시에 "추정량의 정규화"다
(Baxter & Bartlett 2001 이 다루는 편향이 이것이다).

**P2 (증명, ★★★, R3·R4)** 성능 차 보조정리 (3)을 직접 증명하고, 그것으로
$\nabla_{\theta'}L_{\pi_\theta}(\pi_{\theta'})|_{\theta'=\theta} = \nabla_\theta J(\theta)$ 를 보여라.
그 다음 (4)의 2단계(점유 분포 치환 오차)에서 $\alpha^2$ 이 아니라 $\alpha$ 만 얻게 되는
잘못된 논증을 하나 만들고 어디가 틀렸는지 지적하라.
*전략과 핵심 부등식*: (3)은 망원 전개. 1차 일치는 $\mathbb{E}_\pi[A^\pi]=0$. 틀린 논증은 보통
"불일치가 한 번만 일어난다"고 가정해 $\alpha$ 한 번만 세는 경우다 — 불일치 **이후의 분포
차이**가 다시 $\alpha$ 를 곱한다. 전개는 숨긴다.

**P3 (계산, ★, R2)** 단일 상태 2행동 문제($\gamma=0$): $\pi(a_1) = \sigma(\theta) = 0.8$,
$r(a_1) = 1$, $r(a_2) = 0$. 스칼라 경사 추정기
$\hat{g}(a) = \nabla\log\pi(a)\,(r(a) - b)$ 에 대해 (i) $\mathbb{E}[\hat{g}]$, (ii) $b=0$,
$b = V^\pi$, $b = b^\star$ 각각의 분산, (iii) $b^\star$ 를 구하라.
*정답*: $\nabla\log\pi(a_1) = 1-p = 0.2$, $\nabla\log\pi(a_2) = -p = -0.8$.
$\mathbb{E}[\hat{g}] = p(1-p) = 0.16$ (모든 $b$ 에서 동일). 분산은
$b=0$: $0.0064$, $b=V^\pi=0.8$: $0.0576$, $b^\star = 1-p = 0.2$: **정확히 0**.
허용오차 $10^{-12}$. 즉 $V^\pi$ 기저선이 $b=0$ 보다 **9 배 나쁘고**, 최적 기저선은 평균
보상이 아니다.
검산: $b=0.2$ 에서 $\hat{g}(a_1) = \hat{g}(a_2) = 0.16$ 임을 직접 확인한다 — 추정기가
상수이므로 분산이 0 이다.

**P4 (구현, ★★, R1·R2)** 작은 랜덤 MDP(상태 6·행동 3·softmax 정책)에서 (1)의 해석적 경사를
선형 해로 정확히 계산하고, 중앙차분과 비교하라. 그 다음 세 가지 Monte Carlo 추정기(전체
보상 / 잔여 보상 / 잔여 보상 − 선형 기저선)의 표본 평균이 모두 해석적 경사로 수렴하는지
확인하라.
*루브릭*: ⓐ 해석적 경사와 중앙차분의 상대오차가 $10^{-6}$ 이하 ⓑ $\rho^\pi$ 를
$(I-\gamma (P^\pi)^\top)^{-1}\rho_0$ 로 계산했다(샘플링이 아니라 선형 해) ⓒ 기저선을 바꿔도
해석적 경사가 $10^{-12}$ 이내로 불변임을 보였다 ⓓ 세 추정기의 표본 분산을 함께 보고했다
ⓔ 중앙차분의 $h$ 선택 근거(절단오차와 반올림의 균형)를 적었다.

**P5 (반례, ★★, R2)** 행동에 의존하는 기저선 $b(s,a)$ 가 불편성을 깨뜨림을 P3 의 설정에서
**정확한 편향 값**으로 보이라. 그리고 "이점 $A^\pi(s,a)$ 를 기저선으로 쓰면 추정기가 0 이
된다"는 관찰이 왜 모순이 아닌지 설명하라.
*성질 체크리스트*: ⓐ $b(a) = r(a)$ 로 두면 $\hat{g} \equiv 0$ 이므로 $\mathbb{E}[\hat{g}] = 0$,
편향 $= -0.16$ ⓑ (8)을 쓸 수 없는 지점을 정확히 지적($b$ 가 $a$ 의 함수라 $b$ 를 기댓값 밖으로
뺄 수 없다) ⓒ $Q$ 를 그대로 빼는 것은 "기저선"이 아니라 목적함수를 바꾼 것이라는 구분
ⓓ 행동 의존 기저선을 쓰면서 불편성을 되찾는 방법(보정 항이 필요하다)을 한 줄로.

**P6 (논문, ★★, R4·R6)** TRPO(§2–3, 부록 A)와 PPO(§3)를 읽고, 다음 셋을 각각 3문장 이내로
쓰라: (i) TRPO 의 정리가 보장하는 것과 TRPO 구현이 실제로 하는 것의 차이, (ii) PPO 의
클리핑이 KL 을 제약하지 못하는 이유, (iii) Engstrom et al. 2020 의 절제 실험에서 PPO 의
이득 중 클리핑에 귀속되는 부분.
*채점 루브릭*: (i) $D^{\max}_{\mathrm{KL}} \to \bar{D}_{\mathrm{KL}}$ 치환과 선탐색을 짚으면
통과. (ii) 비율이 구간을 벗어나면 기울기가 0 이 되지만 **그 전에 이미 이동한 양**은 제약되지
않고, 비율 제약은 상태별 KL 과 다른 양이라는 점. (iii) 관측·이점 정규화와 학습률 감쇠가
클리핑과 비슷하거나 더 큰 기여를 한다는 보고. "PPO 가 더 간단하다"만 쓰면 미달.

**P7 (유도, ★★, R5)** $F(\theta) = \nabla^2_{\Delta\theta} \bar{D}_{\mathrm{KL}}
(\theta\Vert\theta+\Delta\theta)\big|_{\Delta\theta=0}$ 를 보이고, 자연 경사 스텝이 재매개화에
불변임을 $\theta = h(\psi)$ 로 확인하라.
*해답 스케치*: $\log$ 의 2차 Taylor 전개에서 1차 항은 (8)로 0 이 되고, 2차 항에서
$\mathbb{E}[\nabla\log\pi \nabla\log\pi^\top]$ 와 $-\mathbb{E}[\nabla^2\log\pi]$ 가 같다는
항등식을 쓴다. 불변성은 $F_\psi = H^\top F_\theta H$ 와 $\nabla_\psi = H^\top\nabla_\theta$ 를
대입하면 $H^{-1}$ 만 남는다.

## 논문 읽기

**필독 3편.** 각 논문에 고정 질문 10개로 1페이지 노트를 쓴다(`lesson-standard.md` §5).
3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Sutton, McAllester, Singh & Mansour, "Policy gradient methods for reinforcement learning
   with function approximation" (2000, NIPS 12)** — 역할: `원전(seminal)`.
   <https://papers.nips.cc/paper_files/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html>
   읽는 이유: R1 의 원전이고, 호환 가능(compatible) 함수 근사 조건이 자연 경사(R5)로 이어진다.
   추가 질문: ⓐ 저자들의 "compatible features" 조건은 (1)의 어느 항을 바꾸는가?
   ⓑ 정리 2 의 수렴 주장은 무엇을 보장하고 무엇을 보장하지 않는가(국소? 전역?)?
2. **Schulman, Levine, Abbeel, Jordan & Moritz, "Trust region policy optimization" (2015, ICML)**
   — 역할: `원전(seminal)`. <https://arxiv.org/abs/1502.05477> (§2–3, 부록 A)
   읽는 이유: R3·R4 가 이 논문의 보조정리들이다. 정리와 구현의 간극을 직접 보는 것이 목적이다.
   추가 질문: ⓐ 부록 A 의 짝지음 논증에서 $\alpha^2$ 가 나오는 자리를 식 번호로 지적하라.
   ⓑ 저자들이 $D^{\max}_{\mathrm{KL}}$ 을 평균으로 바꾸며 포기한 것을 논문은 어떻게 정당화하는가?
3. **Schulman, Wolski, Dhariwal, Radford & Klimov, "Proximal policy optimization algorithms"
   (2017, arXiv)** — 역할: `표준(standard)`. <https://arxiv.org/abs/1707.06347> (§3 중심)
   읽는 이유: 사실상의 표준 알고리즘이고, **이론적 보장 없이 표준이 된 사례**다.
   추가 질문: ⓐ 클리핑 목적함수가 $\rho_t$ 의 어느 영역에서 기울기를 0 으로 만드는지 그림으로
   그려라. ⓑ 논문의 실험에서 시드 수와 신뢰구간 보고는 어떤가(질문 6)?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU **1분 이내**(측정값: 학습 비교 15개 실행
약 10초, 분산 측정 약 2초), 메모리 200 MB 이내, numpy 만. 시뮬레이터는 쓰지 않는다 —
CartPole 동역학을 20줄로 직접 적는다.

환경은 CartPole-v1 과 같은 동역학·종료 조건이다: $m_c = 1.0$, $m_p = 0.1$, 반길이 $l = 0.5$,
$F = \pm 10$, $\Delta t = 0.02$ (오일러), 종료 $\lvert x\rvert > 2.4$ 또는
$\lvert\vartheta\rvert > 12^\circ$, 최대 500 스텝, 보상은 스텝마다 $1$. 정책은
$\pi_\theta(a\mid s) = \mathrm{softmax}(\theta\,\phi(s))$, $\phi(s) = (s, 1) \in \mathbb{R}^5$,
$\theta \in \mathbb{R}^{2\times5}$, $\theta_0 = 0$. 할인 $\gamma = 0.99$, GAE $\lambda = 0.95$.

**세 추정기**를 구현한다: ⓐ 전체 보상 REINFORCE($G_0$), ⓑ 잔여 보상 REINFORCE($G_t$),
ⓒ 잔여 보상 − 선형 가치 기저선. 그리고 **세 알고리즘**: REINFORCE(기저선 없음),
REINFORCE+기저선, PPO(클리핑 $0.2$, 배치당 20 에폭, 이점 정규화).

**수용 기준** — 네 조건을 모두 만족해야 통과다.

1. **불편성(해석적 검증)**: 문제 P4 의 작은 MDP 에서 해석적 경사와 중앙차분의 상대오차가
   $10^{-6}$ 이하이고, 기저선을 $0 \to V^\pi \to$ 상수로 바꿀 때 해석적 경사의 변화가
   $10^{-12}$ 이하다.
2. **분산 서열(CartPole)**: 고정된 $\theta$(기저선 버전으로 10,000 스텝 학습한 결과)에서
   에피소드당 경사 추정치 400개의 공분산 trace $\mathrm{tr}\,\widehat{\mathrm{Cov}}$ 가
   **모든 5 시드에서** 다음을 만족한다:

$$
\frac{\mathrm{tr}_{\text{전체 보상}}}{\mathrm{tr}_{\text{잔여 보상}}} \ge 2.5, \qquad
  \frac{\mathrm{tr}_{\text{잔여 보상}}}{\mathrm{tr}_{\text{기저선}}} \ge 1.4, \qquad
  \frac{\mathrm{tr}_{\text{전체 보상}}}{\mathrm{tr}_{\text{기저선}}} \ge 4.0 . \tag{10}
$$

   (측정값: 각각 $2.93$–$3.63$, $1.65$–$1.99$, $5.49$–$6.00$.)
3. **방향 일치**: 잔여 보상 추정기의 표본 평균과 기저선 추정기의 표본 평균의 코사인 유사도가
   모든 시드에서 $\ge 0.85$ (측정값 $0.874$–$0.987$). 전체 보상 추정기는 분산이 커서 400
   에피소드로는 방향이 안정되지 않는다($0.58$–$0.94$) — **이 자체가 조건 2 의 의미**이므로
   전체 보상에는 방향 조건을 걸지 않는다.
4. **표본 효율(5 시드 평균)**: 환경 스텝 예산 60,000, 배치 2,000 스텝에서
   ⓐ PPO 가 5 시드 **모두** 배치 평균 보상 $200$ 에 도달하고, 도달 스텝의 중앙값이
   REINFORCE+기저선의 $60\%$ 이하다(측정값 26,902 vs 49,152 = $55\%$).
   ⓑ REINFORCE+기저선이 5 시드 중 $\ge 4$ 시드에서 $200$ 에 도달하고, 최종 배치 평균 보상의
   5 시드 평균이 기저선 없는 REINFORCE 보다 크다(측정값 $165.6$ vs $87.7$).

**비교 대상(베이스라인)**: ⓐ 기저선 없는 REINFORCE — 세 알고리즘의 하한 역할. ⓑ 조건 1 의
해석적 경사 — 추정기 구현의 참값. ⓒ 선택: 같은 코드에서 PPO 의 클리핑을 끄고
($\epsilon_{\text{clip}} = \infty$) 20 에폭을 돌려 성능이 붕괴하는지 확인한다. 붕괴한다면
클리핑이 **다중 에폭 재사용을 가능하게 하는 장치**라는 R6 의 해석이 코드로 확인된다.

**참고 출력**(numpy 2.x, 시드 0–4): REINFORCE 는 4/5 시드에서 200 도달(중앙값 53,116 스텝,
최종 평균 $87.7$), REINFORCE+기저선은 5/5(중앙값 49,152, 최종 평균 $165.6$), PPO 는
5/5(중앙값 26,902, 최종 평균 $282.0$). 이 숫자는 난수 스트림에 의존하므로 **판정은 네
조건으로만** 한다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 2 의 첫 비율이 1 에 가깝다 | 전체 보상 추정기에도 $G_t$ 를 썼다(인과성 제거를 중복 적용) | 두 추정기의 계수 배열을 출력해 $G_0$ 가 모든 $t$ 에 같은 값인지 본다 |
| 조건 1 의 기저선 불변성이 깨진다 | 기저선을 **같은 배치**로 적합하고 그 배치로 경사를 추정 | 기저선을 별도 배치(또는 직전 배치)로 적합해 다시 돌린다 |
| PPO 가 학습하지 않는다(보상 $\approx 45$ 에서 정체) | 학습률이 작아 20 에폭으로도 신뢰영역을 채우지 못한다 | 이점을 정규화했는지 확인하고 학습률을 $\times 10$ 씩 올려 본다(측정에서는 $1.0$ 에서 동작) |
| PPO 가 초반에 붕괴한다 | 클리핑 없이 다중 에폭을 돌렸다 | 비율 $\rho_t$ 의 분포를 히스토그램으로 본다 — 꼬리가 $10$ 을 넘으면 폭주다 |
| 모든 방법의 분산이 비정상적으로 크다 | $\gamma^t$ 가중을 빼먹었다 | 추정기에서 $\gamma^t$ 를 곱하는 줄을 확인한다(없으면 (1)의 추정기가 아니다) |
| 시드마다 결론이 뒤집힌다 | 시드 1–2개로 비교했다 | 5 시드 전체를 보고한다 — Henderson et al. 2017 이 보고한 실패 양상이다 |

## 열린 문제

- **(열린 문제) 접촉·비매끄러운 동역학에서 정책 경사의 타당성** — (1)의 유도는 $P$ 를
  미분하지 않지만, 접촉이 있는 시스템에서는 보상과 가치가 상태에 대해 **불연속**이고 시뮬레이터의
  부드러운 근사(soft contact)가 실제와 다른 기울기를 준다. 매끄럽게 만든 모형에서 얻은 경사가
  원래 목적함수의 하강 방향이라는 보장은 없다. 현재 접근: 접촉을 상보성 제약으로 다루는 궤적
  최적화([Posa et al. 2014](https://doi.org/10.1177/0278364913506757)), 볼록 완화된 접촉
  모형([Todorov 2014](https://doi.org/10.1109/ICRA.2014.6907751)), 접촉 암시적
  MPC([Aydinoglu et al. 2024](https://arxiv.org/abs/2304.11259)). 비어 있는 자리: 평활화
  매개변수와 경사 품질을 잇는 정량적 기준.
- **(열린 문제) 신뢰영역 보장과 실제 구현의 간극** — (4)의 상수는 실무에서 사실상 무한대라
  정리를 그대로 쓰면 스텝이 0 이고, 쓰이는 알고리즘(평균 KL TRPO, PPO)에는 단조 개선 보장이
  없다. 성능 차이가 알고리즘에서 오는지 구현에서 오는지조차 논쟁 중이다. 현재 접근:
  절제 실험([Engstrom et al. 2020](https://arxiv.org/abs/2005.12729)), 평가 방법론
  ([Henderson et al. 2017](https://arxiv.org/abs/1709.06560),
  [Agarwal et al. 2021](https://arxiv.org/abs/2108.13264)). 비어 있는 자리: 실무 스텝 크기에서
  타이트한 개선 한계.
- **(열린 문제) 정책 경사의 표본 복잡도와 분포 이동 항** — softmax 정책의 전역 수렴은
  정확한 경사와 충분한 탐색 가정 아래 증명되었지만, 수렴률에 등장하는 분포 불일치 항
  $\lVert d^{\pi^\*}/d^{\pi_0}\rVert_\infty$ 는 로봇 문제에서 지수적으로 클 수 있다. 현재 접근:
  [Agarwal, Kakade, Lee & Mahajan 2019](https://arxiv.org/abs/1908.00261),
  [Mei et al. 2020](https://arxiv.org/abs/2005.06392). 비어 있는 자리: 로봇 규모 상태
  공간에서 이 항을 실제로 묶는 구조 가정.
- **(열린 문제) 편향-분산 손잡이의 원칙 있는 선택** — GAE 의 $\lambda$, 기저선의 적합 방식,
  보상 스케일링은 모두 편향과 분산을 교환하지만 선택은 경험적이다. 현재 접근:
  [GAE](https://arxiv.org/abs/1506.02438), [Baxter & Bartlett 2001](https://doi.org/10.1613/jair.806)
  의 할인 편향 분석. 비어 있는 자리: 목표 성능이 주어졌을 때 $\lambda$·$\gamma$ 를 고르는 기준.

## 개념 점검

`rc quiz c8-policy-gradient` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위 문제
세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c8-policy-gradient-quiz
questions:
  - id: q1
    type: single
    prompt: "정책 경사 정리 (1)에서 '놀라운' 부분은 무엇인가?"
    choices:
      - "보상이 할인되어 유계가 된다는 점"
      - "점유도 $\\rho^\\pi$ 의 $\\theta$-의존성이 최종 식에서 미분되지 않은 채로만 남는다는 점"
      - "$Q^\\pi$ 를 몰라도 경사를 계산할 수 있다는 점"
      - "정책이 결정론일 때도 성립한다는 점"
    answer: 1
    explanation: "$\\Pr(s_t=s)$ 는 $\\theta$ 에 의존하지만, 가치함수 재귀를 Neumann 급수로 풀면 그 의존성의 기울기가 급수에 흡수되고 최종 식에는 미분되지 않은 $\\rho^\\pi$ 만 남는다. 그래서 전이 모형 $P$ 를 미분할 필요가 없다."
    concept: { front: "정책 경사 정리의 핵심", back: "점유도의 $\\theta$-의존성이 흡수되어 $P$ 를 미분하지 않아도 된다 — 모형 없이 표본으로 추정 가능" }
  - id: q2
    type: truefalse
    prompt: "분산을 최소화하는 기저선은 항상 $V^\\pi(s)$ 다."
    answer: false
    explanation: "최적 기저선은 (2)의 $\\lVert \\nabla\\log\\pi \\rVert^2$ 로 가중한 $Q$ 의 평균이고, 가중을 무시한 $V^\\pi = \\mathbb{E}_a[Q]$ 와 일반적으로 다르다. 문제 P3 은 $V^\\pi$ 기저선이 $b=0$ 보다 9 배 나쁘고 최적 기저선은 분산을 정확히 0 으로 만드는 예다."
    concept: { front: "최적 기저선", back: "$\\mathbb{E}[\\lVert g\\rVert^2 Q]/\\mathbb{E}[\\lVert g\\rVert^2]$ — $V^\\pi$ 가 아니다" }
  - id: q3
    type: short
    prompt: "성능 차 보조정리 (3)에서 이점 $A^\\pi$ 를 평균하는 점유 분포는 어느 정책의 것인가? (pi 또는 pi')"
    answer: ["pi'", "pi prime", "π'", "새 정책", "pi′", "pi-prime", "'"]
    explanation: "$J(\\pi')-J(\\pi) = \\frac{1}{1-\\gamma}\\mathbb{E}_{s\\sim d^{\\pi'}}[A^\\pi]$ — 이점은 **낡은** 정책 $\\pi$ 의 것이지만 분포는 **새** 정책 $\\pi'$ 의 것이다. 이 불일치가 신뢰영역이 필요한 이유 전부다."
    concept: { front: "성능 차 보조정리의 분포", back: "$d^{\\pi'}$ (새 정책) 에서 $A^\\pi$ (낡은 정책의 이점) 를 평균한다 — 그래서 $d^{\\pi'}$ 를 $d^\\pi$ 로 바꾸는 대리 목적함수에 오차 항이 붙는다" }
  - id: q4
    type: single
    prompt: "실무 TRPO 가 $D_{\\mathrm{KL}}^{\\max}$ 를 평균 KL 로 바꾸면 무엇이 사라지는가?"
    choices:
      - "경사의 불편성"
      - "단조 개선 보장"
      - "자연 경사의 재매개화 불변성"
      - "대리 목적함수의 1차 일치"
    answer: 1
    explanation: "(4)의 짝지음 논증은 최악 상태의 KL 을 쓰므로, 평균으로 바꾸면 부등식이 성립하지 않고 단조 개선 보장이 사라진다. 불편성과 1차 일치는 영향받지 않는다. 그래서 실무 TRPO 는 정리의 알고리즘이 아니라 정리에서 영감을 받은 알고리즘이다."
    concept: { front: "실무 TRPO 와 정리의 간극", back: "$D^{\\max}_{\\mathrm{KL}} \\to \\bar{D}_{\\mathrm{KL}}$ 치환으로 단조 개선 보장이 사라지고, 선탐색이 그 자리를 메운다" }
  - id: q5
    type: truefalse
    prompt: "PPO 의 클리핑은 두 정책 사이의 KL 발산을 제약한다."
    answer: false
    explanation: "클리핑은 비율 $\\rho_t$ 가 $[1-\\epsilon, 1+\\epsilon]$ 를 벗어났을 때 그 표본의 기울기를 0 으로 만드는 장치다. 이미 이동한 양은 되돌리지 않고, 상태별 KL 을 직접 묶지도 않는다. 따라서 (4)의 전제가 성립하지 않아 단조 개선 보장이 없다."
    concept: { front: "PPO 클리핑이 하는 일", back: "비율이 구간을 벗어난 표본의 기울기를 0 으로 만든다 — KL 제약이 아니고 단조 개선 보장도 없다" }
```

## 이 단계 공부법

1. **(1)을 백지에서 유도한다 (90분)** — (6)→(7)→Neumann 급수 순서를 손으로 쓴다. 막히는
   곳은 거의 항상 $\nabla Q^\pi$ 를 $\nabla V^\pi$ 로 되돌리는 2단계다. S&B ch.13.2 와
   Sutton et al. 2000 의 정리 1 을 **같은 결과의 다른 표기**로 대조해 읽는다.
2. **기저선을 숫자로 만난다 (45분)** — 문제 P3 을 먼저 풀어 $V^\pi$ 기저선이 더 나쁜 예를
   손으로 계산한다. "이점을 쓰면 분산이 줄어든다"를 신앙이 아니라 조건부 사실로 바꾸는 것이
   목적이다. 그 다음 P5 로 행동 의존 기저선의 편향을 확인한다.
3. **성능 차 보조정리를 먼저, 신뢰영역을 나중에 (90분)** — (3)의 망원 전개는 짧고, 이것만
   손에 있으면 TRPO 부록 A 가 읽힌다. $d^{\pi'}$ 와 $d^\pi$ 의 교체가 유일한 근사라는 구조를
   먼저 파악하고, 그 다음 짝지음과 Pinsker 를 따라간다.
4. **구현으로 분산 서열을 확인한다 (105분)** — 재현 과제의 조건 1(해석적 불편성)을 먼저
   통과시킨 뒤 조건 2(분산 서열)로 간다. 순서를 바꾸면 분산이 큰 것인지 구현이 틀린 것인지
   구분할 수 없다. PPO 는 마지막에, 클리핑을 끈 버전과 함께 돌린다.
5. **논문 3편을 이론→구현 순서로 읽는다 (150분)** — Sutton et al.(정리) → TRPO(보장) →
   PPO(실무). 논문당 1페이지 노트는 **반드시** 쓴다. TRPO 노트에는 "정리가 보장하는 것"과
   "코드가 하는 것"을 두 열로 나란히 적는다.
6. **무엇을 못 하는지로 끝낸다 (60분)** — "열린 문제" 중 접촉 동역학 항목을 골라, 재현 과제의
   CartPole 에 접촉(벽에 부딪히는 경계)을 넣으면 (1)의 어느 가정이 먼저 흔들리는지 한 문단으로
   쓴다.

**통과 기준**: 백지에서 (1)과 (3)을 유도할 수 있고, (4)의 상수가 어디서 오고 왜 실무에서
공허한지 말할 수 있고, 최적 기저선이 $V^\pi$ 가 아닌 이유를 수치 예로 들 수 있고, 재현 과제의
네 조건을 만족하는 코드와 논문 3편의 노트를 갖고 있다.
