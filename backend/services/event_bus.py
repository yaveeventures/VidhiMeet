import asyncio
import json
import logging
from typing import Dict, Set

log = logging.getLogger("event_bus")

class EventBus:
    def __init__(self):
        # Maps user_id -> Set of asyncio.Queue
        self._user_subscribers: Dict[str, Set[asyncio.Queue]] = {}
        # Maps role (e.g. "lawyer") -> Set of asyncio.Queue
        self._role_subscribers: Dict[str, Set[asyncio.Queue]] = {}

    def subscribe_user(self, user_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        if user_id not in self._user_subscribers:
            self._user_subscribers[user_id] = set()
        self._user_subscribers[user_id].add(queue)
        log.debug(f"User {user_id} subscribed to SSE events. Total user queues: {len(self._user_subscribers[user_id])}")
        return queue

    def unsubscribe_user(self, user_id: str, queue: asyncio.Queue):
        if user_id in self._user_subscribers:
            self._user_subscribers[user_id].discard(queue)
            if not self._user_subscribers[user_id]:
                del self._user_subscribers[user_id]
        log.debug(f"User {user_id} unsubscribed from SSE events.")

    def subscribe_role(self, role: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        if role not in self._role_subscribers:
            self._role_subscribers[role] = set()
        self._role_subscribers[role].add(queue)
        log.debug(f"Role {role} subscribed to SSE events. Total role queues: {len(self._role_subscribers[role])}")
        return queue

    def unsubscribe_role(self, role: str, queue: asyncio.Queue):
        if role in self._role_subscribers:
            self._role_subscribers[role].discard(queue)
            if not self._role_subscribers[role]:
                del self._role_subscribers[role]
        log.debug(f"Role {role} unsubscribed from SSE events.")

    async def publish_user(self, user_id: str, event_type: str, data: dict):
        payload = {"event": event_type, "data": data}
        queues = list(self._user_subscribers.get(user_id, []))
        for q in queues:
            await q.put(payload)
        if queues:
            log.info(f"Published event '{event_type}' to user {user_id} across {len(queues)} listener(s).")

    async def publish_role(self, role: str, event_type: str, data: dict):
        payload = {"event": event_type, "data": data}
        queues = list(self._role_subscribers.get(role, []))
        for q in queues:
            await q.put(payload)
        if queues:
            log.info(f"Published event '{event_type}' to role {role} across {len(queues)} listener(s).")

    async def broadcast(self, event_type: str, data: dict):
        payload = {"event": event_type, "data": data}
        all_queues = set()
        for qs in self._user_subscribers.values():
            all_queues.update(qs)
        for qs in self._role_subscribers.values():
            all_queues.update(qs)
        for q in all_queues:
            await q.put(payload)

event_bus = EventBus()
