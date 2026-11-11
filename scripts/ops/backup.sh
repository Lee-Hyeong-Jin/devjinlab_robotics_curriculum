#!/usr/bin/env bash
# Back up the PostgreSQL database to a compressed custom-format dump (P2-5, AC-OPS.4).
#
#   bash scripts/ops/backup.sh                  # -> backups/rc-<utc timestamp>.dump
#   BACKUP_DIR=/srv/backups bash scripts/ops/backup.sh
#   RETENTION_DAYS=30 bash scripts/ops/backup.sh   # prune older dumps (0 = keep everything)
#
# The dump is taken with `pg_dump -Fc` inside the `db` service, so the client and server
# versions always match. Restore it with scripts/ops/restore.sh.
#
# Operational contract (docs/architecture/operations.md §5): daily at 02:00, 30-day retention,
# RPO 24h / RTO 4h. Ship the dumps off the host (object storage, server-side encryption) —
# a dump sitting next to the database is not a backup.
set -euo pipefail

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$root"

backup_dir="${BACKUP_DIR:-$root/backups}"
retention="${RETENTION_DAYS:-30}"
db_user="${POSTGRES_USER:-rc}"
db_name="${POSTGRES_DB:-rc}"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
target="$backup_dir/rc-$stamp.dump"

mkdir -p "$backup_dir"

if ! docker compose ps --status running --services 2>/dev/null | grep -qx db; then
  echo "error: the 'db' service is not running (docker compose up -d --wait db)" >&2
  exit 1
fi

echo "--- pg_dump -> $target"
# -Fc: custom format (compressed, selective restore). Write to a temp name so a failed dump
# never looks like a usable backup.
if ! docker compose exec -T db pg_dump -Fc -U "$db_user" -d "$db_name" >"$target.part" 2>"$target.err"; then
  echo "error: pg_dump failed:" >&2
  sed 's/^/  /' "$target.err" >&2
  rm -f "$target.part" "$target.err"
  exit 1
fi
rm -f "$target.err"
mv "$target.part" "$target"

size="$(wc -c <"$target" | tr -d ' ')"
[ "$size" -gt 0 ] || {
  echo "error: dump is empty" >&2
  exit 1
}
echo "  OK   $(basename "$target") ($size bytes)"

if [ "$retention" -gt 0 ]; then
  # -mtime +N is whole days; keep it simple and predictable.
  pruned="$(find "$backup_dir" -maxdepth 1 -name 'rc-*.dump' -type f -mtime "+$retention" -print -delete | wc -l | tr -d ' ')"
  [ "$pruned" = "0" ] || echo "  OK   pruned $pruned dump(s) older than $retention days"
fi

echo "$target"
