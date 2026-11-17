---
id: s2-grasp-mechanics
title: 접촉 역학과 파지 안정성
summary: >-
  파지를 렌치 공간(wrench space)의 볼록 기하 문제로 환원한다. 마찰 원뿔을 유한 생성자로 바꾸고,
  force closure 가 "생성자들이 렌치 공간을 양으로 생성한다" 즉 "원점이 볼록 포의 내부에 있다"와
  동치임을 분리 초평면으로 증명한 뒤 LP 판정으로 옮긴다. Ferrari–Canny 품질 지표를 유도하고
  단위 원판의 대심 파지에서 닫힌 형태로 풀어, 그 지표가 마찰계수에 대해 **단조가 아니라**
  $\mu = 2^{1/4}$ 에서 최대 $\sqrt2 - 1$ 을 갖는다는 것까지 간다. 마지막으로 caging 을 force
  closure 와 분리한다. 재현 과제에서 force closure 가능 영역을 접촉점 수에 대해 도표화한다.
objectives:
  - 마찰 원뿔을 유한 생성자로 이산화하고 접촉 렌치를 렌치 공간의 점으로 쓸 수 있다.
  - force closure 가 "원점이 생성자 볼록 포의 내부"와 동치임을 분리 초평면으로 증명할 수 있다.
  - 그 판정을 선형계획으로 옮기고 rank 조건이 왜 따로 필요한지 설명할 수 있다.
  - Ferrari–Canny 지표를 유도하고 단위 원판 대심 파지에서 닫힌 형태로 계산할 수 있다.
  - caging 과 force closure 를 구성공간의 언어로 분리하고 둘 중 어느 것도 다른 것을 함의하지 않음을 예로 보일 수 있다.
prerequisites: [c2-contact-dynamics]
difficulty: 5
estimated_minutes: 470
tags: [manipulation, grasping, friction-cone, force-closure, wrench-space, caging, research]
activities:
  - id: s2-grasp-mechanics-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 100
  - id: s2-grasp-mechanics-papers
    kind: paper
    title: 필독 논문 2편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 120
  - id: s2-grasp-mechanics-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 2 · 계산 2 · 구현 1 · 반례 1)
    estimated_minutes: 150
  - id: s2-grasp-mechanics-reproduction
    kind: reproduction
    title: 재현 과제 — force closure 의 LP 판정과 가능 영역 도표 (R2)
    estimated_minutes: 80
  - id: s2-grasp-mechanics-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 20
resources:
  - title: "Murray, Li & Sastry, A Mathematical Introduction to Robotic Manipulation"
    kind: book
    note: ch.5 (Multifingered Hand Kinematics) — 5.2 의 접촉 모델과 5.3 의 파지 제약. (공식 URL 미확인)
  - title: "Prattichizzo & Trinkle — Grasping (Springer Handbook of Robotics, 2016)"
    url: https://doi.org/10.1007/978-3-319-32552-1_38
    kind: notes
    note: 이 레슨의 2순위 입구. 접촉 모델·force closure·품질 지표의 표준 정리.
  - title: "SciPy"
    url: https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs.html
    kind: code
    note: 재현 과제의 LP 는 `scipy.optimize.linprog(method="highs")`, 볼록 포는 `scipy.spatial.ConvexHull`.
papers:
  - id: ferrari1992-grasp-quality
    required: true
    role: seminal
    note: "§2-3"
  - id: rodriguez2012-caging
    required: true
    role: standard
    note: "§1-2, §6"
  - id: nguyen1988-force-closure
    role: seminal
  - id: mishra1987-positive-grips
    role: seminal
  - id: rimon1998-mobility
    role: standard
  - id: bicchi2000-grasping-review
    role: survey
---

# 접촉 역학과 파지 안정성

## 전제와 기호

이 모듈의 첫 레슨이다. 권장 선수는 C1–C4 와 C6 이며, 특히 다음을 전제한다:

- `c2-contact-dynamics` — 상보성 조건(법선 간격 $\phi \ge 0$, 법선력 $\lambda \ge 0$,
  $\phi\lambda = 0$)과 쿨롱 마찰 원뿔. 이 레슨은 그 **정적(static)** 측면만 쓴다.
- `c6-tamp` — 접촉 모드가 $3^{n_c}$ 개라는 것(그 레슨의 R3). 여기서는 모드를 고정하고
  **힘의 평형**만 본다.
- 볼록해석: 볼록 원뿔, 볼록 포, 분리 초평면 정리, Farkas 보조정리, LP 쌍대성
  (권장 선수 `r0-convex-optimization`).

표기(S2 모듈 전체에 고정):

| 기호 | 뜻 |
|---|---|
| $\mathcal{B} \subset \mathbb{R}^d$ | 물체. 평면은 $d = 2$, 공간은 $d = 3$ |
| $p_i$ | 접촉점 $i$ 의 위치(물체 좌표계) |
| $\hat n_i$ | 접촉점 $i$ 에서 물체로 **들어가는** 단위 법선 |
| $\mu$ | 마찰계수. $\alpha = \arctan\mu$ 는 마찰 원뿔의 반각 |
| $FC_i$ | 접촉 $i$ 의 마찰 원뿔 $\{f : \lVert f_t\rVert \le \mu f_n,\ f_n \ge 0\}$ |
| $w = (f, \tau)$ | 렌치. 평면은 $w \in \mathbb{R}^3$($\tau$ 는 스칼라), 공간은 $\mathbb{R}^6$ |
| $W = \{w_1,\dots,w_m\}$ | 이산화한 **렌치 생성자** 집합 |
| $\mathcal{W} = \mathrm{cone}(W)$ | 생성자가 양으로 생성하는 원뿔 |
| $Q$ | Ferrari–Canny 품질 지표 (§R2) |
| $\mathcal{C}_{\mathcal{B}}$ | 물체의 구성공간(손가락을 장애물로 본다). caging 에 쓴다 |

**문제 정의 (force closure).** 접촉점과 마찰계수가 주어졌을 때, **임의의** 외부 렌치
$w_{ext}$ 에 대해 마찰 원뿔 안의 접촉력 $f_i \in FC_i$ 가 존재해

$$
\sum_{i=1}^{n} w_i(f_i) \;+\; w_{ext} \;=\; 0
  \tag{1}
$$

을 만족하면 그 파지는 **force closure** 다. 즉 손이 물체에 가할 수 있는 렌치의 집합이
렌치 공간 **전체**여야 한다. 중요한 것은 이것이 **힘에 대한 조건이고 운동에 대한 조건이
아니라는 점**이다 — 그 구별이 R3(caging)의 출발점이다.

전제 둘을 명시한다.

- **(A1) 강체·점 접촉·쿨롱 마찰** — 접촉은 점이고 마찰은 쿨롱 모델을 따르며 물체는 강체다.
  면 접촉·변형체는 §R1 의 실패 모드에서 다룬다.
- **(A2) 접촉력의 상한 없음** — $f_n$ 에 상한이 없다. 상한이 있으면 force closure 는
  이진 성질이 아니라 "얼마나 큰 외란까지"의 **정량** 문제가 되고, 그것이 R2 의 $Q$ 다.

## 시작 전 자가 진단

이 모듈의 첫 레슨이므로 준비 상태를 먼저 점검한다. **선수 레슨은 잠겨 있지 않다** — 아래를
전부 풀 수 있으면 권장 선수를 건너뛰고 바로 시작해도 된다. **두 문항 이상 막히면** 괄호 안의
레슨으로 돌아가는 편이 빠르다.

1. 평면에서 위치 $p = (1, 0)$ 에 힘 $f = (0, 2)$ 를 가할 때 원점에 대한 토크는?
   공간에서 $p = (1,0,0)$, $f = (0,0,3)$ 이면 토크 벡터는? (`c1-twists-wrenches-adjoint`)
   **정답**: 평면 $\tau = p_x f_y - p_y f_x = 1\cdot2 - 0 = 2$.
   공간 $\tau = p \times f = (0\cdot3 - 0\cdot0,\ 0\cdot0 - 1\cdot3,\ 0) = (0, -3, 0)$.
2. 쿨롱 마찰 원뿔을 법선력 $f_n$ 과 접선력 $f_t$ 로 쓰고, 반각이 $\arctan\mu$ 인 이유를
   한 줄로 설명하라. (`c2-contact-dynamics`)
   **정답**: $FC = \{(f_n, f_t) : \lVert f_t \rVert \le \mu f_n,\ f_n \ge 0\}$. 원뿔 표면에서
   $\lVert f_t\rVert / f_n = \mu$ 이고 그 비가 법선에서 재는 각의 탄젠트이므로 반각은 $\arctan\mu$.
3. $\mathbb{R}^3$ 의 점 네 개가 주어졌다. "원점이 그 볼록 포의 **내부**에 있다"를 선형
   부등식·등식으로 쓰면? (`r0-convex-optimization`)
   **정답**: $\exists\lambda$ 로 $\sum_j \lambda_j w_j = 0$, $\sum_j \lambda_j = 1$,
   $\lambda_j > 0$ (모두 **엄격히** 양수). 추가로 점들이 $\mathbb{R}^3$ 를 **아핀 생성**해야
   한다(그렇지 않으면 내부가 비어 있다).
4. 분리 초평면 정리를 볼록집합 $K$ 와 그에 속하지 않는 점 $x$ 에 대해 진술하라.
   (`r0-convex-optimization`)
   **정답**: $K$ 가 닫힌 볼록집합이고 $x \notin K$ 이면 $u \ne 0$ 과 $c$ 가 있어
   $u^\top x > c \ge u^\top y$ ($\forall y \in K$). 원뿔이면 $c = 0$ 으로 잡을 수 있다.
5. $\mathrm{rank}$ 가 3 미만인 $m \times 3$ 행렬의 행들이 $\mathbb{R}^3$ 를 양으로 생성할 수
   있는가? (`r0-linear-algebra-decompositions`)
   **정답**: 할 수 없다. 양의 생성은 선형 생성을 함의하므로 rank 가 3 이어야 한다.
   이것이 LP 판정에 **rank 조건을 따로** 넣어야 하는 이유다(§R1).

전부 풀렸다면 바로 `## 핵심 결과` 로 간다. 2·4 번이 막히면 `r0-convex-optimization` 을,
1 번이 막히면 `c1-twists-wrenches-adjoint` 를 먼저 본다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (force closure 의 볼록 기하 판정) [D3]** — (A1)(A2) 아래, 마찰 원뿔을 $k$ 개의
  모선(edge)으로 이산화해 얻은 렌치 생성자 $W$ 에 대해 다음이 **동치**다.
  (ⓐ) 파지가 force closure 다. (ⓑ) $\mathrm{cone}(W) = \mathbb{R}^{d'}$
  ($d' = 3$ 평면, $6$ 공간). (ⓒ) **원점이 $\mathrm{conv}(W)$ 의 내부에 있다.**
  (ⓓ) $u^\top w_j \le 0\ (\forall j)$ 를 만족하는 $u \ne 0$ 이 **없다**. 따라서 판정은
  $$\max_{\lambda,\,\epsilon}\ \epsilon \quad \text{s.t.}\quad
    W^\top \lambda = 0,\ \ \mathbf{1}^\top\lambda = 1,\ \ \lambda_j \ge \epsilon,\ \ \epsilon \ge 0
    \tag{2}$$
  라는 **선형계획**이고, force closure $\iff$ $\mathrm{rank}\,W = d'$ **그리고** $\epsilon^\ast > 0$ 다.
  rank 조건은 LP 로 흡수되지 않는다 — 이산화가 **보수적**(원뿔의 내부 근사)이라는 것도 함께.
- **R2 (Ferrari–Canny 지표와 그 비단조성) [D2]** — 접촉력의 크기를 정규화하면 품질 지표는
  "원점 중심의 가장 큰 내접구의 반지름"
  $$Q = \min_{\text{facets } (a,b) \text{ of } \mathrm{conv}(W)} \frac{-b}{\lVert a\rVert}
    \qquad (a^\top x + b \le 0) \tag{3}$$
  이고 $Q > 0 \iff$ force closure 다. 단위 원판의 **대심(antipodal) 두 접촉**에서는 닫힌 형태
  $$Q(\mu) \;=\; \frac{\sin\alpha\,\cos\alpha}{\sqrt{1 + \cos^2\alpha}},
    \qquad \alpha = \arctan\mu \tag{4}$$
  를 가지며, **$\mu$ 에 대해 단조가 아니다**: $\mu^\ast = 2^{1/4} = 1.189207115$ 에서
  최대 $Q_{\max} = \sqrt2 - 1 = 0.414213562$ 를 갖고 그 뒤 감소한다.
- **R3 (caging 과 force closure 의 분리) [D2]** — caging 은 **힘이 아니라 구성공간**의
  성질이다: 손가락을 장애물로 본 물체의 구성공간 $\mathcal{C}_{\mathcal{B}}$ 에서 현재 구성이
  있는 자유 성분이 **유계**이면 cage 다. 두 성질은 서로를 함의하지 않는다 — force closure 가
  아니면서 cage 인 배치(느슨한 우리)와, cage 가 아니면서 force closure 인 배치(마찰로만
  붙잡는 두 점)가 모두 존재한다. 다만 **일부 cage 는 손가락을 좁히면 force closure 로
  수렴**하고, 그 부류를 식별하는 것이 [Rodriguez et al. 2012](https://doi.org/10.1177/0278364912442972)
  의 결과다.
- **R4 (무마찰 하한) [D1]** — $\mu = 0$ 이면 force closure 에 필요한 최소 접촉점 수는 평면
  4개, 공간 7개다([Mishra, Schwartz & Sharir 1987](https://doi.org/10.1007/bf01840373)).
  그리고 **원판·구는 무마찰에서 접촉점을 아무리 늘려도 force closure 가 불가능하다** —
  모든 법선이 중심을 지나 토크 성분이 항등적으로 0 이기 때문이다(§R1 의 실패 모드).

## 유도

### R1 — 마찰 원뿔에서 렌치 생성자로

**접촉 렌치.** 접촉 $i$ 에서 힘 $f_i$ 를 가하면 물체에 작용하는 렌치는

$$
w_i(f_i) \;=\; \begin{bmatrix} f_i \\ p_i \times f_i \end{bmatrix}
  \quad (d = 3), \qquad
w_i(f_i) \;=\; \begin{bmatrix} f_i \\ p_{i,x} f_{i,y} - p_{i,y} f_{i,x} \end{bmatrix}
  \quad (d = 2).
  \tag{5}
$$

$w_i$ 는 $f_i$ 에 대해 **선형**이다. 따라서 $f_i$ 가 볼록 원뿔 $FC_i$ 를 달리면 $w_i$ 도
볼록 원뿔을 달리고, 손 전체가 가할 수 있는 렌치 집합은 그 원뿔들의 **민코프스키 합**

$$
\mathcal{W} \;=\; \Big\{\textstyle\sum_i w_i(f_i) \;:\; f_i \in FC_i\Big\}
  \;=\; \mathrm{cone}\Big(\bigcup_i w_i(\mathrm{ext}\,FC_i)\Big)
  \tag{6}
$$

이다. 둘째 등식이 **이산화의 근거**다: 볼록 원뿔의 민코프스키 합은 각 원뿔의 **모선(extreme
ray)** 들이 양으로 생성하는 원뿔과 같다. 평면에서 $FC_i$ 의 모선은 정확히 둘
($\hat n_i$ 를 $\pm\alpha$ 회전), 공간에서는 **무한히 많다**(원뿔의 테두리가 원) —
그래서 공간에서는 $k$ 개의 모선으로 **내부 근사**하고, 그 근사는 항상 보수적이다
($\mathcal{W}_k \subseteq \mathcal{W}$, 따라서 "force closure 라고 판정하면 참이고,
아니라고 판정한 것이 실제로는 force closure 일 수 있다").

**(1)과 $\mathcal{W}$ 의 관계.** (1)은 "$-w_{ext} \in \mathcal{W}$" 와 같다.
$w_{ext}$ 가 임의여야 하므로

$$
\text{force closure} \iff \mathcal{W} = \mathbb{R}^{d'},
  \tag{7}
$$

즉 (ⓐ) $\iff$ (ⓑ)다. 이것이 R1 의 첫 동치이고, 나머지는 볼록 기하다(§증명 스케치).

**가정이 깨지는 곳 세 군데.**

1. **원판·구의 무마찰 파지.** 단위 원판에서 접촉점이 $p_i$, 들어가는 법선이 $\hat n_i = -p_i$
   이면 무마찰 힘은 $f_i = \lambda_i \hat n_i \parallel p_i$ 이고 토크는
   $p_{i,x}f_{i,y} - p_{i,y}f_{i,x} = \lambda_i(p_{i,x}(-p_{i,y}) - p_{i,y}(-p_{i,x})) = 0$ 이다.
   **모든 생성자의 토크 성분이 0** 이므로 $\mathrm{rank}\,W \le 2 < 3$ 이고, 접촉점을 아무리
   늘려도 force closure 가 아니다. 재현 과제 조건 2 가 이것을 $n = 12$ 까지 확인한다.
2. **면 접촉.** (A1)의 점 접촉을 버리면 접촉 영역이 2차원이고 "모선"이 유한 집합이 아니다.
   표준 우회는 접촉 영역을 **soft finger** 모델(법선 토크 항을 추가)이나 다각형 근사로 바꾸는
   것이고, 그러면 생성자 수가 늘어 (2)의 LP 는 그대로 쓸 수 있다. 바뀌는 것은 **보수성의
   크기**뿐이다.
3. **접촉력 상한.** (A2)를 버리면 force closure 는 이진 판정으로 쓸모가 줄어든다. 임의로 큰
   외란에 저항하려면 임의로 큰 접촉력이 필요하기 때문이다. 그래서 실무는 $\sum_i f_{n,i} \le 1$
   같은 정규화를 넣고 **얼마나 큰 외란까지 버티는지**를 재는데, 그 양이 R2 의 $Q$ 다.

### R2 — Ferrari–Canny 지표

**정의.** 접촉력을 정규화한다. $L^1$ 정규화 $\sum_i f_{n,i} \le 1$ 을 쓰면 가할 수 있는 렌치의
집합은 $\mathrm{conv}(W \cup \{0\})$ 이고, $L^\infty$ 정규화 $f_{n,i} \le 1$ 을 쓰면
각 접촉의 볼록 포들의 민코프스키 합이다. 어느 쪽이든 **유계 볼록 다면체** $P$ 가 나오고

$$
Q \;=\; \max\{\,r \ge 0 \;:\; B(0, r) \subseteq P \,\}
  \tag{8}
$$

로 정의한다. $P$ 가 다면체이면 $B(0,r) \subseteq P$ 는 "모든 면까지의 거리가 $r$ 이상"과 같고,
면이 $a^\top x + b \le 0$ ($b < 0$ 이면 원점이 그 면의 안쪽)로 주어지므로 원점에서 그 면까지의
거리는 $-b/\lVert a\rVert$ 다. 최솟값을 취하면 (3)이다. **$Q > 0 \iff$ 원점이 내부
$\iff$ force closure** 이므로, $Q$ 는 이진 판정의 **연속 확장**이다.

**단위 원판 대심 파지의 닫힌 형태.** $p_1 = (1,0)$, $p_2 = (-1,0)$, 들어가는 법선은
$\hat n_1 = (-1,0)$, $\hat n_2 = (1,0)$. 모선은 법선을 $\pm\alpha$ 회전한 단위 벡터이고
(5)로 토크를 계산하면 네 생성자는

$$
\begin{aligned}
A_\pm &= (-\cos\alpha,\ \mp\sin\alpha,\ \mp\sin\alpha), \\
B_\pm &= (\ \ \cos\alpha,\ \pm\sin\alpha,\ \mp\sin\alpha).
\end{aligned}
  \tag{9}
$$

(부호를 직접 확인하라 — $p_1$ 에서 토크는 $1\cdot f_y$, $p_2$ 에서는 $-1\cdot f_y$ 다.)
네 점의 합이 0 이므로 **원점은 이 사면체의 무게중심**이고, 따라서 네 면까지의 거리가 모두
같다. 면 $A_+A_-B_+$ 의 법선을 외적으로 구하면

$$
(A_- - A_+)\times(B_+ - A_+) = (0, 2s, 2s)\times(2c, 2s, 0) = (-4s^2,\ 4sc,\ -4sc),
  \qquad s = \sin\alpha,\ c = \cos\alpha,
$$

이고 $A_+$ 를 지나므로 상수항은 $(-4s^2)(-c) + (4sc)(-s) + (-4sc)(-s) = 4s^2c$ 다. 원점에서의
거리는

$$
\frac{4s^2 c}{\lVert(-4s^2, 4sc, -4sc)\rVert} = \frac{4s^2c}{4s\sqrt{s^2 + 2c^2}}
  = \frac{sc}{\sqrt{s^2 + 2c^2}} = \frac{\sin\alpha\cos\alpha}{\sqrt{1 + \cos^2\alpha}},
$$

즉 (4)다($s^2 + 2c^2 = 1 + c^2$). 수치 확인: $\mu = 1$ 에서 $\alpha = \pi/4$,
$Q = \tfrac12/\sqrt{3/2} = 1/\sqrt6 = 0.408248290$.

**비단조성.** $u = \cos^2\alpha$ 로 두면 $Q^2 = u(1-u)/(1+u)$ 이고

$$
\frac{d}{du}\frac{u(1-u)}{1+u} = \frac{1 - 2u - u^2}{(1+u)^2} = 0
  \;\Longrightarrow\; u^2 + 2u - 1 = 0 \;\Longrightarrow\; u = \sqrt2 - 1.
$$

그러면 $\tan^2\alpha = (1-u)/u = (2-\sqrt2)/(\sqrt2-1) = \sqrt2$ 이므로
$\mu^\ast = \tan\alpha = 2^{1/4}$ 이고, $Q_{\max}^2 = u(1-u)/(1+u) = (\sqrt2-1)^2$ 에서
$Q_{\max} = \sqrt2 - 1$ 이다. **마찰이 커질수록 파지가 좋아지는 것이 아니다.**

**가정이 깨지는 곳 — $Q$ 는 단위에 의존한다.** (3)의 "구"는 힘 성분과 토크 성분을 **같은
단위로** 취급한다. 실제로는 힘은 N, 토크는 N·m 이므로 $Q$ 는 **특성 길이의 선택**에
의존한다(토크를 $\tau/\ell$ 로 정규화해야 한다). $\ell$ 을 물체 지름으로 잡느냐 파지 폭으로
잡느냐에 따라 **같은 파지의 순위가 뒤집힌다.** 그리고 (4)의 비단조성은 모선 벡터를 **단위
길이**로 잡은 결과이기도 하다 — 법선력을 단위로 정규화하면($f_n = 1$, 즉 모선을
$1/\cos\alpha$ 배) $Q$ 가 $\mu$ 에 대해 단조 증가로 바뀐다. 문제 P5 가 이것을 다룬다.
**지표를 비교할 때 정규화를 명시하지 않으면 그 비교는 의미가 없다** — 학습 기반 파지에서
라벨을 만들 때 그대로 문제가 되고, `s2-learned-grasping` 에서 다시 나온다.

### R3 — caging: 힘이 아니라 구성공간

**정의.** 손가락을 고정 장애물로 보고 **물체**의 구성공간 $\mathcal{C}_{\mathcal{B}}$
(평면 강체면 $\mathbb{R}^2 \times S^1$, `c6-cspace-complexity` R2)를 생각하자. 현재 구성
$q_0$ 가 속한 자유 성분 $\mathcal{F}(q_0) \subseteq \mathcal{C}_{\mathcal{B},free}$ 가
**유계**이면 그 배치는 $q_0$ 를 **cage** 한다. 뜻: 물체가 손가락을 통과하지 않고는
무한히 멀리 갈 수 없다.

**두 성질은 독립이다.** 네 조합이 모두 실현된다.

| | force closure | force closure 아님 |
|---|---|---|
| **cage** | 세 손가락으로 꽉 쥔 원판 | 원판을 둘러싼 느슨한 네 손가락(움직일 수는 있으나 빠져나가지 못한다) |
| **cage 아님** | 마찰로 붙잡은 대심 두 점($\mu > 0$, R2) — 손가락을 벌리면 물체가 나간다 | 한 점 접촉 |

오른쪽 아래를 뺀 세 칸이 요점이다. 특히 **대심 두 점 파지는 force closure 지만 cage 가
아니다** — 자유 성분이 유계가 아니다(물체를 접선 방향으로 밀면 접촉을 유지한 채 멀어진다).
반대로 느슨한 우리는 아무 렌치도 저항하지 못하지만 물체를 잃지 않는다. **force closure 는
"어떤 외란도 즉시 막는다", caging 은 "결국 잃지 않는다"** 로 읽으면 구별이 남는다.

**왜 caging 이 쓸모 있는가.** force closure 는 접촉점의 **정확한** 위치와 법선을 요구하는데
그것은 지각 오차에 민감하다. caging 은 위치 오차에 **열려 있는 조건**(자유 성분의 유계성은
손가락을 조금 움직여도 유지된다)이므로 불확실성 아래에서 쓸 수 있다. Rodriguez et al. 은
한 걸음 더 나아가 **cage 를 좁히면 force closure 로 수렴하는 부류**를 식별했고, 그래서
"일단 가두고 조여라"라는 전략에 보장을 준다.

**가정이 깨지는 곳**: caging 판정은 구성공간의 **위상** 계산이므로
`c6-cspace-complexity` R4 의 비용을 그대로 물려받는다 — 평면 강체(3차원 C-space)에서는
계산 가능하지만 3차원 강체(6차원) + 다관절 손에서는 실용적 알고리즘이 없다. 그리고
"유계"는 **마찰을 전혀 쓰지 않는** 조건이라 마찰이 있으면 지나치게 보수적이다
(마찰만으로 유지되는 배치를 cage 가 아니라고 판정한다).

## 증명 스케치

### R1 — 네 조건의 동치

**가설** H1: (A1)(A2). H2: 생성자 집합 $W$ 는 유한하고 각 $w_j$ 는 어떤 $FC_i$ 의 모선에서
(5)로 얻었다. H3: 렌치 공간은 $\mathbb{R}^{d'}$ 이고 접촉력은 **독립적으로** 고를 수 있다.
**결론** C: (ⓐ) $\iff$ (ⓑ) $\iff$ (ⓒ) $\iff$ (ⓓ), 그리고 (2)의 LP 가 (ⓒ)를 판정한다.

**전략**: (ⓐ)$\Leftrightarrow$(ⓑ)는 정의 전개, (ⓑ)$\Leftrightarrow$(ⓓ)는 **분리 초평면**,
(ⓒ)$\Leftrightarrow$(ⓓ)는 원뿔과 볼록 포의 관계, (ⓒ)$\Leftrightarrow$LP 는 정의의 재기술이다.

1. **(ⓐ) $\Leftrightarrow$ (ⓑ).** (1)은 $-w_{ext} \in \mathcal{W}$ 와 동치다(유도 (7)).
   모든 $w_{ext}$ 에 대해 성립 $\iff$ $\mathcal{W} = \mathbb{R}^{d'}$.
2. **(ⓑ) $\Rightarrow$ (ⓓ).** $u \ne 0$ 이 $u^\top w_j \le 0\ \forall j$ 를 만족하면
   양의 결합에서도 $u^\top w \le 0$ 이므로 $\mathcal{W} \subseteq \{w : u^\top w \le 0\}$ 이고
   $\mathcal{W} \ne \mathbb{R}^{d'}$. 대우가 (ⓑ)$\Rightarrow$(ⓓ)다.
3. **(ⓓ) $\Rightarrow$ (ⓑ).** $\mathcal{W}$ 는 유한 생성 볼록 원뿔이므로 **닫혀 있다**
   (Minkowski–Weyl). $\mathcal{W} \ne \mathbb{R}^{d'}$ 이면 어떤 $v \notin \mathcal{W}$ 가 있고,
   닫힌 볼록 원뿔과 그 밖의 점에 분리 초평면 정리를 쓰면 $u \ne 0$ 로
   $u^\top v > 0 \ge u^\top w\ (\forall w \in \mathcal{W})$ 를 얻는다. 특히
   $u^\top w_j \le 0\ \forall j$ 이므로 (ⓓ)가 거짓이다. **닫힘성이 여기서 결정적이다** —
   유한 생성이 아니면(§실패 모드 2 의 면 접촉) 이 단계가 무너질 수 있다.
4. **(ⓒ) $\Leftrightarrow$ (ⓓ).** $0 \in \mathrm{int}\,\mathrm{conv}(W)$ 가 아니라고 하자.
   그러면 $\mathrm{conv}(W)$ 와 $\{0\}$ 을 분리하는 초평면(또는 지지 초평면)이 있어
   $u^\top w_j \le 0\ \forall j$ 인 $u \ne 0$ 이 존재한다. 역으로 그런 $u$ 가 있으면
   $\mathrm{conv}(W)$ 가 반공간 $\{u^\top x \le 0\}$ 에 들어가므로 원점은 내부가 아니다.
5. **(ⓒ) $\Leftrightarrow$ LP.** $0 \in \mathrm{int}\,\mathrm{conv}(W)$ 는
   "$\sum\lambda_j w_j = 0$, $\sum\lambda_j = 1$, $\lambda_j > 0$ 인 $\lambda$ 가 존재하고
   $W$ 가 $\mathbb{R}^{d'}$ 를 아핀 생성한다"와 같다. 앞 조건이 (2)의 $\epsilon^\ast > 0$,
   뒤 조건이 $\mathrm{rank}\,W = d'$ 다. **LP 는 rank 조건을 보지 못한다**: 모든 생성자가
   한 부분공간에 있으면 $\epsilon^\ast > 0$ 이면서도 force closure 가 아닐 수 있다
   (무마찰 원판이 정확히 그 경우다 — $\lambda$ 를 대칭으로 잡으면 합이 0 이 된다).
   그래서 구현은 **두 검사를 모두** 해야 한다.

**가설을 지우면**: H3 의 독립성을 빼면(예: 하나의 액추에이터가 두 손가락을 함께 구동) 가할 수
있는 렌치 집합이 원뿔이 아니라 그 **부분집합**이 되어 (6)이 등식이 아니게 되고, (2)는
**필요조건만** 준다. H2 의 유한성을 빼면 3단계의 닫힘성 논증을 다시 세워야 한다.
H1 의 강체 가정을 빼면 (5)의 선형성 자체가 깨진다(변형에 따라 $p_i$ 가 움직인다).

## 문제 세트

난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** (6)의 둘째 등식 — 볼록 원뿔들의 민코프스키 합이 모선들의 양의
생성과 같다 — 를 증명하라. 그 다음 평면 접촉의 모선이 정확히 두 개이고 공간 접촉의 모선이
무한히 많은 이유를 쓰라.
*해답 스케치*: 각 $f_i \in FC_i$ 를 모선의 음이 아닌 결합으로 쓰고 $w_i$ 의 선형성을 쓴다.
역 포함은 모선 자체가 $FC_i$ 에 속한다는 것. 평면 원뿔은 2차원이라 모선이 둘, 공간 원뿔은
단면이 원이라 극점이 연속이다.

**P2 (유도, ★★, R2)** (9)의 네 생성자를 부호까지 직접 유도하고, 그 네 점의 합이 0 임을
확인하라. 그 다음 (4)를 $\mu$ 로 다시 써서 $Q(\mu) = \mu/\big((1+\mu^2)\sqrt{1 + 1/(1+\mu^2)}\big)$
꼴로 정리하고 $\mu \to \infty$ 에서 $Q \to 0$ 임을 보이라.
*해답 스케치*: $s = \mu/\sqrt{1+\mu^2}$, $c = 1/\sqrt{1+\mu^2}$ 를 (4)에 넣는다.
$\mu \to \infty$ 에서 $c \to 0$ 이고 분자가 $sc \to 0$ 이다 — **모선이 접선 방향으로 누워
법선 성분을 잃는다**는 기하적 뜻을 함께 쓸 것.

**P3 (계산, ★, R2)** 단위 원판 대심 파지에서 $\mu = 0.1,\ 0.5,\ 1,\ 2$ 의 $Q$ 를 (4)로
구하고, $Q$ 를 최대화하는 $\mu^\ast$ 와 $Q_{\max}$ 를 구하라.
*정답*: $Q(0.1) = 0.070184512$, $Q(0.5) = 0.298142397$, $Q(1) = 1/\sqrt6 = 0.408248290$,
$Q(2) = 0.365148372$. 최대는 $\cos^2\alpha = \sqrt2 - 1$ 에서, 즉
$\mu^\ast = 2^{1/4} = 1.189207115$ 이고 $Q_{\max} = \sqrt2 - 1 = 0.414213562$.
허용오차 $10^{-9}$. 검산: $Q(1) < Q(\mu^\ast)$ 이고 $Q(2) < Q(1)$ — **비단조**임을 수치로 확인.

**P4 (계산, ★★, R1)** 단위 원판 위에 접촉 두 개를 각 $\theta_1, \theta_2$ 에 두었을 때
force closure 조건을 $\Delta\theta$ 와 $\alpha$ 로 쓰고, $\theta_1, \theta_2$ 가 독립 균등일
때의 force closure 확률을 닫힌 형태로 구하라.
*정답*: 삼각형 $O p_1 p_2$ 가 이등변이고 꼭지각이 $\Delta\theta$(두 각의 차를 $[0,\pi]$ 로
잡은 것)이므로 밑각이 $(\pi - \Delta\theta)/2$ 다. 현(chord)이 두 마찰 원뿔 안에 들어가는
조건은 $(\pi - \Delta\theta)/2 \le \alpha$, 즉 $\Delta\theta \ge \pi - 2\alpha$.
$\Delta\theta$ 는 $[0,\pi]$ 에서 균등하므로
$$\mathbb{P}[\text{force closure}] = \frac{2\alpha}{\pi} = \frac{2\arctan\mu}{\pi}.$$
$\mu = 1$ 이면 정확히 $1/2$. 허용오차: 몬테카를로 $2\times10^4$ 회에서 $\pm 2\,\mathrm{SE}$
(측정값 $\mu = 0.1/0.2/0.5/1.0$ 에서 $0.0625/0.1250/0.2951/0.4991$, 예측
$0.063451/0.125666/0.295167/0.500000$, 최대 $z = 0.55$).

**P5 (반례/증명, ★★, R2)** $Q$ 의 비단조성이 **모선의 정규화** 때문임을 보이라: 모선을
단위 벡터가 아니라 **법선 성분이 1** 이 되게($f_n = 1$, 즉 길이 $1/\cos\alpha$) 잡아 (4)를
다시 계산하고, 그 지표가 $\mu$ 에 대해 단조 증가함을 보이라. 어느 정규화가 "옳은가"에
답하고, 답이 **문제 설정에 의존한다**는 것을 설명하라.
*성질 체크리스트*: 새 지표는 $Q/\cos\alpha = \sin\alpha/\sqrt{1+\cos^2\alpha}$ 이고
$\alpha$ 에 대해 증가한다. "옳은" 정규화는 액추에이터의 한계가 **법선력**에 걸리는가
(그러면 $f_n = 1$) **총 힘 크기**에 걸리는가(그러면 단위 모선)에 따라 다르다. 토크의
특성 길이 $\ell$ 도 함께 선언해야 한다는 점을 쓸 것.

**P6 (증명, ★★, R1)** R1 증명 5단계의 주장 — LP 가 rank 조건을 보지 못한다 — 를 무마찰
단위 원판으로 구체화하라. $n$ 개의 등간격 접촉에 대해 $\epsilon^\ast > 0$ 인 $\lambda$ 를
명시적으로 구성하고, 그럼에도 force closure 가 아닌 이유를 쓰라.
*전략*: $\lambda_j = 1/n$ 로 잡으면 $\sum \lambda_j w_j = (\frac1n\sum \hat n_j,\ 0) = (0, 0)$
(등간격이므로 법선 합이 0). 따라서 (2)의 LP 는 $\epsilon^\ast = 1/n > 0$ 을 낸다. 그러나
모든 생성자의 토크가 0 이라 $\mathrm{rank}\,W = 2$ 이고 토크 방향 외란을 저항하지 못한다.

**P7 (구현, ★★, R1·R2)** 재현 과제의 LP 판정기와 $Q$ 계산기를 쓰라. 요구: (2)의 LP
(`scipy.optimize.linprog(method="highs")`), rank 검사, `scipy.spatial.ConvexHull` 로 (3).
*루브릭*: ⓐ 조건 1·2·3 의 수치가 일치한다 ⓑ rank 검사를 **빼면** 무마찰 원판이 force
closure 로 오판정되는 것을 보인다 ⓒ $Q$ 와 LP 의 $\epsilon^\ast$ 가 **같은 부호**를 주는지
확인하고 둘의 크기가 다른 이유를 쓴다 ⓓ 공간 접촉(원뿔을 $k$ 모선으로 이산화)에서 $k$ 를
8 → 32 로 늘릴 때 판정이 한 방향으로만 바뀌는 것(보수성)을 보인다.

**P8 (논문, ★★, R2·R3)** Ferrari & Canny 1992 와 Rodriguez et al. 2012 를 읽고,
(ⓐ) Ferrari–Canny 가 쓰는 정규화를 정확히 옮기고 이 레슨 (3)과 비교하라
(ⓑ) Rodriguez et al. 이 "cage 를 좁히면 force closure 로 수렴한다"를 어느 부류에 대해
증명하는지, 그 부류를 식별하는 조건이 **계산 가능**한지 쓰라.
*루브릭*: (ⓐ)에서 $L^1$ 과 $L^\infty$ 정규화의 차이와 토크 스케일링을 짚으면 통과.
(ⓑ)에서 결과가 **모든** cage 에 대한 것이 아니라는 점을 짚으면 통과. "좋은 지표다"만 쓰면 미달.

## 논문 읽기

**필독 2편.** 각 논문에 고정 질문 10개로 1페이지 노트를 쓴다(`lesson-standard.md` §5).

1. **Ferrari & Canny, "Planning optimal grasps" (1992, ICRA)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1109/ROBOT.1992.219918> (§2–3)
   *왜 읽는가*: R2 의 $Q$ 가 여기서 나온다. 특히 **정규화를 어디서 선택하는지**(총 힘 대
   접촉별 힘)와 그 선택이 최적 파지를 어떻게 바꾸는지가 요점이다.
   추가 질문: ⓐ 저자들의 지표를 (3)의 꼴로 다시 쓰면 무엇이 달라지는가?
   ⓑ 토크 성분의 단위를 어떻게 다루는가(특성 길이가 등장하는가)?
   ⓒ "최적" 파지를 찾는 문제는 볼록인가?
2. **Rodriguez, Mason & Ferry, "From caging to grasping" (2012, IJRR)** — 역할:
   `표준(standard)`. <https://doi.org/10.1177/0278364912442972> (§1–2, §6)
   *왜 읽는가*: R3 의 출처. caging 을 **구성공간의 유계성**으로 정의하고 force closure 와
   잇는 유일한 1차 자료다. 불확실성 아래 파지 전략의 이론적 근거이기도 하다.
   추가 질문: ⓐ 저자들의 "grasping cage" 정의를 옮기고 이 레슨 R3 의 표와 대조하라.
   ⓑ 판정 알고리즘의 차원 한계는 무엇인가? ⓒ 마찰을 쓰지 않는 조건이 주는 보수성을
   저자들은 어떻게 다루는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄 또는 그림 한 장으로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지
않는가** (5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가,
분산·시드를 보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, 전체 5분 이내, 메모리 1GB 이내.
numpy + scipy(`optimize.linprog`, `spatial.ConvexHull`)만. 외부 데이터 불필요.

**입력 데이터(레슨이 지정).** 물체는 **단위 원판**이다. 접촉점은 경계 위의 각
$\theta_i$ 로 주고, 들어가는 법선은 $\hat n_i = -p_i$ (중심을 향한다). 마찰 원뿔은 평면이므로
모선이 둘이고, 각 접촉이 생성자 2개를 준다. 렌치는 (5)의 평면 형태를 쓴다.

**수용 기준 — 네 조건을 모두 만족해야 통과.**

1. **닫힌 형태 대조(R2 검증)** — 대심 두 접촉($\theta = 0, \pi$)에서 (3)으로 계산한 $Q$ 가
   (4)의 닫힌 형태와 상대오차 $10^{-12}$ 이내로 일치한다. 구체적으로

   | $\mu$ | 0.0 | 0.1 | 0.3 | 0.5 | 1.0 | 2.0 |
   |---|---|---|---|---|---|---|
   | $Q$ | 0 | 0.070184512 | 0.198762689 | 0.298142397 | 0.408248290 | 0.365148372 |

   그리고 $\mu^\ast = 2^{1/4}$ 에서 $Q = \sqrt2 - 1$ 을 상대오차 $10^{-9}$ 이내로 얻는다.
   **$Q(2.0) < Q(1.0)$ 인 비단조성을 보고서에 한 문단으로 쓴다.**
2. **무마찰 원판(R1 의 실패 모드·R4 검증)** — $\mu = 0$ 에서 $n \in \{2,3,4,6,12\}$ 등간격
   접촉 모두가 force closure **아님**으로 판정되고, $\mathrm{rank}\,W \le 2$ 이며 모든
   생성자의 토크 성분이 $10^{-15}$ 이내로 0 이다. 또한 **rank 검사를 끄면**
   $\epsilon^\ast = 1/(2n) > 0$ 이 나와 오판정되는 것을 보인다(P6).
3. **가능 영역 도표(블루프린트 과제)** — 접촉점을 $[0, 2\pi)$ 에서 독립 균등으로 뽑아
   ($n$ 개, 시드 $s\cdot97 + n$, $s = 0..1999$) force closure 비율을 재면

   | $\mu$ | $n=1$ | $n=2$ | $n=3$ | $n=4$ |
   |---|---|---|---|---|
   | 0.0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
   | 0.1 | 0.0000 | 0.0585 | 0.3325 | 0.5805 |
   | 0.2 | 0.0000 | 0.1245 | 0.4195 | 0.6520 |
   | 0.5 | 0.0000 | 0.2940 | 0.6245 | 0.8270 |
   | 1.0 | 0.0000 | 0.5030 | 0.8060 | 0.9405 |

   와 절대오차 0.02 이내로 일치한다. $n = 1$ 열이 **모든 $\mu$ 에서 정확히 0** 이어야 한다.
4. **해석해 대조(P4 검증)** — $n = 2$ 열이 닫힌 형태 $\frac{2}{\pi}\arctan\mu$ 와 일치한다.
   시행을 $2\times10^4$ 회로 늘리면 $\mu = 0.1/0.2/0.5/1.0$ 에서 측정값
   $0.0625/0.1250/0.2951/0.4991$ 이 예측 $0.063451/0.125666/0.295167/0.500000$ 과
   $|z| \le 1$ 안에서 일치한다($z = |\hat p - p|/\mathrm{SE}$, 측정 최대 $z = 0.55$).

**비교 대상.** ⓐ 닫힌 형태 (4)와 $\frac2\pi\arctan\mu$ — 조건 1·4. ⓑ 두 독립 판정:
LP 의 $\epsilon^\ast > 0$ 과 ConvexHull 의 $Q > 0$ 이 2000개 무작위 배치 전부에서 **같은
결론**을 주는지 확인한다(불일치 0건). ⓒ 자기 자신의 결함 버전: rank 검사 제거 — 조건 2.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 무마찰 원판이 force closure 로 나온다 | rank 검사를 빼고 LP 결과만 썼다 | 생성자 행렬의 특이값을 출력해 세 번째가 $10^{-15}$ 수준인지 본다 |
| $Q$ 가 닫힌 형태와 다르다 | 모선을 단위 벡터가 아니라 법선력 1 로 정규화했다(P5) | $\mu = 1$ 에서 $1/\sqrt6$ 이 나오는지 먼저 맞춘다 |
| 토크 부호가 뒤집힌다 | 평면 토크를 $p_y f_x - p_x f_y$ 로 썼다 | $p = (1,0)$, $f = (0,1)$ 에서 $\tau = +1$ 인지 본다 |
| $n = 2$ 비율이 닫힌 형태의 두 배다 | $\Delta\theta$ 를 $[0, 2\pi)$ 로 두고 꼭지각으로 접지 않았다 | $\Delta\theta$ 의 히스토그램이 $[0,\pi]$ 에서 균등인지 본다 |
| ConvexHull 이 예외를 던진다 | 생성자가 퇴화(무마찰)해 3차원 포가 만들어지지 않는다 | 예외를 $Q = 0$ 으로 처리하고 rank 를 따로 보고한다 |
| 비율이 실행마다 달라진다 | 시드를 루프 안에서 만들지 않았다 | 같은 명령을 두 번 돌려 표가 동일한지 본다 |

## 열린 문제

- **(열린 문제) 품질 지표의 정규화 불변성** — R2 의 실패 모드가 보여 주듯 $Q$ 는 힘 정규화와
  토크의 특성 길이에 의존하고, 그래서 **서로 다른 논문의 파지 품질 수치는 비교할 수 없다.**
  학습 기반 파지의 라벨이 이 지표로 만들어지므로 문제가 그대로 데이터로 들어간다
  (`s2-learned-grasping`). 현재 접근: 지표를 정의와 함께 보고하도록 요구하는 서베이
  ([Bicchi & Kumar 2000](https://doi.org/10.1109/ROBOT.2000.844081),
  [Prattichizzo & Trinkle 2016](https://doi.org/10.1007/978-3-319-32552-1_38)).
  비어 있는 자리: 단위·정규화에 불변인 파지 품질 척도.
- **(열린 문제) 불확실성 아래의 force closure** — (3)의 판정은 접촉점과 법선을 **정확히**
  안다고 가정한다. 지각 오차 $\pm\delta$ 아래에서 "확률 $1-\gamma$ 로 force closure"를
  판정하는 문제는 비볼록이고, 실무는 섭동 샘플링으로 근사한다(Dex-Net 의 robust 지표).
  현재 접근: caging 의 열린 조건을 쓰는
  [Rodriguez et al. 2012](https://doi.org/10.1177/0278364912442972), 2차 이동도(mobility)로
  접촉 섭동을 다루는 [Rimon & Burdick 1998](https://doi.org/10.1109/70.720346).
  비어 있는 자리: 지각 오차를 명시적으로 넣은 **인증 가능한** 파지 판정.
- **(열린 문제) 면 접촉·변형체의 렌치 집합** — (A1)을 버리면 (6)의 유한 생성이 깨지고
  증명 3단계의 닫힘성 논증을 다시 세워야 한다. soft finger 근사는 생성자를 늘리는 임시
  방편이고, 변형이 큰 경우(연성 그리퍼) 렌치 집합 자체가 구성에 따라 변한다. 현재 접근:
  접촉 영역을 다각형으로 근사하는 고전 모델, 미분가능 접촉 모델(`c2-contact-dynamics`).
  비어 있는 자리: 변형체 파지의 렌치 집합을 계산 가능한 볼록 근사로 주는 방법.

## 개념 점검

`rc quiz s2-grasp-mechanics` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: s2-grasp-mechanics-quiz
questions:
  - id: q1
    type: single
    prompt: "force closure 판정에서 LP 의 $\\epsilon^\\ast > 0$ 만으로 충분하지 않고 $\\mathrm{rank}\\,W = d'$ 를 따로 봐야 하는 이유는?"
    choices:
      - "LP 가 수치적으로 불안정하기 때문"
      - "모든 생성자가 한 부분공간에 놓이면 $\\epsilon^\\ast > 0$ 이면서도 렌치 공간을 생성하지 못하기 때문"
      - "마찰 원뿔이 비볼록이기 때문"
      - "$\\epsilon$ 의 단위가 렌치의 단위와 다르기 때문"
    answer: 1
    explanation: "$0 \\in \\mathrm{int\\,conv}(W)$ 는 '$\\lambda > 0$ 로 원점을 쓸 수 있다' **그리고** '생성자가 공간을 아핀 생성한다' 두 조건이다. LP 는 앞만 본다. 무마찰 단위 원판이 정확한 반례다 — 등간격 $n$ 접촉에서 $\\lambda_j = 1/(2n)$ 이 원점을 주지만 모든 토크가 0 이라 $\\mathrm{rank}\\,W = 2$ 이고 토크 외란을 저항하지 못한다."
    concept: { front: "force closure LP 판정의 두 조건", back: "$\\epsilon^\\ast > 0$ (원점을 양의 결합으로) + $\\mathrm{rank}\\,W = d'$ (공간을 생성) — LP 는 뒤를 보지 못한다" }
  - id: q2
    type: truefalse
    prompt: "무마찰이면 접촉점을 충분히 많이 늘려 단위 원판을 force closure 로 파지할 수 있다."
    answer: false
    explanation: "원판의 법선은 모두 중심을 지나므로 무마찰 힘 $f_i \\parallel p_i$ 이고 토크 $p_{i,x}f_{i,y} - p_{i,y}f_{i,x} = 0$ 이 **항등적으로** 0 이다. 생성자가 토크 축을 전혀 덮지 못해 $\\mathrm{rank}\\,W \\le 2$ 이고, 접촉점 수와 무관하게 force closure 가 아니다. 무마찰 하한(평면 4점·공간 7점)은 **일반 물체**에 대한 것이고 원판·구에는 적용되지 않는다."
    concept: { front: "무마찰 원판·구", back: "모든 법선이 중심을 지나 토크가 항등적으로 0 → 접촉점을 늘려도 force closure 불가" }
  - id: q3
    type: single
    prompt: "단위 원판의 대심 두 접촉에서 Ferrari–Canny 지표 $Q$ 를 최대화하는 마찰계수는?"
    choices:
      - "$\\mu = 1$ (원뿔 반각 $45^\\circ$)"
      - "$\\mu = 2^{1/4} \\approx 1.189$"
      - "$\\mu \\to \\infty$ — 마찰이 클수록 항상 좋다"
      - "$\\mu = 1/\\sqrt2$"
    answer: 1
    explanation: "$Q = \\sin\\alpha\\cos\\alpha/\\sqrt{1+\\cos^2\\alpha}$ 를 $u = \\cos^2\\alpha$ 로 바꾸면 $Q^2 = u(1-u)/(1+u)$ 이고 극점은 $u^2 + 2u - 1 = 0$, 즉 $u = \\sqrt2 - 1$ 이다. 그러면 $\\tan^2\\alpha = \\sqrt2$ 이므로 $\\mu^\\ast = 2^{1/4}$ 이고 $Q_{\\max} = \\sqrt2 - 1$. 마찰이 더 커지면 단위 모선이 접선 방향으로 누워 법선 성분을 잃어 $Q$ 가 **감소**한다."
    concept: { front: "$Q$ 의 비단조성", back: "$\\mu^\\ast = 2^{1/4}$, $Q_{\\max} = \\sqrt2-1$ — 단위 모선 정규화에서는 마찰이 커져도 좋아지지 않는다" }
  - id: q4
    type: multiple
    prompt: "caging 과 force closure 에 대해 옳은 것을 모두 고르라."
    choices:
      - "force closure 는 힘의 조건, caging 은 구성공간의 조건이다"
      - "둘 중 어느 것도 다른 것을 함의하지 않는다"
      - "마찰로 붙잡은 대심 두 점 파지는 cage 이기도 하다"
      - "caging 판정은 물체 구성공간의 위상 계산이라 고차원에서 실용적 알고리즘이 없다"
    answer: [0, 1, 3]
    explanation: "force closure 는 '임의의 외란을 즉시 막는다', caging 은 '자유 성분이 유계라 결국 잃지 않는다'다. 대심 두 점 파지는 force closure 지만 **cage 가 아니다** — 손가락을 벌리거나 접선 방향으로 밀면 물체가 빠져나간다. caging 판정은 `c6-cspace-complexity` 의 위상 계산 비용을 물려받아 평면 강체(3차원)까지가 실용 한계다."
    concept: { front: "caging 대 force closure", back: "구성공간의 유계성 대 렌치 공간의 생성. 서로 독립이고 caging 은 위치 오차에 열려 있다" }
  - id: q5
    type: single
    prompt: "공간(3차원) 접촉에서 마찰 원뿔을 $k$ 개 모선으로 이산화하면 판정은 어느 방향으로 틀리는가?"
    choices:
      - "보수적 — force closure 라고 판정하면 참이지만, 아니라고 판정한 것이 실제로는 force closure 일 수 있다"
      - "낙관적 — force closure 가 아닌 것을 force closure 라고 판정할 수 있다"
      - "틀리지 않는다 — $k \\ge 3$ 이면 정확하다"
      - "$k$ 가 짝수일 때만 보수적이다"
    answer: 0
    explanation: "$k$ 모선이 생성하는 원뿔은 참 원뿔의 **부분집합**이므로 $\\mathcal{W}_k \\subseteq \\mathcal{W}$ 다. 따라서 $\\mathcal{W}_k = \\mathbb{R}^6$ 이면 $\\mathcal{W} = \\mathbb{R}^6$ 이지만 역은 성립하지 않는다 — 거짓 음성만 생긴다. 평면에서는 모선이 정확히 둘이라 이산화 오차가 **없다**."
    concept: { front: "원뿔 이산화의 방향", back: "내부 근사 → 거짓 음성만. 평면은 모선이 둘이라 정확하다" }
  - id: q6
    type: short
    prompt: "단위 원판 위 두 접촉이 독립 균등일 때 force closure 확률을 $\\mu$ 로 쓰면?"
    answer: ["2 arctan(mu)/pi", "(2/pi) arctan mu", "2*atan(mu)/pi", "$\\frac{2}{\\pi}\\arctan\\mu$", "2arctan(mu)/pi", "2/pi * arctan(mu)"]
    explanation: "삼각형 $Op_1p_2$ 의 밑각이 $(\\pi - \\Delta\\theta)/2$ 이므로 현이 두 원뿔 안에 드는 조건은 $\\Delta\\theta \\ge \\pi - 2\\alpha$ 다. 꼭지각 $\\Delta\\theta$ 가 $[0,\\pi]$ 에서 균등하므로 확률은 $2\\alpha/\\pi = (2/\\pi)\\arctan\\mu$ 이고, $\\mu = 1$ 에서 정확히 $1/2$ 다."
    concept: { front: "원판 2접촉의 force closure 확률", back: "$(2/\\pi)\\arctan\\mu$ — $\\mu=1$ 에서 정확히 1/2" }
```

## 이 단계 공부법

1. **힘과 운동을 먼저 분리한다 (20분)** — "force closure = 렌치 공간을 생성한다"와
   "caging = 구성공간의 자유 성분이 유계다"를 한 장에 쓰고 R3 의 2×2 표를 직접 채운다.
   이 표를 채울 수 있으면 이 레슨의 절반이 끝난다.
2. **동치 네 개를 한 줄씩 외운다 (60분)** — R1 의 (ⓐ)–(ⓓ)와 그 사이 화살표의 근거
   (정의 전개 / 분리 초평면 / 원뿔의 닫힘성)를 백지에서 다시 쓴다. 3단계의 **닫힘성**이
   어디서 쓰이는지 짚는 것이 핵심이다 — 면 접촉에서 깨지는 자리가 거기다.
3. **닫힌 형태를 손으로 얻는다 (50분)** — P2·P3 를 푼다. 네 생성자 (9)의 부호를 직접 맞추고
   사면체의 면까지 거리를 계산해 (4)를 얻는다. 그 다음 비단조성과 $\mu^\ast = 2^{1/4}$ 를
   미분으로 확인한다. **지표를 손으로 미분해 보기 전에는 "마찰이 클수록 좋다"는 직관을
   버리지 못한다.**
4. **정규화의 함정을 만난다 (30분)** — P5 를 푼다. 같은 파지가 정규화에 따라 다른 순위를
   받는 것을 계산으로 확인하고, 그것이 학습 데이터의 라벨 문제로 이어진다는 것을 적어 둔다
   (`s2-learned-grasping` 에서 다시 본다).
5. **구현하고 결함 버전도 돌린다 (80분)** — 재현 과제. 조건 1(닫힌 형태)을 먼저 맞추고,
   조건 2 에서 **rank 검사를 일부러 빼** 무마찰 원판이 오판정되는 것을 본다. 조건 3 의 표를
   그려 "접촉점 수와 마찰이 가능 영역을 어떻게 넓히는가"를 눈으로 확인한다.
6. **논문 2편 (120분)** — 1992 → 2012 순서로 읽는다. 1992 는 지표를, 2012 는 그 지표가
   요구하는 정확성을 **우회하는** 방법을 준다. 두 논문을 "정확한 힘 조건 대 열린 위상 조건"의
   대조로 노트에 정리한다.
7. **문제 세트 (150분)** — P3·P4·P7 먼저, P1·P2 다음, P5·P6·P8 은 남는 시간에.
   P5(정규화)가 실무에서 가장 자주 문제가 되는 항목이다.

**통과 기준**: R1 의 네 동치를 백지에서 증명할 수 있고, (4)를 손으로 유도해
$\mu^\ast = 2^{1/4}$, $Q_{\max} = \sqrt2-1$ 을 얻을 수 있고, 재현 과제의 네 조건을 만족하는
코드를 갖고 있고, caging 과 force closure 의 2×2 표를 예와 함께 채울 수 있다.
논문 2편의 노트가 있다.
