---
id: f0-calculus-single-variable
lang: en
title: Calculus I - single variable
summary: >-
  Gets you to the point of computing limits, derivatives, integrals and Taylor series, and solving
  optimization problems by differentiation. A guide lesson pointing at MIT 18.01 (lecture videos,
  notes and exams with solutions all public); pass the diagnosis and skip it.
objectives:
  - State the definitions of limit and continuity and differentiate the elementary functions.
  - Apply the chain, product and quotient rules and implicit differentiation.
  - Use the fundamental theorem of calculus and integrate by substitution and by parts.
  - Approximate a function by its Taylor series and state the order of the error term.
  - Solve one-variable optimization problems with derivatives and classify critical points.
tags: [foundations, calculus, guide]
---

# Calculus I - single variable

## What you will be able to do

This is a **guide** lesson: it writes no new content, points at a verified public course, and uses
a diagnosis to decide whether you can skip it.

Single-variable calculus is rarely used directly in robotics. But **everything later assumes it**:
multivariable calculus (gradients, Jacobians), differential equations (how robots move),
optimization (all of control and estimation), probability (expectations and integrals). Get stuck
here and every later stage is blocked.

The bar is 5 of the 6 diagnostic questions.

## Self-diagnosis before starting

Run `rc quiz f0-calculus-single-variable` (add `--lang en` for the English text). Score 5/6 or
better and skip this lesson, going to `f0-linear-algebra`. With 4 or fewer, follow the learning path.

The six items cover: the product rule on a polynomial times an exponential; integration by parts;
the Taylor series of $\sin x$; classifying critical points with the second derivative; whether
continuity implies differentiability; and the limit of $\sin x / x$.

## Learning path

**Primary source**: [MIT 18.01 Single Variable Calculus (Fall 2006)](https://ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006/).
Lecture videos, lecture notes and past exams **with solutions** are all public, so it can be done alone.

| Stage | 18.01 scope | What you become able to do | Estimate |
|---|---|---|---|
| 1 | Differentiation (Unit 1) | limits, continuity, the definition of the derivative, product/quotient/chain rules, implicit differentiation | 20 h |
| 2 | Applications of differentiation (Unit 2) | critical points and optimization, linear approximation, related rates, the mean value theorem | 15 h |
| 3 | Integration (Unit 3) | the fundamental theorem, substitution and parts, partial fractions, areas and volumes | 20 h |
| 4 | Series and approximation (Units 4-5) | Taylor series and the error term, improper integrals, polar coordinates | 15 h |

About 70 hours in total. **At the end of each stage, sit a past exam under time and mark it** —
watching lectures alone produces the illusion of understanding.

## How to study this stage

1. **Take the diagnosis first (40 min)** — 5/6 or better and you are done with this lesson.
   Otherwise see which stage your missed questions belong to and start there; you do not have to
   watch everything.
2. **One video plus five problems as a unit (2-3 hours a day)** — watching videos back to back
   leaves nothing behind. 18.01 attaches a problem set to each video, so keeping that pairing is
   enough.
3. **Write by hand** — calculus is a motor skill. This stage is about raising your **speed of
   application**, not memorising derivative formulas, so do not use a calculator or a symbolic tool.
4. **When stuck, read the same topic in a different voice** (Paul's Online Math Notes). One
   explanation failing is common. But **do not switch your primary source** — following one course
   to the end matters.
5. **Judge passing by past exams (2 hours per stage)** — sit the 18.01 midterms and final under
   time and mark them against the published solutions. Below 80%, redo that stage.
6. **Check the link to the next lesson (30 min)** — after this comes `f0-linear-algebra`. Linear
   algebra is placed before multivariable calculus because it is what robotics uses first and most.

**Passing bar**: 5 of 6 diagnostic questions, and a self-marked score of 80% or better on the
18.01 final.
