import time
from typing import Any

from loguru import logger
from redis.asyncio import BlockingConnectionPool, Redis
from taskiq.abc.middleware import TaskiqMiddleware
from taskiq.message import TaskiqMessage
from taskiq.result import TaskiqResult

from api_shared.utils.task_status_manager import TaskStatus, TaskStatusManager


class TaskStatusMiddleware(TaskiqMiddleware):
    """A Taskiq middleware that updates task metadata in Redis."""

    def __init__(
        self,
        redis_url: str,
        max_connection_pool_size: int | None = None,
        **connection_kwargs: Any,
    ) -> None:
        """Initialize the TaskStatusMiddleware.

        Args:
            redis_url: Redis connection URL.
            max_connection_pool_size: Maximum number of connections in pool.
            **connection_kwargs: Additional arguments for Redis BlockingConnectionPool.
        """
        super().__init__()
        self._redis_pool = BlockingConnectionPool.from_url(
            redis_url,
            max_connections=max_connection_pool_size,
            **connection_kwargs,
        )

    async def shutdown(self) -> None:
        """Closes redis connection."""
        await self._redis_pool.aclose()

    async def post_send(self, message: TaskiqMessage) -> None:
        """
        This hook is executed right after the task is sent.

        This is a client-side hook. It executes right
        after the message is kicked in broker.

        :param message: kicked message.
        """
        try:
            async with Redis.from_pool(self._redis_pool) as redis_client:
                await TaskStatusManager.update_task_metadata(
                    task_id=message.task_id,
                    updates={
                        "queued_time": time.time(),
                        "status": TaskStatus.QUEUED,
                    },
                    redis_client=redis_client,
                )
        except Exception as e:
            logger.error(
                "Failed to update task metadata for task_id {}: {}", message.task_id, e
            )

    async def pre_execute(self, message: TaskiqMessage) -> TaskiqMessage:
        """
        This hook is called before executing task.

        This is a worker-side hook, which means it
        executes in the worker process.

        :param message: incoming parsed taskiq message.
        :return: modified message.
        """
        try:
            async with Redis.from_pool(self._redis_pool) as redis_client:
                await TaskStatusManager.update_task_metadata(
                    task_id=message.task_id,
                    updates={
                        "started_time": time.time(),
                        "status": TaskStatus.STARTED,
                    },
                    redis_client=redis_client,
                )
        except Exception as e:
            logger.error(
                "Failed to update task metadata for task_id {}: {}", message.task_id, e
            )
        return message

    async def post_save(
        self,
        message: TaskiqMessage,
        result: TaskiqResult[Any],
    ) -> None:
        """
        Post save hook.

        This function is called after result of
        the executions is saved in the result_backend.

        :param message: processed message.
        :param result: returned value.
        """
        try:
            async with Redis.from_pool(self._redis_pool) as redis_client:
                if result.is_err:
                    await TaskStatusManager.update_task_metadata(
                        task_id=message.task_id,
                        updates={
                            "finished_time": time.time(),
                            "status": TaskStatus.FAILED,
                            "error": str(result.error) if result.is_err else None,
                        },
                        redis_client=redis_client,
                    )
                else:
                    await TaskStatusManager.update_task_metadata(
                        task_id=message.task_id,
                        updates={
                            "finished_time": time.time(),
                            "status": TaskStatus.FINISHED,
                        },
                        redis_client=redis_client,
                    )
        except Exception as e:
            logger.error(
                "Failed to update task metadata for task_id {}: {}", message.task_id, e
            )
