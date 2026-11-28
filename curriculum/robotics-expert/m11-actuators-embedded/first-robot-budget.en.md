---
id: m11-first-robot-budget
lang: en
title: "Optional: your first robot on a small budget"
summary: An optional lesson for those who want to build. A differential-drive robot with two encoders and an IMU, in three budget tiers, described by kind of part rather than by product; and three experiments that run the PID and odometry of M3 on real motors and record what differed from the NumPy examples. The course can be completed without hardware.
objectives:
  - List the parts a differential-drive robot needs by kind, and say what each budget tier adds.
  - Name the checks to make before buying, that voltages, currents, logic levels and encoder resolution fit together.
  - Compare the results of a speed-loop and an odometry experiment on a real robot with simulation and sort the causes of the differences.
tags: [hardware, first-robot, differential-drive, budget, optional]
---

# Optional: your first robot on a small budget

**This lesson is optional.** Every required lesson and exercise of this course can be finished
without hardware, and no other lesson lists this one as a prerequisite. Still, build one if you
can. In simulation the commanded speed is the speed you get, an encoder never misses a count and
the battery never runs down. A real robot is not like that, and meeting the difference with your
own hands is where the most is learned in this whole module.

## Where you will use this

What you build here is a TurtleBot, or a robot vacuum, reduced to its simplest form: two wheels,
two encoders, one IMU. The differential-drive model and PID of M3 and the speed loop and power
budget of this module all go into one machine. Put a single-board computer and a LiDAR on it and
it becomes a platform on which the localization of M5 and the Nav2 of M6 really run.

## Concepts

### The parts you need (by kind, not by product)

| Kind of part | What to look at |
|---|---|
| Chassis, two wheels and a caster | Wheel diameter and wheel separation you can measure; tyres that grip |
| Two geared DC motors with encoders | Rated voltage, no-load speed, stall torque and stall current, gear ratio, encoder PPR (they go into the calculation of the motors lesson) |
| Dual H-bridge motor driver | Do its continuous and peak currents cover the motors' stall current; supply voltage range; logic voltage (3.3 V / 5 V) |
| Microcontroller board | Hardware encoder counters or four interrupt pins, 2–4 PWM pins, I2C, USB serial |
| 6-axis IMU module | An I2C interface; whether it runs at 3.3 V |
| Battery, switch and fuse | A cell count that suits the motor voltage, a C-rate that can deliver the stall current, a protection circuit |
| 5 V buck converter | Rated above the sum of the logic side's peak currents (computed with the table of the power lesson) |

### Three budget tiers

Prices vary a great deal by country and over time, so only rough magnitudes are given. Redo the
sum with the prices you find when you buy.

| Tier | What it consists of | Rough scale | What you can do |
|---|---|---|---|
| 1. On the desk | A microcontroller board, one motor with encoder, a driver, USB and a small supply | a few tens of US dollars | Close a speed loop; see encoder resolution and saturation |
| 2. A robot that drives | Tier 1, a second motor, chassis and wheels, an IMU, battery and converter | around a hundred US dollars | Odometry, path following, measuring errors |
| 3. A ROS 2 robot | Tier 2, a single-board computer and a 2D LiDAR | a few hundred US dollars | The SLAM and navigation of M5–M6, the tools of M8 |

**Start at tier 1.** If you buy the parts of tier 3 before you have closed a speed loop on one
motor, then when something goes wrong you cannot tell whether the cause is the motor, the power,
the communication or the ROS configuration. Before buying anything you can also run the skeleton
of the firmware in a browser simulator (Wokwi).

### What to check before buying

1. **Voltage:** is the battery's range (full to end of discharge) inside the motor's rating and
   the driver's input range?
2. **Current:** can the driver and the battery carry twice the motor's stall current? If not, is
   there a current limit?
3. **Logic levels:** do the logic voltages of the microcontroller (usually 3.3 V) and of the
   driver, encoders and IMU match?
4. **Encoder:** are there several hundred counts or more per wheel revolution (4 × PPR × gear
   ratio)? Too few makes low-speed control hard.
5. **Pins:** can four encoder lines, 4–6 PWM and direction lines and two I2C lines be assigned to
   the board's pins without clashing?

### Safety

- For the first power-on, **lift the wheels off the ground.** A control loop with the wrong sign
  runs away to full speed.
- Use a lithium battery with a protection circuit, and fit a fuse and a switch. Charge it with a
  proper charger and do not leave it unattended.
- Switch the power off before changing wiring. Check that the grounds of the motor supply and the
  logic supply are connected.

### Three experiments

**Experiment 1 - the speed loop (tier 1).** Close a PI speed loop on one motor and step the target
speed. Log the true speed, the duty and the battery voltage over serial and plot them over the
simulation of the encoders lesson. Load the shaft lightly with your fingers and see how P and PI
differ.

**Experiment 2 - calibrating odometry (tier 2).** Send the robot 1 m in a straight line, measure
the real distance with a tape and correct the wheel radius. Spin it ten turns on the spot, measure
the real angle and correct the wheel separation. Then drive the 1 m square of M3 and measure the
position error on returning to the start. Doing it both clockwise and anticlockwise lets you
separate the two sources of error (UMBmark).

**Experiment 3 - path following (tier 2).** Put the go-to-goal controller of M3 on top of the
speed loops and follow the same square. Note separately the final position odometry reports and
the one you measure with the tape. Their difference is the "estimate versus truth" that M5 is
about.

### How it differs from the NumPy examples

For each experiment, record which rows of this table you saw. That record is the product of this
lesson.

| Assumed in simulation | In reality | Lesson |
|---|---|---|
| The motor turns at any small duty | Static friction keeps it still below a certain duty (dead band) | motors, drivers |
| The supply voltage is constant | The battery runs down and sags with current; the same duty gives different speeds | power |
| The speed is known exactly | Encoder quantization makes the measurement a staircase | encoders |
| Wheels do not slip | They slip on accelerating and turning, and odometry drifts | M3, M5 |
| The two motors are identical | Their speeds differ by a few percent at the same duty; the robot veers on a straight command | encoders (the speed loop fixes it) |
| The control period is constant | Communication and interrupts make it jitter | microcontrollers |
| Wheel radius and separation are known | Measuring them is 1–2% off, and odometry accumulates that | the M3 exercise |

## Self-check questions

1. Why start at tier 1 rather than buy everything for tier 3 at once?
2. The robot veers to one side on a straight command. Give three possible causes and how to check
   each.
3. After a lap of the square, odometry says the robot is at the start while the real robot is
   10 cm away. What does that mean?

## How to study this stage

1. **The text (first):** pick a budget tier, list its parts by kind, and fill in the five checks
   of "what to check before buying" as a table. Do this much even if you do not build.
2. **Calculate:** redo the gear-ratio calculation of the motors lesson with the motor you picked,
   and the power budget of the power lesson with the parts you picked.
3. **Experiment (if you build):** do experiments 1 → 2 → 3 in order, recording for each "what
   differed from the NumPy example".
4. **Check:** tie your record to the rows of the difference table. A difference that is not in the
   table is the most valuable result.

## References

- Ben-Ari & Mondada, *Elements of Robotics* (open access) - <https://link.springer.com/book/10.1007/978-3-319-62533-1>
- Wokwi - <https://wokwi.com/>
- MicroPython documentation - <https://docs.micropython.org/>
- J. Borenstein, L. Feng, "Measurement and Correction of Systematic Odometry Errors in Mobile Robots", IEEE Transactions on Robotics and Automation, 1996.
