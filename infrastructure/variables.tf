variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for all resources"
  type        = string
  default     = "asia-southeast1"
}

variable "backend_image" {
  description = "Full Docker image path for backend (e.g. asia-southeast1-docker.pkg.dev/project/hmd-images/backend:sha)"
  type        = string
  default     = ""
}

variable "frontend_image" {
  description = "Full Docker image path for frontend"
  type        = string
  default     = ""
}

variable "mongo_uri_secret_id" {
  description = "Secret Manager secret ID for MongoDB URI"
  type        = string
  default     = "hmd-mongo-uri"
}

variable "jwt_secret_id" {
  description = "Secret Manager secret ID for JWT secret"
  type        = string
  default     = "hmd-jwt-secret"
}
