from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import LawyerProfile, User
from ..schemas import PlatformFeedbackCreate
from ..security import optional_user

router = APIRouter()


@router.get("/api/v1/health")
def health(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@router.get("/api/v1/public/stats")
def public_stats(db: Session = Depends(get_db)):
    """Public endpoint — no auth required. Returns live platform statistics for the home page."""
    from sqlalchemy import func, or_
    from ..models import Practice, Role

    # Per-practice verified lawyer counts
    counts = {}
    for practice_val in Practice:
        counts[practice_val.value] = db.scalar(
            select(func.count()).select_from(
                select(LawyerProfile).where(
                    LawyerProfile.verified.is_(True),
                    or_(
                        LawyerProfile.practice.contains(practice_val.value.upper()),
                        LawyerProfile.practice.contains(practice_val.value.lower())
                    )
                ).join(User).where(User.active.is_(True)).subquery()
            )
        ) or 0

    # Total verified lawyers
    total_lawyers = db.scalar(
        select(func.count()).select_from(
            select(LawyerProfile).where(LawyerProfile.verified.is_(True)).join(User).where(User.active.is_(True)).subquery()
        )
    ) or 0

    # Total active clients
    total_clients = db.scalar(
        select(func.count()).select_from(User).where(User.role == Role.CLIENT, User.active.is_(True))
    ) or 0

    return {
        "verified_lawyers": total_lawyers,
        "total_clients": total_clients,
        "bci_compliant": True,
        "lawyers_by_practice": counts,
    }


@router.post("/api/v1/public/feedback")
def submit_feedback(
    payload: PlatformFeedbackCreate,
    user: User | None = Depends(optional_user),
    db: Session = Depends(get_db)
):
    """Public endpoint allowing users to submit platform feedback."""
    from ..models import PlatformFeedback
    fb = PlatformFeedback(
        rating=payload.rating,
        comments=payload.comments,
        user_id=user.id if user else None
    )
    db.add(fb)
    db.commit()
    return {"status": "ok", "message": "Feedback submitted successfully"}

