---
id: c7-two-view-geometry
title: 다시점 기하와 에피폴라 제약
summary: >-
  두 시점 사이의 에피폴라 제약에서 본질행렬(essential matrix)과 기본행렬(fundamental matrix)을
  직접 유도하고, 실수 행렬이 본질행렬일 필요충분조건(특이값이 $(\sigma,\sigma,0)$)을 증명 수준에서
  다룬다. 8점·5점 알고리즘의 대수 구조를 세우고, 삼각측량의 최적성과 깊이 편향 — 왜 깊이가
  평균적으로 과대추정되는지, 그리고 왜 그 평균이 엄밀하게는 존재하지 않는지 — 까지 간다.
objectives:
  - 공면 조건에서 에피폴라 제약과 $E = \hat{t}R$ 을 빠진 줄 없이 유도할 수 있다.
  - 실수 $3\times3$ 행렬이 본질행렬일 필요충분조건이 특이값 $(\sigma,\sigma,0)$ 임을 증명 스케치로 재구성할 수 있다.
  - 8점 알고리즘의 선형계와 최근접 본질행렬 투영을 구현하고, Hartley 정규화가 어디서 효과가 있고 어디서 없는지 수치로 설명할 수 있다.
  - 5점 문제의 해가 최대 10개인 이유를 단항식 수와 작용행렬(action matrix) 구성으로 설명할 수 있다.
  - 선형 삼각측량의 깊이가 평균적으로 과대편향됨을 2차 전개로 보이고, 역깊이 매개화가 왜 다른지 설명할 수 있다.
prerequisites: [c1-so3-se3-exponential]
difficulty: 5
estimated_minutes: 600
tags: [perception, multi-view-geometry, epipolar-geometry, essential-matrix, triangulation, research]
activities:
  - id: c7-two-view-geometry-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 100
  - id: c7-two-view-geometry-papers
    kind: reading
    title: 필독 논문 2편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 120
  - id: c7-two-view-geometry-problems
    kind: exercise
    title: 문제 세트 (유도 1 · 증명 1 · 계산 3 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: c7-two-view-geometry-reproduction
    kind: exercise
    title: 재현 과제 — 8점·5점 알고리즘과 퇴화 구성 (R2)
    estimated_minutes: 180
  - id: c7-two-view-geometry-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 20
resources:
  - title: "Hartley & Zisserman, Multiple View Geometry in Computer Vision (2nd ed.)"
    url: https://www.robots.ox.ac.uk/~vgg/hzbook/
    kind: book
    note: >-
      ch.9 (에피폴라 기하와 기본행렬), ch.11 (기본행렬 계산), ch.12 (삼각측량), ch.22 (퇴화 구성).
      이 레슨의 1순위 교재. 표본 장 3개와 MATLAB 코드·오류표가 공개되어 있다.
  - title: "Szeliski, Computer Vision: Algorithms and Applications (2nd ed., 2022)"
    url: https://szeliski.org/Book/
    kind: book
    note: ch.11 (Structure from motion and SLAM). 알고리즘 전체 그림과 실무 감각. 개인용 PDF 무료.
  - title: "Longuet-Higgins — A computer algorithm for reconstructing a scene from two projections (1981)"
    url: https://doi.org/10.1038/293133a0
    kind: article
    note: 필독 1 · 역할 `원전(seminal)`. 본질행렬과 8점 선형 해법의 원전. 두 쪽이다.
  - title: "Nistér — An efficient solution to the five-point relative pose problem (2004)"
    url: https://doi.org/10.1109/TPAMI.2004.17
    kind: article
    note: 필독 2 · 역할 `표준(standard)`. 5점 문제의 10차 다항식 해법. §3-4 가 핵심.
  - title: "Huang & Faugeras — Some properties of the E matrix in two-view motion estimation (1989)"
    url: https://doi.org/10.1109/34.41368
    kind: article
    note: 권장. R2 의 특이값 특성화 원전. 두 쪽 반이고 증명이 짧다.
  - title: "Hartley — In defense of the eight-point algorithm (1997)"
    url: https://doi.org/10.1109/34.601246
    kind: article
    note: 권장. 좌표 정규화가 조건수를 통해 정확도를 바꾸는 이유. R3 의 정규화 절의 출처.
  - title: "Hartley & Sturm — Triangulation (1997)"
    url: https://doi.org/10.1006/cviu.1997.0547
    kind: article
    note: 권장. 2시점 최적 삼각측량이 6차 다항식으로 닫힘을 보인 논문.
  - title: "Stewénius, Engels & Nistér — Recent developments on direct relative orientation (2006)"
    url: https://doi.org/10.1016/j.isprsjprs.2006.03.005
    kind: article
    note: 권장. 5점 문제의 작용행렬(Gröbner) 해법 — Nistér 2004 보다 구현하기 쉽다.
  - title: "Lee & Civera — Triangulation: why optimize? (2019)"
    url: https://arxiv.org/abs/1907.11917
    kind: article
    note: 권장. 최적 삼각측량이 왜 생각만큼 이득이 아닌지 — 열린 문제 1의 현재 접근.
  - title: "UZH/ETH 151-0632 Vision Algorithms for Mobile Robotics (Scaramuzza)"
    url: https://rpg.ifi.uzh.ch/teaching.html
    kind: course
    note: 강의 슬라이드와 연습. 이 레슨 범위는 Lecture 5-9.
---

# 다시점 기하와 에피폴라 제약

## 전제와 기호

이 레슨은 C7 모듈의 첫 레슨이다. 권장 선수는 `c1-so3-se3-exponential`(회전의 지수 좌표와
$\hat{\cdot}$ 표기)과 `robotics-expert` 코스의 `m4-camera-model-features`(핀홀 모델과 캘리브레이션)
이지만, 둘 다 잠겨 있지 않다 — 아래 자가 진단을 통과하면 바로 시작하면 된다. 다음을 전제한다:

- 선형대수: SVD, 특이값과 조건수, 영공간, 최소제곱. 직교행렬의 부호 조작.
- 확률: 기댓값, Jensen 부등식, 가우시안. Monte Carlo 추정의 표준오차.
- 사영기하는 **최소한만** 쓴다 — 동차좌표와 "스케일 무관"의 뜻만 알면 되고, 사영 다양체의
  차수(degree) 같은 이야기는 인용으로만 등장한다.

표기 규약(C7 모듈 전체에 고정. $\hat{\cdot}$ 는 C1 모듈과 같다):

| 기호 | 뜻 |
|---|---|
| $X \in \mathbb{R}^3$ | 3D 점. 아래 첨자는 그 점을 표현한 카메라 프레임 ($X_1$, $X_2$) |
| $\tilde{x} = (u, v, 1)^\top$ | **픽셀** 동차좌표 |
| $K$ | 내부 파라미터 행렬. $\tilde{x} = KX/Z$ |
| $x = K^{-1}\tilde{x}$ | **정규화 이미지 좌표**(normalized image coordinates). $x = X/Z$ |
| $(R, t)$ | 상대 자세. $R = {}^2R_1 \in SO(3)$, $t \in \mathbb{R}^3$, $X_2 = R X_1 + t$ |
| $\hat{t}$ | $t$ 의 반대칭 행렬. $\hat{t}a = t \times a$. 비전 문헌의 $[t]_\times$ 와 같다 |
| $E = \hat{t}R$ | 본질행렬(essential matrix). 스케일 무관 |
| $F = K_2^{-\top} E K_1^{-1}$ | 기본행렬(fundamental matrix) |
| $e_1, e_2$ | 에피폴(epipole). $Ee_1 = 0$, $E^\top e_2 = 0$ |
| $\sigma_i(A)$ | $A$ 의 특이값, 내림차순 |
| $\mathcal{E} \subset \mathbb{P}^8$ | 본질행렬 전체의 집합(본질 다양체) |
| $d$, $\rho = 1/Z$ | 시차(disparity)와 역깊이(inverse depth) |

**스케일 규약**: 단안(monocular) 두 시점에서 $\|t\|$ 는 복원되지 않는다. 이 레슨 전체에서
$\|t\| = 1$ 로 정규화하고, 오차는 **회전 오차** $\angle(R_{\text{gt}}^\top \hat{R})$ 와
**평행이동 방향 오차** $\angle(t_{\text{gt}}, \hat{t})$ 로만 보고한다.

## 시작 전 자가 진단

모듈의 첫 레슨이므로 준비 상태를 먼저 점검한다. **선수 레슨은 잠겨 있지 않다** — 아래를 전부
풀 수 있으면 권장 선수를 건너뛰어도 좋다. **두 문항 이상 막히면** 괄호 안의 레슨으로 돌아가는
편이 빠르다.

1. $f = 500$, 주점 $(c_u, c_v) = (320, 320)$, 왜곡 없음인 핀홀 카메라에 $X = (0.4, -0.2, 4.0)$
   이 맺히는 픽셀 좌표는? (`m4-camera-model-features`)
   **정답**: $u = 500 \cdot 0.4/4.0 + 320 = 370$, $v = 500 \cdot (-0.2)/4.0 + 320 = 295$.
2. $t \ne 0$ 일 때 $\hat{t}$ 의 랭크와 영공간은? (`c1-so3-se3-exponential`)
   **정답**: 랭크 2, 영공간은 $\operatorname{span}\{t\}$ ($\hat{t}t = t \times t = 0$ 이고
   $\hat{t}$ 는 반대칭이라 홀수 차원에서 $\det \hat{t} = 0$).
3. $A \in \mathbb{R}^{n \times 9}$ 에 대해 $\min_{\lVert e \rVert = 1} \lVert Ae \rVert$ 의 값과
   최소점은? (`r0-linear-algebra-decompositions`)
   **정답**: 값은 $\sigma_9(A)$ (최소 특이값), 최소점은 그에 대응하는 **오른쪽 특이벡터**.
   허용오차: 수치 실험에서 $10^{-12}$.
4. $X$ 가 상수가 아닌 양의 확률변수이고 $g(x) = 1/x$ 일 때 $\mathbb{E}[g(X)]$ 와 $g(\mathbb{E}[X])$
   의 대소를 부호까지 쓰라. (`r0-estimation-theory`)
   **정답**: $1/x$ 는 $x > 0$ 에서 강볼록(strictly convex)이므로 Jensen 부등식에서
   $\mathbb{E}[1/X] > 1/\mathbb{E}[X]$. 등호는 $X$ 가 상수일 때만.
5. 스케일 무관한 $3\times3$ 행렬의 자유도는? 거기에 $\det = 0$ 을 더하면? (`r0-linear-algebra-decompositions`)
   **정답**: $9 - 1 = 8$, $\det = 0$ 을 더하면 $7$. (이것이 기본행렬 $F$ 의 자유도 7 이다.)

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (에피폴라 제약과 본질행렬) [D2]** — 같은 3D 점을 보는 두 정규화 이미지 좌표
  $x_1, x_2$ 는 깊이와 무관하게
  $$x_2^\top E x_1 = 0, \qquad E = \hat{t}R \tag{1}$$
  를 만족한다. 픽셀 좌표에서는 $\tilde{x}_2^\top F \tilde{x}_1 = 0$, $F = K_2^{-\top} E K_1^{-1}$.
  에피폴은 $e_1 \propto R^\top t$, $e_2 \propto t$ 이고 에피폴라 선은 $l_2 = Ex_1$, $l_1 = E^\top x_2$ 다.
- **R2 (본질행렬의 특성화와 자유도) [D3]** — $E \ne 0$ 에 대해 다음은 동등하다:
  (i) 어떤 $R \in SO(3)$, $t \ne 0$ 에 대해 $E = \hat{t}R$;
  (ii) $E$ 의 특이값이 $(\sigma, \sigma, 0)$, $\sigma > 0$;
  (iii) 대수적 조건
  $$2EE^\top E - \operatorname{tr}(EE^\top)\,E = 0. \tag{2}$$
  따라서 $\mathcal{E}$ 는 $\mathbb{P}^8$ 안의 **5차원** 다양체다 — $E$ 의 자유도는 5,
  $F$ 의 자유도는 7 이다. (2)의 9개 스칼라 식은 $\mathcal{E}$ 의 일반점에서 랭크 3 이다.
- **R3 (8점 알고리즘과 최근접 본질행렬) [D2]** — (1)은 $\operatorname{vec}(E)$ 에 선형이므로
  $n \ge 8$ 개 대응은 $A\mathbf{e} = 0$, $A$ 의 $i$ 행 $= (x_{2}^{(i)} \otimes x_{1}^{(i)})^\top$
  를 준다. $\sigma_9$ 의 오른쪽 특이벡터가 최소제곱 해이고, 그 뒤 **Frobenius 노름에서 가장 가까운
  본질행렬**은
  $$\hat{E} = U \operatorname{diag}(\bar{\sigma}, \bar{\sigma}, 0) V^\top, \qquad
    \bar{\sigma} = \tfrac{1}{2}(\sigma_1 + \sigma_2) \tag{3}$$
  이다 ($E = U\Sigma V^\top$ 는 최소제곱 해의 SVD).
- **R4 (5점 문제의 해 개수) [D2]** — 5개 대응은 $\operatorname{vec}(E)$ 의 4차원 영공간을 남긴다.
  그 안에서 (2)와 $\det E = 0$ 을 풀면 3변수 3차식 10개가 되고, 차수 $\le 3$ 단항식이 20개이므로
  $10 \times 20$ 계수행렬의 소거는 10차원 몫공간 위의 **작용행렬**(action matrix)로 닫힌다.
  따라서 해는 **최대 10개**이고, 일반 구성에서 정확히 10개(복소 포함)다. 각 $E$ 는 4개의
  $(R, t)$ 분해를 주고 그중 카이랄성(chirality)을 만족하는 것이 하나다.
- **R5 (삼각측량의 최적성과 편향) [D3]** — 등방 가우시안 이미지 잡음에서 최대가능도(ML)
  삼각측량은 재투영 오차 최소화이고 2시점에서는 6차 다항식으로 닫힌다(Hartley–Sturm). 그러나
  **어떤 깊이 추정량도 불편향이 아니다**: 정렬된 스테레오에서 $\hat{Z} = fb/\hat{d}$ 는
  $$\mathbb{E}[\hat{Z}] = Z\left(1 + \frac{\sigma_d^2}{d^2}\right) + O\!\left(\frac{\sigma_d^4}{d^4}\right) \tag{4}$$
  로 **과대추정**되는 반면 역깊이 $\hat{\rho} = \hat{d}/(fb)$ 는 정확히 불편향이다. 더 날카롭게,
  잡음이 진짜 가우시안이면 $\mathbb{E}[\hat{Z}]$ 는 **존재하지 않는다**(적분이 발산한다) —
  (4)는 꼬리를 자른 조건부 기댓값에 대한 식이다. **[D3]**

## 유도

### R1 — 에피폴라 제약

핀홀 모델에서 정규화 좌표는 $x_i = X_i / Z_i$ 이므로 $X_i = Z_i x_i$ ($Z_i > 0$). 강체 운동
$X_2 = R X_1 + t$ 에 넣으면

$$Z_2 x_2 = Z_1 R x_1 + t. \tag{5}$$

깊이 $Z_1, Z_2$ 를 지우는 것이 전부다. 양변에 왼쪽에서 $\hat{t}$ 를 곱하면 $\hat{t}t = 0$ 이므로

$$Z_2\,\hat{t}x_2 = Z_1\,\hat{t}Rx_1.$$

이제 양변에 왼쪽에서 $x_2^\top$ 를 곱한다. $\hat{t}$ 는 반대칭이므로 임의의 $a$ 에 대해
$a^\top \hat{t} a = 0$ 이고, 좌변은 사라진다:

$$0 = Z_1\, x_2^\top \hat{t} R x_1.$$

$Z_1 \ne 0$ 이므로 (1)이다. **한 줄도 건너뛰지 않았다** — 쓴 것은 $\hat{t}t = 0$ 과
$a^\top\hat{t}a = 0$ 두 항등식뿐이다.

**기하적 읽기**: (1)은 삼중곱 $x_2 \cdot (t \times Rx_1) = 0$, 즉 기준선(baseline) $t$ 와 두
시선 벡터가 **공면**이라는 뜻이다. 세 벡터가 만드는 평행육면체의 부피가 0 이다. 이 평면이
에피폴라 평면이고, 이미지와의 교선이 에피폴라 선이다.

**에피폴**: $Ev = 0 \iff \hat{t}(Rv) = 0 \iff Rv \parallel t \iff v \propto R^\top t$ 이므로
$e_1 \propto R^\top t$. 또 $E^\top w = R^\top\hat{t}^\top w = 0 \iff \hat{t}w = 0 \iff w \propto t$
이므로 $e_2 \propto t$. 물리적으로 $e_1$ 은 **카메라 2 의 중심을 이미지 1 에 투영한 점**이다 —
카메라 2 의 중심은 프레임 1 에서 $-R^\top t$ 이고, 이는 $R^\top t$ 와 같은 직선 위에 있다.

**픽셀 좌표로**: $x_i = K_i^{-1}\tilde{x}_i$ 를 (1)에 대입하면
$\tilde{x}_2^\top K_2^{-\top} E K_1^{-1} \tilde{x}_1 = 0$, 즉 $F = K_2^{-\top}EK_1^{-1}$ 이다.
$K$ 가 가역이므로 $\operatorname{rank}F = \operatorname{rank}E = 2$ 이지만, **$F$ 의 특이값은
$E$ 의 특이값이 아니다** — $K$ 가 비등방 스케일을 섞기 때문이다. 이 사실이 R2 의 실패 모드와
8점 알고리즘의 정규화 논의로 직결된다.

**가정이 깨지는 곳**: $t = 0$ (순수 회전)이면 $E = 0$ 이고 (1)은 **모든** 대응에 대해 성립한다 —
제약이 공허해지고 상대 회전을 $E$ 에서 복원할 수 없다. 이때는 무한 호모그래피
$\tilde{x}_2 = K_2 R K_1^{-1}\tilde{x}_1$ 을 써야 한다. 또 $Z_1 = 0$ (카메라 중심에 놓인 점)은
배제되고, $\|t\|$ 는 (1)이 $E$ 의 스케일에 무관하므로 **복원 불가능**하다(단안 스케일 모호성).

### R3 — 8점 알고리즘

$x_2^\top E x_1 = \sum_{i,j} E_{ij}\, x_{2,i}\, x_{1,j}$ 이므로, $E$ 를 행 우선으로 펼친
$\mathbf{e} = \operatorname{vec}(E) \in \mathbb{R}^9$ 에 대해

$$x_2^\top E x_1 = (x_2 \otimes x_1)^\top \mathbf{e} = 0 \tag{6}$$

이다 ($\otimes$ 는 Kronecker 곱). $n$ 개 대응을 쌓으면 $A \in \mathbb{R}^{n\times9}$,
$A\mathbf{e} = 0$. 일반 구성에서 $n = 8$ 이면 $\operatorname{rank}A = 8$ 이고 영공간이 1차원이다.
잡음이 있으면 정확한 영벡터가 없으므로

$$\mathbf{e}^\star = \arg\min_{\lVert \mathbf{e}\rVert = 1} \lVert A\mathbf{e}\rVert$$

를 푼다. $A = U_A\Sigma_A V_A^\top$ 로 쓰면 $\lVert A\mathbf{e}\rVert^2 = \sum_k \sigma_k^2 c_k^2$
($c = V_A^\top\mathbf{e}$, $\lVert c\rVert = 1$)이므로 최소는 $c = e_9$, 즉 $\mathbf{e}^\star$ 는
$\sigma_9$ 의 오른쪽 특이벡터다.

이렇게 얻은 $E^\star$ 는 특이값이 $(\sigma_1, \sigma_2, \sigma_3)$ 로 일반적이라 **본질행렬이
아니다**. R2 가 요구하는 $(\bar\sigma, \bar\sigma, 0)$ 로 투영해야 한다. 그 투영이 (3)이라는 것을
유도한다. Mirsky 의 정리(고정된 특이값 집합을 갖는 행렬 중 $A$ 에 Frobenius 최근접인 것은
$A$ 의 특이벡터를 공유한다)로

$$\min_{\substack{\text{특이값이 } (\sigma,\sigma,0)}} \lVert E^\star - B \rVert_F^2
  = (\sigma_1 - \sigma)^2 + (\sigma_2 - \sigma)^2 + \sigma_3^2 \tag{7}$$

이 되고, 오른쪽을 $\sigma$ 에 대해 미분하면 $-2(\sigma_1-\sigma) - 2(\sigma_2-\sigma) = 0$,
즉 $\sigma = \bar\sigma = (\sigma_1+\sigma_2)/2$ 다. 최소값은
$\tfrac{1}{2}(\sigma_1-\sigma_2)^2 + \sigma_3^2$ 이고, 이 값 자체가 **데이터가 보정된 두 시점
모델에 얼마나 맞는지의 척도**다 — 퇴화 구성이나 캘리브레이션 오류를 싸게 감지하는 진단량으로 쓴다.

**좌표 정규화(Hartley)**: $A$ 의 열은 $x_{2,i}x_{1,j}$ 꼴이라 좌표의 **2차** 스케일을 탄다.
픽셀 좌표($u \sim 10^3$)에서는 $u_2u_1 \sim 10^6$ 과 $1$ 이 한 행렬에 섞여 조건수가 폭발한다.
Hartley 의 처방은 각 이미지에서 중심을 원점으로 옮기고 평균 거리를 $\sqrt{2}$ 로 맞추는 닮음변환
$T_i$ 를 적용해 $y_i = T_ix_i$ 로 풀고, 끝에서 $F = T_2^\top F_y T_1$ 로 되돌리는 것이다.

이 레슨의 측정값(아래 재현 과제의 장면 생성기, 8점, 픽셀 잡음 $\sigma = 1$px, 200회):

| | $\operatorname{cond}(A)$ 중앙값 | 회전 오차 중앙값 | 회전 오차 p90 |
|---|---|---|---|
| $F$, 픽셀 좌표, 정규화 **있음** | $3.8\times10^{2}$ | $4.22^\circ$ | $10.42^\circ$ |
| $F$, 픽셀 좌표, 정규화 **없음** | $9.8\times10^{5}$ | $4.99^\circ$ | $16.35^\circ$ |
| $E$, 정규화 좌표, 정규화 있음/없음 | 동일 | $4.61^\circ$ | $12.89^\circ$ |

읽는 법 두 가지. ① 조건수는 2600배 좋아지지만 중앙값 오차는 15% 만 좋아진다 — 정규화의 이득은
**꼬리**에서 온다(p90 36% 개선). ② **정규화 좌표에서 $E$ 를 직접 풀면 Hartley 정규화는 할 일이
없다** — $x$ 의 성분이 이미 $O(1)$ 이기 때문이다. "8점 알고리즘에는 항상 정규화를 해야 한다"는
교과서적 조언은 **픽셀 좌표의 $F$ 에 대한** 조언이고, 보정된 $E$ 에 그대로 옮기면 틀린다.

**가정이 깨지는 곳**: 3D 점이 **한 평면에 있으면** $\operatorname{rank}A = 6$ 이 되어 영공간이
3차원이고, (1)을 만족하는 $F$ 가 3-매개변수 족
$F = \hat{e}_2 H + e_2 a^\top$ ($H$ 는 그 평면이 유도하는 호모그래피) 전체가 된다. $\sigma_9$ 의
특이벡터는 그 족에서 **임의의 원소**를 집어오고, (3)의 투영은 그것을 성실하게 본질행렬로 만든다 —
잡음이 0 이어도 회전 오차가 남는다(측정값: 공면 20점에서 $4.95^\circ$). 순수 회전($t=0$)도 같은
방식으로 조용히 틀린 답을 준다. 두 경우 모두 **잔차로는 감지되지 않는다**: 잔차는 작다.
감지하려면 $\sigma_7(A)/\sigma_6(A)$ 를 봐야 한다(측정값: 공면에서 $10^{-15}$ 수준).

### R4 — 5점 문제의 대수 구조

5개 대응은 (6)에서 $A \in \mathbb{R}^{5\times9}$ 를 주고, 일반 구성에서 영공간은 4차원이다.
그 기저를 $E_1, \dots, E_4$ 라 하면 모든 후보는

$$E(x,y,z,w) = xE_1 + yE_2 + zE_3 + wE_4 \tag{8}$$

이고 스케일 무관하므로 $w = 1$ 로 둔다(이 분기는 $w = 0$ 인 해를 놓치지만, 그것은 영공간의
초평면에 해당하는 측도 0 집합이다 — 구현에서는 기저 순서를 바꿔 재시도한다).

(8)을 (2)에 넣으면 좌변의 각 성분은 $(x,y,z)$ 의 **3차** 동차 아닌 다항식이 된다($E$ 가 1차,
$EE^\top E$ 가 3차). $\det E = 0$ 도 3차다. 따라서 3변수 3차식 **10개**를 얻는다. 차수 $\le 3$
단항식의 수는 $\binom{3+3}{3} = 20$ 개:

$$\{x^3, x^2y, x^2z, xy^2, xyz, xz^2, y^3, y^2z, yz^2, z^3\} \cup
  \{x^2, xy, xz, y^2, yz, z^2, x, y, z, 1\}.$$

앞의 10개(3차)를 왼쪽에, 뒤의 10개를 오른쪽에 두고 계수행렬 $M \in \mathbb{R}^{10\times20}$ 을
만든 뒤 왼쪽 블록으로 Gauss–Jordan 소거를 하면 $[\,I_{10} \mid B\,]$ 가 된다. 즉 **모든 3차
단항식이 10개의 저차 단항식의 선형결합으로 표현된다**. 그러면 몫공간
$\mathbb{R}[x,y,z]/I$ 의 기저가 $\{x^2, xy, xz, y^2, yz, z^2, x, y, z, 1\}$ (10차원)이고,
"$x$ 를 곱하는 연산"은 이 기저에서 $10\times10$ 행렬 $A_x$ (작용행렬)로 적힌다. 해 $(x^\star,
y^\star, z^\star)$ 마다 단항식 벡터 $v^\star$ 가 $A_x v^\star = x^\star v^\star$ 를 만족하므로,
**해는 $A_x$ 의 고유값·고유벡터로 읽힌다**. $10\times10$ 이므로 해는 최대 10개다.

Nistér 2004 는 여기서 한 걸음 더 나아가 소거를 손으로 정리해 **하나의 10차 일변수 다항식**으로
줄인다(§3–4) — 고유분해보다 빠르다. Stewénius et al. 2006 은 위의 작용행렬 형태가 수치적으로
더 안정하고 구현이 훨씬 짧다고 보고한다. 둘 다 "최대 10개"라는 같은 결론에 도달하며, 이 상한은
$\mathcal{E}$ 가 $\mathbb{P}^8$ 에서 차수 10 인 5차원 다양체이고 5개 선형 제약이 $\mathbb{P}^8$ 을
$\mathbb{P}^3$ 으로 자른다는 사실과 일치한다(Demazure; MVG ch.11.6 참고 **[D0]**).

**$(R,t)$ 로 내려가기**: 각 $E$ 에서 R2 의 구성으로 $(R, \pm t)$ 와 $(R', \pm t)$ 네 쌍이 나온다
($R' = UWV^\top$ vs $UW^\top V^\top$). 네 후보 중 **두 시점 모두에서 깊이가 양수**인 것이
하나다(카이랄성). 깊이는 (5)를 $[\,Rx_1 \;\; -x_2\,] (Z_1, Z_2)^\top = -t$ 로 풀어 얻는다.

**가정이 깨지는 곳**: ① 5점이 공면이면 해집합에 평면 모호성이 들어온다 — 참해는 여전히 후보에
들어 있지만(측정값: 회전 오차 $0.00^\circ$) 유일하지 않아 점수화(RANSAC) 없이 고를 수 없다.
② 5점이 두 카메라 중심을 지나는 **임계 곡면**(ruled quadric) 위에 있으면 여러 해가 모두
기하적으로 타당하다(MVG ch.22.2 **[D0]**). ③ $t \to 0$ 에서는 $E \to 0$ 이라 영공간 계산 자체가
무의미해진다. ④ $w = 0$ 분기(위) — 드물지만 구현에서 재시도가 필요하다.

### R5 — 삼각측량: 세 추정량과 깊이 편향

**선형(DLT)**: 각 시점에서 $x \times (P X) = 0$ 의 세 식 중 둘이 독립이므로 2시점에서
$A \in \mathbb{R}^{4\times4}$, $AX = 0$ 을 얻고 $\sigma_4$ 의 특이벡터를 취한다. 이것은
$\lVert AX\rVert$ (대수 오차)를 최소화하며 **재투영 오차를 최소화하지 않는다** — 동차좌표의
정규화 방식에 따라 답이 바뀐다.

**ML(재투영 오차)**: 이미지 잡음이 등방 가우시안이면 음의 로그가능도는

$$\min_{\hat{x}_1, \hat{x}_2} \lVert x_1 - \hat{x}_1\rVert^2 + \lVert x_2 - \hat{x}_2\rVert^2
  \quad \text{s.t.}\quad \hat{x}_2^\top F \hat{x}_1 = 0 \tag{9}$$

이다. Hartley–Sturm 은 이미지 1 의 에피폴라 선 다발(pencil)을 한 매개변수 $s$ 로 적고 (9)를
$s$ 의 유리함수로 바꾼 뒤 미분하면 **6차 다항식**이 되어 닫힌 형태로 풀린다는 것을 보였다.
실무에서는 1차 근사인 Sampson 거리

$$\delta_{\text{Samp}} = \frac{x_2^\top Fx_1}
  {\sqrt{(Fx_1)_1^2 + (Fx_1)_2^2 + (F^\top x_2)_1^2 + (F^\top x_2)_2^2}} \tag{10}$$

를 쓴다 — 제약 위로 한 번 Newton 스텝을 밟은 것과 같다.

**편향**: 정렬된 스테레오(초점거리 $f$, 기준선 $b$, 시차 $d = fb/Z$)로 좁혀 보자. 두 이미지의
위치 잡음이 각각 $N(0,\sigma_p^2)$ 이면 $\hat{d} = d + \epsilon$, $\sigma_d^2 = 2\sigma_p^2$ 이고
$\hat{Z} = fb/\hat{d}$ 다. $\lvert\epsilon\rvert < d$ 에서 Laurent 전개

$$\frac{1}{d+\epsilon} = \frac{1}{d}\left(1 - \frac{\epsilon}{d} + \frac{\epsilon^2}{d^2}
  - \frac{\epsilon^3}{d^3} + \cdots\right)$$

에 기댓값을 취하면 $\mathbb{E}[\epsilon] = 0$, $\mathbb{E}[\epsilon^2] = \sigma_d^2$,
$\mathbb{E}[\epsilon^3] = 0$ 이므로 (4)가 나온다. 상대 편향은
$\sigma_d^2/d^2 = (\sigma_d Z/(fb))^2$ 로 **깊이의 제곱으로 자란다**. 반면

$$\hat{\rho} = \frac{\hat{d}}{fb} = \rho + \frac{\epsilon}{fb}$$

는 $\hat{d}$ 의 **아핀** 함수이므로 정확히 불편향이고 정확히 가우시안이다. 이것이 SLAM 과 BA 가
점을 역깊이로 매개화하는 이유다(Civera 류의 inverse-depth 매개화). 또 $1/x$ 는 $x>0$ 에서
단조감소이므로 **중앙값은 정확히 보존된다**: $\operatorname{med}(\hat{Z}) = fb/\operatorname{med}(\hat{d}) = Z$.

측정값(Monte Carlo $2\times10^6$ 표본, $f=500$, $b=0.5$, $\hat{d}>0$ 조건부):

| $Z$ | $d$ | 예측 $\sigma_d^2/d^2$ | 실측 상대 편향 | 중앙값 오차 |
|---|---|---|---|---|
| 5 | 50.0 | $+0.08\%$ | $+0.08\%$ | $-0.00\%$ |
| 20 | 12.5 | $+1.28\%$ | $+1.35\%$ | $+0.02\%$ |
| 50 ($\sigma_p = 0.5$) | 5.0 | $+2.00\%$ | $+2.15\%$ | $+0.01\%$ |
| 50 ($\sigma_p = 1.0$) | 5.0 | $+8.00\%$ | $+12.72\%$ | $+0.01\%$ |

마지막 행에서 2차 전개가 무너진다 — $\sigma_d/d = 0.28$ 이라 Laurent 급수의 고차항이 더 이상
작지 않다. 중앙값은 네 경우 모두 불편향이다.

**가정이 깨지는 곳**: 잡음이 진짜 가우시안이면 $\hat{d}$ 는 0 을 포함하는 지지집합을 갖고
$\int \frac{1}{x}N(x; d, \sigma_d^2)\,dx$ 는 $x = 0$ 근방에서 발산한다 — 즉
**$\mathbb{E}[\hat{Z}]$ 는 존재하지 않는다**. 위 표는 $\hat{d} > 0$ 로 자른 조건부 기댓값이고,
자르는 위치를 바꾸면 값이 바뀐다. 같은 설정에서 $\hat{d} > 3\sigma_d$ 로 자르면 $Z = 50$ 의
편향이 $+8\%$ 가 아니라 $-9.68\%$ 가 된다(표본의 30%가 버려지며, 버려지는 쪽이 큰 깊이다).
**"삼각측량은 편향되어 있다"는 문장은 어떤 추정량과 어떤 꼬리 처리를 말하는지 밝히지 않으면
의미가 없다.** 논문에서 편향 수치를 볼 때 첫 질문은 "꼬리를 어떻게 처리했는가"다.

## 증명 스케치

### R2 — 본질행렬의 특성화

**가설** H1: $E \in \mathbb{R}^{3\times3}$, $E \ne 0$.
**결론** C: (i) $\exists R \in SO(3), t \ne 0: E = \hat{t}R$ $\iff$ (ii) 특이값이
$(\sigma,\sigma,0)$, $\sigma>0$ $\iff$ (iii) 식 (2).

**전략**: (i)$\Rightarrow$(ii)는 $EE^\top$ 의 스펙트럼 계산. (ii)$\Rightarrow$(i)는 SVD 의 부호를
$SO(3)$ 로 맞춘 뒤 $\operatorname{diag}(1,1,0)$ 을 "회전 × 반대칭"으로 분해. (ii)$\iff$(iii)은
대각 성분의 대수.

1. **(i)$\Rightarrow$(ii)**: $EE^\top = \hat{t}RR^\top\hat{t}^\top = \hat{t}\hat{t}^\top
   = -\hat{t}^2 = \lVert t\rVert^2 I - tt^\top$. 이 대칭행렬의 고유값은 $t$ 방향에서 0,
   $t^\perp$ 에서 $\lVert t\rVert^2$ (중복도 2)다. 따라서 $E$ 의 특이값은
   $(\lVert t\rVert, \lVert t\rVert, 0)$.
2. **(ii)$\Rightarrow$(i)**: $E = U\Sigma V^\top$, $\Sigma = \operatorname{diag}(\sigma,\sigma,0)$.
   $U$ 의 세 번째 열의 부호를 바꾸어도 $\Sigma_{33} = 0$ 이므로 $E$ 는 변하지 않고 $\det U$ 의
   부호만 뒤집힌다. $V$ 에 대해서도 독립적으로 같다. 따라서 $U, V \in SO(3)$ 로 가정해도 좋다.
   이제 $Z = \hat{e}_3$, $W = \exp(\hat{e}_3\pi/2) \in SO(3)$ 로 두면 직접 곱해서
   $$ZW^\top = \operatorname{diag}(1,1,0) \tag{11}$$
   임을 확인한다. 그러면 $\Sigma = \sigma ZW^\top$ 이고
   $$E = \sigma\,U Z W^\top V^\top = \sigma\,(UZU^\top)(UW^\top V^\top).$$
   C1 모듈의 항등식 $R\hat{a}R^\top = \widehat{Ra}$ 로 $UZU^\top = U\hat{e}_3U^\top
   = \widehat{Ue_3} = \hat{u}_3$ ($u_3$ 는 $U$ 의 셋째 열)이고, $R := UW^\top V^\top$ 는
   $SO(3)$ 원소다. 따라서 $E = \hat{t}R$, $t = \sigma u_3$. $\square$
   (부산물: $W$ 대신 $W^\top$, $t$ 대신 $-t$ 를 써도 같은 $E$ 가 나오므로 **분해는 정확히 4개**다.)
3. **(ii)$\Rightarrow$(iii)**: $E = U\Sigma V^\top$ 를 (2)에 넣으면
   $2EE^\top E - \operatorname{tr}(EE^\top)E = U\big(2\Sigma^3 - (\textstyle\sum_j\sigma_j^2)\Sigma\big)V^\top$
   이고 괄호 안은 대각이며 $i$ 번째 성분이 $\sigma_i(2\sigma_i^2 - \sum_j \sigma_j^2)$ 다.
   $(\sigma,\sigma,0)$ 을 넣으면 $i=1,2$ 에서 $\sigma(2\sigma^2 - 2\sigma^2) = 0$, $i=3$ 에서
   $0$ 이므로 (2)가 성립한다.
4. **(iii)$\Rightarrow$(ii)**: 모든 $i$ 에서 $\sigma_i = 0$ 또는 $2\sigma_i^2 = \sum_j\sigma_j^2$.
   세 특이값이 모두 0 이 아니라고 가정하면 $2\sigma_i^2$ 가 $i$ 에 무관하므로 $\sigma_1=\sigma_2=\sigma_3=\sigma$
   이고 $2\sigma^2 = 3\sigma^2$ 에서 $\sigma = 0$ — $E \ne 0$ (H1)에 모순. 따라서 적어도 하나는
   0 이고, $\sigma_3 = 0$ 으로 둘 수 있다. 남은 $i = 1,2$ 중 0 이 아닌 것들은
   $2\sigma_i^2 = \sigma_1^2+\sigma_2^2$ 를 만족해야 하므로 $\sigma_1 = \sigma_2$. $\square$
   (주목: (2)만으로 $\det E = 0$ 이 따라 나온다 — 따로 걸 필요가 없다.)
5. **자유도**: $(R,t)$ 는 6 매개변수, $E$ 는 스케일 무관이므로 $\dim\mathcal{E} = 5$.
   $\mathbb{P}^8$ 의 차원이 8 이므로 $\mathcal{E}$ 는 여차원 3 이고, (2)의 9개 식은 일반점에서
   **랭크 3** 이다(문제 P2). 이것이 "5점이면 충분하다"의 정확한 이유다: 대응 하나가 선형 제약
   하나를 주므로 $8 - 3 = 5$.
6. **가설을 지우면**: (ii)에서 "두 특이값이 같다"를 빼고 랭크 2 만 요구하면 얻는 것은
   기본행렬의 다양체(차원 7)다. 7점 알고리즘이 $\det F = 0$ 만 걸고 푸는 대상이 바로 이것이고,
   거기서 뽑은 $(R,t)$ 는 **유클리드 복원이 아니다** — 비등방 스케일(아핀 변형)이 남는다.
   보정된 카메라에서 $F$ 를 추정한 뒤 $K^\top F K$ 를 그냥 $E$ 로 쓰면 이 때문에 정확도를
   잃는다. 또 H1($E \ne 0$)을 빼면 4단계의 모순 논법이 무너지고 (2)가 $E = 0$ 에서 자명하게
   성립한다 — 순수 회전이 정확히 그 경우다.

생략한 기술적 단계: Mirsky 의 정리(특이값 고정 하 Frobenius 최근접)와 (11)의 직접 곱. 전자는
행렬 근사 표준 결과이고 후자는 손으로 세 줄이다 — 둘 다 문제 세트에 있다.

### R5 — 깊이 추정량의 편향

**가설** H1: $f, b$ 는 정확히 알려져 있고 정렬된 스테레오. H2: $\hat{d} = d + \epsilon$,
$\epsilon \sim N(0,\sigma_d^2)$, $d > 0$. H3: 추정량은 $\hat{Z} = fb/\hat{d}$.
**결론** C1: $\mathbb{E}[\hat{Z}]$ 는 존재하지 않는다. C2: $\lvert\epsilon\rvert \le \delta < d$
로 대칭 절단하면 $\mathbb{E}[\hat{Z}] > Z$ 이고 (4)가 성립한다. C3: $\hat{\rho}$ 는 불편향.
C4: $\operatorname{med}(\hat{Z}) = Z$ 정확히.

**전략**: C1 은 적분의 발산, C2 는 Jensen + Laurent 전개, C4 는 단조변환의 중앙값 보존.

1. **C1**: $x \to 0$ 에서 $N(x;d,\sigma_d^2) \to c > 0$ 이고
   $\int_{-\eta}^{\eta}\lvert 1/x\rvert\,dx = \infty$ 이므로 $\mathbb{E}\lvert\hat{Z}\rvert = \infty$.
   주값(principal value)은 존재하지만 기댓값은 아니다.
2. **C2**: 절단 분포는 $d$ 에 대칭이므로 $\mathbb{E}[\hat{d}] = d$ 가 **정확히** 유지된다.
   $1/x$ 는 $(d-\delta, d+\delta) \subset (0,\infty)$ 에서 강볼록이므로 Jensen 부등식에서
   $\mathbb{E}[1/\hat{d}] > 1/\mathbb{E}[\hat{d}] = 1/d$, 즉 $\mathbb{E}[\hat{Z}] > Z$.
   크기는 Laurent 전개(위 R5)로 $Z\sigma_d^2/d^2 + O(\sigma_d^4/d^4)$.
3. **C3**: $\hat{\rho}$ 는 $\hat{d}$ 의 아핀 함수이므로 $\mathbb{E}[\hat\rho] = \rho$.
   (절단해도 대칭이면 그대로 성립한다.)
4. **C4**: $\hat{d} \mapsto fb/\hat{d}$ 는 $\hat{d} > 0$ 에서 단조(감소)이고 단조변환은 분위수를
   보존하므로 중앙값이 보존된다. 대칭 분포에서 $\operatorname{med}(\hat d) = d$ 이므로 C4.
5. **가설을 지우면**: H2 의 대칭 절단을 빼면 C2 의 Jensen 단계가 "$\mathbb{E}[\hat d] = d$"
   를 잃는다. 한쪽만 자르면(예: $\hat{d} > 3\sigma_d$) 절단이 큰 깊이를 지워 **편향의 부호가
   뒤집힌다**(측정값: $Z=50$, $\sigma_p=1$ 에서 $+8\%$ → $-9.68\%$). 즉 C2 의 "과대추정"은
   꼬리 처리에 대한 진술 없이는 성립하지 않는다 — 이 한 문단이 "$1/d$ 는 볼록하므로 깊이는
   과대추정된다"는 흔한 요약과 실제 상황을 가른다.

생략한 기술적 단계: $N$-시점 ML 추정량의 2차 편향(Fisher 정보의 역행렬에 대한 보정항).
Lee & Civera 2019 의 분석과 그 참고문헌으로.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★, R1)** $e_1 \propto R^\top t$, $e_2 \propto t$ 를 유도하고, 모든 $x_1$ 에 대해
에피폴라 선 $l_2 = Ex_1$ 이 $e_2$ 를 지남을 보여라. 또 $F$ 의 에피폴은 $\tilde{e}_i = K_ie_i$
임을 확인하라.
*해답 스케치*: $e_2^\top l_2 = e_2^\top E x_1 = (E^\top e_2)^\top x_1 = 0$. 에피폴 유도는
$Ev = \hat{t}(Rv)$ 가 0 이 되는 조건을 $\hat{t}$ 의 영공간(자가 진단 2번)으로 환원한다.

**P2 (증명, ★★★, R2)** (2)의 9개 스칼라 식이 $\mathcal{E}$ 의 일반점에서 **랭크 3** 임을 보여라.
즉 $\Phi(E) = 2EE^\top E - \operatorname{tr}(EE^\top)E$ 의 야코비안
$D\Phi(E) \in \mathbb{R}^{9\times9}$ 가 $E = \hat{t}R \in \mathcal{E}$ 에서 랭크 3 임을 증명하라.
*전략과 핵심 부등식*: $E = \sigma \hat{e}_3 I$ 꼴로 좌표를 고정해도 일반성을 잃지 않는다
($U, V$ 로 양쪽에서 회전시키면 $\Phi$ 가 동변(equivariant)이므로). 그 점에서 $D\Phi$ 를
$3\times3$ 블록으로 적고 $\mathcal{E}$ 의 접공간(차원 5)이 핵에 들어감을 보인 뒤, 상(image)의
차원이 3 이상임을 구체적 섭동 $\delta E$ 세 개로 보인다. $\operatorname{rank} D\Phi
= 9 - \dim\ker \le 9 - 5 - 1$ (스케일 방향)에서 상한 3 이 나온다.

**P3 (계산, ★, R2·R3)** 다음 행렬을 Frobenius 노름에서 가장 가까운 본질행렬로 투영하라.
$$
\tilde{E} = \begin{bmatrix} 0 & -0.30 & 0.10 \\ 0.25 & 0 & -0.90 \\ -0.05 & 0.95 & 0 \end{bmatrix}
$$
*정답*: 특이값 $(0.99885152,\ 0.93791041,\ 0.01094111)$,
$\bar\sigma = 0.96838096$, $\lVert \tilde{E} - \hat{E}\rVert_F = 0.04445917$,
$$
\hat{E} = \begin{bmatrix}
 -0.01059627 & -0.29092379 & 0.09748319 \\
  0.25713039 & -0.00816323 & -0.92832907 \\
 -0.05402725 & 0.92212401 & 0.00789420 \end{bmatrix}.
$$
허용오차 $10^{-7}$. 검산: $\hat{E}$ 의 특이값이 $(\bar\sigma, \bar\sigma, 0)$ 이고 (2)의 잔차
$\lVert 2\hat{E}\hat{E}^\top\hat{E} - \operatorname{tr}(\hat{E}\hat{E}^\top)\hat{E}\rVert_F < 10^{-14}$,
그리고 $\lVert\tilde{E}-\hat{E}\rVert_F^2 = \tfrac12(\sigma_1-\sigma_2)^2 + \sigma_3^2$ 와 일치.

**P4 (계산, ★★, R4)** $R$ 은 $y$ 축 둘레 $20^\circ$ 회전, $t = (1,0,0)^\top$ 이고
$E = \hat{t}R$ 이다. 대응 $x_1 = (0.075, -0.05, 1)^\top$,
$x_2 = (0.72480010, -0.05470213, 1)^\top$ 에 대해 $E$ 의 네 가지 $(R,t)$ 분해를 모두 구하고,
카이랄성을 만족하는 하나를 **두 깊이의 수치로** 특정하라.
*정답*: 네 후보의 회전 오차는 $(180^\circ, 180^\circ, 0^\circ, 0^\circ)$ 이고 깊이는 각각
$(-0.930238, +0.850275)$, $(+0.930238, -0.850275)$, $(+4.000000, +3.656164)$,
$(-4.000000, -3.656164)$. 통과하는 것은 셋째, 즉 $R' = UW^\top V^\top$ 와 $t = +u_3$ 이고
$(Z_1, Z_2) = (4.000000, 3.656164)$. 허용오차 $10^{-5}$. 검산: $Z_1x_1$ 을 $R,t$ 로 보내
$Z_2x_2$ 와 $10^{-10}$ 이내로 일치하는지 본다.

**P5 (구현, ★★, R3)** 픽셀 좌표에서 $F$ 를 푸는 8점 알고리즘을 Hartley 정규화 **있음/없음**
두 버전으로 쓰고, 재현 과제의 장면 생성기로 $\operatorname{cond}(A)$ 와 회전 오차를 비교하라.
*루브릭*: ⓐ 정규화 없음의 $\operatorname{cond}(A)$ 중앙값이 있음의 $10^3$ 배 이상 ⓑ p90 회전
오차가 정규화로 20% 이상 개선 ⓒ **정규화 좌표에서 $E$ 를 직접 풀 때는 차이가 없음**을 수치로
보임 ⓓ 되돌리기 변환 $F = T_2^\top F_y T_1$ 이 있고, 왜 $T_2^\top$ 인지 한 줄로 설명한다.

**P6 (반례, ★★, R3·R4)** 잡음이 **0 인데도** 8점 알고리즘이 틀린 자세를 주는 대응 집합을
구성하라. 그 구성에서 $\operatorname{rank}A$ 를 특이값으로 보이고, 같은 점들의 부분집합 5개로
5점 해법을 돌려 참해가 후보에 들어 있음을 확인하라.
*성질 체크리스트*: ⓐ 모든 3D 점이 한 평면 위 ⓑ $\sigma_7(A)/\sigma_6(A) < 10^{-8}$ (영공간
3차원) ⓒ 에피폴라 잔차는 작지만 회전 오차는 $1^\circ$ 이상 ⓓ 5점 해법의 최소 회전 오차는
$10^{-6}$ rad 이하 ⓔ 순수 회전($t=0$)으로도 같은 현상을 만들 수 있다.

**P7 (계산, ★, R5)** $f = 500$, $b = 0.5$, $\sigma_p = 1$px, $Z = 20$m 에서 $\hat{Z}$ 의 상대
편향을 (4)로 예측하고 Monte Carlo($N \ge 10^6$)로 확인하라. 같은 설정에서 $\hat{\rho}$ 와
중앙값의 편향도 측정하라.
*정답*: $d = 12.5$px, $\sigma_d = \sqrt{2}$px, 예측 $\sigma_d^2/d^2 = 2/156.25 = +1.28\%$,
실측 $+1.35\%$ (허용오차: 예측값의 $\pm30\%$). $\mathbb{E}[\hat\rho]$ 의 상대 편향
$< 0.05\%$, 중앙값의 상대 편향 $< 0.1\%$. 검산: 표본을 $\hat{d} > 3\sigma_d$ 로 자르면 값이
바뀌어야 한다 — 바뀌지 않으면 $N$ 이 작거나 꼬리를 이미 버린 것이다.

**P8 (논문, ★★, R4)** Nistér 2004 를 읽고, 그 논문만으로 §3–4 의 해법을 재현할 때 **빠져 있는
정보 3개**를 찾아라. 그리고 Stewénius et al. 2006 의 작용행렬 해법과 비교해 어느 쪽을 구현할지
근거를 들어 선택하라.
*루브릭*: 단항식 순서의 정확한 지정, 소거 피벗 선택과 수치 스케일링, 10차 다항식 근의 선별
기준(실근·카이랄성·퇴화 처리) 중 **구체적으로** 짚으면 통과. "코드가 없다"만 쓰면 미달.

## 논문 읽기

**필독 2편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Longuet-Higgins, "A computer algorithm for reconstructing a scene from two projections"
   (1981, Nature)** — 역할: `원전(seminal)`. <https://doi.org/10.1038/293133a0>
   두 쪽이다. 이 레슨의 R1·R3 이 전부 여기서 나온다.
   추가 질문: ⓐ 저자가 쓴 선형 해법에는 R2 의 특이값 제약도, 좌표 정규화도 없다. 1981년에
   그것이 문제가 되지 않았던 이유는 무엇이고 지금은 왜 문제인가? ⓑ 논문의 자세 복원 단계에서
   카이랄성은 어떻게 처리되는가?
2. **Nistér, "An efficient solution to the five-point relative pose problem" (2004, T-PAMI)**
   — 역할: `표준(standard)`. <https://doi.org/10.1109/TPAMI.2004.17> (§3–4 가 핵심)
   추가 질문: ⓐ 저자가 보고하는 수치 실험에서 5점이 8점을 이기는 폭은 어떤 조건(FOV, 기준선,
   점 개수)에 가장 민감한가? ⓑ 10차 다항식의 근 중 물리적으로 타당한 것을 고르는 절차가
   RANSAC 안에서 비용에 어떻게 들어가는가? ⓒ 이 논문의 결론을 공면 장면에 적용할 때
   무엇이 달라지는가(이 레슨의 R4 실패 모드와 대조)?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

**권장**: Huang & Faugeras 1989 (R2 의 원전, 두 쪽 반), Hartley 1997 (정규화),
Hartley & Sturm 1997 (최적 삼각측량), Stewénius et al. 2006 (작용행렬 5점 해법),
Lee & Civera 2019 (최적 삼각측량이 왜 생각만큼 이득이 아닌가).

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, 전체 10분 이내, numpy + scipy 만.
(5점 해법의 작용행렬 구현이 막히면 영공간 위에서 `scipy.optimize.least_squares` 로
$C(R) = [\,\dots\,(x_2^{(i)} \times Rx_1^{(i)})^\top \dots]$ 의 $3\times3$ 소행렬식을 0 으로 만드는
다중 시작 해법을 대신 써도 된다 — 아래 기준은 어느 쪽으로도 판정된다.)

**장면 생성기(고정)**: $f = 500$, 주점 $(320, 320)$, 3D 점은
$[-2,2]\times[-2,2]\times[3.5,6.5]$ 에서 균등 추출, $R$ 은 균등 랜덤 축에 대한 $10^\circ$ 회전,
$t$ 는 균등 랜덤 방향에 $\lVert t\rVert = 0.5$, 이미지 잡음은 픽셀 좌표에 등방 가우시안
$N(0,\sigma^2)$. 시드를 고정해 보고한다.

아래 **다섯 조건을 모두** 만족해야 통과다.

1. **무잡음 정확성(8점)**: 일반 구성 8점, $\sigma = 0$ 에서
   $\max_i \lvert x_2^{(i)\top}\hat{E}x_1^{(i)}\rvert < 10^{-10}$,
   $\sigma_3(\hat{E})/\sigma_1(\hat{E}) < 10^{-10}$, 회전 오차 $< 10^{-8}$ rad.
   (참조 측정값: $1.4\times10^{-14}$, $7\times10^{-17}$, $0$.)
2. **무잡음 정확성(5점)**: 일반 구성 5점, $\sigma = 0$ 에서 반환된 해 집합에 참해가 들어 있다 —
   최소 회전 오차 $< 10^{-6}$ rad. 반환된 **모든** 해가
   $\lVert 2EE^\top E - \operatorname{tr}(EE^\top)E\rVert_F / \sigma_1(E)^3 < 10^{-8}$ 과
   $\lvert\det E\rvert/\sigma_1(E)^3 < 10^{-8}$ 을 만족하고, 서로 다른 회전의 개수가 20 이하다
   (본질행렬 10개 × 회전 2개). (참조 측정값: 서로 다른 회전 9·12·16개, 최소 오차 $0$.)
3. **공면 퇴화**: 3D 점을 한 평면 위에 놓고 $n \ge 9$, $\sigma = 0$ 에서
   $\sigma_7(A)/\sigma_6(A) < 10^{-8}$ (영공간 3차원)이고 8점의 회전 오차가 $1^\circ$ 를 넘는
   반면, 같은 점들 중 5개로 돌린 5점 해법의 최소 회전 오차는 $10^{-6}$ rad 이하다.
   (참조 측정값: 비 $1.1\times10^{-15}$, 8점 오차 $4.95^\circ$, 5점 오차 $0^\circ$.)
4. **정규화의 효과(픽셀 $F$)**: $\sigma = 1$px, 200회 이상에서 정규화 없음의
   $\operatorname{cond}(A)$ 중앙값이 있음의 $10^3$ 배 이상이고, p90 회전 오차가 정규화로
   20% 이상 개선된다. 또 **정규화 좌표에서 $E$ 를 직접 풀 때는** 두 버전의 회전 오차가
   $10^{-12}$ 이내로 같다. (참조 측정값: $9.8\times10^5$ vs $3.8\times10^2$, p90 $16.35^\circ
   \to 10.42^\circ$ (36% 개선), $E$ 쪽은 완전 동일.)
5. **잡음 대비 비교(이 과제의 본론)**: $\sigma \in \{0.1, 0.5, 1.0, 2.0\}$px, 각 60회 이상에서
   5점(5점 사용, 후보 중 최소 오차)의 **회전 오차 중앙값**이 8점(8점 사용)의 **0.85배 이하**다.
   (참조 측정값 — 중앙값 $^\circ$, 60회:)

   | $\sigma$ (px) | 5점 중앙값 | 8점 중앙값 | 비 | 5점 p90 | 8점 p90 |
   |---|---|---|---|---|---|
   | 0.1 | 0.504 | 0.970 | 0.52 | 4.273 | 3.037 |
   | 0.5 | 2.153 | 3.366 | 0.64 | 6.103 | 8.190 |
   | 1.0 | 3.668 | 4.924 | 0.74 | 8.179 | 16.672 |
   | 2.0 | 4.436 | 6.234 | 0.71 | 19.500 | 15.269 |

   **보고서에 반드시 쓸 것**: p90 은 중앙값과 달리 일관되게 개선되지 않는다($\sigma = 0.1$ 과
   $2.0$ 에서는 5점이 더 나쁘다). 최소 해법은 해가 여러 개라 꼬리가 두껍다 — 이것이 실무에서
   5점을 **RANSAC 안에서만** 쓰고 최종 자세는 번들 조정으로 다듬는 이유다
   (`c7-bundle-adjustment`). "5점이 8점보다 정확하다"는 문장은 **중앙값에 대한 진술**이다.

**비교 대상**: ① 서로(8점 ↔ 5점) ② 정규화 있음/없음 ③ (선택) `cv2.findEssentialMat` 또는
`cv2.findFundamentalMat` 의 같은 입력 결과 — 설치되어 있으면 회전 오차 분포가 겹치는지 본다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 회전 오차가 $180^\circ$ 근처로 나온다 | $W$ 와 $W^\top$, 또는 $t$ 의 부호를 잘못 골랐다 | 네 후보 전부의 깊이를 출력해 카이랄성으로 고른다(P4) |
| 에피폴라 잔차는 $10^{-14}$ 인데 자세가 틀렸다 | 퇴화 구성(공면·순수 회전) | $\sigma_7(A)/\sigma_6(A)$ 와 $\sigma_2(E^\star)/\sigma_1(E^\star)$ 를 본다 |
| 랭크-2 투영 전후 결과가 거의 같다 | 투영을 안 했거나 두 번 했다 | $\sigma_3(\hat{E})$ 를 직접 출력한다 |
| $E$ 가 $F$ 처럼 보인다(성분 크기가 $10^{-6}$ 수준) | 픽셀 좌표를 정규화 좌표로 착각 | $x$ 의 성분이 $O(1)$ 인지 확인 |
| 5점 해가 하나도 안 나온다 | 영공간 차원이 4 가 아니거나 $w=0$ 분기 | $\sigma_5(A)/\sigma_6(A)$ 와 기저 순서를 바꿔 재시도 |
| 5점 해가 20개를 넘는다 | 잔차 허용오차가 느슨해 근방의 점을 해로 셌다 | 허용오차를 상대값으로 바꾸고 중복 제거 각도를 올린다 |

## 열린 문제

- **(열린 문제) 다시점 삼각측량의 편향·분산 트레이드오프** — R5 가 보였듯 ML(재투영 오차) 해는
  불편향이 아니고, 불편향인 역깊이 매개화는 BA 의 등방 가우시안 가정과 어긋난다. 2시점에서는
  편향의 2차 항까지 알려져 있지만 $N$-시점·이상치 섞인 실제 궤적에서 어떤 매개화가 최종 지도
  정확도를 최대화하는지에 대한 정량 기준이 없다. 현재 접근:
  [Lee & Civera 2019](https://arxiv.org/abs/1907.11917) (최적화의 실제 이득 측정),
  [Hartley & Sturm 1997](https://doi.org/10.1006/cviu.1997.0547). 비어 있는 자리: 꼬리 처리를
  포함한 편향 정의와, 그것을 줄이는 것이 지도 정확도에 실제로 이득인지에 대한 증거.
- **(열린 문제) 퇴화 구성의 온라인 인증** — 공면 장면, 순수 회전, 임계 곡면은 잔차를 키우지
  않으면서 자세를 망가뜨린다(R3·R4 실패 모드). 추정 중에 "지금 이 구성은 퇴화다"를
  **증명서(certificate)** 로 내놓는 방법이 없고, 실무는 $\sigma$ 비나 모델 선택 휴리스틱에
  의존한다. 현재 접근: [MAGSAC++](https://arxiv.org/abs/1912.05909) 의 가중 점수화,
  MVG ch.22 의 임계 곡면 이론. 비어 있는 자리: 실시간 예산 안에서 쓸 수 있는 퇴화 인증서.
- **(열린 문제) 기하 최소 해법 vs 학습 기반 대응·자세 추정의 경계** — 학습된 대응·깊이가
  저질감(low-texture)·대 시점차에서 기하 해법을 이기는 사례가 쌓였지만, **언제 기하 제약을
  거는 것이 손해인지**에 대한 정량 기준이 없다. 현재 접근:
  [DUSt3R](https://arxiv.org/abs/2312.14132) (제약을 거의 버린 쪽),
  [DROID-SLAM](https://arxiv.org/abs/2108.10869) (미분가능 BA 로 제약을 유지한 쪽).
  비어 있는 자리: 두 설계의 성능 교차점을 장면 통계로 예측하는 모델.
  이 질문은 `c7-learned-correspondence-slam` 에서 다시 나온다.
- **(열린 문제) 최소 해법의 수치 안정성 인증** — 작용행렬 고유분해의 조건수는 구성에 따라
  수십 자릿수까지 나빠지는데, 샘플을 보고 **미리** 판정할 기준이 없다. 현재 접근:
  [Stewénius et al. 2006](https://doi.org/10.1016/j.isprsjprs.2006.03.005) 의 안정성 비교.
  비어 있는 자리: 자동 생성된 최소 해법에 안정성 보장을 붙이는 방법.

## 개념 점검

`rc quiz c7-two-view-geometry` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c7-two-view-geometry-quiz
questions:
  - id: q1
    type: single
    prompt: "3D 점이 모두 한 평면에 있을 때 8점 알고리즘이 잡음 없이도 틀린 자세를 주는 이유는?"
    choices:
      - "$A$ 의 조건수가 커져서 수치 오차가 증폭되기 때문"
      - "$\\operatorname{rank}A = 6$ 이라 영공간이 3차원이고 해가 유일하지 않기 때문"
      - "랭크-2 투영이 공면 구성에서 정의되지 않기 때문"
      - "에피폴라 제약 자체가 공면 점에서 성립하지 않기 때문"
    answer: 1
    explanation: "공면 점에서는 (1)을 만족하는 $F$ 가 3-매개변수 족 $\\hat{e}_2H + e_2a^\\top$ 전체다. $\\sigma_9$ 의 특이벡터는 그중 임의의 원소를 집어온다. 잔차는 작으므로 잔차로는 감지되지 않고, $\\sigma_7(A)/\\sigma_6(A)$ 를 봐야 한다."
    concept: { front: "공면 장면에서 8점 알고리즘이 깨지는 방식", back: "$\\operatorname{rank}A=6$ → 영공간 3차원 → 잔차는 작은데 자세는 틀림. 진단은 $\\sigma_7/\\sigma_6$" }
  - id: q2
    type: truefalse
    prompt: "보정된 카메라의 정규화 이미지 좌표에서 $E$ 를 8점 알고리즘으로 풀 때도 Hartley 좌표 정규화를 적용하면 조건수가 크게 개선된다."
    answer: false
    explanation: "정규화 이미지 좌표의 성분은 이미 $O(1)$ 이라 $A$ 의 열 스케일이 균형을 이루고 있다. 측정값으로도 정규화 있음/없음의 결과가 완전히 같았다. Hartley 정규화가 필요한 것은 픽셀 좌표에서 $F$ 를 풀 때다(조건수 $9.8\\times10^5 \\to 3.8\\times10^2$)."
    concept: { front: "Hartley 정규화가 필요한 곳", back: "픽셀 좌표의 $F$. 정규화 좌표의 $E$ 에는 효과가 없다 — 이미 $O(1)$ 이므로" }
  - id: q3
    type: single
    prompt: "본질행렬 $E$ 와 기본행렬 $F$ 의 자유도는 각각 몇인가?"
    choices: ["$E$: 5, $F$: 7", "$E$: 6, $F$: 8", "$E$: 5, $F$: 8", "$E$: 7, $F$: 7"]
    answer: 0
    explanation: "$E$ 는 $(R,t)$ 6 매개변수에서 스케일 하나를 빼 5. $F$ 는 스케일 무관 $3\\times3$ 의 8 에서 $\\det F = 0$ 하나를 빼 7. 대응 하나가 선형 제약 하나이므로 각각 5점·7점이 최소 구성이다."
    concept: { front: "$E$ 와 $F$ 의 자유도", back: "$E$ 는 5(= 6 − 스케일), $F$ 는 7(= 8 − det 조건). 최소 구성은 5점·7점" }
  - id: q4
    type: short
    prompt: "정렬된 스테레오에서 $\\hat{Z} = fb/\\hat{d}$ 는 참값 $Z$ 를 평균적으로 과대추정하는가 과소추정하는가? (한 단어)"
    answer: ["과대추정", "과대", "overestimate", "over", "과대평가"]
    explanation: "$1/x$ 가 강볼록이므로 Jensen 부등식에서 $\\mathbb{E}[1/\\hat{d}] > 1/d$ 이고 상대 편향은 $\\sigma_d^2/d^2$ 로 깊이의 제곱에 비례해 자란다. 단 이 문장은 꼬리를 자른 조건부 기댓값에 대한 것이다 — 가우시안 그대로면 $\\mathbb{E}[\\hat{Z}]$ 는 발산한다. 역깊이 $\\hat{\\rho}$ 와 중앙값은 불편향이다."
    concept: { front: "깊이 추정량의 편향 방향", back: "과대추정, 상대 편향 $\\approx \\sigma_d^2/d^2$. 역깊이와 중앙값은 불편향" }
  - id: q5
    type: single
    prompt: "두 시점 사이에 평행이동이 전혀 없을 때($t = 0$) 에피폴라 제약 $x_2^\\top Ex_1 = 0$ 은?"
    choices:
      - "성립하지 않는다 — 대응이 제약을 위반한다"
      - "$E = 0$ 이므로 모든 대응이 자동으로 만족하고 제약이 공허해진다"
      - "$E$ 의 특이값이 $(\\sigma, \\sigma, \\sigma)$ 가 된다"
      - "$F$ 로는 성립하지만 $E$ 로는 성립하지 않는다"
    answer: 1
    explanation: "$E = \\hat{t}R = 0$ 이므로 좌변이 항등적으로 0 이다. 따라서 $E$ 에서 회전을 복원할 수 없고, 무한 호모그래피 $\\tilde{x}_2 = K_2RK_1^{-1}\\tilde{x}_1$ 을 써야 한다. 추정 중에는 $\\sigma_1(E^\\star)$ 가 작아지는 것으로 감지한다."
    concept: { front: "순수 회전($t=0$)에서 에피폴라 제약", back: "$E=0$ → 제약이 공허. 회전은 무한 호모그래피 $K_2RK_1^{-1}$ 로 복원한다" }
```

## 이 단계 공부법

1. **깊이를 지우는 두 줄을 손으로 쓴다 (30분)** — R1 의 유도는 $\hat{t}t = 0$ 과
   $a^\top\hat{t}a = 0$ 두 항등식뿐이다. 백지에서 (5)부터 (1)까지 쓰고, 삼중곱으로 읽은
   공면 조건을 그림으로 그린다. 여기서 에피폴·에피폴라 선의 식도 함께 유도한다(P1).
2. **R2 의 (ii)⇒(i)을 외우지 말고 재구성한다 (60분)** — 핵심은 (11) 한 줄,
   $\operatorname{diag}(1,1,0) = ZW^\top$ 이다. $Z, W$ 를 직접 곱해 확인한 뒤
   $R\hat{a}R^\top = \widehat{Ra}$ (C1 모듈)로 $UZU^\top = \hat{u}_3$ 를 꺼낸다. 이 구성이
   "본질행렬 분해 4개"의 출처이고 P4 의 전부다. MVG ch.9.6 을 같은 결과의 다른 표기로 대조한다.
3. **8점 알고리즘을 먼저 틀리게 구현한다 (90분)** — 랭크-2 투영 **없이**, 정규화 **없이**
   픽셀 좌표로 돌려 본다. $\sigma_3(E)$ 가 0 이 아닌 것과 조건수가 $10^6$ 인 것을 직접 보고
   나서 (3)과 $T_i$ 를 넣는다. 깨지는 것을 본 뒤에 넣은 보정만 기억에 남는다(P5).
4. **퇴화를 만들어 본다 (60분)** — 점을 한 평면에 놓고, 그 다음 $t = 0$ 으로 놓는다. 두 경우
   모두 잔차가 작은데 자세가 틀리는 것을 보고 $\sigma_7(A)/\sigma_6(A)$ 로 감지해 본다(P6).
   이 경험이 `c7-robust-fitting-ransac` 의 퇴화 논의와 연결된다.
5. **5점은 구조만 먼저 잡는다 (120분)** — 단항식 20개를 종이에 적고 $10\times20$ → $[I|B]$ →
   작용행렬의 흐름을 그린다. 구현은 Stewénius et al. 2006 쪽이 짧다. 막히면 재현 과제의
   대안(소행렬식 다중 시작)으로 먼저 수치 결과를 얻고 나중에 작용행렬로 바꾼다.
6. **편향을 Monte Carlo 로 확인한다 (60분)** — P7 을 돌리고, 꼬리를 $3\sigma_d$ 에서 자르면
   부호가 뒤집히는 것을 직접 본다. 이 실험 하나가 "볼록성 때문에 과대추정"이라는 요약과
   실제 상황의 차이를 가르친다.
7. **논문 2편과 노트 (120분)** — Longuet-Higgins 를 먼저(두 쪽이다) 읽어 1981년의 해법에
   무엇이 없었는지 적고, 그 다음 Nistér 를 §3–4 중심으로 읽는다. 논문당 1페이지 노트는
   **반드시** 쓴다.
8. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제"에서 하나를 골라 왜 아직 안 풀렸는지
   한 문단으로 쓴다.

**통과 기준**: 백지에서 (1)과 R2 의 (ii)⇒(i) 구성을 쓸 수 있고, 재현 과제의 다섯 조건을
만족하는 코드를 갖고 있고, 공면 퇴화를 스스로 만들어 진단할 수 있고, P7 의 편향 수치를
예측·실측으로 맞춰 봤고, 논문 2편의 노트가 있다.
