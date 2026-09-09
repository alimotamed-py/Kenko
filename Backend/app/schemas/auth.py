from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class RequestOTP(BaseModel):
    model_config = ConfigDict(extra="forbid")
    phone_number: str = Field(..., min_length=11, max_length=11, pattern=r"^09\d{9}$")


class VerifyOTP(BaseModel):
    model_config = ConfigDict(extra="forbid")
    phone_number: str = Field(..., min_length=11, max_length=11, pattern=r"^09\d{9}$")
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    
    
class CurrentUserResponse(BaseModel):
    id: int
    phone_number: str
    is_active: bool
    is_verified: bool
    created_at: datetime