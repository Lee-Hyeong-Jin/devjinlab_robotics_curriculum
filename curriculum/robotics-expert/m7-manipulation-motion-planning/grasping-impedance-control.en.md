---
id: m7-grasping-impedance-control
lang: en
title: "Grasping and contact: grippers, force control, and impedance"
summary: Decide when a two-finger grasp holds, using gripper types, the friction cone, and force closure, then see with a 1-DOF wall contact simulation how force control and impedance control handle the contact that position control cannot. Also lay out the stages of the pick-and-place pipeline.
objectives:
  - Judge whether a two-finger (antipodal) grasp holds using the Coulomb friction cone and force closure, and compute the grasp force required.
  - Explain the differences between position, force, and impedance control, and show in simulation how impedance stiffness affects contact force and impact.
  - Explain each stage of the pick-and-place pipeline - perception, grasp pose selection, approach, grasp, transport, release - and where it fails.
tags: [manipulation, grasping, friction-cone, force-control, impedance-control, pick-and-place]
---

# Grasping and contact: grippers, force control, and impedance

A mobile robot's goal was "do not hit anything," but a manipulator has to hit things properly -
to grasp, push, and insert. During contact, a 1 mm position error becomes tens of newtons of
force. This lesson covers "when is it grasped" (grasping) and "how do you handle force during
contact" (force and impedance control).

## Concepts

### Grippers and grasp models

Grippers divide into **parallel two-finger** types (including low-cost arms like the SO-101),
**suction**, which is strong on flat surfaces (logistics bin picking), and **multi-fingered
hands**, which allow in-hand manipulation but are hard to control.

Because of Coulomb friction, the force a finger can exert at a contact must lie inside the
**friction cone**. With a normal component $f_n$, the tangential component satisfies
$|f_t| \le \mu f_n$, and the half-angle of the cone is $\arctan\mu$. A state in which the contact
forces alone can hold the object regardless of external forces is called **force closure**. For a
planar two-finger grasp this is equivalent to "the line joining the two contacts lies inside both
friction cones" (the antipodal condition).

### Position, force, and impedance control

- **Position control:** on contact, force explodes in proportion to the environment's stiffness.
- **Force control:** exert $F_d$ directly ($\tau = J^\top F_d + g$). With no contact, it
  accelerates away.
- **Hybrid position/force control:** split by direction (force along the surface normal, position
  along the tangent, say).
- **Impedance control:** make the end-effector a virtual spring and damper. In free space it acts
  like position control; during contact it exerts only about $K \cdot$ (penetration). It becomes
  joint torque through the $\tau = J^\top F$ of lesson 1.

### The pick-and-place pipeline

Perception (estimating object pose from point clouds and RANSAC in M4) → generating and selecting
grasp candidates (antipodal check, collision check) → moving to the pre-grasp pose → a task-space
straight-line approach → closing the gripper and confirming the grasp (finger width, current) →
transport → release. Most failures come from perception error and slip, and low impedance absorbs
perception error.

## Key formulas

The friction cone and the minimum grasp force for a horizontal two-finger grasp:

$$|f_t| \le \mu f_n,\qquad 2\mu N \ge mg \;\Rightarrow\; N \ge \frac{mg}{2\mu}$$

The impedance law and the steady contact force against a wall of stiffness $k_e$:

$$F = K(x_d - x) - D\dot{x},\qquad F_{ss} = \frac{K k_e}{K + k_e}(x_d - x_w)$$

## Example

```python
import numpy as np

# 1) planar two-finger grasp: testing for force closure
MU = 0.5


def antipodal_ok(p1, n1, p2, n2, mu=MU):
    """Force closure holds if the line joining the contacts lies inside both friction cones
    (measured against the inward normals)."""
    d = (p2 - p1) / np.linalg.norm(p2 - p1)
    a1 = np.arccos(np.clip(d @ n1, -1, 1))  # angle between contact 1's inward normal and the line
    a2 = np.arccos(np.clip(-d @ n2, -1, 1))
    return a1 <= np.arctan(mu) and a2 <= np.arctan(mu), np.degrees([a1, a2])


def unit(deg):
    return np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg))])


print(f"friction coefficient {MU} -> cone half-angle {np.degrees(np.arctan(MU)):.1f} deg")
cases = {
    "head on": (np.array([-0.05, 0]), unit(0), np.array([0.05, 0]), unit(180)),
    "slightly off": (np.array([-0.05, -0.01]), unit(0), np.array([0.05, 0.02]), unit(180)),
    "badly off": (np.array([-0.05, -0.03]), unit(0), np.array([0.05, 0.04]), unit(180)),
    "wedge face (normal 40 deg)": (np.array([-0.05, 0]), unit(40), np.array([0.05, 0]), unit(140)),
}
for name, (p1, n1, p2, n2) in cases.items():
    ok, ang = antipodal_ok(p1, n1, p2, n2)
    verdict = "force closure" if ok else "slips"
    print(f"{name:26s} angles {ang.round(1)} -> {verdict}")

m, g = 0.4, 9.81  # pick up a 0.4 kg object from the side with two fingers
print(f"minimum grasp force N >= mg/(2mu) = {m * g / (2 * MU):.2f} N "
      f"(safety factor 2 -> {m * g / MU:.2f} N)")

# 2) 1-DOF impedance control: command x_d = 0.12 m, beyond a wall at x = 0.10 m of stiffness k_e
M_EE, K_ENV, X_WALL, X_D = 1.0, 2.0e4, 0.10, 0.12
dt, steps = 1e-5, 100_000  # 1 s


def simulate(K, zeta=1.0):
    D = 2 * zeta * np.sqrt(K * M_EE)
    x, v, forces = 0.0, 0.0, []
    for _ in range(steps):
        f_env = -K_ENV * (x - X_WALL) if x > X_WALL else 0.0
        f_ctrl = K * (X_D - x) - D * v  # impedance law (gravity assumed compensated)
        v += dt * (f_ctrl + f_env) / M_EE
        x += dt * v
        forces.append(-f_env)
    return max(forces), forces[-1], x


print("impedance K[N/m]  peak contact force[N]  steady contact force[N]  penetration[mm]")
for K in [300.0, 3000.0, 30000.0]:
    fmax, fss, x = simulate(K)
    theory = K * K_ENV / (K + K_ENV) * (X_D - X_WALL)
    print(f"{K:16.0f}  {fmax:21.1f}  {fss:14.2f}({theory:.2f})  {(x - X_WALL) * 1e3:13.3f}")
```

A 16.7° misalignment, inside the 26.6° cone half-angle, holds, while a 35° misalignment and the
40° wedge face slip. The steady contact force matches theory and grows with $K$ from about 6 N to
240 N. What deserves attention is the **peak** contact force: even at low stiffness, the moment
of running into the wall produces six times the steady value (about 36 N), which is why real
grasping decelerates just before contact.

**Exercise:** (1) Redo the test with friction coefficients of 0.3 and 0.8. (2) Approach slowly to
0.5 cm in front of the wall, then switch to impedance and measure the peak contact force.
(3) Switch to pure force control ($F = F_d$) and explain what happens when there is no wall.

## Self-check questions

1. How does the set of contact placements that give an antipodal grasp change as the friction coefficient shrinks?
2. Explain why impedance control is called the "middle ground" between position and force control, separately for free space and for contact.
3. Give two things you can do in the approach stage to reduce failures when the perception error is 2 cm.

## How to study this stage

1. **Textbook (first):** read the whole pick-and-place flow in Tedrake's *Robotic Manipulation*
   Ch. 3 to get the big picture.
2. **This lesson plus the example:** run the grasp test and the impedance experiment, and confirm
   through exercise (2) that "approach speed" is the key.
3. **Theory:** read Modern Robotics Ch. 12 (friction cone, force closure) and the force and
   impedance control sections of Ch. 11 along with the videos.
4. **Problems:** take the quiz in the Korean original (`rc quiz m7-grasping-impedance-control`).
5. **Depth (optional):** follow the pick-and-place and grasping assignments of MIT OCW 6.4210 and
   extend into the grasp candidate selection of Ch. 5.

## References

- Russ Tedrake, *Robotic Manipulation: Perception, Planning, and Control*, Ch. 3, 5, 8 - <https://manipulation.mit.edu/>
- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 11-12 - <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics Ch. 11 Robot Control videos - <https://www.youtube.com/playlist?list=PLggLP4f-rq02N54sD6xwdDWlDScvb32Pp>
- MIT OCW 6.4210 Robotic Manipulation (Fall 2022) - <https://ocw.mit.edu/courses/6-4210-robotic-manipulation-fall-2022/>
- Neville Hogan, "Impedance Control: An Approach to Manipulation", ASME J. Dyn. Sys. Meas. Control 1985 (the original impedance control paper, no link)
