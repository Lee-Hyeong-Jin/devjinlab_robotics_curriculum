---
id: m1-coordinate-transforms
title: 좌표 변환 (동차 변환 행렬)
summary: 회전과 평행 이동을 4×4 동차 변환 행렬 하나로 묶고, 변환의 합성·역변환으로 좌표계 사이를 오가는 법을 익힌다.
objectives:
  - 회전 행렬과 위치 벡터로 동차 변환 행렬을 구성할 수 있다.
  - 좌표계 표기(T_ab 등)를 읽고 변환을 올바른 순서로 합성·역변환할 수 있다.
  - 센서 좌표계에서 측정한 점을 로봇·월드 좌표계로 변환하는 코드를 작성할 수 있다.
prerequisites: [m1-rotation-representations]
difficulty: 2
estimated_minutes: 80
tags: [math, transforms, homogeneous-coordinates, tf]
activities:
  - id: m1-coordinate-transforms-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 30
  - id: m1-coordinate-transforms-quiz
    kind: quiz
    title: 변환 합성 순서 퀴즈
    estimated_minutes: 15
  - id: m1-coordinate-transforms-exercise
    kind: exercise
    title: 센서 → 로봇 → 월드 좌표 변환 시각화 스크립트
    estimated_minutes: 35
resources:
  - title: "Cyrill Stachniss, Homogeneous Coordinates"
    url: https://www.youtube.com/watch?v=MQdm0Z_gNcw
    kind: video
    note: 동차 좌표 직관. 먼저 본다.
  - title: "Modern Robotics, 3.3절 동차 변환 행렬 (Lynch & Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: T_ab 표기와 합성·역변환 규칙. 3장 연습문제 일부를 푼다.
  - title: "Introduction to Robotics: Mechanics and Control, 4th ed. (John J. Craig)"
    kind: book
    note: 2장 Spatial Descriptions and Transformations (대안 교재).
---

# 좌표 변환

로봇에는 좌표계가 많다. 월드(맵), 로봇 몸체, 각 관절, 카메라·라이다 같은 센서가 저마다
좌표계를 가진다. 카메라가 "앞쪽 1 m 에 물체가 있다"고 말해도, 팔이 그 물체를 잡으려면
그 점을 팔의 기준 좌표계로 옮겨야 한다. 이 레슨은 M2 운동학(DH 파라미터, 정기구학)과
M3 이동 로봇 자세 추정의 공통 기반이다.

## 개념

### 자세(pose) = 회전 + 위치

좌표계 $\{b\}$ 의 자세를 좌표계 $\{a\}$ 에서 기술하려면 두 가지가 필요하다.

- $R_{ab}$: $\{b\}$ 의 축들을 $\{a\}$ 에서 본 회전 행렬
- $\mathbf{p}_{ab}$: $\{b\}$ 의 원점을 $\{a\}$ 에서 본 위치

이 둘을 $4\times4$ **동차 변환 행렬(homogeneous transformation matrix)** $T_{ab}$ 하나로
묶으면, 회전과 이동을 행렬 곱 한 번으로 처리할 수 있다. 이런 행렬의 집합을 $SE(3)$
라고 한다.

### 동차 좌표

3차원 점 $\mathbf{p}$ 에 1 을 덧붙여 $[\mathbf{p}; 1]$ 로 쓰면 이동까지 선형 연산처럼
다룰 수 있다. 방향 벡터(속도, 축 방향)는 이동의 영향을 받지 않아야 하므로 마지막
성분을 0 으로 둔다.

### 표기법과 합성 규칙

이 커리큘럼은 Modern Robotics 의 표기를 따른다. $T_{ab}$ 는 "$\{a\}$ 에서 본 $\{b\}$"
이고, $\{b\}$ 에서 표현된 점 $\mathbf{p}_b$ 를 $\{a\}$ 로 옮기면
$\mathbf{p}_a = T_{ab}\,\mathbf{p}_b$ 이다. 아래첨자가 "상쇄"되도록 곱하면 된다:
$T_{ac} = T_{ab}T_{bc}$. 이 규칙만 지키면 곱의 순서를 헷갈릴 일이 거의 없다.

### 두 가지 해석

같은 행렬 $T$ 를 (1) 한 좌표계를 다른 좌표계에서 본 **자세**로, (2) 점이나 좌표계를
**움직이는 연산자**로 해석할 수 있다. 또한 변환을 **왼쪽에 곱하면 고정(월드) 좌표계
기준**, **오른쪽에 곱하면 현재(몸체) 좌표계 기준**으로 움직인다. ROS 2 의 `tf2` 는 이런
좌표계 트리를 관리하는 라이브러리로, M8(ROS 2·도구)에서 다시 만난다.

## 핵심 수식

$$T_{ab} = \begin{bmatrix} R_{ab} & \mathbf{p}_{ab} \\ \mathbf{0}^T & 1 \end{bmatrix}, \qquad
\begin{bmatrix}\mathbf{p}_a\\1\end{bmatrix} = T_{ab}\begin{bmatrix}\mathbf{p}_b\\1\end{bmatrix}
\;\Leftrightarrow\; \mathbf{p}_a = R_{ab}\mathbf{p}_b + \mathbf{p}_{ab}$$

합성과 역변환:

$$T_{ac} = T_{ab}\,T_{bc}, \qquad
T_{ab}^{-1} = T_{ba} = \begin{bmatrix} R_{ab}^T & -R_{ab}^T\mathbf{p}_{ab} \\ \mathbf{0}^T & 1 \end{bmatrix}$$

역변환은 일반 역행렬 계산 없이 전치만으로 구할 수 있다. 평면(2D) 로봇이라면 같은 구조의
$3\times3$ 행렬 $\begin{bmatrix} R(\theta) & \mathbf{p} \\ \mathbf{0}^T & 1\end{bmatrix}$ 를 쓴다.

## 예제

이동 로봇이 월드 좌표 $(2, 1)$ 에서 $90^\circ$ 방향을 보고 있다. 로봇 중심에서 앞으로
$0.1$ m 떨어진 곳에 거리 센서가 달려 있고, 센서가 정면 $0.5$ m 거리에 장애물을 측정했다.
장애물의 월드 좌표는?

- $T_{wr}$: $R(90^\circ)$, $\mathbf{p} = (2, 1)$
- $T_{rs}$: $R(0)$, $\mathbf{p} = (0.1, 0)$
- $\mathbf{p}_s = (0.5, 0)$

$T_{ws} = T_{wr}T_{rs}$ 이므로 센서는 월드에서 $(2, 1.1)$, 장애물은 $(2, 1.6)$ 이다.

```python
import numpy as np


def se2(theta, x, y):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, x], [s, c, y], [0, 0, 1.0]])


def inv_se2(T):
    R, p = T[:2, :2], T[:2, 2]
    Ti = np.eye(3)
    Ti[:2, :2], Ti[:2, 2] = R.T, -R.T @ p
    return Ti


T_wr = se2(np.pi / 2, 2.0, 1.0)
T_rs = se2(0.0, 0.1, 0.0)
p_s = np.array([0.5, 0.0, 1.0])

p_w = T_wr @ T_rs @ p_s
print(p_w[:2].round(3))  # [2.  1.6]
print(np.allclose(inv_se2(T_wr) @ T_wr, np.eye(3)))  # True
```

**연습 과제(exercise, 부록 A "좌표 변환 시각화 스크립트"):** `matplotlib`으로 월드·로봇·센서
좌표계의 축을 화살표로 그리고, 로봇 각도를 바꿔 가며 장애물의 월드 좌표가 어떻게
움직이는지 그려라. 이어서 `inv_se2` 를 이용해 월드 좌표의 목표점을 로봇 좌표로 바꿔
보라(M3 경로 추종에서 그대로 쓴다).

## 자가 점검 질문

1. $T_{ab}$ 와 $T_{ba}$ 의 관계는 무엇이며, $T_{ba}$ 의 위치 성분이 $-\mathbf{p}_{ab}$ 가 아닌 이유는?
2. 같은 변환 $T$ 를 현재 자세 $T_{sb}$ 의 왼쪽에 곱할 때와 오른쪽에 곱할 때 의미가 어떻게 다른가?
3. 방향 벡터를 동차 좌표로 쓸 때 마지막 성분을 0 으로 두는 이유는 무엇인가?

## 이 단계 공부법

1. **영상:** Cyrill Stachniss 의 "Homogeneous Coordinates" 강의로 동차 좌표의 직관을 잡고, 이어서 Modern Robotics 강의 영상 3장의 동차 변환 행렬 부분을 본다.
2. **교재:** Modern Robotics 3.3절(동차 변환 행렬)을 읽는다. Craig 2장을 읽어도 같은 내용을 다른 표기로 확인할 수 있다.
3. **본문 + 예제:** 이 레슨의 장애물 예제를 손으로 먼저 계산한 뒤 코드로 확인한다.
4. **문제:** 확인 퀴즈 → 연습 과제(좌표 변환 시각화 스크립트) 순으로 푼다. Modern Robotics 3장 연습문제 중 변환 합성·역변환 문제를 2~3개 추가로 풀어 본다.
5. **점검:** 자가 점검 질문 2번(왼쪽/오른쪽 곱)에 막힘없이 답할 수 있으면 M2 로 넘어간다.

## 참고 자료

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, 3.3절 "Rigid-Body Motions and Twists" —
  <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- John J. Craig, *Introduction to Robotics: Mechanics and Control*, 4th ed., Pearson —
  2장 "Spatial Descriptions and Transformations".
- Peter Corke, *Robotics, Vision and Control: Fundamental Algorithms in Python*, 3rd ed.,
  Springer, 2023 — 2장.
- Cyrill Stachniss, "Homogeneous Coordinates" 강의 (YouTube) —
  <https://www.youtube.com/watch?v=MQdm0Z_gNcw>
