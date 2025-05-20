from pydantic import BaseModel


class ProductVersionControlResponse(BaseModel):
    version: str
    comment: str
    created_at: str
    created_by: str
