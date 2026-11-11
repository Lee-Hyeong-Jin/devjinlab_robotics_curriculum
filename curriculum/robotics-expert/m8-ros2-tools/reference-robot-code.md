---
id: m8-reference-robot-code
title: 레퍼런스 로봇 코드 읽기
summary: 오픈소스 차동 구동 로봇 Andino 와 TurtleBot 의 저장소를 예로, ROS 2 로봇 프로젝트가 description·bringup·base·control·slam·navigation 패키지로 나뉘는 방식을 읽고, launch 파일에서 출발해 노드·파라미터·tf 로 따라 내려가는 코드 읽기 순서를 익힌다.
objectives:
  - 레퍼런스 로봇 저장소의 패키지들을 L8.4 스택 지도(하드웨어·제어·추정·계획) 위에 배치할 수 있다.
  - bringup launch 파일에서 출발해 실행되는 노드, 불러오는 YAML 파라미터, 발행되는 tf 를 추적할 수 있다.
  - 실행 중인 시스템을 ros2 CLI 로 조사해 코드에서 읽은 구조와 대조할 수 있다.
prerequisites: [m8-stacks-dev-environment, m3-differential-drive]
difficulty: 3
estimated_minutes: 120
tags: [ros2, code-reading, andino, turtlebot, reference-robot, architecture]
activities:
  - id: m8-reference-robot-code-reading
    kind: reading
    title: 본문과 Andino 저장소 구조 읽기
    estimated_minutes: 50
  - id: m8-reference-robot-code-quiz
    kind: quiz
    title: 패키지 역할 맞히기 퀴즈
    estimated_minutes: 15
  - id: m8-reference-robot-code-exercise
    kind: exercise
    title: bringup 에서 /cmd_vel 까지 데이터 흐름 추적 노트
    estimated_minutes: 55
resources:
  - title: Andino (Ekumen-OS)
    url: https://github.com/Ekumen-OS/andino
    kind: other
    note: andino_base(ros2_control HW 인터페이스)·andino_control·andino_slam·andino_navigation 패키지 구조.
  - title: TurtleBot3 e-Manual (ROBOTIS)
    url: https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/
    kind: article
    note: ROS 2 설정·SLAM·Navigation 예제(Humble/Jazzy). 한국어 docs.robotis.com/ko 이전 중.
  - title: TurtleBot 4 User Manual — Tutorials
    url: https://turtlebot.github.io/turtlebot4-user-manual/tutorials/
    kind: article
    note: Driving·First node(Python)·Generating a map·Navigation 튜토리얼, Jazzy 지원.
  - title: Mastering ROS 2 for Robotics Programming, 4th ed. (Joseph & Cacace)
    url: https://www.packtpub.com/en-US/product/mastering-ros-2-for-robotics-programming-9781836209003
    kind: book
    note: ros2 controllers·Nav2·MoveIt 2 장(Jazzy), 유료.
---

# 레퍼런스 로봇 코드 읽기

지금까지 개념과 도구를 조각으로 봤다. 실제 로봇 프로젝트는 이 조각들이 수십 개 패키지로 묶인
형태다. 이 레슨의 목표는 처음 보는 ROS 2 저장소를 열었을 때 30분 안에 "무엇이 어디서 실행되고
데이터가 어떻게 흐르는지" 지도를 그리는 것이다. 주 교재는 Ekumen 의 **Andino** 다. 라즈베리 파이와
마이크로컨트롤러로 만든 완전 오픈소스 차동 구동 로봇이고, Humble·Jazzy 를 지원하며, 패키지가
코스 모듈과 거의 1:1로 대응한다.

## 개념

### 관례적인 패키지 분할

ROS 2 로봇 저장소는 대체로 같은 방식으로 나뉜다. Andino 를 예로 들면:

| 패키지 | 층 | 들어 있는 것 |
|---|---|---|
| `andino_description` | 모델 | URDF/xacro, 메시(L8.3) |
| `andino_firmware` | 하드웨어 | 마이크로컨트롤러 펌웨어(모터 PWM·엔코더 읽기) |
| `andino_base` | 제어 | ros2_control 하드웨어 인터페이스(시리얼로 펌웨어와 통신) |
| `andino_control` | 제어 | diff drive 컨트롤러 + joint state broadcaster 설정·launch |
| `andino_bringup` | 통합 | 로봇 전체를 띄우는 최상위 launch |
| `andino_slam` | 지도 | SLAM Toolbox 설정 |
| `andino_navigation` | 이동 | Nav2 설정·launch |
| `andino_gz` 등 | 시뮬레이션 | Gazebo 등 시뮬레이터 연동(이 코스 범위 밖) |

`description` 은 하드웨어와 시뮬레이션이 공유하고, `bringup` 이 나머지를 조립한다는 점이 핵심이다.
TurtleBot 3·4 저장소도 이름만 다를 뿐 같은 구조다.

### 읽는 순서: 위에서 아래로

1. **README** — 지원 배포판, 의존성, 실행 명령. 배포판이 Jazzy 인지 먼저 확인한다.
2. **bringup launch** — 어떤 launch 를 포함(include)하고 어떤 노드를 띄우는지. 조건부 인자
   (`use_sim_time`, `rviz` 등)도 여기서 본다.
3. **config YAML** — 컨트롤러의 바퀴 간격·반지름, Nav2·SLAM 파라미터. M3 의 차동 구동 식에
   들어가던 $L$, $r$ 이 여기 있다.
4. **description** — 프레임 이름과 센서 장착 위치. tf 트리를 예측한다.
5. **C++/Python 소스** — 마지막에, 필요한 노드만. 대부분의 로봇 패키지는 코드보다 설정과
   launch 가 많다.

### 코드와 실행 결과 대조

읽은 내용은 가설이다. 실행 중인 시스템(실물, 또는 다른 사람이 녹화한 bag)에서 ros2 CLI 로 확인한다.

```bash
ros2 launch andino_bringup andino_robot.launch.py   # README 의 실행 명령을 따른다
ros2 node list
ros2 node info /controller_manager
ros2 control list_controllers
ros2 control list_hardware_interfaces
ros2 topic info /cmd_vel -v
ros2 param dump /diff_controller
ros2 run tf2_tools view_frames
```

launch 파일 이름과 노드 이름은 버전에 따라 다를 수 있으니 저장소 README 를 기준으로 바꿔 쓴다.
하드웨어가 없으면 이 단계는 읽기만 해도 된다. 중요한 것은 "명령 하나로 어느 가설을 확인하는가"를
아는 것이다.

### 데이터 흐름 한 줄 요약

텔레옵이나 Nav2 가 `/cmd_vel`(Twist) 발행 → `diff_drive_controller` 가 M3 의 역기구학으로 좌우 바퀴
속도 명령 계산 → `andino_base` 하드웨어 인터페이스가 시리얼로 펌웨어에 전달 → 펌웨어가 모터 구동,
엔코더 값 반환 → 컨트롤러가 순기구학으로 `/odom` 과 `odom → base_link` tf 발행. 이 한 줄을 스스로
그릴 수 있으면 M5·M6 에서 각 층을 바꿔 끼우는 실습이 쉬워진다.

## 예제

`andino_control` 의 컨트롤러 YAML 에서 다음과 같은 항목을 찾아 M3 개념과 대응시킨다(필드 이름은
`diff_drive_controller` 문서 기준, 값은 저장소에서 확인).

```yaml
diff_controller:
  ros__parameters:
    left_wheel_names: ["left_wheel_joint"]
    right_wheel_names: ["right_wheel_joint"]
    wheel_separation: 0.137   # M3 의 L (예시 값)
    wheel_radius: 0.033       # M3 의 r (예시 값)
    odom_frame_id: odom
    base_frame_id: base_link
```

**연습 과제(exercise):** Andino 저장소를 클론하고 노트 한 장을 작성하라. (1) 패키지별 역할을
본문 표처럼 한 줄씩 적는다. (2) bringup launch 에서 시작해 포함되는 launch 와 노드를 트리로 그린다.
(3) 컨트롤러 YAML 의 실제 바퀴 간격·반지름을 찾아 M3 의 차동 구동 식에 넣고, 바퀴 각속도 1 rad/s
일 때 로봇의 선속도를 계산한다. (4) TurtleBot 3 또는 4 의 저장소에서 같은 역할의 패키지를 찾아
이름을 대응시킨다.

## 자가 점검 질문

1. `description` 패키지를 하드웨어 bringup 과 시뮬레이션이 함께 쓰는 이유는 무엇인가?
2. 바퀴 반지름 값이 실제보다 10% 크게 설정되어 있다면 `/odom` 에는 어떤 오차가 생기는가?
3. 처음 보는 저장소에서 소스 코드보다 launch 와 YAML 을 먼저 읽는 것이 효율적인 이유를 설명하라.

## 확인 퀴즈

`rc quiz m8-reference-robot-code` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m8-reference-robot-code-quiz
questions:
  - id: q1
    type: single
    prompt: '`<robot>_description` 패키지를 하드웨어 bringup 과 시뮬레이션이 함께 쓰는 이유는?'
    choices:
      - '패키지 수를 줄이기 위해'
      - '로봇의 기하·프레임 정의를 한 곳에 두어 실물과 시뮬레이션의 tf 트리가 어긋나지 않게 하려고'
      - '시뮬레이터가 URDF 만 읽을 수 있기 때문'
      - 'URDF 는 빌드 시간에 생성되기 때문'
    answer: 1
    explanation: 'URDF 가 프레임 이름, 링크 길이, 센서 장착 위치를 정의한다. 실물과 시뮬레이션이 같은 description 을 쓰면 같은 tf 트리가 만들어져, 시뮬레이션에서 검증한 코드가 실물에서도 같은 프레임을 가정할 수 있다. 사본을 두면 둘이 조용히 어긋난다.'
    concept: { front: 'description 패키지를 공유하는 이유', back: '기하·프레임 정의의 단일 출처 — 실물과 시뮬레이션의 tf 트리가 일치한다' }
  - id: q2
    type: single
    prompt: '설정된 바퀴 반지름이 실제보다 10% 크면 `/odom` 에 어떤 오차가 생기는가?'
    choices:
      - '회전 각도만 10% 작아진다'
      - '이동 거리가 실제보다 약 10% 크게 적분된다'
      - '오차가 생기지 않는다(엔코더가 보정한다)'
      - '위치는 맞고 속도만 틀리다'
    answer: 1
    explanation: '$v = r(\omega_R + \omega_L)/2$ 에서 $r$ 이 10% 크면 같은 엔코더 값에 대해 선속도와 적분 거리가 약 10% 과대 추정된다(1 m 를 갔는데 1.1 m 로 기록). M3 의 오도메트리 식에 들어가는 $r$, $L$ 이 config YAML 에 있으니 실측과 맞추는 것이 중요하다.'
    concept: { front: '바퀴 반지름 설정 오차의 영향', back: '$v = r(\omega_R+\omega_L)/2$ — $r$ 이 10% 크면 이동 거리가 약 10% 과대 추정' }
  - id: q3
    type: truefalse
    prompt: '처음 보는 로봇 저장소는 C++/Python 소스부터 읽는 것이 전체 구조를 파악하는 가장 빠른 길이다.'
    answer: false
    explanation: '대부분의 로봇 패키지는 코드보다 launch 와 YAML 이 많다. README → bringup launch → config YAML → description 순으로 읽으면 어떤 노드가 어떤 설정으로 뜨는지, tf 트리가 어떻게 생길지 먼저 보인다. 소스는 그 가설을 확인할 때 필요한 노드만 읽으면 된다.'
```

## 이 단계 공부법

1. **저장소 먼저:** Andino README 와 패키지 목록을 읽고, 본문 표를 직접 채워 본다.
2. **추적:** 연습 과제 (2)의 launch 트리를 손으로 그린다. 막히면 L8.2 의 launch 절로 돌아간다.
3. **비교:** TurtleBot 3 e-Manual 이나 TurtleBot 4 튜토리얼에서 같은 층(SLAM·Navigation)이
   어떻게 설정되는지 훑는다. TurtleBot 3 e-Manual 은 ROBOTIS Docs 로 이전 중이니 배포판 표기를 확인한다.
4. **심화(선택, 유료):** *Mastering ROS 2* 의 ros2 controllers·Nav2 장을 읽으면 M6·M7 준비가 된다.

## 참고 자료

- Ekumen-OS, Andino — <https://github.com/Ekumen-OS/andino>
- ROBOTIS, TurtleBot3 e-Manual — <https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/>
- TurtleBot 4 User Manual, Tutorials — <https://turtlebot.github.io/turtlebot4-user-manual/tutorials/>
- Lentin Joseph, Jonathan Cacace, *Mastering ROS 2 for Robotics Programming*, 4th ed., Packt —
  <https://www.packtpub.com/en-US/product/mastering-ros-2-for-robotics-programming-9781836209003>
