from datetime import datetime
from beanie import Document, PydanticObjectId

from src.modules.product.analyzing_status import AnalyzingStatus
from src.modules.product.regulatory_background.schema import (
    AnalyzeRegulatoryBackgroundProgressResponse,
    RegulatoryBackgroundBase,
    RegulatoryBackgroundResponse,
)


class RegulatoryBackground(Document, RegulatoryBackgroundBase):
    product_id: str

    class Settings:
        name = "regulatory_background"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_regulatory_background_response(
        self,
    ) -> RegulatoryBackgroundResponse:
        return RegulatoryBackgroundResponse(
            id=str(self.id),
            product_id=self.product_id,
            predicate_device_reference=self.predicate_device_reference,
            clinical_trial_requirements=self.clinical_trial_requirements,
            risk_classification=self.risk_classification,
            regulatory_submission_history=self.regulatory_submission_history,
            intended_use_statement=self.intended_use_statement,
        )


class AnalyzeRegulatoryBackgroundProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_regulatory_background_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_analyze_regulatory_background_progress_response(
        self,
    ) -> AnalyzeRegulatoryBackgroundProgressResponse:
        return AnalyzeRegulatoryBackgroundProgressResponse(
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
