# curriculum/

This directory holds the course content: lessons as Markdown with YAML front matter,
organized as Course (Track) > Module > Lesson > Activity.

- Layout, front matter fields and validation rules: `docs/curriculum/CONTENT_MODEL.md`
- Copy-pasteable lesson skeleton: `docs/curriculum/LESSON_TEMPLATE.md`
- Validate everything here: `uv run rc validate` (or `rc validate curriculum/<course>`)

Courses:

- `robotics-expert/` — 로보틱스 전문가 코스 (기초→중급→고급, 11개 모듈).
- `robotics-research/` — 로보틱스 연구원 트랙 (연구 수준, 17개 모듈 106 레슨).

### robotics-expert 모듈

권장 학습 순서: M1 → M2 → M3 → M11 → M4 → M8 → M5 → M6 → M7 → M9 → M10 (표도 이 순서).
M11 은 나중에 추가되어 번호가 뒤에 있고, 마지막 레슨(첫 로봇 만들기)은 선택이다.
예상 시간은 각 레슨 `estimated_minutes` 의 합이다. 퀴즈 문항 수는 각 레슨 본문의
` ```quiz ` 블록 문항 합이며, 모든 레슨이 3문항을 갖는다(수용 기준 AC-4.8b).
`rc quiz <lesson_id>` 로 풀고 오답·개념은 복습 카드가 된다.

| id | 제목 | 단계 | 레슨 수 | 예상 시간 | 퀴즈 문항 수 |
|---|---|---|---|---|---|
| `m1-math-physics` | M1 수학·물리 기초 | 기초 | 3 | 230분 (약 3.8시간) | 9 |
| `m2-kinematics` | M2 로봇 운동학 | 기초 | 3 | 250분 (약 4.2시간) | 9 |
| `m3-mobile-robots-control` | M3 이동 로봇·제어 | 기초 | 3 | 270분 (약 4.5시간) | 9 |
| `m11-actuators-embedded` | M11 액추에이터·임베디드 기초 | 기초 | 6 | 470분 (약 7.8시간) | 18 |
| `m4-sensors-perception` | M4 센서·인식 기초 | 기초 | 5 | 480분 (약 8.0시간) | 15 |
| `m8-ros2-tools` | M8 ROS 2·도구 개요 | 중급 | 6 | 610분 (약 10.2시간) | 18 |
| `m5-state-estimation-slam` | M5 상태 추정·SLAM | 중급 | 6 | 750분 (약 12.5시간) | 18 |
| `m6-navigation-planning` | M6 내비게이션·경로 계획 | 중급 | 6 | 750분 (약 12.5시간) | 18 |
| `m7-manipulation-motion-planning` | M7 매니퓰레이션·동작 계획 | 중급 | 6 | 710분 (약 11.8시간) | 18 |
| `m9-learning-based-robotics` | M9 학습 기반 로보틱스 | 고급 | 7 | 860분 (약 14.3시간) | 21 |
| `m10-system-integration-capstone` | M10 시스템 통합·캡스톤 프로젝트 | 고급 | 6 | 750분 (약 12.5시간) | 18 |
| **합계** | | | **57** | **6,130분 (약 102시간)** | **171** |

### robotics-research 모듈

연구원 트랙(`robotics-research/`)은 설계안(`research_notes/연구 트랙 설계/blueprint.md`)의 17개
모듈 106 레슨이 모두 한국어·영어로 들어 있다. 경로는 F0 → R0 → 공통 코어 C1~C8 →
specialization S1~S5 중 선택 → R1·R2 이고, 모든 모듈의 수준은 `연구`다. 논문은 코스 레지스트리
`robotics-research/papers.yaml`(ADR 0014)로 건다. 집필 규칙은
`docs/curriculum/AUTHORING_RESEARCH_TRACK.md`.

| id | 제목 | 레슨 수 | en 번역 | 예상 시간 | 퀴즈 문항 수 |
|---|---|---|---|---|---|
| `f0-foundations-from-zero` | F0 시작 전 기초 | 9 | 9 / 9 | 30,640분 (약 511시간) | 51 |
| `r0-math-numerical-foundations` | R0 수학·수치 기초 (브리지) | 7 | 7 / 7 | 3,090분 (약 52시간) | 28 |
| `c1-rigid-body-geometry-lie-groups` | C1 강체 기하와 리 군 | 5 | 5 / 5 | 2,310분 (약 38시간) | 20 |
| `c2-multibody-dynamics` | C2 다물체 동역학 | 6 | 6 / 6 | 3,240분 (약 54시간) | 30 |
| `c3-nonlinear-robust-control` | C3 비선형·강건 제어 | 6 | 6 / 6 | 3,180분 (약 53시간) | 24 |
| `c4-optimal-control-trajectory-optimization` | C4 최적 제어·궤적 최적화 | 7 | 7 / 7 | 4,440분 (약 74시간) | 46 |
| `c5-state-estimation-manifolds` | C5 상태 추정 | 6 | 6 / 6 | 3,780분 (약 63시간) | 30 |
| `c6-motion-planning-theory` | C6 동작 계획 이론 | 7 | 7 / 7 | 3,360분 (약 56시간) | 40 |
| `c7-perception-3d-representations` | C7 지각과 3D 표현 | 6 | 6 / 6 | 3,900분 (약 65시간) | 30 |
| `c8-decision-making-learning-theory` | C8 의사결정·학습 이론 | 8 | 8 / 8 | 4,200분 (약 70시간) | 40 |
| `s1-slam-spatial-ai` | S1 SLAM·공간 지능 | 6 | 6 / 6 | 3,570분 (약 60시간) | 33 |
| `s2-manipulation-contact` | S2 조작·접촉 | 6 | 6 / 6 | 2,980분 (약 50시간) | 36 |
| `s3-legged-underactuated` | S3 보행·언더액추에이티드 | 6 | 6 / 6 | 3,090분 (약 52시간) | 28 |
| `s4-robot-learning-foundation-models` | S4 로봇 학습·파운데이션 모델 | 6 | 6 / 6 | 2,850분 (약 48시간) | 32 |
| `s5-multi-robot-field-robotics` | S5 다중 로봇·필드 로보틱스 | 6 | 6 / 6 | 3,570분 (약 60시간) | 32 |
| `r1-research-methodology` | R1 연구 방법론 | 6 | 6 / 6 | 2,490분 (약 42시간) | 24 |
| `r2-capstone` | R2 캡스톤 | 3 | 3 / 3 | 12,000분 (약 200시간) | 12 |
| **합계** | | **106** | **106 / 106** | **92,690분 (약 1,545시간)** | **536** |

### 번역 현황 (en)

영어 판은 원문 옆의 형제 파일 `<lesson>.en.md` 다(`docs/curriculum/CONTENT_MODEL.md`
"레슨 번역", ADR 0012). 번역은 텍스트만 담고 구조 필드는 원문에만 있다. 번역이 없는 레슨은
한국어 원문으로 폴백한다(`translated: false`). 영어 사이트는 `uv run rc site build --lang en`.

| 모듈 | 레슨 수 | en 번역 | 비고 |
|---|---|---|---|
| `m1-math-physics` | 3 | 3 / 3 | 완료 |
| `m2-kinematics` | 3 | 3 / 3 | 완료 |
| `m3-mobile-robots-control` | 3 | 3 / 3 | 완료 |
| `m4-sensors-perception` | 5 | 5 / 5 | 완료 |
| `m8-ros2-tools` | 5 | 5 / 5 | 완료 |
| `m5-state-estimation-slam` | 6 | 6 / 6 | 완료 |
| `m6-navigation-planning` | 6 | 6 / 6 | 완료 |
| `m7-manipulation-motion-planning` | 6 | 6 / 6 | 완료 |
| `m9-learning-based-robotics` | 7 | 7 / 7 | 완료 |
| `m10-system-integration-capstone` | 6 | 6 / 6 | 완료 |
| **합계** | **50** | **50 / 50** | 전 모듈 완료 |

번역본에는 ` ```quiz ` 블록을 넣지 않는다. CONTENT_MODEL 의 "레슨 번역" 절이 퀴즈 블록을
다루지 않아 문항 id·활동 참조가 중복될 수 있기 때문이다. 영어 학습자도 `rc quiz <lesson_id>`
로 한국어 원문의 퀴즈를 풀 수 있고, 규칙이 정해지면 번역을 추가한다.

Content in this directory is licensed under [CC BY 4.0](LICENSE) (Creative Commons Attribution 4.0 International); code elsewhere in the repository is Apache-2.0.
