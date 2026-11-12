---
id: c2-dynamics-derivatives-sysid
lang: en
title: Derivatives of dynamics and inertial parameter identification
summary: >-
  Build the regressor $\tau = Y\pi$ from the fact that inverse dynamics is linear in the inertial
  parameters, and treat the structurally unidentifiable subspace and the base parameters at the
  level of proof. Show that physical consistency is an LMI on the pseudo-inertia matrix and
  decompose numerically the finding that the unidentifiable directions are exactly where
  consistency lives; ends at why analytical derivatives of RNEA beat automatic differentiation.
objectives:
  - Write the spatial inertia as linear in ten parameters and construct the regressor $Y$ from RNEA calls.
  - Prove that a state-independent null space exists and explain why the number of base parameters saturates.
  - State the equivalence of positive definiteness of the pseudo-inertia with physical realisability and show that it is an LMI.
  - Derive $\partial\tau/\partial\ddot{q} = M(q)$ and say why analytical derivatives beat automatic differentiation and finite differences.
  - Decompose numerically how the identification error depends on noise and conditioning, and state the goal of excitation trajectory design.
tags: [multibody-dynamics, system-identification, derivatives, lmi, sdp, conditioning, research]
---

# Derivatives of dynamics and inertial parameter identification

## Setup and notation

The results of `c2-rnea-inverse-dynamics` and `c2-crba-aba` are assumed, in particular RNEA, CRBA,
$M = \sum_k J_k^\top I_kJ_k$ and the block structure of the spatial inertia ((4) of the module's
first lesson). This lesson closes the module — its subject is **where the model comes from**, and
all five preceding lessons dealt with "given the inertial parameters".

| Symbol | Meaning |
|---|---|
| $\pi_i \in \mathbb{R}^{10}$ | The inertial parameters of body $i$: $(m,\; h^\top,\; I_{Oxx}, I_{Oxy}, I_{Oxz}, I_{Oyy}, I_{Oyz}, I_{Ozz})$ |
| $h := mc \in \mathbb{R}^3$ | The first mass moment. Using $h$ rather than $c$ is **the key to linearity** |
| $I_O$ | The rotational inertia about the **frame origin** (not $\bar I_C$ about the centre of mass) |
| $\pi \in \mathbb{R}^{10n}$ | The full parameter vector $(\pi_1; \dots; \pi_n)$ |
| $Y(q,\dot q,\ddot q) \in \mathbb{R}^{n\times 10n}$ | The regressor: $\tau = Y\pi$ |
| $\mathcal{N}$ | The structurally unidentifiable subspace, $\mathcal{N} = \{\pi : Y(\cdot)\pi \equiv 0\}$ |
| $n_b := 10n - \dim\mathcal{N}$ | The number of **base parameters** |
| $V_{\mathrm{id}}, V_{\mathrm{null}}$ | Orthonormal bases of the identifiable subspace and of $\mathcal{N}$ |
| $P(\pi_i) \in \mathbb{R}^{4\times4}$ | The **pseudo-inertia** matrix; linear in $\pi_i$ |
| $\sigma$ | The standard deviation of the torque measurement noise |
| $\kappa$ | The condition number on the identifiable subspace, $S_1/S_{n_b}$ |

Assumptions and scope: a kinematic tree, rigid bodies, and no joint friction or compliance in the
model (they dominate the error on a real robot but have different parameters and break the
linearity — an open problem). Every number is obtained with numpy alone and no simulator;
trajectories are replaced by random state samples (real excitation-trajectory design is R5).

**Why $h = mc$ rather than $c$**, first. The spatial inertia is **nonlinear** in
$(m, c, \bar I_C)$ — the term $m\hat c\hat c^\top$ is quadratic in $c$. In $(m, h, I_O)$ it is
completely **linear**. That single reparameterisation turns identification into linear least
squares, and the whole of this lesson follows from it.

## Key results

The bracketed grade is the derivation depth (D0 cited / D1 sketched / D2 full derivation /
D3 proof — see `lesson-standard.md` §2 in the track design notes).

- **R1 (linearity in the inertial parameters) [D2]** — the spatial inertia
  $$
  I(\pi_i) = \begin{bmatrix} I_O & \hat h \\ \hat h^\top & m\,\mathbb{1}_3\end{bmatrix} \tag{1}
  $$
  is **linear** in $\pi_i$, and RNEA is linear in each $I_i$ (the force recursion
  $f_i = I_ia_i + (v_i\times^{*})I_iv_i + \sum {}^iX_j^{*}f_j$ is affine in $I$ with every $I$ term
  of first degree), so in the end
  $$
  \tau = Y(q,\dot q,\ddot q)\,\pi, \qquad Y \text{ independent of } \pi. \tag{2}
  $$
  The $k$-th column of $Y$ is **one RNEA call with $\pi = e_k$** — the shortest and most
  verifiable construction (cost: $10n$ RNEA calls, that is $\Theta(n^2)$).
- **R2 (structural unidentifiability and base parameters) [D3]** —
  $$
  \mathcal{N} := \big\{\pi \;:\; Y(q,\dot q,\ddot q)\,\pi = 0 \ \ \forall (q,\dot q,\ddot q)\big\}
  $$
  is a **state-independent subspace**, and torque data alone can **never** distinguish directions
  in $\mathcal{N}$. The rank of a stacked regressor **saturates** at
  $n_b = 10n - \dim\mathcal{N}$ after finitely many generic samples (because the entries of $Y$ are
  analytic). Measured on the 7-DOF reference arm,
  $$
  n_b = 43, \qquad \dim\mathcal{N} = 27 \quad (10n = 70),
  $$
  with the singular values **dropping twelve orders** from $5.22$ to $1.9\times10^{-14}$. With
  gravity off, $n_b$ falls to $39$ — four directions are revealed **by gravity alone**.
- **R3 (physical consistency is an LMI) [D2]** — $\pi_i$ being **realisable by a positive mass
  density** is equivalent to positive definiteness of the pseudo-inertia matrix
  $$
  P(\pi_i) = \begin{bmatrix} \tfrac{1}{2}\operatorname{tr}(I_O)\,\mathbb{1}_3 - I_O & h \\ h^\top & m \end{bmatrix} \;\succ\; 0. \tag{3}
  $$
  Since $P$ is **linear** in $\pi_i$, (3) is an LMI and the identification problem becomes the
  **SDP** $\min_\pi \lVert A\pi - b\rVert^2$ subject to $P(\pi_i) \succeq 0$. The constraint is
  **strictly stronger** than $I_O \succ 0$ together with the triangle inequalities.
- **R4 (analytical derivatives) [D2; the full recursion is D1]** — since $\tau$ is affine in
  $\ddot q$,
  $$
  \frac{\partial\tau}{\partial\ddot q} = M(q) \tag{4}
  $$
  holds **exactly** (CRBA *is* this Jacobian). $\partial\tau/\partial q$ and
  $\partial\tau/\partial\dot q$ can also be obtained in **$\Theta(n^2)$** by pushing
  $\partial v_i/\partial\cdot$ and $\partial a_i/\partial\cdot$ through the same recursions, an
  order of magnitude faster than automatic differentiation — the reason being that, because the
  motion and force transforms obey different rules, the AD graph produces redundant work (the
  second open problem of the module's first lesson). **[D1]**
- **R5 (noise, conditioning and excitation trajectories) [D2]** — the error on the identifiable
  subspace is **linear** in the noise, with the conditioning setting the constant. Measured on the
  7-DOF reference arm (30 samples = 210 equations, $\kappa = 25.39$),
  $$
  \lVert V_{\mathrm{id}}^\top(\hat\pi - \pi)\rVert = 9.92\times10^{-4},\ 9.92\times10^{-3},\ 9.92\times10^{-2}
  \quad (\sigma = 10^{-3},\ 10^{-2},\ 10^{-1}),
  $$
  exactly $\propto\sigma$. The error along $\mathcal{N}$, by contrast, stays fixed at
  $\lVert V_{\mathrm{null}}^\top\pi\rVert = 4.7586$ **independently of $\sigma$** — it is never
  recovered. And yet **torque prediction is unharmed** (at $\sigma = 10^{-3}$ the prediction error
  at fresh states is $1.98\times10^{-3}$). The goal of excitation-trajectory design is to reduce
  $\kappa$; $\dim\mathcal{N}$ **cannot** be changed by a trajectory.

## Derivation

### R1 — linearity and the construction of the regressor

In the module's first lesson the spatial inertia was written in $(m, c, \bar I_C)$:
$I = \begin{bmatrix}\bar I_C + m\hat c\hat c^\top & m\hat c \\ m\hat c^\top & m\mathbb{1}\end{bmatrix}$.
The term $m\hat c\hat c^\top$ in the upper-left block is **quadratic** in $c$. But by the
parallel-axis theorem $I_O = \bar I_C + m\hat c\hat c^\top$ is the **inertia about the origin**, and
with $h = mc$ we have $m\hat c = \hat h$. Substituting both reparameterisations gives (1), in which
**every entry is of first degree in $\pi_i$**. $I_O$ is symmetric, so it has 6 independent
components, $h$ has 3 and $m$ has 1 — ten in all.

Now see that RNEA is linear in $\pi$. The forward pass ($v_i$, $a_i$) **does not depend on $\pi$
at all** — it is pure kinematics. The backward pass is

$$
f_i = \underbrace{I_i a_i}_{\text{1st degree in } \pi_i} + \underbrace{(v_i\times^{*})I_i v_i}_{\text{1st degree in } \pi_i}
  + \sum_{j\in\mu(i)}{}^iX_j^{*}f_j, \qquad \tau_i = S_i^\top f_i,
$$

and since $I_i$ is linear in $\pi_i$ both terms are of first degree in $\pi_i$. Sums of the
recursion are linear and the projection by $S_i^\top$ is linear, so the whole of $\tau$ is linear
in $\pi$ — that is (2). Gravity enters through $a_0 = -a_g$, which is also in the forward pass, so
it does not break the linearity (**the gravity term is inside $Y\pi$** — problem P1 (b)).

**Constructing the regressor.** Since (2) is linear, extract the columns one at a time: calling
RNEA with $\pi = e_k$ (the $k$-th parameter one, the rest zero) returns $Y_{\cdot k}$. The cost is
$10n$ RNEA calls, that is $\Theta(n^2)$, and the implementation is **three lines** (the core code
below). It is far shorter than the literature's route of expanding the entries of $Y$ by hand, and
above all it is **verified by reusing the RNEA of the previous lessons**:
$\lVert Y\pi - \tau\rVert$ must be at machine precision (measured $7.1\times10^{-15}$).

The "body" made by $\pi = e_k$ has zero mass or negative inertia and is **not physical**. That does
not matter — it is just extracting the columns of a linear map, and RNEA does not require physical
validity. (ABA, however, requires $d_i > 0$, so the same trick cannot be used there — R5 of the
previous lesson.)

### R3 — pseudo-inertia and physical consistency

Suppose $\pi_i$ came from **some positive mass density** $\rho(r) \ge 0$. Then

$$
m = \int \rho\,dV, \quad h = \int \rho\,r\,dV, \quad
I_O = \int \rho\,\big(\lVert r\rVert^2\mathbb{1} - rr^\top\big)dV.
$$

Extract the **second-moment matrix** $\Sigma := \int\rho\,rr^\top dV$. Since
$\operatorname{tr}(I_O) = \int\rho(3\lVert r\rVert^2 - \lVert r\rVert^2) = 2\int\rho\lVert r\rVert^2
= 2\operatorname{tr}\Sigma$,

$$
\Sigma = \operatorname{tr}(\Sigma)\mathbb{1} - I_O = \tfrac{1}{2}\operatorname{tr}(I_O)\,\mathbb{1} - I_O,
$$

which is the upper-left block of (3). Then

$$
P(\pi_i) = \int \rho(r)\begin{bmatrix} rr^\top & r \\ r^\top & 1\end{bmatrix}dV
= \int \rho(r)\begin{bmatrix} r \\ 1\end{bmatrix}\begin{bmatrix} r \\ 1\end{bmatrix}^\top dV,
$$

and since the integrand is **rank-one positive semidefinite** and $\rho \ge 0$, we get
$P \succeq 0$. If the mass is not concentrated on a plane (four points affinely spanning) then
$P \succ 0$. The converse (that $P \succeq 0$ implies a realisable density exists) follows by
eigendecomposing $P$ and realising it with **four point masses**, so (3) is an **equivalence**.
(Omitted: the details of the converse, in the realisability theorem of Wensing et al. 2018.)

**Why this is stronger than the triangle inequalities.** $I_O \succ 0$ and the triangle inequality
of the principal moments ($I_1 + I_2 \ge I_3$) are **necessary** conditions for (3).
$P \succeq 0$ ties in $h$ and $m$ as well, so it also contains conditions of the kind "the centre
of mass must lie inside the body". A common generator going wrong is a good example of this
(problem P2 (a) — and something this very module experienced; see the note in the reproduction
task).

**What "an LMI" means here.** $P(\pi_i)$ is **linear** in $\pi_i$, so
$\{\pi_i : P(\pi_i)\succeq0\}$ is convex (the linear preimage of the symmetric PSD cone). Hence

$$
\min_\pi \; \lVert A\pi - b\rVert_2^2 \quad \text{s.t.} \quad P(\pi_i) \succeq 0 \ \ (i = 1,\dots,n) \tag{5}
$$

is a **convex** problem, specifically an SDP. With the nonconvex parameterisation
$(m, c, \bar I_C)$ the same constraint is nonconvex, so the reparameterisation of R1 pays off
**twice** — in the linear regression and in the convex constraint.

### R4 — $\partial\tau/\partial\ddot q = M$

From the previous lessons, $\tau = M(q)\ddot q + b(q,\dot q)$ with $b$ independent of $\ddot q$. So
the Jacobian with respect to $\ddot q$ is $M(q)$ — that is (4). It is an **exact identity**, not an
approximation. Three things follow:

1. **Never compute $M$ twice.** If a trajectory optimiser wants
   $\partial\tau/\partial\ddot q$, call CRBA; conversely, if $M$ is wanted, RNEA can be called $n$
   times (R4-5 of the previous lesson). They are the same quantity.
2. **The affinity test is free.** $\tau(\ddot q_1 + \ddot q_2) - \tau(0) =
   [\tau(\ddot q_1) - \tau(0)] + [\tau(\ddot q_2) - \tau(0)]$ must hold at machine precision
   (measured $2.1\times10^{-14}$ in the previous lesson).
3. **A finite-difference trap.** With gravity off and $\dot q = 0$, $\tau = M\ddot q$ is
   **exactly linear**, so the central difference has zero truncation error and machine precision is
   reached for every $h$ (measured $4.4\times10^{-16}$). Turn gravity **on** and cancellation
   dominates, growing like $1/h$. That is why condition 2 of the previous lesson specifies gravity
   off.

$\partial\tau/\partial q$ and $\partial\tau/\partial\dot q$ are not free the way (4) is. The
strategy of analytical differentiation is to push the recursions of RNEA through **once more**:
propagate $\partial v_i/\partial q_k$ and $\partial a_i/\partial q_k$ with the recursions obtained
by differentiating (1) and (3) of the previous lesson, and feed them into the force recursion to
get $\partial\tau/\partial q_k$. Each $k$ costs a constant per body, so the total is
$\Theta(n^2)$ — **the same order** as finite differences ($n$ RNEA calls, $\Theta(n^2)$) but with
a smaller constant and, above all, **no truncation error**. Automatic differentiation is slower
because the motion and force transforms obey different rules and the graph produces redundant
work; Carpentier & Mansard 2018 measure that difference. **[D1]** (This lesson completes only (4)
at [D2] and hands the full recursion to that paper.)

### R5 — noise, conditioning, and what can be changed

Take a stacked regressor $A \in \mathbb{R}^{mn\times 10n}$ with measurements $b = A\pi + \varepsilon$,
$\varepsilon \sim \mathcal{N}(0, \sigma^2)$, and solve least squares **on the identifiable subspace
only**: $\hat\beta = \arg\min\lVert AV_{\mathrm{id}}\beta - b\rVert$,
$\hat\pi = V_{\mathrm{id}}\hat\beta$. From the normal equations,

$$
V_{\mathrm{id}}^\top(\hat\pi - \pi) = \big((AV_{\mathrm{id}})^\top AV_{\mathrm{id}}\big)^{-1}(AV_{\mathrm{id}})^\top\varepsilon,
$$

so the size of the error is **linear** in $\sigma$ with a constant set by the singular values of
$AV_{\mathrm{id}}$ — the direction of the smallest singular value is amplified most. The
measurements show exactly this (7 DOF, 30 samples, $\kappa = 25.39$):

| $\sigma$ | $\lVert V_{\mathrm{id}}^\top(\hat\pi - \pi)\rVert$ | $\lVert V_{\mathrm{null}}^\top(\hat\pi - \pi)\rVert$ | Torque prediction error at fresh states |
|---|---|---|---|
| $0$ | $3.2\times10^{-13}$ | $4.7586$ | $1.1\times10^{-13}$ |
| $10^{-3}$ | $9.92\times10^{-4}$ | $4.7586$ | $1.98\times10^{-3}$ |
| $10^{-2}$ | $9.92\times10^{-3}$ | $4.7586$ | $1.98\times10^{-2}$ |
| $10^{-1}$ | $9.92\times10^{-2}$ | $4.7586$ | $1.98\times10^{-1}$ |

How to read the three columns:

- The first is $\propto\sigma$ — it improves by reducing the noise, taking more samples, or
  reducing $\kappa$. **Excitation-trajectory design** does the third.
- The second is **constant** in $\sigma$. Directions in $\mathcal{N}$ are not recovered however
  much, and however clean, the data. It is **not** a quantity a trajectory can change — the
  mechanism's structure sets it.
- The third shows that the second **does no harm to prediction**. Torque prediction is complete
  with the base parameters alone. $\mathcal{N}$ matters for **physical interpretation** (what is
  the mass of this link) and for imposing **physical consistency constraints**.

**The relation between $\mathcal{N}$ and physical consistency — the most important number in this
lesson.** Even with **zero** noise, the minimum-norm solution on the identifiable subspace is
physically inconsistent ($\min_i\lambda_{\min}(P) = -1.1274$). Yet restoring the $\mathcal{N}$
component to its true value makes it consistent ($+9.32\times10^{-4}$) and **does not change the
torque prediction at all** ($1.2\times10^{-12}$). In other words, at $\sigma = 0$ physical
consistency lives **entirely in the unidentifiable directions** — and that is the direction the
SDP of (5) chooses. As $\sigma$ grows ($10^{-2}$) the identifiable component itself is pushed
outside the consistent set and cannot be recovered by the $\mathcal{N}$ direction alone
($-1.6\times10^{-3}$); the LMI constraint then **acts on the identifiable directions too** (that
is, it changes the estimate). These three regimes are condition 3 of the reproduction task.

## Proof sketch

### R2 — the null space is state-independent and the rank saturates

**Hypotheses** H1: a kinematic tree, rigid bodies, $S_i$ constant in body coordinates.
H2: the only measurement is the joint torque $\tau$ (no base reaction or external force is
measured). H3: the entries of $Y$ are analytic functions of $(q,\dot q,\ddot q)$.
**Conclusions** C1: $\mathcal{N}$ is a subspace of $\mathbb{R}^{10n}$ and does not depend on the
state. C2: two parameter vectors are indistinguishable from torque data iff their difference lies
in $\mathcal{N}$. C3: stacking finitely many generic samples attains rank
$n_b = 10n - \dim\mathcal{N}$ **with probability one**. C4: what changes when a hypothesis is
deleted.

**Strategy**: reduce indistinguishability to membership of the null space using linearity (R1), then
use analyticity to get "generic samples give maximal rank". The second step is the only non-trivial
part of this proof.

1. **C1.** $\mathcal{N} = \bigcap_{(q,\dot q,\ddot q)} \ker Y(q,\dot q,\ddot q)$ is an
   intersection of subspaces and so a subspace. Its definition is an intersection over all states,
   so it does not depend on the state.
2. **C2.** By (2), $\tau$ sees $\pi$ **only through $Y\pi$**. So $\pi$ and $\pi'$ give the same
   torque at every state iff $Y(\pi - \pi') = 0$ at every state, that is iff
   $\pi - \pi' \in \mathcal{N}$. (This is where H2 is used — measuring the base reaction shrinks
   $\mathcal{N}$.)
3. **Monotonicity and an upper bound on the rank.** The row space of the stacked $A_m$ increases
   monotonically in $m$ and is contained in $\mathcal{N}^\perp$. So
   $\mathrm{rank}\,A_m \le n_b$, and it stops growing at some $m^{*}$ (finite dimension).
4. **Saturation (C3).** $\mathrm{rank}\,A_m = n_b$ is equivalent to some $n_b \times n_b$ minor
   being non-zero. That minor is, by H3, an analytic function of the samples and is **not
   identically zero** (that is what the definition of $n_b$ says). The zero set of an analytic
   function that is not identically zero has measure zero, so for generic samples drawn from a
   continuous distribution, $\mathrm{rank}\,A_m = n_b$ with probability one.
   (**This step is what justifies counting $n_b$ with random samples** — exactly what condition 2
   of the reproduction task does, and the measured singular-value gap
   $5.22 \to 1.9\times10^{-14}$ is the evidence.)
5. **Where $\mathcal{N}$ comes from (structurally).** There are three archetypes.
   (a) The first body moves along the single fixed axis $S_1$, so only the combination of the
   components of $I_1$ that bears on that axis appears in the torque, and the rest **flows into the
   base reaction** and is invisible. (b) Parallel or intersecting joint axes feed combinations of
   two bodies' parameters into the torque in the same way, erasing the difference. (c) Without
   gravity, the mass and the first moment lose their **static** route into view. Gautier & Khalil
   1990 eliminate (a) and (b) constructively from the mechanism to build a minimal basis.
6. **C4 — delete a hypothesis.** Enlarging the measurement set in H2 (a six-axis force/torque
   sensor at the base, or IMUs on the links) shrinks $\mathcal{N}$ — identifiability is **not a
   property of the mechanism alone but of the mechanism plus the measurements**. Turning gravity off
   instead enlarges $\mathcal{N}$: the measurement shows $n_b$ falling from $43$ to $39$. Deleting
   rigidity from H1 destroys the linearity of (2) itself and makes the problem nonlinear
   regression. Deleting H3 (analyticity) invalidates step 4 and removes the justification for the
   procedure of "counting the rank with random samples".

### R3 — the "necessary" direction of (3)

**Hypothesis** H1: $\pi_i$ came from a positive, finite mass density $\rho \ge 0$ with compact
support. **Conclusion** C: $P(\pi_i) \succeq 0$, and $\succ 0$ unless the mass is concentrated on
a plane.

**Strategy**: write $P$ as a weighted integral of rank-one positive semidefinite matrices. One line.

1. **Pass to the second moment.** In the derivation above,
   $\Sigma = \tfrac12\operatorname{tr}(I_O)\mathbb{1} - I_O = \int\rho\,rr^\top dV$.
2. **A rank-one integral.** With $\tilde r := (r; 1) \in \mathbb{R}^4$,
   $P(\pi_i) = \int\rho(r)\,\tilde r\tilde r^\top dV$.
3. **The sign.** For any $x \in \mathbb{R}^4$,
   $x^\top Px = \int\rho\,(\tilde r^\top x)^2 dV \ge 0$, since $\rho \ge 0$. That is the first half
   of C.
4. **Positive definiteness.** If $x^\top Px = 0$ then $\tilde r^\top x = 0$ for almost every $r$ in
   the support, that is the mass is concentrated on the affine hyperplane
   $\{r : x_{1:3}^\top r + x_4 = 0\}$. Otherwise $P \succ 0$.
5. **The converse is constructive.** If $P \succeq 0$, decompose
   $P = \sum_{j} \mu_j u_ju_j^\top$ and read each $u_j$ (after rescaling) as a point mass; that
   builds a density giving the same $\pi_i$. Omitted: the details of normalising the fourth
   coordinate to one, and the boundary cases, in Wensing et al. 2018.

**Delete a hypothesis**: deleting $\rho \ge 0$ (allowing negative mass) breaks step 3 and (3)
ceases to be a constraint. Deleting compact support can make the integral diverge. And the
difference between $P \succeq 0$ and $P \succ 0$ matters in practice — a thin plate or a linear
link sits on the boundary ($\det P = 0$), and writing the SDP with a strict inequality excludes
such bodies.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ one hour /
★★★ a day or more.

**P1 (derivation, ★★, R1)** (a) Show explicitly, writing out both representations, why (1) is
nonlinear in the $(m, c, \bar I_C)$ parameterisation and linear in $(m, h, I_O)$. (b) Show that the
gravity torque $g(q)$ is expressed as $Y(q,0,0)\pi$, and check whether the columns corresponding to
the $I_O$ components are **all zero** (why?). (c) Count the cost of building $Y$ by $\pi = e_k$
RNEA calls and compare with expanding the entries by hand.
*Solution sketch*: for (b), with $\dot q = \ddot q = 0$ every $v_i = 0$ and
$a_i = {}^iX_0(-a_g)$, so $f_i = I_ia_i$. The angular components of $a_i$ are zero and only the
linear ones remain, so only the **right-hand blocks** of $I$ ($\hat h$ and $m\mathbb{1}$) are
multiplied — the $I_O$ columns are zero. That is, **static experiments alone identify no rotational
inertia whatsoever**.

**P2 (derivation, ★★, R3)** (a) Construct a concrete $\pi_i$ that satisfies $I_O \succ 0$ and the
triangle inequality of the principal moments but has $P \not\succeq 0$ (hint: make $h$ large).
(b) Conversely, show that $P \succ 0$ implies the triangle inequalities. (c) Compute $P$ for a
uniform-density rectangular box and for a **thin disk**, and check whether the disk is on the
boundary.
*Solution sketch*: for (b), note that
$\Sigma = \tfrac12\operatorname{tr}(I_O)\mathbb{1} - I_O \succeq 0$ reads, in principal moments, as
$\tfrac12(I_1+I_2+I_3) - I_k \ge 0$, which is exactly the triangle inequality — the upper-left block
of $P$ being PSD is **precisely** the triangle inequalities, and the $h$ and $m$ blocks are the
extra conditions. The thin disk in (c) has one eigenvalue of $\Sigma$ equal to zero, so
$\det P = 0$.

**P3 (proof, ★★★, R2)** (a) Write the analyticity argument of step 4 of the proof sketch
rigorously, stating where you use that the zero set of a not-identically-zero analytic function has
measure zero. (b) Find $\mathcal{N}$ **by hand** for a one-DOF pendulum and count $n_b$ (how many of
the ten?). (c) Extend to a two-DOF planar arm, find $n_b$, and compare the trend against the
measured 7-DOF value of $43$.
*Strategy and key inequality*: in (b), $\tau$ takes the form
$(I_{Ozz})\ddot\theta + (\text{gravity})$, so only $I_{Ozz}$ and the two components of $h$ entering
gravity are visible — $n_b = 3$ and $\dim\mathcal{N} = 7$. Write down separately why $h_z$ along
the axis, the other five components of $I_O$, and $m$ are invisible. The expansion is withheld.

**P4 (proof, ★★★, R3·R5)** (a) Prove that (5) is convex (objective and constraint separately).
(b) Sharpen the measured statement "at $\sigma = 0$ physical consistency lives entirely in
$\mathcal{N}$" into a general proposition — under what conditions is it true? Is there a
counterexample? (c) Discuss how the solution of (5) differs from the truth when no point on
$\mathcal{N}$ satisfies consistency (large $\sigma$) — does a bias appear?
*Strategy and key inequality*: (b) is a trap. The measurement works because **the true parameters
are consistent**, so $\hat\pi + V_{\mathrm{null}}V_{\mathrm{null}}^\top\pi = \pi$ and it holds
automatically. As a general proposition it becomes "the intersection of the consistent set with
$\hat\pi + \mathcal{N}$ is non-empty", which is true at $\sigma = 0$ because the truth is in that
intersection. In (c) the constraint becomes active and the estimate is **biased**; hoping that bias
is smaller than the model error is practice's choice.

**P5 (numerical, ★, R1·R2·R5)** On the 7-DOF reference arm (the `arm7` of the core code below),
find (a) $\lVert Y\pi - \tau\rVert_\infty$; (b) the rank $n_b$ and the singular-value gap of a
regressor stacked from 40 random states; (c) the condition number $\kappa$ of the identifiable
subspace; (d) $\lVert V_{\mathrm{null}}^\top\pi\rVert$.
*Answer* (seeds fixed; tolerances as stated):
(a) $7.1\times10^{-15}$ (required: $< 10^{-12}$)
(b) $n_b = 43$, $\dim\mathcal{N} = 27$, $S_{43} = 5.220283$, $S_{44} = 1.894\times10^{-14}$
   (required: $n_b$ exactly 43, with a gap of at least a factor $10^{10}$)
(c) $\kappa = S_1/S_{43} = 25.3866$ (tolerance $10^{-3}$; $S_1 = 132.525$)
(d) $\lVert V_{\mathrm{null}}^\top\pi\rVert = 4.7586$ (tolerance $10^{-3}$)
*Checks*: (e) $\max\lVert A V_{\mathrm{null}}\rVert_\infty < 10^{-12}$ (measured
$4.7\times10^{-13}$); (f) repeating with gravity off gives $n_b = 39$; (g) finite-differencing
$\partial\tau/\partial\ddot q$ with gravity off and $\dot q = 0$ agrees with CRBA's $M$ to within
$4.4\times10^{-16}$.

**P6 (implementation, ★★, R1·R3·R5)** (a) Write `params_of(m, c, Ic)` and
`spatial_inertia_of(p)` and check that the round trip is exact. (b) Write
`regressor(q, qd, qdd)` with $\pi = e_k$ RNEA calls. (c) Write `pseudo(p)` and a physical
consistency check. (d) Write `identify`, solving on the identifiable subspace only.
*Rubric*: (a) `spatial_inertia_of(params_of(m, c, Ic))` agrees with `mcI(m, c, Ic)` to within
$10^{-15}$ (measured $4.3\times10^{-19}$); (b) passes P5 (a); (c) a body built from eight point
masses is **positive definite for every body** (measured minimum $9.3\times10^{-4}$) and the old
generator of lessons 2 and 3 ($0.02AA^\top + 0.05\mathbb{1}$) **fails**; (d) varying $\sigma$
reproduces the table of R5; (e) the docstring says why the "non-physical unit bodies" used to build
$Y$ cannot be used with ABA.

**P7 (paper, ★★, R2·R3·R4)** (a) Translate the identifiability discussion of Atkeson et al. 1986
into the $\mathcal{N}$ of this lesson, and check whether the authors treat **physical consistency**.
(b) Compare the LMI of Wensing et al. 2018 against (3) here, and say what the authors add with
their "statistical perspective". (c) Say which baseline the speed-up of analytical derivatives
reported by Carpentier & Mansard 2018 is measured against (automatic differentiation? finite
differences?) and discuss whether that baseline is fair.
*Rubric*: for (a), noting that the 1986 paper treats identifiability **empirically** (via
conditioning) rather than constructing the structural null space passes (that is the contribution
of Gautier-Khalil 1990). For (c), questioning at least one of the implementation quality, the
language or the level of vectorisation of the baseline passes. Writing only "the paper compared
against its own implementation, so it is biased" does not.

## Paper reading

**Three must-reads** (plus one recommended). 1986, 1990, 2018 and 2018 — four axes:
**identification** (linear regression), **minimal parameters** (structure), **consistency**
(a convex constraint) and **derivatives** (computation). Reading all four and summarising in one
paragraph "what has been solved and what remains, in the problem of obtaining a model, since 1986"
is the reading goal of this lesson. Write a one-page note on each with the ten fixed questions
below (`lesson-standard.md` §5). Read in three passes and concentrate on questions 4, 5 and 7 in
the third pass.

1. **Atkeson, An & Hollerbach, "Estimation of Inertial Parameters of Manipulator Loads and
   Links" (1986, IJRR)** — role: `seminal`.
   <https://doi.org/10.1177/027836498600500306>
   Which sections and why: the whole section that sets dynamics up as a regression linear in the
   inertial parameters and solves it by least squares. R1 here is that idea, and the authors'
   experimental design (which trajectories, which measurements) connects directly to the
   conditioning discussion of R5.
   Extra questions: (a) how do the authors treat identifiability — structurally or empirically?
   (b) do they mention physical consistency, and if not, what kind of estimate can result?
   (c) how does their measurement set (torque only? a wrist force sensor?) affect $\mathcal{N}$?
2. **Wensing, Kim & Slotine, "Linear Matrix Inequalities for Physically Consistent Inertial
   Parameter Identification: A Statistical Perspective on the Mass Distribution" (2018, RA-L)** —
   role: `standard`. <https://doi.org/10.1109/LRA.2017.2729659>
   Which sections and why: the ones that set up the LMI on the pseudo-inertia and show it is
   equivalent to realisability. They correspond one-to-one with R3 here, and the focus of the
   reading is what the title's "statistical perspective" adds.
   Extra questions: (a) compare the assumptions their equivalence theorem requires against H1 of
   the R3 proof sketch here. (b) what becomes natural when, in the "statistical perspective", the
   mass distribution is read as a probability distribution? (c) how do the authors show the
   difference between estimation with and without the LMI constraint — is that metric fair?
3. **Carpentier & Mansard, "Analytical derivatives of rigid body dynamics algorithms"
   (2018, RSS)** — role: `standard`. <https://doi.org/10.15607/RSS.2018.XIV.038>
   Which sections and why: the ones that derive the derivatives of RNEA and ABA as recursions, and
   the cost comparison. What this lesson left behind after completing only (4) is there.
   Extra questions: (a) are the authors' derivative recursions of the **same order** as the
   original algorithms, or only different in the constant? (b) how do the authors explain why
   automatic differentiation is slow — is it the same explanation as the second open problem of the
   module's first lesson? (c) does differentiating dynamics with contact fall within this paper's
   scope?

**One recommended** (not required): **Gautier & Khalil, "Direct calculation of minimum set of
inertial parameters of serial robots" (1990, IEEE T-RA)**
<https://doi.org/10.1109/70.56655> — how to eliminate $\mathcal{N}$ **constructively** from the
mechanism to build a minimal basis. Step 5 of R2 is a summary of this paper, and the contrast
between numerical rank counting (this lesson's way) and symbolic elimination (the paper's way) is
worth seeing.

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) independent and dependent variables and baselines — were the baselines tuned fairly?
(6) do the metrics match the claim; are variance and seeds reported? (7) what is missing for
reproduction? (8) if it were wrong, which assumption would you suspect first? (9) compute and
memory complexity, and real-time feasibility. (10) what would you change to go beyond it in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one notebook CPU core, under five minutes, numpy
only (the SDP is optional). Memory under 500 MB.

**Core code — reparameterisation, regressor and consistency check.** Below is the heart of the code
every number in the text came from. It uses the `rnea`, `crba`, `mcI`, `skew` and `Model` of the
previous lessons unchanged.

```python
def params_of(m, c, Ic):
    """The 10 inertial parameters: m, h = m c, and I about the FRAME ORIGIN (upper triangle)."""
    c = np.asarray(c, float)
    C = skew(c)
    Io = Ic + m * C @ C.T  # parallel axis: origin inertia from the com inertia
    return np.array([m, *(m * c), Io[0, 0], Io[0, 1], Io[0, 2], Io[1, 1], Io[1, 2], Io[2, 2]])


def spatial_inertia_of(p):
    """Spatial inertia (1), linear in the 10 parameters p. Inverse of params_of."""
    Io = np.array([[p[4], p[5], p[6]], [p[5], p[7], p[8]], [p[6], p[8], p[9]]])
    H = skew(p[1:4])
    return np.block([[Io, H], [H.T, p[0] * np.eye(3)]])


def unit_models(model):
    """One model per parameter, with pi = e_k. These bodies are NOT physical (zero or negative
    mass), which is fine for RNEA but would break ABA, where d_i > 0 is required."""
    out = []
    for k in range(10 * model.n):
        e = np.zeros(10 * model.n)
        e[k] = 1.0
        m = Model(model.parent, model.jtype, model.Xtree, model.mass_props)
        m.I = [spatial_inertia_of(e[10 * i : 10 * i + 10]) for i in range(model.n)]
        out.append(m)
    return out


def regressor(unit, q, qd, qdd):
    """Y with tau = Y pi, one RNEA call per column (R1)."""
    return np.column_stack([rnea(u, q, qd, qdd) for u in unit])


def pseudo(p):
    """The pseudo-inertia (3). Linear in p, so {p : pseudo(p) >= 0} is an LMI."""
    Io = np.array([[p[4], p[5], p[6]], [p[5], p[7], p[8]], [p[6], p[8], p[9]]])
    Sigma = 0.5 * np.trace(Io) * np.eye(3) - Io
    h = p[1:4]
    return np.block([[Sigma, h.reshape(3, 1)], [h.reshape(1, 3), np.array([[p[0]]])]])


def subspaces(unit, nsamples=40, seed=5, tol=1e-10):
    """The identifiable subspace and the structural null space N, by SVD of a stacked
    regressor at generic random states (step 4 of the R2 proof sketch)."""
    rng = np.random.default_rng(seed)
    n = unit[0].n
    rows = [
        regressor(unit, rng.normal(size=n), rng.normal(size=n), rng.normal(size=n))
        for _ in range(nsamples)
    ]
    A = np.vstack(rows)
    _, S, Vt = np.linalg.svd(A, full_matrices=True)
    nb = int((S > S[0] * tol).sum())
    return A, S, nb, Vt[:nb].T, Vt[nb:].T  # A, singular values, n_b, V_id, V_null


def identify(model, unit, V_id, nsamples, sigma, seed):
    """Least squares on the identifiable subspace only."""
    rng = np.random.default_rng(seed)
    n = model.n
    rows, rhs = [], []
    for _ in range(nsamples):
        a, b, c = rng.normal(size=n), rng.normal(size=n), rng.normal(size=n)
        rows.append(regressor(unit, a, b, c))
        rhs.append(rnea(model, a, b, c) + sigma * rng.normal(size=n))
    A, y = np.vstack(rows), np.concatenate(rhs)
    return V_id @ np.linalg.lstsq(A @ V_id, y, rcond=None)[0]
```

The 7-DOF reference arm is the **same model** as in the previous two lessons (fixed link offsets,
mass properties generated from eight point masses — see the input-data section of the
`c2-rnea-inverse-dynamics` reproduction task). Gravity uses the default
$a_g = (0,0,0,\,0,0,-9.81)$.

**All four** of the following must hold.

1. **Reparameterisation and linearity** — (a) for every body,
   $\lVert\texttt{spatial\_inertia\_of(params\_of}(m, c, \bar I_C)) - \texttt{mcI}(m, c, \bar I_C)\rVert_\infty < 10^{-15}$
   (measured $4.3\times10^{-19}$). (b) At $10^2$ random states,
   $\max\lVert Y\pi - \texttt{rnea}\rVert_\infty < 10^{-12}$ (measured $7.1\times10^{-15}$).
   (c) Confirm that $Y$ is independent of $\pi$ — changing the model's mass properties must give
   the same $Y$ (difference **exactly** zero).
2. **The identifiability decomposition** — stacking 40 random states, show
   $$
   n_b = 43, \qquad \dim\mathcal{N} = 27, \qquad
   \frac{S_{43}}{S_{44}} > 10^{10}, \qquad \max\lVert AV_{\mathrm{null}}\rVert_\infty < 10^{-12}
   $$
   (measured $S_{43} = 5.220283$, $S_{44} = 1.894\times10^{-14}$, ratio $2.8\times10^{14}$,
   $\lVert AV_{\mathrm{null}}\rVert = 4.7\times10^{-13}$). Increase the number of samples over
   $5, 10, 20, 40, 80$ and show that the rank **saturates** (from the point where
   $n \cdot n_{\text{samples}} \ge n_b$ it stays at 43), and confirm that turning gravity off
   reduces it to $n_b = 39$.
3. **Noise, conditioning, and where consistency lives** — (a) reproduce the table of R5 for
   $\sigma \in \{0, 10^{-3}, 10^{-2}, 10^{-1}\}$: the error of the identifiable component
   $\propto\sigma$ (tolerance 5%), the error of the $\mathcal{N}$ component fixed at $4.7586$
   independently of $\sigma$ (tolerance $10^{-3}$), and the torque prediction error at fresh states
   $\propto\sigma$.
   (b) Confirm that the **true parameters are physically consistent**: for every body,
   $\lambda_{\min}(P(\pi_i)) > 0$ (measured minimum $9.3\times10^{-4}$).
   (c) Show that **even at $\sigma = 0$ the minimum-norm solution is inconsistent**:
   $\min_i\lambda_{\min}(P(\hat\pi_i)) < 0$ (measured $-1.1274$). Yet
   $\hat\pi + V_{\mathrm{null}}V_{\mathrm{null}}^\top\pi$ is **consistent** (measured
   $+9.32\times10^{-4}$) and the torque prediction is **unchanged** (measured $1.2\times10^{-12}$).
   (d) Show that at $\sigma = 10^{-2}$ the same correction no longer restores consistency
   (measured $-1.6\times10^{-3}$) — at which point the LMI constraint acts on the identifiable
   directions too.
   > These four are the heart of this lesson. The contrast between (c) and (d) is the whole of
   > "why an SDP is needed".
4. **Accuracy of the analytical derivative** — (a) with gravity off and $\dot q = 0$, finite
   difference $\partial\tau/\partial\ddot q$ and match CRBA's $M$ to within $10^{-12}$, sweeping
   $h$ over $10^{-8} \dots 10^{-4}$ and showing that the level is the same **across the whole
   range** (measured $4.4\times10^{-16}$); then show, by contrast, that with gravity on the
   cancellation dominates and the error grows like $1/h$ (measured $7.1\times10^{-11}$ at
   $10^{-4}$, $8.7\times10^{-9}$ at $10^{-6}$, $9.2\times10^{-7}$ at $10^{-8}$).
   (b) Confirm the affinity of $\tau$ in $\ddot q$ with a unit test (measured
   $2.1\times10^{-14}$).
   (c) Show numerically that static experiments cannot identify $I_O$: the 42 columns of
   $Y(q, 0, 0)$ corresponding to $I_O$ must be **exactly** zero (problem P1 (b)).

**Input data**: no external data needed. The model is identical to the previous two lessons, and
every random draw uses `np.random.default_rng` with the seeds given in the text (7 for the model,
5 for the subspaces, 11 for the identification).

**Baselines** (at least one):
- First choice: condition 1 (b) — $Y\pi$ and the previous lesson's `rnea` are **two independent
  routes**, one a linear regressor and the other a recursive algorithm.
- Second choice: CRBA's $M$ and the finite-difference Jacobian of condition 4 (a).
- Optional check (not required to pass): actually solve the SDP of (5) with `cvxpy` and measure, at
  $\sigma = 10^{-2}$, how much the constrained solution removes the inconsistency of (d) and how
  much the torque prediction error grows. It must be possible to pass without dependencies, so this
  is **optional**.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| $\lVert Y\pi - \tau\rVert$ is at the $10^{-3}$ level | $\bar I_C$ was used as a parameter instead of $I_O$ | Look at `params_of` and check that the parallel-axis term $m\hat c\hat c^\top$ is there |
| The same symptom, only for bodies with $c \ne 0$ | $c$ was passed instead of $h = mc$ | Check whether it is right for bodies with $c = 0$ and wrong otherwise |
| $n_b$ varies from run to run | The SVD threshold sits inside the singular-value gap | Print all the singular values, see the gap ($5.2 \to 1.9\times10^{-14}$) with your own eyes and put the threshold between them |
| $n_b$ comes out as 70 | Too few stacked equations ($n \times$ samples $< 70$), or the threshold is too small | Increase the samples and confirm saturation (condition 2) |
| The $\mathcal{N}$ error varies with $\sigma$ | Least squares was solved on the whole space (without regularisation) | Check that you project with $V_{\mathrm{id}}$ before solving — the whole-space solution is not unique |
| Condition 3 (b) fails | The model generator is not physically consistent | **This module actually experienced this**: the generator $0.02AA^\top + 0.05\mathbb{1}$ violates the triangle inequality for six bodies out of seven. Switch to the point-mass generator |
| A V curve appears in condition 4 (a) | Gravity was not turned off | Print the magnitude of $\tau$ — with gravity on it is $O(10)$ and cancellation dominates |
| The $I_O$ columns in condition 4 (c) are not zero | $\dot q$ or $\ddot q$ was not set to zero | Print all the $v_i$ and check they are zero |

## Open problems

- **(open problem) Identification with contact, and nonlinear elements** — the linearity of (2)
  depends on a tree, rigidity and the absence of friction. On a real robot the torque error is
  dominated by joint friction (Stribeck, hysteresis), harmonic-drive compliance, cabling and
  thermal drift, and none of these is **inside linear regression**. Add contact and the
  non-smoothness of the previous lesson joins in, so even "what is being identified" becomes
  blurred. The practice of identifying the linear part first and learning the residual has no
  guarantee about how the two stages' errors mix. Current approaches: identification with physical
  consistency as a constraint
  ([Wensing et al. 2018](https://doi.org/10.1109/LRA.2017.2729659)), residual learning, and
  differentiable simulation. What is missing: whether the decomposition into a linear model plus a
  learned residual is **unique**, and any generalisation guarantee for it.
- **(open problem) Global optimality of excitation-trajectory design** — as R5 shows, the only
  thing that can be changed is $\kappa$. Finding the trajectory that minimises $\kappa$ is
  nonconvex (the trajectory enters the regressor nonlinearly) and comes with joint, velocity and
  safety constraints. Practice remains at the convention of local optimisation over a finite
  Fourier basis, and neither a **globally optimal trajectory** nor a lower bound is known. That
  $\dim\mathcal{N}$ cannot be changed by a trajectory but **can** be changed by adding measurements
  (C4 of R2) widens the design space, yet formulations that optimise sensor placement and
  trajectory **together** are almost absent. Current approaches: Fourier parameterisation with
  local optimisation, and D-optimal design. What is missing: the joint design of sensor placement
  and trajectory, and an achievable lower bound on $\kappa$.
- **(open problem) Differentiating contact dynamics, and the validity of those gradients** — R4 is
  the derivative of a contact-free tree; with contact, the open problem of the previous lesson
  carries straight over. The explanation of why analytical derivatives beat automatic
  differentiation (redundant work) is an analysis of the smooth case, and for non-smooth contact
  "the derivative of what" has to be defined first. With trajectory optimisation and policy
  learning now demanding **dynamics and its derivatives** at thousands of states at once, this is a
  practical bottleneck. Current approaches: analytical derivatives
  ([Carpentier & Mansard 2018](https://doi.org/10.15607/RSS.2018.XIV.038)), smooth derivatives of a
  convex relaxation, and randomized smoothing. What is missing: an error bound for the relaxed
  gradient — the same wall as the first open problem of `c2-contact-dynamics`, and the wall this
  module ends at.

## Concept check

Run `rc quiz c2-dynamics-derivatives-sysid`. The quiz is for **concept checking only**; the real
work is the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: which parameterisation makes the spatial inertia linear; which statements
about the structurally unidentifiable subspace are true; the condition equivalent to realisability
by a positive mass density; whether $\partial\tau/\partial\ddot q$ is exactly $M(q)$; and why the
minimum-norm solution can be physically inconsistent even with no noise at all.

## How to study this stage

1. **Check the $h = mc$ reparameterisation by hand (25 min)** — write (4) of the module's first
   lesson beside (1) here and follow, component by component, how the parallel-axis term
   disappears. Those ten minutes are the premise of the whole lesson. Then confirm the
   `params_of`/`spatial_inertia_of` round trip at $10^{-15}$ (condition 1 (a)).
2. **Build the regressor in three lines (30 min)** — extract $Y$ with $\pi = e_k$ RNEA calls and
   look at $\lVert Y\pi - \tau\rVert$. **Do not read** the literature's component expansions; start
   this way, because reusing the previous lessons' verified RNEA leaves almost no room for error.
3. **Look at the singular values with your eyes (40 min)** — print all seventy singular values of
   the stacked regressor. The gap from $5.22$ to $1.9\times10^{-14}$ has to be **visible** before
   $n_b = 43$ becomes a number you can trust. Putting the threshold inside that gap is the whole
   procedure, and without a gap counting $n_b$ is meaningless (rows 3 and 4 of the diagnosis table).
4. **Understand step 4 of R2 on its own (40 min)** — write a paragraph on why "the zero set of an
   analytic function has measure zero" is needed and how it justifies "counting the rank with random
   samples". That single step turns a practical procedure (random samples plus an SVD) into a
   theorem.
5. **See for yourself where consistency lives (60 min)** — do conditions 3 (c) and (d) first.
   Seeing with your own hands the three numbers — that at $\sigma = 0$ the minimum-norm solution is
   inconsistent, that restoring the $\mathcal{N}$ component makes it consistent, and that the
   prediction does not change — settles "why an SDP". That experiment is the centre of this lesson.
6. **Doubt your own generator (30 min)** — run condition 3 (b) on your own model. The author of
   this module wrote in lessons 2 and 3 that "$0.02AA^\top + 0.05\mathbb{1}$ satisfies the triangle
   inequalities" and was **wrong** (six of seven violate it). The pseudo-inertia test refutes such a
   claim instantly — run it every time you build a model.
7. **Read the four papers along the four axes (150 min)** — Atkeson (linear regression) →
   Gautier-Khalil (minimal basis) → Wensing (consistency) → Carpentier-Mansard (derivatives) is both
   chronological and logical. For each, write one line on "which of R1-R5 this author produced".
8. **Close the module (30 min)** — summarise the six lessons of C2 on one page: notation (lesson 1)
   → inverse dynamics (2) → mass matrix and forward dynamics (3) → constraints (4) → contact (5) →
   how to obtain the model (6). Then pick three of the open problems and confirm that they converge
   on the single wall of "differentiating contact" — C3, C4 and S2 start from that wall.

**Passing bar**: you can write (1), (2), (3) and (4) from a blank page; you can state the saturation
argument of R2 and the rank-one integral argument of R3; you have a regressor, an identification and
a consistency check that pass all four conditions of the reproduction task; and you have one-page
notes on the three must-reads (four including the recommended one).
