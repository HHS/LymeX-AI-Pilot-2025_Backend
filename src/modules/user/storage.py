from src.infrastructure.minio import (
    generate_get_object_presigned_url,
    generate_put_object_presigned_url,
)


def get_user_folder(user_id: str) -> str:
    return f"user/{user_id}"


def get_user_avatar_object_name(user_id: str) -> str:
    user_folder = get_user_folder(user_id)
    return f"{user_folder}/avatar"


async def get_user_avatar_url(user_id: str) -> str:
    user_avatar_object_name = get_user_avatar_object_name(user_id)
    user_avatar_url = await generate_get_object_presigned_url(
        object_name=user_avatar_object_name,
        expiration_seconds=300,
    )
    return user_avatar_url


async def get_update_user_avatar_url(user_id: str) -> str:
    user_avatar_object_name = get_user_avatar_object_name(user_id)
    user_avatar_url = await generate_put_object_presigned_url(
        object_name=user_avatar_object_name,
        expiration_seconds=300,
    )
    return user_avatar_url
