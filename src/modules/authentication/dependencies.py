from typing import Annotated
from fastapi import Depends, HTTPException, Header, status

from src.modules.totp.service import check_user_totp
from src.modules.totp.constants import TOTP_CODE_HEADER
from src.modules.user.models import User
from src.infrastructure.security import decode_access_token


# 🔐 Dependency to get current user
async def get_current_user(authorization: Annotated[str, Header()]) -> User:
    access_token = authorization.removeprefix("Bearer ")
    user = await decode_access_token(access_token)
    return user


async def require_totp(
    code: Annotated[str, Header(alias=TOTP_CODE_HEADER)],
    current_user: User = Depends(get_current_user),
) -> bool:
    is_totp_valid = await check_user_totp(current_user, code)
    if not is_totp_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )
    return True
