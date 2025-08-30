from datetime import datetime
from beanie import Document, PydanticObjectId
from fastapi import HTTPException
from src.infrastructure.minio import generate_get_object_presigned_url
from src.modules.product.analyzing_status import AnalyzingStatus
from src.modules.product.competitive_analysis.schema import (
    CompetitiveAnalysisCompareItemResponse,
    CompetitiveAnalysisCompareResponse,
    CompetitiveAnalysisDetailBase,
    CompetitiveAnalysisDetailSchema,
    CompetitiveAnalysisResponse,
    CompetitiveAnalysisSource,
    CompetitiveDeviceAnalysisItemResponse,
    CompetitiveDeviceAnalysisResponse,
    LLMGapFinding,
    LLMPredicateRow,
    PredicateLLMAnalysisResponse,
    SourceWithUrl,
)
from src.modules.product.competitive_analysis.analyze_competitive_analysis_progress import (
    get_analyze_competitive_analysis_progress,
)


class CompetitiveAnalysisDetail(Document, CompetitiveAnalysisDetailBase):
    product_simple_name: str
    confidence_score: float
    sources: list[CompetitiveAnalysisSource]
    is_ai_generated: bool
    use_system_data: bool

    class Settings:
        name = "competitive_analysis_detail"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }


class PredicateLLMAnalysis(Document):
    product_id: str
    product_name: str
    competitor_id: str | None = None
    competitor_name: str | None = None
    rows: list[LLMPredicateRow]
    gaps: list[LLMGapFinding]
    model_used: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    class Settings:
        name = "predicate_llm_analysis"

    def to_predicate_llm_analysis_response(
        self,
    ) -> PredicateLLMAnalysisResponse:
        return PredicateLLMAnalysisResponse(
            id=str(self.id),
            product_id=self.product_id,
            product_name=self.product_name,
            competitor_id=self.competitor_id,
            competitor_name=self.competitor_name,
            rows=self.rows,
            gaps=self.gaps,
            model_used=self.model_used,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


async def create_source_with_url(source: CompetitiveAnalysisSource) -> SourceWithUrl:
    url = await generate_get_object_presigned_url(
        source.key,
        expiration_seconds=3600,
    )
    return SourceWithUrl(
        name=source.name,
        document_name=url.split("?")[0].split("/")[-1],
        url=url,
    )


class CompetitiveAnalysis(Document):
    product_id: str
    competitive_analysis_detail_id: str
    is_self_analysis: bool

    accepted: bool | None = None
    accept_reject_reason: str | None = None
    accept_reject_by: str | None = None

    class Settings:
        name = "competitive_analysis"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    async def to_competitive_analysis_response(
        self,
        product,
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

        sources_with_urls = [
            await create_source_with_url(source)
            for source in competitive_analysis_detail.sources
        ]

        analyze_competitive_analysis_progress = (
            await get_analyze_competitive_analysis_progress(
                self.product_id,
            )
        )
        analyze_competitive_analysis_progress_status = (
            analyze_competitive_analysis_progress.to_analyze_competitive_analysis_progress_response().analyzing_status
            if analyze_competitive_analysis_progress
            else AnalyzingStatus.PENDING
        )

        return CompetitiveAnalysisResponse(
            id=str(self.id),
            product_id=self.product_id if self.is_self_analysis else None,
            product_name=(
                product.name
                if self.is_self_analysis
                else competitive_analysis_detail.product_name
            ),
            reference_number=competitive_analysis_detail.regulation_number,
            regulatory_pathway=competitive_analysis_detail.regulatory_pathway,
            fda_approved=competitive_analysis_detail.fda_approved,
            ce_marked=competitive_analysis_detail.ce_marked,
            is_ai_generated=competitive_analysis_detail.is_ai_generated,
            use_system_data=competitive_analysis_detail.use_system_data,
            data_source=(
                "Internal Product"
                if self.is_self_analysis
                else (
                    "System Data"
                    if competitive_analysis_detail.use_system_data
                    else "User Uploaded"
                )
            ),
            confidence_score=competitive_analysis_detail.confidence_score,
            sources=[source.name for source in competitive_analysis_detail.sources],
            sources_with_urls=sources_with_urls,
            accepted=self.accepted,
            accept_reject_reason=self.accept_reject_reason,
            accept_reject_by=self.accept_reject_by,
            comparison=self.to_competitive_compare_response(
                self_product_detail,
                competitive_analysis_detail,
                analyze_competitive_analysis_progress_status,
            ),
            analyzing_status=analyze_competitive_analysis_progress_status,
        )

    def to_competitive_compare_response(
        self,
        self_product_detail: CompetitiveAnalysisDetail,
        competitor_product_detail: CompetitiveAnalysisDetail,
        analyze_competitive_analysis_progress_status: AnalyzingStatus,
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
            accepted=self.accepted,
            accept_reject_reason=self.accept_reject_reason,
            accept_reject_by=self.accept_reject_by,
            analyzing_status=analyze_competitive_analysis_progress_status,
        )

    async def to_competitive_device_analysis_response(
        self,
    ) -> CompetitiveDeviceAnalysisResponse:
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
