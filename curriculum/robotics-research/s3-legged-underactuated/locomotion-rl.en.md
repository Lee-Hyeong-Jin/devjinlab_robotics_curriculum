---
id: s3-locomotion-rl
lang: en
title: Locomotion RL
summary: >-
  Derive the standard architecture of legged reinforcement learning — a teacher that sees
  privileged information, a student that sees only a history, and the estimation of latent
  environment variables — on a reduced linear-quadratic model that can be solved exactly. Show
  that the best a student can reach is "the teacher's policy with the posterior mean plugged in"
  and that the gap, $\kappa\sigma_H^2$, is inversely proportional to the history length; compute
  that a policy without history survives by raising its gain 2.2 times, at 1.96 times the cost.
  Show that distilling actions directly can learn the correlations of the data-collecting policy
  and become unstable (a pole at $-1.68$ with a one-step history), while the RMA-style separation
  that regresses the latent from the history is independent of the collecting policy. Finally,
  derive the over-optimization in which optimizing a misaligned reward for longer makes true
  performance fall again.
objectives:
  - Derive the optimal policies of a privileged teacher and a history-based student in the linear-quadratic model and write the gap through the posterior variance.
  - Derive the optimal gain and cost of a policy without history and compare it with an adaptive policy.
  - Explain, and show numerically, why action distillation depends on the distribution of the collecting policy and can become unstable.
  - Show that the dimension of the latent is set by the number of action-relevant directions and explain its relation to identifiability.
  - Derive the over-optimization of a misaligned reward in a quadratic model and compute the early-stopping time.
tags: [legged-robots, reinforcement-learning, privileged-learning, teacher-student, rma, research]
---

# Locomotion RL

## Setup and notation

The first four lessons of S3 were **model-based** legged control (hybrid limit cycles, HZD,
centroidal MPC, whole-body control). This lesson covers the standard architecture of the other
road — learning a policy in simulation and transferring it to hardware. The covariate shift of
imitation learning is that of `c8-imitation-learning`, and sim-to-real transfer and domain
randomization are those of `c8-generalization-sim2real`. The recommended prerequisites are those
two lessons and `s3-whole-body-control`.

Real locomotion RL is done with neural networks on nonlinear contact dynamics of tens of
dimensions. The **logic** of its architecture is solved exactly in a far smaller model. This
lesson solves that small model to the end and states explicitly how much carries over to reality
and where it stops.

| Symbol | Meaning |
|---|---|
| $x_k$ | Robot state (here a scalar — the velocity tracking error) |
| $u_k$ | Action (a reduced stand-in for joint torques or targets) |
| $e \in \mathbb{R}^p$ | **Environment variables** (friction, payload, slope, …). Constant within an episode, random across episodes. $e \sim \mathcal{N}(0, \Sigma_e)$ |
| $d = c^\top e$ | The **combined effect** of the environment variables on the dynamics (a disturbance) |
| Privileged information | What is known in simulation but cannot be measured on hardware. Here, $e$ |
| Teacher | A policy that sees $(x, e)$ |
| Student | A policy that sees only $x$ and a history of the past $H$ steps |
| $z$ | The latent — the summary of the environment that the policy actually uses |
| $\sigma_H^2$ | Posterior variance of $d$ after seeing $H$ steps of history |

**The reduced model.** The whole lesson uses the system

$$
x_{k+1} = a\,x_k + b\,u_k + c^\top e + w_k, \qquad
\text{cost} = \mathbb{E}\big[x_k^2 + \rho\,u_k^2\big] \ (\text{average per step}), \tag{1}
$$

with $a = 0.9$, $b = 0.5$, $\rho = 0.1$, $w_k \sim \mathcal{N}(0, 0.1^2)$, $c = (1, 0.5, -0.8)$,
$\Sigma_e = \operatorname{diag}(0.3^2, 0.4^2, 0.2^2)$ (hence
$\sigma_d^2 = c^\top\Sigma_ec = 0.1556$). How to read it: the robot tries to follow a target
velocity ($x$), friction, payload and slope ($e$) produce a constant drag $d$, and **no sensor
measures it**.

## Key results

The bracket gives the derivation depth (D0 cited / D1 skeleton / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the student's best is "teacher + posterior mean", and the gap is proportional to the
  posterior variance) [D2]** — the teacher's optimal policy is $u = -Kx - K_dd$ ($K = 1.362$,
  $K_d = 1.938$), and the optimal policy of a student that sees only a history is the same
  expression with the posterior mean, $u = -Kx - K_d\hat{d}$. The student's excess cost is
  $$
  J_{\text{student}} - J_{\text{teacher}} = \kappa\,\sigma_H^2, \qquad
  \sigma_H^2 = \Big(\frac{1}{\sigma_d^2} + \frac{H}{\sigma_w^2}\Big)^{-1} \tag{2}
  $$
  ($\kappa = 1.544$). Measured: at history $H = 1, 5, 20, 50$ the student/teacher cost ratio is
  $1.196, 1.041, 1.010, 1.004$, and the excess cost agrees with (2) to five decimals. **The
  condition for privileged learning to work is that the environment variable be identifiable
  from the history.**
- **R2 (without history the policy becomes stiff) [D2]** — the average cost of a memoryless
  policy $u = -K_0x$ that cannot use a history is
  $$
  J(K_0) = (1 + \rho K_0^2)\Big[\frac{\sigma_d^2}{(1 - a + bK_0)^2} + \frac{\sigma_w^2}{1 - (a - bK_0)^2}\Big] \tag{3}
  $$
  and the optimal gain is $K_0^\star = 2.99$ — **2.2 times** the teacher's gain. Its cost is
  $0.145$, $1.96$ times the teacher's. Using the teacher's gain $K$ unchanged gives $4.2$ times.
  A policy that does not know the environment goes towards **holding on with a high gain** —
  the reason "robust" policies learned by domain randomization are conservative and spend a lot
  of energy.
- **R3 (distilling actions learns the correlations of the collecting policy; regressing the
  latent does not) [D2]** — if the student is trained by regressing "$(x, \text{history})$ → the
  teacher's action", the solution **depends on the policy that collected the data**. With a
  one-step history, a student trained on rollouts of the non-adaptive policy learns the weights
  $(-5.17, +2.98)$ and has a closed-loop pole at $-1.68$ (unstable), and a student trained on
  rollouts of the teacher learns $(+0.55, -2.01)$ with a pole at $+1.17$ (unstable). By contrast,
  **regressing the latent $d$ from the history** gives **the same** weight on both data sets
  ($0.9384$), in agreement with the analytic shrinkage factor $0.9396$, and a student that plugs
  that estimate into the teacher's policy is always stable (pole $0.219$). This is the ground for
  the architecture with a separate adaptation module (RMA).
- **R4 (the dimension of the latent is the number of action-relevant directions) [D2]** —
  although the environment variable is three-dimensional, the teacher's action depends only on
  the single direction $d = c^\top e$. That one direction is fully identified from the history
  (posterior variance $\to 0$) and the individual components are not — the coefficient of
  determination given by $d$ is $0.58, 0.26, 0.16$ for $e_1, e_2, e_3$. **The adaptation module
  does not estimate the environment; it estimates the summary the action needs.** When that
  summary leaves no trace in the observations (terrain ahead that has not yet been stepped on),
  no history however long can estimate it, and exteroception is required.
- **R5 (over-optimization of a misaligned reward) [D2]** — if the optimum of the reward (or of
  the simulator) used for training is displaced from the optimum of the true objective **in a
  weakly determined direction**, true performance rises early in the optimization and falls
  again later. In the quadratic model true performance peaks at $-0.027$ at $t^\star = 2.86$ and
  is $-1.125$ if optimized to the end — **early stopping is 42 times better**. This is why
  optimizing the reward for longer and better is not the answer.

## Derivation

### R1 — teacher, student, posterior variance

**The teacher.** Knowing $d$ fixes the steady state. Minimize $x_{ss}^2 + \rho u_{ss}^2$ subject
to $(1-a)x_{ss} = bu_{ss} + d$. With $g = b/(1-a)$, $x_{ss} = gu_{ss} + d/(1-a)$, and setting the
derivative with respect to $u_{ss}$ to zero,

$$
u_{ss} = -\frac{g/(1-a)}{g^2 + \rho}\,d = -1.992\,d, \qquad x_{ss} = 0.0398\,d. \tag{4}
$$

(Control is cheap ($\rho = 0.1$), so the disturbance is cancelled almost completely.) The
deviation around the steady state is a standard LQR: from the Riccati equation
$P = 1 + a^2P - a^2b^2P^2/(\rho + b^2P)$, $P = 1.245$, $K = abP/(\rho + b^2P) = 1.362$, and the
closed-loop pole is $a - bK = 0.219$. Altogether

$$
u = -K(x - x_{ss}) + u_{ss} = -Kx - K_dd, \qquad K_d = -(Kx_{ss} + u_{ss})/d = 1.938, \tag{5}
$$

and the average cost is
$J_{\text{teacher}} = 0.398\,\sigma_d^2 + (1 + \rho K^2)\sigma_w^2/(1 - 0.219^2) = 0.0744$.

**What the student can see.** The student does not see $d$, but at every step it can compute

$$
r_k := x_{k+1} - a\,x_k - b\,u_k = d + w_k \tag{6}
$$

— it looks at **the difference between prediction and reality** in its own state and its own
action. In the words of a legged robot this is "how much it did not move as commanded", and it
is the reason a proprioceptive history contains information about the environment. $r_k$ is an
independent measurement with mean $d$ and variance $\sigma_w^2$, so after $H$ of them the
posterior is

$$
\hat{d}_H = \frac{\sum r/\sigma_w^2}{1/\sigma_d^2 + H/\sigma_w^2}, \qquad
\sigma_H^2 = \Big(\frac{1}{\sigma_d^2} + \frac{H}{\sigma_w^2}\Big)^{-1}. \tag{7}
$$

**The student's optimal policy.** (1) is linear-quadratic-Gaussian, so the separation theorem
(`c4-dp-lqr-lqg`) holds: the optimal student is the teacher's policy with the **posterior mean**
plugged in, $u = -Kx - K_d\hat{d}$. The student is worse than the teacher not in the form of the
policy but only in $\hat{d} \ne d$.

**The gap.** Treating the estimation error $\varepsilon = \hat{d} - d$ as slowly varying
(quasi-static), the steady state is displaced by $\Delta x = -bK_d\varepsilon/(1 - a + bK)$ and
$\Delta u = -K\Delta x - K_d\varepsilon$. Since (4) is optimal, the first-order change in cost is
zero and the second-order term is

$$
\Delta J = \big(\Delta x^2 + \rho\,\Delta u^2\big) = \kappa\,\varepsilon^2, \qquad
\kappa = \Big(\frac{bK_d}{1 - a + bK}\Big)^2 + \rho\Big(\frac{KbK_d}{1 - a + bK} - K_d\Big)^2 = 1.544,
$$

and taking the expectation gives (2).

| History $H$ | $\sigma_H^2$ | Student cost (measured) | Excess (measured) | $\kappa\sigma_H^2$ | Student/teacher |
|---|---|---|---|---|---|
| 1 | $0.00940$ | $0.0886$ | $0.01451$ | $0.01451$ | $1.196$ |
| 2 | $0.00484$ | $0.0816$ | $0.00748$ | $0.00748$ | $1.101$ |
| 5 | $0.00197$ | $0.0772$ | $0.00305$ | $0.00305$ | $1.041$ |
| 10 | $0.00099$ | $0.0757$ | $0.00153$ | $0.00153$ | $1.021$ |
| 20 | $0.00050$ | $0.0749$ | $0.00077$ | $0.00077$ | $1.010$ |
| 50 | $0.00020$ | $0.0744$ | $0.00031$ | $0.00031$ | $1.004$ |

(4000 episodes, 300 steps, the first 100 steps excluded. The measured cost of the teacher is
$0.0741$.)

**How to read it.** (a) The gap shrinks as $1/H$ — with 20 steps of history the student is
within 1% of the teacher. This is the same order of magnitude as the tens of steps (about one
second) of history that real systems use. (b) What sets the gap is the **signal-to-noise ratio**
$\sigma_d^2/\sigma_w^2$. If the effect of the environment variable is buried in process noise the
history has to be long, and if the environment changes in the meantime (the terrain changes) the
estimate cannot keep up. (c) The imitation loss has a **floor**:
$\mathbb{E}[(u_{\text{teacher}} - u_{\text{student}})^2] = K_d^2\sigma_H^2$ ($0.0074$ at
$H = 5$). A learning curve that stops at this value is not a failure of learning but a limit of
information.

**Where the assumptions break**: (a) the separation theorem holds only in the
linear-quadratic-Gaussian case. For a nonlinear system with contact, "the teacher's policy with
the estimate plugged in" is not optimal — when the estimate is uncertain it is better to act
**cautiously** (`c4-robust-stochastic-oc` R4), and that caution cannot be learned from the
teacher (the teacher has never experienced uncertainty). This is the fundamental limit of the
teacher-student approach. (b) $e$ was assumed constant within an episode. When the terrain
changes the posterior is held back by old information, and the window length $H$ becomes a trade
between "how fast to forget" and "how accurately to estimate" (problem P2). (c) (6) assumes the
student **knows** the dynamics coefficients $a$ and $b$. A real student (a neural network) has to
learn those too, implicitly, from the history.

### R2 — the memoryless policy

**Setting.** No history can be used; only $u = -K_0x$ is available (a purely reactive policy).
The closed loop is $x_{k+1} = (a - bK_0)x_k + d + w_k$; given $d$ the mean goes to
$d/(1 - a + bK_0)$ and the variance around it is $\sigma_w^2/(1 - (a - bK_0)^2)$. Averaging over
$d$ and using $u^2 = K_0^2x^2$ gives (3).

**The optimal gain.** Minimizing (3) numerically gives $K_0^\star = 2.988$, $J = 0.1452$
(measured $0.1446$).

| Policy | Gain | Average cost | Relative to the teacher |
|---|---|---|---|
| Teacher (sees $e$) | $K = 1.362$ | $0.0744$ | $1.00$ |
| Student ($H = 20$) | $K = 1.362$ + adaptation | $0.0749$ | $1.01$ |
| Memoryless, optimal gain | $K_0 = 2.988$ | $0.1452$ | $1.96$ |
| Memoryless, teacher's gain | $K_0 = 1.362$ | $0.3148$ | $4.23$ |

**How to read it.** A memoryless policy cannot cancel $d$, so it **raises its gain** to reduce
the steady-state error $d/(1 - a + bK_0)$. The price is the control cost $\rho K_0^2$ and the
amplification of noise. A policy learned by domain randomization alone (without history) finds
this solution — one high gain that "works" in every environment. On hardware such a policy is
**stiff, noisy and energy hungry**. Adaptation is the device that removes that conservatism:
knowing the environment, the policy spends only what is needed.

**Where the assumptions break**: in the linear model raising the gain is always possible. A real
robot has torque limits, actuator bandwidth and the discontinuity of contact, so a high gain
invites instability — the actual cost of a memoryless policy is worse than (3), and beyond some
range of environments a single policy **does not exist**. That range is the practical limit when
setting the width of domain randomization.

### R3 — distillation: what to regress

**Action distillation.** The most direct method trains the student by regressing
"$(x_k, \bar{r}_H)$ → the teacher's action $u^\star_k$" ($\bar{r}_H$: the mean of the last $H$
residuals (6)). The analytic solution has weights $(-K, -K_d s_H)$ with
$s_H = (H/\sigma_w^2)/(1/\sigma_d^2 + H/\sigma_w^2)$. But least squares does not look for that
analytic solution; it looks for the weights with the smallest error **on the training data**.

**The correlations hidden in the data.** Two correlations cause the trouble. (a) In rollouts of
the non-adaptive policy ($u = -Kx$) the steady state of $x$ is $d/(1 - a + bK)$, so **$x$ itself
reveals $d$**. The regression learns to read $d$ from $x$ instead of from $\bar{r}$. (b) $x_k$
and the preceding residual $r_{k-1} = d + w_{k-1}$ share the same noise $w_{k-1}$. The regression
learns to "trim" the noise of $r$ with $x$. Both correlations hold **only while that policy
collects the data**. When the student acts itself they vanish or flip.

**Measured** (2000 episodes × 120 steps; the least-squares weights of the first iteration and
their closed-loop pole $a + bw_x$):

| History | Collecting policy | Learned weights $(w_x, w_r)$ | Pole | Analytic $(-K, -K_ds_H)$ |
|---|---|---|---|---|
| $H = 1$ | Non-adaptive | $(-5.166, +2.975)$ | $-1.683$ **unstable** | $(-1.362, -1.821)$ |
| $H = 1$ | Teacher | $(+0.546, -2.007)$ | $+1.173$ **unstable** | 〃 |
| $H = 5$ | Non-adaptive | $(-1.363, -1.911)$ | $0.219$ | $(-1.362, -1.913)$ |
| $H = 5$ | Teacher | $(-0.901, -1.938)$ | $0.450$ | 〃 |
| $H = 20$ | Non-adaptive | $(-1.362, -1.931)$ | $0.219$ | $(-1.362, -1.932)$ |
| $H = 20$ | Teacher | $(-1.247, -1.935)$ | $0.276$ | 〃 |

At $H = 1$ **the student is unstable whichever data it is trained on** — look at the sign of the
weight in the first row: the weight on the residual is **positive**. The student reads $d$ from
$x$ ($-5.17$) and uses the residual the wrong way round. Its imitation loss on the training data
is small ($0.016$), yet it diverges when deployed. With a longer history $\bar{r}$ becomes a good
enough signal and the problem recedes, but on teacher data even at $H = 20$, $w_x$ is $-1.247$,
different from the analytic $-1.362$. Iterating with the teacher labelling the student's own
rollouts (DAgger — `c8-imitation-learning`) matches the distributions and reduces this
deviation, but **if the student of the first iteration is unstable, that iteration cannot even
start**.

**Latent regression.** Split the problem in two instead. (a) Leave the teacher policy
$u = -Kx - K_dz$ as it is (frozen), and (b) train only the adaptation module $\phi$: history →
$\hat{z}$. If the target is $z = d$ and the input is $\bar{r}_H$ **alone**,

$$
\hat{z} = s\,\bar{r}_H, \qquad
s = \frac{\operatorname{Cov}(d, \bar{r}_H)}{\operatorname{Var}(\bar{r}_H)} = \frac{\sigma_d^2}{\sigma_d^2 + \sigma_w^2/H} = s_H, \tag{8}
$$

and since the distribution of $\bar{r}_H = d + \bar{w}$ is **independent of the policy** (the
residual of (6) is $d + w$ whatever $u$ is used), the regression weight does not depend on the
collecting policy.

| History | $s$ on non-adaptive data | $s$ on teacher data | Analytic $s_H$ | Cost of the deployed student | Pole |
|---|---|---|---|---|---|
| $H = 1$ | $0.9384$ | $0.9384$ | $0.9396$ | $0.0884$ | $0.219$ |
| $H = 5$ | $0.9865$ | $0.9865$ | $0.9873$ | $0.0769$ | $0.219$ |
| $H = 20$ | $0.9960$ | $0.9960$ | $0.9968$ | $0.0746$ | $0.219$ |

The weights agree **to the fourth decimal** between the two data sets, and the student is stable
even at $H = 1$ (its pole is that of the teacher — the adaptation module does not touch the
feedback gain). This is the two-phase structure of RMA: in phase 1 a base policy is trained with
the privileged information encoded into a latent, and in phase 2 only the adaptation module that
regresses that latent from the history is trained (`kumar2021-rma`).

**Where the assumptions break**: the policy-independence of (8) comes from the residual (6)
being independent of the policy — which is so only for an additive disturbance on a linear
system. On a real robot the effect of an environment variable **depends on the state** (friction
shows only when slipping, payload only when accelerating). The amount of information in the
history then itself depends on the policy — a careful policy reveals less of the environment —
and latent regression too comes to depend on the collecting distribution. This is why RMA
collects the data of phase 2 **from rollouts of the very policy that uses the adaptation
module**. And a neural adaptation module takes the whole history, including $x$, as input, so it
retains room to learn the same hidden correlations as the action distillation of the table
above.

### R4 — what the latent has to carry

**Action-relevant directions.** The teacher's action (5) depends on $e$ only through
$K_dc^\top e$. Hence $z = c^\top e$ (one-dimensional) represents **exactly the same** policy as
the teacher. In general, if the teacher is $u = -Kx - Le$ ($L \in \mathbb{R}^{m\times p}$) the
latent dimension needed is $\operatorname{rank}L$, which does not exceed the action dimension
$m$. Even with tens of environment variables the latent can be small.

**Identifiability.** All the history gives is the $d = c^\top e$ of (6). For the individual
components of $e$, the fraction of variance explained by $d$ is
$\operatorname{Cov}(e_i, d)^2/(\operatorname{Var}(e_i)\operatorname{Var}(d))$:

| Component | Fraction explained by $d$ |
|---|---|
| $e_1$ (coefficient $1.0$, standard deviation $0.3$) | $0.578$ |
| $e_2$ (coefficient $0.5$, standard deviation $0.4$) | $0.257$ |
| $e_3$ (coefficient $-0.8$, standard deviation $0.2$) | $0.165$ |
| $d = c^\top e$ | $1.000$ (for a long history) |

**The adaptation module cannot get the friction coefficient right. Nor does it need to.** The
direction the action needs and the direction identified from the history coincide — because the
environment variables affect the cost **only through the dynamics**. That coincidence is the
structural reason proprioceptive adaptation works.

**When the coincidence fails.** If an environment variable leaves no trace in the present
dynamics but affects the cost **to come** — a step one stride ahead, the start of a patch of
slippery ice — there is a direction the action needs that is not identified from the history. A
proprioceptive history knows only "after stepping on it". Estimating that direction requires
exteroception (a height map, a camera), and a device for **falling back** on the proprioceptive
estimate when that sense cannot be trusted (snow, grass, reflections). A belief encoder that
blends exteroception and proprioception according to their reliability is the core of
`miki2022-anymal-wild`, and the step before it — how far proprioception alone goes — is
`lee2020-blind-locomotion`.

**Where the assumptions break**: "latent dimension needed = $\operatorname{rank}L$" is for a
teacher that depends on $e$ **linearly**. For a nonlinear teacher the action-relevant information
may be a low-dimensional manifold but not a linear subspace, and too small a latent dimension
degrades the teacher itself (a loss in phase 1). In practice the latent dimension is a
hyperparameter, and papers that report the grounds for its choice are rare.

### R5 — over-optimizing the reward

**The model.** Let the parameters of the policy be $\theta = (\theta_1, \theta_2)$ and

$$
J_{\text{true}}(\theta) = -\tfrac12\big(\theta_1^2 + \lambda_{\text{true}}\,\theta_2^2\big), \qquad
J_{\text{reward}}(\theta) = -\tfrac12\big(\theta_1^2 + \lambda\,(\theta_2 - \delta)^2\big). \tag{9}
$$

The two objectives **agree** in $\theta_1$ (the main direction of the task) and their optima are
**displaced** by $\delta$ in $\theta_2$. $\lambda \ll 1$ means the reward determines $\theta_2$
only weakly — in locomotion, a direction that "hardly affects velocity tracking but yields a
little more by exploiting the inaccurate contact model of the simulator", or a direction that an
auxiliary reward term pulls slightly.

**Gradient flow on the reward.** With $\dot\theta = \nabla J_{\text{reward}}$ and
$\theta(0) = (x_0, 0)$,

$$
\theta_1(t) = x_0e^{-t}, \qquad \theta_2(t) = \delta\big(1 - e^{-\lambda t}\big),
$$

$$
J_{\text{true}}(t) = -\tfrac12\Big[x_0^2e^{-2t} + \lambda_{\text{true}}\delta^2\big(1 - e^{-\lambda t}\big)^2\Big]. \tag{10}
$$

The first term improves fast ($e^{-2t}$) and the second deteriorates slowly ($\lambda t$).
$\dot{J}_{\text{true}} = 0$ gives

$$
x_0^2e^{-2t^\star} = \lambda_{\text{true}}\delta^2\lambda\big(1 - e^{-\lambda t^\star}\big)e^{-\lambda t^\star}. \tag{11}
$$

**Numbers** ($x_0 = 2$, $\lambda = 0.05$, $\lambda_{\text{true}} = 1$, $\delta = 1.5$):

| Training time $t$ | 0 | $2.86$ ($t^\star$) | 10 | 50 | 100 | $\infty$ |
|---|---|---|---|---|---|---|
| $J_{\text{true}}$ | $-2.000$ | $-0.027$ | $-0.174$ | $-0.948$ | $-1.110$ | $-1.125$ |
| $J_{\text{reward}}$ | $-2.056$ | $-0.049$ | $-0.021$ | $-0.0004$ | $\approx 0$ | $0$ |

**The reward rises to the end while true performance peaks at $t^\star$ and then falls.** The
true performance $-1.125$ of the policy optimized to the end is 42 times worse than the peak
$-0.027$. And from the learning curve (the reward) alone **one cannot tell when to stop** — the
peak is visible only when evaluating with the true objective.

**How to read it.** (a) Over-optimization arises not because the reward is "wrong" but because
it is **slightly displaced in a weakly determined direction**. While the main direction is right,
optimizing the reward raises true performance at first — which is why the problem shows up late.
(b) There are three remedies: **regularization** that increases the curvature of the displaced
direction (penalties on action rate and on energy — raising $\lambda$ while shrinking $\delta$),
**randomizing** that direction of the simulator so it cannot be exploited, and **early
stopping** by evaluating with the true objective (hardware or a high-fidelity simulation).
(c) The third invites the selection bias of `s4-evaluation-science` R3 — if the evaluation of the
true objective is noisy, the checkpoint that "looks best" is inflated.

**Where the assumptions break**: (9) takes the displacement to be in one direction and the
objectives to be quadratic. In a real policy space there are several displaced directions that
show up on different time scales, so true performance need not be unimodal — it can fall and
rise again. And the optimization of reinforcement learning is not a gradient flow — exploration
noise can **accelerate** the drift along weakly determined directions (where the reward signal
is weak and noise dominates).

## Problem set

The answer policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Derive (4), (5) and $\kappa$ with no line missing, and (a) find and
interpret the limits of $K_d$ and $\kappa$ as $\rho \to 0$ and $\rho \to \infty$, (b) derive the
floor $K_d^2\sigma_H^2$ of the imitation loss.
*Answer sketch*: (a) $\rho \to 0$: $u_{ss} \to -d/b$ (full cancellation), $K \to a/b$ (deadbeat),
$K_d \to 1/b$. The estimation error becomes the error of $x$ unchanged, so $\kappa \to 1$.
$\rho \to \infty$: control is given up, so $K_d \to 0$ and $\kappa \to 0$ — **if the teacher
does not use the environment information the student has nothing to lose**. (b) The difference
of the two actions is $K_d(\hat{d} - d)$.

**P2 (derivation, ★★, R1)** Let the environment vary as a **random walk** within the episode
($d_{k+1} = d_k + \nu_k$, $\nu \sim \mathcal{N}(0, q)$). Find the mean squared error, as a
function of $H$, of using the mean of the last $H$ residuals as the estimate, and find the
$H^\star$ that minimizes it.
*Answer sketch*: the sum of the error due to noise, $\sigma_w^2/H$, and the error due to drift
(the mean over the window lags the current value), $\approx qH/3$.
$H^\star = \sqrt{3\sigma_w^2/q}$. **The history length is set by how fast the environment
changes** — longer is not better. ($qH/3$ is the large-$H$ approximation — the sum in which the
lag within the window accumulates is of the same kind as (3) of `s1-slam-benchmarking`.)

**P3 (derivation, ★★, R4)** Let the action be two-dimensional and the teacher
$u = -Kx - Le$ ($L \in \mathbb{R}^{2\times5}$ of rank 2). (a) Find the minimal latent dimension
that reproduces the teacher exactly, and its encoder, (b) when the history reveals only $Ce$
($C \in \mathbb{R}^{1\times5}$), write in terms of $L$ and $C$ the condition for the student's
excess cost to be zero.
*Answer sketch*: (a) dimension 2, $z = Le$ (or any basis of the row space of $L$). (b) The row
space of $L$ must be contained in that of $C$ — impossible here since $C$ is one-dimensional.
One unidentified action-relevant direction remains, and an excess cost proportional to the prior
variance of that direction remains **however long the history**.

**P4 (numerical, ★, R1, R2)** For $a = 0.8$, $b = 1$, $\rho = 0.5$, $\sigma_w = 0.2$,
$\sigma_d = 0.5$, (a) find $K$ and $K_d$, (b) find the posterior variance at $H = 10$ and the
floor of the imitation loss, (c) find the cost of the memoryless policy at $K_0 = K$ and compare
it with the teacher's cost.
*Answer*: (a) from the Riccati equation $P = 1 + 0.64P - 0.64P^2/(0.5 + P)$, $P = 1.2274$ and
$K = 0.5684$. $g = 5$, $u_{ss}/d = -(g/0.2)/(g^2 + 0.5) = -0.9804$, $x_{ss}/d = 0.0980$,
$K_d = -(0.5684\times0.0980 - 0.9804) = 0.9247$. (b) $\sigma_{10}^2 = (4 + 250)^{-1} = 0.003937$,
floor $K_d^2\sigma_{10}^2 = 0.003366$. (c) Teacher:
$(0.0980^2 + 0.5\times0.9804^2)\times0.25 + (1 + 0.5\times0.5684^2)\times0.04/(1 - 0.2316^2) = 0.1225 + 0.0491 = 0.1716$.
Memoryless ($K_0 = K$):
$1.1616\times[0.25/0.7684^2 + 0.04/0.9464] = 1.1616\times0.4656 = 0.5409$ ($3.15$ times the
teacher). (Tolerance 1%.)
*Check*: confirm that the closed-loop pole $a - bK = 0.2316$ is inside the unit circle and that
$K_d$ is positive.

**P5 (implementation, ★★★, R1, R3)** Carry the reproduction task over to a **nonlinear** system:
replace the disturbance term of (1) by $c^\top e\cdot\tanh(2x_k)$ (the effect of the environment
depends on the state — it does not show at rest). Obtain the teacher by policy gradient or grid
search, build students by action distillation and by latent regression, and compare.
*Rubric*: (a) show that the information the residual (6) carries depends on $x$ (near
$x \approx 0$, $d$ cannot be estimated) (b) show numerically that the weight of latent
regression now **does depend on the collecting policy** (c) measure the improvement from
recollecting data on the student's own rollouts and retraining (d) look for evidence that
"teacher + posterior mean" is not optimal (for example, a policy that deliberately moves at the
start to reveal the environment does better) — if you find none, state how far you searched.

**P6 (counterexample, ★★, R3, R5)** (a) Pick from the tables of this lesson, and give
numerically, a counterexample to "a small imitation loss means good deployed performance".
(b) Construct a counterexample to "if the reward keeps rising the policy keeps improving" by
varying $\lambda$ in (10), and find the condition under which over-optimization **does not
occur** ($t^\star = \infty$).
*Property checklist*: (a) uses the $H = 1$ student trained on non-adaptive data — imitation loss
$0.016$ on the training data, divergence when deployed — and states that the distribution the
loss measures and the distribution of deployment differ. (b) shows that there is no
over-optimization only when $\delta = 0$ (no displacement) or $\lambda_{\text{true}} = 0$ (the
true objective is indifferent to that direction). Increasing $\lambda$ does **not remove
over-optimization; it only makes it faster**.

**P7 (paper, ★★, R1, R3, R4)** Read `lee2020-blind-locomotion`, `kumar2021-rma` and
`miki2022-anymal-wild` and (a) tabulate for each of the three papers the list of privileged
information the teacher sees and the inputs of the student, (b) decide for each paper whether
the target the student is trained on is the **action**, the **latent** (or both), (c) write a
paragraph on how Miki et al. handle the case in which exteroception cannot be trusted, (d) find
the **denominators** (number of trials, distance, time) the three papers report in their
hardware evaluations and estimate the reliability demonstrated through (4) of
`s5-field-deployment`.
*Rubric*: (a) and (b) pass by citing the relevant section or figure of the paper. (c) passes by
naming the encoding of a belief state and the weighting (gating) by sensor reliability. (d) is
the core — for the items whose denominator you cannot find, **write that you could not**.
Discovering that the "action distillation versus latent regression" distinction of R3 in this
lesson is not clean in the actual papers, and writing why, is excellent.

## Paper reading

**Three must-read papers.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read in three passes, and in the third pass concentrate on questions 1,
5 and 7. The three form **one lineage** — read them in order.

1. **Lee, Hwangbo, Wellhausen, Koltun & Hutter, "Learning quadrupedal locomotion over challenging
   terrain" (2020, Science Robotics)** — role: `seminal`.
   <https://arxiv.org/abs/2010.11251> (the method part: privileged learning and the structure of
   the student)
   The paper that trained, by teacher and student, a policy that walks rough terrain on
   proprioception alone. The starting point of R1 and R4 of this lesson.
   Additional questions: (a) what privileged information does the teacher see, and which of it
   could and could not **plausibly** be estimated by the student from a history? (b) what is the
   history length of the student, and are grounds given for it? (c) how does the way the authors
   adjust terrain difficulty during training (the curriculum) relate to the over-optimization of
   R5?
2. **Kumar, Fu, Pathak & Malik, "RMA: rapid motor adaptation for legged robots" (2021, RSS)**
   — role: `standard`.
   <https://arxiv.org/abs/2107.04034> (the method part: two-phase training)
   The paper that set up explicitly the architecture separating a base policy from an adaptation
   module. The primary source for R3 of this lesson.
   Additional questions: (a) what is the dimension of the latent, and how does it compare with
   that of the environment variables? (b) in phase 2, **from whose rollouts** is the training
   data of the adaptation module collected, and why (see "where the assumptions break" of R3)?
   (c) how do the authors show that the latent estimated by the adaptation module responds to
   actual changes of the environment?
3. **Miki, Lee, Hwangbo, Wellhausen, Koltun & Hutter, "Learning robust perceptive locomotion for
   quadrupedal robots in the wild" (2022, Science Robotics)** — role: `frontier`.
   <https://arxiv.org/abs/2201.08117> (the method part: the belief encoder and the integration
   of exteroception)
   An architecture that takes in exteroception yet falls back on proprioception when it is
   wrong. The answer to "when the coincidence fails" of R4 in this lesson.
   Additional questions: (a) what noise and faults are injected into the exteroceptive input
   during training? (b) how do the authors make visible that the policy has decided "not to
   trust" exteroception? (c) the teacher sees perfect terrain information — how does that clash
   with (a) of "where the assumptions break" of R1 (the teacher has never experienced
   uncertainty)?

**Two recommended papers.** `chen2020-learning-by-cheating` (the paper that set up the
privileged teacher-student architecture in autonomous driving — the same logic as in
locomotion, <https://arxiv.org/abs/1912.12294>) and `hwangbo2019-agile-motor-skills` (earlier
work that reduced the sim-to-real gap by learning an actuator model — an approach that shrinks
"the displaced direction of the simulator" of R5, <https://arxiv.org/abs/1901.08652>).

**The ten fixed questions**: (1) what problem is solved under what assumptions (2) what exactly
could earlier work not do (3) the key idea in one line of mathematics (4) what is the theoretical
guarantee and **what is not guaranteed** (5) the independent and dependent variables and baselines
of the experiments, and were they tuned fairly (6) do the metrics match the claims, and are
variance and seeds reported (7) what information needed for reproduction is missing (8) if it is
wrong, which assumption to suspect first (9) computational and memory complexity and real-time
capability (10) what would you change to surpass it a year from now.

## Reproduction task

**Tier R2 (algorithm reimplementation) — required.** Compute budget: one laptop CPU core, under
2 minutes in total, at most 500 MB of memory. numpy + scipy only. It runs the **structure** of
the teacher-student pipeline to the end on the reduced model (1). The extension to an actual
legged environment is the **optional task (R4)** below — as the design prescribes, it may need a
GPU and is therefore optional.

**Input data**: none. The constants below are everything.

```python
"""Reproduction task of s3-locomotion-rl: constants of the reduced model and one step."""

import numpy as np

SEED = 20261117
A, B, RHO, SIGMA_W = 0.9, 0.5, 0.1, 0.1
C = np.array([1.0, 0.5, -0.8])
SIGMA_E = np.diag([0.3**2, 0.4**2, 0.2**2])
SIGMA_D2 = float(C @ SIGMA_E @ C)  # 0.1556


def sample_env(rng, n_episodes):
    """Per-episode constant environment variables e (n, 3) and their combined effect d = e @ C."""
    e = rng.multivariate_normal(np.zeros(3), SIGMA_E, n_episodes)
    return e, e @ C


def step(rng, x, u, d):
    """x_{k+1} = A x + B u + d + w. Also returns the residual r = x_{k+1} - A x - B u."""
    x_next = A * x + B * u + d + SIGMA_W * rng.normal(size=x.shape)
    return x_next, x_next - A * x - B * u
```

**Conventions.** (a) Create `np.random.default_rng(SEED)` afresh for every experiment. (b) The
average cost is the per-step mean of $x_k^2 + \rho u_k^2$, discarding the initial stretch (100
steps in Parts A and B, 40 steps in Parts C and D). (c) Early on, when fewer than $H$ residuals
exist, use as many as there are.

**Part A — the teacher.** Find $K$ by Riccati iteration and $K_d$ through (4) and (5), and
compare the average cost over 4000 episodes × 300 steps with the analytic value.

**Part B — the student and the memoryless policy.** (a) Measure the cost of the student that
uses the posterior mean (7) at $H \in \{1, 2, 5, 10, 20, 50\}$ and compare the excess cost with
$\kappa\sigma_H^2$. (b) Find the $K_0^\star$ that minimizes (3) and its cost, and confirm by
simulation.

**Part C — action distillation.** Run the least-squares regression from the features
$(x_k, \bar{r}_H)$ to the teacher's action on (a) rollouts of the non-adaptive policy
($u = -Kx$) and (b) rollouts of the teacher (2000 episodes × 120 steps, only the steps with
$k \ge H$), for $H \in \{1, 5, 20\}$. Report the learned weights and the closed-loop pole
$a + b\,w_x$, and confirm that a student whose pole is outside the unit circle diverges when
deployed.

**Part D — latent regression.** On the same two data sets find the weight of the (intercept-free)
regression $\bar{r}_H \to d$, compare it with the $s_H$ of (8), and report the cost and the pole
of the student that attaches that adaptation module to the teacher policy.

**Part E — identification and over-optimization.** (a) Compute the fraction of each of the three
components of $e$ explained by $d$. (b) Compute (10) on $t \in [0, 200]$, find $t^\star$ and
$J_{\text{true}}(t^\star)$ and compare with the solution of (11).

**Optional task (R4 — reduced reproduction in a legged environment).** In one public legged
training environment (the `legged_gym` of the resource list, or a smaller two-dimensional walker
that runs on a CPU) (a) train a teacher that sees privileged information (at least two of
friction, payload and terrain height), (b) distil a student that sees only a proprioceptive
history, (c) compare the performance of the teacher, the student and a memoryless policy over
the randomized range of environment variables with 5 seeds. The acceptance criterion is
**agreement of the qualitative trends**: the order teacher ≥ student > memoryless, the student
deteriorating as the history is shortened, and the mean torque (or energy) of the memoryless
policy being larger. There are no numerical reference values — report the environment, the
seeds and the training budget, and record in particular which prediction of R1–R4 of this lesson
**did not hold**.

**Acceptance criteria — all five required conditions must hold to pass.**

1. **Part A** — $K = 1.3624$, $K_d = 1.9378$ (tolerance $10^{-3}$), closed-loop pole $0.2188$,
   analytic cost $0.0744$, with the simulated cost within 1.5% relative error of it (the author
   measured $0.0741$).
2. **Part B** — (a) the student/teacher cost ratios are
   $1.196, 1.101, 1.041, 1.021, 1.010, 1.004$ ($\pm0.01$) and the excess cost is within 5%
   relative error of $\kappa\sigma_H^2$ ($\kappa = 1.544$). (b) $K_0^\star = 2.99 \pm 0.02$ with
   cost $0.1452$ (simulation $\pm2\%$), **at least 1.9 times the teacher's**. Report alongside
   that the cost of the memoryless policy with the teacher's gain is $0.315 \pm 0.01$.
3. **Part C** — at $H = 1$ the weights on non-adaptive data are $(-5.17, +2.98)$ and on teacher
   data $(+0.55, -2.01)$ ($\pm0.1$), and both poles are **outside** the unit circle ($-1.68$ and
   $+1.17$). The weights on non-adaptive data at $H = 5, 20$ agree with the analytic
   $(-1.362, -1.913)$ and $(-1.362, -1.932)$ to $\pm0.01$. **Print explicitly that the $H = 1$
   student diverges when deployed.**
4. **Part D** — the regression weights on the two data sets **agree with each other to within
   $10^{-3}$** and are $0.938, 0.987, 0.996$ ($\pm0.003$) at $H = 1, 5, 20$. The pole of the
   student is $0.2188$ in all three cases and the costs are $0.0884, 0.0769, 0.0746$
   ($\pm2\%$).
5. **Part E** — (a) the explained fractions are $0.578, 0.257, 0.165$ (tolerance $10^{-3}$,
   analytic computation). (b) $t^\star = 2.864 \pm 0.005$,
   $J_{\text{true}}(t^\star) = -0.0265 \pm 0.0005$, $J_{\text{true}}(\infty) = -1.125$, and print
   alongside that **the reward is monotonically increasing** over the same interval.

**Comparison**: (a) the baselines of Part B are the teacher (upper bound) and the memoryless
policy (lower bound). (b) For Parts C and D the analytic $(-K, -K_ds_H)$ and $s_H$ are the
baselines. (c) For Part E (b) the policy optimized to the end is the baseline.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| $K_d$ is near 2.0 | Only $u_{ss}$ was used and the $Kx_{ss}$ term was left out | (5): $K_d = -(Kx_{ss} + u_{ss})/d$ |
| The student's excess cost is several times $\kappa\sigma_H^2$ | The prior term $1/\sigma_d^2$ was dropped and a plain mean was used | Check that the shrinkage factor at $H = 1$ is $0.94$ |
| The student comes out better than the teacher | The student was handed $d$ by mistake, or the comparison used different random numbers | Run the two policies with generators of the same `SEED` |
| The $H = 1$ weights of Part C equal the analytic ones | The residual in the features was a **future** one ($r_k$) | The features at time $k$ use residuals only up to $r_{k-1}$ |
| Nothing diverges in Part C | The analytic weights were deployed, not the learned ones | Roll out with the weights returned by the regression |
| The two weights of Part D differ | $x$ was put into the regression input | The input is $\bar{r}_H$ alone. No intercept either |
| There is no $t^\star$ in Part E (monotone increase) | $\delta = 0$, or the start was $\theta_2(0) = \delta$ | Check that $\theta(0) = (x_0, 0)$ |

## Open problems

- **(Open problem) Behaviour a teacher cannot teach** — (a) of "where the assumptions break" of
  R1: a privileged teacher does not experience uncertainty, so it takes no information-seeking
  actions (probing a foothold gingerly) and no cautious ones, and the student cannot learn them.
  Current approaches: giving the teacher noisy observations too, fine-tuning the student by
  reinforcement learning after imitation, asymmetric actor-critic (only the critic sees
  privileged information). What is missing: a **lower bound** on the teacher-student gap — a
  way to estimate in advance, for a given task, how much performance is out of reach of
  imitation alone.
- **(Open problem) What to randomize** — R2 shows that the wider the randomization the more
  conservative the policy, and R5 that if it is narrow the policy exploits the defects of the
  simulator. The choice in between currently rests on experience. Current approaches: fitting
  the randomization distribution to hardware data, automatic curricula that widen the range
  with performance. What is missing: a criterion for judging the randomization **sufficient**
  for a given range of hardware conditions — the same gap as the "untested conditions" problem
  of `s4-evaluation-science` and `s5-field-deployment`.
- **(Open problem) Guarantees for learned locomotion policies** — model-based controllers come
  with arguments for stability and constraint satisfaction (`s3-hzd-gait-generation`,
  `s3-centroidal-mpc`). A learned policy earns trust through evaluation alone. Current
  approaches: placing a model-based safety filter on top of the learned policy
  (`c3-cbf-safety-filter`), reachability analysis of the closed loop. What is missing: a way to
  certify the closed-loop stability of a neural policy on a high-dimensional system with contact
  **at a verifiable scale**.
- **(Open problem) Principles of reward design** — where the displacement $\delta$ of R5 comes
  from is usually discovered on hardware after training has finished. A locomotion reward
  consists of ten or more terms with hand-tuned weights, and although that choice decides the
  outcome, sensitivity analyses are rare. Current approaches: imitation rewards that follow
  motion-capture or animal data, adversarial motion priors that reduce the number of reward
  terms, generating and revising rewards with language models. What is missing: a way to
  diagnose before training which term of the reward creates **a weakly determined direction**.

## Concept check

Take it with `rc quiz s3-locomotion-rl`. This quiz is a **concept check only**; the real work is
the problem set and the reproduction task above (`lesson-standard.md` §4).

## How to study this stage

1. **Accept the reduced model (15 min)** — translate (1) of "Setup and notation" into the words
   of a legged robot: $x$ is the velocity error, $e$ friction, payload and slope, $d$ the drag
   they produce. Write down also **what this model threw away** (contact, nonlinearity, high
   dimension).
2. **Solve the teacher by hand (40 min)** — (4), (5) and the Riccati equation. Confirm why $K_d$
   is close to $1/b = 2$ (control is cheap, so the disturbance is cancelled almost completely).
3. **(6), (7) and the gap (40 min)** — the one line saying that the residual reveals the
   environment is all there is to proprioceptive adaptation. Derive $\kappa$ and fill in the
   table with Parts A and B. See the measurement and $\kappa\sigma_H^2$ agree to the fifth
   decimal.
4. **The memoryless policy (30 min)** — derive (3) and see the optimal gain become 2.2 times
   larger. Write in one sentence "why a robust policy is stiff".
5. **Break distillation with Part C (50 min)** — **the most important experiment** of this
   lesson. Look at the signs of the weights at $H = 1$ and watch the deployed student diverge.
   Plotting the correlation between $x$ and $d$ in the training data shows what the regression
   learned.
6. **Fix it with Part D (30 min)** — confirm that the weight of latent regression is the same on
   the same two data sets. Explain why (the residual of (6) is independent of the policy) and
   write down the condition under which that fails.
7. **Part E (30 min)** — the identification table and the over-optimization curve. Solve (11)
   numerically for $t^\star$ and plot the reward and the true performance in one figure.
8. **The three papers as a lineage (180 min)** — Lee et al. (proprioceptive teacher-student) →
   Kumar et al. (separating the adaptation module) → Miki et al. (integrating exteroception). In
   each paper find "what the student regresses" and "who collects that data". The one-page note
   per paper is **mandatory**.
9. **End with what does not carry over (30 min)** — collect and read the five "where the
   assumptions break" of this lesson, pick one conclusion of the reduced model that **seems
   unlikely to hold** in real locomotion, and write a paragraph on why. If you do the optional
   task (R4), test that prediction.

**Pass criterion**: from a blank page you can derive (4), (5), (7), $\kappa$, (3), (8) and (11);
you can explain the difference between action distillation and latent regression from the
standpoint of the collecting distribution; you can say **what the adaptation module estimates
and what it cannot**; you have code that satisfies all five required conditions of the
reproduction task; and you have notes on the three papers.
