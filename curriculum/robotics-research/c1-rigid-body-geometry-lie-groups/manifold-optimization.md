---
id: c1-manifold-optimization
title: 매니폴드 위 최적화 — 재추적과 Gauss–Newton
summary: >-
  리 군 위의 최적화를 lift-solve-retract 로 정식화하고, 재추적 기반 Gauss–Newton 의 국소 수렴을
  증명 수준에서 다룬다. 과매개화 + 정규화 방식이 왜 특이한 정규방정식을 만드는지, 그리고 포즈
  그래프의 게이지 자유도가 정보행렬의 영공간으로 나타나는 것까지 간다.
objectives:
  - 재추적(retraction)의 조건을 쓰고 지수 사상이 그 조건을 만족함을 확인할 수 있다.
  - lift-solve-retract 가 리만 기울기와 1차에서 일치함을 유도할 수 있다.
  - 재추적 기반 Gauss–Newton 의 국소 수렴률을 잔차 크기와 함께 증명 스케치로 재구성할 수 있다.
  - 과매개화 + 정규화 방식의 정규방정식이 왜 랭크 부족인지 보이고 국소 매개화와 비교할 수 있다.
  - 포즈 그래프의 게이지 자유도가 정보행렬의 영공간 차원으로 나타나는 것을 설명할 수 있다.
prerequisites: [c1-poe-analytic-ik]
difficulty: 5
estimated_minutes: 480
tags: [lie-groups, optimization, gauss-newton, retraction, gauge-freedom, research]
activities:
  - id: c1-manifold-optimization-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c1-manifold-optimization-papers
    kind: paper
    title: 필독 논문 2편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 110
  - id: c1-manifold-optimization-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 150
  - id: c1-manifold-optimization-reproduction
    kind: reproduction
    title: 재현 과제 — SE(3) 포즈 정합, 매니폴드 GN 대 과매개화 (R2)
    estimated_minutes: 120
  - id: c1-manifold-optimization-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.7-8. 매니폴드 위 Gauss-Newton 과 리 군 추정의 표준 서술.
  - title: "Nocedal & Wright, Numerical Optimization (2nd ed.)"
    kind: book
    note: ch.10 (Least-Squares Problems). 유클리드 Gauss-Newton 의 수렴 분석. (공식 URL 미확인)
  - title: "GTSAM"
    url: https://github.com/borglab/gtsam
    kind: code
    note: 재추적 기반 최적화와 게이지 처리(prior factor)의 참조 구현. 재현 과제의 비교 대상.
papers:
  - id: absil2008-manifold-opt
    required: true
    role: standard
    note: "ch.4, ch.7"
  - id: dellaert2017-factor-graphs
    required: true
    role: survey
    note: "§3-4"
---

# 매니폴드 위 최적화 — 재추적과 Gauss–Newton

## 전제와 기호

앞 네 레슨의 표기를 쓴다. 특히 `c1-lie-group-derivatives` 의 $\oplus$, $\ominus$, $J_r$ 가 이
레슨의 도구다. 추가 기호:

| 기호 | 뜻 |
|---|---|
| $\mathcal{M}$ | 매끄러운 다양체. 이 레슨에서는 $SO(3)$, $SE(3)$, 또는 그 곱 |
| $T_X\mathcal{M}$ | 점 $X$ 에서의 접공간 |
| $\mathrm{R}_X : T_X\mathcal{M} \to \mathcal{M}$ | 점 $X$ 의 **재추적(retraction)** |
| $X \oplus \delta := X\,\mathrm{Exp}(\delta)$ | 이 레슨이 쓰는 재추적(우 증분) |
| $f : \mathcal{M} \to \mathbb{R}$ | 목적함수. 최소제곱 형태 $f(X) = \tfrac12\sum_k \lVert e_k(X)\rVert^2_{\Sigma_k}$ |
| $J_k$ | 잔차 $e_k$ 의 **접공간에 대한** 야코비안 ($\partial e_k(X\oplus\delta)/\partial\delta|_0$) |
| $\Lambda = J^\top \Sigma^{-1} J$ | 정보행렬(information matrix) |

**재추적의 조건**: $\mathrm{R}_X(0) = X$ 이고 $\mathrm{D}\mathrm{R}_X(0) = \mathrm{id}$
(국소 강성, local rigidity). 즉 원점에서 1차로 접공간과 일치하면 된다 — **측지선일 필요는 없다.**
$\mathrm{Exp}$ 는 이 조건을 만족하고(앞 레슨 R1 의 $J_r(0)=I$), 4원수 정규화
$q \mapsto (q+\delta)/\lVert q+\delta\rVert$ 도 만족한다. 둘 다 재추적이지만 성질이 다르다 — §3.

## 핵심 결과

- **R1 (lift-solve-retract) [D2]** — 매니폴드 위 최적화는 세 단계의 반복이다:

$$
\text{(lift)}\ \ \tilde{f}_X(\delta) := f(X \oplus \delta), \qquad
\text{(solve)}\ \ \delta^\star = \arg\min_\delta \tilde{f}_X(\delta), \qquad
\text{(retract)}\ \ X \leftarrow X \oplus \delta^\star. \tag{1}
$$

  $\tilde{f}_X$ 는 **유클리드 공간의 함수**이므로 보통의 미적분을 쓸 수 있고,
  $\nabla\tilde{f}_X(0)$ 가 리만 기울기와 1차에서 일치한다.
- **R2 (매니폴드 Gauss–Newton) [D2]** — 잔차를 1차로 전개하면 정규방정식은

$$
\Big(\underbrace{\sum_k J_k^\top \Sigma_k^{-1} J_k}_{\Lambda}\Big)\delta
= -\sum_k J_k^\top \Sigma_k^{-1} e_k(X), \tag{2}
$$

  여기서 $J_k$ 는 **접공간에 대한** 야코비안이다. 차원은 매니폴드의 차원과 같다
  ($SE(3)$ 하나당 6, 4원수 과매개화의 7이 아니다).
- **R3 (국소 수렴) [D3]** — $X^\star$ 가 국소 최소이고 $\Lambda(X^\star)$ 가 양정이면, 재추적 기반
  Gauss–Newton 은 $X^\star$ 의 어떤 근방에서 **선형 수렴**하며 수렴률은 잔차의 크기에 비례한다:

$$
\lVert \delta_{i+1} \rVert \le c_1 \lVert r^\star \rVert\,\lVert \delta_i \rVert
+ c_2 \lVert \delta_i \rVert^2. \tag{3}
$$

  잔차가 0 인 문제($r^\star = 0$)에서는 **2차 수렴**이 된다. 재추적이 측지선이 아니어도 결론은
  같다 — 국소 강성만 쓰기 때문이다.
- **R4 (과매개화 + 정규화는 랭크 부족을 만든다) [D2]** — 4원수를 7개 자유 변수로 두고
  $\lVert q \rVert = 1$ 을 벌점/정규화로 처리하면, 정규방정식의 계수행렬이 $q$ 방향으로
  **영공간을 갖는다**: 그 방향의 섭동은 회전을 바꾸지 않으므로 모든 잔차의 야코비안이 0 이다.
  따라서 감쇠(damping) 없이는 풀 수 없고, 감쇠는 수렴률을 떨어뜨린다. 국소 매개화는 이 방향을
  애초에 만들지 않는다.
- **R5 (게이지 자유도) [D2]** — 상대 측정만으로 이루어진 포즈 그래프에서 $\Lambda$ 는
  **$\dim SE(3) = 6$ 차원의 영공간**을 갖는다(전체 궤적을 강체 변환해도 모든 잔차가 불변).
  해를 유일하게 만들려면 한 포즈를 고정하거나 prior 를 더한다. 단안 시각 문제에서는 척도까지
  불관측이라 7차원이 된다.

## 유도

### R1 — lift-solve-retract 와 1차 동등성

$X \in \mathcal{M}$ 을 고정하고 $\tilde{f}_X(\delta) = f(X \oplus \delta)$ 로 **들어올린다(lift)**.
$\delta \in \mathbb{R}^n$ 이므로 $\tilde{f}_X$ 는 보통의 다변수 함수다. 재추적 조건
$\mathrm{R}_X(0)=X$, $\mathrm{D}\mathrm{R}_X(0)=\mathrm{id}$ 에서

$$
\tilde{f}_X(\delta) = f(X) + \nabla\tilde{f}_X(0)^\top\delta + O(\lVert\delta\rVert^2),
\qquad \nabla\tilde{f}_X(0) = \mathrm{grad}\,f(X)
$$

이다 — **1차에서는 어떤 재추적을 쓰든 같은 기울기가 나온다.** 이것이 "측지선을 쓰지 않아도 된다"는
R2·R3 의 근거다. 2차 항부터는 재추적에 의존하므로, 2차 방법(Newton)에서는 재추적의 2차 성질이
수렴 상수에 들어간다(§R5 의 2차 재추적).

**주의**: $\delta$ 는 **매번 새 좌표**다. 반복마다 $X$ 가 바뀌므로 $\delta_i$ 들을 더하거나 비교하면
안 된다. 수렴 판정은 $\lVert\delta_i\rVert$ 로 하고, 누적은 $\oplus$ 로만 한다. 이 규칙을 어기는
것이 매니폴드 최적화에서 가장 흔한 버그다.

### R2 — 접공간 야코비안과 정규방정식

잔차 $e_k(X \oplus \delta)$ 를 $\delta$ 로 1차 전개한다:

$$
e_k(X \oplus \delta) \approx e_k(X) + J_k\delta, \qquad
J_k := \left.\frac{\partial e_k(X \oplus \delta)}{\partial \delta}\right|_{\delta = 0}.
$$

$\tilde{f}_X(\delta) \approx \tfrac12\sum_k \lVert e_k(X) + J_k\delta\rVert^2_{\Sigma_k}$ 를
$\delta$ 로 미분해 0 으로 두면 (2)다. 유클리드 Gauss–Newton 과 **형태가 같고**, 다른 것은
$J_k$ 가 접공간에 대한 미분이라는 점뿐이다. 그래서 희소 Cholesky·Schur 보완 같은 선형대수
기법이 그대로 재사용된다(`c5-sparsity-isam`).

**$J_k$ 를 실제로 구하는 법**: 잔차가 $e(X) = \mathrm{Log}(Z^{-1}X)$ 꼴이면
$e(X\oplus\delta) = \mathrm{Log}(Z^{-1}X\,\mathrm{Exp}(\delta))$ 이고, 앞 레슨 R4 의 BCH 1차 항에서

$$
e(X \oplus \delta) \approx e(X) + J_r^{-1}\big(e(X)\big)\,\delta
\;\;\Longrightarrow\;\; J = J_r^{-1}\big(e(X)\big). \tag{4}
$$

**앞 레슨의 $J_r^{-1}$ 이 여기서 쓰인다.** 이것을 $I$ 로 두면(즉 야코비안을 유클리드로 계산하면)
작은 오차에서는 돌아가지만 오차가 커질수록 수렴이 느려지고, 공분산이 틀린다.

### R4 — 과매개화가 만드는 영공간

회전을 단위 4원수 $q \in \mathbb{R}^4$ 로 두고 제약 $\lVert q\rVert = 1$ 을 벌점항
$\tfrac{\mu}{2}(\lVert q\rVert^2-1)^2$ 로 처리한다고 하자. 잔차는 회전 $R(q)$ 를 통해서만
$q$ 에 의존하고, $R(sq) = R(q)$ (동차성)이므로 방향 $q$ 자체의 섭동은 회전을 바꾸지 않는다:

$$
\left.\frac{\partial e_k(R(q + t q))}{\partial t}\right|_{t=0} = 0 \quad \text{for all } k .
$$

따라서 데이터 항의 계수행렬 $\sum_k J_k^\top\Sigma_k^{-1}J_k$ 는 $q$ 를 **영벡터로 갖는다**.
벌점항만이 그 방향에 곡률을 주는데, 그 곡률은 $\mu$ 에 비례하므로

- $\mu$ 가 작으면 그 방향이 거의 평평해 정규방정식이 악조건이 되고,
- $\mu$ 가 크면 데이터 항과 스케일이 어긋나 다른 방향의 수렴이 느려진다.

국소 매개화($SO(3)$ 당 3변수, $SE(3)$ 당 6변수)는 이 방향을 **애초에 좌표에서 제거**하므로
감쇠도 벌점도 필요 없다. 이것이 재현 과제에서 반복 수 차이로 나타난다.

**혼동하지 말 것**: R4 의 영공간은 **과매개화가 만든 인공적인 것**이고, R5 의 게이지 영공간은
**문제 자체의 성질**이다. 전자는 좌표를 바꿔 없앨 수 있고, 후자는 측정을 더하거나 기준을 고정해야
없어진다. 둘을 같은 감쇠로 덮으면 "왜 수렴이 느린가"를 영원히 모른다.

## 증명 스케치

### R3 — 재추적 기반 Gauss–Newton 의 국소 수렴

**가설** H1: $f(X) = \tfrac12\sum_k\lVert e_k(X)\rVert^2$, 각 $e_k$ 는 $C^2$.
H2: $X^\star$ 는 국소 최소이고 $\Lambda^\star := J^{\star\top}J^\star$ 가 양정.
H3: $\mathrm{R}$ 은 재추적($\mathrm{R}_X(0)=X$, $\mathrm{D}\mathrm{R}_X(0)=\mathrm{id}$).
**결론** C: (3), 즉 $X^\star$ 의 근방에서 선형 수렴하고 $r^\star=0$ 이면 2차 수렴.

**전략**: 들어올린 함수에 유클리드 Gauss–Newton 의 고전적 분석을 적용하고, 매니폴드 쪽 오차를
재추적의 국소 강성으로 흡수한다. 즉 **새 정리를 만들지 않고 좌표를 바꿔 기존 정리를 쓴다.**

1. **좌표 고정.** $X^\star$ 근방에서 $\varepsilon := X \ominus X^\star$ 를 오차 좌표로 쓴다.
   H3 에 의해 $\varepsilon \mapsto X$ 는 0 근방에서 미분동형이고 $\mathrm{D}=\mathrm{id}$ 다.
2. **들어올린 문제.** $g(\varepsilon) := f(X^\star \oplus \varepsilon)$ 는 $\mathbb{R}^n$ 의
   $C^2$ 함수이고 $\nabla g(0)=0$, $\nabla^2 g(0) = \Lambda^\star + \sum_k e_k^\star \nabla^2 e_k^\star$.
   두 번째 항이 **잔차 항**이고 (3)의 $c_1\lVert r^\star\rVert$ 를 만든다.
3. **고전 결과 인용.** 유클리드 Gauss–Newton 의 국소 수렴 정리(Nocedal–Wright ch.10)를 $g$ 에
   적용하면 $\lVert\varepsilon_{i+1}\rVert \le \tilde{c}_1\lVert r^\star\rVert\lVert\varepsilon_i\rVert
   + \tilde{c}_2\lVert\varepsilon_i\rVert^2$. (생략: 그 정리의 증명 — Nocedal–Wright 정리 10.1.)
4. **재추적 오차 흡수.** 실제 알고리즘은 $\varepsilon$ 좌표가 아니라 매 반복 $X_i$ 에서 새로
   들어올린다. 두 좌표의 차이는 $O(\lVert\delta_i\rVert^2)$ 이고(H3 의 1차 일치), 그 항은 3단계의
   $\tilde{c}_2\lVert\varepsilon_i\rVert^2$ 에 흡수된다. 상수만 커지고 **차수는 바뀌지 않는다.**
5. **결론.** $\lVert\delta_i\rVert$ 와 $\lVert\varepsilon_i\rVert$ 가 0 근방에서 동치이므로 C.

**가설을 지우면**: H2 에서 $\Lambda^\star$ 의 양정성을 빼면(= R5 의 게이지 자유도가 있는 경우)
해가 유일하지 않고 반복이 영공간 방향으로 떠다닌다 — 수렴 판정이 $\lVert\delta\rVert$ 로는
내려가지만 해는 매번 다르다. 그래서 게이지를 고정하는 것이 **수렴의 전제**다.
H3 의 국소 강성을 빼면 1단계의 미분동형이 깨져 분석 자체가 성립하지 않는다.

## 문제 세트

★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R2)** 잔차 $e(X) = \mathrm{Log}(Z^{-1}X)$ 에 대해 (4)를 유도하라.
$X \oplus \delta$ 를 넣고 앞 레슨의 BCH 1차 항을 쓰면 된다. $J = J_r^{-1}(e(X))$ 가 $e(X)$ 에
의존한다는 점(상수가 아니다)이 왜 중요한가?
*해답 스케치*: $\mathrm{Log}(Z^{-1}X\mathrm{Exp}(\delta)) = \mathrm{Log}(\mathrm{Exp}(e)\mathrm{Exp}(\delta))
= e + J_r^{-1}(e)\delta + O(\lVert\delta\rVert^2)$. 야코비안이 현재 오차에 의존하므로 **매 반복
재계산**해야 하고, 오차가 크면 $J_r^{-1}$ 이 $I$ 에서 멀어진다(앞 레슨: $\theta\to\pi$ 에서 발산).

**P2 (유도, ★★, R5)** 상대 포즈 측정만 있는 포즈 그래프에서 $\Lambda$ 의 영공간 차원이 6 임을
보이고, 그 영공간의 기저를 적어라. 단안 시각 문제에서 7 이 되는 이유도 쓰라.
*해답 스케치*: 모든 포즈에 같은 $T \in SE(3)$ 를 왼쪽에서 곱하면 상대 측정
$T_i^{-1}T_j$ 가 불변이다. 그 변환의 1-매개변수 군 6개가 영공간의 기저를 준다. 단안에서는
전체 척도를 바꿔도 재투영 잔차가 불변이므로 방향이 하나 더 생긴다.

**P3 (증명, ★★★, R3)** R3 의 4단계("재추적 오차가 2차 항에 흡수된다")를 정확히 쓰라.
$\mathrm{R}$ 이 측지선(= $\mathrm{Exp}$)일 때와 4원수 정규화일 때 상수 $\tilde{c}_2$ 가 어떻게
달라지는지 비교하라.
*해답 스케치*: 두 재추적의 차이는 2차 항에서 처음 나타난다 — Taylor 전개의 2차 항을 비교하면
$\mathrm{Exp}$ 는 $J_r$ 의 2차 항을, 정규화는 $-\tfrac12 q(\delta^\top\delta)$ 꼴의 항을 준다.
차수는 같고 상수만 다르다.

**P4 (계산, ★, R4)** 회전 하나와 측정 하나($e = \mathrm{Log}(Z^{-1}R)$)만 있는 문제에서,
4원수 과매개화 + 벌점 $\mu$ 로 세운 $4\times4$ 계수행렬의 고윳값을 $\mu$ 의 함수로 구하라
($R = Z$, 즉 해에서).
*정답*: 해에서 $e=0$ 이므로 데이터 항은 $J^\top J$ 이고, 그 랭크는 3(접공간 차원)이며 $q$ 방향이
영벡터다. 벌점항의 Hessian 은 해($\lVert q\rVert=1$)에서 $2\mu\,qq^\top$ 이므로 고윳값은
데이터 항의 3개 양수와 **$2\mu$** 하나다. 조건수는 $\mu \to 0$ 에서 발산한다. 허용오차 $10^{-9}$.

**P5 (구현, ★★, R1·R2)** `gn_manifold(X0, residuals, jacobians)` 를 쓰라. 매 반복 ⓐ 접공간
야코비안으로 (2)를 세우고 ⓑ $\delta$ 를 풀고 ⓒ $X \leftarrow X \oplus \delta$ 로 재추적한다.
*루브릭*: ⓐ $\delta_i$ 를 누적하거나 비교하지 않는다(새 좌표임을 코드가 반영) ⓑ 수렴 판정이
$\lVert\delta\rVert$ 와 비용 감소 **둘 다**를 본다 ⓒ $J$ 를 매 반복 재계산한다 ⓓ 게이지가 있는
문제에서 prior 또는 고정을 요구하고, 없으면 명시적으로 거부한다(조용히 감쇠로 덮지 않는다).

**P6 (반례, ★★, R4·R5)** 감쇠(Levenberg–Marquardt)가 **두 종류의 영공간을 모두 덮어 버려**
진단을 불가능하게 만드는 예를 구성하라. 과매개화 영공간과 게이지 영공간을 구분해 보이는
진단 절차를 제시하라.
*성질 체크리스트*: 진단은 **감쇠 없는** 계수행렬의 수치 랭크와 영공간 기저를 보는 것이다.
과매개화 영벡터는 $q$ 방향(변수 하나당 1차원), 게이지 영벡터는 **모든 포즈에 걸친** 전역 방향
(6차원)이다 — 기저 벡터의 지지(support)가 국소인지 전역인지로 갈린다.

## 논문 읽기

**필독 2편.** 고정 질문 10개(레슨 표준 §5)로 논문당 1페이지 노트를 쓴다.

1. **Absil, Mahony & Sepulchre, *Optimization Algorithms on Matrix Manifolds* (2008)** —
   역할: `표준(standard)`. <https://doi.org/10.1515/9781400830244> (ch.4 와 ch.7)
   추가 질문: ⓐ 저자들의 재추적 정의를 이 레슨의 조건과 대조하라 — 무엇이 더 약하거나 강한가?
   ⓑ 측지선 대신 임의 재추적을 쓰는 것이 수렴 **차수**에 영향을 주지 않는 이유를 저자들의
   논증으로 쓰라. ⓒ 신뢰영역(trust-region) 버전이 선탐색 버전보다 나은 상황은?
2. **Dellaert & Kaess, "Factor Graphs for Robot Perception" (2017, FnT Robotics)** —
   역할: `서베이(survey)`. <https://doi.org/10.1561/2300000043> (§3–4)
   추가 질문: ⓐ 이 글이 (2)의 희소 구조를 어떻게 활용하는지 한 문단으로 요약하라.
   ⓑ 게이지 자유도를 실제 시스템에서 어떻게 처리한다고 쓰는가(고정? prior? 둘의 차이는?)
   ⓒ 접공간 야코비안을 쓰지 않으면 어느 식이 틀리는가?

## 재현 과제

**티어 R2 (알고리즘 재구현).** 예산: 노트북 CPU 5분 이내, numpy/scipy 만.

**문제**: $SE(3)$ 포즈 정합. 참 변환 $T^\star$ 로 만든 점 대응 $\{(a_i, b_i)\}$($b_i = T^\star a_i +
\text{노이즈}$, $N=200$)에서 $T$ 를 추정한다. 잔차 $e_i(T) = T a_i - b_i$.

1. **매니폴드 GN**: 접공간 야코비안($6$ 열)으로 (2)를 풀고 $T \leftarrow T\,\mathrm{Exp}(\delta)$ 로
   재추적. 노이즈 $\sigma = 0.01$ 에서 **10회 이내 반복**으로 $\lVert\delta\rVert < 10^{-10}$ 수렴.
2. **과매개화 비교**: 같은 문제를 4원수 7변수 + 벌점 $\mu$ 로 풀고, $\mu \in \{10^{-2}, 1, 10^2\}$
   각각의 반복 수를 보고하라. **어떤 $\mu$ 에서도 매니폴드 GN 보다 반복이 적지 않아야** 한다.
   추가로 감쇠 없는 계수행렬의 최소 고윳값을 두 방식에서 비교해 과매개화 쪽이 0 에 가까운 것을 보여라.
3. **야코비안 정확성**: 접공간 야코비안이 중심 유한차분과 $10^{-7}$ 이내로 일치.
   **$J$ 를 $I$ 로 근사한 버전**(즉 $J_r^{-1}$ 을 무시)도 돌려, 초기 오차가 클 때 반복 수가
   늘어나는 것을 표로 보고하라(초기 회전 오차 $0.1, 0.5, 1.5\,\mathrm{rad}$).
4. **게이지 진단**: 포즈 2개와 그 사이 상대 측정 1개만 있는 문제를 만들고, 감쇠 없는 $\Lambda$ 의
   수치 랭크가 $12 - 6 = 6$ 임을 확인하라. prior 를 하나 더한 뒤 랭크가 12 로 회복되는 것을 보여라.

**비교 대상**: 닫힌 해가 있는 경우(점 대응 정합)에는 Umeyama/Kabsch 해법과 매니폴드 GN 의 해가
$10^{-9}$ 이내로 일치해야 한다. GTSAM 을 설치할 수 있으면 같은 문제를 던져 반복 수를 비교하라(선택).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 초기 오차가 크면 수렴이 느리다 | $J$ 에서 $J_r^{-1}$ 을 생략했다 | 조건 3 의 $J=I$ 버전과 반복 수를 비교 |
| 비용은 줄지만 해가 매번 다르다 | 게이지 영공간(R5) — 기준이 고정되지 않았다 | 감쇠 없는 $\Lambda$ 의 수치 랭크와 영공간 기저의 지지를 본다 |
| 감쇠를 키워야 돌아간다 | 과매개화 영공간(R4)을 감쇠로 덮고 있다 | 국소 매개화로 바꿔 감쇠 없이 되는지 확인 |
| $\delta$ 가 줄지 않고 진동한다 | $\delta_i$ 를 누적했거나 재추적을 빼먹었다 | 반복마다 $X$ 가 실제로 갱신되는지, $J$ 를 재계산하는지 확인 |

## 열린 문제

- **(열린 문제) 전역 최적성 인증의 범위** — 매니폴드 GN 은 국소 방법이다. 포즈 그래프에서는
  쌍대 완화가 타이트한 조건이 알려졌지만(`c5-robust-global-estimation` 의
  [SE-Sync](https://arxiv.org/abs/1612.07386)), 일반적인 매니폴드 최소제곱으로 확장되지 않았다.
  어떤 문제 구조가 인증 가능한지의 분류가 비어 있다.
- **(열린 문제) 비매끄러운 매니폴드 최적화** — 강건 비용(Huber, truncated)과 접촉·조합 구조가
  들어오면 목적함수가 비매끄럽다. 매니폴드 위 비매끄러운 최적화의 수렴 이론은 유클리드만큼
  정리되지 않았고, 로보틱스가 쓰는 IRLS·그래프 중복 제거는 대부분 경험적이다.
- **(열린 문제) 매니폴드 위 전처리(preconditioning)** — 희소 구조를 살린 전처리 기법은
  유클리드 쪽에서 성숙했지만, 접공간이 매 반복 바뀌는 상황에서 전처리기를 **재사용**하는
  원리적 방법이 부족하다. 대규모 번들 조정(`c7-bundle-adjustment`)의 실질적 병목이다.

## 개념 점검

`rc quiz c1-manifold-optimization` 로 푼다. 개념 점검 전용이고 실제 과제는 문제 세트와 재현 과제다.

```quiz
activity: c1-manifold-optimization-quiz
questions:
  - id: q1
    type: multiple
    prompt: "재추적(retraction)이 만족해야 하는 조건을 모두 고르라."
    choices:
      - "$\\mathrm{R}_X(0) = X$"
      - "$\\mathrm{D}\\mathrm{R}_X(0) = \\mathrm{id}$ (국소 강성)"
      - "측지선이어야 한다"
      - "전역 전단사여야 한다"
    answer: [0, 1]
    explanation: "재추적은 원점에서 값과 1차 미분만 맞으면 된다. 측지선일 필요도, 전역 전단사일 필요도 없다 — 그래서 4원수 정규화도 재추적이고, 수렴 **차수**는 재추적 선택에 영향받지 않는다(상수만 달라진다)."
    concept: { front: "재추적의 조건", back: "$\\mathrm{R}_X(0)=X$ 와 $\\mathrm{D}\\mathrm{R}_X(0)=\\mathrm{id}$ 뿐. 측지선·전역 전단사는 불필요" }
  - id: q2
    type: single
    prompt: "잔차 $e(X) = \\mathrm{Log}(Z^{-1}X)$ 의 접공간 야코비안은?"
    choices:
      - "$I$ (항등)"
      - "$J_r^{-1}(e(X))$"
      - "$J_l(e(X))$"
      - "$\\mathrm{Ad}_X$"
    answer: 1
    explanation: "$\\mathrm{Log}(\\mathrm{Exp}(e)\\mathrm{Exp}(\\delta)) = e + J_r^{-1}(e)\\delta + O(\\lVert\\delta\\rVert^2)$ (BCH 1차 항)이므로 $J = J_r^{-1}(e(X))$ 다. **현재 오차에 의존**하므로 매 반복 재계산해야 하고, $I$ 로 근사하면 오차가 클 때 수렴이 느려진다."
    concept: { front: "$\\mathrm{Log}(Z^{-1}X)$ 잔차의 접공간 야코비안", back: "$J_r^{-1}(e(X))$ — 현재 오차에 의존하므로 매 반복 재계산한다" }
  - id: q3
    type: truefalse
    prompt: "4원수를 7변수로 두고 정규화를 벌점으로 처리하면, 정규방정식의 데이터 항이 $q$ 방향으로 영공간을 갖는다."
    answer: true
    explanation: "$R(sq) = R(q)$ 이므로 $q$ 방향 섭동은 회전을 바꾸지 않고, 따라서 모든 잔차의 야코비안이 그 방향으로 0 이다. 벌점항만 곡률을 주므로 $\\mu$ 가 작으면 악조건, 크면 다른 방향이 느려진다. 국소 매개화는 이 방향을 애초에 만들지 않는다."
    concept: { front: "과매개화 + 벌점 방식의 문제", back: "데이터 항이 $q$ 방향 영공간을 가져 감쇠/벌점 없이 못 푼다. 국소 매개화는 그 방향을 좌표에서 제거한다" }
  - id: q4
    type: single
    prompt: "상대 측정만으로 이루어진 $SE(3)$ 포즈 그래프에서 정보행렬 $\\Lambda$ 의 영공간 차원은?"
    choices: ["0", "3", "6", "포즈 개수에 비례"]
    answer: 2
    explanation: "전체 궤적을 같은 강체 변환으로 옮겨도 모든 상대 측정이 불변이므로 $\\dim SE(3) = 6$ 차원의 게이지 자유도가 남는다. 한 포즈를 고정하거나 prior 를 더해야 해가 유일해진다. 단안 시각에서는 척도까지 불관측이라 7 이 된다."
    concept: { front: "포즈 그래프의 게이지 영공간 차원", back: "$SE(3)$ 상대 측정만이면 6 (단안 시각은 척도까지 더해 7). 고정이나 prior 로 없앤다" }
```

## 이 단계 공부법

1. **"매번 새 좌표"를 먼저 새긴다 (20분)** — $\delta_i$ 는 반복마다 다른 좌표계의 벡터다. 더하지도
   비교하지도 않는다. 이 한 줄을 놓치면 구현이 조용히 틀린다.
2. **(2)가 유클리드와 같은 형태임을 확인한다 (40분)** — 다른 것은 $J$ 의 정의뿐이다. 그래서
   희소 선형대수와 LM 감쇠가 그대로 재사용된다. 새로운 이론을 배우는 게 아니라 **좌표를 바꾸는
   것**이라는 감각이 중요하다.
3. **(4)를 손으로 유도한다 (50분)** — 앞 레슨의 $J_r^{-1}$ 이 여기서 쓰인다. P1 을 풀고, 왜 매
   반복 재계산해야 하는지 설명할 수 있게 한다.
4. **두 종류의 영공간을 구분해 본다 (90분)** — P4 와 재현 과제 조건 4 를 모두 하고, 감쇠 없는
   계수행렬의 영공간 기저를 직접 출력한다. **지지가 국소면 과매개화, 전역이면 게이지**다.
   이 구분을 못 하면 평생 LM 감쇠를 올리며 산다.
5. **반복 수로 비교한다 (60분)** — 재현 과제 조건 2 의 표가 이 레슨의 결론이다. "매니폴드를
   왜 쓰는가"에 대한 답이 수렴 속도라는 숫자로 나온다.
6. **논문은 두 층으로 읽는다 (110분)** — Absil et al. 는 왜 임의 재추적이 괜찮은지(이론),
   Dellaert & Kaess 는 그것이 실제 시스템에서 어떻게 희소 구조와 결합하는지(실무)를 준다.
   두 노트에 "이론의 어느 가정이 실무에서 깨지는가"를 한 문단으로 쓴다.

**통과 기준**: lift-solve-retract 를 백지에서 쓸 수 있고, (4)를 유도할 수 있고, R3 의 증명 전략을
말할 수 있고, 두 영공간을 수치로 구분할 수 있고, 재현 과제 네 조건을 만족하는 코드와 논문 2편의
노트가 있다.
