---
id: f0-classical-mechanics
lang: en
title: Classical mechanics
summary: >-
  Gets you to the point of writing equations of motion from Newton's laws and handling energy and
  momentum conservation and rotational motion (moment of inertia, torque, angular momentum). A
  guide lesson pointing at MIT 8.01SC.
objectives:
  - Draw a free-body diagram and write Newton's equations of motion.
  - Solve motion problems with the work-energy theorem and energy conservation.
  - Handle momentum, impulse and elastic and inelastic collisions.
  - Describe rotational motion with moment of inertia, torque and angular momentum.
  - Decompose and solve planar rigid-body motion (translation plus rotation).
tags: [foundations, mechanics, physics, guide]
---

# Classical mechanics

## What you will be able to do

This is a **guide** lesson; pass it and skip.

**A robot is a collection of rigid bodies and its motion is mechanics.** C2 (multibody dynamics)
is the direct continuation of this lesson, and C3 and C4 (control) manipulate those equations of
motion. What matters most is **moment of inertia and angular momentum**, and **the energy view
that is the entrance to Lagrangian mechanics**. Robotics literature uses both Newton-Euler and
Lagrange, so seeing both views here pays off.

The bar is 5 of the 6 diagnostic questions.

## Self-diagnosis before starting

Run `rc quiz f0-classical-mechanics` (add `--lang en` for the English text). Score 5/6 or better
and skip to `f0-proofs-math-maturity`.

The six items cover: the moment of inertia of a uniform rod; the parallel-axis theorem;
acceleration on a frictionless incline; what is conserved when the external torque vanishes;
whether kinetic energy is conserved in an inelastic collision; and the small-amplitude period of a
simple pendulum.

## Learning path

**Primary source**: [MIT 8.01SC Classical Mechanics (Fall 2016)](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/),
with lecture videos, problem sets 1-12 and an online textbook.

| Stage | 8.01 scope | What you become able to do | Estimate |
|---|---|---|---|
| 1 | Kinematics and Newton's laws | free-body diagrams, equations of motion, friction, circular motion | 20 h |
| 2 | Work and energy | the work-energy theorem, conservative forces and potential energy, energy conservation | 15 h |
| 3 | Momentum and collisions | impulse, centre of mass, elastic and inelastic collisions | 12 h |
| 4 | Rotational motion | moment of inertia, torque, angular momentum, the parallel-axis theorem, planar rigid-body motion | 23 h |

About 70 hours. **Stage 4 connects directly to robotics** — if time is short, prioritise stages 1 and 4.

## How to study this stage

1. **Diagnosis first (40 min)** — 5/6 or better and you are done.
2. **Always draw the free-body diagram** — 90% of mechanics problems fall out once the picture is
   right. The habit of skipping it and writing equations first comes back later as sign errors.
3. **Solve the same problem two ways (each stage)** — once with Newton (forces and acceleration),
   once with energy (conservation). C2 uses both Newton-Euler and Lagrange, so this habit carries over.
4. **Read stage 4 thinking about robots (23 hours)** — moment of inertia becomes the inertia matrix
   of C2, the parallel-axis theorem becomes the frame transformation of spatial inertia, and
   angular momentum leads to centroidal dynamics (S3).
5. **Integrate a pendulum numerically (2 hours)** — compare the linearised solution with the
   nonlinear numerical one and watch the period change as the amplitude grows. This is where
   `f0-differential-equations` joins up.
6. **Judge by the problem sets** — work 8.01SC problem sets 1-12 at 80% or better.

**Passing bar**: 5 of 6 diagnostic questions, 80% on the 8.01SC problem sets, and the ability to
go from free-body diagram to equations of motion to numerical integration unaided for any planar
rigid-body problem.
