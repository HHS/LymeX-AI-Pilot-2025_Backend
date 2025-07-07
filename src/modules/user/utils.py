from beanie import Document
from src.modules.company.models import Company
from src.modules.user.schemas import ActiveProduct


async def get_active_product_for_company(company_id: str, current_user_id: str) -> ActiveProduct | None:
    """Determine the active product for a company using the same logic as get_active_products"""
    # Import Product here to avoid circular imports
    from src.modules.product.models import Product
    
    products = await Product.find(
        Product.company_id == company_id,
    ).to_list()

    if not products:
        return None

    # Get the company to check for active_product_id
    company = await Company.get(company_id)
    if not company:
        return None

    # 0. HIGHEST PRECEDENCE: Check if company has an active product set
    if company.active_product_id:
        active_product = next(
            (p for p in products if str(p.id) == company.active_product_id),
            None,
        )
        if active_product:
            return ActiveProduct(
                id=str(active_product.id),
                name=active_product.name,
                code=active_product.code
            )

    # 1. If no active product, find the most recently updated product by the current user
    user_products = [
        p for p in products
        if getattr(p, "updated_by", None) == current_user_id
    ]
    if user_products:
        # Sort by updated_at descending and pick the first
        default_product = max(user_products, key=lambda p: p.updated_at)
        return ActiveProduct(
            id=str(default_product.id),
            name=default_product.name,
            code=default_product.code
        )

    # 2. Else, pick the most recently updated product by anyone
    default_product = max(products, key=lambda p: p.updated_at) if products else None
    if default_product:
        return ActiveProduct(
            id=str(default_product.id),
            name=default_product.name,
            code=default_product.code
        )

    return None 