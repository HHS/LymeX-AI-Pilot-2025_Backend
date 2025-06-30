import asyncio

import httpx
from fastapi import HTTPException
from loguru import logger

from src.celery.tasks.base import BaseTask
from src.celery.worker import celery
from src.environment import environment


@celery.task(
    base=BaseTask,
    name="src.celery.tasks.index_system_data",
)
def index_system_data_task() -> None:
    logger.info("Indexing system data")
    try:
        if environment.use_separated_ai_service:
            logger.info("Using separated AI service for system data analysis")
            httpx.post(f"{environment.ai_service_url}/index-system-data")
        else:
            logger.info("Using internal AI service for system data analysis")
            asyncio.run(index_system_data_task_async())
    except HTTPException as e:
        logger.error(f"Failed index: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(500, "Internal Server Error") from e


async def index_system_data_task_async() -> None:
    raise HTTPException(
        status_code=501,
        detail="Mocking is not implemented. Please use the separated AI service.",
    )
