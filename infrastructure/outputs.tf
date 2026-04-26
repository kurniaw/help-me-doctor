output "backend_url" {
  description = "Cloud Run backend service URL"
  value       = module.cloud_run.backend_url
}

output "frontend_url" {
  description = "Cloud Run frontend service URL"
  value       = module.cloud_run.frontend_url
}

output "artifact_registry_url" {
  description = "Artifact Registry Docker repository URL"
  value       = module.artifact_registry.registry_url
}

output "vertex_index_id" {
  description = "Vertex AI Vector Search index ID"
  value       = module.vertex_ai.index_id
}

output "vertex_endpoint_id" {
  description = "Vertex AI Vector Search endpoint ID"
  value       = module.vertex_ai.endpoint_id
}

output "data_bucket_name" {
  description = "GCS bucket for embeddings and data"
  value       = module.storage.bucket_name
}
