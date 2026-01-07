from fastapi import APIRouter, HTTPException
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import create_booking, get_booking

router = APIRouter(
    prefix="/api/bookings",
    tags=["Bookings"]
)

@router.post("", response_model=BookingResponse, status_code=201)
async def create_booking_api(booking: BookingCreate):
    booking_id = await create_booking(booking)

    if not booking_id:
        raise HTTPException(
            status_code=400,
            detail="Booking already exists"
        )

    return {
        "id": booking_id,
        **booking.dict()
    }

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking_api(booking_id: str):
    booking = await get_booking(booking_id)

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    booking["id"] = str(booking["_id"])
    booking.pop("_id")

    return booking
