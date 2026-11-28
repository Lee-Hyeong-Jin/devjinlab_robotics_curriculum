---
id: m8-stacks-dev-environment
lang: en
title: A map of the higher-level stacks and the development environment
summary: Map which layer of robot software ros2_control, Nav2, MoveIt 2, SLAM Toolbox, robot_localization, and micro-ROS each occupy, then survey native Ubuntu 24.04 versus Docker development containers, testing and CI habits, and where simulators fit.
objectives:
  - Place ros2_control, robot_localization, SLAM Toolbox, Nav2, MoveIt 2, and micro-ROS on the hardware → control → estimation → planning/behavior layers and state each one's input and output topics.
  - Explain the roles of the Controller Manager, the Resource Manager, hardware components, and controllers in ros2_control.
  - Compare the trade-offs of a native installation against a Docker container, and describe the flow of running package tests with colcon test.
tags: [ros2, ros2-control, nav2, moveit2, micro-ros, docker, ci, dev-environment]
---

# A map of the higher-level stacks and the development environment

The real value of ROS 2 lies less in its communication layer than in the proven stacks built on
top of it. You do not have to write wheel control, localization, mapping, path planning, and arm
motion planning from scratch. This lesson surveys those stacks as a **map** only. The principles
and hands-on practice for each come in M5 (estimation and SLAM), M6 (Nav2), and M7 (MoveIt 2),
and those lessons list this one as a prerequisite. The second half covers the development
environment in which you will do that practice.

## Where you will use this

For a mobile robot you take ros2_control for the wheels, robot_localization and SLAM Toolbox for
localization and Nav2 for driving; for an arm, MoveIt 2. What you write yourself is the
configuration that joins them and the hardware driver only your robot has. Knowing which stack owns
which layer and what they exchange is what lets you decide "whose problem is this". The development
environment exists to run those stacks the same way on your PC and in CI.

## Concepts

### The stack map

Read it from the bottom up.

| Layer | Stack | What it does | Main inputs and outputs |
|---|---|---|---|
| Hardware | micro-ROS | turns a microcontroller (ESP32, STM32, Pico, …) into a node in the ROS 2 graph | motors and sensors ↔ topics |
| Control | ros2_control | hardware abstraction + a real-time control loop + controller plugins | `/cmd_vel` → wheel commands, `/joint_states` |
| Estimation | robot_localization | fuses wheel odometry, IMU, and GPS with an EKF | `/odom`, `/imu` → fused `odom → base_link` |
| Mapping and localization | SLAM Toolbox | lidar SLAM, map building and localization | `/scan` → `/map`, `map → odom` |
| Navigation | Nav2 | global and local planning through a behavior tree (BT), costmaps, recovery behaviors | goal pose (action) → `/cmd_vel` |
| Manipulation | MoveIt 2 | inverse kinematics, collision checking, motion planning, and execution for an arm | goal pose (action) → joint trajectory |

Overlay this on the tf tree of L8.4 and you can see which transform each stack publishes. Nav2,
for example, does not estimate its own position; it assumes `map → odom → base_link` already exists.

### A closer look at ros2_control

On a real robot, the PID and differential-drive math you wrote in M3 usually lives inside
ros2_control.

- **Hardware components** (System, Sensor, and Actuator plugins): read from and write to the
  actual device. The `<ros2_control>` tag in the URDF declares which joints have which command
  and state interfaces.
- **Resource Manager**: collects the hardware interfaces and lends them to controllers.
- **Controller Manager**: runs the control loop (read → update → write) and loads and switches
  controllers.
- **Controllers** (pluginlib plugins): `diff_drive_controller`, `joint_trajectory_controller`,
  `joint_state_broadcaster`, and others. Inspect their state with `ros2 control list_controllers`.

Controller configuration is YAML (an illustrative shape):

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100
    diff_cont:
      type: diff_drive_controller/DiffDriveController
    joint_broad:
      type: joint_state_broadcaster/JointStateBroadcaster
```

This stack differs a lot between distributions, so check that an example you are reading is the
Jazzy version. In Lyrical, APIs deprecated in Jazzy have been removed, and older controller
examples may fail.

### The development environment

**First, where ROS 2 has to be installed at all.** In this course only the examples and exercises
of M8, and some tasks of the capstone (M10), need ROS 2 installed. The runnable examples and the
exercises of M1–M7 and M9 need Python with NumPy and SciPy and reading the official documentation,
nothing more (one item in M7 is optional, "if you have it installed"). If the installation gets
stuck you can carry on with the rest of the course.

- **Native Ubuntu 24.04 + Jazzy binaries**: the least trouble. Dual boot works well too.
- **Docker**: a good alternative on macOS or Windows, or when you move between distributions.
  Use the recipe below.
- **WSL2**: it works, but friction with networking and GUIs is reported often.

**The smallest Docker recipe.** In an empty folder, create a `ros2_ws/src` folder and this
`compose.yaml` (checked on 2026-11-28 with the `ros:jazzy` image, which is based on Ubuntu 24.04).

```yaml
services:
  ros:
    image: ros:jazzy
    volumes:
      - ./ros2_ws:/ros2_ws   # your workspace on the PC, visible in the container
    working_dir: /ros2_ws
    command: sleep infinity  # keep the container up; you work in it from terminals
```

```bash
docker compose up -d                     # the first run downloads the image (a little over 1 GB)
docker compose exec ros bash             # terminal 1: into the container
source /opt/ros/jazzy/setup.bash         # first thing, every time you enter
ros2 topic pub /chatter std_msgs/msg/String "{data: hello}"

docker compose exec ros bash             # terminal 2: into the same container again
source /opt/ros/jazzy/setup.bash
ros2 topic echo /chatter                 # success when "data: hello" keeps printing
```

Both terminals are inside one container, so they talk without any network setup. `ros:jazzy` is
the minimal variant (ros-base) and has neither turtlesim nor the demo nodes. Add what you need
inside the container with `apt-get update && apt-get install -y ros-jazzy-turtlesim` (it is gone
when the container is removed, so put what you keep using into a `Dockerfile`). For everything
else follow the official Docker guide (see the references).

```hint
`ros2: command not found`
ROS 2 is not sourced in this terminal. Every shell opened with `docker compose exec` is a new one.

    source /opt/ros/jazzy/setup.bash

If `echo $ROS_DISTRO` prints `jazzy` and the command is still missing, sourcing is indeed what is
missing: the image sets that variable in advance, so it says nothing about sourcing.
```

```hint
`ros2 run` cannot find the package you built (`Package '...' not found`)
You did not source the workspace after `colcon build`, or you sourced a different one.

    source /opt/ros/jazzy/setup.bash      # the installation (underlay) first
    source /ros2_ws/install/setup.bash    # then your workspace (overlay) on top

`echo $AMENT_PREFIX_PATH` shows which paths this shell is looking at. Sourcing in a **new
terminal**, not the one you built in, is the safer habit.
```

```hint
Nodes in another container, on the host or in WSL2 do not appear in `ros2 node list`
DDS finds its peers by multicast within one network. A container is on a virtual network of its
own by default, so it and the nodes outside do not find each other. Check in this order.

1. Is `ROS_DOMAIN_ID` the same on both sides (`echo $ROS_DOMAIN_ID`; empty means 0)?
2. On a Linux host, add `network_mode: host` to the service in `compose.yaml`. If the nodes show
   up but no data arrives, add `ipc: host` as well (the shared-memory transport needs it).
3. Docker Desktop on macOS and Windows, and WSL2 in its default setting, do not pass the host
   network and multicast through as they are. Running the nodes you need **in the same container
   (or the same Compose network)** is what gets stuck least.
4. See for yourself whether multicast gets through with `ros2 multicast receive` and
   `ros2 multicast send`.
```

```hint
GUI windows such as RViz or rqt do not open (`could not connect to display`)
A container has no screen. On Linux (X11) add the following to the service and run
`xhost +local:docker` once on the host.

    environment:
      - DISPLAY=${DISPLAY}
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix

Wayland, macOS and Windows each need something different; see the official Docker guide. If you do
not strictly need a GUI, recording with rosbag2 and opening the file in Foxglove in a browser takes
the least setup.
```

**When you do not need ROS 2.** ROS 2 is a tool for joining parts that run in several processes,
on several computers, written by several people. A line follower with one microcontroller and two
motors, an experiment that reads a sensor or two, and the NumPy examples of this course do not need
it; installing and building would only add work. The time to bring ROS 2 in is when you want a
stack such as Nav2 or MoveIt 2, when you want to use a sensor driver someone else wrote, or when
you start needing the recording and visualization tools (rosbag2, RViz).

Whichever you choose, keep the sourcing line in `~/.bashrc`, and when you mix workspaces stay
aware of what each terminal has sourced.

### Testing and CI

`colcon test` runs each package's tests (pytest for Python, including the flake8 and pep257 lints
generated by default), and `colcon test-result --verbose` collects the results. Run the same
command inside a `ros:jazzy` container and it becomes a CI job as is. It is the cheapest way to
stop code that only works on your own machine.

### Simulators in one line

Gazebo (Harmonic is the Jazzy pairing, bridged by `ros_gz`), Webots, and MuJoCo are the main
ones. This platform does not cover simulator practice. To choose one, start from the one-line
guide below and then read each project's own documentation.

- **[Gazebo](https://gazebosim.org/docs):** the most tightly integrated with ROS 2. The default
  choice for a mobile robot with sensors (LiDAR, camera, IMU) and for trying Nav2 or
  `ros2_control`.
- **[Webots](https://cyberbotics.com/doc/guide/index):** one install brings robot models, example
  worlds and an editor. It runs on Windows, macOS and Linux, which makes it an easy first
  simulator.
- **[MuJoCo](https://mujoco.readthedocs.io/):** fast dynamics with contact. Widely used in
  control and reinforcement-learning research (M9), and usable from Python alone, without ROS.

## Example

```bash
# a Jazzy container with the workspace mounted
docker run -it --rm -v ~/ros2_ws:/ros2_ws -w /ros2_ws ros:jazzy bash

# inside the container
source /opt/ros/jazzy/setup.bash
rosdep update && rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
colcon test --packages-select turtle_ctrl
colcon test-result --verbose
```

**Exercise:** (1) Build and test the `turtle_ctrl` package of L8.3 in the container above.
(2) Bring up the same environment from the `compose.yaml` in this lesson and pass the `/chatter` check. (3) On the
stack table in this lesson, draw arrows for the data flow of the scenario "the robot maps the
living room and drives to the kitchen."

## Self-check questions

1. Which tf transforms and topics must already exist for Nav2 to work? Which stack provides each?
2. Where is the boundary between the Controller Manager and a hardware component in ros2_control? If you swap the actual motor, which side's code do you change?
3. Give a situation where you would choose Docker over a native installation, and one inconvenience you would accept in return.

## How to study this stage

1. **The map first:** rather than memorizing the stack table, redraw it layered on top of the tf
   tree figure of L8.4.
2. **ros2_control:** read the architecture figure in Getting Started, then skim the file layout of
   `ros2_control_demos` example_1 (RRBot) in code (`rrbot_controllers.yaml`,
   `rrbot.ros2_control.xacro`, `rrbot.launch.py`). Running it is optional.
3. **Environment:** if you do not have ROS 2 yet, start with a container from the Docker guide.
   Read the Discourse thread in advance for where beginners get stuck.
4. **Problems:** take the quiz in the Korean original (`rc quiz m8-stacks-dev-environment`), then
   do exercises (1) through (3).
5. **micro-ROS (optional):** if you plan to work with microcontrollers, at least check the list of
   supported boards in the `micro_ros_setup` README.

## References

- ros2_control, Getting Started - <https://control.ros.org/rolling/doc/getting_started/getting_started.html>
- ros2_control_demos - <https://github.com/ros-controls/ros2_control_demos>
- Docker Docs, Introduction to ROS 2 Development with Docker - <https://docs.docker.com/guides/ros2/>
- ROS Discourse, What is the hardest part of learning ROS 2 as a beginner - <https://discourse.openrobotics.org/t/what-is-the-hardest-part-of-learning-ros-2-as-a-beginner/57917>
- micro-ROS, micro_ros_setup - <https://github.com/micro-ROS/micro_ros_setup>
