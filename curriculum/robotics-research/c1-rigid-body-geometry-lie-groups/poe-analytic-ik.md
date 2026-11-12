---
id: c1-poe-analytic-ik
title: Product of exponentials 와 해석적 역기구학
summary: >-
  나선 축의 지수 곱(product of exponentials)으로 정기구학을 쓰고, Paden–Kahan 부문제로 역기구학을
  기하 문제로 분해해 닫힌 해를 얻는다. 일반 6R 의 해 개수와 분기 구조, 그리고 수치 해법으로
  넘어가야 하는 경계까지 다룬다.
objectives:
  - 나선 축으로 PoE 정기구학을 세우고 공간 형식과 물체 형식을 서로 변환할 수 있다.
  - Paden–Kahan 부문제 1 의 해 조건과 닫힌 해를 처음부터 유도할 수 있다.
  - 부문제 2·3 의 전략을 기하적으로 설명하고 해의 개수를 셀 수 있다.
  - 6R 매니퓰레이터의 역기구학 해 분기를 나열하고 왜 최대 16개인지 출처와 함께 말할 수 있다.
  - 해석적 해가 존재하지 않는 구조에서 수치 해법으로 넘어가는 판단 근거를 댈 수 있다.
prerequisites: [c1-lie-group-derivatives]
difficulty: 5
estimated_minutes: 450
tags: [lie-groups, kinematics, product-of-exponentials, inverse-kinematics, research]
activities:
  - id: c1-poe-analytic-ik-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 80
  - id: c1-poe-analytic-ik-papers
    kind: paper
    title: 필독 논문 2편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 100
  - id: c1-poe-analytic-ik-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 140
  - id: c1-poe-analytic-ik-reproduction
    kind: reproduction
    title: 재현 과제 — 6R 해석적 IK 와 정기구학 왕복 (R2)
    estimated_minutes: 110
  - id: c1-poe-analytic-ik-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Murray, Li & Sastry, A Mathematical Introduction to Robotic Manipulation"
    kind: book
    note: ch.3 (Manipulator Kinematics). PoE 와 Paden-Kahan 부문제의 표준 서술. (공식 URL 미확인)
  - title: "Lynch & Park, Modern Robotics"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: ch.4 (Forward Kinematics), ch.6 (Inverse Kinematics). 공간·물체 형식과 수치 IK.
  - title: "Modern Robotics 코드 라이브러리"
    url: https://github.com/NxRLab/ModernRobotics
    kind: code
    note: PoE 정기구학·수치 IK 참조 구현(Python). 재현 과제의 비교 대상으로 쓴다.
papers:
  - id: brockett1984-poe
    required: true
    role: seminal
  - id: husty2007-6r-ik
    required: true
    role: standard
---

# Product of exponentials 와 해석적 역기구학

## 전제와 기호

앞 세 레슨의 표기를 쓴다. 추가 기호:

| 기호 | 뜻 |
|---|---|
| $\mathcal{S}_i = (\omega_i, v_i)$ | $i$ 번째 관절의 나선 축. **영 자세(zero configuration)** 에서 본 값 |
| $M \in SE(3)$ | $\theta = 0$ 일 때의 말단 자세(end-effector home pose) |
| $T(\theta)$ | 관절각 $\theta \in \mathbb{R}^n$ 에서의 말단 자세 |
| $\mathcal{B}_i$ | 물체 프레임에서 본 나선 축 |
| $p, r \in \mathbb{R}^3$ | 부문제에서 옮겨야 하는 점과 목표점 |
| $q_i$ | 축 $i$ 위의 한 점 |

**규약**: 회전 관절은 $\mathcal{S} = (\omega, -\omega \times q)$($\lVert\omega\rVert=1$), 직동 관절은
$\mathcal{S} = (0, v)$($\lVert v\rVert=1$)다. 앞 레슨의 나선 분해(R3)에서 피치 $h=0$ 인 경우와
$\omega=0$ 인 경우에 각각 해당한다.

**왜 DH 를 쓰지 않는가**: DH 파라미터는 프레임 배치 규약에 자유도가 있어 같은 로봇에 여러 표가
나오고, 표를 잘못 읽으면 조용히 틀린다. 나선 축은 **기하 그 자체**(축의 방향과 위치)이므로
규약 선택이 없다. 이것이 Brockett 1984(필독 1)가 가져온 관점이다.

## 핵심 결과

- **R1 (PoE 정기구학) [D2]** — 공간 형식(space form)

$$
T(\theta) = \mathrm{Exp}(\mathcal{S}_1\theta_1)\,\mathrm{Exp}(\mathcal{S}_2\theta_2)\cdots
\mathrm{Exp}(\mathcal{S}_n\theta_n)\,M, \tag{1}
$$

  물체 형식(body form) $T(\theta) = M\,\mathrm{Exp}(\mathcal{B}_1\theta_1)\cdots\mathrm{Exp}(\mathcal{B}_n\theta_n)$
  이고 둘은 $\mathcal{B}_i = \mathrm{Ad}_{M^{-1}}\mathcal{S}_i$ 로 이어진다.
- **R2 (Paden–Kahan 부문제 1) [D3]** — 축 $(\omega, q)$ 에 대한 회전으로 점 $p$ 를 $r$ 로 옮기는
  문제는 **풀릴 조건**

$$
\omega^\top(p - q) = \omega^\top(r - q), \qquad \lVert u'\rVert = \lVert v'\rVert \tag{2}
$$

  ($u = p-q$, $v = r-q$, $u' = u - \omega\omega^\top u$, $v' = v - \omega\omega^\top v$)
  아래에서 **유일한** 해

$$
\theta = \operatorname{atan2}\big(\omega^\top(u' \times v'),\; u'^\top v'\big) \tag{3}
$$

  를 갖는다. $u' = 0$ 이면 $p$ 가 축 위에 있어 $\theta$ 가 **임의**다(퇴화).
- **R3 (부문제 2·3) [D2]** — 부문제 2(교차하는 두 축으로 점 옮기기)는 일반적으로 **0, 1 또는 2개**,
  부문제 3(회전으로 주어진 거리 $\delta$ 만들기)은 **0, 1 또는 2개**의 해를 갖는다. 둘 다
  부문제 1 로 환원되며, 해의 개수는 **평면 원의 교차 개수**로 결정된다.
- **R4 (6R 의 해 개수) [D0]** — 일반 6R 매니퓰레이터의 역기구학은 최대 **16개**의 해를 가지며,
  이는 16차 다항식으로 환원된다. 이 결과는 유도하지 않고 인용한다 — 대수기하의 결과이고,
  현대적 알고리즘과 함께 Husty et al. 2007(필독 2)에 정리되어 있다.
- **R5 (해석적 해가 있는 구조) [D1]** — Paden–Kahan 으로 닫힌 해가 나오는 것은 **축이 교차하거나
  평행한 특수 구조**(예: 구형 손목 + 3축 팔)일 때다. 일반 구조에서는 수치 해법
  (`c1-manifold-optimization` 의 매니폴드 Newton/Gauss–Newton)으로 간다.

## 유도

### R1 — PoE 정기구학과 두 형식의 관계

**공간 형식의 뜻**: $\mathrm{Exp}(\mathcal{S}_i\theta_i)$ 는 "기준 프레임에서 본 나선 축
$\mathcal{S}_i$ 를 $\theta_i$ 만큼 돌리는 강체 운동"이다. 관절 $n$ 부터 거꾸로 생각하면,
$\theta_n$ 을 움직일 때 말단은 축 $\mathcal{S}_n$ 에 대한 나선 운동을 하고, 그 결과를
$\theta_{n-1}$ 의 운동이 다시 옮긴다. 이 중첩이 (1)의 **왼쪽 곱**이다.

중요한 점은 $\mathcal{S}_i$ 가 **영 자세에서 본 고정값**이라는 것이다. $\theta_1$ 이 움직이면
실제 축 2 의 위치는 바뀌지만, (1)은 그 변화를 왼쪽 인자가 흡수하므로 축을 다시 계산하지 않는다.
이것이 DH 표 대신 축 목록만으로 기구학을 쓸 수 있는 이유다.

**두 형식의 관계**: (1)에 $M M^{-1}$ 을 끼워 넣어 각 인자를 $M$ 뒤로 옮긴다. 앞 레슨 R1(수반 표현)에서

$$
M^{-1}\mathrm{Exp}(\mathcal{S}\theta)M = \mathrm{Exp}\big(\mathrm{Ad}_{M^{-1}}\mathcal{S}\,\theta\big)
$$

이므로($\mathrm{Exp}$ 안의 공액이 수반 표현이 된다 — 지수의 급수에 공액을 항별로 적용하면 바로 나온다),

$$
T(\theta) = M\,\mathrm{Exp}(\mathrm{Ad}_{M^{-1}}\mathcal{S}_1\,\theta_1)\cdots
\mathrm{Exp}(\mathrm{Ad}_{M^{-1}}\mathcal{S}_n\,\theta_n),
$$

즉 $\mathcal{B}_i = \mathrm{Ad}_{M^{-1}}\mathcal{S}_i$ 다.

**가정이 깨지는 곳**: (1)은 **직렬 사슬**(serial chain)에만 성립한다. 폐루프가 있으면 관절각이
독립이 아니어서 $T$ 가 $\theta$ 의 함수로 정의되지 않는다 — 제약 방정식을 함께 풀어야 하고,
그것이 `c2-constrained-dynamics` 의 주제다.

## 증명 스케치

### R2 — Paden–Kahan 부문제 1

**가설** H1: 축은 단위 $\omega$ 와 그 위의 점 $q$ 로 주어진다(회전 관절, 피치 0).
H2: 점 $p$ 를 $r$ 로 옮기는 회전 $\mathrm{Exp}(\mathcal{S}\theta)$ 를 찾는다.
**결론** C: (2)가 성립할 때, 그리고 그때만 해가 있고, $u' \ne 0$ 이면 해는 (3)으로 유일하다.

**전략**: 축 방향 성분과 수직 성분으로 분해한다. 회전은 축 방향 성분을 **보존**하고 수직 성분의
**길이도 보존**하므로, 남는 자유도는 수직 평면에서의 각 하나뿐이다.

1. **축 원점으로 평행이동.** $u := p - q$, $v := r - q$ 로 두면 문제는 "원점을 지나는 축 $\omega$
   에 대한 회전으로 $u$ 를 $v$ 로 보내라"가 된다($q$ 가 축 위의 점이므로 회전의 고정점이다).
2. **분해.** $u = \omega(\omega^\top u) + u'$, $v = \omega(\omega^\top v) + v'$ 로 축 성분과 수직
   성분을 나눈다. $R = \mathrm{Exp}(\omega\theta)$ 는 $\omega$ 를 고정하므로
   $R u = \omega(\omega^\top u) + Ru'$ 이고 $Ru' \perp \omega$, $\lVert Ru'\rVert = \lVert u'\rVert$.
3. **필요조건.** $Ru = v$ 이려면 축 성분이 같아야 하고($\omega^\top u = \omega^\top v$) 수직 성분의
   길이가 같아야 한다($\lVert u'\rVert = \lVert v'\rVert$). 이것이 (2)다.
4. **충분조건과 유일성.** (2)가 성립하고 $u' \ne 0$ 이면, $u'$ 와 $v'$ 는 $\omega$ 에 수직인 같은
   평면 위의 같은 길이 벡터이므로 그 평면의 회전 하나가 정확히 $u'$ 를 $v'$ 로 보낸다. 그 각은
   사잇각이고, 부호는 $\omega$ 를 법선으로 한 방향으로 정해진다 — $\cos\theta \propto u'^\top v'$,
   $\sin\theta \propto \omega^\top(u'\times v')$ 이므로 (3)이다. 평면 회전이 유일하므로 해도 유일하다.
5. **퇴화.** $u' = 0$ 이면 $p$ 가 축 위에 있어 어떤 $\theta$ 에서도 움직이지 않는다. (2)의 첫 조건만
   만족하면 모든 $\theta$ 가 해이고, 만족하지 않으면 해가 없다.

**왜 atan2 인가**: $\arccos(u'^\top v'/\lVert u'\rVert^2)$ 로 쓰면 **부호를 잃는다**($[0,\pi]$ 만
나온다). 또 $u' \parallel v'$ 근방에서 $\arccos$ 의 미분이 발산해 수치적으로 나쁘다. 두 성분을
모두 쓰는 `atan2` 는 전구간 $(-\pi,\pi]$ 를 주고 조건수도 낫다. 앞 레슨의 로그 사상에서
$\theta=\pi$ 가 어려웠던 것과 같은 종류의 교훈이다.

**가설을 지우면**: 피치가 0 이 아닌 나선 관절(H1 위반)에서는 축 방향 성분이 **보존되지 않는다**
($\theta$ 에 비례해 미끄러진다). 3단계의 첫 조건이 $\omega^\top(v-u) = h\theta$ 로 바뀌어 $\theta$ 가
양변에 나타나고, 문제는 더 이상 "평면에서 각 하나 찾기"가 아니다.

### R3 — 부문제 2·3 의 전략과 해 개수

- **부문제 2** (교차하는 두 축 $\omega_1, \omega_2$, 교점 $q$): $\mathrm{Exp}(\mathcal{S}_1\theta_1)
  \mathrm{Exp}(\mathcal{S}_2\theta_2)p = r$. 두 회전이 모두 $q$ 를 고정하므로 $\lVert p-q\rVert =
  \lVert r-q\rVert$ 가 필요하다. 전략: 중간점 $c := \mathrm{Exp}(\mathcal{S}_2\theta_2)p$ 가
  ⓐ 축 2 에 대해 $p$ 와 같은 원뿔 위에 있고 ⓑ 축 1 에 대해 $r$ 과 같은 원뿔 위에 있어야 한다.
  두 원뿔(= 두 평면 위의 원)의 교점이 $c$ 의 후보이고, **원 두 개의 교차이므로 0·1·2개**다.
  각 $c$ 마다 부문제 1 을 두 번 적용해 $(\theta_1,\theta_2)$ 를 얻는다.
- **부문제 3** (회전으로 거리 맞추기): $\lVert \mathrm{Exp}(\mathcal{S}\theta)p - r\rVert = \delta$.
  축 성분을 빼서 평면 문제로 만들면 "반지름 $\lVert u'\rVert$ 인 원 위의 점이 고정점에서 거리
  $\delta'$ 가 되는 각"이고, 코사인 법칙으로

$$
\theta = \theta_0 \mp \phi, \quad
\cos\phi = \frac{\lVert u'\rVert^2 + \lVert v'\rVert^2 - \delta'^2}{2\lVert u'\rVert\,\lVert v'\rVert},
\quad \delta'^2 = \delta^2 - \big(\omega^\top(p-r)\big)^2, \tag{4}
$$

  여기서 $\theta_0$ 은 (3)의 각이다. $\lvert\cos\phi\rvert > 1$ 이면 해가 없고, $=1$ 이면 하나,
  $<1$ 이면 둘이다 — **접하는 경우가 해 개수가 바뀌는 분기점**이고 수치적으로 가장 위험한 자리다.

## 문제 세트

★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** $M^{-1}\mathrm{Exp}(\mathcal{S}\theta)M =
\mathrm{Exp}(\mathrm{Ad}_{M^{-1}}\mathcal{S}\,\theta)$ 를 지수의 급수에서 직접 보이고, 이로부터
$\mathcal{B}_i = \mathrm{Ad}_{M^{-1}}\mathcal{S}_i$ 를 유도하라.
*해답 스케치*: $M^{-1}(\hat{\mathcal{S}}\theta)^k M = (M^{-1}\hat{\mathcal{S}}\theta M)^k$ 이고
$M^{-1}\hat{\mathcal{S}}M = \widehat{\mathrm{Ad}_{M^{-1}}\mathcal{S}}$(앞 레슨 R1)이므로 급수를
항별로 옮길 수 있다.

**P2 (유도, ★★, R3)** (4)를 코사인 법칙에서 유도하라. 특히 $\delta'^2$ 가 왜 축 방향 성분을 뺀
값인지, 그리고 $\delta'^2 < 0$ 이면 무엇을 뜻하는지 쓰라.
*해답 스케치*: 회전은 축 방향 거리를 바꾸지 못하므로 그 성분은 상수다 — 평면에서 맞춰야 하는
거리는 피타고라스로 분리된 $\delta'$ 다. $\delta'^2<0$ 이면 축 방향 성분만으로 이미 $\delta$ 를
넘으므로 해가 없다.

**P3 (증명, ★★★, R2)** 부문제 1 의 해가 $u'\ne0$ 일 때 유일함을 증명하라. "평면 회전이
유일하다"를 가정하지 말고, $Ru'=v'$ 를 만족하는 $R = \mathrm{Exp}(\omega\theta)$ 가 두 개 있다고
가정해 모순을 끌어내라.
*해답 스케치*: $\theta_1,\theta_2$ 가 모두 해면 $\mathrm{Exp}(\omega(\theta_1-\theta_2))$ 가 $v'$ 를
고정한다. $v' \ne 0$ 이고 $v' \perp \omega$ 이므로 그 회전은 항등이어야 하고(축에 수직인 0 아닌
벡터를 고정하는 회전은 항등뿐이다 — 앞 레슨 R2 의 2단계), 따라서 $\theta_1 \equiv \theta_2
\pmod{2\pi}$.

**P4 (계산, ★, R2)** 축 $\omega = (0,0,1)$, $q = 0$, $p = (1,0,2)$, $r = (0,1,2)$ 일 때 부문제 1 의
해를 구하라. 해가 존재하는지 (2)로 먼저 확인하라.
*정답*: $\omega^\top u = \omega^\top v = 2$ ✓, $u' = (1,0,0)$, $v' = (0,1,0)$, 길이 모두 1 ✓.
$u'^\top v' = 0$, $\omega^\top(u'\times v') = \omega^\top(0,0,1) = 1$ 이므로
$\theta = \operatorname{atan2}(1,0) = \pi/2 \approx 1.5707963$. 허용오차 $10^{-9}$.

**P5 (구현, ★★, R2·R3)** `subproblem1(omega, q, p, r)`, `subproblem3(omega, q, p, r, delta)` 를 쓰라.
해 없음·퇴화·복수 해를 **예외가 아니라 반환값으로** 구분해야 한다.
*루브릭*: ⓐ (2)를 허용오차와 함께 검사하고 위반 시 "해 없음"을 반환 ⓑ $u'=0$ 퇴화를 별도 표식으로
반환 ⓒ 부문제 3 이 $\lvert\cos\phi\rvert$ 를 $1$ 로 클리핑하기 전에 **허용오차 밖인지 먼저 검사**
(접점 근방에서 조용히 해를 만들어 내지 않도록) ⓓ 모든 반환 해가 원 방정식을 $10^{-9}$ 이내로 만족.

**P6 (반례, ★★, R4·R5)** Paden–Kahan 으로 닫힌 해를 얻을 수 없는 6R 구조를 하나 구성하고, 왜
부문제로 분해되지 않는지 축의 기하로 설명하라. 그 구조에서 해의 개수는 어떻게 알 수 있는가?
*성질 체크리스트*: 부문제는 "한 점이 축 위에서 불변"이라는 성질을 쓴다 — 축이 서로 교차하지도
평행하지도 않으면 그런 불변점이 없다. 일반 6R(틀어진 축)이 그 예이고, 해 개수는 R4 의 대수적
결과(최대 16)와 수치 대수(Husty 2007)로만 알 수 있다.

## 논문 읽기

**필독 2편.** 고정 질문 10개(레슨 표준 §5)로 논문당 1페이지 노트를 쓴다.

1. **Brockett, "Robotic manipulators and the product of exponentials formula" (1984, LNCIS)** —
   역할: `원전(seminal)`. <https://doi.org/10.1007/BFb0031048>
   추가 질문: ⓐ 이 논문이 DH 표 대비 **무엇을 없앴는가**(규약 선택? 계산량? 미분 가능성?)
   ⓑ 저자의 관점이 왜 리 군 언어를 요구하는가 — 같은 공식을 선형대수만으로 쓸 수 있는가?
2. **Husty, Pfurner & Schröcker, "A new and efficient algorithm for the inverse kinematics of a
   general serial 6R manipulator" (2007, Mechanism and Machine Theory)** — 역할: `표준(standard)`.
   <https://doi.org/10.1016/j.mechmachtheory.2006.02.001>
   추가 질문: ⓐ 16개 해라는 상한이 어디서 오는지 이 논문의 서술로 요약하라.
   ⓑ 저자들이 보고하는 수치적 어려움은 무엇이고, 그것이 이 레슨의 퇴화 사례(접점·축 위의 점)와
   어떻게 이어지는가? ⓒ 해석적 해법과 수치 해법의 경계를 저자들은 어디에 두는가?

## 재현 과제

**티어 R2 (알고리즘 재구현).** 예산: 노트북 CPU 10분 이내, numpy 만.

**대상**: 구형 손목을 가진 6R 팔(예: 축 1–3 이 팔, 축 4–6 이 한 점에서 교차하는 손목). 영 자세의
나선 축 $\mathcal{S}_1..\mathcal{S}_6$ 과 $M$ 을 레슨이 제공하는 스크립트로 생성한다.

1. **정기구학 검증**: (1)로 구현한 $T(\theta)$ 가 Modern Robotics 참조 구현(`FKinSpace`)과
   무작위 $\theta$ 1000개에서 $\lVert T - T_{\text{ref}}\rVert_F < 10^{-12}$.
2. **두 형식 일치**: 같은 $\theta$ 에서 공간 형식과 물체 형식의 결과가 $10^{-12}$ 이내로 일치
   ($\mathcal{B}_i = \mathrm{Ad}_{M^{-1}}\mathcal{S}_i$ 를 실제로 계산해서).
3. **해석적 IK 왕복**: 작업 공간 안의 무작위 목표 $10^4$ 개에 대해 Paden–Kahan 분해로 모든 해를
   구하고, **반환된 모든 해**가 $\lVert T(\theta_{\text{sol}}) - T_{\text{goal}}\rVert_F < 10^{-9}$
   를 만족. 해를 하나도 못 찾은 비율이 1% 미만(작업 공간 밖 표본 제외).
4. **분기 개수**: 같은 $10^4$ 표본에서 해 개수의 분포를 히스토그램으로 보고하라. 구형 손목 6R 은
   일반적으로 **8개**(팔 2 × 손목 2 × 어깨/엘보 2)가 나와야 하고, 특이 구성 근방에서 개수가
   줄어드는 것을 확인하라. 개수가 8 을 넘으면 중복 해를 제거하지 않은 것이다.

**비교 대상**: Modern Robotics 의 수치 IK(`IKinSpace`)를 같은 목표에 적용해 ⓐ 해석적 해 중 하나로
수렴하는지 ⓑ 반복 횟수와 실패율을 비교하라. 수치 해법은 초기값에 따라 **한 해만** 준다는 점이
핵심 관찰이다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 정기구학은 맞고 IK 만 틀리다 | 부문제 적용 순서(손목 먼저 vs 팔 먼저) | 손목 교점을 목표에서 역산한 중간 목표로 각 단계를 따로 검증 |
| 해 개수가 8 을 넘는다 | 중복 해를 걸러내지 않았다 | 관절각을 $(-\pi,\pi]$ 로 정규화한 뒤 중복 제거 |
| 특이 구성에서 `nan` | (3)의 $u'=0$ 또는 (4)의 $\cos\phi$ 클리핑 | 퇴화 검사를 클리핑보다 **먼저** 하는지 확인 |
| 경계 근방에서 해를 놓친다 | (2)의 허용오차가 너무 작다 | 허용오차를 $10^{-9} \to 10^{-7}$ 로 올려 재시도하고 왕복 오차를 다시 본다 |

## 열린 문제

- **(열린 문제) 일반 구조의 전역 IK 인증** — 6R 의 상한 16 은 알려졌지만, **주어진 목표에 대해
  모든 해를 찾았음을 인증(certify)** 하는 실용적 방법은 제한적이다. 수치 대수(resultant,
  homotopy continuation)는 비싸고, 수치 IK 는 한 해만 준다. 인증 가능한 전역 최적화를
  SE(3) 문제에 적용하는 흐름(`c5-robust-global-estimation` 의
  [SE-Sync](https://arxiv.org/abs/1612.07386))이 IK 로 확장될지가 열려 있다.
- **(열린 문제) 과잉 자유도와 연속체 로봇의 IK** — 7축 이상이나 연속체(continuum) 구조에서는
  해가 다양체를 이루고 "모든 해"가 유한 집합이 아니다. 어떤 기준으로 그 다양체를 매개화하고
  과제 요구(장애물 회피, 관절 한계)와 결합할지에 대한 일반 해법이 없다 — `c6-tamp` 와 연결된다.
- **(열린 문제) 학습 기반 IK 의 보장** — 신경망 IK 는 빠르지만 해의 존재·정확도·분기 완전성에
  보장이 없다. 해석적 분해를 사전지식으로 넣은 하이브리드가 어디까지 보장을 회복할 수 있는지
  정리되지 않았다.

## 개념 점검

`rc quiz c1-poe-analytic-ik` 로 푼다. 개념 점검 전용이고 실제 과제는 문제 세트와 재현 과제다.

```quiz
activity: c1-poe-analytic-ik-quiz
questions:
  - id: q1
    type: single
    prompt: "PoE 공간 형식 (1)에서 나선 축 $\\mathcal{S}_i$ 는 어느 자세에서 본 값인가?"
    choices:
      - "현재 관절각 $\\theta$ 에서의 값 (매번 다시 계산한다)"
      - "영 자세(zero configuration)에서의 고정값"
      - "말단 프레임에서 본 값"
      - "앞 관절이 움직인 뒤의 값"
    answer: 1
    explanation: "$\\mathcal{S}_i$ 는 영 자세에서 본 고정값이다. $\\theta_1$ 이 움직이면 실제 축 2 의 위치는 바뀌지만 (1)의 왼쪽 인자가 그 변화를 흡수하므로 축을 다시 계산하지 않는다 — DH 표 없이 축 목록만으로 기구학을 쓸 수 있는 이유다."
    concept: { front: "PoE 의 나선 축을 어느 자세에서 재는가", back: "영 자세에서의 고정값. 앞 관절의 운동은 왼쪽 지수 인자가 흡수한다" }
  - id: q2
    type: multiple
    prompt: "Paden–Kahan 부문제 1 의 해가 존재할 조건을 모두 고르라. ($u = p-q$, $v = r-q$)"
    choices:
      - "$\\omega^\\top u = \\omega^\\top v$ (축 방향 성분이 같다)"
      - "$\\lVert u'\\rVert = \\lVert v'\\rVert$ (수직 성분의 길이가 같다)"
      - "$u$ 와 $v$ 가 평행하다"
      - "$p$ 가 축 위에 있다"
    answer: [0, 1]
    explanation: "회전은 축 방향 성분과 수직 성분의 길이를 보존한다. 그 두 보존량이 일치해야 해가 있다. $p$ 가 축 위에 있으면($u'=0$) 오히려 퇴화해서 $\\theta$ 가 임의가 된다."
    concept: { front: "부문제 1 의 해 존재 조건", back: "축 방향 성분이 같고 수직 성분의 길이가 같다 — 회전이 보존하는 두 양이기 때문" }
  - id: q3
    type: single
    prompt: "부문제 1 의 각을 $\\arccos(u'^\\top v'/\\lVert u'\\rVert^2)$ 대신 atan2 로 쓰는 주된 이유는?"
    choices:
      - "atan2 가 더 빠르다"
      - "$\\arccos$ 는 부호를 잃고($[0,\\pi]$ 만 준다) $u' \\parallel v'$ 근방에서 미분이 발산한다"
      - "$\\arccos$ 는 정의역이 좁아 쓸 수 없다"
      - "두 방법은 완전히 동등하다"
    answer: 1
    explanation: "회전 방향(부호)은 $\\omega^\\top(u'\\times v')$ 가 결정한다. $\\arccos$ 만 쓰면 그 정보를 잃고, 벡터가 거의 평행할 때 수치적으로도 나쁘다. 사인·코사인 성분을 모두 쓰는 atan2 가 전구간과 조건수 모두 낫다."
  - id: q4
    type: single
    prompt: "일반 6R 매니퓰레이터 역기구학의 해는 최대 몇 개인가?"
    choices: ["2", "8", "16", "무한"]
    answer: 2
    explanation: "일반 6R 은 최대 16개이며 16차 다항식으로 환원된다(Husty et al. 2007). 구형 손목처럼 특수 구조면 8개로 줄고 Paden–Kahan 으로 닫힌 해가 나온다."
    concept: { front: "일반 6R IK 의 해 개수 상한", back: "16개(16차 다항식). 구형 손목 등 특수 구조는 8개이고 닫힌 해가 있다" }
```

## 이 단계 공부법

1. **축 목록으로 로봇을 쓰는 연습 (40분)** — 종이에 3축 팔 하나를 그리고 $\mathcal{S}_i$ 와 $M$ 을
   직접 적는다. 회전 관절은 $(\omega, -\omega\times q)$ 다. 이걸 못 하면 뒤가 전부 막힌다.
2. **부문제 1 을 기하로 먼저 본다 (50분)** — 식보다 그림이다. 축에 수직인 평면에 $u'$, $v'$ 를
   그리고 "같은 반지름 위의 두 점"임을 확인한 뒤, 그 각이 (3)임을 쓴다. P4 로 검산한다.
3. **퇴화를 먼저 코딩한다 (60분)** — P5 에서 해 없음·퇴화·복수 해를 **먼저** 반환값으로 설계하고
   정상 경로를 나중에 채운다. 거꾸로 하면 예외 처리가 뒤섞여 디버깅이 어렵다.
4. **분기 개수를 눈으로 본다 (60분)** — 재현 과제 조건 4 의 히스토그램을 그린다. 8개가 나오는
   구조에서 특이 구성으로 다가가며 개수가 줄어드는 것을 보는 것이 이 레슨의 핵심 경험이다.
5. **수치 IK 와 비교한다 (40분)** — 같은 목표에 수치 해법을 돌려 **한 해만** 나오는 것을 확인한다.
   "해석적 해가 왜 가치 있는가"에 대한 답이고, 동시에 "왜 일반 구조에서는 수치로 가는가"의 근거다.
6. **논문은 경계를 찾으며 읽는다 (100분)** — Brockett 1984 는 관점의 전환을, Husty 2007 은
   해석적 해법의 한계를 준다. 두 논문의 노트에 "어디까지 닫힌 해이고 어디서 수치로 가는가"를
   한 문단으로 쓴다.

**통과 기준**: 축 목록만으로 PoE 를 세울 수 있고, 부문제 1 의 해 조건과 (3)을 백지에서 유도할 수
있고, 퇴화를 반환값으로 구분하는 구현이 재현 과제 네 조건을 만족하고, 논문 2편의 노트가 있다.
