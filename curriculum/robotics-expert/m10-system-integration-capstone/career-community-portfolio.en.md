---
id: m10-career-community-portfolio
lang: en
title: "Portfolio, community, competitions, and careers"
summary: Organize the capstone into a portfolio others can read and reproduce, and connect it to open-source contribution, domestic and international communities, conferences, competitions, and hiring-linked programs, based on a survey of the Korean ecosystem in 2026.
objectives:
  - Organize the capstone repository into a portfolio with a README, a demo video, result metrics, and a reproduction procedure.
  - Explain the steps of contributing to an open-source robotics project through issues, documentation, and small PRs.
  - Choose, with reasons, the next step among domestic and international communities, competitions, and hiring-linked training that fits your own goals.
tags: [portfolio, career, community, open-source, competition, korea]
---

# Portfolio, community, competitions, and careers

Robotics recruiters and research labs look less at "what you studied" than at **"what you built
and how you verified it."** If you finished the capstone, you already hold that evidence. This
lesson is the final step of turning that evidence into a readable form and connecting a solo
study habit to communities, competitions, and jobs.

## Concepts

### The portfolio: 30 seconds, 5 minutes, 30 minutes

Readers look at three levels. **30 seconds:** the one-line summary at the top of the README and
the demo GIF or video. **5 minutes:** the architecture figure, the table of results against
requirements, and the design decisions with their reasons. **30 minutes:** reproducing it with
Docker and reading the code and tests. The deliverables of L10.1-L10.5 (traceability table, BOM,
FMEA, CI, rubric results) fill those three levels directly. Writing down failures and limitations
is not a deduction; it is evidence of engineering judgment.

### Open-source contribution

The points where you got stuck in the packages your capstone used (Nav2, ros2_control, LeRobot,
drivers) are your first contribution candidates. Go in the order (1) an issue report with a
reproduction procedure, → (2) a documentation or example fix PR, → (3) a small bug fix.
Migration notes for API changes between Jazzy and Lyrical (the removed ros2_control APIs, say)
are contributions in high demand.

### Communities, domestic and international (as of 2026)

- The Korean ROS community is scattered. The ROS Discourse Korea group has been effectively
  dormant since April 2025, and OROCA's old domain (oroca.org) has passed to other use. Activity
  is spread across Naver cafés, offline meetups in Pangyo (the OROCA Pangyo Open Lab seminar in
  January 2026), and announcement channels of Modulabs and PyTorch KR.
- The center of gravity is moving toward **ROSCon Korea 2026** (Pangyo; Kwangwoon University,
  PinkLAB, and XYZ).
- English-language channels: the main ROS Discourse forum, the LeRobot Discord, the Pupper
  (Hands-On Robotics) Discord, and the HomeBrew Robotics Club mailing list.
- Conferences: internationally ICRA, IROS, RSS, and CoRL; domestically the ICROS and the Korea
  Robotics Society conferences (dates and URLs were not confirmed in the research notes, so check
  each society's announcements directly). Students and individuals can participate with workshop
  posters.

### Competitions

The most accessible to an adult software developer are the **RoboCup Korea Open** (February), the
**Robotics Works Competition** (October-November, a project submission format), and
F1TENTH-style autonomous racing in partnership with a university lab. RoboCup 2026 was held in
Incheon for the first time. VEX, FIRST, and WRO are aimed mainly at elementary through high
school teams.

### Hiring and linked training

The major axis of Korea's robot software hiring-linked paths in 2026 is the Ministry of
Employment and Labor's KDT government-funded programs. The ROBOTIS and CLOBOT Physical AI robot
software hiring-linked program (980 hours), the Hanwha Robotics AI Robot Tech School, and the
Doosan Robotics Rokey Bootcamp all converge on the order ROS 2 → SLAM/Nav2 → imitation learning
→ a real-robot capstone. Having finished this course you have already covered most of those
curricula, so differentiate your application with **the capstone's result metrics and repository
link**. Roles divide roughly into navigation, perception, control, robot learning, and
embedded/system integration, and capstone briefs A, B, and C serve as evidence for
navigation/integration, robot learning, and state estimation/perception respectively.

## Key checklist

- [ ] The first screen of the README has a one-line summary, a demo video, and a table of key metrics.
- [ ] There is an architecture figure and at least three design decisions (with alternatives and reasons).
- [ ] It reproduces in a single `docker run` line, or in five steps or fewer.
- [ ] The license and the open source and data sources used are stated.
- [ ] There is a limitations and next steps section.

## Example

Check whether the capstone repository meets the minimum portfolio requirements.

```python
from pathlib import Path

REQUIRED = {
    "README.md": "30-second summary, demo, metrics",
    "LICENSE": "license",
    "Dockerfile": "reproduction environment",
    "docs/architecture.png": "architecture figure",
    "docs/results.md": "results against requirements",
    ".github/workflows": "CI",
}
README_KEYWORDS = ["Demo", "Results", "Reproduc", "Limitations"]


def check_portfolio(repo: Path) -> list[str]:
    missing = [f"{p} ({why})" for p, why in REQUIRED.items() if not (repo / p).exists()]
    readme = repo / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        missing += [f"README has no '{k}' section" for k in README_KEYWORDS if k not in text]
    return missing


problems = check_portfolio(Path("."))
print("portfolio ready" if not problems else "\n".join(f"- {p}" for p in problems))
```

**Exercise:** (1) Run the checker on your own capstone repository and fill in the empty items.
(2) File one issue with a reproduction procedure, or one documentation PR, on an open source
project you used. (3) Pick one of community, competition, or hiring, and write a six-month plan
including deadlines.

## Self-check questions

1. What question does a portfolio with only a demo video and no metrics table leave in the reader's mind?
2. Why is a reproducible issue report or a documentation fix a better first open-source contribution than a large feature PR?
3. With the Korean ROS community scattered, what combination of channels is efficient for asking questions and connecting with others?

## How to study this stage

1. **Organize (first):** check your capstone repository with the example checker and start fixing
   from the first screen of the README.
2. **Look around:** read the ROSCon Korea coverage and the RoboCup and works competition pages,
   and put the next deadline in your calendar.
3. **Contribute:** pick one documentation spot where you got stuck during the capstone and leave
   an issue or a PR.
4. **Problems:** take the quiz in the Korean original (`rc quiz m10-career-community-portfolio`),
   then do the exercise.
5. **Extending (optional):** skim the labs in the F1TENTH public repository as a candidate for
   your next project.

## References

- ROS Discourse, Korea Users Group - <https://discourse.openrobotics.org/c/local/korea/33>
- Korea Times, coverage of ROSCon Korea 2026 (29 January 2026) - <https://www.koreatimes.co.kr/amp/southkorea/20260129/kwangwoon-university-hosts-robot-developer-conference>
- RoboCup South Korea Open 2026 - <https://www.robocup.org/events/78>
- Ministry of Science and ICT, 2026 Robotics Works Competition (in Korean) - <https://eopla.net/magazines/48000>
- mlab-upenn, F1TENTH public course repository - <https://www.github.com/mlab-upenn/f1tenthpublic>
