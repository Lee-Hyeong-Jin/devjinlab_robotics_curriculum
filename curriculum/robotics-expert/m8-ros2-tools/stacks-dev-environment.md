---
id: m8-stacks-dev-environment
title: 상위 스택 지도와 개발 환경
summary: ros2_control·Nav2·MoveIt 2·SLAM Toolbox·robot_localization·micro-ROS 가 로봇 소프트웨어의 어느 층을 맡는지 지도로 정리하고, 네이티브 Ubuntu 24.04 와 Docker 개발 컨테이너, 테스트·CI 습관, 시뮬레이터의 위치를 개괄한다.
objectives:
  - 하드웨어 → 제어 → 추정 → 계획·행동 층에 ros2_control·robot_localization·SLAM Toolbox·Nav2·MoveIt 2·micro-ROS 를 배치하고 각자의 입력·출력 토픽을 말할 수 있다.
  - ros2_control 의 Controller Manager·Resource Manager·하드웨어 컴포넌트·컨트롤러의 역할을 설명할 수 있다.
  - 네이티브 설치와 Docker 컨테이너의 장단점을 비교하고, colcon test 로 패키지 테스트를 돌리는 흐름을 설명할 수 있다.
prerequisites: [m8-tf2-urdf-visualization]
difficulty: 3
estimated_minutes: 100
tags: [ros2, ros2-control, nav2, moveit2, micro-ros, docker, ci, dev-environment]
activities:
  - id: m8-stacks-dev-environment-reading
    kind: reading
    title: 본문과 ros2_control·Docker 가이드 읽기
    estimated_minutes: 50
  - id: m8-stacks-dev-environment-quiz
    kind: quiz
    title: 스택 지도 채우기 퀴즈
    estimated_minutes: 15
  - id: m8-stacks-dev-environment-exercise
    kind: exercise
    title: ros:jazzy 개발 컨테이너 구성과 colcon test
    estimated_minutes: 35
resources:
  - title: ros2_control Getting Started
    url: https://control.ros.org/rolling/doc/getting_started/getting_started.html
    kind: article
    note: 아키텍처 + ros2_control_demos example_1(RRBot) https://github.com/ros-controls/ros2_control_demos
  - title: Introduction to ROS 2 Development with Docker
    url: https://docs.docker.com/guides/ros2/
    kind: article
    note: ros:jazzy 이미지·Compose 개발 컨테이너. 네이티브 Ubuntu 24.04 우선.
  - title: What is the hardest part of learning ROS 2 as a beginner (ROS Discourse)
    url: https://discourse.openrobotics.org/t/what-is-the-hardest-part-of-learning-ros-2-as-a-beginner/57917
    kind: article
    note: 워크스페이스·소싱 고장 연습, 배포판 명시 교훈.
  - title: micro_ros_setup
    url: https://github.com/micro-ROS/micro_ros_setup
    kind: other
    note: 마이크로컨트롤러용 micro-ROS 빌드 도구. Humble·Jazzy·Kilted·Lyrical 지원.
---

# 상위 스택 지도와 개발 환경

ROS 2 의 진짜 가치는 통신 계층보다 그 위에 쌓인 검증된 스택이다. 바퀴 제어, 위치 추정, 지도 작성,
경로 계획, 팔 동작 계획을 처음부터 짤 필요가 없다. 이 레슨은 그 스택들을 **지도**로만 훑는다.
각 스택의 원리와 실습은 M5(추정·SLAM), M6(Nav2), M7(MoveIt 2)에서 다루며, 그 레슨들이 이 레슨을
선수로 요구한다. 후반부는 그 실습을 할 개발 환경을 정리한다.

## 개념

### 스택 지도

아래에서 위로 쌓아 읽는다.

| 층 | 스택 | 하는 일 | 주요 입출력 |
|---|---|---|---|
| 하드웨어 | micro-ROS | 마이크로컨트롤러(ESP32·STM32·Pico 등)를 ROS 2 그래프의 노드로 만든다 | 모터·센서 ↔ 토픽 |
| 제어 | ros2_control | 하드웨어 추상화 + 실시간 제어 루프 + 컨트롤러 플러그인 | `/cmd_vel` → 바퀴 명령, `/joint_states` |
| 추정 | robot_localization | 휠 오도메트리·IMU·GPS 를 EKF 로 융합 | `/odom`, `/imu` → 융합 `odom → base_link` |
| 지도·위치 | SLAM Toolbox | LiDAR SLAM, 지도 작성·위치 추정 | `/scan` → `/map`, `map → odom` |
| 이동 | Nav2 | 행동 트리(BT)로 전역·지역 계획, costmap, 복구 동작 | 목표 자세(액션) → `/cmd_vel` |
| 조작 | MoveIt 2 | 팔의 역기구학·충돌 검사·동작 계획·실행 | 목표 자세(액션) → 관절 궤적 |

L8.3 의 tf 트리와 겹쳐 보면 각 스택이 어느 변환을 발행하는지 보인다. 예를 들어 Nav2 는 스스로
위치를 추정하지 않고 `map → odom → base_link` 가 이미 있다고 가정한다.

### ros2_control 들여다보기

M3 에서 짠 PID·차동 구동 계산이 실제 로봇에서는 대개 ros2_control 안에 있다.

- **하드웨어 컴포넌트**(System·Sensor·Actuator 플러그인): 실제 장치와 읽기/쓰기를 한다. URDF 의
  `<ros2_control>` 태그에 어떤 관절이 어떤 명령·상태 인터페이스를 갖는지 적는다.
- **Resource Manager**: 하드웨어 인터페이스를 모아 컨트롤러에 빌려준다.
- **Controller Manager**: 제어 루프(read → update → write)를 돌리고 컨트롤러를 로드·전환한다.
- **컨트롤러**(pluginlib 플러그인): `diff_drive_controller`, `joint_trajectory_controller`,
  `joint_state_broadcaster` 등. `ros2 control list_controllers` 로 상태를 본다.

컨트롤러 설정은 YAML 이다(형태 예시).

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100
    diff_cont:
      type: diff_drive_controller/DiffDriveController
    joint_broad:
      type: joint_state_broadcaster/JointStateBroadcaster
```

배포판 차이가 큰 스택이므로 예제를 볼 때 Jazzy 판 문서인지 확인한다. Lyrical 에서는 Jazzy 때
deprecated 된 API 가 제거되어 옛 컨트롤러 예제가 실패할 수 있다.

### 개발 환경

- **네이티브 Ubuntu 24.04 + Jazzy 바이너리**: 가장 문제가 적다. 듀얼 부팅도 좋다.
- **Docker**: macOS·Windows 사용자나 여러 배포판을 오가는 사람에게 좋은 대안이다. 공식
  `ros:jazzy` 이미지 위에 Compose 로 개발 컨테이너를 만든다. GUI(RViz)는 X11/Wayland 전달이
  필요하다.
- **WSL2**: 동작은 하지만 네트워크·GUI 마찰 사례가 자주 보고된다.

어느 쪽이든 `~/.bashrc` 에 소싱 줄을 두되, 여러 워크스페이스를 섞을 때는 터미널마다 무엇을
소싱했는지 의식한다.

### 테스트와 CI

`colcon test` 는 각 패키지의 테스트(Python 은 pytest, 기본 생성되는 flake8·pep257 린트 포함)를
실행하고 `colcon test-result --verbose` 가 결과를 모은다. 같은 명령을 `ros:jazzy` 컨테이너 안에서
돌리면 그대로 CI 작업이 된다. 내 PC 에서만 되는 코드를 막는 가장 싼 방법이다.

### 시뮬레이터 한 줄 소개

Gazebo(Jazzy 짝은 Harmonic, `ros_gz` 브리지), Webots, MuJoCo 가 대표적이다. 이 플랫폼은
시뮬레이터 실습을 다루지 않으므로 비교는 조사 보고서의 시뮬레이터 절을 참고한다.

## 예제

```bash
# 워크스페이스를 마운트한 Jazzy 컨테이너
docker run -it --rm -v ~/ros2_ws:/ros2_ws -w /ros2_ws ros:jazzy bash

# 컨테이너 안에서
source /opt/ros/jazzy/setup.bash
rosdep update && rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
colcon test --packages-select turtle_ctrl
colcon test-result --verbose
```

**연습 과제(exercise):** (1) L8.2 의 `turtle_ctrl` 패키지를 위 컨테이너에서 빌드·테스트하라.
(2) Docker 가이드를 따라 Compose 파일로 같은 환경을 재현하라. (3) 본문 스택 표에 "로봇이 거실
지도를 만들고 부엌까지 간다"는 시나리오의 데이터 흐름을 화살표로 그려라.

## 자가 점검 질문

1. Nav2 가 동작하려면 어떤 tf 변환과 토픽이 이미 있어야 하는가? 각각 어떤 스택이 제공하는가?
2. ros2_control 에서 Controller Manager 와 하드웨어 컴포넌트의 경계는 어디인가? 실제 모터를 바꾸면
   어느 쪽 코드를 고치는가?
3. 네이티브 설치 대신 Docker 를 고를 상황과, 그때 감수해야 할 불편 하나를 들어라.

## 이 단계 공부법

1. **지도 먼저:** 스택 표를 외우기보다 L8.3 의 tf 트리 그림 위에 겹쳐 그려 본다.
2. **ros2_control:** Getting Started 의 아키텍처 그림을 읽고, `ros2_control_demos` 의 example_1
   (RRBot) 파일 구성(`rrbot_controllers.yaml`, `rrbot.ros2_control.xacro`, `rrbot.launch.py`)을
   코드로 훑는다. 실행은 선택이다.
3. **환경:** 아직 ROS 2 가 없다면 Docker 가이드로 컨테이너부터 만든다. Discourse 스레드에서
   초보자가 막히는 지점을 미리 읽어 둔다.
4. **micro-ROS(선택):** 마이크로컨트롤러를 다룰 계획이 있다면 `micro_ros_setup` README 의 지원
   보드 목록만 확인해 둔다.

## 참고 자료

- ros2_control, Getting Started — <https://control.ros.org/rolling/doc/getting_started/getting_started.html>
- ros2_control_demos — <https://github.com/ros-controls/ros2_control_demos>
- Docker Docs, Introduction to ROS 2 Development with Docker — <https://docs.docker.com/guides/ros2/>
- ROS Discourse, What is the hardest part of learning ROS 2 as a beginner — <https://discourse.openrobotics.org/t/what-is-the-hardest-part-of-learning-ros-2-as-a-beginner/57917>
- micro-ROS, micro_ros_setup — <https://github.com/micro-ROS/micro_ros_setup>
