---
id: c2-spatial-vector-algebra
title: 공간 벡터 대수
summary: >-
  강체 동역학을 6차원 운동 공간(motion space)과 힘 공간(force space)의 쌍대 쌍으로 다시 쓰고,
  공간 관성의 변환 법칙과 운동·힘 외적을 유도하고, 공간 관성의 시간 미분에서 코리올리·원심
  항이 분리되어 나오는 것을 증명 수준에서 다룬다. "공간 가속도는 점의 가속도가 아니다"라는
  가장 흔한 오류의 원인까지 간다.
objectives:
  - 운동 공간과 힘 공간이 쌍대임을 일률(power) 불변성에서 유도하고 힘 변환이 $X^{-\top}$ 임을 보일 수 있다.
  - 공간 관성 행렬을 운동량 정의에서 직접 조립하고 좌표 변환 법칙을 유도할 수 있다.
  - 운동 외적 $v\times$ 와 힘 외적 $v\times^{*}$ 의 관계를 쓰고 변환 행렬의 시간 미분을 계산할 수 있다.
  - $\dot{I} = v\times^{*} I - I\, v\times$ 를 증명하고 여기서 Newton-Euler 의 편향 항을 분리할 수 있다.
  - 공간 가속도와 물체 고정점의 고전 가속도의 차이를 설명하고 혼동이 만드는 오류를 지목할 수 있다.
prerequisites: [c1-so3-se3-exponential]
difficulty: 4
estimated_minutes: 420
tags: [multibody-dynamics, spatial-vectors, plucker, rigid-body, research]
activities:
  - id: c2-spatial-vector-algebra-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c2-spatial-vector-algebra-papers
    kind: reading
    title: 필독 논문 2편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 120
  - id: c2-spatial-vector-algebra-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 120
  - id: c2-spatial-vector-algebra-reproduction
    kind: exercise
    title: 재현 과제 — 공간 관성 변환과 편향 항 검증 (R1)
    estimated_minutes: 75
  - id: c2-spatial-vector-algebra-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Featherstone, Rigid Body Dynamics Algorithms (2008)"
    url: https://doi.org/10.1007/978-0-387-74315-8
    kind: book
    note: ch.2 (Spatial Vector Algebra). 이 레슨의 1순위 교재. 표기 규약을 여기에 맞춘다.
  - title: "Lynch & Park, Modern Robotics"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: ch.8.1-8.2 (Lagrangian/Newton-Euler 동역학). 같은 결과를 트위스트·렌치 표기로 본다. 전문 PDF 무료.
  - title: "Featherstone — A Beginner's Guide to 6-D Vectors (Part 1) (2010)"
    url: https://doi.org/10.1109/MRA.2010.937853
    kind: article
    note: 필독 1. 6D 벡터가 왜 두 개의 다른 공간인지, 좌표계 없이 쓰는 법.
  - title: "Featherstone — A Beginner's Guide to 6-D Vectors (Part 2) (2010)"
    url: https://doi.org/10.1109/MRA.2010.939560
    kind: article
    note: 필독 2. 공간 관성·외적·미분 규칙과 알고리즘으로의 연결.
  - title: "Featherstone — Plücker basis vectors (2006, ICRA)"
    url: https://doi.org/10.1109/ROBOT.2006.1641982
    kind: article
    note: 권장. 쌍대 기저를 명시적으로 쓰는 방식 — 좌표 변환 규칙이 왜 두 종류인지가 또렷해진다.
  - title: "Featherstone — Spatial vector and rigid-body dynamics software"
    url: https://royfeatherstone.org/spatial/
    kind: other
    note: 권장. 저자가 공개한 공간 벡터 구현(Matlab/Octave). 재현 과제의 교차 검증용.
---

# 공간 벡터 대수

## 전제와 기호

### 모듈 자가 진단 (self-diagnostic)

C2 는 C1 을 **권장** 선수로 둔다(플랫폼이 잠그지는 않는다). 아래 6문항을 종이에서 10분 안에
답할 수 없으면 해당 자료를 먼저 보라 — 이 모듈의 유도는 전부 이 여섯 가지를 조합한 것이다.

1. $\hat{\omega}x = \omega \times x$ 일 때 $\hat{\omega}^\top$ 과 $\widehat{R\omega}$ 를
   $\hat{\omega}$, $R$ 로 각각 쓰라. (→ `c1-so3-se3-exponential`, 식 (1) 주변)
2. $R(t) \in SO(3)$ 일 때 $\dot{R}R^\top$ 이 반대칭임을 보이라. 그 반대칭 행렬의 벡터는 무엇인가?
3. 질량 $m$, 질량중심 $c$, 질량중심 기준 관성 $\bar{I}_C$ 인 강체의 원점 기준 관성행렬을
   평행축 정리로 쓰라. (→ `robotics-expert` M7 또는 MR ch.8.2)
4. 강체 위의 두 점 $P$, $Q$ 의 속도 관계 $v_P = v_Q + \omega \times (p - q)$ 를 유도하라.
5. 라그랑지안 $L = T - V$ 에서 Euler-Lagrange 식을 쓰고, $T = \frac{1}{2}\dot{q}^\top M(q)\dot{q}$
   일 때 $\frac{d}{dt}\frac{\partial T}{\partial \dot{q}}$ 를 전개하라.
6. $A \in \mathbb{R}^{6\times6}$ 가 가역일 때 $\frac{d}{dt}(A^{-1}) = -A^{-1}\dot{A}A^{-1}$ 을 유도하라.

이 레슨 자체는 2·6 번을 집중적으로 쓴다. 1·3·4 는 유도 안에서 다시 등장하고, 5 는 다음 레슨
(`c2-rnea-inverse-dynamics`)에서 RNEA 와 Lagrange 유도의 동등성을 볼 때 쓴다.

### 기호

모듈 전체에서 **Featherstone 규약**을 쓴다(RBDA ch.2). 가장 중요한 선택 두 가지:

- **6D 벡터의 성분 순서는 각(angular) 먼저**다: $v = (\omega; v_O)$, $f = (n_O; f)$.
  Modern Robotics 의 트위스트 $\mathcal{V} = (\omega, v)$ 와 같은 순서이고,
  일부 문헌(특히 수치 라이브러리)은 선형 먼저를 쓴다 — 외부 코드와 맞출 때 **가장 먼저 확인할 것**.
- **운동과 힘은 서로 다른 벡터공간**이다. 같은 $\mathbb{R}^6$ 으로 구현하지만 변환 규칙이 다르다.

| 기호 | 뜻 |
|---|---|
| $M^6$ | 운동 공간(motion space). 공간 속도·가속도·관절축이 사는 6차원 공간 |
| $F^6$ | 힘 공간(force space). 공간 힘·운동량·충격량이 사는 $M^6$ 의 쌍대공간 |
| $v = (\omega; v_O) \in M^6$ | 공간 속도. $\omega$ 는 각속도, $v_O$ 는 **좌표 원점에 순간적으로 겹친 물체 고정점**의 속도 |
| $f = (n_O; f_\ell) \in F^6$ | 공간 힘. $n_O$ 는 원점에 대한 모멘트, $f_\ell$ 은 합력 |
| $a = \dot{v} \in M^6$ | 공간 가속도. **고정 좌표에서 $v$ 를 성분별로 미분한 것** (§R5 주의) |
| $h = (h_\omega; h_\ell) \in F^6$ | 공간 운동량. $h_\ell$ 은 선운동량, $h_\omega$ 는 원점 기준 각운동량 |
| $I \in \mathbb{R}^{6\times6}$ | 공간 관성(spatial inertia). $M^6 \to F^6$ 의 대칭 양정치 사상 |
| $^B X_A$ | 운동 벡터의 좌표 변환 $M^6 \to M^6$: $v_B = {}^BX_A\,v_A$ |
| $^B X_A^{*}$ | 힘 벡터의 좌표 변환 $F^6 \to F^6$: $f_B = {}^BX_A^{*}\,f_A$ |
| $E = {}^B R_A \in SO(3)$, $p \in \mathbb{R}^3$ | 프레임 $B$ 의 자세와 원점. $p$ 는 **$A$ 좌표로 쓴 $B$ 의 원점** |
| $\hat{x}$ | $x \in \mathbb{R}^3$ 의 반대칭 행렬. $\hat{x}y = x \times y$, $\hat{x}^\top = -\hat{x}$ |
| $v\times$, $v\times^{*}$ | 운동 외적과 힘 외적 ($6\times6$ 행렬, §R3) |
| $\mathbb{1}_3$ | $3\times3$ 단위행렬 |

전제: $A$, $B$ 는 둘 다 **동일한 순간에** 정의된 좌표계이고, 물체는 질량 분포가 변하지 않는
강체다. 변형체·가변 질량은 이 모듈 밖이다.

C1 에서 쓴 두 항등식을 계속 쓴다(직접 전개해 확인하라):

$$\hat{x}\hat{x}^\top = -\hat{x}^2 = \lVert x \rVert^2 \mathbb{1}_3 - xx^\top, \qquad \widehat{Rx} = R\hat{x}R^\top \;\; (R \in SO(3)). \tag{1}$$

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (운동·힘 공간의 쌍대성) [D2]** — 일률(power) $p = f \cdot v$ 는 좌표계와 무관한 스칼라다.
  쌍대 기저를 쓰면 $p = f^\top v$ 로 계산되고, 이 **한 가지 요구**가 힘의 변환 규칙을 결정한다:
  $$
  f_B^\top v_B = f_A^\top v_A \;\; \forall v_A \in M^6
    \quad\Longrightarrow\quad {}^BX_A^{*} = \big({}^BX_A\big)^{-\top} = \big({}^AX_B\big)^{\top}. \tag{2}
  $$
  명시적으로, $E = {}^BR_A$ 와 $p$ (프레임 $B$ 원점, $A$ 좌표)에 대해
  $$
  {}^BX_A = \begin{bmatrix} E & 0 \\ -E\hat{p} & E \end{bmatrix}, \qquad
  {}^BX_A^{*} = \begin{bmatrix} E & -E\hat{p} \\ 0 & E \end{bmatrix}. \tag{3}
  $$
- **R2 (공간 관성과 그 변환 법칙) [D2]** — 질량 $m$, 질량중심 $c$ (현재 좌표계 기준), 질량중심
  기준 회전 관성 $\bar{I}_C$ 인 강체에 대해 $h = Iv$ 이고
  $$
  I = \begin{bmatrix} \bar{I}_C + m\,\hat{c}\hat{c}^\top & m\,\hat{c} \\[2pt] m\,\hat{c}^\top & m\,\mathbb{1}_3 \end{bmatrix}, \qquad
  {}^BI = {}^BX_A^{*}\;{}^AI\;{}^AX_B = \big({}^AX_B\big)^\top {}^AI \;{}^AX_B. \tag{4}
  $$
  관성은 $M^6 \to F^6$ 사상이므로 **합동 변환(congruence)**으로 옮겨진다 — 운동 변환의
  전치를 양쪽에 쓰는 유사 변환 $X^{-1}IX$ 가 **아니다**.
- **R3 (운동 외적·힘 외적과 변환의 시간 미분) [D2]** — 프레임 $B$ 가 프레임 $A$ 에 대해 공간
  속도 $v$ (A 좌표)로 움직이면
  $$
  \frac{d}{dt}\,{}^AX_B = (v\times)\;{}^AX_B, \qquad
  \frac{d}{dt}\,{}^BX_A = -\,{}^BX_A\,(v\times), \qquad
  \frac{d}{dt}\,{}^AX_B^{*} = (v\times^{*})\;{}^AX_B^{*}, \tag{5}
  $$
  여기서 $v = (\omega; v_O)$ 에 대해
  $$
  v\times = \begin{bmatrix} \hat{\omega} & 0 \\ \hat{v}_O & \hat{\omega}\end{bmatrix} \in \mathbb{R}^{6\times6},
  \qquad v\times^{*} = \begin{bmatrix} \hat{\omega} & \hat{v}_O \\ 0 & \hat{\omega}\end{bmatrix} = -\,(v\times)^\top. \tag{6}
  $$
  $v\times$ 는 $M^6$ 에, $v\times^{*}$ 는 $F^6$ 에 작용한다. 둘은 **같은 연산의 다른 표현이 아니라
  쌍대 공간에서의 서로 다른 작용**이고, (2)와 같은 이유로 부호·전치가 붙는다.
- **R4 (공간 관성의 시간 미분과 편향 항의 분리) [D3]** — 고정 좌표계에서 본 강체의 공간 관성은
  시간에 따라 변하고
  $$
  \dot{I} = (v\times^{*})\,I - I\,(v\times). \tag{7}
  $$
  따라서 $f = \dot{h} = \dot{I}v + I\dot{v}$ 에서 $v\times v = 0$ 이므로 Newton-Euler 방정식이
  $$
  f = I\,a + (v\times^{*})\,I\,v \tag{8}
  $$
  로 쪼개진다. 둘째 항은 가속도와 무관한 **편향 항(bias force)**이고 $v^\top\!\big((v\times^{*})Iv\big) = 0$
  이므로 **일을 하지 않는다** — 이것이 코리올리·원심 항의 좌표 무관 정의다.
- **R5 (공간 가속도는 점의 가속도가 아니다) [D2]** — $a = \dot{v} = (\dot{\omega}; \dot{v}_O)$ 이고,
  현재 좌표 원점에 겹친 물체 고정점의 **고전 가속도**는
  $$
  a_{\text{classical}} = \dot{v}_O + \omega \times v_O \;\ne\; a_\ell \;(= \dot{v}_O). \tag{9}
  $$
  두 개는 $\omega \times v_O$ 만큼 다르다. (8)에 $a_{\text{classical}}$ 을 넣으면 틀린 토크가
  나오는데, 원점이 질량중심에 있고 $v_O = 0$ 인 특수한 경우에는 우연히 맞아서 테스트를 통과한다. **[D2]**

## 유도

### R1 — 쌍대성이 힘의 변환 규칙을 결정한다

출발점은 물리적 사실 하나다: **일률은 좌표계를 바꿔도 변하지 않는다.** 강체에 작용하는 공간 힘
$f$ 가 공간 속도 $v$ 로 움직이는 물체에 공급하는 일률은 관찰자의 좌표 선택과 무관하다.

$M^6$ 에 기저 $\{m_i\}$ 를 잡고, $F^6$ 에는 **쌍대 기저** $\{f^j\}$, 즉 $f^j \cdot m_i = \delta^j_i$ 를
만족하는 기저를 잡는다. 그러면 성분으로 쓴 일률은 단순히 $p = f^\top v$ 다 (쌍대 기저가
아니면 중간에 계량 행렬이 끼어 이 식이 깨진다 — 이것이 "힘 벡터를 운동 벡터처럼 변환하면
틀리는" 근본 이유다).

같은 물리적 쌍 $(f, v)$ 를 두 좌표계에서 쓰면 $v_B = {}^BX_A v_A$ 이고, 일률 불변은

$$
f_B^\top\,{}^BX_A\,v_A = f_A^\top v_A \quad \forall v_A \in M^6
$$

를 요구한다. $v_A$ 가 임의이므로 양변의 행벡터가 같아야 한다:
$\big({}^BX_A\big)^\top f_B = f_A$. 양변에 $\big({}^BX_A\big)^{-\top}$ 을 곱하면

$$
f_B = \big({}^BX_A\big)^{-\top} f_A \;\;\Longrightarrow\;\; {}^BX_A^{*} = \big({}^BX_A\big)^{-\top} = \big({}^AX_B\big)^{\top},
$$

즉 (2)다. 마지막 등호는 $\big({}^BX_A\big)^{-1} = {}^AX_B$ 에서 나온다.

이제 (3)의 왼쪽 식을 세운다. 프레임 $B$ 의 원점은 $A$ 좌표로 $p$ 에 있고 자세는 $E = {}^BR_A$ 다.
자가 진단 4번(강체 위 두 점의 속도 관계)으로

$$
\omega_B = E\,\omega_A, \qquad
v_{OB} = E\big(v_{OA} + \omega_A \times p\big) = E\big(v_{OA} - \hat{p}\,\omega_A\big),
$$

여기서 $\omega_A \times p = \hat{\omega}_A p = -\hat{p}\,\omega_A$ 를 썼다(반대칭의 반교환성).
블록으로 모으면 (3)의 $^BX_A$ 다. 그 역행렬은 직접 곱해 확인한다:

$$
\begin{bmatrix} E^\top & 0 \\ \hat{p}E^\top & E^\top\end{bmatrix}
\begin{bmatrix} E & 0 \\ -E\hat{p} & E\end{bmatrix}
= \begin{bmatrix} \mathbb{1} & 0 \\ \hat{p} - \hat{p} & \mathbb{1}\end{bmatrix} = \mathbb{1}_6
\;\;\Longrightarrow\;\; {}^AX_B = \begin{bmatrix} E^\top & 0 \\ \hat{p}E^\top & E^\top\end{bmatrix}.
$$

전치하면 $\hat{p}^\top = -\hat{p}$ 에서 (3)의 오른쪽, $^BX_A^{*} = \begin{bmatrix} E & -E\hat{p} \\ 0 & E\end{bmatrix}$ 가
나온다. 물리로 교차 검증하면: $f_{\ell B} = Ef_{\ell A}$, $n_{OB} = E(n_{OA} - p \times f_{\ell A})$ —
모멘트 기준점을 $p$ 로 옮긴 바로 그 식이다. 유도와 물리가 맞는다.

**가정이 깨지는 곳**: (2)는 **쌍대 기저**를 전제한다. 6D 벡터를 "그냥 $\mathbb{R}^6$"으로 보고
운동과 힘에 같은 변환을 쓰면, 순수 평행이동 $E = \mathbb{1}$, $p \ne 0$ 에서 모멘트 이동 항의
부호가 뒤집혀 즉시 틀린다. 또 어떤 문헌은 $M^6$ 과 $F^6$ 의 성분 순서를 서로 다르게
(운동은 각 먼저, 힘은 선 먼저) 두는데, 그러면 $p = f^\top v$ 가 성립하지 않고
$p = f^\top \Sigma v$ ($\Sigma$ 는 블록 교환 행렬)가 된다. 외부 코드와 맞출 때 이 두 가지를 먼저 확인한다.

### R2 — 공간 관성의 조립과 변환

운동량의 정의에서 직접 조립한다. 질량중심의 속도는 자가 진단 4번으로
$v_C = v_O + \omega \times c = v_O - \hat{c}\,\omega$ 이므로 선운동량은

$$
h_\ell = m\,v_C = m\,v_O - m\hat{c}\,\omega = m\hat{c}^\top \omega + m\,v_O,
$$

($\hat{c}^\top = -\hat{c}$). 원점 $O$ 에 대한 각운동량은 "질량중심 기준 고유 각운동량 + 질량중심에
모인 선운동량의 모멘트"다:

$$
h_\omega = \bar{I}_C\,\omega + c \times h_\ell = \bar{I}_C\omega + \hat{c}\big(m v_O - m\hat{c}\omega\big)
  = \big(\bar{I}_C - m\hat{c}^2\big)\omega + m\hat{c}\,v_O.
$$

(1)에서 $-\hat{c}^2 = \hat{c}\hat{c}^\top$ 이므로 $h_\omega = (\bar{I}_C + m\hat{c}\hat{c}^\top)\omega + m\hat{c}v_O$.
두 식을 $h = Iv$ 로 모으면 (4)의 $I$ 다. 좌상 블록의 $m\hat{c}\hat{c}^\top = m(\lVert c\rVert^2\mathbb{1} - cc^\top)$
가 바로 **평행축(Steiner) 항**이고, 비대각 블록이 질량중심 오프셋의 **결합(coupling)**이다.
$I$ 는 대칭이다: $(m\hat{c})^\top = m\hat{c}^\top$ 이므로 비대각 블록이 서로 전치다.

변환 법칙은 $I$ 가 **사상**이라는 데서 나온다. $h_A = {}^AI\,v_A$ 이고 $h$ 는 힘 공간의 원소이므로

$$
h_B = {}^BX_A^{*}\,h_A = {}^BX_A^{*}\,{}^AI\,v_A = {}^BX_A^{*}\,{}^AI\,{}^AX_B\,v_B,
$$

모든 $v_B$ 에 대해 성립하므로 $^BI = {}^BX_A^{*}\,{}^AI\,{}^AX_B$. (2)로 $^BX_A^{*} = ({}^AX_B)^\top$ 이니
이것은 합동 변환 $Y^\top I Y$ ($Y = {}^AX_B$)이고, 따라서 **대칭성과 양정치성이 보존된다**.
운동 에너지로 다시 읽으면 같은 말이다: $T = \frac{1}{2}v^\top I v$ 가 스칼라이므로 $I$ 는
2차 형식처럼 변환되어야 한다.

**가정이 깨지는 곳**: $I$ 를 유사 변환 $X^{-1}IX$ 로 옮기면 대칭성이 깨진다(순수 회전
$p = 0$ 에서는 $X^{-1} = X^\top$ 이라 **우연히 맞고**, 평행이동이 섞이는 순간 틀린다).
이것이 재현 과제 조건 2의 존재 이유다. 또 (4)의 $I$ 는 **현재 좌표 원점 기준**이다 —
$\bar{I}_C$ 를 그대로 좌상 블록에 넣고 $c \ne 0$ 인 채로 쓰면 평행축 항이 빠진다.

### R3 — 외적과 변환의 미분

$v\times$ 의 정의는 "운동 벡터를 움직이는 좌표계에서 미분할 때 나오는 항"이다. 유도는
(5)의 첫 식에서 시작하는 것이 가장 짧다. $^AX_B(t)$ 를 성분으로 쓰고 $E(t) = {}^BR_A(t)$,
$p(t)$ 를 미분한다. $^AR_B = E^\top \equiv R$ 로 두면 C1 에서 $\dot{R} = \hat{\omega}R$
($\omega$ 는 $A$ 좌표의 각속도)이고, 프레임 $B$ 원점의 속도는 $\dot{p} = v_O + \omega \times p$
(원점이 물체에 고정되어 있을 때 — 자가 진단 4번)다. 이제

$$
{}^AX_B = \begin{bmatrix} R & 0 \\ \hat{p}R & R \end{bmatrix}
\;\;\Longrightarrow\;\;
\frac{d}{dt}{}^AX_B = \begin{bmatrix} \hat{\omega}R & 0 \\ \dot{\hat{p}}R + \hat{p}\hat{\omega}R & \hat{\omega}R\end{bmatrix}.
$$

좌하 블록을 정리한다. $\dot{\hat{p}} = \widehat{\dot{p}} = \hat{v}_O + \widehat{\omega \times p}$ 이고
반대칭 행렬의 야코비 항등식 $\widehat{\omega \times p} = \hat{\omega}\hat{p} - \hat{p}\hat{\omega}$ 를 쓰면

$$
\dot{\hat{p}}R + \hat{p}\hat{\omega}R = \big(\hat{v}_O + \hat{\omega}\hat{p} - \hat{p}\hat{\omega} + \hat{p}\hat{\omega}\big)R
  = \big(\hat{v}_O + \hat{\omega}\hat{p}\big)R.
$$

따라서

$$
\frac{d}{dt}{}^AX_B = \begin{bmatrix} \hat{\omega} & 0 \\ \hat{v}_O & \hat{\omega}\end{bmatrix}
\begin{bmatrix} R & 0 \\ \hat{p}R & R\end{bmatrix} = (v\times)\,{}^AX_B,
$$

이것이 (5)의 첫 식이고 동시에 (6)의 $v\times$ 의 **정의**다. 자가 진단 6번($\frac{d}{dt}A^{-1} = -A^{-1}\dot{A}A^{-1}$)
을 $^BX_A = ({}^AX_B)^{-1}$ 에 쓰면 둘째 식

$$
\frac{d}{dt}{}^BX_A = -\,{}^BX_A\,(v\times)\,{}^AX_B\,{}^BX_A = -\,{}^BX_A\,(v\times)
$$

가 나오고, 전치하면 $^AX_B^{*} = ({}^BX_A)^\top$ 에서

$$
\frac{d}{dt}{}^AX_B^{*} = \big(-{}^BX_A (v\times)\big)^\top = -(v\times)^\top\,{}^AX_B^{*} = (v\times^{*})\,{}^AX_B^{*}
$$

즉 (5)의 셋째 식이고, 동시에 $v\times^{*} = -(v\times)^\top$ 이라는 (6)의 둘째 주장이다.
성분으로 쓰면 $-\begin{bmatrix}\hat{\omega} & 0\\ \hat{v}_O & \hat{\omega}\end{bmatrix}^\top
= -\begin{bmatrix}-\hat{\omega} & -\hat{v}_O\\ 0 & -\hat{\omega}\end{bmatrix}
= \begin{bmatrix}\hat{\omega} & \hat{v}_O\\ 0 & \hat{\omega}\end{bmatrix}$ 로 (6)과 일치한다.

**읽기**: $v\times$ 는 $\mathfrak{se}(3)$ 의 수반 표현 $\mathrm{ad}_v$ 이고 $v\times^{*}$ 는 그 쌍대
$\mathrm{ad}_v^{*}$ 다 (`c1-twists-wrenches-adjoint` 의 $\mathrm{Ad}$, $\mathrm{Ad}^{*}$ 가 유한
변환, 여기 두 개가 그 무한소 버전). 공간 벡터 대수는 이 리 대수 구조를 **좌표로 내려 쓴 것**일
뿐이고, 그래서 C1 의 결과가 전부 재사용된다.

### R5 — 공간 가속도와 점의 가속도

$v_O(t)$ 는 "매 순간 좌표 원점에 겹쳐 있는 물체 고정점의 속도"다. 시각 $t$ 와 $t + \delta$ 에서
이 역할을 하는 물체 고정점은 **서로 다른 점**이다. 그래서 $\dot{v}_O$ 는 어떤 한 점의 가속도가
아니다.

원점에 겹친 점을 $P$ 라 하고 그 물질 점의 궤적을 따라가면, 위치는 $r_P(t)$, 속도는
$\dot{r}_P = v_O$ (현재 순간). 한 시간 단계 뒤 그 점은 원점을 떠나므로

$$
a_{\text{classical}} = \ddot{r}_P = \frac{d}{dt}\big(v_O + \omega \times (r_P - 0)\big)\Big|_{r_P = 0} = \dot{v}_O + \omega \times v_O,
$$

즉 (9)다. 반대로 $a_\ell = \dot{v}_O$ 는 "원점에 겹친 점의 속도장"을 미분한 것이고,
그 덕분에 (8)처럼 **선형 사상**으로 쓸 수 있다 — 이것이 공간 가속도를 쓰는 유일한 이유다.
고전 가속도를 쓰면 $f = I a_{\text{classical}} + \text{(다른 편향 항)}$ 이 되어 편향 항이
좌표 선택에 섞여 들어간다.

**가정이 깨지는 곳**: 두 정의의 차는 $\omega \times v_O$ 이므로 (i) $\omega = 0$ 또는
(ii) $v_O = 0$ (원점이 순간 정지) 또는 (iii) $\omega \parallel v_O$ 일 때 사라진다.
질량중심을 원점으로 잡고 정지 상태에서만 테스트하면 **버그가 드러나지 않는다**.
재현 과제 조건 3이 바로 이 지점을 겨냥한다.

## 증명 스케치

### R4 — $\dot{I} = (v\times^{*})I - I(v\times)$ 와 편향 항

**가설** H1: 물체는 강체이고 물체 고정 좌표계 $B$ 에서 본 공간 관성 $^BI$ 는 **상수**다.
H2: 좌표계 $A$ 는 관성(고정) 좌표계다. H3: $B$ 는 $A$ 에 대해 공간 속도 $v$ (A 좌표)로 움직인다.
**결론** C1: $\frac{d}{dt}{}^AI = (v\times^{*})\,{}^AI - {}^AI\,(v\times)$.
C2: $f = I a + (v\times^{*})Iv$ 이고 둘째 항은 $v$ 에 직교한다.

**전략**: 관성을 $^AI = ({}^BX_A)^\top\,{}^BI\,({}^BX_A)$ 로 쓰고, 변환의 미분 규칙 (5) 하나만
대입한다. 미분 기하를 끌어올 필요가 없다 — 모든 것이 (5)에 들어 있다.

1. **합동 표현.** R2 의 변환 법칙과 (2)로
   $^AI = {}^AX_B^{*}\,{}^BI\,{}^BX_A = ({}^BX_A)^\top\,{}^BI\,({}^BX_A)$. H1 로 $^BI$ 는 상수.
2. **미분.** 곱의 미분과 (5)의 둘째 식 $\frac{d}{dt}{}^BX_A = -{}^BX_A(v\times)$ 를 넣는다:
   $$
   \frac{d}{dt}{}^AI = \big(-{}^BX_A(v\times)\big)^\top {}^BI\,{}^BX_A + ({}^BX_A)^\top {}^BI\big(-{}^BX_A(v\times)\big).
   $$
3. **묶기.** 첫 항은 $-(v\times)^\top\big(({}^BX_A)^\top {}^BI\,{}^BX_A\big) = (v\times^{*})\,{}^AI$
   (마지막 등호는 (6)의 $v\times^{*} = -(v\times)^\top$). 둘째 항은 $-\,{}^AI\,(v\times)$.
   더하면 C1 이다.
4. **Newton-Euler.** 공간 운동량은 $h = Iv$ 이고, 관성 좌표계에서 공간 힘은 운동량의 시간
   미분이다($F^6$ 에서의 Newton 제2법칙 — Featherstone 2010 Part 2 §II):
   $$
   f = \dot{h} = \dot{I}v + I\dot{v} = (v\times^{*})Iv - I\underbrace{(v\times)v}_{=\,0} + Ia = Ia + (v\times^{*})Iv.
   $$
   $(v\times)v = 0$ 은 (6)에서 직접 확인된다: 각 블록이 $\hat{\omega}\omega = 0$,
   $\hat{v}_O\omega + \hat{\omega}v_O = v_O \times \omega + \omega \times v_O = 0$.
5. **편향 항은 일을 하지 않는다.** $v^\top (v\times^{*})Iv = \big((v\times^{*})^\top v\big)^\top Iv
   = \big(-(v\times)v\big)^\top Iv = 0$. 즉 운동 에너지 수지에 기여하지 않는다 — 코리올리·원심
   항이 "일을 하지 않는 힘"이라는 교과서적 서술의 정확한 내용이 이것이다.

**가설을 지우면**: H2(관성 좌표계)를 빼면 4단계의 $f = \dot{h}$ 가 성립하지 않는다. 움직이는
좌표계에서 성분을 미분하면 추가 수반 항이 붙고, 그 항이 바로 RNEA 의 재귀식에 나타나는 것이다
(`c2-rnea-inverse-dynamics`). H1(강체)을 빼면 $^BI$ 가 상수가 아니라 1단계부터 $\dot{}^BI$ 항이
남고, 그 항이 변형체·가변 질량 동역학의 추가 항이다.

생략한 기술적 단계: $F^6$ 에서 운동량의 미분이 공간 힘이라는 것 자체는 Newton 제2법칙을
6D 로 올린 공리에 해당한다. 유도를 보려면 Featherstone 2010 Part 2 §II–III, 또는
RBDA ch.2.9 의 운동량 논의를 본다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1·R2)** 순수 평행이동($E = \mathbb{1}$, $p \ne 0$)에서 (4)의 변환 법칙을 전개해,
$^BI$ 의 좌상 블록이 평행축 정리와 정확히 일치함을 보이라. 그 다음 **같은 계산을 틀린 공식**
$({}^BX_A)^\top\,{}^AI\,{}^BX_A$ 로 해서 어느 블록이 어떻게 어긋나는지 쓰라.
*해답 스케치*: $^BX_A = \begin{bmatrix}\mathbb{1} & 0\\ -\hat{p} & \mathbb{1}\end{bmatrix}$,
$^AX_B = \begin{bmatrix}\mathbb{1} & 0\\ \hat{p} & \mathbb{1}\end{bmatrix}$ 로 블록 곱을 하고
질량중심이 $c - p$ 로 옮겨간 것과 대조한다. 틀린 공식에서는 비대각 블록의 부호가 뒤집혀
$I$ 가 비대칭이 된다.

**P2 (유도, ★★, R3)** $v\times$ 와 $v\times^{*}$ 가 각각 $\mathfrak{se}(3)$ 의 $\mathrm{ad}_v$ 와
$\mathrm{ad}_v^{*}$ 임을 확인하라. 구체적으로 $v_1, v_2 \in M^6$ 에 대해
$(v_1\times)v_2 = -(v_2\times)v_1$ (반대칭성)과 야코비 항등식
$\big((v_1\times)v_2\big)\times = (v_1\times)(v_2\times) - (v_2\times)(v_1\times)$ 를 보이라.
*해답 스케치*: 블록으로 전개하고 $3$차원 야코비 항등식
$\widehat{a \times b} = \hat{a}\hat{b} - \hat{b}\hat{a}$ 를 각 블록에 적용한다. 좌하 블록에서
$\hat{\omega}_1\hat{v}_2 - \hat{v}_2\hat{\omega}_1 + \hat{v}_1\hat{\omega}_2 - \hat{\omega}_2\hat{v}_1$ 이
$\widehat{\omega_1 \times v_2 - \omega_2 \times v_1}$ 로 모이는지가 핵심이다.

**P3 (증명, ★★★, R4)** 공간 관성 $I$ 가 대칭 양정치임을 (4)에서 증명하고, R4 의 흐름 (7)이
**대칭성을 보존하는 흐름**임을 보이라. 즉 $I(0)$ 이 대칭이면 모든 $t$ 에서 $I(t)$ 가 대칭이다.
*전략 + 핵심 부등식*: 양정치성은 $v^\top I v = 2T \ge 0$ 와 등호 조건($\omega = 0$ 이고
$v_C = 0$)에서. 대칭 보존은 $\frac{d}{dt}(I - I^\top)$ 을 (7)로 계산해 $(I - I^\top)$ 에 대한
선형 ODE 임을 보이고 유일성으로 닫는다. (전개는 숨긴다.)

**P4 (계산, ★, R2·R4)** $m = 2$, $c = (0.1, -0.2, 0.3)$, $\bar{I}_C = \mathrm{diag}(0.05, 0.08, 0.11)$
인 강체와 $v = (0.3, -0.5, 0.9,\; 0.2, 0.4, -0.1)$ 에 대해 (4)의 $I$, 공간 운동량 $h = Iv$,
편향 항 $(v\times^{*})Iv$ 를 구하라.
*정답* (허용오차 $10^{-9}$):

$$
I = \begin{bmatrix}
 0.31 & 0.04 & -0.06 & 0 & -0.6 & -0.4\\
 0.04 & 0.28 & 0.12 & 0.6 & 0 & -0.2\\
 -0.06 & 0.12 & 0.21 & 0.4 & 0.2 & 0\\
 0 & 0.6 & 0.4 & 2 & 0 & 0\\
 -0.6 & 0 & 0.2 & 0 & 2 & 0\\
 -0.4 & -0.2 & 0 & 0 & 0 & 2
\end{bmatrix},
$$

$h = (-0.181,\; 0.12,\; 0.271,\; 0.46,\; 0.8,\; -0.22)$,
$(v\times^{*})Iv = (-0.2515,\; -0.2462,\; -0.0785,\; -0.61,\; 0.48,\; 0.47)$.
*검산*: ⓐ $I = I^\top$ 이고 고윳값이 모두 양수 ⓑ $v^\top (v\times^{*})Iv = 0$ (오차 $< 10^{-15}$)
ⓒ 하단 3성분의 선운동량이 $m(v_O + \omega \times c)$ 와 일치.

**P5 (구현, ★★, R1·R2·R3)** `skew`, `crm`($v\times$), `crf`($v\times^{*}$), `xform`($^BX_A$),
`xform_dual`($^BX_A^{*}$), `spatial_inertia`($m, c, \bar{I}_C \mapsto I$) 를 numpy 로 구현하라.
전치·역행렬을 **직접 계산하지 말고** (3)의 닫힌 형태로 조립해야 한다.
*루브릭*: ⓐ `xform_dual(E, p)` 가 `inv(xform(E, p)).T` 와 $10^{-14}$ 이내로 일치
ⓑ `crf(v) == -crm(v).T` 가 정확히(비트 단위) 성립 ⓒ 임의 $v$ 에 대해 `crm(v) @ v` 가 0
ⓓ 변환의 합성 $^CX_B\,{}^BX_A = {}^CX_A$ 가 성립(프레임 3개로 확인)
ⓔ 성분 순서 규약이 docstring 에 명시되어 있다.

**P6 (반례, ★★, R5)** "공간 가속도의 하단 3성분은 원점에 겹친 물체 고정점의 가속도다"라는
주장이 틀렸음을 **수치 반례**로 보이라. 반례는 (i) 위 주장을 쓰면 (8)의 토크가 틀리고
(ii) 질량중심 원점 + 정지 상태에서는 그 오류가 사라지는 것을 **둘 다** 보여야 한다.
*성질 체크리스트*: $\omega \ne 0$, $v_O \ne 0$, $\omega \not\parallel v_O$, 원점 $\ne$ 질량중심.
두 계산의 차가 정확히 $I\,(0; \omega \times v_O)$ 인지 확인하면 반례가 옳다.

## 논문 읽기

**필독 2편.** 두 편 모두 튜토리얼이고 합쳐 20쪽이 안 되지만, 이 모듈의 표기 전체가 여기서
나온다. 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다(`lesson-standard.md` §5).
3-pass 로 읽고 3번째 패스에서 질문 4·7·9 를 집중 공략한다 — 튜토리얼 논문에서는 "무엇을
보장하지 않는가"와 "복잡도"가 가장 빨리 흐려지는 항목이다.

1. **Featherstone, "A Beginner's Guide to 6-D Vectors (Part 1)" (2010, IEEE RAM)** — 역할:
   `표준(standard)`. <https://doi.org/10.1109/MRA.2010.937853>
   어느 절을 왜 읽는가: 운동 공간과 힘 공간을 **두 개의 다른 벡터공간**으로 세우는 절과
   Plücker 좌표를 도입하는 절. 이 레슨의 R1 이 그 절의 요구(일률 불변)를 식으로 쓴 것이다.
   추가 질문: ⓐ 저자가 "6D 벡터를 쓰면 식이 줄어든다"는 주장을 어떤 예로 지지하는가, 그 예는
   공정한가? ⓑ 저자의 표기를 이 레슨의 $^BX_A$, $^BX_A^{*}$ 로 옮겨 쓰면 어디서 충돌하는가?
2. **Featherstone, "A Beginner's Guide to 6-D Vectors (Part 2)" (2010, IEEE RAM)** — 역할:
   `표준(standard)`. <https://doi.org/10.1109/MRA.2010.939560>
   어느 절을 왜 읽는가: 공간 관성과 외적·미분 규칙을 세우는 절, 그리고 이를 동역학
   알고리즘으로 잇는 마지막 절. 이 레슨의 R2·R3·R4 와 1:1 로 대응하므로 **유도를 대조**하며 읽는다.
   추가 질문: ⓐ 저자의 $\times$ 와 $\times^{*}$ 정의가 (6)과 부호까지 일치하는가, 다르면 어느
   규약 차이 때문인가? ⓑ 저자가 공간 가속도와 고전 가속도의 차이를 어디서 경고하는가, 그
   경고가 충분한가? ⓒ 이 표기를 쓰지 않았다면 다음 레슨의 RNEA 재귀식이 어떻게 보일까?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

> 두 편은 실험 논문이 아니므로 질문 5·6 은 "저자가 주장을 지지하려고 든 예시"에 적용한다.
> 질문을 건너뛰지 말고, 적용할 수 없는 이유를 한 줄로 적는 것이 노트의 일부다.

## 재현 과제

**티어 R1 (수치 검증).** 계산 예산: 노트북 CPU 1코어, 1분 이내, numpy 만(유한차분 대조에만
`scipy.linalg.expm` 을 쓴다 — 직접 구현해도 된다). 메모리 100MB 이내.

P5 에서 쓴 함수들이 아래 **네 조건을 모두** 만족해야 통과다. 난수는 시드를 고정한다.

1. **쌍대성과 변환의 일관성** — 무작위 $(E, p)$ $10^4$ 개와 무작위 $v \in M^6$, $f \in F^6$ 에 대해
   $$
   \max\big|f^\top v - (\,{}^BX_A^{*}f)^\top({}^BX_A v)\,\big| < 10^{-12},\qquad
   \max\big\lVert {}^BX_A^{*} - ({}^BX_A)^{-\top} \big\rVert_\infty < 10^{-12}.
   $$
2. **공간 관성 변환 ≡ 동차변환 기반 재계산** — 무작위 $m \in (0.1, 10)$, $c$ ($\lVert c\rVert < 1$),
   무작위 양정치 $\bar{I}_C$ 로 $10^4$ 회: 변환 법칙 (4)로 얻은 $^BI_{\text{law}}$ 와, 질량
   속성을 먼저 옮겨($c_B = E(c - p)$, $\bar{I}_{C,B} = E\bar{I}_C E^\top$) (4)의 조립식으로 다시
   만든 $^BI_{\text{direct}}$ 가
   $$
   \max \big\lVert {}^BI_{\text{law}} - {}^BI_{\text{direct}} \big\rVert_\infty < 10^{-10}, \qquad
   \max \big\lVert {}^BI_{\text{law}} - ({}^BI_{\text{law}})^\top \big\rVert_\infty < 10^{-12}.
   $$
   (이것이 blueprint 가 지정한 수용 기준이다. 두 경로가 **서로 독립**인 것이 요점 —
   하나는 $6\times6$ 합동 변환, 하나는 $3\times3$ 평행축 정리다.)
3. **$\dot{I}$ 항등식 (7)** — 고정 $I$, 고정 $v$ 에 대해 $J(t) = \big(\exp(-(v\times)t)\big)^\top I \exp(-(v\times)t)$
   를 중앙 유한차분하고($h = 10^{-6}$)
   $$
   \big\lVert \tfrac{J(h) - J(-h)}{2h} - \big((v\times^{*})I - I(v\times)\big) \big\rVert_\infty < 10^{-8}.
   $$
   이어서 편향 항의 무일성 $\big|v^\top (v\times^{*})Iv\big| < 10^{-14}$ 를 $10^4$ 개 난수로 확인한다.
4. **R5 의 차이를 수치로 분리** — $\omega \ne 0$, $v_O \ne 0$, $\omega \not\parallel v_O$,
   $c \ne 0$ 인 상태 하나를 잡아 (8)의 토크를 $a = \dot{v}$ 로, 그리고 하단 성분만
   $a_{\text{classical}} = \dot{v}_O + \omega \times v_O$ 로 바꿔 두 번 계산하고, 두 결과의 차가
   $$
   \big\lVert f_{\text{wrong}} - f_{\text{right}} - I\,(0;\, \omega \times v_O) \big\rVert_\infty < 10^{-12}
   $$
   를 만족하면서 $\lVert f_{\text{wrong}} - f_{\text{right}}\rVert_\infty > 10^{-2}$ 임을 보이라
   (즉 오류가 실제로 **크다**). 그 다음 $c = 0$, $v_O = 0$ 으로 바꾸면 차가 $10^{-14}$ 이하로
   사라지는 것을 확인한다.

**입력 데이터**: 외부 데이터 불필요. 모든 입력은 고정 시드 난수
(`np.random.default_rng(0)`)로 생성한다. 조건 2의 양정치 $\bar{I}_C$ 는 삼각부등식
($I_{xx} + I_{yy} \ge I_{zz}$ 등)을 만족하도록 **물리적으로 실현 가능한** 값만 쓴다 —
그렇지 않으면 조건 2는 통과하지만 `c2-dynamics-derivatives-sysid` 의 물리적 일관성 제약에서
걸린다.

**비교 대상** (최소 1개):
- 1순위: 직접 구현한 두 번째 독립 경로(조건 2가 이미 이 구조다).
- 2순위: `pinocchio` 의 `pin.Inertia` / `pin.SE3.act` 로 같은 변환을 계산해 $10^{-10}$ 이내 일치.
  성분 순서가 선형 먼저임에 주의한다 — 순서 변환 행렬을 명시적으로 쓴다.
- 참고: Featherstone 의 공개 구현(<https://royfeatherstone.org/spatial/>)의 `Xtrans`·`mcI`·`crm`·`crf`
  와 수치를 대조할 수 있다(Octave).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 1 의 둘째 식만 실패 | $^BX_A^{*}$ 를 $({}^BX_A)^\top$ 로 썼다(역행렬을 빼먹음) | $E = \mathbb{1}$, $p \ne 0$ 을 넣어 모멘트 이동 항의 **부호**를 본다 |
| 조건 2 가 순수 회전에서만 통과 | 합동 변환 대신 유사 변환 $X^{-1}IX$ 를 썼다 | $p \ne 0$, $E = \mathbb{1}$ 로 고정하고 $\lVert I - I^\top\rVert$ 를 본다 |
| 조건 2 가 $10^{-6}$ 수준에서 멈춘다 | $\bar{I}_C$ 가 거의 특이하거나 $m$ 이 $10^{-3}$ 이하 — 조건수 문제 | $m$, $\bar{I}_C$ 의 조건수를 출력하고 샘플 범위를 좁힌다 |
| 조건 3 의 부호가 반대 | $J(t)$ 를 $\exp(+(v\times)t)$ 로 썼다($^AX_B$ 와 $^BX_A$ 혼동) | $t = 0$ 에서 $J(0) = I$ 인지, $J$ 가 **감소하는** 방향인지 확인 |
| 조건 4 의 차가 0 | 테스트 상태가 $v_O = 0$ 또는 $\omega \parallel v_O$ 또는 $c = 0$ | 세 조건을 단위 테스트로 **명시적으로** 검사한다 |
| 성분 순서를 바꾼 뒤 전부 깨진다 | 순서 교환이 $M^6$ 과 $F^6$ 에 **같은** 치환으로 들어가야 한다 | 블록 교환 행렬 $\Sigma$ 를 명시적으로 두고 $\Sigma^\top = \Sigma^{-1} = \Sigma$ 를 확인 |

## 열린 문제

- **(열린 문제) 좌표 선택이 수치 조건수에 주는 영향** — 같은 기구를 어느 프레임에 표현하느냐에
  따라 질량행렬의 조건수가 수십 배 달라지고, 긴 연쇄나 질량비가 큰 계(예: 경량 팔 + 무거운
  엔드이펙터)에서 이것이 적분기와 접촉 해법의 정확도를 지배한다. 공간 벡터 대수는 "어떤
  프레임이 수치적으로 최선인가"에 답을 주지 않는다 — 기구 구조에서 조건수를 **예측**하는
  이론이 없다. 현재 접근: 질량행렬의 사전조건화와 분기 구조를 쓰는 $O(n)$ 해법
  ([Featherstone 1983](https://doi.org/10.1177/027836498300200102), 분할정복
  [Featherstone 1999](https://doi.org/10.1177/02783649922066619)). 비어 있는 자리: 프레임·좌표
  선택을 조건수 기준으로 자동 선택하는 절차.
- **(열린 문제) 6D 대수의 자동 미분 친화성** — 공간 벡터 대수는 사람이 손으로 재귀식을 쓰기에
  최적이지만, $v\times$ 와 $v\times^{*}$ 가 서로 다른 변환 규칙을 갖기 때문에 **미분을 자동으로
  얻을 때** 그래프가 중복 계산을 만든다. 해석적 미분이 자동 미분보다 한 자릿수 빠른 이유가
  여기 있다([Carpentier & Mansard 2018](https://doi.org/10.15607/RSS.2018.XIV.038)). 아직 없는
  것: 쌍대 구조를 컴파일러가 이해해 자동 미분으로도 같은 비용을 내는 표현.
  이 질문은 `c2-dynamics-derivatives-sysid` 에서 다시 나온다.
- **(열린 문제) 연쇄가 아닌 계로의 확장** — 공간 벡터 대수의 알고리즘적 이득(§다음 두 레슨의
  $O(n)$·$O(n^2)$)은 **트리 구조**에 의존한다. 폐루프·접촉으로 그래프에 순환이 생기면 승수나
  널공간 투영이 들어오고 그 비용은 다시 $O(n^3)$ 에 가까워진다
  (`c2-constrained-dynamics`). 현재 접근: 분할정복 $O(\log n)$ 병렬화와
  접촉의 볼록 완화([Todorov 2014](https://doi.org/10.1109/ICRA.2014.6907751)).
  비어 있는 자리: 접촉 수에 대해 선형인 정확한 해법.

## 개념 점검

`rc quiz c2-spatial-vector-algebra` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c2-spatial-vector-algebra-quiz
questions:
  - id: q1
    type: single
    prompt: "운동 변환이 $^{B}X_{A}$ 일 때 힘 변환 $^{B}X^{*}_{A}$ 는?"
    choices:
      - "$({}^{B}X_{A})^{\\top}$"
      - "$({}^{B}X_{A})^{-\\top}$"
      - "$({}^{B}X_{A})^{-1}$"
      - "$^{B}X_{A}$ 와 같다"
    answer: 1
    explanation: "일률 $f^{\\top}v$ 가 좌표 무관이어야 하므로 $f_B^{\\top}({}^{B}X_{A}v_A) = f_A^{\\top}v_A$ 가 모든 $v_A$ 에 성립해야 한다. 따라서 $({}^{B}X_{A})^{\\top}f_B = f_A$, 즉 $^{B}X^{*}_{A} = ({}^{B}X_{A})^{-\\top} = ({}^{A}X_{B})^{\\top}$ 다. 전치만 쓰면 평행이동이 섞일 때 모멘트 이동 항의 부호가 뒤집힌다."
    concept: { front: "힘 벡터의 좌표 변환", back: "$^{B}X^{*}_{A} = ({}^{B}X_{A})^{-\\top} = ({}^{A}X_{B})^{\\top}$ — 일률 불변이 유일한 근거" }
  - id: q2
    type: single
    prompt: "공간 관성을 프레임 $A$ 에서 $B$ 로 옮기는 올바른 식은?"
    choices:
      - "$({}^{B}X_{A})^{-1}\\,{}^{A}I\\,{}^{B}X_{A}$ (유사 변환)"
      - "$({}^{A}X_{B})^{\\top}\\,{}^{A}I\\,{}^{A}X_{B}$ (합동 변환)"
      - "$({}^{B}X_{A})^{\\top}\\,{}^{A}I\\,{}^{B}X_{A}$"
      - "$^{B}X_{A}\\,{}^{A}I\\,({}^{B}X_{A})^{\\top}$"
    answer: 1
    explanation: "$I$ 는 $M^6 \\to F^6$ 사상이므로 입력에 $^{A}X_{B}$, 출력에 $^{B}X^{*}_{A} = ({}^{A}X_{B})^{\\top}$ 가 붙어 합동 변환이 된다. 그래서 대칭성과 양정치성이 보존된다. 유사 변환은 순수 회전에서는 우연히 맞고 평행이동이 섞이면 $I$ 를 비대칭으로 만든다."
    concept: { front: "공간 관성의 변환", back: "$^{B}I = ({}^{A}X_{B})^{\\top}\\,{}^{A}I\\,{}^{A}X_{B}$ — 합동(congruence), 유사 변환이 아니다" }
  - id: q3
    type: truefalse
    prompt: "공간 가속도의 하단 3성분은 좌표 원점에 겹쳐 있는 물체 고정점의 (고전적) 가속도와 같다."
    answer: false
    explanation: "두 개는 $\\omega \\times v_O$ 만큼 다르다: $a_{\\text{classical}} = \\dot{v}_O + \\omega \\times v_O$ 인데 공간 가속도의 하단은 $\\dot{v}_O$ 다. 매 순간 원점에 겹치는 물체 고정점이 서로 다른 점이기 때문이다. 질량중심 원점이거나 $v_O = 0$ 이면 차가 사라져 버그가 숨는다."
    concept: { front: "공간 가속도 vs 점의 가속도", back: "$a_{\\text{classical}} = \\dot{v}_O + \\omega \\times v_O$ — 공간 가속도는 $\\dot{v}_O$. 차이는 $\\omega \\times v_O$" }
  - id: q4
    type: short
    prompt: "(8)의 편향 항 $(v\\times^{*})Iv$ 가 하는 일(power)의 값은?"
    answer: ["0", "zero", "영", "0 이다", "일을 하지 않는다"]
    explanation: "$v^{\\top}(v\\times^{*})Iv = (-(v\\times)v)^{\\top}Iv$ 이고 $(v\\times)v = 0$ 이므로 정확히 0 이다. 코리올리·원심 항이 운동 에너지 수지에 기여하지 않는다는 서술의 정확한 내용이 이것이고, 적분기와 제어기의 수치 점검(일 수지)에 바로 쓴다."
    concept: { front: "코리올리·원심(편향) 항의 일률", back: "정확히 0 — $(v\\times)v = 0$ 에서 따라온다" }
  - id: q5
    type: multiple
    prompt: "$\\dot{I} = (v\\times^{*})I - I(v\\times)$ 의 유도에 **실제로 쓰이는** 가정을 모두 고르라."
    choices:
      - "물체 고정 프레임에서 본 공간 관성이 상수다 (강체)"
      - "기준 프레임이 관성(고정) 좌표계다"
      - "관성 행렬이 대각이다"
      - "질량중심이 좌표 원점에 있다"
    answer: [0, 1]
    explanation: "강체 가정이 $^{B}I$ 를 상수로 만들어 1단계가 성립하고, 관성 좌표계 가정은 뒤이어 $f = \\dot{h}$ 를 쓸 때 필요하다. 관성행렬의 대각성이나 질량중심 위치는 유도에 전혀 쓰이지 않는다 — 다만 질량중심 원점은 R5 의 오류를 숨겨 테스트를 무력화한다."
    concept: { front: "(7)이 쓰는 가정", back: "강체($^{B}I$ 상수) + 관성 좌표계. 대각 관성·질량중심 원점은 불필요" }
```

## 이 단계 공부법

1. **자가 진단으로 시작한다 (20분)** — 위 6문항을 먼저 푼다. 2번과 6번에서 막히면 이 레슨의
   유도를 따라갈 수 없으니 C1 과 선형대수를 먼저 보라. 나머지는 막혀도 진행 가능하다.
2. **성분 순서를 종이에 못 박는다 (20분)** — $(\omega; v_O)$, $(n_O; f_\ell)$ 를 쓰고, (3)과 (6)의
   네 행렬을 손으로 적어 벽에 붙인다. 이 모듈에서 생기는 버그의 대다수가 순서·부호다.
3. **R1 을 거꾸로 유도한다 (40분)** — (3)의 $^BX_A$ 를 **먼저 외우지 말고**, 강체 두 점의 속도
   관계에서 조립한다. 그 다음 일률 불변만으로 $^BX_A^{*}$ 를 끌어내고, 마지막에 모멘트 이동
   공식과 대조해 물리가 맞는지 확인한다. 이 순서로 하면 "왜 두 종류의 변환인가"가 남는다.
4. **R4 를 백지에서 재구성한다 (60분)** — (5)의 둘째 식 하나만 기억하고 증명 스케치 1–4단계를
   다시 쓴다. 막히는 지점은 거의 항상 3단계의 전치 처리다. 그 다음 Featherstone Part 2 의
   같은 결과와 **부호까지** 대조한다.
5. **틀린 구현을 먼저 만든다 (50분)** — P5 를 쓸 때 일부러 ⓐ $X^{*} = X^\top$ ⓑ 유사 변환
   ⓒ 고전 가속도 세 버전을 만들어 재현 과제의 어느 조건이 어떻게 깨지는지 본다. 깨지는 것을
   보지 않고 쓴 테스트는 다음 레슨에서 아무것도 잡아내지 못한다.
6. **재현 과제를 끝낸다 (75분)** — 네 조건을 테스트 함수 4개로 쓴다. 조건 3의 유한차분은
   $h$ 를 $10^{-4}$ 에서 $10^{-8}$ 까지 쓸며 오차 곡선을 그려라. $10^{-6}$ 근처에서 최소가
   되고 그 아래에서 다시 커지는 **V 자**가 보여야 정상이다(절단 오차 vs 반올림 오차).
7. **논문 2편을 표기 대조로 읽는다 (120분)** — Part 1 → Part 2 순서로 읽고, 각 논문의 표기를
   이 레슨의 기호표로 옮겨 적는다. 1페이지 노트는 **반드시** 쓴다 — RNEA·CRBA·ABA 를 쓸 때
   이 노트로 돌아온다.
8. **무엇을 못 하는지로 끝낸다 (20분)** — 열린 문제 중 하나를 골라 왜 아직 안 풀렸는지 한
   문단으로 쓴다. 조건수 문제는 재현 과제 조건 2의 세 번째 실패 모드에서 이미 손으로 만졌다.

**통과 기준**: 백지에서 (3)·(4)·(6)을 쓸 수 있고, (7)의 증명을 4단계로 말할 수 있고,
재현 과제 네 조건을 통과하는 코드를 갖고 있고, 논문 2편의 1페이지 노트가 있다.
