# Anki 생태계 · 개발자 지향 오픈 커리큘럼 플랫폼 · 교차 표준 벤치마크 (2026-11 기준)

조사 범위: (A) Anki 생태계(데스크톱/AnkiDroid/sync server/FSRS/패키지 포맷/AnkiConnect/애드온), (B) 개발자 지향 오픈 커리큘럼 플랫폼(freeCodeCamp, Exercism, The Odin Project, Jupyter Book/MyST, Khan Academy 공개 코드), (C) 교차 표준(xAPI/cmi5/SCORM, LTI 1.3, Open Badges 3.0, FSRS를 플래시카드 밖에서 쓰는 사례). 대상은 "로보틱스 전문가 과정" 단일 코스(모듈→레슨, frontmatter 포함 Markdown 레슨, 학습자 진도 + FSRS 복습 예정, 인증/API/웹/CI 예정)의 설계 벤치마크.

표기 원칙: 라이선스·버전·날짜는 가져온 1차 소스(LICENSE 파일, 공식 문서, 레지스트리)에서 확인한 것만 적고, 2차 소스(포럼·블로그·검색 스니펫)는 그 사실을 명시한다.

---

## A-1. Anki 데스크톱 · AnkiDroid · AnkiConnect · 애드온: 라이선스와 스택

### Takeaway
Anki 데스크톱은 AGPL-3.0-or-later, AnkiDroid는 GPL-3.0, AnkiConnect는 GPL-3.0-or-later 애드온이다. Anki 본체 코드를 끌어오면 AGPL 전염을 감수해야 하므로, 벤치마크 대상으로는 "구조와 데이터 모델"만 참고하고 코드는 FSRS 라이브러리(BSD/MIT) 쪽에서 재사용하는 것이 안전하다.

### Cited Findings
- Anki LICENSE 파일 첫 줄: "Anki is licensed under the GNU Affero General Public License, version 3 or" (later). 일부 벤더 컴포넌트는 BSD-3, MIT, Apache 2.0, CC BY 4.0, 문서 사이트 폴더는 CC BY-SA 4.0 — [ankitects/anki LICENSE](https://raw.githubusercontent.com/ankitects/anki/main/LICENSE)
- Anki 최신 릴리스: 26.09.4 (04 Nov, Latest), 26.09.3 (23 Sep), 26.09 (14 Sep), 26.08.1 (05 Aug), 26.08 (01 Aug). 26.09.4는 보안 수정 3건(에디터 iframe 코드 실행, macOS "Show in Folder" 명령 실행, eMudhra 중간 CA 인증서 차단). 26.09.3에 FSRS 관련 수정: "Fix "Card modified" error in the Cards Info screen when FSRS disabled or memory state is missing." — [ankitects/anki Releases](https://github.com/ankitects/anki/releases)
- 애드온 구조: "Anki's UI is primarily written in Python/PyQt." 리뷰 화면과 에디터는 TypeScript/Svelte 사용. "Add-ons in Anki are implemented as Python modules, which Anki loads at startup." 애드온은 훅(hook)에 등록해 특정 동작(예: 브라우즈 화면 로드) 시 통지를 받고 메뉴 추가 등 UI 변경 가능 — [Anki add-on docs: intro](https://docs.ankiweb.net/addons/intro)
- Anki Rust 코어(`rslib`) 저장소 레이아웃: `rslib/src/storage` 하위에 `card, config, dbcheck, deck, deckconfig, graves, note, notetype, revlog, tag, upgrades` 디렉터리와 `schema11.sql, sqlite.rs, sync.rs, sync_check.rs` 등이 있음 — [rslib/src/storage tree](https://github.com/ankitects/anki/tree/main/rslib/src/storage)
- AnkiDroid COPYING 파일: "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007" — [Anki-Android COPYING](https://raw.githubusercontent.com/ankidroid/Anki-Android/main/COPYING)
- AnkiDroid FSRS 지원: Anki 매뉴얼은 "Anki 23.10, AnkiMobile 23.10, AnkiWeb"이 FSRS를 지원하고 "AnkiDroid supports it in 2.17+"라고 명시 — [Anki manual: Deck Options](https://docs.ankiweb.net/deck-options.html)
- AnkiConnect(FooSoft) GitHub 저장소는 "archived by the owner on Nov 4, 2025. It is now read-only."이며 "This repository has permanently moved to https://git.sr.ht/~foosoft/anki-connect." — [FooSoft/anki-connect (archived)](https://github.com/FooSoft/anki-connect)
- AnkiConnect 미러(amikey) README: 라이선스 "GNU General Public License v3 or later", 포트 8765, 기본 바인드 `127.0.0.1`(`ANKICONNECT_BIND_ADDRESS` 환경변수로 변경, 예: `0.0.0.0`), 요청은 HTTP POST JSON `{action, version, params}`(version 생략 시 4), 응답은 `{result, error}`. 주요 액션: `addNote`, `findCards`, `cardsInfo`, `guiAnswerCard`, `deckNames`. 이 미러 페이지가 문서화한 API 버전은 5 — [amikey/anki-connect (mirror)](https://github.com/amikey/anki-connect)
- Anki 매뉴얼(sync server): "simplicity is a design goal"이므로 REST API나 외부 DB 같은 기능은 받아들여질 가능성이 낮고, REST 통합은 AnkiConnect 애드온을 가리킴 — [Anki manual: Sync Server](https://docs.ankiweb.net/sync-server.html)

### Inferences
- Anki 본체(AGPL)와 AnkiDroid(GPL)는 코드 재사용 대상이 아니라 "데이터 모델·UX·운영 방식" 참고 대상이다. 우리 플랫폼이 서버 사이드에서 Anki 코드를 import하면 AGPL 네트워크 조항이 적용되므로 피하는 것이 맞다.
- AnkiConnect는 Anki 데스크톱이 떠 있을 때만 동작하는 로컬 HTTP 브리지(기본 127.0.0.1:8765)라서, 서버형 커리큘럼 플랫폼에는 "선택적 내보내기/가져오기 커넥터" 정도로만 의미가 있다. 공식 저장소가 sourcehut로 이전되었고 GitHub는 2025-11 아카이브된 점을 유지보수 리스크로 기록해야 한다.
- 애드온 생태계(Python 모듈 + 훅)는 플랫폼 확장 모델로서 "훅 기반 플러그인" 패턴의 참고 사례다.

### Gaps
- AnkiConnect 최신 README(API version 6, `apiKey`, `webCorsOriginList`, `requestPermission`, `sync` 액션 등)는 sourcehut(`git.sr.ht`)이 502, foosoft.net 프로젝트 페이지가 404를 반환해 1차 소스로 확인하지 못했다. amikey 미러는 version 5까지만 기술한다.
- Anki 애드온 패키징 상세(`manifest.json`/`meta.json` 필드, AnkiWeb 애드온 ID 배포)는 getting-started 페이지가 404여서 확인하지 못했다.
- Anki 데스크톱의 정확한 Python/Qt 버전 요구사항은 조사하지 않았다.

---

## A-2. Anki 동기화 프로토콜 · 셀프호스트 sync server · 인증 모델(hkey)

### Takeaway
Anki 2.1.57+ 데스크톱에 내장된 sync server는 `SYNC_USER1=user:pass` 환경변수 기반의 단순 username/password 모델이며, 클라이언트는 `/sync/hostKey`에 `{"u","p"}`를 보내 `key`(hkey)를 받아 이후 요청에 사용한다. 서버는 평문 HTTP만 제공하고 리버스 프록시/VPN을 전제로 한다. "엔터프라이즈 인증"의 참고 모델이 아니라 "최소 토큰 인증"의 참고 모델이다.

### Cited Findings
- 내장 sync server는 "desktop version of Anki as of version 2.1.57+"에서 사용 가능. 독립 Rust 서버(Cargo 빌드)는 Anki "2.1.66+" 필요 — [Anki manual: Sync Server](https://docs.ankiweb.net/sync-server.html)
- 실행 방법: 데스크톱 `SYNC_USER1=user:pass anki --syncserver`; pip `SYNC_USER1=user:pass ~/syncserver/bin/python -m anki.syncserver`(Python 3.9+); Cargo `cargo install --locked --git https://github.com/ankitects/anki.git --tag 25.02.5 anki-sync-server`(protoc 필요) — [Anki manual: Sync Server](https://docs.ankiweb.net/sync-server.html)
- 환경변수: `SYNC_USER1`(필수, 추가 계정은 `SYNC_USER2`…), `SYNC_BASE`(기본 `~/.syncserver`, "must not be the same location as your normal Anki data folder"), `SYNC_HOST`/`SYNC_PORT`, `PASSWORDS_HASHED`(설정 시 `username:password_hash`, PHC 포맷 해시), `MAX_SYNC_PAYLOAD_MEGS`(기본 AnkiWeb 한도 100MB 초과 가능), `SYNC_ENDPOINT`/`SYNC_ENDPOINT_MEDIA`(구형 클라이언트 전용, `/sync/`, `/msync/`) — [Anki manual: Sync Server](https://docs.ankiweb.net/sync-server.html)
- 보안: 서버는 "listens on an unencrypted HTTP connection"이며 인터넷 직접 노출용이 아님. 로컬 네트워크 제한, VPN(Tailscale 언급) 또는 HTTPS 리버스 프록시 권장. 서브패스 바인딩 시 클라이언트 URL은 끝에 `/` 필수, Caddy는 `read_buffer 512k` 권장, iOS는 TLS 1.3 미지원이므로 TLS 1.2 활성화 필요 — [Anki manual: Sync Server](https://docs.ankiweb.net/sync-server.html)
- 프로토콜 호환성 주의: "newer clients may depend on changes to the sync protocol"이므로 클라이언트 업데이트 시 서버도 함께 업데이트해야 함. 서드파티 서버는 테스트되지 않았고 권장하지 않음 — [Anki manual: Sync Server](https://docs.ankiweb.net/sync-server.html)
- 로그인 코드(`rslib/src/sync/login.rs`, AGPL): `SyncAuth { hkey: String, endpoint: Option<Url>, io_timeout_secs: Option<u32> }`; `HostKeyRequest { #[serde(rename="u")] username, #[serde(rename="p")] password }`; `HostKeyResponse { key: String }`; `sync_login(username, password, endpoint, client)`은 `client.host_key(...)`를 호출해 `resp.key`를 `hkey`로 돌려줌. 테스트 코드에 경로 `"/sync/hostKey"`가 등장 — [rslib/src/sync/login.rs](https://raw.githubusercontent.com/ankitects/anki/main/rslib/src/sync/login.rs)
- 포럼(2차): Anki 24.11/25.x에서 애드온이 `sync_login()`에 이메일/비밀번호를 넘기는 구식 방식이 거부되며, 대안으로 `auth = mw.col.sync_login(username=..., password=..., endpoint=mw.pm.sync_endpoint()); mw.pm.set_sync_key(auth.hkey)`가 제시됨 — [Anki Forums: authenticate without GUI](https://forums.ankiweb.net/t/is-there-any-supported-way-to-authenticate-ankiweb-login-without-using-the-gui/67637)
- 비공식 서버: `ankicommunity/anki-sync-server`가 검색 결과에 존재(별도 프로젝트) — [ankicommunity/anki-sync-server](https://github.com/ankicommunity/anki-sync-server/)

### Inferences
- Anki의 인증 모델은 (1) 정적 환경변수 사용자 목록, (2) hostKey 교환으로 얻은 장기 토큰(hkey) 재사용, (3) TLS는 외부 프록시 위임 — 세 가지가 전부다. OAuth/OIDC, 역할, 세션 만료 개념이 없으므로 우리 플랫폼의 "planned auth"에는 참고가 아니라 반면교사다(엔터프라이즈 요구에는 OIDC + 짧은 액세스 토큰이 필요).
- 반대로 "단일 바이너리 + 환경변수 + 파일 시스템 저장소 + 리버스 프록시 전제"라는 운영 단순성은 소규모 오픈소스 플랫폼의 self-host 배포 모델로 그대로 차용할 만하다.
- 프로토콜이 버전 간 변경되며 공식 서버 외에는 호환을 보장하지 않으므로, Anki 동기화 프로토콜 자체를 구현/호환하려는 시도는 비용 대비 가치가 낮다. 필요하면 `.apkg` 내보내기로 충분하다.

### Gaps
- hostKey 이후의 전체 요청 목록(meta, start, applyChanges, chunk, sanityCheck2, finish, 미디어 동기화 등)과 요청 서명 방식은 `rslib/src/sync` 소스를 직접 읽어야 하며 이번 조사에서는 login.rs만 확인했다.
- `PASSWORDS_HASHED`의 해시 알고리즘(PHC 포맷의 어떤 KDF인지)은 매뉴얼에 명시되어 있지 않다.

---

## A-3. Anki 컬렉션 스키마(.apkg/.colpkg), revlog, FSRS 메모리 상태 저장

### Takeaway
Anki 컬렉션은 SQLite 하나이며 핵심은 `notes`(내용) → `cards`(스케줄 단위) → `revlog`(리뷰 로그, append-only)의 3단 구조다. 최신 Anki는 FSRS 메모리 상태를 `cards.data` JSON(`s`, `d`, `dr`, `decay`, `lrt`)에 넣고, `revlog.factor`에 FSRS 난이도를 정규화해 기록한다. 우리 플랫폼의 "레슨 복습 상태 + 리뷰 로그" 테이블 설계에 직접 참고 가능한 가장 작은 모델이다.

### Cited Findings
- schema11.sql 테이블/컬럼: `col(id, crt, mod, scm, ver, dty, usn, ls, conf, models, decks, dconf, tags)`, `notes(id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data)`, `cards(id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data)`, `revlog(id, cid, usn, ease, ivl, lastIvl, factor, time, type)`, `graves(usn, oid, type)` — [rslib/src/storage/schema11.sql](https://raw.githubusercontent.com/ankitects/anki/main/rslib/src/storage/schema11.sql)
- AnkiDroid 위키(스키마 v11 기준) 컬럼 의미: `notes.id`는 생성 시각(epoch ms), `guid`는 동기화용 전역 ID, `mid`는 노트 타입(model) ID, `tags`는 공백 구분(앞뒤 공백 포함, LIKE 검색용), `flds`는 0x1f 구분 필드값, `sfld`는 정렬 필드, `csum`은 첫 필드 SHA-1 앞 8자리(중복 검사). `cards.type`: "0=new, 1=learning, 2=review, 3=relearning"; `queue`: -1 suspended, 음수 buried, 4 preview; `due`: 새 카드=순서, 학습 카드=epoch 초, 복습 카드=컬렉션 생성일 기준 일수; `ivl` 일 단위; `factor` 천분율(2500=2.5x); `reps`, `lapses`; `left`=a*1000+b; `odue`/`odid`는 필터 덱 원본; `flags`는 mod 8 색상 — [AnkiDroid wiki: Database Structure](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure)
- `revlog`: `id` 리뷰 시각(epoch ms), `cid`, `usn`, `ease`(복습: 1 wrong, 2 hard, 3 ok, 4 easy; 학습/재학습: 1 wrong, 2 ok, 3 easy), `ivl`(음수=초, 양수=일), `lastIvl`, `factor`("If FSRS is enabled, it is replaced by the FSRS difficulty normalized to a 100-1100 range."), `time`(ms, 60000 상한), `type`(0 learn, 1 review, 2 relearn, 3 filtered, 4 manual, 5 rescheduled). `graves`는 삭제 항목 동기화용(`type` 0 card, 1 note, 2 deck) — [AnkiDroid wiki: Database Structure](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure)
- v11에서는 노트 타입(`models`, 내부에 `flds`/`tmpls`), `decks`, `dconf`(덱 옵션 그룹), `conf`, `tags`가 `col` 테이블의 JSON 블롭으로 저장됨 — [AnkiDroid wiki: Database Structure](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure)
- FSRS 메모리 상태(`rslib/src/storage/card/data.rs`의 `CardData`): `original_position`→`"pos"`, `fsrs_stability`→`"s"`, `fsrs_difficulty`→`"d"`, `fsrs_desired_retention`→`"dr"`, `decay`→`"decay"`, `last_review_time`→`"lrt"`, `custom_data`→`"cd"`("A string representation of a JSON object storing optional data associated with the card, so v3 custom scheduling code can persist state"). 미설정 필드는 JSON에서 생략. `memory_state()`는 s와 d가 모두 있을 때만 값을 반환. 직렬화 시 s 4자리, d 3자리, dr 2자리, decay 3자리 반올림. 테스트 기대값 예: `{"s":123.4568,"d":1.235,"dr":0.99,"decay":0.123}` — [rslib/src/storage/card/data.rs](https://raw.githubusercontent.com/ankitects/anki/main/rslib/src/storage/card/data.rs)
- `.apkg` 컨테이너(2차 소스): ZIP 아카이브이며 최신 패키지는 "a real v18 SQLite (`collection.anki21b`, zstd-compressed) AND a decoy v11 SQLite at `collection.anki2`" 두 개를 담음(구형 클라이언트용 더미) — [ankisync2 / 검색 결과 요약](https://pypi.org/project/ankisync2/); 포럼: "collection.anki2 is a dummy for older clients trying to import the file" — [Anki Forums: Collection.anki2 in exported .apkg](https://forums.ankiweb.net/t/collection-anki2-in-exported-apkg-file/44380); 파서 구현은 `collection.anki21b`(zstd) → `collection.anki21` → `collection.anki2` 순으로 시도 — [vultan crate source](https://docs.rs/crate/vultan/1.0.1/source/src/anki.rs); 미디어 파일은 번호 항목으로 저장되고 `media` 파일이 번호→파일명 매핑 JSON — [74Genesis/anki-apkg-parser](https://github.com/74Genesis/anki-apkg-parser)
- 노트 타입/템플릿: Anki 매뉴얼의 Deck Options 페이지는 FSRS 파라미터가 "preset-specific"이며 프리셋마다 별도 최적화 대상이라고 설명 — [Anki manual: Deck Options](https://docs.ankiweb.net/deck-options.html)

### Inferences
- 우리 플랫폼용 최소 스키마는 Anki의 3단 구조를 "lesson(콘텐츠, Git의 Markdown이 원천) → review_item(학습자×레슨 스케줄 단위, s/d/dr/decay/last_review/due 보유) → review_log(append-only: item_id, rating 1-4, elapsed, scheduled, reviewed_at, duration_ms)"로 옮기면 된다. Anki가 `revlog`를 절대 삭제하지 않고(`graves`로만 동기화) 옵티마이저 입력으로 쓰는 점이 핵심이므로 review_log는 삭제 금지·불변 테이블로 설계해야 한다.
- Anki가 FSRS 상태를 정규화 컬럼이 아니라 `cards.data` JSON에 넣은 이유는 알고리즘 버전 간 필드 변화(FSRS-6의 `decay` 추가)를 흡수하기 위한 것으로 보인다. 우리도 알고리즘 상태를 JSON/JSONB 컬럼 하나로 두고 버전 키를 함께 저장하면 FSRS-6→7 이행이 쉬워진다.
- v11 스키마의 "JSON 블롭 in `col`" 방식(덱/노트타입)은 최신 Anki에서 별도 테이블(`deck`, `notetype`, `deckconfig`, `config`, `tag` 저장소 모듈 존재)로 이관된 것으로 보이나, 이번 조사에서 schema15+ SQL 원문은 확인하지 못했다(아래 Gaps).
- `.apkg`는 "구형 클라이언트용 더미 + 최신 zstd SQLite" 이중 패키징이라 자체 포맷 설계보다는 "내보내기 타깃"으로만 취급하는 것이 합리적이다.

### Gaps
- Anki 최신 스키마(v18로 추정)의 `decks`, `notetypes`, `fields`, `templates`, `deck_config`, `config`, `tags` 테이블 정의는 `schema15_upgrade.sql` 경로가 404여서 원문을 확인하지 못했다. 저장소 디렉터리 목록에는 `schema11.sql`만 보였다.
- `.apkg` 내 `meta` 파일의 protobuf 스키마와 `.colpkg`(전체 컬렉션 패키지)의 상세 구조는 1차 소스를 찾지 못했다.
- AnkiDroid 위키는 명시적으로 "as of version 11"만 기술하므로 최신 스키마 설명으로 쓰면 안 된다.

---

## A-4. FSRS 알고리즘과 라이브러리(fsrs-rs / py-fsrs / ts-fsrs): 라이선스·버전·통합 API, 재사용 가능 범위

### Takeaway
FSRS는 open-spaced-repetition 조직의 독립 라이브러리로 재사용 가능하며 라이선스는 fsrs-rs BSD-3-Clause, py-fsrs MIT, ts-fsrs MIT다. 2026-11 기준 py-fsrs는 FSRS-6(21 파라미터), ts-fsrs v6.0.0은 FSRS-7 기본, fsrs-rs는 FSRS-6/7을 파라미터 개수로 자동 선택한다(7.0.0이 2026-11-10 등록). Anki 본체(AGPL)는 fsrs-rs를 쓰는 소비자일 뿐이므로, 플랫폼은 Anki 없이 FSRS만 가져오면 된다.

### Cited Findings
- 알고리즘(awesome-fsrs 위키 "The Algorithm"): 구성요소 R(Retrievability, 회상 확률), S(Stability, R=90%가 되는 간격), D(Difficulty, D∈[1,10]). FSRS-6 망각곡선 R(t,S)=(1+factor·t/S)^(−w20), factor=0.9^(−1/w20)−1, 즉 R(S,S)=90%. 파라미터 수: FSRS-4.5 "17 parameters", FSRS-5 "19 parameters", FSRS-6 "21 parameters". FSRS-6 신규: "The forgetting curve's decay is trainable."(w20), 같은 날 리뷰 안정성 공식 변경(w17, w18, w19). 평점 G: 1=again, 2=hard, 3=good, 4=easy. 이 페이지는 FSRS-7을 언급하지 않음 — [awesome-fsrs wiki: The Algorithm](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm)
- fsrs4anki 위키의 구 알고리즘 페이지는 awesome-fsrs 위키로 이전됨("This page has moved to the new wiki") — [fsrs4anki wiki: The Algorithm (moved)](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm)
- fsrs-rs: "BSD-3-Clause license", "FSRS for Rust, including Optimizer and Scheduler", "both FSRS-6 and FSRS-7" 지원이며 "FSRS-6 and FSRS-7 are selected from the parameter count". API: `FSRS::default()`, `next_states(previous_state, desired_retention, elapsed_days)`(평점별 상태, 예 `.good.interval`), `memory_state_from_sm2(ease_factor, interval, sm2_retention)`, `memory_state(FSRSItem{reviews}, Some(initial_state))`, `compute_parameters(ComputeParametersInput{train_set, ..})`, `compute_parameters_from_card_prefixes`, `FSRS::evaluate_from_card_prefixes`, `CostAdrPolicy::next_states`/`simulate_with_cost_adr_policy`("a 15-parameter cost-conditioned desired-retention policy"). FSRS는 "springs from MaiMemo's DHP model" — [open-spaced-repetition/fsrs-rs](https://github.com/open-spaced-repetition/fsrs-rs)
- fsrs crate 레지스트리: 최신 7.0.0, "released Nov 10, 2026"(6.7.0도 같은 날짜로 표시), BSD-3-Clause, "Used in 8 crates (7 directly)" — [lib.rs: fsrs](https://lib.rs/crates/fsrs)
- py-fsrs: "MIT license", `pip install fsrs`, `from fsrs import Scheduler, Card, Rating, ReviewLog`, `card, review_log = scheduler.review_card(card, rating)`, `optimizer = Optimizer(review_logs)`(`pip install "fsrs[optimizer]"`), `get_card_retrievability`, `reschedule_card`, `compute_optimal_retention`, "parameters are a set of 21 model weights" — [open-spaced-repetition/py-fsrs](https://github.com/open-spaced-repetition/py-fsrs); PyPI 최신 6.3.2, "Aug 9, 2026", "MIT License", "Python >=3.10", "a set of 21 model weights" — [PyPI: fsrs](https://pypi.org/project/fsrs/)
- ts-fsrs: MIT, "`ts-fsrs` v6 and `@open-spaced-repetition/binding` require Node.js `>=24.0.0`", "It defaults to FSRS-7; the library version and the FSRS model version are independent.", 지원 모델 배지 FSRS 3/4.5/5/6/7. v6 API: `DefaultScheduler()`, `scheduler.newCard({ now })`, `scheduler.preview({ card, now })`, `scheduler.review({ card, grade: Rating.Good, now })` — [open-spaced-repetition/ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs); npm 레지스트리 최신 6.0.0, MIT, engines node ">=24.0.0", exports에 `./models/fsrs-6`, `./models/fsrs-7` 경로 — [registry.npmjs.org: ts-fsrs/latest](https://registry.npmjs.org/ts-fsrs/latest)
- Anki 내 FSRS 운영 파라미터(매뉴얼): FSRS는 SM-2 대안; "FSRS can only be enabled globally"; Desired retention 기본 90%, "This is the most important setting in FSRS. Higher retention leads to shorter intervals and more reviews per day.", 97% 미만 권장; Optimize는 "uses machine learning to learn your memory patterns", "once every month is sufficient"; "Optimize All Presets", "Check health when optimizing (slow)"; "Compute minimum recommended retention"은 "removed as of anki version 25.07"; Historical Retention(기본 90%, 누락 리뷰 이력 추정), Ignore Cards Reviewed Before, Maximum Interval 기본 100년; 학습 단계는 1일 미만(10m/30m 권장); Custom Scheduling(전역 JavaScript) — [Anki manual: Deck Options](https://docs.ankiweb.net/deck-options.html)
- Anki 25.07 릴리스 노트(2차 집계): "FSRS-6 brings further algorithm improvements by @L-M-Sherlock in #3929", fsrs-rs v3.0.0 업데이트, "use log loss instead of RMSE(bins)" — [newreleases.io: anki 25.07](https://newreleases.io/project/github/ankitects/anki/release/25.07)
- awesome-fsrs 목록(CC0-1.0): 구현체 — Python py-fsrs(scheduler v6 + optimizer), fsrs-optimizer(v6), fsrs-rs-python(v6); Rust fsrs-rs(v6 + optimizer), fsrs-browser; TypeScript ts-fsrs(v3–v7); Go go-fsrs(v5); Java rs-fsrs-java(v5); Kotlin FSRS-Kotlin(v6), android-fsrs(v4); Swift swift-fsrs(v5); Dart dart-fsrs(v4.5); Clojure cljc-fsrs(v4); Haskell haskell-fsrs(v7) 등 — [open-spaced-repetition/awesome-fsrs](https://github.com/open-spaced-repetition/awesome-fsrs)

### Inferences
- "재사용 가능한 라이브러리" 경계: 스케줄러·옵티마이저·시뮬레이터(fsrs-rs/py-fsrs/ts-fsrs)는 Anki와 무관하게 쓸 수 있는 순수 함수형 API(카드 상태 + 평점 + 시각 → 다음 상태)다. "Anki에 결합된" 부분은 (1) 프리셋 단위 파라미터 저장/최적화 UI, (2) 학습 단계(learning steps)·필터 덱·custom scheduling JS 같은 스케줄 큐 운영, (3) revlog→FSRSItem 변환 로직, (4) 동기화다.
- 백엔드 언어 선택에 따른 권장: Python 백엔드면 py-fsrs(MIT, FSRS-6, 옵티마이저 extra 포함), Rust면 fsrs(BSD-3, FSRS-6/7 자동), TS/Node면 ts-fsrs(MIT, FSRS-7 기본, Node 24+). 모델 버전은 "파라미터 배열 길이"로 식별되므로 DB에 파라미터 배열을 그대로 저장하면 라이브러리 간 이동이 가능하다.
- 레슨 복습용 최소 통합 패턴(추론): 레슨 완료 시 `newCard`, 복습 시 사용자 자가평가(Again/Hard/Good/Easy) → `review` → 다음 `due`와 `{s,d,decay}` 저장, 리뷰 로그 누적 후 월 1회 `Optimizer`로 사용자별 파라미터 재학습(Anki의 "once every month" 권장과 동일). desired retention 기본 0.9.
- fsrs-rs 7.0.0과 6.7.0이 같은 날(2026-11-10) 등록된 것은 메이저 전환 직후로 보이며, FSRS-7의 Anki 본체 반영 여부는 미확인이므로 당장은 FSRS-6(21 파라미터)을 기준선으로 잡는 것이 안전하다.

### Gaps
- FSRS-7의 수식·파라미터 수·변경점은 awesome-fsrs 위키 알고리즘 페이지에 없고, fsrs-rs README도 "파라미터 수로 선택"만 밝혀 확인하지 못했다.
- Anki 26.x가 FSRS-7을 탑재했는지는 릴리스 페이지 상단(26.09.x) 노트에 언급이 없어 미확인이다.
- Jarrett Ye(L-M-Sherlock)가 FSRS 원저자라는 점은 Anki 매뉴얼에는 없으며, 25.07 릴리스 노트의 PR 작성자 표기(@L-M-Sherlock)로만 간접 확인된다.
- fsrs-rs의 FSRS 파라미터 수(21)는 README에 명시되지 않았다(py-fsrs 쪽에서 21로 확인).

---

## B-1. freeCodeCamp: 라이선스 · 챌린지 Markdown 포맷 · 진도/인증 모델

### Takeaway
코드는 BSD-3-Clause, 커리큘럼 디렉터리는 README에 "copyright © 2014 freeCodeCamp.org"로만 적혀 있어 저장소 1차 소스에서는 CC-BY-SA를 확인하지 못했다. 챌린지는 ObjectId 파일명의 Markdown(frontmatter `id/title/challengeType/dashedName`) + `# --description--`/`# --hints--`(테스트 ```js 블록)/`# --seed--`/`# --solutions--` 섹션이고, 순서는 `curriculum/structure/*.json`이 담당한다. 진도는 MongoDB `user.completedChallenges[]`, 인증은 이메일 일회용 코드 + Google/GitHub(이메일 획득용).

### Cited Findings
- LICENSE.md: "BSD 3-Clause License", "Copyright (c) 2014, freeCodeCamp. All rights reserved." CC 조항 없음 — [freeCodeCamp LICENSE.md](https://github.com/freeCodeCamp/freeCodeCamp/blob/main/LICENSE.md)
- README: "The computer software is licensed under the BSD-3-Clause license." / "The learning resources in the /curriculum directory" "are copyright © 2014 freeCodeCamp.org." — [freeCodeCamp README](https://raw.githubusercontent.com/freeCodeCamp/freeCodeCamp/main/README.md)
- 파일 구조: 영어 챌린지는 `curriculum/challenges/english/blocks/<block>/<challenge>.md`; 인증 YAML은 `curriculum/challenges/english/certifications/<certification>.yml`; 번역은 `i18n-curriculum` 서브모듈(.md만 번역); 구조 메타는 `curriculum/structure/curriculum.json`, `superblocks/<superblock>.json`, `blocks/<block>.json`. "Challenge files in `curriculum/challenges/english/blocks/<block>/` are named after their `id`"(예 `66ad8294a0ad902f1b31b612.md`). `dashedName`은 URL 슬러그(소문자/숫자/하이픈). 블록 JSON 필드: `dashedName`, `blockLabel`(workshop/lab/lecture), `blockLayout`(challenge-grid/challenge-list/legacy-challenge-list), `helpCategory`, `isUpcomingChange`, `usesMultifileEditor`, `hasEditableBoundaries`, `challengeOrder: [{id, title}]`. 슈퍼블록 JSON은 단순형(`blocks` 배열) 또는 `chapters → modules → blocks` 중첩형(`moduleType` cert-project/review, `chapterType` exam, `comingSoon`) — [contribute.freecodecamp.org: Curriculum File Structure](https://contribute.freecodecamp.org/curriculum-file-structure/)
- 코딩 챌린지 가이드: "Version 9 certifications are organized into chapters, modules, blocks and challenges." 헬퍼 `pnpm run create-next-challenge`, `pnpm run update-challenge-order`. 테스트는 "Node.js `assert` API and the Chai `assert` API" 사용, 사용자 코드는 `code` 변수, `__helpers` 객체 제공, 워크숍은 `--fcc-editable-region--` 마커 사용. challengeType 숫자 의미는 `challenge-types.ts` 참조 — [contribute.freecodecamp.org: Coding Challenges](https://contribute.freecodecamp.org/how-to-work-on-coding-challenges/)
- Lab 템플릿: frontmatter `id: <ObjectId>`, `title: Build / Implement / Design / Debug [Name]`, `challengeType: 26`(JavaScript lab), `dashedName: lab-name`; 섹션 `# --description--`("**Objective:** Fulfill the user stories below and get all the tests to pass to complete the lab." + User Stories), `# --hints--`(설명 한 줄 + ```js 테스트 코드), `# --seed--` 아래 `## --seed-contents--`, `# --solutions--`; 선택 훅 `--before-all--`, `--before-each--`, `--after-each--`, `--after-all--`; 시각 랩은 `demoType: onClick` 가능 — [contribute.freecodecamp.org: Labs](https://contribute.freecodecamp.org/how-to-work-on-labs/)
- 다른 challengeType 예: 비디오 챌린지 `challengeType: 11`과 `videoId` 필드 — [contribute.freecodecamp.org: Video Challenges](https://contribute.freecodecamp.org/how-to-help-with-video-challenges/); 언어 커리큘럼 과제 `challengeType: 31` — [contribute.freecodecamp.org: Language Curricula](https://contribute.freecodecamp.org/how-to-work-on-language-curricula/)
- 진도 데이터 모델(`api/prisma/schema.prisma`, provider = "mongodb"): user 필드 `email String?`, `emailVerified Boolean?`, `username String // TODO(Post-MVP): make this unique`, `externalId String`, `isCheater Boolean?`, `completedChallenges CompletedChallenge[]`, `savedChallenges SavedChallenge[]`, `completedExams CompletedExam[]`, `partiallyCompletedChallenges PartiallyCompletedChallenge[]`, `progressTimestamps Json? // ... TODO: NORMALIZE`. `CompletedChallenge { id String; completedDate Json; solution String?; githubLink String?; challengeType Json?; files File[] }`. 토큰 모델 `AuthToken { id, created DateTime, ttl Int, userId }`, `UserToken { id, created, ttl Float, userId }`. ProfileUI에 `showName`, `showAbout`, `showLocation`, `showPoints`, `showPortfolio`, `isLocked`, `showTimeLine` 등 공개 범위 플래그 — [freeCodeCamp api/prisma/schema.prisma](https://raw.githubusercontent.com/freeCodeCamp/freeCodeCamp/main/api/prisma/schema.prisma)
- 인증: FAQ "Sign in codes are much more secure than passwords, and many websites are moving to them." / "Many websites are following our lead and moving to one time codes or "magic links" as well." Google/GitHub 로그인은 "just use that to access your email address", "Your account is ultimately tied to your email addresses." — [freeCodeCamp Support FAQ](https://www.freecodecamp.org/news/support/)
- (2차, 자동 생성 위키) API 서버는 Fastify 기반이며 Auth0(OAuth 2.0)를 사용(`AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, `AUTH0_CLIENT_SECRET`); 시험 채점 결과는 `completedExams`에 항상 저장되고 합격 시 `completedChallenges`에 추가/갱신 — [freeCodeCamp DeepWiki 요약(비공식)](https://lidarmonitor.kapernikov.com/news/freecodecamp-freecodecamp-deepwiki)

### Inferences
- 빌려올 것: (1) "콘텐츠 파일 = 불변 ID 파일명, 사람용 슬러그는 frontmatter `dashedName`" 분리 — 레슨 리네임이 진도 데이터를 깨지 않는다. (2) 순서/계층을 콘텐츠 파일이 아니라 별도 구조 JSON(`curriculum.json`/`superblocks`/`blocks`)에 두는 방식 — 모듈→레슨 재배치가 diff 친화적. (3) Markdown 본문을 `# --section--` 마커로 분할해 설명/힌트/테스트/시드/해답을 한 파일에 두는 단일 소스 패턴. (4) 진도 레코드가 `completedChallenges[{id, completedDate, solution, files}]`처럼 "챌린지 ID + 완료 시각 + 제출물" 최소 튜플이라는 점.
- 피할 것: 스키마 주석의 `TODO: NORMALIZE`, `Json`으로 느슨하게 저장된 `completedDate`/`challengeType` 등은 MongoDB 유산의 기술 부채로, 우리는 처음부터 정규화된 테이블(완료 레코드에 lesson_id FK, timestamptz)을 쓰는 게 낫다.
- 인증은 "이메일이 정체성, 비밀번호 없음, 소셜 로그인은 이메일 획득 수단" 모델이 소규모 플랫폼에 적합하다. 다만 freeCodeCamp가 Auth0에 위임한다는 점은 2차 소스로만 확인되므로 설계 근거로 쓸 때 주의.

### Gaps
- 커리큘럼 콘텐츠의 CC-BY-SA 라이선스는 1차 소스(LICENSE.md, README)에서 확인하지 못했다(README는 저작권 표기만). 사이트 푸터 등 다른 위치에 있을 수 있다.
- `challenge-types.ts`의 전체 숫자 매핑은 raw 경로가 404여서 확인하지 못했다(확인된 값: 26 JavaScript lab, 11 video, 31 language task).
- frontmatter 선택 필드(`forumTopicId`, `videoUrl`, `videoId`, `demoType` 등)의 전체 목록과 `--notes--`, `--after-user-code--` 같은 추가 섹션은 공식 페이지에서 일부만 확인됐다.
- 이메일 코드 발급/검증 흐름의 서버 구현(라우트)은 읽지 않았다.

---

## B-2. Exercism: 라이선스 · 트랙/콘셉트/연습문제 레이아웃 · 테스트 러너 · 진도

### Takeaway
웹사이트 코드는 AGPL-3.0(Rails + MySQL/MongoDB/Redis). 트랙은 `config.json`(version 3)에 콘셉트·연습문제·선행관계를 선언하고, 각 연습문제는 `.docs/*.md` + `.meta/config.json` + 스텁/테스트/모범답안 파일로 구성된다. 테스트 러너는 Docker에서 `slug input_dir output_dir`를 받아 `results.json`(version 1/2/3)을 쓰는 계약이며, 20초/3GB 한도다. 우리 플랫폼의 "레슨 메타데이터 + 선행관계 그래프 + 실습 채점 계약"의 가장 좋은 참고 모델이다.

### Cited Findings
- exercism/website: 사이드바 "AGPL-3.0 license"; "This is the website component of Exercism. It is Ruby on Rails app, backed by various other services." 사전 요구: Ruby 3.3.0, MySQL, MongoDB, Redis, AnyCable-Go, Docker, LocalStack/OpenSearch(Docker) — [exercism/website](https://github.com/exercism/website)
- 트랙 `config.json` 상위 필드: `language`(필수), `slug`, `active`(bool), `blurb`(≤400자), `version`(고정 3), `online_editor{indent_style, indent_size, highlightjs_language}`, `status{concept_exercises, test_runner, representer, analyzer}`(모두 필수), `test_runner{average_run_time}`, `files{solution, test, example, exemplar, editor}`(`%{pascal_slug}` 등 플레이스홀더), `approaches{snippet_extension}`, `exercises{concept[], practice[], foregone[]}`, `concepts[]`, `key_features`(정확히 6개: title≤25자, content≤100자, icon), `tags`. 콘셉트 연습문제: `uuid`(V4, 불변), `slug`, `name`, `concepts[]`, `prerequisites[]`, `status`(wip/beta/active/deprecated). 실습 연습문제: `uuid, slug, name, practices[], prerequisites[], difficulty(1–10), status`. 콘셉트 항목: `uuid, slug, name, tags{all, any, not}`. "Exercises are ordered on the website in the same order they are listed in this file" — [Exercism docs: config.json](https://exercism.org/docs/building/tracks/config-json)
- 콘셉트 연습문제 디렉터리: `exercises/concept/<slug>/` 아래 `.docs/introduction.md`(필수), `.docs/instructions.md`(필수), `.docs/hints.md`(필수), `.meta/config.json`(필수), `.meta/design.md`(필수), `.meta/Exemplar.*`(모범답안, 필수), 스텁 구현, 테스트, 선택 `.approaches`, `.articles`. `.meta/config.json` 필드: `authors`(필수), `contributors`, `files.solution`/`files.test`/`files.exemplar`(필수), `forked_from`, `language_versions`, `blurb`(≤350자, Markdown 불가, 필수), `icon` — [Exercism docs: Concept Exercises](https://exercism.org/docs/building/tracks/concept-exercises)
- 콘셉트 디렉터리: `concepts/<slug>/{.meta/config.json, about.md, introduction.md, links.json}`; 디렉터리명은 `config.json`의 `slug`와 일치해야 함. `about.md`: "Provide more detailed information about the Concept for a student who has completed the corresponding Concept Exercise"; `introduction.md`: "Provide a brief introduction to a student who has not yet completed the corresponding concept exercise"; `links.json`: `[{url, description, icon_url?}]`; `.meta/config.json`: `authors`(필수), `contributors`, `blurb`(≤350자) — [Exercism docs: Concepts](https://exercism.org/docs/building/tracks/concepts)
- 테스트 러너 인터페이스: "The script will receive three parameters"(exercise slug, input dir, output dir); "The script must write a `results.json` file to the output directory."; "The runner must exit with an exit code of 0 if it has run successfully, regardless of the status of the tests." `results.json`: `version`(1/2/3), `status`(pass/fail/error), `message`, `tests[]{name, status(pass/fail/error), test_code, message, output(≤500자), task_id(v3)}`. 자원 한도: "The test runner gets 100% CPU with 3GB of memory for a 20 second window per solution." — [Exercism docs: Test Runner Interface](https://exercism.org/docs/building/tooling/test-runners/interface)

### Inferences
- 빌려올 것: (1) 레슨 메타데이터에 `uuid`(불변) + `slug`(URL) + `prerequisites[]`(선행 콘셉트) + `status`(wip/beta/active/deprecated) + `difficulty`를 두는 설계 — 모듈→레슨 선형 순서 외에 선행관계 DAG를 표현할 수 있다. (2) 문서를 `introduction.md`(사전) / `about.md`(사후 심화) / `hints.md`로 분리하는 "학습 단계별 문서" 패턴은 로보틱스 레슨(개념 소개 → 실습 → 심화)에 잘 맞는다. (3) 실습 채점을 "Docker 이미지 + 고정 CLI 계약 + results.json" 인터페이스로 분리하면 ROS/시뮬레이터 실습 채점기도 같은 계약으로 플러그인화할 수 있다. (4) `blurb` 길이 제한, `key_features` 개수 고정 같은 린트 가능한 스키마 제약.
- Exercism의 멘토링·학생 진도는 AGPL Rails 앱 내부 DB에 있어 재사용 불가하며, 공개 문서는 "트랙 저장소 포맷"만 표준화한다. 우리도 "콘텐츠 저장소 포맷은 공개 스키마, 진도는 앱 DB"로 분리하는 것이 자연스럽다.

### Gaps
- 학생 진도(solution/iteration/mentoring 요청) 테이블과 인증 방식(Devise/OmniAuth 여부)은 exercism/website 저장소 내부를 읽지 않아 확인하지 못했다.
- 실습(practice) 연습문제 레이아웃 문서(`tests.toml`, `.meta/example` 등)는 docs 저장소 경로가 404였다.
- 테스트 러너 Docker 이미지 요구사항(`docker.md`)은 별도 페이지라 읽지 못했다.

---

## B-3. The Odin Project: 라이선스 · 레슨 Markdown 규약 · Rails 앱의 진도/인증 모델

### Takeaway
앱 코드는 MIT, 커리큘럼 콘텐츠는 CC BY-NC-SA 4.0(비상업)이다. 레슨은 GitHub `curriculum` 저장소의 Markdown이고 앱 DB `lessons.github_path`로 연결되며, 본문은 `contents.body`에 적재된다. 진도는 `lesson_completions(user_id, lesson_id, course_id, path_id)` 한 테이블로 매우 단순하며, 인증은 Devise + GitHub/Google OmniAuth. "Markdown in Git + 작은 Rails 앱 + 완료 테이블" 조합은 우리 목표 구조와 가장 닮았다.

### Cited Findings
- 앱 라이선스: "MIT License", "Copyright (c) 2020 The Odin Project" — [theodinproject license.txt](https://raw.githubusercontent.com/TheOdinProject/theodinproject/main/license.txt)
- 커리큘럼 라이선스: "This curriculum is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License"(링크 http://creativecommons.org/licenses/by-nc-sa/4.0/) — [curriculum license.md](https://raw.githubusercontent.com/TheOdinProject/curriculum/main/license.md)
- 커리큘럼 저장소 구성: 코스 폴더 `foundations, javascript, ruby, ruby_on_rails, react, nodeJS, databases/databases, git, intermediate_html_css, advanced_html_css, getting_hired, shared/the_back_end, templates, archive, markdownlint`; 루트에 `.markdownlint-cli2.jsonc`, `LAYOUT_STYLE_GUIDE.md`, `CONTRIBUTING.md`, `license.md`, `legal_terms_of_use.md`, `.codespellignore`. "This repo contains the actual lesson files used on our website." — [TheOdinProject/curriculum](https://github.com/TheOdinProject/curriculum)
- 레슨 레이아웃(LAYOUT_STYLE_GUIDE.md): 순서대로 `### Introduction`(필수), `### Lesson overview`(선택, 불릿 ≤7개), 커스텀 섹션(`### CUSTOM SECTION HEADING`), `### Assignment`(필수, 번호 목록 3–5개, `<div class="lesson-content__panel" markdown="1">`로 감쌈), `### Additional resources`(선택). 프로젝트 레슨은 `### Introduction` → 선택 사전 섹션 → `### Assignment`(패널 안, 요구사항/유저 스토리) → `#### Extra credit`. 헤딩 규칙: 주 섹션 `###`, 하위 `####`, 문장형 대소문자, "Headings must not end with `.`, `,`, `:` or `;`", 코드 금지, 일반 라벨("Note", "Warning") 금지. 노트 박스 `<div class="lesson-note" markdown="1">`(변형 `lesson-note--tip/--warning/--critical`). 링크는 "Instead of using HTML anchor tags for links, use Markdown links instead.", 필수 읽기 링크는 Assignment/Additional resources에만. 커스텀 markdownlint 규칙 TOP001–TOP013(`lesson-headings` TOP004, `default-section-content` TOP003, `descriptive-link-text-labels` TOP001, `use-markdown-links` TOP007, `fenced-code-language` MD040 등) — [curriculum LAYOUT_STYLE_GUIDE.md](https://raw.githubusercontent.com/TheOdinProject/curriculum/main/LAYOUT_STYLE_GUIDE.md)
- 앱 스택(Gemfile): `gem 'rails', '8.1.3'`, `gem 'pg', '~> 1.6'`, `gem 'devise', '~> 5.0'`, `gem 'omniauth-github', '~> 2.0.1'`, `gem 'omniauth-google-oauth2', '~> 1.2.1'`, `gem 'turbo-rails', '~> 2.0'`, `gem 'stimulus-rails', '~> 1.3'`, `gem 'octokit', '~> 10.0'`, `gem 'github_webhook', '~> 1.4'`, `gem 'kramdown', '~> 2.5'`, `gem 'kramdown-parser-gfm'` — [theodinproject Gemfile](https://raw.githubusercontent.com/TheOdinProject/theodinproject/main/Gemfile)
- 앱 스키마(db/schema.rb): `paths(title, short_title, slug unique, identifier_uuid unique, position, default_path, users_count)`; `courses(title, slug, identifier_uuid, position, path_id, description, badge_uri, lessons_count, projects_count, show_on_homepage)`; `sections(course_id, title, description, identifier_uuid, position)`; `lessons(title, slug[section_id별 unique], position, section_id, course_id, identifier_uuid[course_id별 unique], description, github_path string(255), is_project boolean default false, accepts_submission, previewable, installation_lesson, choose_path_lesson)`; `contents(lesson_id, body text not null)`; `lesson_previews(uuid, content)`; `lesson_completions(user_id, lesson_id, course_id, path_id, lesson_identifier_uuid)`(lesson_id+user_id unique); `project_submissions(user_id, lesson_id, repo_url, live_preview_url, is_public, likes_count, discarded_at)`; `flags(project_submission_id, flagger_id, reason, status, action_taken, resolved_by_id, extra)`; `users(email unique, encrypted_password, username, avatar, learning_goal text, path_id, banned)`; `user_providers(provider, uid, user_id)`; `admin_users(role enum: moderator/maintainer/core)` — [theodinproject db/schema.rb](https://raw.githubusercontent.com/TheOdinProject/theodinproject/main/db/schema.rb)

### Inferences
- 빌려올 것: (1) `identifier_uuid`를 path/course/section/lesson 모두에 두고 `lesson_completions.lesson_identifier_uuid`로 중복 보관하는 설계 — 레슨 행이 재생성/이동되어도 완료 이력이 보존된다. (2) `github_path` + `octokit` + `github_webhook` 조합은 "Git이 콘텐츠의 원천, DB는 렌더링 캐시(`contents.body`)"라는 동기화 모델로 추정된다(Gemfile 근거). 우리 플랫폼이 Markdown을 Git에 두고 CI/웹훅으로 DB에 적재하는 구조와 동일한 패턴. (3) markdownlint 커스텀 규칙(TOP0xx)으로 레슨 구조(필수 섹션, 헤딩 규칙, 링크 라벨)를 CI에서 강제하는 방식은 그대로 채택할 만하다. (4) `is_project`, `accepts_submission`, `project_submissions` 분리는 "레슨 완료"와 "결과물 제출"을 다른 테이블로 모델링하는 선례.
- 진도 모델이 "완료/미완료" 불리언 수준이라는 점은 우리가 FSRS로 확장하려는 "복습 상태"가 TOP에는 없음을 뜻한다. 즉 TOP의 `lesson_completions`는 FSRS `review_item`의 상위 개념(최초 완료 이벤트)으로 흡수할 수 있다.
- CC BY-NC-SA 콘텐츠는 상업적 재사용이 금지되므로 로보틱스 과정 본문에 TOP 텍스트를 복제하면 안 되며, 레이아웃 규약만 참고해야 한다.

### Gaps
- GitHub에서 레슨 본문을 가져와 `contents.body`에 넣는 실제 코드 경로(임포터/서비스 객체)는 읽지 않았다. Gemfile의 octokit/github_webhook는 정황 근거다.
- `LAYOUT_STYLE_GUIDE.md`에는 `### Knowledge check` 섹션이 등장하지 않았다(템플릿 파일 미열람).
- 레슨 Markdown 파일에 YAML frontmatter가 있는지는 확인하지 못했다(앱 DB의 `github_path`로 매핑하는 구조로 보아 frontmatter 의존도는 낮을 것으로 추정).

---

## B-4. Jupyter Book / MyST (mystmd) · Khan Academy 공개 코드

### Takeaway
mystmd는 MIT, Jupyter Book은 BSD-3-Clause이며 Jupyter Book 2는 MyST Document Engine 위에 구축됐다. 페이지 frontmatter와 `myst.yml`의 `project` 키가 같은 필드 집합을 공유하고 "page can override project" 우선순위 규칙이 명문화되어 있어, 우리 레슨 frontmatter 스키마와 코스 수준 기본값 상속 규칙을 설계할 때 참고 모델이 된다. 인증/진도 기능은 없다. Khan Academy의 Perseus는 MIT지만 외부 기여를 받지 않는 "참고용 공개"이며 연습문제 데이터는 비공개다.

### Cited Findings
- mystmd: "MIT license"; "Command line tools for working with MyST Markdown"; "a set of open-source, community-driven tools designed for scientific communication"; "As of v1.0.0 this package is ESM only." — [jupyter-book/mystmd](https://github.com/jupyter-book/mystmd)
- Jupyter Book LICENSE: "BSD 3-Clause License", "Copyright (c) 2024, Jupyter Book Project." — [jupyter-book/jupyter-book LICENSE](https://github.com/jupyter-book/jupyter-book/blob/main/LICENSE)
- jupyterbook.org: "Jupyter Book 2 is here!", "Built on the MyST Document Engine with faster builds, modern features, and improved workflows." "Upgrade from Jupyter Book 1 to 2" 링크와 "JBv1 documentation" 링크 존재 — [jupyterbook.org](https://jupyterbook.org/)
- MyST frontmatter: 페이지 frontmatter는 최상위 키, 프로젝트 설정은 `myst.yml`의 `project` 키 아래. 배치 범주 "page & project", "page only", "project only", "page can override project"("valid in both, with page values taking precedence"). page & project: `title, subtitle, short_title(≤40자), description, exports, downloads, tags, thumbnail, banner, parts`; page can override project: `date, keywords, authors, reviewers, editors, affiliations, doi, arxiv, pmid, pmcid, open_access, license, copyright, funding, github, edit_url, source_url, binder, subject, venue, volume, issue, first_page, last_page, math, abbreviations, numbering, options`; page only: `label, kernelspec, execute`; project only: `id, bibliography, references, requirements, resources, social, jupyter/thebe`. `title` 누락 시 첫 헤딩을 제목으로 사용, `title: null`이면 헤딩을 본문에 유지 — [mystmd.org: Frontmatter](https://mystmd.org/guide/frontmatter)
- Khan/perseus: "MIT License"; "Perseus is Khan Academy's exercise question editor and renderer."; "The Perseus project is not accepting external contributions."; "not open to pull requests or issues at this time." — [Khan/perseus](https://github.com/Khan/perseus)

### Inferences
- 빌려올 것: (1) frontmatter 필드를 "코스(프로젝트) 수준 기본값 ↔ 레슨(페이지) 수준 오버라이드"로 나누고 각 필드의 허용 위치를 표로 명세하는 방식. 우리 로보틱스 과정이라면 `license, authors, keywords, date`는 코스 기본값 + 레슨 오버라이드, `kernelspec/execute`에 해당하는 실습 실행 메타는 레슨 전용. (2) `exports`/`downloads`처럼 산출물(PDF 등)을 frontmatter에 선언하는 방식은 CI 빌드 타깃 선언에 응용 가능. (3) `short_title` 길이 제한 같은 린트 가능한 제약.
- Jupyter Book/MyST는 "정적 사이트 생성기"이므로 인증·진도는 전혀 없으며, 우리 플랫폼의 웹 렌더링 레이어로 MyST를 쓰고 진도/복습은 별도 API로 얹는 구성이 가능하다(Jupyter 노트북 기반 로보틱스 실습과의 궁합도 좋다).
- Khan Academy는 "진짜 오픈"이 아니다: Perseus 렌더러는 MIT지만 외부 기여 차단, 연습문제 콘텐츠는 비공개(검색 결과에 따르면 구 khan-exercises 연습문제는 CC 비상업 라이선스) — 벤치마크에서 제외해도 무방하다.

### Gaps
- mystmd의 현재 버전 번호와 `myst.yml`의 `site`/`toc` 구조는 가져온 페이지에 없었다.
- Jupyter Book 2의 정확한 릴리스 버전/날짜와 Jupyter Book 1(Sphinx 기반)의 지원 종료 일정은 확인하지 못했다.
- Khan Academy의 다른 공개 저장소(KaTeX 등)는 범위 밖으로 조사하지 않았다.

---

## C-1. xAPI / cmi5 / SCORM 의 2026년 현황과 오픈소스 LRS

### Takeaway
xAPI는 IEEE 9274.1.1-2023(xAPI 2.0, 2023-03-30 승인, 2023-10-06 발행)으로 표준화됐고, 오픈소스 LRS로는 Yet Analytics의 lrsql(Apache-2.0, SQLite/Postgres, xAPI 1.0.3과 2.0.0 동시 지원)이 적합하다. cmi5는 공식 릴리스가 여전히 "Quartz, 1st Edition (June 2016)"이고 IEEE P9274.3.1은 2023-02-15 PAR 승인 후 작업 중으로, 2026-11 현재 발행 확인이 안 된다. SCORM은 ADL 1차 소스를 가져오지 못했으나 2차 소스는 2004 4th Edition이 마지막이고 ADL이 xAPI/cmi5로 초점을 옮겼다고 본다.

### Cited Findings
- IEEE SA: "IEEE 9274.1.1-2023", "IEEE Standard for Learning Technology--JavaScript Object Notation (JSON) Data Model Format and Representational State Transfer (RESTful) Web Service for Learner Experience Data Tracking and Access", "Active Standard", Board approval "2023-03-30", publication "2023-10-06". 초록은 "collaborative effort to improve and standardize the 1.0.3 version"으로 기술. "IEEE SA Open Source Project"(opensource.ieee.org/xapi), "Open Source CLA" Apache 2.0; 문서 자체는 Purchase/Subscription 옵션으로 표시 — [IEEE SA: 9274.1.1-2023](https://standards.ieee.org/ieee/9274.1.1/7321/)
- Wikipedia: xAPI는 2013년 4월 1.0 릴리스; 현재 버전은 IEEE 9274.1.1-2023("also referred to as xAPI 2.0"), 2023-10-10 릴리스로 기재(IEEE 페이지의 10-06과 날짜 상이); "meant to succeed SCORM"; LRS는 "can exist within traditional learning management systems (LMSs) or on their own"; 문장은 "actor verb object" — [Wikipedia: Experience API](https://en.wikipedia.org/wiki/Experience_API)
- 검색 결과(2차): ISO/IEC/IEEE 39274-1-1:2025가 2025년 10월 국제 채택으로 발행됨; xAPI 2.0.0이 "breaking change"라는 벤더 주장과 "many changes are additive"라는 주장이 충돌 — [검색 요약, 출처: xapi.com/ADL/IEEE 결과 모음](https://adlnet.gov/news/2023/11/22/xAPI-Officially-Becomes-a-Published-IEEE-Standard) (해당 ADL 페이지는 직접 fetch 시 연결 거부로 본문 미확인)
- xAPI 문장 모델(Rustici "Statements 101"): actor는 `name`, `mbox` 또는 `account{homePage, name}`("Only "mbox" uniquely describes this Sally."); verb는 `id` IRI + `display`("Verbs in xAPI are URIs, and should be paired with a short display string."); object(Activity)는 `id` + 선택 `definition{type, name, description, extensions}`("All activities must be uniquely defined by an URI"); result는 `completion, success, score{scaled | raw, min, max}, response, duration`; context는 `instructor, contextActivities{parent, grouping}, extensions`; extensions 키는 URI; `timestamp`는 발생 시스템이 설정, `stored`는 LRS가 설정("The "stored" field is hence always set by the LRS."), `authority`는 문장 작성 주체 — [xapi.com: Statements 101](https://xapi.com/statements-101/)
- lrsql: "Distributed under the Apache License version 2.0", "Copyright © 2021-2026 Yet Analytics, Inc.", "A SQL-based Learning Record Store", LRS는 "a persistent store for xAPI statements and associated attachments and documents". 지원 DB: SQLite(3.42 임베디드), Postgres 14–18, MariaDB/MySQL도 표에 기재. OpenID Connect 지원과 Auth0 설정 가이드 링크 — [yetanalytics/lrsql](https://github.com/yetanalytics/lrsql); "SQL LRS supports xAPI versions 1.0.3 and 2.0.0." 기본 둘 다 지원, `LRSQL_SUPPORTED_VERSIONS`/`supportedVersions`로 조정, "The version used is determined by the `X-Experience-API-Version` header in the request." — [lrsql doc: xAPI Versioning](https://github.com/yetanalytics/lrsql/blob/main/doc/xapi_versioning.md)
- cmi5: "Current Release: Quartz, 1st Edition (June 2016)"; "cmi5 is a "profile" for using the xAPI specification with traditional learning management (LMS) systems."; 저장소 라이선스 "Apache-2.0 license" — [AICC/CMI-5_Spec_Current](https://github.com/AICC/CMI-5_Spec_Current)
- cmi5 IEEE 진행: P9274.3.1 "xAPI cmi5 Working Group", PAR 승인 2023-02-15, 범위는 세션 기반 학습에서 xAPI의 패키징·런치·런타임 표준 — [IEEE SA: P9274.3.1](https://standards.ieee.org/ieee/9274.3.1/11183/), [IEEE SA groups: 9274-3-1](https://sagroups.ieee.org/9274-3-1); 2026년 승인/발행 증거는 검색에서 발견되지 않음(검색 요약)
- SCORM(2차, 벤더 구매 가이드): SCORM 2004 4th Edition(2009-03)이 마지막 릴리스이고 후속 버전 계획 없음, ADL은 xAPI/cmi5로 전환; cmi5 현행판은 2016 Quartz 1st Edition이며 "there is no cmi5 2.0"; 기업 컴플라이언스에서는 여전히 SCORM이 기본 — [learnsignal: SCORM, xAPI and cmi5 buyer's guide](https://www.learnsignal.com/blog/scorm-xapi-cmi5-elearning-standards-buyers-guide/)

### Inferences
- Markdown-first 플랫폼이 xAPI를 채택할 때의 최소 매핑(추론): actor=`account{homePage: 플랫폼 URL, name: user id}`(이메일 mbox 노출 회피), verb=ADL 표준 verb IRI(completed/passed/failed/experienced 등은 cmi5 정의 동사 집합 활용), object=`https://<platform>/lessons/<uuid>`(레슨 UUID를 Activity IRI로), result=`completion/success/score.scaled`, context.contextActivities.parent=모듈, grouping=코스, extensions에 FSRS 평점/안정성(URI 키). 이렇게 하면 lrsql(SQLite 모드)을 사이드카로 붙여 기업 LRS로 내보내기가 가능하다.
- cmi5는 "LMS가 콘텐츠를 런치하고 LRS에 기록" 모델이라 SCORM 패키지의 대체재지만, 공식판이 2016년이고 IEEE판이 미발행이므로 2026-11 시점에는 "xAPI 문장 호환 + cmi5 정의 동사 채택" 정도로만 반영하고 cmi5 패키징(course structure XML, AU 런치)은 보류하는 것이 합리적이다.
- SCORM은 우리처럼 LMS 밖에서 동작하는 독립 플랫폼에는 맞지 않으며(패키지 런타임 전제), 기업 LMS 임베딩 요구는 LTI 1.3(C-2)로 푸는 것이 2026 기준 표준적이다.

### Gaps
- ADL 공식 페이지(adlnet.gov)는 연결 거부로 SCORM 공식 상태 문구와 xAPI IEEE 뉴스 원문을 확인하지 못했다. SCORM 관련 서술은 전부 2차 소스다.
- cmi5 정의 동사 목록(launched, initialized, completed, passed, failed, abandoned, waived, terminated)과 course structure XML은 저장소 랜딩 페이지에 없어 `cmi5_spec.md` 원문 확인이 필요하다.
- xAPI 2.0 vs 1.0.3의 구체적 변경 목록과 ISO/IEC/IEEE 39274-1-1:2025의 1차 소스는 확인하지 못했다.
- lrsql의 ADL 적합성 인증 여부와 최신 릴리스 번호는 README에 없었다.

---

## C-2. LTI 1.3 / LTI Advantage (기업 LMS 임베딩)

### Takeaway
LTI 1.3 Core는 1EdTech(구 IMS) Final Release(문서 버전 3, 2019-04-16)이며 OpenID Connect + 서명 JWT + OAuth 2.0 기반이다. LTI Advantage는 Deep Linking 2.0, AGS 2.0, NRPS 2.0로 구성되고 Dynamic Registration 1.0, Course Group Service 1.0은 Public Candidate Final이다. Python 구현체 pylti1.3(MIT)은 Django/Flask 어댑터를 제공하나 PyPI 최신이 2.0.0(2022-11-20)으로 3년간 릴리스가 없다.

### Cited Findings
- 스펙 메타: "Learning Tools Interoperability Core Specification 1.3", IMS Final Release, Document Version 3, Date Issued 16 April 2019. LTI v1.3은 "builds on LTI v1.1 by incorporating a new model for security for message and service authentication"; 보안은 "using OpenID Connect, signed JWTs, and OAuth2.0 workflows for authentication"; "Access tokens MUST protect all the services described by the platform." 리소스 링크 런치 필수 클레임: `message_type`(=`LtiResourceLinkRequest`), `version`("the claim must have the value `1.3.0`"), `deployment_id`, `target_link_uri`, `resource_link{id}`, `roles[]`, `sub`(익명 런치 제외). Deep Linking은 별도 스펙(LTI-DL-20); Basic Outcomes 대안으로 "more fully featured LTI Assignment and Grade Service" 언급; "away from the use of OAuth 1.0a-style signing" — [1EdTech: LTI 1.3 Core](https://www.imsglobal.org/spec/lti/v1p3)
- 1EdTech LTI 페이지: "The current version, LTI 1.3, addresses education security requirements and provides a structure for additional services." LTI Advantage 구성: Assignment and Grade Services 2.0, Names and Role Provisioning Services 2.0, Deep Linking 2.0. 선택 서비스: Dynamic Registration 1.0("Public Candidate Final"), LTI postMessage Storage 1.0(v0p1), Course Group Service 1.0("Public Candidate Final"). 인증: "LTI Advantage Certification Suite", "LTI Advantage Conformance Certification Guide", 신규 "Diagnostic & Certification Suite"(BUILD.1EDTECH.ORG, 로그인 필요), 구 "Reference Implementation & Certification Suite"는 "LEGACY" — [1EdTech: LTI](https://www.1edtech.org/standards/lti)
- pylti1.3: MIT; "LTI 1.3 Advantage Tool"; "This library contains adapters for use with the Django and Flask web frameworks."; `OIDCLogin`/`MessageLaunch` 재구현으로 타 프레임워크 적용 가능; 문서에 Deep Linking 응답, Names and Roles Service, Assignments and Grades Service, Data Privacy launch, Submission Review, Course Group Service 섹션; `from pylti1p3.tool_config import ToolConfJsonFile`, `DjangoMessageLaunch`/`FlaskMessageLaunch`, `message_launch.get_deep_link()`, `DeepLinkResource` — [dmitry-viskov/pylti1.3](https://github.com/dmitry-viskov/pylti1.3); PyPI 최신 2.0.0, "Nov 20, 2022", "MIT License (MIT)", Python 3.6–3.11 classifiers, "LTI 1.3 Advantage Tool implementation in Python" — [PyPI: PyLTI1p3](https://pypi.org/project/PyLTI1p3/)

### Inferences
- 우리 플랫폼이 기업 LMS(Canvas/Moodle 등) 안에서 "도구(Tool)"로 열리려면 OIDC 로그인 엔드포인트 + 런치 JWT 검증 + (선택) AGS로 완료/점수 회신이 필요하다. 레슨 UUID를 `target_link_uri`/`resource_link`에 매핑하고 Deep Linking으로 LMS 측에서 레슨을 골라 배치하게 하면 모듈→레슨 구조와 잘 맞는다.
- 자체 인증(이메일/OIDC)과 LTI 런치 인증은 별도 경로로 두되, LTI `sub`+`deployment_id`를 로컬 사용자에 연결하는 매핑 테이블이 필요하다(TOP의 `user_providers(provider, uid)` 패턴 재사용 가능).
- pylti1.3는 기능은 완전하지만 2022년 이후 릴리스가 없고 Python 3.11까지만 분류돼 있어, Python 백엔드라면 포크/벤더링 또는 다른 라이브러리 검토가 필요하다. Node/TS 백엔드용 LTI 라이브러리는 이번 조사 범위 밖이다.

### Gaps
- LTI 1.1 공식 폐기/인증 종료 날짜는 가져온 두 페이지에 명시되지 않았다.
- LTI 1.3 Core 이후의 소수점 개정(1.3.x) 존재 여부와 NRPS 세부는 스펙 페이지가 잘려 확인하지 못했다.
- pylti1.3의 1EdTech 인증 여부, 그리고 Node.js/TypeScript용 LTI 1.3 라이브러리는 조사하지 않았다.

---

## C-3. Open Badges 3.0 / Verifiable Credentials (수료증·배지)

### Takeaway
Open Badges 3.0은 1EdTech Final Release이며 문서 버전 1.4.5(2026-06-29)까지 개정됐고, 배지(Assertion)가 곧 W3C Verifiable Credential(Data Model v2.0 정렬)이다. 증명 포맷은 JWT와 Linked Data Proof 두 가지. 오픈소스 발급기로는 Certo(AGPL-3.0, Strapi 5 + Nuxt 3)와 CredTrail(Longsight; did:web + Ed25519 + Data Integrity 증명으로 소개)이 있으나 성숙도는 검증 필요.

### Cited Findings
- 스펙: "Open Badges Specification", Spec Version 3.0, Final Release, Document Version 1.4.5, 2026-06-29 발행, "This document is made available for adoption by the public community at large." 초록: "aligns with the conventions of the Verifiable Credentials Data Model v2.0"; "Starting with this version of the Open Badges Specification, an Assertion is also a Verifiable Credential (VC)."; 데이터 모델 클래스 Achievement("the content description of a credential that an assertion references"), AchievementCredential, AchievementSubject, EndorsementCredential; 검증 절에서 "OpenBadgeCredential" 용어 사용; 증명 포맷 8.2 "JSON Web Token Proof Format", 8.3 "Linked Data Proof Format"; JSON-LD 컨텍스트 `context-3.0.3.json`; 초록에 "easily be bundled into Comprehensive Learner Records" — [1EdTech: Open Badges 3.0](https://www.imsglobal.org/spec/ob/v3p0/)
- 1EdTech 인증 가이드 존재: "Open Badges Specification Conformance and Certification Guide" v3p0 — [1EdTech: OB 3.0 Cert Guide](https://standards.1edtech.org/open-badges/specifications/standards/v3p0/cert)
- Certo: "This project is licensed under the GNU Affero General Public License v3.0"; "An open source project for courses, workshops and conferences organizers to create certifications using Open Badges 3.0"; 백엔드 "Strapi 5.15.0, TypeScript 5.x, Node.js 18-22.x", 프런트 "Nuxt 3 frontend (Vue 3 + TypeScript + Una UI)", DB PostgreSQL(prod)/SQLite(dev), JWT(jose). 기능: 발급(`POST /api/credentials/batch-issue` CSV 일괄), 검증(`POST /api/credentials/verify`, "cryptographic proofs and the Verifiable Credentials model"), 폐기(`GET /api/revocation-list/check/:id`). DID 방식·서명 알고리즘은 README에 미기재 — [schroedinger-hat/certo](https://github.com/schroedinger-hat/certo)
- CredTrail(2차, 검색): Longsight의 오픈소스 OB3 플랫폼으로 Cloudflare SaaS/Docker self-host 프로필과 공개 검증 엔드포인트를 설명; 참조 구현이 "issuer did:web identifiers, Ed25519 signing, and W3C Data Integrity proofs" 사용 — [Longsight: credential signing stack](https://www.longsight.com/blog/credential-signing-stack)
- Open edX 커뮤니티(2차): edubadges(Badgr 포크), openbadges-modular-server 등은 주로 OB 2.0 시대 도구이며 "none of these solutions are battle-tested in production within the Open edX community" — [Open edX discuss: badging and VCs](https://discuss.openedx.org/t/common-questions-about-badging-and-verifiable-credentials-in-open-edx-teak-ulmo/18434)

### Inferences
- 소규모 플랫폼의 현실적 경로(추론): 코스/모듈 수료를 `AchievementCredential`(JWT proof, 발급자 키는 `did:web:<platform domain>`)로 발급하고, 검증 엔드포인트와 폐기 목록만 제공하면 OB 3.0 데이터 모델 호환 "수료증"이 된다. Certo를 통째로 붙이는 것은 AGPL + Strapi/Nuxt 스택 부담이 커서, 데이터 모델과 API 형태(issue/verify/revoke)만 참고하는 편이 낫다.
- TOP의 `courses.badge_uri` 컬럼은 코스별 배지 이미지/URI를 두는 선례로, OB 3.0의 `Achievement.image`에 대응시킬 수 있다.

### Gaps
- OB 3.0 1.4.5의 개정 이력(3.0.x 변경점)과 CLR 2.0 정렬 여부는 페이지 뒷부분을 읽지 못해 확인하지 못했다.
- Certo의 DID 메서드/서명 스위트, CredTrail의 라이선스는 1차 소스로 확인하지 못했다(CredTrail 저장소 미열람).
- OB 3.0 발급자 인증(1EdTech 인증 제품 목록)은 조사하지 않았다.

---

## C-4. FSRS를 플래시카드 밖(노트·문서·레슨)에서 쓰는 오픈소스 사례와 통합 패턴

### Takeaway
FSRS는 "콘텐츠 무관"한 상태 전이 함수이므로 노트·아티클·레슨 단위 복습에 그대로 적용한 사례가 다수 있다(Obsidian Note Spaced Repetition, Logseq, Org-srs, SiYuan, 증분 읽기 앱 Foliole/ZKMemo/Bundle). 다만 "코스의 레슨"을 FSRS로 재방문 스케줄링한 전용 오픈소스 플랫폼은 찾지 못했으며, 가장 가까운 선례는 Obsidian/Emacs의 노트 단위 리뷰다.

### Cited Findings
- awesome-fsrs 응용 목록 중 노트/문서 리뷰: Logseq(cljc-fsrs, "A privacy-first, open-source platform for knowledge management"), Obsidian 플러그인 obsidian-spaced-repetition-recall(FSRS-6), HiNote(FSRS-6), LearnKit(FSRS-6, "brings flashcards, note review, tests, and AI-assisted study tools into Obsidian"), True Recall(ts-fsrs), Org-srs/Org-fc(Emacs, FSRS-6 실험), RemNote(FSRS-4.5), SiYuan(FSRS-5, riff), TiddlyWiki(fsrs4tw), ZKMemo("combines FSRS-based spaced repetition with incremental reading"); 증분 읽기: Foliole("Native incremental reading with integrated FSRS scheduling", ts-fsrs), Bundle("read-later app for iPhone that helps you remember what you read"); 코스/레슨형: Japanese Learning("a web course for German speakers preparing for JLPT N5: lessons on kana, vocabulary, kanji and grammar", py-fsrs), BiliMind Desktop("turns a folder of lecture slides, past exam papers or notes into a course", ts-fsrs 5.4.2, AGPL-3.0), Verbamor(레슨 녹음→플래시카드). 라이선스 표기된 예: Etude(MIT), Jiaci(MIT), Ordkort(AGPL-3.0), Read Frog(GPLv3) — [open-spaced-repetition/awesome-fsrs](https://github.com/open-spaced-repetition/awesome-fsrs)
- Obsidian "Note Spaced Repetition" 플러그인: 카드가 아니라 노트 전체를 FSRS/SM-2로 리뷰 — [Obsidian plugin: note-spaced-repetition](https://community.obsidian.md/plugins/note-spaced-repetition)
- HN 토론(2차): FSRS는 "content-agnostic and deck-agnostic"이어서 다른 시스템에 끼우기 쉽지만 그만큼 모델 적합도는 다소 낮아진다는 의견 — [hn.svelte.dev item 44790422](https://hn.svelte.dev/item/44790422)
- 라이브러리 API(재확인): py-fsrs `scheduler.review_card(card, rating)` → `(card, review_log)`; `Optimizer(review_logs)`; `compute_optimal_retention` — [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs); ts-fsrs `DefaultScheduler().review({card, grade, now})`, `preview` — [ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs); fsrs-rs `next_states(previous_state, desired_retention, elapsed_days)` — [fsrs-rs](https://github.com/open-spaced-repetition/fsrs-rs)
- Anki 운영 지침(재확인): 학습 단계는 1일 미만 유지, 옵티마이저는 월 1회면 충분, desired retention 기본 90%·97% 미만 권장, "Historical Retention"으로 누락 이력 보정 — [Anki manual: Deck Options](https://docs.ankiweb.net/deck-options.html)

### Inferences
- 레슨 단위 FSRS 통합 패턴(추론, 위 사례들의 공통 구조에서 도출): (1) 복습 단위 = 레슨 UUID(또는 레슨 내 "knowledge check" 문항들). (2) 최초 완료 시 FSRS 새 카드 생성(`newCard`/`Card()`), 이후 due 도달 시 레슨 요약/퀴즈를 보여주고 Again/Hard/Good/Easy 자가평가 → `review` → `{s, d, decay, due, last_review}` 갱신 + review_log 추가. (3) desired retention은 코스 기본 0.9, 사용자 오버라이드 허용. (4) 파라미터는 사용자당 1벌(Anki의 프리셋 단위에 대응) 또는 코스당 1벌로 시작, 로그가 충분히 쌓이면 월 1회 `Optimizer`로 재학습. (5) 평점 척도는 FSRS 표준 1–4를 유지해야 라이브러리/옵티마이저와 호환된다.
- "레슨 1개 = 카드 1장"으로 두면 신호가 거칠고(HN의 적합도 하락 지적과 같은 맥락) 레슨 내부 문항을 카드로 쪼개면 Anki에 가까워진다. Exercism의 `concepts`처럼 레슨이 가르치는 "개념" 단위를 복습 아이템으로 삼는 중간안이 설계상 합리적으로 보인다(추론).
- Markdown-first 플랫폼은 Obsidian 플러그인들처럼 "리뷰 상태를 Markdown 파일 안(frontmatter)에 쓰는" 방식도 가능하나, 다중 사용자 서버에서는 상태를 DB에 두고 콘텐츠만 Git에 두는 분리가 필요하다(Retrieva/Note SR는 단일 사용자 vault 전제).

### Gaps
- "코스 레슨"을 FSRS로 스케줄링하는 전용 오픈소스 플랫폼(인증·다중 사용자 포함)은 검색에서 찾지 못했다. awesome-fsrs의 Japanese Learning/BiliMind는 코스 형태지만 상세 구조·라이선스를 열람하지 않았다.
- 레슨 단위 FSRS의 효과(플래시카드 대비 보존율)를 다룬 연구나 벤치마크는 찾지 못했다(검색 결과의 Duolingo half-life regression 언급은 FSRS가 아닌 별개 알고리즘).
- FSRS-7의 레슨 리뷰 적합성(혹은 7에서 달라진 모델 가정)은 알고리즘 문서 미확인으로 판단 불가.
