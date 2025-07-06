from typing import Annotated
from fastapi import APIRouter, Depends

from src.celery.tasks.analyze_regulatory_pathway import analyze_regulatory_pathway_task
from src.modules.authentication.dependencies import get_current_user
from src.modules.product.product_profile.service import create_audit_record
from src.modules.product.regulatory_pathway.schema import (
    AnalyzeRegulatoryPathwayProgressResponse,
    RegulatoryPathwayResponse,
)
from src.modules.product.regulatory_pathway.service import (
    get_analyze_regulatory_pathway_progress,
    get_product_regulatory_pathways,
)
from src.modules.product.dependencies import get_current_product
from src.modules.product.models import Product
from src.modules.user.models import User


router = APIRouter()


@router.post("/analyze")
async def analyze_regulatory_pathway_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    analyze_regulatory_pathway_task.delay(
        product_id=str(product.id),
    )
    await create_audit_record(
        product.id,
        current_user,
        "Analyze regulatory pathway",
        {},
    )


@router.get("/analyze-progress")
async def get_analyze_regulatory_pathway_progress_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> AnalyzeRegulatoryPathwayProgressResponse:
    analyze_regulatory_pathway_progress = await get_analyze_regulatory_pathway_progress(
        str(product.id),
    )
    return analyze_regulatory_pathway_progress.to_analyze_regulatory_pathway_progress_response()


@router.get("/")
async def get_product_regulatory_pathways_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[RegulatoryPathwayResponse]:
    regulatory_pathways = await get_product_regulatory_pathways(product.id)
    return [pathway.to_regulatory_pathway_response() for pathway in regulatory_pathways]
