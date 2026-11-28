---
id: m4-point-clouds-icp-ransac
lang: en
title: "Point cloud processing and 3D geometry: RANSAC and ICP"
summary: Implement in numpy the two core algorithms for point clouds from lidar and depth cameras - outlier-robust model estimation (RANSAC) and registration of two clouds (ICP).
objectives:
  - Explain how a depth image is back-projected through the camera model into a point cloud.
  - Find a plane in an outlier-laden cloud with RANSAC and compute the number of iterations it needs.
  - Implement point-to-point ICP, alternating SVD-based rigid registration with nearest-neighbor correspondences.
tags: [point-cloud, ransac, icp, registration, lidar, 3d-geometry]
---

# Point cloud processing and 3D geometry: RANSAC and ICP

Lidars and depth cameras hand you a **point cloud** — a list of tens of thousands
of 3D points — rather than an image. Most of what a robot does with a cloud
reduces to two questions: "which of these points belong to a model such as the
floor or a wall?" (RANSAC) and "how far has the robot moved between this cloud and
the previous one?" (ICP). Both algorithms are used directly in the scan-matching
SLAM of the intermediate module M5 and in grasp pose estimation at the advanced
stage.

## Where you will use this

A robot vacuum telling floor from obstacle, a logistics robot finding the top of a pallet, and a
self-driving car removing the road surface are RANSAC plane detection. LiDAR odometry and
scan-matching SLAM (M5), and bin picking that fits a 3D scan to a CAD model to locate a part (M6),
use ICP. PCL and Open3D offer both algorithms as one function each, but without knowing when they
fail (outlier ratio, initial guess) you cannot trust what they return.

## Concepts

### Building a point cloud

A depth camera gives a depth $Z$ for each pixel $(u, v)$; inverting the projection
of the previous lesson turns that into a 3D point. A 2D lidar gives an angle
$\phi_i$ and a range $r_i$, which become $(r_i\cos\phi_i, r_i\sin\phi_i)$. Points
built this way live in the sensor frame, so use the homogeneous transforms of M1
to move them into the robot and world frames. When there are too many points,
**voxel downsampling** (one point per grid cell) thins them out, and a KD-tree
makes neighbor search fast.

### RANSAC

Least squares is dragged badly off course by even a single outlier. RANSAC takes
the opposite approach.

1. Randomly draw the minimum number of points that determine the model (three for a plane).
2. Build a model from them and count the **inliers** within a distance threshold.
3. Repeat many times, keep the model with the most inliers, and re-estimate by least squares on those inliers.

In robotics it is routinely used as preprocessing: find the ground plane, remove
it, and look for obstacles and objects in what remains.

### ICP

Given two clouds $P$ (source) and $Q$ (target) that view the same scene from
different positions, find the rotation $R$ and translation $t$ that align $P$ onto
$Q$. If the correspondences are known, SVD solves it in one shot (Kabsch). Since
they are not known, ICP iterates: **assume the nearest neighbor is the
correspondence → register → find correspondences again**. If the initial guess is
far from the truth it falls into a wrong local minimum, so the initial estimate
usually comes from odometry.

## Key formulas

Distance between a point $p$ and a plane (unit normal $n$, point $a$ on the
plane): $d = |(p - a)\cdot n|$.

RANSAC iteration count (inlier ratio $w$, minimum sample size $s$, success
probability $p$):

$$N = \frac{\log(1 - p)}{\log(1 - w^s)}$$

For example $w = 0.6$, $s = 3$, $p = 0.99$ gives $N \approx 19$.

Rigid registration (given correspondences $p_i \leftrightarrow q_i$):

$$\min_{R,t}\sum_i \lVert R\,p_i + t - q_i\rVert^2,\quad
H = \sum_i (p_i - \bar p)(q_i - \bar q)^\top = U\Sigma V^\top$$

$$R = V\,\mathrm{diag}(1, 1, \det(VU^\top))\,U^\top,\qquad t = \bar q - R\,\bar p$$

## Example

```python
import numpy as np

rng = np.random.default_rng(3)

# 1) RANSAC plane detection: 300 floor points (z=0) plus 150 box and noise outliers
floor = np.c_[rng.uniform(-2, 2, (300, 2)), rng.normal(0, 0.01, 300)]
clutter = rng.uniform([-2, -2, 0.05], [2, 2, 1.0], (150, 3))
cloud = np.vstack([floor, clutter])


def ransac_plane(P, iters=200, thresh=0.03):
    best = np.zeros(len(P), dtype=bool)
    for _ in range(iters):
        a, b, c = P[rng.choice(len(P), 3, replace=False)]
        n = np.cross(b - a, c - a)
        if np.linalg.norm(n) < 1e-9:
            continue  # the three points are collinear
        n /= np.linalg.norm(n)
        inliers = np.abs((P - a) @ n) < thresh
        if inliers.sum() > best.sum():
            best = inliers
    return best


inl = ransac_plane(cloud)
print(f"plane inliers: {inl.sum()} (300 floor points)")


# 2) ICP: rotate and translate a cloud, then register it back
def best_fit(A, B):  # R, t that fit A to B (SVD, Kabsch)
    ca, cb = A.mean(0), B.mean(0)
    U, _, Vt = np.linalg.svd((A - ca).T @ (B - cb))
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])  # guard against reflection
    R = Vt.T @ D @ U.T
    return R, cb - R @ ca


def icp(src, dst, iters=30):
    R_tot, t_tot, cur = np.eye(3), np.zeros(3), src.copy()
    for _ in range(iters):
        d2 = ((cur[:, None, :] - dst[None, :, :]) ** 2).sum(-1)
        nn = dst[d2.argmin(1)]  # nearest-neighbor correspondences
        R, t = best_fit(cur, nn)
        cur = cur @ R.T + t
        R_tot, t_tot = R @ R_tot, R @ t_tot + t
    return R_tot, t_tot, np.sqrt(d2.min(1).mean())


yaw = np.deg2rad(10)
R_true = np.array([[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]])
dst = clutter
src = (dst - [0.1, -0.05, 0.0]) @ R_true  # dst = R_true @ src + t_true
R_est, t_est, err = icp(src, dst)
print(
    f"estimated yaw {np.rad2deg(np.arctan2(R_est[1, 0], R_est[0, 0])):.2f} deg, t {t_est.round(3)}"
)
print(f"RMS distance after registration {err:.4f}")
```

RANSAC finds nearly all the floor points (298/300) even with a third of the cloud
being outliers. ICP recovers the $10^\circ$ rotation and the $(0.1, -0.05, 0)$
translation exactly. Comparing every nearest neighbor is $O(nm)$ and only workable
up to a few hundred points; in practice you use a KD-tree (Open3D).

**Exercise:** (1) vary the outlier ratio, find the iteration count at which RANSAC
starts to fail, and compare with the formula. (2) Re-estimate the plane by least
squares on the RANSAC inliers (the smallest singular vector of the SVD is the
normal). (3) Increase the initial ICP rotation to 10°, 30°, and 60° and record
whether it converges.

```expected
1. All three sampled points are inliers with probability $w^3$, so reaching a success probability
   $p$ needs $N = \log(1-p)/\log(1-w^3)$ iterations. With 450 points, changing the outlier ratio and
   running 100 times each (success = at least 90% of the floor points found):

   | Outlier ratio | $N$ from the formula ($p$ = 0.99) | 20 iterations | 50 | 100 | 200 |
   | --- | --- | --- | --- | --- | --- |
   | 33% (the example) | 13 | 93% | 100% | 100% | 100% |
   | 60% | 70 | 39% | 71% | 91% | 100% |
   | 80% | 573 | 6% | 10% | 26% | 40% |

   At 80% outliers the example's 200 iterations succeed less than half the time, in line with the
   formula: the iterations needed grow as $w^{-3}$.
2. Subtract the centroid of the inliers and take the SVD: the right singular vector of the smallest
   singular value is the normal. On the example's data it is about (0.0007, −0.0002, 1.0000), 0.04°
   from the z axis, and the plane's height is about −0.0003 m. This plane, using every inlier, is
   more accurate than the RANSAC plane built from three points.
3. From initial rotations of 10° and 30° ICP recovers the yaw as 10.00° and 30.00° and the
   translation as (0.1, −0.05, 0) exactly, with an RMS distance of 0. From 60° it stops somewhere
   wrong, near a yaw of −10° with an RMS distance of about 0.32 m: most nearest-neighbour matches are
   wrong from the start, and it falls into a local minimum that fits wrong matches to each other.
```

## Self-check questions

1. Why use RANSAC instead of least squares on data containing outliers?
2. Explain why ICP needs a good initial guess, in terms of nearest-neighbor correspondences.
3. What happens in Kabsch registration if you do not correct the case $\det(VU^\top) = -1$?

## How to study this stage

1. **Videos (first):** watch Stachniss's *RANSAC*, then *ICP*. If the ICP derivation is hard, watch *Least Squares - An Informal Introduction* first.
2. **This lesson plus the example:** compare `best_fit` against a hand calculation on three point pairs with known correspondences.
3. **Problems:** compute the iteration-count formula yourself in the quiz, then do exercises (1) through (3).
4. **Optional real data:** use the point cloud and ICP registration tutorials in Open3D's Getting Started to try KD-trees, downsampling, and point-to-plane ICP.

## References

- Cyrill Stachniss, "ICP" — <https://www.youtube.com/watch?v=djnd502836w>
- Cyrill Stachniss, "RANSAC" — <https://www.youtube.com/watch?v=Cu1f6vpEilg>
- Cyrill Stachniss, "Least Squares - An Informal Introduction" — <https://www.youtube.com/watch?v=r2cyMQ5NB1o>
- Open3D Getting Started (v0.19) — <https://www.open3d.org/docs/release/getting_started.html>
