from typing import Annotated

from fastapi import Depends, HTTPException, status
from src.modules.authorization.roles import CompanyRoles
from src.modules.authorization.dependencies import (
    RequireCompanyRole,
    get_current_company,
)
from src.modules.company.models import Company
from src.modules.product.models import Product


async def get_current_product(
    product_id: str,
    current_company: Annotated[Company, Depends(get_current_company)],
) -> Product:
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )
    if product.company_id != str(current_company.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this product.",
        )
    return product


async def check_product_edit_allowed(
    product: Annotated[Product, Depends(get_current_product)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> bool:
    if product.edit_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product edit is locked",
        )
    return True
