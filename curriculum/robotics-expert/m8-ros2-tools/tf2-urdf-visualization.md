---
id: m8-tf2-urdf-visualization
title: "tf2·URDF·RViz·rosbag2(MCAP)·Foxglove"
summary: M1 의 좌표 변환이 ROS 2 에서 tf2 프레임 트리(map·odom·base_link·센서)로 어떻게 구현되는지, URDF 가 그 트리의 고정 부분을 어떻게 정의하는지 보고, RViz·rqt·ros2 CLI 로 시각화·디버깅하며 rosbag2(MCAP)로 기록·재생하고 Foxglove 로 다시 보는 흐름을 익힌다.
objectives:
  - map·odom·base_link·센서 프레임의 관계와 REP 관례를 설명하고, tf2 로 두 프레임 사이 변환을 조회할 수 있다.
  - URDF 의 link·joint 와 robot_state_publisher 가 tf 트리를 만드는 과정을 설명할 수 있다.
  - RViz·rqt·ros2 CLI·rosbag2·Foxglove 중 디버깅 상황에 맞는 도구를 골라 쓸 수 있다.
prerequisites: [m8-nodes-topics-launch, m1-coordinate-transforms]
difficulty: 3
estimated_minutes: 120
tags: [ros2, tf2, urdf, rviz, rqt, rosbag2, mcap, foxglove, debugging]
activities:
  - id: m8-tf2-urdf-visualization-reading
    kind: reading
    title: 본문과 Intermediate tf2·URDF 자습서 읽기
    estimated_minutes: 50
  - id: m8-tf2-urdf-visualization-quiz
    kind: quiz
    title: 프레임 트리와 도구 선택 퀴즈
    estimated_minutes: 15
  - id: m8-tf2-urdf-visualization-exercise
    kind: exercise
    title: turtlesim tf 데모 기록·재생과 시각화
    estimated_minutes: 55
resources:
  - title: ROS 2 Jazzy Tutorials
    url: https://docs.ros.org/en/jazzy/Tutorials.html
    kind: article
    note: Intermediate tf2·URDF·RViz, Beginner "Recording and playing back data", "Using rqt_console".
  - title: ROS 2 for Beginners Level 2 (TF, URDF, RViz, Gazebo) (Renard, Udemy)
    url: https://roboticsbackend.com/courses/
    kind: course
    note: 약 14시간, 평점 4.8(1,818개), 유료.
  - title: Foxglove ROS 2 docs
    url: https://docs.foxglove.dev/docs/connecting-to-data/frameworks/ros2
    kind: article
    note: Foxglove Bridge·MCAP(Iron 이후 rosbag2 기본), 무료 플랜 3석.
  - title: Visualizing ROS 2 data with Foxglove (ROS 2 docs)
    url: https://docs.ros.org/en/lyrical/Related-Projects/Visualizing-ROS-2-Data-With-Foxglove.html
    kind: article
    note: 공식 문서의 Foxglove 연결 안내(Lyrical 판이지만 Jazzy 에도 같은 흐름).
---

# tf2·URDF·RViz·rosbag2(MCAP)·Foxglove

M1 에서 동차 변환 $T_{AB}$ 를 곱해 좌표계를 옮기는 법을 배웠다. 로봇에는 이런 좌표계가 수십 개
있고, 일부는 움직인다(바퀴, 관절, 로봇 자체). tf2 는 이 변환들을 **시간이 붙은 트리**로 관리해
"0.3 초 전 LiDAR 점을 지금 map 좌표로" 같은 질의에 답한다. 이 레슨은 tf2 와 URDF, 그리고 그
결과를 눈으로 보고 기록하는 도구들을 묶어 다룬다. M5 의 센서 융합·SLAM 레슨이 바로 이 레슨을
선수로 요구한다.

## 핵심 개념

### 프레임 트리

모바일 로봇의 표준 트리는 `map → odom → base_link → (laser, imu, camera_link …)` 다(REP 105).

- `odom → base_link`: 오도메트리(M3 의 차동 구동 적분)가 발행. 연속적이지만 시간이 갈수록 흘러간다.
- `map → odom`: 위치 추정(SLAM·AMCL)이 발행. 흘러감을 보정하느라 순간적으로 점프할 수 있다.
- `base_link → laser`: 센서 장착 위치. 움직이지 않으므로 **static** 변환이다.

각 변환은 정확히 하나의 부모를 갖고, 한 변환은 한 노드만 발행해야 한다. 두 노드가 같은
`odom → base_link` 를 발행하면 로봇이 RViz 에서 떨리는 전형적인 버그가 생긴다.

### tf2 조회와 시간

`lookup_transform(target, source, time)` 은 source 프레임의 자세를 target 프레임에서 표현한
변환을 돌려준다. `Time()`(0)은 "가장 최근 값"이다. 특정 시각을 물었는데 버퍼에 아직 그 시각의
데이터가 없으면 외삽 예외가 나므로, 센서 처리 코드는 예외를 잡거나 짧게 기다린다. 시뮬레이션이나
bag 재생 때는 `use_sim_time` 을 켜 `/clock` 시간을 따르게 한다.

```python
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener


class FrameReader(Node):
    def __init__(self):
        super().__init__("frame_reader")
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.create_timer(1.0, self.on_timer)

    def on_timer(self):
        try:
            t = self.buffer.lookup_transform("odom", "base_link", Time())
        except TransformException as e:
            self.get_logger().warn(f"tf 아직 없음: {e}")
            return
        p = t.transform.translation
        self.get_logger().info(f"base_link in odom: x={p.x:.2f}, y={p.y:.2f}")
```

### URDF 와 robot_state_publisher

URDF 는 로봇을 `link`(강체, 형상·관성)와 `joint`(부모·자식, 원점, 축, 종류)로 기술하는 XML 이다.
M2 의 DH 파라미터가 하던 일을 joint 의 `origin` 과 `axis` 가 한다. `robot_state_publisher` 는
URDF 와 `/joint_states` 를 받아 고정 관절은 static tf, 회전 관절은 순기구학으로 계산한 tf 를
발행한다. 실무에서는 xacro 매크로로 URDF 를 생성하는 경우가 많다.

```xml
<joint name="laser_joint" type="fixed">
  <parent link="base_link"/>
  <child link="laser"/>
  <origin xyz="0.10 0 0.20" rpy="0 0 0"/>
</joint>
```

### 시각화·디버깅 도구

- **ros2 CLI** — `topic hz/echo/info -v`(QoS 확인), `node info`, `param dump`, `ros2 doctor`. 가장 먼저 쓴다.
- **rqt** — `rqt_graph`(연결 관계), `rqt_console`(로그 필터), `rqt_plot`(값 그래프), `rqt_tf_tree`.
- **RViz2** — 3D 장면. Fixed Frame 을 고르고 TF·LaserScan·PointCloud2·RobotModel·Path 를 겹쳐 본다.
  "아무것도 안 보인다"면 Fixed Frame 과 tf 연결부터 의심한다.
- **rosbag2** — `ros2 bag record/play/info`. Iron 이후 기본 저장 형식은 MCAP 이다. 같은 데이터를
  반복 재생하며 알고리즘을 고치는 것이 하드웨어 없이 개발하는 핵심 방법이다.
- **Foxglove** — 웹/데스크톱 시각화 도구. Foxglove Bridge 로 실시간 연결하거나 `.mcap` 파일을
  바로 연다. RViz 를 먼저 익히고 Foxglove 를 두 번째로 익히는 순서를 권한다.

## 예제

turtlesim tf2 데모를 기록하고 다시 본다.

```bash
sudo apt install ros-jazzy-turtle-tf2-py ros-jazzy-tf2-tools
ros2 launch turtle_tf2_py turtle_tf2_demo.launch.py   # 터미널 1
ros2 run turtlesim turtle_teleop_key                  # 터미널 2
ros2 run tf2_tools view_frames                        # frames_*.pdf 생성
ros2 run tf2_ros tf2_echo world turtle2
ros2 bag record -o turtle_run /tf /turtle1/pose        # Ctrl+C 로 종료
ros2 bag info turtle_run
ros2 bag play turtle_run
```

**연습 과제(exercise):** (1) `view_frames` 결과에서 부모·자식 관계를 그려라. (2) 기록한 bag 을
재생하면서 RViz2 에서 Fixed Frame 을 `world` 로 두고 TF 표시를 추가하라. (3) 같은 `.mcap` 파일을
Foxglove 에서 열어 `/turtle1/pose` 의 x, y 를 Plot 패널로 그려라.

## 자가 점검 질문

1. `odom → base_link` 와 `map → odom` 을 서로 다른 노드가 발행하는 이유는 무엇인가?
2. URDF 의 fixed joint 와 revolute joint 는 tf 로 각각 어떻게 발행되는가?
3. RViz 에 LaserScan 이 안 보일 때 확인할 순서를 CLI·rqt·RViz 도구로 세 단계 이상 써라.

## 이 단계 공부법

1. **공식 자습서(먼저):** *Intermediate* 의 tf2 시리즈(Introducing tf2 → static broadcaster →
   broadcaster → listener)와 URDF 시리즈를 읽고, *Beginner* 의 rosbag·rqt_console 을 따라 한다.
2. **본문 + 예제:** M1 레슨의 변환 행렬 곱을 `tf2_echo` 출력과 대응시켜 본다.
3. **보강(선택, 유료):** 영상이 필요하면 Renard Level 2 의 TF·URDF·RViz 파트를 본다(Gazebo 파트는 건너뛰어도 된다).
4. **도구 확장:** RViz 가 익숙해진 뒤 Foxglove 문서로 MCAP 파일 보기를 익힌다. 무료 플랜 한도는
   변할 수 있으니 가입 전에 확인한다.

## 참고 자료

- ROS 2 Jazzy Tutorials, Intermediate tf2·URDF / Beginner rosbag·rqt_console — <https://docs.ros.org/en/jazzy/Tutorials.html>
- Edouard Renard, ROS 2 for Beginners Level 2 (TF, URDF, RViz, Gazebo) — <https://roboticsbackend.com/courses/>
- Foxglove, ROS 2 docs — <https://docs.foxglove.dev/docs/connecting-to-data/frameworks/ros2>
- ROS 2 Documentation, Visualizing ROS 2 data with Foxglove — <https://docs.ros.org/en/lyrical/Related-Projects/Visualizing-ROS-2-Data-With-Foxglove.html>
- Wim Meeussen, REP 105 "Coordinate Frames for Mobile Platforms"
