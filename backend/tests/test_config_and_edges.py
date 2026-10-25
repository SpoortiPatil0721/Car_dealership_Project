from app.config import Settings
from app.models import User
from app.security import verify_password
from tests.conftest import bearer, register


def test_settings_read_from_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@host:5432/cars")
    monkeypatch.setenv("ADMIN_EMAILS", " Admin@Shop.com , second@shop.com ,")
    monkeypatch.setenv("CORS_ORIGINS", "https://a.dev,https://b.dev")
    monkeypatch.setenv("TOKEN_MINUTES", "30")
    settings = Settings.from_env()
    assert settings.database_url == "postgresql://u:p@host:5432/cars"
    assert settings.admin_emails == ("admin@shop.com", "second@shop.com")
    assert settings.cors_origins == ("https://a.dev", "https://b.dev")
    assert settings.token_minutes == 30


def test_settings_defaults_when_env_is_empty(monkeypatch):
    for name in ("DATABASE_URL", "ADMIN_EMAILS", "CORS_ORIGINS", "TOKEN_MINUTES", "LOW_STOCK_THRESHOLD"):
        monkeypatch.delenv(name, raising=False)
    settings = Settings.from_env()
    assert settings.database_url.startswith("sqlite")
    assert settings.admin_emails == ()


def test_health_check_is_public(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_hash_with_unknown_algorithm_is_rejected():
    assert not verify_password("x", "md5$1$abc$def")


def test_token_for_deleted_user_is_rejected(client):
    token = register(client, "temp@test.com")["access_token"]
    with client.app.state.session_factory() as db:
        db.delete(db.query(User).filter_by(email="temp@test.com").one())
        db.commit()
    assert client.get("/api/auth/me", headers=bearer(token)).status_code == 401


def test_update_cannot_null_a_required_field(client, admin_headers, make_vehicle):
    car = make_vehicle()
    response = client.put(f"/api/vehicles/{car['id']}", json={"make": None}, headers=admin_headers)
    assert response.status_code == 422


def test_update_can_clear_an_optional_field(client, admin_headers, make_vehicle):
    car = make_vehicle(color="Red")
    response = client.put(f"/api/vehicles/{car['id']}", json={"color": None}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["color"] is None
