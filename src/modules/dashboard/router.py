from fastapi import APIRouter, Header, Depends
from src.modules.dashboard.schema import DashboardResponse
from src.modules.authorization.dependencies import get_current_company
from src.modules.authentication.dependencies import get_current_user
from typing import Annotated
from src.modules.company.models import Company
from src.modules.user.models import User
from src.modules.dashboard.service import get_dashboard_products
import logging

router = APIRouter()

@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    current_company: Annotated[Company, Depends(get_current_company)],
    current_user: Annotated[User, Depends(get_current_user)],
    authorization: str = Header(...),
):
    logging.info(f"Authorization header: {authorization}")
    products = await get_dashboard_products(current_company, current_user)
    return DashboardResponse(
        company_id=str(current_company.id),
        company_name=current_company.name,
        products=products,
    )