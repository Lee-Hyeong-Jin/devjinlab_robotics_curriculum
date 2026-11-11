---
id: m5-particle-filter-mcl
lang: en
title: "Particle filters and Monte Carlo localization"
summary: Representing the belief as a set of weighted samples (particles) lets you handle nonlinear and multi-modal distributions. Implement the three steps - sampling, weighting, resampling - and connect them to Monte Carlo localization (MCL) on a map and to ROS 2's AMCL.
objectives:
  - Explain the prediction (sampling), weighting, and resampling steps of a particle filter and implement them in numpy.
  - Explain systematic resampling and the meaning of the effective sample size N_eff.
  - Explain, in comparison with the Kalman filter, why MCL is strong at global localization and the kidnapped robot problem, and what it costs.
tags: [particle-filter, mcl, amcl, resampling, localization]
---

# Particle filters and Monte Carlo localization

The Kalman filter assumes the belief is a single-peaked Gaussian. But when a robot powers up in a
building with two identical corridors, you need a **two-peaked** distribution: "corridor A or
corridor B." A particle filter assumes nothing about the shape of the distribution and instead
simulates hundreds or thousands of hypotheses (particles) directly. Applied to localization on a
map it is Monte Carlo localization (MCL), and Nav2's `nav2_amcl` is an implementation of it.

## Concepts

### The three steps

1. **Prediction (sampling):** move each particle through the motion model, drawing and adding
   noise **separately for each one**. The particle cloud spreads, expressing motion uncertainty.
2. **Weighting:** at each particle's position, compute "the probability of the current
   observation if this were the true pose," $p(z \mid x^{[i]})$, and use it as the weight. This is
   where the sensor model of M4 comes in.
3. **Resampling:** draw particles again in proportion to their weights. Plausible hypotheses are
   duplicated and wrong ones disappear. This is the correction step of the Bayes filter,
   implemented with samples.

### The resampling trap

Resampling at every step drains diversity quickly (**sample impoverishment**). So you resample
only when the weights have become lopsided, and you measure that lopsidedness with the effective
sample size $N_\text{eff}$. Systematic resampling builds evenly spaced pointers from a single
uniform random number, which gives low variance and runs in $O(N)$.

### MCL and AMCL

- **Global localization:** scatter particles over the whole map at the start and the filter
  converges even without knowing the position. That is hard with a Kalman filter.
- **The kidnapped robot problem:** if someone picks the robot up and moves it, every particle is
  wrong. Recover by randomly reinjecting some particles.
- **AMCL:** adaptive MCL, which raises the particle count when uncertain and lowers it once
  converged (KLD sampling). In Nav2 it publishes the `map → odom` transform (see the frame tree in
  the M8 tf2 lesson).

The cost is computation. The number of particles needed grows exponentially with the state
dimension, so particle filters are mostly used on low-dimensional problems such as robot pose
(three dimensions).

## Key formulas

Weights and normalization:

$$w^{[i]} \propto p(z_t \mid x_t^{[i]}),\qquad \sum_i w^{[i]} = 1$$

With several independent range measurements the likelihood is a product:
$p(z \mid x) = \prod_j \mathcal{N}(z_j;\ \lVert x - m_j \rVert,\ \sigma^2)$.

The effective sample size:

$$N_\text{eff} = \frac{1}{\sum_i \left(w^{[i]}\right)^2}$$

A common rule is to resample when $N_\text{eff} < N/2$. The estimate is the weighted mean
$\hat x = \sum_i w^{[i]} x^{[i]}$.

## Example

Four landmarks sit in a 10 m × 10 m space; the robot moves (0.3, 0.2) m per step and measures the
range to each landmark ($\sigma = 0.3$ m). Start with 500 particles spread uniformly over the
whole space (global localization).

```python
import numpy as np

rng = np.random.default_rng(3)
landmarks = np.array([[1.0, 1.0], [9.0, 1.0], [1.0, 9.0], [9.0, 9.0]])
N, sigma_move, sigma_range = 500, 0.1, 0.3

x_true = np.array([2.0, 3.0])
particles = rng.uniform(0, 10, size=(N, 2))  # at the start the position is unknown
weights = np.full(N, 1 / N)


def systematic_resample(weights):
    positions = (rng.random() + np.arange(N)) / N
    return np.searchsorted(np.cumsum(weights), positions).clip(max=N - 1)


for t in range(15):
    u = np.array([0.3, 0.2])
    x_true = x_true + u + rng.normal(0, sigma_move, 2)
    z = np.linalg.norm(landmarks - x_true, axis=1) + rng.normal(0, sigma_range, 4)

    particles += u + rng.normal(0, sigma_move, particles.shape)  # 1) prediction
    pred = np.linalg.norm(particles[:, None, :] - landmarks[None], axis=2)
    weights *= np.exp(-0.5 * np.sum((pred - z) ** 2, axis=1) / sigma_range**2)  # 2) weighting
    weights += 1e-300
    weights /= weights.sum()

    n_eff = 1 / np.sum(weights**2)
    if n_eff < N / 2:  # 3) resample only when needed
        particles = particles[systematic_resample(weights)]
        weights = np.full(N, 1 / N)

    est = weights @ particles
    if t in (0, 1, 4, 14):
        err = np.linalg.norm(est - x_true)
        print(f"t={t:2d} error {err:.2f} m, spread {particles.std(axis=0).mean():.2f} m")
```

At the start the particles cover the whole room (a standard deviation of about 2.9 m), but the
ranges to four landmarks constrain the position strongly, so **one observation and one
resampling** are enough to pull the cloud in to about 0.2 m, with the error down at the
measurement noise level (roughly 0.1-0.2 m). With fewer or symmetric landmarks this convergence
is far slower (exercise 2).

**Exercise:** (1) Set `N` to 50, 500, and 5000 and compare convergence speed against run time.
(2) Leave only one landmark and draw the shape (an arc) the particle cloud takes. (3) Add a
"kidnapping" at step 10 that moves `x_true` far away, and recover from it by randomly reinjecting
5% of the particles every step.

## Self-check questions

1. What goes wrong if you resample unconditionally at every step, and how does $N_\text{eff}$ mitigate it?
2. Explain how EKF and MCL would differ at global localization on a map with two identical corridors.
3. What numerical problem can arise in the example code without `weights += 1e-300`?

## How to study this stage

1. **Video (first):** learn the three steps and the resampling picture from Stachniss's
   "Particle Filter & MCL."
2. **Textbook plus notebook:** run Labbe's Particle Filters chapter, paying particular attention
   to the comparison of resampling schemes.
3. **This lesson plus the example:** run the example and do exercises (1) through (3). Plotting
   the particles as a scatter every step builds intuition fast.
4. **Problems:** take the quiz in the Korean original (`rc quiz m5-particle-filter-mcl`).
5. **Depth (optional):** read MCL and KLD sampling in *Probabilistic Robotics* Ch. 8, and connect
   them to what Nav2's AMCL parameters (`min_particles`, `max_particles`) correspond to.

## References

- Cyrill Stachniss, "Particle Filter & MCL" - <https://www.youtube.com/watch?v=MsYlueVDLI0>
- Roger Labbe, *Kalman and Bayesian Filters in Python*, the Particle Filters chapter -
  <https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python>
- Sebastian Thrun, Wolfram Burgard, Dieter Fox, *Probabilistic Robotics*, MIT Press -
  <https://robots.stanford.edu/probabilistic-robotics/>
- University of Michigan, ROB 530 Mobile Robotics - <https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public>
