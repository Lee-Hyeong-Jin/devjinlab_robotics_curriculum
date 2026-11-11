---
id: m2-dh-parameters
lang: en
title: DH parameters
summary: Describe the relationship between links and joints with four Denavit-Hartenberg parameters and turn them into homogeneous transformation matrices.
objectives:
  - Explain the meaning of link length, link twist, link offset, and joint angle.
  - Tell apart the classic (standard) and modified (Craig) DH conventions.
  - Write the DH table of a 2-link planar manipulator and build the per-link transformation matrices.
tags: [kinematics, manipulator, dh]
---

# DH parameters

A robot arm is a chain of links (rigid bodies) joined by joints. To get the pose
of the end effector you multiply the transforms between adjacent link frames in
order (M1 coordinate transforms), but a general transform needs six numbers. The
**Denavit-Hartenberg (DH) convention** fixes rules for placing the frames and
thereby cuts that down to **four**. Proposed in 1955, it remains the most widely
used way to describe manipulators in textbooks, manufacturer datasheets, and
simulators.

## Concepts

### Frame placement rules (standard DH)

Attach a frame $\{i\}$ to each joint $i$ as follows.

1. Put the $z_{i-1}$ axis along the rotation axis of joint $i$ (revolute) or its direction of travel (prismatic).
2. Put the $x_i$ axis along the **common normal** of $z_{i-1}$ and $z_i$, pointing from $z_{i-1}$ toward $z_i$.
3. Choose $y_i$ to make the frame right-handed.

### The four parameters

| Symbol | Name | Meaning |
|---|---|---|
| $\theta_i$ | joint angle | angle from $x_{i-1}$ to $x_i$ about the $z_{i-1}$ axis |
| $d_i$ | link offset | distance measured along the $z_{i-1}$ axis |
| $a_i$ | link length | distance between the two $z$ axes measured along the $x_i$ axis (the common normal) |
| $\alpha_i$ | link twist | angle from $z_{i-1}$ to $z_i$ about the $x_i$ axis |

For a revolute joint $\theta_i$ is the variable and the other three are constants;
for a prismatic joint $d_i$ is the variable.

### Standard DH versus modified DH

Craig's textbook uses **modified DH**, which attaches frame $\{i\}$ to the axis of
joint $i$; its parameters are named $a_{i-1}, \alpha_{i-1}, d_i, \theta_i$ and are
multiplied in a different order. Mixing the two conventions produces wrong
results, so whenever you read a datasheet or someone's code, check which
convention it uses first. Modern Robotics mainly uses the product of exponentials
(PoE) formulation instead and covers DH in Appendix C.

## Key formulas

In standard DH the link transform is a rotation and translation about $z$,
followed by a translation and rotation about $x$.

$$T_{i-1,i} = \mathrm{Rot}_z(\theta_i)\,\mathrm{Trans}_z(d_i)\,\mathrm{Trans}_x(a_i)\,\mathrm{Rot}_x(\alpha_i)$$

$$T_{i-1,i} = \begin{bmatrix}
\cos\theta_i & -\sin\theta_i\cos\alpha_i & \sin\theta_i\sin\alpha_i & a_i\cos\theta_i \\
\sin\theta_i & \cos\theta_i\cos\alpha_i & -\cos\theta_i\sin\alpha_i & a_i\sin\theta_i \\
0 & \sin\alpha_i & \cos\alpha_i & d_i \\
0 & 0 & 0 & 1
\end{bmatrix}$$

## Example

The DH table of a planar 2-link arm with link lengths $L_1, L_2$ (two revolute
joints whose axes are both perpendicular to the ground):

| $i$ | $\theta_i$ | $d_i$ | $a_i$ | $\alpha_i$ |
|---|---|---|---|---|
| 1 | $\theta_1$ (variable) | 0 | $L_1$ | 0 |
| 2 | $\theta_2$ (variable) | 0 | $L_2$ | 0 |

All $z$ axes are parallel, so $\alpha_i = 0$, and everything lies in one plane, so
$d_i = 0$. Substituting $\alpha = 0$ and $d = 0$ into the matrix above makes each
link transform "rotate by $\theta_i$ in the plane, then translate by $L_i$ along
$x$."

```python
import numpy as np


def dh(theta, d, a, alpha):
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)
    return np.array(
        [
            [ct, -st * ca, st * sa, a * ct],
            [st, ct * ca, -ct * sa, a * st],
            [0.0, sa, ca, d],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )


L1, L2 = 0.5, 0.3
T01 = dh(np.deg2rad(30), 0, L1, 0)
T12 = dh(np.deg2rad(45), 0, L2, 0)
print((T01 @ T12)[:3, 3].round(4))  # end-effector position -> next lesson (forward kinematics)
```

**Exercise:** write the DH tables for a 3-link planar arm (the same arm plus a
third revolute joint of length $L_3$) and for a 2-link arm mounted on a rotating
base (where the first joint has $\alpha_1 = 90^\circ$). Then use the `dh()`
function to compute the end-effector position at a few joint angles and compare
with your hand calculation.

## Self-check questions

1. Which DH parameter is the variable for a revolute joint, and which for a prismatic joint?
2. What values do $a_i$ and $\alpha_i$ take when two joint axes are parallel, and when they intersect at right angles?
3. Why does feeding a DH table from Craig's textbook straight into the standard DH formula give a wrong result?

## How to study this stage

1. **Textbook (primary):** pick either Spong et al. *Robot Modeling and Control* Ch. 3 or Craig Ch. 3 and read its frame placement procedure. The two books use different conventions, so follow **only one** of them (this lesson uses standard DH, the Spong version).
2. **Videos:** watch the kinematics lecture on DH frame placement from Stanford CS223A (Khatib).
3. **This lesson plus the example:** fill in the 2-link DH table yourself, then run the `dh()` code.
4. **Problems:** take the quiz in the Korean original (`rc quiz m2-dh-parameters`), then do the exercise (DH tables for the 3-link planar arm and the rotating-base 2-link arm).
5. **Optional comparison:** read Modern Robotics Appendix C and write a paragraph on how DH and PoE differ. The next lesson (forward kinematics) reuses this table directly.

## References

- John J. Craig, *Introduction to Robotics: Mechanics and Control*, 4th ed., Pearson —
  Ch. 3 "Manipulator Kinematics" (modified DH).
- Mark W. Spong, Seth Hutchinson, M. Vidyasagar, *Robot Modeling and Control*, 2nd ed.,
  Wiley, 2020 — Ch. 3 (standard DH).
- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Appendix C "Denavit-Hartenberg Parameters" —
  <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Oussama Khatib, Stanford CS223A *Introduction to Robotics* (lecture videos) —
  <https://see.stanford.edu/Course/CS223A>
