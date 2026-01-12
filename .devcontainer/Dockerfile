FROM python:3.13-slim-bookworm AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_PATH="/app" \
    UV_VERSION="0.6.14"

ENV VIRTUAL_ENV="$APP_PATH/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR $APP_PATH

FROM python-base AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc git curl \
    && rm -rf /var/lib/apt/lists/

RUN pip install --no-cache-dir "uv==$UV_VERSION"

COPY ./pyproject.toml ./uv.lock ./
RUN uv venv -p 3.13 \
    && uv sync --all-extras --no-install-project
COPY ./src ./src
RUN uv sync --all-extras --no-editable

FROM python-base AS devcontainer

ENV PYTHONPATH="$APP_PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        git \
        procps \
        vim \
        postgresql-client \
        build-essential \
        sudo \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "uv==$UV_VERSION"

COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

RUN groupadd -r vscode || true \
    && useradd -r -m -g vscode -s /bin/bash vscode || true \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && chown -R vscode:vscode $APP_PATH \
    && chmod -R 755 $APP_PATH

USER vscode

WORKDIR $APP_PATH
