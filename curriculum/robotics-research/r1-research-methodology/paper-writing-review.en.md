---
title: Paper Writing and Peer Review
summary: >-
  Build a paper structure that runs from problem to contribution, design the figures, and attack
  your own paper as a reviewer. The deliverables are an eight-page draft and one review of someone
  else's paper.
objectives:
  - Design a structure that runs problem -> contribution -> method -> experiments -> limitations.
  - State the contribution as a verifiable sentence and arrange each section to support it.
  - Design each figure to carry one claim and write self-contained captions.
  - Find your paper's weakest point from a reviewer's perspective and address it pre-emptively.
  - Write one constructive review to form, and answer a rebuttal with evidence.
---

# Paper Writing and Peer Review

## Goals

A paper is **not a report of the research but a structure of claims**. A good result written badly
is rejected; a modest result written honestly and well is sometimes accepted. This lesson trains
writing and reading as **one skill**: once you have a reviewer's eyes, you can see your own paper's
weaknesses.

**The central claim of this lesson**: the design of the paper must be finished before the writing.
Fix one contribution sentence, lay out how each section supports it, and only then write sentences.
Done in reverse, the result is "a list of what we did" and the reviewer cannot find the contribution.

Deliverables: **an eight-page draft, one review of another paper, and a rebuttal draft**.

## Self-diagnosis before you start

| Question | If you can | If you cannot |
|---|---|---|
| Can you state your contribution in one sentence? | Start at step 2 | Go back to the proposal from `r1-research-questions` |
| Are your experimental results and intervals ready? | Follow the steps in order | Finish the previous two lessons (evaluation, reproducibility) first |
| Have you ever named a **falsifiable weakness** in someone else's paper? | Move fast through step 4 | Read step 4 closely — review training is half of this lesson |

## Procedure

**Step 1 — fix the contribution sentence (1 h).** One sentence, active voice, verifiable: "we
improve Y by Z under condition X", or "we show that X fails because of Y". Adjectives ("novel",
"efficient") cannot carry a contribution. If there are **two or more**, make one primary and demote
the rest — three equal contributions read as zero.

**Step 2 — reverse-engineer the sections from the contribution (2 h).** Write one line stating why
each section exists. *Introduction*: why the problem matters → the **specific** limitation of
existing approaches → your contribution sentence → a summary of the evidence; the last paragraph is
the contribution list. *Related work*: not a list but **drawing the boundary against your
contribution** — each cluster needs a "so they cannot do X". *Method*: the minimum needed to
reimplement, with design rationale, including what does not work. *Experiments*: each subsection
**answers one question**, in the order question → setup → result → interpretation. *Limitations*:
hide them and the reviewer finds them; write them first and trust goes up. When the structure is
done, **place each figure and table in its section**. The prose comes after.

**Step 3 — design the figures first (3 h).** Reviewers look at figures first. One figure = one
claim: write the sentence the figure must convey, then build it. **Captions must stand alone** — the
reader should know what they are looking at and what the conclusion is without the body text.
Always show axes, units, error bars (confidence intervals) and the trial count; a comparison figure
without error bars is not evidence. Use perceptually uniform colours and check legibility in
greyscale and for colour-vision deficiency. A system figure should show the **data flow**, with each
block matched to a section of the text.

**Step 4 — become the reviewer and attack (3 h).** Read your own paper **as someone else's** and
write a review on the review form. The attack list: (a) is the contribution sentence supported by
the experiments (claim > evidence is grounds for rejection), (b) is the baseline's tuning budget
equal, (c) are trial counts and intervals present, (d) does the ablation decompose the
contribution, (e) do the equations match the implementation, (f) are the limitations real (not
boilerplate)? **For each attack you either (1) fix the text, (2) admit it as a limitation, or
(3) run another experiment.** One of those three.

**Step 5 — write one review of another paper (3 h).** Use the real form (summary / strengths /
weaknesses / questions / limitations / score / confidence). Rules: **summary first**, so the author
feels understood. Weaknesses must be **specific and actionable**: "the experiments are weak" (no) →
"Table 2 uses three seeds with no intervals and therefore does not support the 10-point claim in
§3.1; ten seeds and 95% intervals are needed" (yes). Judge the **paper, not the author**:
speculation about the author and demands to cite your own work are out. Confidentiality: do not
share a manuscript under review externally or **put it into a generative model** (venue policy).

**Step 6 — write the rebuttal (2 h).** Form: (a) thanks and a grouping of the issues, (b) **the most
damaging point first**, (c) answer each with evidence (new numbers, a location in the text),
(d) concede correct points immediately and offer the revision. **Do not argue; supply evidence.**
When space runs short, cut by priority of the issue.

**Research ethics (always)**: no duplicate submission; authorship for actual contributors only with
an agreed order; no manipulation of data or figures (outlier removal only by a pre-set criterion);
disclose conflicts of interest; check venue policy on generative-model use; avoid missing citations.
**Not reporting the settings where your method failed, to make results look better, is selective
reporting and borders on misconduct.**

## Grading criteria

| Item | Pass | Strong |
|---|---|---|
| Contribution sentence | Stated in one sentence | Verifiable, with each section arranged to support it |
| Structure | Follows the standard sections | Each section has a reason to exist; each experiment subsection answers one question |
| Figures | Axes and units present | One figure = one claim, self-contained caption, error bars and trial counts, greyscale/CVD checked |
| Limitations | A limitations section exists | Real weaknesses (low power, unverified assumptions) stated concretely |
| Review | The form is filled in | Weaknesses are actionable, cite section/table numbers, and the tone is professional |
| Rebuttal | Every point is answered | Ordered by severity, new evidence supplied, correct points conceded |

## Failure cases

- **Writing the contribution with adjectives.** "A novel and efficient framework" is not a contribution.
- **Having three contributions.** Three equal ones read as zero to a reviewer.
- **Related work as a list.** Without a boundary, "what is the difference?" becomes the first question.
- **Figures without error bars.** The basis for a comparative claim disappears.
- **A caption that says only "results".** Reviewers often judge from the figures alone.
- **A boilerplate limitations section.** "More experiments are needed in future" is not a limitation.
- **Not reporting failed settings.** That is selective reporting, an ethics problem.
- **Arguing in the rebuttal.** Emotional rebuttal lowers scores. Supply only evidence.
- **Guessing the author in a review.** It breaks double-blind review and degrades review quality.

## Case study

**One required paper plus two dissected introductions.**

**Lipton & Steinhardt, "Troubling trends in machine learning scholarship" (2018)** — `critique`.
Questions: (a) What are the four trends, and how does each mislead the reader? (b) Find an example
of "conflating explanation with speculation" in a paper from your own field. (c) Why is mathiness a
problem — how does it differ from simply having many equations? (d) Find and fix a sentence in your
own draft for each of the four trends.

**Introduction dissection**: split the introductions of two top-venue papers in your field into
sentences and tabulate each sentence's **function** (importance / existing limitation /
contribution / evidence summary / outline). Then build the same table for your own introduction and
find the missing functions. As **supporting material**, read Agarwal et al. (2021)'s reporting
recommendations and audit your experiments section's reporting format against them.

## Deliverables

**Deliverable 1 — an eight-page draft** (venue template): introduction, related work, method,
experiments, limitations, conclusion, plus references (outside the page limit) and an optional
appendix. One contribution sentence, three or more figures (one claim each, self-contained caption,
error bars) and one main results table (with intervals). **Acceptance**: (a) the contribution
sentence is traceable to a specific table or figure in the experiments, (b) every comparison carries
a trial count and an interval, (c) the limitations section is concrete, (d) a link to the
reproduction repository (the previous lesson's deliverable).

**Deliverable 2 — one review of another paper** (1–1.5 pages): a paper from your field published
within the last year (arXiv is fine), on the form summary / strengths / weaknesses / questions /
assessment of limitations / score and confidence. **Acceptance**: three or more weaknesses that each
**name a section or table number** and include an **actionable request**.

**Deliverable 3 — a rebuttal draft for your own paper** (1 page): answers to five points from the
review you wrote in step 4. **Acceptance**: ordered by severity, each answer citing a number or a
location in the text, and at least one that **concedes and offers a revision** rather than rebutting.

**Acceptance**: all three deliverables pass or better, and **at least three points from one
colleague's review are incorporated** into the draft.

## Open problems

- **(Open) The reliability of peer review** — low inter-reviewer agreement on the same paper is
  reported repeatedly. How to keep review quality at large venues (reviewer incentives, reviewer
  training, meta-review design) is unsolved.
- **(Open) A publication path for negative results** — reproduction failures and negative results
  have value but little venue space. The size of the distortion this publication bias causes is
  hard to measure.
- **(Open) Generative models in authoring and reviewing** — norms for using large models to draft
  papers and reviews differ by venue and keep changing. The boundaries of confidentiality and
  authorship are not settled.

## Concept check

Take it with `rc quiz r1-paper-writing-review`. It is a concept check only.

## How to study this stage

1. **Rewrite the contribution sentence ten times (1 h)** — show only the sentence to a colleague and
   ask what you did. If it needs explaining, it is not done.
2. **Make the figures before the prose (3 h)** — three figures with captions give the paper its
   skeleton. Put error bars and trial counts in from the start.
3. **Dissect introductions into a function table (2 h)** — two other papers and your own draft. A
   missing function is the reviewer's first question.
4. **Write a review of your own paper (3 h)** — on the real form, score included. It is the most
   efficient quality improvement available; use step 4's six attack items verbatim.
5. **Actually write one review (3 h)** — the writing eye and the reading eye are the same muscle.
   Follow confidentiality rules (never put the manuscript into an external service) and keep the
   tone professional.
6. **Finish with a rebuttal draft (2 h)** — answer the five points from your own review. Any point
   you cannot answer is **a sentence for the limitations section**.

**Bar to pass**: the draft, review and rebuttal reach pass or better on all six grading items, and
three or more points from a colleague's review are incorporated into the draft.
