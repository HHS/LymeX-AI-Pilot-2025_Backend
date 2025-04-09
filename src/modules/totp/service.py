from fastapi import HTTPException, status
import pyotp
from datetime import datetime, timezone
from src.modules.user.models import User
from src.environment import environment
from src.modules.totp.models import UserTotp


async def setup_user_totp(user: User) -> str:
    existing_user_totp = await UserTotp.find_one(
        UserTotp.user_id == str(user.id),
    )
    if existing_user_totp:
        if existing_user_totp.verified_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TOTP is already setup for this user. You can disable it first to reset.",
            )
        else:
            await existing_user_totp.delete()
    secret = pyotp.random_base32()
    provisioning_uri = pyotp.totp.TOTP(
        secret, digits=environment.totp_digits, interval=environment.totp_interval
    ).provisioning_uri(
        name=user.email,
        issuer_name=environment.application_name,
    )
    user_totp = UserTotp(
        user_id=str(user.id),
        secret=secret,
        created_at=datetime.now(timezone.utc),
    )
    await user_totp.insert()
    return provisioning_uri


async def check_user_totp(user: User, code: str) -> bool:
    """
    Just check if the TOTP code is valid for the user.
    """
    user_totp = await UserTotp.find_one(
        UserTotp.user_id == str(user.id),
        UserTotp.verified_at != None,
    )
    if not user_totp:
        return False
    totp = pyotp.TOTP(
        user_totp.secret,
        digits=environment.totp_digits,
        interval=environment.totp_interval,
    )
    return totp.verify(code, valid_window=environment.totp_valid_window)


async def verify_user_totp(
    user: User,
    code: str,
) -> None:
    user_totp = await UserTotp.find_one(
        UserTotp.user_id == str(user.id),
    )
    if not user_totp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP is not setup for this user yet, setup it before verification.",
        )
    if user_totp.verified_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP is already verified for this user.",
        )
    totp = pyotp.TOTP(
        user_totp.secret,
        digits=environment.totp_digits,
        interval=environment.totp_interval,
    )
    if not totp.verify(code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code.",
        )
    user_totp.verified_at = datetime.now(timezone.utc)
    await user_totp.save()


async def remove_user_totp(user: User) -> None:
    user_totp = await UserTotp.find_one(
        UserTotp.user_id == str(user.id),
        UserTotp.verified_at == None,
    )
    if not user_totp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP is not setup for this user yet.",
        )
    user.enable_totp = False
    await user.save()
    await user_totp.delete()
