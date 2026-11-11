---
id: m1-coordinate-transforms
lang: en
title: Coordinate transforms (homogeneous transformation matrices)
summary: Package rotation and translation into a single 4x4 homogeneous transformation matrix, and move between frames by composing and inverting transforms.
objectives:
  - Build a homogeneous transformation matrix from a rotation matrix and a position vector.
  - Read frame notation (T_ab and friends) and compose or invert transforms in the right order.
  - Write code that transforms a point measured in a sensor frame into the robot and world frames.
tags: [math, transforms, homogeneous-coordinates, tf]
---

# Coordinate transforms

A robot has many frames: the world (map), the robot body, each joint, and sensors
such as cameras and lidars. When a camera says "there is an object 1 m ahead," the
arm cannot grasp it until that point is moved into the arm's reference frame. This
lesson is the shared foundation for M2 kinematics (DH parameters, forward
kinematics) and M3 mobile robot pose estimation.

## Concepts

### Pose = rotation + position

Describing the pose of frame $\{b\}$ in frame $\{a\}$ takes two things.

- $R_{ab}$: the rotation matrix whose columns are the axes of $\{b\}$ seen in $\{a\}$
- $\mathbf{p}_{ab}$: the origin of $\{b\}$ seen in $\{a\}$

Packing the two into a single $4\times4$ **homogeneous transformation matrix**
$T_{ab}$ lets you handle rotation and translation with one matrix product. The set
of such matrices is called $SE(3)$.

### Homogeneous coordinates

Appending a 1 to a 3D point $\mathbf{p}$ to write $[\mathbf{p}; 1]$ lets you treat
translation as a linear operation too. Direction vectors (velocities, axis
directions) must not be affected by translation, so their last component is 0.

### Notation and the composition rule

This curriculum follows the notation of Modern Robotics. $T_{ab}$ means "$\{b\}$ as
seen from $\{a\}$," and a point $\mathbf{p}_b$ expressed in $\{b\}$ moves to $\{a\}$
as $\mathbf{p}_a = T_{ab}\,\mathbf{p}_b$. Just multiply so that the inner
subscripts "cancel": $T_{ac} = T_{ab}T_{bc}$. Follow that rule and you will rarely
get the order wrong.

### Two interpretations

The same matrix $T$ can be read as (1) the **pose** of one frame seen from another,
or (2) an **operator** that moves a point or a frame. Also, multiplying a transform
**on the left moves things relative to the fixed (world) frame**, while multiplying
**on the right moves them relative to the current (body) frame**. ROS 2's `tf2` is
the library that manages such frame trees; you meet it again in M8.

## Key formulas

$$T_{ab} = \begin{bmatrix} R_{ab} & \mathbf{p}_{ab} \\ \mathbf{0}^T & 1 \end{bmatrix}, \qquad
\begin{bmatrix}\mathbf{p}_a\\1\end{bmatrix} = T_{ab}\begin{bmatrix}\mathbf{p}_b\\1\end{bmatrix}
\;\Leftrightarrow\; \mathbf{p}_a = R_{ab}\mathbf{p}_b + \mathbf{p}_{ab}$$

Composition and inversion:

$$T_{ac} = T_{ab}\,T_{bc}, \qquad
T_{ab}^{-1} = T_{ba} = \begin{bmatrix} R_{ab}^T & -R_{ab}^T\mathbf{p}_{ab} \\ \mathbf{0}^T & 1 \end{bmatrix}$$

The inverse needs no general matrix inversion — a transpose is enough. For a planar
(2D) robot you use the same structure in a $3\times3$ matrix
$\begin{bmatrix} R(\theta) & \mathbf{p} \\ \mathbf{0}^T & 1\end{bmatrix}$.

## Example

A mobile robot sits at world coordinates $(2, 1)$ facing $90^\circ$. A range sensor
is mounted $0.1$ m ahead of the robot center, and it measures an obstacle $0.5$ m
straight ahead. What are the obstacle's world coordinates?

- $T_{wr}$: $R(90^\circ)$, $\mathbf{p} = (2, 1)$
- $T_{rs}$: $R(0)$, $\mathbf{p} = (0.1, 0)$
- $\mathbf{p}_s = (0.5, 0)$

Since $T_{ws} = T_{wr}T_{rs}$, the sensor is at $(2, 1.1)$ in the world and the
obstacle is at $(2, 1.6)$.

```python
import numpy as np


def se2(theta, x, y):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, x], [s, c, y], [0, 0, 1.0]])


def inv_se2(T):
    R, p = T[:2, :2], T[:2, 2]
    Ti = np.eye(3)
    Ti[:2, :2], Ti[:2, 2] = R.T, -R.T @ p
    return Ti


T_wr = se2(np.pi / 2, 2.0, 1.0)
T_rs = se2(0.0, 0.1, 0.0)
p_s = np.array([0.5, 0.0, 1.0])

p_w = T_wr @ T_rs @ p_s
print(p_w[:2].round(3))  # [2.  1.6]
print(np.allclose(inv_se2(T_wr) @ T_wr, np.eye(3)))  # True
```

**Exercise (Appendix A, "coordinate transform visualization script"):** use
`matplotlib` to draw the axes of the world, robot, and sensor frames as arrows, and
plot how the obstacle's world coordinates move as you vary the robot's heading.
Then use `inv_se2` to convert a goal point given in world coordinates into the
robot frame (you will reuse this directly in M3 path following).

## Self-check questions

1. What is the relationship between $T_{ab}$ and $T_{ba}$, and why is the position part of $T_{ba}$ not simply $-\mathbf{p}_{ab}$?
2. How does multiplying the current pose $T_{sb}$ by a transform $T$ on the left differ in meaning from multiplying on the right?
3. Why is the last component set to 0 when a direction vector is written in homogeneous coordinates?

## How to study this stage

1. **Videos:** build intuition for homogeneous coordinates with Cyrill Stachniss's "Homogeneous Coordinates" lecture, then watch the homogeneous transformation matrix part of the Modern Robotics Ch. 3 lecture videos.
2. **Textbook:** read Modern Robotics §3.3 (homogeneous transformation matrices). Craig Ch. 2 covers the same material in a different notation if you want a second pass.
3. **This lesson plus the example:** work the obstacle example by hand first, then check it with the code.
4. **Problems:** take the quiz in the Korean original (`rc quiz m1-coordinate-transforms`), then do the exercise (the coordinate transform visualization script). Add two or three composition and inversion problems from the Modern Robotics Ch. 3 exercises.
5. **Checkpoint:** when you can answer self-check question 2 (left versus right multiplication) without hesitating, move on to M2.

## References

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, §3.3 "Rigid-Body Motions and Twists" —
  <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- John J. Craig, *Introduction to Robotics: Mechanics and Control*, 4th ed., Pearson —
  Ch. 2 "Spatial Descriptions and Transformations".
- Peter Corke, *Robotics, Vision and Control: Fundamental Algorithms in Python*, 3rd ed.,
  Springer, 2023 — Ch. 2.
- Cyrill Stachniss, "Homogeneous Coordinates" lecture (YouTube) —
  <https://www.youtube.com/watch?v=MQdm0Z_gNcw>
