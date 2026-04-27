from langchain_google_vertexai import VertexAIEmbeddings

from app.config import get_settings

_embedder: VertexAIEmbeddings | None = None


def get_embedder() -> VertexAIEmbeddings:
    global _embedder
    if _embedder is None:
        settings = get_settings()
        _embedder = VertexAIEmbeddings(
            model=settings.embedding_model,
            project=settings.gcp_project_id,
            location=settings.gcp_region,
        )
    return _embedder


async def embed_query(text: str) -> list[float]:
    embedder = get_embedder()
    result = await embedder.aembed_query(text)
    return result
