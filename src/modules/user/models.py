from beanie import Document, Indexed, PydanticObjectId
from typing import Annotated, Optional
from datetime import datetime, timezone
from src.infrastructure.minio import generate_get_object_presigned_url
from src.modules.user.constants import USER_AVATAR_OBJECT_PREFIX
from src.environment import environment

from src.modules.user.schemas import UserResponse


class User(Document):
    email: Annotated[str, Indexed(unique=True)]
    first_name: str
    last_name: str
    password: str
    phone: Optional[str] = None
    title: Optional[str] = None
    secret_token: str
    enable_totp: bool = False
    verified_at: Optional[datetime] = None
    policy_accepted_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    locked_until: Optional[datetime] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "users"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    async def to_user_response(self) -> UserResponse:
        avatar_url = await generate_get_object_presigned_url(
            object_name=f"{USER_AVATAR_OBJECT_PREFIX}/{self.id}",
            expiration_seconds=300,
        )
        return UserResponse(
            id=str(self.id),
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            avatar=avatar_url,
            phone=self.phone,
            title=self.title,
            verified_at=self.verified_at,
            deleted_at=self.deleted_at,
            locked_until=self.locked_until,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
