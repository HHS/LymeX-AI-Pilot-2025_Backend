from typing import Annotated
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from src.celery.tasks.analyze_checklist import analyze_checklist_task
from src.modules.authentication.dependencies import get_current_user
from src.modules.product.analyzing_status import (
    AnalyzingStatus,
    AnalyzingStatusResponse,
)
from src.modules.product.checklist.analyze_checklist_progress import (
    get_analyze_checklist_progress,
)
from src.modules.product.checklist.service import (
    upload_checklist_file,
    get_checklist_documents,
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


@router.post("/upload-file")
async def upload_checklist_image(
    product: Annotated[Product, Depends(get_current_product)],
    question_number: str = Query(..., description="Question number to upload file for"),
    file: UploadFile | None = File(None),
):
    """Upload a checklist file for a specific question (file is optional)"""
    if not file:
        return {"message": "No file uploaded"}
    try:
        return await upload_checklist_file(str(product.id), question_number, file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def get_checklist_documents_endpoint(
    product: Annotated[Product, Depends(get_current_product)],
    question_number: str = Query(
        None, description="Optional question ID to filter documents"
    ),
):
    """Get all checklist documents for a product, optionally filtered by question"""
    try:
        return await get_checklist_documents(str(product.id), question_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
