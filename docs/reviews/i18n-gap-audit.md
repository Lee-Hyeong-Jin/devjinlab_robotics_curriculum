# i18n gap audit - Korean left in the English build

- generated: 2026-11-12 by `uv run python scripts/i18n/audit.py --write`
- Korean runs found: **11054**
- detector: `robotics_curriculum.i18n.scan` (Hangul syllables, Jamo, compatibility Jamo)
- rows are grouped by field: list indexes and content ids collapse to `*` / `{id}`.

## How to read this

| class | meaning | owner |
| --- | --- | --- |
| **A. no container** | the field has nowhere to hold a translation (course/module title and summary, activity titles, resource title and note, quiz questions) | this audit's follow-up work |
| **B. container unused** | a translation exists but the surface never asks for it (`/progress/status`, `/progress/next`, module listings) | same |
| **C. Korean in code** | a literal in `src/` that reaches the user (report Markdown, quiz type labels, stage names, duration strings, account e-mails) | same |
| **D. lesson body** | `<lesson>.en.md` does not exist yet for M5-M10 | the `translator-en` session |

The web front-end is not listed separately: `web/messages/en.json` is at full key parity with `ko.json` and holds no Korean, so every Korean string the reader sees in the web app comes from the API rows below (lesson and module text, the stage chip, report Markdown). `web/e2e/i18n.spec.ts` guards it with the same detector.

## Summary

| surface | Korean runs | distinct fields |
| --- | ---: | ---: |
| API | 7554 | 15 |
| CLI | 20 | 1 |
| content | 375 | 21 |
| source | 19 | 19 |
| static site | 3086 | 52 |

## API

| where | runs | sample |
| --- | ---: | --- |
| `GET /api/v1/lessons/{id}/quiz /questions/*/choices/*` | 2970 | $\theta = 0^\circ$ 이다 |
| `GET /api/v1/lessons/{id}/quiz /questions/*/prompt` | 1580 | 두 벡터의 내적이 음수라면 두 벡터 사이 각도 $\theta$ 에 대해 무엇을 알 수 있는가? |
| `GET /api/v1/lessons/{id} /resources/*/note` | 1196 | 벡터·선형 변환·행렬 곱·외적 편. 직관을 먼저 잡는다. |
| `GET /api/v1/resources /*/note` | 823 | 벡터·선형 변환·행렬 곱·외적 편. 직관을 먼저 잡는다. |
| `GET /api/v1/lessons/{id} /activities/*/title` | 605 | 본문 읽기 |
| `GET /api/v1/lessons/{id} /resources/*/title` | 133 | Modern Robotics (Lynch & Park) 위키 — Linear Algebra Review |
| `GET /api/v1/resources /*/title` | 108 | Modern Robotics (Lynch & Park) 위키 — Linear Algebra Review |
| `GET /api/v1/lessons/{id} /body` | 58 | /rlabbe/Kalman-and-Bayesian-Filters-in-Python> - Inflearn, "현직자가 알려주는 로보틱스 시스템 완전 해부" (in  |
| `GET /api/v1/search?q=robot /*/snippet` | 26 | Modern Robotics (Lynch & Park) 위키 — Linear Algebra Review |
| `GET /api/v1/search?q=robot /*/title` | 26 | Modern Robotics (Lynch & Park) 위키 — Linear Algebra Review |
| `GET /api/v1/courses/{id} /stages/*/modules/*/level` | 10 | 기초 |
| `GET /api/v1/modules/{id} /level` | 10 | 기초 |
| `GET /api/v1/courses/{id} /stages/*/level` | 3 | 기초 |
| `GET /api/v1/progress/status /stages/*/level` | 3 | 기초 |
| `GET /api/v1/roadmap /stages/*/level` | 3 | 기초 |

## CLI

| where | runs | sample |
| --- | ---: | --- |
| `rc resources m1-vectors-matrices` | 20 | 위키 |

## content

| where | runs | sample |
| --- | ---: | --- |
| `m9-learning-based-robotics/{id}` | 48 | activity m9-mdp-decision-making-reading: title |
| `m10-system-integration-capstone/{id}` | 45 | activity m10-system-architecture-requirements-reading: title |
| `m7-manipulation-motion-planning/{id}` | 45 | activity m7-jacobian-singularity-reading: title |
| `m5-state-estimation-slam/{id}` | 44 | activity m5-bayes-filter-reading: title |
| `m6-navigation-planning/{id}` | 42 | activity m6-configuration-space-graph-search-reading: title |
| `m4-sensors-perception/{id}` | 35 | activity m4-sensor-models-reading: title |
| `m8-ros2-tools/{id}` | 32 | activity m8-ros2-concepts-distros-reading: title |
| `m2-kinematics/{id}` | 22 | activity m2-dh-parameters-reading: title |
| `m3-mobile-robots-control/{id}` | 21 | activity m3-differential-drive-reading: title |
| `m1-math-physics/{id}` | 20 | activity m1-vectors-matrices-reading: title |
| `m1-math-physics/module.yaml` | 2 | title / summary |
| `m10-system-integration-capstone/module.yaml` | 2 | title / summary |
| `m2-kinematics/module.yaml` | 2 | title / summary |
| `m3-mobile-robots-control/module.yaml` | 2 | title / summary |
| `m4-sensors-perception/module.yaml` | 2 | title / summary |
| `m5-state-estimation-slam/module.yaml` | 2 | title / summary |
| `m6-navigation-planning/module.yaml` | 2 | title / summary |
| `m7-manipulation-motion-planning/module.yaml` | 2 | title / summary |
| `m8-ros2-tools/module.yaml` | 2 | title / summary |
| `m9-learning-based-robotics/module.yaml` | 2 | title / summary |
| `course.yaml (robotics-expert)` | 1 | title / summary |

## source

| where | runs | sample |
| --- | ---: | --- |
| `src/robotics_curriculum/content/models.py:20` | 1 | 기초 중급 고급 |
| `src/robotics_curriculum/content/models.py:22` | 1 | 기초 중급 고급 |
| `src/robotics_curriculum/content/models.py:32` | 1 | 기초 |
| `src/robotics_curriculum/content/quiz_block.py:11` | 1 | 두 벡터의 내적이 이면 벡터는 |
| `src/robotics_curriculum/content/quiz_block.py:12` | 1 | 평행하다 직교한다 같은 벡터다 영벡터다 |
| `src/robotics_curriculum/content/quiz_block.py:14` | 1 | 내적이 이면 사잇각이 이므로 직교한다 |
| `src/robotics_curriculum/content/quiz_block.py:15` | 1 | 내적이 인 두 벡터의 관계 직교 사잇각 |
| `src/robotics_curriculum/content/sections.py:7` | 1 | 이 단계 공부법 |
| `src/robotics_curriculum/i18n/catalog.py:36` | 1 | 좋아 |
| `src/robotics_curriculum/i18n/scan.py:20` | 1 | 가 힣ᄀ ᇿ㄰ ㆏ꥠ ꥿ힰ ퟿ |
| `src/robotics_curriculum/i18n/scan.py:7` | 1 | 한국어 |
| `src/robotics_curriculum/learn/quiz.py:40` | 1 | 참 예 맞다 |
| `src/robotics_curriculum/learn/quiz.py:41` | 1 | 거짓 아니오 틀리다 |
| `src/robotics_curriculum/learn/review.py:72` | 1 | 내일 예정 |
| `src/robotics_curriculum/learn/stats.py:113` | 1 | 시간 분 |
| `src/robotics_curriculum/learn/stats.py:29` | 1 | 기초 중급 고급 |
| `src/robotics_curriculum/learn/stats.py:30` | 1 | 단계 미지정 |
| `src/robotics_curriculum/site/__init__.py:1` | 1 | 자료실 |
| `src/robotics_curriculum/site/pages.py:79` | 1 | 교재 |

## static site

| where | runs | sample |
| --- | ---: | --- |
| `docs/modules/{id}/index.md` | 857 | 위키 |
| `docs/resources.md` | 569 | 위키 |
| `docs/modules/{id}/m10-career-community-portfolio.md` | 65 | 본문과 |
| `docs/modules/{id}/m10-realtime-safety-reliability.md` | 60 | 본문과 |
| `docs/modules/{id}/m10-hardware-selection-integration.md` | 57 | 본문과 |
| `docs/modules/{id}/m9-sim-to-real-domain-randomization.md` | 56 | 본문과 |
| `docs/modules/{id}/m10-system-architecture-requirements.md` | 53 | 본문과 |
| `docs/modules/{id}/m4-sensor-models.md` | 47 | 본문 |
| `docs/modules/{id}/m10-capstone-project-guide.md` | 46 | 본문과 |
| `docs/modules/{id}/m5-graph-slam-slam-toolbox.md` | 44 | 본문과 |
| `docs/modules/{id}/m4-filtering-basics.md` | 43 | 본문 |
| `docs/modules/{id}/m3-path-following.md` | 42 | 본문 |
| `docs/modules/{id}/m9-datasets-benchmarks-evaluation.md` | 42 | 본문과 |
| `docs/modules/{id}/m3-differential-drive.md` | 38 | 본문 |
| `docs/modules/{id}/m9-robot-learning-overview.md` | 38 | 본문과 |
| `docs/modules/{id}/m7-moveit2-reading.md` | 37 | 본문과 |
| `docs/modules/{id}/m3-pid-control.md` | 36 | 본문 |
| `docs/modules/{id}/m10-testing-ci-deployment.md` | 34 | 본문과 |
| `docs/modules/{id}/m5-odometry-sensor-fusion.md` | 34 | 본문과 |
| `docs/modules/{id}/m6-costmap-global-planning.md` | 33 | 본문과 |
| `docs/modules/{id}/m6-nav2-architecture-behavior-trees.md` | 33 | 본문과 |
| `docs/modules/{id}/m9-mdp-decision-making.md` | 32 | 본문과 |
| `docs/modules/{id}/m5-bayes-filter.md` | 31 | 본문과 |
| `docs/modules/{id}/m1-rotation-representations.md` | 30 | 본문 |
| `docs/modules/{id}/m2-inverse-kinematics.md` | 30 | 본문 |
| `docs/modules/{id}/m4-camera-model-features.md` | 30 | 본문 |
| `docs/modules/{id}/m4-point-clouds-icp-ransac.md` | 30 | 본문 |
| `docs/modules/{id}/m7-trajectory-generation.md` | 30 | 본문과 |
| `docs/modules/{id}/m8-tf2-urdf-visualization.md` | 30 | 본문과 |
| `docs/modules/{id}/m4-object-detection-intro.md` | 29 | 본문 |
| `docs/modules/{id}/m9-reinforcement-learning-basics.md` | 29 | 본문과 |
| `docs/modules/{id}/m1-vectors-matrices.md` | 28 | 본문 |
| `docs/modules/{id}/m2-dh-parameters.md` | 28 | 본문 |
| `docs/modules/{id}/m5-kalman-filter-ekf.md` | 28 | 본문과 |
| `docs/modules/{id}/m7-manipulator-dynamics-torque-control.md` | 28 | 본문과 |
| `docs/modules/{id}/m8-ros2-concepts-distros.md` | 28 | 본문과 |
| `docs/modules/{id}/m1-coordinate-transforms.md` | 27 | 본문 |
| `docs/modules/{id}/m8-nodes-topics-launch.md` | 27 | 본문과 |
| `docs/modules/{id}/m7-manipulator-motion-planning.md` | 26 | 본문과 |
| `docs/modules/{id}/m9-vla-foundation-models.md` | 26 | 본문과 |
| `docs/modules/{id}/m5-occupancy-grid-scan-matching.md` | 25 | 본문과 |
| `docs/modules/{id}/m5-particle-filter-mcl.md` | 25 | 본문과 |
| `docs/modules/{id}/m6-path-smoothing-trajectory.md` | 25 | 본문과 |
| `docs/modules/{id}/m7-jacobian-singularity.md` | 25 | 본문과 |
| `docs/modules/{id}/m8-stacks-dev-environment.md` | 25 | 본문과 |
| `docs/modules/{id}/m8-reference-robot-code.md` | 24 | 본문과 |
| `docs/modules/{id}/m2-forward-kinematics.md` | 23 | 본문 |
| `docs/modules/{id}/m6-local-planning-dwa-mppi.md` | 23 | 본문과 |
| `docs/modules/{id}/m9-imitation-learning-bc-dagger.md` | 23 | 본문과 |
| `docs/modules/{id}/m7-grasping-impedance-control.md` | 21 | 본문과 |
| `docs/modules/{id}/m6-configuration-space-graph-search.md` | 19 | 본문과 |
| `docs/modules/{id}/m6-sampling-based-planning.md` | 17 | 본문과 |
