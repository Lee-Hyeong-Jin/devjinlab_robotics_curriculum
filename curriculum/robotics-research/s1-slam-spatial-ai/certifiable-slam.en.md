---
id: s1-certifiable-slam
lang: en
title: Certifiable SLAM
summary: >-
  Derive how to **check after solving** whether the solution found by pose-graph optimization is
  the global optimum. Eliminate the translations in closed form to obtain the rotation-only
  problem $\min\operatorname{tr}(QR^\top R)$, and prove that if the certificate matrix
  $S = Q - \Lambda$ arising from its Lagrangian dual is positive semidefinite, the solution is
  globally optimal and the semidefinite relaxation is tight. When certification fails, the lower
  bound $f^\star \ge f(\hat R) + nd\,\lambda_{\min}(S)$ still remains. Numerically, show that on a
  ring graph 66% of random initializations fall into uncertified local minima, that the
  relaxation stops being tight once the rotation noise exceeds 0.3 rad, and that loop closures
  displaced by one place through perceptual aliasing inflate the ATE by a factor of 4 to 9
  **while remaining certified**.
objectives:
  - Derive, for pose-graph optimization, the rotation-only problem and its data matrix by eliminating the translations.
  - Prove by weak duality that positive semidefiniteness of the certificate matrix implies global optimality.
  - Show that when certification holds the semidefinite relaxation is tight, and derive the lower bound on the optimum when it fails.
  - Tell local from global minima with the certificate and measure the breakdown of tightness with noise.
  - Distinguish what the certificate guarantees (optimality for the given problem) from what it does not (correctness of the map).
tags: [slam, certifiable, semidefinite-relaxation, lagrangian-duality, pose-graph, research]
---

# Certifiable SLAM

## Setup and notation

`c5-robust-global-estimation` treated the certification of global optimality for $SO(2)$ rotation
synchronization. This lesson extends it to **the whole of pose-graph optimization** (rotations +
translations) and works out to the end what the certificate does and does not say in actual
SLAM. Pose graphs and loop closures are those of `s1-loop-closure-lifelong`. The recommended
prerequisites are those two lessons.

| Symbol | Meaning |
|---|---|
| $(R_i, t_i) \in SE(d)$ | Pose $i = 1,\dots,n$. The numbers of this lesson are for $d = 2$, the arguments for any $d$ |
| $(\tilde{R}_{ij}, \tilde{t}_{ij})$ | Relative pose measurement of edge $(i,j)$. $\tilde{R}_{ij} \approx R_i^\top R_j$, $\tilde{t}_{ij} \approx R_i^\top(t_j - t_i)$ |
| $\kappa_{ij}$, $\tau_{ij}$ | Weights (precisions) of the rotation and translation measurements |
| $R = [R_1\ \cdots\ R_n] \in \mathbb{R}^{d\times dn}$ | The rotations stacked horizontally |
| $Q \in \mathbb{S}^{dn}$ | The data matrix after eliminating the translations. $f(R) = \operatorname{tr}(QR^\top R)$ |
| $\Lambda$ | Symmetric matrix that is block diagonal with $d\times d$ blocks (the Lagrange multiplier) |
| $S = Q - \Lambda$ | The **certificate matrix**. $S \succeq 0$ implies global optimality |
| $Z = R^\top R \in \mathbb{S}^{dn}$ | The variable of the semidefinite relaxation. $Z \succeq 0$, diagonal blocks $= I_d$ |
| Tight | The optimal value of the relaxation equals that of the original problem (the solution of the relaxation has rank $d$) |

**The plan of this lesson.**

| Stage | What is done | Result |
|---|---|---|
| Formulation | Eliminate the translations to get a quadratic problem in the rotations only | R1 |
| Certification | Build $S$ from the dual and check $S \succeq 0$ | R2 |
| Relaxation | Certification = tightness of the relaxation. A lower bound on failure | R3 |
| Landscape | When local minima arise and how the certificate separates them | R4 |
| Limits | A certified solution can be a wrong map | R5 |

## Key results

The bracket gives the derivation depth (D0 cited / D1 skeleton / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (eliminating the translations, and the data matrix) [D2]** — in the maximum-likelihood
  problem of a pose graph
  $$
  \min_{R_i\in SO(d),\,t_i}\ \sum_{(i,j)}\kappa_{ij}\lVert R_j - R_i\tilde{R}_{ij}\rVert_F^2
   + \tau_{ij}\lVert t_j - t_i - R_i\tilde{t}_{ij}\rVert^2 \tag{1}
  $$
  the translations, once the rotations are fixed, are solved in closed form by linear least
  squares, and substituting leaves
  $$
  \min_{R\in SO(d)^n}\ \operatorname{tr}(QR^\top R), \qquad
  Q = L(G^\rho) + V\,\Omega^{1/2}\Pi\,\Omega^{1/2}V^\top \tag{2}
  $$
  ($L(G^\rho)$: the connection Laplacian of the rotation measurements; $\Pi$: the projection
  orthogonal to the row space of the weighted incidence matrix). The reproduction task confirms
  the agreement of the two objectives to $10^{-9}$.
- **R2 (the certificate: $S \succeq 0$ implies global optimality) [D3]** — for a feasible
  $\hat{R}$ put
  $$
  \Lambda = \operatorname{SymBlockDiag}\big(Q\hat{R}^\top\hat{R}\big), \qquad S = Q - \Lambda. \tag{3}
  $$
  If $S \succeq 0$ then $\hat{R}$ is a **global minimizer** of (2) (even over the whole
  orthogonal group $O(d)^n$). The check is the computation of a single eigenvalue
  $\lambda_{\min}(S)$ and does not depend on which algorithm produced the solution.
- **R3 (certification = tightness, and a lower bound on failure) [D3]** — if $S \succeq 0$ then
  $\hat{Z} = \hat{R}^\top\hat{R}$ solves the semidefinite relaxation
  $\min\{\operatorname{tr}(QZ) : Z\succeq0,\ Z_{ii} = I_d\}$ — the relaxation is tight. Even if
  $S \not\succeq 0$,
  $$
  f^\star \;\ge\; f(\hat{R}) + nd\,\lambda_{\min}(S) \tag{4}
  $$
  holds, which gives **an upper bound** $nd\,\lvert\lambda_{\min}(S)\rvert$ **on the
  suboptimality gap**. It is known that the relaxation is tight when the noise is below some
  threshold **[D0]** (the exact-recovery proposition of `rosen2019-se-sync`).
- **R4 (local minima and the breakdown of tightness) [D2]** — (a) on a graph with many loop
  closures (60 poses, 40 loops, $\sigma = 0.1$) **200/200** random initializations converge to
  the same solution and are certified. (b) On a ring graph (30 poses, 1 loop closure) only **103
  of 300** reach the global minimum ($f = 1.712$) and are certified, and 197 fall into local
  minima (the nearest has $f = 1522.2$, $\lambda_{\min}(S) = -26.3$). The objective values of the
  certified solutions are **all equal**. (c) As the rotation noise grows, successful
  certification collapses as $10/10, 8/10, 1/10$ at $\sigma_R = 0.1, 0.3, 0.6$ rad, and at $0.6$
  the relative gap between the best local solution and the rank-3 relaxation value has a median
  of $2.6\%$ — **the relaxation is no longer tight**.
- **R5 (the certificate does not speak about the correctness of the map) [D2]** — the
  certificate asserts global optimality of the objective **for the given measurements**. With 2
  loop closures displaced by one place through perceptual aliasing the solution is still
  **certified** while the ATE goes $0.064 \to 0.235$, a factor of 3.7, and with 4 displaced by
  two places it is $0.604$, a factor of 9.4. Conversely one gross outlier linking unrelated
  places breaks certification ($\lambda_{\min}(S) = -1308$). **What the certificate catches is a
  large contradiction among the measurements, not a plausible falsehood.**

## Derivation

### R1 — eliminating the translations

**In matrix form.** Let $t = [t_1\ \cdots\ t_n] \in \mathbb{R}^{d\times n}$ and let the incidence
vector of edge $e = (i,j)$ be $a_e \in \mathbb{R}^n$ ($-1$ at $i$, $+1$ at $j$), so that
$t\,a_e = t_j - t_i$. Let $V_e \in \mathbb{R}^{dn}$ carry $\tilde{t}_e$ in its $i$-th block and
zeros elsewhere, so that $RV_e = R_i\tilde{t}_e$. With the incidence matrix $A = [a_e]$,
$V = [V_e]$ and $\Omega = \operatorname{diag}(\tau_e)$ the translation term of (1) becomes

$$
\sum_e\tau_e\lVert t\,a_e - RV_e\rVert^2 = \big\lVert(tA - RV)\Omega^{1/2}\big\rVert_F^2. \tag{5}
$$

**Solve for $t$.** (5) is a convex quadratic in $t$ with stationarity condition
$(tA - RV)\Omega A^\top = 0$, that is

$$
t^\star = RV\Omega A^\top\big(A\Omega A^\top\big)^\dagger. \tag{6}
$$

$A\Omega A^\top$ is the weighted graph Laplacian and has the constant vector in its null space
(the gauge of a global translation), hence the pseudo-inverse.

**Substitute.** Since $tA - RV = RV\big(\Omega A^\top(A\Omega A^\top)^\dagger A - I\big)$,

$$
(tA - RV)\Omega^{1/2} = -RV\Omega^{1/2}\underbrace{\big(I - \Omega^{1/2}A^\top(A\Omega A^\top)^\dagger A\Omega^{1/2}\big)}_{=:\,\Pi},
$$

where $\Pi$ is the **projection** orthogonal to the column space of $\Omega^{1/2}A^\top$
($\Pi^2 = \Pi = \Pi^\top$). The minimum of the translation term is therefore
$\operatorname{tr}\big(RV\Omega^{1/2}\Pi\Omega^{1/2}V^\top R^\top\big)$.

**The rotation term.** Since
$\lVert R_j - R_i\tilde{R}_{ij}\rVert_F^2 = 2d - 2\operatorname{tr}(\tilde{R}_{ij}R_j^\top R_i)$,
the **connection Laplacian** $L(G^\rho)$ with blocks $\kappa_{ij}I$ at $(i,i)$ and $(j,j)$,
$-\kappa_{ij}\tilde{R}_{ij}$ at $(i,j)$ and $-\kappa_{ij}\tilde{R}_{ij}^\top$ at $(j,i)$ gives
$\sum\kappa\lVert\cdot\rVert_F^2 = \operatorname{tr}(L(G^\rho)R^\top R)$. Adding the two yields
(2).

**How to read it.** (a) The variables went from $n(d + d(d-1)/2)$ to rotations only. (b) The
objective is a **quadratic** in $R$ and the constraints $R_i^\top R_i = I$ are quadratic
equalities — a quadratically constrained quadratic program (QCQP), and that structure is what
makes the dual of R2 closed form. (c) $Q \succeq 0$, and without noise the true rotations
$R^\natural$ satisfy $QR^{\natural\top} = 0$ (objective value 0).

**Where the assumptions break**: (1) is the maximum likelihood for **isotropic** noise (Langevin
on the rotations, isotropic Gaussian on the translations). The covariances of real odometry and
loop closures are anisotropic (elongated in the forward direction), and then (1) is an
approximation rather than the likelihood — the certificate certifies **the optimality of (1)**,
not the optimality of the actual likelihood. And $\Omega$ must be a scalar per edge for the
elimination (6) to close in this form.

### R3 — relaxation, tightness, lower bound

**The semidefinite relaxation.** $Z = R^\top R$ satisfies $Z \succeq 0$,
$\operatorname{rank}Z = d$ and diagonal blocks $Z_{ii} = R_i^\top R_i = I_d$. Dropping the rank
constraint gives the convex problem

$$
f_{\mathrm{SDP}} = \min\ \operatorname{tr}(QZ) \quad\text{s.t.}\quad Z\succeq0,\ Z_{ii} = I_d\ (i = 1,\dots,n) \tag{7}
$$

with $f_{\mathrm{SDP}} \le f^\star$ (the feasible set got larger).

**If certification holds it is tight.** For any feasible $Z$ of (7),

$$
\operatorname{tr}(QZ) = \operatorname{tr}(SZ) + \operatorname{tr}(\Lambda Z)
 = \operatorname{tr}(SZ) + \sum_i\operatorname{tr}(\Lambda_iZ_{ii})
 = \operatorname{tr}(SZ) + \operatorname{tr}\Lambda \;\ge\; \operatorname{tr}\Lambda, \tag{8}
$$

where the second equality is that $\Lambda$ is block diagonal, the third is $Z_{ii} = I$, and the
inequality is $\operatorname{tr}(SZ)\ge0$ from $S\succeq0$, $Z\succeq0$. And since
$\operatorname{tr}(Q\hat{Z}) = \operatorname{tr}\Lambda$ (step 2 of the proof sketch), $\hat{Z}$
attains the minimum of (7). That is, $f_{\mathrm{SDP}} = f(\hat{R}) = f^\star$ — **the solution
of the relaxation has rank $d$ and is the solution of the original problem.**

**If certification fails, a lower bound.** Even when $S\not\succeq0$ the first two equalities of
(8) hold. For $Z = R^\top R$ ($R$ feasible),
$\operatorname{tr}(SR^\top R) = \operatorname{tr}(RSR^\top) \ge \lambda_{\min}(S)\lVert R\rVert_F^2 = nd\,\lambda_{\min}(S)$,
so

$$
f(R) \ge \operatorname{tr}\Lambda + nd\,\lambda_{\min}(S) = f(\hat{R}) + nd\,\lambda_{\min}(S)
$$

for every feasible $R$, and taking $R$ optimal gives (4). **Even without knowing whether the
solver fell into a local minimum, one obtains a number saying "the optimum is at least this".**

**Numbers — the local minima of a ring graph.** A graph of 30 poses on a circle whose edges are
29 odometry edges + 1 loop closure ($\sigma_R = \sigma_t = 0.03$). The results of local search
from 300 random initializations:

| Solution reached | Count | $f$ | $\lambda_{\min}(S)$ | Lower bound (4) | ATE (m) |
|---|---|---|---|---|---|
| Global minimum | 103 | $1.712$ | $-6\times10^{-15}$ | $1.712$ | $0.069$ |
| Local minimum A | 83 | $1522.2$ | $-26.31$ | $-56.3$ | $5.24$ |
| Local minimum B | 35 | $5068.9$ | $-235.8$ | $-9078$ | $3.38$ |
| Other local minima | 79 | $5040$–$12918$ | $< -200$ | — | $> 3$ |

Local minimum A is the solution that closes the ring with one **twist** (a different winding
number of the rotations). **Three things to read.** (a) The $f$ of the 103 certified solutions
agree to four decimals — the certificate does not mix the global minimum with anything else.
(b) The lower bound at local minimum A is $-56.3$, below the truth $1.712$ — the bound is
**valid** (at most $f^\star$ in all 300) but not tight enough to be useful. The actual gap
$1520.5$ is $96\%$ of the bound on the gap, $nd\lvert\lambda_{\min}\rvert = 1578.5$. (c) The ATE
of the local minima is $5$ m. **Having converged is not having got it right** — the termination
condition of the iteration (zero gradient) is met in all 197.

**Numbers — tightness against noise.** Ten graphs of 40 poses and 20 loops each; the certificate
is applied to the best of 6 initializations (the truth + 5 random), and the relaxation (7) is
solved through a rank-3 factorization ($Z = Y^\top Y$, $Y_i \in \mathrm{St}(2,3)$) to measure the
gap:

| $\sigma_R$ (rad) | Certified | Relative gap $(f - f_{\mathrm{rank3}})/f_{\mathrm{rank3}}$, median (max) | Rank-3 solution certified |
|---|---|---|---|
| $0.1$ | $10/10$ | $0$ ($2\times10^{-13}$) | $10/10$ |
| $0.3$ | $9/10$ | $0$ ($8\times10^{-4}$) | $10/10$ |
| $0.6$ | $0/10$ | $2.6\%$ ($10.4\%$) | $8/10$ |
| $0.9$ | $0/10$ | $7.5\%$ ($20.3\%$) | $3/10$ |
| $1.2$ | $0/10$ | $10.4\%$ ($25.9\%$) | $0/10$ |

(This table is from a run that solved the rank-3 problem alongside, whose random numbers are
interleaved, so its sample of graphs differs from Part D of the reproduction task. Under the
protocol of Part D as written, successful certification is $10/10, 8/10, 1/10, 0/10$.)

Up to $\sigma_R \le 0.3$ rad ($17^\circ$) the relaxation is (almost) tight, and above that it is
not. The rotation noise of actual SLAM is at the level of $0.01$–$0.1$ rad, so **in the absence
of outliers** it is mostly in the tight regime — this is why certifiable SLAM is practical. The
last column is the fraction in which the rank-3 solution itself is certified as the solution of
(7); its failure for $\sigma_R \ge 0.9$ means that the solution of the relaxation has rank above
3 (the staircase of R4 has to be climbed further).

**Where the assumptions break**: (a) the lower bound (4) is **always valid** but can be loose, as
in the table above. A tight bound requires actually solving the relaxation (7). (b) The
certificate proves optimality over $O(d)^n$. If the solution of the $O(d)$ relaxation contains
reflections (blocks with $\det = -1$), the true solution of the $SO(d)$ problem is not certified
by this certificate — this happens at high noise, and then "certification failed" does not mean
"not globally optimal". (c) $\lambda_{\min}(S)$ is computed numerically, so a threshold is
needed. At the global minimum $\lambda_{\min}(S)$ is exactly 0 ($S\hat{R}^\top = 0$) and the
computed value is around $\pm10^{-12}$. Unless the threshold is relative to the size of $Q$,
large problems give false negatives.

### R4 — landscape and staircase

**When do local minima arise?** Put the two experiments above side by side.

| Graph | Fraction of random initializations reaching the global minimum |
|---|---|
| 60 poses, 59 odometry edges + 40 loops, $\sigma = 0.1$ | $200/200$ |
| Ring: 30 poses, 29 odometry edges + 1 loop, $\sigma = 0.03$ | $103/300$ |

The noise is **smaller** on the ring, yet only the ring has local minima. What sets the landscape
is not so much the noise as **the connectivity of the graph** — on a ring with a single loop, a
configuration with one more turn of rotation contradicts none of the other edges and pays only
on the one loop closure. With many loops such a configuration contradicts several edges at once
and cannot be a stationary point.

**The Riemannian staircase (skeleton).** Solving the relaxation (7) directly has a
$dn\times dn$ variable. Instead **factor at rank $r$**: $Z = Y^\top Y$,
$Y = [Y_1\ \cdots\ Y_n]$, $Y_i \in \mathrm{St}(d, r)$ ($r \times d$ with orthonormal columns),
and optimize $\min\operatorname{tr}(QY^\top Y)$ locally on the Stiefel manifold. With $r = d$ it
is the original problem (the $O(d)$ version). The key fact **[D1]**: if a second-order critical
point $Y$ of the rank-$r$ problem is **rank deficient** ($\operatorname{rank}Y < r$), then
$Y^\top Y$ is a global solution of (7). So the algorithm starts at $r = d$, checks the
certificate (3) (the same formula serves for any $r$ —
$\Lambda_i = \operatorname{sym}(Y_i^\top(YQ)_i)$), and on failure climbs to $r \leftarrow r + 1$
along the negative eigenvector of $S$. The negative eigenvector gives **a descent direction**, so
it escapes the local minimum. This is SE-Sync (`rosen2019-se-sync` §5,
`boumal2016-burer-monteiro`).

Applied to the ring graph above: at local minimum A, $\lambda_{\min}(S) = -26.3$, so adding one
dimension and descending along that eigenvector undoes the twist — the global minimum that lay
beyond a barrier in two dimensions is connected by a downhill path in three.

**Where the assumptions break**: the staircase finds the solution of the relaxation (7). If the
relaxation is not tight ($\sigma_R \ge 0.6$ in the table above), what one gets at the top of the
staircase is a $Y$ of rank above $d$, and the solution obtained by **rounding** it to $SO(d)^n$
carries no guarantee of global optimality — but $f_{\mathrm{SDP}}$ gives a lower bound, so the
gap can be reported. And the fact "rank deficient implies global" concerns **second-order**
critical points, so it does not hold if a first-order method stalls at a saddle.

### R5 — what the certificate does not say

The certificate says "this $\hat{R}$ is the global minimizer **for this $Q$**". $Q$ is built from
the measurements, and if the measurements are wrong so is $Q$.

**Experiment.** On a graph of 40 poses and 20 loops with $\sigma_R = \sigma_t = 0.05$, a few loop
closures are replaced.

| What was replaced | $f$ | $\lambda_{\min}(S)$ | Certified | ATE (m) |
|---|---|---|---|---|
| Nothing | $61.4$ | $-2\times10^{-12}$ | yes | $0.064$ |
| 1 gross outlier (random relative pose) | $32528$ | $-1308$ | **no** | $5.76$ |
| 2 aliased (off by one place) | $454.1$ | $-2\times10^{-12}$ | **yes** | $0.235$ |
| 4 aliased (off by one place) | $716.0$ | $-1\times10^{-12}$ | **yes** | $0.264$ |
| 4 aliased (off by two places) | $2505.6$ | $4\times10^{-13}$ | **yes** | $0.604$ |
| 8 aliased (off by one place) | $1225.8$ | $-2\times10^{-12}$ | **yes** | $0.394$ |

"Aliased" is a loop closure in which the place seen from pose $i$ was wrongly recognized not as
$j$ but as **the neighbouring $j+1$** — an imitation of the perceptual aliasing of
`s1-loop-closure-lifelong`.

**How to read it.** (a) An aliased loop closure contradicts the other measurements **only
slightly**, so it does not break the structure (the tightness) of the problem. The solution is
certified as globally optimal, and that solution is **wrong** (ATE 3.7 to 9.4 times larger).
(b) A gross outlier breaks certification. But what failed to be certified is the best solution
the author's search (8 initializations) found, so whether that is because it is a local minimum
or because the relaxation is not tight **cannot be told from the certificate alone** —
certification is a sufficient condition, not a necessary one. (c) The residual $f$ is
informative: with 2 aliased closures $f$ goes $61.4 \to 454.1$, a factor of 7. Comparing with the
$f$ expected from the number of measurements and the noise level (a chi-square) detects "optimal,
but the model is wrong" (problem P4). **The certificate (optimality) and the goodness-of-fit
test (validity of the model) answer different questions.**

**Where the assumptions break**: the conclusion of this experiment is "plausible false
measurements pass certification", not "certification is useless". The certificate separates
**failure of the solver** (a local minimum) from **failure of the data** (a wrong loop closure)
— when a certified solution is bad there is no need to suspect the solver; suspect the data.
Without that separation the two are mixed in the same symptom (a large error). Defence against
outliers has to be provided separately, by a robust cost and a certifiable relaxation of it
(`c5-robust-global-estimation`).

## Proof sketch

### R2 — the certificate matrix implies global optimality [D3]

**Hypotheses**
H1: $\hat{R} = [\hat{R}_1\ \cdots\ \hat{R}_n]$ is feasible — $\hat{R}_i^\top\hat{R}_i = I_d$.
H2: $\Lambda$ is defined by (3) — block diagonal with $d\times d$ blocks, each
$\Lambda_i = \operatorname{sym}\big((Q\hat{R}^\top)_i\hat{R}_i\big)$ symmetric.
H3: $S = Q - \Lambda \succeq 0$.

**Conclusion** C: for every feasible $R$ ($R_i^\top R_i = I_d$, that is $R \in O(d)^n$),
$\operatorname{tr}(QR^\top R) \ge \operatorname{tr}(Q\hat{R}^\top\hat{R})$. In particular
$\hat{R}$ is a global minimizer over $SO(d)^n$.

**Strategy**: split the objective into an $S$ part and a $\Lambda$ part. The $\Lambda$ part is
**constant** on the feasible set and the $S$ part is non-negative. It is a direct computation of
weak duality.

1. **The $\Lambda$ part is constant.** For any feasible $R$, since $\Lambda$ is block diagonal
   (H2),
   $\operatorname{tr}(\Lambda R^\top R) = \sum_i\operatorname{tr}(\Lambda_iR_i^\top R_i) = \sum_i\operatorname{tr}\Lambda_i = \operatorname{tr}\Lambda$.
2. **The objective at $\hat{R}$ is $\operatorname{tr}\Lambda$.**
   $\operatorname{tr}(Q\hat{R}^\top\hat{R}) = \sum_i\operatorname{tr}\big((Q\hat{R}^\top)_i\hat{R}_i\big)$,
   and the trace of a matrix equals the trace of its symmetric part, so this is
   $\sum_i\operatorname{tr}\Lambda_i$.
3. **The $S$ part is non-negative.** By H3,
   $\operatorname{tr}(SR^\top R) = \operatorname{tr}(RSR^\top) = \sum_{k=1}^{d}r_kSr_k^\top \ge 0$
   ($r_k$ the $k$-th row of $R$).
4. **Combine.**
   $\operatorname{tr}(QR^\top R) = \operatorname{tr}(SR^\top R) + \operatorname{tr}(\Lambda R^\top R) \ge 0 + \operatorname{tr}\Lambda = \operatorname{tr}(Q\hat{R}^\top\hat{R})$.
   **C**.
5. **Corollary: stationarity.** Applying step 4 to $R = \hat{R}$ gives
   $\operatorname{tr}(\hat{R}S\hat{R}^\top) = 0$, and since $S\succeq0$, $S\hat{R}^\top = 0$. That
   is, when certification holds the first-order stationarity condition is **a consequence, not
   an assumption**. Conversely an $\hat{R}$ that is not a stationary point cannot be certified.

**Where it collapses if a hypothesis is removed**

- **Remove H3**: step 3 fails. All that remains is the lower bound (4). Note: $S\not\succeq0$ is
  **not** a proof that "$\hat{R}$ is not globally optimal". If the relaxation is not tight,
  $S\not\succeq0$ at the global minimum too. A failed certification is **undecided**.
- **Remove "block diagonal" from H2**: step 1 fails — if $\Lambda$ had off-diagonal blocks,
  $\operatorname{tr}(\Lambda R^\top R)$ would depend on $R$ and not be constant. The block
  diagonal structure comes from the constraints $R_i^\top R_i = I$ being **per block**. With
  different constraints (for example some poses fixed) the structure of the multiplier changes.
- **Remove "symmetric" from H2**: a non-symmetric multiplier cannot be the dual variable of the
  constraint $R_i^\top R_i = I$ (an equality of symmetric matrices). Using
  $\Lambda_i = (Q\hat{R}^\top)_i\hat{R}_i$ without symmetrizing makes $S$ non-symmetric, for which
  "positive semidefinite" is not defined. At a stationary point that block is already symmetric
  and it makes no difference, but for **a solution that has not fully converged** it does, and
  then the symmetrization is needed.
- **Remove H1** (numerically $\hat{R}_i$ is not exactly orthogonal): the equalities of steps 1
  and 2 carry an error, and the threshold test on $\lambda_{\min}(S)$ is buried in it. Project
  each block onto the nearest rotation before certifying.

## Problem set

The answer policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Derive (2) from (5) with no line missing, and (a) prove that $\Pi$ is
a projection, (b) show that for noise-free measurements $QR^{\natural\top} = 0$, (c) explain
through the gauge why the null space of $Q$ has dimension at least $d$ without noise.
*Answer sketch*: (a) with $M = \Omega^{1/2}A^\top$, $\Pi = I - M(M^\top M)^\dagger M^\top$.
(b) The rotation term is, block by block,
$\kappa(R_i^\natural - R_j^\natural\tilde{R}_{ij}^\top)^\top = 0$; for the translation term,
$R^\natural V$ equals $t^\natural A$ at the true translations and so lies in the null space of
$\Pi$. (c) A global rotation $R \mapsto GR$ leaves the objective unchanged, so all $d$ rows of
$R^\natural$ are null vectors.

**P2 (proof, ★★, R2)** Write the five steps of the proof sketch with no line missing and show
that if $S\succeq0$ and $\operatorname{rank}S = dn - d$, the global minimizer is **unique up to a
global rotation**.
*Strategy + key inequality*: an optimal $R$ must attain equality in step 4, so $RSR^\top = 0$,
that is the rows of $R$ lie in the null space of $S$ ($d$-dimensional, the row space of
$\hat{R}$). Hence $R = G\hat{R}$, and feasibility gives $G \in O(d)$. The expansion is withheld.

**P3 (proof, ★★★, R3)** Derive the Lagrangian dual of (7). Show that the dual variable is a block
diagonal symmetric $\Lambda$ and that the dual problem is
$\max\{\operatorname{tr}\Lambda : Q - \Lambda\succeq0\}$, and show that the $\Lambda$ of (3) is
**dual optimal if dual feasible**, restating R2 and R3 in the language of duality.
*Strategy + key inequality*: minimizing the Lagrangian
$\operatorname{tr}(QZ) - \sum_i\operatorname{tr}(\Lambda_i(Z_{ii} - I))$ over $Z\succeq0$ is
finite only when $Q - \Lambda\succeq0$, with value $\operatorname{tr}\Lambda$. Strong duality
comes from Slater's condition ($Z = I$ is strictly feasible).

**P4 (derivation, ★★, R5)** Approximate the expectation of the optimal objective $f^\star$, when
the noise is as assumed and there are no outliers, in terms of the number of measurements $m$,
the number of poses $n$ and the dimension $d$ (count degrees of freedom). Apply it to the graph
of R5 in this lesson ($n = 40$, $m = 59$) and judge $f = 61.4$ and $f = 454.1$.
*Answer sketch*: with weights $\kappa = 1/(2\sigma_R^2)$, $\tau = 1/\sigma_t^2$, (1) is roughly a
sum of chi-squares. For $d = 2$ each edge has 1 rotational + 2 translational = 3 residual degrees
of freedom, there are 3 unknowns per pose and 3 gauge, so
$\mathbb{E}[f^\star] \approx 3m - (3n - 3) = 177 - 117 = 60$ with standard deviation
$\approx\sqrt{2\times60} = 11$. $61.4$ is the expectation itself and $454.1$ is 36 standard
deviations out — **the model is wrong**. (Confirm that in the small-angle approximation
$\kappa\lVert\cdot\rVert_F^2 \approx \theta^2/\sigma_R^2$.)

**P5 (numerical, ★, R3)** On a problem with 30 poses and $d = 2$ a local search returned a
solution with $f = 1522.2$, $\lambda_{\min}(S) = -26.31$. (a) Find the lower bound (4) and the
bound on the suboptimality gap, (b) given that another initialization returned a solution with
$f = 1.712$, $\lambda_{\min}(S) = -6\times10^{-15}$, state what can be said about each of the
two.
*Answer*: (a) $nd = 60$. Lower bound $1522.2 - 60\times26.31 = -56.4$, bound on the gap
$1578.6$. (Tolerance $\pm0.2$.) (b) The second solution is **certified** globally optimal. The
first is then **established** to be a local minimum with gap $1522.2 - 1.712 = 1520.5$ — the
certificate of the second tells what the certificate of the first alone could not.
*Check*: confirm that the lower bound is at most the certified optimum $1.712$ (otherwise the
computation of $S$ is wrong).

**P6 (implementation, ★★★, R4)** Solve (7) by a rank-3 factorization and implement one step of
the staircase: starting from a local minimum over $SO(2)^n$, climb to $r = 3$ along the minimum
eigenvector of $S$, descend, and round back to $SO(2)^n$.
*Rubric*: (a) implement the Riemannian gradient on the Stiefel manifold (tangent-space
projection) and a retraction (polar decomposition or QR) (b) show that, starting from local
minimum A of the ring graph in this lesson, the global minimum $f = 1.712$ is reached (c) show
that the certificate holds at the solution reached (d) at $\sigma_R = 0.6$ of the table in the
text, show that the third singular value of the rank-3 solution is **not** 0 (not tight) and
report the gap to the rounded solution.

**P7 (counterexample, ★★, R2, R5)** (a) Give numerically a counterexample to "if certification
fails the solution is not globally optimal" — it suffices to find, in the high-noise setting of
the table in the text, a case in which several initializations gather at **the same** best
solution that is nevertheless not certified (for a rigorous counterexample the solution has to
be shown globally optimal by another method — state how far you showed it). (b) Construct a
counterexample to "a certified solution is an accurate map" in a way **different** from the
lesson.
*Property checklist*: (a) must state precisely that certification is a **sufficient condition**.
For small $n$ ($\le 6$) an exhaustive grid search over the angles establishing global optimality
makes it rigorous. (b) for example gives every translation measurement the same scale error (a
calibration error) or uses a consistently biased odometry — if the measurements are wrong
**consistently with one another**, certification passes.

**P8 (paper, ★★, R1, R2, R4)** Read sections 3–5 of `rosen2019-se-sync` and
`carlone2015-lagrangian-duality` and (a) check whether the data matrix of SE-Sync has the same
structure as (2) in this lesson (connection Laplacian + translation term), (b) find the
optimality-certification theorem of the paper and compare it with (3), (c) write whether the
exact-recovery (tightness) proposition gives **a quantitative threshold** on the noise or only
asserts existence, (d) set out the difference in computational cost between the way Carlone et
al. solve the dual (the SDP directly) and the way of SE-Sync (factorization + staircase).
*Rubric*: (a) and (b) pass by citing equation or theorem numbers (if it differs from this
lesson, treat it as an error of this lesson and write down the difference). (c) is the core —
stating the gist "the existence of a threshold is proved, but its value depends on the problem
and is hard to compute" passes. Adding that this is why **a posteriori certification** is needed
is excellent. (d) passes by naming the number of variables ($dn\times dn$ against $r\times dn$).

## Paper reading

**Two must-read papers.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read in three passes, and in the third pass concentrate on questions 1,
4 and 8.

1. **Rosen, Carlone, Bandeira & Leonard, "SE-Sync: a certifiably correct algorithm for
   synchronization over the special Euclidean group" (2019, IJRR)** — role: `standard`.
   <https://arxiv.org/abs/1612.07386> (§3-5: problem formulation, relaxation, algorithm)
   The primary source for R1–R4 of this lesson. It is long but clearly structured: simplify the
   problem (eliminate the translations), relax it, solve the relaxation by factorization, and
   certify.
   Additional questions: (a) what can be lost at each of the authors' two steps, relaxing
   $SO(d)$ to $O(d)$ and then going to the SDP? (b) in which norm is the hypothesis of the
   exact-recovery proposition (the size of the noise) measured? (c) are there cases in the
   experiments in which certification failed, and if so under what conditions?
2. **Carlone, Rosen, Calafiore, Leonard & Dellaert, "Lagrangian duality in 3D SLAM: verification
   techniques and optimal solutions" (2015, IROS)** — role: `seminal`.
   <https://arxiv.org/abs/1506.00746> (the sections on the dual problem and the verification
   techniques)
   The paper that set up the idea of applying Lagrangian duality to pose-graph optimization to
   **verify a given solution**. The source of R2 of this lesson.
   Additional questions: (a) is the authors' "verification" the same condition as the
   certificate of this lesson? (b) on which data do the authors report the fraction of cases
   with zero duality gap? (c) what do the authors say can and cannot be done when verification
   fails?

**Two recommended papers.** `boumal2016-burer-monteiro` (conditions under which a second-order
critical point of the factored non-convex problem is a solution of the SDP — the theory of the
staircase of R4, <https://arxiv.org/abs/1606.04970>) and `bandeira2017-tightness` (a proof of
the noise range in which the relaxation is tight for angular synchronization — it fills in the
[D0] of R3 for one case, <https://arxiv.org/abs/1411.3272>).

**The ten fixed questions**: (1) what problem is solved under what assumptions (2) what exactly
could earlier work not do (3) the key idea in one line of mathematics (4) what is the theoretical
guarantee and **what is not guaranteed** (5) the independent and dependent variables and baselines
of the experiments, and were they tuned fairly (6) do the metrics match the claims, and are
variance and seeds reported (7) what information needed for reproduction is missing (8) if it is
wrong, which assumption to suspect first (9) computational and memory complexity and real-time
capability (10) what would you change to surpass it a year from now.

## Reproduction task

**Tier R3 (reduced reproduction of a paper's result).** Compute budget: one laptop CPU core,
under 10 minutes for all of Parts A–F (the optional item of Part E takes another 10 minutes), at
most 1 GB of memory. numpy + scipy only.

**Input data.** Parts A–F use the $SE(2)$ pose graphs of the generator below (deterministic).
Part G uses **a public pose graph** (g2o format). **What the learner writes is the assembly of
the data matrix $Q$, the local optimization, the certificate and the lower bound.**

```python
"""Reproduction task of s1-certifiable-slam: SE(2) pose-graph generators."""

import numpy as np

SEED = 20261117


def rot2(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s], [s, c]])


def measure(rng, th, t, edges, sig_r, sig_t):
    """Per edge (i, j, relative angle, relative translation). Random order: 1 angle, 2 translation."""
    return [
        (
            i,
            j,
            th[j] - th[i] + rng.normal(0, sig_r),
            rot2(th[i]).T @ (t[j] - t[i]) + rng.normal(0, sig_t, 2),
        )
        for (i, j) in edges
    ]


def chain_graph(rng, n, n_loops, sig_r, sig_t):
    """An odometry chain of n-1 edges + n_loops random loop closures."""
    th = np.cumsum(rng.normal(0, 0.4, n))
    th[0] = 0.0
    t = np.zeros((n, 2))
    for i in range(1, n):
        t[i] = t[i - 1] + rot2(th[i - 1]) @ np.array([1.0, 0.0])
    edges = [(i, i + 1) for i in range(n - 1)]
    while len(edges) < n - 1 + n_loops:
        i, j = sorted(int(v) for v in rng.choice(n, 2, replace=False))
        if j - i > 1 and (i, j) not in edges:
            edges.append((i, j))
    return th, t, edges, measure(rng, th, t, edges, sig_r, sig_t)


def ring_graph(rng, n, sig_r, sig_t):
    """n poses on a circle. n-1 odometry edges + 1 loop closure (0, n-1)."""
    a = 2 * np.pi * np.arange(n) / n
    t = n / (2 * np.pi) * np.stack([np.cos(a), np.sin(a)], 1)
    th = a + np.pi / 2
    edges = [(i, i + 1) for i in range(n - 1)] + [(0, n - 1)]
    return th, t, edges, measure(rng, th, t, edges, sig_r, sig_t)


def alias_loops(rng, th, t, edges, meas, n_out, shift, sig_r, sig_t):
    """Replace n_out loop closures by measurements 'aliased to the neighbour j + shift' (in place)."""
    n = len(th)
    cand = [k for k in range(n - 1, len(edges)) if edges[k][1] + shift < n]
    for k in rng.choice(cand, n_out, replace=False):
        i, j = edges[k]
        j2 = j + shift
        meas[k] = (
            i,
            j,
            th[j2] - th[i] + rng.normal(0, sig_r),
            rot2(th[i]).T @ (t[j2] - t[i]) + rng.normal(0, sig_t, 2),
        )
```

**Conventions (must be followed).** (a) The weights are $\kappa = 1/(2\sigma_R^2)$,
$\tau = 1/\sigma_t^2$ (common to all edges). (b) Create `np.random.default_rng(SEED)` afresh for
every setting, and draw the initializations `rng.uniform(-np.pi, np.pi, n)` one after another
from the same generator **after** building the graph. (c) The local optimization is an
unconstrained optimization over the angles $\theta_i$ (L-BFGS or similar) with the analytic
gradient $\partial f/\partial\theta_i = \langle(2RQ)_i,\ R_iJ\rangle$,
$J = \begin{pmatrix}0&-1\\1&0\end{pmatrix}$. (d) The certification threshold is
$\lambda_{\min}(S) > -10^{-6}\max(1, \lvert f\rvert)$. (e) The ATE is the position RMSE after the
$SE(2)$ alignment of `s1-slam-benchmarking` (Umeyama, no scale), with positions recovered
through (6).

**Part A — the data matrix.** Assemble $Q$ for `chain_graph(rng, 60, 40, 0.1, 0.1)` and confirm
that at the truth $\theta^\natural$ the value $\operatorname{tr}(QR^\top R)$ agrees with (1)
computed directly (with the $t^\star$ of (6) inserted). Compare the analytic gradient with
central differences.

**Part B — certification.** Solve the graph of Part A starting from the truth and report $f$,
$\lambda_{\min}(S)$ and $\max\lvert S\hat{R}^\top\rvert$. Then solve from 200 random
initializations and report the number certified and the range of $f$ over the certified
solutions.

**Part C — local minima and the lower bound.** On `ring_graph(rng, 30, 0.03, 0.03)` obtain the
solution from the truth and the solutions from 300 random initializations, and report (a) the
number certified, (b) the distinct values of $f$ with their counts, $\lambda_{\min}(S)$, lower
bound (4) and ATE, (c) whether the lower bound is valid in all 300.

**Part D — tightness and noise.** For $\sigma_R \in \{0.1, 0.3, 0.6, 0.9\}$ ($\sigma_t = 0.1$)
generate 10 graphs `chain_graph(rng, 40, 20, σ_R, 0.1)` each (in sequence from one generator),
apply the certificate to the best of 6 initializations per graph (the truth + 5 random) and
count the certified ones.

**Part E — what the certificate does not say.** Apply `alias_loops` to
`chain_graph(rng, 40, 20, 0.05, 0.05)` with
$(n_{\mathrm{out}}, \text{shift}) \in \{(0,0), (2,1), (4,1), (4,2), (8,1)\}$ (creating the
generator afresh each time) and report the $f$, the certification status and the ATE of the best
of 8 initializations. **Optional**: on the graphs of Part D obtain the relaxation value by a
rank-3 factorization and measure the relative gap (problem P6).

**Part F — goodness of fit.** For the five cases of Part E compare $f$ with the expectation
$3m - 3n + 3 = 60$ and standard deviation $11$ of problem P4 and classify each as "certified,
model valid", "certified, model rejected" or "not certified".

**Part G — a public pose graph.** Read one public 2D pose graph (the dataset in the resource
list — start small: hundreds to thousands of poses) and (a) solve it from the odometry
initialization and from the chordal initialization (rotations first, by linear least squares),
(b) report the $f$ and $\lambda_{\min}(S)$ of the two solutions (sparse eigenvalue solver:
`scipy.sparse.linalg.eigsh`), (c) if certified report that the solution is globally optimal, and
if not report the lower bound (4) and the bound on the gap. **Note: the author could not
download and run the public datasets and the SE-Sync reference implementation in the environment
in which this lesson was written.** The reference values of Parts A–F are those of the author's
implementation and Part G has no reference values. The verdict is the **internal consistency**
of condition 7 below (the $f$ of the certified solutions agree between the two initializations
and, if the reference implementation is available, with its optimum to a relative error of
$10^{-6}$). If the information matrices of the dataset are anisotropic, build scalar weights in
the manner of the SE-Sync paper so that the problem has the form (1) — and record that
conversion in the report.

**Acceptance criteria — all seven conditions must hold to pass.**

1. **Part A** — the difference between the two objective values is below $10^{-8}$ (the
   author's implementation: $7\times10^{-10}$; $f = 168.601949$ at the truth). The difference
   between the analytic gradient and central differences is below $10^{-4}$.
2. **Part B** — the solution from the truth has $f^\star = 118.509722 \pm 10^{-5}$ and
   $\lvert\lambda_{\min}(S)\rvert < 10^{-8}$ and **is certified**. **All** 200 random
   initializations are certified and their $f$ agree with $f^\star$ to within $10^{-5}$.
3. **Part C** — (a) the global solution $f = 1.7120 \pm 10^{-3}$ is certified, and the number
   certified among the 300 random ones is $103 \pm 25$ (it depends on the local optimizer).
   (b) **The $f$ of the certified solutions are all equal** (to within $10^{-3}$). (c) Among the
   uncertified solutions there is one with $f = 1522.2 \pm 0.5$, whose
   $\lambda_{\min}(S) = -26.3 \pm 0.2$ and lower bound is $-56 \pm 12$. (d) The lower bound (4)
   is at most $f^\star$ in **all** 300.
4. **Part D** — certification succeeds in $10/10$ at $\sigma_R = 0.1$, in at least $8/10$ at
   $0.3$, and in at most $1/10$ at $0.6$ and $0.9$.
5. **Part E** — at $(0,0)$, $f = 61.39$ and ATE $0.064$, certified. The four aliased cases are
   **all certified** with ATE $0.235, 0.264, 0.604, 0.394$ ($\pm0.01$; when the conventions are
   followed). Print explicitly that the ATE of the certified solutions is at least 3 times the
   baseline.
6. **Part F** — $(0,0)$ is classified "certified, model valid" ($f = 61.4$ within
   $60 \pm 2\times11$) and **all** four aliased cases "certified, model rejected"
   ($f = 454, 716, 2506, 1226$).
7. **Part G** — report the name of the dataset used, its numbers of poses and edges, and how the
   weights were built. For the solutions from the two initializations there is a table of $f$,
   $\lambda_{\min}(S)$ and certification status. If both are certified, the two $f$ agree to a
   relative error of $10^{-6}$. An uncertified solution comes with the lower bound and the bound
   on the gap.

**Comparison**: (a) the baseline of Part A is the directly computed objective. (b) The baseline
of Parts B and C is the certified solution from the truth. (c) The baseline of Parts E and F is
the case without outliers. (d) The baselines of Part G are the SE-Sync reference implementation
(if available) and the two different initializations.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The two objective values of Part A differ | The pseudo-inverse of the Laplacian is wrong | `np.linalg.pinv` can cut off the zero eigenvalue wrongly (in the author's environment it judged the rank to be 13 instead of 59). Decompose with `eigh`, drop the single smallest eigenvalue and build the inverse. Check $\Pi^2 = \Pi$ directly |
| Only the rotation term is off | The transposes of the off-diagonal blocks of the connection Laplacian are swapped | Check that block $(i,j)$ is $-\kappa\tilde{R}_{ij}$ and $(j,i)$ its transpose. Compare with a hand computation on 5 poses |
| $\lambda_{\min}(S)$ at the global solution is at the level of $-10^{-3}$ | The optimization has not converged far enough | Look at $\max\lvert S\hat{R}^\top\rvert$. If it exceeds $10^{-4}$, tighten the tolerance |
| Certification always fails | $\Lambda$ was not symmetrized, or the blocks were multiplied in the order $\hat{R}_i(Q\hat{R}^\top)_i$ | $\Lambda_i = \operatorname{sym}(\hat{R}_i^\top(\hat{R}Q)_i)$. Check that $S\hat{R}^\top = 0$ at a stationary point |
| The lower bound exceeds $f^\star$ | $n$ was used instead of $nd$ | $\lVert R\rVert_F^2 = nd$ ($2n$ for $d = 2$) |
| No local minimum appears in Part C | The initializations are near the truth | Check that the initial angles are drawn uniformly from $[-\pi, \pi]$ |
| The values of Part E differ from the reference | Other random numbers were drawn from the generator before `alias_loops` | Keep the order: build the graph → `alias_loops` → initializations |
| In Part G $Q$ does not fit in memory | $Q$ was formed as a dense matrix | Do not assemble $Q$. Compute $Qx$ by sparse products and a Laplacian linear solve, and hand it to `eigsh` as a linear operator |

## Open problems

- **(Open problem) Certification of problems with outliers** — as R5 showed, the standard
  certificate speaks only of the optimality of the problem without outliers. The relaxation of a
  problem with a robust cost (truncated least squares and the like) has far more variables
  (products with the outlier-selection variables) and its tightness breaks as the outlier
  fraction rises. Current approaches: moment relaxations of polynomial optimization and
  exploitation of their sparse structure, a posteriori certification after solving with GNC.
  What is missing: robust certification that is **close to real time** at the scale of thousands
  of poses — at present it is practical only for tens to hundreds of variables.
- **(Open problem) Predicting the tightness threshold in advance** — the existence of a noise
  threshold below which the relaxation is tight is proved (`rosen2019-se-sync`; for angular
  synchronization `bandeira2017-tightness`), but the computable conditions that answer "will
  this problem be tight" **before solving**, for a given graph and noise level, are loose.
  Current approach: sufficient conditions in terms of the algebraic connectivity of the graph and
  the size of the noise. What is missing: conditions that are tight on actual SLAM graphs (long
  chains + sparse loops) — how the threshold shrinks when connectivity is low, as on the ring
  graph of this lesson, is not known quantitatively.
- **(Open problem) Anisotropic noise and general factors** — the elimination of R1 leans on
  isotropic noise and relative-pose measurements. Real factor graphs mix anisotropic
  covariances, landmarks, IMU preintegration and priors. Current approaches: extensions to
  landmarks and range measurements, larger relaxations that include anisotropic noise. What is
  missing: certification for general factor graphs that **scales** at the level of SE-Sync —
  certifying the global optimality of visual-inertial bundle adjustment is still possible only
  at small scale.
- **(Open problem) Online, incremental certification** — in SLAM poses keep being added, but the
  certificate requires recomputing the minimum eigenvalue of the whole $S$. Current approaches:
  incremental eigenvalue solvers warm-started from the previous eigenvector, local updates. What
  is missing: a way to decide whether a new measurement **changes** the certification status
  without a full recomputation, and a way to re-solve only the affected subgraph when
  certification fails.

## Concept check

Take it with `rc quiz s1-certifiable-slam`. This quiz is a **concept check only**; the real work
is the problem set and the reproduction task above (`lesson-standard.md` §4).

## How to study this stage

1. **Read the plan table first (10 min)** — the five-stage table of "Setup and notation".
   Formulation → certification → relaxation → landscape → limits is the whole of this lesson.
2. **From (5) to (2) by hand (60 min)** — eliminating the translations. Work an example with 3
   poses and 3 edges through on paper until $Q$ is a matrix of numbers. The one line that checks
   that $\Pi$ is a projection is the easiest to get wrong.
3. **Validate $Q$ with Part A (60 min)** — until the two objective values agree to $10^{-9}$.
   Read the first row of the diagnosis table (the pseudo-inverse) beforehand — it is a trap the
   author actually fell into.
4. **The five steps of R2 from a blank page (40 min)** — it is a four-line proof. You must be
   able to explain in words the structure "the $\Lambda$ part is constant, the $S$ part is
   non-negative". Remove the four hypotheses one at a time.
5. **Use the certificate with Parts B and C (70 min)** — after seeing 200/200 certified on the
   graph with many loops, see 2/3 fail on the ring graph. **Plot** the trajectory of local
   minimum A — you will see the twisted ring. The difference between having converged and being
   right is in that one picture.
6. **Derive (8) and the lower bound, then Part D (50 min)** — confirm from (8) that certification
   and tightness are the same statement, and find the point where it collapses as the noise
   grows. Compute with the figures of your own sensors where the noise of actual SLAM lies
   relative to that threshold.
7. **See the limits with Parts E and F (50 min)** — **the most important experiment** of this
   lesson. See aliased loop closures pass certification and see the goodness of fit of the
   residual catch them. Write "the certificate and the goodness of fit answer different
   questions" in your own words.
8. **The two papers (150 min)** — Carlone et al. first (where the idea starts: verify a given
   solution), then SE-Sync (which turns the verification into an algorithm). Read sections 3–5
   of SE-Sync matching them line by line with R1–R4 of this lesson. The one-page note per paper
   is **mandatory**.
9. **Part G: public data (90 min)** — drop the dense matrices and rewrite with sparse
   operations. The goal is to see the solutions from the two initializations certified at the
   same value. If they are not certified, report the lower bound and conjecture why (outliers in
   the data, or failure of the solver? — use the tool of Part F).

**Pass criterion**: from a blank page you can derive the elimination (5)–(6), the five steps of
R2, (8) and (4); you can say what success and failure of certification each mean (failure is
undecided); you can explain with an example why a certified solution can be a wrong map; you
have code that satisfies all seven conditions of the reproduction task (including the public
data); and you have notes on the two papers.
