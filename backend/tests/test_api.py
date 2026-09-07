from fastapi.testclient import TestClient

def test_root():
    from app.main import app
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["service"] == "JobFlow"
