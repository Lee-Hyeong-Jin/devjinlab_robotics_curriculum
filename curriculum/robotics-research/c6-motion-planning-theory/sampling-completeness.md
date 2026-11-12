---
id: c6-sampling-completeness
title: 샘플링 기반과 확률적 완전성
summary: >-
  PRM 과 RRT 의 확률적 완전성(probabilistic completeness)을 공 덮개 + 이항 꼬리 논증으로
  끝까지 증명한다. 해 경로의 간격 $\delta$ 가 양수이면 실패 확률이 반복 수에 대해 지수적으로
  감소한다는 결과를 명시 상수와 함께 유도하고, 그 상수가 좁은 통로에서 왜 쓸모없이 보수적인지를
  $\epsilon$-good·확장성(expansiveness) 가정으로 설명한다. 재현 과제에서 실패 확률의 지수
  감소를 직접 측정하고, 고전 한계가 실제 성공 지점보다 $10^3$ 배 이상 늦게 깨어난다는 것을 센다.
objectives:
  - 간격 $\delta$ 의 해 경로를 공 덮개로 바꾸고 한 걸음 전진 보조정리를 빠진 줄 없이 증명할 수 있다.
  - RRT 와 PRM 의 실패 확률 상한을 명시 상수(공 개수 $m$, 한 걸음 확률 $p$)와 함께 유도할 수 있다.
  - 확률적 완전성이 보장하지 않는 것(최적성, 유한 시간 종료, 실패 판정)을 각각 말할 수 있다.
  - $\epsilon$-good 과 $(\epsilon,\alpha,\beta)$-확장성의 정의를 쓰고 간격 기반 한계와의 관계를 설명할 수 있다.
  - 고전 한계가 보수적인 이유 두 가지(공 부피 논증, Voronoi 편향 무시)를 수치 실험으로 보일 수 있다.
prerequisites: [c6-combinatorial-gcs]
difficulty: 5
estimated_minutes: 480
tags: [motion-planning, sampling-based, prm, rrt, probabilistic-completeness, narrow-passage, research]
activities:
  - id: c6-sampling-completeness-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 100
  - id: c6-sampling-completeness-papers
    kind: reading
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 120
  - id: c6-sampling-completeness-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 2 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 150
  - id: c6-sampling-completeness-reproduction
    kind: exercise
    title: 재현 과제 — 좁은 통로 폭 대비 성공률과 지수 감소율 측정 (R2)
    estimated_minutes: 90
  - id: c6-sampling-completeness-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 20
resources:
  - title: "LaValle, Planning Algorithms"
    url: http://lavalle.pl/planning/
    kind: book
    note: ch.5 (샘플링 기반 동작 계획) — 5.2 샘플링 이론과 분산(dispersion), 5.4 PRM, 5.5 RRT. 전문 무료.
  - title: "Kavraki, Svestka, Latombe & Overmars — Probabilistic roadmaps for path planning in high-dimensional configuration spaces (1996)"
    url: https://doi.org/10.1109/70.508439
    kind: article
    note: 필독 1. PRM 의 원전. 로드맵 구성과 최초의 확률적 완전성 논증.
  - title: "LaValle & Kuffner — Randomized kinodynamic planning (2001)"
    url: https://doi.org/10.1177/02783640122067453
    kind: article
    note: 필독 2. RRT 의 원전(IJRR 판). Voronoi 편향과 미분 제약으로의 확장.
  - title: "Hsu, Latombe & Motwani — Path planning in expansive configuration spaces (1999)"
    url: https://doi.org/10.1142/S0218195999000285
    kind: article
    note: 필독 3. $\epsilon$-good 과 $(\epsilon,\alpha,\beta)$-확장성 — 좁은 통로를 정량화하는 유일한 틀.
  - title: "Kleinbort, Solovey, Littlefield, Bekris & Halperin — Probabilistic completeness of RRT for geometric and kinodynamic planning (2019)"
    url: https://doi.org/10.1109/LRA.2018.2888947
    kind: article
    note: 권장. RRT 완전성 증명의 빈틈을 메우고 한계를 개선한다. 이 레슨의 R1 은 이 논문의 구성을 따른다.
  - title: "Hsu, Jiang, Reif & Sun — The bridge test for sampling narrow passages with probabilistic roadmaps (2003)"
    url: https://doi.org/10.1109/ROBOT.2003.1242285
    kind: article
    note: 권장. 좁은 통로를 노리는 샘플러. 균등 샘플링의 $\delta^d$ 장벽을 우회하는 실무적 방법.
  - title: "Ladd & Kavraki — Measure theoretic analysis of probabilistic path planning (2004)"
    url: https://doi.org/10.1109/TRA.2004.824649
    kind: article
    note: 권장. 완전성 논증을 측도론으로 다시 세워 가정을 분리한다.
  - title: "Kuffner & LaValle — RRT-Connect (2000)"
    url: https://doi.org/10.1109/ROBOT.2000.844730
    kind: article
    note: 권장. 양방향 RRT. 완전성은 같고 상수가 달라지는 전형적 예.
---

# 샘플링 기반과 확률적 완전성

## 전제와 기호

`c6-cspace-complexity` 와 `c6-combinatorial-gcs` 를 전제한다. 특히 앞 레슨들의
(ⓐ) $\mathcal{C}_{free}$ 가 **열린집합**이라 자유 구성마다 양의 간격 공이 있다는 것,
(ⓑ) 조합적 완전 계획이 $d \le 3$ 의 도구라는 것이 이 레슨의 출발점이다. 추가 전제:

- 확률: 이항분포, Chernoff·Hoeffding 꼴 꼬리 한계, 유니온 바운드, 측도의 단조성.
  마팅게일은 필요하지 않다(권장 선수 `r0-estimation-theory`).
- $\mathbb{R}^d$ 의 르베그 측도. $\zeta_d$ 는 단위 공의 부피
  ($\zeta_2 = \pi$, $\zeta_3 = 4\pi/3$).

표기(모듈 표기에 추가):

| 기호 | 뜻 |
|---|---|
| $\sigma$ | 해 경로. 길이 $L = \ell(\sigma)$ |
| $\delta$ | 해 경로의 **간격(clearance)** $\min_t \operatorname{dist}(\sigma(t), \mathcal{C}_{obs}) > 0$ |
| $\eta$ | RRT 의 스텝 크기 |
| $x_0, \dots, x_m$ | $\sigma$ 위에 간격 $\eta/2$ 로 놓은 점들 |
| $B_i$ | $B(x_i, \eta/4)$ — **샘플이 떨어져야 하는 공** |
| $p$ | 한 번의 샘플이 지정된 공에 떨어질 확률 $\ge \zeta_d (\eta/4)^d / \mu(\mathcal{C}_{free})$ |
| $\mathcal{V}(q)$ | $q$ 에서 직선으로 보이는 자유 구성의 집합 |
| $\epsilon, \alpha, \beta$ | 확장성(expansiveness) 매개변수 (§R3) |
| $\gamma$ | 허용 실패 확률 |

**이 레슨이 다루는 알고리즘.** 둘 다 "무작위로 구성을 뽑아 충돌 없는 것만 이어붙인다"지만
구조가 다르다.

- **PRM** — $n$ 개를 **먼저** 뽑고, 거리 $r$ 이내인 쌍을 직선으로 이어 로드맵을 만든 뒤
  $q_s, q_g$ 를 붙여 그래프 탐색한다. 다중 질의(multi-query)용.
- **RRT** — 트리 하나를 키운다. 샘플 $s$ 를 뽑고 트리의 **최근접 노드** $u$ 에서 $s$ 쪽으로
  $\eta$ 만큼 뻗는다. 단일 질의(single-query)용. 최근접 노드를 쓰는 것이 **Voronoi 편향**이고,
  이것이 R3 의 수치 관찰 전부를 설명한다.

전제 하나를 명시한다: **(A5) 양의 간격** — 해 경로가 존재하면 **간격 $\delta > 0$ 인** 해
경로가 존재한다. 이 가정 없이는 아래 어떤 보장도 없다. 접촉을 요구하는 과제($\delta = 0$)는
이 이론의 밖이고 `c6-tamp` 와 `s2-planning-through-contact` 의 주제다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명).

- **R1 (한 걸음 전진 보조정리와 RRT 의 확률적 완전성) [D3]** — (A5) 아래 $\eta \le \delta/2$ 로
  두면, 트리에 $B_i$ 안의 노드가 있고 샘플이 $B_{i+1}$ 에 떨어지면 **새 노드는 정확히 그 샘플**
  이고 새 변은 충돌이 없다. 따라서 $m = \lceil 2L/\eta \rceil$, $p \ge \zeta_d(\eta/4)^d/\mu(\mathcal{C}_{free})$ 에 대해
  $$
  \mathbb{P}[\text{$n$ 반복 후 실패}] \;\le\; \mathbb{P}[\mathrm{Bin}(n, p) < m]
    \;\le\; \exp\!\left(-\frac{(np - m)^2}{2np}\right) \quad (m \le np). \tag{1}
  $$
  즉 실패 확률은 $n$ 에 대해 **지수적으로 감소**한다: $\mathbb{P}[\text{실패}] \le a e^{-bn}$.
- **R2 (PRM 의 확률적 완전성) [D3]** — 같은 공 덮개에서 연결 반경이 $r \ge \eta$ 이면,
  모든 $B_i$ 에 샘플이 하나 이상 있으면 로드맵이 $q_s$ 와 $q_g$ 를 잇는다. 유니온 바운드로
  $$
  \mathbb{P}[\text{$n$ 샘플 후 실패}] \;\le\; m\,(1 - p)^n \;\le\; m\, e^{-np}, \tag{2}
  $$
  따라서 $\mathbb{P}[\text{실패}] \le \gamma$ 를 위해 $n \ge \frac{1}{p}\ln\frac{m}{\gamma}$ 면 충분하다.
- **R3 (좁은 통로와 $\epsilon$-good·확장성) [D2]** — (1)(2)의 $p$ 는 $\delta^d$ 에 비례하므로
  좁은 통로($\delta \to 0$)에서 **차원 지수로** 무너진다. 이것을 간격이 아닌 **가시성**으로
  바꿔 쓴 것이 $\epsilon$-good 과 $(\epsilon, \alpha, \beta)$-확장성이고, 필요 샘플 수는
  $$
  n = O\!\left(\frac{1}{\epsilon\alpha}\log\frac{1}{\epsilon\alpha\gamma} + \frac{1}{\beta}\right)
    \tag{3}
  $$
  꼴이 된다([Hsu, Latombe & Motwani 1999](https://doi.org/10.1142/S0218195999000285)).
  두 틀 모두 **충분 조건**이고, 실측 감소율은 한계보다 훨씬 빠르다 — 재현 과제에서
  고전 한계가 실제 성공 지점보다 $6\times10^3$ 배 늦게 깨어나는 것을 센다.
- **R4 (확률적 완전성이 주지 않는 것) [D1]** — (ⓐ) **최적성**: RRT 의 해 비용은 최적값으로
  수렴하지 않는다(`c6-asymptotic-optimality` R3). (ⓑ) **유한 시간 종료**: 해가 **없을** 때
  알고리즘은 영원히 멈추지 않으며, 불가능을 선언할 수 없다(결정 문제를 풀지 못한다).
  (ⓒ) **결정론적 대안과의 분리 없음**: 분산(dispersion) $\delta/2$ 의 결정론적 격자도
  같은 조건에서 완전하고, 실제로 저차원에서는 더 빠르다
  ([Janson, Ichter & Pavone 2018](https://arxiv.org/abs/1505.00023)) —
  **무작위성 자체가 이득의 원천이 아니다.**

## 유도

### R1 — 한 걸음 전진 보조정리

증명의 전체 전략은 "해 경로를 **공의 사슬**로 바꾸고, 각 공을 한 번씩 맞히는 사건의 이항 꼬리를
센다"다. 어려운 곳은 딱 한 군데다: **최근접 노드가 내가 원하는 노드가 아닐 수 있다.** 반지름과
간격을 어떻게 잡으면 그 걱정이 사라지는지가 이 절의 핵심이다.

**구성.** $\eta \le \delta/2$ 로 두고, $\sigma$ 를 호 길이로 매개화해 점
$x_0 = q_s, x_1, \dots, x_m = q_g$ 를 **간격 $\eta/2$** 로 놓는다. 즉
$\lVert x_{i+1} - x_i \rVert \le \eta/2$ 이고 $m = \lceil L/(\eta/2) \rceil = \lceil 2L/\eta \rceil$.
공은 $B_i = B(x_i, \eta/4)$ 로 둔다.

**보조정리 (한 걸음 전진).** 트리 $T$ 가 노드 $v \in B_i$ 를 갖고 이번 반복의 샘플이
$s \in B_{i+1}$ 이면, 새 노드는 $s$ 자신이고($s$ 가 트리에 추가된다) 새 변은 충돌이 없다.

*증명.*
1. **거리 계산.** 삼각 부등식으로
   $$
   \lVert v - s \rVert \;\le\; \underbrace{\lVert v - x_i \rVert}_{\le \eta/4}
     + \underbrace{\lVert x_i - x_{i+1} \rVert}_{\le \eta/2}
     + \underbrace{\lVert x_{i+1} - s \rVert}_{\le \eta/4} \;=\; \eta. \tag{4}
   $$
   **여기서 반지름을 $\eta/4$, 간격을 $\eta/2$ 로 잡은 이유가 드러난다** — 세 항의 합이 정확히
   스텝 $\eta$ 가 되게 맞춘 것이다. 반지름을 $\eta/2$ 로 잡으면 합이 $3\eta/2$ 가 되어 아래
   2단계가 깨진다.
2. **최근접 노드도 $\eta$ 이내다.** $u$ 를 $s$ 의 최근접 트리 노드라 하면 정의상
   $\lVert u - s \rVert \le \lVert v - s \rVert \le \eta$. $u$ 가 누구인지는 **몰라도 된다** —
   거리만으로 충분하다.
3. **확장이 샘플에 도달한다.** RRT 의 확장은
   $\mathrm{new} = u + \eta\,(s-u)/\lVert s-u \rVert$ if $\lVert s-u\rVert > \eta$, else
   $\mathrm{new} = s$ 다. 2단계에서 $\lVert u-s\rVert \le \eta$ 이므로 **후자**, 즉
   $\mathrm{new} = s \in B_{i+1}$.
4. **새 변이 자유다.** $\lVert s - x_{i+1} \rVert \le \eta/4$ 이고
   $\lVert u - x_{i+1} \rVert \le \lVert u - s\rVert + \lVert s - x_{i+1}\rVert \le \eta + \eta/4
   = 5\eta/4 \le 5\delta/8 < \delta$. 간격의 정의로 $B(x_{i+1}, \delta) \subset \mathcal{C}_{free}$
   이고 공은 볼록이므로 $u$ 와 $s$ 를 잇는 선분 전체가 자유다. $\square$

**이항 꼬리.** 트리가 $B_0$ 에서 출발하므로($q_s = x_0$), 보조정리를 $i = 0, 1, \dots, m-1$ 에
차례로 적용하면 **$B_1, \dots, B_m$ 을 차례로 한 번씩 맞히는 것으로 충분**하다. 각 반복에서
"다음 공을 맞히는" 확률은 균등 샘플링에서

$$
p \;=\; \frac{\mu\big(B(x_{i+1}, \eta/4)\big)}{\mu(\mathcal{C}_{free})}
  \;\ge\; \frac{\zeta_d\,(\eta/4)^d}{\mu(\mathcal{C}_{free})} \tag{5}
$$

이다(공이 $\mathcal{C}_{free}$ 안에 완전히 들어가므로 부피를 그대로 쓸 수 있다 — 4단계와 같은
이유다). 서로 다른 반복의 샘플은 독립이고, 각 반복은 "성공"(다음 공 맞힘) 또는 "실패"이므로
$n$ 반복에서 성공 횟수는 $\mathrm{Bin}(n, p)$ 를 **확률적으로 지배한다**(stochastic
domination — 각 반복의 성공 확률이 $p$ 이상이므로). 성공이 $m$ 번 모이면 트리는 $q_g$ 에
도달하므로

$$
\mathbb{P}[\text{실패}] \le \mathbb{P}[\mathrm{Bin}(n,p) < m],
$$

그리고 Chernoff 하한꼬리 $\mathbb{P}[X < (1-\theta)np] \le e^{-\theta^2 np/2}$ 에
$\theta = 1 - m/(np)$ 를 넣으면 (1)이다. $a = e^{m/2}$, $b = p/2$ 로 두면
$\mathbb{P}[\text{실패}] \le a e^{-bn}$ 꼴이 보인다.

**가정이 깨지는 곳 세 군데** — 이 문단이 R1 의 쓸모를 결정한다.

1. **$\eta \le \delta/2$ 는 충분 조건이고 필요 조건이 아니다.** 재현 과제에서는
   $\eta = 0.02 > \delta/2 = w/4$ 인 설정에서도 RRT 가 80% 이상 성공한다. 스텝이 크면
   3단계가 "후자"로 가지 않아 보조정리가 적용되지 않을 뿐, 다른 경로로 통로를 지날 수 있다.
   **정리가 침묵하는 영역에서 알고리즘이 동작한다는 사실을 "정리가 틀렸다"로 읽지 않는다.**
2. **$p$ 의 하한이 극단적으로 느슨하다.** (5)는 Voronoi 편향을 전혀 쓰지 않는다. RRT 는 트리
   끝단의 Voronoi 영역이 크다는 성질 때문에 "통로 쪽으로 뻗는" 샘플의 유효 집합이 공보다
   훨씬 크다. 재현 과제에서 실측 $b$ 가 (5)의 $p/2$ 보다 $10^1$–$10^2$ 배 크게 나온다.
3. **$\delta$ 를 모른다.** 실무에서 $\delta$ 는 해를 알아야 알 수 있다. 그래서 (1)은
   **사후(a posteriori) 한계**이고, 반복 수를 미리 고르는 데 쓸 수 없다. 이 한계가 R3 의
   확장성 매개변수로도 해결되지 않는다는 것이 `c6-cspace-complexity` 의 첫 열린 문제였다.

### R3 — 좁은 통로: 간격에서 가시성으로

**간격 기반 한계의 한계.** (5)에서 $p \propto (\eta/4)^d \propto \delta^d$ 다. 통로 폭이 절반이
되면 $p$ 는 $2^{-d}$ 배가 되고, 같은 성공률을 위한 $n$ 은 $2^d$ 배가 된다. 7-자유도 팔에서
통로를 절반으로 좁히면 $2^7 = 128$ 배다. 이것이 "좁은 통로 문제(narrow passage problem)"의
정량적 내용이고, 간격만으로 쓴 이론이 주는 전부다.

문제는 **간격이 올바른 매개변수가 아니라는 것**이다. 두 공간이 같은 $\delta$ 를 갖고도
난이도가 전혀 다를 수 있다: ⓐ 길이 $L$ 이 짧은 통로 하나와 ⓑ 같은 폭의 통로가 100개 직렬로
있는 공간은 $\delta$ 가 같지만 $m$ 이 100배 차이다. 그래서 Hsu 등은 **가시성 측도**로 바꾼다.

**정의 ($\epsilon$-good).** $q \in \mathcal{C}_{free}$ 가 $\epsilon$-good 이란
$\mu(\mathcal{V}(q)) \ge \epsilon\,\mu(\mathcal{C}_{free})$ 인 것이다. 공간이 $\epsilon$-good
이란 모든 자유 구성이 그런 것이다. 뜻: **어느 점에서도 공간의 $\epsilon$ 비율은 직선으로
보인다.**

**정의 ($\beta$-lookout 과 확장성).** 연결된 $S \subset \mathcal{C}_{free}$ 에 대해

$$
\mathrm{LOOKOUT}_\beta(S) = \big\{\, q \in S \;:\;
  \mu\big(\mathcal{V}(q) \setminus S\big) \ge \beta\,\mu\big(\mathcal{C}_{free} \setminus S\big) \,\big\}
$$

로 두고, 공간이 $(\epsilon, \alpha, \beta)$-**확장적(expansive)** 이란 $\epsilon$-good 이고
모든 연결 $S$ 에 대해 $\mu(\mathrm{LOOKOUT}_\beta(S)) \ge \alpha\,\mu(S)$ 인 것이다.
뜻: **어떤 영역을 이미 덮었더라도, 그 영역의 $\alpha$ 비율은 "밖을 많이 볼 수 있는 자리"다.**
세 매개변수가 각각 ⓐ 로드맵 노드가 쓸모 있을 확률($\epsilon$), ⓑ 아직 못 간 쪽으로 넘어갈
발판의 비율($\alpha$), ⓒ 그 발판에서 넘어갈 확률($\beta$)을 재고, 이로부터 (3)이 나온다.

**왜 이것이 간격보다 나은가.** $\epsilon, \alpha, \beta$ 는 **차원을 명시적으로 쓰지 않는다**.
좁은 통로가 하나뿐인 공간에서 $\delta^d$ 는 지수적으로 작아지지만 $\epsilon$ 은 통로 양쪽
방이 크면 상수로 남을 수 있다. 반대로 통로가 많으면 $\alpha$ 가 작아져 난이도가 반영된다.

**가정이 깨지는 곳**: $\epsilon, \alpha, \beta$ 는 **계산할 수 없다**. 정의가
$\mathcal{C}_{free}$ 의 모든 연결 부분집합에 대한 전칭이고 가시성 측도를 요구하므로, 추정에도
공간을 이미 알아야 한다. 그래서 (3)은 "좁은 통로가 왜 어려운지"를 **설명**하지만 반복 수를
**예측**하지 못한다. 실무가 쓰는 우회는 이론이 아니라 샘플러 설계다 — 가시성 기반 PRM
([Nissoux, Siméon & Laumond 1999](https://doi.org/10.1109/iros.1999.811662)), 브리지 테스트
([Hsu et al. 2003](https://doi.org/10.1109/ROBOT.2003.1242285)), 학습된 샘플러
([Ichter, Harrison & Pavone 2018](https://arxiv.org/abs/1709.05448)). 이들은 균등 측도를
바꾸므로 (5)의 $p$ 를 다시 계산해야 하고, **완전성 증명을 다시 해야 한다** — 바꾼 분포가
해 경로 근방에 양의 밀도를 두지 않으면 완전성을 잃는다. 학습된 샘플러의 보장이 비어 있는
이유가 정확히 이것이다.

## 증명 스케치

### R2 — PRM 의 확률적 완전성

**가설** H1: (A5) — 간격 $\delta > 0$, 길이 $L$ 의 해 경로 $\sigma$ 가 있다.
H2: 샘플은 $\mathcal{C}_{free}$ 에서 독립 균등(또는 해 경로 근방에 양의 밀도를 갖는 분포).
H3: 연결 반경이 $r \ge \eta$ 이고 $\eta \le \delta/2$ 이며, 거리 $\le r$ 인 자유 쌍은
**모두** 직선으로 연결을 시도한다.
**결론** C: $\mathbb{P}[\text{실패}] \le m e^{-np}$, 특히 $n \to \infty$ 에서 0.

**전략**: 공 덮개 + **유니온 바운드**. RRT 와 달리 "순서"가 필요 없다 — 모든 공이 채워지기만
하면 된다. 그래서 증명이 더 짧고 상수가 더 좋다.

1. R1 의 구성(간격 $\eta/2$, 반지름 $\eta/4$)을 그대로 쓴다. $A_i$ = "$B_i$ 에 샘플이 하나 이상
   있다"는 사건.
2. **연결 보조정리.** $\bigcap_i A_i$ 가 일어나면, 각 $B_i$ 에서 샘플 $y_i$ 를 하나 고르면
   $$\lVert y_i - y_{i+1}\rVert \le \eta/4 + \eta/2 + \eta/4 = \eta \le r$$
   이므로 H3 로 로드맵이 변 $(y_i, y_{i+1})$ 을 시도하고, R1 4단계와 같은 논증
   ($y_i, y_{i+1} \in B(x_{i+1}, \delta)$, 공이 볼록·자유)으로 그 변은 충돌이 없다. 따라서
   $y_0 \rightsquigarrow y_m$ 이 로드맵 안에 있다. $q_s, q_g$ 는 $\lVert q_s - y_0 \rVert \le \eta/4 \le r$
   로 붙는다.
3. **유니온 바운드.** $\mathbb{P}[A_i^c] = (1 - p_i)^n \le (1-p)^n \le e^{-np}$ 이고
   $$\mathbb{P}\Big[\bigcup_i A_i^c\Big] \le \sum_{i=1}^{m} \mathbb{P}[A_i^c] \le m\,e^{-np}.$$
   사건들의 독립성은 **필요하지 않다** — 유니온 바운드가 그것을 요구하지 않는다.
4. $m e^{-np} \le \gamma \iff n \ge \frac{1}{p}\ln\frac{m}{\gamma}$. (생략: 로드맵이 연결 반경
   $r$ 안의 모든 쌍을 시도하지 않고 $k$-최근접만 쓰는 변형의 처리 —
   [Kavraki et al. 1996](https://doi.org/10.1109/70.508439) §4 와
   `c6-asymptotic-optimality` 의 $k_n = O(\log n)$ 논의로.)

**가설을 지우면**: H3 의 $r \ge \eta$ 를 빼면 2단계의 $\lVert y_i - y_{i+1}\rVert \le \eta$ 가
$r$ 을 넘어 연결이 시도되지 않고 로드맵이 끊긴다 — 이것이 실무에서 "$r$ 을 너무 작게 잡아
PRM 이 통로를 못 지나는" 현상이다. H2 의 "양의 밀도"를 빼면 (5)의 $p$ 가 0 이 될 수 있어
3단계가 무의미해진다(학습된 샘플러의 함정). H1 의 $\delta > 0$ 을 빼면 공 자체를
$\mathcal{C}_{free}$ 안에 넣을 수 없고 4단계의 볼록성 논증이 무너진다.

## 문제 세트

난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** R1 의 1단계에서 반지름 $\rho$ 와 간격 $h$ 를 **미지수로 두고**
$2\rho + h \le \eta$ 를 만족해야 3단계가 성립함을 보이라. 그 다음 $p \propto \rho^d$ 와
$m \propto L/h$ 의 교환을 고려해 (1)의 우변을 가장 작게 만드는 $(\rho, h)$ 를 구하라
($\eta$ 는 고정).
*해답 스케치*: 제약 $2\rho + h = \eta$ 아래 $np - m$ 을 최대화한다. $n$ 이 크면 $p$ 항이
지배하므로 $\rho \to \eta/2$, $h \to 0$ 이 좋아 보이지만 $m \to \infty$ 다. $np \gg m$ 이
되는 영역에서 $\rho = \eta/4$, $h = \eta/2$ 는 두 항을 같은 차수로 두는 선택이고,
최적해는 $n$ 과 $d$ 에 의존한다는 것을 보이면 된다.

**P2 (유도, ★★, R1·R2)** (1)과 (2)를 비교해 같은 $\gamma$ 에 대해 필요한 $n$ 을 각각
$p, m, \gamma$ 로 쓰고, 어느 쪽이 더 작은지 판정하라. 차이가 나는 **구조적** 이유
(순서 요구 vs 무순서)를 한 문단으로 쓰라.
*해답 스케치*: (2)는 $n \ge p^{-1}\ln(m/\gamma)$ — $m$ 에 **로그**로 의존한다. (1)은
$n \gtrsim m/p$ — $m$ 에 **선형**이다. RRT 는 공을 **순서대로** 맞혀야 하므로 $m$ 번의
성공이 필요하고, PRM 은 모든 공이 채워지기만 하면 되므로 쿠폰 수집 문제가 된다.

**P3 (계산, ★, R1·R3)** 재현 과제의 환경($d=2$, 단위 정사각형, 통로 폭 $w = 0.03$, 해 경로
길이 $L = 0.8$)에서 R1 의 명시 상수를 모두 계산하라: $\delta$, $\eta = \delta/2$, 공 반지름,
$p$ 의 하한, $m$, 그리고 (1)이 **비자명해지는 최소 반복 수** $n_{\min} = m/p$.
*정답*: $\delta = w/2 = 0.015$, $\eta = 0.0075$, 반지름 $\eta/4 = 0.001875$,
$\mu(\mathcal{C}_{free}) = 1 - w(1-w) = 0.9709$,
$$p \ge \frac{\pi (0.001875)^2}{0.9709} = 1.13757\times10^{-5},\qquad
  m = \lceil 2L/\eta \rceil = \lceil 213.33 \rceil = 214,$$
$n_{\min} = m/p = 1.8812\times10^{7}$. 허용오차: $p$ 와 $n_{\min}$ 은 상대오차 $10^{-4}$.
검산: 실측 90% 성공 지점은 $n_{90} \approx 3.06\times10^{3}$ 이므로 한계는 실제보다
$n_{\min}/n_{90} \approx 6.2\times10^{3}$ 배 늦게 깨어난다.

**P4 (증명, ★★, R1)** R1 의 이항 지배(stochastic domination) 단계를 엄밀하게 다시 쓰라.
문제: "다음 공을 맞히는" 사건의 확률이 **조건부**(트리가 이미 $B_i$ 에 도달했을 때)이고
반복마다 조건이 다르다. 적절한 여과(filtration)를 정의하고 성공 횟수가
$\mathrm{Bin}(n,p)$ 를 지배함을 보이라.
*전략*: $\mathcal{F}_k$ = 처음 $k$ 반복까지의 샘플로 생성된 $\sigma$-대수. 지표
$Z_k = \mathbb{1}[\text{$k$ 번째 반복이 전진}]$ 에 대해
$\mathbb{P}[Z_k = 1 \mid \mathcal{F}_{k-1}] \ge p$ 가 **모든** 과거에 대해 성립함을 보조정리로
확인하고, 이런 지표열의 합이 $\mathrm{Bin}(n,p)$ 를 지배한다는 표준 보조정리를 인용한다
(생략: 지배 보조정리의 증명 — 커플링으로.
[Kleinbort et al. 2019](https://doi.org/10.1109/LRA.2018.2888947) §III).

**P5 (증명, ★★★, R3)** $\mathcal{C}_{free}$ 가 간격 $\delta$ 의 해 경로를 가지면
$\epsilon$-good 인가? 참이면 $\epsilon$ 을 $\delta, d, \mu(\mathcal{C}_{free})$ 로 주고,
거짓이면 반례를 구성하라. 역방향($\epsilon$-good $\Rightarrow$ 양의 간격 해 경로)도 판정하라.
*전략*: 정방향은 $\mathcal{V}(q) \supset B(q, \operatorname{dist}(q, \mathcal{C}_{obs}))$ 를
쓰되, $q$ 가 장애물에 **임의로 가까울 수 있다**는 점을 보라 — 자유공간의 점 전체에 대한
전칭이므로 $\epsilon$ 을 양수로 잡을 수 없는 구성이 있다. 역방향은 두 방을 잇는 통로의 폭을
0 으로 보내며 $\epsilon$ 을 상수로 유지할 수 있는지 생각한다.

**P6 (구현, ★★, R1·R3)** 재현 과제의 RRT 와 두 스윕을 쓰라. 요구: 선분–직사각형 연속 충돌
판정, 최근접 이웃 완전 탐색(벡터화), 시드 고정.
*루브릭*: ⓐ 두 스윕의 측정값이 재현 과제 표와 허용오차 안에서 일치한다 ⓑ
$-\log(\text{실패율})$ 의 선형 적합 $r^2 \ge 0.98$ ⓒ $n = 125$ 가 왜 적합에서 제외되는지
설명한다(트리가 통로에 도달하는 데만 최소 $0.4/\eta = 20$ 걸음이 필요하고 성공률이 0.5% 다)
ⓓ P3 의 $n_{\min}$ 을 코드로 계산해 실측과의 비를 출력한다.

**P7 (반례, ★★, R4)** "확률적 완전성이 있으면 충분히 돌리면 해를 찾는다"는 문장이 **실무에서
무의미해지는** 구성을 만들라: $d = 10$, 통로 폭 $w$, 균등 샘플링에서 (5)의 $p$ 를 계산하고
$\gamma = 0.1$ 을 위한 $n$ 을 $w = 0.1$ 과 $w = 0.05$ 에 대해 각각 구하라. 그 다음
"해가 없는 인스턴스에서 알고리즘이 무엇을 출력하는가"에 답하라.
*성질 체크리스트*: $p \propto (w/8)^{10}$ 에서 두 값의 비가 $2^{10}$ 임을 쓰고, 두 번째
질문의 답이 **"영원히 돌린다"** 이며 확률적 완전성은 불가능 판정을 주지 않는다는 것을 쓸 것.

**P8 (논문, ★★, R1·R3)** Kleinbort et al. 2019 를 읽고 (ⓐ) 저자들이 기존 RRT 완전성 증명에서
지적한 빈틈이 정확히 무엇인지, (ⓑ) 그 빈틈이 이 레슨 R1 의 어느 단계에 해당하는지,
(ⓒ) 저자들의 개선된 한계가 (1)보다 얼마나 나은지(어느 인자에서)를 쓰라.
*루브릭*: 빈틈이 "최근접 노드의 정체"와 관련된다는 점(R1 2–3단계), 그리고 개선이 상수 인자
수준인지 지수 인자 수준인지 구별하면 통과. "증명을 고쳤다"만 쓰면 미달.

## 논문 읽기

**필독 3편.** 고정 질문 10개로 논문당 1페이지 노트를 쓴다.

1. **Kavraki, Svestka, Latombe & Overmars, "Probabilistic roadmaps for path planning in
   high-dimensional configuration spaces" (1996, IEEE T-RA)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1109/70.508439>
   *왜 읽는가*: R2 의 원형. 로드맵 구성(학습 단계 + 질의 단계)과 **확장(expansion) 단계**가
   좁은 통로를 어떻게 다루려 했는지 보라.
   추가 질문: ⓐ 저자들의 완전성 논증은 이 레슨 R2 의 어느 단계에 해당하고 무엇이 다른가?
   ⓑ "확장 단계"의 휴리스틱은 R3 의 어느 매개변수를 키우려는 시도인가?
2. **LaValle & Kuffner, "Randomized kinodynamic planning" (2001, IJRR)** — 역할:
   `원전(seminal)`. <https://doi.org/10.1177/02783640122067453>
   *왜 읽는가*: RRT 의 원전이고 **Voronoi 편향**이 설계 의도로 명시된 유일한 1차 자료다.
   미분 제약 확장은 `c6-kinodynamic-planning` 에서 다시 읽는다.
   추가 질문: ⓐ 저자들이 주장하는 완전성의 정확한 진술은 무엇이고 증명의 어느 부분이
   스케치인가? ⓑ Voronoi 편향을 정량화하는 양이 논문에 있는가(없다면 왜 없는가)?
3. **Hsu, Latombe & Motwani, "Path planning in expansive configuration spaces" (1999, IJCGA)**
   — 역할: `표준(standard)`. <https://doi.org/10.1142/S0218195999000285>
   *왜 읽는가*: (3)의 출처이고 좁은 통로를 **측도로** 정의한 유일한 틀이다.
   추가 질문: ⓐ (3)의 정확한 상수를 논문에서 찾아 옮기라(이 레슨은 $O(\cdot)$ 로만 썼다).
   ⓑ $\epsilon, \alpha, \beta$ 중 어느 것이 "좁은 통로의 개수"를, 어느 것이 "폭"을 재는가?
   ⓒ 저자들은 이 매개변수를 추정하는 방법을 제시하는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄 또는 그림 한 장으로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지
않는가** (5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가,
분산·시드를 보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, 두 스윕 합쳐 15분 이내,
메모리 1GB 이내. numpy 만. 외부 데이터 불필요.

**입력 데이터(레슨이 지정).** 작업공간 $[0,1]^2$, 점 로봇. $x = 0.5$ 에 **두께 $w$ 의 벽**을
세우고 $y = 0.5$ 에 **$w \times w$ 정사각형 통로**를 뚫는다. 즉 장애물은 두 직사각형

$$
\Big[\tfrac{1-w}{2},\, \tfrac{1+w}{2}\Big] \times \Big[0,\, \tfrac{1-w}{2}\Big],
\qquad
\Big[\tfrac{1-w}{2},\, \tfrac{1+w}{2}\Big] \times \Big[\tfrac{1+w}{2},\, 1\Big]
$$

이고 내부가 막혀 있다. $q_s = (0.1, 0.5)$, $q_g = (0.9, 0.5)$. 해 경로는 직선이고
$L = 0.8$, 간격 $\delta = w/2$ 다. 통로가 정사각형이므로 **간격이 폭과 같은 비율로 줄어든다** —
한 변수만 움직인다.

RRT 고정 설정: 스텝 $\eta = 0.02$, 목표 편향 5%, 목표 허용 반경 0.03, 시드 $0, \dots, 399$
(시행 400회). 샘플은 $[0,1]^2$ 균등.

**수용 기준 — 다섯 조건을 모두 만족해야 통과.**

1. **스윕 A (폭)** — $n = 2000$ 고정, $w$ 를 바꿔 성공률이 아래와 절대오차 0.05 이내로 일치하고
   **$w$ 에 대해 단조 증가**한다.

   | $w$ | 0.03 | 0.04 | 0.05 | 0.07 | 0.10 | 0.15 |
   |---|---|---|---|---|---|---|
   | 성공률 | 0.7975 | 0.8550 | 0.9300 | 0.9725 | 0.9975 | 1.0000 |

2. **스윕 B (반복 수)** — $w = 0.03$ 고정, $n$ 을 바꿔 성공률이 아래와 절대오차 0.05 이내로
   일치한다.

   | $n$ | 125 | 250 | 500 | 1000 | 2000 | 4000 |
   |---|---|---|---|---|---|---|
   | 성공률 | 0.0050 | 0.3000 | 0.4750 | 0.6575 | 0.7975 | 0.9450 |

3. **지수 감소(R1 검증)** — 스윕 B 에서 $n \ge 250$ 의 다섯 점에 대해
   $-\log(\text{실패율})$ 을 $n$ 에 **선형 적합**했을 때 결정계수 $r^2 \ge 0.98$ 이고
   기울기가 $b = (6.6 \pm 1.0)\times 10^{-4}$ 다(측정값 $6.554\times10^{-4}$, $r^2 = 0.9936$).
   이것이 $\mathbb{P}[\text{실패}] \le a e^{-bn}$ 꼴의 **직접 확인**이다.
4. **고전 한계와의 비교(R1 의 실패 모드 검증)** — P3 의 $n_{\min} = m/p$ 를 코드로 계산해
   $1.8812\times10^{7}$ (상대오차 $10^{-4}$)을 얻고, 3번의 적합에서
   $n_{90} = (\ln 10 - \text{절편})/b$ 를 계산해 $3.1\times10^{3}$ 수준임을 확인한 뒤,
   비 $n_{\min}/n_{90} \ge 10^{3}$ 임을 보인다(측정값 $6.2\times10^{3}$).
5. **폭 지수(R3 검증)** — 스윕 A 에서 성공률이 $(0.02, 0.99)$ 인 점들에 대해
   $-\log(\text{실패율}) \propto w^{\alpha}$ 를 로그–로그 적합하면 $\alpha = 1.0 \pm 0.3$ 이다
   (측정값 0.990). **이론의 $\delta^d = w^2$ 와 다르다** — (5)는 하한이므로 모순이 아니고,
   차이의 원인은 Voronoi 편향이다. 보고서에 이 해석을 한 문단으로 쓴다.

**비교 대상.** ⓐ 해석적 한계: P3 의 $(p, m, n_{\min})$. ⓑ 결정론적 베이스라인: 해상도
$h = w/4$ 의 격자($N = \lceil 1/h \rceil$, 즉 $w = 0.03$ 에서 $134 \times 134$)에서 4-이웃 BFS 는
**여섯 개 $w$ 전부에서 목표에 도달한다**(확인함). 충돌 검사 횟수는 $N^2 \approx 1.8\times10^4$ 로
RRT 가 쓰는 2000–4000 회와 같은 자릿수이므로 **예산이 비슷한 공정한 비교**다 — 2차원에서
샘플링이 결정론적 격자보다 낫지 않다는 것(R4(ⓒ))을 같은 환경에서 확인한다.
ⓒ 독립 구현: 목표 편향을 0% 로 바꿔 돌려 성공률이 떨어지는 방향으로만 변하는지 본다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 모든 $w$ 에서 성공률이 1.0 | 선분 충돌을 끝점만 검사해 벽을 뛰어넘는다 | $\eta$ 를 0.2 로 올려 보라 — 성공률이 1.0 이면 연속 판정이 없는 것이다 |
| $w = 0.03$ 에서도 성공률이 0.99 이상 | 벽의 두께가 $w$ 가 아니라 0 에 가깝다(직사각형 $x$ 범위를 잘못 계산) | $\mu(\mathcal{C}_{obs})$ 를 격자로 재어 $w(1-w)$ 와 비교한다 |
| $n = 125$ 에서 성공률이 0.3 이상 | 목표 허용 반경이 너무 크거나 목표 편향이 5% 보다 크다 | 트리 노드 수를 출력해 $0.8/\eta = 40$ 걸음 미만에 도달하는지 본다 |
| 선형 적합 $r^2 < 0.9$ | 포화된 점($n$ 이 커서 성공률 1.0)이나 $n = 125$ 를 적합에 넣었다 | 성공률 $(0.02, 0.995)$ 밖의 점을 제외한다 |
| 측정 기울기 $b$ 가 $10^{-5}$ 수준 | 실패율을 $1 - \text{성공률}$ 이 아니라 성공률로 썼다 | $n$ 이 커질 때 $-\log(\text{실패})$ 가 증가하는지 확인한다 |
| 시행마다 결과가 달라진다 | 시드를 고정하지 않았다(`default_rng(s)` 를 루프 밖에서 만들었다) | 같은 명령을 두 번 돌려 성공 횟수가 동일한지 본다 |

## 열린 문제

- **(열린 문제) 계산 가능한 난이도 매개변수** — $\delta$ 도 $(\epsilon,\alpha,\beta)$ 도
  **해를 알아야** 알 수 있고, 그래서 어떤 이론도 "이 문제에 몇 번 반복이 필요한가"에 답하지
  못한다. 재현 과제의 조건 4 가 이 간격의 크기를 수치로 보여 준다($6\times10^3$ 배).
  현재 접근: [Hsu, Latombe & Motwani 1999](https://doi.org/10.1142/S0218195999000285) 의
  확장성, [Kleinbort et al. 2019](https://doi.org/10.1109/LRA.2018.2888947) 의 개선된 한계,
  [Chaudhuri & Koltun 2009](https://doi.org/10.1016/j.comgeo.2008.10.005) 의 평탄화 분석
  (smoothed analysis). 비어 있는 자리: 인스턴스에서 **직접 측정 가능한** 양으로 반복 수를
  예측하는 이론.
- **(열린 문제) 학습된 샘플러의 완전성** — 샘플 분포를 바꾸면 (5)의 $p$ 가 바뀌고 완전성
  증명을 다시 해야 하는데, 신경망 샘플러는 해 경로 근방에 양의 밀도를 둔다는 보장이 없다
  (R3 의 실패 모드). 균등 분포와 혼합(mixing)하면 완전성은 복구되지만 **혼합 비율이
  성능 이득을 거의 지워 버린다** — 이 교환의 이론이 없다. 현재 접근:
  [Ichter, Harrison & Pavone 2018](https://arxiv.org/abs/1709.05448),
  [Qureshi et al. 2018](https://arxiv.org/abs/1806.05767). 비어 있는 자리: 보장을 유지하면서
  분포를 바꾸는 원칙 있는 방법.
- **(열린 문제) 무작위성이 정말 필요한가** — 결정론적 저분산(low-dispersion) 수열이 같은
  조건에서 완전하고 저차원에서 더 빠르며, 고차원에서도 분산 기반 한계가 성립한다
  ([Janson, Ichter & Pavone 2018](https://arxiv.org/abs/1505.00023)). 그런데 실무는 거의 전부
  무작위 샘플링을 쓴다. 어느 차원·어느 기하에서 무작위성이 **실제로** 이득인지 분리된 증거가
  없다. 비어 있는 자리: 결정론 대 무작위의 체계적 비교(같은 충돌 검사 예산, 같은 후처리).

## 개념 점검

`rc quiz c6-sampling-completeness` 로 푼다. 개념 점검 전용이고, 실제 과제는 문제 세트와
재현 과제다.

```quiz
activity: c6-sampling-completeness-quiz
questions:
  - id: q1
    type: single
    prompt: "R1 의 공 덮개에서 공 반지름을 $\\eta/4$, 점 간격을 $\\eta/2$ 로 잡는 이유는?"
    choices:
      - "공의 부피를 최대화하기 때문"
      - "$\\eta/4 + \\eta/2 + \\eta/4 = \\eta$ 가 되어 최근접 노드와 샘플의 거리가 스텝 이하임이 보장되기 때문"
      - "공 개수 $m$ 을 최소화하기 때문"
      - "간격 $\\delta$ 와 무관해지기 때문"
    answer: 1
    explanation: "삼각 부등식 $\\lVert v - s\\rVert \\le \\eta/4 + \\eta/2 + \\eta/4 = \\eta$ 가 핵심이다. 이것이 성립하면 최근접 노드 $u$ 도 $\\lVert u-s\\rVert \\le \\eta$ 를 만족하므로 RRT 의 확장이 샘플 자신에 도달하고, 새 노드가 다음 공 안에 들어간다. 반지름을 $\\eta/2$ 로 키우면 합이 $3\\eta/2$ 가 되어 이 논증이 깨진다."
    concept: { front: "공 덮개의 반지름·간격 선택", back: "$2\\rho + h \\le \\eta$ — 최근접 노드와 샘플의 거리가 스텝 이하가 되도록" }
  - id: q2
    type: single
    prompt: "같은 $\\gamma$ 를 달성하는 데 필요한 샘플 수가 공 개수 $m$ 에 대해 PRM 은 로그, RRT 는 선형으로 의존하는 구조적 이유는?"
    choices:
      - "PRM 이 더 많은 메모리를 쓰기 때문"
      - "RRT 는 공을 순서대로 맞혀야 해 $m$ 번의 성공이 필요하고, PRM 은 모든 공이 채워지기만 하면 되기 때문"
      - "PRM 의 연결 반경이 RRT 의 스텝보다 크기 때문"
      - "RRT 가 목표 편향을 쓰기 때문"
    answer: 1
    explanation: "RRT 의 전진 보조정리는 '트리가 $B_i$ 에 있을 때 $B_{i+1}$ 을 맞힌다'는 순차적 사건이라 성공이 $m$ 번 필요하고 $n \\gtrsim m/p$ 가 된다. PRM 은 모든 공이 비지 않기만 하면 되므로 유니온 바운드에서 $n \\ge p^{-1}\\ln(m/\\gamma)$ — 쿠폰 수집 꼴이다."
    concept: { front: "PRM 과 RRT 한계의 $m$ 의존성", back: "PRM $\\ln m$(무순서, 유니온 바운드) vs RRT $m$(순차 전진, 이항 꼬리)" }
  - id: q3
    type: multiple
    prompt: "확률적 완전성이 **보장하지 않는** 것을 모두 고르라."
    choices:
      - "찾은 해의 비용이 최적값으로 수렴한다"
      - "해가 없을 때 유한 시간에 '불가능'을 출력한다"
      - "무작위 샘플링이 결정론적 저분산 수열보다 빠르다"
      - "간격 $\\delta > 0$ 인 해가 있으면 $n \\to \\infty$ 에서 찾을 확률이 1 로 간다"
    answer: [0, 1, 2]
    explanation: "마지막 항목이 바로 확률적 완전성의 정의다. 나머지 셋은 전부 보장되지 않는다 — RRT 의 해 비용은 최적값으로 수렴하지 않고(다음 레슨), 불가능 판정은 할 수 없으며(결정 문제를 풀지 못한다), 결정론적 저분산 수열도 같은 조건에서 완전하고 저차원에서는 더 빠르다."
    concept: { front: "확률적 완전성의 범위", back: "해가 있으면 찾는다 — 최적성·종료·무작위성의 우위는 전부 별개" }
  - id: q4
    type: truefalse
    prompt: "실측한 실패 확률의 감소율이 식 (5)의 $p$ 로 계산한 한계보다 훨씬 빠르면 R1 의 정리가 틀린 것이다."
    answer: false
    explanation: "(5)는 $p$ 의 **하한**이고 (1)은 실패 확률의 **상한**이다. 실제가 더 빠른 것은 모순이 아니라 한계가 보수적이라는 뜻이다. 재현 과제에서 그 보수성은 $6\\times10^3$ 배로 측정되며, 원인은 (5)가 RRT 의 Voronoi 편향을 전혀 쓰지 않는다는 것이다."
    concept: { front: "하한 $p$ / 상한 실패확률의 방향", back: "실측이 더 빠른 것은 정상 — 한계가 보수적이라는 뜻" }
  - id: q5
    type: short
    prompt: "통로 폭이 절반이 되면 균등 샘플링의 한 걸음 확률 $p$ 는 몇 배가 되는가? ($d$ 차원)"
    answer: ["2^{-d}", "2^-d", "1/2^d", "2^{-d} 배", "1/(2^d)", "(1/2)^d"]
    explanation: "$p \\ge \\zeta_d(\\eta/4)^d/\\mu$ 이고 $\\eta \\le \\delta/2$ 이므로 $p \\propto \\delta^d$ 다. 폭이 절반이면 $2^{-d}$ 배, 같은 성공률을 위한 반복 수는 $2^d$ 배다. 7-자유도에서 128배 — 이것이 좁은 통로 문제의 정량적 내용이다."
    concept: { front: "좁은 통로 문제의 정량", back: "$p \\propto \\delta^d$ — 폭이 절반이면 반복 수는 $2^d$ 배" }
  - id: q6
    type: single
    prompt: "$\\epsilon$-good 과 $(\\epsilon,\\alpha,\\beta)$-확장성이 간격 $\\delta$ 보다 나은 점은?"
    choices:
      - "계산하기 쉽다"
      - "차원 $d$ 를 지수로 쓰지 않고, 통로의 폭과 개수를 서로 다른 매개변수로 분리한다"
      - "최적성까지 보장한다"
      - "결정론적 샘플링에도 적용된다"
    answer: 1
    explanation: "$\\epsilon$ 은 '어느 점에서도 보이는 비율', $\\alpha$ 는 '밖을 볼 수 있는 발판의 비율', $\\beta$ 는 '그 발판에서 넘어갈 확률'을 재므로 폭과 개수가 분리되고 $d$ 가 지수로 들어가지 않는다. 다만 세 매개변수 모두 **계산할 수 없다** — 정의가 모든 연결 부분집합에 대한 전칭이기 때문이다."
    concept: { front: "확장성 매개변수의 장점과 한계", back: "폭·개수를 분리하고 $d$ 를 지수로 쓰지 않는다. 그러나 계산 불가" }
```

## 이 단계 공부법

1. **알고리즘 두 개를 다섯 줄로 쓴다 (20분)** — PRM 과 RRT 의 의사코드를 각각 다섯 줄 이내로
   적고, 차이가 **최근접 노드를 쓰는지**에 있다는 것을 표시한다. 이 한 줄이 R1 과 R2 의
   증명 구조 차이(순차 vs 무순서)와 R3 의 수치 관찰을 모두 만든다.
2. **보조정리를 종이에서 닫는다 (60분)** — R1 의 1–4단계를 백지에서 다시 쓴다. 특히
   1단계의 세 항 합이 왜 정확히 $\eta$ 인지, 반지름을 $\eta/2$ 로 바꾸면 어디서 깨지는지를
   손으로 확인한다. P1 을 같이 풀면 선택이 임의가 아니라 **제약 $2\rho + h \le \eta$ 아래의
   설계**임이 보인다.
3. **상수를 숫자로 만든다 (30분)** — P3 를 푼다. $p = 1.14\times10^{-5}$, $m = 214$,
   $n_{\min} = 1.9\times10^{7}$ 를 직접 계산하고, 이 숫자가 실측 $3\times10^{3}$ 과 비교해
   얼마나 큰지 본다. **이론을 숫자로 바꿔 보기 전에는 "보수적"이라는 말의 크기를 모른다.**
4. **두 스윕을 돌린다 (90분)** — 재현 과제. 스윕 B(반복 수)를 먼저 해서 지수 감소를
   눈으로 확인하고, 스윕 A(폭)에서 지수 $\alpha \approx 1$ 이 나오는 것을 본 뒤 조건 5 의
   해석 문단을 직접 쓴다. 이 문단이 이 레슨에서 가장 중요한 산출물이다.
5. **논문 3편 (120분)** — 1996(PRM) → 2001(RRT) → 1999(확장성) 순서가 아니라
   **1996 → 1999 → 2001** 로 읽는다. 로드맵과 그 한계(좁은 통로)를 먼저 보고, 그 다음에
   RRT 가 Voronoi 편향으로 같은 문제를 다르게 공격하는 것을 보는 흐름이다. 권장 자료의
   Kleinbort 2019 는 P8 을 쓸 때 본다.
6. **문제 세트 (150분)** — P3·P6 먼저, P1·P2 다음, P4·P5·P7·P8 은 남는 시간에.
   P5(간격과 $\epsilon$-good 의 관계)가 가장 어렵고 가장 많이 남는다.

**통과 기준**: R1 의 네 단계를 백지에서 재구성할 수 있고, (1)과 (2)의 $m$ 의존성 차이를
설명할 수 있고, 재현 과제의 다섯 조건을 만족하는 코드와 조건 5 의 해석 문단을 갖고 있고,
"확률적 완전성이 보장하지 않는 것" 세 가지를 말할 수 있다. 논문 3편의 노트가 있다.
