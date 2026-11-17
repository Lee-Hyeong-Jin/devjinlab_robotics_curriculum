---
id: r1-research-questions
lang: en
title: Research questions and hypotheses
summary: >-
  Turn the empty cells of a literature table into falsifiable research questions, fix the type of
  contribution, and narrow the scope. The deliverable is a two-page research proposal in the format
  of Georgia Tech's oral examination.
objectives:
  - Turn the empty cells of a literature search into research questions.
  - Rewrite a research question as a falsifiable hypothesis.
  - Distinguish the types of contribution (theory, method, system, analysis) and name yours as one of them.
  - Narrow the scope into a question finishable within six months.
  - Write a two-page research proposal in a form you can defend orally.
tags: [research-methodology, research-questions, hypothesis, research]
---

# Research questions and hypotheses

## What you will be able to do

In the previous lesson you found the **empty cells** of a classification table. This lesson turns
them into **falsifiable questions**.

**Why this is its own lesson**: it is the core ability a graduate qualifying examination tests.
Georgia Tech's oral exam assigns a topic and requires a **two-page written summary (literature
review, research problem, possible solution approaches)** within three weeks plus a 15-20 minute
talk. CMU's Research Qualifier likewise asks whether you can carry out research. Without the
ability to pose a question there is no next step.

Deliverables: **a two-page research proposal and three falsifiable hypotheses**.

## Procedure

**Step 1 — from empty cell to question (1 hour).** For each empty region of the previous lesson's
table, ask *why* it is empty. The answer is one of three: (a) nobody has tried (an opportunity);
(b) it was tried and failed (find the failure report); (c) it need not be done (a meaningless
combination). **Mistaking (c) for (a) is the most common failure.**

**Step 2 — from question to hypothesis (2 hours).** "Is X possible?" is not a hypothesis. A
hypothesis must be a statement that **can be wrong**:
- bad: "does a learned method help SLAM?"
- good: "a learned front end reduces ATE by at least 30% relative to a geometric front end in
  texture-less environments."
A good hypothesis makes its **refutation condition explicit** — you can say which experimental
outcome would make it false.

**Step 3 — pick one type of contribution (1 hour).**

| Type | What it claims | How it is evaluated |
|---|---|---|
| **Theory** | a new guarantee (convergence, optimality, complexity) or an impossibility | a proof; experiments are secondary |
| **Method** | it solves an existing problem better | metric improvement against a fair baseline, plus ablations |
| **System** | composing parts achieves what was previously impossible | a real-robot demonstration plus failure-mode analysis |
| **Analysis** | it explains **why** existing methods work or fail | controlled experiments and counterexamples |

**Claiming two at once weakens both.** Choose one and let the rest be incidental.

**Step 4 — narrow the scope (2 hours).** Cut by "can this be finished in six months?". Ways to
cut: add assumptions (restrict to 2D, no contact), reduce scale (a single robot, a single task),
reduce evaluation (simulation first, one real-world setting). **Narrowing is not a reduction of
ambition but the acquisition of verifiability.**

**Step 5 — write the proposal (3 hours).** Two pages: (1) the problem (one paragraph); (2) why it
is unsolved (2-3 paragraphs, with literature evidence); (3) three hypotheses; (4) the verification
plan (a refutation condition per experiment); (5) the expected contribution type and the success
criterion; (6) the biggest risk and the alternative.

**Step 6 — prepare the oral (1 hour).** A 15-minute talk plus questions. Write ten anticipated
questions and prepare a paragraph for each. **"Why does it matter?" and "hasn't X already done
this?" will certainly come.**

## Rubric

| Item | Pass | Strong |
|---|---|---|
| Specificity of the question | the question is one sentence with an explicit scope | the question points at a specific empty cell of the table |
| Falsifiability | all three hypotheses can be wrong | each hypothesis states its **refutation condition** numerically |
| Contribution type | one of the four is named | why that type, and what its evaluation standard is, are explained |
| Literature evidence | "unsolved" carries citations | the difference from the 2-3 closest prior works is stated **concretely** |
| Scope | it is claimed feasible in six months | the assumptions added to narrow it are stated, with an assessment of how much they limit the result |
| Risk | one risk is listed | 2-3 risks with an alternative (plan B) for each |

## Failure modes

- **"Is it possible?" questions.** A yes/no question almost always ends in "yes" (anything is
  possible to some degree) and teaches nothing. Ask **how much** and **under what conditions**.
- **Mixing contribution types.** A proposal claiming "a new theory, a new system and an analysis"
  ends shallow on all three. Asked "which is the contribution?", you cannot answer.
- **"Unsolved" without literature.** The most common cause of rejection. Not knowing the prior work
  means proposing what already exists.
- **No refutation condition.** "Performance will improve" is unfalsifiable. The **size and
  conditions** of the improvement must be written for an experiment to be designable (next lesson).
- **Scope far too wide.** "Solve general manipulation" is impossible in six months, and when it
  fails you do not know what failed.
- **Choosing the metric later.** Not fixing the metric first leads to choosing it after seeing the
  results (the post-hoc selection problem of `r1-robotics-evaluation-statistics`).

## Case study

**One must-read plus three reverse-engineered.**

1. **Agarwal et al., "Deep reinforcement learning at the edge of the statistical precipice" (2021)**
   — `critique`. Questions: (a) write this paper's **research question** in one sentence. (b) which
   of the four contribution types is it? (c) how did the authors formalise what they refute
   (established practice) into a **falsifiable** form? (d) if this paper were applied to your field,
   which claims would collapse?

2. **Reverse-engineering task**: pick three papers from the previous lesson's table and
   **reverse-engineer each one's research question and hypothesis**. Papers rarely state their
   question, so it must be inferred from the abstract and the experiment design. For each:
   (a) the question in one sentence; (b) the implicit hypothesis; (c) the contribution type;
   (d) whether the authors **stated a refutation condition**. Count how many of the three did —
   usually few.

## Deliverable

**Deliverable 1 — a two-page research proposal** (Georgia Tech oral-exam format)
- Include all six parts of step 5. Do not exceed two pages (the compression is part of the training).
- Attach a citation to every "unsolved", using the verified URLs of the previous lesson.

**Deliverable 2 — three falsifiable hypotheses**
- For each: (a) the metric to measure; (b) the comparison (baseline); (c) the **refutation
  condition** (which number would make it false); (d) one experiment needed.

**Deliverable 3 — ten anticipated questions with answers**
- Must include "why does it matter", "hasn't X already done this", "why not something simpler", and
  "is that assumption realistic".

**Acceptance criteria**: all six rubric items at "pass" or above, and **one peer, reading only the
proposal, can correctly restate (a) the question, (b) the contribution type and (c) the success
criterion.** If they cannot, the thinking rather than the writing is unclear.

## Open problems

- **(Open) Can choosing a good question be taught?** — the procedure here mechanically produces
  "empty cell → question", but judging **which empty cell matters** rests on experience. Attempts
  to formalise that judgement exist but differ by field.
- **(Open) Recovering questions from negative results** — because "it did not work" reports go
  unpublished, case (b) of step 1 is hard to confirm, so the same failures repeat (the same item as
  the publication bias of `r1-literature-survey`).
- **(Open) The trade-off between scope and impact** — a narrow question is verifiable but low
  impact, and a broad one the reverse. There is no way to quantify that trade-off, so **"narrow it"
  is not always right** — research that changed a field usually came from a broad question.

## Concept check

Run `rc quiz r1-research-questions` (add `--lang en` for the English text). It is for concept
checking only; the real work is the deliverable.

The four items cover: which statement is falsifiable; which reason for an empty cell is not an
opportunity; which contribution type "explaining why methods work" is; and whether narrowing the
scope is always right.

## How to study this stage

1. **Sort the empty cells into three kinds (1 hour)** — label each empty region "opportunity,
   failure, meaningless". Filtering out the meaningless changes the quality of your question most.
2. **Rewrite each hypothesis three times (2 hours)** — the first version is always vague. Revise
   while checking that all four elements (metric, condition, baseline, size) are present.
3. **Say the contribution type out loud (30 min)** — try saying "my contribution is an
   **analysis**". If it feels wrong you have not decided. If you want to say two, drop one.
4. **Build instinct by reverse-engineering (110 min)** — infer the questions of the three case-study
   papers. Finding the question in someone else's paper is the fastest training for posing your own.
5. **Keep to two pages (3 hours)** — compress when it overflows; compression organises thought.
   That is why the Georgia Tech format is two pages.
6. **Have a peer restate it (30 min)** — let them read the proposal and restate the question,
   contribution and success criterion. A wrong restatement means **the thinking, not the writing**,
   is unclear.

**Passing bar**: a two-page proposal, three hypotheses each with a refutation condition, and ten
anticipated questions with answers, all at "pass" or above on the six rubric items, plus passing
the peer restatement check.
