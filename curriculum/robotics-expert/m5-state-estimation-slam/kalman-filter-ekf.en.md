---
id: m5-kalman-filter-ekf
lang: en
title: "The Kalman filter (1D to multivariate) and the EKF"
summary: Approximating the belief with a single Gaussian turns the Bayes filter into closed-form updates of a mean and a variance - the Kalman filter. Build intuition for the Kalman gain in one dimension, then extend to the matrix form of the multivariate filter and to the EKF, which linearizes nonlinear models.
objectives:
  - Write the prediction and update equations of the 1D Kalman filter without deriving them, and explain that the Kalman gain is the ratio of confidence between prediction and measurement.
  - Choose the state vector and the F, H, Q, and R matrices and implement a constant-velocity multivariate Kalman filter in numpy.
  - Explain the structure and the limits of the EKF, which linearizes nonlinear motion and observation models with Jacobians.
tags: [kalman-filter, ekf, gaussian, jacobian, state-estimation]
---

# The Kalman filter (1D to multivariate) and the EKF

The histogram filter is intuitive, but the grid explodes once the state has several dimensions.
The Kalman filter instead assumes the belief is a **Gaussian** $\mathcal{N}(\mu, \Sigma)$. With a
linear model and Gaussian noise the belief stays Gaussian after prediction and correction, so
only the mean and the covariance need updating. Where the complementary filter of M4 mixed with a
fixed ratio $\alpha$, the Kalman filter computes that ratio - the Kalman gain - from the
uncertainties at every step.

## Concepts

### The 1D Kalman filter

When the state is a single scalar $x$, the belief is a mean $\mu$ and a variance $P$.

- **Prediction:** add the displacement $u$; uncertainty grows by the motion noise variance $Q$.
- **Update:** multiply the difference between the measurement $z$ (variance $R$) and the
  prediction - the innovation - by the gain $K$ and add it. If $P$ is larger than $R$ then
  $K \to 1$ (trust the measurement); if smaller, $K \to 0$ (trust the prediction).

Multiplying two Gaussians gives a variance smaller than either of them. Combining two independent
pieces of information leaves you more certain than either one alone.

### The multivariate Kalman filter

Write the state as a vector (position and velocity, say) and the model as matrices. $F$ is the
state transition, $B$ the control input, $H$ the map from state to measurement, and $Q$ and $R$
the covariances. The key point is that measuring only position still estimates velocity, through
the **covariance** between position and velocity.

### The EKF

Most robot models are nonlinear (the $\cos\theta$ of differential drive, the $\sqrt{\cdot}$ and
$\operatorname{atan2}$ of range-and-bearing measurements). The EKF linearizes at the current
estimate with the Jacobians $F_t = \partial f/\partial x$ and $H_t = \partial h/\partial x$ and
then uses the same equations. The mean is carried through the nonlinear function directly, and
only the covariance is propagated with the Jacobian. It can diverge when the linearization error
is large (high uncertainty, sharp turns) or the initial estimate is wrong. The alternatives are
the UKF and the particle filter of the next lesson.

## Key formulas

Prediction:

$$\bar\mu_t = F\mu_{t-1} + Bu_t,\qquad \bar\Sigma_t = F\Sigma_{t-1}F^\top + Q$$

Update:

$$K_t = \bar\Sigma_t H^\top (H\bar\Sigma_t H^\top + R)^{-1}$$

$$\mu_t = \bar\mu_t + K_t(z_t - H\bar\mu_t),\qquad \Sigma_t = (I - K_t H)\bar\Sigma_t$$

In one dimension this reduces to $K = P/(P+R)$. The EKF replaces $F\mu$ with $f(\mu, u)$ and
$H\bar\mu$ with $h(\bar\mu)$, and puts the Jacobians where $F$ and $H$ stand.

## Example

First in one dimension: estimate the position of a robot commanded to move 1 m per step, using a
position sensor like GPS ($\sigma = 2$ m).

```python
import numpy as np

rng = np.random.default_rng(0)
Q, R = 0.1**2, 2.0**2  # motion and measurement noise variances
x_true, mu, P = 0.0, 0.0, 10.0**2  # truth, initial estimate, initial variance (unknown)
errs_raw, errs_kf = [], []

for k in range(50):
    x_true += 1.0 + rng.normal(0, np.sqrt(Q))  # actual motion
    z = x_true + rng.normal(0, np.sqrt(R))  # position measurement

    mu, P = mu + 1.0, P + Q  # prediction
    K = P / (P + R)  # Kalman gain
    mu, P = mu + K * (z - mu), (1 - K) * P  # update

    errs_raw.append(z - x_true)
    errs_kf.append(mu - x_true)
    if k in (0, 1, 5, 49):
        print(f"k={k:2d}  K={K:.3f}  sigma={np.sqrt(P):.2f}")

print("measurement-only RMS", np.sqrt(np.mean(np.square(errs_raw))).round(2))
print("KF RMS              ", np.sqrt(np.mean(np.square(errs_kf))).round(2))
```

At first $P$ is large, so $K \approx 1$ and the filter takes the measurement at face value; the
gain shrinks every step until, after 50 steps, $K \approx 0.05$ and the filter mostly trusts its
prediction. The error ends up far below that of the measurement alone (about 2 m).

Next, a constant-velocity model that estimates position and velocity together while measuring
only position.

```python
import numpy as np

rng = np.random.default_rng(1)
dt = 0.1
F = np.array([[1, dt], [0, 1]])
H = np.array([[1.0, 0.0]])
Q = 0.05 * np.array([[dt**3 / 3, dt**2 / 2], [dt**2 / 2, dt]])  # acceleration noise
R = np.array([[0.5**2]])

x = np.array([0.0, 2.0])  # truth: moving at 2 m/s
mu, S = np.zeros(2), np.eye(2) * 10.0
for _ in range(100):
    x = F @ x
    z = H @ x + rng.normal(0, 0.5, 1)
    mu, S = F @ mu, F @ S @ F.T + Q
    K = S @ H.T @ np.linalg.inv(H @ S @ H.T + R)
    mu = mu + K @ (z - H @ mu)
    S = (np.eye(2) - K @ H) @ S

print("true speed 2.0, estimated speed", mu[1].round(2), "+/-", np.sqrt(S[1, 1]).round(2))
```

**Exercise:** (1) Explain how the steady-state $K$ and the RMS change in the 1D example when you
raise $Q$ by a factor of 100. (2) Deliberately set $R$ ten times smaller than reality and observe
the filter "over-trusting" the measurements. (3) Change the observation in the constant-velocity
example to a range $\sqrt{x^2 + d^2}$ (a beacon $d$ m to the side), derive the Jacobian $H_t$ by
hand, and rework it as an EKF.

## Self-check questions

1. In the 1D Kalman filter, what are the Kalman gain and the update result when $P \gg R$, and when $P \ll R$?
2. Explain in terms of the off-diagonal entries of the covariance $\Sigma$ why velocity is estimated when only position is measured.
3. Give two situations in which the EKF is prone to diverging, and the alternatives worth considering then.

## How to study this stage

1. **Textbook (first):** run Labbe's Gaussians and One Dimensional Kalman Filters chapters and
   compare them with the 1D example here.
2. **Videos:** organize the matrix form with Stachniss's "Kalman Filter & EKF," then see it applied
   in "EKF Localization."
3. **This lesson plus the examples:** run both examples and do exercises (1) through (3). Exercise
   (3) is your first EKF implementation.
4. **Problems:** take the quiz in the Korean original (`rc quiz m5-kalman-filter-ekf`).
5. **Depth:** read Labbe's Multivariate Kalman Filters, Kalman Filter Math, and Extended Kalman
   Filters chapters. Solve the same problem with `filterpy`'s `KalmanFilter` and match the result
   against your hand-written implementation.
6. **More practice (optional):** ROB 530 HW 2-3 for further work on nonlinear filters.

## References

- Roger Labbe, *Kalman and Bayesian Filters in Python*, Ch. 4-10 -
  <https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python>
- Cyrill Stachniss, "Kalman Filter & EKF" - <https://www.youtube.com/watch?v=E-6paM_Iwfc>
- Cyrill Stachniss, "EKF Localization" - <https://www.youtube.com/watch?v=PiCC-SxWlH8>
- University of Michigan, ROB 530 Mobile Robotics - <https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public>
