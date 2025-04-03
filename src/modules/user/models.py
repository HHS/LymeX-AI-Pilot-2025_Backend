from beanie import Document, PydanticObjectId
from typing import Optional
from datetime import datetime, timezone

from src.modules.user.schemas import UserResponse


class User(Document):
    email: str
    first_name: str
    last_name: str
    password: str
    phone: Optional[str]
    secret_token: str
    verified_at: Optional[datetime] = None
    policy_accepted_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
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
            verified_at=self.verified_at,
            deleted_at=self.deleted_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
