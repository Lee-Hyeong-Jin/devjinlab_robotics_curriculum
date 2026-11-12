---
id: m10-system-architecture-requirements
lang: en
title: "Robot software architecture and system design (requirements → components → interfaces)"
summary: Learn the top-down design process of writing the robot you want as measurable requirements and decomposing those into components (nodes) and interfaces (topics, services, actions, rates, frames). Check a requirements traceability table in Python to find unowned requirements and broken interfaces.
objectives:
  - Write functional requirements and non-functional requirements (performance, safety, cost, maintainability) as verifiable statements with numbers.
  - Split requirements into components across the sensing, estimation, planning, control, and hardware layers, and define the interface at each boundary (message type, rate, frame_id).
  - Explain which stage of the robot development process - concept, design, prototype, pilot, production - a capstone corresponds to.
tags: [system-design, requirements, architecture, interfaces, ros2, capstone]
---

# Robot software architecture and system design

Across M1-M8 we built the parts one at a time: kinematics, PID, sensor models, Kalman filters,
SLAM, path planning, ROS 2 nodes. But gathering parts does not make a robot. Where real projects
fail is usually not the algorithms but the **boundaries**: frames that do not match, rates that
do not line up, requirements nobody owns. This lesson covers how, before starting the capstone,
to settle on paper what you will build, from which parts, and under which promises (interfaces).

## Concepts

### Requirements: it is only a requirement if you can verify it

"A robot that moves intelligently around the house" is a wish, not a requirement. A requirement
must be **a statement you can judge pass or fail**.

- **Functional requirements (FR):** "The robot drives autonomously to a designated goal point on a
  previously built map."
- **Non-functional requirements (NFR):** "Arrival error at the goal point within 0.15 m, succeeding
  at least 8 times out of 10"; "maximum speed 0.3 m/s"; "stop if commands are interrupted for more
  than 0.5 s"; "total parts cost at most 600,000 won"; "builds within 30 minutes on a fresh PC."

The NFRs are the inputs to the following lessons. Speed and error decide hardware selection
(L10.2), the stop condition decides the safety design (L10.3), and the build time decides CI and
containers (L10.4).

### Components: one responsibility, one component

Place the requirements on the stack map of M8: the hardware layer (motor driver, lidar driver) →
control (ros2_control's diff_drive_controller, M3) → estimation (odometry, EKF, SLAM, M5) →
planning (Nav2's global and local planners, M6) → mission (behavior tree, M6). The criterion for
a good decomposition is simple: **each requirement is owned by exactly one component, and each
component exists because of at least one requirement.**

### Interfaces: contracts between components

In ROS 2 an interface is more than a message type. The contract has to contain all of this:

- the name and the communication mechanism (topic, service, action), and the message type
- the rate (Hz) and tolerable latency, and the QoS (reliability, history depth)
- the frame (`frame_id`) and the units (REP 103: m, rad, right-handed)
- the behavior on failure (what the receiver does when messages stop)

When a repository is split into description, bringup, base, control, slam, and navigation
packages, as Andino is, the package boundaries are the interface boundaries.

### The capstone within the development process

The industrial cycle runs concept → design → prototype (Proto) → pilot → production. A personal
capstone usually goes as far as **concept, design, and Proto**, and with good documentation and
reproducibility you can get a taste of Pilot (repeated trials) as well. Matching your scope to
that stage is the first design decision.

## Key checklist

- [ ] Every requirement has an ID (FR-1, NFR-3, …) and a measurement method.
- [ ] Every requirement is assigned to exactly one component.
- [ ] Every topic has at least one publisher and at least one subscriber (no dangling edges).
- [ ] Every interface records its rate, its frame_id, and its behavior on interruption.
- [ ] The tf tree (map → odom → base_link → sensors) is drawn as a single figure.
- [ ] There is a list of what you will not do (out of scope).

## Example

Writing the requirements traceability table and the interface table as data lets you automate the
design review in code.

```python
from dataclasses import dataclass, field


@dataclass
class Component:
    name: str
    satisfies: list[str]
    publishes: dict[str, float] = field(default_factory=dict)  # topic -> Hz
    subscribes: dict[str, float] = field(default_factory=dict)  # topic -> minimum Hz required


requirements = [
    "FR-1 autonomous navigation",
    "FR-2 mapping",
    "NFR-1 stop if commands are interrupted for 0.5 s",
    "NFR-2 error within 0.15 m",
]
components = [
    Component("lidar_driver", [], publishes={"/scan": 10.0}),
    Component(
        "base_controller",
        ["NFR-1 stop if commands are interrupted for 0.5 s"],
        {"/odom": 50.0},
        {"/cmd_vel": 10.0},
    ),
    Component("slam_toolbox", ["FR-2 mapping"], {"/map": 1.0}, {"/scan": 5.0, "/odom": 20.0}),
    Component(
        "nav2",
        ["FR-1 autonomous navigation"],
        {"/cmd_vel": 20.0},
        {"/map": 0.5, "/scan": 5.0, "/odom": 20.0},
    ),
]

owners = {r: [c.name for c in components if r in c.satisfies] for r in requirements}
for req, who in owners.items():
    if len(who) != 1:
        print(f"[requirement] {req}: owning component {who or 'none'}")
for c in components:
    if not c.satisfies:
        print(
            f"[component] {c.name}: no reason to exist (no requirement) - mark it as a support component"
        )

rates = {t: hz for c in components for t, hz in c.publishes.items()}
for c in components:
    for topic, need in c.subscribes.items():
        have = rates.get(topic)
        if have is None:
            print(f"[interface] no publisher for {topic}, which {c.name} subscribes to")
        elif have < need:
            print(f"[interface] {topic}: published at {have} Hz < {need} Hz required by {c.name}")
```

Running it produces two lines: "NFR-2 error within 0.15 m" has no owner, and `lidar_driver`
exists without a requirement. For NFR-2, add the measurement procedure (an evaluation script) as
the owning component; for the driver, record that it supports FR-2.

**Exercise:** For one of your capstone candidates, write at least 3 FRs and 4 NFRs, build the
component and interface tables in the form above, and make them pass the checker. Submit the node
graph diagram (hand-drawn is fine) and the tf tree alongside.

## Self-check questions

1. What numbers and measurement method do you need to turn "the robot moves fast" into a verifiable NFR?
2. What goes wrong in integration testing when two components share responsibility for one requirement?
3. What accident can happen if the `/cmd_vel` interface contract omits "behavior on interruption"?

## How to study this stage

1. **Course (first):** watch the Inflearn "robot development process" course (45 minutes) for the
   concept-to-production flow and the deliverables of each stage.
2. **Code reading:** place the package list of the Andino repository back onto the stack map of
   the M8 lesson and write one line on which requirement each package exists for.
3. **Document cross-check:** use the order of the Nav2 First-Time Robot Setup Guide as the
   checklist for your interface table.
4. **Problems:** take the quiz in the Korean original
   (`rc quiz m10-system-architecture-requirements`), then do the exercise.
5. **Scoping:** using the project time estimates of the Coursera roadmap, trim your requirements
   list until it fits in six weeks (8-10 hours a week).

## References

- jelly, "현직자가 알려주는 로봇 실무 개발 프로세스: 로봇 양산 사이클", Inflearn (in Korean) - <https://www.inflearn.com/course/robot-development-pr>
- Coursera, "Robotics Learning Roadmap (2026)" - <https://www.coursera.org/resources/robotics-learning-roadmap>
- Nav2 Documentation - <https://docs.nav2.org/rolling/index.html>
- Ekumen, Andino - <https://github.com/Ekumen-OS/andino>
