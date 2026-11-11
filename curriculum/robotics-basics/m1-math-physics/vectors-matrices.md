---
id: m1-vectors-matrices
title: 벡터·행렬
summary: 로봇의 위치와 자세를 표현하는 기본 도구인 벡터와 행렬 연산을 복습한다.
objectives:
  - 벡터의 내적·외적을 계산하고 기하학적 의미를 설명할 수 있다.
  - 행렬 곱과 역행렬을 손과 NumPy로 계산할 수 있다.
  - 선형 변환을 행렬로 표현할 수 있다.
prerequisites: []
difficulty: 1
estimated_minutes: 60
tags: [math, linear-algebra]
activities:
  - id: m1-vectors-matrices-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 30
  - id: m1-vectors-matrices-quiz
    kind: quiz
    title: 내적·외적·행렬 곱 확인 퀴즈
    estimated_minutes: 10
  - id: m1-vectors-matrices-exercise
    kind: exercise
    title: NumPy로 2D 선형 변환 그려 보기
    estimated_minutes: 20
resources:
  - title: Introduction to Linear Algebra (Gilbert Strang)
    kind: book
    url: https://math.mit.edu/~gs/linearalgebra/
    note: Ch. 1-2
  - title: MIT OCW 18.06 Linear Algebra
    kind: course
    url: https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/
    note: Lec. 1-4
  - title: Essence of Linear Algebra (3Blue1Brown)
    kind: video
    url: https://www.3blue1brown.com/topics/linear-algebra
    note: Ch. 1-5, 직관 잡기용
---

# 벡터·행렬

> 이 레슨은 자리표시자(placeholder)입니다. 콘텐츠 작성자가 본문을 채웁니다.

## 왜 필요한가

로봇의 관절 각도, 말단 위치, 센서 측정값은 모두 벡터로 표현되고, 좌표계 사이의
관계는 행렬로 표현된다. 이후 모듈(운동학, 제어)은 이 표기법을 전제로 한다.

## 핵심 개념

- 벡터: 크기와 방향. 내적 $\mathbf{a} \cdot \mathbf{b} = |\mathbf{a}||\mathbf{b}|\cos\theta$,
  외적은 두 벡터에 수직인 벡터를 만든다.
- 행렬: 선형 변환. 행렬 곱은 변환의 합성이며 교환법칙이 성립하지 않는다.
- 역행렬과 전치: 회전 행렬은 $R^{-1} = R^{T}$ 라는 성질이 있다.

## 연습

NumPy로 2D 점 집합에 회전·스케일 행렬을 곱해 결과를 그려 본다.
