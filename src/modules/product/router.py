from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends

from src.modules.product.product_profile.service import delete_product_profile
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
    payload: CreateProductRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> ProductResponse:
    have_update = False
    possible_fields = [
        "name",
        "model",
        "revision",
        "category",
        "intend_use",
        "patient_contact",
    ]
    for field in possible_fields:
        value = getattr(payload, field)
        if value == None:
            continue
        have_update = True
        setattr(product, field, value)
    if have_update:
        product.updated_by = str(current_user.id)
        product.updated_at = datetime.now(timezone.utc)
        await product.save()
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
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    await delete_product_competitive_analysis(
        str(product.id),
    )
    await delete_product_profile(
        str(product.id),
    )
    await product.delete()


@router.post("/{product_id}/lock")
async def lock_product_handler(
    product: Annotated[Product, Depends(get_current_product)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
) -> None:
    if product.edit_locked:
        return
    product.edit_locked = True
    await product.save()


@router.post("/{product_id}/unlock")
async def unlock_product_handler(
    product: Annotated[Product, Depends(get_current_product)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
) -> None:
    if not product.edit_locked:
        return
    product.edit_locked = False
    await product.save()


router.include_router(
    competitive_analysis_router,
    prefix="/{product_id}/competitive-analysis",
    tags=["Competitive Analysis"],
)
router.include_router(
    product_profile_router,
    prefix="/{product_id}/profile",
    tags=["Product Profile"],
)
