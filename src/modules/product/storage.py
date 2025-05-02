from src.modules.product.schema import DocumentType
from src.infrastructure.minio import (
    generate_get_object_presigned_url,
    generate_put_object_presigned_url,
)
from src.modules.company.storage import get_company_folder


def get_product_folder(company_id: str, product_id: str) -> str:
    company_folder = get_company_folder(company_id)
    return f"{company_folder}/product/{product_id}"


def get_documents_folder(
    company_id: str, product_id: str, document_type: DocumentType
) -> str:
    product_folder = get_product_folder(company_id, product_id)
    return f"{product_folder}/documents/{document_type}/"


async def get_product_avatar_url(company_id: str, product_id: str) -> str:
    avatar_object_name = f"{get_product_folder(company_id, product_id)}/avatar"
    avatar_url = await generate_get_object_presigned_url(avatar_object_name)
    return avatar_url


async def get_update_product_avatar_url(company_id: str, product_id: str) -> str:
    avatar_object_name = f"{get_product_folder(company_id, product_id)}/avatar"
    avatar_url = await generate_put_object_presigned_url(avatar_object_name)
    return avatar_url
