---
id: s3-centroidal-mpc
title: 중심 동역학과 MPC 보행
summary: >-
  전신 로봇의 운동을 무게중심 주위의 6차원 운동량(중심 동역학)으로 축약하고, 접촉력이 만들 수 있는
  것과 만들 수 없는 것을 압력중심(CoP·ZMP)으로 정식화한다. 일정 높이 가정에서 선형 역진자(LIPM)와
  발산 성분(DCM·캡처 포인트)을 유도하고, 그 불안정 모드 때문에 선형 MPC 에 **종단 제약이 없으면
  QP 가 성공하면서 로봇이 넘어진다**는 것을 수치로 보인다. 끝으로 디딤 없이 복구할 수 있는 외란의
  한계가 지지 다각형 크기로 정확히 결정되는 것을 유도하고 측정한다.
objectives:
  - 중심 동역학을 전신 뉴턴-오일러에서 유도하고 관절 토크가 왜 나타나지 않는지 설명할 수 있다.
  - 접촉 렌치에서 CoP·ZMP 식을 유도하고 점 발과 평발의 차이를 수치로 확인할 수 있다.
  - LIPM 과 DCM 의 닫힌 형태를 유도하고 불안정 모드를 분리할 수 있다.
  - 선형 MPC 를 QP 로 세우고 종단 DCM 제약이 재귀 실현가능성에 왜 필요한지 보일 수 있다.
  - 디딤 없이 복구 가능한 외란의 상한 $\omega p_{\max}$ 를 유도하고 MPC 실험으로 측정할 수 있다.
prerequisites: [s3-hybrid-limit-cycles, c2-constrained-dynamics]
difficulty: 5
estimated_minutes: 540
tags: [legged-robots, centroidal-dynamics, zmp, capture-point, mpc, research]
activities:
  - id: s3-centroidal-mpc-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: s3-centroidal-mpc-papers
    kind: paper
    title: 필독 논문 2편 + 권장 2편 읽기, 논문별 1페이지 노트
    estimated_minutes: 150
  - id: s3-centroidal-mpc-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 180
  - id: s3-centroidal-mpc-reproduction
    kind: reproduction
    title: 재현 과제 — 선형 중심 MPC 와 복구 한계 (R2)
    estimated_minutes: 105
  - id: s3-centroidal-mpc-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Kajita, Hirukawa, Harada & Yokoi, Introduction to Humanoid Robotics (2014)"
    kind: book
    note: ch.4 — ZMP·LIPM·보행 패턴 생성의 교재 서술. (공식 URL 미확인)
  - title: "Tedrake, Underactuated Robotics"
    url: https://underactuated.csail.mit.edu/
    kind: book
    note: ch.18-19 — 중심 동역학·ZMP·MPC 의 로보틱스 쪽 입구. 전문 무료.
  - title: "CVXPY"
    url: https://www.cvxpy.org/
    kind: code
    note: 재현 과제의 MPC QP 를 푼다. 솔버는 아무 것이나 쓴다(참조 구현은 CLARABEL).
papers:
  - id: kajita2003-zmp-preview
    required: true
    role: seminal
    note: "§II, §III"
  - id: dicarlo2018-convex-mpc
    required: true
    role: standard
    note: "§III, §IV"
  - id: pratt2006-capture-point
    role: seminal
  - id: orin2013-centroidal
    role: standard
    note: "§2, §4"
---

# 중심 동역학과 MPC 보행

## 전제와 기호

앞의 두 레슨은 2자유도 보행기를 **끝까지** 다뤘다. 실제 로봇은 20–30 자유도이고, 그 전체를 매
제어 주기에 최적화하는 것은 아직 비싸다. 실무의 타협은 **축약**이다: 로봇을 "무게중심 하나 +
접촉력들"로 보고 거기서 계획한 뒤, 전신 제어기(다음 레슨)가 그 계획을 관절로 내린다.

이 축약이 정당한 이유는 하나뿐이다 — **관절 토크는 전체 운동량을 바꾸지 못한다.** 바꾸는 것은
외력(중력과 접촉력)뿐이고, 그래서 "무게중심과 접촉력"의 언어로 쓴 동역학은 **정확**하다
(근사가 아니다). 근사가 들어오는 것은 그 다음, LIPM 에서다.

전제: `c2-constrained-dynamics` 의 접촉 제약과 렌치, `s3-hybrid-limit-cycles` 의 보행 모델,
선형 MPC 의 QP 형태(`c4-mpc` 를 아직 안 봤다면 이 레슨이 그 축소판이다).

| 기호 | 뜻 |
|---|---|
| $M$ | 전체 질량. $r_{\mathrm{com}} = (x, z)$ 는 무게중심(평면) |
| $h_G = (l_G, L_G)$ | 중심 운동량 — 선운동량 $l_G = M\dot r_{\mathrm{com}}$ 과 무게중심에 대한 각운동량 $L_G$ |
| $f_i, p_i$ | $i$ 번째 접촉의 힘과 위치 |
| $p_{\mathrm{zmp}}$ | 압력중심(CoP) = 평지에서의 ZMP |
| $p_{\max}$ | 지지 다각형 반길이(평면 모델) |
| $z$ | 무게중심 높이(LIPM 에서 상수) |
| $\omega = \sqrt{g/z}$ | LIPM 의 시간 상수의 역수 |
| $\xi = x + \dot x/\omega$ | DCM(divergent component of motion) = 캡처 포인트 |
| $N$, $\Delta t$ | MPC 지평선 길이와 시간 간격 |

수치는 $z = 0.8$ m, $g = 9.81$ m/s²($\omega = 3.5017852590$ 1/s, $1/\omega = 0.2855686246$ s),
$p_{\max} = 0.05$ m, MPC 는 $N = 40$, $\Delta t = 0.05$ s 로 계산했다. 중심 동역학의 검증에는
`s3-hybrid-limit-cycles` 의 컴퍼스 보행기(점 발, 엉덩이 토크만)를 쓴다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`f0-how-to-read-this-track` 레슨의 "유도 깊이 등급" 절).

- **R1 (중심 동역학) [D3]** — 임의의 다물체 로봇에서
  $$
  M\ddot r_{\mathrm{com}} = \sum_i f_i + Mg, \qquad
  \dot L_G = \sum_i (p_i - r_{\mathrm{com}}) \times f_i + \sum_i \tau_i \tag{1}
  $$
  이고, **관절 토크는 어디에도 나타나지 않는다**(내력). 점 발($\tau_i = 0$)이면 $\dot L_G$ 는
  접촉력의 모멘트로 완전히 결정된다. 수치 확인: 컴퍼스 보행기에서 엉덩이 토크를 $\pm60$ N·m 로
  흔들어도 $\lvert \dot L_G - (p_{\text{foot}}-r_{\mathrm{com}})\times f_c\rvert \le 5.7\cdot10^{-14}$.
- **R2 (CoP·ZMP) [D3]** — 평면에서 접촉 렌치의 모멘트 균형을 풀면
  $$
  p_{\mathrm{zmp}} = x + \frac{\dot L_G/M - z\,\ddot x}{\ddot z + g}. \tag{2}
  $$
  단방향 접촉(끌어당길 수 없음)이 $p_{\mathrm{zmp}} \in [\,-p_{\max}, p_{\max}]$ 를 강제한다.
  점 발은 $p_{\mathrm{zmp}}$ 가 **발 위에 고정**되므로 (2)가 $\dot L_G$ 를 결정해 버린다
  (수치: $\lvert p_{\mathrm{zmp}}\rvert \le 4.7\cdot10^{-15}$). 평발은 $p_{\max}$ 만큼의
  **여유**를 사는 것이고, 그 여유가 이 레슨의 나머지 전부다.
- **R3 (LIPM 과 DCM) [D2]** — $z$ 가 상수이고 $\dot L_G = 0$ 이면 (2)가
  $$
  \ddot x = \omega^2\,(x - p_{\mathrm{zmp}}), \qquad \omega = \sqrt{g/z} \tag{3}
  $$
  로 선형화되고, $\xi := x + \dot x/\omega$ 가 **불안정 모드만** 뽑아낸다:
  $$
  \dot\xi = \omega\,(\xi - p_{\mathrm{zmp}}),
  \qquad
  \xi(t) = p + (\xi_0 - p)e^{\omega t}\ \ (p\ \text{상수}). \tag{4}
  $$
  (수치 확인: $10^{-16}$ 수준으로 일치.) 나머지 성분 $x - \xi$ 는 $e^{-\omega t}$ 로 **저절로**
  수렴하므로, 보행 제어는 $\xi$ 하나를 다루는 문제로 줄어든다.
- **R4 (선형 MPC 와 재귀 실현가능성) [D2]** — (4)를 $\Delta t$ 로 이산화하면
  $\xi_{k+1} = e^{\omega\Delta t}\xi_k + (1-e^{\omega\Delta t})p_k$ 이고, $\lvert p_k\rvert \le p_{\max}$
  아래에서 비용을 최소화하는 QP 가 된다. **$e^{\omega\Delta t} > 1$ 이므로 종단 제약이 없으면
  QP 는 지평선 안의 비용만 줄이고 그 뒤를 버린다**: $\Delta v = 0.3$ m/s 의 외란에서 QP 는
  "최적해"를 돌려주지만 지평선 끝의 $\lvert\xi_N\rvert$ 가 $39.3$ m 다. 종단 제약
  $\lvert\xi_N\rvert \le \epsilon$ 을 넣으면 같은 외란에서 **실현불가능**으로 정직하게 보고한다.
- **R5 (디딤 없는 복구의 한계) [D2]** — (4)에서 $\xi$ 를 줄이려면 $p > \xi$ 여야 하고
  $p \le p_{\max}$ 이므로, 디딤(발 위치 변경) 없이 복구 가능한 조건은 정확히
  $$
  \lvert \xi \rvert < p_{\max} \;\Longleftrightarrow\;
  \lvert \Delta v \rvert < \omega\,p_{\max} \quad(\text{정지 상태에서 받은 충격}). \tag{5}
  $$
  수치: $\omega p_{\max} = 0.17508926$ m/s, MPC 로 이분법 측정한 문턱 $0.17493343$ m/s
  (상대차 $0.09\%$ — 이산화와 종단 허용오차 때문). **캡처 포인트가 지지 다각형을 벗어나면
  반드시 발을 옮겨야 한다**는 명제의 정량적 형태다.

## 유도

### R1 — 중심 동역학: 관절 토크가 사라지는 이유

로봇을 강체 $i = 1,\dots,n$ 의 집합으로 본다. 각 강체의 뉴턴·오일러 방정식을 **모두 더한다**.
내력(관절에서 서로 주고받는 힘·모멘트)은 작용·반작용으로 쌍쌍이 소거되므로 합에는 외력만 남는다:

$$
\sum_i m_i \ddot r_i = \sum_j f_j + Mg
\;\Longrightarrow\;
M\ddot r_{\mathrm{com}} = \sum_j f_j + Mg,
$$

여기서 $r_{\mathrm{com}} = \frac1M\sum m_i r_i$ 의 정의를 썼다. 각운동량은 **무게중심에 대해**
모은다. $L_G = \sum_i \big[I_i\omega_i + m_i (r_i - r_{\mathrm{com}})\times \dot r_i\big]$ 를
미분하면

$$
\dot L_G = \sum_i \big[I_i\dot\omega_i + m_i (r_i-r_{\mathrm{com}})\times\ddot r_i\big]
  + \underbrace{\sum_i m_i(\dot r_i - \dot r_{\mathrm{com}})\times\dot r_i}_{=\,0}
$$

(마지막 항은 $\sum m_i \dot r_i \times \dot r_i = 0$ 과 $\dot r_{\mathrm{com}}\times M\dot r_{\mathrm{com}} = 0$
로 사라진다). 각 강체의 오일러 방정식을 넣고 내부 모멘트를 소거하면 (1)이 된다. **중력은 무게중심에
대해 모멘트가 0 이다**($\sum m_i(r_i-r_{\mathrm{com}})\times g = 0$) — 이것이 무게중심을 기준점으로
고르는 이유다.

**수치 확인 (점 발)**: 컴퍼스 보행기에서 $(q,\dot q)$ 와 엉덩이 토크 $u \in [-60,60]$ N·m 를
무작위로 3000번 뽑아 ⓐ 동역학으로 $\ddot q$ 를 풀고 ⓑ $L_G$ 와 $\dot L_G$ 를 직접 계산하고
ⓒ 접촉력 $f_c = M(\ddot r_{\mathrm{com}} - g)$ 의 발에 대한 모멘트와 비교하면 최대 차가
$5.7\cdot10^{-14}$ 다. $\dot L_G$ 를 유한차분으로 다시 계산한 값과도 $5.7\cdot10^{-9}$ 이내로
일치한다(차분 오차 수준). **토크를 어떻게 흔들어도 이 등식은 변하지 않는다.**

**가정이 깨지는 곳**: 발목에 토크가 있으면(평발 + 구동 발목) $\sum\tau_i \ne 0$ 이 되어 (1)의
둘째 식에 입력이 들어온다 — 그것이 평발 로봇이 점 발보다 쉬운 이유이고, (2)에서 $p_{\max}$ 로
나타난다. 또 (1)은 **접촉점의 위치를 안다**고 가정한다. 미끄러짐·지형 오차는 $p_i$ 의 불확실성으로
들어오고, 중심 계획은 그것을 모른다 — `s3-dynamic-maneuvers` 의 주제다.

### R2 — CoP: 접촉이 만들 수 있는 모멘트의 한계

접촉 렌치를 "한 점 $p$ 에 작용하는 힘 $f$ + 그 점에 대한 모멘트 $m_p$"로 쓰고, **CoP** 를
$m_p = 0$ 이 되는 점으로 정의한다(평지, 수직 모멘트 무시). 그러면 (1)의 둘째 식이

$$
\dot L_G = (p - r_{\mathrm{com}}) \times f, \qquad f = M(\ddot r_{\mathrm{com}} - g)
$$

이고, 평면에서 $p = (p_{\mathrm{zmp}}, 0)$, $r_{\mathrm{com}} = (x,z)$, $f = (M\ddot x,\ M(\ddot z + g))$ 를
넣어 전개하면

$$
\dot L_G = (p_{\mathrm{zmp}} - x)\,M(\ddot z+g) + z\,M\ddot x
$$

이므로 (2)가 나온다. **단방향 접촉**($f_z \ge 0$, 발이 지면을 당길 수 없음)이 CoP 를 발바닥
내부로 제한하고, 그래서 (2)는 "달성 가능한 $(\ddot x, \dot L_G)$ 의 집합"을 정의하는 **제약**이다.

- **점 발**: 지지 다각형이 한 점이므로 $p_{\mathrm{zmp}}$ 가 발에 고정되고, (2)는 $\dot L_G$ 를
  **계산해 버린다** — 자유도가 없다. 수치로 확인하면 $\lvert p_{\mathrm{zmp}}\rvert \le 4.7\cdot10^{-15}$
  로 발 위에 붙어 있다(컴퍼스 보행기, 토크 무작위).
- **평발**: $p_{\mathrm{zmp}}$ 를 $[-p_{\max},p_{\max}]$ 에서 고를 수 있다. 이 **한 구간**이
  보행 제어의 입력이다.

**가정이 깨지는 곳**: ⓐ 경사·요철 지형에서는 "지지 다각형"이 평면 다각형이 아니고 마찰 원뿔까지
고려해야 한다(접촉 렌치 원뿔, `c2-contact-dynamics`). ⓑ 여러 접촉이 있으면 CoP 는 개별 접촉력의
가중 평균이므로, CoP 가 다각형 안에 있어도 **개별** 접촉력이 마찰 한계를 넘을 수 있다 —
CoP 조건은 **필요조건일 뿐**이다. 이 사실이 평발 ZMP 보행과 다중 접촉 MPC 를 갈라놓는다
(Di Carlo et al. 2018 은 접촉력을 직접 변수로 둔다).

### R3 — LIPM 과 DCM: 불안정 모드만 떼어내기

(2)에 두 가정을 넣는다: $z$ 가 상수($\ddot z = 0$)이고 $\dot L_G = 0$. 그러면
$p_{\mathrm{zmp}} = x - z\ddot x/g$, 즉 (3)이다. 이 선형계의 고유값은 $\pm\omega$ — **하나가
불안정하다**. 불안정 모드의 좌표를 고른다:

$$
\xi := x + \frac{\dot x}{\omega}
\;\Longrightarrow\;
\dot\xi = \dot x + \frac{\ddot x}{\omega} = \dot x + \omega(x - p) = \omega\left(x + \frac{\dot x}{\omega} - p\right)
 = \omega(\xi - p),
$$

즉 (4)의 첫 식이다. 반대 조합 $\eta := x - \dot x/\omega$ 는 $\dot\eta = -\omega(\eta - p)$ 로
**저절로 수렴**한다. 따라서 상태를 $(\xi,\eta)$ 로 바꾸면 보행 제어는 $\xi$ 하나를 지지 다각형
안으로 넣는 문제가 된다 — $\eta$ 는 내버려 두면 된다.

$p$ 가 구간마다 상수면 (4)는 **닫힌 형태** $\xi(t) = p + (\xi_0-p)e^{\omega t}$ 로 풀린다.
수치 확인: 무작위 $(x,\dot x,p,\Delta t)$ 2000개에서 정확해로 한 걸음 보낸 뒤 (4)와 비교하면
최대 차가 $4.4\cdot10^{-16}$ 다.

**$\xi$ 의 이름들**: 발산 성분(DCM), 캡처 포인트(capture point), 즉시 캡처 점 — 같은 양의 다른
이름이다. 물리적 뜻: **지금 발을 $\xi$ 에 놓으면 로봇이 (LIPM 모델 안에서) 정지한다**.
$p = \xi$ 로 두면 (4)에서 $\dot\xi = 0$ 이므로 $\xi$ 가 **그 자리에 멈춘다** — 줄어들지 않는다.
줄이려면 $p$ 를 $\xi$ **너머**로 보내야 하고, 그 여유가 $p_{\max}$ 다. 이 한 문장이 R5 다.

**가정이 깨지는 곳**: $\dot L_G = 0$ 과 $\ddot z = 0$ 은 **선택**이지 사실이 아니다. 팔을 휘두르거나
무릎을 굽히면 둘 다 깨지고, 그때 (3)은 틀린다 — 그러나 (2)는 여전히 정확하다. 실무의 순서는
"LIPM 으로 계획하고, 전신 제어기가 $\dot L_G$ 를 0 으로 **만들어** 준다"이고, 그 전신 제어기가
다음 레슨이다.

### R4·R5 — MPC, 종단 제약, 그리고 복구 한계

(4)를 $\Delta t$ 간격으로 이산화한다($p$ 는 구간 상수):

$$
\xi_{k+1} = a\,\xi_k + (1-a)\,p_k, \qquad a := e^{\omega\Delta t} > 1. \tag{6}
$$

MPC 는 $\min \sum_{k=1}^{N}\xi_k^2 + \rho\sum_k p_k^2$ 를 $\lvert p_k\rvert\le p_{\max}$ 아래에서
푸는 QP 다. 문제는 $a>1$ 이다: 지평선 **안**의 $\xi_k$ 를 줄이는 것과 **끝난 뒤** 발산하지
않는 것은 다른 요구다.

**실험 (종단 제약 없음)**: $\Delta v = 0.3$ m/s 의 충격($\xi_0 = 0.08567$ m $> p_{\max}$)에서 QP 는
"optimal" 을 돌려주고 비용도 유한하다. 그런데 그 해의 지평선 끝 DCM 은
$\lvert\xi_N\rvert = 39.307468$ m 다 — **QP 는 성공했고 로봇은 넘어진다**. 종단 제약
$\lvert\xi_N\rvert\le10^{-3}$ 을 넣으면 같은 외란에서 QP 가 **실현불가능**을 보고한다. 이것이
정직한 답이다: 그 외란은 디딤 없이 복구할 수 없다.

**복구 한계의 유도.** (4)에서 $\lvert\xi\rvert$ 가 줄어들려면 $\operatorname{sign}$ 을 따져
$p$ 가 $\xi$ 보다 **멀리** 있어야 한다. $\lvert p\rvert\le p_{\max}$ 이므로 $\lvert\xi\rvert < p_{\max}$
가 필요하고, 충분하다(상수 $p = p_{\max}\operatorname{sign}\xi$ 로 (4)를 풀면 유한 시간에
$\xi\to0$ 으로 몰 수 있다). 정지 상태에서 받은 충격 $\Delta v$ 는 $\xi_0 = \Delta v/\omega$ 를 만들므로
(5)가 된다. 수치: 임계값을 MPC 실현가능성의 이분법으로 재면 $0.17493343$ m/s 이고
$\omega p_{\max} = 0.17508926$ m/s 와 $0.09\%$ 차이다(이산화 $\Delta t=0.05$ s 와 종단 허용오차
$10^{-3}$ 이 설명한다).

| $\Delta v$ (m/s) | $\xi_0$ (m) | 종단 제약 있는 QP |
|---|---|---|
| 0.050 | 0.01428 | 실현가능 |
| 0.150 | 0.04284 | 실현가능 |
| 0.174 | 0.04969 | 실현가능 |
| **0.176** | **0.05026** | **실현불가능** |
| 0.300 | 0.08567 | 실현불가능 |

**가정이 깨지는 곳**: (5)는 **디딤 없음**을 전제한다. 발을 옮기면 지지 다각형이 이동하므로
복구 가능 집합이 훨씬 커진다 — 그것이 `s3-dynamic-maneuvers` 의 접촉 일정 최적화다. 또 (5)는
LIPM 안의 명제다: 팔 휘두르기($\dot L_G \ne 0$)와 무릎 굽히기($\ddot z \ne 0$)는 (2)를 통해
추가 여유를 만든다. 사람이 그 두 가지를 모두 쓰는 이유다.

## 증명 스케치

### R4 — 종단 제약이 재귀 실현가능성을 주는 이유

**가설** H1: (6)이 성립하고 $a>1$. H2: $\lvert p_k\rvert\le p_{\max}$. H3: 종단 제약
$\mathcal{X}_f = \{\lvert\xi\rvert\le\epsilon\}$ 이고 $\epsilon < p_{\max}$. H4: $\mathcal{X}_f$ 가
**제어 불변**이다 — 즉 $\lvert\xi\rvert\le\epsilon$ 이면 $\lvert p\rvert\le p_{\max}$ 로
$\lvert\xi^+\rvert\le\epsilon$ 을 만들 수 있다.
**결론** C: 시각 $k$ 에서 QP 가 실현가능하면 $k+1$ 에서도 실현가능하고, 폐루프는
$\mathcal{X}_f$ 로 수렴한다.

**전략**: 표준 MPC 논증(`c4-mpc`)을 그대로 쓴다. 핵심은 H4 를 **확인**하는 것뿐이다.

1. **꼬리 이어붙이기.** $k$ 의 최적해 $(p_k^\star,\dots,p_{k+N-1}^\star)$ 가 $\xi_{k+N}\in\mathcal{X}_f$
   를 만족한다. $k+1$ 에서는 그 해의 뒤쪽을 그대로 쓰고 **마지막에 H4 가 주는 입력 하나를
   붙인다**. 그 후보는 (6)과 H2·H3 를 모두 만족하므로 $k+1$ 의 QP 는 실현가능하다.
2. **H4 의 확인.** (6)에서 $\xi^+ = a\xi + (1-a)p$ 이고 $a>1$ 이므로 $p = \xi$ 로 두면
   $\xi^+ = \xi$ (멈춤), $p = p_{\max}\operatorname{sign}\xi$ 로 두면
   $\lvert\xi^+\rvert = \lvert a\xi - (a-1)p_{\max}\operatorname{sign}\xi\rvert$ 가
   $\lvert\xi\rvert < p_{\max}$ 에서 **줄어든다**. 따라서 $\epsilon < p_{\max}$ 인 어떤
   $\mathcal{X}_f$ 도 제어 불변이다.
3. **수렴.** 최적 비용을 Lyapunov 함수로 쓰면 1단계의 후보해가 비용의 비증가를 주고,
   비용이 $\sum\xi_k^2$ 를 포함하므로 $\xi_k\to\mathcal{X}_f$ 다
   (`c3-lyapunov-stability` 의 R3 를 이산 사상에 적용).

**가설을 지우면**: H3(종단 제약)를 빼면 1단계의 꼬리 이어붙이기가 $\xi_{k+N}$ 에 대해 아무 것도
보장하지 못하고, $a>1$ 때문에 **지평선 밖에서 발산**한다 — 수치 실험의 $39.3$ m 가 그 모습이다.
H4 가 깨지는 경우($\epsilon \ge p_{\max}$)에는 종단 집합 자체가 지킬 수 없는 약속이 된다.
H2 를 빼면(지지 다각형 무한) 문제가 자명해진다 — 보행 제어의 어려움 전부가 H2 에서 온다.

생략한 기술적 단계: 종단 비용을 쓰는 변형(종단 집합 대신 $P$-가중 종단 비용)과 그 동등성,
`c4-mpc` 의 정리. 또 (6)의 이산화 오차가 재귀 실현가능성을 깨뜨리지 않는 조건(강건 MPC).

## 문제 세트

```problemset
activity: s3-centroidal-mpc-problems
problems:
  - id: p1
    type: derivation
    stars: 2
    refers_to: ["R1", "R2"]
    prompt: >-
      (1)에서 (2)를 유도하라. 평면에서 접촉 렌치를 CoP 로 쓰는 단계와 중력이 무게중심에 대해 모멘트를
      만들지 않는다는 사실을 각각 어디에서 쓰는지 표시하라. 이어서 발목 토크 tau_a 가 있는 평발의
      경우 (2)가 어떻게 바뀌는지 쓰라.
    solution_policy: sketch
    solution: >-
      L_G dot = (p - r_com) x f 에 f = M(r_com ddot - g) 를 넣고 평면 성분으로 전개한다. 중력의
      모멘트 소거는 L_G 를 무게중심 기준으로 정의한 데서 나온다. 발목 토크가 있으면 오른쪽에 + tau_a
      가 붙어 p_zmp 가 tau_a/(M(zddot+g)) 만큼 이동한다 - 평발이 사는 여유를 토크로도 살 수 있다는 뜻이다.
  - id: p2
    type: derivation
    stars: 2
    refers_to: ["R3"]
    prompt: >-
      xi = x + xdot/omega 와 eta = x - xdot/omega 로 좌표를 바꿔 (3)을 두 개의 1차 방정식으로 분해하라.
      초기값에서 eta 성분이 폐루프 거동에 미치는 영향이 왜 걸음 시간 규모에서 무시되는지, 1/omega 의
      수치와 함께 설명하라.
    solution_policy: sketch
    solution: >-
      행렬 [[0,1],[omega^2,0]] 의 고유벡터가 (1, +-omega) 이고 그 좌표가 xi, eta 다. eta 는
      e^{-omega t} 로 줄어들고 1/omega = 0.2856 s 이므로 한 걸음(0.5-0.8 s)에 e^{-2} 이하로 줄어든다.
      그래서 보행 제어는 xi 만 다룬다.
  - id: p3
    type: proof
    stars: 3
    refers_to: ["R4", "R5"]
    prompt: >-
      종단 집합 X_f = {|xi| <= eps} 가 eps < p_max 일 때 제어 불변임을 증명하고, 그것으로 재귀
      실현가능성을 증명하라. 이어서 eps >= p_max 이면 어디가 깨지는지 보이라.
    solution_policy: sketch
    solution: >-
      전략: (6)에서 p = p_max sign(xi) 를 넣어 |xi^+| < |xi| 를 보이고(a > 1 이 필요), 꼬리
      이어붙이기로 실현가능성을 전파한다. eps >= p_max 이면 |xi| 가 p_max 를 넘는 상태가 X_f 안에
      있고 그 상태에서는 어떤 p 로도 |xi| 를 줄일 수 없어 불변성이 깨진다.
  - id: p4
    type: numerical
    stars: 1
    refers_to: ["R3", "R5"]
    prompt: >-
      z = 0.8 m, g = 9.81 m/s^2, p_max = 0.05 m 에서 (a) omega, (b) 1/omega, (c) 정지 상태에서
      디딤 없이 복구 가능한 최대 충격 속도, (d) 그 충격을 받은 직후의 xi 를 구하라.
    solution_policy: answer
    solution: >-
      (a) omega = 3.5017852590 1/s, (b) 0.2855686246 s, (c) omega * p_max = 0.17508926 m/s,
      (d) xi = dv/omega = p_max = 0.05 m. 검산: MPC 로 이분법 측정한 문턱은 0.17493343 m/s 로
      상대차 0.09% 다(이산화와 종단 허용오차).
    tolerance: 1.0e-6
  - id: p5
    type: implementation
    stars: 2
    refers_to: ["R4", "R5"]
    prompt: >-
      (6)의 선형 MPC 를 QP 로 구현해 재현 과제의 네 조건을 통과시켜라. 추가로 지평선 N 을
      10, 20, 40, 80 으로 바꿔 (a) 측정 문턱 (b) 종단 제약 없는 판의 |xi_N| 를 표로 만들고, N 을
      키우는 것이 종단 제약을 대체할 수 있는지 논하라.
    solution_policy: rubric
    solution: >-
      통과 기준: (1) N 을 키우면 측정 문턱이 omega p_max 로 단조 접근 (2) 종단 제약 없는 판의
      |xi_N| 가 N 에 대해 지수적으로 커짐을 보임 (3) "충분히 긴 지평선"이 종단 제약을 근사하지만
      수치적으로 e^{omega N dt} 의 조건수 문제를 만든다는 점을 지적. 솔버와 허용오차를 함께 보고.
  - id: p6
    type: counterexample
    stars: 2
    refers_to: ["R3", "R4"]
    prompt: >-
      (a) p = xi (캡처 포인트에 CoP 를 두는 '직관적' 제어)가 xi 를 줄이지 못함을 (4)로 보이고
      수치로 확인하라. (b) 종단 제약 없는 MPC 가 "성공"하면서 로봇이 넘어지는 사례를 재현하고,
      비용 함수만 보고 설계를 판단하면 안 되는 이유를 쓰라.
    solution_policy: rubric
    solution: >-
      통과 기준: (a) p = xi 에서 xi dot = 0 이므로 DCM 이 그 자리에 머문다 - 수렴하지 않는다.
      (b) dv = 0.3 m/s 에서 QP status 가 optimal 인데 |xi_N| = 39.3 m 임을 보이고, 종단 제약을
      넣으면 infeasible 로 바뀌는 것을 대조한다.
```

## 논문 읽기

**필독 2편 + 권장 2편.** 각 논문에 고정 질문 10개로 1페이지 노트를 쓴다
(`f0-how-to-read-this-track` 레슨의 "논문 읽기" 절).

1. **Kajita et al., "Biped walking pattern generation by using preview control of zero-moment
   point" (2003, ICRA)** — 역할: `원전(seminal)`. <https://doi.org/10.1109/ROBOT.2003.1241826>
   (§II·§III). ZMP 를 추종하는 preview 제어가 사실상 "미래를 보는 선형 MPC"다.
   추가 질문: ⓐ preview 이득이 우리 (6)의 MPC 와 어떤 관계인가 — 제약이 없을 때 둘은 같은가?
   ⓑ 저자들이 $\dot L_G = 0$ 과 $\ddot z = 0$ 을 어디에서 쓰고, 실기에서 그 가정이 깨질 때 무엇을
   하는가?
2. **Di Carlo et al., "Dynamic locomotion in the MIT Cheetah 3 through convex model-predictive
   control" (2018, IROS)** — 역할: `표준(standard)`.
   <https://doi.org/10.1109/IROS.2018.8594448> (§III·§IV). 접촉력을 **직접** 변수로 두는 중심
   MPC 다.
   추가 질문: ⓐ CoP 제약 대신 마찰 원뿔과 접촉력 상한을 쓰면 R2 의 "필요조건일 뿐" 문제가 어떻게
   해결되는가? ⓑ 저자들이 볼록성을 유지하기 위해 포기한 것(각운동량 항, 접촉 일정)은 무엇인가?
3. **Pratt et al., "Capture Point: a step toward humanoid push recovery" (2006, Humanoids)**
   — 역할: `권장`. <https://doi.org/10.1109/ICHR.2006.321385> — (5)의 원전.
4. **Orin, Goswami & Lee, "Centroidal dynamics of a humanoid robot" (2013, Autonomous Robots)**
   — 역할: `권장`. <https://doi.org/10.1007/s10514-013-9341-4> (§2·§4) — 중심 운동량 행렬
   $A_G(q)$ 의 구조와 계산.

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 10분 이내, numpy + QP 솔버 하나.
대상은 ⓐ `s3-hybrid-limit-cycles` 의 컴퍼스 보행기(조건 1)와 ⓑ LIPM($z=0.8$ m, $p_{\max}=0.05$ m,
$N=40$, $\Delta t=0.05$ s)(조건 2–4)다. 입력 데이터는 없다.

**수용 기준 (네 조건 모두)**

1. **중심 동역학과 CoP**: 무작위 $(q,\dot q,u)$ $10^3$ 개($\lvert u\rvert\le60$)에서
   ⓐ $\lvert \dot L_G - (p_{\text{foot}}-r_{\mathrm{com}})\times f_c\rvert < 10^{-10}$
   (참조 $5.7\cdot10^{-14}$) ⓑ (2)로 계산한 $\lvert p_{\mathrm{zmp}}\rvert < 10^{-12}$
   (점 발이므로 발 위에 있어야 한다. 참조 $4.7\cdot10^{-15}$) ⓒ $\dot L_G$ 를 유한차분으로
   재계산해 $10^{-7}$ 이내 일치(참조 $5.7\cdot10^{-9}$).
2. **DCM 닫힌 형태**: 무작위 $(x,\dot x,p,\Delta t)$ $10^3$ 개에서 (4)와 LIPM 정확해의 차가
   $< 10^{-12}$ (참조 $4.4\cdot10^{-16}$). $\omega = 3.5017852590$, $1/\omega = 0.2855686246$ 를
   함께 보고한다.
3. **복구 문턱**: 종단 제약이 있는 MPC 의 실현가능성을 이분법으로 재서 $\Delta v^\star$ 를 구하고
   $\omega p_{\max} = 0.17508926$ m/s 와 **상대차 1% 이내**로 일치시킨다(참조 $0.17493343$,
   차이 $0.09\%$). $\Delta v = 0.174$ 에서 실현가능, $0.176$ 에서 실현불가능임을 함께 보인다.
4. **종단 제약의 효과**: $\Delta v = 0.3$ m/s 에서 ⓐ 종단 제약을 뺀 QP 가 "optimal" 을 보고하면서
   $\lvert\xi_N\rvert > 1$ m 임을 보이고(참조 $39.3$ m) ⓑ 종단 제약을 넣으면 **실현불가능**이
   되는 것을 대조한다. 두 경우의 solver status 를 그대로 보고한다.

**비교 대상**: ⓐ CoP 를 지지 다각형 중앙에 고정($p\equiv0$) — $\xi$ 가 $e^{\omega t}$ 로 발산해야
한다 ⓑ $p = \xi$ (캡처 포인트에 CoP 를 두는 직관적 제어) — $\xi$ 가 **줄지 않고 머무는** 것을
보인다 ⓒ 본문 수치.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 1ⓐ 가 $O(10)$ 으로 틀린다 | 베이스(발목) 관절 토크를 내력으로 취급했다 — 구동 발목은 **외부** 모멘트다 | 점 발 모델(엉덩이 토크만)인지 확인한다. 핀 조인트를 구동하면 (1)에 $\tau$ 가 남는다 |
| 조건 1ⓑ 의 $p_{\mathrm{zmp}}$ 가 $O(10)$ 이다 | (2)의 $\dot L_G$ 항 부호 — $p = x + (\dot L_G/M - z\ddot x)/(\ddot z+g)$ 다 | 점 발에서 0 이 나오는지로 부호를 교정한다 |
| DCM 비교가 $10^{-3}$ 수준이다 | LIPM 을 오일러로 적분했다 | $\cosh/\sinh$ 정확해를 쓰거나 $\Delta t$ 를 줄여 2차 수렴을 확인한다 |
| 측정 문턱이 $\omega p_{\max}$ 보다 **크다** | 종단 허용오차 $\epsilon$ 가 너무 크다($\epsilon \gtrsim p_{\max}$) | $\epsilon$ 를 $10^{-3}$ 으로 조이고 $N$ 을 키운다 |
| QP 가 모든 외란에서 실현가능하다 | 종단 제약을 넣지 않았거나 $p$ 의 상한을 걸지 않았다 | $\lvert p_k\rvert\le p_{\max}$ 와 $\lvert\xi_N\rvert\le\epsilon$ 을 모두 출력해 확인한다 |

## 열린 문제

- **(열린 문제) 각운동량을 쓰는 복구의 정량화** — (5)는 $\dot L_G = 0$ 아래의 한계다. 사람은 팔을
  휘둘러 $\dot L_G \ne 0$ 을 만들어 그 한계를 넘는다. (2)는 그 여유를 정확히 기술하지만, **팔
  관절 한계와 전신 제어 가능성까지 포함한** 복구 가능 집합의 계산은 여전히 비싸다. 비어 있는
  자리: 전신 자유도를 포함한 복구 가능 집합의 실시간 근사.
- **(열린 문제) 접촉 일정이 변수인 중심 MPC** — Di Carlo et al. 2018 은 볼록성을 지키려고 접촉
  일정을 **고정**한다. 일정을 변수로 올리면 혼합정수 문제가 되고 실시간성이 깨진다. 현재 접근:
  위상 기반 매개화([Winkler et al. 2018](https://doi.org/10.1109/LRA.2018.2798285)), 미분 가능한
  완화. 비어 있는 자리: 실시간 안에서 일정 변경을 허용하면서 실현가능성을 보장하는 정식화 —
  `s3-dynamic-maneuvers` 에서 다시 만난다.
- **(열린 문제) 축약의 비용** — 중심 MPC 는 전신 운동학·토크 한계를 모른다. 그래서 중심 계획이
  전신 제어기에서 **실현 불가능**해지는 경우가 실기에서 생긴다. 비어 있는 자리: 중심 계획 단계에서
  전신 실현가능성을 보장하는 (보수적이지만 타이트한) 조건. 다음 레슨
  `s3-whole-body-control` 의 QP 실현가능성과 직접 이어진다.
- **(열린 문제) 모델 오차와 강건 MPC** — $z$ 가 상수가 아니고 접촉 위치에 오차가 있을 때 (6)의
  재귀 실현가능성은 보장되지 않는다. 현재 접근: 관(tube) MPC(`c3-contraction-incremental` 의 관
  경계와 같은 도구), 시나리오 MPC. 비어 있는 자리: 보행에서 쓸 만큼 타이트한 관 크기 추정.

## 개념 점검

`rc quiz s3-centroidal-mpc` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위 문제
세트와 재현 과제다(`f0-how-to-read-this-track` 레슨의 "문제 세트" 절).

```quiz
activity: s3-centroidal-mpc-quiz
questions:
  - id: q1
    type: single
    prompt: "중심 동역학 (1)에 관절 토크가 나타나지 않는 이유는?"
    choices:
      - "관절 토크가 작기 때문"
      - "관절 토크는 내력이어서 전체 운동량의 변화율에 기여하지 않기 때문"
      - "무게중심을 기준점으로 잡았기 때문"
      - "중력이 지배적이기 때문"
    answer: 1
    explanation: "강체별 뉴턴·오일러를 모두 더하면 내력은 작용·반작용으로 쌍쌍이 소거된다. 남는 것은 중력과 접촉력뿐이다. 다만 **구동 발목**은 지면과 로봇 사이의 외부 모멘트이므로 예외다 — 그래서 평발 로봇이 점 발보다 쉽다."
    concept: { front: "중심 동역학에 관절 토크가 없는 이유", back: "내력은 전체 운동량을 바꾸지 못한다. 구동 발목은 외력이므로 예외" }
  - id: q2
    type: short
    prompt: "LIPM 에서 DCM(캡처 포인트)의 정의를 $x$, $\\dot x$, $\\omega$ 로 쓰면?"
    answer: ["x + xdot/omega", "x + v/omega", "x + xdot/w", "x + ẋ/ω"]
    explanation: "$\\xi = x + \\dot x/\\omega$ 이고 $\\dot\\xi = \\omega(\\xi - p)$ 로 **불안정 모드만** 담는다. 반대 조합 $x - \\dot x/\\omega$ 는 $e^{-\\omega t}$ 로 저절로 수렴하므로 보행 제어는 $\\xi$ 하나를 다루는 문제가 된다."
    concept: { front: "DCM(캡처 포인트)", back: "$\\xi = x + \\dot x/\\omega$, $\\dot\\xi = \\omega(\\xi-p)$ — LIPM 의 불안정 모드" }
  - id: q3
    type: truefalse
    prompt: "CoP 를 캡처 포인트에 두면($p = \\xi$) DCM 이 0 으로 수렴한다."
    answer: false
    explanation: "(4)에서 $p=\\xi$ 면 $\\dot\\xi = 0$ 이므로 DCM 이 **그 자리에 머문다**. 줄이려면 CoP 를 $\\xi$ 너머로 보내야 하고, 그 여유가 지지 다각형 $p_{\\max}$ 다. 그래서 복구 가능 조건이 $|\\xi| < p_{\\max}$ 로 나온다."
    concept: { front: "$p=\\xi$ 로 두면?", back: "DCM 이 멈춘다(수렴하지 않는다). 줄이려면 $p$ 를 $\\xi$ 너머로 — 그래서 $|\\xi|<p_{\\max}$ 가 복구 조건" }
  - id: q4
    type: single
    prompt: "종단 DCM 제약이 없는 선형 MPC 가 큰 외란에서 보이는 전형적 증상은?"
    choices:
      - "QP 가 실현불가능을 보고한다"
      - "QP 가 optimal 을 보고하는데 지평선 끝의 DCM 이 발산한다"
      - "CoP 가 지지 다각형을 벗어난다"
      - "계산 시간이 급증한다"
    answer: 1
    explanation: "$e^{\\omega\\Delta t}>1$ 이므로 비용은 지평선 **안**만 본다. $\\Delta v = 0.3$ m/s 실험에서 QP 는 optimal 을 돌려주면서 $|\\xi_N| = 39.3$ m 였다 — QP 는 성공하고 로봇은 넘어진다. 종단 제약을 넣으면 같은 외란에서 정직하게 infeasible 이 된다."
    concept: { front: "종단 제약 없는 MPC 의 함정", back: "불안정 모드가 지평선 밖에서 발산 — QP 는 성공하고 로봇은 넘어진다" }
```

## 이 단계 공부법

1. **"정확한 축약"과 "근사"를 구분해 적는다 (30분)** — (1)·(2)는 **정확**하고 (3)은 **근사**다.
   이 구분을 처음에 적어 두지 않으면 나중에 어느 결론이 모델 가정 때문인지 분간할 수 없다.
2. **점 발로 중심 동역학을 검증한다 (60분)** — 재현 과제 조건 1. 토크를 흔들어도 등식이 변하지
   않는 것을 보는 것이 이 레슨의 출발점이다. 구동 발목을 넣으면 깨지는 것도 확인한다.
3. **CoP 식의 부호를 직접 맞춘다 (40분)** — (2)를 유도하고 점 발에서 $p_{\mathrm{zmp}}=0$ 이
   나오는지로 부호를 교정한다. 진단표의 첫 두 줄이 그 실수들이다.
4. **DCM 을 손으로 분해한다 (40분)** — P2. 고유벡터 좌표라는 것을 보면 "왜 $\xi$ 하나만 보면
   되는가"가 식에서 보인다. $1/\omega = 0.2856$ s 라는 숫자를 기억한다.
5. **MPC 를 두 번 돌린다 (90분)** — 종단 제약 없이, 그리고 있게. $39.3$ m 를 직접 본다.
   **비용 함수만 보고 설계를 판단하면 안 된다**는 교훈은 이 숫자로만 남는다.
6. **복구 한계를 측정한다 (60분)** — 조건 3. 이분법으로 $0.1749$ m/s 를 재고 $\omega p_{\max}$ 와
   비교한다. 차이의 원인($\Delta t$, $\epsilon$)을 설명할 수 있어야 통과다.
7. **논문은 "무엇을 변수로 두는가"로 읽는다 (150분)** — Kajita 2003 은 ZMP 를, Di Carlo 2018 은
   접촉력을 변수로 둔다. 그 선택이 제약(단방향·마찰)과 볼록성에 어떤 차이를 만드는지 표로 정리한다.

**통과 기준**: 백지에서 (1)·(2)·(4)를 유도할 수 있고, $p=\xi$ 가 왜 부족한지 말할 수 있고,
재현 과제의 네 조건을 만족하는 코드와 논문 노트가 있다.
