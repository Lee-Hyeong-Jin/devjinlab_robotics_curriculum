---
title: Capstone 2 - Reproduction
summary: >-
  Reproduce one paper chosen from your survey at tier R3. The bar is to reproduce the reported key
  numbers within a stated tolerance, or to establish the cause of the reproduction failure with
  evidence. The deliverables are a reproduction report and a repository.
objectives:
  - Choose the target paper and the one or two claims to reproduce, with the reasons recorded.
  - Extract the information needed to rebuild the experiment and state the missing parts as assumptions.
  - Define the tolerance in advance and judge success or failure against it.
  - On failure, decompose the cause into implementation error, assumption difference or reporting gap, with evidence.
  - Produce a reproduction repository and report a third party can re-run.
---

# Capstone 2 - Reproduction

## Goals

Reproduction is **the most honest test of research ability**. There is a wide gap between believing
you understood a paper and actually rebuilding its result, and learning from that gap is the point
of this lesson: what the paper **did not say**, which choices the authors left **implicit**, and
where your own implementation is wrong.

**Important**: the bar here is not "a successful reproduction". It is one of two things:
(a) reproduce the reported key numbers **within a tolerance stated in advance**, or (b) **establish
the cause of the failure with evidence**. (b) is not the easier path — "it did not work" is not a
report, and you must **sort the cause by evidence** into implementation error, assumption
difference or reporting gap. Establishing a failure's cause is itself a contribution to the field.

The tier is R3 (the "Reproduction tasks" section of lesson `f0-how-to-read-this-track`): reproduce one or two main results **at reduced scale** and
compare both the trend and the numbers.

Deliverables: **a reproduction report and a reproduction repository**.

## Self-diagnosis before you start

| Question | If you can | If you cannot |
|---|---|---|
| Have you built the reproducible repository from `r1-reproducibility-artifacts`? | Start at step 1 | Finish that lesson — its tools and habits are assumed |
| Have you identified two or three reproduction candidates in your survey? | Move fast through step 1 | Look for rows with "code released + reducible" in the survey table |
| Can you do statistical comparison (intervals, trial counts)? | Move fast through step 4 | Review `r1-robotics-evaluation-statistics` |
| Do you have the compute (GPU, robot) secured? | Proceed | Pick a target that fits your resources in step 1 — that is the first selection criterion |

## Procedure

**Step 1 — choose the target and the claims (3 h).** Selection criteria, in priority order:
(a) **reducibility** — does the main claim hold in a small setting? (b) **resource fit** — can a
reduced run fit in 10% of what you have? (c) **importance** — does the claim touch an empty cell in
your survey? (d) whether code is released (if it is, the task becomes **result reproduction** rather
than implementation reproduction — both are valuable). Then write the **one or two claims as
sentences** ("Table 3 in §5.2: method A has a 15-point higher success rate than baseline B"). You
reproduce **a claim**, not a whole paper.

**Step 2 — rebuild the experiment as a specification (8 h).** Read the paper and build the
specification: data (source, version, splits), model and algorithm (every hyper-parameter),
training and tuning budget, evaluation procedure (metric definitions, trial counts, seeds),
hardware. **It is normal for more than half of these to be missing.** For each gap, (a) **state a
reasonable default as an assumption** and (b) mark whether it could change the result. This
"assumption list" becomes the key tool for failure analysis later. Draw your questions for the
authors from it too.

**Step 3 — fix the tolerance in advance (2 h).** Write it **before running**. For example: "the
success-rate gap falls within ±5 points of the reported 15, and the 95% intervals overlap"; "the
median ATE is within ±20% of the reported value"; "the ranking (A > B) is preserved". Different
metrics need different criteria. **A tolerance set afterwards is not a judgment but a
rationalisation** — this is pre-registration applied to reproduction.

**Step 4 — run the reduced reproduction (40 h).** Keep the order: (a) **pin the environment** first
(lockfile, container); (b) get **the whole pipeline through once** in the smallest setting,
regardless of result quality; (c) cross-validate your metric code against a public tool; (d) then
scale up; (e) run several seeds to get a distribution (a reproduction comparison without intervals
is impossible). **Keep every run log, config and intermediate output.** The cause of a discrepancy
can only be found in the logs.

**Step 5 — decompose the discrepancy (15 h).** If your value differs from the reported one, sort the
cause into three categories.
*Implementation error (your side)*: units, frame conventions (is angular velocity first?),
normalisation, the alignment method in the evaluation script. **Check** against the paper's
intermediate values (loss curves, parameter counts, inference time).
*Assumption difference*: pick candidates from step 2's assumption list and **change them one at a
time** to measure sensitivity. This is the most productive part of reproduction work — it reveals
which choices the result is sensitive to.
*Reporting gap or error (authors' side)*: write this conclusion only after excluding the first two.
The evidence is a **sensitivity analysis** ("no combination of assumptions reaches the reported
value; here is the range searched").
**The order matters.** A failure report that did not first suspect its own implementation is not trusted.

**Step 6 — write the report (10 h).** Structure: the target and the claims → the specification and
the **assumption list** → the pre-set tolerance → results (reported vs reproduced, with intervals)
→ discrepancy decomposition and sensitivity analysis → the judgment against the tolerance → a fair
assessment of the original paper → a reproduction guide (a list of traps for the next person).
**Tone**: do not blame the authors. Reproduction failure is common, and the purpose of the report is
**to correct the record**.

**Step 7 — repository and DOI (3 h).** Apply `r1-reproducibility-artifacts`'s criteria as they are:
lockfile, container, seed function, smoke path (10 min), table and figure scripts, LICENSE. If you
modified the original code, **isolate the changes as patches** so what you changed is visible.

## Grading criteria

| Item | Pass | Strong |
|---|---|---|
| Target choice | The claims are stated as sentences | The reasons (reducibility, resources, link to the survey) are recorded |
| Specification | The main settings are organised | Every gap is **stated as an assumption** with its potential impact marked |
| Tolerance | A criterion exists | Defined per metric **before running**, proven by the commit timestamp |
| Execution | The reduced reproduction is complete | Multi-seed distributions + cross-validated metric code + all logs kept |
| Decomposition | The discrepancy is described | Decomposed into implementation/assumption/reporting with sensitivity evidence |
| Report | Results and a judgment | Includes a reproduction guide (trap list) and a fair assessment; repository DOI published |

## Failure cases

- **Trying to reproduce the whole paper.** The scope explodes. Narrow to one or two claims.
- **Setting the tolerance afterwards.** Then any result counts as "reproduced".
- **Declaring "not reproducible" without suspecting your own code.** Most cases are units, conventions or normalisation.
- **Comparing with a single seed.** Without the variance the discrepancy has no meaning.
- **Keeping no logs.** The cause cannot be found after the fact.
- **Running the released code and calling it reproduction.** Result reproduction is valuable, but state
  **what you verified** (environment difference? data? metric code?).
- **Writing the report as blame.** Reproduction failure is ordinary; the tone decides whether the report is trusted.
- **Not publishing a failure.** That is a loss to the whole field; a negative result is a contribution.

## Case study

**Two required papers plus a close reading of the target.**

**Pineau et al. (2021)** — `standard`. Questions: (a) Apply the reproducibility checklist to **your
target paper** and count how many items it meets. (b) How do the unmet items map onto your
assumption list? (c) What definition of "reproducibility" does the report measure, and how does it
differ from your tolerance criterion?

**Agarwal et al. (2021)** — `critique`. Questions: (a) Does your target paper report point
estimates only? (b) Do its conclusions survive a stratified bootstrap or performance profiles?
(c) Report your own reproduction results in the format this paper recommends.

**Close reading of the target**: read it sentence by sentence and build a two-column table of
**information needed to implement** and **information missing** (8 h). That table is step 2's output.

## Deliverables

**Deliverable 1 — reproduction report** (6-10 pages): structured as in step 6. The key table is
reported vs reproduced values with trial counts and 95% intervals, plus the tolerance judgment.
**Acceptance**: (a) the commit history proves the tolerance was set in advance, (b) the discrepancy
is decomposed into implementation/assumption/reporting, (c) a sensitivity analysis covers at least
two assumptions, (d) five or more traps are listed for the next reproducer.

**Deliverable 2 — reproduction repository**: lockfile, container, seed function, smoke path (10 min),
table and figure scripts, LICENSE, README. Modifications to the original code isolated as patches,
and all run logs and configs retained. **Acceptance**: a third party succeeds at the smoke path
within 10 minutes from the README alone.

**Deliverable 3 — assumption and sensitivity table**: the full list of gaps and assumptions from
step 2, with the measured sensitivity of each (a number if measured, "not measured" otherwise).
**Acceptance**: at least two of the assumptions marked as able to change the result were actually measured.

**Final acceptance**: pass or better on all six grading items, and **the judgment is unambiguous** —
either reproduced within tolerance, or the failure's cause established with evidence (the
sensitivity analysis). "We do not know which" is not a pass.

## Open problems

- **(Open) The criterion for judging reproduction** — there is no agreement on who should set the
  tolerance and how. Authors set it loosely; reproducers can set it arbitrarily.
- **(Open) Equivalence in real-robot reproduction** — the conditions under which reproduction on a
  different robot or environment counts as "the same experiment" are unsettled (the same item as in
  `r1-reproducibility-artifacts`).
- **(Open) Rewarding reproduction labour** — reproduction work takes a lot of time and has little
  venue space. A sustainable reproduction ecosystem (dedicated tracks, artifact badges, citation
  norms) has not taken hold in robotics.

## Concept check

Take it with `rc quiz r2-capstone-reproduction`. It is a concept check only.

## How to study this stage

1. **Pick a target that fits your resources (3 h)** — reducibility is the first criterion. A result
   whose training takes two weeks is not a capstone target.
2. **Build the specification and assumption list first (8 h)** — before writing code. Half of it
   being missing is normal, and that list becomes your analysis tool.
3. **Write and commit the tolerance (2 h)** — before running. What matters is leaving a timestamp.
4. **Get the pipeline through once in the smallest setting (10 h)** — quality irrelevant. A path that
   runs end to end makes all later debugging easier.
5. **Cross-check the metric code against a public tool (3 h)** — this uncovers many mismatches. If the
   metric is wrong, every comparison is meaningless.
6. **Change assumptions one at a time and watch the sensitivity (15 h)** — the step you learn most
   from. Which choices the result is sensitive to *is* the field's hidden knowledge.
7. **Write the trap list for the next reproducer (2 h)** — every place you got stuck. It becomes the
   most-read part of the report.

**Bar to pass**: pass or better on all six grading items, an unambiguous judgment (reproduced within
tolerance, or a failure cause established with evidence), and a third party succeeding at the
repository's smoke path within 10 minutes.
