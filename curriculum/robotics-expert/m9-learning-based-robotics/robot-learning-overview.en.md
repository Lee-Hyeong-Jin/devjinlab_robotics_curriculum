---
id: m9-robot-learning-overview
lang: en
title: "Robot learning in outline: from model-based to data-centric"
summary: Compare the model-based pipeline built so far (perception → estimation → planning → control) with learned policies, and map out the data and assumptions that reinforcement learning, imitation learning, and foundation models each rest on. Lay out the rest of M9 and its compute requirements in advance.
objectives:
  - Explain the difference between a model-based robot stack and an end-to-end learned policy in terms of inputs, outputs, and failure modes.
  - Distinguish reinforcement learning, imitation learning, and VLAs (foundation models) by their data source (rewards, demonstrations, large-scale multi-robot data).
  - Choose, with reasons, the learning approach and compute tier that fit a given task (locomotion, picking, language-instructed manipulation).
tags: [robot-learning, reinforcement-learning, imitation-learning, foundation-models, overview, lerobot]
---

# Robot learning in outline: from model-based to data-centric

The robot built across M1-M8 is a chain of human-written models. A camera model (M4) extracts
features, a Kalman filter (M5) estimates position, and A* and DWA (M6) set the path and the
speed. Every part can be interpreted and verified. But on **tasks where models are hard to
write** - folding a towel, plugging in a cable, picking up an object never seen before - the
chain breaks easily. Robot learning is the bundle of methods that fill that gap with data.

## Concepts

### The policy as a common language

Generalize the MDP policy $\pi(s)$ of the previous lesson and the output of a learning-based robot
is a single **policy** $\pi_\theta(a \mid o)$. It takes an observation $o$ (images, joint angles,
a language instruction) and produces an action $a$ (a joint target, an end-effector velocity). It
splits into three branches by what the parameters $\theta$ are fit to.

| Approach | Learning signal | Strengths | Weaknesses |
|---|---|---|---|
| Reinforcement learning (RL) | a reward function | can surpass human behavior without demonstrations | needs so much trial and error that it is mostly trained in simulation |
| Imitation learning (IL) | human demonstrations (teleoperation) | starts from dozens of demonstrations on a real robot | error accumulates in states outside the demonstrations |
| VLA and foundation models | large-scale multi-robot data + language | language instructions, generalization across robots and tasks | large GPUs, and evaluation is hard |

In practice the three are mixed. Locomotion policies are dominated by simulation RL, while
manipulation either does behavior cloning from teleoperated demonstrations (ACT, Diffusion
Policy) or fine-tunes a VLA. Nor does the classical stack disappear. Beneath a learned policy are
still the low-level control and safety limits of M3, and beside it the localization and
navigation of M5 and M6.

### Why "data-centric"

If the bottleneck of model-based methods is "a better model," the bottleneck of learning-based
methods is **the quantity, diversity, and quality of data**. So the latter part of this module
covers data collection (teleoperation), dataset formats (LeRobotDataset, RLDS), and evaluation
protocols as much as algorithms. The "realistic path" of the Interconnects article is ultimately
about lowering the cost of collecting data.

### Compute tiers

The rough guidance collected in the research notes
(`research_notes/.../ai_robot_learning.md`) is as follows.

- **No GPU:** the numpy examples of this module, plus remote resources such as Colab and HF Jobs.
  LeRobot does not recommend CPU training.
- **12-16 GB:** lightweight behavior cloning such as ACT, and Diffusion Policy at small batch sizes.
- **24 GB:** SmolVLA fine-tuning, and inference for π0.5 and GR00T. Full VLA fine-tuning requires
  renting 40-80 GB.

## Key formulas

The probability of a trajectory $\tau = (o_0, a_0, o_1, a_1, \dots)$ and the RL objective:

$$p_\theta(\tau) = p(s_0) \prod_t \pi_\theta(a_t \mid o_t)\, P(s_{t+1} \mid s_t, a_t),\qquad J(\theta) = \mathbb{E}_{\tau \sim p_\theta}\Big[\sum_t \gamma^t r_t\Big]$$

The imitation learning (behavior cloning) objective - maximum likelihood over the demonstration
data $\mathcal{D}$:

$$\theta^* = \arg\max_\theta \sum_{(o, a) \in \mathcal{D}} \log \pi_\theta(a \mid o)$$

The difference between the two is the key point. RL raises expected reward over the distribution
$p_\theta$ **its own policy produces**, while behavior cloning does supervised learning over the
fixed distribution **the expert produced**. That difference leads to the distribution shift
problem of the later lessons.

## Example

Instead of code, practice judgment. For the three tasks below, tabulate the learning signal, the
data source, and the GPU tier required.

1. Velocity tracking on flat ground for a quadruped → rewards are easy to design and the
   simulators are good: **simulation RL**, with an NVIDIA GPU for training.
2. Picking blocks into a box with a low-cost 6-axis arm (SO-101) → around 50 demonstrations:
   **behavior cloning (ACT)**, 12 GB class.
3. A language instruction such as "put the red cup next to the plate" → **VLA fine-tuning**
   (SmolVLA), 24 GB class or a remote GPU.

**Exercise:** Pick a task you care about, build the same table for it, and write three lines on
what you gain and lose compared with solving it with the classical stack (M3-M6).

## Self-check questions

1. Where do you find out that localization has failed in the classical pipeline? Why is it harder to find the cause when an end-to-end policy fails?
2. Over which distribution does each of the RL objective and the behavior cloning objective take its expectation, and why does that difference matter?
3. Give one example of a task where a reward function is hard to write and one where demonstrations are hard to collect, and say which approach you would choose for each.

## How to study this stage

1. **Course (first):** read Units 0-2 of the Hugging Face Robotics Course and work out what
   LeRobot ties together.
2. **Tutorial:** skim only the introduction and the overviews of the RL and behavior cloning
   chapters of *Robot Learning: A Tutorial* (details come in later lessons).
3. **Commentary:** sort out "why data-centric now" from the Interconnects article, and add a line
   of evidence to each row of this lesson's table.
4. **Problems:** take the quiz in the Korean original (`rc quiz m9-robot-learning-overview`) and
   do the exercise.
5. **Check:** write answers to the self-check questions, and revise your table again at the end
   of M9.

## References

- Hugging Face, Robotics Course - <https://huggingface.co/learn/robotics-course>
- Francesco Capuano et al., "Robot Learning: A Tutorial" (arXiv:2510.12403) - <https://arxiv.org/abs/2510.12403>
  (interactive version <https://huggingface.co/spaces/lerobot/robot-learning-tutorial>)
- Nathan Lambert, "A realistic path to robotic foundation models", Interconnects -
  <https://www.interconnects.ai/p/robotic-foundation-models>
- LeRobot Hardware Guide (compute tiers) - <https://huggingface.co/docs/lerobot/main/hardware_guide>
