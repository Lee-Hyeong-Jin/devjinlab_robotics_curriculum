---
id: m7-jacobian-singularity
lang: en
title: The Jacobian, velocity kinematics, and singularities
summary: Derive the Jacobian that converts joint velocities into end-effector velocities and end-effector forces into joint torques, then examine singularities, the manipulability ellipsoid, and the damped least-squares inverse near a singularity in numpy.
objectives:
  - Derive the Jacobian of a 2-link planar arm as the partial derivatives of the forward kinematics and explain the meaning of $\dot{x} = J\dot{\theta}$ and $\tau = J^\top F$.
  - Identify singularities from the determinant, the singular values, and the manipulability measure, and explain why joint velocities blow up near a singularity.
  - Implement the damped least-squares (DLS) inverse to stabilize velocity commands near a singularity.
tags: [manipulator, jacobian, velocity-kinematics, singularity, statics]
---

# The Jacobian, velocity kinematics, and singularities

M2 dealt only with "where it goes" - position. To actually move a manipulator you need to know
"how fast, and with how much force." The matrix joining those two is the **Jacobian**. It made a
brief appearance in the numerical IK of M2, but since this module's dynamics, impedance control,
and task-space trajectories all stand on this matrix, it gets a proper treatment here.

## Concepts

### Velocity kinematics

Differentiating the forward kinematics $x = f(\theta)$ in time gives
$\dot{x} = J(\theta)\dot{\theta}$. The $i$-th column of $J$ is "the velocity of the end-effector
when only joint $i$ turns at unit speed." For a 6-DOF arm it is a 6×n matrix stacking three
linear and three angular velocities, and Modern Robotics expresses it with twists, splitting it
into the **space Jacobian** and the **body Jacobian**. The principle is the same as for the
2-link planar arm.

### Statics

When the end-effector exerts a force $F$ on the environment, the joint torques required follow
from the principle of virtual work, $F^\top \dot{x} = \tau^\top \dot{\theta}$, as
$\tau = J^\top F$. The same matrix carries velocity from joints to end-effector and force from
end-effector to joints. This relationship is used directly in the impedance control of lesson 4.

### Singularities

A **singularity** is a configuration where $J$ loses rank. There, some direction of end-effector
velocity cannot be produced by any joint velocity. For the 2-link arm
$\det J = l_1 l_2 \sin\theta_2$, so it is singular when the arm is fully extended
($\theta_2 = 0$) or fully folded ($\theta_2 = \pi$). Using $\dot{\theta} = J^{-1}\dot{x}$ near a
singularity makes joint velocities explode even for a small end-effector velocity command.

### Manipulability and damped least squares

The eigenvectors and eigenvalues of $JJ^\top$ give the ellipsoid of end-effector velocities
achievable with unit joint velocity (the **manipulability ellipsoid**). The product of the
singular values $\sigma_i$, $w = \sqrt{\det(JJ^\top)}$, is Yoshikawa's manipulability measure,
and the closer $\sigma_{min}/\sigma_{max}$ is to 0, the nearer the singularity. Real controllers
use the **damped least-squares (DLS)** inverse instead of the matrix inverse, giving up a little
accuracy to keep joint velocities finite.

## Key formulas

The 2-link planar arm ($c_{12} = \cos(\theta_1 + \theta_2)$, and so on):

$$J(\theta) = \begin{bmatrix} -l_1 s_1 - l_2 s_{12} & -l_2 s_{12} \\ l_1 c_1 + l_2 c_{12} & l_2 c_{12} \end{bmatrix},\qquad \det J = l_1 l_2 \sin\theta_2$$

Statics and the DLS inverse ($\lambda$ is the damping factor):

$$\tau = J^\top F,\qquad \dot{\theta} = J^\top (JJ^\top + \lambda^2 I)^{-1}\dot{x}$$

## Example

Extend the arm progressively while demanding the same end-effector velocity
$\dot{x} = (0.1, 0)$ m/s (along the arm).

```python
import numpy as np

L1, L2 = 1.0, 0.8


def fk(th):
    t1, t12 = th[0], th[0] + th[1]
    return np.array([L1 * np.cos(t1) + L2 * np.cos(t12), L1 * np.sin(t1) + L2 * np.sin(t12)])


def jacobian(th):
    s1, c1 = np.sin(th[0]), np.cos(th[0])
    s12, c12 = np.sin(th[0] + th[1]), np.cos(th[0] + th[1])
    return np.array([[-L1 * s1 - L2 * s12, -L2 * s12], [L1 * c1 + L2 * c12, L2 * c12]])


# 1) check the analytic Jacobian against a numerical derivative
th = np.array([0.4, 0.9])
eps = 1e-6
J_num = np.column_stack([(fk(th + eps * e) - fk(th - eps * e)) / (2 * eps) for e in np.eye(2)])
print("max analytic/numerical Jacobian difference:", np.abs(jacobian(th) - J_num).max().round(9))

# 2) approaching a singularity: condition number and the joint velocities required
xdot = np.array([0.1, 0.0])
lam = 0.05
for th2 in [1.0, 0.3, 0.1, 0.01]:
    J = jacobian(np.array([0.0, th2]))
    sv = np.linalg.svd(J, compute_uv=False)
    qd_inv = np.linalg.solve(J, xdot)
    qd_dls = J.T @ np.linalg.solve(J @ J.T + lam**2 * np.eye(2), xdot)
    err = np.linalg.norm(J @ qd_dls - xdot)
    print(
        f"th2={th2:5.2f}  det={np.linalg.det(J):7.4f}  manipulability={sv.prod():6.4f}  "
        f"|qd_inv|={np.linalg.norm(qd_inv):8.2f}  |qd_dls|={np.linalg.norm(qd_dls):5.2f}  "
        f"DLS error={err:.3f}"
    )

# 3) statics: what joint torques press the end-effector into the floor with 10 N?
th = np.array([0.5, -1.0])
F = np.array([0.0, -10.0])
print("tau = J^T F =", (jacobian(th).T @ F).round(3), "N*m")
```

As $\theta_2$ falls from 1.0 to 0.01 the determinant drops from about 0.67 to 0.008, and the joint
velocity of the inverse solution explodes more than a hundredfold, from 0.22 rad/s to about
24.6 rad/s. The DLS solution keeps joint velocity below 1 rad/s by accepting error instead, and
at $\theta_2 = 0.01$ it essentially abandons velocity along the arm (error ≈ 0.1 m/s) - precisely
the direction an extended arm cannot produce. Real-time controllers such as MoveIt Servo likewise
watch the condition number and slow down or stop near a singularity.

**Exercise:** (1) Set $\lambda$ to 0.01, 0.05, and 0.2 and tabulate the balance between joint
velocity magnitude and end-effector velocity error. (2) Plot the manipulability $w$ over
$\theta_2 \in (0, \pi)$, derive analytically the $\theta_2$ that maximizes it, and confirm
($w = l_1 l_2 |\sin\theta_2|$). (3) Find the null space of $J^\top$ at the singular configuration
$\theta_2 = 0$ and explain why an end-effector force in that direction is resisted with no joint
torque.

## Self-check questions

1. Explain with the principle of virtual work why the Jacobian carries velocity from joints to end-effector and force from end-effector to joints.
2. At each of the two singular configurations of the 2-link arm, which end-effector velocity direction is unachievable?
3. What do you gain and lose by increasing $\lambda$ in DLS?

## How to study this stage

1. **Video (first):** watch the Jacobian, singularity, and manipulability ellipsoid portions of
   the Modern Robotics Ch. 5 videos.
2. **This lesson plus the example:** run the numerical-derivative check first so you can trust the
   analytic expression, then interpret the singularity table.
3. **Textbook:** read Modern Robotics §5.1-5.4 and work out by hand, on the 2-link example, the
   difference between the space and body Jacobians.
4. **Problems:** take the quiz in the Korean original (`rc quiz m7-jacobian-singularity`), then do
   exercises (1) through (3).
5. **Verification (optional):** build the same arm with the Robotics Toolbox for Python and
   compare Jacobian values.

## References

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 5 - <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics lecture videos - <https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos>
- Peter Corke, Robotics Toolbox for Python - <https://github.com/petercorke/robotics-toolbox-python>
- Bruno Siciliano et al., *Robotics: Modelling, Planning and Control*, Springer, 2009 - Ch. 3 (no link)
- Tsuneo Yoshikawa, "Manipulability of Robotic Mechanisms", IJRR 1985 (the original manipulability paper, no link)
