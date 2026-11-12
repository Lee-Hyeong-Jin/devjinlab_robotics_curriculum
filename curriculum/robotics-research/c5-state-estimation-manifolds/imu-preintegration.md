---
id: c5-imu-preintegration
title: IMU 선적분과 관성 융합
summary: >-
  IMU 운동학에서 출발해 상대 운동량 세 개(ΔR, Δv, Δp)가 초기 상태와 무관하게 IMU 측정과 바이어스만의
  함수임을 증명한다. 바이어스가 바뀔 때 재적분하지 않는 1차 보정의 야코비안 재귀와 선적분 잡음의
  9차원 공분산 전파를 유도하고, 등가속 운동에서 단안 관성-시각 융합의 척도와 중력 방향이 두 개의
  정확한 해를 갖는다는 것을 유도해 수치로 확인한다.
objectives:
  - IMU 운동학을 적분해 선적분 항등식을 빠진 줄 없이 유도할 수 있다.
  - 선적분량이 초기 상태와 무관한 이유와 중력 항의 정산이 어디서 맞아떨어지는지 설명할 수 있다.
  - 바이어스 재선형화의 야코비안 재귀를 유도하고 보정 오차가 2차임을 수치로 확인할 수 있다.
  - 선적분 잡음의 공분산 전파 행렬 A, B 를 쓰고 몬테카를로로 검증할 수 있다.
  - 등가속 운동에서 척도와 중력 방향의 두 번째 해를 닫힌 형태로 구할 수 있다.
  - 선적분 오차와 이산화 오차를 구분해 설명할 수 있다.
prerequisites: [c5-manifold-estimation, c5-factor-graphs-map]
difficulty: 5
estimated_minutes: 660
tags: [state-estimation, imu, preintegration, visual-inertial, observability, research]
activities:
  - id: c5-imu-preintegration-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 105
  - id: c5-imu-preintegration-papers
    kind: reading
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c5-imu-preintegration-problems
    kind: exercise
    title: 문제 세트 (증명 1 · 유도 1 · 계산 2 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: c5-imu-preintegration-reproduction
    kind: exercise
    title: 재현 과제 — 선적분 항등식, 바이어스 보정, 공분산, 척도 모호성 (R2)
    estimated_minutes: 210
  - id: c5-imu-preintegration-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.9 (Pose Estimation). 관성 융합의 교재 진입로. 전문 PDF 무료.
  - title: "Forster, Carlone, Dellaert & Scaramuzza — On-manifold preintegration (2017, T-RO)"
    url: https://arxiv.org/abs/1512.02363
    kind: article
    note: 필독 1. 역할 원전(seminal). IV-V 절과 부록(야코비안·공분산 재귀).
  - title: "Lupton & Sukkarieh — Visual-inertial-aided navigation for high-dynamic motion (2012, T-RO)"
    url: https://doi.org/10.1109/TRO.2011.2170332
    kind: article
    note: 필독 2. 역할 원전(seminal). 선적분의 최초 제안. III-IV 절.
  - title: "Martinelli — Vision and IMU data fusion: closed-form solutions for attitude, speed, absolute scale, and bias (2012, T-RO)"
    url: https://doi.org/10.1109/TRO.2011.2160468
    kind: article
    note: 필독 3. 역할 표준(standard). 척도·속도·자세의 닫힌 형태 해와 퇴화 조건.
  - title: "Qin, Li & Shen — VINS-Mono (2018)"
    url: https://arxiv.org/abs/1708.03852
    kind: article
    note: 권장. 선적분을 실제 시스템에 올린 표준 사례와 초기화 절차(V 절).
  - title: "Mourikis & Roumeliotis — A multi-state constraint Kalman filter for VIO (2007)"
    url: https://doi.org/10.1109/ROBOT.2007.364024
    kind: article
    note: 권장. 필터 쪽 접근(MSCKF)과의 대조. 선적분이 왜 평활 쪽 해법인지 보인다.
---

# IMU 선적분과 관성 융합

## 전제와 기호

`c5-manifold-estimation` 의 리 군 표기($\exp$, $\log$, $J_r$, $\mathrm{Ad}$)와
`c5-factor-graphs-map` 의 인자 그래프 표기를 그대로 쓴다. 추가 기호:

| 기호 | 뜻 |
|---|---|
| $R_t \in SO(3)$, $v_t, p_t \in \mathbb{R}^3$ | 시각 $t$ 의 자세·속도·위치. 속도와 위치는 **세계 프레임** |
| $g \in \mathbb{R}^3$ | 중력 가속도 벡터(세계 프레임). 이 레슨에서는 $(0,0,-9.81)$ |
| $\tilde\omega_k$, $\tilde a_k$ | $k$ 번째 IMU 표본의 각속도·가속도 측정(**동체 프레임**) |
| $b^g$, $b^a$ | 자이로·가속도계 바이어스(동체 프레임). 한 구간 안에서는 상수로 본다 |
| $\eta^g_k$, $\eta^a_k$ | 표본별 백색 잡음. $\eta^g_k\sim\mathcal{N}(0,\sigma_g^2 I)$, $\eta^a_k\sim\mathcal{N}(0,\sigma_a^2 I)$ |
| $\Delta t$, $n$, $\Delta t_{ij} = n\Delta t$ | IMU 표본 간격, 키프레임 $i\to j$ 사이의 표본 수, 구간 길이 |
| $\Delta R_{ij}$, $\Delta v_{ij}$, $\Delta p_{ij}$ | **선적분량**(preintegrated measurement). 정의는 (4)-(6) |
| $J^R_g$, $J^v_g$, $J^v_a$, $J^p_g$, $J^p_a$ | 선적분량의 바이어스 야코비안 |
| $\delta\xi = (\delta\phi, \delta v, \delta p) \in \mathbb{R}^9$ | 선적분 잡음의 오차 상태 |

**측정 모형**(동체 프레임, 가법 바이어스 + 백색 잡음):

$$
\tilde\omega_k = \omega_k + b^g + \eta^g_k, \qquad
\tilde a_k = R_k^\top\!\left(a_k - g\right) + b^a + \eta^a_k. \tag{1}
$$

$a_k$ 는 **세계 프레임의 가속도**이고, 가속도계가 중력을 포함해 "비중력 가속도"를 재기 때문에
$-g$ 가 들어간다. 정지한 IMU 가 위쪽으로 $9.81\,\mathrm{m/s^2}$ 를 보고하는 것이 (1)의 둘째 식이다.

**이산화 규약(중요).** 이 레슨은 다음 사각형(rectangular) 규칙을 **정의로 고정**한다:

$$
R_{k+1} = R_k\exp\!\big((\tilde\omega_k - b^g - \eta^g_k)\Delta t\big), \quad
v_{k+1} = v_k + a^w_k\Delta t, \quad
p_{k+1} = p_k + v_k\Delta t + \tfrac12 a^w_k\Delta t^2, \tag{2}
$$

$$
a^w_k := R_k(\tilde a_k - b^a - \eta^a_k) + g. \tag{3}
$$

R1 의 항등식은 **이 규약에서 정확**하다. 중간점(midpoint)이나 RK 규칙으로 바꾸면 항등식의 형태가
달라진다(문제 P1) — 그래서 구현과 논문을 대조할 때 **가장 먼저 확인할 것이 이산화 규약**이다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (선적분 항등식) [D3]** — 상대 운동량을
  $$
  \Delta R_{ij} := R_i^\top R_j, \tag{4}
  $$
  $$
  \Delta v_{ij} := R_i^\top\!\big(v_j - v_i - g\,\Delta t_{ij}\big), \tag{5}
  $$
  $$
  \Delta p_{ij} := R_i^\top\!\big(p_j - p_i - v_i\,\Delta t_{ij} - \tfrac12 g\,\Delta t_{ij}^2\big) \tag{6}
  $$
  로 정의하면, (2)(3) 아래에서 이 셋은 **IMU 측정과 바이어스만의 함수**이고 $R_i, v_i, p_i$ 에
  전혀 의존하지 않는다:
  $$
  \Delta R_{ij} = \prod_{k=i}^{j-1}\exp(\psi_k), \quad
  \Delta v_{ij} = \sum_{k} \Delta R_{ik}\,\alpha_k\,\Delta t, \quad
  \Delta p_{ij} = \sum_{k}\Big[\Delta v_{ik}\Delta t + \tfrac12 \Delta R_{ik}\,\alpha_k\Delta t^2\Big], \tag{7}
  $$
  여기서 $\psi_k := (\tilde\omega_k - b^g - \eta^g_k)\Delta t$, $\alpha_k := \tilde a_k - b^a - \eta^a_k$.
  따라서 키프레임 상태가 갱신되어도 **선적분을 다시 계산하지 않는다** — 이것이 선적분의 전부다.
- **R2 (바이어스 재선형화의 1차 보정) [D2]** — $\bar b$ 에서 계산해 둔 선적분량을 $\bar b + \delta b$
  에서 다시 쓸 때, 재적분 대신
  $$
  \Delta R_{ij}(\bar b + \delta b) \approx \Delta R_{ij}(\bar b)\exp\!\big(J^R_g\,\delta b^g\big), \quad
  \begin{aligned}
  \Delta v_{ij} &\approx \Delta v_{ij} + J^v_g\delta b^g + J^v_a\delta b^a,\\
  \Delta p_{ij} &\approx \Delta p_{ij} + J^p_g\delta b^g + J^p_a\delta b^a,
  \end{aligned} \tag{8}
  $$
  를 쓴다. 야코비안은 적분과 **같은 루프에서** 재귀로 얻어지고((11)-(15)), 보정 오차는
  $O(\lVert\delta b\rVert^2)$ 다. 재현 과제의 실측: $\lVert\delta b\rVert$ 를 $10^{-4}$ 에서
  $10^{-1}$ 로 세 자리 올릴 때 오차가 정확히 $10^6$ 배 커진다(2차 상수 $\Delta R$ 0.0094,
  $\Delta v$ 0.164, $\Delta p$ 0.0240).
- **R3 (선적분 잡음의 공분산 전파) [D2]** — 오차 상태 $\delta\xi_{ik} \in \mathbb{R}^9$ 는
  $\delta\xi_{i,k+1} = A_k\,\delta\xi_{ik} + B_k\,\eta_k$ 로 선형 전파되고
  $$
  \Sigma_{i,k+1} = A_k\Sigma_{ik}A_k^\top + B_k\Sigma_\eta B_k^\top, \qquad
  \Sigma_\eta = \mathrm{diag}(\sigma_g^2 I,\ \sigma_a^2 I), \tag{9}
  $$
  $A_k$, $B_k$ 의 명시적 형태는 (16)(17)이다. $9\times9$ 공분산을 적분 루프에서 함께 얻으므로
  인자 그래프의 IMU 인자가 바로 쓸 수 있다.
- **R4 (등가속 운동에서 척도·중력의 두 번째 해) [D2]** — 세계 프레임 가속도가 상수
  $a_t \equiv c$ 이면, 장면과 궤적을 $\lambda$ 배 하고 중력을 $g^\ast = g + (\lambda-1)c$ 로
  바꾼 해가 **같은 IMU 측정과 같은 베어링**을 만든다. 중력의 크기 $\lVert g\rVert$ 를 고정하면
  $\lambda$ 는 두 값만 허용된다:
  $$
  \lambda = 1 \qquad\text{또는}\qquad
  \lambda^\ast = 1 - \frac{2\,g^\top c}{\lVert c\rVert^2}. \tag{10}
  $$
  즉 단안 관성-시각 초기화에서 **척도와 중력 방향은 등가속 구간에서 구별되지 않는다.**
  재현 과제의 실측: $c = (0.5,-0.3,1.2)$, $g = (0,0,-9.81)$ 에서
  $\lambda^\ast = 6331/445 = 14.2269662921$ — 14배 척도 오차가 **측정과 완벽히 일치한다**.
- **R5 (선적분 오차와 이산화 오차는 다른 것이다) [D1]** — R1 은 (2)의 이산 모형에 대해 **정확한
  항등식**이다. 반면 (2) 자체는 연속 모형의 $O(\Delta t)$ 근사다. 따라서 재현 과제의 Part A 가
  $10^{-15}$ 로 맞는 것은 "선적분이 정확하다"는 뜻이고, 연속 궤적에 대한 오차는 별도로
  $\Delta t$ 를 줄여 측정해야 한다. 논문들이 보고하는 "preintegration error"가 어느 쪽인지
  반드시 확인한다.

## 유도

### R1 — 선적분량이 초기 상태를 잊는다

(2)를 $i$ 에서 $j$ 까지 펼친다. 회전은 곱이므로 바로

$$
R_j = R_i\prod_{k=i}^{j-1}\exp(\psi_k) \quad\Longrightarrow\quad
  \Delta R_{ij} = R_i^\top R_j = \prod_{k=i}^{j-1}\exp(\psi_k). \tag{7a}
$$

$R_i$ 가 소거된다. 중간 회전도 같은 방식으로 $R_k = R_i\Delta R_{ik}$ 다.

**속도.** (2)의 둘째 식을 합하면

$$
v_j - v_i = \sum_{k=i}^{j-1} a^w_k\Delta t
  = \sum_{k} \big[R_k\alpha_k + g\big]\Delta t
  = g\,\Delta t_{ij} + \sum_{k} R_i\Delta R_{ik}\,\alpha_k\,\Delta t.
$$

양변에 $R_i^\top$ 를 곱하고 $g\Delta t_{ij}$ 를 옮기면 (5)의 정의가 그대로 (7)의 둘째 식이 된다.
$R_i$ 는 $\Delta R_{ik}$ 안으로 들어가 사라지고, $v_i$ 는 정의에서 빠졌다.

**위치.** 여기가 유일하게 조심할 곳이다. (2)의 셋째 식을 합하면

$$
p_j - p_i = \sum_{k=i}^{j-1}\Big[v_k\Delta t + \tfrac12 a^w_k\Delta t^2\Big]
  = \underbrace{\sum_k v_k\Delta t}_{(\mathrm{I})}
  + \underbrace{\sum_k \tfrac12 g\Delta t^2}_{(\mathrm{II})}
  + \underbrace{\sum_k \tfrac12 R_i\Delta R_{ik}\alpha_k\Delta t^2}_{(\mathrm{III})}.
$$

(I)에 (5)를 $i\to k$ 로 쓴 $v_k = v_i + g\,\Delta t_{ik} + R_i\Delta v_{ik}$ 를 넣는다
($\Delta t_{ik} = (k-i)\Delta t$):

$$
(\mathrm{I}) = v_i\Delta t_{ij}
  + g\,\Delta t^2\sum_{k=i}^{j-1}(k-i)
  + R_i\sum_k \Delta v_{ik}\Delta t
  = v_i\Delta t_{ij} + g\,\Delta t^2\frac{n(n-1)}{2} + R_i\sum_k\Delta v_{ik}\Delta t,
$$

$(\mathrm{II}) = \tfrac12 g\,n\,\Delta t^2$. 두 중력 항을 합치면 **정확히** 맞아떨어진다:

$$
g\Delta t^2\left[\frac{n(n-1)}{2} + \frac n2\right] = g\Delta t^2\frac{n^2}{2}
  = \tfrac12 g\,\Delta t_{ij}^2. \tag{7b}
$$

따라서

$$
p_j - p_i = v_i\Delta t_{ij} + \tfrac12 g\Delta t_{ij}^2
  + R_i\sum_k\Big[\Delta v_{ik}\Delta t + \tfrac12\Delta R_{ik}\alpha_k\Delta t^2\Big],
$$

이고 양변을 (6)의 꼴로 정리하면 (7)의 셋째 식이다. $R_i, v_i, p_i$ 가 모두 좌변으로 빠졌다.

**가정이 깨지는 곳**: (7b)의 정산은 **$v$ 와 $p$ 를 같은 $a^w_k$ 로, 같은 사각형 규칙으로**
갱신했기 때문에 성립한다. 중간점 규칙($v_{k+1/2}$ 로 $p$ 를 갱신)으로 바꾸면 $\sum(k-i)$ 가
$\sum(k-i+\tfrac12)$ 로 바뀌어 (7b)가 $\tfrac12 g\Delta t_{ij}^2$ 를 **주지 않는다**. 구현이
중간점을 쓰면서 식 (6)의 정의를 그대로 쓰면 구간 길이에 비례하는 체계적 위치 편향이 생긴다 —
$\Delta t_{ij} = 0.5\,\mathrm{s}$ 에서 $\tfrac12\cdot9.81\cdot(\Delta t/2)\cdot\Delta t_{ij}$ 규모다.
또 $b^g, b^a$ 를 구간 안에서 상수로 본 것이 (7)의 전제다 — 바이어스 랜덤워크는 R3 의 잡음에
들어가지 않고 별도 인자로 모형화해야 한다.

### R2 — 바이어스 야코비안의 재귀

$\Delta R$ 부터. $\Delta R_{i,k+1} = \Delta R_{ik}\exp(\psi_k)$ 이고 $\psi_k$ 는 $b^g$ 에 대해
$\partial\psi_k/\partial b^g = -I\Delta t$ 다. $J^R_g$ 를
$\Delta R_{ik}(\bar b^g + \delta) \approx \Delta R_{ik}\exp(J^R_{g,k}\delta)$ 로 정의하면

$$
\Delta R_{i,k+1}(\bar b + \delta)
  \approx \Delta R_{ik}\exp\!\big(J^R_{g,k}\delta\big)\,
    \exp(\psi_k)\exp\!\big(-J_r(\psi_k)\Delta t\,\delta\big),
$$

여기서 둘째 지수는 $\exp(\psi_k + \partial\psi_k\delta) \approx
\exp(\psi_k)\exp(J_r(\psi_k)\partial\psi_k\delta)$ (우 야코비안의 정의,
`c5-manifold-estimation` 표기표)에서 나왔다. 가운데 두 지수의 순서를 바꾼다 —
$SO(3)$ 에서 $\exp(u)\exp(\psi) = \exp(\psi)\exp(\exp(-\psi)\,u)$ 이므로
($\mathrm{Ad}_{R} = R$):

$$
\Delta R_{i,k+1}(\bar b+\delta) \approx \Delta R_{i,k+1}
  \exp\!\Big(\big[\exp(-\psi_k)J^R_{g,k} - J_r(\psi_k)\Delta t\big]\delta\Big)
$$

$$
\Longrightarrow\quad
J^R_{g,k+1} = \Delta R_{k,k+1}^\top J^R_{g,k} - J_r(\psi_k)\,\Delta t,
  \qquad J^R_{g,i} = 0. \tag{11}
$$

$\Delta v$: (7)의 둘째 식을 $b^a$ 로 미분하면 $\alpha_k$ 가 $-\delta b^a$ 만큼 변하므로

$$
J^v_{a,k+1} = J^v_{a,k} - \Delta R_{ik}\,\Delta t. \tag{12}
$$

$b^g$ 로 미분할 때는 $\Delta R_{ik}$ 가 움직인다. $\Delta R_{ik}(\bar b+\delta)\alpha_k \approx
\Delta R_{ik}(I + \widehat{J^R_{g,k}\delta})\alpha_k = \Delta R_{ik}\alpha_k
- \Delta R_{ik}\widehat{\alpha_k}J^R_{g,k}\delta$ ($\hat x y = -\hat y x$ 를 썼다). 따라서

$$
J^v_{g,k+1} = J^v_{g,k} - \Delta R_{ik}\,\widehat{\alpha_k}\,J^R_{g,k}\,\Delta t. \tag{13}
$$

$\Delta p$ 는 (7)의 셋째 식에 같은 두 규칙을 적용한다:

$$
J^p_{a,k+1} = J^p_{a,k} + J^v_{a,k}\Delta t - \tfrac12\Delta R_{ik}\Delta t^2, \tag{14}
$$

$$
J^p_{g,k+1} = J^p_{g,k} + J^v_{g,k}\Delta t
  - \tfrac12\Delta R_{ik}\widehat{\alpha_k}J^R_{g,k}\Delta t^2. \tag{15}
$$

**순서 주의**: (14)(15)는 **갱신 전의** $J^v$ 와 $\Delta R_{ik}$ 를, (12)(13)은 갱신 전의
$\Delta R_{ik}$ 와 $J^R_{g,k}$ 를, (11)은 갱신 전의 $J^R_{g,k}$ 를 쓴다. 루프 안에서 순서를
$p \to v \to R$ 로 두어야 한다 — 이것이 구현에서 가장 흔한 버그다(진단표 참조).

**가정이 깨지는 곳**: (8)은 1차 전개이므로 오차가 $O(\lVert\delta b\rVert^2)$ 다. 재현 과제가
그 2차 계수를 직접 재는데, $\lVert\delta b^g\rVert = 0.1\ \mathrm{rad/s}$ (큰 자이로 바이어스
변화)에서 $\Delta v$ 보정 오차가 이미 $1.6\times10^{-3}\,\mathrm{m/s}$ 다. 따라서 바이어스
추정이 크게 움직이면 **재적분해야 한다** — iSAM2 의 fluid relinearization 임계값
(`c5-sparsity-isam` R3)이 여기서 실제 의미를 갖는다.

### R3 — 선적분 잡음의 공분산

오차를 $\delta\phi_{ik} := \mathrm{Log}(\Delta R_{ik}^\top\Delta\tilde R_{ik})$,
$\delta v_{ik} := \Delta\tilde v_{ik} - \Delta v_{ik}$,
$\delta p_{ik} := \Delta\tilde p_{ik} - \Delta p_{ik}$ 로 둔다(물결은 잡음이 섞인 쪽). R2 의 두
규칙($J_r$ 로 지수 안의 섭동을 빼내기, $\hat x y = -\hat y x$)을 같은 방식으로 적용하면

$$
A_k = \begin{bmatrix}
  \Delta R_{k,k+1}^\top & 0 & 0\\
  -\Delta R_{ik}\widehat{\alpha_k}\Delta t & I & 0\\
  -\tfrac12\Delta R_{ik}\widehat{\alpha_k}\Delta t^2 & I\Delta t & I
\end{bmatrix}, \qquad
B_k = \begin{bmatrix}
  J_r(\psi_k)\Delta t & 0\\
  0 & \Delta R_{ik}\Delta t\\
  0 & \tfrac12\Delta R_{ik}\Delta t^2
\end{bmatrix} \tag{16}
$$

이고 (9)로 전파한다. $A_k$ 의 첫 열이 R2 의 (13)(15)와 **같은 구조**인 것에 주목하라 —
바이어스 섭동과 잡음 섭동이 같은 경로로 전파되기 때문이다. 초기값은
$\Sigma_{ii} = 0_{9\times9}$ 다.

$$
\eta_k = \begin{bmatrix}\eta^g_k\\ \eta^a_k\end{bmatrix}
  \sim \mathcal{N}\!\left(0, \Sigma_\eta\right),
  \qquad \Sigma_\eta = \mathrm{diag}(\sigma_g^2 I_3,\ \sigma_a^2 I_3). \tag{17}
$$

**단위 주의**: (17)은 **표본별 이산 잡음**이다. 데이터시트의 잡음 밀도
$\sigma^{\mathrm{cont}}$ ($\mathrm{rad/s/\sqrt{Hz}}$)로 주어지면
$\sigma_g = \sigma_g^{\mathrm{cont}}/\sqrt{\Delta t}$ 로 바꿔야 하고, 이것을 빼먹으면 공분산이
$\Delta t$ 배 틀린다. 재현 과제는 혼동을 피하려고 이산 잡음을 직접 지정한다.

**정합성 점검(sanity check).** 회전 오차는 $J_r \approx I$ 인 작은 스텝에서
$\delta\phi \approx \sum_k \eta^g_k\Delta t$ 이므로 표준편차가 $\sigma_g\Delta t\sqrt n$ 이다.
재현 과제의 설정($\sigma_g = 0.004$, $\Delta t = 0.005$, $n = 100$)에서
$0.004\cdot0.005\cdot10 = 2\times10^{-4}$ 이고, 실측 해석값이 정확히 $2.000\times10^{-4}$ 다.
$\delta v$ 는 $\sigma_a\Delta t\sqrt n = 10^{-3}$ 보다 큰 $1.126\times10^{-3}$ (12.6% 초과)인데, 그 차이가
$A_k$ 의 $-\Delta R\widehat\alpha\Delta t$ 결합항(회전 오차가 속도로 새는 경로)의 몫이다.

**가정이 깨지는 곳**: (16)은 1차이고 $\Sigma_\eta$ 가 상수·백색이라고 본다. 실제 IMU 는
바이어스 랜덤워크(저주파)와 기계적 공진·포화(고주파)를 갖고, 둘 다 백색이 아니다. 구간이 길어질수록
1차 전개가 과소평가하는 쪽으로 틀리며, 이에 대한 상계는 알려져 있지 않다(열린 문제).

### R4 — 등가속 구간에서 척도와 중력이 구별되지 않는다

단안 카메라가 주는 것은 **베어링**(방향)뿐이다. 장면과 궤적을 모두 $\lambda > 0$ 배 하면

$$
\frac{R_k^\top(\lambda p_\ell - \lambda p_k)}{\lVert \lambda p_\ell - \lambda p_k\rVert}
  = \frac{R_k^\top(p_\ell - p_k)}{\lVert p_\ell - p_k\rVert}
$$

이므로 **베어링은 전혀 바뀌지 않는다.** 척도를 묶어 주는 것은 IMU 다. (1)의 둘째 식에서
가속도계가 보는 것은 $R_k^\top(a_k - g)$ 이고, 궤적을 $\lambda$ 배 하면 $a_k \to \lambda a_k$ 다.
따라서 같은 측정을 내려면 어떤 $g^\ast$ 에 대해

$$
R_k^\top(\lambda a_k - g^\ast) = R_k^\top(a_k - g) \quad \forall k
  \quad\Longleftrightarrow\quad (\lambda - 1)\,a_k = g^\ast - g \quad \forall k. \tag{18}
$$

$a_k$ 가 시간에 따라 변하면 (18)의 좌변도 변하므로 $\lambda = 1$, $g^\ast = g$ 뿐이다 —
**가속도가 변하면 척도가 관측된다.** 그런데 $a_k \equiv c$ 가 상수이면 (18)은 $\lambda$ 하나에
대한 한 개의 방정식이 되어

$$
g^\ast = g + (\lambda - 1)\,c \tag{19}
$$

가 모든 $\lambda$ 에서 성립한다. 여기에 중력 **크기**가 알려져 있다는 조건
$\lVert g^\ast\rVert = \lVert g\rVert$ 를 넣으면

$$
\lVert g + (\lambda-1)c\rVert^2 = \lVert g\rVert^2
  \;\Longleftrightarrow\;
  (\lambda-1)\Big[(\lambda-1)\lVert c\rVert^2 + 2\,g^\top c\Big] = 0, \tag{20}
$$

즉 (10)의 두 근이다. **중력의 방향까지 알려져 있으면** $g^\ast = g$ 가 강제되어 (19)에서
$(\lambda-1)c = 0$, 즉 $\lambda = 1$ 뿐이다. 단안 VIO 초기화가 척도와 중력 방향(롤·피치)을
**함께** 추정하기 때문에 이 모호성이 실제로 나타난다.

**수치.** $c = (0.5, -0.3, 1.2)$, $g = (0,0,-9.81)$ 이면 $g^\top c = -11.772$,
$\lVert c\rVert^2 = 1.78$ 이므로

$$
\lambda^\ast = 1 + \frac{2\cdot11.772}{1.78} = \frac{6331}{445} = 14.2269662921\ldots,
$$

$g^\ast = (6.613483,\ -3.968090,\ 6.062360)$, $\lVert g^\ast\rVert = 9.81$. 척도가 14배 틀린 해가
IMU 측정과 베어링을 **$10^{-15}$ 수준에서 완벽히 재현한다**. 등가속 구간에서 초기화를 시도하면
안 되는 이유가 이것이고, 실제 시스템이 "충분한 가속도 변화"를 기다리는 근거다.

**가정이 깨지는 곳**: (18)은 가속도계 바이어스를 **알려진 것으로** 두었다. $b^a$ 도 미지이면
자유도가 하나 더 늘어 등가속이 아니어도 퇴화가 생길 수 있다 — Martinelli 의 닫힌 형태 해가
바로 이 결합(척도·속도·자세·바이어스)을 다루며, 그 논문의 퇴화 조건 목록이 이 레슨의 (18)보다
넓다. 또 (18)은 중력이 공간적으로 일정하다고 본다(실내 규모에서는 타당).

## 증명 스케치

### R1 — 선적분 항등식

**가설** H1: 이산 운동학이 정확히 (2)(3)이다. H2: 구간 $[i,j)$ 안에서 $b^g, b^a$ 가 상수다.
H3: $g$ 가 상수다.
**결론** C: (4)-(6)으로 정의한 $\Delta R_{ij}, \Delta v_{ij}, \Delta p_{ij}$ 가 (7)과 같고,
따라서 $\{R_i, v_i, p_i\}$ 에 의존하지 않는다.

**전략**: 망원 합(telescoping)과 중력 항의 산술. 매니폴드 구조는 회전에만 쓰인다.

1. **회전.** H1 의 첫 식을 $k = i,\dots,j-1$ 에 대해 곱하면 $R_j = R_i\prod\exp(\psi_k)$.
   좌변에 $R_i^\top$ 를 곱하면 (7a). 중간 회전은 $R_k = R_i\Delta R_{ik}$ 이고, 이것이 이후
   단계에서 $R_i$ 를 소거하는 유일한 도구다.
2. **속도.** H1 의 둘째 식을 합한다. $g$ 가 상수(H3)이므로 $\sum g\Delta t = g\Delta t_{ij}$ 로
   묶이고, 나머지에 1단계를 넣으면 $R_i$ 가 앞으로 빠진다. 정의 (5)가 그 결과다.
3. **위치의 중력 정산.** H1 의 셋째 식을 합하고 (I)에 2단계의 결과를 대입한다. 핵심은 산술
   항등식 $\sum_{m=0}^{n-1} m + \tfrac n2 = \tfrac{n^2}{2}$ 이고, 이것이 (7b)를 준다.
   이 한 줄이 "왜 정의 (6)에 $\tfrac12 g\Delta t_{ij}^2$ 가 들어가는가"의 답이다.
4. **결론.** 2·3 단계에서 좌변에 모인 것이 정확히 (5)(6)의 정의이고, 우변은 $\psi_k$ 와
   $\alpha_k$ 만의 함수다(H2 로 $b$ 가 상수이므로 $\alpha_k$ 가 측정만으로 결정된다). C.
5. **왜 이것이 유용한가.** 키프레임 상태 $\{R_i,v_i,p_i,R_j,v_j,p_j\}$ 가 최적화 중에 바뀌어도
   (7)의 우변은 불변이므로, IMU 인자의 잔차를 "선적분량 vs (4)-(6)의 좌변"으로 쓰면 야코비안만
   다시 계산하면 된다. 재적분을 피하는 것이 비용 전부다
   (`c5-factor-graphs-map` R2 의 선형화와 같은 구조).

**가설을 지우면**: H1 을 중간점 규칙으로 바꾸면 3단계의 산술이 $\tfrac{n^2}{2}$ 를 주지 않아
정의 (6)이 더는 (7)과 같지 않다(문제 P1). H2 를 빼면(바이어스가 구간 안에서 변하면)
$\alpha_k$ 가 미지 시계열이 되어 선적분량이 유한 차원 파라미터의 함수가 아니게 된다 — 실무는
구간을 짧게 잡아 H2 를 근사적으로 유지하고, 구간 사이에 바이어스 랜덤워크 인자를 넣는다.
H3 를 빼면 $\sum g_k\Delta t$ 가 묶이지 않는다(궤도 규모에서 문제가 된다).

(생략: 연속 모형과 (2) 사이의 국소 절단 오차 분석. Barfoot SER ch.9 와 Forster et al. IV 절.)

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (증명, ★★★, R1)** ⓐ (7b)의 산술 항등식을 증명하고, ⓑ (2)의 위치 갱신을 중간점 규칙
$p_{k+1} = p_k + \tfrac12(v_k + v_{k+1})\Delta t$ 로 바꾸면 (6)의 정의가 더는 (7)의 셋째 식과
같지 않음을 보이고 그 차이를 $n$, $\Delta t$, $g$ 로 표현하라. ⓒ 중간점 규칙에서도 성립하는
$\Delta p$ 의 **수정된 정의**를 찾아라.
*전략 + 핵심 부등식*: ⓐ 는 $\sum_{m=0}^{n-1}m = n(n-1)/2$ 한 줄이다. ⓑ 는 중간점 규칙이
$v_{k+1} = v_k + a^w_k\Delta t$ 와 결합되어 $p_{k+1} = p_k + v_k\Delta t + \tfrac12 a^w_k\Delta t^2$
와 **같아진다**는 함정을 먼저 확인하라 — 진짜 차이가 생기는 것은 $v$ 갱신까지 중간점으로 바꿀 때다.
그 경우 $\sum(k-i)$ 가 $\sum(k-i+\tfrac12)$ 가 되어 중력 항이 $\tfrac12 g\Delta t_{ij}^2
+ \tfrac12 g\,n\Delta t^2$ 가 된다. 전개는 숨긴다.

**P2 (유도, ★★, R2)** (11)을 빠진 줄 없이 유도하라. 특히 ⓐ $\exp(\psi + J_r^{-1}u) \approx
\exp(\psi)\exp(u)$ 형태의 우 야코비안 관계를 어느 방향으로 썼는지 밝히고, ⓑ
$\exp(u)\exp(\psi) = \exp(\psi)\exp(\exp(-\psi)u)$ 를 $\mathrm{Ad}$ 로 정당화하라.
ⓒ (13)의 부호가 $\hat x y = -\hat y x$ 에서 나옴을 보여라.
*해답 스케치*: ⓑ 는 $\exp(\psi)^{-1}\exp(u)\exp(\psi) = \exp(\mathrm{Ad}_{\exp(-\psi)}u)$ 와
$SO(3)$ 에서 $\mathrm{Ad}_R = R$ 이라는 두 사실의 결합이다
(`c5-manifold-estimation` 표기표). ⓐ 는 섭동이 **오른쪽**에 붙어야 (11)의 $\Delta R^\top$ 전파가
나온다는 점이 핵심이다.

**P3 (계산, ★, R1)** 재현 과제의 시뮬레이터와 바이어스 참값에서 선적분량을 계산하라.
*정답*: $\mathrm{Log}(\Delta R_{ij}) = (0.070574508,\ 0.231862532,\ 0.397082183)$,
$\Delta v_{ij} = (2.166640013,\ 0.085362195,\ 4.498185860)$,
$\Delta p_{ij} = (0.549102630,\ 0.029297900,\ 1.117894720)$. 허용오차 $10^{-9}$.
검산: (4)-(6)의 좌변을 조밀 적분으로 따로 계산해 $10^{-12}$ 이내로 일치하는지 본다
(재현 과제 Part A). 두 값이 다르면 이산화 규약이 (2)와 다르다는 뜻이다.

**P4 (계산, ★★, R4)** $c = (0.5,-0.3,1.2)$, $g = (0,0,-9.81)$ 에서 ⓐ $\lambda^\ast$ 와
$g^\ast$ 를 구하고 ⓑ $\lVert g^\ast\rVert = \lVert g\rVert$ 를 확인하고 ⓒ 두 해가 같은 IMU
측정과 같은 베어링을 주는지 수치로 확인하라. ⓓ $c$ 가 $g$ 와 평행하면 $\lambda^\ast$ 는?
ⓔ $c \perp g$ 이면?
*정답*: ⓐ $\lambda^\ast = 6331/445 = 14.2269662921$,
$g^\ast = (6.613483,\ -3.968090,\ 6.062360)$. ⓑ $\lVert g^\ast\rVert = 9.81$ (정확히).
ⓒ 가속도계 측정 차 $< 10^{-14}$, 베어링 차 $< 10^{-14}$. 허용오차 $10^{-8}$.
ⓓ $c = \mu g$ 이면 $g^\top c = \mu\lVert g\rVert^2$, $\lVert c\rVert^2 = \mu^2\lVert g\rVert^2$
이므로 $\lambda^\ast = 1 - 2/\mu$ — **평행해도 모호성이 남는다**(예: $\mu = 1$ 에서
$\lambda^\ast = -1$ 인데 $\lambda > 0$ 이어야 하므로 이 경우는 배제된다. $\mu = 4$ 면
$\lambda^\ast = 0.5$ 로 유효하다). ⓔ $g^\top c = 0$ 이면 $\lambda^\ast = 1$ 이므로 두 근이
겹쳐 **모호성이 사라진다** — 중력에 수직인 등가속은 척도를 결정한다. ⓓⓔ 의 대조를 쓰지 않으면 미달.

**P5 (구현, ★★★, R2·R3)** 선적분을 야코비안 (11)-(15)와 공분산 (9)(16)과 **같은 루프에서**
구현하라.
*루브릭*: ⓐ Part A 가 $10^{-12}$ 이내로 통과 ⓑ 야코비안 보정 오차가 $\lVert\delta b\rVert^2$
로 스케일함을 네 자리 이상에서 보고(재현 과제 Part B 의 표) ⓒ 공분산이 몬테카를로와 3% 이내로
일치(Part D) ⓓ 루프 내 갱신 순서($p \to v \to R$)를 코드 주석으로 **근거와 함께** 명시
ⓔ 잡음 단위(이산 vs 밀도)를 문서화했다.

**P6 (반례, ★★, R4)** "IMU 를 쓰면 단안 척도가 항상 관측된다"가 거짓임을 보이고, 거짓이 되는
조건을 **두 가지 서로 다른 방식**으로 특징화하라: ⓐ (18)에서 직접, ⓑ 선형화된 계의 영공간
차원으로. ⓒ 그리고 정지 상태($a_k \equiv 0$)에서 무엇이 관측되고 무엇이 관측되지 않는지 쓰라.
*성질 체크리스트*: ⓐ 는 $a_k$ 가 상수인 모든 경우(정지·등속·등가속 포함)를 포괄해야 한다.
ⓑ 는 `c5-observability-consistency` 의 도구를 미리 쓰는 것이므로 "영공간 차원이 하나 늘어난다"
수준의 진술이면 통과. ⓒ 는 $c = 0$ 이면 (20)이 $(\lambda-1)^2\cdot0 = 0$ 로 모든 $\lambda$ 를
허용 — 즉 척도가 **완전히** 미결정이고 중력 방향만 관측된다는 점을 짚어야 한다.

**P7 (논문, ★★, R1·R2·R3)** `forster2017-preintegration` IV-V 절과 부록을 읽고 ⓐ 저자들의
이산화 규약이 본문 (2)와 같은지 확인하고 다르면 어디가 다른지 쓰고, ⓑ 저자들이 보장하는 것과
보장하지 않는 것을 각각 두 줄로 구분하고, ⓒ Table/그림을 재현하는 데 빠진 정보 3개를 찾아라.
*루브릭*: ⓐ 는 "회전은 같고 위치·속도의 적분 규칙과 잡음을 리 대수에 넣는 위치가 다를 수 있다"를
구체적 식 번호로 짚으면 통과. ⓑ 는 "항등식은 정확, 잡음·바이어스 전파는 1차" 를 구분하면 통과.
ⓒ 는 IMU 잡음 파라미터의 단위와 출처, 키프레임 선택 규칙, 초기화 절차 중 셋.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Forster, Carlone, Dellaert & Scaramuzza, "On-manifold preintegration for real-time
   visual-inertial odometry" (2017, IEEE T-RO)** — 역할: `원전(seminal)`.
   <https://arxiv.org/abs/1512.02363> (IV-V 절 + 부록)
   추가 질문: ⓐ 저자들이 "on-manifold"를 강조하는 이유를 `c5-manifold-estimation` R1 의
   재추적 불변성으로 다시 쓰면? ⓑ 부록의 야코비안이 본문 (11)-(15)와 부호까지 일치하는가?
2. **Lupton & Sukkarieh, "Visual-inertial-aided navigation for high-dynamic motion in built
   environments without initial conditions" (2012, IEEE T-RO)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1109/TRO.2011.2170332> (III-IV 절)
   추가 질문: ⓐ 이 논문의 선적분은 회전을 어떤 매개화로 다루며, 그 선택이 Forster et al. 의
   비판 대상인 이유는? ⓑ "without initial conditions"가 정확히 무엇을 주장하는가?
3. **Martinelli, "Vision and IMU data fusion: closed-form solutions for attitude, speed,
   absolute scale, and bias" (2012, IEEE T-RO)** — 역할: `표준(standard)`.
   <https://doi.org/10.1109/TRO.2011.2160468>
   추가 질문: ⓐ 저자가 나열한 퇴화(degenerate) 운동 목록에 본문 (18)의 "가속도가 상수"가
   포함되는가, 더 넓은가? ⓑ 닫힌 형태 해가 있는데도 실제 시스템이 반복 최적화를 쓰는 이유는?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, Part A-C 가 각 1초 이내,
Part D 의 몬테카를로 20000회가 3분 이내. 메모리 200MB 이하. numpy 만 쓴다.

**입력 데이터**는 아래 시뮬레이터가 만든다(고정 시드·결정론적). 외부 데이터셋이 필요 없다.
$SO(3)$ 유틸리티도 제공하므로 **학습자가 쓸 것은 `preintegrate`, `dense`, `propagate_cov` 세
함수뿐**이다.

```python
"""c5-imu-preintegration 재현 과제: IMU 시뮬레이터와 SO(3) 유틸리티."""

import numpy as np

SEED = 20261112
DT, NSTEP = 0.005, 100  # 200 Hz, 키프레임 간격 0.5 s
G = np.array([0.0, 0.0, -9.81])
SIGMA_G, SIGMA_A = 0.004, 0.02  # 표본별 이산 잡음 표준편차: rad/s, m/s^2
B_G = np.array([0.01, -0.02, 0.005])
B_A = np.array([0.05, 0.02, -0.03])
R0_PHI = np.array([0.2, -0.3, 0.5])
V0 = np.array([0.7, -0.2, 0.1])
P0 = np.array([1.0, 2.0, -0.5])


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


def jac_r_so3(phi):
    """우 야코비안 J_r(phi) = J_l(-phi)."""
    t, W = float(np.linalg.norm(phi)), skew(phi)
    if t < 1e-10:
        return np.eye(3) - 0.5 * W + W @ W / 6.0
    return np.eye(3) - (1.0 - np.cos(t)) / t**2 * W + (t - np.sin(t)) / t**3 * W @ W


def truth_signals():
    """해석적 궤적의 참 각속도(동체)와 참 가속도(세계)."""
    t = DT * np.arange(NSTEP)
    omega = np.column_stack([0.3 * np.sin(2.0 * t), 0.5 * np.cos(1.5 * t), 0.8 + 0.0 * t])
    acc_w = np.column_stack([1.5 * np.cos(t), -1.0 * np.sin(1.2 * t), 0.4 * np.sin(0.7 * t)])
    return omega, acc_w


def imu_readings(omega, acc_w, noise_rng=None):
    """참 신호에서 IMU 측정을 만든다 (식 (1), 자세는 (2)의 규약으로 전진)."""
    R, wm, am = exp_so3(R0_PHI), [], []
    for k in range(NSTEP):
        w = omega[k] + B_G
        a = R.T @ (acc_w[k] - G) + B_A
        if noise_rng is not None:
            w = w + noise_rng.normal(scale=SIGMA_G, size=3)
            a = a + noise_rng.normal(scale=SIGMA_A, size=3)
        wm.append(w)
        am.append(a)
        R = R @ exp_so3(omega[k] * DT)
    return np.array(wm), np.array(am)
```

**해야 할 일.** ⓐ `preintegrate(wm, am, bg, ba)` — (7)의 세 양과 (11)-(15)의 야코비안 다섯 개를
한 루프에서. ⓑ `dense(wm, am, bg, ba, R0, v0, p0)` — (2)(3)을 그대로 적분해 $(R_j, v_j, p_j)$.
ⓒ `propagate_cov(wm, am, bg, ba)` — (9)(16)의 $9\times9$ 공분산.

**Part A — 선적분 항등식.** `preintegrate` 의 결과로 복원한
$R_i\Delta R$, $v_i + g\Delta t_{ij} + R_i\Delta v$,
$p_i + v_i\Delta t_{ij} + \tfrac12 g\Delta t_{ij}^2 + R_i\Delta p$ 가 `dense` 의 결과와
일치하는지 본다(잡음 없이, 참 바이어스로).

**Part B — 바이어스 보정의 1차 정확도.** $\lVert\delta b^g\rVert = \lVert\delta b^a\rVert
\in \{10^{-4}, 10^{-3}, 10^{-2}, 10^{-1}\}$ 에 대해 (8)의 보정값과 $\bar b + \delta b$ 에서의
**재적분값**을 비교한다. 방향은 `np.random.default_rng(7)` 로 뽑고 정규화한다.

**Part C — 척도·중력 모호성.** (10)의 $\lambda^\ast$ 와 (19)의 $g^\ast$ 를 계산하고, 상수
가속도 $c = (0.5,-0.3,1.2)$ 궤적에서 두 해의 가속도계 측정과 베어링이 같은지 확인한다.
랜드마크는 $(4,1,2)$, $(-2,3,0.5)$, $(1,-5,3)$ 을 쓰고 $\lambda^\ast$ 배 한다.

**Part D — 공분산.** `propagate_cov` 의 해석 공분산과, 잡음을 20000회 뽑아 선적분을 다시 한
몬테카를로 공분산을 비교한다(시드 `SEED`).

**수용 기준 — 네 조건을 모두 만족해야 통과다.**

1. **Part A** — $\max\lvert\cdot\rvert$ 오차가 $R_j$, $v_j$, $p_j$ 모두 $< 10^{-12}$
   (참조 구현 $1.0\times10^{-15}$, $1.4\times10^{-15}$, $6.7\times10^{-16}$).
   **이것은 수치 근사가 아니라 대수 항등식**이므로 기계 정밀도로 맞아야 한다. $10^{-6}$ 수준으로만
   맞으면 이산화 규약이 (2)와 다르다. 또 선적분량 자체가 P3 의 정답과 $10^{-9}$ 이내로 일치한다.
2. **Part B** — 아래 표를 재현하고(각 값 상대오차 1% 이내), **오차/$\lVert\delta b\rVert^2$ 가
   네 행에서 같은 값**임을 보인다.

   | $\lVert\delta b\rVert$ | $\Delta R$ 오차 (rad) | $\Delta v$ 오차 (m/s) | $\Delta p$ 오차 (m) |
   |---|---|---|---|
   | $10^{-4}$ | $9.401\times10^{-11}$ | $1.642\times10^{-9}$ | $2.403\times10^{-10}$ |
   | $10^{-3}$ | $9.401\times10^{-9}$ | $1.642\times10^{-7}$ | $2.403\times10^{-8}$ |
   | $10^{-2}$ | $9.401\times10^{-7}$ | $1.642\times10^{-5}$ | $2.403\times10^{-6}$ |
   | $10^{-1}$ | $9.402\times10^{-5}$ | $1.645\times10^{-3}$ | $2.406\times10^{-4}$ |

   2차 상수는 $\Delta R$ 0.00940, $\Delta v$ 0.1642, $\Delta p$ 0.02403 이다.
3. **Part C** — $\lambda^\ast = 14.2269662921$ ($=6331/445$, 허용오차 $10^{-9}$),
   $g^\ast = (6.613483,\ -3.968090,\ 6.062360)$ ($10^{-6}$),
   $\lVert g^\ast\rVert = 9.81$ ($10^{-9}$), 그리고 두 해의 **가속도계 측정 차**와 **베어링 차**가
   모두 $< 10^{-14}$ (참조 $3.6\times10^{-15}$, $3.3\times10^{-16}$).
4. **Part D** — 해석 표준편차가 아래와 일치하고($10^{-8}$), 20000회 몬테카를로와의 상대오차가
   대각에서 3% 이내, $\sigma_i\sigma_j$ 로 정규화한 $9\times9$ 전체에서 5% 이내
   (참조 1.07% 와 2.13%).

   | 블록 | 해석 표준편차 |
   |---|---|
   | $\delta\phi$ | $(2.000, 2.000, 2.000)\times10^{-4}$ |
   | $\delta v$ | $(1.12614, 1.152626, 1.029786)\times10^{-3}$ |
   | $\delta p$ | $(3.05226, 3.08985, 2.92659)\times10^{-4}$ |

   $\delta\phi$ 가 $\sigma_g\Delta t\sqrt n = 2\times10^{-4}$ 와 **정확히** 같고 $\delta v$ 는
   $\sigma_a\Delta t\sqrt n = 10^{-3}$ 보다 12.6% 큰 것을 함께 보고한다 — 그 차이가 $A_k$ 의
   회전-속도 결합항이다.

**비교 대상**: ⓐ Part A 의 `dense` 가 그 자체로 베이스라인이다. ⓑ Part B 의 베이스라인은
**매번 재적분**이고, 참조 구현에서 보정은 재적분의 $1/n$ 비용이다($n = 100$). ⓒ Part D 의
베이스라인은 몬테카를로. 선택: $\Delta t$ 를 $0.005 \to 0.0025 \to 0.00125$ 로 줄여 Part A 의
오차가 **변하지 않는** 것과(항등식은 $\Delta t$ 와 무관) 연속 궤적에 대한 오차는 줄어드는 것을
대조해 R5 를 확인한다.

**보고할 수치**: 위 네 조건의 모든 값, Part B 의 2차 상수 세 개, 그리고 Part D 의
$\delta\phi$ 해석값과 $\sigma_g\Delta t\sqrt n$ 의 비.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| Part A 오차가 $10^{-3}$ 규모 | $\Delta p$ 정의에서 $\tfrac12 g\Delta t_{ij}^2$ 를 빼먹었다 | 오차가 $\tfrac12\cdot9.81\cdot0.25 = 1.23$ m 의 배수인지 본다 |
| Part A 오차가 $\Delta t_{ij}$ 에 비례해 커진다 | 적분 규칙 불일치 — `dense` 는 사각형, `preintegrate` 는 중간점(또는 반대) | 두 함수에서 $v$ 와 $p$ 갱신 순서를 나란히 비교한다 |
| Part A 의 $v$ 만 틀린다 | $\Delta v$ 에서 $\Delta R_{ik}$ 가 아니라 $\Delta R_{i,k+1}$ 을 썼다 | $n = 1$ 로 줄여 손으로 대조한다 |
| Part B 오차가 $\lVert\delta b\rVert$ 에 **선형** | 야코비안 재귀의 갱신 순서가 틀렸다($R$ 을 먼저 갱신) | 루프에서 $p\to v\to R$ 순서인지, (14)(15)가 **갱신 전** $J^v$ 를 쓰는지 확인 |
| Part B 의 $\Delta R$ 오차만 선형 | (11)에서 $\Delta R_{k,k+1}^\top$ 대신 $\Delta R_{k,k+1}$ 을 썼다 | $\delta b^a = 0$ 으로 두고 $\Delta R$ 만 분리해 본다 |
| Part D 가 $\Delta t$ 배 틀리다 | 잡음을 밀도로 넣었다 | $\delta\phi$ 표준편차를 $\sigma_g\Delta t\sqrt n$ 과 비교한다 |
| Part D 의 $\delta p$ 만 틀리다 | $B_k$ 의 $\tfrac12\Delta R\Delta t^2$ 항을 빠뜨렸다 | $\sigma_a$ 만 켜고(=$\sigma_g=0$) $\delta p/\delta v$ 비가 $\approx\Delta t_{ij}/3$ 인지 본다 |
| Part C 의 베어링이 다르다 | 랜드마크를 $\lambda^\ast$ 배 하지 않았다 | $\lambda = 1$ 로 두면 차가 0 인지 먼저 확인한다 |

## 열린 문제

- **(열린 문제) 시변 바이어스와 군 구조의 충돌** — (7)은 구간 안에서 바이어스가 상수라는 H2 에
  의존하고, 바이어스를 상태에 넣으면 동역학이 더는 군 아핀이 아니다
  (`c5-manifold-estimation` R3 의 가설). 현재 접근은 구간을 짧게 잡고 랜덤워크 인자를 넣거나,
  바이어스를 포함한 더 큰 군을 찾는 것이다([contact-aided
  InEKF](https://doi.org/10.1177/0278364919894385) 가 접촉 상태에 대해 하는 일과 같은 종류).
  비어 있는 자리: 바이어스를 포함한 상태에 대해 **로그-선형성을 보존하는** 군 구조, 또는 그것이
  불가능함의 증명.
- **(열린 문제) 초기화가 충분히 정보적인지 온라인으로 판정하기** — R4 는 등가속 구간에서 척도가
  두 값을 갖는다는 **정확한** 진술이지만, 실제로 필요한 것은 "지금까지 모은 구간이 척도를
  얼마나 잘 결정하는가"의 정량적 판정이다. 현재 접근은 휴리스틱(가속도 분산 임계값,
  [VINS-Mono](https://arxiv.org/abs/1708.03852) V 절의 조건수 검사)과
  [닫힌 형태 해의 퇴화 조건 목록](https://doi.org/10.1109/TRO.2011.2160468)이다.
  비어 있는 자리: 척도 추정 오차에 대한 **인증 가능한 하한**(Cramér-Rao 류)을 온라인으로
  계산해 초기화 성공을 판정하는 규칙.
- **(열린 문제) 긴 구간에서 선적분 공분산의 신뢰도** — (16)은 1차 전개이고 $\Sigma_\eta$ 가
  백색·상수라고 본다. 구간이 길어지거나 진동이 심하면 과소평가하는 쪽으로 틀리는데, 그 편향의
  상계가 없다. 현재 접근: 구간 길이를 공학적으로 제한하고 사후에 $\chi^2$ 로 점검하는 것
  ([Forster et al.](https://arxiv.org/abs/1512.02363) 부록, Barfoot SER ch.9). 비어 있는 자리:
  구간 길이·운동 강도에서 공분산 편향으로 가는 명시적 상계, 또는 2차 항을 싸게 넣는 방법.

## 개념 점검

`rc quiz c5-imu-preintegration` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c5-imu-preintegration-quiz
questions:
  - id: q1
    type: single
    prompt: "선적분량 $\\Delta p_{ij}$ 의 정의에서 $-v_i\\Delta t_{ij} - \\tfrac12 g\\Delta t_{ij}^2$ 를 빼는 이유는?"
    choices:
      - "단위를 맞추기 위해서"
      - "그 두 항이 IMU 측정이 아니라 초기 상태와 중력으로만 결정되므로, 빼야 남는 양이 IMU 만의 함수가 된다"
      - "중력을 보상해 가속도계 측정을 복원하기 위해서"
      - "수치 안정성을 위해서"
    answer: 1
    explanation: "(7b)의 산술에서 중력 항이 정확히 $\\tfrac12 g\\Delta t_{ij}^2$ 로 묶이고 $v_i\\Delta t_{ij}$ 도 따로 떨어진다. 둘을 정의에서 빼 두면 남는 $\\Delta p_{ij}$ 가 측정과 바이어스만의 함수가 되어 키프레임 상태가 바뀌어도 재적분이 필요 없다."
    concept: { front: "$\\Delta p$ 정의의 중력·속도 항", back: "초기 상태와 중력으로 결정되는 부분을 미리 떼어내 선적분량을 IMU 만의 함수로 만든다 — 재적분을 피하는 전부" }
  - id: q2
    type: truefalse
    prompt: "선적분 항등식은 연속 운동학에 대한 1차 근사이므로 $\\Delta t$ 를 줄여야 정확해진다."
    answer: false
    explanation: "항등식은 (2)의 **이산** 모형에 대해 정확하다 — 재현 과제 Part A 가 $10^{-15}$ 로 맞는 이유다. $\\Delta t$ 를 줄여 줄어드는 것은 (2) 자체가 연속 모형을 근사하는 이산화 오차이고, 이는 선적분 오차와 **다른 것**이다(R5)."
    concept: { front: "선적분 오차 vs 이산화 오차", back: "항등식은 이산 모형에서 정확(기계 정밀도). 이산화 오차는 별개이며 $\\Delta t$ 로 줄어든다" }
  - id: q3
    type: single
    prompt: "바이어스 추정이 $\\delta b$ 만큼 바뀔 때 (8)의 1차 보정을 쓰면 오차는 어떻게 커지는가?"
    choices:
      - "$O(\\lVert\\delta b\\rVert)$"
      - "$O(\\lVert\\delta b\\rVert^2)$"
      - "$O(\\lVert\\delta b\\rVert)\\cdot\\Delta t_{ij}$ 로 구간 길이에 비례"
      - "커지지 않는다 — 보정은 정확하다"
    answer: 1
    explanation: "1차 Taylor 전개이므로 잔차가 2차다. 재현 과제가 네 자리에 걸쳐 그것을 측정한다 — $\\lVert\\delta b\\rVert$ 를 10배 하면 오차가 100배가 되고, 2차 상수는 $\\Delta v$ 에서 0.1642 다. 그래서 바이어스가 크게 움직이면 재적분해야 한다."
    concept: { front: "바이어스 1차 보정의 오차", back: "$O(\\lVert\\delta b\\rVert^2)$ — 10배 변화에 오차 100배. 크게 움직이면 재적분(iSAM2 의 재선형화 임계값과 같은 판단)" }
  - id: q4
    type: single
    prompt: "세계 프레임 가속도가 상수인 구간에서 단안 관성-시각 융합의 척도는?"
    choices:
      - "항상 관측된다 — IMU 가 절대 가속도를 주기 때문"
      - "중력 크기를 알면 두 값만 가능하고, 중력 방향까지 알면 유일하다"
      - "완전히 미결정이다"
      - "베어링만으로 결정된다"
    answer: 1
    explanation: "(18)에서 $(\\lambda-1)a_k = g^\\ast - g$ 가 모든 $k$ 에 대해 성립해야 하므로 $a_k$ 가 상수면 $\\lambda$ 가 자유로워진다. $\\lVert g\\rVert$ 를 고정하면 (20)의 두 근만 남고, 방향까지 고정하면 $\\lambda = 1$ 이다. 재현 과제의 설정에서 두 번째 근은 $\\lambda^\\ast = 14.23$ — 14배 틀린 척도가 측정을 완벽히 재현한다."
    concept: { front: "등가속 구간의 척도 모호성", back: "$\\lambda^\\ast = 1 - 2g^\\top c/\\lVert c\\rVert^2$ — 중력 크기만 알면 두 해, 방향까지 알면 유일. 정지($c=0$)면 완전 미결정" }
  - id: q5
    type: short
    prompt: "자이로 잡음이 $\\sigma_g$(표본별, rad/s)일 때 $n$ 표본 선적분의 회전 오차 표준편차를 $\\sigma_g$, $\\Delta t$, $n$ 으로 쓰면?"
    answer: ["sigma_g * dt * sqrt(n)", "sigma_g dt sqrt(n)", "σ_g Δt √n", "sigma_g*dt*sqrt(n)", "sigma_g dt n^(1/2)"]
    explanation: "$J_r \\approx I$ 인 작은 스텝에서 $\\delta\\phi \\approx \\sum_k \\eta^g_k\\Delta t$ 이므로 독립 합의 표준편차가 $\\sigma_g\\Delta t\\sqrt n$ 이다. 재현 과제에서 $0.004\\cdot0.005\\cdot10 = 2\\times10^{-4}$ 이고 해석 공분산이 정확히 그 값을 준다 — 공분산 코드의 1차 정합성 점검으로 쓴다."
    concept: { front: "선적분 회전 오차의 크기", back: "$\\sigma_g\\Delta t\\sqrt n$ — 표본별 이산 잡음 기준. 밀도로 주어지면 $\\sigma_g = \\sigma^{cont}/\\sqrt{\\Delta t}$ 로 변환" }
```

## 이 단계 공부법

1. **측정 모형의 부호를 먼저 손으로 확인한다 (30분)** — (1)의 둘째 식에 정지 상태
   ($a = 0$, $R = I$)를 넣어 가속도계가 $(0,0,+9.81)$ 을 보고하는지 확인한다. 이 부호를 틀리면
   이후 전부 틀린다.
2. **(7b)를 종이에서 맞춰 본다 (45분)** — $n = 3$ 으로 두고 위치 합을 손으로 전개해 중력 항이
   $\tfrac12 g(3\Delta t)^2$ 로 정확히 맞아떨어지는 것을 본다. 이 한 줄이 R1 의 전부이고,
   P1 ⓑ 가 그것이 깨지는 조건을 보여 준다.
3. **야코비안 재귀를 $n=2$ 로 손으로 (60분)** — (11)-(15)를 두 스텝만 손으로 돌려 보고,
   갱신 순서를 바꾸면 무엇이 틀리는지 직접 확인한다. Forster et al. 부록과 부호까지 대조한다.
4. **Part A·B 를 먼저 구현한다 (90분)** — Part A 가 $10^{-15}$ 로 맞을 때까지 고치고
   (맞지 않으면 이산화 규약 문제다), Part B 의 표에서 2차 스케일링을 네 자리로 확인한다.
   **야코비안이 틀리면 Part B 가 선형으로 나온다** — 가장 민감한 검사다.
5. **Part C 를 계산기로 먼저 (30분)** — $\lambda^\ast$ 를 (10)에 손으로 넣어 14.23 을 얻고,
   그 다음 코드로 측정이 실제로 같은지 확인한다. 14배 척도 오차가 완벽히 측정을 재현하는 것을
   눈으로 보면 "초기화"가 왜 별도 문제인지 이해된다.
6. **Part D (90분)** — 공분산을 몬테카를로로 검증한다. $\delta\phi$ 가
   $\sigma_g\Delta t\sqrt n$ 과 정확히 같은지 먼저 보고, 그 다음 $\delta v$ 의 12.6% 초과가
   결합항에서 오는 것을 $\sigma_g = 0$ 으로 두어 확인한다.
7. **논문은 식 번호를 들고 읽는다 (150분)** — Forster et al. 부록을 본문 (11)-(16)과 한 줄씩
   대조하고(부호까지), Lupton & Sukkarieh 에서 "선적분"이라는 아이디어가 처음 나오는 지점을
   찾고, Martinelli 의 퇴화 조건 목록을 (18)과 비교한다. 논문당 1페이지 노트는 **반드시** 쓴다.
8. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제" 세 개 중 하나를 골라 한 문단으로 쓴다.
   초기화 판정은 재현 과제의 $\lambda^\ast$ 가 바로 동기이므로 가장 쓰기 쉽다.

**통과 기준**: 백지에서 (7)과 (7b)를 유도할 수 있고, (11)을 유도할 수 있고, 재현 과제의 네
조건을 모두 만족하는 코드를 갖고 있고, 논문 3편의 노트가 있다.
