"""Model loading and caching from GCS."""

import os
import tempfile

import xgboost as xgb
from google.cloud import storage

PROJECT_ID = os.environ["GCP_PROJECT"]
ARTIFACTS_BUCKET = os.getenv("ML_ARTIFACTS_BUCKET", f"{PROJECT_ID}-ml-artifacts")
MODEL_PATH = "models/fare_model.xgb"

_model = None


def get_model() -> xgb.XGBRegressor:
    global _model
    if _model is None:
        _model = _load_model()
    return _model


def _load_model() -> xgb.XGBRegressor:
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(ARTIFACTS_BUCKET)

    with tempfile.NamedTemporaryFile(suffix=".xgb", delete=False) as f:
        bucket.blob(MODEL_PATH).download_to_filename(f.name)
        model = xgb.XGBRegressor()
        model.load_model(f.name)

    os.unlink(f.name)
    return model
