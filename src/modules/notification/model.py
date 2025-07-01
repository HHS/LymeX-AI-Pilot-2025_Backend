from beanie import Document, PydanticObjectId
from datetime import datetime
from typing import Optional
from src.modules.notification.schema import NotificationCategory


class Notification(Document):
    user_id: str
    company_id: str
    type: str
    title: str
    text: str
    category: str
    is_read: bool = False
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "notifications"
        indexes = [
            "user_id",
            "company_id",
            "is_read",
            "category",
            ("user_id", "is_read"),
            ("company_id", "is_read"),
        ]

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_notification_response(self):
        from src.modules.notification.schema import NotificationResponse

        return NotificationResponse(
            id=str(self.id),
            user_id=self.user_id,
            company_id=self.company_id,
            type=self.type,
            title=self.title,
            text=self.text,
            category=self.category,
            is_read=self.is_read,
            time=self.created_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
