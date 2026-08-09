import asyncio
import json
import structlog
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..security import decode_token
from ..services.event_bus import event_bus

log = structlog.get_logger("events")
router = APIRouter(tags=["events"])

def authenticate_stream_user(token: Optional[str] = Query(None), request: Request = None, db: Session = Depends(get_db)) -> User:
    jwt_token = token
    if not jwt_token and request:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            jwt_token = auth_header.split(" ")[1]

    if not jwt_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication token required")

    payload = decode_token(jwt_token)
    user = db.get(User, payload["sub"])
    if not user or not user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account unavailable")
    return user

@router.get("/api/v1/events/stream")
async def sse_event_stream(request: Request, user: User = Depends(authenticate_stream_user)):
    """
    Server-Sent Events (SSE) stream endpoint for real-time notifications and UI auto-refresh.
    Pushes events: BOOKING_CREATED, DRAFT_REQUEST_SUBMITTED, PROPOSAL_ACCEPTED, etc.
    """
    user_id = str(user.id)
    role_val = user.role.value if hasattr(user.role, "value") else str(user.role)

    user_queue = event_bus.subscribe_user(user_id)
    role_queue = event_bus.subscribe_role(role_val)

    async def event_generator():
        log.info(f"SSE client connected: user={user_id} role={role_val}")
        try:
            # Yield initial connection confirmation event
            init_payload = {"status": "connected", "user_id": user_id, "role": role_val}
            yield f"event: connected\ndata: {json.dumps(init_payload)}\n\n"

            while True:
                if await request.is_disconnected():
                    log.info(f"SSE client disconnected: user={user_id}")
                    break

                try:
                    # Wait for message on user queue or role queue, or timeout after 15s for heartbeat
                    get_user_task = asyncio.create_task(user_queue.get())
                    get_role_task = asyncio.create_task(role_queue.get())

                    done, pending = await asyncio.wait(
                        [get_user_task, get_role_task],
                        timeout=15.0,
                        return_when=asyncio.FIRST_COMPLETED
                    )

                    for task in pending:
                        task.cancel()

                    if not done:
                        # Heartbeat ping to keep connection alive over proxies / ngrok
                        yield ": ping\n\n"
                        continue

                    for task in done:
                        event_item = task.result()
                        event_name = event_item.get("event", "message")
                        event_data = event_item.get("data", {})
                        log.info(f"Sending SSE event '{event_name}' to user {user_id}")
                        yield f"event: {event_name}\ndata: {json.dumps(event_data)}\n\n"

                except asyncio.CancelledError:
                    break
                except (RuntimeError, OSError) as exc:
                    log.error("Error in SSE generator", user_id=user_id, error=str(exc))
                    break
        finally:
            event_bus.unsubscribe_user(user_id, user_queue)
            event_bus.unsubscribe_role(role_val, role_queue)
            log.info(f"SSE client subscription cleaned up: user={user_id}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
