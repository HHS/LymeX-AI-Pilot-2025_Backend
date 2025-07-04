from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends

from src.modules.product.regulatory_background.service import get_regulatory_background
from src.modules.product.regulatory_background.schema import (
    RegulatoryBackgroundResponse,
)
from src.modules.product.dependencies import get_current_product
from src.modules.product.models import Product


router = APIRouter()


@router.get("/")
async def get_regulatory_background_endpoint(
    product: Annotated[Product, Depends(get_current_product)],
) -> RegulatoryBackgroundResponse:
    """Get regulatory background for a product"""
    try:
        return await get_regulatory_background(str(product.id))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting regulatory background: {str(e)}"
        )
