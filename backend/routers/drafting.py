from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import (
    DraftComment, DraftingProposal, DraftingRequest, DraftingStatus, LawyerProfile,
    Practice, ProposalStatus, Role, User
)
from ..schemas import (
    DraftCommentCreate, DraftCommentOut, DraftingProposalCreate, DraftingProposalOut,
    DraftingRequestCreate, DraftingRequestOut, DraftSubmit
)
from ..security import current_user, require_roles
from ..services import audit

router = APIRouter(prefix="/api/v1/drafting", tags=["drafting"])

MAX_ACTIVE_DRAFTS_PER_LAWYER = 2
_ACTIVE_STATUSES = (
    DraftingStatus.PENDING_PAYMENT,
    DraftingStatus.IN_PROGRESS,
    DraftingStatus.SUBMITTED,
    DraftingStatus.REVISION_REQUESTED,
)


@router.post("", response_model=DraftingRequestOut, status_code=201)
def create_drafting_request(payload: DraftingRequestCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in (Role.CLIENT, Role.LAWYER):
        raise HTTPException(403, "only clients and lawyers can request drafting")

    req = DraftingRequest(
        title=payload.title.strip(),
        description=payload.description.strip(),
        price_minor=payload.price_minor,
        creator_id=user.id,
        status=DraftingStatus.OPEN,
        documents=payload.documents
    )
    db.add(req)
    db.flush()
    audit(db, user, "drafting.created", "drafting_request", req.id, {"price": req.price_minor})
    db.commit()
    db.refresh(req)
    return req


def check_and_process_auto_approvals(db: Session):
    from datetime import datetime, timedelta, timezone
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    expired_query = select(DraftingRequest).where(
        DraftingRequest.status == DraftingStatus.SUBMITTED,
        DraftingRequest.submitted_at.is_not(None),
        DraftingRequest.submitted_at <= cutoff
    )
    expired_requests = db.scalars(expired_query).all()
    for req in expired_requests:
        req.status = DraftingStatus.COMPLETED
        audit(db, None, "drafting.auto_approved_7day_window", "drafting_request", req.id, {
            "agreed_price": req.agreed_price_minor,
            "platform_fee": req.platform_fee_minor,
            "lawyer_amount": req.drafter_amount_minor,
            "submitted_at": req.submitted_at.isoformat() if req.submitted_at else None,
            "auto_approved_at": datetime.now(timezone.utc).isoformat(),
            "reason": "7-day client revision inactivity auto-approval window expired"
        })
    if expired_requests:
        db.commit()


@router.get("", response_model=list[DraftingRequestOut])
def list_drafting_requests(user: User = Depends(current_user), db: Session = Depends(get_db)):
    check_and_process_auto_approvals(db)

    if user.role == Role.CLIENT:
        query = select(DraftingRequest).where(DraftingRequest.creator_id == user.id)
        requests = db.scalars(query).all()
        return list(requests)

    elif user.role == Role.LAWYER:
        # Check if lawyer profile is verified
        profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == user.id))
        is_verified = profile.verified if profile else False

        if is_verified:
            query = select(DraftingRequest).where(
                (DraftingRequest.status == DraftingStatus.OPEN) |
                (DraftingRequest.creator_id == user.id) |
                (DraftingRequest.drafter_id == user.id) |
                (DraftingRequest.id.in_(
                    select(DraftingProposal.request_id).where(DraftingProposal.lawyer_id == user.id)
                ))
            )
        else:
            query = select(DraftingRequest).where(
                (DraftingRequest.creator_id == user.id) |
                (DraftingRequest.drafter_id == user.id) |
                (DraftingRequest.id.in_(
                    select(DraftingProposal.request_id).where(DraftingProposal.lawyer_id == user.id)
                ))
            )

        requests = db.scalars(query).all()
        return list(requests)

    elif user.role == Role.ADMIN:
        query = select(DraftingRequest)
        requests = db.scalars(query).all()
        return list(requests)

    return []


@router.get("/documents/download")
def download_drafting_document(key: str, token: str | None = None,
                               authorization: str | None = None,
                               db: Session = Depends(get_db)):
    from fastapi import Header
    from ..sanitizer import sanitize_key
    key = sanitize_key(key)
    raw_token = None
    if authorization and authorization.startswith("Bearer "):
        raw_token = authorization.split(" ")[1]
    elif token:
        raw_token = token

    if not raw_token:
        raise HTTPException(401, "authentication required")

    try:
        from ..security import decode_token
        user_data = decode_token(raw_token)
        # Enforce 15-minute maximum link expiration (900 seconds) for document access
        from datetime import datetime, timezone
        token_iat = user_data.get("iat")
        if token_iat:
            now_ts = datetime.now(timezone.utc).timestamp()
            if now_ts - token_iat > 900:
                raise HTTPException(401, "document access link has expired")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(401, "invalid session token")

    user = db.get(User, user_data["sub"])
    if not user:
        raise HTTPException(401, "user not found")

    if user.role == Role.LAWYER:
        if not user.active:
            raise HTTPException(403, "unauthorized to view this document")

    from ..config import get_settings
    settings = get_settings()
    expiry = settings.presigned_url_expiry_seconds
    if settings.document_bucket:
        import boto3
        client = boto3.client("s3", region_name=settings.aws_region)
        url = client.generate_presigned_url(
            "get_object", Params={"Bucket": settings.document_bucket, "Key": key}, ExpiresIn=expiry
        )
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url)

    import os
    from fastapi.responses import FileResponse
    file_path = os.path.join("uploads", key)
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        basename = os.path.basename(key)
        _write_mock_pdf(file_path, basename)
    return FileResponse(file_path, filename=os.path.basename(key), media_type="application/pdf")


from ..rate_limiter import rate_limit_dependency


@router.post("/documents/presign", dependencies=[Depends(rate_limit_dependency("uploads"))])
def drafting_document_presign(filename: str, content_type: str,
                              user: User = Depends(current_user),
                              db: Session = Depends(get_db)):
    import secrets
    from ..config import get_settings
    from ..sanitizer import sanitize_filename
    settings = get_settings()
    filename = sanitize_filename(filename)
    expiry = settings.presigned_url_expiry_seconds

    allowed = {"application/pdf", "image/jpeg", "image/png",
               "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
               "application/msword", "text/plain", "application/rtf", "application/octet-stream"}
    if content_type not in allowed:
        raise HTTPException(415, "unsupported document type")

    if not settings.document_bucket:
        return {
            "upload": {
                "url": "/api/v1/drafting/documents/mock-upload",
                "fields": {"key": f"drafting/{user.id}/mock-{filename}"}
            },
            "key": f"drafting/{user.id}/mock-{filename}",
            "expires_in": expiry
        }

    import boto3
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._-")[:120]
    key = f"drafting/{user.id}/{secrets.token_hex(16)}-{safe_name}"
    client = boto3.client("s3", region_name=settings.aws_region)
    result = client.generate_presigned_post(
        settings.document_bucket, key,
        Fields={"Content-Type": content_type, "x-amz-server-side-encryption": "aws:kms"},
        Conditions=[{"Content-Type": content_type}, {"x-amz-server-side-encryption": "aws:kms"},
                    ["content-length-range", 1, settings.max_document_bytes]], ExpiresIn=expiry)
    return {"upload": result, "key": key, "expires_in": expiry}


@router.post("/documents/mock-upload", dependencies=[Depends(rate_limit_dependency("uploads"))])
def drafting_document_mock_upload(key: str = Form(...), file: UploadFile = File(...),
                                _user: User = Depends(current_user)):
    import os
    from ..sanitizer import sanitize_key
    key = sanitize_key(key)
    file_path = os.path.join("uploads", key)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return {"status": "mock_success"}


@router.get("/{request_id}", response_model=DraftingRequestOut)
def get_drafting_request(request_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    check_and_process_auto_approvals(db)
    req = db.get(DraftingRequest, request_id)
    if not req:
        raise HTTPException(404, "drafting request not found")

    profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == user.id)) if user.role == Role.LAWYER else None
    is_verified_lawyer = (user.role == Role.LAWYER and profile and profile.verified)

    has_bid = False
    if user.role == Role.LAWYER:
        has_bid = db.scalar(select(func.count(DraftingProposal.id)).where(
            DraftingProposal.request_id == request_id,
            DraftingProposal.lawyer_id == user.id
        )) > 0

    if (user.role != Role.ADMIN and
        user.id != req.creator_id and
        user.id != req.drafter_id and
        not has_bid and
        not (is_verified_lawyer and req.status == DraftingStatus.OPEN)):
        raise HTTPException(403, "unauthorized to view this request")

    return req


@router.post("/{request_id}/accept", response_model=DraftingRequestOut)
def accept_drafting_request(request_id: str, user: User = Depends(require_roles(Role.LAWYER)), db: Session = Depends(get_db)):
    profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == user.id))
    if not profile or not profile.verified:
        raise HTTPException(403, "only verified lawyers can accept drafting requests")

    req = db.get(DraftingRequest, request_id)
    if not req:
        raise HTTPException(404, "drafting request not found")

    if req.status != DraftingStatus.OPEN:
        raise HTTPException(400, "this drafting request is not open for acceptance")

    if req.creator_id == user.id:
        raise HTTPException(400, "you cannot accept your own drafting request")

    active_count = db.scalar(
        select(func.count(DraftingRequest.id)).where(
            DraftingRequest.drafter_id == user.id,
            DraftingRequest.status.in_(_ACTIVE_STATUSES)
        )
    )
    if active_count >= MAX_ACTIVE_DRAFTS_PER_LAWYER:
        raise HTTPException(400, f"you already have {MAX_ACTIVE_DRAFTS_PER_LAWYER} active drafts; complete or cancel one before accepting a new request")

    req.drafter_id = user.id
    req.agreed_price_minor = req.price_minor
    req.status = DraftingStatus.PENDING_PAYMENT

    proposal = DraftingProposal(
        request_id=req.id,
        lawyer_id=user.id,
        amount_minor=req.price_minor,
        status=ProposalStatus.ACCEPTED
    )
    db.add(proposal)

    audit(db, user, "drafting.accepted_original", "drafting_request", req.id, {"price": req.price_minor})
    db.commit()
    db.refresh(req)
    return req


@router.post("/{request_id}/proposals", response_model=DraftingProposalOut, status_code=201)
def counter_drafting_request(request_id: str, payload: DraftingProposalCreate, user: User = Depends(require_roles(Role.LAWYER)), db: Session = Depends(get_db)):
    profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == user.id))
    if not profile or not profile.verified:
        raise HTTPException(403, "only verified lawyers can quote/counter drafting requests")

    req = db.get(DraftingRequest, request_id)
    if not req:
        raise HTTPException(404, "drafting request not found")

    if req.status != DraftingStatus.OPEN:
        raise HTTPException(400, "this drafting request is not open for counter-offers")

    if req.creator_id == user.id:
        raise HTTPException(400, "you cannot counter your own drafting request")

    existing = db.scalar(select(DraftingProposal).where(
        DraftingProposal.request_id == request_id,
        DraftingProposal.lawyer_id == user.id,
        DraftingProposal.status == ProposalStatus.PENDING
    ))
    if existing:
        existing.amount_minor = payload.amount_minor
        proposal = existing
    else:
        proposal = DraftingProposal(
            request_id=req.id,
            lawyer_id=user.id,
            amount_minor=payload.amount_minor,
            status=ProposalStatus.PENDING
        )
        db.add(proposal)

    audit(db, user, "drafting.proposal_created", "drafting_proposal", request_id, {"amount": payload.amount_minor})
    db.commit()
    db.refresh(proposal)
    return proposal


@router.post("/{request_id}/proposals/{proposal_id}/accept", response_model=DraftingRequestOut)
def accept_drafting_proposal(request_id: str, proposal_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    req = db.get(DraftingRequest, request_id)
    if not req:
        raise HTTPException(404, "drafting request not found")

    if req.creator_id != user.id:
        raise HTTPException(403, "only the creator of the request can accept proposals")

    if req.status != DraftingStatus.OPEN:
        raise HTTPException(400, "request is no longer open")

    proposal = db.get(DraftingProposal, proposal_id)
    if not proposal or proposal.request_id != request_id:
        raise HTTPException(404, "proposal not found")

    if proposal.status != ProposalStatus.PENDING:
        raise HTTPException(400, "proposal is not pending")

    # Enforce per-lawyer active draft cap
    lawyer_active_count = db.scalar(
        select(func.count(DraftingRequest.id)).where(
            DraftingRequest.drafter_id == proposal.lawyer_id,
            DraftingRequest.status.in_(_ACTIVE_STATUSES)
        )
    )
    if lawyer_active_count >= MAX_ACTIVE_DRAFTS_PER_LAWYER:
        raise HTTPException(400, f"the selected lawyer already has {MAX_ACTIVE_DRAFTS_PER_LAWYER} active drafts and cannot take on more work right now")

    proposal.status = ProposalStatus.ACCEPTED
    req.drafter_id = proposal.lawyer_id
    req.agreed_price_minor = proposal.amount_minor
    req.status = DraftingStatus.PENDING_PAYMENT

    db.execute(
        update(DraftingProposal)
        .where(DraftingProposal.request_id == request_id, DraftingProposal.id != proposal_id)
        .values(status=ProposalStatus.REJECTED)
    )

    audit(db, user, "drafting.proposal_accepted", "drafting_request", req.id, {"proposal_id": proposal_id, "price": proposal.amount_minor})
    db.commit()
    db.refresh(req)
    return req


@router.post("/{request_id}/confirm-payment", response_model=DraftingRequestOut)
def confirm_drafting_payment(request_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    req = db.get(DraftingRequest, request_id)
    if not req:
        raise HTTPException(404, "drafting request not found")

    if req.creator_id != user.id:
        raise HTTPException(403, "only the creator can confirm payment")

    if req.status != DraftingStatus.PENDING_PAYMENT:
        raise HTTPException(400, "request is not pending payment")

    req.status = DraftingStatus.IN_PROGRESS
    audit(db, user, "drafting.payment_confirmed", "drafting_request", req.id, {"price": req.agreed_price_minor})
    db.commit()
    db.refresh(req)
    return req


@router.post("/{request_id}/submit", response_model=DraftingRequestOut)
def submit_draft(request_id: str, payload: DraftSubmit, request: Request, user: User = Depends(require_roles(Role.LAWYER)), db: Session = Depends(get_db)):
    from datetime import datetime, timedelta, timezone
    req = db.get(DraftingRequest, request_id)
    if not req:
        raise HTTPException(404, "drafting request not found")

    if req.drafter_id != user.id:
        raise HTTPException(403, "only the assigned lawyer can submit the draft")

    if req.status not in (DraftingStatus.IN_PROGRESS, DraftingStatus.REVISION_REQUESTED):
        raise HTTPException(400, "cannot submit draft, request is not in progress or in revision")

    if payload.draft_file_key:
        req.draft_file_key = payload.draft_file_key.strip()
    if payload.draft_filename:
        req.draft_filename = payload.draft_filename.strip()
    if payload.draft_text:
        req.draft_text = payload.draft_text.strip()

    now_ts = datetime.now(timezone.utc)
    req.submitted_at = now_ts
    req.status = DraftingStatus.SUBMITTED

    client_ip = request.client.host if (request and request.client) else "unknown"
    user_agent = request.headers.get("user-agent", "unknown") if request else "unknown"

    audit(db, user, "drafting.submitted", "drafting_request", req.id, {
        "filename": req.draft_filename,
        "draft_file_key": req.draft_file_key,
        "submitted_at": now_ts.isoformat(),
        "auto_approve_at": (now_ts + timedelta(days=7)).isoformat(),
        "lawyer_ip": client_ip,
        "user_agent": user_agent
    })
    db.commit()
    db.refresh(req)
    return req


@router.post("/{request_id}/approve", response_model=DraftingRequestOut)
def approve_draft(request_id: str, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    from datetime import datetime, timezone
    req = db.get(DraftingRequest, request_id)
    if not req:
        raise HTTPException(404, "drafting request not found")

    if req.creator_id != user.id:
        raise HTTPException(403, "only the creator can approve the draft")

    if req.status not in (DraftingStatus.SUBMITTED, DraftingStatus.REVISION_REQUESTED):
        raise HTTPException(400, "no draft is submitted for review")

    now_ts = datetime.now(timezone.utc)
    req.status = DraftingStatus.COMPLETED

    client_ip = request.client.host if (request and request.client) else "unknown"
    user_agent = request.headers.get("user-agent", "unknown") if request else "unknown"

    audit(db, user, "drafting.approved", "drafting_request", req.id, {
        "agreed_price": req.agreed_price_minor,
        "platform_fee": req.platform_fee_minor,
        "lawyer_amount": req.drafter_amount_minor,
        "client_ip": client_ip,
        "user_agent": user_agent,
        "draft_file_key": req.draft_file_key,
        "draft_filename": req.draft_filename,
        "approved_timestamp": now_ts.isoformat(),
        "legal_signoff_proof": f"Client {user.id} ({user.full_name}) manually reviewed and signed off final version {req.draft_filename or 'document'} ({req.draft_file_key}) from IP {client_ip} at {now_ts.isoformat()}"
    })
    db.commit()
    db.refresh(req)
    return req


@router.post("/{request_id}/cancel", response_model=DraftingRequestOut)
def cancel_drafting_request(request_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    req = db.get(DraftingRequest, request_id)
    if not req:
        raise HTTPException(404, "drafting request not found")

    if req.creator_id != user.id and req.drafter_id != user.id:
        raise HTTPException(403, "unauthorized to cancel this request")

    if req.status not in (DraftingStatus.OPEN, DraftingStatus.PENDING_PAYMENT):
        raise HTTPException(400, "cannot cancel request at this stage")

    req.status = DraftingStatus.CANCELLED

    db.execute(
        update(DraftingProposal)
        .where(DraftingProposal.request_id == request_id)
        .values(status=ProposalStatus.REJECTED)
    )

    audit(db, user, "drafting.cancelled", "drafting_request", req.id)
    db.commit()
    db.refresh(req)
    return req


@router.get("/{request_id}/comments", response_model=list[DraftCommentOut])
def list_draft_comments(request_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    req = db.get(DraftingRequest, request_id)
    if not req:
        raise HTTPException(404, "drafting request not found")

    if user.role != Role.ADMIN and user.id != req.creator_id and user.id != req.drafter_id:
        raise HTTPException(403, "unauthorized to view comments")

    return req.comments


@router.post("/{request_id}/comments", response_model=DraftCommentOut, status_code=201)
def add_draft_comment(request_id: str, payload: DraftCommentCreate, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    req = db.get(DraftingRequest, request_id)
    if not req:
        raise HTTPException(404, "drafting request not found")

    if req.status in (DraftingStatus.COMPLETED, DraftingStatus.CANCELLED):
        raise HTTPException(400, "Version freeze active: document is finalized and read-only.")

    if user.id != req.creator_id and user.id != req.drafter_id and user.role != Role.ADMIN:
        raise HTTPException(403, "unauthorized to comment on this draft")

    comment = DraftComment(
        request_id=req.id,
        user_id=user.id,
        page_number=payload.page_number,
        position_x=payload.position_x,
        position_y=payload.position_y,
        selected_text=payload.selected_text.strip() if payload.selected_text else None,
        comment=payload.comment.strip()
    )
    db.add(comment)
    client_ip = request.client.host if (request and request.client) else "unknown"
    audit(db, user, "drafting.comment_added", "drafting_request", req.id, {
        "page_number": payload.page_number,
        "position_x": payload.position_x,
        "position_y": payload.position_y,
        "user_ip": client_ip
    })
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{request_id}/comments/{comment_id}", status_code=204)
def delete_draft_comment(request_id: str, comment_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    comment = db.get(DraftComment, comment_id)
    if not comment:
        return None  # Idempotent success if comment is already removed

    req = db.get(DraftingRequest, comment.request_id or request_id)
    if req and req.status in (DraftingStatus.COMPLETED, DraftingStatus.CANCELLED):
        raise HTTPException(400, "Version freeze active: document is finalized and read-only.")

    # Allow request participants (client, lawyer, author, or admin) to delete feedback comments
    if req and user.role != Role.ADMIN and user.id != comment.user_id and user.id != req.creator_id and user.id != req.drafter_id:
        if user.role not in (Role.CLIENT, Role.LAWYER):
            raise HTTPException(403, "unauthorized to delete this comment")

    db.delete(comment)
    audit(db, user, "drafting.comment_deleted", "drafting_request", request_id, {"comment_id": comment_id})
    db.commit()
    return None


@router.post("/{request_id}/request-revisions", response_model=DraftingRequestOut)
def request_draft_revisions(request_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    req = db.get(DraftingRequest, request_id)
    if not req:
        raise HTTPException(404, "drafting request not found")

    if req.creator_id != user.id:
        raise HTTPException(403, "only the client can request revisions")

    if req.status not in (DraftingStatus.SUBMITTED, DraftingStatus.REVISION_REQUESTED):
        raise HTTPException(400, "cannot request revisions for this request")

    req.status = DraftingStatus.REVISION_REQUESTED
    audit(db, user, "drafting.revisions_requested", "drafting_request", req.id, {"comments_count": len(req.comments)})
    db.commit()
    db.refresh(req)
    return req
