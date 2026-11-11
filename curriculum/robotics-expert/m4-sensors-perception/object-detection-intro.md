---
id: m4-object-detection-intro
title: 딥러닝 기반 객체 인식 입문
summary: CNN 검출기가 무엇을 입력받아 무엇을 출력하는지, 그 출력을 IoU·NMS·정밀도/재현율로 후처리·평가하는 법, 그리고 2D 검출을 깊이와 카메라 모델로 3D 위치로 바꾸는 법을 익힌다.
objectives:
  - 합성곱 신경망 기반 객체 검출기의 입력·출력(상자, 클래스, 점수) 구조를 설명할 수 있다.
  - IoU 와 NMS 를 구현하고 정밀도·재현율로 검출 결과를 평가할 수 있다.
  - 2D 검출 상자와 깊이 값을 카메라 내부 파라미터로 역투영해 물체의 3D 위치를 구할 수 있다.
prerequisites: [m4-camera-model-features]
difficulty: 3
estimated_minutes: 90
tags: [deep-learning, object-detection, cnn, iou, nms, perception]
activities:
  - id: m4-object-detection-intro-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 30
  - id: m4-object-detection-intro-quiz
    kind: quiz
    title: IoU·NMS·정밀도/재현율 퀴즈
    estimated_minutes: 15
  - id: m4-object-detection-intro-exercise
    kind: exercise
    title: 검출 후처리와 3D 위치 추정 구현
    estimated_minutes: 45
resources:
  - title: "Robotic Manipulation (Russ Tedrake)"
    url: https://manipulation.mit.edu/
    kind: book
    note: Ch. 9 Object Detection and Segmentation, Ch. 10 Deep Perception. 로봇 관점의 인식. 먼저 읽는다.
  - title: "First Principles of Computer Vision (Shree Nayar)"
    url: https://fpcv.cs.columbia.edu/
    kind: video
    note: 신경망 이전의 인식 기초를 보강할 때(선택).
  - title: "Physical AI 입문 All-In-One (패스트캠퍼스)"
    url: https://fastcampus.co.kr/data_online_physicalai
    kind: course
    note: Part 2 인지(YOLO·OpenCV). 2026-12 순차 공개, 유료 303,000원~ (한국어, 선택).
---

# 딥러닝 기반 객체 인식 입문

앞 레슨들의 코너·평면 검출은 사람이 규칙을 설계했다. "컵", "문손잡이"처럼 의미가 있는 물체는
규칙으로 정의하기 어려워, 오늘날 로봇은 라벨 이미지로 학습한 **합성곱 신경망(CNN)** 검출기를
쓴다. 이 레슨은 신경망을 학습시키지 않고, 검출기를 **부품으로 쓰는 법**(출력 형태, 후처리·평가,
3D 위치로의 변환)을 익힌다. 모델 학습은 고급 단계에서 다룬다.

## 개념

### CNN 검출기의 입력과 출력

입력은 이미지 텐서(높이×너비×3)다. 합성곱 층은 앞 레슨의 Sobel 필터 같은 작은 커널을 이미지
전체에 미끄러뜨리는 연산인데, 커널 값을 사람이 정하지 않고 데이터로 학습한다. 층이 깊어질수록
에지 → 모서리·질감 → 부품 → 물체 순으로 추상적인 특징 맵이 만들어진다.

검출기(YOLO 계열 등)의 출력은 후보 상자 수백~수천 개이며, 각 후보는 **상자** $[x_1, y_1, x_2, y_2]$,
**클래스**, **신뢰도 점수**를 가진다. 같은 물체에 상자가 여러 개 겹쳐 나오므로 후처리가 필요하다.
분할(segmentation) 모델은 상자 대신 픽셀 단위 마스크를 내놓는다.

### 후처리: IoU 와 NMS

- **IoU(Intersection over Union):** 두 상자의 교집합 넓이 / 합집합 넓이. 0~1.
- **NMS(Non-Maximum Suppression):** 점수가 가장 높은 상자를 남기고, 그와 IoU 가 임계값
  (보통 0.5) 이상인 상자를 지운다. 남은 상자에 대해 반복한다.
- **점수 임계값:** 낮은 점수 상자를 버린다. 낮추면 놓치는 물체가 줄고 오검출이 는다.

### 평가: 정밀도와 재현율

정답 상자와 IoU ≥ 0.5 로 짝지어지면 참 양성(TP), 아니면 거짓 양성(FP), 짝이 없는 정답은
거짓 음성(FN)이다. 점수 임계값을 바꾸며 그린 정밀도–재현율 곡선의 넓이가 AP, 클래스 평균이
mAP 다. 로봇에서는 놓치면 충돌(재현율 중요), 잘못 잡으면 엉뚱한 물체 파지(정밀도 중요)처럼
용도에 따라 기준이 달라진다.

### 2D 검출에서 3D 위치로

검출 상자는 픽셀 좌표일 뿐이다. 로봇 팔이 컵을 잡으려면 미터 단위 3D 위치가 필요하다. 깊이
카메라의 상자 중심 깊이 $Z$ 와 내부 파라미터 $K$ 로 역투영하면 카메라 좌표의 3D 점이 되고,
M1 의 변환으로 로봇 좌표계로 옮긴다. 반사·투명 물체는 깊이 값이 비어 있을 수 있으므로 상자 안
깊이의 중앙값을 쓰는 것이 안전하다(M4 첫 레슨의 이상치 이야기와 같다).

## 핵심 수식

$$\mathrm{IoU}(A, B) = \frac{|A \cap B|}{|A| + |B| - |A \cap B|}$$

$$\text{정밀도} = \frac{TP}{TP + FP},\qquad \text{재현율} = \frac{TP}{TP + FN}$$

역투영(픽셀 $(u, v)$, 깊이 $Z$):

$$P_c = Z\,K^{-1}\begin{bmatrix} u \\ v \\ 1 \end{bmatrix}
= \begin{bmatrix} (u - c_x)\,Z/f_x \\ (v - c_y)\,Z/f_y \\ Z \end{bmatrix}$$

## 예제

가정한 검출기 출력으로 NMS, 평가, 3D 위치 추정을 한다. 실제로는 `boxes`, `scores` 에 모델 출력을 넣는다.

```python
import numpy as np


def area(r):
    return (r[2] - r[0]) * (r[3] - r[1])


def iou(a, b):  # 상자: [x1, y1, x2, y2]
    w = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    h = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = w * h
    return inter / (area(a) + area(b) - inter)


def nms(boxes, scores, thresh=0.5):
    order, keep = list(np.argsort(scores)[::-1]), []
    while order:
        i = order.pop(0)
        keep.append(int(i))
        order = [j for j in order if iou(boxes[i], boxes[j]) < thresh]
    return keep


# 검출기 출력(가정): 같은 컵을 여러 번 잡은 상자 + 다른 물체
boxes = np.array(
    [
        [100, 100, 200, 220],
        [105, 98, 205, 225],
        [95, 110, 190, 215],
        [300, 150, 380, 260],
        [500, 50, 540, 90],
    ],
    dtype=float,
)
scores = np.array([0.92, 0.85, 0.60, 0.88, 0.30])
keep = nms(boxes, scores)
print("NMS 후 남은 상자:", keep)

# 정답과 비교: IoU ≥ 0.5 이면 참 양성(TP)
gt = np.array([[102, 102, 202, 222], [310, 150, 385, 255]], dtype=float)
matched, tp = set(), 0
for i in keep:  # keep 은 점수 내림차순
    ious = [iou(boxes[i], g) for g in gt]
    j = int(np.argmax(ious))
    if ious[j] >= 0.5 and j not in matched:
        matched.add(j)
        tp += 1
print(f"정밀도 {tp / len(keep):.2f}, 재현율 {tp / len(gt):.2f}")

# 2D 상자 + 깊이 → 3D 위치 (핀홀 역투영)
K = np.array([[600.0, 0, 320], [0, 600.0, 240], [0, 0, 1]])
x1, y1, x2, y2 = boxes[keep[0]]
u, v, depth = (x1 + x2) / 2, (y1 + y2) / 2, 1.2  # 깊이 센서 값 [m]
P_c = depth * np.linalg.inv(K) @ np.array([u, v, 1.0])
print("컵 중심(카메라 좌표) [m]:", P_c.round(3))
```

NMS 는 컵 위의 겹친 상자 세 개 중 점수 0.92 하나만 남겨 `[0, 3, 4]` 를 낸다. 상자 4 는 정답이 없는
오검출이라 정밀도 0.67, 재현율 1.00 이다. 점수 임계값 0.5 를 먼저 적용하면 정밀도도 1.00 이 된다.
컵 중심은 카메라 기준 왼쪽 0.34 m, 위쪽 0.16 m, 앞 1.2 m 에 있다.

**연습 과제(exercise):** (1) 점수 임계값을 0~1 로 바꾸며 정밀도·재현율을 계산해 곡선을 그려라.
(2) NMS 임계값을 0.3 과 0.8 로 바꾸면 결과가 어떻게 달라지는지 설명하라. (3) 상자 안 깊이
값 배열(일부 0 = 측정 실패)을 만들어 중앙값 기반 3D 위치 추정 함수를 작성하라.

## 자가 점검 질문

1. 검출기 출력에 NMS 가 필요한 이유와 NMS 임계값이 너무 낮을 때의 부작용은 무엇인가?
2. 장애물 회피용 검출기와 파지용 검출기에서 정밀도·재현율 중 무엇을 더 중시해야 하는가?
3. 2D 상자만으로는 물체의 3D 위치를 알 수 없는 이유와 이를 보완하는 센서 두 가지를 들어라.

## 이 단계 공부법

1. **교재(먼저):** Tedrake *Robotic Manipulation* Ch. 9 을 읽으며 로봇에서 검출·분할 결과가 어떻게
   쓰이는지 큰 그림을 잡고, Ch. 10 Deep Perception 은 훑어본다.
2. **본문 + 예제:** IoU 를 손으로 한 번 계산하고 코드와 맞춰 본다.
3. **문제:** 퀴즈 → 연습 과제 (1)~(3). 곡선을 그려 임계값 선택 감각을 기른다.
4. **실습(선택):** PyTorch 가 익숙하다면 사전 학습 검출기를 내려받아 출력 상자를 이 레슨의
   후처리 코드에 넣어 본다. 한국어 실습 강의가 필요하면 패스트캠퍼스 Physical AI 입문 Part 2 를 참고한다.
5. **마무리:** M1~M4 의 좌표 변환·노이즈 모델·카메라 모델이 어디서 다시 쓰였는지 정리한다.

## 참고 자료

- Russ Tedrake, *Robotic Manipulation*, Ch. 9–10 — <https://manipulation.mit.edu/>
- Shree Nayar, *First Principles of Computer Vision* — <https://fpcv.cs.columbia.edu/>
- 패스트캠퍼스, Physical AI 입문 All-In-One — <https://fastcampus.co.kr/data_online_physicalai>
