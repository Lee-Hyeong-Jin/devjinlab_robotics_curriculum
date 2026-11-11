# integration 보안·품질 리뷰 (2026-11-11)

- 대상: `integration` @ `8c53d4e`, 범위 `src/robotics_curriculum/{content,progress,report,site,roadmap.py,library.py,cli.py}`
- 방법: 코드 정독 + 실제 `rc` 명령 실행(임시 디렉터리, 악성 입력). 재현 테스트는
  `tests/test_security_review.py`(QA-01 ~ QA-12, `xfail(strict=True)`). 고쳐지면 XPASS 가 게이트를
  실패시키므로, 수정한 사람이 마커를 지워 회귀 테스트로 전환한다.
- 기준: `docs/PRD.md` 7절(ASVS L2 목표: 입력 검증, 출력 인코딩, 의존성 스캔), `.claude/rules/engineering.md`
  보안 리뷰 체크리스트.
- 게이트: 이 브랜치에서 `scripts/harness/check.sh` 통과(95 passed, 12 xfailed, coverage 94.45%).
- 공개 범위: `SECURITY.md` 는 취약점을 공개 이슈·커밋에서 논의하지 말라고 한다. 이 문서는 아직 로컬
  브랜치에만 있다. 공개 저장소에 푸시하기 전에 QA-01~04 를 고치거나, 이 문서를 비공개 어드바이저리로
  옮길지 사용자가 정해야 한다.

## 요약

| 심각도 | 건수 | ID | 상태 |
|---|---|---|---|
| critical | 0 | — | — |
| high | 4 | QA-01, QA-02, QA-03, QA-04 | 해결됨 `ffdab29` |
| medium | 8 | QA-05 ~ QA-11, QA-15 | 해결됨 `ffdab29` |
| low | 9 | QA-12 ~ QA-14, QA-16 ~ QA-21 | QA-12·QA-17 해결됨 `ffdab29`, QA-20 해결됨 `84b13c2`(DevOps), 나머지(QA-13·14·16·18·19·21) 미해결 |

담당: 모두 코어(content/progress/report/site/cli). 범위 안에 P1-2 퀴즈·API·DB 코드는 없었다.

## 해결 상태 (2026-11-11)

`ffdab29`(브랜치 `worktree-qa-review`)에서 QA-01~QA-12 와 QA-15·QA-17 을 고쳤다. 수용 기준은 PRD 부록
C.0 AC-SEC.1~6. `tests/test_security_review.py` 의 재현 테스트 12개는 strict xfail 에서 통과하는 회귀
테스트로 바뀌었고, `scripts/harness/check.sh` 는 통과한다(107 passed, coverage 93.49%).

적용한 수정과 남은 한계:

- QA-01: 프런트매터 값은 `pages.md_text`(HTML escape → Markdown escape)로, `mkdocs.yml` 의 nav 제목과
  `site_name` 은 `html.escape` 로 처리한다(Material 이 이 둘을 이스케이프 없이 출력하는 것을 실측 확인).
  렌더된 모든 페이지는 생성된 mkdocs 훅에서 `nh3` 허용 목록(`site/sanitize.py`)으로 정리하고, 테마
  override 가 CSP 메타 태그를 넣는다. **한계**: Material 이 인라인 부트스트랩 스크립트를 쓰기 때문에
  CSP 는 `script-src 'unsafe-inline'` 을 허용한다 — 주 방어선은 sanitizer 다. 또한 `site_name` 이
  `<title>` 에서는 테마가 한 번 더 이스케이프하므로, 제목에 `<`·`&` 가 들어가면 그 자리에서만
  `&lt;` 가 글자로 보인다(안전하나 표시가 어색함).
- QA-02: `ProgressService.load_curriculum` 이 `validate_courses` 를 실행하므로 모든 명령이 `rc validate`
  와 같은 검증을 거친다. 자료 링크는 `is_http_url` 로 한 번 더 걸러 `javascript:` 를 링크로 만들지 않는다.
- QA-03·QA-04: `site/build.py: ensure_writable` 가 `.rc-site` 표식이 없는 비어 있지 않은 디렉터리를
  거부하고, cwd·저장소 루트·`$HOME` 은 `--force` 로도 허용하지 않는다. 진행 바는 width 클래스를 쓰므로
  sanitizer 가 `style` 속성을 전면 금지할 수 있다.
- QA-05: 순환 검사는 반복형 DFS. QA-06: 코스 간 id 중복 검사(규칙 7). QA-07: 디코딩·I/O 오류 수집.
  QA-08: 심링크를 해석한 경로가 콘텐츠 루트를 벗어나면 거부.
- QA-09·QA-10: `ProgressExport` 모델이 DB 불변식(세션 id 유일, 사용자별 열린 세션 1개, 시간 순서,
  done↔completed_at)을 검증하고, import 는 커리큘럼에 없는 레슨 id 를 `--allow-unknown` 없이는 거부한다.
- QA-11: WAL + busy timeout(15s), `sqlite3.Error` → `StoreError` → CLI 에서 `error: ...`.
  QA-12: 학습 시간 상한 24시간. QA-15: `logging` 설정과 `rc -v`. QA-17: DB 파일 0600, 데이터 디렉터리 0700.
- 미해결(low): QA-13(완료일 UTC 표시), QA-14(출력 파일 무확인 덮어쓰기), QA-16(i18n 하드코딩),
  QA-18(터미널 이스케이프), QA-19(KaTeX 파일별 해시 검증·버전 갱신), QA-21(CLI 일관성).

## High

| ID | 파일:줄 | 재현 | 영향 | 권고 |
|---|---|---|---|---|
| QA-01 사이트 저장형 XSS | `site/pages.py:223,384,426,433,440,477,549`(제목·요약·목표·본문·자료 note 를 Markdown 에 그대로 삽입), `site/pages.py:353,389`(모듈 summary), `site/build.py:90,92,100`(레슨·모듈 제목을 nav 로, 코스 제목을 `site_name` 으로 전달. Material 테마가 이스케이프 없이 출력) | 레슨 `title: "<img src=x onerror=alert('t')>"`, 본문 `<script>alert('body')</script>`, 모듈 summary `<script>…`를 넣고 `rc site build` 실행. HTML 파서로 확인하면 모든 페이지(404 포함)의 nav·헤더에 `<img onerror>` 가 살아 있고, 레슨·모듈·로드맵 페이지에 `<script>` 가 남는다. `test_qa01` | 콘텐츠는 외부 기여(PR)로 들어온다. 악성 레슨 하나가 빌드된 사이트의 모든 페이지에서 스크립트를 실행한다(대시보드에는 학습 기록·메모가 있다). Phase 2 웹이나 GitHub Pages 로 호스팅하면 저장형 XSS 가 된다. ASVS V5.3(출력 인코딩) 위반 | ① 프런트매터 값은 모두 `html.escape`(Markdown 문맥이면 escape + `esc_text`). ② `mkdocs_config` 의 nav 키와 `site_name` 도 escape 한다. ③ 본문의 raw HTML 은 허용 목록 sanitizer(예: `nh3`)로 정리하는 mkdocs hook(`on_page_content`)을 쓰거나, 콘텐츠 검증에서 raw HTML 을 금지한다. ④ `extra` 템플릿에 CSP 메타 태그(`script-src 'self'`)를 넣는다 |
| QA-02 사이트 빌드가 검증을 건너뜀(`javascript:` 링크) | `progress/service.py:326`(`open_service` 는 `load_courses` 만 하고 `validate_courses` 는 하지 않음), `site/pages.py:543`(url 을 Markdown 링크에 그대로 넣음) | 자료 `url: "javascript:alert('u')"`. `rc validate` 는 exit 1 로 잡지만 `rc site build` 는 exit 0 이고, 레슨·모듈·자료실 페이지에 `<a href="javascript:…">` 가 생긴다. `test_qa02` | 검증 규칙 5(http(s) URL), 2·3(선수 레슨 존재·순환)이 사이트·진도·리포트 경로에서 강제되지 않는다. 클릭하면 XSS. 순환이 있으면 레슨이 영구 잠긴다 | `open_service`/`load_curriculum` 에서 `check()` 를 써서 검증 오류가 있으면 `ProgressError` 를 낸다. 링크 생성 시 `is_http_url` 로 다시 거른다(심층 방어) |
| QA-03 `site build --out` 이 기존 디렉터리를 비움 | `site/cli.py:18,42`, `site/build.py:181`(mkdocs 가 `site_dir` 를 clean) | 파일이 든 디렉터리를 `--out` 으로 지정하면 `important.txt`, `notes/` 가 확인 없이 삭제된다. `test_qa03`. `rc site build --out .` 을 저장소 루트에서 실행하면 점 파일을 뺀 작업 트리 전체(`src/`, `curriculum/`)가 지워진다(코드상 동일 경로이며, 실제 저장소에서는 실행하지 않았다) | 오타 하나로 데이터가 사라진다. 엔지니어링 규칙 "덮어쓰기 전에 대상 확인" 위반 | 비어 있지 않은 디렉터리에 마커(`.rc-site`)가 없으면 거부한다(`--force` 로만 허용). cwd, 저장소 루트, 그 조상, `$HOME` 은 거부한다. 임시 디렉터리에 빌드한 뒤 교체한다 |
| QA-04 `--src` 가 `<src>/docs` 를 rmtree | `site/build.py:154-155`, `:171-172`(`mkdocs.yml` 덮어씀) | `--src proj` 에 `proj/docs/PRD.md` 가 있으면 빌드 후 삭제되고 `mkdocs.yml` 도 덮어쓴다. `test_qa04`. `rc site build --src .` 을 저장소 루트에서 실행하면 저장소의 `docs/`(PRD·ADR)가 지워진다 | 데이터 손실(QA-03 과 같은 계열) | 마커 파일이 있는 디렉터리나 빈 디렉터리만 허용하고, 아니면 거부한다 |

## Medium

| ID | 파일:줄 | 재현 | 영향 | 권고 |
|---|---|---|---|---|
| QA-05 순환 검사 재귀 한도 | `content/validate.py:104-125`(재귀 DFS) | `l0→l1→…→l1099` 선수 체인(의존 레슨이 앞에 정렬되게): `rc validate` 에서 `RecursionError` 가 난다(900 개는 통과). `test_qa05` | 큰 커리큘럼이나 악성 PR 이 검증기와 CI 를 트레이스백으로 죽인다 | 명시적 스택으로 반복 DFS 를 쓰거나, Kahn 위상 정렬로 순환을 찾는다 |
| QA-06 레슨 id 전역 유일성 미검증 | `content/validate.py:22-30`(코스 단위 `seen`) 대 `progress/service.py:111-116`(전역 유일 요구) | 두 코스에 같은 id `dup`: `rc validate` 는 OK 인데 `rc status` 등 모든 진도 명령이 exit 1. `test_qa06` | 검증을 통과한 콘텐츠가 플랫폼을 쓸 수 없게 만든다. CONTENT_MODEL 의 "전역 유일" 규칙을 검증기가 강제하지 않는다 | `validate_courses` 에서 코스 간 레슨(그리고 모듈) id 중복을 검사한다 |
| QA-07 인코딩·I/O 오류 미처리 | `content/loader.py:70,104`(`read_text` 에서 `UnicodeDecodeError`/`OSError` 를 잡지 않음) | UTF-8 이 아닌 레슨 하나로 `rc validate` 가 `UnicodeDecodeError` 트레이스백. `test_qa07` | "모든 오류를 모아 보고"하는 로더 계약이 깨지고, 사용자에게 스택이 노출된다 | `_Collector.add(path, "not UTF-8 …")` 로 수집한다 |
| QA-08 심볼릭 링크로 콘텐츠 루트 탈출 | `content/loader.py:166`(`glob("*.md")` + `is_file()`), `:207`(`iterdir` + `is_dir()`). 둘 다 링크를 따라간다 | 모듈 안 `leak.md → ../outside.md`: `rc validate` OK, `rc show leak` 이 외부 파일 내용을 출력하고, 사이트에도 게시된다. `test_qa08` | 기여 PR 에 심링크를 넣으면 빌드 머신의 임의 Markdown/YAML 을 읽어 정적 사이트로 게시할 수 있다. 체크리스트 "심볼릭 링크 차단" 위반 | `path.is_symlink()` 를 거부하거나, `resolve()` 결과가 루트 하위인지 확인한다 |
| QA-09 import 무결성 오류가 트레이스백 | `progress/service.py:310-315`, `cli.py:317-318`(`ProgressError` 만 처리) | 열린 세션 2개면 `IntegrityError: UNIQUE … sessions.user_id`, 세션 id 가 중복이면 `IntegrityError: … sessions.id`, `total_seconds=2**63` 이면 `OverflowError`. `test_qa09` | 사용자에게 스택이 노출된다. 롤백은 되므로 데이터 손상은 없다 | `ProgressExport` 에 model_validator 를 둔다(열린 세션 ≤1/사용자, id 유일, 정수 범위). `sqlite3.Error` 를 `ProgressError` 로 감싼다 |
| QA-10 import 가 커리큘럼·의미 검증을 안 함 | `progress/service.py:301-316`, `progress/models.py:26-58` | 알 수 없는 lesson_id(`../../etc/passwd`, `ghost`), 음수 `user_id`, `ended_at < started_at`, `done` 인데 `completed_at` 없음이 모두 import 된다. `ghost` 의 열린 세션 때문에 `rc start` 가 계속 거부되고, `rc stop` 은 존재하지 않는 레슨에 시간을 더한다. `test_qa10` | 진도 데이터 무결성(FR-10.2), 혼란스러운 상태 | 커리큘럼에 없는 id 는 경고하고 거부하거나 `--allow-unknown` 일 때만 받는다. 시간 순서, 상태 대 타임스탬프 불변식, `user_id ≥ 1` 을 검증한다 |
| QA-11 DB 잠금 처리 | `progress/store.py:118`(기본 timeout 5s, journal_mode=delete), `cli.py:72-79` | 다른 프로세스가 `BEGIN IMMEDIATE` 를 잡고 있으면 `rc start` 가 5초 뒤 `OperationalError: database is locked` 트레이스백. `test_qa11` | 터미널 두 개를 쓰거나 `site build --serve` 와 동시에 쓰면 실패하고 스택이 노출된다 | `timeout` 을 설정하고 WAL(`PRAGMA journal_mode=WAL`, `busy_timeout`)을 쓴다. `sqlite3.OperationalError` 를 사용자 메시지로 바꾼다 |
| QA-15 로깅 부재 | `src/` 전체(`import logging` 0건) | grep 결과 | 엔지니어링 규칙("logging 모듈 사용")과 PRD 7절 관측성 요구에 미달. 운영 진단이 불가능하다 | 모듈별 `logging.getLogger(__name__)`, `--verbose/-v`, 개인 데이터(메모·경로) 마스킹 |

## Low

| ID | 파일:줄 | 재현·근거 | 권고 |
|---|---|---|---|
| QA-12 거대 duration | `progress/service.py:54-65,208` | `rc log m1-vectors-matrices 99999999999999` 에서 `OverflowError` 트레이스백. `test_qa12` | 상한(예: 24h)을 두고 `ProgressError` 로 처리 |
| QA-13 완료일이 UTC 날짜 | `cli.py:183`, `report/module.py:65` | `completed_at=2026-11-11T23:30Z`(KST 11-12 08:30)가 `rc status` 에 `2026-11-11` 로 표시된다. 주간 리포트·사이트는 로컬 시간대를 쓰므로 표시가 서로 다르다 | `.astimezone()` 후 포맷 |
| QA-14 출력 파일 무확인 덮어쓰기 | `cli.py:296`(`progress export FILE`), `report/cli.py:43-44`(`--out` 임의 경로, 부모 디렉터리 생성) | 기존 `keep.txt` 가 JSON 으로 덮어써진다 | 존재하면 거부하고 `--force` 로만 허용 |
| QA-16 i18n 하드코딩 | `cli.py`(영어 `error:`/`started` 와 한국어 `열린 타이머` 혼재), `site/pages.py` 전반 | 코드 확인 | 메시지 카탈로그(gettext)나 최소한 언어 통일 |
| QA-17 DB 파일 권한 | `progress/store.py:116-118` | `progress.db` 모드 `0644`(학습 메모 포함) | 데이터 디렉터리 `0700`, DB `0600` |
| QA-18 터미널 이스케이프 주입 | `library.py:68,149`(`rc show`/`resources` 가 본문·note 를 그대로 출력) | 코드 확인(미재현) | 제어 문자(`\x1b` 등) 제거 후 출력 |
| QA-19 번들 KaTeX 무결성·버전 | `site/assets/katex/VERSION`(0.16.11, tarball sha1 만 기록) | 파일별 해시 검증 테스트·CI 없음. 0.16.21 미만에는 `trust` 옵션 관련 공지가 있는 것으로 알지만 이 리뷰에서 공지 원문은 확인하지 않았다. `katex-init.js` 는 `trust` 를 켜지 않는다 | 파일별 sha256 매니페스트와 테스트, 최신 0.16.x 로 갱신, 권고 확인 |
| QA-20 의존성 스캔이 CI 에 없음 | `pyproject.toml` dev 그룹, `.github/workflows/ci.yml` | `uv export` 로 158줄 → `uvx pip-audit --no-deps -r`: **No known vulnerabilities found**(2026-11-11). `uv run pip-audit` 은 미설치라 실행 불가 | dev 의존성 추가와 CI 단계(PRD 7절 요구) |
| QA-21 CLI 일관성 | `cli.py:131`(`validate` 가 전역 `--curriculum`/`RC_CURRICULUM_DIR` 를 무시하고 cwd 의 `curriculum` 사용), 오류에 절대 경로 포함(`loader.py:43`) | 코드 확인 | `validate` 기본값을 전역 옵션과 맞춤. 경로는 루트 상대로 표시 |

## 확인했고 문제없음

- YAML: 콘텐츠 로딩은 모두 `yaml.safe_load`(`loader.py:70,110`). 생성되는 `mkdocs.yml` 은 `safe_dump` 이고,
  제목에 `!!python/object/apply:…` 를 넣어도 따옴표로 감싸여 태그로 해석되지 않는다(레슨·모듈 제목으로 실행해 확인).
  고정 문자열 `MARKDOWN_EXTENSIONS` 의 python 태그만 mkdocs 로더에 들어간다.
- SQL: 모든 값이 바인딩 파라미터. f-string 은 상수 테이블명(`store.py:305`)과 상수 조건절(`:297`)에만 쓰인다. 인젝션 경로 없음.
- 페이지 경로: 레슨·모듈 id 가 `^[a-z0-9][a-z0-9-]*$` 로 제한되어 `modules/<id>/<id>.md` 에서 경로 탐색이 불가능하다.
- 셸: `serve_site` 는 인자 리스트로 `subprocess.call` 을 쓴다(`shell=True` 아님). mkdocs serve 기본 바인드는 127.0.0.1.
- ISO 주: `IsoWeek.parse` 가 `2026-W53`(실재), `2020-W53` 는 받고 `2026-W00`, `26-W1` 은 거부한다.
- 성능: 레슨 2000개 커리큘럼에서 `validate`·`status`·`done` 이 각각 약 0.6s.
- 의존성 취약점: 위 QA-20 참조(현재 0건).

## 재현 방법

```bash
uv run pytest tests/test_security_review.py   # 12 passed = 회귀 테스트 (ffdab29 이후)
git show ffdab29 --stat                        # 수정 범위
```

`ffdab29` 이전 커밋에서 같은 테스트를 돌리면 12건이 실패한다(결함 재현).

수동 재현에 쓴 스크립트(XSS 스캐너, 경로·import·잠금 시나리오)는 위 표의 절차와 같고 임시 디렉터리에서만 실행했다.
