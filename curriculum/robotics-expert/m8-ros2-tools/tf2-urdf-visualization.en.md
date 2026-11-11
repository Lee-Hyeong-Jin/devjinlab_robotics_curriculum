---
id: m8-tf2-urdf-visualization
lang: en
title: "tf2, URDF, RViz, rosbag2 (MCAP), and Foxglove"
summary: See how the coordinate transforms of M1 are implemented in ROS 2 as a tf2 frame tree (map, odom, base_link, sensors) and how a URDF defines the fixed part of that tree, then learn to visualize and debug with RViz, rqt, and the ros2 CLI, record and replay with rosbag2 (MCAP), and review the result in Foxglove.
objectives:
  - Explain the relationship between the map, odom, base_link, and sensor frames and the REP conventions, and look up the transform between two frames with tf2.
  - Explain how URDF links and joints together with robot_state_publisher build the tf tree.
  - Choose the right tool among RViz, rqt, the ros2 CLI, rosbag2, and Foxglove for a given debugging situation.
tags: [ros2, tf2, urdf, rviz, rqt, rosbag2, mcap, foxglove, debugging]
---

# tf2, URDF, RViz, rosbag2 (MCAP), and Foxglove

M1 taught how to move between coordinate frames by multiplying homogeneous transforms $T_{AB}$.
A robot has dozens of such frames, and some of them move (wheels, joints, the robot itself).
tf2 manages these transforms as a **time-stamped tree** so it can answer queries like "this lidar
point from 0.3 seconds ago, in map coordinates now." This lesson covers tf2 and URDF together
with the tools that let you see and record the result. The sensor fusion and SLAM lessons of M5
list this lesson as a prerequisite.

## Concepts

### The frame tree

The standard tree for a mobile robot is `map → odom → base_link → (laser, imu, camera_link, …)`
(REP 105).

- `odom → base_link`: published by odometry (the differential-drive integration of M3). Continuous, but drifts over time.
- `map → odom`: published by localization (SLAM or AMCL). It can jump momentarily as it corrects that drift.
- `base_link → laser`: the sensor mounting position. It does not move, so it is a **static** transform.

Each transform has exactly one parent, and a given transform must be published by exactly one
node. If two nodes publish the same `odom → base_link`, you get the classic bug where the robot
jitters in RViz.

### tf2 lookups and time

`lookup_transform(target, source, time)` returns the transform that expresses the pose of the
source frame in the target frame. `Time()` (0) means "the most recent value." If you ask for a
specific time that the buffer does not hold yet, you get an extrapolation exception, so sensor
processing code either catches the exception or waits briefly. In simulation or during bag
playback, turn on `use_sim_time` so that nodes follow `/clock`.

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
            self.get_logger().warn(f"tf not available yet: {e}")
            return
        p = t.transform.translation
        self.get_logger().info(f"base_link in odom: x={p.x:.2f}, y={p.y:.2f}")
```

### URDF and robot_state_publisher

A URDF is XML that describes a robot as `link` elements (rigid bodies with geometry and inertia)
and `joint` elements (parent, child, origin, axis, type). What the DH parameters of M2 did is
done here by a joint's `origin` and `axis`. `robot_state_publisher` takes the URDF and
`/joint_states` and publishes static tf for fixed joints and forward-kinematics tf for revolute
joints. In practice URDFs are often generated from xacro macros.

```xml
<joint name="laser_joint" type="fixed">
  <parent link="base_link"/>
  <child link="laser"/>
  <origin xyz="0.10 0 0.20" rpy="0 0 0"/>
</joint>
```

### Visualization and debugging tools

- **ros2 CLI** - `topic hz/echo/info -v` (checking QoS), `node info`, `param dump`, `ros2 doctor`. Reach for it first.
- **rqt** - `rqt_graph` (connections), `rqt_console` (log filtering), `rqt_plot` (value graphs), `rqt_tf_tree`.
- **RViz2** - the 3D scene. Pick a Fixed Frame and overlay TF, LaserScan, PointCloud2, RobotModel, and Path.
  If "nothing shows up," suspect the Fixed Frame and the tf connection first.
- **rosbag2** - `ros2 bag record/play/info`. Since Iron the default storage format is MCAP. Replaying
  the same data over and over while you fix the algorithm is the core way to develop without hardware.
- **Foxglove** - a web and desktop visualization tool. Connect live through the Foxglove Bridge, or
  open an `.mcap` file directly. Learn RViz first and Foxglove second.

## Example

Record the turtlesim tf2 demo and review it.

```bash
sudo apt install ros-jazzy-turtle-tf2-py ros-jazzy-tf2-tools
ros2 launch turtle_tf2_py turtle_tf2_demo.launch.py   # terminal 1
ros2 run turtlesim turtle_teleop_key                  # terminal 2
ros2 run tf2_tools view_frames                        # generates frames_*.pdf
ros2 run tf2_ros tf2_echo world turtle2
ros2 bag record -o turtle_run /tf /turtle1/pose        # stop with Ctrl+C
ros2 bag info turtle_run
ros2 bag play turtle_run
```

**Exercise:** (1) Draw the parent-child relationships from the `view_frames` output. (2) Replay the
bag you recorded and add a TF display in RViz2 with the Fixed Frame set to `world`. (3) Open the
same `.mcap` file in Foxglove and plot the x and y of `/turtle1/pose` in a Plot panel.

## Self-check questions

1. Why are `odom → base_link` and `map → odom` published by different nodes?
2. How are a fixed joint and a revolute joint in a URDF each published as tf?
3. Write down three or more steps, in order, for diagnosing a LaserScan that does not appear in RViz, using the CLI, rqt, and RViz.

## How to study this stage

1. **Official tutorials (first):** read the tf2 series in *Intermediate* (Introducing tf2 → static
   broadcaster → broadcaster → listener) and the URDF series, then follow rosbag and rqt_console in
   *Beginner*.
2. **This lesson plus the example:** match the transform matrix products of the M1 lesson against
   the output of `tf2_echo`.
3. **Problems:** take the quiz in the Korean original (`rc quiz m8-tf2-urdf-visualization`), then
   do exercises (1) through (3).
4. **Optional reinforcement (paid):** if you want video, watch the TF, URDF, and RViz parts of
   Renard Level 2 (you can skip the Gazebo part).
5. **Extending your tools:** once RViz feels familiar, learn to view MCAP files from the Foxglove
   documentation. The free-plan limits can change, so check before signing up.

## References

- ROS 2 Jazzy Tutorials, Intermediate tf2 and URDF / Beginner rosbag and rqt_console - <https://docs.ros.org/en/jazzy/Tutorials.html>
- Edouard Renard, ROS 2 for Beginners Level 2 (TF, URDF, RViz, Gazebo) - <https://roboticsbackend.com/courses/>
- Foxglove, ROS 2 docs - <https://docs.foxglove.dev/docs/connecting-to-data/frameworks/ros2>
- ROS 2 Documentation, Visualizing ROS 2 data with Foxglove - <https://docs.ros.org/en/lyrical/Related-Projects/Visualizing-ROS-2-Data-With-Foxglove.html>
- Wim Meeussen, REP 105 "Coordinate Frames for Mobile Platforms"
