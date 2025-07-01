from beanie import PydanticObjectId
from typing import List, Optional
from datetime import datetime
from src.modules.notification.model import Notification
from src.modules.notification.schema import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
    NotificationCategory,
)


async def create_notification(notification_data: NotificationCreate) -> NotificationResponse:
    """Create a new notification."""
    notification = Notification(
        user_id=notification_data.user_id,
        company_id=notification_data.company_id,
        type=notification_data.type,
        title=notification_data.title,
        text=notification_data.text,
        category=notification_data.category,
        is_read=notification_data.is_read,
    )
    
    await notification.save()
    return notification.to_notification_response()


async def get_user_notifications(
    user_id: str,
    company_id: str,
    is_read: Optional[bool] = None,
    category: Optional[NotificationCategory] = None,
) -> List[NotificationResponse]:
    """Get notifications for a specific user."""
    query = {"user_id": user_id, "company_id": company_id}
    
    if is_read is not None:
        query["is_read"] = is_read
    
    if category is not None:
        query["category"] = category
    
    notifications = await Notification.find(query).sort(-Notification.created_at).to_list()
    
    return [notification.to_notification_response() for notification in notifications]


async def get_notification_by_id(notification_id: str, user_id: str, company_id: str) -> Optional[NotificationResponse]:
    """Get a specific notification by ID."""
    notification = await Notification.find_one({
        "_id": notification_id,
        "user_id": user_id,
        "company_id": company_id
    })
    
    return notification.to_notification_response() if notification else None


async def update_notification(
    notification_id: str,
    user_id: str,
    company_id: str,
    update_data: NotificationUpdate,
) -> Optional[NotificationResponse]:
    """Update a notification."""
    notification = await Notification.find_one({
        "_id": notification_id,
        "user_id": user_id,
        "company_id": company_id
    })
    
    if not notification:
        return None
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    if update_dict:
        update_dict["updated_at"] = datetime.now()
        await notification.update({"$set": update_dict})
        
        # Refresh the document
        await notification.fetch()
    
    return notification.to_notification_response()


async def mark_notification_as_read(notification_id: str, user_id: str, company_id: str) -> Optional[NotificationResponse]:
    """Mark a notification as read."""
    return await update_notification(
        notification_id,
        user_id,
        company_id,
        NotificationUpdate(is_read=True)
    )


async def mark_all_notifications_as_read(user_id: str, company_id: str, category: Optional[NotificationCategory] = None) -> int:
    """Mark all notifications as read for a user."""
    query = {"user_id": user_id, "company_id": company_id, "is_read": False}
    
    if category is not None:
        query["category"] = category
    
    result = await Notification.find(query).update_many({
        "$set": {"is_read": True, "updated_at": datetime.now()}
    })
    
    return result.modified_count


async def delete_notification(notification_id: str, user_id: str, company_id: str) -> bool:
    """Delete a notification."""
    notification = await Notification.find_one({
        "_id": notification_id,
        "user_id": user_id,
        "company_id": company_id
    })
    
    if not notification:
        return False
    
    await notification.delete()
    return True


async def get_unread_count(user_id: str, company_id: str, category: Optional[NotificationCategory] = None) -> int:
    """Get count of unread notifications for a user."""
    query = {"user_id": user_id, "company_id": company_id, "is_read": False}
    
    if category is not None:
        query["category"] = category
    
    return await Notification.find(query).count()


async def create_system_notification(
    user_id: str,
    company_id: str,
    title: str,
    text: str,
    notification_type: str = "System"
) -> NotificationResponse:
    """Create a system notification."""
    return await create_notification(
        NotificationCreate(
            user_id=user_id,
            company_id=company_id,
            type=notification_type,
            title=title,
            text=text,
            category=NotificationCategory.SYSTEM,
            is_read=False,
        )
    ) 