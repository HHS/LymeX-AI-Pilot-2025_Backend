from beanie import PydanticObjectId
from fastapi import HTTPException, status
from src.modules.product.competitive_analysis.analyze_competitive_analysis_progress import (
    AnalyzeCompetitiveAnalysisProgress,
)
from src.modules.product.competitive_analysis.model import (
    CompetitiveAnalysis,
    CompetitiveAnalysisDetail,
)
from src.modules.product.competitive_analysis.storage import (
    clone_competitive_analysis_documents,
)


async def get_all_product_competitive_analysis(
    product_id: str,
) -> list[CompetitiveAnalysis]:
    competitive_analysis = await CompetitiveAnalysis.find(
        CompetitiveAnalysis.product_id == product_id,
    ).to_list()
    return competitive_analysis


async def get_product_competitive_analysis(
    product_id: str,
    competitive_analysis_id: PydanticObjectId | str,
) -> CompetitiveAnalysis:
    competitive_analysis = await CompetitiveAnalysis.get(
        competitive_analysis_id,
    )
    if not competitive_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitive analysis not found",
        )
    if competitive_analysis.product_id != product_id:
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
    if competitive_analysis.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this competitive analysis",
        )
    competitive_analysis_detail = await CompetitiveAnalysisDetail.get(
        competitive_analysis.competitive_analysis_detail_id,
    )
    await competitive_analysis.delete()

    if competitive_analysis_detail:
        await competitive_analysis_detail.delete()


async def delete_product_competitive_analysis(
    product_id: str,
) -> None:
    await CompetitiveAnalysis.find_many(
        CompetitiveAnalysis.product_id == product_id,
    ).delete_many()
    await AnalyzeCompetitiveAnalysisProgress.find_many(
        AnalyzeCompetitiveAnalysisProgress.product_id == product_id,
    ).delete_many()


async def clone_competitive_analysis(
    product_id: str | PydanticObjectId,
    new_product_id: str | PydanticObjectId,
) -> None:
    competitive_analysis = await CompetitiveAnalysis.find(
        CompetitiveAnalysis.product_id == product_id,
    ).to_list()
    if competitive_analysis:
        await CompetitiveAnalysis.insert_many([
            CompetitiveAnalysis(
                **analysis.model_dump(exclude={"id", "product_id"}),
                product_id=str(new_product_id),
            )
            for analysis in competitive_analysis
        ])

    analyze_competitive_analysis_progress = (
        await AnalyzeCompetitiveAnalysisProgress.find_one(
            AnalyzeCompetitiveAnalysisProgress.product_id == product_id,
        )
    )
    if analyze_competitive_analysis_progress:
        new_analyze_competitive_analysis_progress = AnalyzeCompetitiveAnalysisProgress(
            **analyze_competitive_analysis_progress.model_dump(
                exclude={"id", "product_id"},
            ),
            product_id=str(new_product_id),
        )
        await new_analyze_competitive_analysis_progress.insert()

    await clone_competitive_analysis_documents(
        product_id=str(product_id),
        new_product_id=str(new_product_id),
    )
