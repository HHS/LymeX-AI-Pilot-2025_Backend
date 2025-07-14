from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from src.modules.user.schemas import UserResponse


class RegulatoryClassification(BaseModel):
    organization: str
    classification: str


class Feature(BaseModel):
    name: str
    description: str
    icon: str | None = Field(None, description="Icon representing the feature")


class Performance(BaseModel):
    speed: int
    reliability: int


class AnalyzingStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In_Progress"
    COMPLETED = "Completed"


# ============================
# Product Profile Request
# ============================


class UpdateProductProfileRequest(BaseModel):
    description: str | None = Field(None, description="Description of the product")
    regulatory_classifications: list[RegulatoryClassification] | None = Field(
        None, description="Regulatory classifications of the product"
    )
    device_description: str | None = Field(
        None, description="Description of the device associated with the product"
    )
    features: list[Feature] | None = Field(
        None, description="List of features associated with the product"
    )
    claims: list[str] | None = Field(
        None, description="List of claims associated with the product"
    )
    conflict_alerts: list[str] | None = Field(
        None, description="List of conflict alerts associated with the product"
    )


class UploadTextInputDocumentRequest(BaseModel):
    text: str | None = Field(None, description="Text input for the document")
    files: list[str] | None = Field(None, description="List of file names to upload")


# ============================
# Product Profile Response
# ============================


class ProductProfileDocumentResponse(BaseModel):
    document_name: str = Field(..., description="Name of the product profile document")
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    uploaded_at: str = Field(
        ..., description="Date and time when the document was uploaded"
    )
    author: str = Field(..., description="Author of the document")
    size: int = Field(..., description="Size of the document in bytes")


class ProductProfileAuditResponse(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    product_name: str | None = Field(None, description="Name of the product")
    user_id: str = Field(..., description="ID of the user who performed the action")
    user_email: str = Field(
        ..., description="Email of the user who performed the action"
    )
    user_name: str | None = Field(
        None, description="Name of the user who performed the action"
    )
    action: str = Field(..., description="Action performed on the product profile")
    data: Any = Field(..., description="Additional data related to the action")
    timestamp: datetime = Field(
        ..., description="Timestamp when the action was performed"
    )
    version: str = Field(
        ..., description="Version of the product profile at the time of the action"
    )


class ProductProfileResponse(BaseModel):
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    model: str = Field(..., description="Product model")
    revision: str = Field(..., description="Product revision")
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
    description: str | None = Field(None, description="Description of the product")
    regulatory_classifications: list[RegulatoryClassification] | None = Field(
        None, description="Regulatory classifications of the product"
    )
    device_description: str | None = Field(
        None, description="Description of the device associated with the product"
    )
    features: list[Feature] | None = Field(
        None, description="List of features associated with the product"
    )
    claims: list[str] | None = Field(
        None, description="List of claims associated with the product"
    )
    conflict_alerts: list[str] | None = Field(
        None, description="List of conflict alerts associated with the product"
    )
    analyzing_status: AnalyzingStatus = Field(
        ..., description="Current status of the product analysis"
    )
    documents: list[ProductProfileDocumentResponse] = Field(
        default=[], description="List of all documents uploaded for this product"
    )
    latest_audits: list[ProductProfileAuditResponse] = Field(
        default=[], description="Last three audit records for this product"
    )


class AnalyzeProductProfileProgressResponse(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    total_files: int = Field(..., description="Total number of files")
    processed_files: int = Field(
        ..., description="Number of files that have been processed"
    )
    updated_at: datetime = Field(
        ..., description="Date and time when the progress was last updated"
    )
    analyzing_status: AnalyzingStatus = Field(
        ..., description="Current status of the product analysis"
    )


class ProductProfileAnalysisResponse(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    product_code: str = Field(..., description="Code of the product")
    product_name: str = Field(..., description="Name of the product")
    updated_at: datetime = Field(
        ..., description="Date and time when the profile was last updated"
    )
    fda_approved: bool | None = Field(
        None, description="Indicates if the product is FDA approved"
    )
    ce_marked: bool | None = Field(
        None, description="Indicates if the product is CE marked"
    )
    features: list[Feature] = Field(..., description="List of features of the product")
    regulatory_classifications: list[RegulatoryClassification] = Field(
        ..., description="Li sst of regulatory classifications for the product"
    )
    analyzing_status: AnalyzingStatus = Field(
        ..., description="Current status of the product analysis"
    )
