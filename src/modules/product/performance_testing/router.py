from typing import Annotated
from fastapi import APIRouter, Depends
import httpx

from src.celery.tasks.analyze_performance_testing import (
    analyze_performance_testing_task,
)
from src.modules.authentication.dependencies import get_current_user
from src.modules.product.performance_testing.storage import (
    TestingDocumentInfo,
    delete_performance_testing_document,
    get_performance_testing_documents,
    get_upload_performance_testing_document_url,
)
from src.modules.product.product_profile.service import create_audit_record
from src.modules.product.performance_testing.schema import (
    AnalyzePerformanceTestingProgressResponse,
    PerformanceTestingDocumentResponse,
    PerformanceTestingResponse,
    UploadTextInputDocumentRequest,
)
from src.modules.product.performance_testing.service import (
    get_analyze_performance_testing_progress,
    get_product_performance_testings,
)
from src.modules.product.dependencies import (
    check_product_edit_allowed,
    get_current_product,
)
from src.modules.product.models import Product
from src.modules.user.models import User


router = APIRouter()


@router.post("/analyze")
async def analyze_performance_testing_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    analyze_performance_testing_task.delay(
        product_id=str(product.id),
    )
    await create_audit_record(
        product,
        current_user,
        "Analyze performance testing",
        {},
    )


@router.get("/analyze-progress")
async def get_analyze_performance_testing_progress_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> AnalyzePerformanceTestingProgressResponse:
    analyze_performance_testing_progress = (
        await get_analyze_performance_testing_progress(
            str(product.id),
        )
    )
    return analyze_performance_testing_progress.to_analyze_performance_testing_progress_response()


@router.get("/")
async def get_product_performance_testings_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[PerformanceTestingResponse]:
    performance_testings = await get_product_performance_testings(product.id)
    return [
        testing.to_performance_testing_response() for testing in performance_testings
    ]


@router.get("/document")
async def get_performance_testing_document_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[PerformanceTestingDocumentResponse]:
    performance_testing_documents = await get_performance_testing_documents(
        str(product.id),
    )
    return performance_testing_documents


@router.get("/document/upload-url")
async def get_upload_performance_testing_document_url_handler(
    file_name: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> str:
    upload_url = await get_upload_performance_testing_document_url(
        str(product.id),
        TestingDocumentInfo(
            file_name=file_name,
            author=current_user.email,
        ),
    )
    return upload_url


@router.put("/document/text-input")
async def upload_performance_testing_text_input_handler(
    payload: UploadTextInputDocumentRequest,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    upload_url = await get_upload_performance_testing_document_url(
        str(product.id),
        TestingDocumentInfo(
            file_name="TextInput.txt",
            author=current_user.email,
        ),
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
        "Upload performance testing text input",
        payload.model_dump(),
    )


@router.delete("/document/{document_name}")
async def delete_performance_testing_document_handler(
    document_name: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
):
    await delete_performance_testing_document(
        str(product.id),
        document_name,
    )
    await create_audit_record(
        product,
        current_user,
        "Delete performance testing document",
        {"document_name": document_name},
    )
