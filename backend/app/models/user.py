from datetime import datetime, timezone

from beanie import Document
from pydantic import EmailStr, Field


class UserDocument(Document):
    name: str
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"
        indexes = ["email"]
