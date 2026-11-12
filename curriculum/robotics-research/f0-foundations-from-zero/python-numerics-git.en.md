---
id: f0-python-numerics-git
lang: en
title: Python, numerical computing and Git
summary: >-
  Gets you to the point of using numpy array operations and broadcasting, recognising
  floating-point error and condition numbers, and managing your work with Git. A guide lesson
  pointing at public documentation and free books.
objectives:
  - Use numpy array operations, broadcasting and slicing, and vectorise instead of looping.
  - Recognise the limits of floating point (machine epsilon, cancellation, accumulated error) and write verification tests.
  - Check derivatives and Jacobians by finite differences and choose the step size with a reason.
  - Solve linear systems, least squares and ODEs with scipy and verify the results.
  - Handle branches, commits and diffs in Git and undo work safely.
tags: [foundations, python, numpy, git, guide]
---

# Python, numerical computing and Git

## What you will be able to do

This is a **guide** lesson; pass it and skip.

Every lesson of the research track has a **reproduction task** whose acceptance criteria are
numerically decidable conditions. So this lesson is not optional: without being able to check
things in numpy, no lesson can be passed. In particular **verifying an analytic derivative by
finite differences** appears in almost every reproduction task from C1 through S5.

The bar is 5 of the 6 diagnostic questions.

## Self-diagnosis before starting

Run `rc quiz f0-python-numerics-git` (add `--lang en` for the English text). Score 5/6 or better
and skip to `f0-classical-mechanics`.

The six items cover: the shape produced by broadcasting; double-precision machine epsilon; the
optimal step size for a central difference; the safest way to solve least squares in numpy;
whether a numpy slice is a view; and the Git command that discards working-tree changes.

## Learning path

| Stage | Source | What you become able to do | Estimate |
|---|---|---|---|
| 1 | The Python and NumPy chapters of [Scientific Python Lectures](https://lectures.scientific-python.org/) | array creation, indexing, broadcasting, vectorisation, matplotlib | 12 h |
| 2 | The whole [NumPy user guide](https://numpy.org/doc/stable/user/) | dtypes, copies and views, ufuncs, advanced indexing | 8 h |
| 3 | The SciPy, optimization and debugging chapters of Scientific Python Lectures | solve/lstsq/svd, least_squares, solve_ivp, profiling | 10 h |
| 4 | [Pro Git](https://git-scm.com/book/en/v2) ch.1-3 and ch.7 | commits, branches, diffs, undoing, what rebase means | 6 h |
| 5 | Your own exercises (see item 3 below) | finite-difference verification, condition-number experiments, tracking accumulated error | 4 h |

About 40 hours. Shorter than the other F0 lessons, but **the most frequently used.**

## How to study this stage

1. **Diagnosis first (30 min)** — 5/6 or better and you are done.
2. **Type rather than read** — numpy documentation is not memorised by reading. The only way to
   learn broadcasting is to add arrays of varying shapes yourself.
3. **Do three numerical experiments yourself (4 hours)** — these are the moves the research track
   uses constantly:
   (a) derive the gradient of $f(x)=x^\top Mx$ analytically, compare with a central difference, and
   sweep the step $h$ from $10^{-1}$ to $10^{-12}$ to plot the **V-shaped error curve** (its
   minimum sits near $\epsilon^{1/3}$);
   (b) compare the error of `lstsq` against the normal equations as the condition number grows;
   (c) multiply a rotation matrix $10^5$ times, watch $\lVert R^\top R - I\rVert$ grow, and
   re-project with an SVD.
4. **Learn undoing first in Git (2 hours)** — this repository blocks destructive undo commands
   with a hook and uses WIP commits instead. Learn **safe undoing** (`git restore`, a WIP commit)
   before memorising the dangerous ones.
5. **Attach tests to your code (2 hours)** — the acceptance criteria of a reproduction task are
   ultimately asserts. Get into the habit of writing `assert np.allclose(a, b, atol=1e-9)`.
6. **Rewrite with vectorisation (2 hours)** — convert loop-based code into array operations and
   time it. Reproduction tasks ask for $10^4$-$10^5$ samples, so vectorisation is necessary.

**Passing bar**: 5 of 6 diagnostic questions, and all three experiments of item 3 done, with the
V-curve, the condition-number comparison and the re-projection result as plots you hold.
