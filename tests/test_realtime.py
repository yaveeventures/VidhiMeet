import asyncio
import pytest
from fastapi.testclient import TestClient
from backend.services.event_bus import event_bus
from backend.models import User, Role, Practice, LawyerProfile, Booking, BookingStatus, Message
from backend.security import hash_password, create_access_token
from backend.main import app
from datetime import datetime, timezone, timedelta

def test_event_bus_pub_sub():
    async def _test():
        q1 = event_bus.subscribe_user("user-123")
        q2 = event_bus.subscribe_role("lawyer")

        await event_bus.publish_user("user-123", "TEST_USER_EVENT", {"foo": "bar"})
        await event_bus.publish_role("lawyer", "TEST_ROLE_EVENT", {"role": "lawyer"})

        msg1 = q1.get_nowait()
        assert msg1["event"] == "TEST_USER_EVENT"
        assert msg1["data"] == {"foo": "bar"}

        msg2 = q2.get_nowait()
        assert msg2["event"] == "TEST_ROLE_EVENT"

        event_bus.unsubscribe_user("user-123", q1)
        event_bus.unsubscribe_role("lawyer", q2)

    asyncio.run(_test())

def test_websocket_chat(database):
    no_raise_client = TestClient(app, raise_server_exceptions=False)
    pwd = hash_password("Pass123!")
    c_user = User(email="ws_client@test.com", password_hash=pwd, full_name="WS Client", role=Role.CLIENT)
    l_user = User(email="ws_lawyer@test.com", password_hash=pwd, full_name="WS Lawyer", role=Role.LAWYER)
    database.add(c_user)
    database.add(l_user)
    database.commit()

    lawyer_prof = LawyerProfile(user_id=l_user.id, practice=["corporate"], bar_number="BC-12345", hourly_fee_minor=50000)
    database.add(lawyer_prof)
    database.commit()

    now = datetime.now(timezone.utc)
    booking = Booking(
        client_id=c_user.id, lawyer_id=l_user.id, practice=Practice.CORPORATE,
        starts_at=now + timedelta(days=1), duration_minutes=30,
        amount_minor=50000, intake={}, disclaimer_version="1.0",
        disclaimer_accepted_at=now, status=BookingStatus.CONFIRMED, jitsi_room="room-ws"
    )
    database.add(booking)
    database.commit()

    token = create_access_token(c_user)

    with no_raise_client.websocket_connect(f"/api/v1/ws/chat/{booking.id}?token={token}") as websocket:
        websocket.send_json({"content": "Hello live WS chat!", "encrypted": False})
        data = websocket.receive_json()
        assert data["type"] == "new_message"
        assert data["message"]["content"] == "Hello live WS chat!"
        assert data["message"]["sender_id"] == str(c_user.id)
        websocket.close(code=1000)
