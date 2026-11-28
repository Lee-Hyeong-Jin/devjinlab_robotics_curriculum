---
id: s3-hzd-gait-generation
title: 영역 동역학(HZD)과 보행 생성
summary: >-
  언더액추에이티드 이족 보행을 "가상 제약(virtual constraint)으로 자유도를 묶고 남은 1자유도를
  설계한다"는 관점으로 다룬다. 출력을 0 으로 만드는 면(영역 동역학 면) 위에서 동역학이 2차원으로
  축소되는 과정을 유도하고, 그 면이 **충격을 지나서도 불변**이게 만드는 조건(HZD)을 설계 조건으로
  쓴다. 축소된 동역학이 1차원 아핀 복귀 사상이 되어 안정성 판정이 $\delta_{\mathrm{zero}}^2 < 1$
  한 줄로 끝나는 것을 유도하고, 그 예측을 4상태 전체 모델의 푸앵카레 고유값과 8자리까지 비교한다.
objectives:
  - 가상 제약에서 출력의 상대 차수와 영역 동역학 면을 유도하고 그 면의 차원을 셀 수 있다.
  - 충격 불변성 조건 $\Delta(S\cap Z)\subset Z$ 를 가상 제약의 경계 조건으로 번역할 수 있다.
  - 지지발에 대한 각운동량이 구동 토크와 무관하다는 사실에서 1차원 아핀 복귀 사상을 유도할 수 있다.
  - 리미트 사이클의 존재 조건과 안정성 조건을 각각 $\zeta^\star>0$ 과 $\delta_{\mathrm{zero}}^2<1$ 로 분리해 설명할 수 있다.
  - 축소 모델의 예측과 전체 모델의 푸앵카레 고유값을 수치로 비교해 일치/불일치의 원인을 지목할 수 있다.
prerequisites: [s3-hybrid-limit-cycles, c3-feedback-linearization]
difficulty: 5
estimated_minutes: 540
tags: [legged-robots, hybrid-zero-dynamics, virtual-constraints, underactuated, research]
activities:
  - id: s3-hzd-gait-generation-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: s3-hzd-gait-generation-papers
    kind: paper
    title: 필독 논문 2편 + 권장 1편 읽기, 논문별 1페이지 노트
    estimated_minutes: 135
  - id: s3-hzd-gait-generation-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 180
  - id: s3-hzd-gait-generation-reproduction
    kind: reproduction
    title: 재현 과제 — 가상 제약 설계와 축소 모델 검증 (R2)
    estimated_minutes: 120
  - id: s3-hzd-gait-generation-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Westervelt, Grizzle, Chevallereau, Choi & Morris, Feedback Control of Dynamic Bipedal Robot Locomotion (2007)"
    kind: book
    note: ch.5-6 — HZD 의 교재 서술. 이 레슨의 R1-R3 가 그 축소판이다. (공식 URL 미확인)
  - title: "Tedrake, Underactuated Robotics"
    url: https://underactuated.csail.mit.edu/
    kind: book
    note: ch.4-5 — 부분 피드백 선형화와 가상 제약의 직관. 전문 무료.
  - title: "NumPy"
    url: https://numpy.org/
    kind: code
    note: 재현 과제는 numpy 만으로 끝난다. Bézier 계수 4개와 RK4 가 전부다.
papers:
  - id: westervelt2003-hzd
    required: true
    role: seminal
    note: "§III, §IV"
  - id: ames2014-hzd-experimental
    required: true
    role: standard
    note: "§II, §V"
  - id: grizzle2001-asymptotically-stable-walking
    role: standard
    note: "§III"
---

# 영역 동역학(HZD)과 보행 생성

## 전제와 기호

`s3-hybrid-limit-cycles` 는 **주어진** 보행의 안정성을 판정했다. 이 레슨은 보행을 **설계**한다.
문제는 언더액추에이티드라는 점이다 — 발이 점이면 지면에서 토크를 만들 수 없으므로, 자유도보다
구동기가 적다. 그래서 "모든 관절을 원하는 궤적에 올린다"는 전략이 애초에 불가능하다.

HZD 의 답은 두 단계다. ⓐ 구동기 수만큼의 **가상 제약**으로 관절들을 서로 묶어 자유도를 1 로
줄이고, ⓑ 남은 1자유도의 동역학을 **그대로 받아들이고** 그것의 리미트 사이클을 설계한다.
받아들인다는 말이 중요하다: 남은 자유도는 중력이 지배하고 **구동 토크로 바꿀 수 없다**.

전제: `c3-feedback-linearization` 의 상대 차수·입출력 선형화·영역 동역학,
`s3-hybrid-limit-cycles` 의 가드·리셋·푸앵카레 사상, 각운동량.

| 기호 | 뜻 |
|---|---|
| $q = (\theta_{\mathrm s},\theta_{\mathrm n})$ | 지지·유각 다리 각(경사면 법선 기준, 내리막이 양) |
| $u$ | 엉덩이 토크. 일반화 힘은 $Bu$, $B = (-1, +1)^\top$ |
| $\theta$ | 위상 변수(여기서는 $\theta = \theta_{\mathrm s}$, 한 걸음 동안 단조) |
| $h_{\mathrm d}(\theta)$ | 가상 제약. 설계 대상 |
| $y = \theta_{\mathrm n} - h_{\mathrm d}(\theta_{\mathrm s})$ | 출력(가상 제약 오차) |
| $Z = \{(q,\dot q) : y = 0,\ \dot y = 0\}$ | 영역 동역학 면(zero dynamics surface) |
| $S$ | 가드 $\{\theta_{\mathrm s} = \alpha\}$, $\Delta$ | 리셋 사상(충격 + 다리 교체) |
| $\sigma$ | **지지발에 대한 전체 각운동량** |
| $\zeta = \tfrac12\sigma^2$ | 축소 동역학의 상태 |
| $\delta_{\mathrm{zero}}$ | 충격이 $\sigma$ 를 곱하는 비 $\sigma^+/\sigma^-$ ($Z$ 위에서 상수) |
| $V_{\mathrm{zero}}$ | 축소 동역학의 유효 위치 에너지 |

수치는 `s3-hybrid-limit-cycles` 와 **같은 보행기**($m=5$, $m_H=10$, $a=b=0.5$, $g=9.81$,
$\gamma = 0.05$)에 엉덩이 토크를 하나 더한 것이고, 설계 변수는 $\alpha = 0.25$ rad,
$h_{\mathrm d}'(\alpha) = -0.8$ 이다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`f0-how-to-read-this-track` 레슨의 "유도 깊이 등급" 절).

- **R1 (가상 제약과 영역 동역학 면) [D3]** — $y = \theta_{\mathrm n} - h_{\mathrm d}(\theta_{\mathrm s})$ 의
  상대 차수는 2 이고, 디커플링 항
  $$
  L_{g}\dot y = \begin{bmatrix}-h_{\mathrm d}'(\theta_{\mathrm s}) & 1\end{bmatrix} M(q)^{-1}B \tag{1}
  $$
  이 0 이 아니면 $y \equiv 0$ 을 강제하는 피드백이 존재하고, $Z$ 는 **연속 흐름에 대해 불변**인
  2차원 다양체다($\theta_{\mathrm s}$ 와 $\dot\theta_{\mathrm s}$ 가 좌표).
- **R2 (HZD: 충격 불변성은 **설계 조건**이다) [D3]** — 연속 불변성만으로는 부족하다. 걸음마다
  충격이 상태를 $Z$ 밖으로 던지면 매 걸음 과도 응답이 되살아난다. 따라서
  $$
  \Delta\big(S \cap Z\big) \subset Z \tag{2}
  $$
  를 요구하고, 이것이 **가상 제약의 경계 조건**으로 번역된다. 컴퍼스 보행기에서는
  $h_{\mathrm d}(-\alpha) = \alpha$, $h_{\mathrm d}(\alpha) = -\alpha$ 와 **스칼라 한 개**
  $$
  h_{\mathrm d}'(-\alpha) = \frac{w_2}{w_1},\qquad
    w = Q^+(\alpha)^{-1}Q^-(\alpha)\begin{bmatrix}1\\ h_{\mathrm d}'(\alpha)\end{bmatrix} \tag{3}
  $$
  이다. 3차 Bézier 로 쓰면 계수 4개가 이 세 조건과 설계 자유도
  $h_{\mathrm d}'(\alpha)$ 로 **정확히** 결정된다(수치: $h_{\mathrm d}'(-\alpha) = 0.7192862572$).
- **R3 (축소된 1차원 아핀 복귀 사상) [D3]** — **엉덩이 토크는 지지발에 대한 모멘트를 만들지
  않는다**. 따라서 $\dot\sigma = \tau_{\mathrm g}(q)$ (중력 모멘트)뿐이고, $Z$ 위에서 형상이
  $\theta$ 하나로 정해지므로 $\sigma = c(\theta)\dot\theta$ 와
  $$
  \frac{d\zeta}{d\theta} = c(\theta)\,\tau_{\mathrm g}(\theta) =: -\frac{dV_{\mathrm{zero}}}{d\theta}
  \;\Longrightarrow\;
  \zeta^- = \zeta^+ - \Delta V_{\mathrm{zero}} \tag{4}
  $$
  를 얻는다. 충격은 $Z$ 위에서 $\sigma$ 를 **상수배**($\delta_{\mathrm{zero}}$) 하므로 걸음
  사상이 **아핀**이 된다:
  $$
  \zeta^+_{k+1} = \delta_{\mathrm{zero}}^2\big(\zeta^+_k - \Delta V_{\mathrm{zero}}\big),
  \qquad
  \zeta^\star = \frac{-\delta_{\mathrm{zero}}^2\,\Delta V_{\mathrm{zero}}}{1-\delta_{\mathrm{zero}}^2}. \tag{5}
  $$
  **존재**는 $\zeta^\star > 0$ 와 걸음 내내 $\zeta(\theta) > 0$ (멈추지 않음), **안정성**은
  $\delta_{\mathrm{zero}}^2 < 1$ 로 **완전히 분리**된다.
- **R4 (축소 예측 = 전체 모델의 지배 고유값) [D2]** — 횡방향 안정화가 충분히 빠르면 4상태 하이브리드
  모델의 푸앵카레 고유값은 $\{\delta_{\mathrm{zero}}^2,\ \approx0,\ \approx0\}$ 다. 수치:
  설계값 $\delta_{\mathrm{zero}}^2 = 0.7601914255$, 전체 모델의 측정값
  $\{4.6\cdot10^{-5},\ 0.76019143,\ 0\}$ — **8자리 일치**.
- **R5 (설계 자유도와 그 대가) [D2]** — $\alpha$ 와 $h_{\mathrm d}$ 의 모양이 자유롭고, 그 선택이
  $\delta_{\mathrm{zero}}$ 와 $\Delta V_{\mathrm{zero}}$ 를 통해 **보행 속도와 수렴률을 동시에**
  정한다. 같은 보행기에서 수동 보행의 스펙트럼 반지름은 $0.582$ 였는데($\gamma=0.05$,
  `s3-hybrid-limit-cycles` R5) 설계한 HZD 보행은 $0.760$ 이다 — 더 느리게 수렴하지만 보폭·주기를
  **고를 수 있다**(주기 $0.4957$ s vs 수동 $0.7324$ s).

## 유도

### R1 — 가상 제약에서 영역 동역학 면까지

제어 대상은 $M(q)\ddot q + N(q,\dot q) = Bu$ 다($N$ 에 중력·원심항이 모두 들어 있고
$B=(-1,1)^\top$). 출력 $y = \theta_{\mathrm n} - h_{\mathrm d}(\theta_{\mathrm s})$ 를 미분하면

$$
\dot y = \dot\theta_{\mathrm n} - h_{\mathrm d}'\dot\theta_{\mathrm s}
  = \begin{bmatrix}-h_{\mathrm d}' & 1\end{bmatrix}\dot q
$$

로 $u$ 가 나타나지 않는다(상대 차수 $\ge 2$). 한 번 더 미분하면

$$
\ddot y = \begin{bmatrix}-h_{\mathrm d}' & 1\end{bmatrix}\ddot q - h_{\mathrm d}''\dot\theta_{\mathrm s}^2
 = \underbrace{\begin{bmatrix}-h_{\mathrm d}' & 1\end{bmatrix}M^{-1}(-N) - h_{\mathrm d}''\dot\theta_{\mathrm s}^2}_{=:A(q,\dot q)}
 + \underbrace{\begin{bmatrix}-h_{\mathrm d}' & 1\end{bmatrix}M^{-1}B}_{=:b(q)}\,u \tag{6}
$$

이므로 $b(q) \ne 0$ 인 영역에서 상대 차수는 정확히 2 이고

$$
u = \frac{1}{b(q)}\Big(-A(q,\dot q) - K_p\,y - K_d\,\dot y\Big) \tag{7}
$$

가 $\ddot y = -K_py - K_d\dot y$ 를 만들어 $y\to0$ 을 지수적으로 보장한다. $Z = \{y=0,\dot y=0\}$
는 (7) 아래에서 **연속 흐름에 대해 불변**이고, 네 상태 중 두 개의 제약이 걸렸으므로 2차원이다.
$Z$ 위에서는 $\theta_{\mathrm n} = h_{\mathrm d}(\theta_{\mathrm s})$,
$\dot\theta_{\mathrm n} = h_{\mathrm d}'\dot\theta_{\mathrm s}$ 이므로 상태는
$(\theta_{\mathrm s}, \dot\theta_{\mathrm s})$ 둘로 끝난다.

**가정이 깨지는 곳**: $b(q) = 0$ 이면 (7)이 폭발한다 — 가상 제약을 아무렇게나 고르면 걸음 중간에
그런 형상을 지날 수 있다. 설계 후 반드시 $\min_\theta \lvert b \rvert$ 를 확인한다.
또 (7)은 $K_p, K_d$ 를 크게 잡으면 횡방향을 빨리 죽이지만 토크가 커진다 —
`c3-feedback-linearization` 의 $1/d$ 폭발과 같은 구조의 교환이다.

### R3 — 축소: 토크가 건드릴 수 없는 양을 찾는다

**1단계 (왜 $\sigma$ 인가).** 지지발을 원점으로 잡고 전체 각운동량
$\sigma = \sum_i m_i (r_i)\times v_i$ 를 본다. 엉덩이 토크는 두 다리 사이의 **내력**이므로
지지발에 대한 모멘트가 0 이고, 지면 반력은 지지발에 작용하므로 모멘트가 0 이다. 남는 것은
중력뿐이다:

$$
\dot\sigma = \tau_{\mathrm g}(q) = \sum_i m_i\,(r_i \times g). \tag{8}
$$

**수치 확인**: 무작위 $(q,\dot q,u)$ 2000개에서 동역학으로 계산한 $d\sigma/dt$ 와 (8)의 차가
최대 $7.6\cdot10^{-9}$ — **토크 $u$ 를 $\pm50$ N·m 로 흔들어도 변하지 않는다**. 이것이 HZD
축소의 물리적 핵심이다: 구동기로 바꿀 수 없는 양이 하나 있고, 그 양이 보행의 "속도"다.

**2단계 ($Z$ 위에서 1차원으로).** $Z$ 위에서 $\dot q = (1, h_{\mathrm d}'(\theta))^\top\dot\theta$
이므로 $\sigma$ 는 $\dot\theta$ 에 선형이다: $\sigma = c(\theta)\dot\theta$ 로 쓰면
$c(\theta) = \rho(\theta)^\top(1, h_{\mathrm d}'(\theta))^\top$ 이고 $\rho$ 는 $\sigma$ 의 행벡터다.
$\zeta := \tfrac12\sigma^2$ 로 두고 $\theta$ 에 대한 미분으로 바꾸면

$$
\frac{d\zeta}{d\theta} = \sigma\frac{d\sigma}{d\theta}
  = \sigma\frac{\dot\sigma}{\dot\theta} = c(\theta)\,\tau_{\mathrm g}(\theta),
$$

즉 (4)다. **시간이 사라졌다** — 걸음의 궤적이 아니라 $\theta$ 에 대한 1차원 적분만 남는다.
$V_{\mathrm{zero}}(\theta) := -\int_{-\alpha}^{\theta} c\,\tau_{\mathrm g}\,d\vartheta$ 로 정의하면
$\zeta(\theta) = \zeta^+ - \big(V_{\mathrm{zero}}(\theta)-V_{\mathrm{zero}}(-\alpha)\big)$ 다.
수치: $\Delta V_{\mathrm{zero}} = V_{\mathrm{zero}}(\alpha)-V_{\mathrm{zero}}(-\alpha) = -49.65652176$
(내리막이므로 음수 — 한 걸음에 $\zeta$ 가 **늘어난다**).

**3단계 (충격이 상수배가 되는 이유).** 충격 순간의 형상은 $Z$ 위에서 **항상 같다**
($\theta_{\mathrm s}=\alpha$, $\theta_{\mathrm n}=-\alpha$). 충격 사상은 속도에 선형이고,
$Z$ 위의 속도는 방향 $(1,h_{\mathrm d}'(\alpha))$ 로 고정되어 크기만 다르다. 따라서

$$
\sigma^+ = \delta_{\mathrm{zero}}\,\sigma^-, \qquad
\delta_{\mathrm{zero}} = \frac{\rho(q^+)^\top Q^+(\alpha)^{-1}Q^-(\alpha)\,(1,h_{\mathrm d}'(\alpha))^\top}
  {\rho(q^-)^\top (1,h_{\mathrm d}'(\alpha))^\top} \tag{9}
$$

는 **상수**다(수치: $\delta_{\mathrm{zero}} = 0.8718895718$). $\zeta$ 는 $\sigma$ 의 제곱이므로
$\zeta^+ = \delta_{\mathrm{zero}}^2\,\zeta^-$ 이고, (4)와 합치면 (5)의 아핀 사상이 된다.

**4단계 (존재와 안정성의 분리).** (5)는 스칼라 아핀 사상 $\zeta \mapsto \delta^2(\zeta - \Delta V)$
이므로 ⓐ 고정점은 $\zeta^\star = -\delta^2\Delta V/(1-\delta^2)$ 로 **닫힌 형태**, ⓑ 수렴률은
기울기 $\delta^2$ 로 **초기값과 무관**하다. 수치: $\zeta^\star = 157.4108104$,
$\sigma^{+\star} = -17.74321337$(전진 운동이므로 음수 규약),
$\dot\theta_{\mathrm s}^{+\star} = 1.32639024$ rad/s.

**실제로 걸으려면 하나 더**: 걸음 내내 $\zeta(\theta)>0$ 여야 한다. $\zeta$ 가 0 이 되면 그
자리에서 **멈춘다**(지지 다리를 넘어가지 못한다). 수치: 걸음 중 최소 $\zeta = 87.86 > 0$ 로
여유가 있다.

**가정이 깨지는 곳**: ⓐ $\delta_{\mathrm{zero}}^2 \ge 1$ 이면 (5)가 발산한다 — 충격이 각운동량을
충분히 깎지 못하는 설계다. ⓑ $\Delta V_{\mathrm{zero}} > 0$ (평지나 오르막)이면 $\zeta^\star<0$ 로
**해가 없다**: 토크가 아무리 세도 $\sigma$ 를 못 키우기 때문이다. 평지 보행에는 몸통이나 발목
같은 **추가 구동**이 필요하고, 그때는 축소 동역학에 입력이 들어와 (5)가 더 복잡해진다.
ⓒ 횡방향 수렴이 느리면 R4 의 "지배 고유값 = $\delta^2$" 가 깨진다.

### R2 — 충격 불변성을 Bézier 경계 조건으로

(2)를 성분으로 쓴다. $Z$ 위에서 걸음이 끝날 때 $q^- = (\alpha,-\alpha)$,
$\dot q^- = \dot\theta^-(1, h_{\mathrm d}'(\alpha))^\top$ 다. 충격 사상을 통과하면
$\dot q^+ = \dot\theta^-\,w$, $w := Q^+(\alpha)^{-1}Q^-(\alpha)(1,h_{\mathrm d}'(\alpha))^\top$ 이고,
교체 후 형상은 $q^+ = (-\alpha, \alpha)$ 다. 새 상태가 $Z$ 에 있으려면

$$
\underbrace{\alpha = h_{\mathrm d}(-\alpha)}_{y^+=0}, \qquad
\underbrace{w_2 = h_{\mathrm d}'(-\alpha)\,w_1}_{\dot y^+=0} \tag{10}
$$

이고, 걸음이 가드에서 끝나려면 $h_{\mathrm d}(\alpha) = -\alpha$ 다. 세 조건과 설계 자유도
$h_{\mathrm d}'(\alpha) = k$ 를 3차 Bézier $h_{\mathrm d}(s) = \sum_{i=0}^3 c_i\binom{3}{i}s^i(1-s)^{3-i}$
($s = (\theta+\alpha)/2\alpha$)에 넣으면 계수가 **닫힌 형태**로 나온다:

$$
c_0 = \alpha,\quad c_3 = -\alpha,\quad
c_1 = c_0 + \frac{2\alpha}{3}\frac{w_2}{w_1},\quad
c_2 = c_3 - \frac{2\alpha}{3}k. \tag{11}
$$

수치($\alpha=0.25$, $k=-0.8$): $c = (0.25,\ 0.36988104,\ -0.11666667,\ -0.25)$ 이고
$h_{\mathrm d}'(-\alpha) = 0.7192862572$ 가 (10)의 요구값과 **자리 전부** 일치한다.

**이 조건을 어기면 무엇이 보이는가**: $h_{\mathrm d}'(-\alpha)$ 를 일부러 $0.2$ 만큼 틀리게 두면
매 걸음 $y^+ \ne 0$ 이 되어 걸음마다 과도 응답이 들어가고, 전체 모델의 지배 고유값이
$\delta_{\mathrm{zero}}^2$ 와 더 이상 일치하지 않는다(재현 과제 비교 대상 ⓐ).

### R4 — 축소 모델의 예측을 전체 모델로 확인

(5)의 고정점에서 얻은 $\dot\theta_{\mathrm s}^{+\star} = 1.32639024$ 로 **4상태 전체 모델**을
(7)의 제어기($K_p=400$, $K_d=40$)와 함께 적분하면

| 걸음 | 주기 (s) | $\dot\theta_{\mathrm s}^+$ | $\lvert y^+\rvert$ | $\sigma^+$ |
|---|---|---|---|---|
| 1 | 0.495686 | 1.32639024 | $1.7\cdot10^{-16}$ | $-17.74321337$ |
| 2–6 | 0.495686 | 1.32639024 | $\le 1.7\cdot10^{-16}$ | $-17.74321337$ |

로 **처음부터 리미트 사이클**이다(축소 모델이 고정점을 정확히 맞혔다는 뜻). 1차원 복귀 사상의
기울기를 수치 미분으로 재면 $0.76019143$ 로 $\delta_{\mathrm{zero}}^2 = 0.76019143$ 과
8자리 일치하고, 3차원 푸앵카레 사상의 고유값은

$$
\{4.6\cdot10^{-5},\quad 0.76019143,\quad 0\} \tag{12}
$$

다 — 지배 고유값이 정확히 $\delta_{\mathrm{zero}}^2$ 이고 나머지 두 개는 횡방향이 죽은 흔적이다.
**이것이 HZD 가 주는 것이다**: 4상태 하이브리드 계의 안정성을 1차원 적분 두 개
($\Delta V_{\mathrm{zero}}$, $\delta_{\mathrm{zero}}$)로 설계 단계에서 **미리** 알 수 있다.

## 증명 스케치

### R2 — 충격 불변성이 왜 "하이브리드" 영역 동역학의 정의인가

**가설** H1: (7)로 $Z$ 가 연속 흐름에 대해 불변. H2: 리셋 $\Delta$ 가 $S$ 근방에서 $C^1$.
H3: (2) $\Delta(S\cap Z)\subset Z$. H4: $Z$ 위의 축소 동역학이 (5)의 고정점
$\zeta^\star>0$ 을 갖고 걸음 내내 $\zeta>0$.
**결론** C: $Z$ 는 **하이브리드** 계 전체에 대해 불변이고, $Z$ 위의 주기 궤도는
$\delta_{\mathrm{zero}}^2<1$ 일 때 그리고 그때만 $Z$ **안에서** 궤도 점근 안정이다. 횡방향이
지수 안정이면 전체 계에서도 궤도 점근 안정이다.

**전략**: 불변 다양체를 하나 만들고, 그 위에서 **차원이 낮아진** 문제를 푼다. 하이브리드 계에서는
"흐름에 대한 불변"과 "리셋에 대한 불변"을 **따로** 보여야 한다는 점이 전부다.

1. **흐름 쪽.** H1 로 $y(0)=\dot y(0)=0$ 이면 $y\equiv0$ 이므로 궤적이 $Z$ 를 떠나지 않는다.
2. **리셋 쪽.** H3 가 바로 그 요구다. (2)가 없으면 궤적이 $Z$ 를 떠나고, 다시 (7)이 $y$ 를
   0 으로 끌고 오지만 **그 과도 응답이 매 걸음 반복**되어 축소 모델의 예측이 깨진다.
3. **축소 동역학.** $Z$ 위의 좌표 $(\theta,\zeta)$ 에서 동역학은 (4)–(5)이고, 걸음 사상은 스칼라
   아핀 사상이다. 아핀 사상 $\zeta\mapsto \delta^2(\zeta-\Delta V)$ 의 고정점은
   $\lvert\delta^2\rvert<1$ 일 때 유일하고 전역 지수 안정(1차원이므로 **흡인 영역이
   $\zeta>0$ 전체**)이다.
4. **전체 계로 올리기.** $Z$ 가 하이브리드 불변이고 횡방향($y,\dot y$)이 걸음마다 지수적으로
   줄어들면, 전체 푸앵카레 사상의 스펙트럼은 "축소 방향의 $\delta^2$ ⊕ 횡방향의 작은 값"으로
   쪼개진다(블록 삼각 구조). 수치 (12)가 그 모습이다.
   (생략: 횡방향 수렴이 축소 방향보다 **충분히 빠르다**는 조건을 정량화하는 단계 —
   Westervelt et al. 2003 §IV 의 정리.)

**가설을 지우면**: H3 를 빼면 2단계에서 $Z$ 가 하이브리드 불변이 아니므로 (5)의 예측이 틀린다 —
"HZD" 의 H 가 바로 이 조건이다. H4 의 $\zeta>0$ 를 빼면 보행 중간에 멈춰 가드에 도달하지 못하고,
$\zeta^\star>0$ 를 빼면 고정점이 물리적으로 존재하지 않는다. 또 $b(q)=0$ (R1)인 형상을 지나면
H1 자체가 깨진다.

## 문제 세트

```problemset
activity: s3-hzd-gait-generation-problems
problems:
  - id: p1
    type: derivation
    stars: 2
    refers_to: ["R1", "R3"]
    prompt: >-
      (6)의 디커플링 항 b(q) 를 컴퍼스 보행기의 질량행렬로 명시적으로 쓰고, b(q) = 0 이 되는 형상이
      존재하는지 alpha = 0.25, hd'(alpha) = -0.8 의 설계에서 수치로 확인하라. 이어서 왜 sigma 의
      동역학에는 토크가 들어오지 않는데 y 의 동역학에는 들어오는지 한 문단으로 설명하라.
    solution_policy: sketch
    solution: >-
      b(q) = [-hd'(th_s), 1] M(q)^{-1} B 를 2x2 역행렬로 전개한다. 걸음 구간에서 |b| 의 최소값을
      수치로 재고 0 에서 떨어져 있음을 보인다. 토크는 두 다리 사이의 내력이므로 지지발에 대한
      모멘트가 0 이고, 따라서 sigma 에는 영향이 없다. 반면 y 는 두 다리의 상대 자유도이므로 내력이
      직접 가속시킨다 - 구동 가능한 방향과 불가능한 방향이 정확히 이렇게 갈린다.
  - id: p2
    type: derivation
    stars: 2
    refers_to: ["R2"]
    prompt: >-
      (10)에서 (11)을 유도하라. 3차 Bezier 대신 5차를 쓰면 자유도가 몇 개 남고, 그 자유도로 무엇을
      최적화할 수 있는가? (예: 최대 토크, 보행 속도, 발 들림 높이 중 하나를 골라 목적함수를 쓰라.)
    solution_policy: sketch
    solution: >-
      Bezier 의 끝점 값과 끝점 기울기가 각각 c0, c3 과 (c1-c0), (c3-c2) 로 주어지는 성질을 쓴다.
      5차에서는 계수 6개 중 4개가 경계 조건에 쓰이고 2개가 남는다. 남은 자유도로는 예컨대
      max_t |u(t)| 를 최소화하거나(미니맥스 토크) 주기를 목표값에 맞추는 문제를 세울 수 있고,
      둘 다 축소 모델 안에서 평가되므로 전체 모델을 적분하지 않고 설계할 수 있다.
  - id: p3
    type: proof
    stars: 3
    refers_to: ["R3"]
    prompt: >-
      Z 위의 걸음 사상이 아핀이라는 사실(5)로부터 (a) 고정점의 유일성, (b) 흡인 영역이 zeta > 0 의
      전체라는 것, (c) 수렴률이 초기 조건과 무관하다는 것을 증명하라. 이어서 delta^2 = 1 인
      경계에서 무슨 일이 일어나는지 쓰라.
    solution_policy: sketch
    solution: >-
      스칼라 아핀 사상의 고정점과 수렴은 등비 수열이다. delta^2 = 1 에서는 사상이
      zeta -> zeta - delta_V 의 평행 이동이 되어 고정점이 없거나(delta_V != 0) 모든 점이
      고정점이다(delta_V = 0) - 전자는 매 걸음 속도가 단조 변하는 비주기 보행, 후자는 임의의
      속도로 걷는 중립 안정이다. 물리적으로는 충격 손실과 중력 입력의 균형이 무너진 경우다.
  - id: p4
    type: numerical
    stars: 1
    refers_to: ["R2", "R3", "R4"]
    prompt: >-
      alpha = 0.25, hd'(alpha) = -0.8, gamma = 0.05 의 설계에서 (a) hd'(-alpha), (b) delta_zero^2,
      (c) delta_V_zero, (d) zeta*, (e) dth_s+* 를 구하라.
    solution_policy: answer
    solution: >-
      (a) 0.7192862572, (b) 0.7601914255, (c) -49.65652176, (d) 157.4108104, (e) 1.32639024 rad/s.
      검산: (d) = -(b)(c)/(1-(b)) 이고, (e) 는 sigma+* = -sqrt(2 zeta*) 를 Z 위의 c(theta) 로 나눈 값이다.
    tolerance: 1.0e-6
  - id: p5
    type: implementation
    stars: 2
    refers_to: ["R1", "R2", "R4"]
    prompt: >-
      가상 제약을 (11)로 설계하고 (7)의 제어기로 4상태 모델을 적분해 재현 과제의 네 조건을 통과시켜라.
      이어서 Kp, Kd 를 10배 낮춰 횡방향 수렴을 느리게 만들고, 전체 모델의 지배 고유값이
      delta_zero^2 에서 얼마나 벗어나는지 표로 보고하라.
    solution_policy: rubric
    solution: >-
      통과 기준: (1) hd 의 경계 조건이 1e-12 이내로 맞고 (2) 예측한 초기 상태에서 첫 걸음부터
      |y+| < 1e-12 이고 (3) 지배 고유값이 delta_zero^2 와 1e-6 이내로 일치하고 (4) Kp, Kd 를 낮추면
      그 일치가 깨지는 방향(횡방향 고유값이 커지고 지배 고유값이 흔들림)을 수치로 보인다.
  - id: p6
    type: counterexample
    stars: 2
    refers_to: ["R2", "R3"]
    prompt: >-
      (a) 충격 불변성 (10)을 일부러 깨서 (hd'(-alpha) 를 0.2 만큼 틀리게) 전체 모델을 돌리고 무엇이
      달라지는지 보이라. (b) 평지(gamma = 0)에서 같은 설계를 시도해 zeta* < 0 이 되는 것을 보이고,
      엉덩이 토크를 아무리 키워도 해결되지 않는 이유를 (8)로 설명하라.
    solution_policy: rubric
    solution: >-
      성질 체크리스트: (a) 매 걸음 |y+| != 0 이 남고, 1차원 예측과 전체 모델의 지배 고유값이
      어긋나며, 과도 응답이 주기마다 반복된다. (b) delta_V_zero > 0 이 되어 (5)의 고정점이 음수다.
      토크는 sigma 의 방정식 (8)에 들어오지 않으므로 축소 동역학을 바꾸지 못한다 - 평지 보행에는
      발목이나 몸통 같은 추가 구동이 필요하다.
```

## 논문 읽기

**필독 2편 + 권장 1편.** 각 논문에 고정 질문 10개로 1페이지 노트를 쓴다
(`f0-how-to-read-this-track` 레슨의 "논문 읽기" 절). 3-pass 로 읽고 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Westervelt, Grizzle & Koditschek, "Hybrid zero dynamics of planar biped walkers" (2003,
   IEEE T-AC)** — 역할: `원전(seminal)`. <https://doi.org/10.1109/TAC.2002.806653> (§III·§IV).
   이 레슨의 R1–R4 가 이 논문의 축소판이다.
   추가 질문: ⓐ 저자들의 "hybrid invariance" 조건과 우리 (2)·(10)을 같은 기호로 나란히 쓰라.
   ⓑ 저자들이 축소 사상을 **각운동량**으로 세우는 이유를, 다른 양(예: 전체 에너지)을 썼을 때
   무엇이 깨지는지로 설명하라.
2. **Ames, "Human-inspired control of bipedal walking robots" (2014, IEEE T-AC)**
   — 역할: `표준(standard)`. <https://doi.org/10.1109/TAC.2014.2299342> (§II·§V).
   가상 제약을 **사람 데이터**에서 가져오고 실기(NAO)에서 돌린 사례다.
   추가 질문: ⓐ 사람 데이터로 가상 제약을 고르면 (10)의 충격 불변성은 어떻게 보장하는가?
   ⓑ 실기 실험에서 보고된 실패 모드 중 이 레슨의 가정(점 발, 강체 지면)과 직접 연결되는 것은?
3. **Grizzle, Abba & Plestan (2001)** — 역할: `권장`. <https://doi.org/10.1109/9.898695> (§III).
   `s3-hybrid-limit-cycles` 에서 읽은 논문이다. 이번에는 **축소 없이** 같은 판정을 하는 방법으로
   읽고, 축소가 무엇을 절약하는지 한 문단으로 쓴다.

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 10분 이내, numpy 만. 대상은
`s3-hybrid-limit-cycles` 의 컴퍼스 보행기에 엉덩이 토크를 더한 모델($\gamma=0.05$)이고,
설계 변수는 $\alpha = 0.25$, $h_{\mathrm d}'(\alpha) = -0.8$ 이다. 입력 데이터는 없다.

**수용 기준 (네 조건 모두)**

1. **구조 확인**: 무작위 $(q,\dot q,u)$ $10^3$ 개 ($\lvert u\rvert \le 50$)에서 동역학으로 계산한
   $d\sigma/dt$ 와 중력 모멘트 (8)의 차가 $< 10^{-8}$ (참조 $7.6\cdot10^{-9}$). 토크를 바꿔도
   값이 변하지 않음을 함께 보고한다.
2. **충격 불변성**: (11)의 Bézier 계수로 $h_{\mathrm d}(-\alpha)=\alpha$,
   $h_{\mathrm d}(\alpha)=-\alpha$, $h_{\mathrm d}'(\alpha)=-0.8$ 가 각각 $10^{-12}$ 이내이고
   $h_{\mathrm d}'(-\alpha) = 0.7192862572 \pm 10^{-9}$ 가 (10)의 요구값과 일치한다.
3. **축소 예측**: $\delta_{\mathrm{zero}}^2 = 0.7601914255$,
   $\Delta V_{\mathrm{zero}} = -49.65652176$, $\zeta^\star = 157.4108104$,
   $\dot\theta_{\mathrm s}^{+\star} = 1.32639024$ 를 각각 상대오차 $10^{-6}$ 이내로 재현하고,
   걸음 내내 $\zeta>0$ (최소값 참조 $87.86$)임을 확인한다.
4. **전체 모델 일치**: 예측한 상태에서 출발해 10걸음을 적분해 ⓐ 주기가 $0.495686$ s 로 유지되고
   ⓑ 매 걸음 $\lvert y^+\rvert < 10^{-12}$ ⓒ 3차원 푸앵카레 사상의 지배 고유값이
   $0.76019143$ 과 $10^{-6}$ 이내로 일치하고 나머지 두 고유값의 크기가 $10^{-3}$ 미만이다.

**비교 대상**: ⓐ 충격 불변성을 깬 판($h_{\mathrm d}'(-\alpha)$ 를 $+0.2$ 틀리게) — 조건 4ⓑ·4ⓒ 가
**실패해야 한다** ⓑ 평지($\gamma=0$) — 조건 3 에서 $\zeta^\star<0$ 이 되어 **해가 없어야 한다**
ⓒ `s3-hybrid-limit-cycles` 의 수동 보행(스펙트럼 반지름 $0.582$, 주기 $0.7324$ s) — 같은 보행기에서
설계한 보행이 더 빠르지만($0.4957$ s) 수렴은 느리다($0.760$)는 교환을 표로 보고한다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 1 이 실패($u$ 에 따라 값이 변한다) | $\sigma$ 를 지지발이 아닌 다른 점(엉덩이·무게중심)에 대해 계산했다 | 지지발이 원점인지, 그리고 모든 질량을 포함했는지 확인한다 |
| $\lvert y^+\rvert$ 가 $10^{-3}$ 수준으로 남는다 | (10)의 두 번째 조건을 $w$ 가 아니라 $\dot q^-$ 로 썼다(충격 사상 누락) | $w = Q^{+-1}Q^-(1,h_{\mathrm d}'(\alpha))^\top$ 를 출력해 본다 |
| 지배 고유값이 $\delta^2$ 보다 **크다** | $K_p,K_d$ 가 작아 횡방향이 걸음 시간 안에 죽지 않는다 | $K_p$ 를 4배 키워 고유값이 $\delta^2$ 로 수렴하는지 본다 |
| $\zeta^\star$ 의 부호가 반대로 나온다 | (5)의 부호 — $\zeta^\star = -\delta^2\Delta V/(1-\delta^2)$ 다 | $\Delta V<0$(내리막)에서 $\zeta^\star>0$ 인지 확인한다 |
| 적분 중 토크가 수백 N·m 로 튄다 | $b(q)$ 가 작은 형상을 지난다 | 걸음 구간에서 $\min\lvert b\rvert$ 를 출력하고 $h_{\mathrm d}'(\alpha)$ 를 조정한다 |

## 열린 문제

- **(열린 문제) 가상 제약의 최적 설계** — (11)은 경계 조건만 맞춘 것이고, 남는 자유도(고차 Bézier)로
  무엇을 최적화해야 하는지는 정해져 있지 않다. 토크 최소화·에너지 효율·수렴률은 서로 다른 해를
  주고, 세 목적의 파레토 경계를 축소 모델 안에서 특성화하는 일반 방법이 없다.
  `c4-direct-collocation-sqp` 의 궤적 최적화와 만나는 지점이다.
- **(열린 문제) 3차원과 다중 접촉으로의 확장** — 평면 HZD 의 우아함은 "남는 자유도가 1개"에 기대고
  있다. 3차원 보행에서는 남는 자유도가 여러 개이고 발바닥 면적·발목 토크가 있어 축소가
  1차원으로 떨어지지 않는다. 현재 접근:
  [Ames 2014](https://doi.org/10.1109/TAC.2014.2299342) 의 사람 데이터 기반 제약,
  다중 영역(multi-domain) HZD. 비어 있는 자리: 축소 차원이 2 이상일 때의 닫힌 형태 판정.
- **(열린 문제) 모델 오차 아래의 HZD** — $\delta_{\mathrm{zero}}$ 와 $\Delta V_{\mathrm{zero}}$ 는
  둘 다 모델 적분값이다. 질량·관성·충격 모델이 몇 % 틀리면 예측 고유값이 얼마나 움직이는지에
  대한 민감도 경계가 없다. 비어 있는 자리: 축소 모델의 **강건** 버전 —
  `c3-contraction-incremental` 의 관(tube) 경계를 축소 좌표에 적용하는 시도가 자연스럽다.
- **(열린 문제) 학습과의 결합** — 가상 제약을 데이터에서 학습하면 (10)을 **제약으로** 걸어야
  하는데, 학습된 제약이 충격 불변성을 만족한다는 보장을 유지하는 방법이 정립되지 않았다.
  `s3-locomotion-rl` 에서 반대 방향(제약 없이 학습)과 비교한다.

## 개념 점검

`rc quiz s3-hzd-gait-generation` 으로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`f0-how-to-read-this-track` 레슨의 "문제 세트" 절).

```quiz
activity: s3-hzd-gait-generation-quiz
questions:
  - id: q1
    type: single
    prompt: "엉덩이 토크가 **지지발에 대한 전체 각운동량** $\\sigma$ 를 바꿀 수 없는 이유는?"
    choices:
      - "토크가 작기 때문"
      - "엉덩이 토크는 두 다리 사이의 내력이어서 지지발에 대한 모멘트가 0 이기 때문"
      - "$\\sigma$ 가 보존량이기 때문"
      - "충격이 $\\sigma$ 를 지배하기 때문"
    answer: 1
    explanation: "내력은 전체 각운동량에 기여하지 않고, 지면 반력은 지지발에 작용하므로 그 점에 대한 모멘트가 0 이다. 남는 것은 중력뿐이어서 $\\dot\\sigma = \\tau_g$ 다. 본문에서 토크를 $\\pm50$ N·m 로 흔들어도 차이가 $7.6\\cdot10^{-9}$ 이내였다 — 이것이 HZD 축소의 물리적 근거다."
    concept: { front: "HZD 축소가 성립하는 물리적 이유", back: "엉덩이 토크는 지지발에 대한 모멘트가 0 → $\\dot\\sigma = \\tau_g$ 는 토크와 무관" }
  - id: q2
    type: truefalse
    prompt: "출력을 0 으로 만드는 피드백이 있으면 영역 동역학 면은 하이브리드 계 전체에 대해 불변이다."
    answer: false
    explanation: "연속 흐름에 대해서만 불변이다. 충격이 상태를 면 밖으로 던지면 걸음마다 과도 응답이 반복되고 축소 모델의 예측이 깨진다. 그래서 $\\Delta(S\\cap Z)\\subset Z$ 를 **설계 조건**으로 걸어야 하고, 그 H 가 HZD 의 H 다."
    concept: { front: "HZD 의 'H'", back: "충격 불변성 $\\Delta(S\\cap Z)\\subset Z$ — 가상 제약의 경계 조건으로 번역된다" }
  - id: q3
    type: short
    prompt: "$Z$ 위의 걸음 사상 $\\zeta^+_{k+1} = \\delta^2(\\zeta^+_k - \\Delta V)$ 의 고정점을 $\\delta$ 와 $\\Delta V$ 로 쓰면?"
    answer: ["-delta^2 dV/(1-delta^2)", "-d^2 dV/(1-d^2)", "zeta* = -delta^2 deltaV/(1-delta^2)", "−δ²ΔV/(1−δ²)"]
    explanation: "$\\zeta^\\star = \\delta^2(\\zeta^\\star-\\Delta V)$ 를 풀면 $\\zeta^\\star = -\\delta^2\\Delta V/(1-\\delta^2)$ 다. 내리막에서 $\\Delta V<0$ 이므로 양수가 되고, 평지·오르막에서는 음수가 되어 **해가 없다**. 수치: $-0.760\\cdot(-49.657)/(1-0.760) = 157.41$."
    concept: { front: "축소 보행의 고정점", back: "$\\zeta^\\star = -\\delta^2\\Delta V/(1-\\delta^2)$. 존재는 $\\zeta^\\star>0$, 안정성은 $\\delta^2<1$ 로 분리된다" }
  - id: q4
    type: single
    prompt: "축소 모델이 예측한 수렴률 $\\delta_{\\mathrm{zero}}^2 = 0.760$ 과 4상태 전체 모델의 지배 고유값이 8자리까지 일치한 이유로 가장 정확한 것은?"
    choices:
      - "모델이 선형이기 때문"
      - "$Z$ 가 하이브리드 불변이고 횡방향이 걸음 시간보다 훨씬 빠르게 죽어 푸앵카레 사상이 블록 삼각이 되기 때문"
      - "적분기의 정밀도가 높기 때문"
      - "우연이다"
    answer: 1
    explanation: "충격 불변성 덕분에 궤적이 $Z$ 를 떠나지 않고, 횡방향 고유값이 $4.6\\cdot10^{-5}$ 와 $0$ 으로 사실상 소멸해 스펙트럼이 축소 방향의 $\\delta^2$ 하나로 결정된다. 충격 불변성을 깨거나 $K_p,K_d$ 를 낮추면 이 일치가 깨진다."
    concept: { front: "축소 예측이 전체 모델과 일치하는 조건", back: "하이브리드 불변성 + 빠른 횡방향 수렴 → 푸앵카레 스펙트럼 = {$\\delta^2$, ≈0, ≈0}" }
```

## 이 단계 공부법

1. **언더액추에이티드의 의미를 먼저 적는다 (30분)** — 점 발 로봇에서 "모든 관절을 궤적에 올린다"가
   왜 불가능한지, 그리고 HZD 가 그 대신 무엇을 포기하는지(남는 1자유도의 **시간 궤적**을 포기한다)
   한 문단으로 쓴다.
2. **$\sigma$ 가 토크와 무관하다는 것을 손과 코드로 확인한다 (60분)** — 재현 과제 조건 1 을 먼저
   통과시킨다. 이 사실 없이는 R3 의 축소가 왜 성립하는지 보이지 않는다.
3. **Bézier 경계 조건을 손으로 푼다 (60분)** — (10)→(11). 충격 사상 $w$ 가 들어오는 자리를 정확히
   짚는다. P2 를 풀면 고차 Bézier 의 남는 자유도가 보인다.
4. **축소 모델만으로 설계를 끝낸다 (90분)** — 조건 2·3. 전체 모델을 **한 번도 적분하지 않고**
   $\delta^2$, $\Delta V$, $\zeta^\star$, $\dot\theta^{+\star}$ 를 구한다. 이것이 HZD 의 실제 가치다.
5. **그 다음에 전체 모델로 확인한다 (90분)** — 조건 4. 첫 걸음부터 리미트 사이클이어야 한다.
   아니면 2·3 중 하나가 틀렸다.
6. **두 가지 방식으로 깨 본다 (60분)** — 비교 대상 ⓐ(충격 불변성 위반)와 ⓑ(평지). 전자는 "H 가
   없으면 HZD 가 아니다", 후자는 "축소 동역학은 토크로 바꿀 수 없다"를 각각 보여 준다.
7. **논문은 "축소가 무엇을 절약하는가"로 읽는다 (135분)** — Westervelt 2003 과 Grizzle 2001 을
   나란히 놓고, 같은 판정을 축소 없이 하려면 무엇을 계산해야 하는지 센다. Ames 2014 는 그 축소를
   실기에 올릴 때 추가로 필요한 것들의 목록으로 읽는다.

**통과 기준**: 백지에서 (4)·(5)·(10)을 유도할 수 있고, $\sigma$ 가 토크와 무관한 이유를 말할 수
있고, 재현 과제의 네 조건을 만족하는 코드와 논문 노트 3편이 있다.
