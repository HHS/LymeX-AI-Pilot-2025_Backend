from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from src.infrastructure.authentication import get_current_user
from src.modules.user.models import User
from src.modules.authentication.service import (
    create_and_send_forgot_password_email,
    create_and_send_verify_email,
)
from src.modules.user.schemas import UserCreateRequest, UserResponse
from src.modules.user.service import (
    check_email_password,
    create_user,
    get_user_by_email,
    hash_password,
)
from .schemas import (
    ForgotPasswordRequest,
    SendForgotPasswordEmailRequest,
    LoginPasswordRequest,
    LoginRefreshTokenRequest,
    SendVerifyEmailRequest,
    UserLoginResponse,
    VerifyEmailRequest,
)
from src.infrastructure.security import (
    create_access_token,
    create_refresh_token,
    decode_forgot_password_token,
    decode_refresh_token,
    decode_verify_email_token,
)

router = APIRouter()


# 📥 Register
@router.post("/register/password")
async def register_user_using_password(request: UserCreateRequest) -> UserResponse:
    try:
        user = await create_user(request)
        create_and_send_verify_email(user)
        return user.to_user_response()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/register/verify-email/send-email")
async def send_verify_email(payload: SendVerifyEmailRequest) -> None:
    user = await get_user_by_email(payload.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    create_and_send_verify_email(user)


@router.post("/register/verify-email")
async def verify_email(payload: VerifyEmailRequest) -> None:
    user = await decode_verify_email_token(payload.verify_email_token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user.verified_at = datetime.now(timezone.utc)
    await user.save()


@router.post("/login/password")
async def login_password(request: LoginPasswordRequest) -> UserLoginResponse:
    user = await check_email_password(request.email, request.password)
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return UserLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login/refresh-token")
async def login_refresh_token(request: LoginRefreshTokenRequest) -> UserLoginResponse:
    user = await decode_refresh_token(request.refresh_token)
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return UserLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/forgot-password/send-email")
async def send_forgot_password_email(payload: SendForgotPasswordEmailRequest) -> None:
    user = await get_user_by_email(payload.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    create_and_send_forgot_password_email(user)


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest) -> None:
    user = await decode_forgot_password_token(payload.forgot_password_token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user.password = hash_password(payload.new_password)
    await user.save()


@router.post("/logout-all-devices")
async def logout_all_devices(current_user: User = Depends(get_current_user)) -> None:
    current_user.secret_token = uuid4().hex
    await current_user.save()
