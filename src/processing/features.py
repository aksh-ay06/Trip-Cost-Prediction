"""Feature engineering for taxi trip data using BigQuery SQL."""

from google.cloud import bigquery

from src.config import PROJECT_ID

INPUT_TABLE = f"{PROJECT_ID}.taxi_raw.yellow_trips"
OUTPUT_TABLE = f"{PROJECT_ID}.taxi_staging.yellow_trips_processed"

FEATURE_QUERY = f"""
CREATE OR REPLACE TABLE `{OUTPUT_TABLE}` AS
SELECT
    pickup_datetime,
    dropoff_datetime,
    passenger_count,
    trip_distance,
    fare_amount,
    tip_amount,
    tolls_amount,
    total_amount,
    payment_type,
    TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime, MINUTE) AS trip_duration_min,
    EXTRACT(HOUR FROM pickup_datetime) AS pickup_hour,
    EXTRACT(DAYOFWEEK FROM pickup_datetime) AS pickup_dayofweek,
    CASE WHEN EXTRACT(DAYOFWEEK FROM pickup_datetime) IN (1, 7) THEN 1 ELSE 0 END AS is_weekend
FROM `{INPUT_TABLE}`
WHERE TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime, MINUTE) BETWEEN 1 AND 180
  AND fare_amount BETWEEN 2.5 AND 500
  AND trip_distance BETWEEN 0.1 AND 100
"""


def main():
    client = bigquery.Client(project=PROJECT_ID)

    print(f"Running feature engineering: {INPUT_TABLE} -> {OUTPUT_TABLE}...")
    job = client.query(FEATURE_QUERY)
    job.result(timeout=300)

    table = client.get_table(OUTPUT_TABLE)
    print(f"Created {OUTPUT_TABLE} with {table.num_rows} rows")


if __name__ == "__main__":
    main()
