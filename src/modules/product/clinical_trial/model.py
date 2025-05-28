from beanie import Document, PydanticObjectId

from src.modules.product.clinical_trial.schema import (
    ClinicalTrialResponse,
    ClinicalTrialStatus,
)


class ClinicalTrial(Document):
    product_id: str
    name: str
    sponsor: str
    study_design: str
    enrollment: int
    status: ClinicalTrialStatus
    phase: int
    outcome: str
    inclusion_criteria: list[str]
    marked: bool = False

    class Settings:
        name = "clinical_trial"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_clinical_trial_response(self) -> ClinicalTrialResponse:
        return ClinicalTrialResponse(
            id=str(self.id),
            product_id=self.product_id,
            name=self.name,
            sponsor=self.sponsor,
            study_design=self.study_design,
            enrollment=self.enrollment,
            status=self.status,
            phase=self.phase,
            outcome=self.outcome,
            inclusion_criteria=self.inclusion_criteria,
            marked=self.marked,
        )
