---
id: m11-motors-gearing
lang: en
title: Kinds of motor and how to choose one
summary: Sort out how brushed DC, servo, stepper and BLDC motors differ, then use the torque-speed line of a DC motor and a gear ratio to work out whether "this motor can move this robot".
objectives:
  - Tell apart how brushed DC motors, RC servos, steppers and BLDC motors are driven and what each is used for on a robot.
  - Compute the torque-speed line, the stall current and the maximum power point from a datasheet's no-load speed and stall torque.
  - Derive the wheel torque and speed a robot needs from its mass, wheel radius, acceleration and slope, and choose a gear ratio.
tags: [actuators, dc-motor, bldc, servo, stepper, gearing, sizing]
---

# Kinds of motor and how to choose one

M3 assumed that "commanding wheel speeds $\omega_R$, $\omega_L$ makes the wheels turn at them". In
reality a motor produces that speed, and a motor has limits on the torque and the speed it can
give. A robot that cannot climb a slope, jerks when it starts, or drains its battery quickly often
has not a code problem but the wrong motor and gears. This lesson shows how to make that judgement
from two or three numbers on a datasheet.

## Where you will use this

The wheels of a robot vacuum, the joints of an arm, the propellers of a drone and the axes of a 3D
printer are all motors, but of different kinds. Building a first wheeled robot, the first decision
is "which geared DC motor do I buy"; designing an arm or a legged robot, you compute the torque
and speed each joint needs and choose a motor and reducer for it. The procedure in the M10
capstone, from requirements to parts, uses the calculation of this lesson unchanged.

## Concepts

### Four kinds of motor

| Kind | How it is driven | Strength | Weakness | Use on robots |
|---|---|---|---|---|
| Brushed DC | Apply a voltage and it turns; voltage sets the speed, current the torque | Cheap and simple | Brush wear, efficiency | Small wheeled robots, low-cost grippers |
| RC servo | A DC motor, gears and a position controller in one case; you send a target angle | Three wires, angle control built in | Limited range and precision, little feedback | Small arms, pan-tilt heads |
| Stepper | Turns a fixed angle per pulse | Position control without an encoder | Loses steps when overloaded, weak torque at speed | 3D printers, Cartesian robots |
| BLDC | Electronics switch the winding currents in sequence (electronic commutation) | Efficiency, power density, life | Needs a dedicated driver and the rotor angle | Drones, legged robots, cobot joints |

A serial-bus servo ("smart servo") is an RC servo with a communication link: position, speed,
current and temperature can be read back, which is why educational arms use them widely.

### The two equations of a DC motor

Two equations describe a brushed DC motor well enough. Current makes torque, and rotation makes a
voltage (the back-EMF).

$$\tau = k_t\, i, \qquad V = R\, i + k_e\, \omega$$

In SI units $k_t = k_e$. Eliminating $i$ gives the **torque-speed line**: the faster the motor
turns, the more the back-EMF cuts the current and the less torque is available. Its two end points
are the two numbers on the datasheet.

- **Stall torque** $\tau_s = k_t V / R$: the maximum torque, with the shaft held still. The current
  is then at its largest ($V/R$, the stall current).
- **No-load speed** $\omega_0 = V / k_e$: the maximum speed, with nothing attached. The torque is
  then zero.

Mechanical power $P = \tau\omega$ peaks in the middle of the line ($\omega_0/2$) at
$\tau_s\omega_0/4$. Running near the stall torque for long turns a large current into heat and
burns the motor. A common rule is to keep the continuous torque at or below 20–30% of the stall
torque.

### Gears

A small DC motor is fast and weak (thousands to ten thousand revolutions a minute, a few mN·m). A
wheel needs the opposite. A reducer of ratio $N$ divides the speed by $N$ and multiplies the
torque by $N\eta$ ($\eta$ is the efficiency, 0.6–0.8 for small gearboxes).

$$\omega_{out} = \frac{\omega_m}{N}, \qquad \tau_{out} = N\,\eta\,\tau_m$$

Too small a ratio leaves too little torque; too large a ratio leaves too little top speed. A
larger ratio also brings more backlash and friction and makes the shaft harder to turn from
outside (poorer backdrivability), which is why arms that touch people and legged robots use large
motors with small ratios.

### The torque and speed you need

For a wheeled robot the driving force is the sum of acceleration, slope and rolling resistance.

$$F = m a + m g \sin\theta + c_{rr}\, m g \cos\theta$$

With $n$ driven wheels each wheel needs the torque $\tau_w = F r / n$ at the speed
$\omega_w = v_{max}/r$. The motor has to meet **both conditions at once**: the required point must
lie below the torque-speed line.

## Key formulas

- Motor: $\tau = k_t i$, $V = R i + k_e\omega$ → $\tau(\omega) = k_t (V - k_e\omega)/R$
- End points: $\tau_s = k_t V/R$, $\omega_0 = V/k_e$, maximum power $\tau_s\omega_0/4$ (at $\omega_0/2$)
- Gears: $\omega_{out} = \omega_m/N$, $\tau_{out} = N\eta\tau_m$
- Requirement: $F = ma + mg\sin\theta + c_{rr} mg\cos\theta$, $\tau_w = Fr/n$, $\omega_w = v_{max}/r$

## Example

Get the motor constants from three datasheet values (rated voltage, no-load speed, stall torque),
then find a gear ratio that meets the requirements of a 2 kg robot.

```python
import numpy as np

# a small brushed DC motor (datasheet values): 6 V rated, 12000 rpm no-load, 20 mN·m stall
V, w0, tau_s = 6.0, 12000 * 2 * np.pi / 60, 0.020
k = V / w0  # back-EMF constant k_e = torque constant k_t [V·s/rad = N·m/A]
R = k * V / tau_s  # winding resistance [ohm]
print(
    f"k = {k * 1000:.2f} mN·m/A, R = {R:.2f} ohm, stall current = {V / R:.2f} A"
)  # 4.77, 1.43, 4.19


def motor_torque(w, v=V):
    return k * (v - k * w) / R  # the torque-speed line


# requirements: a 2 kg robot, wheel radius 3 cm, two driven wheels
m, r, g = 2.0, 0.03, 9.81
a, slope, c_rr, v_max = 0.5, np.deg2rad(10), 0.03, 0.5
force = m * a + m * g * np.sin(slope) + c_rr * m * g * np.cos(slope)
tau_wheel, w_wheel = force * r / 2, v_max / r
print(
    f"force needed {force:.2f} N -> per wheel {tau_wheel * 1000:.1f} mN·m, {w_wheel:.1f} rad/s"
)  # 4.99, 74.8, 16.7

eta = 0.7  # gearbox efficiency
for N in (10, 30, 50, 100):
    tau_m, w_m = tau_wheel / (N * eta), w_wheel * N
    ok = tau_m <= 0.3 * tau_s and motor_torque(w_m) >= tau_m
    print(
        f"N={N:3d}: motor torque {tau_m / tau_s * 100:5.1f}% of stall, "
        f"motor speed {w_m / w0 * 100:5.1f}% of no-load -> {'OK' if ok else 'X'}"
    )
# N= 10: 53.4%, 13.3% -> X (too much torque)   N= 30: 17.8%, 39.8% -> OK
# N= 50: 10.7%, 66.3% -> OK                    N=100:  5.3%, 132.6% -> X (too slow)
```

A ratio of 10 asks for more than half the stall torque and overheats the motor; 100 needs a speed
above the no-load speed, which the motor cannot give at all. The answer lies between 30 and 50.

**Exercise:** (1) Find this motor's maximum mechanical power, the speed at which it occurs, and the
efficiency there. (2) If the robot's mass grows to 5 kg, which of the four ratios remain? (3) With
a ratio of 30 and a mass of 2 kg, find the steady speed up a 10° slope and on level ground (the
acceleration term is 0). What does comparing them with the required 0.5 m/s tell you?

```expected
1. Maximum power is $\tau_s\omega_0/4 = 0.020 \times 1256.6 / 4 = 6.28$ W, at half the no-load
   speed, 6000 rpm. The current there is half the stall current (2.09 A), so the electrical input
   is $6 \times 2.09 = 12.6$ W and the efficiency is 50%. The maximum power point is not an
   efficient point; efficiency is high near the no-load speed, at small torque.
2. The force needed rises to 12.47 N, 187 mN·m per wheel.

   | $N$ | Motor torque (of stall) | Motor speed (of no-load) | Verdict |
   | --- | --- | --- | --- |
   | 10 | 133.6% | 13.3% | impossible (above the stall torque) |
   | 30 | 44.5% | 39.8% | no (above the 30% rule; overheats) |
   | 50 | 26.7% | 66.3% | possible |
   | 100 | 13.4% | 132.6% | impossible (too slow) |

   Only 50 remains, with hardly any margin: a sign that a larger motor is needed.
3. On the slope the force is 3.99 N, the motor torque 14.2% of stall (0.60 A), and the speed about
   1.08 m/s. On level ground only rolling resistance has to be overcome: 0.09 A and about
   1.23 m/s. Both are more than twice the required 0.5 m/s. The required speed is one the robot
   "must be able to reach"; the actual speed is set by the controller lowering the voltage (PWM).
   With this much speed in hand, raising the ratio to 50 for more torque margin is an option.
```

## Self-check questions

1. Why does the current rise when you stop the motor shaft by hand? Explain with the back-EMF.
2. Doubling the gear ratio does what to the wheel's maximum torque and to its top speed?
3. Give two reasons a drone propeller uses a BLDC motor rather than a brushed DC motor.

## How to study this stage

1. **The text (first):** derive the torque-speed line from the two equations by hand, draw it, and
   mark the stall torque, the no-load speed and the maximum power point.
2. **The example:** run the code and put the "required point" for each gear ratio on your drawing.
3. **The exercise:** redo the calculation with the mass, slope and wheel radius of a robot you
   would like to build.
4. **Check:** find the datasheet of a real gear motor and see whether its no-load speed and stall
   torque are stated in a form this calculation can take (with the gearbox, or motor only).

## References

- Lynch & Park, *Modern Robotics*, section 8.9 - <https://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Ben-Ari & Mondada, *Elements of Robotics* (open access) - <https://link.springer.com/book/10.1007/978-3-319-62533-1>
- Control Tutorials for MATLAB and Simulink, DC Motor Speed - <https://ctms.engin.umich.edu/CTMS/index.php?example=MotorSpeed&section=SystemModeling>
