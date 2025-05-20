from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from src.modules.authentication.dependencies import get_current_user
from src.modules.user.models import User
from src.celery.tasks.analyze_claim_builder import analyze_claim_builder_task
from src.modules.product.claim_builder.service import (
    get_analyze_claim_builder_progress,
    get_claim_builder,
)
from src.modules.product.claim_builder.schema import (
    AnalyzeClaimBuilderProgressResponse,
    ClaimBuilderResponse,
    Draft,
    UpdateClaimBuilderDraftRequest,
)
from src.modules.product.dependencies import (
    check_product_edit_allowed,
    get_current_product,
)
from src.modules.product.models import Product
from src.modules.product.claim_builder.model import (
    AnalyzeClaimBuilderProgress,
)


router = APIRouter()


@router.get("/result")
async def get_claim_builder_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> ClaimBuilderResponse:
    claim_builder = await get_claim_builder(product.id)
    profile_response = claim_builder.to_claim_builder_response(product)
    return profile_response


@router.get("/analyze-progress")
async def get_analyze_claim_builder_progress_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> AnalyzeClaimBuilderProgressResponse:
    analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
        str(product.id),
    )
    return analyze_claim_builder_progress.to_analyze_claim_builder_progress_response()


@router.post("/analyze")
async def analyze_claim_builder_handler(
    product: Annotated[Product, Depends(get_current_product)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    try:
        claim_builder = await get_claim_builder(product.id)
    except HTTPException as e:
        claim_builder = None
    if claim_builder and claim_builder.user_acceptance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after user acceptance.",
        )
    await AnalyzeClaimBuilderProgress.find(
        AnalyzeClaimBuilderProgress.product_id == str(product.id),
    ).delete_many()
    analyze_claim_builder_progress = AnalyzeClaimBuilderProgress(
        product_id=str(product.id),
        total_files=0,
        processed_files=0,
        updated_at=datetime.now(timezone.utc),
    )
    await analyze_claim_builder_progress.save()
    analyze_claim_builder_task.delay(str(product.id))


@router.put("/draft")
async def update_claim_builder_draft_handler(
    payload: UpdateClaimBuilderDraftRequest,
    product: Annotated[Product, Depends(get_current_product)],
    user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ClaimBuilderResponse:
    claim_builder = await get_claim_builder(product.id)
    if claim_builder.user_acceptance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after user acceptance.",
        )
    latest_draft = claim_builder.draft[-1]
    claim_builder.draft.append(
        Draft(
            version=latest_draft.version + 1,
            updated_at=datetime.now(timezone.utc),
            updated_by=user.email,
            content=payload.content,
        )
    )
    profile_response = claim_builder.to_claim_builder_response(product)
    return profile_response


@router.post("/accept")
async def accept_claim_builder_handler(
    product: Annotated[Product, Depends(get_current_product)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ClaimBuilderResponse:
    claim_builder = await get_claim_builder(product.id)
    claim_builder.user_acceptance = True
    await claim_builder.save()
    profile_response = claim_builder.to_claim_builder_response(product)
    return profile_response
