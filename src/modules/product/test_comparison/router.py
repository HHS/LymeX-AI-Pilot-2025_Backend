from typing import Annotated
from fastapi import APIRouter, Depends

from src.celery.tasks.analyze_test_comparison import analyze_test_comparison_task
from src.modules.authentication.dependencies import get_current_user
from src.modules.product.dependencies import (
    get_current_product,
)
from src.modules.product.models import Product
from src.modules.product.product_profile.service import create_audit_record
from src.modules.product.test_comparison.schema import TestComparisonResponse
from src.modules.product.test_comparison.service import (
    get_product_all_test_comparison,
    get_product_test_comparison,
)
from src.modules.user.models import User


router = APIRouter()


@router.get("/")
async def get_product_all_test_comparison_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[TestComparisonResponse]:
    test_comparisons = await get_product_all_test_comparison(product.id)
    return [
        test_comparison.to_test_comparison_response()
        for test_comparison in test_comparisons
    ]


@router.get("/{comparison_id}")
async def get_product_test_comparison_handler(
    comparison_id: str,
    product: Annotated[Product, Depends(get_current_product)],
) -> TestComparisonResponse:
    test_comparison = await get_product_test_comparison(comparison_id, product.id)
    return test_comparison.to_test_comparison_response()


@router.post("/")
async def analyze_product_test_comparison_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    analyze_test_comparison_task.delay(
        product_id=str(product.id),
    )
    await create_audit_record(
        product,
        current_user,
        "Analyze product test comparison",
        {},
    )


@router.post("/analyze")
async def analyze_product_test_comparison_handler_2(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    analyze_test_comparison_task.delay(
        product_id=str(product.id),
    )
    await create_audit_record(
        product,
        current_user,
        "Analyze product test comparison",
        {},
    )


@router.post("/{comparison_id}/accept/{suggestion_id}")
async def accept_test_comparison_suggestion_handler(
    comparison_id: str,
    suggestion_id: int,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    test_comparison = await get_product_test_comparison(comparison_id, product.id)
    test_comparison.identified_gaps_and_suggested_adjustments[
        suggestion_id
    ].accepted = True
    await test_comparison.save()
    await create_audit_record(
        product,
        current_user,
        "Accept test comparison suggestion",
        {
            "comparison_id": comparison_id,
            "suggestion_id": suggestion_id,
        },
    )


@router.post("/{comparison_id}/reject/{suggestion_id}")
async def reject_test_comparison_suggestion_handler(
    comparison_id: str,
    suggestion_id: int,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    test_comparison = await get_product_test_comparison(comparison_id, product.id)
    test_comparison.identified_gaps_and_suggested_adjustments[
        suggestion_id
    ].accepted = False
    await test_comparison.save()
    await create_audit_record(
        product,
        current_user,
        "Reject test comparison suggestion",
        {
            "comparison_id": comparison_id,
            "suggestion_id": suggestion_id,
        },
    )
