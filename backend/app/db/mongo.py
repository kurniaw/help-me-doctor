from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

_client: AsyncIOMotorClient | None = None  # type: ignore[type-arg]


def get_client() -> AsyncIOMotorClient:  # type: ignore[type-arg]
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.mongo_uri)
    return _client


def get_database() -> AsyncIOMotorDatabase:  # type: ignore[type-arg]
    settings = get_settings()
    return get_client()[settings.mongo_db_name]


async def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
