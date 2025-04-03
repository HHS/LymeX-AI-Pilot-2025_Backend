from fastapi import APIRouter
from src.celery.tasks.send_email import send_email_task

router = APIRouter()


@router.post("/test")
async def login_user():
    send_email_task.delay(
        "empty",
        {
            "subject": "HO THIEN LAC TEST",
            "body": "TEST BODY",
            "from_name": "Ho Thien Lac",
            "from_email": "hothienlac@hothienlac.com",
        },
        "hothienlac@gmail.com",
    )
