---
id: m10-hardware-selection-integration
lang: en
title: "Hardware selection and integration (sensors, actuators, compute, power, communication)"
summary: Starting from the numbers in your requirements, choose sensors, actuators, and compute boards, and design the power budget and the communication buses (UART, USB, I2C, CAN, Ethernet). Validate the bill of materials (BOM) with a budget ladder reflecting 2026 price movements and a power and cost calculation script.
objectives:
  - Work backward from NFRs (speed, accuracy, rate, budget) to sensor specifications (range, resolution, rate) and motor specifications (torque, speed, encoder).
  - Choose, with reasons, the division of labor between the high-level controller (SBC) and the low-level controller (MCU) and the communication between them.
  - Sum per-part currents to design battery capacity, runtime, and voltage rails, and check the BOM total against the budget.
tags: [hardware, bom, sensors, actuators, power, communication, budget]
---

# Hardware selection and integration

L10.1 settled the requirements and the interfaces. Now it is time to plug real parts in behind
those interfaces. Hardware selection is not "picking good parts" but **finding the cheapest,
simplest combination that satisfies the numbers in the requirements**. And 2026 is a particularly
awkward year for that arithmetic. The DRAM shortage pushed the Raspberry Pi 5 16GB to $385 and
the Jetson Orin Nano Super from $249 to $399, and the Jetson Nano is on its way to end of life.

## Concepts

### Working backward from requirements to specifications

- **Sensors:** "stop 0.5 m in front of an obstacle while driving at 0.3 m/s" → reaction time =
  sensor period + processing latency + braking. At 10 Hz a lidar lets the robot travel 3 cm
  during a worst-case 0.1 s. Look at range, resolution, and rate from the sensor model view of
  M4. Among low-cost 2D lidars, the LD19 family (about $69; the successor D500 is recommended)
  and the RPLIDAR A1 (about $99) have ROS 2 drivers. The OAK-D Lite depth camera went from $169
  to $269 in July 2026.
- **Actuators:** for differential drive (M3), get the motor speed $\omega = v / r$ from the wheel
  radius $r$ and the maximum speed $v$, and the torque needed for acceleration and slopes.
  Encoder resolution governs odometry accuracy (M5). For a manipulator, chaining position-control
  servos (STS3215) on a serial bus, as the SO-101 does, is the cheapest arrangement.
- **Compute:** a CPU-based SBC (Pi 4/5) is enough through SLAM and Nav2; a GPU board is needed
  only to run neural network inference on the robot. Separating training (laptop or cloud) from
  inference (on the robot) cuts the budget substantially.

### Dividing labor between high- and low-level controllers

| Layer | Examples | What it does | Timing character |
|---|---|---|---|
| High-level (SBC) | Raspberry Pi, Jetson | ROS 2, SLAM, planning, logging | tens of ms, non-real-time OS |
| Low-level (MCU) | ESP32, Pico, STM32 | motor PWM, encoder counting, watchdog | under 1 ms, deterministic |

Between them, USB serial (UART) with a hand-designed packet is the most common; with micro-ROS
the MCU appears as a ROS 2 node. Industrial setups connecting several motor drivers use CAN or
EtherCAT, and short-range sensor connections use I2C or SPI.

### Power and wiring

- Separate the motor rail from the logic rail (the voltage drop from motor inrush current reboots
  the SBC), and tie the grounds at a single point.
- Runtime ≈ battery capacity (Wh) × 0.8 / average power draw (W). The 0.8 is margin for depth of
  discharge and conversion loss.
- Place fuses and the **physical emergency stop (E-stop) switch where it cuts the motor power
  directly** (L10.3).

## Key checklist

- [ ] Every part specification was worked backward from at least one NFR number in L10.1.
- [ ] A ROS 2 (Jazzy) driver or an MCU firmware path has been confirmed for every part.
- [ ] The high-to-low controller communication method, baud rate, and packet format (including a checksum) are decided.
- [ ] The power budget table lists peak current separately from average current.
- [ ] The BOM has unit price, quantity, vendor, and spares, and the total is at most 80% of the budget (the rest is margin for failures and exchange rates).

## Example

Check the power budget and the BOM total in one pass. The numbers are illustrative; substitute
the actual part datasheets.

```python
parts = [
    # name, rail, average A, peak A, unit price (USD), quantity
    ("Raspberry Pi 5 4GB", "5V", 1.2, 2.5, 120.0, 1),
    ("LD19 lidar", "5V", 0.18, 0.3, 69.0, 1),
    ("ESP32 board", "5V", 0.1, 0.25, 10.0, 1),
    ("DC geared motor (with encoder)", "12V", 0.4, 2.0, 20.0, 2),
    ("motor driver", "12V", 0.02, 0.05, 12.0, 1),
]
battery_wh, budget_usd, regulator_5v_max_a = 3 * 3.7 * 2.6, 450.0, 3.0  # 3S 2600mAh

power_w = 0.0
for rail in ("5V", "12V"):
    volts = float(rail.rstrip("V"))
    avg = sum(a * n for _, r, a, _, _, n in parts if r == rail)
    peak = sum(p * n for _, r, _, p, _, n in parts if r == rail)
    power_w += avg * volts
    print(f"{rail:>4} average {avg:4.2f} A, peak {peak:4.2f} A")
    if rail == "5V" and peak > regulator_5v_max_a:
        print(f"     warning: 5V regulator {regulator_5v_max_a} A < peak {peak:.2f} A")

runtime_h = battery_wh * 0.8 / power_w
total = sum(price * n for *_, price, n in parts)
print(f"average draw {power_w:.1f} W, expected runtime {runtime_h:.1f} h")
print(f"BOM {total:.0f} USD / budget {budget_usd:.0f} USD ({total / budget_usd:.0%})")
```

The output warns that the 5V peak current (3.05 A) exceeds the regulator limit (3 A). The Pi 5
spikes during boot and under USB load, so moving to a 5 A regulator is the right call. Check the
budget ratio against 80% at the same time.

**Exercise:** Build your capstone BOM in the table form above and compute (1) peak current per
rail, (2) runtime, and (3) the budget ratio. Record prices with the date you checked them and the
vendor.

## Self-check questions

1. What symptom appears if you put the motors and the SBC on the same 5 V regulator, and why?
2. Why hand motor PWM and encoder counting to an MCU instead of processing them directly in a Python node on the Raspberry Pi?
3. What do you lose in budget and power by choosing a GPU board for a Nav2 robot that needs no neural network inference?

## How to study this stage

1. **Course (first):** watch the Inflearn "robotics system breakdown" course (58 minutes) to see
   the high- and low-level controllers, the communication buses, and the power and emergency stop
   structure in one pass.
2. **Reading BOMs:** compare the BOM in the SO-ARM100 README against the TurtleBot3 Burger parts
   list and write down the price and time difference between "buy assembled" and "build yourself."
3. **Checking prices:** compute boards moved a lot in price during 2026, so check again right
   before buying (see the OMG! Ubuntu article).
4. **Problems:** take the quiz in the Korean original
   (`rc quiz m10-hardware-selection-integration`), then do the exercise.
5. **Low-level controller (optional):** skim the micro_ros_setup README for the path to attaching
   an ESP32 or Pico as a ROS 2 node.

## References

- jelly, "현직자가 알려주는 로보틱스 시스템 완전 해부: 부품부터 통신까지", Inflearn (in Korean) - <https://www.inflearn.com/course/a-complete-breakdown>
- TheRobotStudio, SO-ARM100 - <https://github.com/TheRobotStudio/SO-ARM100>
- Generation Robots, TurtleBot3 Burger - <https://www.generationrobots.com/en/402707-turtlebot3-burger-mobile-robot.html>
- OMG! Ubuntu, "Raspberry Pi 5 price goes up and up" (November 2026) - <https://omgubuntu.co.uk/2026/11/raspberry-pi-5-price-goes-up-and-up>
- micro-ROS, micro_ros_setup - <https://github.com/micro-ROS/micro_ros_setup>
