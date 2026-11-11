---
id: m2-inverse-kinematics
lang: en
title: Inverse kinematics
summary: Find the joint values that reach a desired end-effector position, analytically and with Jacobian-based numerical methods, and understand solution counts and singularities.
objectives:
  - Solve the inverse kinematics of a 2-link planar arm analytically and obtain both the elbow-up and elbow-down solutions.
  - Identify unreachable targets and singularities.
  - Implement Newton-Raphson numerical inverse kinematics using the Jacobian.
tags: [kinematics, manipulator, inverse-kinematics, jacobian]
---

# Inverse kinematics

Inverse kinematics (IK) answers "how far do I have to turn the joints to put the
fingertip at that point?" It is the inverse problem of forward kinematics,
$\boldsymbol{\theta} = f^{-1}(\mathbf{x})$ for $\mathbf{x} = f(\boldsymbol{\theta})$,
and it is the starting point of almost any task that commands a goal pose to an
arm. Unlike FK, the key point is that a solution may **not exist, may be one of
several, or may be infinite in number**.

## Concepts

### Existence and number of solutions

- **No solution:** the target lies outside the workspace (for a 2-link arm, $r > L_1 + L_2$ or $r < |L_1 - L_2|$).
- **Several solutions:** a 2-link arm reaches most points two ways, with the elbow bent up (elbow-up) or down (elbow-down). A 6-DOF industrial arm can have up to eight (or more) solutions.
- **Infinitely many solutions:** a **redundant** arm, with more joints than task dimensions.

### Analytical methods

Geometry (triangles, the law of cosines) or algebraic manipulation gives a closed
form. It is fast and yields all solutions at once, but is only possible for
certain structures (for example a 6-axis arm whose three wrist axes meet at a
point).

### Numerical methods and the Jacobian

The Jacobian $J(\boldsymbol{\theta}) = \partial f / \partial \boldsymbol{\theta}$ is
the matrix that converts joint velocities into end-effector velocities. Repeatedly
pushing the current error back into joint space through the Jacobian
(Newton-Raphson) works for general arms. However, it finds only **one solution
near the initial guess**, and convergence is not guaranteed.

### Singularities

At a pose where $\det J = 0$ there is some direction the end effector cannot move
in, and near it IK demands very large joint velocities. A 2-link arm is singular
at $\theta_2 = 0$ (fully extended) and at $\pi$ (fully folded). Numerical IK
softens this with damped least squares.

## Key formulas

Analytical 2-link IK (law of cosines):

$$\cos\theta_2 = \frac{x^2 + y^2 - L_1^2 - L_2^2}{2L_1L_2}, \qquad
\theta_2 = \operatorname{atan2}\!\left(\pm\sqrt{1-\cos^2\theta_2},\ \cos\theta_2\right)$$

$$\theta_1 = \operatorname{atan2}(y, x) - \operatorname{atan2}\!\left(L_2\sin\theta_2,\ L_1 + L_2\cos\theta_2\right)$$

If $|\cos\theta_2| > 1$ the target is unreachable. The 2-link Jacobian and its
determinant:

$$J = \begin{bmatrix} -L_1 s_1 - L_2 s_{12} & -L_2 s_{12} \\ L_1 c_1 + L_2 c_{12} & L_2 c_{12} \end{bmatrix}, \qquad \det J = L_1 L_2 \sin\theta_2$$

The Newton-Raphson iteration ($J^{\dagger}$ is the pseudoinverse):

$$\boldsymbol{\theta}_{k+1} = \boldsymbol{\theta}_k + J^{\dagger}(\boldsymbol{\theta}_k)\,\big(\mathbf{x}_d - f(\boldsymbol{\theta}_k)\big)$$

## Example

Solve $L_1 = L_2 = 1$ with target $(1, 1)$ by hand.

- $\cos\theta_2 = (1 + 1 - 1 - 1)/2 = 0$, so $\theta_2 = \pm 90^\circ$.
- $\theta_2 = +90^\circ$: $\theta_1 = 45^\circ - \operatorname{atan2}(1, 1) = 0^\circ$.
  Check with FK: $x = \cos 0 + \cos 90^\circ = 1$, $y = \sin 0 + \sin 90^\circ = 1$.
- $\theta_2 = -90^\circ$: $\theta_1 = 45^\circ - \operatorname{atan2}(-1, 1) = 90^\circ$.
  Check with FK: $x = \cos 90^\circ + \cos 0 = 1$, $y = \sin 90^\circ + \sin 0 = 1$.

```python
import numpy as np

L1, L2 = 1.0, 1.0


def fk(th):
    return np.array(
        [
            L1 * np.cos(th[0]) + L2 * np.cos(th[0] + th[1]),
            L1 * np.sin(th[0]) + L2 * np.sin(th[0] + th[1]),
        ]
    )


def jac(th):
    s1, c1 = np.sin(th[0]), np.cos(th[0])
    s12, c12 = np.sin(th[0] + th[1]), np.cos(th[0] + th[1])
    return np.array([[-L1 * s1 - L2 * s12, -L2 * s12], [L1 * c1 + L2 * c12, L2 * c12]])


def ik_analytic(x, y, elbow=+1):
    c2 = (x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2)
    if abs(c2) > 1:
        return None  # outside the workspace
    t2 = np.arctan2(elbow * np.sqrt(1 - c2**2), c2)
    t1 = np.arctan2(y, x) - np.arctan2(L2 * np.sin(t2), L1 + L2 * np.cos(t2))
    return np.array([t1, t2])


def ik_newton(xd, th0, iters=50, tol=1e-9):
    th = np.array(th0, dtype=float)
    for _ in range(iters):
        err = xd - fk(th)
        if np.linalg.norm(err) < tol:
            break
        th += np.linalg.pinv(jac(th)) @ err
    return th


print(np.rad2deg(ik_analytic(1, 1, +1)))  # [ 0. 90.]
print(np.rad2deg(ik_analytic(1, 1, -1)))  # [90. -90.]
th = ik_newton(np.array([1.0, 1.0]), [0.3, 0.5])
print(np.rad2deg(th).round(3), fk(th).round(6))
```

**Exercise:** (1) for 200 random targets inside the workspace, compute both
analytical solutions and verify with FK that the error is below $10^{-9}$.
(2) Record which solution the numerical IK converges to as you vary the initial
guess. (3) Observe what happens when the initial guess has $\theta_2 = 0$, then
replace `pinv` with damped least squares $J^T(JJ^T + \lambda^2 I)^{-1}$ and
compare.

## Self-check questions

1. At which target positions do the elbow-up and elbow-down solutions of a 2-link arm merge into one?
2. In which direction can the end effector not move at a pose where $\det J = 0$? Explain intuitively.
3. Give one case where numerical IK is preferable to analytical IK, and one where it is worse.

## How to study this stage

1. **Videos:** watch the Jacobian introduction in the Modern Robotics Ch. 5 lecture videos and Ch. 6, "Inverse Kinematics" (analytical and numerical IK).
2. **Textbook:** read Modern Robotics Ch. 6 (6.1 analytical, 6.2 numerical). If the Jacobian is new to you, reading only §5.1 first is enough. For more analytical IK examples, see Craig Ch. 4.
3. **This lesson plus the example:** work $(1, 1)$ by hand, run the code, then verify with FK.
4. **Problems:** take the quiz in the Korean original (`rc quiz m2-inverse-kinematics`), then do exercises (1) through (3). Do not skip (3) — it is the one that builds intuition for singularities.
5. **Optional tooling:** solve the same problem with `IKinSpace` from the `modern_robotics` package and compare.

## References

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 5 "Velocity Kinematics and Statics"
  and Ch. 6 "Inverse Kinematics" — <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics lecture video index — <https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos>
- Official Modern Robotics code library — <https://github.com/NxRLab/ModernRobotics>
- John J. Craig, *Introduction to Robotics: Mechanics and Control*, 4th ed., Pearson —
  Ch. 4 "Inverse Manipulator Kinematics".
- Bruno Siciliano, Lorenzo Sciavicco, Luigi Villani, Giuseppe Oriolo, *Robotics: Modelling,
  Planning and Control*, Springer, 2009 — Ch. 3 (Jacobian, singularities, IK algorithms).
