---
id: f0-probability-statistics
lang: en
title: Probability and statistics
summary: >-
  Gets you to the point of using conditional probability, Bayes' theorem, expectation, variance,
  the law of large numbers and the central limit theorem, and computing estimates and confidence
  intervals. A guide lesson pointing at MIT 18.05, with 6.041 if you want lecture videos.
objectives:
  - Use conditional probability and Bayes' theorem and distinguish prior from posterior.
  - Compute expectation, variance and covariance and write how they change under a linear transformation.
  - State the properties of the Gaussian distribution (linear transformation, marginalisation, conditioning).
  - Explain the difference between the law of large numbers and the central limit theorem.
  - Compute point estimates and confidence intervals and say what a hypothesis test means.
tags: [foundations, probability, statistics, guide]
---

# Probability and statistics

## What you will be able to do

This is a **guide** lesson; pass it and skip.

In robotics **sensors give noise and estimation is a probability problem.** All of C5 (state
estimation), the estimation theory of R0, the learning theory of C8 and the evaluation and
statistics of R1 assume this lesson. In particular the three Gaussian properties (**linear
transformation, marginalisation, conditioning**) and **Bayes' theorem** are used verbatim when
deriving the Kalman filter and factor graphs.

The bar is 5 of the 6 diagnostic questions.

## Self-diagnosis before starting

Run `rc quiz f0-probability-statistics` (add `--lang en` for the English text). Score 5/6 or
better and skip to `f0-python-numerics-git`.

The six items cover: Bayes' theorem with a low prior; the covariance of a linearly transformed
Gaussian; the law of large numbers versus the central limit theorem; marginalising a joint
Gaussian in covariance versus information form; the width of a confidence interval; and whether
zero correlation implies independence.

## Learning path

**Primary**: [MIT 18.05 (Spring 2022)](https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/) —
notes, problem sets and exams with solutions (no videos).
**If you want videos**: [MIT 6.041 (Fall 2010)](https://ocw.mit.edu/courses/6-041-probabilistic-systems-analysis-and-applied-probability-fall-2010/) —
lecture videos, problem sets and exams with solutions; being engineering-oriented, it is closer to robotics.

| Stage | Scope | What you become able to do | Estimate |
|---|---|---|---|
| 1 | Probability basics | sample spaces, conditional probability, independence, Bayes' theorem | 15 h |
| 2 | Random variables | distributions, expectation and variance, covariance, change of variables | 18 h |
| 3 | The multivariate Gaussian | linear transformation, marginalisation, conditioning, covariance versus information form | 15 h |
| 4 | Limit theorems and estimation | the law of large numbers, the central limit theorem, MLE, confidence intervals, hypothesis tests | 22 h |

About 70 hours. **Do stage 3 most carefully** — every derivation in C5 stands on those three properties.

## How to study this stage

1. **Diagnosis first (40 min)** — 5/6 or better and you are done.
2. **Confirm every theorem by Monte Carlo (each stage)** — reproduce Bayes' theorem, the central
   limit theorem and the coverage of a confidence interval in numpy. "I read the theorem" and "I
   watched the theorem be true" are different things.
3. **Do the block computations of stage 3 by hand (15 hours)** — derive the marginal and the
   conditional of a 2×2 block Gaussian. Do it in **both** covariance and information form; the
   difference is the heart of the sparsity discussion in C5.
4. **Remember "uncorrelated ≠ independent" by its counterexample (1 hour)** — check the $y=x^2$
   example numerically. You will then see why the Gaussian exception is special.
5. **Invert a confidence interval (2 hours)** — compute "how many trials are needed to detect a
   5-point difference in success rate at 95% confidence". The evaluation design of R1 and S4 is
   that computation.
6. **Judge by past exams** — two 18.05 or two 6.041 past papers at 80% or better.

**Passing bar**: 5 of 6 diagnostic questions, 80% on a past paper, and the ability to write code
confirming the central limit theorem and confidence-interval coverage by Monte Carlo.
