---
id: m1-vectors-matrices
title: 벡터·행렬
summary: 로봇의 위치·자세·속도를 표현하는 기본 도구인 벡터와 행렬 연산을 로보틱스 관점에서 복습한다.
objectives:
  - 벡터의 내적·외적을 계산하고 기하학적 의미(각도, 투영, 수직 벡터)를 설명할 수 있다.
  - 행렬 곱을 선형 변환의 합성으로 해석하고, 곱의 순서가 중요한 이유를 설명할 수 있다.
  - 역행렬·전치·행렬식을 손과 NumPy로 계산할 수 있다.
prerequisites: []
difficulty: 1
estimated_minutes: 60
tags: [math, linear-algebra, numpy]
activities:
  - id: m1-vectors-matrices-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 25
  - id: m1-vectors-matrices-quiz
    kind: quiz
    title: 내적·외적·행렬 곱 확인 퀴즈
    estimated_minutes: 10
  - id: m1-vectors-matrices-exercise
    kind: exercise
    title: NumPy로 2D 선형 변환 그려 보기
    estimated_minutes: 25
resources:
  - title: "3Blue1Brown, Essence of Linear Algebra"
    url: https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab
    kind: video
    note: 벡터·선형 변환·행렬 곱·외적 편. 직관을 먼저 잡는다.
  - title: "Modern Robotics (Lynch & Park) 위키 — Linear Algebra Review"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: 무료 프리프린트와 선형대수 복습 자료.
  - title: "MIT 18.06SC Linear Algebra (Gilbert Strang)"
    url: https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/
    kind: course
    note: 행렬식·역행렬 보강용(선택).
---

# 벡터·행렬

로봇의 관절 각도, 말단(end-effector) 위치, 바퀴 속도, 센서 측정값은 모두 벡터로
표현되고, 좌표계 사이의 관계는 행렬로 표현된다. 이후 레슨(회전 표현, 좌표 변환,
운동학, 제어)은 이 레슨의 표기법을 그대로 사용하므로, 계산 자체보다 **기하학적
의미**를 붙잡는 데 집중하자.

## 개념

### 벡터

벡터는 크기와 방향을 가진 양이다. 이 커리큘럼에서는 열벡터
$\mathbf{a} = [a_x, a_y, a_z]^T$ 를 기본으로 쓴다. 같은 화살표라도 **어느 좌표계에서
성분을 읽었는지**에 따라 숫자가 달라진다는 점을 기억하자. 이것이 다음 레슨들의 핵심
주제다.

- **내적(dot product)** 은 스칼라를 돌려준다. 두 벡터 사이 각도를 구하거나, 한 벡터를
  다른 방향으로 투영할 때 쓴다. 내적이 0이면 두 벡터는 수직이다.
- **외적(cross product)** 은 3차원에서만 정의되며, 두 벡터에 모두 수직인 벡터를
  돌려준다. 방향은 오른손 법칙을 따르고, 크기는 두 벡터가 만드는 평행사변형의 넓이다.
  로봇에서는 회전축, 토크 $\boldsymbol{\tau} = \mathbf{r} \times \mathbf{f}$,
  회전하는 강체 위 점의 속도 $\mathbf{v} = \boldsymbol{\omega} \times \mathbf{r}$ 에 등장한다.

### 행렬 = 선형 변환

행렬 $A$ 는 벡터를 다른 벡터로 보내는 선형 변환이다. $A$ 의 각 열은 기저 벡터
$\mathbf{e}_1, \mathbf{e}_2, \dots$ 가 변환 후 도착하는 위치다. 이 관점 하나로 회전
행렬을 "새 좌표축을 열로 나열한 것"으로 읽을 수 있게 된다.

행렬 곱 $AB$ 는 "먼저 $B$, 그다음 $A$" 를 적용하는 변환의 합성이다. 일반적으로
$AB \neq BA$ 이며, 로봇에서 "먼저 회전하고 이동" 과 "먼저 이동하고 회전" 이 다른 결과를
주는 이유가 바로 이것이다.

### 역행렬, 전치, 행렬식

- 역행렬 $A^{-1}$ 은 변환을 되돌린다. 행렬식 $\det A = 0$ 이면 역행렬이 없다(어떤 방향의
  정보가 사라졌다는 뜻). 이는 M2 역기구학의 **특이점(singularity)** 과 연결된다.
- 회전 행렬 $R$ 은 특별해서 $R^{-1} = R^T$, $\det R = 1$ 이다. 역행렬 계산이 전치로
  끝나므로 로봇 소프트웨어에서 매우 자주 활용된다.

## 핵심 수식

$$\mathbf{a}\cdot\mathbf{b} = \mathbf{a}^T\mathbf{b} = |\mathbf{a}||\mathbf{b}|\cos\theta$$

$$\mathbf{a}\times\mathbf{b} = [\mathbf{a}]_\times \mathbf{b}, \quad
[\mathbf{a}]_\times = \begin{bmatrix} 0 & -a_z & a_y \\ a_z & 0 & -a_x \\ -a_y & a_x & 0 \end{bmatrix}$$

$$(AB)^T = B^T A^T, \qquad (AB)^{-1} = B^{-1} A^{-1}$$

2차원 회전 행렬:

$$R(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}$$

$[\mathbf{a}]_\times$ (skew-symmetric 행렬) 는 외적을 행렬 곱으로 바꿔 준다. Modern
Robotics 3장에서 각속도를 다룰 때 다시 등장하니 지금 익숙해져 두자.

## 예제

정사각형의 꼭짓점을 30° 회전한 뒤 x 방향으로 2배 늘려 보고, 순서를 바꾸면 결과가
달라지는지 확인한다.

```python
import numpy as np

th = np.deg2rad(30)
R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
S = np.diag([2.0, 1.0])

square = np.array([[0, 1, 1, 0], [0, 0, 1, 1]], dtype=float)  # 각 열이 한 점

a = S @ R @ square  # 회전 후 스케일
b = R @ S @ square  # 스케일 후 회전
print(np.allclose(a, b))  # False: 순서가 중요하다
print(np.allclose(R.T @ R, np.eye(2)))  # True: R^T = R^{-1}
print(np.linalg.det(R))  # 1.0

u, v = np.array([1, 0, 0]), np.array([0, 1, 0])
print(np.dot(u, v), np.cross(u, v))  # 0, [0 0 1]
```

**연습 과제(exercise):** 위 코드에 `matplotlib`으로 원래 사각형과 `a`, `b` 를 함께
그려 차이를 눈으로 확인하라. 이어서 $\det S$ 와 변환 후 넓이의 관계를 설명해 보라.

## 자가 점검 질문

1. 두 벡터의 내적이 음수라면 두 벡터 사이 각도에 대해 무엇을 알 수 있는가?
2. 행렬 $A$ 의 첫 번째 열은 기하학적으로 무엇을 의미하는가?
3. 회전 행렬의 역행렬을 전치로 계산할 수 있는 이유는 무엇이며, 일반 행렬에서는 왜 안 되는가?

## 이 단계 공부법

1. **영상(약 1.5시간):** 3Blue1Brown *Essence of Linear Algebra* 에서 벡터, 선형 결합, 선형 변환, 행렬 곱, 3차원 변환, 외적 편을 먼저 본다. 계산보다 "행렬 = 공간 변환" 직관을 잡는 것이 목표다.
2. **본문:** 이 레슨의 개념·핵심 수식을 읽고 예제 코드를 직접 실행한다.
3. **교재:** Modern Robotics 위키의 "Linear Algebra Review" 를 훑어보며 모르는 용어(행렬식, 고유값)만 표시한다.
4. **문제:** 확인 퀴즈 → 연습 과제(사각형 변환 그리기) 순으로 푼다.
5. **보강(선택):** 행렬식·역행렬이 약하다면 MIT 18.06SC 의 해당 강의와 문제 풀이 영상으로 보강한다.

## 참고 자료

- Kevin M. Lynch, Frank C. Park, *Modern Robotics: Mechanics, Planning, and Control*,
  Cambridge University Press, 2017 — 무료 프리프린트, 선형대수 복습 페이지, 강의 영상:
  <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- 3Blue1Brown, *Essence of Linear Algebra* (YouTube 시리즈) —
  <https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab>
- Gilbert Strang, MIT 18.06SC Linear Algebra (MIT OpenCourseWare) —
  <https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/>
