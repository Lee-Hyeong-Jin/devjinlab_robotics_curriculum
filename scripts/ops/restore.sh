#!/usr/bin/env bash
# Restore a dump produced by scripts/ops/backup.sh (P2-5, AC-OPS.4).
#
#   bash scripts/ops/restore.sh backups/rc-20261111T020000Z.dump
#   FORCE=1 bash scripts/ops/restore.sh <dump>   # skip the confirmation prompt
#
# This REPLACES the contents of the target database: every object in the dump is dropped and
# recreated. Stop the api service first so nothing writes during the restore.
set -euo pipefail

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$root"

dump="${1:-}"
db_user="${POSTGRES_USER:-rc}"
db_name="${POSTGRES_DB:-rc}"

[ -n "$dump" ] || {
  echo "usage: bash scripts/ops/restore.sh <dump file>" >&2
  exit 2
}
[ -f "$dump" ] || {
  echo "error: no such dump: $dump" >&2
  exit 2
}

if ! docker compose ps --status running --services 2>/dev/null | grep -qx db; then
  echo "error: the 'db' service is not running (docker compose up -d --wait db)" >&2
  exit 1
fi

if [ -z "${FORCE:-}" ]; then
  printf 'Replace the contents of database "%s" with %s? [y/N] ' "$db_name" "$dump"
  read -r answer </dev/tty || answer=""
  case "$answer" in
    y | Y | yes | YES) ;;
    *)
      echo "aborted"
      exit 1
      ;;
  esac
fi

echo "--- stopping api (if running) so the restore is not raced"
docker compose stop api >/dev/null 2>&1 || true

echo "--- pg_restore <- $dump"
# --clean --if-exists drops the dumped objects first; --exit-on-error so a partial restore fails
# loudly instead of leaving a half-populated database behind.
if ! docker compose exec -T db pg_restore --clean --if-exists --no-owner --no-privileges \
  --exit-on-error -U "$db_user" -d "$db_name" <"$dump"; then
  echo "error: pg_restore failed; the database may be partially restored" >&2
  exit 1
fi
echo "  OK   restored"

echo "--- starting api"
docker compose up -d --wait api
echo "RESTORE DONE (check: curl -fsS http://127.0.0.1:8000/readyz)"
