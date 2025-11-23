FROM python:3.12-slim

RUN mkdir /app
WORKDIR /app

COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt

COPY . .

COPY /home/lyubolp/homeworks-2025/homework2/pygrader_config_public_local.json /app/config.json
COPY /home/lyubolp/homeworks-2025/homework2/pygrader_structure.json /app/pygrader_structure.json

VOLUME ["/project"]

ENTRYPOINT ["python", "pygrader.py", "--config", "/app/config.json", "/project"]
