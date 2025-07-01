from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    SYSTEM = "System"
    PRODUCT = "Product"
    TASK = "Task"
    ALERT = "Alert"
    INFO = "Info"


class NotificationCategory(str, Enum):
    SYSTEM = "System"
    PRODUCT = "Product"
    TASK = "Task"
    ALERT = "Alert"
    INFO = "Info"


class NotificationBase(BaseModel):
    type: str
    title: str
    text: str
    category: NotificationCategory = NotificationCategory.SYSTEM
    is_read: bool = False


class NotificationCreate(NotificationBase):
    user_id: str
    company_id: str


# New schema for client POST requests (no user_id/company_id)
class NotificationCreateRequest(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    company_id: str
    time: datetime
    created_at: datetime
    updated_at: datetime


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    title: Optional[str] = None
    text: Optional[str] = None
