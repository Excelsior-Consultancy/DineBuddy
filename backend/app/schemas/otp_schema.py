from pydantic import BaseModel, Field


class OTPRequest(BaseModel):
    phone: str = Field(..., example="9876543210")


class OTPVerify(BaseModel):
    phone: str
    otp: str
