---
id: m5-odometry-sensor-fusion
lang: en
title: "Odometry and sensor fusion (IMU + wheels)"
summary: Combine wheel odometry and an IMU gyroscope with an EKF to reduce the drift of dead reckoning. Implement the robot_localization style of state design, which treats velocities as measurements, in numpy, then read how ekf_filter_node publishes odom → base_link in ROS 2 and what its configuration file says.
objectives:
  - Compare the error characteristics of wheel odometry and an IMU (slip and scale error versus bias and noise) and explain why fusion is needed.
  - Implement an EKF whose state holds position, heading, and velocities and which updates sequentially from the velocity measurements of both sensors.
  - Read what the frame settings and the per-sensor choice of fused variables mean in robot_localization's ekf.yaml.
tags: [odometry, imu, sensor-fusion, ekf, robot-localization, ros2]
---

# Odometry and sensor fusion (IMU + wheels)

The differential-drive odometry of M3 picks up **heading** error from the slightest wheel slip or
difference in left and right wheel radii, and heading error grows into position error in
proportion to the distance traveled. An IMU gyroscope is immune to slip but carries a bias.
Fusing the two with an EKF is the standard answer, and in ROS 2 `robot_localization` does that job.

## Concepts

### The error characteristics of the two sensors

| Sensor | Measures well | Weakness |
|---|---|---|
| Wheel encoder | forward velocity $v$ | $\omega$ goes wrong from slip and wheel radius error |
| IMU gyroscope | angular velocity $\omega$ | a small bias (which drifts once integrated); cannot measure forward velocity |

So you mostly **trust $v$ from the wheels and $\omega$ from the gyroscope**. Express that
confidence through the measurement covariance $R$ and the Kalman filter settles the ratio itself.

### State design: velocities as measurements

Take the state to be $s = [x, y, \theta, v, \omega]$ and model the sensors as measuring
**velocities**. Position and heading are integrated inside the filter. Each sensor can be folded
in as it arrives, so differing rates are no problem. `robot_localization` uses the same approach
over a 15-dimensional state.

### Continuous versus global estimation

The fused result is smooth, but with no absolute reference it still **drifts**. That is why it is
published as `odom → base_link`, with the drift correction left to AMCL or SLAM through
`map → odom` (the frame tree of the M8 tf2 lesson).

## Key formulas

The constant-velocity motion model and the nonzero off-diagonal terms of its Jacobian:

$$f(s) = \begin{bmatrix} x + v\cos\theta\,\Delta t \\ y + v\sin\theta\,\Delta t \\ \theta + \omega\Delta t \\ v \\ \omega \end{bmatrix},\quad
\frac{\partial x'}{\partial \theta} = -v\sin\theta\,\Delta t,\ \frac{\partial y'}{\partial \theta} = v\cos\theta\,\Delta t$$

The measurement models are linear ($H_w$ selects $v$ and $\omega$, $H_i$ selects $\omega$), and
updating twice from the same $\omega$ gives the inverse-variance weighted mean
$\hat\omega = (\omega_w/R_w + \omega_i/R_i)/(1/R_w + 1/R_i)$.

## Example

A 60-second drive. The wheel $\omega$ carries a bias (0.02 rad/s) and slip, and the gyroscope a
bias of 0.002 rad/s.

```python
import numpy as np

rng = np.random.default_rng(7)
dt, T = 0.05, 1200  # 20 Hz, 60 s


def f(s):
    """Constant-velocity model. State s = [x, y, theta, v, omega]."""
    x, y, th, v, w = s
    return np.array([x + v * np.cos(th) * dt, y + v * np.sin(th) * dt, th + w * dt, v, w])


def F_jac(s):
    _, _, th, v, _ = s
    J = np.eye(5)
    J[0, 2], J[0, 3] = -v * np.sin(th) * dt, np.cos(th) * dt
    J[1, 2], J[1, 3] = v * np.cos(th) * dt, np.sin(th) * dt
    J[2, 4] = dt
    return J


def kf_update(s, P, z, H, R):
    K = P @ H.T @ np.linalg.inv(H @ P @ H.T + R)
    return s + K @ (z - H @ s), (np.eye(5) - K @ H) @ P


H_wheel = np.array([[0, 0, 0, 1, 0], [0, 0, 0, 0, 1.0]])  # wheels: v, omega
R_wheel = np.diag([0.02**2, 0.05**2])
H_imu = np.array([[0, 0, 0, 0, 1.0]])  # IMU gyroscope: omega
R_imu = np.array([[0.01**2]])
Q = np.diag([1e-6, 1e-6, 1e-6, 0.05**2, 0.1**2]) * dt

truth, dr = np.zeros(5), np.zeros(5)  # dr: dead reckoning from the wheels alone
s, P = np.zeros(5), np.eye(5) * 0.01
for k in range(T):
    t = k * dt
    truth[3], truth[4] = 0.5, 0.3 * np.sin(0.2 * t)
    truth = f(truth)
    slip = 0.03 if 20 < t < 30 else 0.0
    z_wheel = truth[3:] + [0.0, 0.02 + slip] + rng.normal(0, [0.02, 0.05])
    z_imu = truth[4:] + 0.002 + rng.normal(0, 0.01, 1)

    dr[3:] = z_wheel
    dr = f(dr)

    J = F_jac(s)
    s, P = f(s), J @ P @ J.T + Q  # prediction
    s, P = kf_update(s, P, z_wheel, H_wheel, R_wheel)  # wheel update
    s, P = kf_update(s, P, z_imu, H_imu, R_imu)  # IMU update

for name, est in [("wheels only", dr), ("EKF", s)]:
    pos_err = np.linalg.norm(est[:2] - truth[:2])
    print(f"{name}: position error {pos_err:.2f} m, heading error {np.rad2deg(est[2] - truth[2]):.1f} deg")
```

Integrating the wheels alone leaves more than 10 m of position error and about 80° of heading
error, while the EKF stays near 1.4 m and 11°. The residual error comes mostly from the gyroscope
bias and cannot be removed without an absolute reference (a map). That is the job of the next two
lessons.

### Reading the ROS 2 configuration

The `ekf_filter_node` configuration corresponds to the code above (an excerpt showing only the
structure).

```yaml
ekf_filter_node:
  ros__parameters:
    two_d_mode: true
    world_frame: odom          # publishes odom -> base_link
    odom0: /wheel/odometry
    odom0_config: [false, false, false, false, false, false,
                   true, false, false, false, false, true,
                   false, false, false]  # fuse only vx and vyaw
    imu0: /imu/data            # imu0_config sets only vyaw to true
```

The 15 booleans are in the order x, y, z, roll, pitch, yaw, vx, vy, vz, vroll, vpitch, vyaw, ax,
ay, az.

**Exercise:** (1) Explain how the result degrades when you set the $\omega$ variance of `R_wheel`
equal to that of `R_imu`. (2) Add a gyroscope bias $b$ to the state and check whether it is
estimated during the stationary intervals. (3) Tabulate the fused variables that are enabled in
the ekf.yaml of the Nav2 guide.

## Self-check questions

1. Why is heading error especially dangerous in wheel odometry?
2. What is the advantage of modeling the sensors as measuring velocity instead of position?
3. Why is the fused result published as `odom → base_link` rather than `map → base_link`?

## How to study this stage

1. **This lesson plus the example (first):** run the example and plot the trajectories.
2. **Official guide:** read Nav2's "Smoothing Odometry using Robot Localization" and match
   ekf.yaml against the excerpt in this lesson.
3. **A ROS 2 Jazzy example:** read the launch file and topic wiring in the Automatic Addison article.
4. **Problems:** take the quiz in the Korean original (`rc quiz m5-odometry-sensor-fusion`), then
   do exercises (1) through (3).
5. **Korean reinforcement:** read the EKF sensor fusion chapter of Choi Jong-myung's Wikidocs book.
6. **Depth (optional):** learn $Q$ tuning from Labbe's Kalman Filter Design chapter.

## References

- Nav2 First-Time Robot Setup Guide, "Setting Up Odometry" - <https://docs.nav2.org/rolling/configuration_and_development/first_time_robot_setup_guide/odom/setup_robot_localization/>
- robot_localization official documentation (ROS 2 Rolling) - <https://docs.ros.org/en/rolling/p/robot_localization/>
- Automatic Addison, "Sensor Fusion and Robot Localization Using ROS 2 Jazzy" -
  <https://automaticaddison.com/sensor-fusion-and-robot-localization-using-ros-2-jazzy/>
- 최종명, "ROS2로 배우는 자율주행 로봇 센서 융합과 SLAM" (Wikidocs, in Korean) - <https://wikidocs.net/book/18464>
- Roger Labbe, *Kalman and Bayesian Filters in Python* - <https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python>
