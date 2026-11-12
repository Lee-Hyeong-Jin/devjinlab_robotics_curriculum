---
id: c1-lie-group-derivatives
title: 리 군 위의 미분 — 좌·우 야코비안
summary: >-
  지수 사상의 미분을 Duhamel 공식에서 유도해 좌·우 야코비안의 닫힌 형태를 얻고, BCH 전개로
  군 곱의 선형화 오차 차수를 정한다. 불변 거리와 Fréchet 평균까지 가서, 왜 추정 문제가
  유클리드 덧셈이 아니라 이 야코비안을 써야 하는지 확인한다.
objectives:
  - 지수 사상의 미분에 대한 Duhamel(Dyson) 공식을 유도하고 좌·우 야코비안의 적분 표현을 쓸 수 있다.
  - 적분 표현을 적분해 $J_l$ 과 $J_r$ 의 닫힌 형태를 유도하고 작은 각 급수를 구할 수 있다.
  - $J_l(\phi) = \mathrm{Exp}(\phi)J_r(\phi)$ 와 $J_l(\phi) = J_r(-\phi)$ 를 증명할 수 있다.
  - BCH 전개로 $\mathrm{Log}(\mathrm{Exp}(\phi)\mathrm{Exp}(\delta))$ 의 1차 항이 $J_r^{-1}$ 임을 보일 수 있다.
  - 불변 거리와 Fréchet 평균을 정의하고 리만 경사하강으로 계산할 수 있다.
prerequisites: [c1-twists-wrenches-adjoint]
difficulty: 5
estimated_minutes: 480
tags: [lie-groups, so3, jacobian, bch, frechet-mean, research]
activities:
  - id: c1-lie-group-derivatives-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c1-lie-group-derivatives-papers
    kind: reading
    title: 필독 논문 2편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 120
  - id: c1-lie-group-derivatives-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 150
  - id: c1-lie-group-derivatives-reproduction
    kind: exercise
    title: 재현 과제 — 야코비안 검증과 Fréchet 평균 (R1)
    estimated_minutes: 90
  - id: c1-lie-group-derivatives-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.7.1–7.3. 좌·우 야코비안의 닫힌 형태와 그 역행렬, 불확실성의 좌/우 표현.
  - title: "Solà, Deray & Atchuthan — A micro Lie theory for state estimation in robotics (2018)"
    url: https://arxiv.org/abs/1812.01537
    kind: article
    note: 필독 1. 2–4절. 이 레슨의 표기와 야코비안 규약의 표준 참고서.
  - title: "Forster, Carlone, Dellaert & Scaramuzza — On-manifold preintegration (2017)"
    url: https://arxiv.org/abs/1512.02363
    kind: article
    note: 필독 2. II·III절과 부록. 우 야코비안이 바이어스 재선형화·불확실성 전파에 쓰이는 실제 자리.
  - title: "Lynch & Park, Modern Robotics"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: ch.3.3 과 부록 B. SE(3) 지수 사상의 $G(\theta)$ 가 좌 야코비안과 같은 적분에서 나온다.
  - title: "Absil, Mahony & Sepulchre, Optimization Algorithms on Matrix Manifolds (2008)"
    url: https://doi.org/10.1515/9781400830244
    kind: book
    note: 권장. 4장 리만 경사하강과 수렴. 다음 레슨(매니폴드 위 최적화)의 교재.
---

# 리 군 위의 미분 — 좌·우 야코비안

## 전제와 기호

앞 두 레슨(`c1-so3-se3-exponential`, `c1-twists-wrenches-adjoint`)의 표기를 쓴다. 추가 기호:

| 기호 | 뜻 |
|---|---|
| $\mathrm{Exp}(\phi) := \exp(\hat{\phi})$ | 벡터를 받는 지수 사상. $\mathrm{Log}$ 는 그 역 |
| $R \oplus \delta := R\,\mathrm{Exp}(\delta)$ | **우(right)** 증분. 물체 프레임에서의 섭동 |
| $\delta \oplus R := \mathrm{Exp}(\delta)\,R$ | **좌(left)** 증분. 기준 프레임에서의 섭동 |
| $R_2 \ominus R_1 := \mathrm{Log}(R_1^{-1}R_2)$ | 우 차이. $\ominus$ 는 $\oplus$ 의 역연산 |
| $J_l(\phi),\ J_r(\phi) \in \mathbb{R}^{3\times3}$ | 좌·우 야코비안 |
| $\theta = \lVert\phi\rVert$, $\hat{u} = \hat{\phi}/\theta$ | 각과 단위 축 |

**왜 이 레슨이 필요한가**: $SO(3)$ 은 벡터공간이 아니므로 $R + \delta$ 가 회전이 아니다. 추정과
최적화는 그래서 $R \oplus \delta$ 를 쓰는데, 그러면 "$\delta$ 에 대한 미분"이 유클리드 미분과
다르다. 그 차이를 정확히 담는 것이 좌·우 야코비안이고, 이것을 틀리면 공분산이 조용히 틀린다.

## 핵심 결과

- **R1 (Duhamel 공식과 야코비안의 적분 표현) [D3]** — $A(t) = \hat{\phi} + t\hat{\delta}$ 에 대해

$$
\left.\frac{d}{dt}e^{A(t)}\right|_{t=0} = \int_0^1 e^{\alpha\hat{\phi}}\,\hat{\delta}\,e^{(1-\alpha)\hat{\phi}}\,d\alpha,
\tag{1}
$$

  이고 이로부터

$$
J_l(\phi) = \int_0^1 \mathrm{Exp}(\alpha\phi)\,d\alpha, \qquad
J_r(\phi) = \int_0^1 \mathrm{Exp}(-\alpha\phi)\,d\alpha. \tag{2}
$$

- **R2 (닫힌 형태) [D2]** — (2)를 적분하면

$$
J_l(\phi) = I + \frac{1-\cos\theta}{\theta^2}\hat{\phi} + \frac{\theta-\sin\theta}{\theta^3}\hat{\phi}^2,
\qquad J_r(\phi) = J_l(-\phi). \tag{3}
$$

  작은 각 급수는 $J_l \approx I + \tfrac12\hat{\phi} + \tfrac16\hat{\phi}^2$,
  $J_r \approx I - \tfrac12\hat{\phi} + \tfrac16\hat{\phi}^2$ 이다.
- **R3 (좌·우 관계) [D3]** — $R = \mathrm{Exp}(\phi)$ 에 대해

$$
J_l(\phi) = R\,J_r(\phi), \qquad J_l(\phi) = J_r(-\phi) = J_r(\phi)^\top. \tag{4}
$$

- **R4 (BCH 1차 항과 선형화 오차) [D2]** — $\lVert\delta\rVert$ 가 작을 때

$$
\mathrm{Log}\big(\mathrm{Exp}(\phi)\,\mathrm{Exp}(\delta)\big)
= \phi + J_r^{-1}(\phi)\,\delta + O(\lVert\delta\rVert^2), \tag{5}
$$

  그리고 $J_r^{-1}(\phi) = I + \tfrac12\hat{\phi} + \tfrac1{12}\hat{\phi}^2 + O(\theta^4)$.
  닫힌 형태는 Barfoot ch.7.1 과 Forster et al. 의 식에 있다 **[D0]** — 부호를 외우지 말고
  수치로 검증하는 것이 이 레슨의 재현 과제다.
- **R5 (불변 거리와 Fréchet 평균) [D2]** — $d(R_1,R_2) = \lVert\mathrm{Log}(R_1^\top R_2)\rVert$ 는
  $SO(3)$ 에서 좌·우 양쪽으로 불변(bi-invariant)이고, Frobenius 거리와는

$$
\lVert R_1 - R_2\rVert_F = 2\sqrt{2}\,\big|\sin(\theta/2)\big|, \qquad \theta = d(R_1,R_2) \tag{6}
$$

  로 이어진다. 측지 평균(Fréchet mean) $\bar{R} = \arg\min_R \sum_i d^2(R, R_i)$ 는 리만
  경사하강

$$
\bar{R} \leftarrow \bar{R}\,\mathrm{Exp}\!\left(\frac{1}{N}\sum_i \mathrm{Log}(\bar{R}^\top R_i)\right)
\tag{7}
$$

  으로 계산하고, 표본이 반지름 $\pi/2$ 의 공 안에 있으면 유일하다 **[D0]**(Karcher 조건).

## 유도

### R1 — Duhamel 공식

$F(t,s) := e^{sA(t)}$ 로 두고 $s$ 에 대한 ODE 를 쓴다: $\partial_s F = A F$, $F(t,0)=I$.
양변을 $t$ 로 미분하고 $G := \partial_t F$ 라 하면

$$
\partial_s G = A G + \dot{A}F, \qquad G(t,0) = 0 .
$$

이것은 $G$ 에 대한 비동차 선형 ODE 다. 동차해 $e^{sA}$ 로 적분인자를 잡으면(Duhamel 원리)

$$
G(t,s) = \int_0^s e^{(s-\alpha)A}\,\dot{A}\,e^{\alpha A}\,d\alpha .
$$

$s=1$, $t=0$ 에서 $A = \hat{\phi}$, $\dot{A} = \hat{\delta}$ 이므로 (1)이다. 변수를
$\alpha \to 1-\alpha$ 로 바꾸면 (1)의 두 지수 위치가 바뀐 형태도 같은 식임을 알 수 있다.

**(2)로 가는 한 줄**: (1)의 양변 오른쪽에 $e^{-\hat{\phi}}$ 를 곱하고 수반 표현
$e^{\alpha\hat{\phi}}\hat{\delta}e^{-\alpha\hat{\phi}} = \widehat{\mathrm{Exp}(\alpha\phi)\delta}$
(앞 레슨 R1)를 쓰면

$$
\left.\frac{d}{dt}\mathrm{Exp}(\phi + t\delta)\right|_{t=0}\mathrm{Exp}(-\phi)
= \widehat{\left(\int_0^1 \mathrm{Exp}(\alpha\phi)\,d\alpha\right)\delta},
$$

즉 **좌** 증분으로 본 미분이 $J_l(\phi)\delta$ 다. 왼쪽에 곱하면 같은 계산이 $J_r$ 을 준다.
$\oplus$ 표기로 쓰면 이것이 흔히 보는 형태다:

$$
\mathrm{Exp}(\phi + \delta) \approx \mathrm{Exp}(\phi)\,\mathrm{Exp}\big(J_r(\phi)\delta\big)
\approx \mathrm{Exp}\big(J_l(\phi)\delta\big)\,\mathrm{Exp}(\phi). \tag{8}
$$

### R2 — 닫힌 형태

(2)에 Rodrigues 공식을 넣고 $\alpha$ 로 적분한다. $\hat{\phi} = \theta\hat{u}$ 이므로

$$
J_l(\phi) = \int_0^1\! \Big(I + \sin(\alpha\theta)\hat{u} + \big(1-\cos(\alpha\theta)\big)\hat{u}^2\Big) d\alpha
= I + \frac{1-\cos\theta}{\theta}\hat{u} + \Big(1 - \frac{\sin\theta}{\theta}\Big)\hat{u}^2 .
$$

$\hat{u} = \hat{\phi}/\theta$, $\hat{u}^2 = \hat{\phi}^2/\theta^2$ 로 되돌리면 (3)이다. 두 계수의
작은 각 극한은 $\frac{1-\cos\theta}{\theta^2}\to\frac12$,
$\frac{\theta-\sin\theta}{\theta^3}\to\frac16$ 이므로 급수 형태가 나온다.

**$J_r^{-1}$ 의 급수를 직접 얻기**: $J_r \approx I - \frac12 X + \frac16 X^2$ ($X := \hat{\phi}$)에
$J_r^{-1} = I + \frac12 X + cX^2$ 를 곱하면

$$
\Big(I - \tfrac12 X + \tfrac16 X^2\Big)\Big(I + \tfrac12 X + cX^2\Big)
= I + \big(c - \tfrac14 + \tfrac16\big)X^2 + O(X^3),
$$

따라서 $c = \frac1{12}$ 다. 이 한 줄이 R4 의 급수를 준다.

**가정이 깨지는 곳**: (3)은 $\theta>0$ 에서만 쓸 수 있고 $\theta\to0$ 에서 두 계수가 0/0 이다 —
구현에서는 $\theta \lesssim 10^{-4}$ 에서 급수로 갈아탄다. 더 사나운 쪽은 $J_r^{-1}$ 의 닫힌
형태인데, 분모에 $\sin\theta$ 가 있어 $\theta \to \pi$ 에서 **발산**한다. 즉 야코비안의 역은
$\theta<\pi$ 에서만 존재한다. 큰 회전 섭동을 한 번에 선형화하면 안 되는 수학적 이유가 이것이다.

### R5 — 불변 거리와 (6)

$\lVert R_1 - R_2\rVert_F^2 = \operatorname{tr}\big((R_1-R_2)^\top(R_1-R_2)\big)
= 6 - 2\operatorname{tr}(R_1^\top R_2)$ 이고, $R_1^\top R_2$ 의 회전각이 $\theta$ 이므로
$\operatorname{tr}(R_1^\top R_2) = 1 + 2\cos\theta$ (앞 레슨 R3). 넣으면

$$
\lVert R_1 - R_2\rVert_F^2 = 6 - 2(1+2\cos\theta) = 4(1-\cos\theta) = 8\sin^2(\theta/2),
$$

즉 (6)이다. 두 거리는 작은 각에서 $\theta$ 에 비례해 거의 같지만($2\sqrt2\sin(\theta/2)\approx\sqrt2\,\theta$),
$\theta$ 가 커지면 갈라지고 $\theta=\pi$ 에서 Frobenius 거리는 포화된다($2\sqrt2$). **그래서
Frobenius 기반 평균(산술 평균 후 SVD 투영)은 퍼진 표본에서 측지 평균과 다른 답을 준다** — 문제 P5.

(7)은 목적함수 $f(R) = \frac12\sum_i \lVert\mathrm{Log}(R^\top R_i)\rVert^2$ 의 리만 기울기가
$-\sum_i \mathrm{Log}(R^\top R_i)$ 임을 쓰면 나온다(우 증분으로 미분하고 R1 을 적용).

## 증명 스케치

### R3 — $J_l(\phi) = \mathrm{Exp}(\phi)J_r(\phi)$

**가설** H1: (2)의 적분 표현. H2: $\mathrm{Exp}$ 가 군 준동형이 아니지만 같은 축의 회전끼리는
$\mathrm{Exp}(a\phi)\mathrm{Exp}(b\phi) = \mathrm{Exp}((a+b)\phi)$ 를 만족한다(같은 축이므로 교환).
**결론** C: (4).

**전략**: 적분 안에서 변수 치환. 같은 축의 회전이 교환한다는 사실만 쓴다.

1. (2)에서 $J_r(\phi) = \int_0^1 \mathrm{Exp}(-\alpha\phi)d\alpha$.
2. 좌변에 $\mathrm{Exp}(\phi)$ 를 곱하고 적분 안으로 넣는다(적분은 $\alpha$ 에 대한 것이고
   $\mathrm{Exp}(\phi)$ 는 상수):
   $\mathrm{Exp}(\phi)J_r(\phi) = \int_0^1 \mathrm{Exp}(\phi)\mathrm{Exp}(-\alpha\phi)\,d\alpha$.
3. H2 로 $\mathrm{Exp}(\phi)\mathrm{Exp}(-\alpha\phi) = \mathrm{Exp}((1-\alpha)\phi)$.
4. $\beta := 1-\alpha$ 로 치환하면 $\int_0^1 \mathrm{Exp}(\beta\phi)d\beta = J_l(\phi)$. C.
5. $J_l(\phi) = J_r(-\phi)$ 는 (2)에서 바로 보인다. 또 $\mathrm{Exp}(\alpha\phi)^\top =
   \mathrm{Exp}(-\alpha\phi)$ 이므로 $J_l(\phi)^\top = J_r(\phi)$, 즉 (4)의 마지막 등식.

**가설을 지우면**: H2(같은 축의 교환성)가 핵심이다. 축이 다른 두 회전은 교환하지 않으므로
3단계가 깨진다 — 일반적인 두 리 대수 원소에 대해서는 $\mathrm{Exp}(X)\mathrm{Exp}(Y) \ne
\mathrm{Exp}(X+Y)$ 이고, 그 차이를 재는 것이 바로 BCH 전개(R4)다. 이 레슨의 두 결과가 같은
사실의 양면인 셈이다.

**$SE(3)$ 로의 확장에서 깨지는 것**: $SO(3)$ 의 측지 거리는 양쪽 불변이지만, **$SE(3)$ 에는
양쪽 불변 리만 계량이 존재하지 않는다** [D0]. 회전과 평행이동의 단위가 달라 둘을 한 계량으로
묶는 선택이 임의적이기 때문이다. 그래서 $SE(3)$ 위의 "평균"과 "거리"는 가중치 선택에 의존한다 —
문제 P6 과 `c5-manifold-estimation` 에서 다시 나온다.

## 문제 세트

★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** (1)에서 (2)를 얻는 단계를 빠짐없이 쓰라. 특히 수반 표현
$e^{\alpha\hat\phi}\hat\delta e^{-\alpha\hat\phi} = \widehat{\mathrm{Exp}(\alpha\phi)\delta}$ 를
어디서 쓰는지, 그리고 왜 그 결과가 **좌** 야코비안인지 밝혀라.
*해답 스케치*: (1)의 오른쪽에 $e^{-\hat\phi}$ 를 곱해 $\dot{R}R^{-1}$ 형태(= 기준 프레임에서
본 각속도)를 만들면 좌 증분이 된다. 왼쪽에 곱하면 $R^{-1}\dot{R}$(물체 프레임)이 되어 우 야코비안이다.

**P2 (유도, ★★★, R4)** $J_r^{-1}(\phi)$ 의 **닫힌 형태**를 유도하라(급수가 아니라).
$J_r$ 이 $I$, $\hat\phi$, $\hat\phi^2$ 의 선형결합이고 $\hat\phi^3 = -\theta^2\hat\phi$ 임을
쓰면 역행렬도 같은 형태임을 보일 수 있다. 계수를 연립방정식으로 풀어라.
*해답 스케치*: $J_r^{-1} = aI + b\hat\phi + c\hat\phi^2$ 로 놓고 $J_rJ_r^{-1} = I$ 를 전개한 뒤
$I$, $\hat\phi$, $\hat\phi^2$ 의 계수를 각각 0 또는 1 로 맞춘다($\hat\phi^3$ 은 $\hat\phi$ 로
환원된다). 결과에 $\sin\theta$ 가 분모로 들어가고 $\theta\to\pi$ 에서 발산하는 것을 확인하라.
**얻은 식은 반드시 수치로 검증하라** — 부호를 틀리기 쉽고, 틀려도 작은 각에서는 드러나지 않는다.

**P3 (증명, ★★, R3·R4)** $\mathrm{Log}(\mathrm{Exp}(\phi)\mathrm{Exp}(\delta))$ 의 1차 항이
$J_r^{-1}(\phi)\delta$ 임을 (8)에서 유도하고, 2차 항이 $O(\lVert\delta\rVert^2)$ 임을
BCH 전개의 교환자 항으로 설명하라.
*해답 스케치*: (8)의 첫 등식에서 $\delta \mapsto J_r^{-1}\delta$ 를 대입한다. BCH 의 2차 항은
$\frac12[\hat\phi,\hat\delta]$ 이고 $\lVert\delta\rVert$ 에 **1차**이지만 $J_r^{-1}$ 에 이미
흡수되어 있다 — 남는 것은 $\lVert\delta\rVert^2$ 항부터다. 이 구분을 정확히 쓰는 것이 문제의 핵심.

**P4 (계산, ★, R2)** $\phi = (0, 0, \pi/2)$ 에서 $J_l(\phi)$ 와 $J_r(\phi)$ 를 구하라.
*정답*: $\theta=\pi/2$, $\frac{1-\cos\theta}{\theta^2} = 1/(\pi/2)^2 = 4/\pi^2 \approx 0.405285$,
$\frac{\theta-\sin\theta}{\theta^3} = (\pi/2-1)/(\pi/2)^3 \approx 0.147942$.
$\hat\phi = \frac{\pi}{2}\begin{psmallmatrix}0&-1&0\\1&0&0\\0&0&0\end{psmallmatrix}$ 이므로
$J_l \approx \begin{psmallmatrix}0.635&-0.637&0\\0.637&0.635&0\\0&0&1\end{psmallmatrix}$,
$J_r = J_l^\top$. 허용오차 $10^{-3}$. 검산: $J_l = \mathrm{Exp}(\phi)J_r$ 을 수치로 확인하라.

**P5 (반례, ★★, R5)** Frobenius 기반 평균(회전행렬을 산술평균한 뒤 SVD 로 $SO(3)$ 에 투영)과
측지 평균 (7)이 **다른 답**을 주는 표본을 구성하라. 두 평균의 차이가 표본의 퍼짐에 따라 어떻게
커지는지 수치로 보이고, 왜 작은 퍼짐에서는 구분되지 않는지 (6)으로 설명하라.
*성질 체크리스트*: 한 축 주위로 $\pm\psi$ 떨어진 두 회전이면 두 평균이 일치한다(대칭) — 반례는
**비대칭**이거나 **세 개 이상**이어야 한다. $\psi$ 를 $\pi/2$ 근처로 키우면 차이가 드러난다.

**P6 (반례·서술, ★★, R5 확장)** $SE(3)$ 에 양쪽 불변 리만 계량이 없다는 사실이 실무에서
무엇을 뜻하는지 쓰라. 포즈 두 개의 "거리"를 정의하는 서로 다른 두 방법을 제시하고, 각각이
어떤 단위 선택을 암묵적으로 하는지 밝혀라.
*루브릭*: 회전과 평행이동을 하나의 수로 묶으려면 길이 척도(예: 로봇의 특성 길이)를 골라야 하고,
그 선택이 결과(최근접 포즈, 평균, 공분산)를 바꾼다는 점을 짚으면 통과.

## 논문 읽기

**필독 2편.** 고정 질문 10개(`research_notes/연구 트랙 설계/lesson-standard.md` §5)로
논문당 1페이지 노트를 쓴다.

1. **Solà, Deray & Atchuthan, "A micro Lie theory for state estimation in robotics" (2018)** —
   역할: `표준(standard)`. <https://arxiv.org/abs/1812.01537> (2–4절)
   추가 질문: ⓐ 저자들의 야코비안 표기를 이 레슨의 $J_l$, $J_r$ 로 옮겨 표를 만들라.
   ⓑ "right-plus" 와 "left-plus" 중 어느 쪽을 쓸지는 무엇이 결정하는가?
2. **Forster, Carlone, Dellaert & Scaramuzza, "On-manifold preintegration" (2017)** —
   역할: `원전(seminal)`. <https://arxiv.org/abs/1512.02363> (II·III절 + 부록)
   추가 질문: ⓐ $J_r$ 이 등장하는 식을 전부 찾아 각각이 **왜** 필요한지 한 줄로 쓰라.
   ⓑ 바이어스가 바뀔 때 선적분을 다시 하지 않고 1차 보정으로 끝내는 근거가 이 레슨의 어느
   결과인가? ⓒ 그 1차 근사가 깨지는 조건은?

## 재현 과제

**티어 R1 (수치 검증).** 예산: 노트북 CPU 1분 이내, numpy 만. 네 조건을 모두 만족해야 통과다.

1. **야코비안이 미분과 일치**: $\lVert\phi\rVert \in (10^{-6}, \pi-10^{-3})$ 인 $\phi$ 1000개와
   무작위 방향 $\delta$ 에 대해, 중심 유한차분으로 계산한
   $\partial\,\mathrm{Log}\big(\mathrm{Exp}(\phi)^\top\mathrm{Exp}(\phi+t\delta)\big)/\partial t|_{t=0}$
   가 $J_r(\phi)\delta$ 와 $10^{-7}$ 이내로 일치.
2. **좌·우 관계**: 같은 $\phi$ 들에 대해
   $\lVert J_l(\phi) - \mathrm{Exp}(\phi)J_r(\phi)\rVert_F < 10^{-12}$ 이고
   $\lVert J_l(\phi) - J_r(\phi)^\top\rVert_F < 10^{-12}$.
3. **역행렬**: P2 에서 유도한 닫힌 형태로 $\lVert J_r(\phi)J_r^{-1}(\phi) - I\rVert_F < 10^{-10}$.
   $\theta \to \pi$ 로 쓸어가며 **조건수가 발산하는 것**을 로그 도표로 확인하라(발산해야 맞다).
4. **Fréchet 평균**: 참 평균 주위로 표준편차 $0.3\,\mathrm{rad}$ 로 흩뿌린 회전 50개에 대해
   (7)을 수렴시킨다. ⓐ 무작위 초기값 100회 재시작이 모두 같은 해로 수렴
   ($\max$ 쌍거리 $< 10^{-9}$) ⓑ 수렴 후 $\lVert\sum_i\mathrm{Log}(\bar R^\top R_i)\rVert < 10^{-10}$
   (1차 조건) ⓒ 같은 표본에서 Frobenius 평균과의 차이를 보고하고, 퍼짐을 $1.2\,\mathrm{rad}$ 로
   키우면 차이가 커지는 것을 보여라.

**비교 대상**: `scipy.spatial.transform.Rotation.mean()` (측지 평균 구현)과 조건 4ⓐ 의 해가
$10^{-8}$ 이내로 일치해야 한다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 1 이 $\theta$ 가 클 때만 실패 | 좌·우 야코비안을 바꿔 썼다 | $\theta$ 를 키우며 오차를 그린다. 작은 각에서는 $J_l\approx J_r$ 이라 안 드러난다 |
| 작은 각에서 `nan` | (3)의 계수가 0/0 | $\theta=10^{-12}$ 를 직접 넣고, 급수 분기 임계값을 확인 |
| 조건 3 이 $\theta\to\pi$ 에서 실패 | **정상이다** — $J_r^{-1}$ 은 $\theta<\pi$ 에서만 존재 | 허용 구간을 $\pi-10^{-3}$ 로 제한했는지 확인 |
| 평균이 초기값에 따라 다른 해로 간다 | 표본이 너무 퍼졌다(Karcher 조건 위반) 또는 $\mathrm{Log}$ 의 분기 처리 오류 | 퍼짐을 줄여 재시도하고, $\theta\approx\pi$ 표본이 있는지 본다 |

## 열린 문제

- **(열린 문제) 큰 불확실성에서의 선형화** — $J_r^{-1}$ 이 $\theta\to\pi$ 에서 발산하므로 큰
  회전 오차를 한 번에 선형화할 수 없다. 실무는 반복 재선형화로 우회하지만, **어느 정도의 불확실성
  까지 접공간 가우시안이 타당한지**에 대한 정량적 기준이 없다. 현재 접근:
  [Barfoot SER ch.7](https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf) 의 좌/우 불확실성
  표현, [불변 EKF](https://arxiv.org/abs/1410.1465) 의 군 아핀 오차 동역학. 비어 있는 자리:
  "언제 선형화를 포기하고 다봉(multi-modal) 표현으로 가야 하는가".
- **(열린 문제) $SE(3)$ 거리의 임의성** — 양쪽 불변 계량이 없으므로 회전·평행이동의 가중치를
  골라야 하고, 그 선택이 최근접 포즈·평균·공분산을 바꾼다. 과제에 따라 자동으로 가중치를 정하는
  원리적 방법이 없다. `c5-manifold-estimation` 과 `s1-slam-benchmarking` 의 ATE 정의에서 같은
  문제가 다시 나온다.
- **(열린 문제) 학습 모델 안의 야코비안** — 미분가능 파이프라인에서 $\mathrm{Log}/\mathrm{Exp}$ 를
  통과하는 기울기는 $\theta\approx\pi$ 근방에서 수치적으로 불안정하다. 자동 미분이 주는 기울기를
  그대로 믿어도 되는 영역이 어디까지인지 정리되지 않았다
  ([Pinocchio 의 해석적 미분](https://doi.org/10.15607/RSS.2018.XIV.038)이 한 대안).

## 개념 점검

`rc quiz c1-lie-group-derivatives` 로 푼다. 개념 점검 전용이고 실제 과제는 문제 세트와 재현 과제다.

```quiz
activity: c1-lie-group-derivatives-quiz
questions:
  - id: q1
    type: single
    prompt: "$\\mathrm{Exp}(\\phi + \\delta) \\approx \\mathrm{Exp}(\\phi)\\mathrm{Exp}(X\\delta)$ 에서 $X$ 는?"
    choices:
      - "$J_l(\\phi)$ (좌 야코비안)"
      - "$J_r(\\phi)$ (우 야코비안)"
      - "$I$ (보정이 필요 없다)"
      - "$\\mathrm{Exp}(\\phi)$"
    answer: 1
    explanation: "증분이 **오른쪽**에 곱해지므로 우 야코비안이다. 왼쪽에 곱하는 형태 $\\mathrm{Exp}(J_l(\\phi)\\delta)\\mathrm{Exp}(\\phi)$ 에서는 좌 야코비안이 된다. 둘은 $J_l(\\phi) = \\mathrm{Exp}(\\phi)J_r(\\phi)$ 로 이어진다."
    concept: { front: "좌 야코비안과 우 야코비안을 가르는 것", back: "증분을 어느 쪽에 곱하는가. 오른쪽($R\\,\\mathrm{Exp}(\\delta)$)이면 $J_r$, 왼쪽이면 $J_l$. $J_l(\\phi) = \\mathrm{Exp}(\\phi)J_r(\\phi) = J_r(\\phi)^\\top$" }
  - id: q2
    type: truefalse
    prompt: "$J_r(\\phi)^{-1}$ 은 모든 $\\phi \\in \\mathbb{R}^3$ 에서 존재한다."
    answer: false
    explanation: "닫힌 형태의 분모에 $\\sin\\theta$ 가 들어가 $\\theta \\to \\pi$ 에서 발산한다 — 역은 $\\theta < \\pi$ 에서만 존재한다. 이것이 큰 회전 섭동을 한 번에 선형화할 수 없는 수학적 이유다."
    concept: { front: "$J_r^{-1}$ 이 존재하는 범위", back: "$\\theta < \\pi$. $\\theta \\to \\pi$ 에서 발산하므로 큰 회전 오차는 한 번에 선형화할 수 없다" }
  - id: q3
    type: short
    prompt: "작은 각에서 $J_r^{-1}(\\phi) \\approx I + \\frac{1}{2}\\hat{\\phi} + c\\,\\hat{\\phi}^2$ 의 계수 $c$ 는?"
    answer: ["1/12", "0.0833", "0.08333", "1÷12"]
    explanation: "$J_r \\approx I - \\frac12\\hat\\phi + \\frac16\\hat\\phi^2$ 와 곱해 2차 항을 지우면 $c - \\frac14 + \\frac16 = 0$, 즉 $c = \\frac1{12}$ 다."
  - id: q4
    type: single
    prompt: "$SO(3)$ 에서 측지 거리 $\\theta$ 와 Frobenius 거리의 관계는?"
    choices:
      - "$\\lVert R_1-R_2\\rVert_F = \\theta$ (같다)"
      - "$\\lVert R_1-R_2\\rVert_F = 2\\sqrt{2}\\,|\\sin(\\theta/2)|$"
      - "$\\lVert R_1-R_2\\rVert_F = 2(1-\\cos\\theta)$"
      - "두 거리는 비교할 수 없다"
    answer: 1
    explanation: "$\\lVert R_1-R_2\\rVert_F^2 = 6 - 2\\operatorname{tr}(R_1^\\top R_2) = 4(1-\\cos\\theta) = 8\\sin^2(\\theta/2)$. 작은 각에서는 거의 비례하지만 $\\theta=\\pi$ 에서 Frobenius 거리는 $2\\sqrt2$ 로 포화된다 — 그래서 퍼진 표본의 평균이 달라진다."
```

## 이 단계 공부법

1. **좌/우를 처음부터 구분해 적는다 (30분)** — $\oplus$ 가 오른쪽인지 왼쪽인지 종이 맨 위에 쓰고
   시작한다. 이 레슨의 모든 오류는 여기서 나온다. Solà et al. 의 표기와 대조표를 만들어 둔다.
2. **Duhamel 공식을 ODE 로 이해한다 (60분)** — (1)을 외우려 하지 말고 "비동차 선형 ODE 를
   적분인자로 푼 것"으로 본다. $G$ 에 대한 ODE 를 직접 세워 보면 적분 표현이 자연스럽다.
3. **적분은 직접 해 본다 (40분)** — (3)을 유도하는 적분은 세 줄이다. $\hat u$ 에서 $\hat\phi$ 로
   되돌리는 마지막 치환에서 $\theta$ 의 거듭제곱을 틀리기 쉽다.
4. **$J_r^{-1}$ 은 급수부터, 닫힌 형태는 그 다음 (90분)** — 본문의 한 줄짜리 급수 계산($c=1/12$)을
   먼저 하고, 그 다음 P2 의 닫힌 형태를 유도한다. 유도한 식은 **반드시** 재현 과제 조건 3 으로
   검증한다 — 부호 오류는 작은 각에서 드러나지 않는다.
5. **평균을 직접 구현해 본다 (60분)** — (7)은 다섯 줄이다. 구현한 뒤 표본의 퍼짐을 키우며
   Frobenius 평균과의 차이를 그려 본다. 이 그림 하나가 "왜 매니폴드를 신경 쓰는가"에 대한 답이다.
6. **논문에서 야코비안이 나오는 자리를 전부 센다 (120분)** — Forster et al. 에서 $J_r$ 이
   등장하는 식을 하나씩 짚으며 "여기서 왜 필요한가"를 쓴다. 이 작업이 C5(상태 추정) 전체의 예습이다.

**통과 기준**: (1)→(2)→(3)을 백지에서 이어서 유도할 수 있고, $J_l = \mathrm{Exp}(\phi)J_r$ 를
증명할 수 있고, $J_r^{-1}$ 의 닫힌 형태를 유도해 수치로 검증했고, Fréchet 평균 구현이 재현 과제
네 조건을 만족하고, 논문 2편의 노트가 있다.
