import asyncio
from datetime import datetime, timezone
from random import randint
from fastapi import HTTPException
from loguru import logger
from src.modules.product.product_profile.schema import Feature, Performance
from src.modules.product.product_profile.model import (
    ProductProfile,
    AnalyzeProductProfileProgress,
)
from src.modules.product.product_profile.storage import (
    get_product_profile_documents,
)
from src.celery.worker import celery
from src.celery.tasks.base import BaseTask
from src.infrastructure.redis import redis_client


@celery.task(
    base=BaseTask,
    name="src.celery.tasks.analyze_product_profile",
)
def analyze_product_profile_task(
    product_id: str,
) -> None:
    logger.info(f"Parsing product profile for product: {product_id}")
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            analyze_product_profile_task_async(
                product_id,
            )
        )
    except HTTPException as e:
        logger.error(f"Failed to analyze product profile: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(500, "Internal Server Error") from e


class AnalyzeProgress:
    initialized = False
    progress: AnalyzeProductProfileProgress

    async def initialize(self, product_id: str, total_files: int):
        existing_progress = await AnalyzeProductProfileProgress.find_one(
            AnalyzeProductProfileProgress.product_id == product_id,
        )
        if existing_progress:
            self.progress = existing_progress
            self.progress.product_id = product_id
            self.progress.total_files = total_files
            self.progress.processed_files = 0
            self.progress.updated_at = datetime.now(timezone.utc)
        else:
            self.progress = AnalyzeProductProfileProgress(
                product_id=product_id,
                total_files=total_files,
                processed_files=0,
                updated_at=datetime.now(timezone.utc),
            )
        await self.progress.save()
        self.initialized = True
        logger.info(
            f"Initialized progress for product {product_id} with total files {total_files}"
        )

    async def increase(self, count: int = 1):
        if not self.initialized:
            raise HTTPException(
                status_code=500,
                detail="Progress not initialized. Call initialize() first.",
            )
        self.progress.processed_files += count
        self.progress.updated_at = datetime.now(timezone.utc)
        await self.progress.save()


async def analyze_product_profile_task_async(
    product_id: str,
) -> None:
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzeProductProfile:AnalyzeLock:{product_id}",
        timeout=100,
    )
    lock_acquired = await lock.acquire(blocking=False)
    if not lock_acquired:
        logger.info(
            f"Task is already running for product {product_id}. Skipping analysis."
        )
        return

    product_profile_documents = await get_product_profile_documents(product_id)
    number_of_documents = len(product_profile_documents)

    progress = AnalyzeProgress()
    await progress.initialize(product_id, number_of_documents)

    for i, document in enumerate(product_profile_documents):
        await progress.increase()
        logger.info(
            f"Analyzed product profile document {i + 1}/{number_of_documents} for product: {product_id}"
        )
    logger.info("Starting AI generation of product profile...")
    logger.info(f"Finished analyzing product profile for product: {product_id}")
    await ProductProfile.find(
        ProductProfile.product_id == product_id,
    ).delete_many()
    product_profile = ProductProfile(
        product_id=product_id,
        reference_number="Sample reference number",
        description="Sample description",
        regulatory_pathway="Sample regulatory pathway",
        regulatory_classifications=[
            {
                "organization": "FDA",
                "classification": "Class II",
            },
            {
                "organization": "CE",
                "classification": "Class IIa",
            },
            {
                "organization": "PMDA",
                "classification": "Class II",
            },
        ],
        device_description="Sample device description",
        features=[
            Feature(
                name="Battery life",
                description="The battery life of the device is 10 hours.",
                icon="battery",
            )
        ],
        claims=["Claim 1", "Claim 2"],
        conflict_alerts=["Conflict alert 1", "Conflict alert 2"],
        fda_approved=False,
        ce_marked=False,
        device_ifu_description="Sample device instructions for use description",
        confidence_score=0.95,
        sources=[document.url for document in product_profile_documents],
        performance=Performance(
            speed=randint(50, 100),
            reliability=randint(50, 100),
        ),
        price=randint(1000, 5000),
    )
    await product_profile.save()
    logger.info(
        f"Analyzed product profile for product: {product_id}, including {number_of_documents} documents."
    )
    await lock.release()
    logger.info(f"Released lock for product {product_id}")
