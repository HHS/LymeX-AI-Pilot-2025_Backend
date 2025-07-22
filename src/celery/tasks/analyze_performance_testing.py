from fastapi import HTTPException
import httpx
from loguru import logger
from src.environment import environment
from src.celery.worker import celery
from src.celery.tasks.base import BaseTask


@celery.task(
    base=BaseTask,
    name="src.celery.tasks.analyze_performance_testing",
)
def analyze_performance_testing_task(
    performance_testing_id: str,
) -> None:
    logger.info(f"Analyzing test for test id: {performance_testing_id}")
    try:
        httpx.post(
            f"{environment.ai_service_url}/analyze-performance-testing?performance_testing_id={performance_testing_id}"
        )
    except HTTPException as e:
        logger.error(f"Failed to test: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(500, "Internal Server Error") from e
