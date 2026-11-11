#!/usr/bin/env bash
# Recovery rehearsal (P2-5, AC-OPS.4): prove that a backup can actually be restored.
#
#   bash scripts/ops/restore_drill.sh
#
# What it does, against the local compose stack:
#   1. brings up db -> migrate -> api
#   2. writes a marker through the API (marks a real lesson done)
#   3. takes a backup with scripts/ops/backup.sh
#   4. destroys the data (drops the public schema) to simulate the loss
#   5. restores the dump and checks /readyz plus the marker through the API
#   6. appends the result to docs/ops/restore-drills.md
#
# It is destructive by design and meant for a drill environment, never production. Run the
# restore itself (scripts/ops/restore.sh) against production instead.
set -euo pipefail

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$root"

base="http://127.0.0.1:8000"
log="docs/ops/restore-drills.md"
started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
db_user="${POSTGRES_USER:-rc}"
db_name="${POSTGRES_DB:-rc}"

# compose has no default secrets (server review SRV-06); use throwaway ones for the drill.
rand() { od -An -N16 -tx1 /dev/urandom | tr -d ' \n'; }
export RC_DB_PASSWORD="${RC_DB_PASSWORD:-drill-$(rand)}"
export RC_AUTH_SECRET="${RC_AUTH_SECRET:-drill-$(rand)}"

fail() {
  echo "  FAIL $*" >&2
  exit 1
}

# The compose api runs in server mode (SRV-01), so every call carries the drill session.
sid=""
csrf=""

api_json() { # path -> body on stdout
  curl -fsS --max-time 15 -H "Cookie: sid=$sid" "$base$1" || fail "GET $1 failed"
}

echo "--- bringing the stack up"
docker compose up -d --wait --wait-timeout 300 api >/dev/null

echo "--- creating the drill account"
email="drill-$(rand | head -c 8)@example.org"
password="Drill-pass-$(rand | head -c 12)"
cred="{\"email\":\"$email\",\"password\":\"$password\"}"
curl -fsS --max-time 15 -o /dev/null -H 'Content-Type: application/json' -d "$cred" \
  "$base/api/v1/auth/signup" || fail "signup failed"
jar="$(mktemp)"
login="$(curl -fsS --max-time 15 -c "$jar" -H 'Content-Type: application/json' -d "$cred" \
  "$base/api/v1/auth/login")" || fail "login failed"
sid="$(awk '$6=="sid"{print $7}' "$jar")"
csrf="$(printf '%s' "$login" | python3 -I -c 'import json,sys; print(json.load(sys.stdin)["csrf_token"])')"
rm -f "$jar"
[ -n "$sid" ] && [ -n "$csrf" ] || fail "login returned no session or CSRF token"
echo "  OK   drill account $email"

echo "--- picking a lesson to use as the marker"
lesson="$(api_json /api/v1/progress/next | python3 -I -c '
import json, sys
items = json.load(sys.stdin)
if not items:
    sys.exit("no lessons returned by /api/v1/progress/next")
print(items[0]["lesson"]["id"])
')"
[ -n "$lesson" ] || fail "could not determine a lesson id"
echo "  OK   marker lesson: $lesson"

echo "--- marking it done through the API"
curl -fsS --max-time 15 -X POST "$base/api/v1/progress/done" \
  -H 'Content-Type: application/json' -H "Cookie: sid=$sid" -H "X-CSRF-Token: $csrf" \
  -d "{\"lesson_id\":\"$lesson\",\"note\":\"restore drill $started\"}" >/dev/null ||
  fail "POST /api/v1/progress/done failed"

marker_count() { # how many lessons are recorded as done
  api_json /api/v1/progress/lessons | python3 -I -c '
import json, sys
print(sum(1 for row in json.load(sys.stdin) if row.get("status") == "done"))
'
}
before="$(marker_count)"
[ "$before" -ge 1 ] || fail "the marker was not recorded (done count $before)"
echo "  OK   done lessons before backup: $before"

echo "--- backup"
dump="$(bash scripts/ops/backup.sh | tail -n1)"
[ -f "$dump" ] || fail "backup did not produce a dump"

echo "--- simulating data loss (drop schema public)"
docker compose stop api >/dev/null
docker compose exec -T db psql -q -U "$db_user" -d "$db_name" \
  -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;' >/dev/null ||
  fail "could not drop the schema"
echo "  OK   schema dropped"

echo "--- restore"
FORCE=1 bash scripts/ops/restore.sh "$dump" >/dev/null || fail "restore failed"

echo "--- verifying"
status="$(curl -fsS -o /dev/null -w '%{http_code}' --max-time 15 "$base/readyz" || true)"
[ "$status" = "200" ] || fail "/readyz returned ${status:-no response} after the restore"
echo "  OK   /readyz 200"

after="$(marker_count)"
[ "$after" = "$before" ] || fail "done lessons: $before before, $after after the restore"
echo "  OK   done lessons after restore: $after"

finished="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
mkdir -p "$(dirname "$log")"
if [ ! -f "$log" ]; then
  cat >"$log" <<'HEADER'
# Restore drills

Each row is one run of `bash scripts/ops/restore_drill.sh`: back up, destroy the data, restore,
then check `/readyz` and that the recorded progress survived. The release checklist
(docs/architecture/operations.md §5) asks for one drill per release.

| Started (UTC) | Finished (UTC) | Dump | Done lessons before / after | Result |
|---|---|---|---|---|
HEADER
fi
printf '| %s | %s | `%s` | %s / %s | PASS |\n' \
  "$started" "$finished" "$(basename "$dump")" "$before" "$after" >>"$log"

echo "DRILL PASSED (recorded in $log)"
