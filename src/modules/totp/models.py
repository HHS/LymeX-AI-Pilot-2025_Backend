from datetime import datetime
from beanie import Document, Indexed, PydanticObjectId
from typing import Annotated


class UserTotp(Document):
    user_id: Annotated[str, Indexed(unique=True)]
    secret: str
    created_at: datetime | None = None
    verified_at: datetime | None = None

    class Settings:
        name = "user_totp"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
