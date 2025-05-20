from typing import Annotated
from fastapi import APIRouter, Depends

from src.modules.product.version_control.service import get_product_version_control
from src.modules.product.version_control.schema import ProductVersionControlResponse
from src.modules.product.dependencies import get_current_product
from src.modules.product.models import Product


router = APIRouter()


@router.get("/")
async def get_product_profile_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[ProductVersionControlResponse]:
    product_version_controls = await get_product_version_control(str(product.id))
    return [
        product_version_control.to_product_version_control_response()
        for product_version_control in product_version_controls
    ]
