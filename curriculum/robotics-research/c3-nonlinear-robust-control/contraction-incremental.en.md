---
id: c3-contraction-incremental
lang: en
title: Contraction theory and incremental stability
summary: >-
  A viewpoint that looks at convergence **between** trajectories rather than to an equilibrium.
  The contraction condition is derived from virtual displacements and a Riemannian metric, and why
  it gives exponential convergence and incremental stability is treated at the level of proof. It
  then derives the disturbance tube and shows why a control contraction metric (CCM) makes the
  design problem convex, and finally measures how conservative a certified rate is against the
  measured one.
objectives:
  - Derive the contraction condition and the exponential bound from virtual displacements with no missing steps.
  - Find a constant metric by LMI for a system in which the Euclidean metric shows no contraction.
  - Derive the tube radius $\sup\lVert\Theta d\rVert/\lambda$ under disturbance with the comparison lemma.
  - Explain why the control contraction metric condition becomes convex in the dual metric $W = M^{-1}$.
  - Measure the gap between the certified and the measured convergence rate and name the sources of conservatism.
tags: [nonlinear-control, contraction, incremental-stability, riemannian-metric, ccm, research]
---

# Contraction theory and incremental stability

## Setup and notation

The Lyapunov function of `c3-lyapunov-stability` measures distance to **one equilibrium**, and
`c3-feedback-linearization` moved that equilibrium to the origin of a linear system. Contraction
theory changes the question: does the **distance between two trajectories** shrink? It can be
answered without knowing an equilibrium, or even when there is none (time-varying systems), which
is why it is used directly for tracking control, observers and tube-based planning.

Assumed: the matrix exponential and the variational equation (used in R3 of
`c3-feedback-linearization`), the comparison lemma (R4 of `c3-lyapunov-stability`), definiteness
and LMIs. Riemannian metrics are defined here **only as far as needed** — the general theory on
manifolds belongs to `c1-manifold-optimization` and `c5-manifold-estimation`.

| Symbol | Meaning |
|---|---|
| $\dot{x} = f(x,t)$ | $f$ is $C^1$ in $x$; no equilibrium is assumed to exist |
| $J(x,t) = \dfrac{\partial f}{\partial x}(x,t)$ | the Jacobian |
| $\delta x$ | virtual displacement — the difference of two neighbouring trajectories at the same time, $\dot{\delta x} = J\,\delta x$ |
| $M(x,t) \succ 0$ | the Riemannian metric; $\Theta$ is any factor with $M = \Theta^\top\Theta$ |
| $\dot{M}$ | total derivative along the trajectory, $\dfrac{\partial M}{\partial t} + \sum_i \dfrac{\partial M}{\partial x_i}\dot{x}_i$ |
| $\lVert \delta x\rVert_M$ | $\sqrt{\delta x^\top M \delta x}$ |
| $d_M(x,y)$ | Riemannian distance $\inf_\gamma \int_0^1 \lVert \gamma'(s)\rVert_{M(\gamma(s))}\,ds$ with $\gamma(0)=x$, $\gamma(1)=y$ |
| $\underline{m}, \overline{m}$ | uniform bounds $\underline{m}I \preceq M \preceq \overline{m}I$ |
| $\lambda$ | contraction rate |
| $W$ | dual metric $M^{-1}$ |

The running example is a **damped nonlinear pendulum-like system**:

$$
\dot{x}_1 = x_2, \qquad \dot{x}_2 = -2x_1 - 2x_2 - \sin x_1. \tag{1}
$$

The Jacobian is $J(x_1) = \begin{bmatrix}0 & 1\\ -2-\cos x_1 & -2\end{bmatrix}$, and since
$\cos x_1 \in [-1,1]$ it lies in the convex hull of the two vertices

$$
J_+ = \begin{bmatrix}0&1\\-3&-2\end{bmatrix}, \qquad
J_- = \begin{bmatrix}0&1\\-1&-2\end{bmatrix}. \tag{2}
$$

Both vertices have eigenvalues with real part $-1$ ($J_+$: $-1\pm i\sqrt2$; $J_-$: a double root
at $-1$). **And yet the Euclidean metric shows no contraction**:

$$
\lambda_{\max}(J_+^\top + J_+) = -2 + 2\sqrt2 \approx 0.8284271 > 0, \qquad
\lambda_{\max}(J_-^\top + J_-) = 0. \tag{3}
$$

That is, the distance can **grow transiently**. Equation (3) is why changing the metric is the
essential step.

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (contraction condition and exponential convergence) [D3]** — on a forward-invariant,
  geodesically convex region $\mathcal{X}$ where $\underline{m}I \preceq M \preceq \overline{m}I$
  and
  $$
  \dot{M} + J^\top M + M J \preceq -2\lambda M, \tag{4}
  $$
  any two trajectories in the region satisfy
  $d_M(x(t),y(t)) \le d_M(x(0),y(0))\,e^{-\lambda t}$, and in the Euclidean distance
  $$
  \lVert x(t)-y(t)\rVert \le \sqrt{\overline{m}/\underline{m}}\;\lVert x(0)-y(0)\rVert\,e^{-\lambda t}. \tag{5}
  $$
  The system is **incrementally exponentially stable**.
- **R2 (choosing the metric = an LMI) [D2]** — restricting $M$ to be constant makes (4) linear in
  $M$, and if $J$ lies in a polytope $\operatorname{conv}\{J_1,\dots,J_V\}$ it suffices to check
  **the vertices**. For (1), bisecting on $\lambda$ gives $\lambda^\star \approx 0.4913$, and at
  $\lambda = 0.4814$ the metric
  $$
  M = \begin{bmatrix}3.865360 & 1.876934\\ 1.876934 & 2.229473\end{bmatrix},
    \qquad \lambda_{\min}(M)=1,\ \lambda_{\max}(M) = 5.094833 \tag{6}
  $$
  satisfies (4) (the largest eigenvalue of the LMI residual at both vertices is
  $\approx 3\cdot10^{-11}$).
- **R3 (the disturbance tube) [D2]** — for a disturbed trajectory $\dot x = f(x,t)+d(t)$ against a
  nominal one $\dot y = f(y,t)$,
  $$
  d_M(x(t),y(t)) \le d_M(x(0),y(0))\,e^{-\lambda t} + \frac{1}{\lambda}\sup_{s\le t}\lVert \Theta\, d(s)\rVert, \tag{7}
  $$
  so the contraction rate **is** the inverse of the disturbance gain. The asymptotic tube radius is
  $\sup\lVert\Theta d\rVert/\lambda$.
- **R4 (control contraction metrics, CCM) [D2]** — for $\dot x = f(x) + B(x)u$, the condition for a
  metric that makes every trajectory trackable becomes, after projecting onto the orthogonal
  complement of $B$, **convex** in the dual metric $W = M^{-1}$:
  $$
  B_\perp^\top\!\left(-\dot{W} + \frac{\partial f}{\partial x}W + W\frac{\partial f}{\partial x}^\top + 2\lambda W\right)\!B_\perp \preceq 0. \tag{8}
  $$
  That the CLF search is non-convex while the CCM search is convex is the point of
  Manchester & Slotine.
- **R5 (contraction $\Rightarrow$ a unique equilibrium) [D1]** — a time-invariant system that
  contracts on a forward-invariant region has **at most one** equilibrium there. So a system with
  two or more equilibria ($\dot x = x - x^3$, say) contracts in no metric on that region.

## Derivation

### R1 — from virtual displacements to exponential convergence

**Step 1 (dynamics of a virtual displacement).** The difference $\delta x$ of two neighbouring
trajectories at the same time obeys the variational equation

$$
\dot{\delta x} = J(x,t)\,\delta x \tag{9}
$$

(from differentiability of solutions in the initial condition). Here $x(t)$ is the **actual
trajectory** and $J$ is evaluated along it — that "along the trajectory" is the difference between
linearisation and contraction.

**Step 2 (differentiating the length measured in the metric).** Differentiate
$V := \delta x^\top M(x,t)\,\delta x$. Since $M$ depends on $x$ and $t$, the total derivative
$\dot M$ appears:

$$
\dot{V} = \delta x^\top \dot{M}\delta x + 2\,\delta x^\top M \dot{\delta x}
  = \delta x^\top\big(\dot{M} + J^\top M + MJ\big)\delta x. \tag{10}
$$

(Insert (9) in the second term and symmetrise using
$\delta x^\top MJ\delta x = \delta x^\top J^\top M\delta x$.) With (4), $\dot V \le -2\lambda V$,
hence

$$
\lVert \delta x(t)\rVert_M \le \lVert \delta x(0)\rVert_M\,e^{-\lambda t}. \tag{11}
$$

**Step 3 (from infinitesimal to finite distance).** (11) is about infinitesimal displacements. To
lift it to two finite points, pick a path and measure its length. Take a smooth path
$\gamma_0(s)$ joining $x(0)$ and $y(0)$, and let $\gamma_t(s)$ be the trajectory started from
$\gamma_0(s)$. Then $\partial\gamma_t/\partial s$ is, at each $s$, a virtual displacement
satisfying (9), so (11) applies pointwise and

$$
L(t) := \int_0^1 \left\lVert \frac{\partial \gamma_t}{\partial s}(s)\right\rVert_{M(\gamma_t(s),t)} ds
  \le e^{-\lambda t}\int_0^1 \left\lVert \frac{\partial \gamma_0}{\partial s}(s)\right\rVert_{M(\gamma_0(s),0)} ds
  = e^{-\lambda t} L(0). \tag{12}
$$

The Riemannian distance is the infimum of path lengths, so $d_M(x(t),y(t)) \le L(t)$, and taking
$\gamma_0$ to be a geodesic gives $L(0) = d_M(x(0),y(0))$. Chaining the two inequalities gives the
first conclusion of R1. (This is where $\mathcal{X}$ must be **geodesically convex** — if the path
$\gamma_t$ leaves the region, we are not entitled to use (4). Technical step omitted: existence of
geodesics and smoothness of $\gamma_t$, Lohmiller & Slotine §3.)

**Step 4 (to the Euclidean distance).** From $\underline{m}I\preceq M\preceq\overline{m}I$ we get
$\sqrt{\underline{m}}\lVert u\rVert \le \lVert u\rVert_M \le \sqrt{\overline{m}}\lVert u\rVert$,
and lifting that to path lengths gives
$\sqrt{\underline{m}}\lVert x-y\rVert \le d_M(x,y) \le \sqrt{\overline{m}}\lVert x-y\rVert$. Hence

$$
\lVert x(t)-y(t)\rVert \le \frac{d_M(x(t),y(t))}{\sqrt{\underline{m}}}
  \le \frac{e^{-\lambda t}}{\sqrt{\underline{m}}}d_M(x(0),y(0))
  \le \sqrt{\frac{\overline{m}}{\underline{m}}}\;\lVert x(0)-y(0)\rVert e^{-\lambda t},
$$

which is (5). The **condition number** of the metric becomes the overshoot factor of the
transient — for (6) it is $\sqrt{5.094833/1} \approx 2.2572$.

**Where the assumptions break**: ⓐ without $\overline{m}$ (a metric that grows without bound in
some direction) the factor in (5) is meaningless — the Riemannian distance still shrinks but the
Euclidean conclusion is lost. ⓑ if the region is not geodesically convex, the path of step 3 can
leave the set where the condition holds, and two trajectories can each be in a contracting region
without contracting towards each other. ⓒ contraction is a **relative** property: trajectories
approaching one another is compatible with both diverging. Boundedness must be shown separately.

### R2 — finding a constant metric by LMI (and why Euclidean fails)

Start with an example that can be done by hand. Put
$J = \begin{bmatrix}-1 & k\\ 0 & -1\end{bmatrix}$ (with $k$ large) and the diagonal metric
$M = \operatorname{diag}(1, m)$ into (4). With $\dot M = 0$,

$$
J^\top M + MJ + 2\lambda M
  = \begin{bmatrix}-2+2\lambda & k\\ k & -2m + 2\lambda m\end{bmatrix} \preceq 0
$$

and the conditions for a $2\times2$ symmetric matrix to be negative semidefinite (non-positive
diagonal, non-negative determinant) give

$$
(2-2\lambda)(2m-2\lambda m) \ge k^2
  \quad\Longleftrightarrow\quad m \ge \frac{k^2}{4(1-\lambda)^2}. \tag{13}
$$

So for any $\lambda < 1$ a large enough $m$ **always certifies** contraction: for $k = 10$ and
$\lambda = 0.5$, $m \ge 100$. In the Euclidean metric ($m=1$), by contrast, the symmetric part
$\begin{bmatrix}-1 & k/2\\ k/2 & -1\end{bmatrix}$ has eigenvalues $-1 \pm k/2$, so for $k>2$ there
is a positive eigenvalue and **no contraction rate at all** is obtained. The same system contracts
or not depending on the metric — contraction is not a coordinate-dependent property but one
**asserted together with a metric**.

Now back to (1). Since $J$ is affine in $\cos x_1$, for constant $M$ condition (4) is
**equivalent** to the two LMIs at the vertices (2) (negative semidefiniteness is preserved by
convex combination). So solve

$$
\max_{\lambda,\,M} \lambda \quad\text{s.t.}\quad M \succeq I,\quad
  J_\pm^\top M + MJ_\pm + 2\lambda M \preceq 0 \tag{14}
$$

by bisection on $\lambda$ with an SDP at each step (fixing $\lambda$ makes it linear in $M$).
Numerically $\lambda^\star \approx 0.4913$, and at $\lambda = 0.4814$ one gets the $M$ of (6).
**The measured convergence rate is about $1.00$** (over 60 random trajectory pairs: median
1.0003, minimum 0.9760, maximum 1.0258), so the certificate is **about 2.08 times conservative**.
There are three sources: ⓐ the metric was restricted to be constant, ⓑ the whole range of
$\cos x_1$ was covered by vertices (real trajectories hardly visit those corners), and ⓒ the
condition was demanded for all directions of $\delta x$ at once. ⓐ can be reduced with a
state-dependent metric (SOS) and ⓑ by narrowing the region — the extension of the reproduction
task.

**Where the assumptions break**: the vertex argument needs $J$ to be **affine in a parameter**
confined to a polytope. If $J$ depends nonlinearly on $x$ (through $x_1^2$, say) the vertex set is
conservative or not bounded at all. Then one must go to state-dependent metrics with SOS, and the
degree gaps and numerical problems of R5 in `c3-lyapunov-stability` return.

### R3 — the tube made by a disturbance

Compare $\dot x = f(x,t) + d(t)$ with $\dot y = f(y,t)$. Use the path argument of step 3, but now
the disturbance enters at one end of the path, so the derivative of the length picks up an extra
term. With $R(t) := d_M(x(t),y(t))$ (absolutely continuous and differentiable almost everywhere),

$$
\dot{R} \le -\lambda R + \lVert \Theta(x,t)\,d(t)\rVert. \tag{15}
$$

(Derivation: applying (10) along the geodesic gives the $-\lambda$ term, and the velocity $d$ added
at the endpoint contributes at most $\lVert\Theta d\rVert$ to the rate of change of length, by
Cauchy-Schwarz. Omitted: the differential-inclusion treatment when the geodesic is not unique —
Lohmiller & Slotine §3, Tsukamoto et al. §2.4.)

Applying the comparison lemma to (15),

$$
R(t) \le R(0)e^{-\lambda t} + \int_0^t e^{-\lambda(t-s)}\lVert\Theta d(s)\rVert\,ds
     \le R(0)e^{-\lambda t} + \frac{1-e^{-\lambda t}}{\lambda}\sup_{s\le t}\lVert\Theta d(s)\rVert, \tag{16}
$$

which is (7). **Numerical check**: for (1) with the metric (6) and a square-wave disturbance
$\lvert d\rvert \le \delta$ on the second channel, over 20 random pairs the maximum of the ratio
$R(t)/\text{bound}(t)$ in (7) is 0.99984 for $\delta=0.1$ and 0.99927 for $\delta=0.5$ — **the
bound is never exceeded**. The asymptotic tube radii $\sup\lVert\Theta d\rVert/\lambda$ are 0.3101
and 1.5507.

That equation is the main reason contraction theory is used in robotics. Raising $\lambda$ narrows
the tube, and a narrower tube lets the planner leave smaller clearances — the design collapses
onto one axis: convergence rate ↔ clearance ↔ control effort.

**Where the assumptions break**: if $\Theta$ depends on the state, $\sup\lVert\Theta d\rVert$ must
be a bound over the **whole region**, and a wide region inflates the tube quickly. Also (7) assumes
a bounded disturbance, so it does not apply as-is to stochastic ones (stochastic contraction
theory uses separate results).

### R4 — why the CCM condition becomes convex in the dual metric

With control, $\dot x = f(x) + B(x)u$, the virtual displacement obeys
$\dot{\delta x} = (A(x,u) + B\,\partial u/\partial x)\delta x + B\,\delta u$ with
$A := \partial(f+Bu)/\partial x$. The point is that **the directions $\delta u$ can pull are the
range of $B$**. So the question "can some feedback make this contract?" needs a condition only in
the directions $B$ **cannot** pull:

$$
\delta x^\top M B = 0 \;\Longrightarrow\;
  \delta x^\top\big(\dot M + A^\top M + MA + 2\lambda M\big)\delta x \le 0. \tag{17}
$$

(17) is **conditional** and mixes $M$ with $\delta x$, so it is not convex as written. Changing to
$W := M^{-1}$ is Manchester & Slotine's move. Substituting $\delta x = M^{-1}\eta = W\eta$ turns the
condition $\delta x^\top MB = 0$ into $\eta^\top B = 0$, which is **independent of the metric**,
and the quadratic form of (17) becomes (8), with the sign of the $\dot{W}$ term flipped:

$$
B_\perp^\top\!\left(-\dot W + \frac{\partial f}{\partial x}W + W\frac{\partial f}{\partial x}^\top + 2\lambda W\right)\!B_\perp \preceq 0.
$$

(The sign flips because $\frac{d}{dt}(M^{-1}) = -M^{-1}\dot M M^{-1}$. The terms of $A$ that depend
on $u$ lie in the range of $B$ and vanish against $B_\perp$ — omitted: the expansion in
Manchester & Slotine Thm 1.) Equation (8) is **linear** in $W$, so writing $W$ as a linear
combination of basis functions makes it searchable by SOS or SDP. Contrast the CLF search: a CLF
requires "there exists a $u$" jointly in $V$ and $u$, while a CCM eliminates that existence in
advance through the $B_\perp$ projection.

**Where the assumptions break**: (8) assumes no input constraints. With
$\lvert u\rvert \le u_{\max}$, the feedback obtained by integrating along the geodesic can
saturate, and the guarantee weakens to a local one. (8) also requires **uniform** bounds on $W$, so
finding a $W$ valid on a wide region forces a lower rate — the conservatism of R2 reappears
throughout the design.

## Proof sketch

### R5 — contraction implies at most one equilibrium

**Hypotheses** H1: time-invariant $\dot x = f(x)$. H2: (4) holds with $\lambda>0$ and a uniformly
bounded $M$ on a forward-invariant, geodesically convex $\mathcal{X}$.
**Conclusion** C: $\mathcal{X}$ contains at most one equilibrium.

**Strategy**: an equilibrium is a constant trajectory. The distance between two constant
trajectories does not change, while R1 says it decays exponentially — a contradiction.

1. Suppose $x^\star \ne y^\star$ are both equilibria. The trajectories from them are
   $x(t)\equiv x^\star$ and $y(t)\equiv y^\star$.
2. R1 gives $d_M(x^\star,y^\star) = d_M(x(t),y(t)) \le d_M(x^\star,y^\star)e^{-\lambda t}$.
3. As $t\to\infty$ the right side goes to zero while the left is the constant
   $d_M(x^\star,y^\star) > 0$ (since $M \succeq \underline{m}I$, the Riemannian distance between
   distinct points is positive). Contradiction.
4. Hence at most one equilibrium. Getting existence as well needs boundedness and compactness
   (for instance Brouwer's fixed point theorem on a compact forward-invariant $\mathcal{X}$).

**Remove a hypothesis**: dropping **geodesic convexity** in H2 can make the conclusion false.
$\dot x = x - x^3$ contracts locally near $x=\pm1$ (where $f'(\pm1) = -2$), but a path joining the
two regions passes through $x=0$, where $f'(0)=+1>0$, so there is no contraction on the whole
region — and the existence of three equilibria proves it. **This is the real cost of contraction
theory**: global contraction is a very strong demand, and on systems with several equilibria (most
robot tasks) the claim has to be made region by region.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R2)** Derive (13) and say how the required $m$ diverges as
$\lambda \to 1^-$. What price does that divergence charge in the factor
$\sqrt{\overline m/\underline m}$ of (5)?
*Solution sketch*: use the negative semidefiniteness conditions of a $2\times2$ symmetric matrix
(non-positive diagonal, non-negative determinant). Since
$m \sim k^2/4(1-\lambda)^2 \to \infty$, the factor grows like $k/2(1-\lambda)$ — **a certificate
with a higher rate makes the bound on the transient correspondingly worse.**

**P2 (derivation, ★★, R3)** Derive the second inequality of (16) directly (multiply by the
integrating factor $e^{\lambda t}$) without invoking the comparison lemma. When $\Theta$ depends on
the state, at which step is a bound over the whole region needed?
*Solution sketch*: integrate
$\frac{d}{dt}(e^{\lambda t}R) \le e^{\lambda t}\lVert\Theta d\rVert$. Since $\Theta$ is evaluated
at $x(s)$, using the bound without knowing where the trajectory goes requires a region-wide bound.

**P3 (numerical, ★, R1·R2)** For (1), find ⓐ the two eigenvalues in (3), ⓑ whether the $M$ of (6)
satisfies (4) at both vertices with $\lambda = 0.4814$, ⓒ the factor in (5).
*Answers*: ⓐ $-2+2\sqrt2 = 0.8284271$ and $0$ (tolerance $10^{-6}$) — neither is negative, so the
Euclidean metric certifies no contraction. ⓑ the largest eigenvalue of both LMIs is
$\le 10^{-8}$ (the reference implementation gets $3\cdot10^{-11}$). ⓒ
$\sqrt{5.094833} = 2.2571738$ (tolerance $10^{-6}$).

**P4 (implementation, ★★★, R2·R4)** Solve (14) by bisection plus SDP to reproduce
$\lambda^\star$, then extend to a **state-dependent** metric of the form
$M(x_1) = M_0 + M_1\cos x_1$ and see whether $\lambda$ improves. Do not forget the $\dot M$ term —
$\dot M = -M_1 \sin x_1\,\dot x_1 = -M_1 x_2\sin x_1$, so $x_2$ must be restricted to a bounded
range for the condition to be an LMI.
*Rubric*: ⓐ reproduces $\lambda^\star = 0.4913 \pm 0.002$ for the constant metric ⓑ the
state-dependent result is no worse than the constant one (equal or better) ⓒ the $\dot M$ term and
the boundedness assumption on $x_2$ are **stated** in the code and the report ⓓ if there is no
improvement, analyses why (which vertex binds).

**P5 (counterexample, ★★, R1·R5)** Refute the claim that "asymptotic stability implies contraction
in some metric", with ① a system with several equilibria and ② a system with a single equilibrium
that contracts in no **constant** metric.
*Property checklist*: ① something like $\dot x = x - x^3$ with three equilibria (R5 concludes it
at once). ② an example where no constant metric satisfies (4) on the region — for instance one
vertex of $J(x)$ being unstable (an eigenvalue with positive real part) makes the constant-metric
LMI infeasible. Showing that such a system can still be asymptotically stable (trajectories do not
dwell in that region) completes the answer.

**P6 (paper, ★★, R4)** Read Manchester & Slotine 2017 and write, in three sentences each, ⓐ what
exactly is convex and in which variable, ⓑ which non-convexity of the CLF search that convexity
avoids, ⓒ how the guarantees weaken with input constraints and disturbances.
*Rubric*: naming "linear in the dual metric $W=M^{-1}$, with the existence of $u$ eliminated by the
$B_\perp$ projection" passes. Adding "optimising $W$ and $\lambda$ jointly is non-convex again"
earns extra credit.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read in three passes and attack questions 4, 5, 6, 7 in the third.

1. **Lohmiller & Slotine, "On contraction analysis for non-linear systems" (1998, Automatica)**
   — role: `seminal`. <https://doi.org/10.1016/S0005-1098(98)00019-3>
   §2 is the basic form of R1; §3 is general metrics and coordinate changes.
   Extra questions: ⓐ Where do the authors separate contraction from Lyapunov analysis — which
   assumption did they **drop**? ⓑ Do their results give **boundedness** of trajectories?
2. **Manchester & Slotine, "Control contraction metrics: convex and intrinsic criteria for
   nonlinear feedback design" (2017, IEEE T-AC; arXiv 2015)** — role: `standard`.
   <https://arxiv.org/abs/1503.03144>
   Extra questions: ⓐ What invariance does "intrinsic" refer to? ⓑ What computation does an
   implementation that integrates the feedback along a geodesic demand in real time?
3. **Tsukamoto, Chung & Slotine, "Contraction theory for nonlinear stability analysis and
   learning-based control: a tutorial overview" (2021, Annual Reviews in Control)**
   — role: `survey`. <https://arxiv.org/abs/2110.00675>
   Extra questions: ⓐ Does a learned (neural) contraction metric guarantee something about the
   learned model or about the real system — and where is that gap closed? ⓑ Which of the open
   problems the survey lists can be measured with the reproduction task of this lesson?

**The ten fixed questions**: (1) which problem under which assumptions (2) what exactly earlier
work could not do (3) the core idea in one equation (4) what is guaranteed and **what is not**
(5) independent and dependent variables and baselines, fairly tuned (6) do the metrics match the
claim, are variance and seeds reported (7) what is missing for reproduction (8) the first
assumption to doubt if the result is wrong (9) computational and memory complexity and real-time
feasibility (10) what you would change to go beyond it in a year.

## Reproduction task

**Tier R1 (numerical check).** Budget: laptop CPU under one minute (batching the trajectory pairs
into arrays and integrating them at once is enough), numpy plus scipy plus one SDP solver. The
system is (1) and there is no input data.

> Design note: the original wording in the blueprint was "whether the upper bound on the
> convergence rate given by the contraction metric exceeds the actual rate". A certified $\lambda$
> bounds the **distance** from above and the actual rate from **below**, so what follows is that
> statement rewritten in the correct direction (every number below was produced by running it).

**Acceptance criteria (all four)**

1. **Euclidean failure and the certificate**: reproduce both values of (3) to within $10^{-6}$
   ($0.8284271$ and $0$), and find $\lambda \ge 0.48$ with $M \succeq I$ by bisection plus SDP. The
   $(M,\lambda)$ found must satisfy
   $\lambda_{\max}(J^\top M + MJ + 2\lambda M) \le 10^{-8}$ not only at the two vertices but at
   **every** one of $10^4$ values of $x_1$ drawn uniformly from $[-\pi,\pi]$.
2. **Pairwise bound**: integrate $10^3$ random trajectory pairs from $[-3,3]^2$ with RK4
   ($\Delta t \le 2\cdot10^{-3}$, $T=12$) and check, for every pair at every time,
   $d_M(x(t),y(t)) \le d_M(x(0),y(0))e^{-\lambda t}\,(1+10^{-6})$.
   (The metric is constant, so $d_M(x,y) = \lVert\Theta(x-y)\rVert$.)
3. **Measuring the conservatism**: over the same pairs, the median measured rate
   $\hat\lambda = -\ln\!\big(d_M(T)/d_M(0)\big)/T$ is $1.00 \pm 0.05$ and its minimum exceeds
   $\lambda$. Report the ratio $\hat\lambda_{\text{median}}/\lambda$ (reference: 2.08).
4. **The tube bound**: add a disturbance $\lvert d\rvert \le \delta$ on the second channel (a square
   wave or random switching) and check (7) for $\delta \in \{0.1, 0.5\}$ at every time over $10^2$
   random pairs ($R/\text{bound} \le 1+10^{-6}$). Report the asymptotic tube radius
   $\sup\lVert\Theta d\rVert/\lambda$ (reference: $0.3101$ and $1.5507$).

**Baselines**: ⓐ the Euclidean metric ($M=I$), which must **fail** criterion 1 (no certificate);
ⓑ the measured rate $\approx 1.00$ — the certified value must be below it (criterion 3), and if it
is above, the LMI or the distance computation is wrong; ⓒ the reference numbers
$\lambda^\star \approx 0.4913$, the $M$ of (6), and $\sqrt{\overline m/\underline m} = 2.2572$.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| The certified $\lambda$ exceeds the measured rate | the distance was measured as $\lVert x-y\rVert$, dropping $\Theta$ | run with $M=I$ and see whether criterion 1 fails — if it does not, the sign of the LMI is flipped |
| The SDP calls every $\lambda$ feasible | there is no normalisation such as $M \succeq I$, so $M \to 0$ degenerates | print $\lambda_{\min}(M)$ of the solution and the LMI residual directly |
| Criterion 2 fails only for very large initial distances | the vertex cover is invalid outside the region (here it is global, so integration error is more likely) | halve $\Delta t$ and see whether the violation disappears |
| The ratio in criterion 4 slightly exceeds 1 | $\sup\lVert\Theta d\rVert$ was computed from the component size rather than the disturbance vector | compute $\lVert\Theta(0,\delta)^\top\rVert$ by hand and compare |
| The state-dependent metric of P4 is infeasible | the $\dot M$ term was dropped, or $x_2$ was not bounded | set $M_1 = 0$ and check that the constant-metric result comes back |

## Open problems

- **(open problem) How to find the metric — and what a learned metric guarantees** — searching for a
  state-dependent metric is expensive in the dimension with SOS, and with a neural network the
  guarantee weakens to one about the learned model. Current approaches: the neural contraction
  metrics of [Tsukamoto & Chung 2020](https://arxiv.org/abs/2006.04361), the certified control
  learning of [Sun, Jha & Fan 2020](https://arxiv.org/abs/2011.12569), and dynamics learned with
  contraction-based regularisation in [Singh et al. 2019](https://arxiv.org/abs/1907.13122). The
  gap: an explicit map from learning error to lost contraction rate.
- **(open problem) The conservatism of certificates** — the measurement in this lesson is itself an
  open problem: of the factor-of-two gap between the $\lambda=0.49$ obtained from a constant metric
  with a vertex cover and the measured $1.00$, there is no general way to say **which part is
  intrinsic and which is a limitation of the technique**. The gap: an upper bound on the best
  achievable contraction rate for a given system (a proof that "no better metric exists").
- **(open problem) Contraction for systems with contact and impact** — when the state jumps at an
  impact the virtual displacement is discontinuous and (9) becomes meaningless. The condition that
  the Jacobian of the reset map be non-expansive in the metric is known, but using it as a **design**
  condition on walking or manipulation systems whose contact mode changes is not established. The
  same wall appears in `c2-contact-dynamics` and `s3-legged-underactuated`.
- **(open problem) Trading contraction rate against control effort** — (7) says raising $\lambda$
  narrows the tube, but the feedback that raises $\lambda$ raises the input. There is no theory
  giving the **Pareto frontier** of achievable (rate, tube radius) pairs under input limits.
  `c4-mpc` handles the same trade in the language of tube MPC.

## Concept check

Take it with `rc quiz c3-contraction-incremental`. The quiz is **for concept checking only**; the
real work is the problem set and the reproduction task above (`lesson-standard.md` §4). Four
questions ask: what it means that the symmetric part of the Jacobian is not negative definite even
though the eigenvalues have real part $-1$; the asymptotic tube radius in terms of $\lambda$ and the
disturbance bound; whether a contracting time-invariant system can have several equilibria; and why
the CCM condition becomes convex in the dual metric.

## How to study this stage

1. **Write (10) three times (30 min)** — expand
   $\dot V = \delta x^\top(\dot M + J^\top M + MJ)\delta x$ by hand three times. The one trap is
   that $\dot M$ is a **total** derivative (for a state-dependent metric the
   $\partial M/\partial x_i \dot x_i$ terms survive).
2. **See the Euclidean metric fail first (30 min)** — compute (3) yourself. Seeing eigenvalues at
   $-1$ together with a positive eigenvalue in the symmetric part is what makes "search for a
   metric" feel like real work.
3. **Get the feel from the metric you can do by hand (40 min)** — derive (13) and check
   $m\ge100$ for $k=10$, $\lambda=0.5$. Solving P1 shows the trade between rate and transient
   sitting in a single formula.
4. **Run the LMI yourself (90 min)** — pass criterion 1 of the reproduction task first. The point is
   to see in code that each bisection step is an SDP (fixing $\lambda$ makes it linear).
5. **Meet conservatism as a number (60 min)** — run criteria 2 and 3 and look at the gap between the
   certified $0.49$ and the measured $1.00$. **Certificates are conservative** has to be felt as a
   number before you can expect the same property in the next lesson (passivity) and in CBFs.
6. **Read the papers for "the assumption they dropped" (150 min)** — Lohmiller & Slotine dropped the
   equilibrium, Manchester & Slotine dropped non-convexity through the $B_\perp$ projection, and
   Tsukamoto et al. tie both threads to learning. The one-page note per paper is **mandatory**.
7. **The bridge to the next lesson (20 min)** — contraction compares trajectories. But when a robot
   **touches its environment**, the counterpart is not a trajectory but another system exchanging
   energy. That viewpoint is `c3-passivity-impedance`.

**Passing bar**: you can derive (10)-(12) and (16) from memory, explain numerically why the
Euclidean metric fails for (1), and you have code meeting all four acceptance criteria plus
one-page notes on the three papers.
