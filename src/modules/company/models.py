from datetime import datetime
from typing import Annotated, Optional
from beanie import Document, Indexed, PydanticObjectId
from src.environment import environment
from src.modules.company.constants import COMPANY_LOGO_OBJECT_PREFIX
from src.modules.company.schema import CompanyResponse, CompanyRoleResponse
from src.modules.authorization.roles import CompanyMemberStatus, CompanyRoles


class Company(Document):
    name: Annotated[str, Indexed(unique=True)]
    description: str
    industry: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "company"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_company_response(self) -> CompanyResponse:
        return CompanyResponse(
            id=str(self.id),
            name=self.name,
            description=self.description,
            industry=self.industry,
            logo=f"{environment.minio_external_endpoint}/{environment.minio_bucket}/{COMPANY_LOGO_OBJECT_PREFIX}/{self.id}",
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
