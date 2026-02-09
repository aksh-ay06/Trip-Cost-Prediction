output "data_lake_bucket" {
  value = google_storage_bucket.data_lake.name
}

output "ml_artifacts_bucket" {
  value = google_storage_bucket.ml_artifacts.name
}

output "artifact_registry_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}"
}

output "cloud_run_url" {
  value = google_cloud_run_v2_service.taxi_prediction.uri
}

output "frontend_url" {
  value = google_cloud_run_v2_service.taxi_frontend.uri
}
