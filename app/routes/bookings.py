from fastapi import APIRouter, HTTPException
from bson import ObjectId
from database import bookings_collection
from models import BookingCreate, BookingResponse

router = APIRouter(prefix="/api/bookings", tags=["bookings"])

@router.post("", response_model=BookingResponse, status_code=201)
async def create_booking(booking: BookingCreate):
    booking_dict = booking.model_dump()
    booking_dict["adventure_park"] = booking.adventure_park.value
    result = await bookings_collection.insert_one(booking_dict)
    booking_dict["id"] = str(result.inserted_id)
    return BookingResponse(**booking_dict)

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: str):
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(status_code=400, detail="Invalid booking ID")
    booking = await bookings_collection.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking["id"] = str(booking["_id"])
    return BookingResponse(**booking)
