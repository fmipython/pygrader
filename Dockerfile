FROM ghcr.io/astral-sh/uv:python3.13-slim

RUN mkdir /app
RUN mkdir /assets
WORKDIR /app

# COPY uv.lock .
# COPY pyproject.toml .
# RUN uv sync --locked --no-install-project --no-dev

COPY . .

RUN uv sync --locked --no-dev

VOLUME ["/project"]

ENTRYPOINT ["uv", "run", "--no-dev", "pygrader.py", "--config", "https://api.github.com/repos/fmipython/PythonCourse2025/contents/homeworks/homework3/pygrader_config_public_web.json", "/project"]

