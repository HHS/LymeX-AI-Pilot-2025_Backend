from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RegulatoryPathwaySummary(BaseModel):
    recommended_pathway: str
    device_class: str
    review_type: str
    description: Optional[str] = None

class CostBreakdown(BaseModel):
    base_mdufa_fee: str
    sbd_fee_reduction: str
    estimated_consulting_costs: str
    clinical_trial_costs: str
    total_estimated_cost: str

class SubmissionTimelineItem(BaseModel):
    row: int
    start_date: datetime
    end_date: datetime
    name: str

class MajorSubmissionRequirement(BaseModel):
    name: str
    completed: bool

class SpecialReviewProgramEligibility(BaseModel):
    program_name: str
    is_qualified: bool
    reason: Optional[str] = None

class FinalRegulatoryReportResponse(BaseModel):
    product_id: str
    project_name: Optional[str]
    regulatory_pathway_summary: RegulatoryPathwaySummary
    cost_breakdown: CostBreakdown
    submission_timeline: List[SubmissionTimelineItem]
    major_submission_requirements: List[MajorSubmissionRequirement]
    special_review_program_eligibility: List[SpecialReviewProgramEligibility]
