---
id: m1-rotation-representations
lang: en
title: Rotation representations (Euler angles / quaternions)
summary: Express 3D rotations as rotation matrices, Euler angles, axis-angle, and quaternions, and learn the trade-offs and conversions between them.
objectives:
  - Explain the properties of a rotation matrix (orthogonal, determinant 1) and the meaning of its columns.
  - Build a rotation matrix from ZYX (roll-pitch-yaw) Euler angles and explain when gimbal lock occurs.
  - Convert between unit quaternions, rotation matrices, and Euler angles, and tell apart the component orders used by different libraries.
tags: [math, rotation, euler-angles, quaternion]
---

# Rotation representations

The pose of a robot arm's end effector, the tilt of a drone, and the heading of a
mobile robot are all "rotations." A rotation has three degrees of freedom, but
there are several ways to write it down as numbers, and each one differs in
convenience and in the traps it sets. This lesson compares four representations
and how to convert between them.

## Concepts

### Rotation matrix

A rotation matrix $R$ is a $3\times3$ orthogonal matrix satisfying $R^TR = I$ and
$\det R = 1$. The set of such matrices is called $SO(3)$. The three columns of $R$
are **the x, y, and z axes of the rotated frame, seen as unit vectors in the
original frame**. Composition is a single matrix product and is unambiguous, but
nine numbers carry only three degrees of freedom, so the representation is highly
redundant, and accumulated numerical error breaks orthogonality — which means you
have to renormalize periodically.

### Euler angles

Three successive axis rotations express an orientation. The common convention in
robotics and aerospace is the ZYX order: yaw ($\psi$), pitch ($\theta$), roll
($\phi$). Being easy for humans to read is a real advantage, but:

- The axis order (XYZ, ZYX, ZYZ, …) and the **extrinsic (fixed-axis) versus
  intrinsic (moving-axis)** interpretation mean that the same three numbers can
  denote different rotations. Always check the convention of the library you use.
- At a pitch of $\pm 90^\circ$ the first and third rotation axes line up and one
  degree of freedom disappears — **gimbal lock**. Near that point the angle values
  jump sharply and interpolation breaks down.

### Axis-angle

Every 3D rotation can be expressed as a rotation by an angle $\theta$ about some
unit axis $\hat{\boldsymbol{\omega}}$ (Euler's rotation theorem). The rotation
vector $\hat{\boldsymbol{\omega}}\theta$ carries a clear geometric meaning in
three numbers, and it is exactly what Modern Robotics calls exponential
coordinates.

### Unit quaternions

A unit quaternion encodes axis-angle in four numbers. It has no gimbal lock,
composition is a quaternion product, and smooth interpolation is handled by SLERP.
It is the default orientation representation in robot middleware, such as ROS 2's
`geometry_msgs/Quaternion`. Two cautions:

- $q$ and $-q$ are **the same rotation** (the double cover). Align the signs before
  comparing or interpolating.
- The component order differs between libraries. SciPy's `Rotation.as_quat()` and
  ROS messages use $(x, y, z, w)$ (scalar last), while textbooks and some libraries
  use $(w, x, y, z)$.

## Key formulas

Elementary rotation matrices (rotations about an axis):

$$R_z(\psi)=\begin{bmatrix}\cos\psi&-\sin\psi&0\\ \sin\psi&\cos\psi&0\\ 0&0&1\end{bmatrix},\quad
R_y(\theta)=\begin{bmatrix}\cos\theta&0&\sin\theta\\ 0&1&0\\ -\sin\theta&0&\cos\theta\end{bmatrix}$$

ZYX Euler angles (intrinsic Z → Y → X):

$$R = R_z(\psi)\,R_y(\theta)\,R_x(\phi)$$

From axis-angle to quaternion:

$$q = \left(\cos\tfrac{\theta}{2},\ \hat{\boldsymbol{\omega}}\sin\tfrac{\theta}{2}\right) = (w, x, y, z), \quad w^2+x^2+y^2+z^2 = 1$$

Getting the rotation angle from the trace of a rotation matrix:
$\operatorname{tr}(R) = 1 + 2\cos\theta$.

## Example

Check a 90° rotation about the z axis in three representations, and reproduce
gimbal lock.

```python
import numpy as np
from scipy.spatial.transform import Rotation as Rot

r = Rot.from_euler("ZYX", [90, 0, 0], degrees=True)  # uppercase = intrinsic
print(r.as_matrix().round(3))  # [[0,-1,0],[1,0,0],[0,0,1]]
print(r.as_quat())  # [0, 0, 0.7071, 0.7071]  (x, y, z, w)
print(r.as_rotvec())  # [0, 0, 1.5708]

# Gimbal lock: at 90° pitch, yaw and roll are indistinguishable
a = Rot.from_euler("ZYX", [30, 90, 0], degrees=True)
b = Rot.from_euler("ZYX", [0, 90, -30], degrees=True)
print(np.allclose(a.as_matrix(), b.as_matrix()))  # True: different angles, same rotation
```

Check by hand: $\theta = 90^\circ$ gives $\cos 45^\circ = \sin 45^\circ \approx 0.7071$,
and the axis is $z$, so $q = (0.7071, 0, 0, 0.7071)$ (writing $w$ first).

**Exercise:** generate 100 random Euler angle triples and round-trip them through
Euler → quaternion → matrix → Euler. Record when the result differs from the
original (near gimbal lock, and from angle-range wrapping).

## Self-check questions

1. What does the second column of a rotation matrix mean?
2. At which angles does gimbal lock occur in ZYX Euler angles, and why?
3. How can the fact that $q$ and $-q$ are the same rotation cause trouble when interpolating or comparing?

## How to study this stage

1. **Videos:** watch the rotation matrix, angular velocity, and exponential coordinates parts of the Modern Robotics Ch. 3 lecture videos (the wiki's Videos page indexes them by chapter).
2. **Textbook:** read Modern Robotics §3.2 (rotation matrices, exponential coordinates) and the Euler angle and quaternion parts of Appendix B. If you have Corke's book, reading the same material in Ch. 2 is a good way to pick up the coding side.
3. **This lesson plus the example:** run the example and check the SciPy `Rotation` docs for how uppercase (intrinsic) and lowercase (extrinsic) axis letters work in `from_euler`.
4. **Problems:** take the quiz in the Korean original (`rc quiz m1-rotation-representations`), then do the exercise (Euler ↔ quaternion ↔ matrix round trip).
5. **Optional reinforcement:** build visual intuition for 3D rotations with the Spatial Maths lectures at QUT Robot Academy.

## References

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 3 "Rigid-Body Motions" and
  Appendix B "Other Representations of Rotations" —
  <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Peter Corke, *Robotics, Vision and Control: Fundamental Algorithms in Python*, 3rd ed.,
  Springer, 2023 — Ch. 2 "Representing Position and Orientation".
- SciPy `Rotation` documentation —
  <https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html>
- QUT Robot Academy (Peter Corke), free "Spatial Maths" lectures — <https://robotacademy.net.au/>
