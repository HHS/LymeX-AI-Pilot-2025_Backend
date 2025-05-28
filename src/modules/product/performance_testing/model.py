from datetime import datetime
from enum import Enum
from beanie import Document, PydanticObjectId

from src.modules.product.performance_testing.schema import (
    PerformanceTestingConfidentLevel,
    PerformanceTestingResponse,
    PerformanceTestingStatus,
    PerformanceTestingRiskLevel,
    PerformanceTestingReference,
    PerformanceTestingAssociatedStandard,
)


class PerformanceTesting(Document):
    product_id: str
    test_name: str
    test_description: str
    status: PerformanceTestingStatus
    risk_level: PerformanceTestingRiskLevel
    ai_confident: int | None = None
    confident_level: PerformanceTestingConfidentLevel | None = None
    ai_rationale: str | None = None
    references: list[PerformanceTestingReference] | None = None
    associated_standards: list[PerformanceTestingAssociatedStandard] | None = None
    rejected_justification: str | None = None
    created_at: datetime
    created_by: str

    class Settings:
        name = "performance_testing"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_performance_testing_response(self) -> PerformanceTestingResponse:
        return PerformanceTestingResponse(
            id=str(self.id),
            product_id=self.product_id,
            test_name=self.test_name,
            test_description=self.test_description,
            status=self.status,
            risk_level=self.risk_level,
            ai_confident=self.ai_confident,
            confident_level=self.confident_level,
            ai_rationale=self.ai_rationale,
            references=self.references,
            associated_standards=self.associated_standards,
            rejected_justification=self.rejected_justification,
            created_at=self.created_at,
            created_by=self.created_by,
        )
