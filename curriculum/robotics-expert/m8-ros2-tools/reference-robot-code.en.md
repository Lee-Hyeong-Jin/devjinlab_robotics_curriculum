---
id: m8-reference-robot-code
lang: en
title: Reading reference robot code
summary: Using the repositories of the open-source differential-drive robots Andino and TurtleBot as examples, read how a ROS 2 robot project splits into description, bringup, base, control, slam, and navigation packages, and learn the code-reading order that starts from the launch file and follows it down through nodes, parameters, and tf.
objectives:
  - Place the packages of a reference robot repository onto the stack map of L8.4 (hardware, control, estimation, planning).
  - Start from the bringup launch file and trace the nodes it runs, the YAML parameters it loads, and the tf it publishes.
  - Investigate a running system with the ros2 CLI and check it against the structure you read in the code.
tags: [ros2, code-reading, andino, turtlebot, reference-robot, architecture]
---

# Reading reference robot code

So far you have seen concepts and tools as separate pieces. A real robot project is those pieces
bundled into dozens of packages. The goal of this lesson is to open an unfamiliar ROS 2
repository and draw a map of "what runs where and how the data flows" within 30 minutes. The main
text is Ekumen's **Andino**: a fully open-source differential-drive robot built from a Raspberry
Pi and a microcontroller, supporting Humble and Jazzy, whose packages correspond almost one to
one with this course's modules.

## Concepts

### The conventional package split

ROS 2 robot repositories are split much the same way. Taking Andino as the example:

| Package | Layer | What is in it |
|---|---|---|
| `andino_description` | model | URDF/xacro, meshes (L8.3) |
| `andino_firmware` | hardware | microcontroller firmware (motor PWM, reading encoders) |
| `andino_base` | control | the ros2_control hardware interface (talks to the firmware over serial) |
| `andino_control` | control | diff drive controller + joint state broadcaster configuration and launch |
| `andino_bringup` | integration | the top-level launch that brings up the whole robot |
| `andino_slam` | mapping | SLAM Toolbox configuration |
| `andino_navigation` | navigation | Nav2 configuration and launch |
| `andino_gz` and others | simulation | simulator integration such as Gazebo (outside this course) |

The key points are that `description` is shared by the hardware and the simulation, and that
`bringup` assembles the rest. The TurtleBot 3 and 4 repositories have the same structure under
different names.

### The reading order: top down

1. **README** - supported distributions, dependencies, run commands. Check first whether the distribution is Jazzy.
2. **bringup launch** - which launch files it includes and which nodes it starts. Conditional
   arguments (`use_sim_time`, `rviz`, …) are visible here too.
3. **config YAML** - the controller's wheel separation and radius, the Nav2 and SLAM parameters.
   The $L$ and $r$ that went into the differential-drive equations of M3 are here.
4. **description** - frame names and sensor mounting positions. Predict the tf tree from it.
5. **C++/Python source** - last, and only the nodes you need. Most robot packages hold more
   configuration and launch than code.

### Checking the code against what runs

What you read is a hypothesis. Confirm it against a running system (real hardware, or a bag
somebody else recorded) with the ros2 CLI.

```bash
ros2 launch andino_bringup andino_robot.launch.py   # follow the run command in the README
ros2 node list
ros2 node info /controller_manager
ros2 control list_controllers
ros2 control list_hardware_interfaces
ros2 topic info /cmd_vel -v
ros2 param dump /diff_controller
ros2 run tf2_tools view_frames
```

Launch file and node names can differ between versions, so adapt them to the repository's README.
If you have no hardware, reading this step is enough. What matters is knowing "which hypothesis
each command confirms."

### The data flow in one line

Teleop or Nav2 publishes `/cmd_vel` (Twist) → `diff_drive_controller` computes left and right
wheel speed commands with the inverse kinematics of M3 → the `andino_base` hardware interface
passes them to the firmware over serial → the firmware drives the motors and returns encoder
values → the controller publishes `/odom` and the `odom → base_link` tf through forward
kinematics. Once you can draw this line yourself, the exercises in M5 and M6 that swap out
individual layers become easy.

## Example

Find entries like the following in the controller YAML of `andino_control` and match them to the
concepts of M3 (field names follow the `diff_drive_controller` documentation; check the values in
the repository).

```yaml
diff_controller:
  ros__parameters:
    left_wheel_names: ["left_wheel_joint"]
    right_wheel_names: ["right_wheel_joint"]
    wheel_separation: 0.137   # the L of M3 (example value)
    wheel_radius: 0.033       # the r of M3 (example value)
    odom_frame_id: odom
    base_frame_id: base_link
```

**Exercise:** Clone the Andino repository and write a one-page note. (1) Write one line per
package describing its role, as in the table above. (2) Starting from the bringup launch, draw a
tree of the launch files and nodes it includes. (3) Find the actual wheel separation and radius in
the controller YAML, put them into the differential-drive equations of M3, and compute the
robot's linear velocity when the wheel angular velocity is 1 rad/s. (4) Find the packages with the
same roles in the TurtleBot 3 or 4 repository and map the names across.

## Self-check questions

1. Why do the hardware bringup and the simulation share the `description` package?
2. If the wheel radius is configured 10% larger than the real one, what error appears in `/odom`?
3. Explain why reading the launch files and YAML before the source code is more efficient in an unfamiliar repository.

## How to study this stage

1. **The repository first:** read the Andino README and package list, and fill in the table of
   this lesson yourself.
2. **Tracing:** draw the launch tree of exercise (2) by hand. If you get stuck, go back to the
   launch section of L8.2.
3. **Problems:** take the quiz in the Korean original (`rc quiz m8-reference-robot-code`), then do
   exercises (1) through (4).
4. **Comparison:** skim how the same layers (SLAM, Navigation) are configured in the TurtleBot 3
   e-Manual or the TurtleBot 4 tutorials. The TurtleBot 3 e-Manual is migrating to ROBOTIS Docs,
   so check which distribution it states.
5. **Depth (optional, paid):** reading the ros2 controllers and Nav2 chapters of *Mastering ROS 2*
   prepares you for M6 and M7.

## References

- Ekumen-OS, Andino - <https://github.com/Ekumen-OS/andino>
- ROBOTIS, TurtleBot3 e-Manual - <https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/>
- TurtleBot 4 User Manual, Tutorials - <https://turtlebot.github.io/turtlebot4-user-manual/tutorials/>
- Lentin Joseph, Jonathan Cacace, *Mastering ROS 2 for Robotics Programming*, 4th ed., Packt -
  <https://www.packtpub.com/en-US/product/mastering-ros-2-for-robotics-programming-9781836209003>
