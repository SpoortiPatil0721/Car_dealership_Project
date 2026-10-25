import pytest

NEW_CAR = {
    "make": "Honda",
    "model": "Civic",
    "category": "Sedan",
    "price": 24500.0,
    "quantity": 3,
    "year": 2024,
    "color": "Blue",
}


def test_listing_vehicles_needs_login(client):
    assert client.get("/api/vehicles").status_code == 401


def test_admin_can_add_vehicle(client, admin_headers):
    response = client.post("/api/vehicles", json=NEW_CAR, headers=admin_headers)
    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int)
    for key, value in NEW_CAR.items():
        assert body[key] == value


def test_regular_user_cannot_add_vehicle(client, user_headers):
    response = client.post("/api/vehicles", json=NEW_CAR, headers=user_headers)
    assert response.status_code == 403


@pytest.mark.parametrize(
    "bad_field",
    [
        {"price": -10},
        {"price": 0},
        {"quantity": -1},
        {"make": ""},
        {"model": "   "},
        {"year": 1850},
    ],
)
def test_add_vehicle_rejects_invalid_data(client, admin_headers, bad_field):
    response = client.post("/api/vehicles", json={**NEW_CAR, **bad_field}, headers=admin_headers)
    assert response.status_code == 422


def test_add_vehicle_requires_core_fields(client, admin_headers):
    response = client.post("/api/vehicles", json={"make": "Honda"}, headers=admin_headers)
    assert response.status_code == 422


def test_list_returns_every_vehicle_including_sold_out(client, user_headers, make_vehicle):
    make_vehicle(model="Corolla")
    make_vehicle(model="Camry", quantity=0)
    response = client.get("/api/vehicles", headers=user_headers)
    assert response.status_code == 200
    assert sorted(v["model"] for v in response.json()) == ["Camry", "Corolla"]


def test_get_single_vehicle(client, user_headers, make_vehicle):
    car = make_vehicle()
    response = client.get(f"/api/vehicles/{car['id']}", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["model"] == "Corolla"


def test_get_missing_vehicle_is_404(client, user_headers):
    assert client.get("/api/vehicles/999", headers=user_headers).status_code == 404


def test_admin_can_update_some_fields(client, admin_headers, make_vehicle):
    car = make_vehicle()
    response = client.put(f"/api/vehicles/{car['id']}", json={"price": 18999.99, "color": "Red"}, headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["price"] == 18999.99
    assert body["color"] == "Red"
    assert body["model"] == "Corolla"


def test_update_rejects_invalid_values(client, admin_headers, make_vehicle):
    car = make_vehicle()
    response = client.put(f"/api/vehicles/{car['id']}", json={"price": -5}, headers=admin_headers)
    assert response.status_code == 422


def test_update_with_empty_body_is_rejected(client, admin_headers, make_vehicle):
    car = make_vehicle()
    response = client.put(f"/api/vehicles/{car['id']}", json={}, headers=admin_headers)
    assert response.status_code == 422


def test_update_missing_vehicle_is_404(client, admin_headers):
    response = client.put("/api/vehicles/999", json={"price": 100}, headers=admin_headers)
    assert response.status_code == 404


def test_regular_user_cannot_update(client, user_headers, make_vehicle):
    car = make_vehicle()
    response = client.put(f"/api/vehicles/{car['id']}", json={"price": 1}, headers=user_headers)
    assert response.status_code == 403


def test_admin_can_delete_vehicle(client, admin_headers, make_vehicle):
    car = make_vehicle()
    assert client.delete(f"/api/vehicles/{car['id']}", headers=admin_headers).status_code == 204
    assert client.get(f"/api/vehicles/{car['id']}", headers=admin_headers).status_code == 404


def test_regular_user_cannot_delete(client, user_headers, make_vehicle):
    car = make_vehicle()
    assert client.delete(f"/api/vehicles/{car['id']}", headers=user_headers).status_code == 403


def test_delete_missing_vehicle_is_404(client, admin_headers):
    assert client.delete("/api/vehicles/999", headers=admin_headers).status_code == 404
