from datetime import datetime
from beanie import Document, PydanticObjectId

from src.modules.product.product_profile.schema import Feature
from src.modules.product.competitive_analysis.schema import (
    AnalyzeCompetitiveAnalysisProgressResponse,
    CompetitiveAnalysisResponse,
)


class CompetitiveAnalysis(Document):
    reference_product_id: str
    product_name: str
    category: str
    regulatory_pathway: str
    clinical_study: str
    fda_approved: bool
    is_ai_generated: bool
    features: list[Feature]
    claims: list[str]
    reference_number: str
    confidence_score: float
    sources: list[str]

    class Settings:
        name = "competitive_analysis"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    async def to_competitive_analysis_response(self) -> CompetitiveAnalysisResponse:
        return CompetitiveAnalysisResponse(
            id=str(self.id),
            product_name=self.product_name,
            reference_number=self.reference_number,
            regulatory_pathway=self.regulatory_pathway,
            fda_approved=self.fda_approved,
            is_ai_generated=self.is_ai_generated,
            confidence_score=self.confidence_score,
            sources=self.sources,
        )


class AnalyzeCompetitiveAnalysisProgress(Document):
    reference_product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_competitive_analysis_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_analyze_competitive_analysis_progress_response(
        self,
    ) -> AnalyzeCompetitiveAnalysisProgressResponse:
        return {
            "reference_product_id": self.reference_product_id,
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "updated_at": self.updated_at,
        }
