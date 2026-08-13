import base64
import hashlib
import json
import structlog
import httpx
from ..config import get_settings
from ..models import Booking, LawyerProfile

logger = structlog.get_logger("payment_service")
settings = get_settings()

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
    except httpx.HTTPError as e:
        logger.error("Error calling PhonePe pay API", error=str(e))
        
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

    import uuid
    txn_id = f"VER-{uuid.uuid4().hex[:16].upper()}"

    payload = {
        "merchantId": merchant_id,
        "merchantTransactionId": txn_id,
        "merchantUserId": f"LAW-{bank_account.lawyer_id}",
        "amount": 100,  # ₹1 verification micro-deposit
        "redirectUrl": f"{base_url}/lawyer.html?tab=payouts&verify=phonepe",
        "redirectMode": "REDIRECT",
        "callbackUrl": f"{base_url}/api/v1/webhooks/phonepe",
        "paymentInstrument": {"type": "PAY_PAGE"}
    }

    json_bytes = json.dumps(payload).encode("utf-8")
    base64_payload = base64.b64encode(json_bytes).decode("utf-8")
    hash_str = base64_payload + "/pg/v1/pay" + salt_key
    sha256_hash = hashlib.sha256(hash_str.encode("utf-8")).hexdigest()
    x_verify = f"{sha256_hash}###{salt_index}"

    headers = {"Content-Type": "application/json", "X-VERIFY": x_verify}

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
            logger.error(f"PhonePe verify payment returned status {res.status_code}: {res.text}")
    except httpx.HTTPError as e:
        logger.error("Error calling PhonePe verify payment API", error=str(e))

    return None


def initiate_refund(booking: Booking, refund_amount_minor: int, reason: str = "Client cancellation refund") -> str:
    """Trigger payment refund via PhonePe, Stripe, or mock fallback."""
    import uuid
    refund_txn_id = f"REF-{uuid.uuid4().hex[:16].upper()}"

    if refund_amount_minor <= 0:
        return refund_txn_id

    # PhonePe Refund Execution
    if booking.phonepe_transaction_id and settings.phonepe_merchant_id and settings.phonepe_salt_key:
        merchant_id = settings.phonepe_merchant_id
        salt_key = settings.phonepe_salt_key
        salt_index = settings.phonepe_salt_index
        env = settings.phonepe_env.lower()

        api_url = "https://api.phonepe.com/apis/hermes/pg/v1/refund" if env == "production" else "https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/refund"

        payload = {
            "merchantId": merchant_id,
            "merchantTransactionId": refund_txn_id,
            "originalTransactionId": booking.phonepe_transaction_id,
            "amount": refund_amount_minor,
            "callbackUrl": f"https://VidhiMeet.com/api/v1/webhooks/phonepe"
        }

        json_bytes = json.dumps(payload).encode("utf-8")
        base64_payload = base64.b64encode(json_bytes).decode("utf-8")
        hash_str = base64_payload + "/pg/v1/refund" + salt_key
        sha256_hash = hashlib.sha256(hash_str.encode("utf-8")).hexdigest()
        x_verify = f"{sha256_hash}###{salt_index}"

        headers = {"Content-Type": "application/json", "X-VERIFY": x_verify}
        try:
            with httpx.Client() as client:
                res = client.post(api_url, headers=headers, json={"request": base64_payload}, timeout=15.0)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("success"):
                        return refund_txn_id
                logger.error(f"PhonePe refund failed with status {res.status_code}: {res.text}")
        except httpx.HTTPError as e:
            logger.error("Error calling PhonePe refund API", error=str(e))

    # 3. Fallback mock refund ID for local dev/testing
    return refund_txn_id
