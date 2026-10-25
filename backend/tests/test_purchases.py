from tests.test_inventory import purchase


def my_history(client, headers):
    response = client.get("/api/purchases/me", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def test_history_needs_login(client):
    assert client.get("/api/purchases/me").status_code == 401


def test_history_starts_empty(client, user_headers):
    assert my_history(client, user_headers) == []


def test_purchase_shows_up_in_history_with_price_snapshot(client, user_headers, make_vehicle):
    car = make_vehicle(make="Kia", model="Seltos", price=15000, quantity=4)
    purchase(client, user_headers, car["id"], quantity=2)
    [entry] = my_history(client, user_headers)
    assert entry["vehicle_id"] == car["id"]
    assert entry["make"] == "Kia"
    assert entry["model"] == "Seltos"
    assert entry["quantity"] == 2
    assert entry["unit_price"] == 15000
    assert entry["total_price"] == 30000
    assert entry["purchased_at"]


def test_failed_purchase_is_not_recorded(client, user_headers, make_vehicle):
    car = make_vehicle(quantity=0)
    purchase(client, user_headers, car["id"])
    assert my_history(client, user_headers) == []


def test_later_price_change_does_not_rewrite_history(client, user_headers, admin_headers, make_vehicle):
    car = make_vehicle(price=10000)
    purchase(client, user_headers, car["id"])
    client.put(f"/api/vehicles/{car['id']}", json={"price": 99999}, headers=admin_headers)
    assert my_history(client, user_headers)[0]["unit_price"] == 10000


def test_users_only_see_their_own_purchases(client, user_headers, other_user_headers, make_vehicle):
    car = make_vehicle()
    purchase(client, user_headers, car["id"])
    assert my_history(client, other_user_headers) == []


def test_newest_purchase_comes_first(client, user_headers, make_vehicle):
    first = make_vehicle(model="First")
    second = make_vehicle(model="Second")
    purchase(client, user_headers, first["id"])
    purchase(client, user_headers, second["id"])
    assert [p["model"] for p in my_history(client, user_headers)] == ["Second", "First"]


def test_history_survives_vehicle_being_deleted(client, user_headers, admin_headers, make_vehicle):
    car = make_vehicle(model="Gone")
    purchase(client, user_headers, car["id"])
    client.delete(f"/api/vehicles/{car['id']}", headers=admin_headers)
    [entry] = my_history(client, user_headers)
    assert entry["model"] == "Gone"
    assert entry["vehicle_id"] is None


def test_admin_sees_all_sales_with_buyer(client, user_headers, other_user_headers, admin_headers, make_vehicle):
    car = make_vehicle()
    purchase(client, user_headers, car["id"])
    purchase(client, other_user_headers, car["id"])
    response = client.get("/api/purchases", headers=admin_headers)
    assert response.status_code == 200
    assert sorted(p["buyer_email"] for p in response.json()) == ["buyer@test.com", "second@test.com"]


def test_regular_user_cannot_see_all_sales(client, user_headers):
    assert client.get("/api/purchases", headers=user_headers).status_code == 403
