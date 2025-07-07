from src.modules.product.service import get_products
from src.modules.dashboard.schema import DashboardProductResponse, ProductListResponse
from src.modules.company.models import Company
from src.modules.product.models import Product
from typing import List
from src.modules.user.models import User
from src.modules.checklist.service import get_or_create_checklist


async def calculate_remaining_tasks(product_id: str) -> int:
    """Calculate remaining tasks for a product using existing checklist progress data"""
    try:
        # Get or create checklist for the product
        checklist_response = await get_or_create_checklist(product_id)
        checklist = checklist_response["checklist"]
        
        # Use existing checklist progress data
        # remaining_tasks = total - completed
        remaining_tasks = checklist.checklist.total - checklist.checklist.completed
        
        return remaining_tasks
    except Exception as e:
        # If there's any error getting the checklist, return 0
        print(f"Error calculating remaining tasks for product {product_id}: {e}")
        return 0


async def get_dashboard_products(
    current_company: Company, current_user: User
) -> List[DashboardProductResponse]:
    products = await Product.find(
        Product.company_id == str(current_company.id),
    ).to_list()

    # 1. Find the most recently updated product by the current user
    user_products = [
        p for p in products if getattr(p, "updated_by", None) == str(current_user.id)
    ]
    if user_products:
        # Sort by updated_at descending and pick the first
        default_product = max(user_products, key=lambda p: p.updated_at)
    else:
        # 2. Else, pick the most recently updated product by anyone
        default_product = (
            max(products, key=lambda p: p.updated_at) if products else None
        )

    dashboard_products = []
    for product in products:
        # Calculate remaining tasks for this product
        remaining_tasks = await calculate_remaining_tasks(str(product.id))
        
        dashboard_products.append(
            DashboardProductResponse(
                id=str(product.id),
                name=product.name,
                is_default=(default_product and product.id == default_product.id),
                updated_at=product.updated_at,
                regulatory_background_percentage=product.regulatory_background_percentage,
                claims_builder_percentage=product.claims_builder_percentage,
                competitive_analysis_percentage=product.competitive_analysis_percentage,
                standards_guidance_documents_percentage=product.standards_guidance_documents_percentage,
                performance_testing_requirements_percentage=product.performance_testing_requirements_percentage,
                regulatory_pathway_analysis_percentage=product.regulatory_pathway_analysis_percentage,
                remaining_tasks=remaining_tasks,
            )
        )
    return dashboard_products


async def get_active_products(
    current_company: Company, current_user: User, active_product_id: str
) -> List[DashboardProductResponse]:
    products = await Product.find(
        Product.company_id == str(current_company.id),
    ).to_list()

    # 0. HIGHEST PRECEDENCE: Check if company has an active product set
    if current_company.active_product_id:
        active_product = next(
            (p for p in products if str(p.id) == current_company.active_product_id),
            None,
        )
        if active_product:
            default_product = active_product
        else:
            # Active product not found, fall back to other logic
            default_product = None
    else:
        default_product = None

    # 1. If no active product, find the most recently updated product by the current user
    if not default_product:
        user_products = [
            p
            for p in products
            if getattr(p, "updated_by", None) == str(current_user.id)
        ]
        if user_products:
            # Sort by updated_at descending and pick the first
            default_product = max(user_products, key=lambda p: p.updated_at)
        else:
            # 2. Else, pick the most recently updated product by anyone
            default_product = (
                max(products, key=lambda p: p.updated_at) if products else None
            )

    dashboard_products = []
    for product in products:
        # Calculate remaining tasks for this product
        remaining_tasks = await calculate_remaining_tasks(str(product.id))
        
        dashboard_products.append(
            ProductListResponse(
                id=str(product.id),
                name=product.name,
                code=product.code,
                model=product.model,
                revision=product.revision,
                category=product.category,
                is_default=(default_product and product.id == default_product.id),
                updated_at=product.updated_at,
                remaining_tasks=remaining_tasks,
            )
        )
    return dashboard_products
