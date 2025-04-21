from datetime import datetime, timezone

from fastapi import HTTPException, status
from src.modules.product.models import Product
from src.modules.company.models import Company
from src.modules.product.schema import CreateProductRequest, ProductStatus
from src.modules.user.models import User


async def get_products(
    current_company: Company,
) -> list[Product]:
    products = await Product.find(
        Product.company_id == str(current_company.id),
    ).to_list()
    return products


async def create_product(
    payload: CreateProductRequest,
    current_user: User,
    current_company: Company,
) -> Product:
    product_code_exists = await Product.find_one(
        Product.code == payload.code,
        Product.company_id == str(current_company.id),
    )
    if product_code_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product code already exists for this company.",
        )
    product = Product(
        code=payload.code,
        name=payload.name,
        model=payload.model,
        revision=payload.revision,
        description=payload.description,
        intend_use=payload.intend_use,
        patient_contact=payload.patient_contact,
        device_description=payload.device_description,
        key_features=payload.key_features,
        category=payload.category,
        version=payload.version,
        is_latest=True,
        status=ProductStatus.DRAFT,
        company_id=str(current_company.id),
        created_by=str(current_user.id),
        created_at=datetime.now(timezone.utc),
    )
    await product.insert()
    return product


async def update_product(
    product_id: str,
    payload: CreateProductRequest,
    current_user: User,
    current_company: Company,
) -> Product:
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )
    if product.company_id != str(current_company.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this product.",
        )
    if product.edit_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product is locked for editing.",
        )
    product.code = payload.code
    product.name = payload.name
    product.model = payload.model
    product.revision = payload.revision
    product.description = payload.description
    product.intend_use = payload.intend_use
    product.patient_contact = payload.patient_contact
    product.device_description = payload.device_description
    product.key_features = payload.key_features
    product.category = payload.category
    product.version = payload.version
    product.is_latest = True
    product.status = ProductStatus.DRAFT
    product.company_id = str(current_company.id)
    product.created_by = str(current_user.id)
    product.created_at = datetime.now(timezone.utc)
    await product.save()
    return product


async def get_product_by_id(
    product_id: str,
    current_company: Company,
) -> Product:
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )
    if product.company_id != str(current_company.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this product.",
        )
    return product


async def delete_product(
    product_id: str,
    current_company: Company,
) -> None:
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )
    if product.company_id != str(current_company.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this product.",
        )
    if product.edit_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product is locked for editing.",
        )
    await product.delete()
    return None
