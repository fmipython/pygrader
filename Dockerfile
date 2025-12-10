FROM python:3.12-slim

RUN mkdir /app
RUN mkdir /assets
WORKDIR /app

COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt

COPY . .

VOLUME ["/project"]

ENTRYPOINT ["python", "pygrader.py", "--config", "https://api.github.com/repos/fmipython/PythonCourse2025/contents/homeworks/homework3/pygrader_config_public_web.json", "/project"]
