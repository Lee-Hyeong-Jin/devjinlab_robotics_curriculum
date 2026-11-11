---
id: m3-path-following
lang: en
title: Path following
summary: Combine the differential drive model with PID to implement go-to-goal, waypoint following, and Pure Pursuit controllers, and evaluate them by their arrival error.
objectives:
  - Implement a go-to-goal controller that turns distance and heading error into linear and angular velocity commands.
  - Implement a follower that advances through a waypoint list using an acceptance radius.
  - Derive the Pure Pursuit curvature formula and explain how the lookahead distance affects tracking.
tags: [mobile-robot, control, path-following, pure-pursuit]
---

# Path following

This is the last lesson of M3. Combining the differential drive model (what moves)
with PID (how error is reduced) makes the robot **arrive at a goal and follow a
given path**. Tasks such as line tracing and goal seeking can all be solved with
one of the controllers in this lesson.

## Concepts

### 1) Go-to-goal

Given the robot pose $(x, y, \theta)$ and a goal $(x_g, y_g)$, define two errors.

- Distance error $\rho$: the straight-line distance to the goal
- Heading error $\alpha$: the difference between the direction to the goal and the current heading (always wrapped into $(-\pi, \pi]$)

Compute $\omega$ with P (or PID) control on $\alpha$, and make $v$ proportional to
$\rho$ with an upper bound. Shrinking $v$ when $\alpha$ is large (for example by
multiplying by $\cos\alpha$) keeps the robot from swinging far off in the wrong
direction. Moving the goal into the **robot frame** with the inverse transform
from M1 simplifies the equations.

### 2) Waypoint following

Split the path into a list of points and advance to the next one as soon as the
distance to the current waypoint falls below an **acceptance radius**
$\varepsilon$. It is easy to implement, but the robot decelerates and turns at
every point so the motion is choppy, and if $\varepsilon$ is too small the robot
can circle around a point without ever accepting it.

### 3) Pure Pursuit

Keep choosing a point on the path that is a **lookahead distance** $L_d$ away from
the robot, and set the curvature so the robot follows the arc through that point.
As the robot moves the target point slides forward too, which makes the tracking
smooth. A small $L_d$ hugs the path but oscillates; a large one is smooth but cuts
corners widely. Scaling $L_d$ with speed is a common rule in practice.

### Performance metrics

- **Cross-track error:** the perpendicular distance from the path to the robot
- **Final arrival error:** the distance between the last goal point and where the robot stops
- Elapsed time, and peak angular velocity

## Key formulas

$$\rho = \sqrt{(x_g - x)^2 + (y_g - y)^2}, \qquad
\alpha = \operatorname{wrap}\!\big(\operatorname{atan2}(y_g - y,\ x_g - x) - \theta\big)$$

$$v = \min(k_\rho\,\rho,\ v_{\max})\cos\alpha, \qquad \omega = k_\alpha\,\alpha$$

Pure Pursuit: when the lookahead point makes an angle $\alpha$ with the heading in
the robot frame,

$$\kappa = \frac{2\sin\alpha}{L_d}, \qquad \omega = v\,\kappa$$

(equivalently $\kappa = 2y_r / L_d^2$, where $y_r$ is the lateral coordinate of
that point in the robot frame).

## Example

Visit the waypoints of a square path one by one with the go-to-goal controller and
print the final arrival error.

```python
import numpy as np


def wrap(a):
    return np.arctan2(np.sin(a), np.cos(a))


def go_to_goal(pose, goal, k_rho=1.0, k_alpha=4.0, v_max=0.2):
    x, y, th = pose
    dx, dy = goal[0] - x, goal[1] - y
    rho = np.hypot(dx, dy)
    alpha = wrap(np.arctan2(dy, dx) - th)
    v = min(k_rho * rho, v_max) * max(np.cos(alpha), 0.0)  # turn in place if the goal is behind
    return v, k_alpha * alpha, rho


def follow(waypoints, eps=0.05, dt=0.02, t_max=60.0):
    pose, i, traj = np.array([0.0, 0.0, 0.0]), 0, []
    for _ in range(int(t_max / dt)):
        last = i == len(waypoints) - 1
        v, w, rho = go_to_goal(pose, waypoints[i])
        if rho < (0.005 if last else eps):
            if last:
                break
            i += 1
            continue
        pose = pose + np.array([v * np.cos(pose[2]), v * np.sin(pose[2]), w]) * dt
        traj.append(pose.copy())
    return pose, np.array(traj)


wps = [(1, 0), (1, 1), (0, 1), (0, 0)]
final, traj = follow(wps)
print("final arrival error [m]:", round(float(np.hypot(*final[:2])), 4))  # under 0.005
```

**Exercise:** (1) plot the trajectory and compare corner behavior and elapsed time
for $\varepsilon$ = 0.02, 0.05, and 0.2 m. (2) Replace the angular velocity
control with the `PID` class from the PID lesson, add a constant disturbance, and
see how the final arrival error changes. (3) Resample the same square path into
dense points, implement Pure Pursuit, and tabulate the peak cross-track error for
$L_d$ = 0.1, 0.3, and 0.6 m.

## Self-check questions

1. What goes wrong in the go-to-goal controller if the heading error $\alpha$ is not wrapped?
2. In Pure Pursuit, what happens when the lookahead distance is set too small, and what when it is too large?
3. Why can a waypoint acceptance radius close to zero make the robot circle around the goal?

## How to study this stage

1. **Textbook (primary):** read the moving-to-a-point, line following, and path following sections of Corke's *Robotics, Vision and Control* (3rd ed.) Ch. 4 and work through the Python examples.
2. **Primary source:** read just the curvature derivation in Coulter's Pure Pursuit technical report, then derive this lesson's $\kappa = 2\sin\alpha / L_d$ yourself.
3. **This lesson plus the example:** run the example and check the square path and the final arrival error.
4. **Problems:** take the quiz in the Korean original (`rc quiz m3-path-following`), then do exercises (1) through (3). The table from (3) is this module's deliverable.
5. **Wrap-up:** look back over M1-M3 and summarize the flow "coordinate transforms → kinematic model → feedback control → path following" on a single page. For more depth, read the polar-coordinate goal controller (and its stability condition) in Siegwart Ch. 3.

## References

- Peter Corke, *Robotics, Vision and Control: Fundamental Algorithms in Python*, 3rd ed.,
  Springer, 2023 — Ch. 4 "Mobile Robot Vehicles" — <https://link.springer.com/10.1007/978-3-031-06469-2>
- R. Craig Coulter, *Implementation of the Pure Pursuit Path Tracking Algorithm*,
  Carnegie Mellon University Robotics Institute Technical Report, 1992.
- Roland Siegwart, Illah R. Nourbakhsh, Davide Scaramuzza, *Introduction to Autonomous Mobile
  Robots*, 2nd ed., MIT Press, 2011 — Ch. 3 "Mobile Robot Kinematics" (motion control section).
- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 13 —
  <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
