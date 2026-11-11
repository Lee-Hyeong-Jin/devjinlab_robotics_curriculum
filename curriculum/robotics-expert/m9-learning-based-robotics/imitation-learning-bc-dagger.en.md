---
id: m9-imitation-learning-bc-dagger
lang: en
title: "Imitation learning: behavior cloning, DAgger, ACT, and Diffusion Policy"
summary: Cover behavior cloning (BC), which supervises a policy from human demonstrations, the distribution shift problem that accumulates error in states outside the demonstrations, and DAgger, which fixes it by collecting data. Reproduce BC's failure and DAgger's recovery in a small numpy example, then read the ideas behind the practical policy families ACT and Diffusion Policy along with tips for collecting teleoperation data.
objectives:
  - Formalize behavior cloning as a supervised learning problem and regress a policy from demonstration data.
  - Explain why error accumulates through distribution (covariate) shift and implement DAgger's data aggregation procedure.
  - Explain which weakness of BC each of ACT's action chunks and Diffusion Policy's multimodal action representation addresses.
tags: [imitation-learning, behavior-cloning, dagger, act, diffusion-policy, teleoperation]
---

# Imitation learning: behavior cloning, DAgger, ACT, and Diffusion Policy

You cannot run millions of trials on a real robot arm. So in manipulation the starting point is
**imitation learning**: a person drives the robot with a leader arm or in VR (teleoperation) to
collect **demonstrations**, and the policy imitates them.

## Concepts

### Behavior cloning (BC)

Treat the demonstrations $\mathcal{D} = \{(o_i, a_i)\}$ as input-label pairs and do regression or
classification. No reward is needed, and it works from a few dozen demonstrations. The problem is
that **the state distribution differs between training and execution**. The training data covers
only states the expert visited; at execution, a small mistake by the policy takes the robot into
states the expert never visited, where the mistakes grow. This is **distribution (covariate)
shift**, or compounding error.

### DAgger: fixing distribution shift with data

DAgger (Dataset Aggregation) (1) rolls the robot out under the current learner policy to collect
states, (2) has the expert label those states with the correct actions, and (3) merges them into
the existing data and retrains. A few iterations later the training distribution covers the
learner's own visitation distribution. The price is that the expert must supply answers while the
learner drives, so in practice it is adapted into forms where a person intervenes only when
things get dangerous (HIL).

### Practical policy families

- **ACT (Action Chunking with Transformers):** predicts a $k$-step **action chunk** rather than
  one action at a time. The number of decisions drops by a factor of $k$, reducing compounding
  error. By LeRobot's measure it is a light policy at 2-6 GB of VRAM.
- **Diffusion Policy:** when a person goes left in one demonstration and right in another from
  the same situation, mean squared error regression produces the **average** of the two (straight
  into the obstacle). Representing the action distribution itself with a diffusion model handles
  that multimodality (8-14 GB).

### Tips for collecting data

Keep the strategy consistent and the object positions and lighting varied, and deliberately
include some recovery maneuvers from near-failures (a hand-made DAgger effect). Camera placement
and calibration (M4) must be the same at training and deployment.

## Key formulas

Behavior cloning (equivalent to mean squared error for a Gaussian policy):

$$\hat\theta = \arg\min_\theta \sum_{(o, a) \in \mathcal{D}} \lVert \pi_\theta(o) - a \rVert^2$$

Compounding error: when the probability of a mistake per step is $\epsilon$, the cost increase of
BC over an episode of length $T$ is $O(\epsilon T^2)$ in the worst case, against $O(\epsilon T)$
for DAgger (Ross et al., 2011).

The DAgger iteration ($d_{\pi_i}$ is the state visitation distribution of the learner policy
$\pi_i$):

$$\mathcal{D} \leftarrow \mathcal{D} \cup \{(s, \pi^*(s)) : s \sim d_{\pi_i}\},\qquad \pi_{i+1} = \text{BC}(\mathcal{D})$$

## Example

One-dimensional lane keeping. The demonstrations were collected only near the center, while the
test starts off-center. The policy is ridge regression over RBF features.

```python
import numpy as np

# 1D lane keeping: x = lateral error from the lane center [m]. A crosswind DRIFT keeps
# pushing toward +x.
DT, DRIFT, T = 0.1, 0.5, 100
CENTERS = np.linspace(-3, 3, 25)  # centers of the RBF features
rng = np.random.default_rng(0)


def expert(x):
    return -2.0 * x - DRIFT  # the expert (a human driver) cancels the wind and returns to center


def features(x):
    return np.exp(-((np.atleast_1d(x)[:, None] - CENTERS) ** 2) / (2 * 0.25**2))


def fit(X, U, lam=1e-3):  # behavior cloning = supervised learning (ridge regression)
    F = features(X)
    return np.linalg.solve(F.T @ F + lam * np.eye(len(CENTERS)), F.T @ U)


def learner(w):
    return lambda x: (features(x) @ w)[0]


def rollout(policy, x0):
    xs, x = [], x0
    for _ in range(T):
        xs.append(x)
        x = float(np.clip(x + DT * (policy(x) + DRIFT) + rng.normal(0, 0.05), -3, 3))
    return np.array(xs)


starts = [-1.5, 1.0, 1.5]  # test: start away from the center


def report(name, policy):
    err = np.mean([np.abs(rollout(policy, x0)).mean() for x0 in starts for _ in range(5)])
    print(f"{name:9s} mean |x| = {err:.2f} m")


# 1) ten expert demonstrations, all starting near the lane center
X = np.concatenate([rollout(expert, rng.normal(0, 0.05)) for _ in range(10)])
U = expert(X)
w = fit(X, U)
print(f"demonstration data range x in [{X.min():+.2f}, {X.max():+.2f}]")
report("expert", expert)
report("BC", learner(w))

# 2) DAgger: the expert labels the states the learner itself drove through, merged into the data
for it in range(1, 4):
    Xn = np.concatenate([rollout(learner(w), x0) for x0 in starts])
    X, U = np.concatenate([X, Xn]), np.concatenate([U, expert(Xn)])
    w = fit(X, U)
    report(f"DAgger {it}", learner(w))
```

Output:

```text
demonstration data range x in [-0.29, +0.27]
expert    mean |x| = 0.12 m
BC        mean |x| = 1.54 m
DAgger 1  mean |x| = 0.12 m
DAgger 2  mean |x| = 0.12 m
DAgger 3  mean |x| = 0.13 m
```

The BC policy outputs nearly zero outside the demonstration range $|x| < 0.3$ and gets blown
away. DAgger labels the states the learner actually visited and recovers expert-level performance
after a single aggregation.

**Exercise:** (1) Collect demonstrations from varied starting points (±2 m) and check whether BC
succeeds without DAgger. (2) Add noise of standard deviation 0.3 to the expert's actions to mimic
the wobble of human demonstrations, and compare BC against DAgger.

## Self-check questions

1. Why do the generalization guarantees of supervised learning not carry over to behavior cloning, even though it is supervised learning?
2. Why is DAgger's expert query cost a problem on real robots, and how do human-intervention variants reduce it?
3. What does mean squared error BC output when demonstrations avoiding an obstacle to the left and to the right are mixed? How does Diffusion Policy handle it differently?

## How to study this stage

1. **Textbook (first):** get the theory of BC, distribution shift, and DAgger from Tedrake's
   *Underactuated Robotics* Ch. 21.
2. **This lesson plus the example:** run the example and confirm through exercise (1) that "data
   diversity" and "DAgger" are two ways of solving the same problem.
3. **Problems:** take the quiz in the Korean original (`rc quiz m9-imitation-learning-bc-dagger`).
4. **Lectures and assignments:** watch the imitation learning lecture of CS 285 and attempt HW1.
5. **Practical reading:** read LeRobot's ACT policy code and "How I trained ACT on SO-101," and
   note the practical feel for the number of demonstrations, the cameras, and the training time.

## References

- Russ Tedrake, *Underactuated Robotics*, Ch. 21 - <https://underactuated.mit.edu/>
- Hugging Face, LeRobot - <https://github.com/huggingface/lerobot>
- Sherry Chen, "How I trained Action Chunking Transformer (ACT) on SO-101" (HF blog mirror) -
  <https://www.plushcap.com/content/huggingface/blog/huggingface-how-i-trained-action-chunking-transformer-act-on-so-101-my-journey-gotchas-and-lessons>
- Stéphane Ross, Geoffrey Gordon, J. Andrew Bagnell, "A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning" (AISTATS 2011, DAgger)
- Tony Z. Zhao et al., "Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware" (2023, ACT)
- Cheng Chi et al., "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion" (2023)
