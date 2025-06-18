from fastapi import APIRouter, Depends
from typing import Annotated
from src.modules.product.models import Product
from src.modules.product.dependencies import get_current_product
from .service import get_final_regulatory_report
from .schema import FinalRegulatoryReportResponse

router = APIRouter()

@router.get("/", response_model=FinalRegulatoryReportResponse)
async def get_final_regulatory_report_handler(
    product: Annotated[Product, Depends(get_current_product)],
):
    return await get_final_regulatory_report(str(product.id))
