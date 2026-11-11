#!/usr/bin/env bash
# Pull-based continuous deployment for a single host (home server, small VPS).
#
# Run it from cron or a systemd timer inside a deployment checkout of this repository:
#
#   */5 * * * * /path/to/rc-deploy/scripts/ops/deploy_pull.sh >> /path/to/rc-deploy/deploy.log 2>&1
#
# Each run:
#   1. fetches origin/<branch>; stops if there is nothing new
#   2. deploys only a commit whose GitHub Actions "CI" workflow run concluded "success"
#   3. takes a database backup (scripts/ops/backup.sh) before touching the stack
#   4. fast-forwards the checkout, rebuilds and restarts the compose stack, waits for health
#   5. on failure, puts the previous commit back and restarts it
#
# No inbound access and no GitHub secret are needed: the host only makes outbound requests.
# Private repositories need DEPLOY_GITHUB_TOKEN (read access to Actions) for step 2.
#
# Configuration (environment, all optional):
#   DEPLOY_DIR            deployment checkout            (default: the repository this script is in)
#   DEPLOY_BRANCH         branch to follow               (default: main)
#   DEPLOY_PROJECT        docker compose project name    (default: rc)
#   DEPLOY_REQUIRE_CI     1 = wait for a green CI run    (default: 1)
#   DEPLOY_CI_WORKFLOW    workflow name to require       (default: CI)
#   DEPLOY_GITHUB_TOKEN   token for private repositories (default: none)
#   DEPLOY_SKIP_BACKUP    1 = do not back up first       (default: 0)
#   DEPLOY_HEALTH_URLS    space-separated URLs that must answer 200 after the deploy
#                         (default: http://127.0.0.1:8000/readyz http://127.0.0.1:3000/login)
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="${DEPLOY_DIR:-$(cd "$here/../.." && pwd)}"
BRANCH="${DEPLOY_BRANCH:-main}"
PROJECT="${DEPLOY_PROJECT:-rc}"
REQUIRE_CI="${DEPLOY_REQUIRE_CI:-1}"
WORKFLOW="${DEPLOY_CI_WORKFLOW:-CI}"
HEALTH_URLS="${DEPLOY_HEALTH_URLS:-http://127.0.0.1:8000/readyz http://127.0.0.1:3000/login}"

log() { printf '%s deploy: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }

cd "$DEPLOY_DIR"

# One run at a time: a build can outlast the timer interval.
exec 9>"$DEPLOY_DIR/.deploy.lock"
if ! flock -n 9; then
  log "another run holds the lock; skipping"
  exit 0
fi

# Compose reads the secrets from .env in the deployment checkout.
if [ ! -f .env ]; then
  log "missing $DEPLOY_DIR/.env (see .env.example); refusing to deploy"
  exit 1
fi

git fetch --quiet origin "$BRANCH"
current="$(git rev-parse HEAD)"
target="$(git rev-parse "origin/$BRANCH")"
if [ "$current" = "$target" ]; then
  exit 0
fi
if ! git merge-base --is-ancestor "$current" "$target"; then
  log "origin/$BRANCH ($target) is not a descendant of the deployed commit ($current); refusing"
  exit 1
fi

ci_conclusion() { # prints the conclusion of the newest run of $WORKFLOW for commit $1
  local sha="$1" url slug
  url="$(git remote get-url origin)"
  slug="$(printf '%s' "$url" | sed -E 's#^(https://github\.com/|git@github\.com:)##; s#\.git$##')"
  local auth=()
  if [ -n "${DEPLOY_GITHUB_TOKEN:-}" ]; then
    auth=(-H "Authorization: Bearer $DEPLOY_GITHUB_TOKEN")
  fi
  curl -fsS --max-time 30 -H "Accept: application/vnd.github+json" "${auth[@]}" \
    "https://api.github.com/repos/$slug/actions/runs?head_sha=$sha&per_page=50" |
    WORKFLOW="$WORKFLOW" python3 -I -c '
import json, os, sys
runs = [r for r in json.load(sys.stdin).get("workflow_runs", []) if r.get("name") == os.environ["WORKFLOW"]]
runs.sort(key=lambda r: r.get("run_started_at") or "", reverse=True)
print((runs[0].get("conclusion") or runs[0].get("status")) if runs else "none")
'
}

if [ "$REQUIRE_CI" = "1" ]; then
  conclusion="$(ci_conclusion "$target" || echo "unknown")"
  if [ "$conclusion" != "success" ]; then
    log "commit ${target:0:7} has CI '$conclusion'; waiting for success"
    exit 0
  fi
fi

log "deploying ${current:0:7} -> ${target:0:7}"

if [ "${DEPLOY_SKIP_BACKUP:-0}" != "1" ] && [ -x scripts/ops/backup.sh ]; then
  if COMPOSE_PROJECT_NAME="$PROJECT" bash scripts/ops/backup.sh; then
    log "backup taken"
  else
    log "backup failed; refusing to deploy"
    exit 1
  fi
fi

bring_up() {
  docker compose -p "$PROJECT" up -d --build --wait web
}

healthy() {
  local url code
  for url in $HEALTH_URLS; do
    code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$url" || true)"
    if [ "$code" != "200" ]; then
      log "health check failed: $url -> $code"
      return 1
    fi
  done
}

git merge --quiet --ff-only "$target"

if bring_up && healthy; then
  log "deployed ${target:0:7}"
  exit 0
fi

log "deploy of ${target:0:7} failed; rolling back to ${current:0:7}"
git switch --quiet --force-create "$BRANCH" "$current"
if bring_up && healthy; then
  log "rolled back to ${current:0:7}"
else
  log "rollback did not come up healthy; manual attention needed"
fi
exit 1
