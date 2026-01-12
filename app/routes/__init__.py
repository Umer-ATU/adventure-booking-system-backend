from fastapi import APIRouter

from app.routes.booking import router as booking_router

api_router = APIRouter()
api_router.include_router(booking_router)
