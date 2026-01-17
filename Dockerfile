FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

RUN mkdir /app
RUN mkdir /assets
WORKDIR /app

COPY . .

RUN uv sync --locked --no-dev

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

VOLUME ["/project", "/tmp/project_bind"]

ENTRYPOINT ["/app/entrypoint.sh"]

