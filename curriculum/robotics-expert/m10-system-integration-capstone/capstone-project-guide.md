---
id: m10-capstone-project-guide
title: "캡스톤 프로젝트 설계 가이드(주제 선택, 마일스톤, 평가 기준)"
summary: 6주 캡스톤의 주제를 고르는 기준, 주차별 마일스톤, 점수 배분이 있는 평가 루브릭을 제시하고, 시뮬레이터 없이 저가 실하드웨어나 기록 데이터로 수행할 수 있는 예시 프로젝트 브리프 3개를 제공한다.
objectives:
  - 관심·예산·위험도 기준으로 캡스톤 주제를 고르고, L10.1 형식의 요구사항으로 범위를 고정할 수 있다.
  - 6주 마일스톤과 주차별 산출물을 정하고, 위험이 큰 통합 작업을 앞쪽에 배치할 수 있다.
  - 평가 루브릭으로 자기 프로젝트를 채점하고, 점수가 낮은 항목을 다음 반복의 작업으로 바꿀 수 있다.
prerequisites: [m10-hardware-selection-integration, m10-realtime-safety-reliability, m10-testing-ci-deployment, m6-nav2-architecture-behavior-trees]
difficulty: 5
estimated_minutes: 180
tags: [capstone, project, rubric, milestones, andino, so-101, dataset]
activities:
  - id: m10-capstone-project-guide-reading
    kind: reading
    title: 본문과 예시 브리프 읽기
    estimated_minutes: 40
  - id: m10-capstone-project-guide-quiz
    kind: quiz
    title: 범위·위험 판단 퀴즈
    estimated_minutes: 20
  - id: m10-capstone-project-guide-exercise
    kind: exercise
    title: 내 캡스톤 기획서(브리프·마일스톤·자기 채점) 작성
    estimated_minutes: 120
resources:
  - title: Andino (Ekumen-OS)
    url: https://github.com/Ekumen-OS/andino
    kind: other
    note: 하드웨어 조립(andino_hardware·firmware) → ros2_control → SLAM → Nav2 전체 스택. 브리프 A 의 기준 설계.
  - title: TurtleBot 4 User Manual Tutorials
    url: https://turtlebot.github.io/turtlebot4-user-manual/tutorials/
    kind: article
    note: Generating a map·Navigation·Navigator 튜토리얼(Jazzy). 브리프 A 의 단계 참고.
  - title: LeRobot SO-101 docs
    url: https://huggingface.co/docs/lerobot/so101
    kind: article
    note: 텔레옵·데이터 기록·정책 학습·평가 전 과정. 브리프 B 의 기준 절차.
  - title: Train an ACT Policy for an SO-101 Robot (Trelis)
    url: https://trelis.substack.com/p/train-an-act-policy-for-an-so-101
    kind: article
    note: ACT 학습 실전 기록. 에피소드 수·실패 사례 참고.
  - title: Open X-Embodiment
    url: https://robotics-transformer-x.github.io/
    kind: article
    note: 1M+ 궤적·22 임바디먼트·RLDS. 브리프 C 의 데이터셋 변형(매니퓰레이션 데이터 분석)용.
---

# 캡스톤 프로젝트 설계 가이드

캡스톤은 이 코스의 졸업 작품이다. 목표는 "가장 어려운 것"이 아니라 **끝까지 동작하고, 남이 재현할 수
있고, 왜 그렇게 설계했는지 설명할 수 있는 것**이다. 이 플랫폼은 시뮬레이터 실습을 전제하지 않으므로,
여기 제시하는 프로젝트는 모두 저가 실하드웨어나 기록 데이터로 수행한다.

## 개념

### 주제 고르기: 세 개의 질문

1. **관심:** 6주 동안 매주 8–10시간을 쓸 만큼 궁금한가?
2. **예산:** L10.2 의 BOM 이 감당 가능한가? 하드웨어가 없다면 데이터셋 프로젝트(브리프 C)를 고른다.
3. **위험:** 처음 써 보는 부품·알고리즘이 두 개를 넘지 않는가? 새로운 것이 셋 이상이면 범위를 줄인다.

### 마일스톤: 통합을 앞으로 당긴다

| 주 | 마일스톤 | 산출물 |
|---|---|---|
| 1 | 요구사항·아키텍처 고정 | 요구사항 추적표, 노드 그래프, BOM(L10.1–10.2) |
| 2 | "걷는 뼈대": 입력→출력이 끝까지 한 번 흐름 | 최소 데모 영상, Dockerfile |
| 3 | 핵심 기능 1차 | 첫 정량 지표, 기준 로그 1개 |
| 4 | 안전·테스트 | 워치독·FMEA(L10.3), CI 녹색(L10.4) |
| 5 | 반복 시험·튜닝 | 10회 이상 시험 결과표 |
| 6 | 문서·발표 | README, 결과 보고서, 3분 영상(L10.6) |

2주 차의 "걷는 뼈대"가 가장 중요하다. 품질이 낮아도 센서에서 액추에이터까지(또는 데이터에서 지표까지)
한 번 이어 두면 이후의 위험은 모두 "개선"이 된다.

## 핵심 체크리스트

### 평가 루브릭(100점)

| 항목 | 배점 | 우수(만점) | 보통(절반) | 미흡(0) |
|---|---|---|---|---|
| 요구사항·설계 | 15 | 측정 가능한 FR/NFR, 추적표, 인터페이스 표 완비 | 요구사항은 있으나 일부 측정 불가 | 문서 없음 |
| 통합·기능 | 25 | 모든 FR 을 실제 하드웨어/데이터로 시연 | 핵심 FR 일부만 시연 | 단일 부품 데모 |
| 정량 평가 | 15 | 10회 이상 반복, 평균·분산·실패 원인 분석 | 1–3회 결과만 제시 | 지표 없음 |
| 안전·신뢰성 | 15 | 워치독·E-stop·FMEA, 고장 주입 시험 | 워치독만 있음 | 안전 설계 없음 |
| 재현성·엔지니어링 | 15 | Docker·CI·기준 로그, 새 PC 에서 30분 내 재현 | 설치 문서만 있음 | 재현 불가 |
| 문서·발표 | 15 | README·보고서·영상, 한계와 다음 단계 명시 | README 만 있음 | 없음 |

## 예제

### 예시 프로젝트 브리프

**A. 저가 차동 구동 로봇의 지도 작성·자율 주행 (실하드웨어, 부품비 약 $250–450 추정)**
Andino 설계를 기준으로 Raspberry Pi + LD19 급 2D LiDAR + ESP32 모터 제어기로 로봇을 조립하고,
ros2_control 차동 구동 → SLAM Toolbox 지도 → Nav2 주행까지 통합한다. 평가: 거실 지도에서 목표점 5곳,
10회 왕복의 도착 오차와 성공률. 안전: `/cmd_vel` 워치독과 모터 전원 E-stop.

**B. SO-101 모방학습 픽앤플레이스 (실하드웨어, BOM 약 $230 + 3D 프린팅)**
SO-101 리더·팔로워 팔로 텔레옵 시연 50에피소드를 LeRobot 으로 기록하고 ACT 정책을 학습해 정해진 물체를
상자로 옮긴다. 평가: 물체 위치를 바꾼 20회 시도의 성공률, 학습 에피소드 수에 따른 성공률 곡선.
안전: 관절 속도·토크 제한, 작업 영역 밖 명령 거부. 학습은 클라우드 GPU 로 해도 된다(M9 참고).

**C. 기록 데이터 기반 상태 추정 벤치마크 (하드웨어 선택, 비용 0원 가능)**
직접 기록했거나 빌린 로봇의 MCAP(바퀴 오도메트리·IMU·LiDAR)으로 순수 오도메트리, EKF 융합(M5),
스캔 매칭 보정의 궤적 오차를 비교하는 재현 가능한 파이프라인을 만든다. 평가: 동일 출발·도착 지점의
폐루프 오차, 알고리즘별 CPU 시간. 재현성: Docker + CI 에서 데이터 내려받기→지표 표 생성까지 자동.
변형: Open X-Embodiment 의 일부 서브셋으로 매니퓰레이션 데이터 품질(에피소드 길이·행동 분포) 분석.

### 자기 채점 스크립트

```python
rubric = {
    "요구사항·설계": 15,
    "통합·기능": 25,
    "정량 평가": 15,
    "안전·신뢰성": 15,
    "재현성·엔지니어링": 15,
    "문서·발표": 15,
}
levels = {"우수": 1.0, "보통": 0.5, "미흡": 0.0}
self_eval = {
    "요구사항·설계": "우수",
    "통합·기능": "보통",
    "정량 평가": "보통",
    "안전·신뢰성": "우수",
    "재현성·엔지니어링": "미흡",
    "문서·발표": "보통",
}

assert sum(rubric.values()) == 100
score = sum(w * levels[self_eval[k]] for k, w in rubric.items())
print(f"총점 {score:.0f}/100")
for k, w in sorted(rubric.items(), key=lambda kv: kv[1] * levels[self_eval[kv[0]]] - kv[1]):
    lost = w * (1 - levels[self_eval[k]])
    if lost:
        print(f"다음 반복 우선순위: {k} (잃은 점수 {lost:.1f})")
```

**연습 과제(exercise):** 브리프 A·B·C 중 하나를 고르거나 직접 만들어 한 쪽짜리 기획서(목표, FR/NFR, BOM,
6주 마일스톤, 위험 3개와 대응)를 쓰고, 2주 차와 6주 차에 루브릭으로 자기 채점한다.

## 자가 점검 질문

1. "걷는 뼈대"를 2주 차에 만들지 않고 5주 차에 처음 통합하면 어떤 위험이 생기는가?
2. 브리프 B 에서 성공률을 3회 시도로만 보고하면 루브릭의 어느 항목에서 감점되며, 왜 부족한가?
3. 하드웨어가 없는 학습자가 브리프 C 로도 "통합·기능" 만점을 받으려면 무엇을 시연해야 하는가?

## 이 단계 공부법

1. **브리프 비교(먼저):** 세 브리프를 L10.2 의 예산·전력 기준과 내 일정에 대 보고 하나를 고른다.
2. **기준 절차 읽기:** A 는 Andino README 와 TurtleBot 4 튜토리얼, B 는 LeRobot SO-101 문서와 Trelis 기록, C 는 M5 레슨과 내 MCAP 을 기준으로 단계 목록을 만든다.
3. **기획서 작성:** 루브릭의 "우수" 칸을 그대로 완료 조건으로 옮겨 적는다.
4. **주간 점검:** 매주 끝에 자기 채점 스크립트를 돌리고 잃은 점수가 큰 항목부터 다음 주 작업으로 삼는다.

## 참고 자료

- Ekumen, Andino — <https://github.com/Ekumen-OS/andino>
- Clearpath Robotics, TurtleBot 4 User Manual — Tutorials — <https://turtlebot.github.io/turtlebot4-user-manual/tutorials/>
- Hugging Face, LeRobot SO-101 — <https://huggingface.co/docs/lerobot/so101>
- Trelis, "Train an ACT Policy for an SO-101 Robot" — <https://trelis.substack.com/p/train-an-act-policy-for-an-so-101>
- Open X-Embodiment Collaboration, Open X-Embodiment — <https://robotics-transformer-x.github.io/>
