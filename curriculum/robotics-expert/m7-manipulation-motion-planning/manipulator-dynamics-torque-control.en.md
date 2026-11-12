---
id: m7-manipulator-dynamics-torque-control
lang: en
title: "Manipulator dynamics and torque control"
summary: Build the equations of motion of a 2-link arm with the Lagrangian, $M(\theta)\ddot{\theta} + c(\theta,\dot{\theta}) + g(\theta) = \tau$, see the role of the inertia, Coriolis, and gravity terms, then compare the tracking performance of PD, gravity-compensated PD, and computed-torque control in a numpy simulation.
objectives:
  - Derive the manipulator equations of motion from the Lagrangian $L = K - P$ and distinguish the mass matrix, the Coriolis/centrifugal term, and the gravity term.
  - Distinguish the uses of inverse dynamics (computing torque) and forward dynamics (computing and integrating acceleration), and verify the simulator through energy conservation.
  - Implement PD, gravity-compensated PD, and computed-torque control and explain how model knowledge affects tracking error.
tags: [manipulator, dynamics, lagrangian, computed-torque, control]
---

# Manipulator dynamics and torque control

The PID of M3 controlled from error alone, with no model. A manipulator's inertia changes with
its configuration, its joints push and pull on each other, and it must hold against gravity at
all times. This lesson gathers those effects into a single equation and puts it into the control.

## Concepts

### The Lagrangian equations of motion

Applying the Euler-Lagrange equation to $L = K - P$ (kinetic minus potential energy) gives every
open-chain arm an equation of the same form.

- **Mass matrix $M(\theta)$:** symmetric and positive definite, and it changes with configuration.
  Extending the arm increases the inertia of the first joint.
- **Coriolis and centrifugal term $c(\theta, \dot{\theta})$:** quadratic in velocity. It is the
  effect of joints pushing and pulling each other at speed.
- **Gravity term $g(\theta)$:** the torque needed even at rest. It is the largest term at low speed.

**Inverse dynamics** finds the $\tau$ required for a desired $\ddot{\theta}$ (the controller);
**forward dynamics** obtains $\ddot{\theta} = M^{-1}(\tau - c - g)$ from $\tau$ and integrates it
(the simulator). Beyond six degrees of freedom, libraries such as Pinocchio compute this with
$O(n)$ recursions.

### Three stages of torque control

1. **PD:** $\tau = K_p e + K_d \dot{e}$. Gravity leaves a steady-state error.
2. **Gravity-compensated PD:** add $g(\theta)$. Holding still is accurate, but error remains on
   fast trajectories.
3. **Computed torque:** cancel the nonlinearities with the model, making each joint the linear
   system $\ddot{e} + K_d\dot{e} + K_p e = 0$. The PD terms absorb model error.

## Key formulas

$$M(\theta)\ddot{\theta} + c(\theta, \dot{\theta}) + g(\theta) = \tau$$

Computed-torque control ($\theta_d$ is the reference trajectory, $e = \theta_d - \theta$):

$$\tau = M(\theta)\big(\ddot{\theta}_d + K_d \dot{e} + K_p e\big) + c(\theta, \dot{\theta}) + g(\theta)$$

## Example

A 2-link arm with a point mass at the end of each link. Verify the equations through energy
conservation, then track a sine wave with the three controllers.

```python
import numpy as np

L1, L2, M1, M2, G = 1.0, 0.8, 2.0, 1.0, 9.81  # masses are point masses at each link's end


def dynamics_terms(q, qd):
    c2, s2 = np.cos(q[1]), np.sin(q[1])
    M = np.array(
        [
            [M1 * L1**2 + M2 * (L1**2 + 2 * L1 * L2 * c2 + L2**2), M2 * (L1 * L2 * c2 + L2**2)],
            [M2 * (L1 * L2 * c2 + L2**2), M2 * L2**2],
        ]
    )
    h = M2 * L1 * L2 * s2
    c = np.array([-h * (2 * qd[0] * qd[1] + qd[1] ** 2), h * qd[0] ** 2])  # Coriolis/centrifugal
    g = np.array(
        [
            (M1 + M2) * L1 * G * np.cos(q[0]) + M2 * L2 * G * np.cos(q[0] + q[1]),
            M2 * L2 * G * np.cos(q[0] + q[1]),
        ]
    )
    return M, c, g


def energy(q, qd):
    M, _, _ = dynamics_terms(q, qd)
    y1 = L1 * np.sin(q[0])
    y2 = y1 + L2 * np.sin(q[0] + q[1])
    return 0.5 * qd @ M @ qd + G * (M1 * y1 + M2 * y2)


def step(q, qd, tau, dt):
    """Integrate the forward dynamics with RK4."""

    def f(x):
        M, c, g = dynamics_terms(x[:2], x[2:])
        return np.concatenate([x[2:], np.linalg.solve(M, tau - c - g)])

    x = np.concatenate([q, qd])
    k1 = f(x)
    k2 = f(x + dt / 2 * k1)
    k3 = f(x + dt / 2 * k2)
    k4 = f(x + dt * k3)
    x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return x[:2], x[2:]


# 1) with zero torque, energy is conserved
q, qd, dt = np.array([0.3, 0.5]), np.zeros(2), 1e-3
E0 = energy(q, qd)
for _ in range(3000):
    q, qd = step(q, qd, np.zeros(2), dt)
print(f"energy change after 3 s of free motion: {energy(q, qd) - E0:.2e} J")


# 2) tracking a reference trajectory
def ref(t, w=2.0):
    qr = np.array([0.5 + 0.5 * np.sin(w * t), 0.8 * np.cos(w * t)])
    qdr = np.array([0.5 * w * np.cos(w * t), -0.8 * w * np.sin(w * t)])
    qddr = np.array([-0.5 * w**2 * np.sin(w * t), -0.8 * w**2 * np.cos(w * t)])
    return qr, qdr, qddr


Kp, Kd = 100.0, 20.0  # critically damped: Kd = 2*sqrt(Kp)
for name in ["PD", "PD+gravity", "computed torque"]:
    q, qd = ref(0)[0].copy(), ref(0)[1].copy()
    errs = []
    for k in range(4000):
        qr, qdr, qddr = ref(k * dt)
        e, ed = qr - q, qdr - qd
        M, c, g = dynamics_terms(q, qd)
        if name == "PD":
            tau = Kp * e + Kd * ed
        elif name == "PD+gravity":
            tau = Kp * e + Kd * ed + g
        else:
            tau = M @ (qddr + Kp * e + Kd * ed) + c + g
        q, qd = step(q, qd, tau, dt)
        errs.append(np.linalg.norm(e))
    print(f"{name:15s} max error over the last 2 s {np.degrees(max(errs[2000:])):7.3f} deg")
```

The energy change is on the order of $10^{-10}$ J, so $M$, $c$, and $g$ agree with one another.
The maximum tracking errors are about 26° for PD, about 7° for gravity-compensated PD, and about
0.01° for computed torque.

**Exercise:** (1) Make only `M2` wrong inside the controller by a factor of 1.2 (model error) and
observe the computed-torque error. (2) Vary `w` over 1, 2, and 4 and build a table of errors for
the three controllers.

## Self-check questions

1. Explain with the equations how $M_{11}$ changes as the arm extends and folds.
2. Why does PD without gravity compensation leave a steady-state error?
3. Explain the principle by which computed-torque control makes a joint a linear second-order system, and its limits under model error.

## How to study this stage

1. **Video (first):** watch the Lagrangian derivation and the 2-link example in the Modern
   Robotics Ch. 8 videos.
2. **The example:** deliberately get one term wrong and see whether energy leaks.
3. **Control:** watch the computed-torque portion of the Ch. 11 videos.
4. **Problems:** take the quiz in the Korean original
   (`rc quiz m7-manipulator-dynamics-torque-control`), then do exercises (1) and (2).
5. **Depth (optional):** compute the dynamics of a 6-DOF arm with the Coursera Course 3
   assignments or Pinocchio exercise 4.

## References

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 8 and 11 - <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics videos, Ch. 8 <https://www.youtube.com/playlist?list=PLggLP4f-rq00TQamz2pXjzPWpuxhVN_Vy>, Ch. 11 <https://www.youtube.com/playlist?list=PLggLP4f-rq02N54sD6xwdDWlDScvb32Pp>
- Coursera Modern Robotics Specialization - <https://www.coursera.org/specializations/modernrobotics>
- Pinocchio exercise 4 - <https://docs.ros.org/en/jazzy/p/pinocchio/doc/d-practical-exercises/4-dyn.html>
