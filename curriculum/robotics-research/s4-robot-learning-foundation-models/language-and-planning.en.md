---
id: s4-language-and-planning
lang: en
title: Coupling language with planning
summary: >-
  Formalize the boundary between symbolic abstraction and geometric feasibility, and show by
  construction that **symbolic preconditions do not imply geometric feasibility** (downward
  refinability fails). A symbolic verifier therefore drives precondition violations to zero but
  does **nothing at all** for affordance failures, and success decays exponentially in plan
  length as $(1-p_{\mathrm{aff}})^T$. Finally, derive the optimal abstraction granularity in
  closed form, $g^\star = a/\sqrt{2e}$.
objectives:
  - Formalize symbolic abstraction as a map $\alpha$ and define downward refinability.
  - Construct an example where symbolic preconditions do not imply geometric feasibility.
  - Distinguish the failures a symbolic verifier removes from the ones it cannot touch.
  - Derive the exponential law $(1-p_{\mathrm{aff}})^T$ and convert it into plan lengths.
  - Derive and compute the optimal granularity $g^\star = a/\sqrt{2e}$.
  - Separate what an LLM planner guarantees from what it does not.
tags: [language-and-planning, hierarchical-policy, abstraction, llm-planning, research]
---

# Coupling language with planning

## Premises and notation

We use the failure-decomposition view of `s4-robot-data-scaling` and the state/action notation of
`c8-mdp-pomdp-bellman`. Additional **recommended prerequisites**:

- Discrete planning: STRIPS-style precondition/effect representations, graph search (BFS).
- Probability: products of independent events, exponential decay, decomposing failures by cause
  with conditional probability.
- Optimization: interior optima of a smooth univariate function (first-order condition), turning
  products into sums with $\log$.

Notation:

| Symbol | Meaning |
|---|---|
| $s \in \mathcal{S}$ | **Geometric (low-level) state**: continuous joint angles, object poses |
| $\bar{s} \in \bar{\mathcal{S}}$ | **Symbolic (high-level) state**: a set of predicates such as `in(room3)`, `holding(cup)` |
| $\alpha : \mathcal{S} \to \bar{\mathcal{S}}$ | The abstraction map, $\bar{s} = \alpha(s)$ |
| $\bar{a}$ | A symbolic action (skill) with precondition $\mathrm{pre}(\bar{a})$ and effect $\mathrm{eff}(\bar{a})$ |
| $T$ | Plan length (number of symbolic actions) |
| $p_{\mathrm{pre}}$ | Rate of symbolic precondition violations (planner hallucination, etc.) |
| $p_{\mathrm{aff}}$ | **Affordance gap**: the preconditions hold but no geometric motion exists |
| $p_{\mathrm{exec}}$ | Rate of stochastic low-level execution failure |
| $g$ | Abstraction granularity; larger is finer (symbolic actions are chopped smaller) |

**The confusion this lesson targets.** In the architecture "an LLM plans and a low-level policy
executes", the claim that the plan is **symbolically valid** and the claim that the robot **can
actually do it** are different statements. Conflating them yields the wrong prescription: "improve
the planner and success will rise." This lesson separates and measures the two failures, and
quantifies the part that symbolic verification **cannot reduce in principle**.

## Core results

The bracketed tags are derivation depths (the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (Downward refinability and its failure) [D2]** — a symbolic plan
  $\bar{a}_1,\dots,\bar{a}_T$ is symbolically valid at $\alpha(s_0)$ when
  $\mathrm{pre}(\bar{a}_t) \subseteq \bar{s}_{t-1}$ for every $t$. The plan is **downward
  refinable** when a geometric trajectory realizing each step exists, and for the abstraction to
  be downward refinable we need
  $$
  \forall s \text{ with } \mathrm{pre}(\bar{a}) \subseteq \alpha(s): \;\;
    \exists \text{ a geometric trajectory } s \rightsquigarrow s' \text{ with } \alpha(s') = \mathrm{eff}(\bar{a}) . \tag{1}
  $$
  **Abstractions used in practice do not satisfy (1)** — predicates encode only **necessary**
  conditions for geometric feasibility (construction in derivation §R1).
- **R2 (What a symbolic verifier reduces and what it does not) [D2]** — verifying the plan
  symbolically and re-planning on failure drives precondition violations to **zero**. Affordance
  failures lie outside the verifier's field of view, so they are **not reduced at all**.
  Measured ($p_{\mathrm{aff}}=0.04$, $p_{\mathrm{exec}}=0.02$, hallucination rate $0.15$,
  20,000 trials):
  $$
  \text{no verifier: } 45.17\% \;\to\; \text{verifier: } 73.68\%,
  \qquad p_{\mathrm{pre}}\text{ failures } 37.27\% \to 0.00\% \tag{2}
  $$
  and **with a verifier, a hallucinating planner is indistinguishable from a perfect one**
  ($73.68\%$ vs $73.92\%$). The remaining $26\%$ is entirely the affordance gap and execution noise.
- **R3 (The exponential law of absent feasibility guarantees) [D2]** — if per-step affordance
  failures are independent,
  $$
  \Pr[\text{success}] \;=\; (1-p_{\mathrm{aff}})^{T}\,(1-p_{\mathrm{exec}})^{T}
    \;\approx\; e^{-(p_{\mathrm{aff}}+p_{\mathrm{exec}})T}, \tag{3}
  $$
  an **exponential decay in plan length**. Measured: at $p_{\mathrm{aff}}=0.05$ the success rates
  for $T = 2,5,10,20,40$ match $(1-p)^T$ with ratios $0.994$–$1.007$. **No amount of improvement
  on the symbolic side reduces this term.**
- **R4 (Optimal abstraction granularity) [D2]** — raising $g$ shrinks the affordance gap
  ($p_{\mathrm{aff}} \approx a/g$) but lengthens the plan ($T \approx cg$). With a fixed per-step
  execution risk $e$, success is $\big[(1-a/g)(1-e)\big]^{cg}$; expanding $\log$ to second order
  and differentiating gives
  $$
  g^\star \;=\; \frac{a}{\sqrt{2e}}, \tag{4}
  $$
  an **interior** optimum. At $a=0.25$, $e=0.01$ we get $g^\star = 1.768$, and the numerical grid
  optimum is $g=2$ (success $0.31706$), agreeing with $g=1.77$ ($0.31688$) to within $0.06\%$.
- **R5 (What an LLM planner does and does not guarantee) [D1]** — an LLM planner supplies a
  **distributional prior** (a plausible ordering of subgoals). It supplies no guarantee: symbolic
  validity comes from a **verifier**, geometric feasibility from a **geometric checker**. SayCan's
  affordance function is an attempt to approximate the latter with a **learned value function**,
  and a learned value is not a guarantee, so it lowers $p_{\mathrm{aff}}$ in (3) without driving
  it to zero.

## Derivations

### R1 — a construction where downward refinability fails

**Formalization.** A symbolic state is a set of predicates and the abstraction is $\alpha(s)$. A
symbolic action $\bar{a}$ is a pair $(\mathrm{pre}, \mathrm{eff})$, and the symbolic transition is
$\bar{s}' = (\bar{s} \setminus \mathrm{del}) \cup \mathrm{add}$ whenever
$\mathrm{pre} \subseteq \bar{s}$.

**Downward refinability.** The abstraction is downward refinable when (1) holds. If it does, "we
found a symbolic plan" means "the robot can do it", so symbolic planning and geometric execution
can be designed **separately**. That is exactly the premise of the hierarchy.

**The construction that fails.** Take rooms $0,\dots,5$ connected in a ring, with symbolic actions
$\texttt{move}(i,j)$ for $j = i+1 \bmod 6$ and precondition `in(i)`. Now suppose the doorway
between rooms $2$ and $3$ is **narrower than the robot**. The symbolic state does not encode
doorway width, so $\alpha(s)$ is `in(2)` and
$\mathrm{pre}(\texttt{move}(2,3)) = \{\texttt{in}(2)\}$ **holds**. Yet no geometric trajectory
realizes that action — the conclusion of (1) is false.

**Why this is generic.** Predicates are finite and geometric state is continuous, so $\alpha$ must
discard information. The moment the discarded information bears on feasibility, (1) breaks, and
that moment involves quantities that are commonplace in robotics: **doorway width, friction,
clearance, joint limits**. Hand-designing an abstraction that satisfies (1) therefore amounts to
"putting all of geometry into the predicates", which destroys the benefit of symbolic planning (a
small search space). **That trade-off is the centre of this lesson.**

**Where the assumptions break.** (1) requires only **existence**, so it is a weak condition and it
still breaks. Demanding something stronger (that a **uniformly** short trajectory exists from every
$s$) makes matters worse. Relaxing (1) **probabilistically** — "it holds with rate
$1-p_{\mathrm{aff}}$" — is the model behind R3, and it is the relaxation this lesson uses.

### R2 — the failures a verifier removes and the ones it leaves

**Separate three failures.** In a single trial, failure comes in three kinds.

1. **Precondition violation**: the plan is not symbolically valid (planner hallucination, wrong
   ordering).
2. **Affordance gap**: it is symbolically valid but geometrically unrealizable — the failure of (1).
3. **Execution failure**: it is realizable, but low-level control fails stochastically.

A symbolic verifier sees **only 1**. Checking the plan against $\mathrm{pre}$ and re-planning on
failure drives 1 to zero. Items 2 and 3 depend on information the verifier cannot access
(geometry), so they **do not change**.

**Measurement.** In the ring-of-rooms domain with $p_{\mathrm{aff}} = 0.04$,
$p_{\mathrm{exec}} = 0.02$, planner hallucination rate $0.15$, 20,000 trials:

| Setting | Success | Precondition | Affordance | Execution |
|---|---|---|---|---|
| No verifier, hallucinating planner | $45.17\%$ | $37.27\%$ | $12.07\%$ | $5.47\%$ |
| Symbolic verifier, hallucinating planner | $73.68\%$ | $0.00\%$ | $17.86\%$ | $8.46\%$ |
| Symbolic verifier, perfect planner | $73.92\%$ | $0.00\%$ | $17.89\%$ | $8.19\%$ |

Read three things. ⓐ The verifier **removes** precondition failures, $37.27\% \to 0.00\%$.
ⓑ The **share** of affordance failures rises ($12.07\% \to 17.86\%$) — not because the absolute
rate rose but because more trials now reach the geometric stage, changing the denominator.
Geometric failures are **indifferent** to the verifier. ⓒ **With a verifier, the hallucinating and
the perfect planner are indistinguishable** ($73.68\%$ vs $73.92\%$, a difference at the level of
the standard error over 20,000 trials). So **planner quality is nearly meaningless behind a
verifier**, and the remaining $26\%$ is entirely the abstraction gap and execution noise.

**The prescription changes.** What ⓒ means is that the lever is **a verifier plus a geometric
checker**, not "a better LLM". Investment in the planner pays off only when there is no verifier
(the $45\% \to 74\%$ jump is the verifier's doing); with a verifier the return is $0.24$ percentage
points.

**Where the assumptions break.** This decomposition assumes the three failures are
**independent**. In reality they are correlated — a hallucinated plan takes a longer route and so
increases affordance exposure, among other couplings. (The low affordance share in the
no-verifier row is the effect of precondition failures happening **first**, so the trial never
reaches the geometric stage.) The shares in the table must therefore be read as **conditional**,
and comparisons of absolute rates must be normalized by the number of trials that reached the
stage (problem P5).

### R3 — the exponential law

If the plan has length $T$ and the per-step affordance and execution failures are independent,
success is the event that every step succeeds, so

$$
\Pr[\text{success}] = \prod_{t=1}^{T}(1-p_{\mathrm{aff}})(1-p_{\mathrm{exec}})
  = \big[(1-p_{\mathrm{aff}})(1-p_{\mathrm{exec}})\big]^{T},
$$

which is (3). Expanding $\log$ for $p \ll 1$ gives
$\Pr \approx \exp\!\big(-(p_{\mathrm{aff}}+p_{\mathrm{exec}})T\big)$.

**Convert it into numbers.** At $p_{\mathrm{aff}} = 0.05$ the plan length at which success falls to
$50\%$ is $T_{1/2} = \log 2 / \log\frac{1}{1-p} = 0.693/0.0513 = 13.5$ steps. Measured:

| $T$ | Measured success | $(1-p)^T$ | Ratio |
|---|---|---|---|
| 2 | $0.9001$ | $0.9025$ | $0.997$ |
| 5 | $0.7712$ | $0.7738$ | $0.997$ |
| 10 | $0.5953$ | $0.5987$ | $0.994$ |
| 20 | $0.3610$ | $0.3585$ | $1.007$ |
| 40 | $0.1286$ | $0.1285$ | $1.001$ |

**This term cannot be reduced from the symbolic side.** Verifiers, better planners and more
examples all act on $p_{\mathrm{pre}}$, and $p_{\mathrm{pre}}$ **does not appear** in (3). To
reduce it you must ⓐ attach a geometric checker and lower $p_{\mathrm{aff}}$ directly, ⓑ shorten
the plan $T$ (coarsen the abstraction — which raises $p_{\mathrm{aff}}$, R4), or ⓒ allow
**recovery** after failure, breaking the independent-product structure. ⓒ is why re-planning loops
matter in practice.

**Where the assumptions break.** Independence is the crux. If failures are correlated (a plan that
must pass the same narrow doorway repeatedly), (3) is wrong in one direction or the other — a
repeated obstacle makes success **higher** than $(1-p)^T$, since passing once means you can pass
again. Conversely, accumulating factors such as fatigue or battery drain make it lower.

### R4 — the optimal abstraction granularity

Raising $g$ means chopping symbolic actions smaller. Two effects pull in opposite directions.

- The affordance gap shrinks: a finely chopped action has preconditions **closer** to geometric
  feasibility. Model it as $p_{\mathrm{aff}}(g) = a/g$.
- The plan gets longer: $T(g) = cg$.
- A **fixed** per-step execution risk $e$ remains regardless of granularity (sensor noise, contact
  uncertainty).

Substituting into (3),

$$
S(g) = \Big[\big(1 - \tfrac{a}{g}\big)(1-e)\Big]^{cg} .
$$

Take $\log$ and expand to second order for $a/g \ll 1$:

$$
\log S = cg\Big[\log\big(1-\tfrac{a}{g}\big) + \log(1-e)\Big]
  \approx cg\Big[-\tfrac{a}{g} - \tfrac{a^2}{2g^2} - e\Big]
  = -ca - \frac{ca^2}{2g} - ceg .
$$

Differentiating in $g$ and setting to zero gives $\dfrac{ca^2}{2g^2} = ce$, that is, (4):

$$
g^\star = \frac{a}{\sqrt{2e}} .
$$

**The constant $c$ cancels** — the optimal granularity is independent of the plan-length
coefficient and is set solely by the ratio of the "affordance-gap coefficient $a$" to the
"per-step execution risk $e$". At $a=0.25$, $e=0.01$ we get $g^\star = 1.768$; on the numerical
grid $g=2$ is optimal ($S=0.31706$) with $g=1.77$ at $0.31688$, inside $0.06\%$.

**How to read it.** If execution is nearly perfect ($e \to 0$) the optimal granularity is
**infinite** — finer is always better. If execution is unreliable (large $e$) the optimum is
coarse — a few chunky skills are better. Reports that "we subdivided the skills further and
success dropped" are reports of having moved to the right of (4).

**Where the assumptions break.** $p_{\mathrm{aff}}(g) = a/g$ and $T(g) = cg$ are **models**. Real
abstraction families are not parameterized by $g$, they are discrete, and $p_{\mathrm{aff}}$ need
not be monotone in $g$ (splitting a skill can complicate its preconditions and widen the gap).
The second-order expansion also uses $a/g \ll 1$, so (4) is unusable for $g \lesssim a$.

## Proof sketches

### R3·R4 — the exponential law and the optimal granularity [D2 → in proof form]

**Hypotheses** H1: per-step affordance and execution failures are **independent** with
step-independent rates. H2: $p_{\mathrm{aff}}, p_{\mathrm{exec}} \in [0,1)$. H3:
$p_{\mathrm{aff}}(g) = a/g$, $T(g) = cg$, $a/g \ll 1$. H4: a failure ends the trial (no recovery).
**Conclusions** C1: (3). C2: (4).

**Strategy**: C1 is a product of independent events. C2 is a second-order expansion of $\log S$
plus the first-order condition.

1. Write success as the intersection of per-step successes and multiply by independence → C1.
   Uses: H1, H4.
2. Write $\log S = cg[\log(1-a/g) + \log(1-e)]$. Uses: H3.
3. Apply $\log(1-x) = -x - x^2/2 + O(x^3)$ at $x = a/g$ to get
   $\log S \approx -ca - ca^2/(2g) - ceg$. Uses: the $a/g \ll 1$ part of H3.
4. The first-order condition in $g$, $ca^2/(2g^2) = ce$ → C2. The second derivative is negative, so
   it is a maximum.

**Delete one hypothesis**: dropping H4 (no recovery) breaks the product structure of step 1 and
success no longer decays exponentially in $T$ — this is exactly how a re-planning loop defeats (3).
Dropping the independence in H1 makes (3) an upper or a lower bound depending on the sign of the
correlation. Replacing $p_{\mathrm{aff}} \propto 1/g$ in H3 with another decay rate $a/g^\beta$
turns (4) into the form
$g^\star = \big(\beta a^\beta \cdot \tfrac{\beta+1}{2}/e\big)^{1/(\beta+1)}$, so without knowing
$\beta$ the optimal granularity cannot be predicted.

## Problem set

Each problem states how to approach it. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R3)** From (3), write $T_{1/2}$, the plan length at which success is $1/2$,
in closed form and evaluate it at $p_{\mathrm{aff}} + p_{\mathrm{exec}} = 0.07$. Then derive how (3)
changes if **one recovery attempt** is allowed.
*Solution sketch*: $T_{1/2} = \log 2/\log\frac{1}{(1-p_a)(1-p_e)}$. At $0.07$,
$\log 2/0.0726 = 9.5$ steps. One recovery makes each step "success, or failure followed by
successful recovery", so the per-step success rate becomes $1-p^2$ and $T_{1/2}$ lengthens by a
**squared** factor in $p$ — the point is that recovery changes the base of the exponent.

**P2 (proof, ★★★, R1)** State a **sufficient** condition for an abstraction satisfying downward
refinability (1) to exist: show that (1) holds if $\alpha$ is a homomorphism with respect to the
geometric reachability relation, and explain why that condition almost never holds in practice.
*Strategy and key inequality*: $\alpha$ being a homomorphism means that whenever
$\bar{s} \to \bar{s}'$ is symbolically possible, a trajectory into $\alpha^{-1}(\bar{s}')$ exists
from **every** point of $\alpha^{-1}(\bar{s})$; (1) then follows immediately. It breaks in practice
because $\alpha^{-1}(\bar{s})$ is a large set that mixes points from which you can get there with
points from which you cannot. The expansion is left hidden.

**P3 (computation, ★, R3·R4)** Compute (ⓐ) the success rate at $T=20$ with
$p_{\mathrm{aff}}=0.05$, $p_{\mathrm{exec}}=0$; (ⓑ) $T_{1/2}$ under the same conditions; (ⓒ)
$g^\star$ and the success there for $a=0.25$, $e=0.01$ ($c=4$).
*Answers*: (ⓐ) $0.95^{20} = 0.35849$ (tolerance $10^{-5}$). (ⓑ)
$\log2/\log(1/0.95) = 0.6931/0.05129 = 13.51$ steps. (ⓒ) $g^\star = 0.25/\sqrt{0.02} = 1.7678$,
$S = [(1-0.25/1.7678)(0.99)]^{4\cdot1.7678} = 0.31688$ (tolerance $10^{-4}$).
Cross-check: compare (ⓐ) with the reproduction task's measured $0.3610$ and confirm the ratio is
$1.007$; confirm (ⓒ) is within $0.1\%$ of the grid optimum $g=2$ at $0.31706$.

**P4 (implementation, ★★, R2·R3·R4)** Implement the reproduction task and pass all four conditions.
*Rubric*: ⓐ the three failure causes are recorded **mutually exclusively** (classified by
whichever happened first); ⓑ the verifier **re-plans** on failure (rather than simply counting a
failure); ⓒ when reporting the affordance share you **also report the value normalized by the
number of trials that reached the geometric stage** (the assumption in R2); ⓓ the comparison in (3)
is run with $p_{\mathrm{exec}}=0$ separated out; ⓔ the grid for (4) is dense near $g^\star$.

**P5 (counterexample, ★★, R2·R3)** Show that two claims are false: (i) "the affordance share rising
from 12% to 18% means the verifier increased affordance failures"; (ii) "success always decays
exponentially in plan length".
*Property checklist*: (i) shares are conditional — the verifier removed precondition failures, so
**more trials reach the geometric stage** and the denominator changed. Normalized by trials that
reached it, the affordance rate is unchanged (in the measurement both cases are around
$p_{\mathrm{aff}}T$). (ii) In a plan that passes the same obstacle repeatedly, failures are
**perfectly correlated**, so success is $(1-p)$ independent of $T$. Independence is the whole of (3).

**P6 (paper, ★★, R2·R5)** Read SayCan (§3–4) and Code as Policies (§3, §5) and write, in three
sentences or fewer each: (i) which of symbolic validity and geometric feasibility each paper
addresses, and how; (ii) whether SayCan's affordance function reduces $p_{\mathrm{aff}}$ in (3) —
is it a guarantee or an estimate; (iii) whether either paper reports failures broken down by cause.
*Grading rubric*: (i) Identifying SayCan's "can say × can do" product structure and Code as
Policies' separation of code generation from perception-API calls passes. (ii) It is a learned value
function, hence an **estimate** and not a guarantee, which is why it lowers $p_{\mathrm{aff}}$
without driving it to zero. (iii) They mostly report only total success with no decomposition by
cause — which is what makes the prescription in (2) (where to invest) impossible to form. Writing
only "the LLM plans well" fails.

**P7 (derivation, ★★, R4)** Generalize (4) to $p_{\mathrm{aff}}(g) = a/g^\beta$ and write $g^\star$
as a function of $\beta$. Check that it returns to (4) at $\beta=1$, and state what the limit
$\beta \to 0$ means.
*Solution sketch*: differentiating $\log S \approx cg[-a g^{-\beta} - e]$ gives a condition of the
form $a(\beta-1)g^{-\beta} = e$ (including the second-order term complicates it further); at
$\beta=1$ the first-order term becomes independent of $g$, so the second-order term determines the
optimum — which is (4). $\beta \to 0$ means "raising granularity does not shrink the affordance
gap", so the optimal granularity is the **coarsest** one (keep the plan short).

## Paper reading

**Two required papers.** Write a one-page note on each using the ten fixed questions
(the "Reading papers" section of lesson `f0-how-to-read-this-track`).

1. **Ahn et al., "Do as I can, not as I say: grounding language in robotic affordances" (2022,
   CoRL)** — role: `seminal`. <https://arxiv.org/abs/2204.01691> — §3–4.
   Why read it: the structure of multiplying a language model's "can say" by a learned
   affordance's "can do" is the first attempt to separate the two guarantees of R5. The issue is
   how far it reduces $p_{\mathrm{aff}}$ in (3).
   Additional questions: ⓐ How does the whole structure fail when the affordance value function is
   wrong — does the paper report that case? ⓑ Does it decompose failures by cause (precondition,
   affordance, execution), and if not, can you form the prescription in (2)?
2. **Liang et al., "Code as policies: language model programs for embodied control" (2023,
   ICRA)** — role: `standard`. <https://arxiv.org/abs/2209.07753> — §3 and §5.
   Why read it: generating the plan as **code** makes control flow and perception-API calls
   explicit, which moves part of symbolic validity into **program verification**.
   Additional questions: ⓐ Which errors in the generated code are caught before execution and
   which are not — is that boundary the same as the verifier boundary in (2)? ⓑ Does the handling
   of perception-API failure correspond to the recovery structure in (3)?

**The ten fixed questions**: (1) What problem, under what assumptions? (2) What exactly could prior
work not do? (3) The core idea in one equation. (4) What is guaranteed theoretically, and **what is
not**? (5) The independent and dependent variables and the baselines — were they tuned fairly?
(6) Do the metrics match the claim, and are variances and seeds reported? (7) What information
needed for reproduction is missing? (8) If it is wrong, which assumption would you suspect first?
(9) Compute and memory complexity, and real-time behaviour. (10) What would you change to surpass
it in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: **under 1 minute** on a laptop CPU, under 100 MB
of memory, numpy only. **No GPU or LLM API is required** — planner hallucination is simulated with
probability $p$. Extending to a real LLM planner is the **optional extension (R4)** below.

**Environment.** Rooms $0,\dots,5$ are connected in a ring and the symbolic actions are
$\texttt{move}(i,i{+}1)$, $\texttt{pick}$, $\texttt{place}$. The goal is to go from room $0$ to
room $3$, pick, and place. With probability $p_{\mathrm{hal}}$ the planner inserts a
**non-adjacent** move (a precondition violation). At each execution step an affordance failure
occurs with probability $p_{\mathrm{aff}}$ and an execution failure with probability
$p_{\mathrm{exec}}$. The failure cause is classified by **whichever happened first**.

**Acceptance criteria** — all four conditions must hold to pass.

1. **The verifier's effect**: with $p_{\mathrm{aff}}=0.04$, $p_{\mathrm{exec}}=0.02$,
   $p_{\mathrm{hal}}=0.15$ over 20,000 trials, ⓐ success without a verifier is $45\% \pm 2\%$
   (measured $45.17\%$), ⓑ turning on the symbolic verifier gives $74\% \pm 2\%$ (measured
   $73.68\%$), and ⓒ precondition failures go from $37\% \pm 2\%$ to **exactly** $0.00\%$ (because
   the verifier re-plans).
2. **The irrelevance of planner quality**: with the verifier on, the success difference between a
   hallucinating planner ($p_{\mathrm{hal}}=0.15$) and a perfect one ($p_{\mathrm{hal}}=0$) is
   **under $1$ percentage point** (measured $73.68\%$ vs $73.92\%$, a gap of $0.24$pp). Report it
   together with the standard error over 20,000 trials ($\approx0.3$pp).
3. **The exponential law (3)**: with $p_{\mathrm{aff}}=0.05$, $p_{\mathrm{exec}}=0$,
   $T \in \{2,5,10,20,40\}$ over 20,000 trials, the measured success divided by $(1-p)^T$ lies in
   **$[0.98,\,1.02]$ for every $T$** (measured $0.997$, $0.997$, $0.994$, $1.007$, $1.001$). Also
   compute $T_{1/2} = 13.51$ and confirm success crosses $0.5$ between $T=10$ and $T=20$.
4. **The optimal granularity (4)**: with $a=0.25$, $e=0.01$, $c=4$, ⓐ compute the closed form
   $g^\star = 1.7678$; ⓑ confirm that the numerical optimum over the grid
   $\{0.5,1,1.5,1.77,2,3,4,8,16\}$ is a **grid point adjacent to** $g^\star$ (measured optimum
   $g=2$, $S=0.31706$; $g=1.77$ gives $0.31688$ — a $0.06\%$ difference); ⓒ confirm that lowering
   $e$ from $0.01$ to $0.0025$ **doubles** $g^\star$ ($0.25/\sqrt{0.005} = 3.536$).

**Baselines to compare against**: ⓐ no verifier — the reference point for condition 1.
ⓑ A perfect planner — the ceiling for condition 2 (the most that can be gained on the planner
side). ⓒ A hypothetical **perfect abstraction** with $p_{\mathrm{aff}}=0$ — a sanity check that the
remaining failures are all execution noise. ⓓ Optional: allow one retry on failure and measure
whether the base in (3) changes from $1-p$ to $1-p^2$ (problem P1).

**Optional extension (R4, may require an LLM API — not required)**: have a real LLM generate plans
for the same ring-of-rooms task and compare the failure distribution with and without the symbolic
verifier. **No acceptance criterion is set** — hallucination rates vary greatly with the model and
the prompt. The point is to check whether the conclusion of condition 2 (planner quality is nearly
meaningless behind a verifier) shows up **qualitatively** with a real LLM.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| Precondition failures in condition 1ⓒ are not zero | The verifier counted a failure instead of re-planning | Print the distribution of re-plan counts — all zeros means there is no re-planning |
| The two success rates in condition 1 are equal | The verified and unverified failure paths fell into the same branch | Print the return values of the verification branch and the execution branch separately |
| The gap in condition 2 exceeds $5$pp | The re-plan cap is too low, so the hallucinating planner cannot find a valid plan | Print the cap and the failure rate — a cap of 20 is enough |
| The ratio in condition 3 exceeds $1.05$ | $p_{\mathrm{exec}}$ was not separated out to zero | Print both probabilities — condition 3 has $p_{\mathrm{exec}}=0$ |
| The affordance share **fell** with the verifier | Causes were not recorded mutually exclusively, so they were double-counted | Check that the four categories sum exactly to the number of trials |
| The optimum in condition 4ⓑ is at a grid boundary | $e$ was set to zero, making $S$ monotone increasing in $g$ | Check that $e > 0$ — with $e=0$ there is no interior optimum |

## Open problems

- **(Open) Constructing downward-refinable abstractions automatically** — R1 shows that
  hand-designed predicates do not satisfy (1). No method is known for **learning** an abstraction
  from data that captures geometric feasibility while keeping the search space small. Current
  approaches: binding symbols and geometry into a single optimization
  ([Toussaint 2015](https://www.ijcai.org/Proceedings/15/Papers/248.pdf)), sampling-based TAMP
  ([Garrett et al. 2021](https://arxiv.org/abs/2010.01083)). The empty slot: a learned abstraction
  with a refinability guarantee.
- **(Open) Attaching a guarantee to affordance estimates** — the only way to reduce
  $p_{\mathrm{aff}}$ in (3) is to decide geometric feasibility, and SayCan-style systems approximate
  that with a learned value function. Without a guarantee on that estimate's error rate, you do not
  even know what $p_{\mathrm{aff}}$ is. The conformal-prediction route to a guarantee is covered in
  `s4-safety-ood`. Current approaches: [SayCan](https://arxiv.org/abs/2204.01691), coupling a
  geometric checker (TAMP). The empty slot: a calibrated affordance estimator.
- **(Open) The absence of a reporting standard for failure causes** — the prescription in (2)
  ("invest in the verifier and the geometric checker, not the planner") can only be formed if
  failures are decomposed by cause. Yet published reports usually give a single total success rate,
  so cross-paper comparison cannot tell you where to invest. Current approaches: the error-type
  discussion in [Code as Policies](https://arxiv.org/abs/2209.07753), evaluation methodology
  (`s4-evaluation-science`). The empty slot: a reporting convention that requires decomposition by
  cause.
- **(Open) How far recovery breaks the exponential law** — problem P1 shows that one recovery
  changes the base to $1-p^2$, but real re-planning changes the state and the possibility of
  recovery itself depends on the state. There is no model that predicts the success rate of a system
  with a re-planning loop from its plan length. The empty slot: a success model that includes
  recovery.

## Concept check

Take it with `rc quiz s4-language-and-planning`. This quiz is **for concept checking only**; the
real work is the problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

## How to study this stage

1. **Write the abstraction down formally (45 min)** — define $\alpha$, $\mathrm{pre}$,
   $\mathrm{eff}$ and write downward refinability (1) from a blank page. Then build the narrow-door
   construction that breaks (1) yourself. The one sentence "predicates encode only necessary
   conditions" is the axis of this lesson.
2. **Count the three failures separately (60 min)** — run condition 1 of the reproduction task and
   watch the verifier remove only precondition failures. Then use condition 2 to confirm that
   **planner quality moves the result by only 0.24pp**. After seeing that number you will hear the
   prescription "a better LLM" differently.
3. **Convert the exponential law into numbers (40 min)** — derive (3) and compute $T_{1/2}$
   (13.5 steps at $p=0.05$). Confirm with condition 3 that the ratio is $1.00$, then use problem P1
   to derive how recovery changes the base to $1-p^2$ — why re-planning matters structurally becomes
   visible on the spot.
4. **Derive the optimal granularity (60 min)** — obtain (4) from the second-order expansion of
   $\log S$ and confirm that $c$ cancels. Run condition 4 to see whether the grid optimum is
   adjacent to $g^\star$ and whether cutting $e$ by four doubles $g^\star$. Doing problem P7's
   $\beta$ generalization exposes the model dependence.
5. **Read the two papers along the axis of guarantees (105 min)** — SayCan (affordance as a value
   function) → Code as Policies (verification moved toward the program side). Write the one-page
   note per paper **without exception**. In each note, add one line: "does this paper reduce
   $p_{\mathrm{pre}}$ or $p_{\mathrm{aff}}$?"
6. **Finish with what cannot be done (60 min)** — pick the missing reporting standard for failure
   causes from "Open problems" and write a paragraph on what the format should be if the four
   categories of the reproduction task were required of published papers.

**Passing bar**: you can construct a counterexample to (1) and derive (3) from a blank page; you can
distinguish the failures a verifier removes from the ones it leaves; you can derive (4) and say why
$c$ cancels; and you have code passing the four conditions of the reproduction task plus one-page
notes on both papers.
