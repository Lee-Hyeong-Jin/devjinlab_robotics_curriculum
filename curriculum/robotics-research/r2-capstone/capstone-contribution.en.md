---
title: Capstone 3 - Contribution
summary: >-
  Build one small contribution on the evidence of the survey's empty cells and the reproduction's
  sensitivities, and finish with an eight-page workshop-format draft and a 20-minute oral defence.
  The bar is one clear contribution, fair baselines, an ablation, stated limitations and
  reproducible code.
objectives:
  - Set one narrow, verifiable contribution grounded in the survey and the reproduction.
  - Design and run fair baselines (equal budget) and an ablation that decomposes the contribution.
  - Report results with confidence intervals and match the scope of the claim to the evidence.
  - Complete an eight-page workshop-format draft with reproducible code.
  - Defend the work in a 20-minute talk and answer challenges with evidence.
---

# Capstone 3 - Contribution

## Goals

This is the track's final lesson. What the previous two gave you is **one well-grounded question**:
the empty cell in your survey's comparison table, and the sensitivity the reproduction exposed
(which choices the result depends on). This lesson produces **one small but verified answer** to it.

**"Small" matters.** The most common failure of early doctoral work is an oversized scope. A
workshop paper's contribution is not "we opened a new field" but "we show that Y holds (or fails)
under condition X". The narrower the scope, the easier it is to have the evidence — and a small
claim with evidence is **better research** than a large claim without it.

Deliverables: **an eight-page workshop-format draft, a reproduction repository, and a 20-minute
oral defence**.

## Self-diagnosis before you start

| Question | If you can | If you cannot |
|---|---|---|
| Can you name three empty cells in your survey's table? | Start at step 1 | Go back to the survey and re-read the empty-cell pattern |
| Did you measure two sensitive assumptions in the reproduction? | Move fast through step 1 | Finish the reproduction lesson's sensitivity table — the raw material is there |
| Can you compute a trial count with a power analysis? | Move fast through step 2 | Review `r1-robotics-evaluation-statistics` |
| Have you ever written a review of your own paper? | Start at step 4 | Do the self-review in `r1-paper-writing-review` first |

## Procedure

**Step 1 — narrow to one contribution (6 h).** Candidates come from three places: (a) **the survey's
empty cells** — a combination nobody has tried (e.g. method X without assumption Y); (b) **the
reproduction's sensitivities** — if the result was sensitive to a choice, that choice is itself a
research object; (c) **the cause of a reproduction failure** — test whether the cause you
established is a general phenomenon. Write three candidates and for each note (1) the contribution
sentence (verifiable), (2) the experiments required, (3) whether your resources allow it, (4)
whether it is worth reporting even if it fails. **Discard any candidate whose (4) is "no"** —
research that is only valuable when the hypothesis is true is risky. Pick one and fix the
contribution sentence.

**Step 2 — design the experiments (10 h).** Apply `r1-experiment-design` and
`r1-robotics-evaluation-statistics` directly. *Hypothesis*: falsifiable. "A is better" (no) →
"under more than 50% occlusion, A's success rate exceeds B's" (yes). *Baseline fairness*: equal
budget (search trials, training steps), starting from the official implementation and official
hyper-parameters, with modifications disclosed. **Tuning only your own method heavily is the most
common and most damaging defect.** *Ablation*: decompose the contribution into components and remove
**one at a time**, adding two-component removals where interaction is suspected. *Trial count*:
computed by power analysis; if infeasible on hardware, invert for the minimum detectable effect size
and **reduce the claim** to that range. *Pre-registration*: commit the metrics, trial counts and
analysis before running.

**Step 3 — run the experiments (30 h).** Keep the reproduction lesson's discipline: pin the
environment, get the smallest setting through end to end, validate the metric code, scale up, use
several seeds. In addition: **do not discard negative results** — the failed settings are what write
your limitations section and your ablation interpretation. If you **want to change the hypothesis**
mid-way, record it (when, why): a changed hypothesis needs a new pre-registration, and the fact that
it changed goes in the paper. Hiding it is post-hoc selection.

**Step 4 — write the draft (18 h).** Apply `r1-paper-writing-review`'s procedure: contribution
sentence → reverse-engineer the sections → figures first → self-review. Eight-page layout:
introduction 1.5 p / related work 1 p (your survey's axis, compressed) / method 2 p / experiments
2.5 p / limitations and conclusion 1 p. **Every comparison carries a trial count and a 95%
interval**, in the format Agarwal et al. (2021) recommend. The **limitations section** is concrete:
limits of power, unverified assumptions, scope, whether hardware was tested. Apply **Lipton &
Steinhardt's four trends** to your own manuscript as a checklist (explanation confused with
speculation, mathiness, and so on).

**Step 5 — release the code and get a DOI (4 h).** The full `r1-reproducibility-artifacts` criteria
plus a 10-minute smoke path. The paper cites **a DOI for a specific commit**.

**Step 6 — the 20-minute oral defence (10 h preparation + 1 h).** Format (modelled on Georgia
Tech's oral exam): a 15–20 minute talk plus questions. Structure: the problem and why it matters
(3 min) → the limits of existing approaches (2 min) → the contribution sentence and approach
(5 min) → evidence: main result and ablation (6 min) → limitations and next steps (2 min).
Preparation rules: **write 20 anticipated questions and prepare answers** — your self-review's six
attack items are the starting point. For a question you cannot answer, reply **"I don't know, and
here is how it could be found out"**; that is a researcher's answer, not a deduction. Stating a
guess as fact is what loses marks. Back-up slides: the full ablation table, the failed settings, the
hyper-parameters, the reproduction procedure. **Give at least one practice talk in front of two or
more people** and record their questions.

## Grading criteria

| Item | Pass | Strong |
|---|---|---|
| Contribution | One contribution stated as a sentence | **Traceable** to a survey empty cell or a reproduction sensitivity; narrow and verifiable |
| Baseline fairness | A baseline exists | Equal budget given numerically and modifications to the official setup disclosed |
| Ablation | Components are removed | One at a time + interaction check + each component's contribution with intervals |
| Statistics | Trial counts reported | Counts set by power analysis + 95% intervals on every comparison + multiple-comparison correction |
| Limitations | A limitations section exists | Power, assumptions and scope stated concretely; negative results reported |
| Reproducibility | Code released | 10-minute smoke path + third-party reproduction confirmed + the paper cites a DOI commit |
| Oral defence | The 20-minute talk is delivered | 20 anticipated questions prepared; unknowns answered as unknown with a route to find out |

## Failure cases

- **Making the contribution too large.** "A new framework" cannot be proved in eight pages.
- **A design that is only valuable if the hypothesis is true.** Failure leaves nothing to report.
- **Tuning only your own method.** The most common and most damaging defect.
- **An ablation that does not decompose the contribution.** Removing two components at once cannot be interpreted.
- **Changing the hypothesis mid-way without recording it.** Post-hoc selection, an ethics problem.
- **Discarding negative results.** You destroy the material for the limitations section and the ablation interpretation.
- **Reporting comparisons without intervals.** The first thing review flags.
- **Stating guesses as facts in the talk.** "I don't know" costs nothing; a guess costs credibility.
- **No back-up slides.** You cannot produce evidence during questions.

## Case study

**Apply the two required papers to your own manuscript.**

**Lipton & Steinhardt (2018)** — `critique`. Questions: (a) Find and fix a sentence in your draft
for each of the four trends (explanation confused with speculation, mathiness, misuse of language,
overstated narrative). (b) Does your contribution sentence claim more than the evidence? (c) Does
your related-work section understate prior contributions?

**Agarwal et al. (2021)** — `standard`. Questions: (a) Report your results as intervals and profiles
rather than point estimates. (b) If your trial count is low, which claim must you **withdraw**?
(c) Did you store your results in a form a stratified bootstrap can be applied to?

**Also**: pick two eight-page workshop papers in your field and count their **page allocation**
(pages per section, number of figures) to calibrate what fits in eight pages.

## Deliverables

**Deliverable 1 — the eight-page draft** (workshop format): structure and page allocation as in step
4, with three or more figures, one main results table (with intervals) and one ablation table.
**Acceptance**: (a) the contribution sentence is traceable to the survey or reproduction evidence,
(b) baseline budget equality is given numerically, (c) every comparison carries a trial count and a
95% interval, (d) the limitations section is concrete, (e) the code DOI is cited.

**Deliverable 2 — reproduction repository**: the full `r1-reproducibility-artifacts` criteria, a
10-minute smoke path, and scripts that generate the paper's tables and figures. **Acceptance**: a
third party succeeds at the smoke path within 10 minutes from the README alone and regenerates one
main results table.

**Deliverable 3 — the 20-minute oral defence**: slides, back-up slides and a document of 20
anticipated questions with answers. **Acceptance**: (a) finished within 15–20 minutes, (b) at least
five questions answered with evidence (back-up slides), (c) unanswerable questions met with **a way
to find out**, (d) written assessments from two or more audience members.

**Final acceptance**: pass or better on all seven grading items, with **the contribution sentence
traceable to a specific table or figure** in the draft, third-party reproduction confirmed, and no
instance of answering by guesswork in the defence.

## Open problems

- **(Open) Venue space for small contributions** — a structure that prefers novelty makes narrow,
  well-evidenced results hard to publish, which distorts how the field accumulates knowledge.
- **(Open) Valuing negative results** — there is no criterion for the importance of "X does not
  work", and no common reporting format covering both reproduction failures and negative results.
- **(Open) The reliability of oral assessment** — how well an oral-defence score separates
  presentation skill from research quality has barely been validated.

## Concept check

Take it with `rc quiz r2-capstone-contribution`. It is a concept check only.

## How to study this stage

1. **Write three candidate contributions and discard two (6 h)** — the discard criterion is "is it
   worth reporting even if it fails?". That question decides the capstone.
2. **Freeze the design as a pre-registration (10 h)** — commit metrics, trial counts and analysis. The
   power analysis sets the trial count, and if resources fall short, **reduce the claim**.
3. **Tune the baseline before your own method (during the run)** — reverse the order and budget
   asymmetry creeps in unnoticed.
4. **Make the three figures mid-experiment (during the run)** — a result that will not become a figure
   is a sign the claim is blurry.
5. **Revise the draft after writing a self-review (18 h)** — the six attack items from
   `r1-paper-writing-review`. Score yourself on the NeurIPS form before submitting.
6. **Give two practice talks (10 h)** — one to colleagues, one to an audience outside the field. The
   outside audience finds the introduction's defects best. Put every question you get into the
   anticipated list.
7. **Reverse-engineer the back-up slides from the question list (3 h)** — one evidence slide per
   anticipated question. That is the only way to prepare for questions.

**Bar to pass**: pass or better on all seven grading items, the contribution sentence traceable to a
specific table or figure, third-party reproduction confirmed, and no answer given by guesswork.

**Track complete**: passing this lesson finishes the whole path F0 → R0 → C1-C8 → S1-S5 → R1 → R2.
What remains is to **submit this work to a real venue** and get reviews — and that is research
outside the curriculum.
