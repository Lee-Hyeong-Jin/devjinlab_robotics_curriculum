# i18n gap audit - Korean left in the English build

- generated: 2026-11-12 by `uv run python scripts/i18n/audit.py --write`
- Korean runs found: **4147**
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
| API | 3856 | 12 |
| content | 119 | 7 |
| source | 19 | 19 |
| static site | 153 | 13 |

## API

| where | runs | sample |
| --- | ---: | --- |
| `GET /api/v1/lessons/{id}/quiz /questions/*/choices/*` | 2504 | 토픽 — 명령을 계속 흘려보낸다 |
| `GET /api/v1/lessons/{id}/quiz /questions/*/prompt` | 1142 | 로봇 팔에 "물체를 집어라"를 지시하는 인터페이스로 가장 알맞은 것은? |
| `GET /api/v1/lessons/{id} /resources/*/title` | 67 | 현직자가 알려주는 로보틱스 시스템 완전 해부 (인프런, jelly) |
| `GET /api/v1/lessons/{id} /body` | 58 | /rlabbe/Kalman-and-Bayesian-Filters-in-Python> - Inflearn, "현직자가 알려주는 로보틱스 시스템 완전 해부" (in  |
| `GET /api/v1/resources /*/title` | 50 | 현직자가 알려주는 로보틱스 시스템 완전 해부 (인프런, jelly) |
| `GET /api/v1/courses/{id} /stages/*/modules/*/level` | 10 | 기초 |
| `GET /api/v1/modules/{id} /level` | 10 | 기초 |
| `GET /api/v1/courses/{id} /stages/*/level` | 3 | 기초 |
| `GET /api/v1/lessons/{id} /resources/*/note` | 3 | 13 h 13 min, paid. A Korean alternative is "[R2R] 무작정 따라하는 ROS2 입문과정" (https://www.udemy.c |
| `GET /api/v1/progress/status /stages/*/level` | 3 | 기초 |
| `GET /api/v1/resources /*/note` | 3 | 13 h 13 min, paid. A Korean alternative is "[R2R] 무작정 따라하는 ROS2 입문과정" (https://www.udemy.c |
| `GET /api/v1/roadmap /stages/*/level` | 3 | 기초 |

## content

| where | runs | sample |
| --- | ---: | --- |
| `m10-system-integration-capstone/{id}` | 21 | resource 0: title / note |
| `m9-learning-based-robotics/{id}` | 21 | quiz q1 |
| `m5-state-estimation-slam/{id}` | 20 | quiz q1 |
| `m6-navigation-planning/{id}` | 19 | quiz q1 |
| `m7-manipulation-motion-planning/{id}` | 19 | quiz q1 |
| `m8-ros2-tools/{id}` | 17 | resource 2: title / note |
| `m4-sensors-perception/{id}` | 2 | resource 3: title / note |

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
| `docs/modules/{id}/index.md` | 49 | 현직자가 |
| `docs/resources.md` | 35 | 문서 |
| `docs/modules/{id}/m10-hardware-selection-integration.md` | 9 | 현직자가 |
| `docs/modules/{id}/m10-realtime-safety-reliability.md` | 9 | 현직자가 |
| `docs/modules/{id}/m10-system-architecture-requirements.md` | 9 | 현직자가 |
| `docs/modules/{id}/m5-graph-slam-slam-toolbox.md` | 8 | 최종명 |
| `docs/modules/{id}/m5-odometry-sensor-fusion.md` | 8 | 최종명 |
| `docs/modules/{id}/m4-sensor-models.md` | 7 | 현직자가 |
| `docs/modules/{id}/m6-nav2-architecture-behavior-trees.md` | 6 | 자율주행 |
| `docs/modules/{id}/m7-moveit2-reading.md` | 5 | 이성원 |
| `docs/modules/{id}/m8-nodes-topics-launch.md` | 3 | 무작정 |
| `docs/modules/{id}/m8-ros2-concepts-distros.md` | 3 | 문서 |
| `docs/modules/{id}/m4-object-detection-intro.md` | 2 | 입문 |
