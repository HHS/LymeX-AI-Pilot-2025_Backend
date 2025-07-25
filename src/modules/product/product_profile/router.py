from datetime import datetime, timezone
from typing import Annotated, List
from fastapi import APIRouter, Depends, Form, File, UploadFile
import httpx

from src.modules.authentication.dependencies import get_current_user
from src.modules.authorization.dependencies import get_current_company
from src.modules.product.analyzing_status import AnalyzingStatusResponse
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
    get_product_documents,
)
from src.modules.company.models import Company
from src.modules.product.service import upload_product_files
from src.modules.product.product_profile.schema import (
    AnalyzeProductProfileProgressResponse,
    AnalyzingStatus,
    ProductProfileAnalysisResponse,
    ProductProfileAuditResponse,
    ProductProfileDocumentResponse,
    ProductProfileResponse,
    UpdateProductProfileRequest,
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


async def calculate_is_active_profile(product: Product) -> bool:
    """Calculate if the product is the active profile for the company"""
    try:
        # Get the company to check for active_product_id
        company = await Company.get(product.company_id)
        if company:
            # 0. HIGHEST PRECEDENCE: Check if company has an active product set
            if company.active_product_id:
                return str(product.id) == company.active_product_id
            else:
                # If no active product set, check if this is the most recently updated product
                # Get all products for this company
                from src.modules.product.models import Product

                products = await Product.find(
                    Product.company_id == product.company_id,
                ).to_list()

                if products:
                    # Find the most recently updated product
                    most_recent_product = max(products, key=lambda p: p.updated_at)
                    return product.id == most_recent_product.id
        return False
    except Exception as e:
        # If there's any error, default to False
        print(f"Error calculating is_active_profile for product {product.id}: {e}")
        return False


@router.get("/")
async def get_product_profile_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> ProductProfileResponse:
    product_response = await product.to_product_response()
    product_profile = await get_product_profile(product.id)
    analyze_product_profile_progress = await get_analyze_product_profile_progress(
        product.id,
    )

    # Get all documents for the product
    documents = await get_product_documents(str(product.id))

    # Get last 3 audit records
    audits = (
        await ProductProfileAudit.find(
            ProductProfileAudit.product_id == str(product.id),
            sort=[("timestamp", -1)],
        )
        .limit(3)
        .to_list()
    )
    latest_audits = [
        audit.to_product_profile_audit_response(f"V{len(audits) - i}")
        for i, audit in enumerate(audits)
    ]

    # Calculate is_active_profile
    is_active_profile = await calculate_is_active_profile(product)

    if not product_profile:
        # Exclude is_active_profile from product_response since we're passing it explicitly
        product_data = product_response.model_dump()
        product_data.pop("is_active_profile", None)

        return ProductProfileResponse(
            **product_data,
            documents=documents,
            latest_audits=latest_audits,
            is_active_profile=is_active_profile,
        )
    profile_response = await product_profile.to_product_profile_response(
        product_response,
        (
            analyze_product_profile_progress.to_analyze_product_profile_progress_response()
            if analyze_product_profile_progress
            else None
        ),
    )
    # Add documents and latest audits to the response
    profile_response.documents = documents
    profile_response.latest_audits = latest_audits
    profile_response.is_active_profile = is_active_profile
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
    product_profile_response = await product_profile.to_product_profile_response(
        product_response,
        (
            analyze_product_profile_progress.to_analyze_product_profile_progress_response()
            if analyze_product_profile_progress
            else None
        ),
    )
    await create_audit_record(
        product,
        current_user,
        "Update product profile",
        payload.model_dump(),
    )
    return product_profile_response


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
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
    text: str | None = Form(None, description="Text input for the document"),
    files: List[UploadFile] = File([], description="Files to upload"),
) -> None:
    # Upload text if provided
    if text:
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
        else None
    )


@router.get("/analysis")
async def get_product_profile_analysis_handler(
    product: Annotated[Product, Depends(get_current_product)],
    company: Annotated[Company, Depends(get_current_company)],
) -> ProductProfileAnalysisResponse | AnalyzingStatusResponse:
    product_profile = await get_product_profile(product.id)
    if not product_profile:
        return AnalyzingStatusResponse(
            analyzing_status=AnalyzingStatus.IN_PROGRESS,
        )
    analyze_product_profile_progress = await get_analyze_product_profile_progress(
        product.id,
    )
    analysis = await product_profile.to_product_profile_analysis_response(
        product,
        company,
        (
            analyze_product_profile_progress.to_analyze_product_profile_progress_response()
            if analyze_product_profile_progress
            else None
        ),
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
