---
id: c1-twists-wrenches-adjoint
title: 트위스트·렌치와 수반 표현
summary: >-
  강체의 속도를 트위스트, 힘을 렌치로 묶어 6차원 벡터로 쓰고, 좌표 변환 하의 변환 법칙(수반 표현
  Ad 와 그 쌍대 Ad^T)을 일률 불변성에서 유도한다. Chasles–Mozzi 정리로 모든 트위스트를 나선 축과
  피치로 분해하고, Ad 가 군 표현임을 증명한다.
objectives:
  - 트위스트의 좌표 변환 법칙을 동차변환의 공액(conjugation)에서 유도할 수 있다.
  - 렌치의 변환이 왜 Ad 의 전치인지 일률 불변성으로 유도할 수 있다.
  - 임의의 트위스트를 나선 축·피치·크기로 분해하고 순수 평행이동이 왜 예외인지 설명할 수 있다.
  - Ad 가 SE(3)의 군 표현임을 증명하고 리 괄호 ad 와의 관계를 쓸 수 있다.
  - (ω, v) 와 (v, ω) 규약 차이가 실제 코드에서 만드는 버그를 진단할 수 있다.
prerequisites: [c1-so3-se3-exponential]
difficulty: 5
estimated_minutes: 420
tags: [lie-groups, se3, twist, wrench, screw-theory, research]
activities:
  - id: c1-twists-wrenches-adjoint-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 80
  - id: c1-twists-wrenches-adjoint-papers
    kind: reading
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 110
  - id: c1-twists-wrenches-adjoint-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 130
  - id: c1-twists-wrenches-adjoint-reproduction
    kind: exercise
    title: 재현 과제 — Ad·Ad^T·나선 분해 수치 검증 (R1)
    estimated_minutes: 80
  - id: c1-twists-wrenches-adjoint-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Lynch & Park, Modern Robotics"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: ch.3.3 (Rigid-Body Motions and Twists), 3.4 (Wrenches). 이 레슨의 표기 기준.
  - title: "Murray, Li & Sastry, A Mathematical Introduction to Robotic Manipulation"
    kind: book
    note: ch.2.3–2.5 (Rigid Body Velocity, Screws, Wrenches). (공식 URL 미확인)
  - title: "Featherstone, Rigid Body Dynamics Algorithms"
    url: https://royfeatherstone.org/
    kind: book
    note: ch.2 (Spatial Vector Algebra). 다른 규약((v, ω) 순서)의 같은 이론.
  - title: "Featherstone — A beginner's guide to 6-D vectors, part 1 (2010)"
    url: https://doi.org/10.1109/MRA.2010.937853
    kind: article
    note: 필독 1. 6D 벡터의 운동·힘 쌍대성을 규약부터 설명한다.
  - title: "Featherstone — A beginner's guide to 6-D vectors, part 2 (2010)"
    url: https://doi.org/10.1109/MRA.2010.939560
    kind: article
    note: 필독 2. 좌표 변환과 알고리즘에서의 사용.
  - title: "Brockett — Robotic manipulators and the product of exponentials formula (1984)"
    url: https://doi.org/10.1007/BFb0031048
    kind: article
    note: 필독 3. 트위스트를 지수 사상으로 엮는 원전. 다음 레슨(PoE)의 출발점.
---

# 트위스트·렌치와 수반 표현

## 전제와 기호

앞 레슨([`c1-so3-se3-exponential`](so3-se3-exponential.md))의 표기를 그대로 쓴다. 추가 기호:

| 기호 | 뜻 |
|---|---|
| $\mathcal{V} = (\omega, v) \in \mathbb{R}^6$ | 트위스트(twist). $\omega$ 각속도, $v$ 선속도. **이 순서를 고정한다** |
| $[\mathcal{V}] = \begin{bmatrix} \hat{\omega} & v \\ 0 & 0 \end{bmatrix}$ | $\mathfrak{se}(3)$ 의 원소 (4×4) |
| $\mathcal{F} = (m, f) \in \mathbb{R}^6$ | 렌치(wrench). $m$ 모멘트, $f$ 힘. 트위스트와 **같은 순서** |
| $[\mathrm{Ad}_T] \in \mathbb{R}^{6\times6}$ | $T \in SE(3)$ 의 수반 표현(adjoint representation) |
| $[\mathrm{ad}_{\mathcal{V}}] \in \mathbb{R}^{6\times6}$ | 리 괄호의 행렬 표현 |
| $\mathcal{S} = (\hat{s}, -\hat{s}\times q + h\hat{s})$ | 나선 축(screw axis). $\hat{s}$ 단위 방향, $q$ 축 위의 한 점, $h$ 피치 |

**규약 경고**: 이 코스는 $(\omega, v)$ 순서(Modern Robotics, MLS)를 쓴다. Featherstone 의
공간 벡터와 Pinocchio 는 $(v, \omega)$ 순서를 쓴다. 필독 논문 1·2 를 읽을 때 **순서가 뒤집혀
있다는 것을 먼저 확인**하라 — 이 불일치가 실무에서 가장 흔한 6D 버그다(§문제 세트 P5).

$\hat{a}b = a \times b = -\hat{b}a$ 와 $R\hat{\omega}R^\top = \widehat{R\omega}$ 를 계속 쓴다.
후자는 직접 확인하라(앞 레슨 P1 과 같은 요령).

## 핵심 결과

- **R1 (트위스트의 변환 법칙) [D2]** — $T_{ab} = (R, p) \in SE(3)$ 에 대해
  $\mathcal{V}_a = [\mathrm{Ad}_{T_{ab}}] \mathcal{V}_b$ 이고

$$
[\mathrm{Ad}_T] = \begin{bmatrix} R & 0 \\ \hat{p}R & R \end{bmatrix}. \tag{1}
$$

- **R2 (렌치의 쌍대 변환) [D2]** — 일률(power) $\mathcal{V}^\top \mathcal{F}$ 가 프레임과
  무관하다는 사실만으로

$$
\mathcal{F}_b = [\mathrm{Ad}_{T_{ab}}]^\top \mathcal{F}_a. \tag{2}
$$

  즉 트위스트는 $\mathrm{Ad}$ 로, 렌치는 $\mathrm{Ad}^\top$ 로 **반대 방향으로** 옮겨진다.
- **R3 (Chasles–Mozzi: 나선 분해) [D2]** — $\omega \ne 0$ 인 모든 트위스트는 나선 축
  $(\hat{s}, q)$ 와 피치 $h$, 크기 $\dot{\theta} = \lVert\omega\rVert$ 로 유일하게 분해된다:

$$
\hat{s} = \frac{\omega}{\lVert\omega\rVert}, \qquad
h = \frac{\omega^\top v}{\lVert\omega\rVert^2}, \qquad
q_\perp = \frac{\omega \times v}{\lVert\omega\rVert^2}. \tag{3}
$$

  $\omega = 0$ (순수 평행이동)은 **예외**다 — 축이 무한원으로 가고 피치가 정의되지 않는다.
- **R4 ($\mathrm{Ad}$ 는 군 표현) [D3]** — $[\mathrm{Ad}_{T_1 T_2}] = [\mathrm{Ad}_{T_1}][\mathrm{Ad}_{T_2}]$,
  $[\mathrm{Ad}_T]^{-1} = [\mathrm{Ad}_{T^{-1}}]$. 미분하면 리 괄호가 나온다:

$$
[\mathrm{ad}_{\mathcal{V}}] = \begin{bmatrix} \hat{\omega} & 0 \\ \hat{v} & \hat{\omega} \end{bmatrix},
\qquad [\mathcal{V}_1, \mathcal{V}_2] = [\mathrm{ad}_{\mathcal{V}_1}]\mathcal{V}_2. \tag{4}
$$

- **R5 (운동과 힘은 다른 공간이다) [D1]** — 트위스트는 접공간 $\mathfrak{se}(3)$, 렌치는 그
  쌍대공간 $\mathfrak{se}(3)^*$ 에 산다. 둘은 6차원이라 코드에서 같은 배열로 보이지만 **변환
  법칙이 다르다**. 같은 6×6 행렬을 둘 다에 쓰면 조용히 틀린다.

## 유도

### R1 — 트위스트의 변환 법칙

트위스트는 벡터가 아니라 **$\mathfrak{se}(3)$ 의 원소**이고, 프레임을 바꾸는 연산은
동차변환에 의한 공액(conjugation)이다:

$$
[\mathcal{V}_a] = T_{ab}\,[\mathcal{V}_b]\,T_{ab}^{-1}. \tag{5}
$$

(5)가 출발점이라는 것이 이 레슨의 핵심이다 — 왜 공액인지는 $T_a(t) = T_{ab} T_b(t)$ 를
미분하면 나온다(문제 P1). $T = (R, p)$, $T^{-1} = (R^\top, -R^\top p)$ 를 넣고 블록으로 전개한다:

$$
\begin{bmatrix} R & p \\ 0 & 1 \end{bmatrix}
\begin{bmatrix} \hat{\omega} & v \\ 0 & 0 \end{bmatrix}
\begin{bmatrix} R^\top & -R^\top p \\ 0 & 1 \end{bmatrix}
= \begin{bmatrix} R\hat{\omega} & Rv \\ 0 & 0 \end{bmatrix}
\begin{bmatrix} R^\top & -R^\top p \\ 0 & 1 \end{bmatrix}
= \begin{bmatrix} R\hat{\omega}R^\top & -R\hat{\omega}R^\top p + Rv \\ 0 & 0 \end{bmatrix}.
$$

좌상 블록에 $R\hat{\omega}R^\top = \widehat{R\omega}$ 를 쓰면 $\omega_a = R\omega_b$. 우상 블록은

$$
v_a = -\widehat{R\omega_b}\,p + Rv_b = p \times (R\omega_b) + Rv_b = \hat{p}R\omega_b + Rv_b,
$$

여기서 $-\hat{a}b = \hat{b}a$ 를 썼다. 두 식을 쌓으면 (1)이다.

**부호를 틀리기 쉬운 지점**: $-\widehat{R\omega}p$ 를 $\hat{p}R\omega$ 로 바꾸는 한 줄.
$-a \times b = b \times a$ 이므로 부호가 흡수된다. 이 줄을 건너뛰면 $\hat{p}$ 의 부호가 뒤집혀
속도 변환이 조용히 틀린다 — 각속도는 맞고 선속도만 틀리므로 회전 테스트로는 잡히지 않는다.

**가정이 깨지는 곳**: (5)는 $T_{ab}$ 가 **상수**일 때의 변환이다. 프레임이 시간에 따라 움직이면
$\dot{T}_{ab} \ne 0$ 항이 더해진다(움직이는 관측 프레임의 코리올리 항). `c2-spatial-vector-algebra`
에서 이 항이 공간 가속도의 코리올리 항으로 다시 나온다.

### R2 — 렌치의 쌍대 변환

힘이 하는 일(일률)은 좌표계를 고르는 방식과 무관하다. 이것만 쓴다:

$$
\mathcal{V}_b^\top \mathcal{F}_b = \mathcal{V}_a^\top \mathcal{F}_a
\quad \text{(모든 } \mathcal{V}_b \text{ 에 대해)}. \tag{6}
$$

R1 으로 $\mathcal{V}_a = [\mathrm{Ad}_{T_{ab}}]\mathcal{V}_b$ 를 대입하면

$$
\mathcal{V}_b^\top \mathcal{F}_b = \big([\mathrm{Ad}_{T_{ab}}]\mathcal{V}_b\big)^\top \mathcal{F}_a
= \mathcal{V}_b^\top [\mathrm{Ad}_{T_{ab}}]^\top \mathcal{F}_a .
$$

모든 $\mathcal{V}_b$ 에 대해 성립하므로 괄호 안을 지울 수 있고, (2)를 얻는다.

**읽는 법**: 트위스트는 $b \to a$ 로 $\mathrm{Ad}_{T_{ab}}$ 가 옮기는데, 렌치는 같은 행렬의
전치가 $a \to b$ 로 옮긴다. 방향이 반대다. 이것이 R5 가 말하는 쌍대성의 실체이며,
조작 공간 제어에서 $\Lambda$ 와 $J^\top$ 이 등장하는 이유와 같은 구조다
(`c2-constrained-dynamics`).

**실패 모드**: $\mathcal{F}_a = [\mathrm{Ad}_{T_{ab}}]\mathcal{F}_b$ 로 쓰면(즉 전치를 잊으면)
회전만 있는 변환($p = 0$)에서는 $[\mathrm{Ad}]$ 가 블록 대각이고 직교이므로 **오차가 드러나지
않는다**. 평행이동이 있는 변환에서만 틀린다. 그래서 테스트에 반드시 $p \ne 0$ 을 넣어야 한다.

### R3 — 나선 분해

$\omega \ne 0$ 을 가정하고 $\dot{\theta} = \lVert\omega\rVert$, $\hat{s} = \omega/\dot{\theta}$ 로
둔다. 축이 점 $q$ 를 지나고 피치가 $h$ 인 나선 운동의 트위스트는 정의상

$$
\omega = \hat{s}\dot{\theta}, \qquad v = (-\hat{s} \times q + h\hat{s})\dot{\theta}. \tag{7}
$$

$\dot{\theta} = 1$ 로 정규화하고 $(7)$ 에서 $h$ 와 $q$ 를 역으로 푼다.

- **피치**: $\hat{s}^\top v = \hat{s}^\top(-\hat{s}\times q) + h\,\hat{s}^\top\hat{s} = 0 + h$.
  두 번째 항에서 $\hat{s} \perp (\hat{s}\times q)$ 를 썼다. 정규화를 풀면 (3)의 $h$.
- **축의 위치**: $\hat{s} \times v = \hat{s}\times(-\hat{s}\times q) + h(\hat{s}\times\hat{s})
  = -\big(\hat{s}(\hat{s}^\top q) - q\big) = q - \hat{s}(\hat{s}^\top q) = q_\perp$,
  즉 $q$ 의 축에 수직인 성분이다. 축 **방향의** 성분은 복원되지 않는다 — 축 위의 어느 점을
  고르든 같은 나선이므로 당연하다. 이것이 (3)이 $q$ 가 아니라 $q_\perp$ 를 주는 이유다.

**$\omega = 0$ 인 경우**: (3)의 분모가 0 이다. 기하적으로는 축이 무한히 멀어지면서 회전이
평행이동으로 퇴화한 것이고, 대수적으로는 $\mathcal{V} = (0, v)$ 를 "피치 $\infty$" 로 다룰 수밖에
없다. 구현에서는 **분기**로 처리한다(문제 P4). 이 퇴화는 `c6-kinodynamic-planning` 의 나선
보간에서도 같은 자리에 나타난다.

## 증명 스케치

### R4 — $\mathrm{Ad}$ 가 군 표현임

**가설** H1: $T_1, T_2 \in SE(3)$. H2: $\mathrm{Ad}$ 가 (5)의 공액으로 정의된다.
**결론** C: $[\mathrm{Ad}_{T_1T_2}] = [\mathrm{Ad}_{T_1}][\mathrm{Ad}_{T_2}]$.

**전략**: 공액의 결합성. 행렬을 곱해 비교하지 않고 **정의로** 보인다 — 이것이 6×6 블록 곱을
전개하는 것보다 짧고, 왜 성립하는지도 보여 준다.

1. $\mathrm{Ad}$ 의 정의 (5)를 $[\mathrm{Ad}_T]\mathcal{V} = \big(T[\mathcal{V}]T^{-1}\big)^\vee$
   로 쓴다(여기서 $(\cdot)^\vee$ 는 $[\cdot]$ 의 역연산).
2. 임의의 $\mathcal{V}$ 에 대해
   $$
   [\mathrm{Ad}_{T_1T_2}]\mathcal{V} = \big((T_1T_2)[\mathcal{V}](T_1T_2)^{-1}\big)^\vee
   = \big(T_1\big(T_2[\mathcal{V}]T_2^{-1}\big)T_1^{-1}\big)^\vee,
   $$
   여기서 $(T_1T_2)^{-1} = T_2^{-1}T_1^{-1}$ 과 행렬곱의 결합성만 썼다.
3. 안쪽 괄호가 $[\,[\mathrm{Ad}_{T_2}]\mathcal{V}\,]$ 이므로(1단계의 정의), 바깥은
   $[\mathrm{Ad}_{T_1}]\big([\mathrm{Ad}_{T_2}]\mathcal{V}\big)$.
4. 모든 $\mathcal{V}$ 에 대해 같으므로 행렬로서 같다. C.
5. $T_2 = T_1^{-1}$ 로 두면 $[\mathrm{Ad}_T][\mathrm{Ad}_{T^{-1}}] = [\mathrm{Ad}_I] = I$ 이므로
   역행렬 공식도 따라온다.
6. $T = \exp([\mathcal{V}_1]t)$ 로 두고 $t=0$ 에서 미분하면 (4)의 $\mathrm{ad}$ 가 나온다
   (생략: 지수 사상의 미분 — `c1-lie-group-derivatives` 에서 다룬다).

**가설을 지우면**: $T$ 가 $SE(3)$ 가 아니라 일반 가역행렬이면 2단계까지는 성립하지만
$T[\mathcal{V}]T^{-1}$ 이 $\mathfrak{se}(3)$ 에 남지 않는다 — 좌상 블록이 반대칭이 아니게 되어
$(\cdot)^\vee$ 가 정의되지 않는다. 즉 **공액이 리 대수를 보존한다**는 것이 $SE(3)$ 구조에서 나온다.

## 문제 세트

★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** (5)가 왜 트위스트의 변환 법칙인지 유도하라. $T_a(t) = T_{ab}T_b(t)$ 를
미분해 $\dot{T}_a T_a^{-1}$ 를 $\dot{T}_b T_b^{-1}$ 로 나타내고, 그 결과가 (5)임을 보여라.
*해답 스케치*: $\dot{T}_a = T_{ab}\dot{T}_b$, $T_a^{-1} = T_b^{-1}T_{ab}^{-1}$ 를 곱하면
$\dot{T}_aT_a^{-1} = T_{ab}(\dot{T}_bT_b^{-1})T_{ab}^{-1}$. 좌변·우변의 괄호가 각각
$[\mathcal{V}_a]$, $[\mathcal{V}_b]$ 다(공간 트위스트의 정의).

**P2 (유도, ★★, R2·R4)** $[\mathrm{Ad}_T]^{-1} = [\mathrm{Ad}_{T^{-1}}]$ 를 (1)의 블록 형태에서
직접 계산해 확인하고, R4 의 5단계(정의에서 따라오는 논증)와 비교하라. 어느 쪽이 더 짧은가?
무엇을 더 많이 알려 주는가?
*해답 스케치*: 블록 역행렬은 $\begin{bmatrix} R^\top & 0 \\ -R^\top\hat{p} & R^\top\end{bmatrix}$
이고, $-R^\top\hat{p} = \widehat{(-R^\top p)}R^\top$ 를 쓰면 $[\mathrm{Ad}_{T^{-1}}]$ 와 같다.

**P3 (증명, ★★★, R4)** (4)의 $[\mathrm{ad}_{\mathcal{V}}]$ 가 리 괄호
$[\mathcal{V}_1,\mathcal{V}_2] = ([\mathcal{V}_1][\mathcal{V}_2] - [\mathcal{V}_2][\mathcal{V}_1])^\vee$
를 올바르게 표현함을 보이고, Jacobi 항등식이 성립함을 확인하라.
*해답 스케치*: 4×4 블록 곱을 전개하면 좌상 블록이 $\hat{\omega}_1\hat{\omega}_2 -
\hat{\omega}_2\hat{\omega}_1 = \widehat{\omega_1\times\omega_2}$ 이고 우상 블록이
$\hat{\omega}_1v_2 - \hat{\omega}_2v_1$ 이다. Jacobi 는 행렬 교환자의 성질로 환원된다.

**P4 (구현, ★★, R1·R2·R3)** `Ad(T)`, `ad(V)`, `twist_to_screw(V)`, `screw_to_twist(s, q, h, dtheta)`
를 쓰라. `twist_to_screw` 는 $\omega = 0$ 분기를 처리해야 한다.
*루브릭*: ⓐ $\lVert\omega\rVert < 10^{-12}$ 에서 예외 대신 "순수 평행이동" 표식을 반환한다
ⓑ 왕복(`screw_to_twist(*twist_to_screw(V))`)이 재현 과제 기준을 만족한다 ⓒ 렌치 변환에
$[\mathrm{Ad}]^\top$ 를 쓰고 전치를 잊지 않았다 ⓓ $(\omega, v)$ 순서가 문서화되어 있다.

**P5 (반례, ★★, R2·R5)** 전치를 잊은 렌치 변환
($\mathcal{F}_a \leftarrow [\mathrm{Ad}_{T_{ab}}]\mathcal{F}_b$)이 **통과시켜 버리는** 테스트와
**잡아내는** 테스트를 각각 구성하라. 왜 회전만 있는 테스트로는 이 버그를 잡을 수 없는가?
*성질 체크리스트*: $p = 0$ 이면 $[\mathrm{Ad}]$ 가 블록 대각 $\mathrm{diag}(R, R)$ 이고
$[\mathrm{Ad}]^\top = \mathrm{diag}(R^\top, R^\top) = [\mathrm{Ad}]^{-1}$ 이므로, "역변환으로
되돌아오는지"만 보는 왕복 테스트는 두 경우를 구분하지 못한다.

**P6 (계산, ★, R3)** $\mathcal{V} = (\omega, v)$, $\omega = (0, 0, 2)$, $v = (0, 4, 6)$ 의 나선
축·피치·크기를 구하라.
*정답*: $\dot{\theta} = 2$, $\hat{s} = (0,0,1)$, $h = \omega^\top v/\lVert\omega\rVert^2
= 12/4 = 3$, $q_\perp = (\omega\times v)/\lVert\omega\rVert^2 = (-8, 0, 0)/4 = (-2, 0, 0)$.
허용오차 $10^{-9}$. 검산: (7)에 넣어 $v$ 를 복원하라 —
$(-\hat{s}\times q_\perp + h\hat{s})\dot{\theta} = (-(0,0,1)\times(-2,0,0) + (0,0,3))\cdot 2
= ((0,2,0)+(0,0,3))\cdot2 = (0,4,6)$. ✓

## 논문 읽기

**필독 3편.** 고정 질문 10개(`research_notes/연구 트랙 설계/lesson-standard.md` §5)로 논문당
1페이지 노트를 쓴다.

1. **Featherstone, "A beginner's guide to 6-D vectors", part 1 (2010, IEEE RAM)** —
   역할: `표준(standard)`. <https://doi.org/10.1109/MRA.2010.937853>
   추가 질문: ⓐ 저자의 $(v, \omega)$ 순서를 이 레슨의 $(\omega, v)$ 로 옮기면 $[\mathrm{Ad}]$ 의
   블록이 어떻게 재배치되는가? ⓑ 저자가 "운동 벡터"와 "힘 벡터"를 **다른 타입**으로 다루라고
   주장하는 이유를 R2·R5 와 연결해 쓰라.
2. **Featherstone, part 2 (2010, IEEE RAM)** — 역할: `표준(standard)`.
   <https://doi.org/10.1109/MRA.2010.939560>
   추가 질문: 좌표 변환을 "한 번에 6×6 으로" 하는 것과 "3×3 두 번"으로 하는 것의 연산량 차이는?
3. **Brockett, "Robotic manipulators and the product of exponentials formula" (1984, LNCIS)** —
   역할: `원전(seminal)`. <https://doi.org/10.1007/BFb0031048>
   추가 질문: 이 논문이 관절을 트위스트로 보는 관점이 DH 파라미터 대비 무엇을 단순화하는가?
   (다음 레슨 `c1-poe-analytic-ik` 의 출발점이다.)

## 재현 과제

**티어 R1 (수치 검증).** 예산: 노트북 CPU 1분 이내, numpy 만. 네 조건을 모두 만족해야 통과다.
**모든 테스트에 $p \ne 0$ 인 변환을 포함하라** — $p = 0$ 만 쓰면 §유도 R2 의 실패 모드를 놓친다.

1. **$\mathrm{Ad}$ 가 공액과 일치**: 무작위 $T \in SE(3)$ 와 $\mathcal{V} \in \mathbb{R}^6$ 1000쌍에 대해
   $\big\lVert \big(T[\mathcal{V}]T^{-1}\big)^\vee - [\mathrm{Ad}_T]\mathcal{V} \big\rVert_\infty < 10^{-12}$.
2. **군 표현 성질**: 무작위 $T_1, T_2$ 1000쌍에 대해
   $\lVert [\mathrm{Ad}_{T_1T_2}] - [\mathrm{Ad}_{T_1}][\mathrm{Ad}_{T_2}] \rVert_F < 10^{-12}$ 이고
   $\lVert [\mathrm{Ad}_T]^{-1} - [\mathrm{Ad}_{T^{-1}}] \rVert_F < 10^{-12}$.
3. **일률 불변성**: 무작위 $T$, $\mathcal{V}_b$, $\mathcal{F}_a$ 에 대해
   $\big| \mathcal{V}_b^\top([\mathrm{Ad}_T]^\top\mathcal{F}_a) - ([\mathrm{Ad}_T]\mathcal{V}_b)^\top\mathcal{F}_a \big| < 10^{-12}$.
   추가로 **전치를 뺀 잘못된 구현이 이 테스트를 실패하는지** 확인하라(일부러 틀린 버전을 돌려 본다).
4. **나선 분해 왕복**: $\lVert\omega\rVert \in (10^{-6}, 10)$ 인 트위스트 $10^4$ 개에 대해
   `screw_to_twist(*twist_to_screw(V))` 가 원래 $\mathcal{V}$ 와 $10^{-10}$ 이내로 일치.
   $\omega = 0$ 인 입력 10개에 대해 예외 없이 순수 평행이동으로 처리됨.

**비교 대상**: 유한차분으로 계산한 속도. $T_a(t) = T_{ab}\exp([\mathcal{V}_b]t)$ 를 수치
미분해 얻은 $\mathcal{V}_a$ 가 $[\mathrm{Ad}_{T_{ab}}]\mathcal{V}_b$ 와 $10^{-6}$ 이내로 일치해야 한다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 각속도는 맞고 선속도만 틀리다 | $\hat{p}R$ 블록의 부호($-\widehat{R\omega}p = \hat{p}R\omega$) | $p = (1,0,0)$, $\omega = (0,0,1)$, $v = 0$ 으로 손으로 검산 |
| 회전만 있는 테스트는 통과, 평행이동이 있으면 실패 | 렌치 변환에서 전치를 잊었다 | 조건 3 을 $p \ne 0$ 으로 돌린다 |
| 6D 벡터 성분이 뒤섞인다 | 라이브러리의 $(v,\omega)$ 순서와 혼용 | 단위 트위스트 $e_1 \dots e_6$ 를 넣어 어느 블록이 움직이는지 본다 |
| $\omega \to 0$ 에서 나선 축이 폭발한다 | (3)의 $1/\lVert\omega\rVert^2$ | 분기 임계값을 로그 스케일로 쓸며 오차를 그린다 |

## 열린 문제

- **(열린 문제) 접촉·제약이 있는 계에서 6D 표기의 수치 안정성** — 제약 공간으로의 투영
  ($J\Lambda^{-1}J^\top$ 꼴)은 특이 구성 근방에서 조건수가 폭발한다. 어떤 6D 좌표·스케일링이
  조건수를 최소화하는지에 대한 일반 지침이 없다(길이 단위와 각도 단위가 섞여 있어 스케일이
  물리 단위에 의존한다). 현재 접근: `c2-constrained-dynamics` 의 조작 공간 정식화
  ([Khatib 1987](https://doi.org/10.1109/JRA.1987.1087068)), 가중 유사역행렬.
- **(열린 문제) 미분가능 시뮬레이터에서 $\mathrm{Ad}$ 미분의 전파** — 접촉이 비매끄러워
  기울기가 정의되지 않는 지점에서, 리 군 구조를 유지한 채 어떤 기울기를 쓰는 것이 타당한지
  정리되지 않았다. 현재 접근: [Pinocchio 의 해석적 미분](https://doi.org/10.15607/RSS.2018.XIV.038),
  [볼록 접촉 완화](https://doi.org/10.1109/ICRA.2014.6907751). `c2-contact-dynamics` 에서 다시 다룬다.
- **(열린 문제) 규약 불일치의 재현성 비용** — $(\omega,v)$ 와 $(v,\omega)$, 좌/우 야코비안,
  body/spatial 트위스트가 라이브러리마다 다르고, 논문은 종종 규약을 명시하지 않는다. 이로 인한
  재현 실패가 얼마나 흔한지 정량화된 조사가 없다 — `r1-reproducibility-artifacts` 의 사례로 삼을 만하다.

## 개념 점검

`rc quiz c1-twists-wrenches-adjoint` 로 푼다. 개념 점검 전용이고 실제 과제는 위 문제 세트와
재현 과제다.

```quiz
activity: c1-twists-wrenches-adjoint-quiz
questions:
  - id: q1
    type: single
    prompt: "렌치는 프레임 사이를 어떻게 옮겨지는가? (트위스트가 $[\\mathrm{Ad}_{T_{ab}}]$ 로 $b \\to a$ 옮겨질 때)"
    choices:
      - "$[\\mathrm{Ad}_{T_{ab}}]$ 로 똑같이 $b \\to a$"
      - "$[\\mathrm{Ad}_{T_{ab}}]^\\top$ 로 $a \\to b$ (반대 방향)"
      - "$[\\mathrm{Ad}_{T_{ab}}]^{-1}$ 로 $b \\to a$"
      - "변환되지 않는다 (렌치는 프레임에 무관하다)"
    answer: 1
    explanation: "일률 $\\mathcal{V}^\\top\\mathcal{F}$ 가 프레임과 무관하다는 조건에서 $\\mathcal{F}_b = [\\mathrm{Ad}_{T_{ab}}]^\\top\\mathcal{F}_a$ 가 나온다. 트위스트는 접공간, 렌치는 그 쌍대공간에 살기 때문이다."
    concept: { front: "트위스트와 렌치의 변환 법칙 차이", back: "트위스트는 $\\mathrm{Ad}$ 로, 렌치는 $\\mathrm{Ad}^\\top$ 로 반대 방향으로 옮겨진다 (쌍대공간)" }
  - id: q2
    type: truefalse
    prompt: "렌치 변환에서 전치를 잊은 버그는 회전만 있는($p = 0$) 변환으로 테스트해도 잡을 수 있다."
    answer: false
    explanation: "$p = 0$ 이면 $[\\mathrm{Ad}]$ 가 블록 대각 $\\mathrm{diag}(R, R)$ 이고 직교이므로 전치와 역행렬이 같다. 평행이동이 있는 변환에서만 차이가 드러난다 — 테스트에 반드시 $p \\neq 0$ 을 넣어야 한다."
    concept: { front: "렌치 전치 버그를 드러내는 테스트 조건", back: "$p \\neq 0$ (평행이동이 있는 변환). $p = 0$ 이면 $\\mathrm{Ad}^\\top = \\mathrm{Ad}^{-1}$ 이라 구분되지 않는다" }
  - id: q3
    type: short
    prompt: "트위스트 $\\mathcal{V} = (\\omega, v)$ 의 나선 피치 $h$ 를 $\\omega$ 와 $v$ 로 쓰면?"
    answer: ["w^T v / |w|^2", "omega^T v / |omega|^2", "wTv/|w|^2", "(w.v)/|w|^2", "\\omega^\\top v / \\lVert\\omega\\rVert^2"]
    explanation: "$\\hat{s}^\\top v = h$ 이고 $\\hat{s} = \\omega/\\lVert\\omega\\rVert$ 이므로 $h = \\omega^\\top v/\\lVert\\omega\\rVert^2$. $\\omega = 0$ 이면 정의되지 않는다(순수 평행이동)."
  - id: q4
    type: single
    prompt: "$\\mathrm{Ad}$ 가 군 표현임($[\\mathrm{Ad}_{T_1T_2}] = [\\mathrm{Ad}_{T_1}][\\mathrm{Ad}_{T_2}]$)을 가장 짧게 보이는 방법은?"
    choices:
      - "6×6 블록 곱을 전개해 양변을 비교한다"
      - "$\\mathrm{Ad}$ 를 공액으로 정의한 뒤 행렬곱의 결합성과 $(T_1T_2)^{-1} = T_2^{-1}T_1^{-1}$ 만 쓴다"
      - "지수 사상으로 양변을 전개해 비교한다"
      - "수치적으로 무작위 $T_1, T_2$ 에 대해 확인한다"
    answer: 1
    explanation: "공액 정의에서 $(T_1T_2)[\\mathcal{V}](T_1T_2)^{-1} = T_1(T_2[\\mathcal{V}]T_2^{-1})T_1^{-1}$ 이 바로 나온다. 블록 전개보다 짧고, 왜 성립하는지(공액이 리 대수를 보존한다는 것)도 보여 준다."
```

## 이 단계 공부법

1. **표기 순서를 먼저 못 박는다 (20분)** — $(\omega, v)$ 로 쓸 것을 정하고, 참고 자료마다 순서를
   확인해 메모한다. Featherstone 은 뒤집혀 있다. 이 20분을 아끼면 나중에 하루를 잃는다.
2. **R1 을 블록으로 직접 전개한다 (60분)** — 본문의 세 줄짜리 전개를 종이에서 재현한다.
   $-\widehat{R\omega}p = \hat{p}R\omega$ 한 줄에서 막히면 $-a\times b = b\times a$ 만 확인하면 된다.
3. **R2 는 "일률 불변"만 기억한다 (30분)** — 전치가 어디서 오는지 외우지 말고, (6)에서 다시
   끌어낼 수 있게 한다. 시험에서 부호와 전치를 헷갈리는 사람은 이 유도를 못 하는 사람이다.
4. **나선 분해는 손으로 한 번 (40분)** — P6 을 먼저 풀고 (7)로 검산한다. $q_\perp$ 만 복원되는
   이유를 그림으로 그려 본다(축 위의 점은 아무 데나 고를 수 있다).
5. **버그를 일부러 만들어 본다 (60분)** — 재현 과제 조건 3 에서 전치를 뺀 버전을 돌려
   **테스트가 실제로 실패하는지** 확인한다. 통과해 버리면 테스트가 약한 것이다(P5).
6. **논문은 규약 대조로 읽는다 (110분)** — Featherstone part 1 을 읽으며 그의 $(v,\omega)$ 를
   이 레슨 표기로 옮겨 적고, part 2 에서 연산량 논의를 본다. Brockett 1984 는 다음 레슨의
   전제이므로 "관절을 트위스트로 본다"는 관점만 확실히 가져간다.

**통과 기준**: (1)과 (2)를 백지에서 유도할 수 있고, 전치를 잊은 렌치 버그가 왜 회전 테스트를
통과하는지 설명할 수 있고, 재현 과제 네 조건을 만족하는 코드가 있고, 논문 3편의 노트가 있다.
