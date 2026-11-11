---
id: m10-capstone-project-guide
lang: en
title: "Capstone project design guide (choosing a topic, milestones, evaluation criteria)"
summary: Presents the criteria for choosing a six-week capstone topic, week-by-week milestones, and a scored evaluation rubric, along with three example project briefs that can be done on low-cost real hardware or recorded data, with no simulator.
objectives:
  - Choose a capstone topic by interest, budget, and risk, and fix its scope with requirements in the form of L10.1.
  - Set six weekly milestones with deliverables, placing the riskiest integration work early.
  - Score your own project against the evaluation rubric and turn the low-scoring items into the work of the next iteration.
tags: [capstone, project, rubric, milestones, andino, so-101, dataset]
---

# Capstone project design guide

The capstone is the graduation work of this course. The goal is not "the hardest thing" but
**something that works end to end, that someone else can reproduce, and whose design you can
explain**. This platform does not assume simulator practice, so every project presented here runs
on low-cost real hardware or on recorded data.

## Concepts

### Choosing a topic: three questions

1. **Interest:** are you curious enough to spend 8-10 hours a week on it for six weeks?
2. **Budget:** can you afford the BOM of L10.2? With no hardware, pick the dataset project
   (brief C).
3. **Risk:** are there no more than two parts or algorithms you have never used? If three or more
   things are new, cut the scope.

### Milestones: pull integration forward

| Week | Milestone | Deliverables |
|---|---|---|
| 1 | Requirements and architecture fixed | requirements traceability table, node graph, BOM (L10.1-10.2) |
| 2 | "Walking skeleton": input to output flows end to end once | a minimal demo video, a Dockerfile |
| 3 | Core functionality, first pass | first quantitative metric, one reference log |
| 4 | Safety and testing | watchdog and FMEA (L10.3), green CI (L10.4) |
| 5 | Repeated trials and tuning | a table of 10 or more trial results |
| 6 | Documentation and presentation | README, results report, 3-minute video (L10.6) |

Week 2's "walking skeleton" matters most. Even at low quality, once it runs from sensor to
actuator (or from data to metric) once, every remaining risk becomes "improvement."

## Key checklist

### Evaluation rubric (100 points)

| Item | Points | Excellent (full) | Adequate (half) | Insufficient (0) |
|---|---|---|---|---|
| Requirements and design | 15 | measurable FRs/NFRs, traceability table, interface table complete | requirements exist but some are not measurable | no documentation |
| Integration and functionality | 25 | every FR demonstrated on real hardware or data | only some core FRs demonstrated | a single-component demo |
| Quantitative evaluation | 15 | 10 or more repetitions, with mean, variance, and failure cause analysis | only 1-3 results presented | no metrics |
| Safety and reliability | 15 | watchdog, E-stop, FMEA, fault injection testing | watchdog only | no safety design |
| Reproducibility and engineering | 15 | Docker, CI, reference logs, reproducible on a fresh PC in 30 minutes | installation documentation only | not reproducible |
| Documentation and presentation | 15 | README, report, video, with limitations and next steps stated | README only | none |

## Example

### Example project briefs

**A. Mapping and autonomous navigation with a low-cost differential-drive robot (real hardware,
parts cost estimated at $250-450)**
Following the Andino design, assemble a robot from a Raspberry Pi, an LD19-class 2D lidar, and an
ESP32 motor controller, then integrate ros2_control differential drive → SLAM Toolbox mapping →
Nav2 navigation. Evaluation: arrival error and success rate over 10 round trips to 5 goal points
on a living room map. Safety: a `/cmd_vel` watchdog and a motor power E-stop.

**B. SO-101 imitation learning pick-and-place (real hardware, BOM about $230 plus 3D printing)**
Record 50 teleoperated demonstration episodes with LeRobot using SO-101 leader and follower arms,
train an ACT policy, and move a designated object into a box. Evaluation: success rate over 20
attempts with varied object positions, and the success-rate curve against the number of training
episodes. Safety: joint velocity and torque limits, and rejecting commands outside the
workspace. Training may be done on a cloud GPU (see M9).

**C. A recorded-data state estimation benchmark (hardware optional, can cost nothing)**
Using MCAP (wheel odometry, IMU, lidar) that you recorded or borrowed, build a reproducible
pipeline comparing the trajectory error of pure odometry, EKF fusion (M5), and scan matching
correction. Evaluation: closed-loop error between identical start and end points, and CPU time
per algorithm. Reproducibility: fully automated in Docker and CI from downloading the data to
generating the metrics table. Variant: analyze manipulation data quality (episode length, action
distribution) on a subset of Open X-Embodiment.

### A self-scoring script

```python
rubric = {
    "requirements and design": 15,
    "integration and functionality": 25,
    "quantitative evaluation": 15,
    "safety and reliability": 15,
    "reproducibility and engineering": 15,
    "documentation and presentation": 15,
}
levels = {"excellent": 1.0, "adequate": 0.5, "insufficient": 0.0}
self_eval = {
    "requirements and design": "excellent",
    "integration and functionality": "adequate",
    "quantitative evaluation": "adequate",
    "safety and reliability": "excellent",
    "reproducibility and engineering": "insufficient",
    "documentation and presentation": "adequate",
}

assert sum(rubric.values()) == 100
score = sum(w * levels[self_eval[k]] for k, w in rubric.items())
print(f"total {score:.0f}/100")
for k, w in sorted(rubric.items(), key=lambda kv: kv[1] * levels[self_eval[kv[0]]] - kv[1]):
    lost = w * (1 - levels[self_eval[k]])
    if lost:
        print(f"next iteration priority: {k} (points lost {lost:.1f})")
```

**Exercise:** Pick one of briefs A, B, or C - or invent your own - write a one-page plan (goal,
FRs/NFRs, BOM, six weekly milestones, three risks and their mitigations), and score yourself
against the rubric at week 2 and week 6.

## Self-check questions

1. What risk arises from first integrating at week 5 instead of building the "walking skeleton" at week 2?
2. If brief B reports its success rate from only 3 attempts, which rubric item loses points, and why is it insufficient?
3. What must a learner with no hardware demonstrate to earn full marks on "integration and functionality" with brief C?

## How to study this stage

1. **Compare the briefs (first):** hold the three briefs against the budget and power criteria of
   L10.2 and your own schedule, and pick one.
2. **Read the reference procedures:** build a step list from the Andino README and the TurtleBot 4
   tutorials for A, the LeRobot SO-101 documentation and the Trelis write-up for B, and the M5
   lessons and your own MCAP for C.
3. **Write the plan:** copy the "Excellent" column of the rubric straight across as your
   completion criteria.
4. **Problems:** take the quiz in the Korean original (`rc quiz m10-capstone-project-guide`), then
   do the exercise.
5. **Weekly check:** run the self-scoring script at the end of each week and make the items
   losing the most points next week's work.

## References

- Ekumen, Andino - <https://github.com/Ekumen-OS/andino>
- Clearpath Robotics, TurtleBot 4 User Manual - Tutorials - <https://turtlebot.github.io/turtlebot4-user-manual/tutorials/>
- Hugging Face, LeRobot SO-101 - <https://huggingface.co/docs/lerobot/so101>
- Trelis, "Train an ACT Policy for an SO-101 Robot" - <https://trelis.substack.com/p/train-an-act-policy-for-an-so-101>
- Open X-Embodiment Collaboration, Open X-Embodiment - <https://robotics-transformer-x.github.io/>
