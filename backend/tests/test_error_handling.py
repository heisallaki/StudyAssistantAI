import uuid

from fastapi.testclient import TestClient

from app.core.rate_limit import limiter
from app.db.session import get_db
from app.main import app

client = TestClient(app)


def _broken_db():
    raise RuntimeError("Simulated unexpected database failure")
    yield  # pragma: no cover


def _register_and_login():
    email = f"{uuid.uuid4()}@example.com"
    password = "S3curePassw0rd!"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]
    return {"email": email, "headers": {"Authorization": f"Bearer {token}"}}


def test_unhandled_exception_returns_generic_500_without_leaking_details():
    user = _register_and_login()
    lenient_client = TestClient(app, raise_server_exceptions=False)

    app.dependency_overrides[get_db] = _broken_db
    try:
        response = lenient_client.get("/api/v1/subjects", headers=user["headers"])
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 500
    body = response.json()
    assert body == {"detail": "An unexpected error occurred. Please try again later."}
    assert "RuntimeError" not in response.text
    assert "Simulated unexpected database failure" not in response.text


def test_rate_limit_exceeded_returns_429_with_generic_message():
    was_enabled = limiter.enabled
    limiter.enabled = True
    try:
        last_response = None
        for _ in range(15):
            last_response = client.post(
                "/api/v1/auth/login",
                json={"email": "ratelimit-probe@example.com", "password": "wrong-password"},
            )
            if last_response.status_code == 429:
                break

        assert last_response is not None
        assert last_response.status_code == 429
        assert last_response.json() == {"detail": "Too many requests. Please try again later."}
    finally:
        limiter.enabled = was_enabled