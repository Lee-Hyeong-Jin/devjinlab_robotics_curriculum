---
id: m9-datasets-benchmarks-evaluation
lang: en
title: "The LeRobot ecosystem, datasets, benchmarks, and safe evaluation"
summary: Centered on LeRobot, cover how robot learning data is recorded and shared (LeRobotDataset, RLDS, Open X-Embodiment, DROID), which benchmarks policies are compared on (LIBERO, MetaWorld), and how to report success rates honestly from few trials and evaluate safely on hardware. Compute success rate confidence intervals and a permutation test in numpy.
objectives:
  - Explain LeRobot's components (datasets, policies, robot drivers, evaluation), the LeRobotDataset and RLDS formats, and the scale and licensing caveats of the major datasets.
  - Explain the difference in role between simulation benchmarks and hardware evaluation, and design an evaluation protocol (initial conditions, number of trials, success criteria).
  - Compute a Wilson confidence interval for a success rate and a permutation test to judge whether the difference between two policies is meaningful, and list the safety measures for hardware evaluation.
tags: [lerobot, datasets, benchmarks, evaluation, open-x-embodiment, safety]
---

# The LeRobot ecosystem, datasets, benchmarks, and safe evaluation

The ability of a learning-based robot comes from data, and evaluation is what says whether that
ability is real. Closing out M9, this lesson covers **how to record data, how to compare
policies, and how to report results honestly**. The imitation learning track of the M10 capstone
uses this procedure directly.

## Concepts

### The LeRobot ecosystem

Hugging Face LeRobot bundles, behind a single `pip install lerobot`, (1) teleoperation recording
and a dataset format, (2) policy implementations including ACT, Diffusion, SmolVLA, and the π0
family, (3) motor configuration and calibration CLIs for low-cost arms such as the SO-101, and
(4) LIBERO and MetaWorld simulation evaluation. The installation and training interfaces change
often between releases, so this curriculum pins a version (v0.7.0 as surveyed).

### Dataset formats and the major datasets

- **LeRobotDataset:** stores per-episode joint states and actions in tabular form and cameras as
  video, shared and streamed from the Hugging Face Hub. You can visualize recorded data directly
  in the browser to weed out bad episodes.
- **RLDS:** a format based on TensorFlow Datasets. Open X-Embodiment (1M+ trajectories, 22 robots)
  and DROID started in this format. Mirrored subsets in the LeRobot format also exist.
- **Licensing:** OXE's sub-datasets carry different licenses (from commercially usable CC-BY to
  non-commercial only). Using them in a product means checking at the sub-dataset level.

### Benchmarks and hardware evaluation

Simulation benchmarks (LIBERO, MetaWorld) can reproduce the same initial conditions hundreds of
times, which makes them good for **comparing algorithms**. They are not a substitute for hardware
performance. Hardware evaluation is expensive per trial and usually stops at a few dozen runs, so
the **protocol** matters. Fix the initial object placements in advance and use the same ones for
both policies, write down the success criteria and the time limit beforehand, and record the
failure modes (missed grasp, dropped, collision). A report that gives only "80% success rate,"
with no trial count and no confidence interval, is not grounds for comparison.

### Safety

A learned policy behaves unpredictably outside its training distribution. Before hardware
evaluation, (1) enforce joint, velocity, and torque limits in a low-level controller outside the
policy, (2) keep an emergency stop within reach, (3) put a virtual boundary around the workspace,
(4) run at a low speed scaling at first, and (5) have people observe from outside the workspace.
Safety is the responsibility of the system wrapped around the policy, not of the policy.

## Key formulas

With $k$ successes out of $n$ trials, $\hat p = k/n$, and $z = 1.96$, the 95% Wilson confidence
interval:

$$\frac{\hat p + \frac{z^2}{2n}}{1 + \frac{z^2}{n}} \pm \frac{z}{1 + \frac{z^2}{n}} \sqrt{\frac{\hat p (1 - \hat p)}{n} + \frac{z^2}{4n^2}}$$

The interval width shrinks roughly as $1/\sqrt{n}$. Halving the width takes four times the trials.

## Example

Suppose policies A and B were each evaluated 20 times, and then 200 times.

```python
import numpy as np


def wilson(successes, n, z=1.96):
    """95% Wilson confidence interval for a success rate. Stable at small n and near 0% or 100%."""
    p = successes / n
    center = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return center - half, center + half


for name, k, n in [
    ("policy A", 16, 20),
    ("policy B", 13, 20),
    ("policy A", 160, 200),
    ("policy B", 130, 200),
]:
    lo, hi = wilson(k, n)
    print(f"{name} {k:3d}/{n:3d} = {k / n:.0%}  95% CI [{lo:.0%}, {hi:.0%}]")

# permutation test: if the two policies' true success rates were equal, how often would
# 20 trials each differ by 3 or more?
rng = np.random.default_rng(0)
pooled = np.array([1] * (16 + 13) + [0] * (40 - 29))
diffs = []
for _ in range(20000):
    rng.shuffle(pooled)
    diffs.append(pooled[:20].sum() - pooled[20:].sum())
print(f"p-value of the 20-trial comparison ~ {np.mean(np.abs(diffs) >= 3):.2f}")
```

Output:

```text
policy A  16/ 20 = 80%  95% CI [58%, 92%]
policy B  13/ 20 = 65%  95% CI [43%, 82%]
policy A 160/200 = 80%  95% CI [74%, 85%]
policy B 130/200 = 65%  95% CI [58%, 71%]
p-value of the 20-trial comparison ~ 0.48
```

At 20 trials each, the confidence intervals of 80% and 65% overlap heavily and the permutation
test gives p = 0.48. There are no grounds to say "A is better." At the same success rates but 200
trials each, the intervals separate. Hardware trials are expensive, which is why candidates are
narrowed down on simulation benchmarks and hardware is saved for the final comparison.

**Exercise:** (1) With true success rates of 80% and 65%, find by simulation roughly how many
trials each it takes for the permutation test to detect the difference at the 5% level.
(2) Assuming your own M10 task, write a one-page evaluation plan listing 10 initial conditions,
the success criteria, the time limit, and the safety measures.

## Self-check questions

1. Explain, connecting it to the reality gap of the previous lesson, why a policy with a high simulation benchmark score can score low on hardware.
2. If you succeed 20 out of 20 trials, may you report a "100% success rate"? Roughly what is the lower bound of the Wilson interval?
3. Why must the safety of a learned policy be guaranteed by the surrounding system rather than by the policy itself?

## How to study this stage

1. **Documentation (first):** open one public dataset on the Hub with the LeRobot README and the
   dataset visualization tool and inspect the episode structure.
2. **This lesson plus the example:** run the example and get a feel for "how many trials are
   needed" through exercise (1).
3. **Reading the data:** check the embodiment and task composition and the licensing notes on the
   Open X-Embodiment site.
4. **Problems:** take the quiz in the Korean original
   (`rc quiz m9-datasets-benchmarks-evaluation`).
5. **Survey:** read the evaluation protocol section of the dataset and benchmark survey
   (2604.23001) and revise your own evaluation plan.

## References

- Hugging Face, LeRobot - <https://github.com/huggingface/lerobot>
- Open X-Embodiment Collaboration, Open X-Embodiment - <https://robotics-transformer-x.github.io/>
- "Vision-Language-Action in Robotics: A Survey of Datasets, Benchmarks, and Data Engines" - <https://arxiv.org/html/2604.23001>
- NVIDIA Physical AI Learning, "Sim-to-Real with SO-101" -
  <https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/index.html>
- DROID collaboration, DROID (Distributed Robot Interaction Dataset) - <https://droid-dataset.github.io>
