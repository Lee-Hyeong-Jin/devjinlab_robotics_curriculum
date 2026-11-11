---
id: m3-path-following
title: 경로 추종
summary: 차동 구동 모델과 PID 를 결합해 목표점 도달(go-to-goal), 웨이포인트 추종, Pure Pursuit 경로 추종 제어기를 구현하고 도달 오차로 성능을 평가한다.
objectives:
  - 목표점까지의 거리·방향 오차로 선속도·각속도 명령을 만드는 go-to-goal 제어기를 구현할 수 있다.
  - 웨이포인트 목록을 수용 반경으로 전환하며 따라가는 추종기를 구현할 수 있다.
  - Pure Pursuit 의 곡률 식을 유도하고 전방 주시 거리가 추종 성능에 주는 영향을 설명할 수 있다.
prerequisites: [m3-differential-drive, m3-pid-control]
difficulty: 3
estimated_minutes: 100
tags: [mobile-robot, control, path-following, pure-pursuit]
activities:
  - id: m3-path-following-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 35
  - id: m3-path-following-quiz
    kind: quiz
    title: 경로 추종 오차·전방 주시 거리 퀴즈
    estimated_minutes: 15
  - id: m3-path-following-exercise
    kind: exercise
    title: 웨이포인트 추종기 구현과 최종 도달 오차 측정
    estimated_minutes: 50
resources:
  - title: "Robotics, Vision and Control, 3rd ed. (Peter Corke)"
    url: https://link.springer.com/10.1007/978-3-031-06469-2
    kind: book
    note: 4장 이동 로봇 — 점으로 이동(moving to a point), 선·경로 추종, pure pursuit 를 Python 으로 다룬다.
  - title: "Implementation of the Pure Pursuit Path Tracking Algorithm (R. Craig Coulter, CMU Robotics Institute, 1992)"
    kind: article
    note: Pure Pursuit 의 원전 기술 보고서. 곡률 유도와 전방 주시 거리 논의.
  - title: "Introduction to Autonomous Mobile Robots, 2nd ed. (Siegwart, Nourbakhsh, Scaramuzza)"
    kind: book
    note: 3장 끝부분의 이동 로봇 운동 제어(극좌표 기반 목표점 제어).
  - title: "Modern Robotics, 13장 Wheeled Mobile Robots (Lynch & Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: 13.3절 비홀로노믹 로봇의 운동 계획과 피드백 제어(심화).
---

# 경로 추종

M3 의 마지막 레슨이다. 차동 구동 모델(무엇을 움직이는가)과 PID(어떻게 오차를 줄이는가)를
합쳐, 로봇이 **목표점에 도착하고 주어진 경로를 따라가게** 만든다. 라인 트레이싱, 목표점
도달 같은 과제는 모두 이 레슨의 제어기 중 하나로 풀 수 있다.

## 개념

### 1) 목표점 도달 (go-to-goal)

로봇 자세 $(x, y, \theta)$, 목표 $(x_g, y_g)$ 가 있을 때 두 오차를 정의한다.

- 거리 오차 $\rho$: 목표까지의 직선 거리
- 방향 오차 $\alpha$: 목표를 바라보는 방향과 현재 방향의 차이(반드시 $(-\pi, \pi]$ 로 감는다)

$\omega$ 는 $\alpha$ 에 대한 P(또는 PID) 제어로, $v$ 는 $\rho$ 에 비례하되 상한을 둔다.
$\alpha$ 가 클 때 $v$ 를 줄이면(예: $\cos\alpha$ 를 곱함) 로봇이 엉뚱한 방향으로 크게 돌아가는
것을 막을 수 있다. 목표를 M1 의 역변환으로 **로봇 좌표계**로 옮겨 놓고 생각하면 식이 단순해진다.

### 2) 웨이포인트 추종

경로를 점 목록으로 나누고, 현재 웨이포인트까지 거리가 **수용 반경** $\varepsilon$ 보다 작아지면
다음 점으로 넘어간다. 구현이 쉽지만 점마다 감속·방향 전환이 생겨 움직임이 끊기고,
$\varepsilon$ 이 너무 작으면 점 주변을 맴도는 문제가 생긴다.

### 3) Pure Pursuit

경로 위에서 로봇으로부터 **전방 주시 거리** $L_d$ 만큼 떨어진 점을 계속 골라, 그 점을 지나는
원호를 따라가도록 곡률을 정한다. 이동하면서 목표점도 앞으로 미끄러지므로 부드럽게 경로를
따라간다. $L_d$ 가 작으면 경로에 바짝 붙지만 진동하고, 크면 부드럽지만 모서리를 크게 잘라
먹는다. 속도에 비례해 $L_d$ 를 키우는 것이 흔한 실전 규칙이다.

### 성능 지표

- **횡방향 오차(cross-track error):** 경로에서 로봇까지의 수직 거리
- **최종 도달 오차:** 마지막 목표점과 정지 위치 사이의 거리
- 소요 시간, 최대 각속도

## 핵심 수식

$$\rho = \sqrt{(x_g - x)^2 + (y_g - y)^2}, \qquad
\alpha = \operatorname{wrap}\!\big(\operatorname{atan2}(y_g - y,\ x_g - x) - \theta\big)$$

$$v = \min(k_\rho\,\rho,\ v_{\max})\cos\alpha, \qquad \omega = k_\alpha\,\alpha$$

Pure Pursuit: 전방 주시 점이 로봇 좌표계에서 진행 방향과 각도 $\alpha$ 를 이룰 때,

$$\kappa = \frac{2\sin\alpha}{L_d}, \qquad \omega = v\,\kappa$$

(로봇 좌표계에서 그 점의 횡방향 좌표가 $y_r$ 이면 $\kappa = 2y_r / L_d^2$ 와 같다.)

## 예제

정사각형 경로의 웨이포인트를 go-to-goal 제어기로 차례로 방문하고 최종 도달 오차를 출력한다.

```python
import numpy as np


def wrap(a):
    return np.arctan2(np.sin(a), np.cos(a))


def go_to_goal(pose, goal, k_rho=1.0, k_alpha=4.0, v_max=0.2):
    x, y, th = pose
    dx, dy = goal[0] - x, goal[1] - y
    rho = np.hypot(dx, dy)
    alpha = wrap(np.arctan2(dy, dx) - th)
    v = min(k_rho * rho, v_max) * max(np.cos(alpha), 0.0)  # 뒤쪽 목표면 제자리 회전
    return v, k_alpha * alpha, rho


def follow(waypoints, eps=0.05, dt=0.02, t_max=60.0):
    pose, i, traj = np.array([0.0, 0.0, 0.0]), 0, []
    for _ in range(int(t_max / dt)):
        last = i == len(waypoints) - 1
        v, w, rho = go_to_goal(pose, waypoints[i])
        if rho < (0.005 if last else eps):
            if last:
                break
            i += 1
            continue
        pose = pose + np.array([v * np.cos(pose[2]), v * np.sin(pose[2]), w]) * dt
        traj.append(pose.copy())
    return pose, np.array(traj)


wps = [(1, 0), (1, 1), (0, 1), (0, 0)]
final, traj = follow(wps)
print("최종 도달 오차 [m]:", round(float(np.hypot(*final[:2])), 4))  # 0.005 미만
```

**연습 과제(exercise):** (1) 궤적을 그리고 $\varepsilon$ 을 0.02, 0.05, 0.2 m 로 바꿔 모서리
처리와 소요 시간을 비교하라. (2) 각속도 제어를 PID 레슨의 `PID` 클래스로 바꾸고 일정한
외란을 넣어 최종 도달 오차가 어떻게 달라지는지 확인하라. (3) 같은 정사각형 경로를 촘촘한 점으로
나누어 Pure Pursuit 를 구현하고, $L_d$ = 0.1, 0.3, 0.6 m 에서 최대 횡방향 오차를 표로 정리하라.

## 자가 점검 질문

1. 방향 오차 $\alpha$ 를 감지 않으면 go-to-goal 제어기에 어떤 문제가 생기는가?
2. Pure Pursuit 에서 전방 주시 거리를 너무 작게, 또 너무 크게 잡으면 각각 어떤 현상이 나타나는가?
3. 웨이포인트 수용 반경이 0 에 가까우면 왜 로봇이 목표 주변을 맴돌 수 있는가?

## 이 단계 공부법

1. **교재(주):** Corke *Robotics, Vision and Control* 3판 4장에서 점으로 이동, 선 추종,
   경로 추종 절을 읽고 Python 예제를 따라 한다.
2. **원전:** Coulter 의 Pure Pursuit 기술 보고서에서 곡률 유도 부분만 읽고, 이 레슨의
   $\kappa = 2\sin\alpha / L_d$ 를 직접 유도해 본다.
3. **본문 + 예제:** 예제를 실행해 정사각형 경로와 최종 도달 오차를 확인한다.
4. **문제:** 확인 퀴즈 → 연습 과제 (1)~(3) 순으로 푼다. (3) 의 표가 이 모듈의 결과물이다.
5. **정리:** M1–M3 을 돌아보며 "좌표 변환 → 기구학 모델 → 피드백 제어 → 경로 추종" 의 흐름을
   한 장으로 요약한다. 심화로 Siegwart 3장의 극좌표 기반 목표점 제어(안정성 조건)를 읽는다.

## 참고 자료

- Peter Corke, *Robotics, Vision and Control: Fundamental Algorithms in Python*, 3rd ed.,
  Springer, 2023 — 4장 "Mobile Robot Vehicles" — <https://link.springer.com/10.1007/978-3-031-06469-2>
- R. Craig Coulter, *Implementation of the Pure Pursuit Path Tracking Algorithm*,
  Carnegie Mellon University Robotics Institute Technical Report, 1992.
- Roland Siegwart, Illah R. Nourbakhsh, Davide Scaramuzza, *Introduction to Autonomous Mobile
  Robots*, 2nd ed., MIT Press, 2011 — 3장 "Mobile Robot Kinematics" (운동 제어 절).
- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, 13장 —
  <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
