import asyncio
from fastapi import HTTPException
from loguru import logger
from src.celery.worker import celery
from src.celery.tasks.base import BaseTask
from src.infrastructure.redis import redis_client
from src.modules.product.milestone_planning.model import MilestonePlanning
from src.modules.product.milestone_planning.schema import Milestone
from datetime import datetime, timedelta


@celery.task(
    base=BaseTask,
    name="src.celery.tasks.analyze_milestone_planning",
)
def analyze_milestone_planning_task(
    product_id: str,
) -> None:
    logger.info(f"Analyzing milestone planning for product_id: {product_id}")
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            analyze_milestone_planning_task_async(
                product_id,
            )
        )
    except HTTPException as e:
        logger.error(f"Failed analyze: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(500, "Internal Server Error") from e


async def analyze_milestone_planning_task_async(
    product_id: str,
) -> None:
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzeMilestonePlanning:AnalyzeLock:{product_id}",
        timeout=100,
    )
    lock_acquired = await lock.acquire(blocking=False)
    if not lock_acquired:
        logger.info(
            f"Lock already acquired for milestone planning {product_id}. Skipping analysis."
        )
        return

    # Example milestone planning analysis
    # In a real system, this would be replaced with actual analysis logic
    milestone_planning = MilestonePlanning(
        product_id=product_id,
        milestones=[
            Milestone(
                row=1,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=90),
                name="Initial Design Phase"
            ),
            Milestone(
                row=2,
                start_date=datetime.now() + timedelta(days=91),
                end_date=datetime.now() + timedelta(days=180),
                name="Development Phase"
            ),
            Milestone(
                row=3,
                start_date=datetime.now() + timedelta(days=181),
                end_date=datetime.now() + timedelta(days=270),
                name="Testing Phase"
            )
        ]
    )

    # Delete any existing milestone planning for this product
    await MilestonePlanning.find(
        MilestonePlanning.product_id == product_id,
    ).delete_many()

    # Save the new milestone planning
    await milestone_planning.save()

    logger.info(f"Milestone planning analysis completed for product_id: {product_id}")
    await lock.release()
    logger.info(f"Released lock for milestone planning {product_id}.")
