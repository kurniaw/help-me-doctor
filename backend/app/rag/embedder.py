from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import get_settings

_embedder: GoogleGenerativeAIEmbeddings | None = None


def get_embedder() -> GoogleGenerativeAIEmbeddings:
    global _embedder
    if _embedder is None:
        settings = get_settings()
        _embedder = GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model,
            google_api_key=settings.google_api_key,
        )
    return _embedder


async def embed_query(text: str) -> list[float]:
    embedder = get_embedder()
    result = await embedder.aembed_query(text)
    return result
