---
id: m8-nodes-topics-launch
title: "노드·토픽·서비스·액션·파라미터·launch 프로그래밍"
summary: colcon 워크스페이스와 ament_python 패키지 구조를 익히고, rclpy 로 발행·구독·파라미터를 쓰는 노드를 읽고 쓰며, 서비스·액션 클라이언트의 흐름과 Python launch 파일로 여러 노드를 한 번에 띄우는 방법을 정리한다.
objectives:
  - colcon 워크스페이스(src·build·install·log)와 소싱(underlay·overlay)의 관계를 설명하고 빌드·실행 순서를 쓸 수 있다.
  - rclpy 노드에서 구독·타이머·발행·파라미터가 어떻게 연결되는지 읽고, M3 의 P 제어기를 노드로 옮길 수 있다.
  - 서비스와 액션의 호출 흐름 차이를 설명하고, launch 파일로 노드·파라미터·리매핑을 묶을 수 있다.
prerequisites: [m8-ros2-concepts-distros, m3-pid-control]
difficulty: 3
estimated_minutes: 120
tags: [ros2, rclpy, colcon, workspace, launch, parameters, actions]
activities:
  - id: m8-nodes-topics-launch-reading
    kind: reading
    title: 본문과 Beginner Client libraries 자습서 읽기
    estimated_minutes: 50
  - id: m8-nodes-topics-launch-quiz
    kind: quiz
    title: 워크스페이스·소싱·콜백 퀴즈
    estimated_minutes: 15
  - id: m8-nodes-topics-launch-exercise
    kind: exercise
    title: turtlesim P 제어 노드와 launch 파일 작성
    estimated_minutes: 55
resources:
  - title: ROS 2 Jazzy Tutorials
    url: https://docs.ros.org/en/jazzy/Tutorials.html
    kind: article
    note: "Beginner: Client libraries(colcon·워크스페이스·pub/sub·srv/cli·커스텀 인터페이스·파라미터·ros2doctor) + Intermediate 액션·launch."
  - title: ROS 2 from Scratch (Renard, Packt)
    url: https://www.packtpub.com/en-ro/product/ros-2-from-scratch-9781835881415
    kind: book
    note: 전권(Python 우선, Jazzy/Ubuntu 24.04), 유료.
  - title: ROS 2 for Beginners (ROS Jazzy) Level 1 (Renard, Udemy)
    url: https://www.udemy.com/course/ros2-for-beginners/
    kind: course
    note: 13시간 13분, 유료. 한국어 대안은 [R2R] 무작정 따라하는 ROS2 입문과정 https://www.udemy.com/course/r2r_ros2_bgn/ (Humble, Jazzy 호환 표기).
---

# 노드·토픽·서비스·액션·파라미터·launch 프로그래밍

앞 레슨에서 CLI 로 그래프를 관찰했다면, 이번에는 그래프의 한 조각을 직접 만든다. 목표는 rclpy
API 를 외우는 것이 아니라, 남이 쓴 ROS 2 패키지를 열었을 때 "어디서 구독하고, 어디서 계산하고,
어디서 발행하는지"를 바로 찾는 눈을 기르는 것이다. L8.5 의 레퍼런스 로봇 코드 읽기가 이 눈을 쓴다.

## 개념

### 워크스페이스와 소싱

colcon 워크스페이스는 `src/` 에 패키지 소스를 두고 `colcon build` 로 `build/`, `install/`, `log/`
를 만든다. `/opt/ros/jazzy` 가 **underlay**, 내 워크스페이스가 그 위의 **overlay** 다. 새 터미널마다
underlay 를 소싱한 뒤 `install/setup.bash` 를 소싱해야 내 패키지가 보인다. 커뮤니티 경험담에서 가장
흔한 시간 낭비가 "빌드는 됐는데 `Package not found`" 류의 소싱 문제이니, 일부러 소싱을 빼 보고
오류 메시지를 익혀 두면 좋다.

Python 패키지(`ament_python`)의 뼈대는 다음과 같다. `package.xml` 은 의존성, `setup.py` 의
`entry_points` 는 `ros2 run` 으로 부를 실행 이름을 정한다.

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python --dependencies rclpy geometry_msgs turtlesim \
  turtle_ctrl
cd ~/ros2_ws && colcon build --symlink-install
source install/setup.bash
ros2 run turtle_ctrl goto_node
```

### 노드 = 콜백의 모음

rclpy 노드는 구독 콜백, 타이머 콜백, 서비스 콜백을 등록하고 `rclpy.spin()` 이 이벤트가 올 때마다
그것들을 호출한다. 콜백 안에서 오래 막히면(긴 `sleep`, 동기 서비스 호출) 다른 콜백도 멈춘다.
그래서 "최신 센서 값을 구독 콜백에서 저장 → 타이머 콜백에서 제어 계산·발행" 구조가 흔하다.

### 서비스와 액션

서비스 클라이언트는 `call_async()` 로 요청을 보내고 Future 로 응답을 받는다. 액션은 내부적으로
목표 전송·취소 서비스와 피드백·상태 토픽의 묶음이다. 클라이언트는 목표를 보내고, 수락 여부를 받고,
진행 중 피드백을 받다가, 최종 결과를 받는다. Nav2 의 `NavigateToPose`, MoveIt 2 의 동작 실행이
모두 액션이다.

### launch

실제 로봇은 노드가 수십 개다. Python launch 파일은 어떤 노드를 어떤 파라미터·리매핑·네임스페이스로
띄울지 기술한다. 파라미터는 보통 YAML 파일로 따로 두고 launch 에서 불러온다.

## 예제

M3 의 P 제어를 turtlesim 에 붙인 노드다. `/turtle1/pose` 를 구독하고 목표점을 향해 `/turtle1/cmd_vel`
을 발행한다. 목표와 이득은 파라미터다.

```python
import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtlesim.msg import Pose


class GoTo(Node):
    def __init__(self):
        super().__init__("goto_node")
        self.declare_parameter("goal", [8.0, 8.0])
        self.declare_parameter("kp_lin", 1.0)
        self.declare_parameter("kp_ang", 4.0)
        self.pose = None
        self.create_subscription(Pose, "/turtle1/pose", self.on_pose, 10)
        self.pub = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.create_timer(0.05, self.on_timer)  # 20 Hz 제어 주기

    def on_pose(self, msg):
        self.pose = msg  # 최신 값만 저장

    def on_timer(self):
        if self.pose is None:
            return
        gx, gy = self.get_parameter("goal").value
        dx, dy = gx - self.pose.x, gy - self.pose.y
        dist = math.hypot(dx, dy)
        err = math.atan2(dy, dx) - self.pose.theta
        err = math.atan2(math.sin(err), math.cos(err))  # [-pi, pi]로 감기
        cmd = Twist()
        if dist > 0.05:
            cmd.linear.x = self.get_parameter("kp_lin").value * dist
            cmd.angular.z = self.get_parameter("kp_ang").value * err
        self.pub.publish(cmd)


def main():
    rclpy.init()
    rclpy.spin(GoTo())
    rclpy.shutdown()
```

launch 파일(`launch/goto.launch.py`)로 시뮬레이터와 제어 노드를 함께 띄운다.

```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(package="turtlesim", executable="turtlesim_node"),
            Node(
                package="turtle_ctrl",
                executable="goto_node",
                parameters=[{"goal": [2.0, 9.0], "kp_ang": 6.0}],
            ),
        ]
    )
```

실행 중에 `ros2 param set /goto_node goal "[3.0, 3.0]"` 으로 목표를 바꾸면 거북이가 방향을 튼다.

**연습 과제(exercise):** (1) 위 패키지를 만들어 빌드하고 launch 로 실행하라. (2) 새 터미널에서
`install/setup.bash` 소싱을 빼고 `ros2 run turtle_ctrl goto_node` 를 실행해 오류를 기록하라.
(3) 거북이가 목표에 도착하면 `/clear` 서비스를 `call_async()` 로 호출하도록 고쳐라.

## 자가 점검 질문

1. `colcon build` 는 성공했는데 `ros2 run` 이 패키지를 못 찾는다. 가장 먼저 확인할 두 가지는?
2. 예제에서 제어 계산을 구독 콜백이 아니라 타이머 콜백에 둔 이유는 무엇인가?
3. 서비스 대신 액션을 써야 하는 상황을 예로 들고, 액션 클라이언트가 받는 세 종류의 응답을 써라.

## 이 단계 공부법

1. **공식 자습서(먼저):** *Beginner: Client libraries* 의 colcon → 워크스페이스 → 패키지 →
   Python pub/sub → 서비스 → 파라미터 순서로 따라 하고, *Intermediate* 의 액션과 launch 를 읽는다.
2. **본문 + 예제:** 예제 노드를 직접 타이핑해 실행하고, 구독·타이머·발행이 어디서 연결되는지
   주석을 달아 본다.
3. **보강(선택, 유료):** 서술형 설명이 필요하면 *ROS 2 from Scratch* 나 Renard 의 Udemy Level 1 을
   병행한다. Humble 기준 한국어 강의를 쓸 때는 배포판 이름만 바꿔 읽는다.
4. **연습:** 소싱 고장 연습(과제 2)을 꼭 한다. 이후 모든 ROS 2 레슨의 디버깅 시간을 줄여 준다.

## 참고 자료

- ROS 2 Jazzy Tutorials, Beginner: Client libraries / Intermediate — <https://docs.ros.org/en/jazzy/Tutorials.html>
- Edouard Renard, *ROS 2 from Scratch*, Packt — <https://www.packtpub.com/en-ro/product/ros-2-from-scratch-9781835881415>
- Edouard Renard, ROS 2 for Beginners (ROS Jazzy) Level 1, Udemy — <https://www.udemy.com/course/ros2-for-beginners/>
- [R2R] 무작정 따라하는 ROS2 입문과정, Udemy (Humble) — <https://www.udemy.com/course/r2r_ros2_bgn/>
