---
id: r0-manifolds-lie-groups
title: 다양체와 행렬 리 군 입문
summary: >-
  매끄러운 다양체와 접공간을 정의하고, 행렬 리 군을 "군이면서 다양체"로 다루며, 행렬 지수가 왜
  리 대수에서 군으로 가는 다리인지 확인한다. C1 이 쓰는 언어를 미리 익히는 브리지 레슨이다.
objectives:
  - 매끄러운 다양체와 접공간을 정의하고 제약 집합이 다양체가 되는 조건을 쓸 수 있다.
  - 행렬 리 군의 정의를 쓰고 SO(3)·SE(3)가 그 예임을 확인할 수 있다.
  - 리 대수를 항등원의 접공간으로 정의하고 so(3)가 반대칭 행렬임을 유도할 수 있다.
  - 행렬 지수가 리 대수에서 군으로 가는 사상임을 보이고 그 성질을 쓸 수 있다.
  - 다양체 위에서 "미분"과 "덧셈"이 왜 조심스러운지 설명할 수 있다.
prerequisites: [r0-estimation-theory]
difficulty: 3
estimated_minutes: 420
tags: [differential-geometry, lie-groups, manifolds, research]
activities:
  - id: r0-manifolds-lie-groups-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 80
  - id: r0-manifolds-lie-groups-textbook
    kind: reading
    title: 교재 읽기 (Barfoot ch.7, MLS ch.2, Solà et al.) + 1페이지 노트
    estimated_minutes: 100
  - id: r0-manifolds-lie-groups-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 130
  - id: r0-manifolds-lie-groups-reproduction
    kind: reproduction
    title: 재현 과제 — 제약 다양체와 접공간을 수치로 확인 (R1)
    estimated_minutes: 95
  - id: r0-manifolds-lie-groups-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.7 (3차원 기하 입문). 로보틱스 표기로 쓰인 1순위 교재.
  - title: "Murray, Li & Sastry, A Mathematical Introduction to Robotic Manipulation"
    kind: book
    note: ch.2 (강체 운동). 리 군 관점의 고전적 서술. (공식 URL 미확인)
  - title: "Solà, Deray & Atchuthan — A micro Lie theory for state estimation in robotics (2018)"
    url: https://arxiv.org/abs/1812.01537
    kind: paper
    note: 2절까지. 이 레슨이 끝나면 읽을 수 있고, C1 에서 본격적으로 쓴다.
  - title: "NumPy linalg 문서"
    url: https://numpy.org/doc/stable/reference/routines.linalg.html
    kind: notes
    note: expm 은 scipy.linalg 에 있다. 재현 과제에서 행렬 지수를 쓴다.
---

# 다양체와 행렬 리 군 입문

## 전제와 기호

| 기호 | 뜻 |
|---|---|
| $\mathcal{M}$ | 매끄러운 다양체 |
| $T_p\mathcal{M}$ | 점 $p$ 에서의 접공간 |
| $G$ | 행렬 리 군 (행렬들로 이루어진 군이면서 다양체) |
| $\mathfrak{g} = T_I G$ | $G$ 의 리 대수 (항등원의 접공간) |
| $\exp: \mathfrak{g} \to G$ | 행렬 지수 |
| $h(x)=0$ | 다양체를 정의하는 제약 |

**이 레슨의 위치**: 이것은 **브리지**다. `c1-so3-se3-exponential` 부터 C1 전체가 여기서 익힌
언어로 쓰여 있고, 거기서 Rodrigues 공식·전사성·야코비안을 **증명 수준으로** 다룬다. 이 레슨의
목표는 그 유도를 **읽을 수 있게** 만드는 것이고, 같은 결과를 두 번 증명하지 않는다.

전제: `f0-linear-algebra`, `f0-calculus-multivariable`(음함수 정리), `r0-estimation-theory`.

## 핵심 결과

- **R1 (제약이 다양체를 만드는 조건) [D3]** — $h: \mathbb{R}^n \to \mathbb{R}^m$ 가 $C^1$ 이고
  $\mathcal{M} = \{x : h(x)=0\}$ 위의 모든 점에서 $\mathrm{rank}\,Dh(x) = m$ (최대 랭크)이면,
  $\mathcal{M}$ 은 차원 $n-m$ 의 매끄러운 다양체이고

$$
T_x\mathcal{M} = \ker Dh(x) = \{v : Dh(x)\,v = 0\} . \tag{1}
$$

  (음함수 정리의 귀결.)
- **R2 (행렬 리 군과 리 대수) [D2]** — $SO(3) = \{R : R^\top R=I,\ \det R=1\}$ 은 R1 의 조건을
  만족하는 3차원 다양체이고, 항등원의 접공간은

$$
\mathfrak{so}(3) = T_I SO(3) = \{\Omega : \Omega^\top = -\Omega\} \tag{2}
$$

  — **반대칭 행렬**이다. 차원 3 이 회전의 자유도와 맞는다.
- **R3 (행렬 지수가 다리다) [D2]** — $\Omega \in \mathfrak{g}$ 에 대해 $\exp(\Omega) \in G$ 이고,
  $t \mapsto \exp(\Omega t)$ 는 $I$ 를 지나는 $G$ 안의 곡선으로 그 속도가 $\Omega$ 다:

$$
\left.\frac{d}{dt}\exp(\Omega t)\right|_{t=0} = \Omega . \tag{3}
$$

  즉 지수 사상은 **접공간의 벡터를 군의 원소로 바꾸는** 자연스러운 사상이다.
- **R4 (군 구조가 주는 두 성질) [D2]** — ⓐ $\exp(\Omega)^{-1} = \exp(-\Omega)$ ⓑ 같은 $\Omega$ 의
  지수들은 교환하고 $\exp(\Omega s)\exp(\Omega t) = \exp(\Omega(s+t))$. 그러나
  **일반적으로 $\exp(A)\exp(B) \ne \exp(A+B)$** 이고, 이 간극을 재는 것이 C1 의 BCH 전개다.
- **R5 (다양체에서는 덧셈이 없다) [D1]** — $\mathcal{M}$ 은 벡터공간이 아니므로 $p + v$ 가
  $\mathcal{M}$ 에 있다는 보장이 없다. 그래서 ⓐ 점은 군 원소로, ⓑ 증분은 접공간 벡터로,
  ⓒ 둘의 결합은 $p\,\exp(v)$ 로 쓴다. C1·C5 의 모든 추정·최적화가 이 규약 위에 있다.

## 유도

### R2 — $\mathfrak{so}(3)$ 가 반대칭인 이유

$SO(3)$ 안의 곡선 $R(t)$ 가 $R(0)=I$ 를 지난다고 하자. 제약 $R^\top R = I$ 를 $t$ 로 미분하면

$$
\dot{R}^\top R + R^\top\dot{R} = 0 .
$$

$t=0$ 에서 $R=I$ 이므로 $\dot{R}(0)^\top + \dot{R}(0) = 0$, 즉 $\dot{R}(0)$ 은 **반대칭**이다.
역으로 임의의 반대칭 $\Omega$ 에 대해 $R(t) = \exp(\Omega t)$ 가 $SO(3)$ 안의 곡선임을 R3 로
확인할 수 있으므로, 접공간은 정확히 반대칭 행렬 전체다 — (2).

**차원 확인**: $3\times3$ 반대칭 행렬은 대각이 0 이고 상삼각 3개가 독립이므로 **차원 3**이다.
R1 로도 셀 수 있다: 제약 $R^\top R=I$ 는 대칭행렬 등식이므로 식이 6개($3\cdot4/2$)이고
$9-6=3$ 이다. 두 계산이 맞는다.

**$\det R = 1$ 은 왜 차원을 줄이지 않는가**: $\det$ 는 $R^\top R=I$ 아래에서 $\pm1$ 만 가능한
**이산** 조건이므로 연결 성분을 고를 뿐 차원을 바꾸지 않는다. 그래서 $O(3)$ 과 $SO(3)$ 은 같은
차원이고, $SO(3)$ 은 그중 $I$ 를 포함하는 성분이다.

### R3 — 지수 사상이 군 안에 머무는 이유

$\Omega$ 가 반대칭일 때 $\exp(\Omega)$ 가 $SO(3)$ 에 있음을 직접 보인다:

$$
\exp(\Omega)^\top\exp(\Omega) = \exp(\Omega^\top)\exp(\Omega) = \exp(-\Omega)\exp(\Omega) = \exp(0) = I ,
$$

여기서 ⓐ $\exp(A)^\top = \exp(A^\top)$(급수를 항별로 전치) ⓑ $\Omega^\top = -\Omega$
ⓒ **같은 행렬의 지수는 교환하므로** $\exp(-\Omega)\exp(\Omega) = \exp(0)$ 을 썼다.
행렬식은 $\det\exp(\Omega) = e^{\mathrm{tr}\,\Omega} = e^0 = 1$ 이므로 $\det=1$ 도 만족한다
(반대칭이면 대각이 0, 따라서 trace 가 0).

(3)은 급수 $\exp(\Omega t) = I + \Omega t + O(t^2)$ 를 미분하면 바로 나온다.

**가정이 깨지는 곳**: ⓒ 에서 **같은 행렬**이라는 조건이 결정적이다. $\exp(A)\exp(B)$ 를
$\exp(A+B)$ 로 바꾸려면 $AB=BA$ 가 필요하다. 축이 다른 두 회전은 교환하지 않으므로 이 치환이
불가능하고, 그 차이가 BCH 전개로 측정된다(C1 의 `c1-lie-group-derivatives`).

## 증명 스케치

### R1 — 제약 집합이 다양체가 되는 조건

**가설** H1: $h \in C^1$. H2: $\mathcal{M}$ 의 모든 점에서 $Dh$ 가 최대 랭크 $m$.
**결론** C: $\mathcal{M}$ 은 $(n-m)$ 차원 매끄러운 다양체이고 접공간이 (1)이다.

**전략**: 음함수 정리로 국소 매개화를 만든다. "다양체"의 정의가 곧 "국소적으로 $\mathbb{R}^{n-m}$
처럼 보인다"이므로, 그 매개화를 구성하면 끝난다.

1. 점 $x_0 \in \mathcal{M}$ 에서 $Dh(x_0)$ 가 랭크 $m$ 이므로, 좌표를 재배열해
   $Dh = [D_1h \;|\; D_2h]$ 에서 $D_2h \in \mathbb{R}^{m\times m}$ 가 가역이 되게 할 수 있다.
2. 음함수 정리: $x_0$ 근방에서 $x_2 = \varphi(x_1)$ 인 $C^1$ 함수 $\varphi$ 가 존재해
   $h(x_1, \varphi(x_1)) = 0$ 이다.
3. 따라서 $\mathcal{M}$ 은 국소적으로 $x_1 \in \mathbb{R}^{n-m}$ 의 그래프이고, 이 그래프 사상이
   국소 매개화(차트)다 — 다양체의 정의를 만족하며 차원은 $n-m$.
4. **접공간**: $\mathcal{M}$ 안의 곡선 $x(t)$ 에 대해 $h(x(t))=0$ 을 미분하면
   $Dh(x)\dot{x} = 0$ 이므로 모든 접벡터가 $\ker Dh$ 에 있다. 차원이 둘 다 $n-m$ 이므로 같다 — (1).

**가설을 지우면**: H2(최대 랭크)가 깨지는 점에서는 $\mathcal{M}$ 이 **매끄럽지 않을 수 있다**.
예: $h(x,y)=x^2-y^2$ 의 영집합은 원점에서 두 직선이 교차해 다양체가 아니고, 그 점에서
$Dh = (2x, -2y) = (0,0)$ 로 랭크가 0 이다. **랭크 조건은 형식이 아니라 실질**이다.

**로보틱스에서의 쓰임**: 폐루프 기구(4절 링크)의 구성공간이 바로 이런 제약 다양체이고, 랭크가
떨어지는 점이 **특이 구성**이다(C2 의 제약 동역학, C6 의 구성공간). 즉 R1 의 랭크 조건이 실무의
특이점 개념과 같은 것이다.

## 문제 세트

★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R2)** $SE(3)$ 의 리 대수 $\mathfrak{se}(3)$ 를 R2 와 같은 방법으로 유도하라
(동차변환의 제약을 미분한다). 차원이 6 임을 두 방법으로 확인하라.
*해답 스케치*: $T = \begin{bmatrix}R & p\\ 0 & 1\end{bmatrix}$ 에서 $R^\top R=I$ 와 마지막 행이
상수라는 제약을 미분한다. 차원은 ⓐ 반대칭 3 + 평행이동 3 ⓑ $16 - 6 - 4$(마지막 행 고정) = 6.

**P2 (유도, ★★, R3·R4)** $\exp(A)\exp(B) = \exp(A+B)$ 가 $AB=BA$ 일 때만 일반적으로 성립함을
급수로 확인하고, $2\times2$ 반대칭·대각 행렬로 반례를 만들라.
*해답 스케치*: 급수의 2차 항을 비교하면 $\tfrac12(AB+BA)$ 대 $\tfrac12(A+B)^2$ 의 차이가
$\tfrac12[A,B]$ 로 남는다. 교환자가 0 이 아니면 틀린다.

**P3 (증명, ★★★, R1)** R1 의 증명을 빈틈 없이 쓰고, 4단계에서 "차원이 같으므로 같다"를 정당화하라
(포함 관계만으로는 부족한 이유).
*해답 스케치*: 접벡터 집합이 $\ker Dh$ 의 부분집합임은 미분으로 나오지만, 같음을 보이려면
3단계의 매개화로 $n-m$ 개의 독립 접벡터를 **구성**해야 한다.

**P4 (계산, ★, R2·R3)** $\Omega = \begin{psmallmatrix}0&-1&0\\1&0&0\\0&0&0\end{psmallmatrix}$ 에
대해 ⓐ $\Omega$ 가 반대칭인지 ⓑ $\exp(\Omega\cdot\pi/2)$ 를 ⓒ $\det$ 와 $R^\top R$ 를 확인하라.
*정답*: ⓐ 그렇다 ⓑ $z$ 축 90° 회전
$\begin{psmallmatrix}0&-1&0\\1&0&0\\0&0&1\end{psmallmatrix}$ ⓒ $\det=1$, $R^\top R=I$.
허용오차 $10^{-12}$.

**P5 (구현, ★★, R1·R3)** ⓐ 구면 $\lVert x\rVert=1$ 과 ⓑ 4절 링크의 폐루프 제약을 각각
$h(x)=0$ 으로 쓰고, 무작위 점에서 $Dh$ 의 수치 랭크와 $\ker Dh$ 의 기저를 구하라. 그 기저 방향으로
작은 스텝을 가면 제약 위반이 $O(\epsilon^2)$ 임을 확인하라.
*루브릭*: ⓐ 유한차분 또는 해석적 $Dh$ 를 쓰고 랭크 임계값을 명시한다 ⓑ 접공간 스텝의 제약 위반이
2차임을 로그-로그 기울기 2 로 보인다 ⓒ 법선 방향 스텝은 위반이 1차임을 대조한다
ⓓ 4절 링크의 특이 구성에서 랭크가 떨어지는 것을 찾아 보고한다.

**P6 (반례, ★★, R1·R5)** ⓐ 랭크 조건이 깨져 다양체가 아닌 제약 집합의 예와 ⓑ 다양체 위에서
"덧셈"이 집합을 벗어나는 예를 각각 들라. ⓑ 에서 $p\exp(v)$ 가 왜 안전한지 설명하라.
*성질 체크리스트*: ⓐ $x^2-y^2=0$ 의 원점, ⓑ $R + \Omega$ 는 회전행렬이 아니다($R^\top R \ne I$).
$p\exp(v)$ 는 군 연산이므로 결과가 반드시 군 안에 있다.

## 논문 읽기

**교재 예외 적용**(레슨 표준 §5). 교재 2장과 논문 1편을 읽고 1페이지 노트를 쓴다(고정 질문 1·3·4·8).

1. **Barfoot, ch.7** — 질문: ⓐ 저자가 회전을 "제약 있는 행렬"로 보는 관점과 "리 군"으로 보는
   관점을 어떻게 연결하는지 쓰라. ⓑ 이 장에서 제시되는 표기 중 C1 에서 쓸 것들을 목록으로 만들라.
2. **Solà, Deray & Atchuthan, "A micro Lie theory for state estimation in robotics" (2018), 2절까지** —
   <https://arxiv.org/abs/1812.01537>
   질문: ⓐ 저자들이 $\oplus$·$\ominus$ 를 도입하는 **동기**를 R5 와 연결해 쓰라.
   ⓑ 이 글에서 "아직 이해하지 못한 것" 세 가지를 적어 두라 — C1 을 마친 뒤 다시 보면 답이 있다.

## 재현 과제

**티어 R1 (수치 검증).** 예산: 노트북 CPU 1분 이내, numpy/scipy 만. 네 조건을 모두 만족해야 한다.

1. **지수 사상이 군 안에 머문다**: 무작위 반대칭 $\Omega$ 1000개에 대해 $R=\exp(\Omega)$ 가
   $\lVert R^\top R - I\rVert_F < 10^{-12}$ 와 $|\det R - 1| < 10^{-12}$ 를 만족한다.
2. **(3)의 수치 확인**: 중심 유한차분으로 계산한
   $\frac{d}{dt}\exp(\Omega t)|_{t=0}$ 가 $\Omega$ 와 $10^{-7}$ 이내로 일치한다.
3. **접공간이 제약의 영공간**: 구면과 4절 링크 제약에서 ⓐ $\ker Dh$ 의 기저를 구하고
   ⓑ 그 방향 스텝 $\epsilon$ 에 대한 제약 위반이 $O(\epsilon^2)$(로그-로그 기울기 $2\pm0.2$),
   ⓒ 법선 방향 스텝의 위반은 $O(\epsilon)$(기울기 $1\pm0.2$)임을 보인다.
4. **덧셈이 틀리는 것**: 무작위 $R \in SO(3)$ 와 작은 반대칭 $\Omega$ 에 대해
   ⓐ $R+\Omega$ 의 $\lVert(\cdot)^\top(\cdot)-I\rVert_F$ 가 $O(\lVert\Omega\rVert)$ 로 커지고
   ⓑ $R\exp(\Omega)$ 는 $10^{-12}$ 이내로 군 안에 머무는 것을 대조한다.

**비교 대상**: `scipy.linalg.expm` 과 (Rodrigues 공식을 직접 구현했다면) 그 결과가 $10^{-12}$
이내로 일치.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 1 이 큰 $\lVert\Omega\rVert$ 에서 실패 | `expm` 의 정확도 한계가 아니라 $\Omega$ 가 반대칭이 아님 | $\lVert\Omega+\Omega^\top\rVert$ 를 출력 |
| 조건 2 의 오차가 크다 | 유한차분 스텝이 너무 작거나 크다 | $h\sim\epsilon^{1/3}$ 로 맞춘다(`f0-python-numerics-git`) |
| 조건 3 의 기울기가 2 가 아니다 | 접공간 기저가 정규화되지 않았거나 랭크 판정이 틀렸다 | 기저를 SVD 로 구하고 임계값을 출력 |
| 4절 링크에서 랭크가 항상 최대 | 특이 구성을 지나지 않았다 | 링크 각을 쓸며 $Dh$ 의 최소 특이값을 그린다 |

## 열린 문제

- **(열린 문제) 특이 구성 근방의 수치적 취급** — 랭크 조건이 **경계상으로** 깨지는 근방에서
  접공간 계산이 불안정하다. 폐루프 기구와 접촉 제약에서 특이 구성을 어떻게 안전하게 지날지가
  정리되지 않았다(C2 의 제약 동역학과 연결).
- **(열린 문제) 다양체 제약과 학습의 결합** — 신경망 출력을 다양체에 제약하는 방법(투영,
  매개화, 정칙화)이 여러 가지인데, 각각이 표현력과 학습 안정성에 주는 영향이 비교되지 않았다
  (`c7-learned-correspondence-slam` 과 연결).
- **(열린 문제) 비매끄러운 제약 집합** — 접촉·충돌이 있는 구성공간은 다양체가 아니라 **경계가
  있는 집합**이다. 그 위의 미분·최적화 이론이 매끄러운 경우만큼 정리되지 않았다(C6 의 계획 이론).

## 개념 점검

`rc quiz r0-manifolds-lie-groups` 로 푼다. 개념 점검 전용이다.

```quiz
activity: r0-manifolds-lie-groups-quiz
questions:
  - id: q1
    type: short
    prompt: "$\\mathcal{M}=\\{x\\in\\mathbb{R}^n : h(x)=0\\}$ ($h:\\mathbb{R}^n\\to\\mathbb{R}^m$, 최대 랭크)의 차원은?"
    answer: ["n-m", "n - m", "n−m", "n minus m"]
    explanation: "음함수 정리에서 국소적으로 $n-m$ 개 자유 변수의 그래프가 되므로 차원은 $n-m$ 이다. 접공간은 $\\ker Dh$ 이고 그 차원도 $n-m$ 이다."
    concept: { front: "제약 다양체의 차원", back: "$n-m$ (최대 랭크 조건 아래). 접공간은 $\\ker Dh$" }
  - id: q2
    type: single
    prompt: "$\\mathfrak{so}(3)$ (항등원에서 $SO(3)$ 의 접공간)은 어떤 행렬의 집합인가?"
    choices:
      - "대칭 행렬"
      - "반대칭 행렬"
      - "직교 행렬"
      - "trace 가 0 인 모든 행렬"
    answer: 1
    explanation: "$R^\\top R=I$ 를 미분해 $t=0$ 에서 평가하면 $\\dot{R}^\\top+\\dot{R}=0$, 즉 반대칭이다. 차원 3 이 회전의 자유도와 맞는다."
    concept: { front: "$\\mathfrak{so}(3)$ 의 정체", back: "반대칭 행렬 전체(차원 3). 제약 $R^\\top R=I$ 를 미분해서 나온다" }
  - id: q3
    type: truefalse
    prompt: "임의의 행렬 $A, B$ 에 대해 $\\exp(A)\\exp(B) = \\exp(A+B)$ 다."
    answer: false
    explanation: "$AB=BA$ 일 때만 성립한다. 급수의 2차 항을 비교하면 교환자 $\\tfrac12[A,B]$ 만큼 차이가 난다. 그 간극을 재는 것이 BCH 전개이고 C1 에서 다룬다."
    concept: { front: "지수의 곱", back: "$\\exp(A)\\exp(B)=\\exp(A+B)$ 는 $AB=BA$ 일 때만. 차이는 교환자(BCH)" }
  - id: q4
    type: single
    prompt: "회전 $R$ 에 작은 증분을 주는 **올바른** 방법은?"
    choices:
      - "$R + \\Omega$ (행렬 덧셈)"
      - "$R\\exp(\\Omega)$ 또는 $\\exp(\\Omega)R$"
      - "$R \\cdot \\Omega$"
      - "$\\Omega^{-1}R$"
    answer: 1
    explanation: "$SO(3)$ 은 벡터공간이 아니므로 $R+\\Omega$ 는 회전행렬이 아니다($R^\\top R \\ne I$). 군 연산으로 결합하면 결과가 반드시 군 안에 있다. 왼쪽/오른쪽 선택이 좌/우 야코비안의 구분으로 이어진다(C1)."
    concept: { front: "다양체 위의 증분", back: "$R\\exp(\\Omega)$ (군 연산). 덧셈 $R+\\Omega$ 는 군을 벗어난다" }
```

## 이 단계 공부법

1. **R2 의 미분을 손으로 한다 (30분)** — $R^\top R=I$ 를 미분해 반대칭을 얻는 세 줄이 이 레슨의
   핵심이다. 같은 요령으로 P1 에서 $\mathfrak{se}(3)$ 를 유도한다.
2. **차원을 두 방법으로 센다 (30분)** — 기저를 직접 세는 방법과 R1 의 $n-m$ 공식. 두 값이 맞는지
   확인하는 습관이 뒤에서 게이지 자유도 차원을 셀 때 쓰인다.
3. **군 안에 머무는 것을 수치로 본다 (60분)** — 재현 과제 조건 1·4 를 함께 한다. $R+\Omega$ 가
   군을 벗어나고 $R\exp(\Omega)$ 는 머무는 대조가 C1·C5 전체의 설계 이유다.
4. **접공간을 영공간으로 계산해 본다 (70분)** — 조건 3. 구면은 직관적이고 4절 링크는 실제
   로보틱스 제약이다. 특이 구성에서 랭크가 떨어지는 것을 보면 R1 의 가설이 왜 실질적인지 안다.
5. **BCH 는 "아직 모르는 것"으로 남긴다 (20분)** — R4 에서 $\exp(A)\exp(B)\ne\exp(A+B)$ 만
   확인하고 넘어간다. 간극을 재는 방법은 C1 의 `c1-lie-group-derivatives` 가 다룬다. **여기서
   욕심내면 브리지가 코어를 중복한다.**
6. **논문의 "모르는 것 세 가지"를 적어 둔다 (100분)** — Solà et al. 2절까지 읽고 이해하지 못한
   것을 기록한다. C1 을 마친 뒤 그 목록을 다시 보면 이 두 레슨의 관계가 분명해진다.

**통과 기준**: $R^\top R=I$ 에서 $\mathfrak{so}(3)$ 를 유도할 수 있고, R1 의 랭크 조건과 접공간
공식을 쓸 수 있고, 재현 과제 네 조건을 만족하는 코드와 노트 2편이 있다.
