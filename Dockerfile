# syntax=docker/dockerfile:1

# ---- build: resolve the locked dependencies and install the package into /app/.venv ----
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS build

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies first so this layer is cached until uv.lock changes.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

COPY README.md LICENSE NOTICE ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

# ---- runtime: slim Python with only the virtualenv and the content ----
FROM python:3.15-slim-bookworm AS runtime

RUN groupadd --system --gid 10001 rc \
    && useradd --system --uid 10001 --gid rc --home-dir /app --shell /usr/sbin/nologin rc

WORKDIR /app
COPY --from=build --chown=rc:rc /app/.venv /app/.venv
COPY --chown=rc:rc curriculum ./curriculum
COPY --chown=rc:rc LICENSE NOTICE ./

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RC_DATA_DIR=/data

RUN mkdir -p /data && chown rc:rc /data
VOLUME ["/data"]

USER rc

ENTRYPOINT ["rc"]
CMD ["--help"]

# ---- build-api: the same project plus the api and postgres extras ----
FROM build AS build-api

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable --extra api --extra postgres

# ---- api: server mode (P2-5, docs/architecture/operations.md) ----
# Build with: docker build --target api -t robotics-curriculum-api:local .
FROM python:3.15-slim-bookworm AS api

RUN groupadd --system --gid 10001 rc \
    && useradd --system --uid 10001 --gid rc --home-dir /app --shell /usr/sbin/nologin rc

WORKDIR /app
COPY --from=build-api --chown=rc:rc /app/.venv /app/.venv
COPY --chown=rc:rc curriculum ./curriculum
COPY --chown=rc:rc LICENSE NOTICE alembic.ini ./

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RC_DATA_DIR=/data \
    RC_CURRICULUM_DIR=/app/curriculum \
    RC_AUTH_MODE=server \
    RC_API_HOST=0.0.0.0 \
    RC_API_PORT=8000

RUN mkdir -p /data && chown rc:rc /data
VOLUME ["/data"]
EXPOSE 8000

USER rc

# Server mode by default: every /api/v1 call needs a session or token (server review SRV-01).
# Local mode on 0.0.0.0 is refused by `rc api serve` unless RC_API_ALLOW_REMOTE_LOCAL=1.
# No curl or wget in the image, so the health check uses python.
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
    CMD ["python", "-c", "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/readyz', timeout=3).status == 200 else 1)"]

# `rc api serve` reads the RC_* variables above; the migrate service overrides the entrypoint
# with alembic.
ENTRYPOINT ["rc"]
CMD ["api", "serve"]

# ---- web-build: the Next.js frontend, compiled to a self-contained server bundle ----
# web/next.config.ts turns on `output: 'standalone'` when NEXT_OUTPUT=standalone, which puts the
# server, its package.json and only the node_modules it imports into .next/standalone;
# .next/static ships beside it.
FROM node:22-bookworm-slim AS web-build

ENV NEXT_TELEMETRY_DISABLED=1 \
    NEXT_OUTPUT=standalone

WORKDIR /app/web

# Dependencies first so this layer is cached until the lockfile changes.
COPY web/package.json web/package-lock.json ./
RUN npm ci

COPY web ./
RUN npm run build

# ---- web: server mode frontend (P2-5, docs/architecture/operations.md) ----
# Build with: docker build --target web -t robotics-curriculum-web:local .
FROM node:22-bookworm-slim AS web

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

WORKDIR /app

# The standalone bundle carries its own node_modules; .next/static and public/ do not travel
# with it. `web/public` does not exist yet, so nothing is copied for it.
COPY --from=web-build --chown=node:node /app/web/.next/standalone ./
COPY --from=web-build --chown=node:node /app/web/.next/static ./.next/static

EXPOSE 3000

# node:* images ship an unprivileged `node` user (uid 1000).
USER node

# No curl or wget in the image; node's own fetch is the probe. The api it talks to is set by
# RC_API_BASE_URL (compose points it at http://api:8000).
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=15s \
    CMD node -e "fetch('http://127.0.0.1:'+(process.env.PORT||3000)+'/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

CMD ["node", "server.js"]
