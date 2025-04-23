from src.infrastructure.minio import (
    generate_get_object_presigned_url,
    generate_put_object_presigned_url,
)
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.modules.user.models import User


def get_user_folder(user: "User") -> str:
    return f"user/{user.id}"


def get_user_avatar_object_name(user: "User") -> str:
    user_folder = get_user_folder(user)
    return f"{user_folder}/avatar"


async def get_user_avatar_url(user: "User") -> str:
    user_avatar_object_name = get_user_avatar_object_name(user)
    user_avatar_url = await generate_get_object_presigned_url(
        object_name=user_avatar_object_name,
        expiration_seconds=300,
    )
    return user_avatar_url


async def get_update_user_avatar_url(user: "User") -> str:
    user_avatar_object_name = get_user_avatar_object_name(user)
    user_avatar_url = await generate_put_object_presigned_url(
        object_name=user_avatar_object_name,
        expiration_seconds=300,
    )
    return user_avatar_url
