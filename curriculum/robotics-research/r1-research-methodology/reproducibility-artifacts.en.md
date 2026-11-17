---
title: Reproducibility and Artifacts
summary: >-
  Pin the environment and control randomness so that someone else can re-run your work. The
  deliverable is a reproducible repository (seeds, environment, scripts) and an artifact checklist.
objectives:
  - Pin an environment with a lockfile and a container so a third party gets the same result.
  - Separate and control random seeds from nondeterministic operations, and state what cannot be controlled.
  - Write a script that regenerates every table and figure with one command.
  - Decide the release scope and licence of code, data and models, and freeze them with a DOI.
  - Audit your own repository against artifact-evaluation criteria and fix what is missing.
---

# Reproducibility and Artifacts

## Goals

**"It works on my machine" is not a research result.** This lesson trains the work that lets a
third party take your repository and regenerate the paper's tables and figures with one command.

Reproducibility is a **skill**, not goodwill: environment pinning, randomness control, data
provenance, output automation, licensing and DOIs each have a concrete procedure. And it is for
**yourself in six months** before it is for anyone else — a researcher with an irreproducible
repository cannot answer a reviewer's request for one more experiment.

Deliverable: **a reproducible repository plus an artifact checklist**.

## Self-diagnosis before you start

| Question | If you can | If you cannot |
|---|---|---|
| Can you reproduce your own experiment from six months ago as it was? | Start at step 3 | Start at step 1 — that is why this lesson exists |
| Can you state the difference between a lockfile and `requirements.txt`? | Move fast through step 1 | Read uv's "Locking and syncing" first |
| Do two runs with the same seed on a GPU give bit-identical results? | Move fast through step 2 | Read step 2 closely — the answer is usually no |
| Do you know your own code's licence? | Move fast through step 5 | Read step 5 — a release without a licence grants no permission |

## Procedure

**Step 1 — pin the environment (2 h).** Pin all three layers. *Dependencies*: commit the lockfile
(`uv.lock`) and run with `uv run --locked` so a stale lockfile **fails**; a range specifier (`>=`)
in `requirements.txt` is not a pin. *System*: record the OS, CUDA and driver level in a container
definition (`Dockerfile`), and pin images by digest (`@sha256:...`). *Hardware*: put the GPU model,
CPU and RAM in the README — numerical results can depend on them.

**Step 2 — control randomness and nondeterminism (2 h).** These are two different problems.
*Seeds*: set Python, NumPy and framework seeds **in one function** and record the seed used in the
result file. Fixing a seed and **running many seeds** are not in conflict — fix the seed list
(e.g. 0–9) in config and run all of them. *Nondeterministic operations*: GPU atomic accumulation,
nondeterministic kernels and parallel data-loader ordering are not covered by seeds. Turn on a
deterministic mode if you can (there is a performance cost); if you cannot, state that **bit-level
reproduction is not guaranteed, only statistical reproduction**. Real robots are **nondeterministic
in principle** (friction, temperature, battery), so there the unit of reproducibility is not a run
but a **distribution**: reproduce with a trial count and a confidence interval (previous lesson).

**Step 3 — automate output generation (3 h).** The target is **one command**:

```
make all     # or python -m scripts.reproduce --all
```

Fix the path from raw data through intermediates to tables and figures in scripts — a table pasted
into a spreadsheet by hand is not reproducible. Map **each table and figure to one generating
script** (`figures/fig3.py` → `fig3.pdf`). For expensive experiments provide **two paths**: full
reproduction (`--full`, days) and a smoke path (`--smoke`, 10 minutes); without the smoke path
nobody checks. Ship cached intermediates, but ship the script that builds them from raw data too.

**Step 4 — record data and model provenance (2 h).** A dataset name is not enough: record the
version, download date, preprocessing script and the split definition file. For public data give
the URL and a checksum; for private data state **why it cannot be released and what the substitute
is**. For pretrained weights record the source and licence — weight licences can differ from code
licences.

**Step 5 — decide licence and release scope (1.5 h).** **A public repository without a licence file
is code nobody has legal permission to use.** Default to a permissive licence for code (Apache-2.0,
MIT) and a CC BY family licence for data and documents. Check your institution's rules and
co-authors' consent first. If release is restricted (company data, safety), state **what you cannot
release and why** in the paper — better than silence.

**Step 6 — freeze with a DOI and audit with a checklist (1.5 h).** Get a DOI for a snapshot of the
repository (e.g. Zenodo's GitHub integration) so the paper cites a **specific commit**. Then audit
yourself: (a) does it install, (b) does the smoke path finish in 10 minutes, (c) do the tables and
figures regenerate, (d) do the numbers match the paper, (e) are licence and citation information
present? **The surest audit is a colleague running it in a clean environment.**

## Grading criteria

| Item | Pass | Strong |
|---|---|---|
| Environment pinning | A lockfile is committed | Container digest pin + `--locked` execution + hardware stated |
| Randomness control | Seeds are set and recorded | Nondeterministic operations isolated and declared; reported as a multi-seed distribution |
| Output automation | Scripts generate the main results | 1:1 script per table/figure + a 10-minute smoke path |
| Data provenance | Dataset and splits are stated | Version, checksum, preprocessing script and reasons for non-release recorded |
| Licence | A LICENSE file exists | Code, data and weight licences and their constraints recorded separately |
| External validation | You reproduced it in a clean environment | A third party reproduced it from the repository alone, with the log published |

## Failure cases

- **Only a `requirements.txt`, no lockfile.** Six months later a newer version installs and the result shifts.
- **Believing a fixed seed means reproducibility.** GPU nondeterminism is outside the seed.
- **Building tables by hand.** One changed number means redoing everything, unrecorded.
- **No smoke path.** If full reproduction takes three days, neither reviewers nor successors check it.
- **No LICENSE.** Released, but nobody can legally use it.
- **Hard-coding the data split without saving it as a file.** A changed split breaks every comparison.
- **Writing "code available upon request."** Response rates are low and it disappears when the author moves.
- **Submitting a real-robot result from a single run.** Hardware must be reproduced as a distribution.

## Case study

**One required paper plus an audit of two public repositories.**

**Pineau et al. (2021)** — `standard`, the report from the NeurIPS 2019 reproducibility program.
Questions: (a) What does the reproducibility checklist require, and which failure does each item
prevent? (b) What reasons do the authors give for the rise in code submission **even though it was
not mandatory**? (c) What reproducibility measures did they collect, and what are their limits?
(d) Applied to **real-robot robotics**, which additional items would the checklist need?

**Repository audit**: take the public repositories of two well-known papers in your field and score
them on the six grading items. Actually install them and attempt the smoke run, recording **where
you got stuck and how long it took**. That experience changes how you design your own repository.
(Pick one that was easy to reproduce and one that was hard.)

## Deliverables

**Deliverable 1 — a reproducible repository**: lockfile, container definition, seed-setting
function, output-generating scripts, LICENSE and README. The README gives the one-line install, the
smoke command (10 min), the full command and its expected runtime, the hardware, and how to obtain
the data. **Acceptance**: (a) installation through smoke run succeeds in a clean virtual
environment **from the documentation alone**, (b) the smoke run finishes within 10 minutes, (c) one
main table and one figure are regenerated by script and the values match.

**Deliverable 2 — artifact checklist** (1–2 pages): a self-assessment of your repository against
the six grading items, with **evidence** (commands, log paths) for each. For items you fail, state
**why you cannot pass and what you guarantee instead** (e.g. no bit-level reproduction → a 10-seed
distribution is reproduced).

**Deliverable 3 — cross-reproduction log** (1 page): the record of trying to reproduce two other
repositories — where you got stuck, resolved or gave up, how long it took — plus **three changes you
made to your own repository** as a result.

**Acceptance**: all three deliverables pass or better on the grading criteria, and **a third party
(one colleague) reproduced Deliverable 1 in a clean environment**.

## Open problems

- **(Open) The unit of reproducibility for real robots** — with different hardware and environments
  the same code does not give the same result. There is no agreement on what counts as "reproduced"
  (matching distributions? matching rankings? matching trends?).
- **(Open) The cost of reproducing large models** — results that take thousands of GPU-hours to
  train cannot be verified by reproduction in principle. Alternatives such as partial reproduction
  or verifiable training logs are not established.
- **(Open) Incentives for artifact evaluation** — artifact verification is labour-intensive and
  poorly rewarded. Building a sustainable verification system in robotics venues is an open problem.

## Concept check

Take it with `rc quiz r1-reproducibility-artifacts`. It is a concept check only.

## How to study this stage

1. **Reproduce your own past experiment (2 h)** — rebuild a result from six months ago. Where you
   get stuck is your personal task list for this lesson.
2. **Pin the environment first (2 h)** — lockfile and container. This alone removes a large share of
   reproduction failures.
3. **Write one seed function (1 h)** — set every source of randomness in one place and record the
   seed in the result. Then measure nondeterminism by **running the same seed twice**.
4. **Bind tables and figures to scripts (3 h)** — move them one at a time into `fig3.py`-style
   scripts. Nothing changes your paper-revision speed more.
5. **Reproduce two other repositories (110 min)** — you cannot write a README without having been
   the reproducer. Record where you got stuck and fold it back into your own repository.
6. **Have a colleague run it in a clean environment (1 h)** — the final check. Your own machine
   carries unrecorded settings, so self-validation is always optimistic.

**Bar to pass**: the repository, checklist and cross-reproduction log reach pass or better on all
six grading items, and a third party succeeded at the smoke path within 10 minutes from the
documentation alone.
