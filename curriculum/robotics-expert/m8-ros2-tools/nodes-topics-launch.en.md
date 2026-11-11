---
id: m8-nodes-topics-launch
lang: en
title: "Programming nodes, topics, services, actions, parameters, and launch files"
summary: Learn the structure of a colcon workspace and an ament_python package, read and write rclpy nodes that publish, subscribe, and use parameters, and sort out the flow of service and action clients and how a Python launch file brings up several nodes at once.
objectives:
  - Explain the relationship between a colcon workspace (src, build, install, log) and sourcing (underlay and overlay), and write down the build and run order.
  - Read how subscriptions, timers, publishers, and parameters connect inside an rclpy node, and port the P controller of M3 into a node.
  - Explain the difference between the call flows of a service and an action, and bundle nodes, parameters, and remappings in a launch file.
tags: [ros2, rclpy, colcon, workspace, launch, parameters, actions]
---

# Programming nodes, topics, services, actions, parameters, and launch files

The previous lesson observed the graph from the CLI; this one builds a piece of the graph
yourself. The goal is not to memorize the rclpy API but to train the eye that, on opening
someone else's ROS 2 package, immediately finds "where it subscribes, where it computes, and
where it publishes." The reference-robot code reading of L8.5 puts that eye to work.

## Concepts

### Workspaces and sourcing

A colcon workspace keeps package sources in `src/`, and `colcon build` produces `build/`,
`install/`, and `log/`. `/opt/ros/jazzy` is the **underlay** and your workspace is the
**overlay** on top of it. In every new terminal you have to source the underlay and then
`install/setup.bash` before your packages are visible. The most common waste of time reported by
the community is a sourcing problem of the "it built fine but `Package not found`" kind, so it
pays to deliberately skip the sourcing once and get familiar with the error message.

The skeleton of a Python package (`ament_python`) is below. `package.xml` holds dependencies,
and `entry_points` in `setup.py` decides the executable name you call with `ros2 run`.

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python --dependencies rclpy geometry_msgs turtlesim \
  turtle_ctrl
cd ~/ros2_ws && colcon build --symlink-install
source install/setup.bash
ros2 run turtle_ctrl goto_node
```

### A node is a collection of callbacks

An rclpy node registers subscription callbacks, timer callbacks, and service callbacks, and
`rclpy.spin()` invokes them whenever an event arrives. Blocking for a long time inside a callback
(a long `sleep`, a synchronous service call) stalls the other callbacks too. Hence the common
structure: "store the latest sensor value in the subscription callback → compute and publish the
control in the timer callback."

### Services and actions

A service client sends a request with `call_async()` and receives the response through a Future.
An action is internally a bundle of goal and cancel services plus feedback and status topics.
The client sends a goal, learns whether it was accepted, receives feedback while it runs, and
finally receives the result. Nav2's `NavigateToPose` and MoveIt 2's motion execution are both
actions.

### launch

A real robot has dozens of nodes. A Python launch file describes which nodes to bring up with
which parameters, remappings, and namespaces. Parameters usually live in a separate YAML file
that the launch file loads.

## Example

Here is the P control of M3 attached to turtlesim. It subscribes to `/turtle1/pose` and publishes
`/turtle1/cmd_vel` toward a goal point. The goal and the gains are parameters.

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
        self.create_timer(0.05, self.on_timer)  # 20 Hz control period

    def on_pose(self, msg):
        self.pose = msg  # store only the latest value

    def on_timer(self):
        if self.pose is None:
            return
        gx, gy = self.get_parameter("goal").value
        dx, dy = gx - self.pose.x, gy - self.pose.y
        dist = math.hypot(dx, dy)
        err = math.atan2(dy, dx) - self.pose.theta
        err = math.atan2(math.sin(err), math.cos(err))  # wrap into [-pi, pi]
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

A launch file (`launch/goto.launch.py`) brings up the simulator and the control node together.

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

Change the goal while it runs with `ros2 param set /goto_node goal "[3.0, 3.0]"` and the turtle
turns toward it.

**Exercise:** (1) Create the package above, build it, and run it through the launch file. (2) In a
new terminal, skip the `install/setup.bash` sourcing, run `ros2 run turtle_ctrl goto_node`, and
record the error. (3) Modify the node to call the `/clear` service with `call_async()` once the
turtle reaches the goal.

## Self-check questions

1. `colcon build` succeeded but `ros2 run` cannot find the package. What are the first two things to check?
2. Why does the example put the control computation in the timer callback rather than the subscription callback?
3. Give an example of a situation that calls for an action rather than a service, and write down the three kinds of response an action client receives.

## How to study this stage

1. **Official tutorials (first):** follow *Beginner: Client libraries* in order - colcon →
   workspace → package → Python pub/sub → services → parameters - then read actions and launch in
   *Intermediate*.
2. **This lesson plus the example:** type the example node in yourself and run it, annotating
   where the subscription, the timer, and the publisher connect.
3. **Problems:** take the quiz in the Korean original (`rc quiz m8-nodes-topics-launch`), then do
   exercises (1) through (3). Do not skip the broken-sourcing drill in (2) - it cuts the debugging
   time of every later ROS 2 lesson.
4. **Optional reinforcement (paid):** if you want prose explanations, work through *ROS 2 from
   Scratch* or Renard's Udemy Level 1 alongside. When using a Korean course based on Humble, just
   read the distribution name as Jazzy.

## References

- ROS 2 Jazzy Tutorials, Beginner: Client libraries / Intermediate - <https://docs.ros.org/en/jazzy/Tutorials.html>
- Edouard Renard, *ROS 2 from Scratch*, Packt - <https://www.packtpub.com/en-ro/product/ros-2-from-scratch-9781835881415>
- Edouard Renard, ROS 2 for Beginners (ROS Jazzy) Level 1, Udemy - <https://www.udemy.com/course/ros2-for-beginners/>
- "[R2R] 무작정 따라하는 ROS2 입문과정", Udemy (Humble, in Korean) - <https://www.udemy.com/course/r2r_ros2_bgn/>
