---
id: m10-realtime-safety-reliability
lang: en
title: "Real-time behavior, safety, and reliability (watchdogs, failsafes, functional safety in outline)"
summary: Learn what "real-time" means in robot software (deadlines and jitter), how to design watchdogs and failsafes against interrupted commands, sensor failures, and overcurrent, where the hardware emergency stop belongs, and - at an outline level - the way of thinking that functional safety standards require (hazard analysis → safety functions → verification).
objectives:
  - Distinguish soft from hard real-time, and measure a control loop's period, latency, and jitter to compare against the requirements.
  - Design and implement a command timeout watchdog and the state machine that moves into a safe state (stop, slow down).
  - Enumerate failure modes and tabulate the detection method and safe reaction for each (a simplified FMEA).
tags: [real-time, safety, watchdog, failsafe, reliability, fmea, e-stop]
---

# Real-time behavior, safety, and reliability

The robot in the demo video always moves well. The quality of a real robot shows **when something
goes wrong**. What does the robot do when the Wi-Fi drops, when the lidar cable comes loose, when
a node dies on an exception? This lesson covers how to answer that question by design. The
capstone rubric (L10.5) also scores safety separately.

## Concepts

### Real-time means "on time," not "fast"

A real-time system is one that **meets its deadlines**. A 50 Hz control loop must run every
20 ms, and the wobble in the actual period is called **jitter**.

- **Hard real-time:** missing a deadline even once is a failure (motor current control, airbags).
  The domain of MCUs and RTOSes.
- **Soft real-time:** occasional lateness only degrades performance (the Nav2 local planner,
  SLAM). The domain of ordinary Linux plus ROS 2.

Hence the division of labor of L10.2. Work whose deadline is under 1 ms and whose misses are
dangerous (PWM, current limiting, the final watchdog) goes on the MCU; judgment on the scale of
tens of milliseconds goes on the SBC. ros2_control is a structure that runs a read → update →
write loop at a fixed rate on the SBC, and a PREEMPT_RT kernel reduces jitter - but it still does
not replace an MCU.

### Watchdogs and failsafes

A **watchdog** is a monitor that forces a safe action when an "I am alive" signal (a heartbeat)
fails to arrive within a set time.

- Software watchdog: the base controller sets speed to 0 if it has not received `/cmd_vel` for
  more than 0.5 s.
- Hardware watchdog: the MCU drops the motor driver's enable pin if it stops receiving serial
  packets from the SBC.
- The MCU's own watchdog timer: resets the MCU if the firmware hangs.

A **failsafe** is the property that, on failure, the system moves into a predetermined **safe
state**. For a mobile robot the safe state is usually "stop plus brake"; for a manipulator it is
"hold the current pose" or "release torque with a drop prevented" - it differs by platform. You
cannot reach a safe state without detecting the failure, so design **detection → reaction** as a
pair.

### The emergency stop (E-stop) is not software

A physical E-stop must work even when all the software has stopped, so it **cuts the motor power
circuit directly**. A software stop button (a topic) is a convenience; it does not replace an
E-stop.

### The way of thinking of functional safety (in outline)

Standards such as IEC 61508 (general electrical and electronic safety-related systems),
ISO 10218 (industrial robots), and ISO 13482 (personal care robots) all require the same flow:
**hazard analysis → defining safety functions → determining the required integrity level →
verification and documentation**. A capstone will not be certified, but merely imitating this
flow with a simplified FMEA (failure mode and effects analysis) table raises design quality
noticeably.

## Key checklist

- [ ] The target period and the measured maximum jitter of each control loop are recorded.
- [ ] A command timeout watchdog exists on both the SBC and the MCU.
- [ ] A physical E-stop cuts the motor power directly.
- [ ] The failure mode table lists the detection method, the safe reaction, and the recovery condition.
- [ ] The robot does not resume motion automatically from a safe state (a person resumes it explicitly).

## Example

Implement a command timeout watchdog as a state machine and run scenarios against a fake clock.

```python
from enum import Enum


class State(Enum):
    RUN = "RUN"
    SAFE_STOP = "SAFE_STOP"


class CmdWatchdog:
    def __init__(self, timeout_s=0.5, max_speed=0.3):
        self.timeout_s, self.max_speed = timeout_s, max_speed
        self.state, self.last_cmd_t, self.cmd = State.SAFE_STOP, None, 0.0

    def on_cmd(self, t, v):
        self.last_cmd_t, self.cmd = t, max(-self.max_speed, min(self.max_speed, v))

    def reset(self, t):  # only an explicit human reset returns it to RUN
        if self.last_cmd_t is not None and t - self.last_cmd_t < self.timeout_s:
            self.state = State.RUN

    def output(self, t):
        if self.state is State.RUN and (
            self.last_cmd_t is None or t - self.last_cmd_t > self.timeout_s
        ):
            self.state = State.SAFE_STOP  # detection -> safe state
        return self.cmd if self.state is State.RUN else 0.0


wd = CmdWatchdog()
events = {0.00: ("cmd", 0.5), 0.10: ("reset", None), 0.40: ("cmd", 0.2), 1.50: ("cmd", 0.2)}
for k in range(0, 200, 10):  # 0-2 s at 100 ms steps (a coarse sampling of a 50 Hz loop)
    t = k / 100
    kind, v = events.get(t, (None, None))
    if kind == "cmd":
        wd.on_cmd(t, v)
    elif kind == "reset":
        wd.reset(t)
    out = wd.output(t)
    print(f"t={t:4.2f}s  state={wd.state.value:9s}  output={out:4.2f} m/s")
```

The 0.5 m/s command is clipped to 0.3 m/s, and more than 0.5 s after the last command at 0.4 s it
drops into SAFE_STOP at 1.0 s. Even when a command arrives again at 1.5 s, it does not move
without a `reset`. That is the "no automatic resumption" rule.

**Exercise:** (1) Wrap the class above in an rclpy node that subscribes to `/cmd_vel` and outputs
on a 50 Hz timer. (2) Build an FMEA table with detection, reaction, and recovery columns for at
least six failure modes of your capstone robot (communication loss, unresponsive lidar, low
battery voltage, a node dying on an exception, encoder error, localization divergence).

## Self-check questions

1. Why do the risks differ between the Nav2 local planner occasionally finishing 30 ms late and the motor current loop occasionally being 1 ms late?
2. With only a software stop topic and no physical E-stop, which failures leave you unable to stop the robot?
3. What is the danger of a design that moves again automatically when commands resume after the watchdog entered the safe state?

## How to study this stage

1. **Course (first):** rewatch the power and emergency stop section of the Inflearn "robotics
   system breakdown" course and draw where the E-stop sits in the wiring.
2. **This lesson plus the example:** vary the event times in the watchdog example, predict the
   state transitions by hand, then run it and check.
3. **Documentation:** read the boundary between the control loop and hardware components in
   ros2_control Getting Started and mark where the watchdog goes.
4. **Problems:** take the quiz in the Korean original (`rc quiz m10-realtime-safety-reliability`),
   then do exercises (1) and (2).
5. **Low-level controller (optional):** implement heartbeat monitoring on the MCU side yourself
   with the micro-ROS Pico tutorial.

## References

- jelly, "현직자가 알려주는 로보틱스 시스템 완전 해부: 부품부터 통신까지", Inflearn (in Korean) - <https://www.inflearn.com/course/a-complete-breakdown>
- ros2_control, Getting Started - <https://control.ros.org/rolling/doc/getting_started/getting_started.html>
- Canonical, "Getting started with micro-ROS on Raspberry Pi Pico" - <https://ubuntu.com/blog/getting-started-with-micro-ros-on-raspberry-pi-pico>
- IEC 61508 / ISO 10218 / ISO 13482 (the standards themselves are paid; no URL obtained)
