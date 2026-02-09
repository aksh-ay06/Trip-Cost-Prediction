"""Load parquet data from GCS into BigQuery taxi_raw dataset."""

from google.cloud import bigquery

from src.config import DATA_LAKE_BUCKET, PROJECT_ID

BUCKET_NAME = DATA_LAKE_BUCKET
GCS_URI = f"gs://{BUCKET_NAME}/raw/yellow_trips.parquet"
TABLE_ID = f"{PROJECT_ID}.taxi_raw.yellow_trips"


def load():
    client = bigquery.Client(project=PROJECT_ID)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    print(f"Loading {GCS_URI} → {TABLE_ID}...")
    load_job = client.load_table_from_uri(GCS_URI, TABLE_ID, job_config=job_config)
    load_job.result(timeout=300)

    table = client.get_table(TABLE_ID)
    if table.num_rows == 0:
        raise RuntimeError(f"Load succeeded but {TABLE_ID} has 0 rows")
    print(f"Loaded {table.num_rows} rows into {TABLE_ID}")


if __name__ == "__main__":
    load()
