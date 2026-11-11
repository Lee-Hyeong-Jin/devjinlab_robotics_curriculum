# 0004. 정적 사이트: 생성한 Markdown + MkDocs Material, KaTeX 동봉

- 상태: accepted
- 날짜: 2026-11-11
- 관련: docs/PRD.md FR-2, FR-3, FR-6, FR-7; docs/platform-design.md §2.2–2.3; harness/roadmap.yaml P1-5

## 맥락

"로보틱스 전문가 코스" 하나를 단계(기초→중급→고급)별로 읽고, 개인 진도와 레슨별 공부법·자료를
쉽게 보는 화면이 필요하다. 제약: 웹 서버 없음(읽기 전용, 쓰기는 CLI), 오프라인 동작,
Python 단일 스택, 수식(KaTeX)·코드 하이라이트 렌더링, 라이트/다크 모드.

## 선택지

| 선택지 | 장점 | 단점 |
|---|---|---|
| A. 직접 HTML 템플릿(Jinja2) | 의존성 최소 | 내비게이션·검색·테마·다크 모드를 전부 직접 구현 |
| B. MkDocs + Material, 페이지는 Markdown으로 생성 | 내비·검색·다크 모드·코드 하이라이트 기본 제공, 레슨 본문을 그대로 사용 | 런타임 의존성 3개, 빌드 시 임시 프로젝트 생성 |
| C. 웹 앱(FastAPI 등) | 실시간 진도 | 서버 운영 필요, 범위 밖(사용자 결정) |

## 결정

B. `rc site build`가 콘텐츠와 진도 저장소에서 `mkdocs.yml` + `docs/`(대시보드, 로드맵,
모듈·레슨, 자료실)를 f-string으로 생성하고 MkDocs Python API로 빌드한다.

- 레슨 본문은 그대로 쓰되, 맨 앞 H1은 페이지 제목과 겹치므로 빼고 `## 이 단계 공부법` 절은
  본문 뒤의 강조 콜아웃(admonition)으로 옮긴다.
- 수식: `pymdownx.arithmatex`(generic) + **KaTeX 0.16.11을 패키지에 동봉**
  (`src/robotics_curriculum/site/assets/katex/`, woff2 글꼴만, MIT). CDN을 쓰지 않는다.
- `theme.font: false`로 Google Fonts 요청을 막고, `use_directory_urls: false`로 `.html` 링크를
  만들어 서버 없이 파일로 열어도 동작한다.
- 진도는 빌드 시점 스냅샷이다. 진도를 바꾼 뒤 다시 빌드한다.

## 결과

- 얻는 것: 네트워크 없이 빌드·열람, 라이트/다크, 검색, 테스트 가능한 순수 Markdown 생성기.
- 잃는 것 / 감수하는 리스크: 저장소에 약 0.6 MB의 KaTeX 파일, 사이트 URL이 `.html` 형식.
  Mermaid 선수지식 그래프는 JS가 CDN을 쓰므로 넣지 않았다(목록으로 대체). Material for MkDocs는
  2027-05 지원 종료 예정이므로 후속(Zensical 등) 검토가 필요하다.
- 후속 작업: 복습 카드(SRS)가 생기면 대시보드 "오늘 복습" 채우기, 퀴즈 미리보기, 리포트·노트 페이지.
