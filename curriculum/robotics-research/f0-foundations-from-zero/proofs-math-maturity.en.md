---
id: f0-proofs-math-maturity
lang: en
title: Reading and writing proofs (mathematical maturity)
summary: >-
  Gets you to the point of reading definition-theorem-proof structure and proving simple
  statements yourself by induction, contraposition and contradiction. A guide lesson pointing at
  Hammack's Book of Proof (free full text) and MIT 6.042J.
objectives:
  - Distinguish the roles of definition, theorem, lemma and corollary and read the structure of a proof.
  - Choose appropriately among direct proof, contraposition, contradiction and counterexample.
  - Prove statements by mathematical induction, including strong induction.
  - Use universal and existential quantifiers precisely and form their negations.
  - Find the gaps in a proof and point out what more is needed.
tags: [foundations, proofs, mathematical-maturity, guide]
---

# Reading and writing proofs (mathematical maturity)

## What you will be able to do

This is a **guide** lesson; pass it and skip.

**It is the most important lesson in F0 and the most often skipped.** The research-track lesson
standard requires depth D2 (a full derivation) or better in every lesson, and a proof sketch for
every D3 result. If you cannot **read** a proof you cannot assess the guarantees of a must-read
paper, and if you cannot **write** one you cannot solve the proof-type problems in a problem set.

It must be finished **before** meeting the D3 results of R0 (quadratic convergence of Newton's
method, the Cramér-Rao bound, KKT). It sits last in F0 because it is more efficient after you have
**read** proofs in the earlier subjects.

The bar is 5 of the 6 diagnostic questions.

## Self-diagnosis before starting

Run `rc quiz f0-proofs-math-maturity` (add `--lang en` for the English text). Score 5/6 or better
and you are done with F0; go on to the `robotics-expert` course or the R0 mathematics bridge.

The six items cover: negating a universally quantified implication; choosing contraposition;
what distinguishes strong induction; whether the absence of a counterexample proves anything; the
role of a lemma; and the name of the technique used for the irrationality of $\sqrt{2}$.

## Learning path

**Primary**: [Hammack, *Book of Proof* (free full text)](https://richardhammack.github.io/BookOfProof/) —
the 14 chapters of Parts I-IV with selected solutions.
**Alongside**: [MIT 6.042J (Fall 2010)](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/) —
lecture videos and past exams with solutions; particularly good training in **writing** proofs.

| Stage | Scope | What you become able to do | Estimate |
|---|---|---|---|
| 1 | Book of Proof Part I (sets and logic) | quantifiers, implication and contraposition, forming negations | 10 h |
| 2 | Part II (proof techniques) | direct proof, contraposition, contradiction, case analysis | 14 h |
| 3 | Part III (induction, relations, functions) | mathematical and strong induction, equivalence relations, injections and surjections | 14 h |
| 4 | Writing practice with 6.042J | training by **writing** proofs yourself and having them marked | 12 h |

About 50 hours. **Do not skip stage 4** — reading and writing are different skills, and the
research track demands writing.

## How to study this stage

1. **Diagnosis first (40 min)** — 5/6 or better and you are done. If you missed q1 (forming
   negations) or q4 (absence of a counterexample), you definitely need this lesson.
2. **Close the book and rewrite the proof (every chapter)** — the feeling of having understood a
   proof you just read is a trap. You have understood it only when you can rewrite it on a blank
   page. That method is exactly the "derive it on a blank page" passing bar of the research-track lessons.
3. **Choose the strategy first** — before writing, note "direct? contraposition? contradiction?
   induction?". The "one-line strategy" required by the proof sketches of the lesson standard is
   this habit.
4. **Practise finding gaps (2 hours per stage)** — read deliberately flawed proofs and find what
   is wrong. 6.042J past papers contain such items. The ability to assess a paper's guarantees
   comes from here.
5. **Write quantifiers symbolically (3 hours)** — translate natural-language statements into
   $\forall/\exists$ and form their negations. The goal is fluency with structures like "for every
   $\epsilon$ there exists a $\delta$ such that...".
6. **Show your proofs to someone else (stage 4)** — work 6.042J past papers and compare your
   **structure** with the solutions. Even when the answer is right, ask why the structure differs.

**Passing bar**: 5 of 6 diagnostic questions, 80% on the selected-solution problems of Book of
Proof Parts I-III, and proof items from 6.042J past papers written yourself whose structure matches
the published solutions.
