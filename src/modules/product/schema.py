from datetime import datetime
from pydantic import BaseModel, Field

from src.modules.product.constants import ProductStatus
from src.modules.user.schemas import UserResponse


class CreateProductRequest(BaseModel):
    code: str = Field(..., description="Product code")
    name: str = Field(..., description="Product name")
    model: str = Field(..., description="Product model")
    revision: str = Field(..., description="Product revision")
    description: str = Field(..., description="Product description")
    intend_use: str = Field(..., description="Intended use of the product")
    patient_contact: bool = Field(
        ..., description="Indicates if the product has patient contact"
    )
    device_description: str = Field(..., description="Description of the device")
    key_features: str = Field(..., description="Key features of the product")
    category: str = Field(..., description="Product category")
    version: str = Field(..., description="Product version")
    is_latest: bool = Field(..., description="Indicates if this is the latest version")
    status: ProductStatus = Field(..., description="Product status")


class UpdateProductRequest(BaseModel):
    code: str | None = Field(None, description="Product code")
    name: str | None = Field(None, description="Product name")
    model: str | None = Field(None, description="Product model")
    revision: str | None = Field(None, description="Product revision")
    description: str | None = Field(None, description="Product description")
    intend_use: str | None = Field(None, description="Intended use of the product")
    patient_contact: bool | None = Field(
        None, description="Indicates if the product has patient contact"
    )
    device_description: str | None = Field(
        None, description="Description of the device"
    )
    key_features: str | None = Field(None, description="Key features of the product")
    category: str | None = Field(None, description="Product category")
    version: str | None = Field(None, description="Product version")
    is_latest: bool | None = Field(
        None, description="Indicates if this is the latest version"
    )
    status: ProductStatus | None = Field(None, description="Product status")


class ProductResponse(BaseModel):
    id: str = Field(..., description="Product ID")
    code: str = Field(..., description="Product code")
    name: str = Field(..., description="Product name")
    model: str = Field(..., description="Product model")
    revision: str = Field(..., description="Product revision")
    description: str = Field(..., description="Product description")
    intend_use: str = Field(..., description="Intended use of the product")
    patient_contact: bool = Field(
        ..., description="Indicates if the product has patient contact"
    )
    device_description: str = Field(..., description="Description of the device")
    key_features: str = Field(..., description="Key features of the product")
    category: str = Field(..., description="Product category")
    version: str = Field(..., description="Product version")
    is_latest: bool = Field(..., description="Indicates if this is the latest version")
    status: ProductStatus = Field(..., description="Product status")
    created_by: UserResponse = Field(..., description="User who created the product")
    created_at: datetime = Field(
        ..., description="Timestamp when the product was created"
    )


class UploadDocumentUrlResponse(BaseModel):
    url: str = Field(..., description="Presigned URL for uploading a file")


class GetDocumentResponse(BaseModel):
    name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="Presigned URL for downloading the document")
