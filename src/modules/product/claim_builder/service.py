from beanie import PydanticObjectId
from fastapi import HTTPException, status
from src.modules.product.claim_builder.model import (
    AnalyzeClaimBuilderProgress,
    ClaimBuilder,
)


async def get_analyze_claim_builder_progress(
    product_id: str,
) -> AnalyzeClaimBuilderProgress:
    analyze_claim_builder_progress = await AnalyzeClaimBuilderProgress.find_one(
        AnalyzeClaimBuilderProgress.product_id == product_id,
    )
    if not analyze_claim_builder_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analyze product profile progress not found",
        )
    return analyze_claim_builder_progress


async def get_claim_builder(
    product_id: str | PydanticObjectId,
) -> ClaimBuilder:
    claim_builder = await ClaimBuilder.find_one(
        ClaimBuilder.product_id == str(product_id),
    )
    if not claim_builder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim builder not found for this product.",
        )
    return claim_builder
