from datetime import UTC, date, datetime
from typing import Optional

from beanie import Document
from pydantic import EmailStr, Field


class UserDocument(Document):
    name: str
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    daily_prompt_count: int = 0
    daily_prompt_date: Optional[date] = None

    class Settings:
        name = "users"
        indexes = ["email"]
