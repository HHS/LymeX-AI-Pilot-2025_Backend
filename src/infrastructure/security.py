from src.infrastructure.utils.token import encode_jwt, decode_jwt
from src.modules.user.models import User
from src.environment import environment


def create_access_token(user: User) -> str:
    access_token = encode_jwt(
        user=user,
        secret=environment.access_token_secret,
        expiration_seconds=environment.access_token_expiration_seconds,
    )
    return access_token


async def decode_access_token(token: str) -> User:
    user = await decode_jwt(
        token=token,
        secret=environment.access_token_secret,
    )
    return user


def create_refresh_token(user: User) -> str:
    refresh_token = encode_jwt(
        user=user,
        secret=environment.refresh_token_secret,
        expiration_seconds=environment.refresh_token_expiration_seconds,
    )
    return refresh_token


async def decode_refresh_token(token: str) -> User:
    user = await decode_jwt(
        token=token,
        secret=environment.refresh_token_secret,
    )
    return user


def create_verify_login_token(user: User, otp: str) -> str:
    verify_login_token = encode_jwt(
        user=user,
        secret=environment.verify_login_token_secret + otp,
        expiration_seconds=environment.verify_login_token_expiration_seconds,
    )
    return verify_login_token


async def decode_verify_login_token(token: str, otp: str) -> User:
    user = await decode_jwt(
        token=token,
        secret=environment.verify_login_token_secret + otp,
    )
    return user


def create_totp_login_token(user: User) -> str:
    totp_login_token = encode_jwt(
        user=user,
        secret=environment.totp_login_token_secret,
        expiration_seconds=environment.totp_login_token_expiration_seconds,
    )
    return totp_login_token


async def decode_totp_login_token(token: str) -> User:
    user = await decode_jwt(
        token=token,
        secret=environment.totp_login_token_secret,
    )
    return user


def create_forgot_password_token(user: User) -> str:
    forgot_password_token = encode_jwt(
        user=user,
        secret=environment.forgot_password_token_secret,
        expiration_seconds=environment.forgot_password_token_expiration_seconds,
    )
    return forgot_password_token


async def decode_forgot_password_token(token: str) -> User:
    user = await decode_jwt(
        token=token,
        secret=environment.forgot_password_token_secret,
    )
    return user


def create_verify_email_token(user: User) -> str:
    verify_email_token = encode_jwt(
        user=user,
        secret=environment.verify_email_token_secret,
        expiration_seconds=environment.verify_email_token_expiration_seconds,
    )
    return verify_email_token


async def decode_verify_email_token(token: str) -> User:
    user = await decode_jwt(
        token=token,
        secret=environment.verify_email_token_secret,
    )
    return user
