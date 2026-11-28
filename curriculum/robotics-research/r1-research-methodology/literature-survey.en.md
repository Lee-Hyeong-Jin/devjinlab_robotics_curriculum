---
id: r1-literature-survey
lang: en
title: Literature search and reading and writing surveys
summary: >-
  Systematically collect and classify the literature of one topic, and build a classification axis
  that differs from existing surveys. The deliverables are a 30-paper classification table and a
  survey outline.
objectives:
  - Collect the literature of a topic exhaustively using search terms, citation networks and conference proceedings.
  - Distinguish primary sources (original papers) from secondary ones (surveys, blog posts) and state what each is for.
  - Organise 30 papers along classification axes and explain what those axes reveal and what they hide.
  - Criticise the classification axis of an existing survey and propose a different one.
  - Write a survey outline (the section structure and the claim of each section).
tags: [research-methodology, literature-review, survey, research]
---

# Literature search and reading and writing surveys

## What you will be able to do

Research **starts with reading** — but "reading a lot" and "reading systematically" are different
things. This lesson trains the latter: collecting the literature of a topic exhaustively, building
a classification axis, and judging what that axis reveals.

**Why it matters**: (1) claiming a contribution requires knowing what already exists, and the most
common failure in research is solving an already-solved problem; (2) building a classification axis
is itself a **research contribution** — a good survey gives a perspective, not a summary; (3) the
first deliverable of the R2 capstone is a survey.

Deliverables: **a 30-paper classification table and a survey outline** (section structure with the
claim of each section). The bar is in the rubric below.

## Self-diagnosis before starting

This is the module's first lesson, so check your readiness. If you can answer all of these, go
straight to the procedure. **If two or more stop you**, returning to the prerequisite named in
parentheses is faster.

1. What do you use to see the list of papers **citing** a given paper, and why is that better than
   a search term? (the procedure, step 1)
   **Answer**: "Cited by" in Google Scholar or citations in Semantic Scholar. Search terms depend on
   the vocabulary the authors used, whereas a citation graph follows the **actual connections of the
   topic** — which matters especially in a field whose terminology has changed.
2. To see the latest work in a field exhaustively, whose proceedings should you read? Name four for
   robotics.
   **Answer**: RSS, ICRA, IROS, CoRL (plus the journals IJRR, T-RO, RA-L, and NeurIPS, ICML, ICLR
   on the learning side).
3. On reading a paper claiming "method A beats B" without statistical significance, what do you
   check first? (`f0-probability-statistics`)
   **Answer**: the seeds, the number of trials and the confidence intervals. A single-run comparison
   is not evidence — `r1-robotics-evaluation-statistics` treats this.
4. Which should you read first, a survey or an original paper, and why? (the procedure)
   **Answer**: use a survey to see the landscape and original papers to go in. But **the evidence
   for a claim is always the original paper** — citing a survey's summary uses a secondary source
   as a primary one.
5. The arXiv and published versions of a paper can differ; which should you cite?
   **Answer**: the peer-reviewed version, with its numbering. If only an arXiv version exists, cite
   that and state the version. Cases where the two differ in their results do occur.

## Procedure

**Step 1 — start from three seed papers (2 hours).** Fix a topic and find (a) the most cited paper,
(b) the most recent paper and (c) the best survey. Start with search terms, but **do not stop there.**

**Step 2 — expand the citation graph in both directions (4 hours).** From each seed, follow
(a) its references (backwards) and (b) its citations (forwards). Two hops usually gather 100-300
papers. **Do not read** at this stage — build the list from titles and abstracts only.

**Step 3 — cut down to 30 (2 hours).** Criteria: (a) the original (where the idea first appeared);
(b) the current best (within two years, top of a benchmark); (c) rebuttals and failure reports;
(d) surveys. **Do not omit (c)** — collecting only successes hides the limits of the field.

**Step 4 — build a classification axis (4 hours).** Classify the 30 along 2-3 axes. Common axes:
methodology (analytic versus learned), assumptions (observability, presence of contact), mode of
evaluation (simulation versus real), chronology. **Using the same axis as an existing survey
contributes nothing** — at least one axis must be your own.

**Step 5 — build the table (3 hours).** Rows are papers; columns are the axes plus core claim,
guarantees, mode of evaluation and limitations. Filling it in reveals **patterns in the empty
cells**, and those are research opportunities.

**Step 6 — write the survey outline (2 hours).** Write the section structure and **one sentence of
claim per section**. Write "X is true" rather than "this covers X".

## Rubric

The deliverables are judged as follows (four levels: below / pass / strong / presentable).

| Item | Pass | Strong |
|---|---|---|
| Coverage | 30 papers including all four kinds: original, recent, rebuttal, survey | an expert in the field names at most one important missing paper |
| Citation accuracy | author, year, venue and URL of every entry are **verified** | published and preprint versions are distinguished |
| Classification axis | everything classified along 2-3 clearly defined axes | **at least one** axis differing from existing surveys, with an account of what it reveals |
| Reading the empty cells | the empty regions of the table are identified | each is judged a research opportunity or a meaningless combination, with reasons |
| Survey outline | a section structure exists | each section carries a **claim** (not "this covers X" but "X fails because of Y") |

## Failure modes

- **Stopping at search terms.** In a field whose terminology has shifted ("visual odometry" versus
  "ego-motion estimation"), search terms alone miss half the work. The citation graph crosses the
  change in vocabulary.
- **Citing a survey as a primary source.** A survey's summary is the author's interpretation. To use
  it as evidence you must read and cite the original.
- **Collecting only successes.** Without rebuttals and failure reports you get a distorted
  landscape ("this field is going well") and misplace your own work within it.
- **Reading only the recent.** Without the original you do not know **what the method was invented
  to solve**, which is where most misunderstandings of assumptions come from.
- **Copying the classification axis from an existing survey.** Then the survey is a summary, not a
  contribution.
- **Not verifying URLs.** Building this track's own paper list is the example: of 145
  candidates, one could not be verified and was **removed from the list**.
  Presenting an unverified link as verified makes the work irreproducible.

## Case study

Read the two must-read papers not for their **content** but for their **classification axis**, and
write a one-page note on each.

1. **Cadena et al., "Past, present, and future of SLAM: towards the robust-perception age" (2016)**
   — `survey`. §I-III.
   Questions: (a) what is the authors' classification axis (eras? problems? methods?). (b) what does
   that axis **hide** — are there differences it cannot compare? (c) name two things from their 2016
   "future" that happened and two that did not.
2. **Garrett et al., "Integrated task and motion planning" (2021, Annual Review)** — `survey`.
   Questions: (a) compare its axis (algorithmic categories) with Cadena et al.'s. Which **helps the
   reader judge** more? (b) is there anything in their "open problems" you disagree with?

**Additional case (optional)**: the
[Stanford CS326 syllabus](https://web.stanford.edu/class/cs326/syllabus.html) — 14 topics with
representative papers. As teaching material with **an axis already built**, work backwards to what
that axis was based on.

## Deliverable

**Deliverable 1 — a 30-paper classification table** (spreadsheet or Markdown table)
- 30 rows. Columns: id, title, first author, year, venue, **verified URL**, axis 1, axis 2, core
  claim, theoretical guarantee, mode of evaluation, limitations.
- Include all four kinds: originals ≥ 3, within two years ≥ 10, rebuttals/failure reports ≥ 2,
  surveys ≥ 1.
- **Open every URL and verify it.** Mark unverified entries `(unverified)` and report that
  proportion (aim for 0%).

**Deliverable 2 — a survey outline** (two pages)
- A section structure (5-8 sections) with **one sentence of claim** per section.
- The definition of your classification axes, and the justification of **at least one** axis
  differing from existing surveys.
- Two or three empty regions of the table identified, with a judgement on whether each is a
  research opportunity.

**Acceptance criteria**: all five rubric items at "pass" or above, at most 10% unverified URLs, and
someone else can **explain the landscape of the field from your table alone** (verified with one peer).

## Open problems

- **(Open) The volume of literature has outgrown human processing** — thousands of papers a year
  appear in robot learning. There is no method **guaranteeing completeness** of a systematic
  search, and the hallucination and omission risks of LLM-assisted search are not quantified. Even
  the procedure of this lesson uses an arbitrary cut-off ("two hops").
- **(Open) Criteria for evaluating a classification axis** — there is no objective criterion
  separating a good axis from a bad one. "Does it help the reader judge" is hard to evaluate and
  ends up resting on expert judgement.
- **(Open) The absence of negative results** — publication bias against failure reports and
  rebuttals distorts the landscape of a field. Almost no work measures the size of that bias in
  robotics (connecting to the open problems of `r1-robotics-evaluation-statistics` and
  `s4-evaluation-science`).

## Concept check

Run `rc quiz r1-literature-survey` (add `--lang en` for the English text). It is for concept
checking only; the real work is the deliverable.

The four items cover: the most effective way to search a field whose terminology changed; whether a
survey summary is an acceptable citation; which kinds of paper a 30-item list must include; and
what distinguishes a good survey from a summary.

## How to study this stage

1. **Choose a narrow topic (30 min)** — "SLAM" is far too broad. Narrow to something like "handling
   false positives in loop closure" so that 30 papers cover the landscape. Failing to narrow blurs
   everything that follows.
2. **Separate collecting from reading (4 hours)** — starting to read during step 2 biases the list.
   Gather 100-300 from titles and abstracts, then select.
3. **Hunt for rebuttals deliberately (1 hour)** — search titles like "X does not work",
   "revisiting X", "a critical look at X". This hour changes your understanding of the landscape
   more than any other.
4. **Watch the empty cells as you fill the table (3 hours)** — the purpose of the table is
   **finding patterns**, not tidying. An empty cell such as "no paper evaluates the case with
   contact" becomes a research question (the next lesson).
5. **Verify every URL (1 hour)** — the methods are those of
   `AUTHORING_RESEARCH_TRACK.md` §4 (arXiv API, Crossref, OpenAlex, proceedings pages).
   **This habit is basic to being a researcher.**
6. **Show a peer the table alone (30 min)** — if they can state the landscape of the field from the
   table with no explanation, you have succeeded. If not, the axis is wrong or a column is missing.

**Passing bar**: a 30-paper table (at most 10% unverified URLs, all four kinds) and a two-page
survey outline (at least one distinct axis) at "pass" or above on all five rubric items, plus the
landscape check with one peer.
