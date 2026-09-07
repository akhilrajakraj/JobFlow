"""API smoke and authentication tests."""

from fastapi.testclient import TestClient


def test_root() -> None:
    from app.main import app

    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["service"] == "JobFlow"
        assert response.headers["X-Request-ID"]


def test_protected_jobs_require_authentication() -> None:
    from app.main import app

    with TestClient(app) as client:
        response = client.get("/api/v1/jobs")
        assert response.status_code == 401


def test_admin_can_login_and_list_jobs() -> None:
    from app.core.config import settings
    from app.main import app

    with TestClient(app) as client:
        login = client.post(
            "/api/v1/auth/login",
            json={"username": settings.admin_username, "password": settings.admin_password},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]
        jobs = client.get("/api/v1/jobs", headers={"Authorization": f"Bearer {token}"})
        assert jobs.status_code == 200
