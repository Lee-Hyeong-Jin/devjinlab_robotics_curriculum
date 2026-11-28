---
id: s5-graph-consensus
title: 그래프 이론과 합의
summary: >-
  다중 로봇 조율의 바탕인 합의(consensus) 동역학을 그래프 라플라시안의 스펙트럼으로 분석한다.
  연속시간 합의의 수렴률이 정확히 대수적 연결성 λ₂ 임을 증명하고, 이산시간 합의의 최적 보폭과
  그때의 수렴률을 닫힌 형태로 유도한다. 방향 그래프에서 합의값이 평균이 아니라 좌 영벡터의
  가중 평균임을, 시변 그래프에서는 매 순간의 연결성이 아니라 결합 연결성만이 문제임을 보이고,
  λ₂ = 0 인 그래프만 번갈아 써도 합의에 도달하는 것을 수치로 확인한다.
objectives:
  - 라플라시안의 스펙트럼으로 연속시간 합의의 수렴과 수렴률 λ₂ 를 증명할 수 있다.
  - 이산시간 합의의 수렴 조건과 최적 보폭 2/(λ₂+λₙ) 및 그 수렴률을 유도할 수 있다.
  - 방향 그래프의 합의값을 좌 영벡터로 쓰고 평균 합의가 균형 그래프와 동등함을 보일 수 있다.
  - 시변 그래프에서 결합 연결성이 필요충분에 가까운 조건인 이유를 설명할 수 있다.
  - Fiedler 벡터로 그래프의 병목을 찾고 간선 추가의 효과를 정량화할 수 있다.
  - 합의 수렴률을 수치로 측정해 λ₂ 와 1e-5 이내로 일치시킬 수 있다.
prerequisites: [f0-linear-algebra, c5-factor-graphs-map]
difficulty: 4
estimated_minutes: 600
tags: [multi-robot, consensus, graph-laplacian, algebraic-connectivity, distributed, research]
activities:
  - id: s5-graph-consensus-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: s5-graph-consensus-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: s5-graph-consensus-problems
    kind: exercise
    title: 문제 세트 (증명 2 · 유도 1 · 계산 2 · 구현 1 · 반례 1)
    estimated_minutes: 180
  - id: s5-graph-consensus-reproduction
    kind: reproduction
    title: 재현 과제 — 수렴률 = λ₂, 최적 보폭, 방향·시변 그래프 (R1)
    estimated_minutes: 165
  - id: s5-graph-consensus-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Mesbahi & Egerstedt, Graph Theoretic Methods in Multiagent Networks (2010)"
    url: https://doi.org/10.1515/9781400835355
    kind: book
    note: ch.2-3 (그래프와 라플라시안), ch.3.3 (합의). 이 레슨의 1순위 교재.
  - title: "Boyd & Vandenberghe, Convex Optimization"
    url: https://web.stanford.edu/~boyd/cvxbook/
    kind: book
    note: ch.2-4. λ₂ 최대화가 왜 볼록 문제가 되는지(문제 P6)의 배경. 전문 PDF 무료.
papers:
  - id: olfati-saber2007-consensus
    required: true
    role: survey
    note: "§II-III"
  - id: jadbabaie2003-coordination
    required: true
    role: seminal
    note: "§III"
  - id: fiedler1973-algebraic-connectivity
    required: true
    role: seminal
    note: "§2-3"
---

# 그래프 이론과 합의

## 전제와 기호

이 레슨은 S5 모듈의 첫 레슨이다. 전제:

- 선형대수: 대칭 행렬의 스펙트럼 분해, 양반정부호성, Rayleigh 몫, 행렬 지수
  (`f0-linear-algebra`).
- `c5-factor-graphs-map` 의 정보행렬 관점. **라플라시안은 상대 측정만 있는 추정 문제의
  정보행렬이다** — 그 레슨의 게이지 자유도(영공간 = 전역 상수)가 여기서는 "합의값이 하나로
  정해지지 않는다"로 나타난다. 두 레슨은 같은 행렬을 다른 쪽에서 보고 있다.
- 그래프 이론은 요구하지 않는다 — 필요한 정의를 아래에 모아 둔다.

| 기호 | 뜻 |
|---|---|
| $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ | 노드 $n = \lvert\mathcal{V}\rvert$ 개의 그래프. 노드 = 로봇, 간선 = 통신 링크 |
| $A$ | 인접행렬. 무향이면 $A = A^\top$. **방향 그래프에서는 $A_{ij} = 1$ 이 "$i$ 가 $j$ 를 듣는다"($j\to i$)** |
| $D$ | 차수 행렬 $\mathrm{diag}(A\mathbf{1})$. 방향 그래프에서는 **in-degree** |
| $L := D - A$ | **라플라시안**. 무향이면 대칭 양반정부호 |
| $0 = \lambda_1 \le \lambda_2 \le \cdots \le \lambda_n$ | $L$ 의 고윳값(무향). $\lambda_2$ 가 **대수적 연결성(algebraic connectivity)** |
| $f$ | $\lambda_2$ 의 고유벡터 = **Fiedler 벡터** |
| $\mathbf{1}$ | 전부 1 인 벡터. $L\mathbf{1} = 0$ 이 항상 성립한다 |
| $\delta := x - \bar x\mathbf{1}$ | **불일치(disagreement)** 벡터. $\bar x = \frac1n\mathbf{1}^\top x$ |
| $P := I - \epsilon L$ | 이산시간 합의의 **Perron 행렬**. $\epsilon$ 은 보폭 |
| $w$ | 방향 그래프에서 $w^\top L = 0$, $w^\top\mathbf{1} = 1$, $w \ge 0$ 인 **좌 영벡터** |

**합의 동역학.** 각 로봇이 이웃과의 차이를 보고 자기 값을 고치는 가장 단순한 규칙이

$$
\dot x_i = \sum_{j \in \mathcal{N}_i} a_{ij}\,(x_j - x_i)
\qquad\Longleftrightarrow\qquad
\dot x = -L\,x \tag{1}
$$

이고, 이산시간판이 $x_{k+1} = (I - \epsilon L)x_k = P x_k$ 다. (1)은 **분산(distributed)**
알고리즘이다 — 각 노드는 자기 이웃만 보고, 전역 정보를 쓰지 않는다. 이 레슨의 질문은 하나다:
**언제, 어디로, 얼마나 빨리 수렴하는가.**

## 시작 전 자가 진단

이 모듈의 첫 레슨이므로 준비 상태를 먼저 점검한다. **선수 레슨은 잠겨 있지 않다** — 아래를 전부
풀 수 있으면 권장 선수(`f0-linear-algebra`, C5·C6·C8 모듈)를 건너뛰고 바로 시작해도 된다.
**두 문항 이상 막히면** 괄호 안의 선수 레슨으로 돌아가는 편이 빠르다.

1. 경로 그래프 $1 - 2 - 3$ 의 라플라시안을 쓰고 고윳값을 구하라. (`f0-linear-algebra`)
   **정답**: $L = \begin{bmatrix}1&-1&0\\-1&2&-1\\0&-1&1\end{bmatrix}$, 고윳값 $\{0, 1, 3\}$.
   허용오차 $10^{-9}$.
2. 대칭 행렬 $M$ 에 대해 $\min_{v \perp \mathbf{1},\, v\ne0} \dfrac{v^\top Mv}{v^\top v}$ 가
   무엇인가($M\mathbf{1} = 0$ 일 때)? (`f0-linear-algebra`)
   **정답**: $\mathbf{1}$ 을 제외한 가장 작은 고윳값, 즉 $\lambda_2$ (Courant-Fischer / Rayleigh 몫).
3. $\dot x = Mx$ 의 해를 행렬 지수로 쓰고, $M$ 이 대칭일 때 $\lVert x(t)\rVert$ 의 감소율을
   고윳값으로 표현하라. (`f0-differential-equations`, `f0-linear-algebra`)
   **정답**: $x(t) = e^{Mt}x(0)$. $M$ 이 대칭이고 고윳값이 $\mu_i$ 면
   $\lVert x(t)\rVert \le e^{\mu_{\max}t}\lVert x(0)\rVert$ 이고, 성분별로는 $e^{\mu_i t}$ 다.
4. `c5-factor-graphs-map` 에서 상대 측정만 있는 포즈 그래프의 정보행렬 $\Lambda$ 의 영공간은
   무엇이었나? 1차원 스칼라 변수라면? (`c5-factor-graphs-map`)
   **정답**: 전역 강체 변환. 1차원 스칼라에서는 전역 상수 이동, 즉 $\ker\Lambda = \mathrm{span}(\mathbf{1})$
   — 바로 $\ker L$ 이다.
5. 행렬 $P$ 의 모든 행이 음이 아니고 합이 1 일 때 $P\mathbf{1} = ?$ 이고, 그런 행렬의
   스펙트럼 반경은? (`f0-linear-algebra`)
   **정답**: $P\mathbf{1} = \mathbf{1}$ (고윳값 1). 행 확률행렬의 스펙트럼 반경은 1 이고
   $\lvert\lambda\rvert \le 1$ 이 모든 고윳값에 대해 성립한다(Gershgorin 또는 노름 논증).

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`f0-how-to-read-this-track` 레슨의 "유도 깊이 등급" 절).

- **R1 (연속시간 합의: 수렴·합의값·수렴률) [D3]** — 무향 연결 그래프에서 (1)의 해는
  $$
  x(t) \longrightarrow \bar x(0)\,\mathbf{1}, \qquad
  \lVert \delta(t)\rVert \le e^{-\lambda_2 t}\,\lVert \delta(0)\rVert, \tag{2}
  $$
  이고 이 지수는 **정확히 최선**이다(Fiedler 벡터 방향에서 등식). 즉 **합의의 수렴률은
  $\lambda_2$ 다.** 평균 $\bar x$ 는 모든 $t$ 에서 보존된다. 재현 과제의 실측: 네 그래프에서
  점근 수렴률이 $\lambda_2$ 와 상대오차 $10^{-6}\!\sim\!10^{-5}$ 로 일치한다.
- **R2 (이산시간 합의: 수렴 조건과 최적 보폭) [D2]** — $P = I - \epsilon L$ 에 대해
  $$
  \text{수렴} \iff 0 < \epsilon < \frac{2}{\lambda_n}, \qquad
  \text{수렴률} = \max\big(\lvert1-\epsilon\lambda_2\rvert,\ \lvert1-\epsilon\lambda_n\rvert\big), \tag{3}
  $$
  이고 이를 최소화하는 보폭과 그때의 수렴률은
  $$
  \epsilon^\ast = \frac{2}{\lambda_2 + \lambda_n}, \qquad
  r^\ast = \frac{\lambda_n - \lambda_2}{\lambda_n + \lambda_2} = \frac{\kappa - 1}{\kappa + 1},
  \quad \kappa := \frac{\lambda_n}{\lambda_2}. \tag{4}
  $$
  **수렴률을 지배하는 것은 $\lambda_2$ 가 아니라 비율 $\kappa$ 다** — 연속시간과 다른 점이고,
  차수가 큰 노드 하나가 $\lambda_n$ 을 키워 전체를 느리게 만든다. 재현 과제의 실측:
  격자 탐색 최적값이 (4)와 6자리 이상 일치.
- **R3 (방향 그래프: 합의값은 평균이 아니다) [D2]** — 방향 그래프에서 $L$ 은 비대칭이고
  $L\mathbf{1} = 0$ 은 여전하지만 $\mathbf{1}^\top L = 0$ 은 일반적으로 거짓이다. 뿌리 있는
  신장 외향 트리(rooted out-branching)가 있으면 (1)은 수렴하고
  $$
  x(t) \longrightarrow (w^\top x(0))\,\mathbf{1}, \qquad w^\top L = 0,\ w \ge 0,\ w^\top\mathbf{1} = 1 \tag{5}
  $$
  이다. **평균 합의 $\iff$ 그래프가 균형(balanced, in-degree = out-degree) $\iff$
  $\mathbf{1}^\top L = 0 \iff w = \mathbf{1}/n$.** 재현 과제의 실측: 방향 사이클에 현 하나를
  더하면 $w = (\tfrac27,\tfrac17,\tfrac17,\tfrac17,\tfrac27)$ 이 되어 합의값이 $6/7$ 로,
  평균 $0.9$ 와 다르다.
- **R4 (시변 그래프: 결합 연결성만이 문제다) [D2]** — 매 순간의 그래프가 연결일 필요가 없다.
  유계 구간마다 그래프들의 **합집합**이 연결이면(jointly connected) 합의에 도달한다
  (`jadbabaie2003-coordination`). 재현 과제의 실측이 극적이다: $\lambda_2 = 0$ 인(즉 각각
  연결이 **아닌**) 두 그래프를 번갈아 쓰기만 해도 불일치가 $2.2\times10^{-16}$ 까지 줄어든다.
  **순간 $\lambda_2$ 는 시변 그래프에서 아무것도 말해 주지 않는다.**
- **R5 (Fiedler 벡터는 병목을 가리킨다) [D1]** — $f$ 의 부호는 그래프를 둘로 나누고
  ($\lambda_2$ 를 Rayleigh 몫으로 최소화하는 분할), 절댓값이 작은 노드가 경계에 있다.
  $\lambda_2$ 를 최대화하는 간선 추가는 조합 문제지만, $f$ 의 양극단을 잇는 탐욕 선택이
  실무적 휴리스틱이다. 재현 과제의 실측(아령 그래프 $n=10$): $\lambda_2$ 가 $0.29844$ 에서
  최선의 간선 하나로 $0.62772$ (2.10배)가 되고, Fiedler 탐욕 선택이 그 최적과 **일치**한다
  (단, 보장은 아니다).

## 유도

### R1 — 수렴률이 $\lambda_2$ 인 이유

무향 그래프이므로 $L = L^\top$ 이고 스펙트럼 분해 $L = \sum_{i=1}^n \lambda_i u_iu_i^\top$ 를 쓸 수
있다($\{u_i\}$ 정규직교). 세 가지 사실부터 고정한다.

**(a) $L \succeq 0$ 이고 $L\mathbf{1} = 0$.** 임의의 $v$ 에 대해

$$
v^\top L v = \sum_{\{i,j\}\in\mathcal{E}} a_{ij}\,(v_i - v_j)^2 \;\ge\; 0, \tag{6}
$$

이 항등식은 $L = D - A$ 를 직접 전개하면 나온다($\sum_i d_i v_i^2 - \sum_{i,j}a_{ij}v_iv_j$ 를
간선별로 모으면 (6)이다). 그리고 $v = \mathbf{1}$ 에서 (6)이 0 이므로 $\lambda_1 = 0$,
$u_1 = \mathbf{1}/\sqrt n$.

**(b) 연결 $\iff \lambda_2 > 0$.** (6)이 0 이면 모든 간선에서 $v_i = v_j$ 이므로 $v$ 는 각
연결성분 위에서 상수다. 따라서 $\dim\ker L$ = 연결성분의 수이고, 연결 $\iff$ $\ker L$ 이
1차원 $\iff \lambda_2 > 0$. (여기가 `c5-factor-graphs-map` R3 의 게이지 논증과 **같은
문장**이다 — 영공간의 차원이 "따로 떨어진 덩어리의 수"다.)

**(c) 평균 보존.** (1)의 양변에 $\mathbf{1}^\top$ 을 곱하면 $\mathbf{1}^\top L = (L\mathbf{1})^\top = 0$
(대칭!)이므로 $\frac{d}{dt}\mathbf{1}^\top x = 0$. 즉 $\bar x(t) = \bar x(0)$ 가 **모든 $t$ 에서**
성립한다. 대칭성을 쓴 지점을 기억하라 — R3 에서 이 줄이 깨진다.

**수렴률.** 불일치 $\delta = x - \bar x\mathbf{1} = (I - \frac1n\mathbf{1}\mathbf{1}^\top)x$ 는
$\mathbf{1}$ 에 직교하고, $L\mathbf{1} = 0$ 이므로

$$
\dot\delta = \dot x - \underbrace{\dot{\bar x}}_{=0}\mathbf{1} = -Lx = -L(\delta + \bar x\mathbf{1}) = -L\delta. \tag{7}
$$

$\delta$ 가 같은 선형계를 따르면서 $\mathbf{1}^\perp$ 에 머문다. 그 부분공간에서 $L$ 의 고윳값은
$\lambda_2, \dots, \lambda_n$ 이므로 $\delta(0) = \sum_{i\ge2}c_iu_i$ 에 대해

$$
\delta(t) = \sum_{i\ge2} c_i e^{-\lambda_i t}u_i,
\qquad
\lVert\delta(t)\rVert^2 = \sum_{i\ge2}c_i^2 e^{-2\lambda_i t} \le e^{-2\lambda_2 t}\lVert\delta(0)\rVert^2, \tag{8}
$$

즉 (2)다. **등식이 언제 성립하는가**: $\delta(0) = c_2u_2$ (Fiedler 벡터 방향)이면 (8)이
등식이다. 따라서 $\lambda_2$ 는 **상계가 아니라 최악의 경우 정확한 지수**이고, 일반적인
$\delta(0)$ 에서도 $t\to\infty$ 의 점근 감소율은 $\lambda_2$ 다($c_2 \ne 0$ 인 한).

**가정이 깨지는 곳**: (c)의 평균 보존과 (8)의 직교 분해는 **$L$ 의 대칭성**에 전적으로 의존한다.
방향 그래프에서는 $\mathbf{1}^\top L \ne 0$ 이라 (c)가 무너지고(R3), 고유벡터가 직교하지 않아
(8)의 성분별 감쇠 논증도 그대로 쓸 수 없다. 또 (2)는 **고정된** 그래프에 대한 진술이다 —
시변 그래프에서는 매 순간 $\lambda_2$ 가 0 이어도 수렴할 수 있다(R4). 그리고 수렴률이
$\lambda_2$ 라는 말은 **단위가 시간$^{-1}$** 이라는 뜻이다: 가중치 $a_{ij}$ 를 두 배로 하면
$\lambda_2$ 도 두 배가 되므로 "빠르다"는 통신·제어 대역폭을 고정한 뒤에만 비교 가능하다.

### R2 — 이산시간의 최적 보폭

$P = I - \epsilon L$ 은 $L$ 과 고유벡터를 공유하고 고윳값이 $1 - \epsilon\lambda_i$ 다.
$\mathbf{1}$ 방향은 고윳값 1 로 보존되고, 불일치는 $\mathbf{1}^\perp$ 에서

$$
\lVert\delta_{k}\rVert \le r(\epsilon)^k\lVert\delta_0\rVert,
\qquad r(\epsilon) := \max_{2\le i\le n}\lvert 1 - \epsilon\lambda_i\rvert \tag{9}
$$

로 줄어든다. $\lambda_i$ 가 $[\lambda_2, \lambda_n]$ 에 있고 $g(\lambda) = \lvert1-\epsilon\lambda\rvert$
가 $\lambda$ 에 대해 (고정 $\epsilon>0$ 에서) 꺾인 선형함수이므로 최대는 **구간의 양 끝에서만**
난다:

$$
r(\epsilon) = \max\big(\lvert1-\epsilon\lambda_2\rvert,\ \lvert1-\epsilon\lambda_n\rvert\big). \tag{3 재확인}
$$

$r < 1$ 이려면 양쪽이 1 보다 작아야 하므로 $0 < \epsilon\lambda_i < 2$ 가 모든 $i\ge2$ 에서
필요하고, 가장 센 제약이 $i = n$ 이라 $0 < \epsilon < 2/\lambda_n$ 이다.

**최소화.** $\epsilon$ 이 작으면 $\lvert1-\epsilon\lambda_2\rvert = 1-\epsilon\lambda_2$ 가 감소하고
$\lvert1-\epsilon\lambda_n\rvert$ 은 $\epsilon = 1/\lambda_n$ 을 지나며 증가로 바뀐다. 전자는
감소, 후자는 (충분히 큰 $\epsilon$ 에서) 증가하므로 최소는 **두 값이 같아지는 곳**이다:

$$
1 - \epsilon\lambda_2 = \epsilon\lambda_n - 1
\quad\Longrightarrow\quad
\epsilon^\ast = \frac{2}{\lambda_2+\lambda_n},
\quad
r^\ast = 1 - \epsilon^\ast\lambda_2 = \frac{\lambda_n-\lambda_2}{\lambda_n+\lambda_2}, \tag{10}
$$

즉 (4)다. 조건수 $\kappa = \lambda_n/\lambda_2$ 로 쓰면 $r^\ast = (\kappa-1)/(\kappa+1)$ 이고,
수렴에 필요한 반복 수는 $\log(1/\varepsilon)/\log(1/r^\ast) \approx \tfrac{\kappa}{2}\log(1/\varepsilon)$
규모다. **연속시간은 $\lambda_2$ 만 보지만 이산시간은 $\kappa$ 를 본다** — 이 차이가 실무에서
중요하다. 별 모양 그래프처럼 허브가 하나인 구조는 $\lambda_n \approx n$ 이라 $\kappa$ 가 커지고,
그래서 이산 합의가 느리다.

**가정이 깨지는 곳**: (10)은 $\lambda_2$ 와 $\lambda_n$ 을 **안다고** 전제한다. 둘은 전역량이라
분산 환경에서 공짜로 얻을 수 없다 — 실무에서는 $\epsilon < 1/\max_i d_i$ 같은 **국소** 상계를
쓰고(Gershgorin 에서 $\lambda_n \le 2\max_i d_i$) 최적성을 포기한다. 또 (9)는 보폭이 **모든
노드에서 같다**고 가정한다. 노드마다 다른 $\epsilon_i$ 를 쓰면 $P$ 가 비대칭이 되어 R3 의
상황으로 넘어간다 — 가중치를 각자 고르는 것만으로 평균 합의가 깨진다.

### R3 — 방향 그래프에서 합의값이 옮겨가는 이유

방향 그래프에서 $L = D_{\mathrm{in}} - A$ 이고 행 합이 0 이므로 $L\mathbf{1} = 0$ 은 여전하다.
그러나 **열** 합은 0 이 아니다. R1 의 (c)를 다시 보면

$$
\frac{d}{dt}\big(\mathbf{1}^\top x\big) = -\mathbf{1}^\top L x \ne 0 \quad \text{(일반적으로)} \tag{11}
$$

이라 평균이 보존되지 않는다. 그러면 무엇이 보존되는가? $w^\top L = 0$ 인 좌 영벡터를 잡으면

$$
\frac{d}{dt}\big(w^\top x\big) = -w^\top L x = 0 \tag{12}
$$

이므로 **$w$ 로 가중한 평균이 불변량**이다. 수렴하면 극한이 상수 벡터 $c\mathbf{1}$ 이고
(12)에서 $c = w^\top x(0)$ (단 $w^\top\mathbf{1} = 1$ 로 정규화)이므로 (5)가 나온다. $w$ 의
존재·비음성은 Perron-Frobenius 로 보장된다(뿌리 있는 신장 외향 트리가 있으면 $\ker L^\top$ 이
1차원이고 비음 벡터를 갖는다).

**균형 조건.** $w = \mathbf{1}/n$ $\iff$ $\mathbf{1}^\top L = 0$ $\iff$ 모든 노드에서
in-degree = out-degree $\iff$ 그래프가 **균형(balanced)** 이다. 셋의 동등성은 정의를 직접
비교하면 나온다: $(\mathbf{1}^\top L)_j = \sum_i L_{ij} = d_{\mathrm{in}}(j)\cdot[\,\cdot\,] - \sum_i A_{ij}
= d_{\mathrm{in}}(j) - d_{\mathrm{out}}(j)$.

**수치.** 방향 사이클 $0\to1\to2\to3\to4\to0$ 에 현 $0\to3$ 을 더하면 노드 0 의 out-degree 가
2 로 늘어 균형이 깨진다. 실측: $\lVert\mathbf{1}^\top L\rVert_\infty = 1$,
$w = (\tfrac27, \tfrac17, \tfrac17, \tfrac17, \tfrac27)$ 이고
$x(0) = (1, 2, -3, 4, 0.5)$ 에서 합의값이

$$
w^\top x(0) = \frac{2 + 2 - 3 + 4 + 1}{7} = \frac{6}{7} = 0.857142857\ldots
$$

로, 평균 $0.9$ 와 다르다. 현을 빼서 순수 방향 사이클로 만들면 균형이 되고 합의값이 정확히
$0.9$ 가 된다.

**가정이 깨지는 곳**: $w$ 는 **그래프 구조에만** 의존하고 초기값과 무관하다. 그래서 방향
그래프에서는 "누가 더 많이 듣히는가"가 합의값을 좌우한다 — in-degree 가 낮고 out-degree 가
높은 노드(많이 말하고 적게 듣는 노드)가 큰 $w_i$ 를 받는다. 다중 로봇 시스템에서 통신
비대칭(송신 출력 차이, 지형에 따른 단방향 링크)이 그대로 **추정 편향**이 되는 경로가 이것이다.
그리고 뿌리 있는 신장 외향 트리가 없으면 수렴 자체가 깨진다 — 강연결성은 필요하지 않지만
"모두에게 도달하는 하나의 뿌리"는 필요하다.

### R4 — 시변 그래프에서 순간 연결성은 필요하지 않다

이산시간으로 본다. $x_{k+1} = P_k x_k$, $P_k = I - \epsilon L_k$ 이고 $\{P_k\}$ 는 모두 행
확률행렬(비음·행합 1)이 되도록 $\epsilon$ 을 잡는다($\epsilon \le 1/\max_i d_i$). 그러면

$$
x_k = P_{k-1}\cdots P_1P_0\,x_0 \tag{13}
$$

이고 질문은 **확률행렬의 곱이 랭크 1 로 수축하는가**다. 각 $P_k$ 가 자기 그래프에서 연결이면
각각이 수축이지만, 연결이 아니면 $P_k$ 는 블록 대각이고 **그 자체로는 아무것도 섞지 않는다.**
핵심 관찰은 곱이 섞는다는 것이다: $P_0$ 가 $\{0,1\}$ 과 $\{2,3\}$ 을 각각 섞고 $P_1$ 이
$\{1,2\}$ 를 섞으면, $P_1P_0$ 는 0 의 정보를 3 까지 옮긴다.

`jadbabaie2003-coordination` 의 정리는 이것을 정확히 한다: 어떤 유한 구간 $[k, k+T)$ 마다
$\bigcup_{s=k}^{k+T-1}\mathcal{G}_s$ 가 연결이면(결합 연결성), (13)의 곱이 랭크 1 로 수렴하고
합의에 도달한다. 증명은 구간마다 곱의 **Dobrushin 계수**(또는 ergodicity 계수)가 $1-\gamma$
이하로 떨어짐을 보이고 그것을 거듭제곱한다. **[D2]**

**실측이 요점이다.** $n=6$ 에서 $\mathcal{G}_0 = \{(0,1),(2,3),(4,5)\}$,
$\mathcal{G}_1 = \{(1,2),(3,4)\}$ 를 번갈아 쓰면 **둘 다 $\lambda_2 = 0$**(연결이 아니다)인데
합집합이 경로 $0{-}1{-}2{-}3{-}4{-}5$ 로 연결이므로 합의에 도달한다 — 재현 과제에서 4000
스텝 뒤 불일치가 $2.2\times10^{-16}$ 이다. 반면 $\{(0,1),(2,3)\}$ 과 $\{(1,2)\}$ 만 쓰면
노드 4, 5 가 합집합에서도 고립되어 불일치가 $2.5$ 에 머문다. **매 순간의 $\lambda_2$ 로
시변 합의의 수렴률을 예측하려는 시도는 무의미하다.**

**가정이 깨지는 곳**: 결합 연결성은 **충분**조건이고, 정리는 수렴률을 $T$ 와 $\gamma$ 로만
느슨하게 준다 — 고정 그래프의 $\lambda_2$ 처럼 정확한 지수를 주지 않는다. 또 각 $P_k$ 가 확률
행렬이어야 하므로 $\epsilon$ 상계가 필요하고, 그래프가 적대적으로 선택되면(각 구간의 합집합이
연결이지만 매번 다른 쪽을 끊으면) 수렴이 임의로 느려질 수 있다.

### R5 — Fiedler 벡터와 간선 추가

$\lambda_2$ 는 Courant-Fischer 로

$$
\lambda_2 = \min_{v\perp\mathbf{1},\,v\ne0}\frac{v^\top Lv}{v^\top v}
  = \min_{v\perp\mathbf{1},\,v\ne0}\frac{\sum_{\{i,j\}\in\mathcal{E}}a_{ij}(v_i-v_j)^2}{\sum_i v_i^2} \tag{14}
$$

이고 최소를 주는 $v$ 가 Fiedler 벡터 $f$ 다. (14)의 분자는 "$f$ 가 간선을 가로질러 얼마나
변하는가"이므로, $\lambda_2$ 가 작다는 것은 **적은 간선만 끊으면 둘로 갈라지는 분할이
있다**는 뜻이다(Cheeger 부등식의 직관). $f$ 의 부호가 그 분할을 주고, $\lvert f_i\rvert$ 가 작은
노드가 경계에 앉는다.

**간선 하나의 효과.** 간선 $\{i,j\}$ 를 더하면 $L \to L + (e_i-e_j)(e_i-e_j)^\top$ 이므로
1차 섭동으로

$$
\Delta\lambda_2 \approx (f_i - f_j)^2 \tag{15}
$$

이다(비퇴화 $\lambda_2$ 에서 고윳값 섭동 공식). 따라서 **$f$ 의 양극단을 잇는 것이 1차에서
최선**이고, 이것이 실무 휴리스틱이다. 실측(아령 그래프, 5-클리크 둘을 간선 하나로 이은 $n=10$):
$\lambda_2 = 0.29844$, Fiedler 벡터가 $\pm0.3336$ 로 5:5 로 갈리고 다리 양끝 노드만
$\pm0.2341$ 이다. 간선 하나를 더해 얻을 수 있는 최선은 $\lambda_2 = 0.62772$ (2.10배)이고,
Fiedler 탐욕 선택이 **그 최적을 맞춘다**. 무작위 간선은 평균 $0.59834$ 다. **[D1]**

**가정이 깨지는 곳**: (15)는 1차이고 $\lambda_2$ 가 단순(비중복) 고윳값일 때만 쓸 수 있다.
$\lambda_2$ 가 중복이면(대칭성이 높은 그래프에서 흔하다) 섭동이 미분가능하지 않고 탐욕 선택이
최적이 아니다. 아령 그래프에서 일치한 것은 **보장이 아니라 그 인스턴스의 대칭성** 덕이다.
한편 $\lambda_2$ 를 최대화하는 문제 자체는 간선 가중치에 대해서는 **볼록**(SDP 로 쓸 수 있다)
이지만 간선 집합에 대해서는 조합 문제다(문제 P6).

## 증명 스케치

### R1 — 합의의 수렴과 그 지수

**가설** H1: $\mathcal{G}$ 가 무향이고 가중치 $a_{ij} = a_{ji} > 0$ 이다. H2: $\mathcal{G}$ 가
연결이다. H3: 동역학이 (1)이다.
**결론** C1: $x(t) \to \bar x(0)\mathbf{1}$. C2: $\lVert\delta(t)\rVert \le e^{-\lambda_2 t}\lVert\delta(0)\rVert$
이고 이 지수는 개선 불가능하다.

**전략**: 대칭 행렬의 스펙트럼 분해 하나로 끝난다. 리아푸노프 함수를 따로 만들 필요가 없다 —
$V = \tfrac12\lVert\delta\rVert^2$ 가 그 역할을 하지만 수렴률까지 주려면 분해가 필요하다.

1. **$\ker L = \mathrm{span}(\mathbf{1})$.** H1 으로 (6)이 성립하고, H2 로 (6)이 0 인 $v$ 는
   상수뿐이다. 따라서 $\lambda_1 = 0$ 은 단순 고윳값이고 $\lambda_2 > 0$.
2. **불변 부분공간.** H1(대칭)으로 $\mathbf{1}^\top L = 0$ 이므로 $\bar x$ 가 보존되고, $\delta$ 가
   $\mathbf{1}^\perp$ 에 머물며 같은 방정식 (7)을 따른다. $L$ 이 $\mathbf{1}^\perp$ 를 불변으로
   두는 것은 대칭성의 결과다.
3. **감쇠.** $\mathbf{1}^\perp$ 에서 $L$ 의 고윳값이 $\lambda_2,\dots,\lambda_n > 0$ 이므로 (8)이
   성립하고 $\delta \to 0$. C1·C2 의 상계.
4. **최선성.** $\delta(0) = u_2$ 로 두면 (8)이 등식이다. 따라서 지수를 $\lambda_2$ 보다 크게
   잡은 상계는 거짓이다. C2 의 "개선 불가능".
5. **리아푸노프 해석(참고).** $V = \tfrac12\delta^\top\delta$ 에 대해
   $\dot V = -\delta^\top L\delta \le -\lambda_2\,\delta^\top\delta = -2\lambda_2 V$ 이고
   Grönwall 로 같은 결론을 얻는다. 이 길은 **방향 그래프로도 확장되지 않는다** —
   $\delta^\top L\delta$ 가 $\tfrac12\delta^\top(L+L^\top)\delta$ 로 바뀌어 $L+L^\top$ 의
   양정부호성이 따로 필요해진다(문제 P2).

**가설을 지우면**: H2 를 빼면 $\lambda_2 = 0$ 이고 $\ker L$ 이 연결성분 수만큼 커진다 — 각
성분이 **자기 평균으로** 따로 수렴하고 전역 합의는 없다(재현 과제의 반례 설정). H1 의 대칭성을
빼면 2단계가 무너진다(R3). 가중치의 양수성을 빼면 (6)이 부호를 잃고 $L$ 이 양반정부호가
아니라 발산할 수 있다 — 음의 가중치(적대적 이웃)를 넣은 합의가 불안정해지는 것이 이 때문이다.

(생략: Grönwall 부등식과 Courant-Fischer 의 증명. Mesbahi & Egerstedt ch.2-3 과
`fiedler1973-algebraic-connectivity`.)

### R3' — $w$ 의 존재와 비음성

**가설** H1: $\mathcal{G}$ 가 방향 그래프이고 뿌리 있는 신장 외향 트리를 갖는다.
H2: $L = D_{\mathrm{in}} - A$.
**결론** C1: $\ker L^\top$ 이 1차원이고 비음 벡터 $w$ 로 생성된다. C2: $w^\top x$ 가 (1)의
불변량이고 $x \to (w^\top x(0))\mathbf{1}$.

**전략**: Perron-Frobenius 를 쓸 수 있게 $L$ 을 확률행렬로 바꾼다.

1. **확률행렬로.** $\epsilon \le 1/\max_i d_{\mathrm{in}}(i)$ 로 $P = I - \epsilon L$ 을 만들면
   $P \ge 0$, $P\mathbf{1} = \mathbf{1}$ 이다(행 확률행렬).
2. **Perron-Frobenius.** H1 의 외향 트리는 $P$ 에 대응하는 그래프가 "모든 노드에 도달하는
   뿌리"를 가짐을 뜻한다. 그런 비음 확률행렬의 고윳값 1 은 **단순**하고, 좌 고유벡터
   $w^\top P = w^\top$ 를 비음으로 고를 수 있다(원시성까지 있으면 양수).
3. **$L$ 로 되돌리기.** $w^\top P = w^\top \iff w^\top(I - \epsilon L) = w^\top \iff w^\top L = 0$.
   $\epsilon > 0$ 이므로 두 조건이 동등하다. C1.
4. **불변량과 극한.** (12)로 $w^\top x$ 가 불변이고, 2단계의 단순성으로 $P^k \to \mathbf{1}w^\top$
   이므로 $x_k \to (w^\top x_0)\mathbf{1}$. 연속시간은 $e^{-Lt} \to \mathbf{1}w^\top$ 로 같다. C2.
5. **균형 $\iff$ 평균.** $w = \mathbf{1}/n$ $\iff \mathbf{1}^\top L = 0$ $\iff$
   $d_{\mathrm{in}} = d_{\mathrm{out}}$ 가 모든 노드에서. 세 조건의 동등성은 R3 의 성분 계산 한 줄이다.

**가설을 지우면**: H1 의 외향 트리가 없으면 도달 불가능한 노드 집합이 둘 이상 생겨
$\ker L^\top$ 이 1차원보다 커지고, 극한이 초기값에 의존하는 여러 합의값으로 쪼개진다.
강연결성은 **필요하지 않다** — 뿌리 하나면 충분하다는 것이 이 가설의 요점이고, 다중 로봇에서
"리더 하나가 모두에게 도달하면 된다"가 여기서 나온다.

(생략: Perron-Frobenius 정리와 $P^k$ 의 수렴. Mesbahi & Egerstedt ch.3 과
`olfati-saber2007-consensus` §II.)

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (증명, ★★, R1)** (6)의 항등식 $v^\top Lv = \sum_{\{i,j\}}a_{ij}(v_i-v_j)^2$ 를 빠진 줄 없이
전개하고, 그로부터 ⓐ $L\succeq0$, ⓑ $\dim\ker L$ = 연결성분 수, ⓒ 연결 $\iff\lambda_2>0$ 를
차례로 보여라. ⓓ 간선 가중치를 모두 $c$ 배 하면 $\lambda_2$ 가 어떻게 되는가, 그리고 그것이
"수렴이 빨라졌다"는 주장에 어떤 조건을 붙이는가?
*전략 + 핵심 부등식*: ⓐⓑ 는 (6)에서 바로 나온다. ⓒ 는 ⓑ 의 특수경우다. ⓓ 는 $\lambda_2 \to c\lambda_2$
이므로 수렴률이 $c$ 배가 되지만, 통신 주기나 제어 대역폭을 고정하지 않으면 무의미한 비교라는
점을 써야 통과 — **단위를 묻는 문제다.** 전개는 숨긴다.

**P2 (증명, ★★★, R1·R3)** 방향 그래프에서 R1 의 리아푸노프 논증(증명 스케치 5단계)이 어디서
깨지는지 정확히 쓰고, ⓐ $L + L^\top \succeq 0$ 이면 $\lVert\delta\rVert$ 가 단조 감소함을
보이고, ⓑ 그 조건이 균형성보다 강한지 약한지 판정하고, ⓒ $L+L^\top$ 이 양반정부호가 아닌
강연결 방향 그래프를 하나 구성하라(그래도 합의에는 도달한다).
*전략*: ⓐ 는 $\dot V = -\tfrac12\delta^\top(L+L^\top)\delta$ 를 쓴다. ⓒ 가 핵심 — 합의 수렴이
$\lVert\delta\rVert$ 의 **단조** 감소를 요구하지 않는다는 점을 보이는 것이 목표다(과도
응답에서 불일치가 커질 수 있다). 전개는 숨긴다.

**P3 (유도, ★★, R2)** (3)(4)를 빠진 줄 없이 유도하고, ⓐ $r(\epsilon)$ 의 최대가 구간의 양 끝에서만
나는 이유를 쓰고, ⓑ $\epsilon$ 을 Gershgorin 상계 $1/\max_i d_i$ 로 고정했을 때의 수렴률을
$\lambda_2$, $\max_i d_i$ 로 쓰고, ⓒ 별 그래프($n$ 노드, 허브 1개)에서 $\kappa$ 와 $r^\ast$ 를
$n$ 의 함수로 구하라.
*해답 스케치*: ⓒ 별 그래프의 라플라시안 고윳값은 $\{0, 1^{(n-2)}, n\}$ 이므로 $\lambda_2 = 1$,
$\lambda_n = n$, $\kappa = n$, $r^\ast = (n-1)/(n+1)$ 이다. 즉 **노드가 늘면 이산 합의가
선형으로 느려진다.** 연속시간에서는 $\lambda_2 = 1$ 로 $n$ 과 무관하다는 대조를 쓰면 우수.

**P4 (계산, ★, R1·R2·R5)** 재현 과제의 네 그래프에 대해 ⓐ $\lambda_2$ 와 점근 수렴률,
ⓑ 이산시간 최적 보폭과 그때의 수렴률, ⓒ 아령 그래프 $n=10$ 의 $\lambda_2$ 와 간선 하나를 더해
얻는 최선·최악·Fiedler 선택의 $\lambda_2$ 를 구하라.
*정답*: ⓐⓑ 는 재현 과제 수용 기준 1·2 의 표. ⓒ 기본 $\lambda_2 = 0.29843788$, 최선
$0.62771868$(간선 $(3,9)$), 최악 $0.53589838$(간선 $(2,5)$), Fiedler 선택 $(6,1)$ →
$0.62771868$ (최적과 일치), 무작위 간선 평균 $0.59833618$. 허용오차 $10^{-6}$.
검산: 아령 그래프의 Fiedler 벡터가 5:5 로 갈리고 다리 양끝 두 노드의 절댓값이 가장 작은지
($\pm0.2341$ 대 $\pm0.3336$) 확인한다 — 다르면 라플라시안이나 그래프 구성이 틀렸다.

**P5 (계산, ★★, R3·R4)** ⓐ 방향 사이클 $0\to1\to2\to3\to4\to0$ 에 현 $0\to3$ 을 더한 그래프의
$w$ 와 $x(0) = (1,2,-3,4,0.5)$ 에서의 합의값을 **손으로** 구하고 수치와 대조하라.
ⓑ 현을 뺀 순수 방향 사이클에서 합의값이 평균임을 확인하라. ⓒ $n=6$ 에서 각각 $\lambda_2 = 0$
이지만 합집합이 연결인 두 그래프를 만들어 합의에 도달함을 보이고, 합집합이 연결이 아닌 쌍에서는
도달하지 않음을 보이라.
*정답*: ⓐ $w = (\tfrac27,\tfrac17,\tfrac17,\tfrac17,\tfrac27)$, 합의값
$\tfrac{2+2-3+4+1}{7} = \tfrac67 = 0.857142857$ (평균 $0.9$ 와 다름). ⓑ 정확히 $0.9$.
ⓒ 합집합 연결: 4000 스텝 뒤 불일치 $< 10^{-15}$ (참조 $2.2\times10^{-16}$); 합집합 비연결:
불일치 $2.5$ 로 정체. 허용오차 $10^{-8}$.
*ⓐ의 채점 포인트*: $w$ 를 고유분해로 "구하는" 것이 아니라 $w^\top L = 0$ 을 성분별 연립으로
손으로 풀어야 통과. 왜 노드 0 과 4 가 큰 가중치를 받는지(out-degree 대 in-degree) 한 줄로
설명해야 한다.

**P6 (구현, ★★, R5)** $\lambda_2$ 를 최대화하는 문제를 두 방식으로 풀어 비교하라.
ⓐ 간선 **가중치**에 대한 최대화: $\max_{a\ge0,\ \sum a = 1}\lambda_2(L(a))$ 를 SDP
($\max t$ s.t. $L(a) \succeq t(I - \tfrac1n\mathbf{1}\mathbf{1}^\top)$)로 풀고, ⓑ 간선 **집합**에
대한 탐욕 추가(Fiedler 휴리스틱)와 완전 탐색을 비교하라.
*루브릭*: ⓐ 가 볼록임을 제약식으로 보이고(λ₂ 가 $a$ 의 오목 함수) 수치 해를 보고 ⓑ 에서
탐욕과 완전 탐색이 간선 1개에서는 일치하고 2-3개에서는 갈라지는 것을 수치로 제시
ⓒ $\lambda_2$ 가 중복인 그래프(예: 완전 그래프, 사이클)에서 (15)의 1차 섭동이 쓸 수 없음을
보이고 ⓓ 두 문제의 복잡도 차이(볼록 대 조합)를 한 문단으로 정리.

**P7 (반례, ★★, R2·R4)** ⓐ "합의가 빠른 그래프는 $\lambda_2$ 가 큰 그래프다"가 **이산시간에서**
거짓임을 보여라 — $\lambda_2$ 가 더 큰데 이산 수렴이 더 느린 그래프 쌍을 구성하라.
ⓑ "매 순간 그래프가 연결이면 시변 합의가 고정 그래프보다 빠르다"가 거짓임을 보여라.
*성질 체크리스트*: ⓐ 는 $\kappa = \lambda_n/\lambda_2$ 가 지배한다는 R2 를 쓴다 — 별 그래프와
사이클을 비교하면 된다($\lambda_2$: 별 1, 사이클 $2(1-\cos(2\pi/n))$ 로 별이 크지만 $\kappa$ 는
별이 $n$, 사이클이 $O(n^2)$ ... 어느 쪽이 큰지 직접 계산해 결론을 뒤집지 말 것).
ⓑ 는 매 순간 연결이어도 간선이 거의 없는 트리만 번갈아 쓰면 느려진다는 구성을 쓴다.
"반례를 수치로 확인했다"까지 써야 통과.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`f0-how-to-read-this-track` 레슨의 "논문 읽기" 절). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Olfati-Saber, Fax & Murray, "Consensus and cooperation in networked multi-agent systems"
   (2007, Proceedings of the IEEE)** — 역할: `서베이(survey)`.
   <https://doi.org/10.1109/JPROC.2006.887293> (II-III 절)
   추가 질문: ⓐ 저자들이 정리한 합의 변형(가중, 리더-추종, 시간 지연) 중 본문 R1-R4 로
   설명되는 것과 새 도구가 필요한 것을 나누면? ⓑ 시간 지연이 들어오면 (2)의 지수가 어떻게
   바뀌는가?
2. **Jadbabaie, Lin & Morse, "Coordination of groups of mobile autonomous agents using nearest
   neighbor rules" (2003, IEEE T-AC)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1109/TAC.2003.812781> (III 절)
   추가 질문: ⓐ 저자들의 결합 연결성 조건이 본문 R4 의 진술과 정확히 같은가, 더 약한가?
   ⓑ 증명에 쓰인 ergodicity(Dobrushin) 계수가 고정 그래프의 $\lambda_2$ 와 어떤 관계인가?
   ⓒ 저자들이 **보장하지 않는** 것은 무엇인가(수렴률?)
3. **Fiedler, "Algebraic connectivity of graphs" (1973, Czechoslovak Mathematical Journal)** —
   역할: `원전(seminal)`. <https://doi.org/10.21136/CMJ.1973.101168> (§2-3)
   추가 질문: ⓐ Fiedler 가 $\lambda_2$ 에 대해 증명한 상·하계를 하나씩 쓰고 본문 (14)와
   연결하라. ⓑ 이 논문에 "합의"라는 말이 없는데도 다중 로봇 문헌의 1순위 인용인 이유는?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R1 (수치 검증).** 계산 예산: 노트북 CPU 1코어, 전체 1분 이내, 메모리 200MB 이하.
numpy + scipy 만 쓴다.

**입력 데이터**는 아래 생성기가 만든다(고정 시드·결정론적). 외부 데이터셋이 필요 없다.

```python
"""s5-graph-consensus 재현 과제: 그래프 생성기와 라플라시안."""

import numpy as np

SEED = 20261112


def laplacian(A):
    """무향이면 대칭 라플라시안, 방향이면 in-degree 라플라시안 L = D_in - A."""
    return np.diag(A.sum(1)) - A


def er_graph(n, p, rng):
    """Erdos-Renyi G(n,p). 연결될 때까지 다시 뽑는다. 인접행렬을 돌려준다."""
    while True:
        A = (rng.random((n, n)) < p).astype(float)
        A = np.triu(A, 1)
        A = A + A.T
        if np.linalg.eigvalsh(laplacian(A))[1] > 1e-9:
            return A


def directed_cycle(n, chord=None):
    """방향 사이클 i -> i+1. chord=(i, j) 를 주면 간선 i -> j 를 추가한다."""
    A = np.zeros((n, n))
    for i in range(n):
        A[(i + 1) % n, i] = 1.0  # A[i, j] = 1 은 "i 가 j 를 듣는다"
    if chord is not None:
        i, j = chord
        A[j, i] = 1.0
    return A


def edge_graph(n, pairs):
    """주어진 무향 간선 목록만 가진 그래프의 라플라시안."""
    A = np.zeros((n, n))
    for i, j in pairs:
        A[i, j] = A[j, i] = 1.0
    return laplacian(A)


def barbell(k):
    """k-클리크 두 개를 간선 하나로 이은 아령 그래프 (n = 2k)."""
    n = 2 * k
    A = np.zeros((n, n))
    for a in range(k):
        for b in range(a + 1, k):
            A[a, b] = A[b, a] = 1.0
            A[k + a, k + b] = A[k + b, k + a] = 1.0
    A[k - 1, k] = A[k, k - 1] = 1.0
    return A
```

**해야 할 일.** 네 Part 를 측정한다. 연속시간 전파는 `scipy.linalg.expm` 을 쓴다.

**Part A — 수렴률 = $\lambda_2$.** `rng = np.random.default_rng(SEED)` 로
$(n,p) \in \{(20,0.2), (20,0.5), (40,0.15), (60,0.1)\}$ 를 **그 순서로** 뽑는다(같은 `rng` 를
계속 쓴다). 각 그래프에서 $x_0 \sim$ `rng.standard_normal(n)`, $\delta_0 = x_0 - \bar x_0$ 으로
두고, **늦은 구간의 두 점 기울기**로 점근 수렴률을 잰다:
$t_1 = 20/\lambda_2$, $t_2 = 25/\lambda_2$ 에서
$\text{rate} = \big(\log\lVert\delta(t_1)\rVert - \log\lVert\delta(t_2)\rVert\big)/(t_2-t_1)$.
(이른 구간을 쓰면 빠른 모드가 섞여 10% 규모로 틀린다 — 진단표 참조.)

**Part B — 이산시간 최적 보폭.** `np.random.default_rng(SEED + 1)` 로 $(20,0.3)$, $(30,0.2)$ 를
그 순서로 뽑는다. 각 그래프에서 (4)의 $\epsilon^\ast, r^\ast$ 를 계산하고, $\epsilon$ 을
$[10^{-4},\ 2/\lambda_n)$ 에서 20001 점 격자로 쓸어 (3)의 $r(\epsilon)$ 을 최소화한 값과 비교한다.

**Part C — 방향·시변 그래프.** ⓐ `directed_cycle(5, chord=(0, 3))` 와 `directed_cycle(5)` 에서
$w$(좌 영벡터, $w^\top\mathbf{1}=1$ 로 정규화), $\lVert\mathbf{1}^\top L\rVert_\infty$,
$x(0) = (1,2,-3,4,0.5)$ 에서의 합의값($t = 400$ 의 `expm`)을 구한다. ⓑ $n=6$ 에서
$\mathcal{G}_0 = \{(0,1),(2,3),(4,5)\}$, $\mathcal{G}_1 = \{(1,2),(3,4)\}$ 를 $\epsilon = 0.4$ 로
4000 스텝 번갈아 적용하고, 같은 것을 $\{(0,1),(2,3)\}$, $\{(1,2)\}$ 쌍에 대해서도 한다.
$x_0 = (1,2,-3,4,0.5,-1.5)$.

**Part D — Fiedler 벡터와 간선 추가.** `barbell(5)` 에서 $\lambda_2$ 와 Fiedler 벡터를 구하고,
없는 간선 전부를 하나씩 더해 $\lambda_2$ 를 재어 최선·최악을 찾고, Fiedler 휴리스틱
($\arg\max f$ 와 $\arg\min f$ 를 잇기)의 결과와 비교한다.

**수용 기준 — 네 조건을 모두 만족해야 통과다.**

1. **Part A** — 아래 표를 재현하고, 네 경우 모두 **상대오차 $< 10^{-5}$**.

   | $n$ | $p$ | $\lambda_2$ | 점근 수렴률 | 상대오차 |
   |---|---|---|---|---|
   | 20 | 0.20 | $1.483185$ | $1.483190$ | $3.2\times10^{-6}$ |
   | 20 | 0.50 | $2.765269$ | $2.765270$ | $4.5\times10^{-7}$ |
   | 40 | 0.15 | $1.350570$ | $1.350571$ | $4.5\times10^{-7}$ |
   | 60 | 0.10 | $1.253177$ | $1.253180$ | $1.9\times10^{-6}$ |

   $\lambda_2$ 값은 허용오차 $10^{-6}$ (그래프가 시드로 고정되어 있다).
2. **Part B** — 예측과 격자 탐색이 **6자리 이상** 일치한다.

   | $n$ | $\lambda_2$ | $\lambda_n$ | $\epsilon^\ast$ (예측 / 격자) | $r^\ast$ (예측 / 격자) |
   |---|---|---|---|---|
   | 20 | $1.7280$ | $11.7097$ | $0.14883470$ / $0.14882942$ | $0.74281249$ / $0.74282161$ |
   | 30 | $0.8708$ | $12.7777$ | $0.14653635$ / $0.14653534$ | $0.87239449$ / $0.87239537$ |

   (격자 쪽이 6-7번째 자리에서 다른 것은 격자 간격 때문이다 — 격자를 촘촘히 하면 수렴한다.)
3. **Part C** — ⓐ 현이 있는 그래프에서 $\lVert\mathbf{1}^\top L\rVert_\infty = 1$,
   $w = (0.2857, 0.1429, 0.1429, 0.1429, 0.2857)$ ($=(\tfrac27,\tfrac17,\tfrac17,\tfrac17,\tfrac27)$,
   허용오차 $10^{-6}$), 합의값 $0.85714286$ ($=6/7$) 로 평균 $0.9$ 와 다르다. 순수 사이클에서는
   $\lVert\mathbf{1}^\top L\rVert_\infty = 0$, $w = \mathbf{1}/5$, 합의값 $0.9$ (정확히 평균).
   두 경우 모두 최종 **퍼짐 $< 10^{-14}$** (참조 $1.1\times10^{-15}$, $6.7\times10^{-16}$).
   ⓑ 합집합이 연결인 쌍에서 4000 스텝 뒤 퍼짐 $< 10^{-14}$ (참조 $2.2\times10^{-16}$)이고
   평균이 보존된다($< 10^{-14}$); 합집합이 연결이 아닌 쌍에서는 퍼짐이 $2.500$ 에 정체한다
   (허용오차 $10^{-3}$). **두 경우 모두 각 그래프의 $\lambda_2$ 가 0 임을, 그리고 합집합
   라플라시안 $L_0+L_1$ 의 $\lambda_2$ 가 각각 $0.2679$ 와 $0.0000$ 임을 함께 보고한다** —
   판별하는 것은 순간 $\lambda_2$ 가 아니라 합집합의 $\lambda_2$ 라는 것이 Part C 의 요점이다.
4. **Part D** — `barbell(5)` 에서 $\lambda_2 = 0.29843788$, Fiedler 벡터가 부호로 5:5 로 갈리고
   다리 양끝 노드(인덱스 4, 5)의 절댓값이 $0.2341$, 나머지가 $0.3336$ 이다(허용오차 $10^{-4}$).
   간선 하나 추가의 최선 $\lambda_2 = 0.62771868$, 최악 $0.53589838$, Fiedler 휴리스틱
   $0.62771868$ (최적과 $10^{-9}$ 이내로 일치), 무작위 간선 200개 평균 $0.59833618$
   (`default_rng(3)`, 허용오차 $10^{-3}$).

**비교 대상**: ⓐ Part A 의 베이스라인은 $\lambda_2$ 자체(해석값)다. ⓑ Part B 의 베이스라인은
격자 탐색. ⓒ Part C ⓐ 의 베이스라인은 평균 $\bar x_0$ — **그것이 틀린 답이라는 것이 측정
대상**이다. ⓓ Part D 의 베이스라인은 완전 탐색과 무작위 간선. 선택: Part A 에서 이른 구간
($t \in [0, 12/\lambda_2]$ 전체)으로 최소제곱 적합을 해 상대오차가 $10^{-1}$ 규모로 나빠지는
것을 함께 보고하면 왜 늦은 구간을 쓰는지가 분명해진다(참조: $1.5\times10^{-1}$ 까지).

**보고할 수치**: 위 네 조건의 모든 값, 그리고 Part B 에서 $\kappa = \lambda_n/\lambda_2$ 와
$r^\ast = (\kappa-1)/(\kappa+1)$ 가 일치하는지(두 번째 그래프는 $\kappa = 14.67$,
$r^\ast = 0.8724$).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| Part A 의 수렴률이 $\lambda_2$ 보다 10% 정도 **크다** | 이른 구간을 포함해 적합했다 — 빠른 모드가 아직 살아 있다 | $t_1 = 20/\lambda_2$ 로 늦추고, 선택 비교(전 구간 적합)와 나란히 본다 |
| Part A 에서 $\lVert\delta(t)\rVert$ 가 0 이 되어 로그가 발산 | $t_2$ 가 너무 커서 언더플로 | $e^{-25} \approx 1.4\times10^{-11}$ 이 상대 규모임을 확인하고 $t_2$ 를 줄인다 |
| Part A 의 $\lambda_2$ 가 표와 다르다 | `rng` 를 그래프마다 새로 만들었다 | 하나의 `rng` 를 네 그래프에 **연속으로** 쓰는지, 재추출 루프가 `rng` 를 소비하는지 확인 |
| Part B 의 격자 최적이 예측과 2자리만 맞는다 | 격자가 거칠다 | 점 수를 10배로 올려 예측값으로 수렴하는지 본다 |
| Part C ⓐ 의 $w$ 가 음수 성분을 갖는다 | 고유벡터의 부호·정규화를 안 맞췄다 | $w$ 를 $w^\top\mathbf{1} = 1$ 로 정규화하고 부호를 양수로 고정 |
| Part C ⓐ 의 합의값이 평균과 같게 나온다 | 인접행렬 방향을 뒤집었다($A_{ij}$ 의 뜻) | $\lVert\mathbf{1}^\top L\rVert_\infty$ 가 0 이 아닌지 먼저 확인한다 |
| Part C ⓑ 가 합집합 비연결에서도 수렴한다 | 두 그래프에 노드 4, 5 를 잇는 간선이 섞여 들어갔다 | 두 라플라시안의 합의 $\lambda_2$ 를 출력해 0 인지 확인 |
| Part D 의 Fiedler 벡터가 5:5 로 안 갈린다 | $\lambda_2$ 가 중복이라 고유벡터가 섞였다 | $\lambda_3-\lambda_2$ 를 출력한다 — 아령(5)에서는 $4.7016$ 으로 단순 고윳값이다 |

## 열린 문제

- **(열린 문제) 분산 환경에서 $\lambda_2$ 를 알지 못한 채 최적 보폭을 고르기** — (4)의
  $\epsilon^\ast$ 는 전역량 $\lambda_2, \lambda_n$ 을 요구하지만 각 로봇은 자기 이웃만 안다.
  현재 접근은 보수적인 국소 상계($\epsilon < 1/\max_i d_i$)를 쓰거나, 합의 자체로 $\lambda_n$ 을
  추정하는 2단계 방법, 또는 가속(Chebyshev·heavy-ball) 합의다. 현재 접근:
  [consensus survey](https://doi.org/10.1109/JPROC.2006.887293) §II-III.
  비어 있는 자리: **적응적으로** 보폭을 고치면서 수렴을 보장하고 최적 $r^\ast$ 에
  점근하는 완전 분산 규칙.
- **(열린 문제) 적대적·비협조 노드가 섞인 합의** — R1-R4 는 모든 노드가 같은 규칙을 따른다고
  전제한다. 일부가 임의의 값을 보내면(Byzantine) 합의값이 임의로 조작될 수 있고, 합의와
  강건 추정을 함께 다루는 이론은 아직 조각난 상태다
  (`c5-robust-global-estimation` 의 뭉친 이상치 문제와 같은 뿌리다). 현재 접근: 극단값을
  버리는 필터링 규칙과 연결성 조건의 강화. 비어 있는 자리: 적대 노드 비율과 그래프 연결성에서
  달성 가능한 정확도로 가는 상계.
- **(열린 문제) 통신 비용과 수렴률의 교환** — $\lambda_2$ 를 키우려면 간선(통신 링크)이
  필요하고, 링크는 대역폭·전력·탐지 위험을 쓴다. 가중치에 대한 $\lambda_2$ 최대화는 볼록이지만
  (문제 P6), **비용 제약 아래 간선 집합을 고르는** 문제는 조합이고 submodular 도 아니다
  ($\lambda_2$ 는 간선 집합의 submodular 함수가 아니다 — `s5-active-information-gathering` 의
  보장이 여기 적용되지 않는 이유다). 현재 접근: SDP 완화 + 라운딩, 탐욕 휴리스틱.
  비어 있는 자리: 간선 선택에 대한 근사비 보장.

## 개념 점검

`rc quiz s5-graph-consensus` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`f0-how-to-read-this-track` 레슨의 "문제 세트" 절).

```quiz
activity: s5-graph-consensus-quiz
questions:
  - id: q1
    type: short
    prompt: "무향 연결 그래프에서 연속시간 합의 $\\dot x = -Lx$ 의 불일치가 줄어드는 지수(수렴률)는 라플라시안의 무엇인가? 기호로 쓰라."
    answer: ["lambda_2", "λ2", "λ_2", "lambda2", "second smallest eigenvalue", "algebraic connectivity", "대수적 연결성"]
    explanation: "$\\lambda_2$(대수적 연결성)다. 불일치 $\\delta$ 가 $\\mathbf{1}^\\perp$ 에 머물고 그 부분공간에서 $L$ 의 가장 작은 고윳값이 $\\lambda_2$ 이므로 $\\lVert\\delta(t)\\rVert \\le e^{-\\lambda_2 t}\\lVert\\delta(0)\\rVert$ 이고, Fiedler 벡터 방향에서 등식이므로 **개선할 수 없는** 지수다."
    concept: { front: "연속시간 합의의 수렴률", back: "$\\lambda_2$ (대수적 연결성). Fiedler 벡터 방향에서 등식 — 상계가 아니라 정확한 최악 지수" }
  - id: q2
    type: single
    prompt: "이산시간 합의 $x_{k+1} = (I-\\epsilon L)x_k$ 의 최적 보폭에서 수렴률을 지배하는 양은?"
    choices:
      - "$\\lambda_2$ 뿐"
      - "$\\lambda_n$ 뿐"
      - "비율 $\\kappa = \\lambda_n/\\lambda_2$ — 수렴률이 $(\\kappa-1)/(\\kappa+1)$ 이다"
      - "노드 수 $n$ 뿐"
    answer: 2
    explanation: "$\\epsilon^\\ast = 2/(\\lambda_2+\\lambda_n)$ 에서 $r^\\ast = (\\lambda_n-\\lambda_2)/(\\lambda_n+\\lambda_2) = (\\kappa-1)/(\\kappa+1)$ 이다. 연속시간은 $\\lambda_2$ 만 보지만 **이산시간은 비율을 본다** — 허브가 하나인 별 그래프는 $\\lambda_2 = 1$ 로 크지만 $\\lambda_n = n$ 이라 $\\kappa = n$ 이 되어 느리다."
    concept: { front: "이산 합의의 수렴률", back: "$r^\\ast = (\\kappa-1)/(\\kappa+1)$, $\\kappa = \\lambda_n/\\lambda_2$. 연속시간($\\lambda_2$)과 다른 양이 지배한다" }
  - id: q3
    type: single
    prompt: "방향 그래프에서 합의값이 초기값의 **평균**이 되는 조건은?"
    choices:
      - "강연결이면 된다"
      - "그래프가 균형(balanced, in-degree = out-degree)이어야 한다"
      - "뿌리 있는 신장 외향 트리가 있으면 된다"
      - "방향 그래프에서는 항상 평균이다"
    answer: 1
    explanation: "합의값은 좌 영벡터로 가중한 $w^\\top x(0)$ 이고, $w = \\mathbf{1}/n$ 인 것이 $\\mathbf{1}^\\top L = 0$, 즉 균형성과 동등하다. 외향 트리는 **수렴**의 조건이고 평균의 조건이 아니다 — 재현 과제에서 방향 사이클에 현 하나를 더하면 강연결인데도 합의값이 $6/7$ 로 평균 $0.9$ 와 다르다."
    concept: { front: "방향 그래프의 평균 합의", back: "균형(in-deg = out-deg) $\\iff \\mathbf{1}^\\top L = 0 \\iff w = \\mathbf{1}/n$. 강연결·외향 트리는 수렴 조건일 뿐" }
  - id: q4
    type: truefalse
    prompt: "시변 그래프에서 합의에 도달하려면 적어도 때때로 연결된 그래프가 나타나야 한다."
    answer: false
    explanation: "필요한 것은 **결합 연결성**뿐이다 — 유계 구간마다 그래프들의 합집합이 연결이면 된다. 재현 과제에서 $\\lambda_2 = 0$ 인(각각 연결이 아닌) 두 그래프를 번갈아 쓰기만 해도 불일치가 $2.2\\times10^{-16}$ 까지 줄어든다. 확률행렬의 **곱**이 섞기 때문이다."
    concept: { front: "시변 합의의 조건", back: "결합 연결성(구간별 합집합이 연결)만 필요. 각 순간 $\\lambda_2 = 0$ 이어도 수렴한다 — 순간 $\\lambda_2$ 는 예측력이 없다" }
  - id: q5
    type: single
    prompt: "Fiedler 벡터 $f$ 의 양극단을 잇는 간선을 추가하는 휴리스틱의 근거는?"
    choices:
      - "항상 $\\lambda_2$ 를 최대로 올린다는 정리가 있다"
      - "1차 섭동에서 $\\Delta\\lambda_2 \\approx (f_i-f_j)^2$ 이므로 그 차가 최대인 쌍이 1차에서 최선이다"
      - "통신 거리가 가장 짧기 때문"
      - "$f$ 의 부호가 같은 노드끼리 이어야 하기 때문"
    answer: 1
    explanation: "간선 추가는 $L \\to L + (e_i-e_j)(e_i-e_j)^\\top$ 이고 1차 고윳값 섭동이 $(f_i-f_j)^2$ 다. 재현 과제의 아령 그래프에서 이 휴리스틱이 완전 탐색의 최적($0.62772$)과 일치하지만, **보장은 아니다** — $\\lambda_2$ 가 중복이면 1차 섭동 자체를 쓸 수 없다."
    concept: { front: "Fiedler 탐욕 간선 추가", back: "$\\Delta\\lambda_2 \\approx (f_i-f_j)^2$ 의 1차 섭동. 휴리스틱이며 보장 없음 — $\\lambda_2$ 중복이면 무효" }
```

## 이 단계 공부법

1. **(6)을 손으로 전개한다 (30분)** — $v^\top Lv = \sum_{\{i,j\}}a_{ij}(v_i-v_j)^2$ 를 $n=3$
   경로 그래프에서 직접 확인한다. 이 한 줄에서 $L\succeq0$, 영공간, 연결성이 모두 나온다.
   `c5-factor-graphs-map` 의 게이지 논증과 **같은 문장**이라는 것을 확인하는 순간이 중요하다.
2. **R1 을 백지에서 (45분)** — (7)(8)을 재구성한다. 특히 "$\delta$ 가 $\mathbf{1}^\perp$ 에
   머문다"는 단계가 **대칭성** 때문이라는 것을 여백에 적는다. R3 에서 그 줄이 깨진다.
3. **Part A 를 먼저 돌린다 (45분)** — 전 구간 적합으로 10% 틀리는 것을 **먼저** 보고, 늦은
   구간으로 바꿔 $10^{-6}$ 이 되는 것을 본다. "점근 수렴률"이라는 말의 뜻이 몸에 남는다.
4. **R2 를 종이에서 최적화한다 (45분)** — (10)의 "두 값이 같아지는 곳"이 최소라는 논증을
   그림으로 그린다. 그 다음 P3ⓒ 의 별 그래프를 계산해 $\kappa = n$ 을 얻는다. 연속시간과
   이산시간이 다른 양을 본다는 것이 이 레슨에서 가장 실무적인 결론이다.
5. **Part C 를 손 계산과 대조한다 (60분)** — $w^\top L = 0$ 을 성분별로 손으로 풀어
   $(\tfrac27,\tfrac17,\tfrac17,\tfrac17,\tfrac27)$ 을 얻고 $6/7$ 을 계산한 뒤 코드와 맞춘다.
   그 다음 시변 실험에서 $\lambda_2 = 0$ 인 그래프들로 합의가 되는 것을 본다 — 이 레슨에서
   가장 반직관적인 숫자다.
6. **Part D 와 P6 (60분)** — Fiedler 벡터를 출력해 아령의 다리를 눈으로 찾고, 간선 추가의
   효과를 완전 탐색과 대조한다. P6 의 SDP 를 풀어 "가중치에는 볼록, 간선 집합에는 조합"을
   수치로 확인한다.
7. **논문은 보장의 범위로 읽는다 (150분)** — Jadbabaie et al. III 절에서 결합 연결성 정리가
   **수렴률을 주지 않는다**는 것을 확인하고, Olfati-Saber et al. II-III 절로 변형들을 훑고,
   Fiedler 1973 으로 $\lambda_2$ 의 상·하계를 본다. 논문당 1페이지 노트는 **반드시** 쓴다.
8. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제" 세 개 중 하나를 골라 한 문단으로 쓴다.
   분산 환경에서 보폭을 고르는 문제는 Part B 의 숫자가 바로 동기다.

**통과 기준**: 백지에서 (6)(8)과 (10)을 유도할 수 있고, 방향 그래프에서 합의값이 $w^\top x(0)$
인 이유를 쓸 수 있고, 재현 과제의 네 조건을 모두 만족하는 코드를 갖고 있고, 논문 3편의 노트가 있다.
