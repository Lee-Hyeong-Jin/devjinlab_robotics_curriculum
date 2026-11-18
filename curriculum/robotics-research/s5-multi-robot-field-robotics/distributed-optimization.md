---
id: s5-distributed-optimization
title: 분산 최적화와 분산 SLAM
summary: >-
  여러 로봇이 자기 데이터를 남에게 넘기지 않고 함께 하나의 최적화를 푸는 방법을 다룬다. 2블록
  ADMM 의 수렴을 증명하고, 2차 문제에서 ADMM 이 아핀 반복이 되어 수렴률이 명시적 스펙트럼
  반경임을 유도한다. 분산 포즈 그래프의 블록 Gauss-Seidel 수렴률이 정확히
  1 − λ_min(Λ₂₂⁻¹S)(S 는 Schur 보완)임을 증명해 Λ ≻ 0 이면 항상 수렴함을 보이고, 2대 로봇
  포즈 그래프에서 중앙집중 해와 1e-4 이내로 일치시키면서 통신량·수렴률 교환을 수치로 측정한다.
objectives:
  - 2블록 ADMM 의 반복식을 증강 라그랑주에서 유도하고 수렴 정리의 가설을 분리해 진술할 수 있다.
  - 2차 목적함수에서 ADMM 이 아핀 반복임을 보이고 수렴률을 스펙트럼 반경으로 쓸 수 있다.
  - 블록 Gauss-Seidel 의 오차 재귀와 그 수렴률을 Schur 보완으로 유도할 수 있다.
  - Λ ≻ 0 이면 블록 Gauss-Seidel 이 항상 수렴함을 증명할 수 있다.
  - 분산 포즈 그래프에서 separator 크기가 통신량을, 결합 강도가 수렴률을 정하는 것을 측정할 수 있다.
  - 분산 최적화의 수렴과 전역 최적성 인증이 서로 다른 보장임을 설명할 수 있다.
prerequisites: [c5-factor-graphs-map, s5-graph-consensus]
difficulty: 5
estimated_minutes: 630
tags: [multi-robot, distributed-optimization, admm, gauss-seidel, distributed-slam, research]
activities:
  - id: s5-distributed-optimization-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 105
  - id: s5-distributed-optimization-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: s5-distributed-optimization-problems
    kind: exercise
    title: 문제 세트 (증명 2 · 유도 1 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: s5-distributed-optimization-reproduction
    kind: reproduction
    title: 재현 과제 — 2대 분산 포즈 그래프, Gauss-Seidel·ADMM, 통신 교환 (R2)
    estimated_minutes: 180
  - id: s5-distributed-optimization-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Boyd & Vandenberghe, Convex Optimization"
    url: https://web.stanford.edu/~boyd/cvxbook/
    kind: book
    note: ch.5 (쌍대성), ch.9-10. 증강 라그랑주와 쌍대 상승의 배경. 전문 PDF 무료.
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.3-4. 선형화된 포즈 그래프의 정보행렬 — 이 레슨의 2차 문제가 거기서 온다.
papers:
  - id: boyd2011-admm
    required: true
    role: standard
    note: "§3, §7"
  - id: choudhary2017-distributed-slam
    required: true
    role: standard
    note: "§IV-V"
  - id: tian2021-distributed-certifiable
    required: true
    role: seminal
    note: "§III-V"
---

# 분산 최적화와 분산 SLAM

## 전제와 기호

`c5-factor-graphs-map` 의 정규방정식과 Schur 보완, `s5-graph-consensus` 의 분산·수렴률 관점을
그대로 쓴다. **이 레슨의 문제는 `c5-factor-graphs-map` R2 의 선형화된 최소제곱을 두 로봇이
나눠 푸는 것**이다. 추가 기호:

| 기호 | 뜻 |
|---|---|
| $f_i$ | 로봇 $i$ 가 **자기 데이터만으로** 만들 수 있는 목적함수 조각 |
| $\Lambda, \eta$ | 선형화된 전체 문제의 정보행렬·정보벡터($\Lambda\delta = \eta$, `c5-factor-graphs-map` (3)) |
| $\Lambda_{11}, \Lambda_{12}, \Lambda_{22}$ | 로봇 A·B 블록으로 분할한 $\Lambda$. $\Lambda_{21} = \Lambda_{12}^\top$ |
| $S := \Lambda_{22} - \Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ | $\Lambda_{11}$ 에 대한 **Schur 보완**(`c5-factor-graphs-map` R3) |
| $\mathcal{S}$ | **separator** — 로봇 간 측정에 등장하는 포즈들. 통신되는 것은 이들뿐이다 |
| $\rho > 0$ | ADMM 의 페널티(증강) 매개변수 |
| $u, v, w$ | ADMM 의 두 블록 변수와 (스케일된) 쌍대 변수 |
| $M$ | 블록 Gauss-Seidel 의 오차 반복 행렬. $M = \Lambda_{22}^{-1}\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ |
| $T(\rho)$ | 2차 문제에서 ADMM 반복의 아핀 행렬. 수렴률 $= \rho(T)$ |

**왜 분산인가.** 중앙집중 해 $\delta^\ast = \Lambda^{-1}\eta$ 를 구하려면 누군가 $\Lambda$ 전체를
가져야 한다. 그것이 불가능하거나 바람직하지 않은 이유가 셋이다 — ⓐ 통신 대역폭(모든 측정을
한 곳으로 보낼 수 없다) ⓑ 프라이버시(자기 궤적·관측을 남에게 주지 않는다) ⓒ 단일 실패점
(중앙 노드가 죽으면 끝난다). 이 레슨은 **각 로봇이 자기 블록만 풀고 separator 만 교환해서**
같은 답에 도달하는 두 방법(ADMM, 블록 Gauss-Seidel)을 분석한다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (2블록 ADMM 의 반복식과 수렴) [D3]** — $\min_{u,v} f_1(u) + f_2(v)$ s.t. $u = v$ 에 대해
  증강 라그랑주에서
  $$
  u^{k+1} = \arg\min_u f_1(u) + \tfrac{\rho}{2}\lVert u - v^k + w^k\rVert^2, \quad
  v^{k+1} = \arg\min_v f_2(v) + \tfrac{\rho}{2}\lVert u^{k+1} - v + w^k\rVert^2, \quad
  w^{k+1} = w^k + u^{k+1} - v^{k+1} \tag{1}
  $$
  이 나온다. $f_1, f_2$ 가 닫힌 진 볼록이고 증강 라그랑주의 안점(saddle point)이 존재하면
  **잔차 $u^k - v^k \to 0$ 이고 목적값이 최적값으로 수렴**한다(`boyd2011-admm` §3.2). 강볼록성이나
  매끄러움은 **필요하지 않다** — 그 대가로 **수렴률이 보장되지 않는다.**
- **R2 (2차 문제에서 ADMM 은 아핀 반복) [D2]** — $f_i(x) = \tfrac12 x^\top\Lambda_i x - \eta_i^\top x$
  이면 (1)의 두 $\arg\min$ 이 닫힌 형태 $(\Lambda_i + \rho I)^{-1}(\cdots)$ 이고 반복 전체가
  아핀이다. 상태 $(v, w)$ 에 대한 반복 행렬 $T(\rho)$ 를 명시적으로 쓸 수 있고
  **수렴률 $= \rho(T(\rho))$** 다. $\rho$ 가 작으면 쌍대 갱신이 느리고 크면 원 변수가 묶여
  둘 다 느리므로 **최적 $\rho$ 가 내부에 있다.** 재현 과제의 실측: $\rho = 56.23$ 에서
  $\rho(T) = 0.979669$ 가 최소.
- **R3 (블록 Gauss-Seidel 의 오차 재귀와 수렴률) [D2]** — 로봇 A·B 가 번갈아 자기 블록을
  정확히 최소화하면
  $$
  \delta_1^{k+1} = \Lambda_{11}^{-1}(\eta_1 - \Lambda_{12}\delta_2^{k}), \qquad
  \delta_2^{k+1} = \Lambda_{22}^{-1}(\eta_2 - \Lambda_{21}\delta_1^{k+1}) \tag{2}
  $$
  이고, 오차 $e_2^k := \delta_2^k - \delta_2^\ast$ 가 $e_2^{k+1} = M\,e_2^k$,
  $M = \Lambda_{22}^{-1}\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ 를 만족한다. 수렴률은
  $\rho(M)$ 이다. 재현 과제의 실측: 예측 $0.96860653$, 실측 $0.96860641$(상대오차
  $1.2\times10^{-7}$).
- **R3' ($\Lambda \succ 0$ 이면 항상 수렴한다; 수렴률의 닫힌 형태) [D3]** —
  $$
  M = I - \Lambda_{22}^{-1}S \quad\Longrightarrow\quad
  \mathrm{spec}(M) = \{1 - \mu : \mu \in \mathrm{spec}(\Lambda_{22}^{-1}S)\} \subset [0, 1),
  \qquad \rho(M) = 1 - \lambda_{\min}\big(\Lambda_{22}^{-1}S\big). \tag{3}
  $$
  $\Lambda\succ0$ 이면 $S \succ 0$ 이고(`c5-factor-graphs-map` 문제 P2) $S \preceq \Lambda_{22}$
  이므로 $\mu \in (0, 1]$ 이고 따라서 $\rho(M) < 1$ — **블록 Gauss-Seidel 은 추가 가정 없이
  수렴한다.** 재현 과제의 실측: $\lambda_{\min}(\Lambda_{22}^{-1}S) = 0.0313934719$ 이고
  $1 - \lambda_{\min} = \rho(M)$ 가 $2.0\times10^{-15}$ 이내로 일치한다.
- **R4 (통신량과 수렴률은 다른 축이고 서로 반대로 움직인다) [D2]** — 한 번의 왕복에서 교환되는
  것은 **separator 의 포즈뿐**이므로 통신량은 $O(\lvert\mathcal{S}\rvert)$ 이고 전체 통신량은
  (라운드 수) $\times$ $O(\lvert\mathcal{S}\rvert)$ 다. 그런데 로봇 간 측정을 늘리면 정확도는
  올라가지만 (3)의 결합이 강해져 $\rho(M)$ 이 **1 에 가까워진다.** 재현 과제의 실측:
  로봇 간 간선 $13 \to 5 \to 3 \to 1$ 에서 $\rho(M)$ 이
  $0.98968 \to 0.96861 \to 0.95421 \to 0.00466$ 으로 **단조 감소**한다. 간선 하나면 거의
  한 번에 끝난다.
- **R5 (분산 수렴 $\ne$ 전역 최적성 인증) [D1]** — (2)(3)은 **선형화된** 2차 문제의 해로 수렴한다는
  진술이다. $SE(d)$ 위 원 문제의 전역 최적성은 `c5-robust-global-estimation` R3 의 인증
  기계가 필요하고, 그 인증을 분산으로 하는 것은 또 다른 문제다
  (`tian2021-distributed-certifiable`). **"분산으로 수렴했다"와 "전역 최적이다"는 서로 다른
  보장이다.**

## 유도

### R1 — 증강 라그랑주에서 ADMM 이 나오는 과정

제약 $u = v$ 에 승수 $y$ 를 붙인 **증강** 라그랑주는

$$
L_\rho(u, v, y) = f_1(u) + f_2(v) + y^\top(u - v) + \tfrac{\rho}{2}\lVert u - v\rVert^2 \tag{4}
$$

이다. 보통의 라그랑주에 2차 벌점을 더한 것이고, 그 벌점이 ⓐ $f_i$ 가 강볼록이 아니어도 각
부분문제를 강볼록으로 만들고 ⓑ 쌍대 함수를 미분가능하게 만든다.

$w := y/\rho$ (스케일된 쌍대 변수)로 두면 $y^\top(u-v) + \tfrac\rho2\lVert u-v\rVert^2
= \tfrac\rho2\lVert u - v + w\rVert^2 - \tfrac\rho2\lVert w\rVert^2$ 이므로(제곱 완성),
$u$ 에 대한 최소화에서 $v, w$ 를 고정하면 (1)의 첫 식이, $v$ 에 대해서는 둘째 식이 된다.
쌍대 상승(dual ascent) 단계는 $y^{k+1} = y^k + \rho(u^{k+1}-v^{k+1})$ 이고 $w$ 로 나누면
(1)의 셋째 식이다. **ADMM 은 "두 블록을 번갈아 최소화 + 쌍대 상승 한 걸음"** 이고, 블록이
하나면 증강 라그랑주법, 벌점이 없으면 쌍대 분해로 퇴화한다.

**무엇이 보장되는가.** `boyd2011-admm` §3.2 의 정리는 두 가정만 쓴다 — (A1) $f_1, f_2$ 가
닫힌 진 볼록, (A2) (4)의 비증강 라그랑주가 안점을 가진다. 그러면
$\lVert u^k - v^k\rVert \to 0$(원 잔차), $y^k \to y^\ast$(쌍대 수렴),
$f_1(u^k)+f_2(v^k) \to p^\ast$ 다. **$f_i$ 의 강볼록성·매끄러움·유한성은 쓰이지 않는다** —
그래서 ADMM 이 $\ell_1$ 벌점이나 지시 함수(사영)에도 쓰인다.

**가정이 깨지는 곳**: 정리는 **수렴률을 주지 않는다.** 일반 볼록에서 ADMM 은
$O(1/k)$ 규모이고, 강볼록 + 매끄러움을 더해야 선형 수렴을 말할 수 있다. 그리고 $\rho$ 의
선택에 대해 정리가 아무 말도 하지 않는데, 실무 성능은 $\rho$ 에 **수십 배** 차이로 반응한다
(재현 과제 Part C: $\rho = 1$ 과 $\rho = 56$ 에서 3000 반복 뒤 오차가
$4.4\times10^{-3}$ 대 $3.1\times10^{-14}$). 3블록 이상으로 늘리면 **수렴 자체가 깨질 수 있다**
(반례가 알려져 있다) — 2블록이라는 가설이 본질적이다.

### R2 — 2차 문제에서 반복 행렬을 명시적으로 쓴다

$f_i(x) = \tfrac12 x^\top\Lambda_i x - \eta_i^\top x$ 이고 $\Lambda = \Lambda_1 + \Lambda_2$,
$\eta = \eta_1 + \eta_2$ 라 하자(각 로봇이 **자기 간선만** 쌓아 만든 조각이다. 개별
$\Lambda_i$ 는 특이해도 된다). (1)의 두 $\arg\min$ 은 1차 조건에서 닫힌 형태로 나온다:

$$
u^{k+1} = A_1\big(\eta_1 + \rho(v^k - w^k)\big), \qquad
v^{k+1} = A_2\big(\eta_2 + \rho(u^{k+1} + w^k)\big), \tag{5}
$$

$$
A_i := (\Lambda_i + \rho I)^{-1} \quad (\rho > 0 \text{ 이므로 } \Lambda_i \succeq 0 \text{ 만으로 가역}).
$$

(5)를 $w^{k+1} = w^k + u^{k+1} - v^{k+1}$ 과 합치면 상태 $(v^k, w^k)$ 에 대한 **아핀** 반복이다.
$u^{k+1}$ 을 소거하고 계수를 모으면

$$
\begin{bmatrix}v^{k+1}\\ w^{k+1}\end{bmatrix}
= T(\rho)\begin{bmatrix}v^{k}\\ w^{k}\end{bmatrix} + c(\rho),
\qquad
T(\rho) = \begin{bmatrix}
\rho A_2 B_v & \rho A_2(B_w + I)\\
B_v - \rho A_2 B_v & I + B_w - \rho A_2(B_w + I)
\end{bmatrix}, \tag{6}
$$

여기서 $B_v := \rho A_1$, $B_w := -\rho A_1$ 이다($u^{k+1}$ 의 $v^k, w^k$ 계수). 아핀 반복의
수렴 조건과 률은 고정점 이론에서 바로 나온다:

$$
\text{수렴} \iff \rho(T) < 1, \qquad \lVert \text{오차}^k\rVert \sim \rho(T)^k. \tag{7}
$$

**$\rho$ 의 양극단이 모두 나쁜 이유.** $\rho \to 0$ 이면 $A_i \to \Lambda_i^{-1}$ 로 각 부분문제는
잘 풀리지만 쌍대 갱신 $w^{k+1} - w^k = u-v$ 의 효과가 $\rho$ 배로 들어가 **합의가 느리다.**
$\rho \to \infty$ 이면 $A_i \to \rho^{-1}I$ 로 두 변수가 서로에게 강하게 묶여 **원 문제를 거의
풀지 않는다.** 그래서 $\rho(T(\rho))$ 가 내부 최소를 갖는다. 재현 과제의 실측:
$\rho = 1$ 에서 $0.999552$, $\rho = 10^5$ 에서 $0.999991$, $\rho = 56.23$ 에서 $0.979669$ 로
최소다.

**가정이 깨지는 곳**: (6)은 **분할이 고정**되고 각 로봇이 자기 부분문제를 **정확히** 푼다고
가정한다. 부분문제를 반복법으로 근사하면 ADMM 은 부정확(inexact) 버전이 되고 수렴 보장이
약해진다. 또 (6)은 $u, v$ 가 **전체 상태의 복사본**이라는 형태다 — 그래서 한 라운드에 상태
전체를 주고받는다(R4 에서 비용으로 드러난다). 복사 대상을 separator 로 줄이면 행렬이 달라지고
$T$ 를 다시 유도해야 한다.

### R3 — 블록 Gauss-Seidel 의 오차 재귀

ADMM 과 달리, **각 로봇이 상대의 현재 추정을 상수로 보고 자기 블록을 정확히 최소화**하는 것이
블록 Gauss-Seidel(Choudhary et al. 의 distributed Gauss-Seidel)이다. 전체 1차 조건

$$
\begin{bmatrix}\Lambda_{11} & \Lambda_{12}\\ \Lambda_{21} & \Lambda_{22}\end{bmatrix}
\begin{bmatrix}\delta_1\\ \delta_2\end{bmatrix}
= \begin{bmatrix}\eta_1\\ \eta_2\end{bmatrix} \tag{8}
$$

에서 첫 블록 행을 $\delta_1$ 에 대해, 둘째를 $\delta_2$ 에 대해 풀면 (2)가 된다. 최적해
$(\delta_1^\ast, \delta_2^\ast)$ 는 (8)을 만족하므로 (2)에서 빼면 오차가 남는다:

$$
e_1^{k+1} = -\Lambda_{11}^{-1}\Lambda_{12}\,e_2^{k}, \qquad
e_2^{k+1} = -\Lambda_{22}^{-1}\Lambda_{21}\,e_1^{k+1}
= \underbrace{\Lambda_{22}^{-1}\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}}_{=: M}\,e_2^{k}. \tag{9}
$$

오차가 **선형 재귀**를 따르고 반복 행렬이 $M$ 이다. 따라서 수렴률은 $\rho(M)$ 이고, 로봇 A 의
오차는 $e_1^k = -\Lambda_{11}^{-1}\Lambda_{12}e_2^{k-1}$ 로 같은 률을 따른다.

**중앙집중 해와의 관계.** (9)가 0 으로 가면 두 로봇의 추정이 $\Lambda^{-1}\eta$ 로 간다 —
**중앙집중 해와 같은 점**이다. 분산이 정확도를 깎지 않는다. 깎는 것은 **라운드 수**다.
재현 과제의 실측: $10^{-2}$ 까지 44 라운드, $10^{-4}$ 까지 186 라운드, $10^{-8}$ 까지 475
라운드, 4000 라운드 뒤 오차 $1.5\times10^{-15}$.

**가정이 깨지는 곳**: (2)는 각 로봇이 자기 블록을 **정확히** 푼다고 가정한다 — $\Lambda_{11}$ 이
크면 그 자체가 비싸고, 근사하면 (9)의 깔끔한 재귀가 깨진다. 더 중요한 것은 (8)이 **선형화된**
문제라는 점이다: 비선형 포즈 그래프에서는 매 Gauss-Newton 바깥 반복마다 $\Lambda$ 가 바뀌고,
안쪽 Gauss-Seidel 라운드 수를 줄이면 바깥 반복이 더 필요해진다(문제 P5). 그리고 블록이 2개가
아니라 $m$ 개면 $M$ 이 블록 삼각 분해에서 나오고 로봇 순서에 의존한다 — **순서가 수렴률을
바꾼다**(`c5-sparsity-isam` 의 소거 순서와 같은 종류의 문제다).

### R4 — 통신량과 수렴률

**한 라운드에 무엇이 오가는가.** (2)에서 로봇 A 가 필요한 것은 $\Lambda_{12}\delta_2^k$ 뿐이고,
$\Lambda_{12}$ 는 **로봇 간 측정이 있는 포즈에서만** 비영이다. 따라서 B 가 보내야 하는 것은
separator $\mathcal{S}$ 에 있는 자기 포즈의 증분뿐이다:

$$
\text{라운드당 통신량} = O\big(d\,\lvert\mathcal{S}\rvert\big), \qquad
\text{전체} = (\text{라운드 수}) \times O\big(d\,\lvert\mathcal{S}\rvert\big) \tag{10}
$$

($d = 3$ 이 $SE(2)$ 포즈의 차원). 반면 R2 의 전체 복사 ADMM 은 라운드당 $O(d\,N)$ 을 보낸다.
재현 과제의 실측($N = 50$, $\lvert\mathcal{S}\rvert = 10$): Gauss-Seidel 이 라운드당 30 double,
전체 복사 ADMM 이 150 double — **5배** 차이다. 그리고 $10^{-4}$ 에 도달하는 라운드 수도
186 대 377 로 Gauss-Seidel 이 적다. **이 문제에서 전체 복사 ADMM 은 두 축 모두에서 진다** —
분산 SLAM 문헌이 Gauss-Seidel 계열을 쓰는 이유가 이것이다.

**교환은 어디에 있는가.** 로봇 간 측정을 늘리면 추정 정확도는 올라간다(제약이 늘어난다).
그런데 (3)에서 $\Lambda_{12}$ 가 커지면 $S = \Lambda_{22} - \Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ 가
작아지고 $\lambda_{\min}(\Lambda_{22}^{-1}S)$ 도 작아져 $\rho(M) = 1 - \lambda_{\min}$ 이 1 에
가까워진다. 실측:

| 로봇 간 간선 | separator | $\rho(M)$ |
|---|---|---|
| 13 | 26 | $0.98968495$ |
| 5 | 10 | $0.96860653$ |
| 3 | 6 | $0.95420678$ |
| 1 | 2 | $0.00466476$ |

**더 많이 공유하면 더 정확하지만 더 많이 반복해야 한다.** 간선이 하나면 $\rho(M) \approx 0.005$ 로
사실상 한 라운드에 끝나지만 두 궤적의 상대 위치가 그 하나에 걸린다. 이것이 분산 SLAM 의
설계 교환이고, **라운드당 통신량(separator 크기)과 라운드 수(결합 강도)가 같은 방향으로
나빠진다**는 점이 특히 고약하다.

**가정이 깨지는 곳**: (10)은 통신이 **무손실·무지연**이라고 본다. 패킷 손실이 있으면 (9)의
재귀가 비동기 반복이 되고 수렴 조건이 달라진다(`s5-comms-constrained-estimation` 의 주제).
그리고 (10)은 증분만 센다 — 실제로는 포즈 id, 공분산 블록, 데이터 연관 가설이 함께 가므로
상수 배가 크다.

### R5 — 수렴과 인증은 다른 보장이다

(2)(3)이 주는 것은 "**선형화된** 2차 문제의 유일한 해로 수렴한다"이다. 원 문제는
$SE(d)^N$ 위의 비볼록 문제이고, 거기서 전역 최적성을 말하려면
`c5-robust-global-estimation` R3 의 쌍대 인증($S \succeq 0$)이 필요하다. 그리고 그 인증을
분산으로 계산하는 것(각 로봇이 자기 블록만 보고 전역 인증에 기여하는 것)은 별도의 문제이며,
`tian2021-distributed-certifiable` 이 그것을 푼다 — Riemannian 블록 좌표 하강으로 랭크 완화
문제를 분산으로 풀고 인증까지 분산으로 수행한다. **[D1]**

보고할 때 셋을 구분한다: ⓐ 분산 반복이 중앙집중 해에 얼마나 가까운가(재현 과제 Part A),
ⓑ 그 중앙집중 해가 선형화 문제의 해인가 원 문제의 지역 최솟값인가, ⓒ 그 지역 최솟값이
전역인가(인증). 논문이 "distributed"와 "certifiably correct"를 같이 쓸 때 어느 것을 주장하는지
확인하는 습관이 필요하다.

## 증명 스케치

### R3' — $\Lambda \succ 0$ 이면 블록 Gauss-Seidel 이 수렴한다

**가설** H1: $\Lambda = \begin{bmatrix}\Lambda_{11} & \Lambda_{12}\\ \Lambda_{21} & \Lambda_{22}\end{bmatrix}$
가 대칭 양정부호다($\Lambda_{21} = \Lambda_{12}^\top$). H2: 반복이 (2)다.
**결론** C1: $M = I - \Lambda_{22}^{-1}S$ 이고 $\mathrm{spec}(M) \subset [0,1)$.
C2: $\rho(M) = 1 - \lambda_{\min}(\Lambda_{22}^{-1}S) < 1$, 따라서 (2)가 **항상** 수렴한다.

**전략**: $M$ 을 Schur 보완으로 다시 쓰고 두 부등식 $S \succ 0$, $S \preceq \Lambda_{22}$ 만 쓴다.
`c5-factor-graphs-map` 의 Schur 보완이 그대로 재사용된다.

1. **$M$ 의 재작성.** $S = \Lambda_{22} - \Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ 의 정의에서
   $\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12} = \Lambda_{22} - S$ 이므로
   $$
   M = \Lambda_{22}^{-1}\big(\Lambda_{22} - S\big) = I - \Lambda_{22}^{-1}S .
   $$
   따라서 $M$ 의 고윳값은 $1 - \mu$, $\mu \in \mathrm{spec}(\Lambda_{22}^{-1}S)$ 다.
2. **$\mu > 0$.** H1 로 주 소행렬 $\Lambda_{11} \succ 0$, $\Lambda_{22} \succ 0$ 이고 Schur
   보완도 $S \succ 0$ 이다(`c5-factor-graphs-map` 문제 P2 — $v\ne0$ 에 대해
   $x = (-\Lambda_{11}^{-1}\Lambda_{12}v,\ v)$ 를 $x^\top\Lambda x > 0$ 에 넣는다).
   $\Lambda_{22}^{-1}S$ 는 두 양정부호 행렬의 곱이므로 고윳값이 모두 **양의 실수**다
   ($\Lambda_{22}^{-1/2}S\Lambda_{22}^{-1/2} \succ 0$ 와 닮음이다).
3. **$\mu \le 1$.** $\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12} \succeq 0$ 이므로
   $S = \Lambda_{22} - \Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12} \preceq \Lambda_{22}$ 이고,
   따라서 $\Lambda_{22}^{-1/2}S\Lambda_{22}^{-1/2} \preceq I$ 로 $\mu \le 1$.
4. **결론.** 2·3 에서 $\mu \in (0, 1]$ 이므로 $1 - \mu \in [0, 1)$ 이고 C1. 가장 큰
   $\lvert 1-\mu\rvert$ 는 가장 작은 $\mu$ 에서 나므로 C2. $\square$
5. **등호가 나는 곳.** $\mu = 1$ $\iff$ 그 방향에서 $\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ 가
   0 $\iff$ 로봇 B 의 그 자유도가 **로봇 간 측정에 전혀 닿지 않는다.** 그 방향의 오차는
   한 라운드에 정확히 사라진다($1-\mu = 0$). 실측에서 $\mathrm{spec}(\Lambda_{22}^{-1}S)$ 의
   최대가 정확히 $1.0000000000$ 이고 $\mathrm{spec}(M)$ 의 최소가 $0$ 인 것이 이것이다.

**가설을 지우면**: H1 의 양정부호성을 빼면(상대 측정만 있어 게이지가 남으면)
$\Lambda_{11}$ 이 특이해 (2)의 첫 식 자체가 정의되지 않는다 — **앵커가 없으면 분산 솔버도
돌지 않는다**(`c5-factor-graphs-map` R3 의 "가설을 지우면"과 같은 이야기). 대칭성을 빼면
2단계의 닮음 논증이 무너지고 $\mu$ 가 복소수가 될 수 있어 $\rho(M) < 1$ 이 보장되지 않는다.
블록이 3개 이상이면 (9)가 블록 삼각 형태가 되고 순서에 의존한다 — 그래도 $\Lambda\succ0$ 이면
수렴하지만(Ostrowski-Reich) 률의 닫힌 형태 (3)은 사라진다.

(생략: 두 양정부호 행렬의 곱의 고윳값이 양의 실수라는 사실의 증명, 그리고 Ostrowski-Reich
정리. Boyd & Vandenberghe ch.9 와 `boyd2011-admm` §3.)

### R1' — ADMM 수렴 정리의 구조

**가설** H1: $f_1, f_2$ 가 닫힌(closed) 진(proper) 볼록 함수다. H2: 비증강 라그랑주
$f_1(u)+f_2(v)+y^\top(u-v)$ 가 안점 $(u^\ast, v^\ast, y^\ast)$ 를 가진다.
**결론** C1: $u^k - v^k \to 0$. C2: $f_1(u^k)+f_2(v^k) \to p^\ast$. C3: $y^k \to y^\ast$.

**전략**: 리아푸노프 함수 $V^k = \tfrac1\rho\lVert y^k - y^\ast\rVert^2 + \rho\lVert v^k - v^\ast\rVert^2$
가 매 반복 감소하고, 감소량이 잔차의 제곱을 상계한다는 것을 보인다.

1. **최적성 조건.** H2 의 안점에서 $u^\ast = v^\ast$, $-y^\ast \in \partial f_1(u^\ast)$,
   $y^\ast \in \partial f_2(v^\ast)$.
2. **반복의 1차 조건.** (1)의 각 $\arg\min$ 에서
   $-\rho(u^{k+1}-v^k+w^k) \in \partial f_1(u^{k+1})$ 등을 읽고, $w$ 의 갱신을 넣어 $y^{k+1}$ 로
   정리한다.
3. **볼록성 부등식.** $f_i$ 의 부분미분 단조성($\langle \partial f(a)-\partial f(b), a-b\rangle \ge 0$)을
   1·2 단계의 식에 적용해 $V^k - V^{k+1} \ge \rho\lVert u^{k+1}-v^{k+1}\rVert^2
   + \rho\lVert v^{k+1}-v^k\rVert^2$ 를 얻는다.
4. **합의 수렴.** $V^k \ge 0$ 이고 감소하므로 우변의 급수가 수렴하고, 따라서 각 항이 0 으로
   간다 — C1 과 $v^{k+1}-v^k \to 0$. 여기서 C2·C3 가 따라온다.
5. **률이 없는 이유.** 3단계는 감소량의 **하계**만 주고 $V^k$ 에 비례하는 감소를 주지 않는다.
   $V^{k+1} \le (1-c)V^k$ 꼴을 얻으려면 $f_i$ 의 강볼록성(또는 메트릭 준정규성)이 필요하다 —
   그래서 R2 의 2차 문제에서는 률을 **정확히** 쓸 수 있지만 일반 볼록에서는 못 쓴다.

**가설을 지우면**: H2 의 안점 존재를 빼면(예: 제약이 모순이거나 최적값이 $-\infty$) 1단계가
무너지고 $y^k$ 가 발산할 수 있다. H1 의 닫힘성을 빼면 $\arg\min$ 이 달성되지 않을 수 있다.
그리고 **블록을 3개로 늘리면** 3단계의 부등식이 성립하지 않고 발산하는 반례가 있다 —
"ADMM 은 블록 수에 무관하다"는 흔한 오해의 반례다.

(생략: 3단계 부등식의 전개. `boyd2011-admm` 부록 A.)

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (증명, ★★, R3')** R3' 의 네 단계를 빠진 줄 없이 쓰고, ⓐ 두 양정부호 행렬의 곱의 고윳값이
양의 실수임을 닮음 변환으로 보이고, ⓑ 5단계의 "등호가 나는 곳"을 정확히 특징화하고,
ⓒ $\rho(M)$ 을 $\Lambda_{22}$ 와 $S$ 의 **고윳값**만으로 상계하라.
*전략 + 핵심 부등식*: ⓐ 는 $\Lambda_{22}^{-1}S \sim \Lambda_{22}^{-1/2}S\Lambda_{22}^{-1/2}$ 로
대칭 양정부호와 닮음임을 쓴다. ⓒ 는
$\lambda_{\min}(\Lambda_{22}^{-1}S) \ge \lambda_{\min}(S)/\lambda_{\max}(\Lambda_{22})$ 로
$\rho(M) \le 1 - \lambda_{\min}(S)/\lambda_{\max}(\Lambda_{22})$ 를 얻는다 — 이 상계는 느슨하지만
**각 로봇이 자기 블록만으로 계산할 수 있다**는 점이 중요하다(분산 가능한 상계). 전개는 숨긴다.

**P2 (증명, ★★★, R1')** R1' 의 3단계 부등식
$V^k - V^{k+1} \ge \rho\lVert u^{k+1}-v^{k+1}\rVert^2 + \rho\lVert v^{k+1}-v^k\rVert^2$ 를
유도하라. ⓑ 그 다음 $f_1, f_2$ 가 $m$-강볼록이면 $V^{k+1} \le (1-c)V^k$ 꼴을 얻을 수 있음을
논증하고 $c$ 를 $m, \rho$ 로 쓰라(상수의 정확한 값은 요구하지 않는다).
ⓒ 3블록 ADMM 이 발산하는 알려진 반례의 **구조**를 한 문단으로 쓰라.
*전략*: ⓐ 는 부분미분 단조성을 두 번 쓰고 $w$ 갱신으로 항을 묶는다. ⓒ 는 세 블록의 제약
행렬이 선형독립이 아닐 때 순환이 생긴다는 점을 쓰면 통과(구체적 $3\times3$ 반례를 찾아
인용하면 우수). 전개는 숨긴다.

**P3 (유도, ★★, R2)** (5)에서 출발해 (6)의 $T(\rho)$ 를 빠진 줄 없이 유도하고, ⓐ $\rho\to0$ 과
ⓑ $\rho\to\infty$ 에서 $\rho(T) \to 1$ 임을 각각 보이고, ⓒ 그로부터 내부 최소의 존재를
논증하라. ⓓ $\Lambda_1 = \Lambda_2 = \tfrac12\Lambda$ 인 대칭 분할에서 $\rho(T)$ 를
$\Lambda$ 의 고윳값으로 닫힌 형태로 구하라.
*해답 스케치*: ⓓ 가 핵심 — 대칭 분할에서 $A_1 = A_2 = (\tfrac12\Lambda+\rho I)^{-1}$ 이고 $T$ 가
$\Lambda$ 의 고유기저에서 $2\times2$ 블록으로 분해되므로, 고윳값 $\lambda$ 마다
$2\times2$ 행렬의 스펙트럼 반경을 계산해 최대를 취하면 된다. 그 결과를 $\rho$ 로 최소화하면
최적 $\rho$ 가 $\Lambda$ 의 **극단 고윳값의 기하평균** 규모로 나온다 —
`s5-graph-consensus` R2 의 $2/(\lambda_2+\lambda_n)$ 과 같은 종류의 결과다.

**P4 (계산, ★, R3·R3'·R4)** 재현 과제의 2대 로봇 포즈 그래프에서 ⓐ $\rho(M)$ 의 예측값과
실측값, ⓑ $\lambda_{\min}(\Lambda_{22}^{-1}S)$ 와 $1-\lambda_{\min}$ 이 $\rho(M)$ 과 일치하는지,
ⓒ $10^{-2}, 10^{-4}, 10^{-6}, 10^{-8}$ 에 도달하는 라운드 수, ⓓ 로봇 간 간선 수에 따른
$\rho(M)$ 표를 구하라.
*정답*: ⓐ 예측 $0.96860653$, 실측 $0.96860641$ (상대오차 $1.2\times10^{-7}$).
ⓑ $\lambda_{\min} = 0.0313934719$, $1-\lambda_{\min} = 0.9686065281 = \rho(M)$ (차
$2.0\times10^{-15}$). 그리고 $\mathrm{spec}(\Lambda_{22}^{-1}S)$ 의 최대가 정확히 $1.0$ 이고
$\mathrm{spec}(M)$ 의 최소가 $0$ 이다. ⓒ $44, 186, 330, 475$ 라운드. ⓓ 본문 R4 의 표
($0.98968495 / 0.96860653 / 0.95420678 / 0.00466476$). 허용오차 $10^{-6}$.
검산: $\Lambda$ 와 $S$ 가 모두 양정부호인지(최소 고윳값 > 0) 먼저 확인한다 — 아니면 앵커가
빠졌다는 뜻이고 (2)가 아예 정의되지 않는다.

**P5 (구현, ★★★, R3·R4)** ⓐ 블록 Gauss-Seidel 과 ⓑ 전체 복사 2블록 ADMM 을 구현해 같은
문제에서 비교하라. ⓒ 그 다음 **비선형** 바깥 반복을 붙여(Gauss-Newton 바깥, Gauss-Seidel 안쪽)
안쪽 라운드 수를 $1, 3, 10, \infty$ 로 바꿔 전체 비용(바깥 반복 $\times$ 안쪽 라운드)을 비교하라.
*루브릭*: ⓐⓑ 는 재현 과제 수용 기준 1·3 을 만족하고, 라운드당 통신량(double 개수)을 함께
보고 ⓒ 는 안쪽 라운드를 줄이면 바깥 반복이 늘어나는 교환을 수치 표로 제시하고 **총 통신량의
최소가 안쪽 $\infty$ 가 아님**을 보여야 통과 ⓓ ADMM 의 $\rho$ 를 격자로 쓸어 최적을 찾고
(6)의 예측과 1% 이내로 일치시킨다.

**P6 (반례, ★★, R4·R5)** ⓐ "로봇 간 측정을 많이 공유하면 분산 최적화가 더 좋아진다"가 거짓임을
재현 과제의 표로 보이고, ⓑ 정확도와 라운드 수를 **같은 단위**(예: 목표 ATE 를 달성하는 총
통신량)로 환산해 최적 공유량이 내부에 있음을 수치로 보이라. ⓒ "분산으로 수렴했으므로 전역
최적이다"가 거짓인 이유를 `c5-robust-global-estimation` R3 의 인증으로 설명하라.
*성질 체크리스트*: ⓐ 는 $\rho(M)$ 의 단조 증가를 쓰면 된다. ⓑ 가 핵심 — 두 축을 하나의
비용으로 묶어야 "최적이 내부에 있다"를 말할 수 있고, 환산 방법(라운드당 바이트 × 라운드 수)을
명시해야 통과. ⓒ 는 "선형화된 문제의 유일 해 $\ne$ 원 비볼록 문제의 전역 최솟값"을 짚어야 한다.

**P7 (논문, ★★, R3·R5)** `choudhary2017-distributed-slam` IV-V 절과
`tian2021-distributed-certifiable` III-V 절을 읽고 ⓐ 두 논문이 각각 **무엇을 분산으로
계산하고 무엇을 보장하는가**를 한 문장씩 쓰고, ⓑ Choudhary et al. 의 "privacy" 주장이 정확히
무엇을 숨기는지(그리고 무엇은 숨기지 못하는지) 쓰고, ⓒ Tian et al. 의 인증이
`c5-robust-global-estimation` R3 의 $S \succeq 0$ 과 어떻게 대응하는지 쓰라.
*루브릭*: ⓐ Choudhary 는 "선형화된(또는 2단계) 포즈 그래프의 분산 해", Tian 은 "랭크 완화
문제의 분산 해 + 전역 최적성의 분산 인증"으로 구분하면 통과. ⓑ 는 separator 포즈의 증분은
여전히 노출된다는 점을 짚으면 우수. ⓒ 는 인증 행렬의 양반정부호성 검사를 분산으로 하는 것이
무엇을 요구하는지(최소 고윳값의 분산 계산) 쓰면 우수.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Boyd, Parikh, Chu, Peleato & Eckstein, "Distributed optimization and statistical learning
   via the alternating direction method of multipliers" (2011, Foundations and Trends in ML)** —
   역할: `표준(standard)`. <https://doi.org/10.1561/9781601984616> (§3, §7)
   추가 질문: ⓐ §3.2 의 수렴 정리가 쓰는 가정과 **쓰지 않는** 가정을 각각 나열하라.
   ⓑ §7 의 consensus ADMM 형태가 본문 R2 의 전체 복사 형태와 같은가 다른가?
   ⓒ 저자들이 $\rho$ 선택에 대해 무엇을 말하고 무엇을 말하지 않는가?
2. **Choudhary, Carlone, Nieto, Rogers, Christensen & Dellaert, "Distributed mapping with privacy
   and communication constraints" (2017, IJRR)** — 역할: `표준(standard)`.
   <https://arxiv.org/abs/1702.03435> (§IV-V)
   추가 질문: ⓐ 저자들의 distributed Gauss-Seidel 이 본문 (2)와 같은가, separator 처리가
   다른가? ⓑ 통신량을 어떤 단위로 보고하며 본문 (10)과 대조 가능한가?
   ⓒ 2단계(회전 먼저, 포즈 다음) 분해가 수렴률에 미치는 영향은?
3. **Tian, Khosoussi, Rosen & How, "Distributed certifiably correct pose-graph optimization"
   (2021, IEEE T-RO)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1109/TRO.2021.3072346> (§III-V)
   추가 질문: ⓐ 저자들이 분산으로 계산하는 **인증**이 정확히 무엇인가?
   ⓑ Riemannian 블록 좌표 하강의 수렴 보장이 본문 R3' 와 같은 종류인가?
   ⓒ 통신 라운드 수가 로봇 수에 어떻게 비례하는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, 전체 2분 이내, 메모리 300MB 이하.
numpy 만 쓴다(가장 큰 행렬이 $300\times300$ 이다).

**입력 데이터**는 아래 생성기가 만든다(고정 시드·결정론적). 외부 데이터셋이 필요 없다.
잔차·야코비안은 `c5-factor-graphs-map` 재현 과제의 (15)(16)을 그대로 쓴다.

```python
"""s5-distributed-optimization 재현 과제: 2대 로봇 포즈 그래프 생성기."""

import numpy as np

SEED = 20261112
SIG_ODOM = np.array([0.02, 0.02, 0.01])
SIG_INTER = np.array([0.05, 0.05, 0.02])
SIG_ANCHOR = np.array([1e-3, 1e-3, 1e-3])


def wrap(a):
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def rot(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]])


def between(xi, xj):
    return np.array([*(rot(xi[2]).T @ (xj[:2] - xi[:2])), wrap(xj[2] - xi[2])])


def make_two_robot(n=25, radius=5.0, inter_every=5, seed=SEED):
    """두 로봇이 어긋난 원형 궤적을 돌고, 오도메트리와 로봇 간 측정을 갖는다.

    포즈 인덱스 0..n-1 이 로봇 A, n..2n-1 이 로봇 B 다. 앵커는 A 의 포즈 0 에만 있다.
    """
    rng = np.random.default_rng(seed)
    ang = np.linspace(0.0, 1.6 * np.pi, n)
    gt_a = np.column_stack([radius * np.cos(ang), radius * np.sin(ang), wrap(ang + np.pi / 2)])
    gt_b = np.column_stack(
        [radius * np.cos(ang) + 2.0, radius * np.sin(ang) + 1.0, wrap(ang + np.pi / 2 + 0.3)]
    )
    gt = np.vstack([gt_a, gt_b])
    edges = [(i, i + 1, SIG_ODOM) for i in range(n - 1)]
    edges += [(n + i, n + i + 1, SIG_ODOM) for i in range(n - 1)]
    inter = [(i, n + i, SIG_INTER) for i in range(0, n, inter_every)]
    edges += inter
    meas = [between(gt[i], gt[j]) + s * rng.standard_normal(3) for i, j, s in edges]
    return gt, edges, np.array(meas), n, len(inter)
```

**해야 할 일.** ⓐ `c5-factor-graphs-map` 의 야코비안으로 선형화해 $\Lambda$, $\eta$ 를 만든다
(앵커는 A 의 포즈 0, 가중치 $1/\sigma$). 선형화 지점은 **로봇별 추측 항법**이다 — 각 로봇이
자기 앵커(A 는 참 포즈 0, B 는 참 포즈 $n$)에서 자기 오도메트리만 누적한다. ⓑ 중앙집중 해
$\delta^\ast = \Lambda^{-1}\eta$ 를 구한다. ⓒ 블록 분할은 포즈 인덱스로 $I_1 = \{0..3n-1\}$,
$I_2 = \{3n..6n-1\}$ (상태 차원 $3\cdot2n = 150$).

**Part A — 블록 Gauss-Seidel.** (2)를 4000 라운드 돌려 $\delta^\ast$ 와의
$\lVert\cdot\rVert_\infty$ 오차를 기록한다. 점근 수렴률은 **늦은 구간의 두 점**
($k_1 = 200$, $k_2 = 400$)에서
$\big(\log e_{k_2} - \log e_{k_1}\big)/(k_2-k_1)$ 의 지수로 잰다(너무 늦게 잡으면 기계
정밀도에 묻힌다 — 진단표 참조). 예측값 $\rho(M)$ 과 비교한다.

**Part B — Schur 보완 항등식.** $S = \Lambda_{22}-\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ 를
만들어 $\mathrm{spec}(\Lambda_{22}^{-1}S)$ 를 구하고 (3)을 확인한다.

**Part C — ADMM.** 간선을 소유자별로 나눠 $\Lambda_1, \eta_1$(A 의 오도메트리 + 앵커),
$\Lambda_2, \eta_2$(B 의 오도메트리 + 로봇 간 측정)를 만들고($\Lambda_1+\Lambda_2 = \Lambda$ 를
assert 로 확인), (5)(6)의 ADMM 을 구현한다. $\rho$ 를
`np.geomspace(1.0, 1e5, 41)` 로 쓸어 (6)의 $\rho(T)$ 를 최소화하는 $\rho$ 를 찾고, 그
$\rho$ 와 $\rho=1$, $\rho=10^5$ 에서 3000 반복을 돌린다.

**Part D — 결합 강도와 수렴률.** `inter_every` 를 $2, 5, 10, 25$ 로 바꿔 각각 $\rho(M)$,
로봇 간 간선 수, separator 크기를 구한다.

**수용 기준 — 네 조건을 모두 만족해야 통과다.**

1. **Part A** — 포즈 50개(25+25), 간선 53개(오도메트리 48 + 로봇 간 5), 상태 차원 150,
   $\kappa(\Lambda) = 1.105\times10^{6}$. 예측 $\rho(M) = 0.96860653$ 과 실측이 **상대오차
   $< 10^{-5}$** (참조 실측 $0.96860641$, $1.2\times10^{-7}$). 라운드 수는
   $10^{-2}$:44, $10^{-4}$:186, $10^{-6}$:330, $10^{-8}$:475 이고 4000 라운드 뒤 오차
   $1.5\times10^{-15}$. **중앙집중 해와 $10^{-4}$ 이내로 일치하는 데 186 라운드**가 블루프린트의
   요구를 만족하는 지점이다. 허용오차: 라운드 수 $\pm3$, 오차 자리수.
2. **Part B** — $\Lambda \succ 0$ 과 $S \succ 0$ 을 확인하고,
   $\mathrm{spec}(\Lambda_{22}^{-1}S) \subset (0, 1]$ 이며 $\lambda_{\min} = 0.0313934719$,
   $\lambda_{\max} = 1.0000000000$ (허용오차 $10^{-8}$). 그리고
   $\lvert\rho(M) - (1-\lambda_{\min})\rvert < 10^{-12}$ (참조 $2.0\times10^{-15}$),
   $\min\mathrm{spec}(M) = 0$ (허용오차 $10^{-12}$).
3. **Part C** — $\Lambda_1+\Lambda_2 = \Lambda$ 와 $\eta_1+\eta_2 = \eta$ 가 성립하고,
   격자에서 $\rho(T)$ 의 최소가 $0.979669$ at $\rho = 56.23$ (허용오차 $10^{-5}$ / 1%).
   그 $\rho$ 에서 3000 반복 뒤 오차 $3.1\times10^{-14}$ 이고 $10^{-4}$ 에 377 라운드.
   $\rho = 1$ 과 $\rho = 10^5$ 에서는 예측 $0.999552$, $0.999991$ 이고 3000 반복 뒤 오차가
   $4.4\times10^{-3}$, $1.1\times10^{-1}$ 로 $10^{-4}$ 에 **도달하지 못한다.**
   실측 수렴률은 측정 구간에 따라 $0.9745$(구간 300-600)에서 $0.9814$(구간 900-1500)로
   예측값 $0.979669$ 를 **감싸며** 수렴한다 — 예측과 1% 이내면 통과다.
   그리고 **Gauss-Seidel 이 라운드 수(186 대 377)와 라운드당 통신량(30 대 150 double) 양쪽에서
   이긴다**는 것을 보고한다.
4. **Part D** — 아래 표를 재현한다(허용오차 $10^{-6}$).

   | `inter_every` | 로봇 간 간선 | separator | $\rho(M)$ |
   |---|---|---|---|
   | 2 | 13 | 26 | $0.98968495$ |
   | 5 | 5 | 10 | $0.96860653$ |
   | 10 | 3 | 6 | $0.95420678$ |
   | 25 | 1 | 2 | $0.00466476$ |

   **단조 증가**임을 명시하고, 간선 1개에서 $\rho(M)$ 이 $0.005$ 로 떨어지는 것을 함께 보고한다.

**비교 대상**: ⓐ Part A 의 베이스라인은 중앙집중 해 $\Lambda^{-1}\eta$ 다. ⓑ Part C 의
베이스라인은 Part A 의 Gauss-Seidel 이다 — **ADMM 이 지는 것이 측정 결과**다. ⓒ Part D 의
베이스라인은 `inter_every=5` 행. 선택: 로봇별 추측 항법 대신 참값에서 선형화해 $\rho(M)$ 이
거의 바뀌지 않는 것을 확인하면(결합 구조가 값이 아니라 **구조**로 정해진다는 점) R3' 의
의미가 분명해진다.

**보고할 수치**: 위 네 조건의 모든 값, 그리고 Part A 의 $10^{-4}$ 도달 시점의 총 통신량
(참조 $186 \times 30 = 5580$ double)과 $10^{-6}$ 의 총 통신량(참조 $330 \times 30 = 9900$).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| Part A 의 실측 수렴률이 정확히 $1.0$ | 측정 구간이 너무 늦어 오차가 이미 기계 정밀도다 | 오차 수열을 출력해 $k_1$ 에서 $10^{-8}$ 보다 큰지 확인하고 $k_1 = 200$ 으로 당긴다 |
| Part A 의 실측 수렴률이 예측보다 작다 | 측정 구간이 너무 이르다 — 느린 모드가 아직 지배하지 않는다 | $k_1$ 을 100 에서 400 까지 쓸어 값이 예측으로 수렴하는지 본다 |
| $\Lambda_{11}$ 이 특이해 `solve` 가 실패 | 앵커를 넣지 않았다 — 게이지가 남아 있다 | $\lambda_{\min}(\Lambda)$ 를 출력한다. 0 이면 앵커 누락이다 |
| Part B 에서 $\mathrm{spec}(\Lambda_{22}^{-1}S)$ 가 복소수 | $\Lambda$ 를 비대칭으로 쌓았다 | $\lVert\Lambda-\Lambda^\top\rVert_\infty$ 를 출력한다 |
| Part B 의 $\lambda_{\max}$ 가 1 보다 크다 | $S$ 를 $\Lambda_{11}$ 대신 $\Lambda_{22}$ 에 대해 만들었다 | $S \preceq \Lambda_{22}$ 를 고윳값으로 확인한다 |
| Part C 의 assert 가 실패 | 로봇 간 간선을 양쪽에 중복으로 넣었거나 앵커를 두 번 더했다 | 간선을 소유자별로 **분할**(중복 없이)했는지 확인 |
| Part C 가 $\rho$ 를 키울수록 좋아진다 | $T(\rho)$ 를 틀리게 조립했다(쌍대 갱신 부호) | $\rho = 10^5$ 에서 $\rho(T) \to 1$ 인지 확인한다 |
| Part D 가 단조가 아니다 | `inter_every` 를 바꿀 때 시드를 함께 바꿨다 | 생성기의 `seed` 를 고정하고 `inter_every` 만 바꾼다 |

## 열린 문제

- **(열린 문제) 통신량과 라운드 수를 동시에 줄이는 분할** — R4 의 실측은 두 축이 **같은
  방향으로** 나빠진다는 것을 보여 준다(공유를 늘리면 라운드당 통신량과 라운드 수가 모두
  증가). 그래프 분할 이론은 separator 를 줄이는 쪽만 다루고 수렴률을 목적에 넣지 않는다.
  현재 접근: [분산 SLAM](https://arxiv.org/abs/1702.03435) 의 2단계 분해와 블록 순서 휴리스틱.
  비어 있는 자리: **$\rho(M)$ 과 $\lvert\mathcal{S}\rvert$ 를 동시에 목적에 넣은** 로봇-포즈
  분할 문제의 정식화와 근사비 보장.
- **(열린 문제) 비동기·손실 통신에서의 분산 포즈 그래프** — (2)(9)는 동기 라운드와 무손실
  통신을 가정한다. 비동기 블록 좌표 하강의 수렴 이론은 있으나, 포즈 그래프처럼 **블록이 크고
  결합이 구조적인** 경우의 률은 알려져 있지 않다. 현재 접근: 보수적인 지연 상계 아래의 수렴
  증명과 공학적 재시도. 비어 있는 자리: 지연·손실 분포에서 $\rho(M)$ 에 대응하는 유효 수렴률로
  가는 상계(`s5-comms-constrained-estimation` 과 이어진다).
- **(열린 문제) 프라이버시의 정량화** — "분산이라서 원 데이터를 주지 않는다"는 주장은 separator
  증분을 노출한다는 사실과 공존한다. 여러 라운드의 separator 증분에서 상대의 궤적·관측을
  얼마나 복원할 수 있는지에 대한 정량적 분석이 없다. 현재 접근:
  [privacy·communication 제약](https://arxiv.org/abs/1702.03435) 의 정성적 논의와, 다른 분야의
  차분 프라이버시. 비어 있는 자리: 분산 SLAM 의 통신 내용에 대한 **공격 모델과 누출 상계**.

## 개념 점검

`rc quiz s5-distributed-optimization` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: s5-distributed-optimization-quiz
questions:
  - id: q1
    type: single
    prompt: "2블록 ADMM 의 수렴 정리가 **쓰지 않는** 가정은?"
    choices:
      - "$f_1, f_2$ 가 볼록이다"
      - "$f_1, f_2$ 가 강볼록이고 매끄럽다"
      - "라그랑주가 안점을 가진다"
      - "$f_1, f_2$ 가 닫힌 진 함수다"
    answer: 1
    explanation: "닫힌 진 볼록성과 안점 존재만으로 잔차 $\\to 0$ 과 목적값 수렴이 나온다(`boyd2011-admm` §3.2). 강볼록성·매끄러움은 **필요하지 않고**, 그 대가로 정리가 **수렴률을 주지 않는다**. 률을 말하려면 그 가정들을 추가해야 한다."
    concept: { front: "ADMM 수렴 정리의 가정", back: "닫힌 진 볼록 + 안점 존재면 충분. 강볼록·매끄러움은 불필요하지만 **률은 보장되지 않는다**" }
  - id: q2
    type: short
    prompt: "블록 Gauss-Seidel 의 오차 반복 행렬 $M$ 을 $\\Lambda$ 의 블록으로 쓰면?"
    answer: ["Lambda22^-1 Lambda21 Lambda11^-1 Lambda12", "L22^-1 L21 L11^-1 L12", "Λ22⁻¹Λ21Λ11⁻¹Λ12", "inv(L22) L21 inv(L11) L12"]
    explanation: "(9)에서 $e_2^{k+1} = \\Lambda_{22}^{-1}\\Lambda_{21}\\Lambda_{11}^{-1}\\Lambda_{12}e_2^k$ 다. 두 블록을 번갈아 정확히 최소화한 뒤 최적 조건을 빼면 바로 나온다. 수렴률은 $\\rho(M)$ 이고, Schur 보완으로 $M = I - \\Lambda_{22}^{-1}S$ 로도 쓸 수 있다."
    concept: { front: "블록 Gauss-Seidel 의 반복 행렬", back: "$M = \\Lambda_{22}^{-1}\\Lambda_{21}\\Lambda_{11}^{-1}\\Lambda_{12} = I - \\Lambda_{22}^{-1}S$. 수렴률 $\\rho(M)$" }
  - id: q3
    type: single
    prompt: "$\\Lambda \\succ 0$ 이면 블록 Gauss-Seidel 이 항상 수렴하는 이유는?"
    choices:
      - "$M$ 이 대칭이기 때문"
      - "$M = I - \\Lambda_{22}^{-1}S$ 이고 $S \\succ 0$, $S \\preceq \\Lambda_{22}$ 이므로 $\\mathrm{spec}(M) \\subset [0,1)$ 이기 때문"
      - "$\\Lambda_{12}$ 가 희소하기 때문"
      - "목적함수가 매 라운드 감소하기 때문(그것만으로 충분)"
    answer: 1
    explanation: "Schur 보완 $S$ 가 양정부호이고($\\Lambda\\succ0$ 에서) $\\Lambda_{21}\\Lambda_{11}^{-1}\\Lambda_{12}\\succeq0$ 이므로 $S\\preceq\\Lambda_{22}$ 다. 따라서 $\\mathrm{spec}(\\Lambda_{22}^{-1}S)\\subset(0,1]$ 이고 $\\mathrm{spec}(M)\\subset[0,1)$ 이다. 목적함수의 단조 감소만으로는 **률**도 수렴도 보장되지 않는다(정체할 수 있다)."
    concept: { front: "블록 Gauss-Seidel 의 무조건 수렴", back: "$M = I-\\Lambda_{22}^{-1}S$, $0 \\prec S \\preceq \\Lambda_{22}$ $\\Rightarrow$ $\\mathrm{spec}(M)\\subset[0,1)$. $\\rho(M)=1-\\lambda_{\\min}(\\Lambda_{22}^{-1}S)$" }
  - id: q4
    type: truefalse
    prompt: "로봇 간 측정을 더 많이 공유하면 분산 포즈 그래프 최적화의 수렴이 빨라진다."
    answer: false
    explanation: "반대다. 공유를 늘리면 $\\Lambda_{12}$ 가 커져 $S$ 가 작아지고 $\\rho(M) = 1-\\lambda_{\\min}(\\Lambda_{22}^{-1}S)$ 가 1 에 가까워진다. 재현 과제의 실측: 로봇 간 간선 $1 \\to 3 \\to 5 \\to 13$ 에서 $\\rho(M)$ 이 $0.0047 \\to 0.954 \\to 0.969 \\to 0.990$ 으로 커진다. 정확도는 올라가지만 라운드 수와 라운드당 통신량이 **둘 다** 늘어난다."
    concept: { front: "공유량과 수렴률의 교환", back: "공유를 늘리면 정확도는 올라가지만 $\\rho(M)$ 이 1 에 가까워진다 — 라운드 수와 라운드당 통신량이 같은 방향으로 나빠진다" }
  - id: q5
    type: single
    prompt: "분산 최적화가 중앙집중 해로 수렴했다는 것이 보장하는 것은?"
    choices:
      - "원 비볼록 문제의 전역 최솟값에 도달했다"
      - "선형화된 2차 문제의 유일한 해에 도달했을 뿐이고, 전역 최적성은 별도의 인증이 필요하다"
      - "모든 로봇이 같은 정보를 갖게 되었다"
      - "통신량이 최소였다"
    answer: 1
    explanation: "(2)(3)은 **선형화된** 문제에 대한 진술이다. $SE(d)$ 위 원 문제의 전역 최적성은 `c5-robust-global-estimation` R3 의 쌍대 인증이 필요하고, 그 인증을 분산으로 하는 것은 또 다른 문제다(`tian2021-distributed-certifiable`). 논문이 'distributed'와 'certifiably correct'를 같이 쓸 때 어느 쪽을 주장하는지 확인해야 한다."
    concept: { front: "분산 수렴 vs 전역 최적성", back: "분산 수렴 = 선형화 문제의 해. 전역 최적성은 별도 인증($S\\succeq0$)이고 그 인증의 분산화도 별도 문제" }
```

## 이 단계 공부법

1. **(4)에서 (1)을 손으로 유도한다 (45분)** — 제곱 완성 한 줄로 $w = y/\rho$ 꼴이 나오는 것을
   직접 확인한다. ADMM 이 "번갈아 최소화 + 쌍대 상승"이라는 구조가 보이면 된다.
2. **(9)를 백지에서 (30분)** — (8)에서 최적 조건을 빼는 세 줄이다. 이 레슨에서 가장 짧고 가장
   많이 쓰는 유도다.
3. **R3' 의 네 줄을 외운다 (45분)** — $M = I - \Lambda_{22}^{-1}S$ 한 줄과 부등식 두 개
   ($S\succ0$, $S\preceq\Lambda_{22}$)가 전부다. `c5-factor-graphs-map` 문제 P2 를 다시 풀어
   $S\succ0$ 을 자기 손에 넣어 두면 이 레슨이 쉬워진다.
4. **Part A·B 를 먼저 돌린다 (60분)** — 실측 수렴률이 예측과 $10^{-7}$ 로 맞는 것을 보고,
   그 다음 Part B 에서 $1-\lambda_{\min}$ 이 같은 값인 것을 본다. 두 경로가 같은 숫자를
   주는 순간이 R3' 를 이해한 증거다.
5. **Part D 로 교환을 본다 (30분)** — 간선 1개에서 $\rho(M) = 0.005$, 13개에서 $0.990$ 인
   표를 직접 찍는다. "더 공유하면 더 느리다"는 결론이 반직관적이므로 수치로 못 박는다.
6. **Part C 를 마지막에 (60분)** — ADMM 의 $T(\rho)$ 를 조립하고 $\rho$ 를 쓸어 최적을 찾는다.
   $\rho=1$ 과 $\rho=10^5$ 에서 둘 다 느린 것을 보고 내부 최소를 확인한다. 그리고 ADMM 이
   Gauss-Seidel 에 **두 축 모두에서 지는** 것을 보고서에 쓴다.
7. **논문은 "무엇을 분산으로 하는가"로 읽는다 (150분)** — Boyd et al. §3.2 로 가정을 정확히
   확인하고 §7 로 consensus 형태를 보고, Choudhary et al. IV-V 로 실제 분산 SLAM 의 분해를
   보고, Tian et al. III-V 로 **인증의 분산화**가 무엇인지 본다. 논문당 1페이지 노트는
   **반드시** 쓴다.
8. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제" 세 개 중 하나를 골라 한 문단으로 쓴다.
   통신량과 라운드 수를 함께 목적에 넣는 분할 문제는 Part D 의 표가 바로 동기다.

**통과 기준**: 백지에서 (1)(9)와 R3' 의 네 줄을 유도할 수 있고, $\rho(M)$ 과
$1-\lambda_{\min}(\Lambda_{22}^{-1}S)$ 가 같은 이유를 쓸 수 있고, 재현 과제의 네 조건을 모두
만족하는 코드를 갖고 있고, 논문 3편의 노트가 있다.
