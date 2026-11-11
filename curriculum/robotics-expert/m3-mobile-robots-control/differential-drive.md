---
id: m3-differential-drive
title: 차동 구동 모델
summary: 두 바퀴 속도로 움직이는 차동 구동 로봇의 기구학(유니사이클 모델)을 유도하고, 바퀴 속도와 로봇 속도를 상호 변환하며 오도메트리로 자세를 추정한다.
objectives:
  - 좌·우 바퀴 각속도로부터 로봇의 선속도와 각속도를 계산하고, 그 역변환을 할 수 있다.
  - 유니사이클 기구학 모델과 비홀로노믹 구속 조건을 설명할 수 있다.
  - 오일러 적분으로 오도메트리(추측 항법)를 구현하고 오차가 누적되는 이유를 설명할 수 있다.
prerequisites: [m1-coordinate-transforms]
difficulty: 2
estimated_minutes: 80
tags: [mobile-robot, kinematics, differential-drive, odometry]
activities:
  - id: m3-differential-drive-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 30
  - id: m3-differential-drive-quiz
    kind: quiz
    title: 바퀴 속도 ↔ 로봇 속도 변환 퀴즈
    estimated_minutes: 15
  - id: m3-differential-drive-exercise
    kind: exercise
    title: 오도메트리 시뮬레이션으로 원·8자 궤적 그리기
    estimated_minutes: 35
resources:
  - title: "Modern Robotics, 13장 Wheeled Mobile Robots (Lynch & Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: 13.2–13.3절의 차동 구동(diff-drive) 기구학과 비홀로노믹 구속. 무료 프리프린트.
  - title: Modern Robotics 강의 영상 (13장)
    url: https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos
    kind: video
    note: 바퀴 달린 이동 로봇 챕터 영상.
  - title: "Introduction to Autonomous Mobile Robots, 2nd ed. (Siegwart, Nourbakhsh, Scaramuzza)"
    kind: book
    note: 3장 이동 로봇 기구학. 바퀴 종류별 구속 조건을 체계적으로 다룬다.
  - title: "Probabilistic Robotics (Thrun, Burgard, Fox)"
    url: https://robots.stanford.edu/probabilistic-robotics/
    kind: book
    note: 5장 Robot Motion — 속도 모델·오도메트리 모델과 그 불확실성(선택, 심화).
---

# 차동 구동 모델

차동 구동(differential drive)은 좌우 두 바퀴를 독립적으로 돌려 움직이는 가장 흔한 이동 로봇
구조다. 로봇 청소기, 교육용 e-puck, TurtleBot 이 모두 이 방식이다. 두 바퀴의 속도 차이로
방향을 바꾸기 때문에 조향 장치가 필요 없고 제자리 회전도 가능하다. 이 레슨의 모델은 이어지는
PID 제어와 경로 추종 레슨에서 "제어할 대상(plant)" 으로 그대로 쓰인다.

## 개념

### 상태와 입력

평면 위 로봇의 자세(pose)는 $(x, y, \theta)$ 세 값이다. M1 에서 배운 $SE(2)$ 변환
$T_{wr}$ 이 바로 이 자세다. 제어 입력은 오른쪽·왼쪽 바퀴의 각속도 $\omega_R, \omega_L$ 이며,
바퀴 반지름을 $r$, 두 바퀴 사이 거리(축간 거리)를 $L$ 이라 한다.

### 바퀴 속도 → 로봇 속도

각 바퀴의 접지점 속도는 $r\omega_R$, $r\omega_L$ 이다. 로봇 중심의 선속도 $v$ 는 두 값의
평균이고, 각속도 $\omega$ 는 두 값의 차이를 축간 거리로 나눈 것이다. 두 바퀴가 같은 속도면
직진, 크기가 같고 방향이 반대면 제자리 회전, 그 사이면 반지름 $R = v/\omega$ 인 원호를 그린다.

### 유니사이클 모델과 비홀로노믹 구속

로봇 속도 $(v, \omega)$ 를 입력으로 보면 차동 구동은 **유니사이클(unicycle) 모델**과 같아진다.
바퀴는 옆으로 미끄러지지 않으므로 로봇은 자기 몸체의 옆 방향으로 순간 이동할 수 없다.
이 **비홀로노믹(nonholonomic) 구속** 때문에 3차원 자세를 2개 입력으로 제어해야 하고,
"옆으로 30 cm 평행 주차" 같은 동작은 전진·회전을 조합해야만 가능하다.

### 오도메트리

바퀴 엔코더로 $\omega_R, \omega_L$ 을 측정해 위 식을 시간에 대해 적분하면 자세를 추정할 수 있다.
이것이 **오도메트리(추측 항법, dead reckoning)** 다. 바퀴 미끄러짐, 반지름·축간 거리 오차,
적분 오차가 계속 누적되므로 장시간 쓰면 위치가 크게 어긋난다. 이를 보정하는 것이 M4 센서와
이후 상태 추정의 역할이다.

## 핵심 수식

$$v = \frac{r(\omega_R + \omega_L)}{2}, \qquad \omega = \frac{r(\omega_R - \omega_L)}{L}$$

역변환(원하는 로봇 속도 → 바퀴 명령):

$$\omega_R = \frac{v + \omega L/2}{r}, \qquad \omega_L = \frac{v - \omega L/2}{r}$$

유니사이클 기구학과 비홀로노믹 구속:

$$\dot{x} = v\cos\theta, \quad \dot{y} = v\sin\theta, \quad \dot{\theta} = \omega, \qquad
\dot{x}\sin\theta - \dot{y}\cos\theta = 0$$

시간 간격 $\Delta t$ 의 오일러 적분(오도메트리 갱신):

$$x_{k+1} = x_k + v\cos\theta_k\,\Delta t, \quad y_{k+1} = y_k + v\sin\theta_k\,\Delta t, \quad \theta_{k+1} = \theta_k + \omega\,\Delta t$$

## 예제

e-puck 정도 크기의 로봇을 가정하자(예시 값: $r = 0.02$ m, $L = 0.05$ m). $\omega_R = 10$,
$\omega_L = 5$ rad/s 이면

- $v = 0.02 \times 15 / 2 = 0.15$ m/s
- $\omega = 0.02 \times 5 / 0.05 = 2$ rad/s
- 회전 반지름 $R = v/\omega = 0.075$ m

```python
import numpy as np

r, L, dt = 0.02, 0.05, 0.01


def wheels_to_body(wR, wL):
    return r * (wR + wL) / 2, r * (wR - wL) / L


def body_to_wheels(v, w):
    return (v + w * L / 2) / r, (v - w * L / 2) / r


def step(pose, v, w):
    x, y, th = pose
    return np.array([x + v * np.cos(th) * dt, y + v * np.sin(th) * dt, th + w * dt])


v, w = wheels_to_body(10, 5)
print(v, w, body_to_wheels(v, w))  # 0.15 2.0 (10.0, 5.0) — 부동소수점 오차 무시

pose = np.zeros(3)
for _ in range(int(np.pi / w / dt)):  # 반 바퀴 (pi rad)
    pose = step(pose, v, w)
print(pose.round(3))  # 대략 [0, 0.15, pi]: 지름 2R = 0.15 m
```

**연습 과제(exercise):** (1) 일정한 바퀴 속도로 원을, 시간에 따라 $\omega$ 부호를 바꿔 8자를
그려라. (2) $\Delta t$ 를 0.1 s 로 키우면 원이 닫히지 않는 이유를 설명하라. (3) 실제 $r$ 이
모델보다 2% 작다고 가정해 바퀴 속도를 계산하고, 오도메트리 추정 위치와 "실제" 위치의 차이가
시간에 따라 어떻게 커지는지 그려라.

## 자가 점검 질문

1. $\omega_R = -\omega_L$ 일 때 로봇은 어떻게 움직이며, 회전 중심은 어디인가?
2. 비홀로노믹 구속이 있어도 차동 구동 로봇이 평면 위 임의의 자세에 도달할 수 있는 이유는 무엇인가?
3. 오도메트리 오차가 시간이 지날수록 커지는 원인 세 가지를 들어라.

## 이 단계 공부법

1. **교재:** Modern Robotics 13장 도입부와 차동 구동 로봇 기구학 부분을 읽는다(이 레슨 수식과
   표기가 조금 다르니 대응 관계를 표로 정리해 둔다). Siegwart 책이 있다면 3장을 함께 본다.
2. **영상:** Modern Robotics 강의 영상 13장 중 바퀴 달린 이동 로봇 기구학 영상을 본다.
3. **본문 + 예제:** 예제 수치를 손으로 계산한 뒤 코드로 반 바퀴 궤적을 재현한다.
4. **문제:** 확인 퀴즈 → 연습 과제 (1)~(3) 순으로 푼다.
5. **심화(선택):** Probabilistic Robotics 5장에서 오도메트리 모델의 확률적 해석을 훑어본다.
   M4 센서·필터링 레슨의 예고편이다.

## 참고 자료

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, 13장 "Wheeled Mobile Robots" —
  <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics 강의 영상 목록 — <https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos>
- Roland Siegwart, Illah R. Nourbakhsh, Davide Scaramuzza, *Introduction to Autonomous Mobile
  Robots*, 2nd ed., MIT Press, 2011 — 3장 "Mobile Robot Kinematics".
- Sebastian Thrun, Wolfram Burgard, Dieter Fox, *Probabilistic Robotics*, MIT Press, 2005 —
  5장 "Robot Motion" (동반 사이트: <https://robots.stanford.edu/probabilistic-robotics/>).
