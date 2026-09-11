import base64
import hashlib
import hmac
import re
import uuid
import httpx
import structlog
from ..config import get_settings
from ..models import Booking, User

logger = structlog.get_logger("payment_service")
settings = get_settings()


def _sanitize_phone(phone: str | None) -> str:
    """Format phone number for Cashfree requirements (10 digits)."""
    if not phone:
        return "9999999999"
    digits = re.sub(r"\D", "", phone)
    if len(digits) >= 10:
        return digits[-10:]
    return digits.ljust(10, "0")


def _get_cf_headers() -> dict[str, str]:
    return {
        "x-client-id": settings.cashfree_app_id,
        "x-client-secret": settings.cashfree_secret_key,
        "x-api-version": settings.cashfree_api_version,
        "Content-Type": "application/json",
    }


def create_cashfree_order(booking: Booking, user: User, return_url: str | None = None) -> dict:
    """
    Create an order in Cashfree PG V3 API (2023-08-01).
    Returns order details including payment_session_id.
    """
    order_id = f"order_{booking.id.replace('-', '')}"
    amount = round(booking.amount_minor / 100.0, 2)
    customer_id = f"cust_{user.id.replace('-', '')[:30]}"
    customer_phone = _sanitize_phone(getattr(user, "phone", None))
    customer_email = user.email or "customer@vidhimeet.in"
    customer_name = getattr(user, "name", None) or "Client"

    # In dev or test environments without API keys, return mock order
    if not settings.cashfree_app_id or not settings.cashfree_secret_key:
        logger.info("Cashfree keys missing, returning mock order session for testing/dev", booking_id=booking.id)
        return {
            "order_id": order_id,
            "payment_session_id": f"mock_session_{uuid.uuid4().hex}",
            "order_status": "ACTIVE",
            "cf_order_id": f"cf_mock_{uuid.uuid4().hex[:12]}",
            "order_amount": amount,
            "order_currency": "INR",
        }

    url = f"{settings.cashfree_base_url}/orders"
    payload = {
        "order_id": order_id,
        "order_amount": amount,
        "order_currency": "INR",
        "customer_details": {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
        },
        "order_meta": {
            "return_url": return_url or f"https://vidhimeet.in/?booking_id={booking.id}&order_id={order_id}",
        },
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload, headers=_get_cf_headers())
            resp.raise_for_status()
            data = resp.json()
            logger.info("Cashfree order created successfully", booking_id=booking.id, order_id=order_id)
            return data
    except Exception as exc:
        logger.error("Failed to create Cashfree order", booking_id=booking.id, error=str(exc))
        raise RuntimeError(f"Payment gateway error: {exc}") from exc


def get_cashfree_order(order_id: str) -> dict:
    """
    Fetch status of an order from Cashfree PG.
    """
    if not settings.cashfree_app_id or not settings.cashfree_secret_key:
        logger.info("Cashfree keys missing, returning mock order status", order_id=order_id)
        return {
            "order_id": order_id,
            "order_status": "PAID",
            "order_amount": 0.0,
        }

    url = f"{settings.cashfree_base_url}/orders/{order_id}"
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, headers=_get_cf_headers())
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        logger.error("Failed to fetch Cashfree order", order_id=order_id, error=str(exc))
        raise RuntimeError(f"Payment verification failed: {exc}") from exc


def verify_cashfree_signature(raw_body: bytes, timestamp: str, signature: str) -> bool:
    """
    Verify Cashfree PG Webhook signature using HMAC-SHA256.
    Signature = Base64(HMAC-SHA256(timestamp + raw_body, secret_key))
    """
    if not settings.cashfree_secret_key:
        logger.warning("Cashfree secret key not configured, allowing webhook for dev")
        return True

    try:
        data = timestamp.encode("utf-8") + raw_body
        secret = settings.cashfree_secret_key.encode("utf-8")
        computed = base64.b64encode(hmac.new(secret, data, hashlib.sha256).digest()).decode("utf-8")
        return hmac.compare_digest(computed, signature)
    except Exception as exc:
        logger.error("Error verifying Cashfree webhook signature", error=str(exc))
        return False


def initiate_refund(booking: Booking, refund_amount_minor: int, reason: str = "Client cancellation refund") -> str:
    """
    Trigger Cashfree payment refund.
    """
    refund_id = f"REF-{uuid.uuid4().hex[:16].upper()}"

    if refund_amount_minor <= 0:
        return refund_id

    refund_amount = round(refund_amount_minor / 100.0, 2)
    logger.info("Initiating refund", booking_id=booking.id, amount=refund_amount, refund_id=refund_id)

    if settings.cashfree_app_id and settings.cashfree_secret_key and booking.cashfree_order_id:
        url = f"{settings.cashfree_base_url}/orders/{booking.cashfree_order_id}/refunds"
        payload = {
            "refund_id": refund_id,
            "refund_amount": refund_amount,
            "refund_note": reason[:100],
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, json=payload, headers=_get_cf_headers())
                resp.raise_for_status()
                logger.info("Cashfree refund processed successfully", booking_id=booking.id, refund_id=refund_id)
        except Exception as exc:
            logger.error("Cashfree refund request failed", booking_id=booking.id, error=str(exc))
            # Even if API fails, return refund_id for audit tracking

    return refund_id
