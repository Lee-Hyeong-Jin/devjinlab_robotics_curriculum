---
id: m6-sampling-based-planning
lang: en
title: "Sampling-based planning (RRT, RRT*, PRM)"
summary: For high-dimensional and complex problems whose configuration space resists gridding, cover PRM and RRT, which find paths using only random samples and collision checks, and RRT*, which adds asymptotic optimality. Implement small 2D RRT and RRT* in numpy and compare path lengths.
objectives:
  - Explain why grid search fails in high-dimensional configuration spaces and how sampling-based planning avoids that with collision checks alone.
  - Distinguish the structure and the use cases of PRM (multi-query) and RRT (single-query).
  - Implement RRT's sample-nearest-steer-check loop and RRT*'s parent selection and rewiring in numpy.
tags: [motion-planning, sampling, rrt, rrt-star, prm, collision-checking]
---

# Sampling-based planning (RRT, RRT*, PRM)

The grid search of the previous lesson suits a 2D mobile robot well, but it collapses as
dimensions grow. Even at only 100 cells per axis, the configuration space of a six-joint arm has
$100^6 = 10^{12}$ cells - and $C_{obs}$ cannot be drawn explicitly anyway. Sampling-based
planning explores $C_{free}$ by repeatedly asking a single question: "does this configuration
collide?" The OMPL planners that MoveIt 2 uses in M7 belong to this family.

## Concepts

### PRM (Probabilistic Roadmap)

1. Draw $N$ random configurations from $C_{free}$.
2. Connect each point to its $k$ nearest neighbors, keeping an edge only when the connecting
   segment is collision-free.
3. Attach the start and goal to the roadmap and search it with A*.

Build the roadmap once and it can be reused for many queries in the same environment
(**multi-query**). Its weakness is that samples rarely land in small-volume regions such as
narrow passages.

### RRT (Rapidly-exploring Random Tree)

Grow a tree from the start. Each iteration draws a random point $q_{rand}$, steps a single
distance $\eta$ from the nearest node $q_{near}$ toward it to form $q_{new}$, and adds it if the
segment is collision-free. Points in large empty areas are drawn more often, so the tree spreads
rapidly into unexplored regions (Voronoi bias). Using the goal itself as the sample a few percent
of the time (goal bias) speeds up convergence. It is specialized to one query
(**single-query**), and it will eventually find a solution if one exists (probabilistic
completeness), but the path is wiggly and not optimal.

### RRT*

RRT plus two steps. (1) Choose the parent of $q_{new}$ not as the nearest node but as the node
within radius $r$ with the smallest accumulated cost. (2) **Rewire:** if a neighbor within the
radius would become cheaper by routing through $q_{new}$, change its parent. As samples
accumulate the path cost converges to the optimum (asymptotic optimality). The price is
computation per iteration.

## Key formulas

RRT's steer (a single step $\eta$):

$$q_{new} = q_{near} + \min\!\left(1, \frac{\eta}{\lVert q_{rand} - q_{near}\rVert}\right)(q_{rand} - q_{near})$$

RRT*'s parent selection ($\mathcal{N}$ is the set of neighbors within radius $r$, $c$ the
accumulated cost):

$$\text{parent}(q_{new}) = \arg\min_{q \in \mathcal{N}} \big[c(q) + \lVert q_{new} - q\rVert\big]$$

## Example

Go from (0.5, 0.5) to (9.5, 9.5) in a 10 m × 10 m space, avoiding three circular obstacles.

```python
import numpy as np

rng = np.random.default_rng(1)
obstacles = np.array([[3.0, 3.0, 1.2], [6.0, 6.5, 1.5], [7.5, 2.5, 1.0]])  # (cx, cy, r)
start, goal = np.array([0.5, 0.5]), np.array([9.5, 9.5])
STEP, GOAL_TOL, N_ITER = 0.5, 0.5, 3000


def collision_free(a, b, n=10):
    """True if all n+1 points on the segment a->b lie outside every circle (simple discrete check)."""
    pts = a + np.linspace(0, 1, n + 1)[:, None] * (b - a)
    d = np.linalg.norm(pts[:, None, :] - obstacles[None, :, :2], axis=2)
    return bool(np.all(d > obstacles[:, 2]))


def rrt(star=False, radius=1.5):
    nodes, parent, cost = [start], [-1], [0.0]
    best = None
    for _ in range(N_ITER):
        sample = goal if rng.random() < 0.05 else rng.uniform(0, 10, 2)  # 5% goal bias
        pts = np.array(nodes)
        i_near = int(np.argmin(np.linalg.norm(pts - sample, axis=1)))
        d = sample - pts[i_near]
        new = pts[i_near] + d * min(1.0, STEP / (np.linalg.norm(d) + 1e-12))  # steer
        if not collision_free(pts[i_near], new):
            continue
        p_best, c_best = i_near, cost[i_near] + np.linalg.norm(new - pts[i_near])
        if star:  # pick the lowest-cost parent among the neighbors within the radius
            near = np.flatnonzero(np.linalg.norm(pts - new, axis=1) < radius)
            for j in near:
                c = cost[j] + np.linalg.norm(new - pts[j])
                if c < c_best and collision_free(pts[j], new):
                    p_best, c_best = int(j), c
        nodes.append(new)
        parent.append(p_best)
        cost.append(c_best)
        k = len(nodes) - 1
        if star:  # rewire: reparent neighbors that get cheaper through the new node
            for j in near:
                c = c_best + np.linalg.norm(pts[j] - new)
                if c < cost[j] and collision_free(new, pts[j]):
                    parent[j], cost[j] = k, c  # (simplified: descendant costs are not propagated)
        if np.linalg.norm(new - goal) < GOAL_TOL and (best is None or cost[k] < cost[best]):
            best = k
            if not star:
                break  # RRT stops at the first path it finds
    path, k = [goal], best  # join the last node straight to the goal point
    while k != -1:
        path.append(nodes[k])
        k = parent[k]
    return np.array(path[::-1]), len(nodes)


for name, star in [("RRT", False), ("RRT*", True)]:
    path, n_nodes = rrt(star)
    length = np.linalg.norm(np.diff(path, axis=0), axis=1).sum()
    print(f"{name:5s} nodes {n_nodes:4d}  path points {len(path):3d}  length {length:5.2f}")
print("straight-line distance (lower bound ignoring obstacles)", round(float(np.linalg.norm(goal - start)), 2))
```

RRT finds a path quickly with only about 150 nodes, but at roughly 15.5 m it wanders. RRT* spends
more than 2500 nodes and in return passes almost straight between the obstacles at about 13.2 m.
The collision check is a simple version that samples only a few points along the segment, so it
can tunnel through very thin obstacles.

**Exercise:** (1) Run both ten times with different seeds and compare the mean and variance of
their path lengths. (2) Vary RRT*'s `N_ITER` over 500, 1000, and 3000 and plot the curve of
decreasing length. (3) Build a PRM (300 samples, $k = 10$) over the same obstacles and search it
with the A* of lesson 1.

## Self-check questions

1. Give two reasons to use sampling-based planning instead of grid A* for path planning of a six-joint arm.
2. Give an example of a situation that favors PRM and one that favors RRT.
3. What goes wrong if you make RRT's goal bias too large (50%, say)?

## How to study this stage

1. **Video (first):** watch the configuration space, PRM, and RRT portions of the Modern Robotics
   Ch. 10 videos.
2. **This lesson plus the example:** run the example and plot the tree (`nodes`, `parent`) to see
   the difference between RRT and RRT* with your own eyes.
3. **Textbook:** read the part of LaValle Ch. 5 explaining that collision checking and
   nearest-neighbor search are the real bottlenecks.
4. **Problems:** take the quiz in the Korean original (`rc quiz m6-sampling-based-planning`), then
   do exercises (1) through (3).
5. **Depth (optional):** implement a bidirectional tree with the RRT-Connect assignment of AutoRob.

## References

- Steven M. LaValle, *Planning Algorithms*, Cambridge University Press - <https://lavalle.pl/planning/>
- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 10 - <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics Ch. 10 Motion Planning videos - <https://www.youtube.com/playlist?list=PLggLP4f-rq01Q3clJrnWFPRtpUwSlr4mG>
- University of Michigan, AutoRob - <https://autorob.org/>
- Sertac Karaman, Emilio Frazzoli, "Sampling-based Algorithms for Optimal Motion Planning", IJRR 2011 (the original RRT* paper, no link)
