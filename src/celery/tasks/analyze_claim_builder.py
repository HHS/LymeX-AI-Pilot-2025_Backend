from fastapi import HTTPException
import httpx
from loguru import logger
from src.environment import environment
from src.celery.worker import celery
from src.celery.tasks.base import BaseTask


@celery.task(
    base=BaseTask,
    name="src.celery.tasks.analyze_claim_builder",
)
def analyze_claim_builder_task(
    product_id: str,
) -> None:
    logger.info(f"Parsing product profile for product: {product_id}")
    try:
        httpx.post(
            f"{environment.ai_service_url}/analyze-claim-builder?product_id={product_id}",
            timeout=100,
        )
    except HTTPException as e:
        logger.error(f"Failed to analyze product profile: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(500, "Internal Server Error") from e
