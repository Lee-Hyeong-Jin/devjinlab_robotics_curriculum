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
FROM python:3.12-slim-bookworm AS runtime

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
