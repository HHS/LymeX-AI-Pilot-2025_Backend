from fastapi import APIRouter, Header, Depends
from src.modules.dashboard.schema import DashboardResponse, ProductListResponse
from src.modules.authorization.dependencies import get_current_company
from src.modules.authentication.dependencies import get_current_user
from typing import Annotated, List
from src.modules.company.models import Company
from src.modules.user.models import User
from src.modules.dashboard.service import get_dashboard_products, get_active_products

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    company_id: Annotated[str, Header()],
    current_company: Annotated[Company, Depends(get_current_company)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    products = await get_dashboard_products(current_company, current_user)
    return DashboardResponse(
        company_id=str(current_company.id),
        company_name=current_company.name,
        products=products,
    )


@router.get("/products-list", response_model=List[ProductListResponse])
async def get_active_product_dashboards(
    company_id: Annotated[str, Header()],
    current_company: Annotated[Company, Depends(get_current_company)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    products = await get_active_products(
        current_company, current_user, current_company.active_product_id or ""
    )
    return products
