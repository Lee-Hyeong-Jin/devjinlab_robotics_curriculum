---
id: m6-nav2-architecture-behavior-trees
lang: en
title: "Nav2 architecture and reading behavior trees"
summary: Read which server and plugin each part from the previous lessons - planner, costmap, controller, smoother - becomes in Nav2, and how bt_navigator ties them together with a behavior tree (BT) to replan and recover. Implement a minimal BT in Python to see how a RecoveryNode behaves.
objectives:
  - Explain the roles of Nav2's main servers (bt_navigator, the planner, controller, smoother, and behavior servers) and the lifecycle manager, along with its tf, map, and odometry inputs.
  - Explain the tick of a behavior tree and the meaning of Sequence, Fallback, Recovery, and RoundRobin nodes, and read the default navigate_to_pose BT XML.
  - Follow the BT's recovery flow in a navigation failure and decide which server and parameters to look at.
tags: [nav2, behavior-tree, bt-navigator, ros2, architecture, recovery]
---

# Nav2 architecture and reading behavior trees

The parts built in this module - the costmap (lesson 3), the global planner (lessons 1-3), the
local controller (lesson 4), and the smoother (lesson 5) - are each a plugin of a separate server
in Nav2. This lesson reads the structure that binds them into a single "drive to the goal pose"
behavior. At its heart are **bt_navigator** and the **behavior tree (BT)** inside it.

## Concepts

### The server layout

- **bt_navigator:** receives an action goal such as `NavigateToPose` and runs the BT.
- **planner_server:** computes a path from the global costmap and a planner plugin (NavFn, Smac, Theta*).
- **controller_server:** produces `cmd_vel` from the local costmap and a controller plugin (DWB, MPPI, Regulated Pure Pursuit).
- **smoother_server:** smooths the path.
- **behavior_server:** performs recovery behaviors such as Spin, BackUp, and Wait.
- **lifecycle_manager:** configures and activates each server as a lifecycle node in a set order.

The inputs are the ones seen in M5 and M8. The map server (or SLAM Toolbox) provides `map`, AMCL
or SLAM the `map→odom` tf, odometry (fused by robot_localization) the `odom→base_link` tf, and
the URDF with robot_state_publisher the sensor frames. If the tf tree breaks, the costmaps stop
updating and navigation as a whole halts.

### Behavior trees

A BT sends a **tick** down from the root, and each node returns one of SUCCESS, FAILURE, or
RUNNING.

- **Sequence:** runs its children in order and fails if any one of them fails.
- **Fallback:** tries its children in order and succeeds if any one of them succeeds.
- **RecoveryNode (Nav2):** if the first child fails, runs the second child (the recovery) and
  retries the first a set number of times.
- **RoundRobin (Nav2):** moves to the next child on each failure, trying the recovery behaviors in turn.
- Decorators such as **RateController** limit how often a child is ticked (replanning at 1 Hz, say).

Unlike a state machine, it expresses priority and retries through tree structure instead of
enumerating transitions, so behavior can be changed by editing the XML alone. The skeleton of the
default tree `navigate_to_pose_w_replanning_and_recovery.xml` is as follows (simplified).

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

You can find and read the installed default trees like this:

```bash
ls "$(ros2 pkg prefix nav2_bt_navigator)/share/nav2_bt_navigator/behavior_trees/"
```

## Key formulas

The composition rules of a BT (child states $s_1, \dots, s_n$, executed left to right):

$$\text{Sequence} = \begin{cases}\text{FAILURE} & \exists i: s_i = \text{FAILURE} \\ \text{SUCCESS} & \forall i: s_i = \text{SUCCESS}\end{cases}\qquad \text{Fallback} = \begin{cases}\text{SUCCESS} & \exists i: s_i = \text{SUCCESS} \\ \text{FAILURE} & \forall i: s_i = \text{FAILURE}\end{cases}$$

## Example

A minimal synchronous BT with RUNNING left out. FollowPath fails because of a "ghost" obstacle
lingering in the local costmap, and RoundRobin attempts recovery in the order Spin → Wait →
ClearCostmaps.

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


class Sequence:  # succeeds only if every child succeeds; fails immediately on any failure
    def __init__(self, *children):
        self.children = children

    def tick(self, bb):
        for child in self.children:
            if child.tick(bb) == FAILURE:
                return FAILURE
        return SUCCESS


class RoundRobin:  # on each failure, try the next recovery behavior in turn
    def __init__(self, *children):
        self.children, self.i = children, 0

    def tick(self, bb):
        child = self.children[self.i % len(self.children)]
        self.i += 1
        return child.tick(bb)


class Recovery:  # if the first child fails, run the second (recovery) and retry the first
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


def follow_path(bb):  # blocked by a "ghost" obstacle left in the local costmap
    return FAILURE if bb["ghost_obstacle"] else SUCCESS


def clear_costmaps(bb):
    bb["ghost_obstacle"] = False  # the sensor looks again and clears the cell
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
print("result:", navigate.tick(blackboard))
print("execution order:", " -> ".join(log))
```

The third recovery (ClearCostmaps) removes the ghost obstacle, and the fourth attempt succeeds.

**Exercise:** (1) Set `goal_reachable` to False and follow the process by which it becomes FAILURE
after six retries. (2) How does the execution order shorten if you put ClearCostmaps first in the
RoundRobin? Connect that to why the default tree puts costmap clearing first. (3) Open the Nav2
default XML, find the nodes missing from the simplification above (GoalUpdated, ReactiveFallback,
and others), and write one line on each of their roles.

## Self-check questions

1. If the `map→odom` tf is not published, which part of Nav2 fails and how?
2. How do PipelineSequence and RateController together implement "replan at 1 Hz while driving"?
3. If the robot keeps spinning in front of a narrow doorway, which would you check first: the BT, the costmap, or the controller?

## How to study this stage

1. **Documentation (first):** read the server diagram and the Behavior Trees section of Nav2's
   Navigation Concepts.
2. **This lesson plus the example:** run the minimal BT, do the exercises, then map it node by node
   onto the default XML.
3. **Code reading:** find the planner, controller, and costmap layer settings in Andino's
   `andino_navigation` parameter file and connect them to this module's lessons.
4. **Problems:** take the quiz in the Korean original
   (`rc quiz m6-nav2-architecture-behavior-trees`).
5. **Depth (optional):** learn BT design patterns from Martín Rico's Behavior Trees and Nav2
   chapters and the Colledanchise and Ögren textbook; if you want a Korean-language course, see
   Parts 4-5 of the Fastcampus course.

## References

- Nav2 Documentation - <https://docs.nav2.org/rolling/index.html>
- Francisco Martín Rico, *A Concise Introduction to Robot Programming with ROS 2*, 2nd ed., CRC Press -
  <https://www.routledge.com/A-Concise-Introduction-to-Robot-Programming-with-ROS-2/MartinRico/p/book/9781032851488>
- Michele Colledanchise, Petter Ögren, *Behavior Trees in Robotics and AI* (no link)
- Fastcampus, "자율주행 로봇을 위한 ROS 2 & SLAM & Nav2 한번에 끝내기" (in Korean) - <https://fastcampus.co.kr/data_online_selfdriving>
- Ekumen-OS, Andino - <https://github.com/Ekumen-OS/andino>
