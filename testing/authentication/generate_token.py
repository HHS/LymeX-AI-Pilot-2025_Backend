import asyncio
import os

from src.infrastructure.database import init_db
from src.modules.authentication.service import (
    generate_access_token_refresh_token_response,
)
from src.modules.user.models import User


async def async_test() -> None:
    user_id = os.getenv("TEST_USER_ID")
    if not user_id:
        raise ValueError("TEST_USER_ID environment variable is not set.")
    print(f"TEST_USER_ID: {user_id}")
    await init_db()
    user = await User.get(user_id)
    token = generate_access_token_refresh_token_response(user)
    print(token)


def test() -> None:
    asyncio.run(async_test())
