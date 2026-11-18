---
id: c4-ilqr-ddp
title: iLQR/DDP 와 정규화
summary: >-
  DDP 의 2차 역방향 패스를 빠진 줄 없이 유도하고, DDP 가 제어열에 대한 Newton 법이라 2차
  수렴하는 반면 iLQR 은 Gauss-Newton 이라 1차 수렴한다는 것을 증명 스케치와 수치로 확인한다.
  최적점에서 멀면 $Q_{uu}$ 가 부정부호가 되는 것이 왜 정규화·merit function·선탐색을
  필수로 만드는지, 그리고 제어 상자 제약은 왜 정확히 처리할 수 있고 상태 제약은 왜 못 하는지를
  다룬다. 재현 과제에서 진자로 수렴 차수를 측정하고 카트폴 스윙업을 토크 한계 아래 푼다.
objectives:
  - DDP 의 2차 역방향 패스($Q_x$부터 $V_{xx}$까지)를 빠진 줄 없이 유도할 수 있다.
  - DDP 가 2차, iLQR 이 1차 수렴하는 이유를 Newton 대 Gauss-Newton 으로 설명하고 수렴율을 수치로 측정할 수 있다.
  - 정규화 없이 iLQR·DDP 가 발산하는 조건을 설명하고, $Q_{uu}$ 정규화와 $V_{xx}$ 정규화의 차이를 말할 수 있다.
  - merit function 과 기대 감소량 비 검정이 선탐색에서 하는 일을 쓰고 구현할 수 있다.
  - 제어 상자 제약을 투영으로 정확히 처리하고, 같은 방법이 상태 제약에 왜 통하지 않는지 설명할 수 있다.
prerequisites: [c4-dp-lqr-lqg]
difficulty: 5
estimated_minutes: 660
tags: [optimal-control, ilqr, ddp, regularization, line-search, research]
activities:
  - id: c4-ilqr-ddp-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 110
  - id: c4-ilqr-ddp-papers
    kind: paper
    title: 필독 논문 4편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 180
  - id: c4-ilqr-ddp-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 2 · 반례 1 · 논문 1)
    estimated_minutes: 210
  - id: c4-ilqr-ddp-reproduction
    kind: reproduction
    title: 재현 과제 — 진자의 수렴 차수와 카트폴 스윙업 (R2)
    estimated_minutes: 140
  - id: c4-ilqr-ddp-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 20
resources:
  - title: "Tedrake, Underactuated Robotics — Trajectory Optimization"
    url: https://underactuated.csail.mit.edu/trajopt.html
    kind: book
    note: ch.10.3 이 DDP·iLQR. 전문 무료.
  - title: "Nocedal & Wright, Numerical Optimization"
    kind: book
    note: 권장. ch.3(선탐색), ch.10(Gauss-Newton), ch.4(신뢰영역). R2·R3 의 배경. (공식 URL 미확인)
papers:
  - id: mayne1966-ddp
    required: true
    role: seminal
  - id: liao1991-ddp-convergence
    required: true
    role: standard
  - id: tassa2012-ilqr
    required: true
    role: standard
    note: "§III"
  - id: tassa2014-control-limited-ddp
    required: true
    role: standard
  - id: howell2019-altro
    role: standard
---

# iLQR/DDP 와 정규화

## 전제와 기호

앞 레슨은 **선형** 문제의 값 함수가 2차형식으로 닫힌다는 것을 썼다. 이 레슨은 그 계산을
비선형 문제의 **기준 궤적 주변**에서 반복한다. 그것이 iLQR/DDP 이고, 로보틱스 궤적 최적화의
작업용 도구다. 권장 선수는 앞 두 레슨과 R0 모듈(수치 최적화)이다.

이 레슨이 추가로 전제하는 것:

- 수치 최적화: Newton 법과 Gauss-Newton 의 차이, 선탐색(line search)과 신뢰영역,
  Armijo 조건. 2차 수렴·1차 수렴의 정의.
- 자동 미분 또는 유한차분으로 $f_x, f_u$ 를 얻을 수 있다는 것(`r0-ad-and-integrators`).

표기 규약(C4 모듈 공통, 앞 레슨들에 이어서):

| 기호 | 뜻 |
|---|---|
| $x_k \in \mathbb{R}^n$, $u_k \in \mathbb{R}^m$ | 기준 궤적 $(\bar{x}, \bar{u})$ 의 상태·제어. 아래 첨자는 단계 |
| $f(x,u)$ | 이산 동역학 $x_{k+1} = f(x_k, u_k)$. $f_x, f_u$ 는 야코비안, $f_{xx}$ 는 3-텐서 |
| $\ell(x,u)$, $\ell_f(x)$ | 단계 비용과 종단 비용 |
| $V_k(x)$ | $k$ 단계의 값 함수. 2차 근사의 계수가 $V_x, V_{xx}$ |
| $Q_k(\delta x, \delta u)$ | 한 단계의 작용 가치(action-value) 2차 근사 |
| $k_k \in \mathbb{R}^m$, $K_k \in \mathbb{R}^{m\times n}$ | 전향 항(feedforward)과 피드백 이득. $\delta u = k_k + K_k\delta x$ |
| $\mu \ge 0$ | 정규화 세기 |
| $\alpha \in (0, 1]$ | 선탐색 보폭. $u_k = \bar{u}_k + \alpha k_k + K_k(x_k - \bar{x}_k)$ |
| $\Delta_1, \Delta_2$ | 기대 비용 감소량의 1차·2차 계수 |
| $\bar{u}$ (스칼라) | 제어 한계. $\lvert u \rvert \le \bar{u}$ |

**$\tfrac12$ 규약**: 앞 레슨과 같다. 비용은 $J = \sum_k \ell(x_k,u_k) + \ell_f(x_N)$ 이고
2차형식에는 $\tfrac12$ 를 붙인다.

**중요한 구분**: **iLQR** 은 역방향 패스에서 $f_{xx}, f_{ux}, f_{uu}$ 항을 **버린** 것이고
**DDP** 는 그 항을 유지한 것이다. 둘은 같은 알고리즘의 두 설정이며, 이 레슨의 R2 가 그 차이가
수렴 차수로 나타남을 보인다. 논문을 읽을 때 "iLQR"이라 쓰고 DDP 를 뜻하는 경우가 흔하므로
역방향 패스의 식을 직접 확인하라.

문제:

$$
\min_{u_{0:N-1}} \; J = \sum_{k=0}^{N-1}\ell(x_k, u_k) + \ell_f(x_N)
  \quad \text{s.t.}\quad x_{k+1} = f(x_k, u_k), \; x_0 \text{ 주어짐},
  \; \lvert u_k \rvert \le \bar{u}. \tag{1}
$$

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (DDP 의 2차 역방향 패스) [D2]** — 기준 궤적 주변에서 값 함수를 2차까지 전개하면,
  $V' := V_{k+1}$ 의 계수 $(V'_x, V'_{xx})$ 로부터
  $$
  \begin{aligned}
  Q_x &= \ell_x + f_x^\top V'_x, &
  Q_u &= \ell_u + f_u^\top V'_x, \\
  Q_{xx} &= \ell_{xx} + f_x^\top V'_{xx} f_x + V'_x \!\cdot\! f_{xx}, &
  Q_{ux} &= \ell_{ux} + f_u^\top V'_{xx} f_x + V'_x \!\cdot\! f_{ux}, \\
  Q_{uu} &= \ell_{uu} + f_u^\top V'_{xx} f_u + V'_x \!\cdot\! f_{uu}, & &
  \end{aligned} \tag{2}
  $$
  이고 제약이 없으면 최소화자는
  $$k = -Q_{uu}^{-1}Q_u, \qquad K = -Q_{uu}^{-1}Q_{ux}, \tag{3}$$
  이며 값 함수 계수는
  $$
  V_x = Q_x - Q_{ux}^\top Q_{uu}^{-1}Q_u, \qquad
    V_{xx} = Q_{xx} - Q_{ux}^\top Q_{uu}^{-1}Q_{ux}, \qquad
    \Delta V = -\tfrac12 Q_u^\top Q_{uu}^{-1}Q_u \tag{4}
  $$
  로 갱신된다. $V'_x \!\cdot\! f_{xx}$ 류의 세 항을 버리면 **iLQR**이다.
- **R2 (수렴 차수: DDP 는 2차, iLQR 은 1차) [D3]** — (1)을 $u_{0:N-1}$ 만의 무제약 문제로
  보면 DDP 의 한 반복은 그 문제에 대한 **Newton 단계와 일치**하므로 국소 2차 수렴한다
  (Liao & Shoemaker 1991). iLQR 은 버린 곡률만큼 Hessian 을 근사하므로 **Gauss-Newton**이고,
  국소 수렴율은
  $$\limsup_{n\to\infty}\frac{\lVert k^{(n+1)}\rVert}{\lVert k^{(n)}\rVert} = r < 1 \tag{5}$$
  인 1차(선형) 수렴이며 $r$ 은 버린 항의 상대 크기로 결정된다. 재현 과제의 진자에서
  $r = 0.2592$ (4자리까지 안정)이고, DDP 는 $\lVert k^{(n+1)}\rVert/\lVert k^{(n)}\rVert^2
  \approx 0.02$ 로 2차다.
- **R3 (정규화·merit·선탐색이 필수인 이유) [D2]** — 최적점에서 멀면 $Q_{uu}$ 가 부정부호일 수
  있고((2)의 $V'_x\!\cdot\!f_{uu}$ 항과 음의 $V'_{xx}$ 때문), 그러면 (3)은 최소화자가 아니라
  **안장점이나 최대점**을 준다. 두 가지 정규화가 쓰인다:
  $$
  \tilde{Q}_{uu} = Q_{uu} + \mu I \quad\text{(제어 정규화)}, \qquad
    \tilde{Q}_{uu} = \ell_{uu} + f_u^\top (V'_{xx} + \mu I) f_u + \cdots
    \quad\text{(상태 정규화, Tassa 2012)} \tag{6}
  $$
  이고 후자가 선호된다 — $\mu \to \infty$ 에서 전자는 $k \to 0$ 으로 **기준 궤적에 멈추지만**
  후자는 $K$ 도 함께 줄어 **이전 궤적을 따라가는 피드백**으로 수렴해 신뢰영역의 의미가 맞다.
  보폭은 기대 감소량
  $$
  \Delta J(\alpha) = \alpha\,\Delta_1 + \tfrac12\alpha^2\Delta_2, \quad
    \Delta_1 = \sum_k k_k^\top Q_{u,k}, \quad \Delta_2 = \sum_k k_k^\top Q_{uu,k}k_k \tag{7}
  $$
  과 실제 감소량의 비 $z = (J - J')/(-\Delta J(\alpha))$ 가 문턱(보통 $0.1$)을 넘을 때만
  받아들인다. $z$ 검정이 없으면 "비용이 줄었지만 모델과 무관하게 줄은" 단계를 받아들여
  정규화가 영원히 커지지 않는다.
- **R4 (제어 제약은 정확히, 상태 제약은 못 한다) [D2]** — $\lvert u\rvert \le \bar{u}$ 는
  역방향 패스의 상자 제약 QP
  $$
  \min_{\delta u:\ \underline{b} \le \delta u \le \overline{b}}
    \tfrac12\delta u^\top Q_{uu}\delta u + (Q_u + Q_{ux}\delta x)^\top \delta u \tag{8}
  $$
  로 정확히 풀 수 있다. $m = 1$ 이면 무제약 해를 **구간으로 자르는 것**이 정확한 해이고,
  잘린 성분의 피드백 행은 0 으로 둔다. $m > 1$ 은 투영 Newton 이 필요하다(Tassa 2014).
  반면 상태 제약 $g(x_k) \le 0$ 은 **$\delta u$ 에 대한 제약이 아니어서** (8)에 들어가지
  못하고, DDP 구조 안에 자연스러운 처리법이 없다 — 증강 라그랑주(ALTRO)나 장벽 함수로
  **비용에 얹는** 것이 현재의 길이다.
- **R5 (iLQR 은 국소 방법이다) [D2]** — (1)은 비볼록이고 iLQR/DDP 는 기준 궤적 주변의
  2차 모델만 쓰므로 **초기 추정에 따라 다른 국소 최적해**로 간다. 재현 과제의 카트폴에서
  영 초기 추정은 $J^* = 307.815$, 무작위 초기 추정은 $J^* = 199.299$ 로 수렴한다 —
  같은 문제, 같은 제약, 다른 해다.

## 유도

### R1 — 2차 역방향 패스

기준 궤적 $(\bar{x}_{0:N}, \bar{u}_{0:N-1})$ 과 그 주변의 편차
$\delta x_k = x_k - \bar{x}_k$, $\delta u_k = u_k - \bar{u}_k$ 를 둔다. 값 함수를
기준 궤적 위에서 2차까지 전개한다:

$$
V_k(\bar{x}_k + \delta x) \approx V_k(\bar{x}_k) + V_{x,k}^\top\delta x
  + \tfrac12 \delta x^\top V_{xx,k}\,\delta x. \tag{9}
$$

Bellman 방정식(앞 레슨 (2))을 편차 변수로 쓴다. $V' := V_{k+1}$ 로 줄여 쓰면

$$
V_k(\bar{x}_k + \delta x) = \min_{\delta u}\Big\{
  \ell(\bar{x}_k + \delta x,\ \bar{u}_k + \delta u)
  + V'\big(f(\bar{x}_k + \delta x,\ \bar{u}_k + \delta u)\big)\Big\}. \tag{10}
$$

중괄호 안을 $Q_k(\delta x, \delta u)$ 라 부르고 **2차까지** 전개한다. 두 항을 따로 본다.

**첫 항(단계 비용)** 은 그냥 Taylor 전개다:
$\ell \approx \ell + \ell_x^\top\delta x + \ell_u^\top\delta u
+ \tfrac12(\delta x^\top \ell_{xx}\delta x + 2\delta u^\top \ell_{ux}\delta x
+ \delta u^\top \ell_{uu}\delta u)$.

**둘째 항** 이 유도의 전부다. 먼저 동역학을 2차까지 전개한다:

$$
\delta x' := f(\bar{x}+\delta x, \bar{u}+\delta u) - \bar{x}_{k+1}
  = f_x\delta x + f_u\delta u
  + \tfrac12\Big[\delta x^\top f_{xx}\delta x + 2\,\delta u^\top f_{ux}\delta x
  + \delta u^\top f_{uu}\delta u\Big] + O(\lVert\cdot\rVert^3), \tag{11}
$$

여기서 $f_{xx}$ 등은 3-텐서이고 대괄호는 성분마다 하나의 2차형식을 주는 벡터다. 이것을
(9)의 $V'$ 에 넣는다:

$$
V'(\bar{x}_{k+1} + \delta x') \approx V' + V_x'^\top\delta x'
  + \tfrac12\delta x'^\top V'_{xx}\delta x'.
$$

**$\delta x'$ 의 2차 항이 어디로 가는지가 핵심이다.**

- $V_x'^\top \delta x'$ 에서 (11)의 **2차 괄호**가 살아남는다 —
  $\tfrac12 V_x'\!\cdot\![\delta x^\top f_{xx}\delta x + \cdots]$. 이것이 (2)의
  $V'_x\!\cdot\!f_{xx}$, $V'_x\!\cdot\!f_{ux}$, $V'_x\!\cdot\!f_{uu}$ 세 항이고,
  **DDP 와 iLQR 을 가르는 항**이다.
- $\tfrac12\delta x'^\top V'_{xx}\delta x'$ 에서는 (11)의 **1차 부분만** 2차에 기여한다
  ($\delta x'$ 의 2차 항과 $V'_{xx}$ 가 만나면 3차 이상이므로 버린다). 즉
  $\tfrac12(f_x\delta x + f_u\delta u)^\top V'_{xx}(f_x\delta x + f_u\delta u)$ 이고,
  이것이 (2)의 $f_x^\top V'_{xx}f_x$, $f_u^\top V'_{xx}f_x$, $f_u^\top V'_{xx}f_u$ 세 항이다.

두 항을 모아 계수별로 정리하면 정확히 (2)다. 즉

$$
Q_k(\delta x, \delta u) = \text{const} + Q_x^\top\delta x + Q_u^\top\delta u
  + \tfrac12\begin{bmatrix}\delta x \\ \delta u\end{bmatrix}^\top
  \begin{bmatrix} Q_{xx} & Q_{ux}^\top \\ Q_{ux} & Q_{uu}\end{bmatrix}
  \begin{bmatrix}\delta x \\ \delta u\end{bmatrix}. \tag{12}
$$

**최소화.** $Q_{uu} \succ 0$ 이면 (12)를 $\delta u$ 로 미분해 0 으로 두면
$Q_u + Q_{uu}\delta u + Q_{ux}\delta x = 0$, 즉

$$\delta u^*(\delta x) = -Q_{uu}^{-1}(Q_u + Q_{ux}\delta x) = k + K\delta x \tag{13}$$

로 (3)이다. **$k$ 는 기준 궤적 자체를 고치는 전향 항이고 $K$ 는 편차에 대한 피드백**이다.
이 구분이 전향 패스에서 결정적이다(아래 R3).

**값 함수 갱신.** (13)을 (12)에 다시 넣는다. $\delta u^* = k + K\delta x$ 를 대입하고
$k = -Q_{uu}^{-1}Q_u$, $K = -Q_{uu}^{-1}Q_{ux}$ 를 쓰면

$$
\begin{aligned}
Q_u^\top\delta u^* + \tfrac12 \delta u^{*\top}Q_{uu}\delta u^* + \delta u^{*\top}Q_{ux}\delta x
  &= Q_u^\top k + Q_u^\top K\delta x + \tfrac12 k^\top Q_{uu}k + k^\top Q_{uu}K\delta x \\
  &\quad + \tfrac12 \delta x^\top K^\top Q_{uu}K\delta x + k^\top Q_{ux}\delta x
  + \delta x^\top K^\top Q_{ux}\delta x.
\end{aligned}
$$

여기서 $Q_{uu}k = -Q_u$, $Q_{uu}K = -Q_{ux}$ 를 써서 항을 지운다:
$\tfrac12 k^\top Q_{uu}k = -\tfrac12 k^\top Q_u$ 이므로 상수항은
$Q_u^\top k - \tfrac12 k^\top Q_u = \tfrac12 Q_u^\top k = -\tfrac12 Q_u^\top Q_{uu}^{-1}Q_u$ —
(4)의 $\Delta V$ 다. $\delta x$ 의 1차 계수는
$K^\top Q_u + Q_{uu}^{\top}{}^{-1}\cdots$ 를 정리하면 $K^\top Q_u + Q_{ux}^\top k
+ K^\top Q_{uu}k = K^\top Q_u + Q_{ux}^\top k - K^\top Q_u = Q_{ux}^\top k
= -Q_{ux}^\top Q_{uu}^{-1}Q_u$ 가 되어 $V_x = Q_x - Q_{ux}^\top Q_{uu}^{-1}Q_u$ 다.
2차 계수는 같은 방식으로 $K^\top Q_{uu}K + 2K^\top Q_{ux} = -Q_{ux}^\top Q_{uu}^{-1}Q_{ux}$ 이므로
$V_{xx} = Q_{xx} - Q_{ux}^\top Q_{uu}^{-1}Q_{ux}$ — (4)다.

> **구현 주의**: (4)의 형태는 앞 레슨 (13)과 같은 "두 양의 차"다. 실제 코드는 앞 레슨의
> Joseph 형태에 대응하는
> $V_{xx} = Q_{xx} + K^\top Q_{uu}K + K^\top Q_{ux} + Q_{ux}^\top K$ 를 쓰고 매 단계
> $(V_{xx} + V_{xx}^\top)/2$ 로 대칭화한다. 두 형태는 (3)을 대입하면 같다(문제 P1).

**가정이 깨지는 곳**: (13)은 $Q_{uu} \succ 0$ 을 썼다. $Q_{uu}$ 는 $\ell_{uu} \succ 0$ 이어도
$V'_{xx}$ 가 음의 고윳값을 갖거나 $V'_x\!\cdot\!f_{uu}$ 가 크면 부정부호가 된다. 그러면
(13)은 최소화자가 아니다 — $Q_{uu}$ 의 음의 고유방향으로 $\delta u$ 를 키우면 모델 비용이
$-\infty$ 로 가고, 전향 패스는 발산한다. **이것이 R3 의 출발점이다.** 두 번째 실패:
(11)의 전개는 $\lVert\delta x\rVert$, $\lVert\delta u\rVert$ 가 작을 때만 유효하다 —
$k$ 가 크면 3차 항이 지배해 2차 모델이 거짓말을 한다. 그래서 $\alpha$ 가 필요하다.

### R3 — 정규화, merit function, 선탐색

#### 정규화

$Q_{uu}$ 가 부정부호일 때 고치는 두 방법이 (6)이다.

**제어 정규화** $\tilde{Q}_{uu} = Q_{uu} + \mu I$ 는 Levenberg-Marquardt 다. $\mu$ 를 키우면
$k \to -\mu^{-1}Q_u \to 0$ 이고 $K \to -\mu^{-1}Q_{ux} \to 0$ 이므로, 극한에서
**제어가 기준 궤적의 $\bar{u}$ 에 그대로 멈춘다**. 문제는 $\bar{u}$ 가 피드백이 **없는**
개루프 제어열이라는 점이다. $\mu$ 가 클 때 전향 패스는 사실상 "아무것도 하지 않는" 궤적을
굴리므로 신뢰영역의 중심이 **개루프 궤적**이 된다.

**상태 정규화**(Tassa 2012 §III-A)는 $V'_{xx}$ 에 $\mu I$ 를 더한다:

$$
\tilde{Q}_{uu} = \ell_{uu} + f_u^\top(V'_{xx} + \mu I)f_u + V'_x\!\cdot\!f_{uu}, \qquad
  \tilde{Q}_{ux} = \ell_{ux} + f_u^\top(V'_{xx} + \mu I)f_x + V'_x\!\cdot\!f_{ux}. \tag{14}
$$

$\mu \to \infty$ 에서 $\tilde{Q}_{uu} \approx \mu f_u^\top f_u$,
$\tilde{Q}_{ux} \approx \mu f_u^\top f_x$ 이므로
$K \to -(f_u^\top f_u)^{-1}f_u^\top f_x$ 로 **0 이 아닌 값**에 수렴한다. 그 $K$ 는
"$\delta x$ 를 가능한 한 지우는" 최소제곱 피드백이고, 전향 패스는 **이전 궤적을 추종하는
폐루프**를 굴린다. 신뢰영역의 중심이 궤적 자체가 되므로 발산이 억제된다 — 같은 $\mu$ 에서
훨씬 안전하다. 그래서 실무 구현은 (14)를 쓴다.

$\mu$ 의 조절은 신뢰영역의 표준 방식이다: 단계가 **받아들여지면 줄이고**($\mu \leftarrow \mu/10$,
하한 있음), **거부되면 키운다**($\mu \leftarrow 10\mu$). 상한($10^{10}$ 정도)에 닿으면
실패를 보고하고 멈춘다 — 무한 루프를 만들지 않는다(엔지니어링 규칙: 루프에는 종료 조건과
최대 반복 수가 있다).

#### merit function 과 기대 감소량 비

전향 패스는 (13)의 $k$ 와 $K$ 를 **다르게 쓴다**:

$$
u_k = \bar{u}_k + \alpha\,k_k + K_k\,(x_k - \bar{x}_k). \tag{15}
$$

$\alpha$ 가 $k$ 에만 붙고 $K$ 에는 붙지 않는 것이 중요하다. $K$ 에도 $\alpha$ 를 곱하면
$\alpha \to 0$ 에서 피드백이 사라져 비선형 동역학이 기준 궤적에서 멀어지고, 작은 보폭이
오히려 **더 나쁜** 궤적을 준다. $\alpha$ 는 "기준 궤적을 얼마나 바꿀지"를 재는 양이지
"피드백을 얼마나 쓸지"가 아니다. (문제 P5 가 이것을 수치로 보게 한다.)

보폭을 받아들일지는 (7)의 기대 감소량으로 판정한다. (4)에서 한 단계의 모델 감소량이
$-\tfrac12 Q_u^\top Q_{uu}^{-1}Q_u = \tfrac12 k^\top Q_u$ 였고, 보폭 $\alpha$ 를 넣으면
$\delta u = \alpha k$ 이므로 모델 비용의 변화는

$$
Q_u^\top(\alpha k) + \tfrac12(\alpha k)^\top Q_{uu}(\alpha k)
  = \alpha\,k^\top Q_u + \tfrac12\alpha^2 k^\top Q_{uu}k,
$$

단계마다 더하면 (7)이다. **merit 검정**은

$$
z = \frac{J(\bar{u}) - J(u(\alpha))}{-\Delta J(\alpha)} > c \quad (c = 0.1 \text{ 이 표준}) \tag{16}
$$

이고, $z$ 가 문턱을 넘지 못하면 $\alpha$ 를 반으로 줄여 다시 시도한다(backtracking). 모든
$\alpha$ 가 실패하면 $\mu$ 를 키워 역방향 패스를 다시 돈다.

**$z$ 검정이 왜 필요한가**: "$J$ 가 줄었으면 받아들인다"만 쓰면, 2차 모델이 전혀 맞지 않는
큰 단계도 운 좋게 비용이 조금 줄면 통과한다. 그러면 $\mu$ 가 줄어들고(단계가 받아들여졌으므로)
다음 반복에서 더 큰 단계를 시도해 발산한다. $z$ 는 "모델이 예측한 만큼 실제로 줄었는가"를
재므로, 모델이 틀린 영역에서 $\mu$ 를 **올리는** 신호가 된다. Armijo 조건의 신뢰영역 버전이다.

**가정이 깨지는 곳**: $\Delta J(\alpha)$ 는 $Q_{uu}$ 로 계산되는데, 정규화한
$\tilde{Q}_{uu}$ 로 계산하면 기대 감소량이 과소평가되어 $z > 1$ 이 흔해지고 검정이 느슨해진다.
**(7)은 정규화하지 않은 $Q_{uu}$ 로 계산해야 한다.** 둘째, 제어가 상자에서 잘렸으면
(R4) 잘린 $k$ 로 (7)을 계산해야 한다 — 무제약 $k$ 를 쓰면 실제보다 큰 감소를 예측해
$z$ 가 늘 작아지고 선탐색이 영원히 실패한다.

### R4 — 상자 제약은 정확히, 상태 제약은 못 한다

#### 제어 상자 제약

(1)의 $\lvert u_k\rvert \le \bar{u}$ 는 $\delta u_k$ 에 대한 상자
$\underline{b} = -\bar{u} - \bar{u}_k$, $\overline{b} = \bar{u} - \bar{u}_k$ 가 되므로
역방향 패스의 최소화 (13)이 상자 제약 QP (8)로 바뀐다. $\delta x = 0$ (기준 궤적 위)에서
전향 항만 보면

$$
k = \arg\min_{\underline{b}\le\delta u\le\overline{b}}
  \tfrac12\delta u^\top Q_{uu}\delta u + Q_u^\top\delta u. \tag{17}
$$

- **$m = 1$ 이면 정확하다.** 1차원 2차함수를 구간에서 최소화하는 것은 무제약 최소화자
  $-Q_u/Q_{uu}$ 를 구간으로 **자르는 것**이다($Q_{uu} > 0$ 이므로 볼록). 추가 반복이 없다.
- **잘렸으면 피드백 행을 0 으로 둔다.** $k$ 가 경계에 붙었다는 것은 그 성분이 활성 제약에
  있다는 뜻이고, $\delta x$ 가 조금 변해도 그 성분은 경계에 머문다. 따라서 그 행에서
  $K = 0$ 이 1차적으로 옳다. 이것이 Tassa 2014 의 투영(projection)이고, $m=1$ 에서는
  정확한 활성집합 판정이다.
- **$m > 1$ 이면 활성집합을 찾아야 한다.** 상자 제약 QP 는 다항식 시간에 풀리지만 닫힌
  형태가 없다. Tassa 2014 는 투영 Newton(자유 성분에 대해서만 $Q_{uu}$ 를 분해)으로 푼다.

전향 패스에서도 $u_k$ 를 상자로 자른다((15) 다음에 `clip`). 이 두 가지를 **함께** 해야
한다 — 전향에서만 자르면 역방향의 $K$ 가 "자를 수 있다는 사실을 모르는" 이득이라
선탐색이 실패하고, 역방향에서만 자르면 비선형 전향 패스가 제약을 위반한다.

#### 상태 제약

$g(x_k) \le 0$ 은 사정이 다르다. (8)은 $\delta u$ 에 대한 최소화이고, 상태 제약은
$\delta u$ 를 통해 **여러 단계 뒤에** 영향을 준다. 그러므로

- 역방향 패스의 QP 에 **넣을 자리가 없다**. $\delta x_k$ 는 결정변수가 아니라 전향 패스가
  주는 값이기 때문이다.
- 전향 패스에서 상태를 자르는 것은 **동역학을 위반**하는 것이다(제어와 달리 상태는 자유롭게
  고칠 수 없다).

따라서 실무의 선택지는 셋뿐이고 모두 **비용에 얹는** 방식이다.
① **벌점(penalty)**: $\ell \mathrel{+}= \rho\max(0, g)^2$. 간단하지만 $\rho$ 가 커지면
$Q_{uu}$ 가 악조건이 되고, 제약을 정확히 만족시키려면 $\rho \to \infty$ 가 필요하다.
② **증강 라그랑주**: 벌점에 승수 항을 더해 유한한 $\rho$ 로 정확한 제약 만족을 얻는다
([ALTRO](https://doi.org/10.1109/IROS40897.2019.8967788)). 외부 루프가 승수를 갱신한다.
③ **장벽(barrier)/내부점**: 실행 가능 영역 안에서만 움직인다. 초기 궤적이 실행 가능해야
한다는 요구가 로보틱스에서는 종종 비현실적이다.

**가정이 깨지는 곳**: ①·②는 중간 반복에서 제약을 **위반한 궤적**을 만든다. 충돌 회피처럼
위반이 물리적으로 의미 없는 제약에서는 그 궤적 위의 동역학·비용 평가 자체가 무의미해질 수
있다. 또 활성집합이 반복마다 바뀌면 DDP 의 2차 모델이 불연속적으로 변해 수렴이 급격히
느려진다 — 재현 과제의 카트폴에서 제약이 100 단계 중 66 단계에서 활성일 때 수렴이
느려지는 것이 그 현상이다.

### R5 — iLQR 은 국소 방법이다

(1)은 일반적으로 비볼록이다. iLQR/DDP 는 기준 궤적 주변의 2차 모델만 쓰므로, 수렴한 점은
**국소** 최적점(1차 필요조건 $Q_u = 0$ 을 만족하는 점)이고 어느 점에 가는지는 초기 추정이
정한다. 카트폴 스윙업처럼 "왼쪽으로 돌려 세우기 / 오른쪽으로 돌려 세우기 / 두 번 흔들어
세우기"가 모두 가능한 문제에서는 국소 최적해가 여러 개 있고, 비용 차이가 **수십 퍼센트**에
이른다. 재현 과제의 조건 4 가 이것을 측정한다.

**가정이 깨지는 곳**: "비용이 낮으면 더 좋은 해"라는 읽기는 같은 국소해 **안에서만** 맞다.
서로 다른 국소해를 비교할 때는 비용뿐 아니라 그 궤적이 실제로 쓸 수 있는지(제약 여유,
모델 오차에 대한 민감도)를 함께 봐야 한다. 전역성을 원하면 다중 시작(random restarts),
그래프 기반 계획과의 결합(`c6-sampling-based-planning`), 또는 볼록 완화가 필요하다.

## 증명 스케치

### R2 — DDP 는 2차, iLQR 은 1차 수렴한다 [D3]

**가설**
H1: $f, \ell, \ell_f$ 가 $C^3$ 이고 야코비안·Hessian 이 국소 리프시츠다.
H2: 국소 최적해 $u^*$ 에서 축약된 목적함수 $\hat{J}(u_{0:N-1})$ (상태를 동역학으로 제거한
것)의 Hessian $\nabla^2\hat{J}(u^*)$ 가 양정부호다.
H3: 각 반복에서 $\alpha = 1$ 이 받아들여지고 정규화 $\mu = 0$ 이다(국소 수렴 영역).

**결론** C1 (DDP): $\lVert u^{(n+1)} - u^*\rVert \le C\lVert u^{(n)} - u^*\rVert^2$.
C2 (iLQR): $\lVert u^{(n+1)} - u^*\rVert \le r\lVert u^{(n)} - u^*\rVert + O(\lVert\cdot\rVert^2)$
이고 $r < 1$ 은 버린 곡률의 상대 크기다.

**전략**: (1)을 $u$ 만의 무제약 문제로 축약하고, 역방향 패스가 그 문제의 Hessian에 대한
선형계를 **정확히** 푼다는 것을 보인 뒤, Newton 과 Gauss-Newton 의 표준 수렴 정리를 적용한다.

1. **문제를 축약한다.** $x_0$ 가 고정이고 동역학이 결정론적이므로 상태는 제어의 함수다.
   $\hat{J}(u) := J(x(u), u)$ 로 두면 (1)은 $\min_u \hat{J}(u)$ 인 무제약 문제이고
   결정변수는 $Nm$ 개다.
2. **역방향 패스가 Newton 단계를 만든다.** $\nabla\hat{J}$ 의 $k$ 번째 블록은 정확히
   $Q_{u,k}$ 이고(앞 레슨 R2 의 $\lambda = V_x$ 로 쓰면 수반 변수 계산과 같다),
   $\nabla^2\hat{J}$ 의 블록들은 (2)의 $Q_{uu}, Q_{ux}$ 와 상태 전이 행렬로 표현된다.
   DDP 의 역방향 패스는 이 **블록 3중 대각 구조를 가진 선형계를 뒤에서부터 소거하는 것**이고,
   그 결과 $\delta u = k + K\delta x$ 는 $\nabla^2\hat{J}\,\delta u = -\nabla\hat{J}$ 의
   해와 **같다**(Liao & Shoemaker 1991, Thm. 1). 즉 DDP 한 반복 = Newton 한 단계.
   (생략: 소거가 Schur 보완의 반복이고 중간 행렬이 가역이라는 보조정리 — 원 논문 §III.)
3. **Newton 의 2차 수렴.** H1·H2 아래 표준 정리(Nocedal-Wright ch.3)로
   $\lVert u^{(n+1)} - u^*\rVert \le C\lVert u^{(n)} - u^*\rVert^2$. **C1**.
4. **iLQR 은 Hessian 을 바꾼다.** iLQR 은 (2)에서 $V'_x\!\cdot\!f_{xx}$ 류 항을 버리므로
   2단계의 선형계가 $\nabla^2\hat{J}$ 가 아니라 근사 $B \approx \nabla^2\hat{J}$ 를 쓴다.
   버린 항은 $V'_x$ (즉 수반 변수)에 비례하고, $V'_x$ 는 최적점에서 **0 이 되지 않는다**
   (제약이 있는 종단 조건 때문에). 따라서 $B \ne \nabla^2\hat{J}$ 가 극한에서도 남는다 —
   이것이 최소제곱 문제의 Gauss-Newton 과 **다른** 점이다(그쪽은 잔차가 0 으로 가면
   근사 오차도 0 으로 간다).
5. **고정 Hessian 오차 → 1차 수렴.** $\delta u = -B^{-1}\nabla\hat J$ 꼴의 수정 Newton 법은
   오차 전파가 $e^{(n+1)} = (I - B^{-1}\nabla^2\hat{J})e^{(n)} + O(\lVert e^{(n)}\rVert^2)$ 이므로
   $$r = \rho\big(I - B^{-1}\nabla^2\hat{J}\big)$$
   가 수렴율이다. $r < 1$ 이면 선형 수렴하고, $r \ge 1$ 이면 **수렴하지 않는다**. **C2**.
6. **수치 확인.** 재현 과제의 진자에서 $r = 0.2592$ 가 4자리까지 안정하고 세 가지 초기
   추정에서 **같은 값**이다 — (5)가 초기값이 아니라 해의 성질임을 보인다. DDP 는 같은
   문제에서 $\lVert k^{(n+1)}\rVert/\lVert k^{(n)}\rVert^2 \approx 0.02$ 로 2차다.

**가설을 지우면 어디서 무너지는가**

- **H2(Hessian 양정부호)를 지우면**: 2단계의 선형계가 특이하거나 부정부호가 되어 Newton
  방향이 하강 방향이 아니다. 실무의 정규화 (6)이 바로 이 경우를 다루는 장치이고,
  정규화를 켜면 $\mu > 0$ 이므로 H3 이 깨져 2차 수렴이 사라진다 — **DDP 의 2차 수렴은
  정규화가 꺼진 최종 몇 반복에서만 관측된다.**
- **H3($\alpha = 1$)을 지우면**: $\alpha < 1$ 이 매 반복 유지되면 수렴율이 $\alpha$ 에
  지배된다. 재현 과제의 카트폴에서 선탐색이 수십 반복 동안 $\alpha = 0.25$ 를 고르고,
  그 결과 **iLQR 과 DDP 가 똑같이** $\lVert k\rVert$ 비 $\approx 0.46$ 의 1차 수렴을 보인다.
  즉 "DDP 를 썼는데 2차 수렴이 안 보인다"의 가장 흔한 원인은 2차 항이 아니라 **보폭**이다.
- **H1($C^3$)을 지우면**: 접촉처럼 $f$ 가 비매끄러우면 $f_{xx}$ 가 존재하지 않고
  (2)의 DDP 항이 정의되지 않는다. 완화된 접촉 모델에서는 $f_{xx}$ 가 **매우 커서**
  $Q_{uu}$ 를 쉽게 부정부호로 만들고, 그래서 접촉 문제에서는 iLQR(2차 항을 버린 쪽)이
  오히려 안정적이다(`c4-contact-implicit-hybrid`).
- **"2차 수렴이 항상 더 좋다"고 읽으면**: DDP 의 2차 항은 최적점에서 **멀 때** $Q_{uu}$ 를
  부정부호로 만드는 주범이기도 하다. 재현 과제의 진자에서 **무작위 초기 추정으로 시작하면
  DDP 는 정규화 상한에 닿아 실패하고 iLQR 은 같은 해로 수렴한다** — 2차 정보는 수렴의
  마지막 구간에서만 이득이고 초반에는 위험이다. 그래서 실무 기본값이 iLQR 이다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★, R1)** (4)의 $V_{xx} = Q_{xx} - Q_{ux}^\top Q_{uu}^{-1}Q_{ux}$ 와 구현용
$V_{xx} = Q_{xx} + K^\top Q_{uu}K + K^\top Q_{ux} + Q_{ux}^\top K$ 가 (3)을 대입하면 같은 식임을
보여라. 왜 후자를 쓰는가?
*해답 스케치*: $K = -Q_{uu}^{-1}Q_{ux}$ 를 넣으면 $K^\top Q_{uu}K = Q_{ux}^\top Q_{uu}^{-1}Q_{ux}$,
$K^\top Q_{ux} = -Q_{ux}^\top Q_{uu}^{-1}Q_{ux}$ 이므로 세 항의 합이
$-Q_{ux}^\top Q_{uu}^{-1}Q_{ux}$ 다. 이유는 앞 레슨 P1 과 같다(PSD 항의 합 대 두 양의 차).

**P2 (유도, ★★, R1)** (11)의 2차 전개에서 "$\delta x'$ 의 2차 항이 $V'_{xx}$ 와 만나면
3차 이상"이라는 주장을 정확히 쓰라. 그 다음 $f$ 가 **제어에 아핀**($f = a(x) + B(x)u$)일 때
(2)의 세 DDP 항 중 어느 것이 0 이 되는지 보여라.
*해답 스케치*: $\delta x'$ 의 2차 항은 $O(\lVert(\delta x,\delta u)\rVert^2)$ 이고
$V'_{xx}$ 와의 2차형식은 두 인자를 가지므로 교차항이 $O(\lVert\cdot\rVert^3)$ 이다.
제어 아핀이면 $f_{uu} = 0$ 이고 $f_{ux} = \partial B/\partial x$ 는 일반적으로 0 이 아니다.
$f_{xx}$ 도 $a$ 와 $B$ 의 2차 미분으로 남는다. 즉 **아핀이어도 DDP 항이 다 사라지지는 않는다**.

**P3 (증명, ★★★, R2)** 증명 스케치 5단계의 오차 전파
$e^{(n+1)} = (I - B^{-1}H)e^{(n)} + O(\lVert e^{(n)}\rVert^2)$ ($H = \nabla^2\hat{J}(u^*)$)를
유도하고, $r = \rho(I - B^{-1}H) < 1$ 이 성립하는 충분조건을 $B$ 와 $H$ 의 스펙트럼으로 쓰라.
$B = H$ 일 때 2차 수렴이 복원되는 것도 확인하라.
*해답 스케치*: $\nabla\hat{J}(u^*) = 0$ 에서 $\nabla\hat{J}(u) = H e + O(\lVert e\rVert^2)$ 로
전개하고 $u^{(n+1)} = u^{(n)} - B^{-1}\nabla\hat{J}(u^{(n)})$ 에 넣는다. 핵심 부등식:
$B, H \succ 0$ 이고 $\tfrac12 H \preceq B$ 이면 $I - B^{-1}H$ 의 고윳값이 $(-1, 1)$ 에 든다
(두 대칭 양정부호 행렬의 곱의 고윳값이 실수이고 양수라는 사실을 쓴다). $B = H$ 면 1차 항이
사라지므로 남는 것은 $O(\lVert e\rVert^2)$ 다.

**P4 (계산, ★, R1)** 스칼라 계 $x_{k+1} = x_k + \Delta(x_k^2 + u_k)$,
$\ell = \tfrac12(x^2 + u^2)$, $\ell_f = \tfrac12 c x^2$, $N = 1$, $\Delta = 0.1$, $c = 10$,
$\bar{x}_0 = 1$, $\bar{u}_0 = 0$ 에서 (2)의 모든 계수와 (3)의 $k, K$ 를 손으로 구하라.
iLQR 값과 DDP 값을 **따로** 쓰고 차이가 어디서 오는지 적어라.
*정답*: $\bar{x}_1 = 1 + 0.1(1 + 0) = 1.1$. $V'_x = c\bar{x}_1 = 11$, $V'_{xx} = c = 10$.
$f_x = 1 + 2\Delta\bar{x}_0 = 1.2$, $f_u = \Delta = 0.1$, $f_{xx} = 2\Delta = 0.2$,
$f_{ux} = f_{uu} = 0$. $\ell_x = 1$, $\ell_u = 0$, $\ell_{xx} = \ell_{uu} = 1$, $\ell_{ux} = 0$.
따라서 두 방법 모두 $Q_u = 0 + 0.1\cdot11 = 1.1$,
$Q_{uu} = 1 + 0.1\cdot10\cdot0.1 = 1.1$, $Q_{ux} = 0 + 0.1\cdot10\cdot1.2 = 1.2$ 이므로
$$k = -1, \qquad K = -1.0909090909$$
(허용오차 $10^{-9}$)로 **같다**. 차이는 $Q_{xx}$ 에만 나타난다: iLQR 은
$1 + 1.2\cdot10\cdot1.2 = 15.4$, DDP 는 $15.4 + V'_x f_{xx} = 15.4 + 11\cdot0.2 = 17.6$.
*검산*: $f_{uu} = f_{ux} = 0$ 이므로 $Q_u, Q_{uu}, Q_{ux}$ 에는 DDP 항이 없다 — 그래서 한
단계($N=1$)에서는 두 방법의 **제어가 같다**. 차이는 $V_{xx}$ 를 통해 **앞 단계로 전파될 때**
비로소 나타난다. $N = 2$ 로 늘려 직접 확인하라.

**P5 (구현, ★★, R3)** 전향 패스 (15)에서 $\alpha$ 를 $k$ 에만 곱하는 대신 $K$ 에도 곱한
버전을 구현하고, 재현 과제의 카트폴에서 두 버전의 반복 수와 최종 비용을 비교하라.
*루브릭*: ⓐ $K$ 에도 $\alpha$ 를 곱한 버전이 작은 $\alpha$ 에서 **더 나쁜** 궤적을 주는 것을
비용으로 보인다 ⓑ 그 이유를 "피드백이 없으면 비선형 동역학이 기준 궤적에서 멀어진다"로 설명한다
ⓒ 두 버전의 선탐색 수용 $\alpha$ 분포를 히스토그램으로 비교한다 ⓓ 어느 쪽도 발산하지 않게
정규화 상한을 두고, 상한에 닿으면 멈추고 보고한다.

**P6 (구현, ★★★, R3·R5)** 카트폴 스윙업에서 반복 수를 **20 이하**로 줄여라. 재현 과제의
기본 설정(영 초기 추정)은 100번대 반복이 필요하다. 허용되는 수단: 워밍 스타트(더 쉬운
문제의 해로 시작), 종단 비용 가중의 연속화(homotopy), 지평선 연장, 다중 시작.
*루브릭*: ⓐ 반복 수 20 이하를 달성하고, 그 반복 수가 **전체 계산 시간**을 줄였는지도
보고한다(워밍 스타트의 비용을 포함해야 공정하다) ⓑ 쓴 수단이 왜 통했는지를 R2 의 H3
($\alpha = 1$ 이 받아들여지는 영역에 들어갔는가)으로 설명한다 ⓒ 찾은 해가 기본 설정의
해와 같은 국소해인지 비용으로 판정한다 ⓓ 실패한 시도도 한 줄씩 적는다.

**P7 (반례, ★★, R2·R3)** "DDP 가 iLQR 보다 항상 낫다"가 틀렸음을 **두 가지 서로 다른
방식**으로 보여라: (i) DDP 는 실패하고 iLQR 은 수렴하는 초기 추정, (ii) 보폭 때문에 DDP 의
2차 수렴이 관측되지 않는 문제.
*성질 체크리스트*: (i) 은 재현 과제의 진자에 무작위 초기 제어열을 주면 바로 나온다 —
$Q_{uu}$ 가 부정부호가 되는 단계 수를 세어 보고, $V'_x\!\cdot\!f_{xx}$ 항의 노름을
$f_u^\top V'_{xx}f_u$ 와 비교하라. (ii) 는 카트폴에서 수용된 $\alpha$ 를 기록해
$\alpha < 1$ 이 유지되는 동안 두 방법의 $\lVert k\rVert$ 비가 같은지 본다. 확인할 성질:
2차 수렴은 **국소** 성질이라 정규화가 꺼지고 $\alpha = 1$ 인 영역에서만 의미가 있다.

**P8 (논문, ★★, R3·R4)** Tassa et al. 2012 §III 와 Tassa et al. 2014 §III 를 읽고
ⓐ 2012 의 정규화가 (6)의 어느 쪽이고 저자가 그 선택의 근거로 무엇을 드는지
ⓑ 2014 의 투영 Newton 이 $m=1$ 에서 이 레슨의 "자르고 피드백 행을 0 으로"와 같아지는지
ⓒ 두 논문이 **보고하지 않는** 재현 정보 3개를 쓰라.
*루브릭*: ⓐ 는 $V_{xx}$ 정규화이고 근거가 "$\mu\to\infty$ 에서 이전 궤적을 추종하는
피드백으로 간다"임을 짚으면 통과. ⓑ 는 활성집합이 1차원에서는 자르기와 일치한다는 점.
ⓒ 는 "정규화 상·하한, $\alpha$ 격자, 수렴 판정 문턱, 초기 궤적 생성법, 미분 획득 방법" 중
3개를 들면 통과. "코드가 없다"만 쓰면 미달(2012 은 코드가 공개되어 있다).

## 논문 읽기

**필독 4편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Mayne, "A second-order gradient method for determining optimal trajectories of non-linear
   discrete-time systems" (1966, Int. J. Control)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1080/00207176608921369>
   읽을 곳: 2차 전개를 세우는 절. 이 레슨 (2)와 표기를 대조하며 읽는다.
   추가 질문: ⓐ 1966년의 표기에서 이 레슨의 $Q_{uu}$ 와 $V_{xx}$ 에 해당하는 양은 무엇인가?
   ⓑ 저자가 정규화나 선탐색을 다루는가? 다루지 않는다면 그 알고리즘을 그대로 구현하면
   무엇이 깨지겠는가? ⓒ "2차 경사법(second-order gradient method)"이라는 이름이 Newton 법과
   어떤 관계인지 저자의 말로 설명되는가?
2. **Liao & Shoemaker, "Convergence in unconstrained discrete-time differential dynamic
   programming" (1991, IEEE T-AC)** — 역할: `표준(standard)`.
   <https://doi.org/10.1109/9.86943>
   읽을 곳: DDP 의 한 반복이 Newton 단계와 같다는 정리와 그 증명 구조. R2 의 2단계가 여기서 온다.
   추가 질문: ⓐ 저자들이 쓰는 가정 중 이 레슨의 H1–H3 에 없는 것은 무엇인가?
   ⓑ "unconstrained"가 제어 제약이 없다는 뜻인가, 상태 제약이 없다는 뜻인가, 둘 다인가?
   ⓒ 이 정리가 iLQR 에는 적용되지 않는 이유를 저자들의 틀로 한 문장으로 쓰라.
3. **Tassa, Erez & Todorov, "Synthesis and stabilization of complex behaviors through online
   trajectory optimization" (2012, IROS)** — 역할: `표준(standard)`.
   <https://doi.org/10.1109/IROS.2012.6386025>
   읽을 곳: §III 전체(정규화, 선탐색, 수용 검정). 이 레슨 R3 의 1차 자료다.
   추가 질문: ⓐ 저자들의 정규화 선택이 (6)의 어느 쪽이고 근거는 무엇인가?
   ⓑ 저자들이 보고하는 실시간 성능(제어 주기)은 어떤 하드웨어와 어떤 모델 복잡도에서인가?
   ⓒ 이 논문의 실험에 베이스라인이 있는가? 없다면 주장을 어떻게 검증할 수 있는가?
4. **Tassa, Mansard & Todorov, "Control-limited differential dynamic programming" (2014, ICRA)**
   — 역할: `표준(standard)`. <https://doi.org/10.1109/ICRA.2014.6907001>
   읽을 곳: 상자 제약 QP 와 투영 Newton 절, 그리고 실험의 비교 대상.
   추가 질문: ⓐ 저자들이 비교하는 "naive clamping"이 왜 실패하는지 이 레슨 R4 의 말로 쓰라.
   ⓑ 투영 Newton 의 반복 당 비용이 무제약 DDP 대비 얼마나 늘어나는가?
   ⓒ 이 방법을 **상태** 제약으로 확장할 수 없는 구조적 이유는 무엇인가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히
무엇인가 (3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지
않는가** (5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과
맞는가, 분산·시드를 보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저
의심할 가정 (9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, 전체 5분 이내, 메모리 500 MB
이하. numpy 만(scipy 불필요). 시뮬레이터는 쓰지 않는다.

**입력 데이터**: 없다. 두 계 모두 상수로 지정한다.

**계 A — 진자**(수렴 차수 측정용. 1·2차 미분이 해석적으로 나오므로 차수가 깨끗하게 보인다):
질량 $m = 1$, 길이 $\ell = 1$, 감쇠 $b = 0.1$, $g = 9.81$, **명시적 Euler** $\Delta t = 0.05$,
$$
x = (\theta, \dot\theta), \quad
  \dot{x} = \big(\dot\theta,\ (u - b\dot\theta - mg\ell\sin\theta)/(m\ell^2)\big),
$$
$N = 100$, $Q = \mathrm{diag}(1, 0.1)$, $R = [0.01]$, $Q_f = \mathrm{diag}(200, 20)$,
$x_0 = (\pi, 0)$ (아래로 매달림), $x_{\mathrm{goal}} = (0,0)$, 제어 제약 없음.
$f_{xx}$ 의 유일한 비영 성분은 $\partial^2 f_2/\partial\theta^2
= \Delta t\,(g/\ell)\sin\theta$ 다.

**계 B — 카트폴**(토크 한계와 국소성 측정용): $m_c = 1$, $m_p = 0.1$, $\ell = 0.5$,
$g = 9.81$. $\theta$ 는 **위쪽 수직선**에서 재고 $x = (q, \theta, \dot q, \dot\theta)$,
$$
\begin{bmatrix} m_c + m_p & m_p\ell\cos\theta \\ \cos\theta & \ell \end{bmatrix}
  \begin{bmatrix}\ddot q \\ \ddot\theta\end{bmatrix}
  = \begin{bmatrix} u + m_p\ell\dot\theta^2\sin\theta \\ g\sin\theta\end{bmatrix},
$$
적분은 **중점(RK2)** $\Delta t = 0.05$, $N = 100$, $Q = \mathrm{diag}(0.1, 1, 0.01, 0.01)$,
$R = [0.01]$, $Q_f = \mathrm{diag}(100, 500, 50, 50)$, $x_0 = (0, \pi, 0, 0)$,
$x_{\mathrm{goal}} = 0$, 토크 한계 $\lvert u\rvert \le \bar{u}$.

**알고리즘 명세**(수용 기준이 이것에 의존하므로 그대로 쓴다): 정규화는 (14)의 $V_{xx}$
방식, $\mu_0 = 10^{-6}$, 수용 시 $\mu \leftarrow \max(\mu/10, 10^{-9})$, 거부 시
$\mu \leftarrow 10\mu$, 상한 $10^{12}$. 선탐색은 $\alpha \in \{2^{-j}\}_{j=0}^{13}$ 을
큰 쪽부터, 수용 조건은 $J' < J$ **그리고** (16)의 $z > 0.1$(단 $-\Delta J(\alpha) \le 0$ 이면
$z$ 검정 생략). 수렴 판정은 수용된 단계의 비용 감소량이 $\varepsilon\max(1, \lvert J\rvert)$
미만. 전향 패스는 (15), $\alpha$ 는 $k$ 에만.

**수용 기준** — 네 조건을 **모두** 만족해야 통과다.

1. **두 방법이 같은 해로 간다(계 A).** $\varepsilon = 10^{-13}$, 영 초기 추정에서
   $$J^*_{\text{iLQR}} = J^*_{\text{DDP}} = 66.156792572835$$
   가 상대오차 $10^{-11}$ 이내로 일치하고, 반복 수는 iLQR **14**회, DDP **7**회다(±1 허용).
   두 경우 모두 수용된 단계의 비용이 **단조 감소**하고 $\lVert x_N\rVert_\infty < 10^{-4}$,
   $\max_k\lvert u_k\rvert = 26.889 \pm 0.01$ 이다.
2. **수렴 차수가 예측대로다(계 A).** 반복 $n$ 의 $\lVert k^{(n)}\rVert_\infty$ 를 기록하면
   ⓐ iLQR 은 마지막 5개 비 $\lVert k^{(n+1)}\rVert/\lVert k^{(n)}\rVert$ 가 모두
   $0.2592 \pm 0.001$ (1차 수렴, (5)),
   ⓑ DDP 는 같은 비가 $0.40 \to 0.085 \to 0.009 \to 0.0001$ 로 **0 으로 가고**
   $\lVert k^{(n+1)}\rVert/\lVert k^{(n)}\rVert^2$ 가 마지막 4개에서
   $[0.015,\ 0.045]$ 구간에 머문다(2차 수렴),
   ⓒ 서로 다른 초기 추정 3개(영, 그리고 $\mathcal{N}(0,1)$·$\mathcal{N}(0,25)$ 두 개)에서
   iLQR 의 비가 **같은 값** $0.2592$ 로 나온다 — 수렴율이 초기값이 아니라 해의 성질임을 확인.
3. **토크 한계를 만족하며 스윙업한다(계 B).** 영 초기 추정, $\varepsilon = 10^{-11}$ 에서
   ⓐ $\bar{u} = 30$: $J^* = 46.8449 \pm 0.01$, $\lVert x_N\rVert_\infty < 0.01$,
   포화 단계 수 $1 \pm 1$,
   ⓑ $\bar{u} = 10$: $J^* = 307.815 \pm 0.1$, $\lVert x_N\rVert_\infty < 0.05$,
   포화 단계 수 $66 \pm 3$,
   ⓒ 두 경우 모두 **모든** $k$ 에서 $\lvert u_k\rvert \le \bar{u} + 10^{-12}$ 이고 비용이
   단조 감소한다,
   ⓓ $\bar{u}$ 를 조이면 비용이 **6배 이상** 커지고 포화 단계가 1 에서 60 이상으로 늘어난다
   (제약이 궤적의 모양을 바꾼다는 증거).
4. **국소성과 DDP 의 취약성을 측정한다.** ⓐ 계 B, $\bar{u} = 10$ 에서 서로 다른 무작위 초기
   제어열 5개로 돌려 **적어도 두 개의 서로 다른 최종 비용**(1% 이상 차이)을 얻고, 그중
   하나가 영 초기 추정의 $307.815$ 보다 **낮다**는 것을 보인다(저자 구현에서는
   $J^* = 199.299$, 포화 47 단계). ⓑ 계 A 에서 DDP 를 무작위 초기 추정
   ($\mathcal{N}(0,1)$, $\mathcal{N}(0,25)$)으로 돌리면 정규화가 상한 $10^{12}$ 에 닿아
   **실패**하고, 같은 초기 추정에서 iLQR 은 조건 1 의 해로 수렴한다. ⓒ 실패한 DDP 실행에서
   $Q_{uu} \preceq 0$ 이 된 단계의 수를 세어 보고한다.

**비교 대상**: ① 계 A 의 iLQR 과 DDP 가 서로의 베이스라인이다(같은 해에 가야 한다).
② 계 A 는 $u$ 에 대한 유한차분 경사로 $\nabla\hat{J}$ 를 직접 계산해 역방향 패스의
$Q_{u,k}$ 와 $10^{-6}$ 이내로 일치하는지 확인한다(증명 스케치 2단계의 수치 검산 —
역방향 패스 구현 버그를 잡는 가장 빠른 방법이다).
③ 계 B 의 $\bar{u} = 30$ 결과가 $\bar{u} = \infty$ 결과($J^* = 46.8413$, 포화 0 단계)와
거의 같아야 한다(제약이 거의 활성이 아니므로).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 전향 패스가 `nan` 으로 발산한다 | $Q_{uu}$ 가 부정부호인데 정규화를 켜지 않았다 | 매 단계 $Q_{uu}$ 의 최소 고윳값을 출력한다. 음수면 (14)로 $\mu$ 를 올려 역방향을 다시 돈다 |
| 선탐색이 모든 $\alpha$ 에서 실패한다 | (7)을 정규화된 $\tilde{Q}_{uu}$ 로 계산했다 | $\Delta_2$ 를 $\mu = 0$ 의 $Q_{uu}$ 로 다시 계산한다. 또는 잘린 $k$ 를 쓰지 않았는지 본다 |
| 비용이 줄다가 갑자기 커진다 | $z$ 검정을 빼고 "$J' < J$"만 썼다 | 수용된 단계의 $z$ 를 기록한다. $z < 0.1$ 인 단계가 있으면 검정이 빠진 것이다 |
| $\alpha$ 가 작을 때 궤적이 **더** 나빠진다 | $K$ 에도 $\alpha$ 를 곱했다 | (15)대로 $k$ 에만 곱한다. 문제 P5 가 이 현상이다 |
| DDP 가 iLQR 보다 느리다 | 수용된 $\alpha$ 가 계속 1 보다 작다(H3 위반) | $\alpha$ 이력을 출력한다. $\alpha < 1$ 이 유지되면 2차 수렴은 관측되지 않는다 |
| 제어가 한계를 $10^{-3}$ 쯤 넘는다 | 전향 패스에서만 자르고 역방향에서 투영하지 않았다 | 역방향에서 $k$ 를 자르고 그 행의 $K$ 를 0 으로 두는지 확인한다 |
| 역방향 패스의 $Q_u$ 가 유한차분 경사와 다르다 | $\ell_{ux}$ 의 전치, 또는 $V_x$ 를 갱신하기 전에 썼다 | 비교 대상 ②를 $N = 2$ 에서 먼저 돌려 본다 |
| 진자의 $r$ 이 $0.2592$ 가 아니다 | $f_{xx}$ 를 iLQR 쪽에 **넣었거나** $\Delta t$·가중이 다르다 | 입력 상수를 다시 확인하고, $f_{xx}$ 를 0 으로 두었는지 본다 |

## 열린 문제

- **(열린 문제) 2차 정보를 안전하게 쓰는 방법** — DDP 의 2차 항은 수렴의 마지막 구간에서는
  이득이고 초반에는 발산의 원인이다(수용 기준 4ⓑ). 언제 켜고 언제 끌지에 대한 **판정
  규칙**이 없어 실무는 그냥 iLQR 을 쓴다. 현재 접근: 신뢰영역 반경에 따라 2차 항을 섞는
  방식과 [Tassa et al. 2012](https://doi.org/10.1109/IROS.2012.6386025) 의 정규화 스케줄.
  비어 있는 자리: "지금 2차 항을 켜면 $Q_{uu} \succ 0$ 이 유지된다"를 **역방향 패스 안에서**
  값싸게 판정하는 조건.
- **(열린 문제) 상태 제약을 DDP 구조 안에서 다루기** — R4 가 보인 대로 상태 제약은
  $\delta u$ 의 QP 에 들어가지 못해 비용으로 밀려난다. 증강 라그랑주([ALTRO](https://doi.org/10.1109/IROS40897.2019.8967788))는
  외부 루프를 추가해 수렴 보장을 약화시키고, 내부점은 실행 가능한 초기 궤적을 요구한다.
  비어 있는 자리: 상태 제약을 **단일 루프**로 다루면서 DDP 의 $O(N)$ 복잡도와 2차 수렴을
  함께 유지하는 전사(transcription). 이 질문은 `c4-direct-collocation-sqp` 에서 직접법 쪽의
  답과 비교된다.
- **(열린 문제) 비볼록 궤적 최적화의 전역성** — R5 의 국소성은 측정 가능한 사실이지만,
  어떤 문제가 몇 개의 국소해를 갖는지, 어느 초기 추정이 어느 해로 가는지에 대한 이론이 없다.
  현재 접근: 다중 시작의 통계적 분석, 볼록 완화(그래프 상의 Shortest-Path),
  그리고 `c6-sampling-based-planning` 의 계획기로 초기 궤적을 만드는 혼성 방식.
  비어 있는 자리: 로봇 규모에서 "이 해가 전역해와 몇 % 이내"를 말하는 인증
  (앞 레슨의 열린 문제 1 과 같은 자리다).
- **(열린 문제) 비매끄러운 동역학에서의 $f_{xx}$** — 접촉이 있으면 $f$ 가 $C^2$ 가 아니라
  (2)의 DDP 항이 정의되지 않고, 완화 모델에서는 $f_{xx}$ 가 완화 파라미터의 역수로 커져
  $Q_{uu}$ 를 부정부호로 만든다. 현재 접근: 접촉을 매끄럽게 완화하고 그 파라미터를
  연속화(annealing)하는 방식, 그리고 미분 가능한 접촉 모델.
  비어 있는 자리: 완화 파라미터와 정규화 $\mu$ 를 **함께** 고르는 원칙
  (`c4-contact-implicit-hybrid` 에서 다시 본다).

## 개념 점검

`rc quiz c4-ilqr-ddp` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c4-ilqr-ddp-quiz
questions:
  - id: q1
    type: single
    prompt: "iLQR 과 DDP 를 가르는 것은 (2)의 어느 항인가?"
    choices:
      - "$f_x^\\top V'_{xx} f_x$ 류의 항 — iLQR 은 이것을 버린다"
      - "$V'_x \\cdot f_{xx}$ 류의 항 — iLQR 은 이것을 버린다"
      - "$\\ell_{uu}$ — iLQR 은 이것을 단위행렬로 근사한다"
      - "$Q_{ux}$ — iLQR 은 피드백 이득을 쓰지 않는다"
    answer: 1
    explanation: "iLQR 은 동역학의 **2차** 미분이 들어오는 세 항($V'_x\\cdot f_{xx}$, $V'_x\\cdot f_{ux}$, $V'_x\\cdot f_{uu}$)을 버린다. $f_x^\\top V'_{xx}f_x$ 류는 1차 미분만 쓰므로 양쪽에 다 있다. 둘 다 $K$ 를 쓰며, 버린 항이 수렴 차수를 2차에서 1차로 떨어뜨린다."
    concept: { front: "iLQR 과 DDP 의 차이", back: "동역학의 2차 미분 항($V'_x \\cdot f_{xx}$ 류)을 버리면 iLQR, 유지하면 DDP. 1차 미분만 쓰는 항은 양쪽에 공통" }
  - id: q2
    type: single
    prompt: "DDP 가 국소적으로 2차 수렴하는 근거는?"
    choices:
      - "값 함수를 2차까지 전개했기 때문"
      - "역방향 패스가 축약 문제 $\\min_u \\hat{J}(u)$ 의 Newton 선형계를 정확히 푸는 것과 같기 때문"
      - "$Q_{uu}$ 가 양정부호이기 때문"
      - "선탐색이 Armijo 조건을 만족하기 때문"
    answer: 1
    explanation: "'2차까지 전개했다'는 필요하지만 충분하지 않다 — iLQR 도 값 함수를 2차까지 쓴다. 핵심은 Liao & Shoemaker 1991 의 결과다: DDP 의 역방향 소거는 $\\nabla^2\\hat{J}\\,\\delta u = -\\nabla\\hat{J}$ 를 푸는 것과 같다. iLQR 은 $\\nabla^2\\hat{J}$ 대신 고정된 근사 $B$ 를 쓰므로 수렴율이 $\\rho(I - B^{-1}\\nabla^2\\hat{J})$ 인 1차가 된다."
    concept: { front: "DDP = Newton, iLQR = Gauss-Newton", back: "DDP 역방향 패스는 축약 문제의 Newton 선형계를 정확히 푼다(Liao-Shoemaker 1991). iLQR 은 Hessian 근사라 수렴율 $\\rho(I-B^{-1}H) < 1$ 의 1차" }
  - id: q3
    type: single
    prompt: "Tassa 2012 가 $Q_{uu} + \\mu I$ 대신 $V'_{xx} + \\mu I$ 로 정규화하는 이유는?"
    choices:
      - "연산량이 적기 때문"
      - "$\\mu \\to \\infty$ 에서 피드백 $K$ 가 0 이 아닌 값으로 가 이전 궤적을 추종하는 폐루프가 되기 때문"
      - "$Q_{uu}$ 를 분해할 필요가 없어지기 때문"
      - "제어 제약을 함께 다룰 수 있기 때문"
    answer: 1
    explanation: "$Q_{uu} + \\mu I$ 는 $\\mu\\to\\infty$ 에서 $k \\to 0$ **그리고** $K \\to 0$ 이므로 전향 패스가 피드백 없는 개루프 $\\bar{u}$ 를 굴린다. $V'_{xx} + \\mu I$ 는 $K \\to -(f_u^\\top f_u)^{-1}f_u^\\top f_x$ 로 가 $\\delta x$ 를 지우는 최소제곱 피드백이 남아, 신뢰영역의 중심이 **궤적**이 된다. 그래서 같은 $\\mu$ 에서 훨씬 안전하다."
    concept: { front: "상태 정규화가 제어 정규화보다 나은 이유", back: "$\\mu\\to\\infty$ 에서 $K$ 가 살아남아 이전 궤적을 추종하는 폐루프가 된다 — 신뢰영역의 중심이 개루프 제어열이 아니라 궤적이다" }
  - id: q4
    type: truefalse
    prompt: "전향 패스에서 보폭 $\\alpha$ 는 전향 항 $k$ 와 피드백 이득 $K$ 에 모두 곱해야 한다."
    answer: false
    explanation: "$\\alpha$ 는 $k$ 에만 곱한다: $u_k = \\bar{u}_k + \\alpha k_k + K_k(x_k - \\bar{x}_k)$. $K$ 에도 곱하면 $\\alpha \\to 0$ 에서 피드백이 사라져 비선형 동역학이 기준 궤적에서 벗어나고, **작은 보폭이 더 나쁜 궤적**을 준다. $\\alpha$ 는 '기준 궤적을 얼마나 바꿀지'이지 '피드백을 얼마나 쓸지'가 아니다."
    concept: { front: "선탐색 보폭을 어디에 곱하는가", back: "$k$ 에만. $K$ 에 곱하면 작은 $\\alpha$ 에서 피드백이 사라져 궤적이 더 나빠진다" }
  - id: q5
    type: single
    prompt: "기대 감소량 비 $z = (J - J')/(-\\Delta J(\\alpha))$ 검정을 빼면 무엇이 깨지는가?"
    choices:
      - "제어 제약이 위반된다"
      - "2차 모델이 틀린 영역에서도 단계가 수용되어 정규화 $\\mu$ 가 올라가지 않고 발산한다"
      - "비용이 단조 감소하지 않는다"
      - "수렴 차수가 1차로 떨어진다"
    answer: 1
    explanation: "'$J' < J$' 만 쓰면 2차 모델이 전혀 맞지 않는 큰 단계도 운 좋게 비용이 조금 줄면 통과한다. 그러면 수용되었으므로 $\\mu$ 가 줄고, 다음 반복에서 더 큰 단계를 시도해 발산한다. $z$ 는 '모델이 예측한 만큼 실제로 줄었는가'를 재므로 모델이 틀린 영역에서 $\\mu$ 를 **올리는** 신호다 — Armijo 조건의 신뢰영역 버전이다."
    concept: { front: "$z$ 검정의 역할", back: "모델 신뢰도의 측정. 빼면 모델이 틀린 큰 단계가 수용되어 $\\mu$ 가 줄고 발산한다" }
  - id: q6
    type: single
    prompt: "상태 제약 $g(x_k) \\le 0$ 을 역방향 패스의 상자 제약 QP 에 넣을 수 없는 이유는?"
    choices:
      - "$g$ 가 비선형이기 때문"
      - "역방향 패스의 결정변수는 $\\delta u$ 뿐이고 $\\delta x$ 는 전향 패스가 주는 값이기 때문"
      - "$Q_{uu}$ 가 특이해지기 때문"
      - "상태 제약은 항등적으로 활성이기 때문"
    answer: 1
    explanation: "(8)은 $\\delta u$ 에 대한 최소화이고, 제어 상자는 그대로 $\\delta u$ 의 상자가 된다. 상태 제약은 $\\delta u$ 를 통해 **여러 단계 뒤에** 영향을 주므로 그 QP 에 들어갈 자리가 없다. 전향 패스에서 상태를 자르는 것은 동역학 위반이다. 그래서 벌점·증강 라그랑주·장벽처럼 **비용에 얹는** 길만 남는다."
    concept: { front: "제어 제약은 되고 상태 제약은 안 되는 이유", back: "역방향 QP 의 결정변수가 $\\delta u$ 뿐이다. 제어 상자는 $\\delta u$ 의 상자지만 상태 제약은 여러 단계 뒤의 결과라 넣을 자리가 없다" }
  - id: q7
    type: truefalse
    prompt: "DDP 는 2차 수렴하므로 어떤 초기 추정에서도 iLQR 보다 빠르게 수렴한다."
    answer: false
    explanation: "2차 수렴은 **국소** 성질이고 정규화가 꺼지고 $\\alpha=1$ 이 수용되는 영역에서만 나타난다. 최적점에서 멀면 $V'_x\\cdot f_{xx}$ 항이 $Q_{uu}$ 를 부정부호로 만들어 DDP 가 더 위험하다 — 재현 과제에서 무작위 초기 추정을 주면 DDP 는 정규화 상한에 닿아 실패하고 iLQR 은 같은 해로 수렴한다. 실무 기본값이 iLQR 인 이유다."
    concept: { front: "DDP 2차 수렴의 적용 범위", back: "정규화가 꺼지고 $\\alpha=1$ 인 국소 영역에서만. 멀리서는 2차 항이 $Q_{uu}$ 를 부정부호로 만드는 주범이다" }
```

## 이 단계 공부법

1. **역방향 패스를 종이에서 만든다 (100분)** — (9)→(12) 를 책을 덮고 재구성한다.
   유일한 함정은 "$\delta x'$ 의 2차 항이 $V'_x$ 와는 만나고 $V'_{xx}$ 와는 만나지 않는다"는
   한 줄이다. 이 줄을 손으로 쓰면 iLQR/DDP 의 차이가 영구히 기억된다. UA ch.10.3 을
   **같은 결과의 다른 표기**로 대조해 읽는다.
2. **$N = 1$ 로 손계산한다 (30분)** — 문제 P4 를 먼저 푼다. 한 단계에서는 두 방법의 제어가
   같고 $Q_{xx}$ 만 다르다는 것을 확인하면, 차이가 **앞 단계로 전파될 때** 생긴다는 구조가
   보인다. 코드를 쓰기 전에 이걸 해야 디버깅이 쉽다.
3. **진자를 먼저 구현한다 (120분)** — 계 A 는 $f_x, f_{xx}$ 가 해석적으로 나와 구현 오류를
   격리할 수 있다. 비교 대상 ②(유한차분 경사 대 $Q_u$)를 $N=2$ 에서 먼저 돌려 역방향 패스를
   검증하고, 그 다음 전체를 돌린다. **이 검산을 건너뛰면 나머지 전부를 의심해야 한다.**
4. **수렴 차수를 자기 손으로 뽑는다 (60분)** — $\lVert k^{(n)}\rVert$ 의 비를 표로 만든다.
   iLQR 의 $0.2592$ 가 소수 넷째 자리까지 **상수**인 것과 DDP 의 비가 0 으로 가는 것을
   나란히 보는 순간 R2 의 증명이 기억에 남는다. 초기 추정을 바꿔도 $0.2592$ 가 같은 것까지
   확인하라 — 수렴율이 **해의 성질**이라는 뜻이다.
5. **정규화를 끄고 깨뜨린다 (50분)** — 진자에 무작위 초기 제어열을 주고 $\mu = 0$ 으로
   고정해 DDP 를 돌린다. $Q_{uu}$ 의 최소 고윳값을 출력하면 음수가 되는 단계가 보인다.
   깨지는 것을 본 뒤에 (14)를 넣어야 정규화가 왜 그 형태인지 기억에 남는다.
6. **카트폴은 제약부터 넣는다 (120분)** — 무제약으로 먼저 풀고 나중에 자르면, 역방향의
   투영과 전향의 자르기를 **함께** 해야 한다는 것을 놓친다. 처음부터
   $\bar{u} = 10$ 으로 구현하고, 포화 단계가 100 중 66 개라는 것과 비용이 6배 커지는 것을
   본다. 수용된 $\alpha$ 를 로그로 남겨라 — $\alpha = 0.25$ 가 수십 반복 유지되는 것이
   "왜 20 반복이 아니라 140 반복인가"의 답이다.
7. **국소성을 측정한다 (40분)** — 무작위 초기 제어열 5개로 돌려 최종 비용을 표로 만든다.
   영 초기 추정이 **최선이 아니라는** 것을 보는 것이 이 레슨에서 가장 실무적인 교훈이다.
8. **논문은 구현 순서대로 읽는다 (180분)** — Mayne 1966(원형) → Liao & Shoemaker 1991
   (왜 2차인가) → Tassa 2012(어떻게 돌아가게 하는가) → Tassa 2014(제약). 2012 와 2014 는
   **코드를 쓴 뒤에** 읽으면 §III 의 한 줄 한 줄이 자기가 겪은 버그로 읽힌다.
   논문당 1페이지 노트는 **반드시** 쓴다.
9. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제" 넷 중 하나를 골라 한 문단으로 쓴다.
   둘째(상태 제약)는 바로 다음 레슨 `c4-direct-collocation-sqp` 가 다른 답을 내놓는다.

**통과 기준**: 백지에서 (2)와 (4)를 유도할 수 있고, "DDP = Newton, iLQR = Gauss-Newton"을
축약 문제 $\hat{J}(u)$ 로 설명할 수 있고, 정규화 두 방식의 차이를 $\mu\to\infty$ 극한으로
말할 수 있고, 재현 과제의 네 조건을 모두 만족하는 코드를 갖고 있고, 논문 4편의 노트가 있다.
