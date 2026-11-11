---
id: m8-ros2-concepts-distros
lang: en
title: ROS 2 concepts and choosing a distribution
summary: Understand ROS 2 as a "computation graph of nodes exchanging messages," sort out what topics, services, actions, and parameters are each for and what DDS/RMW, QoS, and the domain ID do, then decide which distribution (Jazzy, Lyrical, Humble) to pick as of late 2026.
objectives:
  - Distinguish nodes, topics, services, actions, and parameters, and choose the right communication pattern for a given robot feature.
  - Explain how the DDS-based middleware (RMW), QoS, and ROS_DOMAIN_ID affect node discovery and communication.
  - Justify the choice of Jazzy as the learning distribution from support windows and Ubuntu pairings.
tags: [ros2, computation-graph, dds, qos, distributions, jazzy]
---

# ROS 2 concepts and choosing a distribution

M1-M4 treated coordinate transforms, kinematics, control, and sensor processing as separate,
self-contained Python code. On a real robot those pieces run at the same time in different
processes - sometimes on different computers - and have to exchange data. ROS 2 (Robot Operating
System 2) is not an operating system but the communication layer that joins those pieces,
plus the ecosystem of tools and libraries built on top of it. This module is a reading-first
survey of ROS 2 that builds the foundation the ROS 2 lessons of M5 (state estimation),
M6 (planning and Nav2), and M7 (manipulation and MoveIt 2) expect.

## Concepts

### The computation graph

A ROS 2 system is a graph of **nodes** connected by named channels. A node is a unit of
execution responsible for one job (a lidar driver, an odometry calculator, a path follower),
and the channels are the following.

| Mechanism | Pattern | When to use it | Examples |
|---|---|---|---|
| Topic | publish/subscribe, many-to-many, asynchronous | continuously flowing data | `/scan`, `/odom`, `/cmd_vel` |
| Service | request/response, finishes quickly | queries and commands that end immediately | saving a map, resetting state |
| Action | goal -> feedback -> result, cancellable | long-running work | "drive to this pose" |
| Parameter | per-node configuration value | settings tuned while running | PID gains, maximum speed |

Porting the path follower of M3 to ROS 2 makes it a node that subscribes to `/odom` and
publishes `/cmd_vel`, with the gain $K_p$ becoming a parameter. A request of the form
"drive to the destination" needs feedback (distance remaining) and cancellation, so it belongs
in an action, not a service.

### Messages and interfaces

The data formats that topics, services, and actions exchange are defined by `.msg`, `.srv`,
and `.action` interfaces. Reach for standard messages such as `geometry_msgs/msg/Twist`
(linear and angular velocity) or `sensor_msgs/msg/LaserScan` first, and build a custom
interface only when you truly need one. With standard messages, tools like RViz understand
the data immediately.

### DDS, RMW, QoS, and domains

ROS 2 does not implement communication itself; it delegates to middleware such as DDS (Data
Distribution Service). The abstraction layer in between is the RMW (ROS MiddleWare interface),
and the default implementation is Fast DDS (the `RMW_IMPLEMENTATION` environment variable
switches it to Cyclone DDS or another). There is no central master, so nodes **discover each
other automatically** over the network. To keep from mixing with another robot on the same
network, give them different values of `ROS_DOMAIN_ID`.

QoS (Quality of Service) is the per-channel delivery policy. A sensor stream cares about the
latest value, so it uses *best effort* and tolerates loss; data that must not be dropped, such
as commands or maps, uses *reliable*. If the QoS of a publisher and a subscriber are not
compatible, **nothing arrives and there is no error**. That is the classic cause of the
beginner's complaint, "I can see the topic but no data comes."

### Choosing a distribution

ROS 2 releases a distribution every May, and even-year releases get five years of support
(LTS). As of November 2026:

- **Jazzy Jalisco** - LTS, until May 2029, Ubuntu 24.04 Tier 1.
- **Lyrical Luth** - LTS, released May 2026, until May 2031, Ubuntu 26.04 Tier 1.
- **Humble Hawksbill** - LTS, ends May 2027, Ubuntu 22.04.
- Kilted Kaiju (non-LTS) ends in November 2026, and ROS 1 (Noetic) reached end of life on 31 May 2025.

This course targets **Jazzy + Ubuntu 24.04**. Most courses, books, and reference robots from
2024-2026 aim at Jazzy, while learning material for Lyrical is still thin. Korean-language paid
courses are often based on Humble, so read `humble` as `jazzy` in their commands - and build
the habit of **checking the distribution first** for any material you pick up.

## Example

Observe the graph with turtlesim. Start the nodes in two terminals, then inspect from a third.

```bash
source /opt/ros/jazzy/setup.bash          # first, in every terminal
ros2 run turtlesim turtlesim_node         # terminal 1
ros2 run turtlesim turtle_teleop_key      # terminal 2

ros2 node list                            # /turtlesim, /teleop_turtle
ros2 topic list -t                        # topics and their message types
ros2 topic echo /turtle1/pose             # watch the data flow
ros2 interface show geometry_msgs/msg/Twist
ros2 service call /clear std_srvs/srv/Empty
ros2 param get /turtlesim background_r
ros2 action send_goal /turtle1/rotate_absolute \
  turtlesim/action/RotateAbsolute "{theta: 1.57}" --feedback
```

**Exercise:** (1) Use the commands above to tabulate turtlesim's nodes, topics, services, and
actions. (2) Draw the same graph with `rqt_graph` and compare it against your table.
(3) Run `export ROS_DOMAIN_ID=7` in one terminal only and explain how the result of
`ros2 node list` changes.

## Self-check questions

1. Would you build the interface that tells a robot arm to "pick up the object" as a topic, a service, or an action? Why?
2. What happens when a lidar node publishes best effort but a subscriber demands reliable?
3. Give two reasons to recommend Jazzy over Humble to someone starting to learn at the end of 2026.

## How to study this stage

1. **Official tutorials (first):** work through *Beginner: CLI tools* in the Jazzy Tutorials in
   order, with the documentation's distribution selector set to Jazzy. If Korean is easier, keep
   the Wikidocs translation open beside it.
2. **This lesson:** read the table of communication mechanisms and the QoS section, then sketch
   on paper how the code of earlier modules (PID, path following, filtering) would split into
   nodes and topics.
3. **Practice:** take the quiz in the Korean original (`rc quiz m8-ros2-concepts-distros`), then
   run the example commands and the exercise yourself. If you have no installation to work in,
   look at the Docker approach of L8.4 first.
4. **Check:** find the EOL of the distribution you are using in the Releases table and note it down.

## References

- ROS 2 Documentation, Releases - <https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases.rst>
- ROS 2 Jazzy Tutorials, Beginner: CLI tools - <https://docs.ros.org/en/jazzy/Tutorials.html>
- ROS 2 Jazzy documentation in Korean (Wikidocs) - <https://wikidocs.net/book/16208>
