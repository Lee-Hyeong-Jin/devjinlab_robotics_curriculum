# 0005. 간격 반복 알고리즘: SM-2 (FSRS 는 Phase 2 재검토)

- 상태: accepted
- 날짜: 2026-11-11
- 관련: docs/PRD.md FR-4.3, §7(비기능), 결정 2; docs/platform-design.md §5 `rc review`;
  harness/roadmap.yaml P1-2; docs/specs/P1-2.md

## 맥락

퀴즈 오답과 핵심 개념을 플래시카드로 만들어 복습 일정을 자동 계산해야 한다(G4, FR-4.2~4.3).
제약: 오프라인·로컬 단일 사용자, Python 단일 스택, 런타임 의존성 최소, 계산은 단위 테스트로
검증 가능해야 한다(PRD §7). 카드 수는 Phase 1 기준 수십~수백 장이고 복습은 터미널에서 한다.

## 선택지

| 선택지 | 장점 | 단점 |
|---|---|---|
| A. SM-2 (SuperMemo 2, 1987) | 공식이 10줄, 상태가 3개(repetitions, interval, ease)라 순수 함수로 구현·테스트가 쉽다. 의존성 없음. Anki 가 수십 년 써서 동작이 널리 이해된다. | 개인별 망각 곡선을 학습하지 않아 일정이 덜 최적. 초반 `again` 이 간격을 1일로 완전히 리셋한다. |
| B. FSRS (Free Spaced Repetition Scheduler) | 기억 모델(difficulty, stability, retrievability) 기반으로 복습 부담을 20~30% 줄인다는 보고. 목표 유지율을 조절할 수 있다. | 파라미터 17~21개, 최적화기(복습 로그 수천 건 필요). 참조 구현(`fsrs` 패키지)에 의존하거나 직접 이식해야 한다. 로그가 적은 Phase 1 에서는 기본 파라미터로만 돌아 이점이 작다. |
| C. 고정 간격(1-3-7-14-30일) | 가장 단순 | 응답 품질을 반영하지 못해 "간격 반복" 요구(FR-4.3, 응답별 일정 변화)를 만족하지 않는다. |

## 결정

A(SM-2)를 택한다. PRD 결정 2 와 일치한다.

- 구현: `src/robotics_curriculum/learn/sm2.py` 의 순수 함수 `schedule(state, rating, today)`.
  응답 `again/hard/good/easy` 를 q = 1/3/4/5 로 매핑한다. q < 3 이면 repetitions 0, 간격 1일;
  아니면 repetitions+1, 간격 1 → 6 → round(이전 간격 × ease); ease 는
  `max(1.3, ease + 0.1 − (5−q)(0.08 + (5−q)·0.02))`; due = today + 간격.
- 상태는 `card_state(card_id, user_id, repetitions, interval_days, ease, due)` 에 저장하고
  모든 응답을 `reviews` 에 남긴다. 이 로그는 나중에 FSRS 최적화기의 입력이 될 수 있다.
- 복습 세션에서 `again` 카드는 세션 끝에 다시 제시한다(최대 2회). 이는 저장 상태와 무관한
  세션 내 동작이며 SM-2 상태는 첫 응답 기준으로 한 번만 갱신한다.

## 결과

- 얻는 것: 의존성 0, 결정적 단위 테스트, 사용자가 이해하기 쉬운 일정("틀리면 내일, 맞히면
  6일 뒤 …").
- 잃는 것 / 감수하는 리스크: 개인화된 최적 일정은 아니다. ease 가 1.3 으로 바닥에 붙는
  "ease hell" 이 생길 수 있다(카드가 많아지면 체감).
- 후속 작업: Phase 2 에서 `reviews` 로그가 충분히 쌓이면 FSRS 를 같은 `schedule` 인터페이스로
  추가하고 설정으로 고르게 한다. 상태 컬럼은 FSRS 용(difficulty, stability)을 그때 마이그레이션으로
  더한다.
