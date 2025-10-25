FROM node:25

COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /bin/

RUN npm i -g @bitwarden/cli@2025.10.0 semver@7.7.3

WORKDIR /app

ENV UV_MANAGED_PYTHON=true \
    UV_LOCKED=true \
    UV_PYTHON=3.13.7 \
    PATH=/app/.venv/bin:/root/.local/bin:$PATH

RUN uv python install

COPY . .

RUN uv sync --locked --no-extra dev

RUN bitwarden-exporter --help
