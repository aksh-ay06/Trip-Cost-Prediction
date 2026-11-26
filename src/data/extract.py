"""Extract NYC taxi data from BigQuery public datasets to GCS as parquet."""

import os
import sys

from google.api_core.retry import Retry
from google.cloud import bigquery, storage

from src.config import DATA_LAKE_BUCKET, PROJECT_ID

BUCKET_NAME = DATA_LAKE_BUCKET
GCS_PATH = "raw/yellow_trips.parquet"

# Reproducible sample: a fixed pickup date range plus a hash-based sample, so
# every run extracts the same rows. (LIMIT without ORDER BY returned an
# arbitrary, different subset each time.) The 2020 table also contains stray
# out-of-range timestamps, which the date filter removes.
START_DATE = os.getenv("EXTRACT_START_DATE", "2020-01-01")  # inclusive
END_DATE = os.getenv("EXTRACT_END_DATE", "2021-01-01")  # exclusive
# Rows kept per 1,000. 2020 has roughly 24M yellow trips, so 20 gives about 500k.
SAMPLE_PER_MILLE = int(os.getenv("EXTRACT_SAMPLE_PER_MILLE", "20"))
ROW_LIMIT = int(os.getenv("EXTRACT_ROW_LIMIT", "500000"))  # safety cap

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
WHERE pickup_datetime >= TIMESTAMP('{START_DATE}')
  AND pickup_datetime < TIMESTAMP('{END_DATE}')
  AND fare_amount > 0
  AND trip_distance > 0
  AND passenger_count > 0
  AND MOD(ABS(FARM_FINGERPRINT(FORMAT('%t|%t|%t|%t|%t',
        pickup_datetime, dropoff_datetime, trip_distance, fare_amount, total_amount))), 1000)
      < {SAMPLE_PER_MILLE}
ORDER BY pickup_datetime, dropoff_datetime, trip_distance, fare_amount, total_amount
LIMIT {ROW_LIMIT}
"""


def extract():
    client = bigquery.Client(project=PROJECT_ID)

    print(f"Extracting {START_DATE} to {END_DATE}, sample {SAMPLE_PER_MILLE}/1000, cap {ROW_LIMIT} rows...")
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
