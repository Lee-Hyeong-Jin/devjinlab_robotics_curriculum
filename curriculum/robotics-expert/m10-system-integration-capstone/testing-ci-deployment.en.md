---
id: m10-testing-ci-deployment
lang: en
title: "Testing, CI, and deployment (unit/integration/HIL, containers, logging and observability)"
summary: Verify robot software through a pyramid of unit tests, integration tests, recorded-data replay tests, and HIL (hardware-in-the-loop) tests; pin the development and deployment environment with Docker containers; and observe a running robot with rosbag2 (MCAP), logs, and metrics.
objectives:
  - Separate algorithm code into pure functions free of ROS dependencies and write pytest unit tests for them.
  - Design a regression test that replays recorded sensor logs and compares the resulting metrics against a baseline.
  - Compare the kinds of defects unit, integration, and HIL tests each catch and their costs, and decide what to automate in CI.
  - Establish a deployment and observability procedure using Docker images, rosbag2, and structured logs to reduce "it works on my machine" problems.
tags: [testing, pytest, ci, hil, docker, rosbag2, mcap, logging, observability]
---

# Testing, CI, and deployment

Robot bugs are expensive. An error you would find in five minutes at your desk takes an hour on
the robot, counting battery swaps, reboots, and walking to the test area. The goal of this lesson
is to build a structure that catches **as many defects as possible before they reach the robot**.
The development environment built in M8 now hardens into a reproducible one.

## Concepts

### The test pyramid

| Layer | Target | Tools | Speed | Defects it catches |
|---|---|---|---|---|
| Unit | pure functions (kinematics, one filter step, a cost function) | pytest, GTest | ms | mistakes in equations, signs, units |
| Integration | several nodes plus topics | launch_testing, `ros2 topic` | seconds | mismatched topic names, QoS, frame_id |
| Log replay | recorded sensor data → algorithm | rosbag2 (MCAP) playback | minutes | performance regressions under real noise |
| HIL | real MCU, motors, sensors + a faked environment | a test jig, the robot on a stand | minutes to hours | firmware timing, power, wiring |

The lower layers are cheap and fast, so have many; the upper ones are expensive, so have few. The
key habit is **separating the algorithm from ROS**. Keep node callbacks as a thin shell that
unpacks the message, hands it to a pure function, and wraps the result back into a message. Then
the numpy code written in M3-M6 becomes directly testable.

**HIL (hardware-in-the-loop)** puts some of the real hardware in the loop and fakes the rest. It
needs no simulator. The simplest HIL is putting the robot on a stand with the wheels in the air,
feeding `/cmd_vel` step inputs, and recording the encoder response and the watchdog behavior
(L10.3).

### CI: hand the checks people forget to a machine

On every commit, run (1) lint and format, (2) the build (`colcon build`), (3) unit and
integration tests (`colcon test`), and (4) a short log replay regression test. CI must run inside
the same Docker image for its results to match a developer's PC.

### Deployment and observability

- **Containers:** pin the distribution (Jazzy) and the dependencies in an image. On the robot you
  need `--network host` and device passthrough (`--device /dev/ttyUSB0`).
- **Recording:** leave an MCAP from every test with `ros2 bag record`, putting the date, the commit
  hash, and the scenario in the filename.
- **Observability:** use RViz first, and open MCAP in Foxglove for remote and post-hoc analysis.
  Logs should be left as "key=value" rather than free prose in the style of `RCLCPP_INFO`, so you
  can search and aggregate them later.

## Key checklist

- [ ] Algorithm code lives in modules that do not import rclpy.
- [ ] Unit tests cover boundary values (0, negatives, large angles, empty input).
- [ ] At least one reference MCAP and its baseline metrics are in the repository (or downloadable).
- [ ] CI runs in the same Docker image as development.
- [ ] Every test recording carries a commit hash.

## Example

Put one step of differential-drive odometry (M3, M5) in a pure function, then write a unit test
and a "log replay" regression test. The log is synthesized here; in practice you would use the
(dt, v, ω) arrays extracted from an MCAP.

```python
import numpy as np


def odom_step(pose, v, w, dt):
    x, y, th = pose
    return np.array(
        [
            x + v * np.cos(th) * dt,
            y + v * np.sin(th) * dt,
            (th + w * dt + np.pi) % (2 * np.pi) - np.pi,
        ]
    )


def test_straight_line():
    assert np.allclose(odom_step(np.zeros(3), 1.0, 0.0, 0.5), [0.5, 0.0, 0.0])


def test_angle_wraps():
    assert -np.pi <= odom_step(np.array([0, 0, 3.1]), 0.0, 1.0, 0.1)[2] < np.pi


def test_replay_regression(baseline_end_error=0.05):
    # once around a circle of radius 1 m: the endpoint should return to the start
    dt, n = 0.02, 314
    log = [(dt, 1.0, 1.0)] * n  # (dt, v, w)
    pose = np.zeros(3)
    for d, v, w in log:
        pose = odom_step(pose, v, w, d)
    err = float(np.hypot(pose[0], pose[1]))
    print(f"replay end_error_m={err:.4f} baseline={baseline_end_error}")
    assert err < baseline_end_error


for test in (test_straight_line, test_angle_wraps, test_replay_regression):
    test()
    print("PASS", test.__name__)
```

pytest discovers `test_` functions automatically, so you can drop the final loop and put this in
`tests/test_odom.py`. With real logs, set the baseline to "the current result plus margin" and
check on every algorithm change that the number has not gotten worse.

The skeleton of building and testing with the same image in CI and on the robot looks like this:

```bash
docker build -t capstone:jazzy .
docker run --rm capstone:jazzy bash -c "colcon build && colcon test && colcon test-result --verbose"
docker run --rm -it --network host --device /dev/ttyUSB0 capstone:jazzy ros2 launch capstone_bringup robot.launch.py
ros2 bag record -s mcap -o "$(date +%F)_$(git rev-parse --short HEAD)_square" /odom /scan /cmd_vel /tf
```

**Exercise:** (1) Record a 1-2 minute MCAP on your own robot and build a regression test that
computes an odometry or EKF metric from that data. (2) Write a workflow (on GitHub Actions or
similar) that runs lint → build → test in the Docker image. (3) Write a one-page HIL test
procedure for the robot on a stand.

## Self-check questions

1. At which layer of the pyramid is a typo in a topic name first caught? Why can a unit test not catch it?
2. Why set the baseline of a log replay regression test to "the current result plus margin" rather than to "the right answer"?
3. What problems can appear six months later if you deployed to the robot with a direct `apt install` and no Docker image?

## How to study this stage

1. **Documentation (first):** follow the official Docker ROS 2 guide with the Jazzy image
   substituted, and create a Dockerfile in your own capstone repository.
2. **This lesson plus the example:** move the example into pytest and run it, then deliberately
   introduce a sign error into `odom_step` and see which test fails.
3. **Observability:** following the Foxglove documentation, open an MCAP you recorded and view
   `/odom` and `/scan` side by side.
4. **Problems:** take the quiz in the Korean original (`rc quiz m10-testing-ci-deployment`), then
   do exercises (1) through (3).
5. **Reinforcement (optional):** read Automatic Addison's pytest, bag, and ros2 doctor articles,
   and the GUI and WSL2 sections of docker-for-robotics.

## References

- Docker, "Introduction to ROS 2 Development with Docker" - <https://docs.docker.com/guides/ros2/>
- 2b-t, docker-for-robotics - <https://github.com/2b-t/docker-for-robotics>
- Foxglove, "Connecting to ROS 2 data" - <https://docs.foxglove.dev/docs/connecting-to-data/frameworks/ros2>
- Automatic Addison, ROS 2 Tutorials - <https://automaticaddison.com/tutorials>
