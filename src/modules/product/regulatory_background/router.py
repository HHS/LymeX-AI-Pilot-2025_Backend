from typing import Annotated, List
from fastapi import APIRouter, Depends, Form, File, UploadFile
import httpx

from src.modules.authentication.dependencies import get_current_user
from src.modules.product.analyzing_status import AnalyzingStatusResponse
from src.modules.product.product_profile.service import create_audit_record
from src.modules.product.regulatory_background.analyze_regulatory_background_progress import (
    get_analyze_regulatory_background_progress,
)
from src.modules.product.regulatory_background.model import (
    RegulatoryBackground,
)
from src.modules.product.regulatory_background.storage import (
    delete_regulatory_background_document,
    get_regulatory_background_documents,
    get_upload_regulatory_background_document_url,
)
from src.modules.user.models import User
from src.celery.tasks.analyze_regulatory_background import (
    analyze_regulatory_background_task,
)
from src.modules.product.service import upload_product_files
from src.modules.product.regulatory_background.schema import (
    AnalyzeRegulatoryBackgroundProgressResponse,
    AnalyzingStatus,
    RegulatoryBackgroundDocumentResponse,
    RegulatoryBackgroundResponse,
)
from src.modules.product.dependencies import (
    check_product_edit_allowed,
    get_current_product,
)
from src.modules.product.models import Product


router = APIRouter()


@router.get("/documents")
async def get_regulatory_background_document_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[RegulatoryBackgroundDocumentResponse]:
    regulatory_background_documents = await get_regulatory_background_documents(
        str(product.id),
    )
    return regulatory_background_documents


@router.get("/documents/upload-url")
async def get_upload_regulatory_background_document_url_handler(
    file_name: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> str:
    upload_url = await get_upload_regulatory_background_document_url(
        str(product.id),
        {
            "file_name": file_name,
            "author": current_user.email,
        },
    )
    return upload_url


@router.put("/documents/text-input")
async def upload_regulatory_background_text_input_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
    text: str | None = Form(None, description="Text input for the documents"),
    files: List[UploadFile] = File([], description="Files to upload"),
) -> None:
    # Upload text if provided
    if text:
        upload_url = await get_upload_regulatory_background_document_url(
            str(product.id),
            {
                "file_name": "TextInput.txt",
                "author": current_user.email,
            },
        )
        async with httpx.AsyncClient() as client:
            await client.put(
                upload_url,
                data=text,
                headers={"Content-Type": "text/plain"},
            )

    # Upload files if provided
    if files:
        await upload_product_files(str(product.id), files, current_user)

    await create_audit_record(
        product,
        current_user,
        "Upload product profile text input and files",
        {"text_provided": text is not None, "files_count": len(files)},
    )


@router.delete("/documents/{document_name}")
async def delete_regulatory_background_document_handler(
    document_name: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    await delete_regulatory_background_document(
        str(product.id),
        document_name,
    )
    await create_audit_record(
        product,
        current_user,
        "Delete product profile documents",
        {"document_name": document_name},
    )


@router.post("/analyze")
async def analyze_regulatory_background_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    analyze_regulatory_background_task.delay(
        product_id=str(product.id),
    )
    await create_audit_record(
        product,
        current_user,
        "Analyze regulatory background",
        {},
    )


@router.get("/analyze-progress")
async def get_analyze_regulatory_background_progress_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> AnalyzeRegulatoryBackgroundProgressResponse | AnalyzingStatusResponse:
    analyze_regulatory_background_progress = (
        await get_analyze_regulatory_background_progress(
            str(product.id),
        )
    )
    if not analyze_regulatory_background_progress:
        return AnalyzingStatusResponse(
            analyzing_status=AnalyzingStatus.IN_PROGRESS,
        )
    return analyze_regulatory_background_progress.to_analyze_regulatory_background_progress_response()


@router.get("/")
async def get_regulatory_background_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> RegulatoryBackgroundResponse | AnalyzingStatusResponse:
    regulatory_background = await RegulatoryBackground.find_one(
        RegulatoryBackground.product_id == str(product.id)
    )
    if not regulatory_background:
        return AnalyzingStatusResponse(
            analyzing_status=AnalyzingStatus.IN_PROGRESS,
        )
    return await regulatory_background.to_regulatory_background_response()
