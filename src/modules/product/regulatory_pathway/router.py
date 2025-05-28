from typing import Annotated
from fastapi import APIRouter, Depends

from src.celery.tasks.analyze_regulatory_pathway import analyze_regulatory_pathway_task
from src.modules.product.regulatory_pathway.schema import RegulatoryPathwayResponse
from src.modules.product.regulatory_pathway.service import (
    get_product_regulatory_pathways,
)
from src.modules.product.dependencies import get_current_product
from src.modules.product.models import Product


router = APIRouter()


@router.post("/analyze")
async def analyze_regulatory_pathway_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> None:
    analyze_regulatory_pathway_task.delay(
        product_id=str(product.id),
    )


@router.get("/")
async def get_product_regulatory_pathways_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[RegulatoryPathwayResponse]:
    regulatory_pathways = await get_product_regulatory_pathways(product.id)
    return [pathway.to_regulatory_pathway_response() for pathway in regulatory_pathways]
