from datetime import datetime
from typing import List
from beanie import Document, PydanticObjectId
from pydantic import Field

from src.modules.product.regulatory_background.schema import (
    RegulatorySummary,
    RegulatoryFinding,
    RegulatoryConflict,
    RegulatoryBackgroundResponse,
)


class RegulatoryBackground(Document):
    """Regulatory background document model"""

    product_id: str = Field(
        ..., description="Product ID this regulatory background belongs to"
    )
    summary: RegulatorySummary = Field(
        ..., description="Regulatory summary information"
    )
    findings: List[RegulatoryFinding] = Field(
        ..., description="List of regulatory findings"
    )
    conflicts: List[RegulatoryConflict] = Field(
        ..., description="List of regulatory conflicts"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    class Settings:
        name = "regulatory_background"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_regulatory_background_response(
        self, product_name: str, product_code: str | None = None
    ) -> RegulatoryBackgroundResponse:
        """Convert to response format with product information"""
        return RegulatoryBackgroundResponse(
            id=str(self.id),
            product_id=self.product_id,
            product_name=product_name,
            product_code=product_code,
            summary=self.summary,
            findings=self.findings,
            conflicts=self.conflicts,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()

    def get_findings_by_status(self, status: str) -> List[RegulatoryFinding]:
        """Get all findings with a specific status"""
        return [finding for finding in self.findings if finding.status == status]

    def get_findings_by_field(self, field: str) -> List[RegulatoryFinding]:
        """Get all findings for a specific field"""
        return [finding for finding in self.findings if finding.field == field]

    def get_conflicts_by_field(self, field: str) -> List[RegulatoryConflict]:
        """Get all conflicts for a specific field"""
        return [conflict for conflict in self.conflicts if conflict.field == field]

    def get_findings_with_user_action(self) -> List[RegulatoryFinding]:
        """Get all findings that have user actions"""
        return [finding for finding in self.findings if finding.user_action is not None]

    def get_conflicts_with_user_action(self) -> List[RegulatoryConflict]:
        """Get all conflicts that have user actions"""
        return [
            conflict for conflict in self.conflicts if conflict.user_action is not None
        ]

    def get_high_confidence_findings(
        self, threshold: float = 80.0
    ) -> List[RegulatoryFinding]:
        """Get all findings with confidence score above threshold"""
        return [
            finding
            for finding in self.findings
            if finding.confidence_score and finding.confidence_score >= threshold
        ]

    def get_missing_findings(self) -> List[RegulatoryFinding]:
        """Get all findings with 'missing' status"""
        return self.get_findings_by_status("missing")

    def get_found_findings(self) -> List[RegulatoryFinding]:
        """Get all findings with 'found' status"""
        return self.get_findings_by_status("found")
