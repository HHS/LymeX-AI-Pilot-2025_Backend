from src.modules.product.regulatory_pathway.model import RegulatoryPathway
from src.modules.product.milestone_planning.model import MilestonePlanning
from src.modules.product.review_program.model import ReviewProgram
from src.modules.product.cost_estimation.model import CostEstimation
from src.modules.product.models import Product
from .schema import (
    FinalRegulatoryReportResponse,
    RegulatoryPathwaySummary,
    CostBreakdown,
    SubmissionTimelineItem,
    MajorSubmissionRequirement,
    SpecialReviewProgramEligibility,
)


async def get_final_regulatory_report(product_id: str) -> FinalRegulatoryReportResponse:
    # Fetch product (for project name)
    product = await Product.get(product_id)
    project_name = product.name if product else None

    # Fetch regulatory pathway
    reg_pathway = await RegulatoryPathway.find_one({"product_id": product_id})

    regulatory_pathway_summary = RegulatoryPathwaySummary(
        recommended_pathway=reg_pathway.recommended_pathway if reg_pathway else "",
        device_class="Class 1",
        review_type="Traditional",
        description=getattr(reg_pathway, "description", None) if reg_pathway else None,
    )

    # Fetch cost estimation (match pathway with recommended_pathway)
    cost_estimation = await CostEstimation.find_one({"product_id": product_id})

    cost_analysis = None
    if cost_estimation and cost_estimation.pathways and reg_pathway:
        for pathway in cost_estimation.pathways:
            if pathway.pathway == reg_pathway.recommended_pathway:
                cost_analysis = pathway.costAnalysis
                break

    cost_breakdown = CostBreakdown(
        base_mdufa_fee=cost_analysis.base_mdufa_fee if cost_analysis else "",
        sbd_fee_reduction=cost_analysis.sbd_fee_reduction if cost_analysis else "",
        estimated_consulting_costs=(
            cost_analysis.estimated_consulting_costs if cost_analysis else ""
        ),
        clinical_trial_costs=(
            cost_analysis.clinical_trial_costs if cost_analysis else ""
        ),
        total_estimated_cost=(
            cost_analysis.total_estimated_cost if cost_analysis else ""
        ),
    )

    # Fetch milestone planning (timeline)
    milestone = await MilestonePlanning.find_one({"product_id": product_id})
    submission_timeline = []
    if milestone and hasattr(milestone, "milestones"):
        for item in milestone.milestones:
            submission_timeline.append(
                SubmissionTimelineItem(
                    row=item.row,
                    start_date=item.start_date,
                    end_date=item.end_date,
                    name=item.name,
                )
            )

    # Major submission requirements (dummy for now)
    major_submission_requirements = [
        MajorSubmissionRequirement(name="Device Description", completed=True),
        MajorSubmissionRequirement(name="Substantial Equivalence", completed=True),
        MajorSubmissionRequirement(name="Performance Testing", completed=True),
        MajorSubmissionRequirement(name="Sterilization Validation", completed=True),
    ]

    # Special review program eligibility
    review_program = await ReviewProgram.find_one({"productId": product_id})
    special_review_program_eligibility = []
    if review_program:
        for prog in review_program.specialityPrograms:
            special_review_program_eligibility.append(
                SpecialReviewProgramEligibility(
                    program_name=prog.programName,
                    is_qualified=prog.isQualified,
                    reason=prog.reason,
                )
            )

    return FinalRegulatoryReportResponse(
        product_id=product_id,
        project_name=project_name,
        regulatory_pathway_summary=regulatory_pathway_summary,
        cost_breakdown=cost_breakdown,
        submission_timeline=submission_timeline,
        major_submission_requirements=major_submission_requirements,
        special_review_program_eligibility=special_review_program_eligibility,
    )
