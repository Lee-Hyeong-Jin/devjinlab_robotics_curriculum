#!/usr/bin/env bash
# SessionStart hook: inject a short project / graph status into context.
set -u
root="$(git rev-parse --show-toplevel 2>/dev/null || echo "${CLAUDE_PROJECT_DIR:-$PWD}")"
cd "$root" || exit 0
tmp="$(mktemp 2>/dev/null || echo "${TMPDIR:-/tmp}/claude_session_ctx.$$")"
{
  echo "## Harness status"
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "- branch: $(git branch --show-current 2>/dev/null || echo '(detached)')"
    echo "- uncommitted changes: $(git status --porcelain 2>/dev/null | wc -l | tr -d ' ') file(s)"
    echo "- last commit: $(git log -1 --format='%h %s' 2>/dev/null || echo none)"
  else
    echo "- not a git repository"
  fi
  echo "- stack: $(bash scripts/harness/detect_stack.sh | paste -sd, -)"
  if [ -f harness/roadmap.yaml ]; then
    echo "- roadmap (harness/roadmap.yaml):"
    python3 -I "$root/scripts/harness/roadmap.py" summary 2>/dev/null | sed 's/^/    /'
  fi
  echo "- verify gate: scripts/harness/check.sh | graph spec: harness/graph.md | docs: docs/HARNESS.md"
} > "$tmp"
python3 -I -c 'import json,sys; print(json.dumps({"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":open(sys.argv[1]).read()}}))' "$tmp"
rm -f "$tmp"
exit 0
