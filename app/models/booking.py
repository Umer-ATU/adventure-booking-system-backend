from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]



class UserDetails(BaseModel):
    full_name: str = Field(..., min_length=2)
    email: EmailStr
    phone: str = Field(..., min_length=7)
    consent: bool

class Booking(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    ride_id: PyObjectId = Field(...)
    user_details: UserDetails
    seats_booked: int = Field(1, gt=0)
    total_price: float = Field(..., gt=0)
    payment_status: str = Field(default="PENDING")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "ride_id": "659d8a5b9d8a5b9d8a5b9d8a",
                "user_details": {
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+123456789",
                    "consent": True
                },
                "seats_booked": 2,
                "total_price": 100.0,
                "payment_status": "PENDING"
            }
        }
    )
