from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from src.modules.authentication.dependencies import get_current_user
from src.modules.user.models import User
from src.modules.authorization.dependencies import get_current_company
from src.modules.company.models import Company
from src.modules.notification.service import (
    get_user_notifications,
    mark_all_notifications_as_read,
    get_unread_count,
    create_notification,
)
from src.modules.notification.schema import (
    NotificationResponse,
    NotificationCategory,
    NotificationCreate,
    NotificationCreateRequest,
    NotificationUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    category: Optional[NotificationCategory] = Query(
        None, description="Filter by category"
    ),
) -> List[NotificationResponse]:
    """Get notifications for the current user."""
    return await get_user_notifications(
        user_id=str(user.id),
        company_id=str(company.id),
        is_read=is_read,
        category=category,
    )


@router.get("/unread-count")
async def get_unread_notifications_count(
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
    category: Optional[NotificationCategory] = Query(
        None, description="Filter by category"
    ),
) -> dict:
    """Get count of unread notifications for the current user."""
    count = await get_unread_count(
        user_id=str(user.id),
        company_id=str(company.id),
        category=category,
    )
    return {"unread_count": count}


@router.patch("/mark-all-read")
async def mark_all_notifications_read(
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
    category: Optional[NotificationCategory] = Query(
        None, description="Filter by category"
    ),
) -> dict:
    """Mark all notifications as read for the current user."""
    await mark_all_notifications_as_read(
        user_id=str(user.id),
        company_id=str(company.id),
        category=category,
    )
    return {"message": "All notifications marked as read"}


@router.post("/", response_model=NotificationResponse)
async def create_new_notification(
    notification_data: NotificationCreateRequest,
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
) -> NotificationResponse:
    """Create a new notification."""
    # Set user_id and company_id from context
    notification = NotificationCreate(
        **notification_data.model_dump(),
        user_id=str(user.id),
        company_id=str(company.id),
    )
    return await create_notification(notification)
