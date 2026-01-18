import asyncio
import logging
from typing import Any
from urllib.parse import urljoin

import httpx
from taskiq.compat import model_dump
from taskiq.message import TaskiqMessage
from taskiq_dashboard import DashboardMiddleware

logger = logging.getLogger(__name__)


class CustomDashboardMiddleware(DashboardMiddleware):
    async def _spawn_request(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> None:
        """Fire and forget helper.

        Start an async POST to the admin API, keep the resulting Task in _pending
        so it can be awaited/cleaned during graceful shutdown.
        """

        async def _send() -> None:
            client = self._get_client()
            try:
                resp = await client.post(
                    urljoin(self.url, endpoint),
                    headers={"access-token": self.api_token},
                    json=payload,
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(
                    "Dashboard POST %s failed: %s - %s",
                    endpoint,
                    e.response.status_code,
                    e.response.text,
                )
            except httpx.RequestError as e:
                logger.error("Dashboard connection failed for %s: %s", endpoint, str(e))
            except Exception:
                logger.exception(
                    "Unexpected error sending dashboard request to %s", endpoint
                )

        task = asyncio.create_task(_send())
        self._pending.add(task)
        task.add_done_callback(self._pending.discard)

    async def post_send(self, message: TaskiqMessage) -> None:
        """
        This hook is executed right after the task is sent.

        This is a client-side hook. It executes right
        after the message is kicked in broker.

        :param message: kicked message.
        """
        dict_message: dict[str, Any] = model_dump(message)

        args = dict_message.get("args")
        if not isinstance(args, list):
            args = []

        kwargs = dict_message.get("kwargs")
        if not isinstance(kwargs, dict):
            kwargs = {}

        labels = dict_message.get("labels")
        if not isinstance(labels, dict):
            labels = {}

        await self._spawn_request(
            f"api/tasks/{message.task_id}/queued",
            {
                "args": args,
                "kwargs": kwargs,
                "labels": labels,
                "queuedAt": self._now_iso(),
                "taskName": message.task_name,
                "worker": self.broker_name,
            },
        )

    async def pre_execute(self, message: TaskiqMessage) -> TaskiqMessage:
        """
        This hook is called before executing task.

        This is a worker-side hook, which means it
        executes in the worker process.

        :param message: incoming parsed taskiq message.
        :return: modified message.
        """
        dict_message: dict[str, Any] = model_dump(message)

        args = dict_message.get("args")
        if not isinstance(args, list):
            args = []

        kwargs = dict_message.get("kwargs")
        if not isinstance(kwargs, dict):
            kwargs = {}

        labels = dict_message.get("labels")
        if not isinstance(labels, dict):
            labels = {}

        await self._spawn_request(
            f"api/tasks/{message.task_id}/started",
            {
                "args": args,
                "kwargs": kwargs,
                "labels": labels,
                "startedAt": self._now_iso(),
                "taskName": message.task_name,
                "worker": self.broker_name,
            },
        )
        return message
