from contextlib import asynccontextmanager
from typing import AsyncGenerator

import beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.db.mongo import close_client, get_client
from app.models.chat import ChatSessionDocument
from app.models.user import UserDocument


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    client = get_client()
    await beanie.init_beanie(
        database=client[settings.mongo_db_name],
        document_models=[UserDocument, ChatSessionDocument],
    )
    yield
    await close_client()


def create_app() -> FastAPI:
    app = FastAPI(
        title="HelpMeDoctor API",
        description="Singapore Medical/Legal RAG Multi-Agent System",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://*.run.app"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "help-me-doctor-api"}

    return app


app = create_app()
