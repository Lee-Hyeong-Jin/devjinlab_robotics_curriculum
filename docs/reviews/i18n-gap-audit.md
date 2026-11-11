# i18n gap audit - Korean left in the English build

- generated: 2026-11-12 by `uv run python scripts/i18n/audit.py --write`
- Korean runs found: **61718**
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
| API | 40561 | 38 |
| CLI | 852 | 7 |
| content | 411 | 21 |
| source | 82 | 82 |
| static site | 19812 | 55 |

## API

| where | runs | sample |
| --- | ---: | --- |
| `GET /api/v1/lessons/{id} /body` | 24617 | /rlabbe/Kalman-and-Bayesian-Filters-in-Python> - Inflearn, "현직자가 알려주는 로보틱스 시스템 완전 해부" (in  |
| `GET /api/v1/lessons/{id}/quiz /questions/*/choices/*` | 2970 | $\theta = 0^\circ$ 이다 |
| `GET /api/v1/lessons/{id} /study_method` | 1659 | 1. **공식 자습서(먼저):** Jazzy Tutorials 의 *Beginner: CLI tools* 를 문서의 배포 |
| `GET /api/v1/lessons/{id} /objectives/*` | 1596 | 노드·토픽·서비스·액션·파라미터를 구분하고, 주어진 로봇 기능에 어떤 통신 방식이 맞는지 고를 수 있다. |
| `GET /api/v1/lessons/{id}/quiz /questions/*/prompt` | 1580 | 두 벡터의 내적이 음수라면 두 벡터 사이 각도 $\theta$ 에 대해 무엇을 알 수 있는가? |
| `GET /api/v1/progress/status /lessons/*/lesson/summary` | 1322 | 로봇의 위치·자세·속도를 표현하는 기본 도구인 벡터와 행렬 연산을 로보틱스 관점에서 복습한다. |
| `GET /api/v1/lessons/{id} /resources/*/note` | 1196 | 벡터·선형 변환·행렬 곱·외적 편. 직관을 먼저 잡는다. |
| `GET /api/v1/lessons/{id} /summary` | 1077 | ROS 2 를 "노드들이 메시지를 주고받는 계산 그래프"로 이해하고, 토픽·서비스·액션·파라미터의 쓰임과 DDS/RMW· |
| `GET /api/v1/modules/{id} /lessons/*/summary` | 1077 | ROS 2 를 "노드들이 메시지를 주고받는 계산 그래프"로 이해하고, 토픽·서비스·액션·파라미터의 쓰임과 DDS/RMW· |
| `GET /api/v1/resources /*/note` | 823 | 벡터·선형 변환·행렬 곱·외적 편. 직관을 먼저 잡는다. |
| `GET /api/v1/lessons/{id} /activities/*/title` | 605 | 본문 읽기 |
| `GET /api/v1/courses/{id} /stages/*/modules/*/summary` | 323 | 벡터·행렬, 회전 표현, 좌표 변환 등 로봇을 기술하는 데 필요한 수학 도구. |
| `GET /api/v1/modules/{id} /summary` | 323 | 벡터·행렬, 회전 표현, 좌표 변환 등 로봇을 기술하는 데 필요한 수학 도구. |
| `GET /api/v1/progress/status /lessons/*/lesson/title` | 224 | 벡터·행렬 |
| `GET /api/v1/lessons/{id} /title` | 178 | ROS 2 개념과 배포판 선택 |
| `GET /api/v1/modules/{id} /lessons/*/title` | 178 | ROS 2 개념과 배포판 선택 |
| `GET /api/v1/roadmap /stages/*/modules/*/lessons/*/title` | 178 | ROS 2 개념과 배포판 선택 |
| `GET /api/v1/lessons/{id} /resources/*/title` | 133 | Modern Robotics (Lynch & Park) 위키 — Linear Algebra Review |
| `GET /api/v1/resources /*/title` | 108 | Modern Robotics (Lynch & Park) 위키 — Linear Algebra Review |
| `GET /api/v1/reports/weekly /markdown` | 74 | # 주간 리포트 2026-W46 기간: 2026-11-09 ~ 2026-11-15 (기준일 2026-11-12) |
| `GET /api/v1/courses /*/summary` | 46 | 기초→중급→고급의 단계적 경로로 로보틱스 전문가를 기르는 단일 코스(10개 모듈). 기초(M1–M4): 수학·물 |
| `GET /api/v1/courses/{id} /summary` | 46 | 기초→중급→고급의 단계적 경로로 로보틱스 전문가를 기르는 단일 코스(10개 모듈). 기초(M1–M4): 수학·물 |
| `GET /api/v1/progress/next /*/lesson/summary` | 39 | 로봇의 위치·자세·속도를 표현하는 기본 도구인 벡터와 행렬 연산을 로보틱스 관점에서 복습한다. |
| `GET /api/v1/courses/{id} /stages/*/modules/*/title` | 28 | M1 수학·물리 기초 |
| `GET /api/v1/modules/{id} /title` | 28 | M1 수학·물리 기초 |
| `GET /api/v1/roadmap /stages/*/modules/*/title` | 28 | M1 수학·물리 기초 |
| `GET /api/v1/search?q=robot /*/snippet` | 26 | Modern Robotics (Lynch & Park) 위키 — Linear Algebra Review |
| `GET /api/v1/search?q=robot /*/title` | 26 | Modern Robotics (Lynch & Park) 위키 — Linear Algebra Review |
| `GET /api/v1/courses/{id} /stages/*/modules/*/level` | 10 | 기초 |
| `GET /api/v1/modules/{id} /level` | 10 | 기초 |
| `GET /api/v1/reports/weekly /summary/next_lessons/*/detail` | 8 | 시작 전, 예상 60분 |
| `GET /api/v1/progress/next /*/lesson/title` | 5 | 벡터·행렬 |
| `GET /api/v1/reports/weekly /summary/next_lessons/*/title` | 5 | 벡터·행렬 |
| `GET /api/v1/courses /*/title` | 3 | 로보틱스 전문가 코스 |
| `GET /api/v1/courses/{id} /stages/*/level` | 3 | 기초 |
| `GET /api/v1/courses/{id} /title` | 3 | 로보틱스 전문가 코스 |
| `GET /api/v1/progress/status /stages/*/level` | 3 | 기초 |
| `GET /api/v1/roadmap /stages/*/level` | 3 | 기초 |

## CLI

| where | runs | sample |
| --- | ---: | --- |
| `rc show m1-vectors-matrices` | 365 | 벡터 |
| `rc roadmap` | 193 | 로보틱스 |
| `rc status` | 182 | 로보틱스 |
| `rc resources m1-vectors-matrices` | 71 | 벡터 |
| `rc report module m1-math-physics` | 33 | 모듈 |
| `rc next` | 5 | 벡터 |
| `rc --help` | 3 | 이 |

## content

| where | runs | sample |
| --- | ---: | --- |
| `m9-learning-based-robotics/{id}` | 55 | no .en.md translation |
| `m10-system-integration-capstone/{id}` | 51 | no .en.md translation |
| `m7-manipulation-motion-planning/{id}` | 51 | no .en.md translation |
| `m5-state-estimation-slam/{id}` | 50 | no .en.md translation |
| `m6-navigation-planning/{id}` | 48 | no .en.md translation |
| `m8-ros2-tools/{id}` | 37 | no .en.md translation |
| `m4-sensors-perception/{id}` | 35 | activity m4-sensor-models-reading: title |
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
| `src/robotics_curriculum/api/schemas.py:105` | 1 | 이 단계 공부법 |
| `src/robotics_curriculum/api/schemas.py:220` | 1 | 기초 중급 고급 |
| `src/robotics_curriculum/auth/service.py:292` | 1 | 이메일 주소를 확인해 주세요 |
| `src/robotics_curriculum/auth/service.py:293` | 1 | 비밀번호 재설정 |
| `src/robotics_curriculum/auth/service.py:294` | 1 | 초대 |
| `src/robotics_curriculum/auth/service.py:299` | 1 | 이 링크는 분 동안 한 번만 쓸 수 있습니다 요청하지 않았다면 무시하세요 |
| `src/robotics_curriculum/content/models.py:19` | 1 | 기초 중급 고급 |
| `src/robotics_curriculum/content/quiz_block.py:11` | 1 | 두 벡터의 내적이 이면 벡터는 |
| `src/robotics_curriculum/content/quiz_block.py:12` | 1 | 평행하다 직교한다 같은 벡터다 영벡터다 |
| `src/robotics_curriculum/content/quiz_block.py:14` | 1 | 내적이 이면 사잇각이 이므로 직교한다 |
| `src/robotics_curriculum/content/quiz_block.py:15` | 1 | 내적이 인 두 벡터의 관계 직교 사잇각 |
| `src/robotics_curriculum/content/quiz_block.py:155` | 1 | 참 거짓 |
| `src/robotics_curriculum/content/quiz_block.py:42` | 1 | 객관식 |
| `src/robotics_curriculum/content/quiz_block.py:43` | 1 | 다중선택 |
| `src/robotics_curriculum/content/quiz_block.py:45` | 1 | 단답 |
| `src/robotics_curriculum/content/sections.py:7` | 1 | 이 단계 공부법 |
| `src/robotics_curriculum/i18n/catalog.py:36` | 1 | 좋아 |
| `src/robotics_curriculum/i18n/scan.py:20` | 1 | 가 힣ᄀ ᇿ㄰ ㆏ꥠ ꥿ힰ ퟿ |
| `src/robotics_curriculum/i18n/scan.py:7` | 1 | 한국어 |
| `src/robotics_curriculum/learn/quiz.py:40` | 1 | 참 예 맞다 |
| `src/robotics_curriculum/learn/quiz.py:41` | 1 | 거짓 아니오 틀리다 |
| `src/robotics_curriculum/learn/review.py:72` | 1 | 내일 예정 |
| `src/robotics_curriculum/learn/stats.py:107` | 1 | 시간 분 |
| `src/robotics_curriculum/learn/stats.py:108` | 1 | 시간 분 |
| `src/robotics_curriculum/learn/stats.py:113` | 1 | 분 |
| `src/robotics_curriculum/learn/stats.py:114` | 1 | 분 미만 |
| `src/robotics_curriculum/learn/stats.py:122` | 1 | 기초 중급 고급 |
| `src/robotics_curriculum/learn/stats.py:28` | 1 | 기초 중급 고급 |
| `src/robotics_curriculum/learn/stats.py:29` | 1 | 단계 미지정 |
| `src/robotics_curriculum/learn/stats.py:38` | 1 | 단계 미지정 |
| `src/robotics_curriculum/library.py:89` | 1 | 이 단계 공부법 |
| `src/robotics_curriculum/report/module.py:14` | 1 | 완료 진행 중 시작 전 |
| `src/robotics_curriculum/report/module.py:46` | 1 | 모듈 리포트 |
| `src/robotics_curriculum/report/module.py:48` | 1 | 코스 |
| `src/robotics_curriculum/report/module.py:49` | 1 | 진도 레슨 |
| `src/robotics_curriculum/report/module.py:50` | 1 | 누적 학습 시간 |
| `src/robotics_curriculum/report/module.py:52` | 1 | 레슨 |
| `src/robotics_curriculum/report/module.py:57` | 1 | 잠김 |
| `src/robotics_curriculum/report/module.py:68` | 1 | 레슨 상태 시간 이해도 완료일 |
| `src/robotics_curriculum/report/module.py:69` | 1 | 이해도 분포 |
| `src/robotics_curriculum/report/module.py:72` | 1 | 점 개 |
| `src/robotics_curriculum/report/module.py:74` | 1 | 아직 이해도 기록이 없습니다 |
| `src/robotics_curriculum/report/weekly.py:173` | 1 | 일째 진행 중 |
| `src/robotics_curriculum/report/weekly.py:175` | 1 | 이해도 |
| `src/robotics_curriculum/report/weekly.py:190` | 1 | 복습 카드 회 |
| `src/robotics_curriculum/report/weekly.py:192` | 1 | 진행 중 시작 전 |
| `src/robotics_curriculum/report/weekly.py:193` | 1 | 예상 분 |
| `src/robotics_curriculum/report/weekly.py:253` | 1 | 주간 리포트 |
| `src/robotics_curriculum/report/weekly.py:255` | 1 | 기간 기준일 |
| `src/robotics_curriculum/report/weekly.py:257` | 1 | 요약 |
| `src/robotics_curriculum/report/weekly.py:259` | 1 | 학습 시간 |
| `src/robotics_curriculum/report/weekly.py:260` | 1 | 세션 회 학습한 날 일 |
| `src/robotics_curriculum/report/weekly.py:261` | 1 | 완료한 레슨 개 |
| `src/robotics_curriculum/report/weekly.py:262` | 1 | 진행 중인 레슨 개 |
| `src/robotics_curriculum/report/weekly.py:264` | 1 | 모듈별 학습 시간 |
| `src/robotics_curriculum/report/weekly.py:271` | 1 | 모듈 시간 |
| `src/robotics_curriculum/report/weekly.py:273` | 1 | 이번 주 학습 기록이 없습니다 |
| `src/robotics_curriculum/report/weekly.py:275` | 1 | 완료한 레슨 |
| `src/robotics_curriculum/report/weekly.py:281` | 1 | 레슨 이번 주 시간 이해도 |
| `src/robotics_curriculum/report/weekly.py:283` | 1 | 이번 주 완료한 레슨이 없습니다 |
| `src/robotics_curriculum/report/weekly.py:285` | 1 | 진행 중인 레슨 |
| `src/robotics_curriculum/report/weekly.py:288` | 1 | 이번 주 |
| `src/robotics_curriculum/report/weekly.py:292` | 1 | 없음 |
| `src/robotics_curriculum/report/weekly.py:296` | 1 | 문항 회 응시 |
| `src/robotics_curriculum/report/weekly.py:297` | 1 | 퀴즈 정답률 |
| `src/robotics_curriculum/report/weekly.py:299` | 1 | 퀴즈 정답률 기록 없음 |
| `src/robotics_curriculum/report/weekly.py:303` | 1 | 복습 카드 장 |
| `src/robotics_curriculum/report/weekly.py:305` | 1 | 복습 카드 기록 없음 |
| `src/robotics_curriculum/report/weekly.py:306` | 1 | 퀴즈 복습 메모 요약 |
| `src/robotics_curriculum/report/weekly.py:310` | 1 | 이번 주 메모가 없습니다 |
| `src/robotics_curriculum/report/weekly.py:312` | 1 | 막힌 지점 |
| `src/robotics_curriculum/report/weekly.py:316` | 1 | 없음 |
| `src/robotics_curriculum/report/weekly.py:318` | 1 | 다음 주 제안 |
| `src/robotics_curriculum/report/weekly.py:321` | 1 | 시작 |
| `src/robotics_curriculum/report/weekly.py:323` | 1 | 모든 레슨을 완료했습니다 |
| `src/robotics_curriculum/roadmap.py:95` | 1 | 기초 중급 고급 |
| `src/robotics_curriculum/site/__init__.py:1` | 1 | 자료실 |
| `src/robotics_curriculum/site/build.py:246` | 1 | 다크 모드로 전환 |
| `src/robotics_curriculum/site/build.py:253` | 1 | 라이트 모드로 전환 |
| `src/robotics_curriculum/site/pages.py:50` | 1 | 이 단계 공부법 |
| `src/robotics_curriculum/site/pages.py:78` | 1 | 교재 |
| `src/robotics_curriculum/site/pages.py:89` | 1 | 기초 중급 고급 |

## static site

| where | runs | sample |
| --- | ---: | --- |
| `docs/modules/{id}/index.md` | 1187 | 수학 |
| `docs/resources.md` | 642 | 위키 |
| `docs/modules/{id}/m10-realtime-safety-reliability.md` | 572 | 실시간성 |
| `docs/modules/{id}/m10-capstone-project-guide.md` | 571 | 캡스톤 |
| `docs/modules/{id}/m10-system-architecture-requirements.md` | 562 | 로봇 |
| `docs/modules/{id}/m10-testing-ci-deployment.md` | 546 | 테스트 |
| `docs/modules/{id}/m9-datasets-benchmarks-evaluation.md` | 544 | 생태계 |
| `docs/modules/{id}/m9-robot-learning-overview.md` | 542 | 로봇 |
| `docs/modules/{id}/m9-sim-to-real-domain-randomization.md` | 530 | 시뮬레이션 |
| `docs/modules/{id}/m10-career-community-portfolio.md` | 524 | 포트폴리오 |
| `docs/modules/{id}/m10-hardware-selection-integration.md` | 522 | 하드웨어 |
| `docs/modules/{id}/m9-imitation-learning-bc-dagger.md` | 522 | 모방학습 |
| `docs/modules/{id}/m8-ros2-concepts-distros.md` | 504 | 개념과 |
| `docs/modules/{id}/m9-reinforcement-learning-basics.md` | 500 | 강화학습 |
| `docs/modules/{id}/m9-vla-foundation-models.md` | 487 | 로봇 |
| `docs/modules/{id}/m5-particle-filter-mcl.md` | 485 | 파티클 |
| `docs/modules/{id}/m7-grasping-impedance-control.md` | 480 | 파지 |
| `docs/modules/{id}/m6-configuration-space-graph-search.md` | 466 | 구성공간과 |
| `docs/modules/{id}/m9-mdp-decision-making.md` | 464 | 의사결정과 |
| `docs/modules/{id}/m5-bayes-filter.md` | 457 | 확률 |
| `docs/modules/{id}/m6-sampling-based-planning.md` | 457 | 샘플링 |
| `docs/modules/{id}/m7-moveit2-reading.md` | 456 | 읽기 |
| `docs/modules/{id}/m5-kalman-filter-ekf.md` | 455 | 칼만 |
| `docs/modules/{id}/m5-occupancy-grid-scan-matching.md` | 452 | 점유 |
| `docs/modules/{id}/m6-costmap-global-planning.md` | 449 | 비용 |
| `docs/modules/{id}/m8-reference-robot-code.md` | 447 | 레퍼런스 |
| `docs/modules/{id}/m8-stacks-dev-environment.md` | 443 | 상위 |
| `docs/modules/{id}/m6-path-smoothing-trajectory.md` | 435 | 경로 |
| `docs/modules/{id}/m6-nav2-architecture-behavior-trees.md` | 434 | 아키텍처와 |
| `docs/modules/{id}/m5-graph-slam-slam-toolbox.md` | 432 | 그래프 |
| `docs/modules/{id}/m8-nodes-topics-launch.md` | 423 | 노드 |
| `docs/modules/{id}/m7-jacobian-singularity.md` | 411 | 자코비안 |
| `docs/modules/{id}/m6-local-planning-dwa-mppi.md` | 408 | 지역 |
| `docs/modules/{id}/m5-odometry-sensor-fusion.md` | 404 | 오도메트리 |
| `docs/modules/{id}/m8-tf2-urdf-visualization.md` | 395 | 중급 |
| `docs/modules/{id}/m7-manipulator-dynamics-torque-control.md` | 380 | 매니퓰레이터 |
| `docs/modules/{id}/m7-manipulator-motion-planning.md` | 378 | 매니퓰레이터 |
| `docs/modules/{id}/m7-trajectory-generation.md` | 375 | 궤적 |
| `docs/roadmap.md` | 305 | 기초 |
| `mkdocs.yml` | 210 | 로보틱스 |
| `docs/modules/{id}/m4-sensor-models.md` | 50 | 기초 |
| `docs/modules/{id}/m4-filtering-basics.md` | 46 | 기초 |
| `docs/modules/{id}/m3-path-following.md` | 45 | 기초 |
| `docs/modules/{id}/m3-differential-drive.md` | 42 | 기초 |
| `docs/modules/{id}/m3-pid-control.md` | 41 | 기초 |
| `docs/modules/{id}/m1-rotation-representations.md` | 35 | 기초 |
| `docs/modules/{id}/m2-inverse-kinematics.md` | 35 | 기초 |
| `docs/modules/{id}/m4-camera-model-features.md` | 35 | 기초 |
| `docs/modules/{id}/m4-point-clouds-icp-ransac.md` | 35 | 기초 |
| `docs/index.md` | 34 | 로보틱스 |
| `docs/modules/{id}/m1-vectors-matrices.md` | 33 | 기초 |
| `docs/modules/{id}/m4-object-detection-intro.md` | 33 | 기초 |
| `docs/modules/{id}/m1-coordinate-transforms.md` | 32 | 기초 |
| `docs/modules/{id}/m2-dh-parameters.md` | 32 | 기초 |
| `docs/modules/{id}/m2-forward-kinematics.md` | 28 | 기초 |
