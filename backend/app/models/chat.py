from datetime import UTC, datetime
from typing import Any

from beanie import Document
from pydantic import Field


class MessageDocument:
    def __init__(
        self,
        role: str,
        content: str,
        urgency: str | None = None,
        pathway: str | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        self.role = role
        self.content = content
        self.urgency = urgency
        self.pathway = pathway
        self.timestamp = timestamp or datetime.now(UTC)


class ChatSessionDocument(Document):
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    messages: list[dict[str, Any]] = Field(default_factory=list)

    class Settings:
        name = "chat_sessions"
        indexes = ["user_id"]
