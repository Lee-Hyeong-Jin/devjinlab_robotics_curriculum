---
id: f0-calculus-multivariable
lang: en
title: Calculus II - multivariable
summary: >-
  Gets you to the point of computing partial derivatives, gradients, the chain rule, multiple
  integrals, divergence and curl, and explaining the geometric meaning of the gradient. A guide
  lesson pointing at MIT 18.02; pass the diagnosis and skip it.
objectives:
  - Compute partial derivatives and gradients and explain why the gradient is the direction of steepest increase.
  - Use the multivariable chain rule and Jacobian matrices.
  - Approximate a multivariable function by first- and second-order Taylor expansion and classify critical points with the Hessian.
  - Solve constrained optimization problems with Lagrange multipliers.
  - Compute multiple integrals and changes of variable (the Jacobian determinant).
tags: [foundations, calculus, guide]
---

# Calculus II - multivariable

## What you will be able to do

This is a **guide** lesson; pass it and skip.

Put in the terms the research track uses: **without gradients and Jacobians there is no
optimization and no estimation.** Every derivation in C4 (optimal control), every Jacobian in C5
(state estimation) and the numerical-derivative checks of R0 assume this lesson. What matters most
is handling **a Jacobian as "the matrix collecting the partial derivatives"** fluently, and
**classifying critical points with the Hessian**.

The bar is 5 of the 6 diagnostic questions.

## Self-diagnosis before starting

Run `rc quiz f0-calculus-multivariable` (add `--lang en` for the English text). Score 5/6 or
better and skip to `f0-differential-equations`.

The six items cover: the gradient of a quadratic form; the geometric meaning of the gradient; the
shape convention of a Jacobian; classifying a saddle point with the Hessian; the Lagrange
multiplier condition; and the Jacobian determinant in a change of variables.

## Learning path

**Primary source**: [MIT 18.02 Multivariable Calculus (Fall 2007)](https://ocw.mit.edu/courses/18-02-multivariable-calculus-fall-2007/).

| Stage | 18.02 scope | What you become able to do | Estimate |
|---|---|---|---|
| 1 | Vectors, matrices, parametric curves (L1-L6) | dot and cross products, planes and lines, velocity and acceleration | 12 h |
| 2 | Partial derivatives and gradients (L8-L13) | gradients, directional derivatives, the chain rule, Jacobians, Lagrange multipliers | 22 h |
| 3 | Multiple integrals (L16-L21) | double and triple integrals, polar and spherical coordinates, change of variables | 18 h |
| 4 | Vector fields (L22-L31) | line integrals, divergence and curl, Green's and Stokes' theorems | 18 h |

About 70 hours. **Stage 2 is the heart of this lesson** and what the research track uses most.
Stage 4 is used less in robotics but is needed to read fluid and electromagnetic literature — if
time is short it can be deferred.

## How to study this stage

1. **Diagnosis first (40 min)** — 5/6 or better and you are done.
2. **Concentrate your time on stage 2** — gradients, Jacobians and the chain rule are used daily
   later. Practise them twice as much as the rest.
3. **Check every gradient by finite differences (each stage)** — compare the $\nabla f$ you derived
   with a numpy central difference. **This habit is the basic move of every reproduction task in
   the research track**, and R0 goes as far as choosing the step size.
4. **Write the shape of a Jacobian first** — note "outputs × inputs" before computing. It is the
   cheapest way to prevent transpose mistakes.
5. **Understand Lagrange multipliers geometrically (2 hours)** — draw the picture of level sets
   touching. Pontryagin's maximum principle in C4 and constrained dynamics in C2 are extensions of
   that same picture.
6. **Judge by past exams** — two 18.02 past papers under time at 80% or better.

**Passing bar**: 5 of 6 diagnostic questions, 80% on an 18.02 past paper, and the ability to write
code that computes a Jacobian of an arbitrary $g:\mathbb{R}^n\to\mathbb{R}^m$ by hand and checks
it by finite differences.
