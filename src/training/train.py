"""Train XGBoost model for taxi fare prediction."""

import json
import os
import tempfile

import numpy as np
import pandas as pd
import xgboost as xgb
from google.cloud import bigquery, storage
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from src.config import FEATURE_TABLE, FEATURES, ML_ARTIFACTS_BUCKET, PROJECT_ID, TARGET

ARTIFACTS_BUCKET = ML_ARTIFACTS_BUCKET
MODEL_PATH = "models/fare_model.xgb"
METRICS_PATH = "models/metrics.json"


def load_data():
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
    SELECT {', '.join(FEATURES)}, {TARGET}
    FROM `{FEATURE_TABLE}`
    """
    return client.query(query).to_dataframe()


def train():
    print("Loading data...")
    df = load_data()
    print(f"Dataset: {len(df)} rows")

    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training XGBoost model...")
    model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=20)

    y_pred = model.predict(X_test)
    metrics = {
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "r2": float(r2_score(y_test, y_pred)),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
    print(f"Metrics: {metrics}")

    # Upload model and metrics to GCS
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(ARTIFACTS_BUCKET)

    with tempfile.TemporaryDirectory() as tmpdir:
        model_file = os.path.join(tmpdir, "fare_model.xgb")
        model.save_model(model_file)
        bucket.blob(MODEL_PATH).upload_from_filename(model_file)
        print(f"Model uploaded to gs://{ARTIFACTS_BUCKET}/{MODEL_PATH}")

        metrics_file = os.path.join(tmpdir, "metrics.json")
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)
        bucket.blob(METRICS_PATH).upload_from_filename(metrics_file)
        print(f"Metrics uploaded to gs://{ARTIFACTS_BUCKET}/{METRICS_PATH}")


if __name__ == "__main__":
    train()
