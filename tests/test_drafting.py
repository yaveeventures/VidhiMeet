import pytest
from backend.db import SessionLocal
from backend.models import User, Role, LawyerProfile, DraftingRequest, DraftingProposal, DraftingStatus, ProposalStatus
from backend.security import hash_password

def register_user(client, email, role, full_name="Test User"):
    payload = {
        "email": email,
        "password": "a-secure-password-123",
        "full_name": full_name,
        "role": role,
        "consent_privacy_policy": True,
        "consent_terms": True
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    return resp.json()["access_token"]

def get_user_by_email(email):
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    db.close()
    return user

def verify_lawyer(user_id):
    db = SessionLocal()
    profile = db.query(LawyerProfile).filter_by(user_id=user_id).first()
    if profile:
        profile.verified = True
        db.commit()
    db.close()


def test_create_drafting_request(client):
    token = register_user(client, "client@example.com", "client", "John Client")
    
    payload = {
        "title": "Partnership Deed",
        "description": "Standard business partnership agreement draft",
        "price_minor": 300000 # 3000 INR
    }
    
    resp = client.post(
        "/api/v1/drafting",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Partnership Deed"
    assert data["description"] == "Standard business partnership agreement draft"
    assert data["price_minor"] == 300000
    assert data["status"] == "open"
    assert data["creator_name"] == "John Client"


def test_list_drafting_requests_visibility(client):
    c1_token = register_user(client, "c1@example.com", "client", "Client One")
    c2_token = register_user(client, "c2@example.com", "client", "Client Two")
    l1_token = register_user(client, "l1@example.com", "lawyer", "Lawyer One")
    
    l1_user = get_user_by_email("l1@example.com")
    
    # Client 1 creates request
    r1 = client.post(
        "/api/v1/drafting",
        json={"title": "Request One", "description": "Desc One", "price_minor": 10000},
        headers={"Authorization": f"Bearer {c1_token}"}
    )
    assert r1.status_code == 201
    
    # Client 2 creates request
    r2 = client.post(
        "/api/v1/drafting",
        json={"title": "Request Two", "description": "Desc Two", "price_minor": 20000},
        headers={"Authorization": f"Bearer {c2_token}"}
    )
    assert r2.status_code == 201
    
    # Client 1 list -> should only see Request One
    c1_list = client.get("/api/v1/drafting", headers={"Authorization": f"Bearer {c1_token}"}).json()
    assert len(c1_list) == 1
    assert c1_list[0]["title"] == "Request One"
    
    # Unverified lawyer 1 list -> should see nothing
    l1_list_unverified = client.get("/api/v1/drafting", headers={"Authorization": f"Bearer {l1_token}"}).json()
    assert len(l1_list_unverified) == 0
    
    # Verify lawyer 1
    verify_lawyer(l1_user.id)
    
    # Verified lawyer 1 list -> should see both requests (since they are open)
    l1_list_verified = client.get("/api/v1/drafting", headers={"Authorization": f"Bearer {l1_token}"}).json()
    assert len(l1_list_verified) == 2


def test_accept_drafting_request(client):
    c1_token = register_user(client, "c1@example.com", "client", "Client One")
    l1_token = register_user(client, "l1@example.com", "lawyer", "Lawyer One")
    
    l1_user = get_user_by_email("l1@example.com")
    
    r = client.post(
        "/api/v1/drafting",
        json={"title": "NDA", "description": "NDA draft needed", "price_minor": 15000},
        headers={"Authorization": f"Bearer {c1_token}"}
    ).json()
    
    # Unverified lawyer tries to accept
    err_resp = client.post(
        f"/api/v1/drafting/{r['id']}/accept",
        headers={"Authorization": f"Bearer {l1_token}"}
    )
    assert err_resp.status_code == 403
    
    # Verify lawyer
    verify_lawyer(l1_user.id)
    
    # Accept request
    accept_resp = client.post(
        f"/api/v1/drafting/{r['id']}/accept",
        headers={"Authorization": f"Bearer {l1_token}"}
    )
    assert accept_resp.status_code == 200
    
    data = accept_resp.json()
    assert data["status"] == "pending_payment"
    assert data["drafter_id"] == l1_user.id
    assert data["agreed_price_minor"] == 15000


def test_counter_proposal_flow(client):
    c1_token = register_user(client, "c1@example.com", "client", "Client One")
    l1_token = register_user(client, "l1@example.com", "lawyer", "Lawyer One")
    
    l1_user = get_user_by_email("l1@example.com")
    verify_lawyer(l1_user.id)
    
    r = client.post(
        "/api/v1/drafting",
        json={"title": "Will Draft", "description": "Will draft needed", "price_minor": 20000},
        headers={"Authorization": f"Bearer {c1_token}"}
    ).json()
    
    # Lawyer counter-offers
    counter = client.post(
        f"/api/v1/drafting/{r['id']}/proposals",
        json={"amount_minor": 25000},
        headers={"Authorization": f"Bearer {l1_token}"}
    )
    assert counter.status_code == 201
    prop = counter.json()
    assert prop["amount_minor"] == 25000
    assert prop["status"] == "pending"
    
    # Client accepts counter-offer
    accept = client.post(
        f"/api/v1/drafting/{r['id']}/proposals/{prop['id']}/accept",
        headers={"Authorization": f"Bearer {c1_token}"}
    )
    assert accept.status_code == 200
    data = accept.json()
    assert data["status"] == "pending_payment"
    assert data["drafter_id"] == l1_user.id
    assert data["agreed_price_minor"] == 25000


def test_payment_and_draft_submission_and_approval(client):
    c1_token = register_user(client, "c1@example.com", "client", "Client One")
    l1_token = register_user(client, "l1@example.com", "lawyer", "Lawyer One")
    
    l1_user = get_user_by_email("l1@example.com")
    verify_lawyer(l1_user.id)
    
    r = client.post(
        "/api/v1/drafting",
        json={"title": "Rent Agreement", "description": "Rent agreement draft", "price_minor": 100000},
        headers={"Authorization": f"Bearer {c1_token}"}
    ).json()
    
    # Lawyer accepts
    client.post(f"/api/v1/drafting/{r['id']}/accept", headers={"Authorization": f"Bearer {l1_token}"})
    
    # Client pays
    pay_resp = client.post(
        f"/api/v1/drafting/{r['id']}/confirm-payment",
        headers={"Authorization": f"Bearer {c1_token}"}
    )
    assert pay_resp.status_code == 200
    assert pay_resp.json()["status"] == "in_progress"
    
    # Lawyer submits draft
    submit_resp = client.post(
        f"/api/v1/drafting/{r['id']}/submit",
        json={"draft_text": "This rent agreement is made on this 20th day of..."},
        headers={"Authorization": f"Bearer {l1_token}"}
    )
    assert submit_resp.status_code == 200
    assert submit_resp.json()["status"] == "submitted"
    assert submit_resp.json()["draft_text"] == "This rent agreement is made on this 20th day of..."
    
    # Client approves draft
    approve_resp = client.post(
        f"/api/v1/drafting/{r['id']}/approve",
        headers={"Authorization": f"Bearer {c1_token}"}
    )
    assert approve_resp.status_code == 200
    
    data = approve_resp.json()
    assert data["status"] == "completed"
    assert data["platform_fee_minor"] == 10000  # 10% of 100000
    assert data["drafter_amount_minor"] == 90000 # 90% of 100000


def test_cancel_drafting_request(client):
    c1_token = register_user(client, "c1@example.com", "client", "Client One")
    
    r = client.post(
        "/api/v1/drafting",
        json={"title": "To Cancel", "description": "To cancel desc", "price_minor": 10000},
        headers={"Authorization": f"Bearer {c1_token}"}
    ).json()
    
    cancel_resp = client.post(
        f"/api/v1/drafting/{r['id']}/cancel",
        headers={"Authorization": f"Bearer {c1_token}"}
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"


def test_draft_inline_comments_and_revision_flow(client):
    c1_token = register_user(client, "c1@example.com", "client", "Client One")
    l1_token = register_user(client, "l1@example.com", "lawyer", "Lawyer One")
    
    l1_user = get_user_by_email("l1@example.com")
    verify_lawyer(l1_user.id)
    
    r = client.post(
        "/api/v1/drafting",
        json={"title": "Partnership Deed", "description": "Draft partnership deed", "price_minor": 50000},
        headers={"Authorization": f"Bearer {c1_token}"}
    ).json()
    
    client.post(f"/api/v1/drafting/{r['id']}/accept", headers={"Authorization": f"Bearer {l1_token}"})
    client.post(f"/api/v1/drafting/{r['id']}/confirm-payment", headers={"Authorization": f"Bearer {c1_token}"})
    
    # Lawyer submits draft
    client.post(
        f"/api/v1/drafting/{r['id']}/submit",
        json={"draft_file_key": "drafts/v1.pdf", "draft_filename": "Partnership_Deed_v1.pdf"},
        headers={"Authorization": f"Bearer {l1_token}"}
    )
    
    # Client adds inline comment pin
    cmt_resp = client.post(
        f"/api/v1/drafting/{r['id']}/comments",
        json={
            "page_number": 1,
            "position_x": 25.5,
            "position_y": 40.0,
            "selected_text": "Profit ratio 50:50",
            "comment": "Please change profit ratio to 60:40."
        },
        headers={"Authorization": f"Bearer {c1_token}"}
    )
    assert cmt_resp.status_code == 201
    cmt_data = cmt_resp.json()
    assert cmt_data["page_number"] == 1
    assert cmt_data["comment"] == "Please change profit ratio to 60:40."

    # Client requests revisions
    rev_resp = client.post(
        f"/api/v1/drafting/{r['id']}/request-revisions",
        headers={"Authorization": f"Bearer {c1_token}"}
    )
    assert rev_resp.status_code == 200
    assert rev_resp.json()["status"] == "revision_requested"

    # Lawyer views comments
    comments_resp = client.get(
        f"/api/v1/drafting/{r['id']}/comments",
        headers={"Authorization": f"Bearer {l1_token}"}
    )
    assert comments_resp.status_code == 200
    assert len(comments_resp.json()) == 1

    # Client deletes comment
    del_resp = client.delete(
        f"/api/v1/drafting/{r['id']}/comments/{cmt_data['id']}",
        headers={"Authorization": f"Bearer {c1_token}"}
    )
    assert del_resp.status_code == 204

    # Lawyer re-submits updated draft
    submit_v2 = client.post(
        f"/api/v1/drafting/{r['id']}/submit",
        json={"draft_file_key": "drafts/v2.pdf", "draft_filename": "Partnership_Deed_v2.pdf"},
        headers={"Authorization": f"Bearer {l1_token}"}
    )
    assert submit_v2.status_code == 200
    assert submit_v2.json()["status"] == "submitted"


def test_version_freeze_and_legal_audit_trail(client):
    c1_token = register_user(client, "c1@example.com", "client", "Client One")
    l1_token = register_user(client, "l1@example.com", "lawyer", "Lawyer One")
    
    l1_user = get_user_by_email("l1@example.com")
    verify_lawyer(l1_user.id)
    
    r = client.post(
        "/api/v1/drafting",
        json={"title": "NDA Agreement", "description": "Draft NDA", "price_minor": 20000},
        headers={"Authorization": f"Bearer {c1_token}"}
    ).json()
    
    client.post(f"/api/v1/drafting/{r['id']}/accept", headers={"Authorization": f"Bearer {l1_token}"})
    client.post(f"/api/v1/drafting/{r['id']}/confirm-payment", headers={"Authorization": f"Bearer {c1_token}"})
    
    sub = client.post(
        f"/api/v1/drafting/{r['id']}/submit",
        json={"draft_file_key": "drafts/nda_v1.pdf", "draft_filename": "NDA_v1.pdf"},
        headers={"Authorization": f"Bearer {l1_token}"}
    ).json()

    assert sub["submitted_at"] is not None
    assert sub["auto_approve_at"] is not None

    # Client approves document (Version Freeze trigger)
    app_resp = client.post(
        f"/api/v1/drafting/{r['id']}/approve",
        headers={"Authorization": f"Bearer {c1_token}"}
    )
    assert app_resp.status_code == 200
    assert app_resp.json()["status"] == "completed"

    # Version Freeze: attempt to add comment on finalized document should return 400
    freeze_resp = client.post(
        f"/api/v1/drafting/{r['id']}/comments",
        json={"page_number": 1, "comment": "Late change request"},
        headers={"Authorization": f"Bearer {c1_token}"}
    )
    assert freeze_resp.status_code == 400
    assert "Version freeze active" in freeze_resp.json()["detail"]


def test_7day_auto_approval_window(client):
    from datetime import datetime, timedelta, timezone
    from backend.db import get_db
    from backend.models import DraftingRequest, DraftingStatus

    c1_token = register_user(client, "c1@example.com", "client", "Client One")
    l1_token = register_user(client, "l1@example.com", "lawyer", "Lawyer One")
    
    l1_user = get_user_by_email("l1@example.com")
    verify_lawyer(l1_user.id)
    
    r = client.post(
        "/api/v1/drafting",
        json={"title": "Service Contract", "description": "Draft service contract", "price_minor": 30000},
        headers={"Authorization": f"Bearer {c1_token}"}
    ).json()
    
    client.post(f"/api/v1/drafting/{r['id']}/accept", headers={"Authorization": f"Bearer {l1_token}"})
    client.post(f"/api/v1/drafting/{r['id']}/confirm-payment", headers={"Authorization": f"Bearer {c1_token}"})
    
    # Lawyer submits draft
    client.post(
        f"/api/v1/drafting/{r['id']}/submit",
        json={"draft_file_key": "drafts/contract.pdf", "draft_filename": "Contract.pdf"},
        headers={"Authorization": f"Bearer {l1_token}"}
    )

    # Manually backdate submitted_at by 8 days to simulate client inactivity
    db = next(get_db())
    db_req = db.get(DraftingRequest, r['id'])
    db_req.submitted_at = datetime.now(timezone.utc) - timedelta(days=8)
    db.commit()

    # Query request (triggers auto-approval check)
    get_resp = client.get(
        f"/api/v1/drafting/{r['id']}",
        headers={"Authorization": f"Bearer {c1_token}"}
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "completed"


def test_drafting_document_mock_upload_requires_auth(client):
    """Verify that /api/v1/drafting/documents/mock-upload requires authentication."""
    # Unauthenticated request should fail with 401
    resp_unauth = client.post(
        "/api/v1/drafting/documents/mock-upload",
        data={"key": "drafting/test.pdf"},
        files={"file": ("test.pdf", b"pdf content", "application/pdf")}
    )
    assert resp_unauth.status_code == 401

    # Authenticated request succeeds
    token = register_user(client, "uploader@example.com", "client", "Uploader User")
    resp_auth = client.post(
        "/api/v1/drafting/documents/mock-upload",
        data={"key": "drafting/test.pdf"},
        files={"file": ("test.pdf", b"pdf content", "application/pdf")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_auth.status_code == 200
    assert resp_auth.json() == {"status": "mock_success"}

