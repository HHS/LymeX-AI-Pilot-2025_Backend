import asyncio
from fastapi import HTTPException
from loguru import logger
from src.celery.worker import celery
from src.celery.tasks.base import BaseTask
from src.infrastructure.redis import redis_client
from src.modules.product.regulatory_pathway.model import RegulatoryPathway
from src.modules.product.regulatory_pathway.schema import (
    AlternativePathway,
    RegulatoryPathwayJustification,
)


@celery.task(
    base=BaseTask,
    name="src.celery.tasks.analyze_regulatory_pathway",
)
def analyze_regulatory_pathway_task(
    product_id: str,
) -> None:
    logger.info(f"Analyzing for product_id: {product_id}")
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            analyze_regulatory_pathway_task_async(
                product_id,
            )
        )
    except HTTPException as e:
        logger.error(f"Failed analyze: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(500, "Internal Server Error") from e


async def analyze_regulatory_pathway_task_async(
    product_id: str,
) -> None:
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzeRegulatoryPathway:AnalyzeLock:{product_id}",
        timeout=100,
    )
    lock_acquired = await lock.acquire(blocking=False)
    if not lock_acquired:
        logger.info(
            f"Lock already acquired for test comparison {product_id}. Skipping analysis."
        )
        return
    regulatory_pathway = RegulatoryPathway(
        product_id=product_id,
        recommended_pathway="510(k)",
        confident_score=85,
        description="The product is classified under Class II and requires a 510(k) submission.",
        estimated_time_days=90,
        alternative_pathways=[
            AlternativePathway(
                name="De Novo Classification",
                confident_score=25,
            ),
            AlternativePathway(
                name="Premarket Approval (PMA)",
                confident_score=15,
            ),
        ],
        justifications=[
            RegulatoryPathwayJustification(
                title="Product Classification",
                content="Class II medical device with substantial equivalence to predicate devices",
            ),
            RegulatoryPathwayJustification(
                title="Risk Assessment",
                content="Low to moderate risk based on device characteristics and intended use",
            ),
        ],
        supporting_documents=[
            "https://example.com/supporting_document_1.pdf",
            "https://example.com/supporting_document_2.pdf",
        ],
    )
    await RegulatoryPathway.find(
        RegulatoryPathway.product_id == product_id,
    ).delete_many()
    await regulatory_pathway.save()

    logger.info(f"Regulatory pathway analysis completed for product_id: {product_id}")
    await lock.release()
    logger.info(f"Released lock for regulatory pathway {product_id}.")
