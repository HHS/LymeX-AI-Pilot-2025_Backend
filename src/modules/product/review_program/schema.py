from pydantic import BaseModel
from typing import List


class SpecialityProgram(BaseModel):
    programName: str
    isQualified: bool
    reason: str
    benefits: List[str]


class ReviewProgramResponse(BaseModel):
    productId: str
    product_name: str
    product_code: str | None
    specialityPrograms: List[SpecialityProgram]
