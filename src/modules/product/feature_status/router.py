from typing import Annotated
from fastapi import APIRouter, Depends

from src.modules.product.dependencies import get_current_product
from src.modules.product.feature_status.schema import FeaturesStatusResponse
from src.modules.product.feature_status.service import get_feature_status
from src.modules.product.models import Product


router = APIRouter()


@router.get("/")
async def get_feature_status_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> FeaturesStatusResponse:
    feature_status = await get_feature_status(product.id)
    return feature_status.to_features_status_response()
