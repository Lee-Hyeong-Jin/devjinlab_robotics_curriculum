---
id: c3-feedback-linearization
title: 피드백 선형화와 가제어성
summary: >-
  좌표와 입력을 바꿔 비선형 계를 선형계로 만드는 조건(involutivity 와 Frobenius 정리)을
  증명 수준에서 다루고, 입출력 선형화에서 남는 영역 동역학(zero dynamics)이 추적 성능을
  어떻게 제한하는지 본다. 이어서 선형화가 불가능한 비홀로노믹 계로 넘어가 리 괄호가 왜
  가제어성은 주면서 적분가능성은 깨뜨리는지(Chow–Rashevskii) 유도하고, 연쇄형(chained form)과
  사인파 조향으로 차동구동 로봇을 주차시킨다.
objectives:
  - 단일 입력 계의 완전 피드백 선형화 조건을 Frobenius 정리로 환원해 증명 스케치를 재구성할 수 있다.
  - 상대 차수와 정규형을 계산하고 영역 동역학이 불안정할 때 무엇이 깨지는지 설명할 수 있다.
  - 리 괄호 방향으로의 2차 운동을 흐름의 합성에서 직접 전개할 수 있다.
  - 차동구동 로봇을 연쇄형으로 변환하고 사인파 조향의 변위 $\pi ab/\omega^2$ 를 유도할 수 있다.
  - 매끄러운 시불변 피드백으로 비홀로노믹 계를 안정화할 수 없는 이유를 구체적으로 보일 수 있다.
prerequisites: [c3-lyapunov-stability]
difficulty: 5
estimated_minutes: 540
tags: [nonlinear-control, feedback-linearization, nonholonomic, lie-brackets, controllability, research]
activities:
  - id: c3-feedback-linearization-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c3-feedback-linearization-papers
    kind: reading
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c3-feedback-linearization-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 2 · 구현 1 · 반례 1)
    estimated_minutes: 180
  - id: c3-feedback-linearization-reproduction
    kind: exercise
    title: 재현 과제 — 사인파 조향으로 주차 (R2)
    estimated_minutes: 105
  - id: c3-feedback-linearization-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Khalil, Nonlinear Systems (3rd ed., 2002)"
    kind: book
    note: ch.13 (피드백 선형화) — 13.1 정규형, 13.2 입출력 선형화, 13.4 완전 선형화 조건. (공식 URL 미확인)
  - title: "Murray, Li & Sastry, A Mathematical Introduction to Robotic Manipulation"
    kind: book
    note: ch.7 (비홀로노믹 운동 계획) — 연쇄형·사인파 조향·Chow 정리의 로보틱스 쪽 표준 서술. (공식 URL 미확인)
  - title: "Murray & Sastry — Nonholonomic motion planning: steering using sinusoids (1993)"
    url: https://doi.org/10.1109/9.277235
    kind: article
    note: 필독 1. 연쇄형과 사인파 조향의 원전. §II·§III 가 재현 과제의 알고리즘이다.
  - title: "Hauser, Sastry & Meyer — Nonlinear control design for slightly non-minimum phase systems (1992)"
    url: https://doi.org/10.1016/0005-1098(92)90029-F
    kind: article
    note: 필독 2. 영역 동역학이 불안정할 때 정확 선형화를 포기하고 무엇을 하는지.
  - title: "Devasia, Chen & Paden — Nonlinear inversion-based output tracking (1996)"
    url: https://doi.org/10.1109/9.508898
    kind: article
    note: 필독 3. 비최소위상 계에서 안정 역변환(stable inversion)으로 정확 추적을 복구하는 방법.
  - title: "Tedrake, Underactuated Robotics"
    url: https://underactuated.csail.mit.edu/
    kind: book
    note: 권장. 부분 피드백 선형화(collocated/non-collocated)와 언더액추에이티드 계에서의 한계.
---

# 피드백 선형화와 가제어성

## 전제와 기호

`c3-lyapunov-stability` 에서 안정성 **판정** 도구를 세웠다. 이 레슨은 **좌표를 바꿔** 문제를
선형계로 옮기려는 시도이고, 그 시도가 어디서 막히는지를 다룬다. 막히는 지점이 비홀로노믹
로봇(차동구동 로봇, 자동차, 위성)의 제어·계획 전체를 규정한다.

전제: 벡터장과 흐름(flow), 야코비안, 암시 함수 정리. 리 괄호와 분포(distribution)는 이 레슨에서
정의하고 쓴다 — 미분기하 과목을 들었을 필요는 없다.

| 기호 | 뜻 |
|---|---|
| $\dot{x} = f(x) + \sum_{i=1}^m g_i(x)u_i$ | 입력에 아핀인 계. $f$ 는 드리프트, $g_i$ 는 입력 벡터장 |
| $L_f h$ | 리 미분 $\nabla h(x)^\top f(x)$. $L_f^k h$ 는 $k$ 번 반복 |
| $[f, g]$ | 리 괄호 $\dfrac{\partial g}{\partial x}f - \dfrac{\partial f}{\partial x}g$ |
| $\operatorname{ad}_f^k g$ | $\operatorname{ad}_f^0 g = g$, $\operatorname{ad}_f^{k}g = [f, \operatorname{ad}_f^{k-1}g]$ |
| $\Delta = \operatorname{span}\{g_1,\dots,g_m\}$ | 분포. 각 점에서 접공간의 부분공간 |
| 분포가 **involutive** | 모든 $X, Y \in \Delta$ 에 대해 $[X,Y] \in \Delta$ |
| $\rho$ | 상대 차수(relative degree). $L_{g}L_f^{k}h = 0$ ($k<\rho-1$), $L_gL_f^{\rho-1}h \ne 0$ |
| $q = (x, y, \theta)$ | 평면 위 차동구동 로봇의 자세. $u_1$ 전진 속도, $u_2$ 각속도 |
| $z = (z_1,z_2,z_3)$ | 연쇄형(chained form) 좌표. $v = (v_1,v_2)$ 는 그 좌표의 입력 |
| $\Phi^X_t(x)$ | 벡터장 $X$ 의 흐름. $\frac{d}{dt}\Phi^X_t = X(\Phi^X_t)$, $\Phi^X_0 = \operatorname{id}$ |

이 레슨의 달리는 예(running example)는 차동구동 로봇이다:

$$
\dot{q} = \underbrace{\begin{bmatrix}\cos\theta\\ \sin\theta\\ 0\end{bmatrix}}_{g_1(q)}u_1
  + \underbrace{\begin{bmatrix}0\\ 0\\ 1\end{bmatrix}}_{g_2(q)}u_2, \qquad f \equiv 0. \tag{1}
$$

드리프트가 없고($f=0$) 입력이 상태보다 적다($m=2 < n=3$) — 이 두 사실이 이 레슨의 후반부를
전부 설명한다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (완전 피드백 선형화 조건) [D3]** — 단일 입력 계 $\dot x = f(x) + g(x)u$ 가 $x_0$ 근방에서
  좌표변환 $\xi = \Phi(x)$ 와 입력변환 $u = \alpha(x) + \beta(x)v$ 로 선형계
  $\dot\xi = A\xi + Bv$ (가제어)로 바뀌는 것은 다음과 **동치**다:
  (i) $\operatorname{rank}\{g, \operatorname{ad}_fg, \dots, \operatorname{ad}_f^{n-1}g\} = n$,
  (ii) $\Delta_{n-1} = \operatorname{span}\{g, \dots, \operatorname{ad}_f^{n-2}g\}$ 가 involutive.
  (ii)가 없으면 선형화 출력 $h$ 가 **존재하지 않는다** — Frobenius 정리가 그 사실을 말해 준다.
- **R2 (입출력 선형화와 영역 동역학) [D2]** — 출력 $y=h(x)$ 의 상대 차수가 $\rho$ 면
  $$
  u = \frac{1}{L_gL_f^{\rho-1}h(x)}\big(v - L_f^{\rho}h(x)\big) \tag{2}
  $$
  이 입출력 관계를 $y^{(\rho)} = v$ 로 만든다. 남는 $n-\rho$ 차원의 내부 동역학은 $y\equiv0$ 을
  유지하는 입력 아래에서 **영역 동역학(zero dynamics)** $\dot\eta = q(0,\eta)$ 가 되고, 이것이
  불안정하면 정확 추적은 내부 상태를 발산시킨다.
- **R3 (리 괄호 운동과 Chow–Rashevskii) [D2]** — 네 흐름을 교대로 합성하면
  $$
  \Phi^{g_2}_{-\varepsilon}\circ\Phi^{g_1}_{-\varepsilon}\circ\Phi^{g_2}_{\varepsilon}\circ
    \Phi^{g_1}_{\varepsilon}(x) = x + \varepsilon^2 [g_1,g_2](x) + O(\varepsilon^3) \tag{3}
  $$
  이다. 따라서 괄호가 만드는 리 대수가 모든 점에서 $\mathbb{R}^n$ 을 생성하면(LARC,
  bracket-generating) 드리프트 없는 계는 **국소적으로 도달 가능**하다(Chow–Rashevskii).
  (1)의 경우 $[g_1,g_2] = (\sin\theta, -\cos\theta, 0)^\top$ 이고
  $\det[g_1\ g_2\ [g_1,g_2]] = 1$ 이므로 가제어다.
- **R4 (연쇄형과 사인파 조향) [D2]** — 변환
  $$
  z_1 = \theta,\quad z_2 = x\cos\theta + y\sin\theta,\quad z_3 = x\sin\theta - y\cos\theta,
    \qquad v_1 = u_2,\quad v_2 = u_1 - u_2 z_3 \tag{4}
  $$
  는 (1)을 연쇄형 $\dot z_1 = v_1$, $\dot z_2 = v_2$, $\dot z_3 = z_2v_1$ 로 바꾼다. 한 주기
  $T = 2\pi/\omega$ 동안 $v_1 = a\sin\omega t$, $v_2 = b\cos\omega t$ 를 넣으면 $z_1,z_2$ 는
  제자리로 돌아오고
  $$
  \Delta z_3 = \frac{\pi a b}{\omega^2} \tag{5}
  $$
  만큼 $z_3$ 가 이동한다.
- **R5 (매끄러운 시불변 피드백의 부재, Brockett 의 필요조건) [D2]** — $\dot x = f(x,u)$ 가
  $C^1$ 시불변 피드백으로 원점에서 점근 안정화되면 $(x,u)\mapsto f(x,u)$ 의 상(image)이 원점의
  근방을 덮어야 한다(Brockett 1983, 책 챕터 — 영구 링크 없음, Murray–Sastry 1993 §I 에 재진술).
  (1)에서는 $\lvert\theta\rvert<\delta$, $\lvert u\rvert<\delta$ 로 제한하면
  $\dot q = (\cos\theta\,u_1,\ \sin\theta\,u_1,\ u_2)$ 가 **측면 방향 $(0,\epsilon,0)$ 을 전혀
  만들지 못한다** — 따라서 (1)은 어떤 매끄러운 시불변 피드백으로도 안정화되지 않는다.

## 유도

### R3 — 리 괄호 방향으로의 2차 운동

(3)을 Taylor 전개로 직접 만든다. 흐름을 $\varepsilon$ 의 2차까지 쓰면, 임의의 매끄러운 벡터장
$X$ 에 대해

$$
\Phi^X_\varepsilon(x) = x + \varepsilon X(x) + \frac{\varepsilon^2}{2}\,\frac{\partial X}{\partial x}(x)X(x)
  + O(\varepsilon^3). \tag{6}
$$

($\frac{d}{dt}\Phi = X(\Phi)$ 를 한 번 더 미분하면 $\ddot\Phi = \frac{\partial X}{\partial x}X$ 다.)
표기를 줄여 $A := \frac{\partial g_1}{\partial x}$, $B := \frac{\partial g_2}{\partial x}$ 로 쓰고
네 단계를 차례로 합성한다. 1단계:

$$
x_1 = x + \varepsilon g_1 + \tfrac{\varepsilon^2}{2}Ag_1 + O(\varepsilon^3).
$$

2단계에서는 $g_2$ 를 $x_1$ 에서 평가해야 하므로 $g_2(x_1) = g_2 + \varepsilon B g_1 + O(\varepsilon^2)$:

$$
x_2 = x_1 + \varepsilon g_2(x_1) + \tfrac{\varepsilon^2}{2}(Bg_2)(x_1) + O(\varepsilon^3)
    = x + \varepsilon(g_1+g_2) + \varepsilon^2\!\left(\tfrac12 Ag_1 + Bg_1 + \tfrac12 Bg_2\right) + O(\varepsilon^3).
$$

3단계는 $-g_1$ 을 $x_2$ 에서 평가한다. $g_1(x_2) = g_1 + \varepsilon A(g_1+g_2) + O(\varepsilon^2)$ 이므로

$$
x_3 = x_2 - \varepsilon g_1(x_2) + \tfrac{\varepsilon^2}{2}(Ag_1)(x_2) + O(\varepsilon^3)
    = x + \varepsilon g_2 + \varepsilon^2\!\left(Bg_1 + \tfrac12 Bg_2 - Ag_2\right) + O(\varepsilon^3).
$$

($-g_1$ 의 흐름에서도 (6)의 2차 항은 $\frac{(-\varepsilon)^2}{2}\frac{\partial(-g_1)}{\partial x}(-g_1)
= +\frac{\varepsilon^2}{2}Ag_1$ 로 **부호가 그대로**라는 점이 틀리기 쉬운 지점이다.)
4단계도 같은 방식으로 $-g_2$ 를 $x_3$ 에서 평가하면 $\varepsilon$ 의 1차 항이 모두 소거되고

$$
x_4 = x + \varepsilon^2\big(Bg_1 - Ag_2\big) + O(\varepsilon^3)
    = x + \varepsilon^2[g_1,g_2](x) + O(\varepsilon^3), \tag{7}
$$

즉 (3)이다. **수치 확인**: (1)에서 $\theta=0$, 네 구간을 각각 $\varepsilon$ 만큼 적분하면
$[g_1,g_2](q)=(\sin\theta,-\cos\theta,0)^\top$ 에서 예측값은 $(0,-\varepsilon^2,0)$ 이고,
$\varepsilon = 0.1,\ 0.05,\ 0.02$ 에서 잔차 노름이 각각 $0.4999\varepsilon^3$,
$0.5000\varepsilon^3$, $0.5000\varepsilon^3$ 로 3차에 정확히 비례한다. 즉 **앞뒤로 움직이며
제자리에서 핸들을 꺾는 네 동작이 로봇을 옆으로 $\varepsilon^2$ 만큼 민다** — 평행 주차가
리 괄호다.

여기서 Chow–Rashevskii 로 가는 길이 보인다: 괄호와 그 반복 괄호가 $\mathbb{R}^n$ 을 생성하면,
각 방향으로 $O(\varepsilon^2)$(또는 더 깊은 괄호면 $O(\varepsilon^k)$) 크기의 운동을 조립할 수
있고, 그 운동들을 이어 붙여 근방의 임의 점에 도달한다. 완전한 증명은 운동의 합성이 열린
사상이 됨을 보이는 것이고(생략: Chow 정리의 표준 증명, MLS ch.7 Thm 7.? 또는
Sussmann 의 궤도 정리), 이 레슨은 그 **구성 단계**만 유도한다.

**가정이 깨지는 곳**: (3)은 $\varepsilon \to 0$ 의 국소 성질이다. 괄호 방향의 운동이
$\varepsilon^2$ 로 줄어들기 때문에, 측면으로 거리 $d$ 를 가려면 $O(d/\varepsilon^2)$ 번의 동작이
필요하다 — "가제어" 와 "효율적으로 움직인다" 는 전혀 다른 말이다. 괄호가 더 깊어질수록
($O(\varepsilon^3)$, $O(\varepsilon^4)$) 이 비용은 급격히 커지고, 이것이 비홀로노믹 계의
운동 계획이 어려운 근본 이유다(`c6-nonholonomic-planning` 에서 다시 나온다).

### R4 — 연쇄형 변환과 사인파 조향

**1단계 (변환 유도).** (4)의 $z_2,z_3$ 는 로봇 몸체 좌표에서 본 위치다. $z_2$ 를 미분하면

$$
\dot z_2 = \dot x\cos\theta - x\sin\theta\,\dot\theta + \dot y\sin\theta + y\cos\theta\,\dot\theta
  = u_1(\cos^2\theta+\sin^2\theta) + u_2(-x\sin\theta + y\cos\theta) = u_1 - u_2 z_3,
$$

여기서 마지막 등호는 $-x\sin\theta+y\cos\theta = -z_3$ 이기 때문이다. 같은 방식으로

$$
\dot z_3 = u_1\cos\theta\sin\theta - u_1\sin\theta\cos\theta + u_2(x\cos\theta + y\sin\theta) = u_2 z_2,
$$

그리고 $\dot z_1 = u_2$. 따라서 $v_1 := u_2$, $v_2 := u_1 - u_2z_3$ 로 입력을 바꾸면

$$
\dot z_1 = v_1, \qquad \dot z_2 = v_2, \qquad \dot z_3 = z_2 v_1 \tag{8}
$$

이고, 역변환은 $u_2 = v_1$, $u_1 = v_2 + v_1 z_3$ 다. 원래 좌표로 돌아오는 식도 필요하다:
$x = z_2\cos z_1 + z_3 \sin z_1$, $y = z_2 \sin z_1 - z_3\cos z_1$, $\theta = z_1$ (대입해 확인).

**2단계 (사인파 한 주기의 변위).** (8)에 $v_1 = a\sin\omega t$, $v_2 = b\cos\omega t$ 를 넣고
$T = 2\pi/\omega$ 까지 적분한다.

$$
z_1(t) = z_1(0) + \frac{a}{\omega}(1-\cos\omega t), \qquad
z_2(t) = z_2(0) + \frac{b}{\omega}\sin\omega t,
$$

둘 다 $t=T$ 에서 **정확히 제자리**로 돌아온다. 남은 $z_3$ 는

$$
\Delta z_3 = \int_0^T z_2(t)v_1(t)\,dt
  = \underbrace{z_2(0)\,a\!\int_0^T\!\sin\omega t\,dt}_{=\,0}
  + \frac{ab}{\omega}\!\int_0^T\!\sin^2\omega t\,dt
  = \frac{ab}{\omega}\cdot\frac{T}{2} = \frac{\pi ab}{\omega^2}, \tag{9}
$$

즉 (5)다. $z_2(0)$ 항이 사라지는 것이 핵심이다 — **출발 위치와 무관하게** 변위가
$\pi ab/\omega^2$ 로 정해진다.

**3단계 (주차 알고리즘).** (8)의 구조 때문에 세 구간으로 끝난다. 목표
$q^\star=(x^\star,y^\star,\theta^\star)$ 를 (4)로 $z^\star$ 로 옮기고:

- **A**: $v_2=0$, $v_1$ 을 상수로 두어 $z_1 \to z_1^\star$. ($z_2$ 는 불변, $z_3$ 는 $z_2v_1$ 만큼 변한다.)
- **B**: 사인파 쌍으로 $z_3 \to z_3^\star$. $z_1, z_2$ 는 주기 끝에서 제자리.
  필요한 $\Delta z_3$ 에서 (5)로 $b = \Delta z_3\,\omega^2/(\pi a)$ 를 정한다.
- **C**: $v_1 = 0$, $v_2$ 를 상수로 두어 $z_2 \to z_2^\star$. ($\dot z_3 = z_2v_1 = 0$ 이므로
  $z_3$ 가 보존되고 $z_1$ 도 불변이다.)

순서가 A→B→C 인 이유는 C 가 $z_3$ 를 건드리지 않고 B 가 $z_1,z_2$ 를 되돌려 주기 때문이다.
A 를 마지막에 두면 $z_2 \ne 0$ 인 상태에서 $z_1$ 을 돌리므로 $z_3$ 가 다시 어긋난다.

**수치 확인**: $(0,0,0) \to (1,1,\pi/2)$ 를 세 구간 각 1초로 풀면 $z^\star=(\pi/2, 1, 1)$,
B 구간의 $\omega = 2\pi$, $a=1$ 에서 $b = 4\pi \approx 12.566371$ 이고, RK4 로 원래 좌표 (1)을
적분한 종단 오차는 $\lVert q(T)-q^\star\rVert_\infty \approx 2\cdot10^{-11}$ 이다.

**가정이 깨지는 곳**: (4)는 $z_1 = \theta$ 를 **감싸지 않은(unwrapped)** 각으로 본다.
$\theta$ 를 $(-\pi,\pi]$ 로 랩핑하면 A 구간이 짧은 쪽으로 돌면서 $z_3$ 의 누적이 달라지므로,
구현에서는 각을 랩핑하지 말고 목표를 $\theta^\star + 2k\pi$ 중 하나로 **골라야** 한다. 또
$b = \Delta z_3\omega^2/(\pi a)$ 는 $\Delta z_3$ 가 크거나 $T$ 가 짧으면 폭발한다 — 입력 한계가
있으면 주기를 여러 번 반복해 나눠야 한다($N$ 주기로 쪼개면 각 주기의 $b$ 가 $1/N$).

### R2 — 입출력 선형화, 그리고 바퀴 축에서 $d$ 만큼 앞을 보는 점

(1)에서 출력을 로봇의 위치 $(x,y)$ 로 잡으면 입출력 선형화가 **실패**한다:

$$
\begin{bmatrix}\dot x\\ \dot y\end{bmatrix}
  = \begin{bmatrix}\cos\theta & 0\\ \sin\theta & 0\end{bmatrix}
    \begin{bmatrix}u_1\\u_2\end{bmatrix},
$$

디커플링 행렬의 2열이 0 이라 $u_2$ 가 출력에 전혀 나타나지 않는다. 그런데 출력을 바퀴 축에서
전방 $d>0$ 의 점 $h_d(q) = (x + d\cos\theta,\ y + d\sin\theta)$ 로 바꾸면

$$
\dot h_d = \underbrace{\begin{bmatrix}\cos\theta & -d\sin\theta\\
  \sin\theta & d\cos\theta\end{bmatrix}}_{=:J_d(\theta)}\begin{bmatrix}u_1\\u_2\end{bmatrix},
  \qquad \det J_d = d\,(\cos^2\theta+\sin^2\theta) = d. \tag{10}
$$

$d \ne 0$ 이면 $J_d$ 는 **모든 $\theta$ 에서** 가역이므로 $u = J_d^{-1}v$ 로 $\dot h_d = v$ 를
얻는다. 상대 차수는 각 출력에 대해 1 이고, 남는 내부 상태는 1차원($\theta$)이다. $h_d \equiv$
상수를 유지하는 입력은 $v=0$, 즉 $u=0$ 이고 그때 $\dot\theta = 0$ — 영역 동역학은
$\dot\eta = 0$ 으로 **안정하지도 불안정하지도 않다**(한계 안정). 그래서 전방 점은 추적되지만
자세 $\theta$ 는 제어되지 않는다. 주차(자세 포함)가 여전히 어려운 이유가 여기 있다.

**가정이 깨지는 곳**: $d \to 0$ 에서 $\det J_d = d \to 0$ 이므로 $\lVert J_d^{-1}\rVert$ 가
$1/d$ 로 폭발한다. 작은 $d$ 는 "거의 바퀴 축을 추적" 하지만 **각속도 명령이 $1/d$ 로 커진다** —
선형화가 특이점으로 가는 전형적 모습이다. 반대로 $d$ 를 크게 잡으면 명령은 온순해지지만
추적하는 점이 로봇에서 멀어져 장애물 회피가 거짓이 된다. $d$ 는 성능과 조건수의 교환이다.

영역 동역학이 **불안정한** 경우가 진짜 문제다. 예를 들어

$$
\dot\xi = u, \qquad \dot\eta = \eta + \xi, \qquad y = \xi \tag{11}
$$

는 상대 차수 1 이고, $y\equiv0$ 을 유지하려면 $u\equiv0$ 이어서 $\dot\eta=\eta$ 가 발산한다.
즉 "정확 추적"이 내부 상태의 발산을 **요구**한다. 이런 비최소위상 계에서 쓰는 선택지는
ⓐ 근사 선형화(Hauser et al. 1992: 작은 결합 항을 버리고 설계한 뒤 오차를 유계로 통제)
ⓑ 안정 역변환(Devasia et al. 1996: 미래 궤적까지 쓰는 비인과적 입력을 풀어 정확 추적을 복구)
ⓒ 출력을 바꾸기(위의 $h_d$ 처럼). 세 선택지의 가정과 비용이 필독 논문의 내용이다.

### R5 — 매끄러운 시불변 피드백이 없다

Brockett 의 필요조건을 (1)에 직접 적용한다. 목표는 "임의로 작은 $\delta$ 에 대해
$\{f(q,u) : \lvert q\rvert<\delta,\ \lvert u\rvert<\delta\}$ 가 $0 \in \mathbb{R}^3$ 의 근방을
덮는가" 다. (1)에서 그 집합의 원소는 $(\cos\theta\,u_1,\ \sin\theta\,u_1,\ u_2)$ 꼴이다.
목표 벡터 $(0,\ \epsilon,\ 0)$ 을 만들려면

- 셋째 성분에서 $u_2 = 0$,
- 첫째 성분에서 $\cos\theta\,u_1 = 0$ 이고 $\lvert\theta\rvert<\delta < \pi/2$ 이므로
  $\cos\theta \ne 0$, 따라서 $u_1 = 0$,
- 그러면 둘째 성분이 $\sin\theta\cdot 0 = 0 \ne \epsilon$.

즉 상은 측면 방향을 **전혀** 포함하지 않는다. 필요조건이 깨지므로 (1)은 $C^1$ 시불변 피드백으로
원점에서 점근 안정화될 수 없다. 이것이 사인파 조향처럼 **시변(time-varying)** 또는 불연속
전략이 필수인 이유다.

**가정이 깨지는 곳**: 이 결론은 "매끄러운 + 시불변 + 상태만의 함수" 세 조건이 모두 있을 때의
이야기다. 하나만 풀면 길이 열린다 — 시변 피드백(사인파 조향), 불연속 피드백, 또는 목표를
점이 아닌 집합으로 바꾸는 practical stabilization. 다만 **열린 길에는 강건성의 대가**가 따른다
(열린 문제 참조).

## 증명 스케치

### R1 — 완전 피드백 선형화 조건

**가설** H1: $f, g$ 가 $x_0$ 근방에서 매끄럽고 $g(x_0)\ne0$.
H2: $\operatorname{rank}\{g,\operatorname{ad}_fg,\dots,\operatorname{ad}_f^{n-1}g\}(x_0) = n$.
H3: $\Delta_{n-1}=\operatorname{span}\{g,\dots,\operatorname{ad}_f^{n-2}g\}$ 가 $x_0$ 근방에서 involutive.
**결론** C: $L_gh = L_gL_fh = \dots = L_gL_f^{n-2}h = 0$, $L_gL_f^{n-1}h \ne 0$ 인 $h$ 가 존재하고,
$\xi = (h, L_fh, \dots, L_f^{n-1}h)$ 가 좌표계를 이루며 (2)꼴 입력변환이 계를 선형화한다.

**전략**: "선형화 출력 $h$ 를 찾는 문제" 를 "$\Delta_{n-1}$ 에 수직인 1-형식 $dh$ 를 찾는 문제" 로
바꾸고, Frobenius 정리로 그 존재를 involutivity 와 맞바꾼다.

1. **조건을 1-형식으로.** 요구 $L_gL_f^kh = 0$ ($k \le n-2$)은 $dh$ 가 $g,\dots,\operatorname{ad}_f^{n-2}g$
   전부와 직교한다는 뜻이다(반복 리 미분과 괄호의 관계 $L_{[X,Y]}h = L_XL_Yh - L_YL_Xh$ 를
   써서 귀납). 즉 $dh \perp \Delta_{n-1}$.
2. **Frobenius.** $\Delta_{n-1}$ 은 H2 로 차원 $n-1$ 이고 H3 로 involutive 다. Frobenius 정리:
   involutive 한 $(n-1)$-차원 분포는 **적분가능**하고, 국소적으로 $\Delta_{n-1} = \ker dh$ 인
   $h$ ($dh \ne 0$)가 존재한다. 이 한 줄이 H3 를 소비하는 지점이다.
3. **마지막 미분이 0 이 아니다.** H2 로 $\operatorname{ad}_f^{n-1}g \notin \Delta_{n-1}$ 이므로
   $L_gL_f^{n-1}h = \pm L_{\operatorname{ad}_f^{n-1}g}h \ne 0$ (부호는 괄호 전개에서 나온다).
   따라서 (2)의 분모가 살아 있다.
4. **좌표가 된다.** $\xi_i = L_f^{i-1}h$ 의 야코비안이 비특이임을 1·3단계의 직교 관계로 보이고
   (생략: $d h, dL_fh, \dots$ 의 선형독립 — Khalil Lemma 13.1), 그 좌표에서
   $\dot\xi_i = \xi_{i+1}$ ($i<n$), $\dot\xi_n = L_f^nh + L_gL_f^{n-1}h\,u$ 이므로 (2)가 선형계를 준다.
5. **역방향.** 선형화가 가능하면 $\xi_1$ 이 1단계의 $h$ 를 주고, $\ker d\xi_1 = \Delta_{n-1}$ 이
   적분가능하므로 involutive 다 — 즉 H3 는 **필요**조건이기도 하다.

**가설을 지우면**: H3 를 빼면 2단계의 $h$ 가 존재하지 않는다. (1)이 바로 그 경우다 —
$\Delta = \operatorname{span}\{g_1,g_2\}$ 는 2차원인데 $[g_1,g_2]\notin\Delta$ 이므로 involutive 가
아니고(확인: $\det[g_1\ g_2\ [g_1,g_2]]=1\ne0$), 따라서 상태 전체를 선형화하는 출력이 없다.
같은 괄호가 R3 에서는 **가제어성을 주는** 바로 그 양이다. 모순이 아니다: 괄호가 분포 밖으로
나가는 것이 "새 방향으로 움직일 수 있다"(좋다)와 "적분 곡면이 없다"(선형화 불가)를 동시에
뜻한다.

생략한 기술적 단계: Frobenius 정리의 증명과 $\{dL_f^{i}h\}$ 의 독립성. Khalil ch.13.1·Thm 13.2,
MLS ch.7 또는 Isidori ch.4 로.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R4)** (9)를 $v_1 = a\sin\omega t$, $v_2 = b\cos(k\omega t)$ ($k$ 는 양의 정수)로
다시 계산하라. 어떤 $k$ 에서 $\Delta z_3 = 0$ 이 되고, 그 사실을 더 높은 차원의 연쇄형
($\dot z_4 = z_3v_1$ 까지 있는 계)에서 어떻게 쓰는가?
*해답 스케치*: $\int_0^T \sin\omega t\sin k\omega t\,dt$ 의 직교성으로 $k\ne1$ 이면 기여가 0 이다.
고차 연쇄형에서는 $z_4$ 를 움직이려면 $\int z_3v_1$ 이 필요하고 $z_3$ 자체가 $\sin$ 의 적분이라
주파수 비를 $k=2$ 로 맞춰야 $z_3$ 와 $v_1$ 의 곱이 비영 평균을 갖는다 — Murray–Sastry 1993 §III
의 사인파 조향 일반형이 이 계산이다.

**P2 (증명, ★★★, R1·R3)** (1)에 대해 ⓐ LARC 가 성립함을 괄호로 보이고, ⓑ $\Delta$ 가
involutive 가 아님을 보이고, ⓒ 두 사실이 모순이 아닌 이유를 Frobenius 정리의 진술로 설명하라.
*해답 스케치*: $[g_1,g_2]=(\sin\theta,-\cos\theta,0)^\top$, $\det[g_1\ g_2\ [g_1,g_2]]=1$.
Frobenius 는 involutive $\Rightarrow$ 적분 곡면족 존재를 말하므로, involutive 가 아니면
"운동이 곡면에 갇히지 않는다" 는 뜻이고 그것이 바로 가제어성이다.

**P3 (계산, ★, R4)** $(0,0,0)$ 에서 $(1,1,\pi/2)$ 로 주차한다. 세 구간을 각 1초, B 구간에서
$a=1$ 로 둘 때 ⓐ $z^\star$, ⓑ B 구간의 $b$, ⓒ A 구간의 $v_1$ 을 구하라.
*정답*: ⓐ $z^\star = (\pi/2,\ 1,\ 1)$ ⓑ $\omega = 2\pi$ 이므로 $b = 1\cdot(2\pi)^2/\pi = 4\pi
\approx 12.566371$ ⓒ $v_1 = \pi/2 \approx 1.5707963$ (허용오차 $10^{-6}$).
검산: RK4($\Delta t \le 10^{-4}$)로 (1)을 적분해 종단 오차가 $10^{-6}$ 미만이면 맞다
(참조 구현은 $2\cdot10^{-11}$).

**P4 (계산, ★, R2)** (10)의 $J_d$ 에 대해 ⓐ $\det J_d$, ⓑ $\theta = 0$ 에서 $J_d^{-1}$,
ⓒ 전방 점을 속도 $(0, 1)$ 로 움직이려 할 때의 $u$ 를 $d$ 의 함수로 구하라.
*정답*: ⓐ $d$ ⓑ $J_d^{-1} = \begin{bmatrix}1 & 0\\ 0 & 1/d\end{bmatrix}$
ⓒ $u = (0,\ 1/d)$ — 각속도가 $1/d$ 로 폭발한다. 허용오차 $10^{-9}$.

**P5 (구현, ★★, R2)** $h_d$ 기반 입출력 선형화로 전방 점이 원을 따라가게 하는 추적기를 쓰고,
$d \in \{1, 0.3, 0.1, 0.03\}$ 에서 최대 각속도와 추적 오차를 표로 만들라.
*루브릭*: ⓐ 최대 $\lvert u_2\rvert$ 가 대략 $1/d$ 로 커지는 것을 보인다 ⓑ 자세 $\theta$ 는
제어되지 않는다는 점을 궤적으로 보인다 ⓒ $d$ 선택 기준을 조건수와 입력 한계로 쓴다.

**P6 (반례, ★★, R5)** (1)에 대해 "매끄러운 시불변 피드백 $u = \kappa(q)$, $\kappa(0)=0$ 으로
원점을 점근 안정화했다" 는 주장을 **두 가지 방식**으로 반박하라: (i) R5 의 상(image) 논증,
(ii) 구체적 피드백 하나를 잡아 원점 아닌 평형점(또는 수렴하지 않는 초기조건)을 제시.
*성질 체크리스트*: (i) 측면 방향이 상에 없음을 $\delta$ 와 함께 쓴다. (ii) 예:
$u = (\,\cos\theta\,e_x + \sin\theta\,e_y,\ k\,\theta_{\text{err}})$ 꼴의 "경사 하강" 피드백은
$q_0 = (0,0,0)$, 목표 $(0,1,0)$ 에서 $u \equiv 0$ 이 되어 로봇이 **전혀 움직이지 않는다**.

**P7 (논문, ★★, R2)** Hauser et al. 1992 와 Devasia et al. 1996 을 읽고, 같은 비최소위상
문제에 대한 두 처방의 차이를 ⓐ 가정 ⓑ 보장 ⓒ 실시간 구현 가능성의 세 줄로 대조하라.
*루브릭*: "근사(오차 유계, 인과적) vs 정확(비인과적, 미래 궤적 필요)" 의 대립을 짚으면 통과.
로봇에 올릴 때 어느 쪽이 왜 더 흔한지 한 문장 추가하면 가점.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Murray & Sastry, "Nonholonomic motion planning: steering using sinusoids" (1993, IEEE T-AC)**
   — 역할: `원전(seminal)`. <https://doi.org/10.1109/9.277235>
   §II(연쇄형과 변환 존재 조건)와 §III(사인파 조향)이 이 레슨의 R4 와 재현 과제다.
   추가 질문: ⓐ 어떤 계가 연쇄형으로 변환되는가 — 저자들이 요구하는 조건을 우리 표기로 쓰라.
   ⓑ 입력 크기·경로 길이에 대한 최적성은 주장하는가, 아닌가?
   ⓒ Brockett 의 필요조건은 논문의 어디에서 어떤 역할로 인용되는가?
2. **Hauser, Sastry & Meyer, "Nonlinear control design for slightly non-minimum phase systems:
   application to V/STOL aircraft" (1992, Automatica)** — 역할: `표준(standard)`.
   <https://doi.org/10.1016/0005-1098(92)90029-F>
   추가 질문: ⓐ "slightly" 를 정량화하는 양은 무엇이고, 그 양이 커지면 보장이 어떻게 바뀌는가?
   ⓑ 버린 항이 만드는 추적 오차의 상한을 저자들은 어떤 가정 아래 얻는가?
3. **Devasia, Chen & Paden, "Nonlinear inversion-based output tracking" (1996, IEEE T-AC)**
   — 역할: `표준(standard)`. <https://doi.org/10.1109/9.508898>
   추가 질문: ⓐ 안정 역변환이 **비인과적**이라는 것은 구현에서 정확히 무엇을 요구하는가?
   ⓑ 영역 동역학의 쌍곡성(hyperbolicity) 가정이 깨지면 어느 단계가 먼저 무너지는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 10분 이내, numpy 만. 대상은 (1)의
차동구동 로봇이고 입력 데이터는 없다 — 목표 자세는 스크립트가 생성한다.

**수용 기준 (네 조건 모두)**

1. **변환 검증**: 무작위 $10^4$ 개의 $(q, u)$ ($\lvert x\rvert,\lvert y\rvert \le 5$,
   $\theta \in (-\pi,\pi)$, $\lvert u\rvert \le 5$)에 대해, (4)로 얻은 $\dot z$ 와
   (8)의 $(v_1,\ v_2,\ z_2v_1)$ 이 $\max$ 절대 오차 $< 10^{-10}$ 로 일치.
2. **한 주기 변위**: 무작위 $(a,b,\omega) \in [0.5,2]\times[0.5,10]\times[0.5,4]$ 10 쌍에 대해
   한 주기 뒤 $\lvert \Delta z_3 - \pi ab/\omega^2\rvert < 10^{-8}$ 이고
   $\lvert z_1(T)-z_1(0)\rvert, \lvert z_2(T)-z_2(0)\rvert < 10^{-8}$.
3. **주차**: $(0,0,0)$ 에서 ⓐ 명시 목표 $(1,1,\pi/2)$ 와 ⓑ 무작위 목표 20개
   ($\lvert x^\star\rvert,\lvert y^\star\rvert \le 2$, $\theta^\star \in (-\pi,\pi)$)에 대해
   $\lVert q(T) - q^\star\rVert_\infty < 10^{-3}$ (RK4, $\Delta t \le 10^{-4}$, 세 구간 각 1초).
   목표별 최대 오차와 최대 $\lvert u_1\rvert,\lvert u_2\rvert$ 를 표로 보고한다.
4. **Brockett 반례 대조**: 같은 목표 집합에 대해 매끄러운 시불변 피드백
   $u_1 = k_1(\cos\theta\,e_x + \sin\theta\,e_y)$, $u_2 = k_2(\theta^\star-\theta)$
   ($e = q^\star - q$, $k_i>0$ 자유)를 돌려, **순수 측면 목표** $(0,1,0)$ 에서 종단 오차가
   $\ge 0.9$ (즉 사실상 움직이지 않음)임을 보인다. 같은 목표에서 사인파 조향은 $<10^{-3}$ 이다.

**비교 대상**: 조건 4 의 매끄러운 피드백(실패해야 한다)과, 조건 3ⓐ 의 참조 수치
(참조 구현의 종단 오차 $2\cdot10^{-11}$, $b = 4\pi \approx 12.566371$).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 주차 종단 오차가 $O(1)$ 로 남는다 | $u_1 = v_2 + v_1z_3$ 의 $z_3$ 항을 빼먹었다(역변환 오류) | 조건 1 을 먼저 통과시킨다 — 변환이 틀리면 나머지는 의미가 없다 |
| B 구간 뒤 $z_1,z_2$ 가 제자리로 안 온다 | 주기를 $T=2\pi/\omega$ 로 정확히 맞추지 않았거나 $\Delta t$ 가 주기를 나누지 못한다 | $\Delta t$ 를 $T/N$ 으로 잡고 $N$ 을 2배로 늘려 오차가 $16$ 배 줄어드는지(RK4 4차) 본다 |
| $\theta^\star$ 가 $\pm\pi$ 근처인 목표만 실패 | 각 랩핑 — $z_1=\theta$ 를 $(-\pi,\pi]$ 로 접었다 | 목표를 $\theta^\star+2k\pi$ 중 A 구간 회전이 가장 작은 쪽으로 고르고, 적분 중에는 랩핑하지 않는다 |
| 입력이 수백으로 튄다 | $b = \Delta z_3\omega^2/(\pi a)$ 가 큰 $\Delta z_3$ 에서 폭발 | 주기를 $N$ 번 반복해 $b$ 를 $1/N$ 로 낮춘다(총 변위는 같다) |
| 조건 4 의 피드백이 목표에 수렴한다 | 피드백에 시간 또는 불연속 항이 섞였다 | $u$ 가 $q$ 만의 연속 함수인지, $u(q^\star)=0$ 인지 확인한다 |

## 열린 문제

- **(열린 문제) 비홀로노믹 안정화의 강건성** — 시변·불연속 피드백은 수렴을 주지만, 수렴률이
  $t^{-1/k}$ 꼴로 느려지거나 모델 오차에 대한 여유가 정량화되지 않는다. 현재 접근:
  [Sørdalen & Egeland 1995](https://doi.org/10.1109/9.362901) 의 지수 안정화,
  [Morin & Samson 2003](https://doi.org/10.1109/TAC.2003.816963) 의 transverse function
  방식(점 대신 집합으로의 practical stabilization). 비어 있는 자리: 입력 한계와 측정 잡음까지
  포함한 강건성 여유를 설계 변수로 다루는 방법.
- **(열린 문제) 학습한 모델 위에서의 피드백 선형화** — (2)의 $1/L_gL_f^{\rho-1}h$ 는 모델에
  **나눗셈**으로 의존하므로 모델 오차가 이득을 직접 왜곡한다. 현재 접근:
  [Westenbroek et al. 2019](https://arxiv.org/abs/1910.13272) 처럼 선형화 오차를 강화학습으로
  보상하는 방식. 비어 있는 자리: 학습된 보정 아래에서도 상대 차수와 특이점 회피를 보장하는 조건.
- **(열린 문제) 근사 선형화 오차의 정량적 한계** — Hauser et al. 1992 의 "slightly" 를 로봇
  규모(접촉·유연성이 있는 다관절 계)에서 어떤 양으로 측정해야 하는지, 그 양이 크면 성능이
  얼마나 나빠지는지에 대한 일반 경계가 없다. 비어 있는 자리: 버린 항의 크기 →
  추적 오차 상한의 명시적 사상.
- **(열린 문제) 계획과 제어의 접합** — 사인파 조향은 장애물을 모른다. 괄호 운동의 비용
  ($O(d/\varepsilon^2)$)과 장애물 제약을 동시에 다루는 완전한(complete) 방법은 저차원에서만
  알려져 있다. `c6-nonholonomic-planning` 에서 계획 쪽에서 같은 문제를 다시 만난다.

## 개념 점검

`rc quiz c3-feedback-linearization` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c3-feedback-linearization-quiz
questions:
  - id: q1
    type: single
    prompt: "차동구동 로봇 (1)에서 $[g_1, g_2]$ 가 $\\Delta = \\mathrm{span}\\{g_1,g_2\\}$ 밖으로 나가는 사실은 무엇을 동시에 뜻하는가?"
    choices:
      - "가제어성이 없고 선형화도 불가능하다"
      - "새 방향으로 움직일 수 있고(가제어), 동시에 상태 전체를 선형화하는 출력은 없다"
      - "가제어성은 없지만 선형화는 가능하다"
      - "둘 다 괄호와 무관하다"
    answer: 1
    explanation: "괄호가 분포 밖으로 나가면 운동이 적분 곡면에 갇히지 않으므로 LARC 로 가제어성이 나온다. 같은 이유로 $\\Delta$ 가 involutive 가 아니어서 Frobenius 정리가 선형화 출력의 존재를 주지 못한다. 하나의 사실이 두 결론을 만든다."
    concept: { front: "비involutive 분포의 두 얼굴", back: "괄호가 밖으로 나감 = 가제어(Chow) + 완전 선형화 불가(Frobenius)" }
  - id: q2
    type: short
    prompt: "연쇄형에서 $v_1 = a\\sin\\omega t$, $v_2 = b\\cos\\omega t$ 를 한 주기 넣었을 때 $z_3$ 의 변위를 $a, b, \\omega$ 로 쓰면?"
    answer: ["pi*a*b/omega^2", "pi a b / omega^2", "πab/ω²", "pi*a*b/w^2", "\\pi a b/\\omega^2", "pi ab/omega^2"]
    explanation: "$\\Delta z_3 = \\int_0^T z_2v_1\\,dt$ 에서 $z_2(0)$ 항은 $\\int\\sin = 0$ 으로 사라지고 $\\frac{ab}{\\omega}\\int_0^T\\sin^2\\omega t\\,dt = \\frac{ab}{\\omega}\\cdot\\frac{T}{2} = \\frac{\\pi ab}{\\omega^2}$ 가 남는다. 출발 위치와 무관하다는 점이 알고리즘의 핵심이다."
    concept: { front: "사인파 조향 한 주기의 변위", back: "$\\Delta z_3 = \\pi ab/\\omega^2$ — $z_1, z_2$ 는 제자리로 돌아온다" }
  - id: q3
    type: truefalse
    prompt: "전방 거리 $d$ 를 0 에 가깝게 잡으면 바퀴 축을 더 정확히 추적할 수 있으므로 $d$ 는 작을수록 좋다."
    answer: false
    explanation: "$\\det J_d = d$ 이므로 $J_d^{-1}$ 의 노름이 $1/d$ 로 커진다. 작은 $d$ 는 각속도 명령을 $1/d$ 로 폭발시켜 입력 한계와 잡음 증폭에서 먼저 깨진다. $d$ 는 추적 대상의 위치와 조건수의 교환이다."
    concept: { front: "전방 점 $d$ 의 교환 관계", back: "$\\det J_d = d$ — 작은 $d$ 는 $1/d$ 로 커지는 각속도, 큰 $d$ 는 로봇에서 먼 추적점" }
  - id: q4
    type: single
    prompt: "Brockett 의 필요조건을 (1)에 적용할 때 측면 방향 $(0,\\epsilon,0)$ 이 상에 없다는 결론은 어디서 나오는가?"
    choices:
      - "$u_2 = 0$ 과 $\\cos\\theta \\ne 0$ 에서 $u_1 = 0$ 이 강제되고, 그러면 둘째 성분도 0 이 되기 때문"
      - "$\\theta$ 가 유계이기 때문"
      - "$g_1, g_2$ 가 선형독립이기 때문"
      - "리 괄호가 3차원을 생성하기 때문"
    answer: 0
    explanation: "작은 근방에서는 $\\lvert\\theta\\rvert<\\delta<\\pi/2$ 이므로 $\\cos\\theta\\ne0$ 이다. 첫째 성분 $\\cos\\theta\\,u_1 = 0$ 이 $u_1=0$ 을 강제하고, 그러면 둘째 성분 $\\sin\\theta\\,u_1$ 도 0 이다. 리 괄호로는 (두 동작을 이어 붙이면) 측면으로 갈 수 있지만, 한 시점의 속도 집합에는 그 방향이 없다."
    concept: { front: "Brockett 조건이 (1)에서 깨지는 자리", back: "한 시점의 가능한 속도 집합이 측면 방향을 포함하지 않는다 — 매끄러운 시불변 피드백 불가" }
```

## 이 단계 공부법

1. **괄호를 손으로 계산한다 (40분)** — (1)의 $[g_1,g_2]$ 를 정의대로 계산하고
   $\det[g_1\ g_2\ [g_1,g_2]]=1$ 을 확인한다. 이 한 계산이 레슨의 절반이다.
2. **평행 주차를 코드로 만나 본다 (60분)** — (3)의 네 동작을 그대로 구현해 로봇이 옆으로
   $\varepsilon^2$ 만큼 움직이는 것을 보고, $\varepsilon$ 을 절반으로 줄여 변위가 1/4 로 줄어드는지
   확인한다. 리 괄호를 "본" 뒤에는 잊히지 않는다.
3. **Frobenius 를 진술로만 외운다 (40분)** — 증명은 지금 필요 없다. "involutive $\iff$ 적분가능"
   과 "그래서 선형화 출력이 존재한다" 의 연결만 정확히 외운다. R1 의 2단계가 그 지점이다.
   Khalil ch.13.1 을 같은 표기로 대조해 읽는다.
4. **연쇄형 변환을 백지에서 다시 유도한다 (60분)** — (4)를 미분해 (8)이 나오는 과정을 두 번
   쓴다. $-x\sin\theta+y\cos\theta = -z_3$ 를 쓰는 지점이 유일한 트릭이다.
5. **재현 과제는 조건 순서대로 (105분)** — 변환 검증(조건 1) → 한 주기 변위(조건 2) → 주차
   (조건 3) → Brockett 대조(조건 4). 순서를 바꾸면 어디가 틀렸는지 알 수 없다. 조건 4 를
   **반드시** 돌려 본다: 매끄러운 피드백이 조용히 멈추는 것을 보는 것이 이 레슨의 결론이다.
6. **논문은 "포기한 것" 으로 읽는다 (150분)** — Murray–Sastry 는 최적성을 포기하고 구성 가능성을
   얻었고, Hauser 는 정확성을 포기하고 인과성을 얻었고, Devasia 는 인과성을 포기하고 정확성을
   얻었다. 세 편의 교환을 한 표로 정리하면 이 레슨이 끝난다.
7. **다음 레슨으로의 다리 (20분)** — 피드백 선형화는 "하나의 평형점" 을 다룬다. 궤적 **사이**의
   수렴을 보는 관점이 `c3-contraction-incremental` 이고, 거기서는 좌표변환 대신 **계량**을 찾는다.

**통과 기준**: 백지에서 (3)과 (8)을 유도할 수 있고, (1)이 선형화 불가이면서 가제어인 이유를
한 문단으로 쓸 수 있고, 재현 과제의 네 조건을 만족하는 코드와 논문 3편의 노트가 있다.
