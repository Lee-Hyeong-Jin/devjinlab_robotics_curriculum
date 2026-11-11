---
id: m6-path-smoothing-trajectory
lang: en
title: "Path smoothing and trajectory generation"
summary: Smooth the jagged paths produced by grid and sampling planners (gradient descent smoothing) and attach a velocity profile that respects curvature and acceleration limits, turning the path into a trajectory with timing. Along the way, see the difference between a path and a trajectory and where Nav2's smoother server sits.
objectives:
  - Distinguish a path from a trajectory and explain why planner output needs smoothing and time parameterization.
  - Implement gradient descent smoothing with a data term and a smoothness term and explain the role of the two weights.
  - Build a trapezoidal velocity profile from a curvature-based speed limit and forward and backward acceleration passes.
tags: [path-smoothing, trajectory-generation, curvature, velocity-profile, time-parameterization]
---

# Path smoothing and trajectory generation

The A* of lesson 1 produced a staircase path turning in 45° steps, and the RRT of lesson 2 a
zigzag. At those corners the curvature approaches infinity, so the robot would have to nearly
stop to turn. Planner output is also only a **path**: a sequence of points with no timing. For a
robot to follow it, you need a **trajectory** that fixes when and at what speed each point is
passed.

## Concepts

### Smoothing

The simplest method is **shortcutting**. Pick two points on the path and, if the straight line
between them is collision-free, delete the points in between. It is particularly effective on RRT
paths.

**Gradient descent smoothing** moves each point $y_i$ under two forces. The data term pulls it
toward the original point $x_i$ so the path does not stray too far, and the smoothness term pulls
it toward the midpoint of its neighbors, straightening the corners. A larger smoothness weight
gives a straighter path but moves it farther from the original - and thus from the safe region
the planner verified. That is why real smoothers re-check collisions against the costmap. Nav2
puts plugins such as the Simple Smoother and the Constrained Smoother in a **smoother server**
separate from the planner.

### Time parameterization (the velocity profile)

Resample the path by arc length $s$, then set a speed limit at each point.

- **Maximum speed** $v_{max}$
- **Curvature limit:** where the curvature is $\kappa$, keep the lateral acceleration $v^2\kappa$
  within its limit.
- **Acceleration and deceleration limits:** trim the speed from the front under the acceleration
  limit and from the back under the deceleration limit (the forward and backward passes).

The result is a trapezoid of accelerate-cruise-decelerate on straights, with a dip carved out of
it at corners. It is the same idea as the time scaling of Modern Robotics Ch. 9.

## Key formulas

Gradient descent smoothing (endpoints fixed):

$$y_i \leftarrow y_i + \alpha\,(x_i - y_i) + \beta\,(y_{i-1} + y_{i+1} - 2y_i)$$

The curvature of a plane curve and the curvature speed limit:

$$\kappa = \frac{|x'y'' - y'x''|}{(x'^2 + y'^2)^{3/2}},\qquad v(s) \le \sqrt{a_{lat}/\kappa(s)}$$

The acceleration limit (forward pass; the backward pass only reverses direction):

$$v_i^2 \le v_{i-1}^2 + 2\,a_{max}\,\Delta s$$

## Example

Smooth a staircase path of the kind a grid planner would produce, then attach the same velocity
profile to the original and the smoothed path.

```python
import numpy as np

# a staircase path of the kind grid A* would produce (0.5 m spacing, 45-degree turns)
raw = np.array([[0, 0], [1, 0], [2, 0], [3, 1], [4, 2], [4, 3], [4, 4], [5, 5], [6, 5], [7, 5]])
path = raw * 0.5


def smooth(path, w_data=0.1, w_smooth=0.4, iters=500):
    """Stay near the original points (data term) while pulling toward the neighbors' mean
    (smoothness term). Both endpoints are fixed."""
    y = path.copy()
    for _ in range(iters):
        y[1:-1] += w_data * (path[1:-1] - y[1:-1]) + w_smooth * (y[:-2] + y[2:] - 2 * y[1:-1])
    return y


def resample(path, ds=0.05):
    seg = np.linalg.norm(np.diff(path, axis=0), axis=1)
    s = np.r_[0, np.cumsum(seg)]
    s_new = np.arange(0, s[-1], ds)
    return np.c_[np.interp(s_new, s, path[:, 0]), np.interp(s_new, s, path[:, 1])], s_new


def curvature(p):
    d1, d2 = np.gradient(p, axis=0), np.gradient(np.gradient(p, axis=0), axis=0)
    return np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / np.linalg.norm(d1, axis=1) ** 3


def velocity_profile(s, kappa, v_max=0.5, a_max=0.3, a_lat=0.2):
    v = np.minimum(
        v_max, np.sqrt(a_lat / np.maximum(kappa, 1e-6))
    )  # curvature limit v <= sqrt(a_lat/kappa)
    v[0] = v[-1] = 0.0  # start and stop
    ds = np.diff(s)
    for i in range(1, len(v)):  # forward: acceleration limit v_i^2 <= v_{i-1}^2 + 2 a ds
        v[i] = min(v[i], np.sqrt(v[i - 1] ** 2 + 2 * a_max * ds[i - 1]))
    for i in range(len(v) - 2, -1, -1):  # backward: deceleration limit
        v[i] = min(v[i], np.sqrt(v[i + 1] ** 2 + 2 * a_max * ds[i]))
    t = np.r_[
        0, np.cumsum(2 * ds / np.maximum(v[1:] + v[:-1], 1e-6))
    ]  # time from segment mean speed
    return v, t


for name, p in [("original path", path), ("smoothed", smooth(path))]:
    dense, s = resample(p)
    kappa = curvature(dense)
    v, t = velocity_profile(s, kappa)
    print(
        f"{name}: length {s[-1]:.2f} m, max curvature {kappa.max():6.2f} 1/m, "
        f"corner speed limit {min(0.5, np.sqrt(0.2 / kappa.max())):.2f} m/s, travel time {t[-1]:.1f} s"
    )
```

Smoothing shortens the path from 5.10 m to 4.35 m and drops the maximum curvature from about 9 to
2.0 1/m, raising the corner speed limit from 0.15 to 0.32 m/s. Travel time goes from 15.3 s to
11.0 s. Note that the curvature of the original path is an approximation that depends on the
resampling interval.

**Exercise:** (1) Set `w_smooth` to 0.1, 0.25, and 0.45 and measure the maximum deviation of the
path from the original points. (2) On the costmap of lesson 3, check the cost at each point of the
smoothed path and add a rule that stops the smoothing update for a point that touches a lethal
cell. (3) Plot `v` from `velocity_profile` against $s$ and find the trapezoid and the dips at the
corners.

## Self-check questions

1. What is the difference between a path and a trajectory, and which of the two does the local controller take as input?
2. What do you gain and what do you lose by increasing the smoothness weight?
3. What happens if you omit the backward (deceleration) pass of the velocity profile?

## How to study this stage

1. **Textbook (first):** watch the time scaling and trapezoidal profile of Modern Robotics Ch. 9
   together with the videos.
2. **This lesson plus the example:** run the example, plot both paths and the velocity curves, and
   do the exercises.
3. **Connecting back:** apply shortcutting and then smoothing to the RRT path of lesson 2 and
   record the change in length and curvature.
4. **Problems:** take the quiz in the Korean original (`rc quiz m6-path-smoothing-trajectory`).
5. **Depth (optional):** skim planning that handles differential constraints directly, in the Nav2
   smoother server documentation and LaValle Part IV.

## References

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 9-10 - <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics Videos - <https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos>
- Steven M. LaValle, *Planning Algorithms*, Cambridge University Press - <https://lavalle.pl/planning/>
- Nav2 Documentation - <https://docs.nav2.org/rolling/index.html>
