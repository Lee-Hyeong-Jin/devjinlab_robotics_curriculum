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

## 어디에 쓰는가

이동 로봇을 만든다면 바퀴 제어는 ros2_control, 위치 추정은 robot_localization 과 SLAM Toolbox,
주행은 Nav2 를 가져다 쓰고, 팔이라면 MoveIt 2 를 쓴다. 직접 짜는 부분은 그 사이를 잇는 설정과 내 로봇에만
있는 하드웨어 드라이버다. 어떤 스택이 어느 층을 맡고 무엇을 주고받는지 알아야 "이 문제는 누구의
문제인가"를 가릴 수 있다. 개발 환경은 그 스택들을 내 PC 와 CI 에서 같은 방식으로 돌리기 위한 것이다.

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

L8.4 의 tf 트리와 겹쳐 보면 각 스택이 어느 변환을 발행하는지 보인다. 예를 들어 Nav2 는 스스로
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

**ROS 2 설치가 필요한 곳부터 확인한다.** 이 코스에서 ROS 2 가 설치되어 있어야 할 수 있는 것은
M8 의 예제·연습과 캡스톤(M10)의 일부 과제뿐이다. M1–M7 과 M9 의 실행 예제와 연습 과제는 Python 과
NumPy·SciPy, 그리고 공식 문서를 읽는 것만으로 할 수 있다(M7 의 한 문항만 "설치했다면" 하는 선택
과제다). 설치가 막혀도 나머지 코스는 계속 나갈 수 있다.

- **네이티브 Ubuntu 24.04 + Jazzy 바이너리**: 가장 문제가 적다. 듀얼 부팅도 좋다.
- **Docker**: macOS·Windows 사용자나 여러 배포판을 오가는 사람에게 좋은 대안이다. 아래 레시피를 쓴다.
- **WSL2**: 동작은 하지만 네트워크·GUI 마찰 사례가 자주 보고된다.

**가장 작은 Docker 레시피.** 빈 폴더에 `ros2_ws/src` 폴더와 아래 `compose.yaml` 을 둔다
(2026-11-28 에 `ros:jazzy` 이미지, Ubuntu 24.04 기반으로 확인했다).

```yaml
services:
  ros:
    image: ros:jazzy
    volumes:
      - ./ros2_ws:/ros2_ws   # 내 PC 의 워크스페이스를 컨테이너에 연결
    working_dir: /ros2_ws
    command: sleep infinity  # 컨테이너를 켜 두고 터미널로 들어가 쓴다
```

```bash
docker compose up -d                     # 처음에는 이미지를 내려받는다(1 GB 남짓)
docker compose exec ros bash             # 터미널 1: 컨테이너 안으로
source /opt/ros/jazzy/setup.bash         # 들어갈 때마다 먼저
ros2 topic pub /chatter std_msgs/msg/String "{data: hello}"

docker compose exec ros bash             # 터미널 2: 같은 컨테이너로 한 번 더
source /opt/ros/jazzy/setup.bash
ros2 topic echo /chatter                 # "data: hello" 가 계속 찍히면 성공
```

두 터미널이 같은 컨테이너 안이므로 네트워크 설정 없이 통신한다. `ros:jazzy` 는 최소 구성(ros-base)
이라 turtlesim 과 demo 노드가 들어 있지 않다. 필요하면 컨테이너 안에서
`apt-get update && apt-get install -y ros-jazzy-turtlesim` 으로 더한다(컨테이너를 지우면 사라지므로
계속 쓸 것은 `Dockerfile` 에 적는다). 그 밖의 설정은 공식 Docker 가이드(참고 자료)를 따른다.

```hint
`ros2: command not found`
이 터미널에서 ROS 2 를 소싱하지 않았다. `docker compose exec` 로 연 셸은 매번 새 셸이다.

    source /opt/ros/jazzy/setup.bash

`echo $ROS_DISTRO` 가 `jazzy` 를 찍는데도 명령이 없다면 소싱이 빠진 것이 맞다(이 변수는 이미지가
미리 넣어 둔 값이라 소싱 여부를 알려 주지 않는다).
```

```hint
빌드한 내 패키지를 `ros2 run` 이 찾지 못한다 (`Package '...' not found`)
`colcon build` 뒤에 워크스페이스를 소싱하지 않았거나, 다른 워크스페이스를 소싱했다.

    source /opt/ros/jazzy/setup.bash      # 설치본(underlay) 먼저
    source /ros2_ws/install/setup.bash    # 그 위에 내 워크스페이스(overlay)

`echo $AMENT_PREFIX_PATH` 로 지금 셸이 어떤 경로를 보고 있는지 확인한다. 빌드한 터미널이 아니라
**새 터미널**에서 소싱하는 편이 안전하다.
```

```hint
다른 컨테이너·호스트·WSL2 의 노드가 `ros2 node list` 에 보이지 않는다
DDS 는 같은 네트워크 안에서 멀티캐스트로 서로를 찾는다. 컨테이너는 기본적으로 자기만의 가상
네트워크에 있으므로 밖의 노드와는 서로 찾지 못한다. 순서대로 확인한다.

1. 양쪽의 `ROS_DOMAIN_ID` 가 같은가(`echo $ROS_DOMAIN_ID`, 비어 있으면 0).
2. Linux 호스트라면 `compose.yaml` 의 서비스에 `network_mode: host` 를 넣는다. 노드는 보이는데
   데이터가 오지 않으면 `ipc: host` 도 넣는다(공유 메모리 전송 때문이다).
3. macOS·Windows 의 Docker Desktop 과 WSL2 기본 설정은 호스트 네트워크와 멀티캐스트를 그대로
   넘겨주지 않는다. 필요한 노드를 **같은 컨테이너(또는 같은 Compose 네트워크) 안에서** 함께 돌리는
   쪽이 가장 덜 막힌다.
4. `ros2 multicast receive` 와 `ros2 multicast send` 로 멀티캐스트가 통하는지 직접 본다.
```

```hint
RViz·rqt 같은 GUI 창이 뜨지 않는다 (`could not connect to display`)
컨테이너에는 화면이 없다. Linux(X11)에서는 서비스에 아래를 더하고 호스트에서 `xhost +local:docker`
를 한 번 실행한다.

    environment:
      - DISPLAY=${DISPLAY}
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix

Wayland·macOS·Windows 는 방법이 다르므로 공식 Docker 가이드를 본다. GUI 가 꼭 필요하지 않으면
rosbag2 로 기록해 브라우저의 Foxglove 로 여는 방법이 설정이 가장 적다.
```

**ROS 2 를 쓰지 않아도 되는 경우.** ROS 2 는 여러 프로세스·여러 컴퓨터·여러 사람이 만든 부품을
잇는 도구다. 마이크로컨트롤러 하나로 모터 두 개를 돌리는 라인 트레이서, 센서 한두 개를 읽는
실험, 이 코스의 NumPy 예제에는 필요 없고 오히려 설치와 빌드가 일을 늘린다. Nav2·MoveIt 2 같은
스택을 쓰려 할 때, 센서 드라이버를 남이 만든 것으로 쓰려 할 때, 기록·시각화 도구(rosbag2, RViz)가
필요해질 때가 ROS 2 를 들일 시점이다.

어느 쪽이든 `~/.bashrc` 에 소싱 줄을 두되, 여러 워크스페이스를 섞을 때는 터미널마다 무엇을
소싱했는지 의식한다.

### 테스트와 CI

`colcon test` 는 각 패키지의 테스트(Python 은 pytest, 기본 생성되는 flake8·pep257 린트 포함)를
실행하고 `colcon test-result --verbose` 가 결과를 모은다. 같은 명령을 `ros:jazzy` 컨테이너 안에서
돌리면 그대로 CI 작업이 된다. 내 PC 에서만 되는 코드를 막는 가장 싼 방법이다.

### 시뮬레이터 고르기

하드웨어에 돈을 쓰기 전에 시뮬레이터에서 먼저 해 보라는 것이 흔한 조언이다. 이 플랫폼은 시뮬레이터
설치와 실습을 다루지 않는다. 아래 표에서 고르고, 설치는 각 공식 문서를 따른다.

| 시뮬레이터 | 잘하는 것 | 필요한 하드웨어 | 라이선스 | 공식 문서 |
|---|---|---|---|---|
| Gazebo (Jazzy 짝은 Harmonic) | ROS 2 와 가장 긴밀하다(`ros_gz` 브리지). 센서(LiDAR·카메라·IMU)를 단 이동 로봇, Nav2·`ros2_control` 연동 시험 | 일반 PC. GPU 는 카메라·LiDAR 렌더링에 도움 | Apache-2.0 | [gazebosim.org/docs](https://gazebosim.org/docs) |
| Webots | 설치 한 번에 로봇 모델·예제 월드·편집기가 함께 온다. Windows·macOS·Linux 지원이라 처음 써 보기 쉽다 | 일반 PC | Apache-2.0 | [cyberbotics.com/doc](https://cyberbotics.com/doc/guide/index) |
| MuJoCo | 접촉이 있는 동역학을 빠르고 정확하게 계산한다. 제어·강화학습 연구(M9)의 표준. ROS 없이 Python 만으로 쓴다 | 노트북 CPU 로 충분 | Apache-2.0 | [mujoco.readthedocs.io](https://mujoco.readthedocs.io/) |
| Isaac Sim | 사실적인 렌더링과 GPU 병렬 시뮬레이션. 카메라 기반 인식과 대규모 강화학습(Isaac Lab)·합성 데이터 | **NVIDIA RTX GPU 필수**, 메모리·디스크 요구가 크다 | 소스 공개. 구성 요소별 약관은 저장소에서 확인 | [docs.isaacsim.omniverse.nvidia.com](https://docs.isaacsim.omniverse.nvidia.com/) |

고르는 기준은 셋이다. ROS 2 스택(Nav2, `ros2_control`)을 시험하려면 Gazebo, 제어·강화학습 알고리즘을
빠르게 돌리려면 MuJoCo, 처음이고 OS 를 가리고 싶지 않으면 Webots. Isaac Sim 은 RTX GPU 가 있고
카메라 렌더링이나 수천 개 환경의 병렬 학습이 필요할 때 고른다.

시뮬레이터에서 된 것이 실제 로봇에서 그대로 되지는 않는다. 마찰, 지연, 센서 잡음, 배터리가 다르다.
그 차이를 줄이는 방법은 M9 의 sim-to-real 레슨에서, 차이를 직접 겪는 방법은 M11 의 선택 레슨에서 다룬다.

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

**연습 과제(exercise):** (1) L8.3 의 `turtle_ctrl` 패키지를 위 컨테이너에서 빌드·테스트하라.
(2) 본문의 `compose.yaml` 로 같은 환경을 띄우고 `/chatter` 확인 명령을 통과시켜라. (3) 본문 스택 표에 "로봇이 거실
지도를 만들고 부엌까지 간다"는 시나리오의 데이터 흐름을 화살표로 그려라.

## 자가 점검 질문

1. Nav2 가 동작하려면 어떤 tf 변환과 토픽이 이미 있어야 하는가? 각각 어떤 스택이 제공하는가?
2. ros2_control 에서 Controller Manager 와 하드웨어 컴포넌트의 경계는 어디인가? 실제 모터를 바꾸면
   어느 쪽 코드를 고치는가?
3. 네이티브 설치 대신 Docker 를 고를 상황과, 그때 감수해야 할 불편 하나를 들어라.

## 확인 퀴즈

`rc quiz m8-stacks-dev-environment` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m8-stacks-dev-environment-quiz
questions:
  - id: q1
    type: truefalse
    prompt: 'Nav2 는 스스로 로봇의 위치를 추정하므로 SLAM 이나 AMCL 없이도 지도 위에서 주행할 수 있다.'
    answer: false
    explanation: 'Nav2 는 `map → odom → base_link` 변환과 `/scan`·`/map` 이 이미 있다고 가정한다. `odom → base_link` 는 오도메트리(또는 robot_localization), `map → odom` 은 SLAM Toolbox·AMCL 이 제공한다. 위치 추정이 없으면 Nav2 는 동작하지 않는다.'
    concept: { front: 'Nav2 의 전제 조건', back: '`map → odom → base_link` tf 와 `/scan`·`/map` 이 먼저 있어야 한다 — 위치 추정은 다른 스택의 일' }
  - id: q2
    type: single
    prompt: '실제 모터 드라이버를 다른 제품으로 교체했다. ros2_control 에서 고쳐야 하는 쪽은?'
    choices:
      - '컨트롤러(예: `diff_drive_controller`) 코드'
      - '하드웨어 컴포넌트(System/Actuator 플러그인)'
      - 'Controller Manager 의 제어 루프'
      - 'Nav2 의 행동 트리'
    answer: 1
    explanation: '하드웨어 컴포넌트가 실제 장치와 read/write 를 담당하고, 컨트롤러는 표준 명령·상태 인터페이스만 보고 동작한다. 그래서 장치를 바꿔도 컨트롤러와 상위 스택은 그대로 두고 하드웨어 컴포넌트만 교체하면 된다. 이것이 하드웨어 추상화의 목적이다.'
    concept: { front: 'ros2_control 의 경계', back: '하드웨어 컴포넌트 = 장치별 read/write, 컨트롤러 = 장치와 무관한 제어 로직' }
  - id: q3
    type: single
    prompt: 'ROS 2 개발 환경으로 가장 마찰이 적은 선택은?'
    choices:
      - '네이티브 Ubuntu 24.04 + Jazzy 바이너리'
      - 'WSL2'
      - '소스에서 전부 빌드'
      - '가상 머신 안의 다른 배포판'
    answer: 0
    explanation: '문서와 패키지가 전제하는 조합이므로 문제가 가장 적다. macOS·Windows 사용자나 여러 배포판을 오가야 하면 공식 `ros:jazzy` 이미지 기반 Docker 가 좋은 대안이고, WSL2 는 동작하지만 네트워크·GUI 마찰 보고가 잦다.'
```

## 이 단계 공부법

1. **지도 먼저:** 스택 표를 외우기보다 L8.4 의 tf 트리 그림 위에 겹쳐 그려 본다.
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
