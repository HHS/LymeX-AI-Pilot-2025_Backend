from datetime import datetime
from beanie import Document, PydanticObjectId

from src.modules.product.models import Product
from src.modules.product.product_profile.model import ProductProfile
from src.modules.product.product_profile.schema import Feature, Performance
from src.modules.product.competitive_analysis.schema import (
    AnalyzeCompetitiveAnalysisProgressResponse,
    CompetitiveAnalysisCompareItemResponse,
    CompetitiveAnalysisCompareResponse,
    CompetitiveAnalysisCompareSummary,
    CompetitiveAnalysisResponse,
    CompetitiveDeviceAnalysisItemResponse,
    CompetitiveDeviceAnalysisKeyDifferenceResponse,
    CompetitiveDeviceAnalysisResponse,
)


class CompetitiveAnalysis(Document):
    reference_product_id: str
    product_name: str
    category: str
    regulatory_pathway: str
    clinical_study: str
    fda_approved: bool
    ce_marked: bool
    device_ifu_description: str
    key_differences: list[CompetitiveDeviceAnalysisKeyDifferenceResponse]
    recommendations: list[str]
    is_ai_generated: bool
    features: list[Feature]
    claims: list[str]
    reference_number: str
    confidence_score: float
    sources: list[str]
    performance: Performance
    price: int
    your_product_summary: CompetitiveAnalysisCompareSummary
    competitor_summary: CompetitiveAnalysisCompareSummary
    instructions: list[str]
    type_of_use: str

    class Settings:
        name = "competitive_analysis"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_competitive_analysis_response(self) -> CompetitiveAnalysisResponse:
        return CompetitiveAnalysisResponse(
            id=str(self.id),
            product_name=self.product_name,
            reference_number=self.reference_number,
            regulatory_pathway=self.regulatory_pathway,
            fda_approved=self.fda_approved,
            ce_marked=self.ce_marked,
            is_ai_generated=self.is_ai_generated,
            confidence_score=self.confidence_score,
            sources=self.sources,
        )

    def to_competitive_compare_response(
        self,
        product: Product,
        product_profile: ProductProfile,
    ) -> CompetitiveAnalysisCompareResponse:
        your_product = CompetitiveAnalysisCompareItemResponse(
            product_name=product.name,
            price=product_profile.price,
            features=product_profile.features,
            performance=product_profile.performance,
            summary=self.your_product_summary,
        )
        competitor = CompetitiveAnalysisCompareItemResponse(
            product_name=self.product_name,
            price=self.price,
            features=self.features,
            performance=self.performance,
            summary=self.competitor_summary,
        )
        return CompetitiveAnalysisCompareResponse(
            your_product=your_product,
            competitor=competitor,
        )

    def to_competitive_device_analysis_response(
        self,
        product_profile: ProductProfile,
    ) -> CompetitiveDeviceAnalysisResponse:
        return CompetitiveDeviceAnalysisResponse(
            your_device=CompetitiveDeviceAnalysisItemResponse(
                id=str(product_profile.id),
                content=product_profile.device_ifu_description,
                instructions=product_profile.instructions,
                type_of_use=product_profile.type_of_use,
                fda_approved=product_profile.fda_approved,
                ce_marked=product_profile.ce_marked,
            ),
            competitor_device=CompetitiveDeviceAnalysisItemResponse(
                id=str(self.id),
                content=self.device_ifu_description,
                instructions=self.instructions,
                type_of_use=self.type_of_use,
                fda_approved=self.fda_approved,
                ce_marked=self.ce_marked,
            ),
            key_differences=self.key_differences,
            recommendations=self.recommendations,
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
