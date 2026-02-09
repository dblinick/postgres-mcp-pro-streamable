from starlette.testclient import TestClient

from postgres_mcp.server import API_KEY_HEADER
from postgres_mcp.server import StreamableHttpApiKeyMiddleware
from postgres_mcp.server import mcp


def _initialize_payload():
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "0.0.0"},
        },
    }


def _build_app(api_key: str):
    app = mcp.streamable_http_app()
    app.add_middleware(
        StreamableHttpApiKeyMiddleware,
        api_key=api_key,
        path=mcp.settings.streamable_http_path,
    )
    return app


def test_streamable_http_requires_api_key():
    app = _build_app("test-key")

    with TestClient(app) as client:
        response = client.post(
            "/mcp",
            headers={"Accept": "application/json"},
            json=_initialize_payload(),
        )

    assert response.status_code == 401
    payload = response.json()
    assert payload["error"]["message"] == "Unauthorized"


def test_streamable_http_allows_valid_api_key():
    app = _build_app("test-key")

    with TestClient(app) as client:
        response = client.post(
            "/mcp",
            headers={
                "Accept": "application/json",
                API_KEY_HEADER: "test-key",
            },
            json=_initialize_payload(),
        )

    assert response.status_code == 200
