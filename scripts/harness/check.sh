#!/usr/bin/env bash
# Verification gate (the "verify" node of the dev graph).
# Usage: scripts/harness/check.sh [--quick]
#   --quick : lint + type-check only (used by the Stop hook)
#   (none)  : lint + type-check + tests
# Exit 0 = all green, or no stack configured. Non-zero = something failed.
set -u
root="$(git rev-parse --show-toplevel 2>/dev/null || echo "${CLAUDE_PROJECT_DIR:-$PWD}")"
cd "$root" || exit 1
quick=0; [ "${1:-}" = "--quick" ] && quick=1
status=0

run() { # run <label> <cmd...>
  local label="$1"; shift
  printf '> %s\n' "$label"
  if "$@"; then printf '  OK   %s\n' "$label"; else printf '  FAIL %s (exit %s)\n' "$label" "$?"; status=1; fi
}
have() { command -v "$1" >/dev/null 2>&1; }
has_script() { python3 -I -c "import json,sys; sys.exit(0 if '$1' in json.load(open('package.json')).get('scripts',{}) else 1)" 2>/dev/null; }

stacks="$(bash "$root/scripts/harness/detect_stack.sh")"

for s in $stacks; do
  case "$s" in
    python)
      PY=""; have uv && PY="uv run --quiet"
      if $PY ruff --version >/dev/null 2>&1; then
        run "ruff check" $PY ruff check .
        run "ruff format --check" $PY ruff format --check .
      fi
      $PY mypy --version >/dev/null 2>&1 && run "mypy" $PY mypy .
      if [ "$quick" = 0 ] && $PY pytest --version >/dev/null 2>&1; then
        run "pytest" $PY pytest -q
      fi
      ;;
    node)
      pm=npm; [ -f pnpm-lock.yaml ] && pm=pnpm; [ -f yarn.lock ] && pm=yarn
      has_script lint      && run "$pm run lint"      $pm run --silent lint
      has_script typecheck && run "$pm run typecheck" $pm run --silent typecheck
      if [ "$quick" = 0 ] && has_script test; then
        run "$pm run test" $pm run --silent test
      fi
      ;;
    none)
      echo "INFO no build stack detected (no pyproject.toml / package.json) - nothing to check"
      ;;
  esac
done

if [ "$status" = 0 ]; then echo "ALL CHECKS PASSED"; else echo "CHECKS FAILED"; fi
exit $status
