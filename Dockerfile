FROM python:3.12-alpine

RUN mkdir /app
WORKDIR /app

COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt

COPY . .

VOLUME ["/project"]

ENTRYPOINT ["python", "pygrader.py", "/project"]
