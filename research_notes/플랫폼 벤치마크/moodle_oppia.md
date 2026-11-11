# Moodle · Oppia 플랫폼 벤치마크 (2026-11-11 기준)

> 범위: 소규모 오픈소스 커리큘럼 플랫폼(단일 "robotics expert course", module → lesson, Markdown + frontmatter 레슨, 학습자 진행 추적, 향후 auth/API/web/CI)의 설계 레퍼런스로서 Moodle LMS와 Oppia를 조사. 모든 URL은 2026-11-11에 실제로 fetch했거나 fetch한 페이지에 그대로 적힌 링크만 사용. 검색 스니펫에서만 확인한 내용은 "(검색 스니펫 기준)"으로 표시.

---

## KQ1. 라이선스 · 현재 버전 · 릴리스 주기 · CLA · 거버넌스

### Takeaway
Moodle은 GPL-3.0(핵심 저장소 COPYING.txt = GPLv3 전문, GitHub 라이선스 감지 GPL-3.0)이며 2026-10-05 출시된 5.3이 차기 LTS·현재 안정 버전이고, 6개월 메이저/2개월 마이너 주기로 Moodle HQ(Moodle Pty Ltd)가 주도한다. Oppia는 Apache-2.0이며 2026-09-23 공개된 v3.5.3이 최신 릴리스이고, 월간 릴리스(매월 첫 수요일 cut)·CLA 필수·Oppia Foundation(501(c)(3), EIN 81-1740068)이 운영한다. Moodle은 별도 CLA를 요구한다는 근거를 찾지 못했고(저작권이 "수백 명의 저자"에게 분산), Oppia는 "CLA 미서명 시 PR을 닫는다"고 명시한다.

### Cited Findings
**Moodle**
- `COPYING.txt`는 "GNU GENERAL PUBLIC LICENSE, Version 3, 29 June 2007" 전문이며, 14조에 "or any later version" 선택 조항이 포함된 표준 GPLv3 텍스트다 — [moodle/moodle COPYING.txt](https://raw.githubusercontent.com/moodle/moodle/main/COPYING.txt)
- GitHub API 기준 moodle/moodle의 license spdx_id는 `GPL-3.0`("GNU General Public License v3.0"), default_branch `main`, stars 7,600 / forks 7,711, 마지막 push 2026-10-30 — [api.github.com/repos/moodle/moodle](https://api.github.com/repos/moodle/moodle)
- Standards 페이지: Moodle은 "free, open source software" under the GNU General Public License — [Standards](https://docs.moodle.org/en/Standards)
- 버전 지원 표(2026-10-04 갱신): 4.5(LTS, 2024-10-07 출시, 보안지원 2027-10-04), 5.1(2025-10-06), 5.2(2026-04-20, 최신 포인트 5.2.3 2026-09-14), **5.3(LTS, 2026-10-05 출시, 보안지원 2029-10-01)**, 6.0(2027-04-19 예정), 6.1(2027-10-04 예정). "The next LTS version will be Moodle 5.3." 메이저 릴리스는 매 6개월(4월/10월), 마이너는 2개월마다 — [Moodle releases](https://moodledev.io/general/releases)
- 5.3 릴리스 노트: 출시일 2026-10-05, "Moodle 5.3 (LTS)"로 표기, Classic 테마 core에서 제거, Anthropic Claude AI provider 플러그인 추가, 학습성과(Learning outcomes) 도입, OAuth 2 server/client/token 관리와 routed web services 로그인 흐름 — [Moodle 5.3 release notes](https://moodledev.io/general/releases/5.3)
- 개발 프로세스: "Every change must have an issue in the tracker." HQ component lead가 peer review → "the integration team (a small team of senior developers employed by Moodle HQ)"가 통합 리뷰 → 전담 테스터가 테스트 → 매주 목요일 production maintainers가 머지. 이 페이지에는 CLA/저작권 양도 요구가 언급되지 않음 — [Development process](https://moodledev.io/general/development/process)
- 기여 가이드: 아이디어는 moodle.org 포럼 토론 → tracker "New feature/Improvement" 이슈 → 투표/펀딩 → 로드맵. "Moodle LMS Community Product Advisory Group"으로 로드맵에 영향 가능. 플러그인은 marketplace.moodle.com에 등록. CLA 언급 없음 — [Contributing](https://moodledev.io/general/community/contribute)
- 라이선스 변경 가능성 FAQ: "The copyrights belong to hundreds of authors and they would ALL need to agree to any change in the license." 핵심 개발자는 "Moodle Pty Ltd"이며 회사가 해산되어도 "the software would not be affected", 커뮤니티가 포크 가능 — [Future (dev FAQ)](https://docs.moodle.org/dev/Future)
- moodle.org 사이트 정책(policyid=4)은 CLA가 아니라 사이트 이용약관이며, 업로드 콘텐츠에 대해 "a non-exclusive, irrevocable, worldwide, royalty-free licence"를 Moodle에 부여하되 "does not supersede the terms of any open source licence you may explicitly apply" — [Moodle.org Site Policy](https://moodle.org/admin/tool/policy/view.php?policyid=4)
- Moodle Users Association(MUA): 2015년 설립된 비영리, 회원 구독료로 Moodle HQ가 개발하는 프로젝트를 펀딩(20개 프로젝트, 100만 AUD 이상). "MUA membership voted in late 2024 to dissolve the MUA." 후속은 Moodle LMS Product Advisory Group(PAG) — [moodle.org/mua](https://moodle.org/mua)
- Moodle Pty Ltd는 상표 소유자이자 Certified B Corporation; Certified Partners가 호스팅/커스터마이징 서비스 제공; UNESCO Global Education Coalition 회원 — [moodle.com/about](https://moodle.com/about/)

**Oppia**
- `LICENSE` 파일은 "Apache License, Version 2.0, January 2004" 전문(저작권 라인은 템플릿 "[yyyy] [name of copyright owner]"로 남아 있음) — [oppia/oppia LICENSE](https://raw.githubusercontent.com/oppia/oppia/develop/LICENSE)
- README: "The Oppia code is released under the Apache v2 license." 기술 스택 Python, Angular, Google App Engine; stars 약 7.0k, forks 5.9k, develop 브랜치 17,043 commits — [github.com/oppia/oppia](https://github.com/oppia/oppia)
- 최신 릴리스 `v3.5.3` ("Version 3.5.3") published_at 2026-09-23T12:40:52Z, author mon4our — [GitHub API releases/latest](https://api.github.com/repos/oppia/oppia/releases/latest); 릴리스 목록: v3.5.3(9/23), v3.5.2(7/20), v3.5.1(4/09), v3.5.0(3/05), v3.4.9(12/24) — [Releases](https://github.com/oppia/oppia/releases); v3.5.3 노트는 학습자/제작자 버그픽스 중심 — [v3.5.3](https://github.com/oppia/oppia/releases/tag/v3.5.3)
- `package.json`의 `"version": "3.5.4"` (develop 브랜치, 차기 버전) — [package.json](https://raw.githubusercontent.com/oppia/oppia/develop/package.json)
- 릴리스 주기: "Oppia releases happen monthly, and are typically cut on the first Wednesday of each month." cut → QA 1주 → 배포 1주; 월별 release coordinator가 테스트/프로덕션 서버 배포 담당; 회귀는 fix-forward보다 revert 선호 — [Release schedule](https://github.com/oppia/oppia/wiki/Release-schedule-and-other-information)
- CLA: 개인/기업 CLA 폼 서명 필수. "If you do not sign the CLA, any PRs you open will be closed." GitHub 2FA 필수, "Impact: High/Medium" 라벨 이슈만 신규 기여자 착수 가능 — [Contributing code to Oppia](https://github.com/oppia/oppia/wiki/Contributing-code-to-Oppia)
- Oppia Foundation Inc: EIN 81-1740068, 501(c)(3), Sacramento CA, NTEE Education N.E.C., 면세 승인 2016-03, 최근 신고 FY2025 Form 990-EZ(2026-04-29 제출), 수입 $124,178 — [ProPublica Nonprofit Explorer](https://projects.propublica.org/nonprofits/organizations/811740068)

### Inferences
- Moodle은 "GPL-3.0+"로 흔히 표기되지만 저장소 루트 COPYING.txt는 GPLv3 전문일 뿐이며 "or later"는 각 소스 파일 헤더에 적히는 관행이다. 파일 헤더(lib/moodlelib.php, version.php)는 raw.githubusercontent에서 404로 확인 실패 → "GPL-3.0-or-later" 여부는 파일 헤더를 직접 열어 확인 필요.
- Moodle은 CLA 없이 GPL 기여를 받고 저작권을 기여자가 보유하는 모델로 보인다(Future FAQ의 "hundreds of authors" 발언, 프로세스 문서의 CLA 부재). 반면 Oppia는 CLA로 재라이선스 여지를 확보한다. 소규모 플랫폼은 초기에 CLA 없이 DCO(Signed-off-by) 수준으로 시작해도 되지만, Apache-2.0을 택하면 특허 조항으로 기여 리스크가 줄어든다.
- Oppia의 "3.5.x" 번호는 월간 릴리스와 1:1이 아니며(2026년 1~9월에 4개 릴리스), 위키상 cadence(월간)와 실제 공개 릴리스 빈도(약 2~4개월)가 어긋난다. "November is marked Skipped"처럼 건너뛰는 달도 있다.

### Gaps
- Moodle 소스 파일 헤더의 정확한 라이선스 문구(“either version 3 … or any later version”)는 raw.githubusercontent 404로 직접 확인하지 못함.
- Moodle 공식 "CLA 없음" 명시 문서는 찾지 못함(부재 근거만 수집). Oppia CLA 폼의 구체 조항(저작권 양도 vs 라이선스)은 폼 자체를 열지 않아 미확인.
- Oppia Foundation 공식 소개 페이지(oppia.org/about-foundation)는 404; 이사회 구성은 제3자 집계 사이트에만 있어 인용하지 않음.

---

## KQ2. 인증(Authentication) 모델 — 로그인 방식

### Takeaway
Moodle 5.3 core는 Manual, Email self-registration, External DB, LDAP, LTI, OAuth 2(OIDC discovery 지원), Shibboleth, Web services, No login, MFA 등 플러그인형 인증을 제공하고 SAML2는 Catalyst의 서드파티 `auth_saml2`(설치 4,796 사이트, Moodle 2.7–5.1 지원)로 해결한다. Oppia는 자체 로그인 폼 없이 Firebase Authentication(OpenID Connect 1.0)에 위임하며, ID 토큰 → HttpOnly 세션 쿠키(14일) 방식이다.

### Cited Findings
**Moodle**
- 인증 플러그인 목록(5.3 docs): Manual accounts, No login, Email-based self-registration, External database, LDAP, LTI, No authentication, OAuth 2, Shibboleth, Web services, Multi-factor authentication. 5.2부터 로그인 관련 설정이 "Login settings" 페이지로 이동 — [Managing authentication](https://docs.moodle.org/en/Managing_authentication)
- OAuth 2 services 사전 설정 제공자: Google, Microsoft, Facebook, Nextcloud, MoodleNet, Open Badges, LinkedIn, Clever. 커스텀 발급자가 "Open ID Connect compliant"면 base URL만 입력하면 `<issuer base url>/.well-known/openid-configuration` discovery 문서로 나머지 설정을 가져온다 — [OAuth 2 services](https://docs.moodle.org/en/OAuth_2_services)
- 플러그인 타입 표에 `auth`(/auth), `enrol`(/enrol) 포함(총 56종) — [Plugin types](https://moodledev.io/docs/apis/plugintypes)
- Standards 페이지: LDAP는 "the most widely used standard protocol for authentication"; Shibboleth, IMAP, NNTP, FirstClass, direct DB lookup도 인증 대안으로 열거; OAuth2/OIDC/SAML은 이 페이지에 없음 — [Standards](https://docs.moodle.org/en/Standards)
- SAML2: 서드파티 플러그인 `auth_saml2`(Catalyst IT, Brendan Heywood, Rossco Hellmans), 최신 릴리스 2026-04-02, 지원 Moodle 2.7–5.1, 설치 4,796 사이트, "completely embeds a SimpleSamlPHP instance as an internal dependancy", back-channel Single Logout 지원 — [auth_saml2 (Moodle marketplace)](https://marketplace.moodle.com/plugins/auth_saml2)
- LTI 인증 플러그인은 "Publish as LTI tool" 등록 플러그인과 짝을 이뤄 원격 플랫폼 사용자가 Moodle 콘텐츠에 접근하게 하며, LTI Advantage는 보안을 OAuth 1.0에서 "OAuth 2.0 and OpenID Connect"로 이동 — [Publish as LTI tool](https://docs.moodle.org/en/Publish_as_LTI_tool)
- 5.3: "OAuth 2: Server, client, and token management, plus login flows for routed web services" — [Moodle 5.3 release notes](https://moodledev.io/general/releases/5.3)

**Oppia**
- `firebase_auth_services.py` docstring: "Oppia depends on OpenID Connect 1.0 to handle user authentication." Firebase가 자격증명 저장과 IdP 연결을 담당; 예시 IdP "Google, Facebook, Email verification links, and Text message SMS codes". `auth_id`는 `sub` 클레임에서 가져오며 "locally unique and never reassigned". ID 토큰은 `Authorization: Bearer`로 전달되어 세션 생성에만 쓰이고, `establish_auth_session`이 Firebase 세션 쿠키(HttpOnly, 에뮬레이터 아니면 secure)로 교환; `verify_session_cookie`는 `check_revoked=True`. super admin은 `ADMIN_EMAIL_ADDRESS` 플랫폼 파라미터 일치 또는 Firebase custom claim `role == super_admin`. "Users have ZERO CONTROL over what their assigned role is." Oppia `user_id`↔`auth_id` 매핑은 `UserIdByFirebaseAuthIdModel`, `UserAuthDetailsModel` — [firebase_auth_services.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/platform/auth/firebase_auth_services.py)
- `core/feconf.py`: `FIREBASE_AUTH_PROVIDER_ID = 'Firebase'`, `FIREBASE_ROLE_SUPER_ADMIN = 'super_admin'`, `FIREBASE_AUTH_ID_REGEX = '^[A-Za-z0-9]{1,128}$'`, `FIREBASE_EMULATOR_PORT = 9099`, `FIREBASE_SESSION_COOKIE_MAX_AGE = datetime.timedelta(days=14)` — [core/feconf.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/feconf.py)
- `app_dev.yaml`에 `FIREBASE_AUTH_EMULATOR_HOST: localhost:9099`가 있으며 "Firebase and Datastore emulator variables must not reach production" — [app_dev.yaml](https://raw.githubusercontent.com/oppia/oppia/develop/app_dev.yaml)

### Inferences
- Moodle의 "인증은 플러그인, 역할은 core"라는 분리(auth 플러그인은 신원만 확인, 권한은 역할/컨텍스트가 결정)는 소규모 플랫폼에도 그대로 적용 가능: 인증 어댑터(local password / OIDC)와 권한 모델을 분리하면 SAML/LDAP 같은 기업 요구는 어댑터 추가로 대응된다.
- Oppia처럼 인증을 외부 IdP(Firebase/OIDC)에 완전히 위임하면 비밀번호 저장 책임이 사라지지만, 오프라인/온프레미스 배포가 어려워진다(에뮬레이터 필요). 엔터프라이즈용이면 OIDC 표준 흐름을 직접 구현하되 IdP는 교체 가능하게 두는 편이 안전하다.
- Moodle 5.3의 OAuth 2 server/REST API 도입은 "토큰 발급 + scope"라는 현대적 API 인증으로의 전환이므로, 신규 플랫폼은 처음부터 OAuth2/OIDC + scope 기반으로 설계하는 것이 합리적이다.

### Gaps
- Moodle core에 OIDC 전용(auth_oidc) 플러그인이 포함되는지(Microsoft의 auth_oidc는 서드파티)는 이번 조사에서 미확인.
- Oppia 프로덕션 oppia.org에서 실제 활성화된 Firebase sign-in provider 목록(Google만인지 등)은 코드에 명시되지 않아 미확인.
- Oppia Android용 "mobile learner" 프로필의 인증 방식은 미조사.

---

## KQ3. 권한(Authorization) 모델 — Moodle 역할·능력·컨텍스트 / Oppia 역할·액션

### Takeaway
Moodle은 "역할(role) = 능력(capability)별 권한 값의 집합"을 6단계 컨텍스트 트리(SYSTEM 10 → USER 30 → COURSECAT 40 → COURSE 50 → MODULE 70 → BLOCK 80)에 할당하고, 하위 컨텍스트에서 Inherit/Allow/Prevent/Prohibit로 override하는 계층형 RBAC이다. Oppia는 컨텍스트 없는 평면 역할(ADMIN=curriculum admin, MODERATOR, TOPIC_MANAGER, EXPLORATION_EDITOR=full user, GUEST, LEARNER=mobile learner 등 16종) → 액션 상수 매핑(`_ROLE_ACTIONS`)과, 리소스별 rights(exploration/topic 소유자·편집자 ID 리스트)를 데코레이터에서 조합한다.

### Cited Findings
**Moodle — 개념과 컨텍스트**
- "A role is a collection of permissions defined for the whole system"; "The combination of roles and context define a specific user's ability to do something on any page." 하위 페이지: Managing roles, Assign roles, Standard roles, Permissions, Override permissions, Role export and import — [Roles and permissions](https://docs.moodle.org/en/Roles_and_permissions)
- "A context is a space in Moodle where roles can be assigned." `lib/accesslib.php` 상수: SYSTEM=10, USER=30, COURSECAT=40, COURSE=50, MODULE=70, BLOCK=80. 계층: System → (Front page, Course category) → Course → Activity module / Block. 역할은 트리 아래로 상속("a course's role assignments apply to its quizzes"); 예외(override)는 설정한 컨텍스트와 그 아래에만 적용 — [Context](https://docs.moodle.org/en/Context)
- 개발자 문서의 6개 컨텍스트 클래스: `context_system`("root context… only one"), `context_user`, `context_coursecat`, `context_course`, `context_module`, `context_block`. "Roles can be overridden by contexts further down the tree." — [Access API](https://moodledev.io/docs/apis/subsystems/access)

**Moodle — 능력(capability) 정의와 네이밍**
- 능력은 플러그인의 `db/access.php`의 `$capabilities` 배열에 정의. 이름 규칙 `plugintype/pluginname:capabilityname` (예 `mod/folder:managefiles`). 필드: `riskbitmask`(예 RISK_SPAM), `captype`("read or write"; write는 guest/비로그인 차단), `contextlevel`(상수; 그 아래 컨텍스트에서도 검사 가능), `archetypes`(표준 역할 기본값, 예 `'editingteacher' => CAP_ALLOW`, CAP_ALLOW만 권장), `clonepermissionsfrom`. 변경 시 플러그인 version bump 필요. 체크 API: `has_capability()`(admin은 기본 true), `require_capability()`(예외 throw). 지침: "Does the user have capability to do something?"로 묻고 "역할이 있는가"로 묻지 말 것. 비로그인은 `$CFG->notloggedinroleid`, guest는 `$CFG->guestroleid` — [Access API](https://moodledev.io/docs/apis/subsystems/access)
- 웹서비스 관련 능력 예: `moodle/webservice:createtoken`, `webservice/rest:use`, `webservice/soap:use` — [Using web services](https://docs.moodle.org/en/Using_web_services); REST API용 `moodle/api:createtoken`(Authenticated user 기본 보유), `moodle/site:manageoauth2clients`(Manager 기본 보유) — [REST API tokens](https://docs.moodle.org/en/REST_API_tokens); override용 `moodle/role:override`, `moodle/role:safeoverride` — [Override permissions](https://docs.moodle.org/en/Override_permissions)

**Moodle — 표준 역할과 override 규칙**
- 표준 역할: Site administrator("can 'do everything'"), Manager("a lesser administrator role"), Course creator, Teacher("can manage and add content to courses"), Non-editing teacher("can grade… but not edit"), Student, Guest("can view courses but not participate"), Authenticated user("the role all logged in users have"), Authenticated user on the front page — [Standard roles](https://docs.moodle.org/en/Standard_roles)
- 권한 값 4종: **Inherit**(기본; 상위 컨텍스트/다른 역할의 값 유지), **Allow**(해당 컨텍스트와 하위에 허용), **Prevent**("removing permission for this capability (only for this role)"; 다른 역할이 Allow면 무효), **Prohibit**("can NOT be overridden at any lower context or by another role"). 충돌 규칙: 하위 컨텍스트가 상위를 덮어씀(단 Prohibit 예외); 같은 컨텍스트에서 한 역할 Allow + 다른 역할 Prevent면 Allow 승. Override는 "modifies an existing specific role and affects all users assigned to that role in the context"(새 역할 생성 아님). 기본값: Manager는 모든 역할 override 가능, Teacher는 non-editing teacher/student/guest만 — [Override permissions](https://docs.moodle.org/en/Override_permissions)

**Oppia — 역할과 액션**
- 역할 ID 상수와 문자열 값: `ROLE_ID_CURRICULUM_ADMIN = 'ADMIN'`, `ROLE_ID_BLOG_ADMIN = 'BLOG_ADMIN'`, `ROLE_ID_BLOG_POST_EDITOR = 'BLOG_POST_EDITOR'`, `ROLE_ID_COLLECTION_EDITOR = 'COLLECTION_EDITOR'`, `ROLE_ID_FULL_USER = 'EXPLORATION_EDITOR'`, `ROLE_ID_GUEST = 'GUEST'`, `ROLE_ID_MOBILE_LEARNER = 'LEARNER'`, `ROLE_ID_MODERATOR = 'MODERATOR'`, `ROLE_ID_QUESTION_ADMIN`, `ROLE_ID_RELEASE_COORDINATOR`, `ROLE_ID_TOPIC_MANAGER = 'TOPIC_MANAGER'`, `ROLE_ID_TRANSLATION_ADMIN`, `ROLE_ID_VOICEOVER_ADMIN`, `ROLE_ID_QUESTION_COORDINATOR`, `ROLE_ID_TRANSLATION_COORDINATOR`, `ROLE_ID_TECH_TEAM_LEAD` — [core/feconf.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/feconf.py)
- `_ROLE_ACTIONS` 매핑(발췌): **curriculum admin** = ACCESS_TOPICS_AND_SKILLS_DASHBOARD, ACCESS_CLASSROOM_ADMIN_PAGE, CHANGE_STORY_STATUS, CHANGE_TOPIC_STATUS, CREATE_NEW_SKILL, CREATE_NEW_TOPIC, DELETE_TOPIC, EDIT_ANY_STORY/TOPIC/SUBTOPIC_PAGE/QUESTION/ACTIVITY, MANAGE_TOPIC_RIGHTS, PUBLISH_ANY_ACTIVITY 등; **topic manager** = ACCESS_TOPICS_AND_SKILLS_DASHBOARD, EDIT_OWNED_STORY, EDIT_OWNED_TOPIC, EDIT_SKILL, EDIT_ANY_SUBTOPIC_PAGE, EDIT_QUESTION_IN_MANAGED_TOPIC, MANAGE_QUESTION_SKILL_STATUS 등; **moderator** = ACCESS_MODERATOR_PAGE, DELETE/EDIT_ANY_(PUBLIC_)ACTIVITY, PLAY_ANY_PRIVATE_ACTIVITY, SEND_MODERATOR_EMAILS, UNPUBLISH_ANY_PUBLIC_ACTIVITY; **full user** = ACCESS_CREATOR_DASHBOARD, ACCESS_LEARNER_DASHBOARD, ACCESS_LEARNER_GROUPS, CREATE_EXPLORATION, EDIT_OWNED_ACTIVITY, PUBLISH_OWNED_ACTIVITY, SUGGEST_CHANGES 등; **guest/mobile learner** = PLAY_ANY_PUBLIC_ACTIVITY만. `UPDATABLE_ROLES`에서 LEARNER는 의도적으로 제외(계정이 아닌 프로필). "No role hierarchy or inheritance logic appears in this module." `get_all_actions(roles)`는 역할들의 액션 합집합 — [core/domain/role_services.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/role_services.py)
- 컨트롤러 데코레이터("Decorators to provide authorization across the site"): 대부분 `role_services.ACTION_* in self.user.actions` 검사(예 `can_access_moderator_page`, `can_create_exploration`); 리소스별로는 `rights_manager.check_can_edit_activity/publish/delete/voiceover/save`로 소유권 확인; 일부는 `self.current_user_is_super_admin`(`can_access_admin_page`) 또는 `X-AppEngine-Cron` 헤더 검사(`can_perform_cron_tasks`) — [core/controllers/acl_decorators.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/controllers/acl_decorators.py)
- 리소스 rights: `TopicRights(manager_ids, topic_is_published)` — [topic_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/topic_domain.py); `ExplorationSummary`는 `community_owned, owner_ids, editor_ids, voice_artist_ids, viewer_ids` 보유, `is_private()`은 `constants.ACTIVITY_STATUS_PRIVATE` 비교 — [exp_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/exp_domain.py)

### Inferences
- Moodle 모델의 핵심 가치는 (1) 능력 이름이 `component:action`으로 네임스페이스화되어 플러그인이 자기 능력을 선언하고, (2) 결정이 "역할 보유 여부"가 아니라 "이 컨텍스트에서 이 능력이 있는가"로 이뤄지며, (3) Prohibit로 하향 거부를 강제할 수 있다는 점이다. 단일 코스 플랫폼이라면 컨텍스트는 `system → course → module → lesson` 4단계로 축소해도 동일 구조를 유지할 수 있다.
- Oppia의 "역할→액션 집합 + 리소스 소유자 리스트" 모델은 구현이 단순하고 테스트하기 쉽지만, 역할 상속이 없어 역할이 16개로 불어나고 액션 중복이 많다. 소규모 플랫폼에는 Oppia식 액션 열거(enum)를 Moodle식 컨텍스트 트리에 얹는 하이브리드가 적합하다.
- Oppia의 `manager_ids/owner_ids/editor_ids` 패턴은 Markdown 저장소에서 "lesson 폴더별 CODEOWNERS"와 유사한 효과를 낸다.

### Gaps
- Moodle `CAP_INHERIT/CAP_PREVENT/CAP_PROHIBIT` 상수의 숫자값과 risk bitmask 상수 목록은 Access API 페이지에 없어 미확인(accesslib.php 직접 확인 필요).
- Oppia의 `ACTIVITY_STATUS_*` 상수 값과 `ExplorationRights` 클래스 자체(파일 위치 `rights_domain.py`로 추정)는 fetch하지 않음.

---

## KQ4. API 인증 — Moodle 웹서비스 토큰·신규 REST API / Oppia 내부 API

### Takeaway
Moodle의 전통 웹서비스는 `login/token.php?username&password&service`로 발급받은 `wstoken`을 `webservice/rest/server.php?wstoken=…&wsfunction=…&moodlewsrestformat=json`에 붙여 호출하는 RPC형("not RESTful") 구조이며, 5.3에서 scope 기반 REST API 토큰(개인 액세스 토큰 + OAuth 2 client)과 SwaggerUI가 새로 추가되었다. GraphQL은 어느 문서에도 없다. Oppia는 공개 API가 아니라 Angular 프런트엔드가 쓰는 내부 JSON 핸들러(`*-backend-api.ts` → `core/controllers/`)에 Firebase 세션 쿠키 + ACL 데코레이터로 접근을 제어한다.

### Cited Findings
**Moodle — 전통 웹서비스**
- "Each user will have a specific and unique security key (also known as a 'token') to access the service." 관리자 토큰은 Site administration > Server > Web services > Manage tokens에서만 생성; 토큰에 IP 제한·"Valid until" 설정 가능. 프로토콜 관리(Manage protocols)에서 REST/SOAP/AMF 등 활성화, 각 프로토콜마다 `webservice/<proto>:use` 능력 필요. 설정 절차: Enable web services → 프로토콜 활성화 → 커스텀 서비스 생성("Authorised users only", "Required capability") → 함수 추가 → 능력 부여 → 인가 사용자 등록. API Documentation 페이지가 함수별 문서 제공. GraphQL 언급 없음 — [Using web services](https://docs.moodle.org/en/Using_web_services)
- 토큰 발급: `https://www.yourmoodle.com/login/token.php?username=USERNAME&password=PASSWORD&service=SERVICESHORTNAME` (모바일 앱 서비스 shortname `moodle_mobile_app`; 3.9+ 응답은 `token`, `privatetoken` JSON). 호출: `https://your.site.com/webservice/rest/server.php?wstoken=...&wsfunction=...&moodlewsrestformat=json` (배열 파라미터는 `&array_name[index][parameter_name]=value`; 포맷 `xml` 기본/`json`). REST는 "not RESTful"; SOAP(Zend), XML-RPC(Zend), AMF(3.0 이전). 샘플 클라이언트 `https://github.com/moodlehq/sample-ws-clients` — [Creating a web service client](https://docs.moodle.org/dev/Creating_a_web_service_client)
- 프레임워크 개요: "Moodle has a full-featured Web Service framework"; 동일 웹서비스가 웹 UI의 AJAX와 공식 Moodle Mobile App에 사용됨; 파일 업/다운로드 전용 엔드포인트 별도 — [External services](https://moodledev.io/docs/apis/subsystems/external)
- 함수 정의: `db/services.php`의 `$functions` 배열에 `classname`(예 `local_groupmanager\external\create_groups`), `description`, `type`('read'|'write'), `ajax`(브라우저 AJAX 허용 여부), `capabilities`("advisory only"), `services`(`MOODLE_OFFICIAL_MOBILE_SERVICE`에 넣으면 모바일 앱 노출). 클래스는 `\core_external\external_api` 상속, `execute_parameters()/execute()/execute_returns()` 구현, `validate_parameters()` 후 능력 검사 — [Adding a web service to your plugin](https://moodledev.io/docs/apis/subsystems/external/writing-a-service)

**Moodle 5.3 — 신규 REST API**
- "New feature in Moodle 5.3! … REST API tokens let external apps and scripts connect to Moodle's new REST API." 토큰 2종: Personal access tokens(사용자 preferences에서 생성, `moodle/api:createtoken` 필요)과 OAuth 2 clients(관리자가 앱 등록, 사용자 동의 흐름; `moodle/site:manageoauth2clients`, Composer 의존성 설치 필요). "Every token has one or more scopes, which limit what it can do." 플러그인이 scope 추가 가능. SwaggerUI: Site administration > Development > "Moodle REST API UI (SwaggerUI)". REST API 토큰은 전통 웹서비스 토큰과 별개이며 "Enable web services" 설정의 영향을 받지 않음. "only a few parts of Moodle are available through the REST API" — [REST API tokens](https://docs.moodle.org/en/REST_API_tokens)
- OAuth 2 클라이언트 유형: confidential(서버측, secret 보유) vs public(모바일, secret 없음); 클라이언트당 활성 secret 최대 2개, secret 만료 1년 (검색 스니펫 기준, 5.3 docs "OAuth 2 clients" 페이지) — [OAuth 2 clients](https://docs.moodle.org/en/OAuth_2_clients)

**Oppia**
- 아키텍처: `main.py`가 요청을 컨트롤러로 라우팅; `core/controllers/`는 "Thin HTTP handlers that call services and return JSON"; 프런트엔드 `*-backend-api.ts` 파일이 HTTP 호출 담당 — [Overview of the Oppia codebase](https://github.com/oppia/oppia/wiki/Overview-of-the-Oppia-codebase)
- 핸들러 URL 상수 예: `LEARNER_DASHBOARD_LEARNER_GROUPS_HANDLER = '/learner_dashboard_learner_groups_handler'`, `CLASSROOM_DATA_HANDLER = '/classroom_data_handler'`, `CLASSROOM_HANDLER_URL = '/classroom'` — [core/feconf.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/feconf.py)
- 접근 제어는 KQ3의 `acl_decorators.py` 데코레이터로 핸들러 단위 적용; 큐/크론 핸들러는 `X-AppEngine-QueueName`/`X-AppEngine-Cron` 헤더 또는 super admin만 허용 — [acl_decorators.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/controllers/acl_decorators.py)
- 세션은 Firebase ID 토큰을 Bearer로 받아 세션 쿠키로 교환(KQ2 참조) — [firebase_auth_services.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/platform/auth/firebase_auth_services.py)

### Inferences
- Moodle의 20년 된 `wsfunction` RPC는 "함수별 self-describing 스키마 + 토큰 + 서비스 번들"이라는 장점이 있지만 리소스 지향이 아니어서 5.3에서 scope 기반 REST를 새로 만들었다. 신규 플랫폼은 처음부터 OpenAPI 스펙 + scope 토큰으로 가고, 내부 UI와 외부 API가 같은 엔드포인트를 쓰도록(Moodle이 AJAX/모바일에 웹서비스를 재사용하듯) 설계하는 것이 좋다.
- Oppia는 공개 API 계약이 없어(내부 핸들러 + CSRF/세션) 서드파티 연동이 사실상 불가능하다 — "API 우선"을 목표로 한다면 반면교사.

### Gaps
- Moodle 5.3 REST API의 실제 엔드포인트 경로/버전 프리픽스와 노출된 리소스 목록은 docs에 없음(개발자 문서 "Routing"/"scopes" 페이지 미조사).
- Oppia의 CSRF 토큰 처리(`core/controllers/base.py`)와 Android 앱용 API(`ANDROID_BUILD_SECRET`)는 미조사.

---

## KQ5. 콘텐츠 모델과 포맷 — Moodle (코스/섹션/활동, .mbz, Book/Page/Lesson, Markdown)

### Takeaway
Moodle 코스는 "course → section(및 subsection) → activity/resource(mod 플러그인 인스턴스)"의 3계층이며, 콘텐츠 저작 단위는 HTML 에디터(TinyMCE) 중심이고 Markdown은 "Plain text area" 에디터를 선택한 사용자에게만 열리는 텍스트 포맷 옵션이다. 백업 `.mbz`는 기본 tgz(옵션 zip)이며 루트 `moodle_backup.xml`을 지도 삼아 `course/`, `sections/`, `activities/<cmid>/`, `files.xml` 등으로 분해된 XML 묶음이다.

### Cited Findings
- 코스 포맷: Custom sections("The course is divided into customisable sections that a teacher can give titles to"), Weekly sections, Single activity("only has one section, and allows the teacher to add one activity only"). "Show one section per page" 옵션과 Course index로 섹션 간 이동 — [Course formats](https://docs.moodle.org/en/Course_formats)
- 5.3: 모든 코스에 선형 내비게이션(Previous/Next 푸터) 적용, 서브섹션 활동 순서 로직 개선(MDL-86393), 학습성과(Learning outcomes)를 코스에 추가하고 backup/restore/import/export 지원 — [Moodle 5.3 release notes](https://moodledev.io/general/releases/5.3)
- 플러그인 타입 표: 활동 모듈 `mod`(/mod), 코스 포맷 `format`(/course/format), 콘텐츠뱅크 `contenttype`, H5P 라이브러리 `h5plib`, 질문 유형 `qtype`, 질문 가져오기/내보내기 `qformat`, 텍스트 필터 `filter`, 에디터 `editor`, 가용성 조건 `availability` 등 56종(페이지에 총계 미기재, 행 수 집계) — [Plugin types](https://moodledev.io/docs/apis/plugintypes)
- **Book**: "create multi-page resources with a book-like format and table of contents"; 챕터에 이미지/비디오/오디오/H5P 임베드 가능(H5P는 성적부 연동 없음); 학생이 책 전체나 챕터를 PDF로 인쇄 가능. 서브챕터·HTML import는 이 페이지에 없음 — [Book resource](https://docs.moodle.org/en/Book_resource)
- **Lesson**: "'branching' exercises" — Content page와 Question page를 Jumps로 연결, 학생 응답에 따라 다음 페이지가 결정; 연습용/채점용 선택 가능 — [Lesson activity](https://docs.moodle.org/en/Lesson_activity)
- **Markdown**: "To use Markdown, you need to choose 'Plain text area' as text editor"(사용자 Preferences > Editor preferences), 이후 텍스트 영역 아래 드롭다운에서 "Markdown format" 선택. 목록 앞 빈 줄 필수 등 문법 주의사항 — [Markdown](https://docs.moodle.org/en/Markdown)
- **백업(.mbz)**: 기본 파일명 `backup-moodle2-course-coursename-date-hour.mbz`(사용자 제외 `-nu`, 익명화 `-an`); 활동/블록/필터, 권한에 따라 사용자·역할 할당·그룹·완료 정보·로그·성적 이력 포함 가능; 4.4부터 신규 설치에 비동기 백업 기본 활성 — [Course backup](https://docs.moodle.org/en/Course_backup)
- `.mbz`는 "Moodle backup zip"의 약자이지만 "The default format is TGZ (gzip)"(헥스 `#1F8B`), `$CFG->usezipbackups = true;`로 zip(`#504B0304`) 전환; `tar -xzf …mbz`로 해제, `files.xml`의 contenthash로 `files/<앞 2자>/` 폴더에서 원본 파일 찾기 — [Backup and restore FAQ](https://docs.moodle.org/en/Backup_and_restore_FAQ)
- Backup 2.0 구조(역사 문서로 표시됨): 루트 `moodle_backup.xml`("the 'map' that shows/describes the whole backup"), `files.xml` + `files/`, users/roles/scales/groups/outcomes "stores"; `course/`(course.xml, inforef.xml 등), `sections/<sectionid>/section.xml`, `activities/<cmid>/`(activityname.xml, module.xml, completion, grade items, logs, inforef.xml), `blocks/<instanceid>/block.xml`. 플랜 → 태스크 → 스텝(execution step / structure step) — [Backup 2.0 general architecture](https://docs.moodle.org/dev/Backup_2.0_general_architecture)
- 플러그인 백업 구현: `mod/foobar/backup/moodle2/backup_foobar_activity_task.class.php`(`backup_activity_task` 상속, `define_my_steps()`, `encode_content_links()`), `backup_foobar_stepslib.php`의 structure step이 `backup_nested_element` + `set_source_table()`로 XML 정의 — [Backup API](https://moodledev.io/docs/apis/subsystems/backup)
- IMS CC: "Moodle currently only supports the import of IMS CC version 1.0 and 1.1 packages." 내보내기는 IMS CC 1.1만, 내보내기 가능 요소는 Forums, Labels, IMS LTI activity, Page, URL, Quiz(부분) — "the ONLY activities that can be exported to IMS CC"; 비동기 백업 활성 시 CC 내보내기 불가; v1.2/1.3은 MDL-60803 — [IMS Common Cartridge import and export](https://docs.moodle.org/en/IMS_Common_Cartridge_import_and_export)

### Inferences
- Moodle의 콘텐츠 단위는 "활동 모듈 인스턴스(DB 레코드 + 파일 영역)"이고, Markdown은 저장 포맷이 아니라 렌더링 시 선택되는 텍스트 포맷(FORMAT_MARKDOWN)이다. Git 친화적 Markdown-first 플랫폼은 Moodle의 Page/Book 대신 "폴더 = 섹션, 파일 = 레슨" 매핑을 택하되, `.mbz`의 교훈(루트 manifest + 콘텐츠별 파일 + 파일 해시 스토어)을 export 포맷 설계에 차용할 수 있다.
- Lesson 모듈의 Jump 기반 분기와 Oppia의 state machine(KQ6)은 같은 아이디어다; frontmatter에 `next:`/`branches:`를 두면 Markdown에서도 구현 가능하다.
- IMS CC 내보내기 지원 범위가 좁다는 점(5개 활동 + 퀴즈 부분)은 "표준 패키지로 모든 것을 옮길 수 있다"는 기대가 비현실적임을 보여준다. 소규모 플랫폼은 CC 1.1 내보내기(Page/URL/LTI 링크 수준) 정도를 목표로 잡는 편이 현실적이다.

### Gaps
- Page 리소스(mod_page) 문서는 별도 fetch하지 않음.
- Subsections 도입 버전(4.5로 알려짐)은 docs 페이지 404로 1차 출처 확인 실패 — 5.3 노트에 "Subsection activity order logic"이 있어 존재는 확인.
- Book의 HTML/zip 챕터 import(booktool_importhtml) 기능은 문서에 없어 미확인.

---

## KQ6. 콘텐츠 모델과 포맷 — Oppia (topic/story/chapter/exploration/skill/subtopic/classroom, YAML)

### Takeaway
Oppia의 커리큘럼은 Classroom(예 'math') → Topic → Story(canonical/additional) → Chapter(StoryNode, 각각 published exploration 1개 + prerequisite/acquired skill IDs) → Exploration(카드=State의 상태기계)이며, Skill은 Topic 아래 Subtopic으로 묶여 practice/diagnostic에 쓰인다. Exploration은 YAML(스키마 v62, states_schema 57)로 직렬화되며 각 State는 content(HTML) + interaction(id, customization_args, answer_groups[rule_specs→outcome(dest, feedback)], default_outcome, hints, solution)으로 이루어진다.

### Cited Findings
**계층 용어**
- "A topic refers to a subject a learner is learning (e.g., Decimals, Fractions)." / "A story is a set of lessons that teaches a topic with real-life examples." / "A subtopic is a group of Skills within a Topic." / "Each Skill belongs to a Topic and supports learning of that Topic." / "Explorations (or lessons) are learning units in Oppia." / "A lesson is made up of a series of cards, where each card consists of the tutor's question…" / "An interaction is the answer learners provide in response to a question (content) and the feedback (response) from Oppia." — [Key Terms (Oppia lesson-creator docs)](https://oppia-lesson-creator-documentation.readthedocs.io/en/latest/start/terms.html)
- "A topic, like Fractions, consists of one or more stories." / "A story is a group of explorations, and is the new name we'll be giving to what are currently called 'collections'." / Exploration: "It is the core unit of learning in Oppia." / Skill: "a concrete learning outcome that describes something that a learner should be able to do." 선행 스킬은 "generate random review questions at the start of each lesson"에 사용; practice question은 "a standalone question that may be used by students as part of a practice session" — [Lesson Creation Guide (wiki)](https://github.com/oppia/oppia/wiki/Lesson-Creation-Guide)
- 저작 흐름: Topics and Skills Dashboard → "Create New Topic"(name, URL, web title fragment, description) → Topic Editor의 Canonical Stories에서 "Add Story" → "Add Chapter"(chapter title, Exploration ID, thumbnail) → 각 chapter에 Chapter Outline, published Exploration ID("You cannot publish the Story without this step"), "Add prerequisite skill", "Add acquired skill" → "Publish story" — [Create a New Topic, Story, or Chapter](https://oppia-lesson-creator-documentation.readthedocs.io/en/latest/admins/create-topic-story-chapter.html)

**도메인 객체(코드)**
- `Topic`: id, name, abbreviated_name, url_fragment, description, `canonical_story_references`, `additional_story_references`, `uncategorized_skill_ids`("not part of any subtopic"), `subtopics`, subtopic_schema_version, next_subtopic_id, language_code, version, story_reference_schema_version, meta_tag_content, `practice_tab_is_displayed`, page_title_fragment_for_web, `skill_ids_for_diagnostic_test`. `Subtopic`: id(int), title, `skill_ids`, thumbnail_*, url_fragment — [topic_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/topic_domain.py)
- `StoryNode`("Domain object describing a node in the exploration graph of a story"): id, title, description, thumbnail_*, `destination_node_ids`, `acquired_skill_ids`, `prerequisite_skill_ids`, `outline`, outline_is_finalized, `exploration_id`, status, planned_publication_date, last_modified, first_publication_date, unpublishing_reason. `StoryContents`: nodes, initial_node_id, next_node_id, arcs. `Story`: id, title, url_fragment, meta_tag_content, `corresponding_topic_id`, description, notes, story_contents, `story_contents_schema_version`, language_code, version. `get_ordered_nodes`: "NOTE: Currently, this function assumes only a linear arrangement of nodes." — [story_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/story_domain.py)
- `Skill`: description("Describes the observable behaviour of the skill"), misconceptions(id, name, notes, feedback, must_be_addressed), rubrics(difficulty별 explanations; 정확히 3개, `constants.SKILL_DIFFICULTIES` 순서), skill_contents.explanation(SubtitledHtml), `superseding_skill_id`, `prerequisite_skill_ids`; v5 스키마에서 worked_examples 제거. `UserSkillMastery.degree_of_mastery`(float) — [skill_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/skill_domain.py)
- `Classroom`: classroom_id, name, url_fragment, feedback_recipient_email, course_details, teaser_text, topic_list_intro, `topic_id_to_prerequisite_topic_ids`, is_published, diagnostic_test_is_enabled, thumbnail_data, banner_data, index; 최소 1개 topic 필요 — [classroom_config_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/classroom_config_domain.py); `CLASSROOM_PAGES = ['math']`, `DEFAULT_CLASSROOM_PUBLICATION_STATUS = False` — [core/feconf.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/feconf.py)
- 스키마 버전 상수: `CURRENT_STATE_SCHEMA_VERSION = 57`, `CURRENT_STORY_CONTENTS_SCHEMA_VERSION = 7`, `CURRENT_SKILL_CONTENTS_SCHEMA_VERSION = 5`, `CURRENT_SUBTOPIC_PAGE_CONTENTS_SCHEMA_VERSION = 4` — [core/feconf.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/feconf.py); `CURRENT_EXP_SCHEMA_VERSION = 62`("The current version of the exploration YAML schema"), `EARLIEST_SUPPORTED_EXP_SCHEMA_VERSION = 46`; `to_yaml`("Convert the exploration domain object into YAML string"), `from_yaml`("Creates and returns exploration from a YAML text string for YAML schema versions 10 and later") — [exp_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/exp_domain.py)
- `Exploration` 필드: id, title, category, objective, language_code, tags, blurb, author_notes, states_schema_version, init_state_name, states, param_specs, param_changes, version, created_on, last_updated, auto_tts_enabled, next_content_id_index, edits_allowed — [exp_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/exp_domain.py)
- `State`("Domain object for a state"): content, param_changes, interaction, solicit_answer_details, `card_is_checkpoint`("If the card is marked as a checkpoint by the creator or not"), `linked_skill_id`, classifier_model_id, inapplicable_skill_misconception_ids. `Outcome`: `dest`("The name of the destination state"), `dest_if_really_stuck`, feedback, `labelled_as_correct`, param_changes, `refresher_exploration_id`("redirect the learner to if they seem to lack understanding of a prerequisite concept"), `missing_prerequisite_skill_id`. `InteractionInstance`: id, customization_args, answer_groups, default_outcome, confirmed_unclassified_answers, hints, solution — [state_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/state_domain.py)

**YAML 샘플**
- `data/explorations/`에 `hola.yaml`, `welcome/`, `solar_system/`, `multiples.yaml` 등 샘플 수록 — [data/explorations](https://github.com/oppia/oppia/tree/develop/data/explorations)
- `hola.yaml` 최상위 키 16개: author_notes, auto_tts_enabled, blurb, category, correctness_feedback_enabled, edits_allowed, init_state_name, language_code, objective, param_changes, param_specs, schema_version(47), states, states_schema_version(42), tags, title. 각 state: classifier_model_id, content{content_id, html}, interaction{id, answer_groups[{outcome{dest, feedback{content_id, html}, labelled_as_correct, missing_prerequisite_skill_id, param_changes, refresher_exploration_id}, rule_specs[{inputs, rule_type}], tagged_skill_misconception_id, training_data}], confirmed_unclassified_answers, customization_args, default_outcome, hints, solution}, next_content_id_index, param_changes, recorded_voiceovers{voiceovers_mapping}, solicit_answer_details, written_translations{translations_mapping}. 사용 interaction id: `TextInput`, `MultipleChoiceInput`, `EndExploration`; rule_type: `Equals`, `Contains`, `StartsWith`, `FuzzyEquals` — [hola.yaml](https://raw.githubusercontent.com/oppia/oppia/develop/data/explorations/hola.yaml)

### Inferences
- Oppia의 콘텐츠 모델은 "스킬 그래프(skill tree) + 스토리 그래프(현재는 선형) + 카드 상태기계" 3층이며, 각 층이 schema_version으로 버저닝되고 마이그레이션 함수(`_convert_states_v41_dict_to_v42_dict` 등)를 유지한다. Markdown-first 플랫폼은 frontmatter에 `schema_version`을 두고 마이그레이션 스크립트를 갖추는 관행을 차용할 가치가 있다.
- Oppia는 콘텐츠 본문이 HTML 문자열(`content.html`)이며 Markdown이 아니다; 대신 content_id 단위 번역/음성(written_translations, recorded_voiceovers)을 붙인다. Markdown 레슨에서 i18n을 하려면 블록 ID 부여가 필요하다는 시사점.
- "chapter = 스토리 노드 1개 = 발행된 exploration 1개 + 선행/획득 스킬"은 module → lesson 모델에 거의 그대로 대응되며, 레슨 frontmatter에 `prerequisite_skills`/`acquired_skills`를 두면 Oppia식 복습 질문 생성·진단 테스트 기반이 된다.

### Gaps
- 샘플 `hola.yaml`은 schema_version 47(구버전)이어서 최신 62 스키마의 추가 키(`card_is_checkpoint`, `linked_skill_id`, `dest_if_really_stuck` 등)는 YAML에서 직접 보지 못함(도메인 코드로만 확인).
- Subtopic page(개념 설명 페이지)의 콘텐츠 구조와 Question(문제 은행) 도메인은 미조사.
- Exploration 내보내기(YAML 다운로드)의 UI 경로와 `can_download_exploration` 권한 조건은 미확인.

---

## KQ7. 상호운용 표준 (LTI / SCORM / H5P / xAPI / IMS CC / Open Badges)

### Takeaway
Moodle은 LTI Advantage(1.3 + AGS/NRPS/Deep Linking) 소비자·제공자, SCORM 1.2(+AICC), H5P(core), IMS CC 1.0/1.1 가져오기·1.1 내보내기, Open Badges 2.0/2.1, 그리고 core xAPI 라이브러리(LRS는 아님)를 갖춘다. Oppia는 이들 표준을 지원한다는 근거를 전혀 찾지 못했다(자체 YAML/Android 앱 중심).

### Cited Findings
- Standards 요약: "Learning Tool Interoperability (LTI) Advantage Complete" 인증; "can also act as an LTI 1.1 and 2.0 tool provider" (Publish as LTI tool, 3.1+); "Moodle complies with the SCORM 1.2 specification"; AICC 패키지 업로드; "Open Badges v 2.0 compliant as Issuer by IMS"(3.11에서 v2.1 구현); WCAG 2.1 AA; IMS Common Cartridge import/export; IMS Content Packaging; IMS Enterprise는 "via a downloadable plugin"; xAPI/Tin Can은 "community plugins available that provide limited support"; SCORM 2004·xAPI 완전 지원은 상용 mod_scormcloud — [Standards](https://docs.moodle.org/en/Standards)
- External tool(소비자): LTI Advantage와 LTI 1.1(cartridge) 등록 흐름; "LTI 2.0 … are no more the preferred way"; Content Selection URL(딥링킹), "Accept grades from the tool"(성적 반환), "Memberships"(역할별 사용자 목록 요청) — [External tool](https://docs.moodle.org/en/External_tool)
- Publish as LTI tool(제공자): "allows remote users on a different platform to access selected courses and activities"; LTI Advantage(1.3) = core 1.3 + Assignment and Grade Services, Names and Role Provisioning, Deep Linking; "LTI 1.1 and 2.0 have been deprecated"; 코스 또는 단일 활동 공유; 성적은 30분 주기 scheduled task로 동기화 — [Publish as LTI tool](https://docs.moodle.org/en/Publish_as_LTI_tool)
- SCORM activity: "provides a way for teachers to easily upload and manage SCORM or AICC packages within their courses"; Reports 탭으로 시도 정보 열람 — [SCORM activity](https://docs.moodle.org/en/SCORM_activity)
- H5P: H5P 콘텐츠 타입/라이브러리를 사이트에 먼저 설치(h5p.org에서 scheduled task로 다운로드 또는 수동 업로드), 관리자가 특정 타입 비활성화 가능; "An H5P activity is one activity, for the students can interact with it"(리소스로 올린 H5P 파일과 구분); Custom CSS는 4.3.3+ — [H5P](https://docs.moodle.org/en/H5P); 플러그인 타입 `h5plib`(/h5p/h5plib), `contenttype`(/contentbank/contenttype) — [Plugin types](https://moodledev.io/docs/apis/plugintypes)
- xAPI core 라이브러리: `core_xapi_statement_post`가 "to process xAPI statements and generate standard Moodle events"; 플러그인별 handler 클래스; actor/verb/object 검증; 4.2부터 State API(`core_xapi_post_state/get_state/delete_state`); "final objective... is NOT to implement a full LRS inside Moodle" — [xAPI API](https://moodledev.io/docs/apis/subsystems/xapi)
- IMS CC: 가져오기 1.0/1.1, 내보내기 1.1만 (상세 KQ5) — [IMS Common Cartridge import and export](https://docs.moodle.org/en/IMS_Common_Cartridge_import_and_export)
- Oppia: README/위키/도메인 코드 어디에도 LTI, SCORM, xAPI, IMS CC, H5P 언급 없음 — [github.com/oppia/oppia](https://github.com/oppia/oppia), [Overview of the Oppia codebase](https://github.com/oppia/oppia/wiki/Overview-of-the-Oppia-codebase)

### Inferences
- 소규모 플랫폼이 "기업용"을 표방하려면 LTI 1.3 Tool(제공자) 역할이 가장 가성비 높은 표준이다: 기업 LMS(Moodle 포함)가 코스를 임베드하고 성적을 AGS로 받아갈 수 있다. SCORM 패키지 생성은 Markdown 정적 빌드 결과를 SCORM 1.2 manifest로 감싸는 수준이면 충분하다.
- Moodle조차 LRS를 내장하지 않으므로, 진행 이벤트를 xAPI statement 형태로 외부 LRS에 보내는 "emitter"만 갖추는 것이 적정 범위다.

### Gaps
- Moodle의 SCORM 2004 지원 수준(부분 지원으로 알려짐)은 SCORM activity 페이지에 명시되지 않아 미확인.
- Moodle H5P core 통합 도입 버전(3.8/3.9로 알려짐)과 mod_h5pactivity의 xAPI 기반 시도 기록 세부는 docs에서 확인 실패(tracker MDL-67788 검색 스니펫만 존재).
- IMS QTI 지원 여부는 Standards 페이지에 없음.

---

## KQ8. 아키텍처 · 기술 스택 · 최소 서버 요구사항

### Takeaway
Moodle 5.3은 PHP 8.3+(64-bit, sodium 확장, max_input_vars≥5000)와 PostgreSQL 17 / MySQL 8.4 / MariaDB 11.4 / MSSQL 2019 중 하나가 필요하고(Oracle은 5.0부터 미지원), 하드웨어 권고는 디스크 200MB+콘텐츠(현실적 5GB), 1GHz/512MB 최소·2GHz 듀얼코어/1GB 권장, 56종 플러그인 타입을 가진 모놀리식 PHP 앱이다. Oppia는 Python 3.12(App Engine `python312`, gunicorn, F2 인스턴스) + Cloud NDB/Datastore + Redis(VPC connector) + Firebase + Angular 11(AngularJS 잔존) 구조로, 로컬 개발도 Datastore/Firebase 에뮬레이터와 Java 11, Chrome, pyenv Python 3.12.13을 요구하는 GCP 종속 아키텍처다.

### Cited Findings
**Moodle**
- 5.3 요구사항: 업그레이드는 4.4+에서; PHP 최소 8.3.0, 8.4.x 지원; sodium 확장 필수; `max_input_vars` ≥ 5000; 64-bit PHP만; DB 최소 PostgreSQL 17, MySQL 8.4, MariaDB 11.4.0, MS SQL Server 2019, Aurora MySQL 8.0; "Oracle … is no longer supported from Moodle LMS 5.0" — [Moodle 5.3 release notes](https://moodledev.io/general/releases/5.3)
- 하드웨어: 디스크 "200MB for the Moodle code, plus as much as you need to store content. 5GB is probably a realistic minimum."; 프로세서 "1 GHz (min), 2 GHz dual core or more recommended."; 메모리 "512MB (min), 1GB or more is recommended."; 주로 Linux + Apache + PostgreSQL/MySQL/MariaDB + PHP로 개발, Nginx/OpenLiteSpeed 가능; `moodledata`는 "should NOT be located inside a web-accessible area", NFS 등 느린 스토리지는 성능 문제, 캐시는 Redis/Memcached 권장 — [Installing Moodle](https://docs.moodle.org/en/Installing_Moodle)
- 플러그인 타입 56종(mod, block, qtype, filter, editor, enrol, auth, tool, logstore, availability, format, report, gradereport, repository, theme, local, contenttype, h5plib, qbank 등). 머신명은 소문자/숫자/밑줄(활동 모듈은 밑줄 불가) — [Plugin types](https://moodledev.io/docs/apis/plugintypes)
- 백업은 플랜/태스크/스텝 설계로 플러그인마다 분산 구현(KQ5) — [Backup API](https://moodledev.io/docs/apis/subsystems/backup)
- 웹서비스 프레임워크가 AJAX·모바일 앱·외부 연동을 모두 담당 — [External services](https://moodledev.io/docs/apis/subsystems/external)

**Oppia**
- "Its backend is written in Python, and its frontend is written using AngularJS and Angular." Google App Engine에서 실행; `main.py` 라우팅 → `core/controllers/`(thin handlers) → `core/domain/*_services.py`(비즈니스 로직)·`*_domain.py`(도메인 객체, from_dict/to_dict, 버전 변환) → `core/storage`(프로덕션은 Google Cloud Datastore via Cloud NDB); `core/platform/models.py`가 플랫폼 구현 선택; 프런트엔드는 MVC, `core/templates/domain|pages|components|services`, `-backend-api.ts`가 HTTP 호출; PEG.js 표현식 파서 — [Overview of the Oppia codebase](https://github.com/oppia/oppia/wiki/Overview-of-the-Oppia-codebase)
- `app_dev.yaml`: `runtime: python312`, `instance_class: F2`, entrypoint `gunicorn --timeout 60 --log-level warning --bind :$PORT main:app`, Datastore 에뮬레이터 env(`DATASTORE_EMULATOR_HOST: localhost:8089`), `FIREBASE_AUTH_EMULATOR_HOST: localhost:9099`, VPC access connector `oppia-redis-connector-1`, inbound services warmup/mail — [app_dev.yaml](https://raw.githubusercontent.com/oppia/oppia/develop/app_dev.yaml)
- `package.json`: `@angular/core ^11.2.10`, `typescript ~4.1.6`, `@angular-devkit/build-angular ^0.1102.10`, `engines` 필드 없음 — [package.json](https://raw.githubusercontent.com/oppia/oppia/develop/package.json)
- Linux 설치: Debian/Ubuntu는 `install_prerequisites.sh`; curl, git, unzip, openjdk-11-jre("needed for GCP to work"), Java 11+, Google Chrome(테스트용); pyenv로 "install Python 3.12.13"; direnv; `python -m scripts.start`로 dev 서버(localhost:8181, App Engine 콘솔 localhost:8000); `start.py`가 "the required dependencies (such as Google App Engine)"를 내려받음; RAM/디스크 수치 없음, 첫 실행 "about 5 - 10 minutes when we last tested it in Sep 2020"; sudo 사용 금지 — [Installing Oppia (Linux; Python 3)](https://github.com/oppia/oppia/wiki/Installing-Oppia-(Linux;-Python-3))
- 설치 인덱스는 Linux/Mac OS/Windows 가이드로 분기, Node 버전·RAM·Docker 미기재 — [Installing Oppia](https://github.com/oppia/oppia/wiki/Installing-Oppia)
- Docker 경로(검색 스니펫 기준; 위키 페이지 직접 fetch 시 Home으로 리다이렉트되어 본문 미확인): `make build` 시 의존성 약 2.1GB 다운로드, 첫 `make run-devserver`에 약 470MB 추가, Windows는 WSL2 백엔드 필수, "Experimental installation using Docker - under development" — [Installing Oppia using Docker](https://www.github.com/oppia/oppia/wiki/Installing-Oppia-using-Docker)
- Apache Beam 잡 위키 페이지가 존재(배치 처리) — [Overview of the Oppia codebase](https://github.com/oppia/oppia/wiki/Overview-of-the-Oppia-codebase)

### Inferences
- Moodle은 "LAMP 한 대"에 올릴 수 있는 반면 Oppia는 Datastore/Redis/Firebase/App Engine에 결합되어 셀프호스팅 현실성이 낮다. 엔터프라이즈 셀프호스팅을 전제로 하는 소규모 플랫폼은 Moodle 쪽(단일 DB + 파일 스토어 + 캐시 옵션)의 배포 무게를 상한으로, 그보다 가벼운 단일 바이너리/컨테이너 + SQLite/PostgreSQL을 목표로 잡는 것이 합리적이다.
- Oppia의 controllers → services → domain → storage 레이어 분리와 `platform/models.py`의 스토리지 추상화는 작은 코드베이스에도 유용한 구조이며, 도메인 객체의 `from_dict/to_dict` + 스키마 버전 변환 패턴은 Markdown frontmatter 파싱 계층에 그대로 적용 가능하다.
- Oppia가 2026년에도 Angular 11(2020년 릴리스)과 AngularJS 잔존을 안고 있다는 점은 대규모 프런트엔드 마이그레이션 부채의 사례다.

### Gaps
- Moodle의 "~1,000+ plugin types"라는 과제 전제는 사실과 다름: 공식 문서상 플러그인 *타입*은 56종이며, 플러그인 *개수*(디렉터리 등록 수)는 이번 조사에서 확인하지 않음.
- Oppia의 프로덕션 인스턴스 수/오토스케일 설정, Elasticsearch 사용 여부, Node 버전 요구는 미확인.
- Oppia Docker 위키 본문은 직접 읽지 못함(검색 스니펫 의존).

---

## KQ9. 진행 · 분석 모델 (완료 추적, 성적부, 로그, 역량 / Oppia 진행·숙련도·learner group)

### Takeaway
Moodle은 활동 완료(view/grade/passing grade/모듈별 조건/수동) → 코스 완료(Any/All 집계, 활동·타 코스·날짜·등록기간·성적·수동) → 성적부(grade item/category 집계) → 이벤트 기반 로그스토어(Standard/External DB) → 역량 프레임워크·학습계획(evidence, review, 자동 완료)로 이어지는 다층 모델이다. Oppia는 사용자별 CompletedActivities/IncompleteActivities(exploration/story/topic id 리스트), StoryProgress(completed_node_ids), ExplorationUserData(checkpoint), UserSkillMastery(degree_of_mastery float), LearnerGoals, 그리고 facilitator 주도의 LearnerGroup(syllabus = subtopic page + story)으로 진행을 표현한다.

### Cited Findings
**Moodle**
- 활동 완료 조건: None(기본), 수동("Mark as done"), View("students have to view the activity"), Require grade("Getting any grade will mark the activity completed"), Receive a passing grade(Require grade와 함께), Quiz(passing grade/attempts), Lesson(end reached/time spent), Assignment(submit), Forum(posts/discussions/replies); "Expect completed on"은 Timeline 알림용. 퀴즈 재응시 시 완료 아이콘 자동 갱신; 숨긴 성적이면 pass/fail 판정 불가; 잠긴 후 조건 변경 시 "all completion information for the activity will be deleted then recalculated" — [Activity completion settings](https://docs.moodle.org/en/Activity_completion_settings); 사이트 Advanced features에서 completion tracking 활성 필요, 교사는 "Override activity completion" 능력으로 수동 완료 처리 — [Activity completion](https://docs.moodle.org/en/Activity_completion)
- 코스 완료: "does not have a 'restrict access' function. It is best thought of as a report." 접근 제한은 활동 완료 기반으로 — [Course completion](https://docs.moodle.org/en/Course_completion); 조건: 전체 Any/All 집계, Activity completion(ALL/ANY), Completion of other courses, Date, Enrolment duration, Unenrolment, Course grade(rawgrade 기준), Manual self-completion(Self completion block), Manual completion by others(역할별 ALL/ANY) — [Course completion settings](https://docs.moodle.org/en/Course_completion_settings)
- 성적부(Grader report): 평가 항목이 추가되면 컬럼 생성, 원점수(raw)로 표시, 카테고리로 묶어 총점 계산, 미분류는 코스명 카테고리; 확장점은 grade reports/import/export 플러그인 — [Grader report](https://docs.moodle.org/en/Gradebook)
- 로깅: Site administration > Plugins > Logging > Manage log stores; Standard("very detailed and should meet most requirements")·External database(동일 포맷, 바쁜 사이트용); Write buffer size; 일부 logstore는 write-only라 Analytics 불가; 핵심 상호작용은 Events 서브시스템으로 기록; Moodle Analytics는 로그에 ML 적용 — [Logging](https://docs.moodle.org/en/Logging); 플러그인 타입 `logstore`(/admin/tool/log/store), `mlbackend` — [Plugin types](https://moodledev.io/docs/apis/plugintypes)
- 역량: 관리자가 competency framework 생성 → 학습계획 템플릿을 학생/코호트에 배정, 템플릿 통계로 진행 확인; 교사는 코스에 역량 연결, 활동 설정 시 역량 링크(복수 가능), "Upon activity completion"에 evidence 첨부/검토 요청/역량 완료 선택; 학생은 선행학습 evidence 업로드·검토 요청; Competency breakdown 보고서에서 평가; 예: 연결된 과제 통과 시 역량 자동 완료 — [Competencies](https://docs.moodle.org/en/Competencies)
- 5.3 학습성과(Learning outcomes): "Support for constructive alignment, including a new course page showing outcomes and linked activities" — [Moodle 5.3 release notes](https://moodledev.io/general/releases/5.3)
- 백업에 "user completion details, course logs, and grade history" 포함 가능 — [Course backup](https://docs.moodle.org/en/Course_backup)

**Oppia**
- 스토리지 모델: `CompletedActivitiesModel`(exploration_ids, collection_ids, story_ids, learnt_topic_ids, mastered_topic_ids), `IncompleteActivitiesModel`(…, partially_learnt_topic_ids, partially_mastered_topic_ids), `StoryProgressModel`(id `[user_id].[story_id]`, completed_node_ids), `ExplorationUserDataModel`(rating 1–5, draft change list, "furthest and most recently reached checkpoint state name and exploration version"), `LearnerPlaylistModel`, `LearnerGoalsModel`(topic_ids_to_learn, topic_ids_to_master), `UserSkillMasteryModel`("Model for storing a user's degree of mastery of a skill in Oppia"; id `[user_id].[skill_id]`, `degree_of_mastery` FloatProperty), `UserContributionProficiencyModel` — [core/storage/user/gae_models.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/storage/user/gae_models.py)
- `State.card_is_checkpoint`로 체크포인트 카드 지정; `Outcome.refresher_exploration_id`/`missing_prerequisite_skill_id`로 선행 개념 부족 시 리다이렉트 — [state_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/state_domain.py)
- `LearnerGroup`("Domain object for learner group"): group_id, title, description, facilitator_user_ids, learner_user_ids, invited_learner_user_ids, `subtopic_page_ids`("`topicId:subtopicId` format"), `story_ids`; 최소 1명 facilitator, 학습자/초대자/퍼실리테이터 역할 중복 금지 — [learner_group_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/learner_group_domain.py); URL `/create-learner-group`, `/edit-learner-group`, `MAX_CURRENT_GOALS_COUNT = 5` — [core/feconf.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/feconf.py)
- Topic의 `skill_ids_for_diagnostic_test`, Classroom의 `diagnostic_test_is_enabled`/`topic_id_to_prerequisite_topic_ids`(진단 테스트·선행 토픽) — [topic_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/topic_domain.py), [classroom_config_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/classroom_config_domain.py)
- Practice session(검색 스니펫 기준, 2023 제품 스펙 Google Doc): 학습자가 subtopic을 골라 10문항을 스킬 혼합으로 풀고 세션 점수와 스킬별 점수를 받으며, 로그인 사용자의 subtopic/topic 숙련도 점수가 첫 시도 정답 기준으로 Learner Dashboard에 표시 — [Practice sessions product spec (Google Doc PDF)](https://docs.google.com/document/d/1r9IEQ5z_t-eu9XAWN3eRA7iKdKuYsOQbVUjO2ZH1qKg/export?format=pdf)
- v3.5.3에서 "removed the Skills and Community sections from the new Learner Dashboard's Progress tab" — [v3.5.3](https://github.com/oppia/oppia/releases/tag/v3.5.3)

### Inferences
- Moodle의 핵심 교훈은 "완료"와 "성적"과 "역량"을 별개 엔티티로 두고 완료 조건을 모듈별 플러그인 규칙으로 선언한다는 점이다. 단일 코스 플랫폼은 (a) lesson 완료 조건(viewed / quiz passed / manual), (b) module/course 완료 집계(ALL/ANY), (c) 선택적 역량 매핑의 3단만 있어도 Moodle 수준의 리포팅을 흉내낼 수 있다.
- Oppia의 모델은 "ID 리스트" 수준의 가벼운 진행 저장(완료 exploration/story/topic ID 집합 + 스토리별 완료 노드 집합)이라 구현 비용이 매우 낮다. 여기에 `degree_of_mastery`(skill별 float)와 checkpoint만 더하면 "스킬 기반 복습/진단"이 가능해진다.
- 이벤트 소싱(Moodle Events → logstore)은 분석과 감사 로그를 동시에 해결하므로 enterprise-grade 요건(감사)과 학습 분석을 하나의 append-only 이벤트 테이블로 충족할 수 있다.

### Gaps
- Moodle 로그 이벤트의 필드 스키마(eventname, component, action, crud, edulevel, contextid 등)는 docs 페이지에 없어 미확인(개발자 Events API 페이지 미조사).
- Moodle 성적 집계 방식 목록(mean/weighted/natural 등)과 grade export 포맷은 Grader report 페이지에 없음.
- Oppia `degree_of_mastery`의 유효 범위(0–1로 추정)와 갱신 알고리즘(정답/오답에 따른 증감)은 코드에서 확인하지 못함.
- Oppia Learner Dashboard의 topic 단위 숙련도 계산식은 제품 스펙(비공식 Google Doc)에만 있음.

---

## KQ10. 소규모 Markdown-first 플랫폼을 위한 설계 포인트 (차용 / 회피)

### Takeaway
차용: (1) Moodle의 `component:action` 네이밍 + 컨텍스트 트리 + Inherit/Allow/Prevent/Prohibit RBAC, (2) Oppia의 lesson frontmatter에 `prerequisite_skills`/`acquired_skills`를 두는 스킬 그래프와 `degree_of_mastery`, (3) Oppia의 schema_version + 마이그레이션 관행과 StoryNode(=lesson) 그래프, (4) Moodle의 "완료 조건 선언 → 집계 → 역량"의 3단 진행 모델과 이벤트 로그, (5) `.mbz`식 "manifest + 콘텐츠 파일 + 해시 파일 스토어" 내보내기. 회피: Moodle의 RPC형 `wsfunction` API와 HTML-에디터 중심 저작(Markdown은 2급 시민), Oppia의 GCP 종속·공개 API 부재·평면 역할 16종 난립·HTML 문자열 콘텐츠.

### Cited Findings
- (차용) 컨텍스트 트리와 override 규칙, "capability to do something?"로 묻기 — [Access API](https://moodledev.io/docs/apis/subsystems/access), [Override permissions](https://docs.moodle.org/en/Override_permissions), [Context](https://docs.moodle.org/en/Context)
- (차용) `db/access.php`로 플러그인이 자기 능력을 선언하고 `archetypes`로 기본 역할 값을 제공 — [Access API](https://moodledev.io/docs/apis/subsystems/access)
- (차용) StoryNode의 `destination_node_ids` + `prerequisite_skill_ids`/`acquired_skill_ids`, Skill의 `misconceptions`/`rubrics`/`prerequisite_skill_ids` — [story_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/story_domain.py), [skill_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/skill_domain.py)
- (차용) `card_is_checkpoint`, `dest_if_really_stuck`, `refresher_exploration_id` — 레슨 내 체크포인트와 막힘 시 우회 경로 — [state_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/state_domain.py)
- (차용) `CURRENT_EXP_SCHEMA_VERSION = 62`, `EARLIEST_SUPPORTED_EXP_SCHEMA_VERSION = 46`, `from_yaml`이 범위 밖 버전은 거부 — [exp_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/exp_domain.py)
- (차용) 활동 완료 조건 선언 → 코스 완료 Any/All 집계 → 역량 evidence/자동 완료 — [Activity completion settings](https://docs.moodle.org/en/Activity_completion_settings), [Course completion settings](https://docs.moodle.org/en/Course_completion_settings), [Competencies](https://docs.moodle.org/en/Competencies)
- (차용) Events → pluggable logstore, 일부 스토어는 write-only — [Logging](https://docs.moodle.org/en/Logging)
- (차용) 백업 구조: 루트 `moodle_backup.xml` 지도 + `files.xml`/contenthash 스토어 + 활동별 디렉터리 — [Backup 2.0 general architecture](https://docs.moodle.org/dev/Backup_2.0_general_architecture), [Backup and restore FAQ](https://docs.moodle.org/en/Backup_and_restore_FAQ)
- (차용) scope 기반 토큰 + OAuth 2 client + SwaggerUI — [REST API tokens](https://docs.moodle.org/en/REST_API_tokens)
- (회피) 전통 웹서비스는 "not RESTful", `wsfunction` RPC — [Creating a web service client](https://docs.moodle.org/dev/Creating_a_web_service_client); 5.3 REST API도 "only a few parts of Moodle are available" — [REST API tokens](https://docs.moodle.org/en/REST_API_tokens)
- (회피) Markdown은 "Plain text area" 에디터 사용자만 선택 가능 — [Markdown](https://docs.moodle.org/en/Markdown)
- (회피) Oppia: App Engine/Datastore/Firebase/Redis 결합 — [app_dev.yaml](https://raw.githubusercontent.com/oppia/oppia/develop/app_dev.yaml); 역할 간 상속 없음, 16개 역할 — [role_services.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/role_services.py); 스토리 그래프가 실질 선형("assumes only a linear arrangement of nodes") — [story_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/story_domain.py); 콘텐츠는 `content.html` — [hola.yaml](https://raw.githubusercontent.com/oppia/oppia/develop/data/explorations/hola.yaml)
- (회피) IMS CC 내보내기 범위가 5개 활동으로 제한 — [IMS Common Cartridge import and export](https://docs.moodle.org/en/IMS_Common_Cartridge_import_and_export)

### Inferences
1. **권한 모델**: `course:edit`, `lesson:view`, `progress:read_any` 같은 `component:action` 능력 + 컨텍스트 4단(system/course/module/lesson) + 역할 archetype(admin/author/reviewer/learner) + 하위 컨텍스트 override(Prohibit 포함)를 채택. Oppia처럼 리소스 소유자 리스트(`owner_ids`)를 보조로 두면 Markdown 폴더 단위 권한을 쉽게 표현.
2. **콘텐츠 스키마**: lesson frontmatter에 `id, schema_version, module, order, prerequisite_skills[], acquired_skills[], checkpoint, estimated_minutes, next[]`를 두고 skills를 별도 `skills/*.yaml`(description, rubric, misconceptions, prerequisites)로 관리. 마이그레이션 스크립트는 Oppia식으로 `vN→vN+1` 함수 체인.
3. **진행 모델**: 이벤트 테이블(append-only, Moodle Events 유사) → lesson 완료 조건(viewed / quiz_passed / manual) → module/course 집계(ALL/ANY) → skill `degree_of_mastery`(Oppia). 리포트는 이벤트에서 파생.
4. **API**: 처음부터 OpenAPI + scope 토큰(개인 액세스 토큰 + OAuth2/OIDC 클라이언트), 내부 웹 UI도 같은 API 사용.
5. **내보내기/상호운용**: 정적 빌드 → (a) 자체 manifest+파일 zip(.mbz 교훈), (b) SCORM 1.2 래핑, (c) LTI 1.3 Tool(AGS) 제공 — 이 세 가지가 기업 LMS 연동의 최소 집합.
6. **배포 무게**: 단일 컨테이너 + PostgreSQL/SQLite + 파일 스토어, 외부 IdP 선택적. Oppia식 클라우드 종속은 피한다.

### Gaps
- 위 설계 포인트는 본 조사 결과로부터의 추론이며, 실제 Moodle/Oppia 사용자 커뮤니티의 만족도/불만 데이터(설문, 이슈 통계)는 수집하지 않음.

---

## KQ11. 비교 요약 표

### Takeaway
Moodle은 "범용·표준 준수·셀프호스팅 가능한 모놀리스", Oppia는 "스킬 기반 튜터형 레슨에 특화된 GCP 네이티브 앱"으로, 소규모 Markdown-first 플랫폼은 권한·진행·내보내기는 Moodle에서, 스킬 그래프·레슨 상태기계·스키마 버저닝은 Oppia에서 가져오는 조합이 적절하다.

### Cited Findings
| 항목 | Moodle LMS | Oppia |
|---|---|---|
| 라이선스 | GPL-3.0 (COPYING.txt = GPLv3 전문; GitHub spdx `GPL-3.0`) — [COPYING.txt](https://raw.githubusercontent.com/moodle/moodle/main/COPYING.txt), [GitHub API](https://api.github.com/repos/moodle/moodle) | Apache-2.0 (LICENSE 전문; README "Apache v2 license") — [LICENSE](https://raw.githubusercontent.com/oppia/oppia/develop/LICENSE), [README](https://github.com/oppia/oppia) |
| 현재 버전 (2026-11) | 5.3 (LTS, 2026-10-05); 4.5 LTS 보안지원 중; 6.0 2027-04 예정 — [Releases](https://moodledev.io/general/releases) | v3.5.3 (2026-09-23); develop `package.json` 3.5.4 — [GitHub API](https://api.github.com/repos/oppia/oppia/releases/latest), [package.json](https://raw.githubusercontent.com/oppia/oppia/develop/package.json) |
| 릴리스 주기 | 메이저 6개월(4/10월), 마이너 2개월 — [Releases](https://moodledev.io/general/releases) | 월간 cut(첫 수요일), 실제 공개는 2~4개월 간격 — [Release schedule](https://github.com/oppia/oppia/wiki/Release-schedule-and-other-information), [Releases](https://github.com/oppia/oppia/releases) |
| CLA | 요구 근거 없음; tracker 이슈 + HQ 통합팀 리뷰 — [Process](https://moodledev.io/general/development/process) | 필수("PRs… will be closed") — [Contributing](https://github.com/oppia/oppia/wiki/Contributing-code-to-Oppia) |
| 거버넌스 | Moodle Pty Ltd(HQ, B Corp); MUA 2024년 말 해산 → LMS Product Advisory Group — [moodle.com/about](https://moodle.com/about/), [MUA](https://moodle.org/mua) | Oppia Foundation Inc, 501(c)(3), EIN 81-1740068, FY2025 수입 $124,178 — [ProPublica](https://projects.propublica.org/nonprofits/organizations/811740068) |
| 로그인 | Manual, Email, External DB, LDAP, LTI, OAuth 2(OIDC discovery), Shibboleth, MFA; SAML2는 서드파티 auth_saml2 — [Managing authentication](https://docs.moodle.org/en/Managing_authentication), [OAuth 2 services](https://docs.moodle.org/en/OAuth_2_services), [auth_saml2](https://marketplace.moodle.com/plugins/auth_saml2) | Firebase Authentication(OIDC 1.0), 세션 쿠키 14일 — [firebase_auth_services.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/platform/auth/firebase_auth_services.py), [feconf.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/feconf.py) |
| 권한 모델 | 역할×능력×컨텍스트(10/30/40/50/70/80), Inherit/Allow/Prevent/Prohibit override — [Context](https://docs.moodle.org/en/Context), [Override permissions](https://docs.moodle.org/en/Override_permissions) | 평면 역할 16종 → 액션 집합 + 리소스 owner/editor/manager ID — [role_services.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/role_services.py) |
| API 인증 | `login/token.php` 토큰 + `webservice/rest/server.php?wstoken` RPC; 5.3 scope 기반 REST API(PAT + OAuth 2 client, SwaggerUI) — [Client guide](https://docs.moodle.org/dev/Creating_a_web_service_client), [REST API tokens](https://docs.moodle.org/en/REST_API_tokens) | 공개 API 없음; 내부 JSON 핸들러 + ACL 데코레이터 — [acl_decorators.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/controllers/acl_decorators.py) |
| 콘텐츠 계층 | course → section(+subsection) → activity(mod) ; Book/Page/Lesson 모듈 — [Course formats](https://docs.moodle.org/en/Course_formats), [Book](https://docs.moodle.org/en/Book_resource), [Lesson](https://docs.moodle.org/en/Lesson_activity) | classroom → topic → story → chapter(StoryNode) → exploration(state 카드) ; skill/subtopic — [topic_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/topic_domain.py), [story_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/story_domain.py) |
| 저장/교환 포맷 | HTML(TinyMCE) 중심, Markdown은 Plain text area 옵션; `.mbz`(tgz 기본, moodle_backup.xml) — [Markdown](https://docs.moodle.org/en/Markdown), [Backup FAQ](https://docs.moodle.org/en/Backup_and_restore_FAQ) | HTML 문자열 콘텐츠; exploration YAML(schema 62) — [hola.yaml](https://raw.githubusercontent.com/oppia/oppia/develop/data/explorations/hola.yaml), [exp_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/exp_domain.py) |
| 표준 | LTI Advantage(소비/제공), SCORM 1.2+AICC, H5P core, IMS CC 1.0/1.1 in·1.1 out, Open Badges 2.x, xAPI 라이브러리(LRS 아님) — [Standards](https://docs.moodle.org/en/Standards), [xAPI](https://moodledev.io/docs/apis/subsystems/xapi) | 확인된 표준 지원 없음 — [README](https://github.com/oppia/oppia) |
| 스택/배포 | PHP 8.3+, PostgreSQL 17/MySQL 8.4/MariaDB 11.4/MSSQL 2019; 512MB–1GB RAM, 5GB 디스크 현실 최소; 56 플러그인 타입 — [5.3 notes](https://moodledev.io/general/releases/5.3), [Installing](https://docs.moodle.org/en/Installing_Moodle), [Plugin types](https://moodledev.io/docs/apis/plugintypes) | Python 3.12 + App Engine(gunicorn, F2) + Cloud Datastore/NDB + Redis + Firebase; Angular 11/AngularJS; Java 11·Chrome·pyenv 필요 — [app_dev.yaml](https://raw.githubusercontent.com/oppia/oppia/develop/app_dev.yaml), [Linux install](https://github.com/oppia/oppia/wiki/Installing-Oppia-(Linux;-Python-3)) |
| 진행/분석 | 활동 완료 → 코스 완료(Any/All) → 성적부 → Events/logstore → 역량·학습계획, 5.3 학습성과 — [Activity completion settings](https://docs.moodle.org/en/Activity_completion_settings), [Course completion settings](https://docs.moodle.org/en/Course_completion_settings), [Logging](https://docs.moodle.org/en/Logging), [Competencies](https://docs.moodle.org/en/Competencies) | Completed/IncompleteActivities, StoryProgress(completed_node_ids), checkpoint, UserSkillMastery(float), LearnerGoals, LearnerGroup(facilitator+syllabus), 진단 테스트 — [user gae_models.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/storage/user/gae_models.py), [learner_group_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/learner_group_domain.py) |

### Inferences
- 표의 좌/우 열은 "범용 LMS 인프라" 대 "학습 과학 중심 콘텐츠 모델"의 대비로 읽힌다. 목표 플랫폼(단일 전문가 코스, Markdown, 기업용)은 인프라 측면에서는 Moodle보다 훨씬 가볍게, 콘텐츠 모델 측면에서는 Oppia의 스킬/체크포인트 개념을 frontmatter로 단순화해 채택하는 것이 타당하다.

### Gaps
- Moodle 플러그인 디렉터리의 총 플러그인 수, Oppia 등록 사용자/레슨 수 등 규모 지표는 수집하지 않음.
- 두 플랫폼의 접근성(WCAG) 비교는 Moodle만 2.1 AA 인증 기재가 있고 Oppia는 미조사.
