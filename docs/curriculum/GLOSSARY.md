# 용어집 (ko ↔ en)

이 저장소의 한국어 원문과 영어 번역(`<lesson>.en.md`, `<lesson>.en.yaml`,
`module.en.yaml`, `course.en.yaml`, `web/messages/en.json`,
`src/robotics_curriculum/i18n/locales/en.yaml`)이 같은 용어를 쓰게 하는 단일 출처다.

규칙:

- **원문**: 한국어 본문은 기술 용어에 영문을 병기한다 — 정기구학(forward kinematics).
  영어 번역에서는 영문만 쓰고 한국어를 병기하지 않는다.
- **번역하지 않는 것**: 제품·라이브러리·규격 이름(ROS 2, Nav2, MoveIt 2, RViz, URDF, tf2,
  rosbag2, MCAP, Foxglove, ros2_control, micro-ROS, NumPy, SciPy, LeRobot, OMPL, PyTorch),
  논문·강의·책 제목, 사람 이름, 식별자(레슨·모듈·활동 id, `level` 값).
- **고정 값**: `module.yaml` 의 `level` 은 `기초|중급|고급` 그대로 둔다. 화면에 보이는 라벨만
  `level.foundation|intermediate|advanced` 메시지 키로 번역한다(ADR 0012).
- 새 용어를 쓰기 전에 여기 추가하고, 이미 있는 항목과 다른 번역을 쓰지 않는다.

## 단계·구조

| 한국어 | English | 비고 |
|---|---|---|
| 코스 | course | |
| 모듈 | module | |
| 레슨 | lesson | |
| 활동 | activity | |
| 단계 | stage | 목록 묶음. `level` 값의 표시 라벨 |
| 기초 | Foundation | `level` 내부 값은 `기초` 로 유지 |
| 중급 | Intermediate | |
| 고급 | Advanced | |
| 단계 미지정 | No stage | `level` 이 없는 모듈 |
| 선수지식 / 선수 레슨 | prerequisite | |
| 학습 목표 | objective | |
| 난이도 | difficulty | |
| 예상 시간 | estimated time | |
| 본문 읽기 | Read the lesson | 활동 제목 |
| 확인 퀴즈 | Check-your-understanding quiz | 활동 제목 |
| 이 단계 공부법 | How to study this stage | 레슨 본문의 `## ` 절 제목 |
| 학습 자료 | study resources | |
| 자료실 | Resources | 사이트·웹의 페이지 이름 |
| 교재 | Books | `resource.kind: book` |
| 강의 | Courses | `resource.kind: course` |
| 영상 | Videos | `resource.kind: video` |
| 글·문서 | Articles | `resource.kind: article` |

## 진행도·복습

| 한국어 | English | 비고 |
|---|---|---|
| 진행도 | progress | 문서의 정식 용어 |
| 진행 중 | in progress | |
| 완료 | done | |
| 시작 전 | not started | |
| 잠김 | locked | 선수 레슨 미완료 |
| 이해도 | understanding | 1–5 자기 평가 |
| 연속 학습 | streak | |
| 복습 카드 / 플래시카드 | flashcard | |
| 오늘 복습 | due today | |
| 간격 반복 | spaced repetition | SM-2 |
| 객관식 | single choice | 퀴즈 유형 |
| 다중선택 | multiple choice | |
| O/X | true/false | |
| 단답 | short answer | |
| 해설 | explanation | |
| 개념 카드 | concept card | 퀴즈 문항의 `concept` |
| 주간 리포트 | weekly report | |
| 막힌 지점 | where you are stuck | |

## 로보틱스 용어

| 한국어 | English | 비고 |
|---|---|---|
| 벡터 / 행렬 | vector / matrix | |
| 내적 / 외적 | dot product / cross product | |
| 역행렬 / 전치 / 행렬식 | inverse / transpose / determinant | |
| 회전 행렬 | rotation matrix | |
| 쿼터니언 | quaternion | |
| 오일러 각 | Euler angles | |
| 좌표계 | frame | "coordinate frame" |
| 좌표 변환 | coordinate transform | |
| 동차 변환 행렬 | homogeneous transformation matrix | |
| 강체 | rigid body | |
| 정기구학 | forward kinematics | |
| 역기구학 | inverse kinematics | |
| 기구학 | kinematics | |
| 동역학 | dynamics | |
| DH 파라미터 | DH parameters | Denavit-Hartenberg |
| 말단 장치 | end-effector | |
| 자코비안 | Jacobian | |
| 특이점 | singularity | |
| 작업 공간 | workspace | |
| 관절 공간 | joint space | |
| 구성공간 | configuration space | C-space |
| 궤적 생성 | trajectory generation | |
| 경로 계획 | path planning | |
| 동작 계획 | motion planning | |
| 전역 계획 / 지역 계획 | global planning / local planning | |
| 비용 지도 | costmap | |
| 경로 평활화 | path smoothing | |
| 샘플링 기반 계획 | sampling-based planning | PRM, RRT, RRT* |
| 장애물 회피 | obstacle avoidance | |
| 행동 트리 | behaviour tree | 영국식 철자로 통일 |
| 차동 구동 | differential drive | |
| 경로 추종 | path following | |
| 전방 주시 거리 | look-ahead distance | |
| 오도메트리 | odometry | |
| 피드백 제어 | feedback control | |
| 와인드업 | windup | integral windup |
| 임피던스 제어 | impedance control | |
| 계산 토크 제어 | computed-torque control | |
| 파지 | grasping | |
| 매니퓰레이터 | manipulator | |
| 매니퓰레이션 | manipulation | |
| 센서 융합 | sensor fusion | |
| 관측 모델 | observation model | |
| 상태 추정 | state estimation | |
| 베이즈 필터 | Bayes filter | |
| 칼만 필터 | Kalman filter | EKF = extended Kalman filter |
| 파티클 필터 | particle filter | |
| 몬테카를로 로컬라이제이션 | Monte Carlo localisation | MCL |
| 점유 격자 지도 | occupancy-grid map | |
| 스캔 매칭 | scan matching | |
| 점군 | point cloud | |
| 이미지 특징 | image feature | |
| 객체 인식 | object detection | |
| 인식 | perception | 센서 해석 전반 |
| 의사결정 | decision making | |
| 강화학습 | reinforcement learning | RL |
| 정책 경사 | policy gradient | |
| 가치 반복 / 정책 반복 | value iteration / policy iteration | |
| 모방학습 | imitation learning | |
| 행동 복제 | behaviour cloning | |
| 도메인 랜덤화 | domain randomisation | |
| 로봇 파운데이션 모델 | robot foundation model | |
| 데이터셋 / 벤치마크 | dataset / benchmark | |
| 노드 / 토픽 / 서비스 / 액션 | node / topic / service / action | ROS 2 개념 |
| 계산 그래프 | computation graph | |
| 배포판 | distribution | ROS 2 distro |
| 실시간성 | real-time behaviour | |
| 페일세이프 | fail-safe | |
| 기능 안전 | functional safety | |
| 시스템 통합 | system integration | |
| 하드웨어 통합 | hardware integration | |
| 캡스톤 프로젝트 | capstone project | |
