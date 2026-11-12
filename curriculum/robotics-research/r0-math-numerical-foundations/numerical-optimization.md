---
id: r0-numerical-optimization
title: 수치 최적화 — Newton·준뉴턴·SQP
summary: >-
  Newton 법의 2차 수렴을 증명하고, BFGS 의 secant 조건을 유도하며, 선탐색·신뢰영역이 전역 수렴을
  어떻게 보장하는지 본다. 제약 문제의 SQP·내부점 구조까지 연결한다.
objectives:
  - Newton 법의 국소 2차 수렴을 조건과 함께 증명할 수 있다.
  - BFGS 업데이트를 secant 조건과 최소 변화 원리에서 유도할 수 있다.
  - 선탐색(Armijo·Wolfe)과 신뢰영역이 전역 수렴을 주는 구조를 설명할 수 있다.
  - Gauss-Newton 과 Levenberg-Marquardt 의 관계를 신뢰영역 관점에서 쓸 수 있다.
  - SQP 와 내부점법이 KKT 조건을 어떻게 수치적으로 푸는지 말할 수 있다.
prerequisites: [r0-convex-optimization]
difficulty: 4
estimated_minutes: 480
tags: [optimization, newton, quasi-newton, sqp, research]
activities:
  - id: r0-numerical-optimization-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: r0-numerical-optimization-textbook
    kind: reading
    title: 교재 읽기 (Nocedal-Wright ch.3,6,18,19) + 1페이지 노트
    estimated_minutes: 120
  - id: r0-numerical-optimization-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 150
  - id: r0-numerical-optimization-reproduction
    kind: reproduction
    title: 재현 과제 — 수렴 차수를 로그 도표로 분리 (R2)
    estimated_minutes: 105
  - id: r0-numerical-optimization-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Nocedal & Wright, Numerical Optimization (2nd ed.)"
    kind: book
    note: ch.3 (선탐색), 6 (준뉴턴), 10 (최소제곱), 18 (SQP), 19 (내부점). 1순위. (공식 URL 미확인)
  - title: "Boyd & Vandenberghe, Convex Optimization"
    url: https://web.stanford.edu/~boyd/cvxbook/
    kind: book
    note: ch.9-11 (무제약·등식제약·내부점). 볼록 관점의 같은 알고리즘.
  - title: "SciPy optimize 문서"
    url: https://docs.scipy.org/doc/scipy/reference/optimize.html
    kind: notes
    note: minimize(BFGS, trust-constr, SLSQP), least_squares(trf, lm). 재현 과제의 비교 대상.
---

# 수치 최적화 — Newton·준뉴턴·SQP

## 전제와 기호

| 기호 | 뜻 |
|---|---|
| $f: \mathbb{R}^n \to \mathbb{R}$ | 목적함수, $C^2$ |
| $g_k = \nabla f(x_k)$, $H_k = \nabla^2 f(x_k)$ | 기울기와 Hessian |
| $p_k$ | 탐색 방향, $\alpha_k$ 스텝 길이 |
| $B_k$ | Hessian 근사(준뉴턴), $B_k \approx H_k$ |
| $s_k = x_{k+1}-x_k$, $y_k = g_{k+1}-g_k$ | 스텝과 기울기 변화 |
| $\Delta_k$ | 신뢰영역 반지름 |

전제: `r0-convex-optimization`(KKT, 쌍대성)과 `r0-linear-algebra-decompositions`(조건수).

## 핵심 결과

- **R1 (Newton 법의 2차 수렴) [D3]** — $x^\star$ 가 $\nabla f(x^\star)=0$, $H(x^\star) \succ 0$,
  $H$ 가 Lipschitz($L$)인 국소 최소면, $x_0$ 가 충분히 가까울 때

$$
\lVert x_{k+1}-x^\star\rVert \le \frac{L}{2\sigma_{\min}(H^\star)}\lVert x_k-x^\star\rVert^2 . \tag{1}
$$

- **R2 (BFGS 와 secant 조건) [D2]** — 준뉴턴 근사는 **secant 조건** $B_{k+1}s_k = y_k$ 를
  만족해야 하고, 그 중 **대칭 양정이면서 이전 근사에서 가장 적게 변하는** 업데이트가 BFGS 다:

$$
B_{k+1} = B_k - \frac{B_ks_ks_k^\top B_k}{s_k^\top B_k s_k} + \frac{y_ky_k^\top}{y_k^\top s_k}. \tag{2}
$$

  $y_k^\top s_k > 0$ (곡률 조건)이면 양정이 보존된다.
- **R3 (선탐색의 전역 수렴) [D1]** — Armijo(충분 감소)와 곡률 조건(Wolfe)을 만족하는 스텝을
  고르고 방향이 기울기와 각도 조건을 만족하면 $\lVert g_k\rVert \to 0$ 이다(Zoutendijk 정리).
  증명은 인용한다 **[D0]**(Nocedal–Wright 정리 3.2).
- **R4 (LM = 신뢰영역 Gauss–Newton) [D2]** — 최소제곱에서 Gauss–Newton 방향은
  $(J^\top J)p = -J^\top r$ 이고, Levenberg–Marquardt 의 $(J^\top J+\lambda I)p = -J^\top r$ 는
  **신뢰영역 반지름 $\Delta$ 에 대응하는 $\lambda$** 로 제약된 부문제의 해다. 즉 감쇠는 임의의
  정칙화가 아니라 **스텝 길이 제어**다.
- **R5 (SQP·내부점은 KKT 를 푼다) [D1]** — SQP 는 각 반복에서 KKT 조건을 선형화해 QP 부문제를
  풀고, 내부점법은 상보 여유를 $\lambda_i f_i = -\mu$ 로 완화해 $\mu \to 0$ 으로 보낸다.
  **둘 다 R4(KKT)를 수치적으로 추적하는 방법**이다.

## 유도

### R1 — 2차 수렴 (증명 스케치는 §증명 스케치)

Newton 스텝은 $p_k = -H_k^{-1}g_k$ 다. 이것이 어디서 오는지: $f$ 를 2차까지 전개하면

$$
f(x_k+p) \approx f(x_k) + g_k^\top p + \tfrac12 p^\top H_k p ,
$$

우변을 $p$ 로 미분해 0 으로 두면 $H_kp = -g_k$ 다. 즉 **Newton 법은 2차 모형의 최소점으로 가는 것**이고,
모형이 정확한 만큼 수렴이 빠르다. 2차 수렴 (1)은 Taylor 잔차가 $O(\lVert x_k-x^\star\rVert^2)$
이라는 사실에서 나온다.

**가정이 깨지는 곳**: $H_k \succ 0$ 이 아니면 $p_k$ 가 하강 방향이 아닐 수 있다(안장점 근방).
그래서 실무는 ⓐ $H_k$ 를 수정(modified Cholesky) ⓑ 신뢰영역 사용 ⓒ $H$ 대신 $J^\top J$
(Gauss–Newton, 항상 양반정) 중 하나를 쓴다. 또 $H_k$ 를 만들고 분해하는 비용이 $O(n^3)$ 이라
대규모에서는 준뉴턴이나 CG 를 쓴다.

### R2 — secant 조건과 BFGS

$B_{k+1}$ 은 **이미 본 정보와 일관**해야 한다. 기울기의 평균값 정리에서

$$
y_k = g_{k+1}-g_k = \left(\int_0^1 H(x_k+ts_k)\,dt\right)s_k \approx H_{k+1}s_k ,
$$

따라서 근사도 $B_{k+1}s_k = y_k$ 를 만족해야 한다 — 이것이 secant 조건이다. 미지수가
$n(n+1)/2$ 개인데 조건은 $n$ 개뿐이므로 **해가 무수히 많다**. BFGS 는 그중

$$
B_{k+1} = \arg\min_B \lVert B - B_k\rVert_W \quad \text{s.t. } B = B^\top,\ Bs_k = y_k
$$

(가중 Frobenius 노름)을 택한 것이고, 계산하면 (2)가 나온다(생략: 가중 노름의 선택과 대수 —
Nocedal–Wright §6.1).

**곡률 조건의 뜻**: $y_k^\top s_k > 0$ 은 "스텝 방향으로 기울기가 증가했다", 즉 **그 방향의 곡률이
양수**라는 것이다. 이것이 깨지면(비볼록 영역) 양정성이 유지되지 않아 업데이트를 건너뛰거나
감쇠해야 한다. Wolfe 곡률 조건을 만족하는 선탐색이 이 조건을 **자동으로** 보장한다 — 두 요소가
짝을 이루는 이유다.

### R4 — LM 이 신뢰영역인 이유

신뢰영역 부문제는 $\min_p \tfrac12\lVert r + Jp\rVert^2$ s.t. $\lVert p\rVert \le \Delta$ 다.
라그랑주 조건(R0 의 KKT)을 쓰면

$$
(J^\top J + \lambda I)p = -J^\top r, \qquad \lambda \ge 0,\quad \lambda(\lVert p\rVert-\Delta) = 0 ,
$$

즉 **LM 의 $\lambda$ 는 신뢰영역 제약의 쌍대 변수**다. 상보 여유에서: 제약이 비활성($\lVert p\rVert<\Delta$)이면
$\lambda=0$ 이고 순수 Gauss–Newton 이, 활성이면 $\lambda>0$ 이고 스텝이 짧아진다.

**실무적 함의**: "$\lambda$ 를 키워야 돌아간다"는 말은 **두 가지 중 하나**다 — ⓐ 2차 모형이
나쁜 영역에 있다(정상, 신뢰영역이 작아야 한다) ⓑ $J^\top J$ 가 구조적으로 특이하다(과매개화나
게이지 결핍 — `c1-manifold-optimization` R4·R5). 둘을 구분하지 않으면 영원히 감쇠를 올린다.

## 증명 스케치

### R1 — Newton 법의 국소 2차 수렴

**가설** H1: $f \in C^2$, $H$ 가 $x^\star$ 근방에서 Lipschitz 상수 $L$. H2: $H^\star \succ 0$.
H3: $x_k$ 가 충분히 가깝다. **결론** C: (1).

**전략**: Newton 스텝의 오차를 Taylor 잔차로 바꾸고, $H^{-1}$ 의 노름으로 묶는다.

1. $e_k := x_k - x^\star$ 로 두면
   $e_{k+1} = e_k - H_k^{-1}g_k = H_k^{-1}\big(H_ke_k - g_k\big)$.
2. $g_k = g_k - g^\star = \int_0^1 H(x^\star+te_k)e_k\,dt$ (평균값 정리, $g^\star=0$).
3. 1·2 를 합치면
   $e_{k+1} = H_k^{-1}\int_0^1\big(H_k - H(x^\star+te_k)\big)e_k\,dt$.
4. Lipschitz 조건에서 $\lVert H_k - H(x^\star+te_k)\rVert \le L(1-t)\lVert e_k\rVert$ 이므로
   적분이 $\tfrac{L}{2}\lVert e_k\rVert^2$ 로 묶인다.
5. $x_k$ 가 가까우면 연속성에서 $\lVert H_k^{-1}\rVert \le 1/\sigma_{\min}(H^\star)$ 수준이므로 (1). C.

**가설을 지우면**: H2 를 빼면 4단계 뒤의 $\lVert H_k^{-1}\rVert$ 가 폭발해 수렴이 보장되지 않는다
— 안장점 근방에서 Newton 이 **발산하거나 안장점으로 수렴**하는 이유다. H3 를 빼면 전역 수렴이
없다: Newton 은 국소 방법이고, 전역성은 선탐색·신뢰영역이 준다(R3).

**Gauss–Newton 과의 비교**: 최소제곱에서 $H = J^\top J + \sum_i r_i\nabla^2 r_i$ 이고 Gauss–Newton 은
둘째 항을 버린다. 잔차가 0 에 가까우면 그 항이 작아 **2차 수렴에 근접**하고, 잔차가 크면 선형
수렴으로 떨어진다 — `c1-manifold-optimization` R3 의 (3)과 같은 구조다.

## 문제 세트

★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R2)** secant 조건을 평균값 정리에서 유도하고, $n=2$ 에서 조건을 만족하는
대칭 $B$ 의 자유도가 몇인지 세어라.
*해답 스케치*: 대칭 $2\times2$ 는 자유도 3, secant 조건은 식 2개 → 자유도 1 이 남는다. 그 1 을
"가장 적게 변하는" 기준으로 고르는 것이 BFGS 다.

**P2 (유도, ★★, R4)** 신뢰영역 부문제의 KKT 조건에서 LM 방정식을 유도하고, $\lambda$ 가
$\Delta$ 의 단조 감소 함수임을 보여라.
*해답 스케치*: $\lambda$ 가 커지면 $\lVert p(\lambda)\rVert$ 가 줄어든다($(J^\top J+\lambda I)^{-1}$
의 고윳값이 줄어들므로). 따라서 $\Delta$ 를 주면 대응하는 $\lambda$ 가 유일하다.

**P3 (증명, ★★★, R1)** R1 의 증명을 빈틈 없이 쓰고, 5단계의 "충분히 가까우면"을 정량화하라
(어떤 반지름 안에서 성립하는가).
*해답 스케치*: $\lVert H_k^{-1}\rVert \le 2/\sigma_{\min}(H^\star)$ 가 성립하는 반지름을
Lipschitz 조건으로 구하고, 그 안에서 (1)의 계수가 1 보다 작아지는 조건을 쓴다.

**P4 (계산, ★, R1)** $f(x)=x^4$ 에 Newton 법을 $x_0=1$ 에서 적용할 때 $x_1, x_2, x_3$ 을 구하고
수렴 차수를 판정하라.
*정답*: $x_{k+1} = x_k - \frac{4x_k^3}{12x_k^2} = \tfrac23 x_k$ 이므로 $x_1 = 0.666\ldots$,
$x_2 = 0.444\ldots$, $x_3 = 0.296\ldots$ — **선형 수렴**이다(비율 2/3). 허용오차 $10^{-9}$.
**왜 2차가 아닌가**: $x^\star=0$ 에서 $H^\star = 12x^{\star2} = 0$ 이라 H2 가 깨진다.

**P5 (구현, ★★, R1·R2·R3)** Rosenbrock 함수에 ⓐ 경사하강 ⓑ BFGS ⓒ Newton 을 구현해
반복 수와 수렴 차수를 비교하라. 선탐색은 Armijo 로 통일한다.
*루브릭*: ⓐ 세 방법이 같은 수렴 판정과 같은 선탐색을 쓴다 ⓑ $\log\lVert e_{k+1}\rVert$ 대
$\log\lVert e_k\rVert$ 기울기로 수렴 차수를 **추정해서** 보고한다(1, ~1.6, 2 근방) ⓒ Newton 이
$H$ 가 부정인 영역에서 실패하는 것을 보이고 수정 방법을 적용한다.

**P6 (반례, ★★, R1·R4)** Newton 법이 ⓐ 안장점으로 수렴하는 예와 ⓑ 발산하는 예를 각각 만들어라.
그리고 LM 감쇠가 ⓐ 를 고치지만 **게이지 결핍은 고치지 못하는** 것을 보여라.
*성질 체크리스트*: ⓐ 는 $f(x,y)=x^2-y^2$ 에서 임의 초기값, ⓑ 는 $f(x)=\sqrt{1+x^2}$ 류에서 먼
초기값. 게이지 결핍은 $J^\top J$ 의 영공간이 **구조적**이라 $\lambda$ 를 키워도 그 방향의 해가
임의로 남는다.

## 논문 읽기

**교재 예외 적용**(레슨 표준 §5). 아래를 읽고 1페이지 노트 2편을 쓴다(고정 질문 1·3·4·8).

1. **Nocedal & Wright, ch.3 와 ch.6** — 선탐색과 준뉴턴. 질문: ⓐ Wolfe 조건의 두 부분이 각각
   무엇을 막는지 쓰라(너무 긴 스텝? 너무 짧은 스텝?). ⓑ 저자들이 BFGS 를 "가장 적게 변하는
   업데이트"로 특징짓는 방식과, 그 가중 노름 선택의 근거는?
2. **Nocedal & Wright, ch.18 또는 19** — SQP 또는 내부점. 질문: ⓐ 선택한 방법이 KKT 조건을
   어떻게 수치적으로 추적하는지 한 문단으로 쓰라. ⓑ 실현가능성을 유지하는 방식(내부점은 내부를
   유지, SQP 는 아니다)이 로보틱스의 안전 제약에서 무엇을 뜻하는가?

**보조 문헌 1편**(방법론): Boyd & Vandenberghe ch.9–11 — 같은 알고리즘을 볼록 관점에서.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 예산: 노트북 CPU 2분 이내, numpy 만. 네 조건을 모두 만족해야 한다.

1. **수렴 차수 분리**: Rosenbrock 에서 경사하강·BFGS·Newton 의 오차열 $\lVert e_k\rVert$ 를
   기록하고, $\log\lVert e_{k+1}\rVert$ 대 $\log\lVert e_k\rVert$ 의 기울기로 수렴 차수를 추정한다.
   **경사하강 ≈ 1, BFGS ≈ 1.2–1.8(초선형), Newton ≈ 2** 가 나와야 한다(각 ±0.3).
2. **secant 조건 보존**: BFGS 구현이 매 반복 $\lVert B_{k+1}s_k - y_k\rVert < 10^{-10}$ 를
   만족하고, 곡률 조건 $y_k^\top s_k > 0$ 이 깨지는 반복에서 업데이트를 건너뛰는지 확인한다.
3. **LM = 신뢰영역**: 최소제곱 문제에서 ⓐ $\lambda$ 를 직접 바꿔 가며 $\lVert p(\lambda)\rVert$ 가
   단조 감소하는 것을 확인하고 ⓑ 주어진 $\Delta$ 에 대응하는 $\lambda$ 를 이분법으로 찾아
   $\lVert p\rVert = \Delta$ 를 $10^{-8}$ 이내로 맞춘다.
4. **H2 가 깨질 때**: $f(x)=x^4$ (P4)에서 Newton 이 **선형 수렴**하는 것을 수치로 확인하고,
   추정한 수렴 차수가 1 근방임을 보인다(2차 수렴 가정이 $H^\star \succ 0$ 에 의존함을 확인).

**비교 대상**: `scipy.optimize.minimize` 의 `BFGS`·`trust-ncg` 와 반복 수를 비교하고,
`least_squares(method='lm')` 와 LM 해가 $10^{-8}$ 이내로 일치.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| Newton 의 수렴 차수가 2 가 아니다 | $H^\star$ 가 특이하거나(P4 류) 선탐색이 스텝을 자르고 있다 | $H$ 의 최소 고윳값과 $\alpha_k$ 를 출력 |
| BFGS 가 발산한다 | 곡률 조건 위반 시 업데이트를 건너뛰지 않았다 | $y_k^\top s_k$ 를 매 반복 출력 |
| LM 이 신뢰영역과 안 맞는다 | $\lambda$ 와 $\Delta$ 의 대응을 상보 여유 없이 임의로 썼다 | 조건 3ⓑ 의 이분법으로 짝을 맞춘다 |
| 수렴 차수 추정이 불안정하다 | 기계 정밀도 근방의 오차를 회귀에 포함했다 | $\lVert e_k\rVert > 10^{-12}$ 구간만 회귀 |

## 열린 문제

- **(열린 문제) 비볼록 대규모 문제에서의 2차 정보** — Newton 급 수렴은 매력적이지만 $H$ 를
  만들고 분해하는 비용이 로보틱스 규모에서 금지적이다. 희소성·저랭크 구조를 활용한 **싼 2차
  정보**(Hessian-free, L-BFGS 변형)의 수렴 보장이 부분적으로만 알려졌다.
- **(열린 문제) 비매끄러운 목적함수의 준뉴턴** — 강건 비용(Huber, truncated)과 접촉이 들어오면
  곡률 조건과 secant 조건의 근거가 약해진다. 로보틱스가 쓰는 IRLS·감쇠 조정은 대부분 경험적이다
  (`c1-manifold-optimization` 의 열린 문제와 같은 항목).
- **(열린 문제) 실시간 제약 아래의 종료 기준** — MPC 는 수렴하지 않은 반복에서 해를 써야 한다.
  **조기 종료한 해의 보장**(준최적성, 안정성)을 정량화하는 방법이 제한적이다(C4 의 RTI 와 연결).

## 개념 점검

`rc quiz r0-numerical-optimization` 로 푼다. 개념 점검 전용이다.

```quiz
activity: r0-numerical-optimization-quiz
questions:
  - id: q1
    type: single
    prompt: "Newton 법의 국소 2차 수렴에 필요한 가정이 **아닌** 것은?"
    choices:
      - "$H$ 가 해 근방에서 Lipschitz"
      - "$H(x^\\star) \\succ 0$ (양정)"
      - "$f$ 가 볼록"
      - "초기값이 해에 충분히 가깝다"
    answer: 2
    explanation: "볼록성은 필요하지 않다 — 국소 최소 근방에서 Hessian 이 양정이고 Lipschitz 이면 충분하다. 반대로 $H^\\star \\succ 0$ 이 깨지면($f=x^4$) 2차 수렴이 선형으로 떨어진다."
    concept: { front: "Newton 2차 수렴의 가정", back: "$H$ Lipschitz + $H^\\star \\succ 0$ + 충분히 가까운 초기값. 볼록성은 불필요" }
  - id: q2
    type: short
    prompt: "준뉴턴 근사가 만족해야 하는 조건의 이름은? ($B_{k+1}s_k = y_k$)"
    answer: ["secant 조건", "secant", "시컨트 조건", "secant condition", "준뉴턴 조건"]
    explanation: "secant 조건이다. 기울기의 평균값 정리에서 $y_k \\approx H_{k+1}s_k$ 이므로 근사도 같은 관계를 만족해야 한다. 조건이 $n$ 개뿐이어서 해가 무수히 많고, BFGS 는 '가장 적게 변하는' 것을 고른다."
    concept: { front: "secant 조건", back: "$B_{k+1}s_k = y_k$ — 기울기 변화와 일관된 Hessian 근사. 해가 무수히 많다" }
  - id: q3
    type: single
    prompt: "Levenberg-Marquardt 의 감쇠 $\\lambda$ 의 정확한 해석은?"
    choices:
      - "임의로 고르는 정칙화 상수"
      - "신뢰영역 제약 $\\lVert p\\rVert \\le \\Delta$ 의 쌍대 변수"
      - "학습률"
      - "조건수의 역수"
    answer: 1
    explanation: "신뢰영역 부문제의 KKT 조건에서 $(J^\\top J+\\lambda I)p=-J^\\top r$ 과 $\\lambda(\\lVert p\\rVert-\\Delta)=0$ 이 나온다. 즉 $\\lambda$ 는 쌍대 변수이고 감쇠는 **스텝 길이 제어**다 — 임의의 정칙화가 아니다."
    concept: { front: "LM 감쇠의 의미", back: "신뢰영역 제약의 쌍대 변수. 감쇠 = 스텝 길이 제어이고, 비활성이면 순수 Gauss-Newton" }
  - id: q4
    type: truefalse
    prompt: "감쇠를 충분히 키우면 게이지 결핍(구조적 영공간)으로 인한 해의 비유일성도 해결된다."
    answer: false
    explanation: "감쇠는 그 방향에 곡률을 **인공적으로** 넣어 수치적으로 풀리게 할 뿐, 데이터가 그 방향을 결정하지 못하는 사실은 바뀌지 않는다. 해는 감쇠 크기에 따라 달라진다. 게이지는 prior 나 기준 고정으로 없애야 한다."
    concept: { front: "감쇠로 고칠 수 없는 것", back: "구조적 영공간(게이지). 감쇠는 수치적으로만 풀리게 하고 해는 감쇠에 의존한다 — prior/고정이 필요" }
```

## 이 단계 공부법

1. **Newton 을 "2차 모형의 최소점"으로 본다 (30분)** — 공식을 외우지 말고 2차 전개를 미분해
   유도한다. 이 관점이 Gauss–Newton·LM·SQP 전부로 이어진다.
2. **수렴 차수를 도표로 분리한다 (90분)** — 재현 과제 조건 1 을 먼저 한다. 기울기 1, 1.6, 2 가
   눈으로 갈라지는 것을 보면 이론이 설명으로 읽힌다.
3. **H2 가 깨지는 예를 직접 본다 (40분)** — P4 와 재현 과제 조건 4. "가정이 깨지면 무엇이
   깨지는가"를 수치로 확인하는 것이 연구 트랙 전체의 작업 방식이다.
4. **LM 을 KKT 로 다시 쓴다 (60분)** — R0 의 앞 레슨(KKT)이 여기서 바로 쓰인다. 감쇠를 "임의의
   정칙화"로 알고 있었다면 이 60분이 이 레슨의 가장 큰 수확이다.
5. **두 종류의 "감쇠가 필요한 상황"을 구분한다 (50분)** — P6 을 푼다. ⓐ 2차 모형이 나쁜 영역
   (정상) ⓑ 구조적 영공간(게이지·과매개화). 구분하지 못하면 `c1-manifold-optimization` 과
   `c5-sparsity-isam` 에서 같은 함정에 빠진다.
6. **교재는 알고리즘 설계 논리로 읽는다 (120분)** — Nocedal & Wright 는 "왜 이 조건을 요구하는가"
   를 설명하는 책이다. Wolfe 조건의 두 부분이 각각 무엇을 막는지 쓸 수 있으면 제대로 읽은 것이다.

**통과 기준**: R1 을 백지에서 증명할 수 있고, secant 조건을 유도할 수 있고, LM 을 신뢰영역 KKT 로
설명할 수 있고, 재현 과제 네 조건을 만족하는 코드와 교재 노트 2편이 있다.
