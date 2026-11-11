---
id: m5-graph-slam-slam-toolbox
lang: en
title: "Graph SLAM in outline, and reading SLAM Toolbox"
summary: View SLAM as a least-squares problem over a pose graph of pose nodes and relative-measurement edges, and watch in numpy how a loop closure undoes accumulated error. Then read, alongside its configuration, how ROS 2's SLAM Toolbox divides scan matching (front end) from graph optimization (back end) and publishes map → odom.
objectives:
  - Explain the difference between online and full SLAM and the roles of the front end and back end of graph SLAM.
  - Solve a pose graph of relative-measurement edges and loop closures as an information-matrix-weighted least-squares problem.
  - Read and explain SLAM Toolbox's main parameters, its mapping and localization modes, and the tf and topics it publishes.
tags: [slam, graph-slam, pose-graph, loop-closure, slam-toolbox, ros2]
---

# Graph SLAM in outline, and reading SLAM Toolbox

The previous lessons showed that knowing the pose lets you build a map, and having a map lets you
correct the pose. Solving both at once, when you know neither, is SLAM. Chaining scan matches
alone accumulates small errors until the map bends and walls are drawn twice where you return to
the same place. Graph SLAM adds the constraint "this is somewhere I have been before" - a **loop
closure** - and re-optimizes the whole trajectory to undo that accumulated error.

## Concepts

### Online SLAM and full SLAM

- **Online SLAM:** estimates only the current pose and the map,
  $p(x_t, m \mid z_{1:t}, u_{1:t})$. EKF-SLAM and the particle-based FastSLAM and GMapping belong here.
- **Full SLAM:** estimates the entire trajectory $x_{1:t}$. Being able to correct past poses makes
  it well suited to loop closure. Graph SLAM is the representative method.

### The pose graph

- **Nodes:** robot poses $x_i$ (usually one per fixed distance or angle traveled).
- **Edges:** a relative measurement $z_{ij}$ between two poses and its confidence (the information
  matrix $\Omega_{ij}$). Between consecutive nodes it comes from odometry and scan matching;
  between distant nodes, from loop closure.
- **Front end:** creates the edges (scan matching, loop candidate search). A single wrong loop
  closure ruins the whole map, so verification matters.
- **Back end:** minimizes the error of all edges simultaneously (Gauss-Newton,
  Levenberg-Marquardt). The matrix is sparse, so even thousands of nodes solve quickly.

### SLAM Toolbox

Steve Macenski's SLAM Toolbox is the default 2D lidar SLAM of ROS 2 and Nav2. It creates edges by
Karto-style correlative scan matching and optimizes the pose graph with Ceres. It publishes
`/map` (an OccupancyGrid) and the `map → odom` transform. Since the EKF of the previous lesson
handles `odom → base_link`, the tf tree completes as
`map → odom → base_link → laser`.

## Key formulas

The edge error and the total cost:

$$e_{ij}(x) = z_{ij} - \hat z_{ij}(x_i, x_j),\qquad x^{\star} = \arg\min_x \sum_{(i,j)} e_{ij}^\top\,\Omega_{ij}\,e_{ij}$$

Linearizing leads to the normal equations $H\,\Delta x = -b$, where
$H = \sum J_{ij}^\top \Omega_{ij} J_{ij}$ and $b = \sum J_{ij}^\top \Omega_{ij} e_{ij}$. Because
every measurement is relative, the first pose must be fixed (the gauge freedom) for $H$ to be
invertible.

## Example

A 2D position pose graph with rotation left out. The robot goes around a square back to the
origin, and the odometry has a consistent bias in the same direction at every step. With position
alone the problem is linear, so a single solve finishes it.

```python
import numpy as np

rng = np.random.default_rng(2)
# true trajectory: around a 4 m x 4 m square in 1 m steps, back to the origin (17 nodes)
dirs = [(1, 0)] * 4 + [(0, 1)] * 4 + [(-1, 0)] * 4 + [(0, -1)] * 4
moves = [np.array(d, float) for d in dirs]
truth = np.cumsum([np.zeros(2)] + moves, axis=0)
n = len(truth)

# edges: (i, j, measured x_j - x_i, information weight)
edges = []
for i, d in enumerate(moves):  # odometry: a constant bias plus noise
    edges.append((i, i + 1, d + [0.03, 0.02] + rng.normal(0, 0.03, 2), 1 / 0.03**2))
loop_z = truth[0] - truth[n - 1] + rng.normal(0, 0.02, 2)
edges.append((n - 1, 0, loop_z, 1 / 0.02**2))  # loop closure: "back at the origin"

odom_only = np.cumsum([np.zeros(2)] + [e[2] for e in edges[:-1]], axis=0)

H = np.zeros((2 * n, 2 * n))
b = np.zeros(2 * n)
for i, j, z, w in edges:
    A = np.zeros((2, 2 * n))  # Jacobian of the error e = (x_j - x_i) - z
    A[:, 2 * i : 2 * i + 2], A[:, 2 * j : 2 * j + 2] = -np.eye(2), np.eye(2)
    H += w * A.T @ A
    b += w * A.T @ z
H[:2, :2] += 1e6 * np.eye(2)  # anchor the first pose at the origin
x = np.linalg.solve(H, b).reshape(n, 2)


def rmse(est):
    return np.sqrt(np.mean(np.sum((est - truth) ** 2, axis=1)))


print(f"odometry only: RMSE {rmse(odom_only):.3f} m, endpoint {np.linalg.norm(odom_only[-1]):.3f} m")
print(f"pose graph   : RMSE {rmse(x):.3f} m, endpoint {np.linalg.norm(x[-1]):.3f} m")
```

With odometry alone the endpoint lands about 0.6 m from the origin, but a single loop closure edge
spreads the error evenly over the whole trajectory, cutting the RMSE from 0.38 m to about 0.03 m.
Real SLAM is nonlinear because of rotation, so it iterates this solve with Gauss-Newton.

### Reading the SLAM Toolbox configuration

The first entries to look at in `mapper_params_online_async.yaml` (an excerpt):

```yaml
slam_toolbox:
  ros__parameters:
    mode: mapping               # localization uses a saved graph for localization only
    odom_frame: odom
    map_frame: map
    base_frame: base_footprint
    scan_topic: /scan
    resolution: 0.05            # occupancy grid cell size [m]
    minimum_travel_distance: 0.5   # distance traveled before a new node is created
    do_loop_closing: true
```

**Exercise:** (1) Solve with the loop closure edge removed, confirm the result equals the odometry,
and explain why. (2) Deliberately offset the loop closure measurement by 1 m and see how the map
breaks. (3) Read the Nav2 "Navigating While Mapping" tutorial and diagram the topics and tf that
SLAM Toolbox subscribes to and publishes.

## Self-check questions

1. What do the front end and the back end of graph SLAM each do, and which one is responsible for a wrong loop closure?
2. Why do the normal equations fail to solve if the first pose is not fixed?
3. Which tf do SLAM Toolbox and robot_localization each publish to complete the tree?

## How to study this stage

1. **Videos (first):** watch Stachniss's "Introduction to SLAM" then "Graph-based SLAM."
2. **This lesson plus the example:** run the example, plot the trajectory to compare before and
   after loop closure, then do the exercises.
3. **Reading the tools:** read the Nav2 "Navigating While Mapping" (slam_toolbox) tutorial and the
   SLAM chapter of Choi Jong-myung's Wikidocs book, matching the configuration file against this
   lesson.
4. **Problems:** take the quiz in the Korean original (`rc quiz m5-graph-slam-slam-toolbox`).
5. **Depth (optional):** broaden with the ROB 530 SLAM assignment and Stachniss's Graph SLAM with
   Landmarks and Robust LS lectures.

## References

- Cyrill Stachniss, "Introduction to SLAM" - <https://www.youtube.com/watch?v=0I30M6yTklo>
- Cyrill Stachniss, "Graph-based SLAM" - <https://www.youtube.com/watch?v=uHbRKvD8TWg>
- Nav2 tutorial, "Navigating While Mapping" -
  <https://docs.nav2.org/rolling/tutorials/general_tutorials/navigation2_with_slam/navigation2_with_slam/>
- 최종명, "ROS2로 배우는 자율주행 로봇 센서 융합과 SLAM" (Wikidocs, in Korean) - <https://wikidocs.net/book/18464>
- University of Michigan, ROB 530 Mobile Robotics - <https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public>
- Steve Macenski, Ivona Jambrecic, "SLAM Toolbox: SLAM for the dynamic world" (JOSS, 2021)
