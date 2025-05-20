from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class IFUSource(BaseModel):
    source: str = Field(..., description="Source of the IFU phrase")
    reason: str = Field(..., description="Reason for including this phrase in the IFU")
    category: str = Field(
        ..., description="Category of the IFU phrase, e.g., safety, usage, maintenance"
    )  # Example: safety, usage, maintenance, etc.


class IFU(BaseModel):
    phrase: str = Field(
        ..., description="The phrase from the Instructions for Use (IFU)"
    )
    sources: list[IFUSource] | None = Field(
        None, description="List of sources for the IFU phrase"
    )


class ComplianceStatus(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Compliance(BaseModel):
    content: str
    status: ComplianceStatus


class MissingElementLevel(str, Enum):
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"


class MissingElement(BaseModel):
    description: str
    suggested_fix: str
    level: MissingElementLevel


class RiskIndicatorSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskIndicator(BaseModel):
    description: str
    severity: RiskIndicatorSeverity


class PhraseConflict(BaseModel):
    statement: str
    conflicting_regulation: str
    suggested_fix: str


class Draft(BaseModel):
    version: int = Field(..., description="Version of the draft")
    updated_at: datetime = Field(
        ..., description="Date and time when the draft was last updated"
    )
    updated_by: str = Field(..., description="User email who last updated the draft")
    content: str = Field(..., description="Content of the draft claim builder")


# ============== REQUESTS ================


class UpdateClaimBuilderDraftRequest(BaseModel):
    content: str = Field(..., description="Content of the draft claim builder")


# ============== RESPONSES ================


class ClaimBuilderResponse(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    product_code: str = Field(
        ..., description="Code of the product associated with the claim builder"
    )
    product_name: str = Field(
        ..., description="Name of the product associated with the claim builder"
    )
    draft: list[Draft] = Field(..., description="Draft content for the claim builder")
    key_phrases: list[str] = Field(
        ..., description="List of key phrases used in the claim"
    )
    ifu: list[IFU] = Field(..., description="Instructions for Use (IFU) content")
    compliance: list[Compliance] = Field(..., description="List of compliance checks")
    missing_elements: list[MissingElement] = Field(
        ..., description="List of missing elements in the claim"
    )
    risk_indicators: list[RiskIndicator] = Field(
        ..., description="List of risk indicators associated with the claim"
    )
    phrase_conflicts: list[PhraseConflict] = Field(
        ..., description="List of phrase conflicts identified in the claim"
    )
    user_acceptance: bool = Field(
        ..., description="Indicates if the user has accepted the claim builder"
    )


class AnalyzeClaimBuilderProgressResponse(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    total_files: int = Field(..., description="Total number of files")
    processed_files: int = Field(
        ..., description="Number of files that have been processed"
    )
    updated_at: datetime = Field(
        ..., description="Date and time when the progress was last updated"
    )
