from beanie import PydanticObjectId
from fastapi import HTTPException, status
from src.modules.product.claim_builder.model import (
    AnalyzeClaimBuilderProgress,
    ClaimBuilder,
)
from src.modules.product.claim_builder.schema import ClaimBuilderResponse


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


def filter_accepted_missing_elements_and_phrase_conflicts(
    claim_builder_response: ClaimBuilderResponse,
):
    claim_builder_response.missing_elements = [
        element
        for element in claim_builder_response.missing_elements
        if element.accepted is None
    ]
    claim_builder_response.phrase_conflicts = [
        conflict
        for conflict in claim_builder_response.phrase_conflicts
        if conflict.accepted_fix is None and conflict.rejected_reason is None
    ]
