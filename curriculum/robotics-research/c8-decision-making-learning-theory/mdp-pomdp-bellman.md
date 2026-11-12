---
id: c8-mdp-pomdp-bellman
title: MDP·POMDP 와 Bellman 최적성
summary: >-
  순차 의사결정의 바탕이 되는 Bellman 최적 연산자를 sup-노름 수축 사상으로 증명하고, 가치
  반복과 정책 반복의 수렴률·정지 규칙을 기계적으로 쓸 수 있는 형태까지 유도한다. 이어서
  부분 관측 문제를 신념(belief) MDP 로 바꾸고, 유한 지평 POMDP 가치함수가 조각마다 선형이고
  볼록(PWLC)임을 알파 벡터 역행으로 보인다.
objectives:
  - Bellman 최적 연산자가 sup-노름에서 $\gamma$-수축임을 빠진 줄 없이 증명할 수 있다.
  - 수축성과 Banach 고정점 정리로 $V^\*$ 의 존재·유일성과 그리디 정책의 최적성을 재구성할 수 있다.
  - 가치 반복의 오차 상한과 정지 규칙 $\lVert V_{k+1}-V_k \rVert_\infty < \epsilon(1-\gamma)/(2\gamma)$ 를 유도할 수 있다.
  - 정책 반복의 단조 개선과 유한 종료를 증명하고 가치 반복과의 관계를 설명할 수 있다.
  - POMDP 를 신념 MDP 로 변환하고 유한 지평 가치함수의 PWLC 성질을 알파 벡터로 쓸 수 있다.
  - 할인율·보상 유계성 가정이 깨질 때 어느 단계가 먼저 무너지는지 지적할 수 있다.
prerequisites: []
difficulty: 4
estimated_minutes: 480
tags: [mdp, pomdp, bellman, dynamic-programming, contraction, research]
activities:
  - id: c8-mdp-pomdp-bellman-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c8-mdp-pomdp-bellman-papers
    kind: reading
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c8-mdp-pomdp-bellman-problems
    kind: exercise
    title: 문제 세트 (유도 1 · 증명 1 · 계산 2 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 150
  - id: c8-mdp-pomdp-bellman-reproduction
    kind: exercise
    title: 재현 과제 — 가치 반복의 $\gamma^k$ 오차 감소 검증 (R1)
    estimated_minutes: 75
  - id: c8-mdp-pomdp-bellman-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Sutton & Barto, Reinforcement Learning: An Introduction (2nd ed.)"
    kind: book
    note: ch.3 (유한 MDP), ch.4 (동적 계획법). 이 레슨의 1순위 교재. (공식 URL 미확인)
  - title: "LaValle, Planning Algorithms"
    url: https://lavalle.pl/planning/
    kind: book
    note: ch.10 (불확실성 하 순차 의사결정), ch.11 (센서와 정보 공간), ch.12. 전문 무료.
  - title: "Blackwell — Discounted dynamic programming (1965)"
    url: https://doi.org/10.1214/aoms/1177700285
    kind: article
    note: 필독 1. 할인 DP 의 수축 논증과 최적 정책 존재의 원전.
  - title: "Smallwood & Sondik — The optimal control of partially observable Markov processes over a finite horizon (1973)"
    url: https://doi.org/10.1287/opre.21.5.1071
    kind: article
    note: 필독 2. PWLC 가치함수와 알파 벡터의 원전.
  - title: "Kaelbling, Littman & Cassandra — Planning and acting in partially observable stochastic domains (1998)"
    url: https://doi.org/10.1016/S0004-3702(98)00023-X
    kind: article
    note: 필독 3. 신념 MDP 변환과 POMDP 계획의 표준 참조.
  - title: "Papadimitriou & Tsitsiklis — The complexity of Markov decision processes (1987)"
    url: https://doi.org/10.1287/moor.12.3.441
    kind: article
    note: 권장. MDP·POMDP 의 복잡도 분류(유한 지평 POMDP 는 PSPACE-완전).
  - title: "Madani, Hanks & Condon — On the undecidability of probabilistic planning (2003)"
    url: https://doi.org/10.1016/S0004-3702(02)00378-8
    kind: article
    note: 권장. 무한 지평 POMDP 의 결정 불가능성.
  - title: "Sunberg & Kochenderfer — Online algorithms for POMDPs with continuous spaces (2017)"
    url: https://arxiv.org/abs/1709.06196
    kind: article
    note: 권장. 연속 상태·관측 POMDP 의 온라인 계획(POMCPOW)과 입자 붕괴 문제.
---

# MDP·POMDP 와 Bellman 최적성

## 전제와 기호

이 레슨은 C8 모듈의 첫 레슨이고, 이후 모든 레슨(정책 경사·가치 기반·모델 기반·오프라인)이
여기의 연산자 표기와 수축 논증을 재사용한다. 다음을 **권장 선수**로 둔다(플랫폼이 잠그지는
않는다 — 아래 자가 진단으로 직접 판단한다):

- 해석: 완비 거리공간, Banach 고정점 정리, sup-노름, 단조 수렴.
- 선형대수: 행렬의 스펙트럼 반지름, $(I - \gamma P)^{-1}$ 의 Neumann 급수.
- 확률: 조건부 기댓값, Markov 성질, 충분통계량(sufficient statistic).
- 최적 제어의 DP 는 **요구하지 않는다** — 유한 지평 LQR 과의 대응은 `c8-control-as-inference`
  에서 다시 다룬다.

표기 규약(C8 모듈 전체에 고정):

| 기호 | 뜻 |
|---|---|
| $\mathcal{S}, \mathcal{A}$ | 유한 상태·행동 집합. $\lvert \mathcal{S} \rvert = n$, $\lvert \mathcal{A} \rvert = m$ |
| $P(s' \mid s, a)$ | 전이 확률. 행렬 표기 $P^\pi \in \mathbb{R}^{n \times n}$, $(P^\pi)_{ss'} = \sum_a \pi(a \mid s) P(s' \mid s,a)$ |
| $r(s,a)$ | 보상. $\lvert r(s,a) \rvert \le R_{\max} < \infty$ (가정 **A1**) |
| $\gamma$ | 할인율. $0 \le \gamma < 1$ (가정 **A2**) |
| $\pi(a \mid s)$ | 정상(stationary) 확률 정책. 결정론 정책은 $\pi : \mathcal{S} \to \mathcal{A}$ |
| $V^\pi \in \mathbb{R}^n$ | $V^\pi(s) = \mathbb{E}^\pi\!\left[\sum_{t\ge0} \gamma^t r(s_t,a_t) \mid s_0 = s\right]$ |
| $V^\*, Q^\*$ | 최적 가치함수. $V^\*(s) = \sup_\pi V^\pi(s)$ |
| $T^\pi, T^\*$ | Bellman 기대 연산자와 최적 연산자(아래 (1)·(2)) |
| $\lVert v \rVert_\infty$ | $\max_s \lvert v(s) \rvert$. 이 레슨의 모든 수축은 이 노름에서다 |
| $b \in \Delta(\mathcal{S})$ | 신념(belief). $b(s) \ge 0$, $\sum_s b(s) = 1$ |
| $\mathcal{O}, O(o \mid s', a)$ | 관측 집합과 관측 모형 |
| $\alpha \in \mathbb{R}^n$ | 알파 벡터. $V(b) = \max_\alpha \langle \alpha, b \rangle$ |

두 연산자를 정의한다. $v \in \mathbb{R}^n$ 에 대해

$$
(T^\pi v)(s) = \sum_a \pi(a \mid s)\Big[r(s,a) + \gamma \sum_{s'} P(s' \mid s,a)\, v(s')\Big], \tag{1}
$$

$$
(T^\* v)(s) = \max_{a \in \mathcal{A}} \Big[r(s,a) + \gamma \sum_{s'} P(s' \mid s,a)\, v(s')\Big]. \tag{2}
$$

$v$ 에 대해 그리디(greedy) 정책은 (2)의 $\max$ 를 달성하는 행동을 고르는 결정론 정책
$\pi_v(s) \in \arg\max_a [\,\cdot\,]$ 다. 동점은 아무렇게나 깨도 아래 결과가 바뀌지 않는다.

## 시작 전 자가 진단

C8 모듈의 첫 레슨이므로 모듈 전체의 선수지식을 여기서 점검한다. 아래 5문항은 **모두 채점
가능**하다 — 종이와 계산기로 10분 안에 풀고 정답과 맞춰 본다. 3문항 이상 맞으면 이 모듈을
바로 시작한다. 2문항 이하면 각 문항에 적힌 선수 레슨을 먼저 본다. 선수는 **권장**이고
플랫폼이 잠그지 않는다.

**D1 (선형 해, 선수: `r0-linear-algebra-decompositions`)** $\gamma = 0.9$,
$P = \begin{bmatrix} 0.5 & 0.5 \\ 0 & 1\end{bmatrix}$, $r = (2, 0)^\top$ 인 Markov 보상
과정에서 $V = (I - \gamma P)^{-1} r$ 의 첫 성분을 구하라.
*정답*: $V(s_0) = 2/0.55 = 40/11 = 3.636363\ldots$, $V(s_1) = 0$. 허용오차 $10^{-9}$.

**D2 (수축, 선수: 해석학 — Banach 고정점 정리)** $\lvert \max_a f(a) - \max_a g(a) \rvert
\le L \max_a \lvert f(a) - g(a)\rvert$ 가 성립하는 가장 작은 상수 $L$ 은?
*정답*: $L = 1$. (등호는 $f, g$ 가 같은 $a$ 에서 최대가 될 때 달성된다.)

**D3 (기하급수, 선수: `r0-estimation-theory` 또는 S&B ch.3)** $\lvert r \rvert \le 2$,
$\gamma = 0.95$ 일 때 $\lvert V^\pi(s) \rvert$ 의 가능한 최댓값은?
*정답*: $2/(1-0.95) = 40$. 허용오차 $10^{-9}$. (이 상한이 A1 이 (4)에서 하는 일 전부다.)

**D4 (볼록성, 선수: `r0-convex-optimization`)** 단체 $b = (p, 1-p)$ 위에서
$f(b) = \max\big(\langle (1,0), b\rangle,\ \langle (0,2), b\rangle\big)$ 의 두 선형 조각이
교차하는 $p$ 와 그때의 $f$ 값을 구하라.
*정답*: $p = 2/3$, $f = 2/3$. 허용오차 $10^{-9}$. ($f$ 는 조각마다 선형이고 볼록 — R4 의 PWLC 가
바로 이 구조의 $n$ 차원 버전이다.)

**D5 (Bayes 갱신, 선수: `r0-estimation-theory`)** 상태가 바뀌지 않고
$\Pr(o \mid s_0) = 0.9$, $\Pr(o \mid s_1) = 0.3$ 일 때 $b(s_0) = 0.5$ 에서 $o$ 를 한 번 관측한
뒤의 $b'(s_0)$ 를 구하라.
*정답*: $0.45/0.6 = 0.75$. 허용오차 $10^{-12}$.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (Bellman 최적 연산자는 $\gamma$-수축이고 고정점은 유일하며 $V^\*$ 와 같다) [D3]** —
  A1·A2 아래 모든 $u, v$ 에 대해
  $$\lVert T^\* u - T^\* v \rVert_\infty \le \gamma \lVert u - v \rVert_\infty, \tag{3}$$
  따라서 $T^\* v = v$ 인 $v$ 가 유일하게 존재한다. 그 $v$ 는 $V^\*$ 이고, $v$ 에 대한 그리디
  정책 $\pi_v$ 는 **정상·결정론 정책으로 최적**이다. 같은 결론이 각 $\pi$ 에 대한 $T^\pi$ 와
  $V^\pi$ 에도 성립한다.
- **R2 (가치 반복의 수렴률·정지 규칙과 정책 반복의 유한 종료) [D3]** —
  $V_{k+1} = T^\* V_k$ 로 두면
  $$\lVert V_k - V^\* \rVert_\infty \le \gamma^k \lVert V_0 - V^\* \rVert_\infty, \tag{4}$$
  이고 $\pi_k$ 를 $V_k$ 에 대한 그리디 정책이라 하면
  $$\lVert V^{\pi_k} - V^\* \rVert_\infty \le \frac{2\gamma}{1-\gamma}\,\lVert V_{k+1} - V_k \rVert_\infty. \tag{5}$$
  그러므로 $\lVert V_{k+1} - V_k \rVert_\infty < \epsilon(1-\gamma)/(2\gamma)$ 에서 멈추면
  $\pi_k$ 는 $\epsilon$-최적이다. 정책 반복은 매 반복에서 $V^{\pi_{k+1}} \ge V^{\pi_k}$ 이고
  결정론 정책이 $m^n$ 개뿐이므로 **유한 반복에 정확히 종료**한다.
- **R3 (POMDP 의 신념 MDP 변환) [D2]** — 신념 $b$ 는 과거 전체 $(a_0,o_1,\dots,o_t)$ 의
  충분통계량이고, 신념 공간 $\Delta(\mathcal{S})$ 위에서 전이 $\tau(b,a,o)$ 와 보상
  $\rho(b,a) = \langle b, r(\cdot,a)\rangle$ 를 쓰면 POMDP 는 **상태가 연속인 MDP** 와 동등하다.
- **R4 (유한 지평 POMDP 가치함수는 PWLC) [D2]** — 지평 $h$ 의 최적 가치함수는 유한 집합
  $\Gamma_h \subset \mathbb{R}^n$ 에 대해
  $$V_h(b) = \max_{\alpha \in \Gamma_h} \langle \alpha, b \rangle \tag{6}$$
  꼴이다. 즉 조각마다 선형이고 볼록(piecewise-linear and convex)이며, $\Gamma_h$ 는 알파 벡터
  역행으로 $\Gamma_{h-1}$ 에서 생성된다.
- **R5 (계산 복잡도의 벽) [D1]** — 유한 지평 POMDP 의 최적 정책 결정은 PSPACE-완전이고
  (Papadimitriou & Tsitsiklis 1987), 무한 지평 POMDP 의 $\epsilon$-최적 정책 존재 판정은
  일반적으로 결정 불가능하다(Madani et al. 2003). R4 의 $\lvert \Gamma_h \rvert$ 가 지평마다
  $\lvert \mathcal{A} \rvert \lvert \Gamma_{h-1} \rvert^{\lvert \mathcal{O} \rvert}$ 로 커지는 것이 그 구체적 얼굴이다.

## 유도

### R1 — 수축성에서 최적성까지

**1단계: max 의 Lipschitz 성질.** 임의의 유계 함수 $f, g : \mathcal{A} \to \mathbb{R}$ 에 대해

$$
\big\lvert \max_a f(a) - \max_a g(a) \big\rvert \le \max_a \lvert f(a) - g(a) \rvert. \tag{7}
$$

증명: $a^\star \in \arg\max_a f(a)$ 를 잡으면
$\max_a f - \max_a g \le f(a^\star) - g(a^\star) \le \max_a \lvert f - g\rvert$.
$f$ 와 $g$ 의 역할을 바꾸면 반대 방향도 같은 상한을 받는다. (A1 이 $\max$ 의 존재를 준다.)

**2단계: (3).** 고정된 $s$ 에서 (2)의 대괄호를 $f(a), g(a)$ 로 보면

$$
\lvert (T^\* u)(s) - (T^\* v)(s) \rvert
  \overset{(7)}{\le} \max_a \gamma \Big\lvert \sum_{s'} P(s' \mid s,a)\,\big(u(s') - v(s')\big) \Big\rvert
  \le \max_a \gamma \sum_{s'} P(s' \mid s,a)\,\lVert u - v \rVert_\infty
  = \gamma \lVert u - v \rVert_\infty,
$$

마지막 등식은 $\sum_{s'} P(s' \mid s,a) = 1$ 때문이다. $s$ 에 대해 최대를 취하면 (3)이다.
$T^\pi$ 도 (7) 없이 같은 계산으로 $\gamma$-수축이다.

**3단계: 고정점의 존재·유일성.** $(\mathbb{R}^n, \lVert\cdot\rVert_\infty)$ 는 완비이고 A1 에서
$T^\*$ 는 유계 벡터를 유계 벡터로 보낸다. Banach 고정점 정리로 $T^\* v^\star = v^\star$ 인
$v^\star$ 가 유일하게 존재하고, 임의의 $V_0$ 에서 $(T^\*)^k V_0 \to v^\star$ 다.

**4단계: $v^\star = V^\*$ 이고 $\pi_{v^\star}$ 가 최적이다.** 두 방향을 따로 본다.

(i) 임의의 정책 $\pi$ 에 대해 $T^\pi v^\star \le T^\* v^\star = v^\star$ 다((2)의 $\max$ 가
모든 $a$ 를 지배하므로). $T^\pi$ 는 **단조**($u \le v \Rightarrow T^\pi u \le T^\pi v$, (1)에서
계수가 모두 음이 아니므로)이고 $\gamma$-수축이므로, 양변에 $T^\pi$ 를 $k$ 번 먹이면
$(T^\pi)^k v^\star \le v^\star$ 이고 $k \to \infty$ 에서 좌변은 $V^\pi$ 로 간다. 즉
$V^\pi \le v^\star$ — 모든 $\pi$ 에 대해.

(ii) $\pi^\star := \pi_{v^\star}$ 로 두면 정의상 $T^{\pi^\star} v^\star = T^\* v^\star = v^\star$,
즉 $v^\star$ 는 $T^{\pi^\star}$ 의 고정점이다. $T^{\pi^\star}$ 의 고정점은 유일하고 그것이
$V^{\pi^\star}$ 이므로 $V^{\pi^\star} = v^\star$.

(i)과 (ii)를 합치면 $v^\star = \max_\pi V^\pi = V^\*$ 이고 최대를 달성하는 정책이
**정상·결정론·Markov** 정책 $\pi^\star$ 다. 과거 전체를 보는 정책이나 비정상 정책을 허용해도
더 좋아지지 않는다는 뜻이고, 이 사실이 이후 모든 레슨에서 "정책을 $\pi(a \mid s)$ 로만
파라미터화해도 된다"는 근거다.

**가정이 깨지는 곳.** $\gamma = 1$ 이면 2단계의 마지막 등식이 $1 \cdot \lVert u-v \rVert_\infty$
가 되어 수축이 사라진다. 그러면 고정점이 유일하지 않다 — 보상이 모두 0 인 MDP 에서
$T^\* v = v$ 는 **모든 상수 벡터**가 만족한다(문제 P5). 또 A1 이 깨져 $r$ 이 유계가 아니면
$\lVert V_0 - V^\* \rVert_\infty = \infty$ 가 되어 (4)가 공허해지고, 3단계에서 $T^\*$ 가
유계 공간을 보존한다는 말 자체가 성립하지 않는다. 평균 보상(average-reward) 기준은 이
수축 논증을 버리고 span 반노름과 단일 사슬(unichain) 가정 위에서 다시 세운다.

### R2 — 수렴률과 정지 규칙

**(4)** 는 (3)에 $u = V_k$, $v = V^\*$ 를 넣고 $T^\* V^\* = V^\*$ 를 쓴 뒤 $k$ 에 대해 반복하면 나온다.

**(5)** 가 실제로 쓰는 양이다. 유도의 요점은 **그리디 정책을 어느 반복의 가치에서 뽑는가**다.
$\pi_k$ 를 $V_k$ 에 대한 그리디 정책이라 하면 정의상

$$
T^{\pi_k} V_k = T^\* V_k = V_{k+1}. \tag{8}
$$

$d_k := \lVert V_{k+1} - V_k \rVert_\infty$ 로 둔다. 두 부분으로 쪼갠다.

(a) $\pi_k$ 의 실제 가치와 $V_{k+1}$ 의 거리. $V^{\pi_k} = T^{\pi_k} V^{\pi_k}$ 와 (8)에서

$$
\lVert V^{\pi_k} - V_{k+1} \rVert_\infty = \lVert T^{\pi_k} V^{\pi_k} - T^{\pi_k} V_k \rVert_\infty
  \le \gamma \lVert V^{\pi_k} - V_k \rVert_\infty
  \le \gamma\big(\lVert V^{\pi_k} - V_{k+1} \rVert_\infty + d_k\big),
$$

즉 $\lVert V^{\pi_k} - V_{k+1} \rVert_\infty \le \gamma d_k / (1-\gamma)$.

(b) $V_{k+1}$ 과 $V^\*$ 의 거리. (3)으로 $\lVert V_{k+j+1} - V_{k+j} \rVert_\infty \le \gamma^j d_k$
이므로 망원 급수

$$
\lVert V_{k+1} - V^\* \rVert_\infty \le \sum_{j \ge 1} \lVert V_{k+j} - V_{k+j+1} \rVert_\infty
  \le d_k \sum_{j\ge1} \gamma^{j} = \frac{\gamma}{1-\gamma} d_k .
$$

(a)와 (b)를 삼각부등식으로 합치면 (5)다. 따라서 $d_k < \epsilon(1-\gamma)/(2\gamma)$ 에서
멈추는 것이 "$\epsilon$-최적 정책을 얻었다"의 **기계적 판정**이다.

> **흔한 오류**: $\pi_{k+1}$(= $V_{k+1}$ 에 대한 그리디)의 손실을 $d_k$ 로 재면 (8)이 깨져
> (a)의 첫 등식을 쓸 수 없고, 상한에 $\gamma$ 가 한 번 더 붙는다(문제 P1). 구현에서 이
> 한 칸 차이로 정지 규칙이 느슨해지거나 조용히 틀린다.

**정책 반복.** $\pi' = \pi_{V^\pi}$ (즉 $V^\pi$ 에 대한 그리디)로 두면
$T^{\pi'} V^\pi = T^\* V^\pi \ge T^\pi V^\pi = V^\pi$. $T^{\pi'}$ 의 단조성을 반복 적용하면
$(T^{\pi'})^k V^\pi \ge V^\pi$ 이고 $k\to\infty$ 에서 좌변이 $V^{\pi'}$ 로 수렴하므로

$$
V^{\pi'} \ge V^\pi \quad \text{(성분별)}. \tag{9}
$$

$V^{\pi'} = V^\pi$ 가 되는 순간 $V^\pi = T^\* V^\pi$ 이고 R1 의 유일성으로 $V^\pi = V^\*$ 다.
결정론 정책은 $m^n$ 개뿐이고 (9)가 성립하는 동안 값이 **엄격히** 개선되거나 종료되므로 반복은
유한하다. 실무에서 정책 반복의 반복 수가 $n$ 과 거의 무관하게 10 안쪽인 이유는 (9)가 단조일
뿐 아니라 각 단계가 Newton 법의 한 스텝과 같기 때문이다(생략: Puterman ch.6 의 Newton–Kantorovich
해석).

**가정이 깨지는 곳.** 상태·행동이 무한하면 "결정론 정책이 유한개"라는 종료 논증이 사라지고
정책 반복은 유한 종료를 잃는다(수렴은 남는다). 또 정책 평가를 근사로 하면 (9)가 성립하지
않을 수 있어 **정책이 나빠지는 반복**이 생긴다 — 이것이 근사 정책 반복의 진동이고,
`c8-value-based-rl` 의 발산 예와 같은 뿌리다.

### R3 — 신념 MDP 변환

POMDP 는 $(\mathcal{S},\mathcal{A},P,r,\mathcal{O},O,\gamma)$ 다. 행동 $a$ 를 하고 관측 $o$ 를
받았을 때 신념은 Bayes 로 갱신된다:

$$
b'(s') = \tau(b,a,o)(s') = \frac{O(o \mid s',a) \sum_s P(s' \mid s,a)\, b(s)}{\Pr(o \mid b,a)},
  \qquad \Pr(o \mid b,a) = \sum_{s'} O(o \mid s',a)\sum_s P(s'\mid s,a)\,b(s). \tag{10}
$$

**충분통계량임을 보이는 줄.** $h_t = (a_0,o_1,\dots,a_{t-1},o_t)$ 라 하자. (10)은 $b_t$ 가
$b_{t-1}, a_{t-1}, o_t$ 만으로 결정됨을 보여주므로 $b_t$ 는 $h_t$ 의 함수다. 반대로 미래의
분포는 $\Pr(s_{t+1}, o_{t+1} \mid h_t, a_t) = \sum_{s_t} \Pr(s_t \mid h_t) P(s_{t+1}\mid s_t,a_t)
O(o_{t+1}\mid s_{t+1},a_t)$ 이고 $\Pr(s_t \mid h_t) = b_t(s_t)$ 이므로 **$h_t$ 는 $b_t$ 를 넘어서는
정보를 주지 않는다**. 따라서 $(\Delta(\mathcal{S}), \mathcal{A}, \tau, \rho, \gamma)$ 는 Markov 이고
보상은 $\rho(b,a) = \sum_s b(s) r(s,a)$ 다. R1 이 이 MDP 에도 그대로 적용되어

$$
V^\*(b) = \max_a \Big[ \rho(b,a) + \gamma \sum_{o} \Pr(o \mid b,a)\, V^\*\big(\tau(b,a,o)\big) \Big]. \tag{11}
$$

**가정이 깨지는 곳.** 상태 공간이 유한해야 $b$ 가 유한 차원 단체(simplex) 위의 점이다. 연속
상태에서는 $b$ 가 **확률측도**이고 (10)은 측도 갱신이 되어, 입자 필터로 근사하면 관측 공간이
연속일 때 유효 입자 수가 붕괴한다(`c8-model-based-world-models` 와 Sunberg & Kochenderfer 2017).
또 $\Pr(o \mid b,a) = 0$ 인 관측에서 (10)은 정의되지 않는다 — 구현에서 0 나눗셈 분기가 필요하다.

### R4 — PWLC 와 알파 벡터

$h = 0$ 에서 $V_0(b) = 0 = \langle 0, b\rangle$ 이므로 $\Gamma_0 = \{0\}$ 이고 (6)이 성립한다.
$V_{h-1}(b) = \max_{\alpha \in \Gamma_{h-1}} \langle \alpha, b\rangle$ 를 가정하고 (11)의 한 스텝을
전개한다. $\Pr(o \mid b,a)\,\tau(b,a,o)(s')$ 가 (10)의 분모와 약분되는 것이 핵심이다:

$$
\Pr(o\mid b,a)\, \big\langle \alpha, \tau(b,a,o) \big\rangle
  = \sum_{s'} \alpha(s')\, O(o \mid s',a) \sum_s P(s'\mid s,a)\, b(s)
  = \big\langle g_{a,o,\alpha},\, b \big\rangle, \tag{12}
$$

여기서 $g_{a,o,\alpha}(s) := \sum_{s'} P(s'\mid s,a)\, O(o\mid s',a)\, \alpha(s')$ 다. 즉 **신념에
대한 비선형성이 사라지고 $b$ 에 선형인 항만 남는다.** 따라서

$$
V_h(b) = \max_a \Big[ \langle r_a, b\rangle + \gamma \sum_o \max_{\alpha \in \Gamma_{h-1}}
  \big\langle g_{a,o,\alpha}, b \big\rangle \Big], \tag{13}
$$

이고 $\max$ 와 합은 선형함수의 **상한과 합**이므로 결과는 다시 조각마다 선형인 볼록함수다.
생성 규칙을 쓰면

$$
\Gamma_h = \Big\{\, r_a + \gamma \sum_{o} g_{a,o,\alpha_o} \;:\; a \in \mathcal{A},\;
  (\alpha_o)_{o \in \mathcal{O}} \in \Gamma_{h-1}^{\mathcal{O}} \,\Big\}, \tag{14}
$$

즉 $\lvert \Gamma_h \rvert \le m \lvert \Gamma_{h-1}\rvert^{\lvert \mathcal{O}\rvert}$ 다. 이 이중
지수 폭발이 R5 의 복잡도이고, 지배되는 알파 벡터를 LP 로 쳐내는 가지치기(pruning)가 고전적
POMDP 해법의 실제 작업량이다(Smallwood & Sondik 1973, Kaelbling et al. 1998 §4).

**가정이 깨지는 곳.** (6)은 **유한 지평**에서만 유한 집합 $\Gamma_h$ 를 준다. 무한 지평에서
$V^\*$ 는 볼록이지만 유한개의 알파 벡터로 정확히 표현되지 않는다(일반적으로 가산 무한 또는
비표현). 그래서 무한 지평 POMDP 는 $\epsilon$-근사만 다루고, 그조차 R5 의 결정 불가능성에
걸린다. 또 보상이 신념에 비선형인 문제(예: 엔트로피 감소를 직접 보상하는 활성 지각)는 (12)의
약분이 깨져 PWLC 를 잃는다 — 이때는 $\rho$ 를 볼록 조각으로 다시 모델링해야 한다.

## 증명 스케치

### R1 — 수축 사상과 최적성 [D3]

**가설** H1: $\lvert r \rvert \le R_{\max} < \infty$. H2: $0 \le \gamma < 1$.
H3: $\mathcal{S}, \mathcal{A}$ 유한(또는 $\mathcal{A}$ 콤팩트하고 $r$ 연속).
**결론** C1: $T^\*$ 는 $\lVert\cdot\rVert_\infty$ 에서 $\gamma$-수축. C2: 고정점이 유일하게 존재.
C3: 그 고정점은 $V^\*$ 이고 그리디 정책이 최적.

**전략**: 수축 사상 + Banach 고정점 정리. 최적성은 **단조성**으로 두 방향 부등식을 만든다.

1. (7)을 보인다 — $\max$ 는 sup-노름에서 1-Lipschitz. 쓰는 것: H3(최대의 존재).
2. $P(\cdot\mid s,a)$ 가 확률분포라는 사실로 $\gamma$ 를 뽑아낸다 → C1. 쓰는 것: H2.
3. $\mathbb{R}^n$ 의 완비성과 H1 로 Banach 를 적용 → C2.
4. $T^\pi$ 의 단조성으로 $V^\pi \le v^\star$ (모든 $\pi$), 그리디 정책에 대해 등호 → C3.
   쓰는 것: (1)의 계수가 음이 아님.

**가설 하나를 지우면**: H2 를 $\gamma = 1$ 로 풀면 2단계에서 수축 계수가 1 이 되어 Banach 가
적용되지 않고, C2 가 **거짓**이 된다(상수만큼 평행이동한 가치가 모두 고정점). H1 을 지우면
$T^\*$ 가 유계 함수 공간을 보존하지 않아 3단계가 무의미해진다. H3 에서 $\mathcal{A}$ 의
콤팩트성을 지우면 $\max$ 가 달성되지 않아 그리디 정책이 존재하지 않을 수 있고, C3 는
$\epsilon$-그리디 형태로 약화된다.

생략: 연속 상태·비유계 보상으로의 확장은 가중 sup-노름($\lVert v \rVert_w = \sup_s \lvert v(s)\rvert/w(s)$)
위의 수축으로 다시 쓴다. Blackwell 1965 와 Puterman ch.6.10.

### R2 — 수렴률과 종료 [D3]

**가설** H1–H3 (위와 동일) + H4: 정책 평가를 **정확히** 한다($V^\pi = (I-\gamma P^\pi)^{-1} r^\pi$).
**결론** C1: (4). C2: (5)와 정지 규칙. C3: 정책 반복은 $m^n$ 반복 안에 정확히 종료.

**전략**: 수축의 반복 적용(C1) + 망원 급수와 삼각부등식(C2) + 단조 개선 + 유한 집합의
사다리 논증(C3).

1. (3)에 $V^\*$ 를 대입해 귀납 → C1.
2. 그리디 정책을 $V_k$ 에서 뽑아 $T^{\pi_k} V_k = V_{k+1}$ 을 확보한다. 이 한 줄이 (a)의
   첫 등식을 가능하게 한다. 쓰는 것: (8).
3. (a) $\lVert V^{\pi_k} - V_{k+1}\rVert \le \gamma d_k/(1-\gamma)$, (b) $\lVert V_{k+1} - V^\*\rVert
   \le \gamma d_k/(1-\gamma)$ → 합쳐 (5) → C2.
4. $T^{\pi'}$ 의 단조성으로 (9). 값이 같아지면 $T^\*$ 의 고정점 → 최적. 유한 정책 집합에서
   엄격 개선은 유한 번 → C3. 쓰는 것: H4.

**가설 하나를 지우면**: H4(정확한 정책 평가)를 지우면 (9)가 깨져 정책 반복이 단조가 아니고,
근사 정책 반복의 성능 한계는 $\lVert V^{\pi_k} - V^\*\rVert \le 2\gamma\epsilon_{\text{eval}}/(1-\gamma)^2$
꼴로 **$(1-\gamma)^{-2}$** 가 된다. 이 $(1-\gamma)^{-2}$ 는 C8 모듈에서 계속 다시 나온다
(모델 오차 전파, 오프라인 RL 의 분포 이동 한계).

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R2)** (5)를 $\pi_{k+1}$(= $V_{k+1}$ 에 대한 그리디)에 대해 다시 유도하라.
상한에 $\gamma$ 가 몇 번 붙는지, 그리고 그 차이가 $\gamma = 0.99$ 에서 정지 임계값을 몇 배
바꾸는지 수치로 쓰라.
*해답 스케치*: $T^{\pi_{k+1}} V_{k+1} = T^\* V_{k+1} = V_{k+2}$ 이므로 (a)의 역할을 하는 양이
$d_{k+1} \le \gamma d_k$ 로 바뀐다. 상한은 $2\gamma^2 d_k/(1-\gamma)$ 가 되어 임계값이 $\gamma$ 배
더 작아진다. $\gamma = 0.99$ 에서 임계값 비는 $0.99$ — 작아 보이지만 반복 수는 로그로 들어간다.

**P2 (증명, ★★★, R1·R2)** 정책 반복이 가치 반복을 지배함을 보여라: 같은 $V_0$ 에서 출발해
$V_0 \le V^{\pi_0}$ 이면 모든 $k$ 에 대해 $V_k^{\text{VI}} \le V^{\pi_k}$ 다.
*전략과 핵심 부등식*: $T^\* u \le T^{\pi_u} v$ 를 $u \le v$ 에서 끌어내고(그리디의 정의 +
단조성), 귀납으로 넘긴다. 핵심은 $T^\* V_k \le T^{\pi_k} V^{\pi_k} = V^{\pi_k}$. 전개는 숨긴다.

**P3 (계산, ★, R1·R2)** 2상태·2행동 MDP, $\gamma = 0.9$:
$s_0$ 에서 $a_0$ 은 $s_0$ 에 머물며 $r=1$, $a_1$ 은 확률 $0.8$ 로 $s_1$ 로 가고(나머지는 $s_0$)
$r=0$. $s_1$ 에서 $a_0$ 은 $s_0$ 로 가며 $r=0$, $a_1$ 은 $s_1$ 에 머물며 $r=2$.
$V^\*$ 와 최적 정책을 구하고, $V_0 = 0$ 에서 시작한 가치 반복이 $\epsilon = 10^{-3}$ 의 정지
규칙을 만족하기까지의 백업 횟수를 구하라.
*정답*: $V^\*(s_1) = 2/(1-0.9) = 20$, $V^\*(s_0) = 14.4/0.82 = 17.56097561\ldots$ (허용오차
$10^{-9}$), 최적 정책은 두 상태 모두 $a_1$. 정지 임계값은
$\epsilon(1-\gamma)/(2\gamma) = 5.5555\ldots\times10^{-5}$ 이고 백업 횟수는 **101**
(정의: $d_k$ 가 처음으로 임계값 아래로 내려가는 $k$).
검산: $V^\*$ 를 (2)에 넣어 양변이 $10^{-12}$ 이내로 일치하는지, 그리고
$\lVert V^{\pi^\*} - V^\* \rVert_\infty < 10^{-12}$ 인지 — $V^{\pi^\*}$ 는
$(I - \gamma P^{\pi^\*})^{-1} r^{\pi^\*}$ 로 직접 푼다.

**P4 (구현, ★★, R2)** 가치 반복과 정확 정책 반복을 각각 쓰고, 정지 규칙과 $\epsilon$-최적성
판정을 함수로 분리하라. 정책 평가는 선형 해로 한다.
*루브릭*: ⓐ 정지 규칙이 (5)의 상수를 그대로 쓰고 하드코딩된 반복 수가 아니다 ⓑ 두 방법의
$V^\*$ 가 $10^{-9}$ 이내로 일치한다 ⓒ 그리디 정책을 $V_k$ 에서 뽑는다(P1 의 함정) ⓓ 동점
처리 규칙이 문서화되어 있다 ⓔ $\gamma \to 1$ 에서 반복 수가 $O\big((1-\gamma)^{-1}\log(1/\epsilon)\big)$
로 늘어남을 도표로 보인다.

**P5 (반례, ★★, R1)** $\gamma = 1$ 에서 (3)이 깨지고 고정점이 유일하지 않은 MDP 를 만들라.
그리고 "보상이 모두 음수면 $\gamma=1$ 에서도 유일하다"는 주장이 왜 일반적으로 거짓인지
한 문단으로 쓰라.
*성질 체크리스트*: ⓐ 모든 상태가 흡수(absorbing)이고 $r \equiv 0$ 이면 모든 상수 벡터가
고정점이다 ⓑ 수축 계수가 정확히 1 임을 (7)의 등호 조건으로 확인 ⓒ 음수 보상에서도 흡수
상태의 가치가 $-\infty$ 로 갈 수 있어 유계성(A1 이 주는 것)이 깨지는 경로를 지적 ⓓ 해결책은
할인이 아니라 적절(proper) 정책 가정 또는 span 반노름이라는 점.

**P6 (논문, ★★, R3·R4)** Kaelbling et al. 1998 의 §3–4 와 Smallwood & Sondik 1973 을 읽고,
"알파 벡터 가지치기 없이 (14)를 그대로 돌리면 어느 규모에서 메모리가 터지는가"를
$n, m, \lvert\mathcal{O}\rvert, h$ 의 식으로 쓰라. 그리고 두 논문이 재현에 필요한 정보 중
빠뜨린 것 3개를 찾으라.
*채점 루브릭*: (14)의 이중 지수 $m \lvert\Gamma_{h-1}\rvert^{\lvert\mathcal{O}\rvert}$ 를 바르게
쓰고 구체적 수치 예(예: $m=3$, $\lvert\mathcal{O}\rvert=3$, $h=5$)를 들면 통과. 누락 정보는
가지치기 LP 의 허용오차·동점 처리·초기 신념 분포·난수 시드 중 3개를 들면 통과.
"계산량이 많다"만 쓰면 미달.

**P7 (계산, ★, R3)** 2상태 POMDP: 상태는 바뀌지 않고($P = I$), 관측은 $\Pr(o_0 \mid s_0) = 0.85$,
$\Pr(o_0 \mid s_1) = 0.15$ 다. $b(s_0) = 0.5$ 에서 $o_0$ 을 연속 2회, 3회 관측한 뒤의 $b(s_0)$ 를
분수와 소수로 구하라.
*정답*: 1회 $17/20 = 0.85$, 2회 $289/298 = 0.969798657718\ldots$, 3회
$4913/4940 = 0.994534412955\ldots$ (허용오차 $10^{-12}$).
검산: $\Pr(o_0 \mid b) = 0.85b + 0.15(1-b)$ 가 (10)의 분모와 일치하는지 확인하고,
$b$ 와 $1-b$ 의 로그 오즈가 관측마다 $\log(0.85/0.15)$ 만큼 선형으로 증가하는지 본다.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Blackwell, "Discounted dynamic programming" (1965, Ann. Math. Statist.)** — 역할:
   `원전(seminal)`. <https://doi.org/10.1214/aoms/1177700285>
   읽는 이유: R1 의 수축 논증과 "정상·결정론 최적 정책이 존재한다"는 주장의 원천이다.
   §2–3 만 읽는다.
   추가 질문: ⓐ 저자가 가정하는 보상 유계성과 측도 구조는 이 레슨의 A1·H3 와 어떻게 다른가?
   ⓑ Blackwell 최적성(모든 $\gamma$ 에 대해 동시에 최적)은 $\gamma$ 고정 최적성보다 무엇을 더 요구하는가?
2. **Smallwood & Sondik, "The optimal control of partially observable Markov processes over a
   finite horizon" (1973, Operations Research)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1287/opre.21.5.1071>
   읽는 이유: R4 의 PWLC 성질과 (14)의 알파 벡터 역행이 여기서 나왔다.
   추가 질문: ⓐ 저자의 가지치기 절차가 쳐내는 알파 벡터의 "지배(dominated)" 정의는 무엇인가?
   ⓑ 유한 지평을 무한 지평으로 미는 순간 어느 보조정리가 깨지는가?
3. **Kaelbling, Littman & Cassandra, "Planning and acting in partially observable stochastic
   domains" (1998, Artificial Intelligence)** — 역할: `표준(standard)`.
   <https://doi.org/10.1016/S0004-3702(98)00023-X> (§3–4 중심)
   읽는 이유: 신념 MDP 변환(R3)과 POMDP 계획의 표준 어휘·실험 설계를 고정한 글이다.
   추가 질문: ⓐ 저자들이 보고하는 witness 알고리즘의 계산량은 (14)의 상한 중 어느 부분을
   줄이는가? ⓑ 논문의 실험 규모를 2026 년 로봇 문제(관측이 이미지)로 옮기면 어디서 먼저 막히는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R1 (수치 검증).** 계산 예산: 노트북 CPU 1분 이내, 메모리 200 MB 이내, numpy 만.

(4)의 $\gamma^k$ 감소가 **이론 상한 안에서 거의 타이트하게** 성립하는지, 그리고 (5)의 정지
규칙이 실제로 $\epsilon$-최적 정책을 주는지 확인한다. 입력은 레슨이 제공하는 생성 스크립트다
(사용자 데이터 불필요):

```python
import numpy as np


def random_mdp(n_s=100, n_a=5, gamma=0.99, seed=0):
    """희소 보상 랜덤 MDP: 전이는 Dirichlet(0.1), 보상은 30% 상태-행동에만."""
    rng = np.random.default_rng(seed)
    p = rng.dirichlet(np.full(n_s, 0.1), size=(n_s, n_a))
    r = rng.uniform(0.0, 1.0, size=(n_s, n_a)) * (rng.random((n_s, n_a)) < 0.3)
    return p, r, gamma
```

**수용 기준** — 네 조건을 모두 만족해야 통과다. $V^\*$ 는 정확 정책 반복(정책 평가는
`np.linalg.solve`)으로 얻고, 가치 반복은 $V_0 = 0$ 에서 시작한다.

1. **누적 상한**: $e_k := \lVert V_k - V^\* \rVert_\infty$, $e_0 = \lVert V^\* \rVert_\infty$ 에 대해
   $\max_{1 \le k \le 2000,\ e_k > 10^{-6}} e_k / (\gamma^k e_0) \le 1$ 이고, 동시에 그 최댓값이
   $\ge 0.9$ 다(상한이 공허하지 않고 타이트함을 함께 요구한다).
2. **단계별 비**: $e_k > 10^{-6}$ 인 모든 $k$ 에 대해 $e_{k+1}/e_k \le \gamma + 10^{-8}$.
   ($10^{-8}$ 은 배정도 반올림 여유다 — $e_k$ 가 $10^{-6}$ 수준이면 백업 한 번의 반올림
   $\sim 10^{-13}$ 이 비에 $10^{-7}$ 규모로 보인다. 이 여유 없이 쓰면 조건 2 는 거짓이 된다.)
3. **정지 규칙**: $\epsilon \in \{10^{-3}, 10^{-6}\}$ 에 대해 $d_k < \epsilon(1-\gamma)/(2\gamma)$
   에서 멈췄을 때 $\lVert V^{\pi_k} - V^\* \rVert_\infty < \epsilon$. ($\pi_k$ 는 $V_k$ 에 대한
   그리디, $V^{\pi_k}$ 는 선형 해.)
4. **두 방법의 일치**: 정책 반복이 20 반복 안에 종료하고, 조건 3 의 $\epsilon = 10^{-6}$ 에서
   얻은 가치 반복 해와 $\lVert V^{\text{VI}} - V^\* \rVert_\infty < 10^{-6}$ 로 일치한다.

**비교 대상(베이스라인)**: ⓐ 정확 정책 반복 — 선형 해이므로 참값 역할을 한다.
ⓑ 같은 문제를 `scipy.optimize.linprog` 로 푼 LP 정식화
($\min \sum_s v(s)$ s.t. $v(s) \ge r(s,a) + \gamma \sum_{s'} P v$) — 선택이지만, 세 방법이
$10^{-6}$ 이내로 일치하면 구현 오류 가능성이 사실상 사라진다.

**참고 출력**(numpy 2.x, `seed=0`, $\gamma=0.99$): 정책 반복 5 반복에 종료,
$V^\* \in [57.21, 58.33]$, 조건 1 의 최댓값 $\approx 0.994$, $\epsilon=10^{-3}$ 정지까지 1160 백업,
$\epsilon=10^{-6}$ 까지 1848 백업, 두 경우 모두 정책 손실 $0$. **수용 기준은 생성기 버전과
무관하지만 이 참고 수치는 그렇지 않다** — `np.random.Generator` 의 `dirichlet` 스트림이 바뀌면
숫자가 달라지므로, 숫자가 아니라 네 조건으로 판정한다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 2 가 간신히 깨진다($e_{k+1}/e_k = \gamma + 10^{-7}$) | $V^\*$ 자체의 수치 오차가 작은 $e_k$ 를 오염 | $e_k$ 하한을 $10^{-6}$ 로 올리고, $V^\*$ 를 배정도 선형 해로 다시 계산해 잔차 $\lVert (I-\gamma P^{\pi^\*})V^\* - r^{\pi^\*}\rVert_\infty$ 를 본다 |
| 조건 3 이 실패한다 | 그리디 정책을 $V_{k+1}$ 에서 뽑았다(P1 의 함정) | 같은 코드로 $\pi_k$ 를 $V_k$ 에서 뽑아 다시 돌린다 — 손실이 $\gamma$ 배로 줄어든다 |
| 조건 1 의 최댓값이 $0.9$ 미만 | $V_0$ 가 0 이 아니거나 $e_0$ 를 $\lVert V_0 - V^\*\rVert$ 로 쓰지 않았다 | $e_0$ 를 출력해 $\lVert V^\*\rVert_\infty$ 와 비교한다 |
| 정책 반복이 종료하지 않는다 | 동점에서 정책이 진동 | $\arg\max$ 를 "값이 엄격히 개선될 때만 바꾸기"로 고정하거나 `np.argmax` 의 첫 인덱스 규칙을 유지한다 |
| 반복이 느리다($\gamma=0.999$) | 수렴 반복 수가 $(1-\gamma)^{-1}$ 로 커진다 | 정책 반복으로 갈아탄다 — 반복 수가 $\gamma$ 에 거의 둔감하다 |

## 열린 문제

- **(열린 문제) 연속 상태·관측 POMDP 의 보장** — R3 는 신념을 측도로 올리면 형식적으로
  성립하지만, 입자 필터로 근사하면 관측 공간이 연속일 때 가중치가 한 입자로 붕괴해
  유효 표본 수가 1 이 된다. 온라인 트리 탐색에 점진적 넓히기(progressive widening)를 붙여
  일관성을 되찾는 접근이 있으나(현재 접근:
  [Sunberg & Kochenderfer 2017](https://arxiv.org/abs/1709.06196)), 관측 밀도가 고차원 이미지일
  때의 수렴률은 알려지지 않았다. 비어 있는 자리: 고차원 관측에서 신념 근사 오차를 정책 손실로
  옮기는 상한.
- **(열린 문제) POMDP 복잡도 벽을 로봇 문제에서 우회하는 구조 조건** — 유한 지평은
  PSPACE-완전이고([Papadimitriou & Tsitsiklis 1987](https://doi.org/10.1287/moor.12.3.441))
  무한 지평 $\epsilon$-최적 판정은 결정 불가능하다
  ([Madani et al. 2003](https://doi.org/10.1016/S0004-3702(02)00378-8)). 로봇 문제에서 실제로
  성립하는 구조(관측이 대개 정보적이다, 상태가 저차원 다양체에 산다, 과제가 계층적이다)를
  **가정으로 적어** 다항 시간 보장을 받는 하위 클래스는 아직 정리되지 않았다. 비어 있는 자리:
  "로봇에서 흔한 POMDP"의 형식적 정의.
- **(열린 문제) 학습된 신념 표현이 충분통계량인가** — 잠재 공간 세계 모델은 $b$ 대신 학습된
  은닉 상태를 쓴다(현재 접근: [DreamerV3](https://arxiv.org/abs/2301.04104)). R3 의 충분통계량
  논증은 **정확한** 모형에서만 성립하므로, 학습된 은닉 상태가 충분하지 않으면 그 위의 DP 는
  Markov 가 아닌 문제에 Bellman 방정식을 적용하는 셈이다. 분포 밖 입력에서 이 결함을
  런타임에 탐지하는 방법도 미해결이다(현재 접근:
  [Sinha et al. 2022](https://arxiv.org/abs/2212.14020)). 비어 있는 자리: 충분성의 검증 가능한
  대리 지표.
- **(열린 문제) $\gamma$ 의 지위** — 할인율은 보통 모델링 편의로 고정되지만 (5)의 상한이
  $(1-\gamma)^{-1}$, 근사 정책 반복은 $(1-\gamma)^{-2}$ 로 커지므로 **보고되는 성능이 $\gamma$
  선택에 민감**하다. 평가에서 $\gamma$ 를 하이퍼파라미터로 튜닝하는 관행이 비교를 무의미하게
  만드는 정도는 정량화되지 않았다(평가 방법론의 현재 접근:
  [Agarwal et al. 2021](https://arxiv.org/abs/2108.13264)). 비어 있는 자리: 과제 지평과 $\gamma$ 를
  연결하는 원칙.

## 개념 점검

`rc quiz c8-mdp-pomdp-bellman` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c8-mdp-pomdp-bellman-quiz
questions:
  - id: q1
    type: single
    prompt: "$T^\\*$ 가 sup-노름에서 $\\gamma$-수축임을 보일 때 전이확률에 대해 실제로 쓰는 성질은?"
    choices:
      - "전이행렬이 대칭이다"
      - "각 행의 합이 1 이고 성분이 음이 아니다"
      - "전이행렬이 가역이다"
      - "정상분포가 유일하다"
    answer: 1
    explanation: "$\\sum_{s'} P(s' \\mid s,a) = 1$ 과 비음수성만 쓴다. 그래서 $\\max_a \\gamma \\sum_{s'} P \\lVert u-v \\rVert_\\infty = \\gamma \\lVert u-v \\rVert_\\infty$ 가 된다. 대칭성·가역성·에르고딕성은 필요하지 않다."
    concept: { front: "Bellman 수축이 쓰는 전이 성질", back: "행 합이 1 인 비음수 행렬(확률행렬)이라는 것뿐 — 에르고딕성·대칭성은 불필요" }
  - id: q2
    type: short
    prompt: "가치 반복에서 $\\epsilon$-최적 정책을 보장하는 정지 임계값을 $\\epsilon, \\gamma$ 로 쓰면? (분수 형태로)"
    answer: ["eps(1-gamma)/(2gamma)", "ε(1-γ)/(2γ)", "epsilon(1-gamma)/(2gamma)", "e(1-g)/(2g)", "\\epsilon(1-\\gamma)/(2\\gamma)"]
    explanation: "$\\lVert V_{k+1}-V_k \\rVert_\\infty < \\epsilon(1-\\gamma)/(2\\gamma)$ 이면 $V_k$ 에 대한 그리디 정책이 $\\epsilon$-최적이다. 유도는 (a) $\\lVert V^{\\pi_k}-V_{k+1}\\rVert \\le \\gamma d_k/(1-\\gamma)$ 와 (b) $\\lVert V_{k+1}-V^\\*\\rVert \\le \\gamma d_k/(1-\\gamma)$ 의 합이다."
    concept: { front: "가치 반복의 정지 규칙", back: "$d_k < \\epsilon(1-\\gamma)/(2\\gamma)$ — 그리디는 $V_k$ 에서 뽑는다" }
  - id: q3
    type: truefalse
    prompt: "무한 지평 POMDP 의 최적 가치함수도 유한개의 알파 벡터로 정확히 표현된다."
    answer: false
    explanation: "PWLC 성질(6)이 유한 집합 $\\Gamma_h$ 를 주는 것은 유한 지평에서다. 무한 지평에서는 볼록성은 남지만 유한개의 선형 조각으로 정확히 표현되지 않고 $\\epsilon$-근사만 다룬다. 게다가 $\\epsilon$-최적 판정 자체가 일반적으로 결정 불가능하다."
    concept: { front: "PWLC 가 성립하는 범위", back: "유한 지평뿐 — 무한 지평은 볼록하지만 유한 알파 벡터로 정확 표현 불가" }
  - id: q4
    type: single
    prompt: "(14)의 알파 벡터 집합 크기 상한은?"
    choices:
      - "$\\lvert \\mathcal{A} \\rvert \\cdot \\lvert \\Gamma_{h-1} \\rvert$"
      - "$\\lvert \\mathcal{A} \\rvert \\cdot \\lvert \\Gamma_{h-1} \\rvert^{\\lvert \\mathcal{O} \\rvert}$"
      - "$\\lvert \\mathcal{O} \\rvert \\cdot \\lvert \\Gamma_{h-1} \\rvert^{\\lvert \\mathcal{A} \\rvert}$"
      - "$\\lvert \\mathcal{S} \\rvert \\cdot \\lvert \\mathcal{A} \\rvert \\cdot \\lvert \\mathcal{O} \\rvert$"
    answer: 1
    explanation: "각 행동마다, 관측별로 독립적으로 $\\Gamma_{h-1}$ 에서 하나를 고르므로 $\\lvert \\mathcal{A} \\rvert \\lvert \\Gamma_{h-1} \\rvert^{\\lvert \\mathcal{O} \\rvert}$ 다. 이 이중 지수가 가지치기를 필수로 만든다."
    concept: { front: "알파 벡터 역행의 폭발 차수", back: "$\\lvert \\mathcal{A} \\rvert \\lvert \\Gamma_{h-1} \\rvert^{\\lvert \\mathcal{O} \\rvert}$ — 지평마다 이중 지수" }
  - id: q5
    type: truefalse
    prompt: "근사 정책 평가를 쓰면 정책 반복의 단조 개선(9)이 보장되지 않는다."
    answer: true
    explanation: "(9)는 $V^\\pi$ 를 정확히 알 때 $T^{\\pi'}V^\\pi \\ge V^\\pi$ 에서 나온다. 평가에 오차 $\\epsilon_{\\text{eval}}$ 이 있으면 부등식이 깨져 정책이 나빠지는 반복이 생기고, 성능 한계가 $(1-\\gamma)^{-2}$ 꼴로 악화된다."
    concept: { front: "근사 정책 반복이 단조가 아닌 이유", back: "(9)가 정확한 $V^\\pi$ 를 쓰므로 — 평가 오차는 $2\\gamma\\epsilon/(1-\\gamma)^2$ 로 증폭" }
```

## 이 단계 공부법

1. **연산자 표기를 먼저 고정한다 (30분)** — (1)·(2)를 종이에 옮겨 쓰고 $T^\pi$, $T^\*$ 의
   단조성과 수축성을 각각 한 줄로 확인한다. C8 의 남은 7개 레슨이 전부 이 두 연산자 위에서
   돌아간다.
2. **(7)에서 (3)까지를 백지에서 다시 쓴다 (90분)** — 본문을 덮고 재구성한다. $\max$ 의
   1-Lipschitz 성질을 빼먹으면 막히는 지점이 어디인지 직접 확인한다. S&B ch.3–4 와 LaValle
   ch.10 을 **같은 결과의 다른 표기**로 대조해 읽는다.
3. **정지 규칙을 손으로 유도한다 (60분)** — (5)의 (a)·(b)를 각각 유도하고, P1 을 풀어
   "그리디를 $V_k$ 에서 뽑는다"는 한 줄이 왜 중요한지 몸으로 익힌다. 이 함정은 실제 구현에서
   가장 흔한 조용한 버그다.
4. **구현으로 상한의 타이트함을 본다 (75분)** — 재현 과제를 먼저 $\gamma = 0.9$ 로 돌려
   조건 1 의 비율이 $1$ 에 얼마나 붙는지 보고, 그 다음 $\gamma = 0.999$ 로 올려 반복 수가
   어떻게 늘어나는지 본다. 이론의 $(1-\gamma)^{-1}$ 을 숫자로 만나는 것이 목적이다.
5. **논문 3편을 시간순으로 읽는다 (150분)** — Blackwell(수축) → Smallwood & Sondik(PWLC) →
   Kaelbling et al.(신념 MDP 와 실험). 논문당 1페이지 노트는 **반드시** 쓴다. 특히 질문 4
   ("무엇은 보장하지 않는가")가 이 레슨의 열린 문제와 직접 이어진다.
6. **무엇을 못 하는지로 끝낸다 (75분)** — "열린 문제" 4개 중 하나를 골라 왜 아직 안 풀렸는지
   한 문단으로 쓰고, P7 의 로그 오즈 관찰을 고차원 관측으로 확장하면 무엇이 깨지는지 적는다.

**통과 기준**: 백지에서 (3)과 (5)를 유도할 수 있고, $\gamma=1$ 에서 무엇이 먼저 깨지는지
말할 수 있고, (14)의 폭발 차수를 쓸 수 있고, 재현 과제의 네 조건을 만족하는 코드와 논문
3편의 노트를 갖고 있다.
