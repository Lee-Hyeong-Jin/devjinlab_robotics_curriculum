---
id: c3-cbf-safety-filter
title: CBF·CLF 안전 필터
summary: >-
  제어 장벽 함수(control barrier function)가 안전 집합의 전진 불변성을 어떻게 보장하는지
  비교 보조정리로 증명하고, 최소 개입 QP 필터의 닫힌 형태를 KKT 조건에서 유도한다. 상대 차수가
  2 이상인 제약을 다루는 고차(지수) CBF 를 구성하고, 입력 제약이 들어오면 보장이 **어디서
  무너지는지**를 수치로 측정한다. 마지막으로 CBF-QP 가 만들어 내는 원하지 않는 평형점을 본다.
objectives:
  - CBF 조건에서 안전 집합의 전진 불변성을 비교 보조정리로 증명 스케치할 수 있다.
  - 단일 제약 최소 개입 QP 의 닫힌 해를 KKT 조건에서 유도하고 비활성 구간에서 명목 제어와 일치함을 보일 수 있다.
  - 상대 차수 2 인 제약에 대해 지수 CBF 사슬을 구성하고 이중 적분기의 명시적 입력 상한을 쓸 수 있다.
  - 입력 제약이 있을 때 QP 가 실현불가능해지는 영역을 수치로 측정하고 그 조건을 식으로 쓸 수 있다.
  - CBF-QP 가 목표 아닌 평형점을 만드는 기구를 설명할 수 있다.
prerequisites: [c3-lyapunov-stability]
difficulty: 5
estimated_minutes: 480
tags: [nonlinear-control, control-barrier-function, safety, quadratic-program, research]
activities:
  - id: c3-cbf-safety-filter-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c3-cbf-safety-filter-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 135
  - id: c3-cbf-safety-filter-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 150
  - id: c3-cbf-safety-filter-reproduction
    kind: reproduction
    title: 재현 과제 — 이중 적분기 안전 필터와 실현가능성 경계 (R2)
    estimated_minutes: 90
  - id: c3-cbf-safety-filter-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Khalil, Nonlinear Systems (3rd ed., 2002)"
    kind: book
    note: ch.3.4 (비교 보조정리) — R1 증명의 도구. (공식 URL 미확인)
  - title: "Boyd & Vandenberghe, Convex Optimization"
    url: https://web.stanford.edu/~boyd/cvxbook/
    kind: book
    note: ch.5 (쌍대성과 KKT) — R2 의 닫힌 해를 유도하는 데 쓴다. 전문 PDF 무료.
  - title: "CVXPY"
    url: https://www.cvxpy.org/
    kind: code
    note: 재현 과제에서 닫힌 해를 대조할 QP 솔버. 아무 솔버나 쓴다.
papers:
  - id: ames2017-cbf
    required: true
    role: seminal
    note: "§II, §III"
  - id: ames2019-cbf-survey
    required: true
    role: survey
  - id: nguyen2016-ecbf
    required: true
    role: standard
---

# CBF·CLF 안전 필터

## 전제와 기호

이 모듈의 앞선 레슨들은 모두 **목표에 수렴하는 것**을 다뤘다. 이 레슨은 다른 요구를 다룬다:
**절대 들어가면 안 되는 영역이 있다.** 수렴과 안전은 서로 다른 성질이고(안전은 불변성이지
안정성이 아니다), 실무에서는 "성능을 내는 제어기" 와 "안전을 지키는 필터" 를 분리해 설계한다.
이 분리를 가능하게 하는 것이 제어 장벽 함수(CBF)와 그 QP 필터다.

전제: `c3-lyapunov-stability` 의 비교 보조정리와 불변 집합, 볼록 최적화의 KKT 조건
(`r0-convex-optimization`), 리 미분과 상대 차수(`c3-feedback-linearization` 의 R2).

| 기호 | 뜻 |
|---|---|
| $\dot x = f(x) + g(x)u$ | 입력에 아핀, $f, g$ 국소 Lipschitz |
| $h : \mathbb{R}^n\to\mathbb{R}$ | 안전 함수. 안전 집합은 $\mathcal{C} = \{x : h(x)\ge0\}$ |
| $\alpha$ | 확장 class-$\mathcal{K}$ 함수($\alpha(0)=0$, 강증가, 정의역 $\mathbb{R}$) |
| $L_fh, L_gh$ | $\nabla h^\top f$, $\nabla h^\top g$ (후자는 행벡터) |
| $u_{\text{nom}}(x,t)$ | 명목 제어(성능 제어기) |
| $u^\star$ | 필터를 통과한 제어 |
| $\psi_0, \psi_1,\dots$ | 고차 CBF 사슬 $\psi_0 = h$, $\psi_{i+1} = \dot\psi_i + \alpha_{i+1}(\psi_i)$ |
| $u_{\max}$ | 입력 크기 한계 |

달리는 예는 이중 적분기 $\ddot x = u$ 와 벽 제약 $x \le x_{\max} = 1$ 이다. 이 예가 중요한 이유는
$h = x_{\max} - x$ 가 **상대 차수 2** 라서 ($L_gh = 0$) 1차 CBF 이론이 그대로 쓰이지 않는다는
점이다 — 로봇의 위치·관절 한계 제약이 모두 이 모양이다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (CBF 와 전진 불변성) [D3]** — $h$ 가 $\mathcal{C}$ 의 경계에서
  $\nabla h \ne 0$ 이고, 확장 class-$\mathcal{K}$ 함수 $\alpha$ 와 국소 Lipschitz 제어
  $u(x)$ 가
  $$
  \dot h(x) = L_fh(x) + L_gh(x)u(x) \;\ge\; -\alpha\big(h(x)\big) \tag{1}
  $$
  를 만족하면 $\mathcal{C}$ 는 **전진 불변**이다: $x(0)\in\mathcal{C} \Rightarrow x(t)\in\mathcal{C}$
  (해가 존재하는 동안). 증명은 비교 보조정리 한 줄이다.
- **R2 (최소 개입 QP 필터와 그 닫힌 해) [D2]** — 제약이 하나이고 입력 제약이 없으면
  $$
  u^\star = \arg\min_u \tfrac12\lVert u - u_{\text{nom}}\rVert^2
    \;\;\text{s.t.}\;\; L_fh + L_ghu + \alpha(h) \ge 0 \tag{2}
  $$
  의 해가 **닫힌 형태**로 나온다:
  $$
  u^\star = u_{\text{nom}} + \frac{\big[-\lambda\big]_+}{\lVert L_gh\rVert^2}\,L_gh^\top,
    \qquad \lambda := L_fh + L_ghu_{\text{nom}} + \alpha(h), \tag{3}
  $$
  즉 제약이 **비활성이면 ($\lambda \ge 0$) 명목 제어를 정확히 통과시키고**, 활성이면
  $L_gh$ 방향으로 최소한만 민다. 수치 확인: 무작위 1500개 사례에서 (3)과 QP 솔버의 차가
  $6.1\cdot10^{-7}$ (솔버 허용오차), 비활성 구간의 $\lVert u^\star - u_{\text{nom}}\rVert = 0$.
- **R3 (고차·지수 CBF) [D2]** — $L_gh \equiv 0$ 이면 (1)을 쓸 수 없다. 사슬
  $\psi_0 = h$, $\psi_1 = \dot\psi_0 + \alpha_1(\psi_0)$, 제약 $\dot\psi_1 + \alpha_2(\psi_1)\ge0$
  을 쓰면 $\mathcal{C}_0\cap\mathcal{C}_1$ ($\mathcal{C}_i = \{\psi_i\ge0\}$)이 전진 불변이다.
  이중 적분기·선형 $\alpha_i$ 에 대해 이 제약은 **명시적 입력 상한**이 된다:
  $$
  u \;\le\; -(\alpha_1+\alpha_2)\,\dot x + \alpha_1\alpha_2\,(x_{\max}-x). \tag{4}
  $$
- **R4 (실현가능성과 입력 제약) [D2]** — (2)는 $L_gh \ne 0$ 이면 항상 가해다. 그러나
  ⓐ $L_gh = 0$ 이고 $L_fh + \alpha(h) < 0$ 이면 **실현불가능**하고, ⓑ $\lVert u\rVert\le u_{\max}$
  를 넣으면 (4)의 상한이 $-u_{\max}$ 보다 작아지는 영역에서 제약을 만족시킬 수 없다. 수치
  확인($\alpha_1=\alpha_2=3$, $x_{\max}=1$, 명목 $u\equiv10$): $u_{\max}=2$ 에서 189개 중
  95개가 포화되고 **안전이 깨진다**(최악 $\min_t h = -0.138$), $u_{\max}=5$ 에서는 183개 중 2개가
  포화되지만 위반은 없고, $u_{\max}=20$ 에서는 포화가 없다.
- **R5 (CBF-QP 가 만드는 원하지 않는 평형점) [D1]** — CBF-QP 로 CLF 기반 제어기를 필터링하면,
  장벽 제약이 활성인 경계에서 **목표가 아닌 점근 안정 평형점**이 생길 수 있다
  (Reis, Aguiar & Tabuada 2021). 안전은 지켜지지만 작업은 끝나지 않는다 — 안전과 성능을 분리한
  대가다.

## 유도

### R2 — 최소 개입 QP 의 닫힌 해

(2)는 변수 $u \in \mathbb{R}^m$, 제약 1개의 볼록 QP 다. 라그랑지안을

$$
\mathcal{L}(u,\mu) = \tfrac12\lVert u - u_{\text{nom}}\rVert^2
  - \mu\big(L_fh + L_ghu + \alpha(h)\big), \qquad \mu \ge 0
$$

로 쓰면 KKT 조건은 ⓐ 정류성 $\nabla_u\mathcal{L} = u - u_{\text{nom}} - \mu L_gh^\top = 0$,
ⓑ 상보성 $\mu\big(L_fh+L_ghu+\alpha(h)\big) = 0$, ⓒ 가능성, ⓓ $\mu\ge0$ 이다.

**1단계.** ⓐ 에서 $u = u_{\text{nom}} + \mu L_gh^\top$ — 해는 반드시 $L_gh$ 방향으로만
움직인다(목적함수가 유클리드 거리이므로).

**2단계.** 이것을 제약식에 넣으면

$$
L_fh + L_gh\big(u_{\text{nom}} + \mu L_gh^\top\big) + \alpha(h)
  = \lambda + \mu\lVert L_gh\rVert^2,
$$

여기서 $\lambda := L_fh + L_ghu_{\text{nom}} + \alpha(h)$ 는 **명목 제어의 여유**다.

**3단계 (두 경우).** $\lambda \ge 0$ 이면 $\mu = 0$ 이 ⓑ·ⓒ·ⓓ 를 모두 만족하므로
$u^\star = u_{\text{nom}}$ — **명목 제어를 그대로 통과**시킨다. $\lambda < 0$ 이면 $\mu = 0$ 은
제약을 위반하므로 ⓑ 에서 제약이 등식으로 활성이어야 하고
$\mu = -\lambda/\lVert L_gh\rVert^2 > 0$. 둘을 합치면 (3)이다.

**4단계 (연속성).** $\lambda$ 는 $x$ 의 연속 함수이고 $[\cdot]_+$ 는 Lipschitz 이므로, $L_gh$ 가
0 에서 떨어져 있는 영역에서 $u^\star(x)$ 는 Lipschitz 다 — R1 이 요구하는 "국소 Lipschitz 제어"
조건이 이렇게 충족된다. **$\lVert L_gh\rVert \to 0$ 에서는 (3)의 분모가 0 이 되어 이 성질이
깨진다**(R4 의 ⓐ).

**수치 확인**: 입력 차원 1–3, 무작위 $(u_{\text{nom}}, L_gh, L_fh, \alpha(h))$ 1500개에서
(3)과 CLARABEL QP 해의 최대 성분 차가 $6.1\cdot10^{-7}$ 이고, $\lambda>0$ 인 사례에서
$\lVert u^\star - u_{\text{nom}}\rVert_\infty$ 가 **정확히 0** 이다.

### R3 — 상대 차수 2 인 제약: 지수 CBF

이중 적분기 $\dot x_1 = x_2$, $\dot x_2 = u$ 와 $h = x_{\max}-x_1$ 을 보자.
$\nabla h = (-1, 0)$ 이므로 $L_gh = 0$ — (1)의 좌변에 $u$ 가 **나타나지 않는다**. 1차 CBF 로는
아무 제어도 제약을 바꿀 수 없다.

**1단계 (사슬 만들기).** $\psi_0 := h = x_{\max}-x_1$ 에서 $\dot\psi_0 = -x_2$ 이고, 1차
조건이 요구하는 $\dot\psi_0 + \alpha_1(\psi_0) \ge 0$ 을 **새 안전 함수**로 올린다:

$$
\psi_1 := \dot\psi_0 + \alpha_1(\psi_0) = -x_2 + \alpha_1(x_{\max}-x_1). \tag{5}
$$

**2단계 ($u$ 가 나타나는 조건).** 이제 $\dot\psi_1$ 을 계산하면 $u$ 가 등장한다:

$$
\dot\psi_1 = -u - \alpha_1'(\psi_0)\,x_2 \;\xrightarrow{\ \alpha_i(s)=\alpha_is\ }\; -u - \alpha_1 x_2.
$$

따라서 2차 조건 $\dot\psi_1 + \alpha_2(\psi_1) \ge 0$ 은

$$
-u - \alpha_1x_2 + \alpha_2\big(-x_2 + \alpha_1(x_{\max}-x_1)\big) \ge 0
  \iff u \le -(\alpha_1+\alpha_2)x_2 + \alpha_1\alpha_2(x_{\max}-x_1),
$$

즉 (4)다. **제약이 입력의 상한 하나로 환원**되므로 필터는
$u^\star = \min\{u_{\text{nom}},\ \text{상한}\}$ 이라는 한 줄이 된다(스칼라 입력에서 (3)과 동치).

**3단계 (불변성의 범위).** 2차 조건은 $\psi_1 \ge 0$ 을 지키고, $\psi_1\ge0$ 은 다시 (5)로
$\dot\psi_0 \ge -\alpha_1(\psi_0)$ 를 주어 R1 에 의해 $\psi_0 \ge 0$ 을 지킨다. 즉 불변인 것은
$\mathcal{C}_0\cap\mathcal{C}_1$ 이고, **초기 상태가 두 집합 모두에 있어야 한다**.
$x$ 가 벽에서 멀어도 **속도가 너무 크면** $\psi_1 < 0$ 이라 보장 밖이다 — 이것이 고차 CBF 의
실질적 제약이고, $\alpha_1\alpha_2$ 는 "제동 거리" 를 정하는 숫자다.

**수치 확인**: $\alpha_1 = \alpha_2 = 3$, $x_{\max}=1$, 명목 제어
$u_{\text{nom}}(t) = c + A\sin\omega t$ (무작위 $c\in[-2,4]$, $A\in[0.5,5]$, $\omega\in[0.5,4]$),
$\mathcal{C}_0\cap\mathcal{C}_1$ 안의 무작위 초기조건 295개를 $T=12$, $\Delta t = 10^{-4}$ 로
적분하면 **최악의 $\min_t h = +1.4\cdot10^{-13}$** (위반 없음)이고, 제약이 비활성인 시각에서
$\lvert u^\star - u_{\text{nom}}\rvert$ 의 최댓값이 **정확히 0** 이다.

**가정이 깨지는 곳**: $\alpha_i$ 를 키우면 상한이 느슨해져 명목 제어를 덜 건드리지만
$\mathcal{C}_1$ 이 좁아져(속도 허용 범위가 줄어) **초기 조건이 보장 밖으로 나가기 쉬워진다**.
반대로 작게 하면 보장 영역은 넓어지지만 필터가 보수적이 된다. 이 교환에는 자동적인 정답이
없고, 입력 한계가 있으면 더 나빠진다(R4).

### R4 — 실현가능성: 두 가지 방식으로 깨진다

**ⓐ 제어가 닿지 않는 방향.** (2)의 제약은 $L_gh u \ge -L_fh - \alpha(h)$ 다. $L_gh = 0$ 이면
좌변이 $u$ 와 무관하므로, $L_fh + \alpha(h) < 0$ 인 상태에서는 **어떤 $u$ 로도** 제약을 만족할 수
없다. 고차 CBF(R3)가 이 문제를 사슬로 미루는 방법이고, 사슬의 마지막 단계에서도 $u$ 가 나타나지
않으면(가제어성 부족) 그 제약은 애초에 불가능하다.

**ⓑ 입력 한계.** $\lvert u\rvert \le u_{\max}$ 를 (2)에 더하면 실현가능 집합이
$\{u : L_ghu \ge -L_fh-\alpha(h)\} \cap \{\lVert u\rVert_\infty \le u_{\max}\}$ 로 좁아지고,
이중 적분기에서는 (4)의 상한이 $-u_{\max}$ 보다 작아지는 순간 교집합이 빈다:

$$
-(\alpha_1+\alpha_2)x_2 + \alpha_1\alpha_2(x_{\max}-x_1) < -u_{\max}. \tag{6}
$$

(6)이 성립하면 "최대 제동" 으로도 제약을 만족할 수 없다. **수치 확인**(명목 $u\equiv10$,
$\mathcal{C}_0\cap\mathcal{C}_1$ 안에서 출발, $x_2(0)\in[0,2]$):

| $u_{\max}$ | 포화(실현불가) 발생 | 최악 $\min_t h$ |
|---|---|---|
| 2 | 189 중 **95** | $-0.138$ (**안전 위반**) |
| 5 | 183 중 2 | $0.0000$ |
| 20 | 188 중 0 | $0.0000$ |

$u_{\max}=2$ 에서 보듯 **포화가 생기면 보장이 사라진다**. 처방은 세 갈래다: ⓘ 입력 제약을
고려해 안전 집합을 **미리 줄인다**(입력 제약 CBF), ⓘⓘ 백업 제어기(backup controller)의 궤적으로
불변 집합을 수치적으로 구성한다(backup CBF), ⓘⓘⓘ $\alpha_i$ 를 입력 한계에 맞춰 낮춘다
(대가: 보수적 필터). 어느 쪽도 공짜가 아니며, 이것이 이 레슨의 열린 문제다.

## 증명 스케치

### R1 — CBF 조건이 전진 불변성을 주는 이유

**가설** H1: $\mathcal{C} = \{h\ge0\}$ 이고 $h$ 는 $C^1$, $\partial\mathcal{C}$ 에서 $\nabla h\ne0$.
H2: $u(\cdot)$ 가 국소 Lipschitz 이고 (1)이 $\mathcal{C}$ 의 근방에서 성립. H3: $\alpha$ 가
국소 Lipschitz 인 확장 class-$\mathcal{K}$.
**결론** C: $x(0)\in\mathcal{C} \Rightarrow x(t)\in\mathcal{C}$ (해의 최대 존재 구간에서).

**전략**: 비교 보조정리. $h$ 를 따라가는 스칼라 ODE 와 비교해 **그 해가 0 아래로 내려가지
못한다**는 것만 보인다.

1. $\eta(t) := h(x(t))$ 로 두면 H2 로 $\dot\eta \ge -\alpha(\eta)$ (거의 모든 $t$ 에서).
2. 비교 ODE $\dot y = -\alpha(y)$, $y(0) = \eta(0) \ge 0$ 를 생각한다. H3 로 해가 유일하게
   존재하고, $\alpha(0)=0$ 이므로 $y\equiv0$ 이 해다. 따라서 $y(0)\ge0$ 인 해는 모든 $t$ 에서
   $y(t)\ge0$ 이다(유일성으로 0 을 **가로지를 수 없다**).
3. 비교 보조정리(Khalil Lemma 3.4)로 $\eta(t) \ge y(t) \ge 0$. 즉 $h(x(t))\ge0$.
4. 따라서 $x(t)\in\mathcal{C}$ 다. (경계에서의 $\nabla h\ne0$ 은 $\mathcal{C}$ 가 정칙 집합이어서
   "경계에 닿는 것" 이 "넘어가는 것" 과 구분된다는 기하적 전제다 — Nagumo 조건과 연결된다.)

**가설을 지우면**: H3 에서 $\alpha$ 의 Lipschitz 성을 빼면 2단계의 유일성이 깨져 $y$ 가 0 을
가로지를 수 있고($\dot y = -\sqrt{y}$ 류) 결론이 거짓이 된다. H2 의 Lipschitz 제어를 빼면 해의
존재·유일성이 없어 1단계부터 성립하지 않는다 — **QP 필터의 해가 Lipschitz 인지**(R2 의 4단계)가
이 때문에 중요하다. 또 H1 의 $\nabla h \ne 0$ 을 빼면 $h$ 가 경계에서 접하는 퇴화 집합이 생겨
불변성이 깨질 수 있다. 마지막으로 **이 정리는 안정성을 주지 않는다**: $\mathcal{C}$ 안에
머문다는 것뿐이고, 목표에 도달하는지는 전혀 말하지 않는다(R5).

생략한 기술적 단계: 비교 보조정리의 증명과 해의 전진 완전성(forward completeness) 가정.
Khalil Lemma 3.4, Ames et al. 2017 §II.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R2)** 제약이 **두 개**인 경우 (2)의 KKT 조건을 쓰고, 두 제약이 동시에 활성일
때 해를 $L_gh_1, L_gh_2$ 로 표현하라. 두 제약의 기울기가 평행하고 서로 모순이면 어떻게 되는가?
*해답 스케치*: $u = u_{\text{nom}} + \mu_1L_gh_1^\top + \mu_2L_gh_2^\top$ 를 두 등식에 넣으면
$2\times2$ 선형계가 되고 Gram 행렬 $[L_gh_iL_gh_j^\top]$ 의 가역성이 조건이다. 평행·모순이면
그 행렬이 특이해지고 실현가능 집합이 비어 QP 가 infeasible 이 된다.

**P2 (유도, ★★, R3)** 상대 차수 3 인 제약에 대해 사슬을 한 단계 더 쌓고($\psi_2$), 선형
$\alpha_i(s) = \alpha_is$ 에서 전체 조건이 $h$ 와 그 도함수들의 선형 결합으로 쓰임을 보여라.
그 결합의 계수를 특성 다항식의 근으로 읽는 방법을 쓰라.
*해답 스케치*: $\psi_2 = \dot\psi_1 + \alpha_2\psi_1$ 를 전개하면
$h^{(3)} + (\alpha_1+\alpha_2+\alpha_3)\ddot h + \dots \ge 0$ 꼴이 되고, 괄호의 계수는
$\prod(s+\alpha_i)$ 의 계수다. 즉 $\alpha_i$ 는 "안전 여유의 극점" 이다(Nguyen–Sreenath 의
exponential CBF 가 이 이름을 쓰는 이유).

**P3 (계산, ★, R3·R4)** $\alpha_1=\alpha_2=3$, $x_{\max}=1$ 에서 ⓐ $x=(0,1)$ 일 때 (4)의 입력
상한, ⓑ $x=(0.9,\ 1.5)$ 일 때 같은 값, ⓒ ⓑ 의 상태에서 (6)이 깨지지 않을 최소 $u_{\max}$ 를
구하라.
*정답*: ⓐ $-(3+3)(1) + 9(1-0) = 3$ ⓑ $-6(1.5) + 9(0.1) = -8.1$
ⓒ $u_{\max} \ge 8.1$ (허용오차 $10^{-9}$). 검산: ⓑ 의 상태는 $\psi_1 = -1.5+3(0.1) = -1.2 < 0$
이므로 이미 $\mathcal{C}_1$ **밖**이다 — 보장 영역 밖에서는 상한이 음수가 되는 것이 정상이다.

**P4 (구현, ★★, R2·R3)** (3)의 닫힌 해와 QP 솔버를 같은 입력에서 대조하고, 이중 적분기
안전 필터를 구현해 재현 과제의 네 조건을 통과시켜라. 추가로 $\alpha_1=\alpha_2 \in \{1,3,10\}$
에서 ⓐ 명목 제어와의 평균 편차 ⓑ $\mathcal{C}_1$ 의 면적을 표로 만들라.
*루브릭*: ⓐ $\alpha$ 가 커지면 편차가 줄고 ⓑ 보장 영역이 좁아지는 교환을 **수치로** 보인다
ⓒ 비활성 구간의 편차가 정확히 0 임을 확인한다 ⓓ 적분 $\Delta t$ 를 절반으로 줄여 $\min_t h$ 의
부호가 바뀌지 않는지 확인한다.

**P5 (반례, ★★★, R4·R5)** ① 입력 제약 때문에 안전이 깨지는 초기조건을 하나 찾아 (6)으로
설명하고, ② CBF-QP 가 목표 아닌 평형점을 만드는 예를 구성하라(장벽 제약이 활성인 상태에서
필터된 제어가 0 이 되는 점).
*성질 체크리스트*: ① 포화 시각과 그때의 (6) 좌변 값을 함께 보고 ② 평형점에서
$f + gu^\star = 0$ 이고 $h = 0$ 또는 $\psi_1 = 0$ 임을 확인하고, 그 점이 **점근 안정**인지
선형화로 판정한다. "안전은 지켜지지만 작업이 끝나지 않는다" 를 궤적으로 보이면 완성.

**P6 (논문, ★★, R1·R4)** Ames et al. 2019 서베이에서 ⓐ 확장 class-$\mathcal{K}$ 를 쓰는
이유(class-$\mathcal{K}$ 와 무엇이 다른가), ⓑ 모델 오차가 있을 때의 강건 CBF 정식화,
ⓒ 입력 제약을 다루는 절의 처방들을 각각 3문장 이내로 정리하라. 그중 이 레슨의 재현 과제로
검증 가능한 것을 하나 고르고 그 검증 절차를 쓰라.
*루브릭*: "확장은 $h<0$ 에서도 정의되어 집합 **밖에서 복귀**를 말할 수 있게 한다" 를 짚으면
통과. 강건 CBF 를 "최악의 외란에 대해 여유를 깎는 것" 으로 요약하면 가점.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Ames, Xu, Grizzle & Tabuada, "Control barrier function based quadratic programs for safety
   critical systems" (2017, IEEE T-AC; arXiv 2016)** — 역할: `원전(seminal)`.
   <https://arxiv.org/abs/1609.06408>
   §II·§III 가 이 레슨의 R1·R2 다.
   추가 질문: ⓐ 저자들이 CLF 와 CBF 를 **같은 QP 안에** 넣을 때 안전과 성능의 우선순위를 어떻게
   표현하는가(완화 변수의 역할)? ⓑ QP 해의 Lipschitz 연속성은 어디서 보장되고, 그 가정이 깨지는
   상태는 무엇인가?
2. **Ames, Coogan, Egerstedt, Notomista, Sreenath & Tabuada, "Control barrier functions: theory
   and applications" (2019, ECC)** — 역할: `서베이(survey)`. <https://arxiv.org/abs/1903.11199>
   추가 질문: ⓐ 서베이가 열린 문제로 꼽는 것 중 입력 제약·실현가능성에 관한 항목을 요약하라.
   ⓑ 안전 집합을 **학습**으로 얻는 접근의 보장은 무엇에 대한 것인가?
3. **Nguyen & Sreenath, "Exponential control barrier functions for enforcing high relative-degree
   safety-critical constraints" (2016, ACC)** — 역할: `표준(standard)`.
   <https://doi.org/10.1109/ACC.2016.7524935>
   추가 질문: ⓐ "exponential" 이 가리키는 것은 무엇의 지수적 성질인가? ⓑ 극점 선택
   ($\alpha_i$)이 보장 영역과 보수성에 주는 영향을 이 레슨의 (4)로 다시 쓰라.

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 10분 이내, numpy + QP 솔버 하나(조건 1
대조용). 대상은 이중 적분기 $\ddot x = u$ 와 벽 $x \le 1$ 이고 입력 데이터는 없다.

**수용 기준 (네 조건 모두)**

1. **닫힌 해 대조**: 입력 차원 1–3, 무작위 $(u_{\text{nom}}, L_gh, L_fh, \alpha(h))$ $10^3$ 개에서
   (3)과 QP 솔버의 해가 성분별 $10^{-5}$ 이내로 일치(참조 $6.1\cdot10^{-7}$), 그리고
   $\lambda>0$ (비활성)인 사례 전부에서 $\lVert u^\star - u_{\text{nom}}\rVert_\infty = 0$
   (**정확히** 0 — 부동소수 비교가 아니라 분기로 통과해야 한다).
2. **제약 위반 0**: $\alpha_1=\alpha_2=3$, $\mathcal{C}_0\cap\mathcal{C}_1$ 안의 무작위 초기조건
   $\ge 250$ 개와 무작위 정현 명목 제어에 대해 $T=12$, $\Delta t \le 10^{-4}$ 로 적분하고
   $\min_t h \ge -10^{-9}$ (참조: 최악 $+1.4\cdot10^{-13}$).
3. **비활성 구간의 투명성**: 같은 실험에서 제약이 비활성인 모든 시각
   ($u_{\text{nom}} \le$ (4)의 상한 $- 10^{-6}$)에서 $\lvert u^\star - u_{\text{nom}}\rvert = 0$.
4. **입력 제약의 경계**: $\lvert u\rvert \le u_{\max}$ 를 넣고 $u_{\max}\in\{2,5,20\}$ 에 대해
   포화 발생 비율과 최악 $\min_t h$ 를 보고한다. $u_{\max}=2$ 에서 **안전 위반이 발생해야 하고**
   (참조: 189개 중 95개 포화, 최악 $\min_t h = -0.138$), $u_{\max}=20$ 에서는 포화가 0 이어야
   한다. 위반이 일어난 시각에 (6)의 좌변 값을 함께 출력해 원인을 확인한다.

**비교 대상**: ⓐ 명목 제어만 쓴 경우(필터 없음) — 같은 초기조건에서 벽을 넘어야 한다
(필터가 실제로 무엇을 막는지 보여주는 대조군) ⓑ 단순 클리핑 $u = \min(u_{\text{nom}}, 0)$ —
속도가 이미 큰 경우 벽을 넘는다는 것을 보인다 ⓒ 조건 1·2·4 의 참조 수치.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| $\min_t h$ 가 $-10^{-6}$ 수준으로 작게 음수 | 적분 오차(제약은 연속시간 조건) | $\Delta t$ 를 절반으로 줄여 위반이 비례해 줄는지 본다 — 줄면 적분 문제다 |
| 조건 3 이 실패(비활성에서도 편차) | $\min$ 을 쓰지 않고 항상 상한으로 사영했다 | $\lambda \ge 0$ 분기를 명시적으로 넣는다((3)의 $[\cdot]_+$) |
| 위반이 큰데 $\Delta t$ 와 무관 | $\mathcal{C}_1$ 밖에서 출발했다(초기 속도가 과도) | 초기조건 생성에서 $\psi_1 \ge 0$ 를 **반드시** 검사한다 |
| $u_{\max}=20$ 에서도 포화가 생긴다 | (4)의 부호 또는 $\alpha_1\alpha_2$ 항 오류 | $x=(0,1)$ 에서 상한이 3 인지 손으로 확인한다(P3 ⓐ) |
| QP 솔버와 닫힌 해가 $10^{-3}$ 수준으로 다르다 | 솔버 허용오차 또는 제약 부호 반대 | $L_gh$ 를 양수 스칼라로 고정한 단순 사례부터 대조한다 |

## 열린 문제

- **(열린 문제) 입력 제약 아래의 실현가능성** — (6)이 보여준 것처럼 포화가 생기면 보장이
  사라진다. 현재 접근: 백업 제어기의 궤적으로 불변 집합을 구성하는
  [backup CBF (Chen, Jankovic, Santillo & Li 2021)](https://doi.org/10.1109/CDC45484.2021.9683111),
  입력 제약을 포함한 CBF 합성. 비어 있는 자리: 실시간 계산량과 보장 영역 크기의 교환을
  정량화하는 일반 방법 — 백업 궤적을 길게 적분할수록 영역은 커지지만 매 스텝 비용이 커진다.
- **(열린 문제) CBF-QP 가 만드는 평형점과 작업 완수** — 안전 필터는 경계에서 원하지 않는
  점근 안정 평형점을 만들 수 있다
  ([Reis, Aguiar & Tabuada 2021](https://doi.org/10.1109/LCSYS.2020.3004797)). 현재 접근:
  장벽을 바꾸거나(경계 모양 설계) 계획 단계에서 안전을 반영. 비어 있는 자리: **안전과 수렴을
  동시에** 보장하는 구성적 설계(일반 조건은 아직 없다).
- **(열린 문제) 학습된 안전 함수의 보장** — $h$ 를 자료에서 학습하면 보장이 "학습된 모델에
  대한" 것으로 약해진다. 현재 접근:
  [Robey et al. 2020](https://arxiv.org/abs/2004.03315) 의 전문가 시연으로부터의 CBF 학습,
  [Dawson, Gao & Fan 2022](https://arxiv.org/abs/2202.11762) 의 학습된 인증서 서베이.
  비어 있는 자리: 학습 오차 → 안전 여유 손실의 명시적 사상. `c3-lyapunov-stability` 와
  `c3-contraction-incremental` 의 열린 문제와 같은 벽이다.
- **(열린 문제) 상대 차수가 높고 접촉이 섞인 제약** — 관절 한계·충돌 회피는 상대 차수 2 이지만
  접촉이 생기면 동역학이 비매끄럽고 $\psi$ 사슬의 미분이 존재하지 않는다. 비어 있는 자리:
  하이브리드·비매끄러운 계에서의 CBF 이론 — `c2-contact-dynamics` 와
  `c4-contact-implicit-hybrid` 에서 같은 벽을 만난다.

## 개념 점검

`rc quiz c3-cbf-safety-filter` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c3-cbf-safety-filter-quiz
questions:
  - id: q1
    type: single
    prompt: "CBF 조건 $\\dot h \\ge -\\alpha(h)$ 가 전진 불변성을 주는 증명의 핵심 단계는?"
    choices:
      - "$h$ 가 Lyapunov 함수이므로 $h \\to 0$ 이기 때문"
      - "비교 ODE $\\dot y = -\\alpha(y)$ 의 해가 $y(0)\\ge0$ 이면 0 아래로 내려갈 수 없고, 비교 보조정리로 $h \\ge y$ 이기 때문"
      - "$\\alpha$ 가 유계이기 때문"
      - "QP 가 항상 가해이기 때문"
    answer: 1
    explanation: "$\\alpha(0)=0$ 이므로 $y\\equiv0$ 이 비교 ODE 의 해이고, 해의 유일성 때문에 다른 해가 0 을 가로지를 수 없다. 비교 보조정리로 $h(x(t)) \\ge y(t) \\ge 0$ 이다. $\\alpha$ 의 Lipschitz 성이 빠지면 유일성이 깨져 결론도 깨진다."
    concept: { front: "CBF 전진 불변성의 증명 전략", back: "비교 ODE $\\dot y=-\\alpha(y)$ 의 해가 0 을 가로지르지 못함 + 비교 보조정리" }
  - id: q2
    type: single
    prompt: "단일 제약 최소 개입 QP (2)의 해가 제약이 비활성일 때 명목 제어와 **정확히** 일치하는 이유는?"
    choices:
      - "목적함수가 선형이기 때문"
      - "KKT 상보성에서 $\\lambda \\ge 0$ 이면 승수 $\\mu=0$ 이 모든 조건을 만족하기 때문"
      - "$L_gh$ 가 0 이기 때문"
      - "QP 솔버의 수치 오차가 작기 때문"
    answer: 1
    explanation: "여유 $\\lambda = L_fh + L_ghu_{\\mathrm{nom}} + \\alpha(h) \\ge 0$ 이면 $\\mu=0$ 으로 정류성·상보성·가능성·부호가 모두 만족되고, 그때 해는 $u_{\\mathrm{nom}}$ 이다. 그래서 필터는 **필요할 때만** 개입한다."
    concept: { front: "최소 개입 필터의 투명성", back: "$\\lambda\\ge0$ 이면 $\\mu=0$ 이라 $u^\\star = u_{\\mathrm{nom}}$ — 활성일 때만 $L_gh$ 방향으로 최소한 민다" }
  - id: q3
    type: short
    prompt: "이중 적분기 $\\ddot x = u$, $h = x_{\\max}-x$, 선형 $\\alpha_i$ 에 대해 지수 CBF 조건이 주는 입력 상한을 쓰면? ($\\alpha_1,\\alpha_2,x,\\dot x$ 로)"
    answer: ["-(a1+a2) xdot + a1 a2 (xmax - x)", "-(alpha1+alpha2)*xdot + alpha1*alpha2*(xmax-x)", "u <= -(a1+a2)v + a1a2(xmax-x)", "-(α1+α2)ẋ + α1α2(x_max−x)"]
    explanation: "$\\psi_1 = -\\dot x + \\alpha_1(x_{\\max}-x)$ 에 $\\dot\\psi_1 + \\alpha_2\\psi_1 \\ge 0$ 를 적용하면 $u \\le -(\\alpha_1+\\alpha_2)\\dot x + \\alpha_1\\alpha_2(x_{\\max}-x)$ 다. 제약이 입력 상한 하나로 환원되므로 필터는 $\\min$ 한 번이다."
    concept: { front: "이중 적분기의 지수 CBF 상한", back: "$u \\le -(\\alpha_1+\\alpha_2)\\dot x + \\alpha_1\\alpha_2(x_{\\max}-x)$" }
  - id: q4
    type: truefalse
    prompt: "입력 한계 $|u| \\le u_{\\max}$ 가 있어도 CBF-QP 필터는 안전을 보장한다."
    answer: false
    explanation: "필요한 제동이 $u_{\\max}$ 를 넘으면 제약을 만족시킬 수 없고 보장이 사라진다. 측정값: $\\alpha_1=\\alpha_2=3$, $x_{\\max}=1$ 에서 $u_{\\max}=2$ 면 189개 중 95개가 포화되고 최악 $\\min_t h = -0.138$ 로 **위반**이 발생한다. $u_{\\max}=20$ 에서는 포화가 없다."
    concept: { front: "입력 제약과 CBF 보장", back: "포화가 생기면 보장이 사라진다 — 입력 제약 CBF·백업 CBF 로 안전 집합을 미리 줄여야 한다" }
```

## 이 단계 공부법

1. **증명을 세 줄로 줄인다 (30분)** — "비교 ODE, 0 을 못 넘음, 비교 보조정리". R1 의 전부다.
   그 다음 $\alpha$ 의 Lipschitz 성을 빼면 어디가 깨지는지 한 문장으로 쓴다.
2. **KKT 로 (3)을 직접 유도한다 (40분)** — 승수 하나뿐인 QP 이므로 손으로 끝난다. 유도하고 나면
   "필터는 활성일 때만 $L_gh$ 방향으로 민다" 가 식에서 보인다.
3. **상대 차수를 손으로 만난다 (40분)** — $h = x_{\max}-x$ 에 $L_gh = 0$ 임을 확인하고, 1차
   CBF 를 그대로 쓰면 **아무것도 못 한다**는 것을 본다. 그 뒤에 (5)의 사슬을 세운다.
4. **필터 없이 먼저 돌린다 (40분)** — 재현 과제의 비교 대상 ⓐ(필터 없음)와 ⓑ(단순 클리핑)를
   **먼저** 돌려 벽을 넘는 것을 본다. 막아야 할 것이 무엇인지 보고 나서 필터를 켠다.
5. **입력 한계로 보장을 깨 본다 (60분)** — 조건 4. $u_{\max}=2$ 에서 위반이 나오는 것을 보고
   (6)의 좌변을 출력해 원인을 확인한다. **보장에는 전제가 있다**를 숫자로 겪는 단계다.
6. **$\alpha$ 의 교환을 표로 만든다 (40분)** — P4 의 추가 과제. $\alpha$ 를 키우면 투명해지지만
   보장 영역이 좁아진다. 이 표가 안전 필터 튜닝의 전부다.
7. **논문은 "보장의 전제" 로 읽는다 (135분)** — Ames 2017 은 정식화, Nguyen–Sreenath 는 고차
   확장, Ames 2019 서베이는 전제들이 깨지는 목록이다. 논문당 1페이지 노트를 쓰고, 서베이의 열린
   문제 하나를 이 레슨의 재현 과제로 어떻게 측정할지 적는다.

**통과 기준**: 백지에서 R1 의 증명과 (3)·(4)를 유도할 수 있고, 입력 제약이 보장을 깨는 조건을
식과 숫자로 쓸 수 있고, 재현 과제의 네 조건을 만족하는 코드와 논문 3편의 노트가 있다.

**모듈을 마치며**: C3 의 여섯 레슨은 같은 구조를 여섯 번 반복했다 — **보장은 가정과 함께
온다**. Lyapunov 는 준위집합의 유계성을, 피드백 선형화는 involutivity 를, 수축은 균일 계량과
측지적 볼록성을, 수동성은 환경의 수동성을, 적응은 지속 여진을, CBF 는 입력의 여유를 요구했다.
각 레슨의 재현 과제가 그 가정을 **깨는** 실험을 하나씩 포함한 것은 우연이 아니다. 다음 모듈
`c4-pontryagin-indirect` 부터는 "안전하고 안정한" 것들 중에서 **최적인** 것을 고르기 시작한다.
