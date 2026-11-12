#!/usr/bin/env bash
# Verification gate (the "verify" node of the dev graph).
# Usage: scripts/harness/check.sh [--quick]
#   --quick : lint + type-check only, Python only (used by the Stop hook)
#   (none)  : lint + type-check + tests for every detected stack (with the coverage gate when
#             pytest-cov is present), installing web/node_modules first if it is missing,
#             then `rc validate` and a strict static-site build when curriculum/ exists
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
# Reads package.json in the current directory; the node branch cd's into $node_dir first.
has_script() { python3 -I -c "import json,sys; sys.exit(0 if '$1' in json.load(open('package.json')).get('scripts',{}) else 1)" 2>/dev/null; }
# The frontend lives in web/ (P2-4); a root package.json still wins if someone adds one.
node_dir="."; [ -f package.json ] || { [ -f web/package.json ] && node_dir="web"; }

stacks="$(bash "$root/scripts/harness/detect_stack.sh")"

for s in $stacks; do
  case "$s" in
    python)
      PY=""; have uv && PY="uv run --quiet"
      if $PY ruff --version >/dev/null 2>&1; then
        run "ruff check" $PY ruff check .
        run "ruff format --check" $PY ruff format --check .
      fi
      # mypy targets come from [tool.mypy] files in pyproject.toml (src/, strict).
      $PY mypy --version >/dev/null 2>&1 && run "mypy" $PY mypy
      if [ "$quick" = 0 ] && $PY pytest --version >/dev/null 2>&1; then
        # With pytest-cov installed, enforce [tool.coverage.report] fail_under.
        cov=""; $PY python -c "import pytest_cov" >/dev/null 2>&1 && cov="--cov --cov-report=term"
        run "pytest" $PY pytest -q $cov
      fi
      ;;
    node)
      # The Stop hook runs --quick after every turn; a frontend install plus lint is far too
      # slow for that, and most turns here touch Python only. CI and a full check.sh cover web.
      if [ "$quick" = 1 ]; then
        echo "> frontend checks ($node_dir)"
        echo "  SKIP --quick skips the node stack (CI and a full check.sh run it)"
        continue
      fi
      pm=npm
      [ -f "$node_dir/pnpm-lock.yaml" ] && pm=pnpm
      [ -f "$node_dir/yarn.lock" ] && pm=yarn
      cd "$root/$node_dir" || exit 1
      # A fresh worktree has no node_modules, so the scripts below would die with exit 127.
      if [ ! -d node_modules ]; then
        printf '> %s install (%s/node_modules missing)\n' "$pm" "$node_dir"
        if [ "$pm" = npm ] && [ -f package-lock.json ]; then
          install_cmd="npm ci"
        else
          install_cmd="$pm install"
        fi
        if ! $install_cmd >/dev/null 2>&1; then
          printf '  FAIL %s in %s. Run it by hand to see why (no network in this environment?).\n' \
            "$install_cmd" "$node_dir"
          status=1
          cd "$root" || exit 1
          continue
        fi
        printf '  OK   %s\n' "$install_cmd"
      fi
      has_script lint && run "$pm run lint ($node_dir)" $pm run --silent lint
      has_script typecheck && run "$pm run typecheck ($node_dir)" $pm run --silent typecheck
      has_script format:check && run "$pm run format:check ($node_dir)" $pm run --silent format:check
      if [ "$quick" = 0 ] && has_script test; then
        run "$pm run test ($node_dir)" $pm run --silent test
      fi
      cd "$root" || exit 1
      ;;
    none)
      echo "INFO no build stack detected (no pyproject.toml / package.json) - nothing to check"
      ;;
  esac
done

# -- content gate -------------------------------------------------------------------------
# Not a "stack": the curriculum and the static site it has to build into. `rc site build`
# only *warned* about a broken lesson link and still exited 0, so bad content reached a green
# CI run; --strict makes a mkdocs warning a failure.
if [ "$quick" = 0 ] && [ -d "$root/curriculum" ]; then
  PY=""; have uv && PY="uv run --quiet"
  # `rc version` is a subcommand, not a flag; this is the cheapest "is rc installed" probe.
  if $PY rc version >/dev/null 2>&1; then
    run "rc validate" $PY rc validate
    site_out="$(mktemp -d -t rc-site-check-XXXXXX)"
    run "rc site build --strict" $PY rc site build --strict --out "$site_out"
    rm -rf "$site_out"
  fi
fi

if [ "$status" = 0 ]; then echo "ALL CHECKS PASSED"; else echo "CHECKS FAILED"; fi
exit $status
