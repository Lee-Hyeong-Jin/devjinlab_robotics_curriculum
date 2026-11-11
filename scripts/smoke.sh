#!/usr/bin/env bash
# Server-mode smoke test (P2-5, AC-OPS.2): bring up db -> migrate -> api with compose and check
# that the API answers. Run from the repository root:
#
#   bash scripts/smoke.sh            # build, up, check, then tear down
#   KEEP_UP=1 bash scripts/smoke.sh  # leave the stack running for manual poking
#
# Requires docker with the compose plugin. Exits non-zero on the first failed check.
set -euo pipefail

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$root"

compose() { docker compose "$@"; }
base="http://127.0.0.1:8000"
keep="${KEEP_UP:-}"

cleanup() {
  rc=$?
  if [ -z "$keep" ]; then
    echo "--- tearing down"
    compose logs --no-color --tail 30 api migrate >"${SMOKE_LOG:-/tmp/rc-smoke-compose.log}" 2>&1 || true
    compose down --volumes --remove-orphans >/dev/null 2>&1 || true
  else
    echo "--- stack left running (KEEP_UP=1); stop it with: docker compose down -v"
  fi
  if [ "$rc" -ne 0 ]; then
    echo "SMOKE FAILED (exit $rc). Recent service logs:"
    compose logs --no-color --tail 40 api migrate 2>&1 | sed 's/^/  /' || true
  fi
  exit "$rc"
}
trap cleanup EXIT

fail() {
  echo "  FAIL $*" >&2
  exit 1
}

# `--wait` blocks until every started service is healthy (api) or has completed (migrate).
echo "--- docker compose up -d --wait api"
compose up -d --wait --wait-timeout 300 api

echo "--- migrate ran to completion"
state="$(compose ps --all --format '{{.Service}} {{.State}} {{.ExitCode}}' | awk '$1=="migrate"{print $2" "$3}')"
case "$state" in
  "exited 0") echo "  OK   migrate exited 0" ;;
  *) fail "migrate did not finish cleanly (state: ${state:-missing})" ;;
esac

check() {
  local path="$1" expect="$2" grep_for="${3:-}"
  local body code
  body="$(curl -fsS -w '\n%{http_code}' --max-time 10 "$base$path" 2>/dev/null)" || fail "$path did not respond"
  code="$(printf '%s' "$body" | tail -n1)"
  body="$(printf '%s' "$body" | sed '$d')"
  [ "$code" = "$expect" ] || fail "$path returned $code, expected $expect"
  if [ -n "$grep_for" ]; then
    printf '%s' "$body" | grep -q "$grep_for" || fail "$path body lacks '$grep_for': ${body:0:200}"
  fi
  echo "  OK   $path -> $code"
}

echo "--- system endpoints"
check /healthz 200 '"status"'
check /readyz 200 '"status"'
check /version 200 '"version"'

echo "--- api endpoints"
check /openapi.json 200 '"openapi"'
check /api/v1/courses 200 'robotics-expert'

echo "--- metrics"
# /metrics is optional until the api session's work lands, and RC_API_METRICS=0 turns it off.
mcode="$(curl -fsS -o /tmp/rc-smoke-metrics -w '%{http_code}' --max-time 10 "$base/metrics" 2>/dev/null || true)"
case "$mcode" in
  200)
    grep -q 'http_requests_total' /tmp/rc-smoke-metrics ||
      fail "/metrics lacks http_requests_total: $(head -c 200 /tmp/rc-smoke-metrics)"
    echo "  OK   /metrics -> 200 with http_requests_total"
    ;;
  404 | "")
    echo "  SKIP /metrics not served (RC_API_METRICS=0 or not implemented yet)"
    ;;
  *) fail "/metrics returned $mcode" ;;
esac
rm -f /tmp/rc-smoke-metrics

echo "--- request id correlation"
rid="smoke-$$"
got="$(curl -fsS -o /dev/null -D - --max-time 10 -H "X-Request-ID: $rid" "$base/healthz" |
  tr -d '\r' | awk 'tolower($1)=="x-request-id:"{print $2}')"
[ "$got" = "$rid" ] || fail "X-Request-ID not echoed (got '${got:-none}')"
echo "  OK   X-Request-ID echoed"

echo "--- logs are single-line JSON"
compose logs --no-color --tail 50 api | sed 's/^api[^|]*| *//' | grep -c '^{.*}$' >/dev/null ||
  fail "no JSON log lines found in api output"
echo "  OK   JSON logs"

echo "SMOKE PASSED"
