---
id: r0-sparse-linear-algebra
title: 희소 선형대수와 대규모 최소제곱
summary: >-
  희소 Cholesky 의 fill-in 이 소거 순서에 어떻게 의존하는지 유도하고, Schur 보완으로 블록 구조를
  활용하며, 반복법(CG)의 수렴이 조건수의 제곱근에 지배되는 것을 확인한다.
objectives:
  - 희소 행렬의 Cholesky 분해에서 fill-in 이 생기는 조건을 그래프로 설명할 수 있다.
  - 소거 순서가 fill-in 을 바꾸는 것을 유도하고 순서화 알고리즘의 목적을 말할 수 있다.
  - Schur 보완으로 블록 구조를 소거하고 그 결과가 조밀해지는 이유를 설명할 수 있다.
  - 공액기울기법(CG)의 수렴 한계가 조건수의 제곱근에 비례함을 쓸 수 있다.
  - 로보틱스 문제(포즈 그래프, 번들 조정)의 희소 구조를 식별하고 적절한 해법을 고를 수 있다.
prerequisites: [r0-linear-algebra-decompositions]
difficulty: 4
estimated_minutes: 420
tags: [numerical-linear-algebra, sparsity, cholesky, conjugate-gradient, research]
activities:
  - id: r0-sparse-linear-algebra-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 80
  - id: r0-sparse-linear-algebra-textbook
    kind: reading
    title: 교재 읽기 (Barfoot ch.3, Nocedal-Wright ch.5, Davis) + 1페이지 노트
    estimated_minutes: 100
  - id: r0-sparse-linear-algebra-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 130
  - id: r0-sparse-linear-algebra-reproduction
    kind: reproduction
    title: 재현 과제 — 소거 순서에 따른 fill-in 과 CG 수렴 (R1)
    estimated_minutes: 95
  - id: r0-sparse-linear-algebra-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.3 (선형-가우시안 추정). 희소 구조와 소거 순서를 추정 문제의 맥락에서 다룬다.
  - title: "Nocedal & Wright, Numerical Optimization (2nd ed.)"
    kind: book
    note: ch.5 (공액기울기법). CG 의 수렴 한계와 전처리. (공식 URL 미확인)
  - title: "SciPy sparse 문서"
    url: https://docs.scipy.org/doc/scipy/reference/sparse.html
    kind: notes
    note: csr/csc 형식, splu, spsolve, cg. 재현 과제의 도구.
  - title: "SuiteSparse (Tim Davis)"
    url: https://people.engr.tamu.edu/davis/suitesparse.html
    kind: code
    note: CHOLMOD·COLAMD 의 원 구현. 순서화 알고리즘의 표준.
---

# 희소 선형대수와 대규모 최소제곱

## 전제와 기호

| 기호 | 뜻 |
|---|---|
| $\Lambda \in \mathbb{R}^{n\times n}$ | 대칭 양정 정보행렬 ($= A^\top A$ 또는 $J^\top\Sigma^{-1}J$) |
| $G(\Lambda)$ | $\Lambda$ 의 **인접 그래프**: 정점 = 변수, 간선 = 비영 성분 |
| $L$ | Cholesky 인자 ($\Lambda = LL^\top$) |
| $\mathrm{nnz}(\cdot)$ | 비영원소 개수 |
| $\pi$ | 소거 순서(permutation) |
| $\kappa$ | $\Lambda$ 의 조건수 |

전제: `r0-linear-algebra-decompositions`(조건수·분해)와 `f0-linear-algebra`.

## 핵심 결과

- **R1 (fill-in 의 그래프 조건) [D2]** — 변수 $k$ 를 소거하면 그 이웃들이 **완전 그래프(clique)로
  연결**된다. 따라서 $L$ 의 비영원소는

$$
L_{ij} \ne 0 \iff \text{소거 순서에서 } j < i \text{ 이고 } G \text{ 에 } j \to i \text{ 경로가 존재(중간 정점은 모두 } < j) \tag{1}
$$

  — 이것이 fill-in 이다. 원래 $\Lambda$ 에 없던 간선이 생긴다.
- **R2 (순서 의존성) [D2]** — 같은 $\Lambda$ 에 대해 $\mathrm{nnz}(L)$ 은 소거 순서에 따라
  **수십 배** 달라진다. 최적 순서를 찾는 것은 NP-난해이고, 실무는 근사 알고리즘(COLAMD, AMD,
  nested dissection)을 쓴다 **[D0]**.
- **R3 (Schur 보완) [D3]** — 블록 분할 $\Lambda = \begin{bmatrix}\Lambda_{11} & \Lambda_{12}\\
  \Lambda_{21} & \Lambda_{22}\end{bmatrix}$ 에서 첫 블록을 소거하면

$$
S = \Lambda_{22} - \Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}, \tag{2}
$$

  이고 $S$ 는 양정이지만 **일반적으로 $\Lambda_{22}$ 보다 조밀하다** — 주변화(marginalization)가
  그래프를 조밀하게 만드는 것이 이 사실이다.
- **R4 (CG 의 수렴 한계) [D2]** — 공액기울기법의 $k$ 번째 반복 오차는

$$
\frac{\lVert x_k - x^\star\rVert_\Lambda}{\lVert x_0 - x^\star\rVert_\Lambda}
\le 2\left(\frac{\sqrt{\kappa}-1}{\sqrt{\kappa}+1}\right)^{k} , \tag{3}
$$

  즉 필요한 반복 수가 $O(\sqrt{\kappa})$ 다. 직접법의 $\kappa$ 의존성과 달리 **제곱근**이 들어가고,
  전처리의 목표는 이 $\kappa$ 를 줄이는 것이다.
- **R5 (로보틱스의 두 구조) [D1]** — 포즈 그래프는 **띠(band)에 가까운** 구조라 순서화가 잘 듣고
  직접법이 빠르다. 번들 조정은 포즈–랜드마크 **이분 구조**라 Schur 보완으로 랜드마크를 먼저
  소거하는 것이 표준이다(축소된 카메라 블록만 풀면 된다).

## 유도

### R1 — 소거가 clique 을 만든다

Cholesky 의 한 단계는 변수 $k$ 를 소거하는 것이고, 수식으로는 Schur 보완 (2)의 1차원 판이다:

$$
\Lambda^{(k+1)}_{ij} = \Lambda^{(k)}_{ij} - \frac{\Lambda^{(k)}_{ik}\Lambda^{(k)}_{kj}}{\Lambda^{(k)}_{kk}} .
$$

여기서 $\Lambda_{ik} \ne 0$ 이고 $\Lambda_{kj} \ne 0$ 이면, 원래 $\Lambda_{ij} = 0$ 이었어도
갱신 후 $\ne 0$ 이 된다. **그래프로 읽으면**: $k$ 의 이웃 $i$ 와 $j$ 가 $k$ 를 통해 연결되어
있었으므로, $k$ 를 지우면서 $i$–$j$ 간선을 새로 만들어야 한다. $k$ 의 모든 이웃 쌍에 대해 이 일이
일어나므로 이웃들이 **clique** 이 된다.

**따라서**: 차수(이웃 수)가 큰 정점을 먼저 소거하면 큰 clique 가 생긴다. 순서화 알고리즘의
기본 발상이 "차수가 작은 정점을 먼저 소거"(minimum degree)인 이유다.

**가정이 깨지는 곳**: 위 갱신은 $\Lambda_{kk} \ne 0$ 을 요구한다. 양정이면 보장되지만, 양정이
아닌(게이지 결핍) 행렬에서는 피벗이 0 이 되어 분해가 실패한다 — `c1-manifold-optimization` 의
게이지 영공간이 여기서 **분해 실패**로 나타난다.

### R4 — CG 수렴 한계의 출처

CG 의 $k$ 번째 반복해는 Krylov 부분공간
$\mathrm{span}\{r_0, \Lambda r_0, \dots, \Lambda^{k-1}r_0\}$ 에서 $\Lambda$-노름 오차를
최소화한다. 따라서 오차는 **$k$ 차 다항식 $p$ 중 $p(0)=1$ 인 것들에 대한 최소값**으로 쓰인다:

$$
\frac{\lVert x_k-x^\star\rVert_\Lambda}{\lVert x_0-x^\star\rVert_\Lambda}
\le \min_{p:\,p(0)=1,\ \deg p \le k}\ \max_{\lambda \in [\lambda_{\min}, \lambda_{\max}]} |p(\lambda)| .
$$

이 최소최대 문제의 답이 **구간에서 균등 진동하는 Chebyshev 다항식**이고, 그 값을 계산하면 (3)이
나온다(생략: Chebyshev 다항식의 극값 성질 — Nocedal–Wright 정리 5.5).

**읽는 법**: 조건수가 $10^6$ 이면 직접법의 정확도 손실은 $\kappa\epsilon$ 이지만 CG 의 반복 수는
$\sqrt{10^6}=10^3$ 수준이다. **고유값이 뭉쳐 있으면 훨씬 빨라진다** — (3)은 구간만 쓰는 느슨한
한계이고, 실제 수렴은 스펙트럼 분포에 달려 있다. 전처리가 "조건수를 줄인다"기보다
"고유값을 뭉친다"로 이해하는 것이 정확하다.

## 증명 스케치

### R3 — Schur 보완의 양정성과 조밀화

**가설** H1: $\Lambda$ 는 대칭 양정. H2: $\Lambda_{11}$ 은 가역(H1 에서 따라온다).
**결론** C: $S = \Lambda_{22} - \Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ 는 대칭 양정이고,
$x_2$ 의 주변 분포의 정보행렬이다.

**전략**: 블록 LDL 분해로 $\Lambda$ 를 쓰고 이차형식을 분리한다.

1. 블록 소거로
   $\Lambda = \begin{bmatrix}I & 0\\ \Lambda_{21}\Lambda_{11}^{-1} & I\end{bmatrix}
   \begin{bmatrix}\Lambda_{11} & 0\\ 0 & S\end{bmatrix}
   \begin{bmatrix}I & \Lambda_{11}^{-1}\Lambda_{12}\\ 0 & I\end{bmatrix}$.
2. 양쪽 삼각 인자는 가역이므로 $\Lambda \succ 0 \iff \Lambda_{11} \succ 0$ 이고 $S \succ 0$.
   따라서 $S$ 는 양정이다.
3. 확률적 해석: $x \sim \mathcal{N}(\mu, \Lambda^{-1})$ 에서 $x_1$ 을 주변화하면 $x_2$ 의
   정보행렬이 정확히 $S$ 다(가우시안 주변화 — `f0-probability-statistics`).
4. **조밀화**: $\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ 는 $\Lambda_{11}^{-1}$ 이 일반적으로
   조밀하므로 조밀하다. 즉 $x_1$ 의 이웃이던 $x_2$ 성분들이 **서로 연결**된다 — R1 의 clique 생성과
   같은 현상의 블록 판이다.

**가설을 지우면**: H1 을 빼면 $\Lambda_{11}$ 이 특이할 수 있어 $S$ 가 정의되지 않는다. 실무에서는
의사역행렬이나 정칙화를 쓰지만, 그러면 주변 분포의 해석이 달라진다.

**왜 중요한가**: C5 의 iSAM2 가 "주변화하지 않고 변수를 유지"하는 설계를 택한 이유가 4단계다.
번들 조정은 거꾸로 **의도적으로** 랜드마크를 주변화해 작은 조밀 블록을 만든다(R5).

## 문제 세트

★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** 정점 5개의 경로 그래프(1–2–3–4–5)에 대응하는 $\Lambda$ 에서
ⓐ 순서 $(1,2,3,4,5)$ ⓑ 순서 $(3,1,5,2,4)$ 로 소거했을 때 $\mathrm{nnz}(L)$ 를 각각 구하라.
*해답 스케치*: ⓐ 는 fill-in 이 없다(띠 구조를 순서대로 소거). ⓑ 는 중앙을 먼저 지워 양쪽이
연결되므로 fill-in 이 생긴다. 소거마다 clique 을 그려서 세면 된다.

**P2 (유도, ★★, R4)** (3)에서 "반복 수가 $O(\sqrt{\kappa})$" 를 끌어내라. 즉
상대오차 $\delta$ 를 달성하는 $k$ 의 상한을 $\kappa$ 와 $\delta$ 로 쓰라.
*해답 스케치*: $\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^k \le \delta/2$ 에 로그를 취하고
$\log\frac{\sqrt\kappa+1}{\sqrt\kappa-1} \approx 2/\sqrt\kappa$ 를 쓰면
$k \gtrsim \tfrac{1}{2}\sqrt\kappa\log(2/\delta)$.

**P3 (증명, ★★★, R3)** R3 의 1단계 블록 LDL 분해를 직접 전개해 확인하고, 3단계(가우시안
주변화가 Schur 보완을 준다)를 증명하라.
*해답 스케치*: 결합 밀도의 지수를 $x_1$ 에 대해 완전제곱식으로 정리하고 적분한다. $x_1$ 항이
사라지고 남는 이차형식의 계수가 $S$ 다.

**P4 (계산, ★, R4)** $\kappa = 10^4$ 일 때 상대오차 $10^{-6}$ 을 달성하는 CG 반복 수의 상한은?
*정답*: $k \gtrsim \tfrac12\sqrt{10^4}\log(2\times10^6) = 50 \times 14.5 \approx 725$.
허용오차: 같은 자리수(수백 회)면 통과. 직접법이 더 나을 수 있는 규모라는 점을 함께 적어야 한다.

**P5 (구현, ★★, R1·R2·R4)** 포즈 그래프 모양의 희소 $\Lambda$(사슬 + 루프 폐쇄 몇 개)를 만들어
ⓐ 순서화 없이 ⓑ COLAMD/AMD 순서로 Cholesky 를 구해 $\mathrm{nnz}(L)$ 를 비교하고
ⓒ 같은 계를 CG 로 풀어 반복 수를 (3)의 한계와 비교하라.
*루브릭*: ⓐ 희소 형식(csc)을 쓰고 밀집으로 변환하지 않는다 ⓑ $\mathrm{nnz}$ 차이가 **10배 이상**
나오도록 문제를 충분히 크게 잡는다($n \gtrsim 2000$) ⓒ CG 반복 수가 (3)의 상한 이하임을 확인한다
ⓓ 게이지를 고정하지 않으면 Cholesky 가 실패하는 것을 확인하고 prior 를 더해 해결한다.

**P6 (반례, ★★, R3·R5)** 주변화가 **이득인** 구조와 **손해인** 구조를 각각 만들어라.
번들 조정에서 랜드마크 주변화가 이득인 이유와, 포즈 그래프에서 과거 포즈 주변화가 손해일 수 있는
이유를 $\mathrm{nnz}$ 로 보여라.
*성질 체크리스트*: 이분 구조에서 한쪽이 **서로 연결되지 않은** 많은 변수면 주변화가 이득이다
(랜드마크끼리 간선이 없다). 반대로 주변화 대상의 이웃이 많으면 큰 clique 가 생겨 손해다.

## 논문 읽기

**교재 예외 적용**(레슨 표준 §5). 아래 두 장을 읽고 1페이지 노트를 쓴다(고정 질문 1·3·4·8).

1. **Barfoot, *State Estimation for Robotics*, ch.3** — 선형-가우시안 추정의 희소 구조.
   질문: ⓐ 저자가 추정 문제의 희소성을 **어디서** 끌어내는지(측정의 국소성?) 쓰라.
   ⓑ 순서화가 추정 정확도를 바꾸는가, 비용만 바꾸는가?
2. **Nocedal & Wright, *Numerical Optimization*, ch.5** — 공액기울기법과 전처리.
   질문: ⓐ 저자들이 CG 를 "직접법보다 나은" 경우로 제시하는 조건은? ⓑ 전처리기 선택에 대해
   저자들이 제시하는 원칙과, 그것이 로보틱스 문제에 적용 가능한지 판단하라.

**보조 문헌 1편**(방법론): [SuiteSparse](https://people.engr.tamu.edu/davis/suitesparse.html) 의
CHOLMOD·COLAMD 문서 — 순서화 알고리즘이 실제로 무엇을 최소화하는지.

## 재현 과제

**티어 R1 (수치 검증).** 예산: 노트북 CPU 1분 이내, scipy.sparse 만. 네 조건을 모두 만족해야 한다.

1. **fill-in 의 순서 의존성**: 포즈 그래프 모양($n = 2000$ 변수, 사슬 + 루프 폐쇄 20개)의
   $\Lambda$ 에서 ⓐ 자연 순서 ⓑ AMD/COLAMD 순서의 $\mathrm{nnz}(L)$ 를 비교해 **10배 이상** 차이를
   확인한다.
2. **Schur 보완의 조밀화**: 포즈 50 · 랜드마크 500 의 이분 구조를 만들고, 랜드마크를 주변화한
   축소 계의 밀도(= $\mathrm{nnz}/n^2$)가 원래 포즈 블록보다 **커지는 것**을 수치로 보인다.
   동시에 전체 해가 주변화 전후로 $10^{-10}$ 이내로 일치함을 확인한다.
3. **CG 수렴과 (3)**: 조건수를 $10^2, 10^4, 10^6$ 으로 설계한 계에서 CG 반복 수를 세고,
   (3)의 상한 이하이며 $\sqrt\kappa$ 에 비례해 증가하는 것을 확인한다(로그-로그 기울기 0.5±0.15).
4. **게이지 결핍에서의 분해 실패**: 상대 측정만으로 만든 $\Lambda$ 에서 Cholesky 가 실패하거나
   피벗이 $10^{-12}$ 이하로 떨어지는 것을 확인하고, prior 하나를 더한 뒤 성공하는 것을 보인다.

**비교 대상**: `scipy.sparse.linalg.splu` 또는 `cholmod`(설치 가능하면)와 직접 구현한 해의 차이가
$10^{-10}$ 이내.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 순서화 효과가 안 보인다 | 문제가 너무 작거나 루프 폐쇄가 없다 | $n$ 을 키우고 루프 간선을 추가. 순수 사슬은 자연 순서가 이미 최적이다 |
| Cholesky 가 실패한다 | 게이지 결핍(R1 의 피벗 0) 또는 수치 비양정 | $\Lambda$ 의 최소 고윳값을 확인하고 prior 를 더한다 |
| CG 가 한계보다 느리다 | 조건수 추정이 틀렸거나 전처리 없이 비정규화 문제 | `eigsh` 로 극단 고윳값을 추정해 $\kappa$ 를 다시 계산 |
| 주변화 후 해가 달라진다 | Schur 보완의 우변 갱신을 빠뜨렸다 | $b_2 - \Lambda_{21}\Lambda_{11}^{-1}b_1$ 를 확인 |

## 열린 문제

- **(열린 문제) 로보틱스 구조에 맞는 순서화** — COLAMD·AMD 는 일반 희소 행렬용이고, 포즈 그래프나
  번들 조정의 **알려진 구조**(사슬 + 희소 루프, 이분 구조)를 활용하는 전용 순서화가 체계화되지
  않았다. 실무는 휴리스틱에 의존한다(`c5-sparsity-isam`).
- **(열린 문제) 매니폴드 위 전처리기의 재사용** — 접공간이 매 반복 바뀌므로 전처리기를 재사용할
  원리적 방법이 부족하다(`c1-manifold-optimization` 의 열린 문제와 같은 항목).
- **(열린 문제) 직접법과 반복법의 전환 기준** — 문제 크기·조건수·희소 구조가 주어졌을 때 어느
  쪽이 빠른지를 **사전에** 판단하는 정량적 기준이 없다. 번들 조정 규모에서 특히 실무적 문제다.

## 개념 점검

`rc quiz r0-sparse-linear-algebra` 로 푼다. 개념 점검 전용이다.

```quiz
activity: r0-sparse-linear-algebra-quiz
questions:
  - id: q1
    type: single
    prompt: "Cholesky 에서 변수 $k$ 를 소거하면 그래프에 무슨 일이 일어나는가?"
    choices:
      - "$k$ 와 그 간선들이 사라지고 끝난다"
      - "$k$ 의 이웃들이 서로 완전 연결(clique)된다"
      - "그래프가 항상 더 희소해진다"
      - "간선 수가 변하지 않는다"
    answer: 1
    explanation: "갱신식 $\\Lambda_{ij} \\mathrel{-}= \\Lambda_{ik}\\Lambda_{kj}/\\Lambda_{kk}$ 가 $k$ 의 이웃 쌍마다 새 간선을 만든다. 그래서 차수가 작은 정점을 먼저 소거하는 것(minimum degree)이 fill-in 을 줄인다."
    concept: { front: "소거와 fill-in", back: "소거된 정점의 이웃들이 clique 이 된다 — 차수가 작은 정점을 먼저 소거해야 fill-in 이 적다" }
  - id: q2
    type: truefalse
    prompt: "소거 순서는 해의 정확도를 바꾸지 않고 계산 비용만 바꾼다."
    answer: true
    explanation: "순서는 같은 해를 다른 비용으로 계산한다(수치 오차는 미세하게 다를 수 있으나 해 자체는 같다). 그래서 순서화는 **비용** 문제이고, 비용이 수십 배 차이 나므로 중요하다."
    concept: { front: "소거 순서가 바꾸는 것", back: "계산 비용(fill-in). 해는 같다 — 그래서 순서화는 성능 문제다" }
  - id: q3
    type: single
    prompt: "번들 조정에서 랜드마크를 Schur 보완으로 먼저 소거하는 이유는?"
    choices:
      - "랜드마크가 포즈보다 중요하지 않기 때문"
      - "랜드마크끼리는 서로 연결되지 않아 소거해도 랜드마크 쪽 fill-in 이 없고, 남는 카메라 블록이 작기 때문"
      - "Schur 보완이 조건수를 줄이기 때문"
      - "랜드마크의 정보행렬이 항상 대각이라서"
    answer: 1
    explanation: "이분 구조에서 랜드마크끼리 간선이 없으므로 각 랜드마크를 독립적으로 소거할 수 있고, 남는 축소 카메라 계가 훨씬 작다. 조건수는 오히려 나빠질 수 있다."
    concept: { front: "번들 조정의 Schur 보완", back: "랜드마크는 서로 연결되지 않아 싸게 소거되고, 남는 카메라 블록이 작다" }
  - id: q4
    type: short
    prompt: "CG 로 상대오차를 줄이는 데 필요한 반복 수는 조건수 $\\kappa$ 의 어떤 함수에 비례하는가? (예: kappa, sqrt(kappa), kappa^2)"
    answer: ["sqrt(kappa)", "√kappa", "sqrt κ", "루트 kappa", "kappa^0.5", "sqrt(k)"]
    explanation: "(3)에서 $k = O(\\sqrt\\kappa\\log(1/\\delta))$ 다. 직접법의 정확도 손실이 $\\kappa\\epsilon$ 인 것과 대조된다. 전처리의 목표는 고유값을 뭉쳐 이 값을 줄이는 것이다."
    concept: { front: "CG 의 반복 수", back: "$O(\\sqrt{\\kappa}\\log(1/\\delta))$ — 조건수의 제곱근" }
```

## 이 단계 공부법

1. **그래프로 먼저 본다 (40분)** — R1 을 식이 아니라 그림으로 익힌다. 작은 그래프(정점 5–6개)에서
   손으로 소거하며 clique 이 생기는 것을 그린다. P1 이 그 연습이다.
2. **fill-in 차이를 숫자로 본다 (60분)** — 재현 과제 조건 1 을 먼저 한다. 10배 차이를 보고 나면
   순서화가 왜 별도 연구 분야인지 납득된다.
3. **Schur 보완을 두 관점으로 쓴다 (60분)** — 선형대수(블록 소거)와 확률(가우시안 주변화)로
   각각 유도한다. C5 의 iSAM2 와 C7 의 번들 조정이 이 두 관점을 번갈아 쓴다.
4. **게이지 결핍을 분해 실패로 만난다 (40분)** — 재현 과제 조건 4 를 반드시 한다. `c1-manifold-optimization`
   에서 "영공간"으로 배운 것이 여기서는 "피벗 0"으로 나타난다. 같은 현상의 두 얼굴이다.
5. **CG 는 스펙트럼으로 이해한다 (50분)** — (3)은 느슨한 한계다. 고유값을 일부러 뭉쳐 놓은 계에서
   CG 가 한계보다 훨씬 빨리 수렴하는 것을 확인하면, 전처리의 목적이 "조건수 축소"가 아니라
   "고유값 뭉치기"임이 분명해진다.
6. **교재는 구조의 출처를 찾으며 읽는다 (100분)** — Barfoot ch.3 에서 "희소성이 어디서 오는가"
   (측정의 국소성)를 찾는다. 이 질문의 답이 C5 전체의 설계 근거다.

**통과 기준**: R1 을 그래프로 설명할 수 있고, Schur 보완을 두 관점으로 유도할 수 있고, (3)에서
반복 수 상한을 끌어낼 수 있고, 재현 과제 네 조건을 만족하는 코드와 교재 노트 2편이 있다.
