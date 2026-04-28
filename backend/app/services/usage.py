from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.models.user import UserDocument

DAILY_LIMIT = 5


async def check_and_increment_daily_usage(user: UserDocument) -> int:
    """Enforce daily prompt limit. Returns remaining count after increment."""
    today = datetime.now(UTC).date()

    if user.daily_prompt_date != today:
        user.daily_prompt_count = 0
        user.daily_prompt_date = today

    if user.daily_prompt_count >= DAILY_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily limit of {DAILY_LIMIT} prompts reached. Try again tomorrow.",
        )

    user.daily_prompt_count += 1
    await user.save()
    return DAILY_LIMIT - user.daily_prompt_count
