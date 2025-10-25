FROM python:3.12-alpine

RUN mkdir /app
WORKDIR /app

COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt

COPY . .

VOLUME ["/project"]

ENTRYPOINT ["python", "pygrader.py", "--config", "https://api.github.com/repos/fmipython/homeworks-2025/contents/homework1/pygrader_config_public.json", "/project"]
