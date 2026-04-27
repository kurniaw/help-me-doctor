from datetime import timedelta

from beanie.operators import Eq
from fastapi import APIRouter, HTTPException, status

from app.auth.jwt import create_access_token
from app.auth.password import hash_password, verify_password
from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.config import get_settings
from app.models.user import UserDocument

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest) -> TokenResponse:
    settings = get_settings()

    existing = await UserDocument.find_one(Eq(UserDocument.email, payload.email))  # type: ignore[no-untyped-call]
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = UserDocument(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    await user.insert()

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes),
    )
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.jwt_expire_minutes * 60,
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    settings = get_settings()

    user = await UserDocument.find_one(Eq(UserDocument.email, payload.email))  # type: ignore[no-untyped-call]
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes),
    )
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.jwt_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def me_endpoint() -> UserResponse:
    """Placeholder — actual auth check is done in dependencies.get_current_user."""
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
