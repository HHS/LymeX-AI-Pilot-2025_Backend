from typing import Annotated
from fastapi import Depends, Header

from src.modules.user.models import User
from src.infrastructure.security import decode_access_token

# 🔐 Dependency to get current user
async def get_current_user(authorization: Annotated[str, Header()]) -> User:
    access_token = authorization.removeprefix("Bearer ")
    user = await decode_access_token(access_token)
    return user
