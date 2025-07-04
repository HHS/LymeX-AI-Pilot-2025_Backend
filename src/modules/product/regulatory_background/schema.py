from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SummaryHighlight(BaseModel):
    """Individual highlight in the regulatory summary"""
    title: str = Field(..., description="Title of the highlight")
    detail: str = Field(..., description="Detailed description of the highlight")


class RegulatorySummary(BaseModel):
    """Summary section of regulatory background"""
    title: str = Field(..., description="Title of the regulatory overview")
    description: str = Field(..., description="Detailed description of regulatory overview")
    highlights: List[SummaryHighlight] = Field(..., description="List of key highlights")


class RegulatoryFinding(BaseModel):
    """Individual finding in regulatory analysis"""
    status: Literal["found", "missing"] = Field(..., description="Status of the finding")
    field: str = Field(..., description="Field identifier")
    label: str = Field(..., description="Human-readable label")
    value: str = Field(..., description="Value or description of the finding")
    source_file: Optional[str] = Field(None, description="Source file name")
    source_page: Optional[int] = Field(None, description="Page number in source file")
    tooltip: Optional[str] = Field(None, description="Tooltip text for the finding")
    suggestion: Optional[str] = Field(None, description="Suggestion for improvement")
    confidence_score: Optional[float] = Field(None, ge=0, le=100, description="Confidence score (0-100)")
    user_action: Optional[bool] = Field(None, description="User action taken on this finding")


class RegulatoryConflict(BaseModel):
    """Individual conflict identified in regulatory analysis"""
    field: str = Field(..., description="Field where conflict was found")
    phrase: str = Field(..., description="Conflicting phrase or statement")
    conflict: str = Field(..., description="Description of the conflict")
    source: str = Field(..., description="Source file where conflict was found")
    suggestion: str = Field(..., description="Suggestion to resolve the conflict")
    user_action: Optional[bool] = Field(None, description="User action taken on this conflict")


class RegulatoryBackgroundData(BaseModel):
    """Complete regulatory background data structure"""
    summary: RegulatorySummary = Field(..., description="Regulatory summary information")
    findings: List[RegulatoryFinding] = Field(..., description="List of regulatory findings")
    conflicts: List[RegulatoryConflict] = Field(..., description="List of regulatory conflicts")


# Request/Response schemas
class CreateRegulatoryBackgroundRequest(BaseModel):
    """Request schema for creating regulatory background"""
    summary: RegulatorySummary
    findings: List[RegulatoryFinding]
    conflicts: List[RegulatoryConflict]


class UpdateRegulatoryBackgroundRequest(BaseModel):
    """Request schema for updating regulatory background"""
    summary: Optional[RegulatorySummary] = None
    findings: Optional[List[RegulatoryFinding]] = None
    conflicts: Optional[List[RegulatoryConflict]] = None


class RegulatoryBackgroundResponse(BaseModel):
    """Response schema for regulatory background"""
    id: str = Field(..., description="Regulatory background ID")
    product_id: str = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    product_code: Optional[str] = Field(None, description="Product code")
    summary: RegulatorySummary
    findings: List[RegulatoryFinding]
    conflicts: List[RegulatoryConflict]
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class RegulatoryBackgroundListResponse(BaseModel):
    """Response schema for list of regulatory backgrounds"""
    regulatory_backgrounds: List[RegulatoryBackgroundResponse] = Field(..., description="List of regulatory backgrounds")
    total: int = Field(..., description="Total number of regulatory backgrounds")
