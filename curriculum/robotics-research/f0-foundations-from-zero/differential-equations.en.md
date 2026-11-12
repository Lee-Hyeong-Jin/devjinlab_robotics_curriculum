---
id: f0-differential-equations
lang: en
title: Differential equations
summary: >-
  Gets you to the point of solving first- and second-order ODEs, reading the solution of a linear
  system from its eigenvalues, and explaining why numerical integrators are needed. A guide lesson
  pointing at MIT 18.03; pass the diagnosis and skip it.
objectives:
  - Solve first-order linear and separable ODEs and use an integrating factor.
  - Find the general solution of a second-order constant-coefficient ODE from its characteristic equation and classify the damping.
  - Write the solution of a linear system of ODEs with the matrix exponential and eigenvalues.
  - Classify equilibria in the phase plane and decide stability.
  - Say why a numerical integrator is needed when no closed form exists, and what stiffness means.
tags: [foundations, differential-equations, guide]
---

# Differential equations

## What you will be able to do

This is a **guide** lesson; pass it and skip.

**A robot's motion is a differential equation.** $\dot{x} = f(x,u)$ is the starting point of the
whole research track: C2 (dynamics) is how to write that $f$, C3 and C4 (control) how to choose
$u$, and C5 (estimation) how to recover $x$ from noisy observations. In particular **reading the
solution of a linear system from its eigenvalues** (stability) and **the matrix exponential** lead
straight into the exponential map of C1, Lyapunov stability in C3 and LQR in C4.

The bar is 5 of the 6 diagnostic questions.

## Self-diagnosis before starting

Run `rc quiz f0-differential-equations` (add `--lang en` for the English text). Score 5/6 or
better and skip to `f0-probability-statistics`.

The six items cover: the solution of $\dot{x}=ax$; classifying the damping of a second-order ODE;
the stability condition for $\dot{x}=Ax$; the integrating factor of a first-order linear ODE;
forward Euler on a stiff problem; and classifying an equilibrium from the signs of its Jacobian's
eigenvalues.

## Learning path

**Primary source**: [MIT 18.03 Differential Equations (Spring 2010)](https://ocw.mit.edu/courses/18-03-differential-equations-spring-2010/),
with lecture videos, notes, and problem sets with solutions.

| Stage | 18.03 scope | What you become able to do | Estimate |
|---|---|---|---|
| 1 | First-order ODEs | separable equations, integrating factors, direction fields, existence and uniqueness | 12 h |
| 2 | Second-order constant coefficients | characteristic equations, damping classification, resonance and frequency response | 15 h |
| 3 | Systems of ODEs and matrices | the matrix exponential, writing solutions from eigenvalues, the phase plane | 20 h |
| 4 | Nonlinear systems and numerics | classifying equilibria, linearisation, numerical integrators and stiffness | 13 h |

About 60 hours. **Stage 3 connects most directly to the research track** (matrix exponential → C1,
stability → C3).

## How to study this stage

1. **Diagnosis first (40 min)** — 5/6 or better and you are done.
2. **Always view the closed form and the numerical solution together (each stage)** — overlay your
   hand solution with the output of `scipy.integrate.solve_ivp`. Where they diverge (step size,
   stiffness) leads into the integrator lesson of R0.
3. **Do stage 3 alongside linear algebra (20 hours)** — compute $e^{At}$ by eigendecomposition.
   This is where putting `f0-linear-algebra` first pays off.
4. **Draw phase planes (3 hours)** — plot the vector field of a two-dimensional nonlinear system
   with matplotlib and zoom in around the equilibria. The limit cycles of S3 (legged locomotion)
   are an extension of that picture.
5. **Create stiffness yourself (2 hours)** — integrate a linear system with eigenvalues $-1$ and
   $-1000$ by forward Euler and shrink the step until it becomes stable. The answer to "why do
   implicit integrators exist" arrives as a number.
6. **Judge by the problem sets** — mark the full 18.03 problem sets against the solutions at 80% or better.

**Passing bar**: 5 of 6 diagnostic questions, 80% on the 18.03 problem sets, and the ability to
write code that expresses the solution of $\dot{x}=Ax$ via eigenvalues and compares it with
numerical integration.
