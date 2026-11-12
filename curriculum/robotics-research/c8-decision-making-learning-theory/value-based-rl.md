---
id: c8-value-based-rl
title: 가치 기반 RL 과 함수 근사
summary: >-
  선형 함수 근사에서 TD 가 언제 수렴하고 언제 발산하는지를 양쪽 다 증명 수준으로 다룬다.
  on-policy 에서 투영 Bellman 연산자가 가중 노름 수축임을 보여 수렴과 근사 오차 한계를 얻고,
  Baird 반례에서 기대 업데이트 행렬의 고윳값이 음의 실수부를 가져 발산함을 보인다. 마지막으로
  최댓값 연산자의 과대추정 편향을 정확히 계산하고 이중 추정기가 그것을 제거하는 이유를 쓴다.
objectives:
  - $\lVert P^\pi v\rVert_D \le \lVert v \rVert_D$ 를 증명하고 어디서 on-policy 가정이 쓰이는지 지적할 수 있다.
  - 투영 Bellman 연산자가 $\gamma$-수축임을 보이고 근사 오차 한계 $1/\sqrt{1-\gamma^2}$ 를 유도할 수 있다.
  - Baird 반례를 구성하고 기대 TD 업데이트 행렬의 스펙트럼으로 발산을 증명할 수 있다.
  - 잔차 경사법의 업데이트 행렬이 대칭 준정부호임을 보이고 왜 수렴하는지 설명할 수 있다.
  - $m$ 개 잡음 추정치의 최댓값 편향을 정확히 계산하고 이중 추정기가 그 편향을 없애는 이유를 쓸 수 있다.
  - 죽음의 삼요소(함수 근사·부트스트랩·off-policy) 중 하나를 빼면 어느 단계가 복구되는지 설명할 수 있다.
prerequisites: [c8-mdp-pomdp-bellman]
difficulty: 5
estimated_minutes: 540
tags: [value-based-rl, function-approximation, td-learning, dqn, overestimation, research]
activities:
  - id: c8-value-based-rl-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c8-value-based-rl-papers
    kind: paper
    title: 필독 논문 4편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 180
  - id: c8-value-based-rl-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 165
  - id: c8-value-based-rl-reproduction
    kind: reproduction
    title: 재현 과제 — Baird 반례의 발산과 잔차 경사법의 수렴 (R1)
    estimated_minutes: 90
  - id: c8-value-based-rl-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
papers:
  - id: baird1995-residual
    required: true
    role: seminal
    note: "§2-3"
  - id: tsitsiklis1997-td-function-approx
    required: true
    role: seminal
    note: "§3-5"
  - id: mnih2015-dqn
    required: true
    role: standard
    note: "Methods"
  - id: vanhasselt2016-double-q
    required: true
    role: standard
    note: "§3-4"
resources:
  - title: "Sutton & Barto, Reinforcement Learning: An Introduction (2nd ed.)"
    kind: book
    note: ch.9 (on-policy 근사), ch.10 (off-policy 근사), ch.11 (off-policy 방법의 불안정성). 1순위 교재. (공식 URL 미확인)
  - title: "van Hasselt et al. — Deep reinforcement learning and the deadly triad (2018)"
    url: https://arxiv.org/abs/1812.02648
    kind: paper
    note: 권장. 삼요소의 각 다리를 실험으로 분리한다.
  - title: "Fujimoto, van Hoof & Meger — Addressing function approximation error in actor-critic methods (2018)"
    url: https://arxiv.org/abs/1802.09477
    kind: paper
    note: 권장. 연속 행동에서의 과대추정과 쌍둥이 비평자(TD3).
---

# 가치 기반 RL 과 함수 근사

## 전제와 기호

`c8-mdp-pomdp-bellman` 의 MDP 표기와 Bellman 연산자를 쓴다. 추가 **권장 선수**:

- 선형대수: 가중 내적과 노름, 직교 투영, 비대칭 행렬의 스펙트럼, 비정규(non-normal) 행렬의
  과도 응답(`r0-linear-algebra-decompositions`).
- 확률: 정상분포, Jensen 부등식, 중요도 가중(importance ratio).
- ODE 관점의 확률 근사(stochastic approximation): 기대 업데이트의 ODE 가 안정하면 작은
  학습률의 확률적 반복도 같은 곳으로 간다는 사실(Robbins–Monro). 이 레슨은 **기대 업데이트**
  만 다루므로 ODE 수준의 논의로 충분하다.

표기 추가:

| 기호 | 뜻 |
|---|---|
| $\Phi \in \mathbb{R}^{n\times k}$ | 특징 행렬. 행 $\phi(s)^\top$ 이 상태 $s$ 의 특징 |
| $v_\theta = \Phi\theta$ | 선형 근사 가치함수, $\theta \in \mathbb{R}^k$ |
| $D = \operatorname{diag}(d)$ | 상태 가중. $\lVert v \rVert_D^2 = \sum_s d(s) v(s)^2$ |
| $\Pi$ | $\lVert\cdot\rVert_D$ 에서 $\operatorname{span}(\Phi)$ 로의 직교 투영. $\Pi = \Phi(\Phi^\top D\Phi)^{-1}\Phi^\top D$ |
| $\delta_t$ | TD 오차. $\delta_t = r_t + \gamma v_\theta(s_{t+1}) - v_\theta(s_t)$ |
| $\varrho_t$ | 중요도 비. $\varrho_t = \pi(a_t\mid s_t)/b(a_t\mid s_t)$ ($b$ 는 행동 정책) |
| $A, b$ | 기대 TD 업데이트. $A = \Phi^\top D(I - \gamma P^\pi)\Phi$, $b = \Phi^\top D r^\pi$ |
| $\mathrm{MSBE}$ | 평균 제곱 Bellman 오차. $\lVert T^\pi v_\theta - v_\theta \rVert_D^2$ |

기대 업데이트를 한 줄로 쓴다. 학습률 $\alpha$ 의 선형 TD(0)는

$$
\theta_{k+1} = \theta_k + \alpha\,(b - A\,\theta_k), \tag{1}
$$

즉 $\theta$ 의 오차가 선형 사상 $(I - \alpha A)$ 로 전파된다. **이 레슨의 모든 수렴·발산
판정은 $A$ 의 스펙트럼에 대한 진술이다.**

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (on-policy 수렴과 투영 Bellman 오차 한계) [D2]** — $d$ 가 $P^\pi$ 의 정상분포이면
  $\lVert P^\pi v \rVert_D \le \lVert v\rVert_D$ 이고, 따라서 $\Pi T^\pi$ 는 $\lVert\cdot\rVert_D$
  에서 $\gamma$-수축이다. 고정점 $v_{\mathrm{TD}} = \Phi\theta_{\mathrm{TD}}$ 가 유일하게 존재하고
  $$
  \lVert v_{\mathrm{TD}} - V^\pi \rVert_D \;\le\; \frac{1}{\sqrt{1-\gamma^2}}\,
    \lVert \Pi V^\pi - V^\pi \rVert_D . \tag{2}
  $$
  동시에 $A$ 의 대칭부가 정부호여서 (1)은 충분히 작은 $\alpha$ 에서 수렴한다.
- **R2 (off-policy 선형 TD 의 발산: Baird 반례) [D3]** — 7상태·8특징의 구체적 MDP 와 가중 $d$ 에서
  $A$ 의 고윳값이 **음의 실수부**를 갖는다:
  $$
  \min_i \operatorname{Re}\lambda_i(A) = -0.2392504642\ldots < 0, \tag{3}
  $$
  따라서 (1)은 모든 $\alpha > 0$ 에서 발산하고 $\lVert\theta_k\rVert$ 는 점근적으로
  $(1 + \alpha\,\lvert\lambda_{\min}\rvert)$ 배씩 커진다. 보상이 모두 0 이고 참 가치가
  $V^\pi \equiv 0$ 인데도 그렇다 — **발산은 잡음이 아니라 결정론적 사실이다.**
- **R3 (잔차 경사법의 수렴) [D2]** — MSBE 를 직접 경사하강하면 업데이트 행렬
  $B = \Phi^\top_\Delta D_\varrho \Phi_\Delta$ ($\Phi_\Delta$ 의 행은
  $\phi(s) - \gamma\,\mathbb{E}[\phi(s')]$)가 **대칭 준정부호**여서 MSBE 가 단조 비증가한다.
  대가는 (i) 수렴 지점이 투영 Bellman 고정점이 아니고 (ii) 확률적 전이에서 **이중 표본
  (double sampling)** 이 필요하다는 것이다.
- **R4 (최댓값의 과대추정 편향과 이중 추정기) [D2]** — $Q(s,a)$ 의 참값이 모두 같고 추정치가
  독립 잡음 $\eta_a$ 를 가지면 Jensen 으로
  $\mathbb{E}[\max_a \hat{Q}] \ge \max_a \mathbb{E}[\hat{Q}]$ 이고, $\eta_a \sim
  \mathrm{Unif}(-\epsilon,\epsilon)$ 일 때 편향은 **정확히**
  $$
  \mathbb{E}\big[\max_{a \in \mathcal{A}} \eta_a\big] = \epsilon\,\frac{m-1}{m+1},
    \qquad m = \lvert\mathcal{A}\rvert . \tag{4}
  $$
  두 독립 추정치 $\hat{Q}_A, \hat{Q}_B$ 로 **선택과 평가를 분리**하면
  $\mathbb{E}\big[\hat{Q}_B(\arg\max_a \hat{Q}_A(a))\big] = 0$ 으로 양의 편향이 사라진다
  (대신 아래쪽으로 치우친다).
- **R5 (죽음의 삼요소) [D1]** — 발산에는 ⓐ 함수 근사 ⓑ 부트스트랩 ⓒ off-policy 분포가 **모두**
  필요하다. Baird 반례에서 ⓐ를 빼면(특징을 one-hot 으로) $\min_i\operatorname{Re}\lambda_i(A)
  = (1-\gamma)/7 > 0$ 이 되어 수렴하고, ⓒ를 빼면 R1 이 적용된다. ⓑ를 빼면(몬테카를로)
  목표가 $\theta$ 와 무관해져 문제가 지도학습이 된다.

## 유도

### R1 — 가중 노름에서의 수축

**1단계: $P^\pi$ 는 $\lVert\cdot\rVert_D$ 에서 비확장이다.** $d$ 가 $P^\pi$ 의 **정상분포**
($d^\top P^\pi = d^\top$)라고 가정한다. Jensen 부등식(제곱은 볼록)으로

$$
\lVert P^\pi v\rVert_D^2 = \sum_s d(s)\Big(\sum_{s'} P^\pi_{ss'} v(s')\Big)^2
  \;\le\; \sum_s d(s) \sum_{s'} P^\pi_{ss'}\, v(s')^2
  = \sum_{s'} \Big(\underbrace{\sum_s d(s) P^\pi_{ss'}}_{= \,d(s')}\Big) v(s')^2
  = \lVert v \rVert_D^2 . \tag{5}
$$

**on-policy 가정이 들어가는 자리는 밑줄 친 등식 하나뿐이다.** $d$ 가 $P^\pi$ 의 정상분포가
아니면 그 등식이 $\le$ 도 $\ge$ 도 아니고, (5) 전체가 깨진다. 이것이 R2 의 씨앗이다.

**2단계: $T^\pi$ 는 $\gamma$-수축.** $T^\pi u - T^\pi v = \gamma P^\pi(u-v)$ 이므로 (5)에서
$\lVert T^\pi u - T^\pi v\rVert_D \le \gamma\lVert u - v\rVert_D$.

**3단계: $\Pi$ 는 비확장.** $\Pi$ 는 $\lVert\cdot\rVert_D$ 에 대한 직교 투영이므로
$\lVert \Pi x \rVert_D \le \lVert x \rVert_D$. 따라서 $\Pi T^\pi$ 는 $\gamma$-수축이고
Banach 로 고정점 $v_{\mathrm{TD}}$ 가 유일하다. 그 고정점을 $\theta$ 로 쓰면
$\Phi\theta = \Pi T^\pi \Phi\theta$ 이고, 정의를 풀면 $A\theta = b$ 다.

**4단계: 오차 한계 (2).** $v_{\mathrm{TD}} - V^\pi$ 를 투영 성분과 직교 성분으로 쪼갠다.
$v_{\mathrm{TD}} - \Pi V^\pi \in \operatorname{span}(\Phi)$ 이고 $\Pi V^\pi - V^\pi$ 는 그에
직교하므로 피타고라스가 성립한다:

$$
\lVert v_{\mathrm{TD}} - V^\pi\rVert_D^2
  = \lVert v_{\mathrm{TD}} - \Pi V^\pi\rVert_D^2 + \lVert \Pi V^\pi - V^\pi\rVert_D^2 .
$$

첫 항은 $v_{\mathrm{TD}} = \Pi T^\pi v_{\mathrm{TD}}$ 와 $\Pi V^\pi = \Pi T^\pi V^\pi$ 에서

$$
\lVert v_{\mathrm{TD}} - \Pi V^\pi\rVert_D = \lVert \Pi T^\pi v_{\mathrm{TD}} - \Pi T^\pi V^\pi \rVert_D
  \le \gamma \lVert v_{\mathrm{TD}} - V^\pi \rVert_D .
$$

합치면 $\lVert v_{\mathrm{TD}} - V^\pi\rVert_D^2 \le \gamma^2\lVert v_{\mathrm{TD}} - V^\pi\rVert_D^2
+ \lVert \Pi V^\pi - V^\pi\rVert_D^2$, 정리하면 (2)다.

**읽는 법**: (2)는 "TD 해는 최선의 근사($\Pi V^\pi$)보다 최대 $1/\sqrt{1-\gamma^2}$ 배 나쁘다"는
뜻이다. $\gamma = 0.99$ 에서 이 계수는 $7.09$ 이고 $\gamma = 0.999$ 에서 $22.4$ 다 — 할인이
1 에 가까워지면 **보장 자체가 느슨해진다**.

**가정이 깨지는 곳.** (5)의 정상성이 없으면 2–4단계가 전부 무효다. 또 (2)는 **고정점이
존재할 때**의 진술이고, $A$ 가 특이하면 고정점이 없거나 유일하지 않다. 특징이 선형 종속이면
$\Phi^\top D\Phi$ 가 특이해 $\Pi$ 자체가 정의되지 않는다.

### R2 — Baird 반례

**구성.** 상태 $1,\dots,7$. 행동은 두 개다.

- `solid`: 어느 상태에서든 상태 $7$ 로 간다.
- `dashed`: 상태 $1,\dots,6$ 중 하나로 균등하게 간다.

보상은 모두 $0$, $\gamma = 0.99$. 목표 정책은 $\pi(\texttt{solid}\mid s) = 1$, 행동 정책은
$b(\texttt{solid}\mid s) = 1/7$, $b(\texttt{dashed}\mid s) = 6/7$. 따라서
$\varrho = \pi/b = 7$ (solid) 또는 $0$ (dashed)다. 가중은 행동 정책이 방문하는 분포에 맞춘
$d(s) = 1/7$ (균등)로 둔다. 특징은 $\theta \in \mathbb{R}^8$ 에 대해

$$
v_\theta(s_i) = 2\theta_i + \theta_8 \;(i=1,\dots,6), \qquad v_\theta(s_7) = \theta_7 + 2\theta_8, \tag{6}
$$

즉 $\phi(s_i) = 2e_i + e_8$, $\phi(s_7) = e_7 + 2e_8$ 이다. **$\theta_8$ 이 모든 상태에
공유되는 것**이 함수 근사의 역할이다. 참 가치는 $V^\pi \equiv 0$ 이고 $\theta = 0$ 으로 정확히
표현된다 — 표현력 부족이 원인이 아니라는 뜻이다.

**기대 업데이트.** 중요도 가중 off-policy TD(0)의 기대 업데이트는 $r \equiv 0$ 이므로
$b = 0$ 이고

$$
A = \sum_{s} d(s)\, b(\texttt{solid}\mid s)\, \varrho \; \phi(s)\big(\phi(s) - \gamma\,\phi(s_7)\big)^\top
  = \frac{1}{7}\sum_{s=1}^{7} \phi(s)\big(\phi(s) - \gamma\phi(s_7)\big)^\top , \tag{7}
$$

( $d(s)\,b(\texttt{solid}\mid s)\,\varrho = \tfrac17\cdot\tfrac17\cdot 7 = \tfrac17$ ).
$\theta_{k+1} = (I - \alpha A)\theta_k$ 이므로 수렴은 **$A$ 의 모든 고윳값이 양의 실수부를
갖는가**에 달려 있다. (7)을 수치로 대각화하면

$$
\operatorname{spec}(A) = \{\,-0.2392504642,\; -0.0221781072,\; 0,\;
  \underbrace{0.5714285714,\dots}_{5\text{개}}\,\}, \tag{8}
$$

음의 실수부가 둘 있다. $\lambda < 0$ 방향의 성분은 매 반복 $(1 - \alpha\lambda) > 1$ 배로
커지므로 $\lVert\theta_k\rVert \to \infty$ 이고, 점근 성장률은 가장 음수인 고윳값이 지배해

$$
\frac{\lVert\theta_{k+1}\rVert}{\lVert\theta_k\rVert} \;\longrightarrow\; 1 + \alpha\,\lvert\lambda_{\min}\rvert
  = 1 + 0.2392504642\,\alpha . \tag{9}
$$

$\alpha = 0.01$, $\theta_0 = (1,1,1,1,1,1,10,1)$ 에서 $\lVert\theta_{20000}\rVert \approx 2.6\times10^{22}$
이고 (9)의 비는 $k \ge 5000$ 에서 $1.002393$ 에 소수점 6자리까지 일치한다.

**왜 음수가 나오는가(한 문단).** (7)의 각 항은 $\phi(s)$ 와 $\phi(s) - \gamma\phi(s_7)$ 의
**비대칭** 외적이다. on-policy 라면 (5)의 정상성이 $\sum_s d(s)\phi(s)\phi(s)^\top$ 쪽을
우세하게 만들어 대칭부가 정부호가 되는데, 여기서는 $d$ 가 균등인 반면 목표 정책의 전이는
상태 $7$ 로만 가므로 $\phi(s_7)$ 방향이 과대 반영된다. 공유 성분 $\theta_8$ 을 통해 상태 $7$
의 가치를 올리면 모든 상태의 가치가 함께 올라가고, 그것이 다시 목표를 올린다 — **자기
강화 고리**다. 이 고리는 세 요소(공유 특징, 부트스트랩 목표, 어긋난 분포)가 동시에 있어야만
닫힌다.

**가정이 깨지는 곳 = 삼요소의 절단.** 특징을 one-hot ($\Phi = I$, 표 형식)으로 바꾸면 (7)이
$A = \tfrac17\big(I - \gamma\,\mathbf{1}e_7^\top\big)$ 가 되고 고윳값은
$\{(1-\gamma)/7,\ 1/7\ (\times6)\}$ 로 **모두 양수**다. 실제로 $\alpha=0.01$ 에서
$\lVert\theta_k\rVert$ 는 $k\approx10^3$ 까지 $21.3$ 으로 **일시 증가한 뒤** 감소해
$k=2\times10^6$ 에서 $1.0\times10^{-11}$ 까지 간다. 이 과도 증가는 $A$ 가 **비정규**이기
때문이고, "고윳값이 모두 양수 ⇒ 노름이 단조 감소"가 **거짓**이라는 좋은 예다.

### R3 — 잔차 경사법

MSBE 를 직접 쓰면 목적함수가 $\theta$ 의 2차식이다. 전이가 결정론적인 Baird 설정에서
$\delta(s) = \gamma v_\theta(s_7) - v_\theta(s)$ 이고

$$
J_{\mathrm{MSBE}}(\theta) = \sum_s w(s)\,\big(\phi_\Delta(s)^\top\theta\big)^2,
  \qquad \phi_\Delta(s) := \phi(s) - \gamma\,\phi(s_7), \tag{10}
$$

$w(s) = d(s)b(\texttt{solid}\mid s)\varrho$. 경사하강 업데이트는
$\theta \leftarrow \theta - \alpha\, B\theta$, $B = \sum_s w(s)\,\phi_\Delta(s)\phi_\Delta(s)^\top$.
$B$ 는 **대칭 준정부호**(외적의 비음 가중합)이므로 고윳값이 모두 $\ge 0$ 이고,
$\alpha < 2/\lambda_{\max}(B)$ 에서 $J_{\mathrm{MSBE}}$ 가 단조 비증가한다. 수치로
$\operatorname{spec}(B) = \{0,\ 2.4\times10^{-5},\ 0.571\ (\times5),\ 2.235\}$ 이고,
$2.4\times10^{-5}$ 때문에 **수렴이 느리다** — $\alpha=0.05$, $2\times10^5$ 반복에서 MSBE 가
$3.4\times10^{-5}$ 다. 그래도 $\max_s\lvert v_\theta(s)\rvert \le 2$ 로 **유계**를 유지한다
(같은 조건의 TD 는 $10^{10}$ 을 넘는다).

**치르는 대가 두 가지.**
1. **다른 고정점**: $B\theta = 0$ 의 해는 투영 Bellman 고정점이 아니다. 일반적으로 MSBE
   최소해는 $\lVert \cdot \rVert_D$ 기준 최선 근사와도 다르고, 결정론 전이가 아니면 **잡음을
   벌점으로 세어** 과도하게 평활한 해로 간다.
2. **이중 표본**: 확률적 전이에서 $\nabla_\theta \mathbb{E}[\delta]^2 \ne \mathbb{E}[\nabla_\theta
   \delta^2]$ 이므로, 같은 $(s,a)$ 에서 **독립인 두 후속 상태** 표본이 필요하다. 시뮬레이터를
   되감을 수 없는 실제 로봇에서는 이 조건을 충족하기 어렵다 — 그래서 실무는 잔차 경사법 대신
   목표망(target network)으로 부트스트랩의 자기 강화를 끊는다.

### R4 — 과대추정과 이중 추정기

$m$ 개 행동의 참 가치가 모두 $0$ 이고 추정치가 $\hat{Q}(a) = \eta_a$ ($\eta_a$ 독립 동일분포,
$\mathbb{E}[\eta_a]=0$)라 하자. $\max$ 는 볼록이므로 Jensen 으로

$$
\mathbb{E}\big[\max_a \hat{Q}(a)\big] \;\ge\; \max_a \mathbb{E}\big[\hat{Q}(a)\big] = 0, \tag{11}
$$

즉 **최댓값 추정은 체계적으로 위로 치우친다**. 등호는 $\eta$ 가 상수일 때만 성립한다.
$\eta_a \sim \mathrm{Unif}(-\epsilon,\epsilon)$ 이면 $U_a = (\eta_a+\epsilon)/2\epsilon \sim
\mathrm{Unif}(0,1)$ 의 최댓값 기댓값이 $m/(m+1)$ 이므로

$$
\mathbb{E}[\max_a \eta_a] = -\epsilon + 2\epsilon\cdot\frac{m}{m+1} = \epsilon\,\frac{m-1}{m+1},
$$

(4)다. $\eta_a \sim \mathcal{N}(0,\sigma^2)$, $m=2$ 이면 $\mathbb{E}[\max] = \sigma/\sqrt{\pi}$.
이 편향은 $\gamma$ 를 통해 매 부트스트랩마다 누적되므로, 지평이 길수록 $Q$ 가 체계적으로
부풀고 **정책이 과대평가된 행동 쪽으로 쏠린다**.

**이중 추정기.** 독립인 두 추정치 $\hat{Q}_A, \hat{Q}_B$ 를 두고
$a^\star = \arg\max_a \hat{Q}_A(a)$ 를 **선택**에만, $\hat{Q}_B(a^\star)$ 를 **평가**에만 쓴다.
$a^\star$ 는 $\hat{Q}_A$ 의 함수이고 $\hat{Q}_B$ 와 독립이므로

$$
\mathbb{E}\big[\hat{Q}_B(a^\star)\big]
  = \sum_a \Pr(a^\star = a)\,\mathbb{E}\big[\hat{Q}_B(a)\big] = 0 . \tag{12}
$$

양의 편향이 사라졌다. 단 (12)는 "최댓값을 불편하게 추정한다"는 뜻이 **아니다** — 참값이
서로 다르면 $\mathbb{E}[\hat{Q}_B(a^\star)] \le \max_a \mathbb{E}[\hat{Q}(a)]$ 로 아래쪽으로
치우친다(문제 P7). 즉 이중 Q 는 편향의 **부호를 바꾸는** 장치다.

**가정이 깨지는 곳.** (12)는 $\hat{Q}_A \perp \hat{Q}_B$ 를 쓴다. Double DQN 은 온라인망으로
선택하고 목표망으로 평가하는데, 목표망은 온라인망의 **지연된 복사본**이라 독립이 아니다 —
그래서 편향이 줄기는 하지만 0 이 되지는 않는다. 또 (11)은 잡음이 행동 간 독립이라고 가정한다.
신경망은 행동 간 특징을 공유하므로 잡음이 상관되고, 상관이 완전하면 과대추정이 사라진다
(대신 행동 순위를 전혀 못 가린다).

## 증명 스케치

### R2 — Baird 반례의 발산 [D3]

**가설** H1: (6)의 특징과 위의 전이·정책·가중. H2: $\gamma = 0.99$. H3: 기대 업데이트 (1)을
쓴다(확률적 표본의 잡음은 논점이 아니다).
**결론** C: 모든 $\alpha > 0$ 에서 $\lVert\theta_k\rVert \to \infty$, 성장률은 (9).

**전략**: 선형 반복의 스펙트럼 판정. $\theta_{k+1} = (I-\alpha A)\theta_k$ 에서
$\rho(I - \alpha A) > 1$ 을 보인다.

1. (7)로 $A$ 를 명시적으로 쓴다. 쓰는 것: H1(특히 $\varrho$ 가 solid 에서만 0 이 아님).
2. $A$ 를 대각화해 (8)을 얻는다. 핵심은 $\lambda_{\min} < 0$ 이라는 **한 개의 수치 사실**이고,
   손으로 확인하려면 공유 성분 $\theta_8$ 과 $\theta_7$ 이 만드는 $2\times2$ 부분공간을
   분리하면 된다(생략: 나머지 5차원은 $\lambda = (1-\gamma\cdot\tfrac{?}{})\cdot\tfrac{4}{7}$
   형태로 분리된다 — Baird 1995 §3).
3. $\lambda < 0$ 이면 $\lvert 1 - \alpha\lambda\rvert = 1 + \alpha\lvert\lambda\rvert > 1$ 이므로
   그 고유방향 성분이 기하적으로 커진다 → C. 쓰는 것: H3.
4. 성장률은 지배 고유값이 결정한다 → (9).

**가설 하나를 지우면**: H1 에서 공유 특징 $\theta_8$ 을 지우면($\Phi = I$) $A$ 의 고윳값이
$\{(1-\gamma)/7,\ 1/7\}$ 로 전부 양수가 되어 C 가 거짓이다. 가중 $d$ 를 목표 정책의 정상분포로
바꾸면 R1 이 적용되어 역시 C 가 거짓이다. 즉 이 정리는 **세 조건의 결합에 대한 진술**이고,
어느 하나만 바꿔도 성립하지 않는다.

### R1 — 투영 Bellman 오차 한계 [D2 → 증명 형태]

**가설** H1: $d^\top P^\pi = d^\top$, $d > 0$. H2: $\Phi$ 가 열 완전계수. H3: $\gamma<1$.
**결론** C: $\Pi T^\pi$ 가 $\gamma$-수축, 고정점 유일, (2).

**전략**: 가중 노름에서의 수축 + 직교 투영의 비확장성 + 피타고라스.

1. Jensen 과 H1 로 (5). 쓰는 것: 제곱의 볼록성, 정상성.
2. $T^\pi$ 의 $\gamma$-수축(차가 $\gamma P^\pi(u-v)$).
3. $\Pi$ 비확장 → $\Pi T^\pi$ $\gamma$-수축 → Banach. 쓰는 것: H2($\Pi$ 의 well-definedness).
4. 피타고라스 + 2단계 → (2) → C.

**가설 하나를 지우면**: H1 을 지우면 1단계가 깨지고 R2 가 반례를 제공한다. H2 를 지우면 $\Pi$ 가
정의되지 않아 3단계가 무의미하다. H3 을 $\gamma\to1$ 로 밀면 수축 계수가 1 로 가고 (2)의 계수
$1/\sqrt{1-\gamma^2}$ 가 발산한다 — 보장은 형식적으로 남지만 **쓸모가 없어진다**.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** (5)를 빠진 줄 없이 쓰고, Baird 반례의 $d$(균등)와 목표 정책의 $P^\pi$
에 대해 (5)의 밑줄 친 등식이 구체적으로 어떻게 틀리는지 숫자로 보이라.
*해답 스케치*: Jensen 은 $d$ 와 무관하게 성립하고, 깨지는 것은 $\sum_s d(s)P^\pi_{ss'} = d(s')$
뿐이다. Baird 에서 $P^\pi$ 는 모든 질량을 $s_7$ 로 보내므로 좌변은 $s'=7$ 에서 $1$, 나머지에서
$0$ 인데 $d(s') = 1/7$ 이다. $v = e_7$ 같은 벡터로 $\lVert P^\pi v\rVert_D / \lVert v\rVert_D$ 를
계산해 $1$ 을 넘기는 예를 만든다.

**P2 (증명, ★★★, R1)** (2)를 증명하고, 등호에 가까워지는 경우를 하나 구성하라. 그 다음
$\gamma \in \{0.9, 0.99, 0.999\}$ 에서 계수 $1/\sqrt{1-\gamma^2}$ 를 계산해 보장이 얼마나
느슨해지는지 쓰라.
*전략과 핵심 부등식*: 피타고라스 분해 + $\lVert \Pi T v_{\mathrm{TD}} - \Pi T V^\pi\rVert_D \le
\gamma\lVert v_{\mathrm{TD}} - V^\pi\rVert_D$. 계수는 $2.29$, $7.09$, $22.4$. 등호 구성은
$\Phi$ 를 1차원으로 두고 $V^\pi$ 의 잔차를 $P^\pi$ 의 "가장 느린" 방향에 맞추는 것이다.
전개는 숨긴다.

**P3 (계산, ★, R4)** (4)를 유도하고 $\epsilon = 1$ 에 대해 $m = 2, 10, 100$ 의 편향을 구하라.
또 $\eta_a\sim\mathcal{N}(0,1)$, $m=2$ 의 편향을 닫힌 형태로 쓰라.
*정답*: $1/3 = 0.333333\ldots$, $9/11 = 0.818181\ldots$, $99/101 = 0.980198\ldots$ (허용오차
$10^{-9}$). 가우시안 $m=2$ 는 $1/\sqrt{\pi} = 0.5641895835\ldots$.
검산: $2\times10^6$ 표본 몬테카를로로 각 값을 재현하면 표준오차 $\approx 4\times10^{-4}$ 안에
들어온다. 이중 추정기의 평균은 같은 표본에서 $0$ 과 $3\sigma$ 이내로 일치해야 한다.

**P4 (구현, ★★, R2·R3)** Baird 반례의 기대 업데이트 (7)과 잔차 경사 업데이트 (10)을 구현해
$A$ 의 스펙트럼, $B$ 의 스펙트럼, 두 반복의 $\lVert\theta_k\rVert$ 궤적을 보고하라.
*루브릭*: ⓐ $\min\operatorname{Re}\lambda(A)$ 가 (3)과 $10^{-6}$ 이내로 일치 ⓑ $B$ 의 최소
고윳값이 $\ge -10^{-12}$ (대칭 PSD) ⓒ (9)의 점근 성장률을 $k\ge5000$ 에서 $10^{-5}$ 이내로
재현 ⓓ MSBE 가 단조 비증가임을 수치로 확인 ⓔ 중요도 비 $\varrho$ 를 상수 7 로 하드코딩하지 않고
$\pi/b$ 로 계산했다.

**P5 (반례, ★★, R2·R5)** Baird 반례를 **세 가지 서로 다른 방법**으로 수렴하게 만들라: (i) 함수
근사를 빼기, (ii) off-policy 를 빼기, (iii) 부트스트랩을 빼기. 각 경우 (7)의 $A$ 가 어떻게
바뀌고 고윳값이 어떻게 되는지 쓰라. 그리고 (i)에서 $\lVert\theta_k\rVert$ 가 **일시적으로
증가**하는 이유를 설명하라.
*성질 체크리스트*: (i) $\Phi = I$ → $A = \tfrac17(I - \gamma\mathbf{1}e_7^\top)$, 고윳값
$\{(1-\gamma)/7,\ 1/7\times6\}$ 전부 양수. (ii) $d$ 를 $\pi$ 의 정상분포로 → R1 적용, 대칭부
준정부호. (iii) 몬테카를로 목표 → $A = \Phi^\top D\Phi$ 로 대칭 정부호. 일시 증가는 $A$ 가
비정규여서 $\lVert(I-\alpha A)^k\rVert$ 가 초기에 1 을 넘기 때문이다(고윳값만으로는 과도 응답을
못 본다).

**P6 (논문, ★★, R2·R4·R5)** DQN(Methods)과 Double DQN(§3–4)을 읽고 다음을 각각 3문장 이내로
쓰라: (i) 경험 재생과 목표망이 삼요소의 어느 다리를 어떻게 약화하는가, (ii) Double DQN 의
목표망이 (12)의 독립 가정을 어기는데도 편향이 줄어드는 이유, (iii) 두 논문의 실험에서
재현에 필요한데 빠진 정보 3개.
*채점 루브릭*: (i) 재생은 off-policy 를 **더 심하게** 만들지만 샘플 상관을 깨고, 목표망은
부트스트랩의 자기 강화 고리를 지연시킨다 — 둘을 구분하면 통과. (ii) 지연된 복사본은 완전
독립은 아니지만 선택과 평가의 **잡음 상관을 낮춘다**는 점. (iii) 전처리·시드·평가 프로토콜
(no-op 시작, 에피소드 경계)·하이퍼파라미터 탐색 범위 중 3개. "성능이 좋아졌다"만 쓰면 미달.

**P7 (유도, ★★, R4)** (12)가 "최댓값의 불편 추정"이 아님을 보이라: 참 가치 $q_a$ 가 서로 다를 때
$\mathbb{E}[\hat{Q}_B(a^\star)] \le \max_a q_a$ 임을 증명하고, 등호 조건을 쓰라. $m=2$,
$q = (0, \Delta)$, $\eta \sim \mathcal{N}(0,\sigma^2)$ 에서 편향을 $\Delta/\sigma$ 의 함수로
스케치하라.
*해답 스케치*: $\mathbb{E}[\hat{Q}_B(a^\star)] = \sum_a \Pr(a^\star=a)\,q_a \le \max_a q_a$ —
확률 가중 평균이 최댓값을 넘을 수 없다. 등호는 $\Pr(a^\star = \arg\max q) = 1$ 일 때뿐이다.
$\Delta/\sigma \to 0$ 에서 편향 $\to -\Delta/2$, $\Delta/\sigma \to \infty$ 에서 $\to 0$.

## 논문 읽기

**필독 4편.** 각 논문에 고정 질문 10개로 1페이지 노트를 쓴다(`lesson-standard.md` §5).
3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Baird, "Residual algorithms: reinforcement learning with function approximation" (1995, ICML)**
   — 역할: `원전(seminal)`. <https://doi.org/10.1016/B978-1-55860-377-6.50013-X>
   읽는 이유: R2 의 반례와 R3 의 잔차 경사법이 모두 이 논문이다. §2–3 만 읽는다.
   추가 질문: ⓐ 저자가 제안하는 residual **gradient** 와 residual **algorithm**(두 업데이트의
   혼합)의 차이는 무엇이고, 혼합 계수는 무엇을 거래하는가?
   ⓑ 이중 표본 요구를 저자는 어떻게 다루는가, 그리고 로봇에서 그것이 왜 어려운가?
2. **Tsitsiklis & Van Roy, "An analysis of temporal-difference learning with function
   approximation" (1997, IEEE T-AC)** — 역할: `원전(seminal)`. <https://doi.org/10.1109/9.580874>
   읽는 이유: R1 의 (5)와 (2)가 이 논문의 정리다. §3–5 를 읽는다.
   추가 질문: ⓐ 저자들의 가정 중 "on-policy"에 해당하는 것을 정확히 어느 조건에서 쓰는가?
   ⓑ $\lambda > 0$ ($\mathrm{TD}(\lambda)$)에서 (2)의 계수가 어떻게 바뀌는가?
3. **Mnih et al., "Human-level control through deep reinforcement learning" (2015, Nature)** —
   역할: `표준(standard)`. <https://doi.org/10.1038/nature14236> (Methods 절 중심)
   읽는 이유: 삼요소를 그대로 둔 채 **공학적으로** 안정화한 사례다. 보장은 없지만 무엇이
   작동했는지가 중요하다.
   추가 질문: ⓐ 목표망 갱신 주기 $C$ 를 0 과 $\infty$ 로 밀면 각각 무엇이 되는가?
   ⓑ 보상 클리핑이 (2)의 어느 항에 영향을 주는가?
4. **van Hasselt, Guez & Silver, "Deep reinforcement learning with double Q-learning" (2016, AAAI)**
   — 역할: `표준(standard)`. <https://arxiv.org/abs/1509.06461> (§3–4)
   읽는 이유: R4 의 (4)·(12)를 실제 규모에서 **측정**한 글이다.
   추가 질문: ⓐ 저자들이 과대추정을 측정하는 방법(참값을 무엇으로 대체하는가)은 공정한가?
   ⓑ 편향이 줄었는데 성능이 거의 그대로인 게임이 있다면 그것은 무엇을 뜻하는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R1 (수치 검증).** 계산 예산: 노트북 CPU **10초 이내**(측정값 약 3초), 메모리 100 MB
이내, numpy 만. 데이터는 필요 없다 — 반례가 $7\times8$ 행렬 하나다.

Baird 반례를 구성해 ⓐ 중요도 가중 TD 가 발산하고 ⓑ 잔차 경사법이 수렴하며 ⓒ 삼요소 중 하나를
빼면 TD 도 수렴함을 보인다. 특징·전이·정책·가중은 R2 의 구성을 그대로 쓰고
$\theta_0 = (1,1,1,1,1,1,10,1)$, $\alpha = 0.01$ (TD) 과 $\alpha = 0.05$ (잔차 경사)로 둔다.

**수용 기준** — 네 조건을 모두 만족해야 통과다.

1. **스펙트럼**: (7)의 $A$ 에 대해
   $\lvert \min_i \operatorname{Re}\lambda_i(A) - (-0.2392504642)\rvert < 10^{-6}$ 이고, (10)의
   $B$ 는 대칭($\lVert B - B^\top\rVert_\infty < 10^{-12}$)이며 $\lambda_{\min}(B) \ge -10^{-12}$.
2. **TD 의 발산**: $\alpha=0.01$, $k \le 20000$ 에서 $\lVert\theta_k\rVert$ 가 **단조 증가**하고
   $\lVert\theta_{20000}\rVert > 10^{20}$ 이며, $k\ge5000$ 에서
   $\big\lvert \lVert\theta_{k+1}\rVert/\lVert\theta_k\rVert - (1+0.2392504642\,\alpha)\big\rvert < 10^{-5}$.
3. **잔차 경사법의 수렴**: $\alpha=0.05$, $2\times10^5$ 반복에서 MSBE 가 **단조 비증가**
   (허용 $10^{-18}$ 의 수치 여유)이고 $\mathrm{MSBE} < 10^{-4}$, 그리고 전 구간에서
   $\max_s\lvert v_\theta(s)\rvert \le 2$. 같은 $k$ 에서 TD 는
   $\max_s\lvert v_\theta(s)\rvert > 10^{10}$ 이다.
4. **삼요소 절단**: 특징을 one-hot 으로 바꾼 $A_{\text{tab}}$ 에 대해
   $\lvert \min_i\operatorname{Re}\lambda_i(A_{\text{tab}}) - (1-\gamma)/7\rvert < 10^{-9}$ 이고,
   $\alpha=0.01$ 로 $2\times10^6$ 반복하면 $\lVert\theta_k\rVert < 10^{-9}$ 가 된다. 동시에
   그 궤적이 **단조가 아님**($k\approx10^3$ 에서 $\lVert\theta\rVert > \lVert\theta_0\rVert$)을
   확인한다.

**비교 대상(베이스라인)**: ⓐ 표 형식(one-hot) TD — 조건 4 가 그 역할을 한다. ⓑ $\theta$ 를
닫힌 형태로 구한 투영 Bellman 해: on-policy 가중에서는 $A\theta = b$ 를 직접 풀어 반복 해와
$10^{-9}$ 이내로 일치해야 한다. ⓒ 선택: $\mathrm{TD}(\lambda)$ 를 $\lambda = 0.9$ 로 돌려
발산이 완화되는지(사라지지는 않는다) 확인.

**참고 출력**(numpy 2.x): $\operatorname{spec}(A)$ 는 (8),
$\operatorname{spec}(B) = \{0,\ 2.4\times10^{-5},\ 0.5714\ (\times5),\ 2.2348\}$,
TD 는 $\lVert\theta_{1000}\rVert = 436.9$, $\lVert\theta_{20000}\rVert = 2.56\times10^{22}$,
성장률 $1.002393$; 잔차 경사법은 MSBE $3.39\times10^{-5}$,
$\max_s\lvert v\rvert = 1.54$; one-hot TD 는 $\lVert\theta_{10^3}\rVert = 21.3$ 에서
$\lVert\theta_{2\times10^6}\rVert = 1.0\times10^{-11}$. **이 값들은 결정론적이므로 (난수가
없다) 재현되지 않으면 구현이 틀린 것이다** — 재현 과제 중 유일하게 숫자가 그대로 맞아야 하는
경우다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| $\min\operatorname{Re}\lambda(A) > 0$ 이 나온다 | 중요도 비를 빼먹었거나 dashed 행동에도 $\varrho>0$ 을 줬다 | $\varrho = \pi/b$ 를 출력한다 — solid 에서 $7$, dashed 에서 $0$ 이어야 한다 |
| TD 가 수렴한다 | 특징에서 공유 성분 $\theta_8$ 을 빼먹었다 | $\Phi$ 의 마지막 열이 $(1,1,1,1,1,1,2)^\top$ 인지 확인한다 |
| 성장률이 (9)와 다르다 | $k$ 가 작아 지배 고유모드가 아직 안 섰다 | $k=1000$ 과 $k=10000$ 의 비를 함께 출력한다($1.002656$ vs $1.002393$) |
| 잔차 경사법도 발산한다 | $\phi_\Delta$ 에 $-\gamma\phi(s_7)$ 를 빼먹어 $B$ 가 비대칭이 됐다 | $\lVert B-B^\top\rVert_\infty$ 를 출력한다 |
| MSBE 가 $10^{-4}$ 아래로 안 내려간다 | $B$ 의 최소 비영 고윳값이 $2.4\times10^{-5}$ 라 느리다 | 반복 수를 $2\times10^5$ 이상으로 늘리거나 $\alpha$ 를 $2/\lambda_{\max}$ 근처로 올린다 |
| one-hot TD 가 발산한다고 보고된다 | 노름이 일시 증가하는 구간만 보고 판단했다 | $k$ 를 $2\times10^6$ 까지 늘려 본다 — 비정규 행렬의 과도 응답이다 |

## 열린 문제

- **(열린 문제) 심층 신경망에서의 삼요소 — 무엇이 실제로 불안정을 만드는가** — 선형 사례에서는
  (3)처럼 발산이 스펙트럼으로 깔끔히 판정되지만, 심층망에서는 특징이 학습되며 변하므로
  $A$ 자체가 시간에 따라 바뀐다. 목표망·재생 버퍼·정규화가 왜 작동하는지에 대한 이론은 없고,
  실험적 분해만 있다(현재 접근:
  [van Hasselt et al. 2018](https://arxiv.org/abs/1812.02648)). 비어 있는 자리: 학습되는
  특징에서 발산을 예측하는 진단량.
- **(열린 문제) 투영 Bellman 오차와 실제 정책 성능의 연결** — (2)는 **가치 오차**의 한계이고
  정책 성능과는 $\lVert V^{\pi_v} - V^\*\rVert \le 2\gamma\lVert v - V^\*\rVert/(1-\gamma)$ 로만
  이어진다. 이 두 단계의 느슨함이 곱해지면 $\gamma=0.99$ 에서 보장이 사실상 사라진다. 현재
  접근: 정책 경사의 전역 수렴 분석([Agarwal et al. 2019](https://arxiv.org/abs/1908.00261)).
  비어 있는 자리: 가치 근사 품질에서 정책 성능으로 가는 타이트한 경로.
- **(열린 문제) 과대추정의 부호를 선택하는 원칙** — 이중 Q 는 양의 편향을 음의 편향으로
  바꾸고, TD3 의 쌍둥이 최솟값은 더 보수적으로 민다. 어느 부호·크기가 과제에 맞는지에 대한
  기준은 없다 — 오프라인 설정에서는 보수성이 **이득**이지만(`c8-offline-rl`) 탐색이 필요한
  설정에서는 손해다. 현재 접근:
  [Double DQN](https://arxiv.org/abs/1509.06461), [TD3](https://arxiv.org/abs/1802.09477).
  비어 있는 자리: 편향 부호를 과제 특성과 연결하는 규칙.
- **(열린 문제) 로봇 규모에서 잔차 경사법의 이중 표본 요구를 우회하기** — R3 의 수렴 보장은
  같은 상태에서 독립인 두 후속 표본을 요구하는데, 실제 로봇에서는 상태를 되감을 수 없다.
  모델을 학습해 두 번째 표본을 만드는 접근은 모델 오차를 들여온다
  (`c8-model-based-world-models`). 현재 접근: 경사 TD 계열(S&B ch.11.7 의 GTD2·TDC).
  비어 있는 자리: 되감기 없이 MSBE 의 참 경사를 얻는 추정기.

## 개념 점검

`rc quiz c8-value-based-rl` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위 문제
세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c8-value-based-rl-quiz
questions:
  - id: q1
    type: single
    prompt: "$\\lVert P^\\pi v\\rVert_D \\le \\lVert v\\rVert_D$ 의 증명에서 on-policy 가정이 쓰이는 자리는?"
    choices:
      - "제곱의 볼록성(Jensen)을 적용하는 단계"
      - "$\\sum_s d(s) P^\\pi_{ss'} = d(s')$ 라는 정상성 등식"
      - "$\\gamma < 1$ 로 수축 계수를 뽑는 단계"
      - "직교 투영 $\\Pi$ 가 비확장이라는 단계"
    answer: 1
    explanation: "Jensen 은 $d$ 와 무관하게 성립하고 $\\Pi$ 의 비확장성도 $P^\\pi$ 와 무관하다. 깨지는 것은 $d$ 가 $P^\\pi$ 의 정상분포라는 등식 하나뿐이며, Baird 반례는 바로 그 등식을 위반한다(가중은 균등, 목표 정책은 모든 질량을 한 상태로 보낸다)."
    concept: { front: "on-policy 가정이 들어가는 자리", back: "$d^\\top P^\\pi = d^\\top$ (정상성) 한 줄 — 이것만 깨지면 수축 논증 전체가 무너진다" }
  - id: q2
    type: truefalse
    prompt: "Baird 반례에서 선형 TD 가 발산하는 것은 참 가치함수를 특징으로 표현할 수 없기 때문이다."
    answer: false
    explanation: "참 가치는 $V^\\pi \\equiv 0$ 이고 $\\theta = 0$ 으로 **정확히** 표현된다. 발산의 원인은 표현력 부족이 아니라 기대 업데이트 행렬 $A$ 의 고윳값이 음의 실수부를 갖는 것이고, 그 원인은 공유 특징·부트스트랩·어긋난 분포의 결합이다."
    concept: { front: "Baird 발산의 원인", back: "표현력 부족이 아니다 — $A$ 의 음의 실수부 고윳값(삼요소의 결합)" }
  - id: q3
    type: short
    prompt: "$m$ 개의 독립 $\\mathrm{Unif}(-\\epsilon,\\epsilon)$ 잡음의 최댓값 기댓값을 $\\epsilon, m$ 으로 쓰면? (분수 형태로)"
    answer: ["eps(m-1)/(m+1)", "ε(m-1)/(m+1)", "epsilon(m-1)/(m+1)", "e(m-1)/(m+1)", "\\epsilon(m-1)/(m+1)", "(m-1)/(m+1)"]
    explanation: "$U \\sim \\mathrm{Unif}(0,1)$ 의 최댓값 기댓값이 $m/(m+1)$ 이므로 $-\\epsilon + 2\\epsilon m/(m+1) = \\epsilon(m-1)/(m+1)$ 이다. $m$ 이 커지면 $\\epsilon$ 에 수렴하고, 이 편향이 부트스트랩마다 누적된다."
    concept: { front: "최댓값 과대추정 편향(균등 잡음)", back: "$\\epsilon(m-1)/(m+1)$ — 행동 수가 많아지면 $\\epsilon$ 에 수렴" }
  - id: q4
    type: single
    prompt: "잔차 경사법이 수렴하는 구조적 이유는?"
    choices:
      - "목표가 $\\theta$ 에 의존하지 않기 때문"
      - "업데이트 행렬 $B$ 가 외적의 비음 가중합이라 대칭 준정부호이기 때문"
      - "중요도 비가 1 이 되기 때문"
      - "학습률을 충분히 작게 잡기 때문"
    answer: 1
    explanation: "$B = \\sum_s w(s)\\phi_\\Delta(s)\\phi_\\Delta(s)^\\top$ 는 대칭이고 고윳값이 모두 $\\ge 0$ 이므로 $\\alpha < 2/\\lambda_{\\max}$ 에서 MSBE 가 단조 비증가한다. 목표는 여전히 $\\theta$ 에 의존하고(부트스트랩은 남아 있다), 작은 학습률만으로는 TD 의 발산을 막을 수 없다."
    concept: { front: "잔차 경사법의 수렴 근거", back: "$B$ 가 대칭 PSD — 대가는 다른 고정점과 이중 표본 요구" }
  - id: q5
    type: truefalse
    prompt: "이중 추정기는 $\\max_a \\mathbb{E}[\\hat{Q}(a)]$ 를 불편하게 추정한다."
    answer: false
    explanation: "선택과 평가를 분리하면 참값이 모두 같을 때 편향이 0 이 되지만, 참값이 서로 다르면 $\\mathbb{E}[\\hat{Q}_B(a^\\star)] = \\sum_a \\Pr(a^\\star=a) q_a \\le \\max_a q_a$ 로 아래쪽으로 치우친다. 이중 Q 는 편향을 없애는 장치가 아니라 **부호를 바꾸는** 장치다."
    concept: { front: "이중 추정기가 하는 일", back: "양의 편향을 음의 편향으로 바꾼다 — 불편 추정기가 아니다" }
```

## 이 단계 공부법

1. **수축을 가중 노름에서 다시 배운다 (60분)** — (5)를 백지에서 쓰고, 밑줄 친 정상성 등식에
   동그라미를 친다. `c8-mdp-pomdp-bellman` 의 sup-노름 수축과 **무엇이 달라졌는지**를 한 문단으로
   적는다. S&B ch.9.4 와 Tsitsiklis–Van Roy §3 을 대조해 읽는다.
2. **오차 한계의 계수를 숫자로 만난다 (45분)** — (2)를 유도하고 $\gamma$ 세 값에서 계수를
   계산한다($2.29$, $7.09$, $22.4$). "TD 는 수렴한다"는 말이 **무엇을 보장하지 않는지**가
   이 숫자에 있다.
3. **반례를 손으로 만든다 (90분)** — (6)의 특징과 (7)의 $A$ 를 직접 적고, numpy 로 고윳값을
   확인한 뒤 **왜 음수가 나오는지**를 공유 성분 $\theta_8$ 의 자기 강화 고리로 설명해 본다.
   먼저 구성하고 나중에 Baird 1995 §3 과 대조한다 — 순서를 바꾸면 "읽은 것"이 되고 만다.
4. **삼요소를 하나씩 끊어 본다 (90분)** — 재현 과제 조건 4 를 세 변형(one-hot / on-policy /
   몬테카를로) 모두에 대해 돌린다. 특히 one-hot 에서 노름이 **일시 증가**하는 것을 직접 보고,
   고윳값만으로 과도 응답을 판단할 수 없다는 사실을 기억에 남긴다.
5. **논문 4편을 이론→실무 순서로 읽는다 (180분)** — Baird(반례) → Tsitsiklis–Van Roy(수렴) →
   DQN(공학적 안정화) → Double DQN(편향 측정). 논문당 1페이지 노트는 **반드시** 쓴다. DQN
   노트에는 "삼요소 중 어느 다리를 건드렸는가"를 한 줄로 적는다.
6. **무엇을 못 하는지로 끝낸다 (75분)** — "열린 문제" 중 심층망의 삼요소 항목을 골라, 재현
   과제의 $A$ 를 학습되는 특징으로 바꾸면 무엇을 더는 계산할 수 없는지 한 문단으로 쓴다.

**통과 기준**: 백지에서 (5)와 (2)를 유도할 수 있고, Baird 반례를 구성해 $A$ 의 음의 고윳값을
보일 수 있고, (4)를 유도해 숫자를 댈 수 있고, 재현 과제의 네 조건을 만족하는 코드와 논문
4편의 노트를 갖고 있다.
