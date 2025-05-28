from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from src.celery.tasks.analyze_test_comparison import analyze_test_comparison_task
from src.modules.authentication.dependencies import get_current_user
from src.modules.product.dependencies import (
    check_product_edit_allowed,
    get_current_product,
)
from src.modules.product.models import Product
from src.modules.product.test_comparison.model import (
    TestComparison,
    TestComparisonNote,
)
from src.modules.product.test_comparison.schema import (
    CreateTestComparisonNoteRequest,
    GetTestComparisonNoteDocumentUrlsResponse,
    TestComparisonNoteResponse,
    UploadTestComparisonNoteDocumentUrlResponse,
)
from src.modules.product.test_comparison.service import (
    get_product_test_comparison,
    get_product_test_comparison_note,
)
from src.modules.product.test_comparison.storage import (
    get_test_comparison_note_document_urls,
    get_upload_test_comparison_note_document_url,
)
from src.modules.user.models import User


router = APIRouter()


@router.get("/")
async def get_product_test_comparison_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> TestComparison:
    test_comparison = await get_product_test_comparison(product.id)
    if not test_comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test comparison data not found for the product. Please analyze the product first.",
        )
    return test_comparison.to_test_comparison_response()


@router.post("/")
async def analyze_product_test_comparison_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> None:
    analyze_test_comparison_task.delay(
        product_id=str(product.id),
    )


@router.get("/note")
async def get_test_comparison_note_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> TestComparisonNoteResponse:
    test_comparison_note = await get_product_test_comparison_note(product.id)
    if not test_comparison_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test comparison note not found for the product.",
        )
    return test_comparison_note.to_test_comparison_note_response()


@router.put("/note")
async def create_test_comparison_note_handler(
    payload: CreateTestComparisonNoteRequest,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> TestComparisonNoteResponse:
    test_comparison_note = await get_product_test_comparison_note(product.id)
    if not test_comparison_note:
        test_comparison_note = TestComparisonNote(
            product_id=str(product.id),
            note=payload.note,
            updated_at=datetime.now(timezone.utc),
            updated_by=current_user.email,
        )
    else:
        test_comparison_note.note = payload.note
        test_comparison_note.updated_at = datetime.now(timezone.utc)
        test_comparison_note.updated_by = current_user.email
    await test_comparison_note.save()
    return test_comparison_note.to_test_comparison_note_response()


@router.get("/note/upload-document-url")
async def get_test_comparison_note_upload_document_url_handler(
    file_name: str,
    product: Annotated[Product, Depends(get_current_product)],
) -> UploadTestComparisonNoteDocumentUrlResponse:
    upload_test_comparison_note_document_url = (
        await get_upload_test_comparison_note_document_url(
            product_id=product.id,
            file_name=file_name,
        )
    )
    return UploadTestComparisonNoteDocumentUrlResponse(
        upload_url=upload_test_comparison_note_document_url
    )


@router.get("/note/document-urls")
async def get_test_comparison_note_document_urls_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> GetTestComparisonNoteDocumentUrlsResponse:
    test_comparison_note_document_urls = await get_test_comparison_note_document_urls(
        product_id=product.id,
    )
    return GetTestComparisonNoteDocumentUrlsResponse(
        document_urls=test_comparison_note_document_urls
    )
