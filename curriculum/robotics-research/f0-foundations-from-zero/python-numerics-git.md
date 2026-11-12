---
id: f0-python-numerics-git
title: 파이썬·수치계산·Git
summary: >-
  numpy 로 배열 연산과 브로드캐스팅을 쓰고, 부동소수점 오차와 조건수를 인식하고, Git 으로 작업을
  관리하는 수준까지 올린다. 공개 문서·무료 교재로 안내하는 가이드형 레슨이다.
objectives:
  - numpy 배열 연산·브로드캐스팅·슬라이싱을 쓰고 루프 대신 벡터화할 수 있다.
  - 부동소수점의 한계(기계 정밀도, 상쇄, 누적 오차)를 인식하고 검증 테스트를 쓸 수 있다.
  - 유한차분으로 도함수·야코비안을 검산하고 스텝 크기를 근거 있게 고를 수 있다.
  - scipy 로 선형계·최소제곱·ODE 를 풀고 결과를 검증할 수 있다.
  - Git 으로 브랜치·커밋·diff 를 다루고 작업을 안전하게 되돌릴 수 있다.
prerequisites: [f0-linear-algebra]
difficulty: 1
estimated_minutes: 2400
tags: [foundations, python, numpy, git, guide]
activities:
  - id: f0-python-numerics-git-diagnostic
    kind: quiz
    title: 시작 전 자가 진단 (통과하면 이 레슨을 건너뛴다)
    estimated_minutes: 30
  - id: f0-python-numerics-git-reading
    kind: reading
    title: NumPy 사용자 가이드·Scientific Python Lectures·Pro Git 읽기
    estimated_minutes: 1100
  - id: f0-python-numerics-git-exercise
    kind: exercise
    title: 수치 검증 연습 (유한차분·조건수·누적 오차) + Git 실습
    estimated_minutes: 1270
resources:
  - title: "NumPy user guide"
    url: https://numpy.org/doc/stable/user/
    kind: notes
    note: 1순위. 배열 생성·인덱싱·브로드캐스팅·dtype·ufunc·복사와 뷰. 처음부터 끝까지 읽는다.
  - title: "Scientific Python Lectures"
    url: https://lectures.scientific-python.org/
    kind: course
    note: 1순위. 파이썬·numpy·matplotlib·scipy·수치 최적화·디버깅·성능. 무료 공개.
  - title: "Pro Git (2nd edition, 무료 전문)"
    url: https://git-scm.com/book/en/v2
    kind: book
    note: 1순위. 1-3장과 7장. CC BY-NC-SA 로 전문 공개(PDF·EPUB 포함).
  - title: "SciPy linalg / optimize 문서"
    url: https://docs.scipy.org/doc/scipy/reference/index.html
    kind: notes
    note: solve, lstsq, svd, least_squares, solve_ivp 를 익혀 둔다.
---

# 파이썬·수치계산·Git

## 도달 목표

이 레슨은 **가이드형**이다. 통과하면 건너뛴다.

연구 트랙의 모든 레슨은 **재현 과제**를 갖고, 그 수용 기준은 "수치로 판정 가능한 조건"이다.
즉 이 레슨은 선택이 아니다 — numpy 로 검산하지 못하면 어느 레슨도 통과할 수 없다. 특히
**유한차분으로 해석적 미분을 검증하는 동작**은 C1 부터 S5 까지 거의 모든 재현 과제에 나온다.

통과 기준은 §시작 전 자가 진단의 6문항 중 5문항 이상이다.

## 시작 전 자가 진단

`rc quiz f0-python-numerics-git` 로 푼다. 5/6 이상이면 건너뛰고 `f0-classical-mechanics` 로 간다.

```quiz
activity: f0-python-numerics-git-diagnostic
questions:
  - id: q1
    type: single
    prompt: "`a` 가 `(3, 1)`, `b` 가 `(1, 4)` 모양일 때 `a + b` 의 모양은?"
    choices: ["(3, 1)", "(1, 4)", "(3, 4)", "오류가 난다"]
    answer: 2
    explanation: "브로드캐스팅으로 양쪽의 1 차원이 늘어나 `(3, 4)` 가 된다. 이 규칙을 모르면 의도하지 않은 큰 배열이 조용히 만들어져 메모리와 결과가 둘 다 틀린다."
    concept: { front: "numpy 브로드캐스팅", back: "크기 1 인 축이 상대 축의 크기로 늘어난다. `(3,1)+(1,4)` → `(3,4)`" }
  - id: q2
    type: short
    prompt: "배정밀도 부동소수점의 기계 정밀도(machine epsilon)는 약 $2.2 \\times 10^{-k}$ 다. $k$ 는?"
    answer: ["16", "-16", "16자리"]
    explanation: "$\\epsilon \\approx 2.22\\times10^{-16}$ (`np.finfo(float).eps`). 유효숫자 약 16자리이고, 이 값이 유한차분 스텝 크기와 수렴 허용오차의 하한을 정한다."
    concept: { front: "배정밀도 기계 정밀도", back: "$\\approx 2.2\\times10^{-16}$. 유효숫자 약 16자리 — 허용오차를 이보다 작게 요구하면 안 된다" }
  - id: q3
    type: single
    prompt: "중심 유한차분 $\\frac{f(x+h)-f(x-h)}{2h}$ 에서 전체 오차를 최소화하는 $h$ 의 대략적 크기는?"
    choices:
      - "$h \\sim \\epsilon$ (기계 정밀도)"
      - "$h \\sim \\epsilon^{1/2}$"
      - "$h \\sim \\epsilon^{1/3} \\approx 6\\times10^{-6}$"
      - "가능한 한 작게"
    answer: 2
    explanation: "절단 오차는 $O(h^2)$, 반올림 오차는 $O(\\epsilon/h)$ 이므로 합을 최소화하면 $h \\sim \\epsilon^{1/3}$ 이다. 무작정 작게 하면 반올림 오차가 지배한다 — 연구 트랙의 모든 야코비안 검증이 이 선택을 요구한다."
    concept: { front: "중심 차분의 최적 스텝 크기", back: "$h \\sim \\epsilon^{1/3} \\approx 6\\times10^{-6}$ (절단 $O(h^2)$ 와 반올림 $O(\\epsilon/h)$ 의 균형)" }
  - id: q4
    type: single
    prompt: "최소제곱 $\\min\\lVert Ax-b\\rVert$ 를 numpy 로 풀 때 가장 안전한 방법은?"
    choices:
      - "`np.linalg.inv(A.T @ A) @ A.T @ b`"
      - "`np.linalg.solve(A.T @ A, A.T @ b)`"
      - "`np.linalg.lstsq(A, b)`"
      - "세 방법이 모두 동등하다"
    answer: 2
    explanation: "`lstsq` 는 QR/SVD 기반이라 조건수를 제곱하지 않는다. 정규방정식을 직접 세우는 앞의 두 방법은 $\\kappa(A)^2$ 를 겪고, 특히 `inv` 를 쓰는 첫 방법이 가장 나쁘다."
    concept: { front: "최소제곱의 안전한 수치 해법", back: "`lstsq`(QR/SVD). 정규방정식은 조건수를 제곱하고 `inv` 는 더 나쁘다" }
  - id: q5
    type: truefalse
    prompt: "`a = b[:, 0]` 로 얻은 배열을 수정하면 원본 `b` 도 바뀔 수 있다."
    answer: true
    explanation: "기본 슬라이싱은 **뷰(view)** 를 돌려주므로 원본이 바뀐다. 복사가 필요하면 `.copy()` 를 쓴다. 이 구분을 모르면 반복 중에 상태가 조용히 오염된다."
    concept: { front: "numpy 뷰와 복사", back: "기본 슬라이싱은 뷰 — 수정하면 원본이 바뀐다. 독립 배열이 필요하면 `.copy()`" }
  - id: q6
    type: short
    prompt: "직전 커밋을 유지하면서 작업 트리의 변경만 되돌리는 Git 명령은? (파일 하나 `f.py` 기준)"
    answer: ["git restore f.py", "git checkout -- f.py", "git restore", "git checkout f.py"]
    explanation: "`git restore f.py`(구버전은 `git checkout -- f.py`)가 작업 트리를 HEAD 상태로 되돌린다. 이 저장소는 히스토리·작업을 파괴하는 되돌리기 명령(`git reset --hard`, 태그 없는 `git stash`, 강제 push)을 훅으로 금지하고 WIP 커밋을 쓰도록 규정한다."
    concept: { front: "작업 트리 변경 되돌리기", back: "`git restore <file>`. 파괴적 명령보다 WIP 커밋이 안전하다" }
```

## 학습 경로

| 단계 | 자료 | 무엇을 할 수 있게 되는가 | 예상 |
|---|---|---|---|
| 1 | [Scientific Python Lectures](https://lectures.scientific-python.org/) 의 Python·NumPy 장 | 배열 생성·인덱싱·브로드캐스팅, 벡터화, matplotlib | 12시간 |
| 2 | [NumPy user guide](https://numpy.org/doc/stable/user/) 전체 | dtype, 복사와 뷰, ufunc, 고급 인덱싱 | 8시간 |
| 3 | Scientific Python Lectures 의 SciPy·최적화·디버깅 장 | solve/lstsq/svd, least_squares, solve_ivp, 프로파일링 | 10시간 |
| 4 | [Pro Git](https://git-scm.com/book/en/v2) 1–3장, 7장 | 커밋·브랜치·diff·되돌리기, rebase 의 뜻 | 6시간 |
| 5 | 자체 연습 (아래 §공부법 3) | 유한차분 검증, 조건수 실험, 누적 오차 추적 | 4시간 |

합계 약 40시간. 다른 F0 레슨보다 짧지만 **가장 자주 쓰인다.**

## 이 단계 공부법

1. **진단을 먼저 (30분)** — 5/6 이상이면 끝이다.
2. **읽기만 하지 말고 즉시 쳐 본다** — numpy 문서는 읽어서 외워지지 않는다. 브로드캐스팅은
   모양을 바꿔 가며 직접 더해 보는 것이 유일한 방법이다.
3. **세 가지 수치 실험을 직접 한다 (4시간)** — 연구 트랙에서 계속 쓰는 동작이다:
   ① $f(x)=x^\top Mx$ 의 기울기를 해석적으로 구하고 중심 차분과 비교, 스텝 $h$ 를
   $10^{-1}$ 부터 $10^{-12}$ 까지 쓸며 **오차의 V 곡선**을 그린다(최저점이 $\epsilon^{1/3}$ 근방).
   ② 조건수를 키운 행렬에서 `lstsq` 와 정규방정식의 오차를 비교한다.
   ③ 회전행렬을 $10^5$ 번 곱해 $\lVert R^\top R - I\rVert$ 가 커지는 것을 보고 SVD 로 재투영한다.
4. **Git 은 되돌리기부터 익힌다 (2시간)** — 이 저장소는 파괴적 되돌리기 명령을 훅으로 막고 WIP
   커밋을 쓴다. 위험한 명령을 외우기 전에 **안전한 되돌리기**(`git restore`, WIP 커밋)를 익힌다.
5. **코드에 테스트를 붙인다 (2시간)** — 재현 과제의 수용 기준은 결국 assert 다.
   `assert np.allclose(a, b, atol=1e-9)` 꼴로 쓰는 습관을 들인다.
6. **벡터화로 다시 쓴다 (2시간)** — 루프로 쓴 코드를 배열 연산으로 바꿔 시간을 측정한다.
   연구 트랙의 재현 과제는 $10^4$–$10^5$ 표본을 요구하므로 벡터화가 필요하다.

**통과 기준**: 진단 5/6 이상, 그리고 §공부법 3 의 세 실험을 모두 수행해 V 곡선·조건수 비교·
재투영 결과를 그림으로 갖고 있다.
