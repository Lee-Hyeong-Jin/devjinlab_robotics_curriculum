---
id: m4-filtering-basics
lang: en
title: "Filtering basics: moving average, low-pass, complementary filter"
summary: Smooth noisy sensor signals with a moving average and a first-order low-pass filter, then fuse gyroscope and accelerometer with a complementary filter to estimate tilt - building the intuition you need before the Kalman filter in M5.
objectives:
  - Implement a moving average and a first-order low-pass (IIR) filter and explain the trade-off between noise reduction and lag.
  - Compute the filter coefficient alpha from the time constant tau and the sample period dt.
  - Estimate tilt by combining the gyroscope (high frequency) and the accelerometer (low frequency) with a complementary filter.
tags: [filtering, low-pass, complementary-filter, imu, sensor-fusion]
---

# Filtering basics: moving average, low-pass, complementary filter

As the previous lesson showed, sensor values are either too shaky to use directly
(accelerometer) or drift away over time (gyroscope). This lesson handles that with
the three simplest filters. The arithmetic is a few lines, but the ideas — "less
noise means slower response" and "mix sensors whose weaknesses differ" — carry
straight through to the Kalman filter in the intermediate module M5. The
one-dimensional Kalman filter is covered properly in M5 alongside the Bayes
filter.

## Concepts

### Moving average

The average of the most recent $N$ samples. The standard deviation of independent
white noise shrinks by $1/\sqrt{N}$. In exchange the output **lags** by about
$(N-1)/2$ samples. If the signal changes quickly the average cannot keep up. Also,
keeping $N$ samples in memory is a burden on a microcontroller.

### First-order low-pass (exponential moving average)

Blend the new sample and the previous output in the ratio $\alpha$. It stores only
one state, and it passes changes slower than the time constant $\tau$ while
cutting faster ones (noise). The closer $\alpha$ is to 1 the smoother and the
slower it gets. The filter you attach to the derivative term of a PID controller
is exactly this one.

### Complementary filter

There are two ways to get tilt $\theta$ from an IMU.

- **Integrating the gyroscope:** accurate and smooth over short times, but it **drifts** because of bias (low-frequency error).
- **The accelerometer:** gives $\theta = \operatorname{atan2}(a_x, a_z)$ directly from the gravity direction. It does not drift, but vibration and motion acceleration make it **shake** (high-frequency error).

The two errors live in different frequency bands, so high-pass the gyroscope side,
low-pass the accelerometer side, and add them. Choosing the two filters so that
they sum to 1 (complementary) lets the true signal through undistorted. Drones and
balancing robots still use this widely.

## Key formulas

Moving average: $y_k = \dfrac{1}{N}\sum_{i=0}^{N-1} x_{k-i}$

First-order low-pass (time constant $\tau$, sample period $\Delta t$):

$$y_k = \alpha\,y_{k-1} + (1-\alpha)\,x_k,\qquad \alpha = \frac{\tau}{\tau + \Delta t}$$

The cutoff frequency is $f_c = 1/(2\pi\tau)$.

Complementary filter:

$$\hat\theta_k = \alpha\,(\hat\theta_{k-1} + \omega_k\,\Delta t) + (1-\alpha)\,\theta_{\text{acc},k}$$

The parenthesized term is a one-step **prediction** from the gyroscope, and the
term after it is the accelerometer **measurement**. This structure of "blend
prediction and measurement in some ratio" is the same as the Kalman filter, which
computes that ratio from the noise variances at every step.

## Example

Simulate an IMU tracking a true tilt $\theta(t) = 0.5\sin(0.5t)$. The gyroscope
gets a $0.02$ rad/s bias, and the accelerometer angle gets $\sigma = 0.1$ rad of
noise.

```python
import numpy as np

rng = np.random.default_rng(1)
dt = 0.01
t = np.arange(0, 10, dt)
theta = 0.5 * np.sin(0.5 * t)  # true tilt [rad]
omega = 0.25 * np.cos(0.5 * t)  # true angular velocity [rad/s]

gyro = omega + 0.02 + rng.normal(0, 0.02, t.size)  # bias + noise
acc_angle = theta + rng.normal(0, 0.1, t.size)  # angle from the accelerometer


def moving_average(x, n):
    c = np.cumsum(np.insert(x, 0, 0.0))
    y = np.empty_like(x)
    y[n - 1 :] = (c[n:] - c[:-n]) / n
    y[: n - 1] = c[1:n] / np.arange(1, n)  # average over whatever is available at the start
    return y


def low_pass(x, tau, dt):
    a = tau / (tau + dt)
    y = np.empty_like(x)
    y[0] = x[0]
    for k in range(1, x.size):
        y[k] = a * y[k - 1] + (1 - a) * x[k]
    return y


def complementary(gyro, acc_angle, tau, dt):
    a = tau / (tau + dt)
    est = np.empty_like(gyro)
    est[0] = acc_angle[0]
    for k in range(1, gyro.size):
        est[k] = a * (est[k - 1] + gyro[k] * dt) + (1 - a) * acc_angle[k]
    return est


def rms(e):
    return np.sqrt(np.mean(e**2))


estimates = {
    "accelerometer raw": acc_angle,
    "gyro integration": np.cumsum(gyro) * dt,
    "moving average(25)": moving_average(acc_angle, 25),
    "low-pass(0.2 s)": low_pass(acc_angle, 0.2, dt),
    "complementary(0.5 s)": complementary(gyro, acc_angle, 0.5, dt),
}
for name, est in estimates.items():
    print(f"{name:22s} RMS error {np.rad2deg(rms(est - theta)):5.2f} deg")
```

The results are roughly 5.9° for the raw signal, 6.3° for gyro integration (which
keeps growing because of the bias), 1.7° for the moving average, 2.2° for the
low-pass, and 0.85° for the complementary filter. A single-sensor filter has to
compromise between noise and lag, while the complementary filter takes the best of
both sensors.

**Exercise:** (1) sweep the low-pass $\tau$ from 0.05 to 1.0 s, plot the RMS error
curve, and explain why an optimum appears. (2) Overlay $\theta(t)$ with each
estimate and see the moving average's lag with your own eyes. (3) Make $\tau$ very
large and very small in the complementary filter and identify which single sensor
it then behaves like.

## Self-check questions

1. If you double the moving average window $N$, how do the noise and the lag each change?
2. For $\Delta t = 0.01$ s and a time constant $\tau = 0.1$ s, what are the low-pass $\alpha$ and the cutoff frequency?
3. Explain what it means to say that in a complementary filter the gyroscope term acts as a high-pass and the accelerometer term as a low-pass.

## How to study this stage

1. **Textbook (first):** run the g-h filter notebook in Labbe Ch. 1 and absorb the structure "a weighted average of prediction and measurement."
2. **This lesson plus the example:** run the example, then do exercise (1), plotting graphs as you vary $\tau$.
3. **Problems:** work the $\alpha$ and $f_c$ calculations in the quiz by hand.
4. **Reinforcement:** read about real IMU characteristics in the sensors chapter of Correll's book, and if your intuition for filter frequencies is thin, see the MATLAB Tech Talks.
5. **Optional preview:** skim Ch. 2-3 of *Probabilistic Robotics* to connect to the Kalman filter in M5.

## References

- Roger Labbe, *Kalman and Bayesian Filters in Python*, Ch. 1 —
  <https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python>
- Brian Douglas, MATLAB Tech Talks "Control Systems" — <https://mathworks.com/videos/tech-talks/controls>
- Nikolaus Correll et al., *Introduction to Autonomous Robots* — <https://introduction-to-autonomous-robots.github.io/>
- Sebastian Thrun, Wolfram Burgard, Dieter Fox, *Probabilistic Robotics*, MIT Press —
  <https://robots.stanford.edu/probabilistic-robotics/>
