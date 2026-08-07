import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import (
    Booking, BookingStatus, LawyerProfile, Message, Practice, Review, Role, User
)
from ..schemas import (
    BookingCreate, BookingOut, DisputeCreate, MessageCreate, MessageOut,
    ReviewCreate, ReviewOut
)
from ..security import current_user, require_roles
from ..services import (
    audit, create_payment_intent, evaluate_daily_meeting_logs, get_daily_meeting_details,
    presign_document, validate_intake
)


settings = get_settings()

router = APIRouter(tags=["bookings"])


# ── Helper ────────────────────────────────────────────────────────────────────

def booking_for_participant(booking_id: str, user: User, db: Session) -> Booking:
    booking = db.get(Booking, booking_id)
    if not booking or (user.role != Role.ADMIN and user.id not in (booking.client_id, booking.lawyer_id)):
        raise HTTPException(404, "booking not found")
    return booking


# ── Bookings ──────────────────────────────────────────────────────────────────

@router.post("/api/v1/bookings", response_model=BookingOut, status_code=201)
def create_booking(payload: BookingCreate, request: Request, user: User = Depends(require_roles(Role.CLIENT)),
                   db: Session = Depends(get_db)):
    if not payload.disclaimer_accepted:
        raise HTTPException(422, "attorney-client disclaimer acknowledgement is required")
    if payload.starts_at <= datetime.now(timezone.utc):
        raise HTTPException(422, "booking must be in the future")
    validate_intake(payload.practice, payload.intake)
    lawyer = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == payload.lawyer_id,
                                                    LawyerProfile.verified.is_(True)))
    p_practices = [x.lower() for x in lawyer.practice] if isinstance(lawyer.practice, list) else [str(lawyer.practice).lower()]
    if not lawyer or payload.practice.value.lower() not in p_practices:
        raise HTTPException(404, "verified lawyer not found for this practice")
    fee = max(3500, round(lawyer.hourly_fee_minor * 0.05))
    booking = Booking(client_id=user.id, lawyer_id=payload.lawyer_id, practice=payload.practice,
                      starts_at=payload.starts_at, duration_minutes=payload.duration_minutes,
                      amount_minor=lawyer.hourly_fee_minor + fee, intake=payload.intake,
                      disclaimer_version=payload.disclaimer_version,
                      disclaimer_accepted_at=datetime.now(timezone.utc),
                      jitsi_room=f"lc-{secrets.token_urlsafe(24)}")
    db.add(booking); db.flush()

    payment_url = None
    if settings.phonepe_merchant_id and settings.phonepe_salt_key:
        from ..services import create_phonepe_payment
        payment_url = create_phonepe_payment(booking, str(request.base_url))
    else:
        booking.stripe_payment_intent_id = create_payment_intent(booking, lawyer)

    audit(db, user, "booking.created", "booking", booking.id, {"disclaimer": payload.disclaimer_version})
    db.commit(); db.refresh(booking)
    booking.payment_url = payment_url
    return booking


@router.get("/api/v1/bookings", response_model=list[BookingOut])
def list_bookings(user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = select(Booking)
    if user.role == Role.CLIENT: query = query.where(Booking.client_id == user.id)
    elif user.role == Role.LAWYER: query = query.where(Booking.lawyer_id == user.id)
    bookings_list = list(db.scalars(query).all())
    bookings_list.sort(key=lambda b: b.last_message_at or b.created_at, reverse=True)
    return bookings_list


@router.get("/api/v1/bookings/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return booking_for_participant(booking_id, user, db)


@router.post("/api/v1/bookings/{booking_id}/meeting-token")
def meeting_token(booking_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    booking = booking_for_participant(booking_id, user, db)
    if booking.status not in (BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS):
        raise HTTPException(409, "consultation room is unavailable")
    return get_daily_meeting_details(booking, user)


from ..rate_limiter import rate_limit_dependency


@router.post("/api/v1/bookings/{booking_id}/documents/presign", dependencies=[Depends(rate_limit_dependency("uploads"))])
def document_upload(booking_id: str, filename: str, content_type: str,
                    user: User = Depends(current_user), db: Session = Depends(get_db)):
    from ..sanitizer import sanitize_filename
    filename = sanitize_filename(filename)
    booking_for_participant(booking_id, user, db)
    allowed = {"application/pdf", "image/jpeg", "image/png",
               "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    if content_type not in allowed:
        raise HTTPException(415, "unsupported document type")
    result = presign_document(booking_id, filename, content_type)
    audit(db, user, "document.presigned", "booking", booking_id, {"content_type": content_type})
    db.commit()
    return result


@router.post("/api/v1/bookings/{booking_id}/documents/confirm")
def confirm_document(booking_id: str, filename: str, key: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    from ..sanitizer import sanitize_filename, sanitize_key
    filename = sanitize_filename(filename)
    key = sanitize_key(key)
    booking = booking_for_participant(booking_id, user, db)
    docs = list(booking.documents or [])
    docs.append({
        "filename": filename,
        "key": key,
        "uploaded_by": user.full_name,
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    })
    booking.documents = docs
    audit(db, user, "document.uploaded", "booking", booking_id, {"filename": filename, "key": key})
    db.commit()
    return {"status": "success", "documents": docs}


@router.post("/api/v1/bookings/{booking_id}/complete")
def complete_booking(booking_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    booking = booking_for_participant(booking_id, user, db)
    if booking.status not in (BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS):
        raise HTTPException(400, "only confirmed or in-progress bookings can be completed")

    # Enforce minimum call duration of 15 minutes when completed by the lawyer
    if user.role == Role.LAWYER:
        from ..services import verify_daily_meeting_duration
        room_name = booking.jitsi_room or f"lc-{booking.id}"
        duration_mins = verify_daily_meeting_duration(room_name)
        if duration_mins < 15.0:
            raise HTTPException(400, f"Consultation duration is too short ({duration_mins:.1f} mins). A minimum call duration of 15 minutes is required before completing a booking.")

    booking.status = BookingStatus.COMPLETED
    audit(db, user, "booking.completed", "booking", booking_id)
    db.commit()
    return {"booking_id": booking_id, "status": booking.status}


@router.post("/api/v1/bookings/{booking_id}/dispute")
def dispute_booking(booking_id: str, payload: DisputeCreate | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    booking = booking_for_participant(booking_id, user, db)
    if booking.status not in (BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS, BookingStatus.COMPLETED):
        raise HTTPException(400, "only confirmed, in-progress or completed bookings can be disputed")
    
    category = payload.category.value if payload else "quality_other"
    reason = payload.reason if payload else "Dispute raised by participant"

    booking.status = BookingStatus.DISPUTED
    booking.dispute_category = category
    booking.dispute_reason = reason
    booking.disputed_at = datetime.now(timezone.utc)

    # 3-Step Dispute Matrix: Cross-reference Daily.co room logs
    eval_result = evaluate_daily_meeting_logs(booking, db)

    audit(db, user, "booking.disputed", "booking", booking_id, {
        "category": category,
        "reason": reason,
        "auto_resolution_status": booking.auto_resolution_status,
        "lawyer_duration_seconds": booking.lawyer_duration_seconds,
        "client_duration_seconds": booking.client_duration_seconds
    })
    db.commit()
    return {
        "booking_id": booking_id,
        "status": booking.status,
        "dispute_category": booking.dispute_category,
        "dispute_reason": booking.dispute_reason,
        "auto_resolution_status": booking.auto_resolution_status,
        "lawyer_duration_seconds": booking.lawyer_duration_seconds,
        "client_duration_seconds": booking.client_duration_seconds
    }



@router.post("/api/v1/bookings/{booking_id}/confirm-payment")
def confirm_payment(booking_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    booking = booking_for_participant(booking_id, user, db)
    if booking.status != BookingStatus.PENDING_PAYMENT:
        raise HTTPException(400, "booking is not pending payment")
    booking.status = BookingStatus.CONFIRMED
    audit(db, user, "booking.payment_confirmed_mock", "booking", booking_id)
    db.commit()
    return {"status": "success", "booking_status": booking.status}


# ── Messages ──────────────────────────────────────────────────────────────────

@router.get("/api/v1/bookings/{booking_id}/messages", response_model=list[MessageOut])
def get_messages(booking_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    booking = booking_for_participant(booking_id, user, db)
    messages = db.scalars(
        select(Message).where(Message.booking_id == booking.id).order_by(Message.created_at.asc())
    ).all()
    return list(messages)


@router.post("/api/v1/bookings/{booking_id}/messages", response_model=MessageOut)
def send_message(booking_id: str, payload: MessageCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    booking = booking_for_participant(booking_id, user, db)
    msg = Message(
        booking_id=booking.id,
        sender_id=user.id,
        content=payload.content.strip() if not payload.encrypted else payload.content,
        encrypted=payload.encrypted,
        iv=payload.iv
    )
    db.add(msg)
    db.flush()
    audit(db, user, "message.sent", "message", msg.id, {"booking_id": booking.id, "encrypted": payload.encrypted})
    db.commit()
    db.refresh(msg)
    return msg


# ── Reviews ───────────────────────────────────────────────────────────────────

@router.post("/api/v1/bookings/{booking_id}/review", response_model=ReviewOut)
def create_review(booking_id: str, payload: ReviewCreate, user: User = Depends(require_roles(Role.CLIENT)),
                  db: Session = Depends(get_db)):
    raise HTTPException(
        400,
        "Public ratings and reviews are disabled in compliance with Bar Council of India Rule 36 prohibiting advocate advertisement and solicitation."
    )


@router.get("/api/v1/bookings/{booking_id}/review", response_model=ReviewOut | None)
def get_booking_review(booking_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    booking = booking_for_participant(booking_id, user, db)
    review = db.scalar(select(Review).where(Review.booking_id == booking.id))
    if not review:
        raise HTTPException(404, "no review found")
    return review


@router.get("/api/v1/lawyers/{lawyer_id}/reviews", response_model=list[ReviewOut])
def list_lawyer_reviews(lawyer_id: str, db: Session = Depends(get_db)):
    reviews = db.scalars(
        select(Review).where(Review.lawyer_id == lawyer_id).order_by(Review.created_at.desc())
    ).all()
    return list(reviews)
