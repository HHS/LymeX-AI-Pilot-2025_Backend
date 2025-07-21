from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import BaseModel

from src.modules.product.claim_builder.schema import (
    IFU,
    AnalyzeClaimBuilderProgressResponse,
    ClaimBuilderResponse,
    Compliance,
    Draft,
    MissingElement,
    PhraseConflict,
    RiskIndicator,
)
from src.modules.product.analyzing_status import AnalyzingStatus


class ClaimBuilderPydantic(BaseModel):
    product_id: str
    draft: list[Draft]
    key_phrases: list[str]
    ifu: list[IFU]
    compliance: list[Compliance]
    missing_elements: list[MissingElement]
    risk_indicators: list[RiskIndicator]
    phrase_conflicts: list[PhraseConflict]
    user_acceptance: bool = False


class ClaimBuilder(Document):
    product_id: str
    draft: list[Draft]
    key_phrases: list[str]
    ifu: list[IFU]
    compliance: list[Compliance]
    missing_elements: list[MissingElement]
    risk_indicators: list[RiskIndicator]
    phrase_conflicts: list[PhraseConflict]
    user_acceptance: bool = False

    class Settings:
        name = "claim_builder"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_claim_builder_response(self, product) -> ClaimBuilderResponse:
        return ClaimBuilderResponse(
            product_id=self.product_id,
            product_code=product.code,
            product_name=product.name,
            draft=self.draft,
            key_phrases=self.key_phrases,
            ifu=self.ifu,
            compliance=self.compliance,
            missing_elements=self.missing_elements,
            risk_indicators=self.risk_indicators,
            phrase_conflicts=self.phrase_conflicts,
            user_acceptance=self.user_acceptance,
        )

    def to_claim_builder_pydantic(self) -> ClaimBuilderPydantic:
        return ClaimBuilderPydantic(
            product_id=self.product_id,
            draft=self.draft,
            key_phrases=self.key_phrases,
            ifu=self.ifu,
            compliance=self.compliance,
            missing_elements=self.missing_elements,
            risk_indicators=self.risk_indicators,
            phrase_conflicts=self.phrase_conflicts,
            user_acceptance=self.user_acceptance,
        )


class AnalyzeClaimBuilderProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_claim_builder_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_analyze_claim_builder_progress_response(
        self,
    ) -> AnalyzeClaimBuilderProgressResponse:
        return AnalyzeClaimBuilderProgressResponse(
            product_id=self.product_id,
            total_files=self.total_files,
            processed_files=self.processed_files,
            updated_at=self.updated_at,
            analyzing_status=(
                AnalyzingStatus.IN_PROGRESS
                if self.processed_files < self.total_files
                else AnalyzingStatus.COMPLETED
            ),
        )
