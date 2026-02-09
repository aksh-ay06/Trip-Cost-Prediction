"""Standalone model evaluation."""

import tempfile

import numpy as np
import xgboost as xgb
from google.cloud import bigquery, storage
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from src.config import ML_ARTIFACTS_BUCKET, PROJECT_ID

ARTIFACTS_BUCKET = ML_ARTIFACTS_BUCKET
MODEL_PATH = "models/fare_model.xgb"

FEATURES = [
    "pickup_hour",
    "pickup_dayofweek",
    "is_weekend",
    "passenger_count",
    "trip_distance",
]
TARGET = "fare_amount"


def evaluate():
    # Download model
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(ARTIFACTS_BUCKET)

    with tempfile.NamedTemporaryFile(suffix=".xgb") as f:
        bucket.blob(MODEL_PATH).download_to_filename(f.name)
        model = xgb.XGBRegressor()
        model.load_model(f.name)

    # Load data and reproduce the same train/test split used during training
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
    SELECT {', '.join(FEATURES)}, {TARGET}
    FROM `{PROJECT_ID}.taxi_prod.fct_taxi_features`
    """
    df = client.query(query).to_dataframe()

    X = df[FEATURES]
    y = df[TARGET]
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    y_pred = model.predict(X_test)

    print(f"Evaluating on held-out test set ({len(X_test)} rows)")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")
    print(f"MAE:  {mean_absolute_error(y_test, y_pred):.4f}")
    print(f"R2:   {r2_score(y_test, y_pred):.4f}")


if __name__ == "__main__":
    evaluate()
