from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from src.celery.tasks.analyze_performance_testing import (
    analyze_performance_testing_task,
)
from src.modules.product.performance_testing.service import (
    create_performance_testing,
    get_performance_testing,
    get_product_performance_testings,
)
from src.modules.authentication.dependencies import get_current_user
from src.modules.product.performance_testing.schema import (
    CreatePerformanceTestingRequest,
    PerformanceTestingResponse,
    PerformanceTestingStatus,
    RejectedPerformanceTestingRequest,
)
from src.modules.product.product_profile.service import create_audit_record
from src.modules.user.models import User
from src.modules.product.dependencies import (
    check_product_edit_allowed,
    get_current_product,
)
from src.modules.product.models import Product


router = APIRouter()


@router.get("/")
async def get_product_performance_testings_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[PerformanceTestingResponse]:
    performance_testings = await get_product_performance_testings(
        product_id=product.id,
    )
    performance_testings = [
        pt.to_performance_testing_response() for pt in performance_testings
    ]
    return performance_testings


@router.post("/")
async def create_performance_testing_handler(
    payload: CreatePerformanceTestingRequest,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> PerformanceTestingResponse:
    performance_testing = await create_performance_testing(
        product_id=product.id,
        payload=payload,
        user_email=current_user.email,
    )
    await create_audit_record(
        product,
        current_user,
        "Create performance testing",
        {
            "performance_testing_id": performance_testing.id,
            "payload": payload.model_dump(),
        },
    )
    return performance_testing.to_performance_testing_response()


@router.get("/{performance_testing_id}")
async def get_performance_testing_handler(
    performance_testing_id: str,
    product: Annotated[Product, Depends(get_current_product)],
) -> PerformanceTestingResponse:
    performance_testing = await get_performance_testing(performance_testing_id)
    if not performance_testing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance testing not found.",
        )
    if performance_testing.product_id != str(product.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Performance testing does not belong to this product.",
        )
    return performance_testing.to_performance_testing_response()


@router.delete("/{performance_testing_id}")
async def delete_performance_testing_handler(
    performance_testing_id: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    performance_testing = await get_performance_testing(performance_testing_id)
    if not performance_testing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance testing not found.",
        )
    if performance_testing.product_id != str(product.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Performance testing does not belong to this product.",
        )
    await performance_testing.delete()
    await create_audit_record(
        product,
        current_user,
        "Delete performance testing",
        {
            "performance_testing_id": performance_testing.id,
        },
    )
    return


@router.post("/{performance_testing_id}/analyze")
async def analyze_performance_testing_handler(
    performance_testing_id: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    performance_testing = await get_performance_testing(performance_testing_id)
    if not performance_testing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance testing not found.",
        )
    if performance_testing.product_id != str(product.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Performance testing does not belong to this product.",
        )
    analyze_performance_testing_task.delay(performance_testing_id)
    await create_audit_record(
        product,
        current_user,
        "Analyze performance testing",
        {
            "performance_testing_id": performance_testing.id,
        },
    )
    return


@router.post("/{performance_testing_id}/accept")
async def accept_performance_testing_handler(
    performance_testing_id: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> PerformanceTestingResponse:
    performance_testing = await get_performance_testing(performance_testing_id)
    if not performance_testing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance testing not found.",
        )
    if performance_testing.product_id != str(product.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Performance testing does not belong to this product.",
        )
    if performance_testing.status != PerformanceTestingStatus.SUGGESTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Performance testing is not in a state that can be accepted.",
        )
    performance_testing.status = PerformanceTestingStatus.ACCEPTED
    await performance_testing.save()
    await create_audit_record(
        product,
        current_user,
        "Accept performance testing",
        {
            "performance_testing_id": performance_testing.id,
        },
    )
    return performance_testing.to_performance_testing_response()


@router.post("/{performance_testing_id}/reject")
async def reject_performance_testing_handler(
    payload: RejectedPerformanceTestingRequest,
    performance_testing_id: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> PerformanceTestingResponse:
    performance_testing = await get_performance_testing(performance_testing_id)
    if not performance_testing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance testing not found.",
        )
    if performance_testing.product_id != str(product.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Performance testing does not belong to this product.",
        )
    if performance_testing.status != PerformanceTestingStatus.SUGGESTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Performance testing is not in a state that can be rejected.",
        )
    performance_testing.status = PerformanceTestingStatus.REJECTED
    performance_testing.rejected_justification = payload.rejected_justification
    await performance_testing.save()
    await create_audit_record(
        product,
        current_user,
        "Reject performance testing",
        {
            "performance_testing_id": performance_testing.id,
            "rejected_justification": payload.rejected_justification,
        },
    )
    return performance_testing.to_performance_testing_response()
