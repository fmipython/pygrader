FROM ghcr.io/astral-sh/uv:python3.13-slim

RUN mkdir /app
WORKDIR /app

# COPY uv.lock .
# COPY pyproject.toml .
# RUN uv sync --locked --no-install-project --no-dev

COPY . .

RUN uv sync --locked --no-dev

VOLUME ["/project"]

COPY /Users/lyubolp/homeworks-2025/homework2/pygrader_config_public_local.json /app/config.json
COPY /Users/lyubolp/homeworks-2025/homework2/pygrader_structure.json /app/pygrader_structure.json

ENTRYPOINT ["uv", "run", "--no-dev", "pygrader.py", "--config", "https://api.github.com/repos/fmipython/PythonCourse2025/contents/homeworks/homework1/config/pygrader_config_public.json", "/project"]
