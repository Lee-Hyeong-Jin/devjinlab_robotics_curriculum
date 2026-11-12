# 웹 성능: Lighthouse 와 그 대신 측정한 것

PRD §7("성능 / 서버")은 **페이지 LCP 2.5초 이내**를 요구한다. `.claude/rules/engineering.md` 는
`web/` 이 생기는 Phase 2 부터 axe 접근성 CI 를 적용한다고 적고 있고(이미 `e2e/smoke.spec.ts` 에서
돌고 있다), Lighthouse 는 아직 파이프라인에 없다.

## Lighthouse 는 돌리지 못했다 (사유)

이 환경에 Lighthouse 가 없다:

```
$ command -v lighthouse        # 없음
$ ls web/node_modules/.bin | grep -i lighthouse   # 없음
$ npm ls lighthouse            # └── (empty)
```

설치하려면 `npm i -D lighthouse`(또는 `@lhci/cli`)로 **의존성을 새로 추가**해야 한다. 그 결정은
라이선스·유지 상태를 PR 설명에 적는 절차를 거쳐야 하고(engineering.md "의존성 추가는 최소화한다"),
도구를 넣을 자리는 CI 이므로 이 세션의 과제 범위를 넘는다. 그래서 **생략하고 사유를 기록한다.**

## 대신 측정한 것: Core Web Vitals (LCP / FCP / CLS)

Lighthouse 의 점수는 못 냈지만, PRD 가 실제로 요구하는 **LCP** 는 이미 설치된 Playwright
Chromium 으로 직접 잴 수 있다. 측정 방법: 페이지마다 새 브라우저 컨텍스트(캐시 없음)를 열고,
탐색 **전에** `PerformanceObserver`(`buffered: true`)로 `largest-contentful-paint` 와
`layout-shift` 를 구독한 뒤 load + 700 ms 지점의 값을 읽는다. 경로마다 5회 돌려 중앙값과 최악값을
적는다.

### 2026-11-12 (2) — 코스 2개, 연구 트랙 화면 포함

연구 트랙 코스와 코스 전환 탭이 생긴 뒤 다시 쟀다. 이번에는 **기계가 바빴다**(load average 약 20,
CPU 12개), 그래서 (1) 보다 전체적으로 2–5배 느리다. 두 절을 서로 비교하면 안 된다.

| 경로 | FCP(중앙) | LCP(중앙) | LCP(최악) | CLS(최악) |
|---|---:|---:|---:|---:|
| `/` | 260 ms | **260 ms** | 300 ms | 0.000 |
| `/roadmap` | 260 ms | **532 ms** | 624 ms | 0.000 |
| `/roadmap?course=robotics-research` | 212 ms | **212 ms** | 588 ms | 0.000 |
| `/modules/c1-rigid-body-geometry-lie-groups` | 244 ms | **244 ms** | 644 ms | 0.000 |
| `/lessons/c1-so3-se3-exponential` | 128 ms | **128 ms** | 372 ms | 0.000 |
| `/lessons/m1-coordinate-transforms` | 176 ms | **560 ms** | 616 ms | 0.000 |

- **목표는 여전히 크게 밑돈다.** 최악 LCP 644 ms 로 2.5 s 목표의 1/4 다. 바쁜 기계에서조차 그렇다.
- **CLS 는 계속 0 이다.** 코스 탭이 늘어났지만 레이아웃은 전부 서버에서 확정돼 온다.
- **연구 트랙 레슨이 가장 빠르다**(LCP 128 ms). 본문이 아직 짧기 때문이고, 집필이 진행되면
  `m1-coordinate-transforms`(560 ms) 쪽에 가까워질 것으로 본다.

### 2026-11-12 (1) — 코스 1개

환경: 개발용 노트북(Linux x86_64), `next start` 프로덕션 빌드, API 는 local 모드 SQLite,
**localhost·데스크톱·네트워크 스로틀 없음**, 같은 기계에서 다른 작업이 동시에 돌고 있었다.

| 경로 | FCP(중앙) | LCP(중앙) | LCP(최악) | CLS(최악) |
|---|---:|---:|---:|---:|
| `/` | 60 ms | **60 ms** | 88 ms | 0.000 |
| `/roadmap` | 76 ms | **76 ms** | 108 ms | 0.000 |
| `/resources` | 100 ms | **100 ms** | 128 ms | 0.000 |
| `/modules/m1-math-physics` | 72 ms | **72 ms** | 96 ms | 0.000 |
| `/lessons/m1-coordinate-transforms` | 72 ms | **416 ms** | 420 ms | 0.000 |

### 읽기

- **목표 대비 여유가 크다.** 가장 느린 레슨 화면도 LCP 420 ms 로 2.5 s 목표의 6분의 1 수준이다.
- **CLS 는 0 이다.** 레이아웃이 전부 서버에서 확정돼 오고, 폰트를 외부에서 받아오지 않기 때문이다.
- **레슨 화면만 FCP 와 LCP 가 벌어진다**(72 ms → 416 ms). 본문이 가장 큰 요소이고, KaTeX MathML 과
  하이라이트가 들어간 트리를 그리는 시간이다. 그래도 목표의 한참 아래다.

### 이 수치를 믿을 수 있는 범위

- **실제 사용자보다 훨씬 빠른 조건이다.** localhost(RTT 0), 데스크톱 CPU, 스로틀 없음. Lighthouse
  의 기본 모바일 프로필(4x CPU 스로틀 + Slow 4G)은 이보다 몇 배 느린 값을 낸다. 공개 배포
  (<https://learnrobotics.devjinlab.com>)에서는 네트워크와 TLS 핸드셰이크가 더해진다.
- 그래서 위 표는 "목표를 통과한다"의 근거가 아니라 **회귀 감시용 기준선**이다. 공개 주소에서의
  실제 LCP 는 Lighthouse 또는 현장 데이터(RUM)로 따로 재야 한다.
- 점수(Performance / Accessibility / Best Practices / SEO)는 Lighthouse 만 낸다. 접근성은
  axe 로 별도 보장된다(`e2e/smoke.spec.ts`, AC-A11Y.1).

## Lighthouse 를 넣을 때

1. 의존성 추가: `npm i -D lighthouse` 또는 `@lhci/cli`(둘 다 Apache-2.0). PR 설명에 라이선스와
   유지 상태를 적는다.
2. `web/package.json` 에 스크립트를 넣는다:

   ```json
   "lighthouse": "lighthouse http://127.0.0.1:3000/ --preset=desktop --output=json --output-path=./lighthouse.json --chrome-flags=\"--headless\""
   ```

3. CI 는 e2e smoke 레그(`.github/workflows/ci.yml`)가 이미 API + web 을 띄우므로 거기에 붙인다.
   예산은 LCP 2.5 s(PRD §7), CLS 0.1, TBT 300 ms 로 시작하고, `--preset=desktop` 과 모바일
   기본값 중 어느 쪽을 게이트로 삼을지 먼저 정한다(모바일이 더 엄격하다).
4. 결과는 이 문서에 날짜 절로 덧붙인다. 위 표는 덮어쓰지 않는다 — 측정 방식이 다르면 비교 대상이
   아니다.

API 쪽 수치는 [perf-baseline.md](perf-baseline.md) 에 있다.
