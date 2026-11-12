---
id: c7-learned-correspondence-slam
title: 학습 기반 대응과 SfM/SLAM
summary: >-
  미분가능 번들 조정(differentiable BA)의 기울기를 암시적 미분으로 유도하고, 흔히 쓰는
  Gauss-Newton Hessian 단축이 **사라지지 않는 편향**을 만든다는 것을 수치로 보인다. SuperGlue 의
  매칭 층을 엔트로피 정규화 최적수송으로 유도해 쓰레기통(dustbin)과 엔트로피 편향을 다루고,
  깊이·자세 동시 학습의 척도 모호성을 야코비안 영공간으로 정확히 집어낸다. 대응의 실패가
  잡음 크기가 아니라 **구조적 모호성**에서 온다는 것까지 측정으로 확인한다.
objectives:
  - 미분가능 BA 층의 기울기를 정류 조건의 암시적 미분으로 유도하고 Gauss-Newton Hessian 근사가 만드는 편향의 크기를 계산할 수 있다.
  - SuperGlue 의 매칭 층을 엔트로피 정규화 최적수송으로 유도하고 Sinkhorn 반복이 왜 이중 확률 행렬로 수렴하는지 설명할 수 있다.
  - 행 argmax 디코딩이 $\epsilon \to 0$ 에서만 순열이 됨을 수치로 보이고 쓰레기통 질량의 역할을 설명할 수 있다.
  - 깊이·자세 동시 학습의 손실이 척도 변환에 불변임을 보이고 야코비안의 랭크 결손 1 을 확인할 수 있다.
  - 특징 대응의 일반화 실패가 잡음 크기보다 구조적 모호성에서 온다는 것을 실험으로 분리할 수 있다.
prerequisites: [c7-bundle-adjustment, c7-robust-fitting-ransac]
difficulty: 5
estimated_minutes: 660
tags: [perception, learned-correspondence, differentiable-optimization, slam, scale-ambiguity, research]
papers:                                # 서지는 curriculum/robotics-research/papers.yaml
  - { id: teed2021-droid-slam, required: true, role: frontier, note: "§3" }
  - { id: sarlin2020-superglue, required: true, role: standard, note: "§3" }
  - { id: wang2024-dust3r,                     role: frontier }
  - { id: triggs2000-bundle-adjustment,        role: standard, note: "§4" }
activities:
  - id: c7-learned-correspondence-slam-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 110
  - id: c7-learned-correspondence-slam-papers
    kind: paper
    title: 필독 논문 2편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 130
  - id: c7-learned-correspondence-slam-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 2 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: c7-learned-correspondence-slam-reproduction
    kind: reproduction
    title: 재현 과제 — 미분가능 BA 의 기울기·Sinkhorn·척도 영공간 (R2, 선택 확장 R4)
    estimated_minutes: 220
  - id: c7-learned-correspondence-slam-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 20
resources:
  - title: "Szeliski, Computer Vision: Algorithms and Applications (2nd ed., 2022)"
    url: https://szeliski.org/Book/
    kind: book
    note: ch.11 (structure from motion and SLAM). 기하 기반 파이프라인과의 대조용으로만 읽는다.
  - title: "TUM RGB-D SLAM dataset and benchmark"
    url: https://cvg.cit.tum.de/data/datasets/rgbd-dataset
    kind: dataset
    note: 선택 확장(R4)의 입력. ATE/RPE 평가 스크립트와 ground truth 가 함께 공개되어 있다.
  - title: "DROID-SLAM (reference implementation)"
    url: https://github.com/princeton-vl/DROID-SLAM
    kind: code
    note: 선택 확장(R4)에서 쓴다. CUDA GPU 가 필요하므로 본 과제의 필수 조건에는 넣지 않았다.
  - title: "SuperGluePretrainedNetwork"
    url: https://github.com/magicleap/SuperGluePretrainedNetwork
    kind: code
    note: 권장. 매칭 층의 Sinkhorn 구현(반복 수·$\epsilon$ 설정)을 자기 구현과 대조한다.
  - title: "DUSt3R (reference implementation)"
    url: https://github.com/naver/dust3r
    kind: code
    note: 권장. 기하 제약을 거의 버린 설계와 비교하기 위해 본다(열린 문제 2).
---

# 학습 기반 대응과 SfM/SLAM

## 전제와 기호

권장 선수는 같은 모듈의 `c7-bundle-adjustment`(정규방정식·Schur·게이지)와
`c7-robust-fitting-ransac`(식별 불가능성), 그리고 `c8-policy-gradient-theory` 급의 학습 기초다.
어느 것도 잠겨 있지 않다. 다음을 전제한다:

- 최적화: Gauss–Newton, 정류 조건(stationarity), 음함수 정리(implicit function theorem),
  볼록 쌍대성의 초보.
- 선형대수: 야코비안의 영공간, 특이값, 블록 역행렬.
- 학습: 역전파가 계산 그래프의 연쇄법칙이라는 것. 신경망 구조 자체는 필요하지 않다 —
  이 레슨은 **학습된 값이 최적화 층에 들어갈 때 무엇이 수학적으로 변하는가**만 다룬다.
- 최적수송: 필요하지 않다. 엔트로피 정규화와 Sinkhorn 을 여기서 유도한다.

표기(C7 모듈 규약을 잇는다):

| 기호 | 뜻 |
|---|---|
| $r(x) \in \mathbb{R}^n$ | 잔차, $x \in \mathbb{R}^p$ 는 기하 매개변수(포즈·깊이) |
| $J = \partial r/\partial x$ | 야코비안 |
| $w \in \mathbb{R}^n_{>0}$ | **학습된** 가중치, $W = \operatorname{diag}(w)$ |
| $x^\star(w)$ | 가중 최소제곱의 해 — 미분가능 BA 층의 출력 |
| $H_{\mathrm{GN}} = J^\top W J$ | Gauss–Newton Hessian |
| $H = H_{\mathrm{GN}} + \sum_i w_i r_i \nabla^2 r_i$ | 완전 Hessian |
| $S \in \mathbb{R}^{m\times n}$ | 매칭 점수 행렬(학습된 디스크립터의 내적) |
| $P$ | 수송 계획(soft assignment), $\epsilon$ | 엔트로피 정규화 세기 |
| $D_j > 0$, $\rho_j = 1/D_j$ | 점 $j$ 의 깊이와 역깊이 |
| $\tau$ | 디스크립터 공간에서의 섭동 노름 |

**이 레슨의 입장**: "학습이 기하를 대체한다"도 "기하가 학습을 이긴다"도 쓰지 않는다. 다루는 것은
**학습된 양이 최적화 층에 들어갈 때 수학적으로 무엇이 보장에서 빠지는가**다. GPU 가 필요한
학습 자체는 선택 확장으로 분리했다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (미분가능 BA 층의 기울기) [D2]** — 학습된 가중치 $w$ 에 대한 해의 기울기는 정류 조건
  $g(x,w) = J(x)^\top W r(x) = 0$ 의 암시적 미분으로
  $$\frac{\partial x^\star}{\partial w_k} = -H^{-1}\,J_k^\top r_k,
    \qquad H = J^\top W J + \sum_i w_i r_i \nabla^2 r_i \tag{1}$$
  이다. 구현이 흔히 쓰는 $H \approx H_{\mathrm{GN}}$ 단축은 **잔차가 0 이 아니면 편향된 기울기**를
  주고, 그 편향은 반복을 늘려도 줄지 않는다.
- **R2 (매칭 층 = 엔트로피 정규화 최적수송) [D2]** — 쓰레기통을 붙인 점수 행렬에 대해
  $$P^\star = \arg\max_{P \in \mathcal{U}(a,b)} \langle P, S\rangle + \epsilon H(P),
    \qquad H(P) = -\sum_{ij}P_{ij}\log P_{ij} \tag{2}$$
  의 해는 $P^\star = \operatorname{diag}(u)\,K\,\operatorname{diag}(v)$,
  $K = \exp(S/\epsilon)$ 꼴이고 $u, v$ 는 Sinkhorn 반복
  $u \leftarrow a \oslash Kv$, $v \leftarrow b \oslash K^\top u$ 의 고정점이다.
- **R3 (디코딩은 $\epsilon \to 0$ 에서만 순열) [D2]** — 행별 argmax 로 얻은 대응은 $\epsilon$ 이
  크면 **순열이 아니다**(두 행이 같은 열을 고른다). $\epsilon \to 0$ 에서 $P^\star$ 가 할당
  문제의 해로 수렴하고 그때 비로소 Hungarian 해와 일치한다. 쓰레기통 질량은 $\epsilon$ 과 함께
  줄어든다.
- **R4 (깊이·자세 동시 학습의 척도 모호성) [D2]** — 단안 재투영/광측 손실은
  $$(D_j,\; t_i) \;\longmapsto\; (sD_j,\; s\,t_i), \qquad s > 0 \tag{3}$$
  에 **정확히 불변**이다. 따라서 야코비안의 랭크 결손이 정확히 1 이고, 그 영방향의 생성자는
  $\delta D_j = D_j$, $\delta t_i = t_i$, $\delta R_i = 0$ 이다. 척도는 데이터에서 나오지 않는다.
- **R5 (대응의 일반화 실패는 구조적이다) [D2]** — 디스크립터에 등방 섭동을 주는 것만으로는
  매칭이 깨지지 않는다. 깨뜨리는 것은 **구조적 모호성**(반복 패턴·중복 구조)이고, 그래서
  지역 디스크립터의 비율 검정으로는 원리적으로 해결되지 않는다 — 전역 문맥을 쓰는 매처가
  등장한 이유이고, 그것도 같은 한계에 부딪힌다.

## 유도

### R1 — 미분가능 BA 층의 기울기

학습된 가중치 $w$ 가 들어간 가중 최소제곱

$$x^\star(w) = \arg\min_x \tfrac12 \sum_i w_i\, r_i(x)^2$$

를 신경망의 한 층으로 쓰는 것이 미분가능 BA 다(필독 1 의 DBA 층). 학습을 위해 필요한 것은
$\partial x^\star/\partial w$ 다. $x^\star$ 는 정류 조건

$$g(x, w) := J(x)^\top W\, r(x) = 0 \tag{4}$$

으로 **암묵적으로** 정의된다. 음함수 정리를 (4)에 적용하면

$$\frac{\partial x^\star}{\partial w_k}
  = -\left(\frac{\partial g}{\partial x}\right)^{-1}\frac{\partial g}{\partial w_k}.$$

두 편미분을 계산한다. $\partial g/\partial w_k$ 는 $W$ 의 $k$ 번째 성분만 건드리므로

$$\frac{\partial g}{\partial w_k} = J_k^\top r_k$$

($J_k$ 는 $J$ 의 $k$ 번째 행, $r_k$ 는 스칼라). $\partial g/\partial x$ 는 **완전 Hessian** 이다:

$$\frac{\partial g}{\partial x}
  = J^\top W J + \sum_i w_i r_i \nabla^2 r_i(x) = H. \tag{5}$$

두 번째 항은 $J^\top$ 자체를 미분해서 나오고, $\nabla^2 r_i$ 는 잔차의 Hessian 이다. 이것이 (1)이다.

**구현이 흔히 하는 단축**: 역전파를 $H_{\mathrm{GN}} = J^\top W J$ 로 한다. Gauss–Newton 이
이미 $H_{\mathrm{GN}}$ 를 분해해 두었으므로 공짜이기 때문이다. 그 단축의 비용을 측정하자.

측정값(비선형 잔차 $r_i(x) = a_i^\top x + \tfrac12(a_i^\top x)^2 - b_i$, $n = 30$, $p = 4$,
수렴 후 $\lVert J^\top W r\rVert = 2.3\times10^{-16}$):

| 가중치 $k$ | $H_{\mathrm{GN}}$ 로 계산한 (1)의 상대오차 | 완전 $H$ 로 계산한 상대오차 |
|---|---|---|
| 0 | $6.92\times10^{-2}$ | $1.83\times10^{-10}$ |
| 3 | $3.99\times10^{-2}$ | $1.11\times10^{-9}$ |
| 11 | $8.32\times10^{-2}$ | $1.35\times10^{-9}$ |
| 29 | $5.70\times10^{-2}$ | $4.87\times10^{-10}$ |

(기준은 수렴한 해에 대한 중심 유한차분이다.) 완전 Hessian 을 쓰면 기울기가 기계 정밀도로
맞고, Gauss–Newton 단축은 **4~8% 틀린다**. 그 크기는 버린 항의 크기와 같다:
$\lVert \sum_i w_i r_i \nabla^2 r_i\rVert / \lVert J^\top W J\rVert = 0.086$.

**가정이 깨지는 곳 — 그리고 안 깨지는 곳**:
① 이 편향은 **반복을 늘려도 사라지지 않는다**. 측정값: 풀린 문제를 1·2·3·5·10·60 회 GN 으로
전개해 유한차분을 재면 상대차가 $1.08\times10^{-1} \to 4.4\times10^{-2} \to \cdots \to
3.87\times10^{-2}$ 로 **$3.87\%$ 에서 평평해진다** — 수렴은 해를 정확히 하지만 기울기의 편향은
Hessian 근사에서 오기 때문이다.
② 반대로 **잔차가 작으면 편향도 작다**: 버린 항이 $w_i r_i$ 에 비례하므로 $r \to 0$ 에서
$H \to H_{\mathrm{GN}}$ 이다. 잘 수렴한 BA(재투영 오차 1픽셀 이하)에서는 단축이 타당하고,
학습 초기나 이상치가 남은 상태에서는 타당하지 않다. **"DBA 층의 기울기는 믿을 만한가"는
잔차 크기에 대한 질문**이다.
③ 선형 모형에서는 $\nabla^2 r_i = 0$ 이라 두 Hessian 이 같고 편향이 0 이다(측정값: 상대오차
$3.4\times10^{-9}$). 선형 예제로 구현을 검증하면 이 버그가 보이지 않는다 — 비선형 예제가 필요하다.

### R2 — 매칭 층을 최적수송으로

학습된 디스크립터 $d_i^A, d_j^B$ 의 점수 $S_{ij} = \langle d_i^A, d_j^B\rangle$ 가 주어졌을 때
"서로 하나씩 짝짓되 짝이 없을 수도 있다"를 수식으로 적는 것이 매칭 층이다. 먼저 쓰레기통
(dustbin)을 붙인다: $S$ 에 행과 열을 하나 더해 $\bar{S} \in \mathbb{R}^{(m+1)\times(n+1)}$ 로
만들고 그 값을 학습 가능한 상수 $z$ 로 둔다. 주변 제약은

$$a = (\underbrace{1,\dots,1}_{m}, n), \qquad b = (\underbrace{1,\dots,1}_{n}, m)$$

이다 — 각 특징은 질량 1 을 쓰고, 쓰레기통은 남는 질량을 모두 받는다. 할당 문제는

$$\max_{P \ge 0,\; P\mathbf{1} = a,\; P^\top\mathbf{1} = b} \langle P, \bar{S}\rangle$$

인데 이것은 선형계획이고 미분이 거의 모든 곳에서 0 이라 학습에 쓸 수 없다. 엔트로피 항을 더하면
(2)가 되고, 그 해를 Lagrange 쌍대로 구한다. 제약의 승수를 $\alpha, \beta$ 라 하면
Lagrangian 은

$$\mathcal{L} = \langle P, \bar{S}\rangle - \epsilon\sum_{ij}P_{ij}\log P_{ij}
  + \alpha^\top(a - P\mathbf{1}) + \beta^\top(b - P^\top\mathbf{1})$$

이고 $\partial\mathcal{L}/\partial P_{ij} = \bar{S}_{ij} - \epsilon(\log P_{ij} + 1)
- \alpha_i - \beta_j = 0$ 에서

$$P_{ij} = \underbrace{e^{-\alpha_i/\epsilon - 1/2}}_{u_i}\;
           \underbrace{e^{\bar{S}_{ij}/\epsilon}}_{K_{ij}}\;
           \underbrace{e^{-\beta_j/\epsilon - 1/2}}_{v_j} \tag{6}$$

즉 $P = \operatorname{diag}(u)K\operatorname{diag}(v)$ 다. 남은 일은 주변 제약을 만족하는
$u, v$ 를 찾는 것이고, 두 제약을 번갈아 강제하면

$$u \leftarrow a \oslash (Kv), \qquad v \leftarrow b \oslash (K^\top u) \tag{7}$$

가 된다($\oslash$ 는 성분별 나눗셈). 이것이 Sinkhorn 반복이고, $K > 0$ 이면 수렴이 보장된다
(Sinkhorn–Knopp; 증명 스케치 참조). 각 반복은 행렬-벡터 곱이라 **미분가능**하고, 그래서
매칭 층 전체를 역전파할 수 있다. SuperGlue 의 매칭 층이 정확히 이것이다(필독 2 §3).

**$\epsilon$ 의 두 얼굴**: $\epsilon$ 이 크면 해가 퍼져(엔트로피가 큼) 기울기가 잘 흐르지만
할당이 흐려진다. $\epsilon \to 0$ 에서 (2)는 선형계획으로 돌아가 정확한 할당을 주지만 $K$ 의
동적 범위가 $e^{\Delta S/\epsilon}$ 로 폭발해 수치적으로 깨진다(로그 영역 구현이 필요하다).

### R3 — 디코딩: argmax 는 언제 순열인가

학습된 $P$ 에서 실제 대응을 뽑을 때 쓰는 규칙은 보통 "행별 argmax + 상호 검사 + 임계값"이다.
이것이 유효한 할당(순열)을 준다는 보장은 **없다**. 측정값($m = 10$, 정답 매칭에 점수 $+0.8$ 만
얹은 어려운 사례, Sinkhorn 5000 반복):

| $\epsilon$ | 행 argmax 에서 중복된 열 수 | $\max P$ | 쓰레기통 질량 | 순열인가 | Hungarian 해와 일치 |
|---|---|---|---|---|---|
| 2.0 | 3 | 0.198 | 4.96 | 아니오 | — |
| 1.0 | 1 | 0.445 | 4.71 | 아니오 | — |
| 0.5 | 1 | 0.804 | 4.00 | 아니오 | — |
| 0.2 | 1 | 0.988 | 2.58 | 아니오 | — |
| 0.05 | 1 | 1.000 | 0.758 | 아니오 | — |
| 0.01 | 0 | 1.000 | 0.024 | **예** | **예** |

읽는 법. ① $\epsilon$ 이 작아지면서 $\max P$ 는 1 로 가고 엔트로피는 0 으로 가는데, **중복은
$\epsilon = 0.05$ 에서도 남는다**. 즉 "$P$ 가 거의 이진이다"와 "$P$ 의 argmax 가 순열이다"는
다른 진술이다. ② $\epsilon = 0.01$ 에서 처음으로 순열이 되고, 그때 Hungarian(정확한 할당)과
**완전히 일치**한다. ③ 쓰레기통 질량이 $\epsilon$ 과 함께 줄어드는 것도 주의해야 한다 —
$\epsilon$ 을 바꾸면 "매칭 없음" 판정의 민감도까지 같이 바뀐다. $\epsilon$ 은 온도 하나로
**정확도와 거부율을 동시에** 조절하는 손잡이다.

쉬운 사례(정답에 $+3.0$ 을 얹은 경우)에서는 $\epsilon = 1.0$ 에서도 argmax 정확도가 1.00 이고
$\epsilon = 0.03$ 에서 Hungarian 과 점수가 소수점 아래까지 같았다($24.170641$ 대
$24.170641$). **쉬운 데이터로는 이 문제가 보이지 않는다** — 벤치마크 포화의 전형적 모습이다.

### R4 — 깊이·자세 동시 학습의 척도 모호성

단안 깊이·자세 동시 학습의 손실은 예측된 깊이 $D_j$ 로 점을 역투영하고 예측된 포즈
$(R_i, t_i)$ 로 다른 프레임에 투영해 재는 재투영(또는 광측) 오차다. 기준 프레임에서 베어링
$\bar{x}_j$ 가 고정되어 있으면 점은 $X_j = D_j\bar{x}_j$ 이고 프레임 $i$ 에서

$$X_{c} = R_i\,D_j\bar{x}_j + t_i, \qquad \pi(X_c) = f\,\frac{X_{c,xy}}{X_{c,z}}.$$

(3)의 변환을 넣으면 $X_c \mapsto R_i sD_j\bar{x}_j + st_i = s\,X_c$ 이고 $\pi$ 는 $X_c$ 의
방향만 보므로 $\pi(sX_c) = \pi(X_c)$ — **손실이 정확히 불변**이다. $\epsilon$ 미분해 생성자를
읽으면 $\delta D_j = D_j$, $\delta t_i = t_i$, $\delta R_i = 0$ 이다.

측정값(카메라 4개, 점 30개, 베어링 고정, 매개변수 $6\cdot4 + 30 = 54$, $J \in \mathbb{R}^{240\times54}$):
가장 작은 특이값들이 $[\dots,\ 1.8742,\ 1.90\times10^{-8}]$ 로 끊기고
($\sigma_{53}/\sigma_{54} = 9.89\times10^{7}$), 랭크 결손은 **정확히 1**, 척도 생성자는
$\lVert Jg\rVert/(\lVert J\rVert_F\lVert g\rVert) = 2.7\times10^{-12}$ 를 만족한다.
`c7-bundle-adjustment` 의 게이지 7 과 달리 **여기서는 1 뿐**인 이유는 베어링을 기준 프레임에
고정했기 때문이다 — 회전·평행이동은 베어링을 바꾸므로 더 이상 불변이 아니다.

**가정이 깨지는 곳(실무에서 중요)**:
① **프레임별 중앙값 정렬(per-frame median scaling)**. 단안 깊이 평가에서 흔히 쓰는 절차는
예측 깊이를 ground truth 의 중앙값으로 맞춘 뒤 오차를 재는 것이다. 이것은 (3)의 자유도를
프레임마다 따로 소비하므로 **척도 드리프트를 지표에서 지워 버린다**. 궤적 전체에 하나의 $s$ 만
허용하는 평가(ATE 에서의 전역 척도 정렬)와 수치가 체계적으로 달라진다. 논문의 깊이 표를 읽을
때 첫 질문은 "척도를 몇 번 맞췄는가"다.
② **척도는 데이터에서 나오지 않는다**. 보강 정보(스테레오 기준선, IMU, 알려진 물체 크기, 바닥
평면 높이) 없이는 미터 척도를 복원할 수 없다. "학습이 단안에서 미터 척도를 배운다"는 주장은
학습 데이터의 **사전분포**(카메라 높이, 전형적 장면 규모)를 배운 것이고, 분포가 바뀌면 깨진다.
③ $\epsilon$ 영방향은 손실의 평평한 방향이므로 최적화가 그 방향으로 **자유롭게 흘러간다**.
정규화(깊이 평균을 1로 고정하는 등)를 넣지 않으면 학습이 수치적으로 불안정해진다.

### R5 — 대응의 일반화 실패는 어디서 오는가

"학습된 대응이 도메인이 바뀌면 깨진다"는 말은 흔하지만, **무엇이 깨뜨리는가**는 분리해서
측정해야 한다. 디스크립터 공간에서 두 가지를 따로 준다: ⓐ 등방 섭동(노름 $\tau$), ⓑ 구조적
모호성(일부 디스크립터를 다른 점의 복제로 대체 — 반복 패턴의 모형).

측정값(합성 디스크립터 모형, $d = 128$, $n = 400$, 단위 노름, 상호 최근접 + Lowe 비율 검정
0.8, 12회 평균. 전형적 디스크립터 간 거리는 $\sqrt{2}$):

| 조건 | 정밀도 | 재현율 | 남은 대응 |
|---|---|---|---|
| 분포 내 $\tau = 0.30$ | 1.000 | 1.000 | 400/400 |
| 섭동 $\times2$ ($\tau = 0.60$) | 1.000 | 1.000 | 400/400 |
| 섭동 $\times3$ ($\tau = 0.90$) | 1.000 | 1.000 | 400/400 |
| 반복 구조 20% | 0.939 | 0.643 | 274/400 |
| 반복 구조 40% | 0.691 | 0.363 | 210/400 |

**섭동을 세 배로 키워도 매칭은 전혀 깨지지 않는다.** 고차원에서는 등방 잡음이 정답 최근접
관계를 쉽게 뒤집지 못하기 때문이다(측도의 집중). 깨뜨리는 것은 구조다 — 중복 구조 20% 에서
재현율이 0.64 로, 40% 에서 0.36 으로 떨어지고 정밀도도 같이 내려간다.

이 결과를 과대해석하지 않는 것이 중요하다. 이것은 **합성 모형**이고 실제 신경망의 일반화를
측정한 것이 아니다. 말할 수 있는 것은 하나다: **비율 검정은 "두 번째 최근접이 멀다"를 요구하는
장치이므로, 모호성이 데이터 안에 구조적으로 있으면 원리적으로 무력하다.** 지역 디스크립터만
보는 매처는 이 벽을 넘을 수 없고, 그래서 SuperGlue 류가 **전역 문맥**(어텐션으로 다른 모든
특징을 보는 것)과 **할당 제약**(R2 의 주변 제약)을 넣는다. 그리고 그것조차 반복 구조가 장면의
대부분일 때는 실패한다 — 이것이 열린 문제 1 이다.

## 증명 스케치

### R2 — Sinkhorn 반복의 수렴과 (6)의 형태

**가설** H1: $S$ 는 유한, $K = \exp(\bar{S}/\epsilon) > 0$ (성분별 양수). H2:
$a > 0$, $b > 0$, $\sum a = \sum b$. H3: $\epsilon > 0$.
**결론** C1: (2)의 해는 유일하고 (6)의 꼴이다. C2: 반복 (7)은 그 해로 수렴한다.

**전략**: 강볼록 목적함수의 유일성 + Lagrange 쌍대로 형태를 얻고, 수렴은 Hilbert 사영 거리에서의
수축 사상으로 본다.

1. **C1 (유일성)**: $-H(P) = \sum P_{ij}\log P_{ij}$ 는 심플렉스 위에서 **강볼록**이고
   $\langle P, \bar{S}\rangle$ 는 선형이므로 목적함수는 강오목이다. 제약 집합
   $\mathcal{U}(a,b)$ 는 비어 있지 않은 콤팩트 볼록 집합(H2)이므로 최대점이 유일하다.
2. **C1 (형태)**: 위 Lagrangian 의 1차 조건에서 (6)이 나온다. 여기서 $\log P_{ij}$ 가
   미분가능하려면 $P_{ij} > 0$ 이어야 하는데, 엔트로피 항의 기울기가 경계에서 $-\infty$ 로
   발산하므로 최적해는 **내부점**이다 — 이것이 엔트로피 정규화가 주는 것이고, 동시에
   "정확한 0 이 나오지 않는다"는 대가다.
3. **C2 (수렴)**: (7)은 $K$ 에 대한 대각 스케일링을 번갈아 적용하는 것이고, $K > 0$ (H1)이면
   Sinkhorn–Knopp 정리에 의해 유일한 $(u,v)$ (스칼라 배 제외)로 수렴한다. 수렴률은 Hilbert
   사영 거리에서 수축 계수 $\big(\frac{\sqrt{\kappa}-1}{\sqrt{\kappa}+1}\big)^2$,
   $\kappa = \max K / \min K$ 로 **선형(기하)** 이다. $\epsilon \to 0$ 에서
   $\kappa = e^{(\max\bar S - \min \bar S)/\epsilon}$ 가 폭발하므로 수축이 1 에 가까워진다 —
   측정값에서 $\epsilon \le 0.1$ 일 때 주변 제약 오차가 $2.5\times10^{-4}$ 로 남아
   $\epsilon = 1.0$ 의 $10^{-16}$ 과 대비된 것이 이것이다.
   (생략: Sinkhorn–Knopp 정리의 증명과 수축 계수. Peyré–Cuturi 의 계산 최적수송 교재로.)
4. **$\epsilon \to 0$ 극한**: $P^\star(\epsilon)$ 는 선형계획의 해 집합으로 수렴한다(엔트로피
   항이 $O(\epsilon)$ 로 사라짐). 유일한 최적 할당이 있으면 그 할당의 지시행렬로 수렴한다.
   측정값: $\epsilon = 0.01$ 에서 argmax 가 Hungarian 해와 완전히 일치했다.
5. **가설을 지우면**: H1 에서 $K$ 에 0 이 섞이면(즉 $S_{ij} = -\infty$ 로 금지된 짝이 있으면)
   수렴 보장이 깨지고 지지집합에 따라 해가 없을 수도 있다. H2 의 $\sum a = \sum b$ 가 깨지면
   $\mathcal{U}(a,b)$ 가 비어 수송 자체가 정의되지 않는다 — 쓰레기통의 질량 $n$ 과 $m$ 을 그렇게
   고른 이유가 바로 이 균형을 맞추기 위함이다. H3 에서 $\epsilon = 0$ 이면 2단계의 내부점
   논증이 무너지고 미분가능성을 잃는다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** (4)에서 (1)과 (5)를 유도하라. 특히 $\partial g/\partial x$ 에서
$\sum_i w_i r_i \nabla^2 r_i$ 항이 어디서 나오는지 한 줄씩 보이고, 잔차가
$r_i(x) = a_i^\top x + \tfrac12(a_i^\top x)^2 - b_i$ 일 때 $\nabla^2 r_i$ 를 명시적으로 쓰라.
*해답 스케치*: $g = J^\top W r$ 를 곱의 미분으로 전개하면 $(\partial J^\top/\partial x)Wr$ 와
$J^\top W J$ 가 나오고, 앞 항의 성분이 $\sum_i w_i r_i \nabla^2 r_i$ 다.
$\nabla^2 r_i = a_ia_i^\top$.

**P2 (증명, ★★★, R2)** (2)의 해가 유일하고 (6)의 꼴임을 증명하라. 그 다음 $\epsilon \to 0$
에서 $P^\star(\epsilon)$ 가 선형계획의 최적해 집합으로 수렴함을 보이고, **최적 할당이 유일하지
않을 때** 무엇으로 수렴하는지 쓰라.
*전략과 핵심 부등식*: 강오목성 + 콤팩트 볼록 집합으로 유일성. 극한은
$\langle P^\star, \bar S\rangle \ge \langle P_{\mathrm{LP}}, \bar S\rangle - \epsilon(H(P^\star) - H(P_{\mathrm{LP}}))$
꼴의 부등식 양쪽을 조이면 된다. 최적해가 여럿이면 **엔트로피가 최대인 최적해**로 수렴한다.

**P3 (계산, ★★, R1)** 비선형 잔차 예제를 직접 만들고 ⓐ $H_{\mathrm{GN}}$ 과 ⓑ 완전 $H$ 로
(1)을 계산해 유한차분과 비교하라. ⓒ 버린 항의 상대 크기
$\lVert\sum w_ir_i\nabla^2r_i\rVert/\lVert J^\top WJ\rVert$ 와 ⓓ ⓐ 의 상대오차를 함께 보고하라.
*정답(참조 측정값)*: ⓐ 의 상대오차 $4.0\times10^{-2} \sim 8.3\times10^{-2}$,
ⓑ 는 $10^{-10} \sim 10^{-9}$, ⓒ $= 0.086$. 허용오차: ⓑ 는 $10^{-7}$ 이하여야 하고
ⓐ 와 ⓒ 는 같은 자릿수로 일치해야 한다(둘이 같은 크기라는 것이 요점이다).
검산: 잔차를 선형으로 바꾸면 ⓐ 의 오차가 $10^{-8}$ 이하로 떨어진다.

**P4 (계산, ★★, R2·R3)** Sinkhorn 을 구현해 $\epsilon \in \{2, 1, 0.5, 0.2, 0.05, 0.01\}$ 에서
ⓐ 주변 제약 오차 ⓑ 행 argmax 의 중복 열 수 ⓒ 쓰레기통 질량 ⓓ Hungarian 해와의 일치를
표로 만들라. 점수 행렬은 정답에 $+0.8$ 만 얹은 어려운 사례로 한다.
*정답(참조 측정값)*: 중복 열 수가 $\epsilon = 2$ 에서 3, $1 \sim 0.05$ 에서 1,
$0.01$ 에서 0 이고 그때 Hungarian 과 일치. 쓰레기통 질량 $4.96 \to 0.024$.
허용오차: 경향이 같고 $\epsilon = 0.01$ 에서 순열·일치가 재현되면 통과.
검산: 정답에 $+3.0$ 을 얹은 쉬운 사례에서는 $\epsilon = 1$ 에서도 정확도 1.00 이 나와야 한다.

**P5 (유도, ★, R4)** (3)의 불변성을 $\pi(sX_c) = \pi(X_c)$ 에서 보이고 척도 생성자를 쓰라.
그 다음 **스테레오**(기준선 $b$ 가 알려짐)로 바꾸면 그 영방향이 어떻게 사라지는지 식으로 보이라.
*해답 스케치*: 불변성은 투영이 0차 동차(homogeneous of degree 0)라는 것. 스테레오에서는
$t_{\text{stereo}}$ 가 **상수**이므로 (3)의 $t \mapsto st$ 를 쓸 수 없고, 깊이만 $s$ 배 하면
시차가 $1/s$ 로 변해 잔차가 바뀐다 — 영방향이 닫힌다.

**P6 (구현, ★★★, R1·R4)** 미분가능 BA 층을 구현해 ⓐ 학습 가중치에 대한 기울기를 완전
Hessian 으로 계산하고 ⓑ 단안 깊이·자세 설정에서 척도 영방향을 수치로 확인하라.
*루브릭*: ⓐ 기울기가 유한차분과 $10^{-7}$ 이내 ⓑ 랭크 결손이 정확히 1 이고 생성자가 영공간에
들어감 ⓒ $H_{\mathrm{GN}}$ 단축의 편향을 수치로 보고 ⓓ 깊이에 정규화를 걸었을 때와 걸지
않았을 때의 수렴 거동을 비교.

**P7 (반례, ★★, R3·R5)** ⓐ Sinkhorn 의 argmax 가 순열이 아니게 되는 점수 행렬을 만들고,
ⓑ 비율 검정이 원리적으로 실패하는 데이터(반복 구조)를 만들어 정밀도·재현율이 떨어지는 것을
보이라. 그 다음 ⓒ 상호 최근접 검사를 추가하면 무엇이 좋아지고 무엇이 그대로인지 쓰라.
*성질 체크리스트*: ⓐ 두 행의 최대 점수가 같은 열에 있고 $\epsilon$ 이 크다 ⓑ 중복 비율을
20%·40% 로 올리면 재현율이 단조 감소 ⓒ 상호 검사는 정밀도를 올리지만 재현율은 회복하지
못한다 ⓓ 이 실패가 "모형이 덜 배웠다"가 아니라 **데이터의 모호성**이라는 것을 한 문단으로.

**P8 (논문, ★★, R1·R2)** DROID-SLAM §3 과 SuperGlue §3 을 읽고 ⓐ 두 논문이 각각 어떤 양을
학습하고 어떤 양을 최적화에 맡기는지 표로 정리하라. ⓑ DROID-SLAM 이 DBA 층의 기울기를
어떻게 계산하는지(암시적인가 전개인가, 어떤 Hessian 인가)를 논문에서 찾아 이 레슨의 R1 과
대조하라. ⓒ 두 논문의 보고 지표(ATE, 매칭 정밀도)가 각각 **무엇을 숨기는지** 쓰라.
*루브릭*: ⓑ 에서 논문이 명시하지 않는 부분을 "명시하지 않는다"로 정확히 적으면 통과(추측을
사실로 쓰면 미달). ⓒ 에서 ATE 의 척도 정렬 방식(R4 의 실패 모드 ①)을 짚으면 우수.

## 논문 읽기

**필독 2편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.
서지와 권장 논문 전체 목록은 `rc papers c7-learned-correspondence-slam` 로 본다.

1. **Teed & Deng, "DROID-SLAM: deep visual SLAM for monocular, stereo, and RGB-D cameras"
   (2021, NeurIPS)** — 역할: `최신(frontier)`. <https://arxiv.org/abs/2108.10869> (§3 이 핵심)
   추가 질문: ⓐ DBA 층이 학습하는 것은 무엇이고 최적화가 담당하는 것은 무엇인가 — 이 레슨의
   R1 표기로 $w$ 와 $x$ 를 각각 짚어라. ⓑ 단안 모드의 척도는 어디서 오는가(R4)? 보고된 ATE 가
   척도를 몇 번 정렬한 값인가? ⓒ 논문이 보고하지 않는 실패 사례는 어떤 종류일 것 같은가?
2. **Sarlin, DeTone, Malisiewicz & Rabinovich, "SuperGlue: learning feature matching with graph
   neural networks" (2020, CVPR)** — 역할: `표준(standard)`.
   <https://arxiv.org/abs/1911.11763> (§3 이 핵심)
   추가 질문: ⓐ 매칭 층의 Sinkhorn 반복 수와 $\epsilon$ 이 논문에 명시되어 있는가? 그 값이
   R3 의 표에서 어디에 해당하는가? ⓑ 쓰레기통이 없으면 무엇이 깨지는가? ⓒ 전역 어텐션이
   반복 구조의 모호성을 **원리적으로** 해결하는가, 아니면 사전분포로 완화하는가(R5)?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

**권장**: DUSt3R(기하 제약을 거의 버린 설계), Triggs et al. 2000 §4(최적화 쪽의 기준점).

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, 전체 10분 이내, numpy + scipy 만.
입력은 레슨이 제공하는 생성기이고 외부 데이터·GPU 가 필요하지 않다.

> **블루프린트와의 차이(명시)**: 설계안의 재현 과제는 "사전학습 DROID-SLAM 류를 TUM RGB-D
> 1개 시퀀스에 실행해 보고된 ATE 와 20% 이내 일치"다. 그 작업은 CUDA GPU 가 사실상 필요하고,
> 레슨 표준 §6 은 GPU 가 필요할 수 있는 과제를 **항상 선택 과제(R4)** 로 두라고 규정한다.
> 그래서 이 레슨은 **필수 조건을 CPU 로 판정 가능한 네 가지**로 두고, 원래의 ATE 재현을
> 아래 **선택 확장(R4)** 으로 분리했다. 둘 다 같은 핵심 결과(R1·R4)를 겨냥한다.

**생성기(고정)**: ⓐ R1 용 — 비선형 잔차
$r_i(x) = a_i^\top x + \tfrac12(a_i^\top x)^2 - b_i$, $a_i \sim N(0, I_4)$,
$b_i \sim 0.2\,N(0,1)$, $n = 30$, 가중치 $w_i \sim U(0.3, 1.5)$.
ⓑ R2 용 — $m = 10$ 점수 행렬 $S \sim N(0,1)$ 에 정답 순열 자리에만 $+0.8$.
ⓒ R4 용 — 카메라 4개(회전 $\sim 0.15$ rad, 평행이동 $\sim 0.3$), 점 30개
($[-1,1]^2 \times [4,6]$), $f = 500$, 기준 프레임의 베어링 고정. 시드를 고정해 보고한다.

아래 **네 조건을 모두** 만족해야 통과다. 참조값은 모두 이 레슨이 직접 측정한 것이다.

1. **미분가능 BA 기울기의 정확성**: 수렴점($\lVert J^\top Wr\rVert < 10^{-12}$)에서 (1)을
   **완전 Hessian** 으로 계산한 값이 중심 유한차분과 상대오차 $10^{-7}$ 이내로 일치한다
   (참조: $1.8\times10^{-10} \sim 1.4\times10^{-9}$, 가중치 4개).
2. **Gauss–Newton 단축의 편향**: 같은 문제에서 $H_{\mathrm{GN}}$ 으로 계산한 기울기의 상대오차가
   $10^{-2}$ **이상**이고, 그 크기가 버린 항의 상대 크기
   $\lVert\sum w_ir_i\nabla^2r_i\rVert/\lVert J^\top WJ\rVert$ 와 같은 자릿수다
   (참조: 오차 $4.0\sim8.3\times10^{-2}$, 버린 항 $0.086$). 또 GN 반복 수를 1·2·5·60 으로
   늘려도 그 편향이 $10^{-2}$ 아래로 내려가지 않는다(참조: $3.87\times10^{-2}$ 에서 평평).
3. **Sinkhorn 과 디코딩**: $\epsilon \in \{2, 1, 0.5, 0.2, 0.05, 0.01\}$ 에서 ⓐ 주변 제약
   오차가 $\epsilon \ge 0.2$ 에서 $10^{-12}$ 이하 ⓑ 행 argmax 의 중복 열 수가 $\epsilon$ 감소에
   따라 단조 감소해 $\epsilon = 0.01$ 에서 0 이 되고 ⓒ 그때 `scipy.optimize.linear_sum_assignment`
   의 해와 **완전히 일치** ⓓ 쓰레기통 질량이 단조 감소한다
   (참조: 중복 3/1/1/1/1/0, 쓰레기통 $4.96 \to 0.024$).
4. **척도 영공간**: 생성기 ⓒ 에서 야코비안의 랭크 결손이 **정확히 1** 이고
   ($\sigma_{n-1}/\sigma_n > 10^{6}$, 참조 $9.89\times10^{7}$), 척도 생성자
   $(\delta D_j, \delta t_i, \delta R_i) = (D_j, t_i, 0)$ 가
   $\lVert Jg\rVert/(\lVert J\rVert_F\lVert g\rVert) < 10^{-8}$ 를 만족한다(참조 $2.7\times10^{-12}$).

**선택 확장(R4, GPU 필요 가능 — 선택 과제)**: 사전학습 DROID-SLAM 을 TUM RGB-D 의
`freiburg1_desk` 같은 시퀀스 하나에 돌려 ATE RMSE 를 측정하고 **논문 보고값과 20% 이내**로
맞춘다. 보고할 때 ① 척도 정렬을 전역 1회로 했는지 프레임별로 했는지 ② 평가 스크립트(TUM 의
`evaluate_ate.py`)의 연관(association) 허용시간 ③ 시드·반복 수를 함께 적는다. R4 는
**선택 과제**이고 이 레슨의 통과 조건이 아니다.

**보고서에 반드시 쓸 것**: 조건 2 의 결론 — "미분가능 최적화 층의 기울기는 잔차가 작을 때만
Gauss–Newton Hessian 으로 대체해도 된다". 그리고 조건 4 가 평가 절차에 주는 함의(R4 실패 모드 ①).

**비교 대상**: ① 중심 유한차분(조건 1·2) ② `scipy.optimize.linear_sum_assignment` (조건 3)
③ `SuperGluePretrainedNetwork` 의 Sinkhorn 구현(반복 수·로그 영역 처리) — 코드만 읽어도 된다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 1 의 기울기가 유한차분과 10% 틀리다 | $\partial g/\partial x$ 에 2차 항을 안 넣었다 | $\lVert H - H_{\mathrm{GN}}\rVert$ 를 출력해 0 이 아닌지 본다 |
| 선형 예제에서는 맞고 비선형에서 틀리다 | 바로 위와 같은 원인 — 선형에서는 두 Hessian 이 같다 | 잔차에 2차 항을 넣어 다시 본다 |
| 유한차분이 요동한다 | 수렴이 덜 됐거나 스텝 $h$ 가 부적절 | $\lVert J^\top Wr\rVert$ 를 먼저 $10^{-12}$ 아래로 내린다 |
| Sinkhorn 이 `nan` 을 낸다 | 작은 $\epsilon$ 에서 $\exp(S/\epsilon)$ 오버플로 | 로그 영역(log-sum-exp)으로 바꾼다 |
| 주변 제약이 안 맞는다 | 쓰레기통 질량을 $n$, $m$ 으로 주지 않아 $\sum a \ne \sum b$ | $\sum a$ 와 $\sum b$ 를 출력해 비교한다 |
| 랭크 결손이 1 이 아니라 7 이다 | 베어링을 고정하지 않아 세계 닮음 게이지가 살아 있다 | 기준 프레임의 베어링을 상수로 두었는지 확인한다 |
| 랭크 결손이 0 이다 | 깊이에 정규화(평균 1 고정 등)를 이미 걸었다 | 정규화를 끄고 다시 본다 — 그 정규화가 바로 게이지 고정이다 |

## 열린 문제

- **(열린 문제) 학습된 가중치를 관측 잡음 모형으로 환산하는 보정** — DBA 층의 $w$ 는 손실을
  줄이도록 학습될 뿐이고 $1/\sigma^2$ 로 해석할 근거가 없다. 그런데 BA 의 공분산·불확실성
  해석은 전부 그 해석에 기대고 있다. 현재 접근:
  [DROID-SLAM](https://arxiv.org/abs/2108.10869) 의 학습된 신뢰도,
  [MAGSAC++](https://arxiv.org/abs/1912.05909) 의 잡음 척도 주변화. 비어 있는 자리: 학습
  가중치를 보정(calibration)해 BA 의 불확실성 보고를 복원하는 절차. `c7-bundle-adjustment` 의
  게이지 불변 불확실성 문제와 겹친다.
- **(열린 문제) 기하 제약을 언제 거는 것이 손해인가** — 제약을 거의 버린 설계
  ([DUSt3R](https://arxiv.org/abs/2312.14132))와 미분가능 BA 로 제약을 유지한 설계
  ([DROID-SLAM](https://arxiv.org/abs/2108.10869))가 공존하는데, 장면 통계(질감·시점차·반복
  구조 비율)로 교차점을 예측하는 모형이 없다. R5 의 측정은 모호성이 구조적일 때 지역
  디스크립터가 원리적으로 무력하다는 것까지만 말한다. 비어 있는 자리: 제약의 이득을
  장면에서 **사전에** 예측하는 기준.
- **(열린 문제) 척도 모호성을 숨기지 않는 평가 규약** — R4 가 보였듯 프레임별 척도 정렬은
  드리프트를 지표에서 지운다. 단안 깊이·궤적 평가에서 어떤 정렬을 몇 번 허용할지에 대한
  표준이 없어서 논문 간 수치 비교가 사실상 불가능하다. 현재 접근: TUM/KITTI 의 전역 1회 정렬
  관행, [DUSt3R](https://arxiv.org/abs/2312.14132) 류의 척도 불변 지표. 비어 있는 자리:
  정렬 자유도를 명시하고 그에 따른 오차 분해를 보고하는 규약.
- **(열린 문제) 미분가능 최적화 층의 수렴 보장** — DBA 층은 학습 중에 **아직 수렴하지 않은**
  최적화를 통과시킨다. 그때 (1)의 암시적 미분 전제(정류 조건)가 성립하지 않고, 전개
  (unrolling)는 메모리와 편향을 맞바꾼다. 어떤 조건에서 층의 출력과 기울기가 둘 다 안정한지에
  대한 이론이 없다. 현재 접근: 반복 수 고정 + 전개,
  [DROID-SLAM](https://arxiv.org/abs/2108.10869) 의 고정 반복 DBA. 비어 있는 자리: 미수렴
  최적화 층의 기울기 오차 한계.

## 개념 점검

`rc quiz c7-learned-correspondence-slam` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는
위 문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c7-learned-correspondence-slam-quiz
questions:
  - id: q1
    type: single
    prompt: "미분가능 BA 층에서 학습 가중치에 대한 기울기를 Gauss-Newton Hessian $J^\\top WJ$ 로 역전파하면 어떻게 되는가?"
    choices:
      - "정확하다 — 암시적 미분이 $J^\\top WJ$ 를 요구한다"
      - "잔차가 0 이 아니면 편향되고, 그 편향은 반복을 늘려도 줄지 않는다"
      - "편향되지만 반복을 늘리면 사라진다"
      - "선형 모형에서만 편향된다"
    answer: 1
    explanation: "암시적 미분이 요구하는 것은 완전 Hessian $J^\\top WJ + \\sum_i w_i r_i \\nabla^2 r_i$ 다. 측정값: 완전 Hessian 은 유한차분과 $10^{-10}$ 수준으로 맞는데 GN 단축은 4~8% 틀렸고, 그 크기는 버린 항의 상대 크기 0.086 과 같은 자릿수였다. 60회까지 반복해도 3.87% 에서 평평해진다. 선형 모형에서는 $\\nabla^2 r_i = 0$ 이라 두 Hessian 이 같다."
    concept: { front: "DBA 층 기울기의 GN 단축", back: "완전 Hessian 의 2차 항을 버린 편향. 잔차가 작을 때만 타당하고 반복으로는 사라지지 않는다" }
  - id: q2
    type: truefalse
    prompt: "Sinkhorn 으로 얻은 soft assignment 의 행별 argmax 는 항상 유효한 순열(일대일 대응)이다."
    answer: false
    explanation: "$\\epsilon$ 이 크면 두 행이 같은 열을 고른다. 측정값(어려운 사례): $\\epsilon=2$ 에서 중복 열 3개, $\\epsilon=1\\sim0.05$ 에서 1개, $\\epsilon=0.01$ 에서 0개이고 그때 처음으로 Hungarian 해와 일치했다. $\\max P \\approx 1$ 이어도($\\epsilon=0.05$) 중복은 남는다 — '거의 이진'과 '순열'은 다른 진술이다."
    concept: { front: "Sinkhorn argmax 디코딩", back: "$\\epsilon\\to0$ 에서만 순열이 된다. '거의 이진'은 순열을 뜻하지 않는다" }
  - id: q3
    type: short
    prompt: "단안 깊이·자세 동시 학습에서 베어링을 기준 프레임에 고정했을 때 야코비안의 랭크 결손은 몇인가? (숫자만)"
    answer: ["1", "1개", "one"]
    explanation: "손실이 $(D,t) \\mapsto (sD, st)$ 에 불변하므로 척도 한 방향만 남는다. 측정값: $\\sigma_{n-1}/\\sigma_n = 9.89\\times10^7$ 로 끊기고 척도 생성자가 $\\lVert Jg\\rVert/(\\lVert J\\rVert_F\\lVert g\\rVert) = 2.7\\times10^{-12}$. 번들 조정의 게이지 7 과 달리 1 인 이유는 베어링 고정이 회전·평행이동 불변성을 없애기 때문이다."
    concept: { front: "단안 깊이+자세의 게이지", back: "척도 1개뿐(베어링을 고정했을 때). 생성자는 $\\delta D = D$, $\\delta t = t$, $\\delta R = 0$" }
  - id: q4
    type: single
    prompt: "합성 디스크립터 실험에서 상호 최근접 + 비율 검정 매칭을 실제로 깨뜨린 것은?"
    choices:
      - "등방 섭동의 크기 ($\\tau$ 를 3배로)"
      - "반복 구조(중복 디스크립터)의 비율"
      - "디스크립터 차원"
      - "비율 검정 임계값"
    answer: 1
    explanation: "측정값: $\\tau$ 를 0.30에서 0.90으로 3배 키워도 정밀도·재현율이 1.000 이었다. 중복 구조를 20% 넣으면 재현율 0.643, 40% 에서 0.363 으로 떨어졌다. 비율 검정은 '두 번째 최근접이 멀다'를 요구하는 장치이므로 모호성이 구조적이면 원리적으로 무력하다."
    concept: { front: "대응 실패의 원인", back: "잡음 크기가 아니라 구조적 모호성(반복 패턴). 비율 검정으로는 원리적으로 해결되지 않는다" }
  - id: q5
    type: single
    prompt: "단안 깊이 평가에서 '프레임별 중앙값 척도 정렬(per-frame median scaling)'이 문제가 되는 이유는?"
    choices:
      - "중앙값이 평균보다 편향되어 있기 때문"
      - "(3)의 척도 자유도를 프레임마다 따로 소비해 척도 드리프트를 지표에서 지우기 때문"
      - "ground truth 깊이가 필요하기 때문"
      - "문제가 되지 않는다 — 척도는 복원 불가능하므로 정렬이 유일한 방법이다"
    answer: 1
    explanation: "손실은 $(D,t)\\mapsto(sD,st)$ 에 불변하므로 척도는 복원되지 않는다. 그런데 프레임마다 따로 $s$ 를 맞추면 궤적 전체의 척도 드리프트가 지표에 나타나지 않는다. 궤적 전체에 전역 $s$ 하나만 허용하는 평가와 체계적으로 다른 수치가 나오므로, 논문의 깊이 표를 읽을 때 첫 질문은 '척도를 몇 번 맞췄는가'다."
    concept: { front: "프레임별 척도 정렬의 함정", back: "척도 자유도를 프레임마다 소비 → 드리프트가 지표에서 사라짐. 전역 1회 정렬과 수치가 다르다" }
```

## 이 단계 공부법

1. **암시적 미분을 손으로 한다 (60분)** — (4)에서 (1)·(5)를 백지에서 유도한다. $J^\top$ 를
   미분하는 자리에서 2차 항이 나오는 것을 직접 보는 것이 이 레슨의 절반이다(P1).
2. **선형과 비선형으로 각각 검증한다 (90분)** — 먼저 선형 잔차로 구현해 GN 단축과 완전
   Hessian 이 **같은** 답을 주는 것을 확인하고(둘 다 유한차분과 맞는다), 그 다음 2차항을 넣어
   갈라지는 것을 본다(조건 1·2). 선형으로만 테스트한 구현이 왜 버그를 숨기는지 체감한다.
3. **Sinkhorn 을 쌍대에서 유도한다 (60분)** — Lagrangian 의 1차 조건에서 (6)이 나오는 것을
   쓰고, 반복 (7)이 제약을 번갈아 강제하는 것임을 확인한다. 그 다음 로그 영역으로 다시
   구현해 작은 $\epsilon$ 에서 `nan` 이 없어지는 것을 본다.
4. **디코딩을 의심한다 (60분)** — $\epsilon$ 을 쓸어 가며 중복 열 수와 쓰레기통 질량을 재고
   Hungarian 과 비교한다(조건 3). 쉬운 사례와 어려운 사례를 **둘 다** 돌려야 이 현상이 보인다.
5. **척도 영방향을 본다 (60분)** — 생성기 ⓒ 로 야코비안을 만들어 특이값을 출력하고, 척도
   생성자가 영공간에 있는지 확인한다(조건 4). 그 다음 깊이 평균을 1 로 고정해 결손이 0 이
   되는 것을 본다 — **정규화가 게이지 고정이라는 것**을 눈으로 확인한다.
6. **실패의 원인을 분리한다 (60분)** — 디스크립터 실험에서 잡음과 구조를 따로 키워 본다(P7).
   "도메인 변화에 약하다"는 말이 실제로는 무엇을 뜻하는지가 여기서 갈린다.
7. **논문 2편과 노트 (130분)** — SuperGlue §3 을 먼저 읽어 R2·R3 과 대조하고, 그 다음
   DROID-SLAM §3 에서 $w$ 와 $x$ 를 짚는다. 논문당 1페이지 노트는 **반드시** 쓴다.
8. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제"에서 하나를 골라 왜 아직 안 풀렸는지
   한 문단으로 쓴다. 학습 가중치의 보정은 당장 실험으로 손댈 수 있는 질문이다.

**통과 기준**: (1)과 (5)를 백지에서 유도할 수 있고, GN 단축의 편향을 수치로 보일 수 있고,
Sinkhorn 을 쌍대에서 유도해 구현했고, 척도 영방향을 확인했고, 재현 과제의 네 조건을 통과하는
코드를 갖고 있고, 논문 2편의 노트가 있다.
