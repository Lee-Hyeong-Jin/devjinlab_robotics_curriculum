---
id: c3-passivity-impedance
title: 수동성·에너지 성형과 임피던스 제어
summary: >-
  로봇이 환경과 **에너지를 주고받는** 관점으로 제어를 다시 쓴다. 매니퓰레이터의 수동성을
  $\tfrac12\dot{M} - C$ 의 반대칭성에서 유도하고, 수동 계의 피드백 결합이 왜 안정한지를 증명
  수준에서 본다. 이어서 에너지 성형·댐핑 주입과 임피던스 제어를 세우고, 디지털 구현이 수동성을
  어떻게 깨뜨리는지를 **닫힌 형태의 경계**로 유도해 고전적 Colgate–Schenkel 조건과 비교한다.
objectives:
  - 매니퓰레이터의 수동성을 $\tfrac12\dot{M}-C$ 의 반대칭성에서 빠진 줄 없이 유도할 수 있다.
  - 수동 계 두 개의 피드백 결합이 안정한 이유와 그 결론이 약해지는 지점을 설명할 수 있다.
  - 에너지 성형·댐핑 주입 제어기를 설계하고 LaSalle 로 수렴을 결론할 수 있다.
  - 샘플링된 가상 벽의 한 주기 에너지를 닫힌 형태로 계산해 수동성 경계를 유도할 수 있다.
  - 안정 경계와 수동성 경계가 왜 다른지, 어느 쪽이 더 보수적인지 수치로 보일 수 있다.
prerequisites: [c3-lyapunov-stability]
difficulty: 5
estimated_minutes: 540
tags: [nonlinear-control, passivity, impedance-control, energy-shaping, contact, research]
activities:
  - id: c3-passivity-impedance-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c3-passivity-impedance-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c3-passivity-impedance-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 2 · 구현 1 · 반례 1)
    estimated_minutes: 180
  - id: c3-passivity-impedance-reproduction
    kind: reproduction
    title: 재현 과제 — 가상 벽의 안정 경계와 수동성 경계 (R2)
    estimated_minutes: 105
  - id: c3-passivity-impedance-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Lynch & Park, Modern Robotics"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: ch.11.6 (임피던스 제어)와 ch.8.1 (라그랑주 동역학의 수동성 구조). 전문 PDF 무료.
papers:
  - id: hogan1985-impedance
    required: true
    role: seminal
  - id: colgate1988-coupled-stability
    required: true
    role: seminal
    note: "§3"
  - id: colgate1997-sampled-passivity
    required: true
    role: standard
  - id: ortega2002-ida-pbc
    role: standard
  - id: colgate1994-zwidth
    role: standard
---

# 수동성·에너지 성형과 임피던스 제어

## 전제와 기호

앞의 세 레슨은 로봇을 **혼자** 두고 다뤘다. 평형점(Lyapunov), 좌표(피드백 선형화), 궤적 사이의
거리(수축)가 모두 로봇 내부의 이야기였다. 그런데 조작(manipulation)은 정의상 **환경과의 상호
작용**이고, 환경의 모델은 모른다. 모르는 상대와 안정하게 결합하는 유일한 일반 도구가 에너지
—— 수동성(passivity)이다.

전제: 라그랑주 동역학과 질량행렬의 구조(`robotics-expert` M2·M7 또는 연구 트랙 `c2` 모듈),
`c3-lyapunov-stability` 의 LaSalle 정리, 선형계의 전달함수와 Nyquist 선도.

| 기호 | 뜻 |
|---|---|
| $M(q)\ddot q + C(q,\dot q)\dot q + g(q) = \tau + \tau_{\text{ext}}$ | 매니퓰레이터 동역학. $M \succ 0$, $g = \partial U/\partial q$ |
| $C(q,\dot q)$ | 원심·코리올리 행렬. **크리스토펠 기호로 만든** 표준 선택을 쓴다 |
| $U(q)$ | 중력 위치 에너지 |
| $V = \tfrac12\dot q^\top M\dot q + U(q)$ | 전체 에너지(저장 함수, storage function) |
| 한 포트(one-port) | 힘 $f$ 와 속도 $v$ 의 쌍. 포트로 들어간 에너지는 $\int f v\,dt$ |
| 수동(passive) | 저장 함수 $V \ge 0$ 가 있어 $\dot V \le f v$ (= 공급받은 것보다 더 내놓지 않는다) |
| $Z(s)$ | 임피던스 $F(s)/V(s)$. 수동 $\iff$ $Z$ 가 양실(positive real), 특히 $\operatorname{Re}Z(j\omega)\ge0$ |
| $K, B$ | 가상 벽의 강성·감쇠(제어기 안의 수) |
| $b$, $m$ | 장치의 **물리** 감쇠·질량 |
| $T$ | 샘플링 주기. $\theta := \omega T$ |

이 레슨의 두 달리는 예는 ⓐ 2링크 평면 매니퓰레이터(R2·R3)와 ⓑ 1-DOF 햅틱 장치에 구현한
**가상 벽**(R5)이다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (수동성 정리와 피드백 결합 안정성) [D3]** — 두 수동 계를 음의 피드백으로 결합하면
  ($u_1 = -y_2$, $u_2 = y_1$) 결합계는 수동이고 그 저장 함수는 $V_1+V_2$ 다. 한쪽이
  **출력 강수동(output strictly passive)** 이고 영상태 검출성(zero-state detectability)이
  있으면 결합계의 원점은 점근 안정이다.
- **R2 (매니퓰레이터의 수동성) [D2]** — 크리스토펠 선택의 $C$ 에 대해
  $\tfrac12\dot M - C$ 는 **반대칭**이고, 따라서 $V = \tfrac12\dot q^\top M \dot q + U$ 는
  $$
  \dot V = \dot q^\top \tau + \dot q^\top \tau_{\text{ext}} \tag{1}
  $$
  를 만족한다. 즉 로봇은 $(\tau, \dot q)$ 포트에서 **정확히 수동**이다(손실 없음).
- **R3 (에너지 성형과 댐핑 주입) [D2]** — 완전 구동계에서
  $$
  \tau = g(q) - K_p (q - q_d) - K_d \dot q \tag{2}
  $$
  를 쓰면 성형된 에너지 $V_d = \tfrac12 \dot q^\top M \dot q + \tfrac12 (q-q_d)^\top K_p (q-q_d)$ 가
  $\dot V_d = -\dot q^\top K_d \dot q \le 0$ 를 만족하고, LaSalle 로 $q \to q_d$, $\dot q \to 0$.
  **중력 보상만 남기고 $U$ 를 원하는 $U_d$ 로 "교체"하는 것**이 요점이다. 언더액추에이티드
  계에서는 같은 일을 하려면 정합 방정식(matching equations)을 풀어야 한다(IDA-PBC). **[D1]**
- **R4 (임피던스 제어와 결합 안정성) [D2]** — 목표 임피던스
  $M_d\ddot e + B_d \dot e + K_d e = -f_{\text{ext}}$ ($e = q - q_d$)를 실현하는 제어기는
  환경이 **임의의 수동 계**여도 안정하다 — 단 제어기가 포트에서 수동일 때만. 선형 1-DOF 에서
  그 조건은 $\operatorname{Re}Z_c(j\omega) \ge 0$ 이고, 질량 성형($M_d \ne m$)은 힘 측정을
  요구하며 수동성을 깨뜨릴 수 있다.
- **R5 (샘플링된 가상 벽의 에너지 경계) [D2]** — 영차 유지(ZOH)로 구현한 가상 벽
  $F_k = -Kx_k - B(x_k - x_{k-1})/T$ 와 물리 감쇠 $b$ 로 이루어진 포트에, 정현 운동
  $x(t) = A\sin(\omega t + \varphi)$ 를 넣으면 한 주기당 포트로 **들어가는** 에너지가
  $$
  W = A^2 N\left\{\sin^2\!\tfrac{\theta}{2}\left[-K + \tfrac{2B}{T}\cos\theta\right]
    + \frac{b\,\theta^2}{2T}\right\},\qquad \theta = \omega T,\ N = \frac{2\pi}{\theta} \tag{3}
  $$
  로 **닫힌 형태**로 나온다. 따라서 정현 운동에 대한 수동성은
  $$
  b \;\ge\; g(\theta) := \frac{2T}{\theta^2}\sin^2\!\frac{\theta}{2}
    \left[K - \frac{2B}{T}\cos\theta\right] \quad \forall \theta \in (0,\pi] \tag{4}
  $$
  와 동치다. $\theta\to0$ 극한은 $KT/2 - B$, $\theta = \pi$ 는 $2KT/\pi^2 + 4B/\pi^2$ 이고,
  고전적 Colgate–Schenkel 충분조건 $b > KT/2 + \lvert B\rvert$ 는 $B \le 0$ 에서 (4)의
  최댓값과 **정확히 일치**하고 $B>0$ 에서는 보수적이다(수치: $K=2000$, $T=1$ms, $B=0.5$ 에서
  $\max_\theta g = 0.85568$ vs $KT/2+\lvert B\rvert = 1.5$).

## 유도

### R2 — 매니퓰레이터가 포트에서 수동이라는 것

**1단계 (반대칭 구조).** $C$ 를 크리스토펠 기호로 정의하면
$C_{ij} = \sum_k \tfrac12\left(\frac{\partial M_{ij}}{\partial q_k} + \frac{\partial M_{ik}}{\partial q_j}
- \frac{\partial M_{kj}}{\partial q_i}\right)\dot q_k$ 이고, $\dot M_{ij} = \sum_k \frac{\partial M_{ij}}{\partial q_k}\dot q_k$
이므로

$$
\left(\tfrac12\dot M - C\right)_{ij}
  = \sum_k \tfrac12\left(\frac{\partial M_{kj}}{\partial q_i} - \frac{\partial M_{ik}}{\partial q_j}\right)\dot q_k
$$

이고 $i \leftrightarrow j$ 를 바꾸면 괄호 안의 부호가 뒤집힌다($M$ 의 대칭성 $M_{kj}=M_{jk}$ 를
쓴다). 따라서 $S := \tfrac12\dot M - C$ 는 반대칭이고 특히

$$
\dot q^\top \left(\tfrac12 \dot M - C\right)\dot q = 0 \qquad \forall \dot q. \tag{5}
$$

**수치 확인**: 2링크 평면 팔에서 $q$ 와 $\dot q$ 를 무작위로 2000번 뽑아
$\dot M$ 을 중앙 차분($h=10^{-7}$)으로 계산하면 $\max\lVert S + S^\top\rVert_{\max} = 5.6\cdot10^{-9}$,
$\max\lvert \dot q^\top S \dot q\rvert = 3.4\cdot10^{-8}$ 로 차분 오차 수준이다.

**2단계 (에너지 미분).** $V = \tfrac12\dot q^\top M\dot q + U(q)$ 를 미분하고 동역학을 대입한다:

$$
\dot V = \dot q^\top M\ddot q + \tfrac12 \dot q^\top \dot M \dot q + \dot q^\top \frac{\partial U}{\partial q}
  = \dot q^\top(\tau + \tau_{\text{ext}} - C\dot q - g) + \tfrac12\dot q^\top \dot M\dot q + \dot q^\top g,
$$

$g = \partial U/\partial q$ 로 중력 항이 **상쇄**되고 (5)로 $C$ 항도 사라져 (1)이 남는다. 즉
로봇은 에너지를 **만들지도 잃지도** 않는다(마찰이 없다면). 수동성의 정의
$\dot V \le \dot q^\top \tau$ 가 등호로 성립하므로 로봇은 **무손실(lossless)** 이다.

**가정이 깨지는 곳**: ⓐ $C$ 를 크리스토펠 선택이 아닌 다른 방식으로 쓰면 (5)가 성립하지 않는다
— $M\ddot q + C\dot q$ 가 같은 값을 주는 $C$ 는 여러 개이고 그중 반대칭 성질을 갖는 것은
크리스토펠 선택이다. ⓑ 관절 유연성·감속기 마찰·구동기 동역학을 넣으면 포트가 $(\tau,\dot q)$
에서 **옮겨 가고**, 모터 쪽에서 본 수동성은 따로 보여야 한다. ⓒ 이산 구현은 수동성을 깨뜨린다 —
그것이 R5 다.

### R3 — 에너지 성형과 댐핑 주입

**1단계 (에너지를 바꿔 끼운다).** 목표는 원하는 위치 에너지 $U_d(q)$ (최소점이 $q_d$)를 가진
계처럼 행동하게 만드는 것이다. (2)에서 $g(q)$ 항이 실제 중력을 **지우고**,
$-K_p(q-q_d)$ 가 $-\partial U_d/\partial q$ 로 $U_d = \tfrac12(q-q_d)^\top K_p (q-q_d)$ 를
**넣는다**. 남은 $-K_d\dot q$ 가 댐핑 주입이다.

**2단계 (성형된 에너지의 미분).** $V_d = \tfrac12\dot q^\top M\dot q + U_d(q)$ 에 R2 의 계산을
그대로 반복하면(이번에는 $\tau$ 에 (2)를 대입)

$$
\dot V_d = \dot q^\top\left(\tau - g + \frac{\partial U_d}{\partial q}\right)
  = \dot q^\top\left(-K_p(q-q_d) - K_d\dot q + K_p(q-q_d)\right) = -\dot q^\top K_d \dot q \le 0. \tag{6}
$$

**3단계 (LaSalle 로 수렴).** $V_d$ 는 $(q_d, 0)$ 에서 양정이고 $K_p \succ 0$ 이면 준위집합이
유계다. $\dot V_d = 0 \iff \dot q = 0$ 이고, $\dot q \equiv 0$ 인 해는 $\ddot q = 0$ 이어야 하므로
(2)를 동역학에 넣으면 $K_p(q-q_d) = 0$, 즉 $q = q_d$. $E$ 안에 머무는 해가 그 점뿐이므로
`c3-lyapunov-stability` 의 R3(Barbashin–Krasovskii)로 **점근 안정**이다.

**수치 확인**: 2링크 팔, $K_p = \operatorname{diag}(25,16)$, $K_d = \operatorname{diag}(10,6)$,
$q_0 = (-1.0,\ 1.5)$, $q_d = (0.3,\ -0.6)$ 에서 RK4($\Delta t = 10^{-3}$)로 15초 적분하면
$\lvert q - q_d\rvert_\infty = 2.9\cdot10^{-12}$ 이고 에너지 수지
$\lvert V_d(t) - V_d(0) + \int_0^t \dot q^\top K_d\dot q\,ds\rvert$ 의 최댓값이 $7.0\cdot10^{-4}$,
$V_d(0) = 56.4$ 기준 상대오차 $1.2\cdot10^{-5}$ (적분·구적 오차 수준)다.

**가정이 깨지는 곳**: (2)는 **완전 구동**을 전제한다. 입력이 상태보다 적으면 $g$ 를 지우는 일조차
불가능하고, "원하는 에너지" 를 넣으려면 $U_d$ 가 아무 함수여도 되는 게 아니라 **정합 방정식**
(PDE)을 만족해야 한다 — IDA-PBC(Ortega et al. 2002)의 본체가 그 PDE 를 푸는 일이다. 또 (6)은
모델의 $g$ 가 정확하다고 가정한다. $\hat g \ne g$ 면 정상상태 오차가
$K_p^{-1}(\hat g - g)$ 만큼 남는다 — 이 오차를 적응으로 지우는 것이 `c3-adaptive-control` 이다.

### R5 — 샘플링된 가상 벽의 한 주기 에너지 (닫힌 형태)

**설정.** 1-DOF 장치의 위치를 $x$, 포트 변수를 $(f, v=\dot x)$ 로 둔다. 제어기는 주기 $T$ 로
$x$ 를 샘플해 힘을 **한 주기 동안 유지**한다:

$$
F_k = -K x_k - \frac{B}{T}\left(x_k - x_{k-1}\right), \qquad t \in [kT, (k+1)T). \tag{7}
$$

속도는 측정하지 않고 위치의 후진 차분으로 만든다(실제 햅틱 장치의 표준 구현). 포트는 "가상 벽
+ 물리 감쇠 $b$" 이고, 사용자가 공급하는 에너지는 운동을 지정하면 계산된다.

**1단계 (운동을 지정하고 에너지를 적분).** $x(t) = A\sin(\omega t + \varphi)$ 로 두고 한 주기당
포트로 들어가는 에너지를 쓴다. 보존 요소(가상 스프링·운동 에너지)는 한 주기 뒤 제자리이므로

$$
W = \int_{\text{1 cycle}}\left(-F\,v + b\,v^2\right)dt
  = \underbrace{\sum_k \left(-F_k\right)\left(x_{k+1}-x_k\right)}_{\text{유지된 힘의 일}}
    + \underbrace{\pi b A^2\omega}_{\int b v^2}. \tag{8}
$$

($F$ 가 각 구간에서 상수이므로 $\int F v\,dt = F_k \Delta x_k$ 로 **정확히** 떨어진다. 이것이
닫힌 형태가 나오는 이유다.)

**2단계 (두 합을 삼각 항등식으로).** $\theta := \omega T$ 가 한 주기를 정수 $N = 2\pi/\theta$ 개의
샘플로 나눈다고 하자. $x_k = A\sin(\theta k + \varphi)$ 에 대해 표준 합

$$
\sum_{k=1}^{N} x_k x_{k+1} = \frac{A^2N}{2}\cos\theta, \qquad \sum_{k=1}^N x_k^2 = \frac{A^2N}{2}
$$

을 쓰면 스프링 항은

$$
\sum_k K x_k(x_{k+1}-x_k) = \frac{KA^2N}{2}(\cos\theta - 1) = -K A^2 N \sin^2\frac{\theta}{2}.
$$

감쇠 항은 차분 $d_k := x_k - x_{k-1} = 2A\sin\frac{\theta}{2}\cos\!\left(\theta(k-\tfrac12)+\varphi\right)$
(진폭 $2A\sin\frac\theta2$)에 같은 합을 적용해

$$
\sum_k \frac{B}{T} d_k\,d_{k+1} = \frac{B}{T}\cdot\frac{(2A\sin\frac\theta2)^2 N}{2}\cos\theta
  = \frac{2BA^2N}{T}\sin^2\frac{\theta}{2}\cos\theta.
$$

마지막으로 $\pi b A^2\omega = b A^2 N\theta^2/(2T)$ ($\pi = N\theta/2$, $\omega = \theta/T$)를
더하면 (3)이다. $\varphi$ 는 **사라진다** — 한 주기 평균이므로 위상에 무관하다.

**3단계 (수동성 조건).** $W \ge 0$ 을 모든 $\theta \in (0,\pi]$ 와 모든 $A$ 에 대해 요구하면
$A^2$ 과 $N>0$ 이 약분되어 (4)가 남는다. 두 극한이 의미를 준다:

$$
\lim_{\theta\to0} g(\theta) = \frac{KT}{2} - B, \qquad
  g(\pi) = \frac{2KT}{\pi^2} + \frac{4B}{\pi^2}. \tag{9}
$$

$\theta\to0$ 항의 $KT/2$ 가 **샘플링이 만드는 음의 감쇠**다: 유지된 힘이 반 주기만큼 늦게
작용해 매 주기 $K A^2 \theta^2/4$ 만큼의 에너지를 주입하고, 이것이 등가 감쇠 $-KT/2$ 로 보인다.
$-B$ 는 후진 차분 감쇠가 저주파에서 정상 감쇠처럼 **도움이 되는** 몫이고, $\cos\theta$ 때문에
$\theta$ 가 $\pi$ 에 가까워지면 그 부호가 뒤집혀 **해로워진다**.

**수치 (모두 실행 확인, $T = 1$ms)**

| $K$ | $B$ | $\max_\theta g$ (최적 $\theta$) | $KT/2 - B$ | $KT/2+\lvert B\rvert$ |
|---|---|---|---|---|
| 2000 | 0 | $1.00000$ ($\theta\to0$) | 1.0000 | 1.0000 |
| 2000 | $+0.5$ | $0.85568$ ($0.648\pi$) | 0.5000 | 1.5000 |
| 1000 | $+0.5$ | $0.52506$ ($0.742\pi$) | 0.0000 | 1.0000 |
| 2000 | $+1.0$ | $1.05012$ ($0.742\pi$) | 0.0000 | 2.0000 |
| 2000 | $-0.5$ | $1.50000$ ($\theta\to0$) | 1.5000 | 1.5000 |

닫힌 형태 (3)은 직접 합산과 상대오차 $10^{-6}$ 이내로 일치한다($K=2000$, $B=0.5$, $N=8$,
$b=1$: 직접 $952.6815$, 닫힌 형태 $952.6825$).

**안정 경계와 수동성 경계는 다르다.** 같은 가상 벽을 **환경 없이**(장치만) 닫으면, 이산 전이
행렬의 스펙트럼 반지름이 1 이 되는 임계 감쇠는 수치적으로

$$
b_{\text{stab}} = \max\left(0,\ \frac{KT}{2} - B\right) \tag{10}
$$

다($K=2000, B=0$: $0.99983$ vs $1$; $K=2000, B=0.5$: $0.50042$ vs $0.5$; $K=1000, B=0.5$:
$0.00031$ vs $0$). 따라서

$$
\underbrace{\frac{KT}{2}-B}_{\text{그 한 환경에서 안정}}
  \;\le\; \underbrace{\max_\theta g(\theta)}_{\text{정현 운동에 대한 수동}}
  \;\le\; \underbrace{\frac{KT}{2}+\lvert B\rvert}_{\text{Colgate–Schenkel 충분조건}} \tag{11}
$$

이고 $B\le0$ 에서는 셋이 **일치**한다. 가운데 값이 "정현 운동" 으로만 탐침한 결과이므로 참
수동성 문턱의 **하한**이고, 오른쪽은 **상한**이다(고조파가 섞인 운동은 더 많은 에너지를 뽑을 수
있다). 실무의 뜻: 수동성을 요구하면 (사람이 어떻게 밀어도 안전하지만) 강성 $K$ 의 상한이
$2b/T$ 수준으로 묶이고, 특정 환경에 대한 안정만 요구하면 더 높은 강성을 쓸 수 있지만
**사람이 다른 방식으로 밀면 불안정해질 수 있다**. 이 교환이 햅틱의 Z-width 다
(Colgate & Brown 1994).

**가정이 깨지는 곳**: (3)은 ⓐ 선형 가상 벽(상시 접촉), ⓑ 정현 운동, ⓒ 양자화·지연 없음,
ⓓ $\omega T$ 가 한 주기를 정수로 나눔을 가정한다. 실제 벽은 접촉/비접촉이 전환되는
**비선형**이고(접촉 진입 시점이 샘플 격자에 걸려 추가 에너지가 주입된다), 양자화와 통신 지연은
음의 감쇠를 더 키운다. 그래서 (11)의 오른쪽조차 실제 장치에서는 낙관적일 수 있다.

## 증명 스케치

### R1 — 수동 계의 피드백 결합

**가설** H1: 두 계 $\Sigma_i$ 가 저장 함수 $V_i \ge 0$ 와 함께 수동, 즉 $\dot V_i \le u_i^\top y_i$.
H2: 결합은 $u_1 = -y_2 + e$, $u_2 = y_1$ (음의 피드백). H3(점근성용): $\Sigma_1$ 이 출력 강수동
($\dot V_1 \le u_1^\top y_1 - \rho(\lvert y_1\rvert)$, $\rho$ 양정)이고 $\Sigma_2$ 가
영상태 검출 가능($y_2 \equiv 0$, $u_2 \equiv 0 \Rightarrow x_2 \to 0$).
**결론** C: $e=0$ 이면 $V=V_1+V_2$ 가 비증가이므로 원점은 안정하고, H3 아래에서는 점근 안정이다.

**전략**: 에너지를 더한다. 결합의 핵심은 **교차 항이 정확히 상쇄**된다는 것뿐이다.

1. $V := V_1 + V_2$ 로 두고 H1 을 더한다:
   $\dot V \le u_1^\top y_1 + u_2^\top y_2$.
2. H2 를 넣으면 $u_1^\top y_1 + u_2^\top y_2 = (-y_2+e)^\top y_1 + y_1^\top y_2 = e^\top y_1$.
   **$y_1^\top y_2$ 가 서로 지워진다** — 이 한 줄이 수동성 정리의 전부다.
3. 따라서 $e \equiv 0$ 이면 $\dot V \le 0$ 이고 `c3-lyapunov-stability` 의 R1 로 안정.
   $e \ne 0$ 이면 $\dot V \le e^\top y_1$ 이므로 $L_2$ 안정성(유한 이득)이 따라온다.
4. (점근성) H3 로 $\dot V \le -\rho(\lvert y_1\rvert)$ 이므로 LaSalle 을 쓰면 $y_1 \to 0$ 이고,
   $y_1 = -u_2 \to 0$ 에서 $\Sigma_2$ 의 검출성으로 $x_2 \to 0$, 다시
   $u_1 = -y_2 \to 0$ 에서 $\Sigma_1$ 의 검출성으로 $x_1\to0$.

**가설을 지우면**: H1 의 **저장 함수의 비음성**을 빼면 1단계가 무너진다 — 에너지를 "빚질" 수
있는 계는 결합에서 그 빚을 상대에게 넘긴다. 출력 강수동성(H3)이 없으면 결론은 안정까지이고
점근성은 없다(무손실 두 계를 결합하면 영원히 진동한다). 환경이 **수동이 아니면**(사람이
능동적으로 힘을 넣거나, 다른 제어기가 에너지를 주입하면) 정리 자체가 적용되지 않는다 — 이것이
수동성 기반 설계의 가장 흔한 실제 실패다.

생략한 기술적 단계: 저장 함수의 미분가능성과 영상태 검출성의 정확한 정의(Khalil ch.6 과
ch.14.2, Colgate–Hogan 1988 §3).

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R2)** 크리스토펠 선택의 $C$ 에 대해 $\tfrac12\dot M - C$ 가 반대칭임을 성분으로
증명하라. 이어서 $C' = C + S'$ ($S'$ 는 $S'\dot q = 0$ 을 만족하는 비영 행렬)로 바꾸면 (5)가
어떻게 되는지 쓰라.
*해답 스케치*: 본문 1단계의 성분 계산을 그대로 쓰되 $M_{kj}=M_{jk}$ 를 명시적으로 호출한다.
$C'$ 는 동역학을 바꾸지 않지만 (5)는 $\dot q^\top(\tfrac12\dot M - C')\dot q = -\dot q^\top S'\dot q$
로 바뀌어 일반적으로 0 이 아니다 — **수동성 증명은 $C$ 의 선택에 의존한다.**

**P2 (유도, ★★★, R5)** (3)을 유도하라. 두 삼각 합
$\sum x_kx_{k+1}$, $\sum x_k^2$ 를 직접 계산하고, 차분 $d_k$ 의 진폭이
$2A\sin(\theta/2)$ 인 이유를 쓰라. 위상 $\varphi$ 가 사라지는 단계를 지목하라.
*해답 스케치*: $\sin a \sin b = \tfrac12[\cos(a-b)-\cos(a+b)]$ 와 $\sum_k \cos(2\theta k + c) = 0$
($\theta N = 2\pi$)를 쓴다. $d_k$ 는 $\sin(\theta k+\varphi) - \sin(\theta(k-1)+\varphi)$ 를
곱셈 공식으로 묶으면 나온다. $\varphi$ 는 두 합 모두 $\varphi$-독립이라 2단계에서 사라진다.

**P3 (계산, ★, R5)** $K = 2000$ N/m, $T = 1$ ms 에서 ⓐ $B=0$, ⓑ $B=+0.5$, ⓒ $B=-0.5$ 에 대해
$\max_\theta g(\theta)$ 와 그 $\theta$ 를 구하라.
*정답*: ⓐ $1.00000$, $\theta\to0$ ⓑ $0.85568$, $\theta = 2.03531\,\text{rad} = 0.648\pi$
ⓒ $1.50000$, $\theta\to0$. 허용오차 $10^{-4}$. 검산: ⓐ·ⓒ 는 (9)의 $KT/2-B$ 와 일치해야 하고,
ⓑ 는 $(KT/2-B,\ KT/2+\lvert B\rvert) = (0.5,\ 1.5)$ 의 **내부**에 있어야 한다.

**P4 (계산, ★, R3)** $K_p = \operatorname{diag}(25,16)$ 이고 중력 모델에 $\hat g = g + \epsilon$
($\epsilon = (0.5, -0.2)^\top$ N·m)의 오차가 있을 때 (2)의 정상상태 오차 $q_\infty - q_d$ 를
구하라.
*정답*: $K_p^{-1}\epsilon = (0.02,\ -0.0125)^\top$ rad (허용오차 $10^{-9}$). 검산: 정상상태에서
$\ddot q = \dot q = 0$ 을 (2)와 동역학에 넣으면 $K_p(q-q_d) = \hat g - g$.

**P5 (구현, ★★, R4·R5)** 1-DOF 가상 벽을 ⓐ 연속 시간, ⓑ ZOH 샘플링, ⓒ ZOH + 1-스텝 지연으로
구현하고 $(K, b)$ 평면에서 안정 영역을 그려라.
*루브릭*: ⓐ 는 모든 $K>0$ 에서 안정 ⓑ 는 (10)의 경계를 1% 이내로 재현 ⓒ 는 경계가 더
보수적으로 내려간다(지연이 음의 감쇠를 키운다) ⓓ 세 경우를 한 도표에 그리고 축을 $KT$ 로
정규화했다.

**P6 (반례, ★★, R1)** "임피던스 제어기는 수동이므로 어떤 환경과 결합해도 안정하다" 는 주장을
반박하라. ① 환경이 수동이 아닌 예, ② 환경은 수동인데 **구현**이 수동이 아니어서 깨지는 예를
각각 들라.
*성질 체크리스트*: ① 사람·다른 제어기·능동 보조기(에너지 주입원)를 포트에 붙이면 R1 의 H1 이
깨진다. ② (11)에서 $b < \max_\theta g$ 인 디지털 구현 — 수동 환경(스프링·질량)만 붙어도
에너지가 주입된다. $Z_c(j\omega)$ 의 실수부가 음이 되는 주파수를 제시하면 완성.

**P7 (논문, ★★, R4·R5)** Colgate & Schenkel 1997 과 Colgate & Hogan 1988 을 읽고 ⓐ 두 논문이
각각 **무엇에 대해** 안정성을 주장하는지(한 환경 vs 환경 전체), ⓑ 그 차이가 설계 자유도
($K$ 의 상한)에 주는 결과, ⓒ 저자들이 측정하지 않아 재현을 막는 양 2개를 쓰라.
*루브릭*: "포트 수동성은 환경 전체에 대한 보장이고 그 대가가 강성 상한" 을 짚으면 통과.
마찰·양자화·속도 추정 방식 중 빠진 것을 지목하면 가점.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Hogan, "Impedance control: an approach to manipulation" (1985, ASME JDSMC)**
   — 역할: `원전(seminal)`. <https://doi.org/10.1115/1.3140713>
   확인된 것은 Part II/III 의 1985 JDSMC 판이다(Part I 은 ACC 1984).
   추가 질문: ⓐ 저자가 "위치 제어도 힘 제어도 충분하지 않다" 고 말하는 근거는 무엇인가 —
   환경의 무엇을 모른다고 가정하는가? ⓑ 질량 성형($M_d \ne m$)이 요구하는 측정과 그 대가는?
2. **Colgate & Hogan, "Robust control of dynamically interacting systems" (1988, Int. J. Control)**
   — 역할: `원전(seminal)`. <https://doi.org/10.1080/00207178808906161>
   추가 질문: ⓐ 결합 안정성 조건을 Nyquist 선도로 읽는 방법을 한 문단으로 쓰라.
   ⓑ "환경이 수동" 이라는 가정이 실제 조작 작업에서 깨지는 경우를 둘 들라.
3. **Colgate & Schenkel, "Passivity of a class of sampled-data systems: application to haptic
   interfaces" (1997, J. Robotic Systems)** — 역할: `표준(standard)`.
   <https://doi.org/10.1002/(SICI)1097-4563(199701)14:1<37::AID-ROB4>3.0.CO;2-V>
   재현 과제의 원형이다. 우리 (4)와 저자들의 조건을 **같은 기호로** 나란히 적어 비교한다.
   추가 질문: ⓐ 저자들의 조건은 필요조건인가 충분조건인가, 그 판정은 어떤 운동 집합에 대한
   것인가? ⓑ $B>0$ 에서 우리 (4)의 최댓값이 $KT/2+\lvert B\rvert$ 보다 작은 이유를 설명할 수
   있는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 10분 이내, numpy 만(SDP 불필요).
대상은 ⓐ 1-DOF 가상 벽(조건 1–3)과 ⓑ 2링크 매니퓰레이터(조건 4)다. 입력 데이터는 없다.

**수용 기준 (네 조건 모두)**

1. **안정 경계**: ZOH 가상 벽 + 물리 감쇠의 이산 전이 행렬을 세우고, $(K,B) \in
   \{500,1000,2000\}\times\{0,\ 0.5\}$ 에 대해 스펙트럼 반지름이 1 이 되는 $b$ 를 이분법으로
   찾아 (10)과 **상대오차 1% 이내**로 일치시킨다. 참조값: $(2000,0) \to 0.99983$,
   $(2000,0.5) \to 0.50042$, $(1000,0.5) \to 0.00031$, $(1000,0) \to 0.49996$,
   $(500,0) \to 0.24999$.
2. **닫힌 형태 검증**: 한 주기 에너지를 ⓐ 직접 적분(구간당 $\ge 200$ 분할)과 ⓑ 식 (3)으로
   계산해 **상대오차 $10^{-5}$ 이내**로 일치. 최소 3개의 $(K,B,N,b)$ 조합에서 확인하고,
   그중 하나는 $B<0$ 이어야 한다. 참조값: $(K,B,N,b) = (2000,0.5,8,1)$ 에서 직접 $952.6815$,
   닫힌 형태 $952.6825$.
3. **세 경계의 순서**: $(K,B)$ 격자에서 $\max_\theta g(\theta)$ 를 수치로 구해 (11)의 순서
   $KT/2-B \le \max_\theta g \le KT/2+\lvert B\rvert$ 가 **모든 격자점에서** 성립함을 확인하고,
   $B \le 0$ 에서 세 값이 $10^{-6}$ 이내로 일치함을 확인한다. $B = +0.5$, $K=2000$ 에서
   $\max_\theta g = 0.85568 \pm 10^{-4}$ (최적 $\theta = 0.648\pi$).
4. **매니퓰레이터 쪽**: ⓐ 무작위 $(q,\dot q)$ $10^3$ 개에서 $\max\lVert S+S^\top\rVert_{\max} <
   10^{-7}$ (중앙 차분 $h=10^{-7}$) ⓑ (2)의 제어기를 RK4($\Delta t \le 10^{-3}$)로 15초 적분해
   $\lvert q-q_d\rvert_\infty < 10^{-9}$ 이고 에너지 수지의 **상대**오차가 $10^{-4}$ 미만
   (참조: $2.9\cdot10^{-12}$, 상대 $1.2\cdot10^{-5}$).

**비교 대상**: ⓐ 연속시간 구현 — 모든 $K>0$, $b\ge0$ 에서 안정해야 한다(이산화가 원인임을
분리하는 대조군) ⓑ Colgate–Schenkel 충분조건 $b>KT/2+\lvert B\rvert$ — 조건 3 의 상한
ⓒ 조건 1·2·3 의 참조 수치.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 안정 경계가 (10)의 **2배**로 나온다 | 가상 감쇠를 $B(x_k-x_{k-1})/T$ 가 아니라 연속 속도로 구현했다 | $B=0$ 으로 두고 경계가 $KT/2$ 가 되는지 먼저 확인한다 |
| 조건 2 의 직접 적분이 안 맞는다 | 힘을 구간 안에서 **다시 계산**했다(ZOH 위반) | 한 구간에서 $F$ 가 상수인지 출력해 본다 |
| $\max_\theta g$ 가 $KT/2+\lvert B\rvert$ 를 넘는다 | $\cos\theta$ 부호 또는 $2B/T$ 계수 오류 | $B<0$ 에서 $\theta\to0$ 극한이 $KT/2+\lvert B\rvert$ 인지 확인한다 |
| 조건 4ⓐ 가 $10^{-5}$ 수준에서 멈춘다 | $\dot M$ 을 전진 차분으로, 또는 $h$ 를 너무 크게 잡았다 | 중앙 차분 + $h=10^{-7}$ 로 바꾸고 $h$ 를 10배 바꿔 오차가 $h^2$ 로 줄는지 본다 |
| 에너지 수지가 발산한다 | 소산 적분을 오일러로 누적했다 | Simpson 구적으로 바꾸고 $\Delta t$ 를 절반으로 줄여 확인한다 |

## 열린 문제

- **(열린 문제) 학습된 가변 임피던스의 수동성 보장** — 작업에 따라 임피던스를 바꾸는 것이
  성능에 유리하지만, 시변 이득은 **에너지를 주입할 수 있다**($\dot K_d > 0$ 이면 저장 함수가
  커진다). 현재 접근: 강화학습으로 임피던스를 학습하는
  [Buchli et al. 2010](https://doi.org/10.15607/RSS.2010.VI.020), 에너지 탱크(energy tank)로
  주입량을 회계 처리하는 방식. 비어 있는 자리: 학습된 정책 전체에 대해 **구성적으로** 수동성을
  보장하면서 성능 손실을 정량화하는 방법.
- **(열린 문제) 지연·통신이 있는 포트의 수동성** — 원격 조작은 왕복 지연이 에너지를 주입한다.
  파동 변수(wave variable)로 지연에 무관한 수동성을 얻을 수 있지만
  ([Niemeyer & Slotine 1991](https://doi.org/10.1109/48.64895)) 투명성(transparency)을 잃는다.
  비어 있는 자리: 가변 지연·패킷 손실 아래에서 수동성과 투명성의 달성 가능한 경계.
- **(열린 문제) 구현 가능한 임피던스 범위(Z-width)의 이론적 한계** — 샘플링·양자화·마찰·센서
  잡음이 함께 작용할 때 수동으로 구현 가능한 $(K,B)$ 영역의 **정확한** 경계는 알려져 있지 않다.
  현재 접근: [Colgate & Brown 1994](https://doi.org/10.1109/ROBOT.1994.351077) 의 실험적 Z-width,
  이 레슨의 (4) 같은 부분적 닫힌 형태. 비어 있는 자리: 양자화와 비선형 접촉 전환을 포함한 경계.
- **(열린 문제) 언더액추에이티드 계의 에너지 성형** — IDA-PBC 의 정합 방정식은 PDE 이고 일반해가
  없다. 현재 접근: [Ortega et al. 2002](https://doi.org/10.1109/TAC.2002.800770) 의 구성적 해법과
  특수 구조(비홀로노믹·보행 계)에 대한 사례별 해. 비어 있는 자리: 접촉이 바뀌는 계에서
  성형 가능한 에너지의 특성화 — `s3-legged-underactuated` 에서 다시 나온다.

## 개념 점검

`rc quiz c3-passivity-impedance` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c3-passivity-impedance-quiz
questions:
  - id: q1
    type: single
    prompt: "매니퓰레이터가 $(\\tau, \\dot q)$ 포트에서 수동임을 보일 때 결정적으로 쓰이는 구조는?"
    choices:
      - "$M(q) \\succ 0$ 이라는 사실"
      - "크리스토펠 선택의 $C$ 에 대해 $\\tfrac12\\dot M - C$ 가 반대칭이라는 사실"
      - "중력 항이 유계라는 사실"
      - "관절 마찰이 에너지를 소산한다는 사실"
    answer: 1
    explanation: "$\\dot V$ 를 전개하면 $\\dot q^\\top(\\tfrac12\\dot M - C)\\dot q$ 항이 남고, 크리스토펠 선택에서 이 항이 **정확히 0** 이다. $M \\succ 0$ 는 $V$ 가 양정임을 주지만 상쇄를 주지 않는다. 다른 $C$ 를 쓰면 이 상쇄가 깨진다."
    concept: { front: "매니퓰레이터 수동성의 핵", back: "$\\tfrac12\\dot M - C$ 의 반대칭성 — $\\dot q^\\top(\\tfrac12\\dot M-C)\\dot q = 0$. $C$ 의 선택에 의존한다" }
  - id: q2
    type: short
    prompt: "ZOH 로 구현한 가상 스프링 $K$ 가 저주파에서 만들어 내는 등가 음의 감쇠의 크기는? ($K$, $T$ 로)"
    answer: ["KT/2", "K*T/2", "KT / 2", "-KT/2", "K T / 2"]
    explanation: "(3)의 $\\theta \\to 0$ 극한에서 포트의 등가 감쇠는 $b - KT/2 + B$ 이므로, 샘플링된 스프링은 $-KT/2$ 만큼의 감쇠로 보인다. 유지된 힘이 반 주기 늦게 작용하면서 매 주기 에너지를 주입하기 때문이다."
    concept: { front: "샘플링된 가상 스프링의 음의 감쇠", back: "$-KT/2$ — 그래서 물리 감쇠가 $b \\ge KT/2$ 여야 수동이다(B=0)" }
  - id: q3
    type: truefalse
    prompt: "어떤 환경에 대해 안정한 디지털 임피던스 제어기는 모든 수동 환경에 대해서도 안정하다."
    answer: false
    explanation: "안정 경계는 $b > KT/2 - B$, 수동성 경계는 그보다 크다(최대 $KT/2 + |B|$). 그 사이의 이득은 **그 환경에서는** 안정하지만 다른 수동 환경(또는 다르게 밀는 사람)과 결합하면 에너지가 주입될 수 있다. 수동성은 환경 전체에 대한 보장이고, 그 대가가 강성 상한이다."
    concept: { front: "안정 경계 vs 수동성 경계", back: "$KT/2-B \\le$ 수동성 문턱 $\\le KT/2+|B|$ — 수동성은 모든 수동 환경에 대한 보장이라 더 보수적" }
  - id: q4
    type: single
    prompt: "완전 구동 매니퓰레이터에 $\\tau = g(q) - K_p(q-q_d) - K_d\\dot q$ 를 쓰면 $\\dot V_d$ 는?"
    choices:
      - "$-\\dot q^\\top K_p \\dot q$"
      - "$-\\dot q^\\top K_d \\dot q$"
      - "$-(q-q_d)^\\top K_p (q-q_d)$"
      - "$0$"
    answer: 1
    explanation: "$V_d = \\tfrac12\\dot q^\\top M\\dot q + \\tfrac12(q-q_d)^\\top K_p(q-q_d)$ 를 미분하면 중력과 $C$ 항이 상쇄되고 성형 항도 상쇄되어 댐핑 주입 항만 남는다. $\\dot V_d \\le 0$ 이고 등호는 $\\dot q = 0$ 에서만 — LaSalle 로 $q \\to q_d$."
    concept: { front: "에너지 성형 + 댐핑 주입의 에너지 미분", back: "$\\dot V_d = -\\dot q^\\top K_d\\dot q$ — 소산은 오직 주입한 댐핑에서 온다" }
```

## 이 단계 공부법

1. **반대칭 항등식을 성분으로 한 번 쓴다 (40분)** — P1 을 먼저 푼다. 크리스토펠 선택이
   **왜** 특별한지 성분 계산으로 보고 나면, 이후 모든 수동성 논증이 같은 상쇄의 반복으로 읽힌다.
2. **에너지 수지를 코드로 확인한다 (40분)** — (2)를 구현해
   $V_d(t) - V_d(0) + \int\dot q^\top K_d\dot q$ 가 0 인지 **수치로** 본다. 이 한 번의 확인이
   부호 실수를 전부 잡아 준다.
3. **R1 의 2단계만 외운다 (20분)** — 교차 항 $y_1^\top y_2$ 가 지워진다는 한 줄. 수동성 정리의
   나머지는 Lyapunov·LaSalle 의 재사용이다.
4. **가상 벽을 세 번 구현한다 (90분)** — 연속 → ZOH → ZOH + 지연. 재현 과제 조건 1 의 경계가
   $KT/2 - B$ 로 나오는 것을 보고, 지연을 넣으면 더 나빠지는 것을 본다. **디지털이 수동성을
   깨뜨린다** 를 손으로 겪는 단계다.
5. **(3)을 백지에서 유도한다 (90분)** — P2. 두 삼각 합이 전부이고, 유지된 힘의 일이
   $F_k\Delta x_k$ 로 정확히 떨어지는 것이 요점이다. 유도가 끝나면 (9)의 두 극한을 직접 확인한다.
6. **세 경계를 한 도표에 그린다 (60분)** — 조건 3. $B$ 를 음수까지 쓸어가며 세 선이
   $B\le0$ 에서 겹치고 $B>0$ 에서 벌어지는 모양을 본다. 이 그림이 이 레슨의 결론이다.
7. **논문은 "무엇에 대한 보장인가" 로 읽는다 (150분)** — Hogan 은 관계를, Colgate–Hogan 은
   환경 전체를, Colgate–Schenkel 은 디지털 구현을 다룬다. 보장의 **범위**가 각각 어떻게 다른지
   한 표로 정리하고 논문당 1페이지 노트를 쓴다.

**통과 기준**: 백지에서 (1)·(6)·(3)을 유도할 수 있고, 안정 경계와 수동성 경계가 왜 다른지
수로 설명할 수 있고, 재현 과제의 네 조건을 만족하는 코드와 논문 3편의 노트가 있다.
