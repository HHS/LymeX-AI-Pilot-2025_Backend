from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from src.modules.authorization.roles import CompanyMemberStatus, CompanyRoles

# -------- Request DTOs --------


class CreateCompanyRequest(BaseModel):
    admin_user_id: str = Field(..., description="Admin user ID")
    name: str = Field(..., description="Company name")
    description: str = Field(..., description="Company description")
    industry: str = Field(..., description="Industry Name")
    street_address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")


class UpdateCompanyRequest(BaseModel):
    name: Optional[str] = Field(None, description="Company name")
    description: Optional[str] = Field(None, description="Company description")
    industry: Optional[str] = Field(None, description="Industry Name")
    street_address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")


class CreateInvitationRequest(BaseModel):
    email: EmailStr = Field(..., description="Invited user email")
    role: CompanyRoles = Field(..., description="Invited user role")


class AcceptInvitationRequest(BaseModel):
    company_id: str = Field(..., description="Company ID")


class DeactivateMemberRequest(BaseModel):
    user_id: str = Field(..., description="User ID")


class RecoverMemberRequest(BaseModel):
    user_id: str = Field(..., description="User ID")


class UpdateMemberRoleRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    role: CompanyRoles = Field(..., description="User role")


class AddCompanyAdminRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    company_id: str = Field(..., description="Company ID")


# -------- Response DTOs --------


class CompanyResponse(BaseModel):
    id: str = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    description: str = Field(..., description="Company description")
    industry: str = Field(..., description="Industry Name")
    street_address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    logo: str = Field(..., description="Company logo URL")
    created_at: datetime = Field(..., description="Created at timestamp")
    updated_at: datetime = Field(..., description="Updated at timestamp")


class CompanyRoleResponse(BaseModel):
    status: CompanyMemberStatus = Field(..., description="Company member status")
    role: CompanyRoles = Field(..., description="Company member role")


class CompanyMemberResponse(BaseModel):
    user_id: str = Field(..., description="User ID")
    status: CompanyMemberStatus = Field(..., description="Company member status")
    role: CompanyRoles = Field(..., description="Company member role")
    email: EmailStr = Field(..., description="Company member email")
    added_at: datetime = Field(..., description="Added at timestamp")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")


class UpdateCompanyLogoResponse(BaseModel):
    url: str = Field(..., description="Company logo upload URL")
