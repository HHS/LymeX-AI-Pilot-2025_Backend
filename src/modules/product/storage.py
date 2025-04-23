from src.infrastructure.minio import (
    generate_get_object_presigned_url,
    generate_put_object_presigned_url,
)
from src.modules.company.storage import get_company_folder
from src.modules.company.models import Company
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.modules.product.models import Product


def get_product_folder(company: Company, product: "Product") -> str:
    company_folder = get_company_folder(company)
    return f"{company_folder}/product/{product.id}"


def get_documents_folder(company: Company, product: "Product") -> str:
    product_folder = get_product_folder(company, product)
    return f"{product_folder}/documents"


async def get_product_avatar_url(company: Company, product: "Product") -> str:
    avatar_object_name = f"{get_product_folder(company, product)}/avatar"
    avatar_url = await generate_get_object_presigned_url(avatar_object_name)
    return avatar_url


async def get_update_product_avatar_url(company: Company, product: "Product") -> str:
    avatar_object_name = f"{get_product_folder(company, product)}/avatar"
    avatar_url = await generate_put_object_presigned_url(avatar_object_name)
    return avatar_url
