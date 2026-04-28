from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import UserDocument
from app.services.usage import DAILY_LIMIT

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("")
async def get_usage(current_user: UserDocument = Depends(get_current_user)) -> dict:
    today = datetime.now(UTC).date()

    if current_user.daily_prompt_date != today:
        prompts_used = 0
    else:
        prompts_used = current_user.daily_prompt_count

    return {
        "prompts_used": prompts_used,
        "prompts_remaining": max(0, DAILY_LIMIT - prompts_used),
        "prompts_limit": DAILY_LIMIT,
    }
