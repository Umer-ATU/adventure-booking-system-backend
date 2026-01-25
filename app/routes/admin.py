from fastapi import APIRouter, HTTPException, Header
from bson import ObjectId
from typing import List
from database import bookings_collection
from models import BookingUpdate, BookingResponse

router = APIRouter(prefix="/api/admin/bookings", tags=["admin"])

ADMIN_USERS = ["Wednesday", "Pugsley"]

async def verify_admin(x_admin_user: str = Header(None)):
    if not x_admin_user or x_admin_user not in ADMIN_USERS:
        raise HTTPException(status_code=403, detail="Admin access required")
    return x_admin_user

@router.get("", response_model=List[BookingResponse])
async def list_bookings(x_admin_user: str = Header(None)):
    await verify_admin(x_admin_user)
    bookings = []
    async for booking in bookings_collection.find():
        booking["id"] = str(booking["_id"])
        bookings.append(BookingResponse(**booking))
    return bookings

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: str, x_admin_user: str = Header(None)):
    await verify_admin(x_admin_user)
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(status_code=400, detail="Invalid booking ID")
    booking = await bookings_collection.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking["id"] = str(booking["_id"])
    return BookingResponse(**booking)

@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(booking_id: str, update: BookingUpdate, x_admin_user: str = Header(None)):
    await verify_admin(x_admin_user)
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(status_code=400, detail="Invalid booking ID")
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    if "adventure_park" in update_data:
        update_data["adventure_park"] = update_data["adventure_park"].value
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid update data provided")
    result = await bookings_collection.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking = await bookings_collection.find_one({"_id": ObjectId(booking_id)})
    booking["id"] = str(booking["_id"])
    return BookingResponse(**booking)

@router.delete("/{booking_id}", status_code=204)
async def delete_booking(booking_id: str, x_admin_user: str = Header(None)):
    await verify_admin(x_admin_user)
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(status_code=400, detail="Invalid booking ID")
    result = await bookings_collection.delete_one({"_id": ObjectId(booking_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    return None
