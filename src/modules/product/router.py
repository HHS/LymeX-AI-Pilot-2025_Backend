from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from src.modules.product.storage import (
    get_competitive_analysis_folder,
    get_documents_folder,
    get_update_product_avatar_url,
)
from src.infrastructure.minio import (
    generate_get_object_presigned_url,
    generate_put_object_presigned_url,
    list_objects,
    remove_object,
)
from src.modules.product.service import (
    create_product,
    delete_product,
    get_product_by_id,
    get_products,
    update_product,
)
from src.modules.product.schema import (
    CreateProductRequest,
    GetDocumentResponse,
    ProductResponse,
    UpdateAvatarUrlResponse,
    UploadDocumentUrlResponse,
)
from src.modules.authentication.dependencies import get_current_user
from src.modules.authorization.dependencies import (
    RequireCompanyRole,
    get_current_company,
)
from src.modules.authorization.roles import CompanyRoles
from src.modules.company.models import Company
from src.modules.user.models import User


router = APIRouter()


@router.get("/")
async def get_products_handler(
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.VIEWER))],
) -> list[ProductResponse]:
    products = await get_products(current_company)
    return [await product.to_product_response(current_company) for product in products]


@router.post("/")
async def create_product_handler(
    payload: CreateProductRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> ProductResponse:
    created_product = await create_product(payload, current_user, current_company)
    return await created_product.to_product_response(current_company)


@router.get("/{product_id}")
async def get_product_handler(
    product_id: str,
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.VIEWER))],
) -> ProductResponse:
    product = await get_product_by_id(product_id, current_company)
    return await product.to_product_response(current_company)


@router.put("/{product_id}")
async def update_product_handler(
    product_id: str,
    payload: CreateProductRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> ProductResponse:
    created_product = await update_product(
        product_id, payload, current_user, current_company
    )
    return await created_product.to_product_response(current_company)


@router.get("/{product_id}/update-avatar-url")
async def get_update_avatar_url_handler(
    product_id: str,
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> UpdateAvatarUrlResponse:
    product = await get_product_by_id(product_id, current_company)
    if product.edit_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product is locked for editing.",
        )
    avatar_url = await get_update_product_avatar_url(
        current_company.id,
        product.id,
    )
    return {
        "url": avatar_url,
    }


@router.delete("/{product_id}")
async def delete_product_handler(
    product_id: str,
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> None:
    await delete_product(product_id, current_company)


@router.post("/{product_id}/lock")
async def lock_product_handler(
    product_id: str,
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
) -> None:
    product = await get_product_by_id(product_id, current_company)
    if product.edit_locked:
        return
    product.edit_locked = True
    await product.save()


@router.post("/{product_id}/unlock")
async def unlock_product_handler(
    product_id: str,
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
) -> None:
    product = await get_product_by_id(product_id, current_company)
    if not product.edit_locked:
        return
    product.edit_locked = False
    await product.save()


# === GENERAL DOCUMENTS ===


@router.get("/{product_id}/document")
async def get_documents_handler(
    product_id: str,
    document_type: str,
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.VIEWER))],
) -> list[GetDocumentResponse]:
    product = await get_product_by_id(product_id, current_company)
    documents_folder = get_documents_folder(
        current_company.id, product.id, document_type
    )
    documents = await list_objects(prefix=f"{documents_folder}/")
    documents = [document for document in documents if not document.is_dir]
    file_names = [document.object_name.split("/")[-1] for document in documents]
    file_urls = [
        await generate_get_object_presigned_url(
            object_name=document.object_name,
            expiration_seconds=300,
        )
        for document in documents
    ]
    return [
        GetDocumentResponse(
            name=file_name,
            url=file_url,
        )
        for file_name, file_url in zip(file_names, file_urls)
    ]


@router.get("/{product_id}/document/upload-url")
async def get_upload_document_url_handler(
    product_id: str,
    file_name: str,
    document_type: str,
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> UploadDocumentUrlResponse:
    product = await get_product_by_id(product_id, current_company)
    if product.edit_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product is locked for editing.",
        )
    documents_folder = get_documents_folder(
        current_company.id, product.id, document_type
    )
    object_name = f"{documents_folder}/{file_name}"
    upload_document_url = await generate_put_object_presigned_url(
        object_name=object_name,
        expiration_seconds=300,
    )
    return {
        "url": upload_document_url,
    }


@router.delete("/{product_id}/document/delete-file")
async def delete_file_handler(
    product_id: str,
    current_company: Annotated[Company, Depends(get_current_company)],
    file_name: str,
    document_type: str,
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> None:
    product = await get_product_by_id(product_id, current_company)
    if product.edit_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product is locked for editing.",
        )
    documents_folder = get_documents_folder(
        current_company.id, product.id, document_type
    )
    object_name = f"{documents_folder}/{file_name}"
    await remove_object(object_name=object_name)


# === Competitive Analysis ===


@router.get("/{product_id}/competitive-analysis")
async def get_competitive_analysis_handler(
    product_id: str,
    category: str,
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.VIEWER))],
) -> list[GetDocumentResponse]:
    product = await get_product_by_id(product_id, current_company)
    competitive_analysis_folder = get_competitive_analysis_folder(
        current_company.id, product.id, category
    )
    competitive_analysis = await list_objects(prefix=f"{competitive_analysis_folder}/")
    competitive_analysis = [
        document for document in competitive_analysis if not document.is_dir
    ]
    file_names = [
        document.object_name.split("/")[-1] for document in competitive_analysis
    ]
    file_urls = [
        await generate_get_object_presigned_url(
            object_name=document.object_name,
            expiration_seconds=300,
        )
        for document in competitive_analysis
    ]
    return [
        GetDocumentResponse(
            name=file_name,
            url=file_url,
        )
        for file_name, file_url in zip(file_names, file_urls)
    ]


@router.get("/{product_id}/competitive-analysis/upload-url")
async def get_upload_competitive_analysis_url_handler(
    product_id: str,
    file_name: str,
    category: str,
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> UploadDocumentUrlResponse:
    product = await get_product_by_id(product_id, current_company)
    if product.edit_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product is locked for editing.",
        )
    competitive_analysis_folder = get_competitive_analysis_folder(
        current_company.id, product.id, category
    )
    object_name = f"{competitive_analysis_folder}/{file_name}"
    upload_competitive_analysis_url = await generate_put_object_presigned_url(
        object_name=object_name,
        expiration_seconds=300,
    )
    return {
        "url": upload_competitive_analysis_url,
    }


@router.delete("/{product_id}/competitive_analysis/delete-file")
async def delete_file_handler(
    product_id: str,
    current_company: Annotated[Company, Depends(get_current_company)],
    file_name: str,
    category: str,
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> None:
    product = await get_product_by_id(product_id, current_company)
    if product.edit_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product is locked for editing.",
        )
    competitive_analysis_folder = get_competitive_analysis_folder(
        current_company.id, product.id, category
    )
    object_name = f"{competitive_analysis_folder}/{file_name}"
    await remove_object(object_name=object_name)
