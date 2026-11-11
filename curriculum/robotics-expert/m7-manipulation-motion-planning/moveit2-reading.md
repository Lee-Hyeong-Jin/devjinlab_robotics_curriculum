---
id: m7-moveit2-reading
title: "MoveIt 2 읽기: move_group·플래닝 씬·실행 구조"
summary: 이 모듈의 부품(IK·충돌 검사·OMPL 계획·시간 매개화·궤적 실행)이 MoveIt 2 의 move_group 노드, URDF/SRDF 로봇 모델, 플래닝 씬, 계획 파이프라인, ros2_control 궤적 컨트롤러로 어떻게 엮이는지 읽는다. numpy 로 경로점에 시간을 붙여 JointTrajectory 형태의 궤적을 만들고 컨트롤러가 거부하는 조건을 점검한다.
objectives:
  - move_group 노드를 중심으로 로봇 모델(URDF·SRDF), 플래닝 씬, 기구학 플러그인, 계획 파이프라인, 궤적 실행 관리자의 역할과 데이터 흐름을 설명할 수 있다.
  - MoveGroupInterface 의 목표 설정 → plan → execute 흐름과, 계획 결과가 FollowJointTrajectory 액션으로 ros2_control 에 전달되는 과정을 읽을 수 있다.
  - 경로점에 시간을 붙여 JointTrajectory 형태의 궤적을 만들고 관절 한계·시간 단조성을 검사할 수 있다.
prerequisites: [m7-manipulator-motion-planning, m7-grasping-impedance-control, m8-tf2-urdf-visualization, m8-stacks-dev-environment]
difficulty: 3
estimated_minutes: 120
tags: [moveit2, ros2, motion-planning, ros2-control, manipulation]
activities:
  - id: m7-moveit2-reading-reading
    kind: reading
    title: 본문과 MoveIt 2 Tutorials(Getting Started → Quickstart in RViz) 읽기
    estimated_minutes: 50
  - id: m7-moveit2-reading-quiz
    kind: quiz
    title: MoveIt 2 구성 요소·데이터 흐름 퀴즈
    estimated_minutes: 15
  - id: m7-moveit2-reading-exercise
    kind: exercise
    title: 경로점 시간 매개화와 궤적 검사
    estimated_minutes: 55
resources:
  - title: "MoveIt 2 Tutorials"
    url: https://moveit.picknik.ai/main/doc/tutorials/tutorials.html
    kind: article
    note: Getting Started → Quickstart in RViz → First C++ Project → Planning Around Objects → Pick and Place with MTC. Jazzy 권장.
  - title: "MoveIt 2 binary install"
    url: https://moveit.ai/install-moveit2/binary/
    kind: article
    note: "`ros-jazzy-moveit` 바이너리 설치(소스 빌드는 20분 이상·메모리 부담). CycloneDDS 권장."
  - title: "ros2_control documentation (control.ros.org) - Getting Started"
    url: https://control.ros.org/rolling/doc/getting_started/getting_started.html
    kind: article
    note: Controller Manager·하드웨어 인터페이스·궤적 컨트롤러 구조.
  - title: "ROS 2로 시작하는 로보틱스 Motion Planning (패스트캠퍼스, 이성원)"
    url: https://fastcampus.co.kr/data_online_mp
    kind: course
    note: Part 4 모션/경로계획, Part 5–6 ROS 2 실습(MoveIt 2 + UR). Jazzy, 유료(한국어).
  - title: "ROS 2 – MoveIt 2 – Control a Robotic Arm (Renard, Udemy)"
    url: https://www.udemy.com/course/ros2-moveit2/
    kind: course
    note: 7시간 53강, 유료(영어).
---

# MoveIt 2 읽기: move_group·플래닝 씬·실행 구조

M6 에서 Nav2 를 부품들의 조립도로 읽었듯, 이 레슨은 MoveIt 2 를 이 모듈의 조립도로 읽는다. IK(M2),
충돌 검사와 OMPL(레슨 5), 시간 매개화(레슨 3), 궤적 추종(레슨 2)이 어디에 끼워지는지 보는 것이 목표다.

## 개념

### move_group 과 로봇 모델

중심은 **move_group** 노드다. 사용자는 C++ `MoveGroupInterface`, Python `moveit_py`, 또는 RViz
MotionPlanning 플러그인으로 목표를 보내고, move_group 이 계획·실행을 맡는다. 로봇 모델은 두 파일에서 온다.

- **URDF:** 링크·관절·한계·충돌 형상(M8 tf2·URDF 레슨).
- **SRDF:** 계획 그룹(예: `manipulator`, `gripper`), 엔드 이펙터, 이름 붙은 자세(`home`), 서로 충돌할 수 없는 링크 쌍.

이 설정과 `kinematics.yaml`(KDL 같은 IK 플러그인), `joint_limits.yaml`, `ompl_planning.yaml` 은 보통
MoveIt Setup Assistant 가 만든 `*_moveit_config` 패키지에 들어 있다.

### 플래닝 씬

**플래닝 씬**은 "지금 세계"다. 관절 상태(`/joint_states`), 충돌 물체(테이블·상자), 잡은 물체(attached
object), 깊이 센서 옥토맵이 들어 있고 충돌 검사의 기준이 된다. 잡은 물체는 그리퍼에 붙여야 이송 중
충돌 검사가 맞다(레슨 4).

### 계획 파이프라인과 실행

1. 목표(관절 값, 자세, 이름 붙은 자세)를 받으면 자세 목표는 IK 플러그인으로 관절 목표가 된다.
2. 계획 파이프라인이 플래너(OMPL RRTConnect 기본, Pilz, CHOMP·STOMP)를 부르고, 요청·응답 어댑터가
   시작 상태 검사, 경로 단순화, **시간 매개화**를 붙인다.
3. 결과는 `trajectory_msgs/JointTrajectory`(관절 이름, 점마다 위치·속도·가속도·`time_from_start`)다.
4. 궤적 실행 관리자가 이를 `FollowJointTrajectory` 액션으로 **ros2_control** 의
   `joint_trajectory_controller` 에 보내고, 컨트롤러가 점 사이를 보간해 하드웨어 인터페이스로 명령한다.

실시간 원격 조작에는 **MoveIt Servo**(레슨 1의 자코비안 기반 속도 제어, 특이점 감속)를, 여러 단계의
픽앤플레이스에는 **MoveIt Task Constructor(MTC)** 를 쓴다.

### 코드 읽기

First C++ Project 튜토리얼의 핵심 흐름(단순화, 읽기용):

```cpp
using moveit::planning_interface::MoveGroupInterface;
auto move_group = MoveGroupInterface(node, "manipulator");  // SRDF 의 계획 그룹 이름
move_group.setPoseTarget(target_pose);                        // IK 로 관절 목표가 된다
MoveGroupInterface::Plan plan;
if (move_group.plan(plan)) {     // 계획 파이프라인: OMPL + 단순화 + 시간 매개화
  move_group.execute(plan);      // FollowJointTrajectory → ros2_control
}
```

바이너리 설치(Ubuntu 24.04, Jazzy):

```bash
sudo apt install ros-jazzy-moveit
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

## 핵심 수식

구간 $[\theta_a, \theta_b]$ 를 5차 다항식으로 매개화할 때 관절 한계를 만족하는 최소 시간(레슨 3):

$$T = \max_i \max\!\left(\frac{15}{8}\frac{|\Delta_i|}{v_{i,max}},\ \sqrt{\frac{10}{\sqrt{3}}\frac{|\Delta_i|}{a_{i,max}}}\right)$$

## 예제

3관절 경로점 4개에 시간을 붙여 `JointTrajectory` 구조의 점 목록을 만들고, 컨트롤러가 거부하는 대표
조건(한계 위반, `time_from_start` 비단조)을 검사한다.

```python
import numpy as np

# 플래너가 낸 관절 경로점(시간 없음)과 joint_limits.yaml 에 해당하는 한계
waypoints = np.array([[0.0, -0.5, 1.0], [0.6, -0.2, 0.7], [1.2, 0.3, 0.2], [1.5, 0.4, -0.3]])
VMAX = np.array([1.0, 1.0, 1.5])  # rad/s
AMAX = np.array([2.0, 2.0, 3.0])  # rad/s²
KV, KA = 15 / 8, 10 / np.sqrt(3)  # 5차 다항식의 최대 속도·가속도 계수 (레슨 3)


def quintic(tau):
    s = 10 * tau**3 - 15 * tau**4 + 6 * tau**5
    sd = 30 * tau**2 - 60 * tau**3 + 30 * tau**4
    sdd = 60 * tau - 180 * tau**2 + 120 * tau**3
    return s, sd, sdd


# 1) 시간 매개화: 구간마다 모든 관절이 한계 안에 드는 최소 시간 (경로점마다 정지하는 단순판)
points, t0 = [], 0.0  # (positions, velocities, accelerations, time_from_start)
for qa, qb in zip(waypoints[:-1], waypoints[1:]):
    d = np.abs(qb - qa)
    T = max(np.max(KV * d / VMAX), np.max(np.sqrt(KA * d / AMAX)))
    for tau in np.linspace(0, 1, 11)[:-1]:
        s, sd, sdd = quintic(tau)
        points.append(
            (qa + s * (qb - qa), sd / T * (qb - qa), sdd / T**2 * (qb - qa), t0 + tau * T)
        )
    t0 += T
points.append((waypoints[-1], np.zeros(3), np.zeros(3), t0))
print(f"경로점 {len(waypoints)}개 → 궤적 점 {len(points)}개, 총 {t0:.2f} s")

# 2) 컨트롤러 쪽 검사: 한계 위반과 시간 단조 증가
vel = np.array([p[1] for p in points])
acc = np.array([p[2] for p in points])
times = np.array([p[3] for p in points])
print("최대 |v|/VMAX:", (np.abs(vel).max(axis=0) / VMAX).round(3))
print("최대 |a|/AMAX:", (np.abs(acc).max(axis=0) / AMAX).round(3))
print("time_from_start 단조 증가:", bool(np.all(np.diff(times) > 0)))
for k in [0, 5, 10, len(points) - 1]:
    q, v, _, t = points[k]
    print(f"  t={t:5.2f}s  positions={q.round(3) + 0.0}  velocities={v.round(3) + 0.0}")
```

총 3.61 s 짜리 31점 궤적이 나오고, 구간마다 가장 바쁜 관절이 가속도 한계(비율 0.998)에 닿는다.
$t = 1.32$ s 처럼 경로점에서는 속도가 0 이다. 경로점마다 멈추는 이 단순판은 안전하지만 느리다.
MoveIt 2 의 시간 최적 매개화(TOTG)는 경로 전체를 하나로 보고 경로점을 멈추지 않고 지나가게 한다.

**연습 과제(exercise):** (1) `VMAX` 를 절반으로 줄여 총 시간과 한계 비율이 어떻게 바뀌는지 보라.
(2) 경로점에서 멈추지 않도록 중간 점의 속도를 앞뒤 구간 평균으로 두는 3차 Hermite 보간을 구현하고
총 시간을 비교하라. (3) MoveIt 2 Tutorials 의 Quickstart in RViz 를 따라(설치했다면) 계획 결과의
`time_from_start` 를 이 예제의 값과 같은 방식으로 검사해 보라.

## 자가 점검 질문

1. URDF 와 SRDF 에는 각각 무엇이 들어 있으며, SRDF 의 "충돌 안 함" 링크 쌍은 계획 속도에 어떤 영향을 주는가?
2. `setPoseTarget` 부터 모터가 움직이기까지 거치는 구성 요소를 순서대로 써라.
3. 물체를 잡은 뒤 플래닝 씬에서 그 물체를 그리퍼에 붙이지(attach) 않으면 어떤 문제가 생기는가?

## 이 단계 공부법

1. **문서(먼저):** MoveIt 2 Tutorials 의 Getting Started 와 개념 문서를 읽고 본문의 데이터 흐름 그림을 손으로 그린다.
2. **본문 + 예제:** 예제로 JointTrajectory 의 구조와 컨트롤러 검사를 익힌다.
3. **실습(선택):** `ros-jazzy-moveit` 바이너리를 설치해 Quickstart in RViz → First C++ Project → Planning Around Objects 순으로 따라간다.
4. **심화(선택):** Pick and Place with MTC 튜토리얼을 레슨 4의 파이프라인과 대응시켜 읽는다. 한국어 강의가 필요하면
   패스트캠퍼스 Motion Planning 강의, 실기 저가 팔은 LeRobot SO-101 문서(<https://huggingface.co/docs/lerobot/so101>)를 참고한다.

## 참고 자료

- MoveIt 2 Tutorials — <https://moveit.picknik.ai/main/doc/tutorials/tutorials.html>
- MoveIt 2 binary install — <https://moveit.ai/install-moveit2/binary/>
- ros2_control documentation, Getting Started — <https://control.ros.org/rolling/doc/getting_started/getting_started.html>
- 이성원, ROS 2로 시작하는 로보틱스 Motion Planning (패스트캠퍼스) — <https://fastcampus.co.kr/data_online_mp>
- Edouard Renard, ROS 2 – MoveIt 2 – Control a Robotic Arm (Udemy) — <https://www.udemy.com/course/ros2-moveit2/>
- LeRobot SO-101 docs — <https://huggingface.co/docs/lerobot/so101>
