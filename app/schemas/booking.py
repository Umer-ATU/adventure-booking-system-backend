from pydantic import BaseModel, EmailStr
from datetime import date


class BookingCreate(BaseModel):
    customer_name: str
    email: EmailStr
    adventure_type: str
    booking_date: date


class BookingResponse(BookingCreate):
    id: str
