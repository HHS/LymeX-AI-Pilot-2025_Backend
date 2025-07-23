from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field

from src.modules.product.analyzing_status import AnalyzingStatus
from src.modules.product.performance_testing.schema import (
    AnalyticalStudy,
    AnalyzePerformanceTestingProgressResponse,
    AnimalTesting,
    Biocompatibility,
    ClinicalStudy,
    ComparisonStudy,
    CyberSecurity,
    EMCSafety,
    Interoperability,
    ModuleStatus,
    PerformanceTestingResponse,
    RiskLevel,
    ShelfLife,
    SoftwarePerformance,
    SterilityValidation,
    WirelessCoexistence,
)


class PerformanceTesting(Document):
    product_id: str
    analytical: list[AnalyticalStudy] = Field([])
    comparison: list[ComparisonStudy] = Field([])
    clinical: list[ClinicalStudy] = Field([])
    animal_testing: AnimalTesting | None = None
    emc_safety: EMCSafety | None = None
    wireless: WirelessCoexistence | None = None
    software: SoftwarePerformance | None = None
    interoperability: Interoperability | None = None
    biocompatibility: Biocompatibility | None = None
    sterility: SterilityValidation | None = None
    shelf_life: ShelfLife | None = None
    cybersecurity: CyberSecurity | None = None
    overall_risk_level: RiskLevel | None = None
    status: ModuleStatus = ModuleStatus.PENDING
    missing_items: list[str] = Field([])

    class Settings:
        name = "performance_testing"
        use_state_management = True

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_performance_testing_response(self) -> PerformanceTestingResponse:
        return PerformanceTestingResponse(
            id=str(self.id),
            product_id=self.product_id,
            analytical=self.analytical,
            comparison=self.comparison,
            clinical=self.clinical,
            animal_testing=self.animal_testing,
            emc_safety=self.emc_safety,
            wireless=self.wireless,
            software=self.software,
            interoperability=self.interoperability,
            biocompatibility=self.biocompatibility,
            sterility=self.sterility,
            shelf_life=self.shelf_life,
            cybersecurity=self.cybersecurity,
            overall_risk_level=self.overall_risk_level,
            status=self.status,
            missing_items=self.missing_items,
        )


class AnalyzePerformanceTestingProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_performance_testing_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_analyze_performance_testing_progress_response(
        self,
    ) -> AnalyzePerformanceTestingProgressResponse:
        return AnalyzePerformanceTestingProgressResponse(
            product_id=self.product_id,
            total_files=self.total_files,
            processed_files=self.processed_files,
            updated_at=self.updated_at,
            analyzing_status=(
                AnalyzingStatus.IN_PROGRESS
                if self.processed_files == 0
                else AnalyzingStatus.COMPLETED
            ),
        )
