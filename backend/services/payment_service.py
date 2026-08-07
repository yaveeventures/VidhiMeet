import base64
import hashlib
import json
import logging
import stripe
import httpx
from ..config import get_settings
from ..models import Booking, LawyerProfile

logger = logging.getLogger("fastapi")
settings = get_settings()

def create_payment_intent(booking: Booking, lawyer: LawyerProfile) -> str | None:
    if not settings.stripe_secret_key:
        return None
    stripe.api_key = settings.stripe_secret_key
    fee = booking.platform_fee_minor
    params = {
        "amount": booking.amount_minor, "currency": booking.currency.lower(),
        "capture_method": "automatic", "metadata": {"booking_id": booking.id},
        "application_fee_amount": fee,
    }
    if lawyer.stripe_account_id:
        params["transfer_data"] = {"destination": lawyer.stripe_account_id}
    intent = stripe.PaymentIntent.create(**params, idempotency_key=f"booking:{booking.id}")
    return intent.id

def create_phonepe_payment(booking: Booking, base_url: str) -> str | None:
    if not settings.phonepe_merchant_id or not settings.phonepe_salt_key:
        return None
        
    merchant_id = settings.phonepe_merchant_id
    salt_key = settings.phonepe_salt_key
    salt_index = settings.phonepe_salt_index
    env = settings.phonepe_env.lower()
    
    if env == "production":
        api_url = "https://api.phonepe.com/apis/hermes/pg/v1/pay"
    else:
        api_url = "https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay"
        
    transaction_id = f"TXN{booking.id.replace('-', '')[:22]}"
    booking.phonepe_transaction_id = transaction_id
    
    redirect_url = f"{base_url.rstrip('/')}/?booking_id={booking.id}"
    callback_url = f"{base_url.rstrip('/')}/api/v1/webhooks/phonepe"
    
    payload = {
        "merchantId": merchant_id,
        "merchantTransactionId": transaction_id,
        "merchantUserId": f"USER{booking.client_id.replace('-', '')[:22]}",
        "amount": booking.amount_minor,
        "redirectUrl": redirect_url,
        "redirectMode": "REDIRECT",
        "callbackUrl": callback_url,
        "paymentInstrument": {
            "type": "PAY_PAGE"
        }
    }
    
    json_bytes = json.dumps(payload).encode("utf-8")
    base64_payload = base64.b64encode(json_bytes).decode("utf-8")
    
    hash_str = base64_payload + "/pg/v1/pay" + salt_key
    sha256_hash = hashlib.sha256(hash_str.encode("utf-8")).hexdigest()
    x_verify = f"{sha256_hash}###{salt_index}"
    
    headers = {
        "Content-Type": "application/json",
        "X-VERIFY": x_verify
    }
    
    req_body = {"request": base64_payload}
    
    try:
        with httpx.Client() as client:
            res = client.post(api_url, headers=headers, json=req_body, timeout=15.0)
            if res.status_code == 200:
                data = res.json()
                if data.get("success") and "data" in data:
                    instrument_resp = data["data"].get("instrumentResponse", {})
                    redirect_info = instrument_resp.get("redirectInfo", {})
                    return redirect_info.get("url")
            logger.error(f"PhonePe pay API returned status {res.status_code}: {res.text}")
    except Exception as e:
        logger.error(f"Error calling PhonePe pay API: {e}")
        
    return None

def create_phonepe_verification_payment(bank_account, base_url: str) -> str | None:
    if not settings.phonepe_merchant_id or not settings.phonepe_salt_key:
        return None

    merchant_id = settings.phonepe_merchant_id
    salt_key = settings.phonepe_salt_key
    salt_index = settings.phonepe_salt_index
    env = settings.phonepe_env.lower()

    if env == "production":
        api_url = "https://api.phonepe.com/apis/hermes/pg/v1/pay"
    else:
        api_url = "https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay"

    transaction_id = f"VERIFY-{bank_account.user_id.replace('-', '')[:16]}"
    bank_account.phonepe_txn_id = transaction_id

    redirect_url = f"{base_url.rstrip('/')}/lawyer.html?upi_verified=1"
    callback_url = f"{base_url.rstrip('/')}/api/v1/webhooks/phonepe"

    payload = {
        "merchantId": merchant_id,
        "merchantTransactionId": transaction_id,
        "merchantUserId": f"USER{bank_account.user_id.replace('-', '')[:22]}",
        "amount": 100,          # ₹1 = 100 paise
        "redirectUrl": redirect_url,
        "redirectMode": "REDIRECT",
        "callbackUrl": callback_url,
        "paymentInstrument": {"type": "PAY_PAGE"},
        "description": "LawyerGrid identity verification (₹1 refundable)"
    }

    json_bytes = json.dumps(payload).encode("utf-8")
    base64_payload = base64.b64encode(json_bytes).decode("utf-8")

    hash_str = base64_payload + "/pg/v1/pay" + salt_key
    sha256_hash = hashlib.sha256(hash_str.encode("utf-8")).hexdigest()
    x_verify = f"{sha256_hash}###{salt_index}"

    req_body = {"request": base64_payload}
    headers = {"Content-Type": "application/json", "X-VERIFY": x_verify}

    try:
        with httpx.Client() as client:
            res = client.post(api_url, headers=headers, json=req_body, timeout=15.0)
            if res.status_code == 200:
                data = res.json()
                if data.get("success") and "data" in data:
                    instrument_resp = data["data"].get("instrumentResponse", {})
                    redirect_info = instrument_resp.get("redirectInfo", {})
                    return redirect_info.get("url")
            logger.error(f"PhonePe verify payment returned status {res.status_code}: {res.text}")
    except Exception as e:
        logger.error(f"Error calling PhonePe verify payment API: {e}")

    return None
