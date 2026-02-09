resource "google_bigquery_dataset" "taxi_raw" {
  dataset_id                 = "taxi_raw"
  location                   = var.region
  delete_contents_on_destroy = true

  depends_on = [google_project_service.apis["bigquery.googleapis.com"]]
}

resource "google_bigquery_dataset" "taxi_staging" {
  dataset_id                 = "taxi_staging"
  location                   = var.region
  delete_contents_on_destroy = true

  depends_on = [google_project_service.apis["bigquery.googleapis.com"]]
}

resource "google_bigquery_dataset" "taxi_prod" {
  dataset_id                 = "taxi_prod"
  location                   = var.region
  delete_contents_on_destroy = true

  depends_on = [google_project_service.apis["bigquery.googleapis.com"]]
}
