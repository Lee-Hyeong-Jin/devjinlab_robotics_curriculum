---
id: m7-trajectory-generation
lang: en
title: "Trajectory generation: joint and task space interpolation and time optimization"
summary: Separate the path from the time scaling to build manipulator trajectories with cubic and quintic polynomials and trapezoidal velocity profiles, find the minimum time under velocity and acceleration limits, and compare joint-space against task-space straight-line interpolation in numpy.
objectives:
  - Split a trajectory into a path $\theta(s)$ and a time scaling $s(t)$, and compute the boundary conditions and the maximum velocity and acceleration of cubic and quintic polynomials.
  - Find the minimum travel time under per-joint velocity and acceleration limits and explain how several joints are synchronized.
  - Compare the advantages and disadvantages of joint-space and task-space (Cartesian) interpolation in terms of the end-effector path and the joint motion.
tags: [manipulator, trajectory, time-scaling, polynomial, interpolation]
---

# Trajectory generation: joint and task space interpolation and time optimization

M6 distinguished a "path" (no time) from a "trajectory" (with time). A manipulator likewise
cannot move until its sequence of joint values carries timing that stays within the limits. The
result is the reference trajectory $\theta_d(t), \dot{\theta}_d(t), \ddot{\theta}_d(t)$ that the
computed-torque controller of the previous lesson consumes.

## Concepts

### Separating the path from the time scaling

A point-to-point move fixes the path as $\theta(s) = \theta_a + s(\theta_b - \theta_a)$,
$s \in [0, 1]$, and the speed through the time scaling $s(t)$. Then
$\dot{\theta} = \dot{s}(\theta_b - \theta_a)$, so all joints start and finish together, moving in
the same proportion (joint synchronization).

- **Cubic polynomial:** zero velocity at both ends. The acceleration at the endpoints is not
  zero, so torque jumps at the moments of starting and stopping.
- **Quintic polynomial:** zero velocity and acceleration at both ends. Less vibration, but for
  the same duration the maximum speed is higher.
- **Trapezoidal velocity:** maximum acceleration → constant speed → maximum deceleration. The
  fastest within the limits, but its acceleration is discontinuous, so in practice it is smoothed
  into an S-curve (jerk-limited).

### Time optimization

Choose the shortest $T$ at which every joint stays within its limits. The joint with the largest
travel relative to its limits sets the time, and the rest move more slowly to stay synchronized.
Minimum-time parameterization of a whole path with many waypoints is solved by the phase-plane
($s, \dot{s}$) method of Modern Robotics §9.4; MoveIt 2's TOTG belongs to this family.

### Joint space versus task space

- **Joint-space interpolation:** cheap to compute, with no joint-limit or singularity problems.
  The end-effector path comes out curved.
- **Task-space interpolation:** the end-effector follows a straight line (pulling a drawer,
  welding). It requires IK at every point, and passing through a singularity makes joint
  velocities explode (lesson 1).

## Key formulas

Cubic and quintic time scalings ($\tau = t/T$) and their maxima:

$$s_3 = 3\tau^2 - 2\tau^3,\quad \max\dot{\theta} = \tfrac{3}{2}\tfrac{\Delta}{T},\quad \max\ddot{\theta} = 6\tfrac{\Delta}{T^2}$$

$$s_5 = 10\tau^3 - 15\tau^4 + 6\tau^5,\quad \max\dot{\theta} = \tfrac{15}{8}\tfrac{\Delta}{T},\quad \max\ddot{\theta} = \tfrac{10}{\sqrt{3}}\tfrac{\Delta}{T^2}$$

Trapezoidal minimum time (when $\Delta > v_{max}^2 / a_{max}$):
$T = \Delta / v_{max} + v_{max} / a_{max}$.

## Example

```python
import numpy as np


def cubic(tau):
    """Cubic time scaling s(tau), tau = t/T in [0, 1]. Zero velocity at both ends."""
    return 3 * tau**2 - 2 * tau**3, 6 * tau - 6 * tau**2, 6 - 12 * tau


def quintic(tau):
    """Quintic time scaling. Zero velocity and acceleration at both ends."""
    s = 10 * tau**3 - 15 * tau**4 + 6 * tau**5
    sd = 30 * tau**2 - 60 * tau**3 + 30 * tau**4
    sdd = 60 * tau - 180 * tau**2 + 120 * tau**3
    return s, sd, sdd


tau = np.linspace(0, 1, 2001)
for name, fn in [("cubic", cubic), ("quintic", quintic)]:
    s, sd, sdd = fn(tau)
    print(
        f"{name:7s} a(0)={sdd[0]:.0f}  max v*T/delta={sd.max():.3f}  "
        f"max a*T^2/delta={np.abs(sdd).max():.3f}"
    )

# 1) time optimization: the minimum T possible given joint travel delta and the limits vmax, amax
delta = np.array([1.2, -0.6, 2.0])  # travel of three joints [rad]
vmax, amax = 1.0, 2.0  # rad/s, rad/s^2
d = np.abs(delta).max()  # the joint that moves most sets the time
for name, kv, ka in [("cubic", 1.5, 6.0), ("quintic", 1.875, 10 / np.sqrt(3))]:
    T = max(kv * d / vmax, np.sqrt(ka * d / amax))
    print(f"{name:7s} minimum T = {T:.2f} s")
T_trap = d / vmax + vmax / amax if d > vmax**2 / amax else 2 * np.sqrt(d / amax)
print(f"trapezoidal minimum T = {T_trap:.2f} s")

# 2) joint space versus task space straight-line interpolation
L1, L2 = 1.0, 0.8


def fk(q):
    return np.array(
        [L1 * np.cos(q[0]) + L2 * np.cos(q[0] + q[1]), L1 * np.sin(q[0]) + L2 * np.sin(q[0] + q[1])]
    )


def ik(p):  # elbow-down analytic IK (M2)
    c2 = (p @ p - L1**2 - L2**2) / (2 * L1 * L2)
    q2 = np.arccos(np.clip(c2, -1, 1))
    q1 = np.arctan2(p[1], p[0]) - np.arctan2(L2 * np.sin(q2), L1 + L2 * np.cos(q2))
    return np.array([q1, q2])


pa, pb = np.array([1.4, -0.4]), np.array([0.4, 1.2])
qa, qb = ik(pa), ik(pb)
s = quintic(np.linspace(0, 1, 101))[0]
u = (pb - pa) / np.linalg.norm(pb - pa)  # unit vector along the straight line


def dist_to_line(p):
    r = p - pa
    return np.linalg.norm(r - (r @ u) * u)


dev_joint = max(dist_to_line(fk(qa + si * (qb - qa))) for si in s)
q_task = [ik(pa + si * (pb - pa)) for si in s]
len_task = np.abs(np.diff(q_task, axis=0)).sum(axis=0)
print(f"joint space: deviation from the line {dev_joint * 100:.1f} cm, joint travel {np.abs(qb - qa).round(2)}")
print(f"task space : line held exactly, joint travel {len_task.round(2)}")
```

The quintic's maximum speed is 25% higher than the cubic's, so the minimum times come out 3.00 s
for cubic, 3.75 s for quintic, and 2.50 s for trapezoidal - the smoother, the slower. Joint-space
interpolation leaves the end-effector about 39 cm off the straight line, while task-space
interpolation holds the line at the cost of folding and extending the arm, raising the second
joint's travel from 0.33 to 1.17 rad.

**Exercise:** (1) Check whether the three-joint quintic trajectory of example 1 stays within the
limits. (2) Implement the trapezoidal $s(t)$ including the triangular case. (3) Change `pb` so
that the task-space straight line passes near the origin and observe the joint velocities.

## Self-check questions

1. Why is a quintic polynomial preferred over a cubic, and at what cost?
2. How is the total time decided when the joints have different amounts to travel?
3. Give two situations in which task-space straight-line interpolation can be more dangerous.

## How to study this stage

1. **Textbook (first):** organize the separation of path and time scaling from Modern Robotics
   §9.1-9.2.
2. **This lesson plus the example:** derive the coefficients 1.5, 1.875, 6, and 5.77 in the table
   yourself and match them against the code.
3. **Video:** watch waypoint polynomials and time-optimal scaling (§9.4) in the Ch. 9 videos.
4. **Problems:** take the quiz in the Korean original (`rc quiz m7-trajectory-generation`), then do
   exercises (1) through (3).
5. **Verification (optional):** compare the Robotics Toolbox's `jtraj` and `ctraj` results against
   the example.

## References

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 9 - <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics lecture videos - <https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos>
- Coursera Modern Robotics Specialization - <https://www.coursera.org/specializations/modernrobotics>
- Peter Corke, Robotics Toolbox for Python - <https://github.com/petercorke/robotics-toolbox-python>
- Tobias Kunz, Mike Stilman, "Time-Optimal Trajectory Generation for Path Following with Bounded Acceleration and Velocity", RSS 2012 (the original TOTG paper, no link)
