import contextlib
import json
import time
from enum import StrEnum
from typing import Any

from loguru import logger
from redis.asyncio import Redis
from redis.exceptions import LockError

from api_shared.core.settings import settings


class TaskStatus(StrEnum):
    """Task status enumeration."""

    FAILED = "failed"
    FINISHED = "finished"
    QUEUED = "queued"
    QUEUEING = "queueing"
    STARTED = "started"


class TaskStatusManager:
    TASK_LOCK_PREFIX = "task_lock:"
    TASK_META_PREFIX = "task_meta:"

    @staticmethod
    def _task_meta_key(task_id: str) -> str:
        return f"{TaskStatusManager.TASK_META_PREFIX}{task_id}"

    @staticmethod
    def _task_lock_key(task_id: str) -> str:
        return f"{TaskStatusManager.TASK_LOCK_PREFIX}{task_id}"

    @staticmethod
    def create_task_metadata(
        task_id: str,
        task_type: str,
        register_task_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "task_id": task_id,
            "task_type": task_type,
            "queueing_time": time.time(),
            "status": TaskStatus.QUEUEING,
            **(register_task_metadata or {}),
        }

    @staticmethod
    async def get_task_metadata(
        task_id: str,
        redis_client: Redis,
    ) -> dict[str, Any] | None:
        meta_key = TaskStatusManager._task_meta_key(task_id)
        result = await redis_client.get(meta_key)

        if not result:
            return None
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON payload in Redis key {}", meta_key)
            return None

    @staticmethod
    async def _set_task_metadata(
        task_id: str,
        metadata: dict[str, Any],
        redis_client: Redis,
        expiry_seconds: int = settings.TASKIQ_RESULT_EX_TIME,
    ) -> None:
        meta_key = TaskStatusManager._task_meta_key(task_id)
        await redis_client.set(
            meta_key,
            json.dumps(metadata),
            ex=expiry_seconds,
        )

    @staticmethod
    async def update_task_metadata(
        task_id: str,
        updates: dict[str, Any],
        redis_client: Redis,
        expiry_seconds: int = settings.TASKIQ_RESULT_EX_TIME,
    ) -> dict[str, Any]:
        lock = redis_client.lock(
            TaskStatusManager._task_lock_key(task_id), timeout=5, blocking_timeout=10
        )
        try:
            await lock.acquire()

            metadata = await TaskStatusManager.get_task_metadata(task_id, redis_client)
            if metadata is None:
                metadata = {"task_id": task_id}

            metadata.update(updates)
            await TaskStatusManager._set_task_metadata(
                task_id, metadata, redis_client, expiry_seconds
            )

            return metadata
        finally:
            with contextlib.suppress(LockError):
                await lock.release()
