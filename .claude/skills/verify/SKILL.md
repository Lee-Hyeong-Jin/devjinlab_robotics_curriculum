---
name: verify
description: 검증 게이트를 직접 실행한다(scripts/harness/check.sh - 린트, 타입, 테스트). 워크플로 없이 현재 세션에서 바로 돌리고, 실패가 있으면 이 세션에서 고친다. 코드를 바꾼 뒤 끝내기 전에 사용.
argument-hint: "[--quick]"
---

1. `bash scripts/harness/check.sh $ARGUMENTS` 를 실행한다(`--quick` 이면 테스트 생략).
2. "no build stack detected" 가 나오면 아직 pyproject.toml / package.json 이 없다는 뜻이다. 그렇게 보고하고 끝낸다.
3. FAIL 항목이 있으면 원인을 찾아 고친다. 테스트를 약화시키거나 skip 하지 않는다. 고친 뒤 다시 1 을 실행해 ALL CHECKS PASSED 를 확인한다.
4. 결과를 한두 줄로 보고한다(통과한 검사 목록, 고친 내용).
