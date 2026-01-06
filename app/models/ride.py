from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

# Represents an ObjectId field in the database.
# It will be represented as a string in the model.
PyObjectId = Annotated[str, BeforeValidator(str)]

class Ride(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str = Field(...)
    description: str = Field(...)
    image_url: Optional[str] = None
    price: float = Field(..., gt=0)
    location: str = Field(...)
    date: datetime = Field(...)
    max_seats: int = Field(..., gt=0)
    available_seats: int = Field(..., ge=0)
    is_active: bool = True
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "title": "Risky Rollercoaster",
                "description": "The steepest drop in the county!",
                "price": 50.0,
                "location": "Adventure Land",
                "date": "2024-12-25T10:00:00",
                "max_seats": 20,
                "available_seats": 20,
                "is_active": True
            }
        }
    )
