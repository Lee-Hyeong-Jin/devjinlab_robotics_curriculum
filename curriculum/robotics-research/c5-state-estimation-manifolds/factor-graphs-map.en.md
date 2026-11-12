---
id: c5-factor-graphs-map
lang: en
title: Factor graphs and MAP inference
summary: >-
  Set up state estimation as MAP inference on a factor graph rather than as a filter recursion,
  and prove that under Gaussian assumptions MAP is equivalent to nonlinear least squares. Derive
  Gaussian variable elimination as the Schur complement, which shows that filtering is just one
  elimination order of smoothing plus the policy of discarding the conditional. Reproduce the
  Gauss-Newton solution of a two-lap SE(2) pose graph and match the sparse and dense solvers.
objectives:
  - Prove, with the assumptions made explicit, that MAP on a Gaussian factor graph is equivalent to nonlinear least squares.
  - Explain where that equivalence breaks when the measurement covariance depends on the state.
  - Derive the Schur complement from Gaussian variable elimination by completing the square, with no missing steps.
  - Derive the Kalman filter update from the normal equations of a least-squares problem and show it equals the covariance form.
  - Explain the condition-number difference between the normal equations (Cholesky) and QR numerically.
  - Write the Jacobians of an SE(2) pose graph by hand, converge Gauss-Newton, and compare the sparse and dense solutions.
tags: [state-estimation, factor-graph, map, least-squares, smoothing, research]
---

# Factor graphs and MAP inference

## Setup and notation

This is the first lesson of module C5, and the remaining five lessons use the notation fixed
here. The following is assumed:

- Probability: joint, conditional and marginal distributions, linear transformations of
  Gaussians, Bayes' rule. Measure theory is not required.
- Linear algebra: block matrices, Cholesky and QR factorizations, condition numbers, positive
  definiteness. The $\exp$ and $\log$ notation of `c1-so3-se3-exponential`.
- Estimation on manifolds is not used yet — every variable in this lesson is a coordinate vector
  in $\mathbb{R}^d$, and why that choice is wrong is corrected in `c5-manifold-estimation`.

Notation (fixed for the whole C5 module):

| Symbol | Meaning |
|---|---|
| $\mathcal{X} = \{x_1, \dots, x_n\}$ | the variables to estimate, $x_i \in \mathbb{R}^{d_i}$, total dimension $N = \sum_i d_i$ |
| $\mathcal{Z} = \{z_1, \dots, z_m\}$ | the measurements, $z_k \in \mathbb{R}^{p_k}$ |
| $\mathcal{X}_k \subseteq \mathcal{X}$ | the variables factor $k$ touches (its **degree** is $\lvert\mathcal{X}_k\rvert$) |
| $h_k : \mathcal{X}_k \to \mathbb{R}^{p_k}$ | the measurement function (model) |
| $\Sigma_k \succ 0$ | the noise covariance of $z_k$. $\lVert e \rVert^2_{\Sigma} := e^\top \Sigma^{-1} e$ |
| $J_k = \partial h_k / \partial x$ | the Jacobian of $h_k$, evaluated at the linearization point |
| $A$ | the **whitened** Jacobians stacked into an $M \times N$ matrix with blocks $\Sigma_k^{-1/2} J_k$, $M = \sum_k p_k$ |
| $b$ | the whitened residuals $-\Sigma_k^{-1/2}(h_k(x) - z_k)$ stacked |
| $\Lambda = A^\top A \in \mathbb{R}^{N\times N}$ | the information matrix |
| $\eta = A^\top b \in \mathbb{R}^N$ | the information vector |
| $\mathsf{R}$ | the upper-triangular Cholesky factor of $\Lambda = \mathsf{R}^\top \mathsf{R}$, the **square root information matrix**. Kept distinct from a rotation matrix $R$ |
| $\mathcal{S}(x_i)$ | the **separator** of $x_i$ — the other variables that share a factor with it |
| $\chi^2(x)$ | the weighted sum of squared residuals, $\lVert A x - b\rVert^2$ |

A **factor graph** is a bipartite graph of variable nodes $x_i$ and factor nodes $\phi_k$, and
what it represents is one factorization of a function:

$$
\phi(\mathcal{X}) = \prod_{k=1}^{m} \phi_k(\mathcal{X}_k),
  \qquad \phi_k(\mathcal{X}_k) \propto \exp\!\left(-\tfrac{1}{2}\lVert h_k(\mathcal{X}_k) - z_k \rVert^2_{\Sigma_k}\right). \tag{1}
$$

The prior and the motion model are factors too — they hold no special status in the graph. That
is what turns the distinction between filtering and smoothing into a property **of the inference
order rather than of the graph**.

## Self-diagnosis before starting

This is the first lesson of the module, so check your readiness first. **Prerequisite lessons are
not locked** — if you can solve all of the following, skip the recommended prerequisites (the R0
module and `c1-so3-se3-exponential`) and start here. **If two or more stop you**, going back to
the prerequisite lesson named in parentheses is faster.

1. A prior $x\sim\mathcal{N}(0, 1)$ receives one measurement $z = x + v$ with
   $v\sim\mathcal{N}(0, 0.25)$ and $z = 1.0$. What are the posterior mean and variance?
   (`f0-probability-statistics`, `r0-estimation-theory`)
   **Answer**: information adds — $\Lambda = 1 + 1/0.25 = 5$ and $\eta = 0 + 4\cdot1 = 4$, so the
   mean is $0.8$ and the variance $1/5 = 0.2$. Tolerance $10^{-9}$.
2. For $A = \begin{bmatrix}1&0\\1&1\\0&1\end{bmatrix}$ and $b = (1,2,2)^\top$, find the
   least-squares solution, the residual sum of squares $\lVert Ax-b\rVert^2$, and
   $\kappa_2(A^\top A)$. (`r0-linear-algebra-decompositions`)
   **Answer**: $A^\top A = \begin{bmatrix}2&1\\1&2\end{bmatrix}$, $A^\top b = (3,4)^\top$,
   $x^\ast = (2/3,\ 5/3)^\top$, $\lVert Ax^\ast-b\rVert^2 = 1/3$ and
   $\kappa_2(A^\top A) = 3/1 = 3$ (so $\kappa_2(A) = \sqrt{3}$). Tolerance $10^{-9}$.
3. Compute the Schur complement of the first block of $M = \begin{bmatrix}4&2\\2&3\end{bmatrix}$
   and decide whether $M \succ 0$. (`r0-linear-algebra-decompositions`)
   **Answer**: $3 - 2\cdot4^{-1}\cdot2 = 2 > 0$ and $M_{11} = 4 > 0$, so $M \succ 0$
   (eigenvalues $(7\pm\sqrt{17})/2 \approx 5.5616,\ 1.4384$).
4. How many nonzeros does the (lower-triangular) Cholesky factor of a $5\times5$ tridiagonal
   positive definite matrix have? What changes if the **third** variable is eliminated first?
   (`r0-sparse-linear-algebra`)
   **Answer**: with the natural order there is no fill-in, so $5 + 4 = 9$. Eliminating the third
   variable first connects variables 2 and 4 (the separator becomes a clique), adding one
   nonzero. **The order decides the sparsity.**
5. Write $-\log \mathcal{N}(x;\mu,\Sigma)$ with the terms that do not depend on $x$ grouped
   together. Which terms are those? (`f0-probability-statistics`)
   **Answer**: $\tfrac12(x-\mu)^\top\Sigma^{-1}(x-\mu) + \tfrac12\log\det\Sigma
   + \tfrac{d}{2}\log 2\pi$. The last two do not depend on $x$ — as long as $\Sigma$ does not
   depend on $x$. Result R1 of this lesson is exactly about that condition.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (MAP = nonlinear least squares) [D3]** — if the noise is additive Gaussian and $\Sigma_k$
  **does not depend on the state**, then
  $$
  \hat{\mathcal{X}}_{\mathrm{MAP}} = \arg\max_{\mathcal{X}} \prod_k \phi_k(\mathcal{X}_k)
    = \arg\min_{\mathcal{X}} \; \frac{1}{2}\sum_{k=1}^{m} \lVert h_k(\mathcal{X}_k) - z_k \rVert^2_{\Sigma_k}. \tag{2}
  $$
- **R2 (Gauss-Newton and the square root information form) [D2]** — linearizing (2) at
  $\mathcal{X}^{(t)}$ makes the increment $\delta$ satisfy the normal equations
  $$
  \Lambda\,\delta = \eta, \qquad \Lambda = A^\top A, \quad \eta = A^\top b \tag{3}
  $$
  which is equivalent to the linear least-squares problem $\min_\delta \lVert A\delta - b\rVert^2$.
  The QR factorization $A = Q\begin{bmatrix}\mathsf{R}\\0\end{bmatrix}$ solves (3) **without ever
  forming** $\Lambda$, as $\mathsf{R}\delta = Q_1^\top b$. The key numerical fact:
  $\kappa(\Lambda) = \kappa(A)^2$.
- **R3 (Gaussian variable elimination = the Schur complement; elimination = conditioning +
  marginalization) [D3]** — for a Gaussian $p(\mathcal{X}) \propto \exp(-\tfrac12 x^\top\Lambda x
  + \eta^\top x)$ with $\Lambda \succ 0$, eliminating $x_1$ gives
  $$
  p(\mathcal{X}) = \underbrace{p(x_1 \mid x_{\mathcal{S}})}_{\text{conditional, information } \Lambda_{11}}
    \cdot \underbrace{p(x_{\mathcal{S}}, \dots)}_{\text{new factor}}, \quad
    \Lambda^{\mathrm{new}}_{\mathcal{S}} = \Lambda_{\mathcal{S}\mathcal{S}}
      - \Lambda_{\mathcal{S}1}\Lambda_{11}^{-1}\Lambda_{1\mathcal{S}}. \tag{4}
  $$
  The right-hand side of (4) is the **Schur complement** of $\Lambda_{11}$ in $\Lambda$, and it
  is the **same matrix** that marginalizing $x_1$ out by integration produces. The only
  difference between the two is whether the conditional $p(x_1\mid x_{\mathcal{S}})$ is kept
  (smoothing, so back-substitution is possible) or discarded (filtering).
- **R4 (filtering is one elimination order of smoothing; the EKF is one Gauss-Newton step without
  relinearization) [D2]** — in a linear-Gaussian system, eliminating past states in time order
  turns (4) into exactly the Kalman filter recursion, and the filter's estimate equals the
  marginal of the last state of the full MAP solution **exactly**. In the nonlinear case the
  equality fails: the EKF linearizes once per time step at the predicted mean and **never
  relinearizes**, which makes it a single Gauss-Newton step.
- **R5 (the MAP covariance is a Laplace approximation) [D1]** — at the optimum
  $\operatorname{Cov}(\mathcal{X}) \approx \Lambda^{-1}$, and the marginal covariance of $x_i$ is
  $(\Lambda^{-1})_{ii}$. This is an **approximation** obtained by expanding the posterior to
  second order at the optimum, and it underestimates the true covariance where third- and
  higher-order terms matter (large rotational uncertainty, strongly nonlinear range-bearing
  measurements).

## Derivation

### R1 — how MAP becomes nonlinear least squares

State the assumptions. **(A1)** each measurement is $z_k = h_k(\mathcal{X}_k) + \epsilon_k$ with
$\epsilon_k \sim \mathcal{N}(0, \Sigma_k)$. **(A2)** the $\epsilon_k$ are mutually independent.
**(A3)** $\Sigma_k$ is constant — it does not depend on $\mathcal{X}$. The prior
$p(\mathcal{X}_0)$ is absorbed as a factor of the same form (A1) with $h = \mathrm{id}$.

Bayes' rule gives $p(\mathcal{X}\mid\mathcal{Z}) =
p(\mathcal{Z}\mid\mathcal{X})p(\mathcal{X})/p(\mathcal{Z})$, and the denominator does not depend
on $\mathcal{X}$, so it drops out of the maximization. By (A2) the likelihood splits over
factors:

$$
p(\mathcal{X}\mid\mathcal{Z}) \propto \prod_{k=1}^{m}
  \frac{1}{\sqrt{(2\pi)^{p_k}\det\Sigma_k}}
  \exp\!\left(-\tfrac{1}{2}(h_k(\mathcal{X}_k) - z_k)^\top \Sigma_k^{-1}(h_k(\mathcal{X}_k) - z_k)\right). \tag{5}
$$

Take the negative logarithm. Since the logarithm is strictly increasing, nothing happens beyond
turning $\arg\max$ into $\arg\min$:

$$
-\log p(\mathcal{X}\mid\mathcal{Z}) = \frac{1}{2}\sum_{k=1}^{m}
  \lVert h_k(\mathcal{X}_k) - z_k\rVert^2_{\Sigma_k}
  + \underbrace{\frac{1}{2}\sum_{k=1}^{m}\log\det\Sigma_k + \frac{1}{2}\sum_k p_k \log 2\pi + \log p(\mathcal{Z})}_{=: c}. \tag{6}
$$

Because of (A3), $c$ is **constant** in $\mathcal{X}$. Hence (2). The derivation used only (A1)
(the Gaussian form), (A2) (the product factorization) and (A3) ($c$ is constant).

**Where the assumption breaks**: when $\Sigma_k = \Sigma_k(\mathcal{X})$ — LiDAR noise that grows
with range, feature variances that change with illumination, a learned heteroscedastic
uncertainty — the term $\frac12\log\det\Sigma_k(\mathcal{X})$ is no longer constant. The correct
MAP objective is then

$$
\frac{1}{2}\sum_k \left[\lVert h_k - z_k\rVert^2_{\Sigma_k(\mathcal{X})}
  + \log\det\Sigma_k(\mathcal{X})\right] \tag{7}
$$

and dropping the $\log\det$ term to minimize only (2) **pulls the solution towards reporting
larger noise** (the trivial degeneracy of driving every residual to zero with
$\Sigma \to \infty$). Recent work that puts learned covariances into factor graphs gets this
wrong, or adds a separate regularizer, for exactly this reason.

### R2 — the normal equations and the square root information form

Write the objective of (2) as $F(\mathcal{X}) = \tfrac12\sum_k \lVert h_k - z_k\rVert^2_{\Sigma_k}$
and substitute $h_k(\mathcal{X}^{(t)} + \delta) \approx h_k(\mathcal{X}^{(t)}) + J_k\delta$ near
$\mathcal{X}^{(t)}$. Multiplying both sides by $\Sigma_k^{-1/2}$ (whitening) gives, with the $A$
and $b$ of the notation table,

$$
F(\mathcal{X}^{(t)} + \delta) \approx \tfrac{1}{2}\lVert A\delta - b\rVert^2,
  \qquad b = -\Sigma^{-1/2}\big(h(\mathcal{X}^{(t)}) - z\big). \tag{8}
$$

Differentiating in $\delta$ and setting the result to zero yields $A^\top(A\delta - b) = 0$,
which is (3). If $A$ has full column rank then $\Lambda \succ 0$ and the solution is unique. Two
roads diverge here:

1. **Cholesky**: form $\Lambda = \mathsf{R}^\top\mathsf{R}$ and do forward and back substitution.
   The cost is the $O(\sum_k p_k d_k^2)$ of assembling $\Lambda$ plus the factorization.
2. **QR**: factor $A = Q\begin{bmatrix}\mathsf{R}\\0\end{bmatrix}$ directly. Since
   $\lVert A\delta - b\rVert^2 = \lVert \mathsf{R}\delta - Q_1^\top b\rVert^2 + \lVert Q_2^\top b\rVert^2$,
   solving $\mathsf{R}\delta = Q_1^\top b$ suffices and the second term is the remaining $\chi^2$.
   $\Lambda$ is **never formed**.

Up to signs the two roads give the same $\mathsf{R}$ (since $A^\top A = \mathsf{R}^\top Q_1^\top
Q_1 \mathsf{R} = \mathsf{R}^\top\mathsf{R}$). The difference is numerical: the singular values
satisfy $\sigma_i(\Lambda) = \sigma_i(A)^2$, so

$$
\kappa(\Lambda) = \kappa(A)^2. \tag{9}
$$

If $\kappa(A) = 10^8$ then $\Lambda$ is numerically singular in double precision while $A$ is
not. This is the argument of `dellaert2006-square-root-sam` — forming the information matrix
squares the condition number — and the reason to treat the square root information $\mathsf{R}$
as a first-class object.

**Where the assumption breaks**: (8) discards the second-order terms of $h_k$. Where residuals
are large and curvature is high, a Gauss-Newton step can **increase** the objective — the true
Hessian is $A^\top A + \sum_k r_k^\top \partial^2 h_k$ and GN drops the second term. This is why
a pose graph with a poor initial guess diverges, and why a trust region
(Levenberg-Marquardt, Dogleg) is needed. The reproduction task of this lesson stays inside the
region where GN converges.

### R4 — rewriting filtering as elimination

Use a linear-Gaussian chain: $x_{i+1} = F_i x_i + w_i$ with $w_i\sim\mathcal{N}(0,Q_i)$,
$z_i = H_i x_i + v_i$ with $v_i\sim\mathcal{N}(0,R_i)$, and the prior
$x_0\sim\mathcal{N}(\bar x_0, P_0)$. By (6) the full negative log posterior is

$$
F(x_{0:K}) = \tfrac{1}{2}\lVert x_0 - \bar x_0\rVert^2_{P_0}
  + \tfrac{1}{2}\sum_{i=0}^{K-1}\lVert x_{i+1} - F_i x_i\rVert^2_{Q_i}
  + \tfrac{1}{2}\sum_{i=0}^{K}\lVert z_i - H_i x_i\rVert^2_{R_i}. \tag{10}
$$

Eliminate $x_0$. The only factors it touches are the prior, $z_0$ and the motion factor to
$x_1$, so $\mathcal{S}(x_0) = \{x_1\}$. Applying (4), the new factor is a Gaussian on $x_1$ alone
whose information matrix is the Schur complement. Moving that to covariance form gives the Kalman
filter. Here is one step with no missing lines.

**One update step.** For a prediction $\bar x$ with covariance $\bar P$ and a measurement
$z = Hx + v$, $v\sim\mathcal{N}(0,R)$, the part of (10) that involves $x$ is

$$
J(x) = \tfrac{1}{2}(x - \bar x)^\top \bar P^{-1}(x - \bar x)
  + \tfrac{1}{2}(z - Hx)^\top R^{-1}(z - Hx). \tag{11}
$$

$$
\nabla J(x) = \bar P^{-1}(x - \bar x) - H^\top R^{-1}(z - Hx) = 0
$$

$$
\Longrightarrow\quad \underbrace{(\bar P^{-1} + H^\top R^{-1}H)}_{=:\ \Lambda}\,x
  = \bar P^{-1}\bar x + H^\top R^{-1} z. \tag{12}
$$

Rewriting $\bar P^{-1}\bar x = \Lambda\bar x - H^\top R^{-1}H\bar x$ on the right gives

$$
\Lambda x = \Lambda \bar x + H^\top R^{-1}(z - H\bar x)
  \quad\Longrightarrow\quad \hat x = \bar x + \Lambda^{-1}H^\top R^{-1}(z - H\bar x). \tag{13}
$$

Equation (13) is the update in **information form**. That it equals the textbook **covariance
form** $\hat x = \bar x + K(z - H\bar x)$ with $K = \bar P H^\top (H\bar P H^\top + R)^{-1}$ is
the identity

$$
(\bar P^{-1} + H^\top R^{-1}H)^{-1}H^\top R^{-1} = \bar P H^\top (H\bar P H^\top + R)^{-1}. \tag{14}
$$

Proof of (14): multiply the left-hand side by $\Lambda$ on the left and by
$(H\bar PH^\top + R)$ on the right,

$$
H^\top R^{-1}(H\bar P H^\top + R) = H^\top R^{-1}H\bar PH^\top + H^\top,
$$

and do the same to the right-hand side,

$$
\Lambda\,\bar P H^\top = (\bar P^{-1} + H^\top R^{-1}H)\bar P H^\top
  = H^\top + H^\top R^{-1}H\bar PH^\top .
$$

The two results agree, and $\Lambda \succ 0$, $H\bar PH^\top + R \succ 0$, so (14) holds. The
covariance follows the same way as $P = \Lambda^{-1} = \bar P - KH\bar P$ (problem P1).

**So what is different.** Elimination produces two pieces — the conditional $p(x_0\mid x_1)$ and
the new factor $p(x_1,\dots)$. The filter **discards** the conditional. Once discarded:

1. $x_0$ can never be re-estimated. A loop closure that arrives later cannot correct the past.
2. In the nonlinear case it is worse. The **linearization point is frozen forever** at the moment
   the conditional was discarded. Even if new information improves the estimate of $x_0$, the
   $J_k(\hat x_0^{\text{old}})$ already baked into the Schur complement cannot be undone. This is
   the origin of EKF-SLAM inconsistency and the subject of `c5-observability-consistency`.
3. In the linear-Gaussian case, 1 and 2 **do not affect the estimate** — elimination is exact and
   there is no linearization, so the filter's marginal of the last state equals the smoother's.
   What defeats the filter is nonlinearity, not elimination.

Smoothing keeps every conditional. Substituting the stored conditionals in reverse order is
**back-substitution**, and for a linear-Gaussian chain that is precisely the Rauch-Tung-Striebel
smoother (problem P1).

### R5 — why the covariance is an approximation

Expanding $-\log p$ to second order at $\hat{\mathcal{X}}$ gives $-\log p(\mathcal{X}) \approx
\text{const} + \tfrac12 (\mathcal{X}-\hat{\mathcal{X}})^\top \Lambda (\mathcal{X}-\hat{\mathcal{X}})$,
so the posterior is read as $\mathcal{N}(\hat{\mathcal{X}}, \Lambda^{-1})$ (the Laplace
approximation). All of $\Lambda^{-1}$ need not be formed — only the required blocks are extracted
from $\mathsf{R}$ by back-substitution (`dellaert2017-factor-graphs` §4). **[D1]**

It is an approximation for two reasons. (a) If $h_k$ is nonlinear the posterior is not Gaussian
and the third- and higher-order terms are not negligible. (b) The MAP point itself is **not
invariant under reparameterization** — a change of coordinates $y = g(x)$ scales the density by
$\lvert\partial g/\partial x\rvert^{-1}$, which moves the maximum. The least-squares solution
(= MAP) carries a weaker meaning than the intuition "the most probable point" suggests. The
posterior mean does not have this problem but is expensive to compute. Problem P5 builds a
concrete example.

## Proof sketch

### R1 — MAP = nonlinear least squares

**Hypotheses** H1: $z_k = h_k(\mathcal{X}_k) + \epsilon_k$ with
$\epsilon_k\sim\mathcal{N}(0,\Sigma_k)$. H2: the $\{\epsilon_k\}$ are independent. H3: $\Sigma_k$
is independent of $\mathcal{X}$ and $\Sigma_k \succ 0$.
**Conclusion** C: the two $\arg$ sets in (2) are the same.

**Strategy**: invariance under monotone transformations — $\arg\max f = \arg\min(-\log f)$, and a
term constant in $\mathcal{X}$ does not change the $\arg$.

1. **From product to sum.** H2 gives (5). Without H2 the joint likelihood does not split over
   factors and the objective is not representable by a factor graph — the graph *is* the picture
   of H2.
2. **$-\log$ preserves the $\arg$.** $\log$ is strictly increasing on $(0,\infty)$ and
   $x\mapsto -x$ is strictly decreasing, so $\arg\max_{\mathcal{X}} p = \arg\min_{\mathcal{X}}
   (-\log p)$. That $p > 0$ follows from H1 and H3 (a Gaussian density is positive everywhere).
3. **Separate the constant.** H3 makes $c$ in (6) independent of $\mathcal{X}$, and
   $\Sigma_k \succ 0$ gives the existence of $\Sigma_k^{-1}$ and $\log\det\Sigma_k$.
4. **Conclusion.** What remains is the right-hand side of (2), and steps 2 and 3 guarantee the
   $\arg$ is preserved. C.

**Delete a hypothesis**: dropping H3 breaks step 3 and leaves the $\log\det$ term of (7).
Dropping the Gaussian form of H1 keeps step 2 alive but what remains is not a sum of squares —
Cauchy noise, for instance, gives $\sum_k \log(1 + \lVert e_k\rVert^2/c^2)$, which is the
M-estimator of `c5-robust-global-estimation`. In other words **least squares is another name for
the Gaussian assumption**.

(Omitted: measurability of the densities and the existence of the $\arg\min$. Without a compact
domain or coercivity the $\arg\min$ can be empty — a pose graph with gauge freedom is the real
example; see the "delete a hypothesis" note of R3.)

### R3 — Gaussian elimination = the Schur complement

**Hypotheses** H1: $\Lambda \succ 0$ (symmetric positive definite). H2: the partition
$x = (x_1, x_{\mathcal{S}})$ with $\Lambda = \begin{bmatrix}\Lambda_{11} & \Lambda_{1\mathcal{S}}\\
\Lambda_{\mathcal{S}1} & \Lambda_{\mathcal{S}\mathcal{S}}\end{bmatrix}$.
**Conclusions** C1: $p(x) = p(x_1\mid x_{\mathcal{S}})\,q(x_{\mathcal{S}})$ exactly, and the
information matrix of $q$ is the Schur complement in (4). C2: $\int p(x)\,dx_1 =
q(x_{\mathcal{S}})$ — the **new factor created by elimination is the marginal**.

**Strategy**: complete the square in $x_1$. It finishes in algebra, not in an integral.

1. **Invertibility of $\Lambda_{11}$.** By H1 every principal submatrix is positive definite, so
   $\Lambda_{11}\succ 0$ and $\Lambda_{11}^{-1}$ exists.
2. **Collect the $x_1$ terms.** Writing the exponent as $f(x) = \tfrac12 x^\top\Lambda x -
   \eta^\top x$,
   $$
   f = \tfrac{1}{2}x_1^\top\Lambda_{11}x_1 + x_1^\top(\Lambda_{1\mathcal{S}}x_{\mathcal{S}} - \eta_1)
     + \tfrac{1}{2}x_{\mathcal{S}}^\top\Lambda_{\mathcal{S}\mathcal{S}}x_{\mathcal{S}}
     - \eta_{\mathcal{S}}^\top x_{\mathcal{S}}.
   $$
3. **Complete the square.** With $\mu := -\Lambda_{11}^{-1}(\Lambda_{1\mathcal{S}}x_{\mathcal{S}} - \eta_1)$,
   $$
   \tfrac{1}{2}x_1^\top\Lambda_{11}x_1 + x_1^\top(\Lambda_{1\mathcal{S}}x_{\mathcal{S}} - \eta_1)
     = \tfrac{1}{2}\lVert x_1 - \mu\rVert^2_{\Lambda_{11}^{-1}}
       - \tfrac{1}{2}(\Lambda_{1\mathcal{S}}x_{\mathcal{S}} - \eta_1)^\top\Lambda_{11}^{-1}
         (\Lambda_{1\mathcal{S}}x_{\mathcal{S}} - \eta_1).
   $$
   The first term gives $p(x_1\mid x_{\mathcal{S}}) = \mathcal{N}(\mu, \Lambda_{11}^{-1})$ —
   **the information matrix of the conditional is $\Lambda_{11}$ and does not depend on the
   separator.**
4. **Tidy up what is left.** Expanding the second term and using
   $\Lambda_{\mathcal{S}1} = \Lambda_{1\mathcal{S}}^\top$,
   $$
   f - \tfrac{1}{2}\lVert x_1 - \mu\rVert^2_{\Lambda_{11}^{-1}}
     = \tfrac{1}{2}x_{\mathcal{S}}^\top\big(\Lambda_{\mathcal{S}\mathcal{S}}
       - \Lambda_{\mathcal{S}1}\Lambda_{11}^{-1}\Lambda_{1\mathcal{S}}\big)x_{\mathcal{S}}
       - \big(\eta_{\mathcal{S}} - \Lambda_{\mathcal{S}1}\Lambda_{11}^{-1}\eta_1\big)^\top x_{\mathcal{S}}
       + \text{const},
   $$
   which is (4) together with $\eta^{\mathrm{new}}_{\mathcal{S}} = \eta_{\mathcal{S}} -
   \Lambda_{\mathcal{S}1}\Lambda_{11}^{-1}\eta_1$. C1.
5. **Identity with marginalization.** The first term of step 3 is a complete Gaussian in $x_1$, so
   $\int \exp(-\tfrac12\lVert x_1-\mu\rVert^2_{\Lambda_{11}^{-1}})dx_1 =
   \sqrt{(2\pi)^{d_1}/\det\Lambda_{11}}$ — a constant **independent of $x_{\mathcal{S}}$**. The
   integral therefore only rescales $q(x_{\mathcal{S}})$. C2.
6. **Fill-in.** The new factor in (4) creates a nonzero block for every pair in
   $\mathcal{S}(x_1)$ — the separator becomes a **clique**. The elimination order decides the
   sparsity, and finding the optimal order is NP-hard. That line is the starting point of
   `c5-sparsity-isam`.

**Delete a hypothesis**: dropping positive definiteness in H1 breaks step 1. The case that
actually occurs is **gauge freedom** — in a pose graph with only relative measurements, rigidly
transforming everything leaves $\chi^2$ unchanged, so $\Lambda$ is singular (a 3-dimensional null
space for $SE(2)$, 6-dimensional for $SE(3)$); and trying to eliminate a landmark that was never
observed makes $\Lambda_{11}$ singular. The fix is to add an anchor factor that fixes the gauge,
or to solve with a pseudo-inverse. Removing the anchor in the reproduction task confirms this
immediately.

(Omitted: that the Schur complement preserves positive definiteness,
$\Lambda\succ0 \Rightarrow \Lambda_{\mathcal{S}\mathcal{S}} -
\Lambda_{\mathcal{S}1}\Lambda_{11}^{-1}\Lambda_{1\mathcal{S}}\succ 0$. Problem P2 proves it.)

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R4)** Starting from (13) and (14), (a) derive the covariance update
$P = \bar P - K H \bar P$, and (b) show that eliminating $x_{0:K}$ in time order in a
linear-Gaussian chain and then substituting the conditionals in reverse order yields the
Rauch-Tung-Striebel smoother $\hat x_i^{s} = \hat x_i + C_i(\hat x_{i+1}^{s} - \bar x_{i+1})$
with $C_i = P_i F_i^\top \bar P_{i+1}^{-1}$.
*Solution sketch*: (a) put (14) into $P = \Lambda^{-1}$ and verify
$\Lambda^{-1} = \bar P - \bar P H^\top(H\bar PH^\top+R)^{-1}H\bar P$
(Sherman-Morrison-Woodbury). (b) read off from the $\mu$ expression in step 3 of R3 that the
conditional at the elimination of $x_i$ has the form
$p(x_i\mid x_{i+1}) = \mathcal{N}(\hat x_i + C_i(x_{i+1}-\bar x_{i+1}), \cdot)$, then substitute
the smoothed value for $x_{i+1}$. The point is that **back-substitution is smoothing**.

**P2 (proof, ★★, R3)** Show that $\Lambda \succ 0$ implies
$\Lambda_{\mathcal{S}\mathcal{S}} - \Lambda_{\mathcal{S}1}\Lambda_{11}^{-1}\Lambda_{1\mathcal{S}}
\succ 0$. Then show that **changing the elimination order does not change the final marginal**.
*Strategy and key inequality*: for the first part, plug
$x = (-\Lambda_{11}^{-1}\Lambda_{1\mathcal{S}}v,\, v)$ with $v \ne 0$ into $x^\top\Lambda x > 0$.
For the second, combine the fact that the definition of a marginal $\int p\,dx_{\text{elim}}$ does
not depend on the order of integration (Fubini) with C2 of R3 — that is, **the numerics (sparsity,
cost) depend on the order but the answer does not**. The expansion is hidden.

**P3 (numerical, ★, R1·R3·R5)** A one-dimensional pose graph: variables
$x_1,x_2,x_3\in\mathbb{R}$ and four factors — the prior $x_1 = 0\ (\sigma=0.1)$, odometry
$x_2-x_1 = 1.00\ (\sigma=0.1)$ and $x_3-x_2 = 1.00\ (\sigma=0.1)$, and the loop closure
$x_3-x_1 = 2.30\ (\sigma=0.2)$. Find (a) $\Lambda$ and $\eta$, (b) the MAP solution,
(c) $\chi^2$, (d) the marginal standard deviation of each variable. (e) Explain in one paragraph
why $x_1^\ast$ is **exactly** zero.
*Answer*: (a) $\Lambda = \begin{bmatrix}225 & -100 & -25\\ -100 & 200 & -100\\ -25 & -100 & 125\end{bmatrix}$
and $\eta = (-157.5,\ 0,\ 157.5)^\top$. (b) $x^\ast = (0,\ 1.05,\ 2.10)^\top$.
(c) $\chi^2 = 1.5$ (residuals $(0,\ 0.5,\ 0.5,\ -1.0)$). (d) $(0.1,\ 0.13540064,\ 0.15275252)
=(0.1, \sqrt{11/600}, \sqrt{7/300})$. Tolerance $10^{-8}$.
Check it: verify $\Lambda x^\ast = \eta$ directly, then re-solve for $(x_2,x_3)$ from the marginal
information matrix $\frac{1}{9}\begin{bmatrix}1400 & -1000\\ -1000 & 1100\end{bmatrix}$ obtained by
eliminating $x_1$ and confirm the same values.
*Grading point for (e)*: reparameterizing as $(x_1,\ d_1 = x_2-x_1,\ d_2 = x_3-x_2)$ makes the
prior touch only $x_1$ and the other three factors touch only $(d_1,d_2)$, so the **Jacobian is
block diagonal**. Gauge and shape decouple, so the inconsistency of the loop closure never flows
into $x_1$. "It just happens to be" does not pass.

**P4 (implementation, ★★, R2·R3)** Write a **direct variable-elimination solver** for the
$\Lambda$ of the reproduction task: apply (4) repeatedly in a given order, stack the conditionals,
and back-substitute in reverse to get the solution.
*Rubric*: (a) the solution matches `numpy.linalg.solve` to within $10^{-9}$; (b) the conditionals
are stored so that back-substitution actually works; (c) changing the elimination order leaves the
solution unchanged (to $10^{-9}$) while the number of nonzeros created differs, reported
numerically; (d) removing the anchor factor makes $\Lambda_{11}$ or the final block singular,
reproduced along with the dimension of the null space from a numerical rank (3, since this is an
$SE(2)$ pose graph).

**P5 (counterexample, ★★, R1·R5)** Show that the claim "the MAP solution is the most probable
state, so it does not depend on the choice of coordinates" is false. (a) In one dimension,
construct a concrete non-Gaussian posterior where reparameterizing as $y = x^3$ moves the MAP;
(b) for a landmark with a single range-bearing measurement, give numbers showing that the
Cartesian MAP and the polar MAP differ.
*Property checklist*: (a) must use the density transformation
$p_Y(y) = p_X(g^{-1}(y))\lvert dg^{-1}/dy\rvert$ and point at the Jacobian term as what moves the
maximum. (b) must contrast this with the posterior **mean**, which gives the same physical point
in both coordinates (it transforms as an expectation of a measurable quantity) while the MAP does
not. "Because it is nonlinear" does not pass.

**P6 (paper, ★★, R2)** Read sections 3-5 of `dellaert2006-square-root-sam` and (a) state in at
most three sentences the authors' argument for the square root information matrix over the
information matrix, connected to (9); (b) name three pieces of information **missing** for
reproducing the paper's timing table; (c) is any conclusion of the paper no longer true as of
2026?
*Rubric*: (a) passes if it points at the squared condition number and at the incremental
updatability of sparse QR. (b) passes with roughly three of: the concrete settings of the variable
ordering algorithm, the hardware and BLAS implementation, the loop-closure statistics of the
datasets. (c) is excellent if it argues, with evidence, either that "incremental updating was
superseded by the Bayes tree of iSAM2" or that "modern sparse Cholesky (CHOLMOD) beats sparse QR
on many problems".

## Paper reading

**Two must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read with 3-pass and attack questions 4, 5, 6 and 7 on the third pass.

1. **Dellaert & Kaess, "Factor Graphs for Robot Perception" (2017, Foundations and Trends in
   Robotics)** — role: `survey`. <https://doi.org/10.1561/2300000043> (sections 2-4)
   Extra questions: (a) map the conversion between a Bayes net and a factor graph in this text onto
   the "conditional + new factor" decomposition of R3; (b) why does the authors' procedure for
   marginal covariances avoid forming all of $\Lambda^{-1}$?
2. **Dellaert & Kaess, "Square Root SAM" (2006, IJRR)** — role: `seminal`.
   <https://doi.org/10.1177/0278364906072768> (sections 3-5)
   Extra questions: (a) how many digits does the squared condition number of (9) actually cost on a
   real pose graph — use the $\kappa(\Lambda)$ of the reproduction task; (b) were the baselines the
   authors compared against tuned fairly?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) the independent and dependent variables and the baselines — were they tuned fairly?
(6) does the metric match the claim, and are variance and seeds reported? (7) what is missing for
reproduction? (8) if the result were wrong, which assumption would you doubt first?
(9) computational and memory complexity, and real-time feasibility. (10) what would you change to
surpass it in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one laptop CPU core, under 30 seconds, under
200 MB. Only numpy and scipy.sparse.

**The input data** is produced by the generator below (fixed seed). No external dataset is needed.

```python
"""c5-factor-graphs-map reproduction task: the two-lap SE(2) pose graph generator."""

import numpy as np

SEED = 20261112
SIGMA_ODOM = np.array([0.02, 0.02, 0.01])
SIGMA_LOOP = np.array([0.05, 0.05, 0.02])
SIGMA_ANCHOR = np.array([1e-3, 1e-3, 1e-3])


def wrap(a):
    """Wrap an angle to (-pi, pi]."""
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def rot(t):
    """2x2 rotation matrix."""
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]])


def between(xi, xj):
    """The noiseless relative measurement T_i^{-1} T_j in (dx, dy, dtheta) coordinates."""
    return np.array([*(rot(xi[2]).T @ (xj[:2] - xi[:2])), wrap(xj[2] - xi[2])])


def make_graph(laps=2, per_lap=50, radius=5.0, every=10):
    """Ground truth, edges and noisy measurements of a two-lap circular pose graph."""
    rng = np.random.default_rng(SEED)
    n = laps * per_lap
    ang = 2.0 * np.pi * np.arange(n) / per_lap
    gt = np.column_stack([radius * np.cos(ang), radius * np.sin(ang), wrap(ang + np.pi / 2)])
    edges = [(i, i + 1, SIGMA_ODOM) for i in range(n - 1)]
    edges += [(i, i + per_lap, SIGMA_LOOP) for i in range(0, per_lap, every)]
    meas = [between(gt[i], gt[j]) + s * rng.standard_normal(3) for i, j, s in edges]
    return gt, edges, np.array(meas)
```

$n = 100$ poses, $104$ edges (99 odometry + 5 loop closures) and 1 anchor factor, so
$M = 3\cdot104 + 3 = 315$ residual rows, $N = 300$ variables and $M - N = 15$ degrees of freedom.

**What to do.** The variables are $x_i = (p_{x,i}, p_{y,i}, \theta_i) \in \mathbb{R}^3$
(parameterized directly as coordinates — why that is the wrong choice is treated in
`c5-manifold-estimation`). Take the residual in the same form as g2o's `EdgeSE2`,

$$
r_{ij}(x) = \begin{bmatrix}
  R(\bar\theta_{ij})^\top\big(R(\theta_i)^\top(p_j - p_i) - \bar p_{ij}\big) \\
  \mathrm{wrap}(\theta_j - \theta_i - \bar\theta_{ij})
\end{bmatrix} \in \mathbb{R}^3 \tag{15}
$$

and write the Jacobians analytically. With $d := p_j - p_i$ and
$\widehat{1} := \begin{bmatrix}0 & -1\\ 1 & 0\end{bmatrix}$,

$$
\frac{\partial r_{1:2}}{\partial p_i} = -R_{\bar\theta}^\top R_{\theta_i}^\top, \quad
\frac{\partial r_{1:2}}{\partial \theta_i} = -R_{\bar\theta}^\top \widehat{1} R_{\theta_i}^\top d, \quad
\frac{\partial r_{1:2}}{\partial p_j} = R_{\bar\theta}^\top R_{\theta_i}^\top, \quad
\frac{\partial r_3}{\partial(\theta_i,\theta_j)} = (-1,\, +1). \tag{16}
$$

(These come from $\partial R_{\theta}^\top/\partial\theta = -\widehat{1}R_\theta^\top$; expand it
yourself to check.) The initial guess is **dead reckoning that does not use the loop closures**:
put the anchor pose at ground truth and accumulate odometry only.

**Acceptance criteria — all four conditions must hold.**

1. **Sparse and dense agree**: the solution from `scipy.sparse.linalg.spsolve` and the solution
   from building $\Lambda$ densely and calling `numpy.linalg.solve` satisfy
   $\lVert x_{\text{sparse}} - x_{\text{dense}}\rVert_\infty < 10^{-9}$. (The reference
   implementation measures $8.9\times10^{-16}$.)
2. **Convergence**: $\chi^2$ decreases monotonically (tolerance $10^{-9}$), within 8 iterations
   $\lVert\delta\rVert_\infty < 10^{-13}$ is reached, and the final
   $\lVert\eta\rVert_\infty = \lVert A^\top b\rVert_\infty < 10^{-8}$.
3. **Reference values**: with the seed above the $\chi^2$ sequence is
   $296.0248 \to 16.7131 \to 15.3077 \to \cdots$ and the final $\chi^2 = 15.3077 \pm 10^{-3}$.
   With 15 degrees of freedom, $\chi^2/\mathrm{dof} = 1.02$ — **evidence that the noise model
   matches the generating process**. A ratio far from 1 should make you suspect the $\Sigma$
   settings or the whitening.
4. **Accuracy and Jacobians**: the ATE (position RMSE) improves from $0.3790$ to $0.1031$
   ($\pm10^{-3}$). The analytic Jacobians agree with central differences: with a step
   $h = 10^{-5}$, $\max\lvert J_{\text{analytic}} - J_{\text{fd}}\rvert < 10^{-7}$.

**Baselines**: (a) dense `numpy.linalg.solve` (condition 1 is itself the baseline); (b) dead
reckoning that ignores the loop closures (ATE 0.3790). Optional: solve the same residual with
`scipy.optimize.least_squares(method="trf", jac=...)` and check that $\chi^2$ agrees to within
$10^{-6}$.

**Numbers to report**: the $\chi^2$ sequence, the iteration count, $\kappa(\Lambda)$ (the
reference implementation gives $1.73\times10^6$, so $\kappa(A)\approx1.3\times10^3$ by (9)), the
number of nonzeros in $\Lambda$ (reference 1736 out of 90000) and in its Cholesky factor
(reference 3396). The ratio of those last two is **fill-in** and the subject of
`c5-sparsity-isam`.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| Initial $\chi^2$ above $10^4$ | missing angle wrapping — $\theta_j-\theta_i-\bar\theta$ exceeds $2\pi$ | histogram the third component of the residuals and look for values outside $\pm\pi$ |
| `spsolve` warns about a singular matrix | no anchor factor, so the gauge freedom is 3-dimensional | look at the three smallest eigenvalues of $\Lambda$ ($\approx 0$) and check that the null vectors are global translation and rotation |
| Some iteration increases $\chi^2$ | the dropped second-order term of GN (the failure mode of R2), or a Jacobian sign error | verify the Jacobians by central differences; if it still increases, add LM damping |
| $\chi^2/\mathrm{dof} \gg 1$ | $\Sigma$ set differently from the generating process, or whitening by $\sigma^2$ instead of $\sigma$ | check that the weight is $1/\sigma$ — divide by the **standard deviation**, not the covariance |
| Sparse and dense agree only to $10^{-6}$ | $\Lambda$ assembled asymmetrically, or CSR passed to `spsolve` so it takes the LU path | print $\lVert\Lambda-\Lambda^\top\rVert_\infty$ and pass CSC |

## Open problems

- **(Open problem) Putting learned heteroscedastic uncertainty into a factor graph consistently** —
  because of the $\log\det\Sigma(\mathcal{X})$ term in (7), using a network's covariance output
  directly as a weight pulls the objective towards solutions that "report large noise". Current
  approaches correct the covariance with a negative log-likelihood at training time (see the
  [control-as-inference view](https://arxiv.org/abs/1805.00909)) or attach distribution-free
  guarantees post hoc ([conformal prediction](https://arxiv.org/abs/2107.07511),
  [system-level OOD](https://arxiv.org/abs/2212.14020)). What is missing: design rules for using a
  learned covariance while preserving the **consistency** of the back-end estimator.
- **(Open problem) How to live with MAP not being reparameterization invariant** — R5(b) means the
  "least-squares solution" depends on the choice of coordinates, and for manifold variables the
  choice of retraction is added on top. The posterior mean and variational approximations are
  invariant but expensive. Current approaches: the variational inference of
  [Barfoot SER ch.6](https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf) and the left/right
  convention results of [micro Lie theory](https://arxiv.org/abs/1812.01537). What is missing: a
  quantitative study of how much the coordinate dependence of MAP actually costs in accuracy at
  robotics scale.
- **(Open problem) The treewidth barrier for exact inference** — what step 6 of R3 says is that
  cost is decided by the fill-in of the elimination order, that is, by the treewidth of the graph.
  In long-lived graphs with dense loop closures the treewidth grows and exact inference becomes
  impossible. Current approaches: sparsification and marginalization to shrink the graph,
  [incremental relinearization](https://doi.org/10.1177/0278364911430419), and the map-lifetime
  discussion of the [long-term SLAM survey](https://arxiv.org/abs/1606.05830). What is missing:
  sparsification that bounds the treewidth while quantitatively guaranteeing the information loss.

## Concept check

Run `rc quiz c5-factor-graphs-map`. The quiz is for **concept checking only**; the real work is
the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: the extra $\log\det\Sigma(\mathcal{X})$ term that appears when the
measurement covariance depends on the state; whether the Kalman filter estimate equals the
marginal of the full smoothing solution in a linear-Gaussian system; the information matrix of the
factor created by eliminating a variable; the numerical reason to obtain $\mathsf{R}$ by QR
instead of forming $\Lambda$; and whether an $SE(2)$ pose graph with only relative measurements
can be eliminated without an anchor factor.

## How to study this stage

1. **Draw the graph first (30 min)** — draw the reproduction task's graph (100 poses, 99 odometry
   edges, 5 loop closures, 1 anchor) by hand and shade the nonzero pattern of $\Lambda$ on paper.
   Once you can see which edge fills which block, the fill-in of R3 becomes obvious.
2. **Rewrite R1 from a blank page (45 min)** — reconstruct (5) → (6) → (2) with the book closed.
   In the margin, write **which line used which assumption**. If you can say why the $\log\det$
   term of (7) is there, half of this lesson is done.
3. **Do one elimination by hand (60 min)** — eliminate $x_1$ on paper in the $3\times3$ problem of
   P3 to get $\frac19\begin{bmatrix}1400&-1000\\-1000&1100\end{bmatrix}$, then recover $x_1$ by
   back-substitution. Read Barfoot SER ch.3 alongside, as **the same result in different notation**.
4. **Re-derive the filter as least squares (60 min)** — write (11) → (13) and prove (14) by hand.
   When you can state "the filter is one particular elimination order of smoothing" in your own
   words, R4 is done. Read SER ch.3.3 (batch vs recursive) with it.
5. **Run the reproduction task wrong on purpose first (135 min)** — run it **without** angle
   wrapping and watch the initial $\chi^2$ explode; run it **without** the anchor and watch the
   singular matrix; flip one sign in the Jacobian and watch $\chi^2$ increase. Then fix them. The
   goal is to produce the five rows of the diagnosis table yourself.
6. **Read the papers with the numbers in hand (120 min)** — read Square Root SAM sections 3-5 with
   $\kappa(\Lambda) = 1.73\times10^6$ and the fill-in ratio (1736 → 3396) noted down. Comparing the
   paper's claims against your own graph changes the reading speed. Write the one-page note per
   paper **without exception**.
7. **End at what cannot be done (30 min)** — pick one of the three open problems and write one
   paragraph on why it is still open.

**Passing bar**: you can derive (2) and (4) from a blank page, you can prove (14), you have code
that satisfies all four conditions of the reproduction task, and you have notes on both papers.
