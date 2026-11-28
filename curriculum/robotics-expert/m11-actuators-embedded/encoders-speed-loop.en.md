---
id: m11-encoders-speed-loop
lang: en
title: Encoders and the motor speed loop
summary: Measuring a wheel's angle and speed with a quadrature encoder, the trade between speed resolution and delay in the counting method, and closing the motor speed loop that sits under the heading loop of M3 (cascade control) on a simulated motor with saturation, quantization and supply sag.
objectives:
  - Compute the counts per wheel revolution and the angle and speed resolution from an encoder's PPR, quadrature counting and the gear ratio.
  - Explain how the resolution of a count-based speed measurement depends on the window length, and name the problem at low speed and its remedies.
  - Describe the structure of cascade control, an outer loop (position, heading) over an inner loop (motor speed), and the rule for choosing each loop's rate.
tags: [actuators, encoder, velocity-estimation, cascade-control, pid, saturation]
---

# Encoders and the motor speed loop

In the PID example of M3 the angular velocity the controller commanded simply became the robot's
angular velocity. A real motor turns at different speeds for the same duty depending on battery
voltage, floor friction and slope. So a real robot adds **one more small control loop per motor,
which measures the speed and brings it to the commanded speed**. This is the step the community
calls the most instructive: closing a PID speed loop around a DC motor with an encoder. This
lesson does it without hardware, on a simulation that includes the three things a real motor
brings: encoder quantization, output saturation and supply sag.

## Where you will use this

The `cmd_vel` that Nav2 issues says "0.3 m/s forward, 0.5 rad/s turning". After it has been split
into left and right wheel speeds (M3), the motor speed loop is what makes those speeds actually
happen; in ROS 2 it runs below the `diff_drive_controller` of `ros2_control`, inside the
microcontroller firmware. The encoder counts are also the raw material of odometry (M3, M5). A
robot that veers on a straight command, shudders at low speed or slows on a hill is mostly fixed
in this loop.

## Concepts

### The quadrature encoder

An incremental encoder gives pulses as the shaft turns. Two channels (A and B) 90° apart tell the
direction of rotation by which changes first, and counting every rising and falling edge of both
gives four counts per cycle (quadrature counting).

$$\text{counts per wheel revolution} = 4 \times \text{PPR} \times N_{gear}$$

With the encoder on the motor shaft the gear ratio improves the resolution. A magnetic encoder of
PPR 12 with a ratio of 30 gives $4 \times 12 \times 30 = 1440$ counts, an angle resolution of
$360^\circ/1440 = 0.25^\circ$.

An encoder knows only **relative** angle. Zero is wherever it was at power-on, and a missed count
(a late interrupt, or noise) is wrong for ever after. This is why the microcontroller's hardware
counter (a timer in encoder mode) is used.

### Estimating speed

Speed is not measured directly; it is computed from counts. The simplest **counting method** takes
the change in count over a fixed time $T_w$.

$$\hat\omega = \frac{2\pi}{\text{CPR}} \cdot \frac{\Delta \text{count}}{T_w}, \qquad
\text{resolution} = \frac{2\pi}{\text{CPR} \cdot T_w}$$

Counts are whole numbers, so the speed comes only in multiples of this resolution. 1440 CPR
measured every 1 ms resolves 4.36 rad/s: with a target of 10 rad/s the reading jumps between 8.7
and 13.1. Lengthening the window to 10 ms improves the resolution to 0.44 rad/s but makes the
measurement 5 ms late on average. It is the "noise against delay" trade of the filtering lesson in
M4.

At low speed the window holds zero counts or one, and counting becomes useless. Then use the
**period method** (time from one count to the next), or a mix of the two. A finer encoder is the
easiest fix.

### The speed loop

A motor speed loop is usually PI. With P alone an error has to remain to produce the voltage that
overcomes the back-EMF and friction, so there is a steady-state error, and it grows under load
(exactly as in M3). The I term supplies that voltage. A D term amplifies the steps of a quantized
speed measurement and is seldom used in a speed loop.

The output is a PWM duty, which cannot leave $[-1, 1]$. Anti-windup, which keeps the integral from
growing during saturation, is essential. And the speed reachable at a duty of 1 is set by the
battery voltage. The larger the current, the further the battery's internal resistance pulls the
terminal voltage down (supply sag), so the top speed under load is lower than with no load.

### Cascade control

Stacking the heading loop of M3 on this speed loop gives **cascade** control.

| Loop | Measures | Outputs | Rate (example) |
|---|---|---|---|
| Outer: position, heading (path following, M3) | odometry, IMU | wheel speed commands $\omega_R^*$, $\omega_L^*$ | 20–50 Hz |
| Inner: motor speed (this lesson) | encoder | PWM duty | 500–1000 Hz |
| (Innermost: current or torque, in an FOC driver) | current sensor | switches | 10–20 kHz |

The rule is that **the inner loop must be 5–10 times faster than the outer one**. The outer loop
can then treat the inner one as "does what it is told at once", which is the condition under which
the assumption of M3 holds. Tuning also starts from the inside.

## Key formulas

- Counts: $\text{CPR} = 4 \times \text{PPR} \times N_{gear}$, angle resolution $2\pi/\text{CPR}$
- Counting method: $\hat\omega = 2\pi\,\Delta\text{count}/(\text{CPR}\,T_w)$, resolution $2\pi/(\text{CPR}\,T_w)$, mean delay $T_w/2$
- Motor: $J\dot\omega = k i - b\omega - \tau_{load}$, $i = (D\,V_{supply} - k\omega)/R$
- Supply sag: $V_{supply} = V_{batt} - R_{int}\, i_{batt}$

## Example

```python
import numpy as np

# motor + gears + wheel (referred to the wheel shaft): J dw/dt = k i - b w - tau_load,  i = (v - k w) / R
k, R, J, b = 0.05, 2.0, 2e-4, 1e-4
V_BATT, R_INT = 7.4, 0.25  # battery open-circuit voltage and internal resistance
COUNTS = 4 * 12 * 30  # quadrature x 12 PPR x gear ratio 30 = 1440 counts per wheel revolution


def run(kp, ki, w_ref=10.0, dt=0.001, T=2.0, tau_load=0.0, sag=False, window=1):
    """PI speed loop. Speed is the count difference over the last `window` periods. The load arrives at 1 s."""
    w = theta = integ = 0.0
    counts, log = [0] * (window + 1), []
    for n in range(int(T / dt)):
        counts = counts[1:] + [
            int(np.floor(theta / (2 * np.pi) * COUNTS))
        ]  # an encoder counts whole numbers only
        w_meas = (counts[-1] - counts[0]) * 2 * np.pi / COUNTS / (dt * window)
        err = w_ref - w_meas
        u = kp * err + ki * integ
        duty = float(np.clip(u, -1.0, 1.0))  # a PWM duty cannot leave -1..1
        if u == duty:  # anti-windup: no integration while saturated
            integ += err * dt
        v_supply = V_BATT
        if sag:  # current pulls the battery's terminal voltage down
            i_est = (duty * V_BATT - k * w) / (R + R_INT * abs(duty))
            v_supply = V_BATT - R_INT * abs(duty) * i_est
        i = (duty * v_supply - k * w) / R
        load = tau_load if n * dt >= 1.0 else 0.0
        w += (k * i - b * w - load) / J * dt
        theta += w * dt
        log.append((w, w_meas, duty))
    return np.array(log)


print(f"speed resolution (counting over 1 ms): {2 * np.pi / COUNTS / 0.001:.2f} rad/s")  # 4.36
for name, (kp, ki) in {"P ": (0.05, 0.0), "PI": (0.05, 1.0)}.items():
    log = run(kp, ki, tau_load=0.02)
    before, after = log[900:1000, 0].mean(), log[1900:, 0].mean()
    print(f"{name}: before the load {before:5.2f}, after {after:5.2f} rad/s (target 10)")
# P : before  8.72, after  6.84 rad/s    PI: before 10.00, after 10.00 rad/s
log = run(0.05, 1.0)
print(
    f"jitter of measured speed {log[1500:, 1].std():.2f} rad/s, of true speed {log[1500:, 0].std():.3f} rad/s"
)  # 1.98, 0.058
```

With P alone the speed stops at 8.72 rad/s, short of the 10 rad/s target, and falls to 6.84 rad/s
when the load (0.02 N·m) arrives at one second. PI brings it back to 10.00 in both cases. The
measured speed jitters with a standard deviation of 2 rad/s because of quantization, yet the true
speed varies by only 0.06 rad/s: the motor's inertia filters the jittering duty.

**Exercise:** (1) Set `window=10` and see how the resolution, the jitter of the measured speed and
the jitter of the true speed change (`run(0.05, 1.0, window=10)`). (2) Lower the target to 1 rad/s
(`w_ref=1.0`). Which values does the measurement take with `window=1` and with `window=10`? (3)
With a target of 100 rad/s and a load of 0.1 N·m arriving at one second
(`w_ref=100, tau_load=0.1, T=3.0`), compare the final speed and duty for `sag=False` and
`sag=True`. Explain with a formula why the target is not reached.

```expected
1. A 10 ms window makes the measurement finer, and with it the duty and the true speed steadier.

   | `window` | Resolution | Std of measured speed | Std of true speed |
   | --- | --- | --- | --- |
   | 1 (1 ms) | 4.36 rad/s | 1.98 rad/s | 0.058 rad/s |
   | 10 (10 ms) | 0.44 rad/s | 0.12 rad/s | 0.008 rad/s |

   The price is a mean measurement delay of 5 ms: raise the gains further and the long window is
   the first to start oscillating.
2. At 1 rad/s a count arrives about every 4.4 ms. With `window=1` the measurement takes only two
   values, 0 and 4.36 rad/s, so the controller is fed a signal that flips between "stopped" and
   "more than four times too fast". The true speed averages 1.0 correctly (the integral term fits
   the average) but the duty keeps jumping. With `window=10` the readings narrow to 0.87 and
   1.31 rad/s and the jitter of the true speed falls from 0.058 to 0.010 rad/s. Slower than this
   needs the period method or a finer encoder.
3. After the load arrives the duty saturates at 1.0 in both cases and the target is not reached.

   | | Before the load | Speed after | Duty | Current |
   | --- | --- | --- | --- | --- |
   | `sag=False` | 100.0 rad/s | 63.0 rad/s | 1.0 | 2.1 A |
   | `sag=True` | 100.0 rad/s | 53.2 rad/s | 1.0 | 2.1 A |

   Giving 0.1 N·m at 100 rad/s needs a current of $(b\omega + \tau_{load})/k \approx 2.2$ A and a
   voltage of $Ri + k\omega \approx 2 \times 2.2 + 0.05 \times 100 = 9.4$ V, and the battery has 7.4 V.
   No controller, however good, can reach that speed. With sag the terminal voltage drops further,
   to $7.4 - 0.25 \times 2.1 \approx 6.9$ V, and the speed falls by another 10 rad/s or so. What to
   fix here is not the gains but the motor, the gear ratio or the battery. Without anti-windup the
   integral would grow without end over this stretch and the motor would overspeed for a long
   while after the load went away.
```

## Self-check questions

1. With the same PPR, how does the resolution of the wheel angle differ between an encoder on the
   motor shaft and one on the wheel shaft?
2. What improves and what worsens when the speed measurement window is lengthened?
3. Why must the inner loop of a cascade be faster than the outer loop?

## How to study this stage

1. **The text (first):** connect the cascade table to the path-following picture of M3 and draw a
   block diagram in which commands flow down and measurements flow up.
2. **The example:** run the code and plot the three columns of `log` (true speed, measured speed,
   duty) against time.
3. **The exercise:** write down a prediction before running each item. For (3) in particular,
   compute the voltage needed by hand first.
4. **Check:** raise `kp` from 0.05 to 0.5, see how much the quantized measurement shakes the duty,
   and whether a longer window eases it.

## References

- Åström & Murray, *Feedback Systems*, 2nd ed. (free PDF) - <https://fbswiki.org/wiki/index.php/Main_Page>
- Control Tutorials for MATLAB and Simulink, DC Motor Speed: PID Controller Design - <https://ctms.engin.umich.edu/CTMS/index.php?example=MotorSpeed&section=ControlPID>
- Ben-Ari & Mondada, *Elements of Robotics* (open access) - <https://link.springer.com/book/10.1007/978-3-319-62533-1>
