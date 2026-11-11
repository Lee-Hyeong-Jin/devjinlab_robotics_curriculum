---
id: m1-rotation-representations
title: 회전 표현 (오일러 각 / 쿼터니언)
summary: 3차원 회전을 회전 행렬, 오일러 각, 축-각, 쿼터니언으로 표현하고 각각의 장단점과 상호 변환을 익힌다.
objectives:
  - 회전 행렬의 성질(직교, 행렬식 1)과 열벡터의 의미를 설명할 수 있다.
  - ZYX(롤·피치·요) 오일러 각으로 회전 행렬을 구성하고 짐벌 락이 생기는 조건을 설명할 수 있다.
  - 단위 쿼터니언과 회전 행렬·오일러 각을 서로 변환하고, 라이브러리별 성분 순서 차이를 구분할 수 있다.
prerequisites: [m1-vectors-matrices]
difficulty: 2
estimated_minutes: 90
tags: [math, rotation, euler-angles, quaternion]
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
  - title: "Modern Robotics, 3.2절 회전 + 부록 B (Lynch & Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: 회전 행렬, 지수 좌표, 오일러 각·쿼터니언.
  - title: "Modern Robotics 강의 영상 (3장)"
    url: https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos
    kind: video
    note: 회전 행렬과 각속도 영상.
  - title: "Robotics, Vision and Control, 3rd ed. (Peter Corke)"
    url: https://link.springer.com/10.1007/978-3-031-06469-2
    kind: book
    note: 2장 Representing Position and Orientation (Python 예제).
  - title: "SciPy Rotation 문서"
    url: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html
    kind: article
    note: from_euler 축 규약, as_quat 성분 순서 (x, y, z, w).
  - title: "QUT Robot Academy (Peter Corke) — Spatial Maths"
    url: https://robotacademy.net.au/
    kind: course
    note: 3D 회전 시각화 강의(선택).
---

# 회전 표현

로봇 팔의 말단 자세, 드론의 기울기, 이동 로봇의 진행 방향은 모두 "회전"이다. 회전은
3자유도를 가지지만 이를 숫자로 적는 방법은 여러 가지이고, 각 방법은 계산 편의성과
함정이 다르다. 이 레슨에서는 네 가지 표현을 비교하고 서로 변환하는 법을 익힌다.

## 개념

### 회전 행렬

회전 행렬 $R$ 은 $3\times3$ 직교 행렬로, $R^TR = I$, $\det R = 1$ 을 만족한다. 이런
행렬의 집합을 $SO(3)$ 라고 부른다. $R$ 의 세 열은 **회전된 좌표계의 x, y, z 축을 원래
좌표계에서 본 단위 벡터**다. 합성은 행렬 곱 한 번이고 모호함이 없지만, 9개 숫자로
3자유도를 표현하므로 중복이 크고, 수치 오차가 쌓이면 직교성이 깨지므로 주기적으로
정규화해야 한다.

### 오일러 각

세 번의 축 회전으로 자세를 표현한다. 로보틱스와 항공에서 흔한 것은 ZYX 순서의
요(yaw, $\psi$)–피치(pitch, $\theta$)–롤(roll, $\phi$) 이다. 사람이 읽기 쉽다는 큰 장점이
있지만:

- 축 순서(XYZ, ZYX, ZYZ …)와 **고정축(extrinsic)/이동축(intrinsic)** 해석에 따라 같은
  세 숫자가 다른 회전을 뜻한다. 사용하는 라이브러리의 규약을 반드시 확인해야 한다.
- 피치가 $\pm 90^\circ$ 일 때 첫 번째와 세 번째 회전축이 겹쳐 자유도 하나가 사라지는
  **짐벌 락(gimbal lock)** 이 생긴다. 이 근처에서는 각도 값이 급격히 튀고 보간이 깨진다.

### 축-각 (axis-angle)

모든 3차원 회전은 어떤 단위축 $\hat{\boldsymbol{\omega}}$ 둘레로 각도 $\theta$ 만큼 도는 것으로
표현된다(오일러 회전 정리). 회전 벡터 $\hat{\boldsymbol{\omega}}\theta$ 는 3개 숫자로
기하학적 의미가 분명하며, Modern Robotics 의 지수 좌표(exponential coordinates)가
바로 이것이다.

### 단위 쿼터니언

축-각을 4개 숫자로 인코딩한 것이 단위 쿼터니언이다. 짐벌 락이 없고, 합성은 쿼터니언
곱, 부드러운 보간은 SLERP 로 처리한다. ROS 2 의 `geometry_msgs/Quaternion` 등 로봇
미들웨어의 기본 자세 표현이다. 주의할 점:

- $q$ 와 $-q$ 는 **같은 회전**이다(이중 덮개). 비교나 보간 전에 부호를 맞춰야 한다.
- 성분 순서가 라이브러리마다 다르다. SciPy `Rotation.as_quat()` 와 ROS 메시지는
  $(x, y, z, w)$ 순서(스칼라가 마지막)이고, 교재와 일부 라이브러리는 $(w, x, y, z)$ 를 쓴다.

## 핵심 수식

기본 회전 행렬(축 회전):

$$R_z(\psi)=\begin{bmatrix}\cos\psi&-\sin\psi&0\\ \sin\psi&\cos\psi&0\\ 0&0&1\end{bmatrix},\quad
R_y(\theta)=\begin{bmatrix}\cos\theta&0&\sin\theta\\ 0&1&0\\ -\sin\theta&0&\cos\theta\end{bmatrix}$$

ZYX 오일러 각(이동축 기준 Z → Y → X):

$$R = R_z(\psi)\,R_y(\theta)\,R_x(\phi)$$

축-각에서 쿼터니언으로:

$$q = \left(\cos\tfrac{\theta}{2},\ \hat{\boldsymbol{\omega}}\sin\tfrac{\theta}{2}\right) = (w, x, y, z), \quad w^2+x^2+y^2+z^2 = 1$$

회전 행렬의 대각합으로 회전각 구하기: $\operatorname{tr}(R) = 1 + 2\cos\theta$.

## 예제

z 축으로 90° 회전을 세 가지 표현으로 확인하고, 짐벌 락을 재현해 본다.

```python
import numpy as np
from scipy.spatial.transform import Rotation as Rot

r = Rot.from_euler("ZYX", [90, 0, 0], degrees=True)  # 대문자 = 이동축(intrinsic)
print(r.as_matrix().round(3))  # [[0,-1,0],[1,0,0],[0,0,1]]
print(r.as_quat())  # [0, 0, 0.7071, 0.7071]  (x, y, z, w)
print(r.as_rotvec())  # [0, 0, 1.5708]

# 짐벌 락: 피치 90°에서 요와 롤이 구분되지 않는다
a = Rot.from_euler("ZYX", [30, 90, 0], degrees=True)
b = Rot.from_euler("ZYX", [0, 90, -30], degrees=True)
print(np.allclose(a.as_matrix(), b.as_matrix()))  # True: 다른 각도, 같은 회전
```

손으로 확인: $\theta = 90^\circ$ 이므로 $\cos 45^\circ = \sin 45^\circ \approx 0.7071$,
축이 $z$ 이므로 $q = (0.7071, 0, 0, 0.7071)$ ($w$ 먼저 표기)가 된다.

**연습 과제(exercise):** 임의의 오일러 각 100개를 만들어 오일러 → 쿼터니언 → 행렬 →
오일러로 왕복 변환하고, 원래 각도와 달라지는 경우가 언제인지(짐벌 락 근처, 각도 범위
감기) 기록하라.

## 자가 점검 질문

1. 회전 행렬의 두 번째 열은 무엇을 의미하는가?
2. ZYX 오일러 각에서 짐벌 락은 어떤 각도에서, 왜 발생하는가?
3. 쿼터니언 $q$ 와 $-q$ 가 같은 회전이라는 사실이 보간이나 비교에서 어떤 문제를 일으킬 수 있는가?

## 이 단계 공부법

1. **영상:** Modern Robotics 강의 영상 3장 중 회전 행렬·각속도·지수 좌표 부분을 본다(위키의 Videos 페이지에서 챕터별로 찾을 수 있다).
2. **교재:** Modern Robotics 3.2절(회전 행렬, 지수 좌표)을 읽고, 부록 B 에서 오일러 각·쿼터니언 부분을 읽는다. Corke 책이 있다면 2장의 같은 내용을 함께 보면 코드 감각을 얻기 좋다.
3. **본문 + 예제:** 이 레슨 예제를 실행하고 SciPy `Rotation` 문서에서 `from_euler` 의 대문자(이동축)/소문자(고정축) 규약 설명을 확인한다.
4. **문제:** 확인 퀴즈 → 연습 과제(오일러 ↔ 쿼터니언 ↔ 행렬 왕복 변환) 순으로 푼다.
5. **보강(선택):** QUT Robot Academy 의 Spatial Maths 강의로 3D 회전의 시각적 직관을 보강한다.

## 참고 자료

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, 3장 "Rigid-Body Motions" 및 부록 B
  "Other Representations of Rotations" — <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Peter Corke, *Robotics, Vision and Control: Fundamental Algorithms in Python*, 3rd ed.,
  Springer, 2023 — 2장 "Representing Position and Orientation".
- SciPy `Rotation` 문서 —
  <https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html>
- QUT Robot Academy (Peter Corke), "Spatial Maths" 무료 강의 — <https://robotacademy.net.au/>
