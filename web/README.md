# web/ — 로보틱스 전문가 코스 플랫폼 웹 프론트엔드

Next.js 15 (App Router) + React 19 + TypeScript strict. 설계 근거는
`docs/adr/0008-web-nextjs.md`, 구현 규칙은 `docs/architecture/frontend.md`,
수용 기준은 `docs/PRD.md` 부록 C.6·C.7 이다.

이 앱은 **코어(Python)를 import 하지 않는다.** 모든 데이터는 API 에서 온다.

## 실행

```bash
# 1. API 서버 (레포 루트에서)
uv run rc api serve

# 2. 웹 (이 디렉터리에서)
npm ci
npm run dev            # http://localhost:3000
```

## 명령

| 명령                              | 하는 일                                                    |
| --------------------------------- | ---------------------------------------------------------- |
| `npm run dev`                     | 개발 서버                                                  |
| `npm run build` / `npm start`     | 프로덕션 빌드 / 서버 (정적 export 아님)                    |
| `npm run lint`                    | ESLint (next/core-web-vitals, next/typescript, jsx-a11y)   |
| `npm run typecheck`               | `tsc --noEmit`                                             |
| `npm test`                        | Vitest (단위 + 컴포넌트)                                   |
| `npm run e2e`                     | Playwright 스모크 + axe-core (API·웹 서버 필요)            |
| `npm run format` / `format:check` | Prettier                                                   |
| `npm run api:types`               | `docs/api/openapi.yaml` → `src/lib/api/schema.d.ts` 재생성 |

게이트: `npm run lint && npm run typecheck && npm test && npm run build`.

## 환경 변수

`.env.local` 에 넣는다(하네스가 `.env*` 쓰기를 막으므로 예시 파일 대신 여기에 적는다).
모두 서버 전용이며 브라우저로 나가지 않는다.

| 변수                   | 기본값                  | 뜻                             |
| ---------------------- | ----------------------- | ------------------------------ |
| `RC_API_BASE_URL`      | `http://127.0.0.1:8000` | API 서버 주소 (뒤 `/` 없이)    |
| `RC_DEFAULT_COURSE_ID` | `robotics-expert`       | 대시보드·로드맵이 보여 줄 코스 |
| `RC_API_TIMEOUT_MS`    | `10000`                 | API 요청 타임아웃 (ms)         |

## 구조

```
src/
  app/            라우트 (App Router). 모든 화면은 서버 컴포넌트가 기본
  components/     공용 컴포넌트 (Figma 노드 매핑은 각 파일 주석)
  i18n/           next-intl 설정과 로케일 해석 (ko 기본, en)
  lib/api/        생성된 스키마 타입 + fetch 래퍼 + 화면별 로더
  lib/markdown/   레슨 본문 렌더 파이프라인 (remark/rehype)
  lib/            포맷터, 테마, 진도 파생 계산
  test/           테스트 헬퍼
e2e/              Playwright 스모크 + 접근성
messages/         ko.json, en.json (키 누락·미사용 검사는 테스트가 함)
```

### 라우트와 API

`docs/architecture/frontend.md` §2 의 매핑을 따른다. 1차 구현 범위:

| 라우트                           | 주 API                                                          |
| -------------------------------- | --------------------------------------------------------------- |
| `/` 대시보드                     | `GET /api/v1/progress/status`                                   |
| `/roadmap`                       | `GET /api/v1/roadmap` (아래 참고)                               |
| `/modules/[moduleId]`            | `GET /api/v1/modules/{id}`, `GET /api/v1/progress/lessons`      |
| `/modules/[moduleId]/[lessonId]` | `GET /api/v1/lessons/{id}`, `GET /api/v1/progress/lessons/{id}` |
| `/resources`                     | `GET /api/v1/resources`                                         |
| `/login`                         | (P2-2 인증 API 이후) 현재는 401 리다이렉트 대상 자리표시자      |

로그인·회원가입·프로필·관리자·퀴즈·복습·검색·리포트 화면은 2차다.

## 알아 둘 구현 결정

- **타입은 손으로 쓰지 않는다.** API 모양은 전부 `src/lib/api/schema.d.ts`
  (생성물, 커밋됨) 에서 나온다. 계약이 바뀌면 `npm run api:types` 를 다시 돌린다.
  정본은 `docs/api/openapi.yaml`; 실제 구현과의 차이는 `tests/snapshots/openapi.json`
  과 비교하면 보인다.
- **색은 CSS 변수만 쓴다.** `src/app/globals.css` 의 토큰 22개가 Figma `Tokens`
  컬렉션과 1:1 이고 Light/Dark 값을 모두 가진다. ESLint 가 코드 안의 hex 리터럴을
  막는다. Tailwind 유틸(`bg-surface`, `text-muted` …)은 `@theme inline` 로 토큰에
  묶여 있다.
- **레슨 본문은 Markdown 으로 온다**(`content_format: "markdown"`). 변환은
  `src/lib/markdown/render.tsx` 가 하고, 결과는 React 트리라서
  `dangerouslySetInnerHTML` 을 쓰지 않는다.
  - KaTeX 는 **MathML 모드**(`output: 'mathml'`)다. 그래야 sanitizer 에
    `style` 속성을 열어 줄 필요가 없고 KaTeX CSS 도 클라이언트로 안 나간다.
  - 코드 하이라이트는 `rehype-pretty-code`(인라인 style) 대신
    `rehype-highlight`(클래스)를 쓰고, `hljs-*` 클래스를 디자인 토큰으로 칠한다.
  - 두 선택 모두 `docs/architecture/frontend.md` §5 의 제안과 다르다. 이유는 위와
    같고, 바꿔야 하면 sanitize 스키마(`src/lib/markdown/sanitize.ts`)가 같이 바뀐다.
- **로드맵 폴백.** 계약의 `GET /api/v1/roadmap` 이 아직 구현되지 않아서
  `src/lib/api/queries.ts` 가 `/courses/{id}` + 각 모듈 + `/progress/status` 로 같은
  모양을 합성한다. 엔드포인트가 응답하기 시작하면 폴백은 지워도 된다.
- **인증.** 브라우저는 `sid` 쿠키(HttpOnly)를 쓰고 프론트엔드 JS 는 토큰을 보관하지
  않는다. 서버 컴포넌트 fetch 는 요청 쿠키를 그대로 넘기고, 변경 요청에는
  `X-CSRF-Token` 을 더블 서밋한다. 401 이면 `/login?next=<현재 경로>` 로 보내는데,
  현재 경로는 `src/middleware.ts` 가 넣는 `x-current-path` 헤더에서 읽는다.
  **권한 판단은 API 가 한다** — 화면을 숨기는 것으로 보호하지 않는다(AC-WEB.4).

## 접근성 기준선

랜드마크(`header`/`nav`/`main`/`aside`), 건너뛰기 링크, 2px accent 포커스 링,
표 `caption` + `th scope`, 진행률 `role="progressbar"` + `aria-valuenow`,
상태는 색만으로 전달하지 않음(점 + 글자 + 🔒), `prefers-reduced-motion` 존중,
로드맵 그래프의 텍스트 대안 표(AC-A11Y.3). axe-core 검사는 `npm run e2e` 에 있다.
