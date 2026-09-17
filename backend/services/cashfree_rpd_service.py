"""
Cashfree Reverse Penny Drop (RPD) Verification Service.
Enables lawyers to add and verify their payout bank accounts by initiating
a micro-transaction (₹1) via UPI. The ₹1 is auto-refunded to the user.
"""

import time
import uuid
import httpx
import structlog
from typing import Any
from ..config import get_settings
from ..models import User

logger = structlog.get_logger("cashfree_rpd")
settings = get_settings()

# In-memory store for mock verification states during development and test runs
_MOCK_RPD_SESSIONS: dict[str, dict[str, Any]] = {}


def _get_verification_credentials() -> tuple[str, str]:
    app_id = (settings.cashfree_verification_app_id or settings.cashfree_app_id or "").strip()
    secret = (settings.cashfree_verification_secret_key or settings.cashfree_secret_key or "").strip()
    return app_id, secret


def _generate_cf_signature(client_id: str) -> str | None:
    """
    Encrypt clientId.timestamp using RSA with Cashfree's Public Key.
    Used when Two-Factor Authentication is configured as Public Key on Cashfree.
    """
    pub_key_raw = (settings.cashfree_public_key or "").strip()
    if not pub_key_raw or not client_id:
        return None
    try:
        import base64
        import time
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.asymmetric import padding

        clean_body = (
            "".join(pub_key_raw.split())
            .replace("-----BEGINPUBLICKEY-----", "")
            .replace("-----ENDPUBLICKEY-----", "")
            .replace("-----BEGIN PUBLIC KEY-----", "")
            .replace("-----END PUBLIC KEY-----", "")
            .strip('\'"')
        )
        pub_key_pem = f"-----BEGIN PUBLIC KEY-----\n{clean_body}\n-----END PUBLIC KEY-----"

        timestamp = int(time.time())
        data = f"{client_id}.{timestamp}".encode("utf-8")
        public_key = serialization.load_pem_public_key(pub_key_pem.encode("utf-8"))
        try:
            encrypted = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None,
                ),
            )
        except Exception:
            encrypted = public_key.encrypt(data, padding.PKCS1v15())
        return base64.b64encode(encrypted).decode("utf-8")
    except Exception as exc:
        logger.error("Failed to generate Cashfree RSA signature", error=str(exc))
        return None


def _get_verification_headers() -> dict[str, str]:
    app_id, secret = _get_verification_credentials()
    headers = {
        "x-client-id": app_id,
        "x-client-secret": secret,
        "x-api-version": "2024-12-01",
        "Content-Type": "application/json",
    }
    sig = _generate_cf_signature(app_id)
    if sig:
        headers["x-cf-signature"] = sig
    return headers


def initiate_reverse_penny_drop(lawyer: User, return_url: str | None = None) -> dict[str, Any]:
    """
    Create a Reverse Penny Drop request with Cashfree Secure ID suite.
    Returns session details including verification_id, QR code, and UPI intent links.
    """
    verification_id = f"rpd_{lawyer.id[:8]}_{int(time.time())}"
    lawyer_name = lawyer.full_name or "Advocate"
    redirect = return_url or "https://lawyer.vidhimeet.in/lawyer.html"

    app_id, secret = _get_verification_credentials()

    # Fallback to mock session in dev or test environments when keys are unconfigured
    if not app_id or not secret:
        logger.info("Cashfree keys not set; creating mock RPD session", lawyer_id=lawyer.id, verification_id=verification_id)
        mock_upi_uri = f"upi://pay?pa=vidhimeet.verify@cashfree&pn=VidhiMeet%20Verification&am=1.00&cu=INR&tr={verification_id}"
        mock_data = {
            "verification_id": verification_id,
            "reference_id": f"cf_ref_{uuid.uuid4().hex[:10]}",
            "status": "PENDING",
            "payment_link": f"https://sandbox.cashfree.com/verification/rpd/{verification_id}",
            # Inline standard SVG QR placeholder for testing in UI without external network calls
            "qr_code": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 200 200'><rect width='200' height='200' fill='%23ffffff'/><rect x='20' y='20' width='60' height='60' fill='%23173c30'/><rect x='30' y='30' width='40' height='40' fill='%23ffffff'/><rect x='40' y='40' width='20' height='20' fill='%23173c30'/><rect x='120' y='20' width='60' height='60' fill='%23173c30'/><rect x='130' y='30' width='40' height='40' fill='%23ffffff'/><rect x='140' y='40' width='20' height='20' fill='%23173c30'/><rect x='20' y='120' width='60' height='60' fill='%23173c30'/><rect x='30' y='130' width='40' height='40' fill='%23ffffff'/><rect x='40' y='140' width='20' height='20' fill='%23173c30'/><circle cx='150' cy='150' r='20' fill='%23c86245'/><text x='100' y='105' font-family='sans-serif' font-size='10' font-weight='bold' text-anchor='middle' fill='%23173c30'>PAY %E2%82%B91 VIA UPI</text></svg>",
            "upi_intent": {
                "gpay_link": mock_upi_uri,
                "phonepe_link": mock_upi_uri,
                "paytm_link": mock_upi_uri,
                "upi_uri": mock_upi_uri,
            },
            "valid_upto": int(time.time()) + 600,  # 10 minutes
            "amount": 1.0,
            "currency": "INR",
            "is_mock": True,
        }
        _MOCK_RPD_SESSIONS[verification_id] = {
            **mock_data,
            "lawyer_id": lawyer.id,
            "lawyer_name": lawyer_name,
            "created_at": time.time(),
        }
        return mock_data

    url = f"{settings.cashfree_verification_base_url}/reverse-penny-drop"
    payload = {
        "verification_id": verification_id,
        "name": lawyer_name,
        "redirect_url": redirect,
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            res = client.post(url, headers=_get_verification_headers(), json=payload)
            if res.status_code in (200, 201):
                data = res.json()
                logger.info("Cashfree RPD request created", verification_id=verification_id, status=data.get("status"))
                
                raw_qr = data.get("qr_code") or data.get("qrCode") or ""
                if raw_qr and not raw_qr.startswith("data:") and not raw_qr.startswith("http"):
                    raw_qr = f"data:image/png;base64,{raw_qr}"

                upi_uri = data.get("upi_link") or data.get("upi_uri") or ""
                upi_intent = data.get("upi_intent") or data.get("upiIntent") or {}
                if not upi_intent and upi_uri:
                    upi_intent = {
                        "upi_uri": upi_uri,
                        "gpay_link": data.get("gpay") or upi_uri,
                        "phonepe_link": data.get("phonepe") or upi_uri,
                        "paytm_link": data.get("paytm") or upi_uri,
                        "bhim_link": data.get("bhim") or upi_uri,
                    }

                raw_valid = data.get("valid_upto")
                valid_epoch = int(time.time()) + 600
                if isinstance(raw_valid, (int, float)):
                    valid_epoch = int(raw_valid)
                elif isinstance(raw_valid, str):
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(raw_valid.replace("Z", "+00:00"))
                        valid_epoch = int(dt.timestamp())
                    except Exception:
                        valid_epoch = int(time.time()) + 600

                return {
                    "verification_id": verification_id,
                    "reference_id": str(data.get("ref_id") or data.get("reference_id") or ""),
                    "status": data.get("status", "PENDING"),
                    "payment_link": data.get("url") or data.get("payment_link") or upi_uri,
                    "qr_code": raw_qr,
                    "upi_intent": upi_intent,
                    "valid_upto": valid_epoch,
                    "amount": 1.0,
                    "currency": "INR",
                    "is_mock": False,
                }
            
            # Parse error response cleanly from Cashfree
            error_msg = f"Status {res.status_code}"
            try:
                err_data = res.json()
                error_msg = err_data.get("message") or err_data.get("error", {}).get("message") or res.text
            except Exception:
                error_msg = res.text or error_msg
            logger.error("Cashfree RPD creation failed", status_code=res.status_code, error=error_msg)
            raise ValueError(f"Cashfree RPD error: {error_msg}")
    except ValueError:
        raise
    except Exception as exc:
        logger.error("Failed to initiate Cashfree RPD", error=str(exc))
        raise ValueError(f"Unable to connect to Cashfree verification service: {str(exc)}")


def get_reverse_penny_drop_status(verification_id: str) -> dict[str, Any]:
    """
    Retrieve status and remitter details for a Reverse Penny Drop request.
    Normalizes Cashfree remitter details (bank account, IFSC, name, UTR).
    """
    # Check mock store first if active
    if verification_id in _MOCK_RPD_SESSIONS:
        session = _MOCK_RPD_SESSIONS[verification_id]
        if session.get("status") == "SUCCESS":
            return {
                "verification_id": verification_id,
                "reference_id": session.get("reference_id"),
                "status": "SUCCESS",
                "verified": True,
                "utr": session.get("utr", f"UTR{int(time.time())}"),
                "account_number": session.get("account_number", "50100412345678"),
                "ifsc": session.get("ifsc", "HDFC0001234"),
                "account_holder_name": session.get("account_holder_name", session.get("lawyer_name", "Advocate")),
                "bank_name": session.get("bank_name", "HDFC Bank"),
                "upi_vpa": session.get("upi_vpa", "lawyer@okhdfcbank"),
                "upi_name": session.get("upi_name", session.get("lawyer_name", "Advocate")),
                "name_match_score": 100,
                "message": "Bank account verified successfully via UPI Reverse Penny Drop.",
            }
        return {
            "verification_id": verification_id,
            "status": session.get("status", "PENDING"),
            "verified": False,
            "message": "Awaiting UPI payment of ₹1 by lawyer.",
        }

    app_id, secret = _get_verification_credentials()
    if not app_id or not secret:
        return {
            "verification_id": verification_id,
            "status": "PENDING",
            "verified": False,
            "message": "Awaiting UPI payment confirmation.",
        }

    # Live Cashfree API call — try /remitter/status first, then /reverse-penny-drop
    urls_to_try = [
        f"{settings.cashfree_verification_base_url}/remitter/status",
        f"{settings.cashfree_verification_base_url}/reverse-penny-drop",
    ]
    headers = _get_verification_headers()
    params = {"verification_id": verification_id}

    last_error = ""
    try:
        with httpx.Client(timeout=15.0) as client:
            for url in urls_to_try:
                res = client.get(url, headers=headers, params=params)
                if res.status_code == 200:
                    data = res.json()
                    status = (data.get("status") or "").upper()
                    remitter = data.get("remitter_details") or data.get("account_details") or data

                    is_success = status == "SUCCESS"
                    return {
                        "verification_id": verification_id,
                        "reference_id": str(data.get("ref_id") or data.get("reference_id") or ""),
                        "status": status,
                        "verified": is_success,
                        "utr": remitter.get("utr") or data.get("utr"),
                        "account_number": remitter.get("account_number") or remitter.get("bank_account") or data.get("account_number"),
                        "ifsc": (remitter.get("ifsc") or data.get("ifsc") or "").upper(),
                        "account_holder_name": remitter.get("name_at_bank") or remitter.get("account_holder_name") or data.get("name_at_bank"),
                        "bank_name": remitter.get("bank_name") or data.get("bank_name") or "Verified Bank",
                        "upi_vpa": remitter.get("vpa") or remitter.get("upi_id") or data.get("vpa"),
                        "upi_name": remitter.get("upi_name") or remitter.get("name_at_bank"),
                        "name_match_score": data.get("name_match_score", 100),
                        "message": "Bank account verified successfully" if is_success else f"Status: {status}",
                    }
                elif res.status_code != 404:
                    last_error = f"HTTP {res.status_code}: {res.text}"
                    break

            logger.error("Failed to fetch Cashfree RPD status", error=last_error)
            return {
                "verification_id": verification_id,
                "status": "PENDING",
                "verified": False,
                "message": "Awaiting UPI payment confirmation.",
            }
    except Exception as exc:
        logger.error("Error querying Cashfree RPD status", error=str(exc))
        return {
            "verification_id": verification_id,
            "status": "ERROR",
            "verified": False,
            "message": str(exc),
        }


def mock_complete_reverse_penny_drop(verification_id: str,
                                     custom_account: str | None = None,
                                     custom_ifsc: str | None = None,
                                     custom_name: str | None = None) -> bool:
    """
    Test/Dev helper: simulate a successful ₹1 payment and account extraction
    for an active mock session.
    """
    if verification_id not in _MOCK_RPD_SESSIONS:
        # Create an entry on the fly if needed
        _MOCK_RPD_SESSIONS[verification_id] = {
            "verification_id": verification_id,
            "reference_id": f"cf_ref_{uuid.uuid4().hex[:10]}",
            "created_at": time.time(),
        }

    session = _MOCK_RPD_SESSIONS[verification_id]
    session["status"] = "SUCCESS"
    session["utr"] = f"UTR{int(time.time())}{uuid.uuid4().hex[:6].upper()}"
    session["account_number"] = custom_account or "50100498765432"
    session["ifsc"] = custom_ifsc or "HDFC0001234"
    session["account_holder_name"] = custom_name or session.get("lawyer_name", "Advocate Legal")
    session["bank_name"] = "HDFC Bank Ltd"
    session["upi_vpa"] = "advocate@okhdfcbank"
    session["upi_name"] = custom_name or session.get("lawyer_name", "Advocate Legal")
    return True
