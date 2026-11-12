---
id: c2-dynamics-derivatives-sysid
title: 동역학의 미분과 관성 매개변수 식별
summary: >-
  역동역학이 관성 매개변수에 선형이라는 사실에서 회귀자 $\tau = Y\pi$ 를 세우고, 구조적으로
  식별 불가능한 부분공간과 기저 매개변수를 증명 수준에서 다룬다. 물리적 일관성이 유사 관성
  행렬의 LMI 라는 것과, 식별 불가능한 방향이 바로 일관성이 사는 자리라는 것을 수치로 분해하고,
  RNEA 의 해석적 미분이 왜 자동 미분보다 빠른지까지 간다.
objectives:
  - 공간 관성이 10개 매개변수에 선형임을 쓰고 회귀자 $Y$ 를 RNEA 호출로 구성할 수 있다.
  - 상태와 무관한 영공간의 존재를 증명하고 기저 매개변수의 개수가 포화하는 이유를 설명할 수 있다.
  - 유사 관성 행렬의 양정치성이 물리적 실현 가능성과 동치임을 쓰고 그것이 LMI 임을 보일 수 있다.
  - $\partial\tau/\partial\ddot{q} = M(q)$ 를 유도하고 해석적 미분이 자동 미분·유한차분보다 유리한 이유를 말할 수 있다.
  - 식별 오차가 잡음과 조건수에 어떻게 의존하는지 수치로 분해하고 여진 궤적 설계의 목표를 쓸 수 있다.
prerequisites: [c2-contact-dynamics]
difficulty: 5
estimated_minutes: 600
tags: [multibody-dynamics, system-identification, derivatives, lmi, sdp, conditioning, research]
activities:
  - id: c2-dynamics-derivatives-sysid-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 105
  - id: c2-dynamics-derivatives-sysid-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c2-dynamics-derivatives-sysid-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 2 · 계산 1 · 구현 1 · 논문 1)
    estimated_minutes: 180
  - id: c2-dynamics-derivatives-sysid-reproduction
    kind: reproduction
    title: 재현 과제 — 7-DOF 관성 매개변수 식별과 식별 가능성 분해 (R2)
    estimated_minutes: 150
  - id: c2-dynamics-derivatives-sysid-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Featherstone, Rigid Body Dynamics Algorithms (2008)"
    url: https://doi.org/10.1007/978-0-387-74315-8
    kind: book
    note: ch.10 (Accuracy and Efficiency). 관성 매개변수와 수치 정확도. 이 모듈을 닫는 장.
  - title: "Tedrake, Underactuated Robotics"
    url: https://underactuated.csail.mit.edu/
    kind: book
    note: ch.18 (System Identification). 선형 회귀 식별과 물리적 일관성의 현대적 서술. 전문 무료.
  - title: "Boyd & Vandenberghe, Convex Optimization"
    url: https://web.stanford.edu/~boyd/cvxbook/
    kind: book
    note: 권장. ch.4.6 (SDP)·App. A.5.5. LMI 제약과 SDP 의 배경. 전문 PDF 무료.
  - title: "Nocedal & Wright, Numerical Optimization"
    kind: book
    note: 권장. ch.10 (최소제곱)·ch.3. 조건수와 정규방정식 vs QR·SVD. (공식 URL 미확인)
papers:
  - id: atkeson1986-inertial-parameters
    role: seminal
    required: true
  - id: wensing2018-lmi-inertial
    role: standard
    required: true
  - id: carpentier2018-pinocchio
    role: standard
    required: true
  - id: gautier1990-minimal-inertial-parameters
    role: standard
---

# 동역학의 미분과 관성 매개변수 식별

## 전제와 기호

`c2-rnea-inverse-dynamics` 와 `c2-crba-aba` 의 결과를 전제한다. 특히 RNEA, CRBA,
$M = \sum_k J_k^\top I_kJ_k$, 그리고 공간 관성의 블록 구조(앞 모듈 레슨 1 의 (4)).
이 레슨은 모듈을 닫는다 — **모델을 어디서 얻는가**가 주제이고, 앞 다섯 레슨이 전부
"관성 매개변수가 주어졌을 때"를 다뤘다.

| 기호 | 뜻 |
|---|---|
| $\pi_i \in \mathbb{R}^{10}$ | 바디 $i$ 의 관성 매개변수 $(m,\; h^\top,\; I_{Oxx}, I_{Oxy}, I_{Oxz}, I_{Oyy}, I_{Oyz}, I_{Ozz})$ |
| $h := mc \in \mathbb{R}^3$ | 1차 질량 모멘트. $c$ 가 아니라 $h$ 를 쓰는 것이 **선형성의 핵심** |
| $I_O$ | **프레임 원점** 기준 회전 관성(질량중심 기준 $\bar I_C$ 가 아니다) |
| $\pi \in \mathbb{R}^{10n}$ | 전체 매개변수 벡터 $(\pi_1; \dots; \pi_n)$ |
| $Y(q,\dot q,\ddot q) \in \mathbb{R}^{n\times 10n}$ | 회귀자(regressor). $\tau = Y\pi$ |
| $\mathcal{N}$ | 구조적 식별 불가능 부분공간. $\mathcal{N} = \{\pi : Y(\cdot)\pi \equiv 0\}$ |
| $n_b := 10n - \dim\mathcal{N}$ | **기저 매개변수**(base parameters)의 개수 |
| $V_{\mathrm{id}}, V_{\mathrm{null}}$ | 식별 가능 부분공간과 $\mathcal{N}$ 의 정규직교 기저 |
| $P(\pi_i) \in \mathbb{R}^{4\times4}$ | **유사 관성**(pseudo-inertia) 행렬. $\pi_i$ 에 선형 |
| $\sigma$ | 토크 측정 잡음의 표준편차 |
| $\kappa$ | 식별 가능 부분공간에서의 조건수 $S_1/S_{n_b}$ |

전제와 범위: 기구 트리, 강체, 관절 마찰·유연성은 모델에 넣지 않는다(실제 로봇의 지배적
오차원이지만 매개변수가 다르고 선형성이 깨진다 — 열린 문제). 모든 수치는 numpy 만으로 얻고,
시뮬레이터는 쓰지 않는다. 궤적은 무작위 상태 샘플로 대체한다(실제 여진 궤적 설계는 R5).

**$c$ 가 아니라 $h = mc$ 를 쓰는 이유**를 먼저 적어 둔다. 공간 관성은 $(m, c, \bar I_C)$ 에
대해서는 **비선형**이다($m\hat c\hat c^\top$ 항이 $c$ 에 2차다). 반면 $(m, h, I_O)$ 에 대해서는
완전히 **선형**이다. 이 한 번의 재매개화가 식별 문제를 선형 최소제곱으로 만들고, 이 레슨 전체가
거기서 나온다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 — `lesson-standard.md` §2).

- **R1 (관성 매개변수에 대한 선형성) [D2]** — 공간 관성은
  $$
  I(\pi_i) = \begin{bmatrix} I_O & \hat h \\ \hat h^\top & m\,\mathbb{1}_3\end{bmatrix} \tag{1}
  $$
  로 $\pi_i$ 에 **선형**이고, RNEA 는 각 $I_i$ 에 선형이므로(힘 재귀가
  $f_i = I_ia_i + (v_i\times^{*})I_iv_i + \sum {}^iX_j^{*}f_j$ 로 $I$ 에 아핀이고 $I$ 항이 전부
  1차다) 결국
  $$
  \tau = Y(q,\dot q,\ddot q)\,\pi, \qquad Y \text{ 는 } \pi \text{ 와 무관}. \tag{2}
  $$
  $Y$ 의 $k$ 번째 열은 **$\pi = e_k$ 로 RNEA 를 한 번 부른 결과**다 — 이것이 가장 짧고
  검증 가능한 구성이다(비용 $10n$ 회의 RNEA = $\Theta(n^2)$).
- **R2 (구조적 식별 불가능성과 기저 매개변수) [D3]** —
  $$
  \mathcal{N} := \big\{\pi \;:\; Y(q,\dot q,\ddot q)\,\pi = 0 \ \ \forall (q,\dot q,\ddot q)\big\}
  $$
  은 **상태와 무관한 부분공간**이고, 토크 데이터만으로는 $\mathcal{N}$ 방향을 **영원히 구별할
  수 없다**. 쌓은 회귀자의 계수는 유한한 수의 일반적(generic) 샘플에서 $n_b = 10n - \dim\mathcal{N}$
  에 **포화**한다($Y$ 의 성분이 해석 함수이므로). 7-DOF 기준 팔에서 측정하면
  $$
  n_b = 43, \qquad \dim\mathcal{N} = 27 \quad (10n = 70),
  $$
  특이값이 $5.22$ 에서 $1.9\times10^{-14}$ 로 **12 자릿수 떨어진다**. 중력을 끄면
  $n_b = 39$ 로 줄어든다 — 4개 방향은 **중력만이 들추어낸다**.
- **R3 (물리적 일관성은 LMI 다) [D2]** — $\pi_i$ 가 **양의 질량 밀도로 실현 가능**한 것과
  유사 관성 행렬
  $$
  P(\pi_i) = \begin{bmatrix} \tfrac{1}{2}\operatorname{tr}(I_O)\,\mathbb{1}_3 - I_O & h \\ h^\top & m \end{bmatrix} \;\succ\; 0 \tag{3}
  $$
  이 동치다. $P$ 가 $\pi_i$ 에 **선형**이므로 (3)은 LMI 이고, 식별 문제는
  $\min_\pi \lVert A\pi - b\rVert^2$ s.t. $P(\pi_i) \succeq 0$ 의 **SDP** 가 된다.
  이 제약은 $I_O \succ 0$ 과 삼각부등식보다 **엄격히 강하다**.
- **R4 (해석적 미분) [D2 / 전체 재귀는 D1]** — $\tau$ 는 $\ddot q$ 에 아핀이므로
  $$
  \frac{\partial\tau}{\partial\ddot q} = M(q) \tag{4}
  $$
  가 **정확히** 성립한다(CRBA 가 곧 이 야코비안이다). $\partial\tau/\partial q$ 와
  $\partial\tau/\partial\dot q$ 도 같은 재귀에 $\partial v_i/\partial\cdot$,
  $\partial a_i/\partial\cdot$ 를 함께 흘려 **$\Theta(n^2)$** 에 얻을 수 있고, 자동 미분보다
  한 자릿수 빠르다 — 운동·힘 변환이 서로 다른 규칙을 갖기 때문에 자동 미분 그래프가 중복
  계산을 만드는 것이 이유다(앞 모듈 레슨 1 의 둘째 열린 문제). **[D1]**
- **R5 (잡음·조건수와 여진 궤적) [D2]** — 식별 가능 부분공간에서의 오차는 잡음에 **선형**이고
  조건수가 비례상수를 지배한다. 7-DOF 기준 팔(샘플 30개 = 방정식 210개, $\kappa = 25.39$)에서
  측정하면
  $$
  \lVert V_{\mathrm{id}}^\top(\hat\pi - \pi)\rVert = 9.92\times10^{-4},\ 9.92\times10^{-3},\ 9.92\times10^{-2}
  \quad (\sigma = 10^{-3},\ 10^{-2},\ 10^{-1}),
  $$
  즉 정확히 $\propto\sigma$ 다. 반면 $\mathcal{N}$ 방향의 오차는 $\sigma$ 와 **무관하게**
  $\lVert V_{\mathrm{null}}^\top\pi\rVert = 4.7586$ 로 고정된다 — 전혀 복원되지 않는다.
  그런데도 **토크 예측은 멀쩡하다**($\sigma = 10^{-3}$ 에서 새 상태의 예측 오차 $1.98\times10^{-3}$).
  여진 궤적 설계의 목표는 $\kappa$ 를 줄이는 것이고, $\dim\mathcal{N}$ 은 궤적으로 바꿀 수 **없다**.

## 유도

### R1 — 선형성과 회귀자의 구성

앞 모듈 레슨 1 에서 공간 관성을 $(m, c, \bar I_C)$ 로 썼다:
$I = \begin{bmatrix}\bar I_C + m\hat c\hat c^\top & m\hat c \\ m\hat c^\top & m\mathbb{1}\end{bmatrix}$.
여기서 좌상 블록의 $m\hat c\hat c^\top$ 이 $c$ 에 **2차**다. 그런데 평행축 정리로
$I_O = \bar I_C + m\hat c\hat c^\top$ 이 **원점 기준 관성**이고, $h = mc$ 로 두면
$m\hat c = \hat h$ 다. 두 재매개화를 넣으면 (1)이 되고 **모든 성분이 $\pi_i$ 의 1차식**이다.
$I_O$ 는 대칭이므로 독립 성분이 6개, $h$ 가 3개, $m$ 이 1개 — 합이 10 이다.

이제 RNEA 가 $\pi$ 에 선형임을 본다. 전진 패스($v_i$, $a_i$)는 $\pi$ 에 **전혀 의존하지
않는다** — 순수 운동학이다. 후진 패스는

$$
f_i = \underbrace{I_i a_i}_{\pi_i \text{ 1차}} + \underbrace{(v_i\times^{*})I_i v_i}_{\pi_i \text{ 1차}}
  + \sum_{j\in\mu(i)}{}^iX_j^{*}f_j, \qquad \tau_i = S_i^\top f_i,
$$

이고 $I_i$ 가 $\pi_i$ 에 선형이므로 두 항 모두 $\pi_i$ 의 1차식이다. 재귀의 합도 선형이고
$S_i^\top$ 투영도 선형이므로 $\tau$ 전체가 $\pi$ 에 선형이다 — 즉 (2)다. 중력은
$a_0 = -a_g$ 로 들어가고 그것도 전진 패스이므로 선형성을 깨지 않는다
(**중력 항도 $Y\pi$ 안에 있다** — 문제 P1 ⓑ).

**회귀자의 구성.** (2)가 선형이므로 열을 하나씩 뽑으면 된다: $\pi = e_k$ (즉 $k$ 번째
매개변수만 1, 나머지 0)로 RNEA 를 부르면 그 결과가 $Y_{\cdot k}$ 다. 비용은 RNEA $10n$ 회
= $\Theta(n^2)$ 이고, 구현이 **세 줄**이다(아래 핵심 코드). 손으로 $Y$ 의 성분식을 전개하는
문헌의 방식보다 훨씬 짧고, 무엇보다 **앞 레슨의 RNEA 를 그대로 재사용해 검증된다**:
$\lVert Y\pi - \tau\rVert$ 가 기계 정밀도여야 한다(측정 $7.1\times10^{-15}$).

$\pi = e_k$ 로 만든 "바디"는 질량이 0 이거나 관성이 음수여서 **물리적이지 않다**. 그래도
무관하다 — 선형 사상의 열을 뽑는 계산일 뿐이고 RNEA 는 물리적 타당성을 요구하지 않는다.
(다만 ABA 는 $d_i > 0$ 을 요구하므로 같은 트릭을 쓸 수 없다 — 앞 레슨 R5.)

### R3 — 유사 관성과 물리적 일관성

$\pi_i$ 가 **어떤 양의 질량 밀도** $\rho(r) \ge 0$ 에서 나왔다고 하자. 그러면

$$
m = \int \rho\,dV, \quad h = \int \rho\,r\,dV, \quad
I_O = \int \rho\,\big(\lVert r\rVert^2\mathbb{1} - rr^\top\big)dV.
$$

여기서 **2차 모멘트 행렬** $\Sigma := \int\rho\,rr^\top dV$ 를 꺼낸다.
$\operatorname{tr}(I_O) = \int\rho(3\lVert r\rVert^2 - \lVert r\rVert^2) = 2\int\rho\lVert r\rVert^2
= 2\operatorname{tr}\Sigma$ 이므로

$$
\Sigma = \operatorname{tr}(\Sigma)\mathbb{1} - I_O = \tfrac{1}{2}\operatorname{tr}(I_O)\,\mathbb{1} - I_O,
$$

즉 (3)의 좌상 블록이다. 그러면

$$
P(\pi_i) = \int \rho(r)\begin{bmatrix} rr^\top & r \\ r^\top & 1\end{bmatrix}dV
= \int \rho(r)\begin{bmatrix} r \\ 1\end{bmatrix}\begin{bmatrix} r \\ 1\end{bmatrix}^\top dV
$$

이고, 피적분함수가 **랭크 1 양반정치**이며 $\rho \ge 0$ 이므로 $P \succeq 0$ 이다. 질량이
한 평면에 몰려 있지 않으면(점 4개가 아핀 생성) $P \succ 0$ 이다. 역방향(즉 $P \succeq 0$ 이면
실현 가능한 밀도가 존재한다)은 $P$ 를 고윳값 분해해 **점질량 4개**로 실현하면 되고, 그래서
(3)은 **동치**다. (생략: 역방향의 상세는 Wensing et al. 2018 의 실현 가능성 정리.)

**왜 이것이 삼각부등식보다 강한가.** $I_O \succ 0$ 과 주모멘트의 삼각부등식
($I_1 + I_2 \ge I_3$)은 (3)의 **필요조건**이다. $P \succeq 0$ 은 $h$ 와 $m$ 까지 함께 묶으므로
"질량중심이 물체 안에 있어야 한다"는 종류의 조건까지 포함한다. 실무에서 흔한 생성기가
어떻게 틀리는지가 좋은 예다(문제 P2 ⓐ, 그리고 이 모듈이 실제로 겪은 일 — 재현 과제 주석).

**이것이 LMI 라는 뜻.** $P(\pi_i)$ 는 $\pi_i$ 에 **선형**이므로 $\{\pi_i : P(\pi_i)\succeq0\}$ 은
볼록 집합(대칭 PSD 원뿔의 선형 역상)이다. 따라서

$$
\min_\pi \; \lVert A\pi - b\rVert_2^2 \quad \text{s.t.} \quad P(\pi_i) \succeq 0 \ \ (i = 1,\dots,n) \tag{5}
$$

는 **볼록** 문제이고, 구체적으로 SDP 다. 비볼록 매개화($m, c, \bar I_C$)를 쓰면 같은 제약이
비볼록이 되므로, R1 의 재매개화가 **두 번** 값을 한다 — 선형 회귀와 볼록 제약 양쪽에서.

### R4 — $\partial\tau/\partial\ddot q = M$

앞 레슨들에서 $\tau = M(q)\ddot q + b(q,\dot q)$ 이고 $b$ 는 $\ddot q$ 와 무관하다. 따라서
$\ddot q$ 에 대한 야코비안은 $M(q)$ 다 — (4)다. 이것은 **정확한 등식**이고 근사가 아니다.
세 가지가 따라온다:

1. **$M$ 을 두 번 계산하지 않는다.** 궤적 최적화가 $\partial\tau/\partial\ddot q$ 를 요구하면
   CRBA 를 부르면 되고, 역으로 $M$ 이 필요하면 RNEA 를 $n$ 번 부를 수도 있다
   (앞 레슨 R4-5). 둘은 같은 양이다.
2. **아핀성 테스트가 무료다.** $\tau(\ddot q_1 + \ddot q_2) - \tau(0) =
   [\tau(\ddot q_1) - \tau(0)] + [\tau(\ddot q_2) - \tau(0)]$ 가 기계 정밀도로 성립해야 한다
   (앞 레슨에서 측정 $2.1\times10^{-14}$).
3. **유한차분의 함정.** 중력을 끄고 $\dot q = 0$ 이면 $\tau = M\ddot q$ 가 **정확히 선형**이라
   중앙 유한차분의 절단 오차가 0 이고 모든 $h$ 에서 기계 정밀도가 나온다(측정 $4.4\times10^{-16}$).
   중력을 **켜면** 상쇄 오차가 지배해 $1/h$ 로 커진다. 앞 레슨 조건 2 가 중력 0 을 명시하는
   이유다.

$\partial\tau/\partial q$ 와 $\partial\tau/\partial\dot q$ 는 (4)처럼 공짜가 아니다. 해석적
미분의 전략은 RNEA 의 재귀를 **그대로 한 번 더** 흘리는 것이다: $\partial v_i/\partial q_k$ 와
$\partial a_i/\partial q_k$ 를 (앞 레슨 (1)(3)을 미분해 얻은) 재귀로 전파하고, 그것을 힘 재귀에
넣어 $\partial\tau/\partial q_k$ 를 얻는다. 각 $k$ 마다 바디당 상수 작업이므로 총
$\Theta(n^2)$ 이다 — 유한차분($n$ 번의 RNEA = $\Theta(n^2)$)과 **차수는 같지만** 상수가 작고
무엇보다 **절단 오차가 없다**. 자동 미분이 더 느린 이유는 $X$ 와 $X^{*}$ 가 서로 다른 변환
규칙을 갖기 때문에 그래프가 중복 계산을 만드는 것이고, Carpentier & Mansard 2018 이 그
차이를 측정한다. **[D1]** (이 레슨은 (4)만 [D2] 로 완결하고, 전체 재귀의 유도는 그 논문으로 넘긴다.)

### R5 — 잡음, 조건수, 그리고 무엇을 바꿀 수 있는가

쌓은 회귀자 $A \in \mathbb{R}^{mn\times 10n}$ 와 측정 $b = A\pi + \varepsilon$,
$\varepsilon \sim \mathcal{N}(0, \sigma^2)$ 를 두고 **식별 가능 부분공간에서만** 최소제곱을 푼다:
$\hat\beta = \arg\min\lVert AV_{\mathrm{id}}\beta - b\rVert$, $\hat\pi = V_{\mathrm{id}}\hat\beta$.
정규방정식에서

$$
V_{\mathrm{id}}^\top(\hat\pi - \pi) = \big((AV_{\mathrm{id}})^\top AV_{\mathrm{id}}\big)^{-1}(AV_{\mathrm{id}})^\top\varepsilon
$$

이므로 오차의 크기는 $\sigma$ 에 **선형**이고 비례상수는 $AV_{\mathrm{id}}$ 의 특이값이
결정한다 — 가장 작은 특이값 방향이 가장 크게 증폭된다. 측정이 이것을 그대로 보여 준다
(7-DOF, 샘플 30개, $\kappa = 25.39$):

| $\sigma$ | $\lVert V_{\mathrm{id}}^\top(\hat\pi - \pi)\rVert$ | $\lVert V_{\mathrm{null}}^\top(\hat\pi - \pi)\rVert$ | 새 상태의 토크 예측 오차 |
|---|---|---|---|
| $0$ | $3.2\times10^{-13}$ | $4.7586$ | $1.1\times10^{-13}$ |
| $10^{-3}$ | $9.92\times10^{-4}$ | $4.7586$ | $1.98\times10^{-3}$ |
| $10^{-2}$ | $9.92\times10^{-3}$ | $4.7586$ | $1.98\times10^{-2}$ |
| $10^{-1}$ | $9.92\times10^{-2}$ | $4.7586$ | $1.98\times10^{-1}$ |

세 열을 각각 읽는 법:

- 첫 열은 $\propto\sigma$ — 잡음을 줄이거나 샘플을 늘리거나 $\kappa$ 를 줄이면 개선된다.
  **여진 궤적 설계**가 하는 일이 셋째다.
- 둘째 열은 $\sigma$ 와 무관하게 **상수**다. $\mathcal{N}$ 방향은 데이터가 아무리 많고
  깨끗해도 복원되지 않는다. 궤적으로 바꿀 수 있는 양이 **아니다** — 기구 구조가 정한다.
- 셋째 열은 둘째 열이 **예측에는 해롭지 않다**는 것을 보여 준다. 기저 매개변수만으로
  토크 예측은 완전하다. $\mathcal{N}$ 이 문제가 되는 것은 **물리적 해석**(이 링크의 질량이
  얼마인가)과 **물리적 일관성 제약**을 걸 때다.

**$\mathcal{N}$ 과 물리적 일관성의 관계 — 이 레슨의 가장 중요한 수치.** 잡음이 **0** 일 때도
식별 가능 부분공간의 최소노름 해는 물리적으로 비일관이다($\min_i\lambda_{\min}(P) = -1.1274$).
그런데 $\mathcal{N}$ 방향 성분을 참값으로 되돌리면 일관해진다($+9.32\times10^{-4}$), 그리고
**토크 예측은 전혀 바뀌지 않는다**($1.2\times10^{-12}$). 즉 $\sigma = 0$ 에서 물리적 일관성은
**전부 식별 불가능한 방향에 들어 있다** — (5)의 SDP 가 고르는 것이 바로 그 방향이다.
$\sigma$ 가 커지면($10^{-2}$) 식별 가능 성분 자체가 일관 집합 밖으로 밀려나
$\mathcal{N}$ 방향만으로는 복구되지 않고($-1.6\times10^{-3}$), 그때 LMI 제약은
**식별 가능 방향에도 작용**한다(= 추정값을 바꾼다). 이 세 체제가 재현 과제 조건 3 이다.

## 증명 스케치

### R2 — 영공간은 상태와 무관하고 계수는 포화한다

**가설** H1: 기구 트리, 강체, $S_i$ 는 바디 좌표에서 상수. H2: 측정은 관절 토크 $\tau$ 뿐이다
(베이스 반력이나 외력은 측정하지 않는다). H3: $Y$ 의 성분은 $(q,\dot q,\ddot q)$ 의
해석(analytic) 함수다.
**결론** C1: $\mathcal{N}$ 은 $\mathbb{R}^{10n}$ 의 부분공간이고 상태에 의존하지 않는다.
C2: 두 매개변수 벡터가 토크 데이터로 구별 불가능한 것과 차가 $\mathcal{N}$ 에 있는 것이 동치다.
C3: 일반적 샘플을 유한 개 쌓으면 계수가 $n_b = 10n - \dim\mathcal{N}$ 에 **확률 1 로** 도달한다.
C4: 가설을 지우면 무엇이 달라지는가.

**전략**: 선형성(R1)으로 구별 불가능성을 영공간 소속으로 환원하고, 해석성으로 "일반적 샘플이
최대 계수를 준다"를 얻는다. 둘째 단계가 이 증명의 유일한 비자명 부분이다.

1. **C1.** $\mathcal{N} = \bigcap_{(q,\dot q,\ddot q)} \ker Y(q,\dot q,\ddot q)$ 는 부분공간의
   교집합이므로 부분공간이다. 정의 자체가 모든 상태에 대한 교집합이므로 상태에 의존하지 않는다.
2. **C2.** (2)에서 $\tau$ 는 $\pi$ 를 **$Y\pi$ 를 통해서만** 본다. 따라서 $\pi$ 와 $\pi'$ 가
   모든 상태에서 같은 토크를 주는 것은 $Y(\pi - \pi') = 0$ 이 모든 상태에서 성립하는 것,
   즉 $\pi - \pi' \in \mathcal{N}$ 과 동치다. (H2 가 쓰이는 지점 — 베이스 반력을 측정하면
   $\mathcal{N}$ 이 줄어든다.)
3. **계수의 단조성과 상한.** 샘플을 쌓은 $A_m$ 의 행공간은 $m$ 에 대해 단조 증가하고
   $\mathcal{N}^\perp$ 에 포함된다. 따라서 $\mathrm{rank}\,A_m \le n_b$ 이고 어떤 $m^{*}$ 에서
   더 늘지 않는다(유한 차원).
4. **포화 (C3).** $\mathrm{rank}\,A_m = n_b$ 와 동치인 것은 어떤 $n_b \times n_b$ 소행렬식이
   0 이 아니라는 것이다. 그 소행렬식은 H3 에 의해 샘플들의 해석 함수이고, 정의상 **항등적으로
   0 은 아니다**($n_b$ 의 정의가 그렇다). 항등적으로 0 이 아닌 해석 함수의 영집합은 측도 0
   이므로, 연속 분포에서 뽑은 일반적 샘플에 대해 확률 1 로 $\mathrm{rank}\,A_m = n_b$ 다.
   (**이 단계가 "무작위 샘플로 $n_b$ 를 세어도 된다"를 정당화한다** — 재현 과제 조건 2 가
   하는 일이 정확히 이것이고, 측정된 특이값 간극 $5.22 \to 1.9\times10^{-14}$ 가 그 증거다.)
5. **$\mathcal{N}$ 은 어디서 오는가(구조).** 세 가지 전형이 있다.
   ⓐ 첫 바디는 고정 축 $S_1$ 하나로만 움직이므로 $I_1$ 의 성분 중 그 축에 걸리는 조합만
   토크에 나타나고, 나머지는 **베이스 반력으로 흘러** 보이지 않는다. ⓑ 평행·교차하는 관절
   축은 두 바디의 매개변수 조합을 같은 방식으로 토크에 넣어 차이를 지운다. ⓒ 중력이 없으면
   질량과 1차 모멘트가 **정적으로** 드러날 길이 사라진다. Gautier & Khalil 1990 이 ⓐⓑ 를
   기구에서 구성적으로 소거해 최소 기저를 만든다.
6. **C4 — 가설을 지우면.** H2 에서 측정을 늘리면(베이스 6축 힘/토크 센서, 또는 링크에 IMU)
   $\mathcal{N}$ 이 줄어든다 — 식별 가능성은 **기구만의 성질이 아니라 기구 + 측정의 성질**이다.
   중력을 끄면(궤도상 로봇) 거꾸로 $\mathcal{N}$ 이 커진다: 측정에서 $n_b$ 가 $43 \to 39$ 로
   줄어든다. H1 에서 강체를 빼면 (2)의 선형성 자체가 깨지고 문제가 비선형 회귀가 된다.
   H3(해석성)을 빼면 4단계가 무효가 되어 "무작위 샘플로 계수를 세는" 절차의 정당성이 사라진다.

### R3 — (3)의 양방향 중 "필요"쪽

**가설** H1: $\pi_i$ 가 양의 유한 질량 밀도 $\rho \ge 0$ (콤팩트 지지)에서 나왔다.
**결론** C: $P(\pi_i) \succeq 0$, 그리고 질량이 평면에 몰려 있지 않으면 $\succ 0$.

**전략**: $P$ 를 랭크 1 양반정치 행렬의 가중 적분으로 쓴다. 한 줄이다.

1. **2차 모멘트로 바꾼다.** 본문 유도에서
   $\Sigma = \tfrac12\operatorname{tr}(I_O)\mathbb{1} - I_O = \int\rho\,rr^\top dV$.
2. **랭크 1 적분.** $\tilde r := (r; 1) \in \mathbb{R}^4$ 로 두면
   $P(\pi_i) = \int\rho(r)\,\tilde r\tilde r^\top dV$.
3. **부호.** 임의 $x \in \mathbb{R}^4$ 에 대해
   $x^\top Px = \int\rho\,(\tilde r^\top x)^2 dV \ge 0$ — $\rho \ge 0$ 이므로. C 의 전반부.
4. **양정치.** $x^\top Px = 0$ 이면 지지 집합의 거의 모든 $r$ 에서 $\tilde r^\top x = 0$,
   즉 질량이 아핀 초평면 $\{r : x_{1:3}^\top r + x_4 = 0\}$ 에 몰려 있다. 그렇지 않으면
   $P \succ 0$.
5. **역방향은 구성적이다.** $P \succeq 0$ 이면 $P = \sum_{j} \mu_j u_ju_j^\top$ 로 분해하고
   각 $u_j$ 를 (스케일을 맞춰) 점질량으로 읽으면 같은 $\pi_i$ 를 주는 밀도가 만들어진다.
   생략: 4번째 좌표를 1 로 정규화하는 세부와 경계 경우는 Wensing et al. 2018.

**가설을 지우면**: $\rho \ge 0$ 을 빼면(음의 질량 허용) 3단계가 깨지고 (3)은 제약이 되지 못한다.
콤팩트 지지를 빼면 적분이 발산할 수 있다. 그리고 **$P \succeq 0$ 과 $P \succ 0$ 의 차이**는
실무에서 중요하다 — 얇은 판이나 선형 링크는 경계($\det P = 0$)에 있고, SDP 를 엄격 부등식으로
쓰면 그런 물체를 배제한다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** ⓐ (1)이 $(m, c, \bar I_C)$ 파라미터화에서 왜 비선형이고 $(m, h, I_O)$
에서 왜 선형인지, 두 표현을 명시적으로 써서 보이라. ⓑ 중력 토크 $g(q)$ 가 $Y(q,0,0)\pi$ 로
표현됨을 보이고, 그 열 중 **$I_O$ 성분에 해당하는 열이 전부 0** 인지 확인하라(왜 그런가?).
ⓒ $Y$ 를 $\pi = e_k$ RNEA 호출로 만드는 비용을 세고, 손으로 성분식을 전개하는 방식과 비교하라.
*해답 스케치*: ⓑ 는 $\dot q = \ddot q = 0$ 이면 모든 $v_i = 0$ 이고 $a_i = {}^iX_0(-a_g)$ 이므로
$f_i = I_ia_i$ 다. $a_i$ 의 각 성분이 0 이고 선형 성분만 남으므로 $I$ 의 **우측 블록**
($\hat h$, $m\mathbb{1}$)만 곱해진다 — $I_O$ 열이 0 이다. 즉 **정적 실험만으로는 회전 관성을
전혀 식별할 수 없다**.

**P2 (유도, ★★, R3)** ⓐ $I_O \succ 0$ 과 주모멘트 삼각부등식을 만족하지만 $P \not\succeq 0$ 인
구체적 $\pi_i$ 를 만들라(힌트: $h$ 를 크게). ⓑ 거꾸로 $P \succ 0$ 이면 삼각부등식이 따라옴을
보이라. ⓒ 균일 밀도 직육면체와 **얇은 원판**의 $P$ 를 각각 계산하고, 원판이 경계에 있는지
확인하라.
*해답 스케치*: ⓑ 는 $\Sigma = \tfrac12\operatorname{tr}(I_O)\mathbb{1} - I_O \succeq 0$ 이
주모멘트로 $\tfrac12(I_1+I_2+I_3) - I_k \ge 0$, 즉 삼각부등식과 동치임을 쓴다 —
$P$ 의 좌상 블록이 PSD 인 것이 **정확히** 삼각부등식이고, $h$·$m$ 블록이 추가 조건이다.
ⓒ 의 얇은 원판은 $\Sigma$ 의 한 고윳값이 0 이라 $\det P = 0$ 이다.

**P3 (증명, ★★★, R2)** ⓐ 증명 스케치 4단계의 해석성 논증을 엄밀하게 쓰라(항등적으로 0 이 아닌
해석 함수의 영집합이 측도 0 임을 어디서 쓰는지 명시). ⓑ 1자유도 진자에서 $\mathcal{N}$ 을
**손으로** 전부 구하고 $n_b$ 를 세라(10개 중 몇 개인가?). ⓒ 2자유도 평면 팔로 확장해
$n_b$ 를 구하고, 측정한 7-DOF 값 $43$ 과의 경향을 비교하라.
*전략 + 핵심 부등식*: ⓑ 는 $\tau = (I_{Ozz})\ddot\theta + (\text{중력})$ 꼴이 되므로
$I_{Ozz}$ 와 중력에 들어가는 $h$ 의 두 성분만 보인다 — $n_b = 3$ 이고 $\dim\mathcal{N} = 7$ 이다.
축에 수직인 $h_z$ 와 $I_O$ 의 나머지 5성분, 그리고 $m$ 이 보이지 않는 이유를 각각 쓰라.
전개는 숨긴다.

**P4 (증명, ★★★, R3·R5)** ⓐ (5)가 볼록임을 증명하라(목적함수와 제약을 각각).
ⓑ $\sigma = 0$ 에서 "물리적 일관성이 전부 $\mathcal{N}$ 에 들어 있다"는 본문의 측정 결과를
일반 명제로 다듬어 보라 — 어떤 조건에서 참인가? 반례가 있는가?
ⓒ $\mathcal{N}$ 위에서 일관성을 만족시키는 점이 존재하지 않는 데이터($\sigma$ 가 큰 경우)에서
(5)의 해가 참값과 어떻게 다른지 논하라 — 편향(bias)이 생기는가?
*전략 + 핵심 부등식*: ⓑ 는 함정이다. 본문의 측정은 **참값이 일관**하므로
$\hat\pi + V_{\mathrm{null}}V_{\mathrm{null}}^\top\pi = \pi$ 가 되어 자동으로 성립한다.
일반 명제로는 "일관 집합과 $\hat\pi + \mathcal{N}$ 의 교집합이 비지 않는다"가 되고,
$\sigma = 0$ 에서 참값이 그 교집합에 있으므로 참이다. ⓒ 는 제약이 활성이 되어
**편향된** 추정이 되고, 그 편향이 모델 오차보다 작기를 기대하는 것이 실무의 선택이다.

**P5 (계산, ★, R1·R2·R5)** 7-DOF 기준 팔(아래 핵심 코드의 `arm7`)에서 ⓐ $\lVert Y\pi - \tau\rVert_\infty$
ⓑ 무작위 상태 40개를 쌓은 회귀자의 계수 $n_b$ 와 특이값 간극 ⓒ 식별 가능 부분공간의 조건수
$\kappa$ ⓓ $\lVert V_{\mathrm{null}}^\top\pi\rVert$ 를 구하라.
*정답* (시드 고정, 허용오차 아래 명시):
ⓐ $7.1\times10^{-15}$ (요구: $< 10^{-12}$)
ⓑ $n_b = 43$, $\dim\mathcal{N} = 27$, $S_{43} = 5.220283$, $S_{44} = 1.894\times10^{-14}$
   (요구: $n_b$ 가 정확히 43, 간극이 $10^{10}$ 배 이상)
ⓒ $\kappa = S_1/S_{43} = 25.3866$ (허용오차 $10^{-3}$; $S_1 = 132.525$)
ⓓ $\lVert V_{\mathrm{null}}^\top\pi\rVert = 4.7586$ (허용오차 $10^{-3}$)
*검산*: ⓔ $\max\lVert A V_{\mathrm{null}}\rVert_\infty < 10^{-12}$ (측정 $4.7\times10^{-13}$)
ⓕ 중력을 끄고 같은 계산을 하면 $n_b = 39$ 로 줄어든다
ⓖ $\partial\tau/\partial\ddot q$ 를 중력 0·$\dot q = 0$ 에서 유한차분하면 CRBA 의 $M$ 과
$4.4\times10^{-16}$ 이내로 일치한다.

**P6 (구현, ★★, R1·R3·R5)** ⓐ `params_of(m, c, Ic)` 와 `spatial_inertia_of(p)` 를 쓰고 왕복이
정확함을 확인하라. ⓑ `regressor(q, qd, qdd)` 를 $\pi = e_k$ RNEA 로 쓰라.
ⓒ `pseudo(p)` 와 물리적 일관성 검사를 쓰라. ⓓ 식별 가능 부분공간에서만 푸는 `identify` 를 쓰라.
*루브릭*: ⓐ `spatial_inertia_of(params_of(m, c, Ic))` 가 `mcI(m, c, Ic)` 와 $10^{-15}$ 이내
일치(측정 $4.3\times10^{-19}$) ⓑ P5 ⓐ 를 통과 ⓒ 점질량 8개에서 만든 바디가 **전부 PD** 이고
(측정 최소 $9.3\times10^{-4}$) 레슨 2·3 의 구 생성기($0.02AA^\top + 0.05\mathbb{1}$)가
**실패**함을 보인다 ⓓ $\sigma$ 를 바꿔 R5 의 표를 재현 ⓔ $Y$ 를 만들 때 쓰는 "비물리적
단위 바디"가 ABA 에서는 쓸 수 없는 이유를 docstring 에 적는다.

**P7 (논문, ★★, R2·R3·R4)** ⓐ Atkeson et al. 1986 이 쓰는 식별 가능성 논의를 이 레슨의
$\mathcal{N}$ 으로 번역하고, 저자들이 **물리적 일관성**을 다루는가를 확인하라.
ⓑ Wensing et al. 2018 의 LMI 와 이 레슨 (3)을 대조하고, 저자들이 "통계적 관점"으로
무엇을 추가하는지 쓰라. ⓒ Carpentier & Mansard 2018 이 보고하는 해석적 미분의 속도 이득이
어떤 기준선(자동 미분? 유한차분?)에 대한 것이고, 그 기준선이 공정한지 논하라.
*루브릭*: ⓐ 에서 1986년 논문이 식별 가능성을 **경험적**(조건수)으로 다루고 구조적 영공간을
구성적으로 다루지는 않는다는 점을 짚으면 통과(그것은 Gautier–Khalil 1990 의 기여다).
ⓒ 에서 기준선의 구현 품질·언어·벡터화 수준 중 하나 이상을 문제 삼으면 통과.
"논문이 자기 구현을 비교했으니 편향되었다"만 쓰면 미달.

## 논문 읽기

**필독 3편** (권장 1편). 1986·1990·2018·2018 — **식별**(선형 회귀), **최소 매개변수**(구조),
**일관성**(볼록 제약), **미분**(계산) 네 축이다. 네 편을 읽고 "모델을 얻는 문제가 1986년부터
무엇이 해결되고 무엇이 남았는가"를 한 단락으로 정리하는 것이 이 레슨의 읽기 목표다. 각 논문에
아래 고정 질문 10개로 1페이지 노트를 쓴다(`lesson-standard.md` §5). 3-pass 로 읽고 3번째
패스에서 질문 4·5·7 을 집중 공략한다.

1. **Atkeson, An & Hollerbach, "Estimation of Inertial Parameters of Manipulator Loads and
   Links" (1986, IJRR)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1177/027836498600500306>
   어느 절을 왜 읽는가: 동역학을 관성 매개변수에 선형인 회귀로 세우고 최소제곱으로 푸는 절
   전체. 이 레슨 R1 이 그 아이디어이고, 저자들의 실험 설계(어떤 궤적, 어떤 측정)가
   R5 의 조건수 논의와 직접 이어진다.
   추가 질문: ⓐ 저자들이 식별 가능성을 어떻게 다루는가 — 구조적인가, 경험적인가?
   ⓑ 물리적 일관성을 언급하는가? 언급하지 않는다면 그 결과로 어떤 추정값이 나올 수 있는가?
   ⓒ 저자들의 측정 집합(토크만? 손목 힘센서?)이 $\mathcal{N}$ 에 어떤 영향을 주는가?
2. **Wensing, Kim & Slotine, "Linear Matrix Inequalities for Physically Consistent Inertial
   Parameter Identification: A Statistical Perspective on the Mass Distribution" (2018, RA-L)** —
   역할: `표준(standard)`. <https://doi.org/10.1109/LRA.2017.2729659>
   어느 절을 왜 읽는가: 유사 관성의 LMI 를 세우고 실현 가능성과 동치임을 보이는 절.
   이 레슨 R3 와 1:1 대응하고, 제목의 "통계적 관점"이 무엇을 더하는지가 읽기의 초점이다.
   추가 질문: ⓐ 저자들의 동치 정리가 요구하는 가정을 이 레슨 R3 증명 스케치의 H1 과 대조하라.
   ⓑ "통계적 관점"에서 질량 분포를 확률 분포로 읽으면 무엇이 자연스러워지는가?
   ⓒ LMI 제약을 켠 추정과 끈 추정의 차이를 저자들이 어떻게 보여 주는가 — 그 지표가 공정한가?
3. **Carpentier & Mansard, "Analytical derivatives of rigid body dynamics algorithms"
   (2018, RSS)** — 역할: `표준(standard)`.
   <https://doi.org/10.15607/RSS.2018.XIV.038>
   어느 절을 왜 읽는가: RNEA·ABA 의 미분을 재귀로 유도하는 절과 비용을 비교하는 절.
   이 레슨 R4 가 (4)만 완결하고 넘긴 부분이 여기 있다.
   추가 질문: ⓐ 저자들의 미분 재귀가 원래 알고리즘과 **같은 차수**인가, 상수만 다른가?
   ⓑ 자동 미분이 느린 이유를 저자들이 어떻게 설명하는가 — 앞 모듈 레슨 1 의 둘째 열린 문제와
   같은 설명인가? ⓒ 접촉이 있는 동역학의 미분은 이 논문의 범위에 드는가?

**권장 1편** (필독 아님): **Gautier & Khalil, "Direct calculation of minimum set of inertial
parameters of serial robots" (1990, IEEE T-RA)** <https://doi.org/10.1109/70.56655> —
$\mathcal{N}$ 을 기구에서 **구성적으로** 소거해 최소 기저를 만드는 방법. R2 의 5단계가
이 논문의 요약이고, 수치 계수 계산(이 레슨의 방식)과 기호적 소거(이 논문의 방식)의 대비가 볼만하다.

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, 5분 이내, numpy 만(SDP 는 선택).
메모리 500MB 이내.

**핵심 코드 — 재매개화·회귀자·일관성 검사.** 아래는 본문의 모든 수치가 나온 코드의 핵심부다.
앞 레슨들의 `rnea`·`crba`·`mcI`·`skew`·`Model` 을 그대로 쓴다.

```python
def params_of(m, c, Ic):
    """The 10 inertial parameters: m, h = m c, and I about the FRAME ORIGIN (upper triangle)."""
    c = np.asarray(c, float)
    C = skew(c)
    Io = Ic + m * C @ C.T  # parallel axis: origin inertia from the com inertia
    return np.array([m, *(m * c), Io[0, 0], Io[0, 1], Io[0, 2], Io[1, 1], Io[1, 2], Io[2, 2]])


def spatial_inertia_of(p):
    """Spatial inertia (1), linear in the 10 parameters p. Inverse of params_of."""
    Io = np.array([[p[4], p[5], p[6]], [p[5], p[7], p[8]], [p[6], p[8], p[9]]])
    H = skew(p[1:4])
    return np.block([[Io, H], [H.T, p[0] * np.eye(3)]])


def unit_models(model):
    """One model per parameter, with pi = e_k. These bodies are NOT physical (zero or negative
    mass), which is fine for RNEA but would break ABA, where d_i > 0 is required."""
    out = []
    for k in range(10 * model.n):
        e = np.zeros(10 * model.n)
        e[k] = 1.0
        m = Model(model.parent, model.jtype, model.Xtree, model.mass_props)
        m.I = [spatial_inertia_of(e[10 * i : 10 * i + 10]) for i in range(model.n)]
        out.append(m)
    return out


def regressor(unit, q, qd, qdd):
    """Y with tau = Y pi, one RNEA call per column (R1)."""
    return np.column_stack([rnea(u, q, qd, qdd) for u in unit])


def pseudo(p):
    """The pseudo-inertia (3). Linear in p, so {p : pseudo(p) >= 0} is an LMI."""
    Io = np.array([[p[4], p[5], p[6]], [p[5], p[7], p[8]], [p[6], p[8], p[9]]])
    Sigma = 0.5 * np.trace(Io) * np.eye(3) - Io
    h = p[1:4]
    return np.block([[Sigma, h.reshape(3, 1)], [h.reshape(1, 3), np.array([[p[0]]])]])


def subspaces(unit, nsamples=40, seed=5, tol=1e-10):
    """The identifiable subspace and the structural null space N, by SVD of a stacked
    regressor at generic random states (step 4 of the R2 proof sketch)."""
    rng = np.random.default_rng(seed)
    n = unit[0].n
    rows = [
        regressor(unit, rng.normal(size=n), rng.normal(size=n), rng.normal(size=n))
        for _ in range(nsamples)
    ]
    A = np.vstack(rows)
    _, S, Vt = np.linalg.svd(A, full_matrices=True)
    nb = int((S > S[0] * tol).sum())
    return A, S, nb, Vt[:nb].T, Vt[nb:].T  # A, singular values, n_b, V_id, V_null


def identify(model, unit, V_id, nsamples, sigma, seed):
    """Least squares on the identifiable subspace only."""
    rng = np.random.default_rng(seed)
    n = model.n
    rows, rhs = [], []
    for _ in range(nsamples):
        a, b, c = rng.normal(size=n), rng.normal(size=n), rng.normal(size=n)
        rows.append(regressor(unit, a, b, c))
        rhs.append(rnea(model, a, b, c) + sigma * rng.normal(size=n))
    A, y = np.vstack(rows), np.concatenate(rhs)
    return V_id @ np.linalg.lstsq(A @ V_id, y, rcond=None)[0]
```

7-DOF 기준 팔은 앞 두 레슨과 **같은 모델**이다(링크 오프셋 고정, 질량 속성은 점질량 8개에서
생성 — `c2-rnea-inverse-dynamics` 재현 과제의 입력 데이터 절). 중력은 기본값
$a_g = (0,0,0,\,0,0,-9.81)$ 을 쓴다.

아래 **네 조건을 모두** 만족해야 통과다.

1. **재매개화와 선형성** — ⓐ 모든 바디에서
   $\lVert\texttt{spatial\_inertia\_of(params\_of}(m, c, \bar I_C))- \texttt{mcI}(m, c, \bar I_C)\rVert_\infty < 10^{-15}$
   (측정 $4.3\times10^{-19}$). ⓑ 무작위 상태 $10^2$ 개에서
   $\max\lVert Y\pi - \texttt{rnea}\rVert_\infty < 10^{-12}$ (측정 $7.1\times10^{-15}$).
   ⓒ $Y$ 가 $\pi$ 와 무관함을 확인하라 — 모델의 질량 속성을 바꿔도 같은 $Y$ 가 나와야 한다
   (차이가 **정확히** 0).
2. **식별 가능성 분해** — 무작위 상태 40개를 쌓아
   $$
   n_b = 43, \qquad \dim\mathcal{N} = 27, \qquad
   \frac{S_{43}}{S_{44}} > 10^{10}, \qquad \max\lVert AV_{\mathrm{null}}\rVert_\infty < 10^{-12}
   $$
   를 보이라(측정 $S_{43} = 5.220283$, $S_{44} = 1.894\times10^{-14}$, 비 $2.8\times10^{14}$,
   $\lVert AV_{\mathrm{null}}\rVert = 4.7\times10^{-13}$). 샘플 수를 $5, 10, 20, 40, 80$ 으로
   늘려 계수가 **포화**하는 것을 보이고($n \cdot n_{\text{samples}} \ge n_b$ 가 되는 지점부터
   43 에서 변하지 않는다), 중력을 끄면 $n_b = 39$ 로 줄어드는 것을 확인하라.
3. **잡음·조건수, 그리고 일관성이 사는 자리** — ⓐ $\sigma \in \{0, 10^{-3}, 10^{-2}, 10^{-1}\}$
   에서 R5 의 표를 재현하라: 식별 가능 성분의 오차가 $\propto\sigma$ (허용오차 5%),
   $\mathcal{N}$ 성분의 오차가 $\sigma$ 와 무관하게 $4.7586$ (허용오차 $10^{-3}$),
   새 상태의 토크 예측 오차가 $\propto\sigma$.
   ⓑ **참 매개변수가 물리적으로 일관**함을 확인하라: 모든 바디에서
   $\lambda_{\min}(P(\pi_i)) > 0$ (측정 최소 $9.3\times10^{-4}$).
   ⓒ **$\sigma = 0$ 에서도 최소노름 해가 비일관**함을 보이라: $\min_i\lambda_{\min}(P(\hat\pi_i)) < 0$
   (측정 $-1.1274$). 그런데 $\hat\pi + V_{\mathrm{null}}V_{\mathrm{null}}^\top\pi$ 는 **일관**
   하고(측정 $+9.32\times10^{-4}$) 토크 예측이 **바뀌지 않는다**(측정 $1.2\times10^{-12}$).
   ⓓ $\sigma = 10^{-2}$ 에서는 같은 보정으로도 일관성이 복구되지 않음을 보이라
   (측정 $-1.6\times10^{-3}$) — 이때 LMI 제약은 식별 가능 방향에도 작용한다.
   > 이 네 개가 이 레슨의 핵심이다. ⓒ 와 ⓓ 의 대비가 "왜 SDP 가 필요한가"의 전부다.
4. **해석적 미분의 정확성** — ⓐ 중력 0·$\dot q = 0$ 에서 $\partial\tau/\partial\ddot q$ 를
   중앙 유한차분해 CRBA 의 $M$ 과 $10^{-12}$ 이내로 일치시키고($h$ 를 $10^{-8}\dots10^{-4}$
   로 스윕해 **전 구간에서** 같은 수준임을 보이라 — 측정 $4.4\times10^{-16}$),
   중력을 켜면 상쇄가 지배해 오차가 $1/h$ 로 커지는 것을 대비로 보이라
   (측정 $7.1\times10^{-11}$ at $10^{-4}$, $8.7\times10^{-9}$ at $10^{-6}$,
   $9.2\times10^{-7}$ at $10^{-8}$).
   ⓑ $\tau$ 의 $\ddot q$ 아핀성을 단위 테스트로 확인하라(측정 $2.1\times10^{-14}$).
   ⓒ 정적 실험만으로는 $I_O$ 를 식별할 수 없음을 수치로 보이라: $Y(q, 0, 0)$ 의 $I_O$ 에
   해당하는 42개 열이 **정확히 0** 이어야 한다(문제 P1 ⓑ).

**입력 데이터**: 외부 데이터 불필요. 모델은 앞 두 레슨과 동일하고, 모든 난수는
`np.random.default_rng` 에 본문에 적힌 시드를 준다(모델 7, 부분공간 5, 식별 11).

**비교 대상** (최소 1개):
- 1순위: 조건 1 ⓑ — $Y\pi$ 와 앞 레슨의 `rnea` 는 **독립적인 두 경로**이고, 하나는 선형
  회귀자, 하나는 재귀 알고리즘이다.
- 2순위: 조건 4 ⓐ 의 CRBA $M$ 과 유한차분 야코비안.
- 선택 검증(없어도 통과): `cvxpy` 로 (5)의 SDP 를 실제로 풀어, $\sigma = 10^{-2}$ 에서
  제약을 켠 해가 ⓓ 의 비일관성을 제거하고 토크 예측 오차가 얼마나 늘어나는지 측정.
  의존성 없이 통과해야 하므로 **선택**이다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| $\lVert Y\pi - \tau\rVert$ 가 $10^{-3}$ 수준 | $I_O$ 대신 $\bar I_C$ 를 매개변수로 썼다 | 평행축 항 $m\hat c\hat c^\top$ 을 넣었는지 `params_of` 를 본다 |
| 같은 증상, $c \ne 0$ 인 바디에서만 | $h = mc$ 대신 $c$ 를 넣었다 | $c = 0$ 인 바디에서는 맞고 아니면 틀리는지 본다 |
| $n_b$ 가 샘플마다 달라진다 | SVD 문턱값이 특이값 간극 안에 들어가 있다 | 특이값을 전부 출력해 간극($5.2 \to 1.9\times10^{-14}$)을 눈으로 확인하고 문턱을 그 사이로 둔다 |
| $n_b$ 가 70 으로 나온다 | 쌓은 방정식 수가 부족하거나($n \times$ 샘플 < 70) 문턱값이 너무 작다 | 샘플을 늘려 포화를 확인한다(조건 2) |
| $\mathcal{N}$ 성분 오차가 $\sigma$ 와 함께 변한다 | 전체 공간에서 최소제곱을 풀었다(정칙화 없이) | $V_{\mathrm{id}}$ 로 투영한 뒤 푸는지 확인한다 — 전체 공간 해는 유일하지 않다 |
| 조건 3 ⓑ 가 실패 | 모델 생성기가 물리적으로 일관하지 않다 | **이 모듈이 실제로 겪은 일이다**: $0.02AA^\top + 0.05\mathbb{1}$ 생성기는 7개 중 6개가 삼각부등식을 위반한다. 점질량 생성기로 바꾼다 |
| 조건 4 ⓐ 에서 V 곡선이 보인다 | 중력을 끄지 않았다 | $\tau$ 의 크기를 출력한다 — 중력이 켜져 있으면 $O(10)$ 이고 상쇄가 지배한다 |
| 조건 4 ⓒ 에서 $I_O$ 열이 0 이 아니다 | $\dot q$ 또는 $\ddot q$ 를 0 으로 두지 않았다 | $v_i$ 를 전부 출력해 0 인지 확인한다 |

## 열린 문제

- **(열린 문제) 접촉이 있는 계의 식별, 그리고 비선형 요소** — (2)의 선형성은 트리·강체·마찰
  없음에 의존한다. 실제 로봇의 토크 오차는 관절 마찰(Stribeck·이력), 하모닉 드라이브의
  유연성, 케이블, 온도 드리프트가 지배하고 이들은 **선형 회귀 밖**이다. 접촉이 들어오면
  앞 레슨의 비매끄러움까지 더해져 "무엇을 식별하고 있는지" 자체가 흐려진다. 선형 부분을
  먼저 식별하고 잔차를 학습하는 관행은 두 단계의 오차가 어떻게 섞이는지에 대한 보증이 없다.
  현재 접근: 물리적 일관성을 제약으로 둔 식별
  ([Wensing et al. 2018](https://doi.org/10.1109/LRA.2017.2729659)), 잔차 학습, 미분 가능
  시뮬레이션. 비어 있는 자리: 선형 모델 + 학습 잔차의 분해가 **유일**한지, 그리고 그 분해의
  일반화 보증.
- **(열린 문제) 여진 궤적 설계의 전역 최적성** — R5 가 보여 주듯 바꿀 수 있는 것은 $\kappa$
  뿐이다. $\kappa$ 를 최소화하는 궤적을 찾는 문제는 비볼록이고(궤적이 회귀자에 비선형으로
  들어간다) 관절 한계·속도 한계·안전 제약까지 붙는다. 실무는 유한 Fourier 기저에 국소
  최적화를 거는 관행에 머물러 있고, **전역 최적 궤적**이나 그 하한은 알려져 있지 않다.
  $\dim\mathcal{N}$ 은 궤적으로 바꿀 수 없지만 **측정을 늘리면** 바꿀 수 있다는 점(R2 의 C4)이
  설계 공간을 넓히는데, 센서 추가와 궤적 설계를 **함께** 최적화하는 정식화는 거의 없다.
  현재 접근: Fourier 매개화 + 국소 최적화, D-최적 설계.
  비어 있는 자리: 센서 배치와 궤적의 공동 설계, 그리고 $\kappa$ 의 달성 가능한 하한.
- **(열린 문제) 접촉 동역학의 미분과 그 기울기의 정당성** — R4 는 접촉 없는 트리의 미분이고,
  접촉이 들어오면 앞 레슨의 열린 문제가 그대로 이어진다. 해석적 미분이 자동 미분보다 빠른
  이유(중복 계산)는 매끄러운 경우의 분석이고, 비매끄러운 접촉에서는 "무엇의 미분인가"가
  먼저 정의되어야 한다. 궤적 최적화와 정책 학습이 수천 개 상태에서 **동역학과 그 미분**을
  동시에 요구하는 지금, 이것이 실질적 병목이다. 현재 접근: 해석적 미분
  ([Carpentier & Mansard 2018](https://doi.org/10.15607/RSS.2018.XIV.038)), 볼록 완화의
  매끄러운 미분, 무작위 평활화. 비어 있는 자리: 완화 기울기의 오차 한계 —
  `c2-contact-dynamics` 의 첫 열린 문제와 같은 벽이고, 이 모듈이 그 벽에서 끝난다.

## 개념 점검

`rc quiz c2-dynamics-derivatives-sysid` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는
위 문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c2-dynamics-derivatives-sysid-quiz
questions:
  - id: q1
    type: single
    prompt: "공간 관성을 $\\pi$ 에 선형으로 만들려면 어떤 매개변수를 써야 하는가?"
    choices:
      - "$(m,\\; c,\\; \\bar{I}_C)$ — 질량·질량중심·질량중심 기준 관성"
      - "$(m,\\; h = mc,\\; I_O)$ — 질량·1차 모멘트·원점 기준 관성"
      - "$(m,\\; c,\\; I_O)$"
      - "어떤 선택에서도 선형이다"
    answer: 1
    explanation: "$(m, c, \\bar{I}_C)$ 에서는 좌상 블록의 평행축 항 $m\\hat{c}\\hat{c}^{\\top}$ 이 $c$ 에 2차라 비선형이다. $h = mc$ 와 $I_O = \\bar{I}_C + m\\hat{c}\\hat{c}^{\\top}$ 로 재매개화하면 모든 성분이 1차식이 된다. 이 한 번의 재매개화가 식별을 선형 최소제곱으로 만들고, 물리적 일관성 제약까지 볼록(LMI)으로 만든다 — 두 번 값을 한다."
    concept: { front: "관성 매개변수의 선형 매개화", back: "$(m,\\; h = mc,\\; I_O)$ 10개. $(m, c, \\bar{I}_C)$ 는 평행축 항 때문에 비선형" }
  - id: q2
    type: multiple
    prompt: "구조적 식별 불가능 부분공간 $\\mathcal{N}$ 에 대해 **참인** 것을 모두 고르라."
    choices:
      - "상태 $(q, \\dot{q}, \\ddot{q})$ 에 의존하지 않는다"
      - "여진 궤적을 잘 설계하면 줄일 수 있다"
      - "측정을 늘리면(베이스 힘센서 등) 줄어들 수 있다"
      - "$\\mathcal{N}$ 방향을 복원하지 못해도 토크 예측은 완전하다"
    answer: [0, 2, 3]
    explanation: "$\\mathcal{N}$ 은 모든 상태에 대한 커널의 교집합이므로 상태 무관이고, 궤적으로는 바꿀 수 없다 — 궤적이 바꾸는 것은 조건수 $\\kappa$ 다. 측정 집합을 바꾸면 줄어든다(식별 가능성은 기구 + 측정의 성질이다). 그리고 $\\tau$ 는 $Y\\pi$ 만 보므로 기저 매개변수만으로 예측은 완전하다 — 측정에서 $\\sigma = 10^{-3}$ 일 때 새 상태 예측 오차가 $2\\times10^{-3}$ 수준이다."
    concept: { front: "$\\mathcal{N}$ 의 성질", back: "상태 무관·궤적으로 못 바꿈·측정으로 바꿀 수 있음·토크 예측에는 무해. 궤적이 바꾸는 것은 $\\kappa$" }
  - id: q3
    type: short
    prompt: "관성 매개변수가 양의 질량 밀도로 실현 가능한 것과 동치인 조건은? (행렬 이름으로)"
    answer: ["유사 관성 행렬의 양정치성", "pseudo-inertia", "유사 관성", "pseudo inertia", "유사관성 행렬", "P >= 0", "유사 관성이 양정치"]
    explanation: "$P(\\pi_i) = \\int\\rho\\,\\tilde{r}\\tilde{r}^{\\top}dV \\succeq 0$ ($\\tilde{r} = (r; 1)$)이고 역방향도 점질량 4개로 구성된다. $P$ 가 $\\pi_i$ 에 선형이므로 이것은 LMI 이고 식별이 SDP 가 된다. $I_O \\succ 0$ 과 삼각부등식은 $P$ 의 좌상 블록 조건일 뿐이라 **엄격히 약하다**."
    concept: { front: "물리적 일관성의 동치 조건", back: "유사 관성 $P(\\pi_i) \\succeq 0$. $\\pi_i$ 에 선형이라 LMI → 식별이 SDP. 삼각부등식보다 강하다" }
  - id: q4
    type: truefalse
    prompt: "$\\partial\\tau/\\partial\\ddot{q}$ 는 질량행렬 $M(q)$ 와 정확히 같다."
    answer: true
    explanation: "$\\tau = M(q)\\ddot{q} + b(q,\\dot{q})$ 이고 $b$ 는 $\\ddot{q}$ 와 무관하므로 야코비안이 정확히 $M(q)$ 다 — 근사가 아니다. 그래서 중력을 끄고 $\\dot{q} = 0$ 으로 두면 유한차분이 절단 오차 없이 기계 정밀도를 내고($4.4\\times10^{-16}$, 모든 $h$ 에서), 중력을 켜면 상쇄가 지배해 $1/h$ 로 커진다."
    concept: { front: "$\\partial\\tau/\\partial\\ddot{q}$", back: "정확히 $M(q)$ — CRBA 가 곧 이 야코비안. 중력 0 에서 유한차분이 절단 오차 0" }
  - id: q5
    type: single
    prompt: "잡음이 전혀 없는데도($\\sigma = 0$) 최소노름 식별 해가 물리적으로 비일관일 수 있다. 그 이유는?"
    choices:
      - "최소제곱이 수렴하지 않기 때문"
      - "물리적 일관성이 식별 불가능한 방향에 들어 있고, 최소노름 해는 그 방향을 0 으로 두기 때문"
      - "회귀자의 조건수가 크기 때문"
      - "유사 관성이 $\\pi$ 에 비선형이기 때문"
    answer: 1
    explanation: "측정: $\\sigma = 0$ 에서 식별 가능 부분공간의 해는 $\\min\\lambda_{\\min}(P) = -1.1274$ 로 비일관인데, $\\mathcal{N}$ 성분을 참값으로 되돌리면 $+9.3\\times10^{-4}$ 로 일관해지고 **토크 예측은 전혀 바뀌지 않는다**($1.2\\times10^{-12}$). 즉 일관성은 전부 식별 불가능한 방향에 있다 — (5)의 SDP 가 고르는 것이 그 방향이다. $\\sigma$ 가 커지면 식별 가능 성분까지 일관 집합 밖으로 밀려 제약이 추정값을 바꾼다."
    concept: { front: "$\\sigma = 0$ 에서도 비일관인 이유", back: "일관성이 $\\mathcal{N}$ 방향에 있고 최소노름 해는 그것을 0 으로 둔다. SDP 가 그 방향을 고른다" }
```

## 이 단계 공부법

1. **$h = mc$ 재매개화를 손으로 확인한다 (25분)** — 앞 모듈 레슨 1 의 (4)와 이 레슨 (1)을
   나란히 쓰고, 평행축 항이 어떻게 사라지는지 성분으로 따라가라. 이 10분이 레슨 전체의
   전제다. 그 다음 `params_of`/`spatial_inertia_of` 왕복을 $10^{-15}$ 로 확인하라(조건 1 ⓐ).
2. **회귀자를 세 줄로 만든다 (30분)** — $\pi = e_k$ RNEA 로 $Y$ 를 뽑고
   $\lVert Y\pi - \tau\rVert$ 를 본다. 문헌의 성분식 전개를 **읽지 말고** 이 방식으로 시작하라 —
   앞 레슨의 검증된 RNEA 를 재사용하므로 틀릴 여지가 거의 없다.
3. **특이값을 눈으로 본다 (40분)** — 쌓은 회귀자의 특이값 70개를 전부 출력하라.
   $5.22$ 에서 $1.9\times10^{-14}$ 로 떨어지는 간극이 **보여야** $n_b = 43$ 이 믿을 수 있는
   수가 된다. 문턱값을 그 간극 안에 두는 것이 전부고, 간극이 없으면 $n_b$ 를 세는 것 자체가
   무의미하다(진단표 3·4행).
4. **R2 의 4단계만 따로 이해한다 (40분)** — "해석 함수의 영집합은 측도 0"이 왜 필요한지,
   그것이 "무작위 샘플로 계수를 세도 된다"를 어떻게 정당화하는지 한 문단으로 써라.
   이 한 단계가 실무 절차(무작위 샘플 + SVD)를 정리(定理)로 바꾼다.
5. **일관성이 어디 사는지 직접 본다 (60분)** — 조건 3 ⓒⓓ 를 먼저 하라. $\sigma = 0$ 에서도
   최소노름 해가 비일관이고, $\mathcal{N}$ 성분을 되돌리면 일관해지며 예측은 안 바뀐다는
   세 숫자를 자기 손으로 보면 "왜 SDP 인가"가 끝난다. 이 실험이 이 레슨의 중심이다.
6. **자기 생성기를 의심한다 (30분)** — 조건 3 ⓑ 를 자기 모델에 돌려 보라. 이 모듈의 저자는
   레슨 2·3 에서 "$0.02AA^\top + 0.05\mathbb{1}$ 이 삼각부등식을 만족한다"고 썼고 **틀렸다**
   (7개 중 6개 위반). 유사 관성 검사는 그런 주장을 즉시 반증한다 — 모델을 만들 때마다 돌려라.
7. **논문 네 편을 네 축으로 읽는다 (150분)** — Atkeson(선형 회귀) → Gautier–Khalil(최소 기저)
   → Wensing(일관성) → Carpentier–Mansard(미분) 순서가 시간순이자 논리순이다. 각 논문마다
   "이 저자가 R1–R5 중 어느 결과를 만들었는가"를 한 줄로 적어라.
8. **모듈을 닫는다 (30분)** — C2 의 여섯 레슨을 한 장으로 요약하라: 표기(레슨 1) → 역동역학
   (2) → 질량행렬·순동역학(3) → 제약(4) → 접촉(5) → 모델을 얻는 법(6). 그 다음 열린 문제
   세 개를 골라 "접촉의 미분"이라는 하나의 벽으로 수렴하는 것을 확인하라 — C3·C4·S2 가
   그 벽에서 시작한다.

**통과 기준**: 백지에서 (1)(2)(3)(4)를 쓸 수 있고, R2 의 포화 논증과 R3 의 랭크 1 적분
논증을 말할 수 있고, 재현 과제 네 조건을 통과하는 회귀자·식별·일관성 검사를 갖고 있고,
논문 3편(권장 1편 포함 4편)의 1페이지 노트가 있다.
