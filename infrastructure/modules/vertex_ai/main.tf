resource "google_vertex_ai_index" "medical_conditions" {
  project      = var.project_id
  region       = var.region
  display_name = "hmd-medical-conditions"
  description  = "Medical conditions embeddings for semantic symptom search"

  metadata {
    contents_delta_uri = "gs://${var.project_id}-hmd-data/embeddings/"
    config {
      dimensions                  = 768
      approximate_neighbors_count = 10
      distance_measure_type       = "DOT_PRODUCT_DISTANCE"
      algorithm_config {
        tree_ah_config {
          leaf_node_embedding_count    = 500
          leaf_nodes_to_search_percent = 7
        }
      }
    }
  }
}

resource "google_vertex_ai_index_endpoint" "medical_endpoint" {
  project      = var.project_id
  region       = var.region
  display_name = "hmd-medical-endpoint"
  description  = "HelpMeDoctor medical conditions search endpoint"

  public_endpoint_enabled = true
}

resource "google_vertex_ai_index_endpoint_deployed_index" "deployed" {
  index_endpoint   = google_vertex_ai_index_endpoint.medical_endpoint.id
  index            = google_vertex_ai_index.medical_conditions.id
  deployed_index_id = "hmd_medical_deployed"
  display_name     = "hmd-medical-deployed"

  automatic_resources {
    min_replica_count = 1
    max_replica_count = 2
  }
}
