from datetime import datetime
from typing import Annotated, Optional
from beanie import Document, Indexed, PydanticObjectId
from src.modules.company.storage import get_company_logo_url
from src.modules.company.schema import CompanyResponse, CompanyRoleResponse
from src.modules.authorization.roles import CompanyMemberStatus, CompanyRoles


class Company(Document):
    name: Annotated[str, Indexed(unique=True)]
    description: str
    industry: str
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "company"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    async def to_company_response(self) -> CompanyResponse:
        logo_url = await get_company_logo_url(self.id)
        return CompanyResponse(
            id=str(self.id),
            name=self.name,
            description=self.description,
            industry=self.industry,
            street_address=self.street_address,
            city=self.city,
            state=self.state,
            logo=logo_url,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class CompanyMember(Document):
    status: CompanyMemberStatus
    role: CompanyRoles
    company_id: str
    user_id: str
    created_at: datetime

    class Settings:
        name = "company_member"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_company_role_response(self) -> CompanyRoleResponse:
        return CompanyRoleResponse(
            status=self.status,
            role=self.role,
        )
