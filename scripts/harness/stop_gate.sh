#!/usr/bin/env bash
# Stop hook: when Claude is about to end a turn with uncommitted code changes,
# run the quick verification gate. On failure, block the stop so the failure is
# fixed before the turn ends. stop_hook_active prevents re-entrancy.
set -u
input="$(cat)"
active="$(printf '%s' "$input" | python3 -I -c 'import json,sys; print(str(json.load(sys.stdin).get("stop_hook_active", False)).lower())' 2>/dev/null)"
[ "$active" = "true" ] && exit 0
root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$root" || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
# Only code-ish changes trigger the gate; docs/content edits do not.
changed="$(git status --porcelain --untracked-files=all 2>/dev/null | awk '{print $2}' | grep -E '\.(py|ts|tsx|js|jsx|toml)$' | grep -v '^\.claude/' || true)"
[ -z "$changed" ] && exit 0
stack="$(bash scripts/harness/detect_stack.sh)"
[ "$stack" = "none" ] && exit 0
out="$(bash scripts/harness/check.sh --quick 2>&1)"
rc=$?
if [ "$rc" -ne 0 ]; then
  printf '%s' "$out" | tail -40 | python3 -I -c 'import json,sys; print(json.dumps({"decision":"block","reason":"Verification gate failed (scripts/harness/check.sh --quick). Fix before finishing:\n"+sys.stdin.read()}))'
fi
exit 0
