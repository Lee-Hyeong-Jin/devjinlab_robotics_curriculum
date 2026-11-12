---
id: c5-observability-consistency
title: 관측가능성과 추정 일관성
summary: >-
  비선형 관측가능성의 Lie 미분 랭크 조건(Hermann-Krener)을 진술하고, 단안 관성-시각 추정의
  불관측 부분공간이 중력축 요(yaw) 1 + 전역 평행이동 3 = 4차원임을 불변군의 생성원으로 유도한다.
  EKF-SLAM 의 비일관성이 "선형화 지점이 시각마다 달라 영공간이 깨지는" 현상임을 보이고, 대수적으로
  동일한 두 야코비안 중 하나만 영공간을 보존한다는 FEJ 의 기계를 수치 랭크로 확인한다.
objectives:
  - Hermann-Krener 의 국소 약관측가능성 정리를 가설과 결론을 분리해 진술하고 랭크 조건을 계산할 수 있다.
  - 단안 관성-시각 추정의 불관측 방향 4개를 불변군의 생성원으로 직접 쓸 수 있다.
  - 선형화된 계의 영공간 차원을 수치 랭크로 측정하고 퇴화 운동에서 늘어나는 것을 확인할 수 있다.
  - EKF 의 야코비안 평가 지점이 영공간을 깨뜨려 거짓 정보를 주입하는 과정을 설명할 수 있다.
  - 대수적으로 동일한 두 야코비안 표현이 선형화 후에는 다른 필터가 되는 이유를 말할 수 있다.
  - 관측가능성·일관성·정확도가 서로 다른 축임을 수치로 구분해 보고할 수 있다.
prerequisites: [c5-imu-preintegration, c5-manifold-estimation]
difficulty: 5
estimated_minutes: 660
tags: [state-estimation, observability, consistency, fej, ekf-slam, vio, research]
activities:
  - id: c5-observability-consistency-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 105
  - id: c5-observability-consistency-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c5-observability-consistency-problems
    kind: exercise
    title: 문제 세트 (증명 2 · 유도 1 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: c5-observability-consistency-reproduction
    kind: reproduction
    title: 재현 과제 — VIO 영공간 4차원, FEJ 의 영공간 보존, NEES (R2)
    estimated_minutes: 210
  - id: c5-observability-consistency-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.5 (Biases, Correspondences, and Outliers). 비이상성(nonideality) 논의의 교재 진입로. 전문 PDF 무료.
papers:
  - id: huang2010-fej
    required: true
    role: seminal
    note: "§3-5"
  - id: li2013-vio-observability
    required: true
    role: standard
    note: "§3-4"
  - id: hermann1977-observability
    required: true
    role: seminal
    note: "Thm. 3.1"
  - id: hesch2014-vio-observability
    role: standard
  - id: cadena2016-slam-survey
    role: survey
    note: "§III-IV"
---

# 관측가능성과 추정 일관성

## 전제와 기호

`c5-manifold-estimation` 의 리 군·NEES 표기와 `c5-imu-preintegration` 의 IMU 모형을 그대로 쓴다.
추가 기호:

| 기호 | 뜻 |
|---|---|
| $\dot x = f(x, u)$, $z = h(x)$ | 비선형 계의 동역학과 측정. $x \in \mathcal{M}$ (상태 매니폴드) |
| $L_f^k h$ | $h$ 의 $k$ 차 Lie 미분. $L_f h = \nabla h \cdot f$, $L_f^{k+1}h = L_f(L_f^k h)$ |
| $\mathcal{O}$ | **관측가능성 여분포(codistribution)** $= \mathrm{span}\{\mathrm{d}L_f^k h_j : k \ge 0\}$ |
| $\Phi_{k,0}$ | 선형화된 계의 상태 전이 $\Phi_{k-1}\cdots\Phi_0$ |
| $H_k$ | 시각 $k$ 의 측정 야코비안 |
| $M$ | **관측가능성 행렬**. 행 블록이 $H_k\Phi_{k,0}$ 인 쌓은 행렬 |
| $\mathcal{N} = \ker M$ | 선형화된 계의 **불관측 부분공간** |
| $N$ | $\mathcal{N}$ 의 해석적 기저(불변군 생성원을 모은 행렬) |
| $\hat x_{k\mid k-1}$, $\hat x_{k\mid k}$ | 전파(예측) 추정과 갱신 후 추정. **FEJ 는 앞의 것을 선형화 지점으로 쓴다** |
| $u_g = g/\lVert g\rVert$ | 중력 방향 단위벡터(세계 프레임) |

**세 가지를 구별한다.** 이 레슨의 거의 모든 혼동이 다음 셋을 섞는 데서 온다:

- **관측가능성(observability)** — 측정이 상태를 결정하는가. 추정기와 무관한 **문제의 성질**이다.
- **일관성(consistency)** — 추정기가 보고하는 공분산이 실제 오차 분포와 맞는가
  ($\mathbb{E}[\mathrm{NEES}] = \dim$). **추정기의 성질**이다.
- **정확도(accuracy)** — 오차가 작은가. 위 둘과 독립적으로 움직일 수 있다.

R5 와 재현 과제 Part C 가 이 셋이 실제로 어긋나는 것을 수치로 보여 준다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (Hermann-Krener: 국소 약관측가능성의 랭크 조건) [D3]** — 해석적 계
  $\dot x = f(x,u)$, $z = h(x)$ 에 대해 $x_0$ 에서
  $$
  \dim \mathcal{O}(x_0) = \dim\mathcal{M}
    \quad\Longrightarrow\quad x_0 \text{ 에서 국소 약관측가능(locally weakly observable)}. \tag{1}
  $$
  역은 일반적으로 성립하지 않지만, 해석적 계에서는 랭크 조건이 **거의 모든** 점에서 필요조건이기도
  하다. 실무에서 쓰는 것은 대우(contrapositive)다 — **랭크가 모자라면 그 방향은 어떤 추정기로도
  결정할 수 없다.**
- **R2 (단안 관성-시각 추정의 불관측 부분공간은 4차원) [D3]** — 상태가
  $\{(R_k, v_k, p_k)\}_{k} \cup \{p_{f_i}\}_i$ 이고 측정이 IMU(동체 프레임)와 베어링(단안)일 때,
  잔차를 보존하는 변환군은
  $$
  (R_k, v_k, p_k, p_{f_i}) \;\longmapsto\;
    \big(R_\psi R_k,\ R_\psi v_k,\ R_\psi p_k + t,\ R_\psi p_{f_i} + t\big),
    \qquad R_\psi := \exp(\psi\,\hat u_g),\ t\in\mathbb{R}^3 \tag{2}
  $$
  이고 이는 $\dim = 1 + 3 = 4$ 인 리 군이다. 그 생성원 4개가 선형화된 계의 영공간을 **정확히**
  span 한다. 재현 과제의 실측: $N = 45$ 차원 문제에서 수치 랭크 41, 영공간 차원 **4**
  (특잇값 간격이 $1.3\times10^{-3}$ 대 $7.4\times10^{-11}$ — 8자리).
- **R2' (퇴화 운동은 영공간을 키운다) [D2]** — (2)는 운동과 무관한 **구조적** 불관측성이다.
  특정 운동은 여기에 방향을 더한다. 재현 과제의 실측: 세계 프레임 가속도가 상수인 궤적으로
  바꾸면 같은 문제의 영공간 차원이 **5**로 늘어난다 — `c5-imu-preintegration` R4 의 척도 모호성이
  랭크 결손으로 나타난 것이다.
- **R3 (EKF-SLAM 의 비일관성: 영공간이 깨진다) [D2]** — 이상적인 선형화(참값에서 평가)에서는
  $H_k\Phi_{k,0}N = 0$ 이 성립한다. 그런데 EKF 는 $H_k$ 와 $\Phi_k$ 를 **시각마다 다른 추정값**에서
  평가하므로 이 등식이 깨지고, $M$ 의 랭크가 올라간다. 랭크가 올라간 만큼이 **거짓 정보
  (spurious information)** 이고, 불관측 방향에 정보를 넣었으므로 공분산이 실제보다 작아진다.
  재현 과제의 실측(2D EKF-SLAM, $n = 11$): 이상 야코비안 영공간 3 / 표준 EKF 2,
  $\lVert MN\rVert/\lVert N\rVert$ 가 $6.07\times10^{-16}$ 에서 $2.658\times10^{-1}$ 로 올라간다.
- **R4 (FEJ: 대수적으로 같은 두 표현 중 하나만 영공간을 보존한다) [D2]** — 2D SLAM 의 전이
  야코비안의 $(1,3)$ 블록은 참 계에서 두 가지로 **똑같이** 쓸 수 있다:
  $$
  J\,R(\theta_k)u_k \qquad\text{또는}\qquad J\,(p_{k+1} - p_k), \tag{3}
  $$
  $p_{k+1} = p_k + R(\theta_k)u_k$ 이므로 참값에서는 같은 행렬이다. 그러나 추정값을 넣으면
  다르고, **$J(\hat p_{k+1\mid k} - \hat p_{k\mid k-1})$ 형태만** $\Phi_k N_k = N_{k+1}$ 을
  만족한다. 측정 야코비안을 첫 추정(FEJ)에서 평가하는 것과 묶으면 영공간이 **정확히** 보존된다.
  재현 과제의 실측: FEJ 영공간 3, $\lVert MN\rVert/\lVert N\rVert = 6.12\times10^{-16}$ —
  이상 야코비안과 기계 정밀도까지 같다.
- **R5 (관측가능성 ≠ 일관성 ≠ 정확도) [D1]** — R3·R4 는 거짓 정보를 **없앤다**는 진술이고,
  NEES 가 1 이 된다는 진술이 아니다. 재현 과제 Part C 의 실측이 그것을 보여 준다: 30스텝·전수
  관측 설정에서 표준 EKF 와 FEJ 의 $\mathrm{ANEES}/\dim$ 이 둘 다 $0.738$ 로 **구별되지 않고**,
  300스텝·거리 제한 설정에서는 표준 $0.915$ 대 FEJ $1.265$ 로 **FEJ 가 더 과신**하고 위치 RMSE 마저 나쁘다. 영공간
  보존은 필요하지만 충분하지 않다.

## 유도

### R2 — 불관측 방향 네 개를 불변군에서 읽는다

관측가능성을 랭크 계산으로 보기 전에, **무엇이 측정을 바꾸지 않는가**를 먼저 찾는다. 이것이 더
빠르고 기하적으로 정확하다.

측정은 두 종류다.

1. **IMU**(`c5-imu-preintegration` (1)): 자이로는 동체 각속도 $\omega_k$, 가속도계는
   $R_k^\top(a_k - g)$.
2. **단안 베어링**: $R_k^\top(p_{f_i} - p_k)$ 를 정규화한 방향.

(2)의 변환을 넣어 각각이 불변인지 확인한다. $R_\psi = \exp(\psi\hat u_g)$ 는 중력축 회전이므로
$R_\psi g = g$ 이고 $R_\psi^\top g = g$ 다. 이것이 유도의 전부다.

**자이로.** $\omega_k$ 는 동체 프레임 양이고, $R_k' = R_\psi R_k$ 는 $\dot R' = R'\hat\omega$ 를
그대로 만족한다($\dot R' = R_\psi\dot R = R_\psi R\hat\omega = R'\hat\omega$). 불변 ✓

**가속도계.** $a_k' = \ddot p_k' = R_\psi \ddot p_k = R_\psi a_k$ 이므로

$$
R_k'^\top(a_k' - g) = R_k^\top R_\psi^\top(R_\psi a_k - g)
  = R_k^\top\big(a_k - R_\psi^\top g\big) = R_k^\top(a_k - g). \tag{4}
$$

$R_\psi^\top g = g$ 를 쓴 **그 한 줄**이 "왜 중력축 회전만 불관측인가"의 답이다. 중력축이 아닌
회전 $R_\chi$ 에서는 $R_\chi^\top g \ne g$ 라서 (4)가 깨지고, 그래서 롤·피치는 관측된다.

**베어링.** $t$ 는 상쇄되고 $R_\psi$ 는 노름을 보존한다:

$$
\frac{R_k'^\top(p_{f_i}' - p_k')}{\lVert p_{f_i}' - p_k'\rVert}
  = \frac{R_k^\top R_\psi^\top\big(R_\psi p_{f_i} + t - R_\psi p_k - t\big)}{\lVert R_\psi(p_{f_i}-p_k)\rVert}
  = \frac{R_k^\top(p_{f_i} - p_k)}{\lVert p_{f_i} - p_k\rVert}. \tag{5}
$$

따라서 (2)의 4-매개변수 군 전체가 측정을 바꾸지 않는다. **생성원**(항등원에서 미분)을 쓰면
선형화된 계의 영공간 기저가 나온다. 평행이동 $t = \epsilon e$ 방향은

$$
n_e = \big(\underbrace{0}_{\delta\phi_k},\ \underbrace{0}_{\delta v_k},\
  \underbrace{e}_{\delta p_k},\ \underbrace{e}_{\delta p_{f_i}}\big), \tag{6}
$$

요 방향 $\psi = \epsilon$ 은(우 섭동 좌표 $R_k \leftarrow R_k\exp(\delta\phi_k)$ 규약에서)

$$
n_\psi = \big(\underbrace{R_k^\top u_g}_{\delta\phi_k},\
  \underbrace{u_g\times v_k}_{\delta v_k},\
  \underbrace{u_g\times p_k}_{\delta p_k},\
  \underbrace{u_g\times p_{f_i}}_{\delta p_{f_i}}\big). \tag{7}
$$

(7)의 첫 성분: $\exp(\epsilon\hat u_g)R_k = R_k\exp(\epsilon\,\widehat{R_k^\top u_g})$ 이므로
우 섭동 좌표에서 $\delta\phi_k = R_k^\top u_g$ 다(`c5-manifold-estimation` R2 의 $\mathrm{Ad}$
변환과 같은 계산). 나머지 성분은 $\frac{d}{d\epsilon}\exp(\epsilon\hat u_g)x = u_g\times x$ 다.

**가정이 깨지는 곳**: (2)는 ⓐ 중력의 **크기와 방향이 고정**되어 있고 ⓑ 가속도계 바이어스가
상태에 없고 ⓒ 측정이 베어링(스케일 없음)뿐이라는 세 전제에 기댄다. 거리 측정(스테레오·LiDAR)이
하나라도 들어오면 $t$ 는 여전히 불관측이지만 척도는 관측된다. 바이어스를 상태에 넣으면 (4)에
$b^a$ 가 더해져 추가 퇴화가 생길 수 있다(`c5-imu-preintegration` R4 의 "가정이 깨지는 곳").
그리고 (2)는 **운동과 무관한** 불관측성만 준다 — 운동이 만드는 추가 결손이 R2' 다.

### R3 — EKF 는 어떻게 거짓 정보를 만드는가

선형화된 계의 관측가능성 행렬을

$$
M = \begin{bmatrix} H_0 \\ H_1\Phi_{1,0} \\ \vdots \\ H_K\Phi_{K,0}\end{bmatrix} \tag{8}
$$

로 쌓는다. 불관측 방향의 정의는 $\mathcal{N} = \ker M$ 이고, R2 는 **참값에서 평가한**
$H_k, \Phi_k$ 에 대해 $MN = 0$ 임을 말한다. 참값에서 성립하는 이유는 두 항등식이다:

$$
H_k N_k = 0, \qquad \Phi_k N_k = N_{k+1}, \tag{9}
$$

여기서 $N_k$ 는 시각 $k$ 의 상태에서 평가한 생성원이다. 둘을 결합하면
$H_k\Phi_{k,0}N_0 = H_kN_k = 0$ 이다. (9)의 둘째 식이 핵심이다 — 영공간은 **시각마다 다른 벡터**이고,
전이 행렬이 그것을 정확히 실어 나른다.

이제 EKF 를 보자. EKF 는 $H_k$ 를 $\hat x_{k\mid k}$ (혹은 갱신 중간값)에서, $\Phi_k$ 를
$\hat x_{k\mid k}$ 에서 평가한다. 그러면 (9)의 어느 쪽도 성립하지 않는다:

- $H_k$ 가 $\hat x_{k\mid k}$ 에서, $\Phi_{k-1}$ 이 $\hat x_{k-1\mid k-1}$ 에서 평가되므로
  "같은 상태의 같은 선형화 지점"이라는 전제가 깨진다.
- 특히 **같은 상태를 서로 다른 시각에 서로 다른 값에서 평가**한다($\hat x_{k\mid k-1}$ 과
  $\hat x_{k\mid k}$, 그리고 랜드마크는 갱신마다 움직인다).

결과: $MN \ne 0$. $M$ 의 랭크가 올라가고, 올라간 차원은 **관측되지 않는 방향**이다. 필터가
그 방향으로 정보를 넣었다고 믿으므로 $P$ 가 작아지고, 참 오차는 줄지 않으므로 NEES 가 커진다.
이것이 EKF-SLAM 의 비일관성이고, 요(yaw)·방위 쪽에서 가장 먼저 나타난다.

**거짓 정보의 크기를 재는 법.** $\lVert MN\rVert/\lVert N\rVert$ 를 쓴다. 이상 야코비안에서는
기계 정밀도(재현 과제 $6.07\times10^{-16}$)이고, 표준 EKF 에서는 $O(10^{-1})$ 로 올라간다.
이 한 숫자가 "이 필터가 불관측 방향에 얼마나 정보를 넣었는가"의 직접 척도다.

**가정이 깨지는 곳**: 이 논증은 **선형화된** 계에 대한 것이다. 거짓 정보가 0 이어도(FEJ)
2차 이상의 비선형성이 남아 있고, 역으로 거짓 정보가 있어도 다른 효과(잡음 과대 설정, 이상치
제거의 보수성)가 상쇄해 NEES 가 1 근처로 보일 수 있다. R5 와 Part C 가 바로 그 경우다.

### R4 — 같은 야코비안의 두 표현이 다른 필터를 만든다

2D EKF-SLAM 을 쓴다. 상태 $x = (p_R, \theta, p_{f_1},\dots,p_{f_L})$, 운동
$p_{R,k+1} = p_{R,k} + R(\theta_k)u_k$, $\theta_{k+1} = \theta_k + \omega_k$, 측정
$z_{k,i} = R(\theta_k)^\top(p_{f_i} - p_{R,k})$. $J := \begin{bmatrix}0&-1\\1&0\end{bmatrix}$ 로
두면 2D 에서 $R(\theta)J = JR(\theta)$ 다(둘 다 같은 1-매개변수 군의 원소).

야코비안은

$$
\Phi_k = \begin{bmatrix} I_2 & \star & 0\\ 0 & 1 & 0\\ 0 & 0 & I\end{bmatrix}, \qquad
H_{k,i} = \begin{bmatrix} -R(\theta_k)^\top & -J R(\theta_k)^\top(p_{f_i}-p_{R,k}) & R(\theta_k)^\top\end{bmatrix}, \tag{10}
$$

영공간 기저는 R2 의 2D 버전이다(전역 평행이동 2 + 전역 회전 1):

$$
N_k = \begin{bmatrix} I_2 & J p_{R,k}\\ 0 & 1\\ I_2 & J p_{f_i}\end{bmatrix}. \tag{11}
$$

**$H_kN_k = 0$ 확인.** 평행이동 열은 $-R^\top + R^\top = 0$. 회전 열은

$$
-R^\top J p_{R} - JR^\top(p_f - p_R) + R^\top J p_f
  = R^\top J(p_f - p_R) - JR^\top(p_f - p_R) = 0, \tag{12}
$$

마지막 등식이 $R^\top J = JR^\top$ (2D 교환성)이다. **이 등식은 $R$ 을 어느 값에서 평가하든
성립한다** — 그래서 $H$ 쪽은 선형화 지점에 둔감하다. 문제는 $\Phi$ 다.

**$\Phi_kN_k = N_{k+1}$ 확인.** (11)에서 바뀌는 것은 회전 열의 첫 블록 $Jp_{R,k}$ 뿐이므로,
필요한 조건은

$$
\star + J p_{R,k} = J p_{R,k+1} \quad\Longleftrightarrow\quad \star = J\,(p_{R,k+1} - p_{R,k}). \tag{13}
$$

참 계에서는 $p_{R,k+1} - p_{R,k} = R(\theta_k)u_k$ 이므로 $\star$ 를 (3)의 **두 형태 중 아무
것으로나** 써도 된다. 그런데 추정값을 넣으면

$$
\hat p_{R,k+1\mid k} - \hat p_{R,k\mid k-1}
  \;\ne\; R(\hat\theta_{k\mid k-1})u_k \tag{14}
$$

다 — 좌변은 갱신 후 추정 $\hat p_{R,k\mid k}$ 에서 전파되고 우변은 전파 전 추정의 방위를 쓰기
때문이다. 차이는 정확히 시각 $k$ 의 갱신 보정량이다. 따라서 **(13)을 만족하는 것은
$\star = J(\hat p_{R,k+1\mid k} - \hat p_{R,k\mid k-1})$ 형태뿐**이고, 이것을 쓰면서 $H$ 와
$N$ 을 첫 추정($\hat x_{k\mid k-1}$, 랜드마크는 최초 추정)에서 평가하는 것이 **FEJ** 다.

재현 과제의 실측이 이것을 그대로 보여 준다 — 같은 데이터·같은 필터에서 $\star$ 의 표현만 바꾸면
$\lVert MN\rVert/\lVert N\rVert$ 이 $2.658\times10^{-1}$ 에서 $6.12\times10^{-16}$ 으로 떨어지고
영공간 차원이 2 에서 3 으로 돌아온다.

**가정이 깨지는 곳**: FEJ 는 야코비안을 **더 오래된** 추정에서 평가한다. 따라서 선형화 오차 자체는
**커진다** — 영공간을 지키는 대가로 1차 근사의 품질을 포기한다. 이 교환이 언제 이득인지는
문제에 달렸고, 재현 과제 Part C 가 이득이 아닌 설정을 하나 보여 준다. 또 (12)는 2D 의
$R^\top J = JR^\top$ 에 의존한다 — 3D 에서는 $R^\top\hat u \ne \hat u R^\top$ 이므로 $H$ 쪽도
선형화 지점에 민감해지고, 그래서 VIO 의 일관성 개선은 2D SLAM 보다 까다롭다
(`li2013-vio-observability`).

### R5 — 세 축은 따로 움직인다

R3·R4 가 보장하는 것은 "불관측 방향에 정보를 넣지 않는다"이다. 그것이 NEES 를 1 로 만든다는
보장은 **아니다**. 비일관성의 원인은 적어도 셋이다 — ⓐ 거짓 정보(R3), ⓑ 선형화 오차
(`c5-manifold-estimation` R4), ⓒ 잡음 모형 오설정. FEJ 는 ⓐ 를 없애면서 ⓑ 를 **키운다**.
재현 과제 Part C 에서 측정한 두 설정이 그 결과다. **[D1]**

보고할 때는 세 축을 따로 적는다: 영공간 차원과 $\lVert MN\rVert$(관측가능성·거짓 정보),
$\mathrm{ANEES}/\dim$(일관성), RMSE/ATE(정확도). 하나로 다른 둘을 주장하는 논문은 의심한다.

## 증명 스케치

### R1 — Hermann-Krener 의 랭크 조건

**가설** H1: $f$ 와 $h$ 가 해석적(analytic)이고 $\mathcal{M}$ 이 $d$ 차원 해석적 매니폴드다.
H2: $\mathcal{O}(x_0) := \mathrm{span}\{\mathrm{d}L^k_{f_{u}}h_j(x_0)\}$ 가 $x_0$ 에서 차원 $d$ 다.
**결론** C: $x_0$ 의 어떤 근방 $U$ 가 있어, $U$ 안의 모든 $x \ne x_0$ 는 $x_0$ 와 **구별 가능**하다
(국소 약관측가능성).

**전략**: 관측가능성 여분포의 원소들로 국소 좌표를 만든다 — 음함수 정리(또는 역함수 정리)
한 번이 전부다.

1. **좌표 만들기.** H2 로 $\mathcal{O}(x_0)$ 에서 $d$ 개의 선형독립 미분
   $\mathrm{d}\varphi_1,\dots,\mathrm{d}\varphi_d$ 를 고를 수 있다($\varphi_i$ 는 각각 어떤
   $L^{k}_f h_j$).
2. **역함수 정리.** $\varphi = (\varphi_1,\dots,\varphi_d) : \mathcal{M}\to\mathbb{R}^d$ 의
   야코비안이 $x_0$ 에서 가역이므로, $x_0$ 의 근방에서 $\varphi$ 가 미분동형이다. 즉
   $\varphi(x)$ 가 $x$ 를 **국소적으로 결정**한다.
3. **$\varphi$ 는 측정에서 계산된다.** $L^k_f h_j$ 는 입력 $u$ 를 고정한 궤적 위에서 측정
   $z(t) = h(x(t))$ 의 $k$ 차 시간 미분으로 얻어진다. 따라서 $\varphi(x_0)$ 는 측정의 함수다.
4. **결론.** 두 초기 상태가 같은 측정 궤적을 주면 $\varphi$ 값이 같고, 2단계로 국소적으로 같은
   점이다. 대우를 취하면 C.
5. **역방향의 미묘함.** 랭크 조건은 **충분**조건이다. 랭크가 모자라도 유한 시간에 구별될 수
   있다(예: 비해석적 계, 또는 입력 전환으로만 드러나는 구조). 다만 해석적 계에서는 랭크 조건이
   **일반적인(generic)** 점에서 필요조건이기도 하다 — 이것이 실무에서 랭크 결손을 "불관측"으로
   읽어도 되는 근거다.

**가설을 지우면**: H1 의 해석성을 $C^\infty$ 로 약화하면 5단계의 필요조건 방향이 깨진다
(평평한 함수로 만든 반례가 있다). H2 가 $x_0$ 에서만 성립하고 근방에서 랭크가 떨어지면
"국소 약관측가능"의 **균일한** 근방을 얻지 못한다.

(생략: 관측가능성 여분포가 입력에 대해 생성되는 과정과 $\mathcal{O}$ 의 involutivity 논의.
`hermann1977-observability` 정리 3.1 과 그 보조정리들.)

### R2 — 생성원 4개가 영공간을 정확히 span 한다

**가설** H1: 측정이 동체 자이로·가속도계와 단안 베어링뿐이다. H2: $g$ 가 상수이고 크기·방향이
고정이다. H3: 가속도계 바이어스가 상태에 없다. H4: 운동이 퇴화하지 않았다(R2' 의 반대).
**결론** C1: (2)의 변환군은 모든 측정을 보존한다. C2: 그 생성원 (6)(7)이 선형화된 계의 영공간을
**정확히** span 한다(차원 4).

**전략**: 포함 관계를 양쪽에서 보인다. $\subseteq$ 는 불변성 계산(유도 R2), $\supseteq$ 는
랭크 계산.

1. **$\mathrm{span}\{n_e, n_\psi\} \subseteq \ker M$.** 군이 측정을 보존하므로(C1, 식 (4)(5))
   잔차가 군 방향으로 1차 변화가 없다. 즉 $M\,n = 0$. 이 단계는 **수치 없이** 끝난다.
2. **$\dim\mathrm{span}\{n_e, n_\psi\} = 4$.** (6)의 세 벡터는 평행이동 방향이 선형독립이고,
   (7)은 $\delta\phi_k = R_k^\top u_g \ne 0$ 성분을 가지므로 (6)의 span 에 들어가지 않는다.
3. **$\ker M \subseteq \mathrm{span}\{\cdot\}$ 는 랭크로만 보인다.** 이 포함은 **운동에
   의존**하므로 해석적으로 일반 증명이 없다. H4 아래에서 수치 랭크가 $N - 4$ 임을 확인하는 것이
   표준 절차이고, 재현 과제 Part A 가 그것이다(특잇값 간격 $1.3\times10^{-3}$ 대
   $7.4\times10^{-11}$).
4. **H4 가 깨지면.** 3단계의 포함이 깨져 $\ker M$ 이 커진다. 재현 과제가 등가속 궤적에서
   차원 5 를 측정하고, 그 다섯 번째 방향의 정체는 `c5-imu-preintegration` R4 의 척도·중력 족이다
   (문제 P6 에서 확인한다).

**가설을 지우면**: H2 에서 중력 **방향**을 미지로 두면(초기화 단계) 롤·피치 2 차원이 추가되고,
H3 를 지우면 바이어스와 결합한 퇴화가 생긴다. H1 에서 거리 측정 하나를 더하면 척도가 관측되지만
(2)의 4차원은 그대로 남는다 — **거리 센서는 구조적 불관측성을 고치지 않는다.**

(생략: 3단계의 포함을 특정 운동 부류에 대해 해석적으로 보이는 작업. `li2013-vio-observability`
3절과 `hesch2014` 가 운동 부류별로 정리해 두었다.)

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (증명, ★★, R2)** (4)와 (5)를 빠진 줄 없이 다시 쓰고, 다음을 보여라: ⓐ 중력축이 **아닌**
회전 $R_\chi$ 에서 (4)가 깨지는 지점을 정확히 지적하고, ⓑ 그로부터 롤·피치는 관측되지만 요는
관측되지 않는다는 결론을 쓰고, ⓒ 거리 측정(스테레오 기선 또는 LiDAR)을 하나 추가하면 (2)의
어느 부분이 남고 어느 부분이 사라지는지 쓰라.
*전략 + 핵심 부등식*: ⓐ 는 $R_\chi^\top g = g$ 가 $\chi \parallel g$ 일 때만 성립한다는 한 줄이다.
ⓒ 는 (5)의 분모가 사라지는 것이 핵심 — 거리 측정은 $\lVert p_f - p_k\rVert$ 를 고정하므로
척도를 결정하지만 $R_\psi$ 와 $t$ 는 여전히 노름을 보존한다. **"거리 센서를 달면 다 관측된다"는
흔한 오해를 반박하는 것이 이 문제의 목적이다.** 전개는 숨긴다.

**P2 (증명, ★★★, R1)** Hermann-Krener 랭크 조건의 ⓐ 충분성 논증을 본문 1-4 단계대로 쓰고,
ⓑ 랭크가 모자라지만 구별 가능한 계의 반례를 하나 구성하라. ⓒ 왜 해석성(analyticity)이
필요조건 방향에 쓰이는지 한 문단으로 쓰라.
*전략*: ⓑ 는 $C^\infty$ 지만 해석적이지 않은 평평한 함수(예: $x < 0$ 에서 0, $x>0$ 에서
$e^{-1/x}$)를 측정 함수에 넣으면 모든 Lie 미분이 원점에서 0 이지만 $x$ 를 구별할 수 있다는
구성을 쓴다. ⓒ 는 해석적 함수가 한 점의 모든 도함수로 결정된다는 사실을 쓰면 통과. 전개는 숨긴다.

**P3 (유도, ★★, R4)** (12)와 (13)을 빠진 줄 없이 유도하고, ⓐ (12)가 왜 선형화 지점에 둔감한지와
ⓑ (13)이 왜 민감한지의 차이를 한 문장으로 요약하라. ⓒ 3D 로 옮기면 (12)의 논증이 어디서
깨지는지 지적하라.
*해답 스케치*: ⓐ·ⓑ 의 차이는 "$H$ 의 영공간 조건은 **한 시각 안의** 항등식이고 $\Phi$ 의 조건은
**두 시각을 잇는** 항등식"이라는 것이다. 후자만 추정값의 시간적 불일치에 걸린다. ⓒ 는
$R^\top\hat u = \widehat{R^\top u}R^\top$ 형태의 교환 관계가 3D 에서는 축을 회전시킨다는 점
($\mathrm{Ad}$)을 쓰면 통과.

**P4 (계산, ★, R2·R2')** 재현 과제의 VIO 문제에서 ⓐ 수치 랭크와 영공간 차원, ⓑ 랭크 경계
전후의 특잇값, ⓒ 해석적 생성원 4개의 $\lVert Mn\rVert/\lVert n\rVert$, ⓓ 등가속 궤적으로 바꿨을
때의 영공간 차원을 구하라.
*정답*: ⓐ $N = 45$, 행 63, 랭크 **41**, 영공간 **4**. ⓑ $\sigma_{41} = 1.325\times10^{-3}$,
$\sigma_{42} = 7.368\times10^{-11}$ (8자리 간격). ⓒ 네 값 모두 $< 10^{-10}$
(참조 $6.87, 4.63, 5.48, 8.40 \times10^{-11}$ — 중앙 차분의 잡음 수준). ⓓ 랭크 40, 영공간 **5**
($\sigma_{40} = 2.336\times10^{-2}$, $\sigma_{41} = 1.119\times10^{-10}$). 허용오차: 랭크·차원은
정확히, 특잇값은 상대오차 10% 이내(중앙 차분 스텝에 의존).

**P5 (구현, ★★★, R3·R4)** 2D EKF-SLAM 을 세 변형으로 구현하라 — 이상(참값 야코비안), 표준 EKF,
FEJ. 세 경우의 $M$ 을 쌓아 영공간 차원과 $\lVert MN\rVert/\lVert N\rVert$ 를 보고한다.
*루브릭*: ⓐ 세 경우의 영공간 차원이 3 / 2 / 3 이고 $\lVert MN\rVert/\lVert N\rVert$ 가
$10^{-15}$ / $10^{-1}$ / $10^{-15}$ 규모 ⓑ FEJ 의 $N$ 을 **첫 추정**에서, 이상의 $N$ 을
**참값**에서 평가했다(섞으면 즉시 반송) ⓒ (3)의 두 표현을 **둘 다** 구현해 바꿔 끼울 수 있게
했고, 표현만 바꿨을 때의 변화를 보고했다 ⓓ $H$ 를 첫 추정으로 바꾸는 것만으로는 부족하다는 것을
수치로 보였다(Φ 표현을 고치지 않으면 영공간이 복원되지 않는다).

**P6 (반례, ★★, R2'·R5)** ⓐ 재현 과제의 등가속 궤적에서 늘어난 다섯 번째 불관측 방향이
`c5-imu-preintegration` R4 의 척도·중력 족과 같은 것임을 수치로 확인하라(영공간 기저에서
해석적 생성원 4개를 사영해 없앤 뒤 남는 방향을 그 족의 생성원과 비교한다).
ⓑ "영공간을 보존하면 일관성이 좋아진다"가 거짓임을 재현 과제 Part C 의 두 설정으로 보이고,
ⓒ 그 이유를 R5 의 세 원인으로 설명하라.
*성질 체크리스트*: ⓐ 는 척도 방향의 생성원이 $(0,\ v_k,\ p_k,\ p_{f_i})$ 에 중력축이 아닌
회전 성분이 섞인 형태라는 점을 쓴다 — 정확히 일치하지 않으면 **왜 섞이는지**(중력이 고정된
좌표계에서는 척도 변화가 기울기 변화와 결합한다) 쓰는 것이 ⓐ 의 통과 조건이다.
ⓑ 는 수치를 그대로 인용하면 되고, ⓒ 가 핵심 — FEJ 가 거짓 정보를 없애는 대신 선형화 오차를
키운다는 교환을 지적해야 통과. "경우에 따라 다르다"만 쓰면 미달.

**P7 (논문, ★★, R3·R4)** `huang2010-fej` 3-5절을 읽고 ⓐ 저자들의 FEJ 가 본문 (13)과 같은
교정을 하는지 식 번호로 확인하고, ⓑ 저자들이 보장하는 것과 보장하지 않는 것을 각각 두 줄로
구분하고, ⓒ 저자들의 NEES 실험 설정 중 재현 과제 Part C 와 다른 점 3개를 찾아 그 차이가
결과 방향을 바꿀 수 있는지 논하라.
*루브릭*: ⓐ 는 "전이 야코비안의 해당 블록을 위치 추정의 차로 쓴다"를 짚으면 통과.
ⓑ 는 "영공간 보존은 보장, NEES = dim 은 보장 아님" 을 구분하면 통과. ⓒ 는 궤적 길이, 센서
가시 범위, 랜드마크 수·초기 불확실성, 몬테카를로 횟수 중 셋을 들고 **어느 쪽으로** 바꿀지를
쓰면 우수.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Huang, Mourikis & Roumeliotis, "Observability-based rules for designing consistent EKF SLAM
   estimators" (2010, IJRR)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1177/0278364909353640> (3-5절)
   추가 질문: ⓐ 저자들의 "spurious information"을 본문의 $\lVert MN\rVert/\lVert N\rVert$ 로
   정량화할 수 있는가? ⓑ FEJ 와 OC-EKF 의 차이가 본문 (13)의 어느 선택에 해당하는가?
2. **Li & Mourikis, "High-precision, consistent EKF-based visual-inertial odometry" (2013, IJRR)**
   — 역할: `표준(standard)`. <https://doi.org/10.1177/0278364913481251> (3-4절)
   추가 질문: ⓐ 저자들이 세는 불관측 차원이 본문 R2 의 4 와 같은가, 상태 정의가 다르면 어떻게
   달라지는가? ⓑ 3D 에서 $H$ 쪽도 선형화 지점에 민감해지는 문제를 저자들이 어떻게 처리하는가?
3. **Hermann & Krener, "Nonlinear controllability and observability" (1977, IEEE T-AC)** —
   역할: `원전(seminal)`. <https://doi.org/10.1109/TAC.1977.1101601> (정리 3.1 주변)
   추가 질문: ⓐ "locally weakly observable"의 네 가지 변종(observable, locally observable,
   weakly observable, locally weakly observable)을 한 문장씩으로 구별해 쓰라. ⓑ 로보틱스
   논문들이 이 중 어느 것을 쓰면서 어느 것으로 말하는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어. Part A·B 는 각 5초 이내,
Part C 의 몬테카를로는 5분 이내. 메모리 300MB 이하. numpy 만 쓴다.

**입력 데이터**는 아래 두 생성기가 만든다(결정론적·고정 시드). 외부 데이터셋이 필요 없다.

**Part A — VIO 영공간.** 아래 생성기가 참 상태와 잡음 없는 측정을 만든다. 잔차 함수를 중앙
차분으로 미분해 $M$ 을 만들고, 특잇값으로 수치 랭크를 재고, 해석적 생성원 (6)(7)이 영공간에
있는지 확인한다. 그 다음 `const_acc=True` 로 바꿔 영공간 차원이 어떻게 되는지 본다.

```python
"""c5-observability-consistency Part A: VIO 잔차와 해석적 영공간 생성원."""

import numpy as np

G = np.array([0.0, 0.0, -9.81])
K, L, DTK = 4, 3, 0.5
LANDMARKS = np.array([[4.0, 1.0, 2.0], [-2.0, 3.0, 0.5], [1.0, -5.0, 3.0]])


def skew(w):
    return np.array([[0.0, -w[2], w[1]], [w[2], 0.0, -w[0]], [-w[1], w[0], 0.0]])


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


def truth(const_acc=False):
    """참 자세·속도·위치. const_acc=True 면 세계 프레임 가속도가 상수인 궤적이다."""
    Rs, vs, ps = [], [], []
    for k in range(K):
        t = k * DTK
        Rs.append(exp_so3(np.array([0.1 * t, -0.2 * t, 0.6 * t + 0.3])))
        vs.append(np.array([1.0 + 0.2 * t, 0.3 * t, 0.1 * np.sin(t)]))
        if const_acc:
            ps.append(np.array([0.5 * t + 0.4 * t**2, 0.2 * t**2, 0.1 * t]))
        else:
            ps.append(
                np.array(
                    [
                        0.5 * t + 0.4 * t**2 + 0.3 * np.sin(2 * t),
                        0.2 * t**2,
                        0.1 * t + 0.2 * np.cos(t),
                    ]
                )
            )
    return Rs, vs, ps


def measurements(Rs, vs, ps):
    """잡음 없는 선적분 측정과 베어링 (참 상태에서 잔차가 0 이 되도록)."""
    dRb = [Rs[k].T @ Rs[k + 1] for k in range(K - 1)]
    dvb = [Rs[k].T @ (vs[k + 1] - vs[k] - G * DTK) for k in range(K - 1)]
    dpb = [Rs[k].T @ (ps[k + 1] - ps[k] - vs[k] * DTK - 0.5 * G * DTK**2) for k in range(K - 1)]
    bear = []
    for k in range(K):
        for i in range(L):
            d = Rs[k].T @ (LANDMARKS[i] - ps[k])
            bear.append(d / np.linalg.norm(d))
    return dRb, dvb, dpb, bear
```

상태 벡터의 배치는 $x = (\delta\phi_0..\delta\phi_{K-1},\ v_0..v_{K-1},\ p_0..p_{K-1},\
p_{f_0}..p_{f_{L-1}}) \in \mathbb{R}^{45}$ 이고 자세는 우 섭동
$R_k \leftarrow \bar R_k\exp(\delta\phi_k)$ 로 매개화한다. 잔차는
$\mathrm{Log}(\bar{\Delta R}_k^\top R_k^\top R_{k+1})$,
$R_k^\top(v_{k+1}-v_k-g\Delta t) - \bar{\Delta v}_k$,
$R_k^\top(p_{k+1}-p_k-v_k\Delta t-\tfrac12 g\Delta t^2) - \bar{\Delta p}_k$,
그리고 베어링 잔차 $\widehat{R_k^\top(p_{f_i}-p_k)} - \bar b$ 다(총 63행).
중앙 차분 스텝은 $10^{-6}$, 랭크 임계값은 $\sigma_1\cdot10^{-8}$ 을 쓴다.

**Part B·C — 2D EKF-SLAM 과 FEJ.** 아래 생성기를 쓴다.

```python
"""c5-observability-consistency Part B/C: 2D EKF-SLAM 시뮬레이터."""

import numpy as np

JM = np.array([[0.0, -1.0], [1.0, 0.0]])
SEED = 20261112
STEPS, L2 = 30, 4
SIG_U, SIG_W, SIG_Z = 0.03, 0.01, 0.05
U_ODO = np.array([0.2, 0.0])
OMEGA = 0.12
LM2 = np.array([[3.0, 1.0], [-1.0, 3.5], [2.0, -2.5], [-3.0, -1.0]])
LM_OFFSET = np.array([0.15, -0.10])
N_DIM = 3 + 2 * L2


def rot2(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]])


def simulate2(seed):
    """참 궤적, 오도메트리 측정, 랜드마크 관측."""
    rng = np.random.default_rng(seed)
    p, th = np.zeros(2), 0.0
    tr, odo, obs = [(p.copy(), th)], [], []
    for _ in range(STEPS):
        u = U_ODO + rng.normal(scale=SIG_U, size=2)
        w = OMEGA + rng.normal(scale=SIG_W)
        p = p + rot2(th) @ u
        th = th + w
        tr.append((p.copy(), th))
        odo.append((u, w))
        obs.append([rot2(th).T @ (pl - p) + rng.normal(scale=SIG_Z, size=2) for pl in LM2])
    return tr, odo, obs


def h_block(theta, p, pf, i):
    """측정 야코비안 (10)."""
    H = np.zeros((2, N_DIM))
    Rt = rot2(theta).T
    H[:, :2] = -Rt
    H[:, 2] = -JM @ Rt @ (pf - p)
    H[:, 3 + 2 * i : 5 + 2 * i] = Rt
    return H


def null_basis(p_robot, lms):
    """영공간 기저 (11): 전역 평행이동 2 + 전역 회전 1."""
    N = np.zeros((N_DIM, 3))
    N[:2, :2] = np.eye(2)
    N[:2, 2] = JM @ p_robot
    N[2, 2] = 1.0
    for i in range(len(lms)):
        N[3 + 2 * i : 5 + 2 * i, :2] = np.eye(2)
        N[3 + 2 * i : 5 + 2 * i, 2] = JM @ lms[i]
    return N
```

**해야 할 일.** 초기 상태는 로봇 포즈가 참값(공분산 $10^{-6}I_3$), 랜드마크가
`LM2 + LM_OFFSET`(공분산 $0.3^2 I$)이다. 세 변형을 구현한다.

| 변형 | $H$ 평가 지점 | $\Phi$ 의 $(1,3)$ 블록 | $N$ 평가 지점 |
|---|---|---|---|
| 이상(ideal) | 참 상태 | $J R(\theta_k)u_k$, 참값 | 참 상태 |
| 표준 EKF | 현재 추정 $\hat x_{k\mid k}$ | $J R(\hat\theta_{k\mid k})u_k$ | 참 상태 |
| FEJ | 첫 추정 $\hat x_{k\mid k-1}$, 랜드마크는 최초 추정 | $J(\hat p_{k+1\mid k} - \hat p_{k\mid k-1})$ | 첫 추정 |

$M$ 은 (8)대로 쌓는다(각 시각의 $L_2$ 개 측정 × 2행, 총 240행). 랭크 임계값은
$\sigma_1\cdot10^{-10}$.

**Part C — NEES.** 위 설정(설정 1)에서 표준 EKF 와 FEJ 의 $\mathrm{ANEES}/\dim$ 을 500회
몬테카를로로(시드 $\mathrm{SEED}+m$) 측정한다. 그 다음 **설정 2** 로 바꿔 다시 측정한다 —
$\mathrm{STEPS} = 300$, $u = (0.15, 0)$, $\omega = 0.05$, $\sigma_u = 0.03$,
$\sigma_w = 0.03$, $\sigma_z = 0.08$, 센싱 반경 $3.0$(그 안의 랜드마크만 관측), 랜드마크
`np.random.default_rng(11).uniform(-6.0, 6.0, (25, 2))`, 랜드마크 초기 추정은 참값 + 표준편차
$0.5$ 의 가우시안(공분산 $0.5^2 I$), 로봇 포즈 사전분포 $10^{-6}I_3$, 200회.

**수용 기준 — 네 조건을 모두 만족해야 통과다.**

1. **Part A (varying acceleration)** — 랭크 **41**, 영공간 차원 **4**(정확히),
   $\sigma_{41} = 1.325\times10^{-3}$ 와 $\sigma_{42} = 7.368\times10^{-11}$ (상대오차 10% 이내 —
   중앙 차분 스텝에 의존), 그리고 해석적 생성원 4개 전부
   $\lVert Mn\rVert/\lVert n\rVert < 10^{-9}$ (참조 $6.9, 4.6, 5.5, 8.4\times10^{-11}$).
2. **Part A (constant acceleration)** — 같은 코드에서 `const_acc=True` 로 랭크 **40**,
   영공간 차원 **5**($\sigma_{40} = 2.336\times10^{-2}$, $\sigma_{41} = 1.119\times10^{-10}$).
   네 생성원은 여전히 영공간에 있다. **운동이 구조적 불관측성에 방향을 더한다**는 것이 요점이다.
3. **Part B** — 아래 표를 재현한다(영공간 차원은 정확히, 노름은 자리수만).

   | 변형 | 행 | 랭크 | 영공간 차원 | $\lVert MN\rVert/\lVert N\rVert$ |
   |---|---|---|---|---|
   | 이상 | 240 | 8 | 3 | $6.07\times10^{-16}$ |
   | 표준 EKF | 240 | 9 | 2 | $2.658\times10^{-1}$ |
   | FEJ | 240 | 8 | 3 | $6.12\times10^{-16}$ |

   추가로, FEJ 에서 $\Phi$ 의 $(1,3)$ 블록만 $JR(\hat\theta_{k\mid k-1})u_k$ 로 되돌리면
   영공간이 **복원되지 않음**을 보고한다(참조 구현 $\lVert MN\rVert/\lVert N\rVert
   = 4.3\times10^{-2}$, 영공간 차원 2) — **$H$ 를 첫 추정으로 바꾸는 것만으로는 부족하다.**
4. **Part C** — 두 설정의 $\mathrm{ANEES}/\dim$ 을 보고한다. 참조 구현:
   설정 1(30스텝·전수 관측·500회)에서 표준 $0.738$ / FEJ $0.738$ (**구별되지 않음**),
   설정 2(300스텝·거리 제한·200회)에서 표준 $0.915$ / FEJ $1.265$ (**FEJ 가 더 과신**).
   위치 RMSE 는 각각 $0.0438$ / $0.0434$ m 와 $0.1409$ / $0.1543$ m 다 — 설정 2 에서는 FEJ 가
   정확도까지 나쁘다. 허용오차 $\pm0.05$(ANEES), $\pm0.01$ m.
   **이 Part 의 통과 조건은 "FEJ 가 더 좋다"를 재현하는 것이 아니라, 세 축(거짓 정보·일관성·
   정확도)이 따로 움직인다는 것을 수치로 보고하고 R5 의 세 원인으로 설명하는 것이다.**

**비교 대상**: ⓐ Part A·B 의 베이스라인은 "이상 야코비안" 변형이다(같은 데이터, 참값 선형화).
ⓑ Part B 의 두 번째 베이스라인은 $\Phi$ 표현만 바꾼 FEJ 변형(조건 3의 추가 보고).
ⓒ Part C 의 베이스라인은 표준 EKF. 선택: 랜드마크 초기 불확실성을 $0.3 \to 0.05$ 로 줄여
Part B 의 표준 EKF 값이 어떻게 변하는지 본다(거짓 정보는 추정 오차와 함께 줄어든다).

**보고할 수치**: 위 네 조건의 모든 값, 그리고 Part A 의 두 경우에서 영공간 기저로부터 해석적
생성원 4개를 사영해 없앤 뒤 남는 성분의 크기(varying 에서는 잡음 수준, constant 에서는 $O(1)$ —
문제 P6 의 출발점).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| Part A 영공간이 0 또는 1 | 앵커·사전분포 인자를 넣었다 — 그러면 게이지가 고정되어 영공간이 사라진다 | 잔차에 절대 측정이 없는지 확인한다(IMU 와 베어링만) |
| Part A 영공간이 4보다 크고 생성원은 맞다 | 랜드마크·키프레임이 부족하거나 운동이 퇴화했다 | $K$ 를 5-6, $L$ 을 6-8 로 늘려 4 로 돌아오는지 본다 |
| Part A 생성원의 $\lVert Mn\rVert$ 이 $10^{-6}$ 규모 | 중앙 차분 스텝이 너무 작거나 커서 절단·반올림 오차 | 스텝을 $10^{-4}\!\sim\!10^{-7}$ 로 쓸어 가며 최소를 찾는다 |
| Part A 요 생성원만 영공간에 없다 | (7)의 $\delta\phi_k$ 에 $u_g$ 를 그냥 넣었다(좌 섭동 좌표) | 우 섭동 규약이면 $R_k^\top u_g$ 여야 한다 |
| Part B 이상 변형도 영공간 3 이 안 나온다 | $N$ 을 랜드마크 **추정**에서 평가했다 | 이상 변형의 $N$ 은 참값에서 평가한다 |
| Part B FEJ 가 표준과 같다 | $\Phi$ 의 $(1,3)$ 블록을 고치지 않았다 | 조건 3의 추가 보고를 먼저 재현해 본다 |
| Part B 랭크가 변형마다 들쭉날쭉 | 임계값이 너무 느슨하다 | 특잇값을 로그로 출력해 간격이 어디인지 눈으로 확인한다 |
| Part C ANEES 가 $10^2$ 규모 | 각도 오차를 랩핑하지 않았다 | $\mathrm{atan2}(\sin\delta,\cos\delta)$ 를 쓰는지 확인한다 |

## 열린 문제

- **(열린 문제) 영공간 보존과 일관성 사이의 정량적 연결** — R3·R4 는 거짓 정보를 없애는 방법을
  주지만, 그것이 NEES 를 얼마나 개선하는지에 대한 정량적 진술이 없다. 재현 과제 Part C 가 개선이
  없는(또는 역전되는) 설정을 보여 준다. 현재 접근은 설정별 실험 보고
  ([Huang et al.](https://doi.org/10.1177/0278364909353640),
  [Li & Mourikis](https://doi.org/10.1177/0278364913481251))와 불변 필터처럼 선형화 오차 자체를
  줄이는 설계([InEKF](https://arxiv.org/abs/1410.1465))다. 비어 있는 자리:
  $\lVert MN\rVert$ 같은 거짓 정보 척도에서 $\mathbb{E}[\mathrm{NEES}]$ 로 가는 상계.
- **(열린 문제) 퇴화 운동을 온라인으로 탐지하기** — R2' 는 운동이 영공간을 키운다는 것을
  보이지만, 실제로 필요한 것은 "지금 이 구간의 운동이 퇴화에 얼마나 가까운가"를 실시간으로
  재는 것이다. $M$ 의 최소 특잇값은 척도 의존적이고 상태 단위에 민감해 임계값을 정하기 어렵다.
  현재 접근: 운동 부류별 퇴화 목록([Hesch et al.](https://doi.org/10.1177/0278364913509675))과
  조건수 휴리스틱. 비어 있는 자리: 단위에 불변인 퇴화 지표와 그에 대한 판정 보증.
- **(열린 문제) 학습 기반 프런트엔드가 들어온 계의 관측가능성** — R1·R2 는 측정 모형이
  해석적으로 주어진 경우의 분석이다. 측정이 신경망의 출력(학습된 상대 포즈, 깊이, 특징 매칭
  점수)이면 Lie 미분을 쓸 수 없고 불변군도 보장되지 않는다. 현재 접근: 학습 출력을 "가상 측정"
  으로 보고 공분산을 붙이는 것, 그리고
  [장기 SLAM 서베이](https://arxiv.org/abs/1606.05830) III-IV 절의 논의. 비어 있는 자리:
  학습된 측정 모형에 대해 불관측 방향을 **정의하고 측정하는** 방법.

## 개념 점검

`rc quiz c5-observability-consistency` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c5-observability-consistency-quiz
questions:
  - id: q1
    type: single
    prompt: "단안 관성-시각 추정에서 요(yaw)는 불관측인데 롤·피치는 관측되는 이유는?"
    choices:
      - "요가 적분 오차를 더 많이 받기 때문"
      - "중력축 회전만 $R_\\psi^\\top g = g$ 를 만족해 가속도계 측정을 바꾸지 않기 때문"
      - "카메라가 요 방향 변화에 둔감하기 때문"
      - "자이로가 요 축에서 바이어스가 크기 때문"
    answer: 1
    explanation: "(4)의 한 줄이다 — $R_k'^\\top(a_k' - g) = R_k^\\top(a_k - R_\\psi^\\top g)$ 이고 중력축 회전에서만 $R_\\psi^\\top g = g$ 다. 중력축이 아닌 회전은 이 등식을 깨뜨리므로 가속도계가 롤·피치를 관측한다. 센서 품질이나 적분 오차와는 무관한 **구조적** 성질이다."
    concept: { front: "VIO 에서 요만 불관측인 이유", back: "$R_\\psi^\\top g = g$ — 중력축 회전만 가속도계 측정을 보존한다. 구조적 성질이며 센서 품질과 무관" }
  - id: q2
    type: single
    prompt: "단안 VIO 에 거리 측정(스테레오 또는 LiDAR)을 추가하면 불관측 부분공간은?"
    choices:
      - "완전히 사라진다"
      - "4차원에서 3차원으로 줄어든다"
      - "전역 평행이동 3 + 중력축 요 1 = 4차원이 그대로 남는다"
      - "오히려 커진다"
    answer: 2
    explanation: "거리 측정은 (5)의 분모를 고정해 **척도**를 결정하지만, (2)의 $R_\\psi$ 와 $t$ 는 거리도 보존한다. 따라서 4차원 구조적 불관측성은 그대로다 — 절대 위치·방위를 주는 측정(GPS, 알려진 지도, 앵커 인자)이 들어와야 사라진다."
    concept: { front: "거리 센서와 구조적 불관측성", back: "척도는 관측되지만 전역 평행이동 3 + 요 1 = 4차원은 그대로. 절대 측정만이 그것을 없앤다" }
  - id: q3
    type: truefalse
    prompt: "EKF 의 비일관성은 측정 야코비안 $H$ 를 첫 추정에서 평가하는 것만으로 고쳐진다."
    answer: false
    explanation: "2D SLAM 에서 $H_kN_k = 0$ 은 $R^\\top J = JR^\\top$ 덕분에 선형화 지점과 무관하게 성립한다((12)). 깨지는 것은 $\\Phi_kN_k = N_{k+1}$ 이고, 그것을 고치려면 전이 야코비안의 블록을 $J(\\hat p_{k+1|k} - \\hat p_{k|k-1})$ 형태로 써야 한다. 재현 과제에서 $H$ 만 바꾸면 $\\lVert MN\\rVert/\\lVert N\\rVert$ 이 $4.3\\times10^{-2}$ 에 머문다."
    concept: { front: "FEJ 에서 실제로 고쳐야 하는 것", back: "$\\Phi$ 의 $(1,3)$ 블록을 $J(\\hat p_{k+1|k}-\\hat p_{k|k-1})$ 로. $H$ 만 바꾸면 영공간이 복원되지 않는다" }
  - id: q4
    type: single
    prompt: "참 계에서 대수적으로 동일한 두 야코비안 표현 $JR(\\theta_k)u_k$ 와 $J(p_{k+1}-p_k)$ 가 EKF 에서 다른 결과를 주는 이유는?"
    choices:
      - "부동소수점 오차가 다르게 누적되기 때문"
      - "추정값을 넣으면 두 식이 다른 값이 되고, 영공간 전파 조건 (13)을 만족하는 것은 한쪽뿐이기 때문"
      - "하나는 1차, 다른 하나는 2차 근사이기 때문"
      - "$u_k$ 에 잡음이 있기 때문"
    answer: 1
    explanation: "$p_{k+1} = p_k + R(\\theta_k)u_k$ 는 **참값에서만** 성립한다. $\\hat p_{k+1|k}$ 는 갱신 후 추정에서 전파되고 $R(\\hat\\theta_{k|k-1})u_k$ 는 전파 전 방위를 쓰므로 둘의 차가 갱신 보정량만큼 난다. (13)을 만족하는 것은 위치 차 형태뿐이다."
    concept: { front: "대수적 동일성 ≠ 수치적 동일성", back: "참값에서 같은 두 표현이 추정값에서는 다르다. 영공간 전파 조건을 만족하는 표현을 **골라야** 한다" }
  - id: q5
    type: single
    prompt: "어떤 필터의 영공간이 정확히 보존되고 $\\lVert MN\\rVert$ 이 기계 정밀도라면?"
    choices:
      - "그 필터는 일관적이다 ($\\mathbb{E}[\\mathrm{NEES}] = \\dim$)"
      - "불관측 방향에 거짓 정보를 넣지 않았다는 뜻이고, 일관성은 따로 측정해야 한다"
      - "그 필터는 최적이다"
      - "추정 오차가 최소다"
    answer: 1
    explanation: "영공간 보존은 비일관성의 **한 가지** 원인(거짓 정보)을 제거한다. 남는 원인은 선형화 오차와 잡음 모형 오설정이다. 재현 과제 Part C 가 FEJ 가 영공간을 완벽히 보존하면서도 표준 EKF 보다 ANEES 가 나쁜 설정(1.265 대 0.915)을 보여 준다."
    concept: { front: "영공간 보존이 보장하는 것", back: "거짓 정보 없음. 일관성·정확도는 별개 축이며 따로 측정해 보고해야 한다" }
```

## 이 단계 공부법

1. **불변군을 먼저 손으로 확인한다 (45분)** — (4)와 (5)를 종이에 쓰고 $R_\psi^\top g = g$ 를
   쓰는 지점에 표시한다. 그 다음 중력축이 아닌 회전을 넣어 (4)가 깨지는 것을 직접 본다.
   이 레슨의 R2 는 이 두 줄이 전부다.
2. **생성원을 직접 쓴다 (30분)** — (6)(7)을 백지에서 재구성한다. 특히 (7)의 $R_k^\top u_g$ 가
   우 섭동 규약에서 나오는 것을 `c5-manifold-estimation` R2 와 대조해 확인한다.
   규약을 틀리면 재현 과제 Part A 의 요 생성원만 틀린다.
3. **Part A 를 먼저 돌린다 (60분)** — 특잇값을 로그 축으로 그려 8자리 간격을 눈으로 본다.
   그 다음 `const_acc=True` 로 바꿔 차원이 5 가 되는 것을 보고, 늘어난 방향이 무엇인지 P6 로
   추적한다. `c5-imu-preintegration` R4 와 연결되는 순간이 이 레슨의 가장 좋은 지점이다.
4. **(12)(13)을 종이에서 (60분)** — 둘의 차이("한 시각 안의 항등식" 대 "두 시각을 잇는 항등식")를
   한 문장으로 쓸 수 있으면 FEJ 를 이해한 것이다. P3 가 그 자리를 묻는다.
5. **Part B 를 세 변형으로 (90분)** — 이상 → 표준 → FEJ 순으로 구현한다. 표준에서
   $\lVert MN\rVert$ 이 $10^{-1}$ 로 뛰는 것을 보고, FEJ 에서 $\Phi$ 를 고치기 **전과 후**를
   모두 측정한다. 고치기 전 값($4.3\times10^{-2}$)이 "거의 됐는데 안 되는" 상태라는 것이
   이 레슨에서 가장 기억에 남는 숫자다.
6. **Part C 를 보고서로 쓴다 (60분)** — 두 설정의 ANEES 를 재고, **FEJ 가 더 나쁜 경우**를
   정직하게 쓴다. 세 축을 따로 적는 습관이 여기서 생긴다. 논문을 읽을 때 이 습관이 가장 많이
   쓰인다.
7. **논문은 주장과 측정을 분리해 읽는다 (150분)** — Huang et al. 3-5절에서 "영공간 보존"과
   "NEES 개선"이 각각 어디서 주장되고 어디서 측정되는지 표시하며 읽는다. Li & Mourikis 3-4절에서
   3D 로 옮길 때 추가되는 어려움을 찾고, Hermann & Krener 로 정의를 정확히 맞춘다.
   논문당 1페이지 노트는 **반드시** 쓴다.
8. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제" 세 개 중 하나를 골라 한 문단으로 쓴다.
   거짓 정보 척도에서 NEES 로 가는 상계는 재현 과제 Part C 가 바로 동기다.

**통과 기준**: 백지에서 (4)(5)와 생성원 (6)(7)을 쓸 수 있고, (12)(13)의 차이를 설명할 수 있고,
재현 과제의 네 조건을 모두 만족하는 코드를 갖고 있고, 논문 3편의 노트가 있다.
