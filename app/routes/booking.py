from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.database import get_database
from app.core.config import settings
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.repositories.booking import BookingRepository
from app.core.deps import get_current_user
from app.schemas.user import UserInDB, UserRole

router = APIRouter(prefix="/bookings", tags=["Bookings"])


async def get_booking_repository(
    client: AsyncIOMotorClient = Depends(get_database)
) -> BookingRepository:
    """Dependency to get booking repository."""
    database = client[settings.MONGODB_DB_NAME]
    return BookingRepository(database)


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: BookingCreate,
    repo: BookingRepository = Depends(get_booking_repository),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new booking for an adventure park.

    - **full_name**: Customer's full name
    - **email**: Customer's email address
    - **phone**: Customer's phone number
    - **adventure_park**: Selected adventure park (e.g., "Risky Rollercoaster")
    - **consent**: Health and safety acknowledgment (must be true)
    """
    if not booking.consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must acknowledge the health and safety warnings"
        )

    result = await repo.create(booking, user_id=str(current_user.id))
    return result


@router.get("/", response_model=List[BookingResponse])
async def get_all_bookings(
    skip: int = 0,
    limit: int = 100,
    repo: BookingRepository = Depends(get_booking_repository),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get all bookings (admin endpoint).

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    bookings_list, total = await repo.get_all(skip=skip, limit=limit)
    return bookings_list


@router.get("/my", response_model=List[BookingResponse])
async def get_my_bookings(
    repo: BookingRepository = Depends(get_booking_repository),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get current user's bookings.
    """
    bookings_list = await repo.get_by_user(str(current_user.id))
    return bookings_list


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    repo: BookingRepository = Depends(get_booking_repository),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific booking by ID.

    - **booking_id**: The unique booking identifier
    """
    booking = await repo.get_by_id(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    booking_update: BookingUpdate,
    repo: BookingRepository = Depends(get_booking_repository),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update a booking (admin only).

    Only administrators (Wednesday or Pugsley) can modify bookings.
    Customers cannot edit their bookings after submission.

    - **booking_id**: The unique booking identifier
    - **booking_update**: Fields to update
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    booking = await repo.update(booking_id, booking_update)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: str,
    repo: BookingRepository = Depends(get_booking_repository),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a booking (admin only).

    - **booking_id**: The unique booking identifier
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    deleted = await repo.delete(booking_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    return None
