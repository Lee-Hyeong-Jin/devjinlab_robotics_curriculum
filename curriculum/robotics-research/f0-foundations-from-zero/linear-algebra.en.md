---
id: f0-linear-algebra
lang: en
title: Linear algebra
summary: >-
  Gets you to the point of computing elimination, subspaces, the four fundamental subspaces,
  eigenvalues and the SVD by hand and saying what they mean. A guide lesson pointing at MIT 18.06
  (Strang); pass the diagnosis and skip it.
objectives:
  - Solve linear systems by elimination and decide existence and uniqueness from the rank.
  - Explain the dimension relations among the four fundamental subspaces.
  - Derive orthogonal projection and the least-squares solution via the normal equations.
  - Compute eigenvalues and eigenvectors and state the properties of symmetric matrices.
  - Explain the structure of the SVD and compute rank and condition number from singular values.
tags: [foundations, linear-algebra, guide]
---

# Linear algebra

## What you will be able to do

This is a **guide** lesson; pass it and skip.

**It is the mathematics robotics uses first and most.** Rotation matrices, Jacobians, least-squares
estimation, covariance, normal equations, condition numbers — nearly every lesson of the research
track is written in the language of linear algebra. That is why it comes **before** multivariable
calculus in F0. In particular **the SVD and the condition number** are used immediately in R0 and
C5, so "I have heard of them" is not enough.

The bar is 5 of the 6 diagnostic questions.

## Self-diagnosis before starting

Run `rc quiz f0-linear-algebra` (add `--lang en` for the English text). Score 5/6 or better and
skip to `f0-calculus-multivariable`.

The six items cover: the 2-norm condition number of a diagonal matrix; the rank-nullity theorem;
the normal equations of least squares; which properties always hold for a real symmetric matrix;
which columns of an SVD span the column space; and why forming $A^\top A$ is numerically worse
than QR.

## Learning path

**Primary source**: [MIT 18.06 Linear Algebra (Spring 2010, Strang)](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/),
with lecture videos, problem sets and solutions, and past exams with solutions all public.

| Stage | 18.06 scope | What you become able to do | Estimate |
|---|---|---|---|
| 1 | Elimination and $Ax=b$ (L1-L8) | LU factorisation, transposes and inverses, existence and uniqueness | 20 h |
| 2 | Vector spaces and the four subspaces (L9-L14) | rank, bases and dimension, the rank-nullity theorem | 18 h |
| 3 | Orthogonality and least squares (L15-L17) | orthogonal projection, normal equations, Gram-Schmidt and QR | 15 h |
| 4 | Determinants and eigenvalues (L18-L26) | eigenvalues and eigenvectors, diagonalisation, symmetric matrices and definiteness | 20 h |
| 5 | SVD and applications (L29-L33) | the SVD, pseudo-inverse, condition number, principal components | 7 h |

About 80 hours. **Do not skip stages 4 and 5** — eigenvalues and the SVD are what robotics uses most.

## How to study this stage

1. **Diagnosis first (40 min)** — 5/6 or better and you are done. Otherwise see which stage your
   missed questions belong to and start there.
2. **Strang's lectures explain the "why" (2-3 hours a day)** — they are about geometric meaning
   rather than memorising formulas. Work one video plus its problem set as a unit.
3. **Hand computation, then check with numpy (1 hour per stage)** — solve small matrices by hand
   and confirm `numpy.linalg` agrees. That habit is the basic skill behind every reproduction task.
4. **Draw the four subspaces on one page (1 hour)** — at the end of stage 2, put the dimension
   relations of the column, null, row and left-null spaces on a single sheet. That picture is used
   directly later for gauge freedom and for diagnosing rank deficiency.
5. **Get a feel for the SVD in code (2 hours)** — print the singular values of random matrices and
   watch the smallest one approach zero as you make a column nearly dependent. That is when the
   condition number stops being a formula and becomes a quantity you can sense.
6. **Judge by past exams** — sit three 18.06 past papers under time and score 80% or better.

**Passing bar**: 5 of 6 diagnostic questions, a self-marked 80% on the 18.06 final, and the
ability to write numpy code computing rank and condition number from an SVD unaided.
