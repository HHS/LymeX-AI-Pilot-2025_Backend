from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from src.celery.tasks.echo import echo_task
from src.modules.health.service import check_mongo_health

router = APIRouter()


@router.get(
    "/",
    summary="Health Check",
    description="Checks the health of the application, including MongoDB connectivity.",
    responses={
        200: {"description": "Application is healthy."},
        503: {"description": "Application is unavailable due to MongoDB issues."},
    },
)
async def health_check() -> JSONResponse:
    mongo_ok = await check_mongo_health()

    if mongo_ok:
        return JSONResponse(
            content={
                "status": "ok",
                "mongo": "connected",
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unavailable",
                "mongo": "disconnected",
            },
        )


@router.get(
    "/celery",
    summary="Celery Health Check",
    description="Sends a test task to Celery to verify its functionality.",
    responses={
        200: {"description": "Task successfully sent to Celery."},
    },
)
async def celery_health_check() -> JSONResponse:
    echo_task.delay("Hello, Celery!")
    return JSONResponse(
        content={
            "status": "ok",
            "celery": "task sent",
        }
    )
