import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status


# FIXME: Goes to only v1 endpoint. How to change this behavior?
@pytest.mark.anyio
async def test_echo(fastapi_app: FastAPI, client_authenticated: AsyncClient) -> None:
    """Tests that echo route works.

    Args:
        fastapi_app: current application.
        client_authenticated: authenticated client.
    """
    url = fastapi_app.url_path_for("send_echo_message")
    message = uuid.uuid4().hex
    response = await client_authenticated.post(url, json={"message": message})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == message
