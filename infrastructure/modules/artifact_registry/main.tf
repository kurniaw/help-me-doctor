resource "google_artifact_registry_repository" "hmd_images" {
  project       = var.project_id
  location      = var.region
  repository_id = "hmd-images"
  description   = "Help Me Doctor Docker images"
  format        = "DOCKER"
}
