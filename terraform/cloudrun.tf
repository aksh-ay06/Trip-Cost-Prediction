resource "google_cloud_run_v2_service" "taxi_prediction" {
  name     = "taxi-prediction-api"
  location = var.region

  depends_on = [google_project_service.apis["run.googleapis.com"]]

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/taxi-prediction-api:latest"

      ports {
        container_port = 8080
      }

      env {
        name  = "GCP_PROJECT"
        value = var.project_id
      }

      env {
        name  = "ML_ARTIFACTS_BUCKET"
        value = google_storage_bucket.ml_artifacts.name
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.taxi_prediction.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service" "taxi_frontend" {
  name     = "taxi-frontend"
  location = var.region

  depends_on = [google_project_service.apis["run.googleapis.com"]]

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/taxi-frontend:latest"

      ports {
        container_port = 8501
      }

      env {
        name  = "API_URL"
        value = google_cloud_run_v2_service.taxi_prediction.uri
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "frontend_public_access" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.taxi_frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
