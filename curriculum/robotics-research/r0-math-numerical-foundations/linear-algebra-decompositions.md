---
id: r0-linear-algebra-decompositions
title: 분해와 조건수
summary: >-
  최소제곱을 정규방정식·QR·SVD 세 방법으로 풀고, 정규방정식이 조건수를 제곱한다는 사실을 유도해
  수치로 확인한다. 유사역행렬과 영공간, 랭크 결핍의 진단까지 다룬다.
objectives:
  - 최소제곱의 정규방정식을 유도하고 조건수가 제곱되는 것을 증명할 수 있다.
  - QR 과 SVD 로 최소제곱을 풀고 세 방법의 수치 안정성을 비교할 수 있다.
  - 유사역행렬을 SVD 로 정의하고 랭크 결핍에서의 최소 노름 해를 설명할 수 있다.
  - 수치 랭크를 특이값으로 판정하고 임계값 선택의 근거를 댈 수 있다.
  - 조건수가 해의 상대오차 상한에 어떻게 들어가는지 유도할 수 있다.
prerequisites: []
difficulty: 3
estimated_minutes: 420
tags: [numerical-linear-algebra, conditioning, least-squares, research]
activities:
  - id: r0-linear-algebra-decompositions-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 80
  - id: r0-linear-algebra-decompositions-textbook
    kind: reading
    title: 교재 읽기 (Trefethen-Bau, Boyd 부록, Nocedal-Wright) + 1페이지 노트
    estimated_minutes: 100
  - id: r0-linear-algebra-decompositions-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 130
  - id: r0-linear-algebra-decompositions-reproduction
    kind: reproduction
    title: 재현 과제 — 세 해법의 오차를 조건수에 대해 도표화 (R1)
    estimated_minutes: 95
  - id: r0-linear-algebra-decompositions-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Trefethen & Bau, Numerical Linear Algebra"
    kind: book
    note: Lectures 11-20 (QR, 최소제곱, 조건수, 안정성). 이 레슨의 1순위 교재. (공식 URL 미확인)
  - title: "Boyd & Vandenberghe, Convex Optimization"
    url: https://web.stanford.edu/~boyd/cvxbook/
    kind: book
    note: 부록 A (선형대수 배경)와 C. 무료 PDF 공개.
  - title: "Nocedal & Wright, Numerical Optimization (2nd ed.)"
    kind: book
    note: ch.10 (최소제곱 문제). 정규방정식·QR·SVD 의 비교가 이 장에 있다. (공식 URL 미확인)
  - title: "NumPy linalg 문서"
    url: https://numpy.org/doc/stable/reference/routines.linalg.html
    kind: notes
    note: lstsq, qr, svd, cond, matrix_rank. 재현 과제의 도구.
---

# 분해와 조건수

## 전제와 기호

| 기호 | 뜻 |
|---|---|
| $A \in \mathbb{R}^{m\times n}$, $m \ge n$ | 과결정 계의 계수행렬 |
| $\sigma_1 \ge \cdots \ge \sigma_n \ge 0$ | $A$ 의 특이값 |
| $\kappa_2(A) = \sigma_1/\sigma_n$ | 2-노름 조건수(랭크 완전일 때) |
| $A^+ = V\Sigma^+U^\top$ | 유사역행렬(Moore–Penrose) |
| $\epsilon \approx 2.2\times10^{-16}$ | 배정밀도 기계 정밀도 |
| $\hat{x}$ | 유한 정밀도에서 계산된 해 |

전제: `f0-linear-algebra`(소거·부분공간·고윳값·SVD)와 `f0-python-numerics-git`(부동소수점,
유한차분). 이 모듈은 **진단으로 건너뛸 수 있는 선택 모듈**이고 선수는 권장이다.

## 시작 전 자가 진단

이 모듈의 첫 레슨이므로 준비 상태를 점검한다. 아래를 전부 풀 수 있으면 R0 를 건너뛰고 C1 로
바로 가도 된다. **두 문항 이상 막히면** 괄호 안의 선수 레슨으로 돌아가는 편이 빠르다.

1. $A$ 의 특이값이 $(4, 2, 0.5)$ 일 때 $\kappa_2(A)$ 와 $\kappa_2(A^\top A)$ 는?
   (`f0-linear-algebra`)
   **정답**: $\kappa_2(A) = 4/0.5 = 8$, $\kappa_2(A^\top A) = 8^2 = 64$. $A^\top A$ 의 특이값이
   $A$ 의 특이값의 제곱이기 때문이다.
2. 배정밀도에서 상대오차 $10^{-18}$ 을 요구하는 수용 기준이 왜 무의미한가? (`f0-python-numerics-git`)
   **정답**: 기계 정밀도가 $\approx 2.2\times10^{-16}$ 이므로 그보다 작은 상대오차는 표현 자체가
   불가능하다. 절대오차 기준이라면 값의 크기에 따라 가능할 수 있다.
3. $\min_x \lVert Ax-b\rVert^2$ 의 정규방정식을 유도하라. (`f0-linear-algebra`)
   **정답**: $\nabla_x = 2A^\top(Ax-b) = 0 \Rightarrow A^\top Ax = A^\top b$.
4. $f(x)=x^\top Mx$ ($M$ 대칭)의 기울기와 Hessian 은? (`f0-calculus-multivariable`)
   **정답**: $\nabla f = 2Mx$, $\nabla^2 f = 2M$.
5. numpy 에서 `np.linalg.lstsq` 와 `np.linalg.solve(A.T@A, A.T@b)` 중 어느 쪽이 수치적으로
   안전하고 왜인가? (`f0-python-numerics-git`)
   **정답**: `lstsq`. QR/SVD 기반이라 조건수를 제곱하지 않는다. 이 레슨의 R1 이 그 이유를 유도한다.

## 핵심 결과

- **R1 (정규방정식은 조건수를 제곱한다) [D2]** — 랭크 완전 $A$ 에 대해

$$
\kappa_2(A^\top A) = \kappa_2(A)^2 . \tag{1}
$$

  따라서 정규방정식을 세워서 푸는 것은 **유효숫자를 절반 잃는** 것과 같다.
- **R2 (최소제곱 오차 한계) [D3]** — $b$ 에 섭동 $\delta b$ 가 있을 때 해의 상대오차는

$$
\frac{\lVert \delta x\rVert}{\lVert x\rVert} \le \kappa_2(A)\,\frac{\lVert \delta b\rVert}{\lVert b_{\mathcal{R}}\rVert}, \tag{2}
$$

  여기서 $b_{\mathcal{R}}$ 는 $b$ 의 열공간 성분이다. 즉 **조건수가 오차 증폭 계수**다.
- **R3 (QR 과 SVD) [D2]** — $A = QR$ 이면 최소제곱 해는 $Rx = Q^\top b$ 를 후진대입으로 푼 것이고,
  이 과정의 조건수는 $\kappa_2(A)$ 다(제곱되지 않는다). SVD 해는 $x = A^+b$ 이며 랭크 결핍에서도
  정의된다.
- **R4 (유사역행렬과 최소 노름 해) [D3]** — 랭크 $r < n$ 일 때 최소제곱 해는 유일하지 않고
  해집합은 $x_0 + \mathcal{N}(A)$ 다. 그중 **노름이 최소인 해가 유일**하게 존재하고 $x = A^+b$ 다.
- **R5 (수치 랭크) [D2]** — 수치 랭크는 $\sigma_i > \tau$ 인 특이값의 개수로 정의하고, 기본
  임계값은 $\tau = \sigma_1 \cdot \max(m,n)\cdot\epsilon$ 이다. **임계값 선택이 랭크 판정을
  바꾸므로**, 랭크 결핍 진단에서는 임계값을 명시해야 한다.

## 유도

### R1 — 조건수의 제곱

$A = U\Sigma V^\top$ (얇은 SVD)이면

$$
A^\top A = V\Sigma^\top U^\top U \Sigma V^\top = V\Sigma^2 V^\top ,
$$

즉 $A^\top A$ 의 고윳값(= 특이값, 대칭 양반정이므로)이 $\sigma_i^2$ 다. 따라서

$$
\kappa_2(A^\top A) = \frac{\sigma_1^2}{\sigma_n^2} = \left(\frac{\sigma_1}{\sigma_n}\right)^2 = \kappa_2(A)^2 .
$$

**무엇을 잃는가**: 상대오차는 대략 $\kappa \cdot \epsilon$ 로 간다. $\kappa_2(A)=10^8$ 이면
QR 해는 $10^8 \cdot 2.2\times10^{-16} \approx 2\times10^{-8}$ 수준이지만, 정규방정식은
$10^{16}\cdot 2.2\times10^{-16} \approx 2$ — **의미 있는 자리가 남지 않는다.** 재현 과제가
이 경계를 수치로 보여 준다.

**가정이 깨지는 곳**: (1)은 $A$ 가 랭크 완전일 때의 등식이다. 랭크 결핍이면 $\sigma_n = 0$ 이라
양변이 모두 정의되지 않고, 그때는 **유효 조건수**(0 이 아닌 최소 특이값으로 계산)를 쓰거나
정칙화해야 한다.

### R3 — QR 해가 제곱을 피하는 이유

$A = QR$ ($Q^\top Q = I$)을 최소제곱 목적함수에 넣으면

$$
\lVert Ax - b\rVert^2 = \lVert QRx - b\rVert^2 = \lVert Rx - Q^\top b\rVert^2 + \lVert (I-QQ^\top)b\rVert^2,
$$

여기서 두 항은 직교 분해이고 둘째 항은 $x$ 에 무관하다(열공간에 직교하는 잔차). 따라서 해는
$Rx = Q^\top b$ 다. **핵심은 $A^\top A$ 를 만들지 않는다는 것**이다 — 직교 변환은 특이값을
보존하므로 $\kappa_2(R) = \kappa_2(A)$ 이고 조건수가 제곱되지 않는다.

### R5 — 수치 랭크와 임계값

수학적 랭크는 "0 이 아닌 특이값의 개수"지만, 유한 정밀도에서 정확히 0 인 특이값은 거의 없다.
$A$ 의 성분에 크기 $\eta$ 의 섭동이 있으면 특이값은 최대 $\eta$ 만큼 움직인다(Weyl 부등식).
따라서 **$\sigma_i \lesssim \sigma_1\epsilon$ 인 특이값은 0 과 구별할 수 없다.** numpy 의 기본
임계값 $\tau = \sigma_1\max(m,n)\epsilon$ 가 이 추론에서 나온다.

**실무적 함의**: C5 의 게이지 자유도 진단과 C1 의 과매개화 영공간 진단이 모두 "수치 랭크"를
쓰므로, 임계값을 명시하지 않은 랭크 주장은 재현 불가능하다.

## 증명 스케치

### R2 — 최소제곱의 섭동 한계

**가설** H1: $A$ 는 랭크 완전. H2: $x = A^+b$, $x+\delta x = A^+(b+\delta b)$.
**결론** C: (2).

**전략**: 유사역행렬의 노름이 $1/\sigma_n$ 이라는 사실과 해의 노름 하한을 결합한다.

1. $\delta x = A^+\delta b$ (유사역행렬이 선형이므로).
2. $\lVert A^+\rVert_2 = 1/\sigma_n$ (SVD 에서 바로 나온다), 따라서
   $\lVert\delta x\rVert \le \lVert\delta b\rVert/\sigma_n$.
3. 한편 $b_{\mathcal{R}} = Ax$ 이므로 $\lVert b_{\mathcal{R}}\rVert \le \sigma_1\lVert x\rVert$,
   즉 $\lVert x\rVert \ge \lVert b_{\mathcal{R}}\rVert/\sigma_1$.
4. 2·3 을 나누면
   $\frac{\lVert\delta x\rVert}{\lVert x\rVert} \le \frac{\sigma_1}{\sigma_n}\cdot
   \frac{\lVert\delta b\rVert}{\lVert b_{\mathcal{R}}\rVert}$, 즉 C.
5. **상한은 달성된다**: $\delta b$ 를 $\sigma_n$ 의 좌특이벡터 방향으로, $b$ 를 $\sigma_1$ 의
   방향으로 두면 등호가 된다 — 즉 (2)는 느슨한 한계가 아니다.

**가설을 지우면**: H1 을 빼면 $\sigma_n = 0$ 이라 2단계가 무너진다. 랭크 결핍에서는 $\delta b$ 의
영공간 성분이 해를 임의로 바꿀 수 있어 상대오차에 **상한이 없다** — 정칙화(Tikhonov)나 최소 노름
해(R4)로 문제를 다시 정의해야 한다.

### R4 — 최소 노름 해의 유일성

**가설** 랭크 $r<n$, $x_0$ 는 임의의 최소제곱 해. **결론** $x = A^+b$ 가 유일한 최소 노름 해.

1. 해집합은 아핀 부분공간 $x_0 + \mathcal{N}(A)$ 다(잔차가 같은 모든 점).
2. $A^+b$ 는 $\mathcal{R}(A^\top) = \mathcal{N}(A)^\perp$ 에 속한다(SVD 에서 $V$ 의 앞 $r$ 열로만
   표현되므로).
3. 아핀 부분공간 $x_0 + \mathcal{N}(A)$ 에서 노름이 최소인 점은 $\mathcal{N}(A)^\perp$ 성분뿐인
   점이고, 그런 점은 **유일**하다(직교 분해의 유일성).
4. 따라서 그 점이 $A^+b$ 다.

**왜 중요한가**: "랭크 결핍이면 해가 없다"가 아니라 "해가 무한히 많고 그중 하나를 고르는 규칙이
필요하다"는 것이 올바른 이해다. C1 의 게이지 자유도 처리(prior 추가)가 같은 종류의 선택이다.

## 문제 세트

★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** $\kappa_2(A^\top A) = \kappa_2(A)^2$ 를 SVD 없이, 고윳값 정의만으로
유도하라. 그리고 $\kappa_F$(Frobenius 기반 조건수)에서는 이 관계가 성립하지 않음을 보여라.
*해답 스케치*: $A^\top A$ 의 Rayleigh 몫 최대·최소가 $\sigma_1^2, \sigma_n^2$ 임을 쓴다.
Frobenius 노름은 모든 특이값을 합하므로 제곱 관계가 깨진다.

**P2 (유도, ★★, R3)** QR 분해로 최소제곱을 풀 때 **후진대입의** 조건수가 $\kappa_2(R)$ 이고
$\kappa_2(R) = \kappa_2(A)$ 임을 보여라.
*해답 스케치*: $Q$ 가 직교이므로 $A^\top A = R^\top R$ 이고 특이값이 보존된다.

**P3 (증명, ★★★, R2)** (2)의 상한이 달성됨을 구성적으로 증명하라(5단계를 정확히).
*해답 스케치*: $b = \sigma_1 u_1$, $\delta b = \eta u_n$ 으로 두고 양변을 계산한다.

**P4 (계산, ★, R1·R5)** $A$ 의 특이값이 $(1, 10^{-4}, 10^{-9})$ 이고 $m=n=3$ 일 때
ⓐ $\kappa_2(A)$ ⓑ $\kappa_2(A^\top A)$ ⓒ numpy 기본 임계값에서의 수치 랭크를 구하라.
*정답*: ⓐ $10^9$ ⓑ $10^{18}$ ⓒ $\tau = 1\cdot3\cdot2.22\times10^{-16} \approx 6.7\times10^{-16}$
이므로 세 특이값 모두 $\tau$ 보다 크다 → 수치 랭크 **3**. 다만 $\kappa_2 = 10^9$ 이라 해의
유효숫자는 약 7자리뿐이다. 허용오차 $10^{-9}$(상대).

**P5 (구현, ★★, R1·R2·R3)** 조건수를 $10^2$ 부터 $10^{12}$ 까지 바꾼 $A$ 를 생성해
ⓐ 정규방정식(`solve`) ⓑ QR(`lstsq`) ⓒ SVD(`pinv`) 세 해법의 상대오차를 참 해와 비교해 그려라.
*루브℅릭*: ⓐ 조건수를 SVD 로 **설계해서** 생성한다(무작위 행렬에 의존하지 않는다) ⓑ 참 해를
알고 있는 방식으로 $b$ 를 만든다 ⓒ 세 곡선이 $\kappa\epsilon$ 과 $\kappa^2\epsilon$ 기울기를
따르는 것을 보인다 ⓓ 정규방정식이 $\kappa \approx 10^8$ 근방에서 무의미해지는 것을 지적한다.

**P6 (반례, ★★, R4·R5)** 임계값 선택만 바꿔서 수치 랭크가 달라지는 행렬을 구성하고, 그 두
랭크가 각각 어떤 해를 주는지 보여라. "랭크가 2 다"라는 주장이 왜 임계값 없이는 무의미한지 쓰라.
*성질 체크리스트*: 특이값을 $\tau$ 근처에 **일부러** 놓는다(예: $\sigma = (1, 10^{-15}, 10^{-17})$).
임계값을 조금 바꾸면 랭크가 2 ↔ 1 로 바뀌고 최소 노름 해가 달라진다.

## 논문 읽기

**교재 예외 적용** (레슨 표준 §5). 이 레슨의 1차 자료는 논문이 아니라 표준 교재다. 아래 두
장을 읽고 **1페이지 노트**를 쓴다. 고정 질문 중 1·3·4·8(문제·아이디어·보장·의심할 가정)을 적용한다.

1. **Trefethen & Bau, *Numerical Linear Algebra*, Lectures 11–20** — QR, 최소제곱, 조건수,
   안정성. 질문: ⓐ 저자들이 "후진 안정성(backward stability)"을 정의하는 방식을 쓰고, 그것이
   "정확한 해"와 어떻게 다른지 설명하라. ⓑ 정규방정식이 후진 안정하지 **않다**는 주장의 근거는?
2. **Nocedal & Wright, *Numerical Optimization*, ch.10** — 최소제곱 문제. 질문: ⓐ 저자들이
   정규방정식을 쓰는 것을 언제 정당화하는가(어떤 조건에서 괜찮다고 하는가)? ⓑ 그 조건이
   로보틱스의 추정 문제(C5)에서 성립하는가?

**보조 문헌 1편**(방법론): Boyd & Vandenberghe 부록 A 와 C — 선형대수 배경과 수치 선형대수 요약.

## 재현 과제

**티어 R1 (수치 검증).** 예산: 노트북 CPU 1분 이내, numpy 만. 네 조건을 모두 만족해야 통과다.

1. **조건수 제어 생성**: $\kappa$ 를 지정해 $A = U\Sigma V^\top$ 를 만든다($U, V$ 는 무작위
   직교, $\Sigma$ 는 $\sigma_1=1$, $\sigma_n=1/\kappa$ 로 로그 등간격). 생성한 $A$ 에 대해
   `np.linalg.cond(A)` 가 목표 $\kappa$ 와 상대오차 $10^{-10}$ 이내로 일치.
2. **세 해법의 오차 곡선**: $\kappa \in \{10^2, 10^4, \dots, 10^{12}\}$ 에 대해 정규방정식·QR·SVD
   해의 상대오차 $\lVert\hat{x}-x^\star\rVert/\lVert x^\star\rVert$ 를 그린다. 결과가
   **정규방정식 $\approx \kappa^2\epsilon$, QR·SVD $\approx \kappa\epsilon$** 기울기를 따라야 한다
   (로그-로그 기울기 2 와 1, 추정 기울기의 오차 ±0.2 이내).
3. **임계값 경계**: $\kappa = 10^{16}$ 인 $A$ 에서 정규방정식의 상대오차가 $O(1)$ 로 무의미해지고
   QR 은 여전히 $10^{-1}$ 이하임을 확인.
4. **최소 노름 해**: 랭크 2 인 $3\times3$ $A$ 에 대해 `pinv` 해가 ⓐ 잔차 최소이고
   ⓑ 영공간 성분이 $10^{-12}$ 이하이며 ⓒ 임의의 다른 최소제곱 해보다 노름이 작음을 확인.

**비교 대상**: `scipy.linalg.lstsq` 와 `numpy.linalg.lstsq` 의 결과가 $10^{-10}$ 이내로 일치.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 세 해법의 오차 곡선이 모두 같다 | 조건수가 충분히 크지 않다 | `cond(A)` 를 출력해 목표와 비교. 무작위 행렬은 보통 $\kappa \sim 10^2$ 다 |
| 기울기가 2 와 1 로 갈라지지 않는다 | $b$ 에 열공간 밖 성분이 지배적이다 | $b = Ax^\star$ 로(잔차 0) 먼저 확인한 뒤 노이즈를 더한다 |
| `pinv` 해의 영공간 성분이 크다 | 임계값이 너무 커서 랭크를 과소 판정 | `pinv(A, rcond=...)` 를 명시하고 특이값을 출력 |
| 조건수가 목표와 다르다 | $U, V$ 가 직교가 아니다(QR 로 만들지 않았다) | `norm(U.T@U - I)` 를 확인 |

## 열린 문제

- **(열린 문제) 로보틱스 규모 희소 문제의 조건수 추정** — 밀집 행렬의 조건수는 SVD 로 구하면
  되지만, 번들 조정 규모(변수 $10^6$)에서는 SVD 가 불가능하다. 반복법으로 조건수를 **싸게
  추정**하는 실용적 방법이 부족하고, 전처리기 선택이 대부분 경험적이다
  (`c7-bundle-adjustment`, `c5-sparsity-isam` 과 이어진다).
- **(열린 문제) 수치 랭크 임계값의 원리적 선택** — 기본 임계값은 섭동 크기를 기계 정밀도로
  가정하지만, 실제 측정 노이즈는 그보다 훨씬 크다. **측정 불확실성과 임계값을 연결하는** 원리적
  방법이 없어, 게이지 결핍 진단이 임계값 선택에 민감하다.
- **(열린 문제) 혼합 정밀도의 타당 범위** — GPU 의 단정밀도·반정밀도를 로보틱스 추정에 쓰려는
  흐름이 있지만, 조건수가 큰 문제에서 어디까지 안전한지에 대한 기준이 정리되지 않았다.

## 개념 점검

`rc quiz r0-linear-algebra-decompositions` 로 푼다. 개념 점검 전용이고 실제 과제는 문제 세트와
재현 과제다.

```quiz
activity: r0-linear-algebra-decompositions-quiz
questions:
  - id: q1
    type: short
    prompt: "$\\kappa_2(A) = 10^6$ 일 때 $\\kappa_2(A^\\top A)$ 는?"
    answer: ["10^12", "1e12", "10**12", "1000000000000", "10^{12}"]
    explanation: "$A^\\top A$ 의 특이값이 $A$ 의 특이값의 제곱이므로 조건수도 제곱된다. 배정밀도에서 $\\kappa=10^{12}$ 는 유효숫자 약 4자리만 남긴다."
    concept: { front: "정규방정식의 조건수", back: "$\\kappa_2(A^\\top A) = \\kappa_2(A)^2$ — 유효숫자를 절반 잃는다" }
  - id: q2
    type: single
    prompt: "QR 로 최소제곱을 푸는 것이 정규방정식보다 수치적으로 나은 핵심 이유는?"
    choices:
      - "연산량이 더 적다"
      - "$A^\\top A$ 를 만들지 않아 조건수가 제곱되지 않는다"
      - "항상 정확한 해를 준다"
      - "랭크 결핍에서도 유일한 해를 준다"
    answer: 1
    explanation: "직교 변환이 특이값을 보존하므로 $\\kappa_2(R)=\\kappa_2(A)$ 다. 연산량은 QR 이 오히려 더 많고, 랭크 결핍에서 유일 해를 주는 것은 SVD(유사역행렬)다."
    concept: { front: "QR 최소제곱의 이점", back: "$A^\\top A$ 를 만들지 않아 조건수가 제곱되지 않는다(직교 변환이 특이값 보존)" }
  - id: q3
    type: truefalse
    prompt: "랭크 결핍 행렬의 최소제곱 해는 존재하지 않는다."
    answer: false
    explanation: "해가 **무한히 많다**(아핀 부분공간 $x_0+\\mathcal{N}(A)$). 그중 노름이 최소인 해가 유일하게 존재하고 $A^+b$ 로 주어진다. '해가 없다'가 아니라 '고르는 규칙이 필요하다'가 맞다."
    concept: { front: "랭크 결핍에서의 최소제곱 해", back: "무한히 많다. 최소 노름 해가 유일하고 $A^+b$ 다 — 고르는 규칙이 필요한 것" }
  - id: q4
    type: single
    prompt: "\"이 행렬의 수치 랭크는 2 다\" 라는 주장이 재현 가능하려면 무엇이 함께 보고되어야 하는가?"
    choices:
      - "행렬의 크기"
      - "특이값 판정 임계값"
      - "사용한 라이브러리 버전"
      - "조건수"
    answer: 1
    explanation: "수치 랭크는 $\\sigma_i > \\tau$ 인 특이값의 개수이고 $\\tau$ 에 따라 바뀐다. 임계값 없는 랭크 주장은 재현 불가능하다 — C1·C5 의 영공간 진단이 모두 이 값을 쓴다."
    concept: { front: "수치 랭크 보고에 필요한 것", back: "판정 임계값 $\\tau$. 기본값은 $\\sigma_1\\max(m,n)\\epsilon$ 이지만 명시해야 한다" }
```

## 이 단계 공부법

1. **(1)을 백지에서 유도한다 (30분)** — SVD 두 줄이면 끝난다. 이 한 줄이 "왜 정규방정식을
   쓰지 않는가"의 전부이므로 외우지 말고 유도할 수 있게 한다.
2. **오차 곡선을 먼저 그린다 (90분)** — 재현 과제 조건 2 를 이 레슨의 **처음**에 한다. 기울기
   2 와 1 이 갈라지는 그림을 보고 나면 나머지 유도가 설명으로 읽힌다.
3. **조건수를 설계해서 만든다** — 무작위 행렬은 조건수가 작아 차이가 드러나지 않는다. SVD 로
   $\Sigma$ 를 지정해 만드는 기법은 연구 트랙 전체에서 재사용된다.
4. **랭크 결핍을 "선택의 문제"로 본다 (60분)** — P6 을 풀어 임계값이 해를 바꾸는 것을 본다.
   C1 의 게이지 자유도와 C5 의 영공간 진단이 같은 구조다.
5. **교재는 안정성 개념에 집중해 읽는다 (100분)** — Trefethen & Bau 의 후진 안정성 정의가
   핵심이다. "정확한 해"가 아니라 "조금 다른 문제의 정확한 해"라는 관점이 수치해석의 중심이고,
   재현 과제의 수용 기준을 쓰는 방식도 이 관점에서 나온다.
6. **다음 레슨과의 연결을 확인한다 (20분)** — `r0-sparse-linear-algebra` 가 같은 문제를
   희소 구조에서 다룬다. 조건수 논의가 거기서 전처리(preconditioning)로 이어진다.

**통과 기준**: (1)과 (2)를 백지에서 유도할 수 있고, R4 의 최소 노름 해 유일성을 증명할 수 있고,
재현 과제 네 조건을 만족하는 코드와 교재 노트 2편이 있다.
