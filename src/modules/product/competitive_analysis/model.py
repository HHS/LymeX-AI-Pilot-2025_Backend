from datetime import datetime
from beanie import Document, PydanticObjectId
from fastapi import HTTPException
from src.modules.product.product_profile.schema import AnalyzingStatus
from src.modules.product.competitive_analysis.schema import (
    AnalyzeCompetitiveAnalysisProgressResponse,
    CompetitiveAnalysisCompareItemResponse,
    CompetitiveAnalysisCompareResponse,
    CompetitiveAnalysisDetailBase,
    CompetitiveAnalysisDetailSchema,
    CompetitiveAnalysisResponse,
    CompetitiveDeviceAnalysisItemResponse,
    CompetitiveDeviceAnalysisResponse,
)


class CompetitiveAnalysisDetail(Document, CompetitiveAnalysisDetailBase):
    product_simple_name: str
    confidence_score: float
    sources: list[str]
    is_ai_generated: bool
    use_system_data: bool

    accepted: bool | None = None
    accept_reject_reason: str | None = None
    accept_reject_by: str | None = None

    class Settings:
        name = "competitive_analysis_detail"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }


class CompetitiveAnalysis(Document):
    product_id: str
    competitive_analysis_detail_id: str
    is_self_analysis: bool

    class Settings:
        name = "competitive_analysis"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    async def to_competitive_analysis_response(
        self,
    ) -> CompetitiveAnalysisResponse:
        self_product_competitive_analysis = await CompetitiveAnalysis.find_one(
            CompetitiveAnalysis.product_id == self.product_id,
            CompetitiveAnalysis.is_self_analysis == True,
        )
        if not self_product_competitive_analysis:
            raise HTTPException(
                status_code=404,
                detail="Self competitive analysis not found",
            )
        self_product_detail = await CompetitiveAnalysisDetail.get(
            self_product_competitive_analysis.competitive_analysis_detail_id
        )
        competitive_analysis_detail = await CompetitiveAnalysisDetail.get(
            self.competitive_analysis_detail_id
        )
        if not competitive_analysis_detail:
            raise HTTPException(
                status_code=500,
                detail="Competitive analysis detail not found",
            )

        return CompetitiveAnalysisResponse(
            id=str(self.id),
            product_name=competitive_analysis_detail.product_name,
            reference_number=competitive_analysis_detail.regulation_number,
            regulatory_pathway=competitive_analysis_detail.regulatory_pathway,
            fda_approved=competitive_analysis_detail.fda_approved,
            ce_marked=competitive_analysis_detail.ce_marked,
            is_ai_generated=competitive_analysis_detail.is_ai_generated,
            use_system_data=competitive_analysis_detail.use_system_data,
            confidence_score=competitive_analysis_detail.confidence_score,
            sources=competitive_analysis_detail.sources,
            accepted=competitive_analysis_detail.accepted,
            accept_reject_reason=competitive_analysis_detail.accept_reject_reason,
            accept_reject_by=competitive_analysis_detail.accept_reject_by,
            comparison=self.to_competitive_compare_response(
                self_product_detail, competitive_analysis_detail
            ),
        )

    def to_competitive_compare_response(
        self,
        self_product_detail: CompetitiveAnalysisDetail,
        competitor_product_detail: CompetitiveAnalysisDetail,
    ) -> CompetitiveAnalysisCompareResponse:
        your_product = CompetitiveAnalysisCompareItemResponse(
            product_name=self_product_detail.product_name,
            detail=CompetitiveAnalysisDetailSchema(**self_product_detail.model_dump()),
        )
        competitor = CompetitiveAnalysisCompareItemResponse(
            product_name=competitor_product_detail.product_name,
            detail=CompetitiveAnalysisDetailSchema(
                **competitor_product_detail.model_dump()
            ),
        )
        return CompetitiveAnalysisCompareResponse(
            your_product=your_product,
            competitor=competitor,
            accepted=competitor_product_detail.accepted,
            accept_reject_reason=competitor_product_detail.accept_reject_reason,
            accept_reject_by=competitor_product_detail.accept_reject_by,
        )

    async def to_competitive_device_analysis_response(
        self,
    ) -> CompetitiveDeviceAnalysisResponse:
        self_product_competitive_analysis = await CompetitiveAnalysis.find_one(
            CompetitiveAnalysis.product_id == self.product_id,
            CompetitiveAnalysis.is_self_analysis,
        )
        if not self_product_competitive_analysis:
            raise HTTPException(
                status_code=404,
                detail="Self competitive analysis not found",
            )
        self_product_detail = await CompetitiveAnalysisDetail.get(
            self_product_competitive_analysis.competitive_analysis_detail_id
        )
        competitive_analysis_detail = await CompetitiveAnalysisDetail.get(
            self.competitive_analysis_detail_id
        )
        return CompetitiveDeviceAnalysisResponse(
            your_device=CompetitiveDeviceAnalysisItemResponse(
                content=self_product_detail.indications_for_use_statement,
                instructions=self_product_detail.instructions,
                type_of_use=self_product_detail.type_of_use,
                fda_approved=self_product_detail.fda_approved,
                ce_marked=self_product_detail.ce_marked,
            ),
            competitor_device=CompetitiveDeviceAnalysisItemResponse(
                content=competitive_analysis_detail.indications_for_use_statement,
                instructions=competitive_analysis_detail.instructions,
                type_of_use=competitive_analysis_detail.type_of_use,
                fda_approved=competitive_analysis_detail.fda_approved,
                ce_marked=competitive_analysis_detail.ce_marked,
            ),
        )


class AnalyzeCompetitiveAnalysisProgress(Document):
    product_id: str
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
        return AnalyzeCompetitiveAnalysisProgressResponse(
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
