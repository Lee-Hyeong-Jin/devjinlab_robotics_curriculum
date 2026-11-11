---
id: m2-forward-kinematics
title: 정기구학 (Forward Kinematics)
summary: 관절 값이 주어졌을 때 링크 변환을 차례로 곱해 말단의 위치와 자세를 구하고, 작업 공간을 해석한다.
objectives:
  - DH 링크 변환을 곱해 임의의 직렬 매니퓰레이터의 정기구학을 계산할 수 있다.
  - 2-link 평면 팔의 말단 위치를 닫힌 형태의 식으로 유도할 수 있다.
  - 관절 공간과 작업 공간을 구분하고 2-link 팔의 작업 공간을 설명할 수 있다.
prerequisites: [m2-dh-parameters]
difficulty: 3
estimated_minutes: 75
tags: [kinematics, manipulator, forward-kinematics]
activities:
  - id: m2-forward-kinematics-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 30
  - id: m2-forward-kinematics-quiz
    kind: quiz
    title: 정기구학 계산 퀴즈
    estimated_minutes: 15
  - id: m2-forward-kinematics-exercise
    kind: exercise
    title: 2-link / 3-link 팔 정기구학 함수 구현과 작업 공간 그리기
    estimated_minutes: 30
resources:
  - title: "Modern Robotics, 4장 Forward Kinematics (Lynch & Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: PoE 정기구학.
  - title: "Modern Robotics 강의 영상 (4장)"
    url: https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos
    kind: video
    note: 정기구학 영상.
  - title: "Robot Modeling and Control, 2nd ed. (Spong, Hutchinson, Vidyasagar)"
    kind: book
    note: 3장 DH 기반 정기구학 예제.
  - title: "ModernRobotics 공식 코드 라이브러리"
    url: https://github.com/NxRLab/ModernRobotics
    kind: other
    note: FKinSpace 로 결과 비교(선택).
---

# 정기구학

정기구학(forward kinematics, FK)은 "관절을 이렇게 돌리면 손끝이 어디로 가는가?" 에 답한다.
관절 값 $\boldsymbol{\theta} = (\theta_1, \dots, \theta_n)$ 에서 말단 자세 $T_{0n}$ 으로 가는 함수이며,
답이 항상 **하나**로 정해진다. 다음 레슨의 역기구학은 이 함수를 거꾸로 푸는 문제이고,
M3 이후 제어·계획 알고리즘도 FK 를 반복해서 호출한다.

## 개념

### 관절 공간과 작업 공간

- **관절 공간(joint space):** 관절 값들의 공간. $n$ 자유도 팔이면 $n$ 차원이다.
- **작업 공간(task space):** 말단의 위치·자세 공간. 평면이면 $(x, y, \phi)$, 3차원이면 $SE(3)$ 이다.

FK 는 관절 공간 → 작업 공간 사상이다. 말단이 도달할 수 있는 점들의 집합을
**작업 영역(workspace)** 이라고 한다.

### 링크 변환의 곱

DH 레슨에서 만든 링크 변환 $T_{i-1,i}(\theta_i)$ 를 기저에서 말단까지 차례로 곱하면 된다.
M1 의 합성 규칙($T_{ac} = T_{ab}T_{bc}$)이 그대로 적용된다. 마지막에 공구(그리퍼) 좌표계
$T_{n,\text{tool}}$ 같은 고정 변환을 곱하는 일도 흔하다.

### 다른 방법: 지수 곱(PoE)

Modern Robotics 는 DH 대신 각 관절의 나사 축(screw axis)과 영점 자세 $M$ 으로
$T = e^{[\mathcal{S}_1]\theta_1}\cdots e^{[\mathcal{S}_n]\theta_n}M$ 을 쓴다. 링크마다 좌표계를 붙일
필요가 없어 실수가 적다. 계산 결과는 DH 와 같으므로, 이 커리큘럼에서는 DH 로 먼저
익히고 PoE 는 참고 자료로 확인한다.

## 핵심 수식

$$T_{0n}(\boldsymbol{\theta}) = T_{01}(\theta_1)\,T_{12}(\theta_2)\cdots T_{n-1,n}(\theta_n)$$

2-link 평면 팔($c_1 = \cos\theta_1$, $c_{12} = \cos(\theta_1+\theta_2)$ 등의 약식 표기):

$$x = L_1 c_1 + L_2 c_{12}, \qquad y = L_1 s_1 + L_2 s_{12}, \qquad \phi = \theta_1 + \theta_2$$

작업 영역은 기저를 중심으로 하는 고리(annulus)다(관절 제한이 없을 때).

$$|L_1 - L_2| \le \sqrt{x^2 + y^2} \le L_1 + L_2$$

## 예제

$L_1 = 0.5$, $L_2 = 0.3$, $\theta_1 = 30^\circ$, $\theta_2 = 45^\circ$ 일 때 손계산:

- $x = 0.5\cos 30^\circ + 0.3\cos 75^\circ = 0.43301 + 0.07765 \approx 0.5107$
- $y = 0.5\sin 30^\circ + 0.3\sin 75^\circ = 0.2500 + 0.2898 = 0.5398$
- $\phi = 75^\circ$

DH 행렬 곱과 닫힌 식이 같은 답을 주는지 코드로 확인한다.

```python
import numpy as np


def dh(theta, d, a, alpha):
    ct, st, ca, sa = np.cos(theta), np.sin(theta), np.cos(alpha), np.sin(alpha)
    return np.array(
        [
            [ct, -st * ca, st * sa, a * ct],
            [st, ct * ca, -ct * sa, a * st],
            [0.0, sa, ca, d],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )


def fk(thetas, table):
    """table: [(d, a, alpha), ...] — 회전 관절만 가정."""
    T = np.eye(4)
    for th, (d, a, alpha) in zip(thetas, table):
        T = T @ dh(th, d, a, alpha)
    return T


L1, L2 = 0.5, 0.3
table = [(0, L1, 0), (0, L2, 0)]
th = np.deg2rad([30, 45])
print(fk(th, table)[:2, 3].round(4))  # [0.5107 0.5398]
print(L1 * np.cos(th[0]) + L2 * np.cos(th.sum()), L1 * np.sin(th[0]) + L2 * np.sin(th.sum()))
```

**연습 과제(exercise):** (1) 관절 각을 격자로 샘플링해 2-link 팔의 작업 영역을 산점도로
그리고, 위 고리 공식과 비교하라. (2) $\theta_1 \in [0, 180^\circ]$ 처럼 관절 제한을 넣으면
작업 영역이 어떻게 바뀌는지 그려라. (3) 3-link 평면 팔로 확장해 같은 점에 서로 다른
$\phi$ 로 도달할 수 있음을 확인하라.

## 자가 점검 질문

1. 정기구학의 해가 항상 하나로 정해지는 이유는 무엇인가? (역기구학과 비교해 보라.)
2. $L_1 = L_2$ 인 2-link 팔은 기저 원점에 도달할 수 있는가? 그때 $\theta_2$ 는 얼마인가?
3. 링크 변환을 곱하는 순서를 거꾸로($T_{n-1,n}\cdots T_{01}$) 하면 왜 틀린 결과가 나오는가?

## 이 단계 공부법

1. **영상:** Modern Robotics 강의 영상 4장 "Forward Kinematics" (PoE 공식) 를 본다.
2. **교재:** 표준 DH 로 공부했다면 Spong 등 3장의 정기구학 예제(평면 팔, SCARA 등)를,
   Craig 를 기준으로 삼았다면 Craig 3장 예제를 따라 계산한다. 그다음 Modern Robotics 4장을
   읽고 PoE 와 DH 의 결과가 같음을 확인한다.
3. **본문 + 예제:** 손계산 → 코드 순서로 위 예제를 재현한다.
4. **문제:** 확인 퀴즈 → 연습 과제(작업 영역 그리기, 3-link 확장) 순으로 푼다.
5. **도구(선택):** Modern Robotics 공식 Python 라이브러리(`modern_robotics` 패키지)의
   `FKinSpace` 로 같은 팔을 계산해 결과를 비교한다.

## 참고 자료

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, 4장 "Forward Kinematics" —
  <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics 강의 영상 목록 — <https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos>
- Modern Robotics 공식 코드 라이브러리 (Python/MATLAB/Mathematica) —
  <https://github.com/NxRLab/ModernRobotics>
- Mark W. Spong, Seth Hutchinson, M. Vidyasagar, *Robot Modeling and Control*, 2nd ed., Wiley, 2020 — 3장.
- John J. Craig, *Introduction to Robotics: Mechanics and Control*, 4th ed., Pearson — 3장.
