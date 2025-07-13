from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from uuid import uuid4
from src.modules.product.product_profile.schema import AnalyzingStatus
from src.modules.user.schemas import UserResponse


# ============================
# Product Request
# ============================


def create_uuid() -> str:
    """Generate a new UUID."""
    return str(uuid4())


class CreateProductRequest(BaseModel):
    name: str = Field(..., description="Product name")
    code: str = Field(default_factory=create_uuid, description="Product code")
    model: str = Field(..., description="Product model")
    revision: str = Field(..., description="Product revision")
    category: str = Field(..., description="Product category")
    intend_use: str = Field(..., description="Intended use of the product")
    patient_contact: bool = Field(
        ..., description="Indicates if the product has patient contact"
    )


class UpdateProductRequest(BaseModel):
    name: str | None = Field(None, description="Product name")
    code: str | None = Field(None, description="Product code")
    model: str | None = Field(None, description="Product model")
    revision: str | None = Field(None, description="Product revision")
    category: str | None = Field(None, description="Product category")
    intend_use: str | None = Field(None, description="Intended use of the product")
    patient_contact: bool | None = Field(
        None, description="Indicates if the product has patient contact"
    )


class CloneProductRetainingOptions(BaseModel):
    claim_builder: bool = Field(True)
    clinical_trial: bool = Field(True)
    competitive_analysis: bool = Field(True)
    cost_estimation: bool = Field(True)
    custom_test_plan: bool = Field(True)
    feature_status: bool = Field(True)
    milestone_planning: bool = Field(True)
    performance_testing: bool = Field(True)
    product_profile: bool = Field(True)
    regulatory_pathway: bool = Field(True)
    review_program: bool = Field(True)
    test_comparison: bool = Field(True)


class CloneProductRequest(BaseModel):
    updated_fields: UpdateProductRequest | None = Field(None)
    retaining_options: CloneProductRetainingOptions | None = Field(None)


# ============================
# Product Response
# ============================


class ProductResponse(BaseModel):
    id: str = Field(..., description="Product ID")
    code: str | None = Field(None, description="Product code")
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
    is_active_profile: bool = Field(
        default=False,
        description="Indicates if this is the active profile for the company",
    )
    analyzing_status: AnalyzingStatus = Field(
        ..., description="Current status of the product analysis"
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


class FeatureStatus(str, Enum):
    NOT_STARTED = "NotStarted"
    IN_PROGRESS = "InProgress"
    DONE = "Done"
