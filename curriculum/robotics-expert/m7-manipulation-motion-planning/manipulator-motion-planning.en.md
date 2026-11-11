---
id: m7-manipulator-motion-planning
lang: en
title: "Manipulator motion planning: configuration space obstacles and OMPL"
summary: Compute directly, on a 2-link arm, what shape a workspace obstacle takes in joint configuration space, then find a collision-free joint path with grid A* on a torus. Follow that with the OMPL sampling planners used on high-dimensional arms and the plan → simplify → time-parameterize pipeline.
objectives:
  - Map workspace obstacles into joint configuration space obstacles $C_{obs}$ through link collision checking, and explain the torus topology of joint angles.
  - Find a collision-free path with grid A* in the configuration space of a 2-DOF arm, and explain why sampling-based planners are needed beyond six degrees of freedom.
  - Explain OMPL's main planners (RRTConnect, RRT*, PRM) and MoveIt 2's plan → simplify → time-parameterize flow.
tags: [manipulator, motion-planning, configuration-space, collision-checking, ompl]
---

# Manipulator motion planning: configuration space obstacles and OMPL

In M6 the configuration space of a mobile robot was a plane with inflated obstacles. A
manipulator's configuration is a vector of joint angles, and a single ball in the workspace
becomes a curved band in joint space. This lesson computes that shape directly and connects it to
why six-joint arms use OMPL.

## Concepts

### Joint configuration space and $C_{obs}$

The configuration space of $n$ revolute joints is the torus $T^n$. Since $-\pi$ and $\pi$ are the
same point, the grid wraps at both ends too. If any link overlaps an obstacle, then
$\theta \in C_{obs}$. Because the forward kinematics are nonlinear, $C_{obs}$ is not convex, and
it also includes **self-collisions** between links.

### Dimension and collision checking

At six degrees of freedom and 100 cells per joint there are $10^{12}$ cells, so real arms use the
sampling-based planning of M6, and the bottleneck becomes **collision checking**. MoveIt 2 checks
collisions between link collision geometry and planning scene objects with FCL, and skips
unnecessary self-collision checks using the "never colliding" link pairs listed in the SRDF.

### OMPL and the planning pipeline

**OMPL (the Open Motion Planning Library)** is a collection of sampling planners such as
RRTConnect, RRT*, PRM, and KPIECE, with collision checking provided by MoveIt 2. MoveIt 2's
default is the bidirectional-tree RRTConnect; choose Pilz for straight-line and circular motions,
or CHOMP and STOMP when smoothness matters. The full flow is:

1. **Plan:** a sequence of collision-free waypoints (pose goals are converted through IK).
2. **Simplify:** shortcutting (M6).
3. **Time parameterization:** assign timing from the limits (lesson 3).
4. **Execute:** the ros2_control trajectory controller (next lesson).

## Key formulas

Configuration space obstacles ($A(\theta)$ is the region the robot occupies at configuration
$\theta$, $\mathcal{O}$ the obstacles):

$$C_{obs} = \{\theta \in T^n \mid A(\theta) \cap \mathcal{O} \neq \varnothing\},\qquad C_{free} = T^n \setminus C_{obs}$$

Joint distance on the torus (the grid heuristic):
$d_i = \min(|\theta_i - \theta_i'|,\, 2\pi - |\theta_i - \theta_i'|)$.

## Example

```python
import heapq

import numpy as np

L1, L2 = 1.0, 0.8
OBST = np.array([[1.0, 0.9, 0.3], [-0.2, -1.2, 0.3]])  # circular workspace obstacles (cx, cy, r)
N = 180  # grid cells per joint (2-degree spacing)
th = np.linspace(-np.pi, np.pi, N, endpoint=False)


def link_points(q1, q2, n=15):
    """The (x, y) of sample points along the two links."""
    s = np.linspace(0, 1, n)
    q1, q2 = np.asarray(q1)[..., None], np.asarray(q2)[..., None]
    ex, ey = L1 * np.cos(q1), L1 * np.sin(q1)
    p1 = np.stack([s * ex, s * ey], -1)
    p2 = np.stack([ex + s * L2 * np.cos(q1 + q2), ey + s * L2 * np.sin(q1 + q2)], -1)
    return np.concatenate([p1, p2], axis=-2)


def in_collision(q1, q2):
    pts = link_points(q1, q2)
    d = np.linalg.norm(pts[..., None, :] - OBST[:, :2], axis=-1)
    return (d < OBST[:, 2]).any(axis=(-1, -2))


# 1) compute the configuration space obstacles C_obs on a grid
Q1, Q2 = np.meshgrid(th, th, indexing="ij")
C_obs = in_collision(Q1, Q2)
ws = (OBST[:, 2] ** 2).sum() / ((L1 + L2) ** 2 - (L1 - L2) ** 2)
print(
    f"workspace blocked by obstacles {ws * 100:.1f}% -> colliding joint configurations {C_obs.mean() * 100:.1f}%"
)


def idx(q):
    return tuple(np.round((np.asarray(q) + np.pi) / (2 * np.pi) * N).astype(int) % N)


# 2) check whether straight-line interpolation in joint space is blocked
qa, qb = np.array([-0.3, 0.2]), np.array([1.6, -0.4])
line = np.linspace(qa, qb, 200)
print("start/goal in collision:", bool(in_collision(*qa)), bool(in_collision(*qb)))
print("joint-space straight path in collision:", bool(in_collision(line[:, 0], line[:, 1]).any()))


# 3) A* on the torus grid (-pi and pi are neighbors)
def astar(start, goal):
    def h(a):
        d = np.abs(np.subtract(a, goal))
        return float(np.hypot(*np.minimum(d, N - d)))

    openq, came, cost = [(h(start), start)], {start: None}, {start: 0.0}
    nbrs = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]
    while openq:
        _, cur = heapq.heappop(openq)
        if cur == goal:
            path = []
            while cur is not None:
                path.append(cur)
                cur = came[cur]
            return path[::-1]
        for di, dj in nbrs:
            nxt = ((cur[0] + di) % N, (cur[1] + dj) % N)
            if C_obs[nxt]:
                continue
            c = cost[cur] + np.hypot(di, dj)
            if c < cost.get(nxt, np.inf):
                cost[nxt], came[nxt] = c, cur
                heapq.heappush(openq, (c + h(nxt), nxt))
    return None


path = astar(idx(qa), idx(qb))
q_path = np.unwrap(th[np.array(path)], axis=0)
length = np.linalg.norm(np.diff(q_path, axis=0), axis=1).sum()
print(f"A* path: {len(path)} points, joint-space length {length:.2f} rad")
print(f"straight-line distance (lower bound) {np.linalg.norm(qb - qa):.2f} rad")
fine = np.concatenate([np.linspace(a, b, 5) for a, b in zip(q_path[:-1], q_path[1:])])
print("fine re-check collision:", bool(in_collision(fine[:, 0], fine[:, 1]).any()))
```

The two circles cover about 5.6% of the workspace but block about 15.6% of joint configurations,
because the whole link has to avoid them. The joint-space straight line (1.99 rad) is blocked and
A* finds a detour of about 4.68 rad, which stays collision-free even under a dense re-check.
Since the path is a staircase, in practice it goes through simplification and time
parameterization.

**Exercise:** (1) Plot `C_obs` as an image and look at the band shape. (2) Port the RRT of M6 into
this joint space and compare it against A*. (3) Raise the radius to 0.4 m and check whether the
start and goal become disconnected.

## Self-check questions

1. Why does a small workspace obstacle block a wide region of joint space?
2. Which paths do you miss if the joint-angle grid does not join $-\pi$ to $\pi$?
3. Why does MoveIt 2 put its planning results through simplification and time parameterization?

## How to study this stage

1. **Video (first):** watch the configuration space obstacle portion of the Modern Robotics Ch. 10
   videos.
2. **This lesson plus the example:** be sure to draw the figure of exercise (1). The intuition for
   manipulator planning is in that picture.
3. **Textbook:** read the torus topology of LaValle Ch. 4 and the collision checking resolution of
   Ch. 5.
4. **Problems:** take the quiz in the Korean original (`rc quiz m7-manipulator-motion-planning`).
5. **Depth (optional):** Tedrake's Motion Planning chapter and the RRT-Connect project of AutoRob.

## References

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 10 - <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics Ch. 10 Motion Planning videos - <https://www.youtube.com/playlist?list=PLggLP4f-rq01Q3clJrnWFPRtpUwSlr4mG>
- Steven M. LaValle, *Planning Algorithms* - <https://lavalle.pl/planning/>
- Russ Tedrake, *Robotic Manipulation* - <https://manipulation.mit.edu/>
- University of Michigan, AutoRob - <https://autorob.org/>
- Ioan A. Şucan, Mark Moll, Lydia E. Kavraki, "The Open Motion Planning Library", IEEE Robotics & Automation Magazine 2012 (the OMPL paper, no link)
