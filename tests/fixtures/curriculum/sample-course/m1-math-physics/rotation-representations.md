---
id: m1-rotation-representations
title: 회전 표현
summary: 테스트용 레슨.
objectives:
  - 회전 행렬과 쿼터니언을 비교할 수 있다.
prerequisites: [m1-vectors-matrices]
difficulty: 2
estimated_minutes: 30
activities:
  - id: m1-rotation-representations-reading
    kind: reading
    title: 본문 읽기
  - id: m1-rotation-representations-quiz
    kind: quiz
    title: 확인 퀴즈
    estimated_minutes: 5
---

# 회전 표현

본문.

## 확인 퀴즈

```quiz
activity: m1-rotation-representations-quiz
questions:
  - id: q1
    type: single
    prompt: "회전 행렬 $R$ 의 역행렬은?"
    choices: ["$R$", "$R^T$", "$-R$", "$\\det R$"]
    answer: 1
    explanation: "회전 행렬은 직교 행렬이므로 $R^{-1} = R^T$ 다."
    concept: { front: "회전 행렬의 역행렬", back: "전치 행렬 $R^T$ (직교 행렬)" }
  - id: q2
    type: multiple
    prompt: "회전 행렬의 성질을 모두 고르시오."
    choices: ["직교 행렬이다", "행렬식이 1이다", "대칭 행렬이다"]
    answer: [0, 1]
    explanation: "회전 행렬은 직교 행렬이고 행렬식이 +1 이다. 일반적으로 대칭이 아니다."
  - id: q3
    type: truefalse
    prompt: "단위 쿼터니언은 3차원 회전을 표현할 수 있다."
    answer: true
    explanation: "단위 쿼터니언은 회전축과 각도를 4개 수로 담는다."
  - id: q4
    type: short
    prompt: "3×3 회전 행렬의 행렬식 값은?"
    answer: ["1", "+1"]
    explanation: "반사를 포함하지 않는 직교 행렬이므로 det = +1."
    tags: [linear-algebra]
```
