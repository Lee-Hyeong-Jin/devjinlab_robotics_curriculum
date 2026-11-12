---
id: c7-bundle-adjustment
title: N-view 와 번들 조정
summary: >-
  재투영 오차의 정규방정식이 왜 희소한지, Schur 보완이 왜 근사가 아니라 정확한 소거인지를
  블록 LDL 분해와 관성(inertia) 보존으로 증명하고, 번들 조정의 게이지 자유도 7 을 생성자까지
  유도한다. 자기 보정(self-calibration)의 가해성을 절대 쌍대 이차곡면의 선형계 계수로 세고,
  임계 운동열(critical motion sequence)에서 그 계수가 어떻게 포화하는지 수치로 확인한다.
objectives:
  - 번들 조정의 정규방정식에서 카메라·점 블록이 블록 대각임을 잔차의 의존 구조로부터 유도할 수 있다.
  - Schur 보완이 정확한 소거임을 블록 LDL 분해로 증명하고 축소 비용의 Hessian 으로 해석할 수 있다.
  - 축소 행렬 $S$ 의 희소성이 카메라 공동가시성 그래프와 같음을 보이고 그 밀도를 측정할 수 있다.
  - 번들 조정의 게이지 자유도가 7 임을 생성자 7개로 제시하고 수치적으로 영공간임을 확인할 수 있다.
  - 자기 보정의 선형 제약 수를 세어 필요한 시점 수를 도출하고, 임계 운동열에서 계수가 포화함을 보일 수 있다.
prerequisites: [c7-two-view-geometry]
difficulty: 5
estimated_minutes: 720
tags: [perception, bundle-adjustment, schur-complement, gauge-freedom, self-calibration, research]
activities:
  - id: c7-bundle-adjustment-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 110
  - id: c7-bundle-adjustment-papers
    kind: paper
    title: 필독 논문 2편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 130
  - id: c7-bundle-adjustment-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 2 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: c7-bundle-adjustment-reproduction
    kind: reproduction
    title: 재현 과제 — BAL 데이터셋에서 Schur 보완 LM 번들 조정 (R3)
    estimated_minutes: 280
  - id: c7-bundle-adjustment-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 20
papers:                                # 서지는 curriculum/robotics-research/papers.yaml
  - { id: triggs2000-bundle-adjustment, required: true, role: standard, note: "§4, §9" }
  - { id: agarwal2010-rome,             required: true, role: standard }
  - { id: rosen2019-se-sync,                            role: seminal  }
  - { id: kaess2012-isam2,                              role: seminal  }
resources:
  - title: "Hartley & Zisserman, Multiple View Geometry in Computer Vision (2nd ed.)"
    url: https://www.robots.ox.ac.uk/~vgg/hzbook/
    kind: book
    note: >-
      ch.18 (N-view computational methods), ch.19 (auto-calibration), App. 6 (iterative estimation).
      이 레슨의 1순위 교재.
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.10 (pose-and-point estimation). 희소 구조와 Schur 보완을 추정 이론 쪽 표기로 본다. 전문 PDF 무료.
  - title: "Bundle Adjustment in the Large datasets (BAL)"
    url: https://grail.cs.washington.edu/projects/bal/
    kind: dataset
    note: 재현 과제의 입력 데이터. 카메라 모델과 파일 포맷이 이 페이지에 정의되어 있다.
  - title: "Ceres Solver"
    url: https://github.com/ceres-solver/ceres-solver
    kind: code
    note: >-
      권장 비교 대상. `examples/bundle_adjuster.cc` 가 같은 BAL 파일을 받는다. 비용 정의는
      $\frac{1}{2}\sum\lVert r\rVert^2$ 로 이 레슨과 같다.
  - title: "GTSAM"
    url: https://github.com/borglab/gtsam
    kind: code
    note: 권장. 팩터 그래프 쪽 구현. 같은 문제를 다른 소거 순서로 푸는 비교에 쓴다.
---

# N-view 와 번들 조정

## 전제와 기호

권장 선수는 같은 모듈의 `c7-two-view-geometry`(에피폴라 기하와 자세 복원)와
`r0-sparse-linear-algebra`(희소 Cholesky 와 소거 순서), `r0-numerical-optimization`
(Gauss–Newton·신뢰영역)이다. 어느 것도 잠겨 있지 않다. 이 레슨은 다음을 전제한다:

- 선형대수: 블록 행렬 연산, Cholesky, 양정치성, Sylvester 의 관성 법칙(없으면 증명 스케치에서
  한 줄 인용으로 쓴다), 희소 행렬의 nnz 개념.
- 최적화: Gauss–Newton 과 Levenberg–Marquardt, 정규방정식, 신뢰영역 감쇠.
- 리 군: 포즈를 $SE(3)$ 로 보고 우 야코비안으로 증분을 취하는 것(`c1-so3-se3-exponential`).
- 사영기하: 사영 복원의 모호성 $\{P_iH^{-1}, HX_j\}$ 와 무한면(plane at infinity)의 뜻.
  절대 쌍대 이차곡면은 이 레슨에서 필요한 만큼만 쓴다.

표기(C7 모듈 규약을 잇는다. $i$ 는 카메라, $j$ 는 점, $(i,j) \in \mathcal{O}$ 는 관측):

| 기호 | 뜻 |
|---|---|
| $n_c$, $n_p$, $\lvert\mathcal{O}\rvert$ | 카메라 수, 점 수, 관측 수 |
| $\theta_i \in \mathbb{R}^{d_c}$ | 카메라 $i$ 의 매개변수. 포즈만이면 $d_c = 6$, BAL 모델은 $d_c = 9$ (포즈 6 + $f, k_1, k_2$) |
| $X_j \in \mathbb{R}^3$ | 점 $j$ 의 좌표 |
| $z_{ij} \in \mathbb{R}^2$ | 관측된 이미지 좌표, $r_{ij} = \pi(\theta_i, X_j) - z_{ij}$ |
| $A_{ij} = \partial r_{ij}/\partial\theta_i$ | $2 \times d_c$ |
| $B_{ij} = \partial r_{ij}/\partial X_j$ | $2 \times 3$ |
| $H = J^\top J = \begin{bmatrix} B & E \\ E^\top & C\end{bmatrix}$ | 정규방정식 행렬. $B$ 는 카메라, $C$ 는 점 블록 |
| $S = B - EC^{-1}E^\top$ | 축소 카메라 행렬(reduced camera matrix), Schur 보완 |
| $\Omega^* $ | 절대 쌍대 이차곡면(absolute dual quadric), $4\times4$ 대칭, 랭크 3 |
| $\omega^* = KK^\top$ | 절대 원뿔의 쌍대 이미지(DIAC) |

**비용 규약**: $C(\Theta,\mathcal{X}) = \frac{1}{2}\sum_{(i,j)\in\mathcal{O}}\lVert r_{ij}\rVert^2$.
$\frac{1}{2}$ 를 붙이는 것은 Ceres 와 같은 규약이고, 이 레슨이 보고하는 비용 수치는 모두 이
정의다. 재투영 RMS 는 $\sqrt{\sum\lVert r_{ij}\rVert^2 / \lvert\mathcal{O}\rvert}$ (픽셀).

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (정규방정식의 희소 구조) [D2]** — $r_{ij}$ 가 $\theta_i$ 와 $X_j$ **하나씩만** 의존하므로
  $B$ 는 카메라마다 $d_c \times d_c$ 블록의 블록 대각, $C$ 는 점마다 $3\times3$ 블록의 블록
  대각이고, $E$ 는 관측 $(i,j)$ 마다 정확히 하나의 $d_c\times3$ 블록을 갖는다. 따라서
  $$\operatorname{nnz}(B) = d_c^2 n_c,\quad \operatorname{nnz}(C) = 9n_p,\quad
    \operatorname{nnz}(E) = 3d_c\lvert\mathcal{O}\rvert. \tag{1}$$
- **R2 (Schur 보완은 근사가 아니다) [D3]** — $C \succ 0$ 이면 $H$ 는 블록 LDL 분해
  $$H = \begin{bmatrix} I & EC^{-1} \\ 0 & I\end{bmatrix}
        \begin{bmatrix} S & 0 \\ 0 & C\end{bmatrix}
        \begin{bmatrix} I & 0 \\ C^{-1}E^\top & I\end{bmatrix} \tag{2}$$
  를 갖는다. 그러므로 ⓐ $H\delta = (v, w)$ 의 해는 $S\delta_c = v - EC^{-1}w$ 와
  $\delta_p = C^{-1}(w - E^\top\delta_c)$ 로 **정확히** 같고, ⓑ $H \succ 0 \iff S \succ 0$
  (관성 보존), ⓒ $S$ 는 점을 소거한 **축소 비용의 Hessian** 이다.
- **R3 (축소 행렬의 희소성 = 공동가시성) [D2]** — $S_{ik} = B_{ik} - \sum_j E_{ij}C_{jj}^{-1}E_{kj}^\top$
  이므로 $S$ 의 $(i,k)$ 블록은 **카메라 $i$ 와 $k$ 가 같은 점을 하나라도 함께 볼 때만** 0 이
  아니다. 즉 $S$ 의 희소 패턴은 카메라 공동가시성 그래프의 인접행렬이다.
- **R4 (게이지 자유도는 정확히 7) [D2]** — 재투영 비용은 세계좌표계의 **닮음 변환**(similarity)
  에 불변이다. 생성자는
  $$
  \begin{aligned}
  \text{회전}(\omega):&\quad \delta\theta_i^{\mathrm{rot}} = -\omega,\;
    \delta t_i = 0,\; \delta X_j = \omega \times X_j, \\
  \text{평행이동}(a):&\quad \delta\theta_i^{\mathrm{rot}} = 0,\;
    \delta t_i = -R_i a,\; \delta X_j = a, \\
  \text{스케일}(s):&\quad \delta\theta_i^{\mathrm{rot}} = 0,\;
    \delta t_i = t_i,\; \delta X_j = X_j
  \end{aligned} \tag{3}
  $$
  이고 7개가 독립이다. 따라서 $J$ 의 영공간은 7차원, $H$ 의 랭크 결손은 7 이다
  (내부 파라미터를 자유로 두어도 닮음 게이지는 그대로 7 이다).
- **R5 (자기 보정의 가해성) [D2]** — 사영 복원 $\{P_i\}$ 에서 절대 쌍대 이차곡면은
  $\omega_i^* = P_i\Omega^*P_i^\top$ 를 만족한다. 비틀림 0, 종횡비 1, 주점이 원점이라는
  가정은 시점마다 **선형 제약 4개**를 주므로, $\Omega^*$ 의 10개 성분(스케일 제외 9)을
  정하려면 $4N \ge 9$, 즉 $N \ge 3$ 시점이 필요하다. 이 계수는 **필요조건일 뿐**이고,
  임계 운동열에서는 시점을 늘려도 랭크가 8 에서 포화한다.

## 유도

### R1 — 왜 블록 대각인가

잔차 $r_{ij}$ 는 카메라 $i$ 와 점 $j$ 에만 의존한다. 따라서 $k \ne i$ 이면
$\partial r_{ij}/\partial\theta_k = 0$ 이고, 정규방정식의 카메라-카메라 블록은

$$H_{\theta_i\theta_k} = \sum_{(m,j)\in\mathcal{O}}
  \left(\frac{\partial r_{mj}}{\partial\theta_i}\right)^\top
  \left(\frac{\partial r_{mj}}{\partial\theta_k}\right)$$

에서 각 항이 $m = i$ 와 $m = k$ 를 동시에 요구하므로 $i \ne k$ 에서 0 이다. 점-점 블록도
같은 이유로 $j \ne l$ 에서 0 이다. 남는 것은

$$B_{ii} = \sum_{j:(i,j)\in\mathcal{O}} A_{ij}^\top A_{ij}, \quad
  C_{jj} = \sum_{i:(i,j)\in\mathcal{O}} B_{ij}^\top B_{ij}, \quad
  E_{ij} = A_{ij}^\top B_{ij} \tag{4}$$

이고 우변 벡터는 $v_i = -\sum_j A_{ij}^\top r_{ij}$, $w_j = -\sum_i B_{ij}^\top r_{ij}$ 다.
(1)의 nnz 공식은 (4)에서 바로 읽힌다 — $B$ 는 $n_c$ 개의 $d_c\times d_c$ 블록,
$C$ 는 $n_p$ 개의 $3\times3$ 블록, $E$ 는 관측마다 $d_c\times3$ 블록 하나.

측정값(BAL `problem-49-7776-pre.txt`, $n_c = 49$, $n_p = 7776$, $\lvert\mathcal{O}\rvert = 31843$,
$d_c = 9$): $\operatorname{nnz}(B) = 81\cdot49 = 3969$, $\operatorname{nnz}(C) = 9\cdot7776 = 69984$,
$\operatorname{nnz}(E) = 27\cdot31843 = 859761$. 전체
$\operatorname{nnz}(H) = 3969 + 69984 + 2\cdot859761 = 1\,793\,475$ 이고 $n = 23769$ 이므로
밀도는 $3.17\times10^{-3}$ 다. **$H$ 를 조밀하게 담으면 $23769^2\cdot8$ 바이트 = 4.21 GiB** 이고,
희소로 담으면 20 MB 대다. 이 한 줄이 번들 조정 구현의 전부를 설명한다.

**가정이 깨지는 곳**: 잔차가 두 카메라에 동시에 의존하면(예: 카메라 간 상대 포즈 사전분포,
IMU 사전적분 팩터, 롤링 셔터의 이웃 프레임 보간) $B$ 는 더 이상 블록 대각이 아니다. 그래도
Schur 는 성립하지만 $B$ 의 소거 순서가 문제가 되고, 그때부터는 일반 희소 Cholesky 와
소거 순서(COLAMD/AMD) 영역이다(`r0-sparse-linear-algebra`).

### R2 — Schur 보완 (유도)

$$\begin{bmatrix} B & E \\ E^\top & C\end{bmatrix}
  \begin{bmatrix}\delta_c\\\delta_p\end{bmatrix}
  = \begin{bmatrix}v\\w\end{bmatrix} \tag{5}$$

의 둘째 줄에서 $\delta_p$ 를 풀면 ($C$ 가 가역이라 가정)

$$\delta_p = C^{-1}\big(w - E^\top\delta_c\big) \tag{6}$$

이고 첫째 줄에 대입하면 $B\delta_c + EC^{-1}w - EC^{-1}E^\top\delta_c = v$, 즉

$$\underbrace{\left(B - EC^{-1}E^\top\right)}_{S}\delta_c = v - EC^{-1}w. \tag{7}$$

$C$ 가 블록 대각이므로 $C^{-1}$ 은 $3\times3$ 블록을 하나씩 역행렬 취하는 것이고 비용은
$O(n_p)$ 다 — 여기가 번들 조정이 싸지는 지점이다. (7)의 크기는 $d_cn_c$ 로, 원래 문제의
$d_cn_c + 3n_p$ 보다 압도적으로 작다.

**축소 비용으로 읽기**: 2차 모형 $q(\delta) = \frac12\delta^\top H\delta - \delta^\top g$ 를
$\delta_p$ 에 대해 먼저 최소화하면 그 최소점이 정확히 (6)이고, 대입한 결과는

$$\tilde{q}(\delta_c) = \tfrac12\delta_c^\top S\delta_c - \delta_c^\top(v - EC^{-1}w) + \text{const}$$

다. 즉 **$S$ 는 점을 정확히 최소화해 지운 뒤 남는 비용의 Hessian**이고, Schur 보완은
"점을 대충 무시하는 것"이 아니라 "점에 대해 정확히 최적화한 것"이다. 이 해석이 R2 ⓐ·ⓒ 이고,
증명 스케치에서 ⓑ 까지 묶는다.

**비용 회계**: $S$ 를 만드는 비용은 $\sum_j m_j^2$ ($m_j$ = 점 $j$ 를 보는 카메라 수)에
블록 곱 비용을 곱한 것이고, $S$ 를 분해하는 비용은 $O((d_cn_c)^3/3)$ 다. BAL-49 에서
$\dim S = 441$ 이므로 $2.86\times10^7$ flops 인데, $H$ 를 조밀하게 분해하면
$4.48\times10^{12}$ flops 다 — **$1.57\times10^5$ 배**. 측정값: numpy 로 야코비안 생성 +
Schur 스텝 한 번이 0.634 초, LM 40 반복이 약 30 초.

**가정이 깨지는 곳**: $C \succ 0$ 이 깨지는 가장 흔한 경우는 **한 시점에서만 보인 점**이다 —
관측 1개는 잔차 2개뿐이라 $C_{jj} = B_{ij}^\top B_{ij}$ 의 랭크가 최대 2 이고 $3\times3$
행렬이 특이해진다. 해법은 그런 점을 제거하거나 LM 감쇠 $C + \lambda D_C$ 에 기대는 것이다.
(BAL 의 `-pre` 파일은 미리 걸러져 있다 — 측정값: 점당 관측 수 최소 2, 최대 29, 평균 4.10,
관측 2개인 점이 3449개. 특이한 $3\times3$ 블록은 0 개이고 블록 조건수 중앙값은 290.)
반대 방향의 함정은 $n_c \gg$ 인 경우다: 도시 규모에서 $\dim S$ 가 $10^5$ 급이 되면 (7)을
조밀 분해할 수 없고, 반복법(CG)과 전처리자가 필요해진다 — 필독 2 의 주제다.

### R3 — 축소 행렬의 희소성

(7)의 블록 성분을 쓰면

$$S_{ik} = B_{ik} - \sum_{j} E_{ij}\,C_{jj}^{-1}\,E_{kj}^\top \tag{8}$$

이고, $E_{ij} \ne 0$ 은 $(i,j) \in \mathcal{O}$ 와 동치다. 따라서 $i \ne k$ 에서 $S_{ik} \ne 0$
인 것은 **$\exists j$ 로 $(i,j), (k,j) \in \mathcal{O}$**, 즉 두 카메라가 같은 점을 함께 볼 때다.
$S$ 의 희소 패턴 = 카메라 공동가시성 그래프의 인접행렬(+대각).

측정값(BAL-49): 공동가시성 그래프 밀도 0.835, $S$ 의 밀도 0.835 — **같은 수**다. 49개 카메라가
서로 대부분 겹쳐 보므로 $S$ 는 실질적으로 조밀하고, 그래도 $441\times441$ 이라 아무 문제가 없다.
스트리트뷰·인터넷 사진 규모에서는 이 그래프가 희소해지고, 그 희소성을 전처리자로 쓰는 것이
필독 2 의 visibility-based preconditioner 다.

### R4 — 게이지 자유도 7

세계좌표계를 닮음 변환으로 바꿔도 모든 재투영이 그대로임을 먼저 확인한다. 카메라 좌표는
$X_c = R_iX_j + t_i$ 이고 투영은 $X_c$ 의 **방향**만 보므로:

- **회전** $Q \in SO(3)$: $X_j \mapsto QX_j$, $R_i \mapsto R_iQ^\top$, $t_i \mapsto t_i$.
  그러면 $R_iQ^\top\cdot QX_j + t_i = R_iX_j + t_i$ — 불변.
- **평행이동** $a$: $X_j \mapsto X_j + a$, $t_i \mapsto t_i - R_ia$.
  $R_i(X_j+a) + t_i - R_ia = R_iX_j + t_i$ — 불변.
- **스케일** $s > 0$: $X_j \mapsto sX_j$, $t_i \mapsto st_i$.
  $sR_iX_j + st_i = sX_c$ 이고 투영은 $-X_{c,xy}/X_{c,z}$ 이므로 $s$ 가 약분된다 — 불변.
  (내부 파라미터 $f, k_1, k_2$ 는 건드리지 않으므로 BAL 모델에서도 그대로 불변이다.)

$\epsilon$ 으로 미분해 생성자를 읽으면 (3)이다. 회전의 경우 $Q = \exp(\hat\omega\epsilon)$ 에서
$R_i \mapsto R_i\exp(-\hat\omega\epsilon)$ 이므로 **우 증분**이 $-\epsilon\omega$ 이고
(이것이 (3)의 $\delta\theta_i^{\mathrm{rot}} = -\omega$), 점은
$QX_j = X_j + \epsilon\,\omega\times X_j + O(\epsilon^2)$ 다. 7개 생성자는 일반 구성에서
서로 독립이므로 $\dim\ker J = 7$, $\operatorname{rank} H = n - 7$.

측정값(합성 문제: 카메라 6개 × 점 40개, $f$ 고정, $n = 6\cdot6 + 3\cdot40 = 156$):
$J$ 의 특이값은 $\sigma_{149} = 4.7078$ 에서 $\sigma_{150} = 4.37\times10^{-8}$ 로
**$1.08\times10^{8}$ 배 떨어진다** — 랭크 결손이 정확히 7 이다. (3)의 생성자 $g$ 는
$\lVert Jg\rVert/(\lVert J\rVert_F\lVert g\rVert) = 0$ (기계 정밀도)을 만족하고, 생성자가 만드는
부분공간과 수치적 7차원 영공간 사이의 최대 주각은 $9.1\times10^{-8}$ 도다. BAL-49 의 수렴점에서도
7개 생성자 모두 $\lVert Jg\rVert/(\lVert J\rVert_F\lVert g\rVert) \le 4.5\times10^{-12}$ 였다.

**고정 방법 네 가지**: ⓐ **게이지 고정** — 카메라 0 의 $d_c$ 중 포즈 6 개를 상수로 두고
거리 하나(예: 카메라 0-1 사이 기준선 길이)를 1 로 고정한다. 총 7 개를 지운다.
ⓑ **자유 네트워크(free network)** — $H$ 의 Moore–Penrose 유사역행렬을 써서 게이지 방향으로
움직이지 않는 최소 노름 스텝을 취한다(Triggs §9 의 inner constraints).
ⓒ **사전분포·Tikhonov** — 포즈에 약한 사전분포를 더해 $H + \Lambda$ 를 가역으로 만든다.
ⓓ **LM 감쇠에 기대기** — $H + \lambda D$ 는 $\lambda > 0$ 이면 항상 가역이다.

**가정이 깨지는 곳(중요)**: ⓓ 때문에 **게이지를 고정하지 않아도 번들 조정은 "돌아간다"** —
그래서 많은 구현이 이 문제를 모른 채 수렴한다. 깨지는 것은 두 가지다. ① $\lambda \to 0$ 에서
스텝 노름이 게이지 방향으로 발산하므로 수렴 말미에 스텝이 요동친다(측정값: BAL-49 에서
$\lambda$ 가 $10^{-10}$ 아래로 내려가면 비용 감소가 $10^{-6}$ 상대 이하인데 스텝 노름은 줄지
않는다). ② **공분산이 게이지에 의존한다** — 유사역행렬로 뽑은 매개변수 공분산은 어떤 게이지를
골랐는지에 따라 달라지고, 그 값을 "지도의 불확실성"으로 보고하면 틀린다. 게이지 불변인 것은
상대 포즈·재투영 같은 양이다(Triggs §9). 이 구분을 모르고 보고된 BA 공분산은 비교 불가능하다.

### R5 — 자기 보정의 가해성

사영 복원은 $H \in PGL(4)$ 만큼 모호하다: $\{P_i, X_j\}$ 와 $\{P_iH^{-1}, HX_j\}$ 는 같은
이미지를 만든다. 유클리드 복원으로 올라가려면 $H$ 를 정해야 하고, 그 정보를 **내부 파라미터의
구조**에서 가져오는 것이 자기 보정이다. 장치는 절대 쌍대 이차곡면

$$\Omega^* = H\,\operatorname{diag}(1,1,1,0)\,H^\top \tag{9}$$

이다. 유클리드 좌표계에서 무한면의 쌍대가 $\operatorname{diag}(1,1,1,0)$ 이므로 (9)는 "무한면과
절대 원뿔이 사영 좌표계에서 어디로 갔는지"를 담은 $4\times4$ 대칭·랭크 3 행렬이다. 핵심 관계는

$$\omega_i^* = K_iK_i^\top = P_i\,\Omega^*\,P_i^\top \tag{10}$$

다 ($P_i$ 는 사영 복원의 카메라). (10)은 $\Omega^*$ 의 10개 성분에 **선형**이다.

내부 파라미터 가정을 (10)의 좌변에 넣으면 제약이 나온다. 비틀림 0 · 종횡비 1 · 주점이 원점이면
$K = \operatorname{diag}(f, f, 1)$ 이므로 $\omega^* \propto \operatorname{diag}(f^2, f^2, 1)$,
즉 시점마다

$$\omega^*_{12} = 0,\quad \omega^*_{13} = 0,\quad \omega^*_{23} = 0,\quad
  \omega^*_{11} - \omega^*_{22} = 0 \tag{11}$$

네 개의 선형 제약이다($f$ 는 소거된다 — 시점마다 달라도 된다). $N$ 시점이면 $4N$ 개 식,
미지수는 $\Omega^*$ 의 10 성분에서 스케일 하나를 뺀 9 이므로

$$4N \ge 9 \;\Longrightarrow\; N \ge 3. \tag{12}$$

측정값($f = 500$, 임의 사영 변환으로 사영 좌표계로 옮긴 뒤 $4N\times10$ 계수행렬의 랭크):

| 운동 | $N=2$ | $N=3$ | $N=4$ | $N=6$ | $\Omega^*$ 복원 오차 |
|---|---|---|---|---|---|
| 일반 운동 | 랭크 8 | **랭크 9** | 랭크 9 | 랭크 9 | $N\ge3$ 에서 $5\times10^{-16}$ |
| 순수 평행이동 | 랭크 7 | 랭크 8 | 랭크 8 | 랭크 8 | $0.35 \sim 1.0$ (실패) |
| 고정 축 회전 + 임의 평행이동 | 랭크 7 | 랭크 8 | 랭크 8 | 랭크 8 | $0.92 \sim 0.98$ (실패) |
| 순수 회전 ($t_i = 0$) | 랭크 5 | 랭크 5 | 랭크 5 | 랭크 5 | 1.4 (실패) |

일반 운동에서 $N = 3$ 에 랭크가 9 로 차고 (12)와 정확히 맞는다. 덧붙여, 선형해는 $\Omega^*$ 의
**랭크 3 제약을 걸지 않았는데도** 복원된 $\Omega^*$ 의 네 번째 특이값이 $10^{-16}$ 수준으로
나왔다 — 일반 운동에서는 데이터가 랭크 조건을 스스로 함의한다. 임계 운동열에서는 그렇지 않다.

**가정이 깨지는 곳 — 임계 운동열(critical motion sequence)**: 위 표의 아래 세 줄이다.
순수 평행이동과 고정 축 회전에서는 시점을 6개로 늘려도 랭크가 **8 에서 포화**해 1-매개변수
모호성이 남는다. (12)의 부등식은 **필요조건일 뿐이며 운동이 일반적이라는 가정을 숨기고 있다.**
순수 회전은 더 나쁘다: $t_i = 0$ 이면 $P_i = K[R_i\,\vert\,0]$ 의 넷째 열이 0 이라 (10)이
$\Omega^*$ 의 좌상 $3\times3$ 블록(6 성분)만 건드리고, 측정 랭크는 5 다. 이 경우 자기 보정은
$\Omega^*$ 가 아니라 무한 호모그래피 $H_\infty = KR_iK^{-1}$ 의 켤레 구조로 풀어야 한다
(MVG ch.19 **[D0]**). 요약: **"3시점이면 자기 보정이 된다"는 문장은 운동이 일반적일 때만
참이고, 로봇의 전형적 운동(평면 주행, 고정 축 선회)이 바로 그 예외다.**

## 증명 스케치

### R2 — Schur 보완의 정확성과 관성 보존

**가설** H1: $H = \begin{bmatrix} B & E \\ E^\top & C\end{bmatrix}$ 는 대칭. H2: $C$ 는 가역.
**결론** C1: (2)의 분해가 성립한다. C2: (5)의 해는 (6)·(7)과 정확히 같다.
C3: $C \succ 0$ 이면 $H \succ 0 \iff S \succ 0$.

**전략**: 블록 소거를 **합동 변환**(congruence)으로 적고 Sylvester 의 관성 법칙을 쓴다.

1. **C1 (직접 곱셈)**: $L = \begin{bmatrix} I & EC^{-1} \\ 0 & I\end{bmatrix}$,
   $D = \begin{bmatrix} S & 0 \\ 0 & C\end{bmatrix}$ 로 두고 곱한다.
   $$LD = \begin{bmatrix} S & EC^{-1}C \\ 0 & C\end{bmatrix} = \begin{bmatrix} S & E \\ 0 & C\end{bmatrix},$$
   $$LDL^\top = \begin{bmatrix} S & E \\ 0 & C\end{bmatrix}
     \begin{bmatrix} I & 0 \\ C^{-1}E^\top & I\end{bmatrix}
     = \begin{bmatrix} S + EC^{-1}E^\top & E \\ E^\top & C\end{bmatrix} = H,$$
   마지막 등호는 $S = B - EC^{-1}E^\top$ 의 정의다. $\square$
2. **C2**: $L$ 은 단위 상삼각이라 $\det L = 1 \ne 0$. (5)는 $LDL^\top\delta = g$ 이고
   $L^{-1} = \begin{bmatrix} I & -EC^{-1}\\0&I\end{bmatrix}$ 이므로
   $DL^\top\delta = L^{-1}g = (v - EC^{-1}w,\; w)$. 첫 블록이 $S(\delta_c) = v - EC^{-1}w$
   (7)이고 둘째 블록이 $C(C^{-1}E^\top\delta_c + \delta_p) = w$, 즉 (6)이다. 근사가 아니라
   **같은 선형계를 다른 순서로 소거한 것**이다. $\square$
3. **C3**: (2)는 $H = LDL^\top$ 꼴이므로 $H$ 와 $D$ 는 합동이고, Sylvester 의 관성 법칙에서
   양·음·영 고유값의 개수가 같다. $D$ 는 블록 대각이라
   $D \succ 0 \iff S\succ0 \text{ 그리고 } C\succ0$. $C\succ0$ 를 가정했으므로
   $H\succ0 \iff S\succ0$. $\square$
4. **왜 이것이 실무에서 중요한가**: LM 은 $H + \lambda D_H$ 를 푼다. 감쇠를 $B$ 와 $C$ 에
   **각각** 더한 뒤 Schur 를 적용하면 (2)가 그대로 성립하므로 축소 계는 여전히 양정치이고
   Cholesky 가 안전하다. 반대로 $S$ 를 만든 **뒤에** 감쇠를 더하면 그것은 다른 문제를 푸는
   것이다(신뢰영역의 반지름이 점 매개변수에 걸리지 않는다). 구현 버그가 숨는 전형적 자리다.
5. **가설을 지우면**: H2($C$ 가역)가 깨지면 (2) 자체가 정의되지 않는다. 한 시점에서만 보인
   점이 정확히 그 경우이고, 그때 $S$ 를 계산하면 `inf`/`nan` 이 조용히 퍼진다. 또 $C \succ 0$
   가 아니라 준정치면 C3 의 동치가 한쪽 방향만 남는다 — $S \succ 0$ 이어도 $H$ 가 특이할 수
   있다(게이지가 바로 그 경우: $H$ 는 랭크 결손 7 인데 감쇠를 넣으면 $S$ 는 양정치다).

생략한 기술적 단계: Sylvester 의 관성 법칙. 임의의 가역 $L$ 에 대해 $A$ 와 $LAL^\top$ 의
관성이 같다는 표준 결과로, 선형대수 교재 또는 `r0-linear-algebra-decompositions` 를 본다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★, R1)** (4)를 유도하고 (1)의 nnz 공식을 쓰라. BAL `problem-49-7776-pre.txt`
($n_c=49$, $n_p=7776$, $\lvert\mathcal{O}\rvert=31843$, $d_c=9$)에 대해
$\operatorname{nnz}(B), \operatorname{nnz}(C), \operatorname{nnz}(E), \operatorname{nnz}(H)$ 와
$H$ 의 밀도를 계산하라.
*해답 스케치*: $r_{ij}$ 의 의존 변수가 둘뿐이라는 사실만 쓴다. 정답은
$3969,\; 69984,\; 859761,\; 1\,793\,475$, 밀도 $3.17\times10^{-3}$.

**P2 (증명, ★★★, R2)** $C \succeq 0$ 이지만 특이할 때 C3 의 동치가 어느 방향으로 깨지는지
정확히 쓰고, 유사역행렬로 정의한 일반화 Schur 보완 $S = B - EC^{+}E^\top$ 에 대해 어떤 추가
조건($\operatorname{range}$ 조건)이 있으면 C2 가 여전히 성립하는지 보여라.
*전략과 핵심 부등식*: $H \succeq 0$ 와 $\operatorname{range}(E^\top) \subseteq
\operatorname{range}(C)$ 를 가정하고 $LDL^\top$ 을 유사역행렬로 다시 쓴다. 핵심은
$CC^{+}E^\top = E^\top$ 이 성립해야 2단계의 소거가 정보 손실 없이 된다는 점이다. 반례로
$\operatorname{range}$ 조건이 깨지는 $2\times2$ 블록 예를 만들면 한쪽 방향이 무너지는 것을 본다.

**P3 (계산, ★, R2·R3)** BAL-49 에 대해 ⓐ $H$ 를 조밀하게 담는 데 필요한 메모리,
ⓑ $\dim S$, ⓒ $S$ 와 $H$ 의 조밀 Cholesky flop 비, ⓓ $S$ 의 예상 밀도를 구하라.
*정답*: ⓐ $23769^2\cdot8 = 4.52\times10^9$ B $= 4.21$ GiB. ⓑ $9\cdot49 = 441$.
ⓒ $(441^3/3)/(23769^3/3) = 2.86\times10^7 / 4.48\times10^{12} = 6.4\times10^{-6}$
(즉 $1.57\times10^5$ 배 싸다). ⓓ 카메라 공동가시성 밀도와 같다 — 이 파일에서는 0.835.
허용오차 5%. 검산: 실제로 $S$ 를 만들어 `(abs(S)>0).mean()` 을 재면 0.835 가 나와야 한다.

**P4 (유도, ★★, R4)** (3)의 생성자 7개를 직접 유도하라. 그 다음, 카메라 0 의 포즈 6개와
"카메라 0-1 기준선 길이 = 1" 을 고정하면 게이지가 **정확히** 제거됨을, 고정된 매개변수를 지운
야코비안의 랭크로 논증하라. 내부 파라미터를 자유로 두어도 7 이 변하지 않는 이유를 한 줄로 쓰라.
*해답 스케치*: $X_c$ 가 세계 닮음 변환에 불변임을 보이고 $\epsilon$ 으로 미분한다. 회전은
$R_i\exp(-\hat\omega\epsilon)$ 에서 우 증분을 읽는다. 랭크 논증은 "7차원 영공간과 고정한
7개 좌표축이 횡단(transversal)"임을 쓰는 것이다. 내부 파라미터는 닮음 변환이 건드리지 않으므로
불변성 자체가 그대로다.

**P5 (계산, ★★, R5)** (11)의 셈을 다음 세 경우로 바꿔 필요한 최소 시점 수를 구하라.
ⓐ 비틀림 0 만 가정 ⓑ 비틀림 0 + 종횡비 1 ⓒ 모든 내부 파라미터가 **미지이지만 모든 시점에서
동일**. 각 경우 시점당 제약 수와 미지수 수를 명시하라.
*정답*: ⓐ 시점당 1 식, 미지수 9 → $N \ge 9$. ⓑ 시점당 2 식 → $N \ge 5$.
ⓒ 미지수는 $\Omega^*$ 의 9 개가 아니라 $\{H\text{의 무한면 } \pi_\infty (3), K (5)\} = 8$ 이고
시점쌍마다 Kruppa 식 2개 → $2\cdot\binom{N}{2} \ge 8$ 에서 $N \ge 3$ (셈으로는 3, 실제로는
퇴화 때문에 더 필요할 수 있다). 허용오차 없음(정수). 검산: ⓑ 를 수치로 확인하면
$2N\times10$ 행렬의 랭크가 $N = 5$ 에서 9 가 되어야 한다. **주의**: 이 셈은 모두 필요조건이고,
문헌의 정확한 결과(예: ⓐ 에서 8시점으로 충분하다는 논의)는 추가 대수 구조를 쓴다 — 셈만으로
"충분"을 주장하지 않는 것이 이 문제의 요점이다.

**P6 (구현, ★★★, R1·R2·R3)** Schur 보완을 쓰는 LM 번들 조정을 구현해 재현 과제의 다섯
조건을 통과시켜라.
*루브릭*: ⓐ BAL 카메라 모델의 $p = -P/P_z$ 부호를 맞춰 초기 비용이 참조값과 0.1% 이내
ⓑ 감쇠를 $B$ 와 $C$ 에 각각 더한 뒤 Schur 를 적용 ⓒ $C^{-1}$ 을 $3\times3$ 블록 역행렬로
계산(전체 역행렬 금지) ⓓ $S$ 의 밀도를 공동가시성 밀도와 비교해 보고 ⓔ 비용이 단조 감소.

**P7 (반례, ★★, R5)** 시점을 아무리 늘려도 자기 보정이 안 되는 운동열을 **두 가지** 만들고,
$4N\times10$ 계수행렬의 랭크가 8 에서 포화함을 특이값으로 보여라. 그 다음 그 운동열에 아주
작은 일반 운동 성분을 섞으면 랭크가 9 로 올라가지만 **조건수가 나쁘다**는 것을 보여라.
*성질 체크리스트*: ⓐ 순수 평행이동과 고정 축 회전 두 경우 ⓑ $N = 2,3,4,6$ 에서 랭크
$7,8,8,8$ ⓒ 복원된 $\Omega^*$ 와 참값의 거리가 $O(1)$ ⓓ 섭동을 $\epsilon$ 으로 줄이면
$\sigma_9/\sigma_1 \to 0$ 이 $\epsilon$ 에 비례해 감소 ⓔ 왜 "랭크가 9 다"가 "복원이 된다"를
뜻하지 않는지 한 문단.

**P8 (논문, ★★, R2·R3)** Triggs et al. 2000 의 §4·§9 와 Agarwal et al. 2010 을 읽고,
$n_c$ 가 $10^5$ 급이 되면 이 레슨의 (7)이 왜 더 이상 쓸 수 없는지, 두 논문이 각각 어디서
갈라지는지 쓰라. 그리고 Agarwal et al. 의 타이밍 표를 재현하려 할 때 **빠져 있는 정보 3개**를
찾아라.
*루브릭*: "$\dim S$ 가 커져서"에 그치지 않고 ⓐ $S$ 를 명시적으로 만들 때의 메모리
ⓑ 공동가시성 그래프의 밀도가 규모와 함께 어떻게 변하는지 ⓒ 전처리자의 선택이 CG 반복 수에
주는 영향 중 두 가지 이상을 짚으면 통과. 누락 정보는 하드웨어·BLAS·수렴 판정 기준·초기값
생성 방식 중에서 구체적으로 든다.

## 논문 읽기

**필독 2편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.
서지와 권장 논문 전체 목록은 `rc papers c7-bundle-adjustment` 로 본다(코스 레지스트리
`curriculum/robotics-research/papers.yaml`, ADR 0014).

1. **Triggs, McLauchlan, Hartley & Fitzgibbon, "Bundle adjustment: a modern synthesis"
   (2000, Vision Algorithms: Theory and Practice)** — 역할: `표준(standard)`.
   <https://doi.org/10.1007/3-540-44480-7_21> (§4 희소성·Schur, §9 게이지 자유도가 핵심)
   추가 질문: ⓐ 저자들이 "게이지 고정은 공분산을 바꾸지만 추정값은 바꾸지 않는다"를 어떤
   논증으로 말하는가? 그 논증이 이 레슨의 R4 ⓑ 와 어떻게 맞물리는가? ⓑ 이 논문이 2000년에
   권하는 소거 순서와 오늘날 구현(Ceres·GTSAM)의 기본값은 어디서 다른가?
2. **Agarwal, Snavely, Seitz & Szeliski, "Bundle adjustment in the large" (2010, ECCV)**
   — 역할: `표준(standard)`. <https://doi.org/10.1007/978-3-642-15552-9_3>
   추가 질문: ⓐ 명시적(explicit) Schur 와 암시적(implicit) Schur 의 메모리·연산 트레이드오프를
   이 레슨의 측정값(nnz 와 $\dim S$)으로 다시 계산하면 교차점은 어디인가? ⓑ 저자들이 쓰는
   전처리자가 왜 공동가시성 그래프에서 나오는가(R3)? ⓒ 보고된 수렴 판정 기준이 비용 기준인가
   스텝 기준인가, 그 선택이 표의 반복 수에 어떻게 영향을 주는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

**권장**: MVG ch.18–19, Barfoot SER ch.10, SE-Sync(열린 문제 1), iSAM2(열린 문제 3).

## 재현 과제

**티어 R3 (논문 수치 재현).** 계산 예산: 노트북 CPU 1코어, 40 반복에 5분 이내, 메모리 1 GiB
이내, numpy + scipy 만. 입력 데이터는 공개 BAL 데이터셋이다.

**입력**: `https://grail.cs.washington.edu/projects/bal/` 의 Ladybug
`problem-49-7776-pre.txt.bz2` ($n_c = 49$, $n_p = 7776$, $\lvert\mathcal{O}\rvert = 31843$).
카메라 모델은 그 페이지의 정의를 그대로 쓴다 — 특히 **$p = -P/P_z$ 의 음부호**와
$\text{pred} = f(1 + k_1r^2 + k_2r^4)p$ 를 틀리면 1번 조건에서 바로 걸린다.

아래 **다섯 조건을 모두** 만족해야 통과다. 참조값은 모두 이 레슨이 직접 측정한 것이다
(비용 규약 $\frac12\sum\lVert r\rVert^2$).

1. **파싱·모델 정확성**: 초기 비용이 $8.509125\times10^{5}$ 와 **0.1% 이내**, 초기 재투영
   RMS 가 $7.310557$ px 와 0.1% 이내.
2. **수렴**: 비용이 단조 감소하고, 40 반복 안에 최종 비용이 $1.334424\times10^{4}$ 와
   **1% 이내**, 최종 재투영 RMS 가 $0.915493$ px 와 1% 이내. (참조: 63.8배 감소.)
3. **Schur 가 정확한 소거임을 수치로**: 합성 소형 문제(카메라 $\le 8$, 점 $\le 50$)에서
   조밀 해 $\delta_{\text{full}}$ 와 Schur 해 $\delta_{\text{schur}}$ 가
   $\lVert\delta_{\text{full}} - \delta_{\text{schur}}\rVert/\lVert\delta_{\text{full}}\rVert
   < 10^{-8}$. (참조 측정값: $2.2\times10^{-10}$, $\dim H = 156 \to \dim S = 36$.)
4. **게이지 영공간**: 합성 문제에서 $J$ 의 특이값이
   $\sigma_{n-7}/\sigma_{n-6} > 10^{6}$ 로 끊기고(참조: $1.08\times10^{8}$), (3)의 생성자 7개가
   $\lVert Jg\rVert/(\lVert J\rVert_F\lVert g\rVert) < 10^{-8}$ 를 만족한다(참조: BAL-49 의
   수렴점에서 $\le 4.5\times10^{-12}$).
5. **희소성 회계**: $\operatorname{nnz}(B), \operatorname{nnz}(C), \operatorname{nnz}(E)$ 가
   (1)의 공식과 **정확히** 일치하고($3969,\ 69984,\ 859761$), $S$ 의 밀도가 카메라 공동가시성
   그래프의 밀도와 $10^{-12}$ 이내로 같다(참조: 둘 다 0.835).

**보고서에 반드시 쓸 것**: 최종 비용에 도달한 뒤에도 $\lambda$ 를 더 줄이면 스텝 노름이
게이지 방향으로 커지는 것(R4 의 실패 모드 ①). 게이지를 고정하지 않은 구현은 "수렴한 것처럼
보이지만" 매개변수 공분산을 보고할 수 없다.

**비교 대상**: ① Ceres Solver 의 `examples/bundle_adjuster` 를 같은 파일에 돌려 최종 비용을
비교한다(설치 가능하면). 비용 정의가 같으므로 같은 자리로 수렴해야 한다. ② 같은 문제를
**Schur 없이** scipy 의 희소 최소제곱(`scipy.sparse.linalg.lsqr` 또는
`scipy.optimize.least_squares(jac_sparsity=...)`)으로 풀어 반복당 시간을 비교한다.
③ 자기 소형 합성 문제의 조밀 해(조건 3).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 초기 비용이 참조값의 4배 근처 | $p = +P/P_z$ (음부호 누락) | 한 관측의 예측값을 손으로 계산해 관측과 부호를 맞춘다 |
| 초기 비용은 맞는데 발산한다 | 회전 야코비안의 우/좌 야코비안 혼동 | $\partial(RX)/\partial\theta = -R\hat{X}J_r(\theta)$ 를 유한차분과 대조 |
| `nan` 이 $C^{-1}$ 에서 나온다 | 관측 1개짜리 점, 또는 감쇠를 $C$ 에 더하지 않음 | 점당 관측 수 최소값과 $3\times3$ 블록의 최소 특이값을 출력 |
| 비용이 감소하다 요동한다 | $S$ 를 만든 뒤에 감쇠를 더했다 | 감쇠를 $B$, $C$ 에 각각 더하고 다시 돌린다 |
| 반복당 10초 이상 | $C$ 전체를 조밀 역행렬로 계산 | $3\times3$ 블록 역행렬로 바꾼다(`np.linalg.inv` 를 $(n_p,3,3)$ 에 적용) |
| 최종 비용이 참조값보다 10% 높다 | 수렴 전에 멈춤, 또는 $\lambda$ 업데이트가 너무 보수적 | 비용 이력을 로그 축으로 그려 평탄해졌는지 본다 |
| $S$ 의 밀도가 공동가시성과 다르다 | $E$ 의 블록 인덱싱 오류 | 관측 하나를 지우고 $S$ 의 해당 블록이 변하는지 본다 |

## 열린 문제

- **(열린 문제) 번들 조정의 전역 최적성 인증** — BA 는 비볼록이고, 수렴한 극소점이 전역해인지
  판정하는 방법이 없다. 포즈만 있는 문제(점 없음)에서는 쌍대 완화가 타이트한 조건과 인증서가
  알려졌지만([SE-Sync](https://arxiv.org/abs/1612.07386),
  [Carlone et al. 2015](https://arxiv.org/abs/1506.00746)), 점·내부 파라미터·강건 손실이 들어간
  완전한 BA 로 확장되지 않았다. 비어 있는 자리: 재투영 비용에 대한 실용적 전역성 인증서.
- **(열린 문제) 게이지 불변한 불확실성 보고 표준** — R4 가 보였듯 BA 가 내놓는 매개변수
  공분산은 게이지 선택에 의존한다. 하위 소비자(루프 폐쇄 판정, 경로 계획, 센서 융합)가 쓸 수
  있는 **게이지 불변 요약 통계**가 무엇이어야 하는지에 합의가 없고, 논문마다 다른 것을 보고한다.
  현재 접근: Triggs et al. 2000 §9 의 inner constraints,
  [iSAM2](https://doi.org/10.1177/0278364911430419) 의 주변화(marginalization). 비어 있는 자리:
  서로 다른 시스템의 보고값을 비교 가능하게 하는 규약.
- **(열린 문제) 점증적·분산 BA 의 오차 한계** — 실시간 시스템은 소거 순서를 재사용하고 오래된
  변수를 주변화해 정확한 BA 를 포기한다. 그렇게 생기는 편차에 **보장된 상한**이 없어서, 드리프트가
  근사 때문인지 데이터 때문인지 분리할 수 없다. 현재 접근:
  [iSAM2](https://doi.org/10.1177/0278364911430419) (정확 재선형화의 범위를 좁히는 방식),
  Agarwal et al. 2010 (비정확 Newton + CG). 비어 있는 자리: 근사 소거의 오차 한계.
- **(열린 문제) 학습된 가중치와 BA 의 결합** — 미분가능 BA 는 학습된 대응 가중치를 비용에
  넣는데, 그 가중치가 확률적으로 보정(calibrated)되어 있지 않으면 BA 의 공분산 해석이 무너진다.
  현재 접근: [DROID-SLAM](https://arxiv.org/abs/2108.10869) 의 학습된 신뢰도. 비어 있는 자리:
  학습 가중치를 관측 잡음 모델로 환산하는 보정 절차. 이 질문은
  `c7-learned-correspondence-slam` 에서 다시 나온다.

## 개념 점검

`rc quiz c7-bundle-adjustment` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c7-bundle-adjustment-quiz
questions:
  - id: q1
    type: single
    prompt: "번들 조정의 정규방정식에서 카메라 블록 $B$ 가 블록 대각인 이유는?"
    choices:
      - "카메라들이 서로 독립적으로 움직이기 때문"
      - "각 잔차가 카메라 하나에만 의존해 서로 다른 카메라의 편미분 곱이 항마다 0 이기 때문"
      - "Schur 보완을 적용한 결과이기 때문"
      - "LM 감쇠가 비대각 성분을 지우기 때문"
    answer: 1
    explanation: "$r_{ij}$ 는 $\\theta_i$ 와 $X_j$ 에만 의존한다. $(J^\\top J)_{\\theta_i\\theta_k}$ 의 각 항은 같은 잔차가 두 카메라에 동시에 의존할 것을 요구하므로 $i \\ne k$ 에서 0 이다. 카메라 간 사전분포(IMU 사전적분 등)를 넣으면 이 구조가 깨진다."
    concept: { front: "$B$, $C$ 가 블록 대각인 근거", back: "잔차 하나가 카메라 1개·점 1개에만 의존 → 교차 편미분 곱이 0. 카메라 간 팩터를 넣으면 깨진다" }
  - id: q2
    type: truefalse
    prompt: "Schur 보완은 점 매개변수를 무시하는 근사이므로, 정확한 Gauss-Newton 스텝보다 품질이 낮은 스텝을 준다."
    answer: false
    explanation: "Schur 보완은 블록 LDL 분해에서 나오는 **정확한** 소거다. $S\\delta_c = v - EC^{-1}w$ 와 $\\delta_p = C^{-1}(w - E^\\top\\delta_c)$ 를 합치면 원래 선형계의 해와 정확히 같다(측정값: 상대차 $2\\times10^{-10}$). $S$ 는 점에 대해 **정확히 최소화한** 축소 비용의 Hessian 이다."
    concept: { front: "Schur 보완은 근사인가", back: "아니다 — 블록 LDL 소거로 정확히 같은 해. $S$ 는 점을 정확히 최소화한 축소 비용의 Hessian" }
  - id: q3
    type: short
    prompt: "번들 조정에서 $J$ 의 영공간 차원(게이지 자유도)은 몇인가? (숫자만)"
    answer: ["7", "7개", "seven"]
    explanation: "세계좌표계의 닮음 변환 — 회전 3 + 평행이동 3 + 스케일 1 = 7 — 이 재투영을 바꾸지 않는다. 내부 파라미터를 자유로 두어도 닮음 게이지는 그대로 7 이다. 측정값: 합성 문제에서 $\\sigma_{n-7}/\\sigma_{n-6} = 1.08\\times10^8$."
    concept: { front: "번들 조정의 게이지 자유도", back: "7 = 회전 3 + 평행이동 3 + 스케일 1 (세계좌표계의 닮음 변환)" }
  - id: q4
    type: single
    prompt: "축소 카메라 행렬 $S = B - EC^{-1}E^\\top$ 의 희소 패턴은 무엇과 같은가?"
    choices:
      - "카메라-점 관측 행렬의 패턴"
      - "카메라 공동가시성 그래프의 인접행렬 (두 카메라가 같은 점을 함께 볼 때 비영)"
      - "점 블록 $C$ 의 패턴"
      - "항상 조밀하다"
    answer: 1
    explanation: "$S_{ik} = B_{ik} - \\sum_j E_{ij}C_{jj}^{-1}E_{kj}^\\top$ 이고 $E_{ij} \\ne 0 \\iff (i,j)$ 가 관측이므로, $i \\ne k$ 의 블록은 두 카메라가 공유하는 점이 있을 때만 비영이다. 측정값(BAL-49): 공동가시성 밀도 0.835 = $S$ 의 밀도 0.835."
    concept: { front: "$S$ 의 희소 패턴", back: "카메라 공동가시성 그래프. 대규모에서 이 희소성이 전처리자의 근거가 된다" }
  - id: q5
    type: single
    prompt: "비틀림 0 · 종횡비 1 · 주점이 원점인 카메라로 자기 보정을 할 때, 선형 계수 셈이 요구하는 최소 시점 수와 그 셈의 한계는?"
    choices:
      - "2 시점. 셈은 충분조건이다"
      - "3 시점. 셈은 필요조건일 뿐이고 임계 운동열에서는 시점을 늘려도 랭크가 8 에서 포화한다"
      - "5 시점. 임계 운동열은 존재하지 않는다"
      - "9 시점. 비틀림 0 만으로도 같은 수가 나온다"
    answer: 1
    explanation: "시점마다 선형 제약 4개, 미지수는 $\\Omega^*$ 의 10 성분에서 스케일을 뺀 9 이므로 $4N \\ge 9$, $N \\ge 3$. 측정값: 일반 운동은 $N=3$ 에서 랭크 9. 그러나 순수 평행이동과 고정 축 회전에서는 $N=6$ 에서도 랭크 8 이고, 순수 회전은 랭크 5 다."
    concept: { front: "자기 보정의 시점 수 셈", back: "시점당 4식 / 미지수 9 → $N \\ge 3$. 필요조건일 뿐 — 평면 주행·고정 축 선회는 임계 운동열이다" }
```

## 이 단계 공부법

1. **희소 구조를 손으로 그린다 (40분)** — 카메라 3개, 점 5개, 관측 몇 개를 종이에 그리고
   $J$ 와 $H$ 의 비영 패턴을 직접 칠한다. (1)의 nnz 공식을 그 그림에서 읽고 P1 로 BAL 수치와
   맞춰 본다. 이 그림 하나가 R1·R3 전부다.
2. **Schur 를 소거로 본다 (60분)** — (5)에서 (7)까지 세 줄을 백지에서 쓰고, 그 다음 (2)의
   $LDL^\top$ 을 직접 곱해 확인한다. "근사가 아니다"를 스스로 증명한 사람과 외운 사람은
   디버깅에서 갈린다. Triggs §4 를 같은 결과의 다른 표기로 대조해 읽는다.
3. **작게 먼저 구현한다 (120분)** — 카메라 6개·점 40개 합성 문제로 ⓐ 조밀 해 ⓑ Schur 해를
   둘 다 구현해 $10^{-10}$ 수준으로 일치시킨다(조건 3). 여기서 맞지 않으면 BAL 로 가지 않는다.
   같은 문제에서 $J$ 의 특이값을 뽑아 랭크 결손 7 을 눈으로 본다(조건 4).
4. **게이지를 만들고 지운다 (60분)** — (3)의 생성자를 코드로 적용해 비용이 변하지 않는 것을
   확인하고, 카메라 0 과 스케일을 고정한 뒤 $H$ 가 가역이 되는 것을 본다. 그 다음 고정 없이
   LM 으로 수렴시켜 **스텝 노름이 줄지 않는 것**을 관찰한다. 이 대비가 이 레슨의 핵심 체험이다.
5. **BAL 로 간다 (180분)** — 데이터를 내려받고 포맷을 파서부터 쓴다. 초기 비용이 참조값과
   0.1% 이내로 맞을 때까지 다른 것을 건드리지 않는다(조건 1). $p = -P/P_z$ 의 음부호에서
   대부분이 막힌다. 그 다음 40 반복으로 최종 비용을 맞춘다(조건 2).
6. **자기 보정은 셈부터 (60분)** — (11)의 네 식을 직접 쓰고 $4N\times10$ 행렬을 만들어 랭크를
   재 본다. 그 다음 순수 평행이동으로 바꿔 랭크가 포화하는 것을 본다(P7). "셈이 맞으면 풀린다"가
   왜 거짓인지 손으로 확인하는 것이 목적이다.
7. **논문 2편과 노트 (130분)** — Triggs §4·§9 를 먼저, 그 다음 Agarwal et al. 전체를 읽는다.
   두 논문 사이의 10년이 무엇을 바꿨는지 한 문단으로 쓴다. 논문당 1페이지 노트는 **반드시** 쓴다.
8. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제"에서 하나를 골라 왜 아직 안 풀렸는지
   한 문단으로 쓴다. 게이지 불변 불확실성은 당장 연구 주제가 되는 질문이다.

**통과 기준**: (2)의 $LDL^\top$ 을 백지에서 곱할 수 있고, (3)의 생성자 7개를 쓸 수 있고,
BAL-49 에서 재현 과제의 다섯 조건을 통과하는 코드를 갖고 있고, 임계 운동열을 하나 만들어
랭크 포화를 보였고, 논문 2편의 노트가 있다.
