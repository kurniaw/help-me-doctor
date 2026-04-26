from typing import Literal, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class StreamChunk(BaseModel):
    type: Literal["chunk", "done", "error"]
    content: str
    urgency: Optional[str] = None
    pathway: Optional[str] = None
