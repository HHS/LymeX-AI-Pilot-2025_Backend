from src.infrastructure.minio import (
    generate_get_object_presigned_url,
    generate_put_object_presigned_url,
)
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.modules.company.models import Company


def get_company_folder(company_id: str) -> str:
    return f"company/{company_id}"


def get_company_logo_object_name(company_id: str) -> str:
    company_folder = get_company_folder(company_id)
    return f"{company_folder}/logo"


async def get_company_logo_url(company_id: str) -> str:
    logo_object_name = get_company_logo_object_name(company_id)
    logo_url = await generate_get_object_presigned_url(logo_object_name)
    return logo_url


async def get_update_company_logo_url(company_id: str) -> str:
    logo_object_name = get_company_logo_object_name(company_id)
    logo_url = await generate_put_object_presigned_url(logo_object_name)
    return logo_url
