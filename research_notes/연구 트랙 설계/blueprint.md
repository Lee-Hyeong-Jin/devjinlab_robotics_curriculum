# 로보틱스 연구원 트랙 설계안 (Robotics Researcher Track Blueprint)

> 목표: **로보틱스 연구원(robotics researcher)** 을 기르는 specialization 급 전문 과정.
> 기준은 세계 최상위 대학원 과목과 국제 학회(RSS, ICRA, IROS, CoRL, IJRR, T-RO, RA-L,
> NeurIPS/ICML/ICLR)의 연구 수준이다. 근거는 [benchmark.md](benchmark.md)(확인된 강의계획·자격요건),
> 레슨 작성 규칙은 [lesson-standard.md](lesson-standard.md), 필독 논문은 [papers.yaml](papers.yaml).
>
> 기존 `curriculum/robotics-expert`(10모듈 50레슨)은 로보틱스 **엔지니어** 입문~중급 과정이다.
> 이 설계는 그것을 대체하지 않고 **선수 과정으로 두고 그 위에 새 코스를 세운다**
> (새 코스 디렉터리: `curriculum/robotics-research`). 매핑은 §7.
>
> 콘텐츠 언어는 한국어 + 영문 용어 병기이며, 영어 번역본(`.en.md`)이 동등하게 제공되는 것을 전제로
> 설계한다. 레슨 본문의 1차 자료는 **원 논문**이다.

## 1. 전제 지식 (assumed background)

CMU RI 가 박사과정 전제로 명시한 배경(calculus, linear algebra, numerical analysis, probability
and statistics, programming, algorithms, mechanics, dynamics)과 MIT EECS TQE Group 4
(Dynamic Systems and Control, Nonlinear Optimization, Mathematical Programming)를 기준으로 한다
([benchmark.md](benchmark.md) §7.1, §7.3).

| 영역 | 요구 수준 | 판정 기준 (이것을 못 하면 Stage 0 필수) |
|---|---|---|
| 선형대수 (linear algebra) | 학부 상급 + 수치선형대수 입문. SVD·QR·Cholesky, 부분공간, 최소제곱, 조건수 | 정규방정식이 왜 조건수를 제곱하는지 설명하고 QR 로 대신 푸는 이유를 말할 수 있다 |
| 해석·미적분 (analysis) | 다변수 미적분, 음함수 정리, Taylor 정리, ODE 존재·유일성, Gronwall | 음함수 정리로 제약 다양체의 국소 매개화를 유도할 수 있다 |
| 확률·통계 (probability) | 측도론은 불필요하나 확률 수렴(a.s., in probability), 조건부 기댓값, 가우시안 대수, MLE/MAP, Cramér–Rao | 선형 가우시안 모델에서 MAP = 가중 최소제곱임을 유도할 수 있다 |
| 최적화 (optimization) | 볼록성, 쌍대성, KKT, Newton·준뉴턴, SQP·내부점 입문 (Boyd–Vandenberghe + Nocedal–Wright) | 등식·부등식 제약 문제의 KKT 조건을 쓰고 쌍대 간극을 해석할 수 있다 |
| 미분기하 (differential geometry) | 매끄러운 다양체, 접공간, **행렬 리 군·리 대수, 지수·로그 사상** (Barfoot ch.7–8, MLS ch.2) | $SO(3)$ 에서 지수 사상의 미분(좌/우 야코비안)이 왜 항등이 아닌지 설명할 수 있다 |
| 수치해석 (numerical methods) | ODE 적분기(명시·암시·symplectic), 희소 선형대수, 자동 미분 | 강성(stiff) 시스템에서 전진 Euler 가 실패하는 조건을 말할 수 있다 |
| 고전 역학 (mechanics) | Newton–Euler, Lagrange 역학, 변분 원리 | 홀로노믹 제약이 있는 계의 Euler–Lagrange 식을 유도할 수 있다 |
| 프로그래밍 | Python(numpy/scipy, jax 또는 pytorch), C++ **읽기**, Git, 수치 실험 설계 | 수치 야코비안으로 해석적 야코비안을 검증하는 테스트를 쓸 수 있다 |
| 로보틱스 기초 | `robotics-expert` 코스(기존 50레슨) 수준: 기구학, PID, 센서, 베이즈 필터, A*/RRT, ROS 2 개요 | §7 의 "선수로 유지" 레슨을 이수했다 |

**영어**: 모든 1차 자료(논문·교재·강의)는 영어다. 한국어 자료는 보조이며 필수 아니다.

## 2. 트랙 구조 (track structure)

```
Stage -1 F0 시작 전 기초 (foundations from zero)        8 레슨   ─ 진단 통과 시 건너뛰기
         └ 미적분·선형대수·미분방정식·확률·고전역학·증명·파이썬 (가이드형)

Stage 0  R0 수학·수치 기초 (bridge)                     7 레슨   ─ 진단 통과 시 건너뛰기
         └ 기존 robotics-expert 50레슨 = 로보틱스 선수

Stage 1  공통 코어 (common core)                        51 레슨  ─ 권장 전원 이수
         C1 강체 기하와 리 군                   5
         C2 다물체 동역학                       6
         C3 비선형·강건 제어                    6
         C4 최적 제어·궤적 최적화               7
         C5 상태 추정                           6
         C6 동작 계획 이론                      7
         C7 지각과 3D 표현                      6
         C8 의사결정·학습 이론                  8

Stage 2  Specialization (택 1, 권장 2)                  6 레슨/트랙
         S1 SLAM·공간 지능 | S2 조작·접촉 | S3 보행·언더액추에이티드
         S4 로봇 학습·파운데이션 모델 | S5 다중 로봇·필드 로보틱스

Stage 3  연구 실행 (research practice)                   9 레슨  ─ 권장 전원 이수
         R1 연구 방법론  6     R2 캡스톤  3
```

총 105레슨(= 8 + 7 + 51 + 30 + 9). 한 학습자의 이수 경로는 **Stage -1·0(진단으로 건너뛸 수 있음)
+ 코어 51 + specialization 6~12 + Stage 3 의 9** ≈ 66–87레슨.

> **선수는 "권장"이다 (사용자 결정 2026-11-12).** 플랫폼은 선수 레슨을 **잠그지 않는다** — 선수
> 관계는 권장 순서를 보여 주는 정보일 뿐이고, 학습자는 어느 레슨이든 바로 열 수 있다. 대신 각
> 모듈의 **첫 레슨에 "시작 전 자가 진단"** 문항을 두어 학습자가 스스로 준비 상태를 판단한다
> ([lesson-standard.md](lesson-standard.md) §1). 아래 DAG 는 **권장 선수(recommended
> prerequisites)** 를 뜻한다.

**공통 코어 8모듈의 근거**: CMU RI Core Course Qualifier 의 4영역(Perception / Cognition /
Action / Math Foundations)과 MIT EECS TQE Group 3·4 의 교집합이다([benchmark.md](benchmark.md) §9-1).
Action → C1·C2·C3·C4, Perception → C5·C7, Cognition → C8, Math Foundations → R0 + 각 모듈의 유도.

### 모듈 선수 관계 (prerequisite DAG)

```
F0 ──> (robotics-expert 50레슨) ──> R0 ──> C1 ──> C2 ──> C3 ──> C4
       │       │             ↑
       │       └─────────────┘
       │ (R0 에서)
       ├────> C5 <─── C7
       ├────> C6 <─── C4 (미분 제약·커널 계획)
       └────> C8 <─── C4 (DP·LQR), C6 (MDP·탐색)

C1,C5,C7           ──> S1 SLAM·공간 지능
C1,C2,C3,C4,C6     ──> S2 조작·접촉
C1,C2,C3,C4        ──> S3 보행·언더액추에이티드
C7,C8              ──> S4 로봇 학습·파운데이션 모델
C5,C6,C8           ──> S5 다중 로봇·필드 로보틱스
전체 코어 + S* 1개 ──> R1 ──> R2 캡스톤
```

### 권장 순서와 기간

주 12시간(연구 트랙 레슨 1개 = 5–15시간, [lesson-standard.md](lesson-standard.md) §9) 기준:

| 구간 | 내용 | 레슨 | 기간 |
|---|---|---|---|
| -1 | F0 진단 → 부족한 것만 (완전 초보는 전부) | 0–8 | 0–10개월 |
| -0.5 | `robotics-expert` 코스(기존 50레슨) — 로보틱스 선수 | 0–50 | 0–4개월 |
| 0 | R0 진단 → 부족한 것만 | 0–7 | 0–2개월 |
| 1 | C1 → C2 → C3 (기하·동역학·제어) | 17 | 4개월 |
| 2 | C4 → C5 (최적 제어·추정) — 두 모듈이 이 트랙의 중심 | 13 | 3.5개월 |
| 3 | C6 → C7 → C8 (계획·지각·학습) | 21 | 5개월 |
| 4 | Specialization 1개 | 6 | 2개월 |
| 5 | R1 연구 방법론 (specialization 과 병행 가능) | 6 | 1.5개월 |
| 6 | R2 캡스톤 (서베이 → 재현 → 기여 + 워크숍 논문 초안) | 3 | 4개월 |
| | **합계(연구 트랙만)** | **66** | **약 20개월** |

주 20시간이면 약 12개월. 두 번째 specialization 을 더하면 +2개월.

**0에서 박사급까지의 전체 경로**(완전 초보가 아무것도 건너뛰지 않는 경우, 주 12시간 기준):

| 단계 | 도달 수준 | 누적 학습 시간 | 누적 기간 |
|---|---|---|---|
| Stage -1 (F0) | 학부 1–2학년 수학·물리·프로그래밍 | 약 500시간 | 약 10개월 |
| robotics-expert 50레슨 | 로보틱스 엔지니어 입문~중급 | 약 600시간 | 약 12개월 |
| Stage 0 (R0) | 대학원 입학 수준의 수학·수치 도구 | 약 660시간 | 약 13개월 |
| Stage 1 (코어 51) | 박사과정 자격시험 과목 수준 | 약 1,070시간 | 약 21개월 |
| Stage 2 (specialization) | 특정 분야의 최신 논문을 읽고 재현 | 약 1,120시간 | 약 22개월 |
| Stage 3 (R1·R2) | 서베이·재현·작은 기여 + 워크숍 논문 초안 | 약 1,200시간 | 약 24개월 |

즉 **완전한 0에서 시작하면 주 12시간으로 약 2년, 주 20시간으로 약 15개월**이다. 진단으로
건너뛰는 단계가 많을수록 짧아진다. 이 숫자는 레슨의 `estimated_minutes` 합계에서 계산한
추정이며 실측값이 아니다.

## 3. 표기 규약

각 모듈 표의 열:
- **유도해야 할 핵심 결과**: 학습자가 종이 위에서 복원해야 하는 정리·식.
  깊이 등급은 [lesson-standard.md](lesson-standard.md) §2 의 D0–D3.
- **필독**: [papers.yaml](papers.yaml) 의 논문 id. 레슨당 1–3편(총 100편 내외로 맞추기 위한 상한).
  URL·저자·연도·venue 는 papers.yaml 에 있고, 확인 여부는 그 파일의 `verified` 필드가 정한다.
- **교재**: 확인된 교재의 장·절([benchmark.md](benchmark.md) §8). 약어 — **MR** Lynch–Park
  *Modern Robotics* · **UA** Tedrake *Underactuated Robotics* · **PA** LaValle *Planning
  Algorithms* · **SER** Barfoot *State Estimation for Robotics* 2e · **CO** Boyd–Vandenberghe
  *Convex Optimization* · **MVG** Hartley–Zisserman · **CV** Szeliski 2e · **RBDA** Featherstone ·
  **MLS** Murray–Li–Sastry(교재 지정은 확인, 공식 URL 미확인) · **PR** Thrun–Burgard–Fox(동일) ·
  **S&B** Sutton–Barto(동일) · **NW** Nocedal–Wright(동일) · **Khalil**(동일).
- **재현 과제**: 티어 R1–R4([lesson-standard.md](lesson-standard.md) §6)와 수용 기준 요약.

## 3-1. Stage -1 — F0 시작 전 기초 (foundations from zero)

**왜 있는가**: 이 커리큘럼은 "0부터 박사급까지"를 목표로 한다(사용자 결정 2026-11-12). 기존
50레슨은 고교 수학과 기본 파이썬을 전제하고, R0 는 학부 수학을 전제한다. 그 아래를 메우는 단계다.

**형식이 다르다**: F0 레슨은 내용을 새로 쓰지 않는다. **가이드형(guide) 레슨**이다 — 검증된 공개
강의·교재를 어떤 순서로, 어디까지, 무엇으로 확인하며 볼지 안내하고, **진단 문제**로 통과 여부를
스스로 판정하게 한다. 진단을 통과하면 그 레슨을 건너뛴다. 따라서 연구 트랙 레슨 표준
([lesson-standard.md](lesson-standard.md) §1)의 고정 섹션을 적용하지 않고, 아래 4개 절만 **이 순서로** 쓴다:
`## 도달 목표` · `## 시작 전 자가 진단` · `## 학습 경로` · `## 이 단계 공부법`.
진단을 학습 경로보다 앞에 두는 것은 F0 에서 진단이 "이 레슨을 건너뛸지"를 먼저 정하는 관문이기
때문이다(집필하면서 정한 순서다). 진단은 ` ```quiz ` 블록으로 써서 `rc quiz` 로 채점되게 한다.

아래 URL 은 모두 2026-11-12 에 fetch 해 확인했다. 제공 내용(영상·문제집·해답·시험)도 그때 확인한 것이다.

| 레슨 | 도달 목표(통과 기준) | 안내 자료 (확인됨) | 예상 시간 |
|---|---|---|---|
| `f0-calculus-single-variable` 미적분 I | 극한·도함수·적분·Taylor 급수를 계산하고, 최적화 문제를 미분으로 풀 수 있다 | [MIT 18.01 Single Variable Calculus (Fall 2006)](https://ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006/) — 강의 영상, 강의 노트, 시험+해답 | 70시간 |
| `f0-calculus-multivariable` 미적분 II | 편미분·기울기·연쇄법칙·다중적분·발산/회전을 계산하고 기울기의 기하적 의미를 설명할 수 있다 | [MIT 18.02 Multivariable Calculus (Fall 2007)](https://ocw.mit.edu/courses/18-02-multivariable-calculus-fall-2007/) — 강의 영상, 노트, 시험+해답 | 70시간 |
| `f0-linear-algebra` 선형대수 | 소거법·부분공간·4개 기본 부분공간·고윳값·SVD 를 손으로 계산하고 의미를 말할 수 있다 | [MIT 18.06 Linear Algebra (Spring 2010, Strang)](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/) — 강의 영상, 문제집+해답, 시험+해답 | 80시간 |
| `f0-differential-equations` 미분방정식 | 1·2계 ODE 를 풀고, 선형 계의 해를 고윳값으로 해석하고, 수치 적분기의 필요성을 설명할 수 있다 | [MIT 18.03 Differential Equations (Spring 2010)](https://ocw.mit.edu/courses/18-03-differential-equations-spring-2010/) — 강의 영상, 노트, 문제집+해답 | 60시간 |
| `f0-probability-statistics` 확률·통계 | 조건부확률·베이즈 정리·기댓값·분산·대수의 법칙·중심극한정리를 쓰고, 추정과 신뢰구간을 계산할 수 있다 | [MIT 18.05 Introduction to Probability and Statistics (Spring 2022)](https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/) — 노트, 문제집+해답, 시험+해답(영상 없음) · 영상이 필요하면 [MIT 6.041 (Fall 2010)](https://ocw.mit.edu/courses/6-041-probabilistic-systems-analysis-and-applied-probability-fall-2010/) — 강의 영상, 문제집+해답 | 70시간 |
| `f0-classical-mechanics` 고전 역학 | Newton 법칙으로 운동을 세우고, 에너지·운동량 보존과 회전 운동(관성 모멘트, 토크)을 다룰 수 있다 | [MIT 8.01SC Classical Mechanics (Fall 2016)](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/) — 강의 영상, 문제집 1–12, 온라인 교재 | 70시간 |
| `f0-proofs-math-maturity` 증명 읽기·쓰기 | 정의-정리-증명 구조를 읽고, 귀납법·대우·모순법으로 간단한 명제를 **직접 증명**할 수 있다 | [Hammack, *Book of Proof* (3판, 무료 전문)](https://richardhammack.github.io/BookOfProof/) — Part I–IV 14장 + 선별 해답 · [MIT 6.042J Mathematics for Computer Science (Fall 2010)](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/) — 강의 영상, 시험+해답 | 50시간 |
| `f0-python-numerics-git` 파이썬·수치계산·Git | numpy 로 배열 연산·브로드캐스팅을 쓰고, 부동소수점 오차와 조건수를 인식하고, Git 으로 작업을 관리할 수 있다 | [NumPy user guide](https://numpy.org/doc/stable/user/) · [Scientific Python Lectures](https://lectures.scientific-python.org/) · [Pro Git (무료 전문, CC BY-NC-SA)](https://git-scm.com/book/en/v2) | 40시간 |

합계 약 510시간. 주 12시간이면 약 10개월이지만, **대부분의 학습자는 전부 듣지 않는다** — 진단으로
통과한 레슨은 건너뛴다.

**권장 순서**: `f0-calculus-single-variable` → `f0-linear-algebra` → `f0-calculus-multivariable`
→ `f0-differential-equations` → `f0-probability-statistics` → `f0-python-numerics-git`
→ `f0-classical-mechanics` → `f0-proofs-math-maturity`.
선형대수를 일찍 넣는 이유는 로보틱스에서 가장 먼저, 가장 많이 쓰이기 때문이다. 증명 레슨을 마지막에
두는 이유는 앞의 과목들에서 증명을 읽어 본 뒤가 효율적이기 때문이다 — 다만 R0 의 D3 결과를 만나기
**전에는 반드시** 마쳐야 한다.

**진단 문제 작성 규칙**: 레슨당 5–8문항, 전부 **채점 가능한 계산·단답**으로, 정답과 허용오차를
공개한다. 통과선은 80%다. 진단은 "그 과목을 들었는가"가 아니라 "그 과목의 결과를 쓸 수 있는가"를
묻는다(예: "3×3 행렬의 SVD 를 구하고 특이값으로 조건수를 계산하라").

**확인하지 못한 자료**: 3Blue1Brown 의 "Essence of Linear Algebra" 시리즈는 fetch 한 페이지에서
시리즈 제목·목록을 확인하지 못했다 **(미확인)** — 안내 자료로 넣지 않았다. Strang 의 교재는
무료 공개가 아니므로 18.06 OCW 를 1순위로 둔다.

## 4. Stage 0 — R0 수학·수치 기초 (bridge)

`level: 연구`, 진단 퀴즈로 건너뛸 수 있는 모듈. 근거: CMU 16-811 이 Math Foundations 영역의
**유일한** 과목이라는 사실([benchmark.md](benchmark.md) §7.1)과 CS287·16-745 의 선수 요구.

| 레슨 | 유도해야 할 핵심 결과 | 필독 | 교재 | 재현 과제 |
|---|---|---|---|---|
| `r0-linear-algebra-decompositions` 분해와 조건수 | 최소제곱의 정규방정식 조건수 = $\kappa(A)^2$ **[D2]**; QR·SVD 해법의 안정성; 유사역행렬과 영공간 **[D2]** | 교재(예외 §5) | CO App. A, NW ch.2 | R1: 악조건 최소제곱을 정규방정식·QR·SVD 로 풀어 오차를 $\kappa$ 에 대해 도표화, QR 이 더 정확함을 수치로 보임 |
| `r0-sparse-linear-algebra` 희소 선형대수 | 희소 Cholesky 의 fill-in 과 소거 순서 의존성 **[D2]**; 정규방정식의 희소 구조와 Schur 보완 **[D2]**; CG 수렴 한계 $\sqrt{\kappa}$ **[D1]** | 교재(예외 §5) | SER ch.3, NW ch.5 | R1: 포즈 그래프 모양의 희소 행렬에 COLAMD 유무로 Cholesky 비영원소 수를 비교(10배 이상 차이 확인) |
| `r0-convex-optimization` 볼록성·쌍대성·KKT | 라그랑주 쌍대와 약·강 쌍대성 **[D3]**; KKT 필요·충분 조건 **[D3]**; SOCP/SDP 로의 환원 **[D1]** | 교재(예외 §5) | CO ch.2–5 | R1: QP 를 직접 쌍대로 풀고 cvxpy 해와 쌍대 간극 < 1e-8 일치 |
| `r0-numerical-optimization` 수치 최적화 | Newton 의 2차 수렴 **[D3]**; BFGS 업데이트와 secant 조건 **[D2]**; 신뢰영역·선탐색의 전역 수렴 **[D1]**; SQP 와 내부점의 구조 **[D1]** | 교재(예외 §5) | NW ch.3,6,18,19 | R2: Rosenbrock 에 대해 경사하강·Newton·BFGS 구현, 반복 수와 수렴 차수를 로그 도표로 확인 |
| `r0-estimation-theory` 확률과 추정 이론 | 선형 가우시안 MAP = 가중 최소제곱 **[D2]**; Cramér–Rao 하한 **[D3]**; 일관성·효율성·Fisher 정보 **[D2]** | 교재(예외 §5) | SER ch.2–3, PR ch.2 | R1: 1D 추정기 3종의 분산을 몬테카를로로 추정해 CRLB 와 비교(상대오차 < 5%) |
| `r0-manifolds-lie-groups` 다양체와 행렬 리 군 | 접공간·재추적(retraction) **[D2]**; $\exp/\log$ 사상과 그 미분(좌/우 야코비안) **[D3]**; BCH 1·2차 항 **[D2]** | 교재(예외 §5) | SER ch.7–8, MLS ch.2 | R1: $SO(3)$ 에서 $\exp$ 의 해석적 야코비안을 유한차분과 1e-7 이내 일치시킴 |
| `r0-ad-and-integrators` 자동 미분과 적분기 | forward/reverse mode 의 비용 비교 **[D2]**; 명시·암시·symplectic 적분기의 에너지 거동 **[D2]**; 강성 조건 **[D1]** | 교재(예외 §5) | NW ch.8, UA App. | R1: 진자에 Euler·RK4·symplectic 을 적용해 1e4 스텝 에너지 드리프트를 비교(symplectic 이 유계임을 확인) |

**열린 문제(모듈 수준)**: 비볼록 문제의 전역성 인증(certification) 가능 범위; 대규모 희소 2차
문제에서 1차 방법의 조건수 의존성 제거; 자동 미분이 비매끄러운(접촉) 동역학에서 주는 기울기의 타당성.

## 5. Stage 1 — 공통 코어

### C1 강체 기하와 리 군 (rigid-body geometry and Lie groups) — 5레슨
근거: MIT 16.485 L2–5·L18–19, CMU 16-711 Ch1–2(product of exponentials, Paden–Kahan),
16-745 W9(optimizing with attitude), Barfoot ch.7–8.

| 레슨 | 유도해야 할 핵심 결과 | 필독 | 교재 | 재현 과제 |
|---|---|---|---|---|
| `c1-so3-se3-exponential` SO(3)·SE(3)와 지수 좌표 | Rodrigues 공식 **[D3]**; $\mathfrak{so}(3)\to SO(3)$ 전사성과 로그의 특이점 **[D3]**; 4원수 이중 피복 **[D2]** | `sola2018-micro-lie-theory`, `forster2017-preintegration` (권장 `grassia1998-exp-map`, `shoemake1985-quaternion-curves`) | MR ch.3, MLS ch.2, SER ch.7 | R1: 지수·로그 왕복 오차 < 1e-12, $\theta\to\pi$ 근방에서 수치 붕괴 지점을 실험적으로 찾음 |
| `c1-twists-wrenches-adjoint` 트위스트·렌치와 수반 표현 | 좌표 변환 하의 트위스트 변환 $\mathrm{Ad}$ **[D2]**; 렌치의 쌍대 변환 $\mathrm{Ad}^{\!*}$ **[D2]**; 나선 운동(screw) 분해 **[D2]** | `featherstone2010-6d-vectors-part1`, `featherstone2010-6d-vectors-part2`, `brockett1984-poe` | MR ch.3.3, MLS ch.2.5 | R1: 임의 변환에서 $\mathrm{Ad}$ 로 옮긴 트위스트가 수치 미분한 속도와 1e-10 이내 일치 |
| `c1-lie-group-derivatives` 리 군 위의 미분 | 좌/우 야코비안 $J_l, J_r$ 과 $\exp$ 의 미분 **[D3]**; BCH 와 선형화 오차 차수 **[D2]**; 불변 거리와 평균(Fréchet mean) **[D2]** | `forster2017-preintegration` | SER ch.7.1–7.3 | R1: $SO(3)$ 평균을 리만 경사하강으로 계산, 재시작 100회에서 동일 해 수렴 확인 |
| `c1-poe-analytic-ik` Product of exponentials 와 해석적 IK | PoE 정기구학 **[D2]**; Paden–Kahan 부문제 1–3 **[D3]**; 6R 역기구학의 해 개수와 분기 **[D2]** | `brockett1984-poe`, `husty2007-6r-ik` | MLS ch.3, MR ch.4,6 | R2: 6R 팔의 해석적 IK 를 구현, 1e4 무작위 포즈에서 모든 해가 정기구학을 1e-9 이내 만족 |
| `c1-manifold-optimization` 매니폴드 위 최적화 | 재추적 기반 Gauss–Newton 의 국소 수렴 **[D3]**; 국소 매개화(lift-solve-retract)의 1차 동등성 **[D2]**; 과매개화(4원수) 제약 처리 **[D2]** | `absil2008-manifold-opt`, `dellaert2017-factor-graphs` | SER ch.7–8 | R2: $SE(3)$ 포즈 정합을 매니폴드 GN 으로 구현, 과매개화+정규화 방식보다 반복 수가 적음을 확인 |

**열린 문제**: $SE(3)$ 위 비볼록 문제의 전역 최적성 인증 범위; 회전 추정에서 특이점 없는 매개화와
수치 안정성의 교환; 학습 모델에 리 군 구조를 넣는 것의 실제 이득(등변성 vs 데이터 증강).

### C2 다물체 동역학 (multibody dynamics) — 6레슨
근거: CMU 16-711 Ch3–4, Featherstone RBDA, MR ch.8, UA ch.17(접촉).

| 레슨 | 유도해야 할 핵심 결과 | 필독 | 교재 | 재현 과제 |
|---|---|---|---|---|
| `c2-spatial-vector-algebra` 공간 벡터 대수 | 6D 운동·힘 공간의 쌍대성 **[D2]**; 공간 관성의 변환 법칙 **[D2]**; 공간 가속도와 코리올리 항의 분리 **[D3]** | `featherstone2010-6d-vectors-part1`, `featherstone2010-6d-vectors-part2` (권장 `featherstone2006-plucker-basis`) | RBDA ch.2, MR ch.8.2 | R1: 공간 관성 변환과 동차변환 기반 계산이 1e-10 이내 일치 |
| `c2-rnea-inverse-dynamics` 재귀 Newton–Euler | RNEA 의 $O(n)$ 복잡도와 재귀식 **[D3]**; Lagrange 유도와의 동등성 **[D2]** | `luh1980-rnea`, `featherstone2000-dynamics-equations-algorithms` | RBDA ch.5, MR ch.8.3 | R1: RNEA 토크가 Euler–Lagrange 해와 일치 — ① 기호·자동미분으로 미분한 정확한 해 대비 상대오차 < 1e-9(7-DOF) ② 유한차분 해 대비 < 1e-7 + h 스윕 V 곡선 (유한차분으로는 1e-9 가 불안정함을 실측: h=1e-4 에서 5.8e-8, 1e-5 에서 6.8e-10, 1e-6 에서 3.1e-9, 1e-7 에서 7.2e-8 — 저자 세션 측정 2026-11-12, 설계 담당 승인) |
| `c2-crba-aba` 질량행렬과 순동역학 | CRBA 의 $O(n^2)$ **[D3]**; ABA 의 $O(n)$ 과 관절 공간 관성의 분기 구조 **[D3]** | `featherstone1983-aba`, `walker1982-crba` | RBDA ch.6–7 | R1: CRBA 의 $M$ 이 유한차분 역동역학과 일치 — 중력 0·$\dot q = 0$ 에서 $\tau$ 가 $\ddot q$ 에 정확히 선형이므로 기계 정밀도(1e-12, 실측 4.4e-16, 모든 $h$ 에서 동일)로 요구한다. 중력을 켜면 상쇄가 지배해 1e-9 수준에 머문다(저자 세션 측정 2026-11-12); ABA 와 $M^{-1}\tau$ 해가 일치 |
| `c2-constrained-dynamics` 제약 동역학 | 라그랑주 승수와 KKT 형태의 동역학 **[D3]**; 널공간 투영과 조작 공간 관성 $\Lambda$ **[D3]**; Baumgarte 안정화 **[D1]** | `khatib1987-operational-space`, `udwadia1992-constrained-motion`, `baumgarte1972-constraint-stabilization` | RBDA ch.8, MLS ch.6 | R2: 폐루프 4절 링크를 승수법과 축소좌표법으로 적분, 제약 위반 < 1e-8 유지 |
| `c2-contact-dynamics` 접촉 동역학 | 상보성 조건(LCP/NCP)과 해 존재성 **[D3]**; 마찰 원뿔과 Painlevé 역설 **[D2]**; 시간 이산화(semi-implicit) 와 관통 **[D2]** | `stewart1996-implicit-timestepping`, `todorov2014-convex-contact`, `anitescu1997-lcp-contact` (권장 `stewart2000-rigid-body-friction-impact`, `genot1999-painleve`) | UA ch.17, RBDA ch.11 | R2: 평면 접촉 공을 LCP 1스텝 해법(모드 열거)으로 적분, 에너지 비증가와 비관통을 확인 — 실측: 분리·고착·미끄럼 3모드 도달, 충격량 스텝 25031/50000 에서 최대 dE = -3.0e-6(전부 음수), 원판은 관통 정확히 0, 봉은 O(h^2)(비 3.92/3.96/3.98/3.99). Painlevé 임계는 닫힌 형태 mu_crit = 4/3 at theta = -arctan 2 이고 가속도 수준이 비가해인 상태에서도 속도 수준은 풀린다 (저자 세션 측정 2026-11-12) |
| `c2-dynamics-derivatives-sysid` 동역학 미분과 시스템 식별 | RNEA 의 해석적 미분 **[D2]**; 관성 매개변수의 선형성과 식별 가능성 조건 **[D3]**; 물리적 일관성 제약(SDP) **[D2]** | `carpentier2018-pinocchio`, `atkeson1986-inertial-parameters`, `wensing2018-lmi-inertial` (권장 `gautier1990-minimal-inertial-parameters`) | RBDA ch.10, UA ch.18 | R2: 7-DOF 상태 표본에서 관성 매개변수를 선형 최소제곱으로 식별, 식별 가능한 조합만 복원됨을 조건수로 보임 — 실측(기준 팔): n_b = 43/70, dim N = 27, 특이값 간극 5.22 -> 1.9e-14, kappa = 25.39, 식별 가능 성분 오차는 sigma 에 선형(9.9e-4 per 1e-3)이고 N 성분 오차는 sigma 와 무관하게 4.7586 고정. 중력을 끄면 n_b = 39. 유사 관성 LMI 는 sigma = 0 에서도 최소노름 해를 비일관으로 만든다(저자 세션 측정 2026-11-12) |

**열린 문제**: 접촉이 있는 계의 미분가능성과 학습에 쓰는 기울기의 정당성; 실제 마찰·변형의 모델
오차 한계; 대규모 다물체계에서 실시간 미분 동역학의 비용.

### C3 비선형·강건 제어 (nonlinear and robust control) — 6레슨
근거: CMU 16-711 Ch5–6, Berkeley C106B W1–4, CS223A(operational space), UA ch.9, Khalil.

| 레슨 | 유도해야 할 핵심 결과 | 필독 | 교재 | 재현 과제 |
|---|---|---|---|---|
| `c3-lyapunov-stability` Lyapunov 안정성과 ISS | Lyapunov 정리와 역정리 **[D3]**; Barbashin–Krasovskii·LaSalle **[D3]**; ISS 와 비교 함수 **[D2]** | `sontag1989-coprime-factorization`, `papachristodoulou2002-sos`, `topcu2008-local-stability-sos` | Khalil ch.4, UA ch.9 | R1: 2차 계의 Lyapunov 함수를 SOS(sum-of-squares)로 탐색, 흡인 영역 추정값이 수치 적분 결과를 포함함을 확인 |
| `c3-feedback-linearization` 피드백 선형화와 가제어성 | 입출력·완전 선형화 조건(involutivity, Frobenius) **[D3]**; 비홀로노믹 계의 Chow–Rashevskii **[D2]**; 영역 동역학 **[D2]** | `murray1993-steering-sinusoids`, `hauser1992-nonminimum-phase`, `devasia1996-inversion` | Khalil ch.13, MLS ch.7 | R2: 차동구동 로봇을 사인파 조향(steering with sinusoids)으로 주차, 종단 오차 < 1e-3 |
| `c3-contraction-incremental` 수축 이론 | 수축 조건과 지수 수렴 **[D3]**; 미분 Lyapunov 와 리만 계량 **[D2]**; 추적 제어로의 적용 **[D2]** | `lohmiller1998-contraction`, `manchester2017-ccm`, `tsukamoto2021-contraction-tutorial` | Khalil ch.9(비교) | R1: 수축 계량이 주는 수렴률 상한이 실제 궤적 수렴률을 상회하는지 수치 검증 |
| `c3-passivity-impedance` 수동성·에너지 성형과 임피던스 제어 | 수동성 정리와 직렬 결합 안정성 **[D3]**; 에너지 성형·댐핑 주입 **[D2]**; 임피던스/어드미턴스 제어와 접촉 안정성 **[D2]** | `hogan1985-impedance`, `colgate1988-coupled-stability`, `colgate1997-sampled-passivity` | MR ch.11.6, MLS ch.6 | R2: 1-DOF 접촉 작업에서 임피던스 이득을 바꿔 안정 경계를 실험적으로 그림(이론 경계와 비교) |
| `c3-adaptive-control` 적응 제어 | 매개변수 수렴과 지속 여진(persistent excitation) **[D3]**; 확실성 등가의 함정 **[D2]**; $L_1$·강건 적응 **[D1]** | `slotine1987-adaptive-manipulator`, `boyd1986-pe`, `rohrs1985-unmodeled-dynamics` | Khalil ch.9 | R2: 매니퓰레이터 적응 제어를 구현, PE 를 만족하는 궤적에서만 매개변수가 수렴함을 보임 |
| `c3-cbf-safety-filter` CBF/CLF 안전 필터 | CBF 의 전진 불변성 **[D3]**; QP 기반 최소 개입 필터와 실현가능성 **[D2]**; 입력 제약·고차 CBF **[D2]** | `ames2017-cbf`, `ames2019-cbf-survey`, `nguyen2016-ecbf` | — | R2: 이중 적분기 안전 필터를 QP 로 구현, 제약 위반 0 과 비활성 구간에서 명목 제어와 일치 확인 |

**열린 문제**: 학습된 동역학 위에서의 안정성 보장; CBF 의 실현가능성과 보수성의 교환;
접촉·충격이 있는 계의 강건 안정성 이론.

### C4 최적 제어·궤적 최적화 (optimal control and trajectory optimization) — 7레슨
근거: **CMU 16-745 전체**, **Stanford AA203 전체**, Berkeley CS287, UA ch.7–10,13.
이 트랙의 중심 모듈이며, 과제 형식(구현 + ICRA/IROS 포맷 보고서)도 16-745 를 따른다.

| 레슨 | 유도해야 할 핵심 결과 | 필독 | 교재 | 재현 과제 |
|---|---|---|---|---|
| `c4-pontryagin-indirect` Pontryagin 최대 원리와 간접법 | PMP 의 1차 필요조건 **[D3]**; 해밀토니안 보존·수반 방정식 **[D2]**; 슈팅의 민감도 폭발 **[D2]** | `kalman1960-optimal-control`, `betts1998-survey` | AA203 노트, UA ch.10 | R2: 2D 브라키스토크론/최소 시간 문제를 간접법으로 풀고, 초기 추정 민감도를 도표화 |
| `c4-dp-lqr-lqg` 동적 계획법·LQR·LQG | Bellman 방정식 **[D3]**; LQR 의 세 가지 유도(DP·PMP·변분) **[D3]**; Riccati 수렴과 안정성 **[D3]**; LQG 분리 정리 **[D2]** | `athans1971-lqg`, `kalman1960-optimal-control` | UA ch.7–8, AA203 W4–5 | R1: 이산 LQR 이득이 Riccati 반복·고유값 해법과 1e-10 이내 일치, 폐루프 극점이 단위원 내부 |
| `c4-ilqr-ddp` iLQR/DDP 와 정규화 | DDP 의 2차 전개와 수렴 차수 **[D3]**; 정규화·merit function·선탐색의 필요성 **[D2]**; 상태 제약 처리의 한계 **[D2]** | `mayne1966-ddp`, `tassa2012-ilqr` | UA ch.10.3, 16-745 W6 | R2: 카트폴 스윙업을 iLQR 로 해결, 비용 단조 감소와 토크 한계 만족(수용 기준: 20반복 내 수렴) |
| `c4-direct-collocation-sqp` 직접법·collocation·SQP | 직접 전사(transcription)의 희소 구조 **[D2]**; Hermite–Simpson 의 차수 **[D2]**; SQP 와 KKT 의 관계, 2차 수렴 **[D3]** | `hargraves1987-collocation`, `betts1998-survey` | NW ch.18, UA ch.10.2 | R2: 아크로봇 스윙업을 직접법으로 풀고 동역학 제약 위반 < 1e-6, iLQR 해와 비용 비교 |
| `c4-mpc` MPC | 재귀적 실현가능성과 종단 집합 **[D3]**; Lyapunov 기반 안정성 **[D3]**; 명시적 MPC 의 구간 선형 해 **[D2]**; 실시간 반복(RTI) **[D1]** | `rawlings2017-mpc-theory`, `diehl2009-rti` | AA203 W6, 16-745 W5 | R2: 선형 MPC 를 QP 로 구현, 종단 비용·제약 유무에 따른 안정 영역 차이를 수치로 보임 |
| `c4-contact-implicit-hybrid` 접촉·하이브리드 궤적 최적화 | 상보성 제약의 비볼록성과 LICQ 실패 **[D3]**; through-contact 전사 **[D2]**; 모드 스케줄과 살토(saltation) 행렬 **[D2]** | `posa2014-contact-implicit`, `howell2019-altro` | UA ch.17, 16-745 W10 | R3: Posa 2014 의 접촉 궤적(공 던지기/보행 1보)을 축소 규모로 재현, 상보성 잔차 < 1e-5 |
| `c4-robust-stochastic-oc` 강건·확률 최적 제어 | HJB/HJI 와 도달가능성(reachability) **[D3]**; minimax DDP **[D2]**; iLQG·불확실성 전파 **[D2]**; 튜브 MPC **[D1]** | `mitchell2005-hji-reachability` | AA203 W5, 16-745 W11–12 | R2: 2D 계의 도달가능 집합을 레벨셋으로 계산, 몬테카를로 궤적이 집합 안에 있음을 확인 |

**열린 문제**: 접촉이 있는 계의 전역 최적성(복잡도와 인증); 실시간성과 강건성의 동시 보장;
학습 모델 오차 하에서의 MPC 성능 보증; 긴 지평선·고차원에서 DDP 계열의 확장성.

### C5 상태 추정 (state estimation on manifolds) — 6레슨
근거: CMU 16-833(효율적 확률 추론), MIT 16.485 L16–30(manifold 최적화·인자 그래프·강건 추정),
Barfoot SER 전권, UPenn ESE 650 M1.

| 레슨 | 유도해야 할 핵심 결과 | 필독 | 교재 | 재현 과제 |
|---|---|---|---|---|
| `c5-factor-graphs-map` 인자 그래프와 MAP | 필터링에서 평활(smoothing)로의 전환 **[D2]**; MAP = 비선형 최소제곱 **[D3]**; 가우시안 소거와 Schur 보완 **[D3]** | `dellaert2017-factor-graphs`, `dellaert2006-square-root-sam` | SER ch.3–4, 16-833 | R2: 1D/2D 포즈 그래프를 GN 으로 풀고 조밀 해와 1e-9 이내 일치 |
| `c5-sparsity-isam` 희소성과 증분 추론 | 변수 순서와 fill-in **[D3]**; Bayes tree 와 iSAM2 의 증분 재선형화 **[D2]**; 주변화(marginalization) 가 만드는 조밀화 **[D2]** | `kaess2012-isam2`, `rose1976-vertex-elimination`, `carlevaris-bianco2014-node-removal` (권장 `yannakakis1981-min-fill-in`, `lipton1979-nested-dissection`, `kaess2008-isam`) | SER ch.3.3, 16-833 | R2: 증분 해법과 배치 해법의 해가 1e-6 이내 일치하면서 갱신 비용이 $O(1)$ 수준임을 측정 |
| `c5-manifold-estimation` 매니폴드 위 추정 | on-manifold GN·retraction **[D3]**; 불변 EKF 와 군 아핀 계의 오차 동역학 **[D3]**; 불확실성의 좌/우 표현 **[D2]** | `barrau2017-invariant-ekf`, `sola2018-micro-lie-theory`, `absil2008-manifold-opt` (권장 `hartley2020-contact-inekf`) | SER ch.7–8 | R2: $SE(3)$ 추정에서 표준 EKF 와 불변 EKF 의 일관성(NEES)을 비교, 불변형이 더 일관됨을 확인 |
| `c5-imu-preintegration` IMU 선적분과 관성 융합 | IMU 운동학과 선적분 측정 모델 **[D3]**; 바이어스 재선형화의 1차 보정 **[D2]**; 관성-시각 융합의 척도 관측가능성 **[D2]** | `forster2017-preintegration`, `lupton2012-preintegration`, `martinelli2012-closed-form-scale` (권장 `qin2018-vins-mono`, `mourikis2007-msckf`) | SER ch.9 | R2: 시뮬레이션 IMU 로 선적분 계수를 계산해 조밀 적분과 1e-6 이내 일치, 바이어스 보정 항의 1차 정확도 확인 |
| `c5-observability-consistency` 관측가능성과 일관성 | 비선형 관측가능성(Lie 미분 랭크) **[D3]**; VIO 의 불관측 방향(4-DOF) **[D3]**; EKF-SLAM 의 비일관성과 FEJ **[D2]** | `huang2010-fej`, `li2013-vio-observability`, `hermann1977-observability` (권장 `hesch2014-vio-observability`, `cadena2016-slam-survey`) | SER ch.5 | R1: VIO 선형화 계의 영공간 차원을 수치 랭크로 확인(= 4), FEJ 적용 시 보존됨을 보임 |
| `c5-robust-global-estimation` 강건·전역 추정 | M-estimator 와 IRLS, 영향 함수 **[D3]**; 전역 최적 포즈 그래프(SE-Sync) 의 볼록 완화와 타이트성 **[D2]**; 점군 정합의 인증(TEASER) **[D2]** | `rosen2019-se-sync`, `yang2021-teaser`, `sunderhauf2012-switchable` (권장 `carlone2015-lagrangian-duality`, `fischler1981-ransac`) | SER ch.5.3 | R3: 이상치 20% 포즈 그래프에서 강건 커널·SE-Sync 결과를 비교, 강건형의 ATE 가 2배 이상 개선됨을 확인 |

**열린 문제**: 비볼록 SLAM 의 전역 최적성 인증 범위; 학습 기반 프런트엔드의 불확실성 정량화;
장기 운용에서 지도 표현의 수명·압축; 밀집·뉴럴 표현과 확률 추론의 결합.

### C6 동작 계획 이론 (motion planning theory) — 7레슨
근거: **CMU 16-782 전체**, MIT 16.410, LaValle PA, UA ch.12.

| 레슨 | 유도해야 할 핵심 결과 | 필독 | 교재 | 재현 과제 |
|---|---|---|---|---|
| `c6-cspace-complexity` 구성공간과 복잡도 | C-space 위상과 장애물 사상 **[D2]**; 일반 운동 계획의 PSPACE-hardness **[D2]**; 피아노 운반 문제의 대수적 해법 **[D1]** | `reif1979-complexity`, `canny1988-complexity` | PA ch.3–4,6 | R1: 2-링크 팔의 C-space 장애물을 격자로 계산하고 위상(구멍 수)을 확인 |
| `c6-combinatorial-gcs` 조합적 계획과 볼록 분해 | 셀 분해의 완전성 **[D3]**; 가시성 그래프 최적성 **[D2]**; 측지 볼록 집합 그래프(GCS)의 혼합정수 완화 **[D2]** | `lozanoperez1979-visibility`, `marcucci2023-gcs`, `marcucci2024-spp-gcs` | PA ch.6 | R2: 다각형 환경에서 가시성 그래프 최단경로를 구현, 샘플링 해보다 짧음을 확인 |
| `c6-sampling-completeness` 샘플링 기반과 확률적 완전성 | PRM/RRT 의 확률적 완전성 증명 **[D3]**; 확장 실패 확률의 지수 감소 **[D3]**; 좁은 통로와 $\epsilon$-good 가정 **[D2]** | `kavraki1996-prm`, `lavalle2001-rrt` | PA ch.5 | R2: RRT 를 구현해 좁은 통로 폭 대비 성공률 곡선을 그림(이론 경향과 일치) |
| `c6-asymptotic-optimality` 점근 최적성 | RRT* 의 점근 최적성과 연결 반경 $r_n \propto (\log n/n)^{1/d}$ **[D3]**; informed/BIT* 의 수렴 가속 **[D2]**; 차원의 저주 **[D2]** | `karaman2011-rrtstar`, `gammell2015-bitstar` | PA ch.5(비교) | R2: RRT 와 RRT* 의 비용 수렴 곡선을 500회 반복 평균으로 비교, RRT* 가 최적 비용에 수렴 |
| `c6-search-based-planning` 탐색 기반 계획 | A* 의 최적성·허용성 **[D3]**; weighted A* 의 $w$-준최적 한계 **[D3]**; ARA*/D* 의 일관성 복구 **[D2]**; Multi-Heuristic A* **[D2]** | `likhachev2003-ara`, `aine2016-mha` | 16-782 노트, PA ch.2 | R2: 격자 그래프에서 A*/weighted A*/ARA* 의 비용-시간 교환을 재현, 비용 ≤ $w\cdot C^*$ 확인 |
| `c6-kinodynamic-planning` 미분 제약·커널 계획 | 미분 제약 하 도달가능 집합과 조종(steering) **[D2]**; kinodynamic RRT* 의 최적성 조건 **[D2]**; 격자 그래프(lattice)와 운동 원시 **[D2]** | `webb2013-kinodynamic-rrtstar`, `pivtoraiko2009-lattice` | PA ch.13–14 | R2: 이중 적분기 kinodynamic RRT* 를 구현, 최적 비용의 1.1배 이내로 수렴 |
| `c6-tamp` TAMP (task and motion planning) | 기호-연속 결합의 결정가능성 문제 **[D2]**; 샘플링 기반 TAMP 의 완전성 조건 **[D2]**; 접촉 모드 열거의 폭발 **[D2]** | `garrett2021-tamp-survey`, `toussaint2015-lgp` | PA ch.2(비교), 16-782 | R3: 블록 쌓기 TAMP 를 축소 규모로 구현, 문제 크기 대비 탐색 노드 수 증가를 도표화 |

**열린 문제**: 고차원 접촉 풍부 환경의 완전·최적 계획; 학습 기반 샘플러의 보장; TAMP 의 확장성;
불확실성 하 계획(POMDP)과 실시간성의 공존.

### C7 지각과 3D 표현 (perception and 3D representations) — 6레슨
근거: **CMU 16-822**, **UZH/ETH 151-0632 Vision Algorithms** 전체, MIT 16.485 L11–15,
Stanford CS231A, TUM IN2228, MVG·CV 교재.

| 레슨 | 유도해야 할 핵심 결과 | 필독 | 교재 | 재현 과제 |
|---|---|---|---|---|
| `c7-two-view-geometry` 다시점 기하와 에피폴라 | 본질·기본 행렬의 유도와 자유도 **[D3]**; 8점·5점 알고리즘 **[D2]**; 삼각측량의 최적성과 편향 **[D3]** | `nister2004-five-point`, `longuet-higgins1981-essential` | MVG ch.9–11, CV ch.11 | R2: 8점·5점 알고리즘을 구현해 노이즈 대비 회전 오차를 비교(5점이 우수함을 확인) |
| `c7-bundle-adjustment` N-view 와 번들 조정 | 재투영 오차의 희소 정규방정식과 Schur 보완 **[D3]**; 게이지 자유도와 고정 방법 **[D2]**; 자기 보정의 가해성 **[D2]** | `triggs2000-bundle-adjustment`, `agarwal2010-rome` | MVG ch.18, SER ch.10 | R3: 공개 BAL 데이터셋 1개에서 BA 를 수렴시켜 보고된 최종 비용과 1% 이내 일치 |
| `c7-robust-fitting-ransac` 강건 적합과 RANSAC 이론 | RANSAC 반복 수 공식과 실패 확률 **[D3]**; 최소 표본 집합과 오염률 한계 **[D2]**; 전역 최적 정합의 분기한정 **[D2]** | `fischler1981-ransac`, `barath2020-magsac` | MVG ch.4.7, CV ch.8 | R1: 오염률 대비 필요한 반복 수를 실험으로 측정해 이론식과 10% 이내 일치 |
| `c7-learned-correspondence-slam` 학습 기반 대응과 SfM/SLAM | 미분가능 BA 와 학습 가중의 결합 **[D2]**; 특징 대응의 일반화 실패 모드 **[D2]**; 깊이·자세 동시 학습의 척도 모호성 **[D2]** | `teed2021-droid-slam`, `sarlin2020-superglue` | CV ch.11(비교) | R4(선택): 사전학습 DROID-SLAM 류를 TUM RGB-D 1개 시퀀스에 실행해 보고된 ATE 와 20% 이내 일치 — GPU 필요 |
| `c7-neural-fields-3dgs` 뉴럴 필드와 3D Gaussian splatting | 볼륨 렌더링 적분과 이산화 **[D3]**; 위치 인코딩의 스펙트럼 편향 **[D2]**; 3DGS 의 스플래팅·미분 가능 래스터화 **[D2]** | `mildenhall2020-nerf`, `kerbl2023-3dgs` | — | R4(선택): 소형 장면에서 NeRF/3DGS 를 학습해 보고된 PSNR 경향(3DGS 가 더 빠름)을 재현 — GPU 필요 |
| `c7-event-tactile-sensing` 이벤트 카메라와 촉각 센싱 | 이벤트 생성 모델과 대비 최대화 **[D2]**; 모션 보상의 최적화 형태 **[D2]**; 촉각 이미지에서 접촉 기하·힘 추정 **[D2]** | `gallego2020-event-survey`, `yuan2017-gelsight` | — | R2: 이벤트 스트림(공개 데이터)에서 대비 최대화로 각속도를 추정, GT 와 10% 이내 일치 |

**열린 문제**: 기하와 학습의 원리적 결합(언제 기하 제약이 손해인가); 뉴럴 표현의 불확실성과
실시간 지도; 대규모 장기 지도의 표현; 촉각·이벤트의 표준 벤치마크 부재.

### C8 의사결정·학습 이론 (decision making and learning theory) — 8레슨
근거: **Berkeley CS285 전체**, Stanford AA274B/CS237B, AA203 W7–10, CMU 16-831, UPenn ESE 650 M3,
UA ch.11,20–21, S&B.

| 레슨 | 유도해야 할 핵심 결과 | 필독 | 교재 | 재현 과제 |
|---|---|---|---|---|
| `c8-mdp-pomdp-bellman` MDP·POMDP 와 Bellman 최적성 | 수축 사상으로서의 Bellman 연산자와 유일 고정점 **[D3]**; 가치·정책 반복의 수렴률 **[D3]**; POMDP 의 신념 MDP 변환과 PWLC 가치함수 **[D2]** | `kaelbling1998-pomdp`, `blackwell1965-discounted-dp`, `smallwood1973-pomdp-pwlc` | S&B ch.3–4, PA ch.10–12 | R1: 가치 반복의 오차가 $\gamma^k$ 로 감소함을 수치로 확인(이론 상한 내) |
| `c8-policy-gradient` 정책 경사 정리 | 정책 경사 정리 **[D3]**; 기저선과 분산 감소의 불편성 **[D3]**; 자연 경사·TRPO 의 신뢰영역과 단조 개선 한계 **[D3]** | `sutton2000-policy-gradient`, `schulman2015-trpo`, `schulman2017-ppo` | S&B ch.13, CS285 W3,5 | R2: REINFORCE/기저선/PPO 를 CartPole 에 구현, 분산 감소와 표본 효율 차이를 5시드 평균으로 보임 |
| `c8-value-based-rl` 가치 기반 RL 과 함수 근사 | 선형 함수 근사에서 발산 예(Baird) **[D3]**; 수렴 조건(on-policy, 투영 Bellman) **[D2]**; 과대추정과 이중 Q **[D2]** | `baird1995-residual`, `tsitsiklis1997-td-function-approx`, `mnih2015-dqn`, `vanhasselt2016-double-q` | S&B ch.9–11 | R1: Baird 반례를 재현해 TD 가 발산하고 잔차 경사법은 수렴함을 보임 |
| `c8-model-based-world-models` 모델 기반 RL 과 세계 모델 | 모델 오차의 가치 오차 전파 한계(시뮬레이션 보조정리) **[D3]**; Dyna 류의 편향 **[D2]**; 잠재 공간 세계 모델의 학습 목표 **[D2]** | `kearns2002-near-optimal`, `janner2019-mbpo`, `hafner2023-dreamerv3` | S&B ch.8, CS285 W8 | R2: 간단한 모델 기반 롤아웃 길이를 바꿔 성능-편향 곡선을 재현 |
| `c8-imitation-learning` 모방학습과 공변량 이동 | BC 의 복합 오차 $O(\epsilon T^2)$ **[D3]**; DAgger 의 후회 한계 $O(\epsilon T)$ **[D3]**; IRL 의 모호성과 최대 엔트로피 해 **[D2]** | `ross2010-efficient-reductions`, `ross2011-dagger`, `ziebart2008-maxent-irl` | CS285 W1–2 | R2: BC 와 DAgger 를 같은 전문가로 학습해 지평선에 따른 오차 증가 차수를 실험으로 분리 |
| `c8-offline-rl` 오프라인 RL 과 분포 이동 | 외삽 오차와 보수성(pessimism)의 하한 보장 **[D3]**; 행동 정규화 vs 가치 보수성 **[D2]**; 오프라인 평가(OPE)의 분산 **[D2]** | `jin2021-pessimism`, `levine2020-offline-rl`, `kumar2020-cql` | CS285 W9 | R2: D4RL 류 소형 데이터셋에서 BC·CQL 을 비교해 데이터 품질에 따른 역전 현상을 재현 |
| `c8-control-as-inference` 제어로서의 추론 | 최대 엔트로피 RL 과 soft Bellman **[D3]**; 변분 추론과의 동등성 **[D3]**; MPPI·경로 적분 제어의 유도 **[D2]** | `levine2018-control-as-inference`, `haarnoja2018-sac`, `williams2017-mppi` | CS285 W6–7, UA ch.11 | R2: MPPI 와 iLQR 로 같은 과제를 풀어 비용·샘플 수 교환을 도표화 |
| `c8-generalization-sim2real` 일반화와 sim-to-real 이론 | 도메인 랜덤화의 암묵적 목적함수 **[D2]**; 분포 이동 하 일반화 한계 **[D2]**; 특권 학습·교사-학생의 정보 격차 **[D2]** | `tobin2017-domain-randomization`, `rajeswaran2017-epopt`, `chen2020-learning-by-cheating` | CS285 W13 | R2: 랜덤화 폭을 바꿔 보이지 않는 매개변수에서의 성능 곡선을 그림(과도 랜덤화의 손해 확인) |

**열린 문제**: 로봇 규모 데이터에서의 표본 복잡도 이론; 오프라인 RL 의 실기 보장; 평가의 재현성
(CS285 W13 이 "Challenges and Open Problems" 로 한 주를 쓰는 이유); 접촉·비매끄러운 동역학에서
정책 경사의 타당성.

## 6. Stage 2 — Specialization (택 1, 권장 2)

각 트랙 6레슨. 형식은 Stanford CS326(세션마다 논문 리뷰 + 튜토리얼 + 토론, 최종 산출물은 연구
제안서)을 차용한다([benchmark.md](benchmark.md) §2.5, §9-4). 코어와 달리 **필독 논문이 본문의 중심**이고
교재는 보조다.

### S1 SLAM·공간 지능 (SLAM and spatial AI) — 선수: C1, C5, C7
| 레슨 | 유도·분석해야 할 결과 | 필독 | 재현 과제 |
|---|---|---|---|
| `s1-vio-systems` VIO 시스템 해부 | 필터형(MSCKF)과 최적화형의 계산·정확도 교환 **[D2]**; 널공간 투영 기법 **[D3]** | `mourikis2007-msckf`, `qin2018-vins-mono` | R3: EuRoC 1개 시퀀스에서 공개 VIO 를 돌려 보고된 ATE 와 30% 이내 일치, 설정 변경의 영향 측정 |
| `s1-loop-closure-lifelong` 루프 폐쇄와 장기 운용 | 장소 인식의 정밀도-재현율 교환 **[D2]**; 거짓 루프의 파괴적 영향과 강건 백엔드 **[D2]**; 지도 희소화(sparsification) **[D2]** | `galvez-lopez2012-dbow2`, `cadena2016-slam-survey` | R3: 거짓 루프 비율을 주입해 ATE 붕괴 지점을 찾고 강건 커널로 완화됨을 보임 |
| `s1-dense-neural-slam` 밀집·뉴럴 SLAM | TSDF 융합의 가중 평균 유도 **[D2]**; 뉴럴 암시 표현의 증분 학습과 망각 **[D2]** | `newcombe2011-kinectfusion`, `sucar2021-imap` | R3: 소형 RGB-D 시퀀스에서 TSDF 재구성과 뉴럴 SLAM 의 메모리-정확도를 비교 |
| `s1-semantic-scene-graphs` 의미·객체 수준 SLAM | 객체 수준 인자와 데이터 연관의 모호성 **[D2]**; 3D 장면 그래프의 계층 추론 **[D2]** | `rosinol2021-kimera`, `salas-moreno2013-slampp` | R3: 객체 수준 SLAM 의 데이터 연관 오류율을 측정하고 기하 전용 대비 이득 확인 |
| `s1-certifiable-slam` 인증 가능 SLAM | SE-Sync 의 쌍대 완화와 타이트성 조건 **[D3]**; 최적성 인증서(certificate) 검사 **[D3]** | `rosen2019-se-sync`, `carlone2015-lagrangian-duality` | R3: 공개 포즈 그래프에서 완화 해의 인증서를 계산해 전역 최적임을 확인 |
| `s1-slam-benchmarking` 평가의 과학 | ATE/RPE 정의와 정렬(Umeyama) **[D3]**; 시퀀스 간 분산과 통계적 유의성 **[D2]** | `sturm2012-tum-rgbd`, `geiger2012-kitti`, `zhang2018-trajectory-eval` | R2: 평가 도구를 직접 구현해 공개 도구 결과와 1e-6 이내 일치, 시드·시퀀스 분산을 신뢰구간으로 보고 |

**열린 문제**: 전역 최적성의 실시간 인증; 학습 프런트엔드의 불확실성; 수십 년 규모 장기 지도;
동적·변형 환경의 SLAM 정식화.

### S2 조작·접촉 (manipulation and contact) — 선수: C1–C4, C6
| 레슨 | 유도·분석해야 할 결과 | 필독 | 재현 과제 |
|---|---|---|---|
| `s2-grasp-mechanics` 접촉 역학과 파지 안정성 | 마찰 원뿔과 force closure 판정 **[D3]**; 파지 품질 지표와 렌치 공간 **[D2]**; caging **[D2]** | `ferrari1992-grasp-quality`, `rodriguez2012-caging` | R2: 평면 물체의 force closure 를 LP 로 판정, 접촉점 수에 따른 가능 영역을 도표화 |
| `s2-contact-modes-dexterity` 접촉 모드와 외재적 손재주 | 접촉 모드 열거와 운동 제약 다면체 **[D2]**; 비파지 조작(pushing)의 limit surface **[D3]** | `lynch1996-pushing`, `chavan-dafle2014-extrinsic-dexterity` | R2: 준정적 밀기 모델을 구현해 실제 궤적 데이터(공개)와 경향 일치 확인 |
| `s2-tactile-contact-estimation` 촉각과 접촉 상태 추정 | 촉각 이미지에서 힘·기하 역문제의 가해성 **[D2]**; 접촉 입자 필터 **[D2]** | `yuan2017-gelsight`, `koval2015-contact-manifold-pf` | R2: 접촉 상태 추정에 입자 필터를 적용해 모드 모호성이 관측으로 해소되는 과정을 재현 |
| `s2-learned-grasping` 학습 기반 파지 | 파지 성공 확률 모델과 라벨 노이즈 **[D2]**; 시뮬레이션 라벨의 sim-to-real 격차 **[D2]** | `mahler2017-dexnet2`, `sundermeyer2021-contact-graspnet`, `fang2023-anygrasp` | R3: 사전학습 파지 모델을 공개 점군에 적용해 보고된 성공률 경향 재현 |
| `s2-generative-policies` 생성형 정책 | 확산 정책의 점수 기반 목적함수 **[D3]**; 행동 청크(action chunking)의 편향-분산 **[D2]**; flow matching 과의 관계 **[D2]** | `chi2023-diffusion-policy`, `zhao2023-act`, `black2024-pi0` | R3: Diffusion Policy 를 공개 소형 데이터셋에서 재학습해 BC 대비 성공률 우위를 재현 |
| `s2-planning-through-contact` 접촉을 통한 계획·제어 | 접촉 암시 MPC 의 실시간 완화 **[D2]**; GCS 기반 조작 계획의 볼록화 **[D2]** | `aydinoglu2024-contact-implicit-mpc`, `marcucci2023-gcs` | R3: 평면 밀기 과제에서 접촉 암시 MPC 를 축소 구현, 실시간 예산 내 해를 얻음 |

**열린 문제**: 접촉 모델 오차의 근본 한계; 손재주 조작의 일반화; 촉각의 표준 벤치마크 부재;
생성형 정책의 안전·검증.

### S3 보행·언더액추에이티드 (legged and underactuated) — 선수: C1–C4
| 레슨 | 유도·분석해야 할 결과 | 필독 | 재현 과제 |
|---|---|---|---|
| `s3-hybrid-limit-cycles` 하이브리드 동역학과 리미트 사이클 | 푸앵카레 사상과 주기 궤도 안정성 **[D3]**; 살토 행렬과 점프 선형화 **[D3]** | `grizzle2001-asymptotically-stable-walking` | R2: 수동 보행기(compass gait)의 푸앵카레 사상을 수치로 구성해 고정점과 고유값을 구함 |
| `s3-hzd-gait-generation` 영역 동역학(HZD)과 보행 생성 | 가상 제약과 HZD 축소 **[D3]**; 궤도 안정성의 축소 차원 판정 **[D2]** | `westervelt2003-hzd`, `ames2014-hzd-experimental` | R2: 2D 이족 모델에서 가상 제약을 설계해 안정 리미트 사이클을 수치로 확인 |
| `s3-centroidal-mpc` 중심 동역학과 MPC 보행 | 중심 동역학 유도와 ZMP·캡처 포인트 **[D3]**; 선형 MPC 로의 환원과 실현가능성 **[D2]** | `kajita2003-zmp-preview`, `dicarlo2018-convex-mpc` | R2: 선형 중심 MPC 를 구현해 외력 외란 후 캡처 포인트가 지지 다각형으로 복귀함을 보임 |
| `s3-whole-body-control` 전신 제어와 계층 QP | 계층적 널공간 투영의 우선순위 보존 **[D3]**; QP 실현가능성과 완화(slack) **[D2]** | `sentis2005-wbc`, `herzog2016-momentum-wbc` | R2: 다중 과제 WBC 를 QP 로 구현해 우선순위 역전이 없음을 수치로 검증 |
| `s3-locomotion-rl` 로코모션 RL | 특권 학습·교사-학생의 정보 비대칭 **[D2]**; 보상 설계와 과최적화 **[D2]**; 적응(RMA)의 잠재 매개변수 추정 **[D2]** | `lee2020-blind-locomotion`, `kumar2021-rma`, `miki2022-anymal-wild` | R4(선택): 소형 보행 환경에서 교사-학생 파이프라인을 축소 재현, 정성적 경향 일치 |
| `s3-dynamic-maneuvers` 거친 지형·동적 기동 | 접촉 일정 최적화와 모드 폭발 **[D2]**; 실기 평가 설계(시행 수·성공 기준) **[D2]** | `bledt2018-mit-cheetah`, `grandia2023-perceptive-locomotion` | R3: 공개 로그/데이터로 기동 성공률을 분석, 신뢰구간과 실패 모드 분류 |

**열린 문제**: 보행 RL 의 보장 부재; 접촉 일정의 전역 최적; 장기 신뢰성·고장 허용; 모델 기반과
학습의 원리적 결합.

### S4 로봇 학습·파운데이션 모델 (robot learning and foundation models) — 선수: C7, C8
| 레슨 | 유도·분석해야 할 결과 | 필독 | 재현 과제 |
|---|---|---|---|
| `s4-robot-data-scaling` 대규모 로봇 데이터와 스케일링 | 스케일링 법칙의 형태와 로봇 데이터에서의 붕괴 조건 **[D2]**; 데이터 혼합·리밸런싱 **[D2]** | `oxe2023-open-x-embodiment`, `kaplan2020-scaling-laws` | R2: 공개 데이터 하위집합 크기를 바꿔 성능-데이터 곡선을 측정, 포화 지점을 보고 |
| `s4-vla-architectures` VLA 아키텍처와 행동 표현 | 행동 토큰화의 양자화 오차 **[D2]**; 사전학습 전이의 조건 **[D2]**; 흐름/확산 헤드의 선택 근거 **[D2]** | `brohan2023-rt2`, `kim2024-openvla`, `black2024-pi0` | R3: OpenVLA 류를 소형 과제에 미세조정해 보고된 상대 경향 재현 |
| `s4-pretrained-representations` 사전학습 표현과 전이 | 표현 평가의 선형 프로빙 한계 **[D2]**; 시간 대조 목적함수 **[D2]** | `nair2022-r3m`, `majumdar2023-vc1` | R2: 동결 표현 3종 위에 동일 정책 헤드를 학습해 표현별 성능 차이를 5시드로 비교 |
| `s4-language-and-planning` 언어·계획 결합 | 계층 정책의 추상화 경계 **[D2]**; LLM 계획의 실현가능성 보장 부재 **[D2]** | `ahn2022-saycan`, `liang2023-code-as-policies` | R2: 기호 계획 + 저수준 정책의 실패 사례를 분류해 실패 원인 분포를 보고 |
| `s4-evaluation-science` 평가의 과학 | 실기 평가의 표본 수와 신뢰구간 **[D3]**; A/B 비교의 검정력 **[D2]**; 벤치마크 과적합 **[D2]** | `li2024-simpler`, `agarwal2021-deep-rl-at-the-edge` | R2: 성공률 차이를 검출하려면 몇 회 시행이 필요한지 검정력 분석으로 계산하고 공개 결과에 적용 |
| `s4-safety-ood` 안전·OOD·실패 모드 | 불확실성 정량화(앙상블·공형 예측)의 보장 **[D3]**; 중단(abstention) 정책의 비용 **[D2]** | `angelopoulos2021-conformal`, `sinha2022-system-level-ood` | R2: 공형 예측으로 행동 불확실성 구간을 만들고 목표 커버리지(90%)를 실측 확인 |

**열린 문제**: 로봇 데이터의 스케일링 한계; 평가 재현성; 일반화의 측정; 안전 보장과 대형 정책의 결합.

### S5 다중 로봇·필드 로보틱스 (multi-robot and field robotics) — 선수: C5, C6, C8
| 레슨 | 유도·분석해야 할 결과 | 필독 | 재현 과제 |
|---|---|---|---|
| `s5-graph-consensus` 그래프 이론과 합의 | 라플라시안 스펙트럼과 합의 수렴률 $\lambda_2$ **[D3]**; 시변·방향 그래프의 조건 **[D2]** | `olfati-saber2007-consensus`, `jadbabaie2003-coordination` | R1: 무작위 그래프에서 합의 수렴률이 $\lambda_2$ 와 비례함을 수치로 확인 |
| `s5-distributed-optimization` 분산 최적화·분산 SLAM | ADMM 수렴 **[D3]**; 분산 포즈 그래프의 블록 좌표 하강 **[D2]**; 통신-정확도 교환 **[D2]** | `boyd2011-admm`, `choudhary2017-distributed-slam` | R2: 2대 분산 포즈 그래프 최적화를 구현해 중앙집중 해와 1e-4 이내 일치 |
| `s5-multi-agent-planning` 다중 로봇 계획 | MAPF 의 완전성·최적성과 NP-hardness **[D3]**; CBS 의 최적성 증명 **[D3]**; 우선순위 계획의 불완전성 **[D2]** | `sharon2015-cbs`, `yu2013-mapf-complexity` | R2: CBS 와 우선순위 계획을 비교해 최적성·성공률 차이를 격자 크기별로 보임 |
| `s5-active-information-gathering` 능동 지각·정보 수집 | 상호정보 목적함수와 submodularity **[D3]**; 탐욕 알고리즘의 $(1-1/e)$ 보장 **[D3]** | `krause2008-submodular`, `atanasov2015-decentralized-active` | R2: 센서 배치 탐욕 해가 최적 대비 $(1-1/e)$ 이상임을 소규모 완전 탐색과 비교 |
| `s5-comms-constrained-estimation` 통신 제약과 분산 추정 | 지연·패킷 손실 하 추정 일관성 **[D2]**; 상관 무시의 과확신 **[D3]**; 공분산 교차(CI) **[D2]** | `julier1997-covariance-intersection` | R1: 상관을 무시한 융합이 NEES 과확신을 만들고 CI 가 보수적임을 수치로 확인 |
| `s5-field-deployment` 필드 배치와 장기 자율성 | 신뢰성 지표(MTBF)와 고장 모드 분석 **[D2]**; 실기 평가 설계 **[D2]** | `ebadi2022-darpa-subt`, `roucek2019-darpa-subt-system` | R2: 공개 필드 데이터/보고서에서 실패 모드를 분류하고 개선 우선순위를 근거와 함께 제시 |

**열린 문제**: 통신 제약 하 분산 추정의 일관성 보장; 대규모 군집의 확장성; 장기 필드 자율성의
신뢰성 공학; 이질적 팀의 과제 배분.

## 7. Stage 3 — 연구 실행

### R1 연구 방법론 (research methodology) — 6레슨
근거: Georgia Tech 구술시험 형식(3주 전 주제 배정 → 2페이지 서면 요약 → 15–20분 발표),
CMU Research Qualifier 4요소(Research Skills, Speaking, Writing, Teaching), CMU 16-745·
Berkeley CS287 의 학회 포맷 보고서, Stanford CS326 의 연구 제안서 + 동료 리뷰
([benchmark.md](benchmark.md) §7, §9-3).

| 레슨 | 산출물 | 핵심 내용 |
|---|---|---|
| `r1-literature-survey` 문헌 조사와 서베이 읽기·쓰기 | 주제 1개의 서베이 개요 + 논문 30편 분류표 | 검색 전략, 인용 네트워크 추적, 서베이의 분류 축 세우기, 1차/2차 자료 구분 |
| `r1-research-questions` 연구 질문과 가설 | 2페이지 연구 제안(GT 구술 형식) | 문제 정식화, 가설의 반증가능성, 기여 유형(이론·방법·시스템·분석), 범위 설정 |
| `r1-experiment-design` 실험 설계 | 실험 계획서 + ablation 표 | 독립·종속·교란 변수, ablation 설계, 베이스라인 공정성(튜닝 예산 동등), 사전 등록 |
| `r1-robotics-evaluation-statistics` 로보틱스 평가와 통계 | 평가 프로토콜 + 검정력 분석 | 지표 선택과 주장 정합성, 시드·시행 수, 신뢰구간, 다중비교, 효과크기, 실기 실험의 비용 |
| `r1-reproducibility-artifacts` 재현성과 아티팩트 | 재현 가능한 저장소(시드·환경·스크립트) | 환경 고정, 결정론, 데이터·코드 공개, 아티팩트 평가 기준, 라이선스 |
| `r1-paper-writing-review` 논문 작성과 리뷰 | 8페이지 초안 + 타인 논문 리뷰 1편 | 구조(문제→기여→방법→실험→한계), 그림 설계, 반론 대응, 리뷰어 관점, 연구 윤리 |

### R2 캡스톤 (capstone) — 3레슨
| 레슨 | 산출물 | 수용 기준 |
|---|---|---|
| `r2-capstone-survey` 서베이 | 선택 specialization 주제의 서베이 10–15페이지, 논문 40편 이상 분류 | 분류 축이 기존 서베이와 다른 관점을 하나 이상 제시; 모든 인용이 확인된 URL |
| `r2-capstone-reproduction` 재현 | 원 논문 1편의 R3 티어 재현 + 재현 보고서 | 보고된 주요 수치를 명시한 허용오차 안에서 재현하거나, **재현 실패 원인을 근거와 함께 규명** |
| `r2-capstone-contribution` 기여 | 워크숍 논문 형식 8페이지 초안 + 20분 구술 방어 | 명확한 1개 기여, 공정한 베이스라인, ablation, 한계 서술, 재현 가능한 코드 |

## 8. 기존 50레슨의 처분 (기존 `robotics-expert` 코스와의 관계)

**원칙**: 기존 코스는 **삭제하지 않는다**. 로보틱스 엔지니어 입문~중급 과정으로서 독립적 가치가
있고, 연구 트랙의 **로보틱스 선수 과정**이기도 하다(§1). 연구 트랙은 새 코스
(`curriculum/robotics-research`)이며, 겹치는 주제는 **같은 제목의 레슨을 다시 만들지 않고**
연구 수준으로 승격된 코어 레슨이 그 자리를 대신한다.

| 기존 모듈·레슨 | 처분 | 연구 트랙에서 대응되는 자리 |
|---|---|---|
| **M1** vectors-matrices · coordinate-transforms | 선수 유지 | R0-1 로 수치선형대수까지 확장 |
| **M1** rotation-representations | **승격·흡수** | `c1-so3-se3-exponential`, `c1-lie-group-derivatives` (리 군·지수 좌표로 재작성) |
| **M2** dh-parameters · forward-kinematics | 선수 유지 | — (DH 는 연구 트랙에서 쓰지 않고 PoE 로 대체: MR ch.4, MLS ch.3) |
| **M2** inverse-kinematics | **승격·흡수** | `c1-poe-analytic-ik` (Paden–Kahan 부문제·해 분기) |
| **M3** differential-drive | 선수 유지 | `c3-feedback-linearization` 의 비홀로노믹 절에서 재사용 |
| **M3** pid-control · path-following | 선수 유지 | — (연구 트랙의 입구는 Lyapunov·LQR) |
| **M4** sensor-models · filtering-basics | 선수 유지 | R0-5, C5-1 로 흡수 |
| **M4** camera-model-features | **승격·흡수** | `c7-two-view-geometry` (에피폴라·5점) |
| **M4** point-clouds-icp-ransac | **승격·흡수** | `c7-robust-fitting-ransac`, `c5-robust-global-estimation`(TEASER) |
| **M4** object-detection-intro | 선수 유지 | — (연구 트랙은 학습 기반 대응·3D 표현으로 진입) |
| **M8** ros2-concepts-distros … reference-robot-code (5) | **연구 트랙 비포함** | 엔지니어 코스에 잔류. 연구 트랙은 도구를 전제로만 두고 레슨을 쓰지 않는다 |
| **M5** bayes-filter · kalman-filter-ekf · particle-filter-mcl · odometry-sensor-fusion · occupancy-grid-scan-matching | 선수 유지 | C5 가 필터링→평활(인자 그래프)로 전환해 상위를 담당 |
| **M5** graph-slam-slam-toolbox | **승격·흡수** | `c5-factor-graphs-map`, `c5-sparsity-isam` (도구 읽기 → 이론·증명) |
| **M6** configuration-space-graph-search | **승격·흡수** | `c6-cspace-complexity`, `c6-search-based-planning` |
| **M6** sampling-based-planning | **승격·흡수** | `c6-sampling-completeness`, `c6-asymptotic-optimality` (완전성·최적성 증명) |
| **M6** costmap-global-planning · local-planning-dwa-mppi | 선수 유지 | MPPI 는 `c8-control-as-inference` 에서 경로 적분 제어로 재유도 |
| **M6** path-smoothing-trajectory | 선수 유지 | `c4-direct-collocation-sqp` 가 상위를 담당 |
| **M6** nav2-architecture-behavior-trees | **연구 트랙 비포함** | 엔지니어 코스에 잔류 |
| **M7** jacobian-singularity | **승격·흡수** | `c1-twists-wrenches-adjoint`, `c2-constrained-dynamics`(조작 공간 관성) |
| **M7** manipulator-dynamics-torque-control | **승격·흡수** | C2 전체(공간 벡터·RNEA·CRBA/ABA) |
| **M7** trajectory-generation | 선수 유지 | C4 가 상위를 담당 |
| **M7** grasping-impedance-control | **승격·흡수** | `c3-passivity-impedance`, `s2-grasp-mechanics` |
| **M7** manipulator-motion-planning | 선수 유지 | C6 가 상위를 담당 |
| **M7** moveit2-reading | **연구 트랙 비포함** | 엔지니어 코스에 잔류 |
| **M9** mdp-decision-making | **승격·흡수** | `c8-mdp-pomdp-bellman` (수축 사상·수렴 증명) |
| **M9** robot-learning-overview | 선수 유지 | — |
| **M9** reinforcement-learning-basics | **승격·흡수** | `c8-policy-gradient`, `c8-value-based-rl` |
| **M9** imitation-learning-bc-dagger | **승격·흡수** | `c8-imitation-learning` (복합 오차·후회 한계 증명) |
| **M9** sim-to-real-domain-randomization | **승격·흡수** | `c8-generalization-sim2real` |
| **M9** vla-foundation-models | **승격·흡수** | `s4-vla-architectures`, `s4-robot-data-scaling` |
| **M9** datasets-benchmarks-evaluation | **승격·흡수** | `r1-robotics-evaluation-statistics`, `s4-evaluation-science`, `s1-slam-benchmarking` |
| **M10** system-architecture-requirements … career-community-portfolio (6) | 선수 유지 / 일부 비포함 | 엔지니어 코스에 잔류. 연구 트랙의 대응물은 R1·R2(연구 방법론·캡스톤)이며 `realtime-safety-reliability` 는 `s3`/`s4-safety-ood` 에서 연구 수준으로 다시 다룬다 |

**삭제 대상: 없음.** 기존 50레슨 중 "틀렸으니 버려야 하는" 것은 조사에서 나오지 않았다. 다만 위
표의 **승격·흡수 16개**는 연구 트랙에서 다시 쓰이므로, 엔지니어 코스 쪽 레슨에는 "연구 트랙의
어느 레슨으로 이어지는지" 링크를 추가하는 것이 좋다(선택 작업).

## 9. 구현 메모 (스키마·디렉터리)

- 새 코스 디렉터리: `curriculum/robotics-research/` (`course.yaml` + 19개 모듈 디렉터리).
  모듈 `level: 연구` 는 `Level` 리터럴 확장이 필요하다([lesson-standard.md](lesson-standard.md) §11-4).
- 레슨 id 는 코스 전체에서 유일해야 하므로(CONTENT_MODEL.md) 이 설계의 접두어 `r0-/c1-…c8-/s1-…s5-/r1-/r2-`
  를 그대로 쓴다. 기존 코스의 id(`m1-…`)와 충돌하지 않는다.
- 필독 논문은 `curriculum/robotics-research/papers.yaml` 레지스트리 + 레슨 `papers[]` 참조
  ([lesson-standard.md](lesson-standard.md) §11-1). 이 설계의 `필독` 열 값이 그 id 다.
- `prerequisites` 는 레슨 id 만 받으므로, 모듈 간 선수 관계(§2 DAG)는 각 모듈 첫 레슨이 이전
  모듈 마지막 레슨을 가리키는 방식으로 표현한다. 외부 선수지식(§1)은 R0 레슨 + 본문
  `## 전제와 기호` 에 쓴다.
- `estimated_minutes` 는 레슨당 300–900 범위를 쓴다. `difficulty` 는 트랙 내 상대값(3–5).

## 10. 열린 설계 결정 (사용자 확인 필요)

1. **specialization 개수**: 5개로 제안했다. 4개로 줄이려면 S5(다중 로봇·필드)가 1순위 후보이고,
   6개로 늘리려면 "안전·형식 검증(safety and formal methods)"이 다음 후보다.
2. **R0(수학 브리지)을 이 코스에 둘지, 별도 코스로 뺄지**: 현재는 연구 코스 안의 선택 모듈로 두었다.
3. **기존 50레슨에 "연구 트랙으로 이어짐" 링크를 추가할지** (§8 마지막 문단).
4. **97레슨을 한 번에 쓸지, 단계적으로 쓸지**: 권장은 C1 → C4 → C5 → C6 → C2 → C3 → C7 → C8 →
   S* → R* 순의 단계적 작성(코어 51레슨이 1차 목표).
