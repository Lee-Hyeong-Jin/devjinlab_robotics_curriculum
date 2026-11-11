---
id: m9-mdp-decision-making
lang: en
title: "Decision making and MDPs (value iteration, policy iteration)"
summary: Formalize decision making for a robot whose actions have stochastic outcomes as a Markov decision process (MDP), and implement value iteration and policy iteration for the Bellman equations in numpy on a slippery grid world. It is the bridge between the deterministic graph search of M6 and the reinforcement learning of M9.
objectives:
  - Define an MDP by states, actions, transition probabilities, rewards, and a discount factor, and rewrite a grid path planning problem as an MDP.
  - Write the Bellman optimality equation, implement value iteration and policy iteration, and confirm that they converge to the same optimal policy.
  - Explain how slip probability, step cost, and the discount factor affect the optimal policy (risk-averse routes).
tags: [mdp, bellman-equation, value-iteration, policy-iteration, decision-making, gridworld]
---

# Decision making and MDPs (value iteration, policy iteration)

The A* of M6 assumed the robot always reaches the cell it was commanded to, but a real robot
slips. Where M5 dealt with **uncertainty in state**, this lesson deals with **uncertainty in the
outcome of actions**. The standard framework for that is the Markov decision process (MDP), and
the reinforcement learning that follows is "solving an MDP whose model you do not know."

## Concepts

### The five elements of an MDP

An MDP is defined by $(S, A, P, r, \gamma)$.

- **States $S$, actions $A$:** grid cells, and up, down, left, right.
- **Transition probabilities $P(s' \mid s, a)$:** 0.8 in the intended direction, 0.1 slipping to
  each side. The key assumption is the **Markov property**: the next state depends only on the
  current state and action.
- **Rewards $r$:** +1 at the goal, −1 in a pit, −0.04 in every other cell (the cost of time).
- **Discount factor $\gamma \in [0, 1)$:** discounts distant future rewards, making the infinite
  sum finite.

The solution is not a path but a **policy** $\pi(s)$ - a table of "what to do in any cell." Even
if a slip lands the robot in a cell that was not in the plan, the policy has an answer.

### Value functions and the Bellman equation

The state value $V^\pi(s)$ is the expected discounted sum of rewards from following $\pi$ out of
$s$. The optimal value $V^*$ satisfies the **Bellman optimality equation** - "take one step and
be optimal thereafter" - and there are two standard solutions.

- **Value iteration:** repeatedly apply the Bellman equation as an assignment update. It is a
  contraction that shrinks the error by at least a factor of $\gamma$ per sweep, so convergence
  is guaranteed.
- **Policy iteration:** (1) compute the current policy's value exactly from a linear system
  (policy evaluation), then (2) act greedily with respect to that value to get a new policy
  (policy improvement). It needs few iterations but solves an $|S| \times |S|$ system each time.

If you do not know $P$, this extends into reinforcement learning; if you do not even know the
state with certainty, into an MDP over beliefs (a POMDP).

## Key formulas

The value iteration update (the Bellman optimality equation):

$$V_{k+1}(s) = \max_a \sum_{s'} P(s' \mid s, a)\,\big[r(s') + \gamma V_k(s')\big]$$

Policy evaluation (the matrix form of the Bellman expectation equation) and policy improvement:

$$V^\pi = (I - \gamma P_\pi)^{-1} P_\pi r,\qquad \pi'(s) = \arg\max_a \sum_{s'} P(s' \mid s, a)\big[r(s') + \gamma V^\pi(s')\big]$$

## Example

Solve a 4 × 4 grid both ways and compare.

```python
import numpy as np

# 4 x 4 grid. G = goal (+1), P = pit (-1), # = wall. Moving into any other cell costs -0.04
LAYOUT = ["...G", ".#.P", "....", "...."]
MOVES = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # up right down left
NAMES = "↑→↓←"
GAMMA, STEP_COST = 0.95, -0.04
states = [(r, c) for r in range(4) for c in range(4) if LAYOUT[r][c] != "#"]
idx = {s: i for i, s in enumerate(states)}
N = len(states)
R = np.array([{"G": 1.0, "P": -1.0}.get(LAYOUT[r][c], STEP_COST) for r, c in states])


def move(s, a):
    r, c = s[0] + MOVES[a][0], s[1] + MOVES[a][1]
    ok = 0 <= r < 4 and 0 <= c < 4 and LAYOUT[r][c] != "#"
    return (r, c) if ok else s  # blocked by a wall or the border: stay put


# transition probabilities P[a, s, s']: 0.8 intended, 0.1 slipping to each side.
# R[s'] is the reward of the cell arrived at
P = np.zeros((4, N, N))
for a in range(4):
    for s in states:
        if LAYOUT[s[0]][s[1]] in "GP":
            continue  # terminal states: no outgoing transitions, so V stays 0
        for a2, p in [(a, 0.8), ((a - 1) % 4, 0.1), ((a + 1) % 4, 0.1)]:
            P[a, idx[s], idx[move(s, a2)]] += p


def value_iteration(tol=1e-8):
    V, sweeps = np.zeros(N), 0
    while True:
        Q = P @ (R + GAMMA * V)  # Q[a, s] = sum_s' P(s'|s,a) [r(s') + gamma V(s')]
        sweeps += 1
        if np.abs(Q.max(axis=0) - V).max() < tol:
            return Q.max(axis=0), Q.argmax(axis=0), sweeps
        V = Q.max(axis=0)


def policy_iteration():
    pi, rounds = np.zeros(N, dtype=int), 0
    while True:
        P_pi = P[pi, np.arange(N)]  # transition matrix of the actions the policy chose (N x N)
        V = np.linalg.solve(np.eye(N) - GAMMA * P_pi, P_pi @ R)  # policy evaluation
        pi_new = (P @ (R + GAMMA * V)).argmax(axis=0)  # policy improvement (greedy)
        rounds += 1
        if np.array_equal(pi_new, pi):
            return V, pi, rounds
        pi = pi_new


V_vi, pi_vi, sweeps = value_iteration()
V_pi, pi_pi, rounds = policy_iteration()
print(f"value iteration {sweeps} sweeps, policy iteration {rounds} rounds, "
      f"value difference {np.abs(V_vi - V_pi).max():.0e}")
for r in range(4):
    cells = [LAYOUT[r][c] * 5 for c in range(4)]
    for c in range(4):
        if LAYOUT[r][c] == ".":
            i = idx[(r, c)]
            cells[c] = f"{NAMES[pi_vi[i]]}{V_vi[i]:+.2f}"
    print(" ".join(cells))
```

Output:

```text
value iteration 42 sweeps, policy iteration 5 rounds, value difference 1e-08
→+0.72 →+0.83 →+0.94 GGGGG
↑+0.63 ##### ↑+0.64 PPPPP
↑+0.53 ←+0.44 ↑+0.52 ↓+0.30
↑+0.44 ↑+0.38 ↑+0.42 ←+0.34
```

The two methods reach the same policy. In the cell just below the pit, (2, 3), the optimal action
is **down**, not up: going up falls into the pit with probability 0.8, so the policy backs off
and takes the long way around. Deterministic A* cannot express this kind of risk aversion.

**Exercise:** (1) Change `STEP_COST` to −0.4 and see whether the policy switches to the shortcut
past the pit. (2) With slip set to 0, does it match the shortest path of M6? (3) Set $\gamma$ to
0.5 and 0.99 and record the sweep counts.

## Self-check questions

1. What is the difference between A*'s "path" and an MDP's "policy," and why is a policy needed when there is slip?
2. Explain why value iteration converges, in terms of contraction and $\gamma < 1$. What gets slower as $\gamma$ approaches 1?
3. Policy iteration needs far fewer iterations and yet is not always faster on large state spaces. Why?

## How to study this stage

1. **Video (first):** get the overall flow from Stachniss's "MDPs."
2. **This lesson plus the example:** print `V` each sweep and compare how value spreads out from
   the goal against the Dijkstra of M6.
3. **By hand:** compute one Bellman update for cell (0, 2) by hand and match it against the code.
4. **Problems:** take the quiz in the Korean original (`rc quiz m9-mdp-decision-making`), then do
   exercises (1) through (3).
5. **Depth (optional):** read LaValle Part III and the MDP and POMDP chapters of
   *Probabilistic Robotics*.

## References

- Cyrill Stachniss, "MDPs" - <https://www.youtube.com/watch?v=72QwRnSNY88>
- Steven M. LaValle, *Planning Algorithms*, Part III - <https://lavalle.pl/planning/>
- Sebastian Thrun, Wolfram Burgard, Dieter Fox, *Probabilistic Robotics*, MIT Press -
  <https://robots.stanford.edu/probabilistic-robotics/>
- MIT OCW 16.410 Principles of Autonomy and Decision Making -
  <https://ocw.mit.edu/courses/16-410-principles-of-autonomy-and-decision-making-fall-2010>
