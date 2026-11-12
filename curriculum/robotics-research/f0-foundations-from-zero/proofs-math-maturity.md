---
id: f0-proofs-math-maturity
title: 증명 읽기·쓰기 (수학적 성숙도)
summary: >-
  정의-정리-증명 구조를 읽고, 귀납법·대우·모순법으로 간단한 명제를 직접 증명하는 수준까지 올린다.
  Hammack 의 Book of Proof(무료 전문)와 MIT 6.042J 로 안내하는 가이드형 레슨이다.
objectives:
  - 정의·정리·보조정리·따름정리의 역할을 구분하고 증명의 구조를 읽을 수 있다.
  - 직접 증명·대우·모순법·반례를 상황에 맞게 고를 수 있다.
  - 수학적 귀납법(강한 귀납법 포함)으로 명제를 증명할 수 있다.
  - 전칭·존재 한정사를 정확히 쓰고 그 부정을 만들 수 있다.
  - 증명의 빈틈을 찾아 "무엇이 더 필요한가"를 지적할 수 있다.
prerequisites: [f0-calculus-single-variable]
difficulty: 2
estimated_minutes: 3000
tags: [foundations, proofs, mathematical-maturity, guide]
activities:
  - id: f0-proofs-math-maturity-diagnostic
    kind: quiz
    title: 시작 전 자가 진단 (통과하면 이 레슨을 건너뛴다)
    estimated_minutes: 40
  - id: f0-proofs-math-maturity-reading
    kind: reading
    title: Book of Proof 읽기 (Part I-IV) + 6.042J 강의 영상
    estimated_minutes: 1500
  - id: f0-proofs-math-maturity-problems
    kind: exercise
    title: 증명 연습 (선별 해답으로 자기 채점) + 6.042J 기출
    estimated_minutes: 1460
resources:
  - title: "Hammack, Book of Proof (3rd edition, 무료 전문)"
    url: https://richardhammack.github.io/BookOfProof/
    kind: book
    note: 1순위. Part I-IV 14장 + 선별 해답. CC BY-NC-ND 로 전문 공개(v3.4, 2025-02).
  - title: "MIT 6.042J Mathematics for Computer Science (Fall 2010)"
    url: https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/
    kind: course
    note: 강의 영상·읽기 자료·기출 시험과 해답 공개. 증명을 "쓰는" 훈련에 특히 좋다.
---

# 증명 읽기·쓰기 (수학적 성숙도)

## 도달 목표

이 레슨은 **가이드형**이다. 통과하면 건너뛴다.

**이 레슨이 F0 에서 가장 중요하고 가장 자주 건너뛰어진다.** 연구 트랙의 레슨 표준은 레슨마다
깊이 D2(완전 유도) 이상을 요구하고, D3 결과에는 증명 스케치를 요구한다. 증명을 **읽을 수** 없으면
필독 논문의 보장(guarantee)을 평가할 수 없고, 증명을 **쓸 수** 없으면 문제 세트의 P-P 유형을
풀 수 없다.

R0 의 D3 결과(Newton 의 2차 수렴, Cramér–Rao 하한, KKT)를 만나기 **전에는 반드시** 마쳐야 한다.
F0 의 마지막에 두는 것은 앞 과목들에서 증명을 **읽어 본 뒤**가 효율적이기 때문이다.

통과 기준은 §시작 전 자가 진단의 6문항 중 5문항 이상이다.

## 시작 전 자가 진단

`rc quiz f0-proofs-math-maturity` 로 푼다. 5/6 이상이면 F0 를 마치고 `robotics-expert` 코스 또는
R0 수학 브리지로 간다.

```quiz
activity: f0-proofs-math-maturity-diagnostic
questions:
  - id: q1
    type: single
    prompt: "\"모든 $x$ 에 대해 $P(x)$ 이면 $Q(x)$\" 의 부정은?"
    choices:
      - "모든 $x$ 에 대해 $P(x)$ 이고 $\\lnot Q(x)$"
      - "어떤 $x$ 가 존재해 $P(x)$ 이고 $\\lnot Q(x)$"
      - "모든 $x$ 에 대해 $\\lnot P(x)$ 이면 $\\lnot Q(x)$"
      - "어떤 $x$ 가 존재해 $\\lnot P(x)$ 이고 $Q(x)$"
    answer: 1
    explanation: "$\\lnot\\forall x(P\\to Q) \\equiv \\exists x(P \\land \\lnot Q)$. 반례를 찾는 것이 전칭 명제를 반박하는 방법이라는 뜻이다 — 문제 세트의 P-C(반례) 유형이 이 구조를 쓴다."
    concept: { front: "전칭 함축의 부정", back: "$\\lnot\\forall x(P\\to Q) \\equiv \\exists x(P\\land\\lnot Q)$ — 반례 하나로 반박된다" }
  - id: q2
    type: single
    prompt: "\"$n^2$ 이 짝수이면 $n$ 이 짝수\" 를 증명하는 가장 자연스러운 방법은?"
    choices:
      - "직접 증명 ($n^2$ 이 짝수라고 가정하고 $n$ 이 짝수임을 유도)"
      - "대우 증명 ($n$ 이 홀수라고 가정하고 $n^2$ 이 홀수임을 보임)"
      - "수학적 귀납법"
      - "반례 제시"
    answer: 1
    explanation: "대우($\\lnot Q \\to \\lnot P$)가 훨씬 쉽다: $n=2k+1$ 이면 $n^2 = 2(2k^2+2k)+1$ 로 홀수다. 어떤 증명 전략을 고르는지가 증명의 절반이다."
    concept: { front: "대우 증명", back: "$P\\to Q$ 대신 $\\lnot Q\\to\\lnot P$ 를 증명한다. 가정에서 구조를 꺼내기 쉬울 때 유리" }
  - id: q3
    type: single
    prompt: "강한 귀납법(strong induction)이 보통 귀납법과 다른 점은?"
    choices:
      - "기저 사례가 필요 없다"
      - "$n-1$ 뿐 아니라 $n$ 미만의 **모든** 경우를 가정에 쓴다"
      - "무한 집합에만 쓸 수 있다"
      - "결론이 더 약하다"
    answer: 1
    explanation: "강한 귀납법은 $P(1),\\dots,P(n-1)$ 전부를 가정해 $P(n)$ 을 보인다. 재귀적 분할(예: 분할정복 알고리즘의 정당성)에서 필요하다. 기저 사례는 여전히 필요하다."
    concept: { front: "강한 귀납법", back: "$n$ 미만의 모든 경우를 가정한다. 기저 사례는 여전히 필요하고, 결론은 같다" }
  - id: q4
    type: truefalse
    prompt: "어떤 명제에 대해 반례를 찾지 못했다면 그 명제는 참이다."
    answer: false
    explanation: "반례를 못 찾은 것은 증명이 아니다 — 아직 찾지 못했을 뿐일 수 있다. 연구 트랙의 재현 과제가 \"수치 실험에서 성립했다\"를 증명으로 인정하지 않는 이유가 이것이다."
    concept: { front: "반례 부재는 증명이 아니다", back: "참을 보이려면 증명이 필요하다. 수치 실험은 반증 도구일 뿐" }
  - id: q5
    type: single
    prompt: "증명에서 보조정리(lemma)의 역할은?"
    choices:
      - "정리보다 중요한 결과"
      - "주 정리의 증명을 위해 따로 떼어 증명하는 중간 결과"
      - "정리에서 바로 따라오는 결과"
      - "증명되지 않은 가정"
    answer: 1
    explanation: "보조정리는 주 증명을 짧게 만들기 위한 중간 결과이고, 따름정리(corollary)가 정리에서 바로 따라오는 결과다. 레슨 표준의 증명 스케치가 \"어느 보조정리를 생략했는지\" 밝히라고 요구하는 이유다."
    concept: { front: "보조정리와 따름정리", back: "보조정리 = 주 증명을 위한 중간 결과, 따름정리 = 정리에서 바로 따라오는 결과" }
  - id: q6
    type: short
    prompt: "$\\sqrt{2}$ 가 무리수임을 증명할 때 쓰는 증명 기법의 이름은? (한국어 또는 영어)"
    answer: ["모순법", "귀류법", "contradiction", "proof by contradiction", "reductio ad absurdum", "모순 증명"]
    explanation: "유리수라고 가정해 서로소 조건과 모순을 끌어내는 모순법(귀류법)이다. C1 의 \"전역 3-매개변수 좌표가 없다\"는 논증도 같은 구조다(콤팩트성 모순)."
    concept: { front: "모순법(귀류법)", back: "결론의 부정을 가정해 모순을 끌어낸다. 존재하지 않음을 보일 때 특히 유용" }
```

## 학습 경로

**1순위**: [Hammack, *Book of Proof* (무료 전문)](https://richardhammack.github.io/BookOfProof/) —
Part I–IV 의 14장과 선별 해답.
**병행**: [MIT 6.042J (Fall 2010)](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/) —
강의 영상과 기출 시험·해답. 증명을 **쓰는** 훈련에 특히 좋다.

| 단계 | 범위 | 무엇을 할 수 있게 되는가 | 예상 |
|---|---|---|---|
| 1 | Book of Proof Part I (집합·논리) | 한정사, 함축과 대우, 부정 만들기 | 10시간 |
| 2 | Part II (증명 기법) | 직접 증명, 대우, 모순법, 경우 나누기 | 14시간 |
| 3 | Part III (귀납법·관계·함수) | 수학적 귀납법과 강한 귀납법, 동치관계, 단사·전사 | 14시간 |
| 4 | 6.042J 로 쓰기 연습 | 증명을 **스스로 써서** 채점받는 훈련 | 12시간 |

합계 약 50시간. **4단계를 건너뛰지 말라** — 읽는 것과 쓰는 것은 다른 기술이고, 연구 트랙은 쓰기를 요구한다.

## 이 단계 공부법

1. **진단을 먼저 (40분)** — 5/6 이상이면 끝이다. 특히 q1(부정 만들기)과 q4(반례 부재)를
   틀렸다면 반드시 이 레슨을 해야 한다.
2. **증명을 덮고 다시 쓴다 (매 장)** — 증명을 읽고 이해한 느낌이 드는 것은 함정이다. 책을 덮고
   백지에서 다시 쓸 수 있을 때만 이해한 것이다. 이 방법이 연구 트랙 레슨의 "백지에서 유도"
   통과 기준과 같다.
3. **전략을 먼저 고른다** — 증명을 쓰기 전에 "직접? 대우? 모순? 귀납?"을 적는다. 레슨 표준의
   증명 스케치가 "전략 한 줄"을 요구하는 것이 이 습관이다.
4. **빈틈을 찾는 연습을 한다 (단계마다 2시간)** — 일부러 틀린 증명을 읽고 어디가 틀렸는지
   찾는다. 6.042J 기출에 이런 문항이 있다. 논문의 보장을 평가하는 능력이 여기서 온다.
5. **한정사를 기호로 쓴다 (3시간)** — 자연어 명제를 $\forall/\exists$ 로 옮기고 부정을 만든다.
   "모든 $\epsilon$ 에 대해 어떤 $\delta$ 가 존재해..." 구조를 자유롭게 다루는 것이 목표다.
6. **쓴 증명을 남에게 보여 준다 (4단계)** — 6.042J 기출을 풀고 해답과 **구조**를 비교한다.
   답이 맞아도 구조가 다르면 왜 그런지 본다.

**통과 기준**: 진단 5/6 이상, Book of Proof Part I–III 의 선별 해답 문제 80% 이상, 그리고
6.042J 기출의 증명 문항을 스스로 써서 해답과 구조가 일치한다.
