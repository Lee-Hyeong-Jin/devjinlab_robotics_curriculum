---
id: m4-sensor-models
lang: en
title: Robot sensors, noise, and observation models
summary: Survey how encoders, IMUs, and range sensors (lidar, ultrasound, depth) measure and where their errors come from, then write measurements as "truth plus noise" observation models and likelihoods.
objectives:
  - Explain what an encoder, an IMU, and a lidar each measure and what errors they carry (quantization, bias, white noise, outliers).
  - Write a measurement as an observation model z = h(x) + v and compute the Gaussian likelihood p(z|x).
  - Show with equations and code why a bias grows into drift once it is integrated.
tags: [sensors, encoder, imu, lidar, noise-model, observation-model]
---

# Robot sensors, noise, and observation models

A robot only knows the world through its sensors, and every sensor lies a little.
This lesson organizes what each sensor measures and how it errs, then writes those
measurements in the probabilistic form that the filters of M5 consume.

## Concepts

### Proprioceptive versus exteroceptive sensors

- **Proprioceptive:** measures the robot's own state. Wheel **encoders** (amount of rotation), the **IMU** (gyroscope = angular velocity, accelerometer = specific force, magnetometer = heading).
- **Exteroceptive:** measures the surroundings. **Lidar** and ultrasound (range), cameras (brightness), depth cameras.

Proprioceptive sensors are fast and less affected by the environment, but
**integrating them accumulates error**. Exteroceptive sensors give an absolute
reference (walls, landmarks) but are slower and full of outliers. Mixing the two
is the motivation for sensor fusion.

### Characteristic errors by sensor

| Sensor | Principle | Characteristic error |
|---|---|---|
| Encoder | counting pulses per revolution (CPR) | quantization, wheel slip, radius error |
| Gyroscope | Coriolis effect (MEMS) | bias (drifting over time), white noise, scale error |
| Accelerometer | displacement of a mass-spring | cannot separate gravity from motion acceleration, vibration noise |
| Lidar | time of flight / triangulation | noise proportional to range, failed returns (max value), glass and black objects |
| Ultrasound | round-trip time of a sound wave | wide beam width, multiple reflections |

### The observation model

If $h(x)$ is the value a sensor would ideally report in state $x$ (the robot pose,
the distance to a wall, …), then a measurement is $z = h(x) + v$. Treating $v$ as
a random variable lets you compute "the probability that this measurement arises
in this state," the **likelihood** $p(z \mid x)$. Localization ultimately means
finding the $x$ with high likelihood.

A sensor with many outliers, such as a lidar, is not well served by a single
Gaussian. The **beam model** expresses the measurement distribution as a mixture
of correct returns (Gaussian), objects blocking the path (short values), failed
returns (the maximum range), and random values.

## Key formulas

The Gaussian observation model and its likelihood:

$$z = h(x) + v,\quad v \sim \mathcal{N}(0, \sigma^2),\quad
p(z \mid x) = \frac{1}{\sqrt{2\pi}\,\sigma}\exp\!\left(-\frac{(z - h(x))^2}{2\sigma^2}\right)$$

Encoder resolution (wheel radius $r$): $\Delta s = 2\pi r / \text{CPR}$.

The gyroscope model and its heading error (sample period $\Delta t$, elapsed time $t$):

$$\omega_m = \omega + b + n,\quad n \sim \mathcal{N}(0, \sigma_n^2)
\;\Rightarrow\; e_\theta(t) \approx b\,t + \text{std}\;\sigma_n\sqrt{\Delta t\, t}$$

Bias grows **linearly** in time, white noise grows as $\sqrt{t}$ (a random walk).

The beam model (weights summing to 1):

$$p(z \mid x) = w_\text{hit}\,p_\text{hit} + w_\text{short}\,p_\text{short}
+ w_\text{max}\,p_\text{max} + w_\text{rand}\,p_\text{rand}$$

## Example

```python
import numpy as np

rng = np.random.default_rng(0)

# 1) Encoder: 1024 CPR, wheel radius 5 cm
cpr, r = 1024, 0.05
true_angle = 3.3  # rad
ticks = np.floor(true_angle / (2 * np.pi) * cpr)
meas_angle = ticks * 2 * np.pi / cpr
print(f"encoder quantization error: {(true_angle - meas_angle) * r * 1000:.3f} mm")

# 2) Gyroscope: at rest, bias 0.01 rad/s plus white noise, integrated at 100 Hz for 60 s
dt, n = 0.01, 6000
gyro = 0.01 + rng.normal(0.0, 0.05, n)
heading = np.cumsum(gyro) * dt
print(f"heading drift after 60 s: {np.rad2deg(heading[-1]):.1f} deg")

# 3) Lidar beam model: Gaussian + short outliers + max range
z_true, sigma, z_max, m = 2.0, 0.02, 8.0, 200
z = rng.normal(z_true, sigma, m)
u = rng.random(m)
short = u < 0.05
z[short] = rng.uniform(0.0, z_true, short.sum())  # something blocking the beam
z[(u >= 0.05) & (u < 0.08)] = z_max  # failed return
print(f"mean {z.mean():.3f} m, median {np.median(z):.3f} m")


def likelihood(z, z_exp, sigma=0.02):
    return np.exp(-0.5 * ((z - z_exp) / sigma) ** 2) / (np.sqrt(2 * np.pi) * sigma)


print(f"p(z=2.01 | 2.00) = {likelihood(2.01, 2.0):.2f}")
print(f"p(z=2.01 | 2.10) = {likelihood(2.01, 2.1):.2e}")
```

What to look for in the output: the quantization error is a small 0.25 mm, but the
gyroscope turns about 34° in only 60 seconds ($0.01 \times 60 = 0.6$ rad). The
lidar's 8% outliers push the mean off to 2.2 m while the median stays nearly
exact. The last two lines mean that the same measurement supports the hypothesis
"the wall is at 2.00 m" about twenty thousand times more than "2.10 m."

**Exercise:** (1) set the gyroscope bias to zero, simulate the 60-second drift 100
times, and check that the standard deviation matches $\sigma_n\sqrt{\Delta t\,t}$.
(2) Plot a histogram of the lidar measurements and find the four components of the
beam model by eye. (3) Pick a lidar from the awesome-2d-lidars list and transcribe
its datasheet range accuracy and angular resolution into a $\sigma$.

## Self-check questions

1. Besides quantization, give two reasons encoder odometry drifts over a long run.
2. How do a gyroscope's bias and its white noise each grow after integration?
3. Why use the median or a beam model instead of the mean when lidar measurements contain outliers?

## How to study this stage

1. **Videos (first):** review Gaussians and conditional probability with Stachniss's *Probability Primer*, then watch *Observation Models* and redraw the beam model figure in your notes.
2. **Textbook:** run Labbe's notebooks Ch. 1-3 yourself to develop the sense that "a measurement is a distribution."
3. **This lesson plus the example:** run the example and check by hand that each number matches the key formulas.
4. **Problems:** take the quiz in the Korean original (`rc quiz m4-sensor-models`), then do exercises (1) through (3). Always draw the graphs.
5. **Optional reinforcement:** if you are curious about real hardware wiring and communication, see the Inflearn course.

## References

- Cyrill Stachniss, "Observation Models" — <https://www.youtube.com/watch?v=SfwxLpdFB-o>
- Cyrill Stachniss, "Probability Primer" — <https://www.youtube.com/watch?v=JS5ndD8ans4>
- Roger Labbe, *Kalman and Bayesian Filters in Python*, Ch. 1-3 —
  <https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python>
- Inflearn, "현직자가 알려주는 로보틱스 시스템 완전 해부" (in Korean) — <https://www.inflearn.com/course/a-complete-breakdown>
- awesome-2d-lidars — <https://github.com/kaiaai/awesome-2d-lidars>
- Sebastian Thrun, Wolfram Burgard, Dieter Fox, *Probabilistic Robotics*, Ch. 6 "Robot Perception" (advanced).
