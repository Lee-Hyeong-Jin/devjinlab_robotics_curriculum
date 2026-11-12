---
id: c8-model-based-world-models
title: 모델 기반 RL 과 세계 모델
summary: >-
  모델 오차가 가치 오차로 어떻게 번지는지를 시뮬레이션 보조정리로 정확한 등식과 상한 양쪽에서
  유도하고, 그 상한이 왜 $(1-\gamma)^{-2}$ 를 갖는지 본다. 이어서 Dyna 류가 모델의 최적해로
  수렴하는 편향을 보이고, 분기 롤아웃 길이 $k$ 의 성능-편향 교환을 수치로 재현한다. 마지막으로
  잠재 공간 세계 모델의 학습 목표(ELBO)를 유도하고 그 목표가 가치 정확도와 어긋나는 예를 만든다.
objectives:
  - 모델 오차와 가치 오차를 잇는 정확한 등식을 유도하고 그것에서 시뮬레이션 보조정리를 얻을 수 있다.
  - 상한의 $(1-\gamma)^{-2}$ 가 어느 단계에서 생기는지 지적하고 상한이 얼마나 느슨한지 수치로 보일 수 있다.
  - Dyna 류 업데이트의 고정점이 모델의 최적 가치임을 보이고 그 편향을 정량화할 수 있다.
  - 분기 롤아웃 길이 $k$ 의 최적값이 비평자 잡음과 모델 품질에 어떻게 의존하는지 실험으로 분리할 수 있다.
  - 순차 잠재 변수 모델의 ELBO 를 유도하고 각 항이 무엇을 벌점으로 세는지 설명할 수 있다.
  - 로그 가능도가 더 높은 모델이 가치 오차는 더 나쁠 수 있음을 구성적으로 보일 수 있다.
prerequisites: [c8-mdp-pomdp-bellman, c8-value-based-rl]
difficulty: 5
estimated_minutes: 540
tags: [model-based-rl, world-models, simulation-lemma, dyna, elbo, research]
activities:
  - id: c8-model-based-world-models-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c8-model-based-world-models-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c8-model-based-world-models-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 165
  - id: c8-model-based-world-models-reproduction
    kind: reproduction
    title: 재현 과제 — 롤아웃 길이의 성능-편향 곡선과 목표 불일치 (R2)
    estimated_minutes: 120
  - id: c8-model-based-world-models-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
papers:
  - id: kearns2002-near-optimal
    required: true
    role: seminal
    note: "§3"
  - id: janner2019-mbpo
    required: true
    role: standard
    note: "§4-5"
  - id: hafner2023-dreamerv3
    required: true
    role: frontier
    note: "§2-3"
resources:
  - title: "Sutton & Barto, Reinforcement Learning: An Introduction (2nd ed.)"
    kind: book
    note: ch.8 (계획과 학습의 통합, Dyna). 1순위 교재. (공식 URL 미확인)
  - title: "Hafner et al. — Learning latent dynamics for planning from pixels (2018)"
    url: https://arxiv.org/abs/1811.04551
    kind: paper
    note: 권장. PlaNet — RSSM 과 잠재 공간 계획의 ELBO 유도가 가장 명시적이다.
  - title: "Chua, Calandra, McAllister & Levine — Deep RL in a handful of trials using probabilistic dynamics models (2018)"
    url: https://arxiv.org/abs/1805.12114
    kind: paper
    note: 권장. PETS — 앙상블로 불확실성을 다루고 롤아웃 길이를 제한한다.
---

# 모델 기반 RL 과 세계 모델

## 전제와 기호

`c8-mdp-pomdp-bellman` 의 연산자 표기와 `c8-value-based-rl` 의 가중 노름을 쓴다. 추가
**권장 선수**:

- 선형대수: $(I - \gamma P)^{-1}$ 의 Neumann 급수와 $\lVert(I-\gamma P)^{-1}\rVert_\infty
  \le 1/(1-\gamma)$.
- 확률: 전변동 거리와 $\ell_1$ 거리의 관계, 다항분포의 집중(concentration), Jensen 부등식.
- 변분 추론: ELBO, KL 발산, 재매개화 기법(`r0-estimation-theory`).

표기 추가:

| 기호 | 뜻 |
|---|---|
| $\hat{P}, \hat{r}$ | 학습된 모델. 참 모형은 $P, r$ |
| $\epsilon_P$ | 모델의 전이 오차. $\epsilon_P = \max_{s,a} \lVert \hat{P}(\cdot\mid s,a) - P(\cdot\mid s,a)\rVert_1$ |
| $\epsilon_r$ | 보상 오차. $\epsilon_r = \max_{s,a}\lvert \hat{r}(s,a) - r(s,a)\rvert$ |
| $\hat{V}^\pi, \hat{Q}^\pi$ | 모델 MDP 에서의 가치. 참 MDP 의 가치는 $V^\pi, Q^\pi$ |
| $k$ | 분기 롤아웃 길이(모델을 몇 스텝 굴리고 비평자로 부트스트랩하는가) |
| $V_\varphi$ | 비평자(critic). 이 레슨에서는 $V^\* + \mathcal{N}(0,\sigma_V^2)$ 로 모사한다 |
| $z_t$ | 잠재 상태. $o_t$ 는 관측, $q(z_t\mid\cdot)$ 는 추론 분포, $p(z_t \mid z_{t-1},a_{t-1})$ 는 사전 분포 |
| $R_{\max}$ | $\max_{s,a}\lvert r(s,a)\rvert$. 따라서 $\lVert V^\pi\rVert_\infty \le R_{\max}/(1-\gamma)$ |

이 레슨의 모든 상한은 **$(I-\gamma P)^{-1}$ 의 노름이 $1/(1-\gamma)$ 로 묶인다**는 한 가지
사실에서 나온다. 시작하기 전에 그것을 Neumann 급수로 한 줄에 쓸 수 있는지 확인하라
(`c8-mdp-pomdp-bellman` 의 자가 진단 D1).

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (모델 오차 → 가치 오차: 정확한 등식과 시뮬레이션 보조정리) [D3]** — 임의의 정책 $\pi$ 에
  대해 **정확한 등식**
  $$
  \hat{V}^\pi - V^\pi = \big(I - \gamma \hat{P}^\pi\big)^{-1}
    \Big[\big(\hat{r}^\pi - r^\pi\big) + \gamma\big(\hat{P}^\pi - P^\pi\big) V^\pi\Big] \tag{1}
  $$
  이 성립하고, 여기서 노름을 취하면
  $$
  \big\lVert \hat{V}^\pi - V^\pi \big\rVert_\infty \;\le\;
    \frac{\epsilon_r}{1-\gamma} \;+\; \frac{\gamma\,\epsilon_P\,R_{\max}}{(1-\gamma)^2} . \tag{2}
  $$
  $(1-\gamma)^{-2}$ 는 **$(I-\gamma\hat{P}^\pi)^{-1}$ 의 $1/(1-\gamma)$ 와 $\lVert V^\pi\rVert_\infty$
  의 $1/(1-\gamma)$ 가 곱해진 것**이다. (2)는 참이지만 매우 느슨하다 — 재현 과제에서 실제 오차가
  상한의 $10^{-3}$ 수준임을 측정한다.
- **R2 (Dyna 류의 편향) [D2]** — 모델 표본만으로 업데이트하는 Dyna 는 모델 Bellman 연산자
  $\hat{T}^\*$ 의 고정점으로 수렴하므로 그 해는 $\hat{Q}^\*$ 이고,
  $$
  \big\lVert \hat{Q}^\* - Q^\* \big\rVert_\infty \;\le\;
    \frac{\epsilon_r}{1-\gamma} \;+\; \frac{\gamma\,\epsilon_P\,R_{\max}}{(1-\gamma)^2} \tag{3}
  $$
  의 편향을 갖는다 — (2)와 **같은 차수**이고, **실데이터를 더 모아도 모델을 고치지 않으면
  사라지지 않는 편향**이다.
  게다가 $\epsilon_P$ 는 데이터가 모인 분포에서만 작으므로, 정책이 개선되며 분포가 이동하면
  편향이 다시 커진다.
- **R3 (분기 롤아웃의 성능-편향 교환) [D2]** — 모델을 $k$ 스텝 굴리고 비평자 $V_\varphi$ 로
  부트스트랩하면 가치 추정 오차는 대략
  $$
  \mathrm{err}(k) \;\lesssim\; \underbrace{\gamma^k \,\sigma_V}_{\text{비평자 오차의 감쇠}}
    \;+\; \underbrace{\frac{k}{1-\gamma}\,c\,\epsilon_P}_{\text{모델 오차의 누적}} \tag{4}
  $$
  이고(모델 오차는 롤아웃 길이에 **선형**으로 누적된다 — $k$ 스텝 뒤 분포의 전변동이
  $k\epsilon_P$ 규모다), 두 항의 합이 내부 최솟값 $k^\star$ 를 갖는다. $k^\star$ 는 **비평자
  잡음 $\sigma_V$ 에 대해 단조 증가**한다(재현 과제에서 5개 모델 품질 × 4개 잡음 수준 ×
  20시드로 확인). (4)는 MBPO §4 의 한계를 단순화한 **경험적 분해**이고 정리가 아니다 —
  $\epsilon_P$ 방향의 예측은 실제로 **깨진다**(문제 P5).
- **R4 (잠재 세계 모델의 학습 목표) [D2]** — 순차 잠재 변수 모델의 로그 가능도는
  $$
  \log p(o_{1:T}\mid a_{1:T}) \;\ge\; \sum_{t=1}^{T}
    \mathbb{E}_{q}\big[\log p(o_t \mid z_t)\big]
    - \mathbb{E}_{q}\Big[D_{\mathrm{KL}}\big(q(z_t \mid o_{\le t}, a_{<t}) \,\big\Vert\,
      p(z_t \mid z_{t-1}, a_{t-1})\big)\Big] \tag{5}
  $$
  로 하한되고, 이것이 PlaNet·Dreamer 계열의 학습 목표다. 첫 항은 **관측 재구성**, 둘째 항은
  **예측 가능성**을 요구한다.
- **R5 (목표 불일치: 가능도와 가치는 다른 순서를 준다) [D2]** — (5)를 최대화하는 것은
  (2)의 $\epsilon_P$ 를 줄이는 것과 다르다. 구성적으로, 보류 데이터의 로그 가능도가 **더 높은**
  모델이 가치 오차는 **2배 이상 나쁠 수 있다**(재현 과제 조건 4). 원인은 가능도가 모든 방향의
  오차를 동등하게 세는 반면 가치는 $V^\pi$ 방향 성분만 보기 때문이다 — (1)의 괄호 안이
  $(\hat{P}-P)V^\pi$ 라는 **내적**이다.

## 유도

### R1 — 정확한 등식에서 상한까지

$\hat{V}^\pi$ 와 $V^\pi$ 는 각자의 Bellman 방정식을 만족한다:

$$
\hat{V}^\pi = \hat{r}^\pi + \gamma \hat{P}^\pi \hat{V}^\pi, \qquad
  V^\pi = r^\pi + \gamma P^\pi V^\pi .
$$

차를 빼고 $\gamma\hat{P}^\pi V^\pi$ 를 **더하고 빼는** 것이 유일한 기교다:

$$
\hat{V}^\pi - V^\pi
  = (\hat{r}^\pi - r^\pi) + \gamma \hat{P}^\pi \hat{V}^\pi - \gamma P^\pi V^\pi
  = (\hat{r}^\pi - r^\pi) + \gamma \hat{P}^\pi (\hat{V}^\pi - V^\pi)
    + \gamma(\hat{P}^\pi - P^\pi) V^\pi .
$$

$\gamma\hat{P}^\pi(\hat{V}^\pi - V^\pi)$ 를 좌변으로 옮기면
$(I - \gamma\hat{P}^\pi)(\hat{V}^\pi - V^\pi) = (\hat{r}^\pi - r^\pi) + \gamma(\hat{P}^\pi - P^\pi)V^\pi$
이고, $\hat{P}^\pi$ 가 확률행렬이므로 $(I - \gamma\hat{P}^\pi)$ 는 가역이다. 이것이 (1)이다.

**상한 (2).** 세 조각을 각각 묶는다.

1. $\big\lVert (I-\gamma\hat{P}^\pi)^{-1}\big\rVert_\infty
   = \big\lVert \sum_{t\ge0}\gamma^t(\hat{P}^\pi)^t\big\rVert_\infty \le \sum_{t\ge0}\gamma^t
   = \frac{1}{1-\gamma}$ (확률행렬의 $\infty$-노름이 1 이므로).
2. $\lVert \hat{r}^\pi - r^\pi\rVert_\infty \le \epsilon_r$ (정의).
3. $\big\lvert \big[(\hat{P}^\pi - P^\pi)V^\pi\big](s)\big\rvert
   \le \lVert \hat{P}^\pi(\cdot\mid s) - P^\pi(\cdot\mid s)\rVert_1 \lVert V^\pi\rVert_\infty
   \le \epsilon_P \cdot \frac{R_{\max}}{1-\gamma}$ (Hölder).

세 조각을 (1)에 넣으면 (2)다. **$(1-\gamma)^{-2}$ 가 생기는 자리는 1단계의 $1/(1-\gamma)$ 와
3단계의 $1/(1-\gamma)$ 가 곱해지는 곳 하나뿐이다.**

**가정이 깨지는 곳.** 3단계의 Hölder 가 $\lVert V^\pi\rVert_\infty$ 를 쓰는 것이 느슨함의
주범이다. 실제로는 $(\hat{P}-P)V^\pi$ 가 **내적**이므로 모델 오차가 $V^\pi$ 에 직교하면 기여가
0 이다. 더 타이트한 형태는 $\lVert V^\pi\rVert_\infty$ 를 **span** $\tfrac12(\max V - \min V)$ 로
바꾸고 $\epsilon_P$ 를 전변동으로 재는 것인데, 그래도 최악 상태 기준이라 여전히 느슨하다.
재현 과제에서 실제/상한 비가 $6\times10^{-4}$–$5\times10^{-3}$ 로 측정된다 — **상한은 올바르지만
설계 지침으로 쓸 수 없다.**

### R2 — Dyna 의 편향

Dyna 는 실데이터로 모델을 맞추고 **모델에서 뽑은 가상 전이**로 가치 업데이트를 한다. 가상
전이만 쓰는 극한에서 업데이트는 모델 Bellman 최적 연산자
$(\hat{T}^\*v)(s) = \max_a[\hat{r}(s,a) + \gamma\sum_{s'}\hat{P}(s'\mid s,a)v(s')]$ 의 반복이다.
`c8-mdp-pomdp-bellman` 의 R1 이 모델 MDP 에도 적용되므로 수렴점은 $\hat{V}^\*$ 이고, 따라서
Dyna 의 해는 **모델의 최적해**다. 두 최적 가치의 차는 $\max$ 의 1-Lipschitz 성질 (7)로

$$
\lVert \hat{V}^\* - V^\*\rVert_\infty
  \le \frac{1}{1-\gamma}\Big(\epsilon_r + \gamma\,\epsilon_P \frac{R_{\max}}{1-\gamma}\Big), \tag{6}
$$

즉 (2)와 같은 차수다. 핵심은 **이 오차가 실데이터 양과 무관하게 모델 오차에만 의존한다**는
점이다. 실데이터를 섞어 쓰면(real ratio $\beta$) 편향이 $\beta$ 에 비례해 줄지만, 그만큼
모델의 표본 효율 이득도 줄어든다 — 이 교환이 MBPO 의 설계 변수다.

**분포 이동이 더 나쁜 이유.** $\epsilon_P$ 는 모델을 학습한 데이터 분포 $\mu$ 에서만 작다.
정책이 개선되면 방문 분포가 $d^{\pi_{\text{new}}}$ 로 옮겨가고, $\mu$ 가 덮지 않는 곳에서
$\hat{P}$ 는 임의로 틀릴 수 있다. 그런데 정책 최적화는 **모델이 좋다고 말하는 곳**을 찾아가므로
오차가 큰 영역을 **적극적으로 착취**한다(model exploitation). 이것이 모델 기반 RL 의 고전적
실패 양상이고, `c8-offline-rl` 의 외삽 오차와 같은 구조다.

**가정이 깨지는 곳.** (6)은 $\epsilon_P$ 를 **모든** $(s,a)$ 에서의 최댓값으로 재므로, 데이터가
없는 한 점에서만 모델이 틀려도 상한이 커진다. 반대로 최악이 아니라 $d^\pi$-가중 평균으로
재면 상한은 작아지지만 model exploitation 때문에 **그 평균이 보장하는 것이 없다** — 정책이
평균을 깨는 쪽으로 움직인다.

### R3 — 롤아웃 길이 $k$

$k$ 스텝 모델 롤아웃 + 비평자 부트스트랩의 추정량은

$$
Q_k(s,a) = \mathbb{E}_{\hat{P}}\Big[\sum_{t=0}^{k-1}\gamma^t \hat{r}_t
  + \gamma^k V_\varphi(s_k) \,\Big|\, s_0=s, a_0=a\Big].
$$

두 오차원을 분리한다. 비평자 오차 $V_\varphi - V^\*$ 는 $\gamma^k$ 로 **감쇠**하고, 모델 오차는
$t = 0,\dots,k-1$ 에 걸쳐 **누적**되어 $\sum_{t<k}\gamma^t \cdot O(\epsilon_P) =
\frac{1-\gamma^k}{1-\gamma}O(\epsilon_P)$ 가 된다. 합치면 (4)다. $k=0$ 은 순수 비평자(모델을
전혀 믿지 않음), $k\to\infty$ 는 순수 모델(비평자를 전혀 믿지 않음)이고 최적은 보통 그 사이다.

**누적이 선형인 이유.** 모델을 한 스텝 굴릴 때마다 상태 분포의 전변동 오차가 $\epsilon_P$
만큼 더해지므로 $k$ 스텝 뒤에는 $k\epsilon_P$ 규모다. 그 분포 오차가 가치에 들어올 때
$R_{\max}/(1-\gamma)$ 가 곱해져 (4)의 둘째 항이 된다. **$k$ 에 선형**이라는 점이 중요하다 —
$(1-\gamma^k)/(1-\gamma)$ 처럼 포화하는 형태로 쓰면 두 항이 같은 $\gamma^k$ 인자를 가져
$\mathrm{err}(k)$ 가 단조가 되고 내부 최솟값이 사라진다.

(4)를 $k$ 에 대해 미분하면($\gamma^k$ 를 연속으로 보아)
$-\ln(1/\gamma)\,\gamma^k \sigma_V + c\epsilon_P/(1-\gamma) = 0$ 이므로

$$
k^\star \;\approx\; \frac{1}{\ln(1/\gamma)}\,
  \ln\!\frac{\sigma_V\,(1-\gamma)\,\ln(1/\gamma)}{c\,\epsilon_P}
  \quad (\text{양수인 구간에서}). \tag{7}
$$

즉 $k^\star$ 는 $\sigma_V$ 에 **대수적으로 증가**하고 $\epsilon_P$ 에 **대수적으로 감소**한다.
재현 과제에서 $\sigma_V$ 의 단조 증가는 5개 모델 품질 전부에서 확인되고, $\epsilon_P$ 쪽은
**확인되지 않는다** — 표 형식 모델에서 표본 수를 바꿔도 $k^\star$ 가 단조로 변하지 않는다
(문제 P5 에서 왜 그런지 묻는다). (7)은 (4)라는 **근사 모형**의 성질이지 정리가 아니며,
예측이 한쪽에서 깨지는 것을 보는 것이 이 레슨의 실험 목적이다.

### R4 — 잠재 세계 모델의 ELBO

관측열 $o_{1:T}$, 행동열 $a_{1:T}$, 잠재열 $z_{1:T}$ 에 대해 생성 모형을
$p(o_{1:T}, z_{1:T}\mid a_{1:T}) = \prod_t p(z_t\mid z_{t-1},a_{t-1})\,p(o_t\mid z_t)$ 로 두고
추론 분포를 $q(z_{1:T}\mid o_{1:T},a_{1:T}) = \prod_t q(z_t\mid o_{\le t}, a_{<t})$ (필터링
형태)로 둔다. 로그 가능도에 $q$ 를 끼워 Jensen 을 쓴다:

$$
\log p(o_{1:T}\mid a_{1:T})
  = \log \mathbb{E}_{q}\!\left[\frac{p(o_{1:T},z_{1:T}\mid a_{1:T})}{q(z_{1:T}\mid o_{1:T},a_{1:T})}\right]
  \;\ge\; \mathbb{E}_{q}\!\left[\log \frac{p(o_{1:T},z_{1:T}\mid a_{1:T})}{q(z_{1:T}\mid \cdot)}\right].
$$

분자·분모를 시점별로 쪼개면

$$
\mathbb{E}_q\Big[\sum_t \log p(o_t\mid z_t) + \log p(z_t\mid z_{t-1},a_{t-1}) - \log q(z_t\mid o_{\le t},a_{<t})\Big],
$$

이고 뒤 두 항을 시점별 KL 로 묶으면 (5)다. **각 항의 뜻**: 첫 항은 잠재 상태로부터 관측을
복원할 수 있어야 한다는 요구(정보 보존), 둘째 항은 추론 분포가 **예측 가능**해야 한다는 요구
(사전 분포와 가까울 것)다. 보상을 함께 모델링하면 $\log p(r_t\mid z_t)$ 항이 첫 항에 더해진다 —
Dreamer 계열이 그렇게 한다.

**가정이 깨지는 곳.** (5)는 **관측 재구성**을 요구하므로, 과제와 무관한 고차원 배경(나뭇잎의
흔들림, 조명 변화)이 용량을 가져간다. 반대로 재구성 항을 빼고 보상·가치 예측만 쓰면 ELBO 가
아니어서 하한 보장이 없다. 더 근본적으로, (5)를 최대화하는 것은 (2)의 $\epsilon_P$ 를 줄이는
것과 **다른 문제**다 — 다음 결과가 그것이다.

### R5 — 목표 불일치

(1)의 괄호 안을 다시 본다. 모델 오차가 가치에 들어오는 경로는
$\gamma(\hat{P}^\pi - P^\pi)V^\pi$ 이고, 이것은 오차 벡터와 $V^\pi$ 의 **내적**이다. 따라서
$\hat{P} - P$ 가 $V^\pi$ 에 직교하면 모델이 아무리 틀려도 가치는 정확하다. 반대로 작은 오차가
$V^\pi$ 방향으로 정렬되면 가치 오차가 크다.

로그 가능도는 이 방향 구조를 **전혀 모른다**. $\hat{P}$ 를 $V^\pi$ 의 중심화 방향
$c = (V^\pi - \bar{V}^\pi)/\lVert\cdot\rVert$ 로 밀면 가능도는 올라가면서 가치 오차는 커질 수
있다. 재현 과제에서 다음을 측정한다(seed 0, $n=200$):

| 모델 | 보류 데이터 로그 가능도 변화 | 가치 오차 |
|---|---|---|
| 기준 $\hat{P}$ | — | $0.0472$ |
| $\hat{P} + 0.02\,u$ ($u \perp c$) | $+8{,}931$ | $0.0370$ |
| $\hat{P} + 0.004\,c$ | $+24{,}060$ | $0.0957$ |

가능도가 **더 많이** 올라간 모델이 가치 오차는 **2.6배 나쁘다**. 이것이 "목표 불일치
(objective mismatch)"의 가장 단순한 형태다.

**가정이 깨지는 곳.** 이 논증은 $V^\pi$ 를 **알고 있다고** 전제한다. 실제로는 $V^\pi$ 를
모르므로 "가치와 정렬된 방향"을 미리 알 수 없고, 그래서 가능도를 쓰는 관행이 생겼다. 가치
인식 모델 학습(value-aware model learning)이 열린 문제인 이유가 여기다.

## 증명 스케치

### R1 — 시뮬레이션 보조정리 [D3]

**가설** H1: $\lvert r\rvert, \lvert\hat{r}\rvert \le R_{\max} < \infty$. H2: $\gamma<1$.
H3: $\hat{P}(\cdot\mid s,a)$ 가 확률분포. H4: $\epsilon_P, \epsilon_r$ 가 유한.
**결론** C1: 등식 (1). C2: 상한 (2).

**전략**: 두 Bellman 방정식의 차에 **$\gamma\hat{P}^\pi V^\pi$ 를 더하고 빼서** 미지항
$(\hat{V}^\pi - V^\pi)$ 를 한쪽으로 모은다. 그 다음 Neumann 급수와 Hölder 로 각 조각을 묶는다.

1. 두 Bellman 방정식을 쓰고 차를 만든다. 쓰는 것: 두 MDP 모두에서 고정점이 존재한다는 사실
   (`c8-mdp-pomdp-bellman` R1, H2·H3).
2. $\gamma\hat{P}^\pi V^\pi$ 를 더하고 빼서 $(I-\gamma\hat{P}^\pi)(\hat{V}^\pi - V^\pi)$ 를 얻는다
   → C1. **이 한 줄이 보조정리 전체다.**
3. $(I-\gamma\hat{P}^\pi)^{-1}$ 의 노름을 Neumann 급수로 $1/(1-\gamma)$ 로 묶는다. 쓰는 것: H3.
4. $\lVert V^\pi\rVert_\infty \le R_{\max}/(1-\gamma)$ 와 Hölder → C2. 쓰는 것: H1·H4.

**가설 하나를 지우면**: H3 에서 $\hat{P}$ 가 확률분포가 아니면(정규화되지 않은 신경망 출력)
3단계의 $\lVert\hat{P}^\pi\rVert_\infty = 1$ 이 깨지고 $(I-\gamma\hat{P}^\pi)$ 의 가역성조차
보장되지 않는다 — 구현에서 softmax 정규화를 빠뜨리면 상한이 아니라 **등식 (1)이 무의미**해진다.
H1 을 지우면 4단계의 $R_{\max}$ 가 무한이 되어 C2 가 공허하다(C1 은 여전히 참이다).

생략: 연속 상태에서의 버전은 $\ell_1$ 을 전변동 측도로, 합을 적분으로 바꾸면 그대로 간다.
Kearns & Singh 2002 §3 의 보조정리.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** (2)를 $\lVert V^\pi\rVert_\infty$ 대신 **span**
$\mathrm{sp}(V^\pi) = \max_s V^\pi(s) - \min_s V^\pi(s)$ 로 다시 유도하라. 상수가 어떻게
바뀌는지, 그리고 왜 span 쪽이 더 타이트한지 쓰라.
*해답 스케치*: $\sum_{s'}(\hat{P}-P)(s') = 0$ 이므로 임의의 상수 $c$ 에 대해
$(\hat{P}-P)V = (\hat{P}-P)(V - c\mathbf{1})$ 이다. $c = \tfrac12(\max V+\min V)$ 로 잡으면
$\lVert V - c\mathbf{1}\rVert_\infty = \tfrac12\mathrm{sp}(V)$ 이므로 3단계의 인자가
$R_{\max}/(1-\gamma)$ 에서 $\tfrac12\mathrm{sp}(V^\pi)$ 로 바뀐다. 보상이 거의 상수인 MDP 에서
이 차이가 수십 배다.

**P2 (증명, ★★★, R2·R3)** 실데이터와 모델 데이터를 비율 $\beta : 1-\beta$ 로 섞어 쓰는
업데이트의 고정점이 만족하는 방정식을 쓰고, 그 해의 오차가 $\beta$ 에 대해 어떻게 변하는지
상한으로 보여라. $\beta \to 1$ 과 $\beta \to 0$ 의 극한이 각각 무엇이 되는지 확인하라.
*전략과 핵심 부등식*: 혼합 연산자 $T_\beta = \beta T^\* + (1-\beta)\hat{T}^\*$ 가 여전히
$\gamma$-수축임을 보이고(두 수축의 볼록 결합), 그 고정점과 $Q^\*$ 의 차를
$\lVert T_\beta Q^\* - Q^\*\rVert \le (1-\beta)\lVert \hat{T}^\* Q^\* - T^\* Q^\*\rVert$ 로
묶은 뒤 수축으로 나눈다. 전개는 숨긴다.

**P3 (계산, ★, R1)** $\gamma = 0.95$, $R_{\max} = 1$, $\epsilon_r = 0.14$, $\epsilon_P = 1.31$
일 때 (2)의 상한을 계산하라. 그리고 실제 측정값이 $0.309$ 였다면 상한이 몇 배 느슨한지 구하라.
*정답*: 상한 $= 0.14/0.05 + 0.95\cdot1.31\cdot(1/0.05)/0.05 = 2.8 + 497.8 = 500.6$
(허용오차 $0.5$; $R_{\max}/(1-\gamma) = 20$ 을 먼저 계산하면 $0.95\cdot1.31\cdot20/0.05 = 497.8$).
느슨함은 $500.6/0.309 \approx 1.6\times10^3$ 배.
검산: $\epsilon_P$ 를 10 배 줄이면 상한도 거의 10 배 줄어드는지(지배항이 $\epsilon_P$ 항인지)
확인한다.

**P4 (구현, ★★, R1·R3)** 표 형식 MDP 에서 (1)의 **등식**을 수치로 검증하고, $k$-스텝 롤아웃의
가치 오차 곡선을 $\sigma_V$ 4개 값에 대해 그려라.
*루브릭*: ⓐ (1)의 양변 차가 $10^{-12}$ 이하 ⓑ 상한 (2)가 실제 오차를 **위에서** 묶는다
ⓒ $k^\star$ 가 $\sigma_V$ 에 대해 단조 증가함을 20시드 평균으로 보였다 ⓓ $k=0$ 과 $k\to\infty$
의 극한이 각각 순수 비평자·순수 모델임을 코드에서 확인했다 ⓔ 모델을 단순 카운트 추정으로
만들고 행 정규화를 했다(정규화 누락은 R1 의 가설 H3 위반).

**P5 (반례, ★★, R3)** (7)은 $k^\star$ 가 $\epsilon_P$ 에 대해 단조 감소한다고 예측하지만,
표 형식 모델에서 표본 수 $n$ 을 바꾸면 그 단조성이 **관측되지 않는다**. 왜 그런지 설명하고,
단조성이 드러나는 실험 설계를 제안하라.
*성질 체크리스트*: ⓐ $k\to\infty$ 의 극한 오차가 (6)으로 이미 작아서 모델 오차 누적 항이
비평자 항을 못 넘긴다 ⓑ (4)의 $c\epsilon_P$ 는 **최악** 오차인데 롤아웃은 평균적으로 좋은
영역에 머문다 ⓒ 표 형식에서는 $\hat{P}$ 가 참값 주위에 불편하게 분포해 오차가 상쇄된다
ⓓ 단조성을 보려면 **계통 편향**이 있는 모델(예: $\hat{P}$ 를 한 방향으로 민 것)을 쓰거나
데이터 분포 밖에서 롤아웃을 시작해야 한다.

**P6 (논문, ★★, R3·R4·R5)** MBPO(§4–5)와 DreamerV3(§2–3)를 읽고 각각 3문장 이내로 쓰라:
(i) MBPO 의 성능 한계에서 $k$ 가 들어오는 항과 그것이 (4)의 어느 항에 대응하는가,
(ii) DreamerV3 의 목표에서 (5)의 어느 항이 어떻게 변형되었는가,
(iii) 두 논문이 재현에 필요한데 빠뜨린 정보 3개.
*채점 루브릭*: (i) 롤아웃 길이에 **선형**으로 들어오는 모델 오차 항과 $\gamma^{k}$ 로 감쇠하는
정책 이동 항을 구분하면 통과. (ii) 보상·가치 예측 항의 추가와 재구성 가중/정규화(symlog,
KL balancing) 를 짚으면 통과. (iii) 모델 앙상블 크기·재생 비율·$k$ 스케줄·시드·정규화 통계
중 3개. "성능이 좋다"만 쓰면 미달.

**P7 (유도, ★★, R4)** (5)를 유도하고, 추론 분포를 **평활(smoothing)** 형태
$q(z_t\mid o_{1:T},a_{1:T})$ 로 바꾸면 하한이 어떻게 변하는지, 그리고 왜 계획에는 필터링
형태가 필요한지 쓰라.
*해답 스케치*: Jensen 은 $q$ 가 무엇이든 성립하므로 하한은 그대로지만 더 타이트해진다
(평활이 더 많은 정보를 쓰므로). 그러나 계획 시점 $t$ 에는 미래 관측이 없으므로 평활 분포를
**실행할 수 없다** — 학습과 실행의 정보 집합이 달라지면 모델이 실행 불가능한 상태 추정에
맞춰진다.

## 논문 읽기

**필독 3편.** 각 논문에 고정 질문 10개로 1페이지 노트를 쓴다(`lesson-standard.md` §5).

1. **Kearns & Singh, "Near-optimal reinforcement learning in polynomial time" (2002, Machine
   Learning)** — 역할: `원전(seminal)`. <https://doi.org/10.1023/A:1017984413808>
   읽는 이유: R1 의 시뮬레이션 보조정리가 이 논문의 보조정리다. §3 만 읽는다.
   추가 질문: ⓐ 저자들의 보조정리는 (2)와 상수가 다른데, 어느 가정에서 차이가 오는가?
   ⓑ $E^3$ 알고리즘이 "탐색"과 "착취"를 전환하는 기준은 모델 오차와 어떻게 연결되는가?
2. **Janner, Fu, Zhang & Levine, "When to trust your model: model-based policy optimization"
   (2019, NeurIPS)** — 역할: `표준(standard)`. <https://arxiv.org/abs/1906.08253> (§4–5)
   읽는 이유: R3 의 $k$ 교환을 정리와 실험 양쪽으로 다룬 논문이다.
   추가 질문: ⓐ 정리의 성능 한계에서 $k$ 를 늘릴 때 **증가**하는 항과 **감소**하는 항을 각각
   지적하라. ⓑ 실제 알고리즘이 쓰는 $k$ 는 정리가 권하는 값과 같은가, 다르면 왜인가?
3. **Hafner, Pasukonis, Ba & Lillicrap, "Mastering diverse domains through world models" (2023,
   arXiv)** — 역할: `최신(frontier)`. <https://arxiv.org/abs/2301.04104> (§2–3)
   읽는 이유: (5)의 목표가 대규모에서 어떻게 변형·안정화되는지 보는 사례다.
   추가 질문: ⓐ symlog 변환과 KL 균형(KL balancing)은 (5)의 어느 항을 건드리고, 하한 보장은
   유지되는가? ⓑ 단일 하이퍼파라미터 집합으로 다양한 도메인을 푼다는 주장은 무엇을 보장하고
   무엇을 보장하지 않는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU **10초 이내**(측정값: 조건 3 의 격자
(5 품질 × 4 잡음 × 20시드 × 31개 $k$)가 1.3초, 조건 1·2·4 는 합쳐 1초 미만), 메모리
200 MB 이내, numpy 만. 데이터는 레슨이 제공하는 생성 스크립트로 만든다.

```python
import numpy as np

GAMMA = 0.95


def make_mdp(n_s=30, n_a=4, seed=0):
    """참 MDP: Dirichlet(0.3) 전이, 보상은 U(0,1)."""
    rng = np.random.default_rng(seed)
    p = rng.dirichlet(np.full(n_s, 0.3), size=(n_s, n_a))
    r = rng.uniform(0.0, 1.0, size=(n_s, n_a))
    return p, r


def fit_model(P, R, n, rng):
    """(s,a) 마다 n 개 전이 표본으로 카운트 추정 + 보상에 N(0, 0.05) 잡음."""
    Ph = np.empty_like(P)
    for s in range(P.shape[0]):
        for a in range(P.shape[1]):
            Ph[s, a] = rng.multinomial(n, P[s, a]) / n
    return Ph, R + rng.normal(0.0, 0.05, size=R.shape)
```

**수용 기준** — 네 조건을 모두 만족해야 통과다.

1. **등식 (1)의 수치 검증**: $n \in \{10, 50, 500\}$ 에 대해 (1)의 좌변과 우변 차가
   $\max$ 노름으로 $10^{-12}$ 이하다(측정값 $\le 2.7\times10^{-14}$). 동시에 상한 (2)가 실제
   오차를 위에서 묶고, 그 **느슨함 비**(실제/상한)가 $10^{-2}$ 이하임을 보고한다
   (측정값 $6\times10^{-4}$–$5\times10^{-3}$).
2. **모델 오차의 집중 속도**: $n \in \{10, 50, 500, 5000\}$ 에서 5시드 평균 $\epsilon_P$ 가
   $\epsilon_P\sqrt{n} \in [3.5,\ 5.5]$ 를 만족한다 — 다항분포의 $\ell_1$ 집중
   $\mathbb{E}\lVert\hat{p}-p\rVert_1 \approx \sqrt{2\lvert\mathcal{S}\rvert/(\pi n)} = 4.37/\sqrt{n}$
   와 일치해야 한다(측정값 $4.28$–$4.79$).
3. **$k^\star$ 의 단조 이동**: 모델 품질 $n \in \{2,3,5,20,100\}$ 과 비평자 잡음
   $\sigma_V \in \{0.1, 0.3, 1, 3\}$ 의 격자에서, 20시드 평균
   $k^\star = \arg\min_k \lVert Q_k - Q^\*\rVert_\infty$ ($k \in \{0,\dots,30\}$)가 **모든 $n$ 에서
   $\sigma_V$ 에 대해 단조 비감소**다(측정값: $n=2$ 에서 $0.55 \to 2.20 \to 11.40 \to 28.80$).
   반대로 $\epsilon_P$ 쪽(즉 $n$ 쪽) 단조성은 **성립하지 않음**을 함께 보고한다 — 문제 P5 가
   그 이유를 묻는다.
4. **목표 불일치 구성**: $n=200$, seed 0 의 모델 $\hat{P}$ 에 대해 $c$ 를 $V^\pi$ 의 중심화
   단위벡터, $u$ 를 $c$ 에 직교하는 단위벡터로 두고 두 모델
   $\hat{P} + 0.02u$ 와 $\hat{P} + 0.004c$ (각 행을 단체로 재투영)를 만든다. 참 모형에서 뽑은
   보류 카운트($(s,a)$ 마다 2,000개)에 대한 로그 가능도가
   $\mathrm{LL}(\hat{P}+0.004c) > \mathrm{LL}(\hat{P}+0.02u)$ 이면서
   가치 오차가 $\mathrm{err}(\hat{P}+0.004c) > 2\,\mathrm{err}(\hat{P}+0.02u)$ 다
   (측정값: 로그 가능도 $+24{,}060$ vs $+8{,}931$, 가치 오차 $0.0957$ vs $0.0370$ = $2.6$ 배).

**비교 대상(베이스라인)**: ⓐ $k=0$ (순수 비평자)과 $k=30$ (사실상 순수 모델) — 조건 3 의
양 극단이 베이스라인 역할을 한다. ⓑ 참 모형으로 돌린 $k$-스텝 롤아웃: $\epsilon_P = 0$ 이므로
$k$ 가 커질수록 단조 개선되어야 한다(모델 오차 항이 사라졌는지 확인하는 위생 검사).
ⓒ 선택: 실데이터 비율 $\beta$ 를 섞은 혼합 업데이트(문제 P2)를 구현해 $\beta$ 에 대한 편향
감소를 도표화.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 1 의 등식 잔차가 $10^{-6}$ 수준 | $(I-\gamma\hat{P}^\pi)^{-1}$ 를 반복법으로 근사했다 | `np.linalg.solve` 로 직접 풀고 잔차를 다시 본다 |
| 상한 (2)가 실제 오차보다 **작다** | $\epsilon_P$ 를 $\ell_1$ 이 아니라 $\ell_2$ 나 전변동으로 재거나, $R_{\max}$ 대신 평균 보상을 썼다 | $\epsilon_P$ 정의를 행별 $\ell_1$ 합의 최댓값으로 고친다 |
| 조건 2 가 깨진다($\epsilon_P\sqrt{n}$ 가 7 이상) | $\epsilon_P$ 를 평균이 아니라 최댓값의 최댓값으로 재면서 $(s,a)$ 수가 많다 | $(s,a)$ 쌍 수를 출력한다 — 최댓값은 쌍 수에 로그로 커진다 |
| 조건 3 의 단조성이 깨진다 | 시드 수가 적어 $k^\star$ 가 평탄 구간에서 튄다 | 20시드 평균을 쓰고 $k^\star$ 의 표준편차를 함께 출력한다 |
| 조건 4 에서 두 모델의 가능도 차가 거의 없다 | 섭동 후 단체 재투영에서 $\epsilon$ 가 clip 에 먹혔다 | 섭동 전후 행 합과 최소 성분을 출력한다 |
| 조건 4 의 가치 오차 순서가 반대 | $c$ 를 $V^\pi$ 가 아니라 $V^\*$ 로 잡았거나 중심화를 빼먹었다 | $c$ 의 평균이 0 이고 $\lVert c\rVert = 1$ 인지 확인한다 |

## 열린 문제

- **(열린 문제) 가치 인식 모델 학습(value-aware model learning)** — R5 는 가능도가 가치와
  어긋남을 보이지만, 가치와 정렬된 손실을 쓰려면 아직 모르는 $V^\pi$ 가 필요하다. 반복적으로
  추정하며 맞추는 접근은 수렴 보장이 없고, 로봇 규모에서 안정적으로 작동한 사례도 없다.
  현재 접근: [MBPO](https://arxiv.org/abs/1906.08253) 처럼 롤아웃을 짧게 제한하기,
  [PETS](https://arxiv.org/abs/1805.12114) 처럼 앙상블 불확실성으로 가중하기. 비어 있는 자리:
  가치 정렬 손실의 수렴 보장.
- **(열린 문제) model exploitation 을 막는 원칙 있는 불확실성** — 정책 최적화는 모델 오차가
  큰 영역을 적극적으로 찾아간다. 앙상블 분산이나 분포 밖 탐지로 벌점을 주는 방식은 교정
  (calibration)이 없으면 과하거나 부족하다. 현재 접근:
  [PETS](https://arxiv.org/abs/1805.12114),
  [Sinha et al. 2022](https://arxiv.org/abs/2212.14020),
  [등각 예측](https://arxiv.org/abs/2107.07511). 비어 있는 자리: 정책 최적화 **루프 안에서**
  유효한 불확실성 보장.
- **(열린 문제) 잠재 상태가 충분통계량인가** — (5)는 관측 재구성을 요구하지만 그것이
  `c8-mdp-pomdp-bellman` R3 의 충분성을 주지는 않는다. 잠재 상태가 불충분하면 그 위의 DP 는
  Markov 가 아닌 문제에 Bellman 방정식을 적용하는 셈이다. 현재 접근:
  [PlaNet](https://arxiv.org/abs/1811.04551), [DreamerV3](https://arxiv.org/abs/2301.04104).
  비어 있는 자리: 학습된 잠재 상태의 충분성을 검증하는 절차.
- **(열린 문제) 접촉이 있는 동역학의 모델 오차 구조** — (2)는 오차를 최악 상태로 재지만, 접촉
  동역학의 오차는 **접촉 전환면 근처에 집중**된다. 이 구조를 반영한 상한이 없어서, 평활한
  모델이 주는 가치 오차를 예측할 수 없다. 현재 접근:
  [Posa et al. 2014](https://doi.org/10.1177/0278364913506757),
  [Todorov 2014](https://doi.org/10.1109/ICRA.2014.6907751). 비어 있는 자리: 상태 의존
  모델 오차를 가치 오차로 옮기는 국소 상한.

## 개념 점검

`rc quiz c8-model-based-world-models` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는
위 문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c8-model-based-world-models-quiz
questions:
  - id: q1
    type: single
    prompt: "시뮬레이션 보조정리 (2)의 $(1-\\gamma)^{-2}$ 는 어디서 생기는가?"
    choices:
      - "할인된 보상의 합이 두 번 중첩되기 때문"
      - "$(I-\\gamma\\hat{P}^\\pi)^{-1}$ 의 $1/(1-\\gamma)$ 와 $\\lVert V^\\pi\\rVert_\\infty$ 의 $1/(1-\\gamma)$ 가 곱해지기 때문"
      - "전이 오차를 $\\ell_1$ 으로 재기 때문"
      - "$\\max$ 연산자의 1-Lipschitz 성질 때문"
    answer: 1
    explanation: "등식 (1)에서 역행렬의 노름이 $1/(1-\\gamma)$, 그리고 괄호 안 $(\\hat{P}-P)V^\\pi$ 를 Hölder 로 묶을 때 $\\lVert V^\\pi\\rVert_\\infty \\le R_{\\max}/(1-\\gamma)$ 가 또 한 번 들어온다. 두 인자의 곱이 $(1-\\gamma)^{-2}$ 다."
    concept: { front: "시뮬레이션 보조정리의 $(1-\\gamma)^{-2}$", back: "역행렬의 $1/(1-\\gamma)$ × 가치 크기의 $1/(1-\\gamma)$ — span 으로 바꾸면 후자가 타이트해진다" }
  - id: q2
    type: truefalse
    prompt: "Dyna 의 편향은 실데이터를 더 많이 모으면 사라진다."
    answer: false
    explanation: "모델 표본만으로 업데이트하는 극한에서 Dyna 의 고정점은 **모델의** 최적 가치 $\\hat{V}^\\*$ 이고, 그 오차는 (6)처럼 모델 오차에만 의존한다. 실데이터는 모델을 고치는 데 쓰일 때만 편향을 줄이며, 실데이터를 비율 $\\beta$ 로 섞으면 편향이 $\\beta$ 에 비례해 줄지만 표본 효율 이득도 함께 줄어든다."
    concept: { front: "Dyna 의 고정점", back: "모델의 최적 가치 $\\hat{V}^\\*$ — 편향은 모델 오차에만 의존하고 데이터 양으로 사라지지 않는다" }
  - id: q3
    type: single
    prompt: "분기 롤아웃 길이 $k$ 의 최적값은 비평자 잡음 $\\sigma_V$ 가 커질 때 어떻게 되는가?"
    choices:
      - "작아진다 (모델을 덜 믿어야 하므로)"
      - "커진다 (비평자를 덜 믿어야 하므로)"
      - "변하지 않는다"
      - "$\\gamma$ 에만 의존하므로 무관하다"
    answer: 1
    explanation: "(4)에서 비평자 오차는 $\\gamma^k$ 로 감쇠하고 모델 오차는 $k$ 에 따라 누적된다. $\\sigma_V$ 가 크면 감쇠시켜야 할 양이 커지므로 $k^\\star$ 가 커진다 — (7)의 로그 의존성이고, 재현 과제에서 5개 모델 품질 전부에서 단조 증가로 확인된다."
    concept: { front: "$k^\\star$ 의 의존성", back: "$\\sigma_V$ 에 대수적으로 증가, $\\epsilon_P$ 에 대수적으로 감소 — 모델을 믿을 만큼만 굴린다" }
  - id: q4
    type: truefalse
    prompt: "보류 데이터의 로그 가능도가 더 높은 모델은 가치 오차도 더 작다."
    answer: false
    explanation: "모델 오차가 가치에 들어오는 경로는 (1)의 $(\\hat{P}-P)V^\\pi$ 라는 **내적**이므로 $V^\\pi$ 방향 성분만 문제가 된다. 가능도는 방향을 구분하지 않으므로, 가능도가 더 많이 올라간 모델이 가치 오차는 2배 이상 나쁜 예를 구성할 수 있다(재현 과제 조건 4)."
    concept: { front: "목표 불일치(objective mismatch)", back: "가능도는 모든 방향을 동등하게, 가치는 $V^\\pi$ 방향만 센다 — 두 순서가 어긋난다" }
  - id: q5
    type: short
    prompt: "순차 잠재 변수 모델의 ELBO (5)에서 KL 항은 추론 분포를 무엇과 가깝게 만드는가? (한 단어)"
    answer: ["사전 분포", "prior", "prior 분포", "전이 사전분포", "사전분포", "p(z_t|z_{t-1},a_{t-1})"]
    explanation: "KL 항은 $q(z_t\\mid o_{\\le t},a_{<t})$ 를 전이 사전 분포 $p(z_t\\mid z_{t-1},a_{t-1})$ 에 가깝게 당긴다. 즉 잠재 상태가 **예측 가능**해야 한다는 요구이고, 첫 항(재구성)은 정보를 보존해야 한다는 요구다. 두 요구의 균형이 잠재 표현을 결정한다."
    concept: { front: "ELBO 두 항의 역할", back: "재구성 = 정보 보존, KL = 예측 가능성(전이 사전분포와 가까울 것)" }
```

## 이 단계 공부법

1. **등식을 먼저, 상한을 나중에 (60분)** — (1)을 백지에서 유도한다. "$\gamma\hat{P}^\pi V^\pi$
   를 더하고 뺀다"는 한 줄만 기억하면 나머지는 대수다. 상한 (2)는 그 다음 10분이면 나온다.
   순서를 바꾸면 상한만 외우고 등식을 못 쓰게 된다.
2. **상한의 느슨함을 숫자로 만난다 (45분)** — 문제 P3 을 풀고, 재현 과제 조건 1 로 실제/상한
   비를 측정한다. $10^{-3}$ 이라는 숫자를 본 뒤에야 "$(1-\gamma)^{-2}$ 보장"을 설계 지침으로
   쓰면 안 되는 이유가 몸에 남는다. 그 다음 P1 로 span 버전을 만들어 얼마나 타이트해지는지 본다.
3. **$k$ 를 손잡이로 만져 본다 (90분)** — 재현 과제 조건 3 을 $\sigma_V$ 를 바꿔 돌리고
   $k^\star$ 가 움직이는 것을 본다. 그 다음 $n$ 을 바꿔 **단조성이 깨지는 것**을 보고 P5 를
   푼다. 예측이 틀리는 실험을 직접 보는 것이 이 레슨의 핵심 경험이다.
4. **ELBO 를 유도하고 각 항을 해석한다 (60분)** — (5)를 Jensen 한 줄에서 끌어내고, 두 항이
   각각 무엇을 요구하는지 한 문장씩 쓴다. PlaNet §3 의 유도와 대조해 읽는다.
5. **목표 불일치를 스스로 구성한다 (90분)** — 조건 4 를 직접 만든다. $V^\pi$ 방향 $c$ 와 직교
   방향 $u$ 를 구분하는 것이 전부다. 이 구성을 해 본 사람과 안 해 본 사람은 "모델을 더 잘
   학습하면 된다"는 말을 다르게 듣는다.
6. **논문 3편과 열린 문제 (195분)** — Kearns & Singh(보조정리) → MBPO($k$ 교환) →
   DreamerV3(대규모 목표). 논문당 1페이지 노트는 **반드시** 쓴다. 마지막으로 "열린 문제" 중
   가치 인식 모델 학습을 골라, 조건 4 의 구성이 왜 해법이 되지 못하는지($V^\pi$ 를 모른다)
   한 문단으로 쓴다.

**통과 기준**: 백지에서 (1)을 유도하고 (2)의 $(1-\gamma)^{-2}$ 가 생기는 자리를 지적할 수 있고,
$k^\star$ 가 $\sigma_V$ 와 $\epsilon_P$ 에 어떻게 의존하는지 말할 수 있고, (5)를 유도하고
목표 불일치를 구성할 수 있고, 재현 과제의 네 조건을 만족하는 코드와 논문 3편의 노트를 갖고 있다.
