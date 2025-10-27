FROM ghcr.io/astral-sh/uv:python3.13-alpine

RUN mkdir /app
WORKDIR /app

# COPY uv.lock .
# COPY pyproject.toml .
# RUN uv sync --locked --no-install-project --no-dev

COPY . .

RUN uv sync --locked --no-dev

VOLUME ["/project"]

ENTRYPOINT ["uv", "run", "--no-dev", "pygrader.py", "--config", "https://api.github.com/repos/fmipython/homeworks-2025/contents/homework1/pygrader_config_public.json", "/project"]
