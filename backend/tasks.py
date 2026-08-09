import structlog
import asyncio
from typing import Callable, Any

log = structlog.get_logger("tasks")

class BackgroundTaskManager:
    def __init__(self):
        self._tasks = set()

    def enqueue(self, func: Callable[..., Any], *args, **kwargs):
        """Enqueue an async background task safely without blocking request completion."""
        task = asyncio.create_task(self._run(func, *args, **kwargs))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _run(self, func: Callable[..., Any], *args, **kwargs):
        try:
            if asyncio.iscoroutinefunction(func):
                await func(*args, **kwargs)
            else:
                await asyncio.to_thread(func, *args, **kwargs)
        except Exception as exc:
            log.error("Background task execution error", task=getattr(func, "__name__", str(func)), error=str(exc), exc_info=exc)

background_tasks = BackgroundTaskManager()
