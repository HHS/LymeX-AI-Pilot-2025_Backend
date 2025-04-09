from beanie import Document, Indexed, PydanticObjectId
from typing import Annotated, Optional
from datetime import datetime, timezone
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

    def to_user_response(self) -> UserResponse:
        return UserResponse(
            id=str(self.id),
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            avatar=f"{environment.minio_external_endpoint}/{environment.minio_bucket}/{USER_AVATAR_OBJECT_PREFIX}/{self.id}",
            phone=self.phone,
            title=self.title,
            verified_at=self.verified_at,
            deleted_at=self.deleted_at,
            locked_until=self.locked_until,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
