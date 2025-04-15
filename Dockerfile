# Install uv
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    UV_VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable

# Copy the project into the intermediate image
COPY . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable

FROM python:3.12-slim

ENV UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

# Replace shell with bash so we can source files
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN echo "export LS_OPTIONS='--color=auto'" >>~/.bashrc && \
    echo "eval "\`dircolors\`"" >>~/.bashrc && \
    echo "alias ls='ls \$LS_OPTIONS'" >>~/.bashrc && \
    echo "alias ll='ls \$LS_OPTIONS -l'" >>~/.bashrc && \
    echo "alias l='ls \$LS_OPTIONS -lA'" >>~/.bashrc

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    libgdal-dev \
    libmagic-dev

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/ /app/
WORKDIR /app
RUN STATICFILES_MANIFEST=1 ./manage.py collectstatic --no-input
# Run the application
CMD ["gunicorn", "-w", "4", "-b", ":8000", "geovault.wsgi"]
