---
id: c5-manifold-estimation
title: 매니폴드 위 추정과 불변 필터
summary: >-
  상태가 리 군 위에 있을 때의 추정을 바로 세운다. 재추적(retraction)으로 접공간에 들어 올린
  Gauss-Newton 이 재추적 선택과 1차에서 무관함을 증명하고, 좌/우 불확실성 표현이 Ad 로 변환됨을
  유도한다. 군 아핀(group-affine) 계에서 불변 오차의 동역학이 상태에 의존하지 않음을 빠진 줄 없이
  유도하고, SE(3) 추정에서 표준 EKF 와 불변 EKF 의 일관성(NEES)을 1000회 몬테카를로로 비교한다.
objectives:
  - 리 군 위 최소제곱을 접공간으로 들어 올리고 on-manifold Gauss-Newton 의 한 스텝을 쓸 수 있다.
  - 재추적의 정의로부터 1차 모델과 임계점이 재추적 선택과 무관함을 증명할 수 있다.
  - 좌/우 불확실성 표현이 Ad 로 변환됨을 유도하고 수치로 증폭 효과를 계산할 수 있다.
  - 군 아핀 조건에서 불변 오차의 자율 동역학 g_u(eta) = f_u(eta) - eta f_u(I) 를 유도할 수 있다.
  - 로그-선형 성질이 왜 큰 오차에서도 성립하는지와 그 한계(갱신 단계)를 설명할 수 있다.
  - NEES 로 필터의 일관성을 판정하고 표준 EKF 가 큰 오차에서 과신하는 것을 수치로 보일 수 있다.
prerequisites: [c5-factor-graphs-map, c1-so3-se3-exponential]
difficulty: 5
estimated_minutes: 660
tags: [state-estimation, lie-groups, invariant-ekf, retraction, consistency, nees, research]
activities:
  - id: c5-manifold-estimation-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 105
  - id: c5-manifold-estimation-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c5-manifold-estimation-problems
    kind: exercise
    title: 문제 세트 (증명 2 · 유도 1 · 계산 2 · 구현 1 · 반례 1)
    estimated_minutes: 195
  - id: c5-manifold-estimation-reproduction
    kind: reproduction
    title: 재현 과제 — SE(3) 에서 EKF 와 불변 EKF 의 NEES 비교 (R2)
    estimated_minutes: 195
  - id: c5-manifold-estimation-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.7 (3차원 기하), ch.8 (행렬 리 군). 좌/우 불확실성 표현의 1순위 교재. 전문 PDF 무료.
  - title: "MIT 16.485 Visual Navigation for Autonomous Vehicles (OCW)"
    url: https://ocw.mit.edu/courses/16-485-visual-navigation-for-autonomous-vehicles-vnav-fall-2020/
    kind: course
    note: 권장. L18-19 가 매니폴드 위 최적화를 다룬다.
papers:
  - id: barrau2017-invariant-ekf
    required: true
    role: seminal
    note: "§II-III"
  - id: sola2018-micro-lie-theory
    required: true
    role: standard
    note: "§4-7"
  - id: absil2008-manifold-opt
    required: true
    role: standard
    note: "§4.1, ch.7"
  - id: hartley2020-contact-inekf
    role: standard
---

# 매니폴드 위 추정과 불변 필터

## 전제와 기호

`c5-factor-graphs-map` 과 `c5-sparsity-isam` 의 표기를 그대로 쓰고, `c1-so3-se3-exponential` 의
$\exp$·$\log$ 와 $SE(3)$ 규약을 가져온다. 지금까지 두 레슨은 변수를 $\mathbb{R}^d$ 좌표로 두었다.
**이 레슨은 그것을 바로잡는다.**

| 기호 | 뜻 |
|---|---|
| $G$, $\mathfrak{g}$ | 행렬 리 군과 그 리 대수. 이 레슨의 주 예는 $G = SE(3)$, $\dim\mathfrak{g} = 6$ |
| $\xi = (\phi, \rho) \in \mathbb{R}^6$ | $SE(3)$ 의 지수 좌표. $\xi^\wedge = \begin{bmatrix}\hat\phi & \rho\\ 0 & 0\end{bmatrix}$, 회전이 **앞** |
| $X = (R, p) \in SE(3)$ | $\begin{bmatrix}R & p\\ 0 & 1\end{bmatrix}$ |
| $\mathrm{Ad}_X$ | 수반 표현. $X\exp(\xi^\wedge)X^{-1} = \exp\big((\mathrm{Ad}_X\xi)^\wedge\big)$, $\mathrm{Ad}_X = \begin{bmatrix}R & 0\\ \hat p R & R\end{bmatrix}$ |
| $J_l(\phi)$, $J_r(\phi)$ | $SO(3)$ 의 좌·우 야코비안. $J_r(\phi) = J_l(-\phi)$, $J_l(\phi) = \exp(\hat\phi)J_r(\phi)$ |
| $X \oplus \tau$, $Y \ominus X$ | $X\exp(\tau^\wedge)$, $\log(X^{-1}Y)$ — **우(right)** 규약(Solà et al.) |
| $\mathcal{R}_X : T_XG \to G$ | **재추적(retraction)**. $\mathcal{R}_X(0) = X$, $D\mathcal{R}_X(0) = \mathrm{id}_{T_XG}$ |
| $\eta_L = X^{-1}\hat X$ | **좌불변 오차**(동체 프레임). $\eta_L = \exp(\xi_L^\wedge)$ |
| $\eta_R = \hat X X^{-1}$ | **우불변 오차**(세계 프레임). $\eta_R = \exp(\xi_R^\wedge)$ |
| $\mathrm{NEES}$ | $\xi^\top \Sigma^{-1}\xi$. 일관된 필터는 $\mathbb{E}[\mathrm{NEES}] = \dim\mathfrak{g}$ |

**규약 경고.** "오차"와 "공분산"은 ① 좌·우 중 어느 쪽인지 ② 참값 기준인지 추정 기준인지를
밝히지 않으면 의미가 없다. 이 레슨은 $\eta_L = X^{-1}\hat X$ 와 $\eta_R = \hat X X^{-1}$
두 가지만 쓰고, 공분산은 항상 그 $\xi$ 에 대한 것이다. 논문을 읽을 때 가장 먼저 확인할 것이
이 규약이며, R2 가 두 규약 사이의 변환이 **항등이 아님**을 보여 준다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (매니폴드 위 Gauss-Newton 과 재추적 불변성) [D3]** — $\min_{X\in G} F(X)$,
  $F(X) = \tfrac12\sum_k\lVert r_k(X)\rVert^2_{\Sigma_k}$ 를 현재 추정 $\hat X$ 에서 접공간으로
  들어 올린 $\tilde F(\tau) = F(\mathcal{R}_{\hat X}(\tau))$ 에 Euclid Gauss-Newton 을 적용하면
  $$
  \Big(\textstyle\sum_k J_k^\top\Sigma_k^{-1}J_k\Big)\,\tau^\ast = -\sum_k J_k^\top\Sigma_k^{-1}r_k(\hat X),
    \qquad J_k = \frac{\partial\, r_k(\mathcal{R}_{\hat X}(\tau))}{\partial \tau}\bigg|_{\tau=0}, \tag{1}
  $$
  이고 $\hat X \leftarrow \mathcal{R}_{\hat X}(\tau^\ast)$ 로 갱신한다. **$J_k$ 와 임계점은
  재추적 선택과 무관하다** — $\exp$ 든 Cayley 든 사원수 정규화든 1차는 같다. 2차 항은 달라지므로
  Newton 법과 수렴 상수는 영향을 받는다.
- **R2 (좌/우 불확실성 표현과 Ad 변환) [D2]** — 같은 오차를 두 규약으로 쓰면
  $$
  \xi_R = \mathrm{Ad}_{\hat X}\,\xi_L \quad\Longrightarrow\quad
    \Sigma_R = \mathrm{Ad}_{\hat X}\,\Sigma_L\,\mathrm{Ad}_{\hat X}^\top. \tag{2}
  $$
  $SE(3)$ 에서 $\mathrm{Ad}$ 의 $\hat p R$ 블록이 **회전 불확실성을 평행이동으로 증폭**한다:
  $\lVert p\rVert = 10\,\mathrm{m}$, $\sigma_\phi = \sigma_\rho = 0.01$ 이면 세계 프레임의 위치
  표준편차가 $(0.01,\ 0.10049876,\ 0.10049876)$ 로 10배가 된다. 규약을 밝히지 않은 공분산은
  10배 틀릴 수 있다.
- **R3 (군 아핀 계와 불변 오차의 자율 동역학) [D3]** — $\dot X = f_u(X)$ 가 **군 아핀**
  $$
  f_u(XY) = X f_u(Y) + f_u(X)\,Y - X f_u(I)\,Y \qquad \forall X, Y \in G \tag{3}
  $$
  이면 우불변 오차 $\eta_R = \hat X X^{-1}$ 는 $X$ 에 **의존하지 않는** 미분방정식
  $$
  \dot\eta_R = g_u(\eta_R), \qquad g_u(\eta) = f_u(\eta) - \eta\, f_u(I) \tag{4}
  $$
  를 만족한다. 예: 동체 프레임 오도메트리 $f_u(X) = X\hat u$ 는 군 아핀이고 $g_u \equiv 0$ —
  **우불변 오차가 정확히 상수**다.
- **R3' (로그-선형 성질) [D3]** — (4)에 더해, $\xi$ 가 선형 ODE $\dot\xi = A_u \xi$
  ($A_u$ 는 $g_u$ 의 항등원에서의 1차 전개)를 만족하면 $\exp(\xi(t)^\wedge)$ 가 (4)의 **정확한**
  해다. 즉 선형화가 작은 오차 가정 없이 성립한다 — **임의로 큰 오차에서도** 공분산 전파가
  정확하다. 이것이 불변 EKF 의 전부다.
- **R4 (표준 EKF 의 과신과 불변 EKF 의 일관성) [D2]** — $SE(3)$ 이산 모형
  $X_{k+1} = X_k\Delta_k\exp(\nu_k^\wedge)$ 에서 두 필터의 전파 야코비안은
  $$
  F_{\mathrm{InEKF}} = \mathrm{Ad}_{\Delta_k^{-1}} \;\;(\text{추정값과 무관}), \qquad
  F_{\mathrm{EKF}} = \begin{bmatrix} I & 0 \\ -\widehat{\hat R p_\Delta} & I\end{bmatrix}
    \;\;(\hat R \text{ 에 의존}) \tag{5}
  $$
  다. 재현 과제의 실측(전파만, 2000회 몬테카를로): 초기 오차 $\sigma_0 = 0.5$ rad/m 에서
  EKF 의 $\mathrm{NEES}/\dim$ 이 1.95 까지 오르는 동안 불변 EKF 는 1.00-1.05 로 **평평하다**.
  갱신까지 포함한 전체 필터(1000회)에서는 ANEES$/\dim$ 이 EKF 6.858 대 불변 EKF 3.234 다.
- **R5 (공분산은 규약에 상대적이다) [D1]** — `c5-factor-graphs-map` R5 의 재매개화
  비불변성이 매니폴드에서는 **재추적·좌우 규약 선택**으로 나타난다. $\Sigma$ 를 비교하려면
  규약을 함께 적어야 하고, 논문의 수치를 그대로 옮기면 (2)만큼 틀린다.

## 유도

### R2 — 좌/우 불확실성은 Ad 로 변환된다

같은 참값 $X$ 와 추정 $\hat X$ 를 두 방식으로 쓴다:

$$
X = \hat X \exp(-\xi_L^\wedge) \;\; (\text{좌불변}, \; \eta_L = X^{-1}\hat X = \exp(\xi_L^\wedge)),
\qquad
X = \exp(-\xi_R^\wedge)\hat X \;\; (\text{우불변}, \; \eta_R = \hat X X^{-1}). \tag{6}
$$

두 식을 같게 두면 $\exp(-\xi_R^\wedge)\hat X = \hat X\exp(-\xi_L^\wedge)$, 즉

$$
\exp(-\xi_R^\wedge) = \hat X \exp(-\xi_L^\wedge)\hat X^{-1}
  = \exp\!\big(-(\mathrm{Ad}_{\hat X}\xi_L)^\wedge\big), \tag{7}
$$

여기서 두 번째 등식은 $\mathrm{Ad}$ 의 정의($X\exp(\xi^\wedge)X^{-1} =
\exp((\mathrm{Ad}_X\xi)^\wedge)$)다. $\exp$ 가 항등원 근방에서 단사이므로
$\xi_R = \mathrm{Ad}_{\hat X}\xi_L$ 이고, 선형 변환의 공분산 법칙에서 바로 (2)가 나온다.

**수치로 보면.** $\hat X = (R_z(\pi/2),\ (10,0,0)^\top)$, $\Sigma_L = 10^{-4} I_6$ 이라 하자.
$\mathrm{Ad}_{\hat X} = \begin{bmatrix}R & 0\\ \hat pR & R\end{bmatrix}$ 이므로 (2)의 평행이동
블록은

$$
(\Sigma_R)_{\rho\rho} = \hat p R\,(\sigma_\phi^2 I)\,R^\top \hat p^\top + R(\sigma_\rho^2 I)R^\top
  = -\sigma_\phi^2\,\hat p^2 + \sigma_\rho^2 I, \tag{8}
$$

($\hat p^\top = -\hat p$ 를 썼다.) $p = (10,0,0)^\top$ 에서 $-\hat p^2 =
\mathrm{diag}(0, 100, 100)$ 이므로 표준편차는
$(\sigma_\rho,\ \sqrt{100\sigma_\phi^2 + \sigma_\rho^2},\ \cdot) =
(0.01,\ 0.10049876,\ 0.10049876)$ 다. 레버 암 $\lVert p\rVert$ 가 회전 불확실성을 선형으로
증폭한다 — 자이로 오차가 먼 지점의 위치 오차가 되는 것과 같은 현상이다.

**가정이 깨지는 곳**: (7)은 $\exp$ 의 국소 단사성을 쓴다. $\lVert\phi\rVert \ge \pi$ 로 커지면
$\xi_L$ 자체가 유일하지 않으므로($SO(3)$ 의 로그 특이점, `c1-so3-se3-exponential` R3) (2)의
"공분산"이 의미를 잃는다. 또 (2)는 $\hat X$ 에서 평가된 $\mathrm{Ad}$ 를 쓰므로, $\hat X$ 가
갱신되면 **같은 불확실성의 좌표 표현이 매 스텝 바뀐다** — 공분산을 로그에 찍어 비교할 때
단위가 바뀌는 흔한 버그의 원인이다.

### R3 — 군 아핀 계에서 불변 오차는 상태를 잊는다

(4)를 유도한다. $\eta := \hat X X^{-1}$ 로 두고 미분한다. $\hat X$ 와 $X$ 는 같은 동역학
$\dot{\hat X} = f_u(\hat X)$, $\dot X = f_u(X)$ 를 따른다(추정은 같은 모형으로 전파한다).
역행렬의 미분 $\frac{d}{dt}X^{-1} = -X^{-1}\dot X X^{-1}$ 을 쓰면

$$
\dot\eta = \dot{\hat X}X^{-1} + \hat X\,\frac{d}{dt}\big(X^{-1}\big)
  = f_u(\hat X)X^{-1} - \hat X X^{-1} f_u(X) X^{-1}
  = f_u(\hat X)X^{-1} - \eta\, f_u(X)X^{-1}. \tag{9}
$$

이제 $\hat X = \eta X$ 를 첫 항에 넣고 (3)을 $(X, Y) \to (\eta, X)$ 로 적용한다:

$$
f_u(\eta X) = \eta f_u(X) + f_u(\eta)X - \eta f_u(I) X
  \quad\Longrightarrow\quad
  f_u(\hat X)X^{-1} = \eta f_u(X)X^{-1} + f_u(\eta) - \eta f_u(I). \tag{10}
$$

(10)을 (9)에 대입하면 $\eta f_u(X)X^{-1}$ 이 **정확히 소거된다**:

$$
\dot\eta = \eta f_u(X)X^{-1} + f_u(\eta) - \eta f_u(I) - \eta f_u(X)X^{-1}
  = f_u(\eta) - \eta f_u(I). \tag{11}
$$

$X$ 가 사라졌다. (11)의 우변은 $\eta$ 와 (알고 있는) 입력 $u$ 만의 함수다 — 이것이 (4)다.
근사가 **한 줄도 없다**는 점이 중요하다. 선형화도, 작은 오차 가정도 쓰지 않았다.

**예 1 (동체 오도메트리).** $f_u(X) = X\hat u$, $\hat u \in \mathfrak{g}$ 상수. (3) 확인:
$f_u(XY) = XY\hat u$ 이고 우변 $= XY\hat u + X\hat uY - X\hat u Y = XY\hat u$ ✓. 그리고
$f_u(I) = \hat u$ 이므로 (4)에서 $g_u(\eta) = \eta\hat u - \eta\hat u = 0$ —
**우불변 오차가 상수다.** 기하적으로 당연하다: $\hat X$ 와 $X$ 가 같은 양을 오른쪽에서 곱하면
$\hat X X^{-1}$ 는 변하지 않는다.

**예 2 (좌불변 오차).** 같은 동역학에서 $\eta_L = X^{-1}\hat X$ 는
$\dot\eta_L = -X^{-1}\dot X X^{-1}\hat X + X^{-1}\dot{\hat X} = -\hat u\,\eta_L + \eta_L\hat u
= [\eta_L, \hat u]$ 로, 역시 $X$ 와 무관하다. 1차 전개는 $\dot\xi_L = -\mathrm{ad}_{\hat u}\xi_L$,
이산형은 $\xi_{L,k+1} = \mathrm{Ad}_{\Delta_k^{-1}}\xi_{L,k} - \nu_k$ 이고 이것이 (5)의
$F_{\mathrm{InEKF}}$ 다.

**어떤 오차를 골라야 하는가.** 전파만 보면 둘 다 자율이지만 **측정**이 결정한다. 측정이
$y = X^{-1}d + n$(동체 프레임에서 본 알려진 점 $d$) 꼴이면 $X^{-1} = \eta_L\hat X^{-1}$ 를 넣어
$y = \eta_L\,\hat y + n$ ($\hat y := \hat X^{-1}d$) 이므로 혁신(innovation)이 $\eta_L$ 만의
함수가 된다 — 좌불변 오차를 쓴다. 측정이 $y = Xd + n$(세계 프레임) 꼴이면 같은 논리로
$\hat X y$ 를 혁신으로 써서 우불변 오차를 쓴다. **불변성을 측정과 맞추지 않으면 그 자리에서
상태 의존성이 되살아나고, 불변 EKF 의 이점이 사라진다.**

### R4 — 두 필터의 야코비안과 일관성 판정

이산 모형을 고정한다. $\Delta_k = \exp((u_k\Delta t)^\wedge) = (R_\Delta, p_\Delta)$,

$$
X_{k+1} = X_k\,\Delta_k\,\exp(\nu_k^\wedge), \qquad \nu_k\sim\mathcal{N}(0, Q),
\qquad \hat X_{k+1} = \hat X_k \Delta_k. \tag{12}
$$

**불변 EKF (좌불변 오차).** $\eta_{L,k+1} = X_{k+1}^{-1}\hat X_{k+1}
= \exp(-\nu_k^\wedge)\Delta_k^{-1}\,\eta_{L,k}\,\Delta_k
= \exp(-\nu_k^\wedge)\exp\big((\mathrm{Ad}_{\Delta_k^{-1}}\xi_{L,k})^\wedge\big)$.
$\nu$ 에 대해서만 1차를 취하면

$$
\xi_{L,k+1} = \mathrm{Ad}_{\Delta_k^{-1}}\,\xi_{L,k} - \nu_k + O(\lVert\nu_k\rVert^2),
\qquad P_{k+1} = \mathrm{Ad}_{\Delta_k^{-1}} P_k \mathrm{Ad}_{\Delta_k^{-1}}^\top + Q. \tag{13}
$$

$\xi_{L,k}$ 에 대한 항은 **근사가 아니다**($\mathrm{Ad}$ 가 정확한 켤레 변환이다). 그래서
$F$ 가 추정값에 의존하지 않고, 오차가 커도 공분산 전파가 틀리지 않는다.

**표준 EKF.** 오차를 $e = (\phi, e_p)$, $\hat R = \exp(\phi^\wedge)R$, $e_p = \hat p - p$ 로
둔다(세계 프레임 회전 오차 + 세계 프레임 위치 오차 — VIO 구현에서 가장 흔한 선택). (12)에서
$R_{k+1} = R_kR_\Delta\exp(\hat\nu_\phi)$, $p_{k+1} = p_k + R_kp_\Delta + R_kR_\Delta\nu_\rho$ 이고

$$
\exp(\phi_{k+1}^\wedge) = \hat R_{k+1}R_{k+1}^\top
  = \exp(\phi_k^\wedge)\,R_kR_\Delta\exp(-\hat\nu_\phi)R_\Delta^\top R_k^\top
  = \exp(\phi_k^\wedge)\exp\!\big(-(R_kR_\Delta\nu_\phi)^\wedge\big)
$$

$$
\Longrightarrow \quad \phi_{k+1} \approx \phi_k - \hat R_kR_\Delta\,\nu_\phi, \tag{14}
$$

$$
e_{p,k+1} = e_{p,k} + (\hat R_k - R_k)p_\Delta - R_kR_\Delta\nu_\rho
  \approx e_{p,k} - \widehat{(\hat R_kp_\Delta)}\,\phi_k - \hat R_kR_\Delta\nu_\rho. \tag{15}
$$

(15)에서 $\hat R_k - R_k = (\exp(\phi^\wedge) - I)R_k \approx \hat\phi R_k$ 와
$\hat\phi\,a = -\hat a\,\phi$ 를 썼다 — **여기가 1차 근사가 들어가는 유일한 지점이고, 동시에
$\hat R_k$ 가 야코비안에 들어오는 지점이다.** (14)(15)가 (5)의 $F_{\mathrm{EKF}}$ 와
$G_{\mathrm{EKF}} = -\mathrm{diag}(\hat R_kR_\Delta,\ \hat R_kR_\Delta)$ 를 준다.

**측정 야코비안.** $y = R^\top(p_\ell - p) + n$ 에 대해
- 표준 EKF: $y = \hat R^\top\exp(\phi^\wedge)(p_\ell - \hat p + e_p)$ 를 전개하면
  $H_{\mathrm{EKF}} = \big[-\hat R^\top\widehat{(p_\ell - \hat p)},\;\; \hat R^\top\big]$.
- 불변 EKF: $y = \eta_L\hat y + n$, $\hat y = \hat X^{-1}\tilde p_\ell$ 에서
  $y \approx \hat y - \widehat{\hat y}\,\phi_L + \rho_L$, 즉
  $H_{\mathrm{InEKF}} = \big[-\widehat{\hat y},\;\; I\big]$. 여기서 $\hat y$ 를 **측정값 $y$ 로
  바꾸면** $H$ 가 추정값에 전혀 의존하지 않는다 — 이것이 "불변" 갱신이고, 재현 과제가 쓰는 형태다.

**일관성(consistency) 판정.** 오차 $\xi$ 와 공분산 $\Sigma$ 에 대해
$\mathrm{NEES} = \xi^\top\Sigma^{-1}\xi$ 를 정의하면, 오차가 정확히 $\mathcal{N}(0,\Sigma)$ 일 때
$\mathbb{E}[\mathrm{NEES}] = \dim\mathfrak{g}$ 다($\chi^2_{\dim}$ 분포). 몬테카를로 평균
$\mathrm{ANEES}/\dim$ 이 1 보다 **크면 과신(overconfident)**, 작으면 보수적이다. 각 필터의 NEES 는
**그 필터 자신의 오차 정의**로 재야 한다 — 불변 EKF 는 $\xi_L = \log(X^{-1}\hat X)$, 표준 EKF 는
$e = (\log(\hat RR^\top),\ \hat p - p)$.

**가정이 깨지는 곳**: (13)의 정확성은 **전파에만** 해당한다. 측정 야코비안은 여전히 1차 전개이고,
$\hat y$ 대신 $y$ 를 쓰는 것도 잡음 $n$ 만큼의 오차를 $H$ 에 들여온다. 그래서 큰 초기 오차에서
불변 EKF 의 NEES 도 1 이 아니다 — 재현 과제의 실측에서 첫 관측 시각의 $\mathrm{NEES}/\dim$ 이
EKF 96.9, 불변 EKF 33.3 이다. **불변 EKF 는 비일관성을 없애지 않고 줄인다.** 또 오차가 작아지면
두 필터가 수치적으로 같아진다(실측에서 마지막 시각 1.005 대 1.020). 불변 필터의 이점이
"큰 오차 영역"에 한정된다는 점은 논문을 읽을 때 반드시 확인할 사항이다.

### R5 — 매니폴드에서 공분산을 비교할 때

`c5-factor-graphs-map` R5 는 MAP 이 재매개화에 불변이 아니라고 했다. 리 군에서 그 "매개화"는
두 겹이다 — ① 재추적 $\mathcal{R}$ 의 선택(R1 에 따라 1차는 같지만 유한 스텝의 결과는 다르다)
② 좌·우 규약(R2 에 따라 $\mathrm{Ad}$ 만큼 다르다). 따라서 "$\sigma_\theta = 0.5^\circ$" 같은
보고는 규약 없이는 비교 불가능하다. 보고할 때는 ⓐ 군 ⓑ 오차 정의 ⓒ 좌·우 ⓓ 성분 순서
($(\phi,\rho)$ 인지 $(\rho,\phi)$ 인지)를 적는다. **[D1]**

## 증명 스케치

### R1 — 재추적 선택은 1차에서 답을 바꾸지 않는다

**가설** H1: $G$ 는 매끄러운 매니폴드, $F : G \to \mathbb{R}$ 는 $C^2$.
H2: $\mathcal{R}_X : T_XG \to G$ 는 재추적 — $\mathcal{R}_X(0) = X$ 이고
$D\mathcal{R}_X(0) = \mathrm{id}_{T_XG}$.
H3: $\tilde F_{\hat X}(\tau) := F(\mathcal{R}_{\hat X}(\tau))$.
**결론** C1: $\nabla\tilde F_{\hat X}(0) = \nabla F(\hat X)$ (Riemann 기울기) — 따라서
(1)의 우변과 임계점 집합이 $\mathcal{R}$ 에 의존하지 않는다. C2: $\hat X$ 가 임계점이면
$\nabla^2\tilde F_{\hat X}(0)$ 도 $\mathcal{R}$ 에 의존하지 않는다.

**전략**: 연쇄법칙 한 번, 그리고 2차에서는 "기울기 $\times$ 재추적의 2차 미분" 항이 임계점에서
사라진다는 관찰.

1. **1차.** 연쇄법칙으로 $D\tilde F_{\hat X}(0)[\tau] = DF(\hat X)[D\mathcal{R}_{\hat X}(0)\tau]
   = DF(\hat X)[\tau]$ (H2). 따라서 C1. 잔차 야코비안도 같은 이유로
   $J_k = Dr_k(\hat X)\circ D\mathcal{R}_{\hat X}(0) = Dr_k(\hat X)$ 이므로 (1)의 좌변도 같다.
2. **임계점.** C1 에서 $\nabla\tilde F_{\hat X}(0) = 0 \iff \nabla F(\hat X) = 0$. 들어 올린
   문제의 임계점과 원 문제의 임계점이 **집합으로 일치**한다.
3. **2차.** $\tau$ 로 두 번 미분하면
   $$
   D^2\tilde F_{\hat X}(0)[\tau,\tau] = D^2F(\hat X)[\tau,\tau]
     + DF(\hat X)\big[D^2\mathcal{R}_{\hat X}(0)[\tau,\tau]\big].
   $$
   두 번째 항이 $\mathcal{R}$ 에 의존하는 유일한 항이고, **$\hat X$ 가 임계점이면
   $DF(\hat X) = 0$ 이라 사라진다**. 따라서 C2.
4. **수렴.** 2·3 에서 임계점 근방의 Hessian 이 같으므로, Riemann Newton 법의 국소 2차 수렴과
   Gauss-Newton 의 국소 선형 수렴률(잔차 크기로 결정되는 상수)이 재추적 선택과 무관하다
   (`absil2008-manifold-opt` ch.4·7 의 Theorem 4.5.6·7.4.11 류).

**가설을 지우면**: H2 의 $D\mathcal{R}_X(0) = \mathrm{id}$ 를 빼면 1단계가 무너지고 야코비안이
$D\mathcal{R}_X(0)$ 만큼 틀린다. 실제로 일어나는 사고가 **사원수를 정규화 없이 4-벡터로 더하는
갱신**과 **회전 벡터를 그냥 덧셈하는 갱신**이다. 전자는 $\mathcal{R}$ 이 매니폴드로 보내지 않고,
후자는 $D\mathcal{R}(0) \ne \mathrm{id}$ 가 아니라 아예 $\theta$ 가 커질 때 군 연산과 어긋난다
(`c1-so3-se3-exponential` R4). 두 경우 모두 "수렴은 하는데 공분산이 틀린" 상태가 된다.

(생략: 재추적의 존재와 $\exp$ 가 재추적임의 증명, 그리고 멀리서의 전역 수렴.
`absil2008-manifold-opt` §4.1 과 ch.7.)

### R3' — 로그-선형 성질이 큰 오차에서도 성립한다

**가설** H1: $f_u$ 가 (3)의 군 아핀 조건을 만족한다. H2: $\eta(t)$ 는 (4)의 해,
$\eta(0) = \exp(\xi_0^\wedge)$ (**$\xi_0$ 의 크기에 제한 없음**). H3: $A_u$ 는 $g_u$ 의 항등원
근방 1차 전개로 정의된 상수 행렬 — $g_u(\exp(\xi^\wedge)) = (A_u\xi)^\wedge + O(\lVert\xi\rVert^2)$.
**결론** C: $\dot\xi = A_u\xi$, $\xi(0) = \xi_0$ 의 해 $\xi(t)$ 에 대해
$\eta(t) = \exp(\xi(t)^\wedge)$ 가 (4)의 해다.

**전략**: 유일성. 두 곡선이 같은 ODE 와 같은 초기조건을 만족함을 보인다.

1. **$g_u$ 의 구조.** (3)을 $Y = I$ 로 두면 $f_u(X) = Xf_u(I) + f_u(X) - Xf_u(I)$ 라는 자명식이
   나오지만, $X = \exp(s\xi^\wedge)$ 를 넣고 $s$ 로 미분하면 $g_u$ 가 리 대수 위에서
   **선형 사상의 지수**로만 작용함을 얻는다(원 논문의 핵심 보조정리).
2. **후보 곡선.** $\zeta(t) := \exp(\xi(t)^\wedge)$ 로 두고 미분하면
   $\dot\zeta = \big(\text{d}\exp_{\xi}[\dot\xi]\big)$ 이고, 1단계의 구조를 쓰면
   이것이 정확히 $g_u(\zeta)$ 와 같음을 확인할 수 있다.
3. **유일성.** $g_u$ 가 (국소) Lipschitz 이므로 Picard-Lindelöf 로 (4)의 해가 유일하다.
   $\zeta(0) = \exp(\xi_0^\wedge) = \eta(0)$ 이므로 $\zeta \equiv \eta$. C.
4. **왜 "큰 오차에서도"인가.** 2·3 단계는 $\lVert\xi\rVert$ 가 작다는 것을 **쓰지 않는다**.
   보통의 EKF 에서 선형화가 "작은 오차"를 요구하는 것은 상태 공간에서 Taylor 전개를 하기
   때문인데, 여기서는 전개가 아니라 **좌표 변환**($\eta \mapsto \xi$)이 선형 동역학을 만든다.
5. **한계.** C 는 (4)에 대한 진술이고, (4) 자체가 성립하려면 H1(군 아핀)이 필요하다. 군 아핀이
   아닌 동역학(예: 바이어스를 상태에 넣은 IMU 모형의 일부, 공기역학 항)에서는 $\dot\eta$ 에
   $X$ 가 남고 이 정리가 적용되지 않는다. 또 측정 갱신은 이 정리의 범위 밖이다.

**가설을 지우면**: H1 을 빼면 (11)의 소거가 일어나지 않아 $\dot\eta$ 가 $X$ 에 의존하고,
"오차만의 동역학"이라는 전제가 사라진다. H3 의 $A_u$ 는 군 아핀일 때만 **상수**다 —
그렇지 않으면 $A_u(t, X)$ 가 되어 보통의 EKF 로 돌아간다. 즉 **군 아핀성이 로그-선형성의
필요조건에 가깝다**(원 논문 Theorem 1-2 의 역방향 논의).

(생략: 1·2 단계의 $\mathrm{d}\exp$ 계산과 $g_u$ 가 리 대수 위 선형임의 증명.
`barrau2017-invariant-ekf` Theorem 1-2 와 그 증명.)

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (증명, ★★, R1)** R1 의 C1·C2 를 빠진 줄 없이 쓰고, 다음을 보여라: $SO(3)$ 에서
$\mathcal{R}_R(\phi) = R\exp(\hat\phi)$ 와 Cayley 재추적
$\mathcal{R}_R(\phi) = R\,(I - \tfrac12\hat\phi)^{-1}(I + \tfrac12\hat\phi)$ 가 **둘 다** 재추적이고
1차에서 같지만 2차에서 다르다.
*전략 + 핵심 부등식*: 재추적 조건은 $\mathcal{R}(0) = R$ 과 $\frac{d}{ds}\mathcal{R}(s\phi)|_{s=0}
= R\hat\phi$ 둘을 확인하면 끝난다. Cayley 는 $(I-\tfrac12\hat\phi)^{-1} = I + \tfrac12\hat\phi
+ \tfrac14\hat\phi^2 + \cdots$ 로 전개한다. 2차 차이는 $\hat\phi^2$ 계수를 $\exp$ 의 $\tfrac12$ 과
비교하면 보인다. 전개는 숨긴다.

**P2 (증명, ★★★, R3)** ⓐ $f_u(X) = X\hat u + \hat w X$ ($\hat u, \hat w \in \mathfrak{g}$ 상수)가
군 아핀임을 보이고 $g_u$ 를 구하라. ⓑ $f_u(X) = X\hat u X$ 는 군 아핀이 **아님**을 보이고,
(9)에서 $X$ 가 남는 지점을 정확히 지적하라. ⓒ 군 아핀 조건 (3)이 $f_u(I)$ 를 알면
$f_u$ 의 "비선형 부분"을 완전히 결정한다는 의미에서 얼마나 강한 제약인지 한 문단으로 논하라.
*전략*: ⓐ 는 (3)의 양변을 직접 전개해 비교한다. $g_u(\eta) = \hat w\eta - \eta\hat w$
($= [\hat w, \eta]$) 가 나온다 — 세계 프레임 입력은 오차에 남고 동체 프레임 입력은 사라진다는
해석을 쓸 것. ⓑ 는 반례 $X = Y = \exp(\epsilon\hat v)$ 로 충분하다. ⓒ 는 (3)을 $Y$ 로 미분해
$f_u$ 의 미분이 좌·우 평행이동으로 생성된다는 점을 짚으면 통과. 전개는 숨긴다.

**P3 (유도, ★★, R4)** (12)에서 **우불변 오차** $\eta_R = \hat X X^{-1}$ 의 이산 전파식을
유도하고, 잡음 항에 $\mathrm{Ad}_{X_k}$ 가 나타남을 보여라. 그로부터 "동체 프레임 잡음 +
세계 프레임 측정"이라는 조합에서는 좌·우 어느 쪽을 골라도 한쪽이 상태 의존이 됨을 논증하라.
*해답 스케치*: $\eta_{R,k+1} = \hat X_k\Delta\exp(-\nu^\wedge)\Delta^{-1}X_k^{-1}$ 를
$X_k\exp(\cdot)X_k^{-1}$ 꼴로 정리하면 $\eta_{R,k}\exp\big(-(\mathrm{Ad}_{X_k}\mathrm{Ad}_\Delta\nu)^\wedge\big)$
가 된다. 결론은 "불변성은 동역학·잡음·측정 **세 가지가 모두** 같은 쪽일 때만 완전하다"이고,
$SE_2(3)$ 위의 IMU 모형이 그 조합을 맞추는 설계라는 점을 지적하면 우수
(`c5-imu-preintegration` 에서 다룬다).

**P4 (계산, ★, R2)** $\hat X = (R_z(\pi/2),\ (10, 0, 0)^\top)$, $\Sigma_L = 10^{-4}I_6$ 일 때
ⓐ $\mathrm{Ad}_{\hat X}$, ⓑ $\Sigma_R$ 의 평행이동 블록과 그 표준편차, ⓒ 회전-평행이동 교차
블록을 구하라. ⓓ $\lVert p\rVert$ 를 100 m 로 바꾸면 ⓑ 가 어떻게 되는가?
*정답*: ⓐ $\mathrm{Ad} = \begin{bmatrix}R_z(\pi/2) & 0\\ \hat pR_z(\pi/2) & R_z(\pi/2)\end{bmatrix}$.
ⓑ $(\Sigma_R)_{\rho\rho} = \mathrm{diag}(10^{-4},\ 1.01\times10^{-2},\ 1.01\times10^{-2})$,
표준편차 $(0.01,\ 0.10049876,\ 0.10049876)$. ⓒ
$(\Sigma_R)_{\phi\rho} = \sigma_\phi^2 \hat p^\top = -10^{-4}\hat p$, 즉 비영 원소가
$\pm10^{-3}$ 인 반대칭 블록. ⓓ 표준편차가 $(0.01,\ 1.00005,\ 1.00005)$ — 레버 암에 **선형**으로
증폭된다. 허용오차 $10^{-8}$.
검산: $\Sigma_L$ 에서 $4\times10^5$ 개 표본을 뽑아 $\log(\hat X\exp(\xi_L^\wedge)\hat X^{-1})$ 의
표본 공분산을 ⓑ 와 비교한다 — 상대오차 1% 이내여야 한다(참조 구현 0.24%).

**P5 (계산, ★★, R3·R4)** (13)과 (5)를 코드로 옮겨 **전파만** 하는 두 필터를 돌리고
$\sigma_0 \in \{0.05,\ 0.2,\ 0.5\}$ 에서 $\mathrm{NEES}/6$ 을 측정하라(재현 과제 Part A).
ⓐ 두 필터의 값을 표로 쓰고 ⓑ 불변 EKF 의 값이 $\sigma_0$ 과 **무관하게** 1 인 이유를 R3' 의
어느 단계로 설명되는지 지적하라.
*정답*: 재현 과제 수용 기준 1 의 표가 정답이다. 불변 EKF 는 세 경우 모두 $1.00$-$1.05$,
EKF 는 $\sigma_0 = 0.5$ 에서 최대 $1.95$ 까지 오른다(스텝 120 근방). 허용오차: 불변 EKF 는
$[0.95, 1.10]$, EKF 의 최대값은 $> 1.8$.
*ⓑ의 채점 포인트*: R3' 의 4단계 — 선형성이 Taylor 전개가 아니라 **좌표 변환**에서 나오므로
$\lVert\xi\rVert$ 가 커도 $F$ 가 정확하다. "Ad 가 선형이라서"만 쓰면 미달이다
($\mathrm{Ad}$ 가 **정확한** 켤레 변환이라는 점까지 써야 한다).

**P6 (구현, ★★★, R4)** 재현 과제 Part B 를 구현하라 — 측정 갱신까지 포함한 두 필터와
1000회 몬테카를로 NEES.
*루브릭*: ⓐ 각 필터의 NEES 를 **그 필터 자신의 오차 정의**로 계산했다(섞으면 즉시 반송)
ⓑ 불변 EKF 의 $H$ 를 측정값 $y$ 로 구성한 버전과 $\hat y$ 로 구성한 버전을 **둘 다** 돌려
차이를 보고했다 ⓒ 첫 관측 시각과 마지막 관측 시각의 값을 분리해 보고했다 ⓓ 최종 RMSE 가
두 필터에서 거의 같다는 사실을 보고하고 "일관성 $\ne$ 정확도"를 명시했다.

**P7 (반례, ★★, R3·R4)** "불변 EKF 는 EKF 보다 항상 좋다"가 거짓임을 보여라. ⓐ 측정이
불변 구조와 맞지 않는 경우(예: 동체 프레임 잡음 + 세계 프레임 위치 측정)를 구성해 불변 EKF 가
EKF 와 같거나 더 나쁜 영역을 수치로 제시하고, ⓑ 오차가 작을 때 두 필터가 수치적으로 같아지는
이유를 쓰라.
*성질 체크리스트*: ⓐ 는 P3 의 결론을 쓴다 — 측정의 불변성과 잡음의 불변성이 다르면 $H$ 또는
$F$ 한쪽이 상태 의존이 된다. 재현 과제의 설정에서 $H$ 를 $\hat y$ 로 되돌리면 실제로 더
나빠진다(참조 구현: ANEES$/6$ 이 $3.23 \to 13.35$ — EKF 의 $6.86$ 보다도 나쁘다). ⓑ 는 $\mathrm{Ad}_{\exp(\xi)} = I +
\mathrm{ad}_\xi + O(\xi^2)$ 로 두 야코비안의 차가 $O(\lVert\xi\rVert)$ 임을 보이면 통과.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Barrau & Bonnabel, "The invariant extended Kalman filter as a stable observer" (2017,
   IEEE T-AC)** — 역할: `원전(seminal)`. <https://arxiv.org/abs/1410.1465> (II-III 절)
   추가 질문: ⓐ 저자들의 Theorem 1·2 를 본문 (11)과 R3' 의 진술로 각각 옮겨 쓰면?
   ⓑ "stable observer"라는 제목의 안정성 주장은 **무엇에 대한** 안정성이고, 그것이 추정
   정확도를 보장하는가? ⓒ 저자들이 측정 갱신의 비선형성에 대해 무엇을 말하고 무엇을 말하지
   않는가?
2. **Solà, Deray & Atchuthan, "A micro Lie theory for state estimation in robotics" (2018,
   arXiv)** — 역할: `표준(standard)`. <https://arxiv.org/abs/1812.01537> (4-7절)
   추가 질문: ⓐ 이 글의 $\oplus/\ominus$ 규약을 본문의 $\eta_L/\eta_R$ 로 번역하면 어느 쪽인가?
   ⓑ 부록의 $SE(3)$ 야코비안 표를 (13)의 $F$ 와 대조해 부호가 맞는지 확인하라.
3. **Absil, Mahony & Sepulchre, "Optimization Algorithms on Matrix Manifolds" (2008)** —
   역할: `표준(standard)`. <https://doi.org/10.1515/9781400830244> (§4.1 과 ch.7)
   추가 질문: ⓐ 재추적의 정의에서 $D\mathcal{R}_X(0) = \mathrm{id}$ 조건을 빼면 저자들의
   수렴 정리 중 어느 것이 먼저 깨지는가? ⓑ 저자들의 "vector transport"가 추정 문제에서
   무엇에 대응하는가(힌트: R2).

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, Part A 2000회 + Part B 1000회
몬테카를로가 5분 이내(순수 numpy, $6\times6$ 행렬 연산). 메모리 500MB 이하.

**입력 데이터**는 아래 시뮬레이터가 만든다(고정 시드). 외부 데이터셋이 필요 없다. 리 군
유틸리티도 함께 제공하므로 **학습자가 쓸 것은 두 필터뿐**이다.

```python
"""c5-manifold-estimation 재현 과제: SE(3) 시뮬레이터와 리 군 유틸리티."""

import numpy as np

SEED = 20261112
DT, STEPS, OBS_EVERY = 0.05, 200, 10
SIGMA_PHI, SIGMA_RHO, SIGMA_Y = 0.02, 0.01, 0.10
U = np.array([0.1, -0.2, 0.5, 1.0, 0.0, 0.0])  # 동체 트위스트 (omega, v)
LANDMARKS = np.array([[8.0, 0.0, 1.0], [0.0, 8.0, -1.0], [-8.0, 0.0, 2.0], [0.0, -8.0, 0.0]])
Q = np.diag([SIGMA_PHI**2] * 3 + [SIGMA_RHO**2] * 3)
RY = SIGMA_Y**2 * np.eye(3)


def skew(w):
    return np.array([[0.0, -w[2], w[1]], [w[2], 0.0, -w[0]], [-w[1], w[0], 0.0]])


def pose(R, p):
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, p
    return T


def inv(T):
    R, p = T[:3, :3], T[:3, 3]
    return pose(R.T, -R.T @ p)


def exp_so3(phi):
    t, W = float(np.linalg.norm(phi)), skew(phi)
    if t < 1e-10:
        return np.eye(3) + W + 0.5 * W @ W
    return np.eye(3) + np.sin(t) / t * W + (1.0 - np.cos(t)) / t**2 * W @ W


def log_so3(R):
    c = min(1.0, max(-1.0, (np.trace(R) - 1.0) / 2.0))
    t = float(np.arccos(c))
    W = 0.5 * (R - R.T) if t < 1e-10 else 0.5 * (R - R.T) * (t / np.sin(t))
    return np.array([W[2, 1], W[0, 2], W[1, 0]])


def jac_l_so3(phi):
    """좌 야코비안 J_l — SE(3) 지수 사상의 평행이동 블록."""
    t, W = float(np.linalg.norm(phi)), skew(phi)
    if t < 1e-10:
        return np.eye(3) + 0.5 * W + W @ W / 6.0
    return np.eye(3) + (1.0 - np.cos(t)) / t**2 * W + (t - np.sin(t)) / t**3 * W @ W


def exp_se3(xi):
    return pose(exp_so3(xi[:3]), jac_l_so3(xi[:3]) @ xi[3:])


def log_se3(T):
    phi = log_so3(T[:3, :3])
    return np.concatenate([phi, np.linalg.solve(jac_l_so3(phi), T[:3, 3])])


def adjoint(T):
    R, p = T[:3, :3], T[:3, 3]
    A = np.zeros((6, 6))
    A[:3, :3], A[3:, :3], A[3:, 3:] = R, skew(p) @ R, R
    return A


def simulate(seed, p0_cov):
    """참 궤적, 초기 추정, 오도메트리 증분, 관측을 돌려준다."""
    rng = np.random.default_rng(seed)
    delta = exp_se3(U * DT)
    x = np.eye(4)
    x0_hat = x @ exp_se3(rng.multivariate_normal(np.zeros(6), p0_cov))
    truth, obs = [], {}
    for k in range(STEPS):
        x = x @ delta @ exp_se3(rng.multivariate_normal(np.zeros(6), Q))
        truth.append(x.copy())
        if (k + 1) % OBS_EVERY == 0:
            xi = inv(x)
            obs[k] = [
                xi[:3, :3] @ pl + xi[:3, 3] + rng.normal(scale=SIGMA_Y, size=3) for pl in LANDMARKS
            ]
    return truth, x0_hat, delta, obs
```

**해야 할 일.** (13)의 불변 EKF 와 (5)(14)(15)의 표준 EKF 를 구현한다. 초기 추정은
`simulate` 가 돌려주는 `x0_hat` 을 **두 필터에 공통으로** 쓰고, 초기 공분산은 둘 다
$P_0 = \sigma_0^2 I_6$ 로 둔다($X_0 = I$ 이므로 두 규약에서 같다 — 왜 그런지는 (2)에서 확인하라).
NEES 는 각 필터 자신의 오차 정의로 계산한다.

**Part A — 전파만.** 측정을 쓰지 않고 200 스텝을 전파하며 스텝 0·40·80·120·160·199 에서
$\mathrm{NEES}/6$ 을 기록한다. $\sigma_0 \in \{0.05,\ 0.2,\ 0.5\}$, 2000회 몬테카를로
(시드 $5000 + m$).

**Part B — 전체 필터.** 10 스텝마다 랜드마크 4개를 갱신에 넣는다. $\sigma_0 = 0.5$,
1000회 몬테카를로(시드 $\mathrm{SEED} + m$). 관측 시각 20개에서 NEES 를 기록한다.

**Part C — 좌/우 변환.** 문제 P4 의 설정에서 (2)를 수치로 확인한다.

**Part D — 군 아핀 검증.** $f_u(X) = X\hat u$ 에 대해 (3)의 양변 차와 $g_u(\eta)$ 를 무작위
$X, Y, \eta$ 에서 측정한다.

**수용 기준 — 네 조건을 모두 만족해야 통과다.**

1. **Part A** — 아래 표를 재현한다(각 값 $\pm0.05$, 단 EKF 의 $\sigma_0 = 0.5$ 행은 최대값이
   $1.8$ 을 넘는 것만 확인).

   | $\sigma_0$ | 필터 | 스텝 0 / 40 / 80 / 120 / 160 / 199 |
   |---|---|---|
   | 0.05 | EKF | 1.01 / 1.01 / 1.07 / 1.07 / 1.06 / 1.05 |
   | 0.05 | 불변 EKF | 1.02 / 1.00 / 1.01 / 1.00 / 1.01 / 1.00 |
   | 0.20 | EKF | 1.01 / 1.07 / 1.17 / 1.16 / 1.11 / 1.07 |
   | 0.20 | 불변 EKF | 1.02 / 1.02 / 1.01 / 1.01 / 1.03 / 1.02 |
   | 0.50 | EKF | 1.00 / 1.34 / 1.89 / 1.95 / 1.59 / 1.24 |
   | 0.50 | 불변 EKF | 1.02 / 1.02 / 1.02 / 1.03 / 1.05 / 1.04 |

   **핵심은 마지막 두 행의 대조다**: 불변 EKF 의 값이 $\sigma_0$ 에 거의 반응하지 않는다.
2. **Part B** — $\mathrm{ANEES}/6$ 이 EKF $6.86 \pm 0.3$, 불변 EKF $3.23 \pm 0.2$ (비 $\ge 2.0$);
   첫 관측 시각이 EKF $96.9 \pm 5$, 불변 EKF $33.3 \pm 2$ (비 $\ge 2.5$); 마지막 관측 시각은
   **둘 다** $1.00 \pm 0.05$. 최종 위치 RMSE 는 EKF $0.0617$ m, 불변 EKF $0.0624$ m
   ($\pm 0.002$, 서로 5% 이내) — **일관성은 2배 차이인데 정확도는 같다**는 것을 반드시 보고한다.
3. **Part C** — $\Sigma_R$ 의 평행이동 표준편차가 $(0.01,\ 0.10049876,\ 0.10049876)$ 과
   $10^{-8}$ 이내로 일치하고, $4\times10^5$ 표본 몬테카를로 공분산과의 상대오차가 1% 이내
   (참조 구현 0.24%).
4. **Part D** — 무작위 $X, Y$ 500쌍에서 (3)의 양변 차가
   $\max\lvert\cdot\rvert < 10^{-14}$ (참조 $2.2\times10^{-16}$), 그리고 $g_u(\eta) = 0$ 이
   $\max\lvert\cdot\rvert < 10^{-15}$ (참조 정확히 0).

**비교 대상**: ⓐ Part A·B 의 베이스라인은 표준 EKF 자신이다(같은 데이터, 같은 초기 추정).
ⓑ 불변 EKF 의 $H$ 를 측정값 $y$ 대신 예측값 $\hat y$ 로 만든 변형을 세 번째 필터로 돌려
ANEES 를 보고한다 — 불변성이 어디서 오는지 분리된다. 참조 구현의 300회 측정값은
ANEES$/6 = 13.348$ 로, **표준 EKF($6.858$)보다도 나쁘다**: 불변 EKF 의 이점은 군 구조에서
자동으로 오는 것이 아니라 $H$ 를 측정값으로 구성하는 선택에서 온다. ⓒ 선택: $\sigma_0$ 을 $0.05$ 로 줄여
Part B 를 다시 돌려 두 필터의 차이가 사라지는 것을 확인한다.

**보고할 수치**: 위 네 조건의 모든 값, Part B 의 관측 시각별 NEES 곡선(참조 구현 EKF
$96.95 \to 15.67 \to 5.37 \to 2.37 \to 1.46 \to 1.15 \to \cdots \to 1.00$, 불변 EKF
$33.25 \to 9.47 \to 3.63 \to 1.76 \to 1.24 \to 1.08 \to \cdots \to 1.02$), 그리고 최종
회전 RMSE(참조 양쪽 모두 $0.0133$ rad).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 두 필터의 NEES 가 똑같이 나온다 | NEES 를 한 가지 오차 정의로만 계산했다 | 불변 EKF 는 $\log(X^{-1}\hat X)$, EKF 는 $(\log(\hat RR^\top), \hat p - \hat p_{\text{참}})$ 인지 확인 |
| 불변 EKF 가 EKF 보다 **나쁘다** | $H$ 를 $\hat y$ 로 만들었다(불변 형태가 아니다), 또는 $\xi$ 성분 순서를 $(\rho,\phi)$ 로 섞었다 | $H = [-\widehat{y},\ I]$ 인지, $\mathrm{Ad}$ 의 블록 배치가 표기표와 같은지 확인 |
| NEES 가 스텝과 함께 단조 발산한다 | $P$ 가 대칭성을 잃었다(Joseph 형태를 쓰지 않음) | $\lVert P - P^\top\rVert_\infty$ 를 매 스텝 출력하고 $(I-KH)P(I-KH)^\top + KRK^\top$ 을 쓴다 |
| $\sigma_0 = 0.5$ 에서 `log_se3` 가 튄다 | $\lVert\phi\rVert$ 가 $\pi$ 를 넘어 주 분기를 벗어났다 | NEES 계산 전에 $\lVert\log(\cdot)\rVert$ 분포를 보고 $\pi$ 근방 표본 비율을 보고한다 |
| Part A 에서 불변 EKF 도 1 에서 벗어난다 | 전파에 $\mathrm{Ad}_{\Delta^{-1}}$ 대신 $\mathrm{Ad}_{\Delta}$ 를 썼다 | $\Delta$ 를 항등으로 두면 두 경우가 같아지는지, 작은 $u$ 에서 차이가 $O(u)$ 인지 확인 |
| 갱신 뒤 추정이 발산한다 | 보정 부호 — 좌불변 오차에서는 $\hat X \leftarrow \hat X\exp(-\delta\xi^\wedge)$ 다 | 한 스텝만 돌려 $\lVert\log(X^{-1}\hat X)\rVert$ 가 줄어드는지 확인 |

## 열린 문제

- **(열린 문제) 군 아핀이 아닌 계를 위한 체계적 설계** — IMU 바이어스, 축척 인자, 공기역학,
  접촉 상태처럼 실제 로봇의 상태 일부는 (3)을 만족하지 않는다. 지금은 사례별로 더 큰 군을
  찾거나($SE_2(3)$, 접촉점을 상태에 넣은 확장 — [contact-aided
  InEKF](https://doi.org/10.1177/0278364919894385)) "불변 + 비불변" 혼합 필터를 쓴다.
  비어 있는 자리: 주어진 동역학·측정 쌍에 대해 군 아핀 구조를 **찾거나 없음을 증명하는** 절차와,
  그 구조가 없을 때 남는 비일관성의 상계.
- **(열린 문제) 갱신 단계의 비일관성** — R3' 은 전파에 대한 정리이고 측정 갱신은 여전히 1차
  전개다. 재현 과제의 실측이 그 대가다(첫 시각 NEES$/6$ 이 불변 EKF 에서도 33). 현재 접근:
  반복 갱신(iterated EKF), 불변 측정 모형의 설계, 사후 정보를 쓰는 평활
  ([factor graph 백엔드](https://doi.org/10.1561/2300000043)). 비어 있는 자리: 큰 오차에서
  **갱신까지** 정확한(또는 오차가 상계되는) 매니폴드 필터.
- **(열린 문제) 큰 불확실성에서 접공간 가우시안 자체의 타당성** — $\lVert\phi\rVert$ 가
  $\pi$ 에 접근하면 $\xi$ 가 유일하지 않고, 접공간 가우시안이 $SO(3)$ 위의 분포를 제대로
  표현하지 못한다(`c1-so3-se3-exponential` 의 열린 문제와 같은 뿌리). 현재 접근:
  Bingham·von Mises-Fisher 같은 방향 통계 분포, [Barfoot SER
  ch.6](https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf) 의 변분 추론,
  [micro Lie theory](https://arxiv.org/abs/1812.01537) 의 규약 정리. 비어 있는 자리:
  로보틱스 규모에서 "언제 접공간 가우시안을 버려야 하는가"에 대한 정량적 판정 기준.

## 개념 점검

`rc quiz c5-manifold-estimation` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c5-manifold-estimation-quiz
questions:
  - id: q1
    type: single
    prompt: "재추적(retraction) $\\mathcal{R}_X$ 의 정의에서 $D\\mathcal{R}_X(0) = \\mathrm{id}$ 조건이 보장하는 것은?"
    choices:
      - "들어 올린 문제의 전역 최솟값이 원 문제의 전역 최솟값과 같다"
      - "들어 올린 문제의 1차 모델과 임계점이 재추적 선택과 무관하다"
      - "$\\mathcal{R}_X$ 가 전단사다"
      - "Hessian 이 재추적 선택과 무관하다"
    answer: 1
    explanation: "연쇄법칙에서 $D\\tilde F(0) = DF(X)\\circ D\\mathcal{R}_X(0) = DF(X)$ 이므로 기울기·잔차 야코비안·임계점이 모두 같아진다. Hessian 은 임계점에서만 같고(기울기 $\\times$ 재추적의 2차 미분 항이 사라진다), 전역 성질이나 전단사성은 전혀 따라오지 않는다."
    concept: { front: "재추적 조건 $D\\mathcal{R}_X(0)=\\mathrm{id}$", back: "1차 모델·야코비안·임계점이 재추적 선택과 무관해진다. Hessian 은 임계점에서만 같다" }
  - id: q2
    type: single
    prompt: "좌불변 오차의 공분산 $\\Sigma_L$ 을 우불변 규약으로 옮기면?"
    choices:
      - "$\\Sigma_R = \\Sigma_L$ — 규약은 표기 차이일 뿐이다"
      - "$\\Sigma_R = \\mathrm{Ad}_{\\hat X}\\Sigma_L\\mathrm{Ad}_{\\hat X}^\\top$"
      - "$\\Sigma_R = \\mathrm{Ad}_{\\hat X}^{-1}\\Sigma_L\\mathrm{Ad}_{\\hat X}^{-\\top}$"
      - "$\\Sigma_R = J_r\\Sigma_L J_r^\\top$"
    answer: 1
    explanation: "$\\xi_R = \\mathrm{Ad}_{\\hat X}\\xi_L$ 이므로 (2)가 성립한다. $SE(3)$ 에서 $\\mathrm{Ad}$ 의 $\\hat pR$ 블록이 회전 불확실성을 평행이동으로 레버 암에 비례해 증폭한다 — $\\lVert p\\rVert = 10$ m 에서 위치 표준편차가 0.01 에서 0.1005 로 10배가 된다."
    concept: { front: "좌/우 공분산 변환", back: "$\\Sigma_R = \\mathrm{Ad}_{\\hat X}\\Sigma_L\\mathrm{Ad}_{\\hat X}^\\top$ — 레버 암이 회전 불확실성을 위치로 선형 증폭한다. 규약 없는 공분산은 의미가 없다" }
  - id: q3
    type: short
    prompt: "군 아핀 동역학에서 우불변 오차가 만족하는 자율 동역학 $g_u(\\eta)$ 를 $f_u$ 로 쓰면?"
    answer: ["f_u(eta) - eta f_u(I)", "f(eta) - eta f(I)", "f_u(η) - η f_u(I)", "f_u(eta)-eta*f_u(I)", "f_u(eta) - eta f_u(e)"]
    explanation: "$g_u(\\eta) = f_u(\\eta) - \\eta f_u(I)$ 다((4)). 유도의 핵심은 $\\hat X = \\eta X$ 를 넣고 군 아핀 조건을 적용하면 $\\eta f_u(X)X^{-1}$ 항이 정확히 소거되어 $X$ 가 사라지는 것이다. 근사가 한 줄도 들어가지 않는다."
    concept: { front: "군 아핀 계의 불변 오차 동역학", back: "$g_u(\\eta) = f_u(\\eta) - \\eta f_u(I)$ — 상태 $X$ 가 정확히 소거된다. 동체 오도메트리 $f_u(X)=X\\hat u$ 에서는 $g_u \\equiv 0$" }
  - id: q4
    type: truefalse
    prompt: "로그-선형 성질 덕분에 불변 EKF 는 측정 갱신까지 포함해 임의로 큰 오차에서 정확하다."
    answer: false
    explanation: "로그-선형 성질은 **전파**에 대한 정리다. 측정 갱신은 여전히 1차 전개이므로 큰 오차에서는 불변 EKF 도 일관되지 않다 — 재현 과제의 실측에서 첫 관측 시각의 NEES/6 이 EKF 96.9, 불변 EKF 33.3 이다. 불변 EKF 는 비일관성을 없애지 않고 줄인다."
    concept: { front: "로그-선형 성질의 범위", back: "전파만 정확하다. 갱신은 여전히 선형화 — 큰 오차에서 불변 EKF 도 과신한다(33 vs 97, 둘 다 1 아님)" }
  - id: q5
    type: single
    prompt: "필터의 NEES 를 재현 과제처럼 측정했을 때 $\\mathrm{ANEES}/\\dim = 6.9$ 가 뜻하는 것은?"
    choices:
      - "추정 오차가 이론값보다 6.9배 크다"
      - "공분산이 실제 오차에 비해 과소평가되어 있다(과신)"
      - "공분산이 과대평가되어 있다(보수적)"
      - "필터가 발산했다"
    answer: 1
    explanation: "$\\mathbb{E}[\\mathrm{NEES}] = \\dim$ 이 일관성의 기준이므로 $\\mathrm{ANEES}/\\dim > 1$ 은 분모의 $\\Sigma$ 가 너무 작다는 뜻 — 과신이다. 오차 자체의 크기와는 다른 이야기다: 재현 과제에서 두 필터의 최종 RMSE 는 거의 같은데 ANEES 는 2배 차이가 난다."
    concept: { front: "ANEES/dim 의 해석", back: "$>1$ 과신(공분산 과소), $<1$ 보수적. 정확도와 다른 축이다 — RMSE 가 같아도 ANEES 는 2배 차이가 날 수 있다" }
```

## 이 단계 공부법

1. **규약을 먼저 고정한다 (45분)** — 표기표의 $\eta_L$·$\eta_R$·$\mathrm{Ad}$·$(\phi,\rho)$
   순서를 종이에 옮겨 쓰고, (7)을 손으로 전개해 $\xi_R = \mathrm{Ad}_{\hat X}\xi_L$ 을 직접
   얻는다. 이 레슨에서 가장 많이 생기는 버그가 전부 이 표에 있다.
2. **P4 를 먼저 푼다 (30분)** — 숫자가 $0.01 \to 0.1005$ 로 10배 벌어지는 것을 보면 "규약 없는
   공분산"이 왜 무의미한지 몸으로 안다. Barfoot SER ch.7 의 좌/우 불확실성 절을 같이 읽는다.
3. **(9)-(11)을 백지에서 다시 쓴다 (60분)** — R3 의 소거는 **세 줄**이다. 그 세 줄을 외우지
   말고, $\hat X = \eta X$ 를 넣는 지점과 군 아핀 조건을 적용하는 지점을 설명할 수 있게 한다.
   그 다음 예 1·2 를 직접 계산해 $g_u = 0$ 과 $[\eta,\hat u]$ 를 얻는다.
4. **왜 큰 오차에서도 되는지 한 문단으로 쓴다 (30분)** — R3' 4단계가 답이다. "선형화가 아니라
   좌표 변환"이라는 문장을 자기 말로 쓸 수 있으면 이 레슨의 중심이 끝났다.
5. **재현 과제 Part A 를 먼저 (60분)** — 측정 없이 전파만. 불변 EKF 의 줄이 $\sigma_0$ 에
   반응하지 않는 표를 직접 찍는 것이 이 레슨에서 가장 설득력 있는 경험이다. 틀렸을 때
   먼저 볼 것은 $\mathrm{Ad}_{\Delta^{-1}}$ 의 방향과 $(\phi,\rho)$ 순서다.
6. **Part B·C·D (135분)** — Part B 에서 갱신을 넣으면 **둘 다** 1 이 아니게 되는 것을 보고,
   최종 RMSE 가 같은 것을 보고, "일관성 $\ne$ 정확도"를 보고서에 쓴다. $H$ 를 $\hat y$ 로
   되돌린 세 번째 필터를 돌려 불변성이 어디서 오는지 분리한다.
7. **논문은 순서대로 (150분)** — Solà et al. 4-7절로 규약을 맞춘 뒤, Barrau & Bonnabel II-III
   절에서 (11)과 R3' 의 원문을 확인하고, Absil et al. §4.1 로 재추적의 정의를 정확히 읽는다.
   논문당 1페이지 노트는 **반드시** 쓴다.
8. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제" 세 개 중 하나를 골라 한 문단으로 쓴다.
   갱신 단계의 비일관성은 재현 과제의 숫자가 바로 증거이므로 가장 쓰기 쉽다.

**통과 기준**: 백지에서 (2)와 (9)-(11)을 유도할 수 있고, R3' 의 "선형화가 아니라 좌표 변환"
논증을 쓸 수 있고, 재현 과제의 네 조건을 모두 만족하는 코드를 갖고 있고, 논문 3편의 노트가 있다.
