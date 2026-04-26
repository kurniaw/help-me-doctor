output "index_id" {
  value = google_vertex_ai_index.medical_conditions.id
}

output "endpoint_id" {
  value = google_vertex_ai_index_endpoint.medical_endpoint.id
}
