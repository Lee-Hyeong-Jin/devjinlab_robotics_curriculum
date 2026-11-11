---
id: m5-bayes-filter
lang: en
title: "Probability and the Bayes filter"
summary: Represent a robot's state not as a single value but as a probability distribution (the belief), and implement the two steps of the Bayes filter - predicting with a motion model and correcting with an observation model - as a discrete histogram filter. Every filter in M5 shares this structure.
objectives:
  - Explain prior, likelihood, and posterior probabilities and Bayes' theorem by mapping them onto the robot localization problem.
  - Write the prediction and correction steps of the Bayes filter in equations and in code.
  - Implement a histogram filter on a one-dimensional grid world and explain how motion and observation noise affect the belief.
tags: [probability, bayes-filter, histogram-filter, markov-localization, state-estimation]
---

# Probability and the Bayes filter

M3 obtained position by integrating wheel encoders, and M4 showed that every sensor carries
noise. Put the two together and the problem is clear: a robot **cannot know its position
exactly**. So state estimation deals in distributions - "here is the probability the robot is at
each position" - rather than "the robot is at (2.0, 1.5)." That distribution is called the
**belief** $bel(x_t)$, and the rule that updates it on every motion and every observation is the
Bayes filter. The Kalman filter, the particle filter, and SLAM are all special implementations of
this framework.

## Concepts

### Prior, likelihood, and posterior

- **Prior** $p(x)$: the belief before observing. A uniform distribution if you know nothing at the start.
- **Likelihood** $p(z \mid x)$: the probability of observing $z$ when the robot is at $x$. This is
  exactly the sensor model of M4.
- **Posterior** $p(x \mid z)$: the belief with the observation folded in.

Bayes' theorem says the posterior is proportional to likelihood × prior. The denominator $p(z)$
does not depend on $x$, so you can treat it as a normalizing constant $\eta$. In code it is the
one line that multiplies and then divides by the sum.

### The Markov assumption

Assume the current state $x_t$ summarizes all past information: the next state depends only on
$x_{t-1}$ and the control $u_t$, and the observation $z_t$ only on $x_t$. That is what lets you
keep just the previous belief and update recursively instead of storing the whole history. The
assumption breaks when wheel slip accumulates or a person walks past and produces measurements
that disagree with the map; practical filters absorb this by inflating the noise a little.

### The two steps

1. **Prediction:** push the belief through the motion model with the control $u_t$ ("move forward
   one cell," say). Because motion is noisy, the distribution **spreads out** (uncertainty grows).
2. **Correction:** multiply by the likelihood of the observation $z_t$ and normalize. Positions
   that agree with the observation gain probability and the distribution **narrows**
   (uncertainty shrinks).

Dividing the state space into a grid and storing the probabilities as an array gives the
**histogram (discrete Bayes) filter**; applied to localization, it is **Markov localization**.
Computation explodes as the grid grows, so the next lessons approximate the distribution with a
Gaussian (Kalman) or with samples (particles).

## Key formulas

Bayes' theorem:

$$p(x \mid z) = \frac{p(z \mid x)\,p(x)}{p(z)} = \eta\,p(z \mid x)\,p(x)$$

The Bayes filter (prediction → correction):

$$\overline{bel}(x_t) = \sum_{x_{t-1}} p(x_t \mid u_t, x_{t-1})\,bel(x_{t-1})$$

$$bel(x_t) = \eta\,p(z_t \mid x_t)\,\overline{bel}(x_t)$$

In a continuous state space the sum becomes an integral. The prediction step is the
**convolution** of the belief with the motion noise kernel.

## Example

A circular corridor of ten cells has three doors. The robot has a "door / no door" sensor (75%
accurate) and moves one cell at a time (80% accurate, 10% short, 10% far).

```python
import numpy as np

world = np.array([1, 1, 0, 0, 0, 0, 0, 0, 1, 0])  # 1 = door, 0 = wall
belief = np.full(10, 0.1)  # at the start the position is unknown (uniform)


def predict(belief, move, p_exact=0.8, p_under=0.1, p_over=0.1):
    """Motion model: move `move` cells, possibly one short or one far (circular corridor)."""
    return (
        p_exact * np.roll(belief, move)
        + p_under * np.roll(belief, move - 1)
        + p_over * np.roll(belief, move + 1)
    )


def update(belief, z, p_hit=0.75):
    """Observation model: the door sensor reads correctly with probability p_hit."""
    likelihood = np.where(world == z, p_hit, 1 - p_hit)
    posterior = likelihood * belief
    return posterior / posterior.sum()  # the normalizing constant eta


for step, (move, z) in enumerate([(0, 1), (1, 1), (1, 0), (1, 0), (1, 0)]):
    belief = update(predict(belief, move), z)
    print(step, np.round(belief, 2), "most likely cell:", belief.argmax())
```

Right after the first observation, the three cells in front of doors (0, 1, 8) have similar
probabilities. Once the pattern "door → door → wall → wall → wall" plays out, cell 0 is the only
starting point consistent with it, so the probability mass gathers near cell 4. A single
observation is ambiguous, but **the sequence of motions and observations** removes the ambiguity -
that is the point.

**Exercise:** (1) Change `p_hit` to 0.55 and 0.95 and compare how fast the filter converges.
(2) Repeat `predict` ten times with no observations and confirm that the belief spreads back out
to uniform. (3) Build a simulation that actually moves the robot (a true position plus a noisy
sensor) and plot whether the filter's most likely cell tracks the truth.

## Self-check questions

1. Explain why the belief widens in the prediction step and narrows in the correction step.
2. What goes wrong in a histogram filter if you skip the normalizing constant $\eta$?
3. How many state cells does a 2 m × 2 m room have at 1 cm grid and 1° heading resolution? How does that connect to the need for Kalman and particle filters?

## How to study this stage

1. **Video (first):** get the whole picture from Stachniss's "Bayes Filter" lecture. If your
   probability basics feel shaky, watch the Probability Primer in the Basics block first.
2. **Textbook plus notebook:** run Labbe Ch. 2 in Jupyter and compare it with the example here.
3. **This lesson plus the example:** run the example and do exercises (1) through (3).
4. **Problems:** take the quiz in the Korean original (`rc quiz m5-bayes-filter`), and work its
   Bayes' theorem calculation (prior and likelihood → posterior) by hand once.
5. **Depth (optional):** follow the derivation of the Bayes filter in *Probabilistic Robotics* Ch. 2.

## References

- Roger Labbe, *Kalman and Bayesian Filters in Python*, Ch. 2 Discrete Bayes -
  <https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python>
- Cyrill Stachniss, "Bayes Filter" - <https://www.youtube.com/watch?v=0lKHFJpaZvE>
- Cyrill Stachniss, Online Training - Mobile Robotics - <https://www.ipb.uni-bonn.de/online-training-robotics/>
- Sebastian Thrun, Wolfram Burgard, Dieter Fox, *Probabilistic Robotics*, MIT Press -
  <https://robots.stanford.edu/probabilistic-robotics/>
