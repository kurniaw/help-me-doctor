from typing import Literal

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class StreamChunk(BaseModel):
    type: Literal["chunk", "done", "error"]
    content: str
    urgency: str | None = None
    pathway: str | None = None
