from pydantic import BaseModel


class UnifiedSearchResult(BaseModel):
    product_id: str
    product_name: str
    module: str
    matched_key: str
    matched_value: str
