import asyncio
from datetime import datetime, timezone
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from loguru import logger
from beanie.operators import Set

from src.modules.product.product_profile.model import ProductProfile
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
    analyze_all,
    create_product,
    get_products,
    upload_product_files,
)
from src.modules.product.schema import (
    CloneProductRequest,
    CloneProductRetainingOptions,
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

from src.modules.product.claim_builder.service import clone_claim_builder
from src.modules.product.clinical_trial.service import clone_clinical_trial
from src.modules.product.competitive_analysis.service import clone_competitive_analysis
from src.modules.product.cost_estimation.service import clone_cost_estimation
from src.modules.product.custom_test_plan.service import clone_custom_test_plan
from src.modules.product.feature_status.service import clone_feature_status
from src.modules.product.milestone_planning.service import clone_milestone_planning
from src.modules.product.performance_testing.service import clone_performance_testing
from src.modules.product.product_profile.service import clone_product_profile
from src.modules.product.regulatory_pathway.service import clone_regulatory_pathway
from src.modules.product.review_program.service import clone_review_program
from src.modules.product.test_comparison.service import clone_test_comparison

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
    current_user: Annotated[User, Depends(get_current_user)],
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
    name: str = Form(..., description="Product name"),
    code: str | None = Form(None, description="Product code"),
    model: str | None = Form(None, description="Product model"),
    revision: str | None = Form(None, description="Product revision"),
    category: str | None = Form(None, description="Product category"),
    intend_use: str | None = Form(None, description="Intended use of the product"),
    patient_contact: bool | None = Form(
        None, description="Indicates if the product has patient contact"
    ),
    files: List[UploadFile] = File([], description="Files to upload with the product"),
) -> ProductResponse:
    # Create payload from form data
    payload_data = {
        "name": name,
        "model": model,
        "revision": revision,
        "category": category,
        "intend_use": intend_use,
        "patient_contact": patient_contact,
    }

    # Only include code if it's not None to allow default factory to work
    if code is not None:
        payload_data["code"] = code

    payload = CreateProductRequest(**payload_data)

    # Create the product
    created_product = await create_product(payload, current_user, current_company)

    # Upload files if provided
    if files:
        await upload_product_files(str(created_product.id), files, current_user)

    created_product_response = await created_product.to_product_response()
    await create_audit_record(
        created_product,
        current_user,
        "Create product",
        payload.model_dump(),
    )
    return created_product_response


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
    # check if new name is existing
    if payload.name and payload.name != product.name:
        query_conditions = [
            Product.name == payload.name,
            Product.company_id == product.company_id,
        ]

        # Add model to query if provided
        if payload.model:
            query_conditions.append(Product.model == payload.model)

        existing_product = await Product.find_one(*query_conditions)
        if existing_product:
            raise HTTPException(
                status_code=400,
                detail=f"Product with name '{payload.name}' already exists in the company.",
            )

    # check if new model creates duplicate when name is not changing
    elif payload.model and payload.model != product.model:
        query_conditions = [
            Product.name == product.name,  # same name
            Product.company_id == product.company_id,
            Product.model == payload.model,  # new model
        ]

        existing_product = await Product.find_one(*query_conditions)
        if existing_product:
            raise HTTPException(
                status_code=400,
                detail=f"Product with name '{product.name}' and model '{payload.model}' already exists in the company.",
            )
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

    if payload.description is not None:
        logger.info(f"Updating product profile description for {product.id}")
        await ProductProfile.find(ProductProfile.product_id == str(product.id)).update(
            Set(
                {
                    ProductProfile.description: payload.description,
                },
            ),
        )

    await create_audit_record(
        product,
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
        product,
        current_user,
        "Delete product",
        {"product_id": str(product.id)},
    )
    await product.delete()


@router.post("/{product_id}/lock")
async def lock_product_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> None:
    if product.edit_locked:
        return
    product.edit_locked = True
    await create_audit_record(
        product,
        current_user,
        "Lock product",
        {"product_id": str(product.id)},
    )
    await product.save()


@router.post("/{product_id}/unlock")
async def unlock_product_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> None:
    if not product.edit_locked:
        return
    product.edit_locked = False
    await create_audit_record(
        product,
        current_user,
        "Unlock product",
        {"product_id": str(product.id)},
    )
    await product.save()


@router.post("/{product_id}/analyze-all")
async def analyze_all_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> None:
    product_id = str(product.id)
    analyze_all(product_id)
    await create_audit_record(
        product,
        current_user,
        "ANALYZE ALL",
        {"product_id": product_id},
    )


@router.post("/{product_id}/clone")
async def clone_product_handler(
    product: Annotated[Product, Depends(get_current_product)],
    payload: CloneProductRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> ProductResponse:
    now = datetime.now(timezone.utc)
    new_product = Product(
        **product.model_dump(
            exclude={
                "_id",
                "id",
                "created_at",
                "updated_at",
                "created_by",
                "updated_by",
                "edit_locked",
            }
        ),
        created_by=str(current_user.id),
        created_at=now,
        updated_by=str(current_user.id),
        updated_at=now,
    )
    if payload.updated_fields:
        new_name = payload.updated_fields.name
        if not new_name:
            new_name = f"{product.name} (Clone)"

        # Check if product name already exists for this company
        if new_name:
            query_conditions = [
                Product.company_id == product.company_id,
                Product.name == new_name,
            ]

            # Add model to query if provided
            if payload.updated_fields and payload.updated_fields.model:
                query_conditions.append(Product.model == payload.updated_fields.model)

            product_name_exists = await Product.find_one(*query_conditions)
            if product_name_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product name already exists for this company.",
                )

        new_product.name = new_name

        possible_fields = [
            "code",
            "model",
            "revision",
            "category",
            "intend_use",
            "patient_contact",
        ]
        for field in possible_fields:
            value = getattr(payload.updated_fields, field)
            if value is not None:
                setattr(new_product, field, value)
    await new_product.insert()

    if not payload.retaining_options:
        payload.retaining_options = CloneProductRetainingOptions()

    tasks = []

    if payload.retaining_options.claim_builder:
        logger.info(f"Cloning claim_builder from {product.id} to {new_product.id}")
        tasks.append(clone_claim_builder(product.id, new_product.id))
    if payload.retaining_options.clinical_trial:
        logger.info(f"Cloning clinical_trial from {product.id} to {new_product.id}")
        tasks.append(clone_clinical_trial(product.id, new_product.id))
    if payload.retaining_options.competitive_analysis:
        logger.info(
            f"Cloning competitive_analysis from {product.id} to {new_product.id}"
        )
        tasks.append(clone_competitive_analysis(product.id, new_product.id))
    if payload.retaining_options.cost_estimation:
        logger.info(f"Cloning cost_estimation from {product.id} to {new_product.id}")
        tasks.append(clone_cost_estimation(product.id, new_product.id))
    if payload.retaining_options.custom_test_plan:
        logger.info(f"Cloning custom_test_plan from {product.id} to {new_product.id}")
        tasks.append(clone_custom_test_plan(product.id, new_product.id))
    if payload.retaining_options.feature_status:
        logger.info(f"Cloning feature_status from {product.id} to {new_product.id}")
        tasks.append(clone_feature_status(product.id, new_product.id))
    if payload.retaining_options.milestone_planning:
        logger.info(f"Cloning milestone_planning from {product.id} to {new_product.id}")
        tasks.append(clone_milestone_planning(product.id, new_product.id))
    if payload.retaining_options.performance_testing:
        logger.info(
            f"Cloning performance_testing from {product.id} to {new_product.id}"
        )
        tasks.append(clone_performance_testing(product.id, new_product.id))
    if payload.retaining_options.product_profile:
        logger.info(f"Cloning product_profile from {product.id} to {new_product.id}")
        tasks.append(clone_product_profile(product.id, new_product.id))
    if payload.retaining_options.regulatory_pathway:
        logger.info(f"Cloning regulatory_pathway from {product.id} to {new_product.id}")
        tasks.append(clone_regulatory_pathway(product.id, new_product.id))
    if payload.retaining_options.review_program:
        logger.info(f"Cloning review_program from {product.id} to {new_product.id}")
        tasks.append(clone_review_program(product.id, new_product.id))
    if payload.retaining_options.test_comparison:
        logger.info(f"Cloning test_comparison from {product.id} to {new_product.id}")
        tasks.append(clone_test_comparison(product.id, new_product.id))

    # Run all clone tasks concurrently (in parallel)
    if tasks:
        await asyncio.gather(*tasks)

    await create_audit_record(
        product,
        current_user,
        "Clone product",
        payload.model_dump(),
    )
    return await new_product.to_product_response()


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
