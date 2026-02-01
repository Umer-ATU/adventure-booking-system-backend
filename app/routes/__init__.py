"""
API Routes aggregator.
"""
from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.booking import router as booking_router
from app.routes.adventure import router as adventure_router
from app.routes.payment import router as payment_router, webhook_router

# Main API router
api_router = APIRouter()

# Include all routes
api_router.include_router(auth_router)
api_router.include_router(booking_router)
api_router.include_router(adventure_router)
api_router.include_router(payment_router)
api_router.include_router(webhook_router)
