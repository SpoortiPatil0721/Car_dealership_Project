import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

ADMIN_EMAIL = "boss@dealership.test"
TEST_SECRET = "test-secret-that-is-at-least-32-bytes-long"


@pytest.fixture
def settings(tmp_path):
    # real sqlite file per test so nothing leaks between tests
    return Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        jwt_secret=TEST_SECRET,
        password_iterations=1000,
        admin_emails=(ADMIN_EMAIL,),
    )


@pytest.fixture
def client(settings):
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client


def register(client, email, password="secret123", full_name="Test User"):
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    assert response.status_code == 201, response.text
    return response.json()


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_headers(client):
    return bearer(register(client, "buyer@test.com")["access_token"])


@pytest.fixture
def other_user_headers(client):
    return bearer(register(client, "second@test.com")["access_token"])


@pytest.fixture
def admin_headers(client):
    return bearer(register(client, ADMIN_EMAIL, full_name="The Boss")["access_token"])


@pytest.fixture
def make_vehicle(client, admin_headers):
    def _make(**overrides):
        payload = {"make": "Toyota", "model": "Corolla", "category": "Sedan", "price": 20000, "quantity": 5}
        payload.update(overrides)
        response = client.post("/api/vehicles", json=payload, headers=admin_headers)
        assert response.status_code == 201, response.text
        return response.json()

    return _make
