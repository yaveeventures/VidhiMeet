"""
test_ntp.py
-----------
Tests for NTP time synchronization (CERT-In / DPDP compliance).
"""

import socket
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch


# ── ntp_now() tests ────────────────────────────────────────────────────────────

def test_ntp_now_returns_utc_aware_datetime():
    """ntp_now() must always return a UTC-aware datetime regardless of server state."""
    from backend.ntp_time import ntp_now
    result = ntp_now()
    assert isinstance(result, datetime)
    assert result.tzinfo is not None
    assert result.tzinfo == timezone.utc or result.utcoffset().total_seconds() == 0


def test_ntp_now_ist_returns_ist_offset():
    """ntp_now_ist() must return a datetime in IST (UTC+05:30)."""
    from backend.ntp_time import ntp_now_ist
    from datetime import timedelta
    result = ntp_now_ist()
    assert isinstance(result, datetime)
    assert result.tzinfo is not None
    expected_offset = timedelta(hours=5, minutes=30)
    assert result.utcoffset() == expected_offset


def test_ntp_now_fallback_to_system_clock_on_all_failures():
    """When all NTP servers are unreachable, ntp_now() must fall back to system clock gracefully."""
    from backend.ntp_time import ntp_now
    # Patch socket to always raise timeout
    with patch("backend.ntp_time.socket.socket") as mock_sock_cls:
        mock_sock = MagicMock()
        mock_sock.__enter__ = lambda s: s
        mock_sock.__exit__ = MagicMock(return_value=False)
        mock_sock.sendto.side_effect = socket.timeout("timeout")
        mock_sock_cls.return_value = mock_sock

        before = datetime.now(timezone.utc)
        result = ntp_now()
        after = datetime.now(timezone.utc)

        assert isinstance(result, datetime)
        assert result.tzinfo is not None
        # Fallback time should be very close to system time
        assert before <= result <= after


# ── check_clock_drift() tests ──────────────────────────────────────────────────

def test_check_clock_drift_returns_expected_keys():
    """check_clock_drift() must return a dict with all required NtpStatus keys."""
    from backend.ntp_time import check_clock_drift
    result = check_clock_drift()
    assert isinstance(result, dict)
    for key in ("ntp_server", "synced_at", "system_time", "drift_seconds", "within_tolerance"):
        assert key in result, f"Missing key: {key}"


def test_check_clock_drift_within_tolerance_type():
    """within_tolerance must be a boolean."""
    from backend.ntp_time import check_clock_drift
    result = check_clock_drift()
    assert isinstance(result["within_tolerance"], bool)


def test_check_clock_drift_drift_seconds_type():
    """drift_seconds must be a float."""
    from backend.ntp_time import check_clock_drift
    result = check_clock_drift()
    assert isinstance(result["drift_seconds"], float)


def test_check_clock_drift_all_servers_unreachable():
    """When all NTP servers fail, within_tolerance must be False and server must be 'unavailable'."""
    from backend.ntp_time import check_clock_drift
    with patch("backend.ntp_time.socket.socket") as mock_sock_cls:
        mock_sock = MagicMock()
        mock_sock.__enter__ = lambda s: s
        mock_sock.__exit__ = MagicMock(return_value=False)
        mock_sock.sendto.side_effect = socket.timeout("timeout")
        mock_sock_cls.return_value = mock_sock

        result = check_clock_drift()
        assert result["within_tolerance"] is False
        assert result["ntp_server"] == "unavailable"


def test_check_clock_drift_large_drift_sets_within_tolerance_false():
    """Simulated large drift (10s) must set within_tolerance=False."""
    from backend.ntp_time import ntp_now, check_clock_drift
    from datetime import timedelta

    # Build a fake NTP time that is 10s behind system time
    fake_ntp_time = datetime.now(timezone.utc) - timedelta(seconds=10)

    with patch("backend.ntp_time._query_ntp_server", return_value=fake_ntp_time):
        result = check_clock_drift()
        assert result["within_tolerance"] is False
        assert abs(result["drift_seconds"]) >= 9.0  # Allow for tiny test execution lag


def test_check_clock_drift_small_drift_sets_within_tolerance_true():
    """Simulated tiny drift (0.05s) must set within_tolerance=True."""
    from backend.ntp_time import check_clock_drift
    from datetime import timedelta

    fake_ntp_time = datetime.now(timezone.utc) - timedelta(milliseconds=50)

    with patch("backend.ntp_time._query_ntp_server", return_value=fake_ntp_time):
        result = check_clock_drift()
        assert result["within_tolerance"] is True


# ── /api/v1/admin/ntp-status endpoint tests ────────────────────────────────────

def test_admin_ntp_status_endpoint_requires_auth(client):
    """GET /api/v1/admin/ntp-status must return 401 without a valid token."""
    res = client.get("/api/v1/admin/ntp-status")
    assert res.status_code in (401, 403)


def test_admin_ntp_status_endpoint_accessible_by_admin(client):
    """GET /api/v1/admin/ntp-status must return 200 with the expected keys for an admin user."""
    from backend.db import get_db
    from backend.models import User, Role
    from backend.security import hash_password, create_access_token
    from sqlalchemy import select

    # Create an admin user directly in the test DB
    db = next(get_db())
    admin_email = "ntp_admin@example.com"
    existing = db.scalar(select(User).where(User.email == admin_email))
    if not existing:
        admin_user = User(
            email=admin_email,
            password_hash=hash_password("admin-password-secure-123"),
            full_name="NTP Test Admin",
            role=Role.ADMIN,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
    else:
        admin_user = existing

    token = create_access_token(admin_user)
    res = client.get("/api/v1/admin/ntp-status", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    for key in ("ntp_server", "synced_at", "system_time", "drift_seconds", "within_tolerance"):
        assert key in data, f"Missing key in ntp-status response: {key}"
    assert isinstance(data["within_tolerance"], bool)
    assert isinstance(data["drift_seconds"], float)
