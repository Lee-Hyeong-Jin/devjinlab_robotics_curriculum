# 대학원 수준 로보틱스 과정 벤치마크 (Graduate Robotics Curriculum Benchmark)

> 목적: 로보틱스 **연구원(researcher)** 트랙 설계([blueprint.md](blueprint.md))의 근거.
> 세계 최상위 대학원의 실제 강의계획(주차별 주제·과제·교재·선수과목)과 박사과정 자격시험·리딩리스트
> 수준을 확인된 자료로 정리한다.
>
> **확인 규칙**: `확인` = 2026-11-12 에 이 조사 세션이 해당 URL 을 실제로 fetch 해서 그 과목의
> 페이지임을 확인했다. `(미확인)` = 검색 스니펫만 있거나 fetch 가 실패했다. 주차별 목록은 fetch 한
> 페이지가 준 것만 옮겼고, 페이지에 일정이 없으면 `스케줄 미공개` 로 적는다. 과목 주제 제목은
> 원문(영문)을 유지한다.
>
> 한국어 자료는 이 벤치마크의 대상이 아니다(사용자 지시 2026-11-12: 기준은 세계 최상위 대학원과
> 국제 학회 수준). 기존 `research_notes/로보틱스 학습 자료 조사/` 의 `korean_resources_ecosystem.md`
> 는 참고하지 않았다.

## 0. 한눈에 보기 — 대학원 과목이 실제로 가르치는 것

조사한 과목 전체에서 반복적으로 나타난 **코어(core)** 와 그 과목 수:

| 영역 | 확인된 과목 | 공통 형식 |
|---|---|---|
| 강체 기하 · 리 군 (rigid-body geometry, Lie groups) | CMU 16-711 Ch1–2, MIT 16.485 L2–5, CMU 16-745 W9, Berkeley C106B | 지수 좌표·product of exponentials·manifold 위 최적화 |
| 다물체 동역학 (multibody dynamics) | CMU 16-711 Ch3–4, Stanford CS223A, MIT 6.8210 | Lagrange/Newton-Euler 유도 + 재귀 알고리즘 구현 |
| 최적 제어 · 궤적 최적화 (optimal control, trajopt) | CMU 16-745(전체), Stanford AA203(전체), Berkeley CS287, MIT 6.8210 | LQR → iLQR/DDP → 직접법/collocation → MPC, 과제는 전부 구현 |
| 상태 추정 · SLAM (state estimation, SLAM) | CMU 16-833, MIT 16.485 L16–30, UPenn ESE 650 M1, Berkeley C106B W7–8 | 인자 그래프(factor graph)·희소성·manifold 최적화·강건 추정 |
| 동작 계획 (motion planning) | CMU 16-782(전체), MIT 16.410, Stanford AA274A | A*/weighted A*/anytime → PRM/RRT/RRT* → 기호 계획·불확실성 |
| 조작 · 접촉 (manipulation, contact) | MIT 6.4210/6.4212, Stanford CS326, Berkeley C106B W9–10 | 파지 해석 → 학습 기반 파지 → 접촉 활용(extrinsic dexterity) |
| 다시점 기하 · 지각 (multi-view geometry, perception) | CMU 16-822, Stanford CS231A, MIT 16.485 L11–15 | 투영 기하 → 2-view/N-view → 학습 기반 SfM/SLAM |
| 로봇 학습 · RL (robot learning) | Berkeley CS285(전체), Stanford AA274B/CS237B, CMU 16-831, UPenn ESE 650 M3 | 모방학습 → 정책 경사 → 가치 기반 → 모델 기반 → 오프라인 RL |
| 비선형 제어 (nonlinear control) | Berkeley C106B W1–4, CMU 16-711 Ch5–6, Stanford CS223A | Lyapunov·feedback linearization·controllability·impedance |

**형식의 공통점** (연구 트랙 설계에 그대로 반영):
1. **과제가 전부 구현이다.** 16-745 는 4개 과제를 GitHub 으로 배포하고 Gradescope 로 받는다.
   CS287 은 5개 문제 세트가 value iteration, iLQR/DDP, convex/SCP, Kalman/particle filter, RL 구현이다.
   Berkeley C106B 는 Project 1–4(visual servoing, nonholonomic control, state estimation, grasping).
2. **최종 과제가 학회 포맷 논문이다.** CMU 16-745: 1–5인 팀, 발표 + **ICRA/IROS 포맷 6페이지 보고서**.
   Berkeley CS287: 1–2인, 약 6페이지 논문. UPenn MEAM 620: "conference-quality final report".
3. **세미나 과목은 논문 리뷰가 주 활동이다.** Stanford CS326 은 매 세션 전날까지 **논문 리뷰 + 튜토리얼
   질문**을 제출하고, 수업은 튜토리얼 발표 + 토론(debate)이며, 최종 과제는 **연구 제안서(research
   proposal)** + 동료 리뷰(peer review)다.
4. **교재는 필수가 아니다.** 16-745·16-782·16-822·6.4212·CS326 모두 필수 교재 없음. 온라인 노트
   (Tedrake)와 원 논문이 1차 자료다.

## 1. MIT

### 1.1 MIT 6.8210 (구 6.832) Underactuated Robotics — Russ Tedrake
- URL: <https://underactuated.csail.mit.edu/> `확인` (노트 사이트),
  <https://underactuated.csail.mit.edu/Spring2024/> `확인` (과목 페이지),
  <https://underactuated.csail.mit.edu/Spring2024/schedule.html> `확인` (내용은 스텁)
- 학기: Spring 2024. 주차별 일정은 **스케줄 미공개**(페이지가 비어 있음).
- 교재: 저자의 온라인 노트 자체(PDF 판 있음) + YouTube 강의. 노트 목차는 `2 Simple Pendulum` …
  `21 Imitation Learning` + 부록. (3–20장 제목은 **미확인**)
- 과제: Gradescope 문제 세트(Python) 35% + 최종 프로젝트 35%. 각 장 끝 연습문제. 부록 E 에
  과거 우수 프로젝트 모음.
- 선수: 선형대수와 미분방정식에 익숙할 것, 최적화 지식 권장, Python.
- 구판(OCW): <https://ocw.mit.edu/courses/6-832-underactuated-robotics-spring-2009/> `확인` —
  nonlinear dynamics of passive robots, motion planning, partial feedback linearization,
  energy-shaping control, analytical optimal control, RL and approximate optimal control,
  influence of mechanical design on control.

### 1.2 MIT 6.4210 / 6.4212 Robotic Manipulation — Lozano-Pérez, Kaelbling, Tedrake
- URL: <https://manipulation.csail.mit.edu/> `확인`,
  <https://manipulation.csail.mit.edu/Fall2026/index.html> `확인`,
  <https://manipulation.csail.mit.edu/Fall2026/schedule.html> `확인`(강의 목록 미획득)
- 학기: Fall 2026. 6.4212 는 대학원판(12 units)으로 **문제 세트에 추가 문항**이 붙는다.
- 노트 목차(= 사실상 과정 구조): 1 Introduction · 2 Let's get you a robot · 3 Basic Pick and Place ·
  4 Geometric Pose Estimation · 5 Bin Picking · 6 Motion Planning · 7 Mobile Manipulation ·
  8 Manipulator Control · 9 Object Detection and Segmentation · 10 Deep Perception for Manipulation ·
  11 Reinforcement Learning · 12 Soft Robots and Tactile Sensing (+ 부록: spatial algebra, Drake,
  DrakeGym, Manipulation Station)
- 과제: 학기 2/3 지점까지 거의 매주 문제 세트(수식 + Drake Python), 중간 퀴즈 2회, 자유 주제 최종
  프로젝트(제안서 → 보고서 → 영상 → 요약). 공개 범위: 문제 세트 1–6, 퀴즈 1 해답, 중간 연습문제.
- 교재: 필수 없음. 선택 Craig / Modern Robotics / Boyd–Vandenberghe.
- 선수: 기초 선형대수·확률·알고리즘, 신경망 기본, Python. 로보틱스 배경 불필요.

### 1.3 MIT 16.485 Visual Navigation for Autonomous Vehicles (VNAV) — Luca Carlone
- URL: <https://vnav.mit.edu/> `확인`, <https://vnav.mit.edu/syllabus.html> `확인`(Fall 2024),
  <https://vnav.mit.edu/lectures.html> `확인`,
  <https://ocw.mit.edu/courses/16-485-visual-navigation-for-autonomous-vehicles-vnav-fall-2020/> `확인`
- **강의 목록(연구 트랙 SLAM 모듈의 직접적 근거)**: 1 Introduction · 2–3 Basic 3D Geometry ·
  4–5 Lie Groups · 6 Quadrotor Model · 7 Quadrotor Controller · 8 Trajectory Optimization (1) ·
  9–10 Trajectory Optimization (2) · 11 Image Formation · 12–13 Feature Detection and Tracking ·
  14 2-View Geometry · 15 RANSAC · 16 From Optimization to Estimation Theory and Back ·
  17 Introduction to Non-Linear Estimation · 18–19 **Optimization on Manifolds** ·
  20 Visual and Visual-Inertial Odometry · 21 Place Recognition · 22 Bag-of-Words and Object
  Detection · 23 **SLAM I: Formulations and Sparsity** · 24 **SLAM II: Factor Graphs and
  Marginalization** · 25–26 Beyond Cameras · 27 Dense 3D Reconstruction · 28 Research Directions
  in SLAM · 29–30 **Robust Estimation** · 31 Deep Learning Architectures on 3D Data ·
  32 Geometric Deep Learning · 33 GDL and Graph Neural Networks
- 과제: Lab 1–9.5. Lab 1 = Ubuntu 22.04/shell/Git/C++/CMake, Lab 2 = ROS 설치·입문(이후 랩 제목
  미확인). OCW 판은 프로그래밍 과제 + 미니 레이스카·드론 실습 + **최근 연구 비평(critical review)**
  + 팀 프로젝트.
- 교재·선수: fetch 한 페이지에 없음(**미확인**). 2024 실라버스 문서(tinyurl)는 미획득.

### 1.4 MIT 16.410 / 16.413 Principles of Autonomy and Decision Making
- URL: <https://ocw.mit.edu/courses/16-410-principles-of-autonomy-and-decision-making-fall-2010/pages/calendar> `확인`
  (Fall 2010; Williams, Frazzoli, Karaman)
- 25개 세션: state-space search; search complexity, soundness and completeness; constraint
  programming; conflict-directed backjumping; activity planning; GraphPlan; plan execution;
  propositional logic and SAT; planning as SAT; diagnosis and mode estimation; OpSat and
  conflict-directed A*; informed-search path planning; sampling-based motion planning;
  mathematical programming (simplex, MILP for routing and motion planning); reasoning under
  uncertainty; HMMs and Baum-Welch; MDPs and policy iteration; sequential and differential games.
- 과제: 문제 세트 10개 + 중간고사 + 2부 최종 프로젝트.
- 기타 MIT: 2.12 Introduction to Robotics (OCW Fall 2005) `확인` — kinematics and motion planning,
  manipulator and mobile robot design, multi-rigid-body dynamics, control design, actuators,
  sensors, embedded software + 주간 랩 + 팀 프로젝트.
  16.S690/6.S080 Introduction to Autonomy (Spring 2026, Karaman) `확인` — graph search, probability,
  optimization frameworks, learning from experience; 문제 세트 5 + 퀴즈 3.

## 2. Stanford

### 2.1 CS223A / ME320 Introduction to Robotics — Khatib
- URL: <http://cs.stanford.edu/groups/manips/teaching/cs223a/> `확인` · 학기: Winter 2026
- 순서: Introduction · spatial descriptions · essential math review · articulated body systems ·
  forward kinematics · **Jacobians (3 강의)** · inverse kinematics and workspace · trajectory
  generation · (중간고사) · essential physics review · **dynamics: acceleration and inertia /
  Newton-Euler / explicit form** · joint space control · **operational space control** · (기말)
- 과제: 지필 숙제 8세트(Gradescope). 숙제 40% + 중간 25% + 기말 35%. — **지필 비중이 큰 유일한 과목**
- 교재: Course Reader(필수), 선택 Siciliano et al.

### 2.2 AA203 Optimal and Learning-based Control — Pavone, Gammelli
- URL: <https://stanfordasl.github.io/aa203/sp2526/> `확인` · 학기: Spring 2026
- **주차별**: W1 course overview, intro to nonlinear optimization, optimization theory ·
  W2 calculus of variations, indirect methods · W3 **Pontryagin's maximum principle**,
  continuous-time LQR, direct methods (collocation, SCP) · W4 dynamic programming, discrete LQR,
  **nonlinear LQR for tracking (iLQR, DDP)** · W5 stochastic DP, value/policy iteration,
  **HJB, HJI and reachability analysis** · W6 **MPC I–II (persistent feasibility, stability,
  explicit MPC)** · W7 learning, system ID and adaptive control, intro to imitation learning and RL ·
  W8 imitation learning, RL I · W9 RL II (model-free, value-based) · W10 RL III (policy
  optimization), RL IV (model-based), world models for robotics · W11 기말
- 과제: HW0(비채점) + HW1–HW4(4·6·8·10주차 마감). 실라버스 PDF 는 미획득.

### 2.3 AA274A / CS237A Principles of Robot Autonomy I — Schwager (Fall 2025)
- URL: <https://stanfordasl.github.io/PoRA-I/aa274a_aut2526> `확인`
- 주제: perception-action loop, maps, robot geometry, SE(2)/SE(3) transforms · collision checking,
  C-space, motion models, path planning (A*, RRT, RRT*) · trajectory optimization and following
  (PID, LQR, gain-scheduled LQR) · robotic sensors, point clouds, ICP, pinhole cameras,
  calibration · structure from motion, features, RANSAC, learning-based and semantic perception ·
  SLAM, factor graphs, pose graph optimization, bundle adjustment · Bayes rule, occupancy mapping,
  frontier exploration · Gaussians, Kalman/EKF/UKF, particle filtering, MCL · EKF localization,
  object tracking, advanced topics (imitation learning, **VLAs, 3DGS for sim2real, world models**)
- 과제: 숙제 5개(각 4%) + 랩 0–8 + 중간 15% + 기말 25%.
- 선수: CS106A, CME100(공학 수학), CME106(확률·통계) 또는 동급.

### 2.4 AA274B / CS237B Principles of Robot Autonomy II — Bohg, Pavone, Sadigh
- URL: <https://web.stanford.edu/class/cs237b/> `확인` · 학기: Winter 2025
- **주차별**: W1 ML for robotics, neural networks and PyTorch · W2 MDPs, intro to RL ·
  W3 model-based and model-free RL for robot control · W4 learning-based perception, grasping and
  manipulation I · W5 grasping and manipulation II, learning-based grasping · W6 learning-based
  manipulation, interactive perception · W7 imitation learning I · W8 imitation learning II,
  **learning from human feedback** · W9 interaction-aware learning, planning and control; shared
  autonomy · W10 guest lectures
- 과제: HW1–3 + 시험 3회. 4학점 선택 시 **프로젝트 보고서** 필수.
- 선수: CS106A, CME100, CME106, AA174A/274A.

### 2.5 CS326 Topics in Advanced Robotic Manipulation — Bohg (Fall 2024 추정)
- URL: <https://web.stanford.edu/class/cs326/syllabus.html> `확인`,
  <https://web.stanford.edu/class/cs326/index.html> `확인` (학기 표기 없음, 생성일 2024-09-22)
- **형식(연구 세미나의 표준형)**: 매 세션 = 논문 리뷰 제출 + 튜토리얼 발표 + 토론(debate).
  최종 산출물 = **연구 제안서**(초안 → 전체 → 동료 리뷰 → 발표).
- **14개 주제와 대표 논문**: 1 Classic Contact-Based Grasping (Planning Optimal Grasps; FRoGGeR) ·
  2 Grasp Synergies and Taxonomies (GRASP Taxonomy; Pisa/IIT SoftHand) · 3 Exploiting Contact
  Constraints (Extrinsic Dexterity) · 4 Learning to Grasp (Dex-Net 2.0; QT-Opt; Contact-GraspNet;
  AnyGrasp) · 5 Trajectory Optimization for Motion Planning (sequential convex optimization;
  vectorized sampling-based planning; **Graphs of Geodesically-Convex Sets**) · 6 RL for
  Manipulation (End-to-End Visuomotor Policies; dexterous in-hand manipulation) · 7 Imitation
  Learning (DAgger; **Diffusion Policy**; ALOHA; MimicPlay) · 8 Sensorimotor Adaptation (Residual
  policy learning; **Rapid Motor Adaptation**) · 9 High-level Reasoning and Planning (TAMP in the
  Now; SayCan; UniSim) · 10 Visual Tracking and 6D Pose Estimation (DART; BundleSDF;
  FoundationPose) · 11 Interactive/Active Perception (DensePhysNet; Curious Robot) ·
  12 Tactile Sensing (GelSight; Vision and Touch) · 13 Representation Learning (Dense Object Nets;
  Time-Contrastive Networks) · 14 Robotic System Building (Amazon Picking Challenge 2015; FlingBot)
- 선수: 필수 없음. 권장 — Robotics / Computer Vision / ML / Control / Filtering and Recursive
  Estimation / Optimization 중 1과목 이상 (CS131, CS223A, CS229 등).

### 2.6 CS231A Computer Vision: From 3D Perception to 3D Reconstruction — Savarese, Bohg
- URL: <https://web.stanford.edu/class/cs231a/> `확인` · 학기: Spring 2025
- 주제(세부 주차 미확인): cameras and projection models, filtering and edge detection, segmentation
  and clustering, stereo shape reconstruction, recognition, human motion categorization, depth
  estimation and optical/scene flow, 6D pose estimation and object tracking.
- 교재(권장): Forsyth–Ponce 2e; **Hartley–Zisserman Multiple View Geometry**;
  Thrun–Burgard–Fox Probabilistic Robotics.
- 선수: Python, 미적분·선형대수, 기초 확률통계, CS131/CS221/CS229 동급.
- 참고: 브리프의 "CS336 Robot Perception and Learning" 은 **존재하지 않는다**. 현재 CS336 은
  "Language Modeling from Scratch"(미확인, 검색만). 대응 과목은 CS326·CS231A·AA274B 다.

## 3. Carnegie Mellon (Robotics Institute)

### 3.1 16-745 Optimal Control and Reinforcement Learning — Zachary Manchester
연구 트랙 "최적 제어·궤적 최적화" 모듈의 **1순위 기준**.
- URL: <https://optimalcontrol.ri.cmu.edu/> `확인`,
  <https://github.com/Optimal-Control-16-745/lecture-notebooks> `확인` (Lecture 1–24 노트북)
- 학기: Spring 2025
- **주차별**: W1 course overview and dynamics intro; stability and discrete-time dynamics ·
  W2 optimization intro; numerical optimization pt1 · W3 numerical optimization pt2; optimal
  control intro; **regularization and merit functions** · W4 **Pontryagin and shooting methods;
  LQR in three ways** · W5 dynamic programming and convexity; **convex MPC** · W6 nonlinear
  trajectory optimization; **DDP and iLQR** · W7 **direct trajectory optimization, collocation,
  SQP** · W9 **attitude (SO(3), quaternions); optimizing with attitude** · W10 LQR with attitude,
  quadrotors, contact intro; **trajectory optimization for hybrid systems** · W11 data-driven
  methods and iterative learning control; **stochastic optimal control and LQG** ·
  W12 **robust control and minimax DDP** · W13 practical tips and tricks; RL from an optimal
  control perspective; case study: driving a car · W14 case studies: landing a rocket, walking ·
  W15 project presentations
- 과제: HW0 + 숙제 4개, **GitHub 배포 + Gradescope 제출**, 각 약 2주. 최종 프로젝트 1–5인,
  자기 연구에 과목 내용을 적용, 발표 + **ICRA/IROS 포맷 약 6페이지 보고서**.
- 교재: 필수 없음(강의 영상·노트 + 강의별 추가 읽기). 선수: 강한 선형대수, Python/MATLAB/Julia, 기초 ODE.

### 3.2 16-711 Kinematics, Dynamics and Control (KDC)
- URL: <https://sites.google.com/andrew.cmu.edu/ri-lsg/teaching-16-711> `확인`
  (Hartmut Geyer 의 Legged Systems Group 페이지; 연도 미표기, "Thinking about Action" 코어 과목)
- **장·강의 구조**: Ch1 Rigid Body Motions (L1–5) frames, orientation representations, homogeneous
  transforms, twists, velocities, wrenches · Ch2 Manipulator Kinematics (L5–10) **product of
  exponentials, Paden–Kahan subproblems**, Jacobians, numerical IK, redundancy, singularities ·
  Ch3 Rigid Body Dynamics (L10–13) Newton, d'Alembert, Lagrange, Newton–Euler · Ch4 Manipulator
  Dynamics (L14–16) open-chain and constrained dynamics, **contact models**, Newton–Euler algorithm ·
  Ch5 Fundamentals of System Control (L17–21) state space, stability, root locus, Nyquist, PID,
  observers, Kalman filtering · Ch6 Manipulator Control (L22–27) **feedback linearization,
  Lyapunov stability, operational-space and impedance control, LQR, MPC**
- 과제: 2주마다 이론 + 코딩. 예: 평면 운동 기구학, 순동역학 알고리즘, 노이즈 IMU 에서 물체 상태 추정.
- 교재: **Murray–Li–Sastry (MLS)**, Lynch–Park Modern Robotics, Åström–Murray Feedback Systems
  (권장 Siciliano 등). 선수: 공학 수학·물리, MATLAB 또는 Python.

### 3.3 16-833 Robot Localization and Mapping — Michael Kaess
- URL: <https://www.cs.cmu.edu/~kaess/teaching/16833/Fall2024> `확인`
  (Spring 2024·Spring 2022 페이지도 `확인`)
- 페이지는 소개만 제공 → 주차별 일정·과제·교재는 **스케줄 미공개**.
- 소개문: localization, mapping and SLAM; **선형대수와 확률 그래프 모델의 교차점에서의 효율적
  확률 추론(efficient probabilistic inference)**; state-of-the-art systems.

### 3.4 16-822 Geometry-based Methods in Vision
- URL: <https://geometric3d.github.io> `확인` (랜딩 페이지; Piazza 링크상 Fall 2026)
- 주제(일정 없음): fundamentals of projective, affine and Euclidean geometries · projective
  transforms in 2D/3D · single-view geometry (pinhole) · two-view geometry (fundamental matrix)
  and two-view reconstruction · N-view reconstruction · self-calibration ·
  **learning-based SfM and SLAM**
- 평가: assignments 30% + problem sets 30% + project 35% + participation 5%.
- 과제 제목(Fall 2023 아카이브, 검색 스니펫 **미확인**): projective geometry, single-view
  reconstruction, two-view and N-view geometry, learning-based reconstruction.
- 선수: 좋은 코딩 능력, 기초 컴퓨터 비전, 선형대수.

### 3.5 16-782 Planning and Decision-making in Robotics — Maxim Likhachev
연구 트랙 "동작 계획 이론" 모듈의 **1순위 기준**.
- URL: <https://www.cs.cmu.edu/~maxim/classes/robotplanning_grad/> `확인` · 학기: Fall 2026
- **날짜별**: Aug 24–26 introduction to planning; graph-based planning representations (implicit
  vs explicit graphs, skeletonization, cell decomposition, **lattice graphs**) · Aug 31–Sep 9
  search algorithms (A*, multi-goal A*, **weighted A***, backward A*), heuristic functions,
  **Multi-Heuristic A*** · Sep 14–23 **interleaving planning and execution (anytime and
  incremental A*, real-time heuristic search)**; 자율주행 사례 · Sep 28–Oct 7 **PRM, RRT,
  RRT-Connect, RRT***; 모바일 매니퓰레이터·보행 로봇 사례; search with Markov property,
  dependent variables and dominance · Oct 19–26 coverage, mapping and surveillance; **symbolic
  representations and task planning** · Oct 28 최종 프로젝트 아이디어 발표 · Nov 2–11 **planning
  under uncertainty (minimax, expected cost, solving MDPs)**
- 과제: HW1 Robot Catching a Target · HW2 Planning for N-DOF Arm · HW3 Symbolic Planning + 최종
  프로젝트. 평가: HW 33% + 시험 20% + 팝퀴즈 10% + 프로젝트 32% + 참여 5%.

### 3.6 16-720 Computer Vision — Deva Ramanan (Spring 2025)
- URL: <https://sites.google.com/andrew.cmu.edu/16-720spring2025> `확인`
- 주제: low-level image processing (filtering, warping, image descriptors, correspondence
  matching) · geometry and 3D motion (image formation, camera models, optical flow, stereo,
  structure from motion) · pattern recognition (deep learning, CNNs) · radiometry, color,
  photometric stereo. 주차별 목록은 **미확인**.
- 과제: 프로그래밍 숙제 6개(각 약 16.5%). 교재: Szeliski. 선수: 선형대수, 확률, 미적분.
  (상급 대학원생은 16-820, 학부는 16-385)

### 3.7 16-831 Introduction to Robot Learning (구 Statistical Techniques in Robotics)
- <https://16-831.github.io/fall25> 및 하위 lectures 페이지 모두 fetch 실패(404) → **(미확인)**.
  검색 스니펫: Fall 2025, 24개 강의, 마지막 강의는 휴머노이드 학습. 주제·과제·교재 **미확인**.
- 후속 조사 경로: Piazza resources 페이지, 또는 제3자 정리 블로그(미확인).

## 4. UC Berkeley

### 4.1 CS 285 (CS 185/285) Deep Reinforcement Learning — Sergey Levine
- URL: <https://rail.eecs.berkeley.edu/deeprlcourse/> `확인` · 학기: Spring 2026
- **주차별**: W1 course intro and imitation learning (introduction; behavioral cloning) ·
  W2 behavioral cloning pt2; RL basics · W3 policy gradients; actor-critic · W4 value-based RL;
  Q-learning in practice · W5 **advanced policy gradients (pts 1–2)** · W6 variational inference;
  VI in RL · W7 **control as inference**; LLM RL · W8 model-based RL (pts 1–2) ·
  W9 **offline RL (pts 1–2)** · W10 exploration; **RL theory** · W11 midterm review ·
  W12 advanced exploration; multi-task RL · W13 **challenges and open problems** · W14 guest lecture
- 과제: HW1 Imitation Learning · HW2 Policy Gradients · HW3 Q-Learning and Actor Critic ·
  HW4 **LLM RL** · HW5 Offline RL. 프로젝트 기본 옵션: Offline-to-Online RL 또는 LLM RL.
- 교재·선수: 페이지에 절이 있으나 본문 미획득(**미확인**).

### 4.2 CS287 Advanced Robotics — Pieter Abbeel
- URL: <https://people.eecs.berkeley.edu/~pabbeel/cs287-fa19/> `확인` · 학기: **Fall 2019**
  (확인된 최신 개설. 이후 개설은 미확인 — 설계에서는 "구조는 유효하되 최신 주제는 보강 필요"로 취급)
- 주제: exact MDP methods; discretization of continuous-state MDPs · function approximation;
  **LQR, iLQR, DDP** · unconstrained and constrained optimization; optimization-based control
  (collocation, shooting, MPC) · motion planning (RRT, PRM, trajectory optimization) ·
  probability, Bayes filters, Gaussians, Kalman/EKF/UKF, smoothing, MLE, EM ·
  **particle filters and POMDPs** · imitation learning and RL · **physics simulation and sim-to-real**
- 과제: 문제 세트 5개(60%) — value iteration / LQR·iLQR·DDP / convex and sequential convex
  optimization / Kalman and particle filtering / RL. 중간 10% + 최종 프로젝트 30%(1–2인, 약 6페이지).
- 교재(선택): Probabilistic Robotics, Sutton–Barto, Boyd–Vandenberghe, Nocedal–Wright,
  LaValle Planning Algorithms, Bertsekas–Tsitsiklis.
- 선수: 증명, 확률, 알고리즘, 선형대수, 알고리즘 구현 능력(CS188, EE126, EE127 권장).

### 4.3 EECS C106A / C106B Introduction to Robotics · Robotic Manipulation and Interaction
- C106A: <https://www2.eecs.berkeley.edu/Courses/EECSC106A> `확인` (**카탈로그만**) —
  manipulator kinematics, dynamics and control; robotic vision and sensing; motion planning with
  obstacle avoidance; computer vision. 선수: 선형대수(Math 54), Python(CS 61A 수준).
  강의계획은 **스케줄 미공개**.
- C106B: <https://pages.github.berkeley.edu/EECS-106/sp25-site> `확인` (Spring 2025, Sastry)
  - **주차별**: W1–2 dynamical systems, linear control, **Lyapunov stability** ·
    W2–3 **feedback linearization and controllability** · W3–4 **nonholonomic systems and steering
    with sinusoids** · W5–6 multi-input feedback linearization and dynamic extensions (quadrotors) ·
    W7–8 state estimation, Kalman filtering, SLAM · W9–10 **grasping** · W11–12 optimal control
    and RL · W13–14 **legged robotics (Sreenath)**, AR/VR
  - 프로젝트: P0 ROS review(선택) · **P1 Visual Servoing · P2 Nonholonomic Control ·
    P3 State Estimation · P4 Grasping** · HW0–5(HW0 = 106A 진단) · 최종 프로젝트(쇼케이스 + 웹사이트)
  - 교재: **MLS (Murray–Li–Sastry)** + 강의 노트 + Sastry 1999.

## 5. University of Pennsylvania (GRASP)

### 5.1 MEAM 620 / 6200 Advanced Robotics
- URL: <https://alliance.seas.upenn.edu/~meam620/wiki> `확인` — 단, **2018 아카이브**(2019-01 수정).
- 초점: "motion planning, control, and vision for mobile robots". 프로젝트는 개인 + 팀 혼합,
  최종 산출물은 **conference-quality final report**. 주차별 일정·참고문헌은 **스케줄 미공개**.
- 현재 번호는 MEAM 6200(Taylor/Paulos, 검색 스니펫 **미확인**).

### 5.2 MEAM 520 / 5200 Introduction to Robotics
- Fall 2026 개설 목록: <https://www.grasp.upenn.edu/academics/masters-degree-program/current-students/robotics-graduate-courses-fall/> `확인`
  (MEAM 5200/001, Holladay) — 실라버스 없음.
- 아카이브: <https://medesign.seas.upenn.edu/index.php/Courses/MEAM520> `확인` (Fall 2012,
  Kuchenbecker) — rotation matrices and homogeneous transforms; manipulator kinematics and DH;
  IK; velocity kinematics; trajectories; robot hardware; **haptics and teleoperation**; dynamics;
  mobile robots. 과제 HW01 Flying Box … HW06 Teleop, 프로젝트 PUMA Light Painting / PHANToM
  Haptics. 교재: Spong–Hutchinson–Vidyasagar.

### 5.3 ESE 650 / 6500 Learning in Robotics
- URL: <https://sites.google.com/seas.upenn.edu/ese650spr2022> `확인` · 학기: Spring 2022
- **모듈 구조**: M1 State Estimation — Markov chains, HMMs, Kalman filter, EKF/UKF, particle
  filters, occupancy grids · M2 Control and Planning — MDPs, value/policy iteration, Bellman
  equation, LQR, LQG, sampling-based motion planning · M3 Reinforcement Learning — imitation
  learning, policy gradient, Q-learning, **inverse RL**, model-based RL, **offline RL**
- 과제: 숙제 4개(60%) + 중간(20%) + 3인 팀 최종 프로젝트(20%), Python.
- 교재: Probabilistic Robotics, **Barfoot State Estimation for Robotics**, LaValle, Sutton–Barto,
  Russell–Norvig (상급: Bishop; **Ma–Soatto–Košecká–Sastry**; Bertsekas; Åström–Murray;
  Hespanha; **Chirikjian**)
- 선수: Python, 확률, 선형대수 (ML·최적화 권장).
- 관련(검색만, **미확인**): ESE 6800 Real-World Robot Learning (ESE 650 을 선수로 요구),
  CIS 7000 Foundations and Frontiers of Robot Learning (Spring 2026).

## 6. 유럽 (ETH Zürich · UZH · TUM · Imperial · Cambridge)

### 6.1 Vision Algorithms for Mobile Robotics — Davide Scaramuzza (UZH/ETH 151-0632-00L)
연구 트랙 "시각 지각·다시점 기하" 모듈의 **1순위 기준**.
- URL: <https://rpg.ifi.uzh.ch/teaching.html> `확인` · 학기: Fall 2026 (17.09–17.12.2026, 시험 2027-01-07)
- **강의 14개**: 1 Intro to CV and Visual Odometry · 2 Image Formation · 3 Camera Calibration ·
  4 Filtering and Edge Detection · 5–6 Point Feature Detectors (1–2) ·
  **7–10 Multiple-View Geometry 1–4** · 11 Optical Flow and KLT Tracking · 12 Place Recognition
  (+ 딥러닝 튜토리얼) · **13 Visual-Inertial Fusion** · **14 Event-Based Vision**

### 6.2 Autonomous Mobile Robots (ETH ASL 151-0854-00)
- URL: <https://asl.ethz.ch/education/lectures/autonomous_mobile_robots.html> `확인`,
  <https://asl.ethz.ch/education/lectures/autonomous_mobile_robots/spring-2021.html> `확인`
- 페이지에 올라온 개설 학기는 Spring 2017–2021 뿐이고 실라버스가 없다. 교재
  *Introduction to Autonomous Mobile Robots* (Siegwart–Nourbakhsh–Scaramuzza, MIT Press 2e 2011)
  를 따라가는 MOOC 형식. 주제 PDF 는 미획득 → 주차별 **미확인**.
- **ETH Robot Dynamics 151-0851-00 은 확인 실패(미확인)** — rsl.ethz.ch 404. 2차 출처(Scribd
  강의 스크립트 사본, 학생 MATLAB 연습 저장소)만 검색됨. 연구 트랙 설계에서는 CMU 16-711 과
  Featherstone 을 1순위 근거로 쓰고 ETH 는 보조로만 둔다.

### 6.3 Computer Vision II: Multiple View Geometry (TUM IN2228, Daniel Cremers)
- URL: <https://cvg.cit.tum.de/teaching/ss2022/mvg2022> `확인` · 학기: Summer 2022
- 주제(요약만, 주차별 없음): image formation and perspective projection · correspondences across
  images · constraints for camera motion and 3D structure · rigid-body motion math ·
  spectral methods and nonlinear optimization
- 교재: **Ma–Soatto–Košecká–Sastry, *An Invitation to 3-D Vision*** (연습은 MATLAB).
- SS2025 개설(<https://cvg.cit.tum.de/teaching/ss2025/cv2>)은 fetch 404 → **미확인**.
- TUM Introduction to Robotics(Haddadin), Machine Learning for Robotics: **미확인**.

### 6.4 Imperial College: Robotics (60019/70084) — Andrew Davison
- URL: <https://www.doc.ic.ac.uk/~ajd/Robotics/index.html> `확인` (학기 미표기, 슬라이드 2025-01)
- 강의 8개: 1 Introduction to Robotics · 2 Robot Motion · 3 Sensors · 4 Probabilistic Robotics ·
  5 Monte Carlo Localisation · 6 Advanced Sonar Sensing · 7 Camera Measurements · 8 SLAM
- 수준은 학부/석사 입문 → 연구 트랙 기준으로는 **선수 과정 수준**.

### 6.5 Cambridge: Mobile Robot Systems (Part II MRS 2025-26)
- URL: <https://www.cl.cam.ac.uk/teaching/2526/MRS/> `확인`
- 주제: sensor-actuator loops · motion, kinematics, control · perception, localization, mapping ·
  navigation and path planning · **multi-robot systems** · robot learning (ROS 사용)
- 리딩: Siegwart et al. · Thrun et al. · Mondada–Bonani · **Siciliano–Khatib Springer Handbook of
  Robotics (2016)** · **Mesbahi–Egerstedt**(다중 로봇 그래프 이론)

### 6.6 ETH Robot Learning 2026 — Oier Mees
- URL: <https://github.com/mees-robot-learning-course/ethz-course-2026> `확인`
- 숙제 4개: HW1 PyTorch tutorial · HW2 robot control MDPs · HW3 imitation learning ·
  HW4 reinforcement learning. 실라버스는 저장소에 없음.
- 검색 스니펫(**미확인**): 월 강의 + 목 실습, 평가 = 논문 발표 20% / 숙제 40% / 프로젝트 40%.
- 미확인: ETH Perception and Learning for Robotics, Optimal & Learning Control, Oxford Mobile
  Robotics, Imperial Robot Learning, KTH, TU Delft.

## 7. 박사과정 자격시험 · 코스 오브 스터디 (PhD qualifying requirements)

> **중요한 발견: 로보틱스 박사 자격시험은 "리딩리스트 시험"이 아니다.** 조사한 네 학교 모두
> ① 지정된 **영역(area)별 과목 이수**(성적 기준 포함) + ② **연구 수행 능력 심사**(보고서 + 구술)
> 의 두 축이다. 공개된 "필독 논문 리딩리스트"는 **확인되지 않았다**. 따라서 연구 트랙의 논문
> 목록([papers.yaml](papers.yaml))은 자격시험 리스트의 복제가 아니라, **확인된 과목들의 리딩과
> 세미나 과목(CS326 등)의 논문 목록에서 역산**해야 한다.

### 7.1 CMU Robotics Institute PhD — Course of Study AY 2023-24
- URL: <https://www.ri.cmu.edu/app/uploads/2023/08/Ph.D.-Course-of-Study_AY-2023-24.pdf?resolved=1> `확인`
- 구조: **Core Course Qualifier + Specialized Course Qualifier + Research Qualifier** (별도 필기시험 없음,
  과목은 B- 이상).
- **Core: 4개 영역에서 각 1과목** — 연구 트랙의 "공통 코어" 설계에 직접 대응한다.
  | 영역 | 인정 과목 |
  |---|---|
  | **Perception** | 16-720 Computer Vision · 16-722 Sensing and Sensors (비전 경험자: 16-820 Advanced CV · 16-822 Geometry-based Methods in Vision · 16-823 Physics-based Methods in Vision) |
  | **Cognition** | 15-780 Artificial Intelligence · 10-701 Machine Learning (또는 10-715) · 16-831 Introduction to Robot Learning |
  | **Action** | 16-741 Mechanics of Manipulation · 16-711 Kinematics, Dynamic Systems, and Control · 16-761 Mobile Robots |
  | **Math Foundations** | **16-811 Math Fundamentals for Robotics** (이 영역의 유일 과목) — optimal estimation, differential geometry, computational geometry, operations research |
- Specialized: 학생이 정의한 영역에서 48 units 이상(보통 대학원 4과목), 지도교수 승인.
- Research Qualifier: 4개 구성요소(Research Skills, Speaking, Writing, Teaching), 반일 기준 약 2년, 교수 위원회.
- **전제 배경**: calculus, linear algebra, numerical analysis, probability and statistics,
  programming, algorithms, mechanics, dynamics, E&M, optics. → 연구 트랙 선수지식의 근거.
- 리딩리스트: 문서에 없음.

### 7.2 Georgia Tech Robotics PhD
- URL: <https://sites.gatech.edu/robograds/robotics-phd-qualification-exam-process> `확인`
- ① **5개 코어 영역(AI, Controls, HRI, Mechanics, Perception) 중 정확히 2개 영역**에서 4과목,
  GPA 3.5 이상 ② 구술시험(5학기 말까지 1차 응시)
- 구술 형식: 3주 전 주제 배정 → **2페이지 이내 서면 요약(문헌 리뷰 + 연구 문제 + 가능한 해법)**
  → 15–20분 발표, 총 1시간, 로보틱스 교수 3–5인(의결 3인).
  → 연구 트랙 캡스톤의 형식적 근거(서면 제안 + 구술 방어).
- 영역별 과목 목록·리딩리스트는 페이지에 없음(**미확인**; robograds.gatech.edu/quals 503).

### 7.3 MIT EECS — TQE + RQE
- URL: <https://www.eecs.mit.edu/academics/graduate-programs/materials-and-forms-for-graduate-students/phd-academic-progress-i> `확인`,
  TQE 표 <https://www.eecs.mit.edu/wp-content/uploads/2026/09/TQE-Grid-effective-fall-2026-corrected-9.2.2026.pdf> `확인`
- TQE: 7개 Group 중 한 Group 에서 2과목 + 다른 두 Group 에서 각 1과목(총 4), **A 3개 + B 1개 이상**,
  5학기 내 완료. RQE(6.9993): TQE 후, 연구 능력(서면 + 구술) 심사.
- **로보틱스 관련 과목**: Group 3 (AI) — 6.4212 Robotic Manipulation [6.8210 과 배타] ·
  6.8210 Underactuated Robotics · **6.8200 Sensorimotor Learning** · 6.8300 Advances in Computer
  Vision · 6.7900 Machine Learning · 6.7960 Deep Learning. Group 4 (System Science and Control) —
  6.7100 Dynamic Systems and Control · **6.7220 Nonlinear Optimization** ·
  6.7210 Introduction to Mathematical Programming.
  → **로보틱스 박사 자격이 "제어 + 최적화 + 학습 + 비전"의 조합으로 정의된다**는 직접 증거.

### 7.4 MIT MechE · Stanford CS (참고)
- MIT MechE: <https://mechegrad.mit.edu/qualification-exam> `확인` — 과목시험 2개 + RQE Part I
  (심화 과목) + Part II(연구 발표), 구술, 합격선 10점 중 7점. C-list 에 Dynamics 2.032,
  System Dynamics and Controls 2.140/2.151, Stochastic Dynamical Systems 2.122;
  S-list 에 Robotics 2.120.
- Stanford CS: <https://www.cs.stanford.edu/phd-program-foundation-and-breadth-requirements> `확인` —
  4개 영역(Formal Foundations, Learning and Modeling, Systems, People and Society)에서 서로 다른
  영역 3과목, B+ 이상. **로보틱스는 독립 영역이 아니다**.
- 공개 랩 리딩리스트(Utah robot-learning, CMU RPL, Toronto RVL 등)는 검색만 되고 fetch 하지
  않았다 → **미확인**. 후속 조사 과제.

## 8. 교재 정전 (textbook canon)

| 교재 | 확인 URL | 무료 | 구조 |
|---|---|---|---|
| **Lynch & Park, *Modern Robotics*** | <http://hades.mech.northwestern.edu/index.php/Modern_Robotics> `확인` | 예 (v2 2019 PDF, 4종 레이아웃) | 13장: 1 Preview · 2 Configuration Space · 3 Rigid-Body Motions · 4 Forward Kinematics · 5 Velocity Kinematics and Statics · 6 Inverse Kinematics · 7 Kinematics of Closed Chains · 8 Dynamics of Open Chains · 9 Trajectory Generation · 10 Motion Planning · 11 Robot Control · 12 Grasping and Manipulation · 13 Wheeled Mobile Robots + 부록 A–D |
| **Tedrake, *Underactuated Robotics*** | <https://underactuated.csail.mit.edu/> `확인` | 예 (HTML + PDF) | 21장: 1 Fully-/Underactuated · 2 Simple Pendulum · 3 Acrobots, Cart-Poles, Quadrotors · 4 Simple Models of Walking and Running · 5 Highly-Articulated Legged Robots · 6 Model Systems with Stochasticity · 7 Dynamic Programming · 8 LQR · 9 Lyapunov Analysis · 10 Trajectory Optimization · 11 Policy Search · 12 Sampling-Based Motion Planning · 13 Robust and Stochastic Control · 14 Feedback Motion Planning · 15 Output Feedback (Pixels-to-Torques) · 16 Algorithms for Limit Cycles · 17 **Planning and Control through Contact** · 18 System Identification · 19 State Estimation · 20 Model-Free Policy Search · 21 Imitation Learning |
| **LaValle, *Planning Algorithms*** | <https://lavalle.pl/planning/> `확인` | 예 (전문 HTML + PDF) | I 서론(1–2) · II Motion Planning(3 Geometric Representations · 4 The Configuration Space · 5 Sampling-Based Motion Planning · 6 Combinatorial Motion Planning · 7 Extensions · 8 Feedback Motion Planning) · III Decision-Theoretic Planning(9–12, 정보 공간·감지 불확실성) · IV Differential Constraints(13–15) |
| **Barfoot, *State Estimation for Robotics* 2e (2024)** | <https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf> `확인` | 예 (전문 PDF) | I Estimation Machinery(2 Probability · 3 Linear-Gaussian · 4 Nonlinear Non-Gaussian · 5 Nonidealities · 6 변분 추론) · II Three-Dimensional Machinery(7 3D Geometry · **8 Matrix Lie Groups**) · III Applications(9 Pose Estimation · 10 Pose-and-Point Estimation) · IV 부록 |
| **Boyd & Vandenberghe, *Convex Optimization*** | <https://web.stanford.edu/~boyd/cvxbook/> `확인` | 예 (PDF) | 페이지에 장 목록 없음. 슬라이드·연습문제 제공 |
| **Hartley & Zisserman, *Multiple View Geometry* 2e** | <https://www.robots.ox.ac.uk/~vgg/hzbook/> `확인` | 아니오 (표본 장 3개만: Intro, Epipolar Geometry, Trifocal Tensor) | CUP 2004, MATLAB 코드·오류표 |
| **Szeliski, *Computer Vision* 2e (2022)** | <https://szeliski.org/Book/> `확인` | 예 (개인용 PDF, 다운로드 폼) | 페이지에 장 목록 없음 |
| **Featherstone, *Rigid Body Dynamics Algorithms*** | <https://royfeatherstone.org/> `확인` | 아니오 (Springer, ISBN 978-0-387-74314-1) | 동반 라이브러리 `spatial_v2` 제공 |

**fetch 실패 → (미확인)** (존재는 널리 알려졌으나 이 조사에서 URL 확인 못 함):
Murray–Li–Sastry *A Mathematical Introduction to Robotic Manipulation*(Caltech 인증서 오류) ·
Sutton & Barto(인증서 오류) · Siciliano et al. *Robotics: Modelling, Planning and Control* ·
Thrun–Burgard–Fox *Probabilistic Robotics*(MIT Press 403) · Nocedal & Wright(Springer 인증) ·
Khalil *Nonlinear Systems*(미시도) · Choset et al. *Principles of Robot Motion*(500/403) ·
Siciliano & Khatib *Springer Handbook of Robotics*(Springer 인증).
→ MLS 는 CMU 16-711·Berkeley C106B 가, Probabilistic Robotics 는 CS231A·CS287·ESE 650 이,
Springer Handbook 은 Cambridge MRS 가 **확인된 페이지에서 교재로 지정**하고 있어, 교재 지정
사실 자체는 확인됐고 **공식 URL 만 미확인**이다.

## 9. 설계에 대한 함의 (implications for the blueprint)

1. **"연구원 수준"의 조작적 정의**: CMU Core 4영역(Perception / Cognition / Action / Math
   Foundations)과 MIT TQE Group 3+4(AI + System Science and Control)의 교집합이 곧 공통 코어다.
   → 수학 기초(16-811 류) · 동역학·제어(16-711, CS223A) · 최적 제어(16-745, AA203) ·
   추정·SLAM(16-833, 16.485) · 계획(16-782) · 지각(16-822, 151-0632) · 학습(CS285, 16-831).
2. **수학 기초를 독립 모듈로 세워야 한다.** CMU 는 Math Foundations 영역에 **과목 하나만**
   두었고(16-811), 전제 배경으로 numerical analysis·differential geometry 를 요구한다. 기존
   50레슨의 M1(벡터·행렬·회전 표현)은 이 수준이 아니다.
3. **과제는 구현 + 학회 포맷 보고서.** 16-745(ICRA/IROS 6페이지), CS287(6페이지), MEAM 620
   (conference-quality report), GT 구술(2페이지 제안서 + 발표)이 일관된 근거다. →
   [lesson-standard.md](lesson-standard.md) §6 재현 과제와 §8 캡스톤이 이 형식을 따른다.
4. **세미나형 모듈이 필요하다.** CS326(논문 리뷰 + 튜토리얼 + 토론 + 연구 제안서)은 specialization
   트랙의 상위 모듈 형식으로 그대로 차용할 수 있다. CS285 W13("Challenges and Open Problems")은
   열린 문제 섹션의 근거다.
5. **최신 주제가 이미 정규 과목에 들어와 있다.** AA274A 의 advanced topics(VLA, 3DGS for sim2real,
   world models), CS285 HW4(LLM RL), AA203 W10(world models for robotics), CS326 §9(SayCan,
   UniSim) — 연구 트랙은 파운데이션 모델·생성형 정책을 **선택 주제가 아니라 코어로** 다뤄야 한다.
6. **리 군·manifold 최적화가 코어의 입구다.** 16.485 L4–5·L18–19, 16-745 W9("optimizing with
   attitude"), Barfoot ch.8, 16-711 Ch1–2(product of exponentials, Paden–Kahan) 가 모두 같은
   자리를 가리킨다. 기존 M1 의 "회전 표현"은 이 자리의 입문부에 해당한다.
7. **접촉·하이브리드 시스템이 별도 주제다.** 16-745 W10(hybrid systems), Tedrake ch.17,
   16-711 Ch4(contact models), CS326 §3(extrinsic dexterity) — 기존 50레슨에 대응 항목이 없다.
8. **확인 못 한 것은 설계에서 2순위로 둔다**: ETH Robot Dynamics, CMU 16-831 상세, Oxford,
   공개 랩 리딩리스트. 이들은 blueprint 의 근거로 쓰지 않거나 `(미확인)` 표기와 함께 보조로만 쓴다.
