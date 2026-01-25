from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from enum import Enum

class AdventurePark(str, Enum):
    RISKY_ROLLERCOASTER = "Risky Rollercoaster"
    HAUNTED_MANSION = "Haunted Mansion"
    NIGHTFALL_WOODS = "Nightfall Woods"

class BookingCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    adventure_park: AdventurePark
    consent: bool

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if not v or len(v.strip()) < 7:
            raise ValueError("Phone must be at least 7 characters")
        return v.strip()

    @field_validator("consent")
    @classmethod
    def validate_consent(cls, v):
        if not v:
            raise ValueError("Health & Warning consent is required")
        return v

class BookingUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    adventure_park: Optional[AdventurePark] = None
    consent: Optional[bool] = None

class BookingResponse(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    adventure_park: str
    consent: bool
