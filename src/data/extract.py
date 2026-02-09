"""Extract NYC taxi data from BigQuery public datasets to GCS as parquet."""

import sys

from google.api_core.retry import Retry
from google.cloud import bigquery, storage

from src.config import DATA_LAKE_BUCKET, PROJECT_ID

BUCKET_NAME = DATA_LAKE_BUCKET
GCS_PATH = "raw/yellow_trips.parquet"
ROW_LIMIT = 500_000

EXTRACT_QUERY = f"""
SELECT
    pickup_datetime,
    dropoff_datetime,
    passenger_count,
    trip_distance,
    fare_amount,
    tip_amount,
    tolls_amount,
    total_amount,
    payment_type
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2020`
WHERE fare_amount > 0
  AND trip_distance > 0
  AND passenger_count > 0
LIMIT {ROW_LIMIT}
"""


def extract():
    client = bigquery.Client(project=PROJECT_ID)

    print(f"Running extraction query ({ROW_LIMIT} rows)...")
    df = client.query(EXTRACT_QUERY).to_dataframe()
    print(f"Extracted {len(df)} rows")

    if df.empty:
        print("ERROR: Query returned no rows, aborting upload.")
        sys.exit(1)

    local_path = "/tmp/yellow_trips.parquet"
    df.to_parquet(local_path, index=False)

    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(GCS_PATH)
    blob.upload_from_filename(local_path, retry=Retry(deadline=120))
    print(f"Uploaded to gs://{BUCKET_NAME}/{GCS_PATH}")


if __name__ == "__main__":
    extract()
