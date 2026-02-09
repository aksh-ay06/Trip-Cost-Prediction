FROM python:3.10-slim

WORKDIR /app

COPY docker/serving/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/serving/ ./serving/

EXPOSE 8080

CMD ["uvicorn", "serving.app:app", "--host", "0.0.0.0", "--port", "8080"]
