from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


class BookingStatus(str, Enum):
    """Booking status enum."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class BookingBase(BaseModel):
    """Base booking schema with common fields."""
    full_name: str = Field(..., min_length=2, max_length=100, description="Customer full name")
    email: EmailStr = Field(..., description="Customer email address")
    phone: str = Field(..., min_length=10, max_length=20, description="Customer phone number")
    adventure_park: str = Field(..., description="Selected adventure park")
    consent: bool = Field(..., description="Health and safety consent acknowledgment")


class BookingCreate(BookingBase):
    """Schema for creating a new booking."""
    pass


class BookingUpdate(BaseModel):
    """Schema for updating a booking (admin only)."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    adventure_park: Optional[str] = None
    status: Optional[BookingStatus] = None


class BookingInDB(BookingBase):
    """Schema for booking stored in database."""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    status: BookingStatus = BookingStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class BookingResponse(BookingBase):
    """Schema for booking API response."""
    id: str = Field(..., alias="_id")
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True