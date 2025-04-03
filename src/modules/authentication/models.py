from datetime import datetime, timezone, timedelta
from beanie import Document, PydanticObjectId
from pydantic import Field


class Session(Document):
    user_id: str
    ip_address: str
    user_agent: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=30))

    class Settings:
        name = "email_templates"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
