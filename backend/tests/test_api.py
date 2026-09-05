import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_create_and_fetch_session():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post("/api/sessions", json={"title": "Test Session"})
        assert create_resp.status_code == 200
        session = create_resp.json()
        assert session["title"] == "Test Session"

        get_resp = await client.get(f"/api/sessions/{session['id']}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == session["id"]


@pytest.mark.asyncio
async def test_get_nonexistent_session_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/sessions/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_health_endpoint_reports_shape():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
        assert "database" in body
        assert "ollama" in body
