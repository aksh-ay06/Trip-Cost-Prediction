# NYC Taxi Fare Prediction — MLOps Pipeline

End-to-end MLOps project that predicts NYC yellow taxi fares. Pulls trip data from BigQuery public datasets, engineers features with SQL and dbt, trains an XGBoost model, and serves predictions through a FastAPI backend + Streamlit frontend — both running on Cloud Run.

## Architecture

```
BigQuery Public Data
  │
  ▼
extract.py ──► GCS (parquet)
  │
  ▼
load_to_bq.py ──► BigQuery taxi_raw
  │
  ▼
features.py ──► BigQuery taxi_staging.yellow_trips_processed
  │
  ▼
dbt ──► taxi_staging.stg_taxi_trips ──► taxi_prod.fct_taxi_features
  │
  ▼
train.py ──► GCS (xgboost model artifact)
  │
  ▼
Cloud Run ──► FastAPI /predict    ◄── Streamlit frontend (also on Cloud Run)
```

Orchestration is handled by Kestra (Docker task runner). All GCP infrastructure is managed with Terraform.

## Stack

- **Data warehouse**: BigQuery
- **Object storage**: GCS
- **Feature engineering**: BigQuery SQL + dbt
- **Model**: XGBoost
- **Serving**: FastAPI on Cloud Run
- **Frontend**: Streamlit on Cloud Run
- **Orchestration**: Kestra
- **Infra**: Terraform
- **Containers**: Docker

## Prerequisites

- GCP project with billing enabled
- Service account key at `keys/my_keys.json` with BigQuery, GCS, Cloud Run, and Artifact Registry permissions
- Python 3.10+, [uv](https://github.com/astral-sh/uv), Docker, Terraform, gcloud CLI

## Getting started

### 1. Infrastructure

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# fill in project_id and region
terraform init
terraform apply
```

This creates: GCS buckets, BigQuery datasets, Artifact Registry repo, Cloud Run services, IAM bindings.

### 2. Install dependencies

```bash
uv sync
```

### 3. Run the pipeline

```bash
export GOOGLE_APPLICATION_CREDENTIALS=keys/my_keys.json
export GCP_PROJECT=<your-project-id>

uv run python -m src.data.extract
uv run python -m src.data.load_to_bq
uv run python -m src.processing.features
cd dbt && dbt deps && dbt run && cd ..
uv run python -m src.training.train
```

### 4. Build and deploy

```bash
# prediction API
docker build -f docker/serving/Dockerfile -t <ARTIFACT_REGISTRY>/taxi-prediction-api:latest .
docker push <ARTIFACT_REGISTRY>/taxi-prediction-api:latest

# frontend
docker build -f docker/frontend/Dockerfile -t <ARTIFACT_REGISTRY>/taxi-frontend:latest .
docker push <ARTIFACT_REGISTRY>/taxi-frontend:latest

# apply updated images
cd terraform && terraform apply
```

### 5. Test it

```bash
curl -X POST <CLOUD_RUN_URL>/predict \
  -H "Content-Type: application/json" \
  -d '{"pickup_datetime":"2026-03-04T14:30:00","passenger_count":2,"trip_distance":3.5}'
```

`pickup_datetime` is treated as NYC local time unless it includes a UTC offset. The API derives the hour, day of week (BigQuery convention: 1 = Sunday, 7 = Saturday), and weekend flag from it, using the same rules as the training SQL.

### 6. Kestra (orchestration)

```bash
cp .env.example .env
# fill in GCP_PROJECT, KEYS_DIR (absolute path to your keys folder), and the Kestra/Postgres credentials
docker compose up -d
# UI at http://localhost:8080
```

Kestra runs each pipeline step as a Docker container. The flow definition lives in `kestra/flows/taxi_pipeline.yml`.

## Project layout

```text
src/
  config.py              # GCP project/bucket config
  data/
    extract.py           # pull from BQ public dataset → GCS parquet
    load_to_bq.py        # GCS parquet → BQ taxi_raw
  processing/
    features.py          # feature engineering (BigQuery SQL)
  training/
    train.py             # XGBoost training
    evaluate.py          # model evaluation
  serving/
    app.py               # FastAPI endpoints
    model.py             # model loading from GCS
    schemas.py           # request/response schemas
    features.py          # request -> model features (matches training SQL)
  frontend/
    app.py               # Streamlit UI

dbt/
  models/
    staging/             # stg_taxi_trips (view)
    marts/               # fct_taxi_features (table)

terraform/               # all GCP resources
kestra/flows/            # pipeline orchestration
docker/                  # Dockerfiles for serving, frontend, pipeline
scripts/                 # deploy + infra setup helpers
```
