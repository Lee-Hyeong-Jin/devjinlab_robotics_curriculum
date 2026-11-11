---
id: m6-local-planning-dwa-mppi
lang: en
title: "Local planning and obstacle avoidance (DWA and MPPI in outline)"
summary: Cover local planning (the controller), which follows the global path while avoiding the obstacles visible right now. Implement and compare, on the same differential-drive model in numpy, DWA, which sweeps a grid over velocity space, and MPPI, which rolls out random control sequences and takes a cost-weighted average.
objectives:
  - Explain the differences in role, update rate, and costmap used between global and local planning.
  - Implement DWA with a dynamic window and a trajectory scoring function, and explain how the weights of the score terms affect behavior.
  - Explain MPPI's sampling, cost-weighted averaging, and control sequence shifting (warm start), and implement it simply.
tags: [local-planner, controller, dwa, mppi, obstacle-avoidance, nav2]
---

# Local planning and obstacle avoidance (DWA and MPPI in outline)

Once computed, a global path becomes wrong information the moment a person walks past or a door
closes. **Local planning (Nav2's controller)** runs at 10-50 Hz, looks only at the local costmap
around the robot, and decides the next velocity $(v, \omega)$. Unlike the path following of M3, it
also accounts for obstacles and acceleration limits.

## Concepts

### DWA (Dynamic Window Approach)

1. **The dynamic window:** take as candidates only the velocity range reachable from the current
   $(v_0, \omega_0)$ within one control period $\Delta t$ under the acceleration limits.
2. **Forward simulation:** holding each candidate velocity constant, generate a 1-3 second
   trajectory with the differential-drive model of M3.
3. **Scoring:** take a weighted sum of progress toward the goal (or the global path), obstacle
   clearance, and speed, and pick the highest-scoring candidate.

It is simple, but since it only considers constant-velocity trajectories it cannot express
complex maneuvers. Nav2's DWB controller belongs to this family and composes its score terms as
"critic" plugins.

### MPPI (Model Predictive Path Integral)

MPPI is the sampling version of model predictive control (MPC). It takes the previous period's
optimal control sequence as the mean, adds noise to form $K$ control sequences, rolls them all
out and scores them, then averages them with exponentially larger weights for lower costs. Only
the first control is executed, and the sequence is shifted one step for the next period. The cost
need not be differentiable, and vectorization makes thousands of samples feasible. Nav2 has an
MPPI controller too.

## Key formulas

DWA's dynamic window and score:

$$V_d = [v_0 - \dot v_{max}\Delta t,\ v_0 + \dot v_{max}\Delta t] \times [\omega_0 - \dot\omega_{max}\Delta t,\ \omega_0 + \dot\omega_{max}\Delta t]$$

$$(v, \omega)^{\star} = \arg\max_{(v,\omega) \in V_d} \big[\alpha\,\text{heading} + \beta\,\text{clearance} + \gamma\,v\big]$$

MPPI's weighted average ($S_k$ is the cost of the $k$-th rollout, $\lambda$ the temperature):

$$w_k = \frac{\exp\!\big(-(S_k - \min_j S_j)/\lambda\big)}{\sum_i \exp\!\big(-(S_i - \min_j S_j)/\lambda\big)},\qquad u_t \leftarrow \sum_k w_k\, u_t^{(k)}$$

## Example

A differential-drive robot heading to (6, 0) past four point obstacles. The two methods share
`rollout` and `traj_cost` (minimizing cost rather than maximizing a score).

```python
import numpy as np

rng = np.random.default_rng(0)
obstacles = np.array([[2.0, 0.1], [3.0, -0.4], [3.2, 0.6], [4.5, 0.0]])  # point obstacles [m]
goal = np.array([6.0, 0.0])
DT, HORIZON = 0.1, 15  # look 1.5 s ahead in 0.1 s steps
V_MAX, W_MAX, A_MAX, AW_MAX, RADIUS = 0.6, 1.5, 1.0, 3.0, 0.25


def rollout(state, controls):
    """(K, T, 2) control sequences -> (K, T, 3) trajectories. Differential-drive model."""
    x = np.repeat(state[None, :3], len(controls), axis=0)
    traj = []
    for t in range(controls.shape[1]):
        v, w = controls[:, t, 0], controls[:, t, 1]
        x = x + DT * np.c_[v * np.cos(x[:, 2]), v * np.sin(x[:, 2]), w]
        traj.append(x)
    return np.stack(traj, axis=1)


def traj_cost(traj, controls):
    d = np.linalg.norm(traj[:, :, None, :2] - obstacles[None, None], axis=3).min(axis=(1, 2))
    to_goal = np.linalg.norm(traj[:, -1, :2] - goal, axis=1)
    collide = np.where(d < RADIUS, 1e6, 0.0)
    return 1.0 * to_goal + 0.3 / np.maximum(d, 1e-3) - 0.2 * controls[:, -1, 0] + collide


def dwa(state):
    v0, w0 = state[3], state[4]  # dynamic window: only velocities reachable within one period
    vs = np.linspace(max(0.0, v0 - A_MAX * DT), min(V_MAX, v0 + A_MAX * DT), 7)
    ws = np.linspace(max(-W_MAX, w0 - AW_MAX * DT), min(W_MAX, w0 + AW_MAX * DT), 15)
    cand = np.array([(v, w) for v in vs for w in ws])
    controls = np.repeat(cand[:, None, :], HORIZON, axis=1)  # hold the velocity across the window
    return cand[np.argmin(traj_cost(rollout(state, controls), controls))]


mean_seq = np.zeros((HORIZON, 2))


def mppi(state, K=256, lam=0.1, sigma=(0.2, 0.6)):
    global mean_seq
    noise = rng.normal(0, sigma, (K, HORIZON, 2))
    controls = np.clip(mean_seq + noise, [0, -W_MAX], [V_MAX, W_MAX])
    cost = traj_cost(rollout(state, controls), controls)
    w = np.exp(-(cost - cost.min()) / lam)  # lower-cost samples get larger weights
    mean_seq = np.einsum("k,ktc->tc", w / w.sum(), controls)
    u = mean_seq[0].copy()
    mean_seq = np.vstack([mean_seq[1:], mean_seq[-1:]])  # shift one step for the next period
    return u


for name, controller in [("DWA", dwa), ("MPPI", mppi)]:
    state = np.array([0.0, 0.0, 0.0, 0.0, 0.0])  # x, y, theta, v, omega
    min_clear = np.inf
    elapsed = 0.0
    while elapsed < 30.0:  # at most 30 s
        v, w = controller(state)
        x, y, th = rollout(state, np.array([[[v, w]]]))[0, 0]
        state = np.array([x, y, th, v, w])
        elapsed += DT
        min_clear = min(min_clear, np.linalg.norm(obstacles - state[:2], axis=1).min())
        if np.linalg.norm(state[:2] - goal) < 0.15:
            break
    outcome = "arrived" if np.linalg.norm(state[:2] - goal) < 0.15 else "failed"
    print(
        f"{name:4s} {outcome} {elapsed:4.1f} s, "
        f"final position {np.round(state[:2], 2)}, min obstacle distance {min_clear:.2f} m"
    )
```

DWA arrives in about 11.8 s and MPPI in about 16 s, and both keep clearance wider than the 0.25 m
radius.

**Exercise:** (1) Change the obstacle term's coefficient of 0.3 in `traj_cost` to 0.05 and 1.0 and
compare the clearance and arrival time of the two methods. (2) Vary MPPI's `lam` from 0.02 to 1.0
and record successes and failures.

## Self-check questions

1. Why does local planning use a small local costmap that follows the robot rather than the global costmap?
2. What goes wrong without DWA's dynamic window (if every velocity is a candidate)?
3. How does the control behave in MPPI when the temperature $\lambda$ is near zero, and when it is large?

## How to study this stage

1. **This lesson plus the example (first):** run the example and plot the trajectories of the two
   methods on top of each other.
2. **Code reading:** compare the DWA code of PythonRobotics against the `dwa` of the example and
   match up the score terms.
3. **Documentation:** map the DWB and MPPI critic lists of the Nav2 Configuration Guide onto the
   terms of the example's `traj_cost`.
4. **Problems:** take the quiz in the Korean original (`rc quiz m6-local-planning-dwa-mppi`), then
   do exercises (1) and (2).
5. **Depth (optional):** check the derivations in the original DWA and MPPI papers (see the references).

## References

- Nav2 Documentation - <https://docs.nav2.org/rolling/index.html>
- Atsushi Sakai, PythonRobotics - <https://atsushisakai.github.io/PythonRobotics/>
- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 13 - <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Dieter Fox, Wolfram Burgard, Sebastian Thrun, "The Dynamic Window Approach to Collision Avoidance", IEEE RAM 1997 (no link)
- Grady Williams et al., "Information Theoretic MPC for Model-Based Reinforcement Learning", ICRA 2017 (MPPI, no link)
