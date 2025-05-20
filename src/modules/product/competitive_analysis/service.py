from fastapi import HTTPException, status
from src.modules.product.competitive_analysis.model import (
    AnalyzeCompetitiveAnalysisProgress,
    CompetitiveAnalysis,
)
from src.modules.product.competitive_analysis.schema import (
    UpdateCompetitiveAnalysisRequest,
)


async def get_all_product_competitive_analysis(
    product_id: str,
) -> list[CompetitiveAnalysis]:
    competitive_analysis = await CompetitiveAnalysis.find(
        CompetitiveAnalysis.reference_product_id == product_id,
    ).to_list()
    return competitive_analysis


async def get_product_competitive_analysis(
    product_id: str,
    competitive_analysis_id: str,
) -> CompetitiveAnalysis:
    competitive_analysis = await CompetitiveAnalysis.get(
        competitive_analysis_id,
    )
    if not competitive_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitive analysis not found",
        )
    if competitive_analysis.reference_product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this competitive analysis",
        )
    return competitive_analysis


async def delete_competitive_analysis(
    product_id: str,
    competitive_analysis_id: str,
) -> None:
    competitive_analysis = await CompetitiveAnalysis.get(
        competitive_analysis_id,
    )
    if not competitive_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitive analysis not found",
        )
    if competitive_analysis.reference_product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this competitive analysis",
        )
    await competitive_analysis.delete()


async def update_competitive_analysis(
    product_id: str,
    competitive_analysis_id: str,
    payload: UpdateCompetitiveAnalysisRequest,
) -> CompetitiveAnalysis:
    competitive_analysis = await CompetitiveAnalysis.get(
        competitive_analysis_id,
    )
    if not competitive_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitive analysis not found",
        )
    if competitive_analysis.reference_product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this competitive analysis",
        )
    if payload.product_name is not None:
        competitive_analysis.product_name = payload.product_name
    if payload.category is not None:
        competitive_analysis.category = payload.category
    if payload.regulatory_pathway is not None:
        competitive_analysis.regulatory_pathway = payload.regulatory_pathway
    if payload.clinical_study is not None:
        competitive_analysis.clinical_study = payload.clinical_study
    if payload.fda_approved is not None:
        competitive_analysis.fda_approved = payload.fda_approved
    if payload.ce_marked is not None:
        competitive_analysis.ce_marked = payload.ce_marked
    if payload.is_ai_generated is not None:
        competitive_analysis.is_ai_generated = payload.is_ai_generated
    await competitive_analysis.save()
    return competitive_analysis


async def get_analyze_competitive_analysis_progress(
    product_id: str,
) -> AnalyzeCompetitiveAnalysisProgress:
    analyze_competitive_analysis_progress = (
        await AnalyzeCompetitiveAnalysisProgress.find_one(
            AnalyzeCompetitiveAnalysisProgress.reference_product_id == product_id,
        )
    )
    if not analyze_competitive_analysis_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analyze competitive analysis progress not found",
        )
    return analyze_competitive_analysis_progress


async def delete_product_competitive_analysis(
    product_id: str,
) -> None:
    await CompetitiveAnalysis.find_many(
        CompetitiveAnalysis.reference_product_id == product_id,
    ).delete_many()
    await AnalyzeCompetitiveAnalysisProgress.find_many(
        AnalyzeCompetitiveAnalysisProgress.reference_product_id == product_id,
    ).delete_many()
