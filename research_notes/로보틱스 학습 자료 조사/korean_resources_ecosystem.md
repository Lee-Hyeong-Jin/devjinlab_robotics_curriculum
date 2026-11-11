# 한국어 로보틱스 학습 자료 및 한국 로봇 교육 생태계 조사 (2026년 11월 기준)

조사일: 2026-11-11. 대상 독자: 로보틱스 입문~중급 한국 소프트웨어 개발자. 가격은 조회 시점의 KRW 표시가이며 할인/프로모션에 따라 수시로 변동함. "stale" 표기는 2022년 이전 자료.

---

## KQ1. 한국어 온라인 강의 (인프런 / 패스트캠퍼스 / 유데미 / K-MOOC / 코세라 / 부스트코스·엘리스·구름)

### Takeaway
2025–2026년 한국어 로보틱스 온라인 강의 시장은 사실상 **패스트캠퍼스가 독점**하고 있다(ROS 2 기초·SLAM/Nav2·Gazebo/URDF·MoveIt 2 Motion Planning·VLA/LLM·Physical AI 입문·Isaac Lab 휴머노이드까지 7개 이상의 유료 강의, 정가 40만~120만 원에 상시 65~76% 할인). 인프런은 2026년 중반에 올라온 소규모 현직자 강의(수강생 20~50명)와 대학 특성화 무료 강좌 외에는 ROS 2 전용 강의가 사실상 없고, 유데미에는 민형기(PinkWink)의 한국어 R2R 시리즈가 가장 많은 수강생(입문 385명, 평점 4.5)을 보유한다. K-MOOC에는 로보틱스 정규 강좌가 거의 없으며(수원대 '인공지능 HRI' 정도), 부스트코스·엘리스·구름에듀에서는 로봇/ROS 강의를 찾지 못했다.

### Cited Findings

**패스트캠퍼스 (fastcampus.co.kr) — 모두 온라인 VOD, 강사 Q&A 라운지, ROS 2 Humble/Ubuntu 22.04 중심(Motion Planning만 Jazzy/24.04)**

- **ROS 2 자율주행 로봇 Dev Academy Part 1. 개발 환경 및 ROS 2 Basic** — 정가 500,000원 → 판매가 123,000원; 약 11시간(Part 1 개발환경 7클립 1:28, Part 2 ROS 2 기초 30클립 9:41); ROS 2 Humble + Ubuntu 22.04 + Gazebo Classic 11; 최종 영상 공개 2026-04-30; 수강평·평점 미표시 — [FastCampus](https://fastcampus.co.kr/data_online_ros2)
- **ROS 2 & AI로 끝내는 자율주행 로봇 개발 올인원** — 강사 Robby(글로벌 완성차 자율주행 SW 엔지니어, 전 KDT 자율주행 강사); 정가 1,200,000원 → 282,000원~(76% 할인); 약 29시간 104클립 6파트(로봇 선택 → 실물 모바일로봇 조립 → ROS 2 → 자율주행 센서 → SLAM & Navigation → 포트폴리오 프로젝트); 실습 로봇 Hiwonder MentorPi M1(약 40만 원대, 별도 구매) 또는 TurboPi(약 14만 원대, LiDAR SLAM/Nav 실습 제외), Raspberry Pi 5(4GB+), ROS 2 Humble; 전체 공개 2025-12-19; 유료 수강 30일 후 무제한 무료 — [FastCampus](https://fastcampus.co.kr/data_online_ros2ai)
- **자율주행 로봇을 위한 ROS 2 & SLAM & Nav2 한번에 끝내기** — 강사 Robby; 정가 1,000,000원 → 271,000원(72% 할인); 약 24.5시간 약 75클립 5파트(Part1 Linux/VS Code/ROS 2 Humble 설치, Part2 ROS 2 기초[패키지·노드·launch·토픽·서비스·액션·디버깅], Part3 SLAM[Cartographer·AMCL·튜닝·Visual SLAM], Part4 Nav2[planner/controller/smoother/behavior 서버·costmap], Part5 Nav2 심화[Behavior Tree·멀티로봇·창고 시뮬레이션·Keepout/Speed 필터]); Q&A 라운지 2024-12-02~2026-12-01; 패키지 "ROS2 올인원"(정가 2,200,000 → 399,000원)은 판매 종료 표시 — [FastCampus](https://fastcampus.co.kr/data_online_selfdriving)
- **ROS 2 & Gazebo를 활용한 로봇 모델링과 자율주행 시뮬레이션** — 정가 1,000,000원 → 261,000원(73% 할인); URDF 기반 로봇 모델링 + Gazebo 시뮬레이션 — [FastCampus](https://fastcampus.co.kr/data_online_selfdriving2)
- **ROS 2로 시작하는 로보틱스 Motion Planning** — 강사 이성원(UIUC Graduate Research Assistant); 정가 800,000원 → 348,000원; 약 25시간 249클립 6파트(모션플래닝 개요 → 구성요소 → 알고리즘 기초 → 모션/경로계획 기법 107클립 → ROS 2 실습 78클립); **ROS 2 Jazzy + Ubuntu 24.04 + Gazebo**, MoveIt 2 + UR 매니퓰레이터 Pick & Place 파이널 프로젝트; 전체 공개 2025-08-01 — [FastCampus](https://fastcampus.co.kr/data_online_mp)
- **피지컬 AI 개발을 위한 VLA & 로봇 특화 LLM 한번에 끝내기** — 강사 민형기 박사(로봇 R&D 15년, 로봇 교육 10년); 정가 400,000원 → 263,000원(34% 할인); 약 14시간 88클립 6파트(MuJoCo → LLM → VLA → ROS2 자율주행+VLA 연결 → 미니 프로젝트 → ROS2 심층 분석); 도구 MuJoCo·Gazebo·ROS 2·SLAM·Nav2·Ollama·YOLO·OpenAI API(LeRobot·OpenVLA·pi0·GR00T는 언급 없음); 전체 공개 2025-11-14 — [FastCampus](https://fastcampus.co.kr/data_online_vla)
- **Physical AI 입문 All-In-One 초격차 패키지: 파이썬 프로그래밍부터 동체 제작을 위한 회로 설계까지** — 강사 Robby·온진욱(산업/교육용 로봇 개발 20년+)·Kyle(서울대 로봇공학 연구원); 정가 800,000원 → 303,000원~; 약 54시간 177클립 5파트(좌표계 → 인지[YOLO·OpenCV] → 판단 → 제어[MCU·PWM·I2C·CAN] → 하드웨어/동체 설계[Fusion 360·EAGLE PCB]); 순차 공개 2026-08-28 ~ 2026-12-18; Q&A 2026-08-28~2029-07-27; ROS 2·LeRobot·Isaac·MuJoCo 미언급 — [FastCampus](https://fastcampus.co.kr/data_online_physicalai)
- **NVIDIA Isaac Sim과 강화학습을 활용한 휴머노이드 보행 제어** — 강사 임현택; 정가 600,000원 → 387,000원(35% 할인); 약 11시간 28클립 5파트(RL 환경 구축 → PPO 보행 정책 학습 → Whole-body locomotion → 실환경 확장); Isaac Sim + Isaac Lab + rsl_rl(PPO), Unitree G1, Ubuntu 22.04; 2026-03-09 런칭, 최종 공개 2026-08-07 — [FastCampus](https://fastcampus.co.kr/data_online_humanoid)
- 로봇 카테고리 이벤트 페이지는 7개 강의 라인업(위 강의들 + "자율주행을 위한 컴퓨터비전과 라이다 & 센서퓨전", "로보틱스 & 3D 컴퓨터 비전 개발을 위한 SLAM 바이블 with 슬램슬램")과 4개 패키지를 나열하며, 4개 패키지 모두 "판매 기간이 종료된 상품" 표시 — [FastCampus 로보존](https://fastcampus.co.kr/event_online_robozone)
- 검색 결과에서 추가로 확인된 패스트캠퍼스 로봇 관련 슬러그(상세 미확인): `data_online_urdf`(URDF 기반 로봇 모델 구축), `data_online_realrobot`, `data_online_slambasic`, `data_online_autovehicle`, `data_online_robotbegin`, `data_online_digitaltwin`, `data_online_yolov11` — [검색 결과](https://fastcampus.co.kr/data_online_urdf)
- 수강 후기(커뮤니티): "ROS2, SLAM, Nav2를 기초 개념부터 연결해 설명해 준다"는 긍정 후기 — [FastCampus 커뮤니티](https://fastcampus.co.kr/community/101407)
- 패스트캠퍼스는 2026년 4월 국내 최초로 'VLA 자율주행 로봇 개발' 6주 오프라인 과정을 론칭(Agentic VLA 파이프라인 프로젝트) — [디지털데일리 2026-04-13](https://www.ddaily.co.kr/page/view/2026041309320384940)
- 패스트캠퍼스는 2026-09-17 "ROS 2 + Claude Code AI 에이전트 로보틱스" 무료 라이브 세미나 개최(종료) — [FastCampus](https://fastcampus.co.kr/event_online_agentrobotics)

**인프런 (inflearn.com)**

- **현직자가 알려주는 로봇 제어: 시뮬부터 실로봇(SO-ARM101) 제어까지** — 강사 jelly(대기업 로보틱스 개발자); 정가 121,000원(신규가입 25% 할인 90,750원); 난이도 중급이상; 5섹션 27강(SO-ARM 하드웨어/통신 설정 → 정/역기구학·관절/작업공간 경로계획·3D 시뮬레이션 GUI → 제어 알고리즘 → 취업 트렌드); SO-ARM101(STS3215 서보) 선택사항, Python 3.10+ 직접 구현, ROS·MuJoCo 사전지식 불필요; 수강생 23명, 평점 5.0(수강평 1개); 게시 2026-07-06, 최종 업데이트 2026-09-06 — [인프런](https://www.inflearn.com/course/robot-control-taught)
- **현직자가 알려주는 로보틱스 시스템 완전 해부: 부품부터 통신까지** — jelly; 정가 29,700원; 입문; 58분 17강(상/하위 제어기·모터드라이버·센서·전원/비상정지; Serial·CAN·Ethernet·EtherCAT·SPI/I2C·패킷 설계); 수강생 50명, 평점 4.8(5개); 게시 2026-06-21 — [인프런](https://www.inflearn.com/course/a-complete-breakdown)
- **현직자가 알려주는 로봇 실무 개발 프로세스: 로봇 양산 사이클** — jelly; 정가 18,700원; 입문; 45분 17강(기획 → 설계 → Proto → Pilot → 양산, Unitree Go2 예시 APQP); 수강생 25명, 평점 5.0(3개); 게시 2026-06-26 — [인프런](https://www.inflearn.com/course/robot-development-pr)
- **[지금 무료] ROS 기반 로봇운영**(울산대 스마트특성화 사업) — 무료, 평점 5.0(리뷰 6), 학습자 21명, 리눅스 환경 ROS 빌드·Gazebo·SLAM 실습, 80% 출석 시 수료증 — [인프런](https://www.inflearn.com/en/course/ros-기반-로봇운영); 동일 사업의 "ROS기반로봇운영 추가교육과정"은 평점 5.0(수강평 1), 수강생 13명, "교육 신청자만 수강가능" — [인프런](https://www.inflearn.com/course/ros-로봇운영-추가교육/community)
- 일반 웹 검색("인프런 ROS 2 강의")에서는 인프런 강의가 한 건도 노출되지 않고 패스트캠퍼스 강의만 노출됨 — [검색 결과 요약](https://fastcampus.co.kr/data_online_ros2)

**유데미 (udemy.com)**

- **[R2R] 무작정 따라하는 ROS2 - 입문과정 (ROS2 Humble/Jazzy)** — 강사 민형기; 한국어; 평점 4.5(71개 평가), 수강생 385명; Ubuntu 22.04 + ROS 2 Humble 설치, Ubuntu 24.04 Jazzy 호환 명시; 환경설정/기초명령/Topic — [Udemy](https://www.udemy.com/course/r2r_ros2_bgn/)
- **[R2R] 무작정 따라하는 ROS2 - 응용과정 (ROS2 Humble/Jazzy)** — 평점 4.1(18개), 수강생 197명; 패키지 구성·메시지 정의·액션·파라미터·디버깅·launch; 입문과정 선수 필요 — [Udemy](https://www.udemy.com/course/r2r_ros2_app/)
- 한국어 자막 제공 영문 강의: ROS 2 for Beginners Level 3(액션·라이프사이클·익스큐터·컴포넌트) — [Udemy](https://www.udemy.com/course/ros2-advanced-core-concepts/); ROS 2 Nav2 [Navigation 2 Stack] with SLAM and Navigation — [Udemy](https://www.udemy.com/course/ros2-nav2-stack/); Robotics and ROS 2 - Learn by Doing! Manipulators(MoveIt 2·ros2_control·Gazebo) — [Udemy](https://www.udemy.com/course/robotics-and-ros-2-learn-by-doing-manipulators/)
- 유데미 강의 페이지 직접 fetch는 403으로 차단되어 가격·최종 업데이트일은 확인 못 함.

**K-MOOC (kmooc.kr)**

- **인공지능 HRI** — 수원대학교 임동원 교수(산업및기계공학부); 난이도 "교양"; 15주, 학습인정 15시간(동영상 9시간 9분); 운영 2026-03-02~06-15, 수강신청 2026-02-27~05-05; 주차: HRI → AI/신경망 기초 → 딥러닝 → Python 딥러닝 → 로봇공학 기초(6주) → 로봇기구학(7주) → 로봇제어(9주) → CNN 실습 → 역운동학+OpenCV 운동제어 → HRI 실습; 수강료·수강자 수 미표시 — [K-MOOC](https://www.kmooc.kr/view/course/detail/19479); 2020년 K-MOOC AI강좌(휴먼-로봇상호작용 분야) 선정 — [한경 잡앤조이 2020](https://magazine.hankyung.com/job-joy/article/202008054974b)
- "K-MOOC 로봇공학 강좌" 검색에서 위 강좌 외의 로봇공학/ROS 전용 K-MOOC 강좌는 확인되지 않음 — [검색 결과](https://www.kmooc.kr/intro/system)

**코세라 한국어판**

- Northwestern **현대 로봇공학(Modern Robotics) 전문 과정** 한국어 버전이 6개 강좌(`modernrobotics-course1-ko` ~ `course6-ko`)로 존재, 강의 언어 "Taught in Korean", 난이도 Intermediate; 교재는 Lynch & Park(서울대 박종우) *Modern Robotics*(Cambridge UP 2017), 무료 PDF 제공 — [Coursera course1-ko](https://www-cloudfront-alias.coursera.org/learn/modernrobotics-course1-ko); [course6-ko](https://coursera.org/programs/adnoc-learning-program-nc2kl/learn/modernrobotics-course6-ko)
- 2024-11 블로그: "동영상과 교재는 모두 한국어 자막과 번역본이 있다", "[현대 로봇공학] 강의를 신청해야 Graded assignment와 CoppeliaSim 프로젝트 과제를 무료로 할 수 있다" — [istein.tistory.com](https://istein.tistory.com/142)

**부스트코스 / 엘리스 / 구름에듀 / 프로그래머스**

- 도메인 한정 검색(boostcourse.org, elice.io, edu.goorm.io, programmers.co.kr)에서 ROS/로봇 강의는 **프로그래머스 'K-Digital Training: 자율주행 데브코스'(1~6기)만** 확인; ROS 토픽 통신·모니터링·시각화, 1/10 모형차(자이카) 제어, Gazebo 서빙로봇 프로젝트 포함; 페이지 다수가 2022년 전후 기수 — [프로그래머스](https://school.programmers.co.kr/learn/courses/10822); [6기 perception](https://school.programmers.co.kr/learn/courses/17916/17916-6%EA%B8%B0-k-digital-training-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%A8%B8%EC%8A%A4-%EC%9E%90%EC%9C%A8%EC%A3%BC%ED%96%89-%EB%8D%B0%EB%B8%8C%EC%BD%94%EC%8A%A4-perception)
- 부스트코스에서는 강화학습 'MOVE37' 외 로봇 강좌 없음 — [boostcourse](https://www.boostcourse.org/move37)

**The Construct (해외, 한국어 지원)**

- The Construct 지원 포럼: Basic ROS 2, TF2, URDF 코스의 한국어 버전 존재 — [The Construct](https://get-help.theconstruct.ai/t/language-support/31113)
- "Robotics Developer Masterclass" 한국어 모집글(Git·C++·ROS1/2·URDF·TF2·Gazebo·Nav·Perception·Manipulation·컨트롤러·기구학/동역학·칼만필터·경로계획·Docker·Jenkins·CI)이 2023-12부터 2025-06 배치까지 ROS Discourse 한국 그룹에 게시; 등록 roboticsdeveloper.ai; 가격·기간 미표기 — [ROS Discourse](https://discourse.openrobotics.org/t/robotics-developer-masterclass-2024-1/35253)

### Inferences
- 한국어 유료 VOD 시장은 패스트캠퍼스 1개사가 ROS 2 기초→Nav2→MoveIt 2→VLA→Isaac Lab까지 세로로 쌓아 올렸고 강사풀도 Robby·민형기·이성원·임현택 등 소수에 집중. 수강평/평점을 공개하지 않아 품질 신호는 약함.
- 인프런은 2026년에야 로보틱스 강의가 나타나기 시작했으며(jelly 3편, 모두 2026-06/07 게시) 규모가 작다 → 인프런 스타일(저가·세분화)의 ROS 2/Nav2/MoveIt 2 한국어 강의는 공백.
- K-MOOC·KOCW 같은 공공 플랫폼은 로보틱스 이론(기구학)에는 일부 기여하나 ROS 2/현대 툴체인 교육은 전무.

### Gaps
- 패스트캠퍼스 강의의 수강생 수·평점은 페이지에 비공개여서 확인 불가.
- 유데미 R2R 강의의 가격·최종 업데이트일은 403으로 확인 불가.
- 엘리스·구름에듀·부스트코스의 사이트 내부 검색은 수행하지 못함(외부 검색 기준 "없음").

---

## KQ2. 한국어 로보틱스 서적 (ROS 2, 로봇공학 교재, 번역서, 아두이노/라즈베리파이, 2024–2026 신간)

### Takeaway
한국어 ROS 2 종이책은 **표윤석·임태훈 『ROS 2로 시작하는 로봇 프로그래밍』(루비페이퍼, 2021, 636쪽, 32,000원)**과 **민형기 『ROS2 혼자공부하는 로봇SW』(잇플, 2022)** 두 권이 사실상 전부이며 모두 Humble 이전 시기 출간이다. 2025–2026년 신간은 1인 출판 전자책(조형연, 유페이퍼 2025-03)과 **위키독스 무료 온라인 책**(ROS 2 Jazzy 문서 번역, 센서융합/SLAM, ROS2 로봇 만들기, 모두를 위한 Humanoid Robot/Isaac Lab)으로 이동했다. *Modern Robotics*·Craig *Introduction to Robotics*의 정식 한국어 번역본은 검색에서 확인되지 않았다.

### Cited Findings

**ROS / ROS 2 서적**

- **『ROS 2로 시작하는 로봇 프로그래밍』** 표윤석·임태훈, 루비페이퍼, 2021-08-05, ISBN 9791186710722, 정가 32,000원(판매 28,800원), 636쪽; YES24 평점 9.6(9명); 구성 Part1 ROS 2 소개(24장: DDS/QoS, turtlesim, 토픽·서비스·액션·파라미터, CLI/RQt, 빌드시스템) / Part2 기본 프로그래밍(18장: Python·C++ 토픽/서비스/액션/파라미터, launch) / Part3 심화(9장: 로깅, intra-process, QoS, 컴포넌트, 라이프사이클, 보안, 실시간); 특정 배포판 미명시 — [YES24](https://www.yes24.com/Product/Goods/102949767); [교보문고](https://product.kyobobook.co.kr/detail/S000001891112); [알라딘](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=276616576). 2015년 『ROS 로봇 프로그래밍』의 판올림이며 저자는 TurtleBot3 개발자 — [교보문고 검색 요약](https://product.kyobobook.co.kr/detail/S000001891112). **[주의: 2021년 출간 → Foxy/Galactic 시대, Humble/Jazzy 변경점 반영 안 됨]**
- 판교오로카 회원들이 2023-04부터 12주간 이 책 완독 챌린지 진행(블로그 기록) — [makepluscode.tistory](https://makepluscode.tistory.com/228)
- **『ROS2 혼자공부하는 로봇SW 직접 만들고 코딩하자』** 민형기, 잇플, 2022, 종이책 433쪽, 전자책 병행; ROS 기본 사용법(토픽·서비스·액션·파라미터) 입문서 — [교보문고](https://product.kyobobook.co.kr/detail/S000061695943); [YES24 전자책](https://www.yes24.com/product/goods/112926184) (상세 페이지 fetch 실패로 ISBN/가격 미확인)
- **『ROS2 코딩 배우면서 모바일 로봇 만들어 보자』** 조형연, 유페이퍼, 2025-03-16, ISBN 9791173869112, 23,200원, eBook PDF(DRM) 약 228쪽; Ch1 ROS2 플랫폼 → Ch2 시뮬레이션(URDF/Xacro/RViz2/Gazebo) → Ch3 Slampibot(SPB) 하드웨어 → Ch4 SLAM(Cartographer·Navigation2); 리뷰 0건 — [YES24](https://www.yes24.com/product/goods/145268319)
- **『ROS 로보틱스 프로그래밍』** Lentin Joseph 저, 배진호 역, 에이콘, 2017 — MoveIt!·내비게이션 스택(ROS 1) **[stale]** — [교보문고](https://product.kyobobook.co.kr/detail/S000000935968)
- 『ROS 로봇 프로그래밍』(루비페이퍼, 2017)의 영문판 PDF가 ROBOTIS를 통해 무료 공개 **[stale, ROS 1 Kinetic]** — [ROS Robot Programming EN 2017](https://personalpages.bradley.edu/~smiah/files/webBooks/ROS-Robot-Programming-EN2017.pdf); [ROBOTIS 판매 페이지](https://robotis.us/ros-robot-programming-book/)
- 교보 eBook 『ROS로 배우는 로봇 운영체제』(2025-03-04, ISBN 9791194738565)는 페이지에 "AI(생성형) 활용 제작 도서" 표시 — 품질 신호 낮음 — [교보 eBook](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000011164952)
- 2026년 영문 신간(한국어판 없음): *Mastering ROS 2 for Robotics Programming*(Packt; Nav2·MoveIt 2·ros2_control·RL) — [Packt](https://www.packtpub.com/product/MasteringROS2forRoboticsProgramming/9781836209010); *A Concise Introduction to Robot Programming with ROS 2, 2nd ed.*(2026-06) — [ROS Discourse](https://discourse.openrobotics.org/t/a-concise-introduction-to-robot-programming-with-ros-2-second-edition/44410); *Building Robots with ROS 2: A Practical Guide*(2026) — [Akademibokhandeln](https://www.akademibokhandeln.se/bok/building-robots-with-ros-2/9789819577736)

**위키독스/틸노트 무료 온라인 책(사실상 한국어 신간의 주류)**

- **『ROS 2 Jazzy 문서』**(wikidocs book 16208) — docs.ros.org/en/jazzy와 동일 목차(개념·자습서)의 한국어판; 번역자 표기 없음 — [WikiDocs](https://wikidocs.net/book/16208); 하위 페이지 예: 빌드 시스템(254965), 클라이언트 라이브러리(254947), ROS 2 개요(275694)
- **『ROS2로 배우는 자율주행 로봇 센서 융합과 SLAM』** 최종명(Coffee Press) — LiDAR·카메라·IMU 토픽 처리 → EKF 센서융합 → SLAM Toolbox; 최종 편집 2025-10 — [WikiDocs](https://wikidocs.net/book/18464)
- **『ROS2 로봇 만들기』** 정준용 — 입문 교재, 최근 수정 2026-07, **ROS 2 Jazzy + Gazebo Harmonic** 부록 추가 중, 전용 ROS2 2바퀴 로봇 키트(스마트스토어 판매, 라즈베리파이 OS SD카드 포함) 연계 — [WikiDocs](https://wikidocs.net/265188); [키트 안내](https://wikidocs.net/265243)
- **『모두를 위한 Humanoid Robot』**(wikidocs book 18009) — "모두를 위한 Isaac Lab" 장에서 Isaac Lab 한국어 설치 가이드·튜토리얼 제공, "Humanoid Robot LAB 3기"를 통해 계속 수정·작성 예정 — [WikiDocs](https://wikidocs.net/book/18009)
- Isaac Lab 공식 문서 기반 한국어 재구성 튜토리얼(BSD-3 라이선스 명시) — [WikiDocs 291244](https://wikidocs.net/291244); 새 로봇 추가 튜토리얼 — [WikiDocs 291207](https://wikidocs.net/291207); Isaac Sim 입문 '1장 Hello! Isaac Sim' — [WikiDocs 277523](https://wikidocs.net/277523)
- 2026년에 작성 중인 위키독스 책의 부록 페이지 "[참고] 개념 안내 부록 (미실측) · ROS 2 Jazzy 기준 · 검수 완료"(431696) 및 "Isaac Sim 6.0 / Isaac Lab 기준"(431697)이 Isaac Lab 모방학습 데이터 수집 → LeRobot 형식 내보내기 경로를 설명(미실측 표기) — [WikiDocs 431697](https://wikidocs.net/431697)
- 틸노트 『ROS2로 완성하는 자율주행 로봇』(노드·TF·SLAM·Nav2, 무료) — [tilnote](https://tilnote.io/books/6a05ffdcc9380346b3cd233f)
- 『AIoT 프로젝트로 배우는 라즈베리파이5』(호스비, 위키독스, 최종 편집 2025-09, "제작중") — [WikiDocs](https://wikidocs.net/book/18006)
- PythonRobotics 한국어 강의노트(로보틱스 정의·역사·기술) — [WikiDocs 블로그](https://wikidocs.net/blog/@hueykim/3015/)

**로봇공학 이론 교재 / 번역서**

- *Modern Robotics* 한국어 번역 종이책: 검색에서 **확인되지 않음**; 한국어로 접근 가능한 경로는 코세라 한국어 강좌와 영문 무료 PDF — [istein.tistory](https://istein.tistory.com/142); [parkpakrsu.tistory](https://parkpakrsu.tistory.com/407)
- Craig *Introduction to Robotics* 한국어판: 교보문고 결과가 검색에 노출되지 않아 **확인 불가**; 한경국립대 KOCW '로봇기구학'은 이 영문 원서를 교재로 사용 — [KOCW 강의계획서 PDF](https://www.kocw.net:444/home/common/contents/syllabus/1403263_2021072195159103.pdf)
- 교보 eBook 『로봇 공학의 기초와 응용』(2025-03) — 구성요소·센서·응용 사례 개론서, 기구학/제어 중심 여부 불명 — [교보 eBook](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000011164891)

**아두이노 / 라즈베리파이**

- 『모두의 라즈베리파이썬』 개정판(길벗) 판권 PDF 존재 — [길벗](https://gfile.gilbut.co.kr/gilbut/bookdata/BN002363/copyright/모두의라즈베리파이썬개정_판권.pdf)
- 『라즈베리파이4』 리디북스 전자책 2025-03-27 출간(로봇 특화 여부 불명) — [리디북스](https://ridibooks.com/books/3478033298)
- 2024–2025년 출간 '아두이노/라즈베리파이 로봇 제작' 종이책은 검색에서 명확히 확인되지 않음 — [검색 결과](https://tilnote.io/books/6a05853ad4da283b96340fd7/6a058539d4da283b96340fb9)

### Inferences
- 한국어 ROS 2 "정식 출판" 서적은 2021–2022년에 멈춰 있고, 2025년 이후의 지식 갱신은 위키독스 등 개인 저자의 무료 온라인 책이 담당 → 품질 편차가 크고 ISBN/리뷰 같은 품질 신호가 없음.
- Jazzy 기반 한국어 자료는 2026년부터 출현(정준용 위키독스, 패스트캠퍼스 MP, 유데미 R2R Jazzy 호환 표기)하나 대부분 Humble 기준.
- 이론 교재(기구학·동역학·제어)는 번역서 부재 + 코세라 한국어판·KOCW 강의가 대체.

### Gaps
- 『ROS2 혼자공부하는 로봇SW』의 ISBN·가격·목차(교보 페이지 빈 응답).
- 위키독스 431696/431697 부록이 속한 책의 제목·저자(403).
- 공업수학/제어공학 한국어 교재 목록은 조사 범위 내에서 수집하지 못함.
- 교보문고/예스24 내부 "출간연도 필터" 검색을 수행하지 못해 2024–2026 로봇 신간 전수 목록은 미완.

---

## KQ3. 한국어 유튜브 / 블로그 / 커뮤니티 (OROCA, ROS Korea, 표윤석, 로보티즈, 디스코드/카카오)

### Takeaway
한국 ROS 커뮤니티는 **구조적으로 약화**되어 있다. ROS Discourse Korea Users Group은 2025-04 이후 활동이 없고 최근 글의 대부분은 The Construct 광고이며, 오로카의 oroca.org 도메인은 도박 사이트로 넘어갔다(네이버 카페 openrt는 로그인 필요로 상태 미확인). 반면 **ROSCon Korea 2026(2026-01, 판교, 광운대·PinkLAB·XYZ 주최)**이 처음 열렸고, 유튜브에서는 **민형기(PinkWink)의 R2R 무료 강의**가 가장 체계적인 한국어 ROS 2 영상 시리즈이다. 로보티즈는 한국어 e-Manual(docs/kr)을 유지하나 docs.robotis.com으로 통합·삭제 예고 중이며 TurtleBot3 학습 콘텐츠는 영문 기준이다.

### Cited Findings

**커뮤니티**

- ROS Discourse **Korea Users Group**: 최신 활동 2025-04-16("Robotics Developer Masterclass 배치 7"), 2026년 게시물 없음; 2024–2025 글은 모두 The Construct 마스터클래스 홍보; 표윤석(Pyo) 게시물은 "ROS 2 Docs in Korean"(2022-12), "Ros 2 세미나 자료 공개"(2022-06, 조회 9,276), "제9회 오픈 로보틱스 세미나 발표 영상·자료"(2023-03) — [ROS Discourse Korea](https://discourse.openrobotics.org/c/local/korea/33)
- **ROSCon Korea 2026**: 2026-01-21~22, 판교 글로벌비즈센터; 광운대 주최, 로보틱스·AI 교육기업 PinkLAB과 XYZ 공동 주최; Day1 ROS 2 아키텍처·Gazebo·모방학습 워크플로·휴머노이드 제어·서비스로봇, Day2 LLM+로보틱스·피지컬 AI·핸즈온 워크숍; 광운대 로봇게임단 RO:BIT 자원봉사; 대회장 박수한 교수; "국내 ROS 생태계의 이정표" — [Korea Times 2026-01-29](https://www.koreatimes.co.kr/amp/southkorea/20260129/kwangwoon-university-hosts-robot-developer-conference)
- **오로카(OROCA, Open RObotics technology CAfe)**: 2014-12 서울 1회 ROS Korea 밋업, 2015-05 2회 밋업 주최("one of the largest Korean robotics community") — [ROS.org 2014](https://www.ros.org/news/2014/11/ros-korea-users-meetup.html); [ROS.org 2015](https://www.ros.org/news/2015/06/2nd-ros-meetup-in-korea.html); GitHub oroca/oroca-ros-pkg — [GitHub](https://github.com/oroca/oroca-ros-pkg)
- **oroca.org 도메인은 2026-11 현재 "Live Casino Guides & Betting Tips" 도박 블로그**로 운영되어 커뮤니티 링크·내용 없음 — [oroca.org](https://oroca.org/)
- 판교오로카 2023-04 『ROS 2로 시작하는 로봇 프로그래밍』 12주 완독 챌린지 — [makepluscode.tistory](https://makepluscode.tistory.com/228); Robert Choi이 오로카 판교 로컬 밋업에서 매주 금요일 ROS2 스터디 운영 후 GitBook "ROS2 하루에 입문하기" 공개 — [robertchoi.gitbook.io](https://robertchoi.gitbook.io/ros2/)
- "2026 오로카 판교 오픈랩 세미나" 2026-01-24 판교 텔레칩스 회의실, 선착순 20명·참가비 1만 원, 아두이노·ROS2·자율주행·드론·4족 로봇 주제, 아두이노 Uno Club 운영 — [tilnote](https://tilnote.io/pages/696c36aab29e02907eb65462)
- 네이버 카페 cafe.naver.com/openrt(오로카)는 검색에 직접 노출되지 않았고(로그인 필요) 저자 글 cafe.naver.com/openrt/24070이 책 실습자료에 인용됨 — [tilnote 인용](https://tilnote.io/en/pages/6a058539d4da283b96340fb7)
- 한국어 ROS 디스코드/카카오 오픈채팅: 검색에서 **확인되지 않음**; 공식 OSRF Discord(영문)만 확인 — [Open Robotics Discord](https://www.openrobotics.org/blog/2023/3/13/osrf-launches-an-official-discord-server)
- 모두의연구소 모두모임(modulabs.co.kr/community/momos)과 PyTorch KR 포럼이 Physical AI 무료 교육 공지 채널로 활용됨 — [PyTorch KR](https://discuss.pytorch.kr/t/physical-ai-rl-vla-physical-ai/12243)

**유튜브(한국어)**

- **민형기 R2R 무료 강의**: "[ROS2] 0. 우리 강의를 소개합니다｜R2R 입문", "1-1 Ubuntu 설치", "3-5 Service call", "입문편 한 번에 몰아보기", 적용 버전 Humble — [YouTube](https://www.youtube.com/watch?v=u9Fubn3JRVA); [R2R 실전과정 재생목록](https://www.youtube.com/playlist?list=PL0xYz_4oqpvjyrCQKB1eiAbZG-bCDe98_); "PinkWink의 ROS2 강의 6장 Python class" — [YouTube](https://www.youtube.com/watch?v=E4OodDFgvME)
- **강티처(애드인에듀) ROS2 무료강의** EP1 Windows–Ubuntu 듀얼부팅 — [YouTube](https://www.youtube.com/watch?v=sWmrAb1MJvI)
- **Frenz AI로봇랩 2기** "ROS2 이론 및 설치 at Windows WSL2" — [YouTube](https://www.youtube.com/watch?v=AUSOnvOTt2s)
- "ROS2 속성 마스터 과정 1. 개요 및 개발환경 구성" — [YouTube](https://www.youtube.com/watch?v=w5aWnWVuAis&vl=ko)
- 로보티즈 TurtleBot3 튜토리얼 영상 업데이트(2025–2026, 영문): ArUco 마커·Follower·Panorama 등 — [ROS Discourse](https://discourse.openrobotics.org/t/new-turtlebot3-tutorial-videos-aruco-marker-follower-panorama/43666); [TB3 Tutorial Video Update](https://discourse.openrobotics.org/t/tb3-turtlebot3-tutorial-video-update/42121)
- 로보틱스 유튜브 채널 구독자 수 비교 자료는 검색에서 찾지 못함 — [검색 결과](https://www.inflearn.com/course/robot-control-taught)

**블로그 / 문서(한국어)**

- youngju.dev 2026-05 "로보틱스 개발 ROS 2 2026 — Nav2 / MoveIt / Gazebo / Isaac Sim / MuJoCo / LeRobot / GR00T 심층 가이드" 및 "ROS 2 Robotics Stack 2026 (Jazzy/Kilted…)" — "2026년 새 프로젝트는 Jazzy 또는 Lyrical, 운영 중인 산업 시스템은 Humble이 압도적" — [youngju.dev](https://www.youngju.dev/blog/culture/2026-05-15-robotics-development-ros2-2026-nav2-moveit-isaac-sim-mujoco-lerobot-deep-dive); [youngju.dev](https://www.youngju.dev/blog/culture/2026-05-16-ros2-robotics-stack-2026-jazzy-kilted-gazebo-moveit-isaac-sim-drake-foxglove-nav2-deep-dive)
- Zetabank **Zeta Edu ROS2** 한국어 readthedocs(turtlesim·노드·토픽·서비스·파라미터·액션) — [zeta-edu-ros2](https://zeta-edu-ros2.readthedocs.io/en/latest/search.html); 한국어 사용자 매뉴얼 — [user-manual-kr](https://user-manual-kr.readthedocs.io/en/latest/search.html)
- 서울대 rllab 'Intelligent Systems 2025' ROS2 튜토리얼 PDF(한국어 슬라이드) — [rllab.snu.ac.kr](https://rllab.snu.ac.kr/courses/intelligent-systems-2025/project_files/ros2_tutorial.pdf/@@download/file)
- Nav2 한국어 블로그 조각: TF 설정 번역(jihong.tistory) — [jihong.tistory](https://jihong.tistory.com/m/591); Nav2 BT 시뮬레이션 노트(Notion) — [heesang0917.notion](https://heesang0917.notion.site/4-1-BT-Nav2-13281d439b47803f80a2fa340865a214); costmap/planner/controller 개념(틸노트) — [tilnote](https://tilnote.io/pages/6a05ffdac9380346b3cd2317)
- velog ROS2 학습 노트가 "오로카 11강"을 참고문헌으로 인용 — [velog](https://velog.io/@tmddn833/011-ROS-2-액션-action)
- 모두의연구소 Notion 로봇 소프트웨어 플랫폼/ROS 노트, 터틀봇 시리즈 하드웨어 정리 — [modulabs notion](https://modulabs.notion.site/10-65340cb0d83f4a70b047f923ba65c05f)
- mint-lab Robotics Notion, robotiz.notion.site 등 개인 정리 페이지 존재 — [mint-lab](https://mint-lab.notion.site/Robotics-486f2e1102df442d840d333ebf9dc4a5)
- 한국어 ROS 위키(ko/ROS/Tutorials) 미러가 남아 있으나 ROS 1 **[stale]** — [umd 미러](https://mirror.umd.edu/roswiki/ko(2f)ROS(2f)Tutorials.html)

**로보티즈(ROBOTIS) 한국어 자료**

- **한국어 e-Manual**(emanual.robotis.com/docs/kr/) 존재: DYNAMIXEL 전 시리즈·Protocol 1.0/2.0, OpenMANIPULATOR-P/X, TurtleBot3, ROBOTIS OP/OP2/OP3, 똘망3, 교육 키트(STEAMCUP·바이올로이드·ENGINEER 등), SDK/Workbench/Wizard/R+; 단, 페이지 상단에 "ROBOTIS Docs(docs.robotis.com)로 통합되어 7월 삭제 예정" 영문 공지 — [ROBOTIS e-Manual KR](https://emanual.robotis.com/docs/kr/)
- **docs.robotis.com**: 영어/한국어(/ko/) 제공; TurtleBot3, OpenMANIPULATOR-P/X, OMY·OMX(Physical AI용 AI 매니퓰레이터), AI Worker(세미휴머노이드), OP3, THORMANG3, DYNAMIXEL SDK/Wizard/Workbench 문서; 메인 페이지에 ROS 2 튜토리얼 항목은 없음; © 2026 — [ROBOTIS Docs](https://docs.robotis.com/)
- TurtleBot3 e-Manual 학습 페이지(기본 조작·내비게이션·라인추종·객체인식·MoveIt 모션플래닝·그래스핑)는 **영문**; Quick-start/Basic examples @Humble, Simulation @Jazzy — [TB3 Learn](https://emanual.robotis.com/docs/en/platform/turtlebot3/learn/); [TB3 Features](https://emanual.robotis.com/docs/en/platform/turtlebot3/features/)
- TurtleBot3 신규 예제(Patrol·Interactive Marker 등) 2025–2026 공개 — [ROS Discourse](https://discourse.openrobotics.org/t/tb3-new-turtlebot3-examples-are-here/43239)
- ROBOTIS 커뮤니티 포럼(community.robotis.us)은 영문 — [ROBOTIS Community](https://community.robotis.us/t/dynamixel-ros2-quick-start/253)

### Inferences
- "ROS Korea 유저그룹"은 공식 채널(Discourse)로는 사실상 휴면이며, 실질 활동은 네이버 카페·판교 오프라인 모임·유튜브·위키독스로 분산되어 신규 진입자가 찾기 어렵다. 오로카 도메인 상실은 커뮤니티 공식 창구 부재의 상징적 사례.
- ROSCon Korea 2026의 출범(광운대·PinkLAB·XYZ)은 2026년 커뮤니티 구심점이 **교육기업+대학** 연합으로 이동했음을 시사.
- 한국어 영상 콘텐츠는 설치~토픽/서비스 수준의 입문에 집중되어 있으며 Nav2·MoveIt 2·Isaac Lab 수준의 무료 한국어 영상 시리즈는 확인되지 않음.

### Gaps
- 네이버 카페 오로카(openrt)의 현재 회원 수·게시 활동량(로그인 필요).
- 각 유튜브 채널의 구독자 수·조회수·최신 업로드일(검색 결과에 미포함).
- 카카오 오픈채팅/디스코드 한국어 ROS 방의 존재 여부(검색 불가 영역).

---

## KQ4. 대학/공개 강의 (KOCW, KAIST/서울대, 로봇공학과 교육과정 예시)

### Takeaway
KOCW에는 기구학·동역학·제어 중심의 로봇공학 이론 강의(부산대 로봇공학 특론, 한경국립대 로봇기구학, 금오공대 48시간 로봇공학 등)가 있으나 대부분 2020–2022년 촬영이며 ROS 2/현대 툴체인은 다루지 않는다. 학부 로봇학과 교육과정(광운대 로봇학부, 영남대 로봇공학과)은 1학년 로봇학입문·수학/프로그래밍 → 2–3학년 로봇학실험 1~4·로봇운동학(필수) → 3–4학년 로봇제어·컴퓨터비전·딥러닝·로봇내비게이션·강화학습·피지컬AI → 4학년 캡스톤 순으로 구성된다.

### Cited Findings

**KOCW (kocw.net)**

- **부산대 '로봇공학 특론(I)'** — 매니퓰레이터 기구학·동역학·궤적계획·로봇 제어·센서/구동기·적응제어·강인제어·안정도; 차시에 순/역기구학·자코비안·계산토크 제어·슬라이딩 모드 제어 — [KOCW](http://www.kocw.net/home/cview.do?mty=p&kemId=1344305)
- **한경국립대 '로봇기구학'** — DH 표기법 정기구학·역기구학 예제/연습문제 영상, 2020-2학기, 조회수 42,659; 교재 Craig *Introduction to Robotics*; 평가 출석 15%/과제 10%/시험 75% — [KOCW](http://www.kocw.net/home/cview.do?mty=p&kemId=1403263); [강의계획서 PDF](https://www.kocw.net:444/home/common/contents/syllabus/1403263_2021072195159103.pdf)
- **국립금오공대 '48시간만에 끝내는 로봇공학'** — 좌표계·동차변환·순/역기구학·속도기구학(자코비안·특이점)·경로계획 — [KOCW](http://kocw.net/home/cview.do?cid=11f6545e07fc5d1f)
- 동국대 '로봇 프로그래밍' — [KOCW](http://www.kocw.net/home/cview.do?mty=p&kemId=697864&ar=link_gil); 부산외대 '로봇 프로그래밍' — [KOCW](http://www.kocw.net/home/cview.do?mty=p&kemId=1350553); 건국대 '메카트로닉스' — [KOCW](http://www.kocw.net/home/cview.do?mty=p&kemId=1362643); 충북대 '기구학'(로봇은 응용 사례) — [KOCW](http://www.kocw.net/home/cview.do?mty=p&kemId=1084753)
- 세종대 '로보틱스' 강의계획서(2024): 좌표계·좌표변환·기구학·동역학·제어·액추에이터/센서, 3학점 전공선택 — [KOCW PDF](https://www.kocw.net:444/home/common/contents/syllabus/1487027_202403079496577.pdf)
- 터틀봇3 기반 자율주행 로봇 제어 'ROS 프로그래밍' 강의계획서(2022; 개발환경 구축·RViz·터틀봇3 제어) — [KOCW PDF](https://www.kocw.net:444/home/common/contents/syllabus/1431016_202205061649475.pdf)
- KOCW 정의: 국내외 대학·기관이 자발적으로 공개한 강의 동영상·자료를 무료 제공 — [서울과기대 OCW 안내](https://sics.seoultech.ac.kr/elec/ocw/)

**KAIST / 서울대**

- KAIST Robotics Program 공식 페이지는 robots.kaist.ac.kr로 이전(한국어 페이지 포함) — [KAIST RP](https://rp.kaist.ac.kr)
- KAIST 전기및전자공학부 '융합적 로봇공학개론'(좌표변환·항법·제어·운동계획) 및 로봇 매니퓰레이터 기구학/동역학/제어 과목 소개 — [KAIST EE](https://ee.kaist.ac.kr/node02/13324/); [KAIST EE 연구분야](https://ee.kaist.ac.kr/research/robotics-control/)
- 서울대 rllab 'Intelligent Systems 2025' ROS2 튜토리얼 PDF 공개 — [rllab](https://rllab.snu.ac.kr/courses/intelligent-systems-2025/project_files/ros2_tutorial.pdf/@@download/file)
- **서울대 DYROS 로보틱스 부트캠프 2025년 동계** 모집공고(PDF, 2025-12-05 생성; 연락처 (연락처는 원문 공고 참조)): 부트캠프1 ROS2 입문·시뮬레이션 실습, 부트캠프2 ROS2 실제 하드웨어 제어 시스템 개발; 지원 마감 1차 2025-12-15, 2차 2025-12-30 — [SNU 융합과학기술대학원 PDF](https://convergence.snu.ac.kr/wp-content/uploads/sites/214/2025/12/DYROS_로보틱스_부트캠프모집공고2025년도_동계.pdf) (PDF 본문 텍스트 추출 실패, 검색 스니펫 기준)
- KAIST·서울대의 로봇공학 **공개 유튜브 강의**는 검색에서 확인되지 않음 — [검색 결과](https://rp.kaist.ac.kr)

**학과 교육과정 예시**

- **광운대학교 로봇학부**(2010년 정보제어공학과 개편, "국내 최초 로봇 전문 학부"; 정보제어전공·지능시스템전공·AI로봇전공) 교과과정(2023/2024학년도 입학자 기준):
  - 1학년: 로봇학입문(전공선택 3학점, 1·2학기 중 택1), 교양으로 대학수학·공학수학·선형대수학·확률및통계·대학물리·C프로그래밍·자바프로그래밍
  - 2학년 1학기: 로봇학실험1/AI로봇실험1(전공필수) · 2학년 2학기: 로봇학실험2/AI로봇실험2(전공필수)
  - 3학년: 로봇학실험3·4(전공필수), **로봇운동학**(2023학년도 입학자부터 전공필수, 기존 로봇제어·자동제어1 대체)
  - 전공선택: 로봇제어, 컴퓨터비전, 딥러닝, 로봇내비게이션, 강화학습, 자연어처리, **피지컬AI**, 임베디드시스템, 온디바이스인공지능
  - 4학년 1학기: 캡스톤설계(전공선택 3학점)
  — [광운대 로봇학부 교과과정](https://cni.kw.ac.kr/program/process.php); [정보제어전공 교육과정](https://www.kw.ac.kr/ko/univ/electronic08_4.jsp); [대학저널 2022](https://dhnews.co.kr/news/view/179524483013280)
  - 정보제어전공 전공기초: 로봇학 입문·기초역학·전자기학·디지털공학·회로이론·컴퓨터구조; 전공일반: 메카트로닉스·모터제어·액추에이터·자동제어·로봇공학; 전공심화: 임베디드 시스템·로봇설계·로봇 응용 시스템·캡스톤 — [광운대 교과목안내](https://www.kw.ac.kr/ko/univ/electronic08_5.jsp)
- **영남대학교 로봇공학과**: 1학년 공학 기초·입문설계 → 2학년 프로그래밍·정역학·3D 모델링 → 3학년 로봇 기구학·설계·AI·컴퓨터비전 → 4학년 심화·종합설계; 2학년부터 로봇 메커니즘 설계·로봇 전자회로·로봇 소프트웨어 트랙 — [영남대](https://www.yu.ac.kr/main/academics/robotics.do)
- **한양대 ERICA**: 학부는 '지능형로봇학과'/'지능형로봇 융합전공', 대학원 로봇공학과(입학정원 30명); 두산로보틱스 협동로봇 공식 인증교육센터 설립 — [전자신문 2024-07](https://www.etnews.com/20240725000109); [phdkim](https://phdkim.net/gradinfo/school/29/department/483)
- 광운대가 로봇 분야 혁신융합대학(지능형로봇) 사업 중심대학 — [전자신문 2023-07](https://www.etnews.com/20230714000076)

### Inferences
- 대학 커리큘럼은 "수학/프로그래밍 → 실험(하드웨어) → 운동학(필수) → 제어/비전/딥러닝/내비게이션 → 캡스톤"의 공통 골격을 가지며, 2024년 이후 '피지컬AI'·'강화학습'·'온디바이스AI' 과목이 추가되는 추세.
- KOCW 이론 강의는 기구학 기초 학습에 유용하지만 촬영 시점(2020–2022)과 ROS 2 부재로 SW 개발자용 실습 경로로는 부족.

### Gaps
- 광운대 3·4학년 전공선택 과목의 학기별 배치(페이지 표에 미표기).
- 한양대 ERICA·한국공학대 로봇공학과의 학부 교과목표(검색 미노출).
- DYROS 부트캠프의 정원·비용·세부 커리큘럼(PDF 텍스트 추출 실패).

---

## KQ5. 정부/공공 프로그램, 부트캠프(KDT), 기업 교육, 메이커 교육

### Takeaway
2025–2026년 한국 로봇 교육의 가장 큰 공급원은 **고용노동부 K-디지털 트레이닝(KDT) 국비 부트캠프**이며, ROS 2 + SLAM/Nav2를 기본으로 2026년에는 '피지컬 AI'(모방학습·LeRobot SO-101·Isaac Sim/MuJoCo·VLA)를 전면에 내세운 과정(동국대 DAPIER, 로보티즈·클로봇 채용연계, 한화로보틱스 테크스쿨, XYZ·NVIDIA, SeSAC, 성균관대, 한국IT교육원)이 급증했다. 모두 600~1,000시간 풀타임·내일배움카드 요건·미취업자 대상이라 재직 개발자는 접근이 어렵다. KIRIA는 수서 '마이스터 로봇화 지원센터'에서 재직자 대상 코봇·비전·ROS 실습을 운영하며, 기업 교육은 레인보우로보틱스(RB 협동로봇 기본/고급)가 공개 프로그램을 운영하고 두산로보틱스는 KDT '로키 부트캠프'(9기) 형태로 참여한다.

### Cited Findings

**정부/공공 (KIRIA 등)**

- KIRIA '빅데이터 활용 마이스터 로봇화 기반 구축 사업'(2021~현재): 온라인 데이터 기초 → 오프라인 코봇·비전 장비 실습; ROS 기반 시각화·비전 처리·코봇 운용 과제; 거점 서울 강남구 수서동 **마이스터 로봇화 지원센터**(로봇·장비 80대 이상), 안산·구미 교육장; 2025-11-12 '한국의 실용적 미래 로봇교육 전환과 과제' 콘퍼런스에서 "로봇 사용법 + SI 역량을 공통 바탕으로" 제안, 설문 기업 77.4%가 지난 1년간 로봇 교육 無; 확장안으로 코봇 티칭·자율주행 SW/플릿 관제·휴머노이드·AI 피킹·그래스핑·시뮬레이션/원격 모듈 — [헬로티 2025-11-13](https://www.hellot.net/mobile/article.html?no=107176); [헬로티](https://www.hellot.net/mobile/article.html?no=114710)
- KIRIA 로봇 창의교실(사회적 배려 아동) 2026-09 — [헬로티 태그 KIRIA](https://www.hellot.net/news/tag_list_all.html?tag=KIRIA)
- 모두의연구소 모두모임 경유 **'Physical AI 무료 교육(RL·VLA)'**: 강사 박철(코스모다이나믹 대표), 안산 경기테크노파크 '로봇직업교육센터' 오프라인, 4회(2026-11-14 ROS2 로봇 제어 / 11-21 강화학습·HIL-SERL / 11-28 모방학습·ACT / 12-05 VLA·SmolVLA 실로봇 피킹), 무료, **고용보험 가입 재직자만**(프리랜서·구직자·학생 제외) — [PyTorch KR](https://discuss.pytorch.kr/t/physical-ai-rl-vla-physical-ai/12243); [모두모임 신청](https://modulabs.co.kr/community/momos/620)

**KDT / 국비 부트캠프 (2025–2026)**

- **대구가톨릭대 ROS2 기반 AI 융합 로보틱스 부트캠프**(KDT, "대경권 유일"): 960시간, 2025-09-08~2026-02, 전액 무료, ROS2·로봇 제어 프로그래밍·AI/딥러닝·SLAM/자율주행, 300여 기업 취업연계; 신청 dcurobot.kr — [대학저널 2025-08-21](https://dhnews.co.kr/news/view/1065572624453342)
- **두산로보틱스 로키부트캠프 AI·로봇 엔지니어 양성과정 9기**: 접수 2026-02-27~03-29; 국민내일배움카드 필수, 전공 무관, 미취업자/이직준비자; Python·컴퓨터비전·협동로봇·모바일 매니퓰레이터·디지털트윈·ROS 로봇 프로그래밍, 최대 6개 실무 프로젝트, 장학금 4종 — [씽유](https://thinkyou.co.kr/mobile/contest/61443/); [eopla](https://eopla.net/magazines/32797)
- **[로보티즈·클로봇] Physical AI 로봇 SW개발 채용연계과정**(대한상공회의소 서울기술교육센터, 화곡): 980시간, 2026-09-01~2027-03-31, 25명, 전액 국비, 국민취업지원제도 1유형 시 월 지원금; 모듈: 프로그래밍/Linux 80h, 산업용 네트워크 100h, Cortex-M ARM 120h, AI 프로그래밍 100h, **Physical AI 모방학습 및 ROS2 기반 로봇 제어 140h**, AI 비전 120h, ROS 2 이기종 로봇 시스템 110h, AI 통합 로봇 시스템 150h — [theteams](https://www.theteams.kr/activities/page/334015/le)
- **동국대 AI캠퍼스 DAPIER 2기 '피지컬 AI 기반 세미 휴머노이드 엔지니어 양성과정'**: 720시간, 2026-10-19~2027-02-25, 30명, 자부담 0원, 노트북/GPU 대여; 커리큘럼 로봇 프로그래밍 기초 72h → Linux & ROS2 Humble 112h → OpenCV AI 비전 80h → 딥러닝/트랜스포머 80h → **Hugging Face 기반 로봇 전이학습 96h** → **Isaac Sim/MuJoCo 80h** → **양팔 로봇 캡스톤(LeRobot SO-101 또는 jdcobot300) 120h**; 공학 인접 전공자 권장 — [슈퍼루키](https://superookie.com/seminars/6ac5b10d14371c4fe7230343)
- **한화로보틱스 AI 로봇(Physical AI) 테크 스쿨**: 1,000시간/6개월, 2026-07-27~2027-01-26, 구디아카데미(가산), 훈련비 1,800만 원 상당 전액 국비 + 월 40~90만 원 수당, 학사 이상; 분야 로봇 제어·로봇 비전·스마트팩토리 자동화 — [씽유](https://thinkyou.co.kr/mobile/contest/63782/)
- **XYZ × NVIDIA '[NVIDIA] AI융합 첨단산업 AX과정(로보틱스 전문가 양성)'**: 2026-10-12 성수동 XYZ 아카데미 개강, 약 900명 지원(15:1) 60명 선발, 960시간(실습 760h), NVIDIA DLI 기반 Isaac Sim/Isaac Lab → XYZ 양팔 휴머노이드 DEUX 프로젝트, 2027-04까지 — [벤처스퀘어](https://www.venturesquare.net/1119362/)
- **SeSAC Physical AI 로보틱스 실전랩**(서울시, 개포동): 609시간, 2026-09-07~2027-01-11, 28명, 무료+중식, 서울 거주 15세 이상; Python/PyTorch/OpenCV → ROS2(통신·패키지·launch·TF·커스텀 메시지) → SLAM/Nav2 → DDS·CAN·ROS-CAN 게이트웨이·MCU → 자율주행 통합·멀티로봇·로봇팔 프로젝트 — [서울대 CSE 공지](https://cse.snu.ac.kr/community/notice/25333)
- **한국IT교육원 '제조 AX × 피지컬 AI 부트캠프'(융합_AI 미래형모빌리티 로봇·ADAS)**: 대구/경북, 2026-08-26~2027-03-03, 17명, 자부담 40만 원, 월 최대 80만 원 수당; ROS2 자율주행·다중로봇 제어, LLM·VLA 프로젝트, 온디바이스 AI 드론 — [링커리어](https://linkareer.com/activity/344085)
- **성균관대 피지컬 AI 데이터 실무 부트캠프**(고용부 AI 캠퍼스): 30명, 2026-12-28~2027-06-16, ROS2 기반 로봇·VLA 데이터 엔지니어링·VLA 모델 학습/경량화 — [슈퍼루키](https://superookie.com/activities/6aed3800579160199f14a754)
- KG ICT 'KG-KAIROS 5기'(KDT)에 ROS/ROS2 실습 포함 — [한경 2025-06](https://magazine.hankyung.com/business/article/202506183964b); 'AI 자율주행 로봇 AMR 개발자 과정 1기' 2026-12 개강 — [슈퍼루키](https://superookie.com/seminars/6aebd3e1608d6219f55e5fe2)
- 원티드랩 '휴머노이드로 배우는 피지컬 AI 재직자 과정' 개설(2025-12 보도) — [디지털데일리](https://www.ddaily.co.kr/page/view/2025121009213850190); 크라우드웍스·성균관대 'VLA 데이터 엔지니어링 실무 양성과정' — [벤처스퀘어](https://www.venturesquare.net/1114584/)
- 아시아경제 교육센터 과정: ROS2 기반 SW 개발 + 피지컬AI·협동로봇, 현대차 스핀오프 CTO 멘토링 — [아시아경제 2026-04](https://view.asiae.co.kr/article/2026040915174763956)

**기업 교육**

- **레인보우로보틱스**: 협동로봇 기본 과정(조작·프로그램 작성·시스템 설정), 고급 과정(고급 프로그래밍; 선택 과목 PLC 연동·부가축), 온라인 신청; 'RB 협동로봇 기본교육 안내 v2.0' PDF(2026-08) — [레인보우로보틱스 교육지원](https://rainbow-robotics.com/고객지원/교육지원/); [PDF](https://rainbow-robotics.com/wp-content/uploads/2026/08/RB-협동로봇-기본교육-안내-v2.0.pdf); 대학·연구소용 교육용 로봇 플랫폼 소개 — [레인보우 교육](https://rainbow-robotics.com/%EC%9D%B8%EC%82%AC%EC%9D%B4%ED%8A%B8/%EC%82%B0%EC%97%85-%EC%9E%90%EB%8F%99%ED%99%94/%EA%B5%90%EC%9C%A1/)
- **두산로보틱스**: 공식 아카데미 페이지는 검색에서 확인되지 않음; 2023 아동복지시설 협동로봇 교육(사회공헌) — [CEO스코어데일리](https://www.ceoscoredaily.com/page/view/2023081716031834513); 한양대 ERICA 인증교육센터 — [전자신문](https://www.etnews.com/20240725000109)
- **네이버랩스**: KAIST 기계공학과와 'AI 기반 모바일 플랫폼 시스템 설계·구현' 교육과정 공동 개발(TT봇, Intel·NI·NVIDIA·ROBOTIS 참여; 기사 날짜 미상) — [네이버 보도자료](https://navercorp.com/media/pressReleasesDetail?seq=29709)
- **현대로보틱스** 교육센터 과정: 검색에서 확인되지 않음 — [검색 결과](https://www.inews24.com/view/1081548)

**메이커 교육**

- 서울로봇인공지능과학관 '메이킹 데이'(2025-08): 청소년 34개 팀 로봇 시제품 → 메이커 페어 서울 2025 출품 — [서울시](https://news.seoul.go.kr/economy/archives/568197?listPage=1)
- 메이커스쿨 도봉(2025 하반기 11개 프로그램, 코딩·드론 원데이 클래스) — [헤럴드](https://www.heraldk.com/article/2025073014493093617); 동작구 초등 'AI 로봇 가을 특강'(2025-10) — [서울신문](https://m.go.seoul.co.kr/news/2025/10/13/20251013500118)
- 광운대 협업형 메이커스페이스 'Idea to Unicorn: 지능형 로봇 제작 패키지' 기업 모집(2025-06) — [벤처스퀘어](https://www.venturesquare.net/announcement/972137)

### Inferences
- 2026년 국비 부트캠프의 커리큘럼은 "Linux/ROS 2 Humble → OpenCV/딥러닝 → SLAM/Nav2 → 모방학습(ACT/SmolVLA) → Isaac Sim/MuJoCo → 실로봇(SO-101·협동로봇) 캡스톤"으로 수렴하고 있어, 플랫폼 커리큘럼의 '시장 표준' 참조 모델로 활용 가능.
- 재직 개발자용 파트타임/온라인 경로는 패스트캠퍼스 VOD와 KIRIA 재직자 과정·모두의연구소 단기 무료 교육뿐이며, "퇴사하지 않고 ROS 2→Physical AI까지 가는 구조화된 길"이 공백.

### Gaps
- KIRIA 재직자 과정의 정확한 과정명·모집 일정·수강료(언론 보도 외 공식 페이지 미확인).
- 두산로보틱스·현대로보틱스 공식 고객 교육 커리큘럼.
- 각 부트캠프의 수료율·취업률 등 성과 지표.

---

## KQ6. 한국 하드웨어/교육용 로봇 제조사의 학습 콘텐츠 (로보티즈, 로보링크, 로보메이션, 위고, 디바이스마트)

### Takeaway
로보티즈는 한국어 e-Manual·docs.robotis.com(/ko/)과 TurtleBot3/OpenMANIPULATOR/OMY/AI Worker 문서로 가장 풍부한 제조사 콘텐츠를 가지나 ROS 2 학습 튜토리얼 본문은 영문 중심이다. 로보메이션(햄스터)은 초중등 엔트리 블록코딩 교재 중심이고, 로보링크·알버트·위고의 개발자용 학습 콘텐츠는 검색에서 확인되지 않았다. 디바이스마트는 WLKATA Mirobot/MT4 ROS 로봇팔 키트를 판매하지만 강좌 콘텐츠는 없다. 개발자 대상 실습 하드웨어는 오히려 Hiwonder MentorPi/TurboPi, SO-ARM101, Slampibot, 정준용 2바퀴 키트처럼 강의/책에 번들된 소규모 키트가 주류다.

### Cited Findings
- 로보티즈 한국어 e-Manual·docs.robotis.com 상세는 KQ3 참조 — [e-Manual KR](https://emanual.robotis.com/docs/kr/); [ROBOTIS Docs](https://docs.robotis.com/)
- 로보티즈 AI 제품군(OMY·OMX·AI Worker)은 ai.robotis.com으로 연결 — [e-Manual KR](https://emanual.robotis.com/docs/kr/)
- 로보티즈는 KDT 채용연계과정(클로봇 공동)에 참여 — [theteams](https://www.theteams.kr/activities/page/334015/le); AW 2026에서 다이나믹셀 제품군 전시 — [헬로티](https://www.hellot.net/mobile/article.html?no=110873)
- **로보메이션 햄스터**: 엔트리 활용 코딩 e-Book, 햄스터 Plus 확장 활동지(서보·소리센서·그리퍼; © 2021), 활동지 홈페이지 다운로드 — [햄스터 e-Book](https://res.cloudinary.com/dfdbocvwq/image/upload/v1617255606/Hamster_e-Book_03_InstallTheEntry_ghpwbj.pdf); [햄스터 그리퍼](https://res.cloudinary.com/dfdbocvwq/raw/upload/v1626338546/20_Ham-Acc_Grip_DeliveryPie_a5ugyu.pdf); 2025–2026 교육용 로봇팔 '라쿤봇'(웹·Python·블록 코딩, 피지컬 AI 교육 표방) — [벤처스퀘어](https://www.venturesquare.net/1114961/)
- **디바이스마트**: WLKATA 미로봇 전문가 6축 ROS 로봇암 키트, MT4 Edu Kit(Python/C/ROS 지원, 모듈형) 판매 — [디바이스마트](https://www.devicemart.co.kr/goods/view?no=13057933); [MT4 Edu Kit](https://www.devicemart.co.kr/goods/view?no=15636079)
- **Zetabank**(제타뱅크): Zeta Edu ROS2 한국어 교육 문서, 한국어 사용자 매뉴얼 — [zeta-edu-ros2](https://zeta-edu-ros2.readthedocs.io/en/latest/search.html); [zeta-edu-content](https://zeta-edu-content.readthedocs.io/en/latest/search.html)
- 강의·책 번들 키트: Hiwonder MentorPi M1(약 40만 원)/TurboPi(약 14만 원) + RPi5 — [FastCampus](https://fastcampus.co.kr/data_online_ros2ai); SO-ARM101(STS3215) — [인프런](https://www.inflearn.com/course/robot-control-taught); LeRobot SO-101/jdcobot300 — [DAPIER](https://superookie.com/seminars/6ac5b10d14371c4fe7230343); Slampibot — [YES24](https://www.yes24.com/product/goods/145268319); ROS2 2바퀴 로봇 키트(스마트스토어) — [WikiDocs](https://wikidocs.net/265243)
- 로보링크·알버트·코드론·위고(Wego)의 교육 콘텐츠: 두 차례 검색에서 **확인되지 않음** — [검색 결과](https://www.venturesquare.net/1114961/)

### Inferences
- 국산 교육용 로봇(햄스터·알버트·코드론)은 K-12 블록코딩 생태계에 속해 SW 개발자 대상 ROS 2 학습 경로와 단절되어 있다.
- 개발자용 저가 실습 하드웨어는 중국산 키트(Hiwonder, SO-ARM/STS3215, WLKATA)에 의존하며, 한국어 설명서는 강의/책 저자가 개별적으로 작성.

### Gaps
- 로보링크(코드론)·알버트·위고 공식 교육자료 페이지(검색 미노출).
- 로보티즈 OMY/AI Worker의 한국어 ROS 2 튜토리얼 유무(ai.robotis.com 미확인).

---

## KQ7. 한국어 콘텐츠의 공백 (Isaac Lab, LeRobot/VLA, Nav2 심화, MoveIt 2 등)

### Takeaway
한국어 자료는 "설치 → 토픽/서비스 → SLAM/Nav2 기초"까지는 유료(패스트캠퍼스)·무료(R2R 유튜브, 위키독스)로 다층 공급되지만, **MoveIt 2는 유료 강의 1개(Jazzy, 2025)**, **Nav2 심화는 유료 강의 1개 + 블로그 조각**, **Isaac Lab은 작성 중인 위키독스 1권 + 유료 휴머노이드 강의 1개(2026)**, **LeRobot/VLA는 한국어 책 0권·온라인 강의 1개(LeRobot 미포함)·오프라인 국비/무료 단기 교육 일부**에 그친다. 체계적 한국어 ROS 2 기초 교재는 2021–2022년판이 마지막이며, 공식 문서의 Jazzy 한국어 번역(위키독스)이 그 공백을 메우고 있다.

### Cited Findings
- MoveIt 2: 한국어 자료는 패스트캠퍼스 'ROS 2로 시작하는 로보틱스 Motion Planning'(Jazzy, UR, 348,000원)뿐 — [FastCampus](https://fastcampus.co.kr/data_online_mp); 한국어 무료 MoveIt 2 튜토리얼 시리즈는 검색에서 확인 안 됨, 한국어 ROS 위키의 MoveIt! 항목은 ROS 1 — [umd 미러](https://mirror.umd.edu/roswiki/ko(2f)ROS(2f)Tutorials.html); 로봇 카테고리 페이지에 MoveIt 미기재 — [FastCampus 로보존](https://fastcampus.co.kr/event_online_robozone)
- Nav2 심화(BT·멀티로봇·Keepout 필터): 패스트캠퍼스 SLAM&Nav2 강의 Part 5에만 존재 — [FastCampus](https://fastcampus.co.kr/data_online_selfdriving); 무료 한국어 자료는 TF 번역·Notion 노트·틸노트 개념 글 수준 — [jihong.tistory](https://jihong.tistory.com/m/591); [heesang0917](https://heesang0917.notion.site/5-1-Nav2-13281d439b478020904bef3f059601e3)
- Isaac Lab: "모두를 위한 Isaac Lab"(위키독스, Humanoid Robot LAB 3기로 작성 중) — [WikiDocs](https://wikidocs.net/book/18009); NVIDIA 한국어 블로그 번역 — [NVIDIA KR](https://developer.nvidia.com/ko-kr/blog/fast-track-robot-learning-in-simulation-using-nvidia-isaac-lab/); 패스트캠퍼스 휴머노이드 보행(Isaac Lab+rsl_rl, 2026-08 완결) — [FastCampus](https://fastcampus.co.kr/data_online_humanoid); XYZ·NVIDIA DLI 오프라인 과정(60명) — [벤처스퀘어](https://www.venturesquare.net/1119362/)
- LeRobot/VLA: 패스트캠퍼스 VLA 강의는 LeRobot·OpenVLA·pi0·GR00T 미언급 — [FastCampus](https://fastcampus.co.kr/data_online_vla); LeRobot SO-101 실습은 DAPIER 국비 과정(120h 캡스톤) — [슈퍼루키](https://superookie.com/seminars/6ac5b10d14371c4fe7230343); SmolVLA/ACT/HIL-SERL 무료 교육은 재직자 한정 오프라인 4회 — [PyTorch KR](https://discuss.pytorch.kr/t/physical-ai-rl-vla-physical-ai/12243); LeIsaac(Isaac Lab + LeRobot SO101) 문서는 영·중·일·스·포만 있고 한국어 없음 — [Seeed Wiki](https://wiki.seeedstudio.com/simulate_soarm101_by_leisaac/); 인프런 SO-ARM101 강의는 LeRobot 미사용 Python 직접 구현 — [인프런](https://www.inflearn.com/course/robot-control-taught)
- Isaac Lab 한국어 자료 상태 평가: "한국어 자료가 전혀 없다는 말은 맞지 않지만 적은 편"이며 ROS 2 기초를 체계적으로 설명한 한국어 자료는 충분히 확인되지 않음 — [검색 결과 요약](https://wikidocs.net/book/18009)
- 배포판 격차: 2026년 블로그 "새 프로젝트는 Jazzy/Lyrical, 산업 현장은 Humble" — [youngju.dev](https://www.youngju.dev/blog/culture/2026-05-16-ros2-robotics-stack-2026-jazzy-kilted-gazebo-moveit-isaac-sim-drake-foxglove-nav2-deep-dive); 한국어 강의·부트캠프 대부분 Humble 명시(패스트캠퍼스 ROS2/SLAM·DAPIER 'ROS2 Humble' 등) — [FastCampus](https://fastcampus.co.kr/data_online_selfdriving); [DAPIER](https://superookie.com/seminars/6ac5b10d14371c4fe7230343)
- 커뮤니티 공백: Discourse 한국 그룹 2025-04 이후 무활동, oroca.org 도메인 상실 — [ROS Discourse Korea](https://discourse.openrobotics.org/c/local/korea/33); [oroca.org](https://oroca.org/)
- 한국어 ROS 2 기초 교재 최신판은 2021(루비페이퍼)/2022(잇플) — [YES24](https://www.yes24.com/Product/Goods/102949767); [교보문고](https://product.kyobobook.co.kr/detail/S000061695943)
- KIRIA 설문: 기업 77.4%가 지난 1년 로봇 교육 미실시; 교육 거점(수서·안산·구미) 접근성 문제 지적 — [헬로티](https://www.hellot.net/mobile/article.html?no=107176)

### Inferences
- 커리큘럼 플랫폼 관점의 가장 큰 기회 영역(한국어 기준): (1) ros2_control + MoveIt 2 매니퓰레이션 무료/저가 트랙, (2) Nav2 심화(BT·플러그인·멀티로봇·플릿) 트랙, (3) Isaac Lab/MuJoCo → sim2real 트랙, (4) LeRobot(SO-101) 데이터 수집→ACT/SmolVLA 학습→배포 트랙, (5) Jazzy 기준으로 갱신된 ROS 2 기초 레퍼런스. 이 중 (4)는 국비 부트캠프가 이미 표준 커리큘럼으로 채택하고 있어 재직자용 온라인 버전의 수요가 특히 높을 것으로 추정.
- "커뮤니티 공식 창구 부재"는 콘텐츠 공백과 별개로 신규 진입자가 자료를 발견하지 못하는 원인이므로, 큐레이션된 한국어 자료 인덱스 자체가 가치가 있음.

### Gaps
- 커뮤니티 내부(네이버 카페·카카오)에서 실제로 "무엇이 부족하다"고 토론된 1차 발언은 수집하지 못함(로그인 장벽·검색 미노출). 위 공백 판단은 공급 측 인벤토리의 부재로부터 도출한 것임.
- ros2_control·micro-ROS·Foxglove·Docker 기반 ROS 2 개발환경에 관한 한국어 자료는 별도로 조사하지 않음.
