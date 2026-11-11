---
id: m5-occupancy-grid-scan-matching
lang: en
title: "Occupancy grid maps and scan matching"
summary: Implement occupancy grid mapping (log-odds updates), which builds a map from lidar scans when the pose is known, and then scan matching (correlative search and ICP), which corrects the pose against an existing map. Alternating the two gives the front end of SLAM.
objectives:
  - Treat each cell of an occupancy grid as a binary Bayes filter and explain the log-odds update and the inverse sensor model.
  - Build an occupancy grid map in numpy from lidar scans and known poses.
  - Explain how correlative scan matching and ICP reduce odometry error, and the conditions under which they fail.
tags: [occupancy-grid, mapping, log-odds, scan-matching, icp, lidar]
---

# Occupancy grid maps and scan matching

MCL assumed a map **already existed**. This lesson covers how to build that map (mapping with a
known pose) and how to correct the pose by fitting scans to the map (scan matching). Solving both
together is the SLAM of the next lesson, and the maps of Nav2 and SLAM Toolbox are exactly these
occupancy grids.

## Concepts

### The occupancy grid

Divide space into fixed cells (5 cm, say) and store the probability $p(m_i)$ that each cell is
occupied. Assuming the cells are independent of one another, each cell is a **binary Bayes
filter** with only two states, occupied or free.

- A cell a lidar beam passed through → more likely to be empty
- The cell where the beam ended → more likely to be occupied
- A cell no beam reached → unchanged (unknown)

This rule is the **inverse sensor model** $p(m_i \mid z, x)$. Multiplying probabilities directly
is numerically unstable near 0 and 1, so the values are stored as **log odds** and updated by
addition. Clamping the values to a fixed range lets a cell be revised when the environment
changes - a door opening, for instance.

### Scan matching

Near the pose estimate from odometry, find the pose at which the endpoints of a new scan best
overlap the occupied cells of the map.

- **Correlative scan matching:** sweep a small search window $(\Delta x, \Delta y, \Delta\theta)$
  on a grid, scoring each candidate. Simple and robust against local minima. This is what SLAM
  Toolbox (based on Karto) does.
- **ICP:** iteratively optimize point-to-point correspondences, as seen in M4. Fast, but it falls
  into a wrong solution when the initial guess is poor.

In environments whose features run in only one direction, such as a long corridor, motion along
the corridor is indistinguishable and the match fails.

## Key formulas

Log odds and the cell update ($l_0$ is the prior, usually 0):

$$l(m_i) = \log\frac{p(m_i)}{1 - p(m_i)},\qquad l_t(m_i) = l_{t-1}(m_i) + \log\frac{p(m_i \mid z_t, x_t)}{1 - p(m_i \mid z_t, x_t)} - l_0$$

Recovering the probability: $p(m_i) = 1 - 1/(1 + e^{l(m_i)})$

Scan matching (map $m$, scan endpoints $\mathbf{p}_k$, pose transform $T_x$):

$$x^{\star} = \arg\max_{x \in \text{window}} \sum_k \text{score}\big(m,\ T_x\,\mathbf{p}_k\big)$$

## Example

Build a map of a 6 m × 6 m square room from 360° scans at three poses, then correct a new pose
that carries odometry error using correlative search.

```python
import numpy as np

rng = np.random.default_rng(0)
res, size = 0.1, 60  # 10 cm cells, 6 m x 6 m
L_OCC, L_FREE = 0.85, -0.4  # log-odds increments of the inverse sensor model
logodds = np.zeros((size, size))


def raycast(pose, angles, max_r=5.0):
    """Virtual lidar ranges for a square room (walls at x, y = 0.5 and 5.5)."""
    x, y, th = pose
    r = []
    for a in angles:
        c, s = np.cos(th + a), np.sin(th + a)
        tx = [(w - x) / c for w in (0.5, 5.5) if abs(c) > 1e-9 and (w - x) / c > 0]
        ty = [(w - y) / s for w in (0.5, 5.5) if abs(s) > 1e-9 and (w - y) / s > 0]
        r.append(min(tx + ty + [max_r]))
    return np.array(r) + rng.normal(0, 0.02, len(angles))


def integrate_scan(pose, angles, ranges):
    x, y, th = pose
    for a, r in zip(angles, ranges, strict=True):
        d = np.arange(0, r, res / 2)  # sample along the beam every half cell
        free = np.c_[x + d * np.cos(th + a), y + d * np.sin(th + a)]
        cells = np.unique((free / res).astype(int), axis=0)
        logodds[cells[:, 1], cells[:, 0]] += L_FREE
        hit = (np.array([x + r * np.cos(th + a), y + r * np.sin(th + a)]) / res).astype(int)
        logodds[hit[1], hit[0]] += L_OCC - L_FREE  # flip the endpoint to occupied
    np.clip(logodds, -5, 5, out=logodds)


angles = np.linspace(-np.pi, np.pi, 180, endpoint=False)
for pose in [(2.0, 2.0, 0.0), (3.0, 2.5, 0.5), (4.0, 3.5, 1.0)]:
    integrate_scan(pose, angles, raycast(pose, angles))

prob = 1 - 1 / (1 + np.exp(logodds))
print("middle row:", "".join("#" if p > 0.7 else "." if p < 0.3 else "?" for p in prob[30]))


def match_score(pose, angles, ranges):
    x, y, th = pose
    pts = np.c_[x + ranges * np.cos(th + angles), y + ranges * np.sin(th + angles)]
    idx = np.clip((pts / res).astype(int), 0, size - 1)
    return logodds[idx[:, 1], idx[:, 0]].sum()  # higher as endpoints land on wall cells


true_pose = np.array([3.3, 2.8, 0.65])
scan = raycast(true_pose, angles)
guess = true_pose + [0.2, -0.15, 0.08]  # odometry estimate (with error)
steps = np.arange(-0.3, 0.31, 0.05)
candidates = [
    guess + [dx, dy, dth] for dx in steps for dy in steps for dth in np.arange(-0.15, 0.151, 0.01)
]
best = max(candidates, key=lambda p: match_score(p, angles, scan))
print("odometry error    ", np.round(guess - true_pose, 3))
print("scan matching error", np.round(best - true_pose, 3))
```

The middle row comes out shaped like `?????#....#?????`: free space (`.`) inside the walls (`#`),
unknown (`?`) outside. Scan matching reduces the (0.2, −0.15) m and 0.08 rad error to within the
search resolution (5 cm).

**Exercise:** (1) Plot `prob` as an image and vary `L_OCC` and `L_FREE` to see how wall thickness
and noisy cells change. (2) Replace the room with a long corridor (walls at x = 0.5 and 1.5) and
confirm that error along the corridor is not corrected by scan matching. (3) Do the same
correction with the ICP of M4 instead of a search window, and compare as you increase the initial
error.

## Self-check questions

1. Give two reasons an occupancy grid stores log odds rather than probabilities.
2. Explain with the inverse sensor model why the cell where a beam ends and the cells it passed through get different updates.
3. Why does scan matching fail in a long corridor, and what role does fused odometry and IMU play there?

## How to study this stage

1. **Video (first):** follow the log-odds derivation in Stachniss's "Occupancy Grid Maps."
2. **This lesson plus the example:** run the example, plot the map as an image, then do exercises
   (1) through (3).
3. **Review:** revisit scan registration with the M4 ICP lesson and Stachniss's "ICP" lecture.
4. **Problems:** take the quiz in the Korean original (`rc quiz m5-occupancy-grid-scan-matching`).
5. **Depth (optional):** add practice with *Probabilistic Robotics* Ch. 9 and the ROB 530 mapping
   assignment.

## References

- Cyrill Stachniss, "Occupancy Grid Maps" - <https://www.youtube.com/watch?v=v-Rm9TUG9LA>
- Cyrill Stachniss, "ICP" - <https://www.youtube.com/watch?v=djnd502836w>
- Sebastian Thrun, Wolfram Burgard, Dieter Fox, *Probabilistic Robotics*, MIT Press -
  <https://robots.stanford.edu/probabilistic-robotics/>
- University of Michigan, ROB 530 Mobile Robotics - <https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public>
