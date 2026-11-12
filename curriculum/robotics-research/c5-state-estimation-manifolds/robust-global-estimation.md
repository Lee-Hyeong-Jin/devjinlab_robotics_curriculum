---
id: c5-robust-global-estimation
title: 강건 추정과 전역 최적성
summary: >-
  M-estimator 의 정류 조건이 재가중 최소제곱(IRLS)의 정규방정식과 같음을 증명하고, 영향 함수로
  유계·재하강(redescending) 커널의 차이를 설명한다. SO(2) 회전 동기화에서 쌍대 인증 행렬
  S = Λ - C 가 양반정부호면 해가 전역 최적임을 네 줄로 증명하고(SE-Sync 의 축소판), 이상치가
  들어오면 그 타이트성이 깨지는 것을 수치로 확인한다. 이상치 20% 포즈 그래프에서 강건 추정이
  ATE 를 26배 개선하는 것과 그 한계를 함께 측정한다.
objectives:
  - M-estimator 의 정류 조건에서 IRLS 가중치 w = psi(r)/r 를 유도할 수 있다.
  - 영향 함수로 유계 커널과 재하강 커널을 구별하고 각각의 실패 양상을 설명할 수 있다.
  - SO(2) 회전 동기화의 전역 최적성 인증을 빠진 줄 없이 증명할 수 있다.
  - 인증이 깨지는 조건(이상치·잡음)을 수치 실험으로 특징화할 수 있다.
  - GNC 가 왜 보장이 아닌지와 재하강 커널의 대가를 수치로 보일 수 있다.
  - TEASER 의 불변 측정 분해가 왜 문제를 쪼개는지 설명할 수 있다.
prerequisites: [c5-observability-consistency, c5-factor-graphs-map]
difficulty: 5
estimated_minutes: 660
tags: [state-estimation, robust-estimation, m-estimator, irls, se-sync, teaser, certification, research]
activities:
  - id: c5-robust-global-estimation-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 105
  - id: c5-robust-global-estimation-papers
    kind: reading
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c5-robust-global-estimation-problems
    kind: exercise
    title: 문제 세트 (유도 1 · 증명 1 · 계산 2 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: c5-robust-global-estimation-reproduction
    kind: exercise
    title: 재현 과제 — 이상치 20% 포즈 그래프, 전역 최적성 인증, breakdown (R2)
    estimated_minutes: 210
  - id: c5-robust-global-estimation-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.5.3 (Outliers). M-estimator 와 RANSAC 의 교재 진입로. 전문 PDF 무료.
  - title: "Rosen, Carlone, Bandeira & Leonard — SE-Sync (2019, IJRR)"
    url: https://arxiv.org/abs/1612.07386
    kind: article
    note: 필독 1. 역할 원전(seminal). 3-5절(볼록 완화, 랭크 계단, 전역 최적성 인증).
  - title: "Yang, Shi & Carlone — TEASER: fast and certifiable point cloud registration (2021, T-RO)"
    url: https://arxiv.org/abs/2001.07715
    kind: article
    note: 필독 2. 역할 표준(standard). 4-6절(TIM/TRIM 분해, 최대 클리크, GNC).
  - title: "Sunderhauf & Protzel — Switchable constraints for robust pose graph SLAM (2012, IROS)"
    url: https://doi.org/10.1109/IROS.2012.6385590
    kind: article
    note: 필독 3. 역할 표준(standard). 전환 변수로 이상치를 다루는 접근과 그 한계.
  - title: "Carlone, Rosen, Calafiore, Leonard & Dellaert — Lagrangian duality in 3D SLAM (2015)"
    url: https://arxiv.org/abs/1506.00746
    kind: article
    note: 권장. 쌍대 인증의 포즈 그래프 적용과 타이트성 조건. 본문 R3 의 3D 판이다.
  - title: "Fischler & Bolles — RANSAC (1981)"
    url: https://doi.org/10.1145/358669.358692
    kind: article
    note: 권장. 가설-검증식 이상치 처리의 원전. M-estimator 와의 대조로 읽는다.
  - title: "Cadena et al. — Past, present, and future of SLAM (2016)"
    url: https://arxiv.org/abs/1606.05830
    kind: article
    note: 권장. IV 절이 강건성·인증 쟁점을 정리한다.
---

# 강건 추정과 전역 최적성

## 전제와 기호

`c5-factor-graphs-map` 의 MAP·최소제곱 표기와 `c5-observability-consistency` 의 일관성 논의를
그대로 쓴다. `c5-factor-graphs-map` R1 의 "최소제곱은 가우시안 가정의 다른 이름"이 이 레슨의
출발점이다 — 이상치는 가우시안이 아니라는 뜻이다. 추가 기호:

| 기호 | 뜻 |
|---|---|
| $\rho : [0,\infty) \to [0,\infty)$ | **손실 함수(kernel)**. $\rho(0)=0$, 증가. 제곱 손실은 $\rho(r) = \tfrac12 r^2$ |
| $\psi := \rho'$ | **영향 함수(influence function)**. 측정 하나가 해에 미치는 영향의 크기 |
| $w(r) := \psi(r)/r$ | **IRLS 가중치** |
| $c$ | 커널 매개변수(임계값). 화이트닝된 잔차 단위로 잰다 |
| $\epsilon^\ast$ | **breakdown point** — 추정량이 무너지기 시작하는 이상치 비율 |
| $\mu$ | GNC 의 볼록성 매개변수. $\mu\to\infty$ 가 볼록, $\mu\to 0$ 이 원래 커널 |
| $x \in \mathbb{C}^n$, $\lvert x_k\rvert = 1$ | $SO(2)$ 회전의 복소 표현 $x_k = e^{i\theta_k}$ |
| $C$ | 동기화 데이터 행렬. $C_{ij} = e^{-i\bar\theta_{ij}}$ (Hermitian) |
| $\Lambda$, $S := \Lambda - C$ | 쌍대 변수(실수 대각)와 **인증 행렬** |

**주요 커널**(화이트닝된 잔차 노름 $r = \lVert r_k\rVert$ 에 대해):

| 커널 | $\rho(r)$ | $\psi(r)$ | $w(r)$ | 영향 |
|---|---|---|---|---|
| 제곱(L2) | $\tfrac12 r^2$ | $r$ | $1$ | **무계** — 이상치 하나가 해를 끌고 간다 |
| Huber | $r\le c$: $\tfrac12 r^2$ / $r>c$: $c r - \tfrac12 c^2$ | $\min(r, c)$ | $\min(1, c/r)$ | **유계**, 0 은 아님 |
| Cauchy | $\tfrac{c^2}{2}\log(1 + r^2/c^2)$ | $\dfrac{r}{1+r^2/c^2}$ | $\dfrac{1}{1+r^2/c^2}$ | **재하강**($r\to\infty$ 에서 $\psi\to0$) |
| TLS(truncated) | $r\le c$: $\tfrac12 r^2$ / $r>c$: $\tfrac12 c^2$ | $r\le c$: $r$ / $r>c$: $0$ | $\mathbb{1}[r\le c]$ | **재하강**, 완전 절단 |

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (M-estimator 의 정류 조건 = IRLS 의 정규방정식) [D3]** —
  $F(x) = \sum_k \rho(\lVert r_k(x)\rVert)$ 의 정류점은
  $$
  \sum_k w\big(\lVert r_k\rVert\big)\,J_k^\top r_k = 0,
    \qquad w(r) = \frac{\psi(r)}{r} \tag{1}
  $$
  를 만족하고, 이는 가중치를 **고정한** 최소제곱 $\min_\delta\sum_k w_k\lVert r_k + J_k\delta\rVert^2$
  의 정규방정식과 같다. 따라서 "가중치 갱신 → 가중 최소제곱" 반복(IRLS)의 고정점은 $F$ 의
  정류점이다. 재현 과제의 실측: Huber IRLS 가 수렴한 점에서
  $\lVert\nabla F\rVert_\infty = 3.651\times10^{-7}$.
- **R2 (강건 커널은 전역 최적을 주지 않는다; GNC 의 대가) [D2]** — $\rho$ 가 비볼록(재하강)이면
  $F$ 가 여러 지역 최솟값을 갖고 IRLS 는 초기값에 의존한다. GNC 는 볼록한 대리 함수에서
  시작해 $\mu$ 를 어닐링하지만 **전역 최적성 보장은 없다**. 재현 과제의 실측(이상치 20%):
  제곱 손실 ATE $5.4638$, Huber $0.2045$(**26.7배 개선**), GNC-TLS $0.1214$. 다만 GNC-TLS 는
  인라이어 17개를 함께 깎고, 이상치가 **없을 때도** ATE 가 $0.1151$ 이 아니라 $0.1218$ 이다 —
  재하강 커널의 대가다.
- **R3 ($SO(2)$ 회전 동기화의 전역 최적성 인증) [D3]** — $\hat x$ 가 $\max_{\lvert x_k\rvert=1} x^*Cx$
  의 정류점이고
  $$
  \Lambda := \mathrm{diag}\Big(\mathrm{Re}\big(\overline{\hat x}\odot(C\hat x)\big)\Big),
  \qquad S := \Lambda - C \tag{2}
  $$
  가 $S \succeq 0$ 을 만족하면 $\hat x$ 는 **전역** 최적해다. 증명은 네 줄이고(증명 스케치),
  $\lambda_{\min}(S) \ge -\mathrm{tol}$ 를 확인하는 것만으로 전역성을 **인증**할 수 있다.
  이것이 `rosen2019-se-sync` 가 $SO(3)$·$SE(3)$ 에서 하는 일의 축소판이다.
- **R3' (인증의 타이트성은 이상치에서 깨진다) [D2]** — $S\succeq0$ 은 완화가 **타이트**할 때만
  성립한다. 재현 과제의 실측($n=40$, 사슬 + 추가 간선): 이상치 0% 에서는 $\sigma = 0.02, 0.10,
  0.30$ 모두 $\lambda_{\min}(S) = O(10^{-16})$ 로 **인증 성공**, 이상치 10% 만 섞여도
  $\lambda_{\min}(S) < 0$ 이 되어 **인증 실패**한다(전역성을 주장할 수 없다). 즉
  **인증 가능성과 강건성은 아직 함께 가지 않는다.**
- **R4 (TEASER 의 불변 측정 분해) [D2]** — 점군 정합 $y_i = s\,R\,p_i + t + \epsilon_i$ 에서
  두 측정의 차를 취하면 $t$ 가 소거되고(TIM), 그 노름을 취하면 $R$ 까지 소거된다(TRIM).
  따라서 척도 → 회전 → 평행이동을 **차례로** 풀 수 있고, 각 부분문제가 1차원 또는 $SO(3)$ 위의
  작은 문제가 되어 최대 클리크로 인라이어를 고르고 각각을 인증 가능하게 풀 수 있다. 분해가
  강건성을 만드는 것이 아니라 **문제를 작게 만들어 인증을 가능하게** 한다는 점이 핵심이다.
- **R5 (breakdown 은 커널이 아니라 지표로 측정한다) [D1]** — 재현 과제의 sweep: 이상치
  $0 \to 11 \to 20 \to 29 \to 40\%$ 에서 ATE 가 Huber 는
  $0.1151 \to 0.2179 \to 0.2045 \to 0.2980 \to 0.8815$, GNC-TLS 는
  $0.1218 \to 0.1654 \to 0.1214 \to 0.0961 \to 0.1642$ 이다. **Huber 는 20% 의 $0.2045$ 에서
  40% 의 $0.8815$ 로 4.3배 악화되는 반면 재하강 커널은 $0.16$ 수준에 머문다** — 영향 함수의
  차이가 숫자로 나타난다. 대신 재하강 커널은 이상치가 없을 때 약간 더 나쁘다.

## 유도

### R1 — 재가중 최소제곱이 어디서 나오는가

$F(x) = \sum_k \rho(\lVert r_k(x)\rVert)$ 를 미분한다. $n_k := \lVert r_k\rVert$ 로 두고
연쇄법칙을 쓰면 $\partial n_k/\partial x = J_k^\top r_k / n_k$ 이므로

$$
\nabla F(x) = \sum_k \rho'(n_k)\,\frac{J_k^\top r_k}{n_k}
  = \sum_k \frac{\psi(n_k)}{n_k}\,J_k^\top r_k
  = \sum_k w(n_k)\,J_k^\top r_k. \tag{3}
$$

$\nabla F = 0$ 이 (1)이다. 한편 가중치를 **상수로 고정한** 가중 최소제곱
$G(x) = \tfrac12\sum_k w_k\lVert r_k(x)\rVert^2$ 의 기울기는
$\nabla G = \sum_k w_k J_k^\top r_k$ 다. 두 식이 $w_k = w(n_k)$ 에서 **글자 그대로 같다.**
따라서 다음 반복(IRLS)의 고정점은 (1)을 만족한다:

$$
w_k^{(t)} = w\big(\lVert r_k(x^{(t)})\rVert\big), \qquad
x^{(t+1)} = \arg\min_x \tfrac12\sum_k w_k^{(t)}\lVert r_k(x)\rVert^2. \tag{4}
$$

**영향 함수가 말하는 것.** (3)에서 측정 $k$ 가 기울기에 기여하는 크기는
$\lVert w(n_k)J_k^\top r_k\rVert \approx \psi(n_k)\lVert J_k\rVert$ 다. 즉 **$\psi$ 가 그
측정의 "힘"이다.**

- 제곱 손실은 $\psi(r) = r$ 로 무계 — 잔차 $10^3$ 인 이상치 하나가 인라이어 $10^6$ 개와
  맞먹는다. 재현 과제에서 이상치 6개가 ATE 를 $0.115 \to 5.46$ 으로 만드는 이유다.
- Huber 는 $\psi = \min(r,c)$ 로 유계지만 0 이 아니다 — 이상치가 **일정한 힘으로 계속**
  해를 끈다. 이상치가 많아지면 그 합이 커져 무너진다(R5 의 40% 행).
- Cauchy·TLS 는 $\psi \to 0$ (재하강) — 충분히 먼 측정은 **완전히 무시**된다. 대가는 비볼록성과
  인라이어 손실이다(재현 과제에서 GNC-TLS 가 인라이어 17개를 깎고, 이상치가 없을 때도 ATE 가
  $0.1151$ 대신 $0.1218$ 이다).

**가정이 깨지는 곳**: (3)은 $n_k > 0$ 에서만 유효하다. $n_k \to 0$ 에서 $w(n_k) = \psi(n_k)/n_k$
는 0/0 이고, 커널마다 극한이 다르다(Huber·TLS 는 1, Cauchy 는 1). 구현에서는
$n_k < 10^{-12}$ 를 분기 처리한다. 더 중요한 가정은 **잔차가 측정마다 독립**이라는 것이다 —
지각 모호성(perceptual aliasing)으로 이상치가 **뭉쳐서** 들어오면 그들끼리 서로 일관되어
강건 커널이 그 집단을 인라이어로 받아들인다(문제 P6).

### R2 — 비볼록 커널과 GNC 의 어닐링

재하강 커널은 $\rho$ 가 비볼록이므로 $F$ 에 지역 최솟값이 여럿 생긴다. GNC 는 $\rho$ 를
매개변수 $\mu$ 를 가진 대리 함수족 $\rho_\mu$ 로 바꾸되 ⓐ $\mu \to \infty$ 에서 $\rho_\mu$ 가
볼록(제곱 손실에 가까움) ⓑ $\mu \to 0$ 에서 $\rho_\mu \to \rho$ 가 되게 만든다. 그 다음
$\mu$ 를 크게 시작해 조금씩 줄이면서 매번 IRLS 를 돌린다 — 볼록한 문제의 해를 비볼록 문제의
초기값으로 **이어 붙이는** 전략이다.

TLS 에 대한 GNC 가중치는 닫힌 형태로 나온다(`yang2021-teaser` §6):

$$
w_k = \begin{cases}
1 & n_k^2 \le \dfrac{\mu}{\mu+1}c^2,\\[4pt]
\dfrac{c}{n_k}\sqrt{\mu(\mu+1)} - \mu & \dfrac{\mu}{\mu+1}c^2 < n_k^2 < \dfrac{\mu+1}{\mu}c^2,\\[4pt]
0 & n_k^2 \ge \dfrac{\mu+1}{\mu}c^2.
\end{cases} \tag{5}
$$

$\mu$ 가 크면 중간 구간이 넓어 거의 모든 측정이 부분 가중을 받고(볼록에 가깝다), $\mu$ 가
작아지면 양 끝의 0/1 구간이 넓어져 절단에 가까워진다.

**가정이 깨지는 곳**: GNC 는 **휴리스틱**이다. ⓐ $\mu$ 의 초기값과 감소 비율에 대한 이론이 없고
ⓑ 각 $\mu$ 에서 전역 최적을 찾는다는 보장도 없고 ⓒ 어닐링 경로가 올바른 분지(basin)로
이어진다는 보장도 없다. 실무에서 잘 동작하는 이유는 "이상치가 소수이고 서로 일관되지 않다"는
문제 구조이며, 그 구조가 깨지면 GNC 도 깨진다. 재현 과제의 sweep 에서 GNC-TLS 가 이상치 40%
에서도 ATE $0.1642$ 를 내는 것은 **보장이 아니라 이 문제 인스턴스의 성질**이다.

### R3 — $SO(2)$ 동기화의 인증 행렬을 만든다

회전만 있는 동기화를 본다. 각 노드에 $\theta_k$, 간선 $(i,j)$ 에 측정
$\bar\theta_{ij} \approx \theta_j - \theta_i$ 가 주어진다. $x_k := e^{i\theta_k}$ 로 두면
$e^{-i\bar\theta_{ij}}\,\bar x_i x_j \approx 1$ 이므로, 최대화할 목적은

$$
\max_{x\in\mathbb{C}^n,\ \lvert x_k\rvert = 1}\ x^*Cx, \qquad
C_{ij} = e^{-i\bar\theta_{ij}},\ C_{ji} = e^{+i\bar\theta_{ij}},\ C_{ii} = 0. \tag{6}
$$

$x^*Cx = 2\sum_{(i,j)}\mathrm{Re}\big(\bar x_i x_j e^{-i\bar\theta_{ij}}\big)$ 이므로 이것은
각 간선의 일치도를 더한 것이고, 측정이 완벽하면 최대값이 간선 수의 2배다. **이것은 비볼록
문제다** — 제약 $\lvert x_k\rvert = 1$ 이 비볼록이다.

라그랑주 함수를 쓴다. 제약을 $\lvert x_k\rvert^2 = 1$ 로 보고 실수 승수 $\Lambda_{kk}$ 를 붙이면
최소화 형태 $\min -x^*Cx$ 의 정류 조건은

$$
-C\hat x + \Lambda\hat x = 0
  \quad\Longleftrightarrow\quad
  C\hat x = \Lambda\hat x, \qquad \Lambda \text{ 실수 대각}. \tag{7}
$$

(7)의 $k$ 번째 성분에 $\bar{\hat x}_k$ 를 곱하고 실수부를 취하면
$\Lambda_{kk} = \mathrm{Re}\big(\bar{\hat x}_k (C\hat x)_k\big)$ 다($\lvert\hat x_k\rvert = 1$).
이것이 (2)다. 그리고 (7)은 바로 $S\hat x = (\Lambda - C)\hat x = 0$ 을 뜻한다 —
**$\hat x$ 는 항상 $S$ 의 영공간에 있다.** 남은 질문은 $S$ 가 양반정부호인가뿐이고, 그것이
증명 스케치의 네 줄이다.

**인증을 실제로 계산하는 절차.** ⓐ 임의의 국소 해법으로 $\hat x$ 를 구한다(스펙트럼 초기값 +
좌표별 상승 $x_k \leftarrow (C x)_k / \lvert (Cx)_k\rvert$ — 이 갱신은 목적함수를 단조
증가시킨다). ⓑ (2)로 $\Lambda$, $S$ 를 만든다. ⓒ $\lambda_{\min}(S)$ 를 계산한다. 음수가 아니면
**끝** — $\hat x$ 가 전역 최적이다. 음수면 전역성을 주장할 수 없다(해가 틀렸다는 뜻은 아니다).

**가정이 깨지는 곳**: $S \succeq 0$ 은 **충분**조건이다. $\lambda_{\min}(S) < 0$ 이어도 $\hat x$ 가
전역 최적일 수 있다 — 인증이 실패한 것이고 해가 실패한 것이 아니다. 또 (2)(7)은 **회전만**
있는 문제다. 포즈 그래프 전체($SE(d)$)로 가면 평행이동을 소거해야 하고, 그 소거가
`rosen2019-se-sync` 의 첫 단계(일반화 Schur 보완)다 — `c5-factor-graphs-map` R3 과 같은 연산이다.

### R4 — TEASER 는 왜 문제를 쪼개는가

점군 정합 모형은 $y_i = s\,R\,p_i + t + \epsilon_i$ ($s>0$ 척도, $R\in SO(3)$, $t\in\mathbb{R}^3$)
이고, 대응 $i$ 중 상당수가 이상치다. 핵심은 **미지수를 하나씩 소거하는 불변량**이다.

1. **TIM (translation-invariant measurement).** 두 대응의 차를 취하면
   $$
   y_j - y_i = s\,R\,(p_j - p_i) + (\epsilon_j - \epsilon_i) \tag{8}
   $$
   로 $t$ 가 **사라진다.** 남은 미지수는 $s$ 와 $R$ 이다.
2. **TRIM (translation- and rotation-invariant measurement).** (8)의 노름을 취하면 $R$ 이
   노름을 보존하므로
   $$
   \lVert y_j - y_i\rVert \approx s\,\lVert p_j - p_i\rVert \tag{9}
   $$
   로 $R$ 까지 **사라진다.** 남은 미지수는 **스칼라 $s$ 하나**다.
3. **쪼갠 결과.** (9)는 1차원 강건 추정이므로 인증 가능하게 풀린다(구간 투표 또는 적응적
   voting). $s$ 를 알면 (8)이 $SO(3)$ 위의 강건 회전 추정이 되고, $R$ 을 알면 $t$ 가
   성분별 1차원 강건 추정이 된다.
4. **최대 클리크.** (9)를 만족하는 TIM 쌍만 간선으로 남긴 그래프에서 **최대 클리크**를 찾으면
   서로 일치하는 대응 집합을 얻는다 — 이상치를 **조합적으로** 걸러내는 단계다.

**핵심 해석**: 분해 자체가 강건성을 주지 않는다. 분해가 하는 일은 **각 부분문제를 인증 가능한
크기로 줄이는 것**이고, 그래서 TEASER 는 "fast and certifiable"이라고 말할 수 있다.
`c5-factor-graphs-map` R3 의 소거가 비용을 줄였듯, 여기서는 소거가 **인증 가능성**을 만든다.

**가정이 깨지는 곳**: 2단계는 잡음이 $R$ 과 무관하게 노름에 들어간다고 본다. 잡음이 크면
(9)의 양변 차가 $s$ 추정을 편향시킨다. 4단계의 최대 클리크는 NP-난해이고(실무에서는 근사),
그리고 전체 절차는 **이상치가 서로 일관되지 않다**는 가정에 의존한다 — 뭉친 이상치는
자기들끼리 큰 클리크를 만들 수 있다.

## 증명 스케치

### R1 — IRLS 고정점 = M-estimator 정류점

**가설** H1: $\rho$ 가 $(0,\infty)$ 에서 미분가능하고 $\psi = \rho'$ 이다. H2: 모든 $k$ 에 대해
$\lVert r_k(x)\rVert > 0$ 이다. H3: $r_k$ 가 미분가능하고 $J_k = \partial r_k/\partial x$ 다.
**결론** C1: (3)이 성립하므로 $\nabla F = 0 \iff$ (1). C2: (4)의 고정점 $x^\ast$ 는 (1)을
만족한다. C3: **역은 성립하지 않는다** — (1)의 해가 $F$ 의 최솟값이라는 보장은 없다.

**전략**: 연쇄법칙 한 번과 "가중치를 고정하면 다른 함수"라는 관찰.

1. **기울기.** $n_k = \lVert r_k\rVert = \sqrt{r_k^\top r_k}$ 이므로
   $\partial n_k/\partial x = J_k^\top r_k/n_k$ (H2 로 분모가 0 이 아니다). 연쇄법칙으로 (3).
2. **고정점.** (4)에서 $x^{(t+1)} = x^{(t)} = x^\ast$ 라면, $x^\ast$ 는 가중치
   $w_k = w(\lVert r_k(x^\ast)\rVert)$ 로 고정된 가중 최소제곱의 정류점이므로
   $\sum_k w_k J_k^\top r_k = 0$ 이고, 그 $w_k$ 가 바로 $w(n_k)$ 다. C2.
3. **왜 역이 아닌가.** (1)은 1차 조건이므로 지역 최솟값·지역 최댓값·안장점을 모두 포함한다.
   $\rho$ 가 비볼록이면 (1)의 해가 여러 개이고 IRLS 는 초기값이 속한 분지의 해로 간다. C3.
4. **단조성도 보장이 아니다.** 각 IRLS 반복이 $F$ 를 줄인다는 것은 **일반적으로 참이 아니다.**
   $\rho$ 가 $r^2$ 의 오목 증가 함수로 쓰일 때(Huber·Cauchy·TLS 는 그렇다) majorization-
   minimization 논증으로 단조 감소를 얻을 수 있으나, 가중 최소제곱을 **완전히** 풀어야 하고
   GN 을 몇 번만 돌리면 보장이 사라진다.

**가설을 지우면**: H2 를 빼면 1단계의 $J_k^\top r_k/n_k$ 가 정의되지 않는다 — 구현의 0/0 분기가
이 가설을 메우는 것이다. H1 에서 $\rho$ 의 미분가능성을 빼면(예: 순수 절단을 지점에서 미분)
$\psi$ 가 불연속이 되어 IRLS 가 두 가중치 사이에서 진동할 수 있다.

(생략: majorization-minimization 으로서의 IRLS 수렴 해석. Barfoot SER ch.5.3 과
`yang2021-teaser` §6.)

### R3 — $S \succeq 0$ 이면 전역 최적

**가설** H1: $C$ 가 Hermitian이다. H2: $\hat x$ 가 실현가능($\lvert\hat x_k\rvert = 1$)하고
(7)을 만족한다($\Lambda$ 는 (2)로 정의된 실수 대각). H3: $S := \Lambda - C \succeq 0$.
**결론** C: 모든 실현가능한 $x$ 에 대해 $x^*Cx \le \hat x^*C\hat x$. 즉 $\hat x$ 는 **전역**
최적해다.

**전략**: 제약을 써서 목적함수를 $S$ 의 2차형식으로 **정확히** 바꿔 쓰고, $S\succeq0$ 으로
하한을 얻는다. 완화를 풀 필요도, 쌍대 문제를 세울 필요도 없다.

1. **제약이 주는 항등식.** 실현가능한 임의의 $x$ 에 대해
   $$
   x^*\Lambda x = \sum_k \Lambda_{kk}\lvert x_k\rvert^2 = \sum_k\Lambda_{kk} = \operatorname{tr}\Lambda,
   $$
   즉 $x^*\Lambda x$ 가 **$x$ 와 무관한 상수**다. 여기가 증명의 심장이다.
2. **목적함수 다시 쓰기.** 따라서
   $$
   -x^*Cx = -x^*Cx + x^*\Lambda x - \operatorname{tr}\Lambda = x^*Sx - \operatorname{tr}\Lambda .
   $$
3. **하한.** H3 으로 $x^*Sx \ge 0$ 이므로 $-x^*Cx \ge -\operatorname{tr}\Lambda$, 즉
   $x^*Cx \le \operatorname{tr}\Lambda$ 가 **모든** 실현가능한 $x$ 에 대해 성립한다.
4. **하한의 달성.** H2 의 (7)에서 $S\hat x = \Lambda\hat x - C\hat x = 0$ 이므로
   $\hat x^*S\hat x = 0$ 이고, 2단계를 $\hat x$ 에 적용하면
   $\hat x^*C\hat x = \operatorname{tr}\Lambda$. 3단계의 상한을 정확히 달성하므로 C. $\square$

5. **SDP 완화와의 관계.** (6)의 SDP 완화는
   $\max\{\operatorname{tr}(CX) : X\succeq0,\ X_{kk}=1\}$ 이고, 위 논증은 그 완화의 쌍대 최적값이
   $\operatorname{tr}\Lambda$ 임을 보인 것과 같다. 따라서 $S\succeq0$ 은 **완화가 타이트하고
   SDP 해의 랭크가 1** 인 것과 동등하다. `rosen2019-se-sync` 의 "랭크 계단(Riemannian
   staircase)"은 $SO(3)$ 에서 이 랭크 조건을 점진적으로 확인하는 절차다.

**가설을 지우면**: H3 을 빼면 3단계의 하한이 사라져 아무 말도 할 수 없다 — 그래서 인증이
**충분조건**이다. H2 의 정류성을 빼면 4단계에서 $S\hat x \ne 0$ 이 되어 하한을 달성하지 못한다
(이때 $\operatorname{tr}\Lambda$ 는 여전히 **상한**을 주므로, $\hat x$ 의 **최적성 간극**
$\operatorname{tr}\Lambda - \hat x^*C\hat x$ 를 계산해 "얼마나 최적에 가까운가"를 말할 수 있다 —
인증이 실패했을 때도 쓸 수 있는 유용한 수치다).

(생략: $SE(d)$ 로의 확장에서 평행이동을 소거하는 일반화 Schur 보완과 랭크 계단의 수렴.
`rosen2019-se-sync` §3-5 와 `carlone2015-lagrangian-duality`.)

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** 표기표의 네 커널에 대해 ⓐ $\psi$ 와 $w$ 를 유도하고, ⓑ $r\to0$ 과
$r\to\infty$ 에서의 극한을 구하고, ⓒ 어느 것이 재하강인지 판정하고, ⓓ Geman-McClure
$\rho(r) = \dfrac{c^2 r^2}{2(c^2 + r^2)}$ 를 표에 추가하라.
*해답 스케치*: ⓓ 는 $\psi(r) = \dfrac{c^4 r}{(c^2+r^2)^2}$, $w(r) = \dfrac{c^4}{(c^2+r^2)^2}$ 이고
$\psi$ 가 $r = c/\sqrt3$ 에서 최대를 지나 0 으로 떨어지므로 **재하강**이다. ⓑ 에서 모든 커널이
$r\to0$ 에서 $w\to1$ (제곱 손실과 일치)인 것을 확인하는 것이 핵심이다 — 커널은 **큰 잔차에서만**
다르다.

**P2 (증명, ★★★, R3)** R3 의 증명을 빠진 줄 없이 쓰고, 다음을 보여라: ⓐ $\Lambda$ 가 (2)로
정의될 때 $S\hat x = 0$ 이 자동임을, ⓑ $\operatorname{tr}\Lambda$ 가 $S\succeq0$ 여부와
무관하게 항상 **상한**임을, ⓒ 그로부터 인증이 실패했을 때도 최적성 간극을 계산할 수 있음을.
ⓓ SDP 완화의 랭크 1 조건과 $S\succeq0$ 이 동등함을 쌍대성으로 논하라.
*전략 + 핵심 부등식*: ⓑ 가 핵심 — 1·2 단계는 H3 을 쓰지 않으므로
$x^*Cx = \operatorname{tr}\Lambda - x^*Sx$ 가 항상 성립하고, $S$ 의 최소 고윳값이 음수면
$x^*Sx \ge n\lambda_{\min}(S)$ 로 완화된 상한을 얻는다. ⓓ 는 약쌍대성과 보완 여유(complementary
slackness)를 쓴다. 전개는 숨긴다.

**P3 (계산, ★, R2·R5)** 재현 과제의 이상치 sweep 을 수행하고 ⓐ 세 커널의 ATE 표, ⓑ 이상치 20%
에서 제곱 손실 대 Huber 의 개선 배수, ⓒ Huber 가 무너지기 시작하는 이상치 비율을 보고하라.
*정답*: ⓐ 재현 과제 수용 기준 2의 표. ⓑ $5.4638 / 0.2045 = 26.7$ 배. ⓒ 이상치 40%
(Huber ATE 가 $0.2980 \to 0.8815$ 로 약 3배 뛴다; 같은 구간에서 GNC-TLS 는
$0.0961 \to 0.1642$ 로 Huber 보다 5배 이상 좋은 자리에 머문다). 허용오차 ATE $\pm0.02$.
검산: 이상치 0% 에서 **L2 와 Huber** 의 ATE 가 같은지($0.1151$) 확인한다 — 다르면 유계 커널이
인라이어를 건드리고 있다는 뜻이다. GNC-TLS 는 0% 에서도 $0.1218$ 로 조금 나쁘다.

**P4 (계산, ★★, R3·R3')** $n = 40$ 동기화 문제에서 ⓐ 이상치 0% 에서 $\sigma \in
\{0.02, 0.10, 0.30\}$ 의 $\lambda_{\min}(S)$ 와 $\lVert S\hat x\rVert$, ⓑ 이상치
$\{10, 20, 40\}\%$ 에서의 $\lambda_{\min}(S)$, ⓒ 각 경우의 각도 RMSE 를 구하라.
ⓓ 인증이 실패한 경우의 **최적성 간극**(P2ⓒ)을 계산하라.
*정답*: ⓐ $\lambda_{\min}(S)$ 가 세 경우 모두 $\lvert\cdot\rvert < 10^{-14}$
(참조 $7.8\times10^{-16}$, $-4.4\times10^{-16}$, $-3.7\times10^{-16}$), $\lVert S\hat x\rVert
\approx 3.3\times10^{-14}$, 각도 RMSE $0.0298 / 0.1492 / 0.4473$ rad. ⓑ 전부 음수 —
$\sigma = 0.02$ 에서 $-6.8\times10^{-3} / -7.4\times10^{-2} / -8.9\times10^{-2}$ (10회 평균).
ⓒ 각도 RMSE 가 $0.72 / 1.15 / 1.75$ rad 로 악화. 허용오차: ⓐ 는 자리수, ⓑⓒ 는 상대오차 30%
(난수 평균이므로).
*ⓓ의 채점 포인트*: 간극이 $\operatorname{tr}\Lambda - \hat x^*C\hat x$ 가 아니라
$-n\lambda_{\min}(S)$ 규모의 **완화된** 상한에서 나온다는 점을 쓰면 통과.

**P5 (구현, ★★★, R1·R2)** 재현 과제의 포즈 그래프에서 ⓐ Huber IRLS, ⓑ GNC-TLS 를 구현하라.
*루브릭*: ⓐ IRLS 고정점에서 $\lVert\nabla F\rVert_\infty < 10^{-6}$ 을 보고(R1 의 수치 검증)
ⓑ 이상치 탐지 결과를 혼동 행렬로 보고(참조: Huber 는 6/6 탐지·오탐 0, GNC-TLS 는 6/6 탐지·
인라이어 17개 깎음) ⓒ $c$ 를 $1\!\sim\!10$ 으로 쓸어 가며 ATE 와 오탐 수의 교환을 그리고
ⓓ GNC 의 $\mu$ 어닐링 스케줄을 바꿔 결과가 달라지는 것을 보여(R2 의 "보장 아님") 수치로 제시.

**P6 (반례, ★★, R1·R2·R4)** "이상치 비율이 breakdown point 보다 낮으면 강건 추정이 작동한다"가
거짓임을 보여라. ⓐ 서로 **일관된** 이상치 집단(예: 같은 잘못된 루프 클로저를 여러 번 넣기)을
구성해 이상치 비율이 10% 여도 강건 커널이 그 집단을 인라이어로 받아들이는 것을 수치로 보이고,
ⓑ TEASER 의 최대 클리크 단계가 이 경우에도 실패하는 이유를 쓰고, ⓒ 어떤 추가 정보가 있으면
구별되는지 쓰라.
*성질 체크리스트*: ⓐ 는 이상치들이 **서로 일치**해야 한다 — 무작위 이상치로는 재현되지 않는다.
ⓑ 는 일관된 이상치 집단이 큰 클리크를 만든다는 점이다. ⓒ 는 외부 정보(절대 측정, 시간 순서,
외관 기반 검증) 또는 가설 수를 세는 조합적 논증을 쓰면 통과. "더 강건한 커널을 쓰면 된다"는 미달.

**P7 (논문, ★★, R3·R4)** `rosen2019-se-sync` 3-5절과 `yang2021-teaser` 4-6절을 읽고
ⓐ 두 논문이 각각 **무엇을 인증하는가**를 한 문장씩 쓰고, ⓑ SE-Sync 의 인증이 이상치가 있을 때
무엇을 말하는지(본문 R3' 와 대조), ⓒ 두 논문의 "certifiable"이 같은 뜻인지 다른 뜻인지 논하라.
*루브릭*: ⓐ SE-Sync 는 "주어진(이상치 없는) 최소제곱 문제의 전역 최적성", TEASER 는 "분해된
부분문제의 전역 최적성 + 인라이어 집합의 조합적 선택"임을 구분하면 통과. ⓒ 가 핵심 — 전자는
목적함수의 전역 최적성이고 후자는 **올바른 모형을 골랐는지**에 대한 보장이 아니라는 점을 짚으면
우수. 재현 과제의 R3' 수치를 인용하면 더 좋다.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Rosen, Carlone, Bandeira & Leonard, "SE-Sync: a certifiably correct algorithm for
   synchronization over the special Euclidean group" (2019, IJRR)** — 역할: `원전(seminal)`.
   <https://arxiv.org/abs/1612.07386> (3-5절)
   추가 질문: ⓐ 평행이동을 소거하는 단계가 `c5-factor-graphs-map` R3 의 Schur 보완과 같은
   연산인가? ⓑ "certifiably correct"가 보장하는 것과 보장하지 않는 것을 각각 한 문장으로.
   ⓒ 랭크 계단이 종료하지 않는 경우가 있는가?
2. **Yang, Shi & Carlone, "TEASER: fast and certifiable point cloud registration" (2021,
   IEEE T-RO)** — 역할: `표준(standard)`. <https://arxiv.org/abs/2001.07715> (4-6절)
   추가 질문: ⓐ TIM/TRIM 분해가 잡음을 어떻게 전파시키며 그것이 척도 추정을 편향시키는가?
   ⓑ 최대 클리크가 NP-난해인데 저자들이 실제로 무엇을 계산하는가? ⓒ GNC 절(§6)의 보장은
   무엇인가?
3. **Sunderhauf & Protzel, "Switchable constraints for robust pose graph SLAM" (2012, IROS)** —
   역할: `표준(standard)`. <https://doi.org/10.1109/IROS.2012.6385590>
   추가 질문: ⓐ 전환 변수(switch variable)를 상태에 넣는 것이 M-estimator 와 수학적으로 어떻게
   다른가(힌트: 주변화하면 어떤 커널이 되는가)? ⓑ 전환 변수의 사전분포가 하는 역할은?
   ⓒ 이 방법이 뭉친 이상치에 대해 어떻게 행동하겠는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, Part A 가 30초 이내, Part B 가
1분 이내. 메모리 200MB 이하. numpy + scipy.sparse 만 쓴다.

**입력 데이터**는 아래 두 생성기가 만든다(결정론적·고정 시드). 외부 데이터셋이 필요 없다.

**Part A — 이상치 20% 포즈 그래프.** `c5-factor-graphs-map` 의 SE(2) 포즈 그래프에 이상치
루프 클로저를 섞는다. 제곱 손실 GN, Huber IRLS, GNC-TLS 를 비교한다.

```python
"""c5-robust-global-estimation Part A: 이상치가 섞인 SE(2) 포즈 그래프 생성기."""

import numpy as np

SEED = 20261112
SIGMA_ODOM = np.array([0.02, 0.02, 0.01])
SIGMA_LOOP = np.array([0.05, 0.05, 0.02])
SIGMA_ANCHOR = np.array([1e-3, 1e-3, 1e-3])


def wrap(a):
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def rot(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]])


def between(xi, xj):
    return np.array([*(rot(xi[2]).T @ (xj[:2] - xi[:2])), wrap(xj[2] - xi[2])])


def make_graph(outlier_frac=0.2, laps=2, per_lap=50, radius=5.0, every=2, seed=SEED):
    """참값, 간선, 측정, 이상치 마스크. 이상치는 무작위 상대 측정을 가진 추가 간선이다."""
    rng = np.random.default_rng(seed)
    n = laps * per_lap
    ang = 2.0 * np.pi * np.arange(n) / per_lap
    gt = np.column_stack([radius * np.cos(ang), radius * np.sin(ang), wrap(ang + np.pi / 2)])
    edges = [(i, i + 1, SIGMA_ODOM) for i in range(n - 1)]
    loops = [(i, i + per_lap, SIGMA_LOOP) for i in range(0, per_lap - 2, every)]
    n_out = int(round(outlier_frac * len(loops) / (1.0 - outlier_frac)))
    out_pairs = []
    for _ in range(n_out):
        i, j = rng.choice(n, 2, replace=False)
        out_pairs.append((int(min(i, j)), int(max(i, j)), SIGMA_LOOP))
    edges = edges + loops + out_pairs
    meas, is_out = [], []
    for k, (i, j, s) in enumerate(edges):
        if k >= len(edges) - n_out:
            meas.append(
                np.array([rng.uniform(-6, 6), rng.uniform(-6, 6), rng.uniform(-np.pi, np.pi)])
            )
            is_out.append(True)
        else:
            meas.append(between(gt[i], gt[j]) + s * rng.standard_normal(3))
            is_out.append(False)
    return gt, edges, np.array(meas), np.array(is_out)
```

잔차와 야코비안은 `c5-factor-graphs-map` 재현 과제의 (15)(16)을 그대로 쓰고, 앵커 인자도 같다.
가중치는 화이트닝된 잔차 노름 $n_k = \lVert r_k\rVert$ 에 대해 적용한다(**$3\times3$ 블록을
한 덩어리로** 가중한다 — 성분별로 가중하면 회전과 평행이동이 분리되어 커널의 의미가 달라진다).
초기값은 루프 클로저를 쓰지 않은 추측 항법이다. 커널 매개변수는 $c = 3$ 을 쓴다
(자유도 3의 잔차 노름에서 $\chi^2_3$ 의 97% 분위에 해당한다).

**Part B — $SO(2)$ 동기화의 전역 최적성 인증.** 아래 생성기를 쓴다.

```python
"""c5-robust-global-estimation Part B: SO(2) 회전 동기화와 인증 행렬."""

import numpy as np


def make_sync(n=40, sigma=0.02, outlier_frac=0.0, seed=100, extra_edges=3):
    """참 각도, 간선, 상대 측정, 이상치 마스크."""
    rng = np.random.default_rng(seed)
    th = rng.uniform(-np.pi, np.pi, n)
    th[0] = 0.0
    edges = [(k, (k + 1) % n) for k in range(n)]
    for _ in range(extra_edges * n // 10):
        i, j = rng.choice(n, 2, replace=False)
        if i != j:
            edges.append((int(i), int(j)))
    meas, is_out = [], []
    for i, j in edges:
        if rng.random() < outlier_frac:
            meas.append(rng.uniform(-np.pi, np.pi))
            is_out.append(True)
        else:
            meas.append(th[j] - th[i] + rng.normal(scale=sigma))
            is_out.append(False)
    return th, edges, np.array(meas), np.array(is_out)


def build_C(n, edges, meas):
    """Hermitian 데이터 행렬: C_ij = exp(-i * meas_ij), C_ji = conj(C_ij)."""
    C = np.zeros((n, n), dtype=complex)
    for (i, j), m in zip(edges, meas, strict=True):
        C[i, j] += np.exp(-1j * m)
        C[j, i] += np.exp(1j * m)
    return C


def certificate(C, x):
    """Lambda = diag(Re(conj(x) * (C x))), S = Lambda - C. S >= 0 이면 x 가 전역 최적."""
    lam = np.real(np.conj(x) * (C @ x))
    S = np.diag(lam).astype(complex) - C
    ev = np.linalg.eigvalsh(S)
    return float(ev[0]), float(np.linalg.norm(S @ x)), float(np.sum(lam))
```

국소 해법은 **좌표별 상승**을 쓴다 — $C$ 의 최대 고유벡터를 단위 모듈러스로 투영해 초기값으로
두고, $x_k \leftarrow (Cx)_k/\lvert(Cx)_k\rvert$ 를 한 좌표씩 갱신한다(이 갱신은 목적함수를
단조 증가시키므로 수렴한다). 게이지는 $x_0$ 을 양의 실수로 정규화해 고정한다.

**수용 기준 — 네 조건을 모두 만족해야 통과다.**

1. **Part A (이상치 20%)** — 100 포즈, 간선 129개(오도메트리 99 + 루프 클로저 24 + 이상치 6,
   루프 클로저 간선의 **20%**), 추측 항법 ATE $0.2874$. 세 커널의 ATE 가

   | 커널 | ATE (m) |
   |---|---|
   | 제곱 손실(L2) | $5.4638$ |
   | Huber ($c=3$) | $0.2045$ |
   | GNC-TLS ($c=3$) | $0.1214$ |

   허용오차 $\pm0.01$. 개선 배수 $5.4638/0.2045 = 26.7$ 배 (블루프린트의 "2배 이상"을 크게
   넘는다). 그리고 Huber IRLS 고정점에서 $\lVert\nabla F\rVert_\infty < 10^{-6}$
   (참조 $3.651\times10^{-7}$) — R1 의 수치 검증이다.
2. **Part A (sweep)** — 이상치 비율을 바꿔 아래를 재현한다(ATE, 허용오차 $\pm0.02$).

   | 이상치 | 간선 수 | L2 | Huber | GNC-TLS |
   |---|---|---|---|---|
   | 0% | 0 | $0.1151$ | $0.1151$ | $0.1218$ |
   | 11% | 3 | $3.8666$ | $0.2179$ | $0.1654$ |
   | 20% | 6 | $5.4638$ | $0.2045$ | $0.1214$ |
   | 29% | 10 | $4.6225$ | $0.2980$ | $0.0961$ |
   | 40% | 16 | $5.7145$ | $0.8815$ | $0.1642$ |

   **0% 행에서 L2 와 Huber 가 같아야 한다**($0.1151$) — 유계 커널이 인라이어를 건드리지 않는다는
   점검이다. GNC-TLS 는 같지 않고($0.1218$) 그것이 재하강 커널의 대가다. 그리고 Huber 가 20%
   $\to$ 40% 에서 $0.2045 \to 0.8815$ 로 4.3배 악화되는 반면 재하강 커널은 $0.16$ 수준에
   머무는 것을 보고한다.
3. **Part B (인증 성공)** — 이상치 0%, $n = 40$ 에서 $\sigma \in \{0.02, 0.10, 0.30\}$ 모두
   $\lvert\lambda_{\min}(S)\rvert < 10^{-14}$ (참조 $7.8\times10^{-16}$, $-4.4\times10^{-16}$,
   $-3.7\times10^{-16}$) 이고 $\lVert S\hat x\rVert < 10^{-12}$ (참조 $3.3\times10^{-14}$).
   각도 RMSE 는 $0.0298 / 0.1492 / 0.4473$ rad (10회 평균, 상대오차 20% 이내).
   **잡음이 $\sigma = 0.3$ 까지 커져도 인증이 성립한다** — 완화의 타이트성은 잡음에 꽤 강하다.
4. **Part B (인증 실패)** — 이상치 $\{10, 20, 40\}\%$ 에서 $\lambda_{\min}(S) < -10^{-4}$
   (참조 $\sigma=0.02$ 에서 $-6.8\times10^{-3}$, $-7.4\times10^{-2}$, $-8.9\times10^{-2}$;
   10회 평균, 상대오차 30% 이내) 이고 $\lVert S\hat x\rVert$ 는 여전히 $10^{-13}$ 규모다
   (정류점은 맞지만 전역이 아니다). 각도 RMSE 가 $0.72 / 1.15 / 1.75$ rad 로 악화된다.
   **이상치가 들어오면 전역 최적성을 인증할 수 없다**는 것이 이 Part 의 결론이다.

**비교 대상**: ⓐ Part A 의 베이스라인은 제곱 손실 GN(=`c5-factor-graphs-map` 의 솔버)이다.
ⓑ 두 번째 베이스라인은 **이상치를 손으로 제거한** 그래프의 L2 해다 — 강건 추정의 상한을 준다
(참조: 0% 행의 $0.1151$). ⓒ Part B 의 베이스라인은 스펙트럼 해(최대 고유벡터를 투영한 것)이고,
좌표별 상승이 그것을 얼마나 개선하는지 함께 보고한다. 선택: `scipy.optimize` 로 같은 목적함수를
풀어 좌표별 상승과 같은 값에 도달하는지 확인한다.

**보고할 수치**: 위 네 조건의 모든 값, Part A 의 이상치 탐지 혼동 행렬(참조: Huber 6/6 탐지·
오탐 0, GNC-TLS 6/6 탐지·인라이어 17개 깎음), 그리고 Part B 에서 인증이 실패한 경우의
최적성 간극 상한(P2ⓒ).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| Part A 의 0% 행에서 세 커널이 다르다 | $c$ 가 너무 작아 인라이어도 깎인다 | 인라이어 잔차 노름의 분포를 보고 $c$ 가 99% 분위보다 큰지 확인 |
| Huber 가 L2 와 같은 ATE | 가중치를 성분별로 적용했거나 잔차를 화이트닝하지 않았다 | $n_k$ 가 $3\times3$ 블록의 노름인지, 가중치가 $\min(1,c/n_k)$ 인지 확인 |
| IRLS 가 진동한다 | 가중치 갱신마다 GN 을 1회만 돌렸거나 $c$ 가 잔차 분포 경계에 있다 | 내부 GN 반복을 3회로 늘리고 $F$ 를 매 반복 출력한다 |
| $\lVert\nabla F\rVert$ 가 $10^{-2}$ 규모 | 기울기를 (3)이 아니라 제곱 손실로 계산했다 | 가중치 $w(n_k)$ 가 기울기 식에 들어갔는지 확인 |
| GNC-TLS 가 모든 간선을 0 으로 깎는다 | $\mu$ 초기값이 너무 작아 처음부터 절단에 가깝다 | $\mu$ 를 $\max_k n_k^2/c^2$ 규모로 시작해 **감소**시킨다 |
| Part B 의 각도 오차가 $\pi$ 규모 | $C_{ij}$ 의 지수 부호가 뒤집혔다 | $C_{ij} = e^{-i\bar\theta_{ij}}$ 인지 확인하고 $\sigma=0$ 에서 참값이 나오는지 본다 |
| Part B 의 $\lVert S\hat x\rVert$ 가 $10^{-1}$ 규모 | 국소 해법이 수렴하지 않았다(동시 갱신은 진동할 수 있다) | 좌표별(Gauss-Seidel) 갱신인지 확인하고 반복 수를 늘린다 |
| 이상치 0% 에서도 $\lambda_{\min}(S)$ 가 음수 | 게이지를 고정하지 않았거나 $\Lambda$ 의 실수부를 취하지 않았다 | $\Lambda$ 가 실수 대각인지, $x_0$ 을 정규화했는지 확인 |

## 열린 문제

- **(열린 문제) 인증 가능성과 강건성을 함께 갖는 방법** — R3 의 인증은 **이상치 없는** 최소제곱
  문제의 전역 최적성을 증명한다. R3' 가 보여 주듯 이상치가 10% 만 섞여도 타이트성이 깨져
  인증이 실패한다. TEASER 는 문제를 쪼개 부분문제를 인증하지만, 그 인증은 "인라이어 집합을
  올바르게 골랐다"는 보장이 아니다. 현재 접근:
  [SE-Sync](https://arxiv.org/abs/1612.07386) 의 쌍대 인증,
  [TEASER](https://arxiv.org/abs/2001.07715) 의 분해 + 최대 클리크,
  [3D SLAM 의 라그랑주 쌍대성](https://arxiv.org/abs/1506.00746). 비어 있는 자리:
  이상치 비율 $\epsilon$ 과 잡음 $\sigma$ 의 어떤 영역에서 **강건** 목적함수의 전역 최적성을
  인증할 수 있는지에 대한 특징화.
- **(열린 문제) GNC 어닐링의 이론** — $\mu$ 의 초기값·감소율·종료 조건이 전부 휴리스틱이고,
  어닐링 경로가 올바른 분지로 간다는 보장이 없다(R2). 재현 과제에서 GNC-TLS 가 이상치 40%
  에서도 잘 동작하는 것은 보장이 아니라 인스턴스의 성질이다. 현재 접근:
  [TEASER §6](https://arxiv.org/abs/2001.07715) 의 GNC 와 그 실험적 평가. 비어 있는 자리:
  스케줄에서 전역 최적성(또는 그 확률)으로 가는 조건.
- **(열린 문제) 뭉친 이상치(perceptual aliasing)** — 모든 강건 커널과 RANSAC 류는 이상치가
  서로 일관되지 않다고 가정한다. 반복 구조(복도, 주차장, 과수원)에서는 잘못된 루프 클로저가
  **서로 일치**하며 집단으로 들어오고, 그 집단이 충분히 크면 어떤 커널도 그것을 인라이어로
  받아들인다(문제 P6). 현재 접근:
  [전환 제약](https://doi.org/10.1109/IROS.2012.6385590), 외관 기반 검증,
  그리고 [장기 SLAM 서베이 IV 절](https://arxiv.org/abs/1606.05830)의 논의. 비어 있는 자리:
  이상치의 **상관 구조**를 모형에 넣고 그 아래에서 breakdown point 를 말하는 이론.

## 개념 점검

`rc quiz c5-robust-global-estimation` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c5-robust-global-estimation-quiz
questions:
  - id: q1
    type: short
    prompt: "손실 함수 $\\rho$ 와 영향 함수 $\\psi = \\rho'$ 가 주어졌을 때 IRLS 가중치 $w(r)$ 를 쓰면?"
    answer: ["psi(r)/r", "rho'(r)/r", "psi/r", "ψ(r)/r", "psi(r) / r"]
    explanation: "(3)에서 $\\nabla F = \\sum_k \\frac{\\psi(n_k)}{n_k}J_k^\\top r_k$ 이므로 $w(r) = \\psi(r)/r$ 다. 이 가중치를 고정하면 기울기가 가중 최소제곱의 기울기와 **글자 그대로** 같아지고, 그래서 IRLS 의 고정점이 M-estimator 의 정류점이 된다."
    concept: { front: "IRLS 가중치", back: "$w(r) = \\psi(r)/r = \\rho'(r)/r$ — 가중치를 고정하면 M-estimator 의 기울기가 가중 최소제곱의 기울기와 같아진다" }
  - id: q2
    type: single
    prompt: "Huber 커널이 이상치가 많아지면 무너지는 이유는?"
    choices:
      - "$\\rho$ 가 비볼록이라 지역 최솟값에 빠지기 때문"
      - "영향 함수가 유계이지만 0 이 아니라서, 이상치가 일정한 힘으로 계속 해를 끌기 때문"
      - "IRLS 가 수렴하지 않기 때문"
      - "가중치가 음수가 될 수 있기 때문"
    answer: 1
    explanation: "Huber 의 $\\psi = \\min(r, c)$ 는 유계지만 $r\\to\\infty$ 에서 $c$ 로 **수렴**한다 — 0 이 아니다. 이상치 하나의 힘은 제한되지만 이상치 $m$ 개의 합은 $mc$ 로 커진다. 재현 과제에서 이상치 40% 에서 Huber 의 ATE 가 $0.298 \\to 0.882$ 로 뛰는 반면 재하강 커널(TLS)은 $0.16$ 수준에 머문다. Huber 는 볼록이므로 1번은 틀렸다."
    concept: { front: "Huber 의 breakdown", back: "$\\psi$ 가 유계지만 0 이 아니다 — 이상치 수에 비례해 힘이 쌓인다. 재하강 커널은 $\\psi\\to0$ 이라 버틴다(대가는 비볼록성)" }
  - id: q3
    type: single
    prompt: "$SO(2)$ 동기화에서 $S = \\Lambda - C \\succeq 0$ 이 전역 최적성을 증명하는 핵심 단계는?"
    choices:
      - "$S$ 가 희소하다는 점"
      - "실현가능한 모든 $x$ 에 대해 $x^*\\Lambda x = \\operatorname{tr}\\Lambda$ 가 상수라는 점"
      - "$C$ 가 Hermitian 이라는 점"
      - "$\\hat x$ 가 $C$ 의 최대 고유벡터라는 점"
    answer: 1
    explanation: "$\\lvert x_k\\rvert = 1$ 이므로 $x^*\\Lambda x = \\sum_k\\Lambda_{kk}$ 가 $x$ 와 무관하다. 그래서 $-x^*Cx = x^*Sx - \\operatorname{tr}\\Lambda$ 로 **정확히** 다시 쓸 수 있고, $S\\succeq0$ 이 즉시 하한을 준다. $\\hat x$ 는 $C$ 의 고유벡터가 아니라 $S$ 의 영공간 원소다."
    concept: { front: "인증 증명의 심장", back: "$\\lvert x_k\\rvert=1$ 이 $x^*\\Lambda x$ 를 상수로 만든다 → $-x^*Cx = x^*Sx - \\operatorname{tr}\\Lambda$ → $S\\succeq0$ 이 하한" }
  - id: q4
    type: truefalse
    prompt: "SE-Sync 류의 전역 최적성 인증은 이상치가 섞인 포즈 그래프에서도 전역 최적을 보장한다."
    answer: false
    explanation: "인증은 **주어진 목적함수**(보통 이상치 없는 최소제곱)의 전역 최적성을 증명한다. 이상치가 섞이면 완화의 타이트성이 깨져 $\\lambda_{\\min}(S) < 0$ 이 되고 인증 자체가 실패한다 — 재현 과제에서 이상치 10% 만으로 $-6.8\\times10^{-3}$ 이 된다. 더 근본적으로, 목적함수가 전역 최적이어도 **그 목적함수가 올바른 모형인지**는 다른 문제다."
    concept: { front: "인증이 보장하지 않는 것", back: "이상치가 있으면 타이트성이 깨져 인증이 실패한다. 그리고 목적함수의 전역 최적성 ≠ 올바른 모형 선택" }
  - id: q5
    type: single
    prompt: "TEASER 의 TIM/TRIM 분해가 하는 일은?"
    choices:
      - "이상치를 직접 제거한다"
      - "평행이동과 회전을 차례로 소거해 각 부분문제를 인증 가능한 크기로 줄인다"
      - "잡음을 줄인다"
      - "대응 관계를 다시 계산한다"
    answer: 1
    explanation: "두 대응의 차가 $t$ 를 소거하고(TIM), 그 노름이 $R$ 을 소거해(TRIM) 척도 $s$ 하나만 남는 1차원 문제가 된다. 분해 자체가 강건성을 주는 것이 아니라 **각 부분문제를 전역 최적으로 풀고 인증할 수 있을 만큼 작게** 만드는 것이 요점이다. 이상치 제거는 최대 클리크 단계가 한다."
    concept: { front: "TIM/TRIM 분해의 목적", back: "$t$ → $R$ 을 차례로 소거해 1차원 문제로. 강건성이 아니라 **인증 가능성**을 만든다" }
```

## 이 단계 공부법

1. **커널 네 개의 $\psi$ 와 $w$ 를 손으로 (45분)** — 표기표의 네 커널에 대해 $\psi$, $w$ 를
   직접 미분해 쓰고, $r\to0$ 과 $r\to\infty$ 의 극한을 적는다. P1 이 그것이다. 모든 커널이
   작은 잔차에서 제곱 손실과 같다는 것을 확인하는 순간이 중요하다.
2. **(3)을 백지에서 (30분)** — 연쇄법칙 한 줄이고, 그 한 줄이 IRLS 의 존재 이유 전부다.
   "가중치를 고정하면 다른 함수"라는 관찰을 자기 말로 쓸 수 있어야 한다.
3. **Part A 를 먼저 돌린다 (90분)** — L2 가 $5.46$ 으로 망가지고 Huber 가 $0.20$ 으로 복구되는
   것을 직접 본다. 그 다음 $\lVert\nabla F\rVert$ 를 찍어 IRLS 고정점이 정말 정류점인지
   확인한다(R1 의 수치 검증). 이상치 0% 에서 L2 와 Huber 가 같은 값을 주는지가 첫 점검이다.
4. **sweep 으로 breakdown 을 본다 (45분)** — Huber 가 40% 에서 뛰고 TLS 가 버티는 것을 그래프로
   그린다. 영향 함수의 차이가 숫자로 나타나는 자리다. Barfoot SER ch.5.3 을 같이 읽는다.
5. **R3 의 증명을 네 줄로 외운다 (60분)** — 1단계($x^*\Lambda x$ 가 상수)만 기억하면 나머지는
   따라온다. 그 다음 P2ⓑ 로 "인증이 실패해도 상한은 남는다"를 확인한다 — 이 관찰이 실무에서
   가장 쓸모 있다.
6. **Part B 를 돌린다 (60분)** — 이상치 0% 에서 $\lambda_{\min}(S)$ 가 $10^{-16}$ 인 것을 보고,
   이상치를 10% 넣어 음수가 되는 것을 본다. **"잡음에는 강하고 이상치에는 약하다"**가 완화
   타이트성의 성격이고, 이 레슨의 결론이다.
7. **논문은 "무엇을 인증하는가"로 읽는다 (150분)** — SE-Sync 3-5절과 TEASER 4-6절을 읽으며
   각 논문의 "certifiable"이 정확히 무엇에 대한 주장인지 한 문장으로 적는다. 그 다음
   Sunderhauf & Protzel 로 전환 변수를 M-estimator 로 번역해 본다. 논문당 1페이지 노트는
   **반드시** 쓴다.
8. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제" 세 개 중 하나를 골라 한 문단으로 쓴다.
   뭉친 이상치는 P6 를 풀어 보면 바로 연구 주제가 된다.

**통과 기준**: 백지에서 (3)과 R3 의 네 줄 증명을 쓸 수 있고, 커널 네 개의 $\psi$·$w$ 를 유도할
수 있고, 재현 과제의 네 조건을 모두 만족하는 코드를 갖고 있고, 논문 3편의 노트가 있다.
