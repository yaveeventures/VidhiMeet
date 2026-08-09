from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import LawyerProfile, Practice, Role, User
from ..schemas import LawyerOut, LawyerProfileUpdate
from ..security import current_user, require_roles
from ..services import audit

settings = get_settings()

router = APIRouter(tags=["lawyers"])


@router.get("/api/v1/lawyers", response_model=list[LawyerOut])
def lawyers(practice: Practice | None = None, language: str | None = None,
            max_fee_minor: int | None = None,
            db: Session = Depends(get_db)):
    query = select(LawyerProfile, User).join(User).where(LawyerProfile.verified.is_(True), User.active.is_(True))
    if max_fee_minor: query = query.where(LawyerProfile.hourly_fee_minor <= max_fee_minor)
    rows = db.execute(query).all()

    results = []
    for p, u in rows:
        p_practices = p.practice if isinstance(p.practice, list) else [p.practice]
        p_practices_lower = [str(x).lower() for x in p_practices]
        if practice and practice.value.lower() not in p_practices_lower:
            continue
        if language and not any(language.lower() in x.lower() for x in p.languages):
            continue
        results.append(LawyerOut(
            id=u.id, full_name=u.full_name, practice=p_practices, languages=p.languages,
            hourly_fee_minor=p.hourly_fee_minor, rating=float(p.rating or 0),
            verified=p.verified, bar_number=p.bar_number, availability=p.availability or {},
            enrollment_date=p.enrollment_date, practice_address=p.practice_address,
            bar_license_url=p.bar_license_url, aadhaar_url=p.aadhaar_url, mobile_number=p.mobile_number,
            created_at=u.created_at
        ))
    return results


@router.get("/api/v1/lawyers/me", response_model=LawyerOut)
def get_my_profile(user: User = Depends(require_roles(Role.LAWYER)), db: Session = Depends(get_db)):
    profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == user.id))
    if not profile:
        # Create empty profile to begin with
        profile = LawyerProfile(
            user_id=user.id,
            practice=[Practice.PROPERTY],
            bar_number=f"PENDING-{user.id[:8].upper()}",
            languages=["English"],
            hourly_fee_minor=100000,
            rating=0.0,
            verified=False,
            availability={}
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    p_practices = profile.practice if isinstance(profile.practice, list) else [profile.practice]
    return LawyerOut(
        id=user.id,
        full_name=user.full_name,
        practice=p_practices,
        languages=profile.languages,
        hourly_fee_minor=profile.hourly_fee_minor,
        rating=float(profile.rating or 0),
        verified=profile.verified,
        bar_number=profile.bar_number,
        availability=profile.availability or {},
        enrollment_date=profile.enrollment_date,
        practice_address=profile.practice_address,
        bar_license_url=profile.bar_license_url,
        aadhaar_url=profile.aadhaar_url,
        aadhaar_number=profile.aadhaar_number,
        mobile_number=profile.mobile_number,
        created_at=user.created_at
    )


@router.put("/api/v1/lawyers/me")
def update_my_profile(payload: LawyerProfileUpdate, user: User = Depends(require_roles(Role.LAWYER)), db: Session = Depends(get_db)):
    user.full_name = payload.full_name.strip()
    profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == user.id))
    if not profile:
        profile = LawyerProfile(
            user_id=user.id,
            practice=payload.practice,
            bar_number=payload.bar_number,
            languages=payload.languages,
            hourly_fee_minor=payload.hourly_fee_minor,
            rating=0.0,
            verified=False,
            availability=payload.availability,
            enrollment_date=payload.enrollment_date,
            practice_address=payload.practice_address,
            aadhaar_number=payload.aadhaar_number,
            mobile_number=payload.mobile_number
        )
        db.add(profile)
    else:
        profile.practice = payload.practice
        profile.bar_number = payload.bar_number
        profile.languages = payload.languages
        profile.hourly_fee_minor = payload.hourly_fee_minor
        profile.availability = payload.availability
        if payload.enrollment_date is not None:
            profile.enrollment_date = payload.enrollment_date
        if payload.practice_address is not None:
            profile.practice_address = payload.practice_address
        if payload.aadhaar_number is not None:
            profile.aadhaar_number = payload.aadhaar_number
        if payload.mobile_number is not None:
            profile.mobile_number = payload.mobile_number
        if profile.bar_number != payload.bar_number:
            profile.verified = False
    audit(db, user, "lawyer.profile_updated", "lawyer_profile", user.id)
    db.commit()
    return {"status": "success"}


from ..rate_limiter import rate_limit_dependency


@router.post("/api/v1/lawyers/me/documents/presign", dependencies=[Depends(rate_limit_dependency("uploads"))])
def lawyer_document_presign(filename: str, content_type: str,
                            user: User = Depends(require_roles(Role.LAWYER)),
                            db: Session = Depends(get_db)):
    import secrets
    from ..sanitizer import sanitize_filename
    filename = sanitize_filename(filename)
    expiry = settings.presigned_url_expiry_seconds
    if not settings.document_bucket:
        return {
            "upload": {
                "url": "/api/v1/lawyers/me/documents/mock-upload",
                "fields": {"key": f"lawyers/{user.id}/mock-{filename}"}
            },
            "key": f"lawyers/{user.id}/mock-{filename}",
            "expires_in": expiry
        }

    import boto3
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._-")[:120]
    key = f"lawyers/{user.id}/{secrets.token_hex(16)}-{safe_name}"
    client = boto3.client("s3", region_name=settings.aws_region)
    result = client.generate_presigned_post(
        settings.document_bucket, key,
        Fields={"Content-Type": content_type, "x-amz-server-side-encryption": "aws:kms"},
        Conditions=[{"Content-Type": content_type}, {"x-amz-server-side-encryption": "aws:kms"},
                    ["content-length-range", 1, settings.max_document_bytes]], ExpiresIn=expiry)
    return {"upload": result, "key": key, "expires_in": expiry}


@router.post("/api/v1/lawyers/me/documents/mock-upload", dependencies=[Depends(rate_limit_dependency("uploads"))])
def lawyer_document_mock_upload(key: str = Form(...), file: UploadFile = File(...),
                                _user: User = Depends(require_roles(Role.LAWYER))):
    import os
    from ..sanitizer import sanitize_key
    key = sanitize_key(key)
    file_path = os.path.join("uploads", key)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return {"status": "mock_success"}


@router.post("/api/v1/lawyers/me/documents/confirm")
def lawyer_document_confirm(filename: str, key: str, doc_type: str,
                             user: User = Depends(require_roles(Role.LAWYER)),
                             db: Session = Depends(get_db)):
    from ..sanitizer import sanitize_filename, sanitize_key
    if doc_type not in ("bar_license", "aadhaar"):
        raise HTTPException(400, "invalid document type")
    filename = sanitize_filename(filename)
    key = sanitize_key(key)

    profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == user.id))
    if not profile:
        raise HTTPException(404, "profile not found")

    url = f"/api/v1/lawyers/{user.id}/documents/download?key={key}"
    if doc_type == "bar_license":
        profile.bar_license_url = url
    elif doc_type == "aadhaar":
        profile.aadhaar_url = url

    audit(db, user, "lawyer.document_uploaded", "user", user.id, {"filename": filename, "key": key, "doc_type": doc_type})
    db.commit()
    return {"status": "success", "key": key}


@router.get("/api/v1/lawyers/{lawyer_id}/documents/download")
def download_lawyer_document(lawyer_id: str, key: str, token: str | None = None,
                             authorization: str | None = Header(default=None),
                             db: Session = Depends(get_db)):
    from ..sanitizer import sanitize_key
    key = sanitize_key(key)
    raw_token = None
    if authorization and authorization.startswith("Bearer "):
        raw_token = authorization.split(" ")[1]
    elif token:
        raw_token = token

    if not raw_token:
        raise HTTPException(status_code=401, detail="authentication required")

    import jwt
    from ..security import decode_token
    try:
        payload = decode_token(raw_token)
    except (HTTPException, jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc

    user = db.get(User, payload["sub"])
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="account unavailable")

    if user.role != Role.ADMIN and user.id != lawyer_id:
        raise HTTPException(403, "not authorized")

    import os
    from fastapi.responses import FileResponse
    file_path = os.path.join("uploads", key)
    if not os.path.exists(file_path):
        raise HTTPException(404, "file not found")
    return FileResponse(file_path)
