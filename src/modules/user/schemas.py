from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field
from src.modules.authorization.roles import CompanyMemberStatus, CompanyRoles


# -------- Request DTOs --------
class UserCreateRequest(BaseModel):
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="First name of the user",
        examples=["John"],
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Last name of the user",
        examples=["Doe"],
    )
    email: EmailStr = Field(
        ..., description="Email address of the user", examples=["example@domain.com"]
    )
    password: str = Field(
        ...,
        description="Password for the user account",
        examples=["very_secure_password"],
    )
    phone: str | None = Field(
        None,
        pattern=r"^\+?[1-9]\d{1,14}$",
        description="Phone number of the user",
        examples=["+1234567890"],
    )


class UserUpdateRequest(BaseModel):
    first_name: str | None = Field(
        None, min_length=1, max_length=50, description="Updated first name of the user"
    )
    last_name: str | None = Field(
        None, min_length=1, max_length=50, description="Updated last name of the user"
    )
    phone: str | None = Field(
        None,
        pattern=r"^\+?[1-9]\d{1,14}$",
        description="Updated phone number of the user",
    )


class UserUpdatePasswordRequest(BaseModel):
    current_password: str = Field(..., description="Current password of the user")
    new_password: str = Field(
        ...,
        description="New password for the user account",
    )


# -------- Response DTO --------


class ActiveProduct(BaseModel):
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    code: str | None = Field(None, description="Product code")


class UserCompany(BaseModel):
    id: str = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    description: str = Field(..., description="Company description")
    industry: str = Field(..., description="Industry Name")
    street_address: str | None = Field(None, description="Street address")
    city: str | None = Field(None, description="City")
    state: str | None = Field(None, description="State")
    logo: str = Field(..., description="Company logo URL")
    created_at: datetime = Field(..., description="Created at timestamp")
    updated_at: datetime = Field(..., description="Updated at timestamp")
    role: CompanyRoles = Field(
        ...,
        description="Role of the user in the company",
        examples=[role.value for role in CompanyRoles],
    )
    status: CompanyMemberStatus = Field(
        ...,
        description="Status of the user in the company",
        examples=[status.value for status in CompanyMemberStatus],
    )
    active_product: ActiveProduct | None = Field(
        None, description="Active product for this company"
    )


class UserResponse(BaseModel):
    id: str = Field(..., description="Unique identifier of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    first_name: str = Field(..., description="First name of the user")
    last_name: str = Field(..., description="Last name of the user")
    avatar: str = Field(..., description="Avatar URL of the user")
    phone: str | None = Field(None, description="Phone number of the user")
    title: str | None = Field(None, description="Title of the user")
    enable_verify_login: bool = Field(
        True, description="Indicates if login verification is enabled"
    )
    enable_totp: bool = Field(
        False, description="Indicates if TOTP is enabled for the user"
    )
    verified_at: datetime | None = Field(
        None, description="Indicates if the user's email is verified"
    )
    policy_accepted_at: datetime | None = Field(
        None, description="Indicates if the user has accepted the policy"
    )
    deleted_at: datetime | None = None
    locked_until: datetime | None = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
    companies: list[UserCompany] | None = Field(
        None, description="List of companies the user is associated with"
    )
    is_system_admin: bool = Field(
        description="Indicates if the user is a system administrator"
    )


class UpdateAvatarUrlResponse(BaseModel):
    url: str = Field(
        ...,
        description="URL to upload the avatar, using put method. Expires in 5 minutes",
    )


class CompanyAdminUpdateUserRequest(BaseModel):
    first_name: str | None = Field(
        None, min_length=1, max_length=50, description="Updated first name of the user"
    )
    last_name: str | None = Field(
        None, min_length=1, max_length=50, description="Updated last name of the user"
    )
    email: EmailStr | None = Field(
        None,
        description="Email address of the user",
    )
    role: CompanyRoles | None = Field(
        None,
        description="Role of the user in the company",
        examples=[role.value for role in CompanyRoles],
    )
    status: CompanyMemberStatus = Field(None, description="Company member status")


class AddSystemAdminRequest(BaseModel):
    user_id: str | None = Field(
        None,
    )
    user_ids: list[str] | None = Field(
        None,
    )
