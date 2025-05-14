from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from src.modules.user.schemas import UserResponse


# ============================
# Product Request
# ============================


class CreateProductRequest(BaseModel):
    name: str | None = Field(None, description="Product name")
    model: str | None = Field(None, description="Product model")
    revision: str | None = Field(None, description="Product revision")
    category: str | None = Field(None, description="Product category")
    intend_use: str | None = Field(None, description="Intended use of the product")
    patient_contact: bool | None = Field(
        None, description="Indicates if the product has patient contact"
    )


class UpdateProductRequest(BaseModel):
    code: str | None = Field(None, description="Product code")
    name: str | None = Field(None, description="Product name")
    model: str | None = Field(None, description="Product model")
    revision: str | None = Field(None, description="Product revision")
    category: str | None = Field(None, description="Product category")
    intend_use: str | None = Field(None, description="Intended use of the product")
    patient_contact: bool | None = Field(
        None, description="Indicates if the product has patient contact"
    )


# ============================
# Product Response
# ============================


class ProductResponse(BaseModel):
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    model: str = Field(..., description="Product model")
    revision: str = Field(..., description="Product revision")
    category: str = Field(..., description="Product category")
    avatar_url: str = Field(..., description="URL of the product avatar")
    intend_use: str = Field(..., description="Intended use of the product")
    patient_contact: bool = Field(
        ..., description="Indicates if the product has patient contact"
    )
    created_by: UserResponse = Field(..., description="User who created the product")
    created_at: datetime = Field(
        ..., description="Timestamp when the product was created"
    )
    updated_by: UserResponse = Field(..., description="User who updated the product")
    updated_at: datetime = Field(
        ..., description="Timestamp when the product was updated"
    )
    edit_locked: bool = Field(
        ..., description="Indicates if the product is locked for editing"
    )


class UploadDocumentUrlResponse(BaseModel):
    url: str = Field(..., description="Presigned URL for uploading a file")


class GetDocumentResponse(BaseModel):
    name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="Presigned URL for downloading the document")


class UpdateAvatarUrlResponse(BaseModel):
    url: str = Field(
        ...,
        description="URL to upload the avatar, using put method. Expires in 5 minutes",
    )
