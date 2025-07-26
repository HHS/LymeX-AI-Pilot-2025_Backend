from beanie import PydanticObjectId
from fastapi import HTTPException, status
from src.modules.product.claim_builder.model import (
    AnalyzeClaimBuilderProgress,
    ClaimBuilder,
)


async def get_analyze_claim_builder_progress(
    product_id: str,
) -> AnalyzeClaimBuilderProgress | None:
    analyze_claim_builder_progress = await AnalyzeClaimBuilderProgress.find_one(
        AnalyzeClaimBuilderProgress.product_id == str(product_id),
    )
    if not analyze_claim_builder_progress:
        return None
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


async def clone_claim_builder(
    product_id: str | PydanticObjectId,
    new_product_id: str | PydanticObjectId,
) -> None:
    claim_builder = await ClaimBuilder.find_one(
        ClaimBuilder.product_id == str(product_id),
    )
    if not claim_builder:
        return
    new_claim_builder = ClaimBuilder(
        **claim_builder.model_dump(exclude={"id", "product_id"}),
        product_id=str(new_product_id),
    )
    await new_claim_builder.insert()

    analyze_claim_builder_progress = await AnalyzeClaimBuilderProgress.find_one(
        AnalyzeClaimBuilderProgress.product_id == str(product_id),
    )
    if not analyze_claim_builder_progress:
        return
    new_analyze_claim_builder_progress = AnalyzeClaimBuilderProgress(
        **analyze_claim_builder_progress.model_dump(exclude={"id", "product_id"}),
        product_id=str(new_product_id),
    )
    await new_analyze_claim_builder_progress.insert()
