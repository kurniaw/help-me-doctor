locals {
  backend_image  = var.backend_image != "" ? var.backend_image : "gcr.io/cloudrun/hello"
  frontend_image = var.frontend_image != "" ? var.frontend_image : "gcr.io/cloudrun/hello"
}

# Dedicated service account for Cloud Run services
resource "google_service_account" "cloud_run" {
  project      = var.project_id
  account_id   = "hmd-cloud-run"
  display_name = "HelpMeDoctor Cloud Run SA"
}

# Allow Cloud Run SA to access secrets
resource "google_project_iam_member" "cloud_run_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Cloud Run — Backend
resource "google_cloud_run_v2_service" "backend" {
  project  = var.project_id
  location = var.region
  name     = "hmd-backend"

  template {
    service_account = google_service_account.cloud_run.email

    containers {
      image = local.backend_image

      resources {
        cpu_idle = true
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "MONGO_DB_NAME"
        value = "helpmedoctor"
      }
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_REGION"
        value = var.region
      }
      env {
        name  = "VERTEX_INDEX_ID"
        value = var.vertex_index_id
      }
      env {
        name  = "VERTEX_INDEX_ENDPOINT_ID"
        value = var.vertex_endpoint_id
      }

      env {
        name = "MONGO_URI"
        value_source {
          secret_key_ref {
            secret  = var.mongo_uri_secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "JWT_SECRET"
        value_source {
          secret_key_ref {
            secret  = var.jwt_secret_id
            version = "latest"
          }
        }
      }

      ports {
        container_port = 8000
      }

      startup_probe {
        http_get {
          path = "/health"
        }
        initial_delay_seconds = 5
        period_seconds        = 10
        timeout_seconds       = 5
        failure_threshold     = 10
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }

    timeout = "300s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Cloud Run — Frontend
resource "google_cloud_run_v2_service" "frontend" {
  project  = var.project_id
  location = var.region
  name     = "hmd-frontend"

  template {
    service_account = google_service_account.cloud_run.email

    containers {
      image = local.frontend_image

      resources {
        cpu_idle = true
        limits = {
          cpu    = "0.5"
          memory = "256Mi"
        }
      }

      env {
        name  = "NUXT_PUBLIC_API_BASE"
        value = google_cloud_run_v2_service.backend.uri
      }

      ports {
        container_port = 3000
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_cloud_run_v2_service.backend]
}

# Public access — Backend
resource "google_cloud_run_v2_service_iam_member" "backend_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Public access — Frontend
resource "google_cloud_run_v2_service_iam_member" "frontend_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
