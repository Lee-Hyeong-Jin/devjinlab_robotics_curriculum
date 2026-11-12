---
id: c3-contraction-incremental
title: 수축 이론과 증분 안정성
summary: >-
  평형점이 아니라 궤적 **사이**의 수렴을 보는 관점을 세운다. 가상 변위(virtual displacement)와
  리만 계량으로 수축 조건을 유도하고, 그 조건이 왜 지수 수렴과 증분 안정성을 주는지 증명
  수준에서 다룬다. 이어서 교란에 대한 관(tube) 경계를 유도하고, 제어 수축 계량(CCM)이 왜
  볼록 문제가 되는지 본다. 끝으로 인증된 수렴률이 실제 수렴률보다 얼마나 보수적인지를
  수치로 측정한다.
objectives:
  - 가상 변위에서 수축 조건과 지수 수렴 경계를 빠진 줄 없이 유도할 수 있다.
  - 유클리드 계량으로는 수축이 보이지 않는 계에 대해 상수 계량을 LMI 로 찾을 수 있다.
  - 교란이 있을 때의 관 반지름 $\sup\lVert\Theta d\rVert/\lambda$ 를 비교 보조정리로 유도할 수 있다.
  - 제어 수축 계량의 조건이 쌍대 계량 $W = M^{-1}$ 에서 볼록해지는 이유를 설명할 수 있다.
  - 인증된 수렴률과 실측 수렴률의 간극을 직접 측정하고 보수성의 출처를 지목할 수 있다.
prerequisites: [c3-lyapunov-stability]
difficulty: 5
estimated_minutes: 540
tags: [nonlinear-control, contraction, incremental-stability, riemannian-metric, ccm, research]
activities:
  - id: c3-contraction-incremental-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c3-contraction-incremental-papers
    kind: reading
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c3-contraction-incremental-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: c3-contraction-incremental-reproduction
    kind: exercise
    title: 재현 과제 — 수축 계량과 실측 수렴률 비교 (R1)
    estimated_minutes: 105
  - id: c3-contraction-incremental-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Lohmiller & Slotine — On contraction analysis for non-linear systems (1998)"
    url: https://doi.org/10.1016/S0005-1098(98)00019-3
    kind: article
    note: 필독 1. 수축 해석의 원전. §2(기본 결과)와 §3(일반화 계량)이 이 레슨의 R1·R2 다.
  - title: "Manchester & Slotine — Control contraction metrics (2017)"
    url: https://arxiv.org/abs/1503.03144
    kind: article
    note: 필독 2. 제어기 설계를 볼록 문제로 바꾸는 조건. §III·§IV 를 읽는다.
  - title: "Tsukamoto, Chung & Slotine — Contraction theory for nonlinear stability analysis and learning-based control: a tutorial overview (2021)"
    url: https://arxiv.org/abs/2110.00675
    kind: article
    note: 필독 3. 2021년까지의 지도. 학습 기반 제어와의 접점(§5–6)을 본다. Annual Reviews in Control 52:135-169.
  - title: "Khalil, Nonlinear Systems (3rd ed., 2002)"
    kind: book
    note: ch.9 (비교·섭동 해석)와 ch.3.4 (비교 보조정리). 수축 이론은 다루지 않지만 R2 의 도구가 여기 있다. (공식 URL 미확인)
  - title: "CVXPY"
    url: https://www.cvxpy.org/
    kind: other
    note: 재현 과제의 LMI 를 푸는 도구. SCS·Clarabel 중 아무 솔버나 쓴다.
---

# 수축 이론과 증분 안정성

## 전제와 기호

`c3-lyapunov-stability` 의 Lyapunov 함수는 **하나의 평형점**까지의 거리를 재고,
`c3-feedback-linearization` 은 그 평형점을 선형계의 원점으로 옮겼다. 수축 이론은 질문을 바꾼다:
**두 궤적 사이의 거리**가 줄어드는가? 평형점을 몰라도, 심지어 평형점이 없어도(시변계) 답할 수
있고, 그래서 추적 제어·관측기·관(tube) 기반 계획에 바로 쓰인다.

전제: 행렬 지수와 변분방정식(`c3-feedback-linearization` 의 R3 에서 썼다), 비교 보조정리
(`c3-lyapunov-stability` 의 R4), 대칭행렬의 정부호성과 LMI. 리만 계량은 여기서 **필요한 만큼만**
정의한다 — 다양체 위의 일반론은 `c1-manifold-optimization` 과 `c5-manifold-estimation` 의 몫이다.

| 기호 | 뜻 |
|---|---|
| $\dot{x} = f(x,t)$ | $f$ 가 $x$ 에 대해 $C^1$. 평형점의 존재를 가정하지 않는다 |
| $J(x,t) = \dfrac{\partial f}{\partial x}(x,t)$ | 야코비안 |
| $\delta x$ | 가상 변위 — 같은 시각의 두 이웃 궤적의 차. $\dot{\delta x} = J\,\delta x$ |
| $M(x,t) \succ 0$ | 리만 계량. $\Theta$ 는 $M = \Theta^\top\Theta$ 인 아무 분해 |
| $\dot{M}$ | 궤적을 따른 전미분 $\dfrac{\partial M}{\partial t} + \sum_i \dfrac{\partial M}{\partial x_i}\dot{x}_i$ |
| $\lVert \delta x\rVert_M$ | $\sqrt{\delta x^\top M \delta x}$ |
| $d_M(x,y)$ | 리만 거리 $\inf_\gamma \int_0^1 \lVert \gamma'(s)\rVert_{M(\gamma(s))}\,ds$ ($\gamma(0)=x$, $\gamma(1)=y$) |
| $\underline{m}, \overline{m}$ | 균일 경계 $\underline{m}I \preceq M \preceq \overline{m}I$ |
| $\lambda$ | 수축률(contraction rate) |
| $W$ | 쌍대 계량 $M^{-1}$ |

이 레슨의 달리는 예는 **감쇠된 비선형 진자형 계**다:

$$
\dot{x}_1 = x_2, \qquad \dot{x}_2 = -2x_1 - 2x_2 - \sin x_1. \tag{1}
$$

야코비안은 $J(x_1) = \begin{bmatrix}0 & 1\\ -2-\cos x_1 & -2\end{bmatrix}$ 이고
$\cos x_1 \in [-1,1]$ 이므로 $J$ 는 두 꼭짓점

$$
J_+ = \begin{bmatrix}0&1\\-3&-2\end{bmatrix}, \qquad
J_- = \begin{bmatrix}0&1\\-1&-2\end{bmatrix} \tag{2}
$$

의 볼록 결합 안에 있다. 두 꼭짓점 모두 고윳값의 실수부가 $-1$ 이다($J_+$: $-1\pm i\sqrt2$,
$J_-$: $-1$ 이중근). **그런데 유클리드 계량으로는 수축이 보이지 않는다**:

$$
\lambda_{\max}(J_+^\top + J_+) = -2 + 2\sqrt2 \approx 0.8284271 > 0, \qquad
\lambda_{\max}(J_-^\top + J_-) = 0. \tag{3}
$$

즉 거리가 **일시적으로 늘어난다**. 계량을 바꾸는 일이 왜 본질인지가 (3)에 들어 있다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (수축 조건과 지수 수렴) [D3]** — 전진 불변이고 측지적으로 볼록한 영역
  $\mathcal{X}$ 에서 $\underline{m}I \preceq M \preceq \overline{m}I$ 이고
  $$
  \dot{M} + J^\top M + M J \preceq -2\lambda M \tag{4}
  $$
  이면 그 영역의 임의의 두 궤적에 대해 $d_M(x(t),y(t)) \le d_M(x(0),y(0))\,e^{-\lambda t}$ 이고,
  유클리드 거리로는
  $$
  \lVert x(t)-y(t)\rVert \le \sqrt{\overline{m}/\underline{m}}\;\lVert x(0)-y(0)\rVert\,e^{-\lambda t} \tag{5}
  $$
  이다. 즉 계는 **증분 지수 안정(incrementally exponentially stable)** 이다.
- **R2 (계량 선택 = LMI) [D2]** — $M$ 을 상수로 제한하면 (4)는 $M$ 에 대해 선형이고, $J$ 가
  다면체 $\operatorname{conv}\{J_1,\dots,J_V\}$ 안에 있으면 **꼭짓점에서만** 확인하면 된다.
  (1)에 대해 $\lambda$ 를 이분법으로 최대화하면 $\lambda^\star \approx 0.4913$ 이고,
  $\lambda = 0.4814$ 에서 예를 들어
  $$
  M = \begin{bmatrix}3.865360 & 1.876934\\ 1.876934 & 2.229473\end{bmatrix},
    \qquad \lambda_{\min}(M)=1,\ \lambda_{\max}(M) = 5.094833 \tag{6}
  $$
  가 (4)를 만족한다(두 꼭짓점의 LMI 잔차 최대 고윳값 $\approx 3\cdot10^{-11}$).
- **R3 (교란에 대한 관 경계) [D2]** — 교란받은 궤적 $\dot x = f(x,t)+d(t)$ 와 명목 궤적
  $\dot y = f(y,t)$ 에 대해
  $$
  d_M(x(t),y(t)) \le d_M(x(0),y(0))\,e^{-\lambda t} + \frac{1}{\lambda}\sup_{s\le t}\lVert \Theta\, d(s)\rVert, \tag{7}
  $$
  즉 수축률이 곧 **교란 이득의 역수**다. 점근 관 반지름은 $\sup\lVert\Theta d\rVert/\lambda$.
- **R4 (제어 수축 계량, CCM) [D2]** — $\dot x = f(x) + B(x)u$ 에서 "모든 궤적을 추적할 수 있게
  하는" 계량 조건은 $B$ 의 직교여공간으로 사영하면 쌍대 계량 $W = M^{-1}$ 에 대해 **볼록**하다:
  $$
  B_\perp^\top\!\left(-\dot{W} + \frac{\partial f}{\partial x}W + W\frac{\partial f}{\partial x}^\top + 2\lambda W\right)\!B_\perp \preceq 0. \tag{8}
  $$
  CLF 탐색은 비볼록인데 CCM 탐색은 볼록하다는 것이 Manchester–Slotine 의 요점이다.
- **R5 (수축 $\Rightarrow$ 평형점의 유일성) [D1]** — 시불변계가 전진 불변 영역에서 수축하면 그
  영역의 평형점은 **최대 하나**다. 따라서 평형점이 둘 이상인 계($\dot x = x - x^3$ 등)는 그
  영역에서 어떤 계량으로도 수축하지 않는다.

## 유도

### R1 — 가상 변위에서 지수 수렴까지

**1단계 (가상 변위의 동역학).** 같은 시각의 두 이웃 궤적의 차 $\delta x$ 는 변분방정식

$$
\dot{\delta x} = J(x,t)\,\delta x \tag{9}
$$

를 따른다(해의 초기조건에 대한 미분가능성에서 나온다). 여기서 $x(t)$ 는 **실제 궤적**이고,
$J$ 는 그 궤적을 따라 평가된다 — 이 "궤적을 따라" 라는 점이 선형화와 수축의 차이다.

**2단계 (계량으로 잰 길이의 미분).** $V := \delta x^\top M(x,t)\,\delta x$ 를 미분한다.
$M$ 이 $x$ 와 $t$ 에 의존하므로 전미분 $\dot M$ 이 나온다:

$$
\dot{V} = \delta x^\top \dot{M}\delta x + 2\,\delta x^\top M \dot{\delta x}
  = \delta x^\top\big(\dot{M} + J^\top M + MJ\big)\delta x. \tag{10}
$$

(두 번째 항에 (9)를 넣고 $\delta x^\top MJ\delta x = \delta x^\top J^\top M\delta x$ 의 전치
대칭화를 쓴다.) (4)를 쓰면 $\dot V \le -2\lambda V$ 이고, 따라서

$$
\lVert \delta x(t)\rVert_M \le \lVert \delta x(0)\rVert_M\,e^{-\lambda t}. \tag{11}
$$

**3단계 (무한소에서 유한 거리로).** (11)은 무한소 변위의 이야기다. 유한한 두 점으로 올리려면
경로를 하나 잡고 그 길이를 잰다. $x(0)$ 과 $y(0)$ 을 잇는 매끄러운 경로 $\gamma_0(s)$ 를 잡고,
각 $s$ 에서 $\gamma_0(s)$ 를 초기조건으로 하는 궤적을 $\gamma_t(s)$ 라 하자. 그러면
$\partial\gamma_t/\partial s$ 는 각 $s$ 에서 (9)를 만족하는 가상 변위이므로 (11)이 점별로 적용되고

$$
L(t) := \int_0^1 \left\lVert \frac{\partial \gamma_t}{\partial s}(s)\right\rVert_{M(\gamma_t(s),t)} ds
  \le e^{-\lambda t}\int_0^1 \left\lVert \frac{\partial \gamma_0}{\partial s}(s)\right\rVert_{M(\gamma_0(s),0)} ds
  = e^{-\lambda t} L(0). \tag{12}
$$

리만 거리는 경로 길이의 하한이므로 $d_M(x(t),y(t)) \le L(t)$ 이고, $\gamma_0$ 를 측지선으로
택하면 $L(0) = d_M(x(0),y(0))$ 다. 두 부등식을 이으면 R1 의 첫 결론이 나온다. (여기서
$\mathcal{X}$ 가 **측지적으로 볼록**해야 한다 — 경로 $\gamma_t$ 가 영역을 벗어나면 (4)를 쓸
자격이 없다. 생략한 기술적 단계: 측지선의 존재와 $\gamma_t$ 의 매끄러움, Lohmiller–Slotine §3.)

**4단계 (유클리드 거리로).** $\underline{m}I\preceq M\preceq\overline{m}I$ 에서
$\sqrt{\underline{m}}\lVert u\rVert \le \lVert u\rVert_M \le \sqrt{\overline{m}}\lVert u\rVert$ 이고,
경로 길이로 올리면 $\sqrt{\underline{m}}\lVert x-y\rVert \le d_M(x,y) \le \sqrt{\overline{m}}\lVert x-y\rVert$.
따라서

$$
\lVert x(t)-y(t)\rVert \le \frac{d_M(x(t),y(t))}{\sqrt{\underline{m}}}
  \le \frac{e^{-\lambda t}}{\sqrt{\underline{m}}}d_M(x(0),y(0))
  \le \sqrt{\frac{\overline{m}}{\underline{m}}}\;\lVert x(0)-y(0)\rVert e^{-\lambda t},
$$

즉 (5)다. 계량의 **조건수**가 그대로 과도 응답의 배율이 된다 — (6)에서는
$\sqrt{5.094833/1} \approx 2.2572$ 다.

**가정이 깨지는 곳**: ⓐ $\overline{m}$ 이 없으면(계량이 어느 방향으로 무한히 커지면) (5)의
배율이 무의미해진다 — 리만 거리는 줄지만 유클리드 거리의 결론을 잃는다. ⓑ 영역이 측지적으로
볼록하지 않으면 3단계의 경로가 조건이 성립하는 곳을 벗어날 수 있고, 두 궤적이 각자 수축
영역에 있어도 서로 수축하지 않는다. ⓒ 수축은 **상대적** 성질이다: 두 궤적이 서로 가까워지는
것은 둘 다 발산하는 경우에도 성립할 수 있다. 유계성은 따로 보여야 한다.

### R2 — 상수 계량을 LMI 로 찾기 (그리고 유클리드가 왜 실패하는가)

먼저 손으로 풀리는 예를 본다. $J = \begin{bmatrix}-1 & k\\ 0 & -1\end{bmatrix}$ ($k$ 는 큰 수)와
대각 계량 $M = \operatorname{diag}(1, m)$ 을 (4)에 넣으면 $\dot M = 0$ 이므로

$$
J^\top M + MJ + 2\lambda M
  = \begin{bmatrix}-2+2\lambda & k\\ k & -2m + 2\lambda m\end{bmatrix} \preceq 0
$$

이고, $2\times2$ 대칭행렬이 음반정부호인 조건(대각 성분 $\le0$ 과 행렬식 $\ge0$)에서

$$
(2-2\lambda)(2m-2\lambda m) \ge k^2
  \quad\Longleftrightarrow\quad m \ge \frac{k^2}{4(1-\lambda)^2}. \tag{13}
$$

따라서 $\lambda < 1$ 이면 $m$ 을 충분히 크게 잡아 언제나 수축을 **인증할 수 있다**. 예를 들어
$k = 10$, $\lambda = 0.5$ 에서 $m \ge 100$. 반면 유클리드 계량($m=1$)에서는 $J$ 의 대칭부
$\begin{bmatrix}-1 & k/2\\ k/2 & -1\end{bmatrix}$ 의 고윳값이 $-1 \pm k/2$ 이므로 $k>2$ 면
양의 고윳값이 생겨 **아무 수축률도 얻지 못한다**. 같은 계가 계량을 바꾸면 수축하고 안 하고가
갈린다 — 수축은 좌표에 의존하는 성질이 아니라 **계량과 함께 주장되는** 성질이다.

이제 (1)로 돌아간다. $\cos x_1$ 에 대해 $J$ 가 아핀이므로, 상수 $M$ 에 대해 (4)는 꼭짓점 (2)의
두 LMI 와 **동치**다(볼록 결합은 음반정부호를 보존한다). 따라서

$$
\max_{\lambda,\,M} \lambda \quad\text{s.t.}\quad M \succeq I,\quad
  J_\pm^\top M + MJ_\pm + 2\lambda M \preceq 0 \tag{14}
$$

를 $\lambda$ 에 대한 이분법 + 각 단계의 SDP 로 푼다($\lambda$ 를 고정하면 $M$ 에 대해 선형).
수치로 $\lambda^\star \approx 0.4913$ 이고, $\lambda = 0.4814$ 에서 (6)의 $M$ 이 나온다.
**실측 수렴률은 약 $1.00$** (무작위 60쌍의 궤적에서 중앙값 1.0003, 최소 0.9760, 최대 1.0258)
이므로 인증값은 실제보다 **약 2.08배 보수적**이다. 보수성의 출처는 셋이다: ⓐ 상수 계량으로
제한했다 ⓑ $\cos x_1$ 의 전 구간을 꼭짓점으로 덮었다(실제 궤적은 그 구석을 거의 방문하지
않는다) ⓒ 모든 방향의 $\delta x$ 에 대해 동시에 성립하라고 요구했다. ⓐ 는 상태 의존 계량(SOS)
으로, ⓑ 는 영역을 좁혀서 줄일 수 있다 — 재현 과제의 확장 과제다.

**가정이 깨지는 곳**: 꼭짓점 논증은 $J$ 가 **파라미터에 아핀**이고 그 파라미터가 다면체에 갇힐
때만 성립한다. $J$ 가 $x$ 에 비선형으로(예: $x_1^2$) 의존하면 꼭짓점 집합이 보수적이거나
아예 유계가 아니다. 그때는 상태 의존 계량 + SOS 로 가야 하고, `c3-lyapunov-stability` 의 R5 와
같은 차수 간극·수치 문제를 다시 만난다.

### R3 — 교란이 만드는 관(tube)

$\dot x = f(x,t) + d(t)$ 와 $\dot y = f(y,t)$ 를 비교한다. 3단계의 경로 논증을 그대로 쓰되,
교란이 경로의 한쪽 끝에만 들어오므로 길이의 미분에 추가 항이 붙는다. $R(t) := d_M(x(t),y(t))$
라 두면(절대연속이고 거의 모든 곳에서 미분가능)

$$
\dot{R} \le -\lambda R + \lVert \Theta(x,t)\,d(t)\rVert. \tag{15}
$$

(유도: 측지선을 따라 (10)을 적용하면 $-\lambda$ 항이 나오고, 끝점에 더해진 속도 $d$ 는 길이의
변화율에 최대 $\lVert\Theta d\rVert$ 만큼 기여한다 — Cauchy–Schwarz. 생략: 측지선이 유일하지
않을 때의 상미분 포함 처리, Lohmiller–Slotine §3·Tsukamoto et al. §2.4.)

(15)에 비교 보조정리를 적용하면

$$
R(t) \le R(0)e^{-\lambda t} + \int_0^t e^{-\lambda(t-s)}\lVert\Theta d(s)\rVert\,ds
     \le R(0)e^{-\lambda t} + \frac{1-e^{-\lambda t}}{\lambda}\sup_{s\le t}\lVert\Theta d(s)\rVert, \tag{16}
$$

즉 (7)이다. **수치 확인**: (1)과 (6)의 계량에서 두 번째 채널에 $\lvert d\rvert \le \delta$ 의
구형파 교란을 넣으면, 무작위 20쌍에 대해 (7)의 비 $R(t)/\text{bound}(t)$ 의 최댓값이
$\delta=0.1$ 에서 0.99984, $\delta=0.5$ 에서 0.99927 로 **경계를 넘지 않는다**. 점근 관 반지름
$\sup\lVert\Theta d\rVert/\lambda$ 는 각각 0.3101, 1.5507 이다.

이 식이 수축 이론이 로보틱스에서 쓰이는 주된 이유다. $\lambda$ 를 키우면 관이 좁아지고,
관이 좁아지면 계획 단계에서 장애물 여유를 작게 잡을 수 있다 — 설계가
"수렴률 ↔ 여유 ↔ 제어 노력"의 한 축으로 정리된다.

**가정이 깨지는 곳**: $\Theta$ 가 상태에 의존하면 $\sup\lVert\Theta d\rVert$ 는 **영역 전체의**
상한이어야 하고, 영역을 넓게 잡으면 관이 급격히 커진다. 또 (7)은 교란이 유계라는 가정에
기대므로, 확률 교란에는 그대로 쓰이지 않는다(확률 수축 이론은 별도 결과를 쓴다).

### R4 — CCM 조건이 쌍대 계량에서 볼록해지는 이유

$\dot x = f(x) + B(x)u$ 에서 제어를 쓰면 가상 변위의 동역학이
$\dot{\delta x} = (A(x,u) + B\,\partial u/\partial x)\delta x + B\,\delta u$ 로 바뀐다
($A := \partial(f+Bu)/\partial x$). 요점은 **$\delta u$ 로 끌 수 있는 방향은 $B$ 의 상(range)**
이라는 것이다. 따라서 "어떤 피드백을 쓰면 수축하게 만들 수 있는가" 는 $B$ 로 **끌 수 없는**
방향에서만 조건이 필요하다:

$$
\delta x^\top M B = 0 \;\Longrightarrow\;
  \delta x^\top\big(\dot M + A^\top M + MA + 2\lambda M\big)\delta x \le 0. \tag{17}
$$

(17)은 $M$ 에 대해 **조건부**이고 $M$ 과 $\delta x$ 가 섞여 있어 그대로는 볼록하지 않다.
여기서 $W := M^{-1}$ 로 바꾸는 것이 Manchester–Slotine 의 수(手)다. $\delta x = M^{-1}\eta
= W\eta$ 로 치환하면 조건 $\delta x^\top MB = 0$ 은 $\eta^\top B = 0$, 즉 $\eta$ 가
$B_\perp$ 의 열공간에 있다는 **$M$ 과 무관한** 조건이 되고, (17)의 2차형식은
$\dot{W}$ 항의 부호가 바뀌면서 (8)이 된다:

$$
B_\perp^\top\!\left(-\dot W + \frac{\partial f}{\partial x}W + W\frac{\partial f}{\partial x}^\top + 2\lambda W\right)\!B_\perp \preceq 0.
$$

($\frac{d}{dt}(M^{-1}) = -M^{-1}\dot M M^{-1}$ 에서 부호가 뒤집힌다. $A$ 가 $u$ 에 의존하는 항은
$B$ 의 상에 들어가 $B_\perp$ 와의 곱에서 사라진다 — 생략: Manchester–Slotine Thm 1 의 전개.)
(8)은 $W$ 에 대해 **선형**이므로 $W$ 를 기저함수의 선형결합으로 두면 SOS/SDP 로 탐색할 수 있다.
CLF 탐색이 비볼록한 것과 대조된다: CLF 는 "어떤 $u$ 가 존재한다" 를 $V$ 와 $u$ 에 대해 동시에
요구하는데, CCM 은 그 존재를 **$B_\perp$ 사영**으로 미리 소거한다.

**가정이 깨지는 곳**: (8)은 입력 제약이 없다고 가정한다. $\lvert u\rvert \le u_{\max}$ 가 있으면
측지선을 따라 적분해 얻는 피드백이 포화될 수 있고, 그때 보장은 영역 제한부(local)로 약해진다.
또 (8)은 $W$ 의 **균일** 경계를 요구하므로, 넓은 영역에서 성립하는 $W$ 를 찾으려면 수축률을
낮춰야 한다 — R2 에서 본 보수성이 설계 전체에 다시 나타난다.

## 증명 스케치

### R5 — 수축하면 평형점은 최대 하나다

**가설** H1: 시불변계 $\dot x = f(x)$. H2: 전진 불변이고 측지적으로 볼록한 $\mathcal{X}$ 에서
(4)가 $\lambda>0$ 과 균일 유계 $M$ 으로 성립. **결론** C: $\mathcal{X}$ 의 평형점은 최대 하나.

**전략**: 평형점은 상수 궤적이다. 두 상수 궤적 사이의 거리는 변하지 않는데 R1 은 지수적으로
줄어든다고 말한다 — 모순.

1. $x^\star \ne y^\star$ 가 둘 다 평형점이라 하자. 각각에서 출발한 궤적은
   $x(t)\equiv x^\star$, $y(t)\equiv y^\star$ 다.
2. R1 에 의해 $d_M(x^\star,y^\star) = d_M(x(t),y(t)) \le d_M(x^\star,y^\star)e^{-\lambda t}$.
3. $t\to\infty$ 에서 오른쪽은 0 이고 왼쪽은 상수 $d_M(x^\star,y^\star) > 0$ 이다
   ($M \succeq \underline{m}I$ 이므로 서로 다른 두 점의 리만 거리는 양수). 모순.
4. 따라서 평형점은 최대 하나다. 존재까지 얻으려면 유계성·콤팩트성을 더해야 한다
   (예: 콤팩트 전진 불변 $\mathcal{X}$ 에 Brouwer 고정점).

**가설을 지우면**: H2 의 **측지적 볼록성**을 빼면 결론이 거짓이 될 수 있다. $\dot x = x - x^3$ 은
$x=\pm1$ 근방에서 각각 국소 수축하지만($f'(\pm1) = -2$), 두 영역을 잇는 경로가 $x=0$ 을 지나
거기서 $f'(0)=+1>0$ 이므로 전체 영역에서는 수축이 아니다. 평형점이 셋이라는 사실이 그것을
증명한다. **이것이 수축 이론의 실제 비용이다**: 전역 수축은 매우 강한 요구이고, 다중 평형점을
가진 계(대부분의 로봇 작업)에서는 영역을 쪼개 주장해야 한다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R2)** (13)을 유도하고, $\lambda \to 1^-$ 에서 필요한 $m$ 이 어떻게 발산하는지
쓰라. 그 발산이 (5)의 배율 $\sqrt{\overline m/\underline m}$ 에 어떤 대가를 요구하는가?
*해답 스케치*: $2\times2$ 대칭행렬의 음반정부호 조건(대각 $\le0$, 행렬식 $\ge0$)을 그대로 쓴다.
$m \sim k^2/4(1-\lambda)^2 \to \infty$ 이므로 배율이 $k/2(1-\lambda)$ 로 커진다 — **수렴률을
높인 인증은 과도 응답의 상한을 그만큼 나쁘게 만든다.**

**P2 (유도, ★★, R3)** (16)의 두 번째 부등식을 비교 보조정리 없이 직접(적분 인자
$e^{\lambda t}$ 를 곱해서) 유도하라. $\Theta$ 가 상태에 의존할 때 어느 단계에서 "영역 전체의
상한" 이 필요해지는가?
*해답 스케치*: $\frac{d}{dt}(e^{\lambda t}R) \le e^{\lambda t}\lVert\Theta d\rVert$ 를 적분한다.
$\Theta$ 가 $x(s)$ 에서 평가되므로, 궤적이 어디를 지나는지 모르는 채로 쓰려면 영역 상한이 필요하다.

**P3 (계산, ★, R1·R2)** (1)에 대해 ⓐ (3)의 두 고윳값, ⓑ (6)의 $M$ 이 두 꼭짓점에서 (4)를
$\lambda = 0.4814$ 로 만족하는지, ⓒ (5)의 배율을 구하라.
*정답*: ⓐ $-2+2\sqrt2 = 0.8284271$ 과 $0$ (허용오차 $10^{-6}$) — 둘 다 음수가 아니므로 유클리드
계량으로는 수축이 인증되지 않는다. ⓑ 두 LMI 의 최대 고윳값이 $\le 10^{-8}$ (참조 구현은
$3\cdot10^{-11}$). ⓒ $\sqrt{5.094833} = 2.2571738$ (허용오차 $10^{-6}$).

**P4 (구현, ★★★, R2·R4)** (14)를 이분법 + SDP 로 풀어 $\lambda^\star$ 를 재현하고, 이어서
$M(x_1) = M_0 + M_1\cos x_1$ 꼴의 **상태 의존** 계량으로 확장해 $\lambda$ 가 개선되는지 보라.
$\dot M$ 항을 잊지 말 것 — $\dot M = -M_1 \sin x_1\,\dot x_1 = -M_1 x_2\sin x_1$ 이므로
$x_2$ 의 범위를 유계로 제한해야 LMI 가 된다.
*루브릭*: ⓐ 상수 계량에서 $\lambda^\star = 0.4913 \pm 0.002$ 를 재현한다 ⓑ 상태 의존 계량의
결과가 상수 계량보다 나쁘지 않다(같거나 개선) ⓒ $\dot M$ 항과 $x_2$ 유계화 가정을 코드와
보고서에 **명시**한다 ⓓ 개선이 없으면 왜 없는지(어느 꼭짓점이 묶는지) 분석한다.

**P5 (반례, ★★, R1·R5)** "점근 안정이면 적당한 계량에서 수축한다" 는 주장을 반박하라.
① 평형점이 여럿인 계로, ② 평형점이 하나인데도 어떤 **상수** 계량에서도 수축하지 않는 계로,
각각 하나씩 보여라.
*성질 체크리스트*: ① $\dot x = x - x^3$ 처럼 평형점 3개(R5 로 즉시 결론). ② 야코비안이
영역 안에서 어떤 상수 계량으로도 (4)를 만족하지 못하는 예 — 예컨대 $J(x)$ 의 꼭짓점 중 하나가
불안정하면(고윳값의 실수부 $>0$) 상수 계량 LMI 가 불가해다. 그 계가 여전히 점근 안정일 수
있다는 점(궤적이 그 영역을 오래 머물지 않음)을 보이면 완성.

**P6 (논문, ★★, R4)** Manchester & Slotine 2017 을 읽고 ⓐ 정확히 **무엇이** 어느 변수에 대해
볼록한지, ⓑ 그 볼록성이 CLF 탐색의 어떤 비볼록성을 피하는지, ⓒ 입력 제약·외란이 있을 때
보장이 어떻게 약해지는지를 각각 3문장 이내로 쓰라.
*루브릭*: "쌍대 계량 $W=M^{-1}$ 에 대해 선형, $B_\perp$ 사영으로 $u$ 의 존재를 소거" 를 짚으면
통과. "$W$ 와 $\lambda$ 를 동시에 최적화하면 다시 비볼록" 까지 쓰면 가점.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Lohmiller & Slotine, "On contraction analysis for non-linear systems" (1998, Automatica)**
   — 역할: `원전(seminal)`. <https://doi.org/10.1016/S0005-1098(98)00019-3>
   §2 가 R1 의 기본형, §3 이 일반 계량과 좌표변환이다.
   추가 질문: ⓐ 저자들이 "수축" 을 Lyapunov 와 구별하는 지점은 무엇인가 — 어떤 가정을 **버렸는가**?
   ⓑ 논문의 결과는 궤적의 **유계성**을 주는가, 아닌가?
2. **Manchester & Slotine, "Control contraction metrics: convex and intrinsic criteria for
   nonlinear feedback design" (2017, IEEE T-AC; arXiv 2015)** — 역할: `표준(standard)`.
   <https://arxiv.org/abs/1503.03144>
   추가 질문: ⓐ "intrinsic" 은 무엇에 대한 불변성을 뜻하는가? ⓑ 측지선을 따라 피드백을 적분하는
   구현이 실시간에 요구하는 계산은 무엇인가?
3. **Tsukamoto, Chung & Slotine, "Contraction theory for nonlinear stability analysis and
   learning-based control: a tutorial overview" (2021, Annual Reviews in Control)**
   — 역할: `서베이(survey)`. <https://arxiv.org/abs/2110.00675>
   추가 질문: ⓐ 학습된 계량(neural contraction metric)이 주는 보장은 "학습된 모델에 대한" 것인가
   "실제 계에 대한" 것인가 — 그 차이가 어디서 메워지는가? ⓑ 서베이가 열린 문제로 꼽는 것 중
   이 레슨의 재현 과제로 측정 가능한 것은 무엇인가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R1 (수치 검증).** 계산 예산: 노트북 CPU 1분 이내(궤적 쌍을 배열로 묶어 한 번에 적분하면
충분하다), numpy + scipy + SDP 솔버 하나. 대상은 (1)이고 입력 데이터는 없다.

> 설계 노트: blueprint 의 원래 문구는 "수렴률 상한이 실제 수렴률을 상회하는지" 였다. 인증된
> $\lambda$ 는 **거리의 상한**을 주고 실제 수렴률의 **하한**이므로, 아래는 그 방향으로 정확히
> 다시 쓴 것이다(측정값은 모두 실행해 확인했다).

**수용 기준 (네 조건 모두)**

1. **유클리드 실패와 인증서**: (3)의 두 값을 $10^{-6}$ 이내로 재현하고(각각 $0.8284271$, $0$),
   이분법 + SDP 로 $\lambda \ge 0.48$ 과 $M \succeq I$ 를 찾는다. 찾은 $(M,\lambda)$ 는
   꼭짓점 두 개뿐 아니라 $x_1$ 을 $[-\pi,\pi]$ 에서 균등 추출한 $10^4$ 점 **전부**에서
   $\lambda_{\max}(J^\top M + MJ + 2\lambda M) \le 10^{-8}$ 을 만족해야 한다.
2. **쌍 경계**: $[-3,3]^2$ 에서 무작위로 뽑은 궤적 쌍 $10^3$ 개를 RK4($\Delta t \le 2\cdot10^{-3}$,
   $T=12$)로 적분해, 모든 쌍과 모든 시각에서
   $d_M(x(t),y(t)) \le d_M(x(0),y(0))e^{-\lambda t}\,(1+10^{-6})$.
   (상수 계량이므로 $d_M(x,y) = \lVert\Theta(x-y)\rVert$ 로 계산한다.)
3. **보수성 측정**: 같은 쌍들에서 실측 수렴률
   $\hat\lambda = -\ln\!\big(d_M(T)/d_M(0)\big)/T$ 의 중앙값이 $1.00 \pm 0.05$ 이고 최소값이
   $\lambda$ 보다 크다. 비 $\hat\lambda_{\text{median}}/\lambda$ 를 보고한다(참조 구현: 2.08).
4. **관 경계**: 두 번째 채널에 $\lvert d\rvert \le \delta$ 인 교란(구형파 또는 무작위 전환)을
   넣고 $\delta \in \{0.1, 0.5\}$ 에 대해, 무작위 쌍 $10^2$ 개의 모든 시각에서 (7)이 성립한다
   ($R/\text{bound} \le 1+10^{-6}$). 점근 관 반지름 $\sup\lVert\Theta d\rVert/\lambda$ 를
   보고한다(참조 구현: $0.3101$, $1.5507$).

**비교 대상**: ⓐ 유클리드 계량($M=I$) — 조건 1 에서 **실패해야 한다**(인증 불가).
ⓑ 실측 수렴률 $\approx 1.00$ — 인증값은 반드시 이보다 작아야 하고(조건 3), 크면 LMI 나
거리 계산이 틀린 것이다. ⓒ 참조 수치: $\lambda^\star \approx 0.4913$, (6)의 $M$,
$\sqrt{\overline m/\underline m} = 2.2572$.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 인증 $\lambda$ 가 실측 수렴률보다 크다 | 거리를 $\lVert x-y\rVert$ 로 재고 $\Theta$ 를 빼먹었다 | $M=I$ 로 돌려 조건 1 이 실패하는지 본다 — 실패하지 않으면 LMI 부호가 뒤집혔다 |
| SDP 가 $\lambda$ 를 아무리 올려도 가해라고 한다 | $M \succeq I$ 같은 정규화가 없어 $M \to 0$ 으로 축퇴 | 해의 $\lambda_{\min}(M)$ 과 LMI 잔차를 직접 출력한다 |
| 조건 2 가 아주 큰 초기 거리에서만 깨진다 | 영역 밖에서 꼭짓점 덮개가 유효하지 않다(이 예는 전역이므로 적분 오차일 가능성이 높다) | $\Delta t$ 를 절반으로 줄여 위반이 사라지는지 본다 |
| 조건 4 의 비가 1 을 조금 넘는다 | $\sup\lVert\Theta d\rVert$ 를 교란 벡터가 아니라 성분 크기로 계산 | $\lVert\Theta(0,\delta)^\top\rVert$ 를 손으로 계산해 대조한다 |
| 상태 의존 계량(P4)에서 LMI 가 불가해 | $\dot M$ 항을 빼먹었거나 $x_2$ 를 유계화하지 않았다 | $M_1 = 0$ 으로 두면 상수 계량 결과가 복원되는지 확인한다 |

## 열린 문제

- **(열린 문제) 계량을 어떻게 찾는가 — 그리고 학습된 계량의 보장** — 상태 의존 계량의 탐색은
  SOS 로 가면 차원에 대해 비싸고, 신경망으로 가면 보장이 "학습된 모델에 대한" 것으로 약해진다.
  현재 접근: [Tsukamoto & Chung 2020](https://arxiv.org/abs/2006.04361) 의 신경 수축 계량,
  [Sun, Jha & Fan 2020](https://arxiv.org/abs/2011.12569) 의 인증된 제어 학습,
  [Singh et al. 2019](https://arxiv.org/abs/1907.13122) 의 수축 기반 정규화로 학습하는 동역학.
  비어 있는 자리: 학습 오차 $\to$ 수축률 손실의 명시적 사상.
- **(열린 문제) 인증의 보수성** — 이 레슨의 측정값이 그 자체로 열린 문제다: 상수 계량·꼭짓점
  덮개로 얻은 $\lambda=0.49$ 와 실측 $1.00$ 의 2배 간극 중 **어느 부분이 본질적이고 어느 부분이
  기법의 한계인지** 구분하는 일반적 방법이 없다. 비어 있는 자리: 주어진 계에 대해 달성 가능한
  최대 수축률의 상한(즉 "더 좋은 계량은 없다"는 증명).
- **(열린 문제) 접촉·충격이 있는 계의 수축** — 충격에서 상태가 점프하면 가상 변위가 불연속이고
  (9)가 무의미해진다. 리셋 사상의 야코비안이 계량에 대해 비확대(non-expansive)여야 한다는
  조건이 알려져 있지만, 접촉 모드가 바뀌는 보행·조작 계에서 이를 **설계 조건**으로 쓰는 방법은
  정립되지 않았다. `c2-contact-dynamics` 와 `s3-legged-underactuated` 에서 같은 벽을 만난다.
- **(열린 문제) 수축률과 입력 노력의 교환** — (7)은 $\lambda$ 를 키우면 관이 좁아진다고 말하지만,
  $\lambda$ 를 키우는 피드백은 입력을 키운다. 입력 한계 아래에서 달성 가능한 $(\lambda,$ 관
  반지름$)$ 쌍의 **파레토 경계**를 주는 이론이 없다. `c4-mpc` 의 관 MPC 가 같은 교환을 다른
  언어로 다룬다.

## 개념 점검

`rc quiz c3-contraction-incremental` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c3-contraction-incremental-quiz
questions:
  - id: q1
    type: single
    prompt: "(1)의 야코비안은 두 꼭짓점 모두 고윳값 실수부가 $-1$ 인데, 유클리드 계량에서 $\\lambda_{\\max}(J^\\top+J) \\ge 0$ 인 사실은 무엇을 뜻하는가?"
    choices:
      - "계가 불안정하다"
      - "거리가 일시적으로 늘어날 수 있다 — 수축은 계량과 함께 주장되는 성질이고, 계량을 바꾸면 인증할 수 있다"
      - "야코비안 계산이 틀렸다"
      - "수축 이론을 쓸 수 없다"
    answer: 1
    explanation: "고윳값은 점근 거동을, 대칭부는 **순간** 거동을 말한다. $J^\\top+J$ 에 양의 고윳값이 있으면 그 방향으로 거리가 순간적으로 늘어난다. 상수 계량 $M$ 을 바꾸면 (4)를 만족시킬 수 있고, (1)에서는 $\\lambda \\approx 0.49$ 까지 인증된다."
    concept: { front: "고윳값 vs 야코비안의 대칭부", back: "고윳값은 점근, 대칭부는 순간. 유클리드에서 거리가 늘어도 다른 계량에서는 수축일 수 있다" }
  - id: q2
    type: short
    prompt: "수축률 $\\lambda$ 와 교란 상한 $\\sup\\lVert\\Theta d\\rVert$ 가 주어졌을 때 점근 관(tube) 반지름은? (식으로)"
    answer: ["sup|Theta d|/lambda", "sup||Theta d||/lambda", "||Theta d||/lambda", "Theta d / lambda", "sup/lambda", "1/lambda * sup|Theta d|"]
    explanation: "(15)에 비교 보조정리를 적용하면 $R(t) \\le R(0)e^{-\\lambda t} + \\sup\\lVert\\Theta d\\rVert/\\lambda$ 다. 즉 수축률이 교란 이득의 역수이고, $\\lambda$ 를 2배로 하면 관이 절반이 된다."
    concept: { front: "수축 계의 교란 관 반지름", back: "$\\sup\\lVert\\Theta d\\rVert/\\lambda$ — 수축률이 곧 교란 이득의 역수" }
  - id: q3
    type: truefalse
    prompt: "어떤 영역에서 수축하는 시불변계는 그 영역에 평형점을 둘 이상 가질 수 있다."
    answer: false
    explanation: "평형점은 상수 궤적이므로 두 평형점 사이의 거리는 변하지 않는데, 수축은 그 거리가 $e^{-\\lambda t}$ 로 줄어든다고 말한다. 모순이므로 평형점은 최대 하나다. $\\dot x = x - x^3$ 처럼 평형점이 셋인 계는 전역적으로 수축하지 않는다."
    concept: { front: "수축과 평형점 개수", back: "수축하는 영역의 평형점은 최대 하나 — 다중 평형점 계는 전역 수축이 아니다" }
  - id: q4
    type: single
    prompt: "CCM 조건 (17)을 쌍대 계량 $W = M^{-1}$ 로 쓰면 볼록해지는 핵심 이유는?"
    choices:
      - "$W$ 가 $M$ 보다 작아서 수치적으로 안정하기 때문"
      - "조건 $\\delta x^\\top MB = 0$ 이 $W$ 좌표에서 $\\eta^\\top B = 0$ 으로 바뀌어 계량과 무관해지고, $B_\\perp$ 사영으로 입력의 존재가 소거되기 때문"
      - "$\\dot{W}$ 항이 사라지기 때문"
      - "입력 제약을 무시하기 때문"
    answer: 1
    explanation: "$\\delta x = W\\eta$ 로 치환하면 제약이 $\\eta^\\top B = 0$ 이 되어 $M$ 에 의존하지 않는다. 그래서 $B_\\perp$ 로 사영한 (8)은 $W$ 에 대해 선형(LMI)이다. $\\dot W$ 항은 사라지지 않고 부호가 바뀐다."
    concept: { front: "CCM 이 볼록한 이유", back: "$W=M^{-1}$ 에서 제약 $\\eta^\\top B=0$ 이 계량과 무관해지고 $B_\\perp$ 사영이 $u$ 의 존재를 소거한다" }
```

## 이 단계 공부법

1. **(10)을 세 번 쓴다 (30분)** — $\dot V = \delta x^\top(\dot M + J^\top M + MJ)\delta x$ 의
   전개를 손으로 세 번 쓴다. $\dot M$ 이 **전미분**이라는 점(상태 의존 계량에서 $\partial M/\partial x_i \dot x_i$
   항이 살아 있다)이 유일한 함정이다.
2. **유클리드가 실패하는 것을 먼저 본다 (30분)** — (3)을 직접 계산한다. 고윳값이 $-1$ 인데
   대칭부에 양의 고윳값이 있다는 사실을 보면, "계량을 찾는다" 가 왜 작업인지 납득된다.
3. **손으로 풀리는 계량 예로 감을 잡는다 (40분)** — (13)을 유도하고 $k=10$, $\lambda=0.5$ 에서
   $m\ge100$ 을 확인한다. P1 을 풀면 수렴률과 과도 응답의 교환이 식 하나에 들어 있는 것이 보인다.
4. **LMI 를 직접 돌린다 (90분)** — 재현 과제의 조건 1 을 먼저 통과시킨다. 이분법의 각 단계가
   SDP 라는 구조(λ 를 고정하면 선형)를 코드로 확인하는 것이 핵심이다.
5. **보수성을 숫자로 만난다 (60분)** — 조건 2·3 을 돌려 인증 $0.49$ 와 실측 $1.00$ 의 간극을
   직접 본다. **인증은 보수적이다** 를 숫자로 겪어야 다음 레슨(수동성)과 CBF 에서 같은 성질을
   기대할 수 있다.
6. **논문은 "버린 가정" 으로 읽는다 (150분)** — Lohmiller–Slotine 은 평형점을 버렸고,
   Manchester–Slotine 은 비볼록성을 $B_\perp$ 사영으로 버렸고, Tsukamoto 등은 그 두 줄기가
   학습으로 어떻게 이어지는지 정리한다. 논문당 1페이지 노트는 **반드시** 쓴다.
7. **다음 레슨으로의 다리 (20분)** — 수축은 궤적 사이의 수렴을 본다. 그런데 로봇이 **환경과
   접촉**하면 상대가 궤적이 아니라 에너지를 교환하는 또 다른 계다. 그 관점이
   `c3-passivity-impedance` 다.

**통과 기준**: 백지에서 (10)–(12)와 (16)을 유도할 수 있고, 유클리드 계량이 (1)에서 실패하는
이유를 수로 설명할 수 있고, 재현 과제의 네 조건을 만족하는 코드와 논문 3편의 노트가 있다.
