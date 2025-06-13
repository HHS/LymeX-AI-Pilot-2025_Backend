from typing import Annotated
from fastapi import APIRouter, Depends

from src.celery.tasks.analyze_milestone_planning import analyze_milestone_planning_task
from src.modules.product.milestone_planning.schema import (
    MilestonePlanningResponse,
    SaveMilestonePlanningRequest,
)
from src.modules.product.milestone_planning.service import (
    get_product_milestone_planning,
    save_milestone_planning,
)
from src.modules.product.dependencies import get_current_product
from src.modules.product.models import Product


router = APIRouter()


@router.post("/analyze")
async def analyze_milestone_planning_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> None:
    analyze_milestone_planning_task.delay(
        product_id=str(product.id),
    )


@router.get("/")
async def get_product_milestone_planning_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[MilestonePlanningResponse]:
    milestone_plannings = await get_product_milestone_planning(product.id)
    return [await planning.to_milestone_planning_response() for planning in milestone_plannings]


@router.post("/save")
async def save_milestone_planning_handler(
    product: Annotated[Product, Depends(get_current_product)],
    payload: SaveMilestonePlanningRequest,
) -> MilestonePlanningResponse:
    milestone_planning = await save_milestone_planning(
        product_id=product.id,
        milestones=payload.milestones,
    )
    return await milestone_planning.to_milestone_planning_response()