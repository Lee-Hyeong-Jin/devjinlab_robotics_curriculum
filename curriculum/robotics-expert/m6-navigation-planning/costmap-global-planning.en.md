---
id: m6-costmap-global-planning
lang: en
title: "Costmaps and global planning (reading the Nav2 planners)"
summary: Instead of using the occupancy grid directly, turn it into a costmap of stacked static, obstacle, and inflation layers, and find a safe global path well clear of obstacles with A*. Then read Nav2's costmap cost values and how the NavFn and Smac planners work on top of that structure.
objectives:
  - Explain the layers of a costmap (static, obstacle, inflation) and the meaning of its cost values (free, inscribed, lethal, unknown).
  - Compute the exponentially decaying cost of the inflation layer and obtain a path with clearance in numpy using a cost-aware A*.
  - State the criteria for choosing among Nav2's global planner plugins (NavFn, the Smac family, Theta*) for a given robot shape and requirement.
tags: [costmap, inflation, global-planner, nav2, a-star, navfn, smac]
---

# Costmaps and global planning (reading the Nav2 planners)

The A* of lesson 1 produced a path that grazed the corner of a wall. A search that sees only two
values, occupied or free, guarantees no more than "it does not collide"; it does not give a path
a real robot can take safely while carrying localization and control error. Nav2 solves this with
a **costmap**: it paints "how close is this to an obstacle" as a cost over the occupancy grid and
has the planner find a path that is both short and low-cost.

## Concepts

### The layers of a costmap

Nav2's Costmap 2D combines several **layers** in order.

- **Static layer:** copies in the map built by SLAM (M5).
- **Obstacle layer (obstacle / voxel):** marks obstacles absent from the map from current lidar and
  depth camera observations, and clears the cells the beams passed through (the same principle as
  the inverse sensor model of M5).
- **Inflation layer:** spreads cost outward around lethal cells.

The global costmap is a wide map in the `map` frame, used for global planning; the local costmap
is a small window in the `odom` frame that follows the robot, used for the local planning of the
next lesson.

### Cost values

Cell costs are integers from 0 to 255. 254 is **lethal**, the obstacle itself. 253 is
**inscribed**: with the robot's center here, its body touches the obstacle (the circular-robot
C-space inflation of lesson 1). 255 is **unknown** and 0 is free. From outside the inscribed
radius out to the inflation radius, the cost decays exponentially with distance. A larger
`cost_scaling_factor` makes the cost fall off faster and yields paths that hug walls more closely.

### Global planner plugins

Nav2's planner server takes interchangeable plugins.

- **NavFn:** Dijkstra/A* on the grid. Simple and robust for circular, differential-drive robots.
- **Smac Planner:** comes in 2D A*, Hybrid-A* (which accounts for heading and a minimum turning
  radius), and State Lattice variants. Use it for car-like and rectangular robots.
- **Theta\*:** connects straight lines across grid cells by line of sight, producing paths with
  fewer turns.

## Key formulas

Inflation cost ($d$ is the distance to the nearest lethal cell, $r_{in}$ the inscribed radius,
$\alpha$ the decay rate):

$$c(d) = \begin{cases} 254 & d = 0 \\ 253 & 0 < d \le r_{in} \\ 252\, e^{-\alpha (d - r_{in})} & r_{in} < d \le r_{inf} \\ 0 & d > r_{inf} \end{cases}$$

The cost-weighted edge ($w$ is the cost penalty weight):

$$c(n, n') = \lVert n' - n \rVert \left(1 + w\,\frac{c(n')}{252}\right)$$

## Example

Build an inflation layer over two walls and a box in a 3 m × 4 m space, then run A* with penalty
weights of 0 and 3.

```python
import heapq

import numpy as np

res = 0.05  # 5 cm cells
occ = np.zeros((60, 80), dtype=bool)  # 3 m x 4 m, True = occupied (static map layer)
occ[0:40, 25] = True
occ[20:60, 55] = True
occ[28:32, 38:44] = True  # box in the middle

# obstacle + inflation layers: distance from each cell to the nearest occupied cell
# (brute-force distance transform)
rows, cols = np.indices(occ.shape)
cells = np.c_[rows.ravel(), cols.ravel()]
obs = np.argwhere(occ)
dist = np.sqrt(((cells[:, None, :] - obs[None, :, :]) ** 2).sum(-1)).min(1).reshape(occ.shape) * res

INSCRIBED, INFLATION, SCALE = 0.15, 0.6, 5.0  # robot inscribed radius, inflation radius [m], decay
cost = np.zeros(occ.shape)
band = (dist > INSCRIBED) & (dist <= INFLATION)
cost[band] = 252 * np.exp(-SCALE * (dist[band] - INSCRIBED))  # same shape as Nav2's inflation layer
cost[dist <= INSCRIBED] = 253  # the center entering here always collides
cost[occ] = 254  # LETHAL
MOVES = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]


def astar(cost, start, goal, weight):
    def h(n):
        return np.hypot(n[0] - goal[0], n[1] - goal[1])

    g, parent, open_list, closed = {start: 0.0}, {start: None}, [(h(start), start)], set()
    while open_list:
        _, node = heapq.heappop(open_list)
        if node in closed:
            continue
        closed.add(node)
        if node == goal:
            break
        for dr, dc in MOVES:
            nb = (node[0] + dr, node[1] + dc)
            if not (0 <= nb[0] < cost.shape[0] and 0 <= nb[1] < cost.shape[1]) or cost[nb] >= 253:
                continue
            step = np.hypot(dr, dc) * (1 + weight * cost[nb] / 252)  # distance x (1 + cost penalty)
            if g[node] + step < g.get(nb, np.inf):
                g[nb], parent[nb] = g[node] + step, node
                heapq.heappush(open_list, (g[nb] + h(nb), nb))
    path, n = [], goal
    while n is not None:
        path.append(n)
        n = parent[n]
    return np.array(path[::-1])


start, goal = (50, 5), (10, 75)
for weight in [0.0, 3.0]:
    path = astar(cost, start, goal, weight)
    length = np.linalg.norm(np.diff(path, axis=0), axis=1).sum() * res
    clearance = dist[path[:, 0], path[:, 1]]
    print(
        f"penalty weight {weight}: length {length:.2f} m, min clearance {clearance.min():.2f} m, "
        f"mean clearance {clearance.mean():.2f} m"
    )
```

With no penalty the path is a short 4.56 m but runs right along the inscribed boundary (0.15 m).
A penalty of 3 lengthens it slightly to 5.30 m and in return raises the minimum clearance to
0.30 m and the mean to 0.63 m, taking the path down the middle of the corridor.

**Exercise:** (1) Set `SCALE` to 1, 5, and 20 and tabulate the resulting path length and
clearance. (2) What path comes out when `INFLATION` equals the inscribed radius? (3) Count the
size of the `closed` set as in lesson 1 and see how the cost weighting affects the amount of
search.

## Self-check questions

1. Why distinguish inscribed (253) from lethal (254)? What changes for a non-circular robot?
2. Explain from M5 and M8 why the global and local costmaps use different frames (`map` and `odom`).
3. Why should a car-like robot use Smac Hybrid-A* instead of NavFn?

## How to study this stage

1. **Documentation (first):** read the Costmap and planner parts of Nav2's Navigation Concepts and
   draw the layer structure.
2. **This lesson plus the example:** plot the `cost` array as an image to see the inflation band,
   then do the exercises.
3. **Reading the configuration:** map the Inflation Layer parameters of the Nav2 Configuration
   Guide (`inflation_radius`, `cost_scaling_factor`) one to one onto the example's variables.
4. **Problems:** take the quiz in the Korean original (`rc quiz m6-costmap-global-planning`).
5. **Depth (optional):** read the Hybrid A* code of PythonRobotics and summarize what changes when
   heading enters the state.

## References

- Nav2 Documentation - <https://docs.nav2.org/rolling/index.html>
- Cyrill Stachniss, "A* Planning" - <https://www.youtube.com/watch?v=HR1TNa8Lp7w>
- Atsushi Sakai, PythonRobotics - <https://atsushisakai.github.io/PythonRobotics/>
- Steven M. LaValle, *Planning Algorithms*, Cambridge University Press - <https://lavalle.pl/planning/>
