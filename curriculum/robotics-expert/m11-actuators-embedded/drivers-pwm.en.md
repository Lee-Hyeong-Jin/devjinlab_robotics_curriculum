---
id: m11-drivers-pwm
lang: en
title: Motor drivers and PWM
summary: The H-bridge and PWM, which let a microcontroller's weak signal handle a motor's large current; how PWM frequency relates to current ripple and how the stall current relates to the driver's rating; and an outline of six-step drive and FOC for BLDC motors, and when FOC is needed.
objectives:
  - Explain how the four switches of an H-bridge give forward, reverse, brake and coast, and why dead time and flyback diodes are needed.
  - Compute the average voltage and the current ripple from the PWM duty and frequency, and give the reasons for choosing a PWM frequency.
  - Compare a motor's stall current with a driver's continuous and peak ratings and judge whether a current limit is needed.
tags: [actuators, motor-driver, h-bridge, pwm, current-limit, bldc, foc]
---

# Motor drivers and PWM

A microcontroller pin gives a few tens of milliamps at 3.3 V. The motor of the previous lesson
draws more than 4 A at stall. Connect the motor straight to the pin and the motor does not turn;
the board is damaged. The part in between, which "takes a weak signal and switches a large
current", is the motor driver. This lesson covers what a driver does inside (the H-bridge), how
speed is adjusted (PWM), and the condition for not burning the driver (its current rating).

## Where you will use this

Every electric robot has a driver per motor. The dual H-bridge board of a small wheeled robot,
the ESC of a drone and the servo drive inside an arm joint work on the same principle. The output
$u$ of the PID in M3 becomes a "PWM duty" on a real robot, and its limit (saturation) comes from
the supply voltage and the driver's current limit. A board that switches off when the robot
starts, or a driver that runs hot, can be foreseen with the calculation of this lesson.

## Concepts

### The H-bridge

Turning a motor both ways needs the voltage across it to be reversible. An H-bridge is four
switches (MOSFETs) arranged as an H with the motor in the middle.

| Switches on | Across the motor | What happens |
|---|---|---|
| Top left + bottom right | $+V$ | Forward |
| Top right + bottom left | $-V$ | Reverse |
| Both bottom (or both top) | 0 (shorted) | Brake: the motor acts as a generator and stops itself |
| All off | open | Coast |

If the top and bottom switch of one side are on together, the supply is shorted (shoot-through).
So a driver turns one off, waits a moment, and only then turns the other on (**dead time**). A
motor is also an inductor: cutting its current suddenly produces a high voltage. The **flyback
diode** across each switch gives that current a path. A driver IC has both built in; they are what
gets forgotten when building a drive from a relay or a single transistor.

### PWM

A switch can only be on or off. Instead of making an in-between voltage, it is **switched quickly,
and the fraction of time it is on (the duty $D$) is varied.** This is PWM, pulse-width modulation.
The average voltage the motor sees is $D \cdot V$.

The inductance $L$ of the winding smooths the current: it rises while the switch is on and falls
while it is off. When the PWM period is well below the electrical time constant $L/R$, that swing
(the ripple) is

$$\Delta i \approx \frac{V\, D\,(1 - D)}{L\, f_{PWM}}$$

The ripple is largest at $D = 0.5$ and inversely proportional to the frequency. A large ripple
makes the torque shake and adds heat. Three things guide the choice of frequency: (1) the ripple
should be small beside the average current; (2) 20 kHz or more keeps it out of hearing (lower, and
the motor whines); (3) too high increases switching losses, so stay inside the range the driver
recommends. Small robots usually use about 20 kHz.

### Current limits

A driver's datasheet states a **continuous current** and a **peak current**. What to compare them
with is not the motor's usual current but its **stall current** $V/R$. At the moment of starting,
of being blocked by a wall, or of a sudden reversal, a motor draws close to its stall current. If
the driver cannot take it, a protection circuit cuts out (the good case) or the driver burns (the
bad one).

The power turned into heat inside the driver comes from the resistance of the two switches the
current passes through: $P \approx 2\, R_{DS(on)}\, i^2$. It goes as the square, so twice the
current is four times the heat.

There are three remedies: a driver rated above the stall current; a current limit that measures
the current and lowers the duty when it exceeds a threshold (built into many driver ICs); and
raising the duty gradually (soft start).

### BLDC and FOC

A BLDC motor has no brushes, so the driver must switch the direction of the current in its three
windings to suit the rotor position. It uses a three-phase bridge of six switches.

- **Six-step (trapezoidal) drive:** knows the rotor position only to 60° (Hall sensors or the
  back-EMF) and steps through six switch combinations. Simple, and good at high speed; drone ESCs
  started from it. The torque is uneven at low speed.
- **FOC (field-oriented control):** measures the winding currents and the rotor angle, transforms
  the currents into a frame turning with the rotor (d-q), and controls the torque-producing
  component (the q-axis current) with a PI loop. In effect the rotation of M1 runs tens of
  thousands of times a second. Torque is smooth and quiet even at low speed, and **torque can be
  commanded directly**.

FOC is needed where torque must be handled precisely: the joints of legged robots and cobots,
gimbals, direct-drive wheels that must move smoothly at low speed. A small wheeled robot on
brushed motors does not need it. FOC requires a driver with an angle sensor (a magnetic encoder,
for instance) and current sensing.

## Key formulas

- Average voltage: $\bar{V} = D\,V$
- Current ripple (when $T_{PWM} \ll L/R$): $\Delta i \approx V D (1-D) / (L f_{PWM})$
- Stall current: $i_{stall} = V/R$; average current: $\bar{i} = (DV - k_e\omega)/R$
- Driver conduction loss: $P \approx 2 R_{DS(on)} i^2$

## Example

Integrate the winding (an RL circuit) directly over finely divided PWM periods and compare the
ripple with the approximation.

```python
import numpy as np

V, R, L, k = 12.0, 2.0, 1e-3, 0.02  # supply, winding resistance, inductance, back-EMF constant


def ripple(duty, f_pwm, w=0.0, periods=200, sub=400):
    """Integrate the RL circuit over PWM periods split into `sub` steps; mean and ripple of the last."""
    dt, i, last = 1 / f_pwm / sub, 0.0, []
    for p in range(periods):
        for s in range(sub):
            v = V if s < duty * sub else 0.0  # on: the supply; off: freewheeling (0 V)
            i += (v - R * i - k * w) / L * dt
            if p == periods - 1:
                last.append(i)
    return np.mean(last), max(last) - min(last)


for f in (1e3, 5e3, 20e3):
    mean, pp = ripple(0.5, f)
    approx = V * 0.5 * 0.5 / (L * f)
    print(
        f"f = {f / 1e3:4.0f} kHz: mean {mean:.2f} A, ripple {pp:.3f} A (approximation {approx:.3f} A)"
    )
# f =    1 kHz: mean 3.00 A, ripple 2.779 A (approximation 3.000 A)
# f =    5 kHz: mean 3.00 A, ripple 0.598 A (approximation 0.600 A)
# f =   20 kHz: mean 3.00 A, ripple 0.150 A (approximation 0.150 A)

print(f"stall current V/R = {V / R:.1f} A")  # 6.0 A
i_avg = 2.0
print(f"MOSFET loss (2 x 50 mOhm, {i_avg} A): {2 * 0.05 * i_avg**2:.2f} W")  # 0.40 W
```

At 1 kHz the ripple is 2.8 A on an average of 3 A: the current swings between 0.2 A and 5.8 A a
thousand times a second, and since the PWM period (1 ms) is longer than $L/R$ (0.5 ms) the
approximation no longer holds either. At 20 kHz the ripple is 5% of the average.

**Exercise:** (1) At 20 kHz, find the average current and the ripple for duties of 0.1, 0.5 and 0.9
(motor stalled). Which duty gives the largest ripple? (2) With the motor turning at 200 rad/s
(`w=200`), how do the average current and the ripple at a duty of 0.5 change? (3) You use this
motor with a driver rated 2 A continuous. To what must the duty be limited so the current at stall
does not exceed 2 A? Why is a fixed duty limit not a good method?

```expected
1. With the motor stalled the average current is $DV/R$.

   | Duty | Average current | Ripple |
   | --- | --- | --- |
   | 0.1 | 0.6 A | 0.054 A |
   | 0.5 | 3.0 A | 0.150 A |
   | 0.9 | 5.4 A | 0.054 A |

   The ripple is proportional to $D(1-D)$: largest at 0.5 and equal at 0.1 and 0.9.
2. The average current falls to $(DV - k\omega)/R = (6 - 4)/2 = 1.0$ A while the ripple stays at
   0.150 A. The back-EMF lowers the average current and leaves the ripple alone, so when the motor
   runs lightly (a small average current) the ripple is, relatively, larger.
3. At stall $DV/R \le 2$ A gives $D \le 2 \times 2 / 12 = 0.33$. But once the motor turns, the
   back-EMF allows that much more voltage ($D \le (2R + k\omega)/V$), so fixing the duty at 0.33
   ties the top speed to a third. Real drivers therefore limit not the duty but the **measured
   current**, lowering the duty only when it exceeds the limit.
```

## Self-check questions

1. What happens in an H-bridge without dead time?
2. Raising the PWM frequency from 1 kHz to 20 kHz improves which two things and worsens which one?
3. Why is FOC used in the joints of a legged robot and not on a small wheeled robot?

## How to study this stage

1. **The text (first):** draw an H-bridge on paper and trace in colour the path of the current in
   each of the four modes. Put the difference between brake and coast into words.
2. **The example:** run the code and plot the current over one period to see the ripple.
3. **The exercise:** work the three items by hand, then check (1) and (2) with `ripple`.
4. **Check:** in the datasheet of a motor driver IC, find the continuous current, the peak
   current, the recommended PWM frequency, and whether it has a current limit.

## References

- Lynch & Park, *Modern Robotics*, section 8.9 - <https://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- SimpleFOC documentation, FOC theory - <https://docs.simplefoc.com/foc_theory>
- Ben-Ari & Mondada, *Elements of Robotics* (open access) - <https://link.springer.com/book/10.1007/978-3-319-62533-1>
