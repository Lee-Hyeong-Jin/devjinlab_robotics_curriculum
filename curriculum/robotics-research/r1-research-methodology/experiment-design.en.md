---
id: r1-experiment-design
lang: en
title: Experiment design
summary: >-
  Design the experiments that test your hypotheses: separate independent, dependent and confounding
  variables, design ablations, and set the rule for tuning baselines fairly. The deliverables are an
  experiment plan and an ablation table.
objectives:
  - Distinguish independent, dependent and confounding variables and control the confounders.
  - Design, for each hypothesis, an experiment capable of refuting it.
  - Design ablations that isolate the contribution of each component.
  - Set and apply a rule for fairly tuning baselines (equal budget).
  - Pre-register the metrics, number of trials and success criteria before running anything.
tags: [research-methodology, experiment-design, ablation, research]
---

# Experiment design

## What you will be able to do

In the previous lesson you wrote falsifiable hypotheses. This lesson designs **experiments actually
capable of refuting them**.

**Why its own lesson**: the most common defect in robotics papers is experiment design — baselines
left untuned, whole systems compared without ablations, confounders uncontrolled. The result is that
"our method is better" says nothing about **what** makes it better.

Deliverables: **an experiment plan, an ablation table and a pre-registration document** — written
**before** running anything.

## Procedure

**Step 1 — separate the variables into three kinds (1 hour).**
- **Independent**: what you change (method, hyper-parameters, environment difficulty).
- **Dependent**: what you measure (success rate, ATE, computation time). It must be the metric the
  hypothesis named.
- **Confounding**: what affects the result but is not of interest (random seed, hardware, initial
  pose, lighting, battery level). **Robotics has many confounders and controlling them is hard** —
  which is why they must be written down explicitly.

**Step 2 — control the confounders (1 hour).** Three ways: (a) **fix** them (the same initial
pose); (b) **randomise** them (many random seeds); (c) **measure and report** them (record the
lighting if it cannot be fixed). A confounder that can be neither fixed nor randomised is **stated
as a limitation**.

**Step 3 — one refuting experiment per hypothesis (2 hours).** Pair each hypothesis with one
experiment and re-confirm **which outcome would make the hypothesis false**. If hypotheses and
experiments do not pair one to one, the design is incomplete.

**Step 4 — design the ablations (2 hours).** If the method consists of components $A, B, C$,
compare full / $-A$ / $-B$ / $-C$. Rules:
- **Remove only one at a time** (removing two mixes interaction with individual effects).
- If an interaction is suspected, add $-A{-}B$ as well.
- An ablation is a **tool for isolating contributions**. Showing only "the full system is better"
  leaves you ignorant of which component did the work.

**Step 5 — write the baseline fairness rule (1 hour).** The most common dishonesty lives here. Use
an **equal budget** rule:
- the same number of hyper-parameter search trials (e.g. 30 random searches per method);
- the same training budget (steps, time, samples);
- start from the baseline's **official implementation and official hyper-parameters**, and state
  the reason for any change;
- if only your method was adapted to the environment, **report that**.

**Step 6 — pre-register (1 hour).** Before running, fix the metrics, trial counts, success criteria
and analysis methods in a document. That prevents choosing the metric after seeing the results (the
robotics version of p-hacking).

## Rubric

| Item | Pass | Strong |
|---|---|---|
| Variable separation | all three kinds are listed | a control method (fix, randomise, report) is assigned per confounder |
| Hypothesis-experiment pairing | every hypothesis has an experiment | each experiment's **refutation condition** is written numerically |
| Ablation | conditions removing one component at a time exist | two-component removals are added for suspected interactions, with reasons |
| Baseline fairness | the official implementation is used and budgets are matched | search counts, training budgets and modifications are **published** in a table |
| Pre-registration | metrics and trial counts were written in advance | the analysis method (tests, confidence intervals) is also fixed in advance, with post-hoc changes logged |
| Feasibility | the compute and time budget is stated | there is a priority order for **what to cut first** if the budget is exceeded |

## Failure modes

- **Not tuning the baseline.** Searching dozens of times for your own method while running the
  baseline at defaults makes the comparison meaningless. **The most common and most damaging defect.**
- **Comparing wholes without ablations.** You learn that "our system is better" but not **why**.
  It is the first thing a reviewer asks.
- **Removing two components at once.** Individual effects and interactions mix and cannot be interpreted.
- **Not recording confounders.** In real-robot experiments lighting, battery and wear change the
  result; unrecorded, the work is irreproducible and the difference gets mistaken for the method's effect.
- **Choosing the metric after seeing results.** Switching to "path length" when success rate looks
  bad. Pre-registration prevents it.
- **Comparing with one trial.** Robotics has high variance; a single-run comparison is not
  evidence — the next lesson treats trial counts.
- **Using simulation results as a real-world claim.** Writing "it will also work on hardware"
  without evaluating the sim-to-real gap gets rejected.

## Case study

**One must-read plus two audits.**

1. **Agarwal et al., "Deep reinforcement learning at the edge of the statistical precipice" (2021)**
   — `critique`, §3-5. Questions: (a) write the three **defects of existing experiment design** the
   authors identify. (b) what do their alternatives (performance profiles, stratified bootstrap)
   solve? (c) find a paper in your field with the same defect and write where the problem is.

2. **Audit task**: pick **two experiment-heavy papers** from the previous lesson's table and score them.
   | Check | Paper 1 | Paper 2 |
   |---|---|---|
   | Is the baseline's hyper-parameter search budget stated? | | |
   | Are there ablations, removing one component at a time? | | |
   | Are the number of trials and the seeds reported? | | |
   | Are confidence intervals or variances reported? | | |
   | Are confounders stated? | | |
   | Are failure cases reported? | | |
   **Most papers satisfy three or fewer of the six.** That fact is itself the motivation for this lesson.

## Deliverable

**Deliverable 1 — an experiment plan** (at most three pages)
- A list of the three kinds of variable, with a control method per confounder.
- A hypothesis-experiment table (hypothesis / experiment / metric / **refutation condition** /
  number of trials / expected cost).
- The compute and time budget, and the priority of what to cut if exceeded.

**Deliverable 2 — an ablation table design**
- Rows are conditions (full, $-A$, $-B$, $-C$, and two-component removals if needed); columns are
  metrics.
- State **which hypothesis each condition tests**. The numbers may still be empty — the **design**
  is the deliverable.

**Deliverable 3 — a pre-registration document** (one page)
- Metrics (one primary plus secondaries), trial counts, success criteria, analysis method (tests,
  confidence intervals) and the baseline budget rule.
- Date it and commit it **before** the experiments (into the repository, so changes leave a history).

**Acceptance criteria**: all six rubric items at "pass" or above, and **one peer can reproduce the
experiments from the plan alone** (no ambiguity about what is run how many times against what).

## Open problems

- **(Open) Controlling confounders in real-robot experiments** — simulation is controlled by seeds,
  but on hardware wear, lighting and temperature drift over time. Robotics has no standard
  procedure for **systematically controlling or correcting** those confounders.
- **(Open) Defining an equal budget** — matching "fair tuning" by search count is conventional, but
  methods differ in their number and sensitivity of hyper-parameters, so whether it is **truly
  fair** is unclear. How to define the budget to be fair is open.
- **(Open) The effectiveness of pre-registration** — pre-registration, used in psychology and
  medicine, is barely adopted in robotics. Whether it **impedes innovation** in a field full of
  exploratory work has not been tested.

## Concept check

Run `rc quiz r1-experiment-design` (add `--lang en` for the English text). It is for concept
checking only; the real work is the deliverable.

The four items cover: which kind of variable a random seed is; whether removing two components at
once is efficient; what the equal-budget rule does not include; and what pre-registration prevents.

## How to study this stage

1. **Write the confounder list first (1 hour)** — seed, initial pose, lighting, wear, temperature,
   battery, network latency. Recognising how long that list is in robotics is the starting point.
2. **Match hypotheses to experiments one to one (2 hours)** — an unmatched pair means the design is
   incomplete. Claiming one experiment tests two hypotheses usually tests neither.
3. **Design the ablations before implementing (2 hours)** — drawing the table first changes the
   implementation design, because it reveals what must be separable. Bolting ablations on after
   implementation often proves impossible.
4. **Write the baseline budget as numbers (1 hour)** — not "tuned fairly" but "30 random searches
   per method, 1e6 training steps". Without numbers the fairness claim cannot be checked.
5. **Score two papers on the six checks (110 min)** — the audit table of the case study. Seeing for
   yourself that most satisfy three or fewer raises your own standard.
6. **Commit the pre-registration (1 hour)** — put it in the repository before the experiments. If
   you later change the metric, the history records it. That is a device of honesty towards yourself.

**Passing bar**: the experiment plan, ablation table and pre-registration document at "pass" or
above on all six rubric items, and one peer able to reproduce the experiments from the plan alone.
