---
id: c3-adaptive-control
title: 적응 제어와 지속 여진
summary: >-
  모르는 매개변수를 온라인으로 추정하면서 추적하는 Slotine–Li 적응 제어기를 Lyapunov 함수로
  유도하고, **추적은 되지만 매개변수는 수렴하지 않는다**는 사실과 그 경계를 지속 여진(persistent
  excitation)으로 정식화한다. 확실성 등가(certainty equivalence)의 함정과 모델링되지 않은
  동역학이 만드는 불안정(Rohrs 반례)까지 간 뒤, 강건 적응의 처방들을 비교한다.
objectives:
  - 매니퓰레이터 동역학의 선형 매개변수 구조 $Y(q,\dot q,\dot q_r,\ddot q_r)a$ 를 직접 구성할 수 있다.
  - Slotine–Li 적응 제어기의 Lyapunov 함수를 세우고 $\dot V = -s^\top K_D s$ 를 빠진 줄 없이 유도할 수 있다.
  - 지속 여진 조건을 적분 부등식으로 쓰고 그것이 왜 매개변수 수렴의 경계인지 설명할 수 있다.
  - 추적 오차는 0 인데 매개변수 오차가 남는 상황을 수치로 만들고 어느 열이 여진되지 않았는지 지목할 수 있다.
  - 모델링되지 않은 동역학 아래에서 적응이 불안정해지는 기구를 설명하고 강건 처방을 고를 수 있다.
prerequisites: [c3-lyapunov-stability, c3-passivity-impedance]
difficulty: 5
estimated_minutes: 540
tags: [nonlinear-control, adaptive-control, persistent-excitation, manipulator, research]
activities:
  - id: c3-adaptive-control-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c3-adaptive-control-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c3-adaptive-control-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: c3-adaptive-control-reproduction
    kind: reproduction
    title: 재현 과제 — PE 궤적에서만 매개변수가 수렴함을 보임 (R2)
    estimated_minutes: 105
  - id: c3-adaptive-control-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Khalil, Nonlinear Systems (3rd ed., 2002)"
    kind: book
    note: ch.9 (섭동과 평균화), ch.4.8 (비자율계의 비교 함수). PE 논증의 도구가 여기 있다. (공식 URL 미확인)
  - title: "Lynch & Park, Modern Robotics"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: ch.11.4 (적응 제어)와 ch.8.4 (선형 매개변수 구조). 전문 PDF 무료.
papers:
  - id: slotine1987-adaptive-manipulator
    required: true
    role: seminal
    note: "§2, §3"
  - id: boyd1986-pe
    required: true
    role: standard
    note: "§3, §4"
  - id: rohrs1985-unmodeled-dynamics
    required: true
    role: critique
  - id: cao2006-l1-adaptive
    role: standard
---

# 적응 제어와 지속 여진

## 전제와 기호

`c3-passivity-impedance` 의 에너지 성형은 중력 모델 $g(q)$ 가 정확하다고 가정했고, 모델 오차는
$K_p^{-1}(\hat g - g)$ 의 정상상태 오차로 남았다. 이 레슨은 그 오차를 **온라인 추정**으로 지운다.
핵심 질문은 두 개다: ⓐ 추정이 틀린 채로도 추적이 되는가(된다), ⓑ 추정이 참값으로 가는가
(**조건부로만** 간다).

전제: 라그랑주 동역학과 질량행렬 구조, `c3-lyapunov-stability` 의 LaSalle·비교 보조정리,
`c3-passivity-impedance` 의 반대칭 항등식 (5). 선형대수에서 Gram 행렬과 그 최소 고윳값.

| 기호 | 뜻 |
|---|---|
| $a \in \mathbb{R}^p$ | 참 매개변수 벡터(질량·관성·링크 길이의 조합) |
| $\hat a$, $\tilde a = \hat a - a$ | 추정값과 추정 오차 |
| $Y(q,\dot q,\dot q_r,\ddot q_r)$ | 회귀 행렬(regressor). $M\ddot q_r + C\dot q_r + g = Y a$ |
| $\tilde q = q - q_d$ | 추적 오차 |
| $\dot q_r = \dot q_d - \Lambda \tilde q$ | 기준 속도(reference velocity), $\Lambda \succ 0$ |
| $s = \dot q - \dot q_r = \dot{\tilde q} + \Lambda\tilde q$ | 필터된 오차(composite error) |
| $K_D \succ 0$, $\Gamma \succ 0$ | 피드백 이득, 적응 이득 |
| $W(t)$ | 궤적을 따라 평가한 회귀 행렬 $Y(q_d,\dot q_d,\dot q_d,\ddot q_d)$ |

달리는 예는 2링크 평면 매니퓰레이터이고, 매개변수를 다음 5개로 묶는다:

$$
a = \begin{bmatrix} m_1\ell_{c1}^2 + I_1 + m_2\ell_1^2 \\ m_2\ell_{c2}^2 + I_2 \\
  m_2\ell_1\ell_{c2} \\ (m_1\ell_{c1}+m_2\ell_1)g \\ m_2\ell_{c2}g \end{bmatrix}
  \;\xrightarrow{\text{본문 수치}}\;
  \begin{bmatrix} 1.333333 \\ 0.333333 \\ 0.5 \\ 14.715 \\ 4.905 \end{bmatrix}. \tag{1}
$$

($m_i = 1$ kg, $\ell_i = 1$ m, $\ell_{ci} = 0.5$ m, $I_i = 1/12$, $g = 9.81$.)

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (선형 매개변수 구조) [D2]** — 매니퓰레이터 동역학은 **매개변수에 선형**이다:
  $$
  M(q)\ddot q_r + C(q,\dot q)\dot q_r + g(q) = Y(q,\dot q,\dot q_r,\ddot q_r)\,a \tag{2}
  $$
  이고 $Y$ 는 알려진 함수다. 2링크 팔의 $Y$ 를 본문에서 성분까지 구성한다.
- **R2 (Slotine–Li 적응 제어기와 추적 수렴) [D3]** — 제어·적응 법칙
  $$
  \tau = Y\hat a - K_D s, \qquad \dot{\hat a} = -\Gamma Y^\top s \tag{3}
  $$
  에 대해 $V = \tfrac12 s^\top M s + \tfrac12\tilde a^\top \Gamma^{-1}\tilde a$ 가
  $$
  \dot V = -s^\top K_D s \le 0 \tag{4}
  $$
  를 만족한다. 따라서 $s \in L_2 \cap L_\infty$, $s \to 0$, 그리고 $s = \dot{\tilde q} + \Lambda\tilde q$
  이므로 $\tilde q \to 0$ 이다. **$\tilde a$ 는 유계일 뿐 0 으로 간다고 보장되지 않는다.**
- **R3 (지속 여진과 매개변수 수렴) [D3]** — $W(t)$ 가 **지속 여진(PE)** 이면, 즉
  $$
  \exists\,\alpha, T_0 > 0: \quad \int_t^{t+T_0} W(\sigma)^\top W(\sigma)\,d\sigma \succeq \alpha I
    \quad \forall t \ge 0, \tag{5}
  $$
  이면 $\tilde a \to 0$ 이 지수적으로 성립한다. 반대로 PE 가 깨지면($\alpha = 0$) 여진되지 않은
  방향의 매개변수 오차는 **영원히 남는다**. 선형 오차계에서 PE 는 지수 수렴의 **필요충분**
  조건이다(Boyd & Sastry 1986).
- **R4 (확실성 등가의 함정) [D2]** — 정지 목표(set-point)에서는 $W$ 의 랭크가 떨어져
  (2링크 팔에서 5개 열 중 **2개**, 중력 열만) 추적 오차가 $10^{-14}$ 로 떨어져도 관성 매개변수
  오차는 34% 로 **고정**된다. 즉 "잘 추적하므로 모델이 맞다" 는 추론은 틀렸다.
- **R5 (강건 적응) [D1]** — 모델링되지 않은 동역학이 있으면 (4)의 논증이 깨지고 매개변수
  표류(drift)와 버스팅(bursting)이 생긴다(Rohrs et al. 1985). 처방은 사영(projection),
  데드존(dead-zone), $\sigma$-수정, 그리고 적응 속도와 강건성을 저역 통과 필터로 분리하는
  $L_1$ 적응 제어다.

## 유도

### R1 — 2링크 팔의 회귀 행렬

(2)의 좌변을 (1)의 매개변수로 묶는다. 질량행렬과 중력은

$$
M(q) = \begin{bmatrix} a_1 + a_2 + 2a_3\cos q_2 & a_2 + a_3\cos q_2 \\
  a_2 + a_3 \cos q_2 & a_2\end{bmatrix}, \qquad
g(q) = \begin{bmatrix} a_4\cos q_1 + a_5 \cos(q_1+q_2) \\ a_5\cos(q_1+q_2)\end{bmatrix},
$$

이고 크리스토펠 선택의 $C$ 는 $h := -a_3 \sin q_2$ 로

$$
C(q,\dot q) = \begin{bmatrix} h\dot q_2 & h(\dot q_1 + \dot q_2) \\ -h\dot q_1 & 0\end{bmatrix}
$$

이다. $M\ddot q_r + C\dot q_r + g$ 를 전개해 $a_j$ 의 계수를 모으면

$$
Y = \begin{bmatrix}
\ddot q_{r1} & \ddot q_{r1}+\ddot q_{r2} &
  2c_2\ddot q_{r1} + c_2\ddot q_{r2} - s_2\dot q_2\dot q_{r1} - s_2(\dot q_1+\dot q_2)\dot q_{r2}
  & \cos q_1 & \cos(q_1+q_2) \\[2pt]
0 & \ddot q_{r1}+\ddot q_{r2} & c_2\ddot q_{r1} + s_2\dot q_1\dot q_{r1} & 0 & \cos(q_1+q_2)
\end{bmatrix} \tag{6}
$$

($c_2 = \cos q_2$, $s_2 = \sin q_2$). **수치 확인**: $\dot q_r = \dot q$, $\ddot q_r = \ddot q$ 로
두고 무작위 $(q,\dot q,\ddot q)$ 2000개에서
$\max\lvert Ya - (M\ddot q + C\dot q + g)\rvert = 7.1\cdot10^{-15}$ — 기계 정밀도다.

**가정이 깨지는 곳**: (2)는 **마찰과 구동기 동역학을 빼고** 쓴 것이다. 쿨롱 마찰
$\tau_f = F_c\operatorname{sgn}(\dot q)$ 는 매개변수에 선형이지만 $\operatorname{sgn}$ 이
비매끄러워 $\dot q = 0$ 근방에서 $Y$ 가 잘 정의되지 않고, 점성 마찰은 열을 더하면 되지만
여진 조건(R3)을 더 어렵게 만든다. 또 $\ddot q$ 를 쓰지 않는 것이 (3)의 설계 요점이다 —
가속도 측정은 잡음이 크기 때문에 $\ddot q_r$ (기준값, 계산 가능)만 쓴다.

### R2 — Lyapunov 함수와 추적 수렴

**1단계 (오차 동역학).** 동역학에 (3)을 넣고 $s = \dot q - \dot q_r$ 로 정리한다.
$M\dot s = M\ddot q - M\ddot q_r$ 이고 $M\ddot q = \tau - C\dot q - g$ 이므로

$$
M\dot s = Y\hat a - K_Ds - C\dot q - g - M\ddot q_r
  \overset{(2)}{=} Y\hat a - K_Ds - C\dot q - (Ya - C\dot q_r)
  = Y\tilde a - K_D s - Cs, \tag{7}
$$

즉 $M\dot s + Cs + K_Ds = Y\tilde a$. **중력과 $\ddot q_r$ 항이 (2) 덕분에 통째로 사라지는
것**이 이 한 줄의 요점이다.

**2단계 (Lyapunov 함수의 미분).** $V = \tfrac12 s^\top Ms + \tfrac12\tilde a^\top\Gamma^{-1}\tilde a$
를 미분하고 (7)을 넣는다. $\dot{\tilde a} = \dot{\hat a}$ 이므로

$$
\dot V = s^\top M\dot s + \tfrac12 s^\top \dot M s + \tilde a^\top\Gamma^{-1}\dot{\hat a}
  = s^\top\big(Y\tilde a - K_Ds - Cs\big) + \tfrac12 s^\top\dot Ms + \tilde a^\top\Gamma^{-1}\dot{\hat a}.
$$

여기서 `c3-passivity-impedance` 의 반대칭 항등식
$s^\top(\tfrac12\dot M - C)s = 0$ 이 $C$ 항을 지운다(이 항등식이 **$\dot q$ 가 아닌 임의의
벡터** $s$ 에 대해 성립한다는 점이 중요하다 — $\tfrac12\dot M - C$ 가 반대칭이므로 그렇다).
남은 것은

$$
\dot V = s^\top Y\tilde a - s^\top K_D s + \tilde a^\top \Gamma^{-1}\dot{\hat a}.
$$

(3)의 적응 법칙 $\dot{\hat a} = -\Gamma Y^\top s$ 를 넣으면
$\tilde a^\top\Gamma^{-1}(-\Gamma Y^\top s) = -\tilde a^\top Y^\top s = -s^\top Y\tilde a$ 로
**첫 항과 정확히 상쇄**되어 (4)가 남는다. 적응 법칙의 형태는 이 상쇄를 만들기 위해 **설계된**
것이다.

**3단계 (추적 오차로).** (4)에서 $V$ 가 비증가이므로 $s$ 와 $\tilde a$ 는 유계다. $V$ 가 아래로
유계이므로 $\int_0^\infty s^\top K_D s\,dt = V(0) - V(\infty) < \infty$, 즉 $s \in L_2$.
(7)에서 $\dot s$ 가 유계이므로 Barbalat 보조정리로 $s \to 0$. 마지막으로
$s = \dot{\tilde q} + \Lambda\tilde q$ 는 입력 $s$ 에 대해 지수 안정인 선형 필터이므로
$s \to 0 \Rightarrow \tilde q \to 0$, $\dot{\tilde q}\to0$ (`c3-lyapunov-stability` 의 R4,
ISS 추정식의 가장 단순한 사례다).

**가정이 깨지는 곳**: (4)는 $\tilde a$ 에 대해 **음반정부호**다 — $\dot V$ 에 $\tilde a$ 항이
전혀 없다. 따라서 Lyapunov 논증만으로는 $\tilde a \to 0$ 을 말할 수 없고, 실제로도 가지 않는다.
이 간극이 R3 다. 또 (3)은 $\Gamma$ 를 크게 잡으면 빨리 적응하지만, 모델링되지 않은 동역학이
있을 때 그 속도가 바로 불안정으로 바뀐다(R5).

### R4 — 추적은 되는데 매개변수는 틀린 경우 (수치)

2링크 팔에 $\Lambda = 4I$, $K_D = 20I$, $\Gamma = 20I$, $\hat a(0) = 0.5\,a$ 로 (3)을 돌렸다
(RK2 적분, $\Delta t = 5\cdot10^{-4}$, 180초).

| 궤적 | $\max\lvert\tilde q\rvert_\infty$ (마지막 10초) | $\lVert\tilde a\rVert/\lVert a\rVert$ (180초) | PE Gram $\lambda_{\min}$ (10초 창) |
|---|---|---|---|
| PE: $q_{d1} = 0.4\sin t + 0.3\sin\sqrt2 t$, $q_{d2} = 0.5\cos 1.3t - 0.2\sin 0.7t$ | $1.0\cdot10^{-5}$ | $1.0\cdot10^{-4}$ | $0.663$ (랭크 5) |
| 정지 목표 $q_d = (0.3,\ -0.5)$ | $4.8\cdot10^{-14}$ | $0.337$ | $0$ (랭크 2) |
| (대조) 비적응, 매개변수 $0.5a$ 고정 | $0.127$ / $0.119$ | — | — |

PE 궤적에서는 매개변수 오차가 35초에 5%, 51초에 1% 아래로 내려가고 180초에
$10^{-4}$ 가 된다(30·60·120초에서 각각 $0.075$, $0.0074$, $0.0001$). 정지 목표에서는
**추적 오차가 $5\cdot10^{-14}$ 로 사실상 완벽한데** 추정값이

$$
\hat a = (-2.0943,\ 4.1927,\ 1.4563,\ 14.7150,\ 4.9050) \quad\text{vs}\quad
  a = (1.3333,\ 0.3333,\ 0.5,\ 14.7150,\ 4.9050)
$$

로 **중력 매개변수 $a_4, a_5$ 만 정확히 수렴**하고 관성 매개변수 $a_1,a_2,a_3$ 는 부호까지
틀린 값에 멈춘다. 이유는 (6)에서 보인다: $\dot q_d = \ddot q_d = 0$ 이면 1·2·3열이
($\ddot q_r$, $\dot q_r$ 로만 이루어진 항들) 과도 구간 뒤에 **0 이 되고**, 남는 것은 4·5열
(중력)뿐이다. Gram 행렬의 랭크가 5 에서 2 로 떨어지고, 영공간 방향의 오차는 적응 법칙이
**볼 수 없다**.

이것이 확실성 등가의 함정이다. "제어가 잘 되므로 추정된 모델을 다른 일(계획·시뮬레이션·다른
제어기)에 써도 된다" 는 추론은 PE 없이는 **근거가 없다**.

## 증명 스케치

### R3 — 지속 여진이 매개변수 수렴을 주는 이유

**가설** H1: (4)로 $s \to 0$, $s \in L_2$, 모든 신호 유계. H2: $W(t)$ 가 (5)의 PE.
H3: $W$ 와 $\dot W$ 가 유계(궤적이 매끄럽고 유계).
**결론** C: $\tilde a \to 0$ 이 지수적으로.

**전략**: $s \to 0$ 을 쓰면 오차계가 **선형 시변계** $\dot{\tilde a} = -\Gamma W^\top W \tilde a + (\text{소멸항})$
으로 환원된다. PE 는 그 LTV 계의 지수 안정성과 동치다.

1. **환원.** $s \to 0$ 이므로 (7)에서 $Y\tilde a \to 0$ 이고, $Y \to W$ (궤적이 목표로 수렴).
   적응 법칙을 $s$ 대신 "예측 오차" 로 다시 쓰면 $\dot{\tilde a} = -\Gamma W^\top W\tilde a$ 가
   주된 항이고 나머지는 $L_2$ 로 소멸한다(생략: 섭동 항의 ISS 처리, Khalil ch.9).
2. **PE $\Rightarrow$ 지수 안정.** $U = \tfrac12\tilde a^\top\Gamma^{-1}\tilde a$ 를 쓰면
   $\dot U = -\lVert W\tilde a\rVert^2 \le 0$ 이지만 순간적으로 0 일 수 있다. 그래서 **구간**으로
   본다: (5)를 쓰면 한 구간 $[t, t+T_0]$ 에서
   $$
   U(t+T_0) - U(t) = -\int_t^{t+T_0}\lVert W\tilde a\rVert^2 d\sigma \le -\alpha'\,U(t)
   $$
   인 $\alpha' > 0$ 가 존재한다($\tilde a$ 가 구간 안에서 많이 변하지 않음을 H3 로 보이고
   $\int W^\top W \succeq \alpha I$ 를 쓴다). 즉 $U$ 가 **구간마다 기하적으로** 감소하므로
   지수 수렴이다.
3. **필요성.** 반대로 PE 가 깨지면, 즉 어떤 단위 벡터 $v$ 와 모든 $t$ 에 대해
   $\int_t^{t+T_0}\lVert Wv\rVert^2 \to 0$ 이면, $\tilde a(0) = cv$ 로 둔 해는 $\dot U \approx 0$
   이라 수렴하지 않는다. 선형 오차계에서는 이 논증이 정확해져 PE 는 **필요충분**이 된다
   (Boyd & Sastry 1986 §3).

**가설을 지우면**: H3(유계 $\dot W$)를 빼면 2단계에서 "$\tilde a$ 가 구간 안에서 거의 상수" 라는
근사가 깨져 구간 논증이 성립하지 않는다. H1 에서 신호 유계성을 빼면 1단계의 환원 자체가
불가능하다 — 그리고 **모델링되지 않은 동역학**이 있으면 정확히 H1 이 깨진다. 이때 적응은
추정값을 "틀린 방향으로 열심히" 움직이고(표류), 고주파 모드를 여진해 불안정해진다. Rohrs et al.
1985 이 보인 것이 바로 이것이고, 처방은 적응 자체를 제한하는 것이다(사영·데드존·$\sigma$-수정)
또는 적응 속도와 폐루프 대역폭을 **구조적으로 분리**하는 것이다($L_1$ 적응).

생략한 기술적 단계: Barbalat 보조정리와 LTV 계의 균일 지수 안정성 판정(Khalil Lemma 8.2,
Thm 8.5), 섭동된 PE 논증의 정량적 형태(Boyd–Sastry 1986 §4).

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** (6)의 3열(계수 $a_3$)을 끝까지 유도하라. $M$ 의 $\cos q_2$ 항과 $C$ 의
$\sin q_2$ 항이 어떻게 한 열로 합쳐지는지 보이고, 2행에 $\dot q_2$ 가 **나타나지 않는** 이유를
쓰라.
*해답 스케치*: $M\ddot q_r$ 의 $a_3$ 계수는 1행 $2c_2\ddot q_{r1}+c_2\ddot q_{r2}$, 2행
$c_2\ddot q_{r1}$ 이고, $C\dot q_r$ 의 $a_3$ 계수는 $h = -a_3s_2$ 를 빼내면
1행 $-s_2[\dot q_2\dot q_{r1} + (\dot q_1+\dot q_2)\dot q_{r2}]$, 2행 $+s_2\dot q_1\dot q_{r1}$ 이다.
2행의 $C$ 둘째 성분이 0 이라 $\dot q_2$ 가 사라진다.

**P2 (유도, ★★, R2)** (4)를 유도하는 과정에서 반대칭 항등식을 쓰는 지점을 지목하고, 그
항등식이 $\dot q$ 가 아니라 $s$ 에 대해서도 성립하는 이유를 쓰라. 이어서 적응 법칙의 부호를
$+\Gamma Y^\top s$ 로 바꾸면 $\dot V$ 가 어떻게 되는가?
*해답 스케치*: $\tfrac12\dot M - C$ 가 **행렬로서** 반대칭이므로 임의 벡터에 대해 2차형식이 0
이다. 부호를 뒤집으면 $\dot V = 2s^\top Y\tilde a - s^\top K_Ds$ 로 부호가 불확정이 되고
안정성 논증이 사라진다.

**P3 (증명, ★★★, R3)** (5)에서 2단계의 기하적 감소
$U(t+T_0) \le (1-\alpha')U(t)$ 를 명시적인 $\alpha'$ 와 함께 유도하라. $\tilde a$ 의 구간 내
변동을 어떻게 통제하는가?
*해답 스케치*: $\tilde a(\sigma) = \tilde a(t) + \int_t^\sigma \dot{\tilde a}$ 로 쓰고
$\lVert\dot{\tilde a}\rVert \le \lVert\Gamma\rVert\lVert W\rVert^2\lVert\tilde a\rVert$ 로 묶어
$\sigma \in [t,t+T_0]$ 에서 $\lVert\tilde a(\sigma) - \tilde a(t)\rVert \le \epsilon\lVert \tilde a(t)\rVert$
를 얻는다. 그 다음 $\int\lVert W\tilde a\rVert^2 \ge \alpha\lVert\tilde a(t)\rVert^2(1-\epsilon)^2$.

**P4 (계산, ★, R3·R4)** 정지 목표 $q_d = (0.3, -0.5)$ 에 대해 $W(t)$ 의 Gram 행렬
$\int_0^{10} W^\top W\,dt$ 의 ⓐ 랭크와 ⓑ 최소 고윳값, 그리고 PE 궤적
$q_{d1} = 0.4\sin t + 0.3\sin\sqrt2 t$, $q_{d2} = 0.5\cos1.3t - 0.2\sin0.7t$ 에 대한 같은 두 값을
구하라.
*정답*: 정지 목표 ⓐ 2 ⓑ $0$ (수치적으로 $< 10^{-12}$); PE 궤적 ⓐ 5 ⓑ $0.663$
(허용오차 $10^{-2}$, $\Delta t = 10^{-3}$ 구적). 검산: 정지 목표에서 비영인 열은 (6)의 4·5열뿐이다.

**P5 (구현, ★★, R2·R4)** (3)을 구현해 재현 과제의 네 조건을 만족시키고, 추가로 $\Gamma$ 를
$2$, $20$, $200$ 으로 바꿔 ⓐ 매개변수 수렴 시간과 ⓑ 토크의 최댓값을 표로 만들라.
*루브릭*: ⓐ 수렴이 빨라지지만 ⓑ 토크 피크와 고주파 성분이 커지는 교환을 보인다 ⓒ $\Gamma$ 를
더 키우면 적분 $\Delta t$ 를 줄여야 함을 수치로 보인다(강성 문제) ⓓ 모든 수치에 $\Delta t$ 와
적분기를 함께 보고한다.

**P6 (반례, ★★★, R5)** Rohrs 류 반례를 만들라: 제어기가 모르는 **고주파 극점**(예
$1/(\tau s + 1)$, $\tau \ll 1$)을 구동기에 넣고, PE 가 아닌 목표에서 $\Gamma$ 를 키우며
① 매개변수 표류 ② 버스팅 ③ 발산을 차례로 관찰하라. 이어서 사영 또는 데드존을 넣어 ③을
막아라.
*성질 체크리스트*: ⓐ 모델링되지 않은 동역학이 **없을 때는** 같은 $\Gamma$ 에서 안정함을 먼저
보인다(원인 분리) ⓑ 표류는 추정값이 경계 없이 한 방향으로 가는 것으로 확인 ⓒ 데드존은 추적
오차에 바이어스를 남긴다는 대가를 함께 보고한다.

**P7 (논문, ★★, R3·R5)** Boyd & Sastry 1986 과 Rohrs et al. 1985 를 읽고 ⓐ 두 논문이 각각
적응 제어의 **어떤 약속**을 검증·반박하는지, ⓑ Rohrs 의 예가 Boyd–Sastry 의 PE 조건을
위반하는지 아니면 다른 가정을 위반하는지, ⓒ 두 결과가 오늘의 "학습 기반 제어" 에 주는 교훈을
각각 3문장 이내로 쓰라.
*루브릭*: "PE 는 **모델이 맞다는 가정 아래** 수렴을 주고, Rohrs 는 그 가정 자체를 깬다" 를
구분하면 통과. 학습 기반 제어에서 같은 구분(모델 클래스 오차 vs 여진 부족)을 짚으면 가점.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Slotine & Li, "On the adaptive control of robot manipulators" (1987, IJRR)**
   — 역할: `원전(seminal)`. <https://doi.org/10.1177/027836498700600303>
   §2–§3 이 이 레슨의 R1·R2 다.
   추가 질문: ⓐ 저자들이 가속도 측정을 피하려고 도입한 양은 무엇이고 그 대가는?
   ⓑ 논문은 매개변수 수렴을 주장하는가, 추적 수렴만 주장하는가 — 본문의 어느 문장이 그 구분을
   하는가?
2. **Boyd & Sastry, "Necessary and sufficient conditions for parameter convergence in adaptive
   control" (1986, Automatica)** — 역할: `표준(standard)`.
   <https://doi.org/10.1016/0005-1098(86)90002-6>
   추가 질문: ⓐ PE 를 주파수 영역 조건(스펙트럼 라인 수)으로 옮기면 어떻게 되는가 — 미지
   매개변수 $p$ 개에 필요한 최소 주파수 개수는? ⓑ "충분한 풍부함(sufficient richness)" 과 PE 의
   관계를 한 줄로.
3. **Rohrs, Valavani, Athans & Stein, "Robustness of continuous-time adaptive control algorithms
   in the presence of unmodeled dynamics" (1985, IEEE T-AC)** — 역할: `반론(critique)`.
   <https://doi.org/10.1109/TAC.1985.1104070>
   추가 질문: ⓐ 불안정으로 가는 경로를 **신호 수준**에서 서술하라(어느 주파수가 여진되고 무엇이
   그것을 키우는가). ⓑ 저자들의 결론이 "적응 제어는 쓸 수 없다" 가 아니라면, 정확히 무엇인가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 10분 이내, numpy 만. 대상은 (1)의 2링크
팔이고 입력 데이터는 없다 — 목표 궤적은 아래에 식으로 주어진다.

**수용 기준 (네 조건 모두)**

1. **회귀 행렬 검증**: 무작위 $(q,\dot q,\ddot q)$ $10^3$ 개 ($\lvert\dot q\rvert,\lvert\ddot q\rvert\le4$)에서
   $\dot q_r = \dot q$, $\ddot q_r = \ddot q$ 로 두고
   $\max\lvert Y a - (M\ddot q + C\dot q + g)\rvert < 10^{-12}$ (참조: $7.1\cdot10^{-15}$).
2. **여진 측정**: $\int_0^{10}W^\top W\,dt$ 의 최소 고윳값이 PE 궤적에서 $\ge 0.5$ (참조
   $0.663$, 랭크 5), 정지 목표에서 $< 10^{-10}$ 이고 랭크가 2 (참조 $0$). 두 랭크를 함께 보고한다.
3. **PE 궤적**: (3)을 $\Lambda = 4I$, $K_D = 20I$, $\Gamma = 20I$, $\hat a(0) = 0.5a$ 로 180초
   적분($\Delta t \le 5\cdot10^{-4}$)해 마지막 10초의 $\lvert\tilde q\rvert_\infty < 10^{-4}$ 이고
   $\lVert\tilde a\rVert/\lVert a\rVert < 10^{-3}$. 5%·1% 도달 시각을 보고한다(참조 35초, 51초).
4. **정지 목표(반례)**: 같은 이득으로 $q_d = (0.3,-0.5)$ 를 180초 추적해
   $\lvert\tilde q\rvert_\infty < 10^{-6}$ **이면서**
   $\lVert\tilde a\rVert/\lVert a\rVert > 0.1$ 임을 보이고, 중력 성분만 수렴함을 확인한다:
   $\lvert\hat a_4 - a_4\rvert/a_4 < 10^{-3}$, $\lvert\hat a_5-a_5\rvert/a_5 < 10^{-3}$ 이면서
   $\lvert \hat a_1 - a_1\rvert/\lvert a_1\rvert > 0.5$ (참조: 추적 $4.8\cdot10^{-14}$,
   매개변수 오차 $0.337$, $\hat a_1 = -2.09$).

**비교 대상**: 비적응 계산 토크 제어기에 **틀린** 매개변수 $0.5a$ 를 넣은 경우 — 같은 이득으로
마지막 10초의 추적 오차가 PE 궤적에서 $0.127$, 정지 목표에서 $0.119$ rad 로 남아야 한다
(적응이 실제로 무엇을 벌어 주는지 보여주는 대조군).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| $V$ 가 증가한다 | 적응 법칙 부호 오류 또는 $\ddot q_r$ 대신 $\ddot q$ 사용 | $\dot V + s^\top K_Ds$ 를 매 스텝 출력해 0 인지 본다 |
| 추적은 되는데 조건 1 이 실패 | $Y$ 의 3열에서 $\dot q$ 와 $\dot q_r$ 을 뒤섞었다 | $\dot q_r = \dot q$ 로 두고 조건 1 을 먼저 통과시킨다 |
| PE 궤적에서도 매개변수가 안 간다 | 여진 주파수가 **유리수 비**여서 열이 종속 | $\sqrt2$ 처럼 무리수 비를 섞고 조건 2 의 $\lambda_{\min}$ 를 다시 측정한다 |
| 조건 3 에서 발산 | $\Gamma$ 가 커서 적응이 적분기보다 빠르다(강성) | $\Delta t$ 를 절반으로 줄여 결과가 바뀌는지 본다 — 바뀌면 적분기 문제다 |
| 조건 4 의 추적 오차가 $10^{-3}$ 수준에 멈춘다 | 중력 매개변수가 아직 수렴 중(과도) | 적분 시간을 늘리거나 $\Lambda$ 를 키운다. 180초면 $10^{-13}$ 수준까지 간다 |

## 열린 문제

- **(열린 문제) 여진을 만들어 내는 제어** — PE 는 궤적의 성질이므로 "추적하면서 동시에 충분히
  여진하는" 궤적을 **온라인으로 만드는** 문제가 된다. 작업이 정지 목표를 요구하면 여진은 작업과
  충돌한다. 현재 접근: 동시 학습(concurrent learning)으로 과거 데이터를 재사용하는 방식,
  정보 행렬을 비용에 넣는 궤적 최적화(`c4-mpc` 와 겹친다). 비어 있는 자리: 작업 성능 손실과
  식별 품질의 파레토 경계를 주는 설계.
- **(열린 문제) 모델 클래스 오차 아래의 적응** — Rohrs 반례의 본질은 **매개변수가 아니라
  구조**가 틀린 경우다. $L_1$ 적응 제어는 적응 속도와 강건성을 필터로 분리하지만
  ([Cao & Hovakimyan 2006](https://doi.org/10.1109/ACC.2006.1657244)) 필터 대역폭의 선택이
  성능 한계를 만든다. 비어 있는 자리: 구조 오차의 크기를 **측정 가능한 양**으로 바꾸고 그에
  따라 적응 대역폭을 정하는 규칙.
- **(열린 문제) 학습과 적응의 접합** — 신경망으로 잔차 동역학을 학습하고 그 위에서 선형 계수만
  온라인 적응하는 구조가 실기에서 성과를 냈다
  ([O'Connell et al., Neural-Fly, 2022](https://doi.org/10.1126/scirobotics.abm6597)). 그러나
  학습된 기저가 참 동역학을 **포함하지 않을 때**의 보장은 여전히 없다. 비어 있는 자리:
  기저 표현 오차 → 추적·수렴 보장의 명시적 사상. `c3-contraction-incremental` 의 열린 문제와
  같은 벽이다.
- **(열린 문제) 접촉·마찰이 있는 적응** — 쿨롱 마찰은 매개변수에 선형이지만 비매끄러워
  $\dot q \approx 0$ 에서 회귀 행렬이 정의되지 않고, 접촉 전환은 PE 를 구간별로 깨뜨린다.
  비어 있는 자리: 비매끄러운 항을 포함한 식별 가능성(identifiability) 이론 —
  `c2-contact-dynamics` 와 `c2-dynamics-derivatives-sysid` 에서 식별 쪽에서 다시 만난다.

## 개념 점검

`rc quiz c3-adaptive-control` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c3-adaptive-control-quiz
questions:
  - id: q1
    type: single
    prompt: "Slotine–Li 적응 제어기의 $\\dot V = -s^\\top K_D s$ 에서 **매개변수 오차 항이 보이지 않는다**는 사실이 뜻하는 것은?"
    choices:
      - "매개변수가 항상 참값으로 수렴한다"
      - "Lyapunov 논증만으로는 매개변수 수렴을 결론할 수 없다 — 추적 수렴만 얻는다"
      - "제어기가 불안정하다"
      - "$K_D$ 를 크게 하면 매개변수도 수렴한다"
    answer: 1
    explanation: "$\\dot V$ 는 $\\tilde a$ 에 대해 음반정부호(0)다. 따라서 $\\tilde a$ 는 유계일 뿐이고, 수렴은 별도 조건(지속 여진)에서만 나온다. 실제로 정지 목표에서는 추적 오차가 $10^{-14}$ 인데도 매개변수 오차가 34% 로 남는다."
    concept: { front: "적응 제어의 보장 범위", back: "$\\dot V = -s^\\top K_Ds$ 는 추적 수렴만 준다. 매개변수 수렴은 PE 조건이 필요" }
  - id: q2
    type: short
    prompt: "회귀 행렬 $W(t)$ 가 지속 여진이라는 조건을 적분 부등식으로 쓰면? (한 줄)"
    answer: ["int_t^{t+T} W^T W >= alpha I", "∫ W^T W dt >= alpha I", "integral W'W >= alpha I", "int W^T W >= alpha I", "∫_t^{t+T0} WᵀW dσ ⪰ αI"]
    explanation: "$\\exists \\alpha, T_0 > 0$ 에 대해 모든 $t$ 에서 $\\int_t^{t+T_0} W(\\sigma)^\\top W(\\sigma)d\\sigma \\succeq \\alpha I$ 다. 어떤 방향으로도 정보가 꾸준히 들어온다는 뜻이고, 이것이 깨진 방향의 매개변수 오차는 영원히 남는다."
    concept: { front: "지속 여진(PE) 조건", back: "$\\int_t^{t+T_0} W^\\top W\\,d\\sigma \\succeq \\alpha I$ — 모든 $t$ 에서 성립해야 한다" }
  - id: q3
    type: truefalse
    prompt: "추적 오차가 0 으로 수렴했다면 추정된 매개변수를 다른 제어기나 계획기에 재사용해도 된다."
    answer: false
    explanation: "2링크 팔의 정지 목표 실험이 반례다: 추적 오차 $5\\cdot10^{-14}$ 에서도 관성 매개변수는 부호까지 틀려 있고(예 $\\hat a_1 = -2.09$ vs $a_1 = 1.33$) 중력 매개변수만 맞는다. 여진되지 않은 열의 정보는 애초에 데이터에 없다."
    concept: { front: "추적 성능과 식별 품질", back: "별개다 — PE 가 없으면 추적이 완벽해도 추정값은 틀린 채 멈춘다" }
  - id: q4
    type: single
    prompt: "정지 목표에서 2링크 팔의 Gram 행렬 랭크가 5 에서 2 로 떨어지는 이유는?"
    choices:
      - "중력이 0 이 되기 때문"
      - "$\\dot q_d = \\ddot q_d = 0$ 이라 회귀 행렬의 관성·코리올리 열이 과도 구간 뒤 0 이 되고 중력 열만 남기 때문"
      - "적응 이득이 작기 때문"
      - "질량행렬이 특이해지기 때문"
    answer: 1
    explanation: "(6)의 1·2·3열은 $\\ddot q_r$ 와 $\\dot q\\dot q_r$ 로만 이루어져 있다. 정지 목표에서 과도가 끝나면 이 항들이 사라지고 4·5열(중력)만 남아 랭크 2 가 된다. 영공간 방향의 매개변수는 데이터에 흔적을 남기지 않는다."
    concept: { front: "정지 목표에서 여진이 죽는 자리", back: "관성·코리올리 열은 $\\ddot q_r, \\dot q$ 에 비례 — 정지하면 중력 열만 남아 랭크 2" }
```

## 이 단계 공부법

1. **$Y$ 를 손으로 만든다 (60분)** — P1 을 먼저 푼다. (6)을 베끼지 말고 $M\ddot q_r + C\dot q_r + g$
   를 전개해 열별로 모은다. 그 다음 조건 1 을 코드로 통과시킨다. **회귀 행렬이 틀리면 이 레슨의
   나머지 전부가 무의미하다.**
2. **상쇄를 두 번 쓴다 (40분)** — (7)의 중력·$\ddot q_r$ 상쇄와 (4)의 $s^\top Y\tilde a$ 상쇄.
   둘 다 "설계가 상쇄를 만들도록 되어 있다" 는 같은 이야기다. 적응 법칙의 부호를 뒤집어 보면
   왜 그 형태여야 하는지 보인다(P2).
3. **PE 를 Gram 행렬로 **본다** (40분)** — 조건 2 를 돌려 정지 목표의 $\lambda_{\min}$ 이 0 임을
   확인한다. PE 가 추상적인 조건이 아니라 **행렬의 랭크**라는 것을 숫자로 겪는 단계다.
4. **반례를 먼저 돌린다 (60분)** — 조건 4(정지 목표)를 조건 3 보다 **먼저** 돌린다. 추적이
   완벽한데 매개변수가 틀린 화면을 본 사람은 확실성 등가의 함정을 잊지 않는다.
5. **PE 궤적에서 수렴을 확인한다 (60분)** — 조건 3. 무리수 주파수 비를 쓰는 이유를
   진단표에서 확인하고, 유리수 비로 바꿔 수렴이 느려지는 것도 직접 본다.
6. **강건성의 벽을 만난다 (90분)** — P6 의 Rohrs 류 실험. 모델링되지 않은 극점을 넣고 $\Gamma$ 를
   키우면 **같은 코드가** 불안정해진다. 그 뒤에 사영·데드존을 넣어 막는다. 이 경험이 $L_1$
   적응 제어의 동기를 설명해 준다.
7. **논문은 "약속과 반박" 으로 읽는다 (150분)** — Slotine–Li 는 약속하고, Boyd–Sastry 는 그
   약속의 정확한 조건을 주고, Rohrs 는 가정 밖에서 무너지는 것을 보인다. 세 편의 관계를 한
   문단으로 쓰면 이 레슨이 끝난다.

**통과 기준**: 백지에서 (6)의 한 열과 (4)를 유도할 수 있고, PE 조건을 적분 부등식으로 쓸 수
있고, 추적은 되는데 식별은 안 되는 상황을 수치로 만들 수 있고, 재현 과제의 네 조건을 만족하는
코드와 논문 3편의 노트가 있다.
