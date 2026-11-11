---
id: m1-rotation-representations
title: 회전 표현 (오일러 각 / 쿼터니언)
summary: 3차원 회전을 회전 행렬, 오일러 각, 쿼터니언으로 표현하고 서로 변환한다.
objectives:
  - 회전 행렬의 성질(직교, 행렬식 1)을 설명할 수 있다.
  - 오일러 각의 짐벌 락 문제를 설명할 수 있다.
  - 쿼터니언과 회전 행렬을 서로 변환할 수 있다.
prerequisites: [m1-vectors-matrices]
difficulty: 2
estimated_minutes: 90
tags: [math, rotation, quaternion]
activities:
  - id: m1-rotation-representations-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 40
  - id: m1-rotation-representations-quiz
    kind: quiz
    title: 회전 표현 변환 퀴즈
    estimated_minutes: 15
  - id: m1-rotation-representations-exercise
    kind: exercise
    title: scipy.spatial.transform으로 변환 왕복 확인
    estimated_minutes: 35
resources:
  - title: Modern Robotics (Lynch & Park)
    kind: book
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    note: Ch. 3.2 회전과 각속도, Appendix B
  - title: Visualizing quaternions (3Blue1Brown & Ben Eater)
    kind: video
    url: https://eater.net/quaternions
  - title: scipy.spatial.transform.Rotation 문서
    kind: article
    url: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html
---

# 회전 표현

> 이 레슨은 자리표시자(placeholder)입니다. 콘텐츠 작성자가 본문을 채웁니다.

## 회전 행렬

$SO(3)$ 의 원소인 $3\times3$ 직교 행렬. 합성이 쉽고 모호함이 없지만 9개 숫자로
3자유도를 표현하므로 중복이 크다.

## 오일러 각

세 축 회전의 순서(ZYX 등)에 따라 의미가 달라지며, 특정 자세에서 자유도가 하나
사라지는 짐벌 락이 발생한다.

## 쿼터니언

단위 쿼터니언 $q = (w, x, y, z)$ 는 짐벌 락이 없고 보간(SLERP)에 유리하다.
로봇 미들웨어(ROS 2)의 기본 자세 표현이다.
