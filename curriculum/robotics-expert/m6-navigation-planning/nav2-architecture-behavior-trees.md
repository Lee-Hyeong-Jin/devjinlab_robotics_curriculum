---
id: m6-nav2-architecture-behavior-trees
title: "Nav2 아키텍처와 행동 트리 읽기"
summary: 앞 레슨의 플래너·비용 지도·컨트롤러·스무더가 Nav2 에서 각각 어떤 서버와 플러그인이 되는지, 그리고 bt_navigator 가 행동 트리(BT)로 이들을 어떻게 엮어 재계획과 회복 동작을 하는지 읽는다. 최소 BT 를 파이썬으로 구현해 RecoveryNode 의 동작을 확인한다.
objectives:
  - Nav2 의 주요 서버(bt_navigator, planner·controller·smoother·behavior 서버)와 라이프사이클 관리자의 역할, 그리고 tf·지도·오도메트리 입력을 설명할 수 있다.
  - 행동 트리의 tick 과 Sequence·Fallback·Recovery·RoundRobin 노드의 의미를 설명하고, 기본 navigate_to_pose BT XML 을 읽을 수 있다.
  - 내비게이션 실패 상황에서 BT 의 회복 흐름을 따라가며 어느 서버·파라미터를 볼지 판단할 수 있다.
prerequisites:
  - m8-tf2-urdf-visualization
  - m5-occupancy-grid-scan-matching
  - m6-local-planning-dwa-mppi
  - m6-path-smoothing-trajectory
difficulty: 3
estimated_minutes: 130
tags: [nav2, behavior-tree, bt-navigator, ros2, architecture, recovery]
activities:
  - id: m6-nav2-architecture-behavior-trees-reading
    kind: reading
    title: 본문과 Nav2 Navigation Concepts·Behavior Trees 읽기
    estimated_minutes: 50
  - id: m6-nav2-architecture-behavior-trees-quiz
    kind: quiz
    title: Nav2 서버와 BT 노드 퀴즈
    estimated_minutes: 20
  - id: m6-nav2-architecture-behavior-trees-exercise
    kind: exercise
    title: 최소 행동 트리 구현과 기본 BT XML 읽기
    estimated_minutes: 60
resources:
  - title: "Nav2 Documentation"
    url: https://docs.nav2.org/rolling/index.html
    kind: article
    note: Navigation Concepts, Behavior Trees, First-Time Robot Setup Guide, Configuration/Tuning Guide.
  - title: "A Concise Introduction to Robot Programming with ROS 2, 2nd ed. (Martín Rico)"
    url: https://www.routledge.com/A-Concise-Introduction-to-Robot-Programming-with-ROS-2/MartinRico/p/book/9781032851488
    kind: book
    note: Behavior Trees·Nav2 장.
  - title: "Behavior Trees in Robotics and AI (Colledanchise, Ögren)"
    kind: book
    note: 무료 arXiv PDF 로 공개된 BT 교재(링크 없음). Ch. 1–3 기본 노드와 설계 패턴.
  - title: "자율주행 로봇을 위한 ROS 2 & SLAM & Nav2 한번에 끝내기 (패스트캠퍼스)"
    url: https://fastcampus.co.kr/data_online_selfdriving
    kind: course
    note: Part 4 Nav2, Part 5 심화(BT·멀티로봇·Keepout). Humble 기준, 유료(한국어).
  - title: "Andino (Ekumen-OS)"
    url: https://github.com/Ekumen-OS/andino
    kind: other
    note: andino_navigation 패키지의 Nav2 파라미터·launch 읽기(Jazzy).
---

# Nav2 아키텍처와 행동 트리 읽기

이 모듈에서 만든 부품, 즉 비용 지도(레슨 3), 전역 플래너(레슨 1–3), 지역 컨트롤러(레슨 4),
스무더(레슨 5)는 Nav2 에서 각각 독립된 서버의 플러그인이다. 이 레슨은 이들을 하나의 "목표 자세로
가라" 동작으로 묶는 구조를 읽는다. 핵심은 **bt_navigator** 와 그 안의 **행동 트리(behavior tree, BT)** 다.

## 개념

### 서버 구성

- **bt_navigator:** `NavigateToPose` 같은 액션 목표를 받아 BT 를 실행한다.
- **planner_server:** 전역 비용 지도와 플래너 플러그인(NavFn, Smac, Theta*)으로 경로를 계산한다.
- **controller_server:** 지역 비용 지도와 컨트롤러 플러그인(DWB, MPPI, Regulated Pure Pursuit)으로 `cmd_vel` 을 낸다.
- **smoother_server:** 경로를 평활화한다.
- **behavior_server:** Spin, BackUp, Wait 같은 회복 동작을 수행한다.
- **lifecycle_manager:** 각 서버를 라이프사이클 노드로 정해진 순서에 따라 configure·activate 한다.

입력은 M5·M8 에서 본 것들이다. 지도 서버(또는 SLAM Toolbox)가 `map` 을, AMCL 이나 SLAM 이
`map→odom` tf 를, 오도메트리(robot_localization 융합)가 `odom→base_link` tf 를, URDF 와
robot_state_publisher 가 센서 프레임을 제공한다. tf 트리가 끊기면 비용 지도가 갱신되지 않아 내비게이션
전체가 멈춘다.

### 행동 트리

BT 는 루트에서 아래로 **tick** 을 보내고, 각 노드는 SUCCESS·FAILURE·RUNNING 중 하나를 돌려준다.

- **Sequence:** 자식을 차례로 실행하고 하나라도 실패하면 실패한다.
- **Fallback:** 자식을 차례로 시도해 하나라도 성공하면 성공한다.
- **RecoveryNode(Nav2):** 첫 자식이 실패하면 둘째 자식(회복)을 실행하고 첫 자식을 정해진 횟수만큼 재시도한다.
- **RoundRobin(Nav2):** 실패할 때마다 다음 자식으로 넘어가 회복 동작을 돌아가며 시도한다.
- **RateController** 같은 데코레이터는 자식의 tick 빈도를 제한한다(예: 1 Hz 재계획).

상태 기계와 달리 전이를 일일이 적지 않고 트리 구조로 우선순위와 재시도를 표현하므로, XML 만 바꿔
동작을 고칠 수 있다. 기본 트리 `navigate_to_pose_w_replanning_and_recovery.xml` 의 뼈대는 다음과 같다(단순화).

```xml
<RecoveryNode number_of_retries="6" name="NavigateRecovery">
  <PipelineSequence name="NavigateWithReplanning">
    <RateController hz="1.0">
      <ComputePathToPose goal="{goal}" path="{path}"/>
    </RateController>
    <FollowPath path="{path}"/>
  </PipelineSequence>
  <RoundRobin name="RecoveryActions">
    <ClearEntireCostmap name="ClearLocalCostmap"/>
    <Spin spin_dist="1.57"/>
    <Wait wait_duration="5"/>
    <BackUp backup_dist="0.30"/>
  </RoundRobin>
</RecoveryNode>
```

설치된 기본 트리는 아래처럼 찾아 직접 읽을 수 있다.

```bash
ls "$(ros2 pkg prefix nav2_bt_navigator)/share/nav2_bt_navigator/behavior_trees/"
```

## 핵심 수식

BT 의 합성 규칙(자식 상태 $s_1, \dots, s_n$, 실행은 왼쪽부터):

$$\text{Sequence} = \begin{cases}\text{FAILURE} & \exists i: s_i = \text{FAILURE} \\ \text{SUCCESS} & \forall i: s_i = \text{SUCCESS}\end{cases}\qquad \text{Fallback} = \begin{cases}\text{SUCCESS} & \exists i: s_i = \text{SUCCESS} \\ \text{FAILURE} & \forall i: s_i = \text{FAILURE}\end{cases}$$

## 예제

RUNNING 을 생략한 동기식 최소 BT 다. 지역 비용 지도에 남은 '유령' 장애물 때문에 FollowPath 가
실패하고, RoundRobin 이 Spin → Wait → ClearCostmaps 순서로 회복을 시도한다.

```python
SUCCESS, FAILURE = "SUCCESS", "FAILURE"
log = []


class Action:
    def __init__(self, name, fn):
        self.name, self.fn = name, fn

    def tick(self, bb):
        status = self.fn(bb)
        log.append(f"{self.name}:{status[0]}")
        return status


class Sequence:  # 자식이 모두 성공해야 성공, 하나라도 실패하면 즉시 실패
    def __init__(self, *children):
        self.children = children

    def tick(self, bb):
        for child in self.children:
            if child.tick(bb) == FAILURE:
                return FAILURE
        return SUCCESS


class RoundRobin:  # 실패할 때마다 다음 회복 행동을 차례로 하나씩 시도
    def __init__(self, *children):
        self.children, self.i = children, 0

    def tick(self, bb):
        child = self.children[self.i % len(self.children)]
        self.i += 1
        return child.tick(bb)


class Recovery:  # 첫 자식이 실패하면 둘째(회복)를 실행하고 첫 자식을 재시도
    def __init__(self, main, recovery, retries):
        self.main, self.recovery, self.retries = main, recovery, retries

    def tick(self, bb):
        for _ in range(self.retries + 1):
            if self.main.tick(bb) == SUCCESS:
                return SUCCESS
            if self.recovery.tick(bb) == FAILURE:
                return FAILURE
        return FAILURE


def compute_path(bb):
    return SUCCESS if bb["goal_reachable"] else FAILURE


def follow_path(bb):  # 지역 비용 지도에 남은 '유령' 장애물 때문에 막힌다
    return FAILURE if bb["ghost_obstacle"] else SUCCESS


def clear_costmaps(bb):
    bb["ghost_obstacle"] = False  # 센서가 다시 보고 빈 칸으로 지운다
    return SUCCESS


navigate = Recovery(
    Sequence(Action("ComputePathToPose", compute_path), Action("FollowPath", follow_path)),
    RoundRobin(
        Action("Spin", lambda bb: SUCCESS),
        Action("Wait", lambda bb: SUCCESS),
        Action("ClearCostmaps", clear_costmaps),
    ),
    retries=6,
)
blackboard = {"ghost_obstacle": True, "goal_reachable": True}
print("결과:", navigate.tick(blackboard))
print("실행 순서:", " → ".join(log))
```

세 번째 회복(ClearCostmaps)에서 유령 장애물이 지워지고 네 번째 시도에 성공한다.

**연습 과제(exercise):** (1) `goal_reachable` 을 False 로 두고 6 회 재시도 후 FAILURE 가 되는 과정을
따라가라. (2) RoundRobin 의 순서를 ClearCostmaps 먼저로 바꾸면 실행 순서가 어떻게 줄어드는가? 기본
트리가 비용 지도 지우기를 앞에 두는 이유와 연결하라. (3) Nav2 기본 XML 을 열어 위 단순화본에 없는
노드(GoalUpdated, ReactiveFallback 등)를 찾아 역할을 한 줄씩 적어라.

## 자가 점검 질문

1. `map→odom` tf 가 발행되지 않으면 Nav2 의 어느 부분이 어떻게 실패하는가?
2. PipelineSequence 와 RateController 를 함께 쓰면 "주행 중 1 Hz 재계획"이 어떻게 구현되는가?
3. 로봇이 좁은 문 앞에서 계속 Spin 만 반복한다면 BT·비용 지도·컨트롤러 중 무엇부터 확인하겠는가?

## 이 단계 공부법

1. **문서(먼저):** Nav2 Navigation Concepts 에서 서버 구성도와 Behavior Trees 절을 읽는다.
2. **본문 + 예제:** 최소 BT 를 돌리고 연습 과제를 한 뒤, 기본 XML 과 노드별로 대응시킨다.
3. **코드 읽기:** Andino 의 `andino_navigation` 파라미터 파일에서 플래너·컨트롤러·비용 지도 층 설정을 찾아
   이 모듈의 레슨과 연결한다.
4. **심화(선택):** Martín Rico 의 Behavior Trees·Nav2 장, Colledanchise·Ögren 교재로 BT 설계 패턴을
   익히고, 한국어 강의가 필요하면 패스트캠퍼스 강의 Part 4–5 를 본다.

## 참고 자료

- Nav2 Documentation — <https://docs.nav2.org/rolling/index.html>
- Francisco Martín Rico, *A Concise Introduction to Robot Programming with ROS 2*, 2nd ed., CRC Press —
  <https://www.routledge.com/A-Concise-Introduction-to-Robot-Programming-with-ROS-2/MartinRico/p/book/9781032851488>
- Michele Colledanchise, Petter Ögren, *Behavior Trees in Robotics and AI* (링크 없음)
- 패스트캠퍼스, 자율주행 로봇을 위한 ROS 2 & SLAM & Nav2 한번에 끝내기 — <https://fastcampus.co.kr/data_online_selfdriving>
- Ekumen-OS, Andino — <https://github.com/Ekumen-OS/andino>
