from datetime import datetime, timezone
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


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
    phone: Optional[str] = Field(
        None,
        pattern=r"^\+?[1-9]\d{1,14}$",
        description="Phone number of the user",
        examples=["+1234567890"],
    )


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Updated first name of the user"
    )
    last_name: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Updated last name of the user"
    )
    phone: Optional[str] = Field(
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
class UserResponse(BaseModel):
    id: str = Field(..., description="Unique identifier of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    first_name: str = Field(..., description="First name of the user")
    last_name: str = Field(..., description="Last name of the user")
    avatar: str = Field(..., description="Avatar URL of the user")
    phone: Optional[str] = Field(None, description="Phone number of the user")
    title: Optional[str] = Field(None, description="Title of the user")
    enable_verify_login: bool = Field(
        True, description="Indicates if login verification is enabled"
    )
    enable_totp: bool = Field(
        False, description="Indicates if TOTP is enabled for the user"
    )
    verified_at: Optional[datetime] = Field(
        None, description="Indicates if the user's email is verified"
    )
    policy_accepted_at: Optional[datetime] = Field(
        None, description="Indicates if the user has accepted the policy"
    )
    deleted_at: Optional[datetime] = None
    locked_until: Optional[datetime] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)


class UpdateAvatarUrlResponse(BaseModel):
    url: str = Field(
        ...,
        description="URL to upload the avatar, using put method. Expires in 5 minutes",
    )
