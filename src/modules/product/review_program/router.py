from typing import Annotated, List
from fastapi import APIRouter, Depends
from src.modules.product.models import Product
from src.modules.product.dependencies import get_current_product
from src.modules.product.review_program.service import get_product_review_program
from src.modules.product.review_program.schema import ReviewProgramResponse

router = APIRouter()


@router.get("/")
async def get_product_review_program_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> List[ReviewProgramResponse]:
    review_programs = await get_product_review_program(product.id)
    return review_programs
