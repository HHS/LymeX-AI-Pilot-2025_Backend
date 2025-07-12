from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
import httpx

from src.modules.authentication.dependencies import get_current_user
from src.modules.product.product_profile.analyze_product_profile_progress import (
    AnalyzeProductProfileProgress,
    get_analyze_product_profile_progress,
)
from src.modules.product.product_profile.storage import (
    delete_product_profile_document,
    get_product_profile_documents,
    get_upload_product_profile_document_url,
)
from src.modules.user.models import User
from src.celery.tasks.analyze_product_profile import analyze_product_profile_task
from src.modules.product.product_profile.service import (
    create_audit_record,
    get_product_profile,
)
from src.modules.product.product_profile.schema import (
    AnalyzeProductProfileProgressResponse,
    ProductProfileAnalysisResponse,
    ProductProfileAuditResponse,
    ProductProfileDocumentResponse,
    ProductProfileResponse,
    UpdateProductProfileRequest,
    UploadTextInputDocumentRequest,
)
from src.modules.product.dependencies import (
    check_product_edit_allowed,
    get_current_product,
)
from src.modules.product.models import Product
from src.modules.product.product_profile.model import (
    ProductProfile,
    ProductProfileAudit,
)


router = APIRouter()


@router.get("/")
async def get_product_profile_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> ProductProfileResponse:
    product_response = await product.to_product_response()
    product_profile = await get_product_profile(product.id)
    analyze_product_profile_progress = await get_analyze_product_profile_progress(
        product.id,
    )
    if not product_profile:
        return ProductProfileResponse(
            **product_response.model_dump(),
        )
    profile_response = product_profile.to_product_profile_response(
        product_response,
        analyze_product_profile_progress.to_analyze_product_profile_progress_response()
        if analyze_product_profile_progress
        else None,
    )
    return profile_response


@router.patch("/")
async def update_product_profile_handler(
    payload: UpdateProductProfileRequest,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ProductProfileResponse:
    product_response = await product.to_product_response()
    product_profile = await get_product_profile(product.id)
    if not product_profile:
        product_profile = ProductProfile(
            product_id=str(product.id),
            **payload.model_dump(),
        )
        await product_profile.insert()
    else:
        have_update = False
        possible_fields = [
            "description",
            "regulatory_classifications",
            "device_description",
            "features",
            "claims",
            "conflict_alerts",
        ]
        for field in possible_fields:
            value = getattr(payload, field)
            if value is not None:
                have_update = True
                setattr(product, field, value)
        if have_update:
            await product_profile.save()
    analyze_product_profile_progress = await get_analyze_product_profile_progress(
        product.id,
    )
    product_profile_response = product_profile.to_product_profile_response(
        product_response,
        analyze_product_profile_progress.to_analyze_product_profile_progress_response()
        if analyze_product_profile_progress
        else None,
    )
    await create_audit_record(
        product,
        current_user,
        "Update product profile",
        payload.model_dump(),
    )
    return product_profile_response


@router.get("/analyze-progress")
async def get_analyze_product_profile_progress_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> AnalyzeProductProfileProgressResponse:
    analyze_product_profile_progress = await get_analyze_product_profile_progress(
        product.id,
    )
    return (
        analyze_product_profile_progress.to_analyze_product_profile_progress_response()
        if analyze_product_profile_progress
        else None,
    )


@router.post("/analyze")
async def analyze_product_profile_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    await AnalyzeProductProfileProgress.find(
        AnalyzeProductProfileProgress.product_id == str(product.id),
    ).delete_many()
    analyze_product_profile_progress = AnalyzeProductProfileProgress(
        product_id=str(product.id),
        total_files=0,
        processed_files=0,
        updated_at=datetime.now(timezone.utc),
    )
    await analyze_product_profile_progress.save()
    await create_audit_record(
        product,
        current_user,
        "Analyze product profile",
        {},
    )
    analyze_product_profile_task.delay(str(product.id))


@router.get("/document")
async def get_product_profile_document_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[ProductProfileDocumentResponse]:
    product_profile_documents = await get_product_profile_documents(
        str(product.id),
    )
    return product_profile_documents


@router.get("/document/upload-url")
async def get_upload_product_profile_document_url_handler(
    file_name: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> str:
    upload_url = await get_upload_product_profile_document_url(
        str(product.id),
        {
            "file_name": file_name,
            "author": current_user.email,
        },
    )
    return upload_url


@router.put("/document/text-input")
async def upload_product_profile_text_input_handler(
    payload: UploadTextInputDocumentRequest,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    upload_url = await get_upload_product_profile_document_url(
        str(product.id),
        {
            "file_name": "TextInput.txt",
            "author": current_user.email,
        },
    )
    async with httpx.AsyncClient() as client:
        await client.put(
            upload_url,
            data=payload.text,
            headers={"Content-Type": "text/plain"},
        )
    await create_audit_record(
        product,
        current_user,
        "Upload product profile text input",
        payload.model_dump(),
    )


@router.delete("/document/{document_name}")
async def delete_product_profile_document_handler(
    document_name: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    await delete_product_profile_document(
        str(product.id),
        document_name,
    )
    await create_audit_record(
        product,
        current_user,
        "Delete product profile document",
        {"document_name": document_name},
    )


@router.get("/analysis")
async def get_product_profile_analysis_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> ProductProfileAnalysisResponse:
    product_profile = await get_product_profile(product.id)
    if not product_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product profile not found. Please run analysis first.",
        )
    analyze_product_profile_progress = await get_analyze_product_profile_progress(
        product.id,
    )
    analysis = product_profile.to_product_profile_analysis_response(
        product,
        analyze_product_profile_progress.to_analyze_product_profile_progress_response()
        if analyze_product_profile_progress
        else None,
    )
    return analysis


@router.get("/audit")
async def get_product_profile_audit_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[ProductProfileAuditResponse]:
    audits = await ProductProfileAudit.find(
        ProductProfileAudit.product_id == str(product.id),
        sort=[("timestamp", 1)],
    ).to_list()
    result = [
        audit.to_product_profile_audit_response(f"V{i}")
        for i, audit in enumerate(audits)
    ]
    return result[::-1]
