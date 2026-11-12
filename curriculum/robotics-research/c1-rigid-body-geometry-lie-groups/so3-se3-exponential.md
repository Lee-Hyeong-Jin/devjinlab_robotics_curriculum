---
id: c1-so3-se3-exponential
title: SO(3)·SE(3)와 지수 좌표
summary: >-
  강체 회전과 운동을 행렬 리 군 SO(3)·SE(3)으로 기술하고, Rodrigues 공식과 SE(3) 지수 사상을
  직접 유도하고, 지수 사상의 전사성과 로그의 특이점을 증명 수준에서 다룬다. 단위 사원수의 이중
  피복이 왜 전역적 3-매개변수 표현을 불가능하게 하는지까지 간다.
objectives:
  - 행렬 지수의 거듭제곱 급수에서 Rodrigues 공식을 빠진 줄 없이 유도할 수 있다.
  - 모든 회전이 어떤 축에 대한 회전임을(지수 사상의 전사성) 증명 스케치로 재구성할 수 있다.
  - 로그 사상이 θ→0 과 θ→π 에서 어떻게 무너지는지 설명하고, 수치적으로 안전한 분기를 구현할 수 있다.
  - SE(3) 지수 사상의 평행이동 블록 G(θ)를 유도하고 좌 야코비안과의 관계를 쓸 수 있다.
  - 단위 사원수의 이중 피복으로부터 SO(3)에 전역적 특이점 없는 3-매개변수 좌표가 없음을 논증할 수 있다.
prerequisites: []
difficulty: 5
estimated_minutes: 480
tags: [lie-groups, so3, se3, exponential-map, rotation, research]
activities:
  - id: c1-so3-se3-exponential-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c1-so3-se3-exponential-papers
    kind: paper
    title: 필독 논문 2편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 120
  - id: c1-so3-se3-exponential-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 150
  - id: c1-so3-se3-exponential-reproduction
    kind: reproduction
    title: 재현 과제 — exp/log 왕복과 미분 검증 (R1)
    estimated_minutes: 90
  - id: c1-so3-se3-exponential-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.7 (3차원 기하), ch.8 (행렬 리 군). 이 레슨의 1순위 교재. 전문 PDF 무료.
  - title: "Lynch & Park, Modern Robotics"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: ch.3 (Rigid-Body Motions) — 3.2 회전, 3.3 강체 운동과 나선 축. 전문 PDF 무료.
  - title: "Murray, Li & Sastry, A Mathematical Introduction to Robotic Manipulation"
    kind: book
    note: ch.2 (Rigid Body Motion). CMU 16-711·Berkeley C106B 의 지정 교재. (공식 URL 미확인)
papers:
  - id: sola2018-micro-lie-theory
    required: true
    role: standard
    note: "§2-4"
  - id: forster2017-preintegration
    required: true
    role: seminal
    note: "§II-III"
  - id: grassia1998-exp-map
    role: standard
  - id: shoemake1985-quaternion-curves
    role: seminal
---

# SO(3)·SE(3)와 지수 좌표

## 전제와 기호

이 레슨은 연구 트랙의 첫 레슨이고, 이후 모든 모듈이 여기의 표기를 쓴다. 시작하기 전에 다음을
전제한다(없으면 `robotics-expert` 코스의 M1·M2 와 R0 모듈을 먼저 본다):

- 선형대수: 고윳값·고유공간, 직교행렬, 행렬 지수, 최소 다항식.
- 해석: 거듭제곱 급수의 수렴, 행렬값 ODE 의 존재·유일성, Taylor 정리.
- 미분기하는 **요구하지 않는다** — 접공간·다양체는 이 레슨에서 필요한 만큼만 쓰고,
  일반론은 `c1-manifold-optimization` 에서 다룬다.

표기 규약(이 코스 전체에 고정):

| 기호 | 뜻 |
|---|---|
| $R \in SO(3)$ | $R^\top R = I$, $\det R = +1$ 인 $3\times3$ 회전행렬 |
| $\hat{\omega}$ | $\omega \in \mathbb{R}^3$ 의 반대칭 행렬(skew). $\hat{\omega} x = \omega \times x$ |
| $\mathfrak{so}(3)$ | $3\times3$ 반대칭 행렬의 집합 $= \{\hat{\omega} : \omega \in \mathbb{R}^3\}$, $SO(3)$ 의 리 대수 |
| $\phi = \theta u$ | 회전 벡터(지수 좌표). $u$ 는 단위 축, $\theta = \lVert \phi \rVert$ 는 회전각 |
| $T = (R, p) \in SE(3)$ | 동차변환 $\begin{bmatrix} R & p \\ 0 & 1\end{bmatrix}$ |
| $\xi = (\omega, v) \in \mathbb{R}^6$ | 트위스트. $\hat{\xi} = \begin{bmatrix} \hat{\omega} & v \\ 0 & 0\end{bmatrix} \in \mathfrak{se}(3)$ |
| $^A R_B$ | 프레임 $B$ 를 프레임 $A$ 로 보내는 회전. 좌표는 **열벡터**, 변환은 **왼쪽에서** 곱한다 |

$\lVert \omega \rVert = 1$ 일 때 두 항등식을 계속 쓴다. 둘 다 직접 전개해 확인하라:

$$\hat{\omega}^2 = \omega\omega^\top - I, \qquad \hat{\omega}^3 = -\hat{\omega}. \tag{1}$$

## 시작 전 자가 진단

이 모듈의 첫 레슨이므로 준비 상태를 먼저 점검한다. **선수 레슨은 잠겨 있지 않다** — 아래를 전부
풀 수 있으면 권장 선수(R0 모듈, `robotics-expert` 코스의 M1)를 건너뛰고 바로 시작해도 된다.
**두 문항 이상 막히면** 괄호 안의 선수 레슨으로 돌아가는 편이 빠르다.

1. $A = \mathrm{diag}(3, 1, 0.01)$ 의 2-노름 조건수 $\kappa_2(A)$ 는?
   (`r0-linear-algebra-decompositions`)
   **정답**: $\kappa_2 = \sigma_{\max}/\sigma_{\min} = 3/0.01 = 300$.
2. $R \in \mathbb{R}^{3\times3}$ 가 $R^\top R = I$ 를 만족할 때 $\det R$ 이 가질 수 있는 값은?
   그중 $SO(3)$ 에 속하는 것은? (`m1-rotation-representations`)
   **정답**: $\det R = \pm1$ ($\det(R^\top R) = (\det R)^2 = 1$ 에서). $SO(3)$ 는 $+1$ 만.
3. 행렬 지수 $\exp(A)$ 의 정의를 급수로 쓰고, $\exp(A+B) = \exp(A)\exp(B)$ 가 성립하는
   조건을 말하라. (`r0-ad-and-integrators`)
   **정답**: $\exp(A) = \sum_{k\ge0} A^k/k!$. 등식은 $AB = BA$ (교환)일 때만 성립한다.
4. $f(x) = x^\top M x$ ($M$ 은 대칭)의 기울기 $\nabla f$ 와, $x_0$ 에서의 1차 Taylor 전개를
   쓰라. (`f0-calculus-multivariable`)
   **정답**: $\nabla f = 2Mx$, $f(x_0 + \delta) \approx f(x_0) + 2(Mx_0)^\top\delta$.
5. numpy 로 $g: \mathbb{R}^3 \to \mathbb{R}^3$ 의 야코비안을 중심 유한차분으로 계산하는 코드를
   세 줄 이내로 쓰고, 스텝 크기를 $10^{-5}$ 로 고르는 이유를 말하라. (`r0-ad-and-integrators`)
   **정답**: 열마다 $(g(x + he_i) - g(x - he_i))/(2h)$. 중심 차분의 절단 오차는 $O(h^2)$,
   반올림 오차는 $O(\epsilon/h)$ 이므로 배정밀도($\epsilon \approx 2\times10^{-16}$)에서
   $h \sim \epsilon^{1/3} \approx 6\times10^{-6}$ 근방이 최적이다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (Rodrigues 공식) [D3]** — $\lVert \omega \rVert = 1$ 이면
  $$\exp(\hat{\omega}\theta) = I + \sin\theta\,\hat{\omega} + (1 - \cos\theta)\,\hat{\omega}^2. \tag{2}$$
- **R2 (지수 사상의 전사성 = Euler 의 회전 정리) [D3]** — 모든 $R \in SO(3)$ 에 대해
  $R = \exp(\hat{\omega}\theta)$ 인 단위 $\omega$ 와 $\theta \in [0, \pi]$ 가 존재한다.
  즉 $\exp : \mathfrak{so}(3) \to SO(3)$ 는 전사이고, 모든 회전은 **어떤 축에 대한 한 번의 회전**이다.
- **R3 (로그 사상과 그 특이점) [D3]** — $\theta \in (0, \pi)$ 에서
  $$
  \theta = \arccos\!\left(\frac{\operatorname{tr} R - 1}{2}\right), \qquad
    \hat{\omega} = \frac{R - R^\top}{2\sin\theta}. \tag{3}
  $$
  이 공식은 $\theta \to 0$ 에서 축이 **정의되지 않고**(0/0), $\theta \to \pi$ 에서
  $R - R^\top \to 0$ 이라 **축 정보를 잃는다**. 두 경우는 별도 분기가 필요하다.
- **R4 (사원수의 이중 피복과 전역 좌표의 부재) [D2]** — 단위 사원수 $S^3 \to SO(3)$ 는 2:1 피복이고
  $q$ 와 $-q$ 가 같은 회전을 준다. 따라서 $SO(3) \cong \mathbb{RP}^3$ 이고, $SO(3)$ 은 콤팩트이므로
  $\mathbb{R}^3$ 과 미분동형일 수 없다 — **특이점 없는 전역 3-매개변수 좌표는 존재하지 않는다.**
- **R5 (SE(3) 지수 사상) [D2]** — $\lVert \omega \rVert = 1$, $\xi = (\omega, v)$ 이면
  $$
  \exp(\hat{\xi}\theta) = \begin{bmatrix} \exp(\hat{\omega}\theta) & G(\theta)\,v \\ 0 & 1 \end{bmatrix},
    \quad G(\theta) = I\theta + (1 - \cos\theta)\hat{\omega} + (\theta - \sin\theta)\hat{\omega}^2. \tag{4}
  $$
  여기서 $G(\theta) = \theta J_l(\theta u)$ 이고 $J_l$ 은 $SO(3)$ 의 **좌 야코비안**이다 —
  이 연결이 `c1-lie-group-derivatives` 의 출발점이다. **[D1]**

## 유도

### R1 — Rodrigues 공식

$\omega$ 를 고정된 단위 벡터로 두고 회전을 각속도 ODE 의 해로 정의한다:

$$
\dot{R}(t) = \hat{\omega} R(t), \qquad R(0) = I
  \;\;\Longrightarrow\;\; R(\theta) = \exp(\hat{\omega}\theta) = \sum_{k=0}^{\infty} \frac{(\hat{\omega}\theta)^k}{k!}. \tag{5}
$$

급수는 모든 행렬에 대해 절대 수렴하므로 항을 재배열할 수 있다. (1)의 $\hat{\omega}^3 = -\hat{\omega}$
에서 거듭제곱이 주기 4로 닫힌다:

$$
\hat{\omega}^1 = \hat{\omega}, \quad \hat{\omega}^2 = \hat{\omega}^2, \quad
  \hat{\omega}^3 = -\hat{\omega}, \quad \hat{\omega}^4 = -\hat{\omega}^2, \quad
  \hat{\omega}^5 = \hat{\omega}, \; \dots
$$

따라서 $k \ge 1$ 의 항은 **홀수 거듭제곱 → $\hat{\omega}$ 의 배수**, **짝수 거듭제곱 →
$\hat{\omega}^2$ 의 배수**로만 모인다. 계수를 모으면

$$
\exp(\hat{\omega}\theta) = I
  + \underbrace{\left(\theta - \frac{\theta^3}{3!} + \frac{\theta^5}{5!} - \cdots\right)}_{=\,\sin\theta}\hat{\omega}
  + \underbrace{\left(\frac{\theta^2}{2!} - \frac{\theta^4}{4!} + \frac{\theta^6}{6!} - \cdots\right)}_{=\,1-\cos\theta}\hat{\omega}^2,
$$

즉 (2)다. 부호를 틀리기 쉬운 지점은 $\hat{\omega}^4 = -\hat{\omega}^2$ 라서 짝수 급수가
$\cos$ 이 아니라 $1 - \cos$ 이 되는 곳이다. 직접 두 항까지 써서 확인하라.

**가정이 깨지는 곳**: (1)은 $\lVert \omega \rVert = 1$ 에서만 성립한다. 단위가 아닌 $\phi$ 에
(2)를 그대로 쓰면 틀린다 — $\theta = \lVert \phi \rVert$, $u = \phi/\theta$ 로 분해한 뒤 써야 하고,
$\theta \to 0$ 에서 이 분해 자체가 0/0 이다. 구현에서는 $\sin\theta/\theta$ 와
$(1-\cos\theta)/\theta^2$ 를 **Taylor 급수로 교체**해 $\phi$ 를 직접 받는 형태

$$
\exp(\hat{\phi}) = I + \frac{\sin\theta}{\theta}\hat{\phi} + \frac{1 - \cos\theta}{\theta^2}\hat{\phi}^2
  \;\xrightarrow[\theta \to 0]{}\; I + \hat{\phi} + \tfrac{1}{2}\hat{\phi}^2 \tag{6}
$$

를 쓴다. $\theta \lesssim 10^{-4}$ 에서 급수로 갈아타면 상대오차가 기계 정밀도 수준으로 유지된다.

### R5 — SE(3) 지수 사상

$\hat{\xi}$ 의 거듭제곱을 블록으로 계산한다. $\hat{\xi}^k =
\begin{bmatrix} \hat{\omega}^k & \hat{\omega}^{k-1}v \\ 0 & 0\end{bmatrix}$ ($k \ge 1$) 임을 귀납법으로
확인하고 급수에 넣으면

$$
\exp(\hat{\xi}\theta) = \begin{bmatrix}
  \sum_k \frac{(\hat{\omega}\theta)^k}{k!} &
  \left(\sum_{k\ge1} \frac{\theta^k \hat{\omega}^{k-1}}{k!}\right) v \\ 0 & 1 \end{bmatrix}.
$$

좌상 블록은 R1 이다. 우상 블록의 급수를 R1 과 같은 방식으로 $I$, $\hat{\omega}$, $\hat{\omega}^2$
성분으로 모으면 (4)의 $G(\theta)$ 가 나온다. 전개는 문제 P1 로 남긴다.

**기하적 읽기**: $G(\theta)v$ 는 "축 주위로 돌면서 축 방향으로 미끄러진" 나선 운동(screw motion)의
평행이동이다. $\omega = 0$ 인 순수 평행이동은 (4)가 $G \to I\theta$ 로 퇴화하는 별도 경우이며,
이때도 지수 사상은 잘 정의된다.

## 증명 스케치

### R2 — 지수 사상의 전사성 (Euler 의 회전 정리)

**가설** H1: $R^\top R = I$. H2: $\det R = +1$.
**결론** C: $R$ 은 고윳값 1 에 대응하는 실수 고유벡터 $u$ 를 갖고, $u$ 에 직교하는 평면에서
평면 회전으로 작용한다. 따라서 $R = \exp(\hat{u}\theta)$.

**전략**: $\det(R - I) = 0$ 을 직접 보여 고윳값 1 의 존재를 얻고, 불변 축의 직교여공간으로 환원한다.

1. **고윳값 1 의 존재.** H1·H2 로
   $$
   \det(R - I) = \det(R^\top)\det(R - I) = \det(R^\top R - R^\top) = \det(I - R^\top)
     = \det\!\big((I-R)^\top\big) = \det(I - R) = (-1)^3\det(R - I),
   $$
   즉 $\det(R-I) = -\det(R-I)$ 이므로 $\det(R - I) = 0$. 따라서 $Ru = u$ 인 $u \ne 0$ 이 있다.
   정규화해 $\lVert u \rVert = 1$ 로 둔다. (여기서 **홀수 차원**이 결정적이다 — $(-1)^n$ 의 부호가
   $n$ 이 짝수면 $+1$ 이 되어 논증이 무너진다. $SO(2)$·$SO(4)$ 에 그대로 옮길 수 없다.)
2. **평면으로의 환원.** $u^\perp$ 는 $R$-불변이다: $x \perp u$ 면 $\langle Rx, u\rangle =
   \langle Rx, Ru\rangle = \langle x, u \rangle = 0$. $u^\perp$ 의 정규직교기저에서 $R$ 의 제한은
   $2\times2$ 직교행렬이고 행렬식이 $+1$ 이므로 어떤 $\theta$ 에 대한 평면 회전이다.
3. **지수로 쓰기.** $\{u, e_1, e_2\}$ 기저에서 $R = \operatorname{diag}(1, R_{2\times2}(\theta))$ 이고,
   같은 기저에서 $\exp(\hat{u}\theta)$ 도 같은 형태다(R1 에 대입해 확인). 기저 무관하게 두 행렬이
   일치하므로 C.
4. **치역의 범위.** $\theta$ 를 $[0, \pi]$ 로 제한할 수 있다: $\exp(\hat{u}\theta) =
   \exp(\widehat{(-u)}(-\theta))$ 이고 $\theta \mapsto \theta + 2\pi$ 가 같은 회전을 주므로.
   $\theta = \pi$ 에서는 $u$ 와 $-u$ 가 같은 회전을 주어 **유일성이 깨진다** — 이것이 R3 의 특이점이다.

**가설을 지우면**: H2($\det = +1$)를 빼면 반사가 포함되어 2단계의 $2\times2$ 블록이 행렬식 $-1$ 이
될 수 있고, 그런 변환은 어떤 $\exp(\hat{\omega}\theta)$ 로도 쓸 수 없다($\exp$ 의 상은 항상
$\det = +1$). 즉 $O(3)$ 에서는 정리가 거짓이다.

생략한 기술적 단계: 실수 직교행렬의 블록 대각화 정리. Barfoot ch.7 또는 MLS ch.2 의 해당 보조정리로.

### R4 — 전역 좌표가 없다는 논증 [D2]

1. 단위 사원수 $q$ 에 대응하는 회전 $R(q)$ 는 $R(q) = R(-q)$ 이므로 $S^3 \to SO(3)$ 은 2:1 이다.
2. 이 사상은 매끄럽고 전사이며 국소 미분동형이므로 $SO(3) \cong S^3/\{\pm 1\} = \mathbb{RP}^3$.
3. $S^3$ 이 콤팩트하고 몫사상이 연속이므로 $SO(3)$ 은 **콤팩트**하다.
4. $\mathbb{R}^3$ 은 콤팩트하지 않고 미분동형은 콤팩트성을 보존하므로 $SO(3) \not\cong \mathbb{R}^3$.
   따라서 전역적으로 매끄럽고 전단사인 3-매개변수 좌표계는 **존재할 수 없다**.
5. 결과: 모든 3-매개변수 표현은 특이점을 갖는다 — 오일러 각은 짐벌 락, 지수 좌표는 $\theta = \pi$
   (와 $\theta = 2\pi$ 에서 야코비안 퇴화). 피하는 방법은 특이점을 없애는 것이 아니라
   **과매개화(사원수·회전행렬) + 국소 좌표로 증분만 표현**하는 것이다. 이 전략이
   `c1-manifold-optimization` 과 `c5-manifold-estimation` 의 전체 설계다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R5)** (4)의 $G(\theta)$ 를 끝까지 전개하라. 급수
$\sum_{k\ge1} \theta^k \hat{\omega}^{k-1}/k!$ 를 $I$, $\hat{\omega}$, $\hat{\omega}^2$ 성분으로
분리해 각 계수가 $\theta$, $1-\cos\theta$, $\theta - \sin\theta$ 가 됨을 보여라.
*해답 스케치*: $k$ 를 1, 짝수, 홀수($\ge 3$)로 나누고 (1)로 거듭제곱을 축약한 뒤 R1 의 급수와
같은 방식으로 모은다. $\hat{\omega}^2$ 계수에서 $\theta$ 와 $\sin\theta$ 급수의 차가 나온다.

**P2 (증명, ★★★, R2)** $SO(2)$ 와 $SO(4)$ 에서 R2 의 1단계 논증이 어디서 무너지는지 정확히
쓰고, $SO(4)$ 의 회전이 일반적으로 "한 축에 대한 한 번의 회전"이 아님을 반례로 보여라.
*해답 스케치*: $\det(R-I) = (-1)^n \det(R-I)$ 에서 $n$ 이 짝수면 항등식이 되어 정보가 없다.
$SO(4)$ 에서는 서로 직교하는 두 평면에서 각각 다른 각으로 도는 **이중 회전**을 쓴다
(블록 대각 $\operatorname{diag}(R_2(\alpha), R_2(\beta))$, $\alpha \ne \beta$, 고윳값 1 없음).

**P3 (계산, ★, R1·R3)** 다음 행렬의 지수 좌표 $(\theta, u)$ 를 구하라.
$$R = \begin{bmatrix} 0 & 0 & 1 \\ 1 & 0 & 0 \\ 0 & 1 & 0 \end{bmatrix}$$
*정답*: $\operatorname{tr} R = 0$ 이므로 $\theta = \arccos(-1/2) = 2\pi/3 \approx 2.0943951$,
$u = (1, 1, 1)/\sqrt{3} \approx (0.57735027, 0.57735027, 0.57735027)$.
허용오차 $10^{-7}$. 검산: (2)에 넣어 $R$ 을 복원하고 $\lVert \exp(\hat{u}\theta) - R \rVert_F < 10^{-12}$.

**P4 (구현, ★★, R1·R3·R5)** $\phi \in \mathbb{R}^3$ 를 받는 `exp_so3(phi)`, `log_so3(R)` 와
$\xi \in \mathbb{R}^6$ 를 받는 `exp_se3(xi)` 를 쓰라. 작은 각 분기((6))와 $\theta \approx \pi$
분기를 모두 처리해야 한다.
*루브릭*: ⓐ $\theta = 0$ 에서 `nan` 이 나오지 않는다 ⓑ $\theta = \pi$ 근방에서 축의 상대오차가
$10^{-6}$ 이하다 ⓒ 왕복 오차가 재현 과제의 수용 기준을 만족한다 ⓓ $\theta$ 분기 경계가
문서화되어 있고 임의 상수가 아니라 근거(기계 정밀도 기준)로 선택되었다.

**P5 (반례, ★★, R4)** "지수 좌표 $\phi \in \mathbb{R}^3$ 는 $SO(3)$ 의 전역 좌표다"는 주장이
틀렸음을 **두 가지 서로 다른 방식**으로 보여라: (i) 단사성이 깨지는 구체적 $\phi, \phi'$ 쌍,
(ii) 지수 사상의 미분(좌 야코비안)의 행렬식이 0 이 되는 $\theta$.
*성질 체크리스트*: (i) 은 $\theta$ 와 $\theta + 2\pi$, 또는 $\theta = \pi$ 에서 $\pm u$ 를 쓴다.
(ii) 는 $\det J_l(\theta u) = 2(1 - \cos\theta)/\theta^2$ 를 쓰고 $\theta = 2\pi$ 를 찾으면 된다.

**P6 (논문, ★★, R3·R5)** Forster et al. 2017 의 II·III 절을 읽고, 저자들이 우 야코비안
$J_r$ 을 어디에 쓰는지, 그리고 회전 오차를 유클리드 공간에서 단순히 뺄 때 생기는 문제가 무엇인지
각각 3문장 이내로 쓰라. 그 선택이 틀렸다면 무엇이 먼저 깨지겠는가?
*루브릭*: 바이어스 재선형화와 불확실성 전파에서 쓰인다는 점, 그리고 $SO(3)$ 이 벡터공간이 아니라
덧셈이 군 연산과 맞지 않는다는 점을 짚으면 통과. "비선형이라서"만 쓰면 미달.

## 논문 읽기

**필독 2편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Solà, Deray & Atchuthan, "A micro Lie theory for state estimation in robotics" (2018, arXiv)**
   — 역할: `표준(standard)`. <https://arxiv.org/abs/1812.01537>
   추가 질문: ⓐ 이 글의 $\oplus$·$\ominus$ 표기를 이 레슨의 $\exp$·$\log$ 표기로 옮겨 쓰면?
   ⓑ 좌 야코비안과 우 야코비안의 차이가 추정 문제에서 실제로 무엇을 바꾸는가?
2. **Forster, Carlone, Dellaert & Scaramuzza, "On-manifold preintegration for real-time
   visual-inertial odometry" (2017, IEEE T-RO)** — 역할: `원전(seminal)`.
   <https://arxiv.org/abs/1512.02363> (II·III 절만)
   추가 질문: ⓐ 매니폴드 표기를 쓰지 않았다면 어느 식이 틀렸겠는가?
   ⓑ 저자들이 재현에 필요한 정보 중 빠뜨린 것이 있는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R1 (수치 검증).** 계산 예산: 노트북 CPU 1분 이내, numpy 만.

P4 에서 쓴 `exp_so3`/`log_so3`/`exp_se3` 가 아래 **네 조건을 모두** 만족해야 통과다.

1. **왕복 (일반 영역)**: $\lVert \phi \rVert \in (10^{-8},\ \pi - 10^{-3})$ 에서 균등 추출한
   회전 벡터 $10^5$ 개에 대해 $\max \lVert \log(\exp(\hat{\phi})) - \phi \rVert_\infty < 10^{-12}$.
2. **왕복 ($\theta \to \pi$)**: $\lVert \phi \rVert \in (\pi - 10^{-6},\ \pi)$ 에서 $10^3$ 개에 대해
   회전 자체의 오차 $\lVert \exp(\widehat{\log(R)}) - R \rVert_F < 10^{-6}$
   (축의 부호는 $\theta = \pi$ 에서 유일하지 않으므로 **벡터가 아니라 회전으로** 비교한다).
3. **작은 각**: $\lVert \phi \rVert = 10^{-10}$ 에서 $\exp(\hat{\phi})$ 가 `nan` 없이
   $\lVert \exp(\hat{\phi}) - (I + \hat{\phi}) \rVert_F < 10^{-18}$ 를 만족.
4. **미분 검증**: $\phi = 0$ 에서 $\exp$ 의 미분이 항등이다 — 유한차분으로 얻은
   $\partial \log(\exp(\hat{\epsilon}))/\partial \epsilon$ 이 $I$ 와 $10^{-7}$ 이내로 일치.
   (일반 $\phi$ 에서의 야코비안은 `c1-lie-group-derivatives` 에서 다룬다.)

**비교 대상**: `scipy.spatial.transform.Rotation` 의 `from_rotvec`/`as_rotvec` 와 같은 입력에서
회전행렬이 $10^{-12}$ 이내로 일치해야 한다(성분 순서 규약 차이에 주의).

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 작은 각에서 `nan` 또는 0/0 | $\theta$ 로 나누는 항을 급수로 교체하지 않음 | $\theta = 10^{-12}$ 를 직접 넣어 본다 |
| $\theta \approx \pi$ 에서 축이 튄다 | (3)의 $R - R^\top$ 가 0 으로 소멸 — 상쇄 오차 | $\theta$ 를 $\pi$ 로 쓸어가며 축 오차를 로그 도표로 그린다 |
| 왕복 오차가 반복마다 커진다 | 수치 오차로 $R$ 이 $SO(3)$ 에서 벗어남 | $\lVert R^\top R - I \rVert_F$ 를 추적하고 SVD 로 재투영한다 |
| 부호가 뒤집힌다 | $\hat{\omega}x = \omega \times x$ 규약 위반(skew 부호) | $\hat{e}_1 e_2 = e_3$ 인지 확인한다 |

## 열린 문제

- **(열린 문제) 불확실성이 있을 때 어떤 국소 좌표가 최선인가** — R4 가 전역 좌표를 금지하므로
  실무는 증분을 국소 좌표로 표현한다. 그런데 큰 회전 불확실성에서는 국소 가우시안 가정 자체가
  무너지고($\theta$ 의 분포가 $[0,\pi]$ 에 퍼지면 접공간 가우시안이 의미를 잃는다), 어떤
  재추적(retraction)이 추정 일관성을 가장 잘 보존하는지에 대한 일반 이론이 없다. 현재 접근:
  [Barfoot SER ch.7](https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf) 의 좌/우 불확실성 표현,
  [불변 EKF](https://arxiv.org/abs/1410.1465). 비어 있는 자리: 큰 불확실성 영역에서의 선택 기준.
- **(열린 문제) 리 군 구조를 학습 모델에 넣는 것의 실제 이득** — 등변(equivariant) 아키텍처가
  데이터 증강보다 언제 더 나은지에 대한 정량적 기준이 로보틱스 규모 데이터에서는 확립되지 않았다.
  이 질문은 `c7-learned-correspondence-slam` 과 `s4-pretrained-representations` 에서 다시 나온다.
- **(열린 문제) $SE(3)$ 위 비볼록 문제의 전역 최적성 인증 범위** — 포즈 그래프에서는 쌍대 완화가
  타이트한 조건이 알려졌지만(`c5-robust-global-estimation` 의
  [SE-Sync](https://arxiv.org/abs/1612.07386)), 일반적인 $SE(3)$ 비볼록 문제로 확장되지 않았다.

## 개념 점검

`rc quiz c1-so3-se3-exponential` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c1-so3-se3-exponential-quiz
questions:
  - id: q1
    type: short
    prompt: "단위 벡터 $\\omega$ 에 대해 $\\hat{\\omega}^3$ 을 $\\hat{\\omega}$ 로 나타내면?"
    answer: ["-w", "-ω", "-omega", "-hat w", "-ŵ", "-w_hat", "-\\hat{\\omega}"]
    explanation: "$\\hat{\\omega}^2 = \\omega\\omega^\\top - I$ 이므로 $\\hat{\\omega}^3 = \\hat{\\omega}(\\omega\\omega^\\top - I) = -\\hat{\\omega}$. 이 항등식이 Rodrigues 공식에서 급수를 닫는다."
    concept: { front: "단위 $\\omega$ 에 대한 $\\hat{\\omega}^3$", back: "$-\\hat{\\omega}$ — 거듭제곱이 주기 4로 닫히므로 지수 급수가 세 항으로 줄어든다" }
  - id: q2
    type: single
    prompt: "로그 사상 $\\hat{\\omega} = (R - R^\\top)/(2\\sin\\theta)$ 가 $\\theta \\to \\pi$ 에서 무너지는 이유는?"
    choices:
      - "$\\arccos$ 의 정의역을 벗어나기 때문"
      - "$R - R^\\top$ 가 0 으로 소멸해 축 정보가 사라지기 때문"
      - "$R$ 이 더 이상 직교행렬이 아니기 때문"
      - "행렬 지수 급수가 수렴하지 않기 때문"
    answer: 1
    explanation: "$\\theta = \\pi$ 에서 $R$ 은 대칭이 되어 $R - R^\\top = 0$ 이고 $\\sin\\theta = 0$ 이다. 분자와 분모가 함께 소멸하므로 축을 (R+I) 쪽에서 따로 복원해야 한다. $\\pm u$ 가 같은 회전을 주어 유일성도 깨진다."
    concept: { front: "지수 좌표의 특이점 두 곳", back: "$\\theta \\to 0$ (축 미정의, 0/0) 과 $\\theta \\to \\pi$ (축 정보 소멸, $\\pm u$ 중복)" }
  - id: q3
    type: truefalse
    prompt: "적절한 매개화를 고르면 $SO(3)$ 에 특이점 없는 전역 3-매개변수 좌표계를 만들 수 있다."
    answer: false
    explanation: "$SO(3) \\cong \\mathbb{RP}^3$ 은 콤팩트이고 $\\mathbb{R}^3$ 은 콤팩트하지 않다. 미분동형은 콤팩트성을 보존하므로 전역 3-매개변수 좌표는 존재할 수 없다. 해법은 과매개화(사원수·회전행렬) + 국소 좌표로 증분 표현이다."
    concept: { front: "전역 3-매개변수 회전 좌표가 없는 이유", back: "$SO(3)$ 은 콤팩트($\\cong \\mathbb{RP}^3$), $\\mathbb{R}^3$ 은 아니다 — 미분동형 불가" }
  - id: q4
    type: single
    prompt: "$\\operatorname{tr} R = 0$ 인 회전행렬의 회전각은?"
    choices: ["$\\pi/3$", "$\\pi/2$", "$2\\pi/3$", "$\\pi$"]
    answer: 2
    explanation: "$\\theta = \\arccos((\\operatorname{tr} R - 1)/2) = \\arccos(-1/2) = 2\\pi/3$. 문제 P3 의 순환 치환 행렬이 이 경우다."
```

## 이 단계 공부법

1. **표기를 먼저 고정한다 (30분)** — "전제와 기호" 표를 종이에 옮겨 쓰고 (1)의 두 항등식을
   직접 전개해 확인한다. 이후 모든 모듈이 이 표기를 쓴다.
2. **유도를 따라 쓰지 말고 다시 쓴다 (90분)** — R1 을 책이나 본문을 덮고 백지에서 재구성한다.
   짝수 급수가 $1 - \cos\theta$ 가 되는 지점에서 막히면 그 지점만 다시 읽는다.
   Barfoot ch.7 과 Modern Robotics ch.3.2 를 **같은 결과의 다른 표기**로 대조해 읽는다.
3. **증명은 전략부터 외운다 (60분)** — R2 의 1단계($\det(R-I) = 0$)는 한 줄 트릭이다. 트릭 자체보다
   "홀수 차원이 왜 필요한가"를 기억한다. P2 를 풀면 그 자리가 보인다.
4. **구현으로 특이점을 손으로 만난다 (90분)** — P4·재현 과제를 먼저 **분기 없이** 구현해
   $\theta \to 0$ 과 $\theta \to \pi$ 에서 깨지는 것을 직접 본 뒤 분기를 넣는다.
   깨지는 것을 보지 않고 넣은 분기는 기억에 남지 않는다.
5. **논문은 표기 대조로 읽는다 (120분)** — Solà et al. 를 먼저 읽고 $\oplus/\ominus$ 를 이 레슨의
   $\exp/\log$ 로 옮겨 적는다. 그 다음 Forster et al. II·III 절에서 그 표기가 실제 추정 문제에서
   어떻게 쓰이는지 본다. 논문당 1페이지 노트는 **반드시** 쓴다 — 쓰지 않으면 다음 모듈에서 다시 읽게 된다.
6. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제"를 읽고 하나를 골라 왜 아직 안 풀렸는지
   한 문단으로 쓴다. 이 습관이 연구 주제 선택으로 이어진다.

**통과 기준**: 백지에서 (2)와 (4)를 유도할 수 있고, R2 의 증명 전략을 말할 수 있고, 재현 과제의
네 조건을 모두 만족하는 코드를 갖고 있고, 논문 2편의 노트가 있다.
