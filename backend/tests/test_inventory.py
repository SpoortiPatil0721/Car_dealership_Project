def purchase(client, headers, vehicle_id, quantity=None):
    body = None if quantity is None else {"quantity": quantity}
    return client.post(f"/api/vehicles/{vehicle_id}/purchase", json=body, headers=headers)


def restock(client, headers, vehicle_id, quantity):
    return client.post(f"/api/vehicles/{vehicle_id}/restock", json={"quantity": quantity}, headers=headers)


def test_purchase_needs_login(client, make_vehicle):
    car = make_vehicle()
    assert purchase(client, {}, car["id"]).status_code == 401


def test_purchase_takes_one_off_the_stock_by_default(client, user_headers, make_vehicle):
    car = make_vehicle(quantity=5)
    response = purchase(client, user_headers, car["id"])
    assert response.status_code == 200
    assert response.json()["quantity"] == 4


def test_purchase_several_at_once(client, user_headers, make_vehicle):
    car = make_vehicle(quantity=5)
    response = purchase(client, user_headers, car["id"], quantity=3)
    assert response.status_code == 200
    assert response.json()["quantity"] == 2


def test_can_buy_the_last_one(client, user_headers, make_vehicle):
    car = make_vehicle(quantity=1)
    assert purchase(client, user_headers, car["id"]).json()["quantity"] == 0


def test_purchase_when_sold_out_is_conflict(client, user_headers, make_vehicle):
    car = make_vehicle(quantity=0)
    response = purchase(client, user_headers, car["id"])
    assert response.status_code == 409
    assert "stock" in response.json()["detail"].lower()


def test_buying_more_than_available_changes_nothing(client, user_headers, make_vehicle):
    car = make_vehicle(quantity=2)
    assert purchase(client, user_headers, car["id"], quantity=3).status_code == 409
    after = client.get(f"/api/vehicles/{car['id']}", headers=user_headers).json()
    assert after["quantity"] == 2


def test_purchase_quantity_must_be_positive(client, user_headers, make_vehicle):
    car = make_vehicle()
    assert purchase(client, user_headers, car["id"], quantity=0).status_code == 422


def test_purchase_missing_vehicle_is_404(client, user_headers):
    assert purchase(client, user_headers, 999).status_code == 404


def test_admin_can_restock(client, admin_headers, make_vehicle):
    car = make_vehicle(quantity=1)
    response = restock(client, admin_headers, car["id"], 10)
    assert response.status_code == 200
    assert response.json()["quantity"] == 11


def test_regular_user_cannot_restock(client, user_headers, make_vehicle):
    car = make_vehicle()
    assert restock(client, user_headers, car["id"], 10).status_code == 403


def test_restock_needs_positive_quantity(client, admin_headers, make_vehicle):
    car = make_vehicle()
    assert restock(client, admin_headers, car["id"], 0).status_code == 422
    assert restock(client, admin_headers, car["id"], -4).status_code == 422


def test_restock_missing_vehicle_is_404(client, admin_headers):
    assert restock(client, admin_headers, 999, 3).status_code == 404


def test_sold_out_vehicle_can_be_bought_again_after_restock(client, user_headers, admin_headers, make_vehicle):
    car = make_vehicle(quantity=0)
    assert purchase(client, user_headers, car["id"]).status_code == 409
    restock(client, admin_headers, car["id"], 2)
    assert purchase(client, user_headers, car["id"]).status_code == 200
