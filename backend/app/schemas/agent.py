from enum import StrEnum

from pydantic import BaseModel


class PathwayEnum(StrEnum):
    MEDICAL = "MEDICAL"
    LEGAL = "LEGAL"
    DUAL = "DUAL"
    OCCUPATIONAL = "OCCUPATIONAL"


class UrgencyEnum(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RouterOutput(BaseModel):
    pathway: PathwayEnum
    urgency: UrgencyEnum
    medical_keywords: list[str]
    legal_keywords: list[str]
    reasoning: str | None = None
