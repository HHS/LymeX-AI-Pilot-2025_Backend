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


class ProductProfileSchemaBase:
    product_trade_name: str = Field(
        "Not Available", description="Trade name of the product"
    )
    model_number: str = Field(
        "Not Available", description="Model number of the product"
    )
    reference_number: str = Field(
        "Not Available", description="Reference number for the product"
    )
    description: str = Field("Not Available", description="Description of the product")
    generic_name: str = Field(
        "Not Available", description="Generic name of the product"
    )

    regulatory_pathway: str = Field(
        "Not Available", description="Regulatory pathway for product approval"
    )
    regulatory_classifications: list[RegulatoryClassification] = Field(
        default_factory=list,
        description="List of regulatory classifications",
    )
    product_code: str = Field("Not Available", description="Product code")
    regulation_number: str = Field("Not Available", description="Regulation Number")
    analytical_sensitivity: str = Field(
        "Not Available", description="Analytical Sensitivity"
    )
    analytical_specificity: str = Field(
        "Not Available", description="Analytical Specificity"
    )
    precision_reproducibility: str = Field(
        "Not Available", description="APrecision Reproducibility"
    )
    clinical_performance: str = Field(
        "Not Available", description="Clinical Performance"
    )
    performance_summary: str = Field(
        "Not Available", description="Overall Performance Summary"
    )
    performance_references: list[str] = Field(
        default_factory=list, description="Performance References"
    )
    device_description: str = Field(
        "Not Available", description="Description of the device"
    )
    features: list[Feature] = Field(
        default_factory=list, description="List of device features"
    )
    claims: list[str] = Field(
        default_factory=list, description="Claims made about the product"
    )
    conflict_alerts: list[str] = Field(
        default_factory=list, description="Alerts for any conflicts"
    )
    test_principle: str = Field(
        "Not Available", description="Principle of the test performed by the device"
    )
    comparative_claims: list[str] = Field(
        default_factory=list, description="Comparative claims with other products"
    )
    fda_cleared: bool | None = Field(
        None, description="FDA clearance status (None if not applicable)"
    )
    fda_approved: bool | None = Field(
        None, description="FDA approval status (None if not applicable)"
    )
    ce_marked: bool | None = Field(
        None, description="CE marking status (None if not applicable)"
    )
    device_ifu_description: str = Field(
        "Not available", description="Description of instructions for use"
    )
    instructions_for_use: list[str] = Field(
        default_factory=list, description="Step-by-step instructions for use"
    )
    principle_of_operation: str = Field(
        "Not Available", description="Principle of Operation"
    )
    interpretation_of_results: str = Field(
        "Not Available", description="Interpretation of Results"
    )
    generic_name: str = Field("Not Available", description="Generic Name")
    storage_conditions: str = Field("Not Available", description="Storage Conditions")
    shelf_life: str = Field("Not Available", description="Shelf Life")
    sterility_status: str = Field("Not Available", description="Sterility Status")
    software_present: str = Field("Not Available", description="Software Present")
    single_use_or_reprocessed_single_use_device: str = Field(
        "Not Available", description="Single Use or Reprocessed Single Use Device"
    )
    animal_derived_materials: str = Field(
        "Not Available", description="Animal Derived Materials"
    )
    warnings: list[str] = Field(
        default_factory=list, description="Warnings associated with the product"
    )
    limitations: list[str] = Field(
        default_factory=list, description="Limitations of the product"
    )
    contraindications: list[str] = Field(
        default_factory=list, description="Contraindications for product use"
    )
    confidence_score: float = Field(
        0.0, description="Confidence score for the product profile"
    )
    sources: list[str] = Field(
        default_factory=list,
        description="Sources of information for the product profile",
    )
    speed: int = Field(-1, description="Speed")
    reliability: int = Field(-1, description="Reliability")
    price: int = Field(0, description="Price of the product")
    instructions: list[str] = Field(
        default_factory=list, description="General instructions for the product"
    )
    type_of_use: str = Field("Not Available", description="Type of use for the product")
    device_type: str = Field("Not Available", description="Type of device")
    disease_condition: str = Field(
        "Not Available", description="Disease or condition addressed by the product"
    )
    patient_population: str = Field(
        "Not Available", description="Patient population for the product"
    )
    use_environment: str = Field(
        "Not Available", description="Environment where the product is used"
    )
    combination_use: str = Field(
        "Not Available", description="Combination use with other products"
    )
    life_supporting: str = Field(
        "Not Available", description="Whether the product is life supporting"
    )
    specimen_type: str = Field("Not Available", description="Type of specimen used")
    special_attributes: str = Field(
        "Not Available", description="Special attributes of the product"
    )


class ProductProfileSchema(BaseModel, ProductProfileSchemaBase): ...


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


class ProductProfileResponse(BaseModel, ProductProfileSchemaBase):
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    model: str = Field(..., description="Product model")
    revision: str | None = Field(..., description="Product revision")
    avatar_url: str | None = Field(..., description="URL of the product avatar")
    intend_use: str | None = Field(..., description="Intended use of the product")
    patient_contact: bool | None = Field(
        ..., description="Indicates if the product has patient contact"
    )
    created_by: UserResponse | None = Field(
        ..., description="User who created the product"
    )
    created_at: datetime | None = Field(
        ..., description="Timestamp when the product was created"
    )
    updated_by: UserResponse | None = Field(
        ..., description="User who updated the product"
    )
    updated_at: datetime | None = Field(
        ..., description="Timestamp when the product was updated"
    )
    edit_locked: bool | None = Field(
        ..., description="Indicates if the product is locked for editing"
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
