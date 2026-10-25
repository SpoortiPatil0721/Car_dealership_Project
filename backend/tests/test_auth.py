from tests.conftest import ADMIN_EMAIL, bearer, register


def test_register_returns_token_and_user(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "joel@test.com", "password": "secret123", "full_name": "Joel"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "joel@test.com"
    assert body["user"]["is_admin"] is False
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_register_twice_with_same_email_is_conflict(client):
    register(client, "dup@test.com")
    response = client.post(
        "/api/auth/register",
        json={"email": "DUP@test.com", "password": "secret123", "full_name": "Dup"},
    )
    assert response.status_code == 409


def test_register_rejects_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "short@test.com", "password": "123", "full_name": "Short"},
    )
    assert response.status_code == 422


def test_register_rejects_bad_email(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "secret123", "full_name": "Bad"},
    )
    assert response.status_code == 422


def test_email_in_admin_list_becomes_admin(client):
    body = register(client, ADMIN_EMAIL)
    assert body["user"]["is_admin"] is True


def test_login_with_correct_credentials(client):
    register(client, "login@test.com", password="pass1234")
    response = client.post("/api/auth/login", json={"email": "LOGIN@test.com", "password": "pass1234"})
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["user"]["email"] == "login@test.com"


def test_login_with_wrong_password_is_unauthorized(client):
    register(client, "login@test.com", password="pass1234")
    response = client.post("/api/auth/login", json={"email": "login@test.com", "password": "nope1234"})
    assert response.status_code == 401


def test_login_with_unknown_email_is_unauthorized(client):
    response = client.post("/api/auth/login", json={"email": "ghost@test.com", "password": "pass1234"})
    assert response.status_code == 401


def test_me_requires_a_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_rejects_a_bad_token(client):
    assert client.get("/api/auth/me", headers=bearer("garbage.token.here")).status_code == 401


def test_me_returns_current_user(client, user_headers):
    response = client.get("/api/auth/me", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "buyer@test.com"
