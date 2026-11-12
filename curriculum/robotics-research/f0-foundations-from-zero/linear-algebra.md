---
id: f0-linear-algebra
title: 선형대수
summary: >-
  소거법·부분공간·네 개의 기본 부분공간·고윳값·SVD 를 손으로 계산하고 의미를 말하는 수준까지
  올린다. MIT 18.06(Strang)으로 안내하는 가이드형 레슨이고, 진단을 통과하면 건너뛴다.
objectives:
  - 소거법으로 연립방정식을 풀고 해의 존재·유일성을 랭크로 판정할 수 있다.
  - 네 개의 기본 부분공간(열공간·영공간·행공간·좌영공간)의 차원 관계를 설명할 수 있다.
  - 직교 투영과 최소제곱 해를 정규방정식으로 유도할 수 있다.
  - 고윳값·고유벡터를 계산하고 대칭행렬의 성질(직교 대각화, 실수 고윳값)을 말할 수 있다.
  - SVD 의 구조를 설명하고 특이값으로 랭크·조건수를 계산할 수 있다.
prerequisites: [f0-calculus-single-variable]
difficulty: 1
estimated_minutes: 4800
tags: [foundations, linear-algebra, guide]
activities:
  - id: f0-linear-algebra-diagnostic
    kind: quiz
    title: 시작 전 자가 진단 (통과하면 이 레슨을 건너뛴다)
    estimated_minutes: 40
  - id: f0-linear-algebra-lectures
    kind: reading
    title: MIT 18.06 강의 영상 수강
    estimated_minutes: 2400
  - id: f0-linear-algebra-problems
    kind: exercise
    title: 문제집·기출 시험 풀이 (해답으로 자기 채점)
    estimated_minutes: 2360
resources:
  - title: "MIT 18.06 Linear Algebra (Spring 2010, Gilbert Strang)"
    url: https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/
    kind: course
    note: 1순위. 강의 영상, 문제집과 해답, 기출 시험과 해답 전부 공개.
  - title: "Gilbert Strang 의 교재 페이지"
    url: https://math.mit.edu/~gs/
    kind: book
    note: Introduction to Linear Algebra 등. 무료 공개는 아니므로 교재 없이 18.06 만으로 진행해도 된다.
  - title: "NumPy linalg 문서"
    url: https://numpy.org/doc/stable/reference/routines.linalg.html
    kind: notes
    note: 손계산을 코드로 검산할 때. svd, eig, solve, matrix_rank, cond 를 익혀 둔다.
---

# 선형대수

## 도달 목표

이 레슨은 **가이드형**이다. 통과하면 건너뛴다.

**로보틱스에서 가장 먼저, 가장 많이 쓰이는 수학이다.** 회전행렬, 야코비안, 최소제곱 추정,
공분산, 정규방정식, 조건수 — 연구 트랙의 거의 모든 레슨이 선형대수의 언어로 쓰여 있다. 그래서
F0 에서 미적분 II 보다 **앞에** 둔다. 특히 **SVD 와 조건수**는 R0 와 C5 에서 바로 쓰이므로
"들어는 봤다" 수준으로 넘기면 안 된다.

통과 기준은 §시작 전 자가 진단의 6문항 중 5문항 이상이다.

## 시작 전 자가 진단

`rc quiz f0-linear-algebra` 로 푼다. 5/6 이상이면 건너뛰고 `f0-calculus-multivariable` 로 간다.

```quiz
activity: f0-linear-algebra-diagnostic
questions:
  - id: q1
    type: short
    prompt: "$A = \\mathrm{diag}(3, 1, 0.01)$ 의 2-노름 조건수 $\\kappa_2(A)$ 는?"
    answer: ["300", "3/0.01", "300.0"]
    explanation: "$\\kappa_2 = \\sigma_{\\max}/\\sigma_{\\min} = 3/0.01 = 300$. 대각행렬이므로 특이값이 대각 성분의 절댓값이다. 조건수가 크면 수치 해법이 민감해진다 — R0 의 첫 레슨이 이것을 다룬다."
    concept: { front: "2-노름 조건수", back: "$\\kappa_2(A) = \\sigma_{\\max}/\\sigma_{\\min}$ (최대/최소 특이값의 비)" }
  - id: q2
    type: single
    prompt: "$A$ 가 $m \\times n$ 이고 랭크가 $r$ 일 때, 영공간(null space)의 차원은?"
    choices: ["$m - r$", "$n - r$", "$r$", "$n$"]
    answer: 1
    explanation: "랭크-영도 정리: $\\dim\\mathcal{N}(A) = n - r$. 좌영공간의 차원이 $m-r$ 이다. 이 구분이 포즈 그래프의 게이지 자유도(영공간 차원 6)를 이해하는 데 쓰인다."
    concept: { front: "랭크-영도 정리", back: "$m\\times n$ 행렬에서 $\\dim\\mathcal{N}(A) = n - \\mathrm{rank}$, $\\dim\\mathcal{N}(A^\\top) = m - \\mathrm{rank}$" }
  - id: q3
    type: short
    prompt: "최소제곱 문제 $\\min_x \\lVert Ax - b\\rVert^2$ 의 정규방정식을 쓰면 $A^\\top A x = ?$ (우변)"
    answer: ["A^T b", "A^Tb", "A'b", "A transpose b", "A^\\top b"]
    explanation: "$\\nabla_x \\lVert Ax-b\\rVert^2 = 2A^\\top(Ax-b) = 0$ 에서 $A^\\top Ax = A^\\top b$. 연구 트랙의 모든 추정 문제가 이 형태로 환원된다."
    concept: { front: "최소제곱의 정규방정식", back: "$A^\\top A x = A^\\top b$ — 잔차를 열공간에 직교 투영한 결과" }
  - id: q4
    type: multiple
    prompt: "실 대칭행렬 $S$ 에 대해 **항상** 참인 것을 모두 고르라."
    choices:
      - "고윳값이 모두 실수다"
      - "직교행렬로 대각화할 수 있다"
      - "고윳값이 모두 양수다"
      - "역행렬이 존재한다"
    answer: [0, 1]
    explanation: "실 대칭행렬은 실수 고윳값을 갖고 직교 대각화된다($S = Q\\Lambda Q^\\top$). 고윳값이 양수인 것은 **양정(positive definite)** 일 때만이고, 0 고윳값이 있으면 역행렬도 없다."
    concept: { front: "실 대칭행렬의 성질", back: "실수 고윳값 + 직교 대각화($S=Q\\Lambda Q^\\top$). 양정성은 별개 조건" }
  - id: q5
    type: single
    prompt: "$A$ 의 SVD 가 $A = U\\Sigma V^\\top$ 일 때, $A$ 의 열공간의 정규직교 기저는?"
    choices:
      - "$V$ 의 처음 $r$ 개 열"
      - "$U$ 의 처음 $r$ 개 열"
      - "$\\Sigma$ 의 대각 성분"
      - "$U$ 의 마지막 $m-r$ 개 열"
    answer: 1
    explanation: "$U$ 의 처음 $r$ 열이 열공간, 마지막 $m-r$ 열이 좌영공간을 span 한다. $V$ 의 처음 $r$ 열은 행공간, 마지막 $n-r$ 열은 영공간이다. SVD 는 네 부분공간을 한 번에 준다."
    concept: { front: "SVD 와 네 부분공간", back: "$U$ 앞 $r$ = 열공간, $U$ 뒤 = 좌영공간, $V$ 앞 $r$ = 행공간, $V$ 뒤 = 영공간" }
  - id: q6
    type: truefalse
    prompt: "정규방정식 $A^\\top Ax = A^\\top b$ 를 그대로 푸는 것은 QR 분해로 푸는 것과 수치적으로 동등하다."
    answer: false
    explanation: "$\\kappa(A^\\top A) = \\kappa(A)^2$ 이므로 정규방정식은 조건수를 **제곱**한다. 악조건 문제에서 QR 이나 SVD 가 훨씬 정확하다. R0 의 첫 레슨이 이것을 수치로 확인한다."
    concept: { front: "정규방정식의 수치적 약점", back: "조건수가 제곱된다($\\kappa(A^\\top A)=\\kappa(A)^2$) — 악조건에서는 QR/SVD 를 쓴다" }
```

## 학습 경로

**1순위 자료**: [MIT 18.06 Linear Algebra (Spring 2010, Strang)](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/).
강의 영상 + 문제집·해답 + 기출 시험·해답이 모두 공개된다.

| 단계 | 18.06 범위 | 무엇을 할 수 있게 되는가 | 예상 |
|---|---|---|---|
| 1 | 소거법과 $Ax=b$ (L1–L8) | LU 분해, 전치·역행렬, 해의 존재·유일성 | 20시간 |
| 2 | 벡터공간과 네 부분공간 (L9–L14) | 랭크, 기저와 차원, 랭크-영도 정리 | 18시간 |
| 3 | 직교성과 최소제곱 (L15–L17) | 직교 투영, 정규방정식, Gram–Schmidt·QR | 15시간 |
| 4 | 행렬식과 고윳값 (L18–L26) | 고윳값·고유벡터, 대각화, 대칭행렬과 양정성 | 20시간 |
| 5 | SVD 와 응용 (L29–L33) | SVD, 유사역행렬, 조건수, 주성분 | 7시간 |

합계 약 80시간. **4·5단계를 건너뛰지 말라** — 고윳값과 SVD 가 로보틱스에서 가장 많이 쓰인다.

## 이 단계 공부법

1. **진단을 먼저 (40분)** — 5/6 이상이면 끝이다. 틀린 문항이 어느 단계인지 보고 거기서 시작한다.
2. **Strang 의 강의는 "왜"를 말한다 (매일 2–3시간)** — 공식 암기가 아니라 기하적 의미를 잡는
   강의다. 영상 1개 + 해당 문제집 묶음으로 진행한다.
3. **손계산 → numpy 검산 (단계마다 1시간)** — 작은 행렬을 손으로 풀고 `numpy.linalg` 로 같은
   답이 나오는지 본다. 이 습관이 재현 과제의 기본기다.
4. **네 부분공간 그림을 한 장으로 그려 둔다 (1시간)** — 2단계 끝에서 열공간·영공간·행공간·
   좌영공간의 차원 관계를 한 장에 정리한다. 이 그림이 뒤의 게이지 자유도와 랭크 부족 진단에서
   그대로 쓰인다.
5. **SVD 는 코드로 감을 잡는다 (2시간)** — 무작위 행렬의 특이값을 출력하고, 열을 하나 거의
   선형종속으로 만들었을 때 최소 특이값이 0 으로 가는 것을 본다. 조건수가 "무엇을 재는 수"인지가
   이때 감각으로 들어온다.
6. **기출 시험으로 판정한다** — 18.06 의 기출 3회를 시간 재고 풀어 80% 이상.

**통과 기준**: 진단 6문항 중 5개 이상, 18.06 기출 기말 80% 이상 자기 채점, 그리고 SVD 로
랭크·조건수를 계산하는 numpy 코드를 스스로 쓸 수 있다.
