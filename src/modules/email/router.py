from fastapi import APIRouter
from src.celery.tasks.send_email import send_email_task

router = APIRouter()


@router.post("/test")
async def login_user():
    send_email_task.delay(
        "empty",
        {
            "subject": "NOIS2-192 TEST",
            "body": "TEST BODY",
            "from_name": "NOIS2-192 Project",
            "from_email": "noise2.192.do.not.reply@gmail.com",
        },
        "noise2.192.do.not.reply@gmail.com",
    )
