---
id: m8-ros2-concepts-distros
title: ROS 2 개념과 배포판 선택
summary: ROS 2 를 "노드들이 메시지를 주고받는 계산 그래프"로 이해하고, 토픽·서비스·액션·파라미터의 쓰임과 DDS/RMW·QoS·도메인 ID 의 역할을 정리한 뒤, 2026년 말 기준 배포판(Jazzy·Lyrical·Humble) 중 무엇을 고를지 판단한다.
objectives:
  - 노드·토픽·서비스·액션·파라미터를 구분하고, 주어진 로봇 기능에 어떤 통신 방식이 맞는지 고를 수 있다.
  - DDS 기반 미들웨어(RMW), QoS, ROS_DOMAIN_ID 가 노드 발견과 통신에 어떤 영향을 주는지 설명할 수 있다.
  - 배포판 지원 기간과 Ubuntu 짝을 근거로 학습용 배포판(Jazzy)을 고른 이유를 설명할 수 있다.
prerequisites: []
difficulty: 2
estimated_minutes: 90
tags: [ros2, computation-graph, dds, qos, distributions, jazzy]
activities:
  - id: m8-ros2-concepts-distros-reading
    kind: reading
    title: 본문과 공식 Beginner CLI 자습서 읽기
    estimated_minutes: 45
  - id: m8-ros2-concepts-distros-quiz
    kind: quiz
    title: 통신 방식 고르기 퀴즈
    estimated_minutes: 15
  - id: m8-ros2-concepts-distros-exercise
    kind: exercise
    title: turtlesim 그래프를 CLI 로 해부하기
    estimated_minutes: 30
resources:
  - title: ROS 2 Releases
    url: https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases.rst
    kind: article
    note: 배포판·EOL 표(Jazzy 2029-05, Lyrical 2031-05).
  - title: ROS 2 Jazzy Tutorials
    url: https://docs.ros.org/en/jazzy/Tutorials.html
    kind: article
    note: "Beginner: CLI tools(환경 설정·turtlesim·노드·토픽·서비스·파라미터·액션·rqt_console·launch·rosbag)."
  - title: ROS 2 Jazzy 문서 한국어판 (위키독스)
    url: https://wikidocs.net/book/16208
    kind: book
    note: 개념·자습서 한국어 번역(docs.ros.org/en/jazzy 동일 목차).
---

# ROS 2 개념과 배포판 선택

M1–M4 에서는 좌표 변환, 운동학, 제어, 센서 처리를 각각 독립된 파이썬 코드로 다뤘다. 실제
로봇에서는 이 조각들이 서로 다른 프로세스, 때로는 서로 다른 컴퓨터에서 동시에 돌며 데이터를
주고받아야 한다. ROS 2(Robot Operating System 2)는 운영체제가 아니라 이 조각들을 잇는 통신 계층과
그 위의 도구·라이브러리 생태계다. 이 모듈은 읽기 중심으로 ROS 2 를 훑고, M5(상태 추정)·M6(계획·
Nav2)·M7(매니퓰레이션·MoveIt 2)의 ROS 2 레슨이 기대하는 기초를 만든다.

## 핵심 개념

### 계산 그래프

ROS 2 시스템은 **노드**(node)들이 이름 붙은 통로로 연결된 그래프다. 노드는 한 가지 일을 맡는
실행 단위(예: LiDAR 드라이버, 오도메트리 계산기, 경로 추종기)이고, 통로는 다음과 같다.

| 방식 | 패턴 | 언제 쓰나 | 예 |
|---|---|---|---|
| 토픽 | 발행/구독, 다대다, 비동기 | 계속 흐르는 데이터 | `/scan`, `/odom`, `/cmd_vel` |
| 서비스 | 요청/응답, 짧게 끝남 | 즉시 끝나는 질의·명령 | 맵 저장, 상태 초기화 |
| 액션 | 목표 → 피드백 → 결과, 취소 가능 | 오래 걸리는 작업 | "이 자세로 이동하라" |
| 파라미터 | 노드별 설정 값 | 실행 중 조정하는 설정 | PID 이득, 최대 속도 |

M3 의 경로 추종기를 ROS 2 로 옮긴다면 `/odom` 을 구독하고 `/cmd_vel` 을 발행하는 노드가 되며,
이득 $K_p$ 는 파라미터가 된다. "목적지까지 가라"는 요청은 피드백(남은 거리)과 취소가 필요하므로
서비스가 아니라 액션이 맞다.

### 메시지와 인터페이스

토픽·서비스·액션이 주고받는 데이터 형식은 `.msg`/`.srv`/`.action` 인터페이스로 정의된다.
`geometry_msgs/msg/Twist`(선속도·각속도), `sensor_msgs/msg/LaserScan` 같은 표준 메시지를 먼저
쓰고, 꼭 필요할 때만 커스텀 인터페이스를 만든다. 표준 메시지를 쓰면 RViz 같은 도구가 그 데이터를
바로 이해한다.

### DDS, RMW, QoS, 도메인

ROS 2 는 통신을 직접 구현하지 않고 DDS(Data Distribution Service) 같은 미들웨어에 맡긴다.
그 사이의 추상화 계층이 RMW(ROS MiddleWare interface)이며, 기본 구현은 Fast DDS 다
(`RMW_IMPLEMENTATION` 환경 변수로 Cyclone DDS 등으로 바꿀 수 있다). 중앙 마스터가 없어서 노드들은
네트워크에서 서로를 **자동 발견**한다. 같은 네트워크의 다른 로봇과 섞이지 않게 하려면
`ROS_DOMAIN_ID` 를 다르게 준다.

QoS(Quality of Service)는 통로별 전달 정책이다. 센서 스트림은 최신 값이 중요하므로 손실을
허용하는 *best effort* 를, 명령·맵처럼 빠지면 안 되는 데이터는 *reliable* 을 쓴다. 발행자와
구독자의 QoS 가 호환되지 않으면 **에러 없이 아무것도 오지 않는다**. "토픽은 보이는데 데이터가
안 온다"는 초보자 문제의 대표 원인이다.

### 배포판 선택

ROS 2 는 해마다 5월에 배포판을 내고, 짝수 해 배포판이 5년 지원(LTS)이다. 2026년 11월 기준:

- **Jazzy Jalisco** — LTS, 2029년 5월까지, Ubuntu 24.04 Tier 1.
- **Lyrical Luth** — LTS, 2026년 5월 출시, 2031년 5월까지, Ubuntu 26.04 Tier 1.
- **Humble Hawksbill** — LTS, 2027년 5월 종료, Ubuntu 22.04.
- Kilted Kaiju(비 LTS)는 2026년 11월 종료, ROS 1(Noetic)은 2025년 5월 31일에 종료됐다.

이 코스는 **Jazzy + Ubuntu 24.04** 를 기준으로 한다. 2024–2026년의 강의·책·레퍼런스 로봇 대부분이
Jazzy 를 겨냥하고, Lyrical 은 아직 학습 자료가 얇기 때문이다. 한국어 유료 강의는 Humble 기준인
경우가 많으니 명령의 `humble` 을 `jazzy` 로 바꿔 읽고, 어떤 자료든 **배포판을 먼저 확인**하는
습관을 들인다.

## 예제

turtlesim 으로 그래프를 관찰한다. 두 터미널에서 노드를 띄운 뒤 세 번째 터미널에서 살펴본다.

```bash
source /opt/ros/jazzy/setup.bash          # 모든 터미널에서 먼저
ros2 run turtlesim turtlesim_node         # 터미널 1
ros2 run turtlesim turtle_teleop_key      # 터미널 2

ros2 node list                            # /turtlesim, /teleop_turtle
ros2 topic list -t                        # 토픽과 메시지 형식
ros2 topic echo /turtle1/pose             # 흐르는 데이터 보기
ros2 interface show geometry_msgs/msg/Twist
ros2 service call /clear std_srvs/srv/Empty
ros2 param get /turtlesim background_r
ros2 action send_goal /turtle1/rotate_absolute \
  turtlesim/action/RotateAbsolute "{theta: 1.57}" --feedback
```

**연습 과제(exercise):** (1) 위 명령으로 turtlesim 의 노드·토픽·서비스·액션 목록을 표로
정리하라. (2) `rqt_graph` 로 같은 그래프를 그려 표와 비교하라. (3) 한 터미널에서만
`export ROS_DOMAIN_ID=7` 을 하고 `ros2 node list` 결과가 어떻게 달라지는지 설명하라.

## 자가 점검 질문

1. 로봇 팔에 "물체를 집어라"를 지시하는 인터페이스를 토픽·서비스·액션 중 무엇으로 만들겠는가? 이유는?
2. LiDAR 노드가 best effort 로 발행하는데 구독자가 reliable 을 요구하면 어떤 일이 생기는가?
3. 2026년 말에 학습을 시작하는 사람에게 Humble 보다 Jazzy 를 권하는 근거 두 가지를 들어라.

## 이 단계 공부법

1. **공식 자습서(먼저):** Jazzy Tutorials 의 *Beginner: CLI tools* 를 문서의 배포판 선택기를
   Jazzy 로 맞춘 상태에서 순서대로 따라 한다. 한국어가 편하면 위키독스 번역본을 옆에 둔다.
2. **본문:** 통신 방식 표와 QoS 절을 읽고, 앞 모듈의 코드(PID·경로 추종·필터)를 각각 어떤 노드와
   토픽으로 나눌지 종이에 그려 본다.
3. **연습:** 예제 명령과 연습 과제를 직접 실행한다. 설치 환경이 없다면 L8.4 의 Docker 방법을 먼저 본다.
4. **확인:** Releases 표에서 지금 쓰는 배포판의 EOL 을 찾아 메모해 둔다.

## 참고 자료

- ROS 2 Documentation, Releases — <https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases.rst>
- ROS 2 Jazzy Tutorials, Beginner: CLI tools — <https://docs.ros.org/en/jazzy/Tutorials.html>
- ROS 2 Jazzy 문서 한국어판(위키독스) — <https://wikidocs.net/book/16208>
