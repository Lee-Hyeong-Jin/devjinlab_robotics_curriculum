---
id: c2-rnea-inverse-dynamics
title: 재귀 Newton–Euler (RNEA)
summary: >-
  기구 트리의 역동역학을 전진 운동학 재귀와 후진 힘 재귀로 유도하고, 가속도 재귀의 편향 항이
  공간 야코비안의 비적분성(리 괄호)에서 나오는 것을 보이고, RNEA 의 출력이 일반화 힘과 정확히
  같다는 것(Euler–Lagrange 와의 동등성)과 $\Theta(n)$ 이 차수 최적임을 증명 수준에서 다룬다.
objectives:
  - 속도 재귀에서 가속도 재귀를 빠진 줄 없이 유도하고 편향 항 $v_i \times S_i\dot{q}_i$ 의 출처를 설명할 수 있다.
  - 후진 힘 재귀와 $\tau_i = S_i^\top f_i$ 를 힘 균형과 가상 일로 각각 유도할 수 있다.
  - RNEA 의 출력이 $\sum_j (\partial v_j/\partial \dot{q}_k)^\top f_j$ 임을 재귀를 풀어 증명할 수 있다.
  - 공간 야코비안의 $\partial_{q_l} J_{\cdot k} - \partial_{q_k} J_{\cdot l} = [J_{\cdot k}, J_{\cdot l}]$ 를 쓰고 코리올리 항의 기원을 말할 수 있다.
  - RNEA 가 $\Theta(n)$ 이고 차수 최적임을 상한·하한 양쪽으로 논증할 수 있다.
prerequisites: [c2-spatial-vector-algebra]
difficulty: 5
estimated_minutes: 480
tags: [multibody-dynamics, inverse-dynamics, rnea, lagrange, complexity, research]
activities:
  - id: c2-rnea-inverse-dynamics-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c2-rnea-inverse-dynamics-papers
    kind: paper
    title: 필독 논문 2편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 120
  - id: c2-rnea-inverse-dynamics-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 논문 1)
    estimated_minutes: 150
  - id: c2-rnea-inverse-dynamics-reproduction
    kind: reproduction
    title: 재현 과제 — RNEA 와 Euler–Lagrange 의 일치 (R1)
    estimated_minutes: 105
  - id: c2-rnea-inverse-dynamics-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Featherstone, Rigid Body Dynamics Algorithms (2008)"
    url: https://doi.org/10.1007/978-0-387-74315-8
    kind: book
    note: ch.5 (Inverse Dynamics). 재귀식의 표기와 비용 표(§5.3)가 이 레슨의 기준이다.
  - title: "Lynch & Park, Modern Robotics"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: ch.8.3 (Newton–Euler Inverse Dynamics). 같은 알고리즘을 $(\omega, v)$ 트위스트 표기로 본다. 전문 PDF 무료.
  - title: "Featherstone — Spatial vector and rigid-body dynamics software"
    url: https://royfeatherstone.org/spatial/
    kind: code
    note: 권장. 저자의 `ID`(RNEA) 구현. 재현 과제의 선택 교차 검증용(Octave).
papers:
  - id: luh1980-rnea
    role: seminal
    required: true
    note: 전진 운동학 재귀와 후진 힘 재귀를 세우는 절, 그리고 비용을 논하는 절. (1)(3)(5)와 1:1 대응.
  - id: featherstone2000-dynamics-equations-algorithms
    role: survey
    required: true
    note: 역·순동역학·질량행렬 알고리즘을 한 틀에서 비교하는 절. R5 와 다음 레슨의 복잡도 지형.
---

# 재귀 Newton–Euler (RNEA)

## 전제와 기호

앞 레슨 `c2-spatial-vector-algebra` 의 표기를 **그대로** 쓴다(각 성분 먼저, $M^6$/$F^6$,
$X$/$X^{*}$, $v\times$/$v\times^{*}$, 공간 관성 $I$). 거기서 세운 결과 중 이 레슨이 계속 쓰는 것:

- (앞 레슨 R4) 한 강체의 운동 방정식 $f = Ia + (v\times^{*})Iv$.
- (앞 레슨 R3) $\frac{d}{dt}{}^BX_A = -\,{}^BX_A(v\times)$ 와 $v\times^{*} = -(v\times)^\top$.
- (앞 레슨 R2) $^BI = ({}^AX_B)^\top\,{}^AI\,{}^AX_B$.

이 레슨은 **기구 트리(kinematic tree)**만 다룬다 — 폐루프는 `c2-constrained-dynamics`,
접촉은 `c2-contact-dynamics` 다. 관절은 모두 단일 자유도로 둔다(다자유도 관절은
$S_i$ 를 $6\times n_i$ 행렬로 바꾸면 모든 식이 그대로 성립한다 — 문제 P1 의 확장).

| 기호 | 뜻 |
|---|---|
| $n$ | 단일 자유도 관절의 수 = 자유도. 바디는 $1, \dots, n$, 고정 베이스는 $0$ |
| $\lambda(i)$ | 바디 $i$ 의 부모. 번호는 $\lambda(i) < i$ 가 되도록 매긴다(위상 정렬) |
| $\mu(i)$ | 바디 $i$ 의 자식 집합 |
| $\nu(i)$ | 바디 $i$ 를 뿌리로 하는 부분나무(subtree), $i$ 포함 |
| $S_i \in M^6$ | 관절 $i$ 의 운동 축(motion subspace). **바디 $i$ 좌표에서 상수** |
| $^iX_{\lambda(i)}(q_i)$ | 부모→자식 변환 $= X_{J_i}(q_i)\,X_{T,i}$. $X_{T,i}$ 는 트리의 고정 변환 |
| $v_i, a_i$ | 바디 $i$ 의 공간 속도·가속도. **바디 $i$ 좌표** |
| $v_{J_i} = S_i\dot{q}_i$ | 관절 $i$ 를 가로지르는 상대 속도 |
| $f_i \in F^6$ | 관절 $i$ 가 부모에서 바디 $i$ 로 전달하는 공간 힘 |
| $f_i^{x}$ | 바디 $i$ 에 직접 걸리는 외력(접촉·공기저항 등). 없으면 $0$ |
| $a_g = (0; g) \in M^6$ | 중력의 공간 가속도. 지면 좌표에서 $g = (0, 0, -9.81)$ 등 |
| $J_i \in \mathbb{R}^{6\times n}$ | 바디 $i$ 의 공간 야코비안. $v_i = J_i\dot{q}$, 바디 $i$ 좌표 |
| $\tau \in \mathbb{R}^n$ | 관절 일반화 힘(토크) |
| $M(q), C(q,\dot{q}), g(q)$ | 질량행렬·코리올리 행렬·중력 토크. $\tau = M\ddot{q} + C\dot{q} + g$ |

**부호 규약**: $f_i$ 는 **부모가 자식에게** 주는 힘이다. 반대 규약(자식이 부모에게)을 쓰면
후진 재귀의 모든 부호가 뒤집힌다 — 외부 구현과 수치를 맞출 때 두 번째로 확인할 것
(첫 번째는 성분 순서다).

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 — `lesson-standard.md` §2).

- **R1 (속도 재귀와 공간 야코비안) [D2]** —
  $$
  v_i = {}^iX_{\lambda(i)}\,v_{\lambda(i)} + S_i\dot{q}_i, \qquad v_0 = 0, \tag{1}
  $$
  이를 풀면 $v_i = J_i\dot{q}$ 이고 $J_i$ 의 열은
  $$
  J_{i,k} = \begin{cases} {}^iX_k\,S_k & k \in \{i\} \cup \text{(}i\text{ 의 조상)} \\ 0 & \text{그 외.}\end{cases} \tag{2}
  $$
  즉 $J_i$ 의 **희소 구조는 트리의 조상 관계**가 결정한다.
- **R2 (가속도 재귀와 편향 항의 출처) [D2]** —
  $$
  a_i = {}^iX_{\lambda(i)}\,a_{\lambda(i)} + S_i\ddot{q}_i + v_i \times v_{J_i}, \qquad v_{J_i} = S_i\dot{q}_i. \tag{3}
  $$
  마지막 항은 **좌표 변환이 시간에 따라 움직인다는 사실만으로** 생긴다. 그 정체는 공간
  야코비안의 **비적분성**이다: 모든 $k, l$ 과 모든 바디 $i$ 에 대해
  $$
  \frac{\partial J_{i,k}}{\partial q_l} - \frac{\partial J_{i,l}}{\partial q_k}
    = \big(J_{i,k}\times\big)\,J_{i,l} = [\,J_{i,k},\, J_{i,l}\,]. \tag{4}
  $$
  (4)의 우변이 0 이 아니기 때문에 $\dot{J}_i e_k \ne \partial J_i\dot{q}/\partial q_k$ 이고,
  **코리올리 항은 전부 여기서 나온다**. 7-DOF 무작위 자세에서 (4)를 중앙 유한차분으로 확인하면
  오차 $1.5\times10^{-10}$ 수준이다(재현 과제 조건 4).
- **R3 (후진 힘 재귀와 관절 토크) [D2]** — 바디 $i$ 의 합력이 운동 방정식을 만족해야 하므로
  $$
  f_i = \underbrace{I_i a_i + (v_i\times^{*})I_i v_i}_{\text{바디 } i \text{ 의 합력}} \;-\; f_i^{x}
      \;+\; \sum_{j \in \mu(i)} {}^iX_j^{*}\,f_j, \tag{5}
  $$
  $$
  \tau_i = S_i^\top f_i. \tag{6}
  $$
  (6)은 **가상 일(virtual work)**에서 나온다: 관절은 $S_i$ 방향으로만 움직일 수 있으므로
  전달된 힘 중 그 방향 성분만 일반화 힘에 나타난다. 중력은 별도 항이 아니라
  $a_0 := -a_g$ 로 베이스 가속도를 바꾸면 (3)(5)가 **그대로** 중력 토크를 포함한다. **[D1]**
- **R4 (RNEA = 일반화 힘 = Euler–Lagrange 좌변) [D3]** — 재귀 (5)를 풀면
  $$
  f_i = \sum_{j \in \nu(i)} {}^iX_j^{*}\,\big(I_j a_j + (v_j\times^{*})I_j v_j - f_j^{x}\big),
  $$
  따라서 (6)과 $S_i^\top\,{}^iX_j^{*} = \big({}^jX_i S_i\big)^\top = J_{j,i}^\top$ 로
  $$
  \tau_i = \sum_{j=1}^{n} \left(\frac{\partial v_j}{\partial \dot{q}_i}\right)^{\!\top}
    \big(I_j a_j + (v_j\times^{*})I_j v_j - f_j^{x}\big). \tag{7}
  $$
  (7)의 우변은 d'Alembert 원리가 말하는 **일반화 힘**이고, 홀로노믹 계에서 이것은
  Euler–Lagrange 좌변 $\frac{d}{dt}\frac{\partial T}{\partial \dot{q}_i} - \frac{\partial T}{\partial q_i}
  + \frac{\partial V}{\partial q_i}$ 와 같다. **[D1 가교]**
  특수화하면 $\dot{q} = 0$, $a_g = 0$, $\ddot{q} = e_k$ 에서 $\tau = M(q)e_k$ 이고
  (바로 `c2-crba-aba` 의 출발점), $\ddot{q} = 0$, $a_g = 0$ 에서 $\tau = C(q,\dot{q})\dot{q}$,
  $\dot{q} = \ddot{q} = 0$ 에서 $\tau = g(q)$ 다.
- **R5 (복잡도 $\Theta(n)$ 과 차수 최적성) [D3]** — RNEA 는 바디당 **$n$ 과 무관한 고정 개수**의
  6D 연산만 쓰므로 시간·메모리가 $\Theta(n)$ 이다. 반대로 직렬 연쇄에서는 모든 $\tau_k$ 가
  모든 $\ddot{q}_j$ 에 의존하므로($M$ 이 일반적으로 조밀) 어떤 알고리즘도 입력을 다 읽어야 하고
  $\Omega(n)$ 이 하한이다. 따라서 RNEA 는 **차수 최적**이다. $M$ 과 $C$ 를 명시적으로
  만든 뒤 곱하는 경로는 $\Theta(n^2)$(CRBA) 또는 그 이상이다 — RNEA 는 **둘 중 어느 것도
  만들지 않는 것**으로 $\Theta(n)$ 을 얻는다.

## 유도

### R1 — 속도 재귀

관절 $i$ 는 바디 $\lambda(i)$ 와 바디 $i$ 를 잇고, 두 바디의 상대 운동은 정의상 $v_{J_i} = S_i\dot q_i$
다(단일 자유도 관절의 운동 부분공간이 $S_i$ 라는 것이 바로 이 뜻이다). 공간 속도는 벡터이므로
바디 $i$ 좌표에서 더할 수 있고

$$
v_i = \underbrace{{}^iX_{\lambda(i)}v_{\lambda(i)}}_{\text{부모의 운동을 물려받음}} + \underbrace{S_i\dot{q}_i}_{\text{관절의 상대 운동}},
$$

즉 (1)이다. 고정 베이스는 $v_0 = 0$. 재귀를 $\lambda$ 를 따라 풀면

$$
v_i = \sum_{k \in \{i\}\cup \text{anc}(i)} {}^iX_k\,S_k\,\dot{q}_k
$$

이고 $\dot q$ 에 대해 선형이므로 (2)의 $J_i$ 를 얻는다. $k$ 가 $i$ 의 조상도 $i$ 자신도 아니면
그 관절의 운동은 바디 $i$ 에 전달되지 않으므로 열이 0 이다 — **이 희소 구조가 뒤에 나오는
모든 알고리즘의 비용을 결정한다**(CRBA 의 $O(n^2)$, $M$ 의 분기 영 패턴).

### R2 — 가속도 재귀

(1)을 미분한다. 핵심은 **무엇에 대해 미분하는가**다. 앞 레슨 R5 에서 공간 가속도는
"고정 좌표에서 $v$ 를 성분별로 미분한 것"으로 정의했다. 바디 $i$ 좌표에서 쓴 $v_i$ 에 대해서는

$$
a_i\big|_i = \frac{d}{dt}\big(v_i\big)_{\text{성분}} + \underbrace{v_i \times v_i}_{=\,0}
  = \frac{d}{dt}\big(v_i\big)_{\text{성분}} \tag{8}
$$

이 성립한다(움직이는 좌표계에서 성분 미분과 절대 미분의 차가 $v_f \times u$ 이고, 여기서는
$u = v_i$, $v_f = v_i$ 이므로 보정항이 사라진다). **따라서 (1)의 양변을 성분별로 그냥 미분하면
된다** — 이 한 줄이 공간 벡터 대수를 쓰는 실질적 이득이다.

우변의 두 항을 차례로 미분한다.

**둘째 항.** $S_i$ 는 바디 $i$ 좌표에서 상수이므로 $\frac{d}{dt}(S_i\dot q_i) = S_i\ddot{q}_i$.

**첫째 항.** $^iX_{\lambda(i)}$ 가 변하는 원인은 관절 $i$ 의 운동**뿐**이다(트리의 고정 변환
$X_{T,i}$ 는 상수). 프레임 $i$ 가 프레임 $\lambda(i)$ 에 대해 갖는 상대 공간 속도는 $v_{J_i}$ 이고,
앞 레슨 (5)의 둘째 식을 바디 $i$ 좌표로 쓰면

$$
\frac{d}{dt}\,{}^iX_{\lambda(i)} = -\big(v_{J_i}\times\big)\,{}^iX_{\lambda(i)}. \tag{9}
$$

(앞 레슨에서는 $\frac{d}{dt}{}^BX_A = -{}^BX_A(v\times)$ 로 $v$ 를 $A$ 좌표에 두었다. 수반
공액 $X(u\times)X^{-1} = \big((Xu)\times\big)$ 로 좌표를 옮기면 (9)가 된다 — 문제 P1 ⓐ.)
그러면

$$
\frac{d}{dt}\Big({}^iX_{\lambda(i)}v_{\lambda(i)}\Big)
= -\big(v_{J_i}\times\big)\,{}^iX_{\lambda(i)}v_{\lambda(i)} + {}^iX_{\lambda(i)}\,\frac{d}{dt}\big(v_{\lambda(i)}\big)_{\text{성분}}.
$$

(8)을 부모에 적용하면 둘째 항이 $^iX_{\lambda(i)}a_{\lambda(i)}$ 다. 첫째 항은 (1)에서
$^iX_{\lambda(i)}v_{\lambda(i)} = v_i - v_{J_i}$ 이므로

$$
-\big(v_{J_i}\times\big)\big(v_i - v_{J_i}\big)
= -\,v_{J_i} \times v_i + \underbrace{v_{J_i} \times v_{J_i}}_{=\,0}
= v_i \times v_{J_i},
$$

마지막 등호는 운동 외적의 반대칭성 $u \times w = -\,w \times u$ (문제 P2)다. 두 항을 더하면 (3)이다.

**편향 항의 정체.** (3)의 $v_i \times v_{J_i} = \dot{q}_i\,(v_i \times S_i)$ 는 $\ddot{q}$ 에
무관하고 $\dot{q}$ 에 **2차**다. 이 항이 왜 피할 수 없는지는 (4)가 말해 준다. $v_i = J_i\dot q$
를 직접 미분하면

$$
a_i = J_i\ddot{q} + \dot{J}_i\dot{q}, \qquad
\dot{J}_i\dot{q} = \sum_{k,l} \frac{\partial J_{i,k}}{\partial q_l}\dot{q}_k\dot{q}_l,
$$

인데 **만약** $\partial_{q_l}J_{i,k}$ 가 $(k, l)$ 에 대칭이었다면 이 이중 합은
$\partial_{q}\big(\tfrac{1}{2}\dot q^\top \cdots\big)$ 꼴의 완전 미분으로 접혀 코리올리 항이
좌표 변환만으로 사라졌을 것이다. (4)는 그 대칭이 **정확히 리 괄호만큼 깨진다**고 말한다.
(4)의 증명은 (2)를 $q_l$ 로 미분하고 (9)를 쓰는 두 줄이다(문제 P2 ⓑ).

> **수치로 본 (4)**: 2링크 평면 팔($l_1 = 0.6$, $l_2 = 0.4$, $q = (0.3, -0.7)$)의 바디 2 에서
> $\partial_{q_2}J_{2,1} - \partial_{q_1}J_{2,2} = (0,0,0,\;0.4589053124,\;0.3865306124,\;0)$ 이고
> $[J_{2,1}, J_{2,2}]$ 가 같은 값이다(중앙 유한차분 $h = 10^{-6}$, 오차 $1.9\times10^{-11}$).
> $\partial_{q_1}J_{2,2} = 0$ 인데 $\partial_{q_2}J_{2,1} \ne 0$ 인 **비대칭 그 자체**가 보인다.

### R3 — 후진 힘 재귀와 토크 투영

바디 $i$ 에 작용하는 모든 공간 힘의 합이 운동 방정식을 만족해야 한다. 바디 $i$ 가 받는 힘은
ⓐ 부모가 관절 $i$ 를 통해 주는 $f_i$, ⓑ 자식 $j$ 가 관절 $j$ 를 통해 주는 반작용 $-{}^iX_j^{*}f_j$,
ⓒ 외력 $f_i^{x}$ 다. 따라서

$$
f_i - \sum_{j\in\mu(i)} {}^iX_j^{*}f_j + f_i^{x} = I_i a_i + (v_i\times^{*})I_i v_i,
$$

$f_i$ 에 대해 풀면 (5)다. 자식의 힘을 부모 좌표로 옮길 때 $X^{*}$ (운동 변환이 아니라 **힘
변환**)를 쓰는 것이 앞 레슨 R1 의 요점이고, 여기서 $X^\top$ 을 쓰면 평행이동이 섞인
연쇄에서 즉시 틀린다. 재귀는 리프에서 시작해 $\lambda$ 를 따라 올라간다 — $\mu(i)$ 의 모든
$f_j$ 가 $f_i$ 보다 먼저 계산되므로 바디 번호를 역순($i = n, \dots, 1$)으로 훑으면 충분하다
($\lambda(i) < i$ 로 번호를 매겼으므로).

**(6)의 유도 — 가상 일.** 관절 $i$ 가 허용하는 가상 변위는 $\delta q_i$ 하나이고 그에 대응하는
가상 공간 변위는 $S_i\,\delta q_i$ 다. 관절을 가로질러 전달된 힘 $f_i$ 가 이 변위에 하는
가상 일은 $f_i \cdot (S_i\delta q_i) = (S_i^\top f_i)\,\delta q_i$ 다. 일반화 힘 $\tau_i$ 의
정의가 "$\delta q_i$ 에 짝지어지는 힘"이므로 $\tau_i = S_i^\top f_i$. 남은 성분
$(\mathbb{1} - S_i(S_i^\top S_i)^{-1}S_i^\top)f_i$ 는 **구속 반력**이고 일을 하지 않는다 —
이 분해가 `c2-constrained-dynamics` 의 널공간 투영으로 그대로 이어진다.

**중력 처리.** 중력은 바디마다 $f_i^{x} = I_i\,{}^iX_0\,a_g$ 를 더해도 되지만, 더 싼 방법은
$a_0 := -a_g$ 로 두는 것이다. 이유: (3)의 재귀는 $a$ 에 대해 **아핀**이고 $a_0$ 에 대한
의존이 $^iX_0 a_0$ 로 전파되므로, $a_0 = -a_g$ 는 모든 바디에 "위로 $g$ 만큼 가속하는 틀"을
주는 것과 같다 — 등가 원리의 알고리즘적 사용이다. 추가 비용이 **0**이다. **[D1]**

### 알고리즘

```python
def rnea(model, q, qd, qdd, a_grav):
    """Recursive Newton-Euler. Returns tau (n,). Angular-first spatial vectors."""
    n = model.n
    Xup = model.Xup(q)  # i X parent(i) for every body
    v, a, f = [None] * n, [None] * n, [None] * n
    for i in range(n):  # forward pass: kinematics
        S = model.S[i]
        vJ = S * qd[i]
        p = model.parent[i]
        if p < 0:
            v[i] = vJ
            a[i] = Xup[i] @ (-a_grav) + S * qdd[i]
        else:
            v[i] = Xup[i] @ v[p] + vJ
            a[i] = Xup[i] @ a[p] + S * qdd[i] + crm(v[i]) @ vJ
        f[i] = model.I[i] @ a[i] + crf(v[i]) @ model.I[i] @ v[i] - model.fx[i]
    tau = np.zeros(n)
    for i in range(n - 1, -1, -1):  # backward pass: forces
        tau[i] = model.S[i] @ f[i]
        p = model.parent[i]
        if p >= 0:
            f[p] = f[p] + Xup[i].T @ f[i]
    return tau
```

`Xup[i].T @ f[i]` 가 $^{\lambda(i)}X_i^{*}f_i$ 다 — 앞 레슨 (2)의
$^BX_A^{*} = ({}^AX_B)^\top$ 를 전치 **한 번**으로 쓴 것이고, 역행렬을 계산하지 않는다.
이 한 줄이 공간 벡터 대수를 쓰는 두 번째 실질적 이득이다.

## 증명 스케치

### R4 — RNEA 의 출력이 일반화 힘이다

**가설** H1: 계는 기구 트리(폐루프 없음)이고 모든 관절은 홀로노믹하다.
H2: $S_i$ 는 바디 $i$ 좌표에서 상수다. H3: 각 바디의 질량 분포는 상수다(강체).
**결론** C: 모든 $i$ 에 대해 (7)이 성립하고, 그 우변은 홀로노믹 계의 일반화 힘이다.

**전략**: 후진 재귀를 끝까지 **펼쳐** 닫힌 형태로 쓰고, $S_i^\top {}^iX_j^{*}$ 를 야코비안 열의
전치로 알아본다. 변분법은 쓰지 않는다 — 전부 선형대수다.

1. **재귀 펼치기.** $f_i^{\text{net}} := I_ia_i + (v_i\times^{*})I_iv_i - f_i^{x}$ 로 두면 (5)는
   $f_i = f_i^{\text{net}} + \sum_{j\in\mu(i)}{}^iX_j^{*}f_j$ 다. $i$ 의 자식에 같은 식을 반복
   대입하고 $^iX_j^{*}\,{}^jX_k^{*} = {}^iX_k^{*}$ (힘 변환의 합성 — 앞 레슨 P5 ⓓ)를 쓰면
   $$
   f_i = \sum_{j\in\nu(i)} {}^iX_j^{*}\,f_j^{\text{net}}.
   $$
   트리이므로 각 $j$ 가 **정확히 한 번** 나타난다(H1 이 쓰이는 첫 지점 — 폐루프에서는 같은
   바디가 두 경로로 세어져 이 등식이 깨진다).
2. **토크로 투영.** (6)에 넣고 전치를 옮긴다:
   $$
   \tau_i = S_i^\top \sum_{j\in\nu(i)} {}^iX_j^{*}f_j^{\text{net}}
   = \sum_{j\in\nu(i)} \big(({}^iX_j^{*})^\top S_i\big)^\top f_j^{\text{net}}
   = \sum_{j\in\nu(i)} \big({}^jX_i\,S_i\big)^\top f_j^{\text{net}},
   $$
   마지막 등호는 앞 레슨 (2) $({}^iX_j^{*})^\top = {}^jX_i$ 다.
3. **야코비안 열로 알아보기.** (2)에서 $^jX_iS_i = J_{j,i}$ 이고, $i \notin \nu(i)^{c}$ 인
   $j$, 즉 $j \notin \nu(i)$ 에 대해서는 $J_{j,i} = 0$ 이다($i$ 가 $j$ 의 조상이 아니므로).
   따라서 합의 범위를 $j = 1, \dots, n$ 으로 넓혀도 같고, $J_{j,i} = \partial v_j/\partial\dot q_i$
   이므로 (7)이다.
4. **일반화 힘임을 확인.** (7)은 "각 바디의 관성력 $f_j^{\text{net}}$ 를 $\dot q_i$ 방향의
   가상 속도장에 사영해 더한 것"이고, 이것이 d'Alembert 원리의 일반화 힘 정의다. 홀로노믹
   계에서 d'Alembert ⟺ Euler–Lagrange 이므로 (7)의 우변은
   $\frac{d}{dt}\partial T/\partial\dot q_i - \partial T/\partial q_i + \partial V/\partial q_i$ 와 같다.
   (생략: d'Alembert ⟹ Lagrange 의 표준 증명. MLS ch.4.2 또는 임의의 해석역학 교재.
   이 가교는 **[D1]** 이고, 수치적 확인은 재현 과제 조건 2·3 이 담당한다.)
5. **특수화.** $\dot q = 0$, $a_g = 0$ 이면 모든 $v_j = 0$ 이므로 편향 항이 사라지고
   $a_j = J_j\ddot q$ 다. (7)에 넣으면 $\tau = \big(\sum_j J_j^\top I_jJ_j\big)\ddot q$ 이고,
   $T = \frac{1}{2}\sum_j v_j^\top I_jv_j = \frac{1}{2}\dot q^\top\big(\sum_j J_j^\top I_jJ_j\big)\dot q$
   이므로 괄호 안이 바로 $M(q)$ 다. 즉 **RNEA 를 $n$ 번 호출하면 $M$ 의 모든 열을 얻는다** —
   비용 $\Theta(n^2)$ 이고, `c2-crba-aba` 의 CRBA 가 같은 $\Theta(n^2)$ 을 더 작은 상수로 한다.

**가설을 지우면**: H1(트리)을 지우면 1단계의 "각 $j$ 가 정확히 한 번"이 깨지고 부분나무 합
자체가 정의되지 않는다 — 폐루프는 승수를 도입해 따로 처리해야 한다
(`c2-constrained-dynamics`). H2($S_i$ 상수)를 지우면 R2 의 둘째 항에 $\dot S_i\dot q_i$ 가
살아남는다(이것이 다자유도·비표준 관절의 추가 항이고, $\dot S_i = v_i \times S_i$ 로 쓰면
(3)의 편향 항과 합쳐진다). H3 을 지우면 앞 레슨 R4 의 $\dot I = 0$ 가정이 깨져
$f_j^{\text{net}}$ 에 $\dot I_j v_j$ 항이 추가된다.

### R5 — $\Theta(n)$ 과 차수 최적성

**가설** H1: 기구 트리, 단일 자유도 관절 $n$ 개, 바디마다 $S_i$·$X_{T,i}$·$I_i$ 가 상수 크기
데이터다. H2: 실수 산술은 단위 비용이다.
**결론** C1: RNEA 의 시간·공간 비용은 $\Theta(n)$. C2: 직렬 연쇄에서 $\Omega(n)$ 이 하한이므로
RNEA 는 차수 최적이다.

**전략**: 상한은 바디당 연산 수를 세고, 하한은 의존성(모든 출력이 모든 입력에 의존)으로 친다.

1. **바디당 비용이 상수다.** 전진 패스에서 바디 $i$ 가 하는 일은 ⓐ $X_{J_i}(q_i)$ 조립
   (삼각함수 2회 + 고정 개수의 대입) ⓑ $^iX_{\lambda(i)}v_{\lambda(i)}$ 와
   $^iX_{\lambda(i)}a_{\lambda(i)}$ — $6\times6$ 행렬-벡터 곱 2회 ⓒ $S_i$ 스칼라배 2회
   ⓓ $v_i \times v_{J_i}$ — $6\times6$ 곱 1회 ⓔ $I_ia_i$ 와 $(v_i\times^{*})(I_iv_i)$ — 대칭
   곱 1회 + 일반 곱 2회. 후진 패스는 ⓕ $S_i^\top f_i$ 내적 1회 ⓖ $X^\top f_i$ 곱 1회와 덧셈.
   모두 **$6\times6$ 고정 크기**이므로 바디당 비용은 $n$ 과 무관한 상수 $c$ 다
   (관절 유형별 정확한 flop 표는 RBDA §5.3·Table 5.1).
2. **각 바디를 정확히 두 번 방문한다.** 바디 번호가 $\lambda(i) < i$ 로 위상 정렬되어 있으므로
   전진은 $i = 1 \dots n$, 후진은 $i = n \dots 1$ 의 **단순 루프**이고 재귀 스택도 필요 없다.
   방문 횟수는 정확히 $2n$. 저장하는 것은 $v_i, a_i, f_i, X_i$ 로 바디당 상수 — 공간도 $\Theta(n)$.
3. **상한.** 1·2 에서 총 비용 $\le 2cn = O(n)$. 또 전진 패스만으로도 최소 $n$ 회의 $X$ 조립이
   필요하므로 $\Omega(n)$, 즉 $\Theta(n)$.
4. **하한 (C2).** 출력 $\tau$ 가 $n$ 성분이므로 쓰기만으로 $\Omega(n)$ 이다. 더 강하게,
   직렬 연쇄에서 $M(q)$ 는 일반적으로 조밀하므로 **단 하나의** $\tau_k$ 를 정확히 계산하려 해도
   모든 $\ddot{q}_j$ 를 읽어야 한다 — 어떤 $\ddot q_j$ 를 읽지 않는 알고리즘은 $M_{kj} \ne 0$ 인
   입력 쌍을 구별할 수 없다. 따라서 $\tau$ 를 계산하는 임의의 알고리즘은 $\Omega(n)$ 이고
   RNEA 는 차수 최적이다.
5. **무엇이 최적이 아닌가.** 상수는 최적이 아니다. 관절 유형을 특수화하거나($S_i$ 가 희소),
   $X$ 를 조립하지 않고 성분식으로 전개하면 상수가 상당히 줄어든다. 또 **병렬** 모형에서는
   $\Theta(n)$ 이 최적이 아니다 — 분할정복으로 $O(\log n)$ 이 가능하다
   ([Featherstone 1999](https://doi.org/10.1177/02783649922066619)). 4단계의 하한은 **순차**
   모형의 것이다.

**가설을 지우면**: H1 에서 "단일 자유도"를 빼면 관절 $i$ 의 자유도 $n_i$ 가 비용에 들어와
$\Theta(\sum_i n_i)$ 가 되지만 $S_i$ 가 $6\times n_i$ 이므로 ⓕⓖ 가 $O(n_i)$ 로 늘고 차수는 유지된다.
H2(단위 비용 산술)를 빼면 — 예를 들어 임의 정밀도에서는 — 비트 복잡도로 다시 세야 한다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R2)** ⓐ 수반 공액 $X(u\times)X^{-1} = \big((Xu)\times\big)$ 를 증명하고 그것으로
(9)를 앞 레슨 (5)의 둘째 식에서 끌어내라. ⓑ 관절이 $n_i > 1$ 자유도일 때
($S_i \in \mathbb{R}^{6\times n_i}$, $\dot q_i \in \mathbb{R}^{n_i}$) (3)이
$a_i = {}^iX_{\lambda(i)}a_{\lambda(i)} + S_i\ddot q_i + \dot S_i\dot q_i + v_i \times v_{J_i}$ 로
바뀌는 것을 보이고, $S_i$ 가 바디 좌표에서 상수인 관절에서 $\dot S_i = 0$ 임을 확인하라.
*해답 스케치*: ⓐ 는 $u\times$ 를 "$\mathfrak{se}(3)$ 원소의 수반 작용"으로 보고
$X(\cdot)X^{-1}$ 이 리 대수 동형임을 쓰는 것이 가장 짧다. 성분 전개로도 되지만 길다.
ⓑ 는 (1)의 미분에서 $S_i\dot q_i$ 의 미분이 두 항이 되는 것만 추적하면 된다.

**P2 (유도, ★★, R2)** ⓐ 운동 외적의 반대칭성 $u \times w = -w \times u$ 를 (6)의 블록 형태에서
직접 보이라. ⓑ (4)를 증명하라: (2)를 $q_l$ 로 미분하고 (9)를 써서, $k$ 와 $l$ 중 어느 쪽이
조상인지에 따라 두 경우로 나누면 된다.
*해답 스케치*: ⓑ 는 일반성을 잃지 않고 $l$ 이 $k$ 의 자손 쪽에 있다고 두면
$\partial_{q_k}J_{i,l} = 0$ 이 되는 경우와 그렇지 않은 경우가 갈린다. $^iX_k$ 가 $q_l$ 에
의존하는 방식은 (9)뿐이고, 나오는 항이 정확히 $(J_{i,k}\times)J_{i,l}$ 이다. 부호를
$h = 10^{-6}$ 중앙 유한차분으로 **반드시** 교차 확인하라 — 이 부호는 손으로 틀리기 쉽다.

**P3 (증명, ★★★, R4·R5)** ⓐ R4 의 1단계("트리이므로 각 $j$ 가 정확히 한 번")가 폐루프에서
어떻게 깨지는지 구체적인 4절 링크로 보이고, 그때 (7)이 어떤 식으로 수정되어야 하는지 쓰라.
ⓑ R5 의 4단계 하한 논증이 **트리**(직렬이 아닌)에서는 그대로 성립하지 않는 이유를 쓰고,
서로 다른 분기의 $\tau_k$ 를 $o(n)$ 에 계산할 수 있는 트리 모양을 제시하라.
*전략 + 핵심 부등식*: ⓑ 는 깊이 1 의 성형(star) 트리, 즉 베이스에 $n$ 개의 바디가 각각 직접
붙은 경우를 보라. $M$ 이 블록 대각에 가까워지고 $\tau_k$ 가 $O(1)$ 개의 입력에만 의존한다.
전개는 숨긴다.

**P4 (계산, ★, R1–R4)** 2링크 평면 팔: 관절 모두 $z$ 축 회전, 링크 끝에 질점,
$m_1 = 1.5$, $l_1 = 0.6$ (바디 1 질량중심은 관절 1 에서 $x$ 로 $l_1$), $m_2 = 1.0$, $l_2 = 0.4$
(바디 2 좌표 원점은 바디 1 의 $x$ 로 $l_1$ 만큼, 질량중심은 거기서 $x$ 로 $l_2$),
$\bar{I}_{C,1} = \bar{I}_{C,2} = 0$, 중력은 베이스 $-y$ 방향 $9.81$.
$q = (0.3, -0.7)$, $\dot q = (0.5, 1.2)$, $\ddot q = (-0.4, 0.9)$ 에서 $\tau$, $M(q)$,
그리고 $\tau$ 의 세 성분 분해(중력만 / 편향만 / $M\ddot q$)를 구하라.
*정답* (허용오차 $10^{-9}$):
$\tau = (17.818552317079,\; 3.582165429254)$,
$M(q) = \begin{bmatrix} 1.427124249897 & 0.343562124948 \\ 0.343562124948 & 0.16 \end{bmatrix}$,
$g(q) = (17.672019777951,\; 3.614243340467)$,
$C\dot q = (0.408176326634,\; -0.038653061234)$,
$M\ddot q = (-0.261643787505,\; 0.006575150021)$.
*검산*: ⓐ 세 성분의 합이 $\tau$ 와 $10^{-12}$ 이내로 일치
ⓑ $M_{22} = m_2l_2^2 = 0.16$ 이 정확히 나와야 한다($q$ 에 무관)
ⓒ 닫힌 형태 $M_{11} = (m_1+m_2)l_1^2 + m_2l_2^2 + 2m_2l_1l_2\cos q_2$ 와 대조.

**P5 (구현, ★★, R1–R3)** 앞 레슨의 공간 벡터 함수들 위에 `rnea(model, q, qd, qdd, a_grav)` 를
쓰라. 모델은 `parent`, `jtype`, `Xtree`, `(m, c, Ic)` 로 주고 트리(분기 있음)를 지원해야 한다.
*루브릭*: ⓐ P4 의 수치를 $10^{-9}$ 이내로 재현 ⓑ 분기 트리(바디 2 개가 같은 부모)에서
$\tau$ 가 두 분기를 모두 반영 ⓒ $\ddot q$ 에 대한 **아핀성**을 단위 테스트로 확인:
$\tau(\ddot q_1 + \ddot q_2) - \tau(0) = [\tau(\ddot q_1) - \tau(0)] + [\tau(\ddot q_2) - \tau(0)]$,
오차 $< 10^{-12}$ ⓓ 중력을 $a_0 = -a_g$ 로 처리하고, 바디마다 $f^x$ 로 더한 구현과
$10^{-12}$ 이내로 일치 ⓔ 성분 순서와 $f_i$ 의 부호 규약이 docstring 에 적혀 있다.

**P6 (논문, ★★, R5)** Luh, Walker & Paul (1980)을 읽고 ⓐ 저자들이 "온라인(real-time) 계산"으로
무엇을 주장하고 그 주장이 어떤 하드웨어·어떤 로봇을 전제하는지 ⓑ 그들의 $O(n)$ 주장이
이 레슨 R5 의 어느 단계에 대응하고 **무엇은 주장하지 않는지** ⓒ 재현에 필요한 정보 중
빠진 것 3개를 각각 쓰라.
*루브릭*: ⓑ 에서 "바디당 비용이 상수"(상한)와 "차수 최적"(하한)을 구별하면 통과 —
1980년 논문은 하한을 다루지 않는다. ⓒ 에서 좌표계 규약·관성 매개변수의 출처·타이밍 측정
방법 중 둘 이상을 짚으면 통과. "코드가 없다"만 쓰면 미달.

## 논문 읽기

**필독 2편.** 한 편은 원전(1980), 한 편은 20년 뒤의 지형도(2000)다. 둘을 **같은 질문지로**
읽어 "무엇이 그 20년에 바뀌었는지"를 스스로 쓰는 것이 이 레슨의 읽기 목표다. 각 논문에 아래
고정 질문 10개로 1페이지 노트를 쓴다(`lesson-standard.md` §5). 3-pass 로 읽고 3번째 패스에서
질문 4·7·9 를 집중 공략한다.

1. **Luh, Walker & Paul, "On-Line Computational Scheme for Mechanical Manipulators"
   (1980, ASME J. Dyn. Syst. Meas. Control)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1115/1.3149599>
   어느 절을 왜 읽는가: 전진 운동학 재귀와 후진 힘 재귀를 세우는 절. 이 레슨 (1)(3)(5)와
   1:1 로 대응하지만 표기가 $3\times3$ 회전과 벡터로 쪼개져 있어 **같은 알고리즘이 공간 벡터로
   얼마나 짧아지는지**가 드러난다. 비용을 논하는 절도 반드시 읽는다.
   추가 질문: ⓐ 저자들의 재귀식을 이 레슨의 $^iX_{\lambda(i)}$ 표기로 옮겨 쓰면 몇 줄이 되는가?
   ⓑ 저자들이 중력을 어떻게 처리하는가 — $a_0 = -a_g$ 트릭과 같은가?
   ⓒ 같은 권의 정오표(<https://doi.org/10.1115/1.3139629>)는 무엇을 고치는가?
2. **Featherstone & Orin, "Robot dynamics: equations and algorithms" (2000, ICRA)** — 역할:
   `서베이(survey)`. <https://doi.org/10.1109/ROBOT.2000.844153>
   어느 절을 왜 읽는가: 역동역학·순동역학·질량행렬 알고리즘을 한 틀에서 비교하는 절.
   이 레슨의 R5 와 다음 레슨(CRBA·ABA)의 복잡도 지형이 여기 있다.
   추가 질문: ⓐ 저자들이 제시하는 비용 비교에서 $n$ 이 작을 때($n \le 6$) 순서가 뒤집히는
   지점이 있는가, 그 교차점은 무엇이 결정하는가? ⓑ 2000년 이후 바뀐 것은 무엇인가
   (해석적 미분, GPU·벡터화, 접촉) — 이 서베이가 **지금** 틀린 곳을 1개 찾으라.

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R1 (수치 검증).** 계산 예산: 노트북 CPU 1코어, 2분 이내, numpy(조건 2 에 sympy 또는
jax 중 하나). 메모리 200MB 이내.

P5 의 `rnea` 가 아래 **네 조건을 모두** 만족해야 통과다. 모든 난수는 시드를 고정한다.

1. **2링크 닫힌 형태와의 일치** — P4 의 모델에 대해 무작위 $(q, \dot q, \ddot q)$ $10^4$ 개
   (성분을 $[-\pi, \pi] \times [-3, 3] \times [-3, 3]$ 에서 균등 추출)에서
   $$
   \max_k \frac{|\tau_k^{\text{RNEA}} - \tau_k^{\text{closed}}|}{1 + \lVert \tau^{\text{closed}}\rVert_\infty} < 10^{-12}.
   $$
   닫힌 형태는 2링크 질점 모델의 교과서 식을 **직접 유도해 쓴다**(복사하지 말 것 — 유도가
   P4 의 검산 ⓒ 다).
2. **7-DOF 에서 정확한 Euler–Lagrange 와의 일치** — 7자유도 직렬 팔(관절 축 $z,y,z,y,z,y,z$,
   링크 오프셋과 관성은 스크립트가 생성)에 대해, $T = \frac{1}{2}\dot q^\top M(q)\dot q$ 와
   $V(q)$ 를 **기호 미분(sympy) 또는 자동 미분(jax)** 으로 미분해 얻은
   $\tau^{\text{EL}} = \frac{d}{dt}\partial T/\partial\dot q - \partial T/\partial q + \partial V/\partial q$ 와
   $$
   \max_k \frac{|\tau_k^{\text{RNEA}} - \tau_k^{\text{EL}}|}{1 + \lVert\tau^{\text{EL}}\rVert_\infty} < 10^{-9}
   $$
   를 무작위 상태 $10^2$ 개에서 만족해야 한다. $M(q)$ 는 RNEA 와 **독립적으로**
   $M = \sum_j J_j^\top I_j J_j$ 로 만든다(야코비안 경로).
3. **유한차분 Euler–Lagrange 와의 일치 + $h$ 스윕** — 같은 7-DOF 에서 $M$ 과 $V$ 의 미분을
   중앙 유한차분으로 계산한 $\tau^{\text{FD}}$ 에 대해, $h = 10^{-5}$ 에서
   $$
   \max_k \frac{|\tau_k^{\text{RNEA}} - \tau_k^{\text{FD}}|}{1 + \lVert\tau^{\text{RNEA}}\rVert_\infty} < 10^{-7}
   $$
   를 만족하고, $h \in \{10^{-3}, \dots, 10^{-8}\}$ 스윕에서 오차가 **V 자**(최소가
   $10^{-5}$ 근방)를 그려야 한다.
   > 참고: 이 조건이 조건 2보다 느슨한 것은 알고리즘이 아니라 **유한차분의 한계** 때문이다.
   > 저자 환경에서 측정한 7-DOF 절대오차는 $h = 10^{-5}$ 에서 $8.9\times10^{-10}$,
   > $h = 10^{-6}$ 에서 $7.9\times10^{-9}$, $h = 10^{-7}$ 에서 $1.4\times10^{-7}$ 이었다.
   > blueprint 의 "1e-9 이내"는 조건 2(정확한 미분)에만 적용된다.
4. **(4)의 비적분성을 수치로 확인** — 같은 7-DOF 에서 무작위 $q$ 와 모든 $(i, k, l)$ 조합에 대해
   $$
   \max_{i,k,l}\big\lVert \big(\partial_{q_l}J_{i,k} - \partial_{q_k}J_{i,l}\big) - \big(J_{i,k}\times\big)J_{i,l} \big\rVert_\infty < 10^{-8}
   $$
   ($h = 10^{-6}$ 중앙 유한차분). 이어서 **부호를 뒤집은** 가설
   $-\big(J_{i,k}\times\big)J_{i,l}$ 로 같은 양을 계산해 그 값이 $10^{-1}$ 이상으로 **크다**는
   것을 보여라 — 부호가 실제로 결정되어 있음을 확인하는 단계다.
   이어서 편향 항을 **빼먹은** 구현(3)의 $v_i\times v_{J_i}$ 를 생략)으로 P4 의 상태를 계산해
   $\lVert\tau^{\text{bug}} - \tau\rVert_\infty > 10^{-2}$ 이고 $\dot q = 0$ 에서는 차가
   $10^{-14}$ 이하로 사라짐을 보여라.

**입력 데이터**: 외부 데이터 불필요. 7-DOF 모델의 링크 오프셋·질량·관성은 고정 시드
(`np.random.default_rng(7)`)로 생성하고, 관성행렬은 $0.02\,AA^\top + 0.05\,\mathbb{1}$ 꼴로
만들어 양정치와 삼각부등식을 만족시킨다.

**비교 대상** (최소 1개):
- 1순위: 조건 2 의 야코비안 기반 Euler–Lagrange 경로(완전히 독립된 두 번째 구현).
- 2순위: 조건 1 의 2링크 닫힌 형태(손으로 유도한 식).
- 선택 검증(없어도 통과): `pinocchio` 의 `pin.rnea` 와 $10^{-10}$ 이내 일치(성분 순서가
  선형 먼저임에 주의), 또는 Featherstone 의 `ID`(Octave)와 대조.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| $\dot q = 0$ 에서만 맞는다 | (3)의 $v_i \times v_{J_i}$ 를 빼먹었다 | P4 상태에서 두 성분의 차가 **같은 값**(여기서는 $0.0927673470$)으로 나오는지 본다 |
| 중력만 틀리다 | $a_0 = -a_g$ 의 부호, 또는 $a_g$ 를 바디 좌표로 옮기지 않았다 | $\dot q = \ddot q = 0$ 에서 $\tau$ 가 $\partial V/\partial q$ (유한차분)와 맞는지 본다 |
| 2링크는 맞고 7-DOF 는 틀리다 | 관절 축이 $z$ 가 아닌 관절의 $X_{J}$ 조립, 또는 $X_{T,i}$ 적용 순서 | 모든 관절을 $\dot q_i = 1$, 나머지 0 으로 두고 $v_i$ 를 유한차분 정기구학과 대조 |
| 분기 트리에서 틀리다 | 후진 재귀에서 자식의 힘을 $X^\top$ 대신 $X$ 로 올렸다 | 자식 2개를 같은 부모에 달고 한쪽 자식의 질량만 0 으로 두어 대칭성을 본다 |
| 토크 부호가 전부 반대 | $f_i$ 의 방향 규약(부모→자식 vs 자식→부모) | 1링크 진자를 정지 상태로 두고 중력 토크의 부호를 손으로 확인한다 |
| 아핀성 테스트만 실패 | 편향 항 계산에 $\ddot q$ 가 섞여 들어갔다(예: $a_i$ 로 $v_i\times$ 를 만들었다) | $\ddot q$ 를 2배로 하고 $\tau - \tau(0)$ 가 정확히 2배인지 본다 |

## 열린 문제

- **(열린 문제) 접촉이 섞인 계에서 역동역학이 잘 정의되는가** — RNEA 는 $(q, \dot q, \ddot q)$ 가
  주어지면 $\tau$ 가 **유일**하다는 사실에 기대고, 그 사실은 트리 구조에서만 성립한다. 접촉이
  들어오면 같은 $\ddot q$ 를 만드는 $(\tau, \lambda)$ 가 여러 개이거나 하나도 없을 수 있고
  (`c2-contact-dynamics` 의 상보성), "역동역학"이라는 문제 자체가 다시 정의되어야 한다.
  현재 접근: 접촉력을 포함한 QP 로 보는 정식화
  ([Todorov 2014](https://doi.org/10.1109/ICRA.2014.6907751)), 상보성 제약을 둔 궤적 최적화.
  비어 있는 자리: 접촉 모드가 바뀌는 순간에도 연속적인 역동역학 정의.
- **(열린 문제) 모델 오차가 지배하는 영역에서 $\Theta(n)$ 의 의미** — RNEA 는 주어진 관성
  매개변수에 대해 기계 정밀도로 정확하지만, 실제 로봇에서 $\tau$ 의 오차는 거의 전부
  **모델 오차**(관절 마찰, 하모닉 드라이브의 유연성, 케이블, 온도 드리프트)에서 온다.
  어느 정확도 이상은 알고리즘이 아니라 식별과 보상의 문제이고, "어디까지가 모델 오차인가"를
  사전에 가늠하는 방법이 없다. 현재 접근: 물리적 일관성을 제약으로 둔 식별
  ([Wensing et al. 2018](https://doi.org/10.1109/LRA.2017.2729659)), 잔차 학습.
  이 질문은 `c2-dynamics-derivatives-sysid` 에서 정면으로 다룬다.
- **(열린 문제) 병렬·이종 하드웨어에서의 하한** — R5 의 하한은 순차 모형의 것이다. 분할정복은
  $O(\log n)$ 을 주지만 상수가 커서 실제 로봇 크기($n \le 30$)에서는 순차 RNEA 가 더 빠르다.
  GPU·SIMD 에서 "어떤 $n$ 과 어떤 배치(batch) 크기부터 병렬이 이기는가"에 대한 모형이 없고,
  궤적 최적화가 수천 개 상태의 RNEA 를 동시에 부르는 요즘 워크로드에서 이것이 실제 병목이다.
  현재 접근: 배치 동역학의 벡터화와 해석적 미분
  ([Carpentier & Mansard 2018](https://doi.org/10.15607/RSS.2018.XIV.038)),
  [Featherstone 1999](https://doi.org/10.1177/02783649922066619) 의 분할정복.
  비어 있는 자리: 배치 크기·$n$·메모리 대역폭을 함께 담는 비용 모형.

## 개념 점검

`rc quiz c2-rnea-inverse-dynamics` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c2-rnea-inverse-dynamics-quiz
questions:
  - id: q1
    type: single
    prompt: "가속도 재귀 (3)의 마지막 항 $v_i \\times v_{J_i}$ 는 어디서 오는가?"
    choices:
      - "관절의 마찰을 모델링한 항"
      - "부모→자식 좌표 변환 $^{i}X_{\\lambda(i)}$ 가 시간에 따라 변하기 때문"
      - "중력을 $a_0 = -a_g$ 로 처리하기 때문"
      - "공간 관성이 대칭이 아니기 때문"
    answer: 1
    explanation: "$\\frac{d}{dt}{}^{i}X_{\\lambda(i)} = -(v_{J_i}\\times)\\,{}^{i}X_{\\lambda(i)}$ 를 (1)에 넣으면 $-(v_{J_i}\\times)(v_i - v_{J_i}) = v_i \\times v_{J_i}$ 가 남는다. 이 항은 $\\ddot{q}$ 와 무관하고 $\\dot{q}$ 에 2차인 편향 항이고, 코리올리·원심 토크의 전부다. 빼먹으면 $\\dot{q} = 0$ 인 테스트만 통과한다."
    concept: { front: "(3)의 편향 항 $v_i \\times v_{J_i}$ 의 출처", back: "변환 $^{i}X_{\\lambda(i)}$ 의 시간 미분. $\\ddot{q}$ 무관, $\\dot{q}$ 2차 — 코리올리 항의 전부" }
  - id: q2
    type: single
    prompt: "후진 재귀에서 자식의 힘 $f_j$ 를 부모 좌표로 옮길 때 쓰는 것은?"
    choices:
      - "$^{\\lambda(j)}X_j$ (운동 변환)"
      - "$({}^{j}X_{\\lambda(j)})^{\\top}$ (= 힘 변환 $^{\\lambda(j)}X^{*}_j$)"
      - "$({}^{\\lambda(j)}X_j)^{-1}$"
      - "$^{j}X_{\\lambda(j)}$"
    answer: 1
    explanation: "$f_j$ 는 힘 공간 $F^6$ 의 원소이므로 힘 변환 $^{\\lambda(j)}X^{*}_j$ 가 필요하고, 앞 레슨 (2)로 그것이 $({}^{j}X_{\\lambda(j)})^{\\top}$ 다. 코드의 `Xup[j].T @ f[j]` 가 이것이다 — 역행렬을 계산하지 않는다. 운동 변환을 쓰면 평행이동이 섞이는 순간 틀린다."
    concept: { front: "후진 힘 재귀의 변환", back: "$^{\\lambda(j)}X^{*}_j = ({}^{j}X_{\\lambda(j)})^{\\top}$ — 전치 한 번, 역행렬 없음" }
  - id: q3
    type: short
    prompt: "$\\dot{q} = 0$, 중력 없음, $\\ddot{q} = e_k$ 로 RNEA 를 부르면 무엇을 얻는가? (한 단어 또는 기호로)"
    answer: ["M의 k번째 열", "질량행렬의 k열", "M e_k", "Me_k", "mass matrix column", "k-th column of M", "질량행렬 k번째 열"]
    explanation: "$\\dot{q} = 0$ 이면 모든 $v_j = 0$ 이라 편향 항이 사라지고 $a_j = J_j\\ddot{q}$ 다. (7)에 넣으면 $\\tau = (\\sum_j J_j^{\\top}I_jJ_j)e_k = M(q)e_k$. 그래서 RNEA 를 $n$ 번 부르면 $M$ 전체를 $\\Theta(n^2)$ 에 얻는다 — CRBA 가 같은 차수를 더 작은 상수로 한다."
    concept: { front: "RNEA 로 질량행렬 뽑기", back: "$\\dot{q}=0$, 중력 0, $\\ddot{q}=e_k$ → $M(q)e_k$. $n$ 번 호출 = $\\Theta(n^2)$" }
  - id: q4
    type: truefalse
    prompt: "공간 야코비안은 $\\partial_{q_l} J_{\\cdot k} = \\partial_{q_k} J_{\\cdot l}$ 를 만족한다(즉 적분 가능하다)."
    answer: false
    explanation: "(4)가 그 대칭이 정확히 리 괄호만큼 깨진다고 말한다: $\\partial_{q_l}J_{i,k} - \\partial_{q_k}J_{i,l} = (J_{i,k}\\times)J_{i,l}$. 대칭이었다면 코리올리 항이 좌표 변환만으로 사라졌을 것이다. 7-DOF 무작위 자세에서 유한차분으로 확인하면 $10^{-10}$ 수준에서 (4)가 성립한다."
    concept: { front: "공간 야코비안의 비적분성", back: "$\\partial_{q_l}J_{\\cdot k} - \\partial_{q_k}J_{\\cdot l} = [J_{\\cdot k}, J_{\\cdot l}] \\ne 0$ — 코리올리 항의 기원" }
  - id: q5
    type: multiple
    prompt: "RNEA 가 $\\Theta(n)$ 이라는 결론에 **실제로 쓰이는** 사실을 모두 고르라."
    choices:
      - "바디당 연산이 $6\\times6$ 고정 크기여서 $n$ 과 무관하다"
      - "$\\lambda(i) < i$ 로 번호를 매기면 전진·후진이 단순 루프다"
      - "질량행렬 $M$ 을 명시적으로 만들지 않는다"
      - "관절이 모두 회전 관절이다"
    answer: [0, 1, 2]
    explanation: "바디당 상수 비용 + 각 바디 2회 방문이 상한 $O(n)$ 을 준다. $M$ 이나 $C$ 를 만들지 않는 것이 핵심인데, 만들면 그것만으로 $\\Theta(n^2)$ 이상이다. 관절 유형은 상수에만 영향을 주고 차수와는 무관하다 — 다자유도 관절도 $\\Theta(\\sum_i n_i)$ 로 차수가 유지된다."
    concept: { front: "RNEA $\\Theta(n)$ 의 근거", back: "바디당 상수 비용 + 2회 방문 + $M$·$C$ 를 만들지 않음. 관절 유형은 상수만 바꾼다" }
```

## 이 단계 공부법

1. **앞 레슨의 네 식만 꺼내 둔다 (15분)** — $f = Ia + (v\times^{*})Iv$,
   $\frac{d}{dt}{}^BX_A = -{}^BX_A(v\times)$, $v\times^{*} = -(v\times)^\top$,
   $^BX_A^{*} = ({}^AX_B)^\top$. 이 레슨의 모든 유도가 이 넷의 조합이다.
2. **트리 표기를 그림으로 그린다 (20분)** — 바디 5개쯤의 분기 트리를 그리고 $\lambda$, $\mu$,
   $\nu$, 그리고 각 바디의 $J_i$ 희소 패턴을 직접 칠해 보라. (2)의 희소 구조를 손으로 보면
   다음 레슨의 CRBA 가 거의 자명해진다.
3. **R2 를 백지에서 다시 쓴다 (60분)** — (1)을 적고 (9)만 기억한 채 (3)까지 간다. 막히는
   지점은 거의 항상 $^iX_{\lambda(i)}v_{\lambda(i)} = v_i - v_{J_i}$ 로 바꿔 넣는 대입이다.
   끝나면 **(4)를 유한차분으로 직접 확인**하라(문제 P2 ⓑ) — 이 한 번의 수치 실험이 "코리올리
   항은 왜 있는가"를 영구히 해결한다.
4. **R4 의 1·2·3 단계를 외우지 말고 세 번 쓴다 (50분)** — 재귀를 펼치고, 전치를 옮기고,
   야코비안 열로 알아보는 세 동작이다. 4단계(d'Alembert 가교)는 **지금 증명하지 않는다** —
   가교가 [D1]이라는 것을 알고 넘어가고, 재현 과제 조건 2 로 수치 확인하는 것이 이 레슨의 설계다.
5. **먼저 틀리게 구현한다 (60분)** — P5 를 쓸 때 ⓐ 편향 항 생략 ⓑ $X^\top$ 대신 $X$
   ⓒ $a_0 = +a_g$ 세 버전을 만들고 재현 과제의 어느 조건이 어떻게 깨지는지 표로 적어라.
   진단표의 여섯 줄은 전부 이 실험에서 나왔다.
6. **재현 과제를 끝낸다 (105분)** — 조건 2 의 기호·자동 미분 경로를 먼저 만들어라. 그것이
   있으면 이후 모든 레슨(CRBA·ABA·제약·접촉)의 정답지가 된다. 조건 3 의 $h$ 스윕 V 곡선은
   **반드시** 그려 보라 — "1e-9 가 왜 유한차분으로는 안 되는가"를 눈으로 봐야 수용 기준을
   읽을 수 있게 된다.
7. **논문 2편을 20년 간격으로 읽는다 (120분)** — Luh 1980 을 먼저 읽고 재귀식을 공간 벡터로
   옮겨 적는다. 그 다음 Featherstone & Orin 2000 에서 그 알고리즘이 어떤 지형의 한 점인지
   본다. 2000년 서베이가 지금 틀린 곳 1개를 찾는 것(P6 ⓑ)이 이 레슨의 연구 훈련이다.
8. **무엇을 못 하는지로 끝낸다 (20분)** — 열린 문제 중 접촉 쪽을 골라, "역동역학이 유일하다"는
   전제가 어디서 깨지는지 한 문단으로 쓴다. 그 문단이 `c2-contact-dynamics` 의 도입부가 된다.

**통과 기준**: 백지에서 (1)(3)(5)(6)을 쓸 수 있고, R4 의 1–3단계와 R5 의 상한·하한을 말할 수
있고, 재현 과제 네 조건을 통과하는 `rnea` 를 갖고 있고, 논문 2편의 1페이지 노트가 있다.
