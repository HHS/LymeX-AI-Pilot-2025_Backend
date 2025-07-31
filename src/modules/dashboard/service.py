from src.modules.product.analyzing_status import AnalyzingStatus
from src.modules.product.claim_builder.service import get_analyze_claim_builder_progress
from src.modules.product.competitive_analysis.analyze_competitive_analysis_progress import (
    get_analyze_competitive_analysis_progress,
)
from src.modules.product.performance_testing.service import (
    get_analyze_performance_testing_progress,
)
from src.modules.product.regulatory_background.analyze_regulatory_background_progress import (
    get_analyze_regulatory_background_progress,
)
from src.modules.product.regulatory_pathway.service import (
    get_analyze_regulatory_pathway_progress,
)
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

        analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
            str(product.id),
        )
        analyze_claim_builder_progress_status = (
            analyze_claim_builder_progress.to_analyze_claim_builder_progress_response().analyzing_status
            if analyze_claim_builder_progress
            else AnalyzingStatus.PENDING
        )

        analyze_competitive_analysis_progress = (
            await get_analyze_competitive_analysis_progress(
                str(product.id),
            )
        )
        analyze_competitive_analysis_progress_status = (
            analyze_competitive_analysis_progress.to_analyze_competitive_analysis_progress_response().analyzing_status
            if analyze_competitive_analysis_progress
            else AnalyzingStatus.PENDING
        )

        analyze_regulatory_pathway_progress = (
            await get_analyze_regulatory_pathway_progress(str(product.id))
        )
        analyze_regulatory_pathway_progress_status = (
            analyze_regulatory_pathway_progress.to_analyze_regulatory_pathway_progress_response().analyzing_status
            if analyze_regulatory_pathway_progress
            else AnalyzingStatus.PENDING
        )

        analyze_performance_testing_progress = (
            await get_analyze_performance_testing_progress(str(product.id))
        )
        analyze_performance_testing_progress_status = (
            analyze_performance_testing_progress.to_analyze_performance_testing_progress_response().analyzing_status
            if analyze_performance_testing_progress
            else AnalyzingStatus.PENDING
        )

        analyze_regulatory_background_progress = (
            await get_analyze_regulatory_background_progress(str(product.id))
        )
        analyze_regulatory_background_progress_status = (
            analyze_regulatory_background_progress.to_analyze_regulatory_background_progress_response().analyzing_status
            if analyze_regulatory_background_progress
            else AnalyzingStatus.PENDING
        )

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
                regulatory_background_status=analyze_regulatory_background_progress_status,
                claims_builder_status=analyze_claim_builder_progress_status,
                competitive_analysis_status=analyze_competitive_analysis_progress_status,
                standards_guidance_documents_status=AnalyzingStatus.PENDING,
                performance_testing_requirements_status=analyze_performance_testing_progress_status,
                regulatory_pathway_analysis_status=analyze_regulatory_pathway_progress_status,
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
