---
id: m10-testing-ci-deployment
title: "테스트·CI·배포(단위/통합/HIL, 컨테이너, 로깅·관측)"
summary: 로봇 소프트웨어를 단위 테스트·통합 테스트·기록 데이터 재생 테스트·HIL(Hardware-in-the-Loop) 테스트의 피라미드로 검증하고, Docker 컨테이너로 개발·배포 환경을 고정하며, rosbag2(MCAP)·로그·지표로 실행 중인 로봇을 관측하는 방법을 익힌다.
objectives:
  - 알고리즘 코드를 ROS 의존성 없는 순수 함수로 분리해 pytest 단위 테스트를 작성할 수 있다.
  - 기록된 센서 로그를 재생해 결과 지표를 기준값과 비교하는 회귀 테스트를 설계할 수 있다.
  - 단위·통합·HIL 테스트가 각각 잡는 결함의 종류와 비용을 비교하고, CI 에서 무엇을 자동화할지 정할 수 있다.
  - Docker 이미지·rosbag2·구조화 로그로 "내 컴퓨터에서는 되는데" 문제를 줄이는 배포·관측 절차를 세울 수 있다.
prerequisites: [m10-system-architecture-requirements, m8-stacks-dev-environment, m5-odometry-sensor-fusion]
difficulty: 4
estimated_minutes: 120
tags: [testing, pytest, ci, hil, docker, rosbag2, mcap, logging, observability]
activities:
  - id: m10-testing-ci-deployment-reading
    kind: reading
    title: 본문과 Docker·Foxglove 문서
    estimated_minutes: 40
  - id: m10-testing-ci-deployment-quiz
    kind: quiz
    title: 테스트 피라미드와 결함 유형 퀴즈
    estimated_minutes: 15
  - id: m10-testing-ci-deployment-exercise
    kind: exercise
    title: 로그 재생 회귀 테스트와 CI 파이프라인 작성
    estimated_minutes: 65
resources:
  - title: Introduction to ROS 2 Development with Docker (Docker 공식 가이드)
    url: https://docs.docker.com/guides/ros2/
    kind: article
    note: Compose 개발 컨테이너 + Turtlesim 예제. ros:humble 이미지를 ros:jazzy 로 바꿔 쓴다.
  - title: 2b-t/docker-for-robotics (best-practices guide)
    url: https://awesome.ecosyste.ms/projects/github.com%2F2b-t%2Fdocker-for-robotics
    kind: other
    note: 로보틱스용 Docker 모범 사례(GUI, Linux·WSL2). URL 은 ecosyste.ms 목록 페이지.
  - title: "Foxglove docs: connecting to ROS 2 data"
    url: https://docs.foxglove.dev/docs/connecting-to-data/frameworks/ros2
    kind: article
    note: Foxglove Bridge 실시간 관측, .mcap 재생. Iron 이후 ros2 bag 기본 형식이 MCAP.
  - title: Automatic Addison ROS 2 Tutorials
    url: https://automaticaddison.com/tutorials
    kind: article
    note: Jazzy 기준 pytest/GTest, bag 기록·재생, ros2 doctor 글.
---

# 테스트·CI·배포

로봇 버그는 비싸다. 책상 위에서 5분이면 찾을 오류를 로봇 위에서 찾으면 배터리 교체·재부팅·현장 이동까지
한 시간이 든다. 이 레슨의 목표는 **가능한 한 많은 결함을 로봇에 올리기 전에** 잡는 구조를 만드는 것이다.
M8 에서 만든 개발 환경을 이제 "재현 가능한 환경"으로 굳힌다.

## 개념

### 테스트 피라미드

| 층 | 대상 | 도구 | 속도 | 잡는 결함 |
|---|---|---|---|---|
| 단위 | 순수 함수(운동학, 필터 한 스텝, 비용 함수) | pytest, GTest | ms | 수식·부호·단위 실수 |
| 통합 | 노드 여러 개 + 토픽 | launch_testing, `ros2 topic` | 초 | 토픽 이름·QoS·frame_id 불일치 |
| 로그 재생 | 기록된 센서 데이터 → 알고리즘 | rosbag2(MCAP) 재생 | 분 | 실제 노이즈에서의 성능 회귀 |
| HIL | 실제 MCU·모터·센서 + 가짜 환경 | 테스트 지그, 받침대 위 로봇 | 분~시간 | 펌웨어 타이밍, 전원, 배선 |

아래로 갈수록 싸고 빠르니 많이, 위로 갈수록 비싸니 적게 둔다. 핵심 습관은 **알고리즘을 ROS 에서 떼어 내는
것**이다. 노드 콜백은 메시지를 풀어 순수 함수에 넘기고 결과를 다시 메시지로 싸는 얇은 껍질로만 둔다.
그러면 M3–M6 에서 짠 numpy 코드가 그대로 단위 테스트 대상이 된다.

**HIL(Hardware-in-the-Loop)** 은 실제 하드웨어 일부를 루프에 넣고 나머지를 흉내 내는 시험이다. 시뮬레이터가
없어도 된다. 로봇을 받침대에 올려 바퀴를 공중에 띄우고 `/cmd_vel` 계단 입력을 주며 인코더 응답과 워치독
동작(L10.3)을 기록하는 것이 가장 간단한 HIL 이다.

### CI: 사람이 잊어버리는 검사를 기계에 맡긴다

커밋마다 (1) 린트·포맷, (2) 빌드(`colcon build`), (3) 단위·통합 테스트(`colcon test`), (4) 짧은 로그 재생
회귀 테스트를 돌린다. CI 도 같은 Docker 이미지 안에서 돌려야 개발자 PC 와 결과가 같다.

### 배포와 관측

- **컨테이너:** 배포판(Jazzy)·의존성을 이미지로 고정한다. 로봇에는 `--network host` 와 장치 전달
  (`--device /dev/ttyUSB0`)이 필요하다.
- **기록:** 시험마다 `ros2 bag record` 로 MCAP 을 남기고, 파일 이름에 날짜·커밋 해시·시나리오를 넣는다.
- **관측:** RViz 를 먼저 쓰고, 원격·사후 분석에는 Foxglove 로 MCAP 을 연다. 로그는 `RCLCPP_INFO` 류의
  자유 문장보다 "key=value" 형태로 남겨야 나중에 검색·집계할 수 있다.

## 핵심 체크리스트

- [ ] 알고리즘 코드가 rclpy 를 import 하지 않는 모듈에 있다.
- [ ] 단위 테스트가 경계값(0, 음수, 큰 각도, 빈 입력)을 다룬다.
- [ ] 기준 MCAP 1개 이상과 그 결과 지표 기준값이 저장소에 있다(또는 내려받을 수 있다).
- [ ] CI 가 개발과 같은 Docker 이미지에서 돈다.
- [ ] 모든 시험 기록에 커밋 해시가 붙어 있다.

## 예제

차동 구동 오도메트리 한 스텝(M3, M5)을 순수 함수로 두고, 단위 테스트와 "로그 재생" 회귀 테스트를 만든다.
로그는 여기서는 합성하지만, 실제로는 MCAP 에서 뽑은 (dt, v, ω) 배열을 쓴다.

```python
import numpy as np


def odom_step(pose, v, w, dt):
    x, y, th = pose
    return np.array(
        [
            x + v * np.cos(th) * dt,
            y + v * np.sin(th) * dt,
            (th + w * dt + np.pi) % (2 * np.pi) - np.pi,
        ]
    )


def test_straight_line():
    assert np.allclose(odom_step(np.zeros(3), 1.0, 0.0, 0.5), [0.5, 0.0, 0.0])


def test_angle_wraps():
    assert -np.pi <= odom_step(np.array([0, 0, 3.1]), 0.0, 1.0, 0.1)[2] < np.pi


def test_replay_regression(baseline_end_error=0.05):
    # 반지름 1 m 원을 한 바퀴: 끝점은 시작점으로 돌아와야 한다
    dt, n = 0.02, 314
    log = [(dt, 1.0, 1.0)] * n  # (dt, v, w)
    pose = np.zeros(3)
    for d, v, w in log:
        pose = odom_step(pose, v, w, d)
    err = float(np.hypot(pose[0], pose[1]))
    print(f"replay end_error_m={err:.4f} baseline={baseline_end_error}")
    assert err < baseline_end_error


for test in (test_straight_line, test_angle_wraps, test_replay_regression):
    test()
    print("PASS", test.__name__)
```

pytest 는 `test_` 함수를 자동으로 찾으므로 마지막 루프는 빼고 `tests/test_odom.py` 로 두면 된다. 실제 로그를
쓸 때는 기준값을 "현재 결과 + 여유"로 정하고, 알고리즘을 바꿀 때마다 이 수치가 나빠지지 않았는지 본다.

CI 와 로봇에서 같은 이미지로 빌드·테스트하는 명령의 골격은 다음과 같다.

```bash
docker build -t capstone:jazzy .
docker run --rm capstone:jazzy bash -c "colcon build && colcon test && colcon test-result --verbose"
docker run --rm -it --network host --device /dev/ttyUSB0 capstone:jazzy ros2 launch capstone_bringup robot.launch.py
ros2 bag record -s mcap -o "$(date +%F)_$(git rev-parse --short HEAD)_square" /odom /scan /cmd_vel /tf
```

**연습 과제(exercise):** (1) 자신의 로봇에서 1–2분짜리 MCAP 을 기록하고, 그 데이터로 오도메트리 또는 EKF
결과 지표를 계산하는 회귀 테스트를 만들어라. (2) GitHub Actions 등에서 Docker 이미지로 lint → build → test 를
돌리는 워크플로를 작성하라. (3) 받침대 HIL 시험 절차서를 한 쪽으로 써라.

## 자가 점검 질문

1. 토픽 이름 오타는 피라미드의 어느 층에서 처음 잡히는가? 단위 테스트로는 왜 못 잡는가?
2. 로그 재생 회귀 테스트의 기준값을 "정답"이 아니라 "현재 결과 + 여유"로 두는 이유는?
3. Docker 이미지 없이 로봇에 직접 `apt install` 로 배포했을 때 6개월 뒤 생길 수 있는 문제는?

## 이 단계 공부법

1. **문서(먼저):** Docker 공식 ROS 2 가이드를 Jazzy 이미지로 바꿔 따라 하고, 내 캡스톤 저장소에 Dockerfile 을 만든다.
2. **본문 + 예제:** 예제를 pytest 로 옮겨 실행하고, `odom_step` 에 일부러 부호 오류를 넣어 어느 테스트가 실패하는지 본다.
3. **관측:** Foxglove 문서대로 내가 기록한 MCAP 을 열어 `/odom` 과 `/scan` 을 나란히 본다.
4. **보강(선택):** Automatic Addison 의 pytest·bag·ros2 doctor 글, docker-for-robotics 의 GUI·WSL2 절을 읽는다.

## 참고 자료

- Docker, "Introduction to ROS 2 Development with Docker" — <https://docs.docker.com/guides/ros2/>
- 2b-t, docker-for-robotics — <https://awesome.ecosyste.ms/projects/github.com%2F2b-t%2Fdocker-for-robotics>
- Foxglove, "Connecting to ROS 2 data" — <https://docs.foxglove.dev/docs/connecting-to-data/frameworks/ros2>
- Automatic Addison, ROS 2 Tutorials — <https://automaticaddison.com/tutorials>
