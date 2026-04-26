resource "google_storage_bucket" "hmd_data" {
  project                     = var.project_id
  name                        = "${var.project_id}-hmd-data"
  location                    = "ASIA"
  uniform_bucket_level_access = true
  force_destroy               = true

  lifecycle_rule {
    condition { age = 365 }
    action { type = "Delete" }
  }
}
