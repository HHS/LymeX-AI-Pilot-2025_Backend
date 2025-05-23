from pydantic import BaseModel


class ResetToVersionRequest(BaseModel):
    version: str
    comment: str


class ProductVersionControlResponse(BaseModel):
    version: str
    is_current_version: bool
    comment: str
    created_at: str
    created_by: str
