---
id: f0-how-to-read-this-track
lang: en
title: How to read this track (the lesson standard)
summary: >-
  The conventions every lesson of the research track follows, in one place: derivation depth
  (D0-D3), the format of a proof sketch, the types of problem and what is published as their
  solution, the ten fixed questions put to a paper and three-pass reading, and the tiers (R1-R4)
  and acceptance criteria of a reproduction task. This is where other lessons point when they say
  "the ... section of this lesson".
objectives:
  - Tell from a [D0]-[D3] tag how far a result is to be worked through by yourself.
  - Read the problem type codes (P-D, P-P, P-N, P-I, P-C, P-R) and the difficulty marks, and say what solution is published for each.
  - Write a one-page note on a paper with the ten fixed questions and three passes.
  - Read the tier (R1-R4) and the acceptance criterion of a reproduction task and decide what is within your own compute.
tags: [foundations, guide, conventions, paper-reading, reproduction]
---

# How to read this track (the lesson standard)

Every lesson of the research track has the same structure: setup and notation → key results →
derivation → proof sketch → problem set → paper reading → reproduction task → open problems →
concept check. The notation that recurs in every lesson (`[D2]`, `P-N ★★`, "questions 4, 5, 6 and
7", `R2`) is explained here, once. Read it through at the start and come back when a tag puzzles
you.

**"The blueprint"** (or "the design"), which lesson texts mention now and then, is the plan drawn
up before this track was written. Where a lesson departs from the plan it says why; the plan itself
does not need to be read.

## Derivation depth

Each result in a "Key results" section carries a grade such as `[D2]`. It says how far the text
develops the result, and **how far the reader is expected to follow**.

| Grade | Meaning | What the text does | What the reader does |
|---|---|---|---|
| **D0** | cited | States the result and gives the source (textbook chapter and section, equation number in a paper) | Being able to use it is enough; look up the source if needed |
| **D1** | sketched | Starting assumptions → 3-5 key transformations → conclusion; algebra is omitted | Check that you can fill in the omitted steps yourself |
| **D2** | full derivation | Develops it with no line missing and names each assumption where it is used | Close the text and derive it again from the start on paper |
| **D3** | proof | Separates hypotheses from conclusion and gives the strategy and the grounds of each step | Be able to say where it breaks when one hypothesis is removed |

Every lesson has at least one result at D2 or above. A D2 or D3 result comes with at least one
counterexample or failure mode in which an assumption breaks. Skip it and you will not know when
the result must not be used.

## Proof sketches

A proof sketch is not a summary of a proof but **a plan from which you can rebuild it**. Every
sketch is written in the same order.

1. **Hypotheses and conclusion apart:** the hypotheses (H1, H2, ...) and the conclusion (C) are
   restated with numbers.
2. **One line of strategy:** which tool is used (a Lyapunov function, a contraction mapping,
   convex duality, a fixed point and so on).
3. **Three to six steps:** each says "what is shown" and "what is used" (which hypothesis, lemma or
   inequality).
4. **Gaps marked:** an omitted technical step is flagged `(omitted: ...)` with the number of the
   lemma in the original paper.
5. **Why each hypothesis:** one line on where the argument fails if a hypothesis is dropped.

Full proofs are not copied into the text. They are in the original papers and textbooks, and the
lesson points there.

## Problem sets

Each lesson has four to eight problems of at least three types. The type code decides **what is
published as the solution**.

| Code | Type | What is published |
|---|---|---|
| `P-D` | derivation | A solution sketch only (the starting point and two or three key steps) |
| `P-P` | proof | The strategy and the key inequality only |
| `P-N` | numerical | **The numerical answer and a tolerance** |
| `P-I` | implementation | Acceptance criteria and a reference output |
| `P-C` | counterexample | A checklist of the properties the counterexample must have |
| `P-R` | paper | A marking rubric instead of a model answer |

Full solutions to derivations and proofs are left out on purpose: the aim of this track is not to
read solutions but to work them out. Numerical problems publish the answer and tolerance at once
so that you can mark yourself.

Difficulty is shown with stars: ★ is about 15 minutes, ★★ about an hour, ★★★ a day or more. Each
problem carries the number of the key result it belongs to. The "Concept check" quiz at the end of
a lesson only checks concepts and does not replace the problem set; it is the only part connected
to automatic marking and review cards.

## Reading papers

Each lesson has two to four must-read papers, each with a role: seminal, standard, frontier or
critique. For each paper you write a one-page note answering the **ten fixed questions** below.
This is the list lessons refer to by number, as in "questions 4, 5, 6 and 7".

1. What problem does it solve, and under which assumptions? Can you state the assumptions in one
   sentence?
2. What exactly could earlier work not do? (The paper's claim against the real difference.)
3. What is the key idea, reduced to one line of mathematics or one figure?
4. What are the theoretical guarantees (existence, optimality, convergence, completeness), and
   **what is not guaranteed**?
5. What are the independent variables, the dependent variables and the baselines of the
   experiments? Were the baselines tuned fairly?
6. Which metrics are used, and do they fit the claim? Are variance, seeds and confidence intervals
   reported?
7. What information needed for reproduction is **missing**? (Hyperparameters, initialization, data
   preprocessing, hardware.)
8. If this result were wrong, which assumption would you suspect first?
9. What are the computational and memory complexity and the real-time behaviour? Could it run on a
   robot?
10. What would you change to go beyond this paper a year from now? (One research idea.)

The way to read is Keshav's **three passes**. The first pass (5-10 minutes) takes only the title,
abstract, introduction, section headings and conclusion, and decides whether the paper is worth
reading. The second pass (about an hour) grasps the content through the figures and tables,
skipping proofs and details. The third pass rebuilds the paper in your head, doubting each
assumption in turn. In the third pass concentrate on questions 4, 5, 6 and 7 (guarantees,
experimental design, metrics, missing information).

**The textbook exception.** For the pure mathematics lessons of the R0 module (mathematical and
numerical foundations) the primary source is a standard textbook, not a paper. Those lessons read
two or three textbook chapters or sections and one methodological text in place of must-read
papers, and apply questions 1, 3, 4 and 8 (problem, idea, guarantees, the assumption to suspect) to
the textbook.

## Reproduction tasks

Each lesson has one reproduction task, with a tier. The tier says **what is reproduced and how much
compute it takes**.

| Tier | Meaning | Compute budget | Example |
|---|---|---|---|
| **R1** | numerical check | laptop CPU, under a minute | Mass matrices computed by two methods agree to within 1e-8 |
| **R2** | re-implementation | laptop CPU, under ten minutes | Cart-pole swing-up with iLQR, with the cost decreasing monotonically |
| **R3** | figure reproduction | an hour of CPU, or a public dataset | A convergence curve or error table of the paper reproduced on the same dataset |
| **R4** | scaled-down replication | may need a GPU; **always optional** | The trend reproduced by training at a tenth of the paper's scale |

A task that may need a GPU is always R4, that is, optional. The mandatory conditions can be
finished on a laptop CPU. Every reproduction task states the following.

- **Acceptance criterion:** a numerical condition that can be judged mechanically (for example
  "mass-matrix error < 1e-8"). Only numbers the author actually obtained by running the task are
  used as criteria.
- **Input data:** a public dataset or a generation script the lesson provides. No personal data is
  needed.
- **Failure diagnosis table:** three common failures and their causes (for example divergence →
  the linearization point, a sign convention, angle wrapping).
- **Compute budget:** upper limits on cores, time and memory.
- **Comparison:** at least one baseline (a simple method you implement, or the value the paper
  reports).

When the acceptance criterion is not met, start from the failure diagnosis table. Most failures
are one of those three.

## How to study this stage

1. **Skim once (20 minutes):** look at the tables of the five sections first. Do not memorize.
2. **Compare in your first lesson:** in the first core lesson you open, each time you meet `[D2]`,
   `P-N ★★` or `R2`, compare it with the table here. Two or three lessons are enough.
3. **Keep the ten questions apart:** copy the list onto one sheet you can see whenever you write a
   paper note.
4. **Check:** read Keshav's "How to Read a Paper" (two pages) and say what each of the three passes
   is for.

## References

- S. Keshav, "How to Read a Paper", ACM SIGCOMM Computer Communication Review 37(3), 2007 - <http://ccr.sigcomm.org/online/files/p83-keshavA.pdf>
