---
id: c3-lyapunov-stability
lang: en
title: Lyapunov stability and ISS
summary: >-
  The Lyapunov stability theorem and its converse, LaSalle's invariance principle, and
  input-to-state stability (ISS) formulated with comparison functions and derived line by line.
  It ends by searching for the Lyapunov function itself with sum-of-squares (SOS) programming to
  certify a region of attraction, and by showing why such a certificate is always conservative.
objectives:
  - Separate the hypotheses of the Lyapunov theorem and LaSalle's invariance principle and reconstruct their proof strategies.
  - Construct the converse theorem for exponential stability by integrating along trajectories, and say where each bound comes from.
  - Derive the $\beta$ and $\gamma$ of the ISS estimate from an ISS-Lyapunov function with no missing steps.
  - Build a system that is 0-GAS but not ISS and explain which hypothesis fails.
  - Certify a region of attraction with SOS and check that the certificate is contained in the region found by numerical integration.
tags: [nonlinear-control, lyapunov, iss, sum-of-squares, region-of-attraction, research]
---

# Lyapunov stability and ISS

## Setup and notation

This is the first lesson of module C3, and the five lessons that follow (feedback linearisation,
contraction, passivity, adaptive control, CBFs) all use the decision tools built here. The
following is assumed (recommended prerequisites: module M3 of the `robotics-expert` course,
and `r0-convex-optimization` and `r0-estimation-theory` of the research track's R0 bridge).

- Analysis: local Lipschitz conditions and existence/uniqueness for ODEs, Gronwall's inequality, compactness.
- Linear algebra: definiteness of symmetric matrices, the Lyapunov equation $A^\top P + PA = -Q$.
- Convex optimisation: SDPs and their duals, and the fact that "$M \succeq 0$" can be a
  constraint (`r0-convex-optimization`). That is all the SOS section needs.
- Differential geometry is not required; Riemannian metrics first appear in
  `c3-contraction-incremental`.

Notation (fixed for the whole module):

| Symbol | Meaning |
|---|---|
| $\dot{x} = f(x)$ | $f : D \to \mathbb{R}^n$ with $D \subseteq \mathbb{R}^n$ open, $f(0) = 0$, $f$ locally Lipschitz |
| $\dot{x} = f(x, u)$ | the system with input; $u(\cdot)$ essentially bounded measurable, $\lVert u \rVert_\infty = \operatorname{ess\,sup}_{t \ge 0} \lvert u(t) \rvert$ |
| $\phi(t; x_0)$ | the solution (flow) from $x_0$; with an input, $\phi(t; x_0, u)$ |
| $V(x)$ | Lyapunov function candidate; $\dot{V}(x) = \nabla V(x)^\top f(x)$ (the derivative along $f$) |
| $\alpha \in \mathcal{K}$ | comparison function: $\alpha(0)=0$, continuous, strictly increasing |
| $\alpha \in \mathcal{K}_\infty$ | additionally $\alpha(r) \to \infty$ as $r \to \infty$ |
| $\beta \in \mathcal{KL}$ | $\beta(r,t)$ is class $\mathcal{K}$ in $r$, decreasing in $t$, and $\beta(r,t)\to 0$ as $t\to\infty$ |
| $\mathcal{R}_A$ | region of attraction $= \{x_0 : \phi(t;x_0) \to 0\}$ |
| $\Omega_c$ | sublevel set $\{x : V(x) \le c\}$ |

Stability is defined with $\varepsilon$–$\delta$: the origin is **stable** if for every
$\varepsilon>0$ there is a $\delta>0$ such that $\lvert x_0 \rvert < \delta \Rightarrow
\lvert \phi(t;x_0)\rvert < \varepsilon$ for all $t \ge 0$. Adding $\phi(t;x_0) \to 0$ gives
**asymptotic** stability, and a convergence of the form $\lvert \phi \rvert \le
k\lvert x_0\rvert e^{-\lambda t}$ gives **exponential** stability. With comparison functions,
"asymptotically stable $\iff$ there is a $\beta \in \mathcal{KL}$ with
$\lvert \phi(t;x_0)\rvert \le \beta(\lvert x_0\rvert, t)$" fits on one line, and that form is the
bridge to ISS.

## Self-diagnosis before starting

If you can do all four, you may skip the recommended prerequisite lessons. **If two or more
block you**, going back to the lesson in brackets is faster. Answers and tolerances are given
immediately.

1. Find the eigenvalues of $A = \begin{bmatrix} 0 & -1 \\ 1 & -1\end{bmatrix}$. Is the origin
   stable? (recommended: linear algebra — `robotics-expert` M1)
   **Answer**: $\lambda = -\tfrac12 \pm \tfrac{\sqrt3}{2} i$; the real parts are negative, so the
   origin is exponentially stable. Tolerance $10^{-6}$.
2. For the same $A$, find the symmetric $P$ with $A^\top P + PA = -I$.
   (recommended: `r0-linear-algebra-decompositions`)
   **Answer**: $P = \begin{bmatrix} 1.5 & -0.5 \\ -0.5 & 1\end{bmatrix}$, tolerance $10^{-9}$.
   Check: $\operatorname{eig}(P) \approx \{0.690983,\ 1.809017\}$, $\det P = 1.25$.
3. Is the origin of $\dot{x} = -x^3$ asymptotically stable? Exponentially stable? One sentence
   with the reason. (recommended: `robotics-expert` M3)
   **Answer**: asymptotically stable but not exponentially. The solution is
   $x(t) = x_0/\sqrt{1 + 2x_0^2 t}$, which decays only like $O(t^{-1/2})$, and the linearisation
   $\dot{x} \approx 0$ says nothing.
4. What kind of optimisation problem is
   $\min_P \{ \operatorname{tr} P : P \succeq I,\ A^\top P + PA \preceq -I \}$?
   (recommended: `r0-convex-optimization`)
   **Answer**: an SDP — linear objective, linear matrix inequality (LMI) constraints. The SOS
   section of this lesson only adds polynomial constraints to that same frame.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (Lyapunov stability theorem) [D3]** — if $V \in C^1(D)$ with $V(0)=0$, $V(x)>0$ on
  $D\setminus\{0\}$ and $\dot{V}(x) \le 0$, the origin is stable. If $\dot{V}$ is negative on
  $D\setminus\{0\}$ it is asymptotically stable. If $D = \mathbb{R}^n$ and $V$ is **radially
  unbounded** ($\lvert x\rvert \to \infty \Rightarrow V(x) \to \infty$), it is globally
  asymptotically stable (GAS).
- **R2 (converse theorem for exponential stability) [D3]** — if the origin is exponentially
  stable on $D_0$ and $f$ is $C^1$, then
  $$
  V(x) = \int_0^T \phi(\tau; x)^\top \phi(\tau; x)\, d\tau \tag{1}
  $$
  satisfies, for a suitable $T$, $c_1\lvert x\rvert^2 \le V(x) \le c_2 \lvert x \rvert^2$,
  $\dot{V}(x) \le -c_3\lvert x\rvert^2$ and $\lVert \partial V/\partial x\rVert \le c_4 \lvert x \rvert$.
  So **a Lyapunov function always exists** — the problem is not existence but construction.
- **R3 (LaSalle's invariance principle and Barbashin–Krasovskii) [D3]** — if $\Omega$ is compact
  and forward invariant and $V \in C^1$ satisfies $\dot{V} \le 0$ on $\Omega$, every solution
  starting in $\Omega$ converges to the **largest invariant set** $M$ contained in
  $E = \{x \in \Omega : \dot{V}(x) = 0\}$. Corollary (Barbashin–Krasovskii): if $V$ is positive
  definite, $\dot V \le 0$, and no solution other than the origin stays in $E$, the origin is
  asymptotically stable.
- **R4 (ISS and comparison functions) [D2]** — if there is a $V$ (an ISS-Lyapunov function) with
  $\alpha_1,\alpha_2,\alpha_3 \in \mathcal{K}_\infty$ and $\sigma \in \mathcal{K}$ such that
  $$
  \alpha_1(\lvert x\rvert) \le V(x) \le \alpha_2(\lvert x \rvert), \qquad
    \nabla V(x)^\top f(x,u) \le -\alpha_3(\lvert x \rvert) + \sigma(\lvert u \rvert) \tag{2}
  $$
  then the system is ISS:
  $$
  \lvert \phi(t;x_0,u)\rvert \le \beta(\lvert x_0\rvert, t) + \gamma(\lVert u\rVert_\infty),
    \qquad \gamma = \alpha_1^{-1}\!\circ\, 2\,\alpha_2 \circ \alpha_3^{-1} \circ 2\sigma. \tag{3}
  $$
  The converse also holds (Sontag & Wang 1995). **[D1]**
- **R5 (SOS certificates and the region of attraction) [D2]** — for polynomial $f$ and
  polynomial $V$, $\lambda$,
  $$
  V - \epsilon \lvert x\rvert^2 \in \Sigma, \qquad
    -\dot{V} - \lambda(x)\,(c - V(x)) - \epsilon \lvert x \rvert^2 \in \Sigma,
    \qquad \lambda \in \Sigma \tag{4}
  $$
  ($\Sigma$ the set of SOS polynomials) being feasible implies $\Omega_c = \{V \le c\}$, when
  bounded, is contained in $\mathcal{R}_A$. Condition (4) is **bilinear** in $V$ and $\lambda$,
  so it becomes an alternating optimisation in which one of them is fixed. The certificate is
  **only sufficient**.

## Derivation

### R4 — from an ISS-Lyapunov function to the ISS estimate

Assume (2) and build (3). Fix the input and write $\mu := \lVert u \rVert_\infty$. The idea is to
split the state space into the region where $\sigma(\mu)$ can be absorbed into **half** of
$\alpha_3$ (a gain margin) and its complement.

**Step 1 (where there is margin).** Take $\theta = \tfrac12$. Wherever
$\alpha_3(\lvert x \rvert) \ge 2\sigma(\mu)$, (2) gives

$$
\dot{V} \le -\alpha_3(\lvert x\rvert) + \sigma(\mu)
  \le -\alpha_3(\lvert x\rvert) + \tfrac12 \alpha_3(\lvert x\rvert)
  = -\tfrac12 \alpha_3(\lvert x \rvert). \tag{5}
$$

**Step 2 (a differential inequality in $V$ alone).** The right inequality of (2),
$V \le \alpha_2(\lvert x\rvert)$, gives $\lvert x \rvert \ge \alpha_2^{-1}(V)$, and $\alpha_3$ is
increasing, so (5) becomes

$$
\dot{V} \le -\tfrac12\,\alpha_3\!\left(\alpha_2^{-1}(V)\right) =: -\rho(V),
  \qquad \rho \in \mathcal{K}. \tag{6}
$$

The point is that $x$ has disappeared and only $V$ is left. Applying the comparison lemma
(Khalil Lemma 3.4) to $\dot{y} = -\rho(y)$, $y(0) = V(x_0)$ gives
$V(t) \le y(t) = \sigma_{\mathcal{KL}}(V(x_0), t)$ on that interval, with
$\sigma_{\mathcal{KL}} \in \mathcal{KL}$.

**Step 3 (a sublevel set you cannot leave).** Put

$$
c_\mu := \alpha_2\!\left(\alpha_3^{-1}(2\sigma(\mu))\right) \tag{7}
$$

and suppose $V(x) \ge c_\mu$. Then $\alpha_2(\lvert x\rvert) \ge V(x) \ge c_\mu$, hence
$\lvert x \rvert \ge \alpha_3^{-1}(2\sigma(\mu))$, i.e. $\alpha_3(\lvert x\rvert) \ge 2\sigma(\mu)$,
so (5) applies and $\dot{V} \le -\sigma(\mu) < 0$ for $\mu > 0$. Therefore $\Omega_{c_\mu}$ is
**forward invariant** and $V$ strictly decreases outside it. For all $t\ge0$,

$$
V(t) \le \max\{\, \sigma_{\mathcal{KL}}(V(x_0), t),\ c_\mu \,\} \le \sigma_{\mathcal{KL}}(V(x_0),t) + c_\mu. \tag{8}
$$

**Step 4 (back to the state).** Use $\lvert x \rvert \le \alpha_1^{-1}(V)$ and the weak triangle
inequality $\kappa(a+b) \le \kappa(2a) + \kappa(2b)$, valid for any $\kappa \in \mathcal{K}$
(because $a+b \le 2\max(a,b)$ and $\kappa$ is monotone), in (8):

$$
\lvert x(t)\rvert \le \alpha_1^{-1}\!\big(2\sigma_{\mathcal{KL}}(\alpha_2(\lvert x_0\rvert), t)\big)
  + \alpha_1^{-1}\!\big(2 c_\mu\big)
  =: \beta(\lvert x_0 \rvert, t) + \gamma(\mu), \tag{9}
$$

which is (3). Here $\beta \in \mathcal{KL}$ and $\gamma = \alpha_1^{-1}\circ 2\alpha_2 \circ
\alpha_3^{-1}\circ 2\sigma \in \mathcal{K}$; since $\gamma(\mu)\to0$ as $\mu \to 0$, (9) reduces
to the 0-GAS estimate when there is no input.

**Where the assumptions break**: if $\alpha_3$ in (2) is not class $\mathcal{K}_\infty$ but a
bounded class-$\mathcal{K}$ function, then $\alpha_3^{-1}(2\sigma(\mu))$ in step 3 is
**undefined** for large $\mu$, and all you get is local ISS, for small inputs. A concrete example:

$$
\dot{x} = -x + x^2 u \tag{10}
$$

is GAS for $u \equiv 0$ (0-GAS) but not ISS. For a constant input $u \equiv \mu > 0$, the
unstable equilibrium of $\dot{x} = -x + \mu x^2$ is at $x = 1/\mu$, and any $x_0 > 1/\mu$ escapes
in finite time (numerically: with $\mu = 0.1$ and $x_0 = 10.01$ the state passes $10^8$ within
$t \lesssim 20$, while $x_0 = 5$ converges to 0). Bounded inputs therefore do not give bounded
states, so (3) fails and the system is not ISS — but since the escape threshold $1/\mu$ grows as
$\mu$ shrinks, the system **is** locally ISS.

### R5 — finding a Lyapunov function with SOS and certifying a region of attraction

The skeleton is the **S-procedure**. "$\dot V < 0$ inside $\Omega_c$" is a set inclusion, and a
multiplier $\lambda(x) \ge 0$ turns it into a single polynomial inequality.

**Step 1.** The two goals are ⓐ $V$ positive definite and ⓑ
$x \in \Omega_c \setminus\{0\} \Rightarrow \dot{V}(x) < 0$. Written directly, ⓑ is a conditional
inequality and is not an SDP.

**Step 2 (absorb the condition into a multiplier).** Suppose $\lambda(x) \ge 0$ and

$$
-\dot{V}(x) \ge \lambda(x)\,(c - V(x)) + \epsilon\lvert x\rvert^2 \tag{11}
$$

holds for **all** $x$. If $x \in \Omega_c$ then $c - V(x) \ge 0$, so the right-hand side of (11)
is $\ge \epsilon\lvert x\rvert^2$ and hence $\dot{V}(x) \le -\epsilon \lvert x\rvert^2 < 0$ for
$x \ne 0$. The conditional inequality has become a single unconditional one.

**Step 3 (relax to SOS).** "A polynomial is nonnegative everywhere" is NP-hard in general, so
replace it by the stronger sufficient condition of being SOS:
$p \in \Sigma \iff p = \sum_i q_i^2 \iff p = z^\top Q z,\ Q \succeq 0$, with $z$ a vector of
monomials. That equivalence is what makes (4) an **SDP**, because $Q \succeq 0$ is an LMI.

**Step 4 (bilinearity and alternation).** (11) contains the product $\lambda(x) V(x)$, so it is
not jointly convex in $(V, \lambda)$. The practical remedy is to alternate: (i) fix $V$ and
search for $\lambda$ and $c$ (maximising $c$ is quasi-convex — handle it by bisection), and
(ii) fix $\lambda$ and search for $V$ (convex). Each step is an SDP, and the objective is usually
a proxy for the volume of $\Omega_c$ (a determinant, or the $\beta$ of a fixed shape set
$\{x^\top N x \le \beta\} \subseteq \Omega_c$). Topcu et al. 2008 add an **upper** bound obtained
from simulations to narrow the search.

**A concrete example (the baseline of the reproduction task).** The time-reversed van der Pol
system

$$
\dot{x}_1 = -x_2, \qquad \dot{x}_2 = x_1 + (x_1^2 - 1)x_2 \tag{12}
$$

has an exponentially stable origin and a region of attraction bounded by an unstable limit cycle;
it is the standard example. The linearisation is $A = \begin{bmatrix} 0 & -1\\ 1 & -1\end{bmatrix}$
with $\lambda = -\tfrac12 \pm \tfrac{\sqrt3}{2}i$. Solving $A^\top P + PA = -I$ gives

$$
P = \begin{bmatrix} 1.5 & -0.5 \\ -0.5 & 1 \end{bmatrix}, \qquad
  V(x) = 1.5x_1^2 - x_1x_2 + x_2^2, \qquad \det P = 1.25. \tag{13}
$$

Splitting (12) as $f(x) = Ax + \begin{bmatrix}0\\ x_1^2x_2\end{bmatrix}$ makes $\dot V$ closed
form:

$$
\dot{V} = x^\top(A^\top P + PA)x + 2x^\top P \begin{bmatrix}0\\ x_1^2x_2\end{bmatrix}
  = -\lvert x\rvert^2 + 2x_1^2x_2\left(x_2 - \tfrac12 x_1\right). \tag{14}
$$

In polar coordinates $x = r u(\vartheta)$ this is
$\dot V = -r^2 + 2r^4 u_1^2u_2(u_2 - \tfrac12 u_1)$, so the radius where $\dot V = 0$ solves
**explicitly** as $r^2 = 1/g(\vartheta)$ with $g := 2u_1^2u_2(u_2-\tfrac12u_1)$. The largest
certifiable level is

$$
c^\star = \min_{g(\vartheta)>0} \frac{u^\top P u}{g(\vartheta)} = 2.304478, \tag{15}
$$

and the area of $\Omega_{c^\star}$ is $\pi c^\star/\sqrt{\det P} = 6.475411$ (both to tolerance
$10^{-4}$, on a grid of $2\cdot10^6$ directions). Estimating the true region of attraction of the
same system by numerical integration gives an area of about $13.72$, so **the quadratic
certificate covers only 47% of the truth**. Closing that gap is the reproduction task.

**Where the assumptions break**: (4) is only sufficient. ⓐ If $\Omega_c$ is unbounded the
inclusion argument fails, so boundedness must be checked separately before the certificate means
anything. ⓑ Because of the degree gap in the Positivstellensatz there are nonnegative polynomials
that are SOS at no fixed degree — raising the degree may still fail, and "failure" does not mean
"unstable". ⓒ Solver error can return a "certificate" whose Gram matrix has a minimum eigenvalue
of about $-10^{-9}$. Always re-check a certificate after receiving it (sign of $\dot V$ on grids
and random samples, the minimum eigenvalue of the Gram matrices, and exact arithmetic after
rational rounding where possible).

## Proof sketch

### R1 — the Lyapunov theorem

**Hypotheses** H1: $V \in C^1(D)$, $V(0)=0$, $V>0$ on $D\setminus\{0\}$. H2: $\dot V \le 0$ on $D$.
**Conclusion** C: the origin is stable. (Strengthening H2 to $\dot V<0$ gives asymptotic stability.)

**Strategy**: use the sublevel sets of $V$ as a **trapping tube** inside the $\varepsilon$-ball.
A solution cannot cross a sublevel set, so take $\delta$ to be a ball inside the tube.

1. Given $\varepsilon>0$, choose $r \in (0,\varepsilon]$ with $\bar{B}_r \subset D$ and set
   $m := \min_{\lvert x\rvert = r} V(x)$; H1 and compactness of the sphere give $m>0$.
2. Pick $c \in (0,m)$ and consider $\Omega_c \cap B_r$. Continuity of $V$ and $V(0)=0$ give a
   $\delta>0$ with $B_\delta \subseteq \Omega_c$.
3. By H2, $V(\phi(t;x_0))$ is non-increasing. For $x_0 \in B_\delta$, $V(\phi(t)) \le V(x_0) \le c < m$,
   so the solution **cannot reach** $\lvert x \rvert = r$ (reaching it would force $V \ge m$).
   Hence $\lvert \phi(t;x_0)\rvert < r \le \varepsilon$, which is the definition of stability.
4. (Asymptotic) If $\dot V<0$ then $V(\phi(t))$ is strictly decreasing and bounded below, so
   $V \to a \ge 0$. If $a>0$ the solution is trapped in the compact shell
   $\{a \le V \le V(x_0)\}$, where $\dot V \le -\max < 0$, so $V<a$ in finite time —
   a contradiction. Hence $a=0$, i.e. $x \to 0$.

**Remove a hypothesis**: with only $\dot V \le 0$ you do not get asymptotic stability — take
$\dot x_1 = x_2$, $\dot x_2 = -x_1$ with $V = \lvert x\rvert^2$, where $\dot V \equiv 0$ and
solutions circle forever. R3 closes that gap. And even with $D = \mathbb{R}^n$, **the global
conclusion is false without radial unboundedness**. Counterexample (Khalil ch.4):

$$
\dot{x}_1 = \frac{-6x_1}{(1+x_1^2)^2} + 2x_2, \qquad
  \dot{x}_2 = \frac{-2(x_1+x_2)}{(1+x_1^2)^2}, \qquad
  V = \frac{x_1^2}{1+x_1^2} + x_2^2. \tag{16}
$$

Here $\dot V$ is negative everywhere except the origin (its maximum over the grid
$\lvert x\rvert \le 40$ is $-2.9\cdot10^{-9}$), but the sublevel sets of $V$ are unbounded for
$c \ge 1$, so the trapping tube of step 2 disappears. Indeed the solution from $x_0 = (4,\ 1.2)$
has $x_1$ past 144 by $t=60$ and still growing, and never returns to the origin (checked
numerically). The point is that $V$ can stay bounded while the state diverges.

Technical step omitted: that solutions extend to $[0,\infty)$ inside $\Omega_c$ (forward invariant
compact set plus local Lipschitz). See the proof of Khalil Thm 4.1.

### R2 — the converse theorem for exponential stability

**Hypotheses** H1: $\lvert \phi(t;x)\rvert \le k\lvert x\rvert e^{-\lambda t}$ for $x \in D_0$,
$k,\lambda>0$. H2: $f \in C^1$ with $\lVert \partial f/\partial x\rVert \le L$ on $D_0$.
**Conclusion** C: the $V$ of (1) is a Lyapunov function satisfying the four inequalities
($c_1,\dots,c_4$).

**Strategy**: build the Lyapunov function by **integrating along trajectories** (Massera's idea).
Its derivative needs no integration, thanks to the semigroup property
$\phi(\tau;\phi(t;x)) = \phi(t+\tau;x)$: only the two endpoints appear.

1. **Upper bound.** H1 gives $V(x) \le \int_0^T k^2\lvert x\rvert^2 e^{-2\lambda\tau}d\tau
   \le \frac{k^2}{2\lambda}\lvert x\rvert^2 =: c_2 \lvert x\rvert^2$.
2. **Lower bound.** H2 and Gronwall give $\lvert \phi(\tau;x)\rvert \ge \lvert x\rvert e^{-L\tau}$,
   hence $V(x) \ge \frac{1-e^{-2LT}}{2L}\lvert x\rvert^2 =: c_1\lvert x\rvert^2 > 0$.
3. **Decay rate.** Since $V(\phi(t;x))= \int_t^{t+T} \lvert\phi(s;x)\rvert^2 ds$, differentiating
   in $t$ gives $\dot V(x) = \lvert \phi(T;x)\rvert^2 - \lvert x\rvert^2 \le
   (k^2e^{-2\lambda T} - 1)\lvert x\rvert^2$. Choosing $T > \frac{\ln k}{\lambda}$ makes the
   bracket negative and yields $c_3>0$. **Choosing $T$ in that one line is the whole proof.**
4. **Gradient bound.** $x \mapsto \phi(\tau;x)$ has a derivative solving the variational equation,
   and H2 gives $\lVert \partial\phi/\partial x\rVert \le e^{L\tau}$, hence
   $\lVert \partial V/\partial x\rVert \le c_4\lvert x\rvert$ with $c_4$ explicit in
   $k,L,\lambda,T$. Smoothness of $V$ comes from smoothness of $\phi$.

**Remove a hypothesis**: if convergence is merely asymptotic rather than exponential, the integral
in (1) cannot be compared with $\lvert x\rvert^2$ and the constants of steps 2–3 vanish; one then
needs the weighted construction $\int_0^\infty g(\lvert \phi\rvert)d\tau$ of Massera and Kurzweil,
and the conclusion weakens to "a smooth $V$ exists" (Khalil Thm 4.16, 4.17). And if $f$ is merely
locally Lipschitz, solutions are unique but $\phi$ need not be $C^1$ in $x$, which breaks step 4.

Technical step omitted: existence and bounds for solutions of the variational equation
(Khalil Lemma 3.4, Thm 3.5).

### R3 — LaSalle's invariance principle

**Hypotheses** H1: $\Omega$ compact and forward invariant. H2: $V\in C^1$ with $\dot V \le 0$ on
$\Omega$. **Conclusion** C: $x_0 \in \Omega \Rightarrow \phi(t;x_0) \to M$, where $M$ is the
largest invariant set in $E=\{\dot V=0\}$.

**Strategy**: $\omega$-limit sets. "$V$ is constant on the limit set" $\Rightarrow$ "$\dot V = 0$
on the limit set".

1. By H2, $t \mapsto V(\phi(t))$ is non-increasing; by H1 it is bounded below, so a limit $a$ exists.
2. By H1 the trajectory is bounded, so the $\omega$-limit set $\omega(x_0)$ is non-empty, compact
   and **invariant**, and $\phi(t;x_0) \to \omega(x_0)$ in the distance sense. [standard facts]
3. If $p \in \omega(x_0)$ there are $t_n \to\infty$ with $\phi(t_n) \to p$, so continuity of $V$
   gives $V(p) = a$; that is, $V \equiv a$ on $\omega(x_0)$.
4. Since $\omega(x_0)$ is invariant, a solution starting in it stays in it with $V$ constant equal
   to $a$, so $\dot V = 0$ along that solution, i.e. $\omega(x_0) \subseteq E$; using invariance
   again, $\omega(x_0)\subseteq M$. Combined with the convergence of step 2, this is C.
5. (Barbashin–Krasovskii) If $V$ is positive definite with $\dot V\le0$, a bounded $\Omega_c$ can
   serve as $\Omega$; if the only solution staying in $E$ is the origin then $M=\{0\}$ and the
   origin is asymptotically stable.

**Remove a hypothesis**: drop **compactness** in H1 and the conclusion is false — (16) is exactly
that case, with $\dot V\le0$ but unbounded sublevel sets and solutions running to infinity. Also
$M$ can be bigger than the origin: if $E$ contains a limit cycle, LaSalle only says solutions
converge to that cycle.

Technical step omitted: the properties of $\omega$-limit sets (non-empty, compact, invariant,
attracting). Khalil Lemma 4.1.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R4)** Re-derive the gain $\gamma$ of (3) with an arbitrary
$\theta \in (0,1)$ in place of $\theta = \tfrac12$. How does $\gamma$ change as $\theta \to 1$,
and what do you lose instead?
*Solution sketch*: (5) becomes $\dot V \le -(1-\theta)\alpha_3$ and (7) becomes
$c_\mu = \alpha_2(\alpha_3^{-1}(\sigma(\mu)/\theta))$. As $\theta \to 1$, $c_\mu$ shrinks so
$\gamma$ **improves**, but the decay factor $(1-\theta)$ in (6) goes to zero, so the convergence
$\beta$ degrades. The trade between gain and convergence rate sits in that one parameter.

**P2 (derivation, ★★, R2)** Under what condition is $V$ well defined if $T \to \infty$ in (1)?
With the $T=\infty$ version, how does the $\dot V$ computation of step 3 simplify, and which
bound is lost?
*Solution sketch*: the exponential bound of H1 makes the integral converge, so $T=\infty$ is well
defined. Then $\dot V = -\lvert x\rvert^2$ **exactly**, so $c_3=1$. What is lost is not the
constant $c_1 = (1-e^{-2LT})/2L$ (it merely loosens to $1/2L$) but the practicality of a finite
$T$: it can be integrated numerically without knowing $k$ and $\lambda$.

**P3 (numerical, ★, R5)** For (12) compute ⓐ $P$, ⓑ $c^\star$, ⓒ the area of $\Omega_{c^\star}$.
*Answers*: ⓐ the $P$ of (13) (tolerance $10^{-9}$) ⓑ $c^\star = 2.304478$ ($10^{-4}$)
ⓒ $6.475411$ ($10^{-4}$). Check: use the closed form (14), solve $\dot V=0$ in polar coordinates
and minimise $u^\top Pu/g(\vartheta)$. The minimising direction is $\vartheta^\star \approx 2.42174$
rad with $r^\star \approx 1.138343$ there. The area is $\pi c^\star/\sqrt{\det P}$.

**P4 (implementation, ★★★, R5)** Implement the alternating optimisation (4) for a quartic $V$:
build the monomial basis, the Gram matrix constraints and the bisection in $c$ yourself (no
SOS-specific package — only an SDP solver).
*Rubric*: ⓐ with a quadratic $V$ it reproduces the $c^\star$ of (15) to within $10^{-3}$
ⓑ the certified area for the quartic $V$ exceeds the quadratic baseline ⓒ the certificate is
re-checked **independently** ($\dot V<0$ at $10^5$ random points, minimum Gram eigenvalue
reported) ⓓ the termination condition and iteration cap of the alternation are in the code.

**P5 (counterexample, ★★, R4)** Build a system that is 0-GAS but not ISS in a form **different**
from (10), and show which inequality of (2) cannot hold for any $\alpha_3$. Then exhibit a class-
$\mathcal{K}$ function showing the same system is locally ISS.
*Property checklist*: ⓐ GAS for $u\equiv0$ ⓑ some bounded input makes the state unbounded
(finite-time escape suffices) ⓒ the structure forces $\alpha_3$ to be a bounded class-$\mathcal{K}$
function (inputs multiplying the state are typical) ⓓ the local claim states an explicit bound on
the input size.

**P6 (proof, ★★★, R3)** Derive Barbashin–Krasovskii from LaSalle, then construct a system with
$\dot V \le 0$ whose $E$ contains a limit cycle, so that LaSalle does **not** give asymptotic
stability.
*Solution sketch*: the premise is boundedness of $\Omega_c$. For the construction, work in polar
coordinates with something like $\dot r = r(1-r)(\cdot)$ and take $V$ as a function of $r$ so
that $\dot V$ vanishes at $r=1$.

**P7 (paper, ★★, R4·R5)** Read Topcu et al. 2008 and write, in three sentences each, ⓐ whether
simulation gives an upper or a lower bound on the region of attraction, ⓑ where that information
enters the SOS search, ⓒ what the procedure reports when it meets a counterexample. Then find two
pieces of information the authors do not report that block reproduction.
*Rubric*: distinguishing "simulation finds diverging initial conditions and so gives an **outer**
bound, while SOS gives a certified **inner** bound" passes. Naming missing solver settings,
degrees or normalisation earns extra credit.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read in three passes and attack questions 4, 5, 6, 7 in the third.

1. **Sontag, "Smooth stabilization implies coprime factorization" (1989, IEEE T-AC)**
   — role: `seminal`. <https://doi.org/10.1109/9.28018>
   The paper where ISS was first defined. The title is about coprime factorisation, but what we
   read is the ISS definition and its main theorem.
   Extra questions: ⓐ Why are $\mathcal{KL}$ and $\mathcal{K}$ functions used in the definition,
   and what does a "linear gain" ($L_\infty$ induced norm) formulation miss?
   ⓑ What does the result **not** guarantee — in particular for a system like (10)?
2. **Papachristodoulou & Prajna, "On the construction of Lyapunov functions using the sum of
   squares decomposition" (2002, IEEE CDC)** — role: `standard`.
   <https://doi.org/10.1109/CDC.2002.1184414>
   Extra questions: ⓐ Compare their formulation with our (4) and state the role of the multiplier
   $\lambda$ in one line. ⓑ How are rational or non-polynomial nonlinearities (trigonometric
   terms) handled, and what does that transformation assume?
3. **Topcu, Packard & Seiler, "Local stability analysis using simulations and sum-of-squares
   programming" (2008, Automatica)** — role: `standard`.
   <https://doi.org/10.1016/j.automatica.2008.03.010>
   The original of the reproduction task. Look at how simulation and SOS squeeze the answer from
   **both** sides.
   Extra questions: ⓐ Where does conservatism enter when simulation data are turned into linear
   constraints? ⓑ Moving the same procedure to a ten-dimensional system, which step breaks first
   (count the SDP size in the degree and the dimension)?

**The ten fixed questions**: (1) which problem under which assumptions (2) what exactly earlier
work could not do (3) the core idea in one equation (4) what is guaranteed and **what is not**
(5) independent and dependent variables and baselines, fairly tuned (6) do the metrics match the
claim, are variance and seeds reported (7) what is missing for reproduction (8) the first
assumption to doubt if the result is wrong (9) computational and memory complexity and real-time
feasibility (10) what you would change to go beyond it in a year.

## Reproduction task

**Tier R1 (numerical check).** Budget: laptop CPU, under one minute including the SDP; numpy plus
scipy plus one SDP solver (SCS or Clarabel through cvxpy). The system is the time-reversed van der
Pol system (12). There is no input data — the system is given in closed form and you generate the
initial conditions.

**Acceptance criteria (all four)**

1. **Reproduce the baseline**: for the quadratic $V$ of (13),
   $c^\star = 2.304478 \pm 10^{-4}$ and
   $\operatorname{area}(\Omega_{c^\star}) = 6.475411 \pm 10^{-4}$.
2. **Soundness of the certificate**: for the $(V_4, c_4)$ found by SOS ($V_4$ quartic),
   $\dot V_4 < 0$ at every one of $10^5$ points drawn uniformly from $\Omega_{c_4}$ (keeping only
   points with $\lvert x\rvert > 10^{-3}$), and the minimum eigenvalue of both Gram matrices is
   $\ge -10^{-8}$.
3. **Certificate $\subseteq$ truth**: all of $10^3$ points drawn from the boundary of
   $\Omega_{c_4}$ reach $\lvert x(T)\rvert < 10^{-3}$ under numerical integration
   ($T = 80$, RK4, $\Delta t \le 2\cdot10^{-3}$). **If even one diverges the certificate is
   wrong** — in that case report the re-check of criterion 2 and your solver settings.
4. **Improvement**: $\operatorname{area}(\Omega_{c_4}) \ge 1.3 \times 6.475411 = 8.418$. For
   reference, the area of the true region of attraction estimated by integration is about
   $13.72$ (radius bisection along 361 directions, star-shaped approximation), so the quartic
   certificate must cover at least 61% of it.

**Baselines**: ⓐ the quadratic certificate (criterion 1, area 6.475411) and ⓑ the region of
attraction estimated by simulation (area ≈ 13.72). The certified area must lie **between** the
two; exceeding the upper one means criterion 2 or 3 is false.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| The SDP reports "infeasible" | $\epsilon$ too large, or $\lambda$ fixed to degree 0 (a constant) | lower $\epsilon$ to $10^{-6}$, raise $\lambda$ to degree 2 and re-solve |
| The certified area exceeds the true region of attraction | sign convention of the multiplier, or the wrong $f$ substituted in $\dot V$ | run the quadratic $V$ first and check that $c^\star = 2.304478$ |
| The alternation oscillates | the two steps maximise different quantities | fix one objective to $c$ and the other to the shape-set $\beta$, and log monotonicity |
| Minimum Gram eigenvalue around $-10^{-4}$ | solver tolerance and scaling | normalise the state to $O(1)$ and tighten the solver tolerance to $10^{-10}$ |
| Integration diverges and criterion 3 fails | $\Delta t$ too large near the limit cycle | halve $\Delta t$ and see whether the verdict changes (if it does, the integrator is the problem) |

## Open problems

- **(open problem) Certifying stability on learned dynamics** — if $f$ is a neural network the
  polynomial structure of (4) is gone, and ReLU networks are non-smooth, so $\dot V$ exists only
  pointwise. Current approaches:
  [Chang et al., Neural Lyapunov Control (2020)](https://arxiv.org/abs/2005.00611), which learns
  from counterexamples, and
  [Dai et al., Lyapunov-stable neural-network control (2021)](https://arxiv.org/abs/2109.14152),
  which verifies with MILP. The gap: certification that is **sound** and polynomial in the network
  size, plus training objectives that enlarge the certified region.
- **(open problem) The cost of certification in the dimension** — the Gram matrix of a quartic $V$
  is square of side $\binom{n+2}{2}$, so $n=10$ already means thousands of SDP variables, and
  raising the degree grows it exponentially. Current approaches: relaxations that drop to LP or
  SOCP such as [DSOS/SDSOS (Ahmadi & Majumdar 2017)](https://arxiv.org/abs/1706.02586), and
  exploiting coordinate decomposition and sparsity. The gap: certification usable at robot scale
  (20–50 states) with quantified conservatism.
- **(open problem) Lyapunov theory for systems with contact and impact** — solutions are
  non-smooth and may not be unique, so $\dot V$ does not exist in the classical sense. Current
  approaches: non-smooth Lyapunov functions and differential inclusions (Clarke derivatives),
  measure differential inclusions. The gap: region-of-attraction certificates for multibody
  systems with complementarity constraints — the same wall appears in `c2-contact-dynamics` and
  `c4-contact-implicit-hybrid`.
- **(open problem) Estimating ISS gains from data** — the $\gamma$ of (3) is derived from a model,
  but the models used on real robots are wrong. There is no established procedure for giving a
  **confidence upper bound** on $\gamma$ from finitely many experiments. Current approaches:
  extreme-value estimation, scenario optimisation. The gap: estimators with guarantees in the
  number of samples.

## Concept check

Take it with `rc quiz c3-lyapunov-stability`. The quiz is **for concept checking only**; the real
work is the problem set and the reproduction task above (`lesson-standard.md` §4). Four questions
ask: why radial unboundedness is needed for a global conclusion; what fraction of $\alpha_3$ is
left as the decay rate once the input term is absorbed; what an infeasible SOS program does and
does not tell you; and why $\dot x = -x + x^2u$ is not ISS although it is 0-GAS.

## How to study this stage

1. **Rewrite the definitions with comparison functions (40 min)** — write "stable", "asymptotically
   stable", "exponentially stable" and "ISS" both in $\varepsilon$–$\delta$ form and in
   $\mathcal{KL}$ form, and translate between them. Once that is fluent, ISS stops being a new
   concept and reads as "the $\mathcal{KL}$ estimate plus an input term". Read Khalil ch.4.4 on
   comparison functions alongside.
2. **Compress each proof to one strategy line, then restore it (90 min)** — R1 is "sublevel sets
   are a tube", R2 is "integrate along the trajectory", R3 is "$V$ is constant on the
   $\omega$-limit set". Memorise the three lines and rebuild the steps on blank paper, checking
   only the step that blocks you in Khalil Thm 4.1, 4.14, 4.4.
3. **Meet the counterexamples by hand (60 min)** — integrate (16) and watch $x_1$ grow while
   $\dot V<0$, then vary $\mu$ in (10) and find the escape threshold $1/\mu$. **Only people who
   have seen a counterexample remember the hypothesis.**
4. **Write the ISS derivation as four steps (60 min)** — (5)→(6)→(8)→(9), noting in the margin
   which assumption each step uses. Solving P1 shows how $\theta$ trades gain against
   convergence rate.
5. **For SOS, remember one thing: a conditional inequality absorbed by a multiplier (90 min)** —
   line (11) is the whole idea. Then reproduce the quadratic baseline of the reproduction task
   **by hand** first (the closed form (14) needs no SDP), and only then move to the quartic SOS.
   In the other order you will spend all your time debugging the solver.
6. **Read the papers for "what is not guaranteed" (150 min)** — Sontag 1989 gives the definition,
   Papachristodoulou 2002 the formulation, Topcu 2008 the procedure. For all three write a
   paragraph answering fixed question 4 (what is not guaranteed). The one-page note per paper is
   **mandatory**.
7. **Pick one open problem (30 min)** — choose one of the four and write a paragraph on why it is
   still open. The same question returns, in the shape of safety constraints, in the last lesson
   of this module (CBFs).

**Passing bar**: you can state the proof strategies of R1 and R3 from memory, derive the $\gamma$
of (3), build an example that is 0-GAS but not ISS, and you have code meeting all four acceptance
criteria of the reproduction task plus one-page notes on the three papers.
