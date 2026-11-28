---
id: m11-power-budget
lang: en
title: Power and the power budget
summary: Batteries (chemistry, capacity, C-rate, internal resistance), regulators (linear and buck) and common ground; the cause of and remedies for the brown-out that restarts a board when the motors start; and a power budget that turns a list of loads into average and peak currents, runtime and voltage sag.
objectives:
  - Compute the runtime and the sag at peak current from a battery's nominal voltage, capacity, C-rate and internal resistance.
  - Compare the losses of a linear regulator and a buck converter and set the current rating each rail needs.
  - Explain why the logic supply drops out when motors are driven, and how wiring and the supply layout prevent it.
tags: [power, battery, regulator, brown-out, grounding, power-budget]
---

# Power and the power budget

A good share of the "code bugs" in a beginner's robot are power problems. The board restarts when
the motors start; a sensor reading jumps now and then; the robot slows down with charge still left.
No amount of staring at the code finds the cause. This lesson follows the electricity from the
battery to each part and shows how one table, the power budget, catches such problems in advance.

## Where you will use this

In designing a robot, the power budget comes right after choosing the motors and the computer. It
answers "how many minutes does this battery last", "how many amps must the 5 V converter give" and
"what happens when both motors stall at once". Hardware selection in the M10 capstone builds this
very table. And when a robot you have already built restarts for no reason, the brown-out of this
lesson is the first suspect.

## Concepts

### Batteries

| Chemistry | Nominal cell voltage | Full / end of discharge | Character |
|---|---|---|---|
| NiMH | 1.2 V | about 1.4 / 1.0 V | Safe and forgiving; heavy |
| Lithium-ion, lithium-polymer | 3.6–3.7 V | 4.2 / about 3.0 V | Light, high current; dangerous when overcharged, over-discharged or damaged |
| Lithium iron phosphate (LiFePO4) | 3.2 V | 3.65 / about 2.5 V | Safer and longer-lived than lithium-ion; lower energy density |

Four numbers matter.

- **Voltage:** cells in series times the cell voltage. Two lithium cells are nominally 7.4 V and
  really vary from 8.4 V down to 6.0 V. The circuit has to work over this **whole range**.
- **Capacity (Ah):** 1 Ah is 1 A for an hour. Energy is Wh = V × Ah. For life and safety, plan on
  using about 80% of it.
- **C-rate:** current relative to capacity. For a 2.2 Ah battery 1 C is 2.2 A. The maximum
  continuous current is stated as, say, "20 C".
- **Internal resistance:** under current the terminal voltage falls to $V = V_{oc} - R_{int}\, i$.
  It decides how far the voltage dips when a large current is drawn for a moment.

Use lithium batteries with a protection circuit (BMS), charge them with a proper charger, and fit
a fuse and a power switch. Do not use a battery that is swollen or dented.

### Regulators

The battery voltage varies; computers and sensors want a steady 5 V or 3.3 V. Regulators sit in
between.

- **Linear regulator:** burns the excess voltage as heat. The loss is $(V_{in} - V_{out})\, i$.
  Simple and quiet, but hot at high current. Right for a sensor that draws tens of milliamps.
- **Buck converter (switching):** lowers the voltage with PWM and an inductor (the principle of
  the previous lesson). At 85–95% efficiency it is the one for large currents. Its input must stay
  a certain margin above its output for it to work.

A regulator must be rated above the **sum of the peak currents** of the loads on its rail, not the
average.

### Common ground and wiring

A signal voltage is a value relative to ground (GND). If the grounds of the microcontroller, the
driver, the sensors and the single-board computer are not connected, they cannot read each other's
signals. **Connect every ground** is the first rule.

The second rule is to **separate the path of large currents from the path of signals**. Several
amps of motor current through a thin wire shift the ground potential by the wire's resistance
alone, and sensor readings jump. Run the motor wires and the logic wires separately from one point
at the battery terminals (a star ground), and keep motor wires thick and short.

### Brown-out

At the moment a motor starts, a current close to its stall current flows. The battery's internal
resistance and the wiring make the voltage dip for an instant, and if it falls below the minimum
input the regulator needs, the 5 V rail collapses. The microcontroller's under-voltage detector
restarts the chip. The symptom is "the program starts from the top whenever the motors run".

The remedies follow the causes, in order.

1. Do not take the logic supply from the motor driver's 5 V output; make it with a **separate
   regulator** from the battery.
2. Fit a **large capacitor** (hundreds of µF or more) close to the driver's supply terminals. It
   supplies the momentary current.
3. Reduce the current: raise the duty gradually (soft start) and use a current limit.
4. Use a battery with lower internal resistance (larger, or a higher C-rate) and thicker wires.

### The power budget

List the loads in a table: for each, **which rail**, **how much on average**, **how much at peak**.
The average decides the runtime; the peak decides part ratings and the sag. Convert the current of
the 5 V rail to battery current with the converter's efficiency
($i_{batt} = V_{out}\, i_{out} / (\eta\, V_{batt})$).

## Key formulas

- Terminal voltage: $V = V_{oc} - R_{int}\, i$
- Runtime: $t = \text{capacity} \times \text{usable fraction} / \bar{i}_{batt}$
- Linear loss: $(V_{in} - V_{out})\, i$; buck input current: $i_{in} = V_{out}\, i_{out} / (\eta\, V_{in})$
- C-rate: $i / \text{capacity}$

## Example

```python
import numpy as np

# (name, rail, average current A, peak current A)
loads = [
    ("two motors", "battery", 0.60, 4.4),
    ("single-board computer", "5 V", 0.80, 1.20),
    ("LiDAR", "5 V", 0.35, 0.60),
    ("microcontroller + IMU", "5 V", 0.08, 0.10),
]
V_NOM, CAP_AH, R_INT, ETA = (
    7.4,
    2.2,
    0.15,
    0.90,
)  # two-cell lithium battery, buck converter efficiency

i_5v_avg = sum(avg for _, rail, avg, _ in loads if rail == "5 V")
i_5v_peak = sum(peak for _, rail, _, peak in loads if rail == "5 V")
p_5v = 5.0 * i_5v_avg / ETA  # power on the converter's input side
i_batt_avg = sum(avg for _, rail, avg, _ in loads if rail == "battery") + p_5v / V_NOM
i_batt_peak = (
    sum(pk for _, rail, _, pk in loads if rail == "battery") + 5.0 * i_5v_peak / ETA / V_NOM
)

print(f"5 V rail: average {i_5v_avg:.2f} A, peak {i_5v_peak:.2f} A -> a 3 A converter")
print(f"battery: average {i_batt_avg:.2f} A, peak {i_batt_peak:.2f} A")
print(f"runtime (using 80% of the capacity): {CAP_AH * 0.8 / i_batt_avg * 60:.0f} min")
print(
    f"sag at peak current: {i_batt_peak * R_INT:.2f} V -> terminal voltage {V_NOM - i_batt_peak * R_INT:.2f} V"
)
print(f"C-rate needed: {i_batt_peak / CAP_AH:.1f} C")
print(
    f"loss making 5 V with a linear regulator {(V_NOM - 5.0) * i_5v_avg:.2f} W, with a buck {p_5v - 5.0 * i_5v_avg:.2f} W"
)
# 5 V rail: average 1.23 A, peak 1.90 A -> a 3 A converter
# battery: average 1.52 A, peak 5.83 A
# runtime (using 80% of the capacity): 69 min
# sag at peak current: 0.87 V -> terminal voltage 6.53 V
# C-rate needed: 2.6 C
# loss making 5 V with a linear regulator 2.95 W, with a buck 0.68 W
```

The robot runs 69 minutes at an average of 1.5 A, and with both motors stalled 5.8 A flows and the
voltage dips by 0.87 V. Making the 5 V with a linear regulator would turn 3 W into heat, more than
it survives without a heat sink, so a buck converter is the right choice.

**Exercise:** (1) Add a gripper servo (0.2 A average, 1.5 A peak) to the 5 V rail. Is a 3 A
converter enough? What does the runtime fall to? (2) Recompute the peak current and the terminal
voltage with the battery near the end of discharge (6.4 V); the 5 V side takes the same power, so
its current rises. What happens if the buck converter's minimum input is 6.0 V? (3) What is the
runtime with a 5 Ah battery, and what do you give up?

```expected
1. The 5 V rail becomes 1.43 A on average and 3.40 A at peak. The peak is above 3 A, so **a 3 A
   converter is not enough**. Go to a 5 A one, or give the servo a converter of its own (the better
   choice if the servo's surges are not to shake the computer's 5 V). The battery's average current
   becomes 1.67 A and the runtime falls from 69 to 63 minutes. The peak current is 6.95 A.
2. At 6.4 V the 5 V side takes the same power, so the battery current rises to a peak of 6.05 A,
   and the terminal voltage is $6.4 - 6.05 \times 0.15 = 5.49$ V. That is below the converter's
   6.0 V minimum: the 5 V rail collapses and the computer and the microcontroller restart. This is
   the classic brown-out, **the robot restarting when the motors work hard on a nearly empty
   battery**. Measure the battery voltage and stop in time at about 6.6 V, limit the motor current,
   or use three cells for headroom.
3. $5.0 \times 0.8 / 1.52 \times 60 \approx 158$ minutes. In exchange the battery is more than twice
   as heavy and large. More weight needs more motor torque and current (the force formula of the
   motors lesson), so the real runtime is shorter than this. A larger capacity does bring a lower
   internal resistance and so less sag.
```

## Self-check questions

1. What voltage range must a circuit running from two lithium cells withstand?
2. How much power turns into heat when a linear regulator supplies 5 V at 2 A from 7.4 V?
3. What causes "the microcontroller restarts when the motors are switched on", and what is the
   first remedy to try?

## How to study this stage

1. **The text (first):** draw as blocks the path of the current from battery to motor and from
   battery to computer, and write the voltage and the peak current on each arrow.
2. **The example:** replace the load table in the code with the parts of a robot you have in mind,
   taking the currents from their datasheets, and run it.
3. **The exercise:** work the three items and write down the conclusion of (2) in one sentence.
4. **Check:** in the documentation of a single-board computer, find the allowed input voltage range
   and the recommended supply current, and compare them with the values in the example.

## References

- Battery University - <https://batteryuniversity.com/>
- Raspberry Pi hardware documentation - <https://www.raspberrypi.com/documentation/computers/raspberry-pi.html>
- Ben-Ari & Mondada, *Elements of Robotics* (open access) - <https://link.springer.com/book/10.1007/978-3-319-62533-1>
