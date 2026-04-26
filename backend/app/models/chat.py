from datetime import datetime, timezone
from typing import Optional

from beanie import Document, Link
from pydantic import Field

from app.models.user import UserDocument


class MessageDocument:
    def __init__(
        self,
        role: str,
        content: str,
        urgency: Optional[str] = None,
        pathway: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        self.role = role
        self.content = content
        self.urgency = urgency
        self.pathway = pathway
        self.timestamp = timestamp or datetime.now(timezone.utc)


class ChatSessionDocument(Document):
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    messages: list[dict] = Field(default_factory=list)

    class Settings:
        name = "chat_sessions"
        indexes = ["user_id"]
