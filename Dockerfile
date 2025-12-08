FROM python:3.12-slim

RUN mkdir /app
RUN mkdir /assets
WORKDIR /app

COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt

COPY . .

COPY hw2-config/assets /assets

VOLUME ["/project"]

ENTRYPOINT ["python", "pygrader.py", "--config", "/app/hw3-config/pygrader_config_local.json", "/project"]
