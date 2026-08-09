import asyncio
import json
import logging
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from ..db import engine
from ..models import Booking, Message, User
from ..security import decode_token, encrypt_field, decrypt_field
from ..services.event_bus import event_bus

log = logging.getLogger("websocket_chat")
router = APIRouter(tags=["chat"])

class ConnectionManager:
    def __init__(self):
        # Maps booking_id -> Dict[WebSocket, dict(user_id, role, full_name)]
        self.active_connections: Dict[str, Dict[WebSocket, dict]] = {}

    async def connect(self, booking_id: str, websocket: WebSocket, user_info: dict):
        await websocket.accept()
        if booking_id not in self.active_connections:
            self.active_connections[booking_id] = {}
        self.active_connections[booking_id][websocket] = user_info
        log.info(f"WebSocket client connected to booking {booking_id}: user={user_info['user_id']}")

    def disconnect(self, booking_id: str, websocket: WebSocket):
        if booking_id in self.active_connections:
            if websocket in self.active_connections[booking_id]:
                del self.active_connections[booking_id][websocket]
            if not self.active_connections[booking_id]:
                del self.active_connections[booking_id]
        log.info(f"WebSocket client disconnected from booking {booking_id}")

    async def broadcast(self, booking_id: str, message_data: dict):
        if booking_id in self.active_connections:
            for ws in list(self.active_connections[booking_id].keys()):
                try:
                    await ws.send_json(message_data)
                except Exception as exc:
                    log.error(f"Error sending WS message to client in booking {booking_id}: {exc}")

ws_manager = ConnectionManager()

def _validate_ws_user_and_booking(user_id: str, booking_id: str):
    with Session(engine) as db:
        user = db.get(User, user_id)
        booking = db.get(Booking, booking_id)
        if not user or not user.active or not booking:
            return None, None, None

        is_client = booking.client_id == user.id
        is_lawyer = booking.lawyer_id == user.id
        role_val = user.role.value if hasattr(user.role, "value") else str(user.role)
        if not is_client and not is_lawyer and role_val != "admin":
            return None, None, None

        recipient_user_id = str(booking.lawyer_id) if is_client else str(booking.client_id)
        user_info = {
            "user_id": str(user.id),
            "role": role_val,
            "full_name": user.full_name,
            "recipient_user_id": recipient_user_id
        }
        return user, booking, user_info

def _save_ws_message(booking_id: str, user_id: str, content: str, encrypted: bool, iv: str, sender_name: str, sender_role: str):
    with Session(engine) as db:
        stored_content = content if encrypted else encrypt_field(content)
        msg = Message(
            booking_id=booking_id,
            sender_id=user_id,
            content=stored_content,
            encrypted=encrypted,
            iv=iv
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)

        out_content = content if encrypted else (decrypt_field(msg.content) or msg.content)
        return {
            "id": msg.id,
            "booking_id": msg.booking_id,
            "sender_id": msg.sender_id,
            "sender_name": sender_name,
            "sender_role": sender_role,
            "content": out_content,
            "encrypted": msg.encrypted,
            "iv": msg.iv,
            "created_at": msg.created_at.isoformat() if msg.created_at else None
        }

@router.websocket("/api/v1/ws/chat/{booking_id}")
async def websocket_chat_endpoint(websocket: WebSocket, booking_id: str):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token required")
        return

    try:
        payload = decode_token(token)
        user_id = payload["sub"]
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    user, booking, user_info = await run_in_threadpool(_validate_ws_user_and_booking, user_id, booking_id)
    if not user or not booking or not user_info:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Unauthorized or invalid session")
        return

    recipient_user_id = user_info["recipient_user_id"]
    await ws_manager.connect(booking_id, websocket, user_info)

    try:
        while True:
            raw_text = await websocket.receive_text()
            try:
                msg_payload = json.loads(raw_text)
            except Exception:
                continue

            content = msg_payload.get("content", "").strip()
            encrypted = bool(msg_payload.get("encrypted", False))
            iv = msg_payload.get("iv")

            if not content:
                continue

            out_msg = await run_in_threadpool(
                _save_ws_message,
                booking_id,
                user_id,
                content,
                encrypted,
                iv,
                user_info["full_name"],
                user_info["role"]
            )

            # Broadcast to active WebSocket connections in booking
            await ws_manager.broadcast(booking_id, {"type": "new_message", "message": out_msg})

            # Publish SSE event to recipient user queue
            await event_bus.publish_user(recipient_user_id, "CHAT_MESSAGE_RECEIVED", {
                "booking_id": booking_id,
                "sender_name": user_info["full_name"],
                "message": out_msg
            })

    except WebSocketDisconnect:
        ws_manager.disconnect(booking_id, websocket)
    except Exception as exc:
        log.error(f"WebSocket error for booking {booking_id}: {exc}")
        ws_manager.disconnect(booking_id, websocket)
