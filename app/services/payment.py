"""
Stripe payment service for handling payments.
"""
from typing import Optional, Dict, Any
import stripe

from app.core.config import settings


# Initialize Stripe with secret key
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    """Service for handling Stripe payments."""

    @staticmethod
    def is_configured() -> bool:
        """Check if Stripe is configured."""
        return bool(settings.STRIPE_SECRET_KEY)

    @staticmethod
    async def create_payment_intent(
        amount: int,  # Amount in cents
        currency: str = "eur",
        metadata: Optional[Dict[str, str]] = None,
        customer_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a Stripe PaymentIntent. Helena
        
        Args:
            amount: Amount in cents (e.g., 5000 = €50.00)
            currency: Currency code (default: eur)
            metadata: Additional metadata to attach
            customer_email: Customer email for receipt
            
        Returns:
            Dict with client_secret and payment_intent_id
        """
        if not PaymentService.is_configured():
            raise ValueError("Stripe is not configured")

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata=metadata or {},
                receipt_email=customer_email,
                automatic_payment_methods={"enabled": True},
            )
            
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": intent.amount,
                "currency": intent.currency,
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe error: {str(e)}")

    @staticmethod
    async def confirm_payment(payment_intent_id: str) -> Dict[str, Any]:
        """
        Retrieve and confirm payment status.
        
        Args:
            payment_intent_id: The Stripe PaymentIntent ID
            
        Returns:
            Payment status and details
        """
        if not PaymentService.is_configured():
            raise ValueError("Stripe is not configured")

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                "id": intent.id,
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency,
                "metadata": intent.metadata,
                "receipt_email": intent.receipt_email,
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe error: {str(e)}")

    @staticmethod
    async def create_refund(
        payment_intent_id: str,
        amount: Optional[int] = None,  # None = full refund
        reason: str = "requested_by_customer"
    ) -> Dict[str, Any]:
        """
        Create a refund for a payment.
        
        Args:
            payment_intent_id: The PaymentIntent to refund
            amount: Partial refund amount in cents (None = full)
            reason: Refund reason
            
        Returns:
            Refund details
        """
        if not PaymentService.is_configured():
            raise ValueError("Stripe is not configured")

        try:
            refund_params = {
                "payment_intent": payment_intent_id,
                "reason": reason,
            }
            
            if amount:
                refund_params["amount"] = amount
                
            refund = stripe.Refund.create(**refund_params)
            
            return {
                "id": refund.id,
                "status": refund.status,
                "amount": refund.amount,
                "currency": refund.currency,
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe error: {str(e)}")

    @staticmethod
    def construct_webhook_event(
        payload: bytes,
        sig_header: str
    ) -> stripe.Event:
        """
        Construct and verify Stripe webhook event.
        
        Args:
            payload: Raw request body
            sig_header: Stripe-Signature header
            
        Returns:
            Verified Stripe event
        """
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise ValueError("Stripe webhook secret not configured")

        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid webhook signature")


# Singleton instance
payment_service = PaymentService()
