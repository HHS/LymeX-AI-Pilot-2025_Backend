from typing import Annotated
from fastapi import APIRouter, Depends

from src.celery.tasks.analyze_checklist import analyze_checklist_task
from src.modules.authentication.dependencies import get_current_user
from src.modules.product.analyzing_status import (
    AnalyzingStatus,
    AnalyzingStatusResponse,
)
from src.modules.product.checklist.analyze_checklist_progress import (
    get_analyze_checklist_progress,
)
from src.modules.product.checklist.model import Checklist
from src.modules.product.checklist.schema import (
    AnalyzeChecklistProgressResponse,
    ChecklistResponse,
)
from src.modules.product.dependencies import get_current_product
from src.modules.product.models import Product
from src.modules.product.product_profile.service import create_audit_record
from src.modules.user.models import User


router = APIRouter()


@router.post("/analyze")
async def analyze_checklist_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    analyze_checklist_task.delay(
        product_id=str(product.id),
    )
    await create_audit_record(
        product,
        current_user,
        "Analyze checklist",
        {},
    )


@router.get("/analyze-progress")
async def get_analyze_checklist_progress_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> AnalyzeChecklistProgressResponse | AnalyzingStatusResponse:
    analyze_checklist_progress = await get_analyze_checklist_progress(
        str(product.id),
    )
    if not analyze_checklist_progress:
        return AnalyzingStatusResponse(
            analyzing_status=AnalyzingStatus.IN_PROGRESS,
        )
    return analyze_checklist_progress.to_analyze_checklist_progress_response()


@router.get("/")
async def get_checklist_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> ChecklistResponse | AnalyzingStatusResponse:
    checklist = await Checklist.find_one(Checklist.product_id == str(product.id))
    if not checklist:
        return AnalyzingStatusResponse(
            analyzing_status=AnalyzingStatus.IN_PROGRESS,
        )
    analyze_checklist_progress = await get_analyze_checklist_progress(
        product.id,
    )
    return checklist.to_checklist_response(
        product=product,
        analyze_progress=(
            analyze_checklist_progress.to_analyze_checklist_progress_response()
            if analyze_checklist_progress
            else None
        ),
    )
