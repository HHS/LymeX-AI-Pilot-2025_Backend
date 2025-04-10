from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# -------- Request DTOs --------


class CheckTOTPRequest(BaseModel):
    code: str = Field(..., description="The TOTP code to check.")


class VerifyTOTPRequest(BaseModel):
    code: str = Field(..., description="The TOTP code to verify.")


# --------- Response DTOs --------


class CheckTOTPResponse(BaseModel):
    is_valid: bool = Field(..., description="Whether the TOTP code is valid or not.")


class SetupTOTPResponse(BaseModel):
    provisioning_uri: str = Field(
        ...,
        description="The QR code URI for the TOTP secret, used to generate the QR code.",
    )
