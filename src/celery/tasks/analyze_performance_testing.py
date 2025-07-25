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
    product_id: str,
    performance_testing_id: str | None = None,
) -> None:
    logger.info(f"Analyzing test for product id: {product_id}")
    url = f"{environment.ai_service_url}/analyze-performance-testing?product_id={product_id}"
    if performance_testing_id:
        url += f"&performance_testing_id={performance_testing_id}"
    try:
        httpx.post(
            url,
            timeout=100,
        )
    except HTTPException as e:
        logger.error(f"Failed to test: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(500, "Internal Server Error") from e
