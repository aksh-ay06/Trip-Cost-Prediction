resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "mlops-docker"
  format        = "DOCKER"

  depends_on = [google_project_service.apis["artifactregistry.googleapis.com"]]
}
