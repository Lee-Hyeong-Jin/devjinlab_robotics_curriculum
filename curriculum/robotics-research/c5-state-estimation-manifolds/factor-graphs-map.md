---
id: c5-factor-graphs-map
title: 인자 그래프와 MAP 추론
summary: >-
  상태 추정을 필터 재귀가 아니라 인자 그래프(factor graph) 위의 MAP 추론으로 세우고, 가우시안
  가정 아래 MAP 이 비선형 최소제곱과 동등함을 증명한다. 가우시안 변수 소거가 Schur 보완과 같은
  연산임을 유도해, 필터링이 평활(smoothing)의 한 가지 소거 순서 + 조건부를 버리는 정책일 뿐임을
  보인다. 2랩 SE(2) 포즈 그래프를 Gauss-Newton 으로 풀어 희소 해와 조밀 해의 일치를 재현한다.
objectives:
  - 가우시안 인자 그래프의 MAP 문제가 비선형 최소제곱과 동등함을 가정을 명시해 증명할 수 있다.
  - 측정 공분산이 상태에 의존할 때 그 동등성이 어디서 깨지는지 설명할 수 있다.
  - 가우시안 변수 소거를 완전제곱식으로 전개해 Schur 보완을 빠진 줄 없이 유도할 수 있다.
  - 칼만 필터 갱신식을 최소제곱 문제의 정규방정식에서 유도하고 공분산 형태와의 동등성을 보일 수 있다.
  - 정규방정식(Cholesky)과 QR 분해의 조건수 차이를 수치로 설명할 수 있다.
  - SE(2) 포즈 그래프의 야코비안을 직접 쓰고 Gauss-Newton 으로 수렴시켜 희소·조밀 해를 대조할 수 있다.
prerequisites: [c1-so3-se3-exponential]
difficulty: 5
estimated_minutes: 540
tags: [state-estimation, factor-graph, map, least-squares, smoothing, research]
activities:
  - id: c5-factor-graphs-map-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c5-factor-graphs-map-papers
    kind: reading
    title: 필독 논문 2편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 120
  - id: c5-factor-graphs-map-problems
    kind: exercise
    title: 문제 세트 (유도 1 · 증명 2 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: c5-factor-graphs-map-reproduction
    kind: exercise
    title: 재현 과제 — 2랩 SE(2) 포즈 그래프의 GN 해와 희소·조밀 대조 (R2)
    estimated_minutes: 135
  - id: c5-factor-graphs-map-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.3 (Linear-Gaussian Estimation), ch.4 (Nonlinear Non-Gaussian Estimation). 이 레슨의 1순위 교재. 전문 PDF 무료.
  - title: "Dellaert & Kaess — Factor Graphs for Robot Perception (2017)"
    url: https://doi.org/10.1561/2300000043
    kind: article
    note: 필독 1. 역할 서베이(survey). 2-4절(인자 그래프, 변수 소거, Bayes net)을 읽는다.
  - title: "Dellaert & Kaess — Square Root SAM (2006, IJRR)"
    url: https://doi.org/10.1177/0278364906072768
    kind: article
    note: 필독 2. 역할 원전(seminal). 3-5절(정보행렬·제곱근 정보·변수 순서)을 읽는다.
  - title: "CMU 16-833 Robot Localization and Mapping (Kaess)"
    url: https://www.cs.cmu.edu/~kaess/teaching/16833/Fall2024
    kind: course
    note: 이 모듈의 기준 과목. 주차 일정은 비공개이고 소개문만 공개되어 있다.
  - title: "MIT 16.485 Visual Navigation for Autonomous Vehicles (OCW)"
    url: https://ocw.mit.edu/courses/16-485-visual-navigation-for-autonomous-vehicles-vnav-fall-2020/
    kind: course
    note: 권장. L16-20 이 인자 그래프와 SLAM 백엔드를 다룬다.
---

# 인자 그래프와 MAP 추론

## 전제와 기호

이 레슨은 C5 모듈의 첫 레슨이고, 이후 다섯 레슨이 여기의 표기를 쓴다. 전제:

- 확률: 결합·조건·주변 분포, 가우시안의 선형 변환, 베이즈 규칙. 측도론은 요구하지 않는다.
- 선형대수: 블록 행렬, Cholesky·QR 분해, 조건수, 양정부호성. `c1-so3-se3-exponential` 의
  $\exp$·$\log$ 표기.
- 매니폴드 위 추정은 아직 쓰지 않는다 — 이 레슨의 변수는 모두 $\mathbb{R}^d$ 의 좌표이고,
  그 선택이 왜 틀린 것인지는 `c5-manifold-estimation` 에서 바로잡는다.

표기 규약(C5 모듈 전체에 고정):

| 기호 | 뜻 |
|---|---|
| $\mathcal{X} = \{x_1, \dots, x_n\}$ | 추정할 변수. $x_i \in \mathbb{R}^{d_i}$, 전체 차원 $N = \sum_i d_i$ |
| $\mathcal{Z} = \{z_1, \dots, z_m\}$ | 측정값. $z_k \in \mathbb{R}^{p_k}$ |
| $\mathcal{X}_k \subseteq \mathcal{X}$ | $k$ 번째 인자가 닿는 변수들 (인자의 **차수**는 $\lvert\mathcal{X}_k\rvert$) |
| $h_k : \mathcal{X}_k \to \mathbb{R}^{p_k}$ | 측정 함수(모델) |
| $\Sigma_k \succ 0$ | $z_k$ 의 잡음 공분산. $\lVert e \rVert^2_{\Sigma} := e^\top \Sigma^{-1} e$ |
| $J_k = \partial h_k / \partial x$ | $h_k$ 의 야코비안, 선형화 지점에서 평가 |
| $A$ | **화이트닝된** 야코비안을 쌓은 $M \times N$ 행렬. 블록은 $\Sigma_k^{-1/2} J_k$, $M = \sum_k p_k$ |
| $b$ | 화이트닝된 잔차 $-\Sigma_k^{-1/2}(h_k(x) - z_k)$ 를 쌓은 벡터 |
| $\Lambda = A^\top A \in \mathbb{R}^{N\times N}$ | 정보행렬(information matrix) |
| $\eta = A^\top b \in \mathbb{R}^N$ | 정보벡터 |
| $\mathsf{R}$ | $\Lambda = \mathsf{R}^\top \mathsf{R}$ 의 상삼각 Cholesky 인자 = **제곱근 정보행렬**. 회전행렬 $R$ 과 구별한다 |
| $\mathcal{S}(x_i)$ | $x_i$ 를 소거할 때의 **separator** — $x_i$ 와 인자를 공유하는 나머지 변수들 |
| $\chi^2(x)$ | $\lVert A x - b\rVert^2$ 형태의 가중 잔차 제곱합 |

**인자 그래프(factor graph)**는 변수 노드 $x_i$ 와 인자 노드 $\phi_k$ 로 된 이분 그래프이고,
표현하는 것은 하나의 함수 분해다:

$$
\phi(\mathcal{X}) = \prod_{k=1}^{m} \phi_k(\mathcal{X}_k),
  \qquad \phi_k(\mathcal{X}_k) \propto \exp\!\left(-\tfrac{1}{2}\lVert h_k(\mathcal{X}_k) - z_k \rVert^2_{\Sigma_k}\right). \tag{1}
$$

사전분포(prior)와 운동 모델(motion model)도 인자다 — 그래프에서 특별한 지위가 없다. 이 점이
필터와 평활의 구분을 **그래프의 성질이 아니라 추론 순서의 성질**로 바꾼다.

## 시작 전 자가 진단

이 모듈의 첫 레슨이므로 준비 상태를 먼저 점검한다. **선수 레슨은 잠겨 있지 않다** — 아래를 전부
풀 수 있으면 권장 선수(R0 모듈, `c1-so3-se3-exponential`)를 건너뛰고 바로 시작해도 된다.
**두 문항 이상 막히면** 괄호 안의 선수 레슨으로 돌아가는 편이 빠르다.

1. 사전분포 $x\sim\mathcal{N}(0, 1)$ 에 측정 $z = x + v$, $v\sim\mathcal{N}(0, 0.25)$,
   $z = 1.0$ 이 하나 들어왔다. 사후분포의 평균과 분산은?
   (`f0-probability-statistics`, `r0-estimation-theory`)
   **정답**: 정보를 더한다 — $\Lambda = 1 + 1/0.25 = 5$, $\eta = 0 + 4\cdot1 = 4$. 따라서
   평균 $0.8$, 분산 $1/5 = 0.2$. 허용오차 $10^{-9}$.
2. $A = \begin{bmatrix}1&0\\1&1\\0&1\end{bmatrix}$, $b = (1,2,2)^\top$ 의 최소제곱 해와
   잔차 제곱합 $\lVert Ax-b\rVert^2$, 그리고 $\kappa_2(A^\top A)$ 를 구하라.
   (`r0-linear-algebra-decompositions`)
   **정답**: $A^\top A = \begin{bmatrix}2&1\\1&2\end{bmatrix}$, $A^\top b = (3,4)^\top$,
   $x^\ast = (2/3,\ 5/3)^\top$, $\lVert Ax^\ast-b\rVert^2 = 1/3$,
   $\kappa_2(A^\top A) = 3/1 = 3$ (따라서 $\kappa_2(A) = \sqrt{3}$). 허용오차 $10^{-9}$.
3. $M = \begin{bmatrix}4&2\\2&3\end{bmatrix}$ 에서 첫 블록에 대한 Schur 보완을 계산하고,
   $M \succ 0$ 인지 판정하라. (`r0-linear-algebra-decompositions`)
   **정답**: $3 - 2\cdot4^{-1}\cdot2 = 2 > 0$ 이고 $M_{11} = 4 > 0$ 이므로 $M \succ 0$
   (고윳값 $(7\pm\sqrt{17})/2 \approx 5.5616,\ 1.4384$).
4. $5\times5$ 삼대각 양정부호 행렬의 Cholesky 인자(하삼각)의 비영 원소는 몇 개인가? 같은
   행렬에서 **3번째 변수를 가장 먼저** 소거하면 무엇이 달라지는가? (`r0-sparse-linear-algebra`)
   **정답**: 자연 순서에서는 fill-in 이 없어 $5 + 4 = 9$ 개. 3번째를 먼저 소거하면 2번과 4번이
   연결되어(separator 가 클리크가 된다) 비영 원소가 1개 늘어난다. **순서가 희소성을 결정한다**.
5. $-\log \mathcal{N}(x;\mu,\Sigma)$ 를 $x$ 와 무관한 항을 묶어 쓰라. 어느 항이 $x$ 와
   무관한가? (`f0-probability-statistics`)
   **정답**: $\tfrac12(x-\mu)^\top\Sigma^{-1}(x-\mu) + \tfrac12\log\det\Sigma
   + \tfrac{d}{2}\log 2\pi$. 뒤 두 항이 $x$ 와 무관하다 — $\Sigma$ 가 $x$ 에 의존하지 않는
   한. 이 레슨의 R1 이 바로 그 조건을 따진다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (MAP = 비선형 최소제곱) [D3]** — 잡음이 가법 가우시안이고 $\Sigma_k$ 가 **상태에
  의존하지 않으면**
  $$
  \hat{\mathcal{X}}_{\mathrm{MAP}} = \arg\max_{\mathcal{X}} \prod_k \phi_k(\mathcal{X}_k)
    = \arg\min_{\mathcal{X}} \; \frac{1}{2}\sum_{k=1}^{m} \lVert h_k(\mathcal{X}_k) - z_k \rVert^2_{\Sigma_k}. \tag{2}
  $$
- **R2 (Gauss-Newton 과 제곱근 정보 형태) [D2]** — (2)를 $\mathcal{X}^{(t)}$ 에서 선형화하면
  증분 $\delta$ 는 정규방정식
  $$
  \Lambda\,\delta = \eta, \qquad \Lambda = A^\top A, \quad \eta = A^\top b \tag{3}
  $$
  를 만족하고, 이는 선형 최소제곱 $\min_\delta \lVert A\delta - b\rVert^2$ 와 동등하다.
  $A = Q\begin{bmatrix}\mathsf{R}\\0\end{bmatrix}$ 의 QR 분해는 (3)을 $\Lambda$ 를 **만들지
  않고** $\mathsf{R}\delta = Q_1^\top b$ 로 푼다. 핵심 수치적 사실: $\kappa(\Lambda) = \kappa(A)^2$.
- **R3 (가우시안 변수 소거 = Schur 보완; 소거 = 조건화 + 주변화) [D3]** — $\Lambda \succ 0$ 인
  가우시안 $p(\mathcal{X}) \propto \exp(-\tfrac12 x^\top\Lambda x + \eta^\top x)$ 에서 $x_1$ 을
  소거하면
  $$
  p(\mathcal{X}) = \underbrace{p(x_1 \mid x_{\mathcal{S}})}_{\text{조건부, 정보 } \Lambda_{11}}
    \cdot \underbrace{p(x_{\mathcal{S}}, \dots)}_{\text{새 인자}}, \quad
    \Lambda^{\mathrm{new}}_{\mathcal{S}} = \Lambda_{\mathcal{S}\mathcal{S}}
      - \Lambda_{\mathcal{S}1}\Lambda_{11}^{-1}\Lambda_{1\mathcal{S}}. \tag{4}
  $$
  (4)의 우변은 $\Lambda$ 의 $\Lambda_{11}$ 에 대한 **Schur 보완**이고, $x_1$ 을 적분해 없애는
  주변화(marginalization)의 결과와 **같은 행렬**이다. 둘의 차이는 조건부
  $p(x_1\mid x_{\mathcal{S}})$ 를 보관하는가(평활, 역대입 가능) 버리는가(필터)뿐이다.
- **R4 (필터링은 평활의 한 소거 순서다; EKF = 재선형화 없는 1회 GN) [D2]** — 선형-가우시안
  계에서 시간 순서로 과거 상태를 소거하면 (4)가 정확히 칼만 필터 재귀가 되고, 필터의 추정값은
  전체 MAP 해의 마지막 상태 주변값과 **정확히** 일치한다. 비선형에서는 일치가 깨진다: EKF 는
  각 시각에 예측 평균에서 한 번 선형화하고 **다시 선형화하지 않는** Gauss-Newton 1회 스텝이다.
- **R5 (MAP 공분산 = 라플라스 근사) [D1]** — 최적점에서 $\operatorname{Cov}(\mathcal{X}) \approx
  \Lambda^{-1}$ 이고, 변수 $x_i$ 의 주변 공분산은 $(\Lambda^{-1})_{ii}$ 다. 이는 사후분포를
  최적점에서 2차까지 전개한 **근사**이며, 3차 이상 항이 큰 영역(큰 회전 불확실성, 거리-방위
  측정의 비선형성)에서는 실제 공분산을 과소평가한다.

## 유도

### R1 — MAP 이 비선형 최소제곱이 되는 과정

가정을 명시한다. **(A1)** 각 측정은 $z_k = h_k(\mathcal{X}_k) + \epsilon_k$, $\epsilon_k \sim
\mathcal{N}(0, \Sigma_k)$. **(A2)** $\epsilon_k$ 들은 서로 독립. **(A3)** $\Sigma_k$ 는 상수 —
$\mathcal{X}$ 에 의존하지 않는다. 사전분포 $p(\mathcal{X}_0)$ 도 (A1) 형태의 인자로 흡수한다
($h = \mathrm{id}$).

베이즈 규칙에서 $p(\mathcal{X}\mid\mathcal{Z}) = p(\mathcal{Z}\mid\mathcal{X})p(\mathcal{X})/p(\mathcal{Z})$
이고, 분모는 $\mathcal{X}$ 와 무관하므로 최대화에서 빠진다. (A2)로 가능도가 인자별로 쪼개진다:

$$
p(\mathcal{X}\mid\mathcal{Z}) \propto \prod_{k=1}^{m}
  \frac{1}{\sqrt{(2\pi)^{p_k}\det\Sigma_k}}
  \exp\!\left(-\tfrac{1}{2}(h_k(\mathcal{X}_k) - z_k)^\top \Sigma_k^{-1}(h_k(\mathcal{X}_k) - z_k)\right). \tag{5}
$$

음의 로그를 취한다. 로그는 단조증가이므로 $\arg\max$ 가 $\arg\min$ 으로 바뀌는 것 외에 아무
일도 일어나지 않는다:

$$
-\log p(\mathcal{X}\mid\mathcal{Z}) = \frac{1}{2}\sum_{k=1}^{m}
  \lVert h_k(\mathcal{X}_k) - z_k\rVert^2_{\Sigma_k}
  + \underbrace{\frac{1}{2}\sum_{k=1}^{m}\log\det\Sigma_k + \frac{1}{2}\sum_k p_k \log 2\pi + \log p(\mathcal{Z})}_{=: c}. \tag{6}
$$

(A3) 때문에 $c$ 가 $\mathcal{X}$ 에 **상수**다. 따라서 (2)가 성립한다. 유도에서 쓴 것은
(A1)(가우시안 형태), (A2)(곱으로 쪼개짐), (A3)($c$ 가 상수) 셋뿐이다.

**가정이 깨지는 곳**: $\Sigma_k = \Sigma_k(\mathcal{X})$ 인 경우(거리에 비례해 커지는 LiDAR
잡음, 조명에 따라 바뀌는 특징점 분산, 학습된 이분산 불확실성)에는 $\frac12\log\det\Sigma_k(\mathcal{X})$
가 더는 상수가 아니다. 이때 올바른 MAP 목적함수는

$$
\frac{1}{2}\sum_k \left[\lVert h_k - z_k\rVert^2_{\Sigma_k(\mathcal{X})}
  + \log\det\Sigma_k(\mathcal{X})\right] \tag{7}
$$

이고, $\log\det$ 항을 빼고 (2)만 최소화하면 **잡음을 크게 보고하는 쪽으로 해가 끌려간다**
(모든 잔차를 0 으로 만드는 자명한 퇴화: $\Sigma \to \infty$). 학습된 공분산을 인자 그래프에
넣는 최근 연구들이 바로 이 항 때문에 틀리거나 정규화를 따로 넣는다.

### R2 — 정규방정식과 제곱근 정보 형태

(2)의 목적함수를 $F(\mathcal{X}) = \tfrac12\sum_k \lVert h_k - z_k\rVert^2_{\Sigma_k}$ 라 하고
$\mathcal{X}^{(t)}$ 근방에서 $h_k(\mathcal{X}^{(t)} + \delta) \approx h_k(\mathcal{X}^{(t)}) + J_k\delta$
로 치환한다. $\Sigma_k^{-1/2}$ 를 양쪽에 곱해 화이트닝하면 (표기표의 $A, b$)

$$
F(\mathcal{X}^{(t)} + \delta) \approx \tfrac{1}{2}\lVert A\delta - b\rVert^2,
  \qquad b = -\Sigma^{-1/2}\big(h(\mathcal{X}^{(t)}) - z\big). \tag{8}
$$

$\delta$ 로 미분해 0 으로 두면 $A^\top(A\delta - b) = 0$, 즉 (3)이다. $A$ 가 열 full rank 면
$\Lambda \succ 0$ 이고 해는 유일하다. 여기서 두 길이 갈린다:

1. **Cholesky**: $\Lambda = \mathsf{R}^\top\mathsf{R}$ 를 만들고 전진·후진 대입. 비용은
   $\Lambda$ 를 쌓는 $O(\sum_k p_k d_k^2)$ 와 분해 비용.
2. **QR**: $A = Q\begin{bmatrix}\mathsf{R}\\0\end{bmatrix}$ 를 직접 분해한다.
   $\lVert A\delta - b\rVert^2 = \lVert \mathsf{R}\delta - Q_1^\top b\rVert^2 + \lVert Q_2^\top b\rVert^2$
   이므로 $\mathsf{R}\delta = Q_1^\top b$ 를 풀면 되고, 두 번째 항이 남는 $\chi^2$ 다.
   $\Lambda$ 를 **한 번도 만들지 않는다**.

두 길의 $\mathsf{R}$ 은 부호를 빼면 같다($A^\top A = \mathsf{R}^\top Q_1^\top Q_1 \mathsf{R} =
\mathsf{R}^\top\mathsf{R}$). 차이는 수치다: 특잇값이 $\sigma_i(\Lambda) = \sigma_i(A)^2$ 이므로

$$
\kappa(\Lambda) = \kappa(A)^2. \tag{9}
$$

$\kappa(A) = 10^8$ 이면 $\Lambda$ 는 배정밀도에서 수치적으로 특이하지만 $A$ 는 아니다. 이것이
`dellaert2006-square-root-sam` 의 주장 — 정보행렬을 만드는 순간 조건수를 제곱해 버린다 —
이고, 제곱근 정보 $\mathsf{R}$ 을 1급 객체로 두는 이유다.

**가정이 깨지는 곳**: (8)은 $h_k$ 의 2차 항을 버린다. 잔차가 크고 곡률이 큰 지점에서는
Gauss-Newton 스텝이 목적함수를 **증가**시킬 수 있다 — Hessian 의 참값은
$A^\top A + \sum_k r_k^\top \partial^2 h_k$ 이고 GN 은 두 번째 항을 버린다. 포즈 그래프의
초기 추측이 나쁠 때 발산하는 것이 이 때문이며, 신뢰 영역(Levenberg-Marquardt, Dogleg)이
필요한 이유다. 이 레슨의 재현 과제는 GN 이 수렴하는 영역에서만 다룬다.

### R4 — 필터링을 소거로 다시 쓰기

선형-가우시안 체인을 쓴다: $x_{i+1} = F_i x_i + w_i$, $w_i\sim\mathcal{N}(0,Q_i)$,
$z_i = H_i x_i + v_i$, $v_i\sim\mathcal{N}(0,R_i)$, 사전분포 $x_0\sim\mathcal{N}(\bar x_0, P_0)$.
전체 음의 로그 사후확률은 (6)에 의해

$$
F(x_{0:K}) = \tfrac{1}{2}\lVert x_0 - \bar x_0\rVert^2_{P_0}
  + \tfrac{1}{2}\sum_{i=0}^{K-1}\lVert x_{i+1} - F_i x_i\rVert^2_{Q_i}
  + \tfrac{1}{2}\sum_{i=0}^{K}\lVert z_i - H_i x_i\rVert^2_{R_i}. \tag{10}
$$

$x_0$ 을 소거한다. $x_0$ 이 닿는 인자는 사전분포, $z_0$, 그리고 $x_1$ 과의 운동 인자뿐이므로
$\mathcal{S}(x_0) = \{x_1\}$ 이다. (4)를 적용하면 새 인자는 $x_1$ 하나에만 붙는 가우시안이고,
그 정보행렬은 Schur 보완이다. 이것을 공분산 형태로 옮기면 칼만 필터가 된다. 한 스텝을
빠진 줄 없이 쓴다.

**갱신(update) 한 스텝.** 예측값 $\bar x$, 예측 공분산 $\bar P$, 측정 $z = Hx + v$,
$v\sim\mathcal{N}(0,R)$ 에 대해 (10)에서 $x$ 에 걸린 두 인자만 남긴 목적함수는

$$
J(x) = \tfrac{1}{2}(x - \bar x)^\top \bar P^{-1}(x - \bar x)
  + \tfrac{1}{2}(z - Hx)^\top R^{-1}(z - Hx). \tag{11}
$$

$$
\nabla J(x) = \bar P^{-1}(x - \bar x) - H^\top R^{-1}(z - Hx) = 0
$$

$$
\Longrightarrow\quad \underbrace{(\bar P^{-1} + H^\top R^{-1}H)}_{=:\ \Lambda}\,x
  = \bar P^{-1}\bar x + H^\top R^{-1} z. \tag{12}
$$

우변에서 $\bar P^{-1}\bar x = \Lambda\bar x - H^\top R^{-1}H\bar x$ 로 바꿔 쓰면

$$
\Lambda x = \Lambda \bar x + H^\top R^{-1}(z - H\bar x)
  \quad\Longrightarrow\quad \hat x = \bar x + \Lambda^{-1}H^\top R^{-1}(z - H\bar x). \tag{13}
$$

(13)이 **정보 형태**의 갱신이다. 교과서의 **공분산 형태** $\hat x = \bar x + K(z - H\bar x)$,
$K = \bar P H^\top (H\bar P H^\top + R)^{-1}$ 와 같다는 것은 항등식

$$
(\bar P^{-1} + H^\top R^{-1}H)^{-1}H^\top R^{-1} = \bar P H^\top (H\bar P H^\top + R)^{-1} \tag{14}
$$

이다. (14)를 증명한다: 좌변에 왼쪽에서 $\Lambda$, 오른쪽에서 $(H\bar PH^\top + R)$ 를 곱하면

$$
H^\top R^{-1}(H\bar P H^\top + R) = H^\top R^{-1}H\bar PH^\top + H^\top,
$$

우변에 같은 것을 곱하면

$$
\Lambda\,\bar P H^\top = (\bar P^{-1} + H^\top R^{-1}H)\bar P H^\top
  = H^\top + H^\top R^{-1}H\bar PH^\top .
$$

두 결과가 같고 $\Lambda \succ 0$, $H\bar PH^\top + R \succ 0$ 이므로 (14)가 성립한다. 공분산도
같은 방식으로 $P = \Lambda^{-1} = \bar P - KH\bar P$ 가 나온다(문제 P1).

**그래서 무엇이 다른가.** 소거는 두 조각을 만든다 — 조건부 $p(x_0\mid x_1)$ 와 새 인자
$p(x_1,\dots)$. 필터는 조건부를 **버린다**. 버리면:

1. $x_0$ 을 다시 추정할 수 없다. 뒤늦게 루프 클로저가 들어와도 과거를 고칠 수 없다.
2. 비선형에서는 더 나쁘다. 조건부를 버린 시점의 **선형화 지점이 영구히 고정**된다. 새 정보로
   $x_0$ 의 추정이 좋아져도, 이미 Schur 보완에 들어간 $J_k(\hat x_0^{\text{old}})$ 는
   되돌릴 수 없다. 이것이 EKF-SLAM 비일관성의 기원이고 `c5-observability-consistency` 의 주제다.
3. 선형-가우시안에서는 1·2가 **추정값에 영향을 주지 않는다** — 소거는 정확하고 선형화가 없으므로
   필터의 마지막 상태 주변값 = 평활의 마지막 상태 주변값이다. 필터가 지는 것은 비선형 때문이다.

평활은 조건부를 전부 보관한다. 보관된 조건부를 역순으로 대입하는 것이 **역대입(back-substitution)**
이고, 선형-가우시안 체인에서 그것이 바로 Rauch-Tung-Striebel 평활기다(문제 P1).

### R5 — 공분산은 왜 근사인가

$\hat{\mathcal{X}}$ 에서 $-\log p$ 를 2차까지 전개하면 $-\log p(\mathcal{X}) \approx
\text{const} + \tfrac12 (\mathcal{X}-\hat{\mathcal{X}})^\top \Lambda (\mathcal{X}-\hat{\mathcal{X}})$
이므로 사후분포를 $\mathcal{N}(\hat{\mathcal{X}}, \Lambda^{-1})$ 로 읽는다(라플라스 근사).
$\Lambda^{-1}$ 전체를 만들 필요는 없다 — $\mathsf{R}$ 에서 필요한 블록만 역대입으로 뽑는다
(`dellaert2017-factor-graphs` §4). **[D1]**

이것이 근사인 이유는 두 가지다. ⓐ $h_k$ 가 비선형이면 사후분포는 가우시안이 아니고, 3차 이상
항이 무시되지 않는다. ⓑ MAP 점 자체가 **재매개화에 불변이 아니다** — $y = g(x)$ 로 좌표를
바꾸면 밀도가 $\lvert\partial g/\partial x\rvert^{-1}$ 배로 바뀌므로 최대점이 옮겨간다. 최소제곱
해(=MAP)는 "확률이 가장 높은 점"이라는 직관보다 약한 의미를 갖는다. 사후 평균은 이 문제가
없지만 계산이 비싸다. 문제 P5 에서 구체적인 예를 만든다.

## 증명 스케치

### R1 — MAP = 비선형 최소제곱

**가설** H1: $z_k = h_k(\mathcal{X}_k) + \epsilon_k$, $\epsilon_k\sim\mathcal{N}(0,\Sigma_k)$.
H2: $\{\epsilon_k\}$ 독립. H3: $\Sigma_k$ 가 $\mathcal{X}$ 와 무관하고 $\Sigma_k \succ 0$.
**결론** C: (2)의 두 $\arg$ 가 같은 집합이다.

**전략**: 단조 변환 불변성 — $\arg\max f = \arg\max (-\log f)^{-}$ 이고, $\mathcal{X}$ 에
상수인 항은 $\arg$ 를 바꾸지 않는다.

1. **곱을 합으로.** H2 로 (5)가 성립한다. H2 가 없으면 결합 가능도가 인자별로 쪼개지지 않고
   목적함수가 인자 그래프로 표현되지 않는다 — 그래프 자체가 H2 의 그림이다.
2. **$-\log$ 가 $\arg$ 를 보존.** $\log$ 는 $(0,\infty)$ 에서 강증가, $x\mapsto -x$ 는 강감소.
   따라서 $\arg\max_{\mathcal{X}} p = \arg\min_{\mathcal{X}} (-\log p)$. $p > 0$ 은 H1·H3 에서
   따라온다(가우시안 밀도는 어디서나 양수).
3. **상수 분리.** H3 로 (6)의 $c$ 가 $\mathcal{X}$ 와 무관하다. $\Sigma_k \succ 0$ 이
   $\Sigma_k^{-1}$ 과 $\log\det\Sigma_k$ 의 존재를 준다.
4. **결론.** 남은 항이 (2)의 우변이고, 2·3단계가 $\arg$ 의 보존을 보증한다. C.

**가설을 지우면**: H3 를 빼면 3단계가 무너져 (7)의 $\log\det$ 항이 남는다. H1 의 가우시안을
빼면 2단계는 살아 있지만 남는 것이 제곱합이 아니다 — 예를 들어 Cauchy 잡음은
$\sum_k \log(1 + \lVert e_k\rVert^2/c^2)$ 를 주고, 이것이 `c5-robust-global-estimation` 의
M-estimator 다. 즉 **최소제곱은 가우시안 가정의 다른 이름**이다.

(생략: 밀도의 가측성과 $\arg\min$ 의 존재. 콤팩트한 정의역이나 강제성(coercivity)이 없으면
$\arg\min$ 이 비어 있을 수 있다 — 게이지 자유도가 있는 포즈 그래프가 실제 예다. R3 의
가설을 지우면 항을 참조.)

### R3 — 가우시안 소거 = Schur 보완

**가설** H1: $\Lambda \succ 0$ (대칭 양정부호). H2: $x = (x_1, x_{\mathcal{S}})$ 로 분할하고
$\Lambda = \begin{bmatrix}\Lambda_{11} & \Lambda_{1\mathcal{S}}\\ \Lambda_{\mathcal{S}1} &
\Lambda_{\mathcal{S}\mathcal{S}}\end{bmatrix}$.
**결론** C1: $p(x) = p(x_1\mid x_{\mathcal{S}})\,q(x_{\mathcal{S}})$ 로 정확히 쪼개지고,
$q$ 의 정보행렬은 (4)의 Schur 보완이다. C2: $\int p(x)\,dx_1 = q(x_{\mathcal{S}})$ — 즉
**소거가 만든 새 인자가 주변분포다**.

**전략**: $x_1$ 에 대한 완전제곱식(completing the square). 적분이 아니라 대수로 끝난다.

1. **$\Lambda_{11}$ 의 가역성.** H1 에서 주 소행렬은 양정부호이므로 $\Lambda_{11}\succ 0$,
   따라서 $\Lambda_{11}^{-1}$ 이 존재한다.
2. **$x_1$ 항을 모은다.** 지수부를 $f(x) = \tfrac12 x^\top\Lambda x - \eta^\top x$ 라 쓰면
   $$
   f = \tfrac{1}{2}x_1^\top\Lambda_{11}x_1 + x_1^\top(\Lambda_{1\mathcal{S}}x_{\mathcal{S}} - \eta_1)
     + \tfrac{1}{2}x_{\mathcal{S}}^\top\Lambda_{\mathcal{S}\mathcal{S}}x_{\mathcal{S}}
     - \eta_{\mathcal{S}}^\top x_{\mathcal{S}}.
   $$
3. **완전제곱.** $\mu := -\Lambda_{11}^{-1}(\Lambda_{1\mathcal{S}}x_{\mathcal{S}} - \eta_1)$ 로 두면
   $$
   \tfrac{1}{2}x_1^\top\Lambda_{11}x_1 + x_1^\top(\Lambda_{1\mathcal{S}}x_{\mathcal{S}} - \eta_1)
     = \tfrac{1}{2}\lVert x_1 - \mu\rVert^2_{\Lambda_{11}^{-1}}
       - \tfrac{1}{2}(\Lambda_{1\mathcal{S}}x_{\mathcal{S}} - \eta_1)^\top\Lambda_{11}^{-1}
         (\Lambda_{1\mathcal{S}}x_{\mathcal{S}} - \eta_1).
   $$
   첫 항이 $p(x_1\mid x_{\mathcal{S}}) = \mathcal{N}(\mu, \Lambda_{11}^{-1})$ 를 준다 —
   **조건부의 정보행렬은 $\Lambda_{11}$ 이고 separator 에 의존하지 않는다.**
4. **남은 항을 정리.** 두 번째 항을 전개하고 $\Lambda_{\mathcal{S}1} = \Lambda_{1\mathcal{S}}^\top$
   을 쓰면
   $$
   f - \tfrac{1}{2}\lVert x_1 - \mu\rVert^2_{\Lambda_{11}^{-1}}
     = \tfrac{1}{2}x_{\mathcal{S}}^\top\big(\Lambda_{\mathcal{S}\mathcal{S}}
       - \Lambda_{\mathcal{S}1}\Lambda_{11}^{-1}\Lambda_{1\mathcal{S}}\big)x_{\mathcal{S}}
       - \big(\eta_{\mathcal{S}} - \Lambda_{\mathcal{S}1}\Lambda_{11}^{-1}\eta_1\big)^\top x_{\mathcal{S}}
       + \text{const},
   $$
   즉 (4)와 $\eta^{\mathrm{new}}_{\mathcal{S}} = \eta_{\mathcal{S}} -
   \Lambda_{\mathcal{S}1}\Lambda_{11}^{-1}\eta_1$. C1.
5. **주변화와의 동일성.** 3단계의 첫 항은 $x_1$ 에 대한 완전한 가우시안이므로
   $\int \exp(-\tfrac12\lVert x_1-\mu\rVert^2_{\Lambda_{11}^{-1}})dx_1 =
   \sqrt{(2\pi)^{d_1}/\det\Lambda_{11}}$ — $x_{\mathcal{S}}$ 와 **무관한 상수**다. 따라서
   적분은 $q(x_{\mathcal{S}})$ 를 상수배만 바꾼다. C2.
6. **fill-in.** (4)의 새 인자는 $\mathcal{S}(x_1)$ 의 모든 쌍에 비영 블록을 만든다 — separator 가
   **클리크(clique)** 가 된다. 소거 순서가 희소성을 결정하고, 최적 순서를 찾는 것은 NP-난해다.
   이 줄이 `c5-sparsity-isam` 의 출발점이다.

**가설을 지우면**: H1 의 양정부호성을 빼면 1단계가 무너진다. 실제로 일어나는 경우가 **게이지
자유도**다 — 상대 측정만 있는 포즈 그래프에서는 전체를 강체 변환해도 $\chi^2$ 가 변하지 않아
$\Lambda$ 가 특이하고($SE(2)$ 는 영공간 3차원, $SE(3)$ 는 6차원), 한 번도 관측되지 않은
랜드마크를 소거하려 하면 $\Lambda_{11}$ 이 특이하다. 해법은 앵커(anchor) 인자를 넣어 게이지를
고정하거나 의사역행렬로 푸는 것이다. 재현 과제에서 앵커를 빼고 돌려 보면 즉시 확인된다.

(생략: Schur 보완의 양정부호성 보존 — $\Lambda\succ0 \Rightarrow
\Lambda_{\mathcal{S}\mathcal{S}} - \Lambda_{\mathcal{S}1}\Lambda_{11}^{-1}\Lambda_{1\mathcal{S}}\succ 0$.
문제 P2 에서 증명한다.)

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R4)** (13)·(14)에서 출발해 ⓐ 공분산 갱신 $P = \bar P - K H \bar P$ 를 유도하고,
ⓑ 선형-가우시안 체인에서 $x_{0:K}$ 를 시간 순서로 소거한 뒤 조건부를 역순으로 대입하면
Rauch-Tung-Striebel 평활기 $\hat x_i^{s} = \hat x_i + C_i(\hat x_{i+1}^{s} - \bar x_{i+1})$,
$C_i = P_i F_i^\top \bar P_{i+1}^{-1}$ 가 나옴을 보여라.
*해답 스케치*: ⓐ $P = \Lambda^{-1}$ 에 (14)를 쓰고 $\Lambda^{-1} = \bar P - \bar P H^\top
(H\bar PH^\top+R)^{-1}H\bar P$ 를 확인한다(Sherman-Morrison-Woodbury). ⓑ $x_i$ 소거 시의 조건부가
$p(x_i\mid x_{i+1}) = \mathcal{N}(\hat x_i + C_i(x_{i+1}-\bar x_{i+1}), \cdot)$ 형태임을 R3 의
3단계 $\mu$ 식에서 읽고, $x_{i+1}$ 에 평활값을 대입한다. 핵심은 **역대입이 곧 평활**이라는 점이다.

**P2 (증명, ★★, R3)** $\Lambda \succ 0$ 이면 Schur 보완 $\Lambda_{\mathcal{S}\mathcal{S}} -
\Lambda_{\mathcal{S}1}\Lambda_{11}^{-1}\Lambda_{1\mathcal{S}} \succ 0$ 임을 보여라. 이어서
**소거 순서를 바꿔도 최종 주변분포가 같다**는 것을 보여라.
*전략 + 핵심 부등식*: 전자는 $v \ne 0$ 에 대해 $x = (-\Lambda_{11}^{-1}\Lambda_{1\mathcal{S}}v,\, v)$
를 $x^\top\Lambda x > 0$ 에 넣는다. 후자는 주변분포의 정의 $\int p\,dx_{\text{소거}}$ 가 적분
순서에 의존하지 않음(Fubini)과 R3 의 C2 를 결합한다 — 즉 **수치(희소성·비용)는 순서에 의존하지만
답은 의존하지 않는다**. 전개는 숨긴다.

**P3 (계산, ★, R1·R3·R5)** 1차원 포즈 그래프: 변수 $x_1,x_2,x_3\in\mathbb{R}$, 인자 네 개 —
사전분포 $x_1 = 0\ (\sigma=0.1)$, 오도메트리 $x_2-x_1 = 1.00\ (\sigma=0.1)$,
$x_3-x_2 = 1.00\ (\sigma=0.1)$, 루프 클로저 $x_3-x_1 = 2.30\ (\sigma=0.2)$.
ⓐ $\Lambda$ 와 $\eta$, ⓑ MAP 해, ⓒ $\chi^2$, ⓓ 각 변수의 주변 표준편차를 구하라. ⓔ $x_1^\ast$ 이
**정확히** 0 인 이유를 한 문단으로 설명하라.
*정답*: ⓐ $\Lambda = \begin{bmatrix}225 & -100 & -25\\ -100 & 200 & -100\\ -25 & -100 & 125\end{bmatrix}$,
$\eta = (-157.5,\ 0,\ 157.5)^\top$. ⓑ $x^\ast = (0,\ 1.05,\ 2.10)^\top$.
ⓒ $\chi^2 = 1.5$ (잔차 $(0,\ 0.5,\ 0.5,\ -1.0)$). ⓓ $(0.1,\ 0.13540064,\ 0.15275252)$
$=(0.1, \sqrt{11/600}, \sqrt{7/300})$. 허용오차 $10^{-8}$.
검산: $\Lambda x^\ast = \eta$ 를 직접 확인하고, $x_1$ 을 소거한 주변 정보행렬
$\frac{1}{9}\begin{bmatrix}1400 & -1000\\ -1000 & 1100\end{bmatrix}$ 에서 $(x_2,x_3)$ 를 다시 풀어
같은 값이 나오는지 본다.
*ⓔ의 채점 포인트*: $(x_1,\ d_1 = x_2-x_1,\ d_2 = x_3-x_2)$ 로 재매개화하면 사전분포는 $x_1$ 에만,
나머지 세 인자는 $(d_1,d_2)$ 에만 닿아 **야코비안이 블록 대각**이 된다. 게이지와 형상이 분리되므로
루프 클로저의 불일치가 $x_1$ 으로 흐르지 않는다. "우연히 그렇다"는 미달.

**P4 (구현, ★★, R2·R3)** 재현 과제의 $\Lambda$ 에 대해 **직접 변수 소거 솔버**를 쓰라.
주어진 순서대로 (4)를 반복 적용해 조건부를 쌓고, 역순으로 역대입해 해를 얻는다.
*루브릭*: ⓐ 해가 `numpy.linalg.solve` 결과와 $10^{-9}$ 이내로 일치 ⓑ 조건부를 보관해 역대입이
실제로 동작 ⓒ 소거 순서를 바꿔도 해가 같고($10^{-9}$), 생성되는 비영 원소 수는 달라짐을 수치로
제시 ⓓ 앵커 인자를 제거하면 $\Lambda_{11}$ 또는 최종 블록이 특이해져 실패함을 재현하고, 영공간의
차원을 수치 랭크로 보고($SE(2)$ 포즈 그래프이므로 3).

**P5 (반례, ★★, R1·R5)** "MAP 해는 가장 확률이 높은 상태이므로 좌표계 선택과 무관하다"는 주장이
틀렸음을 보여라. ⓐ 1차원에서 $x\sim$ (어떤 비가우시안 사후분포)일 때 $y = x^3$ 로 재매개화하면
MAP 이 옮겨가는 구체적 예를 하나 만들고, ⓑ 2차원 거리-방위(range-bearing) 측정 하나만 있는
랜드마크에서 직교좌표 MAP 과 극좌표 MAP 이 다른 점을 수치로 제시하라.
*성질 체크리스트*: ⓐ 밀도 변환 $p_Y(y) = p_X(g^{-1}(y))\lvert dg^{-1}/dy\rvert$ 에서 야코비안 항이
최대점을 옮긴다는 것을 쓴다. ⓑ 사후 **평균**은 양쪽에서 같은 물리적 점을 주지만(측정 가능한 양의
변환이므로) MAP 은 그렇지 않다는 대조가 있어야 통과. "비선형이라서"만 쓰면 미달.

**P6 (논문, ★★, R2)** `dellaert2006-square-root-sam` 의 3-5절을 읽고 ⓐ 저자들이 정보행렬 대신
제곱근 정보행렬을 쓰는 논거를 (9)와 연결해 세 문장 이내로, ⓑ 논문의 실행 시간 표를 재현하는 데
필요한 정보 중 **빠진 것** 세 개를 쓰라. ⓒ 2026년 기준으로 이 논문의 결론 중 더는 성립하지 않는
것이 있는가?
*루브릭*: ⓐ 조건수 제곱과 희소 QR 의 점진적 갱신 가능성을 짚으면 통과. ⓑ 변수 순서 알고리즘의
구체적 설정, 하드웨어·BLAS 구현, 데이터셋의 루프 클로저 통계 중 셋 정도면 통과. ⓒ "증분
갱신은 iSAM2 의 Bayes tree 가 대체했다", "현대 희소 Cholesky(CHOLMOD) 가 많은 문제에서 희소 QR 보다
빠르다" 중 하나를 근거와 함께 쓰면 우수.

## 논문 읽기

**필독 2편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Dellaert & Kaess, "Factor Graphs for Robot Perception" (2017, Foundations and Trends in
   Robotics)** — 역할: `서베이(survey)`. <https://doi.org/10.1561/2300000043> (2-4절)
   추가 질문: ⓐ 이 글의 Bayes net 과 인자 그래프 사이의 변환을 R3 의 "조건부 + 새 인자" 분해와
   대응시켜 쓰면? ⓑ 저자들이 주변 공분산을 구하는 절차가 왜 $\Lambda^{-1}$ 전체를 만들지 않아도
   되는가?
2. **Dellaert & Kaess, "Square Root SAM" (2006, IJRR)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1177/0278364906072768> (3-5절)
   추가 질문: ⓐ (9)의 조건수 제곱이 실제 포즈 그래프에서 몇 자리 손실로 나타나는가 — 재현 과제의
   $\kappa(\Lambda)$ 를 쓰라. ⓑ 저자들이 비교한 베이스라인은 공정하게 튜닝되었는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, 30초 이내, 메모리 200MB 이하.
numpy + scipy.sparse 만 쓴다.

**입력 데이터**는 아래 생성 스크립트가 만든다(고정 시드). 외부 데이터셋이 필요 없다.

```python
"""c5-factor-graphs-map 재현 과제: 2랩 SE(2) 포즈 그래프 생성기."""

import numpy as np

SEED = 20261112
SIGMA_ODOM = np.array([0.02, 0.02, 0.01])
SIGMA_LOOP = np.array([0.05, 0.05, 0.02])
SIGMA_ANCHOR = np.array([1e-3, 1e-3, 1e-3])


def wrap(a):
    """각도를 (-pi, pi] 로 접는다."""
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def rot(t):
    """2x2 회전행렬."""
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]])


def between(xi, xj):
    """잡음 없는 상대 측정 T_i^{-1} T_j 를 (dx, dy, dtheta) 좌표로."""
    return np.array([*(rot(xi[2]).T @ (xj[:2] - xi[:2])), wrap(xj[2] - xi[2])])


def make_graph(laps=2, per_lap=50, radius=5.0, every=10):
    """2랩 원형 궤적의 참값, 간선, 잡음 섞인 측정값."""
    rng = np.random.default_rng(SEED)
    n = laps * per_lap
    ang = 2.0 * np.pi * np.arange(n) / per_lap
    gt = np.column_stack([radius * np.cos(ang), radius * np.sin(ang), wrap(ang + np.pi / 2)])
    edges = [(i, i + 1, SIGMA_ODOM) for i in range(n - 1)]
    edges += [(i, i + per_lap, SIGMA_LOOP) for i in range(0, per_lap, every)]
    meas = [between(gt[i], gt[j]) + s * rng.standard_normal(3) for i, j, s in edges]
    return gt, edges, np.array(meas)
```

$n = 100$ 개 포즈, 간선 $104$ 개(오도메트리 99 + 루프 클로저 5), 앵커 인자 1 개 →
잔차 행 $M = 3\cdot104 + 3 = 315$, 변수 $N = 300$, 자유도 $M - N = 15$.

**해야 할 일.** 변수는 $x_i = (p_{x,i}, p_{y,i}, \theta_i) \in \mathbb{R}^3$ (좌표로 직접
매개화한다 — 이것이 틀린 선택인 이유는 `c5-manifold-estimation` 에서 다룬다). 잔차는 g2o 의
`EdgeSE2` 와 같은 형태로

$$
r_{ij}(x) = \begin{bmatrix}
  R(\bar\theta_{ij})^\top\big(R(\theta_i)^\top(p_j - p_i) - \bar p_{ij}\big) \\
  \mathrm{wrap}(\theta_j - \theta_i - \bar\theta_{ij})
\end{bmatrix} \in \mathbb{R}^3 \tag{15}
$$

로 두고, 야코비안은 해석적으로 쓴다. $d := p_j - p_i$, $\widehat{1} :=
\begin{bmatrix}0 & -1\\ 1 & 0\end{bmatrix}$ 일 때

$$
\frac{\partial r_{1:2}}{\partial p_i} = -R_{\bar\theta}^\top R_{\theta_i}^\top, \quad
\frac{\partial r_{1:2}}{\partial \theta_i} = -R_{\bar\theta}^\top \widehat{1} R_{\theta_i}^\top d, \quad
\frac{\partial r_{1:2}}{\partial p_j} = R_{\bar\theta}^\top R_{\theta_i}^\top, \quad
\frac{\partial r_3}{\partial(\theta_i,\theta_j)} = (-1,\, +1). \tag{16}
$$

($\partial R_{\theta}^\top/\partial\theta = -\widehat{1}R_\theta^\top$ 에서 나온다. 직접 전개해
확인하라.) 초기 추측은 **루프 클로저를 쓰지 않은 추측 항법(dead reckoning)** 이다: 앵커 포즈를
참값에 두고 오도메트리만 누적한다.

**수용 기준 — 네 조건을 모두 만족해야 통과다.**

1. **희소·조밀 일치**: `scipy.sparse.linalg.spsolve` 로 푼 해와 $\Lambda$ 를 조밀 행렬로 만들어
   `numpy.linalg.solve` 로 푼 해가 $\lVert x_{\text{sparse}} - x_{\text{dense}}\rVert_\infty < 10^{-9}$.
   (참조 구현의 실측값은 $8.9\times10^{-16}$ 이다.)
2. **수렴**: $\chi^2$ 가 단조 감소하고(허용 $10^{-9}$), 8회 이내에
   $\lVert\delta\rVert_\infty < 10^{-13}$ 에 도달하며, 최종 $\lVert\eta\rVert_\infty =
   \lVert A^\top b\rVert_\infty < 10^{-8}$.
3. **참조값**: 위 시드에서 $\chi^2$ 수열이 $296.0248 \to 16.7131 \to 15.3077 \to \cdots$ 이고
   최종 $\chi^2 = 15.3077 \pm 10^{-3}$. 자유도 15 이므로 $\chi^2/\mathrm{dof} = 1.02$ —
   **잡음 모델이 생성 과정과 일치한다는 증거**다. 이 비가 1 에서 크게 벗어나면 $\Sigma$ 설정이나
   화이트닝을 의심한다.
4. **정확도와 야코비안**: ATE(위치 RMSE)가 초기 $0.3790$ 에서 최종 $0.1031$ 로 개선된다
   ($\pm10^{-3}$). 해석 야코비안이 중앙 차분과 일치한다 — 단계 $h = 10^{-5}$ 에서
   $\max\lvert J_{\text{analytic}} - J_{\text{fd}}\rvert < 10^{-7}$.

**비교 대상**: ⓐ 조밀 `numpy.linalg.solve` (조건 1 이 그 자체로 베이스라인이다) ⓑ 루프 클로저를
무시한 추측 항법(ATE 0.3790). 선택: `scipy.optimize.least_squares(method="trf", jac=...)` 로
같은 잔차를 풀어 $\chi^2$ 가 $10^{-6}$ 이내로 일치하는지 확인.

**보고할 수치**: $\chi^2$ 수열, 반복 횟수, $\kappa(\Lambda)$ (참조 구현 $1.73\times10^6$ —
(9)에 따라 $\kappa(A)\approx1.3\times10^3$), $\Lambda$ 의 비영 원소 수(참조 1736/90000)와
Cholesky 인자의 비영 원소 수(참조 3396). 마지막 두 수의 비가 **fill-in** 이고
`c5-sparsity-isam` 의 주제다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 초기 $\chi^2$ 가 $10^4$ 이상 | 각도 랩핑 누락 — $\theta_j-\theta_i-\bar\theta$ 가 $2\pi$ 를 넘음 | 잔차의 3번째 성분 히스토그램을 그려 $\pm\pi$ 밖의 값을 찾는다 |
| `spsolve` 가 특이행렬 경고 | 앵커 인자 누락 → 게이지 자유도 3차원 | $\Lambda$ 의 최소 고윳값 3개를 본다(≈0). 영공간 벡터가 전역 평행이동·회전인지 확인 |
| $\chi^2$ 가 증가하는 반복이 있다 | GN 의 2차 항 무시(R2 의 실패 모드) 또는 야코비안 부호 오류 | 중앙 차분으로 야코비안을 검증하고, 그래도 증가하면 LM 감쇠를 넣는다 |
| $\chi^2/\mathrm{dof} \gg 1$ | $\Sigma$ 를 측정 생성과 다르게 설정, 또는 화이트닝에 $\sigma$ 대신 $\sigma^2$ 사용 | 가중치가 $1/\sigma$ 인지 확인한다(공분산이 아니라 **표준편차**로 나눈다) |
| 희소·조밀 해가 $10^{-6}$ 수준으로만 일치 | $\Lambda$ 를 비대칭으로 쌓았거나 `spsolve` 에 CSR 을 넘겨 LU 로 풀림 | $\lVert\Lambda-\Lambda^\top\rVert_\infty$ 를 출력하고 CSC 로 넘긴다 |

## 열린 문제

- **(열린 문제) 학습된 이분산 불확실성을 인자 그래프에 정합하게 넣는 방법** — (7)의
  $\log\det\Sigma(\mathcal{X})$ 항 때문에, 신경망이 출력한 공분산을 그대로 가중치로 쓰면 목적함수가
  "잡음을 크게 보고하는" 해로 끌린다. 현재 접근은 학습 단계에서 음의 로그 가능도로 공분산을
  보정하거나([Levine, control as inference 관점](https://arxiv.org/abs/1805.00909)) 사후 보정으로
  분포 없는 보장을 붙이는 것이다([conformal prediction](https://arxiv.org/abs/2107.07511),
  [system-level OOD](https://arxiv.org/abs/2212.14020)). 비어 있는 자리: 백엔드 추정의 **일관성**을
  보존하면서 학습된 공분산을 쓰는 설계 규칙.
- **(열린 문제) MAP 이 재매개화에 불변이 아닌 문제를 실무에서 어떻게 처리하는가** — R5ⓑ 는
  "최소제곱 해"가 좌표 선택에 의존한다는 뜻이고, 매니폴드 변수에서는 재추적(retraction) 선택까지
  더해진다. 사후 평균이나 변분 근사는 불변이지만 비싸다. 현재 접근:
  [Barfoot SER ch.6](https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf) 의 변분 추론,
  [micro Lie theory](https://arxiv.org/abs/1812.01537) 의 좌/우 규약 정리. 비어 있는 자리:
  로보틱스 규모에서 MAP 의 좌표 의존성이 실제로 정확도에 얼마나 영향을 주는지에 대한 정량적 연구.
- **(열린 문제) 정확 추론의 treewidth 장벽** — R3 의 6단계가 말하는 것은 비용이 소거 순서의
  fill-in, 즉 그래프의 treewidth 로 결정된다는 것이다. 밀집 루프 클로저가 많은 장기 운용
  그래프에서는 treewidth 가 커지고 정확 추론이 불가능해진다. 현재 접근: 희소화·주변화로 그래프를
  줄이는 방법과 [증분 재선형화](https://doi.org/10.1177/0278364911430419), 그리고
  [장기 SLAM 서베이의 지도 수명 논의](https://arxiv.org/abs/1606.05830). 비어 있는 자리:
  정보 손실을 정량적으로 보장하면서 treewidth 를 상계로 유지하는 희소화.

## 개념 점검

`rc quiz c5-factor-graphs-map` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c5-factor-graphs-map-quiz
questions:
  - id: q1
    type: single
    prompt: "측정 공분산이 상태에 의존해 $\\Sigma_k = \\Sigma_k(\\mathcal{X})$ 가 되면, 올바른 MAP 목적함수에 추가로 나타나는 항은?"
    choices:
      - "$-\\log p(\\mathcal{Z})$"
      - "$\\frac{1}{2}\\log\\det\\Sigma_k(\\mathcal{X})$"
      - "$\\frac{p_k}{2}\\log 2\\pi$"
      - "추가 항은 없다 — 가중치만 바뀐다"
    answer: 1
    explanation: "(6)의 상수 $c$ 에 들어 있던 $\\frac12\\log\\det\\Sigma_k$ 가 더는 상수가 아니다. 이 항을 빼고 제곱합만 최소화하면 공분산을 크게 보고해 모든 잔차를 0 으로 만드는 퇴화 해로 끌린다."
    concept: { front: "MAP = 최소제곱이 깨지는 가정", back: "$\\Sigma$ 가 상태에 의존하면 $\\frac12\\log\\det\\Sigma(\\mathcal{X})$ 항이 남는다 — 가중 최소제곱만으로는 틀린다" }
  - id: q2
    type: truefalse
    prompt: "선형-가우시안 계에서 칼만 필터가 준 마지막 상태의 추정값은, 같은 데이터에 대한 전체 평활(MAP) 해의 마지막 상태 주변값과 정확히 일치한다."
    answer: true
    explanation: "선형-가우시안에서 소거(주변화)는 정확하고 선형화 오차가 없다. 필터는 과거의 조건부를 버리기만 하므로 마지막 상태의 주변분포는 평활과 같다. 필터가 지는 것은 비선형성(재선형화 불가) 때문이다."
    concept: { front: "필터 vs 평활 (선형-가우시안)", back: "마지막 상태 주변값은 동일 — 차이는 과거를 고칠 수 없다는 것과, 비선형에서 선형화 지점이 영구히 고정된다는 것" }
  - id: q3
    type: single
    prompt: "가우시안 인자 그래프에서 $x_1$ 을 소거할 때, separator $\\mathcal{S}$ 에 새로 붙는 인자의 정보행렬은?"
    choices:
      - "$\\Lambda_{\\mathcal{S}\\mathcal{S}} + \\Lambda_{\\mathcal{S}1}\\Lambda_{11}^{-1}\\Lambda_{1\\mathcal{S}}$"
      - "$\\Lambda_{\\mathcal{S}\\mathcal{S}} - \\Lambda_{\\mathcal{S}1}\\Lambda_{11}^{-1}\\Lambda_{1\\mathcal{S}}$"
      - "$\\Lambda_{11} - \\Lambda_{1\\mathcal{S}}\\Lambda_{\\mathcal{S}\\mathcal{S}}^{-1}\\Lambda_{\\mathcal{S}1}$"
      - "$\\Lambda_{\\mathcal{S}\\mathcal{S}}^{-1} - \\Lambda_{11}^{-1}$"
    answer: 1
    explanation: "$\\Lambda_{11}$ 에 대한 Schur 보완이다((4)). 완전제곱식에서 $x_1$ 항을 떼어낼 때 빼지는 양이고, $x_1$ 을 적분해 없앤 주변분포의 정보행렬과 같은 행렬이다."
    concept: { front: "가우시안 소거의 새 인자", back: "$\\Lambda_{\\mathcal{S}\\mathcal{S}} - \\Lambda_{\\mathcal{S}1}\\Lambda_{11}^{-1}\\Lambda_{1\\mathcal{S}}$ — Schur 보완. separator 가 클리크가 되면서 fill-in 이 생긴다" }
  - id: q4
    type: single
    prompt: "제곱근 정보행렬 $\\mathsf{R}$ 을 $\\Lambda = A^\\top A$ 를 만들지 않고 QR 로 직접 얻는 수치적 이유는?"
    choices:
      - "QR 이 Cholesky 보다 항상 연산량이 적다"
      - "$\\kappa(\\Lambda) = \\kappa(A)^2$ 이므로 $\\Lambda$ 를 만드는 순간 조건수가 제곱된다"
      - "$\\Lambda$ 는 희소하지 않지만 $A$ 는 희소하다"
      - "QR 은 야코비안을 필요로 하지 않는다"
    answer: 1
    explanation: "특잇값이 제곱되므로 $\\kappa(\\Lambda)=\\kappa(A)^2$ 이다((9)). $\\kappa(A)=10^8$ 이면 배정밀도에서 $\\Lambda$ 는 수치적으로 특이하지만 $A$ 는 멀쩡하다. 연산량으로는 희소 Cholesky 가 더 빠른 경우가 많다."
    concept: { front: "제곱근 정보 형태를 쓰는 이유", back: "$\\kappa(\\Lambda)=\\kappa(A)^2$ — 정보행렬을 만들면 유효 자릿수가 절반이 된다" }
  - id: q5
    type: truefalse
    prompt: "상대 측정만으로 된 $SE(2)$ 포즈 그래프에서는 앵커 인자 없이도 $\\Lambda$ 가 가역이므로 소거를 진행할 수 있다."
    answer: false
    explanation: "전체를 강체 변환해도 모든 상대 잔차가 변하지 않으므로 $\\Lambda$ 의 영공간이 3차원($SE(2)$ 의 차원)이다. 앵커(사전분포) 인자를 넣어 게이지를 고정하거나 의사역행렬로 풀어야 한다. $SE(3)$ 에서는 영공간이 6차원이다."
    concept: { front: "포즈 그래프의 게이지 자유도", back: "상대 측정만 있으면 $\\Lambda$ 의 영공간 = 전역 강체 변환 ($SE(2)$ 3차원, $SE(3)$ 6차원) — 앵커 인자가 필요하다" }
```

## 이 단계 공부법

1. **그래프를 먼저 그린다 (30분)** — 재현 과제의 그래프(100 포즈, 99 오도메트리, 5 루프 클로저,
   앵커 1)를 손으로 그리고, $\Lambda$ 의 비영 패턴을 종이에 칠해 본다. 어느 간선이 어느 블록을
   채우는지 보이면 R3 의 fill-in 이 당연해진다.
2. **R1 을 백지에서 다시 쓴다 (45분)** — (5)→(6)→(2) 를 책을 덮고 재구성한다. 세 가정 중
   **어느 줄에서 어느 가정을 썼는지**를 여백에 적는다. (7)의 $\log\det$ 항이 왜 거기 있는지
   말할 수 있으면 이 레슨의 절반이 끝났다.
3. **소거를 손으로 한 번 한다 (60분)** — P3 의 $3\times3$ 문제에서 $x_1$ 을 종이로 소거해
   $\frac19\begin{bmatrix}1400&-1000\\-1000&1100\end{bmatrix}$ 를 직접 얻고, 역대입으로 $x_1$ 을
   복원한다. Barfoot SER ch.3 을 **같은 결과의 다른 표기**로 대조해 읽는다.
4. **필터를 최소제곱으로 다시 유도한다 (60분)** — (11)→(13) 을 쓰고 (14)를 손으로 증명한다.
   "필터는 평활의 특수한 소거 순서"라는 문장을 자기 말로 쓸 수 있게 되면 R4 가 끝났다.
   SER ch.3.3(배치 vs 재귀)을 같이 본다.
5. **재현 과제를 분기 없이 먼저 틀리게 돌린다 (135분)** — 각도 랩핑을 **빼고** 돌려 초기
   $\chi^2$ 가 폭발하는 것을 보고, 앵커를 **빼고** 돌려 특이행렬을 보고, 야코비안의 부호를
   하나 뒤집어 $\chi^2$ 가 증가하는 것을 본다. 그 다음 고친다. 진단표의 다섯 줄을 직접 만들어
   보는 것이 목표다.
6. **논문은 수치를 손에 들고 읽는다 (120분)** — 재현 과제의 $\kappa(\Lambda) = 1.73\times10^6$ 과
   fill-in 비(1736 → 3396)를 메모한 상태로 Square Root SAM 3-5절을 읽는다. 논문의 주장이
   내 그래프에서 몇 자리로 나타나는지 대조하면 읽는 속도가 달라진다. 논문당 1페이지 노트는
   **반드시** 쓴다.
7. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제" 세 개 중 하나를 골라 왜 아직 안 풀렸는지
   한 문단으로 쓴다.

**통과 기준**: 백지에서 (2)와 (4)를 유도할 수 있고, (14)를 증명할 수 있고, 재현 과제의 네 조건을
모두 만족하는 코드를 갖고 있고, 논문 2편의 노트가 있다.
