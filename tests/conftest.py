
import sqlite3
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_students.db"

    # App ke database module ko test database par point karo
    import app.database as database
    monkeypatch.setattr(database, "DATABASE_PATH", test_db)

    # Har test ke liye fresh database initialize karo
    init_db()

    with TestClient(app) as test_client:
        import uuid

        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        password = "TestPassword123!"

        register_response = test_client.post(
            "/auth/register",
            json={"email": email, "password": password},
        )
        assert register_response.status_code == 201, (
            register_response.text
        )

        login_response = test_client.post(
            "/auth/login",
            data={"username": email, "password": password},
        )
        assert login_response.status_code == 200, (
            login_response.text
        )

        token = login_response.json()["access_token"]
        test_client.headers.update(
            {"Authorization": f"Bearer {token}"}
        )

        yield test_client
