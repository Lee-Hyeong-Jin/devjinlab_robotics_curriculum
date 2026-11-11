---
# 레슨 템플릿. 복사해서 curriculum/<track>/<module>/<lesson-id>.md 로 저장한다.
# 코드의 콘텐츠 스키마(P0-2 이후)가 있으면 그것이 우선이다. 필수 필드는 docs/PRD.md FR-1.2 를 따른다.
id: robotics-basics/m2-kinematics/forward-kinematics   # <track>/<module>/<lesson>, 파일 경로와 일치
title: 정기구학(Forward Kinematics)
prerequisites:                                         # 레슨 id 목록. 순환 금지.
  - robotics-basics/m2-kinematics/dh-parameters
estimated_minutes: 90
objectives:                                            # 관찰 가능한 동사로
  - DH 파라미터 표로부터 동차 변환 행렬을 구성할 수 있다
  - 2-link 평면 매니퓰레이터의 말단 위치를 계산할 수 있다
  - 정기구학 결과를 시뮬레이터에서 검증할 수 있다
tags: [kinematics, manipulator, webots]
activities:
  - type: reading
    id: read-1
    title: 동차 변환과 DH 체인
  - type: quiz
    id: quiz-1
    title: 핵심 개념 체크
  - type: lab
    id: lab-1
    title: Webots 2-link 매니퓰레이터 목표 자세 도달
    world: labs/m2/two_link.wbt                        # 저장소 상대 경로
    controller_template: labs/m2/two_link_controller_template.py
    judge: labs/m2/two_link_judge.py                   # 또는 YAML 선언형(열린 질문 3)
  - type: external
    id: ext-1
    title: 참고 강의
    url: https://example.org/lecture
---

# 정기구학(Forward Kinematics)

## 왜 배우나

한두 문단. 이 레슨이 트랙 안에서 어디에 놓이고, 다음 레슨(역기구학)에 어떻게 이어지는지.

## 핵심 개념

### 동차 변환

$$
T = \begin{bmatrix} R & p \\ 0 & 1 \end{bmatrix}
$$

### DH 체인

```python
import numpy as np


def dh(a: float, alpha: float, d: float, theta: float) -> np.ndarray:
    """표준 DH 파라미터 하나를 동차 변환 행렬로 바꾼다."""
    ...
```

## 퀴즈 {#quiz-1}

<!-- 퀴즈 형식은 P1-2 에서 확정. 초안: -->

1. [객관식] 동차 변환 행렬의 크기는?
   - a) 2x2  b) 3x3  c) 4x4  d) 6x6
   - 정답: c
   - 해설: 회전 3x3 + 이동 3x1 + 동차 행.

2. [O/X] DH 파라미터는 링크당 4개다.
   - 정답: O

## 실습 {#lab-1}

- 월드: `labs/m2/two_link.wbt`
- 템플릿: `labs/m2/two_link_controller_template.py` 의 `# TODO` 를 채운다.
- 판정: 말단이 목표점 반경 1cm 안에 10초 내 도달.
- 실행: `rc lab open robotics-basics/m2-kinematics/forward-kinematics` (P1-4 에서 구현)

## 더 읽기

- research_notes/... (조사 노트 경로)
- external 활동의 URL
