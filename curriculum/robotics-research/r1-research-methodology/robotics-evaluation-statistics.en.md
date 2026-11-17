---
title: Evaluation and Statistics in Robotics
summary: >-
  Judge whether a metric matches the claim, fix the number of trials by a power analysis, and
  handle confidence intervals and multiple comparisons. The deliverable is an evaluation protocol
  plus a power analysis.
objectives:
  - Judge whether a metric is consistent with the claim and name the metric's failure modes.
  - Compute and report bootstrap confidence intervals.
  - Compute the required number of trials with a power analysis.
  - Identify when a multiple-comparison correction is needed and apply it.
  - Separate the claims you can make from the claims you cannot under real-robot trial budgets.
---

# Evaluation and Statistics in Robotics

## Goals

Once the experiment is designed, you have to **interpret the result**. This lesson trains three
things: (1) does the metric match the claim, (2) how many trials are needed, (3) how do you know
whether a difference is chance.

**Why robotics needs its own lesson on this**: real-robot trials are expensive (minutes each,
hardware wear). So papers that "claim a 10-point gap from 5 trials" are common — and that gap is
**undetectable**. Without statistics you over-read your own result; with it you learn **what you
cannot claim**.

Deliverable: **an evaluation protocol, a power analysis, and bootstrap confidence-interval code**.

## Procedure

**Step 1 — check that the metric matches the claim (1 h).** For each metric write down **what it
hides**: success rate hides the *kind* of failure (near-miss vs destructive); ATE depends on the
alignment (Umeyama) and mixes long-horizon drift with short-scale jitter, so it must be read
together with RPE; mean return hides the tail, so report median and quartiles too; compute time
depends on hardware and implementation quality, so report it with complexity. **Pick one primary
metric and use secondary metrics to expose what it hides.**

**Step 2 — fix the trial count by a power analysis (2 h).** "How many runs?" is a computation, not
a guess. To separate success rates $p_1, p_2$ at level $\alpha$ with power $1-\beta$,

$$
n \approx \frac{\big(z_{1-\alpha/2}\sqrt{2\bar{p}(1-\bar{p})} + z_{1-\beta}\sqrt{p_1(1-p_1)+p_2(1-p_2)}\big)^2}{(p_1-p_2)^2}
$$

($\bar{p}$ is the mean of the two rates). Example: $p_1=0.6$, $p_2=0.7$, $\alpha=0.05$, power 0.8
gives **about 350 trials per condition**. On real hardware 350 is usually impossible, so you then
**claim only larger effects** or back the claim with simulation.

**Step 3 — confidence intervals by bootstrap (2 h).** Safest when you do not know the
distribution: resample with replacement $B=10^4$ times, build the statistic's distribution, take
the 2.5/97.5 percentiles. **Never report the mean alone** — a comparison without an interval is not
evidence.

**Step 4 — correct for multiple comparisons (1 h).** With $k$ conditions there are $k(k-1)/2$
pairs. At $\alpha=0.05$, 20 comparisons produce **about one significant result by chance**.
Bonferroni ($\alpha/m$) is conservative; Holm or Benjamini–Hochberg (FDR) is practical. **If you
compared every pair in an ablation table, you need a correction.**

**Step 5 — state the real-robot constraint (1 h).** With few trials: (a) claim only large effects,
(b) always report intervals, (c) never write "not significant" as "no difference" — it may be lack
of power. **"Not significant at $n=5$" carries almost no information.**

**Step 6 — document the protocol (2 h).** Freeze the metric definitions (with the computing code),
the trial count and its justification, the analysis method, and the reporting format (mean ±
interval, or performance profiles).

## Grading criteria

| Item | Pass | Strong |
|---|---|---|
| Metric consistency | Primary metric equals the hypothesis's metric | **What each metric hides** is written down and exposed by secondary metrics |
| Metric definition | Definition is unambiguous | Computing code is provided and matches a public tool to within $10^{-6}$ |
| Trial count | The count is stated | The count is **computed** by a power analysis; if infeasible, that fact and the alternative are stated |
| Uncertainty | Variance or an interval is reported | Bootstrap intervals and per-seed results are both published |
| Multiple comparisons | The number of comparisons is recognised | The correction is named and applied, with before/after shown |
| Negative results | "Not significant" is not written as "no difference" | Power and the minimum detectable effect size are reported too |

## Failure cases

- **Comparing from 1–5 trials.** Given robotics variance, even a 10-point gap is undetectable.
- **Reporting means only.** A mean without an interval is not grounds for comparison — Agarwal et
  al. (2021)'s central point.
- **Writing "not significant" as "no difference."** With low power, large effects also come out
  non-significant.
- **Ignoring multiple comparisons.** Comparing all 20 pairs of an ablation table and reporting the
  best one is post-hoc selection.
- **Looking at one metric only.** ATE alone cannot separate drift from jitter; read RPE with it.
- **Overfitting the benchmark.** Repeated tuning against the same test set only improves that set —
  the KITTI discussion.
- **Using simulation variance as real-robot variance.** Real variance is usually several times larger.

## Case study

**Read the two required papers plus two benchmarks.**

1. **Agarwal et al. (2021)** — `critique`. Questions: (a) Why do the authors treat
   point-estimate-only reporting as a problem? (b) What do performance profiles and stratified
   bootstrap each reveal? (c) Evaluate your own field's standard reporting against this bar.
2. **Zhang & Scaramuzza, "A tutorial on quantitative trajectory evaluation for visual(-inertial)
   odometry" (2018)** — `standard`. Questions: (a) What is ATE sensitive to, and RPE?
   (b) How much does the alignment method change the result? (c) What reporting do the authors
   recommend?

**Benchmark reading**: read the evaluation procedure and task definitions of
[TUM RGB-D](https://cvg.cit.tum.de/data/datasets/rgbd-dataset) and
[KITTI](https://www.cvlibs.net/datasets/kitti/), and tabulate **which failures each metric exposes
and which it hides**. TUM only ships an evaluation tool, so take the definitions of ATE and RPE
themselves from Zhang & Scaramuzza (2018).

## Deliverables

**Deliverable 1 — evaluation protocol** (2 pages): one primary and 2–3 secondary metrics with
definitions and **what each hides**; the metric code (or a named public tool) and how it is
validated; the reporting format (mean ± 95% bootstrap interval, whether per-seed raw data is published).

**Deliverable 2 — power analysis** (1 page + code): per hypothesis, the expected effect size,
$\alpha$, power and the **computed** trial count. If that count is infeasible on hardware,
(a) invert for the minimum detectable effect size and (b) state the alternative (simulation
support, or a reduced claim).

**Deliverable 3 — bootstrap interval code**: 95% intervals for both a success rate and a continuous
metric. **Acceptance**: (a) coverage of $95\% \pm 2\%$ on synthetic data (checked over $10^3$
repetitions), (b) agreement with `scipy.stats.bootstrap` to within $10^{-2}$, (c) includes a
multiple-comparison correction (Holm or BH).

**Acceptance**: pass or better on all six grading items, and **the power analysis actually changes
your experiment plan** (more trials, or a smaller claim) — if nothing changed, the computation was
a formality.

## Open problems

- **(Open) Trial budgets in real-robot evaluation** — the gap between the trials statistics demands
  and the trials hardware allows is large. There is no settled methodology for the **range of valid
  claims** under few trials (the same item appears in `s4-evaluation-science`).
- **(Open) Consistency evaluation without ground truth** — metrics like NEES require ground truth.
  Assessing estimate quality **without it** on real hardware is limited (same open problem as in
  `r0-estimation-theory`).
- **(Open) Measuring benchmark overfitting** — repeated use of a public benchmark accumulates
  overfitting, and robotics has almost no way to measure its magnitude. Holdout management and new
  test-set generation are not systematised.

## Concept check

Take it with `rc quiz r1-robotics-evaluation-statistics`. It is a concept check only.

## How to study this stage

1. **Write "what it hides" for each metric (1 h)** — success rate, ATE, mean return, compute time.
   That table settles both the primary-metric choice and the secondary-metric design.
2. **Apply the power computation to your own experiment (2 h)** — put your own expected effect size
   in the formula. **If the result does not change your plan, you did it as a formality.**
3. **Implement the bootstrap yourself (2 h)** — ten lines. Then check 95% coverage on synthetic data
   (Deliverable 3's acceptance). Get the principle in hand before reaching for a library.
4. **Apply a multiple-comparison correction to your own ablation table (1 h)** — count the
   comparisons and compare before/after. Experiencing significance disappear after correction matters.
5. **Read the benchmarks' evaluation procedures (110 min)** — TUM and KITTI. Seeing that a metric is
   **designed for that benchmark's purpose** shows why borrowing someone else's metric is risky.
6. **Make a list of "claims I cannot make" (30 min)** — the differences undetectable at your trial
   count. That list becomes your paper's limitations section (next lesson).

**Bar to pass**: the evaluation protocol, power analysis and bootstrap code (with coverage checked)
reach pass or better on all six grading items, and the power analysis actually changed the
experiment plan.
