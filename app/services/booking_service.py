from bson import ObjectId
from app.core.database import booking_collection
from app.models.booking import Booking


async def create_booking(data):
    # Check if booking already exists (by email)
    existing = await booking_collection.find_one({"email": data.email})
    if existing:
        return None

    booking = Booking(**data.dict())
    result = await booking_collection.insert_one(booking.to_dict())
    return str(result.inserted_id)


async def get_booking(booking_id: str):
    return await booking_collection.find_one(
        {"_id": ObjectId(booking_id)}
    )
