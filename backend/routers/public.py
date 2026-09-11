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
    from sqlalchemy import func
    from ..models import Practice, Role

    # Fetch verified, active lawyer profiles (compatible across SQLite and PostgreSQL JSON columns)
    profiles = db.scalars(
        select(LawyerProfile)
        .join(User)
        .where(LawyerProfile.verified.is_(True), User.active.is_(True))
    ).all()

    total_lawyers = len(profiles)

    # Per-practice verified lawyer counts
    counts = {p.value: 0 for p in Practice}
    for p in profiles:
        p_practices = p.practice if isinstance(p.practice, list) else [p.practice]
        practices_str = " ".join(str(x).lower() for x in p_practices)
        for practice_val in Practice:
            if practice_val.value.lower() in practices_str:
                counts[practice_val.value] += 1

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

