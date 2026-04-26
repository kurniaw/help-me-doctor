terraform {
  required_version = ">= 1.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    # Set via -backend-config or terraform.tfvars
    # bucket = "your-project-tf-state"
    # prefix = "hmd/terraform.tfstate"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required GCP APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "aiplatform.googleapis.com",
    "artifactregistry.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com",
  ])
  service            = each.value
  disable_on_destroy = false
}

module "artifact_registry" {
  source     = "./modules/artifact_registry"
  project_id = var.project_id
  region     = var.region
  depends_on = [google_project_service.apis]
}

module "storage" {
  source     = "./modules/storage"
  project_id = var.project_id
  region     = var.region
  depends_on = [google_project_service.apis]
}

module "vertex_ai" {
  source     = "./modules/vertex_ai"
  project_id = var.project_id
  region     = var.region
  depends_on = [google_project_service.apis]
}

module "cloud_run" {
  source                   = "./modules/cloud_run"
  project_id               = var.project_id
  region                   = var.region
  backend_image            = var.backend_image
  frontend_image           = var.frontend_image
  mongo_uri_secret_id      = var.mongo_uri_secret_id
  jwt_secret_id            = var.jwt_secret_id
  vertex_index_id          = module.vertex_ai.index_id
  vertex_endpoint_id       = module.vertex_ai.endpoint_id
  registry_url             = module.artifact_registry.registry_url
  depends_on               = [google_project_service.apis, module.artifact_registry]
}
