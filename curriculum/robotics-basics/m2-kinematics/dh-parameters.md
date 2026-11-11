---
id: m2-dh-parameters
title: DH 파라미터
summary: Denavit–Hartenberg 규약으로 링크와 관절을 네 개의 파라미터로 기술한다.
objectives:
  - 링크 길이, 링크 비틀림, 링크 오프셋, 관절 각의 의미를 설명할 수 있다.
  - 2-link 평면 매니퓰레이터의 DH 테이블을 작성할 수 있다.
  - DH 파라미터로부터 동차 변환 행렬을 구성할 수 있다.
prerequisites: [m1-vectors-matrices]
difficulty: 3
estimated_minutes: 90
tags: [kinematics, manipulator, dh]
activities:
  - id: m2-dh-parameters-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 40
  - id: m2-dh-parameters-exercise
    kind: exercise
    title: 2-link 매니퓰레이터 DH 테이블 작성
    estimated_minutes: 20
---

# DH 파라미터

> 이 레슨은 자리표시자(placeholder)입니다. 콘텐츠 작성자가 본문을 채웁니다.

## 규약

인접한 두 관절 축 사이의 관계를 $(a_i, \alpha_i, d_i, \theta_i)$ 네 값으로 기술한다.
각 링크의 변환은 $z$ 축 회전·이동과 $x$ 축 회전·이동의 곱으로 표현된다.

## 2-link 예제

평면 2-link 팔의 DH 테이블을 작성하고, 두 변환 행렬을 곱해 말단 위치를 구한다.
이 결과는 M2의 다음 레슨(정기구학)과 Webots 실습에서 그대로 사용한다.
