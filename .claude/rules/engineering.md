# 엔지니어링 규칙

- 작업은 개발 그래프(harness/graph.md)의 노드 단위로 한다: 명세 없이 구현하지 않고, 검증(scripts/harness/check.sh) 없이 끝내지 않는다.
- 루프는 항상 종료 조건과 최대 반복 수를 가진다. 같은 실패로 3회 반복하면 멈추고 사람에게 보고한다.
- 동작 변경에는 테스트가 따른다. 테스트를 약화·skip·삭제해서 통과시키지 않는다.
- Python 은 `uv run` 으로 실행한다(`uv run pytest`, `uv run ruff check .`). 의존성은 `uv add`.
- 되돌리기 비싼 결정(스택, 저장소, 알고리즘, 외부 서비스)은 docs/adr/ 에 ADR 로 남긴다(`/adr`).
- main/master 에 직접 커밋하지 않는다. 작업 브랜치 또는 워크트리에서 커밋하고 push 는 사용자가 한다.
- `git stash`(bare), `git reset --hard`, `git checkout -- .`, 강제 push 는 금지. 작업을 잠시 치울 땐 WIP 커밋을 쓴다.
- `.env` 와 비밀은 읽지도 커밋하지도 않는다. 설정 예시는 `.env.example` 에만 쓴다.
- 커밋 메시지: `type(scope): summary` (feat, fix, chore, docs, test, refactor). 마일스톤 커밋은 scope 에 마일스톤 id.
- 보고는 사실만: 실행한 명령과 출력에 근거해 말하고, 확인하지 않은 것은 확인하지 않았다고 쓴다.
