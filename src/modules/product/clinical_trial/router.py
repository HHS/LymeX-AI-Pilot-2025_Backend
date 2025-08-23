from typing import Annotated
from fastapi import APIRouter, Depends

from src.celery.tasks.analyze_clinical_trial import analyze_clinical_trial_task
from src.modules.authentication.dependencies import get_current_user
from src.modules.product.clinical_trial.schema import (
    ClinicalTrialDocumentResponse,
    ClinicalTrialResponse,
)
from src.modules.product.clinical_trial.service import get_product_clinical_trials
from src.modules.product.clinical_trial.storage import (
    TrialDocumentInfo,
    delete_clinical_trial_document,
    get_clinical_trial_documents,
    get_upload_clinical_trial_document_url,
)
from src.modules.product.dependencies import (
    check_product_edit_allowed,
    get_current_product,
)
from src.modules.product.models import Product
from src.modules.product.product_profile.service import create_audit_record
from src.modules.user.models import User


router = APIRouter()


@router.post("/analyze")
async def analyze_clinical_trial_handler(
    current_user: Annotated[User, Depends(get_current_user)],
    product: Annotated[Product, Depends(get_current_product)],
) -> None:
    analyze_clinical_trial_task.delay(
        product_id=str(product.id),
    )
    await create_audit_record(
        product,
        current_user,
        "Analyze clinical trial",
        {},
    )


@router.get("/")
async def get_product_clinical_trials_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[ClinicalTrialResponse]:
    clinical_trials = await get_product_clinical_trials(product.id)
    return [trial.to_clinical_trial_response() for trial in clinical_trials]


@router.get("/document")
async def get_clinical_trial_document_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[ClinicalTrialDocumentResponse]:
    clinical_trial_documents = await get_clinical_trial_documents(
        str(product.id),
    )
    return clinical_trial_documents


@router.get("/document/upload-url")
async def get_upload_clinical_trial_document_url_handler(
    file_name: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> str:
    upload_url = await get_upload_clinical_trial_document_url(
        str(product.id),
        TrialDocumentInfo(
            file_name=file_name,
            author=current_user.email,
        ),
    )
    return upload_url


@router.delete("/document/{document_name}")
async def delete_clinical_trial_document_handler(
    document_name: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
):
    await delete_clinical_trial_document(
        str(product.id),
        document_name,
    )
    await create_audit_record(
        product,
        current_user,
        "Delete clinical trial document",
        {"document_name": document_name},
    )
