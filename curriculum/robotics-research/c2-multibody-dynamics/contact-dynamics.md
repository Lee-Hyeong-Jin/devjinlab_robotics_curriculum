---
id: c2-contact-dynamics
title: 접촉 동역학과 상보성
summary: >-
  단측(unilateral) 접촉을 상보성 조건으로 세우고, 속도 수준 시간 이산화가 왜 풀리는 문제이고
  가속도 수준은 왜 풀리지 않을 수 있는지를 증명 수준에서 다룬다. 마찰 원뿔과 Painlevé 역설의
  임계 마찰계수를 닫힌 형태로 유도하고($\mu_{\mathrm{crit}} = 4/3$), 접촉 충격량의 에너지
  비증가와 비관통의 차수를 수치로 분해한다.
objectives:
  - 접촉을 위치·속도·가속도 세 수준의 상보성 조건으로 쓰고 왜 등식이 아닌 부등식인지 설명할 수 있다.
  - 무마찰 속도 수준 시간 이산화가 양반정치 LCP 임을 보이고 해의 존재를 증명할 수 있다.
  - 가속도 수준 Coulomb 마찰의 비일관성(Painlevé) 조건을 유도하고 균일 봉의 임계 $\mu$ 를 닫힌 형태로 구할 수 있다.
  - 접촉 충격량이 운동 에너지를 증가시키지 않음을 상보성과 최대 산일에서 증명할 수 있다.
  - 비관통이 1차 조건이고 남는 관통이 $O(h^2)$ 임을 유도하고 수치로 확인할 수 있다.
prerequisites: [c2-constrained-dynamics]
difficulty: 5
estimated_minutes: 600
tags: [multibody-dynamics, contact, complementarity, lcp, friction, painleve, research]
activities:
  - id: c2-contact-dynamics-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 105
  - id: c2-contact-dynamics-papers
    kind: paper
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c2-contact-dynamics-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 2 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 180
  - id: c2-contact-dynamics-reproduction
    kind: reproduction
    title: 재현 과제 — 평면 접촉을 1스텝 LCP 로 적분하고 Painlevé 임계값을 재현 (R2)
    estimated_minutes: 150
  - id: c2-contact-dynamics-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Tedrake, Underactuated Robotics"
    url: https://underactuated.csail.mit.edu/
    kind: book
    note: ch.17 (접촉이 있는 동역학). 상보성·시간 이산화·볼록 완화의 현대적 서술. 전문 무료.
  - title: "Featherstone, Rigid Body Dynamics Algorithms (2008)"
    url: https://doi.org/10.1007/978-0-387-74315-8
    kind: book
    note: ch.11 (Contact and Impact). 강체 접촉의 충격·마찰 모델과 알고리즘.
  - title: "Cottle, Pang & Stone, The Linear Complementarity Problem"
    url: https://doi.org/10.1137/1.9780898719000
    kind: book
    note: 권장. LCP 의 존재·유일성 이론(양반정치·P-행렬·Lemke 알고리즘). R2 의 배경.
  - title: "Boyd & Vandenberghe, Convex Optimization"
    url: https://web.stanford.edu/~boyd/cvxbook/
    kind: book
    note: 권장. ch.4-5. 볼록 완화(R5)와 최대 산일 원리를 QP 로 읽을 때의 배경. 전문 PDF 무료.
papers:
  - id: stewart1996-implicit-timestepping
    role: seminal
    required: true
  - id: anitescu1997-lcp-contact
    role: standard
    required: true
  - id: todorov2014-convex-contact
    role: standard
    required: true
  - id: stewart2000-rigid-body-friction-impact
    role: survey
  - id: genot1999-painleve
    role: standard
---

# 접촉 동역학과 상보성

## 전제와 기호

`c2-constrained-dynamics` 의 결과를 전제한다. 특히 KKT 꼴 (2), Delassus 연산자
$\Lambda^{-1} = JM^{-1}J^\top$, 그리고 **제약력은 제약에 수직**이라는 가상 일의 원리.
이 레슨에서 달라지는 것은 **하나**다: 제약이 등식 $\phi = 0$ 에서 **부등식** $g \ge 0$ 으로
바뀌고, 그 결과 선형계가 **상보성 문제**가 된다.

| 기호 | 뜻 |
|---|---|
| $g(q) \in \mathbb{R}^{n_c}$ | 간격(gap) 함수. $g_i \ge 0$ 이 비관통, $g_i = 0$ 이 접촉 |
| $J_n := \partial g/\partial q$ | 법선 야코비안. $v_n := J_n\dot q$ 가 법선 접근 속도 |
| $J_t$ | 접선 야코비안. 평면에서는 1행, 공간에서는 2행 |
| $\lambda_n \ge 0$, $\lambda_t$ | 법선·접선 **힘**(가속도 수준) |
| $p_n \ge 0$, $p_t$ | 법선·접선 **충격량**(속도 수준). $p = h\lambda$ 가 매끄러운 경우의 관계 |
| $\mu \ge 0$ | Coulomb 마찰계수 |
| $0 \le a \perp b \ge 0$ | 상보성: $a \ge 0$, $b \ge 0$, $a^\top b = 0$ |
| $A := J M^{-1} J^\top$ | Delassus 연산자($J = [J_n; J_t]$). 양반정치 |
| $h$ | 적분 스텝 |
| $v^-, v^+$ | 스텝 시작·끝의 일반화 속도. $v_f := v^- + hM^{-1}(\tau - b)$ 는 **자유 속도** |

전제와 범위: 강체(변형 없음), 점 접촉, 등방 Coulomb 마찰, 반발계수 0(완전 비탄성 — 반발은
문제 P2). 시뮬레이터는 쓰지 않는다 — 모든 수치는 numpy 로 직접 푼다.

**상보성 기호 읽기**: $0 \le p_n \perp v_n^+ \ge 0$ 은 세 조건의 묶음이다. ⓐ 당기는 힘은
없다($p_n \ge 0$) ⓑ 파고들지 않는다($v_n^+ \ge 0$) ⓒ **둘 중 하나는 0 이다**($p_n v_n^+ = 0$:
떨어지고 있으면 힘이 없고, 힘이 있으면 떨어지지 않는다). ⓒ 가 부등식 제약을 **비매끄러운**
문제로 만드는 지점이고, 이 레슨의 모든 어려움이 거기서 나온다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 — `lesson-standard.md` §2).

- **R1 (세 수준의 상보성 조건) [D2]** — 접촉은 위치 수준에서
  $$
  0 \le g(q) \perp \lambda_n \ge 0 \tag{1}
  $$
  이고, $g_i = 0$ 인 활성 접촉에서는 미분해 **속도 수준**
  $0 \le v_n \perp p_n \ge 0$, 다시 미분해 **가속도 수준**
  $0 \le \dot v_n \perp \lambda_n \ge 0$ 을 얻는다. 마찰은 원뿔과 **최대 산일**(maximum
  dissipation)로 쓴다:
  $$
  \lVert \lambda_t\rVert \le \mu\lambda_n, \qquad
  \lambda_t \in \arg\min_{\lVert z\rVert \le \mu\lambda_n} \; v_t^\top z. \tag{2}
  $$
  (2)의 둘째 식이 "미끄러지면 마찰은 미끄럼 반대 방향으로 포화하고, 멈춰 있으면 원뿔
  내부 어디든 가능하다"를 한 줄로 쓴 것이다.
- **R2 (속도 수준 시간 이산화와 해의 존재) [D3]** — 한 스텝을
  $$
  M(v^+ - v_f) = J_n^\top p_n + J_t^\top p_t, \qquad
  0 \le p_n \perp \Big(J_nv^+ + \frac{g}{h}\Big) \ge 0, \qquad (2)\ \text{의 이산판} \tag{3}
  $$
  으로 쓴다. **무마찰**($\mu = 0$)이면 (3)은 행렬 $A_n = J_nM^{-1}J_n^\top \succeq 0$ 인
  **단조(monotone) LCP** 이고, 따라서 **항상 해가 존재한다**. 마찰이 있으면 LCP 행렬이
  비대칭이 되어 가속도 수준에서는 해가 없을 수 있지만(R3), **속도 수준 (3)은 여전히 풀린다** —
  이것이 Anitescu–Potra 1997 의 제목이 말하는 바다.
- **R3 (마찰 원뿔과 Painlevé 역설) [D2]** — 가속도 수준에서 접촉점이 $+t$ 방향으로 미끄러지면
  $\lambda_t = -\mu\lambda_n$ 이고 간격 가속도는
  $$
  \ddot g = \underbrace{\big(J_nM^{-1}J_n^\top - \mu\,J_nM^{-1}J_t^\top\big)}_{=:\,a}\lambda_n
    + \ddot g_{\text{free}} \tag{4}
  $$
  다. $a \le 0$ 이고 $\ddot g_{\text{free}} < 0$ 이면 **$\lambda_n \ge 0$ 으로 $\ddot g \ge 0$ 을
  만들 수 없다** — 해가 존재하지 않는다(Painlevé 역설). 질량 $m$, 길이 $2l$ 의 균일 봉이
  아래쪽 끝으로 미끄러질 때
  $$
  a = \frac{1}{m}\Big[\big(1 + 3\cos^2\theta\big) - 3\mu\,\lvert\sin\theta\rvert\cos\theta\Big],
  \qquad
  \mu_{\mathrm{crit}} = \min_{\theta}\frac{1+3\cos^2\theta}{3\lvert\sin\theta\rvert\cos\theta} = \frac{4}{3} \tag{5}
  $$
  이고 최소는 $\theta = -\arctan 2 \approx -63.4349^\circ$ 에서 달성된다. 즉 **$\mu > 4/3$ 이면
  이 기구는 가속도 수준에서 비일관**이다.
- **R4 (접촉 충격량은 에너지를 증가시키지 않는다) [D2]** — (3)의 해에서
  $$
  \tfrac{1}{2}v^{+\top}Mv^+ - \tfrac{1}{2}v_f^\top M v_f \;=\; -\tfrac{1}{2}\lVert v^+ - v_f\rVert_M^2 + (v^+)^\top\!\big(J_n^\top p_n + J_t^\top p_t\big) \;\le\; 0, \tag{6}
  $$
  왜냐하면 상보성에서 $v_n^{+\top}p_n \le 0$ 이고 최대 산일에서 $v_t^{+\top}p_t \le 0$ 이기
  때문이다. 즉 **접촉은 산일적**이고, 이것이 수치 실험의 1차 점검 항목이다.
- **R5 (비관통의 차수와 볼록 완화) [D2 / 완화의 설계 선택은 D1]** — (3)의 $g/h$ 항은
  $g^{k+1} \ge 0$ 을 **1차로만** 보장한다. $J_n$ 이 상수인 기하(평면 위의 원판)에서는 관통이
  **정확히 0** 이지만, $J_n$ 이 자세에 의존하면 $O(h^2)$ 의 관통이 남는다(측정: 봉 1스텝에서
  $h$ 를 절반으로 줄일 때 관통이 $3.9{-}4.0$ 배로 줄어든다). 한편 (3)의 상보성을 **강볼록
  문제로 완화**하면(MuJoCo 계열) 해가 유일해지고 **$v^+ \mapsto p$ 가 역가능**해져 제어·추정에
  쓸 수 있게 되지만, 그 대가로 정지 마찰에서 작은 비물리적 미끄럼이 생긴다. **[D1]**

## 유도

### R1 — 왜 등식이 아니라 부등식인가

앞 레슨의 제약은 양측(bilateral)이었다: $\phi = 0$ 이고 제약력 $\lambda$ 는 **부호가 자유**
였다(관절은 양방향으로 밀 수 있다). 접촉은 **단측**이다 — 바닥은 밀 수만 있고 당길 수 없다.
이 한 가지 물리적 사실이 세 조건을 낳는다:

1. **비관통** $g(q) \ge 0$.
2. **인장 없음** $\lambda_n \ge 0$ (법선 힘은 밀어내는 방향만).
3. **상보성** $g\,\lambda_n = 0$ — 떨어져 있으면($g > 0$) 힘이 없고, 힘이 있으면($\lambda_n > 0$)
   닿아 있다. 이 조건이 없으면 "공중에 뜬 물체를 바닥이 밀어 올리는" 해가 허용된다.

셋을 묶어 (1)로 쓴다. $g$ 가 이미 0 인 **활성** 접촉에서는 $g$ 를 미분해 수준을 내린다:
$\dot g = J_n\dot q = v_n$ 이고 접촉을 유지하려면 $v_n \ge 0$, 떨어지는 중이면($v_n > 0$)
힘이 0 이어야 하므로 $0 \le v_n \perp \lambda_n \ge 0$. 한 번 더 미분하면 가속도 수준이다.

**수준을 내리는 이유와 대가.** 위치 수준 (1)은 $q$ 에 대한 비선형 상보성 문제(NCP)이고 한
스텝 안에서 풀기 어렵다. 속도 수준은 **$v^+$ 에 대해 선형**이므로 LCP 가 되어 유한 알고리즘
(Lemke)으로 풀린다 — 그래서 실무가 속도 수준을 쓴다. 대가는 $g$ 가 직접 제어되지 않는 것이고,
(3)의 $g/h$ 항이 그 보정이다(앞 레슨 Baumgarte 의 위치 항과 같은 역할, 같은 1차 한계).

**마찰 (2)의 읽기.** 최대 산일 원리는 "마찰은 주어진 원뿔 안에서 산일을 최대로 하는 힘을
고른다"다. $\min_{\lVert z\rVert\le\mu\lambda_n} v_t^\top z$ 의 해는 $v_t \ne 0$ 이면
$z = -\mu\lambda_n\,v_t/\lVert v_t\rVert$ (경계에서 포화, **미끄럼 반대 방향**)이고, $v_t = 0$ 이면
목적함수가 0 이라 **원뿔 전체가 해집합**이다(정지 마찰의 부정성). 이 둘이 각각 **sliding** 과
**sticking** 모드다.

### R2 — 속도 수준 한 스텝과 모드 열거

(3)의 첫 식에서 $v^+ = v_f + M^{-1}(J_n^\top p_n + J_t^\top p_t)$ 이므로, 법선·접선 속도는
충격량의 **아핀** 함수다:

$$
\begin{bmatrix} v_n^+ \\ v_t^+\end{bmatrix}
= \begin{bmatrix} J_nv_f \\ J_tv_f\end{bmatrix}
+ \underbrace{\begin{bmatrix} a_{nn} & a_{nt} \\ a_{tn} & a_{tt}\end{bmatrix}}_{A\,=\,JM^{-1}J^\top}
\begin{bmatrix} p_n \\ p_t\end{bmatrix}. \tag{7}
$$

접촉 하나·평면이면 미지수가 $(p_n, p_t)$ 둘뿐이므로 **모드를 열거**해서 정확히 풀 수 있다.
세 모드가 전부다:

- **분리(separate)**: $p_n = p_t = 0$. $J_nv_f + g/h \ge 0$ 이면 이 모드가 답이다.
- **고착(stick)**: $v_n^+ = -g/h$ 와 $v_t^+ = 0$ 을 연립해 $(p_n, p_t)$ 를 구하고,
  $p_n \ge 0$ 과 $\lvert p_t\rvert \le \mu p_n$ (원뿔 안)을 확인한다.
- **미끄럼(slide, 부호 $s = \pm1$)**: $p_t = -s\,\mu p_n$ 을 가정하고 $v_n^+ = -g/h$ 에서
  $$
  p_n = \frac{-g/h - J_nv_f}{a_{nn} - s\,\mu\,a_{nt}}
  $$
  를 얻은 뒤 $p_n \ge 0$ 과 $\operatorname{sign}(v_t^+) = s$ (가정한 미끄럼 방향과 결과가
  일치)를 확인한다.

열거가 **LCP 를 푸는 것과 같다**는 점이 요점이다 — LCP 의 해는 "어느 상보성 쌍이 어느 쪽으로
활성인가"의 조합을 고르는 문제이고, 접촉 1개·평면이면 그 조합이 3개뿐이다. 접촉이 $n_c$ 개면
조합이 지수적으로 늘어 열거가 불가능해지고, 그래서 Lemke 나 투영 Gauss–Seidel 같은 알고리즘이
필요하다 — 하지만 **무엇을 푸는지는 똑같다**.

> **수치로 본 (7)** (재현 과제의 원판: $m = 1$, $R = 0.2$, $I = \tfrac12 mR^2 = 0.02$):
> $a_{nn} = 1$, $a_{tt} = 3$, $a_{nt} = 0$. 법선과 접선이 **분리**되어 있고(원판의
> 특수성 — 문제 P1 ⓒ), 그래서 $p_n$ 이 $\mu$ 와 무관하다. 봉은 $a_{nt} \ne 0$ 이라
> 결합되어 있고, **그 결합이 Painlevé 의 원인**이다.

### R3 — Painlevé 임계 마찰계수를 닫힌 형태로

균일 봉: 질량 $m$, 길이 $2l$, 중심 $(x, y)$, 각 $\theta$, $q = (x, y, \theta)$,
$M = \operatorname{diag}(m, m, I)$, $I = \tfrac{1}{12}m(2l)^2 = \tfrac{1}{3}ml^2$.
아래쪽 끝 $P = (x - l\cos\theta,\; y - l\sin\theta)$ 가 바닥 $y = 0$ 과 접촉하므로

$$
g = y - l\sin\theta, \qquad
J_n = \big[\,0,\; 1,\; -l\cos\theta\,\big], \qquad
J_t = \big[\,1,\; 0,\; l\sin\theta\,\big].
$$

Delassus 성분을 계산한다. $M^{-1} = \operatorname{diag}(1/m, 1/m, 1/I)$ 이므로

$$
a_{nn} = J_nM^{-1}J_n^\top = \frac{1}{m} + \frac{l^2\cos^2\theta}{I} = \frac{1 + 3\cos^2\theta}{m},
$$
$$
a_{nt} = J_nM^{-1}J_t^\top = \frac{(-l\cos\theta)(l\sin\theta)}{I} = \frac{-3\sin\theta\cos\theta}{m},
$$

여기서 $I = ml^2/3$ 을 넣었다. 접촉점이 $+t$ 로 미끄러진다고 하면 (4)의 계수는

$$
a = a_{nn} - \mu\,a_{nt} = \frac{1}{m}\Big[(1+3\cos^2\theta) + 3\mu\sin\theta\cos\theta\Big].
$$

$a \le 0$ 이 되려면 $\sin\theta\cos\theta < 0$ 이 필요하다 — 즉 봉이 **미끄럼 방향으로 기울어져
있어야** 한다. $\theta \in (-\pi/2, 0)$ ($\sin\theta < 0$, $\cos\theta > 0$)로 두고
$c = \cos\theta$, $\lvert s\rvert = -\sin\theta$ 로 쓰면

$$
a \le 0 \iff \mu \ge \frac{1+3c^2}{3\lvert s\rvert c} =: f(\theta),
$$

즉 (5)다. $f$ 의 최소를 **닫힌 형태로** 구한다. $t := \tan\lvert\theta\rvert > 0$ 로 치환하면
$c^2 = 1/(1+t^2)$, $\lvert s\rvert c = t/(1+t^2)$ 이므로

$$
f = \frac{1 + 3/(1+t^2)}{3t/(1+t^2)} = \frac{(1+t^2) + 3}{3t} = \frac{t^2 + 4}{3t},
\qquad
\frac{df}{dt} = \frac{3t^2 - 12}{9t^2} = 0 \iff t = 2.
$$

$t = 2$ 에서 $f = (4+4)/6 = 4/3$ 이고, 이것이 $t > 0$ 에서 유일한 임계점이며 $f \to \infty$
($t \to 0^+, \infty$)이므로 최소다. 따라서

$$
\mu_{\mathrm{crit}} = \frac{4}{3}, \qquad \theta^{*} = -\arctan 2 = -63.434948823^\circ.
$$

**가정이 깨지는 곳 — 무엇이 역설인가.** 역설은 "물리가 모순"이 아니라 **모델이 모순**이라는
것이다. 강체 + Coulomb + 가속도 수준 세 가정을 동시에 두면 해집합이 빌 수 있다. 셋 중 하나를
풀면 해결된다: ⓐ 강체를 풀면(유연 접촉) 해가 존재한다 ⓑ 가속도 수준을 풀면(충격량·속도 수준)
해가 존재한다 — **R2 가 그 길**이다 ⓒ Coulomb 을 풀면(규제된 마찰) 해가 존재한다.
실무는 거의 항상 ⓑ 를 택하고, 그때 Painlevé 상황은 **충격적 고착**으로 해소된다
(측정: $\theta^{*}$, $\mu = 2$ 에서 가속도 수준은 $\lambda_n = -12.2625 < 0$ 으로 비일관이지만
속도 수준 한 스텝은 $p_n = 0.3083$, $p_t = -0.4029$ 의 **stick** 해를 준다).

### R4 — 에너지 비증가

$\Delta v := v^+ - v_f = M^{-1}(J_n^\top p_n + J_t^\top p_t)$ 로 두고 운동 에너지 차를 쓴다:

$$
\tfrac12 v^{+\top}Mv^+ - \tfrac12 v_f^\top Mv_f
= \tfrac12(v^+ + v_f)^\top M\,\Delta v
= (v^+)^\top M\Delta v - \tfrac12\Delta v^\top M\Delta v,
$$

(중간 등호는 $v_f = v^+ - \Delta v$ 를 넣어 전개). $M\Delta v = J_n^\top p_n + J_t^\top p_t$ 이므로

$$
\tfrac12 v^{+\top}Mv^+ - \tfrac12 v_f^\top Mv_f
= \underbrace{v_n^{+\top}p_n}_{\le\,0} + \underbrace{v_t^{+\top}p_t}_{\le\,0}
  - \underbrace{\tfrac12\lVert\Delta v\rVert_M^2}_{\ge\,0} \;\le\; 0,
$$

즉 (6)이다. 세 항의 부호를 각각 확인한다:

- $v_n^{+\top}p_n$: 상보성 $0 \le p_n \perp (v_n^+ + g/h) \ge 0$ 에서
  $p_n^\top(v_n^+ + g/h) = 0$ 이므로 $v_n^{+\top}p_n = -p_n^\top g/h \le 0$
  ($p_n \ge 0$, $g \ge 0$). **접촉이 이미 성립해 $g = 0$ 이면 정확히 0** 이다.
- $v_t^{+\top}p_t$: 최대 산일 (2)에서 $p_t$ 가 $v_t^{+\top}z$ 를 원뿔 안에서 최소화하고
  $z = 0$ 이 가능하므로 $v_t^{+\top}p_t \le 0$.
- 마지막 항은 $M \succ 0$ 에서 음이 아니다 — **충격량 자체의 산일**이고, 완전 비탄성 충돌에서
  잃는 에너지가 바로 이 항이다.

> **수치로 본 (6)**: 접촉 상태의 원판에 무작위 전속도 $5\times10^4$ 개와
> $\mu \sim U(0,1)$ 을 넣어 충격량이 실제로 발생한 $25{,}031$ 스텝에서 운동 에너지 변화의
> **최대값이 $-3.02\times10^{-6}$** 이다(즉 전부 엄격히 음수). 분리 스텝에서는 정확히 0 이다.

### R5 — 비관통의 차수, 그리고 볼록 완화

(3)의 상보성은 $v_n^+ + g/h \ge 0$ 을 요구하므로, 접촉이 활성일 때 $v_n^+ = -g/h$ 가 되어
$g^{k+1} \approx g + h v_n^+ = 0$ 이다 — **1차로** 비관통이 성립한다. 2차 항이 남는 이유는
$J_n$ 이 $q$ 에 의존하기 때문이다: $g^{k+1} = g + hJ_n v^+ + \tfrac{h^2}{2}\dot J_nv^+ + O(h^3)$.

따라서 $J_n$ 이 **상수**인 기하(평면 바닥 위의 원판 — 법선이 자세에 무관)에서는 관통이
정확히 0 이고, $J_n$ 이 자세에 의존하는 기하(봉)에서는 $O(h^2)$ 의 관통이 남는다. 측정값:

| 기하 | $h$ | 1스텝 후 간격 | 비 |
|---|---|---|---|
| 봉, $\mu=2$, $\theta^{*}$ | $4\times10^{-3}$ | $-6.1842\times10^{-6}$ | — |
| 봉 | $2\times10^{-3}$ | $-1.5778\times10^{-6}$ | $3.92$ |
| 봉 | $1\times10^{-3}$ | $-3.9846\times10^{-7}$ | $3.96$ |
| 봉 | $5\times10^{-4}$ | $-1.0012\times10^{-7}$ | $3.98$ |
| 봉 | $2.5\times10^{-4}$ | $-2.5093\times10^{-8}$ | $3.99$ |
| 원판, $\mu=0.3$, 2초 | $10^{-3}$ … $2.5\times10^{-4}$ | $0$ (정확히) | — |

비가 4 로 수렴하므로 관통은 정확히 $O(h^2)$ 다. 실무 처방은 앞 레슨과 같다: 엄격한 비관통이
필요하면 스텝 끝에서 **투영**한다.

**볼록 완화 (Todorov 2014 계열).** (3)은 상보성 때문에 ⓐ 해가 유일하지 않을 수 있고
ⓑ $p \mapsto v^+$ 가 비매끄러워 **미분이 정의되지 않거나 역사상이 없다**. 완화는 접촉 문제를
강볼록 QP 로 바꾼다 — 개략적으로

$$
p = \arg\min_{p\,\in\,\mathcal{K}} \; \tfrac12 p^\top A p + p^\top Jv_f + \tfrac12 p^\top R p,
$$

$\mathcal{K}$ 는 (선형화 또는 원뿔) 마찰 집합이고 $R \succ 0$ 은 정규화다. 얻는 것:
**유일한 해**, **$C^1$ 의존성**(궤적 최적화와 미분 가능 시뮬레이션에 필수), 그리고
$v^+ \mapsto p$ 의 **역가능성**(해석적으로 역산 가능 — 논문 제목의 "analytically-invertible").
잃는 것: $R \ne 0$ 이므로 정지 마찰에서 작은 **비물리적 미끄럼**(boundary-layer)이 생기고,
$R$ 의 크기가 모델 오차와 수치 안정성의 교환을 직접 결정한다. **[D1]**

## 증명 스케치

### R2 — 무마찰 속도 수준 LCP 는 항상 풀린다

**가설** H1: $M \succ 0$. H2: $\mu = 0$ (무마찰). H3: $g \ge 0$ (스텝 시작에서 관통이 없다).
**결론** C1: (3)은 $A_n = J_nM^{-1}J_n^\top \succeq 0$ 인 LCP 이고 **해가 존재한다**.
C2: $J_n$ 이 행 완전계수면 $v_n^+$ 는 유일하고, 계수 결손이면 $p_n$ 이 유일하지 않을 수 있다.
C3: 마찰을 넣으면 어느 가설이 어떻게 깨지는가.

**전략**: 문제를 표준형 LCP 로 정리하고, 양반정치 LCP 의 가해성(Cottle–Pang–Stone)을 쓴다.
그 가해성 자체는 등가인 **볼록 QP** 의 해 존재로 보는 것이 가장 짧다.

1. **표준형으로.** H2 로 $p_t = 0$ 이므로 (7)의 법선 블록만 남는다:
   $$
   w := v_n^+ + \frac{g}{h} = A_np_n + \underbrace{\Big(J_nv_f + \frac{g}{h}\Big)}_{=:\,c},
   \qquad 0 \le p_n \perp w \ge 0.
   $$
   이것이 $\mathrm{LCP}(A_n, c)$ 다.
2. **$A_n \succeq 0$.** $M^{-1} \succ 0$ 의 합동 변환이므로 $x^\top A_nx = \lVert J_n^\top x\rVert^2_{M^{-1}} \ge 0$.
   ($J_n$ 이 계수 결손이면 등호가 가능하므로 **양정치는 아니다** — 접촉이 중복될 때가 그 경우다.)
3. **등가 볼록 QP.** $A_n \succeq 0$ 이면 $\mathrm{LCP}(A_n, c)$ 의 해는
   $$
   \min_{p_n \ge 0} \; \tfrac12 p_n^\top A_n p_n + c^\top p_n
   $$
   의 KKT 점과 **정확히 일치**한다(KKT 조건을 쓰면 $A_np_n + c \ge 0$, $p_n \ge 0$,
   $p_n^\top(A_np_n+c) = 0$). 목적함수가 볼록이고 가능 집합 $\{p_n \ge 0\}$ 이 비지 않았으므로,
   **하방 유계이면** 최소점이 존재한다.
4. **하방 유계임.** $A_n \succeq 0$ 이므로 목적함수가 아래로 무계인 유일한 길은
   $A_nd = 0$, $c^\top d < 0$, $d \ge 0$ 인 방향 $d$ 가 있는 경우다. 그러나 $A_nd = 0$ 은
   2단계에서 $J_n^\top d = 0$ 을 뜻하고, 그러면
   $c^\top d = d^\top J_nv_f + d^\top g/h = (J_n^\top d)^\top v_f + d^\top g/h = d^\top g/h \ge 0$
   (H3 과 $d \ge 0$). 모순이므로 하방 유계다. 따라서 해가 존재한다 — C1.
5. **유일성 (C2).** $v_n^+$ 와 $v^+$ 는 QP 의 목적함수가 $J_n^\top p_n$ 을 통해서만 $p_n$ 에
   의존하므로 **유일**하다. 반면 $J_n$ 이 계수 결손이면 $J_n^\top p_n$ 을 같게 유지하는
   $p_n$ 이 여러 개 있어 **충격량 분배가 유일하지 않다** — 앞 레슨 R1 의 과잉 구속과 같은
   현상이고, 네 다리 보행 로봇의 발 4개가 바로 이 경우다.
6. **C3 — 마찰을 넣으면.** 마찰이 있으면 법선·접선이 (7)로 결합되고, 미끄럼 모드에서
   유효 행렬이 $a_{nn} - s\mu a_{nt}$ 로 **비대칭**이 된다. 비대칭 행렬은 양반정치일 필요가
   없고, 실제로 (5)에서 $\mu > 4/3$ 이면 음수가 되어 3단계의 볼록성이 깨진다. **가속도 수준**
   에서는 그래서 해가 없을 수 있다(R3). **속도 수준** (3)에서는 미끄럼 모드가 비가해이면
   **고착 모드**가 남아 있고, 고착 모드의 행렬은 $A$ 의 주부분행렬이라 양반정치이므로
   해가 존재한다 — 이 구조가 Anitescu–Potra 1997 의 가해성 증명의 뼈대다.
   (생략: 다접촉·다면체 원뿔에서의 일반 증명은 Anitescu & Potra 1997 의 가해성 정리.
   그 논문은 선형화된(다면체) 원뿔을 써서 문제를 LCP 로 유지한다 — **원뿔을 선형화하는 것이
   가해성을 사는 값**이다.)

**가설을 지우면**: H3($g \ge 0$)을 지우면 4단계가 깨진다 — 이미 파고든 상태($g < 0$)에서는
$c^\top d < 0$ 이 가능해 LCP 가 비가해일 수 있다. 그래서 구현은 스텝 시작에서 관통을
허용하지 않거나 $g$ 를 $\max(g, 0)$ 으로 잘라야 한다(진단표). H1($M \succ 0$)을 지우면
2단계의 합동 논증이 양반정치만 주고 3단계의 하방 유계성이 깨진다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1·R2)** ⓐ 최대 산일 원리 (2)에서 미끄럼·고착 두 경우의 해집합을 명시적으로
구하라. ⓑ 공간(3D) 접촉에서 $J_t$ 가 2행이 되고 원뿔이 $\lVert\lambda_t\rVert_2 \le \mu\lambda_n$
가 될 때, 이 원뿔을 **다면체로 선형화**하면 몇 개의 모드가 생기는지 세라(면 $k$ 개).
ⓒ 재현 과제의 원판에서 $a_{nt} = 0$ 인 **기하적 이유**를 쓰고, 그 결과 $p_n$ 이 $\mu$ 와
무관해지는 것을 보이라. 어떤 기하에서 $a_{nt} \ne 0$ 이 되는가?
*해답 스케치*: ⓐ 는 선형 목적함수를 공 위에서 최소화하는 문제다. ⓒ 는 원판의 법선 야코비안이
$\theta$ 에 무관하고($J_n = [0,1,0]$) 접선 야코비안의 $\theta$ 성분만 $R$ 을 갖기 때문이다 —
질량행렬이 대각이라 두 블록이 섞이지 않는다. 봉은 $J_n$ 에 $\theta$ 성분이 있어 섞인다.

**P2 (유도, ★★, R1·R4)** ⓐ 반발계수 $e \in [0,1]$ 을 넣으려면 (3)의 상보성을 어떻게 고쳐야
하는지 쓰고(Newton 식 반발), $e = 1$ 에서 (6)의 부등식이 **등식**이 되는지 확인하라.
ⓑ (6)의 세 항 중 어느 것이 완전 비탄성 충돌의 에너지 손실인지 지목하고, 1자유도 공이
속도 $v$ 로 바닥에 닿을 때 그 값을 구하라. ⓒ 접촉이 이미 성립해 $g = 0$ 이면
$v_n^{+\top}p_n$ 이 정확히 0 인 것을 보이고, $g > 0$ 인데 접촉이 활성화되는 스텝에서는
그 항이 **음수**인 것의 물리적 의미를 쓰라.
*해답 스케치*: ⓐ 는 $v_n^+ \ge -e\,v_n^-$ 로 바꾼다. ⓑ 는 $\tfrac12\lVert\Delta v\rVert_M^2$
항이고 1자유도에서 $\tfrac12 mv^2$ 전부다. ⓒ 의 음수는 "스텝 안에서 간격을 소비하며 멈춘다"는
뜻이고, 이 항이 $g/h$ 보정이 에너지를 **빼앗는** 통로다.

**P3 (증명, ★★★, R2)** ⓐ 양반정치 LCP 와 볼록 QP 의 동치(증명 스케치 3단계)를 KKT 조건으로
완전히 증명하라. ⓑ $J_n$ 이 계수 결손일 때 $v^+$ 는 유일하지만 $p_n$ 은 유일하지 않음을
증명하고, 네 다리 보행 로봇의 발 4개가 평면에 닿은 경우로 구체화하라. ⓒ 증명 스케치 4단계의
하방 유계성 논증이 $g < 0$ (초기 관통)에서 깨지는 구체적 반례를 만들라.
*전략 + 핵심 부등식*: ⓐ 는 $\min_{p\ge0} \frac12p^\top Ap + c^\top p$ 의 KKT 를
$Ap + c - s = 0$, $s \ge 0$, $p \ge 0$, $p^\top s = 0$ 로 쓰고 $s = w$ 로 읽는다.
ⓒ 는 $J_n^\top d = 0$ 이면서 $d^\top g < 0$ 인 $d \ge 0$ 을 만들면 된다. 전개는 숨긴다.

**P4 (증명, ★★★, R3)** ⓐ (5)의 $f(\theta) = (t^2+4)/(3t)$ 치환을 빠진 줄 없이 다시 유도하고,
$t = 2$ 가 **유일한** 임계점임을 보이라. ⓑ 길이가 아니라 **관성 분포**를 바꾸면
($I = \kappa ml^2$, $\kappa > 0$) $\mu_{\mathrm{crit}}$ 이 $\kappa$ 의 함수로 어떻게
변하는지 구하고, $\kappa \to 0$ 과 $\kappa \to \infty$ 의 극한을 해석하라.
ⓒ Painlevé 상황에서 **해가 여러 개**인 경우(비유일성)도 존재한다. 그 경우를 (4)에서
어떤 부호 조합이 만드는지 쓰라.
*전략 + 핵심 부등식*: ⓑ 는 $a_{nn} = 1/m + l^2c^2/I$, $a_{nt} = -l^2sc/I$ 에 $I = \kappa ml^2$
를 넣어 $f_\kappa(\theta) = \frac{\kappa + c^2}{\lvert s\rvert c}$ 를 얻고 같은 치환을 쓴다
($t = \sqrt{\kappa+1}$ 에서 최소, $\mu_{\mathrm{crit}} = 2\sqrt{\kappa+1}\cdot$상수 꼴).
$\kappa = 1/3$ 을 넣어 $4/3$ 이 복원되는지 **반드시** 확인하라. 전개는 숨긴다.

**P5 (계산, ★, R2·R4)** 평면 위의 균일 원판: $m = 1$, $R = 0.2$, $I = \tfrac12 mR^2 = 0.02$,
$q = (x, y, \theta)$, 간격 $g = y - R$, $J_n = [0,1,0]$, $J_t = [1,0,R]$,
중력 $g_0 = 9.81$ (일반화 힘 $-b$, $b = (0, mg_0, 0)$). 접촉 상태 $q = (0, 0.2, 0)$,
$v^- = (1.5, -0.5, -2.0)$, $h = 10^{-3}$ 에서 $\mu \in \{0,\ 0.3,\ 1.0\}$ 각각에 대해
모드, $p_n$, $p_t$, $v^+$, 그리고 충격량에 의한 운동 에너지 변화를 구하라.
*정답* (허용오차 $10^{-9}$). 세 경우 모두 $p_n = 0.50981$ ($a_{nt} = 0$ 이므로 $\mu$ 무관):

| $\mu$ | 모드 | $p_t$ | $v^+$ | $\Delta E_k$ |
|---|---|---|---|---|
| $0$ | slide$+$ | $0$ | $(1.5,\; 0,\; -2)$ | $-0.129953118050$ |
| $0.3$ | slide$+$ | $-0.152943$ | $(1.347057,\; 0,\; -3.52943)$ | $-0.263103076177$ |
| $1.0$ | stick | $-0.366666666667$ | $(1.133333333333,\; 0,\; -5.666666666667)$ | $-0.331619784717$ |

*검산*: ⓐ $a_{nn} = 1$, $a_{tt} = 3$, $a_{nt} = 0$ ⓑ 자유 속도 $v_f = (1.5, -0.50981, -2)$ 가
$\mu$ 와 무관 ⓒ 세 경우 모두 $v_n^+ = 0$ (허용오차 $10^{-15}$) ⓓ $\mu = 1$ 에서 $v_t^+ = 0$
이고 $\lvert p_t\rvert = 0.3667 \le \mu p_n = 0.5098$ (원뿔 안) ⓔ $\mu = 0.3$ 에서
$v_t^+ = 0.641171 > 0$ 이므로 가정한 미끄럼 방향과 일치 ⓕ $\Delta E_k$ 가 $\mu$ 에 대해
단조 감소.

**P6 (구현, ★★, R2·R4·R5)** 모드 열거 1스텝 해법 `step(q, v, h, mu)` 를 쓰라
(아래 재현 과제의 핵심 코드가 뼈대다). 평면 1접촉, 반발 0.
*루브릭*: ⓐ P5 의 세 수치를 $10^{-9}$ 이내로 재현 ⓑ 세 모드를 모두 **도달**하는 테스트가
있다(분리·고착·미끄럼) ⓒ 어느 모드도 일관되지 않으면 **조용히 틀린 답을 내지 말고 예외**를
던진다 ⓓ 가정한 미끄럼 방향과 결과 $\operatorname{sign}(v_t^+)$ 의 일치를 실제로 검사한다
ⓔ 스텝 시작에서 $g < 0$ 이면 경고하거나 $\max(g, 0)$ 으로 자른다(증명 스케치의 H3)
ⓕ $\mu = 0$ 에서 결과가 스칼라 LCP 의 닫힌 해와 일치한다.

**P7 (반례, ★★, R3·R5)** ⓐ $\theta^{*} = -\arctan 2$, $\mu = 2$ 의 봉에서 가속도 수준 해가
없음을 **수치로** 보이라($\lambda_n \ge 0$ 으로 $\ddot g \ge 0$ 이 불가능함을 보이면 된다).
ⓑ 같은 상태에서 속도 수준 1스텝이 **풀리는** 것을 보이고 어느 모드로 해소되는지 쓰라.
ⓒ 같은 상태에서 $\mu$ 를 $5$ 로 올려도 속도 수준이 풀리는지 확인하고, 그 사실이 R2 의
C3 6단계와 어떻게 맞는지 한 문단으로 쓰라.
*성질 체크리스트*: ⓐ 는 $a < 0$ 와 $\ddot g_{\text{free}} < 0$ 두 부호를 모두 확인해야 한다
($\ddot g_{\text{free}} = -9.81$). ⓑ 의 답은 **stick** 이고, ⓒ 에서 $\mu$ 를 올려도 같은
고착 해가 나오는 이유는 고착 모드의 행렬이 $A$ 의 주부분행렬이라 $\mu$ 에 의존하지 않기
때문이다 — $\mu$ 는 원뿔 **검사**에만 쓰인다.

## 논문 읽기

**필독 3편** (권장 2편). 1996·1997·2014 — 같은 문제를 **적분기**, **가해성**, **볼록성**
세 방향에서 공격한 논문들이다. 세 편을 읽고 "강체 접촉의 어느 가정을 각자 포기했는가"를
한 단락으로 정리하는 것이 이 레슨의 읽기 목표다(답은 R3 의 ⓐⓑⓒ 와 R5 에 있다).
각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다(`lesson-standard.md` §5).
3-pass 로 읽고 3번째 패스에서 질문 4·7·8 을 집중 공략한다.

1. **Stewart & Trinkle, "An implicit time-stepping scheme for rigid body dynamics with
   inelastic collisions and Coulomb friction" (1996, Int. J. Numer. Methods Eng.)** — 역할:
   `원전(seminal)`.
   <https://doi.org/10.1002/(SICI)1097-0207(19960815)39:15<2673::AID-NME972>3.0.CO;2-I>
   어느 절을 왜 읽는가: 시간 이산화를 세우고 그 LCP 의 가해성을 논하는 절. 이 레슨 (3)의
   원형이고, **왜 음함수(implicit)여야 하는지**가 핵심이다.
   추가 질문: ⓐ 저자들이 "음함수"로 얻는 것은 정확히 무엇인가(안정성? 가해성? 둘 다?)
   ⓑ 저자들의 수렴 주장은 어떤 극한($h \to 0$)에서 **무엇으로의** 수렴인가?
   ⓒ Painlevé 상황이 이 스킴에서 어떻게 나타나는가 — 사라지는가, 다른 해로 바뀌는가?
2. **Anitescu & Potra, "Formulating dynamic multi-rigid-body contact problems with friction as
   solvable linear complementarity problems" (1997, Nonlinear Dynamics)** — 역할:
   `표준(standard)`. <https://doi.org/10.1023/A:1008292328909>
   어느 절을 왜 읽는가: 제목이 주장인 논문이다 — **가해성**을 증명하는 절. 이 레슨 증명
   스케치의 6단계가 그 뼈대이고, 저자들이 **무엇을 희생해** 가해성을 사는지(원뿔 선형화,
   속도 수준)가 읽기의 초점이다.
   추가 질문: ⓐ 저자들의 가해성 정리가 요구하는 가정을 전부 나열하고, 이 레슨의 H1·H2·H3 과
   대조하라. ⓑ 원뿔을 다면체로 선형화하면 물리적으로 무엇이 틀리는가(등방성? 크기?)
   ⓒ 저자들이 **유일성**도 주장하는가?
3. **Todorov, "Convex and analytically-invertible dynamics with contacts and constraints:
   theory and implementation in MuJoCo" (2014, ICRA)** — 역할: `표준(standard)`.
   <https://doi.org/10.1109/ICRA.2014.6907751>
   어느 절을 왜 읽는가: 상보성을 강볼록 문제로 바꾸는 절과 역가능성을 논하는 절.
   R5 가 그 요약이고, **무엇을 포기해 미분가능성·유일성을 사는지**가 핵심이다.
   추가 질문: ⓐ 저자가 말하는 "analytically invertible" 의 정확한 뜻과, 그것이 제어·추정에서
   왜 필요한가? ⓑ 완화가 만드는 모델 오차를 저자가 어떻게 정량화하는가 — 상한이 있는가?
   ⓒ 이 완화로 Painlevé 상황이 어떻게 처리되는가?

**권장 2편** (필독 아님): **Stewart, "Rigid-Body Dynamics with Friction and Impact"
(2000, SIAM Review)** <https://doi.org/10.1137/S0036144599360110> — 이 분야의 서베이이고
Painlevé·존재·유일성의 수학적 지형을 한 번에 본다. **Génot & Brogliato, "New results on
Painlevé paradoxes" (1999, Eur. J. Mech. A/Solids)**
<https://doi.org/10.1016/S0997-7538(99)00144-8> — R3 의 분류를 더 깊게.

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, 3분 이내, numpy 만.
메모리 200MB 이내. 시뮬레이터는 쓰지 않는다.

**핵심 코드 — 모드 열거 1스텝 해법.** 아래는 본문의 모든 수치가 나온 코드의 핵심부다.
접촉 1개·평면이므로 LCP 를 **정확히** 풀 수 있고, 그래서 수용 기준이 기계 정밀도로 쓰인다.

```python
G0 = 9.81
M_D, R_D = 1.0, 0.2
I_D = 0.5 * M_D * R_D**2  # uniform disk
MASS = np.diag([M_D, M_D, I_D])
MINV = np.linalg.inv(MASS)
JN = np.array([0.0, 1.0, 0.0])  # d(gap)/dq with gap = y - R
JT = np.array([1.0, 0.0, R_D])  # tangential contact-point velocity: xdot + R thetadot
B = np.array([0.0, M_D * G0, 0.0])  # gravity enters the equation of motion as -B


def step(q, v, h, mu, tau=np.zeros(3)):
    """One velocity-level step, solved exactly by enumerating the three contact modes."""
    g = max(q[1] - R_D, 0.0)  # H3 of the proof sketch: no initial penetration
    vf = v + h * MINV @ (tau - B)  # free velocity
    an, at, ant = JN @ MINV @ JN, JT @ MINV @ JT, JN @ MINV @ JT
    if JN @ vf + g / h >= 0.0:  # mode 1: separating
        return q + h * vf, vf, 0.0, 0.0, "separate", vf
    A = np.array([[an, ant], [ant, at]])  # mode 2: sticking
    pn, pt = np.linalg.solve(A, np.array([-g / h - JN @ vf, -JT @ vf]))
    if pn >= 0.0 and abs(pt) <= mu * pn + 1e-14:
        vp = vf + MINV @ (JN * pn + JT * pt)
        return q + h * vp, vp, pn, pt, "stick", vf
    for s in (+1.0, -1.0):  # mode 3: sliding, pt = -s mu pn
        den = an - s * mu * ant
        if den <= 0.0:
            continue  # the Painleve case: this mode is inconsistent
        pn = (-g / h - JN @ vf) / den
        if pn < 0.0:
            continue
        pt = -s * mu * pn
        vp = vf + MINV @ (JN * pn + JT * pt)
        if abs(JT @ vp) < 1e-12 or np.sign(JT @ vp) == s:
            return q + h * vp, vp, pn, pt, f"slide{int(s):+d}", vf
    raise RuntimeError("no consistent contact mode: the LCP is infeasible")


def painleve_coeff(theta, mu, m=1.0, ell=0.5):
    """Coefficient of lambda_n in the gap acceleration (4), for a rod sliding in +t."""
    inertia = m * (2 * ell) ** 2 / 12
    minv = np.diag([1 / m, 1 / m, 1 / inertia])
    c, s = np.cos(theta), np.sin(theta)
    jn = np.array([0.0, 1.0, -ell * c])  # gap = y - ell sin(theta)
    jt = np.array([1.0, 0.0, ell * s])  # x of the contact point
    return jn @ minv @ jn - mu * (jn @ minv @ jt)
```

`step` 의 반환은 $(q^{k+1}, v^+, p_n, p_t, \text{mode}, v_f)$ 다. $v_f$ 를 함께 돌려주는 것이
조건 2 에 필요하다 — 에너지 비교의 기준이 $v^-$ 가 아니라 **자유 속도 $v_f$** 이기 때문이다
(중력이 한 일을 접촉의 산일로 착각하지 않으려면).

아래 **네 조건을 모두** 만족해야 통과다.

1. **적분: 비관통과 모드 도달** — 원판을 $q = (0, 0.5, 0)$, $v = (1.5, 0, -2)$ 에서 떨어뜨려
   $2$ 초 적분한다. $h \in \{10^{-3}, 10^{-4}\}$, $\mu \in \{0,\ 0.3\}$ 네 조합 전부에서
   $$
   \min_k \; g(q^k) \;\ge\; 0 \quad\text{(허용오차 } 0\text{, 즉 정확히 음수가 없어야 한다)},
   $$
   그리고 $\mu = 0$ 에서는 `separate`·`slide+1`, $\mu = 0.3$ 에서는 거기에 `stick` 까지
   **세 모드가 모두** 나타나야 한다.
   > 측정값: 네 조합 모두 $\min g = 0$ (정확히). 원판은 $J_n$ 이 상수여서 관통이 0 이다 —
   > 조건 4 가 그 이유를 확인한다.
2. **에너지 비증가** — 접촉 상태 $q = (0, R, 0)$ 에서 무작위 $v^- \sim 2\,\mathcal{N}(0, I_3)$
   와 $\mu \sim U(0,1)$ 을 $5\times10^4$ 개 뽑아 1스텝씩 돌린다. **충격량이 실제로 발생한
   스텝**($p_n > 0$)에서
   $$
   \max\Big(\tfrac12 v^{+\top}Mv^+ - \tfrac12 v_f^\top Mv_f\Big) \;<\; 0
   $$
   이어야 한다(엄격히 음수). 분리 스텝($p_n = 0$)에서는 그 값이 **정확히 0** 임을 따로 확인한다.
   > 측정값: 충격량 스텝 $25{,}031/50{,}000$, 그중 최대값 $-3.022041\times10^{-6}$.
   > 시드는 `np.random.default_rng(0)` 로 고정한다.
3. **Painlevé 임계값과 가속도/속도 수준의 대비** — ⓐ $f(\theta) = \frac{1+3\cos^2\theta}{3\lvert\sin\theta\rvert\cos\theta}$
   를 $\theta \in (-\pi/2, 0)$ 에서 최소화해
   $$
   \lvert \mu_{\mathrm{crit}} - 4/3\rvert < 10^{-9}, \qquad
   \lvert \theta^{*} + \arctan 2\rvert < 10^{-5}
   $$
   를 보이라(격자 $2\times10^6$ 점이면 충분하다. 측정값: $1.333333333333$,
   $-63.434946528^\circ$ vs 닫힌 해 $-63.434948823^\circ$).
   ⓑ `painleve_coeff` 가 $\mu = 4/3 \mp 10^{-9}$ 에서 부호를 바꾸는 것을 확인하라
   (측정값 $\pm1.2\times10^{-9}$).
   ⓒ $\theta^{*}$, 접촉점이 $+x$ 로 $1\,\mathrm{m/s}$ 미끄러지는 상태에서 **가속도 수준**을
   풀어, $\mu = 1$ 에서는 $\lambda_n = +24.525$ 로 가해이고 $\mu = 2$ 에서는
   $\lambda_n = -12.2625 < 0$ 으로 **비가해**임을 보이라($\ddot g_{\text{free}} = -9.81$).
   ⓓ 같은 상태에서 **속도 수준** 1스텝($h = 10^{-3}$)이 $\mu \in \{1, 2, 5\}$ 에서 모두
   풀리는 것을 보이고, $\mu \in \{2, 5\}$ 에서 모드가 `stick` 이며
   $p_n = 0.3083385$, $p_t = -0.402943$ 임을 확인하라(두 $\mu$ 에서 **같은 값** — 고착 모드는
   $\mu$ 에 의존하지 않고 $\mu$ 는 원뿔 검사에만 쓰인다).
4. **비관통의 차수** — 봉을 $\theta^{*}$, $\mu = 2$, $g = 0$, 접촉점 $+x$ 미끄럼 상태에서
   **1스텝만** 돌리고 $h \in \{4, 2, 1, 0.5, 0.25\}\times10^{-3}$ 로 스윕해, 스텝 후 간격의
   크기가 $h$ 를 절반으로 할 때마다 $3.8 \sim 4.2$ 배로 줄어드는 것(즉 $O(h^2)$)을 보이라.
   > 측정값: $-6.1842\times10^{-6}$, $-1.5778\times10^{-6}$, $-3.9846\times10^{-7}$,
   > $-1.0012\times10^{-7}$, $-2.5093\times10^{-8}$ (비 $3.92,\ 3.96,\ 3.98,\ 3.99$).
   이어서 원판(같은 스윕)에서 관통이 **정확히 0** 임을 보이고, 두 결과의 차이가
   $J_n$ 의 자세 의존성 때문임을 한 줄로 쓰라.

**입력 데이터**: 외부 데이터 불필요. 모델 상수는 P5 와 위 코드에 전부 있다. 난수는
`np.random.default_rng(0)` 로 고정한다.

**비교 대상** (최소 1개):
- 1순위: $\mu = 0$ 에서 스칼라 LCP 의 **닫힌 해**($p_n = \max(0, -(g/h + J_nv_f)/a_{nn})$)와
  모드 열거 결과가 일치($10^{-15}$ 이내).
- 2순위: 조건 3 ⓐ 의 격자 최소화와 ⓑ 의 닫힌 해 $4/3$ — 서로 독립인 두 경로.
- 선택 검증(없어도 통과): 일반 LCP 해법(Lemke 또는 투영 Gauss–Seidel)을 직접 구현해
  모드 열거와 같은 답을 내는지 대조. 접촉이 2개 이상이면 열거가 불가능해지므로 이쪽이
  본격적인 길이다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 관통이 $O(h)$ 로 줄어든다 | 상보성의 $g/h$ 항을 빼먹었다 | $g > 0$ 에서 접촉이 활성화되는 스텝의 $v_n^+$ 를 출력해 $-g/h$ 인지 본다 |
| 에너지가 증가한다 | 기준을 $v^-$ 로 잡았다(중력이 한 일이 섞였다) | 비교 기준을 자유 속도 $v_f$ 로 바꾼다 — (6)의 좌변이 그것이다 |
| 에너지가 증가한다(기준은 맞다) | 미끄럼 모드에서 $p_t$ 의 **부호**가 미끄럼 방향과 같다 | $v_t^{+}p_t \le 0$ 을 단위 테스트로 검사한다 |
| 고착 모드가 원뿔을 벗어난다 | $\lvert p_t\rvert \le \mu p_n$ 검사를 생략했다 | $\mu$ 를 0 으로 두고 고착 모드가 절대 선택되지 않는지 본다 |
| 미끄럼 모드가 진동한다(스텝마다 $s$ 가 뒤집힌다) | 결과 $\operatorname{sign}(v_t^+)$ 와 가정의 일치를 검사하지 않았다 | 두 부호를 모두 시도하고 일관된 쪽만 받아들인다 |
| `nan` 또는 거대한 $p_n$ | 미끄럼 모드 분모 $a_{nn} - s\mu a_{nt}$ 가 0 에 가깝다(Painlevé 근방) | 분모를 출력하고 $\le 0$ 이면 그 모드를 **건너뛴다**(코드의 `continue`) |
| 조건 3 ⓒ 에서 $\lambda_n$ 이 양수로 나온다 | (4)의 부호 — 미끄럼이 $+t$ 면 $\lambda_t = -\mu\lambda_n$ 이다 | $\mu = 0$ 에서 $\lambda_n = 9.81/a_{nn}$ 인지 확인해 부호를 교정한다 |
| 초기 관통 상태에서 LCP 가 풀리지 않는다 | 증명 스케치 H3 위반 | $g$ 를 $\max(g, 0)$ 으로 자르거나 스텝 전에 투영한다 |

## 열린 문제

- **(열린 문제) 접촉 동역학의 미분가능성과 학습에 쓰는 기울기의 정당성** — 상보성 해는
  접촉 모드가 바뀌는 지점에서 **비매끄럽고**, 그 지점에서 자동 미분이 내놓는 값은
  한쪽 방향 도함수이거나 아무 의미가 없다. 볼록 완화(R5)는 매끄러움을 사지만 그 기울기는
  **완화된 모델**의 기울기이고, 원래 문제의 기울기와 얼마나 다른지에 대한 상한이 없다.
  정책 학습과 궤적 최적화가 이 기울기에 전적으로 의존하므로 실질적 문제다. 현재 접근:
  볼록 완화와 해석적 미분([Todorov 2014](https://doi.org/10.1109/ICRA.2014.6907751)),
  무작위 평활화(randomized smoothing). 비어 있는 자리: 완화 기울기와 참 기울기의 오차 한계.
- **(열린 문제) 실제 마찰·변형의 모델 오차 한계** — Coulomb 원뿔은 등방·속도 무관·면적
  무관을 가정하지만 실제 마찰은 셋 다 아니다(Stribeck, 접촉 면적 의존, 예압 이력).
  Painlevé 가 보여 주듯 모델 가정이 모순을 만들 수도 있는데, 어떤 접촉 모델이 주어진
  실험 데이터와 **얼마나 틀릴 수 있는지**에 대한 보증은 없다. 조작(manipulation)의
  sim-to-real 격차가 거의 전부 여기서 온다. 현재 접근: 데이터로 접촉 매개변수를 식별,
  잔차 학습, 분포 강건 제어. 비어 있는 자리: 모델 클래스에 대한 최악 경우 오차 한계.
  Painlevé 의 수학적 지형은 [Stewart 2000](https://doi.org/10.1137/S0036144599360110) 과
  [Génot & Brogliato 1999](https://doi.org/10.1016/S0997-7538(99)00144-8) 가 정리한다.
- **(열린 문제) 접촉 수에 대한 비용 하한** — 앞 레슨의 열린 문제와 같은 벽이다. 접촉이
  $n_c$ 개면 LCP 의 크기가 $O(n_c)$ 이고 Delassus 를 만드는 비용이 $O(n\,n_c + n_c^2)$,
  푸는 비용이 최악 경우 지수적이다(피벗 알고리즘). "접촉 수에 대해 다항식이고 정확한"
  해법이 존재하는지가 열려 있고, 실무는 반복 해법으로 **정확성을 포기**한다.
  현재 접근: 투영 Gauss–Seidel·ADMM 류 1차 해법, 볼록 완화.
  비어 있는 자리: $n_c$ 에 대한 하한, 그리고 반복 해법의 오차가 궤적 수준에서 어떻게
  누적되는지에 대한 분석.

## 개념 점검

`rc quiz c2-contact-dynamics` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c2-contact-dynamics-quiz
questions:
  - id: q1
    type: multiple
    prompt: "법선 접촉의 상보성 $0 \\le g \\perp \\lambda_n \\ge 0$ 이 묶고 있는 물리적 조건을 모두 고르라."
    choices:
      - "비관통: 물체가 바닥을 파고들지 않는다"
      - "인장 없음: 바닥은 밀 수만 있고 당길 수 없다"
      - "떨어져 있으면 법선 힘이 0 이다"
      - "마찰이 미끄럼 반대 방향으로 작용한다"
    answer: [0, 1, 2]
    explanation: "세 조건이 각각 $g \\ge 0$, $\\lambda_n \\ge 0$, $g\\lambda_n = 0$ 이다. 셋째 조건이 없으면 공중에 뜬 물체를 바닥이 밀어 올리는 해가 허용된다. 마찰 방향은 별도의 조건(최대 산일 원리)이고 법선 상보성과 무관하다."
    concept: { front: "법선 상보성이 묶는 세 조건", back: "비관통 $g \\ge 0$ · 인장 없음 $\\lambda_n \\ge 0$ · 상보성 $g\\lambda_n = 0$" }
  - id: q2
    type: single
    prompt: "무마찰 속도 수준 시간 이산화가 **항상** 해를 갖는 근거는?"
    choices:
      - "LCP 행렬 $J_nM^{-1}J_n^{\\top}$ 이 양정치이기 때문"
      - "LCP 행렬이 양반정치이고 초기 관통이 없어 등가 볼록 QP 가 하방 유계이기 때문"
      - "접촉이 1개뿐이기 때문"
      - "Coulomb 원뿔을 다면체로 선형화했기 때문"
    answer: 1
    explanation: "$A_n = J_nM^{-1}J_n^{\\top}$ 은 $M^{-1} \\succ 0$ 의 합동이라 양반정치이고($J_n$ 이 계수 결손이면 양정치가 아니다), 양반정치 LCP 는 $\\min_{p\\ge0}\\frac12 p^{\\top}A_np + c^{\\top}p$ 의 KKT 점과 같다. $A_nd = 0 \\Rightarrow J_n^{\\top}d = 0$ 이고 그러면 $c^{\\top}d = d^{\\top}g/h \\ge 0$ 이므로($g \\ge 0$) 하방 유계다. 초기 관통이 있으면 이 논증이 깨진다."
    concept: { front: "무마찰 접촉 LCP 의 가해성", back: "$A_n \\succeq 0$ + $g \\ge 0$ → 등가 볼록 QP 가 하방 유계 → 해 존재. $p_n$ 은 유일하지 않을 수 있다" }
  - id: q3
    type: short
    prompt: "균일 봉(아래쪽 끝 미끄럼)의 Painlevé 임계 마찰계수 $\\mu_{\\mathrm{crit}}$ 는? (분수로)"
    answer: ["4/3", "4 / 3", "1.3333", "1.333333", "4÷3", "1.33333333"]
    explanation: "$a = \\frac{1}{m}[(1+3\\cos^2\\theta) - 3\\mu|\\sin\\theta|\\cos\\theta]$ 이고 $a \\le 0$ 조건은 $\\mu \\ge (1+3c^2)/(3|s|c)$ 다. $t = \\tan|\\theta|$ 로 치환하면 우변이 $(t^2+4)/(3t)$ 이고 $t = 2$ 에서 최소 $4/3$ 이다. 즉 $\\theta = -\\arctan 2 \\approx -63.43^{\\circ}$ 에서 $\\mu > 4/3$ 이면 가속도 수준에 해가 없다."
    concept: { front: "균일 봉의 Painlevé 임계 $\\mu$", back: "$4/3$, $\\theta = -\\arctan 2 \\approx -63.43^{\\circ}$ 에서. $(t^2+4)/(3t)$ 의 최소($t = \\tan|\\theta| = 2$)" }
  - id: q4
    type: truefalse
    prompt: "Painlevé 역설은 강체 접촉의 물리가 모순이라는 것을 뜻한다."
    answer: false
    explanation: "모순인 것은 물리가 아니라 **모델**이다. 강체 + Coulomb + 가속도 수준 세 가정을 동시에 두면 해집합이 빌 수 있다. 셋 중 하나를 풀면 해결된다: 유연 접촉, 속도 수준(충격량) 정식화, 또는 규제된 마찰. 실무는 거의 항상 속도 수준을 택하고, 그러면 Painlevé 상황은 충격적 고착으로 해소된다 — 측정에서 $\\mu = 2$ 의 봉이 $p_n = 0.3083$ 의 stick 해를 받는다."
    concept: { front: "Painlevé 역설의 정체", back: "모델의 모순(강체 + Coulomb + 가속도 수준). 속도 수준으로 내려가면 충격적 고착으로 해소된다" }
  - id: q5
    type: single
    prompt: "속도 수준 이산화에서 $g/h$ 항을 빼면 무엇이 달라지는가?"
    choices:
      - "에너지가 증가할 수 있다"
      - "비관통이 1차에서 깨지고 관통이 $O(h)$ 로 누적된다"
      - "마찰 원뿔이 깨진다"
      - "아무것도 달라지지 않는다 — $g/h$ 는 편의 항이다"
    answer: 1
    explanation: "$g/h$ 항이 상보성을 $v_n^+ \\ge -g/h$ 로 만들어 $g^{k+1} \\approx g + hv_n^+ \\ge 0$ 을 1차로 보장한다. 빼면 $v_n^+ \\ge 0$ 만 남아 이미 생긴 관통이 회복되지 않고 누적된다. 앞 레슨 Baumgarte 의 위치 항과 같은 역할이고 같은 1차 한계를 갖는다 — $J_n$ 이 자세에 의존하면 $O(h^2)$ 의 관통은 남는다."
    concept: { front: "$g/h$ 항의 역할", back: "비관통을 1차로 보장(Baumgarte 의 위치 항과 같은 역할). 남는 관통은 $O(h^2)$, $J_n$ 상수면 정확히 0" }
```

## 이 단계 공부법

1. **부등식 하나가 바꾸는 것을 먼저 적는다 (20분)** — 앞 레슨의 $\phi = 0$ 과 이 레슨의
   $g \ge 0$ 을 나란히 쓰고, 그 차이가 선형계를 상보성 문제로 바꾸는 경로를 한 문단으로
   써라. 이 레슨의 모든 어려움이 그 한 줄에서 나온다.
2. **모드 세 개를 손으로 분류한다 (40분)** — (7)을 적고 분리·고착·미끄럼 각각에서 어느
   미지수가 0 이고 어느 등식이 활성인지 표로 만들어라. **열거가 LCP 를 푸는 것이다**를
   손으로 확인하면 Lemke 를 몰라도 이 레슨을 끝낼 수 있다.
3. **Painlevé 를 닫힌 형태로 끝까지 계산한다 (60분)** — R3 의 Delassus 성분 두 개를 직접
   계산하고 $t = \tan\lvert\theta\rvert$ 치환으로 $4/3$ 까지 간다. 그 다음 **격자 최소화로
   교차 확인**하라(재현 과제 조건 3 ⓐ). 닫힌 해와 수치가 $10^{-9}$ 에서 만나는 경험이
   이 레슨의 중심이다.
4. **에너지 기준을 $v_f$ 로 잡는 이유를 손으로 본다 (30분)** — (6)의 좌변이 $v^-$ 가 아니라
   $v_f$ 와의 차인 것을 유도에서 확인하고, $v^-$ 로 잡으면 중력이 한 일이 섞여 "에너지가
   증가한다"는 잘못된 결론이 나오는 것을 수치로 직접 만들어 보라. 진단표의 두 번째 줄이다.
5. **먼저 틀리게 구현한다 (60분)** — P6 을 쓸 때 ⓐ $g/h$ 생략 ⓑ 원뿔 검사 생략
   ⓒ 미끄럼 방향 일관성 검사 생략 세 버전을 만들어 재현 과제의 어느 조건이 깨지는지 적어라.
   ⓒ 는 특히 **스텝마다 부호가 뒤집히는 진동**으로 나타나는데, 그 증상을 한 번 보면
   LCP 해법이 왜 "조합을 고르는 문제"인지 몸으로 안다.
6. **재현 과제를 끝낸다 (150분)** — 조건 3 이 이 레슨의 핵심이다. ⓒ 와 ⓓ 를 나란히 놓고
   "같은 상태, 같은 $\mu$, 가속도 수준은 비가해인데 속도 수준은 풀린다"를 자기 숫자로
   확인하라. 그 한 번의 실험이 Anitescu–Potra 의 제목 전체를 설명한다.
7. **논문 3편을 "무엇을 포기했는가"로 읽는다 (150분)** — Stewart–Trinkle(음함수),
   Anitescu–Potra(원뿔 선형화 + 속도 수준), Todorov(볼록 완화) 순서가 좋다. 각 논문마다
   "이 저자가 강체 접촉의 어느 가정을 포기해 무엇을 얻었는가"를 한 줄로 쓰고, 세 줄을
   모아 한 단락으로 합쳐라. 그 단락이 다음 레슨(미분과 식별)의 도입부가 된다.
8. **무엇을 못 하는지로 끝낸다 (25분)** — 열린 문제 중 미분가능성 쪽을 골라, 완화된 모델의
   기울기를 참 기울기로 쓰는 것이 왜 정당화되지 않는지 한 문단으로 쓴다. 이 질문이
   `c2-dynamics-derivatives-sysid` 와 `s2-조작·접촉` 에서 다시 나온다.

**통과 기준**: 백지에서 (1)(2)(3)(4)(6)을 쓸 수 있고, R2 의 가해성 증명 네 단계와 R3 의
$4/3$ 유도를 말할 수 있고, 재현 과제 네 조건을 통과하는 모드 열거 해법을 갖고 있고,
논문 3편의 1페이지 노트가 있다.
