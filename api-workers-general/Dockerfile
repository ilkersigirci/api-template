#
# Stage: builder
#
ARG PYTHON_VERSION=3.13
FROM ghcr.io/astral-sh/uv:0.10.0-python${PYTHON_VERSION}-trixie-slim AS builder

ENV \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,from=api-shared,target=../api-shared \
    uv sync --locked --no-install-project --no-default-groups

COPY --from=api-shared . /app/../api-shared
COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    --mount=type=bind,from=api-shared,target=../api-shared \
    uv sync --locked --no-default-groups

#
# Stage: development
#
FROM builder AS development

ENV HATCHET_WORKER_NAME=general-worker

CMD ["uv", "run", "--module", "worker.main"]

#
# Stage: production
#
ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim-trixie AS production

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PATH="/app/.venv/bin:$PATH" \
    HATCHET_WORKER_NAME=general-worker

RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder --chown=nonroot:nonroot /api-shared /api-shared
COPY --from=builder --chown=nonroot:nonroot /app /app

USER nonroot
WORKDIR /app

CMD ["python", "-m", "worker.main"]
