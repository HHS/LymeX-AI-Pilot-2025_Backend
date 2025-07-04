from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Query

from src.modules.product.regulatory_background.service import (
    get_regulatory_background,
    upload_regulatory_background_file,
    get_regulatory_background_documents,
)
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


@router.post("/upload-file")
async def upload_regulatory_background_file_endpoint(
    product: Annotated[Product, Depends(get_current_product)],
    file: UploadFile = File(...),
):
    """Upload a regulatory background file"""
    try:
        return await upload_regulatory_background_file(str(product.id), file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def get_regulatory_background_documents_endpoint(
    product: Annotated[Product, Depends(get_current_product)],
):
    """Get all regulatory background documents for a product"""
    try:
        return await get_regulatory_background_documents(str(product.id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
