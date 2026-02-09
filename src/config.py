"""Centralized configuration for the MLOps pipeline."""

import os

PROJECT_ID = os.environ["GCP_PROJECT"]
DATA_LAKE_BUCKET = os.getenv("DATA_LAKE_BUCKET", f"{PROJECT_ID}-data-lake")
ML_ARTIFACTS_BUCKET = os.getenv("ML_ARTIFACTS_BUCKET", f"{PROJECT_ID}-ml-artifacts")
