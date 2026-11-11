---
id: m9-reinforcement-learning-basics
lang: en
title: "Reinforcement learning basics (Q-learning, policy gradients, PPO in outline)"
summary: Sort reinforcement learning - solving an MDP from experience alone without knowing the transition probabilities - into value-based (TD, Q-learning) and policy-based (REINFORCE, actor-critic, PPO) methods. Solve the grid world of the previous lesson with tabular Q-learning and compare it against the value iteration result.
objectives:
  - Explain the difference between model-based planning (value iteration) and model-free reinforcement learning, and write the TD error and the Q-learning update.
  - Implement tabular Q-learning with epsilon-greedy exploration and diagnose how insufficient exploration affects the learned policy.
  - Explain which problem each of the policy gradient theorem, baselines and advantages, and PPO's clipped objective solves.
tags: [reinforcement-learning, q-learning, td-learning, policy-gradient, actor-critic, ppo]
---

# Reinforcement learning basics (Q-learning, policy gradients, PPO in outline)

The value iteration of the previous lesson knew the transition probabilities
$P(s' \mid s, a)$. A real robot does not hand you that table. What it can do is act and observe
the result. **Reinforcement learning (RL)** approximates and solves the Bellman equations from
that experience alone. It is strong on problems like locomotion policies, where rewards are
writable but an accurate dynamics model is not.

## Concepts

### Value-based: TD learning and Q-learning

Replace the expectation $\sum_{s'} P(\cdot)[\dots]$ of value iteration with **a single sample**
and you get TD (temporal difference) learning. Keep the action value $Q(s, a)$ in a table and, on
each one-step experience $(s, a, r, s')$, move it a little toward the target
$r + \gamma \max_{a'} Q(s', a')$. That is **Q-learning**. Actions are chosen at random with
probability $\varepsilon$ and as $\arg\max_a Q$ otherwise (epsilon-greedy). You need exploration
to learn the value of unknown cells, and exploitation to collect reward.

When the state is high-dimensional, a neural network $Q_\phi$ replaces the table (DQN), and with
continuous actions the $\max_a$ becomes hard, so actor-critic methods such as SAC are used.

### Policy-based: policy gradients and actor-critic

Parameterize the policy $\pi_\theta(a \mid s)$ directly and raise the expected reward $J(\theta)$
by gradient ascent. The policy gradient theorem is the equation form of "increase the probability
of the actions in trajectories that went well" (REINFORCE). Its variance is enormous, so two
devices are added.

- **Baseline:** subtract the state value $V(s)$ from the reward sum and use the advantage
  $A = Q - V$. The expectation is unchanged, the variance drops.
- **Actor-critic:** a critic that separately learns $V_\phi$ estimates the advantage, and the
  actor updates the policy.

### PPO: the default of robot RL

A policy gradient that steps too far at once destroys the policy. **PPO (Proximal Policy
Optimization)** clips the probability ratio $\rho_t$ between the new and old policies into
$[1-\epsilon, 1+\epsilon]$, so it can update several times safely from one batch. It is simple to
implement and fits parallel simulation well, so the locomotion examples of Isaac Lab and MuJoCo
Playground (RSL-RL and others) use it by default. Being on-policy, however, its sample efficiency
is low, which is why thousands of environments run at once on a GPU simulator.

## Key formulas

The Q-learning update (TD error $\delta$):

$$\delta = r + \gamma \max_{a'} Q(s', a') - Q(s, a),\qquad Q(s, a) \leftarrow Q(s, a) + \alpha\,\delta$$

The policy gradient theorem (advantage form):

$$\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta}\big[\nabla_\theta \log \pi_\theta(a_t \mid s_t)\, A(s_t, a_t)\big]$$

The PPO clipped objective:

$$L^{\text{CLIP}}(\theta) = \mathbb{E}_t\Big[\min\big(\rho_t A_t,\ \operatorname{clip}(\rho_t, 1-\epsilon, 1+\epsilon) A_t\big)\Big],\qquad \rho_t = \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_\text{old}}(a_t \mid s_t)}$$

## Example

Solve the same grid world as the previous lesson with Q-learning, experiencing it only through a
`step()` function. The start cell is the bottom left, (3, 0).

```python
import numpy as np

# the same 4 x 4 grid as m9-mdp-decision-making. This time the transition probabilities are
# unknown and experienced only through step().
LAYOUT = ["...G", ".#.P", "....", "...."]
MOVES = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # ↑ → ↓ ←
NAMES = "↑→↓←"
GAMMA, ALPHA, STEP_COST = 0.95, 0.1, -0.04
rng = np.random.default_rng(0)


def step(s, a):
    a = rng.choice([a, (a - 1) % 4, (a + 1) % 4], p=[0.8, 0.1, 0.1])  # slip
    r, c = s[0] + MOVES[a][0], s[1] + MOVES[a][1]
    if not (0 <= r < 4 and 0 <= c < 4) or LAYOUT[r][c] == "#":
        r, c = s
    cell = LAYOUT[r][c]
    if cell == "G":
        return (r, c), 1.0, True
    if cell == "P":
        return (r, c), -1.0, True
    return (r, c), STEP_COST, False


Q = np.zeros((4, 4, 4))  # Q[row, column, action]
for episode in range(20000):
    eps = max(0.05, 1.0 - episode / 10000)  # epsilon-greedy: taper the exploration rate
    s, done = (3, 0), False
    while not done:
        a = rng.integers(4) if rng.random() < eps else int(Q[s].argmax())
        s2, reward, done = step(s, a)
        target = reward if done else reward + GAMMA * Q[s2].max()  # TD target
        Q[s][a] += ALPHA * (target - Q[s][a])  # move by the TD error
        s = s2

for r in range(4):
    cells = []
    for c in range(4):
        if LAYOUT[r][c] in "#GP":
            cells.append(f"  {LAYOUT[r][c] * (2 if LAYOUT[r][c] == '#' else 1):4s}")
        else:
            cells.append(f"{NAMES[Q[r, c].argmax()]}{Q[r, c].max():+.2f}")
    print(" ".join(cells))
```

Output:

```text
→+0.76 →+0.86 →+0.96   G
↑+0.66   ##   ↑+0.78   P
↑+0.56 ←+0.45 ←+0.35 ↓+0.23
↑+0.44 ←+0.39 ←+0.29 ←+0.25
```

The policy along the left column and the top row, from the start cell to the goal, matches value
iteration. But (2, 2) comes out as ←, 0.35, unlike value iteration's answer (↑, 0.52). Once
exploration tapered off, that cell was almost never visited, so its Q values are
under-trained. Some cells end up with values slightly higher than value iteration's because of
the **overestimation bias** of a fixed learning rate combined with the $\max$ operation.

**Exercise:** (1) Count visits per cell and confirm how rarely (2, 2) is updated. (2) Randomize
the start cell each episode (exploring starts) and see whether the policy then matches value
iteration. (3) Decay $\alpha$ as $1/n$ with the visit count and compare whether the
overestimation shrinks.

## Self-check questions

1. Write the value iteration update and the Q-learning update side by side and point out what changed from an "expectation" to a "sample."
2. Why does subtracting a baseline leave the expected gradient unchanged in a policy gradient, and why subtract it anyway?
3. What can happen when updating several times from one batch without PPO's clipping? Why is being on-policy a disadvantage for learning on real robots?

## How to study this stage

1. **Lectures (first):** connect MDPs, dynamic programming, and model-free prediction and control
   into one line with DeepMind x UCL Lectures 1-5.
2. **This lesson plus the example:** run the example and see the role of exploration with your own
   eyes through exercises (1) and (2).
3. **Problems:** take the quiz in the Korean original (`rc quiz m9-reinforcement-learning-basics`).
4. **Deep RL:** watch the policy gradient and actor-critic lectures of CS 285 and attempt HW2.
   For PPO, read CleanRL's single file `ppo.py` from beginning to end.
5. **The robotics view (optional):** read in Tedrake's *Underactuated Robotics* Ch. 20 how
   model-free policy search connects to optimal control.

## References

- Sergey Levine, Berkeley CS 285 Deep Reinforcement Learning - <https://rail.eecs.berkeley.edu/deeprlcourse/>
- DeepMind x UCL RL Lecture Series 2021 -
  <https://discuss.ai.google.dev/t/deepminds-reinforcement-learning-lecture-series-2021/29496>
- Russ Tedrake, *Underactuated Robotics*, Ch. 20 - <https://underactuated.mit.edu/>
- Shengyi Huang et al., CleanRL - <https://github.com/vwxyzjn/cleanrl>
- John Schulman et al., "Proximal Policy Optimization Algorithms" (2017)
