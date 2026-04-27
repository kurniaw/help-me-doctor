import logging

from google.cloud import aiplatform

from app.config import get_settings
from app.rag.embedder import embed_query

logger = logging.getLogger(__name__)

_endpoint: aiplatform.MatchingEngineIndexEndpoint | None = None


def get_endpoint() -> aiplatform.MatchingEngineIndexEndpoint | None:
    global _endpoint
    settings = get_settings()

    if not settings.vertex_index_endpoint_id:
        return None

    if _endpoint is None:
        aiplatform.init(project=settings.gcp_project_id, location=settings.gcp_region)
        _endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=settings.vertex_index_endpoint_id
        )
    return _endpoint


async def semantic_search_conditions(query: str, top_k: int = 5) -> list[str]:
    """Search medical conditions by semantic similarity. Returns list of vertex_ids."""
    settings = get_settings()
    endpoint = get_endpoint()

    if endpoint is None:
        logger.warning("Vertex AI endpoint not configured, skipping semantic search")
        return []

    try:
        embedding = await embed_query(query)
        response = endpoint.find_neighbors(
            deployed_index_id=settings.vertex_deployed_index_id,
            queries=[embedding],
            num_neighbors=top_k,
        )
        if response and response[0]:
            return [neighbor.id for neighbor in response[0]]
    except Exception as e:
        logger.warning("Vertex AI search failed: %s", e)

    return []
