from typing import Annotated
from fastapi import APIRouter, Depends

from src.celery.tasks.analyze_clinical_trial import analyze_clinical_trial_task
from src.modules.authentication.dependencies import get_current_user
from src.modules.product.clinical_trial.schema import ClinicalTrialResponse
from src.modules.product.clinical_trial.service import get_product_clinical_trials
from src.modules.product.dependencies import get_current_product
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
