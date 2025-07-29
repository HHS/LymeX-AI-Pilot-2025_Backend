from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from src.modules.authorization.dependencies import get_current_company
from src.modules.company.models import Company
from src.modules.product.product_profile.service import create_audit_record
from src.modules.product.version_control.service import snapshot_minor_version
from src.modules.authentication.dependencies import get_current_user
from src.modules.user.models import User
from src.celery.tasks.analyze_claim_builder import analyze_claim_builder_task
from src.modules.product.claim_builder.service import (
    get_analyze_claim_builder_progress,
    get_claim_builder,
)
from src.modules.product.claim_builder.schema import (
    AcceptPhraseConflictRequest,
    AnalyzeClaimBuilderProgressResponse,
    ClaimBuilderResponse,
    DecideMissingElementRequest,
    Draft,
    RejectClaimBuilderDraftRequest,
    RejectPhraseConflictRequest,
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
    company: Annotated[Company, Depends(get_current_company)],
    product: Annotated[Product, Depends(get_current_product)],
) -> ClaimBuilderResponse:
    claim_builder = await get_claim_builder(product.id)
    analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
        product.id,
    )
    claim_builder_response = claim_builder.to_claim_builder_response(
        product,
        company,
        analyze_claim_builder_progress,
    )
    claim_builder_response.missing_elements = [
        element
        for element in claim_builder_response.missing_elements
        if element.accepted is None
    ]
    return claim_builder_response


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
    current_user: Annotated[User, Depends(get_current_user)],
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
    await create_audit_record(
        product,
        current_user,
        "Unlock product",
        {},
    )
    analyze_claim_builder_task.delay(str(product.id))


@router.put("/draft")
async def update_claim_builder_draft_handler(
    payload: UpdateClaimBuilderDraftRequest,
    product: Annotated[Product, Depends(get_current_product)],
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ClaimBuilderResponse:
    claim_builder = await get_claim_builder(product.id)
    if claim_builder.user_acceptance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after user acceptance.",
        )
    if not claim_builder.draft[0].submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after submission.",
        )
    if claim_builder.draft[0].accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after acceptance.",
        )
    claim_builder.draft = [
        Draft(
            version=0,
            updated_at=datetime.now(timezone.utc),
            updated_by=user.email,
            content=payload.content,
            submitted=False,
            accepted=False,
        )
    ]
    await claim_builder.save()
    await snapshot_minor_version(
        claim_builder,
        "Update claim builder draft",
        user.email,
    )
    await create_audit_record(
        product,
        user,
        "Update claim builder draft",
        payload.model_dump(),
    )
    analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
        product.id,
    )
    claim_builder_response = claim_builder.to_claim_builder_response(
        product,
        company,
        analyze_claim_builder_progress,
    )
    claim_builder.missing_elements = [
        element
        for element in claim_builder.missing_elements
        if element.accepted is None
    ]
    return claim_builder_response


@router.post("/draft/submit")
async def submit_claim_builder_draft_handler(
    product: Annotated[Product, Depends(get_current_product)],
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ClaimBuilderResponse:
    claim_builder = await get_claim_builder(product.id)
    if claim_builder.user_acceptance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after user acceptance.",
        )
    if claim_builder.draft[0].submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Draft already submitted.",
        )
    if claim_builder.draft[0].accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after acceptance.",
        )
    claim_builder.draft[0].submitted = True
    claim_builder.draft[0].reject_message = None
    claim_builder.draft[0].updated_by = user.email
    claim_builder.draft[0].updated_at = datetime.now(timezone.utc)
    await claim_builder.save()
    await snapshot_minor_version(
        claim_builder,
        "Submit claim builder draft",
        user.email,
    )
    await create_audit_record(
        product,
        user,
        "Submit claim builder draft",
        {},
    )
    analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
        product.id,
    )
    claim_builder_response = claim_builder.to_claim_builder_response(
        product,
        company,
        analyze_claim_builder_progress,
    )
    claim_builder.missing_elements = [
        element
        for element in claim_builder.missing_elements
        if element.accepted is None
    ]
    return claim_builder_response


@router.post("/draft/reject")
async def reject_claim_builder_draft_handler(
    payload: RejectClaimBuilderDraftRequest,
    product: Annotated[Product, Depends(get_current_product)],
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ClaimBuilderResponse:
    claim_builder = await get_claim_builder(product.id)
    if claim_builder.user_acceptance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after user acceptance.",
        )
    if not claim_builder.draft[0].submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Draft must be submitted before rejection.",
        )
    if claim_builder.draft[0].accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after acceptance.",
        )
    claim_builder.draft[0].submitted = False
    claim_builder.draft[0].reject_message = payload.reject_message
    claim_builder.draft[0].updated_by = user.email
    claim_builder.draft[0].updated_at = datetime.now(timezone.utc)
    await claim_builder.save()
    await snapshot_minor_version(
        claim_builder,
        "Reject claim builder draft",
        user.email,
    )
    await create_audit_record(
        product,
        user,
        "Reject claim builder draft",
        payload.model_dump(),
    )
    analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
        product.id,
    )
    claim_builder_response = claim_builder.to_claim_builder_response(
        product,
        company,
        analyze_claim_builder_progress,
    )
    claim_builder.missing_elements = [
        element
        for element in claim_builder.missing_elements
        if element.accepted is None
    ]
    return claim_builder_response


@router.post("/draft/accept")
async def accept_claim_builder_draft_handler(
    product: Annotated[Product, Depends(get_current_product)],
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ClaimBuilderResponse:
    claim_builder = await get_claim_builder(product.id)
    if claim_builder.user_acceptance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after user acceptance.",
        )
    if not claim_builder.draft[0].submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Draft must be submitted before acceptance.",
        )
    if claim_builder.draft[0].accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after acceptance.",
        )
    claim_builder.draft[0].submitted = False
    claim_builder.draft[0].accepted = True
    claim_builder.draft[0].updated_by = user.email
    claim_builder.draft[0].updated_at = datetime.now(timezone.utc)
    await claim_builder.save()
    await snapshot_minor_version(
        claim_builder,
        "Accept claim builder draft",
        user.email,
    )
    await create_audit_record(
        product,
        user,
        "Accept claim builder draft",
        {},
    )
    analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
        product.id,
    )
    claim_builder_response = claim_builder.to_claim_builder_response(
        product,
        company,
        analyze_claim_builder_progress,
    )
    claim_builder_response.missing_elements = [
        element
        for element in claim_builder_response.missing_elements
        if element.accepted is None
    ]
    return claim_builder_response


@router.post("/missing-element/decide")
async def decide_missing_element_handler(
    payload: DecideMissingElementRequest,
    product: Annotated[Product, Depends(get_current_product)],
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ClaimBuilderResponse:
    claim_builder = await get_claim_builder(product.id)
    if claim_builder.user_acceptance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after user acceptance.",
        )
    # No need to find as id is the same as index
    claim_builder.missing_elements[payload.id - 1].accepted = payload.accepted
    await claim_builder.save()
    await snapshot_minor_version(
        claim_builder,
        (
            f"Accept missing element {payload.id}"
            if payload.accepted
            else f"Reject missing element {payload.id}"
        ),
        user.email,
    )
    await create_audit_record(
        product,
        user,
        ("Accept missing element" if payload.accepted else "Reject missing element"),
        payload.model_dump(),
    )
    analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
        product.id,
    )
    claim_builder_response = claim_builder.to_claim_builder_response(
        product,
        company,
        analyze_claim_builder_progress,
    )
    claim_builder_response.missing_elements = [
        element
        for element in claim_builder_response.missing_elements
        if element.accepted is None
    ]
    return claim_builder_response


@router.post("/phrase-conflict/accept")
async def accept_phrase_conflict_handler(
    payload: AcceptPhraseConflictRequest,
    product: Annotated[Product, Depends(get_current_product)],
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ClaimBuilderResponse:
    claim_builder = await get_claim_builder(product.id)
    if claim_builder.user_acceptance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after user acceptance.",
        )
    # No need to find as id is the same as index
    claim_builder.phrase_conflicts[payload.id].accepted_fix = payload.accepted_fix
    await claim_builder.save()
    await snapshot_minor_version(
        claim_builder,
        f"Accept phrase conflict {payload.id}",
        user.email,
    )
    await create_audit_record(
        product,
        user,
        "Accept phrase conflict",
        payload.model_dump(),
    )
    analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
        product.id,
    )
    claim_builder_response = claim_builder.to_claim_builder_response(
        product,
        company,
        analyze_claim_builder_progress,
    )
    claim_builder_response.missing_elements = [
        element
        for element in claim_builder_response.missing_elements
        if element.accepted is None
    ]
    return claim_builder_response


@router.post("/phrase-conflict/accept-all")
async def accept_all_phrase_conflict_handler(
    product: Annotated[Product, Depends(get_current_product)],
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ClaimBuilderResponse:
    claim_builder = await get_claim_builder(product.id)
    if claim_builder.user_acceptance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after user acceptance.",
        )
    for conflict in claim_builder.phrase_conflicts:
        if conflict.rejected_reason is None:
            conflict.accepted_fix = conflict.suggested_fix
    await claim_builder.save()
    await snapshot_minor_version(
        claim_builder,
        "Accept all phrase conflicts",
        user.email,
    )
    await create_audit_record(
        product,
        user,
        "Accept all phrase conflicts",
        {},
    )
    analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
        product.id,
    )
    claim_builder_response = claim_builder.to_claim_builder_response(
        product,
        company,
        analyze_claim_builder_progress,
    )
    claim_builder_response.missing_elements = [
        element
        for element in claim_builder_response.missing_elements
        if element.accepted is None
    ]
    return claim_builder_response


@router.post("/phrase-conflict/reject")
async def reject_phrase_conflict_handler(
    payload: RejectPhraseConflictRequest,
    product: Annotated[Product, Depends(get_current_product)],
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ClaimBuilderResponse:
    claim_builder = await get_claim_builder(product.id)
    if claim_builder.user_acceptance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update draft after user acceptance.",
        )
    # No need to find as id is the same as index
    claim_builder.phrase_conflicts[payload.id].rejected_reason = payload.rejected_reason
    await claim_builder.save()
    await snapshot_minor_version(
        claim_builder,
        f"Reject phrase conflict {payload.id}",
        user.email,
    )
    await create_audit_record(
        product,
        user,
        "Reject phrase conflict",
        payload.model_dump,
    )
    analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
        product.id,
    )
    claim_builder_response = claim_builder.to_claim_builder_response(
        product,
        company,
        analyze_claim_builder_progress,
    )
    claim_builder_response.missing_elements = [
        element
        for element in claim_builder_response.missing_elements
        if element.accepted is None
    ]
    return claim_builder_response


@router.post("/accept")
async def accept_claim_builder_handler(
    product: Annotated[Product, Depends(get_current_product)],
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ClaimBuilderResponse:
    claim_builder = await get_claim_builder(product.id)
    claim_builder.user_acceptance = True
    await claim_builder.save()
    await create_audit_record(
        product,
        user,
        "Accept claim builder",
        {},
    )
    analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
        product.id,
    )
    claim_builder_response = claim_builder.to_claim_builder_response(
        product,
        company,
        analyze_claim_builder_progress,
    )
    claim_builder_response.missing_elements = [
        element
        for element in claim_builder_response.missing_elements
        if element.accepted is None
    ]
    return claim_builder_response
