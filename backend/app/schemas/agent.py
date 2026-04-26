from enum import Enum
from typing import Optional

from pydantic import BaseModel


class PathwayEnum(str, Enum):
    MEDICAL = "MEDICAL"
    LEGAL = "LEGAL"
    DUAL = "DUAL"
    OCCUPATIONAL = "OCCUPATIONAL"


class UrgencyEnum(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"


class RouterOutput(BaseModel):
    pathway: PathwayEnum
    urgency: UrgencyEnum
    medical_keywords: list[str]
    legal_keywords: list[str]
    reasoning: Optional[str] = None
