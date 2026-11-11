---
id: m3-pid-control
lang: en
title: PID control
summary: Understand what each term of a PID controller does, implement it in discrete time, and apply it to the heading control of a mobile robot.
objectives:
  - Explain how the proportional, integral, and derivative terms affect the response (rise time, overshoot, steady-state error).
  - Implement a discrete-time PID controller and mitigate integral windup and derivative kick.
  - Design a heading control loop for a differential drive robot and tune the gains step by step.
tags: [control, pid, feedback]
---

# PID control

So far we have assumed that a robot moves exactly as commanded. Real robots
differ from their commands because of friction, motor lag, and wheel slip.
**Feedback control** keeps correcting the command by looking at the difference
(the error) between the measurement and the target. PID is the simplest such
scheme and the one behind most control loops in industry. The controller you build
here is a core component of the next lesson, path following.

## Concepts

### The feedback loop

Given a setpoint $r(t)$, a measurement $y(t)$, and the error
$e(t) = r(t) - y(t)$, compute a control input $u(t)$, apply it to the plant, and
measure again. For heading control of a mobile robot, $r$ is the target heading,
$y$ is the current $\theta$, and $u$ is the angular velocity command $\omega$.

### What the three terms do

- **P (proportional):** pushes in proportion to the present error. Raising $K_p$ makes the response faster but increases overshoot and oscillation. With friction or a disturbance, P alone can leave a **steady-state error**.
- **I (integral):** accumulates past error and removes steady-state error. Too much of it creates slow oscillation, and while the actuator is saturated the integral keeps piling up — **integral windup**.
- **D (derivative):** reacts to the rate of change of the error and so acts as a "brake," reducing overshoot. In exchange it amplifies sensor noise, and a step change in the target produces a momentary large output (**derivative kick**). Differentiating the measurement ($-\dot{y}$) or adding a low-pass filter softens this.

### Angle errors must be wrapped

In heading control, if the target is $179^\circ$ and the current heading is
$-179^\circ$, the real error is $+2^\circ$, not $-358^\circ$. Always wrap the error
into the range $(-\pi, \pi]$. Path following uses the same treatment repeatedly.

### A practical tuning order

1. With $K_i = K_d = 0$, raise $K_p$ until the response is fast but slightly oscillatory.
2. Add $K_d$ to reduce overshoot.
3. Only if steady-state error remains, add a small $K_i$, together with output limits and anti-windup.

Rules of thumb such as Ziegler-Nichols exist, but tuning while plotting the
response in simulation is the best way to learn.

## Key formulas

$$u(t) = K_p\,e(t) + K_i\int_0^t e(\tau)\,d\tau + K_d\,\frac{de(t)}{dt}$$

Discrete time (sample period $\Delta t$):

$$u_k = K_p e_k + K_i \sum_{j=0}^{k} e_j\,\Delta t + K_d\,\frac{e_k - e_{k-1}}{\Delta t}$$

Wrapping the angle error:

$$e = \operatorname{atan2}\big(\sin(\theta_d - \theta),\ \cos(\theta_d - \theta)\big)$$

## Example

Turn the heading of a differential drive robot ($\dot\theta = \omega$) from $0$ to
$90^\circ$. The motor limit is $|\omega| \le 3$ rad/s, and a constant disturbance
$d = -0.3$ rad/s stands in for floor friction eating part of the command, so that
the difference between P and PI becomes visible.

```python
import numpy as np


def wrap(a):
    return np.arctan2(np.sin(a), np.cos(a))


class PID:
    def __init__(self, kp, ki, kd, dt, u_max):
        self.kp, self.ki, self.kd, self.dt, self.u_max = kp, ki, kd, dt, u_max
        self.integral, self.prev_y = 0.0, None

    def update(self, e, y):
        d_y = 0.0 if self.prev_y is None else wrap(y - self.prev_y) / self.dt
        self.prev_y = y
        u = self.kp * e + self.ki * self.integral - self.kd * d_y  # derivative on measurement
        u_sat = float(np.clip(u, -self.u_max, self.u_max))
        if u == u_sat:  # stop integrating while saturated (anti-windup)
            self.integral += e * self.dt
        return u_sat


def run(kp, ki, kd, T=5.0, dt=0.01, disturbance=-0.3):
    ctrl, th, target = PID(kp, ki, kd, dt, u_max=3.0), 0.0, np.pi / 2
    for _ in range(int(T / dt)):
        w = ctrl.update(wrap(target - th), th)
        th += (w + disturbance) * dt
    return np.rad2deg(wrap(target - th))


print(f"P  only : {run(4, 0, 0):6.2f} deg left")  # about 4.3 deg steady-state error
print(f"PI      : {run(4, 2, 0):6.2f} deg left")  # under 1 deg
print(f"PID     : {run(4, 2, 0.2):6.2f} deg left")  # under 1 deg (at t = 5 s)
```

With P alone the robot settles where $K_p e = 0.3$, that is at
$e = 0.075$ rad $\approx 4.3^\circ$. The integral term removes that leftover error.

**Exercise:** (1) plot $\theta(t)$ for each case and compare rise time and
overshoot. (2) Delete the anti-windup line and raise $K_i$ to reproduce the large
overshoot windup causes. (3) Add noise with a standard deviation of $1^\circ$ to
the measurement and watch how much the output $\omega$ shakes as you vary $K_d$.

## Self-check questions

1. Explain why P control alone leaves a steady-state error, using the disturbance in the example above.
2. Under what conditions does integral windup occur, and what are two ways to prevent it?
3. If the angle error is not wrapped, how does the robot move when the target is $170^\circ$ and the current heading is $-170^\circ$?

## How to study this stage

1. **Videos (first):** watch the PID introduction videos in Brian Douglas's control lectures from MATLAB Tech Talks to build intuition for the P, I, and D terms.
2. **Textbook:** read the integral windup and tuning parts of the PID chapter in Åström & Murray's *Feedback Systems*. Supplement with the robotics-oriented treatment in Modern Robotics §11.2-11.3.
3. **This lesson plus the example:** run the example and check the P / PI / PID numbers yourself.
4. **Problems:** take the quiz in the Korean original (`rc quiz m3-pid-control`), then do exercises (1) through (3). Be sure to actually plot the graphs.
5. **Optional reinforcement:** look at motor-level PID in the joint control lectures at QUT Robot Academy.

## References

- Brian Douglas, MATLAB Tech Talks "Control Systems" — <https://mathworks.com/videos/tech-talks/controls>
- Karl J. Åström, Richard M. Murray, *Feedback Systems: An Introduction for Scientists and
  Engineers*, Princeton University Press — the PID control chapter.
- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 11 "Robot Control" —
  <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- QUT Robot Academy (Peter Corke) — <https://robotacademy.net.au/>
