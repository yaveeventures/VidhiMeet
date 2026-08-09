"""
Calendar Integration Router — VidhiMeet

Provides RFC 5545-compliant iCal endpoints for calendar sync:
- GET /api/v1/bookings/{booking_id}/calendar.ics  — Single event download (auth required)
- GET /api/v1/calendar/feed/{token}.ics           — Live iCal feed for lawyer (token-based, no auth)
- GET /api/v1/calendar/token                      — Get/rotate lawyer's iCal feed token
"""

import secrets
from datetime import datetime, timedelta, timezone
from textwrap import dedent

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Booking, BookingStatus, LawyerProfile, Role, User
from ..security import current_user, require_roles

router = APIRouter(tags=["calendar"])


# ── Helpers ────────────────────────────────────────────────────────────────────

def _fmt_dt(dt: datetime) -> str:
    """Format datetime to iCal UTC DTSTART/DTEND format (yyyymmddTHHMMSSZ)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    utc = dt.astimezone(timezone.utc)
    return utc.strftime("%Y%m%dT%H%M%SZ")


def _escape(text: str) -> str:
    """Escape iCal string values per RFC 5545."""
    if not text:
        return ""
    return (text.replace("\\", "\\\\")
               .replace(";", "\\;")
               .replace(",", "\\,")
               .replace("\n", "\\n"))


def _fold(line: str) -> str:
    """Fold long iCal lines at 75 octets per RFC 5545."""
    result = []
    while len(line.encode("utf-8")) > 75:
        result.append(line[:75])
        line = " " + line[75:]
    result.append(line)
    return "\r\n".join(result)


def _build_vevent(booking: Booking, base_url: str = "https://VidhiMeet.in") -> str:
    """Build a single VEVENT block from a Booking object."""
    dt = booking.starts_at or booking.original_starts_at
    if not dt:
        return ""

    dtstart = _fmt_dt(dt)
    dtend = _fmt_dt(dt + timedelta(minutes=booking.duration_minutes or 45))
    dtstamp = _fmt_dt(datetime.now(timezone.utc))

    status = "CONFIRMED"
    if booking.status in (BookingStatus.CANCELLED, BookingStatus.REFUNDED):
        status = "CANCELLED"
    elif booking.status == BookingStatus.COMPLETED:
        status = "COMPLETED"

    practice = str(booking.practice.value).replace("_", " ").title() if booking.practice else "Legal"
    client_name = _escape(booking.client_name or "Client")
    lawyer_name = _escape(booking.lawyer_name or "Advocate")

    summary = f"Legal Consultation ({practice}) — {lawyer_name}"
    description = (
        f"VidhiMeet Consultation\\n"
        f"Ref: {booking.id[:8].upper()}\\n"
        f"Lawyer: {lawyer_name}\\n"
        f"Client: {client_name}\\n"
        f"Practice: {practice}\\n"
        f"Duration: {booking.duration_minutes or 45} minutes\\n"
        f"Secure Room: {base_url}/meet/{booking.jitsi_room}"
    )

    location = f"VidhiMeet Secure Video Room ({base_url}/meet/{booking.jitsi_room})"

    lines = [
        "BEGIN:VEVENT",
        f"UID:{booking.id}@VidhiMeet.in",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{_escape(summary)}",
        f"DESCRIPTION:{_escape(description)}",
        f"LOCATION:{_escape(location)}",
        f"STATUS:{status}",
        "TRANSP:OPAQUE",
        "BEGIN:VALARM",
        "TRIGGER:-PT15M",
        "ACTION:DISPLAY",
        "DESCRIPTION:Legal Consultation in 15 minutes",
        "END:VALARM",
        "END:VEVENT",
    ]
    return "\r\n".join(_fold(l) for l in lines)


def _build_ics_calendar(vevents: list[str], name: str = "VidhiMeet Consultations") -> str:
    """Wrap VEVENT blocks in a VCALENDAR container."""
    header = "\r\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//VidhiMeet//VidhiMeet Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_escape(name)}",
        "X-WR-TIMEZONE:Asia/Kolkata",
    ])
    body = "\r\n".join(vevents)
    return f"{header}\r\n{body}\r\nEND:VCALENDAR"


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/api/v1/bookings/{booking_id}/calendar.ics", include_in_schema=True)
def booking_ics(
    booking_id: str,
    token: str | None = None,
    user: User | None = Depends(current_user),
    db: Session = Depends(get_db),
):
    """Download a single .ics event for a specific booking (auth required)."""
    # Support token query param for browser <a> download (can't set auth headers)
    if user is None:
        raise HTTPException(401, "authentication required")
    booking = db.get(Booking, booking_id)
    if not booking or (
        user.role != Role.ADMIN
        and user.id not in (booking.client_id, booking.lawyer_id)
    ):
        raise HTTPException(404, "booking not found")

    vevent = _build_vevent(booking)
    if not vevent:
        raise HTTPException(422, "booking has no scheduled time")

    ics = _build_ics_calendar([vevent], name="VidhiMeet Consultation")
    filename = f"VidhiMeet-{booking_id[:8].lower()}.ics"

    return Response(
        content=ics.encode("utf-8"),
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


@router.get("/api/v1/calendar/feed/{token}.ics", include_in_schema=True)
def lawyer_ical_feed(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Public token-based iCal feed for a lawyer.
    Subscribe this URL in Google Calendar / Apple Calendar / Outlook to
    get live-syncing VidhiMeet appointments.
    """
    profile = db.scalars(
        select(LawyerProfile).where(LawyerProfile.ical_token == token)
    ).first()

    if not profile:
        raise HTTPException(404, "calendar feed not found")

    # Fetch all non-cancelled upcoming bookings for this lawyer
    bookings_q = select(Booking).where(
        Booking.lawyer_id == profile.user_id,
        Booking.status.in_([
            BookingStatus.PENDING_PAYMENT,
            BookingStatus.CONFIRMED,
            BookingStatus.IN_PROGRESS,
            BookingStatus.COMPLETED,
        ]),
    )
    bookings = list(db.scalars(bookings_q).all())

    vevents = [_build_vevent(b) for b in bookings if _build_vevent(b)]

    lawyer_name = profile.user.full_name if profile.user else "Advocate"
    ics = _build_ics_calendar(vevents, name=f"{lawyer_name} — VidhiMeet Schedule")

    return Response(
        content=ics.encode("utf-8"),
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="VidhiMeet-schedule.ics"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


@router.get("/api/v1/calendar/token")
def get_ical_token(
    user: User = Depends(require_roles(Role.LAWYER)),
    db: Session = Depends(get_db),
):
    """Return the lawyer's iCal feed token (used to construct the subscribe URL)."""
    profile = db.scalars(
        select(LawyerProfile).where(LawyerProfile.user_id == user.id)
    ).first()
    if not profile:
        raise HTTPException(404, "lawyer profile not found")

    # Auto-generate token if missing (e.g. legacy accounts)
    if not profile.ical_token:
        profile.ical_token = secrets.token_urlsafe(48)
        db.commit()

    return {"ical_token": profile.ical_token}


@router.post("/api/v1/calendar/token/rotate")
def rotate_ical_token(
    user: User = Depends(require_roles(Role.LAWYER)),
    db: Session = Depends(get_db),
):
    """Rotate (invalidate) the lawyer's iCal token and issue a new one."""
    profile = db.scalars(
        select(LawyerProfile).where(LawyerProfile.user_id == user.id)
    ).first()
    if not profile:
        raise HTTPException(404, "lawyer profile not found")

    profile.ical_token = secrets.token_urlsafe(48)
    db.commit()
    return {"ical_token": profile.ical_token, "message": "iCal feed URL has been rotated."}
