---
id: m10-system-architecture-requirements
title: "로봇 소프트웨어 아키텍처와 시스템 설계(요구사항→컴포넌트→인터페이스)"
summary: 만들고 싶은 로봇을 측정 가능한 요구사항으로 적고, 그것을 컴포넌트(노드)와 인터페이스(토픽·서비스·액션, 주기, 좌표계)로 분해하는 하향식 설계 과정을 익힌다. 요구사항 추적표를 Python 으로 검사해 빠진 요구사항과 끊긴 인터페이스를 찾는다.
objectives:
  - 기능 요구사항과 비기능 요구사항(성능·안전·비용·유지보수)을 검증 가능한 문장과 수치로 쓸 수 있다.
  - 요구사항을 감지·추정·계획·제어·하드웨어 계층의 컴포넌트로 나누고, 각 경계의 인터페이스(메시지 타입, 주기, frame_id)를 정의할 수 있다.
  - 기획→설계→시제품(Proto)→파일럿→양산으로 이어지는 로봇 개발 프로세스에서 캡스톤이 어느 단계에 해당하는지 설명할 수 있다.
prerequisites: [m6-nav2-architecture-behavior-trees, m8-reference-robot-code]
difficulty: 4
estimated_minutes: 120
tags: [system-design, requirements, architecture, interfaces, ros2, capstone]
activities:
  - id: m10-system-architecture-requirements-reading
    kind: reading
    title: 본문과 개발 프로세스 강의
    estimated_minutes: 45
  - id: m10-system-architecture-requirements-quiz
    kind: quiz
    title: 요구사항·인터페이스 구분 퀴즈
    estimated_minutes: 15
  - id: m10-system-architecture-requirements-exercise
    kind: exercise
    title: 내 캡스톤의 요구사항 추적표와 노드 그래프 작성
    estimated_minutes: 60
resources:
  - title: "현직자가 알려주는 로봇 실무 개발 프로세스: 로봇 양산 사이클 (인프런, jelly)"
    url: https://www.inflearn.com/course/robot-development-pr
    kind: course
    note: 17강 45분(기획→설계→Proto→Pilot→양산, Unitree Go2 예시), 18,700원(한국어).
  - title: Robotics Learning Roadmap 2026 (Coursera)
    url: https://www.coursera.org/resources/robotics-learning-roadmap
    kind: article
    note: Stage 2 프로젝트별 시간 추정(라인 팔로워 4–6h ~ 음성 어시스턴트 14–18h). 범위 산정 참고.
  - title: Nav2 Documentation
    url: https://docs.nav2.org/rolling/index.html
    kind: article
    note: First-Time Robot Setup Guide(TF→URDF→오도메트리→센서→지도) 순서가 그대로 인터페이스 체크리스트가 된다.
  - title: Andino (Ekumen-OS)
    url: https://github.com/Ekumen-OS/andino
    kind: other
    note: 하드웨어·펌웨어·ros2_control·SLAM·Nav2 패키지 분할을 실제 아키텍처 예시로 읽는다.
---

# 로봇 소프트웨어 아키텍처와 시스템 설계

M1–M8 에서 우리는 부품을 하나씩 만들었다. 운동학, PID, 센서 모델, 칼만 필터, SLAM, 경로 계획,
ROS 2 노드. 그런데 부품을 모아 놓는다고 로봇이 되지는 않는다. 실제 프로젝트가 실패하는 지점은
대개 알고리즘이 아니라 **경계**다. 좌표계가 맞지 않거나, 주기가 어긋나거나, 아무도 책임지지 않는
요구사항이 남는다. 이 레슨은 캡스톤을 시작하기 전에 "무엇을, 어떤 부품으로, 어떤 약속(인터페이스)으로"
만들지 종이 위에서 먼저 정하는 방법을 다룬다.

## 개념

### 요구사항: 검증할 수 있어야 요구사항이다

"똑똑하게 집 안을 돌아다니는 로봇"은 요구사항이 아니라 소망이다. 요구사항은 **합격/불합격을 판정할
수 있는 문장**이어야 한다.

- **기능 요구사항(FR):** "로봇은 사전에 만든 지도에서 지정한 목표점까지 자율 주행한다."
- **비기능 요구사항(NFR):** "목표점 도착 오차 0.15 m 이하, 10회 중 8회 이상 성공", "최대 속도 0.3 m/s",
  "명령이 0.5 s 이상 끊기면 정지", "총 부품비 60만 원 이하", "새 PC 에서 30분 안에 빌드".

NFR 이 곧 다음 레슨들의 입력이다. 속도·오차는 하드웨어 선정(L10.2)을, 정지 조건은 안전 설계(L10.3)를,
빌드 시간은 CI·컨테이너(L10.4)를 결정한다.

### 컴포넌트: 책임 하나에 컴포넌트 하나

요구사항을 M8 의 스택 지도 위에 배치한다. 하드웨어 계층(모터 드라이버, LiDAR 드라이버) → 제어
(ros2_control 의 diff_drive_controller, M3) → 추정(오도메트리·EKF·SLAM, M5) → 계획(Nav2 전역·지역
플래너, M6) → 임무(행동 트리, M6) 순이다. 좋은 분해의 기준은 단순하다. **각 요구사항은 정확히 하나의
컴포넌트가 책임지고, 각 컴포넌트는 적어도 하나의 요구사항을 이유로 존재한다.**

### 인터페이스: 컴포넌트 사이의 계약

ROS 2 에서 인터페이스는 메시지 타입만이 아니다. 계약서에는 다음이 모두 들어가야 한다.

- 이름과 통신 방식(토픽·서비스·액션), 메시지 타입
- 주기(Hz)와 허용 지연, QoS(신뢰성·이력 깊이)
- 좌표계(`frame_id`)와 단위(REP 103: m, rad, 오른손 좌표계)
- 실패 시 동작(메시지가 끊기면 수신 측은 무엇을 하는가)

Andino 저장소처럼 description·bringup·base·control·slam·navigation 패키지가 나뉘어 있으면, 패키지 경계가
곧 인터페이스 경계다.

### 개발 프로세스 안에서의 캡스톤

산업 현장의 사이클은 기획 → 설계 → 시제품(Proto) → 파일럿(Pilot) → 양산이다. 개인 캡스톤은 보통
**기획·설계·Proto** 까지이고, 문서화와 재현성을 잘 갖추면 Pilot 의 맛(여러 번 반복 시험)까지 볼 수 있다.
범위를 이 단계에 맞추는 것이 첫 번째 설계 결정이다.

## 핵심 체크리스트

- [ ] 모든 요구사항에 ID(FR-1, NFR-3 …)와 측정 방법이 있다.
- [ ] 모든 요구사항이 정확히 하나의 컴포넌트에 할당되어 있다.
- [ ] 모든 토픽에 발행자와 구독자가 각각 하나 이상 있다(끊긴 선 없음).
- [ ] 모든 인터페이스에 주기·frame_id·끊김 시 동작이 적혀 있다.
- [ ] tf 트리(map → odom → base_link → 센서)가 한 그림으로 그려져 있다.
- [ ] "하지 않을 것(out of scope)" 목록이 있다.

## 예제

요구사항 추적표와 인터페이스 표를 데이터로 적어 두면, 설계 리뷰를 코드로 자동화할 수 있다.

```python
from dataclasses import dataclass, field


@dataclass
class Component:
    name: str
    satisfies: list[str]
    publishes: dict[str, float] = field(default_factory=dict)  # 토픽 -> Hz
    subscribes: dict[str, float] = field(default_factory=dict)  # 토픽 -> 필요한 최소 Hz


requirements = [
    "FR-1 자율주행",
    "FR-2 지도 작성",
    "NFR-1 0.5s 명령 끊김 시 정지",
    "NFR-2 오차 0.15m",
]
components = [
    Component("lidar_driver", [], publishes={"/scan": 10.0}),
    Component(
        "base_controller", ["NFR-1 0.5s 명령 끊김 시 정지"], {"/odom": 50.0}, {"/cmd_vel": 10.0}
    ),
    Component("slam_toolbox", ["FR-2 지도 작성"], {"/map": 1.0}, {"/scan": 5.0, "/odom": 20.0}),
    Component(
        "nav2", ["FR-1 자율주행"], {"/cmd_vel": 20.0}, {"/map": 0.5, "/scan": 5.0, "/odom": 20.0}
    ),
]

owners = {r: [c.name for c in components if r in c.satisfies] for r in requirements}
for req, who in owners.items():
    if len(who) != 1:
        print(f"[요구사항] {req}: 담당 컴포넌트 {who or '없음'}")
for c in components:
    if not c.satisfies:
        print(f"[컴포넌트] {c.name}: 존재 이유(요구사항) 없음 — 지원 컴포넌트라면 명시")

rates = {t: hz for c in components for t, hz in c.publishes.items()}
for c in components:
    for topic, need in c.subscribes.items():
        have = rates.get(topic)
        if have is None:
            print(f"[인터페이스] {c.name} 이 구독하는 {topic} 의 발행자 없음")
        elif have < need:
            print(f"[인터페이스] {topic}: {have} Hz 발행 < {c.name} 요구 {need} Hz")
```

실행하면 "NFR-2 오차 0.15m" 에 담당이 없고 `lidar_driver` 가 요구사항 없이 존재한다는 두 줄이 나온다.
NFR-2 는 측정 절차(평가 스크립트)를 담당 컴포넌트로 추가하고, 드라이버는 FR-2 를 지원한다고 적으면 된다.

**연습 과제(exercise):** 자신의 캡스톤 후보 하나에 대해 FR 3개·NFR 4개 이상을 쓰고, 위 형식으로
컴포넌트·인터페이스 표를 만들어 검사기를 통과시켜라. 노드 그래프 그림(손그림도 좋다)과 tf 트리를 함께 제출한다.

## 자가 점검 질문

1. "로봇이 빠르게 움직인다"를 검증 가능한 NFR 로 바꾸면 어떤 수치와 측정 방법이 필요한가?
2. 한 요구사항을 두 컴포넌트가 나눠 책임지면 통합 시험에서 어떤 문제가 생기는가?
3. `/cmd_vel` 인터페이스 계약에 "끊김 시 동작"이 빠져 있으면 어떤 사고가 날 수 있는가?

## 이 단계 공부법

1. **강의(먼저):** 인프런 "로봇 실무 개발 프로세스"(45분)로 기획→양산 흐름과 단계별 산출물을 본다.
2. **코드 읽기:** Andino 저장소의 패키지 목록을 M8 레슨의 스택 지도에 다시 배치하고, 각 패키지가 어떤 요구사항을 위해 있는지 한 줄씩 적는다.
3. **문서 대조:** Nav2 First-Time Robot Setup Guide 의 순서를 내 인터페이스 표의 체크리스트로 쓴다.
4. **범위 산정:** Coursera 로드맵의 프로젝트 시간 추정을 참고해 내 요구사항 목록이 6주(주 8–10시간) 안에 들어오는지 줄인다.

## 참고 자료

- jelly, "현직자가 알려주는 로봇 실무 개발 프로세스: 로봇 양산 사이클", 인프런 — <https://www.inflearn.com/course/robot-development-pr>
- Coursera, "Robotics Learning Roadmap (2026)" — <https://www.coursera.org/resources/robotics-learning-roadmap>
- Nav2 Documentation — <https://docs.nav2.org/rolling/index.html>
- Ekumen, Andino — <https://github.com/Ekumen-OS/andino>
