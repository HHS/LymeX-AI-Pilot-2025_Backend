from src.modules.product.service import get_products
from src.modules.dashboard.schema import DashboardProductResponse
from src.modules.company.models import Company
from src.modules.product.models import Product
from typing import List
from src.modules.user.models import User

async def get_dashboard_products(current_company: Company, current_user: User) -> List[DashboardProductResponse]:
    products = await Product.find(
        Product.company_id == str(current_company.id),
    ).to_list()

    # 1. Find the most recently updated product by the current user
    user_products = [p for p in products if getattr(p, "updated_by", None) == str(current_user.id)]
    if user_products:
        print(1)  
        # Sort by updated_at descending and pick the first
        default_product = max(user_products, key=lambda p: p.updated_at)
    else:
        print(2)
        # 2. Else, pick the most recently updated product by anyone
        default_product = max(products, key=lambda p: p.updated_at) if products else None

    dashboard_products = []
    for product in products:
        dashboard_products.append(
            DashboardProductResponse(
                id=str(product.id),
                name=product.name,
                is_default=(default_product and product.id == default_product.id),
                updated_at=product.updated_at,
                regulatory_background_status=product.regulatory_background_status,
                claims_builder_status=product.claims_builder_status,
                competitive_analysis_status=product.competitive_analysis_status,
                standards_guidance_documents_status=product.standards_guidance_documents_status,
                performance_testing_requirements_status=product.performance_testing_requirements_status,
                regulatory_pathway_analysis_status=product.regulatory_pathway_analysis_status,
            )
        )
    return dashboard_products
