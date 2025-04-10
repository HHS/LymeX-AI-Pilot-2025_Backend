from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# -------- Request DTOs --------


class LoginPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ..., description="User's password", min_length=8, max_length=128
    )


class LoginTOTPTokenRequest(BaseModel):
    totp_login_token: str = Field(
        ...,
        description="TOTP login token, use for login, will need to be sent along with the TOTP code",
    )
    code: str = Field(..., description="TOTP code", min_length=6, max_length=6)


class LoginRefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT refresh token")


class SendForgotPasswordEmailRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    forgot_password_token: str = Field(..., description="Forgot password token")
    new_password: str = Field(
        ..., description="New password", min_length=8, max_length=128
    )


class SendVerifyEmailRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")


class VerifyEmailRequest(BaseModel):
    verify_email_token: str = Field(..., description="Verify email token")


# -------- Response DTO --------


class AccessTokenRefreshTokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")


class TOTPLoginResponse(BaseModel):
    totp_login_token: str = Field(
        ...,
        description="TOTP login token, use for login, will need to be sent along with the TOTP code",
    )


type UserLoginResponse = AccessTokenRefreshTokenResponse | TOTPLoginResponse
