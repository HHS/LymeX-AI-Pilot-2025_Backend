from datetime import datetime

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
    text: str = Field(..., description="Text input for the document")


# ============================
# Product Profile Response
# ============================


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


class ProductProfileDocumentResponse(BaseModel):
    document_name: str = Field(..., description="Name of the product profile document")
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    uploaded_at: str = Field(
        ..., description="Date and time when the document was uploaded"
    )
    author: str = Field(..., description="Author of the document")
    size: int = Field(..., description="Size of the document in bytes")


class AnalyzeProductProfileProgressResponse(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    total_files: int = Field(..., description="Total number of files")
    processed_files: int = Field(
        ..., description="Number of files that have been processed"
    )
    updated_at: datetime = Field(
        ..., description="Date and time when the progress was last updated"
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
