#!/usr/bin/env bash
# PostToolUse formatter for Edit/Write. Reads hook JSON on stdin and formats the
# touched file with whatever formatter the stack provides. Never fails the tool.
set -u
f="$(python3 -I -c 'import json,sys; d=json.load(sys.stdin); print(d.get("tool_response",{}).get("filePath") or d.get("tool_input",{}).get("file_path",""))' 2>/dev/null)"
[ -n "$f" ] && [ -f "$f" ] || exit 0
root="$(git rev-parse --show-toplevel 2>/dev/null || echo "${CLAUDE_PROJECT_DIR:-$PWD}")"
cd "$root" || exit 0
have() { command -v "$1" >/dev/null 2>&1; }
case "$f" in
  *.py)
    if have uv && uv run --quiet ruff --version >/dev/null 2>&1; then
      uv run --quiet ruff format "$f" >/dev/null 2>&1
      uv run --quiet ruff check --fix --quiet "$f" >/dev/null 2>&1
    elif have ruff; then
      ruff format "$f" >/dev/null 2>&1
      ruff check --fix --quiet "$f" >/dev/null 2>&1
    fi ;;
  *.ts|*.tsx|*.js|*.jsx|*.json|*.css|*.yaml|*.yml)
    if [ -f package.json ] && have npx; then
      npx --no-install prettier --write --log-level silent "$f" >/dev/null 2>&1
    fi ;;
esac
exit 0
