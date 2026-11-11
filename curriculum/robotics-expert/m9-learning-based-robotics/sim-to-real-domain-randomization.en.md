---
id: m9-sim-to-real-domain-randomization
lang: en
title: "Simulation-based RL and sim-to-real (domain randomization)"
summary: Read the causes of the reality gap that appears when locomotion and manipulation policies trained by reinforcement learning in GPU-parallel simulators move to real robots, and the countermeasures - system identification, domain randomization, sim2sim validation. A small numpy example compares the real-world performance of a policy overfitted to the nominal simulator against one trained with randomization.
objectives:
  - Explain why GPU-parallel simulation became the standard workflow of PPO-based robot RL, and describe that flow (training → sim2sim → hardware).
  - Distinguish the main causes of the reality gap (dynamics parameters, actuator delay and limits, sensor noise, visual differences) and choose a countermeasure for each.
  - Formalize domain randomization as "optimizing expected performance over a distribution of parameters" and explain the trade-off between robustness and nominal performance with an example.
tags: [sim-to-real, domain-randomization, reality-gap, gpu-simulation, locomotion, system-identification]
---

# Simulation-based RL and sim-to-real (domain randomization)

The previous lesson said PPO has poor sample efficiency. You cannot collect hundreds of millions
of steps on a real quadruped, so locomotion policies are, almost without exception, **trained in
a simulator and transferred to the real robot (sim-to-real)**. This lesson covers that workflow
and the reasons performance collapses in the transfer. Simulator practice is outside this
platform's scope, so documentation reading and a numpy model stand in for it.

## Concepts

### The GPU-parallel simulation workflow

Isaac Lab, MuJoCo Playground, and mjlab simulate thousands of robots at once on a single GPU. The
typical flow is (1) train a task with defined observations, actions, and rewards (velocity
command tracking, say) with PPO, → (2) export the policy to ONNX and **re-validate it in a
different simulator (sim2sim)**, → (3) deploy on hardware. unitree_rl_mjlab recommends running in
`unitree_mujoco` first after training. A policy that survives a different physics engine is more
likely to survive reality.

### Causes of the reality gap

- **Dynamics:** mass, inertia, friction, and contact models differ.
- **Actuators:** motor delay, torque limits, gear backlash. Large enough that the NVIDIA SO-101
  course devotes a separate "Actuation Gap" module to it.
- **Sensors:** the noise, bias, and delay seen in M4, plus differences in camera exposure and texture.
- **Control period:** the simulator runs at exactly 50 Hz while hardware jitters.

### Countermeasures

- **System identification:** fit the simulator's parameters from hardware data. The direct way to
  narrow the gap.
- **Domain randomization:** instead of fitting parameters to a single value, draw them from a wide
  distribution each episode during training. The policy learns behavior that "works in any world,"
  and the hope is that reality is one sample from that distribution. Visual randomization varies
  lighting, textures, and camera placement.
- **Observation design:** put delay and noise into the simulation, and feed in a few steps of past
  observations so the policy can estimate the hidden parameters.
- **Mixing real data:** train on simulation data with a small amount of real demonstrations mixed in
  (co-training).

## Key formulas

Optimization against the nominal simulator parameters $\xi_0$, and the domain randomization
objective:

$$\theta_\text{nom} = \arg\max_\theta J(\theta; \xi_0),\qquad \theta_\text{DR} = \arg\max_\theta \mathbb{E}_{\xi \sim p(\xi)}\big[J(\theta; \xi)\big]$$

If the real parameters $\xi_\text{real}$ lie within the support of $p(\xi)$, then
$\theta_\text{DR}$ is robust. If the distribution is too wide, the policy turns conservative
preparing for every world and loses nominal performance.

## Example

A single joint driven to 0 by a PD policy, with "training" replaced by a grid search over the
gains. The real robot differs from the simulator in mass, delay, and friction.

```python
import numpy as np

# A 1-DOF joint driven to position 0 by the PD policy u = -kp*x - kd*v.
# "Training" = a grid search over kp, kd.
DT, STEPS = 0.01, 300
rng = np.random.default_rng(0)


def cost(kp, kd, mass, delay, friction):
    x, v = 1.0, 0.0
    buf = [0.0] * delay  # actuator delay: the command issued `delay` steps ago applies now
    total = 0.0
    for _ in range(STEPS):
        buf.append(float(np.clip(-kp * x - kd * v, -200, 200)))  # torque limit
        u = buf.pop(0)
        v += DT * (u - friction * v) / mass
        x += DT * v
        total += DT * (x**2 + 1e-6 * u**2)
        if abs(x) > 10:
            return 1e3  # diverged
    return total


GAINS = [(kp, kd) for kp in (10, 30, 100, 300, 1000) for kd in (1, 3, 10, 30)]


def train(params_list):
    scores = [np.mean([cost(kp, kd, *p) for p in params_list]) for kp, kd in GAINS]
    return GAINS[int(np.argmin(scores))]


nominal = [(1.0, 0, 0.1)]  # simulator defaults: mass 1 kg, no delay, friction 0.1
randomized = [
    (rng.uniform(0.5, 2.0), int(rng.integers(0, 6)), rng.uniform(0.0, 1.0)) for _ in range(30)
]
real = (1.6, 4, 0.6)  # the "real robot": heavier, 40 ms delay, more friction (unknown at training)

for name, params in [("nominal sim", nominal), ("domain randomization", randomized)]:
    kp, kd = train(params)
    sim, real_cost = cost(kp, kd, *nominal[0]), cost(kp, kd, *real)
    print(f"{name}: kp={kp}, kd={kd} | sim cost {sim:.3f}, real cost {real_cost:.3f}")
```

Output:

```text
nominal sim: kp=1000, kd=30 | sim cost 0.052, real cost 11.287
domain randomization: kp=100, kd=10 | sim cost 0.088, real cost 0.169
```

The high gains chosen on the nominal simulator are the fastest inside that simulator, but on
hardware with 40 ms of delay they oscillate between the torque limits. The gains chosen under
randomization are a little slower in the simulator and stable on hardware.

**Exercise:** (1) Fix only the delay at 0 in the randomization ranges and see what happens. Which
cause of the gap was decisive? (2) Widen the mass range to 0.1-10 kg and measure how much
excessive randomization costs in performance. (3) Draw several values of `real` and compare the
failure rates of the two policies.

## Self-check questions

1. Give one problem sim2sim validation can catch before hardware deployment, and one it cannot.
2. Are system identification and domain randomization substitutes or complements? Propose an order for using both.
3. Explain with the objective above why nominal performance falls as the randomization distribution widens.

## How to study this stage

1. **Documentation (first):** read NVIDIA's "Robot Learning Fundamentals," marking where the task,
   reward, and randomization settings live, then continue with the 08 Simulation to Reality and
   Visual Domain Randomization units.
2. **This lesson plus the example:** build the habit of finding which gap is decisive, through the
   example and exercise (1).
3. **Code reading:** list the reward terms and randomization entries in the velocity-tracking task
   of unitree_rl_mjlab.
4. **Problems:** take the quiz in the Korean original
   (`rc quiz m9-sim-to-real-domain-randomization`).
5. **Extending (optional, GPU needed):** run MuJoCo Playground CartpoleBalance on CPU, then read
   the SO-101 sim-to-real course.

## References

- NVIDIA Physical AI Learning, "Robot Learning Fundamentals" -
  <https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-lab/latest/robot-learning-fundamentals/index.html>
- NVIDIA Physical AI Learning, "Visual Domain Randomization" -
  <https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-lab/latest/transfer-policies-from-simulation-to-reality/03-bridging-the-gap-simulation-enhancement/01-visual-domain-randomization.html>
- MuJoCo Playground - <https://playground.mujoco.org/>
- Unitree Robotics, unitree_rl_mjlab - <https://github.com/unitreerobotics/unitree_rl_mjlab>
- NVIDIA Physical AI Learning, "Sim-to-Real with SO-101" -
  <https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/index.html>
- Josh Tobin et al., "Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World" (IROS 2017)
