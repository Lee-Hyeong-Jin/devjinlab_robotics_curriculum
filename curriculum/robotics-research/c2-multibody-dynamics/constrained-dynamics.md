---
id: c2-constrained-dynamics
title: 제약 동역학과 조작 공간 관성
summary: >-
  홀로노믹 제약이 있는 다물체계의 운동 방정식을 라그랑주 승수가 들어간 KKT 꼴로 세우고 해의
  존재·유일성을 증명하고, Gauss 의 최소 제약 원리로 그 해를 "제약 없는 가속도의 $M$-가중
  투영"으로 다시 읽고, 조작 공간 관성 $\Lambda$ 와 동적으로 일관된 널공간 투영을 유도한다.
  축소좌표법과의 동등성, 그리고 Baumgarte 안정화의 오차 ODE 까지 간다.
objectives:
  - 제약 동역학을 KKT 꼴로 세우고 KKT 행렬이 비특이인 필요충분조건을 증명할 수 있다.
  - 승수의 명시해 $\lambda = \Lambda(k - JM^{-1}(\tau-b))$ 를 유도하고 $\Lambda$ 의 두 가지 읽기를 설명할 수 있다.
  - Gauss 의 최소 제약 원리를 KKT 조건으로 환원해 제약 가속도의 변분적 의미를 말할 수 있다.
  - 동적으로 일관된 유사역행렬 $\bar{J}$ 와 널공간 투영 $N^\top$ 을 유도하고 널공간 토크가 과제 가속도를 만들지 않음을 증명할 수 있다.
  - Baumgarte 안정화가 제약 오차에 어떤 ODE 를 부과하는지 유도하고 적분기 오차와 구별할 수 있다.
prerequisites: [c2-crba-aba]
difficulty: 5
estimated_minutes: 600
tags: [multibody-dynamics, constraints, kkt, operational-space, null-space, baumgarte, research]
activities:
  - id: c2-constrained-dynamics-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 105
  - id: c2-constrained-dynamics-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c2-constrained-dynamics-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 2 · 계산 1 · 구현 1 · 논문 1)
    estimated_minutes: 180
  - id: c2-constrained-dynamics-reproduction
    kind: reproduction
    title: 재현 과제 — 폐루프 4절 링크를 승수법·축소좌표법으로 적분 (R2)
    estimated_minutes: 150
  - id: c2-constrained-dynamics-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Featherstone, Rigid Body Dynamics Algorithms (2008)"
    url: https://doi.org/10.1007/978-0-387-74315-8
    kind: book
    note: ch.8 (Closed Loop Systems). 루프 폐쇄 제약, 승수법, 축소좌표법의 표준 서술.
  - title: "Murray, Li & Sastry, A Mathematical Introduction to Robotic Manipulation"
    kind: book
    note: ch.6 (Multifingered Hand Kinematics)·ch.5. 제약과 그래스프 행렬. (공식 URL 미확인)
  - title: "Boyd & Vandenberghe, Convex Optimization"
    url: https://web.stanford.edu/~boyd/cvxbook/
    kind: book
    note: 권장. ch.5 (쌍대성·KKT), App. A.5.5 (Schur 보완). 승수를 KKT 조건으로 읽을 때의 배경. 전문 PDF 무료.
  - title: "Featherstone — Spatial vector and rigid-body dynamics software"
    url: https://royfeatherstone.org/spatial/
    kind: code
    note: 권장. 폐루프 예제(`fbkin`, 루프 폐쇄 함수). 재현 과제의 선택 교차 검증용(Octave).
papers:
  - id: khatib1987-operational-space
    role: seminal
    required: true
  - id: udwadia1992-constrained-motion
    role: standard
    required: true
  - id: baumgarte1972-constraint-stabilization
    role: seminal
    required: true
---

# 제약 동역학과 조작 공간 관성

## 전제와 기호

`c2-crba-aba` 까지의 결과를 전제한다. 특히 $M(q) \succ 0$ 과, $M$ 과 편향·중력 항
$b(q,\dot q) := C\dot q + g$ 를 각각 CRBA·RNEA 로 $\Theta(n^2)$·$\Theta(n)$ 에 계산할 수
있다는 것. 이 레슨은 **관절 공간**(일반화 좌표) 수준에서만 다루므로 6D 공간 벡터는 $M$, $b$,
$J$ 를 만드는 데만 쓰인다.

| 기호 | 뜻 |
|---|---|
| $q \in \mathbb{R}^n$ | 일반화 좌표. 트리 좌표계(폐루프는 절단해 트리로 만든 뒤 제약으로 다시 묶는다) |
| $\phi(q) \in \mathbb{R}^m$ | 홀로노믹 제약. $\phi(q) = 0$ 이 제약 다양체를 정의한다 |
| $J := \partial\phi/\partial q \in \mathbb{R}^{m\times n}$ | 제약 야코비안. **행 완전계수**를 가정한다(아니면 R1 의 반례) |
| $k := -\dot{J}\dot q \in \mathbb{R}^m$ | 가속도 수준 제약의 우변. $\ddot\phi = J\ddot q + \dot J\dot q = 0$ 에서 |
| $\lambda \in \mathbb{R}^m$ | 라그랑주 승수 = 제약력. 부호 규약은 $M\ddot q + b = \tau + J^\top\lambda$ |
| $a_u := M^{-1}(\tau - b)$ | **제약 없는** 가속도(unconstrained acceleration) |
| $\Lambda := (JM^{-1}J^\top)^{-1} \in \mathbb{R}^{m\times m}$ | 제약 공간 관성 / **조작 공간 관성**. $\Lambda^{-1}$ 은 Delassus 연산자 |
| $\bar J := M^{-1}J^\top\Lambda \in \mathbb{R}^{n\times m}$ | **동적으로 일관된**(dynamically consistent) 유사역행렬 |
| $N^\top := \mathbb{1}_n - J^\top\bar J^\top$ | 토크 공간의 널공간 투영자 |
| $G(q) \in \mathbb{R}^{n\times(n-m)}$ | $J$ 의 영공간 기저($JG = 0$). 축소좌표 $u$ 의 접사상 |
| $\alpha, \beta > 0$ | Baumgarte 이득(각각 속도·위치 수준) |

**부호 규약 경고**: 이 레슨은
$$
M\ddot q + b = \tau + J^\top\lambda, \qquad J\ddot q = k \tag{1}
$$
를 쓴다. 즉 $\lambda$ 는 **계에 작용하는** 제약력이다. 많은 문헌이 $M\ddot q + b = \tau - J^\top\lambda$
를 쓰고 그러면 $\lambda$ 의 부호가 전부 뒤집힌다 — 외부 구현과 수치를 맞출 때 **가장 먼저
확인할 것**이다(앞 레슨들의 성분 순서·$f_i$ 방향에 이어 세 번째 규약 함정이다).

제약의 출처는 세 가지이고 수식은 모두 같다: ⓐ **루프 폐쇄**(폐루프 기구를 절단해 트리로 만든
뒤 절단면을 다시 붙이는 제약) ⓑ **과제**(엔드이펙터를 어떤 궤적에 묶는 제약) ⓒ **접촉**
(비관통·비활주 제약 — 다만 접촉은 **부등식**이어서 다음 레슨이 따로 필요하다).
이 레슨은 ⓐ·ⓑ 를 다루고, ⓒ 로 가는 길목까지 간다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 — `lesson-standard.md` §2).

- **R1 (KKT 꼴과 해의 존재·유일성) [D3]** — (1)을 하나의 선형계로 쓰면
  $$
  \underbrace{\begin{bmatrix} M & -J^\top \\ J & 0 \end{bmatrix}}_{=:\,K}
  \begin{bmatrix} \ddot q \\ \lambda \end{bmatrix}
  = \begin{bmatrix} \tau - b \\ k \end{bmatrix}. \tag{2}
  $$
  $M \succ 0$ 이고 $J$ 가 **행 완전계수**이면 $K$ 는 비특이이고 해 $(\ddot q, \lambda)$ 는
  유일하다. $J$ 가 계수 결손이면 $\ddot q$ 는 (제약이 양립할 때) 여전히 유일하지만 $\lambda$ 는
  유일하지 않고, 제약이 양립하지 않으면 해가 **없다**.
- **R2 (명시해와 Gauss 의 최소 제약 원리) [D2]** — (2)를 Schur 보완으로 풀면
  $$
  \lambda = \Lambda\big(k - J\,a_u\big), \qquad
  \ddot q = a_u + M^{-1}J^\top\lambda = a_u + \bar J\big(k - J a_u\big). \tag{3}
  $$
  그리고 이 $\ddot q$ 는 **변분 문제**
  $$
  \ddot q = \arg\min_{x}\ \tfrac{1}{2}(x - a_u)^\top M\,(x - a_u) \quad \text{s.t.} \quad Jx = k \tag{4}
  $$
  의 해다(Gauss 의 최소 제약 원리). 즉 **제약 가속도는 제약 없는 가속도의 $M$-가중 투영**이고,
  $\lambda$ 는 그 제약의 승수다. Udwadia–Kalaba 형태는 (4)를 유사역행렬로 푼 것이어서
  계수 결손·과잉 제약도 다룬다.
- **R3 (조작 공간 관성과 동적으로 일관된 투영) [D3]** — $J$ 를 **과제** 야코비안으로 읽으면
  $\ddot x = J\ddot q + \dot J\dot q$ 이고 과제 공간의 운동 방정식은
  $$
  F = \Lambda\ddot x + \Lambda\big(J M^{-1} b - \dot J\dot q\big), \qquad \tau = J^\top F, \tag{5}
  $$
  즉 $\Lambda$ 가 과제점에서 느껴지는 **겉보기 관성**이다. 그리고 토크를
  $\tau = J^\top F + N^\top\tau_0$ 로 분해하면 널공간 토크 $N^\top\tau_0$ 는
  **과제 가속도를 전혀 만들지 않는다**:
  $$
  J M^{-1} N^\top = 0, \qquad J\bar J = \mathbb{1}_m. \tag{6}
  $$
  이것이 "동적으로 일관된"의 정확한 뜻이고, 기하적 유사역행렬 $J^{+} = J^\top(JJ^\top)^{-1}$ 은
  이 성질을 **갖지 않는다**.
- **R4 (축소좌표법과의 동등성) [D2]** — $G(q)$ 가 $J$ 의 영공간 기저이고 $w$ 가
  $Jw = k$ 의 아무 특수해일 때, (2)의 해는
  $$
  \big(G^\top M G\big)\,\ddot u = G^\top\big(\tau - b - M w\big), \qquad \ddot q = G\ddot u + w \tag{7}
  $$
  를 푼 것과 **같다**($G^\top J^\top = 0$ 때문에 승수가 소거된다). $G^\top MG \succ 0$ 이므로
  (7)은 $(n-m)$ 차원의 잘 정의된 계다. 축소좌표법은 제약을 **구조적으로** 만족시키므로
  제약 드리프트가 없지만, $G(q)$ 를 매 스텝 계산해야 하고 전역 매개화가 존재하지 않을 수 있다.
- **R5 (제약 드리프트와 Baumgarte 안정화) [D2 / 매개변수 선택은 D1]** — 가속도 수준 제약
  $J\ddot q = k$ 는 $\phi$ 와 $\dot\phi$ 를 **제어하지 않으므로** 수치 적분에서 둘이 발산한다
  (이중 적분기). $k$ 를
  $$
  k \;\longrightarrow\; k - 2\alpha\,\dot\phi - \beta^2\phi \tag{8}
  $$
  로 바꾸면 제약 오차 $e := \phi$ 가 **정확히**
  $$
  \ddot e + 2\alpha\dot e + \beta^2 e = 0 \tag{9}
  $$
  을 만족하므로 $\alpha, \beta > 0$ 에서 지수 안정이다. $\alpha = \beta$ 는 임계 감쇠이고
  해가 $e(t) = (e_0 + (\dot e_0 + \beta e_0)t)e^{-\beta t}$ 다. 다만 (9)가 보장하는 것은
  **주입된 오차의 감쇠**뿐이고, 정적분 중 실제 $\lVert\phi\rVert$ 의 크기는 **적분기의 국소
  오차**가 지배한다 — 둘을 혼동하는 것이 이 주제의 가장 흔한 오류다(재현 과제 조건 4). **[D1]**

## 유도

### R1·R2 — KKT 꼴과 명시해

$\phi(q(t)) = 0$ 을 두 번 미분한다. 한 번: $\dot\phi = J\dot q = 0$. 두 번:

$$
\ddot\phi = J\ddot q + \dot J\dot q = 0 \;\;\Longleftrightarrow\;\; J\ddot q = -\dot J\dot q = k.
$$

여기서 $\dot J\dot q = \sum_{i,j}\frac{\partial^2\phi}{\partial q_i\partial q_j}\dot q_i\dot q_j$
이고 $\dot q$ 에 2차다 — 앞 레슨의 코리올리 항과 같은 종류의 항이다. 제약력은 가상 일의
원리에서 **제약에 수직**이어야 하므로($\delta q$ 가 $J\delta q = 0$ 을 만족하면 제약력이
일을 하지 않아야 한다) $J^\top$ 의 열공간에 있고, 따라서 $J^\top\lambda$ 꼴이다. 두 식을 쌓으면 (2)다.

(3)을 Schur 보완으로 푼다. (2)의 첫 행에서

$$
\ddot q = M^{-1}(\tau - b) + M^{-1}J^\top\lambda = a_u + M^{-1}J^\top\lambda,
$$

둘째 행에 대입하면

$$
J a_u + \underbrace{JM^{-1}J^\top}_{=\,\Lambda^{-1}}\lambda = k
\;\;\Longrightarrow\;\; \lambda = \Lambda(k - Ja_u),
$$

다시 첫 행에 넣으면 $\ddot q = a_u + M^{-1}J^\top\Lambda(k - Ja_u) = a_u + \bar J(k - Ja_u)$ 다.
$\bar J = M^{-1}J^\top\Lambda$ 가 여기서 **자연스럽게** 나온다는 것이 R3 의 복선이다.

**Gauss 의 최소 제약 원리 (4).** (4)의 KKT 조건을 쓰면 끝난다. 라그랑지안
$L(x,\mu) = \frac{1}{2}(x-a_u)^\top M(x-a_u) + \mu^\top(Jx - k)$ 에 대해

$$
\nabla_x L = M(x - a_u) + J^\top\mu = 0, \qquad Jx = k.
$$

$\mu = -\lambda$ 로 두면 이것이 정확히 (2)다. 목적함수가 $M \succ 0$ 으로 강볼록이고 제약이
아핀이므로 해는 유일하고 KKT 조건이 필요충분이다. 즉 **(2)와 (4)는 같은 문제**다.

이 읽기가 주는 것: ⓐ $\lVert\ddot q - a_u\rVert_M$ 이 **최소**라는 물리적 해석(Gauss 1829),
ⓑ 제약이 과잉이거나 양립하지 않을 때 (4)를 **최소제곱**으로 완화하는 자연스러운 길
(Udwadia–Kalaba 의 유사역행렬 형태), ⓒ 다음 레슨에서 접촉의 **부등식** 제약이 같은 변분
문제의 KKT 조건으로 확장되는 통로.

> **수치로 본 (4)**: 재현 과제의 4절 링크에서 KKT 해의 $\lVert\ddot q - a_u\rVert_M = 5.523095$
> 이고, $J x = k$ 를 만족하는 다른 점($\ddot q + \epsilon g$, $g \in \mathrm{null}(J)$)은
> $\epsilon = 0.1$ 에서 $5.523133$, $\epsilon = -0.3$ 에서 $5.523434$ — **엄격히 크다**.

### R3 — 조작 공간 관성과 널공간 투영

이제 $J$ 를 **과제** 야코비안으로 읽는다($x = h(q)$, $J = \partial h/\partial q$, $m \le n$).
제약이 아니라 **출력**이므로 (1)의 둘째 식이 없고, 대신 과제 가속도를 계산한다:

$$
\ddot x = J\ddot q + \dot J\dot q = J M^{-1}(\tau - b) + \dot J\dot q. \tag{10}
$$

과제 힘 $F$ 로 구동한다고 하면 $\tau = J^\top F$ 이고, (10)에 넣으면

$$
\ddot x = JM^{-1}J^\top F - JM^{-1}b + \dot J\dot q = \Lambda^{-1}F - JM^{-1}b + \dot J\dot q,
$$

$F$ 에 대해 풀면 (5)다. $\Lambda$ 가 $\ddot x$ 의 계수이므로 **과제점에서 느껴지는 관성**이고,
$\Lambda^{-1} = JM^{-1}J^\top$ 은 "단위 과제 힘이 만드는 과제 가속도", 즉 접촉·제약 문헌의
**Delassus 연산자**다. 같은 행렬을 제약으로 읽으면 R2 의 $\Lambda$ 이고, 과제로 읽으면 Khatib 의
조작 공간 관성이다 — **두 읽기가 같은 식**이라는 점이 이 레슨의 축이다.

**널공간 투영 (6).** $J\bar J = JM^{-1}J^\top\Lambda = \Lambda^{-1}\Lambda = \mathbb{1}_m$ 이므로
$\bar J$ 는 $J$ 의 우역행렬(유사역행렬)이다. $N^\top = \mathbb{1} - J^\top\bar J^\top$ 에 대해

$$
JM^{-1}N^\top = JM^{-1} - JM^{-1}J^\top\bar J^\top
= JM^{-1} - \Lambda^{-1}\big(M^{-1}J^\top\Lambda\big)^\top
= JM^{-1} - \Lambda^{-1}\Lambda J M^{-1} = 0,
$$

($\Lambda$ 와 $M$ 이 대칭이므로 $\bar J^\top = \Lambda JM^{-1}$). (10)에서 $\tau = N^\top\tau_0$
를 넣으면 $\ddot x$ 의 토크 기여가 $JM^{-1}N^\top\tau_0 = 0$ 이다 — **널공간 토크는 과제
가속도를 바꾸지 않는다**. 그래서 $\tau = J^\top F + N^\top\tau_0$ 가 과제와 자세(posture)를
**분리**해서 제어할 수 있는 분해가 된다(Khatib 1987 의 핵심).

**기하적 유사역행렬과의 대비.** $J^{+} = J^\top(JJ^\top)^{-1}$ 을 쓰면
$JM^{-1}(\mathbb{1} - J^\top (J^{+})^\top)\ne 0$ 이 일반적으로 성립한다 — 즉 "널공간" 토크가
과제를 흔든다. $J^{+}$ 는 $\lVert\dot q\rVert_2$ 를 최소화하고 $\bar J$ 는
$\lVert\cdot\rVert_M$(운동 에너지)을 최소화하므로, **동역학 문제에서 올바른 계량은 $M$ 이다**.
$M = \mathbb{1}$ 인 특수한 경우에만 둘이 일치한다(문제 P3).

### R4 — 축소좌표법

$J$ 의 영공간 기저 $G(q)$ ($JG = 0$, $\mathrm{rank}\,G = n-m$)를 잡는다. 제약을 만족하는
가속도는 $\ddot q = G\ddot u + w$ ($Jw = k$ 인 특수해) 꼴로 전부 쓸 수 있다. (1)의 첫 식에
넣고 **왼쪽에 $G^\top$ 을 곱하면**

$$
G^\top M G\,\ddot u + G^\top M w + G^\top b = G^\top\tau + \underbrace{G^\top J^\top}_{=\,0}\lambda,
$$

즉 (7)이다. **승수가 사라진 것**이 요점이고, 그 이유는 제약력이 제약 다양체의 접공간에
수직이기 때문이다(가상 일의 원리의 대수적 형태). $G$ 가 완전계수이고 $M \succ 0$ 이므로
$G^\top MG \succ 0$ 이라 (7)은 유일해를 갖는다.

**두 방법의 교환**:

| | 승수법 (2) | 축소좌표법 (7) |
|---|---|---|
| 계의 크기 | $(n+m) \times (n+m)$, 부정부호(indefinite) | $(n-m)\times(n-m)$, 양정치 |
| 제약 만족 | 가속도 수준만 — **드리프트한다** | 구조적으로 만족 — 드리프트 없음 |
| $\lambda$ | 직접 얻는다(접촉력·관절 반력 모니터링에 필요) | 따로 복원해야 한다 |
| 비용 | $K$ 를 분해. 희소 구조를 쓰면 $O(n + m^3)$ 류 | $G$ 계산 + $(n-m)^3$. $G$ 가 비싸다 |
| 함정 | 드리프트, $J$ 계수 결손에서 특이 | $G(q)$ 의 **게이지**(기저가 매끄럽게 선택되지 않을 수 있다), 전역 매개화의 부재 |

$G$ 의 게이지 문제는 실무에서 자주 사람을 잡는다: SVD 나 QR 로 매 스텝 $G$ 를 다시 구하면
부호·열 순서가 튀어 $\dot u$ 가 불연속이 된다. 재현 과제는 그래서 $\ddot u$ 를 적분하지 않고
$\ddot q = G\ddot u + w$ 를 **$\ddot q$ 수준에서만** 비교한다.

### R5 — Baumgarte 안정화의 오차 ODE

(2)의 둘째 식은 $\ddot\phi = 0$ 이다. 이것은 $\phi$ 에 대한 **이중 적분기**이므로, 초기 오차나
반올림이 들어오면 $\phi(t) = \phi_0 + \dot\phi_0 t$ 로 **선형 증가**한다. 감쇠가 전혀 없다.

(8)로 바꾸면 둘째 식이 $J\ddot q = -\dot J\dot q - 2\alpha\dot\phi - \beta^2\phi$ 이고,
$\ddot\phi = J\ddot q + \dot J\dot q$ 를 대입하면 **정확히**

$$
\ddot\phi + 2\alpha\dot\phi + \beta^2\phi = 0,
$$

즉 (9)다. 특성근은 $-\alpha \pm \sqrt{\alpha^2 - \beta^2}$ 이므로

- $\alpha > \beta$: 과감쇠, 느린 근 $\approx -\beta^2/(2\alpha)$ 가 수렴을 지배한다.
- $\alpha = \beta$: **임계 감쇠**, 이중근 $-\beta$, 해 $e(t) = (e_0 + (\dot e_0 + \beta e_0)t)e^{-\beta t}$.
- $\alpha < \beta$: 진동하며 감쇠.

**$\alpha = \beta$ 를 쓰고 $\beta$ 를 "시간 상수 $1/\beta$ 가 적분 스텝보다 충분히 크고 관심
있는 동역학보다 충분히 빠르게"** 고르는 것이 표준 조언이다. $\beta$ 를 크게 하면 계가
**강성(stiff)**이 되어 명시적 적분기의 안정 영역을 벗어난다($\beta\,\Delta t \lesssim 1$ 류의
제한) — 안정화를 세게 할수록 적분이 불안정해지는 교환이다. **[D1]**

**가정이 깨지는 곳 — 가장 흔한 오류.** (9)는 "주입된 오차가 지수적으로 사라진다"만 말한다.
적분 중 매 스텝 새로 생기는 오차(적분기의 국소 절단 오차)에 대해서는 **정상 상태 오차**가
남고 그 크기는 적분기 차수가 결정한다. 측정이 이것을 명확히 보여 준다(재현 과제 4절 링크, 2초):

| 적분기 | $\Delta t$ | 안정화 | $\max\lVert\phi\rVert$ |
|---|---|---|---|
| semi-implicit Euler | $10^{-3}$ | 없음 | $1.5\times10^{-2}$ |
| semi-implicit Euler | $10^{-3}$ | $\alpha=\beta=20$ | $2.2\times10^{-3}$ |
| RK4 | $10^{-3}$ | 없음 | $4.9\times10^{-7}$ |
| RK4 | $10^{-3}$ | $\alpha=\beta=20$ | $1.9\times10^{-9}$ |
| RK4 | $10^{-4}$ | $\alpha=\beta=20$ | $1.9\times10^{-13}$ |
| 아무 적분기 + **좌표 투영** | $10^{-3}$ | 불필요 | $1.0\times10^{-14}$ |

읽는 법: 1차 적분기에서는 Baumgarte 를 켜도 $10^{-3}$ 수준에 머문다 — 병목이 안정화가 아니라
**적분기**다. 4차 적분기에서는 같은 안정화가 $10^{-9}$ 를 준다. 그리고 **좌표 투영**
(매 스텝 $\phi(q) = 0$ 에 Newton 으로 되돌리고 $\dot q$ 를 $\mathrm{null}(J)$ 에 투영)은
적분기와 무관하게 Newton 허용오차 수준을 준다. 실무 권고: 안정화는 "오차를 작게 유지"하는
수단이 아니라 "주입된 오차를 없애는" 수단으로 쓰고, 엄격한 제약이 필요하면 **투영**을 쓴다.

## 증명 스케치

### R1 — KKT 행렬의 비특이성

**가설** H1: $M = M^\top \succ 0$. H2: $J \in \mathbb{R}^{m\times n}$ 이 행 완전계수
($\mathrm{rank}\,J = m \le n$). **결론** C1: $K$ 가 비특이. C2: $\Lambda^{-1} = JM^{-1}J^\top \succ 0$.
C3: H2 가 깨지면 무엇이 깨지는가.

**전략**: 영공간이 자명함을 직접 보인다. 한 줄 계산이고, 어떤 가설이 어디서 쓰이는지가 또렷하다.

1. **영공간.** $K\begin{bmatrix}x\\y\end{bmatrix} = 0$ 이라 하자. 첫 블록은 $Mx = J^\top y$,
   둘째는 $Jx = 0$.
2. **$x = 0$.** 첫 식에 $x^\top$ 을 곱하면
   $x^\top Mx = x^\top J^\top y = (Jx)^\top y = 0$. H1 에서 $x^\top Mx = 0 \Rightarrow x = 0$.
   (**H1 이 쓰이는 유일한 지점**이고, 양반정치만으로는 부족하다.)
3. **$y = 0$.** 그러면 $J^\top y = Mx = 0$ 이고 H2 에서 $J^\top$ 이 열 완전계수이므로 $y = 0$.
4. **C2.** $\Lambda^{-1} = JM^{-1}J^\top$ 은 $M^{-1} \succ 0$ 의 합동 변환이고 $J^\top$ 이 열
   완전계수이므로 $y^\top JM^{-1}J^\top y = 0 \Rightarrow J^\top y = 0 \Rightarrow y = 0$,
   즉 양정치다. 따라서 (3)의 $\Lambda$ 가 존재한다.
5. **C3 — 가설을 지우면.** H2 를 지우면 두 가지가 일어난다.
   (i) $J$ 가 계수 결손이지만 제약이 **양립**하면($k \in \mathrm{range}(J)$) $\ddot q$ 는
   여전히 유일하다 — (4)의 목적함수가 강볼록이고 가능 집합이 비지 않았기 때문이다. 그러나
   $\lambda$ 는 $\mathrm{null}(J^\top)$ 만큼의 자유도를 갖는다(**제약력이 정해지지 않는다** —
   과잉 구속된 폐루프에서 실제로 일어나는 일이고, 측정 가능한 것은 $J^\top\lambda$ 뿐이다).
   (ii) 양립하지 않으면($k \notin \mathrm{range}(J)$) 해가 **없다**. (2)는 모순이고 수치
   해법은 거대한 $\lambda$ 를 뱉는다.
   두 경우 모두 Udwadia–Kalaba 의 유사역행렬 형태가 자연스러운 답을 준다 —
   (4)를 $\min\lVert Jx - k\rVert$ 로 완화한 최소제곱 해다. 생략: 유사역행렬 형태의 전개는
   Udwadia & Kalaba 1992 의 유사역행렬 절.

### R3 — 동적 일관성은 $M$-계량의 유일한 선택이다

**가설** H1: $M \succ 0$, $J$ 행 완전계수. H2: $A \in \mathbb{R}^{n\times m}$ 이 $J$ 의 우역행렬
($JA = \mathbb{1}_m$). **결론** C: $JM^{-1}(\mathbb{1} - J^\top A^\top) = 0$ 이 모든 과제에서
성립하는 것은 $A = \bar J = M^{-1}J^\top\Lambda$ 일 때**뿐**이다.

**전략**: 조건을 $A$ 에 대한 선형 방정식으로 바꾸고 유일성을 본다.

1. **조건을 정리.** $JM^{-1}(\mathbb{1} - J^\top A^\top) = 0 \iff JM^{-1} = JM^{-1}J^\top A^\top
   = \Lambda^{-1}A^\top$, 즉 $A^\top = \Lambda J M^{-1}$, 즉 $A = M^{-1}J^\top\Lambda = \bar J$.
2. **일관성 확인.** 그 $A$ 가 H2 를 만족하는지: $J\bar J = \Lambda^{-1}\Lambda = \mathbb{1}_m$ ✓.
3. **유일성.** 1단계가 동치 변형이므로 다른 $A$ 는 없다. 즉 "널공간 토크가 과제를 흔들지
   않는다"를 요구하면 유사역행렬이 **$M$-가중으로 결정된다**.
4. **변분적 읽기.** $\bar J$ 는 $\min \lVert\dot q\rVert_M^2$ s.t. $J\dot q = \dot x$ 의 해
   연산자이기도 하다(R2 의 (4)와 같은 꼴). 즉 동적 일관성 = 운동 에너지 최소 = $M$-가중 투영.
   생략: 두 특징(널공간 비간섭 / 에너지 최소)이 동치임의 상세는 Khatib 1987 의 조작 공간 절.
5. **가설을 지우면.** $M = \mathbb{1}$ 이면 $\bar J = J^{+}$ 로 기하적 유사역행렬과 일치한다 —
   그래서 질량이 균일하다고 **착각하면** 차이가 보이지 않는다. $J$ 가 특이점에 가까우면
   $\Lambda^{-1}$ 이 특이에 가까워 $\Lambda$ 가 폭발하고 (5)의 $F$ 가 발산한다. 이것이
   **동역학적 특이점**이고 감쇠 유사역행렬(damped least squares)이 필요한 지점이다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1·R2)** ⓐ $\dot J\dot q$ 를 $\phi$ 의 2차 도함수로 명시적으로 쓰고,
그것이 $\dot q$ 에 2차임을 보이라. ⓑ (3)에서 $m = n$ (완전 구속)이면 $\ddot q$ 가 $\tau$ 와
무관해지는 것을 보이고, 그때 $\lambda$ 가 무엇을 뜻하는지 쓰라. ⓒ 부호 규약을
$M\ddot q + b = \tau - J^\top\lambda$ 로 바꾸면 (2)(3)이 어떻게 바뀌는지 모두 다시 쓰라.
*해답 스케치*: ⓐ 는 연쇄율로 $\frac{d}{dt}(J\dot q)$ 를 전개한다.
ⓑ 는 $J$ 가 정칙이라 $\ddot q = J^{-1}k$ — 가속도가 기하만으로 정해지고 $\tau$ 는 전부
$\lambda$ 로 흡수된다. ⓒ 는 $\lambda \to -\lambda$ 뿐이지만 **직접 다 써 보는 것**이 요점이다.

**P2 (유도, ★★, R4·R5)** ⓐ (7)에서 $w$ 의 선택이 $\ddot q$ 에 영향을 주지 않음을 보이라
($w$ 를 $w + Gz$ 로 바꿔도 같은 $\ddot q$ 가 나온다). ⓑ Baumgarte 를 **속도 수준에만**
($\alpha > 0$, $\beta = 0$) 쓰면 어떤 ODE 가 되고 무엇이 보장되지 않는지 쓰라.
ⓒ (9)의 해를 $\alpha = \beta$ 에서 명시적으로 쓰고, $\dot e_0 = 0$, $e_0 = 10^{-3}$,
$\beta = 20$ 에서 $t = 0.2$ 의 $e$ 를 계산하라.
*해답 스케치*: ⓐ 는 $G\ddot u$ 가 $Gz$ 를 흡수하도록 $\ddot u$ 가 조정된다는 것 —
(7)의 해가 $w$ 에 **아핀 의존**하지만 합이 불변이다. ⓒ 의 정답은
$e(0.2) = 10^{-3}(1 + 4)e^{-4} = 9.158\times10^{-5}$ (측정값 $9.075\times10^{-5}$ 와 1% 이내).

**P3 (증명, ★★★, R3)** ⓐ 기하적 유사역행렬 $J^{+} = J^\top(JJ^\top)^{-1}$ 로 만든 "널공간"
투영이 과제 가속도를 **만든다**는 것을 $2$ 자유도 구체 예로 보이라($M$ 을 비대각으로 잡아야 한다).
ⓑ $\bar J$ 가 $\min\lVert\dot q\rVert_M^2$ s.t. $J\dot q = \dot x$ 의 해 연산자임을 증명하라.
ⓒ $M = \mathbb{1}$ 일 때만 $\bar J = J^{+}$ 임을 보이고, "$M$ 이 거의 스칼라 배"일 때 두 투영의
차가 어떤 양으로 가늠되는지 쓰라(힌트: $M$ 의 조건수).
*전략 + 핵심 부등식*: ⓐ 는 $JM^{-1}(\mathbb{1} - J^\top(J^{+})^\top)$ 를 직접 계산해 0 이 아님을
보인다. ⓑ 는 R2 의 (4)와 같은 KKT 계산이다. 전개는 숨긴다.

**P4 (증명, ★★★, R1)** ⓐ $J$ 가 계수 결손이고 제약이 양립할 때 $\ddot q$ 는 유일하지만
$\lambda$ 는 유일하지 않음을 증명하라. ⓑ 과잉 구속된 폐루프의 구체 예(평면 4절 링크에
중복 제약 1개를 더 건 것)를 만들고, 그 경우 **물리적으로 측정 가능한 양**이 무엇인지 쓰라.
ⓒ 제약이 양립하지 않을 때 (4)의 최소제곱 완화가 주는 $\ddot q$ 가 어떤 물리적 의미를 갖는지
논하라 — 그것이 올바른 모델인가?
*전략 + 핵심 부등식*: ⓐ 는 (4)의 강볼록성(유일성)과 $\mathrm{null}(J^\top) \ne \{0\}$
(비유일성)을 분리해 쓴다. ⓒ 는 함정이다 — 최소제곱 완화는 수학적으로 깔끔하지만
"양립하지 않는 제약"은 보통 **모델이 틀렸다는 신호**이고, 완화는 그 사실을 숨긴다.

**P5 (계산, ★, R1·R2·R3)** 평면 3링크 사슬을 루프 폐쇄로 묶은 4절 링크. 링크 길이
$l = (0.5, 0.4, 0.3)$, 질량 $(1.2, 0.9, 0.6)$, 각 링크는 균일 봉(질량중심은 중점,
$\bar I_{zz} = m l^2/12$, 다른 성분 0), 관절은 모두 $z$ 축 회전, 중력은 $-y$ 방향 $9.81$.
제약은 선단이 $P_0 = (1.088822376457,\; 0.223713953272)$ 에 고정
($= \mathrm{tip}(0.6, -0.9, 0.5)$ 이므로 $q_0 = (0.6, -0.9, 0.5)$ 에서 $\phi = 0$).
$\dot q_0 = (0.103360934922,\; 0.001584047916,\; -0.386411707799)$ (제약 양립,
$\lVert\dot q_0\rVert_2 = 0.4$), $\tau = (1.5, -0.3, 0.2)$ 에서 $k$, $\Lambda$, $\lambda$,
$\ddot q$ 를 구하라.
*정답* (허용오차 $10^{-9}$):
$k = (0.031910645927,\; 0.006436080303)$,
$\Lambda = \begin{bmatrix} 1.349861612345 & 0.307260140613 \\ 0.307260140613 & 0.266141510828\end{bmatrix}$,
$\lambda = (6.011670352967,\; 2.224022466169)$,
$\ddot q = (-15.157426569392,\; -0.062542538530,\; 56.297092789389)$.
*검산*: ⓐ $\lVert J\dot q_0\rVert_\infty < 10^{-13}$ ⓑ $\lVert J\ddot q - k\rVert_\infty < 10^{-13}$
ⓒ $\Lambda$ 가 대칭이고 $\lambda_{\min}(\Lambda) = 0.185088157799 > 0$
ⓓ $M\ddot q + b = \tau + J^\top\lambda$ 를 $10^{-12}$ 이내로 만족.

**P6 (구현, ★★, R1–R5)** ⓐ `constrained_accel(q, qd, tau, alpha, beta)` — (2)를 풀어
$(\ddot q, \lambda)$ 를 돌려준다. ⓑ `reduced_accel(q, qd, tau)` — (7)로 $\ddot q$ 만 돌려준다.
ⓒ `project(q, qd)` — $\phi(q) = 0$ 에 Newton 으로 투영하고 $\dot q$ 를 $\mathrm{null}(J)$ 에 투영한다.
ⓓ `operational_space(q)` — $\Lambda$, $\bar J$, $N^\top$ 을 돌려준다.
*루브릭*: ⓐ P5 의 수치를 $10^{-9}$ 이내로 재현 ⓑ ⓐ 와 ⓑ 의 $\ddot q$ 가 $10^{-12}$ 이내 일치
ⓒ `project` 가 20회 이내 Newton 반복에서 $\lVert\phi\rVert_\infty < 10^{-14}$ 달성
ⓓ (6)의 두 항등식을 단위 테스트로 검사 ⓔ $J$ 를 **해석적으로** 계산하고(유한차분 금지)
$\dot J\dot q$ 도 해석식을 쓴다 — 유한차분을 쓰면 재현 과제 조건 1 이 $10^{-9}$ 벽을 넘지 못한다
ⓕ 부호 규약이 docstring 에 적혀 있다.

**P7 (논문, ★★, R2·R3)** ⓐ Khatib 1987 이 $\bar J$ 를 도입하는 논증과 이 레슨 R3 의 유일성
증명을 비교하고, 저자가 유일성을 주장하는가 아니면 구성만 하는가를 쓰라.
ⓑ Udwadia & Kalaba 1992 의 결과를 (4)의 KKT 조건으로 번역하고, 저자들이 **유사역행렬**을
쓰는 덕분에 추가로 다룰 수 있게 되는 경우 2개를 쓰라.
ⓒ Baumgarte 1972 가 제시한 이득 선택 지침이 있는가? 없다면, 이 레슨 R5 의 표를 근거로
그 공백이 왜 55년 동안 메워지지 않았는지 한 문단으로 쓰라.
*루브릭*: ⓑ 에서 계수 결손(과잉 구속)과 비양립(모순) 두 경우를 짚으면 통과.
ⓒ 에서 "적분기 오차와 안정화 오차가 섞여 있어 이득만으로는 정해지지 않는다"에 도달하면 통과.
"논문이 오래되어서"만 쓰면 미달.

## 논문 읽기

**필독 3편.** 1972·1987·1992 — 같은 식 (2)를 **제약 안정화**, **제어 분해**, **변분 원리**
세 방향에서 읽은 논문들이다. 세 편을 같은 질문지로 읽고 "(2)의 어느 부분을 각자 자기 문제로
보았는가"를 한 단락으로 정리하는 것이 이 레슨의 읽기 목표다. 각 논문에 아래 고정 질문 10개로
1페이지 노트를 쓴다(`lesson-standard.md` §5). 3-pass 로 읽고 3번째 패스에서 질문 4·7·8 을
집중 공략한다.

1. **Khatib, "A unified approach for motion and force control of robot manipulators: the
   operational space formulation" (1987, IEEE J. Robotics and Automation)** — 역할:
   `원전(seminal)`. <https://doi.org/10.1109/JRA.1987.1087068>
   어느 절을 왜 읽는가: 조작 공간의 운동 방정식 (5)를 세우는 절과 동적으로 일관된 역행렬을
   도입하는 절. R3 의 유도와 1:1 로 대조하고, **저자가 어떤 성질을 요구해 $\bar J$ 를
   고르는지**에 집중한다.
   추가 질문: ⓐ 저자가 $\bar J$ 의 유일성을 주장하는가, 구성만 하는가?
   ⓑ 힘 제어와 운동 제어를 "통합"한다는 주장에서 통합되는 것은 정확히 무엇인가?
   ⓒ 저자가 동역학적 특이점($\Lambda$ 의 폭발)을 어떻게 다루는가?
2. **Udwadia & Kalaba, "A new perspective on constrained motion" (1992, Proc. R. Soc. A)** —
   역할: `표준(standard)`. <https://doi.org/10.1098/rspa.1992.0158>
   어느 절을 왜 읽는가: Gauss 의 원리에서 출발해 제약 가속도를 유사역행렬 한 줄로 쓰는 절.
   이 레슨 (4)가 그 출발점이고, 저자들의 결과는 (4)를 **최소제곱으로 완화**한 것이다.
   추가 질문: ⓐ 저자들의 식을 이 레슨의 $\Lambda$, $\bar J$ 로 옮기면 어떻게 되는가?
   ⓑ 비홀로노믹 제약까지 확장된다고 주장하는가 — 그 주장은 어떤 꼴의 제약에 한정되는가?
   ⓒ 저자들이 **다루지 않는** 것은 무엇인가(힌트: 부등식, 마찰)?
3. **Baumgarte, "Stabilization of constraints and integrals of motion in dynamical systems"
   (1972, Comput. Methods Appl. Mech. Eng.)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1016/0045-7825(72)90018-7>
   어느 절을 왜 읽는가: 제약 위반에 안정한 ODE 를 부과하는 아이디어 그 자체. 짧다.
   이 레슨 (8)(9)가 그 논문의 식이고, **이득 선택에 대해 논문이 무엇을 말하고 무엇을 말하지
   않는지**를 확인하는 것이 읽기의 목표다.
   추가 질문: ⓐ 저자의 동기가 천체역학(케플러 운동의 적분 보존)에서 왔다는 점이 다물체
   동역학으로의 이전에서 무엇을 바꾸는가? ⓑ 논문이 강성(stiffness) 문제를 인지하는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, 5분 이내, numpy(+ `scipy.linalg`
는 선택). 메모리 200MB 이내.

P5 의 4절 링크를 **승수법과 축소좌표법 두 가지로** 구현해 아래 **네 조건을 모두** 만족해야
통과다. 시뮬레이터는 쓰지 않는다.

**모델과 제약 — 이 레슨이 제공하는 핵심 코드.** 아래는 본문의 수치가 나온 코드의 핵심부다.
$M$, $b$ 는 앞 레슨의 `crba`·`rnea` 를 쓰고, $J$ 와 $\dot J\dot q$ 는 **해석적으로** 쓴다
(유한차분을 쓰면 조건 1 의 $10^{-12}$ 벽을 넘지 못한다).

```python
L = np.array([0.5, 0.4, 0.3])  # link lengths
MASS = np.array([1.2, 0.9, 0.6])


def tip(q):
    s = np.cumsum(q)
    return np.array([np.sum(L * np.cos(s)), np.sum(L * np.sin(s))])


def tip_jac(q):
    """dp/dq, shape (2, 3). Joint i moves every link k >= i."""
    s = np.cumsum(q)
    J = np.zeros((2, 3))
    for k in range(3):
        for i in range(k + 1):
            J[0, i] += -L[k] * np.sin(s[k])
            J[1, i] += L[k] * np.cos(s[k])
    return J


def tip_jdot_qd(q, qd):
    """Jdot qd: the part of d2p/dt2 that is quadratic in qd."""
    s, sd = np.cumsum(q), np.cumsum(qd)
    return np.array([np.sum(-L * sd**2 * np.cos(s)), np.sum(-L * sd**2 * np.sin(s))])


def constrained_accel(q, qd, tau, alpha=0.0, beta=0.0):
    """Solve (2). Sign convention: M qdd + b = tau + J^T lambda, J qdd = k."""
    M = crba(CHAIN, q)
    b = rnea(CHAIN, q, qd, np.zeros(3), A_GRAV)  # Coriolis + gravity
    J = tip_jac(q)
    k = -tip_jdot_qd(q, qd) - 2 * alpha * (J @ qd) - beta**2 * (tip(q) - P0)
    K = np.block([[M, -J.T], [J, np.zeros((2, 2))]])
    sol = np.linalg.solve(K, np.concatenate([tau - b, k]))
    return sol[:3], sol[3:], M, J, k  # qdd, lambda, M, J, k


def reduced_accel(q, qd, tau):
    """Solve (7): G^T M G udd = G^T (tau - b - M w), then qdd = G udd + w."""
    M = crba(CHAIN, q)
    b = rnea(CHAIN, q, qd, np.zeros(3), A_GRAV)
    J = tip_jac(q)
    G = np.linalg.svd(J)[2][2:].T  # a basis of null(J), shape (3, 1)
    w = np.linalg.pinv(J) @ (-tip_jdot_qd(q, qd))  # any particular solution of J w = k
    udd = np.linalg.solve(G.T @ M @ G, G.T @ (tau - b - M @ w))
    return G @ udd + w


def project(q, qd, tol=1e-14):
    """Coordinate projection: Newton onto phi = 0, then qd onto null(J)."""
    for _ in range(20):
        r = tip(q) - P0
        if np.abs(r).max() < tol:
            break
        q = q - np.linalg.pinv(tip_jac(q)) @ r
    G = np.linalg.svd(tip_jac(q))[2][2:].T
    return q, G @ (G.T @ qd)


def operational_space(q):
    """Lambda, the dynamically consistent inverse, and the null-space projector."""
    M, J = crba(CHAIN, q), tip_jac(q)
    Minv = np.linalg.inv(M)
    Lam = np.linalg.inv(J @ Minv @ J.T)
    Jbar = Minv @ J.T @ Lam
    return Lam, Jbar, np.eye(3) - J.T @ Jbar.T
```

`CHAIN` 은 앞 레슨의 모델 객체(부모 $[-1,0,1]$, 축 모두 $z$, 트리 변환
$X_{T,k} = \mathrm{Xtrans}(l_{k-1}e_x)$, 질량 속성은 P5)이고 `A_GRAV` $= (0,0,0,\,0,-9.81,0)$,
`P0` $= \mathrm{tip}(0.6,-0.9,0.5)$ 다. `reduced_accel` 이 `udd` 를 **적분하지 않는다**는 점에
주의하라 — $G$ 의 게이지가 불연속이므로 비교는 $\ddot q$ 수준에서만 한다(R4 의 표).

1. **한 점에서 두 방법의 일치와 제약 만족** — $q_0, \dot q_0, \tau$ (P5 의 값)에서
   $$
   \lVert \ddot q^{\text{KKT}} - \ddot q^{\text{reduced}} \rVert_\infty < 10^{-12},
   \qquad \lVert J\ddot q - k \rVert_\infty < 10^{-13},
   $$
   그리고 P5 의 $\Lambda$, $\lambda$, $\ddot q$ 를 $10^{-9}$ 이내로 재현.
   > 저자 환경 측정값: $2.1\times10^{-14}$, $9.5\times10^{-16}$.
   > $J$ 와 $\dot J\dot q$ 를 **해석적으로** 계산해야 이 수준이 나온다(P6 ⓔ).
2. **Gauss 의 최소 제약 원리** — ⓐ 정규방정식 잔차
   $\lVert M(\ddot q - a_u) - J^\top\lambda\rVert_\infty < 10^{-12}$ (측정값 $1.0\times10^{-14}$).
   ⓑ $\lVert\ddot q - a_u\rVert_M$ 을 계산하고(측정값 $5.523095$), $\mathrm{null}(J)$ 방향으로
   $\epsilon \in \{\pm0.1, \pm0.3, \pm 1\}$ 만큼 옮긴 **가능한** 점들의 $M$-노름이 모두
   **엄격히 크다**는 것을 보이라(측정값: $\epsilon = 0.1$ 에서 $5.523133$,
   $\epsilon = -0.3$ 에서 $5.523434$). 옮긴 점들이 여전히 $\lVert Jx - k\rVert_\infty < 10^{-14}$
   를 만족하는지 함께 확인한다.
   > 주의: ⓑ 를 수치 최적화기(SLSQP 등)로 검증하려 하면 **최적화기 자신의 허용오차**
   > (보통 $10^{-6}$ 수준)에 막힌다. 정규방정식 ⓐ 로 검증하라.
3. **조작 공간 관성과 동적 일관성** — $\Lambda$, $\bar J$, $N^\top$ 에 대해
   $$
   \lVert J\bar J - \mathbb{1}_m\rVert_\infty < 10^{-14}, \qquad
   \lVert JM^{-1}N^\top\rVert_\infty < 10^{-13},
   $$
   $\Lambda = \Lambda^\top$ 이 **정확히** 성립하고 $\lambda_{\min}(\Lambda) > 0$.
   > 측정값: $8.5\times10^{-16}$, $7.2\times10^{-15}$, 대칭 오차 $0.0$, $\lambda_{\min} = 0.185$.
   이어서 기하적 유사역행렬 $J^{+}$ 로 만든 투영에 대해 같은 양을 계산해
   $\lVert JM^{-1}(\mathbb{1} - J^\top(J^{+})^\top)\rVert_\infty > 10^{-2}$ 임을 보이라 —
   **$M$-계량이 필요하다는 것을 수치로 확인하는 단계**다.
4. **적분: 제약 위반을 네 가지 방식으로 비교 (2초, $\Delta t = 10^{-3}$)** —
   ⓐ **RK4 + Baumgarte $\alpha = \beta = 20$**: $\max\lVert\phi\rVert_\infty < 10^{-8}$ 이고
   $\max\lVert J\dot q\rVert_\infty < 10^{-6}$ (측정값 $1.9\times10^{-9}$, $6.4\times10^{-8}$).
   **이것이 blueprint 가 지정한 "제약 위반 < 1e-8" 조건이고, 적분기를 명시해야 성립한다.**
   ⓑ **semi-implicit Euler + 같은 Baumgarte**: 같은 기준을 **통과하지 못해야** 한다
   ($\max\lVert\phi\rVert > 10^{-4}$; 측정값 $2.2\times10^{-3}$). 안정화가 아니라 적분기가
   병목임을 보이는 단계다.
   ⓒ **아무 적분기 + 좌표 투영**(Baumgarte 끔): $\max\lVert\phi\rVert_\infty < 10^{-12}$ 이고
   $\max\lVert J\dot q\rVert_\infty < 10^{-12}$ (측정값 둘 다 $\approx 10^{-14}$).
   ⓓ **Baumgarte 의 오차 ODE 자체**: $\phi$ 에 $10^{-3}$ 의 오차를 주입하고
   ($q \leftarrow q + J^{+}(10^{-3}, 0)^\top$) $\alpha = \beta = 20$, RK4 $\Delta t = 10^{-4}$ 로
   적분해, $t \in \{0.05, 0.1, 0.2, 0.4\}$ 에서 $\lVert\phi\rVert$ 가
   $e_0(1 + \beta t)e^{-\beta t}$ 와 **상대오차 2% 이내**로 일치해야 한다.
   > 측정값: $t = 0.05$ 에서 $7.308\times10^{-4}$ (예측 $7.336\times10^{-4}$),
   > $t = 0.1$ 에서 $4.028\times10^{-4}$ (예측 $4.048\times10^{-4}$),
   > $t = 0.2$ 에서 $9.075\times10^{-5}$ (예측 $9.131\times10^{-5}$),
   > $t = 0.4$ 에서 $2.990\times10^{-6}$ (예측 $3.010\times10^{-6}$).

**입력 데이터**: 외부 데이터 불필요. 모델 상수는 P5 에 전부 적혀 있다. $P_0$ 는
$\mathrm{tip}(0.6,-0.9,0.5)$ 로 **계산해서** 쓰는 것이 좋다(반올림 없이 $\phi(q_0) = 0$ 이 된다).

**비교 대상** (최소 1개):
- 1순위: 승수법 vs 축소좌표법(조건 1) — 완전히 독립된 두 경로.
- 2순위: 조건 2 의 정규방정식(변분 문제에서 독립적으로 유도).
- 선택 검증(없어도 통과): `pinocchio` 의 `pin.forwardDynamics`(제약 포함) 또는 Featherstone 의
  폐루프 예제와 $10^{-10}$ 이내 일치.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 1 이 $10^{-9}$ 벽을 못 넘는다 | $J$ 또는 $\dot J\dot q$ 를 유한차분으로 계산했다 | 해석식으로 바꿔 보고 오차가 $10^{-14}$ 로 떨어지는지 본다 |
| $\lambda$ 의 부호가 반대 | $M\ddot q + b = \tau \pm J^\top\lambda$ 규약 | $\ddot q$ 는 맞고 $\lambda$ 만 틀렸는지 확인한다 — 그러면 규약 문제다 |
| 조건 1 의 축소좌표 쪽만 틀리다 | $w$ ($Jw = k$ 특수해)를 빼먹고 $\ddot q = G\ddot u$ 로 썼다 | $k = 0$ 인 상태($\dot q = 0$)에서는 맞고 $\dot q \ne 0$ 에서 틀리는지 본다 |
| 축소좌표 결과가 스텝마다 튄다 | $G$ 의 **게이지** — SVD/QR 의 부호·열 순서가 불연속 | $\ddot q$ 수준에서만 비교하고, $\ddot u$ 를 적분하지 않는다 |
| 조건 3 의 $N^\top$ 검사가 실패 | $\bar J^\top$ 을 $\Lambda J M^{-1}$ 대신 $(M^{-1}J^\top\Lambda)^\top$ 로 **다시** 전치했다 | $\Lambda$, $M$ 의 대칭을 이용해 두 식이 같은지 손으로 확인한다 |
| 조건 4 ⓐ 가 $10^{-6}$ 수준 | RK4 안에서 Baumgarte 항을 **한 번만** 계산했다(스테이지마다 다시 계산해야 한다) | 각 RK 스테이지에서 $\phi$, $\dot\phi$ 를 그 스테이지의 상태로 다시 계산하는지 본다 |
| 조건 4 ⓒ 가 실패 | 투영에서 $\dot q$ 를 빼먹었다($q$ 만 되돌렸다) | $\lVert J\dot q\rVert$ 를 따로 추적한다 — $\phi$ 는 작고 $\dot\phi$ 만 크면 그것이다 |
| 조건 4 ⓓ 가 10% 이상 어긋난다 | $\dot e_0 \ne 0$ 인데 $\dot e_0 = 0$ 공식과 비교했다 | 주입 직후 $\dot\phi = J\dot q$ 를 출력해 0 인지 확인하고, 아니면 일반해를 쓴다 |
| $\beta$ 를 키우니 발산한다 | 강성 — 명시적 적분기의 안정 영역을 벗어났다 | $\beta\Delta t$ 를 출력하고 $\beta$ 를 절반으로 줄여 본다 |

## 열린 문제

- **(열린 문제) 안정화 이득의 원리적 선택** — Baumgarte 의 (9)는 55년 된 식이고 지금도
  표준이지만, $\alpha, \beta$ 를 **원리적으로** 고르는 방법은 없다. R5 의 표가 이유를 보여
  준다: 실제 제약 오차는 안정화와 적분기 오차의 합이고, 이득을 키우면 안정화 오차는 줄지만
  계가 강성이 되어 적분기 오차가 커진다. 두 항을 함께 최소화하는 이득은 적분기·스텝·기구에
  모두 의존하고, 그 의존을 담은 모형이 없다. 현재 접근: 투영·후안정화(post-stabilization)로
  이득 선택을 **회피**하는 쪽, 그리고 제약을 구조적으로 만족시키는 리 군 적분기.
  비어 있는 자리: 주어진 적분기와 스텝에 대해 이득을 선택하는 절차.
- **(열린 문제) 과잉 구속계의 제약력 분배** — R1 의 C3(i)에서 보듯 $J$ 가 계수 결손이면
  $\lambda$ 가 유일하지 않다. 실제 기계는 과잉 구속이 흔하고(평면 4절 링크의 공간 구현,
  다지 그래스프, 네 다리 보행), 그때 실제로 흐르는 제약력은 **강성**(유연성)이 결정한다 —
  즉 강체 모델이 원리적으로 답할 수 없는 양이다. 최소 노름 $\lambda$ 를 택하는 관행은
  수학적 편의이고 물리적 근거가 없다. 현재 접근: 유연성을 명시적으로 넣는 정식화,
  강성 가중 최소 노름. 비어 있는 자리: 유연성을 모르는 채로 쓸 수 있는 하한·상한.
- **(열린 문제) 특이점 근방의 조작 공간 제어** — $\Lambda = (JM^{-1}J^\top)^{-1}$ 은 $J$ 가
  계수를 잃는 **동역학적 특이점**에서 폭발하고, 감쇠 유사역행렬은 과제 오차를 남긴다.
  "과제를 얼마나 포기하고 안정성을 얼마나 사는가"에 대한 최적 교환이 일반적으로는 열려 있다 —
  특히 여유 자유도가 있어 특이점을 **피할 수 있을 때** 피하는 것과 통과하는 것의 비교가 그렇다.
  현재 접근: 감쇠 최소제곱, 특이점 회피를 널공간 과제로 넣는 계층적 제어
  ([Khatib 1987](https://doi.org/10.1109/JRA.1987.1087068) 의 분해를 쌓은 계열).
  비어 있는 자리: 특이점 통과 궤적의 전역 최적성.

## 개념 점검

`rc quiz c2-constrained-dynamics` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c2-constrained-dynamics-quiz
questions:
  - id: q1
    type: multiple
    prompt: "KKT 행렬 $K = \\begin{bmatrix} M & -J^{\\top} \\\\ J & 0\\end{bmatrix}$ 가 비특이라는 결론에 **실제로 쓰이는** 가정을 모두 고르라."
    choices:
      - "$M \\succ 0$ (양반정치만으로는 부족)"
      - "$J$ 가 행 완전계수"
      - "$m \\le n$"
      - "제약이 홀로노믹"
    answer: [0, 1]
    explanation: "영공간 논증에서 $x^{\\top}Mx = (Jx)^{\\top}y = 0$ 과 $M \\succ 0$ 으로 $x = 0$ 을 얻고(여기서만 H1 이 쓰인다), 그 다음 $J^{\\top}y = 0$ 과 행 완전계수로 $y = 0$ 을 얻는다. $m \\le n$ 은 행 완전계수의 따름결과이고, 홀로노믹성은 $\\phi$ 를 두 번 미분해 $J$ 를 얻는 **과정**에 쓰였지 비특이성 증명에는 쓰이지 않는다."
    concept: { front: "KKT 행렬이 비특이인 조건", back: "$M \\succ 0$ + $J$ 행 완전계수. 계수 결손이면 $\\ddot{q}$ 는 유일하지만 $\\lambda$ 는 아니다" }
  - id: q2
    type: single
    prompt: "Gauss 의 최소 제약 원리에 따르면 제약 가속도 $\\ddot{q}$ 는 무엇을 최소화하는가?"
    choices:
      - "$\\lVert\\ddot{q}\\rVert_2$"
      - "$\\lVert\\ddot{q} - a_u\\rVert_M$ — 제약 없는 가속도로부터의 $M$-가중 거리"
      - "운동 에너지 $\\frac{1}{2}\\dot{q}^{\\top}M\\dot{q}$"
      - "제약력의 크기 $\\lVert\\lambda\\rVert$"
    answer: 1
    explanation: "$\\ddot{q} = \\arg\\min \\frac{1}{2}(x-a_u)^{\\top}M(x-a_u)$ s.t. $Jx = k$ 이고, 그 KKT 조건이 정확히 (2)다. 즉 제약 가속도는 제약 없는 가속도의 $M$-가중 투영이다. 4절 링크 측정에서 KKT 해의 $M$-노름 5.523095 가 $\\mathrm{null}(J)$ 방향으로 옮긴 모든 가능한 점보다 엄격히 작다."
    concept: { front: "Gauss 의 최소 제약 원리", back: "$\\ddot{q}$ 는 $\\lVert x - a_u\\rVert_M$ 을 $Jx = k$ 아래 최소화한다 — KKT 조건이 (2)" }
  - id: q3
    type: single
    prompt: "동적으로 일관된 유사역행렬 $\\bar{J} = M^{-1}J^{\\top}\\Lambda$ 를 쓰는 이유는?"
    choices:
      - "$\\lVert\\dot{q}\\rVert_2$ 를 최소화하기 때문"
      - "널공간 토크 $N^{\\top}\\tau_0$ 가 과제 가속도를 만들지 않기 때문"
      - "계산이 $J^{+}$ 보다 싸기 때문"
      - "$J$ 가 특이점에 가까울 때 안정하기 때문"
    answer: 1
    explanation: "$JM^{-1}N^{\\top} = 0$ 이 성립하고, R3 의 유일성 증명에 따르면 그 성질을 갖는 우역행렬은 $\\bar{J}$ 뿐이다. 기하적 $J^{+}$ 는 $\\lVert\\dot{q}\\rVert_2$ 를 최소화하지만 널공간 토크가 과제를 흔든다. 계산은 더 비싸고($\\Lambda$ 가 필요), 특이점에서는 $\\bar{J}$ 도 폭발한다."
    concept: { front: "$\\bar{J}$ 가 \"동적으로 일관된\" 뜻", back: "$JM^{-1}N^{\\top} = 0$ — 널공간 토크가 과제 가속도를 0 으로 만든다. 그 성질을 갖는 우역행렬은 유일하다" }
  - id: q4
    type: truefalse
    prompt: "Baumgarte 안정화를 켜면 수치 적분 중 제약 위반을 원하는 만큼 작게 유지할 수 있다."
    answer: false
    explanation: "(9)가 보장하는 것은 **주입된** 오차의 지수 감쇠뿐이다. 적분 중 매 스텝 새로 생기는 절단 오차에 대한 정상 상태 오차는 적분기 차수가 결정한다. 같은 $\\alpha=\\beta=20$ 으로 4절 링크를 2초 적분하면 semi-implicit Euler($\\Delta t = 10^{-3}$)는 $2.2\\times10^{-3}$, RK4 는 $1.9\\times10^{-9}$ 다. 엄격한 제약이 필요하면 좌표 투영을 쓴다($\\approx 10^{-14}$)."
    concept: { front: "Baumgarte 가 보장하는 것과 아닌 것", back: "주입된 오차의 지수 감쇠(O). 적분 중 정상 상태 오차 크기(X) — 그것은 적분기 차수가 정한다" }
  - id: q5
    type: short
    prompt: "축소좌표법 (7)에서 라그랑주 승수가 사라지는 이유를 한 항으로 쓰면? (식 한 조각)"
    answer: ["G^T J^T = 0", "G^TJ^T=0", "G^T J^T", "J G = 0", "JG=0", "JG = 0", "G 가 J 의 영공간 기저"]
    explanation: "$JG = 0$ 이므로 $G^{\\top}J^{\\top} = 0$ 이고, (1)의 첫 식에 왼쪽에서 $G^{\\top}$ 를 곱하면 $\\lambda$ 항이 정확히 소거된다. 물리적으로는 제약력이 제약 다양체의 접공간에 수직이어서 접방향 가상 변위에 일을 하지 않는다는 것(가상 일의 원리)의 대수적 형태다."
    concept: { front: "축소좌표법에서 $\\lambda$ 가 소거되는 이유", back: "$JG = 0 \\Rightarrow G^{\\top}J^{\\top} = 0$ — 제약력은 접공간에 수직(가상 일의 원리)" }
```

## 이 단계 공부법

1. **부호 규약을 먼저 못 박는다 (15분)** — (1)을 종이에 쓰고 $\lambda$ 가 "계에 작용하는 힘"
   임을 적어 둔다. 이 레슨에서 생기는 버그의 절반이 규약이고, 외부 코드와 맞출 때 가장
   먼저 보는 곳이다.
2. **(2)를 Schur 보완으로 손으로 푼다 (40분)** — $\ddot q$ 를 소거해 $\lambda$ 를 얻고 다시
   대입하는 두 동작이다. $\Lambda = (JM^{-1}J^\top)^{-1}$ 과 $\bar J = M^{-1}J^\top\Lambda$ 가
   **계산 도중에 저절로 나타나는 것**을 직접 보라 — 그러면 R3 이 새 개념이 아니라 같은
   계산의 다른 읽기임이 분명해진다.
3. **R1 의 증명을 세 줄로 외운다 (30분)** — $x^\top Mx = (Jx)^\top y = 0$ → $x=0$ →
   $J^\top y = 0$ → $y = 0$. 그 다음 **가설을 하나씩 지워** 무엇이 깨지는지 적어라(문제 P4).
   과잉 구속에서 $\lambda$ 가 정해지지 않는다는 사실은 실험실에서 반드시 만나게 된다.
4. **Gauss 원리를 수치로 확인한다 (40분)** — 재현 과제 조건 2 ⓑ 를 먼저 해 보라.
   $\mathrm{null}(J)$ 방향으로 조금 움직인 **가능한** 가속도가 $M$-노름이 더 큰 것을 숫자로
   보면, (4)가 비유가 아니라 등식임이 남는다. 최적화기로 검증하려는 유혹을 참아라 —
   정규방정식으로 해야 $10^{-14}$ 가 나온다.
5. **$J^{+}$ 와 $\bar J$ 를 나란히 구현한다 (50분)** — 같은 과제에 두 투영을 쓰고 과제
   가속도를 비교하라. $M$ 이 비대각일 때 $J^{+}$ 쪽이 과제를 흔드는 것을 보는 것이
   "동역학에서 올바른 계량은 $M$ 이다"를 영구히 각인시킨다.
6. **재현 과제의 조건 4 를 네 번 돌린다 (90분)** — ⓐⓑⓒⓓ 는 각각 다른 것을 말한다.
   특히 ⓑ 는 **실패해야 통과**인 조건이다. 네 결과를 한 표로 만들어 R5 의 표와 비교하고,
   "제약 오차 = 안정화 오차 + 적분기 오차"를 자기 숫자로 분해해 보라.
7. **논문 3편을 (2) 중심으로 읽는다 (150분)** — Khatib → Udwadia–Kalaba → Baumgarte 순서가
   좋다(일반적 → 변분적 → 수치적). 각 논문을 읽을 때 "이 저자는 (2)의 어느 부분을 자기
   문제로 보았는가"를 한 줄로 적고, 세 줄을 모아 한 단락으로 합쳐라.
8. **무엇을 못 하는지로 끝낸다 (25분)** — 열린 문제 중 과잉 구속 쪽을 골라, 강체 모델이
   원리적으로 답할 수 없는 양이 무엇인지 한 문단으로 쓴다. 그 문단이 접촉 레슨
   (`c2-contact-dynamics`)에서 **부등식**이 필요한 이유의 절반이다.

**통과 기준**: 백지에서 (2)(3)(6)(7)(9)를 쓸 수 있고, R1 의 세 줄 증명과 R3 의 유일성 논증을
말할 수 있고, 재현 과제 네 조건을 통과하는 승수법·축소좌표법 두 구현을 갖고 있고,
논문 3편의 1페이지 노트가 있다.
