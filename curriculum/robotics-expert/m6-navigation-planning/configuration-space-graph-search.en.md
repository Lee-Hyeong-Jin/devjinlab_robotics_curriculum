---
id: m6-configuration-space-graph-search
lang: en
title: "Configuration space and graph search (Dijkstra, A*)"
summary: Define the path planning problem in configuration space (C-space), where the robot's whole pose is a single point, then treat the occupancy grid as a graph and find shortest paths with Dijkstra and A*. A numpy example shows the conditions under which a heuristic cuts the search while preserving optimality.
objectives:
  - Explain how obstacles in the workspace become the forbidden region (C_obs) of configuration space, and state that obstacle inflation is that approximation for a circular robot.
  - Build an 8-connected graph from an occupancy grid and implement Dijkstra and A* with a priority queue.
  - Explain what admissible and consistent heuristics mean and how the heuristic affects the number of expanded nodes and optimality.
tags: [configuration-space, graph-search, dijkstra, a-star, heuristic, grid]
---

# Configuration space and graph search (Dijkstra, A*)

In M5 the robot acquired a map (an occupancy grid) and its own position within it. Now it is time
to decide where to go and how. This lesson defines the path planning problem in **configuration
space** and implements its most basic solution, graph search on a grid. Nav2's global planners
(NavFn, Smac) are ultimately variants of these algorithms.

## Concepts

### Configuration space (C-space)

A robot's **configuration** $q$ is the minimal set of variables that fixes the position of every
point of the robot. A planar mobile robot has $q = (x, y, \theta)$; a two-joint arm has
$q = (\theta_1, \theta_2)$ (the forward kinematics of M2 compute body positions from $q$). The
set of all $q$ at which the robot overlaps an obstacle is $C_{obs}$, and the rest is free space
$C_{free}$. Path planning becomes the problem of finding a continuous curve inside $C_{free}$
joining $q_{start}$ to $q_{goal}$.

For a circular robot of radius $r$, the heading $\theta$ does not affect collisions, so you can
inflate the obstacles by $r$ and treat the robot as a point. That is exactly the idea behind the
costmap inflation of the next lesson. For a rectangular robot the shape of $C_{obs}$ changes with
$\theta$, which makes the computation hard - and that is why sampling-based planning is needed.

### The grid as a graph

Treat each free cell of the occupancy grid as a node and each move to a neighboring cell as an
edge (cost 1 horizontally and vertically, $\sqrt{2}$ diagonally), and path planning becomes a
graph shortest-path problem.

- **Dijkstra:** expand the node with the smallest accumulated cost $g(n)$ from the start. It
  spreads evenly in every direction and guarantees the shortest path.
- **A\*:** expand the node with the smallest $f(n) = g(n) + h(n)$, where $h(n)$ estimates the cost
  remaining to the goal. Looking at nodes toward the goal first cuts the number of expansions
  sharply.

If the heuristic never exceeds the true remaining cost (it is **admissible**), A* finds the
optimal path. On an 8-connected grid the octile distance is an admissible heuristic. Multiplying
$h$ by a weight greater than 1 (Weighted A*) is faster but loses optimality.

## Key formulas

The evaluation function of A* and edge relaxation:

$$f(n) = g(n) + h(n),\qquad g(n') \leftarrow \min\big(g(n'),\ g(n) + c(n, n')\big)$$

Admissibility and consistency ($h^*$ is the true minimum remaining cost):

$$h(n) \le h^*(n),\qquad h(n) \le c(n, n') + h(n')$$

The octile distance on an 8-connected grid ($\Delta r$ and $\Delta c$ are the row and column
differences):

$$h = \max(\Delta r, \Delta c) + (\sqrt{2} - 1)\min(\Delta r, \Delta c)$$

## Example

Compare Dijkstra and A* on a 20 × 30 grid with two staggered walls. The same code becomes
Dijkstra when the heuristic is set to 0.

```python
import heapq

import numpy as np

grid = np.zeros((20, 30), dtype=bool)  # True = obstacle
grid[0:16, 10] = True  # vertical wall, gap at the bottom
grid[4:20, 20] = True  # vertical wall, gap at the top
start, goal = (10, 2), (10, 27)  # (row, column)
MOVES = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]


def plan(grid, start, goal, use_heuristic=True):
    def h(n):
        if not use_heuristic:
            return 0.0  # h = 0 gives Dijkstra
        dr, dc = abs(n[0] - goal[0]), abs(n[1] - goal[1])
        return max(dr, dc) + (np.sqrt(2) - 1) * min(dr, dc)  # 8-connected octile distance

    g, parent = {start: 0.0}, {start: None}
    open_list, closed = [(h(start), start)], set()
    while open_list:
        _, node = heapq.heappop(open_list)
        if node in closed:
            continue  # a duplicate entry pushed earlier with a higher cost
        closed.add(node)
        if node == goal:
            break
        for dr, dc in MOVES:
            nb = (node[0] + dr, node[1] + dc)
            if not (0 <= nb[0] < grid.shape[0] and 0 <= nb[1] < grid.shape[1]) or grid[nb]:
                continue
            new_g = g[node] + np.hypot(dr, dc)
            if new_g < g.get(nb, np.inf):
                g[nb], parent[nb] = new_g, node
                heapq.heappush(open_list, (new_g + h(nb), nb))
    path, n = [], goal
    while n is not None:
        path.append(n)
        n = parent[n]
    return path[::-1], g[goal], len(closed)


for name, use_h in [("Dijkstra", False), ("A*", True)]:
    path, cost, expanded = plan(grid, start, goal, use_h)
    print(f"{name:8s} cost {cost:6.2f}  path cells {len(path):3d}  expanded {expanded:4d}")

canvas = np.where(grid, "#", ".").astype("<U1")
for r, c in path:
    canvas[r, c] = "*"
print("\n".join("".join(row) for row in canvas))
```

Both algorithms find the same shortest path at cost 37.53, but Dijkstra expands 484 nodes against
A*'s 325. Note how the `*` in the picture grazes the end of a wall diagonally - a real robot would
scrape the corner.

**Exercise:** (1) Multiply the heuristic by weights of 1.5 and 3 and compare the expanded node
count against the path cost. (2) Modify the code to forbid a diagonal move when either of the two
cells beside it is an obstacle, removing the corner grazing. (3) Switch to 4-connected moves and
use the Manhattan distance as the heuristic. Is the octile distance still admissible there?

## Self-check questions

1. A circular robot can be planned for as a point by inflating the obstacles. Why is it not that simple for a rectangular robot?
2. What can happen to A*'s result if the heuristic violates admissibility? And what if $h = 0$?
3. If you halve the grid resolution (four times as many cells), how do the search cost and the path quality each change?

## How to study this stage

1. **Video (first):** get the flow from Dijkstra to A* from Stachniss's "A* Planning."
2. **This lesson plus the example:** run the example yourself and mark the expanded cells
   (`closed`) on the picture to compare how the two algorithms spread.
3. **Code reading:** put the A* code of PythonRobotics beside your own implementation and find the
   differences.
4. **Problems:** take the quiz in the Korean original
   (`rc quiz m6-configuration-space-graph-search`), then do exercises (1) through (3).
5. **Depth (optional):** read the general search framework of LaValle's *Planning Algorithms*
   Ch. 2 and the configuration space definitions of Ch. 4.

## References

- Steven M. LaValle, *Planning Algorithms*, Cambridge University Press - <https://lavalle.pl/planning/>
- Cyrill Stachniss, "A* Planning" - <https://www.youtube.com/watch?v=HR1TNa8Lp7w>
- Atsushi Sakai, PythonRobotics - <https://atsushisakai.github.io/PythonRobotics/>
- MIT OCW 16.410 Principles of Autonomy and Decision Making -
  <https://ocw.mit.edu/courses/16-410-principles-of-autonomy-and-decision-making-fall-2010>
