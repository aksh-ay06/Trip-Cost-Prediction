FROM python:3.10-slim

WORKDIR /app

COPY docker/pipeline/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY src/ ./src/
COPY dbt/ ./dbt/
