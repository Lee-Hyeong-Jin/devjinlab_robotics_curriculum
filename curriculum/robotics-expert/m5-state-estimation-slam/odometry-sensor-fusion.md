---
id: m5-odometry-sensor-fusion
title: "오도메트리·센서 융합(IMU+휠)"
summary: 휠 오도메트리와 IMU 자이로를 EKF 로 합쳐 dead reckoning 의 흘러감을 줄인다. 속도를 측정으로 넣는 robot_localization 식 상태 설계를 numpy 로 구현하고, ROS 2 에서 ekf_filter_node 가 odom → base_link 를 발행하는 구조와 설정 파일을 읽는다.
objectives:
  - 휠 오도메트리와 IMU 의 오차 특성(미끄러짐·스케일 오차 대 바이어스·잡음)을 비교하고 융합이 필요한 이유를 설명할 수 있다.
  - 위치·방향·속도를 상태로 두고 두 센서의 속도 측정을 순차 갱신하는 EKF 를 구현할 수 있다.
  - robot_localization 의 ekf.yaml 에서 프레임 설정과 센서별 융합 변수 선택이 의미하는 바를 읽을 수 있다.
prerequisites: [m5-kalman-filter-ekf, m3-differential-drive, m4-filtering-basics, m8-tf2-urdf-visualization]
difficulty: 3
estimated_minutes: 130
tags: [odometry, imu, sensor-fusion, ekf, robot-localization, ros2]
activities:
  - id: m5-odometry-sensor-fusion-reading
    kind: reading
    title: 본문과 Nav2 robot_localization 가이드 읽기
    estimated_minutes: 45
  - id: m5-odometry-sensor-fusion-quiz
    kind: quiz
    title: 융합 변수 선택과 프레임 퀴즈
    estimated_minutes: 20
  - id: m5-odometry-sensor-fusion-exercise
    kind: exercise
    title: 휠+IMU EKF 튜닝 실험
    estimated_minutes: 65
resources:
  - title: "Nav2 First-Time Robot Setup Guide: Setting Up Odometry (robot_localization)"
    url: https://docs.nav2.org/rolling/configuration_and_development/first_time_robot_setup_guide/odom/setup_robot_localization/
    kind: article
    note: ekf.yaml, odom→base_link. 공식 설정 가이드.
  - title: "robot_localization 패키지 공식 문서 (ROS 2 Rolling)"
    url: https://docs.ros.org/en/rolling/p/robot_localization/
    kind: article
    note: ekf_node 파라미터 레퍼런스. 설정 중 막힐 때 찾아본다.
  - title: "Sensor Fusion and Robot Localization Using ROS 2 Jazzy (Automatic Addison)"
    url: https://automaticaddison.com/sensor-fusion-and-robot-localization-using-ros-2-jazzy/
    kind: article
    note: ekf_filter_node 설정, Jazzy.
  - title: "ROS2로 배우는 자율주행 로봇 센서 융합과 SLAM (최종명, 위키독스)"
    url: https://wikidocs.net/book/18464
    kind: book
    note: LiDAR·카메라·IMU → EKF → SLAM Toolbox(한국어, 2025-10).
  - title: "Kalman and Bayesian Filters in Python (Labbe)"
    url: https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python
    kind: book
    note: Kalman Filter Design·Extended Kalman Filters 장. 순차 갱신과 Q 튜닝.
---

# 오도메트리·센서 융합(IMU+휠)

M3 의 차동 구동 오도메트리는 바퀴가 미끄러지거나 좌우 반지름이 조금만 달라도 **방향** 오차가
생기고, 방향 오차는 이동 거리만큼 위치 오차로 커진다. IMU 자이로는 미끄러짐과 무관하지만 바이어스가 있다. 둘을 EKF 로 합치는 것이 표준이며,
ROS 2 에서는 `robot_localization` 이 이 일을 한다.

## 개념

### 두 센서의 오차 특성

| 센서 | 잘 재는 것 | 약점 |
|---|---|---|
| 휠 엔코더 | 전진 속도 $v$ | 미끄러짐·바퀴 반지름 오차로 $\omega$ 가 틀어짐 |
| IMU 자이로 | 회전 속도 $\omega$ | 작은 바이어스(적분하면 흘러감), 전진 속도는 못 잼 |

그래서 **휠의 $v$ 와 자이로의 $\omega$ 를 주로 믿는다.** 측정 분산 $R$ 로 신뢰도를 주면 칼만 필터가 비율을 정한다.

### 상태 설계: 속도를 측정으로

상태를 $s = [x, y, \theta, v, \omega]$ 로 두고, 센서는 **속도**를 측정한다고 모델링한다.
위치·방향은 필터 안에서 적분된다. 센서마다 도착할 때 순서대로 갱신하면 되므로 주기가 달라도
괜찮다. `robot_localization` 도 15차원 상태에 대해 같은 방식을 쓴다.

### 연속 추정과 전역 추정

융합 결과는 매끄럽지만 절대 기준이 없어 여전히 **흘러간다**. 그래서 `odom → base_link` 로
발행하고, 흘러감 보정은 AMCL·SLAM 이 `map → odom` 으로 맡는다(M8 tf2 레슨의 프레임 트리).

## 핵심 수식

등속 모션 모델과 야코비안의 0 이 아닌 비대각 항:

$$f(s) = \begin{bmatrix} x + v\cos\theta\,\Delta t \\ y + v\sin\theta\,\Delta t \\ \theta + \omega\Delta t \\ v \\ \omega \end{bmatrix},\quad
\frac{\partial x'}{\partial \theta} = -v\sin\theta\,\Delta t,\ \frac{\partial y'}{\partial \theta} = v\cos\theta\,\Delta t$$

측정 모델은 선형($H_w$ 는 $v, \omega$, $H_i$ 는 $\omega$ 선택)이고, 같은 $\omega$ 의 두 번 갱신은
역분산 가중 평균 $\hat\omega = (\omega_w/R_w + \omega_i/R_i)/(1/R_w + 1/R_i)$ 이다.

## 예제

60 초 주행. 휠 $\omega$ 에는 바이어스(0.02 rad/s)와 미끄러짐, 자이로에는 0.002 rad/s 바이어스를 넣었다.

```python
import numpy as np

rng = np.random.default_rng(7)
dt, T = 0.05, 1200  # 20 Hz, 60 초


def f(s):
    """등속 모델. 상태 s = [x, y, theta, v, omega]."""
    x, y, th, v, w = s
    return np.array([x + v * np.cos(th) * dt, y + v * np.sin(th) * dt, th + w * dt, v, w])


def F_jac(s):
    _, _, th, v, _ = s
    J = np.eye(5)
    J[0, 2], J[0, 3] = -v * np.sin(th) * dt, np.cos(th) * dt
    J[1, 2], J[1, 3] = v * np.cos(th) * dt, np.sin(th) * dt
    J[2, 4] = dt
    return J


def kf_update(s, P, z, H, R):
    K = P @ H.T @ np.linalg.inv(H @ P @ H.T + R)
    return s + K @ (z - H @ s), (np.eye(5) - K @ H) @ P


H_wheel = np.array([[0, 0, 0, 1, 0], [0, 0, 0, 0, 1.0]])  # 휠: v, omega
R_wheel = np.diag([0.02**2, 0.05**2])
H_imu = np.array([[0, 0, 0, 0, 1.0]])  # IMU 자이로: omega
R_imu = np.array([[0.01**2]])
Q = np.diag([1e-6, 1e-6, 1e-6, 0.05**2, 0.1**2]) * dt

truth, dr = np.zeros(5), np.zeros(5)  # dr: 휠만 적분한 dead reckoning
s, P = np.zeros(5), np.eye(5) * 0.01
for k in range(T):
    t = k * dt
    truth[3], truth[4] = 0.5, 0.3 * np.sin(0.2 * t)
    truth = f(truth)
    slip = 0.03 if 20 < t < 30 else 0.0
    z_wheel = truth[3:] + [0.0, 0.02 + slip] + rng.normal(0, [0.02, 0.05])
    z_imu = truth[4:] + 0.002 + rng.normal(0, 0.01, 1)

    dr[3:] = z_wheel
    dr = f(dr)

    J = F_jac(s)
    s, P = f(s), J @ P @ J.T + Q  # 예측
    s, P = kf_update(s, P, z_wheel, H_wheel, R_wheel)  # 휠 갱신
    s, P = kf_update(s, P, z_imu, H_imu, R_imu)  # IMU 갱신

for name, est in [("휠만", dr), ("EKF", s)]:
    pos_err = np.linalg.norm(est[:2] - truth[:2])
    print(f"{name}: 위치 오차 {pos_err:.2f} m, 방향 오차 {np.rad2deg(est[2] - truth[2]):.1f} deg")
```

휠만 적분하면 위치 오차 10 m 이상, 방향 오차 약 80° 지만 EKF 는 약 1.4 m, 11° 에 머문다.
남은 오차는 주로 자이로 바이어스 때문이며 절대 기준(지도) 없이는 없앨 수 없다. 다음 두 레슨의 몫이다.

### ROS 2 설정 읽기

`ekf_filter_node` 설정은 위 코드와 대응한다(구조만 보인 발췌).

```yaml
ekf_filter_node:
  ros__parameters:
    two_d_mode: true
    world_frame: odom          # odom → base_link 를 발행
    odom0: /wheel/odometry
    odom0_config: [false, false, false, false, false, false,
                   true, false, false, false, false, true,
                   false, false, false]  # vx, vyaw 만 융합
    imu0: /imu/data            # imu0_config 는 vyaw 만 true
```

15 개 불리언은 x, y, z, roll, pitch, yaw, vx, vy, vz, vroll, vpitch, vyaw, ax, ay, az 순서다.

**연습 과제(exercise):** (1) `R_wheel` 의 $\omega$ 분산을 `R_imu` 와 같게 바꾸면 결과가 어떻게
나빠지는지 설명하라. (2) 상태에 자이로 바이어스 $b$ 를 추가하고 정지 구간에서 추정되는지 확인하라.
(3) Nav2 가이드의 ekf.yaml 에서 켜진 융합 변수를 표로 정리하라.

## 자가 점검 질문

1. 휠 오도메트리에서 방향 오차가 특히 위험한 이유는?
2. 센서가 위치 대신 속도를 측정한다고 모델링하면 어떤 장점이 있는가?
3. 융합 결과를 `map → base_link` 가 아니라 `odom → base_link` 로 발행하는 이유는 무엇인가?

## 확인 퀴즈

`rc quiz m5-odometry-sensor-fusion` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m5-odometry-sensor-fusion-quiz
questions:
  - id: q1
    type: single
    prompt: '휠 오도메트리에서 **방향** 오차가 특히 위험한 이유는?'
    choices:
      - '방향은 측정할 수 없기 때문'
      - '방향 오차가 이후 모든 전진을 틀린 쪽으로 적분해 위치 오차가 거리에 비례해 커지기 때문'
      - '방향 오차는 항상 거리 오차보다 크기 때문'
      - '방향은 tf 에 들어가지 않기 때문'
    answer: 1
    explanation: '$\dot x = v\cos\theta$, $\dot y = v\sin\theta$ 이므로 $\theta$ 가 틀리면 이후 주행 전체가 틀린 방향으로 쌓인다. 작은 각도 오차도 멀리 갈수록 위치 오차를 선형으로 키운다. 그래서 자이로의 $\omega$ 를 섞어 방향을 먼저 잡는 것이 효과가 크다.'
    concept: { front: '방향 오차가 치명적인 이유', back: '틀린 $\theta$ 로 전진을 적분 → 위치 오차가 주행 거리에 비례해 증가' }
  - id: q2
    type: single
    prompt: '센서가 위치 대신 **속도**를 측정한다고 모델링하면 얻는 장점은?'
    choices:
      - '측정 모델이 선형이 되고, 센서 주기가 달라도 도착하는 대로 갱신할 수 있다'
      - '모션 모델이 필요 없어진다'
      - '공분산을 계산하지 않아도 된다'
      - '드리프트가 사라진다'
    answer: 0
    explanation: '엔코더와 자이로가 실제로 재는 양이 속도이므로 측정 모델 $H$ 가 상태에서 $v$, $\omega$ 를 고르는 선형 행렬이 된다. 위치·방향은 필터 안에서 적분되고, 센서가 도착한 순서대로 갱신하면 되므로 주기가 달라도 문제가 없다. 드리프트 자체는 여전히 남는다.'
    concept: { front: '속도를 측정으로 두는 설계', back: '측정 모델이 선형이 되고 비동기 센서를 순서대로 갱신 가능 — 위치는 필터가 적분' }
  - id: q3
    type: single
    prompt: '융합 결과를 `map → base_link` 가 아니라 `odom → base_link` 로 발행하는 이유는?'
    choices:
      - '`map` 프레임은 존재하지 않기 때문'
      - '융합 결과는 매끄럽지만 절대 기준이 없어 흘러가므로, 전역 보정은 AMCL·SLAM 이 `map → odom` 으로 맡기 때문'
      - '`odom` 프레임이 더 정확하기 때문'
      - 'tf2 가 `map` 을 부모로 허용하지 않기 때문'
    answer: 1
    explanation: 'REP 105 의 역할 분담이다. `odom → base_link` 는 연속적이고 점프가 없어야 하는 추정(제어·지역 계획에 필요)이고, 절대 위치 보정은 점프할 수 있는 `map → odom` 에서 한다. 한 변환은 한 노드만 발행해야 하므로 둘을 섞으면 안 된다.'
```

## 이 단계 공부법

1. **본문 + 예제(먼저):** 예제를 실행하고 궤적을 그려 본다.
2. **공식 가이드:** Nav2 "Smoothing Odometry using Robot Localization" 을 읽고 ekf.yaml 을 본문 발췌와 대응시킨다.
3. **ROS 2 Jazzy 예:** Automatic Addison 글로 launch 파일과 토픽 연결을 읽는다.
4. **한국어 보강:** 최종명 위키독스의 EKF 센서 융합 장을 읽는다.
5. **심화(선택):** Labbe 의 Kalman Filter Design 장으로 $Q$ 튜닝을 익힌다.

## 참고 자료

- Nav2 First-Time Robot Setup Guide, "Setting Up Odometry" — <https://docs.nav2.org/rolling/configuration_and_development/first_time_robot_setup_guide/odom/setup_robot_localization/>
- robot_localization 공식 문서 (ROS 2 Rolling) — <https://docs.ros.org/en/rolling/p/robot_localization/>
- Automatic Addison, "Sensor Fusion and Robot Localization Using ROS 2 Jazzy" —
  <https://automaticaddison.com/sensor-fusion-and-robot-localization-using-ros-2-jazzy/>
- 최종명, 『ROS2로 배우는 자율주행 로봇 센서 융합과 SLAM』(위키독스) — <https://wikidocs.net/book/18464>
- Roger Labbe, *Kalman and Bayesian Filters in Python* — <https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python>
