---
id: c8-offline-rl
title: 오프라인 RL 과 분포 이동
summary: >-
  오프라인 데이터만으로 정책을 개선할 때 생기는 외삽 오차를 정리하고, 불확실성 벌점을 넣은
  보수적 가치 반복이 왜 참 가치의 하한을 주는지, 그리고 차선성이 왜 **최적 정책의 분포에서만**
  측정되는 불확실성으로 묶이는지를 증명한다. 이어서 행동 정규화와 가치 보수성이 서로 다른 것을
  보이고, 중요도 가중 오프라인 평가의 분산이 지평에 지수적으로 커짐을 정확한 식으로 계산한다.
objectives:
  - 불확실성 벌점을 넣은 Bellman 연산자의 고정점이 $Q^\*$ 의 하한임을 증명할 수 있다.
  - 차선성 한계 $2(1-\gamma)^{-1}\mathbb{E}_{d^{\pi^\*}}[\Gamma]$ 를 빠진 줄 없이 유도할 수 있다.
  - 단일 정책 집중성이 전 정책 집중성보다 왜 약한 가정인지 설명할 수 있다.
  - 행동 정규화와 가치 보수성이 다른 정책 집합을 허용함을 예로 보일 수 있다.
  - 중요도 가중 추정량의 분산이 $m^T$ 로 커짐을 유도하고 유효 표본 수를 계산할 수 있다.
  - 데이터 품질에 따라 BC 와 보수적 오프라인 RL 의 우열이 역전하는 지점을 실험으로 찾을 수 있다.
prerequisites: [c8-value-based-rl, c8-imitation-learning]
difficulty: 5
estimated_minutes: 540
tags: [offline-rl, pessimism, distribution-shift, cql, off-policy-evaluation, research]
activities:
  - id: c8-offline-rl-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c8-offline-rl-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c8-offline-rl-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 165
  - id: c8-offline-rl-reproduction
    kind: reproduction
    title: 재현 과제 — 보수성 한계 검증과 데이터 품질에 따른 역전 (R2)
    estimated_minutes: 120
  - id: c8-offline-rl-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
papers:
  - id: jin2021-pessimism
    required: true
    role: seminal
    note: "§3-4"
  - id: levine2020-offline-rl
    required: true
    role: survey
    note: "§4-5"
  - id: kumar2020-cql
    required: true
    role: standard
    note: "§3, App. A"
resources:
  - title: "Sutton & Barto, Reinforcement Learning: An Introduction (2nd ed.)"
    kind: book
    note: ch.5.5-5.9 (off-policy 몬테카를로와 중요도 가중). 보조 교재. (공식 URL 미확인)
  - title: "Fu et al. — D4RL: datasets for deep data-driven reinforcement learning (2020)"
    url: https://arxiv.org/abs/2004.07219
    kind: dataset
    note: 권장. 데이터 품질별 표준 벤치마크(random/medium/expert) 의 설계 근거.
  - title: "Fujimoto, Meger & Precup — Off-policy deep RL without exploration (2018)"
    url: https://arxiv.org/abs/1812.02900
    kind: paper
    note: 권장. 외삽 오차를 처음 분리해 보인 글(BCQ).
  - title: "Kostrikov, Nair & Levine — Offline RL with implicit Q-learning (2021)"
    url: https://arxiv.org/abs/2110.06169
    kind: paper
    note: 권장. 분위수 회귀로 분포 밖 행동을 질의하지 않는 접근.
  - title: "Buckman, Gelada & Bellemare — The importance of pessimism in fixed-dataset policy optimization (2020)"
    url: https://arxiv.org/abs/2009.06799
    kind: paper
    note: 권장. 보수성이 왜 선택이 아니라 필수인지에 대한 분석.
  - title: "Thomas & Brunskill — Data-efficient off-policy policy evaluation (2016)"
    url: https://arxiv.org/abs/1604.00923
    kind: paper
    note: 권장. 이중 강건(doubly robust) 추정량과 분산 감소.
---

# 오프라인 RL 과 분포 이동

## 전제와 기호

`c8-value-based-rl` 의 연산자·가중 노름 표기와 `c8-imitation-learning` 의 분포 이동 관점을
쓴다. 추가 **권장 선수**:

- 확률: Hoeffding 부등식, 유효 표본 수(effective sample size), 중요도 가중의 불편성과 분산.
- 선형대수: $(I-\gamma P^\pi)^{-1}$ 의 비음성(성분이 모두 $\ge 0$)과 단조성.
- 볼록 최적화: 제약 최적화의 쌍대와 벌점 형태의 등가성(`r0-convex-optimization`).

표기 추가:

| 기호 | 뜻 |
|---|---|
| $\mathcal{D}$ | 오프라인 데이터셋. $n(s,a)$ 는 $(s,a)$ 의 방문 횟수 |
| $\pi_b$ | 행동(behaviour) 정책. $\mathcal{D}$ 를 만든 정책 |
| $\hat{T}$ | 경험적 Bellman 연산자. $(\hat{T}Q)(s,a) = \hat{r}(s,a) + \gamma\sum_{s'}\hat{P}(s'\mid s,a)\max_{a'}Q(s',a')$ |
| $\Gamma(s,a)$ | 불확실성 벌점. $\lvert(\hat{T}Q)(s,a) - (TQ)(s,a)\rvert \le \Gamma(s,a)$ 를 만족해야 한다 |
| $\tilde{T}$ | 보수적(pessimistic) 연산자. $\tilde{T}Q = \hat{T}Q - \Gamma$ |
| $\tilde{Q}, \tilde{V}, \tilde{\pi}$ | $\tilde{T}$ 의 고정점과 그 그리디 정책 |
| $d^\pi$ | 정규화 할인 점유 분포($(1-\gamma)\sum_t\gamma^t\Pr(s_t,a_t)$) |
| $C^\star$ | 단일 정책 집중성. $C^\star = \max_{s,a} d^{\pi^\star}(s,a)/d^{\pi_b}(s,a)$ |
| $\varrho_{0:T-1}$ | 궤적 중요도 비. $\prod_{t<T}\pi(a_t\mid s_t)/\pi_b(a_t\mid s_t)$ |
| $V_{\max}$ | $R_{\max}/(1-\gamma)$ |

**핵심 어려움을 한 줄로.** 온라인 RL 은 "모르는 곳에 가서 알아본다"가 가능하지만, 오프라인
RL 은 그럴 수 없다. 그런데 `c8-value-based-rl` 의 $\max$ 는 **데이터가 없는 행동도 후보로**
놓고, 그 행동의 $\hat{Q}$ 는 임의로 틀릴 수 있다 — 최적화는 그 오차를 **적극적으로 찾아간다**.
이것이 외삽 오차(extrapolation error)이고 `c8-model-based-world-models` 의 model exploitation 과
같은 구조다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (보수성은 하한을 준다) [D3]** — $\Gamma$ 가 유효한 불확실성 상한이면 $\tilde{T}$ 의 고정점이
  $$
  \tilde{Q} \le Q^\* \quad\text{(성분별)}, \qquad \tilde{V} \le V^\* \tag{1}
  $$
  를 만족한다. 즉 보수적 추정은 **절대 과대평가하지 않는다** — 그래서 "$\tilde{V}$ 가 높다"는
  보고는 신뢰할 수 있다(반대 방향은 아니다).
- **R2 (단일 정책 차선성 한계) [D3]** — 같은 조건에서 $\tilde{\pi}$ 의 차선성은
  $$
  V^\*(s_0) - V^{\tilde{\pi}}(s_0) \;\le\; \frac{2}{1-\gamma}\,
    \mathbb{E}_{(s,a)\sim d^{\pi^\*}}\big[\Gamma(s,a)\big] \tag{2}
  $$
  로 묶인다. **기댓값이 $d^{\pi^\star}$ 에서만 걸린다**는 것이 요점이다 — 데이터가 최적 정책이
  가는 곳만 덮으면 되고, 전 공간을 덮을 필요가 없다. $\Gamma \propto V_{\max}\sqrt{\log(\cdot)/n}$
  꼴이면 (2)는 $\tilde{O}\big(V_{\max}\sqrt{C^\star/n}/(1-\gamma)\big)$ 가 된다.
- **R3 (보수성 없이는 보장이 없다) [D2]** — $\Gamma$ 를 빼면 (1)이 깨지고, 데이터가 없는 한
  $(s,a)$ 만으로도 $\hat{V}$ 가 $V_{\max}$ 까지 부풀 수 있다. 데이터 분포가 좁을수록 그 효과가
  커서, **좁은 데이터에서는 보수적 방법이, 넓은 데이터에서는 비보수적 방법이** 낫다 —
  재현 과제에서 이 역전을 측정한다.
- **R4 (행동 정규화 $\neq$ 가치 보수성) [D2]** — 행동 정규화(지지집합 제약)는 $\pi$ 를 $\pi_b$ 의
  지지집합 안에 묶으므로 **$\pi_b$ 가 한 번도 하지 않은 최적 행동은 영원히 선택 불가**다.
  가치 보수성(CQL 류)은 벌점 후에도 $Q$ 가 충분히 높으면 그 행동을 고를 수 있다. 두 방법의
  허용 정책 집합이 다르고, 전자는 $J(\pi_b)$ 근처에 상한이 걸린다.
- **R5 (OPE 의 분산: 지평의 저주) [D2]** — 궤적 중요도 가중 추정량은 불편이지만
  $$
  \mathbb{E}\big[\varrho_{0:T-1}^2\big] = \prod_{t<T}
    \Big(\textstyle\sum_a \pi(a\mid s_t)^2/\pi_b(a\mid s_t)\Big), \tag{3}
  $$
  이고 $\pi$ 가 결정론, $\pi_b$ 가 $m$ 개 행동에 균등이면 **정확히 $m^T$** 다. 유효 표본 수는
  $n/m^T$ 이므로, $m=4$·$T=8$ 에서 궤적 200만 개의 유효 표본이 **31개**다.

## 유도

### R1 — 보수성이 하한을 주는 이유

**가정.** 모든 $Q$ (또는 적어도 반복에서 등장하는 $Q$)에 대해

$$
\big\lvert (\hat{T}Q)(s,a) - (TQ)(s,a) \big\rvert \;\le\; \Gamma(s,a) \qquad \forall (s,a). \tag{4}
$$

데이터가 없는 $(s,a)$ 에서는 $\Gamma = V_{\max}$ 로 두면 (4)가 자동으로 성립한다(어떤 추정이든
오차가 $V_{\max}$ 를 넘지 못하므로).

**1단계: $\tilde{T}$ 는 $T$ 를 지배하지 않는다.** (4)에서 $\hat{T}Q \le TQ + \Gamma$ 이므로

$$
\tilde{T}Q = \hat{T}Q - \Gamma \;\le\; TQ \qquad \forall Q. \tag{5}
$$

**2단계: 단조성과 수축성.** $\tilde{T}$ 는 $T$ 와 같은 구조($\max$ 와 비음 계수)이므로 단조이고
sup-노름에서 $\gamma$-수축이다(`c8-mdp-pomdp-bellman` R1 의 2단계와 같은 계산). 따라서 고정점
$\tilde{Q}$ 가 유일하게 존재한다.

**3단계: 사다리 논증.** $Q^\*$ 에서 출발해 $\tilde{T}$ 를 반복한다. (5)로
$\tilde{T}Q^\* \le TQ^\* = Q^\*$ 이고, 단조성으로 $\tilde{T}^2 Q^\* \le \tilde{T}Q^\* \le Q^\*$,
귀납으로 $\tilde{T}^k Q^\* \le Q^\*$ 다. $k\to\infty$ 에서 좌변이 $\tilde{Q}$ 로 수렴하므로

$$
\tilde{Q} \le Q^\* ,
$$

즉 (1)이다. $\max$ 를 취해도 순서가 보존되므로 $\tilde{V}\le V^\*$ 다.

**가정이 깨지는 곳.** (4)가 **모든** 반복 $Q$ 에 대해 성립해야 한다. 실무의 $\Gamma$ 는 유한
표본 집중 부등식에서 나오므로 고정된 $Q$ 에 대한 고확률 진술이고, $Q$ 가 데이터에 의존하면
합집합 경계(union bound)나 분할 기법이 필요하다 — 논문들이 로그 인자를 달고 다니는 이유다.
또 $\Gamma$ 를 **작게 잡으면 (1)이 거짓**이 되어 보수성의 의미가 사라진다. 실무의 CQL 계수
$\alpha$ 가 바로 이 선택이고, 너무 작으면 과대평가, 너무 크면 과도한 보수성이다.

### R2 — 차선성이 $d^{\pi^\star}$ 에서만 걸리는 이유

**1단계: 두 조각으로 쪼갠다.**

$$
V^\*(s_0) - V^{\tilde{\pi}}(s_0)
  = \underbrace{\big[V^\*(s_0) - \tilde{V}(s_0)\big]}_{\text{(a)}}
  + \underbrace{\big[\tilde{V}(s_0) - V^{\tilde{\pi}}(s_0)\big]}_{\text{(b)}} .
$$

**2단계: (b) $\le 0$.** $\tilde{\pi}$ 가 $\tilde{Q}$ 의 그리디이므로
$\tilde{V} = \tilde{T}_{\tilde{\pi}}\tilde{V}$ 이고, (5)의 정책 버전으로
$\tilde{T}_{\tilde\pi}\tilde{V} \le T_{\tilde\pi}\tilde{V}$ 다. 따라서
$\tilde{V} \le T_{\tilde\pi}\tilde{V}$ 이고, $T_{\tilde\pi}$ 의 단조성을 반복 적용하면
$\tilde{V} \le (T_{\tilde\pi})^k\tilde{V} \to V^{\tilde{\pi}}$ — 즉 (b) $\le 0$.
**보수적 추정이 자기 정책의 실제 가치를 과대평가하지 않는다**는 뜻이다.

**3단계: (a)를 $\pi^\star$ 의 분포로 옮긴다.** $\tilde{V}$ 가 $\tilde{T}$ 의 고정점이므로 임의의
정책 — 특히 $\pi^\star$ — 에 대해 $\tilde{V} \ge \tilde{T}_{\pi^\star}\tilde{V}$ 다
($\max$ 가 $\pi^\star$ 를 지배하므로). (4)를 두 번 쓰면

$$
\tilde{T}_{\pi^\star}\tilde{V} = \hat{T}_{\pi^\star}\tilde{V} - \Gamma_{\pi^\star}
  \;\ge\; T_{\pi^\star}\tilde{V} - 2\Gamma_{\pi^\star},
$$

여기서 $\Gamma_{\pi^\star}(s) := \Gamma(s,\pi^\star(s))$ 다. 두 부등식을 합치면
$\tilde{V} \ge T_{\pi^\star}\tilde{V} - 2\Gamma_{\pi^\star}$ 이고, $V^\* = T_{\pi^\star}V^\*$ 를
빼면

$$
V^\* - \tilde{V} \;\le\; T_{\pi^\star}V^\* - T_{\pi^\star}\tilde{V} + 2\Gamma_{\pi^\star}
  = \gamma P^{\pi^\star}\big(V^\* - \tilde{V}\big) + 2\Gamma_{\pi^\star}.
$$

**4단계: 역행렬이 분포를 만든다.** 위 식을 정리하면
$(I - \gamma P^{\pi^\star})(V^\* - \tilde{V}) \le 2\Gamma_{\pi^\star}$ 이고,
$(I-\gamma P^{\pi^\star})^{-1} = \sum_t \gamma^t (P^{\pi^\star})^t$ 의 성분이 모두 음이 아니므로
부등식의 방향이 보존된다:

$$
V^\* - \tilde{V} \;\le\; 2\sum_{t\ge0}\gamma^t (P^{\pi^\star})^t \Gamma_{\pi^\star} .
$$

$s_0 \sim \rho_0$ 로 평균하면 우변이 정확히
$\frac{2}{1-\gamma}\mathbb{E}_{d^{\pi^\star}}[\Gamma]$ 다. (a) $\le$ 이 값이고 (b) $\le 0$ 이므로
(2)가 나온다.

**왜 이것이 중요한가.** $(P^{\pi^\star})^t$ 가 등장하는 것이 전부다 — $\tilde{\pi}$ 의 분포는
어디에도 없다. 따라서 **$\pi^\star$ 가 방문하지 않는 영역의 불확실성은 상한에 기여하지
않는다.** 전 정책 집중성($\max_\pi \lVert d^\pi/d^{\pi_b}\rVert_\infty$)은 로봇 문제에서 사실상
무한이지만, 단일 정책 집중성 $C^\star$ 는 "전문가가 간 길을 데이터가 덮는다"는 현실적인 가정이다.

**가정이 깨지는 곳.** (2)는 $\Gamma$ 가 **유효한** 상한일 때만 성립한다. $\Gamma$ 를 교정 없이
앙상블 분산 같은 대리량으로 쓰면 (4)가 보장되지 않고 (1)·(2) 모두 무효다. 또 $d^{\pi^\star}$ 를
모르므로 (2)는 **사후** 보장이다 — 데이터로 $C^\star$ 를 추정할 수 없다는 점이 실무의 한계다.

### R3 — 보수성이 없으면 무엇이 깨지는가

$\Gamma \equiv 0$ 이면 3단계의 사다리 논증이 (5) 없이는 시작되지 않는다. 구체적으로, 데이터가
없는 $(s_0,a_0)$ 에서 $\hat{r}$ 를 0 으로, $\hat{P}$ 를 균등으로 두는 흔한 관행은
$\hat{Q}(s_0,a_0) = \gamma\,\overline{\hat{V}}$ 를 주는데, $\max$ 는 이 값이 다른 행동보다
크면 **그 행동을 고른다**. 즉 "아무 데이터도 없는 행동"이 평균 가치만으로 선택될 수 있다.

반대 방향의 대가도 분명하다. $\Gamma$ 가 크면 데이터가 **충분한** 영역에서도 벌점이 보상을
압도해 $\tilde{\pi}$ 가 $\pi_b$ 보다 못해질 수 있다. 재현 과제에서 벌점 계수 $c$ 를 $0.05$ 에서
$0.2$ 로 올리면 교차점이 옮겨가는 것을 측정한다. **보수성의 양은 데이터 품질에 의존하는
하이퍼파라미터**이고, 그것을 오프라인에서 고르는 원칙이 열린 문제다.

### R4 — 행동 정규화와 가치 보수성의 차이

**행동 정규화(지지집합 제약).** $\pi(a\mid s) = 0$ for $a \notin \mathrm{supp}(\pi_b(\cdot\mid s))$
를 강제한다. 그러면 허용 정책 집합이 $\Pi_b := \{\pi : \mathrm{supp}(\pi)\subseteq\mathrm{supp}(\pi_b)\}$
이고 달성 가능한 최선은 $\max_{\pi\in\Pi_b} J(\pi)$ 다. 어떤 상태에서 최적 행동이
$\mathrm{supp}(\pi_b)$ 밖이면 그 상태에서는 **영원히 최적이 될 수 없다**. 극단적으로
$\pi_b$ 가 결정론이면 $\Pi_b = \{\pi_b\}$ 이고 개선량이 0 이다 — 행동 복제와 같아진다.

**가치 보수성.** $\tilde{T}$ 는 지지집합을 제약하지 않고 **벌점만** 준다. 따라서 지지집합 밖
행동도 $\hat{Q} - \Gamma$ 가 여전히 최대면 선택된다. 데이터가 $(s,a)$ 를 조금이라도 덮으면
$\Gamma$ 가 $V_{\max}$ 보다 작아지므로 그 행동이 후보에 남는다. 즉

$$
\Pi_b \;\subsetneq\; \{\text{가치 보수성이 허용하는 정책}\}, \tag{6}
$$

이고 (2)의 상한은 $\pi^\star$ 가 $\Pi_b$ 밖이어도 여전히 성립한다($\Gamma$ 가 그 경로에서
작기만 하면). **그래서 데이터가 넓고 얕을 때 가치 보수성이 행동 정규화를 이긴다.** 반대로
데이터가 좁고 깊으면(전문가 궤적) $\Pi_b$ 안에 $\pi^\star$ 가 이미 있으므로 행동 정규화가
단순하고 안전하다 — 재현 과제의 역전이 이 구조다.

**가정이 깨지는 곳.** (6)은 $\Gamma$ 가 **방문 횟수에 따라 감소**한다는 전제를 쓴다. 심층망에서
$\Gamma$ 를 앙상블 분산으로 추정하면 분포 밖에서 오히려 **작게** 나오는 일이 흔하다(과신).
그 경우 가치 보수성의 이점이 사라지고 행동 정규화가 더 안전하다.

### R5 — OPE 의 분산

궤적 중요도 가중(IS) 추정량은 $\hat{J}_{\mathrm{IS}} = \frac1N\sum_{i}\varrho^{(i)}_{0:T-1}G^{(i)}$
이고 $\mathbb{E}[\hat{J}_{\mathrm{IS}}] = J(\pi)$ 로 불편이다(각 궤적이 $\pi_b$ 에서 왔으므로).
분산을 보려면 2차 모멘트를 센다. 스텝별로 독립이므로

$$
\mathbb{E}\big[\varrho_{0:T-1}^2\big]
  = \prod_{t<T}\mathbb{E}_{a\sim\pi_b}\!\left[\left(\frac{\pi(a\mid s_t)}{\pi_b(a\mid s_t)}\right)^{2}\right]
  = \prod_{t<T}\sum_a \frac{\pi(a\mid s_t)^2}{\pi_b(a\mid s_t)} ,
$$

즉 (3)이다. $\pi$ 가 결정론이고 $\pi_b$ 가 $m$ 개 행동에 균등이면 각 인자가
$\frac{1^2}{1/m} = m$ 이므로 $\mathbb{E}[\varrho^2] = m^T$ 이고
$\mathrm{Var}(\varrho_{0:T-1}) = m^T - 1$ 이다. 유효 표본 수는

$$
\mathrm{ESS} \;=\; \frac{N}{\mathbb{E}[\varrho^2]} \;=\; \frac{N}{m^T} . \tag{7}
$$

$m=4$, $T=8$, $N = 2\times10^6$ 에서 $\mathrm{ESS} = 31$ 이다 — 궤적 200만 개를 모아도 **유효하게는
31개**다. 실제로 같은 조건의 몬테카를로에서 $\hat{\mathbb{E}}[\varrho]$ 가 $0.95$ 로 (참값 1에서)
벗어나는 것이 관측된다.

**완화 방법과 그 한계.** 스텝별 IS(per-decision IS)와 가중 IS(WIS)는 상수를 줄이지만 지수
의존성을 없애지 못한다. 이중 강건(doubly robust) 추정량은 모델 $\hat{Q}$ 를 제어 변량으로 써서
분산을 줄이지만, $\hat{Q}$ 가 틀리면 그만큼 편향이 들어온다 — 분산을 편향과 바꾸는 것이고
공짜가 아니다(Thomas & Brunskill 2016).

**가정이 깨지는 곳.** (3)은 $\pi_b$ 를 **정확히 안다**고 가정한다. 사람 시연이나 기록된 로그에서
$\pi_b$ 를 추정하면 비의 분모가 틀리고 불편성 자체가 깨진다. 또 $\pi_b(a\mid s) = 0$ 인 $a$ 에
$\pi$ 가 질량을 주면 비가 무한이다 — 지지집합 포함이 (3)의 암묵 전제다.

## 증명 스케치

### R1·R2 — 보수성의 하한과 차선성 [D3]

**가설** H1: (4)가 반복에 등장하는 모든 $Q$ 에서 성립. H2: $0\le\gamma<1$, 보상 유계.
H3: $\Gamma \ge 0$. H4: $\tilde{T}$ 의 고정점이 존재(H2 로부터).
**결론** C1: (1). C2: (2).

**전략**: C1 은 **연산자 지배 + 단조성의 사다리 논증**. C2 는 **(b)$\le0$ 과 (a)의 분포 이동**을
$(I-\gamma P^{\pi^\star})^{-1}$ 의 비음성으로 묶는다.

1. (4)·H3 에서 $\tilde{T}Q \le TQ$ (연산자 지배) → (5). 쓰는 것: H1·H3.
2. $\tilde{T}$ 의 단조성·수축성 → 고정점 유일. 쓰는 것: H2·H4.
3. $Q^\*$ 에서 $\tilde{T}$ 를 반복해 $\tilde{T}^kQ^\*\le Q^\*$ → C1. 쓰는 것: 1·2단계.
4. 그리디 정책에 대해 $\tilde{V}\le V^{\tilde\pi}$ → (b)$\le0$.
5. $\pi^\star$ 에 대해 $\tilde{V}\ge T_{\pi^\star}\tilde{V}-2\Gamma_{\pi^\star}$ 를 세우고
   $(I-\gamma P^{\pi^\star})$ 로 나눈다 → (a)의 상한 → C2. 쓰는 것: (4)를 두 번, 역행렬의 비음성.

**가설 하나를 지우면**: H3($\Gamma\ge0$)을 지우면 1단계의 연산자 지배가 깨져 C1 이 거짓이다
(과대평가가 돌아온다). H1 을 "데이터에 의존하는 $Q$ 에서는 성립하지 않는다"로 약화하면 3단계가
고확률 진술로 바뀌고 (2)에 로그 인자가 붙는다. H2 의 $\gamma<1$ 을 지우면 5단계의 역행렬이
존재하지 않는다.

생략: $\Gamma$ 를 Hoeffding/Bernstein 에서 명시적으로 구성하고 합집합 경계로 모든 $Q$ 에
확장하는 부분은 Jin et al. 2021 §3 의 보조정리들.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R2)** (2)를 $\Gamma(s,a) = c\,V_{\max}\sqrt{\log(2/\delta)/n(s,a)}$ 로 특수화하고,
$n(s,a) \approx N d^{\pi_b}(s,a)$ 를 대입해 상한을 $C^\star$ 와 $N$ 의 함수로 쓰라.
*해답 스케치*: $\mathbb{E}_{d^{\pi^\star}}[\Gamma] = c V_{\max}\sqrt{\log(2/\delta)/N}\,
\mathbb{E}_{d^{\pi^\star}}\big[\sqrt{1/d^{\pi_b}}\big]$ 이고 Cauchy–Schwarz 로
$\mathbb{E}_{d^{\pi^\star}}[\sqrt{1/d^{\pi_b}}] \le \sqrt{C^\star\,\lvert\mathrm{supp}\rvert}$ 꼴로
묶는다. 결과는 $\tilde{O}\big(V_{\max}\sqrt{C^\star/N}/(1-\gamma)\big)$ — $N^{-1/2}$ 와
$\sqrt{C^\star}$ 의 곱이 핵심이다.

**P2 (증명, ★★★, R1·R2)** (b)$\le 0$ 단계를 정확히 증명하라: $\tilde{V}\le V^{\tilde\pi}$ 를
$T_{\tilde\pi}$ 의 단조 반복으로 보이고, 그 과정에서 $\tilde\pi$ 가 **$\tilde{Q}$ 의** 그리디여야
하는 이유를 지적하라. 그리고 $\tilde\pi$ 를 다른 $Q$ 의 그리디로 바꾸면 어디가 깨지는지 쓰라.
*전략과 핵심 부등식*: $\tilde{V} = \max_a\tilde{Q}(\cdot,a) = \tilde{T}_{\tilde\pi}\tilde{V}
\le T_{\tilde\pi}\tilde{V}$ 가 출발점이고, $T_{\tilde\pi}$ 의 단조성으로
$(T_{\tilde\pi})^k\tilde{V}$ 가 증가하며 $V^{\tilde\pi}$ 로 수렴한다. 전개는 숨긴다.

**P3 (계산, ★, R5)** $m = 4$ 개 행동에 균등한 $\pi_b$ 와 결정론 $\pi$ 에 대해 $T = 2, 4, 8$ 의
$\mathbb{E}[\varrho^2]$ 와 $N = 2\times10^6$ 에서의 유효 표본 수를 구하라. $\mathrm{ESS} \ge 1000$
을 유지하려면 $T$ 가 최대 얼마여야 하는가?
*정답*: $\mathbb{E}[\varrho^2] = 4^T = 16,\ 256,\ 65536$. $\mathrm{ESS} = N/4^T = 125000,\ 7812,\ 31$
(허용오차: 정수 반내림). $\mathrm{ESS}\ge1000$ 은 $4^T \le 2000$, 즉 $T \le 5$ ($4^5 = 1024$,
$\mathrm{ESS} = 1953$).
검산: $2\times10^6$ 표본 몬테카를로로 $\mathbb{E}[\varrho^2]$ 를 추정해 $4^T$ 와 $\pm10\%$ 안에
맞는지 확인한다($T=8$ 에서는 추정 자체가 흔들리므로 그 흔들림이 결론이다).

**P4 (구현, ★★, R1·R2·R3)** 표 형식 오프라인 RL 을 구현해 (1)과 (2)를 수치로 검증하고,
벌점 계수 $c$ 와 데이터 품질 $\beta$ 를 바꿔 역전 지점을 찾으라.
*루브릭*: ⓐ 데이터가 없는 $(s,a)$ 의 $\Gamma$ 를 $V_{\max}$ 로 둔다(그러지 않으면 (4)가 깨진다)
ⓑ $\tilde{Q}\le Q^\*$ 를 성분별로 확인했다 ⓒ (2)의 좌변이 우변 이하임을 확인하고 **느슨함 비**를
보고했다 ⓓ $\pi^\star$ 의 점유 분포를 선형 해로 계산했다(샘플링이 아니라) ⓔ $\beta$ 와 $c$ 의
격자에서 승자가 바뀌는 칸을 표로 보고했다.

**P5 (반례, ★★, R4)** "오프라인 RL 은 행동 정책보다 나빠질 수 없다"는 주장이 틀림을 보이라:
보수성이 과도해서 $J(\tilde\pi) < J(\pi_b)$ 가 되는 예를 만들라. 반대로 행동 정규화가
$J(\pi_b)$ 이상을 보장하는 이유도 쓰라.
*성질 체크리스트*: ⓐ $\Gamma$ 가 보상 규모를 압도하면 $\tilde{Q}$ 가 모든 행동에서 거의 같아져
그리디가 **임의**가 된다 ⓑ 그 임의 선택이 $\pi_b$ 보다 나쁠 수 있다 ⓒ 행동 정규화는
$\pi_b \in \Pi_b$ 이므로 "최소한 $\pi_b$"를 후보로 갖는다(정책 개선 단계가 단조이면)
ⓓ 따라서 보수성은 **하한을 주지만 개선을 보장하지 않는다** — (1)과 (2)가 서로 다른 진술임을
구분하는 것이 이 문제의 요점.

**P6 (논문, ★★, R1·R2·R4)** Jin et al. 2021(§3–4), Levine et al. 2020(§4–5), Kumar et al. 2020
(§3, 부록 A)을 읽고 각각 3문장 이내로 쓰라: (i) Jin et al. 의 $\Gamma$ 구성이 (4)를 어떻게
보장하는가, (ii) Levine et al. 이 정리한 외삽 오차의 원인 중 이 레슨이 다루지 않은 것 하나,
(iii) CQL 의 벌점이 왜 **하한**을 주는지와 그 하한이 (1)과 같은 것인지 다른 것인지.
*채점 루브릭*: (i) 집중 부등식 + 합집합 경계(또는 분할)로 데이터 의존 $Q$ 를 덮는다는 점.
(ii) 함수 근사 오차, 반복적 오차 누적, 정책 제약의 최적화 난점 중 하나. (iii) CQL 은
$\mathbb{E}_{\mu}[Q] - \mathbb{E}_{\pi_b}[Q]$ 를 벌하므로 **정책 가치의 기댓값 수준** 하한이고
(1)의 성분별 하한보다 약하다는 점을 짚으면 통과. "보수적이다"만 쓰면 미달.

**P7 (유도, ★★, R5)** (3)을 유도하고, 스텝별 IS 추정량
$\frac1N\sum_i\sum_t\gamma^t\varrho^{(i)}_{0:t}r^{(i)}_t$ 의 2차 모멘트가 왜 더 작은지, 그리고
그래도 왜 지수 의존성이 남는지 쓰라.
*해답 스케천*: 궤적 IS 는 모든 보상에 $\varrho_{0:T-1}$ 을 곱하지만 스텝별 IS 는 $r_t$ 에
$\varrho_{0:t}$ 만 곱한다. $t$ 가 작은 항의 분산이 $m^{t+1}$ 로 작아 합의 분산이 줄지만,
$t = T-1$ 항은 여전히 $m^T$ 다 — **가장 늦은 보상이 지수 항을 결정**한다. 할인이 $\gamma^t$ 로
늦은 항을 눌러 주는 것이 유일한 완화다.

## 논문 읽기

**필독 3편.** 각 논문에 고정 질문 10개로 1페이지 노트를 쓴다(`lesson-standard.md` §5).
3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Jin, Yang & Wang, "Is pessimism provably efficient for offline RL?" (2021, ICML)** — 역할:
   `원전(seminal)`. <https://arxiv.org/abs/2012.15085> — §3–4.
   읽는 이유: R1 의 (1)과 R2 의 (2)가 이 논문의 정리이고, **단일 정책 집중성**이라는 개념이
   여기서 선명해진다.
   추가 질문: ⓐ 저자들의 $\Gamma$ (논문의 신뢰구간)가 (4)를 만족함을 보이는 자리는 어디이고
   어떤 집중 부등식을 쓰는가? ⓑ 하한(lower bound) 정리는 보수성이 **필수**임을 어떻게 말하는가?
2. **Levine, Kumar, Tucker & Fu, "Offline reinforcement learning: tutorial, review, and
   perspectives on open problems" (2020, arXiv)** — 역할: `서베이(survey)`.
   <https://arxiv.org/abs/2005.01643> — §4–5.
   읽는 이유: 외삽 오차·분포 이동의 원인을 분류한 표준 지도다. 이 레슨은 그중 일부만 다룬다.
   추가 질문: ⓐ 저자들이 드는 실패 원인 중 이 레슨의 (4) 틀로 설명되지 **않는** 것은?
   ⓑ 오프라인 평가 없이 하이퍼파라미터를 고르는 문제(§5)를 저자들은 어떻게 다루는가?
3. **Kumar, Zhou, Tucker & Levine, "Conservative Q-learning for offline reinforcement learning"
   (2020, NeurIPS)** — 역할: `표준(standard)`. <https://arxiv.org/abs/2006.04779> — §3 과 부록 A.
   읽는 이유: R4 의 가치 보수성을 실제로 구현한 표준 알고리즘이고, 그 하한 주장이 (1)과
   어떻게 다른지 비교하는 것이 목적이다.
   추가 질문: ⓐ 부록 A 의 하한 정리는 어떤 노름·어떤 분포에서의 하한인가?
   ⓑ 계수 $\alpha$ 를 데이터로 고르는 절차가 논문에 있는가, 없으면 실험에서 어떻게 정했는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU **2분 이내**, 메모리 200 MB 이내,
numpy 만. 데이터는 생성 스크립트로 만든다(D4RL 의 random/medium/expert 구분을 표 형식으로
축소한 것이다 — 공개 데이터셋 없이 같은 **구조**를 재현한다).

```python
import numpy as np

GAMMA = 0.95


def make_mdp(n_s=20, n_a=4, seed=0):
    rng = np.random.default_rng(seed)
    p = rng.dirichlet(np.full(n_s, 0.4), size=(n_s, n_a))
    r = rng.uniform(0.0, 1.0, size=(n_s, n_a))
    return p, r


def behaviour(pi_star, beta, n_s, n_a):
    """beta 만큼 전문가 행동에 질량을 주고 나머지는 균등 (beta=0 random, 1 expert)."""
    b = np.full((n_s, n_a), (1 - beta) / n_a)
    b[np.arange(n_s), pi_star] += beta
    return b / b.sum(axis=1, keepdims=True)
```

데이터는 궤적 10개 × 길이 40 으로 모으고, 벌점은
$\Gamma(s,a) = c\,V_{\max}\sqrt{\log 4 / n(s,a)}$ (방문 없으면 $V_{\max}$)로 둔다.
비교 대상은 세 가지다: **BC**(상태별 최빈 행동), **보수적 VI**($\tilde{T}$ 의 고정점),
**비보수적 VI**($\Gamma\equiv0$).

**수용 기준** — 네 조건을 모두 만족해야 통과다.

1. **하한 (1)**: 궤적 수 $\in\{2,5,20,100\}$ (균등 행동 정책)에서 $\tilde{Q} \le Q^\* + 10^{-9}$ 가
   **성분별로** 성립한다(측정: 네 경우 모두 성립).
2. **차선성 한계 (2)**: 같은 네 경우에서
   $V^\*(s_0)-V^{\tilde\pi}(s_0) \le \frac{2}{1-\gamma}\mathbb{E}_{d^{\pi^\star}}[\Gamma]$ 가
   성립하고, **느슨함 비**(좌변/우변)를 보고한다(측정값 $0.006$–$0.017$ — 상한이 60–160배 느슨).
   $d^{\pi^\star}$ 는 $(1-\gamma)(I-\gamma (P^{\pi^\star})^\top)^{-1}\rho_0$ 로 **선형 해**로 구한다.
3. **데이터 품질에 따른 역전**: $c = 0.05$, $\beta \in \{0, 0.25, 0.5, 0.75, 1\}$, 12 시드 평균에서
   ⓐ $\beta=0$ 에서 BC 가 **행동 정책보다도 나쁘다**($7.74 < 8.54$),
   ⓑ 보수적 VI 는 모든 $\beta$ 에서 행동 정책 이상이다,
   ⓒ $\beta \le 0.5$ 에서 보수적 VI $>$ BC, $\beta \ge 0.75$ 에서 둘이 모두 $J^\star$ 에 도달해
   동률이다(측정값 $J^\star = 13.285$).
4. **보수성은 공짜가 아니다**: 같은 격자에서 ⓐ $\beta=0$(넓은 데이터)에서는 비보수적 VI 가
   보수적 VI 보다 낫고($12.894 > 12.498$), ⓑ $\beta\in\{0.25,0.5,0.75\}$(좁은 데이터)에서는
   보수적 VI 가 낫다($13.156>12.940$, $13.283>12.911$, $13.285>12.948$), ⓒ $c$ 를 $0.05\to0.2$ 로
   올리면 $\beta=0.25$ 의 승자가 보수적 VI 에서 비보수적 VI 로 **바뀐다**.

**비교 대상(베이스라인)**: ⓐ 행동 정책 자신의 가치 $J(\pi_b)$ — 선형 해로 정확히 계산하며,
"데이터보다 나아졌는가"의 기준점이다. ⓑ $J^\star$ — 도달 가능한 상한. ⓒ 선택: 행동 정규화
(지지집합 제약) 버전을 구현해 $\beta$ 가 작을 때 $J(\pi_b)$ 근처에 **갇히는 것**을 확인한다
(R4 의 (6)이 코드로 보인다).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 1 이 깨진다($\tilde{Q} > Q^\*$) | 미방문 $(s,a)$ 의 $\Gamma$ 를 $V_{\max}$ 로 두지 않았다 | $\Gamma[n=0]$ 를 출력한다 — $R_{\max}/(1-\gamma)$ 여야 한다 |
| 조건 2 의 비가 1 을 넘는다 | $d^{\pi^\star}$ 를 정규화하지 않았거나($(1-\gamma)$ 누락) 전치를 빠뜨렸다 | $\sum_s d^{\pi^\star}(s) = 1$ 을 확인한다 |
| 역전이 보이지 않는다 | 데이터가 너무 많아 모든 $(s,a)$ 가 덮였다 | $n(s,a)=0$ 인 쌍의 수를 출력한다 — $\beta$ 가 커지면 늘어야 한다 |
| BC 가 $\beta=0$ 에서도 잘한다 | 미방문 상태에서 전문가 행동을 기본값으로 썼다(누출) | 기본 행동을 0 으로 고정하고 다시 돌린다 |
| 보수적 VI 가 모든 $\beta$ 에서 진다 | $c$ 가 너무 커서 벌점이 보상($\le1$)을 압도한다 | $\Gamma$ 의 중앙값과 $R_{\max}$ 를 함께 출력한다 |
| 시드마다 승자가 바뀐다 | 12 시드로는 차이가 표준오차 안이다 | 시드 수를 늘리고 승패를 시드별로 집계한다 |

## 열린 문제

- **(열린 문제) 오프라인에서 보수성의 양을 고르는 원칙** — (2)는 $\Gamma$ 가 유효하면 성립하지만,
  $\Gamma$ 를 **얼마나** 크게 잡을지는 데이터 품질에 의존하고(재현 과제 조건 4) 오프라인에서는
  검증 집합으로 고를 수도 없다. 온라인 평가 한 번이 이 문제를 없애지만 그 한 번이 비싼 것이
  오프라인 RL 의 전제다. 현재 접근: [CQL](https://arxiv.org/abs/2006.04779) 의 $\alpha$ 자동
  조정, [IQL](https://arxiv.org/abs/2110.06169) 처럼 분포 밖을 **질의하지 않는** 설계.
  비어 있는 자리: 오프라인 데이터만으로 보수성 수준을 고르는 선택 규칙.
- **(열린 문제) 교정된 불확실성 $\Gamma$ 를 심층망에서 얻기** — 표 형식에서는 방문 횟수가
  $\Gamma$ 를 준다. 심층망에서는 앙상블 분산이 분포 밖에서 오히려 작아지는 과신이 흔해 (4)가
  보장되지 않는다. 현재 접근: [등각 예측](https://arxiv.org/abs/2107.07511),
  [시스템 수준 OOD 탐지](https://arxiv.org/abs/2212.14020). 비어 있는 자리: 제어 루프 안에서
  (4)를 보증하는 $\Gamma$.
- **(열린 문제) 오프라인 평가의 지평의 저주를 구조로 깨기** — (7)의 $m^T$ 는 가정 없이는
  피할 수 없다. 로봇 과제의 구조(상태가 저차원 다양체, 보상이 희소·지연, 정책이 국소적)를
  가정으로 적어 다항 분산을 받는 하위 클래스는 정리되지 않았다. 현재 접근:
  [이중 강건 추정](https://arxiv.org/abs/1604.00923), 모델 기반 OPE
  (`c8-model-based-world-models`). 비어 있는 자리: 로봇 구조를 쓰는 분산 한계.
- **(열린 문제) 데이터 품질을 사전에 진단하기** — 재현 과제의 역전은 $\beta$ 를 **알고 있을 때**
  관측된다. 실제로는 데이터셋을 받고 BC 와 오프라인 RL 중 무엇을 쓸지 **먼저** 정해야 하는데,
  그 판단을 데이터만으로 하는 지표가 없다. 현재 접근:
  [D4RL](https://arxiv.org/abs/2004.07219) 의 품질 분류, 행동 정책의 엔트로피·수익 분포 통계.
  비어 있는 자리: 알고리즘 선택을 예측하는 데이터셋 지표.

## 개념 점검

`rc quiz c8-offline-rl` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위 문제 세트와
재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c8-offline-rl-quiz
questions:
  - id: q1
    type: single
    prompt: "보수적 연산자 $\\tilde{T}Q = \\hat{T}Q - \\Gamma$ 의 고정점이 $Q^\\*$ 의 하한인 이유는?"
    choices:
      - "$\\Gamma$ 가 항상 $V_{\\max}$ 보다 작기 때문"
      - "$\\tilde{T}Q \\le TQ$ (연산자 지배)와 단조성으로 $\\tilde{T}^k Q^\\* \\le Q^\\*$ 이기 때문"
      - "$\\hat{T}$ 가 $T$ 의 불편 추정이기 때문"
      - "데이터가 많아지면 $\\Gamma \\to 0$ 이기 때문"
    answer: 1
    explanation: "(4)에서 $\\hat{T}Q \\le TQ + \\Gamma$ 이므로 $\\tilde{T}Q \\le TQ$ 다. $Q^\\*$ 에서 $\\tilde{T}$ 를 반복하면 단조성으로 $\\tilde{T}^kQ^\\* \\le Q^\\*$ 이고 극한이 $\\tilde{Q}$ 이므로 $\\tilde{Q}\\le Q^\\*$ 다. 불편성이나 $\\Gamma\\to0$ 은 쓰이지 않는다."
    concept: { front: "보수성이 하한을 주는 논증", back: "연산자 지배 $\\tilde{T}Q\\le TQ$ + 단조성의 사다리 — 불편성은 필요 없다" }
  - id: q2
    type: single
    prompt: "차선성 한계 (2)에서 불확실성 $\\Gamma$ 의 기댓값이 걸리는 분포는?"
    choices:
      - "행동 정책의 분포 $d^{\\pi_b}$"
      - "최적 정책의 분포 $d^{\\pi^\\*}$"
      - "학습된 정책의 분포 $d^{\\tilde\\pi}$"
      - "모든 정책에 대한 최악 분포"
    answer: 1
    explanation: "유도 4단계에서 등장하는 것은 $(P^{\\pi^\\*})^t$ 뿐이고 $\\tilde\\pi$ 의 분포는 상한에 나타나지 않는다. 그래서 데이터가 **최적 정책이 가는 길만** 덮으면 되고(단일 정책 집중성), 전 정책 집중성이라는 훨씬 강한 가정이 필요 없다."
    concept: { front: "단일 정책 집중성", back: "(2)는 $d^{\\pi^\\*}$ 에서만 $\\Gamma$ 를 재므로 전 공간 커버리지가 필요 없다" }
  - id: q3
    type: truefalse
    prompt: "보수적 오프라인 RL 은 행동 정책보다 나빠질 수 없다."
    answer: false
    explanation: "(1)은 **가치의 하한**이고 (2)는 $\\Gamma$ 가 작을 때의 차선성 한계다. 둘 다 '$J(\\tilde\\pi) \\ge J(\\pi_b)$' 를 말하지 않는다. 벌점이 보상 규모를 압도하면 $\\tilde{Q}$ 가 거의 평평해져 그리디가 임의로 정해지고, 실제로 행동 정책보다 나빠질 수 있다(문제 P5)."
    concept: { front: "하한 ≠ 개선 보장", back: "(1)은 과대평가를 막고 (2)는 $\\Gamma$ 가 작을 때만 유용 — 어느 것도 $J(\\pi_b)$ 를 보장하지 않는다" }
  - id: q4
    type: truefalse
    prompt: "행동 정규화(지지집합 제약)와 가치 보수성은 같은 정책 집합을 허용한다."
    answer: false
    explanation: "지지집합 제약은 $\\pi_b$ 가 하지 않은 행동을 **구조적으로** 배제하므로, 최적 행동이 지지집합 밖이면 영원히 선택 불가다($\\pi_b$ 가 결정론이면 행동 복제와 같아진다). 가치 보수성은 벌점만 주므로 데이터가 조금이라도 있으면 그 행동이 후보에 남는다."
    concept: { front: "행동 정규화 vs 가치 보수성", back: "전자는 지지집합 밖을 구조적으로 배제(상한이 $\\Pi_b$ 에 걸림), 후자는 벌점만 준다" }
  - id: q5
    type: short
    prompt: "결정론 정책을 $m$ 개 행동 균등 행동정책으로 평가할 때 궤적 중요도 가중의 2차 모멘트는? ($m$ 과 지평 $T$ 로)"
    answer: ["m^T", "m**T", "m^T 입니다", "m의 T승", "m^{T}"]
    explanation: "스텝별 2차 모멘트가 $\\sum_a \\pi(a)^2/\\pi_b(a) = 1/(1/m) = m$ 이고 스텝이 독립이므로 곱해져 $m^T$ 다. 유효 표본 수는 $N/m^T$ 이고, $m=4$·$T=8$ 에서 궤적 200만 개의 유효 표본은 31개뿐이다."
    concept: { front: "지평의 저주", back: "$\\mathbb{E}[\\varrho^2] = m^T$, $\\mathrm{ESS} = N/m^T$ — 스텝별 IS 와 이중 강건은 상수만 줄인다" }
```

## 이 단계 공부법

1. **연산자 지배를 먼저 본다 (45분)** — (5)의 한 줄($\tilde{T}Q \le TQ$)을 쓰고, 거기서 사다리
   논증으로 (1)까지 백지에서 간다. **불편성을 쓰지 않는다**는 점을 확인하는 것이 핵심이다 —
   오프라인 RL 의 보장은 통계적 불편성이 아니라 **순서(부등식)** 위에 서 있다.
2. **(2)의 분포가 왜 $\pi^\star$ 인지 손으로 확인한다 (75분)** — 3·4단계를 다시 쓰면서 어디서
   $\tilde\pi$ 가 사라지는지 추적한다. 이 한 가지가 오프라인 RL 이론의 전환점이고,
   `c8-imitation-learning` 의 공변량 이동과 대비해 읽으면 구조가 보인다.
3. **지평의 저주를 숫자로 만난다 (45분)** — 문제 P3 을 풀고 $m=4$, $T=8$ 의 ESS 31 을 직접
   계산한다. 그 다음 $2\times10^6$ 표본으로 $\mathbb{E}[\varrho]$ 를 추정해 참값 1 에서
   벗어나는 것을 본다 — "불편 추정량"이 쓸모없을 수 있다는 것을 몸으로 아는 단계다.
4. **역전을 실험으로 만든다 (120분)** — 재현 과제 조건 1·2(이론 검증)를 먼저 통과시키고
   조건 3·4(역전)로 간다. $\beta$ 와 $c$ 의 격자를 직접 돌려 **승자가 바뀌는 칸**을 찾는다.
   이 표를 만들어 본 사람은 "오프라인 RL 이 BC 보다 좋다"는 문장을 다시 쓰지 않는다.
5. **논문 3편을 이론→실무 순서로 (150분)** — Jin et al.(보장) → Levine et al.(지도) →
   CQL(구현). 논문당 1페이지 노트는 **반드시** 쓴다. CQL 노트에는 "하한이 어느 노름·어느
   분포에서인가"를 한 줄로 적어 (1)과 비교한다.
6. **무엇을 못 하는지로 끝낸다 (105분)** — "열린 문제" 중 보수성 수준 선택을 골라, 재현 과제의
   격자에서 $c$ 를 **데이터만 보고** 고르는 규칙을 하나 제안하고 그 규칙이 깨지는 경우를 쓴다.

**통과 기준**: 백지에서 (1)과 (2)를 유도하고 (2)의 기댓값 분포가 $d^{\pi^\star}$ 인 이유를
말할 수 있고, (3)과 ESS 를 계산할 수 있고, 데이터 품질 격자에서 역전 지점을 찾은 코드와 논문
3편의 노트를 갖고 있다.
