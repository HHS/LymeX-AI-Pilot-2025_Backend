from typing import Annotated
from fastapi import APIRouter, Depends
from beanie.operators import Set

from src.modules.authorization.dependencies import get_current_company
from src.modules.company.models import Company
from src.modules.product.claim_builder.model import ClaimBuilder
from src.modules.product.claim_builder.service import (
    get_analyze_claim_builder_progress,
    get_claim_builder,
)
from src.modules.product.claim_builder.schema import ClaimBuilderResponse
from src.modules.authentication.dependencies import get_current_user
from src.modules.product.product_profile.service import create_audit_record
from src.modules.user.models import User
from src.modules.product.version_control.service import (
    get_product_version_control,
    get_version_data,
    promote_major_version,
    snapshot_minor_version,
)
from src.modules.product.version_control.schema import (
    ProductVersionControlResponse,
    ResetToVersionRequest,
)
from src.modules.product.dependencies import (
    check_product_edit_allowed,
    get_current_product,
)
from src.modules.product.models import Product


router = APIRouter()


@router.get("/")
async def get_product_profile_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[ProductVersionControlResponse]:
    product_version_controls = await get_product_version_control(str(product.id))
    if not product_version_controls:
        return []
    latest_version = product_version_controls[0]
    product_version_controls = [
        product_version_control.to_product_version_control_response(
            product_version_control.major_version == latest_version.major_version
            and product_version_control.minor_version == latest_version.minor_version
        )
        for product_version_control in product_version_controls
    ]
    return product_version_controls


@router.post("/promote-major-version")
async def promote_major_version_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ProductVersionControlResponse:
    new_version = await promote_major_version(
        product_id=str(product.id),
        created_by=current_user.email,
    )
    await create_audit_record(
        product,
        current_user,
        "Promote major version",
        {
            "new_major_version": new_version.major_version,
            "new_minor_version": new_version.minor_version,
        },
    )
    return new_version.to_product_version_control_response(
        is_current_version=True,
    )


@router.post("/reset-to-version")
async def reset_to_version_handler(
    payload: ResetToVersionRequest,
    product: Annotated[Product, Depends(get_current_product)],
    user: Annotated[User, Depends(get_current_user)],
    company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ClaimBuilderResponse:
    major_version, minor_version = (
        payload.version.replace("v", "").replace("V", "").split(".")
    )
    claim_builder = await get_version_data(
        product_id=str(product.id),
        major_version=major_version,
        minor_version=minor_version,
    )
    current_claim_builder = await get_claim_builder(
        product_id=product.id,
    )
    if not current_claim_builder:
        current_claim_builder = ClaimBuilder(**claim_builder.model_dump())
        await current_claim_builder.save()
    else:
        current_claim_builder = await current_claim_builder.update(
            Set(claim_builder.model_dump(exclude_unset=True))
        )
    await snapshot_minor_version(
        current_claim_builder,
        f"Reset to version {payload.version}",
        user.email,
    )
    await create_audit_record(
        product,
        user,
        "Reset to version",
        {
            "version": payload.version,
            "major_version": major_version,
            "minor_version": minor_version,
        },
    )
    analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
        product.id,
    )
    return current_claim_builder.to_claim_builder_response(
        product,
        company,
        analyze_claim_builder_progress,
    )
