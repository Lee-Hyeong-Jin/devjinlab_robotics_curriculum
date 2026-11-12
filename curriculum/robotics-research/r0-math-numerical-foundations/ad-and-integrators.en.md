---
id: r0-ad-and-integrators
lang: en
title: Automatic differentiation and numerical integrators
summary: >-
  Derive the cost structure of forward and reverse mode automatic differentiation, and examine the
  energy behaviour of explicit, implicit and symplectic integrators together with the condition for
  stiffness. The lesson that organises the tools every reproduction task of the research track uses.
objectives:
  - Compare the cost of forward and reverse mode automatic differentiation in terms of input and output dimension.
  - Explain how automatic differentiation differs from finite differences and symbolic differentiation in accuracy and cost.
  - Derive the stability regions of explicit and implicit integrators and decide when a problem is stiff.
  - Explain why a symplectic integrator keeps the energy bounded.
  - State the limits of gradients given by automatic differentiation for non-smooth (contact) dynamics.
tags: [automatic-differentiation, integrators, stiffness, symplectic, research]
---

# Automatic differentiation and numerical integrators

## Setup and notation

| Symbol | Meaning |
|---|---|
| $f: \mathbb{R}^n \to \mathbb{R}^m$ | the function to differentiate, $J = Df \in \mathbb{R}^{m\times n}$ |
| $\mathrm{cost}(f)$ | the cost of one evaluation of $f$ |
| $\dot{x} = g(x)$ | the ODE to integrate, with step size $h$ |
| $\lambda$ | the eigenvalue of the linear system $\dot{x}=\lambda x$ |
| $z = h\lambda$ | the dimensionless number measuring the stability region |
| $\epsilon$ | machine epsilon |

Assumed: `f0-python-numerics-git` (floating point, finite differences),
`f0-differential-equations` (ODEs, stability) and `r0-manifolds-lie-groups`.

## Key results

- **R1 (the cost of the two AD modes) [D2]** — forward mode costs
  $O(\mathrm{cost}(f))$ per input direction, reverse mode $O(\mathrm{cost}(f))$ per output
  component. So the cost of a full Jacobian is

$$
\text{forward: } O(n\cdot\mathrm{cost}(f)), \qquad \text{reverse: } O(m\cdot\mathrm{cost}(f)) . \tag{1}
$$

  **Forward when $n \ll m$, reverse when $n \gg m$.** An optimization objective has $m=1$, so
  reverse mode (backpropagation) is right.
- **R2 (AD is exact) [D2]** — AD applies the chain rule **at machine precision**, so it has no
  truncation error. Finite differences trade truncation $O(h^p)$ against round-off
  $O(\epsilon/h)$, with a best case of about $O(\epsilon^{2/3})$ (central differences). Unlike
  symbolic differentiation it suffers **no expression swell**.
- **R3 (the stability region of explicit Euler) [D2]** — applying forward Euler to
  $\dot{x}=\lambda x$ gives $x_{k+1} = (1+z)x_k$ with $z=h\lambda$, so stability requires

$$
|1+z| < 1 . \tag{2}
$$

  For real $\lambda<0$ this is $h < 2/|\lambda|$. Backward Euler gives
  $x_{k+1} = x_k/(1-z)$ and is stable for every $h$ when $\mathrm{Re}(\lambda)<0$ (**A-stable**).
- **R4 (stiffness) [D2]** — in a system with a large eigenvalue ratio
  ($|\lambda_{\max}|/|\lambda_{\min}| \gg 1$), **stability rather than accuracy** dictates the
  step: $h < 2/|\lambda_{\max}|$ must be respected even after the fast mode has died out. That is
  the reason for implicit integrators.
- **R5 (symplectic integrators) [D1]** — for a Hamiltonian system, a symplectic integrator (such
  as semi-implicit Euler or leapfrog) **does not conserve energy exactly but keeps it bounded**
  (there is no long-term drift). A general Runge-Kutta method can let energy drift monotonically
  however high its order **[D0]** (Hairer et al.).

## Derivation

### R1 — why the two modes differ in cost

Decomposing $f = f_k \circ \cdots \circ f_1$, the chain rule gives
$J = J_k J_{k-1}\cdots J_1$. The point is **from which side the product is bracketed**.

- **Forward mode**: multiply from the right. For a vector $v$ one computes
  $Jv = J_k(\cdots(J_1v))$, needing only **matrix-vector products**, at cost
  $O(\mathrm{cost}(f))$. A full Jacobian repeats this for $n$ basis vectors, giving
  $O(n\cdot\mathrm{cost}(f))$.
- **Reverse mode**: multiply from the left. For a row vector $u^\top$ one computes
  $u^\top J = ((u^\top J_k)\cdots)J_1$, again only vector products, and a full Jacobian costs
  $O(m\cdot\mathrm{cost}(f))$ over $m$ basis vectors.

**The price**: multiplying from the left requires **storing the intermediate forward values** (a
tape, memory $O(\text{size of the computation graph})$). Forward mode needs no storage. So the
choice in (1) involves a memory trade-off as well as cost — checkpointing in deep learning is the
technique that tunes that trade-off.

**Application in robotics**: a dynamics Jacobian of the order $\mathbb{R}^6 \to \mathbb{R}^{6}$ has
$n \approx m$, so the two modes are comparable and **analytic derivatives** (differentiating RNEA
in C2) beat both. Conversely, a policy gradient of a scalar cost has $m=1$, where reverse mode
dominates.

### R3 — stability regions and their picture

The exact solution of the test equation $\dot{x}=\lambda x$ is $x(t) = e^{\lambda t}x_0$, which
decays to zero when $\mathrm{Re}(\lambda)<0$. An integrator approximates each step by a **rational
function** $R(z)$:

| Integrator | $R(z)$ | Stability condition |
|---|---|---|
| Forward Euler | $1+z$ | $|1+z|<1$ (a finite region) |
| Backward Euler | $1/(1-z)$ | all of $\mathrm{Re}(z)<0$ (A-stable) |
| Implicit midpoint | $(1+z/2)/(1-z/2)$ | all of $\mathrm{Re}(z)<0$, and $|R|=1$ is preserved |
| RK4 | a quartic polynomial | a finite region ($|z| \lesssim 2.8$ on the real axis) |

Since $|R(z)|<1$ is the condition for the numerical solution to decay, **an explicit integrator has
a finite stability region** while an implicit one can be unbounded. That is what creates the
stiffness problem of R4.

**Where the assumption breaks**: this analysis is for the **linear test equation**. For a nonlinear
system one estimates from the eigenvalues of a local linearisation, but those change with the
state, so adaptive stepping is needed. For **non-smooth** systems such as contact there are
instants where the linearisation itself is undefined and the analysis does not apply.

### R5 — how to look at the energy behaviour (at the level of observation)

Integrating the simple pendulum $\ddot\theta = -\sin\theta$ for $10^4$ steps with (a) forward
Euler, (b) RK4 and (c) semi-implicit (symplectic) Euler:

- forward Euler: the energy **increases monotonically** (a tendency to diverge)
- RK4: the energy **decreases** slowly and monotonically (high order makes it slow, but there is drift)
- symplectic: the energy **oscillates but stays bounded**

The core reason: a symplectic integrator exactly conserves a **modified Hamiltonian** — a quantity
differing from the true energy by $O(h^p)$ — so the true energy merely oscillates within that
difference without accumulating drift. The proof needs backward error analysis and is cited here **[D0]**.

## Proof sketch

### R2 — the accuracy of AD and the limits of finite differences

**Hypotheses** H1: $f$ is a composition of elementary operations whose derivatives are known
exactly. H2: the relative error of a floating-point operation is bounded by $\epsilon$.
**Conclusion** C: the derivative error of AD is of order $O(\epsilon)$, while the best error of a
central finite difference is $O(\epsilon^{2/3})$.

**Strategy**: decompose the error of each method and find the optimal step.

1. **AD**: the chain rule is applied with **exact derivative rules**, so the truncation error is
   zero. What remains is the floating-point error of each operation, accumulating as
   $O(N\epsilon)$ over $N$ operations.
2. **Central finite differences**: the Taylor expansion gives truncation
   $\tfrac{h^2}{6}|f'''|$, and the cancellation in the numerator gives round-off
   $\approx \epsilon|f|/h$.
3. Minimising the sum $E(h) = c_1h^2 + c_2\epsilon/h$ gives $h^\star \sim \epsilon^{1/3}$ and
   $E(h^\star) \sim \epsilon^{2/3}$. In double precision that is $\approx 4\times10^{-11}$ —
   **about five digits worse** than AD.
4. With forward differences the truncation is $O(h)$, so $h^\star\sim\epsilon^{1/2}$ and the error
   $\sim\epsilon^{1/2} \approx 10^{-8}$, worse still.

**Delete a hypothesis**: the failure of H1 is what matters in practice — for **non-smooth
operations** (`abs`, `max`, conditional branches, contact detection) no "exact derivative" exists.
AD still returns **some value** (a one-sided derivative, or zero), but there is no guarantee it is
a meaningful gradient. That is why "can AD gradients be trusted" is an open problem in the contact
dynamics of C2 and in differentiable simulators.

## Problem set

★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Decide with (1) which mode should be used for the Jacobians of
$f: \mathbb{R}^{1000}\to\mathbb{R}$ and $g: \mathbb{R}\to\mathbb{R}^{1000}$, and compute the cost ratios.
*Solution sketch*: $f$ has $m=1$ so reverse mode (one evaluation) while forward needs 1000; $g$ has
$n=1$ so forward. Either way the ratio is 1000.

**P2 (derivation, ★★, R3)** Derive $R(z)$ for the implicit midpoint rule and show $|R(z)|=1$ on
$\mathrm{Re}(z)=0$. Why is that related to energy conservation?
*Solution sketch*: solving $x_{k+1} = x_k + hz\frac{x_k+x_{k+1}}{2}$ gives
$R=(1+z/2)/(1-z/2)$. For purely imaginary $z$ numerator and denominator have equal modulus, so
$|R|=1$ — oscillations are not damped.

**P3 (proof, ★★★, R2)** Compute step 3 of R2 exactly (with constants). Then explain the principle
by which **complex-step differentiation** attains $O(\epsilon)$ without truncation error.
*Solution sketch*: taking the imaginary part of $f(x+ih)$ sends the even-order terms to the real
part, so the truncation is $O(h^2)$ but **there is no cancellation**, allowing an extremely small
$h$. The restriction is that it applies only to analytic functions.

**P4 (numerical, ★, R3·R4)** For a linear system with eigenvalues $-1$ and $-1000$ integrated by
forward Euler, find (a) the largest step stability permits, (b) the time constant of the slow mode,
(c) the number of steps needed to integrate 10 seconds.
*Answer*: (a) $h < 2/1000 = 0.002$; (b) the slow time constant is 1 second; (c)
$10/0.002 = 5000$ steps. **With a stiffness ratio of 1000, stability rather than accuracy
dominates the cost.** Tolerance 10%.

**P5 (implementation, ★★, R3·R5)** Integrate the simple pendulum for $10^4$ steps with (a) forward
Euler, (b) RK4 and (c) semi-implicit Euler and plot the energy trajectories. Summarise the drift
behaviour of the three numerically.
*Rubric*: (a) the same $h$ and the same initial condition throughout; (b) report the **relative**
change in energy; (c) show numerically that forward Euler increases, RK4 decreases and symplectic
stays bounded; (d) halve $h$ and confirm the drift shrinks according to the order.

**P6 (counterexample, ★★, R2)** Build three functions on which AD returns a **wrong (or
meaningless) gradient** (one each with `abs`, `max` and a conditional branch). Check what AD returns
in each case and write what problem it could cause in practice.
*Property checklist*: `abs(x)` at $x=0$ returns a one-sided derivative (usually 0 or 1),
`max(a,b)` picks one side at a tie, and a conditional branch differentiates **only the branch that
ran**. If contact detection is a branch, the gradient reflects nothing about a contact transition —
the open problem of C2.

## Paper reading

**The textbook exception applies** (lesson standard §5). Read the following and write two one-page
notes (fixed questions 1, 3, 4 and 8).

1. **Nocedal & Wright, ch.8 (calculating derivatives)** — questions: (a) separate the cases where
   the authors recommend finite differences from those where they recommend AD. (b) summarise how
   techniques exploiting the **sparsity** of a Jacobian (graph colouring) reduce the cost — this
   connects to `r0-sparse-linear-algebra`.
2. **The JAX Automatic differentiation documentation** —
   <https://docs.jax.dev/en/latest/automatic-differentiation.html> (URL unverified)
   Questions: (a) confirm whether the criterion for choosing `jacfwd` versus `jacrev` matches (1).
   (b) find the **non-smooth function** cases the documentation warns about and compare them with P6.

**One methodological source**: the optimization appendix of Tedrake's *Underactuated Robotics* —
it leads into the differentiability discussion for systems with contact.

## Reproduction task

**Tier R1 (numerical check).** Budget: under one minute on a laptop CPU, numpy/scipy (optionally
jax). All four conditions must pass.

1. **AD versus finite-difference accuracy**: compute the gradient of $f(x)=x^\top Mx$ (a)
   analytically, (b) by AD (or a complex step) and (c) by a central difference. The error of (b)
   must be at most $10^{-14}$, the **best** error of (c) around $10^{-10}$, and sweeping $h$ must
   produce a **V-shaped curve** whose minimum sits near $\epsilon^{1/3}$.
2. **Cost structure**: varying $n$ and $m$, time the computation of a Jacobian in forward and
   reverse mode and confirm the linear relation of (1) (slope $1\pm0.3$).
3. **Stability region**: integrate $\dot{x}=\lambda x$ ($\lambda=-1000$) with forward Euler and
   confirm stability, marginality and divergence at $h = 0.0015, 0.002, 0.0025$ respectively
   (compare with (2)).
4. **Energy drift**: integrate the simple pendulum for $10^4$ steps with forward Euler, RK4 and a
   symplectic method and show that the relative energy change **increases, decreases and stays
   bounded** respectively (the symplectic change should be at least an order of magnitude smaller
   than the other two).

**Baseline**: solve the same stiff problem with `RK45` (explicit) and `Radau` (implicit) in
`scipy.integrate.solve_ivp` and compare the **number of function evaluations** (the implicit method
should need far fewer).

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| no V-curve for the central difference | the $h$ range is too narrow, or the function is too simple (zero third derivative) | widen $h$ to $10^{-1}$-$10^{-14}$ and use a function with a cubic term |
| the slope in condition 2 is not 1 | the timings are too short and overhead dominates | repeat the measurement and make the function evaluation more expensive |
| drift appears although the method is symplectic | semi-implicit Euler is implemented wrongly (the order of the two updates) | check the order of the position and velocity updates (one must use the updated value) |
| the implicit integrator is slower | the problem is not stiff | print the eigenvalue ratio; with a small stiffness ratio the explicit method winning is correct |

## Open problems

- **(Open) Gradients of non-smooth dynamics** — there is little theory on whether the gradients AD
  returns for systems with contact and collision are **meaningful**. Relaxations (soft contact) and
  stochastic smoothing are used, but how each changes the optimization outcome is not quantified
  (the same item as the open problem of C2).
- **(Open) Integrators on manifolds** — integrating a rotation in coordinates leaves the group,
  and re-projecting lowers the order. Integrators that **preserve the group structure while
  attaining high order** (Lie group integrators) are not widely used in robotics practice
  (connecting to C1 and C2).
- **(Open) Choosing an integrator under real-time constraints** — MPC must perform thousands of
  forward integrations in real time. There is no **automatic selection** criterion jointly
  optimising accuracy, stability and cost (connecting to the real-time iteration of C4).

## Concept check

Run `rc quiz r0-ad-and-integrators` (add `--lang en` for the English text). It is for concept
checking only.

The four items cover: which AD mode suits a scalar objective; the best achievable error of a
central difference; whether accuracy or stability limits the step for a stiff problem; and the
property a symplectic integrator has.

## How to study this stage

1. **Understand (1) as a cost structure (30 min)** — it is entirely about **which side the chain
   rule's matrix product is bracketed from**. Solving P1 makes the `jacfwd`/`jacrev` choice mechanical.
2. **Redraw the V-curve (40 min)** — repeat the experiment from `f0-python-numerics-git`, now
   comparing against AD. Seeing five digits of difference makes it obvious why reproduction tasks
   demand AD verification.
3. **Compute stability regions by hand (50 min)** — derive $R(z)$ for the four integrators
   (including P2). The finiteness of the explicit region is the whole of the stiffness problem.
4. **Meet stiffness as a number (60 min)** — condition 3 of the reproduction task and the baseline
   (function evaluations of RK45 versus Radau). Seeing the implicit method dominate at an
   eigenvalue ratio of 1000 shows that integrator choice is not a matter of taste.
5. **Plot the energy trajectories (60 min)** — condition 4. With the three curves (increasing,
   decreasing, bounded) on one plot, the meaning of symplectic needs no explanation. It is used
   directly in the simulations of C2 and S3.
6. **Keep a record of where AD fails (50 min)** — actually run the three functions of P6 and record
   what AD returns. That record becomes your reference when reading the contact dynamics of C2 and
   differentiable simulators.

**Passing bar**: you can choose the mode from (1), can derive $R(z)$ for the four integrators, have
confirmed the stiffness condition numerically, and have code meeting all four acceptance conditions
plus notes on both readings.
