from pydantic import BaseModel
from typing import List


class SpecialityProgram(BaseModel):
    programName: str
    isQualified: bool
    reason: str


class ReviewProgramResponse(BaseModel):
    productId: str
    specialityPrograms: List[SpecialityProgram]
