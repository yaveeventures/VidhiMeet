import logging
from datetime import datetime, timedelta, timezone
import httpx
import jwt
from fastapi import HTTPException
from ..config import get_settings
from ..models import Booking, Practice, User

logger = logging.getLogger("fastapi")
settings = get_settings()

REQUIRED_INTAKE = {
    Practice.FAMILY: {"matter_type", "children_involved", "existing_order"},
    Practice.CORPORATE: {"business_type", "help_needed", "deadline"},
    Practice.PROPERTY: {"property_type", "relationship", "active_proceedings"},
}

def validate_intake(practice: Practice, intake: dict):
    missing = REQUIRED_INTAKE[practice] - set(intake)
    if missing:
        raise HTTPException(status_code=422, detail={"missing_intake_fields": sorted(missing)})

def get_jitsi_meeting_details(booking: Booking, user: User) -> dict:
    """Return browser-embeddable Jitsi meeting details scoped to a booking."""
    room_name = booking.jitsi_room or f"lc-{booking.id}"
    domain = (settings.jitsi_domain or "meet.jit.si").strip().strip("/")
    app_id = settings.jitsi_app_id.strip()
    token = None

    if settings.production and (not app_id or not settings.jitsi_app_secret):
        raise HTTPException(503, "secure Jitsi room signing is not configured")

    path_room = f"{app_id}/{room_name}" if app_id else room_name
    url = f"https://{domain}/{path_room}"

    if app_id and settings.jitsi_app_secret:
        now = datetime.now(timezone.utc)
        payload = {
            "aud": "jitsi",
            "iss": "chat",
            "sub": app_id,
            "room": room_name,
            "nbf": int(now.timestamp()) - 10,
            "exp": int((now + timedelta(minutes=booking.duration_minutes + 30)).timestamp()),
            "context": {
                "user": {
                    "id": user.id,
                    "name": user.full_name,
                    "email": user.email,
                    "moderator": user.role.value in ("lawyer", "admin"),
                }
            },
        }
        token = jwt.encode(payload, settings.jitsi_app_secret, algorithm="HS256")

    return {
        "provider": "jitsi",
        "domain": domain,
        "url": url,
        "token": token,
        "room_name": room_name,
        "display_name": user.full_name,
    }

def get_daily_meeting_details(booking: Booking, user: User) -> dict:
    api_key = settings.daily_api_key
    domain = settings.daily_domain or "lexconnect"
    room_name = booking.jitsi_room or f"lc-{booking.id}"
    
    if not api_key:
        demo_room = "https://demo.daily.co/hello"
        return {
            "url": demo_room,
            "token": None,
            "room_name": "hello",
            "display_name": user.full_name
        }
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    room_url = f"https://{domain}.daily.co/{room_name}"
    
    try:
        with httpx.Client() as client:
            room_res = client.post(
                "https://api.daily.co/v1/rooms",
                headers=headers,
                json={
                    "name": room_name,
                    "properties": {
                        "enable_chat": True,
                        "enable_screenshare": True,
                        "enable_people_ui": True,
                        "enable_pip_ui": True,
                        "start_video_off": False,
                        "start_audio_off": False,
                        "enable_simulcast": True,
                        "max_input_video_participants": 2,
                        "client_max_receive_video_bandwidth": 1500,
                        "client_max_send_video_bandwidth": 1500,
                        "enable_end_to_end_encryption": True
                    }
                },
                timeout=10.0
            )
            if room_res.status_code in (200, 201):
                room_url = room_res.json().get("url", room_url)
            elif room_res.status_code == 400 and "already exists" in room_res.text:
                room_url = f"https://{domain}.daily.co/{room_name}"
            else:
                logger.warning(f"Daily room creation returned status {room_res.status_code}: {room_res.text}")
                
            is_owner = user.role.value in ("lawyer", "admin")
            token_res = client.post(
                "https://api.daily.co/v1/meeting-tokens",
                headers=headers,
                json={
                    "properties": {
                        "room_name": room_name,
                        "user_name": user.full_name,
                        "is_owner": is_owner,
                        "enable_screenshare": True
                    }
                },
                timeout=10.0
            )
            token = None
            if token_res.status_code in (200, 201):
                token = token_res.json().get("token")
            else:
                logger.warning(f"Daily token creation returned status {token_res.status_code}: {token_res.text}")
                
            return {
                "url": room_url,
                "token": token,
                "room_name": room_name,
                "display_name": user.full_name
            }
    except Exception as e:
        logger.error(f"Error connecting to Daily.co API: {e}")
        return {
            "url": f"https://{domain}.daily.co/{room_name}",
            "token": None,
            "room_name": room_name,
            "display_name": user.full_name
        }

def verify_daily_meeting_duration(room_name: str) -> float:
    api_key = settings.daily_api_key
    if not api_key:
        return 20.0
        
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        with httpx.Client() as client:
            res = client.get(
                f"https://api.daily.co/v1/meetings?room={room_name}",
                headers=headers,
                timeout=10.0
            )
            if res.status_code == 200:
                data = res.json()
                meetings = data.get("data", [])
                if not meetings:
                    return 0.0
                
                total_seconds = 0
                for meeting in meetings:
                    participants = meeting.get("participants", [])
                    if len(participants) >= 2:
                        total_seconds += meeting.get("duration", 0)
                
                return total_seconds / 60.0
            else:
                logger.warning(f"Daily meetings API returned status {res.status_code}: {res.text}")
                return 0.0
    except Exception as e:
        logger.error(f"Error checking Daily meeting duration: {e}")
        return 0.0


def calculate_cancellation_policy(booking: Booking, cancelled_by_role: str, now_dt: datetime) -> dict:
    """
    Calculate refund and penalty breakdown based on policy matrix:
    - Lawyer Cancel: 100% Refund + 20% Voucher
    - Client Cancel (>24h): 100% Refund (0% Penalty)
    - Client Cancel (2h-24h): 75% Refund (25% Penalty)
    - Client Cancel (<2h / No-Show): 0% Refund (100% Penalty)
    """
    starts_at = booking.starts_at or booking.original_starts_at
    if starts_at and starts_at.tzinfo is None:
        starts_at = starts_at.replace(tzinfo=timezone.utc)
    if now_dt.tzinfo is None:
        now_dt = now_dt.replace(tzinfo=timezone.utc)

    hours_until_start = (starts_at - now_dt).total_seconds() / 3600.0

    if cancelled_by_role in ("lawyer", "admin"):
        policy_tier = "lawyer_cancellation"
        refund_pct = 100
        penalty_pct = 0
        voucher_issued = True
    elif hours_until_start >= 24.0:
        policy_tier = "client_more_than_24h"
        refund_pct = 100
        penalty_pct = 0
        voucher_issued = False
    elif hours_until_start >= 2.0:
        policy_tier = "client_between_2h_and_24h"
        refund_pct = 75
        penalty_pct = 25
        voucher_issued = False
    else:
        policy_tier = "client_under_2h_or_noshow"
        refund_pct = 0
        penalty_pct = 100
        voucher_issued = False

    refund_amount_minor = round(booking.amount_minor * (refund_pct / 100.0))
    penalty_amount_minor = booking.amount_minor - refund_amount_minor

    refund_rupees = refund_amount_minor / 100.0
    notice = f"Your refund of ₹{refund_rupees:.2f} has been initiated and will reflect in your original payment method (UPI/Bank) within 3 to 5 business days per RBI consumer protection rules." if refund_amount_minor > 0 else "No refund issued per cancellation terms for short-notice cancellations under 2 hours."

    return {
        "policy_tier": policy_tier,
        "hours_until_start": round(hours_until_start, 2),
        "total_amount_minor": booking.amount_minor,
        "refund_pct": refund_pct,
        "penalty_pct": penalty_pct,
        "refund_amount_minor": refund_amount_minor,
        "penalty_amount_minor": penalty_amount_minor,
        "voucher_issued": voucher_issued,
        "reversal_timeline_notice": notice
    }

