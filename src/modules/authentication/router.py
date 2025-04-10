from datetime import datetime, timezone
from typing import Annotated
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from src.modules.totp.models import UserTotp
from src.modules.totp.service import check_user_totp
from src.modules.authentication.dependencies import get_current_user
from src.modules.user.models import User
from .service import (
    create_and_send_forgot_password_email,
    create_and_send_verify_email,
    generate_access_token_refresh_token_response,
    generate_totp_login_response,
)
from src.modules.user.schemas import UserCreateRequest, UserResponse
from src.modules.user.service import (
    check_email_password,
    create_user,
    get_user_by_email,
    hash_password,
)
from .schemas import (
    AccessTokenRefreshTokenResponse,
    ForgotPasswordRequest,
    LoginTOTPTokenRequest,
    SendForgotPasswordEmailRequest,
    LoginPasswordRequest,
    LoginRefreshTokenRequest,
    SendVerifyEmailRequest,
    UserLoginResponse,
    VerifyEmailRequest,
)
from src.infrastructure.security import (
    decode_forgot_password_token,
    decode_refresh_token,
    decode_totp_login_token,
    decode_verify_email_token,
)

router = APIRouter()


# 📥 Register
@router.post("/register/password")
async def register_user_using_password(payload: UserCreateRequest) -> UserResponse:
    try:
        user = await create_user(payload)
        create_and_send_verify_email(user)
        return await user.to_user_response()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/register/verify-email/send-email")
async def send_verify_email(payload: SendVerifyEmailRequest) -> None:
    user = await get_user_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    create_and_send_verify_email(user)


@router.post("/register/verify-email")
async def verify_email(payload: VerifyEmailRequest) -> None:
    user = await decode_verify_email_token(payload.verify_email_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    user.verified_at = datetime.now(timezone.utc)
    await user.save()


@router.post("/login/password")
async def login_password(payload: LoginPasswordRequest) -> UserLoginResponse:
    user = await check_email_password(payload.email, payload.password)
    if user.enable_totp:
        existing_user_totp = await UserTotp.find_one(
            UserTotp.user_id == str(user.id),
            UserTotp.verified_at != None,
        )
        if existing_user_totp:
            return generate_totp_login_response(user)
        else:
            user.enable_totp = False
            await user.save()
    return generate_access_token_refresh_token_response(user)


@router.post("/login/totp")
async def login_totp(
    payload: LoginTOTPTokenRequest,
) -> AccessTokenRefreshTokenResponse:
    user = await decode_totp_login_token(payload.totp_login_token)
    is_totp_code_valid = await check_user_totp(user, payload.code)
    if not is_totp_code_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code"
        )
    response = generate_access_token_refresh_token_response(user)
    return response


@router.post("/login/refresh-token")
async def login_refresh_token(
    payload: LoginRefreshTokenRequest,
) -> AccessTokenRefreshTokenResponse:
    user = await decode_refresh_token(payload.refresh_token)
    response = generate_access_token_refresh_token_response(user)
    return response


@router.post("/forgot-password/send-email")
async def send_forgot_password_email(payload: SendForgotPasswordEmailRequest) -> None:
    user = await get_user_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    create_and_send_forgot_password_email(user)


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest) -> None:
    user = await decode_forgot_password_token(payload.forgot_password_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    user.password = hash_password(payload.new_password)
    await user.save()


@router.post("/logout-all-devices")
async def logout_all_devices(
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    current_user.secret_token = uuid4().hex
    await current_user.save()
