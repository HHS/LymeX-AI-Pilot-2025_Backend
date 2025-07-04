from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends

from src.modules.product.product_profile.service import (
    create_audit_record,
    delete_product_profile,
)
from src.modules.product.competitive_analysis.service import (
    delete_product_competitive_analysis,
)
from src.modules.product.dependencies import (
    check_product_edit_allowed,
    get_current_product,
)
from src.modules.product.models import Product
from src.modules.product.storage import (
    get_update_product_avatar_url,
)
from src.modules.product.service import (
    create_product,
    get_products,
)
from src.modules.product.schema import (
    CreateProductRequest,
    ProductResponse,
    UpdateAvatarUrlResponse,
    UpdateProductRequest,
)
from src.modules.authentication.dependencies import get_current_user
from src.modules.authorization.dependencies import (
    RequireCompanyRole,
    get_current_company,
)
from src.modules.authorization.roles import CompanyRoles
from src.modules.company.models import Company
from src.modules.user.models import User

from src.modules.product.competitive_analysis.router import (
    router as competitive_analysis_router,
)
from src.modules.product.product_profile.router import (
    router as product_profile_router,
)
from src.modules.product.claim_builder.router import (
    router as claim_builder_router,
)
from src.modules.product.version_control.router import (
    router as version_control_router,
)
from src.modules.product.performance_testing.router import (
    router as performance_testing_router,
)
from src.modules.product.test_comparison.router import (
    router as test_comparison_router,
)
from src.modules.product.clinical_trial.router import (
    router as clinical_trial_router,
)
from src.modules.product.regulatory_pathway.router import (
    router as regulatory_pathway_router,
)
from src.modules.product.feature_status.router import (
    router as feature_status_router,
)
from src.modules.product.milestone_planning.router import (
    router as milestone_planning_router,
)
from src.modules.product.cost_estimation.router import (
    router as cost_estimation_router,
)
from src.modules.product.review_program.router import (
    router as review_program_router,
)
from src.modules.product.final_regulatory_report.router import (
    router as final_regulatory_report_router,
)
from src.modules.product.custom_test_plan.router import (
    router as custom_test_plan_router,
)
from src.modules.product.regulatory_background.router import (
    router as regulatory_background_router,
)
from src.modules.checklist.router import (
    router as checklist_router,
)

router = APIRouter()


@router.get("/")
async def get_products_handler(
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.VIEWER))],
) -> list[ProductResponse]:
    products = await get_products(current_company)
    return [await product.to_product_response() for product in products]


@router.post("/")
async def create_product_handler(
    payload: CreateProductRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> ProductResponse:
    created_product = await create_product(payload, current_user, current_company)
    created_product = await created_product.to_product_response()
    await create_audit_record(
        created_product.id,
        current_user,
        "Create product",
        payload.model_dump(),
    )
    return created_product


@router.get("/{product_id}")
async def get_product_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> ProductResponse:
    product_response = await product.to_product_response()
    return product_response


@router.patch("/{product_id}")
async def update_product_handler(
    product: Annotated[Product, Depends(get_current_product)],
    payload: UpdateProductRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ProductResponse:
    have_update = False
    possible_fields = [
        "code",
        "name",
        "model",
        "revision",
        "category",
        "intend_use",
        "patient_contact",
    ]
    for field in possible_fields:
        value = getattr(payload, field)
        if value is None:
            continue
        have_update = True
        setattr(product, field, value)
    if have_update:
        product.updated_by = str(current_user.id)
        product.updated_at = datetime.now(timezone.utc)
        await product.save()
    await create_audit_record(
        product.id,
        current_user,
        "Update product",
        payload.model_dump(),
    )
    product_response = await product.to_product_response()
    return product_response


@router.get("/{product_id}/update-avatar-url")
async def get_update_avatar_url_handler(
    product: Annotated[Product, Depends(get_current_product)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> UpdateAvatarUrlResponse:
    avatar_url = await get_update_product_avatar_url(
        product.id,
    )
    return {
        "url": avatar_url,
    }


@router.delete("/{product_id}")
async def delete_product_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    await delete_product_competitive_analysis(
        str(product.id),
    )
    await delete_product_profile(
        str(product.id),
    )
    await create_audit_record(
        product.id,
        current_user,
        "Delete product",
        {"product_id": str(product.id)},
    )
    await product.delete()


@router.post("/{product_id}/lock")
async def lock_product_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
) -> None:
    if product.edit_locked:
        return
    product.edit_locked = True
    await create_audit_record(
        product.id,
        current_user,
        "Lock product",
        {"product_id": str(product.id)},
    )
    await product.save()


@router.post("/{product_id}/unlock")
async def unlock_product_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
) -> None:
    if not product.edit_locked:
        return
    product.edit_locked = False
    await create_audit_record(
        product.id,
        current_user,
        "Unlock product",
        {"product_id": str(product.id)},
    )
    await product.save()


router.include_router(
    competitive_analysis_router,
    prefix="/{product_id}/competitive-analysis",
)
router.include_router(
    product_profile_router,
    prefix="/{product_id}/profile",
)
router.include_router(
    claim_builder_router,
    prefix="/{product_id}/claim-builder",
)
router.include_router(
    version_control_router,
    prefix="/{product_id}/version-control",
)
router.include_router(
    performance_testing_router,
    prefix="/{product_id}/performance-testing",
)
router.include_router(
    test_comparison_router,
    prefix="/{product_id}/test-comparison",
)
router.include_router(
    clinical_trial_router,
    prefix="/{product_id}/clinical-trial",
)
router.include_router(
    regulatory_pathway_router,
    prefix="/{product_id}/regulatory-pathway",
)
router.include_router(
    feature_status_router,
    prefix="/{product_id}/feature-status",
)
router.include_router(
    milestone_planning_router,
    prefix="/{product_id}/milestone-planning",
)
router.include_router(
    cost_estimation_router,
    prefix="/{product_id}/cost-estimation",
)
router.include_router(
    custom_test_plan_router,
    prefix="/{product_id}/custom-test-plan",
)
router.include_router(
    review_program_router,
    prefix="/{product_id}/review-program",
)
router.include_router(
    final_regulatory_report_router,
    prefix="/{product_id}/final-regulatory-report",
)
router.include_router(
    checklist_router,
    prefix="/{product_id}/checklist",
)
router.include_router(
    regulatory_background_router,
    prefix="/{product_id}/regulatory-background",
)