from datetime import datetime
from beanie import Document, Indexed, PydanticObjectId
from typing import Annotated, Optional


class UserTotp(Document):
    user_id: Annotated[str, Indexed(unique=True)]
    secret: str
    created_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None

    class Settings:
        name = "user_totp"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
