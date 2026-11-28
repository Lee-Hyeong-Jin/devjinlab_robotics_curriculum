---
id: m11-microcontrollers-buses
lang: en
title: Microcontrollers, single-board computers and buses
summary: What a microcontroller and a single-board computer are each good at and which code should run where, decided by real-time needs; a comparison of UART, I2C, SPI and CAN; a serial protocol between the two built from frames, a checksum and a timeout; and one page on what micro-ROS does.
objectives:
  - Explain the difference between a microcontroller and a single-board computer in terms of real-time behaviour, and decide on which of the two a robot function belongs.
  - Compare the wiring, speed, distance and multi-device properties of UART, I2C, SPI and CAN and choose a bus for a purpose.
  - Build and parse a serial frame with a header, a length and a checksum, and explain why a watchdog that stops the robot on lost communication is needed.
tags: [embedded, microcontroller, single-board-computer, real-time, uart, i2c, spi, can, micro-ros]
---

# Microcontrollers, single-board computers and buses

The lessons so far have asked for "a motor speed loop at 1 kHz", "no missed encoder counts" and
"stop when communication is lost". Perception, SLAM and planning from M4 onwards ask instead for a
camera, plenty of memory, Linux and ROS 2. One computer rarely does both well. So nearly every
robot uses **a microcontroller (MCU) together with a single-board computer (SBC)** and joins them
with a communication link. This lesson is about where to draw that line and what to join it with.

## Where you will use this

Open a TurtleBot-class robot and you find a microcontroller board attached to the motors and
sensors, connected by USB (serial) to a single-board computer running ROS 2. Arms and legged robots
have a driver per joint, tied together by CAN or EtherCAT. Adding a sensor means checking "is it
I2C or SPI, and does its address clash", and a robot that now and then misses a command sends you
to look at the frames and the timeout. micro-ROS and the `ros2_control` hardware interface of M8
are the software that sits on exactly this boundary.

## Concepts

### Two kinds of computer

| | Microcontroller (MCU) | Single-board computer (SBC) |
|---|---|---|
| Compute and memory | Tens to hundreds of MHz, tens of KB to a few MB of RAM | Multi-core in the GHz range, several GB of RAM |
| Software | No OS, or an RTOS; running within milliseconds of power-on | Linux; tens of seconds to boot |
| Timing | Steady to microseconds, off a timer interrupt | Can be pushed back by milliseconds to tens of milliseconds by other processes |
| Input and output | Handles pins directly: PWM, ADC, timers, encoder counters | USB, Ethernet, cameras, Wi-Fi |
| What it does | Motor speed loops, encoder counting, reading sensors, safety stop | Perception, SLAM, path planning, ROS 2, logging, networking |

### What runs where

One question draws the line: **"what happens if this does not occur within a fixed time, every
time?"**

- Miss one encoder pulse and the odometry is wrong for good. Let a 1 kHz speed loop run 20 ms late
  once and the motor jerks. Let the motors keep following the last command after communication is
  lost and the robot drives into a wall. This work goes on the **MCU**. Work that has failed when
  its deadline is missed is called hard real-time.
- A map update that is 50 ms late leaves the robot slightly less accurate. Such soft real-time
  work, and anything computationally heavy, goes on the **SBC**.

Ordinary Linux does not guarantee when a process runs. A Python loop on the SBC doing 1 kHz control
with `sleep(0.001)` is right on average and now and then tens of milliseconds late. A real-time
kernel reduces that, but leaving the work that touches pins on the MCU is simpler and safer. To run
several jobs by priority inside the MCU, use an RTOS (FreeRTOS, Zephyr and others).

### Buses

| Bus | Wires | Connection | Speed (roughly) | Distance | Use on robots |
|---|---|---|---|---|---|
| UART | TX, RX (+GND) | point to point | 9.6 k–1 M bps | a few metres | MCU ↔ SBC, GPS, serial servos |
| I2C | SDA, SCL (+pull-up resistors) | many devices, told apart by address | 100 k / 400 k bps | on a board (tens of cm) | IMUs, range sensors, small displays |
| SPI | SCK, MOSI, MISO, a CS per device | many devices, told apart by CS line | several M bps | on a board | fast IMUs, magnetic encoders, flash |
| CAN | CAN-H, CAN-L (differential, 120 Ω at both ends) | many nodes, priority by message ID | up to 1 M bps | tens of metres | joint drivers, battery management, vehicles |

The rules of thumb: a few sensors on a board, I2C (fewest wires); if they must be read fast, SPI.
Two separate boards, UART (USB serial included). Many devices on a long cable where motor currents
flow, CAN, for its noise immunity. Between the single-board computer and cameras or a LiDAR, USB or
Ethernet.

Two cautions. With UART both sides must agree on the speed (baud) beforehand, and a start and a
stop bit make each byte cost 10 bits. And connecting a 3.3 V device straight to a 5 V device can
destroy the 3.3 V side (use a level shifter).

### A serial protocol

UART sends bytes; it does not say "where one message starts and ends". Bytes can also go missing
or be changed by noise. So a message is wrapped in a **frame**.

- **Header:** fixed bytes that mark the start of a frame. A receiver that starts reading in the
  middle can find its place again.
- **Length and body:** how many bytes the body has, then the body.
- **Checksum (or CRC):** tells whether the body was damaged. A damaged frame is dropped, not used.

The receiving side has a **watchdog** (timeout): when no valid command has arrived for a set time,
it stops the motors. This is the only thing that keeps the robot from driving on with its last
command when a cable comes out or the program on the single-board computer dies.

### micro-ROS in one page

micro-ROS makes an MCU a node of the ROS 2 graph. A small client library (`rclc`) runs on the MCU,
and on the single-board computer the **micro-ROS Agent** talks to it over serial or UDP and
publishes on its behalf on the DDS side. The result: a `/wheel_ticks` published by the MCU can be
watched with `ros2 topic echo`.

- What you gain: no frames, serialization or message definitions of your own, and the ROS 2 tools
  as they are.
- What it costs: an MCU able to run an RTOS (tens of KB of RAM or more), a heavy build
  environment, and a link that is cut when the Agent dies. You still add the watchdog yourself.
- The alternative: define a simple serial protocol like the frame of this lesson, and let a
  `ros2_control` hardware interface or a small bridge node on the single-board computer turn it
  into topics. On a small robot this is the easier one to debug.

## Key formulas

- UART throughput: bytes per second = baud / 10 (8N1); frames per second = baud / (10 × frame bytes)
- Watchdog stopping distance: $d = v \times t_{timeout}$
- Checksum: the complement of the sum of the body bytes - catches every single-bit error, misses
  two errors whose sum cancels

## Example

Wrap wheel-speed commands in frames, then pick the intact ones out of a stream that also holds junk
bytes and a damaged frame.

```python
import struct

HEADER = b"\xaa\x55"


def checksum(data: bytes) -> int:
    return (~sum(data)) & 0xFF


def pack(left: float, right: float, seq: int) -> bytes:
    """One wheel-speed command as a frame: header 2 + length 1 + body 9 + checksum 1 = 13 bytes."""
    body = struct.pack("<Bff", seq & 0xFF, left, right)
    return HEADER + bytes([len(body)]) + body + bytes([checksum(body)])


def parse(stream: bytes):
    """Pick the intact frames out of a byte stream; drop a broken one and look for the next header."""
    out, i = [], 0
    while i + 3 <= len(stream):
        if stream[i : i + 2] != HEADER:
            i += 1
            continue
        n = stream[i + 2]
        frame_end = i + 3 + n + 1
        if frame_end > len(stream):
            break  # not all of it has arrived yet
        body = stream[i + 3 : i + 3 + n]
        if n == 9 and checksum(body) == stream[frame_end - 1]:
            out.append(struct.unpack("<Bff", body))
            i = frame_end
        else:
            i += 1  # looked like a header but was not
    return out


frames = [pack(1.0 + k, -1.0 - k, k) for k in range(4)]
stream = bytearray(b"\x00\x13" + b"".join(frames))  # two junk bytes in front
stream[2 + 13 + 7] ^= 0x40  # one bit of the second frame is flipped
print([f[0] for f in parse(bytes(stream))])  # [0, 2, 3]: only the broken frame 1 is missing

baud, frame_bytes = 115200, len(frames[0])
print(
    f"frame of {frame_bytes} bytes, at most {baud / 10 / frame_bytes:.0f} a second at {baud} bps"
)  # 13, 886
```

The two junk bytes at the front are not a header and are skipped, and frame 1, with one bit
flipped, fails its checksum and is dropped. Frames 2 and 3 after it are found by their headers and
read normally.

**Exercise:** (1) How many of these 13-byte frames can be sent per second at 9600, 115200 and
1 000 000 bps? Which speed do you need to send commands at 100 Hz and get a status of the same
size back? (2) Make an error the checksum does not catch (hint: add 0x40 to one byte of the body
and subtract 0x40 from another). What should replace the checksum? (3) The watchdog timeout is
0.2 s and the robot drives at 0.5 m/s. How much further does it go after the cable comes out
before it stops? What goes wrong if the timeout is cut to 0.02 s?

```expected
1. Each byte costs 10 bits, so the number of frames per second is baud / 130.

   | Speed | Frames per second, at most |
   | --- | --- |
   | 9600 bps | about 74 |
   | 115200 bps | about 886 |
   | 1 000 000 bps | about 7692 |

   A 100 Hz exchange needs $100 \times 13 \times 10 = 13\,000$ bps in each direction. 9600 bps cannot
   do it; 115200 bps uses about 11% of its capacity.
2. Adding 0x40 to one byte of the body and subtracting 0x40 from another leaves the sum of the
   bytes, and so the checksum, unchanged. `parse` accepts the frame as good and the wheel speeds
   are nonsense. A plain sum catches every single-bit error but misses errors that cancel like
   this, and bytes that swap places. A CRC (CRC-8, CRC-16) catches nearly all such cases. Checking
   once more that a received value is physically possible is a cheap extra defence.
3. It travels $0.5 \times 0.2 = 0.1$ m further (braking distance comes on top). A timeout of 0.02 s
   cuts that to 1 cm, but then one or two late or damaged commands out of a 100 Hz stream (a 10 ms
   period) make the robot hesitate. Linux on the single-board computer is now and then tens of
   milliseconds late, so set the timeout to a few command periods (here 50–200 ms).
```

## Self-check questions

1. Why run the motor speed loop on a microcontroller rather than in a Python program on the
   single-board computer?
2. You want to attach an IMU and two range sensors to an MCU. What must you check before choosing
   I2C?
3. Why does the MCU need a watchdog even when micro-ROS is used?

## How to study this stage

1. **The text (first):** list the functions learned so far (encoder counting, speed loop, path
   following, sensor filtering, object detection), decide for each whether it goes on the MCU or
   the SBC, and draw the data that passes between them.
2. **The example:** run the code, then damage other places in the stream (the header, the length
   byte) and watch how `parse` finds its place again.
3. **The exercise:** work the three items. For (2), really change the bytes and confirm that
   `parse` accepts the frame.
4. **Check:** read the Overview of the micro-ROS documentation and note three things it does for
   you compared with the hand-made protocol of this lesson.

## References

- micro-ROS - <https://micro.ros.org/>
- ros2_control documentation - <https://control.ros.org/>
- Arduino documentation, Learn - <https://docs.arduino.cc/learn/>
