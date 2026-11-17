---
title: Capstone 1 - Survey
summary: >-
  Classify 40 or more papers in your chosen specialisation yourself and write a 10-15 page survey.
  The bar is a classification axis that offers at least one perspective existing surveys do not, and
  a verified URL for every citation.
objectives:
  - Systematically collect 40 or more papers in one field and filter them with inclusion/exclusion criteria.
  - Build a classification axis different from existing surveys and argue what it reveals.
  - Summarise each paper's contribution, assumptions and evidence in a comparable format.
  - Identify the field's open problems with evidence and rank them.
  - Give every citation a verified URL and avoid second-hand citation.
---

# Capstone 1 - Survey

## Goals

A survey is **not a summary of what you read but a new grid for seeing a field**. The same 40 papers
produce completely different terrain depending on the axis you choose, and a good survey uses that
axis to show the **cells nobody has filled yet**. Those empty cells are the starting point for the
next two lessons (reproduction, contribution).

There are two bars for this lesson: (a) the classification axis offers **at least one perspective
that existing surveys do not**, and (b) **every citation's URL is verified** (title, authors, year
and venue). The second looks trivial, but it is the basis of a researcher's credibility and the
promise most often broken.

Deliverables: **a 10-15 page survey, a classification table of 40+ papers, and a citation
verification log**.

## Self-diagnosis before you start

| Question | If you can | If you cannot |
|---|---|---|
| Have you picked a specialisation (one of S1-S5, or their intersection)? | Start at step 1 | Pick one first — a survey without scope never ends |
| Have you built the 30-paper table from `r1-literature-survey`? | Proceed | Finish that lesson first; this is three times the scale |
| Can you tell a primary source from a second-hand citation? | Move fast through step 3 | Read step 3 closely — second-hand citation is the main source of error propagation |
| Do you know two existing surveys in your field? | Start at step 2 | Find them in step 2 — without a differentiator there is no reason to write |

## Procedure

**Step 1 — nail the scope down in sentences (4 h).** Three sentences: (a) what is covered (problem,
methods, target robots), (b) what is not covered **and why**, (c) which period and which venues.
Write the inclusion and exclusion criteria **before searching** (e.g. 2015 onward; peer-reviewed
venues or arXiv with 20+ citations; evaluation on hardware or in reproducible simulation). Collect
without criteria and you cannot stop at 40.

**Step 2 — dissect existing surveys first (5 h).** Extract the **classification axis** of two or
three surveys in your field (including the two required papers) into a table: what did the authors
group by (method family? sensor? assumptions? strength of guarantee?), and **what did that axis
reveal and what did it hide**? Then write three candidate axes of your own and one line each on
what they show that the existing axes do not. **That line is the survey's contribution sentence.**

**Step 3 — collect and filter the corpus (20 h).** Work three paths in parallel: (a) keyword search
including term variants, (b) **citation-network tracing** (the references and citers of five core
papers), (c) the publication lists of the main groups. Record inclusion/exclusion and the **reason**
for each paper — the exclusion record is the evidence for your scope. Rule: **read primary sources.**
Never write "A showed B" from C's description of it; second-hand citation is the main source of
misattribution. Reach 40 or more, but **never put a paper you have not read in the table.**

**Step 4 — build the comparison table (10 h).** The columns come from your axis. At minimum:
contribution type / core assumptions / strength of guarantee (proved, empirical, none) / evaluation
setting (sim, hardware, both) / metrics / reproducibility (code and data released?) / limitations.
This table must be finished before the prose. As you fill it, **patterns of empty cells** appear —
those are candidate open problems.

**Step 5 — write the body (24 h).** Structure: introduction (why this survey is needed = the limits
of the existing axes) → definition and justification of the axis → one section per axis value (each
stating the **shared assumption of the group and its cost**) → the comparison table and its
interpretation → open problems (ranked, with evidence) → conclusion. **Forbidden**: a structure that
summarises papers one paragraph each. That is an annotated list, not a survey.

**Step 6 — verify the citations (5 h).** Open every URL and confirm title, authors, year and venue,
logging the **date and method** of confirmation. If a publisher page blocks automated access, confirm
via the authors' lab page or the conference programme and say so. Mark anything unconfirmed as
**(unverified)** or remove it. A guessed reference is not an error but a **credibility problem**.

**Step 7 — publish it as an artifact (2 h).** Put the classification table (CSV) and the
bibliography (BibTeX) in a repository and get a DOI. A survey's value doubles when other
researchers can **keep filling it in**.

## Grading criteria

| Item | Pass | Strong |
|---|---|---|
| Scope | Inclusion/exclusion criteria stated | Exclusions and reasons recorded; the scope is reproducible |
| Classification axis | An axis is defined | **At least one perspective existing surveys lack**, with an argument for what it reveals |
| Corpus | 40+ papers, all read | Collected by citation-network tracing, with the exclusion record published |
| Comparison table | A table follows the axis | Includes assumptions, guarantee strength and reproducibility; empty-cell patterns interpreted |
| Open problems | A list exists | Evidence (empty cells, failure reports), ranking and an assessment of tractability |
| Citations | Every URL verified | Date/method log + primary-source discipline + CSV and BibTeX published |

## Failure cases

- **Summarising papers one paragraph each.** The most common failure. Without an axis it is not a survey.
- **Starting without reading existing surveys.** You rebuild the same axis and cannot explain the difference.
- **Putting unread papers in the table.** Cells filled from abstracts are wrong.
- **Using a second-hand citation as primary.** "A showed B" often turns out to be C's summary.
- **Not setting a scope.** Forty papers becomes four hundred and never ends.
- **Not verifying citations.** Nonexistent volumes, wrong authors and dead links creep in.
- **Writing open problems as "more research is needed."** That is not a problem statement.
- **Collecting only recent papers.** Omitting the field's turning points distorts the axis.

## Case study

**Dissect the two required papers as model surveys.**

**Cadena et al. (2016), the SLAM survey** — `survey`. Questions: (a) What axis groups the field
(problem components? maturity? guarantees?) (b) What does framing it as the "robust perception age"
reveal? (c) Separate the open problems they list into those now solved and those still open — from
ten years later, assess this survey's **predictive accuracy**.

**Garrett et al. (2021), the TAMP survey** — `survey`. Questions: (a) On what axis does it divide
algorithms (sampling strategy? interface? completeness guarantees?) (b) Compared with Cadena's axis,
**what different kind of terrain** does it produce? (c) Transplanted to your field, what would that
axis show?

**Output**: a one-page comparison of the two surveys' axes and **three candidate axes of your own**
derived from it.

## Deliverables

**Deliverable 1 — the survey body** (10-15 pages, venue template): structured as in step 5, with two
or more figures (one classification-terrain figure required). **Acceptance**: (a) the axis offers at
least one perspective existing surveys lack and the body argues for it, (b) each axis section states
the group's **shared assumption and its cost**, (c) the open problems connect to the table's evidence.

**Deliverable 2 — classification table** (CSV plus an in-paper table): 40+ rows × at least 7 columns
(step 4), every row a paper you **read**. **Acceptance**: empty cells distinguish "not applicable"
from "no information".

**Deliverable 3 — citation verification log** (CSV): per entry the id, URL, date of confirmation,
method (publisher page / author page / conference programme) and outcome. **Acceptance**: every
citation appears in the log, and unverified entries are either marked in the body or removed.

**Final acceptance**: pass or better on all six grading items, three or more points from a
colleague's review (`r1-paper-writing-review` form) incorporated, and the table and BibTeX published
with a DOI.

## Open problems

- **(Open) The lifetime of a survey** — in a fast-moving field a survey is stale in two or three
  years. Operating models for a living survey, and how to attribute contributions to it, are unsettled.
- **(Open) Evaluating a classification axis** — there is no objective criterion separating a good
  axis from a bad one. Judging by predictive power (do the empty cells actually get filled?) takes years.
- **(Open) Selection bias** — even with inclusion criteria, search paths and language or venue
  accessibility cause systematic omissions. Almost no work measures the size of this effect in robotics.

## Concept check

Take it with `rc quiz r2-capstone-survey`. It is a concept check only.

## How to study this stage

1. **Write the three scope sentences first (4 h)** — what is covered, what is not and why, period and
   venues. Without them the work never finishes.
2. **Dissect two existing surveys by axis (5 h)** — your candidate axes come from here. If you cannot
   state the differentiator in one line, do not start yet.
3. **Collect via the citation network (20 h)** — keyword search alone misses the field's skeleton.
   Follow the references and citers of five core papers.
4. **Finish the table before the prose (10 h)** — the pattern of empty cells writes your open-problems
   section. Without the table the body degenerates into a list of summaries.
5. **Revise the axis once while writing (24 h)** — drafting exposes the axis's defects. Revising is
   normal; not revising is the warning sign.
6. **Open every citation (5 h)** — without exception. One wrong reference discounts the whole survey.
7. **Get a colleague's review (3 h)** — on the `r1-paper-writing-review` form; incorporate three or
   more points.

**Bar to pass**: pass or better on all six grading items, the axis's differentiator explained in one
sentence and argued in the body, and every citation backed by a verification log.
