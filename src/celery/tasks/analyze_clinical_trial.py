from fastapi import HTTPException
import httpx
from loguru import logger
from src.environment import environment
from src.celery.worker import celery
from src.celery.tasks.base import BaseTask


@celery.task(
    base=BaseTask,
    name="src.celery.tasks.analyze_clinical_trial",
)
def analyze_clinical_trial_task(
    product_id: str,
) -> None:
    logger.info(f"Analyzing for product_id: {product_id}")
    try:
        httpx.post(
            f"{environment.ai_service_url}/analyze-clinical-trial?product_id={product_id}",
            timeout=100,
        )
    except HTTPException as e:
        logger.error(f"Failed analyze: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(500, "Internal Server Error") from e
