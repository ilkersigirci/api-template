import base64
import json
from collections.abc import Mapping


def _urlsafe_b64encode_json(payload: Mapping[str, object]) -> str:
    encoded = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    return encoded.decode("utf-8").rstrip("=")


def generate_hatchet_test_token(
    *,
    sub: str = "test-tenant",
    server_url: str = "https://example.test",
    grpc_broadcast_address: str = "127.0.0.1:7070",
    exp: int = 4_700_000_000,
) -> str:
    """Generate a JWT-shaped token with claims required by hatchet-sdk ClientConfig."""
    header = {"alg": "HS256", "typ": "JWT"}
    claims = {
        "sub": sub,
        "server_url": server_url,
        "grpc_broadcast_address": grpc_broadcast_address,
        "exp": exp,
    }

    return (
        f"{_urlsafe_b64encode_json(header)}.{_urlsafe_b64encode_json(claims)}.signature"
    )
