"""
Payment routes for Stripe integration.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Request, Header
from pydantic import BaseModel, Field

from app.core.deps import get_current_user, get_booking_repository
from app.services.payment import payment_service
from app.schemas.user import UserInDB
from app.repositories.booking import BookingRepository

router = APIRouter(prefix="/payments", tags=["Payments"])


class CreatePaymentIntentRequest(BaseModel):
    """Request to create a payment intent."""
    adventure_id: str = Field(..., description="Adventure ID being booked")
    amount: int = Field(..., gt=0, description="Amount in cents")
    currency: str = Field("eur", description="Currency code")


class PaymentIntentResponse(BaseModel):
    """Payment intent response."""
    client_secret: str
    payment_intent_id: str
    amount: int
    currency: str


class ConfirmPaymentRequest(BaseModel):
    """Request to confirm payment."""
    payment_intent_id: str
    booking_id: str


@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    request: CreatePaymentIntentRequest,
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Create a Stripe PaymentIntent before booking is created.
    
    This returns a client_secret that the frontend uses to complete payment.
    The booking is only created after payment succeeds.
    """
    if not payment_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service is not configured"
        )

    try:
        result = await payment_service.create_payment_intent(
            amount=request.amount,
            currency=request.currency,
            metadata={
                "adventure_id": request.adventure_id,
                "user_id": current_user.id,
            },
            customer_email=current_user.email,
        )
        return PaymentIntentResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/confirm")
async def confirm_payment(
    request: ConfirmPaymentRequest,
    current_user: UserInDB = Depends(get_current_user),
    booking_repo: BookingRepository = Depends(get_booking_repository)
):
    """
    Confirm payment status and update booking.
    
    Called after Stripe payment is completed on frontend.
    """
    if not payment_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service is not configured"
        )

    try:
        payment_status = await payment_service.confirm_payment(
            request.payment_intent_id
        )
        
        # Update booking with payment info if successful
        if payment_status["status"] == "succeeded":
            await booking_repo.update_payment_status(
                request.booking_id,
                payment_status="PAID",
                stripe_payment_id=request.payment_intent_id
            )
            
            return {
                "success": True,
                "message": "Payment confirmed",
                "booking_id": request.booking_id,
            }
        else:
            return {
                "success": False,
                "message": f"Payment status: {payment_status['status']}",
                "status": payment_status["status"],
            }
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/config")
async def get_stripe_config():
    """Get Stripe publishable key for frontend."""
    from app.core.config import settings
    
    if not settings.STRIPE_PUBLISHABLE_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured"
        )
    
    return {"publishable_key": settings.STRIPE_PUBLISHABLE_KEY}


# Webhook endpoint
webhook_router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@webhook_router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    booking_repo: BookingRepository = Depends(get_booking_repository)
):
    """
    Handle Stripe webhook events.
    
    Processes payment confirmations, failures, and refunds.
    """
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )

    try:
        payload = await request.body()
        event = payment_service.construct_webhook_event(payload, stripe_signature)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Handle the event
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        booking_id = payment_intent.metadata.get("booking_id")
        
        if booking_id:
            await booking_repo.update_payment_status(
                booking_id,
                payment_status="PAID",
                stripe_payment_id=payment_intent.id
            )

    elif event.type == "payment_intent.payment_failed":
        payment_intent = event.data.object
        booking_id = payment_intent.metadata.get("booking_id")
        
        if booking_id:
            await booking_repo.update_payment_status(
                booking_id,
                payment_status="FAILED",
                stripe_payment_id=payment_intent.id
            )

    elif event.type == "charge.refunded":
        charge = event.data.object
        # Handle refund logic if needed

    return {"status": "success"}
