from pydantic import BaseModel
from typing import List
from datetime import datetime


class SaveCustomTestPlanRequest(BaseModel):
    required_tests: List[str]
    internal_testing: bool
    external_testing: bool
    start_date: datetime
    end_date: datetime
    duration: str


class CustomTestPlanResponse(BaseModel):
    id: str
    product_id: str
    required_tests: List[str]
    internal_testing: bool
    external_testing: bool
    start_date: datetime
    end_date: datetime
    duration: str
