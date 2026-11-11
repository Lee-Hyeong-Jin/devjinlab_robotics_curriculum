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
  - 계산 결과를 수치 예제로 검산할 수 있다
tags: [kinematics, manipulator]
activities:
  - type: reading
    id: read-1
    title: 동차 변환과 DH 체인
  - type: quiz
    id: quiz-1
    title: 핵심 개념 체크
  - type: project
    id: proj-1
    title: 2-link 매니퓰레이터 정기구학 계산 스크립트
  - type: external
    id: ext-1
    title: 참고 강의
    url: https://example.org/lecture
resources:                                             # FR-6: 레슨별 추천 자료
  - type: book
    title: Modern Robotics (Lynch & Park) 4장
    url: https://example.org/modern-robotics
    note: 정기구학의 PoE 표현과 DH 비교
  - type: video
    title: 참고 강의 영상
    url: https://example.org/lecture
---

# 정기구학(Forward Kinematics)

## 왜 배우나

한두 문단. 이 레슨이 트랙 안에서 어디에 놓이고, 다음 레슨(역기구학)에 어떻게 이어지는지.

## 단계별 공부법

1. **읽기(20분)**: 아래 핵심 개념을 읽고 동차 변환 행렬을 손으로 한 번 써 본다.
2. **확인(10분)**: 퀴즈로 개념을 점검한다. 틀린 문항은 플래시카드가 된다.
3. **적용(50분)**: 프로젝트 활동에서 2-link 정기구학을 코드로 구현하고 수치 예제로 검산한다.
4. **정리(10분)**: 이해도(1~5)와 메모를 남기고, 막힌 부분은 추천 자료에서 찾아본다.

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

## 프로젝트 {#proj-1}

- 과제: 링크 길이 (1.0, 0.5), 관절각 (30°, 45°) 인 2-link 평면 매니퓰레이터의 말단 위치를 계산하는 스크립트를 작성한다.
- 검산: 손 계산 결과와 1e-6 이내로 일치하는지 확인한다.
- 제출: 스크립트와 결과를 레슨 메모에 남긴다.

## 추천 자료 {#resources}

frontmatter 의 `resources` 가 원본이다. 여기에는 자료별로 "왜 이 자료인가" 한 줄을 적는다.

- Modern Robotics 4장: PoE 와 DH 를 함께 보면 표현 차이가 명확해진다.
- research_notes/... (조사 노트 경로)
