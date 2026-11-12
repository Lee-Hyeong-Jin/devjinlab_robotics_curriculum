---
id: c2-crba-aba
title: 질량행렬(CRBA)과 순동역학(ABA)
summary: >-
  질량행렬의 닫힌 형태를 복합 강체 관성으로 유도하고 CRBA 가 출력의 비영원소당 상수 작업만
  한다는 의미에서 출력 최적임을 증명하고, 관절 공간 관성(articulated-body inertia)의 재귀를
  Schur 보완으로 유도해 ABA 가 트리 구조 질량행렬의 fill-in 없는 소거임을 보인다. $d_i$ 가
  정확히 $M$ 의 Schur 보완이라는 등식까지 간다.
objectives:
  - 복합 강체 관성 $I^c_i$ 를 정의하고 $M_{ij} = S_i^\top I^c_i\,{}^iX_jS_j$ 를 유도할 수 있다.
  - $M$ 의 영 패턴이 트리의 조상 관계로 결정됨을 보이고 CRBA 가 출력 최적임을 논증할 수 있다.
  - 관절 공간 관성 재귀를 $\ddot{q}_j$ 의 Schur 소거로 빠진 줄 없이 유도할 수 있다.
  - $d_i = S_i^\top I^A_i S_i$ 가 $M$ 의 Schur 보완과 같음을 보이고 $0 < d_i \le M_{ii}$ 를 설명할 수 있다.
  - $I^A_i \succ 0$ 을 귀납으로 증명해 ABA 가 0 으로 나누지 않음을 보장할 수 있다.
prerequisites: [c2-rnea-inverse-dynamics]
difficulty: 5
estimated_minutes: 540
tags: [multibody-dynamics, mass-matrix, crba, aba, forward-dynamics, sparse-elimination, research]
activities:
  - id: c2-crba-aba-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 105
  - id: c2-crba-aba-papers
    kind: paper
    title: 필독 논문 2편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 120
  - id: c2-crba-aba-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 2 · 계산 1 · 구현 1 · 논문 1)
    estimated_minutes: 180
  - id: c2-crba-aba-reproduction
    kind: reproduction
    title: 재현 과제 — CRBA·ABA 의 상호 검증과 구조 확인 (R1)
    estimated_minutes: 120
  - id: c2-crba-aba-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Featherstone, Rigid Body Dynamics Algorithms (2008)"
    url: https://doi.org/10.1007/978-0-387-74315-8
    kind: book
    note: ch.6 (Forward Dynamics - the CRB and the articulated-body method), ch.7 (Sparse Factorization). 이 레슨의 1순위 교재.
  - title: "Lynch & Park, Modern Robotics"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: ch.8.2-8.6 (질량행렬과 순동역학). 같은 결과를 트위스트 표기로 본다. 전문 PDF 무료.
  - title: "Nocedal & Wright, Numerical Optimization"
    kind: book
    note: 권장. ch.3 (Cholesky)·ch.16 (KKT 계의 Schur 보완). ABA 를 희소 소거로 읽을 때의 배경. (공식 URL 미확인)
  - title: "Featherstone — Spatial vector and rigid-body dynamics software"
    url: https://royfeatherstone.org/spatial/
    kind: code
    note: 권장. 저자의 `HandC`·`FDab`·`FDcrb` 구현. 재현 과제의 선택 교차 검증용(Octave).
papers:
  - id: walker1982-crba
    role: seminal
    required: true
    note: "Methods 1-4"
  - id: featherstone1983-aba
    role: seminal
    required: true
---

# 질량행렬(CRBA)과 순동역학(ABA)

## 전제와 기호

`c2-rnea-inverse-dynamics` 의 트리 표기를 **그대로** 쓴다($n$, $\lambda(i)$, $\mu(i)$, $\nu(i)$,
$S_i$, $^iX_{\lambda(i)}$, $v_i$, $a_i$, $f_i$, $a_g$, $J_i$). 앞 레슨에서 계속 쓰는 결과:

- (앞 레슨 R4-5) $\dot q = 0$, $a_g = 0$, $\ddot q = e_k$ 로 RNEA 를 부르면 $M(q)e_k$ 다.
  따라서 $M = \sum_k J_k^\top I_kJ_k$ 이고 이 레슨은 그것을 **훨씬 싸게** 계산한다.
- (앞 레슨 R1) $J_{i,k} = {}^iX_kS_k$ ($k$ 가 $i$ 의 조상이거나 $i$ 자신일 때), 그 외 $0$.
- (앞 레슨 (3)) 가속도 재귀의 편향 항 $c_i := v_i \times v_{J_i}$.
- (앞 레슨 (5)) 힘 재귀와 $\tau_i = S_i^\top f_i$.

이 레슨의 새 기호:

| 기호 | 뜻 |
|---|---|
| $I^c_i$ | **복합 강체 관성**(composite-rigid-body inertia). 부분나무 $\nu(i)$ 를 하나의 강체로 굳혔을 때의 공간 관성, 바디 $i$ 좌표 |
| $I^A_i$ | **관절 공간 관성**(articulated-body inertia). $\nu(i)\setminus\{i\}$ 의 관절이 **자유로울 때** 바디 $i$ 가 보이는 겉보기 관성 |
| $p^A_i$ | 관절 공간 편향력(bias force). $f_i = I^A_i a_i + p^A_i$ 가 정의식 |
| $p_i$ | 바디 $i$ 자신의 편향력 $= (v_i\times^{*})I_iv_i - f^x_i$ |
| $U_i := I^A_iS_i$ | 관절 축 방향으로 본 관절 공간 관성 |
| $d_i := S_i^\top U_i = S_i^\top I^A_iS_i$ | 관절 $i$ 에서 본 **겉보기 스칼라 관성**. 이 레슨의 주인공 |
| $u_i := \tau_i - S_i^\top p^A_i$ | 관절 $i$ 의 "남는 토크" |
| $I^a_i := I^A_i - U_iU_i^\top/d_i$ | $\ddot q_i$ 를 소거한 뒤 부모가 보는 관성(랭크 1 하향 수정) |
| $p^a_i := p^A_i + I^a_i c_i + U_i u_i/d_i$ | 같은 소거 뒤의 편향력 |
| $\mathcal{D}(i) := \nu(i)\setminus\{i\}$ | 바디 $i$ 의 **진자손** 집합 |
| $\mathrm{anc}(i)$ | 바디 $i$ 의 진조상 집합. $\mathrm{depth}(i) := |\mathrm{anc}(i)|$ |

전제: 기구 트리, 단일 자유도 관절, 강체. 모든 $I_i \succ 0$ (질량이 양이고 관성이 양정치).
$M(q) \succ 0$ 은 이 전제에서 따라온다(문제 P1 ⓐ).

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 — `lesson-standard.md` §2).

- **R1 (질량행렬의 닫힌 형태와 분기 희소성) [D2]** — 복합 강체 관성을
  $$
  I^c_i := \sum_{k\in\nu(i)} {}^iX_k^{*}\,I_k\,{}^kX_i
  \qquad\Longleftrightarrow\qquad
  I^c_i = I_i + \sum_{j\in\mu(i)} {}^iX_j^{*}\,I^c_j\,{}^jX_i \tag{1}
  $$
  로 두면, $j$ 가 $i$ 의 조상이거나 $i$ 자신일 때
  $$
  M_{ij} = S_i^\top\,I^c_i\;{}^iX_j\,S_j, \tag{2}
  $$
  그리고 $i$ 와 $j$ 가 **서로 다른 분기**에 있으면($\,j \notin \mathrm{anc}(i)\cup\{i\}$ 이고
  $i \notin \mathrm{anc}(j)$) $M_{ij} = 0$ 이다. 즉 $M$ 의 구조적 비영 패턴은 **조상 관계**이고
  상삼각 비영원소의 개수는 정확히
  $$
  \mathrm{nnz}_{\triangle}(M) = \sum_{i=1}^{n}\big(1 + \mathrm{depth}(i)\big). \tag{3}
  $$
- **R2 (CRBA 는 출력 최적) [D3]** — CRBA 의 비용은 $\Theta\big(\sum_i (1+\mathrm{depth}(i))\big)
  = \Theta(\mathrm{nnz}_\triangle(M))$ 이다. 직렬 연쇄에서 $\Theta(n^2)$, 균형 이진 트리에서
  $\Theta(n\log n)$, 성형(star) 트리에서 $\Theta(n)$. 반대로 $M$ 을 출력하는 어떤 알고리즘도
  그 비영원소를 다 써야 하므로 $\Omega(\mathrm{nnz}_\triangle(M))$ 이 하한이다. 따라서 CRBA 는
  **비영원소당 상수 작업**만 하는, 차수로는 더 줄일 수 없는 알고리즘이다.
- **R3 (관절 공간 관성의 재귀 = $\ddot q$ 의 Schur 소거) [D3]** — $f_i = I^A_ia_i + p^A_i$ 를
  정의로 받아들이면, 자식 $j$ 의 $\ddot q_j$ 를 그 관절 방정식에서 풀어 소거하는 **한 번의
  Schur 보완**이 재귀를 준다:
  $$
  \ddot q_j = \frac{u_j - U_j^\top\big({}^jX_{\lambda(j)}a_{\lambda(j)} + c_j\big)}{d_j}, \tag{4}
  $$
  $$
  I^A_i = I_i + \sum_{j\in\mu(i)} {}^iX_j^{*}\,I^a_j\,{}^jX_i, \qquad
  p^A_i = p_i + \sum_{j\in\mu(i)} {}^iX_j^{*}\,p^a_j, \tag{5}
  $$
  $I^a_j = I^A_j - U_jU_j^\top/d_j$ 는 **랭크 1 하향 수정**이고, 정확히
  $$
  I^a_j\,S_j = 0 \tag{6}
  $$
  이다 — 부분나무는 자기 관절 축 방향으로 **아무 저항도 하지 않는다**는 사실의 대수적 형태다.
- **R4 ($d_i$ 는 $M$ 의 Schur 보완이다) [D2]** — $\mathcal{D} = \mathcal{D}(i)$ 에 대해
  $$
  d_i = S_i^\top I^A_i S_i = M_{ii} - M_{i\mathcal{D}}\,\big(M_{\mathcal{D}\mathcal{D}}\big)^{-1} M_{\mathcal{D}i}. \tag{7}
  $$
  즉 $d_i$ 는 "자손 관절은 자유롭게 두고 조상 관절은 고정했을 때 관절 $i$ 에서 느껴지는 관성"
  이고, $M \succ 0$ 에서 $0 < d_i \le M_{ii}$ 가 따라온다(등호는 $\mathcal{D}(i) = \emptyset$,
  즉 리프일 때). **따라서 ABA 는 트리 순서로 $M$ 을 소거하는 희소 Cholesky 와 같은 것**이고,
  트리 순서가 **fill-in 을 만들지 않기** 때문에 $O(n)$ 이다(`r0-sparse-linear-algebra` 의
  소거 순서 의존성이 여기서 현물로 나타난다).
- **R5 (ABA 의 $\Theta(n)$ 과 붕괴 없음) [D3]** — $I_i \succ 0$ 이면 모든 $i$ 에 대해
  $I^A_i \succ 0$ 이고 $I^a_i \succeq 0$ 이며, 따라서 $d_i > 0$ 이므로 (4)의 나눗셈은 **항상
  안전하다**(피벗팅이 필요 없다). 비용은 바디당 상수이므로 $\Theta(n)$. CRBA + 조밀 Cholesky
  경로($\Theta(n^2) + \Theta(n^3)$)와의 교차점은 작은 $n$ 에서 CRBA 쪽이고, 그 위치는 구현과
  하드웨어가 결정한다 — 비용 표는 RBDA ch.6·ch.7 의 비교 절에 있다. **[D1]**

## 유도

### R1 — 복합 강체 관성과 $M$

앞 레슨 R4-5 에서 $M = \sum_k J_k^\top I_kJ_k$ 이므로 성분으로

$$
M_{ij} = \sum_{k=1}^{n} J_{k,i}^\top\,I_k\,J_{k,j}.
$$

$J_{k,i} \ne 0$ 은 $i \in \mathrm{anc}(k)\cup\{k\}$, 즉 $k \in \nu(i)$ 와 동치다. 같은 말이
$j$ 에도 적용되므로 합의 범위는 $k \in \nu(i)\cap\nu(j)$ 다. 트리에서 두 부분나무의 교집합은
**둘 중 하나가 다른 쪽을 포함하거나 비어 있다**:

- $j \in \mathrm{anc}(i)\cup\{i\}$ 이면 $\nu(i) \subseteq \nu(j)$ 이므로 교집합은 $\nu(i)$.
- $i \in \mathrm{anc}(j)$ 이면 대칭적으로 교집합은 $\nu(j)$.
- 둘 다 아니면(서로 다른 분기) 교집합은 $\varnothing$ 이고 $M_{ij} = 0$.

첫 경우를 계산한다. $J_{k,i} = {}^kX_iS_i$, $J_{k,j} = {}^kX_jS_j = {}^kX_i\,{}^iX_jS_j$ 이므로

$$
M_{ij} = \sum_{k\in\nu(i)} \big({}^kX_iS_i\big)^\top I_k\,{}^kX_i\,\big({}^iX_jS_j\big)
= S_i^\top\underbrace{\left(\sum_{k\in\nu(i)} \big({}^kX_i\big)^\top I_k\,{}^kX_i\right)}_{=\,I^c_i}\,{}^iX_jS_j,
$$

여기서 $({}^kX_i)^\top = {}^iX_k^{*}$ (앞 레슨 (2))이므로 괄호 안이 (1)의 $I^c_i$ 다.
이것이 (2)다. $I^c_i$ 의 재귀 형태는 $\nu(i) = \{i\} \cup \bigcup_{j\in\mu(i)}\nu(j)$ 를
합에 대입하고 $^iX_k^{*} = {}^iX_j^{*}\,{}^jX_k^{*}$ 로 묶으면 바로 나온다.

**기하적 읽기**: $I^c_i$ 는 "관절 $i$ 아래를 전부 용접해 하나의 강체로 만들었을 때의 관성"이다.
$M_{ii} = S_i^\top I^c_iS_i$ 가 바로 그 해석이고, **다른 관절을 모두 고정했을 때** 관절 $i$ 에서
느껴지는 관성이다. (R4 의 $d_i$ 와 대비하라 — $d_i$ 는 자손을 **풀어** 놓은 쪽이다.)

(3)은 세기만 하면 된다. 상삼각의 비영 자리는 $(i, j)$ 쌍 중 $j \in \mathrm{anc}(i)\cup\{i\}$ 인
것들이고, 각 $i$ 마다 그런 $j$ 가 $1 + \mathrm{depth}(i)$ 개다.

> **주의**: (3)은 **구조적** 비영 개수다. 특정 기하에서는 실제 값이 0 이 될 수 있다 —
> 예를 들어 관절 축이 직교하고 질량중심이 축 위에 있으면 $M_{ij}$ 가 우연히 0 이 된다.
> 알고리즘의 비용은 구조가 결정하므로 R2 는 구조적 개수로 센다.

### CRBA

```python
def crba(model, q):
    """Composite-rigid-body mass matrix. Returns M (n, n), symmetric positive definite."""
    n = model.n
    Xup = model.Xup(q)
    Ic = [Ii.copy() for Ii in model.I]
    for i in range(n - 1, -1, -1):  # (1): accumulate composite inertias leaf -> root
        p = model.parent[i]
        if p >= 0:
            Ic[p] = Ic[p] + Xup[i].T @ Ic[i] @ Xup[i]
    M = np.zeros((n, n))
    for i in range(n):
        F = Ic[i] @ model.S[i]  # a force in body-i coordinates
        M[i, i] = model.S[i] @ F
        j = i
        while model.parent[j] >= 0:  # (2): walk up the ancestors, carrying F
            F = Xup[j].T @ F  # move the force into the parent's coordinates
            j = model.parent[j]
            M[i, j] = M[j, i] = model.S[j] @ F
    return M
```

`F` 가 힘 공간의 원소라서 `Xup[j].T`(즉 $X^{*}$)로 옮겨지는 것이 핵심이다 — 이 한 줄이
(2)의 $S_i^\top I^c_i\,{}^iX_j$ 를 왼쪽에서 오른쪽으로 **한 번만** 훑어 계산한다. 내부 while
루프가 $\mathrm{depth}(i)$ 회 돌므로 전체 비용이 (3)과 같아진다.

### R3 — 관절 공간 관성의 재귀

**정의부터 분명히 한다.** 바디 $i$ 와 그 **자손 관절이 자유로울 때**(자손 관절에는 주어진
$\tau_j$ 만 걸린다), 바디 $i$ 에 가해지는 힘 $f_i$ 와 바디 $i$ 의 가속도 $a_i$ 사이에는
아핀 관계가 성립한다:

$$
f_i = I^A_i\,a_i + p^A_i. \tag{8}
$$

(8)이 **성립한다는 것 자체**가 귀납의 결론이다. 리프에서는 자손이 없으므로
$I^A_i = I_i$, $p^A_i = p_i$ 로 앞 레슨 (5)가 곧 (8)이다. 이제 바디 $i$ 의 모든 자식 $j$ 에
대해 (8)이 성립한다고 가정하고 바디 $i$ 에서 (8)을 세운다.

**1단계 — 자식의 관절 방정식.** 자식 $j$ 의 가속도 재귀(앞 레슨 (3))를
$a'_j := {}^jX_{\lambda(j)}a_{\lambda(j)} = {}^jX_i\,a_i$ 로 줄여 쓰면

$$
a_j = a'_j + c_j + S_j\ddot q_j. \tag{9}
$$

관절 $j$ 의 토크는 $\tau_j = S_j^\top f_j$ 이고 (8)을 $j$ 에 적용하면

$$
\tau_j = S_j^\top\big(I^A_j(a'_j + c_j + S_j\ddot q_j) + p^A_j\big)
= U_j^\top(a'_j + c_j) + d_j\,\ddot q_j + S_j^\top p^A_j.
$$

$u_j = \tau_j - S_j^\top p^A_j$ 로 두고 $\ddot q_j$ 에 대해 풀면 (4)다. **여기가 Schur
소거다** — 미지수 $\ddot q_j$ 를 그것만 들어 있는 방정식 하나로 제거했다. $d_j \ne 0$ 이
필요하고 그것은 R5 가 보장한다.

**2단계 — 소거 결과를 $f_j$ 에 되돌린다.** (8)과 (9)에 (4)를 넣는다:

$$
f_j = I^A_j(a'_j + c_j) + U_j\ddot q_j + p^A_j
= I^A_j(a'_j + c_j) + \frac{U_j\big(u_j - U_j^\top(a'_j+c_j)\big)}{d_j} + p^A_j.
$$

$a'_j + c_j$ 에 걸리는 항을 모으면 랭크 1 하향 수정이 보인다:

$$
f_j = \underbrace{\left(I^A_j - \frac{U_jU_j^\top}{d_j}\right)}_{=\,I^a_j}(a'_j + c_j)
  + p^A_j + \frac{U_ju_j}{d_j}
= I^a_j\,a'_j + \underbrace{\Big(I^a_jc_j + p^A_j + \frac{U_ju_j}{d_j}\Big)}_{=\,p^a_j}. \tag{10}
$$

**3단계 — 부모의 힘 균형에 더한다.** 앞 레슨 (5)에서 바디 $i$ 가 받는 자식의 반작용은
$^iX_j^{*}f_j$ 이고, $a'_j = {}^jX_ia_i$ 이므로 (10)을 넣으면

$$
f_i = I_ia_i + p_i + \sum_{j\in\mu(i)} {}^iX_j^{*}\big(I^a_j\,{}^jX_i\,a_i + p^a_j\big)
= \Big(I_i + \sum_j {}^iX_j^{*}I^a_j\,{}^jX_i\Big)a_i + \Big(p_i + \sum_j {}^iX_j^{*}p^a_j\Big),
$$

즉 (8)이 바디 $i$ 에서도 성립하고 그 계수가 (5)다. 귀납 완료.

**(6)의 확인.** $I^a_jS_j = I^A_jS_j - \dfrac{U_j(U_j^\top S_j)}{d_j}
= U_j - \dfrac{U_jd_j}{d_j} = 0$. 한 줄이지만 뜻이 크다: $\ddot q_j$ 를 소거한 뒤 부모가 보는
관성은 **관절 축 방향으로 정확히 특이**하다. 물리로는 "자유 관절은 그 방향으로 힘을 전달하지
않는다"이고, 수치로는 "$I^a_j$ 는 양반정치이지만 양정치가 아니다"다(재현 과제 조건 4).

### ABA

```python
def aba(model, q, qd, tau, a_grav):
    """Articulated-body forward dynamics. Returns qdd (n,)."""
    n = model.n
    Xup = model.Xup(q)
    S = model.S
    v, c = [None] * n, [None] * n
    IA = [Ii.copy() for Ii in model.I]
    pA = [None] * n
    for i in range(n):  # pass 1: velocities, bias forces
        vJ = S[i] * qd[i]
        p = model.parent[i]
        v[i] = vJ if p < 0 else Xup[i] @ v[p] + vJ
        c[i] = np.zeros(6) if p < 0 else crm(v[i]) @ vJ
        pA[i] = crf(v[i]) @ IA[i] @ v[i] - model.fx[i]
    U, d, u = [None] * n, np.zeros(n), np.zeros(n)
    for i in range(n - 1, -1, -1):  # pass 2: articulated inertias, leaf -> root
        U[i] = IA[i] @ S[i]
        d[i] = S[i] @ U[i]
        u[i] = tau[i] - S[i] @ pA[i]
        p = model.parent[i]
        if p >= 0:
            Ia = IA[i] - np.outer(U[i], U[i]) / d[i]  # (10): the rank-1 downdate
            pa = pA[i] + Ia @ c[i] + U[i] * (u[i] / d[i])
            IA[p] = IA[p] + Xup[i].T @ Ia @ Xup[i]
            pA[p] = pA[p] + Xup[i].T @ pa
    a, qdd = [None] * n, np.zeros(n)
    for i in range(n):  # pass 3: accelerations, root -> leaf
        p = model.parent[i]
        ap = (Xup[i] @ (-a_grav) if p < 0 else Xup[i] @ a[p]) + c[i]
        qdd[i] = (u[i] - U[i] @ ap) / d[i]  # (4)
        a[i] = ap + S[i] * qdd[i]
    return qdd
```

세 패스 모두 바디당 상수 작업이다. 중력은 RNEA 와 똑같이 $a_0 = -a_g$ 로 들어간다.

### R4 — $d_i$ 가 $M$ 의 Schur 보완이다

(7)을 선형대수로 본다. 관절 $i$ 와 그 진자손 $\mathcal{D} = \mathcal{D}(i)$ 만 남기고
**조상 관절을 고정**하면($\ddot q_k = 0$, $k \in \mathrm{anc}(i)$), 운동 방정식의 관련 블록은

$$
\begin{bmatrix} M_{ii} & M_{i\mathcal{D}} \\ M_{\mathcal{D}i} & M_{\mathcal{D}\mathcal{D}}\end{bmatrix}
\begin{bmatrix} \ddot q_i \\ \ddot q_{\mathcal{D}}\end{bmatrix}
= \begin{bmatrix} \tau_i - b_i \\ \tau_{\mathcal{D}} - b_{\mathcal{D}}\end{bmatrix}
$$

이고($b$ 는 편향·중력 항), 자손 관절을 **자유롭게** 둔다는 것은 $\tau_{\mathcal{D}}$ 가 주어진
값이라는 뜻이다. 두 번째 블록 행에서 $\ddot q_{\mathcal{D}}$ 를 풀어 첫 행에 대입하면

$$
\underbrace{\Big(M_{ii} - M_{i\mathcal{D}}M_{\mathcal{D}\mathcal{D}}^{-1}M_{\mathcal{D}i}\Big)}_{\text{Schur 보완}}\ddot q_i
= (\tau_i - b_i) - M_{i\mathcal{D}}M_{\mathcal{D}\mathcal{D}}^{-1}(\tau_{\mathcal{D}} - b_{\mathcal{D}}).
$$

한편 ABA 의 (4)는 같은 상황에서 $d_i\,\ddot q_i = u_i - U_i^\top(a'_i + c_i)$ 를 주고,
$\ddot q_i$ 의 계수는 $d_i$ 다. 두 식은 **같은 미지수에 대한 같은 1차원 방정식**이므로 계수가
같아야 한다 — 이것이 (7)이다. ($M_{\mathcal{D}\mathcal{D}}$ 가 가역인 것은 $M \succ 0$ 의
주부분행렬이기 때문이다.)

따라서 $d_i$ 는 $M$ 의 양정치성에서 바로 **양수**이고(Schur 보완은 양정치),
$M_{i\mathcal{D}}M_{\mathcal{D}\mathcal{D}}^{-1}M_{\mathcal{D}i} \ge 0$ 이므로
$d_i \le M_{ii}$ 다. 리프에서는 $\mathcal{D} = \varnothing$ 이라 $d_i = M_{ii}$ 로 **정확히**
같다.

> **수치로 본 (7)**: 7-DOF 직렬 팔의 무작위 자세에서 ABA 의 $d$ 와 $M$ 의 Schur 보완을
> 따로 계산해 비교하면 최대 오차 $2.2\times10^{-16}$ 이다. 2링크 팔에서는
> $d_1 = M_{11} - M_{12}^2/M_{22} = 0.689405914278$, $d_2 = M_{22} = 0.16$ 으로 손으로도 확인된다.

**이 등식의 의미.** ABA 는 트리 구조를 가진 $M$ 을 **리프→루트 순서로 소거**하는 것이고,
각 소거가 랭크 1 하향 수정 (10)이다. 트리의 리프→루트 순서는 소거 그래프에 **새 간선을 만들지
않으므로**(자식의 소거가 영향을 주는 것은 부모 하나뿐) fill-in 이 0 이고, 그래서 비용이
$\Theta(n)$ 에 머문다. 같은 $M$ 을 **임의 순서**로 소거하면 fill-in 이 생겨 비용이 올라간다 —
`r0-sparse-linear-algebra` 의 COLAMD 실험이 말하는 바로 그 현상이고, 여기서는 물리 구조가
최적 순서를 공짜로 준다. RBDA ch.7 이 이 관점을 전개한다.

## 증명 스케치

### R2 — CRBA 는 출력 최적이다

**가설** H1: 기구 트리, 단일 자유도 관절 $n$ 개, 바디당 상수 크기 데이터. H2: 실수 산술은
단위 비용. H3: $M$ 전체(또는 상삼각)를 출력해야 한다.
**결론** C1: CRBA 의 비용은 $\Theta\big(\sum_i(1+\mathrm{depth}(i))\big)$.
C2: 임의 알고리즘의 하한이 같은 양이므로 CRBA 는 차수로 최적이다.

**전략**: 상한은 루프를 세고, 하한은 출력 크기로 친다. 트리 모양별 값은 $\sum_i\mathrm{depth}(i)$
를 계산하는 조합론이다.

1. **상한.** (1)의 누적 루프는 바디당 상수 작업 × $n$ = $\Theta(n)$. (2)의 이중 루프는 바디 $i$
   마다 $\mathrm{depth}(i)$ 회 while 을 돌고 회당 상수 작업($X^\top F$ 와 내적)이므로
   $\Theta\big(\sum_i \mathrm{depth}(i)\big)$. 합쳐 $\Theta\big(\sum_i(1+\mathrm{depth}(i))\big)$.
2. **출력 크기와 일치.** (3)에서 그 양이 정확히 $\mathrm{nnz}_\triangle(M)$ 이다. 즉 CRBA 는
   **상삼각 비영원소 하나당 상수 작업**을 한다.
3. **하한.** H3 에서 알고리즘은 $\mathrm{nnz}_\triangle(M)$ 개의 수를 써야 하므로
   $\Omega(\mathrm{nnz}_\triangle(M))$. (더 강한 하한도 가능하다: 구조적으로 비영인 $M_{ij}$ 는
   일반적 기하에서 실제로 0 이 아니고 $q$ 에 의존하므로, 그 값을 내려면 관련 $q_k$ 들을 읽어야 한다.)
4. **트리 모양별 값.** 직렬 연쇄는 $\mathrm{depth}(i) = i-1$ 이므로
   $\sum_i(1+\mathrm{depth}(i)) = n(n+1)/2 = \Theta(n^2)$. 균형 이진 트리는 깊이가
   $O(\log n)$ 이므로 $\Theta(n\log n)$. 깊이 1 의 성형 트리는 $\Theta(n)$ —
   **이 경우 $M$ 은 거의 대각이고 CRBA 는 선형이다**.
5. **무엇이 최적이 아닌가.** 상수와, "$M$ 을 만들어야 하는가"라는 질문 자체다. 순동역학만
   원하면 $M$ 을 만들지 않는 ABA 가 $\Theta(n)$ 이고(R5), 직렬 연쇄에서는 $\Theta(n^2)$ 인
   CRBA 보다 차수가 낮다. **$M$ 이 필요한 이유**(제어 설계, 최적화의 2차 항, 접촉 해법의
   $\Lambda$)가 있을 때만 CRBA 를 쓴다.

**가설을 지우면**: H3 을 빼면 2·3단계가 무의미해진다 — 출력이 $M$ 이 아니라 $M^{-1}\tau$ 라면
하한은 $\Omega(n)$ 으로 떨어지고 ABA 가 그것을 달성한다. H1 에서 트리를 빼면 $M$ 의 영 패턴이
조상 관계로 결정되지 않아 (3) 자체가 성립하지 않는다.

### R5 — $I^A_i \succ 0$, $d_i > 0$, 그리고 $\Theta(n)$

**가설** H1: 모든 $i$ 에 대해 $I_i \succ 0$ (질량 $m_i > 0$, $\bar I_{C,i} \succ 0$).
H2: 기구 트리, 단일 자유도 관절. **결론** C1: 모든 $i$ 에서 $I^A_i \succ 0$ 이고
$I^a_i \succeq 0$ (랭크 결손 정확히 1, 영공간은 $\mathrm{span}(S_i)$).
C2: 따라서 $d_i > 0$ 이고 ABA 는 피벗팅 없이 항상 정의된다. C3: 비용은 $\Theta(n)$.

**전략**: 리프→루트 귀납. 핵심 보조사실은 "양정치 행렬의 Schur 보완은 양반정치"
(Schur 보완 보조정리)와 "합동 변환은 양정치성을 보존"(앞 레슨 R2)이다.

1. **기저(리프).** $\mu(i) = \varnothing$ 이면 $I^A_i = I_i \succ 0$ (H1).
2. **$d_i > 0$.** $I^A_i \succ 0$ 이고 $S_i \ne 0$ 이므로 $d_i = S_i^\top I^A_iS_i > 0$.
   따라서 (4)의 나눗셈과 (10)의 하향 수정이 정의된다.
3. **$I^a_i \succeq 0$ 과 영공간.** $I^a_i = I^A_i - U_iU_i^\top/d_i$ 는 $2\times2$ 블록 행렬
   $\begin{bmatrix} I^A_i & U_i \\ U_i^\top & d_i\end{bmatrix}$ 의 $d_i$ 에 대한 Schur
   보완이고, 그 블록 행렬은 $\begin{bmatrix}\mathbb{1} \\ S_i^\top\end{bmatrix}$ 로 쓴
   $I^A_i$ 의 합동이므로 양반정치다. 따라서 $I^a_i \succeq 0$. (6)에서 $S_i$ 가 영공간에
   있고, 랭크 결손이 1 을 넘지 않는 것은 하향 수정이 랭크 1 이기 때문이다.
4. **귀납 단계.** (5)에서 $I^A_i = I_i + \sum_{j\in\mu(i)}{}^iX_j^{*}I^a_j\,{}^jX_i$ 이고,
   앞 레슨 R2 로 각 항 $^iX_j^{*}I^a_j\,{}^jX_i = ({}^jX_i)^\top I^a_j({}^jX_i)$ 는 양반정치의
   합동이므로 양반정치다. 양정치 + 양반정치 = 양정치이므로 $I^A_i \succeq I_i \succ 0$.
   루트까지 올라가면 C1·C2.
5. **$\Theta(n)$ (C3).** 패스 1·3 은 바디당 상수(앞 레슨 R5 와 같은 셈), 패스 2 는 바디당
   $U_i$($6\times6$ 곱 1회), $d_i$(내적), 랭크 1 하향 수정($6\times6$ 외적 1회),
   $X^\top I^a X$(합동, $6\times6$ 곱 2회) — 모두 $n$ 과 무관한 상수다. 각 바디를 3회
   방문하므로 $\Theta(n)$. 하한은 $\Omega(n)$(출력 $\ddot q$ 가 $n$ 성분)이라 차수 최적이다.

**가설을 지우면**: H1 에서 $m_i > 0$ 을 빼면(질량 0 인 "가상 바디") $I_i$ 가 특이해져 4단계의
"양정치 + 양반정치"가 양반정치로만 남고, 리프에 질량 0 인 바디가 있으면 $d_i = 0$ 이 되어
ABA 가 **0 으로 나눈다**. 실무에서 URDF 의 질량 0 링크가 정확히 이 지점에서 터지므로,
구현은 그런 링크를 부모에 병합하거나 $d_i$ 에 하한을 검사해야 한다(재현 과제의 진단표).
H2 에서 트리를 빼면 (5)의 자식 합 자체가 정의되지 않는다.

> **주의 — 수치적 양정치 vs 정확한 양정치.** 3단계는 $I^a_i \succeq 0$ 을 주지만 부동소수점에서
> 최소 고윳값은 $-10^{-16}$ 수준으로 음수가 될 수 있다(저자 환경에서 측정:
> $\lambda_{\min}(I^a) = -3.1\times10^{-15}$). 이것은 (6)에 의해 **정확히 0 이어야 하는**
> 고윳값의 반올림이다. $I^a_i$ 에 Cholesky 를 걸어 양정치를 확인하려 하면 실패하므로,
> 검증은 "$\lambda_{\min} \ge -\epsilon$ 이고 $I^a_iS_i \approx 0$"으로 해야 한다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** ⓐ $M(q) \succ 0$ 을 $M = \sum_k J_k^\top I_kJ_k$ 에서 증명하라
(등호 조건까지 — 어떤 기구에서 $M$ 이 특이해지는가?). ⓑ (1)의 재귀 형태를 합 형태에서
유도하라. ⓒ 성형 트리(바디 $n$ 개가 모두 베이스에 직접 붙음)에서 $M$ 이 대각인지 확인하고,
대각이 **아닌** 경우가 있다면 어떤 경우인지 쓰라.
*해답 스케치*: ⓐ 는 $v^\top Mv = \sum_k \lVert\cdot\rVert^2_{I_k} \ge 0$ 와 등호 조건
"모든 바디의 공간 속도가 0" = "$J\dot q = 0$". 정기구학이 비특이면 $\dot q = 0$ 이다.
ⓒ 는 함정이다 — 성형 트리에서 서로 다른 분기의 $M_{ij}$ 는 R1 로 **정확히 0** 이지만,
$M_{0j}$ 처럼 베이스가 떠 있는(floating base) 경우는 분기가 다시 연결된다.

**P2 (유도, ★★, R3·R4)** ⓐ (10)의 $p^a_j$ 를 빠진 줄 없이 다시 유도하라. 특히
$I^a_jc_j$ 가 $I^A_jc_j$ 가 **아닌** 이유를 쓰라. ⓑ 리프 바디에서 (7)이 $d_i = M_{ii}$ 로
퇴화하는 것을 (2)와 비교해 확인하라. ⓒ 2링크 팔에서 $d_1 = M_{11} - M_{12}^2/M_{22}$ 를
손으로 계산해 공개 수치와 대조하라.
*해답 스케치*: ⓐ 의 핵심은 $a'_j + c_j$ 를 **하나의 묶음**으로 보고 거기에 하향 수정된 관성이
걸린다는 것이다. $c_j$ 를 따로 떼어 $I^A_j$ 를 곱하면 $U_jU_j^\top c_j/d_j$ 항이 사라져
$\dot q \ne 0$ 에서 틀린다 — 재현 과제 조건 3 이 이것을 잡는다.

**P3 (증명, ★★★, R2)** ⓐ 깊이 $h$ 의 완전 이진 트리($n = 2^h - 1$)에서
$\sum_i(1+\mathrm{depth}(i))$ 를 닫힌 형태로 구하고 $\Theta(n\log n)$ 임을 보이라.
ⓑ 주어진 $n$ 에 대해 $\sum_i\mathrm{depth}(i)$ 를 **최대화·최소화**하는 트리 모양을 각각
구하고, 그 값이 CRBA 비용의 상한·하한임을 논증하라. ⓒ R2 의 3단계 하한을 "$M$ 의 비영원소
하나를 계산하려면 관련 $q_k$ 를 읽어야 한다"는 더 강한 형태로 다듬고, 그 논증이 성립하려면
기하에 어떤 가정이 필요한지 쓰라.
*전략 + 핵심 부등식*: ⓐ 는 깊이 $d$ 에 노드가 $2^d$ 개임을 쓰고 $\sum_d d\,2^d$ 를 계산한다.
ⓑ 의 최대는 직렬, 최소는 성형이다. ⓒ 에서는 "일반적 기하"를 어떻게 정식화할지가 요점이다
(어떤 측도-0 집합을 제외하는가). 전개는 숨긴다.

**P4 (증명, ★★★, R5)** ⓐ Schur 보완 보조정리("$A \succ 0$, $\begin{bmatrix}A & b\\ b^\top & c\end{bmatrix} \succeq 0$
이면 $A - bb^\top/c \succeq 0$")를 증명하라. ⓑ 질량 0 인 리프 링크가 있을 때 ABA 가 어디서
어떻게 터지는지 식으로 쓰고, 그 링크를 부모에 병합하는 것이 **정확히** 같은 동역학을 주는지
논증하라. ⓒ 관절에 마찰·댐핑 $-b_i\dot q_i$ 가 있으면 (4)가 어떻게 바뀌는지 쓰라
(힌트: $\tau_i$ 에 흡수된다 — 그러면 $d_i$ 는 왜 안 바뀌는가?).
*전략 + 핵심 부등식*: ⓐ 는 $\begin{bmatrix}x \\ -b^\top x/c\end{bmatrix}$ 를 2차 형식에 넣는다.
ⓑ 는 질량 0 리프의 $I^A_i = 0$ 에서 $d_i = 0$ 이고, 병합의 동등성은 그 링크가 관절 축 방향으로
어떤 관성도 주지 않는다는 점에서 따라온다. 전개는 숨긴다.

**P5 (계산, ★, R1·R3·R4)** `c2-rnea-inverse-dynamics` P4 의 2링크 팔(같은 모델)에서
$q = (0.3, -0.7)$, $\dot q = (0.5, 1.2)$, $\tau = (2.0, -0.5)$, 중력 $-y$ $9.81$ 일 때
$M(q)$, 편향+중력 항 $b = M\cdot 0 + C\dot q + g$, ABA 의 $\ddot q$, 그리고 $d_1$, $d_2$ 를 구하라.
*정답* (허용오차 $10^{-9}$):
$M(q) = \begin{bmatrix} 1.427124249897 & 0.343562124948 \\ 0.343562124948 & 0.16 \end{bmatrix}$,
$b = (18.080196104584,\; 3.575590279233)$,
$\ddot q = (-10.630646761366,\; -2.645641802023)$,
$d_1 = 0.689405914278$, $d_2 = 0.16$.
*검산*: ⓐ $M\ddot q + b = \tau$ 를 $10^{-12}$ 이내로 만족
ⓑ $d_2 = M_{22}$ 가 **정확히** 같다(리프) ⓒ $d_1 = M_{11} - M_{12}^2/M_{22}$ 가 $10^{-12}$
이내로 일치 ⓓ $1/(M^{-1})_{11} = d_1$ (같은 수의 다른 읽기).

**P6 (구현, ★★, R1·R3)** `crba(model, q)` 와 `aba(model, q, qd, tau, a_grav)` 를 쓰라.
*루브릭*: ⓐ P5 의 수치를 $10^{-9}$ 이내로 재현 ⓑ `crba` 가 **대칭을 강제하지 않고도**
$\lVert M - M^\top\rVert_\infty = 0$ 을 내야 한다(상삼각을 계산하고 하삼각에 대입하므로
비트 단위로 같아야 한다) ⓒ 분기 트리에서 서로 다른 분기의 $M_{ij}$ 가 **정확히 0**
ⓓ `aba` 의 결과가 `solve(crba(q), tau - rnea(q, qd, 0))` 와 $10^{-12}$ 이내로 일치
ⓔ 모든 $d_i > 0$ 과 $\lVert I^a_iS_i\rVert_\infty < 10^{-14}$ 를 단위 테스트로 검사
ⓕ 질량 0 링크가 있는 모델에서 **명확한 예외**를 던진다(조용히 `inf`/`nan` 을 내면 미달).

**P7 (논문, ★★, R2·R5)** Walker & Orin (1982)과 Featherstone (1983)을 읽고 ⓐ 두 논문이
각각 어떤 비용을 주장하고, 그 주장이 이 레슨 R2·R5 의 어느 단계에 대응하는지 ⓑ 1982년
논문의 Method 1·2 가 왜 느린지(이 레슨의 용어로) ⓒ 두 논문의 비용 비교에서 **빠진 변수**를
2개 찾으라(힌트: 캐시, 분기 구조).
*루브릭*: ⓐ 에서 1982년은 상한만, 1983년도 상한만 다루고 **둘 다 하한을 다루지 않는다**는
점을 짚으면 통과. ⓒ 에서 메모리 접근 패턴과 트리 모양 중 하나 이상을 구체적으로 쓰면 통과.
"하드웨어가 달라서"만 쓰면 미달.

## 논문 읽기

**필독 2편.** 1982년과 1983년, 1년 사이에 나온 두 알고리즘이 각각 $O(n^2)$ 과 $O(n)$ 을
주장한다. **같은 문제에 대해 왜 두 답이 공존하는가**를 스스로 설명하는 것이 이 레슨의 읽기
목표다(답은 R2 의 5단계와 R5 의 교차점에 있다). 각 논문에 아래 고정 질문 10개로 1페이지
노트를 쓴다(`lesson-standard.md` §5). 3-pass 로 읽고 3번째 패스에서 질문 4·5·9 를 집중 공략한다.

1. **Walker & Orin, "Efficient Dynamic Computer Simulation of Robotic Mechanisms"
   (1982, ASME J. Dyn. Syst. Meas. Control)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1115/1.3139699>
   어느 절을 왜 읽는가: Method 1–4 를 제시하고 비교하는 절 전체. **Method 3 이 CRBA** 이고,
   이 레슨 (1)(2)와 1:1 로 대응한다. Method 1·2 가 느린 이유를 R2 의 용어로 다시 쓰면
   "$M$ 을 비영원소당 상수 작업보다 비싸게 만든다"다.
   추가 질문: ⓐ 저자들이 비교에 쓴 지표는 무엇이고, 그 지표가 1982년 하드웨어에 특유한가?
   ⓑ 저자들의 Method 3 과 이 레슨의 CRBA 가 **다른 점**이 있는가(분기 처리, 좌표 선택)?
2. **Featherstone, "The Calculation of Robot Dynamics Using Articulated-Body Inertias"
   (1983, IJRR)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1177/027836498300200102>
   어느 절을 왜 읽는가: 관절 공간 관성을 정의하고 재귀를 세우는 절. 이 레슨 R3 의 유도와
   **한 줄씩** 대조하며 읽는다. 저자가 (8)을 어떻게 정당화하는지가 특히 중요하다.
   추가 질문: ⓐ 저자가 $d_i > 0$ 을 어디서 보장하는가, 아니면 암묵적으로 가정하는가?
   ⓑ 이 레슨의 R4(= $M$ 의 Schur 보완)에 해당하는 서술이 논문에 있는가, 없다면 왜
   그 관점이 나중에(RBDA ch.7) 추가되었다고 보는가? ⓒ $O(n)$ 주장의 상수가 $O(n^2)$ 인
   CRBA 를 실제로 언제 이기는가 — 논문이 답하는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R1 (수치 검증).** 계산 예산: 노트북 CPU 1코어, 2분 이내, numpy 만. 메모리 200MB 이내.

P6 의 `crba`·`aba` 가 아래 **네 조건을 모두** 만족해야 통과다. 난수는 시드를 고정한다
(`np.random.default_rng(7)`).

1. **$M$ 의 두 독립 경로 일치** — 7-DOF 직렬 팔(앞 레슨 재현 과제와 **같은 모델**)의 무작위
   자세 $10^3$ 개에서
   $$
   \max\big\lVert M^{\text{CRBA}} - \textstyle\sum_k J_k^\top I_kJ_k \big\rVert_\infty < 10^{-14},
   \qquad \big\lVert M^{\text{CRBA}} - (M^{\text{CRBA}})^\top \big\rVert_\infty = 0,
   $$
   그리고 $\lambda_{\min}(M) > 0$. (대칭 오차가 **정확히 0** 이어야 한다 — 상삼각만 계산하고
   하삼각에 대입했다면 비트 단위로 같다. $10^{-16}$ 이 나오면 두 번 계산하고 있다는 뜻이다.)
2. **$M$ vs 유한차분 역동역학** (blueprint 가 지정한 기준) — 같은 모델에서
   $M^{\text{fd}}_{\cdot k} = \dfrac{\mathrm{rnea}(q, 0, h e_k) - \mathrm{rnea}(q, 0, -h e_k)}{2h}$
   ($h = 10^{-6}$, 중력 0)에 대해
   $$
   \max\big\lVert M^{\text{CRBA}} - M^{\text{fd}} \big\rVert_\infty < 10^{-12}.
   $$
   > 저자 환경 측정값: $4.4\times10^{-16}$, 그리고 $h \in [10^{-8}, 10^{-4}]$ 전 구간에서
   > 같은 수준이다 — **V 곡선이 나타나지 않는 것이 정답**이다. 이유: 중력을 끄고
   > $\dot q = 0$ 으로 두면 $\tau = M\ddot q$ 가 $\ddot q$ 에 **정확히 선형**이므로 중앙
   > 유한차분의 절단 오차가 0 이고, $\tau$ 의 크기가 작아 상쇄 오차도 없다. 중력을 **켜면**
   > 상쇄가 지배해 오차가 $1/h$ 로 커진다(측정: $h = 10^{-4}$ 에서 $7.1\times10^{-11}$,
   > $10^{-6}$ 에서 $8.7\times10^{-9}$, $10^{-8}$ 에서 $9.2\times10^{-7}$). 그래서 이 조건은
   > **중력 0 을 명시한다** — 앞 레슨 조건 3 의 V 곡선과 대비해 보라.
3. **ABA vs $M^{-1}$ 경로, 그리고 RNEA 왕복** — 무작위 $(q, \dot q, \tau)$ $10^3$ 개에서
   $$
   \max\big\lVert \mathrm{aba}(q,\dot q,\tau) - \mathrm{solve}\big(M, \tau - \mathrm{rnea}(q,\dot q,0)\big)\big\rVert_\infty < 10^{-12},
   $$
   $$
   \max\big\lVert \mathrm{rnea}\big(q, \dot q, \mathrm{aba}(q,\dot q,\tau)\big) - \tau \big\rVert_\infty < 10^{-12}.
   $$
   > 저자 환경 측정값: $1.8\times10^{-14}$ 와 $2.4\times10^{-15}$.
   > $\dot q \ne 0$ 에서 반드시 시험하라 — $\dot q = 0$ 에서는 P2 ⓐ 의 버그가 숨는다.
4. **구조 확인 (이 레슨의 고유 조건)** — 네 가지를 모두 확인한다.
   ⓐ **$d_i$ 는 $M$ 의 Schur 보완** (7): 직렬 연쇄에서 $\mathcal{D}(i) = \{i+1,\dots,n\}$ 이므로
   $\max_i|d_i - (M_{ii} - M_{i\mathcal{D}}M_{\mathcal{D}\mathcal{D}}^{-1}M_{\mathcal{D}i})| < 10^{-12}$
   (측정값 $2.2\times10^{-16}$), 그리고 $0 < d_i \le M_{ii}$, $d_n = M_{nn}$ 이 **정확히** 같다.
   ⓑ **$I^a_iS_i = 0$** (6): $\max_i\lVert I^a_iS_i\rVert_\infty < 10^{-14}$ (정확히 0 이어야 한다).
   ⓒ **$I^A_i \succ 0$, $I^a_i \succeq 0$**: $\lambda_{\min}(I^A_i) > 0$ 이고
   $\lambda_{\min}(I^a_i) > -10^{-13}$ (측정값 $-3.1\times10^{-15}$ — **음수가 나오는 것이
   정상**이고, 그 값이 (6)의 정확한 0 고윳값의 반올림임을 $I^a_iS_i$ 와 함께 확인하라).
   ⓓ **분기 희소성** (R1): 바디 4개의 분기 트리(부모 $[-1, 0, 0, 2]$, 축
   $z, y, z, x$, 일반적인 오프셋·관성)에서 서로 다른 분기의 $M_{ij}$ 가 **정확히 0** 이고
   비영원소의 개수가 (3)의 $2\sum_i(1+\mathrm{depth}(i)) - n$ 과 같아야 한다(여기서 12 개).
   축이 직교하고 질량중심이 축 위에 놓이는 **퇴화 기하를 피하라** — 그런 모델에서는 구조적으로
   비영인 자리도 우연히 0 이 되어 ⓓ 가 무의미해진다.

**입력 데이터**: 외부 데이터 불필요. 7-DOF 모델은 앞 레슨과 같은 생성 스크립트를 쓴다
(동일 시드). 분기 트리의 오프셋은 회전을 섞은 일반 변환으로 생성한다.

**비교 대상** (최소 1개):
- 1순위: 조건 1 의 야코비안 경로와 조건 3 의 $M^{-1}$ 경로 — 둘 다 CRBA·ABA 와 독립이다.
- 2순위: 조건 2 의 유한차분 역동역학(앞 레슨의 `rnea` 를 정답지로 씀).
- 선택 검증(없어도 통과): `pinocchio` 의 `pin.crba`·`pin.aba` 와 $10^{-10}$ 이내 일치
  (성분 순서 주의), 또는 Featherstone 의 `HandC`·`FDab`·`FDcrb`(Octave).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 1 의 대칭 오차가 $10^{-16}$ | $M_{ij}$ 와 $M_{ji}$ 를 각각 계산했다 | 상삼각만 계산하고 `M[j, i] = M[i, j]` 로 대입하는지 코드를 본다 |
| $M$ 이 대칭이지만 값이 틀리다 | (1)의 누적을 루트→리프 순서로 했다 | 리프에서 시작하는지(즉 `range(n-1, -1, -1)`) 확인한다 |
| 조건 3 이 $\dot q = 0$ 에서만 통과 | (10)에서 $c_j$ 에 $I^A_j$ 를 곱했다($I^a_j$ 가 아니라) | $p^a_j$ 의 $I^a_jc_j$ 항을 $I^A_jc_j$ 로 바꿔 보고 오차가 같아지는지 본다 |
| 조건 4 ⓑ 가 $10^{-10}$ 수준 | $d_i$ 를 $S_i^\top I^A_iS_i$ 대신 다른 식으로 계산했다 | $U_i = I^A_iS_i$ 를 **먼저** 만들고 $d_i = S_i^\top U_i$ 로 쓰는지 본다 |
| 조건 4 ⓒ 에서 $\lambda_{\min}(I^a) \approx -10^{-8}$ | $I^a_i$ 의 대칭화를 안 했다 — 외적 뺄셈이 비대칭을 만든다 | $(I^a + (I^a)^\top)/2$ 로 고윳값을 보고, 비대칭 크기 $\lVert I^a - (I^a)^\top\rVert$ 를 출력한다 |
| 조건 4 ⓓ 에서 비영 개수가 더 많다 | 분기 판정을 조상 관계가 아니라 번호 크기로 했다 | 부모 배열에서 조상 집합을 명시적으로 만들어 패턴을 비교한다 |
| `nan` 또는 `inf` | 질량 0 링크로 $d_i = 0$ | 모든 $I_i$ 의 $\lambda_{\min}$ 과 $m_i$ 를 로드 시점에 검사하고 예외를 던진다 |
| $n$ 이 커질 때 ABA 가 CRBA 보다 느리다 | numpy 의 $6\times6$ 연산 오버헤드가 상수를 지배 | 두 알고리즘의 **호출 횟수**를 세어 차수를 확인하고, 벽시계는 $n \ge 50$ 에서 비교한다 |

## 열린 문제

- **(열린 문제) 소거 순서와 조건수의 교환** — ABA 는 트리 순서가 fill-in 을 0 으로 만든다는
  점에서 최적이지만, **수치적으로** 최적인 순서는 아니다. 희소 선형대수에서는 fill-in 최소
  순서와 안정성(피벗) 사이에 교환이 있고, 질량비가 큰 계에서는 트리 순서가 조건수를 악화시킬
  수 있다. 다물체 동역학에서 "fill-in 과 조건수를 함께 보는 순서 선택" 이론이 없다.
  현재 접근: 희소 분해 관점의 재정식화(RBDA ch.7), 사전조건화된 반복 해법.
  비어 있는 자리: 기구 구조에서 조건수를 예측해 순서를 고르는 절차 —
  `c2-spatial-vector-algebra` 의 첫 열린 문제와 같은 벽이다.
- **(열린 문제) $M$ 을 만들어야 하는 알고리즘들의 비용 하한** — 순동역학만 원하면 ABA 가
  $\Theta(n)$ 이지만, 조작 공간 관성 $\Lambda$(다음 레슨), 접촉 LCP 의 Delassus 연산자,
  2차 최적화의 Hessian 은 $M$ 또는 그 일부를 요구한다. "제약·접촉이 $k$ 개일 때
  $\Lambda$ 를 얻는 비용의 하한"은 $k$ 와 $n$ 모두에 대해 알려져 있지 않고, 실무에서는
  $O(nk + k^3)$ 류의 상한만 쓰인다. 현재 접근: 효율적 조작 공간 관성 알고리즘
  ([Featherstone 1999](https://doi.org/10.1177/02783649922066619) 의 분할정복 계열),
  접촉의 볼록 완화([Todorov 2014](https://doi.org/10.1109/ICRA.2014.6907751)).
  비어 있는 자리: $k$ 에 대한 하한.
- **(열린 문제) 배치·미분 가능 동역학에서의 알고리즘 선택** — 궤적 최적화와 강화학습은
  수천 개 상태에서 순동역학 **과 그 미분**을 동시에 부른다. 이 워크로드에서는 $\Theta(n)$ 대
  $\Theta(n^2)$ 의 차수보다 메모리 접근과 벡터화 가능성이 지배하고, $M$ 을 명시적으로
  만드는 CRBA 경로가 미분을 더 쉽게 주기도 한다. 어떤 체제에서 어느 쪽이 이기는지에 대한
  모형이 없다. 현재 접근: 해석적 미분
  ([Carpentier & Mansard 2018](https://doi.org/10.15607/RSS.2018.XIV.038)), 배치 동역학의
  GPU 구현. 이 질문은 `c2-dynamics-derivatives-sysid` 에서 다시 나온다.

## 개념 점검

`rc quiz c2-crba-aba` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위 문제 세트와
재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c2-crba-aba-quiz
questions:
  - id: q1
    type: single
    prompt: "$M_{ij} = 0$ 이 **구조적으로** 보장되는 경우는?"
    choices:
      - "$|i - j| > 1$ 일 때"
      - "바디 $i$ 와 $j$ 가 서로 다른 분기에 있을 때(어느 쪽도 다른 쪽의 조상이 아닐 때)"
      - "$i \\ne j$ 일 때 항상"
      - "관절 축 $S_i$ 와 $S_j$ 가 직교할 때"
    answer: 1
    explanation: "$M_{ij} = \\sum_k J_{k,i}^{\\top}I_kJ_{k,j}$ 의 합은 $k \\in \\nu(i)\\cap\\nu(j)$ 에서만 살아 있고, 트리에서 두 부분나무의 교집합은 둘 중 하나가 다른 쪽을 포함하거나 비어 있다. 다른 분기면 교집합이 공집합이라 정확히 0 이다. 축 직교는 특정 기하의 우연한 0 이고 구조적 보장이 아니다."
    concept: { front: "$M$ 의 구조적 영 패턴", back: "조상 관계가 결정한다 — 다른 분기의 $M_{ij}$ 는 정확히 0. 상삼각 비영 개수 $= \\sum_i(1+\\mathrm{depth}(i))$" }
  - id: q2
    type: single
    prompt: "직렬 연쇄 $n$ 자유도에서 CRBA 의 비용 차수는?"
    choices: ["$\\Theta(n)$", "$\\Theta(n\\log n)$", "$\\Theta(n^2)$", "$\\Theta(n^3)$"]
    answer: 2
    explanation: "비용은 $\\Theta(\\sum_i(1+\\mathrm{depth}(i)))$ 이고 직렬 연쇄에서 $\\mathrm{depth}(i) = i-1$ 이므로 $n(n+1)/2 = \\Theta(n^2)$ 다. 이것은 $M$ 의 상삼각 비영원소 개수와 같으므로 CRBA 는 출력 최적이다 — 더 싸게 $M$ 을 만들 수는 없다. 성형 트리에서는 $\\Theta(n)$ 으로 떨어진다."
    concept: { front: "CRBA 의 비용", back: "$\\Theta(\\mathrm{nnz}_{\\triangle}(M)) = \\Theta(\\sum_i(1+\\mathrm{depth}(i)))$ — 직렬 $n^2$, 균형 트리 $n\\log n$, 성형 $n$" }
  - id: q3
    type: short
    prompt: "$I^a_j = I^A_j - U_jU_j^{\\top}/d_j$ 에 관절 축 $S_j$ 를 곱하면? (값 하나)"
    answer: ["0", "zero", "영", "영벡터", "0 벡터", "zero vector"]
    explanation: "$I^a_jS_j = I^A_jS_j - U_j(U_j^{\\top}S_j)/d_j = U_j - U_jd_j/d_j = 0$. 뜻: $\\ddot{q}_j$ 를 소거한 뒤 부모가 보는 관성은 관절 축 방향으로 정확히 특이하다 — 자유 관절은 그 방향으로 힘을 전달하지 않는다. 그래서 $I^a_j$ 는 양반정치이지만 양정치가 아니고, Cholesky 로 검증하면 실패한다."
    concept: { front: "$I^a_jS_j$ 의 값", back: "정확히 0 — 자유 관절 방향으로는 힘이 전달되지 않는다. $I^a_j \\succeq 0$ (양정치 아님)" }
  - id: q4
    type: single
    prompt: "ABA 의 $d_i = S_i^{\\top}I^A_iS_i$ 는 $M$ 의 무엇과 같은가?"
    choices:
      - "$M_{ii}$"
      - "진자손 블록 $\\mathcal{D}(i)$ 를 소거한 Schur 보완"
      - "$(M^{-1})_{ii}$"
      - "$M$ 의 $i$ 번째 고윳값"
    answer: 1
    explanation: "$d_i = M_{ii} - M_{i\\mathcal{D}}M_{\\mathcal{D}\\mathcal{D}}^{-1}M_{\\mathcal{D}i}$ — 자손 관절은 자유롭게, 조상 관절은 고정했을 때 관절 $i$ 에서 느껴지는 관성이다. $M \\succ 0$ 에서 $0 < d_i \\le M_{ii}$ 이고 리프에서만 $d_i = M_{ii}$ 다. 그래서 ABA 는 트리 순서로 $M$ 을 소거하는 fill-in 없는 희소 소거와 같다."
    concept: { front: "$d_i$ 의 정체", back: "$M$ 의 Schur 보완(자손 블록 소거). $0 < d_i \\le M_{ii}$, 리프에서 등호. ABA = fill-in 0 희소 소거" }
  - id: q5
    type: multiple
    prompt: "ABA 가 0 으로 나누지 않는다($d_i > 0$)는 보장에 **실제로 쓰이는** 사실을 모두 고르라."
    choices:
      - "모든 바디의 $I_i$ 가 양정치다 (질량 > 0)"
      - "합동 변환 $X^{\\top}I^aX$ 가 양반정치성을 보존한다"
      - "양정치 행렬의 Schur 보완이 양반정치다"
      - "$M$ 을 명시적으로 만들어 Cholesky 를 한다"
    answer: [0, 1, 2]
    explanation: "리프에서 $I^A_i = I_i \\succ 0$ 으로 시작하고, 각 단계에서 Schur 보완 보조정리로 $I^a_i \\succeq 0$, 합동 변환으로 그 양반정치성이 부모 좌표에서도 유지되며, 양정치 + 양반정치 = 양정치로 귀납이 올라간다. ABA 는 $M$ 을 만들지 않는다 — 그것이 $\\Theta(n)$ 인 이유다. 질량 0 링크가 있으면 리프에서 $d_i = 0$ 이 되어 이 보장이 깨진다."
    concept: { front: "$d_i > 0$ 의 근거", back: "$I_i \\succ 0$ + Schur 보완 보조정리 + 합동 변환의 양정치 보존, 리프→루트 귀납. 질량 0 링크에서 깨진다" }
```

## 이 단계 공부법

1. **앞 레슨의 두 식만 꺼내 둔다 (15분)** — $M = \sum_kJ_k^\top I_kJ_k$ 와
   $J_{i,k} = {}^iX_kS_k$ (조상일 때). R1 은 이 둘에서 **합의 범위를 따지는 것**뿐이다.
2. **트리를 그려 영 패턴을 손으로 칠한다 (30분)** — 바디 6개쯤의 분기 트리를 그리고
   $6\times6$ 격자에 비영 자리를 칠해 (3)을 직접 세어 보라. 그 다음 같은 트리를 직렬로
   펴서 격자가 꽉 차는 것을 보라. **CRBA 의 비용이 모양에 의존한다**는 사실이 눈에 들어온다.
3. **R3 을 백지에서 쓴다 (90분)** — (8)을 정의로 적고, 1→2→3단계(관절 방정식 → Schur 소거
   → 부모로 올리기)를 순서대로 전개한다. 막히는 지점은 거의 항상 2단계에서 $a'_j + c_j$ 를
   묶지 않고 $c_j$ 를 따로 떼는 것이다(문제 P2 ⓐ 가 그 지점이다).
4. **R4 를 두 방향으로 확인한다 (50분)** — 먼저 선형대수로(Schur 보완), 그 다음 **수치로**
   2링크에서 $d_1 = M_{11} - M_{12}^2/M_{22}$ 를 손계산해 공개 수치와 맞춰 보라. 이 등식이
   맞는 순간 "ABA 는 희소 소거다"가 비유가 아니라 등식으로 읽힌다.
5. **먼저 틀리게 구현한다 (70분)** — P6 을 쓸 때 ⓐ $I^A_jc_j$ (하향 수정 전) ⓑ 누적을
   루트→리프 ⓒ $M_{ij}$ 와 $M_{ji}$ 를 따로 계산 세 버전을 만들어 재현 과제의 어느 조건이
   깨지는지 표로 적어라. 진단표의 처음 세 줄이 이 실험이다.
6. **재현 과제를 끝낸다 (120분)** — 조건 4 가 이 레슨의 핵심이다. 특히 ⓒ 에서
   $\lambda_{\min}(I^a)$ 가 **음수로 나오는 것이 정상**이라는 것을 직접 보고, 그 값이 (6)의
   정확한 0 의 반올림임을 $I^a S$ 로 확인하라. "양정치를 Cholesky 로 검증한다"는 습관이
   여기서 한 번 깨져야 한다.
7. **논문 2편을 1년 간격으로 읽는다 (120분)** — Walker & Orin 1982 의 Method 1–4 비교를
   먼저 읽어 "왜 $M$ 을 싸게 만드는 것이 문제였는가"를 보고, Featherstone 1983 에서 "애초에
   $M$ 을 만들지 않는" 전환을 본다. 두 논문 모두 하한을 다루지 않는다는 점(P7 ⓐ)을 노트에 적어라.
8. **무엇을 못 하는지로 끝낸다 (20분)** — 열린 문제 중 소거 순서 쪽을 골라, 트리 순서가
   fill-in 에는 최적이지만 조건수에는 왜 최적이 아닐 수 있는지 한 문단으로 쓴다.
   `r0-sparse-linear-algebra` 의 COLAMD 실험과 나란히 두면 질문이 또렷해진다.

**통과 기준**: 백지에서 (1)(2)(4)(5)(10)을 쓸 수 있고, R3 의 세 단계와 R5 의 귀납을 말할 수
있고, 재현 과제 네 조건을 통과하는 `crba`·`aba` 를 갖고 있고, 논문 2편의 1페이지 노트가 있다.
