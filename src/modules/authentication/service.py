from secrets import randbelow
from .schemas import (
    AccessTokenRefreshTokenResponse,
    LoginVerificationResponse,
    TOTPLoginResponse,
)
from src.celery.tasks.send_email import send_email_task
from src.environment import environment
from src.infrastructure.security import (
    create_access_token,
    create_forgot_password_token,
    create_refresh_token,
    create_totp_login_token,
    create_verify_email_token,
    create_verify_login_token,
)
from src.modules.user.models import User


def generate_access_token_refresh_token_response(
    user: User,
) -> AccessTokenRefreshTokenResponse:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return AccessTokenRefreshTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


def generate_verify_login_token_response(
    user: User,
) -> LoginVerificationResponse:
    length = environment.verify_login_token_number_of_digits
    otp = str(randbelow(10**length)).zfill(length)
    verify_login_token = create_verify_login_token(user, otp)
    send_email_task.delay(
        "verify_login",
        {
            "otp": otp,
        },
        user.email,
    )
    return LoginVerificationResponse(
        verify_login_token=verify_login_token,
    )


def generate_totp_login_token_response(user: User) -> TOTPLoginResponse:
    totp_login_token = create_totp_login_token(user)
    return TOTPLoginResponse(
        totp_login_token=totp_login_token,
    )


def create_verify_email_url(user: User) -> str:
    verify_email_token = create_verify_email_token(user)
    verify_email_url = f"{environment.frontend_url}?token={verify_email_token}"
    return verify_email_url


def create_and_send_verify_email(user: User) -> None:
    verify_email_url = create_verify_email_url(user)
    send_email_task.delay(
        "verify_email",
        {
            "name": f"{user.first_name} {user.last_name}",
            "verify_email_url": verify_email_url,
        },
        user.email,
    )


def create_forgot_password_url(user: User) -> str:
    forgot_password_token = create_forgot_password_token(user)
    forgot_password_url = (
        f"{environment.frontend_url}/forgot-password?token={forgot_password_token}"
    )
    return forgot_password_url


def create_and_send_forgot_password_email(user: User) -> None:
    forgot_password_url = create_forgot_password_url(user)
    send_email_task.delay(
        "forgot_password",
        {
            "name": f"{user.first_name} {user.last_name}",
            "forgot_password_url": forgot_password_url,
        },
        user.email,
    )
