# curriculum/

This directory holds the course content: lessons as Markdown with YAML front matter,
organized as Course (Track) > Module > Lesson > Activity.

- Layout, front matter fields and validation rules: `docs/curriculum/CONTENT_MODEL.md`
- Copy-pasteable lesson skeleton: `docs/curriculum/LESSON_TEMPLATE.md`
- Validate everything here: `uv run rc validate` (or `rc validate curriculum/<course>`)

Courses:

- `robotics-expert/` — 로보틱스 전문가 코스 (기초→중급→고급, 10개 모듈).

### robotics-expert 모듈

권장 학습 순서: M1 → M2 → M3 → M4 → M8 → M5 → M6 → M7 → M9 → M10 (표도 이 순서).
예상 시간은 각 레슨 `estimated_minutes` 의 합이다. 퀴즈 문항 수는 각 레슨 본문의
` ```quiz ` 블록 문항 합이며, 모든 레슨이 3문항을 갖는다(수용 기준 AC-4.8b).
`rc quiz <lesson_id>` 로 풀고 오답·개념은 복습 카드가 된다.

| id | 제목 | 단계 | 레슨 수 | 예상 시간 | 퀴즈 문항 수 |
|---|---|---|---|---|---|
| `m1-math-physics` | M1 수학·물리 기초 | 기초 | 3 | 230분 (약 3.8시간) | 9 |
| `m2-kinematics` | M2 로봇 운동학 | 기초 | 3 | 250분 (약 4.2시간) | 9 |
| `m3-mobile-robots-control` | M3 이동 로봇·제어 | 기초 | 3 | 270분 (약 4.5시간) | 9 |
| `m4-sensors-perception` | M4 센서·인식 기초 | 기초 | 5 | 480분 (약 8.0시간) | 15 |
| `m8-ros2-tools` | M8 ROS 2·도구 개요 | 중급 | 5 | 550분 (약 9.2시간) | 15 |
| `m5-state-estimation-slam` | M5 상태 추정·SLAM | 중급 | 6 | 750분 (약 12.5시간) | 18 |
| `m6-navigation-planning` | M6 내비게이션·경로 계획 | 중급 | 6 | 750분 (약 12.5시간) | 18 |
| `m7-manipulation-motion-planning` | M7 매니퓰레이션·동작 계획 | 중급 | 6 | 710분 (약 11.8시간) | 18 |
| `m9-learning-based-robotics` | M9 학습 기반 로보틱스 | 고급 | 7 | 860분 (약 14.3시간) | 21 |
| `m10-system-integration-capstone` | M10 시스템 통합·캡스톤 프로젝트 | 고급 | 6 | 750분 (약 12.5시간) | 18 |
| **합계** | | | **50** | **5,600분 (약 93시간)** | **150** |

Content in this directory is licensed under [CC BY 4.0](LICENSE) (Creative Commons Attribution 4.0 International); code elsewhere in the repository is Apache-2.0.
