"""Centralized configuration for the MLOps pipeline."""

import os

PROJECT_ID = os.environ["GCP_PROJECT"]
DATA_LAKE_BUCKET = os.getenv("DATA_LAKE_BUCKET", f"{PROJECT_ID}-data-lake")
ML_ARTIFACTS_BUCKET = os.getenv("ML_ARTIFACTS_BUCKET", f"{PROJECT_ID}-ml-artifacts")

# ML-ready feature table built by dbt (dbt/models/marts/fct_taxi_features.sql).
# Training and evaluation must both read this table.
FEATURE_TABLE = f"{PROJECT_ID}.taxi_prod.fct_taxi_features"

FEATURES = [
    "pickup_hour",
    "pickup_dayofweek",
    "is_weekend",
    "passenger_count",
    "trip_distance",
]
TARGET = "fare_amount"
