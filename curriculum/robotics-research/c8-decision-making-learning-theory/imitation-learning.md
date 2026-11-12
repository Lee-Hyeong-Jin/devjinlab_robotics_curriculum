---
id: c8-imitation-learning
title: 모방학습과 공변량 이동
summary: >-
  행동 복제(BC)의 오차가 지평에 대해 $O(\epsilon T^2)$ 로 커지는 이유를 유도하고 그 차수가
  타이트함을 하한 구성으로 보인다. 이어서 DAgger 가 학습자 자신의 분포에서 질의함으로써 후회를
  $O(\epsilon T)$ 로 낮추는 논증을 온라인 학습의 no-regret 성질로 세운다. 마지막으로 역강화학습의
  보상 모호성을 정리하고 최대 엔트로피 해를 Lagrange 쌍대로 유도한다.
objectives:
  - BC 의 복합 오차 상한 $O(\epsilon T^2)$ 를 빠진 줄 없이 유도할 수 있다.
  - 그 차수가 타이트함을 보이는 하한 MDP 를 구성할 수 있다.
  - DAgger 의 후회 한계 $O(\epsilon T)$ 를 no-regret 온라인 학습으로 재구성할 수 있다.
  - BC 와 DAgger 의 지평 의존 차수를 수치 실험으로 1 과 2 로 분리할 수 있다.
  - 보상 함수가 최적 정책만으로는 식별되지 않음을 두 가지 변환으로 보일 수 있다.
  - 특징 기대값 일치 제약 하 최대 엔트로피 해가 $p(\tau)\propto\exp(\theta^\top f(\tau))$ 임을 유도할 수 있다.
prerequisites: [c8-mdp-pomdp-bellman, c8-policy-gradient]
difficulty: 5
estimated_minutes: 540
tags: [imitation-learning, behavior-cloning, dagger, covariate-shift, irl, research]
activities:
  - id: c8-imitation-learning-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c8-imitation-learning-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c8-imitation-learning-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 165
  - id: c8-imitation-learning-reproduction
    kind: reproduction
    title: 재현 과제 — BC 와 DAgger 의 지평 의존 차수 분리 (R2)
    estimated_minutes: 120
  - id: c8-imitation-learning-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
papers:
  - id: ross2010-efficient-reductions
    required: true
    role: seminal
    note: "§2-3"
  - id: ross2011-dagger
    required: true
    role: seminal
    note: "§3-4, App."
  - id: ziebart2008-maxent-irl
    required: true
    role: seminal
    note: "§3-4"
resources:
  - title: "Sutton & Barto, Reinforcement Learning: An Introduction (2nd ed.)"
    kind: book
    note: ch.13 (정책 경사) 와 ch.17.4 (보상 설계). 보조 교재. (공식 URL 미확인)
  - title: "Ho & Ermon — Generative adversarial imitation learning (2016)"
    url: https://arxiv.org/abs/1606.03476
    kind: paper
    note: 권장. 점유도 일치(occupancy matching)로 본 모방학습.
  - title: "Abbeel & Ng — Apprenticeship learning via inverse reinforcement learning (2004)"
    url: https://doi.org/10.1145/1015330.1015430
    kind: paper
    note: 권장. 특징 기대값 일치의 원형과 모호성 논의.
  - title: "Chi et al. — Diffusion policy (2023)"
    url: https://arxiv.org/abs/2303.04137
    kind: paper
    note: 권장. 현대 BC 가 다봉 행동 분포를 다루는 방법.
  - title: "Zhao et al. — Learning fine-grained bimanual manipulation with low-cost hardware (2023)"
    url: https://arxiv.org/abs/2304.13705
    kind: paper
    note: 권장. 행동 청크(action chunking)가 복합 오차에 주는 효과.
---

# 모방학습과 공변량 이동

## 전제와 기호

`c8-mdp-pomdp-bellman` 의 MDP 표기와 `c8-policy-gradient` 의 점유 분포 표기를 쓴다. 이
레슨은 **유한 지평** $T$ 를 쓰고 할인하지 않는다(비용의 합). 추가 **권장 선수**:

- 확률: 유니온 바운드, 전변동 거리, 마팅게일 없이 가능한 1차 결합 논증.
- 온라인 학습: 후회(regret)의 정의와 no-regret 알고리즘(Follow-the-Leader 계열)의 성질.
- 볼록 최적화: 등식 제약 하 엔트로피 최대화와 Lagrange 쌍대(`r0-convex-optimization`).

표기 추가:

| 기호 | 뜻 |
|---|---|
| $T$ | 지평. 비용은 $J(\pi) = \mathbb{E}\big[\sum_{t=0}^{T-1} c(s_t,a_t)\big]$, $c \in [0,1]$ |
| $\pi^\star$ | 전문가(expert) 정책. $\hat{\pi}$ 는 학습된 정책 |
| $d_\pi^t$ | 정책 $\pi$ 를 $t$ 스텝 따를 때의 상태 분포. $d_\pi = \frac1T\sum_{t<T} d_\pi^t$ |
| $\epsilon$ | 지도 오차. $\epsilon = \mathbb{E}_{s\sim d_{\pi^\star}}\big[\mathbf{1}\{\hat{\pi}(s)\neq\pi^\star(s)\}\big]$ |
| $\epsilon_N$ | DAgger 의 $N$ 반복 평균 온라인 손실. $\epsilon_N = \min_\pi \frac1N\sum_{i=1}^N \ell_i(\pi)$ |
| $u$ | 비용-대-목표 격차 상한. $u = \max_{s,a}\big(Q^{\pi^\star}_{T-t}(s,a) - V^{\pi^\star}_{T-t}(s)\big)$ |
| $f(\tau)$ | 궤적 특징. $f(\tau) = \sum_t \phi(s_t,a_t) \in \mathbb{R}^m$ |
| $\theta$ | 보상 매개변수. 선형 보상 $r_\theta(s,a) = \theta^\top\phi(s,a)$ |

비용은 $[0,1]$ 로 정규화한다. 따라서 $J(\pi^\star) \ge 0$ 이고 어떤 정책도 $J \le T$ 다 —
**모든 상한은 $T$ 에서 자명하게 포화**하므로, 의미 있는 영역은 $\epsilon T \ll 1$ 이다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (BC 의 복합 오차) [D3]** — $\hat{\pi}$ 가 전문가 분포에서 지도 오차 $\epsilon$ 을 가질 때
  $$
  J(\hat{\pi}) \;\le\; J(\pi^\star) + \epsilon\,T^2 , \tag{1}
  $$
  더 정확히는 $J(\hat{\pi}) - J(\pi^\star) \le \sum_{t=0}^{T-1} \epsilon\,(T-t) \le \tfrac12\epsilon T(T+1)$
  이다. **$T^2$ 은 "실수 확률 $\epsilon T$" 와 "실수 이후 남은 비용 $T$" 의 곱**이다.
- **R2 (하한: $T^2$ 은 타이트하다) [D3]** — 두 상태(궤도 위/이탈)와 두 행동만으로
  $J(\hat{\pi}) - J(\pi^\star) = \Omega(\epsilon T^2)$ 인 MDP 와 $\hat{\pi}$ 를 만들 수 있다.
  따라서 (1)의 차수는 증명 기법의 느슨함이 아니라 **BC 라는 알고리즘의 성질**이다.
- **R3 (DAgger 의 후회 한계) [D3]** — DAgger 를 no-regret 온라인 학습으로 돌리면 $N$ 반복 뒤
  어떤 $\hat{\pi} \in \{\pi_1,\dots,\pi_N\}$ 에 대해
  $$
  J(\hat{\pi}) \;\le\; J(\pi^\star) + u\,T\,\epsilon_N + O(1), \tag{2}
  $$
  즉 $T$ 에 **선형**이다. 차이를 만드는 것은 손실을 **학습자 자신의 분포** $d_{\pi_i}$ 에서
  재는 것이고, 그래서 학습자가 실제로 방문하는 이탈 상태에서의 복구 행동을 배운다.
- **R4 (IRL 의 보상 모호성) [D2]** — 최적 정책 하나만으로는 보상이 식별되지 않는다. 적어도
  두 종류의 자유도가 있다: ⓐ 양의 스칼라 배 $r \mapsto \alpha r$ ($\alpha>0$),
  ⓑ 퍼텐셜 성형 $r(s,a,s') \mapsto r(s,a,s') + \gamma\Phi(s') - \Phi(s)$ — 둘 다 최적 정책
  집합을 보존한다. 따라서 IRL 은 **추가 원칙 없이는 미결정 문제**다.
- **R5 (최대 엔트로피 해) [D2]** — 특징 기대값 일치 제약
  $\mathbb{E}_{p}[f(\tau)] = \mathbb{E}_{\text{전문가}}[f(\tau)]$ 아래 궤적 분포의 엔트로피를
  최대화하면
  $$
  p_\theta(\tau) \;=\; \frac{1}{Z(\theta)}\exp\!\big(\theta^\top f(\tau)\big),
    \qquad Z(\theta) = \sum_\tau \exp\!\big(\theta^\top f(\tau)\big), \tag{3}
  $$
  이고 $\theta$ 는 **로그 가능도의 볼록 문제**로 결정된다. 경사는
  $\nabla_\theta \log p_\theta(\tau_{\text{data}}) = f(\tau_{\text{data}}) - \mathbb{E}_{p_\theta}[f(\tau)]$
  — 즉 **특징 기대값의 차**다.

## 유도

### R1 — BC 의 복합 오차

**설정.** $\hat{\pi}$ 와 $\pi^\star$ 를 같은 초기 상태에서 동시에 굴린다(짝지음, coupling).
$t$ 스텝까지 두 정책이 한 번도 다른 행동을 고르지 않았다는 사건을 $A_t$ 라 하자.

**1단계: 불일치가 처음 생길 확률.** $A_{t}$ 가 성립하는 동안 $\hat{\pi}$ 가 방문하는 상태의
분포는 $d^t_{\pi^\star}$ 와 **같다**(같은 행동을 했으므로). 따라서 시점 $t$ 에서 처음 다를 확률은
$d^t_{\pi^\star}$ 에서의 오차로 묶인다:

$$
\Pr\!\big[\text{시점 } t \text{ 에서 처음 불일치}\big]
  \;\le\; \mathbb{E}_{s\sim d^t_{\pi^\star}}\big[\mathbf{1}\{\hat{\pi}(s)\neq\pi^\star(s)\}\big]
  \;=:\; \epsilon_t , \qquad \frac{1}{T}\sum_{t<T}\epsilon_t = \epsilon . \tag{4}
$$

**2단계: 불일치 이후의 비용.** 한 번 달라지면 그 뒤는 아무 보장이 없다. 비용이 $[0,1]$ 이므로
남은 $T-t$ 스텝의 비용은 최대 $T-t$ 이고, 전문가가 같은 구간에서 쓰는 비용은 $\ge 0$ 이다.
따라서 그 사건의 기여는 $\le (T-t)$ 다.

**3단계: 합산.** 서로 배타적인 "처음 불일치 시점" 사건으로 분해하면

$$
J(\hat{\pi}) - J(\pi^\star)
  \;\le\; \sum_{t=0}^{T-1} \epsilon_t \,(T-t)
  \;\le\; \Big(\max_t \epsilon_t\Big)\sum_{t=0}^{T-1}(T-t) ,
$$

그리고 $\epsilon_t$ 를 평균 $\epsilon$ 으로 바꾸는 느슨한 형태를 쓰면
$\sum_t (T-t) = T(T+1)/2$ 에서 (1)이 나온다. $\epsilon_t$ 가 균일하다는 가정 없이 쓰려면
$\sum_t \epsilon_t (T-t) \le T\sum_t \epsilon_t = \epsilon T^2$ 로 묶으면 된다 — 이것이 (1)의
형태다.

**$T^2$ 의 해석.** 두 인자가 곱해진다: 실수를 **적어도 한 번** 할 확률이 $O(\epsilon T)$,
그 뒤에 쌓이는 비용이 $O(T)$. 둘 중 어느 하나라도 없애면 선형이 된다 — DAgger 는 전자를
줄이지 않고 **후자**를 줄인다(복구를 배우므로).

**가정이 깨지는 곳.** 1단계는 **짝지음**이 가능해야 한다 — 전이가 결정론이 아니어도 같은 난수를
쓰면 되지만, 두 정책이 확률적이면 "같은 행동"의 확률을 다시 세어야 하고 $\epsilon$ 의 정의가
전변동 거리로 바뀐다. 2단계의 $(T-t)$ 는 **복구 불가능**을 전제한 최악 가정이다. 복구가
$O(1)$ 스텝에 가능한 과제에서는 실제 비용이 $O(\epsilon T)$ 에 가까워지고, 그래서 "BC 가
$T^2$ 이다"는 **과제 구조에 대한 진술**이기도 하다(문제 P5).

### R2 — 하한 구성

$T^2$ 이 증명의 느슨함이 아님을 보이려면 그 차수를 **달성하는** 예가 필요하다.

**구성.** 상태는 $\{g, b\}$ ("궤도 위", "이탈"). 행동은 $\{\texttt{stay}, \texttt{fix}\}$.
전이는 결정론이다: $g$ 에서 $\texttt{stay}$ 는 $g$ 로, $\texttt{fix}$ 는 $b$ 로 간다.
$b$ 에서는 **두 행동 모두** $b$ 로 간다(흡수). 비용은 $c(g,\cdot) = 0$, $c(b,\cdot) = 1$.
전문가는 $\pi^\star(g) = \texttt{stay}$ 이고, $b$ 는 전문가 분포에 **나타나지 않는다**.

학습자 $\hat{\pi}$ 를 "$g$ 에서 확률 $\epsilon$ 으로 $\texttt{fix}$, 나머지는 $\texttt{stay}$"로
둔다. 전문가 분포는 $g$ 에만 질량이 있으므로 지도 오차는 정확히 $\epsilon$ 이다.

**비용 계산.** 처음 $\texttt{fix}$ 를 고르는 시점을 $\tau$ 라 하면 $\Pr[\tau = t] =
\epsilon(1-\epsilon)^{t}$ 이고 그 뒤 모든 스텝의 비용이 1 이므로

$$
J(\hat{\pi}) = \sum_{t=0}^{T-1}\epsilon(1-\epsilon)^{t}\,(T-1-t)
  \;=\; \frac{(1-\epsilon)\big(1 - (1-\epsilon)^{T}\big)}{\epsilon} - (1-\epsilon)^{T}\,\cdot 0 \;-\; \dots
$$

닫힌 형태를 쓰는 대신 $\epsilon T \ll 1$ 에서 $(1-\epsilon)^t \approx 1$ 로 전개하면

$$
J(\hat{\pi}) \;\approx\; \epsilon \sum_{t=0}^{T-1}(T-1-t) = \epsilon\,\frac{T(T-1)}{2}
  \;=\; \Omega(\epsilon T^2), \tag{5}
$$

그리고 $J(\pi^\star) = 0$ 이다. 따라서 (1)의 차수는 타이트하다. **흡수 상태가 결정적이다** —
$b$ 에서 복구가 가능하면 이 구성은 무너진다.

### R3 — DAgger

**알고리즘.** $i = 1,\dots,N$ 에서 ⓐ 현재 정책 $\pi_i$ 로 궤적을 모으고 ⓑ 그 궤적의 상태에
**전문가 라벨**을 붙여 데이터셋에 **누적**하고 ⓒ 누적 데이터로 $\pi_{i+1}$ 을 학습한다.
핵심은 ⓑ 의 상태가 $d_{\pi_i}$ 에서 온다는 것이다.

**1단계: 손실을 분포와 함께 정의한다.** $i$ 번째 반복의 손실을
$\ell_i(\pi) = \mathbb{E}_{s \sim d_{\pi_i}}\big[\mathbf{1}\{\pi(s)\neq\pi^\star(s)\}\big]$ 로 둔다.
DAgger 는 이 손실열에 대한 **온라인 학습**이고, 누적 데이터로 학습하는 것이 Follow-the-Leader 다.

**2단계: no-regret 성질을 쓴다.** 손실열이 볼록(또는 유한 가설 집합에서 랜덤화)일 때
no-regret 알고리즘은

$$
\frac{1}{N}\sum_{i=1}^{N}\ell_i(\pi_i) \;\le\; \underbrace{\min_\pi \frac1N\sum_{i=1}^N \ell_i(\pi)}_{=\;\epsilon_N}
  \;+\; \underbrace{\frac{\gamma_N}{N}}_{\to\,0} , \tag{6}
$$

즉 **자기 분포에서의 평균 오차**가 최선의 고정 정책의 오차 $\epsilon_N$ 에 수렴한다. BC 에서는
이 양을 **전문가 분포**에서만 통제했다는 것이 유일한 차이다.

**3단계: 성능 차 보조정리로 비용으로 옮긴다.** `c8-policy-gradient` 의 R3 을 유한 지평 비용
형태로 쓰면

$$
J(\pi) - J(\pi^\star) = \sum_{t=0}^{T-1}
  \mathbb{E}_{s\sim d^t_{\pi}}\Big[ Q^{\pi^\star}_{T-t}\big(s,\pi(s)\big) - V^{\pi^\star}_{T-t}(s)\Big].
$$

괄호 안은 $\pi$ 가 $\pi^\star$ 와 같은 행동을 고르면 0 이고, 다르면 최대 $u$ 다. 따라서

$$
J(\pi_i) - J(\pi^\star) \;\le\; u\,T\,\ell_i(\pi_i) .
$$

(6)으로 평균을 취하면 적어도 하나의 $i$ 에 대해 $\ell_i(\pi_i) \le \epsilon_N + \gamma_N/N$
이고, 그 $\pi_i$ 가 (2)를 만족한다.

**$T$ 가 한 번만 나오는 이유.** 분포가 $d_{\pi_i}$ 이므로 "이탈 상태에서의 오차"가 이미
$\ell_i$ 에 들어가 있다. BC 의 2단계처럼 "이탈 이후는 모른다"고 포기할 필요가 없으므로
$(T-t)$ 를 곱하는 단계가 사라지고, $u$ (한 번의 실수가 만드는 비용-대-목표 격차)가 그 자리를
대신한다. **$u$ 가 $T$ 규모일 수밖에 없는 과제**(복구 불가능)에서는 DAgger 도 $T^2$ 로 돌아간다.

**가정이 깨지는 곳.** (6)은 손실열이 no-regret 학습 가능해야 한다 — 가설 집합이 유한하거나
손실이 볼록해야 하고, 심층망에서는 보장이 없다. 또 전문가에게 **임의 상태에서 질의**할 수
있어야 한다. 실제 로봇에서 사람 전문가를 이탈 상태에 데려다 놓고 "지금 뭘 할 건가"를 묻는 것은
비용이 크고 라벨 품질도 떨어진다 — DAgger 의 실무 장벽은 이론이 아니라 이 질의 모형이다.

### R4 — 보상 모호성

**ⓐ 스케일.** $r' = \alpha r$ ($\alpha > 0$)이면 모든 정책의 가치가 $\alpha$ 배가 되어 순서가
보존되므로 최적 정책이 같다. 따라서 보상의 **크기**는 관측으로 결정되지 않는다.

**ⓑ 퍼텐셜 성형.** 임의의 $\Phi:\mathcal{S}\to\mathbb{R}$ 에 대해
$r'(s,a,s') = r(s,a,s') + \gamma\Phi(s') - \Phi(s)$ 로 두면, 임의의 궤적에서

$$
\sum_{t}\gamma^t\big(\gamma\Phi(s_{t+1}) - \Phi(s_t)\big) = -\Phi(s_0)
$$

(망원 전개)이므로 모든 정책의 가치가 **같은 상수** $-\Phi(s_0)$ 만큼 이동한다. 상수 이동은
순서를 바꾸지 않으므로 최적 정책 집합이 보존된다.

ⓐ·ⓑ 가 만드는 자유도는 $\Phi$ 의 차원($=\lvert\mathcal{S}\rvert$)만큼이다. 즉 **최적 정책을
완벽히 관측해도 보상은 $\lvert\mathcal{S}\rvert+1$ 차원 다양체 안에서만 결정된다.** IRL 은
이 다양체에서 하나를 고르는 **추가 원칙**을 반드시 도입한다 — 최대 마진(Abbeel & Ng 2004),
최대 엔트로피(Ziebart 2008)가 그 원칙이다.

**가정이 깨지는 곳.** ⓑ 는 $\Phi$ 가 상태만의 함수여야 한다. $\Phi$ 가 행동에 의존하면 망원이
깨지고 최적 정책이 바뀐다 — 성형 보상을 설계할 때 가장 흔한 버그다.

### R5 — 최대 엔트로피 해

**문제.** 궤적 분포 $p$ 에 대해

$$
\max_p \; H(p) = -\sum_\tau p(\tau)\log p(\tau)
  \quad\text{s.t.}\quad \sum_\tau p(\tau) f(\tau) = \tilde{f},\;\; \sum_\tau p(\tau) = 1 ,
$$

여기서 $\tilde{f}$ 는 전문가 데이터의 경험적 특징 기대값이다.

**Lagrange 쌍대.** 승수 $\theta \in \mathbb{R}^m$ (특징 제약)과 $\lambda$ (정규화)를 도입하면

$$
\mathcal{L} = -\sum_\tau p\log p + \theta^\top\Big(\tilde{f} - \sum_\tau p f(\tau)\Big)
  + \lambda\Big(1 - \sum_\tau p\Big).
$$

$\partial\mathcal{L}/\partial p(\tau) = -\log p(\tau) - 1 - \theta^\top f(\tau) - \lambda = 0$ 에서

$$
p(\tau) = \exp\!\big(-1-\lambda\big)\exp\!\big(-\theta^\top f(\tau)\big),
$$

$\lambda$ 를 정규화로 흡수하고 $\theta \to -\theta$ 로 부호를 맞추면 (3)이다. 엔트로피가
강볼록이고 제약이 선형이므로 해는 **유일**하다.

**$\theta$ 를 정하는 문제.** 쌍대 함수는 $g(\theta) = \log Z(\theta) - \theta^\top\tilde{f}$ 이고
$\nabla g = \mathbb{E}_{p_\theta}[f] - \tilde{f}$, $\nabla^2 g = \mathrm{Cov}_{p_\theta}(f) \succeq 0$
이므로 **볼록 최소화**다. 경사가 0 인 지점이 특징 기대값 일치이고, 이것이 R5 의 경사 식이다.
난점은 $Z(\theta)$ 와 $\mathbb{E}_{p_\theta}[f]$ 가 **모든 궤적에 대한 합**이라는 것이다 —
결정론 유한 MDP 에서는 동적 계획법으로 정확히 계산되지만(Ziebart 2008 의 backward pass),
확률적·연속 문제에서는 근사(샘플링, soft 가치 반복)가 필요하다. 그 soft 가치 반복이
`c8-control-as-inference` 의 출발점이다.

**가정이 깨지는 곳.** 특징이 선형이라는 전제($r_\theta = \theta^\top\phi$)가 핵심이다. 특징이
표현하지 못하는 보상은 애초에 후보에 없고, 그래서 "IRL 이 찾은 보상"은 **특징 설계에 의해
결정**된다. 또 (3)은 전문가가 **최적**이 아니라 **볼츠만 합리적**(suboptimality 가 지수적으로
벌점)이라고 가정한다 — 전문가가 실제로 최적이면 MaxEnt 해는 전문가보다 더 확률적이다.

## 증명 스케치

### R1·R2 — 상한과 하한 [D3]

**가설** H1: $c \in [0,1]$. H2: 유한 지평 $T$, 비할인. H3: 전이가 결정론(또는 같은 난수로
짝지음 가능). H4: $\epsilon = \mathbb{E}_{d_{\pi^\star}}[\mathbf{1}\{\hat\pi\neq\pi^\star\}]$.
**결론** C1: (1). C2: 그 차수를 달성하는 MDP 가 존재한다.

**전략**: 상한은 **짝지음 + 첫 불일치 시점으로의 분해**. 하한은 **흡수 상태를 가진 2상태 MDP**.

1. $A_t$ 아래에서 $\hat{\pi}$ 의 상태 분포가 $d^t_{\pi^\star}$ 와 같음을 보인다 → (4).
   쓰는 것: H3(짝지음).
2. 불일치 이후 비용을 $(T-t)$ 로 묶는다. 쓰는 것: H1.
3. 배타적 사건으로 합산 → C1. 쓰는 것: H4.
4. 하한: $b$ 를 흡수로 만들어 2단계의 최악 가정을 **실현**시킨다 → C2.

**가설 하나를 지우면**: H1 의 비용 유계성을 지우면 2단계가 무의미하다. H3 의 짝지음을 지우면
1단계의 "같은 분포"가 깨지고, 확률적 정책에서는 $\epsilon$ 을 전변동으로 재야 한다. 4단계에서
흡수성을 지우면(복구 가능) 하한이 무너지고 $T^2$ 은 **상한일 뿐**이 된다 — 문제 P5 가 이
지점이다.

### R3 — DAgger 의 선형 후회 [D3]

**가설** H1–H2 (위와 동일). H5: 임의 상태에서 전문가 질의가 가능하다. H6: 손실열
$\{\ell_i\}$ 에 대해 no-regret 알고리즘을 쓴다($\gamma_N/N \to 0$). H7:
$u = \max(Q^{\pi^\star}-V^{\pi^\star})$ 가 유한하다.
**결론** C: (2).

**전략**: 성능 차 보조정리로 비용을 **자기 분포에서의 분류 오차**로 바꾼 뒤 no-regret 으로 묶는다.

1. 유한 지평 성능 차 보조정리를 쓴다. 쓰는 것: H2.
2. 괄호 안을 $u\cdot\mathbf{1}\{\pi\neq\pi^\star\}$ 로 묶어 $J(\pi_i)-J(\pi^\star) \le uT\ell_i(\pi_i)$.
   쓰는 것: H7.
3. (6)으로 $\frac1N\sum_i \ell_i(\pi_i) \le \epsilon_N + \gamma_N/N$. 쓰는 것: H5·H6.
4. 평균 이하인 $i$ 가 존재하므로 그 $\pi_i$ 가 C 를 만족한다.

**가설 하나를 지우면**: H7 에서 $u$ 가 $T$ 규모면 (2)가 $uT\epsilon_N = O(T^2\epsilon_N)$ 가 되어
BC 와 같은 차수로 **퇴화**한다. 즉 DAgger 의 이득은 "복구가 싸다"는 과제 성질에 의존한다.
H5 를 지우면 알고리즘 자체가 실행 불가능하다 — 오프라인 데이터만 있으면 DAgger 를 쓸 수 없고,
그 경우가 `c8-offline-rl` 이다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** (1)을 $\epsilon_t$ 가 균일하지 않은 경우에 대해 다시 유도하고, 상한을
가장 나쁘게 만드는 $\{\epsilon_t\}$ 배치를 찾으라(평균 $\epsilon$ 고정).
*해답 스케치*: $\sum_t \epsilon_t(T-t)$ 를 $\sum_t \epsilon_t = \epsilon T$ 제약 아래 최대화하는
문제다. 가중 $(T-t)$ 가 $t=0$ 에서 최대이므로 **모든 오차를 초기 시점에 몰아넣는** 배치가
최악이고 값은 $\epsilon T\cdot T = \epsilon T^2$ 다. 반대로 끝에 몰면 $O(\epsilon T)$ 로 떨어진다 —
"초기 상태에서의 오차가 치명적"이라는 실무 직관의 정확한 형태다.

**P2 (증명, ★★★, R3)** (2)의 유도에서 $u$ 의 역할을 정확히 하라: $u$ 의 정의를 쓰고,
$u \le 1$ 인 과제와 $u = \Theta(T)$ 인 과제의 예를 각각 만들고, 후자에서 DAgger 의 한계가
BC 와 같은 차수가 됨을 보여라.
*전략과 핵심 부등식*: $u = \max_{s,a}(Q^{\pi^\star}_{T-t}(s,a) - V^{\pi^\star}_{T-t}(s))$ 는
"한 번의 실수가 만드는 최대 추가 비용"이다. $u\le1$ 의 예는 1스텝 복구가 되는 추종 과제,
$u=\Theta(T)$ 의 예는 R2 의 흡수 상태 구성. 전개는 숨긴다.

**P3 (계산, ★, R1·R2)** $\epsilon = 10^{-3}$, $T = 200$ 에서 (1)의 상한과 (5)의 하한 구성의
실제 비용을 각각 구하라. 둘의 비는?
*정답*: 상한 $\epsilon T^2 = 40$, 더 조인 형태 $\tfrac12\epsilon T(T+1) = 20.1$.
하한 구성의 **정확한** 비용은 $\sum_{t<T}\epsilon(1-\epsilon)^t(T-1-t) = 18.6488$
(허용오차 $10^{-3}$). $\epsilon(1-\epsilon)^t$ 의 감쇠를 무시한 근사 $\epsilon T(T-1)/2 = 19.9$
보다 약간 작다. 비는 $40/18.6488 = 2.145$ — **상한의 상수만 2배 남짓 느슨하고 차수는 정확하다.**
검산: $T$ 를 2배로 늘려 두 값이 모두 약 4배가 되는지 확인한다($\epsilon T \ll 1$ 인 동안).

**P4 (구현, ★★, R1·R3)** 재현 과제의 환경에서 BC 와 DAgger 를 **같은 전문가 질의 예산**으로
학습시키고, 후회를 $T$ 에 대해 로그-로그로 회귀해 기울기를 구하라.
*루브릭*: ⓐ 두 방법의 질의 예산(라벨 수)이 같다 ⓑ DAgger 가 학습자 자신의 궤적에서 상태를
**균등 표집**한다(궤적 앞부분만 쓰면 이탈 상태를 못 본다 — 가장 흔한 구현 버그) ⓒ 기울기가
BC $\approx 2$, DAgger $\approx 1$ ⓓ 지평 범위가 $\epsilon T \ll 1$ 안에 있다 ⓔ 시드 수와
표준오차를 함께 보고했다.

**P5 (반례, ★★, R1·R2)** "BC 의 오차는 항상 $T^2$ 로 커진다"는 주장이 틀림을 보이라: 복구가
$O(1)$ 스텝에 가능한 MDP 에서 같은 $\epsilon$ 의 BC 가 $O(\epsilon T)$ 만 잃는 예를 만들라.
그리고 그 경우에도 DAgger 가 여전히 유리한 이유(또는 유리하지 않은 이유)를 쓰라.
*성질 체크리스트*: ⓐ 이탈 상태에서 **학습자가 이미 아는 행동**으로 복구되는 구조여야 한다
(예: 행동이 하나뿐인 상태) ⓑ 그 경우 $u = O(1)$ 이므로 R3 의 상한도 $O(\epsilon T)$ 다
ⓒ 따라서 두 방법의 차수가 같아지고 상수에서만 차이가 난다 ⓓ 결론: $T^2$ 은 BC 의 성질이
아니라 **BC × 복구 불가능성**의 성질이다.

**P6 (논문, ★★, R1·R3·R5)** Ross & Bagnell 2010(§2–3), Ross et al. 2011(§3–4),
Ziebart et al. 2008(§3–4)을 읽고 각각 3문장 이내로 쓰라: (i) 2010 논문의 하한 구성이 이 레슨의
R2 와 다른 점, (ii) 2011 논문이 no-regret 을 쓰는 자리와 그것이 없으면 깨지는 단계,
(iii) MaxEnt IRL 의 backward pass 가 (3)의 어느 양을 계산하는가.
*채점 루브릭*: (i) 비용 구조(흡수 vs 확률적 복구)와 $\epsilon$ 의 정의 차이를 짚으면 통과.
(ii) 손실열이 비정상(non-stationary)이라 고정 분포 가정이 불가능하다는 점. (iii) $Z(\theta)$
와 $\mathbb{E}_{p_\theta}[f]$ (분할함수와 특징 기대값)를 짚으면 통과. "성능이 좋다"만 쓰면 미달.

**P7 (유도, ★★, R4·R5)** 퍼텐셜 성형이 최적 정책을 보존함을 망원 전개로 보이고, 그 자유도가
MaxEnt IRL 에서 어떻게 **제거되는지** 설명하라. $\Phi$ 가 행동에 의존하면 어디서 깨지는가?
*해답 스케치*: 망원은 $\sum_t\gamma^t(\gamma\Phi(s_{t+1})-\Phi(s_t)) = -\Phi(s_0)$. MaxEnt 는
$r_\theta = \theta^\top\phi$ 로 **함수 형태를 제한**하므로 성형 항이 특징 생성 공간 안에 있을
때만 자유도가 남는다. $\Phi(s,a)$ 는 $\gamma\Phi(s_{t+1},a_{t+1})$ 에 다음 행동이 들어가
망원이 닫히지 않고, 정책에 의존하는 항이 남아 최적 정책이 바뀐다.

## 논문 읽기

**필독 3편.** 각 논문에 고정 질문 10개로 1페이지 노트를 쓴다(`lesson-standard.md` §5).
3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Ross & Bagnell, "Efficient reductions for imitation learning" (2010, AISTATS)** — 역할:
   `원전(seminal)`. <https://proceedings.mlr.press/v9/ross10a.html> — §2–3 만 읽는다.
   읽는 이유: R1 의 $O(\epsilon T^2)$ 상한과 R2 의 하한이 이 논문이다.
   추가 질문: ⓐ 저자들의 forward training 알고리즘은 왜 $O(\epsilon T)$ 를 얻는데도 실무에서
   쓰이지 않는가(비정상 정책의 비용)? ⓑ $\epsilon$ 을 0-1 손실이 아니라 대리 손실로 재면
   상한이 어떻게 바뀌는가?
2. **Ross, Gordon & Bagnell, "A reduction of imitation learning and structured prediction to
   no-regret online learning" (2011, AISTATS)** — 역할: `원전(seminal)`.
   <https://arxiv.org/abs/1011.0686> — §3–4 와 부록.
   읽는 이유: R3 의 (2)와 그 증명이 이 논문의 정리다.
   추가 질문: ⓐ 정리에서 $\beta_i$ (전문가와 학습자를 섞는 비율) 스케줄이 하는 일은 무엇이고
   $\beta_i = 0$ 으로 두면 무엇이 깨지는가? ⓑ 실험에서 전문가 질의 횟수를 공정하게 맞췄는가?
3. **Ziebart, Maas, Bagnell & Dey, "Maximum entropy inverse reinforcement learning" (2008, AAAI)**
   — 역할: `원전(seminal)`. <https://cdn.aaai.org/AAAI/2008/AAAI08-227.pdf> — §3–4.
   읽는 이유: R4 의 모호성을 R5 의 원칙으로 닫는 글이다.
   추가 질문: ⓐ 저자들의 backward/forward pass 가 계산하는 양을 (3)의 기호로 쓰라.
   ⓑ 전문가가 최적이라고 가정하지 않는 것이 결과를 어떻게 바꾸는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU **2분 이내**(두 실험 합쳐 순수 Python
루프 약 4천만 스텝), 메모리 100 MB 이내, numpy 만. 데이터는 필요 없다 — 환경과 전문가를 레슨이 제공한다.

**환경(드리프트 추종).** 상태는 궤도에서 벗어난 거리 $d \in \{0,\dots,5\}$, 행동은
$a \in \{-1,0,+1\}$ 로 $d$ 를 그만큼 움직인다(구간으로 clip). 매 스텝 확률 $p = 0.002$ 로
외란이 $d$ 를 $+1$ 민다. 비용은 $d > 0$ 일 때 1, 아니면 0. 전문가는
$\pi^\star(d) = -1\ (d>0)$, $0\ (d=0)$ 이다. 학습자는 룩업 테이블이고 **보지 못한 상태에서는
행동 0**(복구하지 않음)을 쓴다.

```python
import numpy as np

D_MAX, P_DRIFT = 5, 0.002


def step(d, a, rng):
    drift = 1 if rng.random() < P_DRIFT else 0
    return int(np.clip(d + a + drift, 0, D_MAX))


def expert(d):
    return -1 if d > 0 else 0
```

두 실험을 돌린다.

**실험 A (오차 모형 시뮬레이션).** 학습을 생략하고 이론의 두 오차 모형을 직접 모사한다.
BC 모형은 "$d=0$ 에서 확률 $\epsilon$ 으로 이탈, 이탈 후에는 복구하지 않음",
DAgger 모형은 "모든 상태에서 확률 $\epsilon$ 으로 틀리지만 이탈 상태에서 복구함"이다.

**실험 B (실제 학습).** 같은 전문가 질의 예산(라벨 20개, 10 반복)으로 BC 와 DAgger 를
학습시킨다. BC 는 **전문가 궤적**에서, DAgger 는 **학습자 궤적**에서 상태를 균등 표집해
라벨을 받는다.

**수용 기준** — 네 조건을 모두 만족해야 통과다.

1. **실험 A 의 차수**: $\epsilon = 10^{-3}$, $T \in \{20,40,80,160\}$ 에서 로그-로그 회귀
   기울기가 BC $\in [1.8,\,2.15]$, DAgger $\in [0.9,\,1.1]$ (측정값 $1.906$, $0.989$;
   4,000 반복).
2. **실험 A 의 상수**: 같은 구간에서 BC 비용이 $\tfrac12\epsilon T^2$ 의 $\pm15\%$ 안에,
   DAgger 비용이 $\epsilon T$ 의 $\pm15\%$ 안에 들어온다
   (측정값 BC $0.2045/0.2 = 1.02$, $12.376/12.8 = 0.97$; DAgger $0.6462/0.64 = 1.01$).
3. **실험 B 의 차수**: $T \in \{10,\dots,320\}$, 800 런에서 후회의 로그-로그 기울기가
   BC $\in [1.8,\,2.2]$, DAgger $\in [0.8,\,1.3]$ (측정값 $1.990$, $1.077$).
4. **실험 B 의 격차**: $T = 320$ 에서 BC 후회가 DAgger 후회의 **10배 이상**이다
   (측정값 $76.86$ vs $2.54$ = $30$ 배).

**비교 대상(베이스라인)**: ⓐ 전문가 자신의 비용(측정값 $T=320$ 에서 $0.64$) — 후회의 기준점.
ⓑ 실험 A 의 이론값 $\tfrac12\epsilon T^2$ 와 $\epsilon T$ — 조건 2 가 그 비교다.
ⓒ 선택: DAgger 의 표집을 "궤적 앞부분 $k$ 개"로 바꿔 돌려 **이득이 사라지는 것**을 확인한다
(측정에서 DAgger 기울기가 $1.08$ 에서 $2.22$ 로 올라가 BC 와 같아진다). 이 위생 검사가
조건 3 의 의미를 확정한다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| DAgger 기울기가 2 에 가깝다 | 학습자 궤적의 **앞부분만** 라벨링해 이탈 상태를 못 봤다 | 라벨된 상태의 히스토그램을 출력한다 — $d\ge1$ 이 하나도 없으면 이 버그다 |
| BC 기울기가 1 에 가깝다 | $\epsilon T \gtrsim 1$ 이라 비용이 $T$ 로 포화했다 | $\epsilon T$ 를 출력한다. $p=0.002$ 에서 $T\le 320$ 이어야 한다 |
| 두 방법의 후회가 음수 | 전문가 비용을 다른 난수로 측정했다 | 평가 난수 시드를 정책과 **무관하게** 고정한다(같은 외란 열) |
| 후회가 시드마다 크게 흔들린다 | 런 수가 적다. $p$ 가 작아 사건이 희귀하다 | 800 런 이상을 쓰고 표준오차를 출력한다 |
| 실험 A 의 BC 상수가 2배 크다 | $\tfrac12\epsilon T^2$ 대신 $\epsilon T^2$ 와 비교했다 | (5)의 $T(T-1)/2$ 를 쓴다 |
| DAgger 가 BC 보다 **나쁘다** | 누적(aggregate) 없이 마지막 반복 데이터만 썼다 | 데이터셋 크기가 반복마다 커지는지 확인한다 |

## 열린 문제

- **(열린 문제) 질의 가능한 전문가 없이 공변량 이동을 다루기** — DAgger 의 보장은 임의 상태에서
  전문가에게 질의할 수 있다는 H5 에 전적으로 의존한다. 실제 로봇에서 사람 전문가를 이탈
  상태에 놓고 질의하는 것은 비싸고 라벨 품질도 떨어지며, 안전하지 않을 수도 있다. 오프라인
  데이터만으로 같은 선형 차수를 얻는 방법은 알려져 있지 않다. 현재 접근: 점유도 일치로 보는
  모방학습([GAIL](https://arxiv.org/abs/1606.03476)), 보수적 오프라인 학습
  (`c8-offline-rl`). 비어 있는 자리: 질의 없이 $O(\epsilon T)$ 를 주는 가정.
- **(열린 문제) 다봉·다중 모드 전문가에서의 오차 정의** — $\epsilon$ 은 0-1 손실로 정의되지만
  사람 전문가는 같은 상태에서 여러 올바른 행동을 쓴다. 평균을 취하는 회귀 손실은 모드 사이의
  **실행 불가능한 평균**을 만든다. 현재 접근: 분포를 직접 모델링하는
  [확산 정책](https://arxiv.org/abs/2303.04137), 시간 상관을 쓰는 행동 청크
  ([ACT](https://arxiv.org/abs/2304.13705)). 비어 있는 자리: 다봉 전문가에 맞는 $\epsilon$ 과
  그에 맞는 복합 오차 한계.
- **(열린 문제) 보상 모호성을 닫는 원칙의 선택** — R4 의 자유도를 최대 엔트로피로 닫는 것은
  "전문가가 볼츠만 합리적"이라는 **경험적 가정**이다. 사람의 차선성이 그 형태가 아니면 복원된
  보상이 체계적으로 틀린다. 현재 접근:
  [MaxEnt IRL](https://cdn.aaai.org/AAAI/2008/AAAI08-227.pdf),
  [최대 마진](https://doi.org/10.1145/1015330.1015430). 비어 있는 자리: 사람 차선성의
  검증 가능한 모형.
- **(열린 문제) 모방으로 학습한 정책의 실패를 런타임에 탐지하기** — BC 의 실패는 분포 밖에서
  발생하는데, 정책 자신은 그 사실을 모른다. 분포 밖 탐지와 등각 예측을 붙이는 접근이 있으나
  제어 루프 안에서의 보장은 없다. 현재 접근:
  [Sinha et al. 2022](https://arxiv.org/abs/2212.14020),
  [등각 예측](https://arxiv.org/abs/2107.07511). 비어 있는 자리: 이탈 시점을 $O(1)$ 스텝 안에
  보증 있게 알리는 탐지기.

## 개념 점검

`rc quiz c8-imitation-learning` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c8-imitation-learning-quiz
questions:
  - id: q1
    type: single
    prompt: "BC 의 상한 (1)에서 $T^2$ 은 어떤 두 인자의 곱인가?"
    choices:
      - "상태 수 × 행동 수"
      - "적어도 한 번 실수할 확률 $O(\\epsilon T)$ × 실수 이후 남은 비용 $O(T)$"
      - "지도 오차 $\\epsilon$ × 전문가 질의 횟수 $T$"
      - "할인 인자 $1/(1-\\gamma)$ 의 제곱"
    answer: 1
    explanation: "첫 불일치 시점으로 분해하면 각 시점의 확률이 $\\epsilon_t$ 이고 그 뒤 비용이 최대 $T-t$ 다. 합이 $\\sum_t \\epsilon_t(T-t) \\le \\epsilon T^2$ 이므로 두 인자의 곱이다. 어느 하나를 없애면 선형이 되고, DAgger 는 뒤쪽 인자를 없앤다."
    concept: { front: "BC 의 $T^2$ 의 출처", back: "실수 확률 $O(\\epsilon T)$ × 복구 못 한 잔여 비용 $O(T)$ — DAgger 는 후자를 없앤다" }
  - id: q2
    type: truefalse
    prompt: "BC 의 $O(\\epsilon T^2)$ 는 증명 기법이 느슨해서 생긴 것이고, 더 조밀한 분석으로 $O(\\epsilon T)$ 로 개선할 수 있다."
    answer: false
    explanation: "R2 의 하한 구성(이탈 상태가 흡수인 2상태 MDP)이 그 차수를 **달성**한다. 따라서 $T^2$ 은 분석의 산물이 아니라 BC 라는 알고리즘(과 복구 불가능한 과제 구조)의 성질이다. 복구가 싼 과제에서는 실제 비용이 선형일 수 있지만 그것은 과제 가정이 바뀐 경우다."
    concept: { front: "$O(\\epsilon T^2)$ 의 타이트함", back: "흡수 이탈 상태를 가진 2상태 MDP 가 달성 — 알고리즘의 성질이지 분석의 느슨함이 아니다" }
  - id: q3
    type: single
    prompt: "DAgger 가 BC 보다 좋은 이유를 한 줄로 고르면?"
    choices:
      - "전문가 질의를 더 많이 하기 때문"
      - "손실을 학습자 자신의 상태 분포에서 재므로 이탈 상태의 복구 행동을 배우기 때문"
      - "정책을 확률적으로 만들어 탐색하기 때문"
      - "보상 함수를 함께 학습하기 때문"
    answer: 1
    explanation: "질의 예산은 같게 맞출 수 있다 — 차이는 **어디서** 질의하는가다. 손실 $\\ell_i$ 가 $d_{\\pi_i}$ 에서 정의되므로 학습자가 실제로 방문하는 이탈 상태가 데이터에 들어오고, (2)에서 $(T-t)$ 를 곱하는 단계가 사라진다."
    concept: { front: "DAgger 의 핵심", back: "자기 분포에서 질의 → 이탈 상태의 복구를 배운다. 질의 수가 아니라 질의 위치의 문제" }
  - id: q4
    type: truefalse
    prompt: "최적 정책을 완벽하게 관측하면 보상 함수가 유일하게 결정된다."
    answer: false
    explanation: "양의 스칼라 배 $r \\mapsto \\alpha r$ 와 퍼텐셜 성형 $r + \\gamma\\Phi(s') - \\Phi(s)$ 가 모두 최적 정책을 보존하므로, 보상은 최소 $\\lvert\\mathcal{S}\\rvert+1$ 차원의 자유도를 남긴다. IRL 은 그 다양체에서 하나를 고르는 추가 원칙(최대 마진, 최대 엔트로피)을 반드시 도입한다."
    concept: { front: "IRL 의 모호성", back: "스케일 + 퍼텐셜 성형만으로 $\\lvert\\mathcal{S}\\rvert+1$ 차원 자유도 — 추가 원칙 없이는 미결정" }
  - id: q5
    type: short
    prompt: "MaxEnt IRL 의 로그 가능도 경사는 데이터의 특징과 무엇의 차인가? (한 구)"
    answer: ["모델의 특징 기대값", "특징 기대값", "모델 기대 특징", "E_{p_theta}[f]", "모델 분포의 특징 기대값"]
    explanation: "$\\nabla_\\theta \\log p_\\theta(\\tau) = f(\\tau) - \\mathbb{E}_{p_\\theta}[f(\\tau)]$ 다. 경사가 0 인 지점이 특징 기대값 일치이고, 쌍대 함수 $\\log Z(\\theta) - \\theta^\\top\\tilde{f}$ 의 Hessian 이 $\\mathrm{Cov}_{p_\\theta}(f) \\succeq 0$ 이므로 볼록 문제다. 난점은 $\\mathbb{E}_{p_\\theta}[f]$ 의 계산이다."
    concept: { front: "MaxEnt IRL 의 경사", back: "데이터 특징 − 모델의 특징 기대값. 볼록 문제이고 난점은 분할함수 계산" }
```

## 이 단계 공부법

1. **분해를 손으로 한다 (60분)** — (4)의 "첫 불일치 시점으로 분해"를 백지에서 쓴다. 짝지음
   아래에서 상태 분포가 같아지는 한 줄이 전부다. 그 다음 $\sum_t(T-t) = T(T+1)/2$ 를 직접
   계산해 $T^2$ 이 어디서 오는지 본다.
2. **하한을 먼저 만들어 본다 (45분)** — R2 의 2상태 MDP 를 스스로 설계해 보고, 흡수성을 빼면
   왜 무너지는지 확인한다(문제 P5). 상한보다 **하한을 만들 수 있는지**가 이 주제의 이해도를
   가른다.
3. **DAgger 를 성능 차 보조정리로 다시 읽는다 (60분)** — `c8-policy-gradient` 의 R3 을 유한
   지평 형태로 옮겨 적고, $u$ 가 $(T-t)$ 를 대신하는 자리를 짚는다. $u = \Theta(T)$ 인 과제를
   하나 떠올려 두면 "DAgger 가 항상 낫다"는 오해가 사라진다.
4. **차수를 실험으로 분리한다 (120분)** — 재현 과제 실험 A(오차 모형)를 먼저 통과시킨 뒤
   실험 B(실제 학습)로 간다. 순서를 바꾸면 기울기가 2 가 아닌 이유가 이론 때문인지 구현 때문인지
   알 수 없다. 마지막으로 DAgger 의 표집을 "궤적 앞부분"으로 바꿔 **이득이 사라지는 것**을 본다.
5. **IRL 의 모호성을 유도로 닫는다 (75분)** — 퍼텐셜 성형의 망원 전개(P7)를 쓰고, 그 다음
   R5 의 Lagrange 쌍대를 직접 유도한다. 엔트로피 최대화가 **왜 지수족을 주는지**를 한 번
   유도해 두면 `c8-control-as-inference` 의 soft Bellman 이 같은 구조로 보인다.
6. **논문 3편과 열린 문제 (180분)** — Ross & Bagnell 2010(상한·하한) → Ross et al. 2011(DAgger)
   → Ziebart et al. 2008(MaxEnt). 논문당 1페이지 노트는 **반드시** 쓴다. 끝으로 "열린 문제"
   중 질의 가능한 전문가 항목을 골라, 실제 로봇에서 H5 를 어떻게 완화할지 한 문단으로 쓴다.

**통과 기준**: 백지에서 (1)을 유도하고 하한 구성을 그릴 수 있고, DAgger 의 (2)에서 $u$ 의
역할을 말할 수 있고, 퍼텐셜 성형과 MaxEnt 해를 유도할 수 있고, 재현 과제의 네 조건을 만족하는
코드와 논문 3편의 노트를 갖고 있다.
