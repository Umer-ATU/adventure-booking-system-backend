"""
Enhanced booking repository for database operations.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.booking import BookingCreate, BookingUpdate, BookingInDB


class BookingRepository:
    """Repository for booking database operations."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.bookings

    async def create(
        self,
        booking: BookingCreate,
        user_id: Optional[str] = None,
        adventure_id: Optional[str] = None
    ) -> BookingInDB:
        """Create a new booking."""
        booking_dict = booking.model_dump()
        booking_dict["_id"] = str(ObjectId())
        booking_dict["created_at"] = datetime.utcnow()
        booking_dict["updated_at"] = datetime.utcnow()
        
        # Enhanced fields
        if user_id:
            booking_dict["user_id"] = user_id
        if adventure_id:
            booking_dict["adventure_id"] = adventure_id
        
        # Payment fields
        booking_dict["payment_status"] = "PENDING"
        booking_dict["stripe_payment_id"] = None
        booking_dict["invoice_number"] = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{booking_dict['_id'][:8].upper()}"

        await self.collection.insert_one(booking_dict)
        return BookingInDB(**booking_dict)

    async def get_by_id(self, booking_id: str) -> Optional[BookingInDB]:
        """Get a booking by ID."""
        if not ObjectId.is_valid(booking_id):
            return None
        booking = await self.collection.find_one({"_id": booking_id})
        if booking:
            return BookingInDB(**booking)
        return None

    async def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        payment_status: Optional[str] = None
    ) -> List[BookingInDB]:
        """Get bookings for a specific user."""
        query: Dict[str, Any] = {"user_id": user_id}
        if payment_status:
            query["payment_status"] = payment_status
            
        cursor = self.collection.find(query) \
            .skip(skip) \
            .limit(limit) \
            .sort("created_at", -1)
        bookings = await cursor.to_list(length=limit)
        return [BookingInDB(**booking) for booking in bookings]

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        payment_status: Optional[str] = None,
        adventure_id: Optional[str] = None
    ) -> tuple[List[BookingInDB], int]:
        """Get all bookings with pagination and filters."""
        query: Dict[str, Any] = {}
        if payment_status:
            query["payment_status"] = payment_status
        if adventure_id:
            query["adventure_id"] = adventure_id
            
        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query) \
            .skip(skip) \
            .limit(limit) \
            .sort("created_at", -1)
        bookings = await cursor.to_list(length=limit)
        return [BookingInDB(**booking) for booking in bookings], total

    async def update(
        self,
        booking_id: str,
        booking_update: BookingUpdate
    ) -> Optional[BookingInDB]:
        """Update a booking (admin only)."""
        if not ObjectId.is_valid(booking_id):
            return None

        update_data = booking_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(booking_id)

        update_data["updated_at"] = datetime.utcnow()

        await self.collection.update_one(
            {"_id": booking_id},
            {"$set": update_data}
        )

        return await self.get_by_id(booking_id)

    async def update_payment_status(
        self,
        booking_id: str,
        payment_status: str,
        stripe_payment_id: Optional[str] = None
    ) -> bool:
        """Update payment status of a booking."""
        update_data: Dict[str, Any] = {
            "payment_status": payment_status,
            "updated_at": datetime.utcnow()
        }
        if stripe_payment_id:
            update_data["stripe_payment_id"] = stripe_payment_id
            
        result = await self.collection.update_one(
            {"_id": booking_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def cancel_booking(
        self,
        booking_id: str,
        cancelled_by: str,
        reason: Optional[str] = None
    ) -> bool:
        """Cancel a booking."""
        result = await self.collection.update_one(
            {"_id": booking_id},
            {
                "$set": {
                    "payment_status": "CANCELLED",
                    "cancelled_by": cancelled_by,
                    "cancellation_reason": reason,
                    "cancelled_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0

    async def delete(self, booking_id: str) -> bool:
        """Delete a booking."""
        if not ObjectId.is_valid(booking_id):
            return False
        result = await self.collection.delete_one({"_id": booking_id})
        return result.deleted_count > 0

    async def count(
        self,
        payment_status: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> int:
        """Get count of bookings."""
        query: Dict[str, Any] = {}
        if payment_status:
            query["payment_status"] = payment_status
        if user_id:
            query["user_id"] = user_id
        return await self.collection.count_documents(query)

    async def get_stats(self) -> Dict[str, Any]:
        """Get booking statistics for admin dashboard."""
        pipeline = [
            {
                "$group": {
                    "_id": "$payment_status",
                    "count": {"$sum": 1}
                }
            }
        ]
        status_counts = await self.collection.aggregate(pipeline).to_list(length=10)
        
        total = await self.collection.count_documents({})
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = await self.collection.count_documents(
            {"created_at": {"$gte": today}}
        )
        
        return {
            "total": total,
            "today": today_count,
            "by_status": {item["_id"]: item["count"] for item in status_counts}
        }